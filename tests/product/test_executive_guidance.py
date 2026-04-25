"""Tests for model-visible Cortex v2 executive guidance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cortex.hosts.openai.runtime import OpenAIRuntimeSession
from cortex.sre.families import SoftControlFamily
from cortex.sre.guidance import (
    ExecutiveGuidanceContext,
    DEFAULT_PRODUCT_GUIDANCE_MODE,
    GUIDANCE_MARKER,
    GuidanceMode,
    GuidanceProfile,
    V2_EXECUTIVE_GUIDANCE_ROWS,
    append_guidance_to_channel,
    assert_status_bio_to_code_coverage,
    build_intervention_intent_view,
    build_guidance_context_from_session,
    guidance_mode_for_profile,
    prepend_guidance_to_prompt,
    render_executive_guidance,
    v2_guidance_denominator_coverage_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_v2_guidance_inventory_covers_status_bio_to_code_matrix() -> None:
    status_payload = json.loads(
        (REPO_ROOT / "internal" / "truth" / "cortex_status.json").read_text(
            encoding="utf-8"
        )
    )

    assert_status_bio_to_code_coverage(status_payload)

    row_ids = {row.row_id for row in V2_EXECUTIVE_GUIDANCE_ROWS}
    assert {
        "core.lifecycle_dispatch",
        "core.commitment_certification",
        "runtime.verified_work_repair",
        "sre.uncertainty_brake",
        "sre.branch_continuity",
        "sre.intervention_pricing",
        "sre.blocker_goal_debt",
        "host.claude_cli",
        "host.codex_cli",
        "aux.default_zero_removable",
        "operational.truth_distinctions",
        "negative.forbidden_shortcuts",
    } <= row_ids


def test_render_executive_guidance_surfaces_dynamic_runtime_state_and_negative_rows() -> None:
    session = OpenAIRuntimeSession(
        session_id="oa-guidance",
        event_index=4,
        active_track_ref="feature-branch",
        pending_goal_refs=("verify-api",),
        brake_history=("guarded",),
        last_selected_family=SoftControlFamily.CHECK,
        next_recommended_move="check",
    )
    context = build_guidance_context_from_session(
        host_name="codex",
        surface="codex-exec",
        transport_channel="prompt",
        session=session,
    )

    rendered = render_executive_guidance(context)

    assert rendered.startswith(GUIDANCE_MARKER)
    assert "host: codex" in rendered
    assert "active_track_ref: feature-branch" in rendered
    assert "pending_goal_refs: verify-api" in rendered
    assert "last_selected_family: check" in rendered
    assert "last_brake_state: guarded" in rendered
    assert "next_recommended_move: check" in rendered
    assert "- row_id: core.lifecycle_dispatch" in rendered
    assert "  packet: core" in rendered
    assert "  visibility: model-visible" in rendered
    assert "negative.forbidden_shortcuts" in rendered
    assert "diagnostics-only output, one file, one host" in rendered


def test_guidance_defaults_aux_to_zero_until_publication_is_explicit() -> None:
    inactive = render_executive_guidance(
        build_guidance_context_from_session(
            host_name="claude",
            surface="claude-message-stream",
            transport_channel="system",
        )
    )
    active = render_executive_guidance(
        build_guidance_context_from_session(
            host_name="openai",
            surface="openai-response-stream",
            transport_channel="instructions",
            offline_publication_active=True,
        )
    )

    assert "aux_publication: inactive-default-zero" in inactive
    assert "do not use raw AUX memory or hidden support priors" in inactive
    assert "aux_publication: explicit-publication-present" in active
    assert "it never certifies commitments or rewrites blockedness" in active


def test_guidance_channel_helpers_preserve_existing_text_and_are_idempotent() -> None:
    context = build_guidance_context_from_session(
        host_name="claude",
        surface="claude-cli",
        transport_channel="prompt",
    )

    prompted = prepend_guidance_to_prompt("Do the task.", context)
    appended = append_guidance_to_channel("Be concise.", context)

    assert prompted.startswith(GUIDANCE_MARKER)
    assert "USER_TASK\nDo the task." in prompted
    assert appended.startswith("Be concise.")
    assert GUIDANCE_MARKER in appended
    assert prepend_guidance_to_prompt(prompted, context) == prompted
    assert append_guidance_to_channel(appended, context) == appended


def test_normal_guidance_profile_uses_compressed_dynamic_as_product_default() -> None:
    assert DEFAULT_PRODUCT_GUIDANCE_MODE is GuidanceMode.COMPRESSED_DYNAMIC
    assert guidance_mode_for_profile(GuidanceProfile.NORMAL) is GuidanceMode.COMPRESSED_DYNAMIC
    assert guidance_mode_for_profile("audit_full") is GuidanceMode.FULL
    assert guidance_mode_for_profile("eval_raw") is GuidanceMode.RAW


def test_guidance_helpers_do_not_treat_marker_mentions_as_rendered_guidance() -> None:
    context = build_guidance_context_from_session(
        host_name="codex",
        surface="codex-exec",
        transport_channel="prompt",
    )

    prompted = prepend_guidance_to_prompt(
        f"Return the {GUIDANCE_MARKER} marker if you see guidance.",
        context,
    )
    appended = append_guidance_to_channel(
        f"Policy note mentions {GUIDANCE_MARKER} but has no contract rows.",
        context,
    )

    assert prompted.startswith(GUIDANCE_MARKER)
    assert "USER_TASK\nReturn the CORTEX_V2_EXECUTIVE_GUIDANCE marker" in prompted
    assert "core.lifecycle_dispatch" in prompted
    assert appended.count(GUIDANCE_MARKER) == 2
    assert "contract_rows:" in appended


def test_guidance_rejects_empty_prompt_channels() -> None:
    context = build_guidance_context_from_session(
        host_name="codex",
        surface="codex-exec",
        transport_channel="prompt",
    )

    with pytest.raises(ValueError, match="prompt must be non-empty"):
        prepend_guidance_to_prompt("   ", context)


def test_compressed_dynamic_guidance_preserves_denominator_with_lower_burden() -> None:
    session = OpenAIRuntimeSession(
        session_id="oa-guidance",
        event_index=7,
        active_track_ref="verified-work:2-paths",
        pending_goal_refs=("repair-port", "verify-test"),
        brake_history=("guarded",),
        last_selected_family=SoftControlFamily.CHECK,
        next_recommended_move="repair",
        last_commitment_result_summary="verification failed on target test",
    )
    context = build_guidance_context_from_session(
        host_name="codex",
        surface="codex-exec",
        transport_channel="prompt",
        session=session,
    )

    full = render_executive_guidance(context, mode=GuidanceMode.FULL)
    compressed = render_executive_guidance(context, mode=GuidanceMode.COMPRESSED_DYNAMIC)
    raw = prepend_guidance_to_prompt("Do the task.", context, mode=GuidanceMode.RAW)
    coverage = v2_guidance_denominator_coverage_payload(context)

    assert raw == "Do the task."
    assert compressed.startswith(GUIDANCE_MARKER)
    assert "mode: compressed_dynamic" in compressed
    assert "contract_rows:" not in compressed
    assert "runtime.verified_work_repair" in compressed
    assert len(compressed) < len(full)
    assert coverage["row_denominator_count"] == len(V2_EXECUTIVE_GUIDANCE_ROWS)
    assert coverage["missing_row_ids"] == []
    assert coverage["guidance_burden"]["mode_is_smaller_than_full"] is True
    statuses = {row["row_id"]: row["status"] for row in coverage["coverage"]}
    assert statuses["core.commitment_certification"] == "always_on"
    assert statuses["runtime.verified_work_repair"] == "dynamic_triggered"
    assert statuses["host.gemini_reference_conformance"] == "silent_with_reason"


def test_intervention_intent_view_maps_repair_close_and_neutral_without_expanding_family_law() -> None:
    repair_context = build_guidance_context_from_session(
        host_name="codex",
        surface="codex-exec",
        transport_channel="prompt",
        session=OpenAIRuntimeSession(
            last_selected_family=SoftControlFamily.CHECK,
            next_recommended_move="repair",
        ),
    )
    close_context = ExecutiveGuidanceContext(
        host_name="claude",
        surface="claude-cli",
        transport_channel="prompt",
        next_recommended_move="close truthfully with blockers explicit",
    )
    neutral_context = build_guidance_context_from_session(
        host_name="claude",
        surface="claude-cli",
        transport_channel="prompt",
    )

    assert build_intervention_intent_view(repair_context).intent.value == "REPAIR"
    assert build_intervention_intent_view(close_context).intent.value == "CLOSE"
    assert build_intervention_intent_view(neutral_context).intent.value == "CONTINUE"
