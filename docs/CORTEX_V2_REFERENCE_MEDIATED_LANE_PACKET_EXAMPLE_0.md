# CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0

Status: committed reference-mediated lane packet example (`active`, evidence)
Date: 2026-03-21

Purpose:
- record one real contradiction-preserving mediated reference-host packet example built from landed surfaces,
- tie the committed example to a live integration test,
- show the exact host-realization delta without changing packet truth or publication meaning,
- expose the runtime-backed experimental mediation diagnostics for the same packet example.

Source test:
- `tests/integration/test_reference_mediated_lane_packet_example.py::test_reference_mediated_lane_current_pair_packet_example_matches_committed_doc`

Earned in this example:
- the same reference-host full-commitment event -> commitment verdict -> event trace artifact -> current-pair fragment -> eval harness -> eval packet path as the baseline example,
- explicit contradiction and degradation preservation,
- explicit truthful-withheld field exposure,
- runtime-backed `seek-context` selection under experimental mediation mode,
- direct host-native opportunity specialization at the `seek-context` finalization layer via `mcp.query`.

Not earned in this example:
- package-level host-realization lift,
- mediation justification,
- any burden or branch-control claim.

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
    "trace_id": "reference-mediated-lane:commit-packet-1",
    "event_refs": [
      "approval/result"
    ],
    "record_refs": [
      "artifact-packet-1"
    ]
  },
  "runtime_control": {
    "selected_family": "seek-context",
    "realized_family": "seek-context",
    "host_opportunity_refs": [
      "mcp.query"
    ],
    "mediation": {
      "mediation_active": true,
      "mediation_identity": false,
      "selected_family_before_finalization": "seek-context",
      "selected_family_after_finalization": "seek-context",
      "preferred_opportunity_ref": "mcp.query",
      "direct_opportunity_specialization_used": true,
      "mediation_reason_tags": [
        "family:seek-context",
        "host-realization-specialized",
        "mode:host-realization-experimental",
        "opportunity-source:runtime-visible"
      ]
    }
  },
  "opportunity_specialization": {
    "selected_family": "seek-context",
    "realized_family": "seek-context",
    "preferred_opportunity_ref": "mcp.query",
    "direct_opportunity_specialization_used": true,
    "host_opportunity_refs": [
      "mcp.query"
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
