"""Mechanical drift checks for the active shipping truth and Cortex-law conformance method."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
LOCAL_VERIFICATION_PATH = REPO_ROOT / "docs" / "CORTEX_V2_LOCAL_VERIFICATION.md"
MAKEFILE_PATH = REPO_ROOT / "Makefile"
ACTIVE_WORKSTREAM_PATH = REPO_ROOT / "docs" / "CORTEX_V2_ACTIVE_WORKSTREAM.md"
IMPLEMENTATION_MASTER_PLAN_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md"
)
PHASE_GATES_PATH = REPO_ROOT / "docs" / "CORTEX_V2_PHASE_GATES_2.md"
LIVE_VALIDATION_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md"
)
LIVE_VALIDATION_VERDICT_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md"
)
LIVE_SERVICE_PROOF_PATH = REPO_ROOT / "docs" / "CORTEX_V2_LIVE_SERVICE_PROOF_0.md"
EXECUTIVE_RESTORATION_NOTE_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_EXECUTIVE_RESTORATION_NOTE.md"
)
OPENAI_VERIFIED_WORK_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPENAI_VERIFIED_WORK_PROGRAM_0.md"
)
LIVE_COMPARE_PATH = REPO_ROOT / "tools" / "live_compare.py"
LIVE_VALIDATION_SCOPE_SOURCE_PATH = REPO_ROOT / "tools" / "live_validation_common.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_git_ref_text(ref: str, path: Path) -> str:
    relative_path = path.relative_to(REPO_ROOT).as_posix()
    return subprocess.check_output(
        ["git", "show", f"{ref}:{relative_path}"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
    )


def _main_sync_state() -> str:
    raw = subprocess.check_output(
        ["git", "rev-list", "--left-right", "--count", "origin/main...main"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
    ).strip()
    behind_str, ahead_str = raw.split()
    behind = int(behind_str)
    ahead = int(ahead_str)
    if ahead and behind:
        return "diverged"
    if ahead:
        return "ahead"
    if behind:
        return "behind"
    return "synced"


def _local_review_branches() -> list[str]:
    output = subprocess.check_output(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/review"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def _extract_doc_make_targets(doc_text: str) -> set[str]:
    return set(re.findall(r"^make ([a-zA-Z0-9][a-zA-Z0-9_-]*)$", doc_text, re.MULTILINE))


def _extract_make_targets(makefile_text: str) -> set[str]:
    return set(re.findall(r"^([a-zA-Z0-9][a-zA-Z0-9_-]*):", makefile_text, re.MULTILINE))


def _extract_section(doc_text: str, heading: str) -> str:
    match = re.search(
        rf"## {re.escape(heading)}\n(?P<section>.*?)(?:\n## |\Z)",
        doc_text,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group("section")


def _extract_phase_gate_row(doc_text: str, gate: str) -> str:
    match = re.search(rf"^\| `{re.escape(gate)}` .*?$", doc_text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing phase-gate row: {gate}")
    return match.group(0)


def test_local_verification_doc_make_targets_exist_in_makefile() -> None:
    doc_text = _read(LOCAL_VERIFICATION_PATH)
    makefile_text = _read(MAKEFILE_PATH)

    assert _extract_doc_make_targets(doc_text) <= _extract_make_targets(makefile_text)


def test_active_openai_only_local_verification_bundle_is_recorded() -> None:
    text = _read(LOCAL_VERIFICATION_PATH)
    section = _extract_section(text, "Active OpenAI-only current-line proof bundle")

    assert (
        "This is the only active current-line proof bundle for the accepted OpenAI-only product scope."
        in section
    )
    assert "python3 tools/live_preflight.py --skip-updates" in section
    assert (
        "python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite current"
        in section
    )
    assert (
        "python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite canonical_anchor"
        in section
    )
    assert "python3 tools/live_compare.py" in section
    assert (
        "python3 -m pytest -q tests/unit/test_live_validation_tools.py "
        "tests/unit/test_verification_docs_sync.py "
        "tests/unit/test_correspondence_sre.py tests/unit/test_import_smoke.py"
    ) in section
    assert (
        "Retained watchlist/reference tools remain callable below, but they are not active closure surfaces for runtime truth."
        in section
    )

    assert "make live-provider-baselines" not in section
    assert "make live-host-native-product-paths" not in section
    assert "make live-openai-app-server" not in section
    assert "make live-operator-payoff-audit" not in section
    assert "make live-operator-directionality" not in section
    assert "make live-operator-directionality-audit" not in section
    assert "tests/unit/test_operator_routing.py" not in section


def test_watchlist_reference_appendix_retains_demoted_tools() -> None:
    text = _read(LOCAL_VERIFICATION_PATH)
    appendix = _extract_section(text, "Retained watchlist/reference appendix")

    assert (
        "These retained tools remain callable for drift detection, host-boundary research, and historical/reference auditing."
        in appendix
    )
    assert (
        "They are explicitly watchlist/reference only after X2 and are not part of the active current-line closure path."
        in appendix
    )
    assert "### Live provider baselines" in appendix
    assert "make live-provider-baselines" in appendix
    assert "make live-provider-baselines-automation" in appendix
    assert "### Live host-native product paths" in appendix
    assert "make live-host-native-product-paths" in appendix
    assert "### Live OpenAI App Server operator proof" in appendix
    assert "make live-openai-app-server" in appendix
    assert "### Live operator payoff audit" in appendix
    assert "make live-operator-payoff-audit" in appendix
    assert "### Operator routing realization" in appendix
    assert "tests/unit/test_operator_routing.py" in appendix
    assert "### Live operator directionality" in appendix
    assert "make live-operator-directionality" in appendix
    assert "### Live operator directionality audit" in appendix
    assert "make live-operator-directionality-audit" in appendix


def test_openai_host_control_local_revalidation_mentions_verified_work_without_widening_canonical_proof() -> None:
    text = _read(LOCAL_VERIFICATION_PATH)
    section = _extract_section(text, "OpenAI host-control revalidation")

    assert "the default thin text-only path when no `work_contract` is present" in section
    assert "shared verified-work law" in section
    assert "runtime-native verification binding" in section
    assert "Any larger-task live-value reruns for the verified-work path remain local exploratory evidence only" in section
    assert "python3 -m pytest tests/unit/test_verified_work.py -q" in section
    assert "python3 -m pytest tests/unit/test_verified_work_runtime.py -q" in section
    assert "python3 -m pytest tests/unit/test_openai_runtime_step.py -q" in section
    assert "make revalidate-openai-host-control" in section


def test_live_compare_is_product_first_but_json_compatible() -> None:
    text = _read(LIVE_COMPARE_PATH)

    assert '"canonical_provider_scope": sorted(canonical_scope)' in text
    assert '"service_success_count": service_success_count' in text
    assert '"watchlist_drift_hosts": watchlist_drift_hosts' in text
    assert '"next_corrective_seam": _next_corrective_seam(' in text
    assert '"verdict_reason": verdict_reason' in text
    assert '"providers": providers' in text

    assert "## OpenAI current product scope" in text
    assert "## Out-of-scope backlog" in text
    assert "## Watchlist drift" in text
    assert "## Next corrective seam" in text
    assert "## Lane relationship" in text
    assert (
        "current OpenAI-only product scope is already re-earned on the canonical direct-API lane and the active support/eval shell is already compressed"
        in text
    )

    assert "Watchlist pass_minimal host count" not in text
    assert "watchlist chosen models" not in text
    assert "watchlist hook labels" not in text
    assert "exploratory pro chosen models" not in text


def test_agents_and_master_plan_record_cortex_law_train_method() -> None:
    agents_text = _read(AGENTS_PATH)
    master_plan_text = _read(IMPLEMENTATION_MASTER_PLAN_PATH)

    assert "## Cortex-law train discipline" in agents_text
    assert "Cortex is the invariant cortical circuit in this repository." in agents_text
    assert "`Cortex truth`" in agents_text
    assert "`brain-wiring truth`" in agents_text
    assert "`conformance truth`" in agents_text
    assert "`shipping truth`" in agents_text
    assert "`Train Charter`" in agents_text
    assert "build -> test -> iterate -> cut" in agents_text
    assert "if two iterations fail without improving the divergence classification" in agents_text
    assert "run the same contract pack on OpenAI, Claude, and Gemini" in agents_text
    assert "`baseline result`" in agents_text
    assert "`primary_metric`" in agents_text
    assert "`guardrail_metric`" in agents_text
    assert "`iteration_budget`" in agents_text
    assert "`rollback_surface`" in agents_text
    assert "`escalation_triggers`" in agents_text
    assert "`promote`, `revise`, `cut`, `escalate`" in agents_text
    assert "`deterministic`" in agents_text
    assert "`shared verification-plumbing`" in agents_text
    assert "`timing/env-sensitive`" in agents_text
    assert "tools/cortex_train_loop.py" in agents_text

    assert "Post-closeout Cortex-law train method:" in master_plan_text
    assert "define the Cortex law being changed" in master_plan_text
    assert "run tri-brain conformance on OpenAI, Claude, and Gemini" in master_plan_text
    assert "one Cortex-law micro-train at a time" in master_plan_text
    assert "no second pack until the first has a stable divergence classification" in master_plan_text
    assert "borrow or clone only proven narrow mechanisms" in master_plan_text
    assert "lock one `Train Charter`, one baseline result, one primary metric, one guardrail metric" in master_plan_text
    assert "end the iteration in exactly one of `promote`, `revise`, `cut`, or `escalate`" in master_plan_text
    assert "`env_blocked` never counts as success" in master_plan_text
    assert "thin local recorder" in master_plan_text


def test_active_current_line_docs_frame_openai_only_truth_and_watchlist_retention() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    local_verification_text = _read(LOCAL_VERIFICATION_PATH)
    program_text = _read(LIVE_VALIDATION_PROGRAM_PATH)
    verdict_text = _read(LIVE_VALIDATION_VERDICT_PATH)
    service_proof_text = _read(LIVE_SERVICE_PROOF_PATH)
    restoration_note_text = _read(EXECUTIVE_RESTORATION_NOTE_PATH)
    verified_work_program_text = _read(OPENAI_VERIFIED_WORK_PROGRAM_PATH)

    assert "`service_api` is the canonical runtime truth lane" in workstream_text
    assert "`operator_cli` is a watchlist and exploratory-comparison lane" in workstream_text
    assert "the repo now distinguishes four truths explicitly" in workstream_text
    assert "`Cortex truth`" in workstream_text
    assert "`brain-wiring truth`" in workstream_text
    assert "`conformance truth`" in workstream_text
    assert "`shipping truth`" in workstream_text
    assert (
        "the accepted product/runtime claim is now explicitly OpenAI-only on the canonical direct-API lane"
        in workstream_text
    )
    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
    ).strip()
    assert f"Current working branch at ledger update: `{current_branch}`" in workstream_text
    if current_branch == "main":
        assert (
            "Current branch role: accepted resting line after the E6 OpenAI verified-work context slice"
            in workstream_text
        )
        assert "Current candidate seam: `none active`" in workstream_text
    else:
        assert (
            "Current branch role: explicit manual/review branch for the E7 verified-work breadth train while the accepted baseline remains local `main`"
            in workstream_text
        )
        assert "Current candidate seam: `E7 verified-work breadth train`" in workstream_text
    assert (
        "A0, P1C, S1, S1C, X1, X2, the first verified-work restoration slice, the Cortex-law / fast-train method slice, the verified-work neutralization / conformance-correction slice, the Claude operator workspace-truth slice, the OpenAI verified-work context slice, and the C3B brutal closed-loop train method are now accepted on local `main`"
        in workstream_text
    )
    assert "docs/CORTEX_V2_EXECUTIVE_RESTORATION_NOTE.md" in workstream_text
    assert (
        "retained operator/watchlist tools stay callable as diagnostics, but they no longer define the active current-line closure path"
        in workstream_text
    )
    assert "the first verified-work restoration slice now lands" in workstream_text
    assert "the `O4R` verified-work row now lands" in workstream_text
    assert "No active verified-work shipping-gap seam remains on the accepted local `main` line." in workstream_text
    assert "write the `Train Charter` first" in workstream_text
    assert "run tri-brain conformance on OpenAI, Claude, and Gemini" in workstream_text
    assert "baseline result, primary metric, guardrail metric, iteration budget, rollback surface, and escalation-trigger fields" in workstream_text
    assert "`promote`, `revise`, `cut`, `escalate`" in workstream_text
    assert "`tools/cortex_train_loop.py`" in workstream_text
    assert "baseline drift where `summary.latest` referenced missing artifacts" in workstream_text
    assert "run_20260408T074128+0000" in workstream_text
    assert "`CT2` therefore re-earned on the current line" in workstream_text
    assert "OpenAI `service_api`: conformant on three repeated targeted current reruns" in workstream_text
    assert "Claude `operator_cli`: no longer divergent on truthful staged-workspace runs" in workstream_text
    assert "Gemini `operator_cli`: conformant on the corrected current line" in workstream_text
    assert "the current E7 breadth slice on this review branch now adds" in workstream_text
    assert "`python_workspace_pytest_port_fix_v1`" in workstream_text
    assert "`verified_work_normalize_port_v1`" in workstream_text

    assert (
        "This is the only active current-line proof bundle for the accepted OpenAI-only product scope."
        in local_verification_text
    )
    assert "Retained watchlist/reference appendix" in local_verification_text

    assert "`service_api`" in program_text
    assert "`operator_cli`" in program_text
    assert "the accepted current product scope on the canonical direct-API lane is now OpenAI-only" in program_text
    assert (
        "retained operator/watchlist and historical/reference tools remain diagnostic evidence, not active closure surfaces"
        in program_text
    )
    assert "no active support/eval compression seam remains on the accepted local `main` line" in program_text

    assert (
        "`service_api`: `execution_surface = direct_api`, `evidence_role = canonical_truth`"
        in verdict_text
    )
    assert (
        "`operator_cli`: `execution_surface = headless_cli`, `evidence_role = watchlist`"
        in verdict_text
    )
    assert (
        "Retained operator/watchlist tools remain diagnostic evidence, not active proof surfaces for the current product claim."
        in verdict_text
    )
    assert "no active support/eval compression seam remains on the accepted local `main` line" in verdict_text

    assert "`service_api` is the canonical runtime truth lane" in service_proof_text
    assert (
        "accepted local `main` line, with `origin/main` reconciliation tracked separately as workflow hygiene"
        in service_proof_text
    )
    assert (
        "retained operator/watchlist tools remain diagnostic evidence only and are outside the active service-proof bundle"
        in service_proof_text
    )
    assert "no active support/eval compression seam remains on the accepted local `main` line" in service_proof_text

    assert "accepted executive-restoration note with the first verified-work restoration slice now landed on the current OpenAI realization" in restoration_note_text
    assert "The local larger-task exploratory runs do not justify prompt shaping" in restoration_note_text
    assert "The next runtime/product seam should improve Cortex law first" in restoration_note_text
    assert "The first restoration slice is now landed on the accepted OpenAI realization" in restoration_note_text
    assert "the shared verified-work runtime helpers now live in the neutral `cortex/runtime/verified_work_runtime.py` home" in restoration_note_text
    assert "repeated targeted local OpenAI reruns on the bookmarks pack now pass on the shipping-default lane" in restoration_note_text
    assert "## Conformance reading under the current method" in restoration_note_text
    assert "It should ask whether the same Cortex law is conformant, partial, divergent, unwired, or env-blocked" in restoration_note_text
    assert "The current next decision for the shipping-default lane is therefore `promote`" in restoration_note_text
    assert "This note does not authorize:" in restoration_note_text

    assert "accepted bounded runtime-program brief for the landed verified-work restoration lane" in verified_work_program_text
    assert "keep the accepted thin `O4` path unchanged when no `work_contract` is present" in verified_work_program_text
    assert "This program is intentionally outside the current compact canonical proof bundle" in verified_work_program_text
    assert "the shared verified-work runtime helpers now live in the neutral `cortex/runtime/verified_work_runtime.py` home" in verified_work_program_text
    assert "`python_workspace_pytest_port_fix_v1`" in verified_work_program_text
    assert "`verified_work_normalize_port_v1`" in verified_work_program_text
    assert "`O4R` is therefore landed for the current OpenAI shipping-default scope" in verified_work_program_text


def test_x2_accepted_line_claims_match_main() -> None:
    local_verification_text = _read(LOCAL_VERIFICATION_PATH)
    program_text = _read(LIVE_VALIDATION_PROGRAM_PATH)
    verdict_text = _read(LIVE_VALIDATION_VERDICT_PATH)
    service_proof_text = _read(LIVE_SERVICE_PROOF_PATH)
    phase_gate_text = _read(PHASE_GATES_PATH)

    main_local_verification_text = _read_git_ref_text("main", LOCAL_VERIFICATION_PATH)
    main_program_text = _read_git_ref_text("main", LIVE_VALIDATION_PROGRAM_PATH)
    main_verdict_text = _read_git_ref_text("main", LIVE_VALIDATION_VERDICT_PATH)
    main_service_proof_text = _read_git_ref_text("main", LIVE_SERVICE_PROOF_PATH)
    main_phase_gate_text = _read_git_ref_text("main", PHASE_GATES_PATH)

    accepted_bundle_claim = (
        "This is the only active current-line proof bundle for the accepted OpenAI-only product scope."
    )
    compact_l3_detail = (
        "the active current-line proof bundle is now intentionally compact around preflight, direct OpenAI host-control reruns, `make live-compare`, and deterministic support checks"
    )
    compact_l6c_detail = (
        "the active service-proof bundle is intentionally compact around preflight, direct OpenAI host-control reruns, `make live-compare`, and deterministic support checks"
    )
    resting_truth_phrase = (
        "no active support/eval compression seam remains on the accepted local `main` line"
    )

    if accepted_bundle_claim in local_verification_text:
        assert accepted_bundle_claim in main_local_verification_text
    if compact_l3_detail in phase_gate_text:
        assert compact_l3_detail in main_phase_gate_text
    if compact_l6c_detail in phase_gate_text:
        assert compact_l6c_detail in main_phase_gate_text
    if resting_truth_phrase in program_text:
        assert resting_truth_phrase in main_program_text
    if resting_truth_phrase in verdict_text:
        assert resting_truth_phrase in main_verdict_text
    if resting_truth_phrase in service_proof_text:
        assert resting_truth_phrase in main_service_proof_text


def test_phase_gates_match_openai_only_truth_and_hygiene() -> None:
    text = _read(PHASE_GATES_PATH)

    o4_row = _extract_phase_gate_row(text, "O4")
    o4r_row = _extract_phase_gate_row(text, "O4R")
    c1_row = _extract_phase_gate_row(text, "CT1")
    c2_row = _extract_phase_gate_row(text, "CT2")
    c3_row = _extract_phase_gate_row(text, "CT3")
    l3_row = _extract_phase_gate_row(text, "L3")
    l4_row = _extract_phase_gate_row(text, "L4")
    l5_row = _extract_phase_gate_row(text, "L5")
    l6c_row = _extract_phase_gate_row(text, "L6C")
    l6d_row = _extract_phase_gate_row(text, "L6D")
    j4f_row = _extract_phase_gate_row(text, "J4F")

    assert (
        "python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite current"
        in l3_row
    )
    assert (
        "python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite canonical_anchor"
        in l3_row
    )
    assert "make live-provider-baselines" not in l3_row
    assert "make live-openai-app-server" not in l3_row

    assert (
        "closed for the accepted OpenAI-only product scope; reopen only if product scope intentionally widens"
        in l4_row
    )
    assert "remains thin and text-only by default when no `work_contract` is present" in o4_row
    assert "keeps `openai_product_journal` v1 only" in o4_row
    assert "closed | landed |" in o4r_row
    assert "the invariant verified-work runtime helpers now live in a neutral runtime home" in o4r_row
    assert "bounded read-only workspace context bundle over the current writable-file contents plus the contract tests" in o4r_row
    assert "tools/cortex_conformance.py" in c1_row
    assert "Train Charter" in c1_row
    assert "tools/cortex_train_loop.py" in c1_row
    assert "baseline / metric / rollback / escalation inputs" in c1_row
    assert "closed on local `main` for the bookmarks anchor pack" in c2_row
    assert "landed" in c2_row
    assert "make conformance-preflight" in c2_row
    assert "python3 tools/cortex_conformance.py --mode reconcile-latest" in c2_row
    assert "OpenAI `service_api` conformant on three repeated targeted reruns" in c2_row
    assert "run_20260408T074128+0000" in c2_row
    assert "Claude `operator_cli` conformant after one lawful repair" in c2_row
    assert "Gemini `operator_cli` conformant" in c2_row
    assert "`summary.latest` now publishes only from full tri-brain runs for the bookmarks anchor pack" in c2_row
    assert "latest surviving full run that matches accepted `CT2` decision" in c2_row
    assert "current shipping-default decision is `promote`" in c2_row
    assert "run_20260408T083436+0000" in c2_row
    assert "strongest available native surface may stand in for development conformance" in c3_row
    assert "historical/watchlist-only; do not use for runtime closure" in l5_row
    assert "closed | landed" in l6c_row
    assert (
        "closed for the accepted OpenAI-only product scope; reopen only if product scope intentionally widens"
        in l6d_row
    )
    assert "origin/main reconciliation only | partial |" in j4f_row


def test_accepted_openai_only_scope_claim_matches_main_line() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    program_text = _read(LIVE_VALIDATION_PROGRAM_PATH)
    verdict_text = _read(LIVE_VALIDATION_VERDICT_PATH)
    phase_gate_text = _read(PHASE_GATES_PATH)

    main_workstream_text = _read_git_ref_text("main", ACTIVE_WORKSTREAM_PATH)
    main_phase_gate_text = _read_git_ref_text("main", PHASE_GATES_PATH)
    main_scope_source_text = _read_git_ref_text("main", LIVE_VALIDATION_SCOPE_SOURCE_PATH)

    assert (
        "the accepted product/runtime claim is now explicitly OpenAI-only on the canonical direct-API lane"
        in workstream_text
    )
    assert "the accepted current product scope on the canonical direct-API lane is now OpenAI-only" in program_text
    assert "the accepted current product scope on the canonical lane is now OpenAI-only" in verdict_text
    assert '"provider_scope": ["openai"]' in main_scope_source_text
    assert (
        "the accepted product/runtime claim is now explicitly OpenAI-only on the canonical direct-API lane"
        in main_workstream_text
    )
    assert (
        "| `L4` lifecycle-first payoff verdict | `docs/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`; `make live-compare` | closed for the accepted OpenAI-only product scope; reopen only if product scope intentionally widens | landed |"
        in phase_gate_text
    )
    assert (
        "| `L4` lifecycle-first payoff verdict | `docs/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`; `make live-compare` | closed for the accepted OpenAI-only product scope; reopen only if product scope intentionally widens | landed |"
        in main_phase_gate_text
    )


def test_workstream_and_phase_gates_do_not_hide_major_brains_behind_generic_backlog_language() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    phase_gate_text = _read(PHASE_GATES_PATH)

    assert "future host-expansion backlog only" not in workstream_text
    assert "future host-expansion backlog only" not in phase_gate_text
    assert "Claude stays outside the accepted current product scope as future host-expansion backlog" not in workstream_text
    assert "Claude and Gemini may remain blocked as future host-expansion backlog" not in phase_gate_text


def test_current_state_docs_use_stable_openai_evidence_and_truthful_hygiene_language() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    program_text = _read(LIVE_VALIDATION_PROGRAM_PATH)
    verdict_text = _read(LIVE_VALIDATION_VERDICT_PATH)
    service_proof_text = _read(LIVE_SERVICE_PROOF_PATH)
    phase_gate_text = _read(PHASE_GATES_PATH)

    for text in (
        workstream_text,
        program_text,
        verdict_text,
        service_proof_text,
        phase_gate_text,
    ):
        assert "three positive current-machine `canonical_anchor` cycles" not in text

    assert "exact cycle count is local-artifact truth" in workstream_text
    assert "exact cycle count is local-artifact truth" in program_text
    assert "exact cycle count remains local-artifact truth" in verdict_text
    assert "exact cycle count and per-scenario totals live only in local artifacts" in service_proof_text
    assert (
        "exact cycle count remains local-artifact truth under `.cortex/live_validation/automation/openai/service/service_runs.json`"
        in phase_gate_text
    )

    assert "clean synced `main`" not in workstream_text
    assert "clean synced `main`" not in program_text
    assert "clean synced `main`" not in service_proof_text
    assert "accepted local `main` line" in workstream_text
    assert "accepted local `main` line" in program_text
    assert "accepted local `main` line" in service_proof_text


def test_j4f_hygiene_status_matches_local_repo_truth() -> None:
    phase_gate_text = _read(PHASE_GATES_PATH)
    current_sync_state = _main_sync_state()
    review_branches = _local_review_branches()
    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
    ).strip()

    partial_row = (
        "| `J4F` workflow closeout and hygiene | `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`; `REPO_WORKFLOW.md`; `python3 scripts/repo_workflow.py close-session --message ...`; `python3 scripts/repo_workflow.py sync-main`; `python3 scripts/repo_workflow.py cleanup-report` | origin/main reconciliation only | partial |"
    )

    assert partial_row in phase_gate_text
    assert current_sync_state == "ahead"
    if current_branch == "main":
        assert review_branches == []
    else:
        assert review_branches == [current_branch]
    assert "archive/review--*` tags and removed" in phase_gate_text
