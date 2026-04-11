"""Manual-user-exception gate for paid OpenAI service-lane evaluation commands."""

from __future__ import annotations

from lab.live_validation_common import SERVICE_SPEND_APPROVAL_ENV, service_spend_approved


def require_openai_service_spend_approval(*, purpose: str) -> None:
    if service_spend_approved():
        return
    raise SystemExit(
        f"OpenAI service-lane spend is blocked for {purpose}. "
        "Only proceed after the user explicitly approves spend in the current chat, "
        f"then set {SERVICE_SPEND_APPROVAL_ENV}=1 as a manual exception, "
        "or use the CLI/watchlist lane instead."
    )


__all__ = ["require_openai_service_spend_approval"]
