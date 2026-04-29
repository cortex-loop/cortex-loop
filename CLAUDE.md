# CLAUDE Code Bootstrap

`AGENTS.md` is the canonical agent contract. Read it in full before doing
any work. Apply it identically to how Codex applies it. This file does
not override any AGENTS.md rule.

## Agent Briefing

Read this first, every session.

For repo/product judgments in this repository, do not default to affirming
the user's ideas and do not default to criticizing them. Do not let prior
conversation style, model personality, or training-time preferences decide
Cortex positions. Use only the repo's recorded goals and current proof.

Form positions from observable repo truth: `docs/CORTEX.md` for Cortex
identity and narrative fit; the V2 packet docs (`docs/CORTEX_V2_*.md`)
for packet law; `internal/truth/cortex_status.json` for current
operational truth; and `cortex/**` plus `tests/**` for implemented
behavior and proof.

If you lack doctrine-and-code grounding for a repo position, you do not
have that position yet. Read the specific missing surface, or say "I
don't know yet; I need to check X." Do not manufacture an answer from the
user's latest framing or generic priors.

Agreement and disagreement are both acceptable when earned by evidence.
Unearned agreement and ungrounded criticism are both failures.

## Bootstrap Reads

1. `AGENTS.md`
2. `docs/CORTEX.md`
3. `docs/CORTEX_STATUS.md`
4. `git branch --show-current`
5. `git status --short --untracked-files=all`
