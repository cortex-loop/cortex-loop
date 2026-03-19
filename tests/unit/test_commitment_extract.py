"""Focused tests for commitment carrier resolution."""

import pytest

from cortex.core.commitment_extract import (
    CommitmentExtractionResult,
    FALLBACK_COMMITMENT_SOURCE,
    NATIVE_COMMITMENT_SOURCE,
    NO_COMMITMENT_SOURCE,
    PAYLOAD_COMMITMENT_SOURCE,
    reconcile_commitment_field,
    resolve_commitment_extract,
)


@pytest.mark.parametrize(
    ("payload", "native_commitment_fields", "expected_source", "expected_fallback_used"),
    [
        (
            {
                "stop_fields": {"claim_summary": "payload"},
                "last_assistant_message": 'COMMITMENT_FIELDS_JSON: {"claim_summary": "fallback"}',
            },
            {"claim_summary": "native"},
            NATIVE_COMMITMENT_SOURCE,
            False,
        ),
        (
            {"stop_fields": {"claim_summary": "payload"}},
            None,
            PAYLOAD_COMMITMENT_SOURCE,
            False,
        ),
        (
            {
                "last_assistant_message": 'COMMITMENT_FIELDS_JSON: {"claim_summary": "fallback"}',
            },
            None,
            FALLBACK_COMMITMENT_SOURCE,
            True,
        ),
    ],
)
def test_source_labeling_matches_resolution_path(
    payload: dict[str, object],
    native_commitment_fields: dict[str, str] | None,
    expected_source: str,
    expected_fallback_used: bool,
) -> None:
    result = resolve_commitment_extract(
        payload,
        native_commitment_fields=native_commitment_fields,
    )

    assert result.carrier_source == expected_source
    assert result.fallback_used is expected_fallback_used


def test_strict_mode_rejects_fallback_only_structured_claims() -> None:
    payload = {
        "last_assistant_message": 'COMMITMENT_FIELDS_JSON: {"claim_summary": "fallback-only"}',
    }

    result = resolve_commitment_extract(
        payload,
        require_structured_commitment_payload=True,
    )

    assert result.commitment_fields == {"claim_summary": "fallback-only"}
    assert result.carrier_source == FALLBACK_COMMITMENT_SOURCE
    assert result.structured_payload_violation is True
    assert "fallback-only commitment fields are rejected" in result.warnings[-1]


def test_reconcile_commitment_field_prefers_direct_payload_value() -> None:
    resolution = reconcile_commitment_field(
        key="claim_summary",
        payload={"claim_summary": "direct-value"},
        commitment_fields={"claim_summary": "structured-value"},
        carrier_source=PAYLOAD_COMMITMENT_SOURCE,
        value_label="claim summary",
    )

    assert resolution.value == "direct-value"
    assert resolution.source == "payload"
    assert resolution.warnings == ()


def test_reconcile_commitment_field_falls_back_to_extracted_fields_when_missing() -> None:
    resolution = reconcile_commitment_field(
        key="claim_summary",
        payload={},
        commitment_fields={"claim_summary": "structured-value"},
        carrier_source=PAYLOAD_COMMITMENT_SOURCE,
        value_label="claim summary",
    )

    assert resolution.value == "structured-value"
    assert resolution.source == PAYLOAD_COMMITMENT_SOURCE
    assert resolution.warnings == ("Using claim summary from payload.stop_fields.",)


def test_resolution_works_without_v1_specific_stop_bundle_fields() -> None:
    result = resolve_commitment_extract(
        {"stop_fields": {"effect_scope": "external", "claim_summary": "done"}},
        require_structured_commitment_payload=True,
    )
    scope = reconcile_commitment_field(
        key="effect_scope",
        payload={},
        commitment_fields=result.commitment_fields,
        carrier_source=result.carrier_source,
    )

    assert result.structured_payload_violation is False
    assert scope.value == "external"
    assert scope.source == PAYLOAD_COMMITMENT_SOURCE


def test_commitment_extraction_result_requires_canonical_carrier_source() -> None:
    direct = CommitmentExtractionResult(
        commitment_fields=None,
        carrier_source=NO_COMMITMENT_SOURCE,
        fallback_used=False,
        normalization_count=0,
        warnings=(),
        structured_payload_violation=False,
    )
    emitted = resolve_commitment_extract({})

    assert direct.carrier_source == NO_COMMITMENT_SOURCE
    assert emitted.carrier_source == NO_COMMITMENT_SOURCE

    with pytest.raises(
        ValueError,
        match="carrier_source must be one of the canonical source labels",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source="   ",
            fallback_used=False,
            normalization_count=0,
            warnings=(),
            structured_payload_violation=False,
        )

    with pytest.raises(
        ValueError,
        match="carrier_source must be one of the canonical source labels",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source="mystery",
            fallback_used=False,
            normalization_count=0,
            warnings=(),
            structured_payload_violation=False,
        )


def test_commitment_extraction_result_requires_dict_commitment_fields() -> None:
    direct = CommitmentExtractionResult(
        commitment_fields={"claim_summary": "done"},
        carrier_source=NO_COMMITMENT_SOURCE,
        fallback_used=False,
        normalization_count=0,
        warnings=(),
        structured_payload_violation=False,
    )
    emitted = resolve_commitment_extract({"stop_fields": {"claim_summary": "done"}})

    assert direct.commitment_fields == {"claim_summary": "done"}
    assert emitted.commitment_fields == {"claim_summary": "done"}

    with pytest.raises(
        TypeError,
        match=r"commitment_fields must be dict\[str, Any\] \| None, got tuple",
    ):
        CommitmentExtractionResult(
            commitment_fields=("not-a-dict",),
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used=False,
            normalization_count=0,
            warnings=(),
            structured_payload_violation=False,
        )


def test_commitment_extraction_result_requires_bool_fallback_used() -> None:
    direct = CommitmentExtractionResult(
        commitment_fields=None,
        carrier_source=NO_COMMITMENT_SOURCE,
        fallback_used=False,
        normalization_count=0,
        warnings=(),
        structured_payload_violation=False,
    )
    emitted = resolve_commitment_extract({})

    assert direct.fallback_used is False
    assert emitted.fallback_used is False

    with pytest.raises(
        TypeError,
        match="fallback_used must be bool, got str",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used="yes",
            normalization_count=0,
            warnings=(),
            structured_payload_violation=False,
        )


def test_commitment_extraction_result_requires_non_negative_int_normalization_count() -> None:
    direct = CommitmentExtractionResult(
        commitment_fields=None,
        carrier_source=NO_COMMITMENT_SOURCE,
        fallback_used=False,
        normalization_count=0,
        warnings=(),
        structured_payload_violation=False,
    )
    emitted = resolve_commitment_extract({})

    assert direct.normalization_count == 0
    assert emitted.normalization_count == 0

    with pytest.raises(
        TypeError,
        match="normalization_count must be int, got str",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used=False,
            normalization_count="1",
            warnings=(),
            structured_payload_violation=False,
        )

    with pytest.raises(
        ValueError,
        match="normalization_count must be non-negative",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used=False,
            normalization_count=-1,
            warnings=(),
            structured_payload_violation=False,
        )


def test_commitment_extraction_result_requires_non_empty_string_warnings() -> None:
    direct = CommitmentExtractionResult(
        commitment_fields=None,
        carrier_source=NO_COMMITMENT_SOURCE,
        fallback_used=False,
        normalization_count=0,
        warnings=("warning",),
        structured_payload_violation=False,
    )
    emitted = resolve_commitment_extract({"stop_fields": "not-an-object"})

    assert direct.warnings == ("warning",)
    assert emitted.warnings == ("Ignoring invalid payload.stop_fields field; expected an object.",)

    with pytest.raises(
        TypeError,
        match="warnings must contain only string entries",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used=False,
            normalization_count=0,
            warnings=("ok", 7),
            structured_payload_violation=False,
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty strings after trimming",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used=False,
            normalization_count=0,
            warnings=("",),
            structured_payload_violation=False,
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty strings after trimming",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used=False,
            normalization_count=0,
            warnings=("   ",),
            structured_payload_violation=False,
        )


def test_commitment_extraction_result_requires_bool_structured_payload_violation() -> None:
    direct = CommitmentExtractionResult(
        commitment_fields=None,
        carrier_source=NO_COMMITMENT_SOURCE,
        fallback_used=False,
        normalization_count=0,
        warnings=(),
        structured_payload_violation=False,
    )
    emitted = resolve_commitment_extract({})

    assert direct.structured_payload_violation is False
    assert emitted.structured_payload_violation is False

    with pytest.raises(
        TypeError,
        match="structured_payload_violation must be bool, got str",
    ):
        CommitmentExtractionResult(
            commitment_fields=None,
            carrier_source=NO_COMMITMENT_SOURCE,
            fallback_used=False,
            normalization_count=0,
            warnings=(),
            structured_payload_violation="yes",
        )
