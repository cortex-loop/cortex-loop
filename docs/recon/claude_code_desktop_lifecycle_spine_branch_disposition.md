# Claude Code Desktop Lifecycle Spine Branch Disposition

Surface: internal doctrine / branch hygiene

Date: 2026-05-05

## Verdict

The managed branch `codex/20260430-155752-claude-code-desktop-lifecycle-spine`
is retired from active branch hygiene. It is not merged into the current
OpenAI Codex App/CLI task-standard train.

The exact branch head is preserved as local archival tag
`archive/claude-code-desktop-lifecycle-spine-20260505` at commit
`0c36c56`. The local managed branch may be deleted after this disposition
document lands.

## Reason

The branch contains substantial Claude Code Desktop host work, not a trivial
note branch. Merging it now would fold stale host-specific lifecycle changes
and status/doc edits into the current task-standard SRE direction. That would
blur the distinction between:

- host-agnostic SRE task-standard law;
- OpenAI Codex App/CLI as the current product realization;
- Claude Code Desktop as a separate host surface requiring its own fresh
  evidence and current doctrine fit.

## Preserved Evidence

Branch head: `0c36c56`

Diff against current `main` at disposition time:

```text
20 files changed, 1118 insertions(+), 272 deletions(-)
```

Changed paths:

```text
M cortex/hosts/claude_code_desktop/__init__.py
M cortex/hosts/claude_code_desktop/hook_control.py
M cortex/hosts/claude_code_desktop/ingress.py
M cortex/hosts/claude_code_desktop/runtime.py
A cortex/hosts/claude_code_desktop/session_io.py
M docs/CORTEX.md
M docs/cortex_plugin/ADAPTER.md
M docs/cortex_plugin/DESIGN.md
M internal/truth/cortex_status.json
M lab/cortex_plugin_skeleton/plugins/cortex-claude-code-desktop/hooks/hooks.json
M lab/cortex_plugin_skeleton/plugins/cortex-claude-code-desktop/scripts/_wire.py
M lab/cortex_plugin_skeleton/plugins/cortex-claude-code-desktop/scripts/cortex_posttool.py
M lab/cortex_plugin_skeleton/plugins/cortex-claude-code-desktop/scripts/cortex_session_end.py
M lab/cortex_plugin_skeleton/plugins/cortex-claude-code-desktop/scripts/cortex_session_start.py
M lab/cortex_plugin_skeleton/plugins/cortex-claude-code-desktop/scripts/cortex_stop.py
M lab/cortex_plugin_skeleton/plugins/cortex-claude-code-desktop/scripts/cortex_user_prompt.py
M tests/conformance/test_claude_code_desktop_host_control.py
M tests/conformance/test_claude_code_desktop_runtime_session_io.py
M tests/internal/test_docs_boundary.py
A tests/lab/test_cortex_plugin_skeleton.py
```

## Salvage Rule

Future Claude Code Desktop work should not resume this branch directly. It
should open a fresh seam from current `main`, reread this disposition, and
selectively re-derive only the pieces that still satisfy current packet law,
task-standard doctrine, and host-surface evidence requirements.

## Claims Not Earned

This disposition does not claim Claude Code Desktop lifecycle parity, product
promotion, behavior lift, or current compatibility with the task-standard SRE
train. It preserves evidence and removes stale branch pressure only.
