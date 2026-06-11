# Definition of Done (DoD gate)

The exit gate of **Review** / pre-merge. Deterministic where possible; the rest is
externalized into a blocking checklist. Fail closed — nothing green-lights itself.

## Deterministic gates (must pass, in CI and locally)

- [ ] Formatter check passes (e.g. `ruff format --check .`).
- [ ] Linter passes (e.g. `ruff check .`).
- [ ] Type check passes (e.g. `mypy .`).
- [ ] Tests pass (e.g. `pytest`), including new tests for behavior changes.
- [ ] Project guardrail scripts pass (import boundaries, docs sync, budgets…).
- [ ] Each tool-wrapping gate asserts the tool **ran to completion** (exit status / no fatal
      halt), not just that error count ≤ baseline — a tool that bails early emits *fewer*
      errors than baseline and would otherwise pass green while checking nothing.

*(Bind the concrete commands per project in `method-bindings.md`.)*

## Review gate

- [ ] Reviewer verdict is APPROVE (or the salvage round closed every finding).
- [ ] No blocking item open on the project review checklist
      (`review-checklist.md`).
- [ ] The change is single-concern and cites exactly one spec section.

## Docs gate

- [ ] Public API / config / contract changes are reflected in docs.

## Per-section gate

- [ ] The cited spec section's acceptance criterion is met.

**Merge only when every box is checked.**
