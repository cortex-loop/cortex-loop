"""Build deterministic Claude-host mediated branch-discipline comparators."""

from __future__ import annotations

from functools import partial
import sys

from tests.integration._claude_mediation_branch_discipline_episode import (
    CLAUDE_BRANCH_DISCIPLINE_PAIR_KEYS,
    CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS,
    DEFAULT_CLAUDE_BRANCH_DISCIPLINE_PAIR_KEY,
    build_claude_branch_discipline_baseline_packet,
    build_claude_branch_discipline_episode_snapshot,
)
from tests.integration._mediation_branch_discipline_common import (
    build_branch_discipline_packet,
    build_branch_discipline_snapshot,
    render_branch_discipline_packet,
)


def build_claude_mediated_branch_discipline_episode_snapshot(
    pair_key: str = DEFAULT_CLAUDE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_snapshot(
        spec=CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_claude_01",
        variant="experimental_mediated",
        candidate_event_name="content_block_delta",
        publication_event_name="message_stop",
    )


def build_claude_branch_discipline_mediated_packet(
    pair_key: str = DEFAULT_CLAUDE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_packet(
        spec=CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_claude_01",
        host_family="claude",
        variant="experimental_mediated",
        snapshot=build_claude_mediated_branch_discipline_episode_snapshot(pair_key),
    )


CLAUDE_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS = {
    pair_key: CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].mediated_packet_path
    for pair_key in CLAUDE_BRANCH_DISCIPLINE_PAIR_KEYS
}
CLAUDE_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS = {
    CLAUDE_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS[pair_key]: partial(
        build_claude_branch_discipline_mediated_packet, pair_key
    )
    for pair_key in CLAUDE_BRANCH_DISCIPLINE_PAIR_KEYS
}


def emit_claude_mediated_branch_discipline_candidate() -> None:
    for relative_path, builder in CLAUDE_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_branch_discipline_packet(relative_path, builder()))

