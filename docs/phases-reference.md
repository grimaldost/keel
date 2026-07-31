# Phases reference

Each phase has an artifact, an entry gate (Ready), and an exit gate (Done).

| Phase | Artifact | Entry (Ready) | Exit (Done) |
|---|---|---|---|
| 1 Decide | Numbered ADR | A choice with non-obvious trade-offs | ADR written, numbered, Accepted |
| 2 Specify | Spec w/ numbered sections + concept DAG | Relevant ADRs exist; scope bounded | **Definition-of-Ready** passes (`keel check-ready`) |
| 3 Decompose | Wave/PR DAG (`series.toml`) | Spec sections stable | Each PR cites one section; deps are a DAG |
| 4 Route & Budget | Per-PR score → tier; wave estimate | PR prompts precise enough to score | Each PR tiered; wave budget + drift gate set |
| 5 Implement | Branch/diff per PR | Prompt + spec section in hand; fresh context | Single-concern; no invariant violated |
| 6 Gate | Deterministic gate results | Implementation believes it is done | format/lint/type/test + guardrails pass (fail-closed) |
| 7 Review | Reviewer verdict vs checklist | Gates green | **Definition-of-Done** met; APPROVE or salvage closed |
| 8 Reflect | Reflection entries | PR merged | **reflection-triage**: recurring traps promoted |

keel gates: phase 2 → `keel check-ready` (+ the pre-mortem pass); phase 4 → `keel budget-drift`;
phase 8 → the `/keel-triage` slash command, which drives `reflection-triage.md`.
(`keel check-ready` is live as of 0.2.0; `keel budget-drift` is still a stub — deferred,
ADR-0003 — and the phase-8 loop is a template procedure, not a deterministic gate.)
