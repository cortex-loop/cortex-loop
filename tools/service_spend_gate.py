"""Local maintainer gate for service-lane spend-heavy evaluation commands."""

from __future__ import annotations

from live_validation_common import SERVICE_SPEND_APPROVAL_ENV, service_spend_approved


def require_openai_service_spend_approval(*, purpose: str) -> None:
    if service_spend_approved():
        return
    raise SystemExit(
        f"OpenAI service-lane spend is blocked for {purpose}. "
        f"Set {SERVICE_SPEND_APPROVAL_ENV}=1 to opt in explicitly, "
        "or use the CLI/watchlist lane instead."
    )


__all__ = ["require_openai_service_spend_approval"]
