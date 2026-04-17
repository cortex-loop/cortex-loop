"""Cross-provider measurement driver for the Cortex v3 replay harness."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cortex_v3.contracts import ProviderTurnRequest, ProviderTurnResponse, VerifiedTurnRequest, WorkContract
from cortex_v3.providers.base import ProviderAdapter
from cortex_v3.providers.claude import ClaudeAdapter
from cortex_v3.providers.gemini import GeminiAdapter
from cortex_v3.providers.openai import OpenAIAdapter
from lab.v3.fixture_payloads import fixture_payload_for_task
from lab.v3.replay import ReplayTask, run_replay_case


_DEFAULT_TRIALS = 10
_DEFAULT_MAX_TOKENS = 4096
_ARMS = ("verified_with_repair", "plain_feedback")
_PROVIDERS = ("openai", "claude", "gemini")
_MODEL_BY_PROVIDER = {
    "openai": "gpt-4o-mini",
    "claude": "claude-haiku-4-5",
    "gemini": "gemini-2.0-flash",
}
_API_KEY_BY_PROVIDER = {
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


@dataclass(frozen=True, slots=True)
class _TaskSpec:
    task_id: str
    task_prompt: str
    work_contract: WorkContract


_TASK_SPECS = (
    _TaskSpec(
        task_id="bookmarks_app_template",
        task_prompt="build bookmarks app",
        work_contract=WorkContract(
            allowed_write_paths=(
                "src/bookmarks_api/main.py",
                "src/bookmarks_api/models.py",
                "src/bookmarks_api/store.py",
            ),
            verification_profile="python_workspace_pytest_v1",
            max_repair_turns=1,
        ),
    ),
    _TaskSpec(
        task_id="project_template",
        task_prompt="fix normalize_port",
        work_contract=WorkContract(
            allowed_write_paths=("src/normalize_port.py",),
            verification_profile="python_workspace_pytest_port_fix_v1",
            max_repair_turns=1,
        ),
    ),
    _TaskSpec(
        task_id="feature_flags_template",
        task_prompt="fix feature flag evaluator",
        work_contract=WorkContract(
            allowed_write_paths=(
                "src/feature_flags/models.py",
                "src/feature_flags/evaluator.py",
            ),
            verification_profile="python_workspace_pytest_feature_flags_v1",
            max_repair_turns=1,
        ),
    ),
)


@dataclass(slots=True)
class _FixtureAdapter:
    provider: str
    output_text: str

    def execute_turn(self, request: ProviderTurnRequest) -> ProviderTurnResponse:
        del request
        return ProviderTurnResponse(
            provider=self.provider,
            output_text=self.output_text,
            raw_events=tuple(),
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fixture", "live"), required=True)
    parser.add_argument("--trials", type=int, default=_DEFAULT_TRIALS)
    parser.add_argument("--providers", type=str, default=",".join(_PROVIDERS))
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--max-tokens", type=int, default=_DEFAULT_MAX_TOKENS)
    args = parser.parse_args(argv)

    providers = _parsed_providers(args.providers)
    if args.trials <= 0:
        raise ValueError("--trials must be positive.")
    if args.max_tokens <= 0:
        raise ValueError("--max-tokens must be positive.")

    live_provider_count = (
        sum(1 for provider in providers if _provider_has_key(provider))
        if args.mode == "live"
        else 0
    )
    if live_provider_count > 0:
        requested_budget = (
            args.trials * len(_TASK_SPECS) * len(_ARMS) * live_provider_count * args.max_tokens
        )
        if requested_budget > 2_000_000:
            raise RuntimeError(
                "Requested live measurement exceeds the configured token budget cap."
            )

    started_at = _timestamp()
    rows: list[dict[str, Any]] = []
    for provider in providers:
        model = _MODEL_BY_PROVIDER[provider]
        missing_key = args.mode == "live" and not _provider_has_key(provider)
        for task_spec in _TASK_SPECS:
            for arm in _ARMS:
                for trial in range(1, args.trials + 1):
                    if missing_key:
                        rows.append(
                            _error_row(
                                provider=provider,
                                task_id=task_spec.task_id,
                                arm=arm,
                                trial=trial,
                                model=model,
                                error="missing_api_key",
                            )
                        )
                        continue
                    task = ReplayTask(
                        task_id=task_spec.task_id,
                        request=VerifiedTurnRequest(
                            model=model,
                            task_prompt=task_spec.task_prompt,
                            work_contract=task_spec.work_contract,
                            instructions="Return protocol blocks only.",
                            max_output_tokens=args.max_tokens,
                        ),
                    )
                    try:
                        adapter = _build_adapter(
                            mode=args.mode,
                            provider=provider,
                            task_id=task_spec.task_id,
                        )
                        outcome = run_replay_case(adapter, task, arm=arm)
                    except Exception as exc:  # noqa: BLE001
                        rows.append(
                            _error_row(
                                provider=provider,
                                task_id=task_spec.task_id,
                                arm=arm,
                                trial=trial,
                                model=model,
                                error=str(exc) or exc.__class__.__name__,
                            )
                        )
                        continue
                    rows.append(
                        {
                            "provider": outcome.provider,
                            "task_id": outcome.task_id,
                            "arm": outcome.arm,
                            "trial": trial,
                            "verification_status": outcome.verification_status,
                            "failure_class": outcome.failure_class,
                            "pytest_passed": outcome.pytest_passed,
                            "pytest_failed": (
                                0
                                if outcome.verification_status == "passed"
                                and outcome.pytest_failed is None
                                else outcome.pytest_failed
                            ),
                            "attempt_count": outcome.attempt_count,
                            "decision": outcome.decision,
                            "duration_seconds": outcome.duration_seconds,
                            "model": outcome.model,
                            "cost_usd": None,
                            "error": None,
                        }
                    )

    rows.sort(key=lambda row: (row["provider"], row["task_id"], row["arm"], row["trial"]))
    payload = {
        "started_at": started_at,
        "completed_at": _timestamp(),
        "config": {
            "mode": args.mode,
            "trials": args.trials,
            "providers": list(providers),
            "max_tokens": args.max_tokens,
        },
        "rows": rows,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} rows to {output_path}")
    return 0


def _build_adapter(
    *,
    mode: str,
    provider: str,
    task_id: str,
) -> ProviderAdapter:
    if mode == "fixture":
        return _FixtureAdapter(
            provider=provider,
            output_text=fixture_payload_for_task(task_id),
        )
    if provider == "openai":
        return OpenAIAdapter()
    if provider == "claude":
        return ClaudeAdapter()
    if provider == "gemini":
        return GeminiAdapter()
    raise ValueError(f"Unsupported provider: {provider}")


def _parsed_providers(raw_value: str) -> tuple[str, ...]:
    providers: list[str] = []
    for provider in raw_value.split(","):
        normalized = provider.strip()
        if not normalized:
            continue
        if normalized not in _PROVIDERS:
            raise ValueError(f"Unsupported provider: {normalized}")
        if normalized not in providers:
            providers.append(normalized)
    if not providers:
        raise ValueError("--providers must contain at least one supported provider.")
    return tuple(providers)


def _provider_has_key(provider: str) -> bool:
    env_var = _API_KEY_BY_PROVIDER[provider]
    value = os.environ.get(env_var)
    return isinstance(value, str) and bool(value.strip())


def _error_row(
    *,
    provider: str,
    task_id: str,
    arm: str,
    trial: int,
    model: str,
    error: str,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "task_id": task_id,
        "arm": arm,
        "trial": trial,
        "verification_status": None,
        "failure_class": None,
        "pytest_passed": None,
        "pytest_failed": None,
        "attempt_count": None,
        "decision": None,
        "duration_seconds": 0.0,
        "model": model,
        "cost_usd": None,
        "error": error,
    }


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
