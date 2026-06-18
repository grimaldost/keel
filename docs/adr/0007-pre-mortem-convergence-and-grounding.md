# ADR-0007: pre-mortem convergence & grounding

- **Status:** Accepted
- **Date:** 2026-06-17

## Context

The post-0.6.0/0.6.1 field round (`docs/feedback/2026-06-17-post-061-field-triage.md`, 3 reports on keel
0.6.1) found the adoption surface and the cross-artifact directives field-validated — the
discriminating-power DoR item and the stress-test-predictions directive between them prevented two
null/over-provisioned studies pre-spend. The residual misses cluster at the pre-mortem's *convergence* and
*grounding* edges, which ADR-0005/0006 did not reach:

1. **Multi-round pre-mortems do not converge.** A fresh adversarial reviewer always finds *something*, so a
   re-review ratchets down in severity but never reaches zero (model-tier: 4 rounds; debt-engine: 4 DESIGN
   passes). The fix — a rising bar on later rounds — had to be hand-injected to make a round terminate; it
   was proven across two specs (4→3 round convergence) without going blind (a real BLOCKER still surfaced).
   And the legitimate non-perfect terminal state, **CONDITIONAL-CERTIFY**, was unrepresentable in the gate:
   B1 accepted only the bare token `CERTIFIED`, so an operator-accepted conditional spec was EXIT=1 forever —
   though the prompt already *emits* CONDITIONAL-CERTIFY and doctrine already blesses it.
2. **A pre-mortem capability claim can be confidently wrong when API-doc-grounded, not source-grounded.**
   debt-engine R1 asserted a BLOCKER ("tu has no engine for this") from a consumer API reference, missing the
   primitives; a domain expert overturned it; R2/R3 confirmed against source. This is the *claim* twin of
   0.6.1's *fix* re-grounding — same meta-cause (a written claim trusted because writing it felt like
   reasoning), one step upstream in the pipeline.
3. **The SERIES pass has no first-class checklist.** It is keel's most-reinforced value pattern (it caught
   2 BLOCKER + 4 MAJOR the four DESIGN passes could not), yet the prompt enumerated only DESIGN attacks.
4. **The 0.6.0 on-ramp fix is partial.** `keel new-spec` + the structural pointer shipped, but the pointer
   fired only on *entirely-absent* structure, so a *malformed* spec (wrong heading shape, broken manifest)
   got no nudge; and the A12 fold-ledger error named the rule without showing the format.

## Decision

- **§1 rising-bar / convergence directive.** `pre-mortem-prompt.md` and the bundled agent gain a directive,
  byte-identical in both: at round ≥2 the bar for BLOCKER/MAJOR rises — a finding is blocking only if it
  plausibly corrupts the decision the spec gates; a round of only nice-to-haves is CERTIFY-with-advisories,
  not another full round; do not manufacture a blocker. Doctrine's convergence note gains the rule.
- **§2 recordable CONDITIONAL-CERTIFY (the one gate change).** `_check_premortem` (B1) widens to accept the
  verdict's leading token `CERTIFIED` **or** `CONDITIONAL-CERTIFY` paired with a named `Operator:` field —
  the operator-accepted "ready modulo a named fix" state. The conditional verdict passes with a non-blocking
  **WARN** (a new `warnings` channel on `GateResult`, printed by the CLI before `OK`), never EXIT=1; a
  CONDITIONAL-CERTIFY with no Operator fails with a contract-stating error. It stays a *form* check
  (a verdict and an owner were RECORDED, not that the spec is correct — ADR-0002). `spec-template.md`'s
  Verdict block gains the `Operator:` field and `definition-of-ready.md`'s B1 description is updated, so the
  state is recordable end to end. Widen-only: a bare `CERTIFIED` passes exactly as before, with no warning.
- **§3 source-ground capability claims.** A directive, byte-identical in both pre-mortem files: any reuse /
  capability / existence claim is verified against the cited symbol's source or its tests — not a consumer
  API doc or a generated reference alone — and tagged observed or inferred. Doctrine sharpening 4 gains the
  clause (the claim twin of the 0.6.1 fix re-grounding).
- **§4 first-class SERIES-pass checklist.** A directive, byte-identical in both files: base-branch content
  reality, per-PR gate × contract-test interactions, cross-prompt contract drift. Project-agnostic items
  only; the orchestrator-constraint items (one-sink-per-dataset, base-branch targeting) route to pr-pilot.
  Doctrine's two-pass cadence note records that the SERIES pass carries its own checklist.
- **§5 on-ramp completion.** The structural pointer now fires on absent OR malformed-*shape* structure
  (un-numbered heading, non-bijection manifest, empty manifest), not only absent — while staying quiet on a
  coverage slip or an A5 path-grounding failure (content, not shape; ADR-0006's author-loop-quiet decision is
  preserved). The A12 fold-ledger error gains a concrete `path:line` example.
- **§6 instrument-defeatability eval axis.** A directive, byte-identical in both files, plus a DoR Part-B
  eval-spec item: ask the cheapest way an agent sidesteps the planted difficulty so the run measures nothing
  — a sibling axis to the 0.6.0 ceiling/floor item (an instrument perfectly discriminating in principle can
  still be trivially bypassed).

The four directives (§1/§3/§4/§6) are each pinned by a distinctive verbatim marker in the existing drift
guard (`tests/test_premortem_agent.py`), so the ADR-0005 agent ⇄ prompt fidelity invariant holds as the
directive set grows.

## Alternatives considered

- **A deterministic convergence gate (round cap / severity-gated stop in code)** — rejected: whether a later
  finding "corrupts the decision the spec gates" is irreducibly semantic (ADR-0002 Part B). It ships as a
  prompt directive; the gate only records the *terminal verdict* (§2), which is a form check.
- **CONDITIONAL-CERTIFY as a silent pass (no Operator, no WARN)** — rejected: it would let a conditional spec
  green without a named owner, defeating the form check. The Operator field is the recorded accountability;
  the WARN keeps it visibly distinct from a clean CERTIFIED.
- **A new deterministic A-letter for source-grounding** — rejected: "read the symbol's source" is a reviewer
  act, not a parseable property of the spec text; it ships as a directive, drift-guarded.
- **Fire the template pointer on every structural-`where` violation** — rejected: it would re-open the
  author-loop noise ADR-0006 closed (a coverage slip or a missing path on a template-shaped spec is content,
  not shape). The trigger is scoped to absent + malformed-shape, with both negatives regression-tested.

## Consequences

- B1 **widens acceptance only** — no previously-passing spec changes outcome; a bare `CERTIFIED` passes with
  no warning, and CONDITIONAL-CERTIFY passes only with a named Operator (and a WARN), never silently. The
  0.7.0 spec itself carries a bare `CERTIFIED`, so it passes the widened B1.
- The multi-round pre-mortem now converges by construction (the rising bar) and its operator-accepted
  terminal state is recordable (the conditional verdict), closing the doctrine↔gate gap debt-engine hit.
- The pre-mortem now source-grounds capability claims and attacks eval-instrument defeatability; the SERIES
  pass has a first-class checklist. All four are drift-guarded in both files.
- The on-ramp is complete: the pointer teaches on a malformed spec, not only an empty one, and the ledger
  error shows the accepted `path:line` form.
- **One gate change ships** (§2, a widen + a non-blocking WARN channel); §1/§3/§4/§6 are drift-guarded
  directives, §5 is two ergonomic fixes. The engine-side slices (program convergence budget, catch-cost
  denominator, orchestrator SERIES checks) are **routed → pr-pilot** (separate ledgers, ADR-0003).
- **Extends ADR-0002, ADR-0003, ADR-0004, ADR-0005, and ADR-0006**; it supersedes none.
