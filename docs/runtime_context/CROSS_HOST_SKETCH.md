# Cortex Runtime Context Cross-Host Sketch

Surface: product eval artifact.

This document is not a build commitment. It records how the
`CORTEX_RUNTIME_CONTEXT_V1` schema should remain portable across hosts
if the OpenAI bridge later earns enough evidence to port.

## Sketch

The runtime context schema ports cleanly as provider-neutral lifecycle
context, but the placement is host-specific. OpenAI ordinary calls place
the block in `OpenAIHostControlRequest.instructions`; OpenAI verified
work places it in model-visible `input_text` because verified-work
instructions are fixed. A Claude port should place the same block in
`ClaudeHostControlRequest.system` while leaving `input_text` as the user
task. A Gemini port should place the same block in
`GeminiHostControlRequest.instructions`, which becomes
`systemInstruction` in the Gemini transport. If a future host lacks a
system/instructions field, the port should not silently append context
to user input unless an explicit host-control contract says that is the
least-bad model-visible field.

## Non-Commitments

- This seam does not implement Claude or Gemini runtime-context shaping.
- This seam does not claim cross-host output lift.
- Host ports must preserve the same last-feedback-only rule, clean-window
  kill switch, field bounds, and no-accumulation rule.
