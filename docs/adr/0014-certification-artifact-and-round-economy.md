# ADR-0014: the certification artifact and the round economy

- **Status:** Accepted
- **Date:** 2026-07-06
- **Relates to:** ADR-0013 (resolves its items 1–3), ADR-0002 (the residual trust B2 narrows but
  does not remove), ADR-0007 (convergence — the round economy prices it)

## Context

ADR-0013 deferred three design calls to 0.12.0: B2 artifact-backed certification, the read-only
agent's executable mandates, and the A4 subset-of-phases relaxation. The 0.11.0 field wave arrived
(two six-spec two-round arcs, two consumer waves, a greenfield build — see the 2026-07-06
post-0.11.0 triage, maintainer-local) and added a fourth design gap the same surface owns: every
campaign hand-rolls what round 2 *is* and when it is worth running. These four are one coherent
change to the certification contract, decided here.

## Decision

### 1. B2 — the certification references a saved pre-mortem artifact

The caller (the orchestrating session or a hook — the agent is read-only and cannot write) **saves
the pre-mortem pass's returned output verbatim** to a sibling file of the spec:
`<spec-stem>.premortem.md` (e.g. `docs/design/my-feature.premortem.md` next to
`docs/design/my-feature.md`), prepending a small header: the spec path, the date, the reviewer,
and `Spec-hash: <sha256>` of the spec **as reviewed**. The certification block gains an optional
`Certification artifact:` field naming that file.

`check-ready` B2 — **verify-when-present in 0.12.0**: when the certification names an artifact, B2
fails the gate if the artifact is missing or carries no `PREMORTEM-VERDICT:` line, fails if the
artifact's verdict token disagrees with the recorded `Verdict:`, and **WARNs** (not fails) when the
artifact's `Spec-hash:` does not match the current spec — "certified against an earlier revision;
re-run the pass" — because a hash mismatch is exactly what a post-certification edit looks like.
When the certification names no artifact, B2 emits a WARN nudging adoption. Requiring the artifact
outright is a 0.13.0 call, after field exposure.

**The hash is computed over the spec with its `## Pre-mortem certification` section's lines
removed** — sha256 over the remaining `splitlines()` sequence joined by `\n` — because recording
the verdict must not invalidate the hash the verdict was recorded against, and the certification
block *grows* when recorded (fold-ledger rows, coherence notes). An earlier draft said "blanked,
line count preserved"; the spec pre-mortem refuted that — blanked lines still contribute newline
bytes, so a growing ledger would change the very hash its own recording is part of. Removal (plus
splitlines normalization, which also absorbs CRLF/LF differences) makes the hash invariant to any
certification-block edit. `keel spec-hash <spec>` computes this canonical hash so callers do not
hand-roll the masking.

**Honest framing (mandatory, ADR-0002):** B2 raises the cost of forging a certification from
"type one line" to "fabricate a structured artifact with a matching hash". It does **not** prove a
blind pass ran — an author can still run the pass themselves or fabricate the file. The residual
trust (a named non-author reviewer, actually blind) remains named, not hidden.

### 2. The reviewer stays read-only; what it cannot execute is surfaced, not implied

Rejected: granting the agent Bash (even scoped) — it changes the agent's capability surface, and
the same prompt is also run by Bash-capable orchestrators, so the mismatch is a property of the
*runner*, not the directive set. Adopted: **generalize the `unverified-offline` tag** (0.8.0
introduced it for generated-artifact claims) to every execution-requiring directive — autofixer
simulation, post-parametrize test counting, AST enumeration. A read-only run tags each such claim
`unverified-offline` and its saved output carries an `Unverified-offline: <N>` count adjacent to
the `PREMORTEM-VERDICT:` line, so the operator weighs an offline pass's verdict knowing what it
could not execute. The output contract also states plainly that recording the certification block
is the **caller's** step — the agent stops reporting its own read-only-ness as a deviation
(a recurrence the field hit on every pass).

The agent states its identity at both ends: its body carries a version line kept in lockstep by
the version-consistency test (a fifth site), and its output contract states the identity beside
the returned `PREMORTEM-VERDICT:` token — the runtime half is what makes a cached or stale copy
self-announcing on every verdict it actually returns.

### 3. A4 — the subset-of-phases convention

A spec header may declare `- **Phases:** Decide+Specify (Decompose: skipped)`. When the
declaration explicitly names Decompose as skipped, A4 relaxes the PR↔section manifest requirement
to absent-ok. A manifest that is present is still checked in full; A1/A2 (numbered sections,
acceptance criteria) apply regardless; and the declaration is content the pre-mortem can challenge
— a series spec that skips Decompose to dodge the bijection is exactly a finding. Not a blanket
escape: nothing else in Part A is relaxed.

### 4. The round economy — when one round is enough

Field calibration (WS-B: round 2 caught 5 fold-introduced defects; WS-C: round 2 converged to zero;
a LOW-stakes closeout: one round sufficed and still caught 2 MAJ; a post-merge recheck: one
targeted pass): run the **full two-round arc** (fresh pass → fold → re-gate under the rising bar)
when round 1 found a BLOCKER, or the spec touches an irreversible or shared-contract surface, or
the spec set is fresh-drafted from an adjudicated catalog/triage. A **single pass with
executor-verified folds** suffices for a LOW-stakes, reversible round with no cross-wave surface. A
**single targeted confirmatory pass** — scoped to the areas an upstream merge could have
invalidated — re-checks an already-certified spec after a dependency lands. The **final pass always
re-reads the folded spec**: fold edits move lines and can introduce errors (which also makes the
B2 artifact's spec-hash match the spec that ships). The value of round 2 is *checking*, not
guaranteeing a hit — a zero-yield round 2 on a re-grounded fold is the system working.

## Consequences

- ADR-0013 items 1–3 are resolved by build (0.12.0); item 4 (the validation experiment) keeps its
  0.13.0 run-or-retire deadline, untouched by this ADR.
- The certification contract grows two optional, verify-when-present surfaces (artifact, kit/agent
  version identity) and one convention (Phases) — old specs stay green, new WARNs guide adoption.
- The forgery-cost asymmetry is stated where it is created (B2), so the gate's guarantee is never
  read as more than it is.
