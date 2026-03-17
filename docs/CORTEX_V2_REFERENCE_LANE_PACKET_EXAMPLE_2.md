# CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2

Status: committed reference-lane packet example (`active`, evidence)
Date: 2026-03-18

Purpose:
- record one real contradiction-preserving reference-host packet example built from landed surfaces,
- tie the committed example to a live integration test,
- keep earned packet truth distinct from later report formatting or UI work.

Source test:
- `tests/integration/test_reference_lane_packet_example.py::test_reference_lane_current_pair_packet_example_matches_committed_doc`

Earned in this example:
- reference-host full-commitment event -> commitment verdict -> event trace artifact -> current-pair fragment -> eval harness -> eval packet,
- explicit contradiction and degradation preservation,
- explicit truthful-withheld field exposure.

Not earned in this example:
- report formatting or UI rendering,
- runtime wiring,
- additional packet taxonomy beyond the minimal current-pair / blocker split.

## Example Snapshot

```json
{
  "source_event": {
    "raw_host_event_name": "ApprovalResult",
    "canonical_event_name": "approval/result"
  },
  "dispatch_lane": "full-commitment",
  "candidate_id": "commit-packet-1",
  "verdict_status": "certified",
  "packet_kind": "current-pair",
  "event_trace": {
    "trace_id": "reference-lane:commit-packet-1",
    "event_refs": [
      "approval/result"
    ],
    "record_refs": [
      "artifact-packet-1"
    ]
  },
  "withheld_fields": [
    {
      "field_ref": "current_pair.verdict_reason_code",
      "reason_code": "not-material-in-minimal-example"
    }
  ],
  "contradiction_refs": [
    {
      "source_tag": "host-check",
      "summary": "write receipt was incomplete"
    }
  ],
  "degradation_refs": [
    {
      "reason_code": "host-surface-degraded",
      "capability_tags": [
        "external/write"
      ]
    }
  ],
  "warnings": []
}
```
