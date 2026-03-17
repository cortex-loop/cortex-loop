"""Focused tests for commitment payload extraction."""

from cortex.core.commitment_payload import extract_commitment_payload


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
