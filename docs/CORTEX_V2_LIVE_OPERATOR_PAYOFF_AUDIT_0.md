# CORTEX_V2_LIVE_OPERATOR_PAYOFF_AUDIT_0

Date: 2026-03-28
Status: accepted operator-only payoff audit note

## Purpose

This note records the first operator-only payoff audit over the current signed-in host-native lanes.
It is an evaluation/support surface, not a runtime or auth-expansion brief.

## Current operator truth used by the audit

- Claude operator lane is strong on documented hooks:
  - `pass_minimal`
  - `truth_gap`
  - `restart_continuity`
- OpenAI operator lane is strong on:
  - `codex exec` smoke
  - `codex app-server` lifecycle proof
- Gemini remains an explicit partial host line:
  - `gemini-2.5-auto` unsupported locally
  - `gemini-2.5-pro` valid but exploratory-only and capacity-blocked on smoke
  - repeated preflight probes currently fall through to usable `gemini-2.5-flash-lite`
  - repeated operator smoke baselines on `gemini-2.5-flash` are currently `capacity_exhausted`
  - `gemini-2.5-flash` closes `pass_minimal` with warning-preserving capacity pressure
  - `gemini-2.5-flash-lite` closes `restart_continuity` with warning-preserving capacity pressure
  - neither model closes `truth_gap` honestly

## Audit verdict

**operator lifecycle-first is already paying off clearly**

Qualifier:

- Gemini remains explicit partial truth rather than hidden success
- automation/service remains blocked on missing machine auth and unproven

## Why this is the current verdict

- Claude and OpenAI are now strong on real host-native operator lifecycle surfaces
- Gemini is not smooth, but the lifecycle-first discipline is already paying off because it keeps:
  - hook visibility explicit
  - model and fallback choice explicit
  - warning pressure explicit
  - continuity truth explicit
  - truth-gap dishonesty explicit

That is already meaningful operator lift over a generic “task passed / task failed” view.
