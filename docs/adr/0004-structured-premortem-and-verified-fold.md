# ADR-0004: structured pre-mortem findings & the verified fold

- **Status:** Accepted
- **Date:** 2026-06-09

## Context

The 2026-06-09 backlog triage (21 field reports, `docs/feedback/2026-06-09-backlog-triage.md`)
surfaced two high-recurrence traps in the pre-mortem → fold → Ready flow that ADR-0002's
form/correctness split did not yet address.

1. **The fold was an unverified hop.** The pre-mortem emitted prose, so folding its findings
   back into the spec was manual `Edit`-string matching (the single most-cited friction across
   five waves), and findings were **half-applied** — a fix landing in one section while a
   contradicting instruction survived in another (half-folds caught across four folds in one
   session). Nothing reviewed the *delta* the fold introduced.
2. **Code-grounding (ADR-0002 Part A, shipped through A6 anchors) stopped at factual anchors.**
   Specs kept asserting things about *referents* — "reuse the proven X", "model on file Y", a
   claimed-existing seam, a superseded prior decision — without verifying them; and design docs
   **overstated enforcement** ("enforced" / "guaranteed" for review-only invariants — 7 of 8
   NOT-CERTIFIED architecture verdicts in one initiative).

## Decision

- **Pre-mortem findings are structured and the fold is verified.** The pre-mortem emits a
  machine-readable findings list (`{id, severity, evidence(file:line), smallest_fix,
  target_section}`) alongside its prose. The fold applies each `smallest_fix` to its
  `target_section` mechanically, then runs a **post-fold coherence re-read**: every finding is
  confirmed applied consistently across all of a section's parts, and any finding that
  *narrowed* scope has every dependent count re-derived (the fold-consistency rule). A
  `Post-fold coherence:` line is recorded in the certification block.
- **Code-grounding extends to referents** (new Part-A checks, under ADR-0002): **A8** resolves
  intra-spec `§N` references against the numbered sections; **A9** resolves `Model-on` / `Reuse`
  reuse-targets (path + symbol); **A10** lints enforcement-claim honesty against a spec's own
  Enforcement-status table. All three verify their convention **when present** — they do not
  require a spec to carry it, and they assert *form*, not correctness (the dominant defect class
  stays with the blind pre-mortem).

## Alternatives considered

- **Make the post-fold coherence pass a deterministic gate** — rejected: a half-fold's two
  halves read alike (both say "calendar"); prose self-consistency is not mechanizable. The
  mechanizable slice (A8 `§`-ref resolution) ships as a gate; the rest is an attested re-read,
  mirroring the Part A / Part B split.
- **Free-text NLP for enforcement claims and reuse targets** — rejected as brittle. A10 keys off
  the Enforcement-status table and A9 off the Model-on/Reuse notation (conventions), so the
  checks are precise and opt-in rather than guessing at meaning.
- **Leave all of this to the pre-mortem prompt (no gates)** — rejected: the mechanizable slices
  recur often and are cheap to assert; leaving them prose-only repeats the "read but never
  enforced" failure the loop exists to prevent.

## Consequences

- New Part-A checks **A8/A9/A10** join A1–A7; each ships a regression test (the gate-health
  rule). They are **checked-when-present**, so existing specs do not retro-break.
- **New authoring convention:** within a spec the `§` glyph denotes that spec's own numbered
  sections (A8 resolves them); a cross-document reference names the document, never a bare `§N`.
  Two further conventions are opt-in: the `Model-on` / `Reuse` notation (A9) and the
  Enforcement-status table (A10).
- The pre-mortem agent's output contract changes (structured findings); the fold gains a
  required, recorded post-fold re-read.
- Easier: the fold is mechanical and verified; the "reuse the proven X" and overstated-enforcement
  traps are caught at authoring time. Harder: authors adopt two small conventions to earn the
  A9/A10 guarantees — but only if they want them.
- **Extends ADR-0002** (form, not correctness); it does not supersede it.
