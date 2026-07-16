# Templates reference

The portable kit (`src/keel/templates/`, emitted by `keel init`):

| Template | Purpose |
|---|---|
| `adr-template.md` | One numbered decision; names the invariant it creates. |
| `spec-template.md` | DoR-ready-by-construction spec (Non-goals, Invariants touched, concept→module map, PR↔section manifest). |
| `definition-of-ready.md` | Exit gate of Specify: Part A (deterministic) + Part B (certified by a non-author reviewer). |
| `definition-of-done.md` | Exit gate of Review / pre-merge; fail-closed. |
| `review-checklist.md` | Blocking reviewer checklist; the promotion target for reflections. |
| `reflection-triage.md` | Sweep prior open rows; cluster reflections; promote recurring traps to checklist/gate/spec and land them. |
| `series-toml-skeleton.md` | The `[budget]` block, per-PR `section = "§N"` traceability, and the tier-vocabulary note (family names; the binding translates). |
| `method-bindings.md` | Bind each portability slot to a concrete mechanism (per project). |
| `pre-mortem-prompt.md` | Adversarial pre-execution pass; output = spec/prompt edits only. |
| `method-agents-snippet.md` | Paste-ready `AGENTS.md` block routing any agent into the method (bindings first, `keel show doctrine`, the DoR gate, the portable pre-mortem). |
| `README.md` | The kit's own index (slot → file mapping). |
