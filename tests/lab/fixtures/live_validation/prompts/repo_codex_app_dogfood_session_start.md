Work on the current repo task in this real Cortex repository.

Follow `AGENTS.md`, `docs/CORTEX_STATUS.md`, and `docs/internal/REPO_WORKFLOW.md`
unchanged. Dogfood mode is active only for this current Codex App chat/session.

Work only on the active managed `codex/...` session branch.
Treat this as normal repo work, not as a lab narrative or diagnostic exercise.
Do not rerun `make live-codex-dogfood` unless the user explicitly asks for the
heavier watchlist probe.

Preserve the repo's normal final handoff contract. After the normal handoff,
append this exact block:

DOGFOOD_SIGNAL
continuity_helped: yes|no
blocker_surfaced: yes|no
uncertainty_or_brake_used: yes|no
truthful_closure: yes|no
cortex_changed_next_action: yes|no
note: <one sentence>
