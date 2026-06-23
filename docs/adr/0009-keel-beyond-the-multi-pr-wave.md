# ADR-0009: keel beyond the multi-PR wave (the measurement lane & the disconfirming-test contract)

- **Status:** Accepted
- **Date:** 2026-06-23
- **Extends:** ADR-0002 (DoR form/correctness split), ADR-0005 (the drift guard), ADR-0008 (grounding reaches the generated & the feasible)

## Context

Post-0.8.0 field triage showed keel's most-exercised non-PR-series use is now the **experiment/eval spec**
(model-tier, context-size, the dyno study, the tu-consumer stress-test), and that the method adapts but
improvises the mapping each time. 0.6.0–0.8.0 gave the eval-spec DoR profile its *measures-nothing* axes
(ceiling/floor, defeatability, feasibility); the field asked for the *experimental-design* axes and a name
for the fact that a design/experiment/triage round is a **subset** of the 8 phases. Separately, the
pre-mortem named risks but not the cheapest observation that would retire them.

This was also the first release whose pre-mortem included a **cross-vendor panel** (OpenRouter: `gpt-5.5` +
`deepseek-r1`; the Gemini slug 404'd and was skipped — gitignored maintainer tooling, ADR-0003). The panel
independently corroborated the round-1 BLOCKER and added two findings the Claude passes missed (a
Status/certification contradiction; the external-review DoD ownership/fallback gap) — substrate-independence
paying off, exactly as its rationale predicts (cross-model agreement is a weak signal among same-substrate
frontier models; an open-weight dissenter buys real independence).

## Decision

1. **Add the experimental-design axes to the eval-spec DoR profile** (`definition-of-ready.md`, Part B) + a
   **measurement-design** pre-mortem directive (prompt ⊕ agent, drift-guarded by the `unit of analysis`
   marker): estimand + unit of analysis; reps / power & the minimum effect worth detecting; blinding +
   held-constant factors; a correctness oracle distinct from "ran green". **Power ≠ feasibility:** power asks
   whether N can detect the effect; feasibility (ADR-0008) asks whether the empirical record supplies the
   variable at all. Sibling axes, not restatements.
2. **Name the subset-of-phases framing** in doctrine §3 and apply-method: a work round runs a named subset of
   the 8 phases (a design/experiment/triage round is a Decide+Specify subset), the unused phases
   named-as-skipped, not faked.
3. **Add a `disconfirming_test` field to the pre-mortem output contract** (prompt ⊕ agent, drift-guarded by
   the `disconfirming` marker): each predicted failure mode names the cheapest observation that would confirm
   or refute it — distinct from `smallest_fix` (which prevents the mode) and from the stress-test-predictions
   directive (which attacks the spec's own claims).

## Alternatives considered

- **A new Part-A `check_ready` check for the measurement axes.** Rejected: like the existing eval-spec items,
  these are correctness (reviewer-certified Part B), not form — a machine can't judge whether the unit of
  analysis is right. A directive + DoR items, not a gate.
- **A parallel experiment-spec template file.** Rejected: a spec-shape note in apply-method/spec-template, not
  a second template to keep in sync (keel thinness, ADR-0003).
- **A full-sentence byte-identity drift guard.** Deferred — the post-080 `watch` item V3b. The current guard
  checks marker-substring presence (ADR-0005); this release states that honestly rather than over-claiming
  byte-identity, and the author keeps the directives identical by hand.

## Consequences

- The eval-spec DoR profile now covers both the *measures-nothing* and the *experimental-design* axes; the
  pre-mortem attacks experimental design on measurement specs and pairs each predicted mode with its
  disconfirming test.
- keel names its reach beyond the multi-PR wave: a round is a subset of the phases, and a measurement spec is
  a first-class artifact with its own validity bar.
- The drift guard stays substring-based (two new markers; tuple length pinned at 24); byte-identity
  mechanization remains deferred (V3b).
- The cross-vendor panel is a non-blocking enrichment of the pre-mortem; a model that 404s is skipped, ≥2
  voices suffice. The bridge is gitignored maintainer tooling, not shipped in the plugin.
