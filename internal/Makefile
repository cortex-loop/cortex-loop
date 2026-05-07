PYTHON ?= python3
AGENT ?= codex
SLUG ?= session
MESSAGE ?= docs: update internal workflow
REPO_WORKFLOW ?= workflow/repo_workflow.py
MODE ?= close-session
SURFACE ?= internal

.PHONY: test closeout-test closeout-init closeout-render closeout-validate sync-main start-session close-session finalize preserve-worktree audit-branches cleanup-report active-stack-report seam-preflight

test:
	PYTHONPATH=.. $(PYTHON) -m pytest ../tests/internal -q

closeout-test:
	$(PYTHON) ../internal/truth/generate_status.py --check
	$(PYTHON) ../internal/archive/generate_archive_index.py --check
	PYTHONPATH=.. $(PYTHON) -m pytest ../tests/internal -q

closeout-init:
	$(PYTHON) ../internal/closeout/contract.py init --mode $(MODE)

closeout-render:
	$(PYTHON) ../internal/closeout/contract.py render

closeout-validate:
	$(PYTHON) ../internal/closeout/contract.py validate --mode $(MODE)

sync-main:
	$(PYTHON) $(REPO_WORKFLOW) sync-main

start-session:
	$(PYTHON) $(REPO_WORKFLOW) start-session --agent $(AGENT) --slug $(SLUG)

close-session:
	$(PYTHON) $(REPO_WORKFLOW) close-session --message "$(MESSAGE)"

finalize:
	$(PYTHON) $(REPO_WORKFLOW) finalize --manual-exception --message "$(MESSAGE)"

preserve-worktree:
	$(PYTHON) $(REPO_WORKFLOW) preserve-worktree --slug $(SLUG)

audit-branches:
	$(PYTHON) $(REPO_WORKFLOW) audit-branches

cleanup-report:
	$(PYTHON) $(REPO_WORKFLOW) cleanup-report

active-stack-report:
	$(PYTHON) $(REPO_WORKFLOW) active-stack-report

seam-preflight:
	$(PYTHON) $(REPO_WORKFLOW) seam-preflight --slug $(SLUG) --surface $(SURFACE)
