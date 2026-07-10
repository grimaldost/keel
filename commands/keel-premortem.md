---
description: Run a fresh-eyes pre-mortem on a Ready spec before execution.
argument-hint: <path-to-spec.md>
---

Dispatch the `pre-mortem-review` agent against the spec at $ARGUMENTS — the agent is read-only and
RETURNS its findings. Then YOU, the caller, fold its top failure modes back into the spec/prompts
(re-grounding each `smallest_fix` first — it is a hypothesis, not an instruction) as the closing
step of the Definition-of-Ready gate.

**Size the arc** (the doctrine's round economy, ADR-0014): two rounds — fresh pass → fold →
re-gate under the rising bar — when round 1 found a BLOCKER, the spec touches an
irreversible/shared-contract surface, or the spec set is fresh-drafted from an adjudicated
catalog/triage; one pass with executor-verified folds for a LOW-stakes reversible round; one
**targeted confirmatory pass** (scoped to what the merge could have invalidated) to re-check an
already-certified spec after an upstream dependency lands. Whatever the shape, the final pass
re-reads the FOLDED spec — fold edits move lines and can introduce their own errors, and on the
ordinary arc the saved artifact's `Spec-hash` (B2) then matches what ships (on an operator close, a
condition discharged after the pass keeps the as-reviewed hash and draws B2's expected WARN — see
the operator close, `definition-of-ready.md` Part B).

**Save the pass's artifact (B2).** Save the agent's returned output verbatim to the spec's sibling
`<spec-stem>.premortem.md`, prepending a short header: the spec path, the date, the reviewer, and
`Spec-hash:` from `keel spec-hash <spec>` (run it after the last fold the pass READ — the final
pass re-reads the folded spec, so its hash matches what ships; on an operator close, conditions
discharged after the pass keep the as-reviewed hash and draw B2's expected WARN, never a
recomputed one). Multi-round arcs: the sibling stem holds the
final certifying pass, latest-wins; keep earlier rounds as `<spec-stem>.premortem-r<N>.md` if you
want them. `check-ready` B2 then verifies the certification against the artifact — which raises
the cost of forging a certification from one typed line to a consistent saved artifact, and does
NOT prove the pass was blind: that residual trust stays named (ADR-0002).

**Record the certification** in the spec's `## Pre-mortem certification` block, or `keel check-ready`
cannot see the pre-mortem and an unledgered fold reads green. Fill:

- `Reviewer:` — the non-author who ran the pass (required; B1).
- `Certification artifact:` — the saved output's path (B2 verifies it when named; absent draws a
  WARN nudging adoption).
- `Verdict:` — a single `CERTIFIED` line once no blocking mode remains (or `CONDITIONAL-CERTIFY`
  with a named `Operator:`; an Operator who applies the conditions closes per the operator close,
  `definition-of-ready.md` Part B — the verdict stays `CONDITIONAL-CERTIFY` with a discharge note,
  and a confirm re-gate is optional). Do not append a second Verdict line — edit in place (B1).
- `Failure modes considered & folded in:` — name what was folded, or `none` for a clean certify.
- `Post-fold coherence:` — record the re-read (every finding applied consistently; dependent counts
  re-derived; each new/reworded claim the fold introduced re-grounded).
- `### Fold ledger` — when the fold is non-trivial, one row per finding (finding · target ·
  `artifact:line` · confirmed); `check-ready` (A12/R1) holds each anchor to a real line.

Then re-run `/keel-check-ready $ARGUMENTS` — it passes only once the certification is recorded.
