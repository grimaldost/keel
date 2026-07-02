---
description: Run a fresh-eyes pre-mortem on a Ready spec before execution.
argument-hint: <path-to-spec.md>
---

Dispatch the `pre-mortem-review` agent against the spec at $ARGUMENTS — the agent is read-only and
RETURNS its findings. Then YOU, the caller, fold its top failure modes back into the spec/prompts
(re-grounding each `smallest_fix` first — it is a hypothesis, not an instruction) as the closing
step of the Definition-of-Ready gate.

**Record the certification** in the spec's `## Pre-mortem certification` block, or `keel check-ready`
cannot see the pre-mortem and an unledgered fold reads green. Fill:

- `Reviewer:` — the non-author who ran the pass (required; B1).
- `Verdict:` — a single `CERTIFIED` line once no blocking mode remains (or `CONDITIONAL-CERTIFY`
  with a named `Operator:`). Do not append a second Verdict line — edit in place (B1).
- `Failure modes considered & folded in:` — name what was folded, or `none` for a clean certify.
- `Post-fold coherence:` — record the re-read (every finding applied consistently; dependent counts
  re-derived; each new/reworded claim the fold introduced re-grounded).
- `### Fold ledger` — when the fold is non-trivial, one row per finding (finding · target ·
  `artifact:line` · confirmed); `check-ready` (A12/R1) holds each anchor to a real line.

Then re-run `/keel-check-ready $ARGUMENTS` — it passes only once the certification is recorded.
