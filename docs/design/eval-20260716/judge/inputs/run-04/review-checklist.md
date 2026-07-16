# Review checklist (starter)

Injected into the reviewer and blocking: any unchecked item is `REQUEST_CHANGES`.
Start from these project-agnostic items and add project-specific ones.

This file is also the **promotion target for reflection triage** (Upgrade 3):
when a trap recurs across rounds, add a line here so it is caught mechanically
next time. That is how "a bug bites once" actually holds.

## Generic items

- [ ] **Scope** — single concern; cites exactly one spec section; no unrelated
      refactor ("while I'm here").
- [ ] **Correctness** — does what the cited section's acceptance criterion says.
- [ ] **Invariants** — respects every boundary/lock/immutability/contract named in
      the spec's "Invariants touched".
- [ ] **Typing** — fully typed; no new type-checker suppressions without reason.
- [ ] **Errors** — no silent `except`; failures surface; user-facing errors use the
      project's error format.
- [ ] **Tests** — behavior changes have tests; tests assert behavior, not
      implementation; no skip/xfail added to mask a real failure.
- [ ] **Docs** — public API/config/contract changes are documented.
- [ ] **No coupling smell** — no reaching through `getattr`/private attrs to dodge
      a boundary.
- [ ] **Gate completion** — every type/lint/test gate ran to completion (exit 0, no
      "fatal" / "source file found twice" halt), not merely error-count ≤ baseline; a
      checker that bailed early must fail the gate, not pass it.

## Project-specific items

- [ ] **Contract shape** — `src/tempo/contract.py`'s record shape and `LEVELS` are the
      shared contract for `parse.py`, `report.py`, and external consumers (per
      `contract.py`'s own module docstring); any PR that changes the record tuple shape
      or field order names every consumer it touches, not just the two in-tree modules.
- [ ] **Positional vs. keyword record access** — a PR adding a field to the record tuple
      checks every unpack site (`epoch, level, message = ...`-style) for silent
      misassignment, not just call sites that already fail loudly.
- [ ] **Backward compatibility during the multi-PR window** — while the source-host
      refactor spans multiple PRs, each individual PR leaves `make_record` and every
      caller in a working, testable state (per its own spec-section acceptance
      criterion) — no PR may depend on a later PR to not be broken.

---
*Keep this file in version control with the project. Each promoted reflection
should cite the round/PR that motivated it, in a comment.*
