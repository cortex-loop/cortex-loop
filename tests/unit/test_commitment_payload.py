"""Focused tests for commitment payload extraction."""

import pytest

from cortex.core.commitment_payload import (
    CommitmentPayloadExtraction,
    extract_commitment_payload,
    normalize_commitment_mapping_keys,
    parse_commitment_fields_json,
)


def test_native_commitment_carrier_wins_when_present() -> None:
    payload = {
        "stop_fields": {"payload_key": "payload-value"},
        "last_assistant_message": 'COMMITMENT_FIELDS_JSON: {"fallback_key": "fallback-value"}',
    }

    result = extract_commitment_payload(
        payload,
        native_commitment_fields={" native_key ": {" nested_key ": "native-value"}},
    )

    assert result.source == "native"
    assert result.commitment_fields == {"native_key": {"nested_key": "native-value"}}
    assert result.normalization_count == 2
    assert result.warnings == ()


def test_invalid_structured_payload_carrier_is_ignored_with_warning() -> None:
    result = extract_commitment_payload({"stop_fields": "not-an-object"})

    assert result.commitment_fields is None
    assert result.source is None
    assert result.warnings == ("Ignoring invalid payload.stop_fields field; expected an object.",)


def test_message_fallback_only_runs_when_allowed_and_normalizes_keys() -> None:
    payload = {
        "last_assistant_message": (
            'prefix text COMMITMENT_FIELDS_JSON: {" primary_key ": {" nested_key ": 1}}'
        )
    }

    allowed = extract_commitment_payload(payload, allow_message_fallback=True)
    blocked = extract_commitment_payload(payload, allow_message_fallback=False)

    assert allowed.source == "last_assistant_message.commitment_fields_json"
    assert allowed.commitment_fields == {"primary_key": {"nested_key": 1}}
    assert allowed.normalization_count == 2
    assert blocked.commitment_fields is None
    assert blocked.source is None


def test_key_normalization_occurs_for_payload_stop_fields() -> None:
    payload = {
        "stop_fields": {
            " outer_key ": [
                {" inner_key ": "value"},
                {"already_clean": {" nested_key ": 2}},
            ]
        }
    }

    result = extract_commitment_payload(payload)

    assert result.commitment_fields == {
        "outer_key": [
            {"inner_key": "value"},
            {"already_clean": {"nested_key": 2}},
        ]
    }
    assert result.normalization_count == 3


def test_malformed_fallback_json_is_rejected_cleanly() -> None:
    payload = {
        "last_assistant_message": "COMMITMENT_FIELDS_JSON: {not valid json",
    }

    result = extract_commitment_payload(payload)

    assert result.commitment_fields is None
    assert result.source is None
    assert len(result.warnings) == 1
    assert "Ignoring invalid COMMITMENT_FIELDS_JSON fallback" in result.warnings[0]


def test_commitment_payload_extraction_source_requires_non_empty_string_when_present() -> None:
    direct = CommitmentPayloadExtraction(
        commitment_fields=None,
        source="native",
        warnings=(),
        normalization_count=0,
    )
    empty = extract_commitment_payload({})

    assert direct.source == "native"
    assert empty.source is None

    with pytest.raises(
        ValueError,
        match="source must be None or a non-empty string after trimming",
    ):
        CommitmentPayloadExtraction(
            commitment_fields=None,
            source="",
            warnings=(),
            normalization_count=0,
        )

    with pytest.raises(
        ValueError,
        match="source must be None or a non-empty string after trimming",
    ):
        CommitmentPayloadExtraction(
            commitment_fields=None,
            source="   ",
            warnings=(),
            normalization_count=0,
        )


def test_commitment_payload_extraction_warnings_require_non_empty_strings() -> None:
    direct = CommitmentPayloadExtraction(
        commitment_fields=None,
        source=None,
        warnings=("warning",),
        normalization_count=0,
    )
    extracted = extract_commitment_payload({"stop_fields": "not-an-object"})

    assert direct.warnings == ("warning",)
    assert extracted.warnings == ("Ignoring invalid payload.stop_fields field; expected an object.",)

    with pytest.raises(
        TypeError,
        match="warnings must contain only string entries",
    ):
        CommitmentPayloadExtraction(
            commitment_fields=None,
            source=None,
            warnings=("ok", 7),
            normalization_count=0,
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty strings after trimming",
    ):
        CommitmentPayloadExtraction(
            commitment_fields=None,
            source=None,
            warnings=("",),
            normalization_count=0,
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty strings after trimming",
    ):
        CommitmentPayloadExtraction(
            commitment_fields=None,
            source=None,
            warnings=("   ",),
            normalization_count=0,
        )


def test_commitment_payload_extraction_normalization_count_requires_non_negative_int() -> None:
    direct = CommitmentPayloadExtraction(
        commitment_fields=None,
        source=None,
        warnings=(),
        normalization_count=0,
    )
    extracted = extract_commitment_payload(
        {"stop_fields": {" key ": "value"}},
    )

    assert direct.normalization_count == 0
    assert extracted.normalization_count == 1

    with pytest.raises(
        TypeError,
        match="normalization_count must be int, got str",
    ):
        CommitmentPayloadExtraction(
            commitment_fields=None,
            source=None,
            warnings=(),
            normalization_count="1",
        )

    with pytest.raises(
        ValueError,
        match="normalization_count must be non-negative",
    ):
        CommitmentPayloadExtraction(
            commitment_fields=None,
            source=None,
            warnings=(),
            normalization_count=-1,
        )


def test_normalize_commitment_mapping_keys_rejects_blank_canonical_keys() -> None:
    with pytest.raises(
        ValueError,
        match="requires non-empty canonical keys after trimming",
    ):
        normalize_commitment_mapping_keys({"": 1})

    with pytest.raises(
        ValueError,
        match="requires non-empty canonical keys after trimming",
    ):
        normalize_commitment_mapping_keys({"   ": 1})


def test_extract_commitment_payload_rejects_blank_stop_fields_keys() -> None:
    with pytest.raises(
        ValueError,
        match="requires non-empty canonical keys after trimming",
    ):
        extract_commitment_payload({"stop_fields": {"   ": 1}})


def test_extract_commitment_payload_rejects_blank_native_commitment_keys() -> None:
    with pytest.raises(
        ValueError,
        match="requires non-empty canonical keys after trimming",
    ):
        extract_commitment_payload({}, native_commitment_fields={"   ": 1})


def test_extract_commitment_payload_rejects_nested_blank_keys() -> None:
    with pytest.raises(
        ValueError,
        match="requires non-empty canonical keys after trimming",
    ):
        extract_commitment_payload({"stop_fields": {"outer": {"   ": 1}}})


def test_parse_commitment_fields_json_rejects_trailing_junk_after_marker() -> None:
    parsed, marker_found, error = parse_commitment_fields_json(
        'COMMITMENT_FIELDS_JSON: {"a": 1} trailing'
    )

    assert parsed is None
    assert marker_found is True
    assert error == "trailing content after commitment fields JSON object"


def test_parse_commitment_fields_json_rejects_trailing_junk_after_fenced_block() -> None:
    parsed, marker_found, error = parse_commitment_fields_json(
        '```commitment-fields {"a": 1}``` trailing'
    )

    assert parsed is None
    assert marker_found is True
    assert error == "trailing content after fenced commitment fields block"


def test_extract_commitment_payload_rejects_mixed_content_fallback_and_keeps_clean_fallbacks() -> None:
    mixed = extract_commitment_payload(
        {"message": 'COMMITMENT_FIELDS_JSON: {"a": 1} trailing'}
    )
    mixed_fenced = extract_commitment_payload(
        {"message": '```commitment-fields {"a": 1}``` trailing'}
    )
    clean_marker = extract_commitment_payload(
        {"message": 'COMMITMENT_FIELDS_JSON: {"a": 1}'}
    )
    clean_fenced = extract_commitment_payload(
        {"message": '```commitment-fields {"a": 1}```'}
    )

    assert mixed.commitment_fields is None
    assert mixed.source is None
    assert mixed.warnings == (
        "Ignoring invalid COMMITMENT_FIELDS_JSON fallback in message: trailing content after commitment fields JSON object",
    )
    assert mixed_fenced.commitment_fields is None
    assert mixed_fenced.source is None
    assert mixed_fenced.warnings == (
        "Ignoring invalid COMMITMENT_FIELDS_JSON fallback in message: trailing content after fenced commitment fields block",
    )
    assert clean_marker.commitment_fields == {"a": 1}
    assert clean_marker.source == "message.commitment_fields_json"
    assert clean_marker.warnings == ()
    assert clean_fenced.commitment_fields == {"a": 1}
    assert clean_fenced.source == "message.commitment_fields_json"
    assert clean_fenced.warnings == ()
