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
            "Never treat diagnostics-only output, one file, one host, v3 successor work, "
            "or final-message assertions as full V2 communication proof."
        ),
        reason="The current closure risk is mistaking calculated state for communicated guidance.",
    ),
)


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


def render_executive_guidance(context: ExecutiveGuidanceContext) -> str:
    if not isinstance(context, ExecutiveGuidanceContext):
        actual_type = type(context).__name__
        raise TypeError(
            "render_executive_guidance.context must be ExecutiveGuidanceContext, "
            f"got {actual_type}."
        )
    lines = [
        GUIDANCE_MARKER,
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


def prepend_guidance_to_prompt(prompt: str, context: ExecutiveGuidanceContext) -> str:
    prompt_text = _required_text(prompt, "prompt")
    guidance = render_executive_guidance(context)
    if _has_rendered_guidance_block(prompt_text):
        return prompt_text
    return f"{guidance}\n\nUSER_TASK\n{prompt_text}"


def append_guidance_to_channel(
    existing_text: str | None,
    context: ExecutiveGuidanceContext,
) -> str:
    guidance = render_executive_guidance(context)
    if existing_text is not None:
        base = _required_text(existing_text, "existing_text")
        if _has_rendered_guidance_block(base):
            return base
        return f"{base.rstrip()}\n\n{guidance}"
    return guidance


def v2_guidance_inventory_payload() -> list[dict[str, Any]]:
    return [row.as_payload() for row in V2_EXECUTIVE_GUIDANCE_ROWS]


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
    "GUIDANCE_MARKER",
    "GuidanceVisibility",
    "V2GuidanceRow",
    "V2_EXECUTIVE_GUIDANCE_ROWS",
    "append_guidance_to_channel",
    "assert_status_bio_to_code_coverage",
    "build_guidance_context_from_session",
    "covered_bio_to_code_skills",
    "prepend_guidance_to_prompt",
    "render_executive_guidance",
    "v2_guidance_inventory_payload",
]
