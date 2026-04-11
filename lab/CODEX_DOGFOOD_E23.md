# Codex App E23 Dogfood

This runbook keeps Codex App dogfooding on the lab watchlist lane.

1. Run `make live-codex-dogfood`.
2. If the summary says `ready_for_e23_session`, run:
   `python3 internal/workflow/repo_workflow.py sync-main`
   `python3 internal/workflow/repo_workflow.py start-session --agent codex --slug e23-kernel-extract`
3. In Codex App, use:
   `tests/lab/fixtures/live_validation/prompts/e23_codex_app_session_start.md`
4. Close the session with the normal workflow and the closeout profile:
   `tests/lab/fixtures/live_validation/prompts/e23_codex_app_closeout.md`
   `python3 internal/workflow/repo_workflow.py close-session --message "kernel: e23 kernel extract end-state summary"`
5. Treat `DOGFOOD_SIGNAL` as qualitative watchlist evidence only. It does not
   replace the repo handoff contract or promote Codex App into product truth.
