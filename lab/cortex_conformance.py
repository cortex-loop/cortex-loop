"""Tri-brain conformance harness for Cortex-law contract packs."""

from __future__ import annotations

import argparse
import shutil
import json
import re
import sys
import tempfile
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from internal.truth.status import accepted_conformance_next_decision  # noqa: E402
from cortex.hosts.openai.host_control import (  # noqa: E402
    OpenAIHostControlRequest,
    OpenAIResponseStreamTransportError,
    run_openai_host_control,
)
from lab.openai_host_control_experiments import (  # noqa: E402
    OpenAIHostControlAblationConfig,
    run_openai_host_control_experiment,
)
from cortex.runtime.verified_work_runtime import (  # noqa: E402
    build_verified_work_instructions,
    build_verified_work_repair_ticket,
    verify_verified_work_result,
)
from cortex.sre.verified_work import VerificationOutcome, WorkContract  # noqa: E402

from lab.live_validation_common import (  # noqa: E402
    BLOCKING_FAILURE_CLASSES,
    LOCAL_LIVE_ROOT,
    api_key_presence,
    classify_failure,
    command_exists,
    extract_result_text,
    load_local_env_file,
    now_utc_iso,
    parse_json_records,
    run_command,
    sanitize_text,
    write_json,
    write_text,
)
from lab.service_spend_gate import require_openai_service_spend_approval  # noqa: E402


Brain = Literal["openai", "claude", "gemini"]
Surface = Literal["service_api", "operator_cli"]
ConformanceStatus = Literal["conformant", "partial", "divergent", "unwired", "env_blocked"]
DivergenceClass = Literal["cortex_law", "brain_wiring", "surface_wiring", "env_blocked"]
ConformanceSummary = dict[str, Any]

ACTIVE_CONTRACT_PACK = "verified_work_bookmarks_v1"
NORMALIZE_PORT_CONTRACT_PACK = "verified_work_normalize_port_v1"
FEATURE_FLAGS_CONTRACT_PACK = "verified_work_feature_flags_v1"
CONFORMANCE_ROOT = LOCAL_LIVE_ROOT / "conformance"
BOOKMARKS_TASK_PATH = (
    ROOT / "tests" / "fixtures" / "live_validation" / "bookmarks_app_template" / "README_TASK.md"
)
NORMALIZE_PORT_TASK_PATH = (
    ROOT / "tests" / "fixtures" / "live_validation" / "project_template" / "README_TASK.md"
)
FEATURE_FLAGS_TASK_PATH = (
    ROOT / "tests" / "fixtures" / "live_validation" / "feature_flags_template" / "README_TASK.md"
)
_OPENAI_ACTION_TAG = "openai-response-stream"
_OPENAI_MODEL = "gpt-5.4"
_CLAUDE_MODEL = "claude-sonnet-4-6"
_CLAUDE_READ_ONLY_TOOLS = "Read,Glob,Grep,LS"
_SURFACE_ORDER: dict[Brain, tuple[Surface, ...]] = {
    "openai": ("service_api",),
    "claude": ("operator_cli",),
    "gemini": ("operator_cli",),
}
_ALL_BRAINS: tuple[Brain, ...] = tuple(_SURFACE_ORDER)


@dataclass(frozen=True, slots=True)
class TrainCharter:
    cortex_invariant: str
    borrowed_mechanism: str
    primary_proving_wiring: str
    conformance_surfaces: tuple[str, ...]
    kill_criteria: tuple[str, ...]

    def __post_init__(self) -> None:
        for label, value in (
            ("cortex_invariant", self.cortex_invariant),
            ("borrowed_mechanism", self.borrowed_mechanism),
            ("primary_proving_wiring", self.primary_proving_wiring),
        ):
            if not (isinstance(value, str) and value.strip()):
                raise ValueError(f"TrainCharter.{label} must be non-empty after trimming.")
        if not self.conformance_surfaces or any(
            not (isinstance(surface, str) and surface.strip())
            for surface in self.conformance_surfaces
        ):
            raise ValueError(
                "TrainCharter.conformance_surfaces must contain at least one non-empty surface label."
            )
        if not self.kill_criteria or any(
            not (isinstance(item, str) and item.strip()) for item in self.kill_criteria
        ):
            raise ValueError(
                "TrainCharter.kill_criteria must contain at least one non-empty criterion."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "cortex_invariant": self.cortex_invariant,
            "borrowed_mechanism": self.borrowed_mechanism,
            "primary_proving_wiring": self.primary_proving_wiring,
            "conformance_surfaces": list(self.conformance_surfaces),
            "kill_criteria": list(self.kill_criteria),
        }


@dataclass(frozen=True, slots=True)
class ContractPack:
    contract_pack: str
    prompt_text: str
    workspace_template_relpath: str
    work_contract: WorkContract
    train_charter: TrainCharter
    shipping_default: str

    def __post_init__(self) -> None:
        if not (isinstance(self.contract_pack, str) and self.contract_pack.strip()):
            raise ValueError("ContractPack.contract_pack must be non-empty after trimming.")
        if not (isinstance(self.prompt_text, str) and self.prompt_text.strip()):
            raise ValueError("ContractPack.prompt_text must be non-empty after trimming.")
        if not (
            isinstance(self.workspace_template_relpath, str)
            and self.workspace_template_relpath.strip()
        ):
            raise ValueError(
                "ContractPack.workspace_template_relpath must be non-empty after trimming."
            )
        if Path(self.workspace_template_relpath).is_absolute():
            raise ValueError(
                "ContractPack.workspace_template_relpath must be repo-relative, not absolute."
            )
        if not isinstance(self.work_contract, WorkContract):
            actual_type = type(self.work_contract).__name__
            raise TypeError(
                "ContractPack.work_contract must be WorkContract, "
                f"got {actual_type}."
            )
        if not isinstance(self.train_charter, TrainCharter):
            actual_type = type(self.train_charter).__name__
            raise TypeError(
                "ContractPack.train_charter must be TrainCharter, "
                f"got {actual_type}."
            )
        if not (isinstance(self.shipping_default, str) and self.shipping_default.strip()):
            raise ValueError("ContractPack.shipping_default must be non-empty after trimming.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "contract_pack": self.contract_pack,
            "prompt_text": self.prompt_text,
            "workspace_template_relpath": self.workspace_template_relpath,
            "work_contract": self.work_contract.as_payload(),
            "train_charter": self.train_charter.as_payload(),
            "shipping_default": self.shipping_default,
        }


@dataclass(frozen=True, slots=True)
class ConformanceRunResult:
    brain: Brain
    surface: Surface
    contract_pack: str
    status: ConformanceStatus
    divergence_class: DivergenceClass | None = None
    first_attempt_status: str | None = None
    first_attempt_failure_class: str | None = None
    final_failure_class: str | None = None
    verification_status: str | None = None
    parseable: bool | None = None
    import_smoke_ok: bool | None = None
    pytest_passed: int | None = None
    pytest_failed: int | None = None
    attempt_count: int | None = None
    repair_conversion: str | None = None
    extraction_mode: str | None = None
    note: str | None = None
    transport_failure_class: str | None = None
    artifact_relpath: str | None = None

    def __post_init__(self) -> None:
        if self.status in {"conformant", "partial", "divergent"} and self.attempt_count is None:
            raise ValueError(
                "ConformanceRunResult.attempt_count is required for executed conformance results."
            )
        if self.status in {"env_blocked", "unwired"} and self.attempt_count is not None:
            raise ValueError(
                "ConformanceRunResult.attempt_count must be omitted when no execution occurred."
            )
        if self.divergence_class == "env_blocked" and self.status != "env_blocked":
            raise ValueError("env_blocked divergence requires env_blocked status.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "brain": self.brain,
            "surface": self.surface,
            "contract_pack": self.contract_pack,
            "status": self.status,
            "divergence_class": self.divergence_class,
            "first_attempt_status": self.first_attempt_status,
            "first_attempt_failure_class": self.first_attempt_failure_class,
            "final_failure_class": self.final_failure_class,
            "verification_status": self.verification_status,
            "parseable": self.parseable,
            "import_smoke_ok": self.import_smoke_ok,
            "pytest_passed": self.pytest_passed,
            "pytest_failed": self.pytest_failed,
            "attempt_count": self.attempt_count,
            "repair_conversion": self.repair_conversion,
            "extraction_mode": self.extraction_mode,
            "note": self.note,
            "transport_failure_class": self.transport_failure_class,
            "artifact_relpath": self.artifact_relpath,
        }


@dataclass(frozen=True, slots=True)
class SurfaceProbe:
    brain: Brain
    surface: Surface
    status: ConformanceStatus
    reason: str

    def as_payload(self) -> dict[str, str]:
        return {
            "brain": self.brain,
            "surface": self.surface,
            "status": self.status,
            "reason": self.reason,
        }


def active_contract_pack() -> ContractPack:
    return contract_pack_by_name(ACTIVE_CONTRACT_PACK)


def contract_pack_with_max_repair_turns(
    contract_pack: ContractPack,
    *,
    max_repair_turns: int,
) -> ContractPack:
    if max_repair_turns not in (0, 1):
        raise ValueError("max_repair_turns override must be 0 or 1.")
    if contract_pack.work_contract.max_repair_turns == max_repair_turns:
        return contract_pack
    return replace(
        contract_pack,
        work_contract=replace(contract_pack.work_contract, max_repair_turns=max_repair_turns),
    )


def contract_pack_by_name(name: str) -> ContractPack:
    if name == ACTIVE_CONTRACT_PACK:
        prompt_text = BOOKMARKS_TASK_PATH.read_text(encoding="utf-8").strip()
        return ContractPack(
            contract_pack=ACTIVE_CONTRACT_PACK,
            prompt_text=prompt_text,
            workspace_template_relpath="tests/fixtures/live_validation/bookmarks_app_template",
            work_contract=WorkContract(
                allowed_write_paths=(
                    "src/bookmarks_api/main.py",
                    "src/bookmarks_api/models.py",
                    "src/bookmarks_api/store.py",
                ),
                verification_profile="python_workspace_pytest_v1",
                output_carrier="full_files",
                max_repair_turns=1,
            ),
            train_charter=TrainCharter(
                cortex_invariant=(
                    "optional work contract, runtime-native verification truth, and one bounded repair turn"
                ),
                borrowed_mechanism=(
                    "reuse the landed verified-work law plus the existing full_files verifier contract instead of adding host-specific policy math"
                ),
                primary_proving_wiring="openai:service_api",
                conformance_surfaces=(
                    "openai:service_api",
                    "claude:operator_cli",
                    "gemini:operator_cli",
                ),
                kill_criteria=(
                    "cut a new Cortex-law addition if it does not improve the active divergence classification after two iterations",
                    "do not widen shipping truth from conformance-only results",
                ),
            ),
            shipping_default="openai:service_api",
        )
    if name == NORMALIZE_PORT_CONTRACT_PACK:
        prompt_text = NORMALIZE_PORT_TASK_PATH.read_text(encoding="utf-8").strip()
        return ContractPack(
            contract_pack=NORMALIZE_PORT_CONTRACT_PACK,
            prompt_text=prompt_text,
            workspace_template_relpath="tests/fixtures/live_validation/project_template",
            work_contract=WorkContract(
                allowed_write_paths=("src/normalize_port.py",),
                verification_profile="python_workspace_pytest_port_fix_v1",
                output_carrier="full_files",
                max_repair_turns=1,
            ),
            train_charter=TrainCharter(
                cortex_invariant=(
                    "optional work contract, runtime-native verification truth, and one bounded repair turn"
                ),
                borrowed_mechanism=(
                    "reuse the existing normalize-port project_template verifier scaffold instead of inventing a new benchmark family"
                ),
                primary_proving_wiring="openai:service_api",
                conformance_surfaces=(
                    "openai:service_api",
                    "claude:operator_cli",
                    "gemini:operator_cli",
                ),
                kill_criteria=(
                    "cut the second-pack breadth slice if repeat-stable OpenAI conformance does not improve within the locked iteration budget",
                    "do not repurpose the bookmarks summary.latest anchor while breadth evidence is still being earned",
                ),
            ),
            shipping_default="openai:service_api",
        )
    if name == FEATURE_FLAGS_CONTRACT_PACK:
        prompt_text = FEATURE_FLAGS_TASK_PATH.read_text(encoding="utf-8").strip()
        return ContractPack(
            contract_pack=FEATURE_FLAGS_CONTRACT_PACK,
            prompt_text=prompt_text,
            workspace_template_relpath="tests/fixtures/live_validation/feature_flags_template",
            work_contract=WorkContract(
                allowed_write_paths=(
                    "src/feature_flags/models.py",
                    "src/feature_flags/evaluator.py",
                ),
                verification_profile="python_workspace_pytest_feature_flags_v1",
                output_carrier="full_files",
                max_repair_turns=1,
            ),
            train_charter=TrainCharter(
                cortex_invariant=(
                    "optional work contract, runtime-native verification truth, and one bounded repair turn"
                ),
                borrowed_mechanism=(
                    "reuse the landed verified-work profile registry and add one middle-weight pure-Python evaluator pack"
                ),
                primary_proving_wiring="openai:service_api",
                conformance_surfaces=(
                    "openai:service_api",
                    "claude:operator_cli",
                    "gemini:operator_cli",
                ),
                kill_criteria=(
                    "cut the third-pack breadth slice if repeat-stable OpenAI conformance does not improve within the locked iteration budget",
                    "do not repurpose the bookmarks summary.latest anchor while breadth evidence is still being earned",
                ),
            ),
            shipping_default="openai:service_api",
        )
    raise ValueError(f"Unsupported contract pack: {name}")


def supported_contract_pack_names() -> tuple[str, ...]:
    return (
        ACTIVE_CONTRACT_PACK,
        NORMALIZE_PORT_CONTRACT_PACK,
        FEATURE_FLAGS_CONTRACT_PACK,
    )


def strongest_native_surface(brain: Brain, contract_pack: ContractPack) -> Surface:
    _ = contract_pack
    return _SURFACE_ORDER[brain][0]


@contextmanager
def _stage_contract_pack_workspace(
    contract_pack: ContractPack,
    *,
    prefix: str,
):
    template_root = ROOT / contract_pack.workspace_template_relpath
    if not template_root.exists():
        raise FileNotFoundError(
            "Contract pack workspace template is missing: "
            f"{contract_pack.workspace_template_relpath}"
        )
    if not template_root.is_dir():
        raise NotADirectoryError(
            "Contract pack workspace template must be a directory: "
            f"{contract_pack.workspace_template_relpath}"
        )
    with tempfile.TemporaryDirectory(prefix=prefix) as tmpdir:
        workspace = Path(tmpdir)
        shutil.copytree(template_root, workspace, dirs_exist_ok=True)
        yield workspace


def preflight_surface(brain: Brain, surface: Surface) -> SurfaceProbe:
    if brain == "openai" and surface == "service_api":
        keys = api_key_presence()
        if keys.get("OPENAI_API_KEY"):
            return SurfaceProbe(brain=brain, surface=surface, status="conformant", reason="OPENAI_API_KEY is present.")
        return SurfaceProbe(brain=brain, surface=surface, status="env_blocked", reason="OPENAI_API_KEY is missing.")
    if brain == "claude" and surface == "operator_cli":
        if not command_exists("claude"):
            return SurfaceProbe(brain=brain, surface=surface, status="env_blocked", reason="claude CLI is not installed.")
        auth = run_command(["claude", "auth", "status"], timeout_seconds=30.0)
        if auth["exit_code"] != 0:
            return SurfaceProbe(brain=brain, surface=surface, status="env_blocked", reason="claude auth status failed.")
        try:
            payload = json.loads(auth["stdout"])
        except json.JSONDecodeError:
            return SurfaceProbe(brain=brain, surface=surface, status="env_blocked", reason="claude auth status returned invalid JSON.")
        if isinstance(payload, dict) and bool(payload.get("loggedIn")):
            return SurfaceProbe(brain=brain, surface=surface, status="conformant", reason="Claude operator surface is signed in.")
        return SurfaceProbe(brain=brain, surface=surface, status="env_blocked", reason="Claude operator surface is not signed in.")
    if brain == "gemini" and surface == "operator_cli":
        if not command_exists("gemini"):
            return SurfaceProbe(brain=brain, surface=surface, status="env_blocked", reason="gemini CLI is not installed.")
        if api_key_presence().get("GEMINI_API_KEY"):
            return SurfaceProbe(brain=brain, surface=surface, status="conformant", reason="GEMINI_API_KEY is present.")
        return SurfaceProbe(
            brain=brain,
            surface=surface,
            status="partial",
            reason="Gemini operator surface requires a live probe to confirm auth and contract obedience on this machine.",
        )
    return SurfaceProbe(brain=brain, surface=surface, status="unwired", reason="No conformance runner is wired for this brain and surface.")


def classify_outcome_divergence(
    *,
    surface: Surface,
    outcome: VerificationOutcome,
) -> tuple[ConformanceStatus, DivergenceClass | None]:
    if outcome.status == "passed":
        return "conformant", None
    if outcome.failure_class in {"blocked_missing_info"}:
        return "partial", "brain_wiring"
    if outcome.failure_class == "blocked_unsafe":
        return "divergent", "brain_wiring"
    if outcome.failure_class == "output_invalid":
        if surface == "operator_cli":
            return "divergent", "surface_wiring"
        return "partial", "brain_wiring"
    if outcome.failure_class in {"import_smoke_failed", "test_failed"}:
        return "partial", "brain_wiring"
    return "divergent", "brain_wiring"


def classify_shared_divergence(
    results: list[ConformanceRunResult],
) -> DivergenceClass | None:
    comparable = [
        result
        for result in results
        if result.status in {"partial", "divergent"}
        and result.final_failure_class in {"output_invalid", "import_smoke_failed", "test_failed"}
        and result.transport_failure_class is None
    ]
    if len(comparable) < 2:
        return None
    failure_classes = {result.final_failure_class for result in comparable}
    if len(failure_classes) == 1:
        return "cortex_law"
    return None


def decide_iteration_outcome(
    results: list[ConformanceRunResult],
    *,
    shipping_default: str,
) -> str:
    shipping_brain, _shipping_surface = shipping_default.split(":", 1)
    shipping_result = next(
        (result for result in results if result.brain == shipping_brain),
        None,
    )
    if shipping_result is not None and shipping_result.status in {"partial", "divergent"}:
        return "revise"
    if classify_shared_divergence(results) == "cortex_law":
        return "revise"
    if any(result.status in {"partial", "divergent", "env_blocked"} for result in results):
        return "revise"
    return "promote"


def run_active_conformance(
    *,
    brains: tuple[Brain, ...],
    contract_pack: ContractPack | None = None,
    max_repair_turns_override: int | None = None,
    openai_ablation_config: OpenAIHostControlAblationConfig | None = None,
) -> dict[str, Any]:
    load_local_env_file()
    pack = contract_pack or active_contract_pack()
    if max_repair_turns_override is not None:
        pack = contract_pack_with_max_repair_turns(
            pack,
            max_repair_turns=max_repair_turns_override,
        )
    timestamp = now_utc_iso().replace(":", "").replace("-", "")
    run_root = CONFORMANCE_ROOT / f"run_{timestamp}"
    run_root.mkdir(parents=True, exist_ok=True)

    results: list[ConformanceRunResult] = []
    probes: list[SurfaceProbe] = []
    for brain in brains:
        surface = strongest_native_surface(brain, pack)
        probe = preflight_surface(brain, surface)
        probes.append(probe)
        if probe.status == "unwired":
            results.append(
                ConformanceRunResult(
                    brain=brain,
                    surface=surface,
                    contract_pack=pack.contract_pack,
                    status="unwired",
                    divergence_class=None,
                    note=probe.reason,
                )
            )
            continue
        if brain == "openai" and probe.status == "env_blocked":
            results.append(
                ConformanceRunResult(
                    brain=brain,
                    surface=surface,
                    contract_pack=pack.contract_pack,
                    status="env_blocked",
                    divergence_class="env_blocked",
                    note=probe.reason,
                    transport_failure_class="auth_missing",
                )
            )
            continue
        if brain == "claude" and probe.status == "env_blocked":
            results.append(
                ConformanceRunResult(
                    brain=brain,
                    surface=surface,
                    contract_pack=pack.contract_pack,
                    status="env_blocked",
                    divergence_class="env_blocked",
                    note=probe.reason,
                    transport_failure_class="not_logged_in",
                )
            )
            continue
        result = _run_conformance(
            brain=brain,
            surface=surface,
            contract_pack=pack,
            run_root=run_root,
            openai_ablation_config=openai_ablation_config,
        )
        results.append(result)

    summary = {
        "generated_at": now_utc_iso(),
        "contract_pack": pack.as_payload(),
        "openai_ablation_config": (
            openai_ablation_config.as_payload() if openai_ablation_config is not None else None
        ),
        "shipping_truth": {
            "default": pack.shipping_default,
            "note": "Shipping truth may remain narrower than development conformance truth.",
        },
        "surface_probes": [probe.as_payload() for probe in probes],
        "results": [result.as_payload() for result in results],
        "overall_divergence_class": classify_shared_divergence(results),
        "iteration_outcome": decide_iteration_outcome(
            results,
            shipping_default=pack.shipping_default,
        ),
    }
    summary["next_decision"] = _next_decision(
        summary["results"],
        summary["overall_divergence_class"],
        shipping_default=pack.shipping_default,
    )

    write_json(run_root / "summary.json", summary)
    write_text(run_root / "summary.md", render_summary_markdown(summary))
    if _is_full_brain_run(brains) and pack.contract_pack == ACTIVE_CONTRACT_PACK:
        write_json(CONFORMANCE_ROOT / "summary.latest.json", summary)
        write_text(CONFORMANCE_ROOT / "summary.latest.md", render_summary_markdown(summary))
    return summary


def build_preflight_report(*, brains: tuple[Brain, ...], contract_pack: ContractPack | None = None) -> dict[str, Any]:
    load_local_env_file()
    pack = contract_pack or active_contract_pack()
    probes = []
    for brain in brains:
        surface = strongest_native_surface(brain, pack)
        probes.append(preflight_surface(brain, surface).as_payload())
    return {
        "generated_at": now_utc_iso(),
        "contract_pack": pack.as_payload(),
        "surface_probes": probes,
    }


def render_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# Cortex Conformance: {summary['contract_pack']['contract_pack']}",
        "",
        f"- generated_at: `{summary['generated_at']}`",
        f"- shipping_default: `{summary['shipping_truth']['default']}`",
        f"- overall_divergence_class: `{summary['overall_divergence_class'] or 'none'}`",
        f"- iteration_outcome: `{summary['iteration_outcome']}`",
        f"- next_decision: `{summary['next_decision']}`",
        "",
        "| brain | surface | status | divergence | parseable | import | tests | repair | extraction | note |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in summary["results"]:
        tests_cell = "-"
        if result["pytest_passed"] is not None or result["pytest_failed"] is not None:
            tests_cell = f"{result['pytest_passed'] or 0}/{result['pytest_failed'] or 0}"
        parseable = "-" if result["parseable"] is None else str(result["parseable"])
        import_ok = "-" if result["import_smoke_ok"] is None else str(result["import_smoke_ok"])
        lines.append(
            "| "
            f"{result['brain']} | "
            f"{result['surface']} | "
            f"{result['status']} | "
            f"{result['divergence_class'] or '-'} | "
            f"{parseable} | "
            f"{import_ok} | "
            f"{tests_cell} | "
            f"{result['repair_conversion'] or '-'} | "
            f"{result['extraction_mode'] or '-'} | "
            f"{result['note'] or '-'} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/cortex_conformance.py",
        description="Run tri-brain Cortex-law conformance against the active contract pack.",
    )
    parser.add_argument(
        "--mode",
        choices=("preflight", "fast", "active", "reconcile-latest"),
        default="active",
    )
    parser.add_argument(
        "--contract-pack",
        default=ACTIVE_CONTRACT_PACK,
        choices=supported_contract_pack_names(),
    )
    parser.add_argument(
        "--brain",
        choices=("all", "openai", "claude", "gemini"),
        default="all",
    )
    parser.add_argument(
        "--max-repair-turns",
        type=int,
        choices=(0, 1),
        default=None,
    )
    parser.add_argument(
        "--visible-contract-binding",
        choices=("on", "off"),
        default="on",
    )
    parser.add_argument(
        "--verification-binding",
        choices=("on", "off"),
        default="on",
    )
    parser.add_argument(
        "--repair-turn",
        choices=("on", "off"),
        default="on",
    )
    parser.add_argument(
        "--repair-ticket-style",
        choices=("factual", "minimal"),
        default="factual",
    )
    parser.add_argument(
        "--visible-context-variant",
        choices=("default", "writable_files_only", "writable_files_plus_visible_tests"),
        default="default",
    )
    args = parser.parse_args(argv)

    brains: tuple[Brain, ...]
    if args.brain == "all":
        brains = ("openai", "claude", "gemini")
    else:
        brains = (args.brain,)  # type: ignore[assignment]

    if args.mode == "active" and "openai" in brains:
        require_openai_service_spend_approval(
            purpose="OpenAI active conformance on the service_api lane"
        )

    pack = contract_pack_by_name(args.contract_pack)
    openai_ablation_config = OpenAIHostControlAblationConfig(
        visible_contract_binding=args.visible_contract_binding,
        verification_binding=args.verification_binding,
        repair_turn=args.repair_turn,
        repair_ticket_style=args.repair_ticket_style,
        visible_context_variant=args.visible_context_variant,
    )

    if args.mode == "preflight":
        payload = build_preflight_report(brains=brains, contract_pack=pack)
    elif args.mode == "reconcile-latest":
        payload = reconcile_latest_summary()
    else:
        payload = run_active_conformance(
            brains=brains,
            contract_pack=pack,
            max_repair_turns_override=args.max_repair_turns,
            openai_ablation_config=openai_ablation_config,
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _run_conformance(
    *,
    brain: Brain,
    surface: Surface,
    contract_pack: ContractPack,
    run_root: Path,
    openai_ablation_config: OpenAIHostControlAblationConfig | None = None,
) -> ConformanceRunResult:
    if brain == "openai" and surface == "service_api":
        return _run_openai_service_conformance(
            contract_pack=contract_pack,
            run_root=run_root,
            openai_ablation_config=openai_ablation_config,
        )
    if brain == "claude" and surface == "operator_cli":
        return _run_claude_cli_conformance(contract_pack=contract_pack, run_root=run_root)
    if brain == "gemini" and surface == "operator_cli":
        return _run_gemini_cli_conformance(contract_pack=contract_pack, run_root=run_root)
    return ConformanceRunResult(
        brain=brain,
        surface=surface,
        contract_pack=contract_pack.contract_pack,
        status="unwired",
        note="No runner is implemented for this brain and surface.",
    )


def _run_openai_service_conformance(
    *,
    contract_pack: ContractPack,
    run_root: Path,
    openai_ablation_config: OpenAIHostControlAblationConfig | None = None,
) -> ConformanceRunResult:
    artifact_dir = run_root / "openai_service_api"
    request = OpenAIHostControlRequest(
        action_tag=_OPENAI_ACTION_TAG,
        model=_OPENAI_MODEL,
        input_text=contract_pack.prompt_text,
        work_contract=contract_pack.work_contract,
    )
    try:
        if openai_ablation_config is None or openai_ablation_config.is_default():
            result, session = run_openai_host_control(request)
        else:
            result, session = run_openai_host_control_experiment(
                request,
                ablation_config=openai_ablation_config,
            )
    except OpenAIResponseStreamTransportError as exc:
        failure_class = classify_failure(str(exc))
        divergence = "env_blocked" if failure_class in BLOCKING_FAILURE_CLASSES else "surface_wiring"
        status: ConformanceStatus = "env_blocked" if divergence == "env_blocked" else "divergent"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            artifact_dir / "transport_error.json",
            {"error": sanitize_text(str(exc)), "failure_class": failure_class},
        )
        return ConformanceRunResult(
            brain="openai",
            surface="service_api",
            contract_pack=contract_pack.contract_pack,
            status=status,
            divergence_class=divergence,
            note=sanitize_text(str(exc)),
            transport_failure_class=failure_class,
            artifact_relpath=_artifact_relpath(artifact_dir),
        )

    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        artifact_dir / "result.json",
        {
            "request": request.as_payload(),
            "result": result.as_payload(),
            "session": session.as_summary(),
        },
    )
    if result.verification is None:
        raise RuntimeError("OpenAI verified-work conformance expected verification output.")
    return _result_from_verification(
        brain="openai",
        surface="service_api",
        contract_pack=contract_pack.contract_pack,
        outcome=result.verification,
        attempt_count=result.attempt_count or 1,
        artifact_relpath=_artifact_relpath(artifact_dir),
        note=f"runtime move: {session.next_recommended_move}",
    )


def _run_claude_cli_conformance(
    *,
    contract_pack: ContractPack,
    run_root: Path,
) -> ConformanceRunResult:
    artifact_dir = run_root / "claude_operator_cli"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    instructions = build_verified_work_instructions(contract_pack.work_contract)
    with _stage_contract_pack_workspace(
        contract_pack,
        prefix="cortex-conformance-claude-",
    ) as workspace:
        initial = run_command(
            [
                "claude",
                "-p",
                contract_pack.prompt_text,
                "--output-format",
                "json",
                "--model",
                _CLAUDE_MODEL,
                "--permission-mode",
                "bypassPermissions",
                "--tools",
                _CLAUDE_READ_ONLY_TOOLS,
                "--append-system-prompt",
                instructions,
            ],
            cwd=workspace,
            timeout_seconds=300.0,
        )
        write_json(artifact_dir / "attempt1.json", initial)
        result = _evaluate_operator_attempt(
            provider="claude",
            command_result=initial,
            work_contract=contract_pack.work_contract,
        )
        if result["status"] == "env_blocked":
            return ConformanceRunResult(
                brain="claude",
                surface="operator_cli",
                contract_pack=contract_pack.contract_pack,
                status="env_blocked",
                divergence_class="env_blocked",
                note=result["note"],
                transport_failure_class=result["transport_failure_class"],
                artifact_relpath=_artifact_relpath(artifact_dir),
            )
        first_outcome = result["verification"]
        assert isinstance(first_outcome, VerificationOutcome)
        first_session_id = result["session_id"]
        final_outcome = first_outcome
        attempt_count = 1
        final_extraction_mode = result["extraction_mode"]
        final_note = result["note"]
        if first_outcome.failure_class in {"output_invalid", "import_smoke_failed", "test_failed"}:
            if not isinstance(first_session_id, str) or not first_session_id.strip():
                return ConformanceRunResult(
                    brain="claude",
                    surface="operator_cli",
                    contract_pack=contract_pack.contract_pack,
                    status="divergent",
                    divergence_class="surface_wiring",
                    first_attempt_status=first_outcome.status,
                    first_attempt_failure_class=first_outcome.failure_class,
                    final_failure_class=first_outcome.failure_class,
                    verification_status=first_outcome.status,
                    parseable=first_outcome.parse_error is None,
                    import_smoke_ok=first_outcome.import_smoke_ok,
                    pytest_passed=first_outcome.pytest_passed,
                    pytest_failed=first_outcome.pytest_failed,
                    attempt_count=1,
                    repair_conversion="failed_without_repair",
                    extraction_mode=result["extraction_mode"],
                    note="Claude operator surface did not return a resumable session id.",
                    artifact_relpath=_artifact_relpath(artifact_dir),
                )
            repair_ticket = build_verified_work_repair_ticket(first_outcome)
            resumed = run_command(
                [
                    "claude",
                    "-r",
                    first_session_id,
                    "-p",
                    repair_ticket,
                    "--output-format",
                    "json",
                    "--model",
                    _CLAUDE_MODEL,
                    "--permission-mode",
                    "bypassPermissions",
                    "--tools",
                    _CLAUDE_READ_ONLY_TOOLS,
                    "--append-system-prompt",
                    instructions,
                ],
                cwd=workspace,
                timeout_seconds=300.0,
            )
            write_json(artifact_dir / "attempt2.json", resumed)
            resumed_result = _evaluate_operator_attempt(
                provider="claude",
                command_result=resumed,
                work_contract=contract_pack.work_contract,
            )
            if resumed_result["status"] == "env_blocked":
                return ConformanceRunResult(
                    brain="claude",
                    surface="operator_cli",
                    contract_pack=contract_pack.contract_pack,
                    status="env_blocked",
                    divergence_class="env_blocked",
                    note=resumed_result["note"],
                    transport_failure_class=resumed_result["transport_failure_class"],
                    artifact_relpath=_artifact_relpath(artifact_dir),
                )
            final_outcome = resumed_result["verification"]
            assert isinstance(final_outcome, VerificationOutcome)
            attempt_count = 2
            final_extraction_mode = resumed_result["extraction_mode"]
            final_note = resumed_result["note"]

    return _result_from_verification(
        brain="claude",
        surface="operator_cli",
        contract_pack=contract_pack.contract_pack,
        outcome=final_outcome,
        attempt_count=attempt_count,
        first_outcome=first_outcome,
        extraction_mode=final_extraction_mode,
        artifact_relpath=_artifact_relpath(artifact_dir),
        note=final_note,
    )


def _run_gemini_cli_conformance(
    *,
    contract_pack: ContractPack,
    run_root: Path,
) -> ConformanceRunResult:
    artifact_dir = run_root / "gemini_operator_cli"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    with _stage_contract_pack_workspace(
        contract_pack,
        prefix="cortex-conformance-gemini-",
    ) as workspace:
        initial_prompt = _render_combined_operator_prompt(
            task_prompt=contract_pack.prompt_text,
            instructions=build_verified_work_instructions(contract_pack.work_contract),
        )
        initial = run_command(
            [
                "gemini",
                "-p",
                initial_prompt,
                "-o",
                "json",
                "--approval-mode",
                "yolo",
            ],
            cwd=workspace,
            timeout_seconds=300.0,
        )
        write_json(artifact_dir / "attempt1.json", initial)
        result = _evaluate_operator_attempt(
            provider="gemini",
            command_result=initial,
            work_contract=contract_pack.work_contract,
        )
        if result["status"] == "env_blocked":
            return ConformanceRunResult(
                brain="gemini",
                surface="operator_cli",
                contract_pack=contract_pack.contract_pack,
                status="env_blocked",
                divergence_class="env_blocked",
                note=result["note"],
                transport_failure_class=result["transport_failure_class"],
                artifact_relpath=_artifact_relpath(artifact_dir),
            )
        first_outcome = result["verification"]
        assert isinstance(first_outcome, VerificationOutcome)
        final_outcome = first_outcome
        attempt_count = 1
        final_extraction_mode = result["extraction_mode"]
        final_note = result["note"]
        if first_outcome.failure_class in {"output_invalid", "import_smoke_failed", "test_failed"}:
            repair_ticket = _render_combined_operator_prompt(
                task_prompt=build_verified_work_repair_ticket(first_outcome),
                instructions=build_verified_work_instructions(contract_pack.work_contract),
            )
            resumed = run_command(
                [
                    "gemini",
                    "--resume",
                    "latest",
                    "-p",
                    repair_ticket,
                    "-o",
                    "json",
                    "--approval-mode",
                    "yolo",
                ],
                cwd=workspace,
                timeout_seconds=300.0,
            )
            write_json(artifact_dir / "attempt2.json", resumed)
            resumed_result = _evaluate_operator_attempt(
                provider="gemini",
                command_result=resumed,
                work_contract=contract_pack.work_contract,
            )
            if resumed_result["status"] == "env_blocked":
                return ConformanceRunResult(
                    brain="gemini",
                    surface="operator_cli",
                    contract_pack=contract_pack.contract_pack,
                    status="env_blocked",
                    divergence_class="env_blocked",
                    note=resumed_result["note"],
                    transport_failure_class=resumed_result["transport_failure_class"],
                    artifact_relpath=_artifact_relpath(artifact_dir),
                )
            final_outcome = resumed_result["verification"]
            assert isinstance(final_outcome, VerificationOutcome)
            attempt_count = 2
            final_extraction_mode = resumed_result["extraction_mode"]
            final_note = resumed_result["note"]

    return _result_from_verification(
        brain="gemini",
        surface="operator_cli",
        contract_pack=contract_pack.contract_pack,
        outcome=final_outcome,
        attempt_count=attempt_count,
        first_outcome=first_outcome,
        extraction_mode=final_extraction_mode,
        artifact_relpath=_artifact_relpath(artifact_dir),
        note=final_note,
    )


def _evaluate_operator_attempt(
    *,
    provider: Literal["claude", "gemini"],
    command_result: dict[str, Any],
    work_contract: WorkContract,
) -> dict[str, Any]:
    raw_stdout = str(command_result.get("stdout", "") or "")
    raw_stderr = str(command_result.get("stderr", "") or "")
    failure_class = classify_failure(f"{raw_stdout}\n{raw_stderr}")
    records, extraction_mode = parse_json_records(raw_stdout)
    if command_result["exit_code"] == 124 and not records and not raw_stdout.strip():
        return {
            "status": "env_blocked",
            "transport_failure_class": "operator_timeout",
            "note": "operator timed out before returning structured output",
        }
    if command_result["exit_code"] != 0 and (
        failure_class in BLOCKING_FAILURE_CLASSES or failure_class is not None
    ):
        return {
            "status": "env_blocked",
            "transport_failure_class": failure_class,
            "note": sanitize_text((raw_stderr or raw_stdout).strip() or "transport blocked"),
        }

    if provider == "claude":
        session_id = _extract_session_id_from_operator_stdout("claude", raw_stdout)
    else:
        session_id = _extract_session_id_from_operator_stdout("gemini", raw_stdout)
    result_text = extract_result_text(records, raw_stdout)
    _, verification = verify_verified_work_result(result_text, work_contract)
    note = sanitize_text(raw_stderr.strip() or "executed")
    if command_result["exit_code"] == 124:
        note = sanitize_text(f"{note}\nstructured output captured before operator timeout")
    return {
        "status": "executed",
        "verification": verification,
        "session_id": session_id,
        "extraction_mode": extraction_mode,
        "note": note,
    }


def _result_from_verification(
    *,
    brain: Brain,
    surface: Surface,
    contract_pack: str,
    outcome: VerificationOutcome,
    attempt_count: int,
    artifact_relpath: str,
    note: str | None = None,
    first_outcome: VerificationOutcome | None = None,
    extraction_mode: str | None = None,
) -> ConformanceRunResult:
    status, divergence_class = classify_outcome_divergence(surface=surface, outcome=outcome)
    return ConformanceRunResult(
        brain=brain,
        surface=surface,
        contract_pack=contract_pack,
        status=status,
        divergence_class=divergence_class,
        first_attempt_status=(first_outcome.status if first_outcome is not None else outcome.status),
        first_attempt_failure_class=(
            first_outcome.failure_class if first_outcome is not None else outcome.failure_class
        ),
        final_failure_class=outcome.failure_class,
        verification_status=outcome.status,
        parseable=outcome.parse_error is None,
        import_smoke_ok=outcome.import_smoke_ok,
        pytest_passed=outcome.pytest_passed,
        pytest_failed=outcome.pytest_failed,
        attempt_count=attempt_count,
        repair_conversion=_repair_conversion(outcome=outcome, attempt_count=attempt_count),
        extraction_mode=extraction_mode,
        note=note,
        artifact_relpath=artifact_relpath,
    )


def _repair_conversion(*, outcome: VerificationOutcome, attempt_count: int) -> str:
    if attempt_count == 1 and outcome.status == "passed":
        return "passed_without_repair"
    if attempt_count == 1 and outcome.status == "blocked":
        return "blocked_without_repair"
    if attempt_count == 1:
        return "failed_without_repair"
    if outcome.status == "passed":
        return "recovered_after_repair"
    return "repair_attempt_no_recovery"


def _artifact_relpath(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _render_combined_operator_prompt(*, task_prompt: str, instructions: str) -> str:
    return (
        f"{task_prompt}\n\n"
        "Follow this exact output contract:\n"
        f"{instructions}"
    )


def _extract_session_id_from_operator_stdout(provider: Literal["claude", "gemini"], raw_stdout: str) -> str | None:
    records, _extraction_mode = parse_json_records(raw_stdout)
    for record in reversed(records):
        session_id = record.get("session_id")
        if isinstance(session_id, str) and session_id.strip():
            return session_id.strip()
        if provider == "gemini":
            maybe_session = record.get("sessionId")
            if isinstance(maybe_session, str) and maybe_session.strip():
                return maybe_session.strip()
    return None


def _next_decision(
    results: list[dict[str, Any]],
    overall_divergence_class: str | None,
    *,
    shipping_default: str,
) -> str:
    if overall_divergence_class == "cortex_law":
        return "revise_cortex_law"
    shipping_brain, _shipping_surface = shipping_default.split(":", 1)
    non_shipping_divergence = [
        result
        for result in results
        if result["brain"] != shipping_brain
        and result["status"] == "divergent"
        and result["divergence_class"] in {"brain_wiring", "surface_wiring"}
    ]
    if non_shipping_divergence:
        return "fix_wiring_only"
    shipping_result = next(
        (result for result in results if result["brain"] == shipping_brain),
        None,
    )
    if shipping_result is not None and shipping_result["status"] in {"partial", "divergent"}:
        return "improve_shipping_default"
    non_shipping_partial = [
        result
        for result in results
        if result["brain"] != shipping_brain
        and result["status"] == "partial"
        and result["divergence_class"] in {"brain_wiring", "surface_wiring"}
    ]
    if non_shipping_partial:
        return "fix_wiring_only"
    shipping_env_blocked = shipping_result is not None and shipping_result["status"] == "env_blocked"
    if shipping_env_blocked:
        return "clear_env_blocks"
    if any(result["status"] == "env_blocked" for result in results):
        return "promote"
    return "promote"


def reconcile_latest_summary() -> ConformanceSummary:
    candidate = _find_latest_full_summary(
        preferred_next_decision=_accepted_ct2_next_decision(),
        contract_pack_name=ACTIVE_CONTRACT_PACK,
    )
    if candidate is None:
        raise RuntimeError(
            "No surviving full tri-brain conformance summary exists under "
            f"{CONFORMANCE_ROOT}."
        )
    write_json(CONFORMANCE_ROOT / "summary.latest.json", candidate)
    write_text(CONFORMANCE_ROOT / "summary.latest.md", render_summary_markdown(candidate))
    return candidate


def _find_latest_full_summary(
    *,
    preferred_next_decision: str | None = None,
    contract_pack_name: str | None = None,
) -> ConformanceSummary | None:
    run_dirs = sorted(
        (path for path in CONFORMANCE_ROOT.glob("run_*") if path.is_dir()),
        reverse=True,
    )
    fallback: ConformanceSummary | None = None
    for run_dir in run_dirs:
        summary_path = run_dir / "summary.json"
        if not summary_path.exists():
            continue
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if contract_pack_name is not None and not _summary_matches_contract_pack(
            summary,
            contract_pack_name=contract_pack_name,
        ):
            continue
        if not _summary_is_full_run(summary):
            continue
        if not _summary_artifacts_exist(summary):
            continue
        if fallback is None:
            fallback = summary
        if preferred_next_decision is None:
            return summary
        if summary.get("next_decision") == preferred_next_decision:
            return summary
    return fallback


def _accepted_ct2_next_decision() -> str | None:
    return accepted_conformance_next_decision()


def _is_full_brain_run(brains: tuple[Brain, ...]) -> bool:
    return tuple(sorted(brains)) == tuple(sorted(_ALL_BRAINS))


def _summary_is_full_run(summary: Mapping[str, Any]) -> bool:
    results = summary.get("results")
    if not isinstance(results, list):
        return False
    brains = {
        result.get("brain")
        for result in results
        if isinstance(result, Mapping) and isinstance(result.get("brain"), str)
    }
    return brains == set(_ALL_BRAINS)


def _summary_artifacts_exist(summary: Mapping[str, Any]) -> bool:
    results = summary.get("results")
    if not isinstance(results, list):
        return False
    for result in results:
        if not isinstance(result, Mapping):
            return False
        artifact_relpath = result.get("artifact_relpath")
        if artifact_relpath is None:
            continue
        if not isinstance(artifact_relpath, str) or not artifact_relpath.strip():
            return False
        if not (ROOT / artifact_relpath).exists():
            return False
    return True


def _summary_matches_contract_pack(
    summary: Mapping[str, Any],
    *,
    contract_pack_name: str,
) -> bool:
    contract_pack = summary.get("contract_pack")
    if not isinstance(contract_pack, Mapping):
        return False
    return contract_pack.get("contract_pack") == contract_pack_name


__all__ = [
    "ACTIVE_CONTRACT_PACK",
    "ContractPack",
    "ConformanceRunResult",
    "DivergenceClass",
    "FEATURE_FLAGS_CONTRACT_PACK",
    "NORMALIZE_PORT_CONTRACT_PACK",
    "TrainCharter",
    "active_contract_pack",
    "build_preflight_report",
    "classify_outcome_divergence",
    "classify_shared_divergence",
    "contract_pack_by_name",
    "decide_iteration_outcome",
    "reconcile_latest_summary",
    "preflight_surface",
    "render_summary_markdown",
    "run_active_conformance",
    "strongest_native_surface",
    "supported_contract_pack_names",
]


if __name__ == "__main__":
    raise SystemExit(main())
