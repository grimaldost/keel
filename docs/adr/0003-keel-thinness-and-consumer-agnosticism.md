# ADR-0003: keel thinness & consumer-agnosticism

- **Status:** Accepted
- **Date:** 2026-06-06

## Context

The 2026-06-05 review panel (critique #6) and the 2026-06-06 field waves pressed on the same
risk: keel sits atop three pre-existing systems (a single-unit discipline, a series
orchestrator, a cross-series memory) and could bloat into a *fourth* — absorbing engine
concerns (orchestrator resilience, the salvage workflow) and consumer-specific knowledge (one
project's typing/dispatch rules). The doctrine also named specific tools (superpowers /
pr-pilot / cognitive-memory) directly in its mechanism map — a portability leak, since the
agnostic contract should be separable from per-project bindings. Two gates
(`check_budget_drift`, `check_bindings`) were scaffolded with no cited motivating failure.

## Decision

keel stays **thin and consumer-agnostic**:

- keel is the **connective doctrine + the gates that live nowhere else** (Definition-of-Ready,
  reflection-triage). It does not re-implement what the three systems already do.
- The doctrine names **roles** (single-unit discipline / series orchestration / cross-series
  memory); specific tools are **reference bindings**, bound per project in `method-bindings.md`.
- **Defer** `check_budget_drift` and `check_bindings` until a real failure demands them.
  "Defer" means their `NotImplementedError` stubs and the `tests/test_gate_contracts.py`
  contract that pins them remain **intact, not removed** — deferral is the live state.
- Feedback flows **up** only: keel extracts the project-agnostic lesson and **declines**
  project- or engine-specific residue (the reporter owns it). keel never files into, or tracks
  the fate of, a consumer.

## Alternatives considered

- **Build all scaffolded gates for completeness** — rejected: speculative generality (YAGNI)
  with no cited motivating failure (panel critique #6).
- **Absorb the long-run resilience playbook / project review knowledge into keel** — rejected:
  those are engine and project concerns; absorbing them makes keel the fourth system it must
  not become.
- **Full slot-ification of the doctrine now** (replace every tool name with an abstract slot)
  — rejected for now: deferred until keel is bound to a *second* project, the real portability
  test; rewriting the source-of-truth ahead of that evidence is premature churn.

## Consequences

- **New invariant:** keel is consumer-agnostic — feedback is up-only, residue is declined not
  tracked, and keel never reaches down into a consumer. This becomes a review-checklist guard.
- `check_budget_drift` / `check_bindings` stay stubbed with their contract test green; a future
  wave un-defers them only against a real failure.
- Doctrine reads role-first; `method-bindings.md` is the home for concrete tools.
- Easier: keel stays portable and small. Harder: the tempting "just add it to keel" is
  resisted, and cross-repo fixes are made in their own repos, not mirrored here.
