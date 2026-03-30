"""Build deterministic reference-host mediated branch-discipline comparators."""

from __future__ import annotations

from functools import partial
import sys

from tests.integration._mediation_branch_discipline_common import (
    build_branch_discipline_packet,
    build_branch_discipline_snapshot,
    render_branch_discipline_packet,
)
from tests.integration._reference_mediation_branch_discipline_episode import (
    DEFAULT_REFERENCE_BRANCH_DISCIPLINE_PAIR_KEY,
    REFERENCE_BRANCH_DISCIPLINE_PAIR_KEYS,
    REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS,
    build_reference_branch_discipline_baseline_packet,
    build_reference_branch_discipline_episode_snapshot,
)


def build_reference_mediated_branch_discipline_episode_snapshot(
    pair_key: str = DEFAULT_REFERENCE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_snapshot(
        spec=REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_reference_01",
        variant="experimental_mediated",
        candidate_event_name="ApprovalRequest",
        publication_event_name="ApprovalResult",
    )


def build_reference_branch_discipline_mediated_packet(
    pair_key: str = DEFAULT_REFERENCE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_packet(
        spec=REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_reference_01",
        host_family="reference",
        variant="experimental_mediated",
        snapshot=build_reference_mediated_branch_discipline_episode_snapshot(pair_key),
    )


REFERENCE_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS = {
    pair_key: REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].mediated_packet_path
    for pair_key in REFERENCE_BRANCH_DISCIPLINE_PAIR_KEYS
}
REFERENCE_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS = {
    REFERENCE_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS[pair_key]: partial(
        build_reference_branch_discipline_mediated_packet, pair_key
    )
    for pair_key in REFERENCE_BRANCH_DISCIPLINE_PAIR_KEYS
}


def emit_reference_mediated_branch_discipline_candidate() -> None:
    for relative_path, builder in REFERENCE_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_branch_discipline_packet(relative_path, builder()))

