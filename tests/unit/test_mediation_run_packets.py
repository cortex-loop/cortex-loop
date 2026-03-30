"""Mechanical checks for committed mediation run packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    CLAUDE_BASELINE_INDEX_PATH,
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_THRASH_BASELINE_BURDEN_PATHS,
    GEMINI_THRASH_BASELINE_PACKET_PATHS,
    GEMINI_THRASH_MEDIATED_BURDEN_PATHS,
    GEMINI_THRASH_MEDIATED_PACKET_PATHS,
    MEDIATION_CLAUDE_PACKET_ROOT,
    MEDIATION_GEMINI_PACKET_ROOT,
    MEDIATION_OPENAI_PACKET_ROOT,
    MEDIATION_REFERENCE_PACKET_ROOT,
    OPENAI_BASELINE_INDEX_PATH,
    OPENAI_THRASH_BASELINE_BURDEN_PATHS,
    OPENAI_THRASH_BASELINE_PACKET_PATHS,
    OPENAI_THRASH_MEDIATED_BURDEN_PATHS,
    OPENAI_THRASH_MEDIATED_PACKET_PATHS,
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_THRASH_BASELINE_BURDEN_PATHS,
    REFERENCE_THRASH_BASELINE_PACKET_PATHS,
    REFERENCE_THRASH_MEDIATED_BURDEN_PATHS,
    REFERENCE_THRASH_MEDIATED_PACKET_PATHS,
    REPO_ROOT,
    RUN_PACKET_INVARIANT_FIELDS,
    VERDICTS,
    all_tags_allowed,
    load_failure_tags,
    load_scenarios,
    parse_aux_burden_artifact,
    parse_markdown_table,
    parse_run_packet,
    read,
    section,
    status,
)

PAIR_KEYS = ("001", "002", "003")

HOST_PACKET_ROOTS = {
    "reference": MEDIATION_REFERENCE_PACKET_ROOT,
    "openai": MEDIATION_OPENAI_PACKET_ROOT,
    "claude": MEDIATION_CLAUDE_PACKET_ROOT,
    "gemini": MEDIATION_GEMINI_PACKET_ROOT,
}

HOST_SCENARIO_IDS = {
    "reference": (
        "scenario_branch_reference_01",
        "scenario_burden_reference_01",
        "scenario_host_reference_01",
        "scenario_thrash_reference_01",
        "scenario_uncertainty_reference_01",
    ),
    "openai": (
        "scenario_branch_openai_01",
        "scenario_burden_openai_01",
        "scenario_host_openai_01",
        "scenario_thrash_openai_01",
        "scenario_uncertainty_openai_01",
    ),
    "claude": (
        "scenario_branch_claude_01",
        "scenario_burden_claude_01",
        "scenario_host_claude_01",
    ),
    "gemini": (
        "scenario_host_gemini_01",
        "scenario_thrash_gemini_01",
        "scenario_uncertainty_gemini_01",
    ),
}

HOST_BASELINE_INDEXES = {
    "reference": REFERENCE_BASELINE_INDEX_PATH,
    "openai": OPENAI_BASELINE_INDEX_PATH,
    "claude": CLAUDE_BASELINE_INDEX_PATH,
    "gemini": GEMINI_BASELINE_INDEX_PATH,
}

HOST_BASELINE_INDEX_STATUSES = {
    "reference": "reference mediation baseline run index (`active`, baseline-only)",
    "openai": "openai mediation baseline run index (`active`, baseline-only)",
    "claude": "claude mediation baseline run index (active, baseline-only)",
    "gemini": "gemini mediation baseline run index (`active`, baseline-only)",
}

HOST_BASELINE_INDEX_SCENARIOS = {
    "reference": {
        "scenario_uncertainty_reference_01",
        "scenario_host_reference_01",
        "scenario_thrash_reference_01",
    },
    "openai": {
        "scenario_host_openai_01",
        "scenario_thrash_openai_01",
        "scenario_uncertainty_openai_01",
    },
    "claude": {"scenario_host_claude_01"},
    "gemini": {
        "scenario_host_gemini_01",
        "scenario_thrash_gemini_01",
        "scenario_uncertainty_gemini_01",
    },
}

HOST_BURDEN_SCENARIO_IDS = {
    "reference": ("scenario_burden_reference_01", "scenario_thrash_reference_01"),
    "openai": ("scenario_burden_openai_01", "scenario_thrash_openai_01"),
    "claude": ("scenario_burden_claude_01",),
    "gemini": ("scenario_thrash_gemini_01",),
}


def _scenario_kind(scenario_id: str) -> str:
    for kind in ("branch", "burden", "host", "thrash", "uncertainty"):
        if scenario_id.startswith(f"scenario_{kind}_"):
            return kind
    raise AssertionError(f"unexpected scenario id: {scenario_id}")


def _expected_run_prefix(host: str, scenario_kind: str, variant: str) -> str:
    suffix = "baseline_run_" if variant == "baseline_non_mediated" else "mediated_run_"
    if scenario_kind == "host":
        return f"{host}_host_realization_{suffix}"
    return f"{host}_{scenario_kind}_{suffix}"


def _expected_pair_prefix(host: str, scenario_kind: str) -> str:
    return f"pair_{host}_{scenario_kind}_"


def _expected_packet_names(host: str) -> list[str]:
    return sorted(
        f"{scenario_id}__{variant}__run_{pair_key}.md"
        for scenario_id in HOST_SCENARIO_IDS[host]
        for variant in ("baseline_non_mediated", "experimental_mediated")
        for pair_key in PAIR_KEYS
    )


def _expected_aux_burden_names(host: str) -> list[str]:
    return sorted(
        f"{scenario_id}__{variant}__run_{pair_key}__aux_burden.md"
        for scenario_id in HOST_BURDEN_SCENARIO_IDS[host]
        for variant in ("baseline_non_mediated", "experimental_mediated")
        for pair_key in PAIR_KEYS
    )


def _host_packet_names(host: str) -> list[str]:
    return sorted(
        path.name
        for path in HOST_PACKET_ROOTS[host].glob("*.md")
        if "__aux_burden" not in path.name
    )


def _host_aux_burden_names(host: str) -> list[str]:
    return sorted(path.name for path in HOST_PACKET_ROOTS[host].glob("*__aux_burden.md"))


def _host_note_token(host: str) -> str:
    return {
        "reference": "reference-only",
        "openai": "OpenAI-only",
        "claude": "Claude-only",
        "gemini": "Gemini-only",
    }[host]


def _assert_baseline_index(host: str) -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    index_path = HOST_BASELINE_INDEXES[host]
    rows = parse_markdown_table(section(read(index_path), "Index Rows"))

    assert index_path.is_file()
    assert status(index_path) == HOST_BASELINE_INDEX_STATUSES[host]
    assert len(rows) == len(HOST_BASELINE_INDEX_SCENARIOS[host])
    assert {row["scenario_id"] for row in rows} == HOST_BASELINE_INDEX_SCENARIOS[host]

    for row in rows:
        assert row["host_family"] == host
        assert row["variant"] == "baseline_non_mediated"
        assert row["scenario_id"] in scenarios
        assert scenarios[row["scenario_id"]]["host_family"] == host
        assert all_tags_allowed(row["failure_tags"], failure_tags)
        assert row["failure_tags"] == "none"
        assert row["evidence_status"] == "baseline_packet_committed"
        packet_path = Path(row["packet_path"])
        assert packet_path.parts[:3] == ("docs", "mediation_evidence", host)
        assert (REPO_ROOT / packet_path).is_file()


def _assert_packet_metadata(packet_path: Path, host: str, variant: str) -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    packet = parse_run_packet(packet_path)
    scenario_id = packet["header"]["scenario_id"]
    scenario = scenarios[scenario_id]
    scenario_kind = _scenario_kind(scenario_id)

    assert packet["status"] == "reviewed_evidence"
    assert packet["variant_metadata"]["variant"] == variant
    assert packet["variant_metadata"]["host_family"] == host
    assert packet["variant_metadata"]["scenario_family"] == scenario["scenario_family"]
    assert packet["variant_metadata"]["task_value_rubric_id"] == scenario["task_value_rubric_id"]
    assert (
        packet["variant_metadata"]["approval_or_environment_context_id"]
        == scenario["approval_or_environment_context_id"]
    )
    assert packet["header"]["run_id"].startswith(_expected_run_prefix(host, scenario_kind, variant))
    assert packet["header"]["paired_episode_set_id"].startswith(_expected_pair_prefix(host, scenario_kind))

    expected_aux_ref = "none"
    if scenario_kind in {"burden", "thrash"}:
        expected_aux_ref = str(
            packet_path.relative_to(REPO_ROOT).with_name(
                packet_path.name.replace(".md", "__aux_burden.md")
            )
        )
    assert packet["artifact_refs"]["aux_burden_refs_if_present"] == expected_aux_ref

    for field_name in RUN_PACKET_INVARIANT_FIELDS:
        assert packet["invariant_lock"][field_name] == "yes"

    for axis_payload in packet["lift_axes"].values():
        assert axis_payload["verdict"] in VERDICTS
        assert axis_payload["verdict"] == "insufficient"

    assert packet["exclusions"]["exclusion_status"] == "none"
    assert all_tags_allowed(packet["exclusions"]["failure_tags"], failure_tags)
    assert packet["exclusions"]["failure_tags"] == "none"

    reviewer_note = packet["reviewer_note"]["reviewer_note"]
    assert "does not justify mediation" in reviewer_note
    if scenario_kind == "branch":
        assert "committed branch-discipline evidence only" in reviewer_note
        assert "package-level evidence notes govern verdicts" in reviewer_note
    elif scenario_kind == "burden":
        assert "committed non-thrash burden evidence only" in reviewer_note
        assert "package-level evidence notes govern verdicts" in reviewer_note
    elif variant == "baseline_non_mediated":
        assert "baseline-only committed evidence" in reviewer_note
        assert "not comparative mediation evidence" in reviewer_note
    else:
        assert "experimental mediated evidence only" in reviewer_note
        assert _host_note_token(host) in reviewer_note
        assert "package-level evidence notes govern any verdict" in reviewer_note


def _assert_host_packets(host: str, variant: str) -> None:
    packet_root = HOST_PACKET_ROOTS[host]
    packets = sorted(
        path
        for path in packet_root.glob(f"*__{variant}__run_*.md")
        if "__aux_burden" not in path.name
    )

    assert len(packets) == len(HOST_SCENARIO_IDS[host]) * len(PAIR_KEYS)
    assert {parse_run_packet(path)["header"]["scenario_id"] for path in packets} == set(
        HOST_SCENARIO_IDS[host]
    )

    for packet_path in packets:
        _assert_packet_metadata(packet_path, host, variant)


def _assert_burden_packet_sync(
    baseline_packet_paths: dict[str, Path],
    mediated_packet_paths: dict[str, Path],
    baseline_burden_paths: dict[str, Path],
    mediated_burden_paths: dict[str, Path],
    baseline_burden_value: str,
    mediated_burden_value: str,
    baseline_sequence_key: str,
    baseline_sequence_value: str,
    mediated_sequence_key: str,
    mediated_sequence_value: str,
) -> None:
    for pair_key in PAIR_KEYS:
        baseline_packet = parse_run_packet(baseline_packet_paths[pair_key])
        mediated_packet = parse_run_packet(mediated_packet_paths[pair_key])
        baseline_burden = parse_aux_burden_artifact(baseline_burden_paths[pair_key])
        mediated_burden = parse_aux_burden_artifact(mediated_burden_paths[pair_key])

        assert baseline_packet["artifact_refs"]["aux_burden_refs_if_present"] == str(
            baseline_burden_paths[pair_key].relative_to(REPO_ROOT)
        )
        assert mediated_packet["artifact_refs"]["aux_burden_refs_if_present"] == str(
            mediated_burden_paths[pair_key].relative_to(REPO_ROOT)
        )
        assert baseline_burden["status"] == "reviewed_evidence"
        assert mediated_burden["status"] == "reviewed_evidence"
        assert baseline_burden["header"]["scenario_id"] == baseline_packet["header"]["scenario_id"]
        assert mediated_burden["header"]["scenario_id"] == mediated_packet["header"]["scenario_id"]
        assert baseline_burden["header"]["run_id"] == baseline_packet["header"]["run_id"]
        assert mediated_burden["header"]["run_id"] == mediated_packet["header"]["run_id"]
        assert baseline_burden["header"]["paired_episode_set_id"] == baseline_packet["header"][
            "paired_episode_set_id"
        ]
        assert mediated_burden["header"]["paired_episode_set_id"] == mediated_packet["header"][
            "paired_episode_set_id"
        ]
        assert (
            baseline_burden["aux_burden_report"]["intervention_burden"] == baseline_burden_value
        )
        assert (
            mediated_burden["aux_burden_report"]["intervention_burden"] == mediated_burden_value
        )
        assert baseline_burden["derivation"][baseline_sequence_key] == baseline_sequence_value
        assert mediated_burden["derivation"][mediated_sequence_key] == mediated_sequence_value


def _non_thrash_burden_packet_paths(host: str, variant: str) -> dict[str, Path]:
    return {
        pair_key: (
            HOST_PACKET_ROOTS[host]
            / f"scenario_burden_{host}_01__{variant}__run_{pair_key}.md"
        )
        for pair_key in PAIR_KEYS
    }


def _non_thrash_burden_aux_paths(host: str, variant: str) -> dict[str, Path]:
    return {
        pair_key: (
            HOST_PACKET_ROOTS[host]
            / f"scenario_burden_{host}_01__{variant}__run_{pair_key}__aux_burden.md"
        )
        for pair_key in PAIR_KEYS
    }


def test_reference_baseline_index_is_reference_only_and_commits_reference_anchors() -> None:
    _assert_baseline_index("reference")


def test_openai_baseline_index_is_openai_only_and_commits_openai_anchors() -> None:
    _assert_baseline_index("openai")


def test_claude_baseline_index_is_claude_only_and_commits_claude_anchor() -> None:
    _assert_baseline_index("claude")


def test_gemini_baseline_index_is_gemini_only_and_commits_gemini_anchors() -> None:
    _assert_baseline_index("gemini")


def test_committed_reference_baseline_packets_match_catalog_and_stay_baseline_only() -> None:
    _assert_host_packets("reference", "baseline_non_mediated")


def test_experimental_reference_packets_match_catalog_and_stay_experimental() -> None:
    _assert_host_packets("reference", "experimental_mediated")


def test_committed_openai_baseline_packets_match_catalog_and_stay_baseline_only() -> None:
    _assert_host_packets("openai", "baseline_non_mediated")


def test_experimental_openai_packets_match_catalog_and_stay_experimental() -> None:
    _assert_host_packets("openai", "experimental_mediated")


def test_committed_claude_baseline_packets_match_catalog_and_stay_baseline_only() -> None:
    _assert_host_packets("claude", "baseline_non_mediated")


def test_experimental_claude_packets_match_catalog_and_stay_experimental() -> None:
    _assert_host_packets("claude", "experimental_mediated")


def test_committed_gemini_baseline_packets_match_catalog_and_stay_baseline_only() -> None:
    _assert_host_packets("gemini", "baseline_non_mediated")


def test_experimental_gemini_packets_match_catalog_and_stay_experimental() -> None:
    _assert_host_packets("gemini", "experimental_mediated")


def test_reference_packet_directory_contains_expected_j2_packets() -> None:
    assert _host_packet_names("reference") == _expected_packet_names("reference")


def test_reference_packet_directory_contains_expected_burden_artifacts() -> None:
    assert _host_aux_burden_names("reference") == _expected_aux_burden_names("reference")


def test_openai_packet_directory_contains_expected_j2_packets() -> None:
    assert _host_packet_names("openai") == _expected_packet_names("openai")


def test_openai_packet_directory_contains_expected_burden_artifacts() -> None:
    assert _host_aux_burden_names("openai") == _expected_aux_burden_names("openai")


def test_claude_packet_directory_contains_expected_j2_packets() -> None:
    assert _host_packet_names("claude") == _expected_packet_names("claude")


def test_claude_packet_directory_contains_expected_burden_artifacts() -> None:
    assert _host_aux_burden_names("claude") == _expected_aux_burden_names("claude")


def test_gemini_packet_directory_contains_expected_packets() -> None:
    assert _host_packet_names("gemini") == _expected_packet_names("gemini")


def test_gemini_packet_directory_contains_expected_burden_artifacts() -> None:
    assert _host_aux_burden_names("gemini") == _expected_aux_burden_names("gemini")


def test_reference_thrash_packets_and_aux_burden_artifacts_stay_in_sync() -> None:
    _assert_burden_packet_sync(
        baseline_packet_paths=REFERENCE_THRASH_BASELINE_PACKET_PATHS,
        mediated_packet_paths=REFERENCE_THRASH_MEDIATED_PACKET_PATHS,
        baseline_burden_paths=REFERENCE_THRASH_BASELINE_BURDEN_PATHS,
        mediated_burden_paths=REFERENCE_THRASH_MEDIATED_BURDEN_PATHS,
        baseline_burden_value="4.0",
        mediated_burden_value="3.0",
        baseline_sequence_key="branch_sequence",
        baseline_sequence_value="open -> suspend -> resume -> merge",
        mediated_sequence_key="branch_sequence",
        mediated_sequence_value="open -> suspend -> merge",
    )


def test_openai_thrash_packets_and_aux_burden_artifacts_stay_in_sync() -> None:
    _assert_burden_packet_sync(
        baseline_packet_paths=OPENAI_THRASH_BASELINE_PACKET_PATHS,
        mediated_packet_paths=OPENAI_THRASH_MEDIATED_PACKET_PATHS,
        baseline_burden_paths=OPENAI_THRASH_BASELINE_BURDEN_PATHS,
        mediated_burden_paths=OPENAI_THRASH_MEDIATED_BURDEN_PATHS,
        baseline_burden_value="4.0",
        mediated_burden_value="3.0",
        baseline_sequence_key="branch_sequence",
        baseline_sequence_value="open -> suspend -> resume -> merge",
        mediated_sequence_key="branch_sequence",
        mediated_sequence_value="open -> suspend -> merge",
    )


def test_gemini_thrash_packets_and_aux_burden_artifacts_stay_in_sync() -> None:
    _assert_burden_packet_sync(
        baseline_packet_paths=GEMINI_THRASH_BASELINE_PACKET_PATHS,
        mediated_packet_paths=GEMINI_THRASH_MEDIATED_PACKET_PATHS,
        baseline_burden_paths=GEMINI_THRASH_BASELINE_BURDEN_PATHS,
        mediated_burden_paths=GEMINI_THRASH_MEDIATED_BURDEN_PATHS,
        baseline_burden_value="4.0",
        mediated_burden_value="3.0",
        baseline_sequence_key="branch_sequence",
        baseline_sequence_value="open -> suspend -> resume -> merge",
        mediated_sequence_key="branch_sequence",
        mediated_sequence_value="open -> suspend -> merge",
    )


def test_reference_non_thrash_burden_packets_and_aux_burden_artifacts_stay_in_sync() -> None:
    _assert_burden_packet_sync(
        baseline_packet_paths=_non_thrash_burden_packet_paths("reference", "baseline_non_mediated"),
        mediated_packet_paths=_non_thrash_burden_packet_paths("reference", "experimental_mediated"),
        baseline_burden_paths=_non_thrash_burden_aux_paths("reference", "baseline_non_mediated"),
        mediated_burden_paths=_non_thrash_burden_aux_paths("reference", "experimental_mediated"),
        baseline_burden_value="3.0",
        mediated_burden_value="2.0",
        baseline_sequence_key="interaction_sequence",
        baseline_sequence_value="observe -> check -> resolve",
        mediated_sequence_key="interaction_sequence",
        mediated_sequence_value="observe -> resolve",
    )


def test_openai_non_thrash_burden_packets_and_aux_burden_artifacts_stay_in_sync() -> None:
    _assert_burden_packet_sync(
        baseline_packet_paths=_non_thrash_burden_packet_paths("openai", "baseline_non_mediated"),
        mediated_packet_paths=_non_thrash_burden_packet_paths("openai", "experimental_mediated"),
        baseline_burden_paths=_non_thrash_burden_aux_paths("openai", "baseline_non_mediated"),
        mediated_burden_paths=_non_thrash_burden_aux_paths("openai", "experimental_mediated"),
        baseline_burden_value="3.0",
        mediated_burden_value="2.0",
        baseline_sequence_key="interaction_sequence",
        baseline_sequence_value="observe -> check -> resolve",
        mediated_sequence_key="interaction_sequence",
        mediated_sequence_value="observe -> resolve",
    )


def test_claude_non_thrash_burden_packets_and_aux_burden_artifacts_stay_in_sync() -> None:
    _assert_burden_packet_sync(
        baseline_packet_paths=_non_thrash_burden_packet_paths("claude", "baseline_non_mediated"),
        mediated_packet_paths=_non_thrash_burden_packet_paths("claude", "experimental_mediated"),
        baseline_burden_paths=_non_thrash_burden_aux_paths("claude", "baseline_non_mediated"),
        mediated_burden_paths=_non_thrash_burden_aux_paths("claude", "experimental_mediated"),
        baseline_burden_value="3.0",
        mediated_burden_value="2.0",
        baseline_sequence_key="interaction_sequence",
        baseline_sequence_value="observe -> check -> resolve",
        mediated_sequence_key="interaction_sequence",
        mediated_sequence_value="observe -> resolve",
    )
