# Definition of Done (DoD gate)

The exit gate of **Review** / pre-merge. Deterministic where possible; the rest is
externalized into a blocking checklist. Fail closed — nothing green-lights itself.

## Deterministic gates (must pass, in CI and locally)

Two of these are field-derived and are what this list adds; the rest is the
bind-your-commands stub, which a project fills from its own toolchain.

- [ ] Each tool-wrapping gate asserts the tool **ran to completion** (exit status / no fatal
      halt), not just that error count ≤ baseline — a tool that bails early emits *fewer*
      errors than baseline and would otherwise pass green while checking nothing.
- [ ] Every durable artifact the spec / its ADRs reference is **tracked in version control** —
      `git ls-files --error-unmatch <path>` succeeds for each referenced path. A file can exist
      on disk and pass every content gate while a stray `.gitignore` rule silently drops it from
      the merge; no content check sees tracking. (A project MAY harden this into a guardrail
      script; this line is the project-agnostic floor. A design-only round that names the DoD
      phase skipped defers this predicate to the next execution round's gate.)

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
