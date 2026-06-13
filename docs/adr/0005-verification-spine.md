# ADR-0005: the verification spine (ground the verification, model the mechanical consumers, verify the transformation)

- **Status:** Accepted
- **Date:** 2026-06-13

## Context

The 2026-06-13 post-0.4.0 field triage (19 reports, `docs/feedback/2026-06-13-post-040-field-triage.md`)
plus a four-lens independent review found the 0.4.0 spine (A8/A9/A10, structured findings, the verified
fold) validated, with the residual misses collapsing to three generative causes a level out from
ADR-0004's "ground referents, verify the fold":

1. **DC1 — the oracle problem.** A claim the author "verified" is wrong when the verification reused a
   partial / stale / moved / wrong-shaped view: a `src`-only grep, the known exemplars rather than the
   population, one table read as a whole file, a line-range ending inside a literal, a dependency whose
   SHA moved mid-session. A verifier's own script (a purity grep, a count regex) is itself such an artifact.
2. **DC2 — map vs territory at the toolchain boundary.** The spec models the logical design, but the
   in-place toolchain consumes the artifact too: a staged `.py` polluting `mypy .`, a diff-shape constraint
   contradicted by isort. Caught three times across three gates, each a phase too late.
3. **DC3 — the unverified delta.** The fold/fix is an instance-scoped, unreviewed transformation: 12
   findings folded produced 11 half-folds in one wave; a fix removed one of two instances of a defect
   class; a CERTIFIED verdict never confirmed the prescribed fix landed.

A keystone defect was also verified: the bundled `pre-mortem-review` agent had drifted two minor versions
behind `pre-mortem-prompt.md` — a DC1/DC3 bug in keel itself (the running prompt ≠ the documented one) —
so judgment-class doctrine never reached the field through the bundled agent.

## Decision

- **Doctrine sharpening 5** names the three causes as the extension of sharpening 4 (ground the
  verification's scope/shape/currency; model the mechanical consumers; verify any transformation via a
  per-finding ledger and class scope).
- **Two new Part-A checks** (extending ADR-0002's form/correctness split, checked-when-present):
  - **A11** — a `path:lo-hi` range anchor must close (string/comment-aware) every bracket it opens; a
    truncated citation is a malformed observation window. Single-line `path:line` anchors stay A6 (a shared
    `_resolve_anchor` helper backs both — a behaviour-preserving extraction).
  - **A12** — when a `### Fold ledger` sub-table is present in the certification block, every row's
    `artifact:line` confirmation anchor must resolve. It verifies the fold was *recorded* against a real
    line, never that it is correct (that stays Part B).
- **R1 — a claimed fold requires a ledger** (a deliberate DoR tightening, NOT verify-when-present): a
  CERTIFIED spec whose certification "folded in" field names a non-trivial fold must carry a `### Fold
  ledger` with at least one resolving row, so the DC3 transformation-verification cannot be skipped by
  omission. A clean certify (folded in: none) dozes.
- **The pre-mortem layer carries DC1/DC2/DC3 as directives** (`pre-mortem-prompt.md`), and the bundled
  agent is rewritten to mirror it with a **drift guard** (`tests/test_premortem_agent.py`): a shared marker
  set must appear in both files, so neither can silently drift again — the **agent ⇄ prompt fidelity**
  invariant.
- **A verification-convergence rule** bounds the hardened passes: a pass stops at zero new BLOCKER/MAJOR
  findings; `CONDITIONAL-CERTIFY` covers "ready modulo a named ≤N-line fix".
- **CLI ergonomics:** `keel --version`; `check-ready --structure-only` (Part A only) for the author loop.

## Alternatives considered

- **Mechanize DC1/DC2/DC3 fully as gates** — rejected: population-completeness, staged×gate simulation,
  and text-consumer enumeration are irreducibly semantic (ADR-0002 Part B); a gate would manufacture the
  false confidence ADR-0002 exists to remove. Only the syntactic slices (A11 anchor shape, A12 anchor
  resolution) are mechanized.
- **An A12 "ledger exists" presence gate** — rejected as vacuous-by-construction (it cannot fail for a
  determined author). A12 instead requires each row's confirmation to be a *resolving* anchor — exactly
  what A6 does not already cover (a blank or prose cell fails).
- **Keep the fold ledger fully verify-when-present (no R1)** — rejected: that leaves DC3's mechanized
  half opt-in (a 12-finding fold with no ledger sails through — the K1 "11 half-folds" class). R1 is a
  deliberate carve-out from "extend never break": it affects only a spec that *claims* a fold without
  evidencing it (which should fail); a clean certify is unaffected.
- **A cardinal-vs-enumeration lint (N6b)** — held at `watch`: the false-positive risk on prose
  enumerations is too high (the same reason ADR-0004 declined to mechanize the coherence re-read).
- **A publish-readiness gate or template (N9a)** — declined for core: repo-publication hygiene is not a
  method/DoR concern; bundling it (as a gate or a template) would breach thinness (ADR-0003). It stays a
  standalone repo script.

## Consequences

- A11/A12 join A1–A10; each ships a regression test (the gate-health rule). A11 and A12's anchor-resolution
  are checked-when-present, so existing specs do not retro-break, and A6's behaviour is unchanged behind
  the extracted resolver.
- **R1 tightens the DoR** beyond verify-when-present: a spec that folds findings must carry a ledger.
  keel's own 0.5.0 spec carries one (the dogfood); a consumer's prior prose-fold spec goes red on re-run
  until it adds a ledger — the intended teeth, not a regression.
- The bundled pre-mortem agent now matches keel's doctrine and is pinned against future drift; the
  `agent ⇄ prompt fidelity` invariant is enforced by a test.
- New optional authoring conventions: the `### Fold ledger` table (A12) and the `path:lo-hi` range anchor
  (A11); a `Reviewed against:` SHA field; a removal/rename/retype text-consumer checklist (directive).
- **Routed out** (separate ledgers, ADR-0003): engine/execution-resilience (silent engine-loss, the
  watchdog), the cost model, and scaffold employer-identity defaults → pr-pilot; keel keeps only the
  project-agnostic doctrine fragment and does not track their fate.
- **Extends ADR-0002 and ADR-0004**; it does not supersede them.
