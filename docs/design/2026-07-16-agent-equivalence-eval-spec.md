# Spec — Equivalence evaluation: keel 0.14.0 (agent-agnostic surface) vs 0.13.1

- **Date:** 2026-07-16
- **Status:** ready (DoR passed, operator close)
- **Audience:** the evaluation runner and the maintainer deciding the merge of `dev/agent-agnostic-surface`
- **Output artifact(s):** `docs/design/eval-20260716/` (corpus, gate runs, behavioral runs, judge
  inputs) and `docs/design/2026-07-16-agent-equivalence-eval-report.md`
- **Phases:** Specify+Run&Report (Decompose: skipped; Decide covered by ADR-0009/ADR-0010's
  measurement lane and ADR-0017's deferrals — no new standing invariant is created)

## Context

The 0.14.0 wave (the agent-agnostic surface, ADR-0017) moved the method's content behind the
CLI: the doctrine is mirrored into the package, the apply-method procedure moved from the fat
Claude skill body into a packaged `playbook.md` reached via `keel show playbook`, and a
consumer-side `AGENTS.md` snippet became the any-agent route. Before merging to main, the
maintainer requires evidence of **non-degradation**: agents driven by the 0.14.0 surface must
produce virtually the same quality of method application as agents driven by the 0.13.1
surface, across agent strength and task scope.

The risk surface is narrow by construction: the deterministic engine (`src/keel/check_ready.py`
and its siblings) was not edited in the wave, and the doctrine/templates content is intended to
be equal-or-additive. What genuinely changed is the **routing hop** — a 0.14.0 agent must fetch
the procedure through a CLI call instead of reading it inline — and that is what the behavioral
layer measures. Both build artifacts exist and are pinned:
`<scratchpad>/eval/wheels/keel-0.13.1-py3-none-any.whl` (built from commit `a8520b9`) and
`<scratchpad>/eval/wheels/keel-0.14.0-py3-none-any.whl` (built from the wave head).

## Goal

Produce a written verdict — no gross degradation, or the named degradations — from three
layers of evidence: a deterministic content-equivalence audit (E1), a deterministic
gate-behavior equivalence run over a spec corpus (E2), and a blinded behavioral experiment
over agent configurations (E3), analyzed exactly per the pre-registered plan below.

## Gate commands

- DoR for this spec: `uv run keel check-ready docs/design/2026-07-16-agent-equivalence-eval-spec.md`
- The repo's four quality gates are untouched by this round (no engine/source edits); the run
  layer's own gates are the oracles defined in §3.

## Non-goals

- **No powered equivalence trial.** With 2 reps per cell this design detects *gross*
  degradation (pass→fail flips on deterministic oracles); it cannot bound small quality
  deltas. The report must state this scope honestly rather than claim statistical equivalence.
- **No superiority claim** for either version, in either direction (ADR-0015's discipline: no
  comparative headline without a controlled, powered run).
- **No production-consumer runs** — sandboxes only (ADR-0003: keel never reaches into a consumer).
- **No merge decision inside this round** — the report informs the maintainer's call; it does
  not execute it.
- **No engine edits** — if E1/E2 find a real divergence, this round *reports* it; the fix is a
  separate change under its own gate.

## Invariants touched

- **Publication boundary** (ADR-0012): all run artifacts and the report live under
  `docs/design/` (maintainer-local; carried on the dev branch by explicit `git add -f`, as this
  round's working record).
- **Consumer-agnosticism** (ADR-0003): the toy consumer is synthetic; no real consumer data.
- **Retired comparative claim** (ADR-0015): the report's language is equivalence-screen
  language, never "measured to beat".

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| publication boundary (ADR-0012) | review-only | review checklist |
| consumer-agnosticism (ADR-0003) | review-only | review checklist |
| no-superiority language (ADR-0015) | review-only | the report review before commit |
| engine untouched by the wave | enforced | `git diff a8520b9..HEAD -- src/keel/check_ready.py src/keel/models.py src/keel/errors.py` empty, recorded in the report (E1) |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| gate-equivalence spec corpus | `docs/design/eval-20260716/corpus/` (to be created) |
| dual-CLI gate-run captures | `docs/design/eval-20260716/gate-runs/` (to be created) |
| behavioral run artifacts (per-run sandbox outputs) | `docs/design/eval-20260716/runs/` (to be created) |
| sanitized judge inputs + judge verdicts | `docs/design/eval-20260716/judge/` (to be created) |
| the evaluation report (E1+E2+E3 + verdict) | `docs/design/2026-07-16-agent-equivalence-eval-report.md` (to be created) |

## Numbered sections

### §1 E1 — deterministic content-equivalence audit

Record in the report, each as a diff-grounded row: (a) `docs/doctrine.md` unchanged between
`a8520b9` and the wave head, and the packaged mirror byte-equal (the §1 gate of the wave);
(b) `src/keel/templates/pre-mortem-prompt.md` unchanged; (c) `agents/pre-mortem-review.md`
diff is the version identity line only; (d) the engine diff for the gate modules is empty;
(e) the templates directory delta is exactly: the spec-template kit stamp version and the new
`method-agents-snippet.md`; (f) a directive-coverage checklist: every load-bearing directive of
the 0.13.1 skill body (entry-rule, setup steps, per-phase gate list, subset-of-phases rule,
when-not-to threshold, source-of-truth boundary) appears in the 0.14.0 `playbook.md`.

**Acceptance criterion:** the report's E1 section carries all six rows with their diff evidence
(command + result), and any non-empty unexpected diff is listed as a finding rather than
explained away.

### §2 E2 — gate-behavior equivalence over a spec corpus

Build `docs/design/eval-20260716/corpus/` with at least 10 spec files exercising the gate's
distinct verdict paths: a fully Ready spec; an uncertified spec (B1 fail); a
CONDITIONAL-CERTIFY + Operator spec (pass with WARN); a structure failure (unnumbered heading);
a trivial acceptance criterion (A2); a manifest bijection failure (A4); a missing concept path
(A5); a bad anchor snippet (A6); a dangling §N reference (A8); a fold-ledger anchor failure
(A12/R1); plus the two real certified specs of this branch. Run BOTH pinned wheels'
`keel check-ready` (and `keel spec-hash` where the spec is hashable) over every corpus file,
capturing exit code and full stdout to `docs/design/eval-20260716/gate-runs/`; diff the
captures pairwise per file.

**Acceptance criterion:** the report's E2 section shows, per corpus file, both exit codes and
a byte-level verdict on the stdout pair; the expected result — identical behavior on every
file — either holds on all files or every divergence is listed as a finding with its capture
paths.

### §3 E3 — blinded behavioral experiment across agent configurations

**Arms.** Arm A (baseline): a sandbox whose `AGENTS.md` carries the 0.13.1 method surface —
the full 0.13.1 skill body text with `${CLAUDE_PLUGIN_ROOT}` **resolved to a full 0.13.1
checkout provisioned inside the harness** (so the skill's own routes — the doctrine file, the
packaged templates dir, the bundle-run CLI — all resolve, as in a real plugin install; a bare
wheel would strand those routes and handicap the baseline, round-1 FM-2). Arm B (candidate): a
sandbox whose `AGENTS.md` carries the 0.14.0 `method-agents-snippet.md` block (as `keel init`
ships it), backed by the pinned 0.14.0 wheel; the full procedure is only reachable through
`keel show playbook` — the routing hop under test. In BOTH arms, `keel` is invoked through an
identical sandbox-local `bin/keel` wrapper that appends each invocation to `.keel-cli.log`
before delegating to the arm's distribution (held constant, arm-blind in form) — the log is
what makes the routing hop observable (o-hop below). The per-run material inventory (recorded
before the agent starts) lists the arm's `AGENTS.md`, wrapper target, and plugin-root
provisioning.

**Tasks.** T1 (above threshold): "this project will undergo a multi-PR refactor on a shared
contract; set up the development method per AGENTS.md, author the refactor spec, and iterate
until the structural readiness gate passes — do not implement, do not self-certify." T2 (below
threshold): "add `scripts/summarize.py`: a small CLI that takes a log-file path argument and
prints the per-level record counts (use the existing modules)" — the correct behavior is to
implement directly, keep the project's unittest suite green, and NOT apply the method (the
when-not-to routing; note the snippet does not carry the threshold inline — an arm-B agent must
take the hop to read it, which gives T2 genuine assay sensitivity, round-1 notes).

**Cells and reps.** 2 tasks × 2 strengths (a weaker and a stronger model tier, held identical
across arms) × 2 arms = 8 cells, 2 reps each = 16 runs. Each run gets a fresh copy of the same
toy consumer project in an isolated scratchpad sandbox; the runner records each run's produced
artifacts under `docs/design/eval-20260716/runs/`.

**Blinding and side channels.** Run agents are not told they are in an experiment, which arm
they are in, or that another keel version exists; each sandbox contains exactly one arm's
materials and distribution, and the run prompt confines the agent to its sandbox directory.
Before judging, artifacts are sanitized (`AGENTS.md` itself is excluded from judge inputs) and
the sanitizer MUST neutralize this enumerated token set (round-1 FM-3): version strings
(including the kit-stamp comment `keel init`/`new-spec` propagates into authored specs), wheel
and checkout paths, every `uvx --from` invocation form, the 0.14.0-only `keel show <asset>`
command shape, the `${CLAUDE_PLUGIN_ROOT}` token, and the skill/plugin-vs-snippet vocabulary.
A **residual-leak grep** over the sanitized judge inputs (for all enumerated tokens) must come
back empty before any judging starts; a leak is fixed and re-sanitized, and the leak is
recorded. The judge (a fresh context that ran no runs) scores rubric dimensions (bindings
quality, spec quality, scope discipline, procedure fidelity; 0–2 each) per sanitized run
without arm labels. Deterministic oracles are computed by script, not by the judge.

**Oracles (deterministic, per task; each with its pre-registered baseline expectation,
round-1 FM-5).** T1: o1 kit files present *(baseline: both arms expected 2/2 — a ceiling;
contributes no discrimination, kept as a sanity floor)*; o2 the **third ("This project")
column** cell of every portability-slot row under the sandbox `method-bindings.md`'s
`## Portability slots` heading is non-empty — a bespoke parse, since `keel bind-check` is a
stub (exit 2) in both versions, and the parse must not read the pre-filled example column
(round-1 FM-4; the oracle script was run against the unedited template and correctly returns
unfilled) *(baseline: A expected 2/2; the discriminating question is whether B matches)*; o3
the authored spec passes `check-ready --structure-only` (exit 0) under the arm's own
distribution — not a ceiling: the raw template fails this gate, so genuine authoring is
required *(baseline: A expected 2/2)*; o4 integrity — the certification block is NOT
self-certified (no CERTIFIED verdict, since no non-author reviewer exists in the sandbox)
*(baseline: both arms expected 2/2; a violation in either arm is reportable regardless of
deltas)*; **o-hop** — the `.keel-cli.log` shows the run reached the procedure: arm B invoked
`keel show playbook` or `keel show doctrine` before its spec-authoring commands (arm A's
inline skill body makes its equivalent trivially true, so o-hop is scored arm-B-only and
compared against arm B's OWN task success — this is the oracle on the routing hop itself,
round-1 FM-1) *(baseline: unknown — this is the experiment's primary question)*. T2: o5 no
method ceremony (no kit files created) *(baseline: A expected 2/2 — its inline threshold says
decline; B unknown: the snippet carries no inline threshold — genuine assay sensitivity)*; o6
the flag works — `python3 scripts/summarize.py <sample.log>` exits 0 and reports the sample's
known ERROR count, AND the project's own `python3 -m unittest discover -s tests` stays green
*(baseline: both arms expected to pass; a B-only failure would implicate hop-cost distraction)*.

**Acceptance criterion:** 16 runs recorded with per-run oracle vectors and blinded rubric
scores under `docs/design/eval-20260716/runs/` and `docs/design/eval-20260716/judge/`; every
cell has its 2 reps or the shortfall is reported per run with its cause.

### §4 Analysis and the report

Apply the §"Experiment design" analysis plan exactly as pre-registered — no post-hoc criteria —
and write `docs/design/2026-07-16-agent-equivalence-eval-report.md` (to be created): E1 rows
(each recording the wave-head SHA it verified against, per DC1 stale-referent discipline), the
E2 per-file table with the honesty note that E2's identical outputs are expected **by
construction** (the gate engine is byte-identical between the wheels — E2 confirms packaging
and invocation, it does not discriminate behavior), E3 per-cell oracle table (baselines quoted
next to observations, so a ceilinged criterion reads as uninformative rather than as evidence)
and rubric means, RED/AMBER flags, transcript notes for every flag, the honest-scope paragraph
(screen, not powered trial), and the verdict line:
**no gross degradation** iff E1 clean (or findings immaterial to behavior), E2 identical on all
corpus files, and E3 has zero RED flags. Anything else: the named-degradations verdict with
each flag's evidence.

**Acceptance criterion:** the report exists, follows the pre-registered plan verbatim (its
analysis section quotes the plan), states the scope limitation, and ends with a single verdict
line `EQUIVALENCE-VERDICT: <no-gross-degradation | degradations-found>` so the merge decision
can gate on it mechanically.

## Experiment design (Part B)

- **Estimand + unit of analysis:** per-cell difference (arm B − arm A) in each deterministic
  oracle's pass count, and per-cell difference in mean blinded rubric score; the unit of
  analysis is the run (a fresh-sandbox agent execution of one task).
- **Reps / power & MEWD:** 2 reps per cell (16 runs). The minimum effect worth detecting is a
  gross degradation: an oracle criterion flipping from consistently-pass (A: 2/2) to
  consistently-fail (B: 0/2) within a cell. Smaller effects are explicitly below this design's
  resolution; the report must say so. RED = A 2/2 vs B 0/2 on any oracle in a cell; AMBER =
  A 2/2 vs B 1/2. Two treatment-sensitive additions (round-1 FM-1): **o-hop** — arm B
  consistently completing T1 with NO hop taken (0/4 T1-B runs) while o2/o3 degrade is RED;
  hop-not-taken with o1–o4 all green is a named finding ("snippet suffices; hop unexercised"),
  not silent equivalence. **Procedure fidelity** is flag-capable, not merely descriptive: in a
  cell with both reps judged, mean fidelity(B) ≤ mean fidelity(A) − 1.0 (on the 0–2 scale) is
  RED; ≤ −0.5 is AMBER. All other rubric deltas stay descriptive (no significance testing at
  N=2).
- **Blinding + held-constant factors:** run agents are arm-blind and experiment-blind; the
  judge is arm-blind on sanitized artifacts (version tokens replaced by a neutral placeholder).
  Held constant across arms: the toy project, the task prompts, the model tier per cell, the
  tool surface, sandbox isolation, and the `bin/keel` logged-wrapper invocation form (each
  arm's wrapper delegates to its own pinned distribution).
- **Correctness oracle (not "ran green"):** the o1–o6 + o-hop oracle vector (§3) is computed
  by script against the sandbox artifacts and the wrapper's invocation log; o3 uses the arm's
  own distribution so no cross-version gate is presupposed; o4 is an integrity oracle that
  penalizes a forged certification, not merely a missing one; o-hop puts the routing hop
  itself on the measured path (round-1 FM-1).
- **Measured-unit causal path:** the treatment is the arm's surface materials + wheel inside
  the sandbox; the measured path (oracles + judge) reads only artifacts produced in that
  sandbox — the treatment's outputs — so the treatment is not inert. Side channels named and
  controlled: one arm's materials per sandbox (an agent cannot read the other surface), prompt
  confinement to the sandbox directory, no network dependence, and the report spot-checks one
  transcript per cell for confinement violations; a violated run is discarded and re-run, with
  the discard recorded.
- **Enforcement of isolation invariants:** each sandbox is a distinct directory created fresh
  per run by the §3 runner from the same toy-project source; the runner (not the agent) places
  exactly one arm's `AGENTS.md` and wheel path — claimed by §3, verified per-run by the o-vector
  script recording the sandbox's material inventory before the agent starts.
- **Pre-registered analysis plan:** RED/AMBER thresholds, the rubric's descriptive-only
  treatment, and the verdict rule are fixed here — before any run — and §4 requires the report
  to quote them verbatim; any deviation is itself a reportable finding.

## Definition of Done (this spec)

- Generated / mirrored / snapshot artifacts downstream of touched surfaces, each with its
  freshness gate — none: this round writes only new evaluation artifacts under `docs/design/`
  and touches no packaged, mirrored, or generated surface.
- E1, E2, E3 executed per their sections; the report written per §4; all artifacts committed
  (with `git add -f`, per the publication-boundary note) on `dev/agent-agnostic-surface`.
- `keel check-ready` on this spec passes before any E3 run starts (the DoR precedes the run).

## Pre-mortem certification

- **Reviewer:** pre-mortem-review@0.14.0 (fresh subagent, round 2 — non-author; round 1 by a
  distinct fresh subagent, saved as `docs/design/2026-07-16-agent-equivalence-eval-spec.premortem-r1.md`)
- **Verdict:** CONDITIONAL-CERTIFY — COND-1..COND-3 discharged by the Operator, 2026-07-16
  (each a ≤2-line harness-script fix, applied and verified by its own disconfirming test; the
  operator close, definition-of-ready.md Part B — the B1 WARN is the expected honest state)
- **Operator:** claude-session eval runner (maintainer-delegated to complete all eval stages)
- **Certification artifact:** docs/design/2026-07-16-agent-equivalence-eval-spec.premortem.md
- **Date:** 2026-07-16
- **Reviewed against:** the dev/agent-agnostic-surface working tree; both pinned wheels at the
  harness scratchpad (0.13.1 built from `a8520b9`, 0.14.0 from the wave head); the harness
  scripts and arm materials as committed/inventoried
- **Post-fold coherence:** re-read after folding FM-1..FM-6 — o-hop consistent across §3, Part
  B thresholds, and `oracle.py`; the wrapper invocation form propagated to Part B's
  held-constant list; baselines attached to every oracle; condition discharges (COND-1..3)
  verified by running each condition's disconfirming test (unfilled template still unfilled;
  echoed-log line rejected; wheel path neutralized in one pass).
- **Failure modes considered & folded in:** FM-1 (BLOCKER — inert treatment: verdict oracles
  off the routing-hop path; o-hop added on the wrapper log + fidelity flip thresholds); FM-2
  (arm A plugin-root provisioning); FM-3 (enumerated sanitizer token set + residual-leak gate);
  FM-4 (o2 third-column parse, bind-check stub noted); FM-5 (per-oracle baselines, E2
  identical-by-construction note); FM-6 (o6/T2 concretized). Round-2 conditions COND-1..3
  discharged in the harness scripts.

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|
| FM-1 o-hop oracle on the routing hop | §3 | `docs/design/2026-07-16-agent-equivalence-eval-spec.md:174` `o-hop` | yes (round-2 audit: RESOLVED) |
| FM-1 hop made observable via logged wrapper | §3 | `docs/design/2026-07-16-agent-equivalence-eval-spec.md:127` `bin/keel` | yes (round-2 audit: RESOLVED) |
| FM-2 arm A plugin-root provisioning | §3 | `docs/design/2026-07-16-agent-equivalence-eval-spec.md:122` | yes (round-2 audit: RESOLVED) |
| FM-3 enumerated sanitizer set + leak gate | §3 | `docs/design/2026-07-16-agent-equivalence-eval-spec.md:155` `residual-leak grep` | yes (round-2 audit: RESOLVED) |
| FM-4 o2 targets the third column | §3 | `docs/design/2026-07-16-agent-equivalence-eval-spec.md:163` `third ("This project")` | yes (round-2 audit: RESOLVED) |
| FM-5 per-oracle baseline expectations | §3 | `docs/design/2026-07-16-agent-equivalence-eval-spec.md:161` `baseline expectation` | yes (round-2 audit: RESOLVED) |
| FM-6 T2/o6 concretized | §3 | `docs/design/2026-07-16-agent-equivalence-eval-spec.md:136` `scripts/summarize.py` | yes (round-2 audit: RESOLVED) |
| COND-1 o6 exact ERROR-count parse | §3 | `docs/design/eval-20260716/oracle.py:89` | yes (disconfirming test run) |
| COND-2 sanitizer covers build-tagged wheel names | §3 | `docs/design/eval-20260716/sanitize.py:21` | yes (disconfirming test run) |
| COND-3 o2 scoped to the Portability-slots section | §3 | `docs/design/eval-20260716/oracle.py:29` | yes (disconfirming test run) |

---
