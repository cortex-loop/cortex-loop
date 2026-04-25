"""Postmortem record for the V2 communication loop early checkpoint."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lab.live_validation_common import LOCAL_LIVE_ROOT, now_utc_iso, write_json


POSTMORTEM_PATH = (
    LOCAL_LIVE_ROOT / "agent_loop_guard" / "v2_communication_postmortem.latest.json"
)


@dataclass(frozen=True, slots=True)
class PostmortemFinding:
    finding_id: str
    severity: str
    failure: str
    evidence: str
    corrective_action: str

    def __post_init__(self) -> None:
        for field_name in (
            "finding_id",
            "severity",
            "failure",
            "evidence",
            "corrective_action",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"PostmortemFinding.{field_name} must be non-empty.")

    def as_payload(self) -> dict[str, str]:
        return {
            "finding_id": self.finding_id,
            "severity": self.severity,
            "failure": self.failure,
            "evidence": self.evidence,
            "corrective_action": self.corrective_action,
        }


FINDINGS: tuple[PostmortemFinding, ...] = (
    PostmortemFinding(
        finding_id="pm-001-blocked-closure-escape",
        severity="critical",
        failure=(
            "`assert-closure --allow-blocked` returned success for blocked live "
            "Claude/Codex gates, which let a checkpoint look like an acceptable "
            "loop outcome."
        ),
        evidence=(
            "The prior report had `claude_live_watchlist_evidence` and "
            "`codex_live_watchlist_evidence` blocked, yet the closeout path used "
            "allow-blocked classification as an acceptable stop."
        ),
        corrective_action=(
            "Blocked gates may still stop for an operator through the hook, but "
            "they can no longer satisfy closure or a closeout contract."
        ),
    ),
    PostmortemFinding(
        finding_id="pm-002-closeout-opt-out",
        severity="critical",
        failure=(
            "The closeout contract allowed `require_full_communication_closure=false` "
            "beside an agent-loop guard, so the live evidence denominator could be "
            "intentionally deferred inside the same closure artifact."
        ),
        evidence=(
            "The prior closeout contract recorded blocked live watchlist gates while "
            "still allowing the managed workflow to checkpoint."
        ),
        corrective_action=(
            "Any closeout that declares an `agent_loop_guard` must require full "
            "communication closure and must reject `allow_blocked`."
        ),
    ),
    PostmortemFinding(
        finding_id="pm-003-live-spend-ambiguity",
        severity="high",
        failure=(
            "The session treated the lack of explicit paid-service approval as a "
            "reason to defer live testing, instead of making that an operator block "
            "that prevents closure."
        ),
        evidence=(
            "Repo policy correctly forbids unapproved paid service-lane commands, "
            "but the loop failed to convert that policy into a hard stop before "
            "closeout."
        ),
        corrective_action=(
            "The S-tier audit protocol gate must lock spend approval or a no-spend "
            "transcript route before live evidence gates can pass."
        ),
    ),
    PostmortemFinding(
        finding_id="pm-004-short-run-anomaly",
        severity="high",
        failure=(
            "A 24-minute run was accepted for a task whose live audit scope should "
            "normally require a multi-hour Claude/Codex evidence pass."
        ),
        evidence=(
            "Only fixture and static review evidence was produced; live transcripts "
            "and next-turn effect checks were absent."
        ),
        corrective_action=(
            "Record expected 180-240 minute audit scope, required live artifact "
            "matrix, and a short-run anomaly rule for sub-120-minute completions."
        ),
    ),
)


def render_postmortem_payload(*, generated_at: str | None = None) -> dict[str, Any]:
    return {
        "surface": "lab",
        "evidence_role": "watchlist",
        "incident": "v2_communication_loop_early_checkpoint",
        "generated_at": generated_at or now_utc_iso(),
        "verdict": "prior_loop_checkpointed_before_live_claude_codex_proof",
        "what_was_not_proven": [
            "Claude CLI live model-visible guidance transcript",
            "Codex CLI/App live model-visible guidance transcript",
            "per-row Core/SRE/AUX live visibility matrix",
            "next-turn effect evidence for guidance meant to constrain behavior",
            "hostile review after live evidence",
        ],
        "minimum_next_session_bar": {
            "closeout_requires": "all agent-loop guard gates pass with evidence",
            "blocked_gate_policy": "operator block only; never closure",
            "expected_runtime_minutes": "180-240",
            "short_run_anomaly_rule": (
                "If the live audit finishes in under 120 minutes, the report must "
                "include explicit hostile-review justification or remain blocked."
            ),
        },
        "findings": [finding.as_payload() for finding in FINDINGS],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.v2_communication_postmortem",
        description="Render the V2 communication loop early-checkpoint postmortem.",
    )
    parser.add_argument("--output", type=Path, default=POSTMORTEM_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    payload = render_postmortem_payload()
    if args.check:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    write_json(args.output, payload)
    print(str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
