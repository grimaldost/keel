# Spec — <feature/refactor name>

- **Date:** YYYY-MM-DD
- **Status:** draft | ready (DoR passed) | in progress | done
- **Kit:** 0.15.0
- **Kind:** series
- **Audience:** <who/what reads this>
- **Output artifact(s):** <paths>

*`Kind:` is resolved, not a menu: leave `series`, or write `single-change` for a spec with nothing
to decompose — doctrine §3 states what each declaration relaxes. `Kit:` is the kit this spec was
scaffolded from; keep it, and W1 warns on skew and on its absence.*

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

*A10: no prose may claim an invariant "enforced" or "guaranteed" unless its row here reads
`enforced`. Checked only when this table is present; a backticked or negated claim does not fire.*

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| <concept> | `path/to/module` |

*Every concept maps to a home; one with no module is a DoR failure. Mark a new path
"(to be created)" and name it — full path, or bare basename when unique — in the body of the
§ that creates it (A5).*

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

*Ground factual claims with `path:line` anchors, repo-root-relative (`src/pkg/mod.py:NN`). The
backticked token right after an anchor IS its snippet: A6 requires an exact substring of that line,
so never backtick prose or an elision there. A bare anchor verifies the address; a claim-supporting
anchor carries its snippet, so the gate verifies the evidence, not just the address.*

*Reuse notation: pin a target as `**Model-on:** <backticked path>` or
`**Reuse:** <backticked path::symbol>`; A9 resolves the path, and the symbol when given.*

*Anchor ranges: a multi-line citation is `` `path:lo-hi` ``; A11 resolves the file and the `hi`
line, and for a `.py`/`.pyi` anchor flags a range that opens a bracket it never closes. Quote a
literal complete or not at all.*

*Gate-adversarial examples: when the spec must QUOTE something the gate scans for — a literal
`Verdict:` line, a to-do token, an example `### heading` — fence it. Fenced content is masked before
every check; unfenced, it false-fails A3 or shadows the certification.*

*Measurement / experiment specs: the experiment-design axes, and the DoR items that gate them, live
in `pre-mortem-profiles.md`. Fill that sheet and name it here.*

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |

*Every section must be covered by exactly one PR, and every PR must cite exactly
one section. A many-to-one or uncovered section is a DoR failure.*

## Definition of Done (this spec)

Concrete, checkable conditions for the whole spec (beyond per-section criteria).

- Generated / mirrored / snapshot artifacts downstream of touched surfaces
  (consumer-reference mirrors, golden fixtures, lockfiles), each with its freshness gate —
  or the word "none": <enumerate them here; the pre-mortem challenges this declaration>
- The `definition-of-done.md` conditions for this project, including release notes in wave.

## Pre-mortem certification

*The externalized correctness pass (`pre-mortem-prompt.md`), certified by a reviewer who did NOT
author this spec; the gate does not pass until the verdict is `CERTIFIED` (ADR-0002), so a
freshly-scaffolded spec is correctly not Ready. Save the pass's output to
`<spec-stem>.premortem.md` with a `Spec-hash:` from `keel spec-hash` and name it below: B2 then
verifies existence, verdict agreement and hash currency. That raises the cost of forging a
certification; it does not prove the pass was blind.*

- **Reviewer:**
- **Verdict:** not yet certified
- **Operator:** <required only when the Verdict is CONDITIONAL-CERTIFY — the named owner who accepts "ready modulo a named fix"; check-ready then passes with a WARN (B1). If the Operator applies the conditions, the verdict stays CONDITIONAL-CERTIFY with a discharge note — the operator close, definition-of-ready.md Part B>
- **Certification artifact:** <the saved pass output's path. `check-ready` reads the LEADING path token and ignores what follows, so a prior round belongs right here: `<stem>.premortem.md` (r1 at `<stem>.premortem-r1.md`)>
- **Date:**
- **Reviewed against:** <external dependency SHAs/versions reasoned against, if any>
- **Post-fold coherence:**
- **Failure modes considered & folded in:**

### Fold ledger

*Required when the certification claims a non-trivial fold (R1); a clean certify dozes. One row per
folded finding. A12 holds each `artifact:line` — or `artifact:lo-hi` — to a resolving anchor:
recorded against a real line, not that it is right. A backticked snippet after it is verified
against those lines, and a `.py` range must close its brackets. Header only and A12 dozes; the
ledger is the FIRST table under this heading.*

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|

---
*Most Definition-of-Ready checks pass by construction here — numbered sections, per-section
criteria, the concept→module map, the manifest. The one that cannot is the pre-mortem
certification: a non-author reviewer must sign it, which is the point (ADR-0002).*
