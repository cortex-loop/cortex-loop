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

from cortex.runtime.openai_host_control import (  # noqa: E402
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
from cortex.sre.preservation import derive_preservation_state  # noqa: E402
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
from lab.openai_operator_cli import (  # noqa: E402
    isolated_codex_home_env,
    run_openai_operator_resumed_turn,
    run_openai_operator_single_turn,
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
REPAIR_PRESSURE_ROOT = CONFORMANCE_ROOT / "repair_pressure"
PHASE_GATES_PATH = ROOT / "docs" / "internal" / "CORTEX_V2_PHASE_GATES_2.md"
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
_OPENAI_OPERATOR_MODEL = "gpt-5.3-codex"
_CLAUDE_MODEL = "claude-sonnet-4-6"
_CLAUDE_READ_ONLY_TOOLS = "Read,Glob,Grep,LS"
OPENAI_PRODUCT_RUNTIME_CLAIM = "openai:service_api"
OPENAI_ACTIVE_PROVING_DEFAULT = "openai:operator_cli"
_REPAIRABLE_FAILURE_CLASSES = frozenset({"output_invalid", "import_smoke_failed", "test_failed"})
_SURFACE_ORDER: dict[Brain, tuple[Surface, ...]] = {
    "openai": ("operator_cli", "service_api"),
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
    product_runtime_claim: str
    active_proving_default: str

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
        for label, value in (
            ("product_runtime_claim", self.product_runtime_claim),
            ("active_proving_default", self.active_proving_default),
        ):
            if not (isinstance(value, str) and value.strip()):
                raise ValueError(f"ContractPack.{label} must be non-empty after trimming.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "contract_pack": self.contract_pack,
            "prompt_text": self.prompt_text,
            "workspace_template_relpath": self.workspace_template_relpath,
            "work_contract": self.work_contract.as_payload(),
            "train_charter": self.train_charter.as_payload(),
            "product_runtime_claim": self.product_runtime_claim,
            "active_proving_default": self.active_proving_default,
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
                primary_proving_wiring=OPENAI_ACTIVE_PROVING_DEFAULT,
                conformance_surfaces=(
                    OPENAI_ACTIVE_PROVING_DEFAULT,
                    "claude:operator_cli",
                    "gemini:operator_cli",
                ),
                kill_criteria=(
                    "cut a new Cortex-law addition if it does not improve the active divergence classification after two iterations",
                    "do not widen shipping truth from conformance-only results",
                ),
            ),
            product_runtime_claim=OPENAI_PRODUCT_RUNTIME_CLAIM,
            active_proving_default=OPENAI_ACTIVE_PROVING_DEFAULT,
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
                primary_proving_wiring=OPENAI_ACTIVE_PROVING_DEFAULT,
                conformance_surfaces=(
                    OPENAI_ACTIVE_PROVING_DEFAULT,
                    "claude:operator_cli",
                    "gemini:operator_cli",
                ),
                kill_criteria=(
                    "cut the second-pack breadth slice if repeat-stable OpenAI conformance does not improve within the locked iteration budget",
                    "do not repurpose the bookmarks summary.latest anchor while breadth evidence is still being earned",
                ),
            ),
            product_runtime_claim=OPENAI_PRODUCT_RUNTIME_CLAIM,
            active_proving_default=OPENAI_ACTIVE_PROVING_DEFAULT,
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
                primary_proving_wiring=OPENAI_ACTIVE_PROVING_DEFAULT,
                conformance_surfaces=(
                    OPENAI_ACTIVE_PROVING_DEFAULT,
                    "claude:operator_cli",
                    "gemini:operator_cli",
                ),
                kill_criteria=(
                    "cut the third-pack breadth slice if repeat-stable OpenAI conformance does not improve within the locked iteration budget",
                    "do not repurpose the bookmarks summary.latest anchor while breadth evidence is still being earned",
                ),
            ),
            product_runtime_claim=OPENAI_PRODUCT_RUNTIME_CLAIM,
            active_proving_default=OPENAI_ACTIVE_PROVING_DEFAULT,
        )
    raise ValueError(f"Unsupported contract pack: {name}")


def supported_contract_pack_names() -> tuple[str, ...]:
    return (
        ACTIVE_CONTRACT_PACK,
        NORMALIZE_PORT_CONTRACT_PACK,
        FEATURE_FLAGS_CONTRACT_PACK,
    )


def strongest_native_surface(
    brain: Brain,
    contract_pack: ContractPack,
    *,
    openai_surface_override: Surface | None = None,
) -> Surface:
    if brain == "openai":
        if openai_surface_override is not None:
            return openai_surface_override
        _proving_brain, proving_surface = contract_pack.active_proving_default.split(":", 1)
        return proving_surface  # type: ignore[return-value]
    return _SURFACE_ORDER[brain][0]


def _render_full_files_result(file_map: Mapping[str, str]) -> str:
    blocks: list[str] = []
    for path in sorted(file_map):
        blocks.append(f"=== FILE: {path} ===")
        blocks.append(file_map[path])
        blocks.append("=== END FILE ===")
    return "\n".join(blocks)


def _materialize_file_map(workspace: Path, file_map: Mapping[str, str]) -> None:
    for relative_path, content in file_map.items():
        destination = workspace / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def _inject_parse_invalid_output(result_text: str) -> str:
    return f"unexpected text outside protocol blocks\n{result_text.strip()}"


def _inject_import_smoke_failure(source_text: str) -> str:
    return f"{source_text.rstrip()}\n\nBROKEN = (\n"


def _inject_test_failure(
    *,
    contract_pack: ContractPack,
    source_text: str,
) -> tuple[str, str]:
    if contract_pack.contract_pack == NORMALIZE_PORT_CONTRACT_PACK:
        return (
            "src/normalize_port.py",
            f"{source_text.rstrip()}\n\n"
            "def normalize_port(value: int | str) -> int:\n"
            "    return 0\n",
        )
    if contract_pack.contract_pack == FEATURE_FLAGS_CONTRACT_PACK:
        return (
            "src/feature_flags/evaluator.py",
            f"{source_text.rstrip()}\n\n"
            "def is_flag_active(*_args, **_kwargs):\n"
            "    return False\n",
        )
    raise ValueError(
        "test-failure repair pressure is only defined for normalize-port and feature-flags packs."
    )


def _repair_pressure_failure_class(contract_pack: ContractPack) -> str:
    if contract_pack.contract_pack == ACTIVE_CONTRACT_PACK:
        return "output_invalid"
    if contract_pack.contract_pack == NORMALIZE_PORT_CONTRACT_PACK:
        return "import_smoke_failed"
    if contract_pack.contract_pack == FEATURE_FLAGS_CONTRACT_PACK:
        return "test_failed"
    raise ValueError(f"Unsupported repair-pressure contract pack: {contract_pack.contract_pack}")


def _default_repair_pressure_target_path(contract_pack: ContractPack) -> str | None:
    if contract_pack.contract_pack == NORMALIZE_PORT_CONTRACT_PACK:
        return "src/normalize_port.py"
    if contract_pack.contract_pack == FEATURE_FLAGS_CONTRACT_PACK:
        return "src/feature_flags/evaluator.py"
    return None


def _narrowed_repair_contract(
    work_contract: WorkContract,
    lawful_repair_surface: frozenset[str],
) -> WorkContract:
    narrowed_paths = tuple(
        path for path in work_contract.allowed_write_paths if path in lawful_repair_surface
    )
    if not narrowed_paths:
        raise ValueError("repair proof requires a non-empty lawful_repair_surface.")
    return replace(
        work_contract,
        allowed_write_paths=narrowed_paths,
        max_repair_turns=0,
    )


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
    if brain == "openai" and surface == "operator_cli":
        if not command_exists("codex"):
            return SurfaceProbe(
                brain=brain,
                surface=surface,
                status="env_blocked",
                reason="codex CLI is not installed.",
            )
        if (Path.home() / ".codex" / "auth.json").exists():
            return SurfaceProbe(
                brain=brain,
                surface=surface,
                status="conformant",
                reason="OpenAI operator surface auth is present.",
            )
        return SurfaceProbe(
            brain=brain,
            surface=surface,
            status="env_blocked",
            reason="~/.codex/auth.json is missing.",
        )
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
    active_proving_default: str,
) -> str:
    primary_brain, _primary_surface = active_proving_default.split(":", 1)
    primary_result = next(
        (result for result in results if result.brain == primary_brain),
        None,
    )
    if primary_result is not None and primary_result.status in {"partial", "divergent"}:
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
    openai_surface_override: Surface | None = None,
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
        surface = strongest_native_surface(
            brain,
            pack,
            openai_surface_override=openai_surface_override,
        )
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
        "product_truth": {
            "runtime_claim": pack.product_runtime_claim,
            "note": "Product/runtime truth remains separate from the active proving default.",
        },
        "proving_truth": {
            "active_default": pack.active_proving_default,
            "note": "Development conformance follows the active proving lane unless explicitly overridden.",
        },
        "surface_probes": [probe.as_payload() for probe in probes],
        "results": [result.as_payload() for result in results],
        "overall_divergence_class": classify_shared_divergence(results),
        "iteration_outcome": decide_iteration_outcome(
            results,
            active_proving_default=pack.active_proving_default,
        ),
    }
    summary["next_decision"] = _next_decision(
        summary["results"],
        summary["overall_divergence_class"],
        active_proving_default=pack.active_proving_default,
    )

    write_json(run_root / "summary.json", summary)
    write_text(run_root / "summary.md", render_summary_markdown(summary))
    if _is_full_brain_run(brains) and pack.contract_pack == ACTIVE_CONTRACT_PACK:
        write_json(CONFORMANCE_ROOT / "summary.latest.json", summary)
        write_text(CONFORMANCE_ROOT / "summary.latest.md", render_summary_markdown(summary))
    return summary


def build_preflight_report(
    *,
    brains: tuple[Brain, ...],
    contract_pack: ContractPack | None = None,
    openai_surface_override: Surface | None = None,
) -> dict[str, Any]:
    load_local_env_file()
    pack = contract_pack or active_contract_pack()
    probes = []
    for brain in brains:
        surface = strongest_native_surface(
            brain,
            pack,
            openai_surface_override=openai_surface_override,
        )
        probes.append(preflight_surface(brain, surface).as_payload())
    return {
        "generated_at": now_utc_iso(),
        "contract_pack": pack.as_payload(),
        "surface_probes": probes,
    }


def render_summary_markdown(summary: dict[str, Any]) -> str:
    product_runtime_claim = _summary_product_runtime_claim(summary) or "unknown"
    active_proving_default = _summary_active_proving_default(summary) or "unknown"
    lines = [
        f"# Cortex Conformance: {summary['contract_pack']['contract_pack']}",
        "",
        f"- generated_at: `{summary['generated_at']}`",
        f"- product_runtime_claim: `{product_runtime_claim}`",
        f"- active_proving_default: `{active_proving_default}`",
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


def render_repair_pressure_markdown(summary: dict[str, Any]) -> str:
    result = summary.get("result") if isinstance(summary.get("result"), Mapping) else None
    repair_case = (
        summary.get("repair_pressure_case")
        if isinstance(summary.get("repair_pressure_case"), Mapping)
        else {}
    )
    audit = summary.get("repair_audit") if isinstance(summary.get("repair_audit"), Mapping) else {}
    lines = [
        f"# OpenAI operator_cli repair pressure: {summary['contract_pack']['contract_pack']}",
        "",
        f"- generated_at: `{summary['generated_at']}`",
        f"- status: `{summary['status']}`",
        f"- proof_surface: `{summary['proof_surface']}`",
        f"- pressure_source: `{repair_case.get('pressure_source', 'unknown')}`",
        f"- failure_class: `{repair_case.get('failure_class', 'unknown')}`",
        f"- target_path: `{repair_case.get('target_path') or '<none>'}`",
        "",
        "| audit | value |",
        "| --- | --- |",
    ]
    for key in (
        "task_anchor_present",
        "preservation_state_present",
        "repair_contract_matches_surface",
        "repair_ticket_mechanical_only",
        "attempt2_paths_within_surface",
        "preserved_overlay_reused",
    ):
        if key in audit:
            lines.append(f"| {key} | {audit[key]} |")
    if result is not None:
        lines.extend(
            [
                "",
                "| brain | surface | status | repair | note |",
                "| --- | --- | --- | --- | --- |",
                "| "
                f"{result.get('brain', '-')} | "
                f"{result.get('surface', '-')} | "
                f"{result.get('status', '-')} | "
                f"{result.get('repair_conversion', '-')} | "
                f"{result.get('note', '-') or '-'} |",
            ]
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/cortex_conformance.py",
        description="Run tri-brain Cortex-law conformance against the active contract pack.",
    )
    parser.add_argument(
        "--mode",
        choices=("preflight", "fast", "active", "repair-pressure", "reconcile-latest"),
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
        "--openai-surface",
        choices=("service_api", "operator_cli"),
        default=None,
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

    if (
        args.mode == "active"
        and "openai" in brains
        and strongest_native_surface(
            "openai",
            contract_pack_by_name(args.contract_pack),
            openai_surface_override=args.openai_surface,
        )
        == "service_api"
    ):
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
        payload = build_preflight_report(
            brains=brains,
            contract_pack=pack,
            openai_surface_override=args.openai_surface,
        )
    elif args.mode == "repair-pressure":
        if args.brain not in {"all", "openai"}:
            raise SystemExit("repair-pressure mode currently supports only --brain openai.")
        requested_surface = strongest_native_surface(
            "openai",
            pack,
            openai_surface_override=args.openai_surface,
        )
        if requested_surface != "operator_cli":
            raise SystemExit("repair-pressure mode requires OpenAI operator_cli.")
        payload = run_openai_operator_cli_repair_pressure(contract_pack=pack)
    elif args.mode == "reconcile-latest":
        payload = reconcile_latest_summary()
    else:
        payload = run_active_conformance(
            brains=brains,
            contract_pack=pack,
            max_repair_turns_override=args.max_repair_turns,
            openai_surface_override=args.openai_surface,
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
    if brain == "openai" and surface == "operator_cli":
        return _run_openai_operator_cli_conformance(
            contract_pack=contract_pack,
            run_root=run_root,
        )
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


def _write_openai_repair_artifacts(
    *,
    artifact_dir: Path,
    preservation_state: Any,
    repair_contract: WorkContract,
    repair_ticket: str,
    repair_prompt: str,
) -> None:
    write_json(artifact_dir / "preservation_state.json", preservation_state.as_payload())
    write_json(artifact_dir / "repair_contract.json", repair_contract.as_payload())
    write_text(artifact_dir / "repair_ticket.txt", repair_ticket)
    write_text(artifact_dir / "repair_prompt.txt", repair_prompt)


def _run_openai_operator_cli_resume_repair(
    *,
    artifact_dir: Path,
    workspace: Path,
    env: dict[str, str],
    model: str,
    thread_id: str,
    preservation_state: Any,
    preserved_file_map: dict[str, str] | None,
    verifier_contract: WorkContract,
) -> dict[str, Any]:
    repair_contract = _narrowed_repair_contract(
        verifier_contract,
        preservation_state.lawful_repair_surface,
    )
    repair_ticket = build_verified_work_repair_ticket(preservation_state)
    repair_prompt = _render_combined_operator_prompt(
        task_prompt=repair_ticket,
        instructions=build_verified_work_instructions(repair_contract),
    )
    _write_openai_repair_artifacts(
        artifact_dir=artifact_dir,
        preservation_state=preservation_state,
        repair_contract=repair_contract,
        repair_ticket=repair_ticket,
        repair_prompt=repair_prompt,
    )
    resumed = run_openai_operator_resumed_turn(
        project_root=workspace,
        prompt=repair_prompt,
        model=model,
        thread_id=thread_id,
        stderr_path=artifact_dir / "attempt2.stderr.log",
        env=env,
    )
    write_json(artifact_dir / "attempt2.json", resumed)
    resumed_result = _evaluate_openai_operator_attempt(
        operator_turn=resumed,
        work_contract=repair_contract,
        preserved_file_map=preserved_file_map,
        verifier_contract=verifier_contract,
    )
    resumed_result["repair_contract"] = repair_contract
    resumed_result["repair_ticket"] = repair_ticket
    resumed_result["repair_prompt"] = repair_prompt
    return resumed_result


def _build_openai_repair_pressure_case(
    *,
    contract_pack: ContractPack,
    workspace: Path,
    initial_output_text: str | None,
    initial_file_map: dict[str, str] | None,
    initial_outcome: VerificationOutcome,
) -> dict[str, Any]:
    if initial_file_map is not None:
        _materialize_file_map(workspace, initial_file_map)
    if initial_outcome.failure_class in _REPAIRABLE_FAILURE_CLASSES:
        return {
            "pressure_source": "natural",
            "failure_class": initial_outcome.failure_class,
            "target_path": _default_repair_pressure_target_path(contract_pack),
            "effective_result_text": initial_output_text or "",
            "effective_file_map": initial_file_map,
            "effective_outcome": initial_outcome,
            "description": "first attempt already exercised a repairable operator_cli failure.",
        }
    if initial_outcome.status != "passed":
        raise RuntimeError(
            "repair-pressure proof requires a passing or repairable first attempt."
        )
    if initial_file_map is None:
        raise RuntimeError(
            "repair-pressure proof requires a parsed first-attempt file map."
        )

    failure_class = _repair_pressure_failure_class(contract_pack)
    target_path = _default_repair_pressure_target_path(contract_pack)
    if failure_class == "output_invalid":
        effective_result_text = _inject_parse_invalid_output(
            initial_output_text or _render_full_files_result(initial_file_map)
        )
        effective_file_map, effective_outcome = verify_verified_work_result(
            effective_result_text,
            contract_pack.work_contract,
        )
    else:
        if target_path is None or target_path not in initial_file_map:
            raise RuntimeError(
                "repair-pressure proof requires the expected target path in the first-attempt file map."
            )
        faulted_file_map = dict(initial_file_map)
        if failure_class == "import_smoke_failed":
            faulted_file_map[target_path] = _inject_import_smoke_failure(
                faulted_file_map[target_path]
            )
        else:
            _actual_target, mutated = _inject_test_failure(
                contract_pack=contract_pack,
                source_text=faulted_file_map[target_path],
            )
            faulted_file_map[target_path] = mutated
        _materialize_file_map(workspace, faulted_file_map)
        effective_result_text = _render_full_files_result(faulted_file_map)
        effective_file_map, effective_outcome = verify_verified_work_result(
            effective_result_text,
            contract_pack.work_contract,
        )

    if effective_outcome.failure_class != failure_class:
        raise RuntimeError(
            "repair-pressure injection did not yield the expected verifier-visible failure "
            f"({failure_class}); got {effective_outcome.failure_class or '<none>'}."
        )
    return {
        "pressure_source": "injected",
        "failure_class": failure_class,
        "target_path": target_path,
        "effective_result_text": effective_result_text,
        "effective_file_map": effective_file_map,
        "effective_outcome": effective_outcome,
        "description": (
            "maintainer-only repair-pressure case injected after a clean first attempt to "
            "exercise the preservation-aware repair branch."
        ),
    }


def _run_openai_operator_cli_conformance(
    *,
    contract_pack: ContractPack,
    run_root: Path,
) -> ConformanceRunResult:
    artifact_dir = run_root / "openai_operator_cli"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    instructions = build_verified_work_instructions(contract_pack.work_contract)
    with _stage_contract_pack_workspace(
        contract_pack,
        prefix="cortex-conformance-openai-",
    ) as workspace, isolated_codex_home_env() as env:
        initial_prompt = _render_combined_operator_prompt(
            task_prompt=contract_pack.prompt_text,
            instructions=instructions,
        )
        initial = run_openai_operator_single_turn(
            project_root=workspace,
            prompt=initial_prompt,
            scenario_id=f"conformance_{contract_pack.contract_pack}_attempt1",
            stderr_path=artifact_dir / "attempt1.stderr.log",
            ephemeral=False,
            env=env,
            model=_OPENAI_OPERATOR_MODEL,
        )
        write_json(artifact_dir / "attempt1.json", initial)
        result = _evaluate_openai_operator_attempt(
            operator_turn=initial,
            work_contract=contract_pack.work_contract,
        )
        if result["status"] == "env_blocked":
            return ConformanceRunResult(
                brain="openai",
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
        first_file_map = result.get("file_map")
        if isinstance(first_file_map, Mapping):
            first_file_map = {
                str(path): str(content) for path, content in first_file_map.items()
            }
        final_outcome = first_outcome
        attempt_count = 1
        final_note = result["note"]
        final_extraction_mode = result["extraction_mode"]
        if first_outcome.failure_class in _REPAIRABLE_FAILURE_CLASSES:
            thread_id = result["session_id"]
            if not isinstance(thread_id, str) or not thread_id.strip():
                return ConformanceRunResult(
                    brain="openai",
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
                    note="OpenAI operator surface did not return a resumable thread id.",
                    artifact_relpath=_artifact_relpath(artifact_dir),
                )
            preservation_state = derive_preservation_state(
                None,
                contract_pack.work_contract,
                first_outcome.parsed_paths,
                first_outcome,
                remaining_repairs=1,
            )
            resumed_result = _run_openai_operator_cli_resume_repair(
                artifact_dir=artifact_dir,
                workspace=workspace,
                env=env,
                model=initial["model"],
                thread_id=thread_id,
                preservation_state=preservation_state,
                preserved_file_map=first_file_map,
                verifier_contract=contract_pack.work_contract,
            )
            if resumed_result["status"] == "env_blocked":
                return ConformanceRunResult(
                    brain="openai",
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
            final_note = resumed_result["note"]
            final_extraction_mode = resumed_result["extraction_mode"]

    return _result_from_verification(
        brain="openai",
        surface="operator_cli",
        contract_pack=contract_pack.contract_pack,
        outcome=final_outcome,
        attempt_count=attempt_count,
        first_outcome=first_outcome,
        extraction_mode=final_extraction_mode,
        artifact_relpath=_artifact_relpath(artifact_dir),
        note=final_note,
    )


def run_openai_operator_cli_repair_pressure(
    *,
    contract_pack: ContractPack,
) -> dict[str, Any]:
    if contract_pack.active_proving_default != OPENAI_ACTIVE_PROVING_DEFAULT:
        raise ValueError(
            "repair-pressure proof currently supports only the OpenAI operator_cli proving lane."
        )

    load_local_env_file()
    timestamp = now_utc_iso().replace(":", "").replace("-", "")
    run_root = REPAIR_PRESSURE_ROOT / f"run_{timestamp}_{contract_pack.contract_pack}"
    artifact_dir = run_root / "openai_operator_cli"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    instructions = build_verified_work_instructions(contract_pack.work_contract)

    with _stage_contract_pack_workspace(
        contract_pack,
        prefix="cortex-repair-pressure-openai-",
    ) as workspace, isolated_codex_home_env() as env:
        initial_prompt = _render_combined_operator_prompt(
            task_prompt=contract_pack.prompt_text,
            instructions=instructions,
        )
        initial = run_openai_operator_single_turn(
            project_root=workspace,
            prompt=initial_prompt,
            scenario_id=f"repair_pressure_{contract_pack.contract_pack}_attempt1",
            stderr_path=artifact_dir / "attempt1.stderr.log",
            ephemeral=False,
            env=env,
            model=_OPENAI_OPERATOR_MODEL,
        )
        write_json(artifact_dir / "attempt1.json", initial)
        initial_result = _evaluate_openai_operator_attempt(
            operator_turn=initial,
            work_contract=contract_pack.work_contract,
        )
        if initial_result["status"] == "env_blocked":
            summary = {
                "generated_at": now_utc_iso(),
                "proof_surface": "openai_operator_cli_repair_pressure",
                "contract_pack": contract_pack.as_payload(),
                "status": "env_blocked",
                "artifact_relpath": _artifact_relpath(artifact_dir),
                "note": initial_result["note"],
                "transport_failure_class": initial_result["transport_failure_class"],
            }
            write_json(run_root / "summary.json", summary)
            return summary

        initial_outcome = initial_result["verification"]
        assert isinstance(initial_outcome, VerificationOutcome)
        initial_file_map = initial_result.get("file_map")
        if isinstance(initial_file_map, Mapping):
            initial_file_map = {
                str(path): str(content) for path, content in initial_file_map.items()
            }
        write_json(
            artifact_dir / "attempt1.initial_verification.json",
            {
                "verification": initial_outcome.as_payload(),
                "file_map": initial_file_map,
            },
        )
        repair_case = _build_openai_repair_pressure_case(
            contract_pack=contract_pack,
            workspace=workspace,
            initial_output_text=initial.get("output_text"),
            initial_file_map=initial_file_map,
            initial_outcome=initial_outcome,
        )
        effective_outcome = repair_case["effective_outcome"]
        assert isinstance(effective_outcome, VerificationOutcome)
        write_text(
            artifact_dir / "attempt1.effective_result.txt",
            str(repair_case["effective_result_text"]),
        )
        write_json(
            artifact_dir / "attempt1.effective_verification.json",
            {
                "pressure_source": repair_case["pressure_source"],
                "failure_class": repair_case["failure_class"],
                "target_path": repair_case["target_path"],
                "description": repair_case["description"],
                "verification": effective_outcome.as_payload(),
                "file_map": repair_case["effective_file_map"],
            },
        )
        preservation_state = derive_preservation_state(
            None,
            contract_pack.work_contract,
            effective_outcome.parsed_paths,
            effective_outcome,
            remaining_repairs=1,
        )
        thread_id = initial_result["session_id"]
        if not isinstance(thread_id, str) or not thread_id.strip():
            summary = {
                "generated_at": now_utc_iso(),
                "proof_surface": "openai_operator_cli_repair_pressure",
                "contract_pack": contract_pack.as_payload(),
                "status": "partial",
                "artifact_relpath": _artifact_relpath(artifact_dir),
                "repair_pressure_case": {
                    "pressure_source": repair_case["pressure_source"],
                    "failure_class": repair_case["failure_class"],
                    "target_path": repair_case["target_path"],
                    "description": repair_case["description"],
                },
                "note": "OpenAI operator surface did not return a resumable thread id.",
            }
            write_json(run_root / "summary.json", summary)
            return summary

        resumed_result = _run_openai_operator_cli_resume_repair(
            artifact_dir=artifact_dir,
            workspace=workspace,
            env=env,
            model=initial["model"],
            thread_id=thread_id,
            preservation_state=preservation_state,
            preserved_file_map=initial_file_map,
            verifier_contract=contract_pack.work_contract,
        )
        if resumed_result["status"] == "env_blocked":
            summary = {
                "generated_at": now_utc_iso(),
                "proof_surface": "openai_operator_cli_repair_pressure",
                "contract_pack": contract_pack.as_payload(),
                "status": "env_blocked",
                "artifact_relpath": _artifact_relpath(artifact_dir),
                "repair_pressure_case": {
                    "pressure_source": repair_case["pressure_source"],
                    "failure_class": repair_case["failure_class"],
                    "target_path": repair_case["target_path"],
                    "description": repair_case["description"],
                },
                "note": resumed_result["note"],
                "transport_failure_class": resumed_result["transport_failure_class"],
            }
            write_json(run_root / "summary.json", summary)
            return summary

        final_outcome = resumed_result["verification"]
        assert isinstance(final_outcome, VerificationOutcome)
        final_file_map = resumed_result.get("file_map")
        if isinstance(final_file_map, Mapping):
            final_file_map = {str(path): str(content) for path, content in final_file_map.items()}
        repair_contract = resumed_result["repair_contract"]
        assert isinstance(repair_contract, WorkContract)
        audit = {
            "task_anchor_present": bool(preservation_state.task_anchor),
            "preservation_state_present": True,
            "repair_contract_matches_surface": tuple(repair_contract.allowed_write_paths)
            == tuple(
                path
                for path in contract_pack.work_contract.allowed_write_paths
                if path in preservation_state.lawful_repair_surface
            ),
            "repair_ticket_mechanical_only": all(
                label in resumed_result["repair_ticket"]
                for label in (
                    "task_anchor:",
                    "trusted_checks:",
                    "trusted_paths:",
                    "failure_class:",
                    "falsified_checks:",
                    "failing_tests:",
                    "lawful_repair_surface:",
                    "remaining_repairs:",
                    "allowed_moves:",
                )
            ),
            "attempt2_paths_within_surface": (
                True
                if not isinstance(final_file_map, Mapping)
                else set(final_file_map).issubset(preservation_state.lawful_repair_surface)
            ),
            "preserved_overlay_reused": initial_file_map is not None,
        }
        result = _result_from_verification(
            brain="openai",
            surface="operator_cli",
            contract_pack=contract_pack.contract_pack,
            outcome=final_outcome,
            attempt_count=2,
            first_outcome=effective_outcome,
            extraction_mode=resumed_result["extraction_mode"],
            artifact_relpath=_artifact_relpath(artifact_dir),
            note=resumed_result["note"],
        )
        summary = {
            "generated_at": now_utc_iso(),
            "proof_surface": "openai_operator_cli_repair_pressure",
            "contract_pack": contract_pack.as_payload(),
            "status": result.status,
            "artifact_relpath": _artifact_relpath(artifact_dir),
            "repair_pressure_case": {
                "pressure_source": repair_case["pressure_source"],
                "failure_class": repair_case["failure_class"],
                "target_path": repair_case["target_path"],
                "description": repair_case["description"],
            },
            "initial_attempt": {
                "verification": initial_outcome.as_payload(),
                "file_map": initial_file_map,
            },
            "effective_first_attempt": {
                "verification": effective_outcome.as_payload(),
                "file_map": repair_case["effective_file_map"],
            },
            "preservation_state": preservation_state.as_payload(),
            "repair_contract": repair_contract.as_payload(),
            "repair_audit": audit,
            "result": result.as_payload(),
        }
        write_json(run_root / "summary.json", summary)
        write_text(run_root / "summary.md", render_repair_pressure_markdown(summary))
        return summary


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
            repair_ticket = build_verified_work_repair_ticket(
                derive_preservation_state(
                    None,
                    contract_pack.work_contract,
                    first_outcome.parsed_paths,
                    first_outcome,
                    remaining_repairs=1,
                )
            )
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
                task_prompt=build_verified_work_repair_ticket(
                    derive_preservation_state(
                        None,
                        contract_pack.work_contract,
                        first_outcome.parsed_paths,
                        first_outcome,
                        remaining_repairs=1,
                    )
                ),
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
    preserved_file_map: dict[str, str] | None = None,
    verifier_contract: WorkContract | None = None,
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
    file_map, verification = verify_verified_work_result(
        result_text,
        work_contract,
        preserved_file_map=preserved_file_map,
        verifier_contract=verifier_contract,
    )
    note = sanitize_text(raw_stderr.strip() or "executed")
    if command_result["exit_code"] == 124:
        note = sanitize_text(f"{note}\nstructured output captured before operator timeout")
    return {
        "status": "executed",
        "file_map": file_map,
        "verification": verification,
        "session_id": session_id,
        "extraction_mode": extraction_mode,
        "note": note,
    }


def _evaluate_openai_operator_attempt(
    *,
    operator_turn: dict[str, Any],
    work_contract: WorkContract,
    preserved_file_map: dict[str, str] | None = None,
    verifier_contract: WorkContract | None = None,
) -> dict[str, Any]:
    output_text = operator_turn.get("output_text")
    failure_class = operator_turn.get("failure_class")
    if failure_class in BLOCKING_FAILURE_CLASSES:
        return {
            "status": "env_blocked",
            "transport_failure_class": failure_class,
            "note": sanitize_text(str(failure_class)),
        }
    if failure_class is not None and not str(output_text or "").strip():
        return {
            "status": "env_blocked",
            "transport_failure_class": failure_class,
            "note": sanitize_text(str(failure_class)),
        }
    file_map, verification = verify_verified_work_result(
        output_text,
        work_contract,
        preserved_file_map=preserved_file_map,
        verifier_contract=verifier_contract,
    )
    model = operator_turn.get("model")
    note = "executed"
    if isinstance(model, str) and model.strip():
        note = f"operator model: {model}"
    if failure_class is not None:
        note = f"{note}; failure_class={failure_class}"
    return {
        "status": "executed",
        "file_map": file_map,
        "verification": verification,
        "session_id": operator_turn.get("thread_id"),
        "extraction_mode": "operator_lifecycle",
        "note": sanitize_text(note),
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
    active_proving_default: str,
) -> str:
    if overall_divergence_class == "cortex_law":
        return "revise_cortex_law"
    proving_brain, _proving_surface = active_proving_default.split(":", 1)
    non_shipping_divergence = [
        result
        for result in results
        if result["brain"] != proving_brain
        and result["status"] == "divergent"
        and result["divergence_class"] in {"brain_wiring", "surface_wiring"}
    ]
    if non_shipping_divergence:
        return "fix_wiring_only"
    proving_result = next(
        (result for result in results if result["brain"] == proving_brain),
        None,
    )
    if proving_result is not None and proving_result["status"] in {"partial", "divergent"}:
        return "improve_proving_default"
    non_shipping_partial = [
        result
        for result in results
        if result["brain"] != proving_brain
        and result["status"] == "partial"
        and result["divergence_class"] in {"brain_wiring", "surface_wiring"}
    ]
    if non_shipping_partial:
        return "fix_wiring_only"
    proving_env_blocked = proving_result is not None and proving_result["status"] == "env_blocked"
    if proving_env_blocked:
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
    if not PHASE_GATES_PATH.exists():
        return None
    text = PHASE_GATES_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^\| `CT2` .*?current (?:shipping-default|active proving-default) decision is `(?P<decision>[a-z_]+)`",
        text,
        re.MULTILINE,
    )
    if match is None:
        return None
    return match.group("decision")


def _summary_active_proving_default(summary: Mapping[str, Any]) -> str | None:
    proving_truth = summary.get("proving_truth")
    if isinstance(proving_truth, Mapping):
        value = proving_truth.get("active_default")
        if isinstance(value, str) and value.strip():
            return value
    shipping_truth = summary.get("shipping_truth")
    if isinstance(shipping_truth, Mapping):
        value = shipping_truth.get("default")
        if isinstance(value, str) and value.strip():
            return value
    return None


def _summary_product_runtime_claim(summary: Mapping[str, Any]) -> str | None:
    product_truth = summary.get("product_truth")
    if isinstance(product_truth, Mapping):
        value = product_truth.get("runtime_claim")
        if isinstance(value, str) and value.strip():
            return value
    shipping_truth = summary.get("shipping_truth")
    if isinstance(shipping_truth, Mapping):
        value = shipping_truth.get("default")
        if isinstance(value, str) and value.strip():
            return value
    return None


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
    "run_openai_operator_cli_repair_pressure",
    "strongest_native_surface",
    "supported_contract_pack_names",
]


if __name__ == "__main__":
    raise SystemExit(main())
