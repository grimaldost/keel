# Templates reference

The portable kit (`src/keel/templates/`, emitted by `keel init`):

| Template | Purpose |
|---|---|
| `adr-template.md` | One numbered decision; names the invariant it creates. |
| `spec-template.md` | DoR-ready-by-construction spec (Non-goals, Invariants touched, concept→module map, PR↔section manifest). |
| `definition-of-ready.md` | Exit gate of Specify: Part A (deterministic) + Part B (signed). |
| `definition-of-done.md` | Exit gate of Review / pre-merge; fail-closed. |
| `review-checklist.md` | Blocking reviewer checklist; the promotion target for reflections. |
| `reflection-triage.md` | Cluster reflections; promote recurring traps to checklist/gate/spec. |
| `series-toml-skeleton.md` | The `[budget]` block + per-PR `section = "§N"` traceability. |
| `method-bindings.md` | Bind each portability slot to a concrete mechanism (per project). |
| `pre-mortem-prompt.md` | Adversarial pre-execution pass; output = spec/prompt edits only. |
| `README.md` | The kit's own index (slot → file mapping). |
