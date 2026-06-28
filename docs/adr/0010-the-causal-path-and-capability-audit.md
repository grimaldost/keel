# ADR-0010: the causal-path & capability audit (the measurement lane gets teeth)

- **Status:** Accepted
- **Date:** 2026-06-28
- **Extends:** ADR-0002 (DoR form/correctness split), ADR-0004 (the verified fold), ADR-0005 (the drift guard), ADR-0008 (feasibility-grounding), ADR-0009 (the measurement lane)

## Context

Post-0.9.0 field triage (`docs/feedback/2026-06-28-post-090-field-triage.md`, 6 reports) showed the 0.9.0
measurement lane is real and load-bearing — and that it gates the *harness* (estimand, power, blinding,
oracle) while having **no lens on the causal path the experiment depends on**. This was a confirmed
BLOCKER that cost a real ~$417 confounded run: the D6 study's headless localizer had default tool access
and grepped the ground truth in every arm, so the independent variable became marginal and the run was
withdrawn (`2026-06-27-agent-discovery-d6`). The same class was then caught **pre-build** on the next
study (an asserted-but-unbuildable read-jail; `2026-06-27-agent-discovery-engine-eval-design`), proving
the lens belongs in the gate. A sibling break arrived from the other end of the arrow: a seeded store the
measured call recomputes live offline made the treatment **inert** (`2026-06-26-tu-memory-eval-premortem`)
— the elevated post-080 `watch` item V1c, on its second report. Separately, a 12-finding fold *introduced*
a fresh factual mis-statement the re-cert caught (`2026-06-26-a5-env-memory-premortem`), and a pivoted
spec rested on a new linchpin (`2026-06-26-tu-memory-eval-premortem`).

The release pre-mortem again paired two blind Claude passes (DESIGN ⊕ SERIES) with the **cross-vendor
panel** (OpenRouter: `deepseek/deepseek-r1` CERTIFIED, `openai/gpt-5.5` NEEDS-REVISION,
`google/gemini-2.5-pro`; gitignored maintainer tooling, ADR-0003). The panel earned its keep:
`gpt-5.5` independently caught a real **pre-registration drift** (the spec-template advertised a
pre-registered analysis plan as DoR-gated, but the DoR item omitted it) that both Claude passes missed —
substrate-independence paying off again.

## Decision

1. **Add a measured-unit causal-path & capability directive** (`pre-mortem-prompt.md` ⊕
   `pre-mortem-review` agent, drift-guarded by the `inert-treatment`, `side channel`, and `enforcement
   mechanism` markers) + matching eval-spec DoR items. A measurement spec is attacked from BOTH ends of
   the causal arrow it assumes, verified against code: the treatment must reach the measured path (else
   **inert** — mis-built, not null), and the measured unit must have no capability beyond its intended
   input that is a **side channel** to the ground truth (else **confounded**, not null). Every
   isolation/safety/leakage invariant the spec asserts must name a buildable **enforcement mechanism**
   claimed by a numbered §/PR — not a bare assertion, and not a smoke that tests a jail no PR creates.
   **Distinct, not duplicative:** inert-treatment ≠ feasibility (feasibility asks whether the record holds
   the variable; inert asks whether the measured path reads it); side-channel *sharpens* instrument
   defeatability (defeatability nulls the planted difficulty → null; a side channel reaches the answer →
   confounded) — the new teeth are the full-capability *enumeration* and the *confounded-not-null* framing.
2. **The re-cert hunts the fold's own errors** (`pre-mortem-prompt.md` ⊕ agent Output-handling,
   drift-guarded by `newly-introduced`; doctrine sharpening 4): the post-fold coherence re-read also
   re-grounds each NEW or REWORDED claim the fold itself added (a multi-finding fold can assert something
   freshly wrong), and when the fold PIVOTS the spec onto a new premise it re-verifies the new linchpin
   against code. This carries the verified fold (ADR-0004) to the fold-introduced error.
3. **Stamp the `## Experiment design (Part B)` section** into `spec-template.md` (optional, self-contained:
   `<...>` placeholders, no bare §N, no anchors, a `##` heading so it needs no acceptance criterion — it
   adds no new Part-A failure), and **close the inherited pre-registration drift** by adding the
   pre-registered-analysis axis to the DoR eval profile.

## Alternatives considered

- **A new Part-A `check_ready` check for the enforcement-mechanism / capability audit.** Rejected: like the
  existing eval-spec items, "the mechanism is buildable and assigned to a §/PR" and "no capability is a
  side channel" are correctness judgments, not form — a script cannot make them. A10 checks table-vs-prose
  *consistency* only; it does not reach this. A directive + DoR items, not a gate (ADR-0002).
- **A brand-new capability attack independent of instrument defeatability.** Rejected: it would partly
  duplicate the shipped defeatability bullet (a grep of the ground truth is both a defeat and a side
  channel). Both the cross-vendor panel and a Claude pass flagged the overlap; the directive is framed as a
  *sharpening* whose new teeth are the enumeration, the confounded-not-null framing, and the
  enforcement-mechanism assignment.
- **A full-sentence byte-identity drift guard.** Still deferred (the `watch` item V3b). The guard stays
  substring-based (ADR-0005); the author keeps the directives identical by hand and confirms with a manual
  diff (a DoD item), as in 0.8.0/0.9.0.

## Consequences

- The measurement lane now attacks both ends of the causal arrow and the enforcement of isolation
  invariants; the gap that cost a ~$417 confounded run is a standing directive + DoR items, caught
  pre-build on the very next study.
- The re-cert catches the fold's own newly-introduced errors and a pivot's new linchpin — the verified
  fold reaches one level further (ADR-0004).
- The drift guard adds three §1 markers + one §2 marker; the tuple length is pinned at 28 (each PR bumps
  the count with its marker, §1 → 27, §2 → 28).
- The spec template scaffolds the experiment-design section, and the eval-spec DoR profile gains the
  pre-registered-analysis axis (an inherited drift, closed). The cross-vendor panel remains non-blocking
  enrichment; this release it added a real finding (the pre-registration drift) the Claude passes missed.
