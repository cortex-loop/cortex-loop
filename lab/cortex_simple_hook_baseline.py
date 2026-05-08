"""Small independent baseline for the Cortex effectiveness evaluator."""

from __future__ import annotations

import re
from dataclasses import dataclass


_WORD_RE = re.compile(r"[a-z0-9][a-z0-9._/-]*", re.IGNORECASE)
_EVIDENCE_RE = re.compile(
    r"\b(evidence|verified|checked|confirmed|observed|pass|matches?|bytes?|"
    r"line|content|cmp_exit=0|exists?|readback)\b",
    re.IGNORECASE,
)
_BLOCKER_RE = re.compile(
    r"\b(blocked|blocker|cannot|can't|unable|missing|not found|does not exist|"
    r"permission denied|waiting)\b",
    re.IGNORECASE,
)
_CLOSURE_RE = re.compile(r"\b(done|complete|completed|finished|pass|passes)\b", re.IGNORECASE)
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "the",
        "to",
        "with",
        "you",
        "your",
    }
)


@dataclass(frozen=True)
class SimpleHookStandard:
    """Visible task standard captured without Cortex state."""

    visible_task: str
    required_terms: tuple[str, ...]


@dataclass(frozen=True)
class SimpleHookClosureResult:
    """Simple closure verdict for evaluator rows."""

    satisfied: bool
    blocker_reported: bool
    evidence_reported: bool
    missing_terms: tuple[str, ...]
    reason: str


def _tokens(text: str) -> tuple[str, ...]:
    seen: set[str] = set()
    tokens: list[str] = []
    for match in _WORD_RE.finditer(text.lower()):
        token = match.group(0).strip(".,:;!?()[]{}")
        if len(token) < 3 or token in _STOPWORDS or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tuple(tokens)


def capture_visible_task_standard(visible_task: str) -> SimpleHookStandard:
    """Capture a tiny standard from visible task text only."""

    normalized = " ".join(visible_task.split())
    terms = _tokens(normalized)
    return SimpleHookStandard(
        visible_task=normalized,
        required_terms=terms[:12],
    )


def render_simple_hook_reminder(standard: SimpleHookStandard) -> str:
    """Render one model-visible reminder without Cortex/internal labels."""

    terms = ", ".join(standard.required_terms[:8]) or "the visible task"
    return (
        "Before closing, check the visible task requirements: "
        f"{terms}. Report the evidence you checked, or name the blocker."
    )


def assess_simple_hook_closure(
    standard: SimpleHookStandard,
    final_message: str,
) -> SimpleHookClosureResult:
    """Accept explicit evidence or blocker reporting; reject unsupported closure."""

    lowered = final_message.lower()
    blocker_reported = bool(_BLOCKER_RE.search(lowered))
    evidence_reported = bool(_EVIDENCE_RE.search(lowered))
    closure_claimed = bool(_CLOSURE_RE.search(lowered))
    missing = tuple(
        term for term in standard.required_terms[:8] if term.lower() not in lowered
    )
    if blocker_reported:
        return SimpleHookClosureResult(
            satisfied=True,
            blocker_reported=True,
            evidence_reported=evidence_reported,
            missing_terms=(),
            reason="blocker_reported",
        )
    if evidence_reported and (not missing or closure_claimed):
        return SimpleHookClosureResult(
            satisfied=True,
            blocker_reported=False,
            evidence_reported=True,
            missing_terms=missing,
            reason="evidence_reported",
        )
    return SimpleHookClosureResult(
        satisfied=False,
        blocker_reported=False,
        evidence_reported=evidence_reported,
        missing_terms=missing,
        reason="unsupported_closure",
    )


def simple_hook_baseline_metadata() -> dict[str, object]:
    return {
        "id": "simple_hook_baseline",
        "imports_cortex": False,
        "allowed_capabilities": [
            "task-standard capture",
            "one reminder or context path",
            "one closure check",
        ],
        "forbidden_capabilities": [
            "Cortex scoring lattice",
            "Core commitment law",
            "AUX support memory",
            "multi-hook policy search",
            "hidden verifier access",
            "fixture-specific scoring",
        ],
    }
