# Spec — <feature/refactor name>

- **Date:** YYYY-MM-DD
- **Status:** draft | ready (DoR passed) | in progress | done
- **Audience:** <who/what reads this>
- **Output artifact(s):** <paths>

## Context

Why this work, and what it builds on (link the relevant ADRs).

## Goal

One or two sentences: what this delivers.

## Gate commands

The exact commands that gate this work, named precisely (scope and excludes included) so
prompts and reviewers don't guess: e.g. `ruff check .`, `uv run pytest`, and the project's
type-check invocation. State *which* command, not "the linter".

## Non-goals

What this explicitly does NOT cover. Bounds scope so workers can't sprawl.

## Invariants touched

List every architectural invariant this work could affect (boundaries, locks,
immutability, schema contracts...). Each must already have an ADR; if not, write
the ADR first. *Naming these is a DoR requirement.*

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| <invariant key> | enforced \| review-only \| planned \| absent | <the gate, when enforced> |

*check-ready (A10): no prose may claim an invariant is "enforced" / "guaranteed" unless its
row here is `enforced`. Checked only when this table is present; a claim inside backticks, or
one negated ("not enforced", "to be enforced later"), does not fire.*

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| <concept> | `path/to/module` |

*Every concept must map to a home. A concept with no module is a DoR failure.*

## Numbered sections

Each numbered section is a unit of work a single PR can cite. Keep them small and
single-concern.

### §1 <title>
What changes. **Acceptance criterion:** <the observable condition that means §1 is
done>.

### §2 <title>
What changes. **Acceptance criterion:** <...>.

*(Add sections as needed. Every section needs an acceptance criterion — this is
both a DoR check and each PR's exit gate.)*

*Ground factual claims with `path:line` anchors (optionally followed by a quoted line in
backticks) — `check-ready` verifies they resolve and match. Cite a new ADR as
`docs/adr/NNNN-slug.md` using the next free number on your base, never a hardcoded guess.*

*Reuse notation: pin a reuse target as `**Model-on:** <backticked path>` or
`**Reuse:** <backticked path::symbol>`; `check-ready` (A9) resolves the path, and the symbol
when given — so a spec cannot say "model-on / reuse X" without X actually existing.*

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |

*Every section must be covered by exactly one PR, and every PR must cite exactly
one section. A many-to-one or uncovered section is a DoR failure.*

## Definition of Done (this spec)

Concrete, checkable conditions for the whole spec (beyond per-section criteria).

## Pre-mortem certification

*The externalized correctness pass (`pre-mortem-prompt.md`), signed by a fresh
reviewer who did NOT author this spec. `keel check-ready` does not pass until the
verdict is `CERTIFIED` (ADR-0002). A freshly-scaffolded spec is, correctly, not Ready.*

- **Reviewer:**
- **Verdict:** not yet certified
- **Date:**
- **Post-fold coherence:**
- **Failure modes considered & folded in:**

---
*This template is structured so that most of the deterministic Definition-of-Ready
checks (`definition-of-ready.md`) pass by construction: numbered sections,
per-section acceptance criteria, the concept→module map, and the PR↔section
manifest are all required fields. The one field NOT satisfied by construction is the
pre-mortem certification — a non-author reviewer must sign it, which is the point
(ADR-0002).*
