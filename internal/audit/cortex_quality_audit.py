#!/usr/bin/env python3
"""Bounded internal audit for live Cortex code quality and proof coverage."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / ".cortex" / "quality_audit"
VALID_FINDINGS = (
    "earning",
    "broken-or-hanging",
    "dead-weight",
    "under-earned-keep",
    "structural-rewrite-candidate",
)
LIVE_CODE_SCOPE = (
    ("Core/runtime kernels", "product", "cortex/core"),
    ("Core/runtime kernels", "product", "cortex/runtime"),
    ("SRE active law", "product", "cortex/sre"),
    ("Host realizations", "product", "cortex/hosts"),
    ("AUX live experimental code", "experimental", "cortex/aux"),
)
JUNK_FILENAMES = frozenset({".DS_Store", "Thumbs.db"})
UNDER_EARNED_NOTES = {
    "cortex/aux/cost.py": (
        "Keep this only as bounded support-side burden accounting for AUX replay; "
        "it should stay off the product critical path."
    ),
    "cortex/aux/evaluation.py": (
        "Keep this only because replay/corpus falsification needs it; do not let it "
        "become a second product surface."
    ),
    "cortex/aux/lift.py": (
        "Keep this as retention/falsification support only; if it stops changing "
        "product decisions, cut it."
    ),
    "cortex/sre/mediation.py": (
        "Keep this behind its explicit experimental boundary; it remains a bounded "
        "host-realization extension, not core executive law."
    ),
}
FALLBACK_TEST_PROOFS = {
    "Core/runtime kernels": (
        "tests/product",
        "tests/conformance",
    ),
    "SRE active law": (
        "tests/product",
        "tests/conformance",
        "tests/experimental/test_sre_mediation.py",
    ),
    "SRE mediation extension": (
        "tests/experimental/test_sre_mediation.py",
        "tests/conformance/test_reference_runtime_step.py",
    ),
    "Host realizations": (
        "tests/conformance",
        "tests/product",
    ),
    "AUX live experimental code": (
        "tests/experimental",
        "tests/archive/test_correspondence_aux.py",
        "tests/conformance/test_reference_runtime_step.py",
    ),
}
EXECUTABLE_PATHS = {
    "Core/runtime kernels": (
        "make product-test",
        "make conformance-test",
    ),
    "SRE active law": (
        "make product-test",
        "make conformance-test",
    ),
    "SRE mediation extension": (
        "python3 -m pytest -q tests/experimental/test_sre_mediation.py",
        "python3 -m pytest -q tests/conformance/test_reference_runtime_step.py",
    ),
    "Host realizations": (
        "make conformance-test",
        "python3 -m lab.cortex_conformance --mode active --brain openai --contract-pack verified_work_bookmarks_v1",
    ),
    "AUX live experimental code": (
        "make experimental-test",
        "python3 -m pytest -q tests/conformance/test_reference_runtime_step.py",
    ),
}
REMOVAL_EFFECTS = {
    "Core/runtime kernels": (
        "Typed commitment, provenance, lifecycle, and shared runtime behavior would "
        "break across hosts and core product proofs would stop being meaningful."
    ),
    "SRE active law": (
        "Shared executive state, family selection, brake, goal-debt, and allocation "
        "truth would drift or fail across product and conformance lanes."
    ),
    "SRE mediation extension": (
        "The bounded reference mediation experiment and its proof surface would vanish, "
        "removing the only explicit off-by-default host-realization extension."
    ),
    "Host realizations": (
        "Host-specific realization of shared Cortex law would break, taking shipping "
        "or conformance behavior with it."
    ),
    "AUX live experimental code": (
        "Offline publication, replay, support-conditioned Q_mem evidence, and AUX "
        "removability proofs would stop working."
    ),
}


@dataclass(frozen=True, slots=True)
class ModuleAuditRecord:
    module_path: str
    subsystem: str
    surface: Literal["product", "experimental"]
    executive_mechanism: str
    proof_surfaces: tuple[str, ...]
    executable_paths: tuple[str, ...]
    removal_effect: str
    finding: str
    rationale: str


def _scope_roots(root: Path = ROOT) -> tuple[tuple[str, str, Path], ...]:
    return tuple(
        (subsystem, surface, root / relative_path)
        for subsystem, surface, relative_path in LIVE_CODE_SCOPE
    )


def _iter_live_code_modules(root: Path = ROOT) -> tuple[str, ...]:
    modules: list[str] = []
    scope_roots = (
        root / "cortex" / "core",
        root / "cortex" / "runtime",
        root / "cortex" / "sre",
        root / "cortex" / "hosts",
        root / "cortex" / "aux",
    )
    for scope_root in scope_roots:
        for path in sorted(scope_root.rglob("*.py")):
            relative = path.relative_to(root).as_posix()
            modules.append(relative)
    return tuple(modules)


def _junk_paths(root: Path = ROOT) -> tuple[str, ...]:
    junk: list[str] = []
    for _subsystem, _surface, scope_root in _scope_roots(root):
        if not scope_root.exists():
            continue
        for path in sorted(scope_root.rglob("*")):
            if path.is_file() and path.name in JUNK_FILENAMES:
                junk.append(path.relative_to(root).as_posix())
    return tuple(junk)


def _subsystem_for_module(module_path: str) -> tuple[str, Literal["product", "experimental"]]:
    if module_path == "cortex/sre/mediation.py":
        return "SRE mediation extension", "experimental"
    for subsystem, surface, relative_path in LIVE_CODE_SCOPE:
        prefix = f"{relative_path}/"
        if module_path.startswith(prefix):
            return subsystem, surface  # type: ignore[return-value]
    raise ValueError(f"Unhandled live-code module {module_path!r}")


def _module_doc_summary(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    docstring = ast.get_docstring(tree)
    if docstring:
        return docstring.strip().splitlines()[0].rstrip(".")
    if path.name == "__init__.py":
        package_name = path.parent.relative_to(ROOT).as_posix()
        return f"Package export surface for {package_name}"
    return f"Load-bearing Cortex module `{path.stem}`"


def _module_import_name(module_path: str) -> str:
    if module_path.endswith("/__init__.py"):
        return module_path[:-12].replace("/", ".")
    return module_path[:-3].replace("/", ".")


def _test_texts(root: Path = ROOT) -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            path.relative_to(root).as_posix(),
            path.read_text(encoding="utf-8"),
        )
        for path in sorted((root / "tests").rglob("test_*.py"))
    )


def _proof_surfaces_for_module(
    module_path: str,
    *,
    subsystem: str,
    test_texts: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    import_name = _module_import_name(module_path)
    package_name = import_name.rsplit(".", 1)[0]
    stem = Path(module_path).stem
    direct_hits: list[str] = []
    for test_path, text in test_texts:
        if import_name in text:
            direct_hits.append(test_path)
            continue
        if path_name := Path(module_path).name:
            if path_name == "__init__.py" and package_name in text:
                direct_hits.append(test_path)
                continue
        if f"from {package_name} import {stem}" in text or f"import {import_name}" in text:
            direct_hits.append(test_path)
    if direct_hits:
        return tuple(sorted(set(direct_hits))[:5])
    return FALLBACK_TEST_PROOFS[subsystem]


def _finding_for_module(module_path: str) -> tuple[str, str]:
    if module_path in UNDER_EARNED_NOTES:
        return "under-earned-keep", UNDER_EARNED_NOTES[module_path]
    return (
        "earning",
        "This module has a clear Cortex-specific purpose, a real proof surface, and "
        "an executable path that exercises it.",
    )


def _record_for_module(
    module_path: str,
    *,
    root: Path,
    test_texts: tuple[tuple[str, str], ...],
) -> ModuleAuditRecord:
    subsystem, surface = _subsystem_for_module(module_path)
    finding, rationale = _finding_for_module(module_path)
    return ModuleAuditRecord(
        module_path=module_path,
        subsystem=subsystem,
        surface=surface,
        executive_mechanism=_module_doc_summary(root / module_path),
        proof_surfaces=_proof_surfaces_for_module(
            module_path,
            subsystem=subsystem,
            test_texts=test_texts,
        ),
        executable_paths=EXECUTABLE_PATHS[subsystem],
        removal_effect=REMOVAL_EFFECTS[subsystem],
        finding=finding,
        rationale=rationale,
    )


def build_live_code_audit(root: Path = ROOT) -> dict[str, object]:
    test_texts = _test_texts(root)
    records = tuple(
        _record_for_module(module_path, root=root, test_texts=test_texts)
        for module_path in _iter_live_code_modules(root)
    )
    invalid_findings = sorted(
        {record.finding for record in records if record.finding not in VALID_FINDINGS}
    )
    if invalid_findings:
        raise ValueError(f"Unexpected audit finding categories: {invalid_findings}")
    return {
        "scope": "live-code",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "module_count": len(records),
        "summary": {
            "by_finding": {
                finding: sum(1 for record in records if record.finding == finding)
                for finding in VALID_FINDINGS
            },
            "by_subsystem": {
                subsystem: sum(1 for record in records if record.subsystem == subsystem)
                for subsystem, _surface, _relative in (
                    ("Core/runtime kernels", "product", "cortex/core"),
                    ("SRE active law", "product", "cortex/sre"),
                    ("Host realizations", "product", "cortex/hosts"),
                    ("AUX live experimental code", "experimental", "cortex/aux"),
                    ("SRE mediation extension", "experimental", "cortex/sre/mediation.py"),
                )
            },
        },
        "dead_weight_paths": _junk_paths(root),
        "records": [asdict(record) for record in records],
    }


def _render_markdown(audit: dict[str, object]) -> str:
    records = audit["records"]
    assert isinstance(records, list)
    lines = [
        "# Cortex Live Code Quality Audit",
        "",
        f"- Scope: `{audit['scope']}`",
        f"- Generated at: `{audit['generated_at']}`",
        f"- Module count: `{audit['module_count']}`",
        "",
        "## Summary",
        "",
    ]
    summary = audit["summary"]
    assert isinstance(summary, dict)
    by_finding = summary["by_finding"]
    assert isinstance(by_finding, dict)
    for finding in VALID_FINDINGS:
        lines.append(f"- `{finding}`: `{by_finding[finding]}`")
    dead_weight_paths = audit["dead_weight_paths"]
    assert isinstance(dead_weight_paths, tuple | list)
    if dead_weight_paths:
        lines.append(f"- `dead-weight paths`: `{len(dead_weight_paths)}`")
        for path in dead_weight_paths:
            lines.append(f"  - `{path}`")
    else:
        lines.append("- `dead-weight paths`: `0`")

    subsystem_order = (
        "Core/runtime kernels",
        "SRE active law",
        "Host realizations",
        "AUX live experimental code",
        "SRE mediation extension",
    )
    for subsystem in subsystem_order:
        subsystem_records = [
            record for record in records if record["subsystem"] == subsystem
        ]
        if not subsystem_records:
            continue
        lines.extend(["", f"## {subsystem}", ""])
        for record in subsystem_records:
            lines.append(f"### `{record['module_path']}`")
            lines.append(f"- Surface: `{record['surface']}`")
            lines.append(f"- Finding: `{record['finding']}`")
            lines.append(f"- Executive mechanism: {record['executive_mechanism']}")
            lines.append(
                "- Proof surfaces: "
                + ", ".join(f"`{item}`" for item in record["proof_surfaces"])
            )
            lines.append(
                "- Executable paths: "
                + ", ".join(f"`{item}`" for item in record["executable_paths"])
            )
            lines.append(f"- If removed: {record['removal_effect']}")
            lines.append(f"- Audit rationale: {record['rationale']}")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def write_live_code_audit(
    audit: dict[str, object],
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "live-code.json"
    markdown_path = output_dir / "live-code.md"
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(audit), encoding="utf-8")
    return json_path, markdown_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a bounded internal quality audit for live Cortex code."
    )
    parser.add_argument(
        "--scope",
        default="live-code",
        choices=("live-code",),
        help="Bounded audit scope to render.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to write generated audit evidence into.",
    )
    args = parser.parse_args(argv)

    if args.scope != "live-code":
        raise SystemExit(f"Unsupported audit scope: {args.scope}")
    audit = build_live_code_audit(ROOT)
    json_path, markdown_path = write_live_code_audit(
        audit,
        output_dir=Path(args.output_dir),
    )
    print(
        json.dumps(
            {
                "scope": audit["scope"],
                "module_count": audit["module_count"],
                "dead_weight_paths": audit["dead_weight_paths"],
                "json": str(json_path.relative_to(ROOT)),
                "markdown": str(markdown_path.relative_to(ROOT)),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
