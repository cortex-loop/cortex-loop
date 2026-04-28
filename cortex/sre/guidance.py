"""Model-visible Cortex v2 executive guidance contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


GUIDANCE_MARKER = "CORTEX_V2_EXECUTIVE_GUIDANCE"


class GuidanceVisibility(str, Enum):
    MODEL_VISIBLE = "model-visible"
    HOST_NATIVE = "host-native"
    INTERNAL_ONLY = "internal-only"
    UNSUPPORTED = "unsupported"


class GuidanceMode(str, Enum):
    RAW = "raw"
    FULL = "full"
    COMPRESSED_DYNAMIC = "compressed_dynamic"
    PRODUCT_NORMAL = "product_normal"


class GuidanceProfile(str, Enum):
    NORMAL = "normal"
    AUDIT_FULL = "audit_full"
    EVAL_RAW = "eval_raw"


class GuidanceCoverageStatus(str, Enum):
    ALWAYS_ON = "always_on"
    DYNAMIC_TRIGGERED = "dynamic_triggered"
    MODEL_VISIBLE_DIRECTIVE = "model_visible_directive"
    KERNEL_ENFORCED = "kernel_enforced"
    SIDECAR_GUARDRAIL = "sidecar_guardrail"
    SILENT_WITH_REASON = "silent_with_reason"


class ExecutiveInterventionIntent(str, Enum):
    CHECK = "CHECK"
    SEEK_CONTEXT = "SEEK_CONTEXT"
    BRAKE = "BRAKE"
    REPAIR = "REPAIR"
    CONTINUE = "CONTINUE"
    CLOSE = "CLOSE"


DEFAULT_GUIDANCE_PROFILE = GuidanceProfile.NORMAL
DEFAULT_PRODUCT_GUIDANCE_MODE = GuidanceMode.PRODUCT_NORMAL


@dataclass(frozen=True, slots=True)
class V2GuidanceRow:
    row_id: str
    packet: str
    responsibility: str
    visibility: GuidanceVisibility
    model_guidance: str
    reason: str
    bio_to_code_skills: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("row_id", "packet", "responsibility", "model_guidance", "reason"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"V2GuidanceRow.{field_name} must be non-empty.")
        if not isinstance(self.visibility, GuidanceVisibility):
            actual_type = type(self.visibility).__name__
            raise TypeError(
                "V2GuidanceRow.visibility must be GuidanceVisibility, "
                f"got {actual_type}."
            )
        if any(not (isinstance(skill, str) and skill.strip()) for skill in self.bio_to_code_skills):
            raise ValueError(
                "V2GuidanceRow.bio_to_code_skills must contain only non-empty strings."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "packet": self.packet,
            "responsibility": self.responsibility,
            "visibility": self.visibility.value,
            "model_guidance": self.model_guidance,
            "reason": self.reason,
            "bio_to_code_skills": list(self.bio_to_code_skills),
        }


@dataclass(frozen=True, slots=True)
class ExecutiveGuidanceContext:
    host_name: str
    surface: str
    transport_channel: str
    session_id: str | None = None
    event_index: int = 0
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    last_selected_family: str | None = None
    last_brake_state: str | None = None
    next_recommended_move: str | None = None
    last_commitment_result_summary: str | None = None
    offline_publication_active: bool = False

    def __post_init__(self) -> None:
        for field_name in ("host_name", "surface", "transport_channel", "active_track_ref"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"ExecutiveGuidanceContext.{field_name} must be non-empty."
                )
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "ExecutiveGuidanceContext.session_id must be non-empty when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ExecutiveGuidanceContext.event_index must be int, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError("ExecutiveGuidanceContext.event_index must be non-negative.")
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "ExecutiveGuidanceContext.pending_goal_refs must contain only non-empty strings."
            )
        for field_name in (
            "last_selected_family",
            "last_brake_state",
            "next_recommended_move",
            "last_commitment_result_summary",
        ):
            value = getattr(self, field_name)
            if value is not None and not (isinstance(value, str) and value.strip()):
                raise ValueError(
                    f"ExecutiveGuidanceContext.{field_name} must be non-empty when provided."
                )
        if not isinstance(self.offline_publication_active, bool):
            actual_type = type(self.offline_publication_active).__name__
            raise TypeError(
                "ExecutiveGuidanceContext.offline_publication_active must be bool, "
                f"got {actual_type}."
            )


@dataclass(frozen=True, slots=True)
class V2GuidanceCoverage:
    row_id: str
    status: GuidanceCoverageStatus
    trigger_reason: str
    rendered: bool

    def __post_init__(self) -> None:
        if not isinstance(self.row_id, str) or not self.row_id.strip():
            raise ValueError("V2GuidanceCoverage.row_id must be non-empty.")
        if not isinstance(self.status, GuidanceCoverageStatus):
            actual_type = type(self.status).__name__
            raise TypeError(
                "V2GuidanceCoverage.status must be GuidanceCoverageStatus, "
                f"got {actual_type}."
            )
        if not isinstance(self.trigger_reason, str) or not self.trigger_reason.strip():
            raise ValueError("V2GuidanceCoverage.trigger_reason must be non-empty.")
        if not isinstance(self.rendered, bool):
            actual_type = type(self.rendered).__name__
            raise TypeError(
                "V2GuidanceCoverage.rendered must be bool, "
                f"got {actual_type}."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "status": self.status.value,
            "trigger_reason": self.trigger_reason,
            "rendered": self.rendered,
        }


@dataclass(frozen=True, slots=True)
class InterventionIntentView:
    intent: ExecutiveInterventionIntent
    source: str
    selected_family: str | None
    next_move: str | None
    policy_note: str

    def as_payload(self) -> dict[str, str | None]:
        return {
            "intent": self.intent.value,
            "source": self.source,
            "selected_family": self.selected_family,
            "next_move": self.next_move,
            "policy_note": self.policy_note,
        }


@dataclass(frozen=True, slots=True)
class ProductTaskSignals:
    repair_requested: bool = False
    verification_requested: bool = False
    missing_context: bool = False
    resume_continuity: bool = False
    repeated_failure: bool = False
    closure_pressure: bool = False
    unsupported_broad_claim: bool = False
    simple_clean: bool = False
    cross_host_conformance: bool = False

    def as_payload(self) -> dict[str, bool]:
        return {
            "repair_requested": self.repair_requested,
            "verification_requested": self.verification_requested,
            "missing_context": self.missing_context,
            "resume_continuity": self.resume_continuity,
            "repeated_failure": self.repeated_failure,
            "closure_pressure": self.closure_pressure,
            "unsupported_broad_claim": self.unsupported_broad_claim,
            "simple_clean": self.simple_clean,
            "cross_host_conformance": self.cross_host_conformance,
        }


@dataclass(frozen=True, slots=True)
class ProductGuidanceDecision:
    posture: ExecutiveInterventionIntent
    source: str
    task_signals: ProductTaskSignals
    runtime_intent: ExecutiveInterventionIntent
    directives: tuple[str, ...] = ()
    prohibitions: tuple[str, ...] = ()
    close_gate: str | None = None
    model_visible_row_ids: tuple[str, ...] = ()
    kernel_enforced_row_ids: tuple[str, ...] = ()
    sidecar_guardrail_row_ids: tuple[str, ...] = ()

    def as_payload(self) -> dict[str, Any]:
        return {
            "posture": self.posture.value,
            "source": self.source,
            "task_signals": self.task_signals.as_payload(),
            "runtime_intent": self.runtime_intent.value,
            "directives": list(self.directives),
            "prohibitions": list(self.prohibitions),
            "close_gate": self.close_gate,
            "model_visible_row_ids": list(self.model_visible_row_ids),
            "kernel_enforced_row_ids": list(self.kernel_enforced_row_ids),
            "sidecar_guardrail_row_ids": list(self.sidecar_guardrail_row_ids),
        }


V2_EXECUTIVE_GUIDANCE_ROWS: tuple[V2GuidanceRow, ...] = (
    V2GuidanceRow(
        row_id="core.lifecycle_dispatch",
        packet="core",
        responsibility="lifecycle dispatch and host-native realization",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Use only the current host's lawful lifecycle surface; when a surface is "
            "missing, degrade explicitly instead of inventing parity."
        ),
        reason="Core native-transport precedence must affect the next turn.",
    ),
    V2GuidanceRow(
        row_id="core.commitment_certification",
        packet="core",
        responsibility="commitment extraction, certification, and provenance",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Do not call work certified, complete, or externally consequential unless "
            "the host evidence and provenance would support that commitment."
        ),
        reason="Commitment truth is core-owned and cannot be softened by executive pressure.",
        bio_to_code_skills=("Truth-preserving commitments and bounded certification",),
    ),
    V2GuidanceRow(
        row_id="core.environment_degradation",
        packet="core",
        responsibility="environment split, degradation, and contradiction preservation",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Preserve environment uncertainty, unsupported capability, and contradiction "
            "as explicit reasons; do not smooth them into a confident story."
        ),
        reason="Unsupported or mixed host behavior must be observable to the model.",
    ),
    V2GuidanceRow(
        row_id="runtime.verified_work_repair",
        packet="shared-runtime",
        responsibility="verified-work preservation and bounded repair",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "If verification or repair is active, preserve the lawful work surface, "
            "repair only the failing allowed paths, and avoid unrelated rewrites."
        ),
        reason="The shared repair loop must constrain the next model action, not only audit it later.",
        bio_to_code_skills=("Bounded correction and verified-work preservation",),
    ),
    V2GuidanceRow(
        row_id="sre.family_policy",
        packet="sre",
        responsibility="soft-control family selection and realization",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Treat the selected family as the executive posture for the next move; if "
            "realization degrades, say which family could not be realized and why."
        ),
        reason="SRE selection is actionable only when it reaches the model-facing turn.",
    ),
    V2GuidanceRow(
        row_id="sre.uncertainty_brake",
        packet="sre",
        responsibility="uncertainty classes, brake state, and tonic hysteresis",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "When uncertainty or brake pressure is elevated, narrow the next move to "
            "evidence, verification, context, or brake relief rather than broad expansion."
        ),
        reason="Brake and uncertainty are executive controls, not diagnostics-only numbers.",
        bio_to_code_skills=("Uncertainty handling and brake",),
    ),
    V2GuidanceRow(
        row_id="sre.branch_continuity",
        packet="sre",
        responsibility="branch continuity, suspend/resume, and pending-goal discipline",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Keep the main task, active track, and pending goals explicit; resume only "
            "from branch-linked cues and close or carry debt truthfully."
        ),
        reason="Continuity has to change the model's next turn to prevent task drift.",
        bio_to_code_skills=("Branch continuity, suspend/resume, and truthful closure",),
    ),
    V2GuidanceRow(
        row_id="sre.intervention_pricing",
        packet="sre",
        responsibility="intervention pricing, neutral dominance, risk weighting",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Prefer neutral continuation unless a bounded executive family clearly "
            "beats it; CHECK/SEEK_CONTEXT may become cheaper under fn-heavy risk."
        ),
        reason="Intervention pricing must prevent gratuitous control burden in the model turn.",
        bio_to_code_skills=("Intervention pricing versus neutrality",),
    ),
    V2GuidanceRow(
        row_id="sre.blocker_goal_debt",
        packet="sre",
        responsibility="blocker surfacing, goal debt, and truthful closure",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Surface blockers and unresolved goal debt before closure; do not hide a "
            "blocked state behind forward-motion language."
        ),
        reason="Blocker truth is useful only if the model cannot skip it.",
        bio_to_code_skills=("Blocker surfacing and goal-debt management",),
    ),
    V2GuidanceRow(
        row_id="sre.anti_thrash_probe",
        packet="sre",
        responsibility="anti-thrash, evidence progress, and probe truth",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Do not repeat the same failed family under unchanged conditions; use real "
            "probe/evidence progress, or state the unsupported probe reason."
        ),
        reason="Anti-thrash and probe truth must constrain the next attempted action.",
    ),
    V2GuidanceRow(
        row_id="host.claude_cli",
        packet="host",
        responsibility="Claude CLI/message-stream realization",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "On Claude, this guidance rides system/prompt text; no undocumented tool or "
            "approval surface is assumed."
        ),
        reason="Claude conformance must preserve host-native differences.",
        bio_to_code_skills=("Multi-host executive continuity",),
    ),
    V2GuidanceRow(
        row_id="host.codex_cli",
        packet="host",
        responsibility="Codex CLI/OpenAI-compatible realization",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "On Codex/OpenAI, this guidance rides instructions or prompt text; hook or "
            "app evidence is watchlist unless separately promoted."
        ),
        reason="Codex proof must show prompt/instruction visibility, not just post-run records.",
        bio_to_code_skills=("Multi-host executive continuity",),
    ),
    V2GuidanceRow(
        row_id="host.gemini_reference_conformance",
        packet="host",
        responsibility="Gemini and reference conformance truth",
        visibility=GuidanceVisibility.HOST_NATIVE,
        model_guidance=(
            "Keep Gemini and reference in conformance truth; do not claim Claude/Codex "
            "fixtures prove every host surface."
        ),
        reason="Shipping truth and conformance truth must not collapse into one host.",
        bio_to_code_skills=("Multi-host executive continuity",),
    ),
    V2GuidanceRow(
        row_id="aux.default_zero_removable",
        packet="aux",
        responsibility="AUX removability, runtime-off default, and Q_mem zero",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Treat AUX as removable and runtime-off by default; without an explicit "
            "publication, do not use raw AUX memory or hidden support priors."
        ),
        reason="AUX boundaries must be communicated because hidden memory would change behavior.",
        bio_to_code_skills=("Offline consolidation and support geometry",),
    ),
    V2GuidanceRow(
        row_id="aux.publication_only",
        packet="aux",
        responsibility="explicit support publication and non-sovereignty",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "If an offline publication is present, use it only as removable soft-control "
            "support; it never certifies commitments or rewrites blockedness."
        ),
        reason="Published support can bias control only through explicit, bounded channels.",
        bio_to_code_skills=("Offline consolidation and support geometry",),
    ),
    V2GuidanceRow(
        row_id="operational.truth_distinctions",
        packet="operational",
        responsibility="Cortex, shipping, conformance, lab, and active-train truth",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Keep Cortex truth, shipping truth, conformance truth, active-train truth, "
            "and lab/watchlist evidence separate in any claim."
        ),
        reason="Truth distinctions prevent overclaiming from partial host evidence.",
    ),
    V2GuidanceRow(
        row_id="negative.forbidden_shortcuts",
        packet="negative",
        responsibility="forbidden communication shortcuts",
        visibility=GuidanceVisibility.MODEL_VISIBLE,
        model_guidance=(
            "Never treat diagnostics-only output, one file, one host, extracted Cortex incubation work, "
            "or final-message assertions as full V2 communication proof."
        ),
        reason="The current closure risk is mistaking calculated state for communicated guidance.",
    ),
)


_ALWAYS_ON_COMPRESSED_ROWS = frozenset(
    {
        "core.commitment_certification",
        "core.environment_degradation",
        "aux.default_zero_removable",
        "operational.truth_distinctions",
        "negative.forbidden_shortcuts",
    }
)

_INTERVENTION_INTENT_POLICY_NOTES = {
    ExecutiveInterventionIntent.CHECK: (
        "Verify before claiming; CHECK is an existing SRE family, not a new law."
    ),
    ExecutiveInterventionIntent.SEEK_CONTEXT: (
        "Seek missing context before expanding; SEEK_CONTEXT is an existing SRE family."
    ),
    ExecutiveInterventionIntent.BRAKE: (
        "Narrow or stop until the brake reason is relieved; BRAKE is an existing SRE family."
    ),
    ExecutiveInterventionIntent.REPAIR: (
        "Preserve verified work and repair only the bounded failing surface."
    ),
    ExecutiveInterventionIntent.CONTINUE: (
        "Continue neutrally when intervention has not clearly beaten the default move."
    ),
    ExecutiveInterventionIntent.CLOSE: (
        "Close only with supported commitments, blockers, and residual debt explicit."
    ),
}


def build_guidance_context_from_session(
    *,
    host_name: str,
    surface: str,
    transport_channel: str,
    session: Any | None = None,
    offline_publication_active: bool = False,
) -> ExecutiveGuidanceContext:
    if session is None:
        return ExecutiveGuidanceContext(
            host_name=host_name,
            surface=surface,
            transport_channel=transport_channel,
            offline_publication_active=offline_publication_active,
        )
    return ExecutiveGuidanceContext(
        host_name=host_name,
        surface=surface,
        transport_channel=transport_channel,
        session_id=_optional_string(getattr(session, "session_id", None)),
        event_index=int(getattr(session, "event_index", 0)),
        active_track_ref=_safe_track_ref(str(getattr(session, "active_track_ref", "main"))),
        pending_goal_refs=tuple(str(ref) for ref in getattr(session, "pending_goal_refs", ())),
        last_selected_family=_enum_or_string(getattr(session, "last_selected_family", None)),
        last_brake_state=_last_string(getattr(session, "brake_history", ())),
        next_recommended_move=_optional_string(
            getattr(session, "next_recommended_move", None)
        ),
        last_commitment_result_summary=_optional_string(
            getattr(session, "last_commitment_result_summary", None)
        ),
        offline_publication_active=offline_publication_active,
    )


def render_executive_guidance(
    context: ExecutiveGuidanceContext,
    *,
    mode: GuidanceMode | str = GuidanceMode.FULL,
    task_text: str | None = None,
) -> str:
    if not isinstance(context, ExecutiveGuidanceContext):
        actual_type = type(context).__name__
        raise TypeError(
            "render_executive_guidance.context must be ExecutiveGuidanceContext, "
            f"got {actual_type}."
        )
    guidance_mode = _coerce_guidance_mode(mode)
    if guidance_mode is GuidanceMode.RAW:
        return ""
    if guidance_mode is GuidanceMode.PRODUCT_NORMAL:
        return _render_product_normal_guidance(context, task_text=task_text)
    if guidance_mode is GuidanceMode.COMPRESSED_DYNAMIC:
        return _render_compressed_dynamic_guidance(context)
    return _render_full_guidance(context)


def guidance_mode_for_profile(profile: GuidanceProfile | str) -> GuidanceMode:
    guidance_profile = _coerce_guidance_profile(profile)
    if guidance_profile is GuidanceProfile.NORMAL:
        return DEFAULT_PRODUCT_GUIDANCE_MODE
    if guidance_profile is GuidanceProfile.AUDIT_FULL:
        return GuidanceMode.FULL
    if guidance_profile is GuidanceProfile.EVAL_RAW:
        return GuidanceMode.RAW
    raise ValueError(f"unsupported guidance profile: {profile}")


def _render_full_guidance(context: ExecutiveGuidanceContext) -> str:
    lines = [
        GUIDANCE_MARKER,
        "mode: full",
        f"host: {context.host_name}",
        f"surface: {context.surface}",
        f"transport_channel: {context.transport_channel}",
        "runtime_state:",
        f"- session_id: {_display(context.session_id)}",
        f"- event_index: {context.event_index}",
        f"- active_track_ref: {context.active_track_ref}",
        f"- pending_goal_refs: {', '.join(context.pending_goal_refs) if context.pending_goal_refs else 'none'}",
        f"- last_selected_family: {_display(context.last_selected_family)}",
        f"- last_brake_state: {_display(context.last_brake_state)}",
        f"- next_recommended_move: {_display(context.next_recommended_move)}",
        f"- last_commitment_result: {_display(context.last_commitment_result_summary)}",
        f"- aux_publication: {'explicit-publication-present' if context.offline_publication_active else 'inactive-default-zero'}",
        "contract_rows:",
    ]
    for row in V2_EXECUTIVE_GUIDANCE_ROWS:
        lines.extend(
            [
                f"- row_id: {row.row_id}",
                f"  packet: {row.packet}",
                f"  responsibility: {row.responsibility}",
                f"  visibility: {row.visibility.value}",
                f"  model_guidance: {row.model_guidance}",
                f"  reason: {row.reason}",
            ]
        )
    lines.extend(
        [
            "next_turn_rule:",
            "- Apply model-visible rows to the next response. For host-native or internal-only rows, keep the reason explicit instead of pretending they were model-visible.",
            "- If guidance conflicts with a hard system/developer instruction, obey the harder instruction and report the Cortex degradation.",
        ]
    )
    return "\n".join(lines)


def prepend_guidance_to_prompt(
    prompt: str,
    context: ExecutiveGuidanceContext,
    *,
    mode: GuidanceMode | str = GuidanceMode.FULL,
    task_text: str | None = None,
) -> str:
    prompt_text = _required_text(prompt, "prompt")
    guidance = render_executive_guidance(
        context,
        mode=mode,
        task_text=prompt_text if task_text is None else task_text,
    )
    if not guidance:
        return prompt_text
    if _has_rendered_guidance_block(prompt_text):
        return prompt_text
    return f"{guidance}\n\nUSER_TASK\n{prompt_text}"


def append_guidance_to_channel(
    existing_text: str | None,
    context: ExecutiveGuidanceContext,
    *,
    mode: GuidanceMode | str = GuidanceMode.FULL,
    task_text: str | None = None,
) -> str:
    guidance = render_executive_guidance(context, mode=mode, task_text=task_text)
    if existing_text is not None:
        base = _required_text(existing_text, "existing_text")
        if not guidance:
            return base
        if _has_rendered_guidance_block(base):
            return base
        return f"{base.rstrip()}\n\n{guidance}"
    if not guidance:
        return ""
    return guidance


def v2_guidance_inventory_payload() -> list[dict[str, Any]]:
    return [row.as_payload() for row in V2_EXECUTIVE_GUIDANCE_ROWS]


def build_intervention_intent_view(
    context: ExecutiveGuidanceContext,
) -> InterventionIntentView:
    if not isinstance(context, ExecutiveGuidanceContext):
        actual_type = type(context).__name__
        raise TypeError(
            "build_intervention_intent_view.context must be ExecutiveGuidanceContext, "
            f"got {actual_type}."
        )
    selected_family = context.last_selected_family
    next_move = context.next_recommended_move
    cue_text = " ".join(
        part.lower()
        for part in (selected_family, next_move, context.last_commitment_result_summary)
        if part
    )
    if _contains_any(cue_text, ("repair", "fix failing", "preserve verified")):
        intent = ExecutiveInterventionIntent.REPAIR
        source = "next_move"
    elif _contains_any(cue_text, ("close", "final", "handoff", "complete")):
        intent = ExecutiveInterventionIntent.CLOSE
        source = "next_move"
    elif selected_family == "check" or _contains_any(cue_text, ("check", "verify", "test")):
        intent = ExecutiveInterventionIntent.CHECK
        source = "selected_family" if selected_family == "check" else "next_move"
    elif selected_family == "seek-context" or _contains_any(cue_text, ("seek", "context", "inspect", "read")):
        intent = ExecutiveInterventionIntent.SEEK_CONTEXT
        source = "selected_family" if selected_family == "seek-context" else "next_move"
    elif selected_family == "brake" or _contains_any(cue_text, ("brake", "blocked", "stop")):
        intent = ExecutiveInterventionIntent.BRAKE
        source = "selected_family" if selected_family == "brake" else "runtime_state"
    else:
        intent = ExecutiveInterventionIntent.CONTINUE
        source = "neutral_default"
    return InterventionIntentView(
        intent=intent,
        source=source,
        selected_family=selected_family,
        next_move=next_move,
        policy_note=_INTERVENTION_INTENT_POLICY_NOTES[intent],
    )


def extract_product_task_signals(task_text: str | None) -> ProductTaskSignals:
    text = _normalized_task_text(task_text)
    if not text:
        return ProductTaskSignals()

    repair_requested = _contains_any(
        text,
        (
            "fix",
            "repair",
            "failing",
            "failure",
            "broken",
            "bug",
            "test failing",
            "tests failing",
            "tests are failing",
            "smallest issue",
            "smallest failing",
        ),
    )
    verification_requested = _contains_any(
        text,
        (
            "verify",
            "verification",
            "test",
            "tests",
            "prove",
            "evidence",
            "check",
        ),
    )
    missing_context = _contains_any(
        text,
        (
            "missing context",
            "need context",
            "insufficient context",
            "not enough context",
            "which file",
            "don't know",
            "dont know",
            "not sure",
            "unclear",
            "ambiguous",
            "unknown",
        ),
    )
    resume_continuity = _contains_any(
        text,
        (
            "resume",
            "previous session",
            "continue from",
            "branch",
            "pending goal",
            "where we left off",
        ),
    )
    repeated_failure = _contains_any(
        text,
        (
            "same patch",
            "same failed",
            "unchanged",
            "again and again",
            "keeps failing",
            "kept failing",
            "repeated failure",
            "three times",
            "multiple times",
        ),
    )
    closure_pressure = _contains_any(
        text,
        (
            "close out",
            "closeout",
            "final handoff",
            "handoff",
            "done",
            "complete",
            "finished",
            "finish the session",
            "session is finished",
        ),
    )
    unsupported_broad_claim = _contains_any(
        text,
        (
            "fully proven",
            "all hosts are proven",
            "proves every host",
            "product perfection",
            "fully optimized across",
            "fully close the gap",
            "perfect across",
            "generally improves models",
        ),
    )
    cross_host_conformance = _contains_any(
        text,
        (
            "all hosts",
            "cross-host",
            "codex",
            "gemini",
            "reference",
            "conformance",
        ),
    )
    simple_clean = (
        not any(
            (
                repair_requested,
                verification_requested,
                missing_context,
                resume_continuity,
                repeated_failure,
                closure_pressure,
                unsupported_broad_claim,
                cross_host_conformance,
            )
        )
        and (
            text.startswith("respond exactly with")
            or text in {"ok", "hello", "say ok", "return ok"}
            or (len(text) <= 80 and _contains_any(text, ("respond", "return", "say")))
        )
    )
    return ProductTaskSignals(
        repair_requested=repair_requested,
        verification_requested=verification_requested,
        missing_context=missing_context,
        resume_continuity=resume_continuity,
        repeated_failure=repeated_failure,
        closure_pressure=closure_pressure,
        unsupported_broad_claim=unsupported_broad_claim,
        simple_clean=simple_clean,
        cross_host_conformance=cross_host_conformance,
    )


def build_product_guidance_decision(
    context: ExecutiveGuidanceContext,
    *,
    task_text: str | None = None,
) -> ProductGuidanceDecision:
    if not isinstance(context, ExecutiveGuidanceContext):
        actual_type = type(context).__name__
        raise TypeError(
            "build_product_guidance_decision.context must be ExecutiveGuidanceContext, "
            f"got {actual_type}."
        )
    task_signals = extract_product_task_signals(task_text)
    runtime_intent = build_intervention_intent_view(context).intent
    posture, source = _product_posture(task_signals, runtime_intent)
    directives, prohibitions, close_gate = _product_directives_for_posture(
        posture,
        task_signals,
    )
    model_visible_row_ids = _product_model_visible_rows(posture, task_signals)
    kernel_enforced_row_ids = _product_kernel_rows(context)
    sidecar_guardrail_row_ids = _product_sidecar_rows(context)
    return ProductGuidanceDecision(
        posture=posture,
        source=source,
        task_signals=task_signals,
        runtime_intent=runtime_intent,
        directives=directives,
        prohibitions=prohibitions,
        close_gate=close_gate,
        model_visible_row_ids=model_visible_row_ids,
        kernel_enforced_row_ids=tuple(
            row_id
            for row_id in kernel_enforced_row_ids
            if row_id not in model_visible_row_ids
        ),
        sidecar_guardrail_row_ids=tuple(
            row_id
            for row_id in sidecar_guardrail_row_ids
            if row_id not in model_visible_row_ids
            and row_id not in kernel_enforced_row_ids
        ),
    )


def v2_guidance_denominator_coverage_payload(
    context: ExecutiveGuidanceContext,
    *,
    mode: GuidanceMode | str = GuidanceMode.COMPRESSED_DYNAMIC,
    task_text: str | None = None,
) -> dict[str, Any]:
    if not isinstance(context, ExecutiveGuidanceContext):
        actual_type = type(context).__name__
        raise TypeError(
            "v2_guidance_denominator_coverage_payload.context must be ExecutiveGuidanceContext, "
            f"got {actual_type}."
        )
    guidance_mode = _coerce_guidance_mode(mode)
    coverages = _coverage_for_mode(context, guidance_mode, task_text=task_text)
    full_guidance = render_executive_guidance(context, mode=GuidanceMode.FULL)
    rendered_guidance = render_executive_guidance(
        context,
        mode=guidance_mode,
        task_text=task_text,
    )
    rows = [coverage.as_payload() for coverage in coverages]
    return {
        "mode": guidance_mode.value,
        "row_denominator_count": len(V2_EXECUTIVE_GUIDANCE_ROWS),
        "coverage": rows,
        "missing_row_ids": _missing_coverage_row_ids(coverages),
        "rendered_row_ids": [
            coverage.row_id for coverage in coverages if coverage.rendered
        ],
        "guidance_burden": {
            "full_chars": len(full_guidance),
            "mode_chars": len(rendered_guidance),
            "reduction_chars": len(full_guidance) - len(rendered_guidance),
            "mode_is_smaller_than_full": len(rendered_guidance) < len(full_guidance),
        },
        "intervention_intent": build_intervention_intent_view(context).as_payload(),
        "product_kernel_decision": build_product_guidance_decision(
            context,
            task_text=task_text,
        ).as_payload()
        if guidance_mode is GuidanceMode.PRODUCT_NORMAL
        else None,
        "guardrails": {
            "denominator_preserved": not _missing_coverage_row_ids(coverages),
            "raw_aux_forbidden": True,
            "extracted_cortex_overclaim_forbidden": True,
            "shipping_conformance_truth_distinct": True,
        },
    }


def covered_bio_to_code_skills() -> frozenset[str]:
    skills: set[str] = set()
    for row in V2_EXECUTIVE_GUIDANCE_ROWS:
        skills.update(row.bio_to_code_skills)
    return frozenset(skills)


def assert_status_bio_to_code_coverage(status_payload: Mapping[str, Any]) -> None:
    if not isinstance(status_payload, Mapping):
        actual_type = type(status_payload).__name__
        raise TypeError(
            "assert_status_bio_to_code_coverage.status_payload must be a mapping, "
            f"got {actual_type}."
        )
    matrix = status_payload.get("bio_to_code_matrix")
    if not isinstance(matrix, list):
        raise ValueError("status payload must include bio_to_code_matrix list.")
    required = {
        item.get("skill")
        for item in matrix
        if isinstance(item, Mapping) and isinstance(item.get("skill"), str)
    }
    missing = sorted(required - set(covered_bio_to_code_skills()))
    if missing:
        raise ValueError(
            "V2 guidance inventory does not cover status bio-to-code skills: "
            + ", ".join(missing)
        )


def _render_product_normal_guidance(
    context: ExecutiveGuidanceContext,
    *,
    task_text: str | None,
) -> str:
    decision = build_product_guidance_decision(context, task_text=task_text)
    if (
        decision.posture is ExecutiveInterventionIntent.CONTINUE
        and not decision.directives
        and not decision.prohibitions
        and decision.close_gate is None
    ):
        return ""

    lines = [
        "<cortex_exec>",
        f"  <posture>{decision.posture.value}</posture>",
    ]
    if decision.directives:
        lines.append(f"  <do_now>{' '.join(decision.directives)}</do_now>")
    if decision.prohibitions:
        lines.append(f"  <do_not>{' '.join(decision.prohibitions)}</do_not>")
    if decision.close_gate is not None:
        lines.append(f"  <close_gate>{decision.close_gate}</close_gate>")
    lines.append("</cortex_exec>")
    guidance = "\n".join(lines)
    if len(guidance) > 1200:
        raise ValueError("product_normal guidance exceeded the 1200 character hard cap.")
    return guidance


def _product_posture(
    task_signals: ProductTaskSignals,
    runtime_intent: ExecutiveInterventionIntent,
) -> tuple[ExecutiveInterventionIntent, str]:
    if task_signals.unsupported_broad_claim:
        return ExecutiveInterventionIntent.BRAKE, "task_unsupported_broad_claim"
    if task_signals.repeated_failure:
        return ExecutiveInterventionIntent.BRAKE, "task_repeated_failure"
    if task_signals.missing_context:
        return ExecutiveInterventionIntent.SEEK_CONTEXT, "task_missing_context"
    if task_signals.repair_requested:
        return ExecutiveInterventionIntent.REPAIR, "task_repair"
    if task_signals.closure_pressure:
        return ExecutiveInterventionIntent.CLOSE, "task_closure"
    if task_signals.verification_requested:
        return ExecutiveInterventionIntent.CHECK, "task_verification"
    if task_signals.resume_continuity:
        return ExecutiveInterventionIntent.CHECK, "task_resume_continuity"
    if runtime_intent is not ExecutiveInterventionIntent.CONTINUE:
        return runtime_intent, "runtime_state"
    return ExecutiveInterventionIntent.CONTINUE, "neutral_default"


def _product_directives_for_posture(
    posture: ExecutiveInterventionIntent,
    task_signals: ProductTaskSignals,
) -> tuple[tuple[str, ...], tuple[str, ...], str | None]:
    if posture is ExecutiveInterventionIntent.CONTINUE:
        return (), (), None
    if posture is ExecutiveInterventionIntent.REPAIR:
        return (
            (
                "Preserve verified work; isolate the smallest failing surface; verify before closing.",
            ),
            (
                "Do not rewrite unrelated files or claim completion without evidence.",
            ),
            "Close only with passing verification or an explicit blocker.",
        )
    if posture is ExecutiveInterventionIntent.SEEK_CONTEXT:
        return (
            (
                "Seek the missing bounded context before expanding or editing.",
            ),
            (
                "Do not guess through unavailable facts or smooth uncertainty into confidence.",
            ),
            "Close only after the missing context is resolved or named as a blocker.",
        )
    if posture is ExecutiveInterventionIntent.BRAKE:
        if task_signals.unsupported_broad_claim:
            return (
                (
                    "Reject or narrow unsupported broad claims; state what evidence is missing.",
                ),
                (
                    "Do not claim Cortex is fully proven, perfect, or proven across every host without direct evidence.",
                ),
                "Close only with a bounded claim and explicit remaining evidence gaps.",
            )
        return (
            (
                "Brake the unchanged retry directly; use at most one bounded read only if it can change the stop/probe decision.",
            ),
            (
                "Do not retry unchanged conditions, keep reading after the retry risk is clear, or expand scope to hide the failure.",
            ),
            "Close with the unchanged-condition risk, missing evidence, and one distinct next probe or stop condition.",
        )
    if posture is ExecutiveInterventionIntent.CHECK:
        return (
            (
                "Check the smallest evidence source that can change the next action.",
            ),
            (
                "Do not present an unchecked assumption as verified.",
            ),
            "Close only with verification evidence or an explicit reason verification is unavailable.",
        )
    if posture is ExecutiveInterventionIntent.CLOSE:
        return (
            (
                "Summarize only supported work, verification, blockers, and residual debt.",
            ),
            (
                "Do not say complete, done, or verified unless evidence supports that exact claim.",
            ),
            "Close with verified facts first; name blockers and unverified claims explicitly.",
        )
    raise ValueError(f"unsupported product posture: {posture}")


def _product_model_visible_rows(
    posture: ExecutiveInterventionIntent,
    task_signals: ProductTaskSignals,
) -> tuple[str, ...]:
    if posture is ExecutiveInterventionIntent.CONTINUE:
        return ()
    row_ids: list[str] = ["sre.family_policy"]
    if posture in {ExecutiveInterventionIntent.REPAIR, ExecutiveInterventionIntent.CHECK}:
        row_ids.extend(("core.commitment_certification", "runtime.verified_work_repair"))
    if posture in {
        ExecutiveInterventionIntent.SEEK_CONTEXT,
        ExecutiveInterventionIntent.BRAKE,
    }:
        row_ids.extend(("core.environment_degradation", "sre.uncertainty_brake"))
    if posture is ExecutiveInterventionIntent.CLOSE:
        row_ids.extend(
            (
                "core.commitment_certification",
                "sre.blocker_goal_debt",
                "operational.truth_distinctions",
            )
        )
    if task_signals.resume_continuity:
        row_ids.append("sre.branch_continuity")
    if task_signals.repeated_failure:
        row_ids.append("sre.anti_thrash_probe")
    if task_signals.unsupported_broad_claim:
        row_ids.extend(("operational.truth_distinctions", "negative.forbidden_shortcuts"))
    if task_signals.missing_context or task_signals.closure_pressure:
        row_ids.append("sre.blocker_goal_debt")
    return _dedupe_row_ids(tuple(row_ids))


def _product_kernel_rows(context: ExecutiveGuidanceContext) -> tuple[str, ...]:
    rows = [
        "core.lifecycle_dispatch",
        "core.commitment_certification",
        "core.environment_degradation",
        "sre.intervention_pricing",
        "aux.default_zero_removable",
    ]
    host = context.host_name.lower()
    surface = context.surface.lower()
    if "claude" in host or "claude" in surface:
        rows.append("host.claude_cli")
    if context.offline_publication_active:
        rows.append("aux.publication_only")
    return _dedupe_row_ids(tuple(rows))


def _product_sidecar_rows(context: ExecutiveGuidanceContext) -> tuple[str, ...]:
    rows = [
        "sre.branch_continuity",
        "sre.blocker_goal_debt",
        "sre.anti_thrash_probe",
        "host.codex_cli",
        "host.gemini_reference_conformance",
        "operational.truth_distinctions",
        "negative.forbidden_shortcuts",
        "aux.publication_only",
    ]
    host = context.host_name.lower()
    surface = context.surface.lower()
    if "codex" in host or "openai" in host or "codex" in surface or "openai" in surface:
        rows.append("host.codex_cli")
    return _dedupe_row_ids(tuple(rows))


def _render_compressed_dynamic_guidance(context: ExecutiveGuidanceContext) -> str:
    coverage_by_id = {
        coverage.row_id: coverage
        for coverage in _coverage_for_mode(context, GuidanceMode.COMPRESSED_DYNAMIC)
    }
    rows_by_id = {row.row_id: row for row in V2_EXECUTIVE_GUIDANCE_ROWS}
    active_rows = [
        rows_by_id[coverage.row_id]
        for coverage in coverage_by_id.values()
        if coverage.rendered
    ]
    intent_view = build_intervention_intent_view(context)
    lines = [
        GUIDANCE_MARKER,
        "mode: compressed_dynamic",
        f"host: {context.host_name}",
        f"surface: {context.surface}",
        f"transport_channel: {context.transport_channel}",
        "active_state:",
        f"- track: {context.active_track_ref}",
        f"- pending_goals: {', '.join(context.pending_goal_refs) if context.pending_goal_refs else 'none'}",
        f"- family: {_display(context.last_selected_family)}",
        f"- brake: {_display(context.last_brake_state)}",
        f"- next_move: {_display(context.next_recommended_move)}",
        f"- aux_publication: {'explicit-publication-present' if context.offline_publication_active else 'inactive-default-zero'}",
        "intervention_intent:",
        f"- intent: {intent_view.intent.value}",
        f"- source: {intent_view.source}",
        f"- note: {intent_view.policy_note}",
        "active_rows:",
    ]
    for row in active_rows:
        coverage = coverage_by_id[row.row_id]
        lines.extend(
            [
                f"- row_id: {row.row_id}",
                f"  status: {coverage.status.value}",
                f"  trigger_reason: {coverage.trigger_reason}",
                f"  action: {row.model_guidance}",
            ]
        )
    lines.extend(
        [
            "denominator_rule:",
            "- This is a compressed active packet. The full 17-row denominator is preserved in the coverage artifact; rows omitted here are silent only with an explicit reason.",
            "- Do not use raw AUX memory, extracted Cortex incubation work, one-host evidence, or diagnostics-only output as a completion claim.",
        ]
    )
    return "\n".join(lines)


def _coverage_for_mode(
    context: ExecutiveGuidanceContext,
    mode: GuidanceMode,
    *,
    task_text: str | None = None,
) -> tuple[V2GuidanceCoverage, ...]:
    if mode is GuidanceMode.FULL:
        return tuple(
            V2GuidanceCoverage(
                row_id=row.row_id,
                status=GuidanceCoverageStatus.ALWAYS_ON,
                trigger_reason="full mode renders every denominator row",
                rendered=True,
            )
            for row in V2_EXECUTIVE_GUIDANCE_ROWS
        )
    if mode is GuidanceMode.RAW:
        return tuple(
            V2GuidanceCoverage(
                row_id=row.row_id,
                status=GuidanceCoverageStatus.SILENT_WITH_REASON,
                trigger_reason="raw baseline intentionally carries no Cortex guidance",
                rendered=False,
            )
            for row in V2_EXECUTIVE_GUIDANCE_ROWS
        )
    if mode is GuidanceMode.PRODUCT_NORMAL:
        decision = build_product_guidance_decision(context, task_text=task_text)
        return tuple(
            _product_normal_coverage_for_row(row, context, decision)
            for row in V2_EXECUTIVE_GUIDANCE_ROWS
        )
    return tuple(_compressed_coverage_for_row(row, context) for row in V2_EXECUTIVE_GUIDANCE_ROWS)


def _compressed_coverage_for_row(
    row: V2GuidanceRow,
    context: ExecutiveGuidanceContext,
) -> V2GuidanceCoverage:
    if row.row_id in _ALWAYS_ON_COMPRESSED_ROWS:
        return V2GuidanceCoverage(
            row_id=row.row_id,
            status=GuidanceCoverageStatus.ALWAYS_ON,
            trigger_reason="always-on compressed kernel for truth, uncertainty, AUX default-zero, and overclaim prevention",
            rendered=True,
        )

    dynamic_reason = _dynamic_trigger_reason(row.row_id, context)
    if dynamic_reason is not None:
        return V2GuidanceCoverage(
            row_id=row.row_id,
            status=GuidanceCoverageStatus.DYNAMIC_TRIGGERED,
            trigger_reason=dynamic_reason,
            rendered=True,
        )

    return V2GuidanceCoverage(
        row_id=row.row_id,
        status=GuidanceCoverageStatus.SILENT_WITH_REASON,
        trigger_reason=_silent_reason(row.row_id, context),
        rendered=False,
    )


def _product_normal_coverage_for_row(
    row: V2GuidanceRow,
    context: ExecutiveGuidanceContext,
    decision: ProductGuidanceDecision,
) -> V2GuidanceCoverage:
    if row.row_id in decision.model_visible_row_ids:
        return V2GuidanceCoverage(
            row_id=row.row_id,
            status=GuidanceCoverageStatus.MODEL_VISIBLE_DIRECTIVE,
            trigger_reason=(
                f"product_normal posture {decision.posture.value} compiles this law "
                "into concise Claude-facing instructions"
            ),
            rendered=True,
        )
    if row.row_id in decision.kernel_enforced_row_ids:
        return V2GuidanceCoverage(
            row_id=row.row_id,
            status=GuidanceCoverageStatus.KERNEL_ENFORCED,
            trigger_reason=(
                "product_normal keeps this row enforced by the Cortex kernel or host "
                "routing instead of showing internal row text to the model"
            ),
            rendered=False,
        )
    if row.row_id in decision.sidecar_guardrail_row_ids:
        return V2GuidanceCoverage(
            row_id=row.row_id,
            status=GuidanceCoverageStatus.SIDECAR_GUARDRAIL,
            trigger_reason=(
                "product_normal preserves this row in sidecar denominator evidence "
                "because it is not useful Claude-facing instruction for this turn"
            ),
            rendered=False,
        )
    return V2GuidanceCoverage(
        row_id=row.row_id,
        status=GuidanceCoverageStatus.SILENT_WITH_REASON,
        trigger_reason=_product_normal_silent_reason(row.row_id, context, decision),
        rendered=False,
    )


def _dynamic_trigger_reason(row_id: str, context: ExecutiveGuidanceContext) -> str | None:
    intent = build_intervention_intent_view(context).intent
    cue_text = _context_cue_text(context)
    host = context.host_name.lower()
    surface = context.surface.lower()

    if row_id == "core.lifecycle_dispatch":
        return "current host, surface, and transport must bind the next turn"
    if row_id == "runtime.verified_work_repair" and (
        intent in {ExecutiveInterventionIntent.REPAIR, ExecutiveInterventionIntent.CHECK}
        or _contains_any(cue_text, ("verify", "test", "repair", "failing", "allowed path"))
        or context.active_track_ref.startswith("verified-work:")
    ):
        return "verification or bounded repair cues are active"
    if row_id == "sre.family_policy" and (
        context.last_selected_family is not None
        or context.next_recommended_move is not None
    ):
        return "a selected family or next recommended move must constrain execution"
    if row_id == "sre.uncertainty_brake" and (
        intent in {ExecutiveInterventionIntent.SEEK_CONTEXT, ExecutiveInterventionIntent.BRAKE}
        or _contains_any(cue_text, ("uncertain", "blocked", "missing", "context", "brake", "guarded"))
        or context.last_brake_state not in {None, "neutral", "quiescent"}
    ):
        return "uncertainty, missing context, or brake pressure is active"
    if row_id == "sre.branch_continuity" and (
        context.pending_goal_refs
        or context.active_track_ref != "main"
        or context.event_index > 0
        or _contains_any(cue_text, ("resume", "branch", "pending", "continuity"))
    ):
        return "track, pending-goal, or resume cues are active"
    if row_id == "sre.intervention_pricing":
        return "intervention intent is priced against neutral continuation"
    if row_id == "sre.blocker_goal_debt" and (
        context.pending_goal_refs
        or intent in {
            ExecutiveInterventionIntent.BRAKE,
            ExecutiveInterventionIntent.SEEK_CONTEXT,
            ExecutiveInterventionIntent.CLOSE,
        }
        or _contains_any(cue_text, ("blocked", "debt", "unresolved", "incomplete"))
    ):
        return "blocker, pending-goal, or closure debt cues are active"
    if row_id == "sre.anti_thrash_probe" and _contains_any(
        cue_text,
        ("repeat", "retry", "same failed", "unchanged", "probe", "failure"),
    ):
        return "repeated-failure or probe-truth cues are active"
    if row_id == "host.claude_cli" and ("claude" in host or "claude" in surface):
        return "Claude host surface is active"
    if row_id == "host.codex_cli" and (
        "codex" in host
        or "openai" in host
        or "codex" in surface
        or "openai" in surface
    ):
        return "Codex/OpenAI host surface is active"
    if row_id == "host.gemini_reference_conformance" and (
        "gemini" in host
        or "reference" in host
        or "gemini" in surface
        or "reference" in surface
    ):
        return "Gemini or reference conformance surface is active"
    if row_id == "aux.publication_only" and context.offline_publication_active:
        return "an explicit offline support publication is present"
    return None


def _silent_reason(row_id: str, context: ExecutiveGuidanceContext) -> str:
    if row_id == "runtime.verified_work_repair":
        return "no verification or repair cue is active"
    if row_id == "sre.family_policy":
        return "no selected family or next recommended move is present"
    if row_id == "sre.uncertainty_brake":
        return "uncertainty and brake cues are below the active packet threshold"
    if row_id == "sre.branch_continuity":
        return "main-track continuation has no pending-goal or resume cue"
    if row_id == "sre.blocker_goal_debt":
        return "no blocker, goal debt, or closure cue is active"
    if row_id == "sre.anti_thrash_probe":
        return "no repeated-failure or probe-truth cue is active"
    if row_id == "host.claude_cli":
        return f"current host is {context.host_name}, not Claude"
    if row_id == "host.codex_cli":
        return f"current host is {context.host_name}, not Codex/OpenAI"
    if row_id == "host.gemini_reference_conformance":
        return "Gemini/reference remain conformance truth but are not the active host surface"
    if row_id == "aux.publication_only":
        return "AUX publication is inactive, so default-zero AUX row carries the boundary"
    return "row has no active dynamic trigger in this turn"


def _product_normal_silent_reason(
    row_id: str,
    context: ExecutiveGuidanceContext,
    decision: ProductGuidanceDecision,
) -> str:
    if decision.posture is ExecutiveInterventionIntent.CONTINUE:
        return "neutral product_normal turn: no marginal model-visible guidance is useful"
    if row_id == "host.claude_cli":
        return "Claude host boundary is kernel-enforced when Claude is active; otherwise not the active host"
    if row_id in {"host.codex_cli", "host.gemini_reference_conformance"}:
        return "cross-host conformance truth is preserved outside Claude's normal product prompt"
    if row_id == "aux.publication_only" and not context.offline_publication_active:
        return "no explicit AUX publication is active"
    return "row is covered by product_normal denominator sidecar without model-facing text"


def _missing_coverage_row_ids(coverages: tuple[V2GuidanceCoverage, ...]) -> list[str]:
    covered = {coverage.row_id for coverage in coverages}
    return [row.row_id for row in V2_EXECUTIVE_GUIDANCE_ROWS if row.row_id not in covered]


def _context_cue_text(context: ExecutiveGuidanceContext) -> str:
    return " ".join(
        part.lower()
        for part in (
            context.active_track_ref,
            context.last_selected_family,
            context.last_brake_state,
            context.next_recommended_move,
            context.last_commitment_result_summary,
            " ".join(context.pending_goal_refs),
        )
        if part
    )


def _contains_any(value: str, needles: tuple[str, ...]) -> bool:
    return any(needle in value for needle in needles)


def _dedupe_row_ids(row_ids: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    valid = {row.row_id for row in V2_EXECUTIVE_GUIDANCE_ROWS}
    for row_id in row_ids:
        if row_id in valid and row_id not in seen:
            seen.add(row_id)
            deduped.append(row_id)
    return tuple(deduped)


def _normalized_task_text(task_text: str | None) -> str:
    if task_text is None:
        return ""
    if not isinstance(task_text, str):
        actual_type = type(task_text).__name__
        raise TypeError(f"task_text must be str | None, got {actual_type}.")
    return " ".join(task_text.lower().strip().split())


def _coerce_guidance_mode(value: GuidanceMode | str) -> GuidanceMode:
    if isinstance(value, GuidanceMode):
        return value
    if isinstance(value, str):
        try:
            return GuidanceMode(value)
        except ValueError as exc:
            raise ValueError(f"unsupported guidance mode: {value}") from exc
    actual_type = type(value).__name__
    raise TypeError(f"guidance mode must be GuidanceMode or str, got {actual_type}.")


def _coerce_guidance_profile(value: GuidanceProfile | str) -> GuidanceProfile:
    if isinstance(value, GuidanceProfile):
        return value
    if isinstance(value, str):
        try:
            return GuidanceProfile(value)
        except ValueError as exc:
            raise ValueError(f"unsupported guidance profile: {value}") from exc
    actual_type = type(value).__name__
    raise TypeError(f"guidance profile must be GuidanceProfile or str, got {actual_type}.")


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _safe_track_ref(value: str) -> str:
    if value.startswith("verified-work:"):
        prefix, separator, path_blob = value.rpartition(":")
        if separator and "|" in path_blob:
            path_count = len([entry for entry in path_blob.split("|") if entry])
            return f"{prefix}:{path_count}-paths"
    return value


def _enum_or_string(value: Any) -> str | None:
    if value is None:
        return None
    enum_value = getattr(value, "value", None)
    if isinstance(enum_value, str) and enum_value.strip():
        return enum_value.strip()
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _last_string(values: Any) -> str | None:
    if not values:
        return None
    try:
        value = values[-1]
    except (IndexError, KeyError, TypeError):
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _display(value: str | None) -> str:
    return value if value is not None else "none"


def _has_rendered_guidance_block(value: str) -> bool:
    product_index = value.find("<cortex_exec>")
    if product_index != -1 and value.find("</cortex_exec>", product_index) != -1:
        return True
    marker_index = value.find(GUIDANCE_MARKER)
    if marker_index == -1:
        return False
    contract_index = value.find("\ncontract_rows:", marker_index)
    next_rule_index = value.find("\nnext_turn_rule:", marker_index)
    return contract_index != -1 and next_rule_index != -1


def _required_text(value: str, label: str) -> str:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be str, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming.")
    return stripped


__all__ = [
    "ExecutiveGuidanceContext",
    "ExecutiveInterventionIntent",
    "GUIDANCE_MARKER",
    "GuidanceCoverageStatus",
    "GuidanceMode",
    "GuidanceVisibility",
    "InterventionIntentView",
    "ProductGuidanceDecision",
    "ProductTaskSignals",
    "V2GuidanceCoverage",
    "V2GuidanceRow",
    "V2_EXECUTIVE_GUIDANCE_ROWS",
    "append_guidance_to_channel",
    "assert_status_bio_to_code_coverage",
    "build_intervention_intent_view",
    "build_guidance_context_from_session",
    "build_product_guidance_decision",
    "covered_bio_to_code_skills",
    "extract_product_task_signals",
    "guidance_mode_for_profile",
    "prepend_guidance_to_prompt",
    "render_executive_guidance",
    "v2_guidance_denominator_coverage_payload",
    "v2_guidance_inventory_payload",
]
