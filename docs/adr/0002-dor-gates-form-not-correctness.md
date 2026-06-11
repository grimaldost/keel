# ADR-0002: DoR gates well-formedness, not correctness

- **Status:** Accepted
- **Date:** 2026-06-05

## Context

A 5-lens blind review panel on keel's design
(`docs/feedback/2026-06-05-review-panel.md`) returned unanimous `REVISE`. Its
central, independently-reproduced finding: the Definition-of-Ready gate externalizes
*form* but not *correctness*. Part A's checks are syntactic (numbered sections, no
`TODO`, a PR↔section bijection) — all satisfiable by a vacuous-but-well-formed spec.
The only checks that catch a confidently-wrong spec live in Part B, which the spec
author signs — re-importing in-session judgment at the exact joint method sharpening
1 names as the single point of failure. The pre-mortem, the one mechanism aimed at
"this approach is wrong," was "(Recommended)".

`check_spec_ready` was a stub. Implementing Part A alone would ship a green gate that
reads as "Ready" on structure alone — the panel's flaw, deployed.

## Decision

DoR gates **well-formedness, not correctness.** `check_spec_ready` passes a spec only
when it is (Part A) well-formed AND (Part B) carries a recorded blind pre-mortem
certification. Correctness is **externalized to a fresh, non-author reviewer** whose
verdict is recorded in an in-spec `## Pre-mortem certification` block; the gate is the
deterministic machine that refuses to pass until that judgment was recorded. The
pre-mortem is promoted from Recommended to **required**. The "symmetric to the
Definition of Done" framing is dropped: DoD checks behaviour against an executable
oracle (tests, types); DoR has no oracle for "the approach is right," so its
correctness half is an externalized human judgment, not a machine verdict.

## Alternatives considered

- **Rename-only** (Part A + an honest label; pre-mortem stays a manual step) —
  rejected: fixes the false-confidence half but leaves the panel's "the antidote is
  optional" flaw to human discipline; the gate still passes on structure alone.
- **Separate companion artifact** (`<spec>.premortem.md`) — rejected for now: two
  files to keep in sync and a second path to resolve, for the same guarantee an
  in-spec block gives.
- **Make Part A judge correctness** — rejected as a category error: "is this approach
  right?" is not machine-checkable; a deterministic check claiming to verify it would
  manufacture the very false confidence this ADR removes.

## Consequences

- **New invariant:** a spec is Ready only when a `## Pre-mortem certification` block
  with `Verdict: CERTIFIED` and a non-empty, non-author `Reviewer:` is present.
  `check_spec_ready` enforces it; `spec-template.md`, `definition-of-ready.md`, and
  `pre-mortem-prompt.md` bind to it. This invariant becomes a review-checklist item.
- **Named residual limit (honest, not hidden):** the gate verifies a certification was
  *recorded*, not that the reviewer was truly blind or competent. That trust is named
  here rather than buried in a green checkmark — the difference between this gate and
  the soft center it replaces.
- Part A's `A2` (acceptance criteria) and `A5` (paths) detect absence/triviality, not
  semantic correctness; Part A's job is well-formedness only.
- Easier: a confidently-wrong-but-tidy spec can no longer earn "Ready" silently.
  Harder: every spec now needs a blind pre-mortem pass before decompose — the intended
  cost, paid where it is cheapest (before any code).
