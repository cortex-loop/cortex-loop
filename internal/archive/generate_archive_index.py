#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "internal" / "archive" / "manifest.json"
ARCHIVE_DOC_PATH = ROOT / "docs" / "archive" / "README.md"


def load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def render_archive_index(payload: dict[str, object]) -> str:
    lines: list[str] = [
        "# Archive Index",
        "",
        "Surface: archive",
        "",
        "_Generated from `internal/archive/manifest.json`. Edit the manifest, then run `python3 internal/archive/generate_archive_index.py`._",
        "",
        "This archive is reference-only. It does not define live Cortex truth.",
        "",
        "## Narrative Archive",
        "",
    ]
    for entry in payload["narrative_roots"]:
        lines.append(f"- `{entry['path']}`")
        lines.append(f"  Purpose: {entry['purpose']}")
    lines.extend(["", "## Retained Evidence Refs", ""])
    for entry in payload["retained_evidence_refs"]:
        lines.append(f"- `{entry['label']}` -> `{entry['ref']}`")
        lines.append(f"  Purpose: {entry['purpose']}")
        lines.append(f"  Restore: `{entry['restore_hint']}`")
    lines.extend(["", "## Archived Branch Ledger", ""])
    for entry in payload["retired_branches"]:
        lines.append(f"- `{entry['branch']}` @ `{entry['head']}`")
        lines.append(f"  Purpose: {entry['purpose']}")
        if entry.get("disposition"):
            lines.append(f"  Disposition: {entry['disposition']}")
    lines.extend(["", "## Offloaded Payloads", ""])
    for entry in payload["offloaded_payloads"]:
        paths = ", ".join(f"`{path}`" for path in entry["paths"])
        lines.append(f"- `{entry['id']}`")
        lines.append(f"  Paths: {paths}")
        lines.append(f"  Restore ref: `{entry['restore_ref']}`")
        lines.append(f"  Restore hint: `{entry['restore_hint']}`")
        lines.append(f"  Local stub: `{entry['local_stub']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the archive index doc.")
    parser.add_argument("--check", action="store_true", help="Fail if the archive index is out of date.")
    args = parser.parse_args()

    rendered = render_archive_index(load_manifest())
    if args.check:
        current = ARCHIVE_DOC_PATH.read_text(encoding="utf-8") if ARCHIVE_DOC_PATH.exists() else ""
        if current != rendered:
            raise SystemExit(
                "docs/archive/README.md is out of date. Run python3 internal/archive/generate_archive_index.py"
            )
        return 0

    ARCHIVE_DOC_PATH.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
