# ADR-0006: the adoption surface & cross-artifact completeness

- **Status:** Accepted
- **Date:** 2026-06-14

## Context

The post-0.5.0 field round (`docs/feedback/2026-06-14-post-050-field-triage.md`, 5 reports across a
real second/third binding) found the 0.5.0 verification spine validated — R1/A12 "could not be faked",
the bundled agent in lock-step with the prompt, the two-pass cadence catching load-bearing BLOCKERs on
the 8th and 9th consecutive waves. The residual misses cluster in two places ADR-0005 did not reach:

1. **The on-ramp is rough.** An external author needed four `check-ready` runs to green: nothing
   pointed at `spec-template.md`; A2 false-negatived a line-wrapped `**Acceptance criterion:**` marker
   (also a self-hit during the 0.5.0 build); B1 rejected `CERTIFIED.` followed by prose. The gate is
   correct; adopting it costs more than it should.
2. **Cross-artifact / cross-PR completeness.** A generated consumer mirror (`*_api.md`) went stale
   because a *later PR in the same wave* mutated its source surface; a freshness test the DESIGN
   *named* for the reviewer subset never reached the executable REVIEW command; cumulative
   release-notes silently under-covered three waves' surfaces and a behaviour change; an eval spec
   certified clean but could not discriminate (10 of 11 criteria ceilinged). The gap is *between
   artifacts that must agree*, which per-wave/per-PR gates structurally cannot see — the DC4-B axis
   (cross-artifact standing consistency) the 0.5.0 backlog had left at `watch`.

## Decision

- **§1 / §2 sand two existing Part-A checks (no new check letter).**
  - **A2** matches `acceptance\s+criterion`, so a hard-wrapped marker is found. Widen-only.
  - **B1** reads the verdict's leading token — the longest leading run of letters and hyphens
    (`^\s*([A-Za-z][A-Za-z-]*)`) — and passes only on `CERTIFIED`; trailing prose is allowed, but a
    hyphenated compound is captured whole, so `CERTIFIED-NOT` still fails. The error states the
    bare-token contract. Widen-only, with a regression test that the hole stays closed.
- **§3 `keel new-spec <path>`** stamps `spec-template.md` (a small new single-file helper, not the
  directory-copy `copy_templates`), and `check-ready` appends a one-line pointer to the template when a
  violation reports a *missing top-level structure* (the A1/A4/A5 closed set: `where` in
  {Numbered sections, PR ↔ section manifest, Concept → module map} and message begins `no `). A
  content-level failure does not trigger it.
- **§4 the drift guard rises to distinctive per-directive tokens.** `tests/test_premortem_agent.py`
  keeps its substring mechanism but pins one distinctive verbatim token per directive, including the
  new §5/§7 ones — so the ADR-0005 agent ⇄ prompt fidelity invariant holds as directives are added.
- **§5 / §7 the pre-mortem gains cross-artifact-completeness directives**, inserted *verbatim and
  byte-identical* into both `pre-mortem-prompt.md` and `agents/pre-mortem-review.md`: a cross-PR
  generated-artifact-invalidation bullet (a later PR mutates a mirror's source → re-run the generator,
  test on the full tree), an intent→executable cross-artifact bullet (a test the design names for the
  reviewer subset must appear in the executable command), and a stress-test-recorded-predictions bullet
  (a "predicted signal" is a claim to attack — could it floor/ceiling?). **§6** adds a
  release-notes-in-wave Definition-of-Done item and a doctrine note blessing the cross-cutting
  blind audit (the consumer's DoD#9-style panel) as the pre-cut pattern; **§7** adds a DoR Part-B
  discriminating-power item for eval/experiment specs.

## Alternatives considered

- **Add a new deterministic A-letter for the cross-artifact class** — rejected: the design-named
  reviewer-subset and the REVIEW command are the *orchestrator's* artifacts (pr-pilot), not keel's; a
  keel gate could not be project-agnostic and would breach thinness (ADR-0003). keel carries the
  directive; the executable diff and full-tree-freshness enforcement route to pr-pilot.
- **A discriminating-power / construct-validity gate** — rejected: whether a design *can answer its
  question* is irreducibly semantic (ADR-0002 Part B). It ships as a pre-mortem directive plus a DoR
  eval-spec profile note, not a check.
- **Make A2/B1 stricter, or leave them as-is** — rejected: the field evidence is over-strict *parsing*
  (a wrapped marker, a verdict with trailing prose), not missing rigor. Widen-only is the fix, fenced
  by a test that `CERTIFIED-NOT` / `CERTIFIEDISH` still fail (no new accept-side hole).
- **`new-spec` reusing `copy_templates`** — rejected: `copy_templates` is a directory-copy proven on
  the kit shape; a single-file stamp is a small distinct helper, not a forced reuse (the directory-copy
  would mis-model the single-file intent).
- **Fire the template pointer on every failure** — rejected: noise in the author loop. It fires only
  on the structure-absent A1/A4/A5 set (the "didn't start from the template" signal); a content
  failure already has a specific, actionable message.

## Consequences

- A2/B1 **widen acceptance only** — no previously-passing spec changes outcome; a hand-wrapped marker
  and a trailing-prose verdict now pass; `CERTIFIED-NOT` still fails (regression-tested). The 0.6.0
  spec carries a trailing-prose-free bare `CERTIFIED`, so it passes both the old and new B1.
- `keel new-spec` + the structural pointer cut the on-ramp from the field's four runs toward one for
  an author starting fresh; the consumer's "hand-wrote it in a foreign format" miss is addressed at
  the source.
- The agent ⇄ prompt fidelity invariant (ADR-0005) is strengthened: distinctive verbatim tokens and
  byte-identical directive text in both files, drift-guarded.
- The pre-mortem now attacks cross-artifact completeness (generated mirrors, intent→executable) and
  the spec's own recorded predictions; the cross-cutting pre-cut audit is blessed doctrine; the DC4-B
  axis graduates from `watch` to an attacked directive.
- **No new gate letter ships** — 0.6.0 sands A2/B1, adds tooling and directives, and hardens the
  guard. The mechanizable cross-artifact slices are routed, not built (thinness).
- **Routed out** (separate ledgers, ADR-0003): the REVIEW-command-vs-design diff and full-tree
  freshness enforcement; the per-wave FIRE release-notes line and predicted-vs-invariant tagging; the
  eval-run cost denominator → pr-pilot.
- **Extends ADR-0002, ADR-0003, ADR-0004, and ADR-0005**; it supersedes none.
