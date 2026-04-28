"""Blind review packet for Cortex V2 payoff and adoption evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

from lab.live_validation_common import (
    comparator_path,
    ensure_live_validation_dirs,
    now_utc_iso,
    write_json,
)
from lab.v2_behavioral_payoff import (
    PAYOFF_SCENARIOS,
    TIER1_PAYOFF_PROVIDERS,
    summarize_adoption_preference,
)


DEFAULT_ADOPTION_REVIEW_PACKET_PATH = comparator_path(
    "v2_adoption_review_packet.latest.json"
)


def build_adoption_review_packet(
    *,
    directionality_summary_path: Path | None = None,
    completed_review_path: Path | None = None,
    provider_names: tuple[str, ...] = TIER1_PAYOFF_PROVIDERS,
    max_samples_per_provider: int = 6,
) -> dict[str, Any]:
    directionality = _read_json(
        directionality_summary_path or comparator_path("operator_directionality_summary.json")
    )
    samples, answer_key = _blind_samples(
        directionality,
        provider_names=provider_names,
        max_samples_per_provider=max_samples_per_provider,
    )
    completed_review = _read_json(completed_review_path) if completed_review_path else {}
    review_samples = completed_review.get("samples", []) if isinstance(completed_review, dict) else []
    adoption_summary = summarize_adoption_preference(review_samples)
    return {
        "generated_at": now_utc_iso(),
        "surface": "lab",
        "evidence_role": "watchlist",
        "train": "v2-intervention-policy-tuning",
        "provider_scope": list(provider_names),
        "sample_count": len(samples),
        "samples": samples,
        "lab_answer_key": answer_key,
        "rubric": {
            "preferred": "cortex | raw_host | tie | unusable",
            "usefulness": "1-5",
            "truthfulness": "1-5",
            "unnecessary_friction": "1-5 where lower is better",
            "would_use_again": "yes | no",
            "notes": "short reviewer rationale",
        },
        "adoption_gate": adoption_summary,
        "hostile_review": {
            "not_product_claim": "This packet collects preference evidence only; it does not by itself prove product adoption.",
            "blindness_required": "Reviewer-visible options omit variant names; completed reviews must not score by knowing which side is Cortex.",
            "distribution_rule": "Distribute only sample_id, option_a, option_b, and rubric fields to reviewers; lab_answer_key is for post-review scoring.",
            "sample_bias": "The sample is drawn from current directionality artifacts, so gaps in live runs remain gaps in adoption evidence.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.v2_adoption_review",
        description="Build a blind pairwise adoption-review packet from directionality artifacts.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_ADOPTION_REVIEW_PACKET_PATH)
    parser.add_argument("--directionality-summary", type=Path, default=None)
    parser.add_argument("--completed-review", type=Path, default=None)
    parser.add_argument(
        "--provider",
        choices=("claude", "codex", "openai"),
        action="append",
        default=None,
    )
    parser.add_argument("--max-samples-per-provider", type=int, default=6)
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    payload = build_adoption_review_packet(
        directionality_summary_path=args.directionality_summary,
        completed_review_path=args.completed_review,
        provider_names=tuple(args.provider or TIER1_PAYOFF_PROVIDERS),
        max_samples_per_provider=max(1, args.max_samples_per_provider),
    )
    write_json(args.output, payload)
    print(str(args.output))
    return 0


def _blind_samples(
    directionality: dict[str, Any],
    *,
    provider_names: tuple[str, ...],
    max_samples_per_provider: int,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    samples: list[dict[str, Any]] = []
    answer_key: dict[str, dict[str, str]] = {}
    providers = directionality.get("providers", {})
    if not isinstance(providers, dict):
        return samples, answer_key
    for provider in provider_names:
        payload = providers.get(provider, {})
        if not isinstance(payload, dict):
            continue
        provider_samples = 0
        for pair in payload.get("pairs", []):
            if provider_samples >= max_samples_per_provider:
                break
            if not isinstance(pair, dict) or pair.get("pair_status") != "compared":
                continue
            scenario_id = pair.get("scenario_id")
            if scenario_id not in PAYOFF_SCENARIOS:
                continue
            raw = pair.get("raw_host")
            product = pair.get("product_normal_cortex")
            if not isinstance(raw, dict) or not isinstance(product, dict):
                continue
            sample = _blind_sample(
                provider=provider,
                scenario_id=str(scenario_id),
                repeat_index=pair.get("repeat_index"),
                raw=raw,
                product=product,
            )
            if sample is not None:
                sample_payload, key_payload = sample
                samples.append(sample_payload)
                answer_key[sample_payload["sample_id"]] = key_payload
                provider_samples += 1
    return samples, answer_key


def _blind_sample(
    *,
    provider: str,
    scenario_id: str,
    repeat_index: Any,
    raw: dict[str, Any],
    product: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]] | None:
    raw_text = _review_text(raw)
    product_text = _review_text(product)
    if not raw_text or not product_text:
        return None
    stable_key = f"{provider}:{scenario_id}:{repeat_index}"
    cortex_first = (sum(ord(char) for char in stable_key) % 2) == 0
    option_a = product_text if cortex_first else raw_text
    option_b = raw_text if cortex_first else product_text
    sample = {
        "sample_id": f"{provider}:{scenario_id}:{repeat_index}",
        "provider": provider,
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "option_a": option_a,
        "option_b": option_b,
    }
    key = {
        "option_a": "product_normal_cortex" if cortex_first else "raw_host",
        "option_b": "raw_host" if cortex_first else "product_normal_cortex",
    }
    return sample, key


def _review_text(payload: dict[str, Any]) -> str | None:
    text = payload.get("result_text")
    if not isinstance(text, str) or not text.strip():
        return None
    stripped = text.strip()
    return stripped if len(stripped) <= 4000 else stripped[:3997] + "..."


def _read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
