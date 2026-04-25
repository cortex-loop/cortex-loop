"""Bounded Claude/Codex Stop-hook guard for Cortex live loop work."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from lab.live_validation_common import LOCAL_LIVE_ROOT, now_utc_iso, write_json


HostSurface = Literal["codex", "claude"]
GateStatus = Literal["pass", "fail", "missing", "blocked", "unknown"]
LoopGuardAction = Literal["allow_stop", "continue", "stop_for_operator"]

LOOP_GUARD_ROOT = LOCAL_LIVE_ROOT / "agent_loop_guard"
LOOP_GUARD_LATEST_PATH = LOOP_GUARD_ROOT / "gates.latest.json"
LOOP_GUARD_SESSIONS_ROOT = LOOP_GUARD_ROOT / "sessions"
DEFAULT_PROFILE = "v2_executive_guidance_live_claude_codex"
DEFAULT_MAX_CONTINUATIONS = 6
SUPPORTED_STOP_EVENTS = frozenset(
    {
        "Stop",
        "SubagentStop",
    }
)
DEFAULT_REQUIRED_GATES = (
    "active_train_reconciled",
    "executive_guidance_contract_present",
    "claude_guidance_fixture_passed",
    "codex_guidance_fixture_passed",
    "claude_live_watchlist_evidence",
    "codex_live_watchlist_evidence",
    "forbidden_claims_absent",
)


@dataclass(frozen=True, slots=True)
class GatePlanStep:
    gate_id: str
    title: str
    pass_criteria: str
    evidence_required: tuple[str, ...]
    next_action: str
    stop_rule: str

    def __post_init__(self) -> None:
        for field_name in (
            "gate_id",
            "title",
            "pass_criteria",
            "next_action",
            "stop_rule",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"GatePlanStep.{field_name} must be non-empty.")
        if not self.evidence_required or any(
            not item.strip() for item in self.evidence_required
        ):
            raise ValueError(
                "GatePlanStep.evidence_required must contain non-empty entries."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "title": self.title,
            "pass_criteria": self.pass_criteria,
            "evidence_required": list(self.evidence_required),
            "next_action": self.next_action,
            "stop_rule": self.stop_rule,
        }


V2_EXECUTIVE_GUIDANCE_PLAN: tuple[GatePlanStep, ...] = (
    GatePlanStep(
        gate_id="active_train_reconciled",
        title="Close the active brake-tonic reconciliation",
        pass_criteria=(
            "The current brake-tonic quiescence exit train is either implemented "
            "in code and tests or explicitly narrowed in doctrine/status before any "
            "successor train is claimed."
        ),
        evidence_required=(
            "updated SRE brake law or explicit doctrine narrowing",
            "targeted SRE/runtime tests proving no sticky guardedness under sustained calm",
            "status truth remains single-owned by internal/truth/cortex_status.json",
        ),
        next_action=(
            "finish or explicitly replace `brake-tonic-quiescence-exit-reconciliation` "
            "before opening the V2 guidance train"
        ),
        stop_rule=(
            "If authority surfaces disagree, stop for operator reconciliation instead "
            "of continuing implementation."
        ),
    ),
    GatePlanStep(
        gate_id="executive_guidance_contract_present",
        title="Define the V2 executive-guidance contract",
        pass_criteria=(
            "A typed V2 contract maps realized SRE families and operator-route state "
            "to bounded model-visible guidance, host-native action, explicit no-op, "
            "or unsupported-with-reason."
        ),
        evidence_required=(
            "typed contract in active V2 code, not V3",
            "tests proving CHECK, SEEK_CONTEXT, BRAKE, BRANCH/continuity, VERIFY/REPAIR, and CLOSURE mappings",
            "negative tests proving no raw AUX memory, certification drift, or hidden policy fork",
        ),
        next_action=(
            "add the smallest V2 executive-guidance carrier and fixture tests before "
            "touching live host loops"
        ),
        stop_rule=(
            "If the mapping only adds diagnostics and cannot affect a model turn, "
            "mark the gate fail and revise the contract."
        ),
    ),
    GatePlanStep(
        gate_id="claude_guidance_fixture_passed",
        title="Prove Claude model-visible guidance in fixtures",
        pass_criteria=(
            "Claude host-control or operator fixture evidence shows Cortex guidance "
            "changes the next Claude turn for the required executive families."
        ),
        evidence_required=(
            "fixture or mocked Claude operator transcript with model-visible guidance",
            "assertions for family-specific next-turn text/action",
            "tests proving unsupported host surfaces degrade to explicit reasons",
        ),
        next_action=(
            "wire Claude-facing prompt or hook guidance for the first failing family "
            "and update the fixture evidence"
        ),
        stop_rule=(
            "If Claude auth or live access is unavailable, keep this fixture gate "
            "separate from the later live gate."
        ),
    ),
    GatePlanStep(
        gate_id="codex_guidance_fixture_passed",
        title="Prove Codex CLI model-visible guidance in fixtures",
        pass_criteria=(
            "Codex CLI/app-server fixture evidence shows Cortex guidance reaches the "
            "next Codex turn through instructions, prompt context, or Stop-hook continuation."
        ),
        evidence_required=(
            "fixture or mocked `codex exec --json`/hook transcript",
            "assertions that continuation prompts include the unmet gate and bounded next action",
            "tests proving the guard does not continue after all gates pass",
        ),
        next_action=(
            "wire Codex-facing guidance through the narrowest prompt/hook path and "
            "record fixture evidence"
        ),
        stop_rule=(
            "If Codex only receives a generic reminder rather than family-specific "
            "guidance, mark the gate fail."
        ),
    ),
    GatePlanStep(
        gate_id="claude_live_watchlist_evidence",
        title="Run bounded Claude live watchlist",
        pass_criteria=(
            "No-spend or explicitly approved Claude operator evidence passes the V2 "
            "guidance watchlist with truthful closure and no approval/safety violations."
        ),
        evidence_required=(
            "preflight/auth result for Claude operator lane",
            "live or approved watchlist artifact covering guidance visibility and closure",
            "explicit classification for auth, budget, or host-capability blocks",
        ),
        next_action=(
            "run the repo live harness for Claude guidance watchlist, or mark blocked "
            "with a concrete operator action if auth/capacity is unavailable"
        ),
        stop_rule=(
            "Do not mark pass from stale transcripts, unavailable auth, or unapproved "
            "paid service-lane calls."
        ),
    ),
    GatePlanStep(
        gate_id="codex_live_watchlist_evidence",
        title="Run bounded Codex CLI live watchlist",
        pass_criteria=(
            "Codex CLI/App evidence passes the V2 guidance watchlist and the loop guard "
            "does not stop early while required gates are pending."
        ),
        evidence_required=(
            "Codex preflight/auth result",
            "`codex exec --json` or app-server evidence showing guidance affects the run",
            "loop-guard state showing bounded continuation and eventual pass/blocked stop",
        ),
        next_action=(
            "run the Codex guidance watchlist through the repo harness and update the "
            "gate report with artifact paths"
        ),
        stop_rule=(
            "Do not pass on final-message claims alone; require event or transcript "
            "evidence that the guidance was visible."
        ),
    ),
    GatePlanStep(
        gate_id="forbidden_claims_absent",
        title="Close with product-truth discipline",
        pass_criteria=(
            "Closeout/status text claims only what shipped runtime behavior or direct "
            "product blockers prove, keeps V3 non-product unless separately archived, "
            "and preserves shipping/conformance distinction."
        ),
        evidence_required=(
            "closeout contract forbidden claims reviewed",
            "status registry/doc regeneration check when status changes",
            "tests or grep proving no V3 cutover or live-pass overclaim is introduced",
        ),
        next_action=(
            "audit final handoff, status text, and closeout claims before allowing the "
            "agent to stop"
        ),
        stop_rule=(
            "If any final text claims full communication, live pass, or V3 archive "
            "without evidence, continue or stop for operator correction."
        ),
    ),
)

if tuple(step.gate_id for step in V2_EXECUTIVE_GUIDANCE_PLAN) != DEFAULT_REQUIRED_GATES:
    raise RuntimeError("V2_EXECUTIVE_GUIDANCE_PLAN must match DEFAULT_REQUIRED_GATES.")


def gate_plan_step(
    gate_id: str,
    plan_steps: tuple[GatePlanStep, ...] = V2_EXECUTIVE_GUIDANCE_PLAN,
) -> GatePlanStep:
    gate_id = _non_empty_string(gate_id, None)
    for step in plan_steps:
        if step.gate_id == gate_id:
            return step
    return _generic_gate_plan_step(gate_id)


def plan_steps_for_required_gates(required_gates: tuple[str, ...]) -> tuple[GatePlanStep, ...]:
    return tuple(gate_plan_step(gate_id) for gate_id in required_gates)


def render_plan_payload(
    plan_steps: tuple[GatePlanStep, ...] = V2_EXECUTIVE_GUIDANCE_PLAN,
) -> dict[str, Any]:
    return {
        "profile": DEFAULT_PROFILE,
        "surface": "agent_loop_guard",
        "scope": "lab",
        "evidence_role": "watchlist",
        "required_gates": [step.gate_id for step in plan_steps],
        "plan_steps": [step.as_payload() for step in plan_steps],
    }


def render_plan_markdown(
    plan_steps: tuple[GatePlanStep, ...] = V2_EXECUTIVE_GUIDANCE_PLAN,
) -> str:
    lines = [
        "# V2 Executive Guidance Loop Plan",
        "",
        "Surface: lab",
        "Evidence role: watchlist",
        "Stop condition: every required gate is pass, or a blocked/max-continuation gate stops for the operator.",
        "",
    ]
    for index, step in enumerate(plan_steps, start=1):
        lines.extend(
            [
                f"{index}. `{step.gate_id}` - {step.title}",
                f"   Pass: {step.pass_criteria}",
                f"   Evidence: {'; '.join(step.evidence_required)}",
                f"   Next: {step.next_action}",
                f"   Stop: {step.stop_rule}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


@dataclass(frozen=True, slots=True)
class GateResult:
    gate_id: str
    status: GateStatus
    reason: str
    next_action: str
    evidence: str | None = None

    def __post_init__(self) -> None:
        if not self.gate_id.strip():
            raise ValueError("GateResult.gate_id must be non-empty after trimming.")
        if self.status not in {"pass", "fail", "missing", "blocked", "unknown"}:
            raise ValueError(
                "GateResult.status must be one of pass, fail, missing, blocked, unknown."
            )
        if not self.reason.strip():
            raise ValueError("GateResult.reason must be non-empty after trimming.")
        if not self.next_action.strip():
            raise ValueError("GateResult.next_action must be non-empty after trimming.")
        if self.evidence is not None and not self.evidence.strip():
            raise ValueError("GateResult.evidence must be non-empty when provided.")

    def as_payload(self) -> dict[str, Any]:
        payload = {
            "gate_id": self.gate_id,
            "status": self.status,
            "reason": self.reason,
            "next_action": self.next_action,
        }
        if self.evidence is not None:
            payload["evidence"] = self.evidence
        return payload


@dataclass(frozen=True, slots=True)
class LoopGateReport:
    profile: str
    required_gates: tuple[str, ...]
    gates: tuple[GateResult, ...]
    max_continuations: int = DEFAULT_MAX_CONTINUATIONS
    generated_at: str | None = None
    surface: str = "agent_loop_guard"
    scope: str = "lab"
    evidence_role: str = "watchlist"
    plan_steps: tuple[GatePlanStep, ...] = V2_EXECUTIVE_GUIDANCE_PLAN

    def __post_init__(self) -> None:
        if not self.profile.strip():
            raise ValueError("LoopGateReport.profile must be non-empty after trimming.")
        if not self.required_gates:
            raise ValueError("LoopGateReport.required_gates must be non-empty.")
        if any(not gate_id.strip() for gate_id in self.required_gates):
            raise ValueError(
                "LoopGateReport.required_gates must contain only non-empty gate ids."
            )
        if self.max_continuations <= 0:
            raise ValueError("LoopGateReport.max_continuations must be positive.")
        if self.surface != "agent_loop_guard":
            raise ValueError("LoopGateReport.surface must be agent_loop_guard.")
        if self.scope != "lab":
            raise ValueError("LoopGateReport.scope must be lab.")
        if self.evidence_role != "watchlist":
            raise ValueError("LoopGateReport.evidence_role must be watchlist.")
        plan_gate_ids = tuple(step.gate_id for step in self.plan_steps)
        if plan_gate_ids != self.required_gates:
            raise ValueError(
                "LoopGateReport.plan_steps must match required_gates in order."
            )

    def gate_map(self) -> dict[str, GateResult]:
        return {gate.gate_id: gate for gate in self.gates}

    def plan_step(self, gate_id: str) -> GatePlanStep:
        return gate_plan_step(gate_id, self.plan_steps)

    def normalized_gates(self) -> tuple[GateResult, ...]:
        gate_map = self.gate_map()
        normalized: list[GateResult] = []
        for gate_id in self.required_gates:
            gate = gate_map.get(gate_id)
            if gate is None:
                gate = GateResult(
                    gate_id=gate_id,
                    status="missing",
                    reason="required gate has no evidence yet",
                    next_action=self.plan_step(gate_id).next_action,
                )
            normalized.append(gate)
        return tuple(normalized)

    def as_payload(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "surface": self.surface,
            "scope": self.scope,
            "evidence_role": self.evidence_role,
            "generated_at": self.generated_at,
            "max_continuations": self.max_continuations,
            "required_gates": list(self.required_gates),
            "gates": [gate.as_payload() for gate in self.gates],
            "plan_steps": [step.as_payload() for step in self.plan_steps],
        }


@dataclass(frozen=True, slots=True)
class LoopGuardState:
    session_id: str
    host: HostSurface
    continuation_count: int = 0
    event_name: str = "Stop"
    stop_hook_active: bool = False
    transcript_path: str | None = None

    def __post_init__(self) -> None:
        if not self.session_id.strip():
            raise ValueError("LoopGuardState.session_id must be non-empty after trimming.")
        if self.host not in {"codex", "claude"}:
            raise ValueError("LoopGuardState.host must be codex or claude.")
        if self.continuation_count < 0:
            raise ValueError("LoopGuardState.continuation_count must be non-negative.")
        if not self.event_name.strip():
            raise ValueError("LoopGuardState.event_name must be non-empty after trimming.")

    def as_payload(self) -> dict[str, Any]:
        payload = {
            "session_id": self.session_id,
            "host": self.host,
            "continuation_count": self.continuation_count,
            "event_name": self.event_name,
            "stop_hook_active": self.stop_hook_active,
        }
        if self.transcript_path is not None:
            payload["transcript_path"] = self.transcript_path
        return payload


@dataclass(frozen=True, slots=True)
class LoopGuardDecision:
    action: LoopGuardAction
    reason: str
    gate_id: str | None = None
    continuation_prompt: str | None = None
    continuation_count: int = 0
    max_continuations: int = DEFAULT_MAX_CONTINUATIONS
    blocking_gate: GateResult | None = None
    pending_gates: tuple[GateResult, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.action not in {"allow_stop", "continue", "stop_for_operator"}:
            raise ValueError(
                "LoopGuardDecision.action must be allow_stop, continue, or stop_for_operator."
            )
        if not self.reason.strip():
            raise ValueError("LoopGuardDecision.reason must be non-empty after trimming.")
        if self.action == "continue" and not (
            self.continuation_prompt and self.continuation_prompt.strip()
        ):
            raise ValueError(
                "LoopGuardDecision.continuation_prompt is required for continue."
            )
        if self.continuation_count < 0:
            raise ValueError("LoopGuardDecision.continuation_count must be non-negative.")
        if self.max_continuations <= 0:
            raise ValueError("LoopGuardDecision.max_continuations must be positive.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "gate_id": self.gate_id,
            "continuation_prompt": self.continuation_prompt,
            "continuation_count": self.continuation_count,
            "max_continuations": self.max_continuations,
            "blocking_gate": (
                self.blocking_gate.as_payload()
                if self.blocking_gate is not None
                else None
            ),
            "pending_gates": [gate.as_payload() for gate in self.pending_gates],
        }

    def as_hook_output(self, *, host: HostSurface) -> dict[str, Any]:
        if host not in {"codex", "claude"}:
            raise ValueError("host must be codex or claude.")
        if self.action == "allow_stop":
            return {"continue": True}
        if self.action == "stop_for_operator":
            return {
                "continue": False,
                "stopReason": self.reason,
                "systemMessage": self.reason,
            }
        return {
            "decision": "block",
            "reason": self.continuation_prompt,
            "systemMessage": (
                "Cortex loop guard prevented an early stop; bounded gate evidence remains."
            ),
        }


def default_gate_report(
    *,
    profile: str = DEFAULT_PROFILE,
    max_continuations: int = DEFAULT_MAX_CONTINUATIONS,
) -> LoopGateReport:
    gates = tuple(
        GateResult(
            gate_id=step.gate_id,
            status="missing",
            reason=f"{step.title} has not been proven yet",
            next_action=step.next_action,
        )
        for step in V2_EXECUTIVE_GUIDANCE_PLAN
    )
    return LoopGateReport(
        profile=profile,
        required_gates=DEFAULT_REQUIRED_GATES,
        gates=gates,
        max_continuations=max_continuations,
        generated_at=now_utc_iso(),
        plan_steps=V2_EXECUTIVE_GUIDANCE_PLAN,
    )


def loop_gate_report_from_payload(payload: dict[str, Any]) -> LoopGateReport:
    if not isinstance(payload, dict):
        raise TypeError("loop gate report payload must be an object.")
    profile = _non_empty_string(payload.get("profile"), DEFAULT_PROFILE)
    required_gates = _coerce_required_gates(payload.get("required_gates"))
    max_continuations = _positive_int(
        payload.get("max_continuations"),
        default=DEFAULT_MAX_CONTINUATIONS,
        field_name="max_continuations",
    )
    gate_payloads = payload.get("gates", [])
    if not isinstance(gate_payloads, list):
        raise TypeError("loop gate report `gates` must be a list.")
    gates = tuple(_gate_result_from_payload(gate_payload) for gate_payload in gate_payloads)
    plan_steps = _coerce_plan_steps(payload.get("plan_steps"), required_gates)
    return LoopGateReport(
        profile=profile,
        required_gates=required_gates,
        gates=gates,
        max_continuations=max_continuations,
        generated_at=_optional_string(payload.get("generated_at")),
        surface=_non_empty_string(payload.get("surface"), "agent_loop_guard"),
        scope=_non_empty_string(payload.get("scope"), "lab"),
        evidence_role=_non_empty_string(payload.get("evidence_role"), "watchlist"),
        plan_steps=plan_steps,
    )


def decide_loop_guard(
    report: LoopGateReport,
    state: LoopGuardState,
    *,
    gate_report_path: Path | None = None,
) -> LoopGuardDecision:
    if state.event_name not in SUPPORTED_STOP_EVENTS:
        return LoopGuardDecision(
            action="allow_stop",
            reason=f"hook event `{state.event_name}` is not a supported stop gate",
            continuation_count=state.continuation_count,
            max_continuations=report.max_continuations,
        )

    normalized_gates = report.normalized_gates()
    blocked = [gate for gate in normalized_gates if gate.status == "blocked"]
    if blocked:
        first = blocked[0]
        return LoopGuardDecision(
            action="stop_for_operator",
            reason=(
                f"Cortex loop guard stopped because gate `{first.gate_id}` is blocked: "
                f"{first.reason}. Next action requires an operator: {first.next_action}."
            ),
            gate_id=first.gate_id,
            continuation_count=state.continuation_count,
            max_continuations=report.max_continuations,
            blocking_gate=first,
            pending_gates=tuple(gate for gate in normalized_gates if gate.status != "pass"),
        )

    pending = tuple(gate for gate in normalized_gates if gate.status != "pass")
    if not pending:
        return LoopGuardDecision(
            action="allow_stop",
            reason="all required Cortex loop gates passed",
            continuation_count=state.continuation_count,
            max_continuations=report.max_continuations,
        )

    if state.continuation_count >= report.max_continuations:
        return LoopGuardDecision(
            action="stop_for_operator",
            reason=(
                "Cortex loop guard reached max_continuations="
                f"{report.max_continuations} with {len(pending)} gate(s) still pending."
            ),
            gate_id=pending[0].gate_id,
            continuation_count=state.continuation_count,
            max_continuations=report.max_continuations,
            pending_gates=pending,
        )

    first = pending[0]
    return LoopGuardDecision(
        action="continue",
        reason=f"gate `{first.gate_id}` is `{first.status}`",
        gate_id=first.gate_id,
        continuation_prompt=_continuation_prompt(
            gate=first,
            pending_count=len(pending),
            report=report,
            state=state,
            gate_report_path=gate_report_path,
        ),
        continuation_count=state.continuation_count,
        max_continuations=report.max_continuations,
        pending_gates=pending,
    )


def render_hook_config(*, host: HostSurface, report_path: Path = LOOP_GUARD_LATEST_PATH) -> str:
    command = f"python3 -m lab.agent_loop_guard hook --host {host} --report {report_path}"
    return json.dumps(
        {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": command,
                                "statusMessage": "Checking Cortex loop gates",
                            }
                        ]
                    }
                ]
            }
        },
        indent=2,
        sort_keys=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.agent_loop_guard",
        description="Evaluate Cortex loop gates and emit Claude/Codex Stop-hook decisions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-report")
    init_parser.add_argument("--output", type=Path, default=LOOP_GUARD_LATEST_PATH)
    init_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    init_parser.add_argument(
        "--max-continuations",
        type=int,
        default=DEFAULT_MAX_CONTINUATIONS,
    )

    evaluate_parser = subparsers.add_parser("evaluate")
    _add_decision_args(evaluate_parser)
    evaluate_parser.add_argument(
        "--format",
        choices=("decision", "hook-json", "summary"),
        default="decision",
    )

    hook_parser = subparsers.add_parser("hook")
    _add_decision_args(hook_parser)

    config_parser = subparsers.add_parser("render-hook-config")
    config_parser.add_argument("--host", choices=("codex", "claude"), required=True)
    config_parser.add_argument("--report", type=Path, default=LOOP_GUARD_LATEST_PATH)

    plan_parser = subparsers.add_parser("render-plan")
    plan_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")

    args = parser.parse_args(argv)
    if args.command == "init-report":
        report = default_gate_report(
            profile=args.profile,
            max_continuations=args.max_continuations,
        )
        write_json(args.output, report.as_payload())
        print(str(args.output))
        return 0

    if args.command == "render-hook-config":
        print(render_hook_config(host=args.host, report_path=args.report))
        return 0

    if args.command == "render-plan":
        if args.format == "json":
            print(json.dumps(render_plan_payload(), indent=2, sort_keys=True))
        else:
            print(render_plan_markdown())
        return 0

    hook_input = _read_stdin_json() if args.command == "hook" else {}
    report = read_gate_report(args.report)
    prior_state = load_loop_guard_state(
        host=args.host,
        hook_input=hook_input,
        explicit_state_path=args.state,
    )
    decision = decide_loop_guard(
        report,
        prior_state,
        gate_report_path=args.report,
    )
    if args.command == "hook":
        updated_state = _state_after_decision(prior_state, decision)
        persist_loop_guard_state(
            updated_state,
            decision=decision,
            explicit_state_path=args.state,
        )
        print(json.dumps(decision.as_hook_output(host=args.host), sort_keys=True))
        return 0

    if args.format == "hook-json":
        print(json.dumps(decision.as_hook_output(host=args.host), indent=2, sort_keys=True))
    elif args.format == "summary":
        print(render_decision_summary(decision))
    else:
        print(json.dumps(decision.as_payload(), indent=2, sort_keys=True))
    return 0


def read_gate_report(path: Path) -> LoopGateReport:
    if not path.exists():
        return default_gate_report()
    return loop_gate_report_from_payload(json.loads(path.read_text(encoding="utf-8")))


def load_loop_guard_state(
    *,
    host: HostSurface,
    hook_input: dict[str, Any] | None = None,
    explicit_state_path: Path | None = None,
) -> LoopGuardState:
    hook_input = hook_input or {}
    session_id = _session_id_from_hook_input(hook_input)
    state_path = explicit_state_path or _session_state_path(session_id, host=host)
    continuation_count = 0
    if state_path.exists():
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        continuation_count = _positive_int(
            payload.get("continuation_count"),
            default=0,
            field_name="continuation_count",
            allow_zero=True,
        )
    return LoopGuardState(
        session_id=session_id,
        host=host,
        continuation_count=continuation_count,
        event_name=_non_empty_string(hook_input.get("hook_event_name"), "Stop"),
        stop_hook_active=bool(hook_input.get("stop_hook_active")),
        transcript_path=_optional_string(hook_input.get("transcript_path")),
    )


def persist_loop_guard_state(
    state: LoopGuardState,
    *,
    decision: LoopGuardDecision,
    explicit_state_path: Path | None = None,
) -> None:
    state_path = explicit_state_path or _session_state_path(state.session_id, host=state.host)
    payload = state.as_payload()
    payload.update(
        {
            "surface": "agent_loop_guard",
            "scope": "lab",
            "evidence_role": "watchlist",
            "updated_at": now_utc_iso(),
            "last_decision": decision.as_payload(),
        }
    )
    write_json(state_path, payload)


def render_decision_summary(decision: LoopGuardDecision) -> str:
    if decision.action == "allow_stop":
        return f"allow_stop: {decision.reason}"
    if decision.action == "stop_for_operator":
        return f"stop_for_operator: {decision.reason}"
    return "\n".join(
        [
            f"continue: {decision.reason}",
            f"pending gates: {len(decision.pending_gates)}",
            f"next prompt: {decision.continuation_prompt}",
        ]
    )


def _continuation_prompt(
    *,
    gate: GateResult,
    pending_count: int,
    report: LoopGateReport,
    state: LoopGuardState,
    gate_report_path: Path | None,
) -> str:
    evidence_path = str(gate_report_path or LOOP_GUARD_LATEST_PATH)
    next_count = state.continuation_count + 1
    plan_step = report.plan_step(gate.gate_id)
    return (
        "Cortex loop guard: do not stop yet. "
        f"The next unmet gate is `{gate.gate_id}` ({plan_step.title}) with status "
        f"`{gate.status}`: {gate.reason}. "
        f"Pass criteria: {plan_step.pass_criteria}. "
        f"Required evidence: {'; '.join(plan_step.evidence_required)}. "
        f"Take only this next action: {gate.next_action}. "
        f"Gate stop rule: {plan_step.stop_rule}. "
        f"Then update `{evidence_path}` with bounded gate evidence. "
        f"Pending gates: {pending_count}. "
        f"Continuation budget after this pass: {next_count}/{report.max_continuations}. "
        "Do not run paid service-lane commands unless the current chat explicitly approved spend. "
        "Do not widen shipping truth, do not reactivate V3 as product truth, and stop only when all required gates pass."
    )


def _state_after_decision(
    state: LoopGuardState,
    decision: LoopGuardDecision,
) -> LoopGuardState:
    if decision.action != "continue":
        return state
    return LoopGuardState(
        session_id=state.session_id,
        host=state.host,
        continuation_count=state.continuation_count + 1,
        event_name=state.event_name,
        stop_hook_active=state.stop_hook_active,
        transcript_path=state.transcript_path,
    )


def _add_decision_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", choices=("codex", "claude"), required=True)
    parser.add_argument("--report", type=Path, default=LOOP_GUARD_LATEST_PATH)
    parser.add_argument("--state", type=Path)


def _read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise TypeError("hook stdin must be a JSON object.")
    return payload


def _gate_result_from_payload(payload: Any) -> GateResult:
    if not isinstance(payload, dict):
        raise TypeError("each gate result must be an object.")
    return GateResult(
        gate_id=_non_empty_string(payload.get("gate_id"), None),
        status=_non_empty_string(payload.get("status"), "unknown"),  # type: ignore[arg-type]
        reason=_non_empty_string(payload.get("reason"), "gate has no reason recorded"),
        next_action=_non_empty_string(
            payload.get("next_action"),
            "produce bounded evidence for this gate",
        ),
        evidence=_optional_string(payload.get("evidence")),
    )


def _gate_plan_step_from_payload(payload: Any) -> GatePlanStep:
    if not isinstance(payload, dict):
        raise TypeError("each gate plan step must be an object.")
    evidence_payload = payload.get("evidence_required")
    if not isinstance(evidence_payload, list):
        raise TypeError("gate plan step `evidence_required` must be a list.")
    return GatePlanStep(
        gate_id=_non_empty_string(payload.get("gate_id"), None),
        title=_non_empty_string(payload.get("title"), None),
        pass_criteria=_non_empty_string(payload.get("pass_criteria"), None),
        evidence_required=tuple(
            _non_empty_string(item, None) for item in evidence_payload
        ),
        next_action=_non_empty_string(payload.get("next_action"), None),
        stop_rule=_non_empty_string(payload.get("stop_rule"), None),
    )


def _coerce_plan_steps(
    value: Any,
    required_gates: tuple[str, ...],
) -> tuple[GatePlanStep, ...]:
    if value is None:
        return plan_steps_for_required_gates(required_gates)
    if not isinstance(value, list):
        raise TypeError("plan_steps must be a list when provided.")
    plan_steps = tuple(_gate_plan_step_from_payload(item) for item in value)
    if not plan_steps:
        raise ValueError("plan_steps must be non-empty when provided.")
    return plan_steps


def _coerce_required_gates(value: Any) -> tuple[str, ...]:
    if value is None:
        return DEFAULT_REQUIRED_GATES
    if not isinstance(value, list):
        raise TypeError("required_gates must be a list when provided.")
    gates = tuple(_non_empty_string(item, None) for item in value)
    if not gates:
        raise ValueError("required_gates must be non-empty when provided.")
    return gates


def _positive_int(
    value: Any,
    *,
    default: int,
    field_name: str,
    allow_zero: bool = False,
) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")
    if allow_zero and value == 0:
        return value
    if value <= 0:
        raise ValueError(f"{field_name} must be positive.")
    return value


def _non_empty_string(value: Any, default: str | None) -> str:
    if value is None:
        if default is None:
            raise ValueError("expected non-empty string.")
        return default
    if not isinstance(value, str) or not value.strip():
        if default is None:
            raise ValueError("expected non-empty string.")
        return default
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _session_id_from_hook_input(hook_input: dict[str, Any]) -> str:
    explicit = _optional_string(hook_input.get("session_id"))
    if explicit is not None:
        return explicit
    transcript_path = _optional_string(hook_input.get("transcript_path"))
    if transcript_path is not None:
        return _slug(transcript_path)
    return "manual"


def _session_state_path(session_id: str, *, host: HostSurface) -> Path:
    return LOOP_GUARD_SESSIONS_ROOT / f"{host}-{_slug(session_id)}.json"


def _generic_gate_plan_step(gate_id: str) -> GatePlanStep:
    return GatePlanStep(
        gate_id=gate_id,
        title=f"Complete `{gate_id}`",
        pass_criteria=(
            f"The `{gate_id}` gate has bounded evidence and passes according to its "
            "owning harness or operator report."
        ),
        evidence_required=(
            f"bounded evidence for `{gate_id}`",
            "updated gate report with pass, fail, blocked, or unknown classification",
        ),
        next_action=f"produce and record bounded evidence for `{gate_id}`",
        stop_rule=(
            f"If `{gate_id}` is blocked by authorization, capacity, or unclear scope, "
            "stop for operator classification instead of marking pass."
        ),
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return slug or "session"


if __name__ == "__main__":
    raise SystemExit(main())
