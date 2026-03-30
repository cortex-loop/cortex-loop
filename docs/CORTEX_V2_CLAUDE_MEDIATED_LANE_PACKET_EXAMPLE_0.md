# CORTEX_V2_CLAUDE_MEDIATED_LANE_PACKET_EXAMPLE_0

Status: committed Claude-mediated lane packet example (`active`, evidence)
Date: 2026-03-30

Purpose:
- record one real contradiction-preserving mediated Claude-host packet example built from landed surfaces,
- tie the committed example to a live integration test,
- show the exact host-realization delta without changing packet truth or publication meaning.

Source test:
- `tests/integration/test_claude_mediated_lane_packet_example.py::test_claude_mediated_lane_current_pair_packet_example_matches_committed_doc`

Earned in this example:
- the same Claude-host candidate-bearing event plus full-commitment event -> commitment verdict -> event trace artifact -> current-pair fragment -> eval harness -> eval packet path as the baseline example,
- explicit contradiction and degradation preservation,
- explicit truthful-withheld field exposure,
- direct host-native opportunity specialization at the `seek-context` selection layer via `mcp.query`.

Not earned in this example:
- package-level host-realization lift,
- mediation justification,
- any burden or branch-control claim.

## Example Snapshot

```json
{
  "candidate_event": {
    "raw_host_event_name": "content_block_delta",
    "canonical_event_name": "external/observation"
  },
  "publication_event": {
    "raw_host_event_name": "message_stop",
    "canonical_event_name": "turn/complete"
  },
  "dispatch_lanes": {
    "candidate": "candidate-bearing",
    "publication": "full-commitment"
  },
  "candidate_id": "cl-host-packet-commit-1",
  "verdict_status": "certified",
  "packet_kind": "current-pair",
  "event_trace": {
    "trace_id": "claude-mediated-lane:cl-host-packet-commit-1",
    "event_refs": [
      "external/observation",
      "turn/complete"
    ],
    "record_refs": [
      "claude-host-artifact-1"
    ]
  },
  "opportunity_specialization": {
    "selected_family": "seek-context",
    "preferred_opportunity_ref": "mcp.query",
    "direct_opportunity_specialization_used": true,
    "host_opportunity_refs": [
      "mcp.query"
    ],
    "native_surface_tags": [
      "mcp",
      "structured-query"
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
      "source_tag": "claude-host-publication-check",
      "summary": "Claude host publication evidence remains partially withheld"
    }
  ],
  "degradation_refs": [
    {
      "reason_code": "claude-host-publication-partial",
      "capability_tags": [
        "trace/read"
      ]
    }
  ],
  "warnings": []
}
```
