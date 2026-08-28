# ADR-0018: the bindings gate is un-deferred, and its findings carry no check letter

- **Status:** Accepted
- **Date:** 2026-08-28

## Context

ADR-0003 scaffolded `check_bindings` and `check_budget_drift` with no cited motivating failure, and
deferred both — "**Defer** … until a real failure demands them", with deferral as the live state
rather than a removal. That held for fourteen releases, and it was the right call: a gate built on
speculation is the "fourth system" ADR-0003 exists to prevent.

Two field failures now meet ADR-0003's own condition. Both are cited by report stem, labelled
maintainer-local and unpublished per ADR-0012, with the consumer project redacted:

- `2026-08-26-…-serving-respec` §Misses [HIGH]. A phase with a clear blast radius — six-plus
  planned PRs, a boundary between three repositories, shared contracts — was specified in four
  hand-written documents with no Definition-of-Ready and no pre-mortem, and nothing accused. The
  report's own words: *"nem o `method-bindings.md` (que morava num quarto repositório e não é lido
  por nenhum mecanismo no início de fase)"* — the bindings sheet lived in a fourth repository and
  is read by no mechanism at phase start. One of those four documents was later condemned whole by
  a rigour review; the one respecified with the method survived its implementation without a red.
- `2026-08-24-…-corrective-wave` #3 [MED]. The report's own words: *"apply-method leaves the
  executor choice to the session, where the harness-native orchestrator wins by in-context
  presence"*. The executor was a conditional the session resolved by whatever was already loaded.

Both are the same shape, and it is the shape a completeness gate answers: **the binding sheet
answers when asked, and never fires.** Neither is an argument for keel absorbing an engine concern
— which is what ADR-0003 was defending against — because neither asks keel to orchestrate anything.
They ask for the sheet keel already ships to be checkable.

## Decision

**`check_bindings` is built.** `keel bind-check <sheet>` reads a method-bindings sheet and reports
per slot.

1. **The binding column is resolved by header, never by position.** The two sheets that exist are
   three-, four- and two-column, and one of the shipped template's tables carried only the worked
   example. A last-column rule reads those examples as bindings — a permanent false negative — and
   a first-column rule reads slot names. The rule is: the column headed `This project` when the
   table has one, else the last column, which is right for a sheet with no example column at all.
   The template's Orchestrator table gains the missing `This project` column in the same change,
   because a gate that guesses around a defective template is worse than a repaired template.
2. **Three states, not two.** An empty cell **fails**. A cell opening `not bound` with a reason
   **warns** — that is the declared state this repo's own sheet uses for three slots and its
   closing line describes, and ADR-0003's whole posture is that a named deferral is a decision.
   `not bound` with no reason fails: a gap with a label on it is still a gap.
3. **Findings carry no check letter.** `CHECK_IDS` is the *spec* gate's closed catalogue — what the
   Part-A reference block enumerates, what the hit-rate ledger counts, and what the adversarial
   corpus stages a positive control for. That corpus stages specs, so a bindings letter could never
   earn one, and a letter with no control is exactly what CONTRIBUTING's gate-health rule 1a
   forbids. The identity problem the letters solved does not arise here: this gate's `where` is the
   slot name, and slot names do not collide. `Violation.check` already defaults to empty for a
   consumer outside the spec gate.

**`check_budget_drift` stays deferred.** No failure cites it, and its disposition in the backlog is
removal rather than construction (KEEL-B30) — un-deferring it here would be the speculative
generality ADR-0003 rejected. `tests/test_gate_contracts.py` keeps pinning its stub.

## Alternatives considered

- **Keep deferring.** Rejected: ADR-0003 set a condition and the condition is met. A deferral whose
  trigger fires and is not honoured stops being a decision and becomes an omission.
- **Couple `check-ready` to the bindings sheet** — fail a spec whose manifest has two or more PRs
  when the series-orchestration slot is unbound. Rejected for now: `check-ready` has no way to find
  a project's bindings sheet, its 0/1/2 contract is pinned, and coupling two gates to answer one
  question is a bigger step than the evidence buys. `bind-check` gives the executor question a
  machine; whether the spec gate should consult it is a separate decision on separate evidence.
- **Give the bindings gate its own letters** (`K1`, `K2`). Rejected per decision 3: a letter
  without a positive control is a claim the suite cannot check.

## Consequences

- `keel bind-check` moves from **stub** to **real** in `docs/cli-reference.md`, and
  `tests/test_gate_contracts.py` has one gate left to pin.
- The shipped template's Orchestrator table changes shape. A project that already copied the kit
  keeps a two-column table whose last column is its binding — which the header rule reads
  correctly, so the change is additive for existing adopters.
- Running this repo's own sheet through the gate is now part of what the suite asserts, so keel's
  three deliberately-unbound slots stay declared rather than drifting into blanks.
- The executor question has a machine but not yet a verdict: `bind-check` can say the
  series-orchestration slot is unbound; nothing yet blocks a multi-PR spec on it. That is
  deliberate, and it is the next decision rather than this one.
