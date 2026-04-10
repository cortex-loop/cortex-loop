"""Build deterministic OpenAI-host mediated non-thrash burden comparators."""

from __future__ import annotations

from functools import partial
import sys

from tests.archive.legacy_integration._mediation_non_thrash_burden_common import (
    build_non_thrash_burden_artifact,
    build_non_thrash_burden_packet,
    build_non_thrash_burden_snapshot,
    emit_burden_artifacts,
    render_non_thrash_burden_artifact,
    render_non_thrash_packet,
)
from tests.archive.legacy_integration._openai_mediation_non_thrash_burden_episode import (
    DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY,
    OPENAI_NON_THRASH_BURDEN_PAIR_KEYS,
    OPENAI_NON_THRASH_BURDEN_PAIR_SPECS,
    build_openai_non_thrash_burden_baseline_packet,
    build_openai_non_thrash_burden_episode_snapshot,
)


def build_openai_mediated_non_thrash_burden_episode_snapshot(
    pair_key: str = DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    return build_non_thrash_burden_snapshot(
        spec=OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key],
        scenario_id="scenario_burden_openai_01",
        variant="experimental_mediated",
        observation_event_name="response.output_text.delta",
        check_event_name="response.output_text.delta",
        publication_event_name="response.completed",
    )


def build_openai_non_thrash_burden_mediated_packet(
    pair_key: str = DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    return build_non_thrash_burden_packet(
        spec=spec,
        scenario_id="scenario_burden_openai_01",
        host_family="openai",
        variant="experimental_mediated",
        snapshot=build_openai_mediated_non_thrash_burden_episode_snapshot(pair_key),
        burden_ref=spec.mediated_burden_path,
    )


def build_openai_non_thrash_burden_mediated_artifact(
    pair_key: str = DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    snapshot = build_openai_mediated_non_thrash_burden_episode_snapshot(pair_key)
    return build_non_thrash_burden_artifact(
        scenario_id="scenario_burden_openai_01",
        pair_id=spec.pair_id,
        pair_key=pair_key,
        run_id=spec.mediated_run_id,
        variant="experimental_mediated",
        host_family="openai",
        interaction_sequence=list(snapshot["interaction_sequence"]),
    )


OPENAI_NON_THRASH_BURDEN_MEDIATED_PACKET_PATHS = {
    pair_key: OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].mediated_packet_path
    for pair_key in OPENAI_NON_THRASH_BURDEN_PAIR_KEYS
}
OPENAI_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS = {
    OPENAI_NON_THRASH_BURDEN_MEDIATED_PACKET_PATHS[pair_key]: partial(
        build_openai_non_thrash_burden_mediated_packet, pair_key
    )
    for pair_key in OPENAI_NON_THRASH_BURDEN_PAIR_KEYS
}
OPENAI_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS = {
    OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].mediated_burden_path: partial(
        build_openai_non_thrash_burden_mediated_artifact, pair_key
    )
    for pair_key in OPENAI_NON_THRASH_BURDEN_PAIR_KEYS
}


def emit_openai_mediated_non_thrash_burden_candidate() -> None:
    for relative_path, builder in OPENAI_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_non_thrash_packet(relative_path, builder()))
        sys.stdout.write("\n")
    emit_burden_artifacts(
        OPENAI_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS,
        renderer=lambda relative_path, artifact: render_non_thrash_burden_artifact(
            relative_path,
            artifact,
            scope_text=(
                "This committed AUX burden artifact records one OpenAI-host experimental "
                "mediated non-thrash burden measurement within the committed OpenAI "
                "non-thrash paired-run series for mediation evidence review.\n"
                "It does not justify mediation, authorize implementation work, or imply "
                "generic runtime burden beyond the visible intervention count recorded here."
            ),
        ),
    )

