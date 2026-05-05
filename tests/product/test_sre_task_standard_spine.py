"""Product locks for task-standard executive state."""

from __future__ import annotations

from cortex.sre.interventions import find_forbidden_model_visible_terms
from cortex.sre.task_standard import (
    TASK_STANDARD_FORMATION_TEXT,
    TaskStandardEvidenceClass,
    TaskStandardSpine,
    external_scoring_boundary_terms,
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


def test_likely_miss_is_not_required_by_generic_done_claim() -> None:
    spine = initialize_task_standard_spine(
        "Create a one-line file, read it back, and report done.",
        event_ref="event:prompt",
    )
    spine = store_assistant_standard_block(
        spine,
        "\n".join(
            (
                "Work standard: create result.txt with exact content and read it back using cat.",
                "Likely misses: typo in filename or reporting completion without readback.",
                "Closure evidence: cat command output shows the exact content.",
            )
        ),
        event_ref="event:standard",
    )
    spine, evidence = record_task_standard_evidence(
        spine,
        event_ref="event:tool",
        tool_text=(
            "Bash {\"command\":\"printf 'ok\\n' > result.txt && cat result.txt\", "
            "\"exit_code\":0} ok"
        ),
        successful=True,
    )
    spine = record_closure_claims(
        spine,
        "Read back from result.txt: ok. Done.",
        event_ref="event:stop",
    )

    assert evidence.evidence_class is TaskStandardEvidenceClass.STANDARD_ALIGNED
    assert not spine.has_unmatched_closure_items
    likely_miss = [
        item for item in spine.standard_items if item.kind.value == "likely_miss"
    ][0]
    assert likely_miss.claimed is False


def test_likely_miss_explicit_claim_still_requires_evidence() -> None:
    spine = initialize_task_standard_spine(
        "Create a one-line file, read it back, and report done.",
        event_ref="event:prompt",
    )
    spine = store_assistant_standard_block(
        spine,
        "\n".join(
            (
                "Work standard: create result.txt with exact content.",
                "Likely misses: typo in filename or content.",
                "Closure evidence: inspect result.txt content.",
            )
        ),
        event_ref="event:standard",
    )
    spine = record_closure_claims(
        spine,
        "Done, and there is no typo in the filename or content.",
        event_ref="event:stop",
    )

    assert spine.has_unmatched_closure_items
    assert any(
        item.kind.value == "likely_miss" and item.item_id in spine.unmatched_standard_item_ids
        for item in spine.standard_items
    )


def test_external_scoring_boundary_terms_are_stripped_from_product_state() -> None:
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

    for term in external_scoring_boundary_terms():
        assert term not in payload_text
    assert "scripts/test-hidden.mjs" not in payload_text
