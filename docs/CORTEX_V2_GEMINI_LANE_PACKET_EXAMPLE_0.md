# CORTEX_V2_GEMINI_LANE_PACKET_EXAMPLE_0

Status: committed Gemini-lane packet example (`active`, evidence)
Date: 2026-03-21

Purpose:
- record one real contradiction-preserving Gemini-host packet example built from landed surfaces,
- tie the committed example to a live integration test,
- keep earned packet truth distinct from later report formatting or UI work.

Source test:
- `tests/integration/test_gemini_lane_packet_example.py::test_gemini_lane_current_pair_packet_example_matches_committed_doc`

Earned in this example:
- Gemini-host candidate-bearing event plus full-commitment event -> commitment verdict -> event trace artifact -> current-pair fragment -> eval harness -> eval packet,
- explicit contradiction and degradation preservation,
- explicit truthful-withheld field exposure.

Not earned in this example:
- report formatting or UI rendering,
- runtime wiring,
- mediated comparison or host-realization lift.

## Example Snapshot

```json
{
  "candidate_event": {
    "raw_host_event_name": "content.delta",
    "canonical_event_name": "external/observation"
  },
  "publication_event": {
    "raw_host_event_name": "interaction.complete",
    "canonical_event_name": "turn/complete"
  },
  "dispatch_lanes": {
    "candidate": "candidate-bearing",
    "publication": "full-commitment"
  },
  "candidate_id": "gemini-host-packet-candidate-1",
  "verdict_status": "certified",
  "packet_kind": "current-pair",
  "event_trace": {
    "trace_id": "gemini-lane:gemini-host-packet-candidate-1",
    "event_refs": [
      "external/observation",
      "turn/complete"
    ],
    "record_refs": [
      "gemini-host-artifact-1"
    ]
  },
  "withheld_fields": [
    {
      "field_ref": "current_pair.verdict_reason_code",
      "reason_code": "truthful-withheld"
    }
  ],
  "contradiction_refs": [
    {
      "source_tag": "gemini-host-publication-check",
      "summary": "Gemini host publication evidence remains partially withheld"
    }
  ],
  "degradation_refs": [
    {
      "reason_code": "gemini-host-publication-partial",
      "capability_tags": [
        "trace/read"
      ]
    }
  ],
  "warnings": []
}
```
