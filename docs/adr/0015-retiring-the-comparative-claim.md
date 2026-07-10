# ADR-0015: retiring the headline comparative claim

- **Status:** Accepted
- **Date:** 2026-07-10
- **Relates to:** ADR-0013 (discharges its item 4 — the run-or-retire deadline), ADR-0012 (the
  publication boundary — this decision strengthens it), ADR-0009/0010 (the measurement lane whose
  own feasibility-first directive this decision applies to keel itself)

## Context

keel's headline is a comparative wager, stated in `README.md` and `docs/doctrine.md` §1: **enforced
discipline beats intended discipline.** Since 0.3.0 that claim has carried an honest qualifier —
*"designed to, and so far observed to,"* not *"measured to beat"* — because the evidence behind it
(the three governed waves) is observational: one operator, un-blinded, no control arm.

ADR-0013 item 4 put a dated commitment on closing that gap: **by 0.13.0, either run a scoped version
of the 2026-06-06 validation experiment and publish the result, or record an ADR retiring the
headline comparative claim.** A third deferral is explicitly forbidden. 0.13.0 is this release, so
the decision falls now.

The experiment (`docs/design/2026-06-06-keel-validation-experiment.md`, maintainer-local) tests
whether the method's observed gains come from the *method* or from a more careful operator (the
"recent-disciplined-me" confound): matched task pairs, arm A = the full method, arm B = a disciplined
generic baseline, ≥8–10 pairs, randomized order, blind defect-after-merge scoring, a pre-registered
decision rule.

Two facts decide the call:

1. **The recorded reason it never ran** (ADR-0013 §4): nothing in the loop schedules it, and its
   scoring is asymmetric — a catch proves the method, a miss proves the loop, so no kept artifact can
   disconfirm the method (the skeptic panel's E3 charge, 2026-07-01). This is a design-time gap, not
   a retrofitted feasibility story: the instrument evidence below only exists as of 2026-06/07 and
   cannot explain the earlier releases.
2. **The instrument does not discriminate at authoring-feasible scale.** keel's own eval harness,
   fathom (public: github.com/grimaldost/fathom, its ledgers committed and pushed), has repeatedly
   shown that on every self-contained task bank it can affordably author, current strong models sit
   at the correctness ceiling — on the order of zero correctness failures across its two hardest banks
   at n=45 — while a strong-tier bare (no-keel) arm self-gates to full pass on a brownfield ablation,
   so every in-session gate or review feature adds nothing; the only discrimination signal fathom
   found lives at a weaker model tier. fathom's own recorded next step names the fix as a harder task
   *class* — large multi-file navigation, a substantial authoring lift — or a weaker base model.

keel's measurement-lane doctrine already contains the response to (2): for an eval/experiment spec, a
**feasibility check runs first** — can the empirical record support the headline being measured at
all? — and can short-circuit the whole review (`docs/doctrine.md` §2). Applied to keel's own
experiment: the task class that would discriminate is coordination-scale, multi-file, above the
doctrine §6 blast-radius trigger — which is exactly the expensive authoring lift fathom names, *and*
exactly the work keel scopes itself to. The affordable banks ceiling. So a matched-pair matrix at
authoring-feasible scale would most likely return a null *by instrument*, not a verdict on the
method — and a null there reads as "keel adds nothing" while actually measuring tasks the method's
own doctrine excludes. Running it as designed would spend a multi-PR authoring series to publish a
number that misleads whichever way a reader leans.

## Decision

**Retire the headline comparative claim.** *Enforced discipline beats intended discipline* is the
method's wager and an observational field report — not a measurement — and the public documents now
say so without a "pending" qualifier (`docs/doctrine.md` §1, `docs/evidence.md`, `docs/concepts.md`).
No controlled comparison ran; the reason is the design-time gap above, sharpened now by instrument
infeasibility on keel's own harness.

This satisfies ADR-0013 item 4 exactly: it demands an ADR retiring the claim, and deferral — not
retirement — is the forbidden move.

### 1. What retirement does and does not touch

- **Retired:** the comparative half — the assertion that the method *measurably beats* a disciplined
  baseline. The wager sentence stays in `README.md` and doctrine §1 **as the wager**, with
  `docs/evidence.md` as its standing qualifier; readers are pointed there rather than the sentence
  being deleted, because it is a true statement of intent and design.
- **Untouched:** the observational record (*designed to, and so far observed to*), the cost-of-defect
  note with its existing single-program / no-counterfactual caveat (`docs/doctrine.md`), and every
  mechanism claim keel can verify in-tree (the gates, the tests, the self-application).

### 2. The reopening path (named, unscheduled — not a deferral)

The comparative claim can be reinstated, but only by a run that happens and favours the method. The
path is priced and designed so it is executable rather than aspirational: a coordination-scale fathom
bank of 8–10 matched task pairs above the doctrine §6 trigger (so ≈80–100 trials), the keel arm
mounted as a plugin, the baseline arm carrying the injected 2026-06-06 checklist, blind
verifier-first scoring, gated by a 2-pair feasibility pilot first (stop if the bare arm ceilings). An
order-of-magnitude cost, token-priced from fathom's public ledgers: a full matrix ~$150–400, the
pilot ~$20–40 (near-zero real spend under subscription auth). The priced plan itself is
maintainer-local (`docs/design/`, gitignored — a consumer boundary, ADR-0003). **No date is
attached and no run is owed:** the claim stays retired unless the run happens and favours the method,
and `docs/evidence.md` records the outcome either way. This directly answers the E3 unfalsifiability
charge — the method now concedes the untested claim rather than protecting it, and names exactly what
testing it costs.

### 3. The K-C1 observational ledger — adopted as the surviving lane

ADR-0013 §4 named re-owning the K-C1 observational ledger (per wave: failure modes predicted →
materialized → catch cost) as "the cheaper first step." It is adopted here as the surviving
observational lane, since the comparative lane is now retired: the per-wave predicted→materialized→
catch-cost data already accrues informally in the field reports, and keeping it is what makes the
*observational* claim (*so far observed to*) auditable. It is an observational record, not a
measurement, and is not a reopening of the comparative claim; formalizing its shape (e.g. a template
slot) is left to a future release and not built here.

### 4. Rejected alternatives

- **Run the experiment as designed.** Rejected: it fails keel's own feasibility-first directive on
  the maintainer's own instrument data (no keel-shaped bank exists; the affordable banks ceiling; the
  discriminating class is the expensive authoring lift the doctrine already targets). It would most
  likely buy a null-by-instrument that misrepresents the method.
- **A weak-tier matrix** (fathom's only current discrimination signal is at the weak tier). Rejected
  as the discharge for item 4: it is cheap and feasible, but it answers a different question — whether
  keel's discipline lifts a *weak* arm — than doctrine §1's claim about an operator's actual
  strong-model flow. It may be worth running for its own sake; it does not discharge the comparative
  claim and is not adopted here.
- **A bare retirement with no reopening plan.** Rejected: cheaper, but it leaves the E3
  unfalsifiability charge with no concrete answer. The priced plan is the answer.

## Consequences

- The public repo trades a nine-release "pending" IOU for "retired, unmeasured — and here is exactly
  what reinstating it would cost," a stronger `docs/evidence.md` posture, not a weaker one. Because
  fathom is public, the retirement's grounding is publicly verifiable.
- `docs/doctrine.md` §1, `docs/evidence.md`, and `docs/concepts.md` drop the "pending" qualifier; a
  regression test (`tests/test_claim_currency.py`) pins the currency so no future edit quietly
  resurrects the IOU without reopening the claim by ADR.
- ADR-0012 (public claims must not cite private evidence) and ADR-0013 §4 are both discharged by this
  record; the "pending" wording in ADR-0012 and in historical CHANGELOG entries stays as provenance
  (an Accepted decision is superseded, not edited).
- ADR-0013's remaining items are all now resolved: items 1–3 by 0.12.0, item 4 by this ADR.
