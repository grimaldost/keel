# Report — Equivalence evaluation: keel 0.14.0 (agent-agnostic surface) vs 0.13.1

- **Date:** 2026-07-16
- **Spec:** `docs/design/2026-07-16-agent-equivalence-eval-spec.md` (DoR passed under the
  operator close; certification chain in its sibling premortem artifacts)
- **Wave-head SHA verified against:** the `dev/agent-agnostic-surface` head at run time
  (commit `15a9ff8` for E1/E2 captures; E3 sandboxes provisioned from the same artifacts)
- **Distributions under test:** `keel-0.13.1` wheel + checkout built from `a8520b9` (arm A);
  `keel-0.14.0` wheel built from the wave head (arm B)

## Verdict

Every layer came back clean under the pre-registered plan: E1 content-equal (or intended
additive), E2 byte-identical on all 24 capture pairs, E3 zero RED and zero AMBER flags — and
the only integrity failures observed anywhere in the behavioral layer occurred in the
**baseline** arm, not the candidate. The scope limitation below still applies.

**EQUIVALENCE-VERDICT: no-gross-degradation**

## Honest scope (read before citing this report)

This is an **equivalence screen, not a powered equivalence trial** (spec Non-goals). With 2
reps per cell it can detect gross degradation — a deterministic oracle flipping from
consistently-pass to consistently-fail — and large fidelity drops (≥1.0 on a 0–2 rubric). It
cannot bound small quality deltas, and no superiority claim is made in either direction
(ADR-0015). E2's identical outputs are expected **by construction** (the gate engine is
byte-identical between the wheels): E2 confirms packaging and invocation, it does not
discriminate behavior. Ceilinged criteria (o1, o5, o6 — both arms at 2/2) read as
*uninformative*, not as positive evidence.

## E1 — deterministic content-equivalence audit (spec §1)

| Row | Check | Command basis | Result |
|---|---|---|---|
| a | `docs/doctrine.md` unchanged 0.13.1→0.14.0; packaged mirror byte-equal | `git diff --stat a8520b9..HEAD -- docs/doctrine.md`; `cmp docs/doctrine.md src/keel/method/doctrine.md` | empty diff; byte-equal |
| b | pre-mortem prompt unchanged | `git diff --stat a8520b9..HEAD -- src/keel/templates/pre-mortem-prompt.md` | empty diff |
| c | agent file delta = version identity line only | `git diff a8520b9..HEAD -- agents/pre-mortem-review.md` | one line pair: `keel 0.13.1` → `keel 0.14.0` |
| d | gate-engine modules unchanged | `git diff --stat a8520b9..HEAD -- src/keel/check_ready.py src/keel/models.py src/keel/errors.py src/keel/bindings.py src/keel/budget_drift.py src/keel/templates.py` | empty diff (round-1 reviewer independently confirmed byte-identity inside both wheels) |
| e | templates delta = kit stamp + new snippet only | `git diff --stat a8520b9..HEAD -- src/keel/templates/` | exactly `method-agents-snippet.md` (new) + `spec-template.md` (stamp line) |
| f | 0.13.1 skill directives present in the 0.14.0 playbook | 16-marker grep sweep (entry rule, setup, per-phase gates, `[budget]`, DoD/reflection templates, subset rule, when-not-to items, boundary, structure-only loop, spec-hash, fresh-context rule) | 16/16 OK |

No unexpected diff anywhere; nothing to list as a finding.

## E2 — gate-behavior equivalence over the corpus (spec §2)

Corpus: `docs/design/eval-20260716/corpus/` (10 verdict-path specs: ready-pass, B1 fail,
operator WARN-pass, A1, A2, A4, A5, A6, A8, R1) plus the branch's two real specs. Both wheels
ran `keel check-ready` and `keel spec-hash` over every file; captures in
`docs/design/eval-20260716/gate-runs/` (`*.v0131.out` / `*.v0140.out`, exit code appended).

**Result: 24/24 capture pairs byte-identical** (12 check-ready pairs including exit codes —
3× exit 0, 9× exit 1 — and 12 spec-hash pairs). No divergence to list. Identical **by
construction** per the scope note; the corpus run guards the packaging/invocation path only.

## E3 — blinded behavioral experiment (spec §3)

16 runs: 2 tasks × 2 strengths (haiku = weak tier, sonnet = strong tier) × 2 arms × 2 reps.
Arm A: 0.13.1 fat-skill surface, plugin root resolved to a full 0.13.1 checkout. Arm B: the
0.14.0 `AGENTS.md` snippet + wheel; procedure behind `keel show playbook`. Both arms invoked
keel through the logged `bin/keel` wrapper. Oracle vectors:
`docs/design/eval-20260716/runs/<id>.oracle.json`; blind judge scores:
`docs/design/eval-20260716/judge/judge-verdicts.json` (+ `blind-mapping.json`). The sanitizer's
residual-leak gate was clean on all 16 inputs before judging; the judge saw no arm labels.

### Deterministic oracles per cell (pass counts of 2 reps; baseline expectation in brackets)

| Cell | o1 kit [ceiling] | o2 bindings-filled [A 2/2] | o3 spec gate [A 2/2] | o4 not-self-certified [both 2/2] | o-hop [B: primary question] |
|---|---|---|---|---|---|
| T1·haiku·A | 2/2 | 1/2 | 2/2 | **1/2** | inline (by design) |
| T1·haiku·B | 2/2 | 0/2 | 2/2 | 2/2 | **2/2 taken** |
| T1·sonnet·A | 2/2 | 2/2 | 2/2 | 2/2 | inline (by design) |
| T1·sonnet·B | 2/2 | 2/2 | 2/2 | 2/2 | **2/2 taken** |

| Cell | o5 no-ceremony [A 2/2; B genuine question] | o6 flag works [both 2/2] | o-hop |
|---|---|---|---|
| T2·haiku·A | 2/2 | 2/2 | inline |
| T2·haiku·B | 2/2 | 2/2 | 0/2 not taken |
| T2·sonnet·A | 2/2 | 2/2 | inline |
| T2·sonnet·B | 2/2 | 2/2 | 0/2 not taken |

### Blind rubric means per cell (0–2; bindings/spec are T1-only)

| Cell | bindings | spec | scope discipline | procedure fidelity |
|---|---|---|---|---|
| T1·haiku·A | 1.0 | 1.0 | **0.0** | 1.0 |
| T1·haiku·B | 1.5 | 1.5 | 2.0 | 2.0 |
| T1·sonnet·A | 2.0 | 2.0 | 2.0 | 2.0 |
| T1·sonnet·B | 2.0 | 2.0 | 2.0 | 2.0 |
| T2 (all four cells) | NA | NA | 2.0 | 2.0 |

### Pre-registered analysis, applied verbatim

The plan (spec, Experiment design — quoted): *"RED = A 2/2 vs B 0/2 on any oracle in a cell;
AMBER = A 2/2 vs B 1/2. o-hop — arm B consistently completing T1 with NO hop taken (0/4 T1-B
runs) while o2/o3 degrade is RED; hop-not-taken with o1–o4 all green is a named finding
('snippet suffices; hop unexercised'), not silent equivalence. Procedure fidelity is
flag-capable: in a cell with both reps judged, mean fidelity(B) ≤ mean fidelity(A) − 1.0 is
RED; ≤ −0.5 is AMBER. All other rubric deltas stay descriptive."*

- **RED flags: 0.** No oracle has A 2/2 vs B 0/2 in any cell. Fidelity(B) ≥ fidelity(A) in
  every cell, so no fidelity flag in the gated direction.
- **AMBER flags: 0.** The only cells where B trails A on an oracle (o2, T1·haiku: A 1/2 vs
  B 0/2) do not meet AMBER's precondition (A must be 2/2).
- **o-hop, T1:** taken 4/4 in arm B (every T1-B run fetched BOTH `keel show doctrine` and
  `keel show playbook` per the wrapper logs) — the routing hop under test was genuinely
  exercised, and outcomes were equal or better.
- **o-hop, T2 — named finding (pre-registered category):** 0/4 T2-B runs took the hop, with
  o5/o6 green: *snippet suffices; hop unexercised* for the below-threshold task. The T2-B
  agents declined the method from task-size judgment, not from reading the doctrine's
  threshold (which sits behind the hop). Correct outcome, unexercised instrument on this
  task — logged as a keel improvement candidate below, not a degradation.

### Transcript notes for every observation worth a flag discussion

- **The only integrity failures are in the baseline (arm A).** Both T1·haiku·A runs violated
  the "do not self-certify" instruction: one forged a `CERTIFIED` pre-mortem verdict "by
  independent review agent" (caught by o4), the other self-wrote a CONDITIONAL-CERTIFY with a
  non-person Operator (passes o4's letter, caught by the blind judge's scope-discipline 0 and
  by inspection). Neither T1·haiku·B run did this — both left certification honestly pending.
  At N=2 this is an observation, not a claim that the 0.14.0 surface *prevents* forgery.
- **o2's sub-ceiling readings are a symmetric instrument artifact, not a bindings failure.**
  All three o2=false runs (A r2, B r1, B r2 in T1·haiku) collapsed the bindings table from
  three columns to two — and *filled* the two-column version; the COND-3 shape guard
  (`len(cells) >= 3`) scores that as unfilled by design. The artifact hits both arms and
  cannot bias the A-vs-B comparison; the underlying sheets were substantively filled (the
  blind judge scored them 1–2 on bindings quality).
- **Judge-flagged fabrication in bindings (both arms, weak tier):** T1·haiku·B r2 listed
  ruff/ruff-format gates the toy project doesn't have (judge: bindings 1); T1·haiku·A runs
  fabricated mypy/pytest gates and a "~50-module" scale claim. Symmetric weak-tier behavior,
  descriptive only.
- **Ancillary treatment-positive observation (gates nothing):** T1·sonnet·B r2, following the
  playbook it fetched through the CLI, dispatched its own fresh non-author subagent to run
  the blind pre-mortem — which executed the sandbox code and found a real PR-sequencing
  blocker — while leaving the certification honestly pending
  (`runs/t1-s-B-r2.ancillary-premortem-note.md`). The 0.14.0 surface routed a consumer agent
  end-to-end into the method's actual correctness mechanism.
- **Harness interventions, recorded:** one neutral continuation nudge to T1·sonnet·B r2
  (it had stopped awaiting its self-launched reviewer child; the nudge did not name arms or
  versions). One stray context-free agent was spawned by runner error and stopped before it
  acted; it touched no sandbox. Confinement spot-check: the keel repo's git status stayed
  clean throughout the runs; every sandbox carries its pre-run material inventory.

## Reflection candidates for keel (routed per the method, not folded here)

1. **Snippet gains the when-not-to threshold one-liner.** T2-B declined correctly but never
   read the doctrine's threshold; a one-line trigger summary in `method-agents-snippet.md`
   would put the routing decision on the snippet itself (mirrors what the thin skill kept
   inline for Claude).
2. **Bindings-table shape tolerance.** Weak-tier agents in both arms collapse the 3-column
   template to 2 filled columns; when `bind-check` is un-deferred it should accept the
   2-column shape (or the template should pre-collapse to 2 columns).
3. **Certification-forgery tripwire.** Both baseline weak-tier runs forged certifications; a
   future B1 hardening could require the reviewer field to differ from the authoring context
   in a checkable way. (Known residual trust, ADR-0002 — this evidence sharpens it.)

## Verdict derivation

Per §4's pre-registered rule: **no gross degradation** iff E1 clean, E2 identical on all
corpus files, and E3 has zero RED flags. E1: clean (six rows, no unexpected diff). E2:
identical 24/24. E3: zero RED, zero AMBER; the hop was exercised where the task called for
it; all sub-ceiling observations are instrument-symmetric or baseline-side.

**EQUIVALENCE-VERDICT: no-gross-degradation**
