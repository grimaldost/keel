# ADR-0008: the grounding directive reaches the generated and the feasible

- **Status:** Accepted
- **Date:** 2026-06-19
- **Extends:** ADR-0004 (referent grounding & the verified fold), ADR-0007 (source-ground capability claims)

## Context

0.7.0 (ADR-0007) grounded the pre-mortem's **capability claims** in the symbol's source, not a consumer
API doc. Two field reports run on the released 0.7.0 (post-070 triage) showed the grounding directive
reaches one step short in two directions, and that the freshly-shipped §5 gate-ergonomics surface had
named residuals:

- **Downstream — the generated artifact.** A datatools pre-mortem read the *generator's* source and
  prescribed a param-binding fix, but missed that the generator double-quotes a SQL identifier — a parse
  error on the live target, valid in every offline test (a mocked connector and a Polars file-source
  both accept double quotes). Reading the right *source* is not enough for a *generated* artifact: its
  behavior is unproven until the generated output runs on the real target/dialect.
- **Upstream — feasibility.** A design-as-analysis study spent two pre-mortem rounds hardening internal
  validity before round 3 grounded the headline against prior-run ledger data and found the corpus could
  not supply the variation the study needed — a null. The highest-leverage check ran last.

Two adjacent gate facts also surfaced: the A12 fold-ledger parser swept *every* table in the
`### Fold ledger` subsection span (a sibling disposition table tripped A12 — a false positive); and the
absent-numbered-sections error named the child `### §N` shape but not the `## Numbered sections` parent.

## Decision

Extend the grounding directive in BOTH the pre-mortem prompt and the bundled agent (drift-guarded):

1. **Generated-artifact behavior is grounded only by running the output on the target.** A claim about
   how a generated artifact behaves (generated SQL/DDL, a rendered template, codegen output, a
   serialized schema) is unverified until that output is executed or parsed on the real target/runtime;
   reading the generator's source is a hypothesis. The read-only reviewer FLAGS such a claim as
   unverified-offline and names whether the offline tests share the target's dialect.
2. **Feasibility-grounding runs first.** Before hardening internal validity, ground the study's headline
   against the empirical record it needs (prior-run data/ledger, the reused instrument); a null here
   short-circuits the round. Sharpens the existing stress-test-predictions directive; adds a DoR
   eval-spec Part-B item.
3. **A committed/generated artifact with a per-change freshness gate is not deferrable.** Sharpens the
   existing Cross-PR-generated-artifacts directive: when a gate asserts the artifact in sync on EVERY
   change to its source, the regenerate-after-the-last-mutating-PR option does not apply — each PR
   perturbing the source regenerates its slice in that same PR.

And fix the gate:

4. **A12 reads only the first contiguous table in the `### Fold ledger` subsection** (a new
   `_first_table_rows` helper), so a sibling table sharing the span is not parsed as ledger rows; the
   ledger is the first table under that heading by template convention.
5. **The absent-sections error names the parent + child shape** (keeping its `no ` prefix so the CLI
   template pointer still fires); the A6 anchor and A5 "to be created" errors teach their rule.

These are **sharpenings of directives that already exist** (1/2/3 extend the source-ground, stress-test,
and Cross-PR directives), not new passes — established by grounding each promoted point against source
during the validity analysis: a standalone "generated-artifact gate coupling" SERIES item would have
duplicated the Cross-PR directive, and a separate "feasibility" directive would have duplicated the
floor/ceiling one.

## Alternatives considered

- **A standalone SERIES-pass item for the generated-artifact coupling.** Rejected: the Cross-PR
  directive already covers regeneration ordering; the increment is one clause (un-deferrable when
  gated), so it sharpens rather than duplicates.
- **A new "feasibility" directive separate from stress-test-predictions.** Rejected: the detection
  overlaps the existing floor/ceiling directive; only the empirical-record grounding and the run-first
  ordering are net-new, so a clause is the right size.
- **Anchor the fold ledger by matching its header columns** (instead of first-table-only). Deferred:
  the template places the ledger first; first-table-only is simpler, and the before-ledger case is
  out-of-contract (documented in `spec-template.md`), not silent.

## Consequences

- The pre-mortem demands one more grounding step in each direction; the read-only agent flags (does not
  perform) the generated-output check, and emits a machine-greppable `PREMORTEM-VERDICT:` line while the
  caller folds and records.
- A12 no longer false-positives on a sibling table, at the cost of a documented limitation (a table
  placed before the ledger in the same subsection is out-of-contract).
- The directives stay drift-guarded (five new markers; the MARKERS tuple length is pinned at 22).
- Engine-side halves (program convergence budget, the orchestrator that gates on the greppable verdict
  line) route to pr-pilot, recorded keel-side only (ADR-0003).
