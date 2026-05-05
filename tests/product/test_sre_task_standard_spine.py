"""Product locks for task-standard executive state."""

from __future__ import annotations

from cortex.sre.interventions import find_forbidden_model_visible_terms
from cortex.sre.task_standard import (
    TASK_STANDARD_FORMATION_TEXT,
    TaskStandardEvidenceClass,
    TaskStandardSpine,
    hidden_verifier_terms,
    initialize_task_standard_spine,
    record_closure_claims,
    record_task_standard_evidence,
    store_assistant_standard_block,
)


def test_signed_off_standard_text_is_exact_and_output_law_clean() -> None:
    assert TASK_STANDARD_FORMATION_TEXT == (
        "Let me put the standard down before I start, in three compact lines "
        "labeled Work standard, Likely misses, Closure evidence. What would "
        "someone with deep experience in this kind of work expect at the "
        "structural level, and what would they expect on the surface. Where do "
        "people usually go wrong here, and what would feel embarrassing to ship. "
        "What would they verify before calling it done."
    )
    assert find_forbidden_model_visible_terms(TASK_STANDARD_FORMATION_TEXT) == ()


def test_task_standard_spine_round_trips_payload() -> None:
    spine = initialize_task_standard_spine(
        "Build a docs site with search and tag pages.",
        event_ref="event:prompt",
    )
    spine = store_assistant_standard_block(
        spine,
        "\n".join(
            (
                "Work standard: docs site search and tag pages are strong.",
                "Likely misses: search data and tag links.",
                "Closure evidence: inspect search data and tag pages.",
            )
        ),
        event_ref="event:standard",
    )
    spine, evidence = record_task_standard_evidence(
        spine,
        event_ref="event:tool",
        tool_text="grep -R search src && grep -R tag src\nexit_code: 0",
        successful=True,
    )
    spine = record_closure_claims(
        spine,
        "Done: implemented the docs search and tag pages.",
        event_ref="event:stop",
    )

    reloaded = TaskStandardSpine.from_payload(spine.as_payload())

    assert evidence.evidence_class is TaskStandardEvidenceClass.STANDARD_ALIGNED
    assert reloaded.as_payload() == spine.as_payload()
    assert not reloaded.has_unmatched_closure_items


def test_generic_check_is_not_standard_aligned() -> None:
    spine = initialize_task_standard_spine(
        "Build a docs site with search.",
        event_ref="event:prompt",
    )
    spine = store_assistant_standard_block(
        spine,
        "\n".join(
            (
                "Work standard: docs site search is strong.",
                "Likely misses: search data.",
                "Closure evidence: inspect search data.",
            )
        ),
        event_ref="event:standard",
    )
    spine, evidence = record_task_standard_evidence(
        spine,
        event_ref="event:tool",
        tool_text="npm run build\nexit_code: 0",
        successful=True,
    )
    spine = record_closure_claims(
        spine,
        "Done: implemented the docs site search.",
        event_ref="event:stop",
    )

    assert evidence.evidence_class is TaskStandardEvidenceClass.GENERIC_CHECK
    assert spine.has_unmatched_closure_items


def test_hidden_verifier_terms_are_stripped_from_product_state() -> None:
    spine = initialize_task_standard_spine(
        "Build the site and do not use scripts/test-hidden.mjs or hidden_quality facts.",
        event_ref="event:prompt",
    )
    spine, evidence = record_task_standard_evidence(
        spine,
        event_ref="event:tool",
        tool_text="scripts/test-hidden.mjs hidden_quality verifier_only output",
        successful=True,
    )
    payload_text = str(spine.as_payload()) + str(evidence.as_payload())

    for term in hidden_verifier_terms():
        assert term not in payload_text
