# Concepts

keel is one method at three nested scopes: **task ⊂ series ⊂ program**.

- **Single-unit discipline** governs a single unit of work (brainstorm → plan → TDD → review
  → finish). *Reference binding:* a process-discipline pack (e.g. humblepowers).
- **Series orchestration** governs a series of units (the wave/PR DAG, gates between phases,
  model routing, injections, reflection extraction). *Reference binding:* a `series.toml`
  orchestrator (e.g. convoy, which runs the DAG, the gates and model routing; injections and
  reflection extraction then stay with the project).
- **Cross-series memory** governs across series (journals → meditation → doctrine). *Reference
  binding:* a consolidating memory store; keel's `docs/doctrine.md` is the doctrine tier.

Inside a series, tasks ship in **waves** — "the batch it ships with", the spec
template's `Wave` column; a wave is not a fourth scope. The eight **phases**
(`phases-reference.md`) say where in the lifecycle a unit is, and "phase" in keel means one
of those eight. A **round** is one repetition of a pass (a pre-mortem round; a work round
through a named subset of the phases, doctrine §3). A project's own nouns and identifiers
for its programs, periods and decisions are bound in its `method-bindings.md`, never here.

keel is the connective doctrine + the gates that live nowhere else (Definition-of-Ready,
reflection-triage). It links to the three systems; it does not restate their mechanics.

The method's value is observed across three governed waves; the comparative claim — that it
beats a disciplined baseline — is retired, unmeasured (ADR-0015; see `docs/evidence.md`).

**When to use it:** apply the method when the work clears a blast-radius trigger — ≥5 PRs, a
chokepoint imported by ≥~50 modules, additive-only on a shared contract, a boundary crossing,
or a >1-quarter lifetime (see `docs/doctrine.md` §6). It is overhead for a throwaway script.
The method applies its own scope discipline to itself.
