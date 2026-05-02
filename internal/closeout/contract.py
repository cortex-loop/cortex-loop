#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT_ENV_VAR = "CORTEX_REPO_WORKFLOW_ROOT"
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = 1
VALID_MODES = {"close-session", "finalize"}
VALID_PROFILES = {"standard", "load_bearing"}
VALID_SURFACES = {"product", "experimental", "lab", "internal"}
VALID_AUDIT_STATUSES = {"pass", "fail"}
VALID_COMPLETENESS_STATES = {"implemented", "explicit_zero", "future_not_active"}
CODEX_MISSION_GRAPH_VALIDATOR_COMMAND = (
    "python3 internal/workflow/repo_workflow.py grid-validate --mode closeout"
)
# The patterns below detect closeout claims of "full V2 communication"
# closure; they exist because the V2 communication bridge postmortem
# (preserved at origin/archive/v2-bridge-and-constraint-fidelity-loop)
# identified that closeouts were claiming closure without an
# agent_loop_guard payload + a passing report. Any closeout that asserts
# one of these claims must declare an agent_loop_guard subobject; without
# one the claim is rejected.
FULL_COMMUNICATION_COMPLETION_CLAIM_PATTERNS = (
    re.compile(r"\bfull v2 communication(?: closure)? (?:is )?(?:proven|passed|complete|closed)\b"),
    re.compile(r"\bfully communicat(?:es|ed|ing)\b"),
    re.compile(r"\b(?:closed|closes|closing) the (?:v2 )?communication gap\b"),
    re.compile(r"\b(?:claude|codex) cli live watchlist (?:gate|gates) (?:has |have )?passed\b"),
    re.compile(r"\bfully model-visible\b"),
)
LOAD_BEARING_PACKET_DOC_RE = re.compile(r"^docs/CORTEX_V2_[^/]+\.md$")
MANAGED_SESSION_BRANCH_RE = re.compile(
    r"^(codex|claude|maint)/(?P<stamp>\d{8}-\d{6})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
# Substantive-content threshold for load-bearing reflection fields. The
# threshold replaces the v1 PHILOSOPHY_AUDIT rubber-stamp ritual: every
# field that asks for substantive reflection must contain enough text to
# carry an actual answer, and must not match the handwave patterns the
# old ritual tolerated. The number is small enough not to penalize tight
# writing but large enough to refuse "fine" / "n/a" / "looks good."
MIN_SUBSTANTIVE_CHARS = 16
HANDWAVE_PHRASE_PATTERNS = (
    re.compile(r"^(?:yes|no|n/?a|none|fine|good|ok|okay|tbd|todo|unsure|maybe|sure|nope|yep)\.?$", re.IGNORECASE),
    re.compile(r"^looks?\s+(?:good|fine|clean|great|right)\.?$", re.IGNORECASE),
    re.compile(r"^(?:no\s+(?:issues?|concerns?|problems?|comments?))\.?$", re.IGNORECASE),
    re.compile(r"^(?:nothing\s+(?:to\s+(?:add|note|report)|notable))\.?$", re.IGNORECASE),
    re.compile(r"^(?:see\s+above|same\s+as\s+above|as\s+stated|as\s+above|ditto)\.?$", re.IGNORECASE),
)


def is_cortex_path(path: str) -> bool:
    """Return True for paths that participate in the connectivity-trace contract.

    The connectivity requirement is a Cortex-specific anti-drift rule:
    every change to cortex/** must trace a path from the change to what
    the model receives or does, otherwise it is closed-loop drift. The
    rule applies to the cortex package only; lab/, internal/, tests/,
    and doc surfaces have their own discipline and do not need a
    connectivity_trace field.
    """
    return path.strip().startswith("cortex/")


def _root() -> Path:
    configured = os.environ.get(ROOT_ENV_VAR)
    if configured:
        return Path(configured).resolve()
    return DEFAULT_ROOT


def _capture_optional(cmd: list[str], *, cwd: Path | None = None) -> str | None:
    proc = subprocess.run(
        cmd,
        cwd=cwd or _root(),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _current_branch(*, cwd: Path | None = None) -> str:
    output = _capture_optional(["git", "branch", "--show-current"], cwd=cwd)
    if not output:
        raise SystemExit("Unable to determine the current git branch for closeout contract handling.")
    return output


def _staged_paths(*, cwd: Path | None = None) -> list[str]:
    output = _capture_optional(["git", "diff", "--cached", "--name-only"], cwd=cwd)
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _worktree_paths(*, cwd: Path | None = None) -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain=1", "--untracked-files=all"],
        cwd=cwd or _root(),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not proc.stdout:
        return []
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            paths.append(path)
    return paths


def _changed_paths_between(base_ref: str, head_ref: str, *, cwd: Path | None = None) -> list[str]:
    output = _capture_optional(["git", "diff", "--name-only", f"{base_ref}..{head_ref}"], cwd=cwd)
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _origin_main_exists(*, cwd: Path | None = None) -> bool:
    return _capture_optional(["git", "rev-parse", "--verify", "origin/main"], cwd=cwd) is not None


def _is_managed_session_branch(branch: str) -> bool:
    return MANAGED_SESSION_BRANCH_RE.fullmatch(branch) is not None


def _normalize_paths(paths: list[str]) -> list[str]:
    return sorted({path.strip() for path in paths if path.strip()})


def is_load_bearing_path(path: str) -> bool:
    normalized = path.strip()
    if not normalized:
        return False
    if normalized.startswith(("cortex/", "lab/")):
        return True
    if normalized == "AGENTS.md":
        return True
    if normalized in {"docs/internal/REPO_WORKFLOW.md", "internal/Makefile"}:
        return True
    if normalized.startswith(("internal/workflow/", "internal/closeout/")):
        return True
    if normalized in {"internal/truth/cortex_status.json", "docs/CORTEX_STATUS.md"}:
        return True
    return LOAD_BEARING_PACKET_DOC_RE.fullmatch(normalized) is not None


def infer_profile(reviewed_paths: list[str]) -> str:
    return "load_bearing" if any(is_load_bearing_path(path) for path in reviewed_paths) else "standard"


def expected_reviewed_paths(
    *,
    mode: str,
    branch: str | None = None,
    base_ref: str | None = None,
    cwd: Path | None = None,
) -> list[str]:
    if mode not in VALID_MODES:
        raise SystemExit(f"Unsupported closeout contract mode '{mode}'.")
    cwd = cwd or _root()
    branch = branch or _current_branch(cwd=cwd)
    if mode == "finalize":
        staged = _normalize_paths(_staged_paths(cwd=cwd))
        return staged or _normalize_paths(_worktree_paths(cwd=cwd))
    staged = _normalize_paths(_staged_paths(cwd=cwd))
    if staged:
        return staged
    worktree = _normalize_paths(_worktree_paths(cwd=cwd))
    if worktree:
        return worktree
    if base_ref is None:
        base_ref = "origin/main" if _is_managed_session_branch(branch) and _origin_main_exists(cwd=cwd) else "main"
    return _normalize_paths(_changed_paths_between(base_ref, branch, cwd=cwd))


def scaffold_payload(*, branch: str, mode: str, reviewed_paths: list[str]) -> dict[str, Any]:
    profile = infer_profile(reviewed_paths)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "branch": branch,
        "mode": mode,
        "profile": profile,
        "reviewed_paths": _normalize_paths(reviewed_paths),
        "seam": {
            "slug": "",
            "surface": "",
            "executive_benefit": "",
            "why_now": "",
        },
        "residuals": {
            "fixed_now": [],
            "intentionally_deferred": [],
            "still_underfit": [],
            "zeroed_or_stubbed_terms": [],
        },
        "hostile_review": {
            "engineer": "",
            "mathematician": "",
            "neuroscientist": "",
        },
        "claims": {
            "earned_now": [],
            "forbidden_still": [],
        },
        "north_light_audit": {
            "microkernel_boundary": {"status": "", "note": ""},
            "repo_governance_leakage": {"status": "", "note": ""},
            "host_specific_policy_fork": {"status": "", "note": ""},
            "generic_bloat": {"status": "", "note": ""},
        },
    }
    if profile == "load_bearing":
        payload["governing_locks"] = {
            "governing_principle": "",
            "executive_skill": "",
            "product_metric": "",
            "guardrail": "",
            "kill_rule": "",
        }
        payload["law_to_code_completeness"] = []
        # Connectivity trace is required when a load-bearing seam touches
        # any cortex/** path. The trace forces the agent to articulate
        # the path from the change to what the model receives or does;
        # an empty path on a `product` surface is the closed-loop drift
        # error and is rejected by validation. For non-cortex/** load-
        # bearing seams the field is scaffolded but stays optional.
        if any(is_cortex_path(path) for path in reviewed_paths):
            payload["connectivity_trace"] = {
                "claim": "",
                "path": [],
                "if_empty_why": None,
            }
            payload["product_spine"] = {
                "executive_capability": "",
                "state_law_path": [],
                "enforcement_decision": "",
                "host_action": "",
                "model_io_effect": "",
                "fixture_boundary": "",
                "non_fixture_controls": [],
            }
    if branch.startswith("codex/") and reviewed_paths:
        payload["mission_reflection_graph"] = {
            "validator": CODEX_MISSION_GRAPH_VALIDATOR_COMMAND,
            "validated": False,
            "note": "",
        }
    stacked_reason = _read_stacked_session_reason(branch)
    if stacked_reason is not None:
        payload["stacked_session_reason"] = stacked_reason
    return payload


def _read_stacked_session_reason(branch: str) -> str | None:
    """Read the marker file written by start-session --allow-stacked.

    The marker is branch-scoped at
    `.cortex/closeout_contract/<branch>/stacked_session_reason.txt`.
    Returns None if the marker does not exist (the common case — most
    sessions do not use --allow-stacked).
    """
    marker = (
        _root()
        / ".cortex"
        / "closeout_contract"
        / Path(*branch.split("/"))
        / "stacked_session_reason.txt"
    )
    if not marker.exists():
        return None
    try:
        text = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _artifact_dir(root: Path, branch: str) -> Path:
    return root / ".cortex" / "closeout_contract" / Path(*branch.split("/"))


def resolve_artifact_paths(root: Path, branch: str) -> dict[str, Path]:
    branch_dir = _artifact_dir(root, branch)
    root_dir = root / ".cortex" / "closeout_contract"
    return {
        "branch_dir": branch_dir,
        "json_path": branch_dir / "closeout.json",
        "markdown_path": branch_dir / "closeout.md",
        "latest_json_path": root_dir / "latest.json",
        "latest_markdown_path": root_dir / "latest.md",
    }


def _load_payload(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Closeout contract is missing at {path}.") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Closeout contract at {path} is not valid JSON: {exc}.") from exc


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_markdown(payload: dict[str, Any]) -> str:
    def append_items(lines: list[str], items: list[str], *, empty: str) -> None:
        if items:
            lines.extend(f"- {item}" for item in items)
            return
        lines.append(f"- {empty}")

    lines = [
        "# Closeout Contract",
        "",
        f"- Branch: `{payload['branch']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Profile: `{payload['profile']}`",
        "",
        "## Seam",
        "",
        f"- Slug: `{payload['seam']['slug']}`",
        f"- Surface: `{payload['seam']['surface']}`",
        f"- Executive Benefit: {payload['seam']['executive_benefit'] or '<fill me>'}",
        f"- Why This Beats Direct Product Work Now: {payload['seam']['why_now'] or '<fill me>'}",
        "",
        "## Reviewed Paths",
        "",
    ]
    if payload["reviewed_paths"]:
        lines.extend(f"- `{path}`" for path in payload["reviewed_paths"])
    else:
        lines.append("- `<none>`")
    residuals = payload["residuals"]
    lines.extend(
        [
            "",
            "## Residuals",
            "",
            "### Fixed Now",
            "",
        ]
    )
    append_items(lines, residuals["fixed_now"], empty="`<fill me>`")
    lines.extend(["", "### Intentionally Deferred", ""])
    append_items(lines, residuals["intentionally_deferred"], empty="`<none>`")
    lines.extend(["", "### Still Underfit", ""])
    append_items(lines, residuals["still_underfit"], empty="`<none>`")
    lines.extend(["", "### Zeroed Or Stubbed Terms", ""])
    append_items(lines, residuals["zeroed_or_stubbed_terms"], empty="`<none>`")
    lines.extend(["", "## Hostile Review", ""])
    for lens in ("engineer", "mathematician", "neuroscientist"):
        lines.append(f"- {lens.title()}: {payload['hostile_review'][lens] or '<fill me>'}")
    lines.extend(["", "## Claims", ""])
    earned = payload["claims"]["earned_now"]
    forbidden = payload["claims"]["forbidden_still"]
    lines.extend(f"- Earned: {item}" for item in earned) if earned else lines.append("- Earned: `<fill me>`")
    lines.extend(f"- Forbidden: {item}" for item in forbidden) if forbidden else lines.append("- Forbidden: `<fill me>`")
    graph = payload.get("mission_reflection_graph")
    if isinstance(graph, dict):
        lines.extend(["", "## Mission Reflection Graph", ""])
        lines.append(f"- Validator: `{graph.get('validator') or '<fill me>'}`")
        lines.append(f"- Validated: `{graph.get('validated')}`")
        lines.append(f"- Note: {graph.get('note') or '<fill me>'}")
    lines.extend(["", "## North Light Audit", ""])
    for key, entry in payload["north_light_audit"].items():
        label = key.replace("_", " ").title()
        lines.append(f"- {label}: `{entry['status'] or 'unset'}` — {entry['note'] or '<fill me>'}")
    if payload["profile"] == "load_bearing":
        lines.extend(["", "## Governing Locks", ""])
        for key, value in payload["governing_locks"].items():
            label = key.replace("_", " ").title()
            lines.append(f"- {label}: {value or '<fill me>'}")
        lines.extend(["", "## Law To Code Completeness", ""])
        rows = payload.get("law_to_code_completeness", [])
        if not rows:
            lines.append("- `<none recorded>`")
        for row in rows:
            lines.append(
                f"- `{row['term']}`: `{row['state']}`; code={', '.join(row['code_refs']) or '<none>'}; proof={', '.join(row['proof_refs']) or '<none>'}; note={row['note']}"
            )
        connectivity = payload.get("connectivity_trace")
        if isinstance(connectivity, dict):
            lines.extend(["", "## Connectivity Trace", ""])
            lines.append(
                f"- Claim: {connectivity.get('claim') or '<fill me>'}"
            )
            path_steps = connectivity.get("path", []) or []
            if path_steps:
                lines.append("- Path:")
                for step in path_steps:
                    lines.append(f"  - {step}")
            else:
                lines.append("- Path: `<empty>`")
            if_empty_why = connectivity.get("if_empty_why")
            if if_empty_why:
                lines.append(f"- If empty why: {if_empty_why}")
        product_spine = payload.get("product_spine")
        if isinstance(product_spine, dict):
            lines.extend(["", "## Product Spine", ""])
            lines.append(
                f"- Executive Capability: {product_spine.get('executive_capability') or '<fill me>'}"
            )
            state_law_path = product_spine.get("state_law_path", []) or []
            if state_law_path:
                lines.append("- State Law Path:")
                for step in state_law_path:
                    lines.append(f"  - {step}")
            else:
                lines.append("- State Law Path: `<empty>`")
            lines.append(
                f"- Enforcement Decision: {product_spine.get('enforcement_decision') or '<fill me>'}"
            )
            lines.append(f"- Host Action: {product_spine.get('host_action') or '<fill me>'}")
            lines.append(
                f"- Model I/O Effect: {product_spine.get('model_io_effect') or '<fill me>'}"
            )
            lines.append(
                f"- Fixture Boundary: {product_spine.get('fixture_boundary') or '<fill me>'}"
            )
            controls = product_spine.get("non_fixture_controls", []) or []
            if controls:
                lines.append("- Non-Fixture Controls:")
                for control in controls:
                    lines.append(f"  - {control}")
            else:
                lines.append("- Non-Fixture Controls: `<empty>`")
    lines.extend(["", "## Final Handoff Mirror", ""])
    lines.extend(["### Fixed now", ""])
    append_items(lines, residuals["fixed_now"], empty="`<fill me>`")
    lines.extend(["", "### Intentionally deferred", ""])
    append_items(lines, residuals["intentionally_deferred"], empty="`<none>`")
    lines.extend(["", "### Still underfit", ""])
    append_items(lines, residuals["still_underfit"], empty="`<none>`")
    lines.extend(["", "### Zeroed or stubbed terms", ""])
    append_items(lines, residuals["zeroed_or_stubbed_terms"], empty="`<none>`")
    lines.extend(["", "### Hostile reviewer critiques", ""])
    for lens in ("engineer", "mathematician", "neuroscientist"):
        lines.append(f"- {lens.title()}: {payload['hostile_review'][lens] or '<fill me>'}")
    lines.extend(["", "### Claim earned now", ""])
    append_items(lines, payload["claims"]["earned_now"], empty="`<fill me>`")
    lines.extend(["", "### Claim still forbidden", ""])
    append_items(lines, payload["claims"]["forbidden_still"], empty="`<fill me>`")
    return "\n".join(lines) + "\n"


def write_artifacts(root: Path, payload: dict[str, Any]) -> dict[str, Path]:
    paths = resolve_artifact_paths(root, str(payload["branch"]))
    _write_json(paths["json_path"], payload)
    markdown = render_markdown(payload)
    paths["markdown_path"].parent.mkdir(parents=True, exist_ok=True)
    paths["markdown_path"].write_text(markdown, encoding="utf-8")
    paths["latest_json_path"].parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(paths["json_path"], paths["latest_json_path"])
    shutil.copyfile(paths["markdown_path"], paths["latest_markdown_path"])
    return paths


def _require_string(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Closeout contract field '{field_name}' must be a non-empty string.")


def _require_string_list(value: Any, field_name: str, *, allow_empty: bool = True) -> None:
    if not isinstance(value, list):
        raise SystemExit(f"Closeout contract field '{field_name}' must be a list of non-empty strings.")
    if not allow_empty and not value:
        raise SystemExit(f"Closeout contract field '{field_name}' must not be empty.")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise SystemExit(f"Closeout contract field '{field_name}' must contain only non-empty strings.")


def is_handwave_phrase(value: str) -> bool:
    """Return True when value matches a known reflection-handwave pattern.

    The patterns codify the failure modes the v1 PHILOSOPHY_AUDIT block
    tolerated: single-word answers ("yes"/"none"), template fillers
    ("looks good"/"no concerns"), and back-references ("see above").
    Substantive reflection cannot pass through any of these.
    """
    text = value.strip()
    return any(pattern.fullmatch(text) for pattern in HANDWAVE_PHRASE_PATTERNS)


def _require_substantive(value: Any, field_name: str) -> None:
    """Validate that a reflection field carries substantive content.

    Combines _require_string's non-empty check with the substantive-content
    rules: the value must be at least MIN_SUBSTANTIVE_CHARS long and must
    not match any handwave-phrase pattern. Used for load-bearing
    reflection fields (north-light notes, hostile-review lenses,
    governing-locks fields, residuals.fixed_now items, claims).
    """
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Closeout contract field '{field_name}' must be a non-empty string.")
    text = value.strip()
    if len(text) < MIN_SUBSTANTIVE_CHARS:
        raise SystemExit(
            f"Closeout contract field '{field_name}' is too short to carry "
            f"substantive reflection: needs at least {MIN_SUBSTANTIVE_CHARS} "
            f"characters, got {len(text)}. Replace handwave with a real answer."
        )
    if is_handwave_phrase(text):
        raise SystemExit(
            f"Closeout contract field '{field_name}' matches a handwave "
            f"pattern ({text!r}); the v1 PHILOSOPHY_AUDIT ritual tolerated "
            f"these but the substantive-content rule rejects them. Replace "
            f"with a real answer that names specific evidence."
        )


def _require_substantive_list_items(value: list[Any], field_name: str) -> None:
    for index, item in enumerate(value):
        _require_substantive(item, f"{field_name}[{index}]")


def validate_payload(
    payload: dict[str, Any],
    *,
    expected_mode: str,
    expected_branch: str,
    expected_reviewed_paths: list[str],
) -> dict[str, Any]:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(f"Closeout contract schema_version must be {SCHEMA_VERSION}.")
    if payload.get("mode") != expected_mode:
        raise SystemExit(
            f"Closeout contract mode mismatch: expected '{expected_mode}', found '{payload.get('mode', '')}'."
        )
    if payload.get("branch") != expected_branch:
        raise SystemExit(
            f"Closeout contract branch mismatch: expected '{expected_branch}', found '{payload.get('branch', '')}'."
        )
    actual_paths = _normalize_paths(payload.get("reviewed_paths", []))
    expected_paths = _normalize_paths(expected_reviewed_paths)
    if actual_paths != expected_paths:
        raise SystemExit(
            "Closeout contract reviewed_paths are stale or incomplete: "
            f"expected {expected_paths}, found {actual_paths}."
        )
    expected_profile = infer_profile(expected_paths)
    profile = payload.get("profile")
    if profile not in VALID_PROFILES:
        raise SystemExit(f"Closeout contract profile must be one of {sorted(VALID_PROFILES)}.")
    if profile != expected_profile:
        raise SystemExit(
            f"Closeout contract profile mismatch: expected '{expected_profile}', found '{profile}'."
        )

    seam = payload.get("seam")
    if not isinstance(seam, dict):
        raise SystemExit("Closeout contract seam must be an object.")
    _require_string(seam.get("slug"), "seam.slug")
    surface = seam.get("surface")
    if surface not in VALID_SURFACES:
        raise SystemExit(f"Closeout contract seam.surface must be one of {sorted(VALID_SURFACES)}.")
    _require_string(seam.get("executive_benefit"), "seam.executive_benefit")
    _require_string(seam.get("why_now"), "seam.why_now")

    residuals = payload.get("residuals")
    if not isinstance(residuals, dict):
        raise SystemExit("Closeout contract residuals must be an object.")
    _require_string_list(residuals.get("fixed_now"), "residuals.fixed_now", allow_empty=False)
    _require_string_list(
        residuals.get("intentionally_deferred"), "residuals.intentionally_deferred", allow_empty=True
    )
    _require_string_list(residuals.get("still_underfit"), "residuals.still_underfit", allow_empty=True)
    _require_string_list(
        residuals.get("zeroed_or_stubbed_terms"), "residuals.zeroed_or_stubbed_terms", allow_empty=True
    )
    # Substantive-content rule for fixed_now: each item must carry a real
    # answer (>=MIN_SUBSTANTIVE_CHARS, no handwave patterns). Other
    # residual buckets stay non-empty-string-only so deferred lists do
    # not get penalized for legitimate brevity.
    _require_substantive_list_items(residuals.get("fixed_now"), "residuals.fixed_now")

    hostile_review = payload.get("hostile_review")
    if not isinstance(hostile_review, dict):
        raise SystemExit("Closeout contract hostile_review must be an object.")
    for lens in ("engineer", "mathematician", "neuroscientist"):
        _require_substantive(hostile_review.get(lens), f"hostile_review.{lens}")

    claims = payload.get("claims")
    if not isinstance(claims, dict):
        raise SystemExit("Closeout contract claims must be an object.")
    _require_string_list(claims.get("earned_now"), "claims.earned_now", allow_empty=False)
    _require_string_list(claims.get("forbidden_still"), "claims.forbidden_still", allow_empty=False)
    _require_substantive_list_items(claims.get("earned_now"), "claims.earned_now")
    _require_substantive_list_items(claims.get("forbidden_still"), "claims.forbidden_still")

    if expected_branch.startswith("codex/") and expected_paths:
        graph = payload.get("mission_reflection_graph")
        if not isinstance(graph, dict):
            raise SystemExit(
                "Codex closeout contracts must include mission_reflection_graph "
                "recording the mandatory `grid-validate` final-graph check. "
                "Codex App has a repo-local Stop hook when the trusted `.codex/` "
                "layer loads, but non-hook Codex surfaces still need this "
                "session-boundary validator evidence."
            )
        if graph.get("validator") != CODEX_MISSION_GRAPH_VALIDATOR_COMMAND:
            raise SystemExit(
                "mission_reflection_graph.validator must be "
                f"`{CODEX_MISSION_GRAPH_VALIDATOR_COMMAND}`."
            )
        if graph.get("validated") is not True:
            raise SystemExit(
                "mission_reflection_graph.validated must be true for Codex "
                "closeouts. Run the final graph through grid-validate before "
                "closing the session."
            )
        _require_substantive(graph.get("note"), "mission_reflection_graph.note")

    north_light_audit = payload.get("north_light_audit")
    if not isinstance(north_light_audit, dict):
        raise SystemExit("Closeout contract north_light_audit must be an object.")
    for key in (
        "microkernel_boundary",
        "repo_governance_leakage",
        "host_specific_policy_fork",
        "generic_bloat",
    ):
        entry = north_light_audit.get(key)
        if not isinstance(entry, dict):
            raise SystemExit(f"Closeout contract north_light_audit.{key} must be an object.")
        if entry.get("status") not in VALID_AUDIT_STATUSES:
            raise SystemExit(
                f"Closeout contract north_light_audit.{key}.status must be one of {sorted(VALID_AUDIT_STATUSES)}."
            )
        _require_substantive(entry.get("note"), f"north_light_audit.{key}.note")

    if profile == "load_bearing":
        governing_locks = payload.get("governing_locks")
        if not isinstance(governing_locks, dict):
            raise SystemExit("Load-bearing closeout contracts must include governing_locks.")
        for key in ("governing_principle", "executive_skill", "product_metric", "guardrail", "kill_rule"):
            _require_substantive(governing_locks.get(key), f"governing_locks.{key}")
        law_to_code = payload.get("law_to_code_completeness")
        if not isinstance(law_to_code, list):
            raise SystemExit("Load-bearing closeout contracts must include law_to_code_completeness as a list.")
        if not law_to_code:
            raise SystemExit("Load-bearing closeout contracts must include at least one law_to_code_completeness row.")
        for index, row in enumerate(law_to_code):
            if not isinstance(row, dict):
                raise SystemExit("Each law_to_code_completeness entry must be an object.")
            _require_string(row.get("term"), f"law_to_code_completeness[{index}].term")
            if row.get("state") not in VALID_COMPLETENESS_STATES:
                raise SystemExit(
                    "law_to_code_completeness entries must use state one of "
                    f"{sorted(VALID_COMPLETENESS_STATES)}."
                )
            _require_string_list(
                row.get("code_refs"), f"law_to_code_completeness[{index}].code_refs", allow_empty=False
            )
            _require_string_list(
                row.get("proof_refs"), f"law_to_code_completeness[{index}].proof_refs", allow_empty=False
            )
            _require_string(row.get("note"), f"law_to_code_completeness[{index}].note")
            # Optional structural join into status registry math_to_code_map.
            # Free-text `term` stays for display and historical compatibility;
            # `math_object_id`, when present, must be a non-empty string and
            # mechanically join to a math_to_code_map entry. Future seam-side
            # validators can treat unknown IDs as drift; today the field is
            # advisory but pinned in shape.
            if "math_object_id" in row:
                math_object_id = row["math_object_id"]
                if math_object_id is not None and not (
                    isinstance(math_object_id, str) and math_object_id.strip()
                ):
                    raise SystemExit(
                        f"law_to_code_completeness[{index}].math_object_id must be a "
                        "non-empty string when present."
                    )

        # Connectivity-trace rule. When a load-bearing closeout touches
        # any cortex/** path, the trace makes the agent articulate the
        # path from the change to the model's input or output. An empty
        # path on a `product` surface is the closed-loop drift error and
        # is rejected; an empty path on `experimental` or `lab` is
        # allowed but requires `if_empty_why` to explain why monitoring
        # / instrumentation is the correct framing.
        cortex_paths_present = any(is_cortex_path(path) for path in expected_paths)
        connectivity = payload.get("connectivity_trace")
        if cortex_paths_present:
            if not isinstance(connectivity, dict):
                raise SystemExit(
                    "Load-bearing closeouts touching cortex/** must include "
                    "a connectivity_trace object {claim, path, if_empty_why}. "
                    "See AGENTS.md `## Anti-Drift` and docs/CORTEX.md §3 for "
                    "the closed-loop drift discipline."
                )
            _require_substantive(
                connectivity.get("claim"), "connectivity_trace.claim"
            )
            path = connectivity.get("path")
            if not isinstance(path, list) or not all(
                isinstance(step, str) and step.strip() for step in path
            ):
                raise SystemExit(
                    "connectivity_trace.path must be a list of non-empty "
                    "strings naming the path from the change to the model's "
                    "input or output (e.g. file -> file -> host adapter -> "
                    "model request)."
                )
            if not path:
                if surface == "product":
                    raise SystemExit(
                        "connectivity_trace.path is empty on a `product` "
                        "surface; this is closed-loop drift. Either trace a "
                        "path from the change to the model, or downgrade "
                        "seam.surface to `experimental` or `lab` and "
                        "explain in connectivity_trace.if_empty_why why "
                        "monitoring / instrumentation is the correct "
                        "framing. See docs/CORTEX.md §3."
                    )
                _require_substantive(
                    connectivity.get("if_empty_why"),
                    "connectivity_trace.if_empty_why",
                )
            else:
                # When path is non-empty, if_empty_why may be null or a
                # supplementary note; do not require substantive content.
                if connectivity.get("if_empty_why") is not None and not (
                    isinstance(connectivity["if_empty_why"], str)
                    and connectivity["if_empty_why"].strip()
                ):
                    raise SystemExit(
                        "connectivity_trace.if_empty_why must be null or a "
                        "non-empty string when path is populated."
                    )
            if surface == "product":
                product_spine = payload.get("product_spine")
                if not isinstance(product_spine, dict):
                    raise SystemExit(
                        "Product closeouts touching cortex/** must include "
                        "product_spine {executive_capability, state_law_path, "
                        "enforcement_decision, host_action, model_io_effect, "
                        "fixture_boundary, non_fixture_controls}. This keeps "
                        "fixture evidence from becoming product Cortex policy."
                    )
                _require_substantive(
                    product_spine.get("executive_capability"),
                    "product_spine.executive_capability",
                )
                _require_string_list(
                    product_spine.get("state_law_path"),
                    "product_spine.state_law_path",
                    allow_empty=False,
                )
                _require_substantive_list_items(
                    product_spine.get("state_law_path"),
                    "product_spine.state_law_path",
                )
                for key in (
                    "enforcement_decision",
                    "host_action",
                    "model_io_effect",
                    "fixture_boundary",
                ):
                    _require_substantive(
                        product_spine.get(key),
                        f"product_spine.{key}",
                    )
                _require_string_list(
                    product_spine.get("non_fixture_controls"),
                    "product_spine.non_fixture_controls",
                    allow_empty=False,
                )
                _require_substantive_list_items(
                    product_spine.get("non_fixture_controls"),
                    "product_spine.non_fixture_controls",
                )

    _validate_agent_loop_guard_claims(payload)

    if "lesson_for_cortex_doc" in payload:
        lesson = payload["lesson_for_cortex_doc"]
        # Optional channel for narrative-update candidates. When a session
        # produces a load-bearing lesson worth landing in CORTEX.md §3
        # (V1 → V2 evolution), the closeout records it here so the next
        # narrative-update session can pick it up. The field is just a
        # marker; the actual prose update is manual.
        if lesson is not None and not (isinstance(lesson, str) and lesson.strip()):
            raise SystemExit(
                "Closeout contract field 'lesson_for_cortex_doc' must be a "
                "non-empty string when present. Use it to mark a candidate "
                "lesson for inclusion in CORTEX.md §3."
            )

    if "stacked_session_reason" in payload:
        reason = payload["stacked_session_reason"]
        if reason is not None and not (isinstance(reason, str) and reason.strip()):
            raise SystemExit(
                "Closeout contract field 'stacked_session_reason' must be a "
                "non-empty string when present. The reason is recorded by "
                "start-session --allow-stacked --stacked-reason \"<text>\" "
                "to leave an audit trail of why parallel session work was "
                "necessary."
            )

    return payload


def _full_communication_completion_claim_present(payload: dict[str, Any]) -> bool:
    """Detect closeout claims of full V2 communication closure.

    Searches `residuals.fixed_now` and `claims.earned_now` for any phrasing
    that asserts the V2 model-visible communication bridge has fully passed
    or been closed. The specific patterns are recovered from the bridge
    postmortem; the postmortem identified that closeouts were claiming
    closure without the agent_loop_guard payload that would have proved
    live evidence.
    """
    residuals = payload.get("residuals") if isinstance(payload.get("residuals"), dict) else {}
    claims = payload.get("claims") if isinstance(payload.get("claims"), dict) else {}
    claim_texts: list[str] = []
    for field_name in ("fixed_now",):
        values = residuals.get(field_name, [])
        if isinstance(values, list):
            claim_texts.extend(str(value).lower() for value in values)
    for field_name in ("earned_now",):
        values = claims.get(field_name, [])
        if isinstance(values, list):
            claim_texts.extend(str(value).lower() for value in values)
    return any(
        pattern.search(text)
        for text in claim_texts
        for pattern in FULL_COMMUNICATION_COMPLETION_CLAIM_PATTERNS
    )


def _validate_agent_loop_guard_claims(payload: dict[str, Any]) -> None:
    """Forward-armed bridge-postmortem guard.

    The closeout contract validates against the procedural shortcuts
    identified in the V2 communication bridge postmortem (preserved at
    origin/archive/v2-bridge-and-constraint-fidelity-loop). Specifically:

    - A closeout payload that introduces an `agent_loop_guard` subobject
      must have `require_full_communication_closure: true` and may not
      have `allow_blocked: true`.
    - A closeout that claims "full V2 communication closure",
      "fully model-visible", or "live watchlist passed" without an
      `agent_loop_guard` subobject is rejected.

    These constraints exist because their absence let the V2 bridge work
    be checkpointed before the live evidence that would have graduated it.
    See AGENTS.md `## Anti-Drift` and CLAUDE.md for the discipline.
    """
    completion_claim = _full_communication_completion_claim_present(payload)
    guard_config = payload.get("agent_loop_guard")
    if guard_config is None:
        if completion_claim:
            raise SystemExit(
                "Closeout contract: full V2 communication completion claims "
                "require an `agent_loop_guard` subobject with a passing report; "
                "the bridge postmortem identified naked completion claims as a "
                "procedural escape hatch. See AGENTS.md `## Anti-Drift`."
            )
        return
    if not isinstance(guard_config, dict):
        raise SystemExit(
            "Closeout contract field 'agent_loop_guard' must be an object when provided."
        )
    require_closure = guard_config.get("require_full_communication_closure", True)
    if require_closure is not True:
        raise SystemExit(
            "Closeout contract: `agent_loop_guard.require_full_communication_closure` "
            "must be true; the bridge postmortem identified opt-out via this field "
            "as a procedural escape hatch. Guarded V2 communication closeouts may "
            "not opt out of closure validation."
        )
    allow_blocked = bool(guard_config.get("allow_blocked", False))
    if allow_blocked:
        raise SystemExit(
            "Closeout contract: `agent_loop_guard.allow_blocked` is forbidden "
            "for closeout. Blocked live gates require operator action and cannot "
            "satisfy closure; the bridge postmortem identified --allow-blocked "
            "as the procedural escape hatch that let the V2 bridge work be "
            "checkpointed before live Claude/Codex proof was completed."
        )


def validate_contract(
    *,
    root: Path,
    mode: str,
    branch: str,
    reviewed_paths: list[str],
) -> dict[str, Any]:
    paths = resolve_artifact_paths(root, branch)
    payload = _load_payload(paths["json_path"])
    return validate_payload(
        payload,
        expected_mode=mode,
        expected_branch=branch,
        expected_reviewed_paths=reviewed_paths,
    )


def init_contract(*, root: Path, mode: str, branch: str | None = None) -> dict[str, Any]:
    branch = branch or _current_branch(cwd=root)
    reviewed_paths = expected_reviewed_paths(mode=mode, branch=branch, cwd=root)
    payload = scaffold_payload(branch=branch, mode=mode, reviewed_paths=reviewed_paths)
    paths = write_artifacts(root, payload)
    return {
        "branch": branch,
        "mode": mode,
        "profile": payload["profile"],
        "reviewed_paths": payload["reviewed_paths"],
        "json_path": str(paths["json_path"].relative_to(root)),
        "markdown_path": str(paths["markdown_path"].relative_to(root)),
    }


def render_contract(*, root: Path, branch: str | None = None) -> dict[str, Any]:
    branch = branch or _current_branch(cwd=root)
    paths = resolve_artifact_paths(root, branch)
    payload = _load_payload(paths["json_path"])
    rendered_paths = write_artifacts(root, payload)
    return {
        "branch": branch,
        "json_path": str(rendered_paths["json_path"].relative_to(root)),
        "markdown_path": str(rendered_paths["markdown_path"].relative_to(root)),
    }


def cli_validate(*, root: Path, mode: str, branch: str | None = None) -> dict[str, Any]:
    branch = branch or _current_branch(cwd=root)
    reviewed_paths = expected_reviewed_paths(mode=mode, branch=branch, cwd=root)
    payload = validate_contract(root=root, mode=mode, branch=branch, reviewed_paths=reviewed_paths)
    return {
        "branch": branch,
        "mode": mode,
        "profile": payload["profile"],
        "reviewed_paths": payload["reviewed_paths"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage the internal closeout contract artifact.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Scaffold a closeout contract for the current branch.")
    init_parser.add_argument("--mode", choices=sorted(VALID_MODES), required=True)
    init_parser.add_argument("--branch")

    render_parser = subparsers.add_parser("render", help="Render markdown from an existing closeout contract.")
    render_parser.add_argument("--branch")

    validate_parser = subparsers.add_parser("validate", help="Validate the current branch closeout contract.")
    validate_parser.add_argument("--mode", choices=sorted(VALID_MODES), required=True)
    validate_parser.add_argument("--branch")

    args = parser.parse_args(argv)
    root = _root()
    if args.command == "init":
        print(json.dumps(init_contract(root=root, mode=args.mode, branch=args.branch), indent=2, sort_keys=True))
        return 0
    if args.command == "render":
        print(json.dumps(render_contract(root=root, branch=args.branch), indent=2, sort_keys=True))
        return 0
    if args.command == "validate":
        print(json.dumps(cli_validate(root=root, mode=args.mode, branch=args.branch), indent=2, sort_keys=True))
        return 0
    raise SystemExit(f"Unhandled closeout contract command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
