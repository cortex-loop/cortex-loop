"""Generated Cortex orientation capsule helpers."""

from __future__ import annotations

from typing import Any


MAX_ORIENTATION_WORDS = 500


def render_orientation_capsule(data: dict[str, Any]) -> str:
    """Render the compact, non-authoritative Cortex orientation capsule."""

    work_today = data.get("work_today", {})
    next_train = data.get("next_product_train", {})
    conformance = data.get("conformance_summary", {})
    matrix = data.get("bio_to_code_matrix", [])
    skills = "; ".join(str(entry.get("skill", "")).strip() for entry in matrix)
    current_slug = _slug_display(work_today.get("slug"))
    next_slug = _slug_display(next_train.get("slug"))
    shipping_default = conformance.get("shipping_default", "unknown")

    lines = [
        "## Cortex Orientation Capsule",
        "",
        "_Generated orientation only; authority remains scoped to `docs/CORTEX.md`, "
        "the V2 packet docs, `internal/truth/cortex_status.json`, and code/proof surfaces._",
        "",
        (
            "Cortex is a post-training runtime executive-function layer around "
            "models and CLI hosts. It is not a plugin, translation layer, monitor, "
            "middleware pile, or post-training replacement."
        ),
        "",
        (
            "Target loop: model/host event -> task-state and executive-risk "
            "understanding -> intervention decision -> control mode -> better "
            "next model behavior. Valid control modes include silence, route, "
            "degrade, block, preserve, recheck, ask, or grounded visible "
            "intervention when a model-integrable anchor exists."
        ),
        "",
        f"Capability families: {skills}.",
        "",
        (
            "Subsystem boundaries: Core owns commitment/provenance/dispatch truth; "
            "SRE owns route, brake, expectation debt, goal debt, continuity, and "
            "policy pressure; AUX owns removable publication-only support priors; "
            "host adapters consume Core/SRE decisions in host-native I/O; lab, "
            "eval, recon, archive, and workflow surfaces prove or preserve evidence "
            "but are not product identity."
        ),
        "",
        (
            "Grounding rule: any product claim, plan, or implementation seam must "
            "name identity/current truth, a code owner, a proof surface, and the "
            "model-I/O path. If the relevant code was not read, say so before "
            "taking a position."
        ),
        "",
        (
            f"Current train: `{current_slug}`. Next train: `{next_slug}`. "
            f"Shipping default: `{shipping_default}`. Keep Cortex truth, "
            "brain-wiring truth, conformance truth, shipping truth, and live "
            "behavior-lift claims separate; structural proof alone does not earn "
            "model-output lift."
        ),
    ]
    capsule = "\n".join(lines)
    words = _word_count(capsule)
    if words > MAX_ORIENTATION_WORDS:
        raise ValueError(
            f"Cortex orientation capsule is {words} words; "
            f"maximum is {MAX_ORIENTATION_WORDS}."
        )
    return capsule


def _slug_display(value: object) -> str:
    if value is None:
        return "none queued yet"
    return str(value)


def _word_count(text: str) -> int:
    return len([part for part in text.replace("`", "").split() if part.strip()])


__all__ = ["MAX_ORIENTATION_WORDS", "render_orientation_capsule"]
