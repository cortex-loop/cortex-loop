"""Shared Cortex Mission Reflection graph contract.

This module owns the end-of-chat graph schema and validator used by
``repo_workflow.py`` and the Claude Code Stop hook. Keeping the schema
here prevents the prior drift where the renderer and hook carried
parallel copies of row labels and validation rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

GRAPH_HEADER_MARKER = "## Cortex Mission Reflection"
TABLE_HEADER_MARKER = "| Field | Value |"
TABLE_SEPARATOR_MARKER = "|---|---|"
FORBIDDEN_SECTION_MARKER = "### "
GRAPH_MODES: tuple[str, ...] = ("exploration", "work", "closeout")
DEFAULT_GRAPH_MODE = "work"

MISSION_REFLECTION_FIELDS: tuple[tuple[str, str], ...] = (
    (
        "Mission: Cortex target",
        "which Cortex executive-function goal this turn served: continuity, focus, context adoption, brake, truthful closure, or capability-aware routing. Cite the mission surface.",
    ),
    (
        "Mission: Boundary judgment",
        "classify the turn as product Cortex, internal doctrine, lab/proof, monitor/scaffolding, or post-training territory, and justify why that boundary is correct.",
    ),
    (
        "Mission: Theory of improvement",
        "why this work should improve Cortex development or model behavior rather than merely changing repo machinery.",
    ),
    (
        "Mission: Model I/O path",
        "exact path to model input/output, or explicit 'none: internal/lab/governance only' with why that is acceptable.",
    ),
    (
        "Reflection: Plan vs actual",
        "planned intention mapped to realized implementation or analysis, with evidence from touched code/tests/docs when work happened.",
    ),
    (
        "Reflection: Quality judgment",
        "whether this was the best implementation, including tradeoffs and what would have made it better.",
    ),
    (
        "Reflection: Iteration evidence",
        "what failed, was caught, changed, or was corrected this turn; if nothing changed, explain why no iteration was needed.",
    ),
    (
        "Evidence: Earned",
        "structural or live evidence earned this turn, explicitly separating live-vs-structural claims.",
    ),
    (
        "Evidence: Not earned / forbidden",
        "claims still forbidden, especially model-output lift or product progress not actually earned.",
    ),
    (
        "Decision: Next ownership move",
        "continue, stop, split, revise, or return to product work, with reason.",
    ),
)

MISSION_REFLECTION_ROW_LABELS = tuple(label for label, _prompt in MISSION_REFLECTION_FIELDS)
EXPLORATION_GRAPH_ROW_LABELS: tuple[str, ...] = (
    "Repo: State",
    "Mission: Cortex target",
    "Mission: Boundary judgment",
    "Decision: Next ownership move",
    "Verdict",
)
WORK_GRAPH_ROW_LABELS: tuple[str, ...] = (
    "Repo: State",
    "Repo: Gates",
    *MISSION_REFLECTION_ROW_LABELS,
    "Verdict",
)
CLOSEOUT_GRAPH_ROW_LABELS: tuple[str, ...] = (
    "Repo: State",
    "Repo: Gates",
    *MISSION_REFLECTION_ROW_LABELS,
    "Closure: Metadata",
    "Verdict",
)
REQUIRED_GRAPH_ROW_LABELS = CLOSEOUT_GRAPH_ROW_LABELS
REQUIRED_GRAPH_ROW_LABELS_BY_MODE: dict[str, tuple[str, ...]] = {
    "exploration": EXPLORATION_GRAPH_ROW_LABELS,
    "work": WORK_GRAPH_ROW_LABELS,
    "closeout": CLOSEOUT_GRAPH_ROW_LABELS,
}
MISSION_ROW_LABELS_BY_MODE: dict[str, tuple[str, ...]] = {
    "exploration": (
        "Mission: Cortex target",
        "Mission: Boundary judgment",
        "Decision: Next ownership move",
    ),
    "work": MISSION_REFLECTION_ROW_LABELS,
    "closeout": MISSION_REFLECTION_ROW_LABELS,
}

CLOSURE_LEAK_MARKERS: tuple[str, ...] = (
    "Ending branch",
    "Verification summary",
    "Fixed now",
    "Claim earned now",
    "Status registry touched",
    "Closure: Metadata",
    "Final Handoff Mirror",
    "DOGFOOD_SIGNAL",
)

MISSION_REFLECTION_TEMPLATE_TOKEN = "mission reflection —"
CLOSURE_METADATA_TEMPLATE_TOKEN = "closure metadata —"
FILL_PLACEHOLDER_TOKEN = "<fill"
MISSION_REFLECTION_MIN_CHARS = 120
MISSION_REFLECTION_MIN_CHARS_BY_MODE: dict[str, int] = {
    "exploration": 60,
    "work": MISSION_REFLECTION_MIN_CHARS,
    "closeout": MISSION_REFLECTION_MIN_CHARS,
}
REQUIRED_REPO_CITATION_ROWS_BY_MODE: dict[str, int | str] = {
    "exploration": 1,
    "work": 3,
    "closeout": "all",
}

REPO_CITATION_PATTERN = re.compile(
    r"(docs/CORTEX\.md|internal/truth/cortex_status\.json|cortex/|tests/|CORTEX_V2_)"
)

STALE_DASHBOARD_ROW_PREFIX = "Progress:"
STALE_DASHBOARD_ROW_LABELS: tuple[str, ...] = (
    "bio_to_code matrix",
    "hosts",
    "shipping default",
    "current train",
    "next train",
    "research lines u/eval",
)
STALE_VERDICT_PHRASES: tuple[str, ...] = (
    "cleared for close-session",
)


@dataclass(frozen=True)
class GraphValidationResult:
    """Result of validating a rendered/filled mission graph."""

    ok: bool
    errors: tuple[str, ...]
    rows: dict[str, str]
    mode: str

    def reason(self) -> str:
        if self.ok:
            return "Cortex Mission Reflection graph is valid."
        return "\n".join(f"- {error}" for error in self.errors)


def table_cell(value: object) -> str:
    """Normalize a value for a single markdown table cell."""

    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "<br>")
    return text.replace("|", "\\|")


def graph_table(rows: list[tuple[str, str]]) -> str:
    """Render one two-column markdown table."""

    lines = [TABLE_HEADER_MARKER, TABLE_SEPARATOR_MARKER]
    for label, value in rows:
        lines.append(f"| **{table_cell(label)}** | {table_cell(value)} |")
    return "\n".join(lines)


def normalize_graph_mode(mode: str | None) -> str:
    """Return a supported graph mode, defaulting to work."""

    if mode is None:
        return DEFAULT_GRAPH_MODE
    if mode not in GRAPH_MODES:
        raise ValueError(f"unsupported mission reflection mode: {mode}")
    return mode


def compact_repo_state(snapshot: dict[str, object]) -> str:
    """Return branch/worktree/closeout/drift in one compact cell."""

    closeout = snapshot["closeout"]
    closeout_value = str(closeout.get("present"))
    profile = closeout.get("profile")
    if profile and closeout_value != "absent":
        closeout_value = f"{closeout_value} ({profile})"
    drift = snapshot.get("drift_signals", [])
    drift_value = "none" if not drift else "; ".join(str(item) for item in drift)
    return (
        f"branch `{snapshot['branch']}`; vs origin/main +{snapshot['ahead']} / "
        f"-{snapshot['behind']}; worktree {snapshot['worktree']}; "
        f"closeout {closeout_value}; drift {drift_value}"
    )


def compact_repo_gates(check_payload: dict[str, object]) -> str:
    """Return reflection-check verdict plus failures/gaps when present."""

    verdict = check_payload.get("verdict", "?")
    failures = [str(f) for f in check_payload.get("failures", [])]
    gaps = [str(g) for g in check_payload.get("gaps", [])]
    parts = [f"reflection-check `{verdict}`"]
    if failures:
        parts.append("failures: " + "; ".join(failures[:5]))
    if gaps:
        parts.append("gaps: " + "; ".join(gaps[:5]))
    if not failures and not gaps:
        parts.append("failures/gaps none")
    return "; ".join(parts)


def close_session_eligibility(check_payload: dict[str, object]) -> tuple[bool, str]:
    """Return whether this turn is eligible for close-session and why."""

    verdict = check_payload.get("verdict")
    if verdict != "PASS":
        return False, f"reflection-check verdict is {verdict}"
    snapshot = check_payload.get("snapshot")
    closeout = snapshot.get("closeout") if isinstance(snapshot, dict) else None
    if not isinstance(closeout, dict):
        return False, "snapshot has no closeout state"
    if closeout.get("present") == "absent":
        return False, "no closeout artifact is present"
    if not closeout.get("validates"):
        return False, "closeout artifact is present but does not validate"
    return True, "closeout artifact validates"


def format_verdict(check_payload: dict[str, object]) -> str:
    """Format turn verdict separately from close-session eligibility."""

    verdict = check_payload.get("verdict")
    failures = [str(f) for f in check_payload.get("failures", [])]
    gaps = [str(g) for g in check_payload.get("gaps", [])]
    eligible, eligibility_reason = close_session_eligibility(check_payload)
    eligibility = (
        f"Close-session eligibility: {'yes' if eligible else 'no'} — {eligibility_reason}."
    )
    if verdict == "FAIL":
        items = "; ".join((failures + gaps)[:10])
        detail = f" Continue work on: {items}." if items else ""
        return f"Turn verdict: ❌ FAIL — continue work.{detail} {eligibility}"
    if verdict == "GAPS":
        items = "; ".join(gaps[:10])
        detail = f" Review gaps: {items}." if items else ""
        return f"Turn verdict: ⚠️ GAPS — resolve or intentionally defer before closure.{detail} {eligibility}"
    return f"Turn verdict: ✅ PASS — mechanical gates clear for this turn. {eligibility}"


def closure_metadata_template(snapshot: dict[str, object]) -> str:
    """Return a compact metadata prompt for the agent to fill in place."""

    return (
        f"_[closure metadata — ending branch `{snapshot['branch']}`; commit hash "
        "or `no commit`; verification summary; returned to main yes/no; "
        "status registry touched keys or none; status doc regenerated yes/no; "
        "CORTEX.md regenerated yes/no]_"
    )


def dogfood_signal_rows() -> list[tuple[str, str]]:
    return [
        ("Dogfood: continuity_helped", "<fill: yes|no>"),
        ("Dogfood: blocker_surfaced", "<fill: yes|no>"),
        ("Dogfood: uncertainty_or_brake_used", "<fill: yes|no>"),
        ("Dogfood: truthful_closure", "<fill: yes|no>"),
        ("Dogfood: cortex_changed_next_action", "<fill: yes|no>"),
        ("Dogfood: note", "<fill: one sentence>"),
    ]


def _mission_fields_for_mode(mode: str) -> tuple[tuple[str, str], ...]:
    labels = set(MISSION_ROW_LABELS_BY_MODE[mode])
    return tuple((label, prompt) for label, prompt in MISSION_REFLECTION_FIELDS if label in labels)


def render_graph(
    *,
    snapshot: dict[str, object],
    check_payload: dict[str, object],
    mode: str = DEFAULT_GRAPH_MODE,
    dogfood_active: bool = False,
) -> str:
    """Render the per-turn Cortex Mission Reflection as one table."""

    graph_mode = normalize_graph_mode(mode)
    rows: list[tuple[str, str]] = [
        ("Repo: State", compact_repo_state(snapshot)),
    ]
    if graph_mode in {"work", "closeout"}:
        rows.append(("Repo: Gates", compact_repo_gates(check_payload)))
    for label, prompt in _mission_fields_for_mode(graph_mode):
        rows.append((label, f"_[{MISSION_REFLECTION_TEMPLATE_TOKEN} {prompt}]_"))
    if graph_mode == "closeout":
        rows.append(("Closure: Metadata", closure_metadata_template(snapshot)))
    if dogfood_active and graph_mode in {"work", "closeout"}:
        rows.extend(dogfood_signal_rows())
    rows.append(("Verdict", format_verdict(check_payload)))
    return "\n\n".join([GRAPH_HEADER_MARKER, graph_table(rows)])


def graph_text(text: str) -> str | None:
    graph_pos = text.find(GRAPH_HEADER_MARKER)
    if graph_pos == -1:
        return None
    return text[graph_pos:]


def parse_rows(text: str) -> dict[str, str]:
    """Parse the one-table graph into {row_label: cell_text}."""

    section = graph_text(text)
    if section is None:
        return {}
    rows: dict[str, str] = {}
    pattern = re.compile(r"^\| \*\*(?P<label>.*?)\*\* \| (?P<body>.*?) \|$", re.MULTILINE)
    for match in pattern.finditer(section):
        rows[match.group("label")] = match.group("body")
    return rows


def infer_graph_mode(text: str) -> str:
    """Infer validation mode from the rendered graph row set.

    The hook cannot know the user's intent, so it infers only from the
    assistant's own graph shape: closeout has Closure Metadata, work has
    repo gates or full reflection rows, and exploration is the compact shape.
    Missing or unparsable graphs fall back to work for a useful canonical
    skeleton in block feedback.
    """

    rows = parse_rows(text)
    if not rows:
        return DEFAULT_GRAPH_MODE
    if "Closure: Metadata" in rows or any("Metadata" in label for label in rows):
        return "closeout"
    work_only_labels = set(WORK_GRAPH_ROW_LABELS) - set(EXPLORATION_GRAPH_ROW_LABELS)
    if "Repo: Gates" in rows or any(label in rows for label in work_only_labels):
        return "work"
    return "exploration"


def clean_cell_text(text: str) -> str:
    """Normalize markdown-table cell text for validation checks."""

    text = text.replace("<br>", " ")
    text = text.replace("\\|", "|")
    text = re.sub(r"[_`*]", "", text)
    return " ".join(text.split())


def _shape_errors(text: str) -> list[str]:
    section = graph_text(text)
    if section is None:
        return [f"missing graph header `{GRAPH_HEADER_MARKER}`"]
    errors: list[str] = []
    if f"\n{FORBIDDEN_SECTION_MARKER}" in section:
        errors.append("forbidden `###` subsection inside graph")
    if section.count(TABLE_HEADER_MARKER) != 1:
        errors.append(f"expected exactly one `{TABLE_HEADER_MARKER}` table header")
    if section.count(TABLE_SEPARATOR_MARKER) != 1:
        errors.append(f"expected exactly one `{TABLE_SEPARATOR_MARKER}` table separator")
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped == GRAPH_HEADER_MARKER:
            continue
        if not stripped.startswith("|"):
            errors.append(f"non-table content inside or after graph: {stripped[:80]}")
            break
    return errors


def _required_row_errors(rows: dict[str, str], mode: str) -> list[str]:
    return [
        f"missing required row `{label}`"
        for label in REQUIRED_GRAPH_ROW_LABELS_BY_MODE[mode]
        if label not in rows
    ]


def _stale_dashboard_rows(rows: dict[str, str]) -> list[str]:
    stale: list[str] = []
    for label in rows:
        if label.startswith(STALE_DASHBOARD_ROW_PREFIX):
            stale.append(label)
        if any(label.endswith(item) for item in STALE_DASHBOARD_ROW_LABELS):
            stale.append(label)
    return sorted(set(stale))


def _closure_leaks(text: str) -> list[str]:
    graph_pos = text.find(GRAPH_HEADER_MARKER)
    if graph_pos == -1:
        return []
    prefix = text[:graph_pos]
    return [marker for marker in CLOSURE_LEAK_MARKERS if marker in prefix]


def _mission_reflection_errors(rows: dict[str, str], mode: str) -> list[str]:
    errors: list[str] = []
    labels = MISSION_ROW_LABELS_BY_MODE[mode]
    cited_rows = 0
    min_chars = MISSION_REFLECTION_MIN_CHARS_BY_MODE[mode]
    for label in labels:
        body = rows.get(label)
        if body is None:
            errors.append(f"{label}: missing")
            continue
        clean_body = clean_cell_text(body)
        if MISSION_REFLECTION_TEMPLATE_TOKEN in body:
            errors.append(f"{label}: template still present")
            continue
        if len(clean_body) < min_chars:
            errors.append(
                f"{label}: too short ({len(clean_body)} chars; minimum {min_chars})"
            )
        if REPO_CITATION_PATTERN.search(body):
            cited_rows += 1
        elif mode == "closeout":
            errors.append(f"{label}: missing repo-grounding citation")
    citation_rule = REQUIRED_REPO_CITATION_ROWS_BY_MODE[mode]
    if citation_rule != "all" and cited_rows < int(citation_rule):
        errors.append(
            f"{mode} mode: expected at least {citation_rule} repo-grounded "
            f"mission/reflection row(s), found {cited_rows}"
        )
    return errors


def _placeholder_errors(rows: dict[str, str], mode: str) -> list[str]:
    errors: list[str] = []
    for label, body in rows.items():
        if FILL_PLACEHOLDER_TOKEN in body:
            errors.append(f"{label}: placeholder `<fill` still present")
    closure = rows.get("Closure: Metadata")
    if mode == "closeout":
        if closure is None:
            errors.append("Closure: Metadata: missing")
        elif CLOSURE_METADATA_TEMPLATE_TOKEN in closure:
            errors.append("Closure: Metadata: template still present")
    elif closure is not None and CLOSURE_METADATA_TEMPLATE_TOKEN in closure:
        errors.append("Closure: Metadata: template still present")
    return errors


def _verdict_errors(rows: dict[str, str], check_payload: dict[str, object] | None) -> list[str]:
    verdict_body = rows.get("Verdict", "")
    clean = clean_cell_text(verdict_body)
    errors: list[str] = []
    if "Turn verdict:" not in clean:
        errors.append("Verdict: missing `Turn verdict:`")
    if "Close-session eligibility:" not in clean:
        errors.append("Verdict: missing `Close-session eligibility:`")
    for phrase in STALE_VERDICT_PHRASES:
        if phrase in clean.lower():
            errors.append(f"Verdict: stale phrase `{phrase}` is forbidden")
    if check_payload is not None:
        expected = str(check_payload.get("verdict", ""))
        if expected and expected not in clean:
            errors.append(f"Verdict: does not contain current reflection-check verdict `{expected}`")
        if expected == "FAIL":
            errors.append("reflection-check verdict is FAIL")
        eligible, _reason = close_session_eligibility(check_payload)
        if not eligible and "Close-session eligibility: yes" in clean:
            errors.append("Verdict: claims close-session eligibility when current state is not eligible")
    return errors


def validate_graph_text(
    text: str,
    *,
    check_payload: dict[str, object] | None = None,
    require_filled: bool = True,
    mode: str | None = None,
) -> GraphValidationResult:
    """Validate a final assistant message containing the mission graph."""

    graph_mode = normalize_graph_mode(mode) if mode is not None else infer_graph_mode(text)
    errors: list[str] = []
    errors.extend(_shape_errors(text))
    rows = parse_rows(text)
    errors.extend(_required_row_errors(rows, graph_mode))
    stale_rows = _stale_dashboard_rows(rows)
    errors.extend(f"stale dashboard row `{row}`" for row in stale_rows)
    leaks = _closure_leaks(text)
    if leaks:
        errors.append(
            "closure-shaped content before graph header: " + ", ".join(leaks)
        )
    if require_filled:
        errors.extend(_mission_reflection_errors(rows, graph_mode))
        errors.extend(_placeholder_errors(rows, graph_mode))
    errors.extend(_verdict_errors(rows, check_payload))
    return GraphValidationResult(
        ok=not errors,
        errors=tuple(errors),
        rows=rows,
        mode=graph_mode,
    )


def filled_example_graph(graph_markdown: str) -> str:
    """Return a syntactically valid filled graph for hook-health tests."""

    mission_fill = (
        "This row cites `docs/CORTEX.md` and `tests/internal/test_repo_workflow.py` "
        "while giving causal Cortex Mission Reflection about boundary, model I/O, "
        "evidence quality, and next ownership rather than static status recitation."
    )
    closure_fill = (
        "ending branch `codex/example`; commit `no commit`; verification no "
        "verification this turn; returned to main no; Status registry touched none; "
        "status doc regenerated no; CORTEX.md regenerated no"
    )
    filled = re.sub(r"_\[mission reflection — [^\]]+\]_", mission_fill, graph_markdown)
    filled = re.sub(r"_\[closure metadata — [^\]]+\]_", closure_fill, filled)
    filled = re.sub(r"<fill: [^>]+>", "no", filled)
    return filled
