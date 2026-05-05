"""Task-specific work-standard state for product lifecycle perception.

This module keeps the product-visible executive object small: what the task
asked for, what the model named as the standard for good work, what tool
evidence touched that standard, and what closure claims outran the evidence.
It does not read files, inspect hidden verifier artifacts, or encode
domain-specific fixture rules.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping


TASK_STANDARD_FORMATION_TEXT = (
    "Let me put the standard down before I start, in three compact lines "
    "labeled Work standard, Likely misses, Closure evidence. What would "
    "someone with deep experience in this kind of work expect at the "
    "structural level, and what would they expect on the surface. Where do "
    "people usually go wrong here, and what would feel embarrassing to ship. "
    "What would they verify before calling it done."
)


class TaskStandardItemKind(str, Enum):
    VISIBLE_OBLIGATION = "visible_obligation"
    WORK_STANDARD = "work_standard"
    LIKELY_MISS = "likely_miss"
    CLOSURE_EVIDENCE = "closure_evidence"


class TaskStandardEvidenceClass(str, Enum):
    CLAIM_ALIGNED = "claim_aligned"
    STANDARD_ALIGNED = "standard_aligned"
    GENERIC_CHECK = "generic_check"
    UNRELATED_ACTIVITY = "unrelated_activity"


@dataclass(frozen=True, slots=True)
class TaskStandardItem:
    item_id: str
    kind: TaskStandardItemKind
    text: str
    source_event_ref: str
    evidence_refs: tuple[str, ...] = ()
    claimed: bool = False

    def __post_init__(self) -> None:
        _require_non_empty_string(self.item_id, "TaskStandardItem.item_id")
        if not isinstance(self.kind, TaskStandardItemKind):
            actual_type = type(self.kind).__name__
            raise TypeError(
                "TaskStandardItem.kind must be TaskStandardItemKind, "
                f"got {actual_type}."
            )
        _require_non_empty_string(self.text, "TaskStandardItem.text")
        _require_non_empty_string(
            self.source_event_ref,
            "TaskStandardItem.source_event_ref",
        )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.evidence_refs):
            raise ValueError(
                "TaskStandardItem.evidence_refs must contain non-empty strings."
            )
        if not isinstance(self.claimed, bool):
            actual_type = type(self.claimed).__name__
            raise TypeError(
                "TaskStandardItem.claimed must be bool, got " f"{actual_type}."
            )

    @property
    def has_aligned_evidence(self) -> bool:
        return bool(self.evidence_refs)

    def as_payload(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "kind": self.kind.value,
            "text": self.text,
            "source_event_ref": self.source_event_ref,
            "evidence_refs": list(self.evidence_refs),
            "claimed": self.claimed,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "TaskStandardItem":
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "TaskStandardItem.from_payload payload must be a mapping, "
                f"got {actual_type}."
            )
        return cls(
            item_id=_required_string(payload.get("item_id"), "item_id"),
            kind=TaskStandardItemKind(
                _required_string(payload.get("kind"), "kind")
            ),
            text=_required_string(payload.get("text"), "text"),
            source_event_ref=_required_string(
                payload.get("source_event_ref"),
                "source_event_ref",
            ),
            evidence_refs=tuple(
                str(ref).strip()
                for ref in payload.get("evidence_refs", ())
                if str(ref).strip()
            ),
            claimed=bool(payload.get("claimed", False)),
        )


@dataclass(frozen=True, slots=True)
class TaskStandardEvidence:
    event_ref: str
    evidence_class: TaskStandardEvidenceClass
    item_ids: tuple[str, ...] = ()
    text_excerpt: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.event_ref, "TaskStandardEvidence.event_ref")
        if not isinstance(self.evidence_class, TaskStandardEvidenceClass):
            actual_type = type(self.evidence_class).__name__
            raise TypeError(
                "TaskStandardEvidence.evidence_class must be "
                f"TaskStandardEvidenceClass, got {actual_type}."
            )
        if any(not (isinstance(item_id, str) and item_id.strip()) for item_id in self.item_ids):
            raise ValueError(
                "TaskStandardEvidence.item_ids must contain non-empty strings."
            )
        if self.text_excerpt is not None and not isinstance(self.text_excerpt, str):
            actual_type = type(self.text_excerpt).__name__
            raise TypeError(
                "TaskStandardEvidence.text_excerpt must be str | None, "
                f"got {actual_type}."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "event_ref": self.event_ref,
            "evidence_class": self.evidence_class.value,
            "item_ids": list(self.item_ids),
            "text_excerpt": self.text_excerpt,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "TaskStandardEvidence":
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "TaskStandardEvidence.from_payload payload must be a mapping, "
                f"got {actual_type}."
            )
        return cls(
            event_ref=_required_string(payload.get("event_ref"), "event_ref"),
            evidence_class=TaskStandardEvidenceClass(
                _required_string(payload.get("evidence_class"), "evidence_class")
            ),
            item_ids=tuple(
                str(item_id).strip()
                for item_id in payload.get("item_ids", ())
                if str(item_id).strip()
            ),
            text_excerpt=_optional_string(payload.get("text_excerpt")),
        )


@dataclass(frozen=True, slots=True)
class TaskStandardSpine:
    visible_task_obligations: tuple[TaskStandardItem, ...] = ()
    standard_items: tuple[TaskStandardItem, ...] = ()
    evidence_refs: tuple[TaskStandardEvidence, ...] = ()
    final_closure_claims: tuple[str, ...] = ()
    unmatched_standard_item_ids: tuple[str, ...] = ()
    malformed_standard_block_count: int = 0

    def __post_init__(self) -> None:
        for item in (*self.visible_task_obligations, *self.standard_items):
            if not isinstance(item, TaskStandardItem):
                actual_type = type(item).__name__
                raise TypeError(
                    "TaskStandardSpine items must be TaskStandardItem, "
                    f"got {actual_type}."
                )
        for evidence in self.evidence_refs:
            if not isinstance(evidence, TaskStandardEvidence):
                actual_type = type(evidence).__name__
                raise TypeError(
                    "TaskStandardSpine.evidence_refs must contain "
                    f"TaskStandardEvidence, got {actual_type}."
                )
        if any(
            not (isinstance(claim, str) and claim.strip())
            for claim in self.final_closure_claims
        ):
            raise ValueError(
                "TaskStandardSpine.final_closure_claims must contain non-empty strings."
            )
        if any(
            not (isinstance(item_id, str) and item_id.strip())
            for item_id in self.unmatched_standard_item_ids
        ):
            raise ValueError(
                "TaskStandardSpine.unmatched_standard_item_ids must contain "
                "non-empty strings."
            )
        if (
            not isinstance(self.malformed_standard_block_count, int)
            or self.malformed_standard_block_count < 0
        ):
            raise ValueError(
                "TaskStandardSpine.malformed_standard_block_count must be "
                "a non-negative int."
            )

    @property
    def all_items(self) -> tuple[TaskStandardItem, ...]:
        return (*self.visible_task_obligations, *self.standard_items)

    @property
    def has_standard(self) -> bool:
        return bool(self.standard_items)

    @property
    def has_unmatched_closure_items(self) -> bool:
        return bool(self.unmatched_standard_item_ids)

    def as_payload(self) -> dict[str, object]:
        return {
            "visible_task_obligations": [
                item.as_payload() for item in self.visible_task_obligations
            ],
            "standard_items": [item.as_payload() for item in self.standard_items],
            "evidence_refs": [evidence.as_payload() for evidence in self.evidence_refs],
            "final_closure_claims": list(self.final_closure_claims),
            "unmatched_standard_item_ids": list(self.unmatched_standard_item_ids),
            "malformed_standard_block_count": self.malformed_standard_block_count,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> "TaskStandardSpine":
        if payload is None:
            return cls()
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "TaskStandardSpine.from_payload payload must be a mapping, "
                f"got {actual_type}."
            )
        return cls(
            visible_task_obligations=tuple(
                TaskStandardItem.from_payload(item)
                for item in payload.get("visible_task_obligations", ())
                if isinstance(item, Mapping)
            ),
            standard_items=tuple(
                TaskStandardItem.from_payload(item)
                for item in payload.get("standard_items", ())
                if isinstance(item, Mapping)
            ),
            evidence_refs=tuple(
                TaskStandardEvidence.from_payload(item)
                for item in payload.get("evidence_refs", ())
                if isinstance(item, Mapping)
            ),
            final_closure_claims=tuple(
                str(claim).strip()
                for claim in payload.get("final_closure_claims", ())
                if str(claim).strip()
            ),
            unmatched_standard_item_ids=tuple(
                str(item_id).strip()
                for item_id in payload.get("unmatched_standard_item_ids", ())
                if str(item_id).strip()
            ),
            malformed_standard_block_count=_optional_int(
                payload.get("malformed_standard_block_count"),
                0,
            ),
        )


def initialize_task_standard_spine(
    prompt_text: str | None,
    *,
    event_ref: str,
) -> TaskStandardSpine:
    """Extract visible task obligations from a UserPromptSubmit payload."""

    if not isinstance(event_ref, str) or not event_ref.strip():
        raise ValueError("initialize_task_standard_spine.event_ref must be non-empty.")
    obligations = tuple(
        TaskStandardItem(
            item_id=_item_id(event_ref, "visible-obligation", index, phrase),
            kind=TaskStandardItemKind.VISIBLE_OBLIGATION,
            text=phrase,
            source_event_ref=event_ref,
        )
        for index, phrase in enumerate(_visible_obligation_phrases(prompt_text), start=1)
    )
    return TaskStandardSpine(visible_task_obligations=obligations)


def store_assistant_standard_block(
    spine: TaskStandardSpine,
    message: str,
    *,
    event_ref: str,
) -> TaskStandardSpine:
    """Store the first valid three-line assistant standard block."""

    if not isinstance(spine, TaskStandardSpine):
        actual_type = type(spine).__name__
        raise TypeError(
            "store_assistant_standard_block.spine must be TaskStandardSpine, "
            f"got {actual_type}."
        )
    if spine.standard_items:
        return spine
    parsed = _parse_standard_block(message)
    if parsed is None:
        return spine
    if not parsed:
        return replace(
            spine,
            malformed_standard_block_count=spine.malformed_standard_block_count + 1,
        )
    items = tuple(
        TaskStandardItem(
            item_id=_item_id(event_ref, kind.value, index, text),
            kind=kind,
            text=text,
            source_event_ref=event_ref,
        )
        for index, (kind, text) in enumerate(parsed, start=1)
    )
    return replace(spine, standard_items=items)


def record_task_standard_evidence(
    spine: TaskStandardSpine,
    *,
    event_ref: str,
    tool_text: str,
    successful: bool,
) -> tuple[TaskStandardSpine, TaskStandardEvidence]:
    """Classify tool evidence against the visible task standard."""

    if not isinstance(spine, TaskStandardSpine):
        actual_type = type(spine).__name__
        raise TypeError(
            "record_task_standard_evidence.spine must be TaskStandardSpine, "
            f"got {actual_type}."
        )
    normalized_tool_text = _normalize_text(tool_text)
    if not successful or not normalized_tool_text:
        evidence = TaskStandardEvidence(
            event_ref=event_ref,
            evidence_class=TaskStandardEvidenceClass.UNRELATED_ACTIVITY,
            text_excerpt=_excerpt(tool_text),
        )
        return _append_evidence(spine, evidence), evidence

    directly_aligned_item_ids = tuple(
        item.item_id
        for item in spine.all_items
        if _texts_align(item.text, normalized_tool_text)
    )
    closure_evidence_item_ids = tuple(
        item.item_id
        for item in spine.standard_items
        if item.kind is TaskStandardItemKind.CLOSURE_EVIDENCE
        and _closure_evidence_action_aligns(item.text, normalized_tool_text)
        and (
            directly_aligned_item_ids
            or _generic_verification_markers_present(normalized_tool_text)
        )
    )
    aligned_item_ids = tuple(
        dict.fromkeys((*directly_aligned_item_ids, *closure_evidence_item_ids))
    )
    if aligned_item_ids:
        evidence_class = (
            TaskStandardEvidenceClass.CLAIM_ALIGNED
            if _closure_claim_markers_present(normalized_tool_text)
            else TaskStandardEvidenceClass.STANDARD_ALIGNED
        )
    elif _generic_verification_markers_present(normalized_tool_text):
        evidence_class = TaskStandardEvidenceClass.GENERIC_CHECK
    else:
        evidence_class = TaskStandardEvidenceClass.UNRELATED_ACTIVITY
    evidence = TaskStandardEvidence(
        event_ref=event_ref,
        evidence_class=evidence_class,
        item_ids=aligned_item_ids,
        text_excerpt=_excerpt(tool_text),
    )
    updated = _append_evidence(spine, evidence)
    if aligned_item_ids:
        updated = _attach_evidence_to_items(updated, aligned_item_ids, event_ref)
    return updated, evidence


def record_closure_claims(
    spine: TaskStandardSpine,
    message: str,
    *,
    event_ref: str,
) -> TaskStandardSpine:
    """Record final assistant closure claims and the standard items they outrun."""

    if not isinstance(spine, TaskStandardSpine):
        actual_type = type(spine).__name__
        raise TypeError(
            "record_closure_claims.spine must be TaskStandardSpine, "
            f"got {actual_type}."
        )
    standard_claims = _closure_claim_phrases(message)
    if not standard_claims:
        return spine
    items = spine.standard_items or spine.visible_task_obligations
    if not items:
        return replace(
            spine,
            final_closure_claims=tuple(
                dict.fromkeys((*spine.final_closure_claims, *standard_claims))
            ),
        )
    normalized_claim_text = _normalize_text(" ".join(standard_claims))
    unmatched_ids: list[str] = []
    updated_items: list[TaskStandardItem] = []
    for item in items:
        claimed = _closure_claims_item(
            item,
            normalized_claim_text,
        )
        if claimed and not item.has_aligned_evidence:
            unmatched_ids.append(item.item_id)
        updated_items.append(replace(item, claimed=item.claimed or claimed))
    if spine.standard_items:
        updated_spine = replace(spine, standard_items=tuple(updated_items))
    else:
        updated_spine = replace(spine, visible_task_obligations=tuple(updated_items))
    return replace(
        updated_spine,
        final_closure_claims=tuple(
            dict.fromkeys((*spine.final_closure_claims, *standard_claims))
        ),
        unmatched_standard_item_ids=tuple(
            dict.fromkeys((*spine.unmatched_standard_item_ids, *unmatched_ids))
        ),
    )


def hidden_verifier_terms() -> tuple[str, ...]:
    """Strings that are never semantic inputs to the product spine."""

    return (
        "test-hidden",
        "hidden verifier",
        "hidden_quality",
        "verifier_only",
        "scripts/test-hidden.mjs",
    )


def _append_evidence(
    spine: TaskStandardSpine,
    evidence: TaskStandardEvidence,
) -> TaskStandardSpine:
    return replace(
        spine,
        evidence_refs=(*spine.evidence_refs, evidence),
    )


def _attach_evidence_to_items(
    spine: TaskStandardSpine,
    item_ids: tuple[str, ...],
    event_ref: str,
) -> TaskStandardSpine:
    item_id_set = set(item_ids)

    def attach(item: TaskStandardItem) -> TaskStandardItem:
        if item.item_id not in item_id_set:
            return item
        return replace(
            item,
            evidence_refs=tuple(dict.fromkeys((*item.evidence_refs, event_ref))),
        )

    return replace(
        spine,
        visible_task_obligations=tuple(
            attach(item) for item in spine.visible_task_obligations
        ),
        standard_items=tuple(attach(item) for item in spine.standard_items),
        unmatched_standard_item_ids=tuple(
            item_id
            for item_id in spine.unmatched_standard_item_ids
            if item_id not in item_id_set
        ),
    )


def _parse_standard_block(
    message: str,
) -> tuple[tuple[TaskStandardItemKind, str], ...] | tuple[()] | None:
    if not isinstance(message, str) or not message.strip():
        return None
    required = {
        "work standard": TaskStandardItemKind.WORK_STANDARD,
        "likely misses": TaskStandardItemKind.LIKELY_MISS,
        "closure evidence": TaskStandardItemKind.CLOSURE_EVIDENCE,
    }
    found: dict[str, str] = {}
    for line in message.splitlines():
        if ":" not in line:
            continue
        label, value = line.split(":", 1)
        label_key = _normalize_label(label)
        if label_key in required and value.strip():
            found[label_key] = _compact(value)
    if not found:
        return None
    if set(found) != set(required):
        return ()
    return tuple((required[label], found[label]) for label in required)


def _visible_obligation_phrases(prompt_text: str | None) -> tuple[str, ...]:
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        return ()
    text = _strip_hidden_terms(prompt_text)
    text = re.sub(r"\s+", " ", text).strip()
    candidates = re.split(r"(?:[.;!?]|\n|\band\b|\bthen\b)", text)
    phrases: list[str] = []
    for candidate in candidates:
        phrase = _compact(
            re.sub(
                r"^(please|can you|could you|i want you to|build|create|make|write|fix|add|implement)\s+",
                "",
                candidate.strip(),
                flags=re.IGNORECASE,
            )
        )
        if len(_meaningful_tokens(phrase)) < 2:
            continue
        if phrase.lower() in {item.lower() for item in phrases}:
            continue
        phrases.append(phrase)
        if len(phrases) >= 6:
            break
    return tuple(phrases)


def _closure_claim_phrases(message: str) -> tuple[str, ...]:
    if not isinstance(message, str) or not message.strip():
        return ()
    sentences = re.split(r"(?<=[.!?])\s+|\n+", message.strip())
    claims: list[str] = []
    for sentence in sentences:
        normalized = _normalize_text(sentence)
        if _general_closure_claim(normalized) or _closure_claim_markers_present(
            normalized
        ):
            claims.append(_compact(sentence))
        if len(claims) >= 8:
            break
    return tuple(claims)


def _texts_align(item_text: str, normalized_other_text: str) -> bool:
    item_tokens = set(_meaningful_tokens(item_text))
    other_tokens = set(_meaningful_tokens(normalized_other_text))
    if not item_tokens or not other_tokens:
        return False
    overlap = item_tokens & other_tokens
    if len(overlap) >= 2:
        return True
    if len(overlap) == 1 and len(item_tokens) <= 3:
        return True
    return False


def _closure_claims_item(
    item: TaskStandardItem,
    normalized_claim_text: str,
) -> bool:
    if _texts_align(item.text, normalized_claim_text):
        return True
    if item.kind is TaskStandardItemKind.LIKELY_MISS:
        return False
    return _general_closure_claim(normalized_claim_text)


def _closure_evidence_action_aligns(
    item_text: str,
    normalized_tool_text: str,
) -> bool:
    item_tokens = set(_meaningful_tokens(item_text))
    tool_tokens = set(_meaningful_tokens(normalized_tool_text))
    action_tokens = {
        "cat",
        "grep",
        "stat",
        "wc",
        "test",
        "tests",
        "pytest",
        "build",
        "lint",
        "typecheck",
        "check",
        "verify",
        "inspect",
        "output",
        "read",
        "readback",
    }
    return bool(item_tokens & tool_tokens & action_tokens)


def _generic_verification_markers_present(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            " test ",
            " tests ",
            " pytest ",
            " unittest ",
            " vitest ",
            " jest ",
            " build ",
            " lint ",
            " typecheck ",
            " tsc ",
            " mypy ",
            " ruff ",
            " check ",
            " verify ",
            " cat ",
            " wc ",
            " grep ",
            " stat ",
            " exit_code 0 ",
            " passed ",
            " success ",
            " content_ok ",
            " file_ok ",
            " exists ",
        )
    )


def _closure_claim_markers_present(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            " done ",
            " complete ",
            " completed ",
            " implemented ",
            " created ",
            " fixed ",
            " ready ",
        )
    )


def _general_closure_claim(text: str) -> bool:
    return _closure_claim_markers_present(f" {text} ")


def _normalize_label(text: str) -> str:
    return re.sub(r"[^a-z ]+", "", text.lower()).strip()


def _normalize_text(text: str) -> str:
    text = _strip_hidden_terms(text)
    text = re.sub(r"[^a-z0-9_./-]+", " ", text.lower())
    return f" {re.sub(r'\\s+', ' ', text).strip()} "


def _meaningful_tokens(text: str) -> tuple[str, ...]:
    normalized = _normalize_text(text)
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "what",
        "from",
        "into",
        "work",
        "task",
        "done",
        "complete",
        "completed",
        "make",
        "create",
        "build",
        "write",
        "implement",
        "using",
        "have",
        "has",
        "had",
        "should",
        "would",
        "could",
        "need",
        "needs",
        "must",
    }
    tokens: list[str] = []
    for token in re.findall(r"[a-z0-9_./-]+", normalized):
        cleaned = token.strip("._/-")
        if len(cleaned) >= 3 and cleaned not in stopwords:
            tokens.append(cleaned)
    return tuple(tokens)


def _strip_hidden_terms(text: str) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = text
    for term in hidden_verifier_terms():
        cleaned = re.sub(re.escape(term), "", cleaned, flags=re.IGNORECASE)
    return cleaned


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _excerpt(text: str) -> str | None:
    compact = _compact(_strip_hidden_terms(text))
    return compact[:240] if compact else None


def _item_id(event_ref: str, kind: str, index: int, text: str) -> str:
    digest = hashlib.sha256(f"{event_ref}:{kind}:{index}:{text}".encode("utf-8")).hexdigest()
    return f"task-standard:{kind}:{digest[:16]}"


def _require_non_empty_string(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string.")
    return value.strip()


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"expected str | None, got {actual_type}.")
    text = value.strip()
    return text or None


def _optional_int(value: object, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        actual_type = type(value).__name__
        raise TypeError(f"expected non-negative int, got {actual_type}.")
    return value


__all__ = [
    "TASK_STANDARD_FORMATION_TEXT",
    "TaskStandardEvidence",
    "TaskStandardEvidenceClass",
    "TaskStandardItem",
    "TaskStandardItemKind",
    "TaskStandardSpine",
    "hidden_verifier_terms",
    "initialize_task_standard_spine",
    "record_closure_claims",
    "record_task_standard_evidence",
    "store_assistant_standard_block",
]
