"""Build deterministic Claude-host mediated non-thrash burden comparators."""

from __future__ import annotations

from functools import partial
import sys

from tests.archive.legacy_integration._claude_mediation_non_thrash_burden_episode import (
    CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS,
    CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS,
    DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY,
    build_claude_non_thrash_burden_baseline_packet,
    build_claude_non_thrash_burden_episode_snapshot,
)
from tests.archive.legacy_integration._mediation_non_thrash_burden_common import (
    build_non_thrash_burden_artifact,
    build_non_thrash_burden_packet,
    build_non_thrash_burden_snapshot,
    emit_burden_artifacts,
    render_non_thrash_burden_artifact,
    render_non_thrash_packet,
)


def build_claude_mediated_non_thrash_burden_episode_snapshot(
    pair_key: str = DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    return build_non_thrash_burden_snapshot(
        spec=CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key],
        scenario_id="scenario_burden_claude_01",
        variant="experimental_mediated",
        observation_event_name="content_block_delta",
        check_event_name="content_block_delta",
        publication_event_name="message_stop",
    )


def build_claude_non_thrash_burden_mediated_packet(
    pair_key: str = DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    return build_non_thrash_burden_packet(
        spec=spec,
        scenario_id="scenario_burden_claude_01",
        host_family="claude",
        variant="experimental_mediated",
        snapshot=build_claude_mediated_non_thrash_burden_episode_snapshot(pair_key),
        burden_ref=spec.mediated_burden_path,
    )


def build_claude_non_thrash_burden_mediated_artifact(
    pair_key: str = DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    snapshot = build_claude_mediated_non_thrash_burden_episode_snapshot(pair_key)
    return build_non_thrash_burden_artifact(
        scenario_id="scenario_burden_claude_01",
        pair_id=spec.pair_id,
        pair_key=pair_key,
        run_id=spec.mediated_run_id,
        variant="experimental_mediated",
        host_family="claude",
        interaction_sequence=list(snapshot["interaction_sequence"]),
    )


CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_PATHS = {
    pair_key: CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].mediated_packet_path
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS
}
CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS = {
    CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_PATHS[pair_key]: partial(
        build_claude_non_thrash_burden_mediated_packet, pair_key
    )
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS
}
CLAUDE_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS = {
    CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].mediated_burden_path: partial(
        build_claude_non_thrash_burden_mediated_artifact, pair_key
    )
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS
}


def emit_claude_mediated_non_thrash_burden_candidate() -> None:
    for relative_path, builder in CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_non_thrash_packet(relative_path, builder()))
        sys.stdout.write("\n")
    emit_burden_artifacts(
        CLAUDE_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS,
        renderer=lambda relative_path, artifact: render_non_thrash_burden_artifact(
            relative_path,
            artifact,
            scope_text=(
                "This committed AUX burden artifact records one Claude-host experimental "
                "mediated non-thrash burden measurement within the committed Claude "
                "non-thrash paired-run series for mediation evidence review.\n"
                "It does not justify mediation, authorize implementation work, or imply "
                "generic runtime burden beyond the visible intervention count recorded here."
            ),
        ),
    )

