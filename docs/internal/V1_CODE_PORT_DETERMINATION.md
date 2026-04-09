# V1 Code Port Determination for Cortex v2

Surface: internal

## 0. Decision in one sentence

Port a **small v1 standard library plus the v1 evidence discipline**, not the v1 architecture.

Cortex v1 proved that a narrow machine-readable commitment carrier, witness-backed provenance, thin host-event normalization, and contradiction-preserving validation artifacts are genuinely reusable. It did **not** prove that the old stop-centered proof stack should remain the center of the system.

## 1. Governing rule

The port test for every v1 artifact is:

1. Was it **cross-runtime proven** or clearly useful on more than one host?
2. Is it **narrow enough** to fit the new Core / SRE / AUX packet without dragging the old worldview with it?
3. Does it strengthen:
   - commitment extraction,
   - downward provenance,
   - host-native lifecycle binding,
   - contradiction-preserving evidence,
   - or removable support memory?
4. Can it be carried over **without** restoring proof-centered product behavior?

If the answer is no, do not port it as architecture.

---

## 2. Final determination

## 2.1 Port now: v1 standard library primitives

These are the best immediate ports because they are narrow, battle-proven, and fit v2 cleanly.

### A. `stop_payload.py`

**Keep**
- structured stop-field extraction
- `payload.stop_fields` handling
- trailer parsing only as bounded fallback
- key normalization helpers

**Why**
This is the single strongest reusable structured-output result in frozen v1. The archive says one shared machine-readable carrier worked across the row-capturable lanes, and that the strongest reusable carrier was `payload.stop_fields`, not per-host custom JSON and not free-form prose.

**V2 home**
- **Core**
- under commitment candidate extraction / commitment surface parsing

**Port shape**
- rename around `commitment_fields` or `commitment_payload` if desired
- keep trailer fallback explicitly weaker than native/payload carriers
- do not import v1 stop-centered semantics with it

### B. Narrow `stop_contract.py` slice

**Keep**
- structured-carrier resolution
- source labeling (`native`, `payload.stop_fields`, fallback)
- strict rejection of fallback-only claims where needed
- key reconciliation logic that belongs to commitment extraction

**Do not keep**
- the full v1 contract worldview
- stop-stage / proof-gap assumptions

**V2 home**
- **Core**
- commitment candidate normalization and certification pre-checks

### C. Provenance helpers from `core_helpers.py`

**Keep**
- `session_git_snapshot(...)`
- `session_changed_files_since_baseline(...)`
- `session_witness_context(...)`
- requirement-id extraction only where it remains useful

**Why**
These are some of the cleanest “hard fact beats model claim” primitives in v1.

**V2 home**
- **Core**
- `BindEnv_r(...)`, `ExecutiveEnvironmentView`, `CommitmentEnvironmentHandle`, downward provenance collection

**Port shape**
- rename toward environment/provenance utility names
- keep them domain-general where possible

### D. Thin event normalization from `adapters.py`

**Keep**
- vendor event normalization into canonical internal lifecycle events
- payload field normalization
- extraction of native structured stop fields from host-native output surfaces

**Do not keep**
- any host-specific doctrine or startup prose assumptions as architecture

**V2 home**
- **Core** host drivers / realization support

**Port shape**
- keep it intentionally thin
- treat it as driver infrastructure, not semantics

### E. The v1 evidence discipline

**Keep fully in spirit, even if rewritten in code**
- shared harness discipline
- current-pair artifacts
- contradiction-preserving audit surfaces
- truthful-withheld packet logic
- explicit blocker truth

**Why**
This is at least as valuable as any single module. The archive’s strongest cultural win is that it stopped laundering contradictions.

**V2 home**
- implementation plan, validation harness, product-proof packet, release criteria

---

## 2.2 Port with rewrite: useful ideas, wrong old shape

These are worth carrying over, but only after being refactored into the v2 packet.

### A. `stop_signals.py`

**Keep**
- relation taxonomy over repeated failed attempts:
  - `identical`
  - `reduced`
  - `expanded`
  - `substituted`
- similarity over command/file/change signals

**Do not keep**
- v1 objective-gap doctrine
- proof-gap-as-center assumptions

**V2 home**
- mostly **SRE** (retry/branch/repair memory)
- maybe small **AUX** support for replay/evaluation
- not commitment certification

**Rewrite target**
- relation state over executive attempts / branch episodes / commitment candidates
- not over the old proof-shaped objective-gap map

### B. `requirements.py` / truth-evidence leaf utilities

**Keep conceptually**
- evidence-reference checking
- command normalization / command-claim matching
- file-claim normalization

**Do not keep as-is**
- v1 requirement-audit and truth-claim doctrine as the product center

**V2 home**
- **Core** microkernel provenance utilities

**Rewrite target**
- compact evidence manifest checking for commitment events
- domain-general evidence evaluators instead of coding-only path assumptions where possible

### C. `graveyard.py`

**Keep**
- cheap retrieval baseline
- token-overlap / FTS candidate narrowing
- explainability hooks

**Do not keep as doctrine**
- any overclaimed “semantic” framing
- any claim that this is the final memory model

**V2 home**
- **AUX**
- retrieval-shadow baseline / memory fallback / evaluation-first support

**Rewrite target**
- keep it removable
- keep it support-only
- treat it as baseline retrieval, not executive identity itself

### D. `store.py`

**Keep**
- WAL / local atomic engineering pattern
- compare-and-set style updates for counters and session state
- small local persistence discipline

**Do not keep**
- v1 schema as law
- old tables as architecture

**V2 home**
- shared runtime substrate under Core/SRE/AUX

**Rewrite target**
- new schema aligned to Core / SRE / AUX ownership
- no silent reuse of v1 stop-object tables

### E. OpenAI event-stream reconstruction

**Keep**
- App Server event reconstruction patterns
- mapping approval requests / command completion / turn completion into canonical internal events

**Do not keep as truth about the future**
- native OpenAI limitations as a permanent model

**V2 home**
- host-specific driver implementation, especially OpenAI

**Rewrite target**
- lifecycle-first, packet-first, host-native driver layer
- not bridge-shaped product identity

---

## 2.3 Do not port as-is

These are exactly the parts most likely to drag v2 back into v1.

### A. `StopVerdict`, `StopPathOutcome`, `StopPathRunner`, and the larger stop stack

Do not port as architecture.

The archive is explicit that the live v1 kernel is the flat `StopContract + StopVerdict + StopPathOutcome` model, and also explicit that there is still **no explicit boundedness term** in the acceptance law. That means this stack is battle-tested for commitment discipline, but not the right long-term product center.

**V2 action**
- mine it for narrow reusable leaf primitives only
- do not preserve the old stop-centered object model

### B. Prompt-heavy adapter shaping and retry doctrine

Do not port as architecture.

This includes:
- startup prose doctrine
- retry scaffolding as host doctrine
- prompt-heavy corrective layers as the assumed solution

These belong in the archive as experimental evidence, not in the v2 center.

### C. The old proof-surface bundle as a single acceptance object

Do not port:
- challenge / requirement / truth / invariant / proof bundle as the conceptual center
- objective-gap-as-product worldview
- “finish the proof” as the dominant state model

That is exactly what v2 is trying to leave behind.

---

## 3. Best v2 mapping table

| v1 artifact | Keep? | V2 destination | Port mode |
| --- | --- | --- | --- |
| `stop_payload.py` | yes | Core | port now |
| narrow `stop_contract.py` carrier-resolution slice | yes | Core | port now |
| `session_git_snapshot(...)` | yes | Core | port now |
| `session_changed_files_since_baseline(...)` | yes | Core | port now |
| `session_witness_context(...)` | yes | Core | port now |
| thin `adapters.py` normalization | yes | Core host drivers | port now |
| evidence-reference leaf utilities from `requirements.py` | yes | Core | port with rewrite |
| `stop_signals.py` relation taxonomy | yes | SRE / AUX | port with rewrite |
| `graveyard.py` baseline retrieval | yes | AUX | port with rewrite |
| `store.py` WAL / atomic persistence patterns | yes | shared substrate | port with rewrite |
| OpenAI App Server reconstruction ideas | yes | Core host driver infra | port with rewrite |
| `stop_policy.py` verdict law | no, not as-is | none | do not port as architecture |
| `StopPathOutcome` / `StopPathRunner` | no, not as-is | none | do not port as architecture |
| adapter retry doctrine / prompt-heavy shaping | no | none | archive only |
| v1 proof bundle as the product center | no | none | reject |

---

## 4. Port order

## Phase 1 — build the v2 core standard library from proven v1 leaves

Port first:
1. `stop_payload.py`
2. narrow `stop_contract.py`
3. provenance/environment helpers from `core_helpers.py`
4. thin event normalization from `adapters.py`
5. evidence-reference leaf utilities from `requirements.py`

This gives v2 a real commitment microkernel substrate without importing v1 architecture.

## Phase 2 — port battle-proven infrastructure

Port next:
1. `store.py` engineering pattern
2. OpenAI event reconstruction patterns
3. contradiction-preserving validation harness structure

This gives v2 battle-proven persistence and host-driver scaffolding.

## Phase 3 — port support memory only after core loop is stable

Port later:
1. `graveyard.py`
2. relation taxonomy from `stop_signals.py`
3. any offline-support carryover

This keeps support memory from becoming a premature architectural center.

---

## 5. Final recommendation

If this needs to collapse to one instruction:

**Steal the v1 commitment-carrier and provenance primitives, steal the thin host-event normalization, steal the evidence discipline, and rewrite everything else around the new Core / SRE / AUX packet.**

More bluntly:

- **port a v1 standard library**
- **do not port the v1 worldview**

That is the highest-leverage way to exploit the battle-proven parts of v1 without importing the exact proof-centered product shape that v2 is trying to replace.
