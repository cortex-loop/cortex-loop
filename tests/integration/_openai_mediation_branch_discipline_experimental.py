"""Build deterministic OpenAI-host mediated branch-discipline comparators."""

from __future__ import annotations

from functools import partial
import sys

from tests.integration._mediation_branch_discipline_common import (
    build_branch_discipline_packet,
    build_branch_discipline_snapshot,
    render_branch_discipline_packet,
)
from tests.integration._openai_mediation_branch_discipline_episode import (
    DEFAULT_OPENAI_BRANCH_DISCIPLINE_PAIR_KEY,
    OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS,
    OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS,
    build_openai_branch_discipline_baseline_packet,
    build_openai_branch_discipline_episode_snapshot,
)


def build_openai_mediated_branch_discipline_episode_snapshot(
    pair_key: str = DEFAULT_OPENAI_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_snapshot(
        spec=OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_openai_01",
        variant="experimental_mediated",
        candidate_event_name="response.output_text.delta",
        publication_event_name="response.completed",
    )


def build_openai_branch_discipline_mediated_packet(
    pair_key: str = DEFAULT_OPENAI_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_packet(
        spec=OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_openai_01",
        host_family="openai",
        variant="experimental_mediated",
        snapshot=build_openai_mediated_branch_discipline_episode_snapshot(pair_key),
    )


OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS = {
    pair_key: OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].mediated_packet_path
    for pair_key in OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS
}
OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS = {
    OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS[pair_key]: partial(
        build_openai_branch_discipline_mediated_packet, pair_key
    )
    for pair_key in OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS
}


def emit_openai_mediated_branch_discipline_candidate() -> None:
    for relative_path, builder in OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_branch_discipline_packet(relative_path, builder()))

