PYTHON ?= python3
AGENT ?= codex
SLUG ?= session
MESSAGE ?= docs: update internal workflow
REPO_WORKFLOW ?= workflow/repo_workflow.py

.PHONY: test closeout-test sync-main start-session close-session finalize preserve-worktree audit-branches cleanup-report

test:
	$(PYTHON) -m pytest ../tests/internal -q

closeout-test:
	$(PYTHON) ../internal/truth/generate_status.py --check
	$(PYTHON) ../internal/archive/generate_archive_index.py --check
	$(PYTHON) -m pytest ../tests/internal -q

sync-main:
	$(PYTHON) $(REPO_WORKFLOW) sync-main

start-session:
	$(PYTHON) $(REPO_WORKFLOW) start-session --agent $(AGENT) --slug $(SLUG)

close-session:
	$(PYTHON) $(REPO_WORKFLOW) close-session --message "$(MESSAGE)"

finalize:
	$(PYTHON) $(REPO_WORKFLOW) finalize --message "$(MESSAGE)"

preserve-worktree:
	$(PYTHON) $(REPO_WORKFLOW) preserve-worktree --slug $(SLUG)

audit-branches:
	$(PYTHON) $(REPO_WORKFLOW) audit-branches

cleanup-report:
	$(PYTHON) $(REPO_WORKFLOW) cleanup-report
