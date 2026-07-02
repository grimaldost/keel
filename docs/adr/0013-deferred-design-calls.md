# ADR-0013: deferred design calls from the 2026-07-01 panel

- **Status:** Accepted
- **Date:** 2026-07-01
- **Relates to:** ADR-0002 (form/correctness split), ADR-0003 (defer until a real failure demands the mechanism)

## Context

Four of the skeptic panel's findings (`docs/feedback/2026-07-01-skeptic-panel-fable5.md`) are not
mechanical fixes — they are **design questions** whose answer changes the shape of the method. Shipping
a rushed version of any of them in 0.11.0 (a release already large with the enforcement-gap fixes,
ADR-0011) would risk the exact half-baked change keel warns against. Following ADR-0003's precedent —
defer a mechanism, with its rationale recorded, until it is designed rather than improvised — this ADR
**decides each one's disposition** so none becomes silent write-only backlog (the failure the
reflection-triage exit-gate exists to prevent).

## Decision

Each item below is **deferred, not declined**, with the trigger that would promote it to a build.

### 1. B2 — artifact-backed certification (panel E1) — DEFER, design next

**Finding:** B1 verifies a `Verdict: CERTIFIED` line + a non-empty `Reviewer:` string. Both are
author-typable, so an unsupervised agent can green the correctness half of the DoR gate without any
pre-mortem running. keel's own 2026-06-09 intake designed the fix (a certification that references the
pre-mortem agent's saved output artifact) and it was never shipped or declined across seven releases.

**Decision:** This is the highest-value deferred item. It needs the pre-mortem agent to **emit a saved
artifact** (the findings YAML + `PREMORTEM-VERDICT` line to a known path) and `check-ready` to validate
that the certification references an existing, shape-valid, verdict-matching artifact. That is a
cross-component contract (agent output → file → gate), not a `check_ready.py` patch. **Design it in
0.12.0.** Interim: ADR-0002's named residual trust stands, and 0.11.0's `keel-premortem.md` now spells
out the record protocol so the human/agent caller records a real certification rather than a bare line.

**Trigger to build:** the next release cycle (this is scheduled, not conditional).

### 2. Read-only pre-mortem agent carries executable mandates (panel F5) — DEFER, needs a tool decision

**Finding:** the bundled agent has `tools: Read, Grep, Glob` but its directives order it to run the
autofixer, simulate `mypy`/`ruff`/pytest collection, count post-parametrize items, and AST-enumerate —
verifications it cannot perform — and the drift guard forces the directives identical to the
Bash-capable prompt template, baking the mismatch in. Only the generated-artifact class has an
"unverified-offline" downgrade path.

**Decision:** DEFER. Two viable answers, both design calls: (a) grant the agent read-only Bash so it
can actually run `ruff/mypy/pytest --collect-only`, or (b) generalize the "unverified-offline" tag to
every execution-requiring directive and surface it in the verdict. (a) changes the agent's capability
surface; (b) changes the output contract. Decide alongside B2 (both touch the agent contract).

**Trigger to build:** 0.12.0, with B2.

### 3. A4 vs the subset-of-phases doctrine (panel ARCH-1) — DEFER, needs a convention

**Finding:** A4 unconditionally requires a PR↔section manifest, but doctrine §3 says a design /
experiment / triage round runs a **subset** of the phases and skips Decompose. So a Decide+Specify
round must invent a manifest to pass its own gate.

**Decision:** DEFER. The fix needs a spec-template **convention** (a `Phases:` declaration, or a
`Decompose: skipped` marker) that A4 reads to relax the manifest requirement for a declared non-series
round — designed so it cannot become a blanket escape hatch. Interim workaround (documented): a
single-unit round records a one-row manifest mapping its sole section to one unit. Low blast radius, so
it waits behind B2.

**Trigger to build:** the first field report of a real adopter (not the author) blocked by this, or 0.12.0.

### 4. Run or retire the controlled validation experiment (panel E3 / ARCH-15) — DEFER with a deadline

**Finding:** the experiment designed 2026-06-06 has been "pending" for eight releases while the method
grew; nothing in the loop schedules it, and the scoring asymmetry (a catch proves the method, a miss
proves the loop) means no kept artifact can disconfirm the method.

**Decision:** DEFER with a commitment. ADR-0012's `docs/evidence.md` now states the claim's evidence
status honestly in the interim. The method owes itself either the experiment or an explicit retirement:
**by 0.13.0, either run a scoped version under keel's own measurement lane and publish the result, or
record an ADR retiring the headline comparative claim.** Re-owning the K-C1 observational ledger
(per-wave: failure modes predicted → materialized → catch cost) is the cheaper first step.

**Trigger to build:** 0.13.0 deadline (a dated commitment, not open-ended).

## Consequences

- Four known-but-unbuilt findings are now decided with triggers, not silent backlog.
- Two (B2, agent tools) are scheduled for 0.12.0; one (A4 subset) waits for a real external report or
  0.12.0; one (the experiment) has a 0.13.0 run-or-retire deadline.
- keel resists cramming design changes into a fix release, while refusing to let them vanish — the
  ADR-0003 discipline (defer with a recorded reason and a live state) applied to itself.
