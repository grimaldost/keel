# Definition of Done (DoD gate)

The exit gate of **Review** / pre-merge. Deterministic where possible; the rest is
externalized into a blocking checklist. Fail closed — nothing green-lights itself.

## Deterministic gates (must pass, in CI and locally)

Six of these are field-derived and are what this list adds; the rest is the
bind-your-commands stub, which a project fills from its own toolchain. The last four came out of a
blind post-execution audit of seven governed series — 68 findings, three of them BLOCKER — whose
central answer was that a wrong PR could have gone green. Green certifies exactly what the gate
observes, and nothing constrained what a gate must observe.

- [ ] Each tool-wrapping gate asserts the tool **ran to completion** (exit status / no fatal
      halt), not just that error count ≤ baseline — a tool that bails early emits *fewer*
      errors than baseline and would otherwise pass green while checking nothing.
- [ ] Every durable artifact the spec / its ADRs reference is **tracked in version control** —
      `git ls-files --error-unmatch <path>` succeeds for each referenced path. A file can exist
      on disk and pass every content gate while a stray `.gitignore` rule silently drops it from
      the merge; no content check sees tracking. (A project MAY harden this into a guardrail
      script; this line is the project-agnostic floor. A design-only round that names the DoD
      phase skipped defers this predicate to the next execution round's gate.)
- [ ] **A red companion is a committed artifact the gate executes** — not a transcript in a notes
      file, not a mutation described in a commit message, not a reverted local plant. Four series
      in the audit accepted prose as proof, and one of them cited a mutation that had come back
      **green**. If the red cannot be re-run by the gate, nothing has been proven to anyone who
      was not watching.
- [ ] **A change that adds to a counted set pins that set's inventory** — tests, bindings,
      relations, gate lines. Gates observe absence-of-failure, so a deliverable that never arrives
      is indistinguishable from one that works: a pinned deliverable vanished entirely from one PR
      while both its checks stayed green, and five production bindings went missing without noise.
      A generic test *not added* fires nothing.
- [ ] **A check never regenerates in place what it validates** — it regenerates into a temporary
      location and compares. Four series ran drift gates that rewrote the corpus over the worktree
      before comparing, so any red self-heals on the second run. Where a baseline is *observed*
      rather than derived, label it as observed and pair it with a drift detector that is itself a
      check; at least one invariant per surface must not read the baseline the run itself wrote.
- [ ] **Every command the spec's Gate-commands section names maps to a check that runs**, or
      carries a named deferral with a trigger. A spec's independent oracle existed as a wrapper
      that skipped always, in two series, and was delivered with a syntax error inside a third —
      with nothing red, because nothing ran it.

The stub — bind the concrete commands per project in `method-bindings.md`:

- [ ] Formatter check passes (e.g. `ruff format --check .`).
- [ ] Linter passes (e.g. `ruff check .`).
- [ ] Type check passes (e.g. `mypy .`).
- [ ] Tests pass (e.g. `pytest`), including new tests for behavior changes.
- [ ] Project guardrail scripts pass (import boundaries, docs sync, budgets…).

## Review gate

- [ ] Reviewer verdict is APPROVE (or the salvage round closed every finding).
- [ ] No blocking item open on the project review checklist
      (`review-checklist.md`).
- [ ] The change is single-concern and cites exactly one spec section.

## Docs gate

- [ ] Public API / config / contract changes are reflected in docs.
- [ ] **Release notes in wave** — any section that adds public surface or changes behaviour
      carries its CHANGELOG entry (and a migration-guide section, if consumer-facing) in the SAME
      wave. Release-notes completeness is a per-wave exit condition, not a terminal-audit cleanup;
      a consistency gate (e.g. a docs-sync check) verifies cross-references, not completeness.

## Per-section gate

- [ ] The cited spec section's acceptance criterion is met.

**Merge only when every box is checked.**
