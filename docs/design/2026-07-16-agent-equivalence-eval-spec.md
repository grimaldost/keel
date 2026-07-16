# Spec — Equivalence evaluation: keel 0.14.0 (agent-agnostic surface) vs 0.13.1

- **Date:** 2026-07-16
- **Status:** draft
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
the full 0.13.1 skill body text (as the plugin would present it), with the pinned 0.13.1 wheel
as its `keel`. Arm B (candidate): a sandbox whose `AGENTS.md` carries the 0.14.0
`method-agents-snippet.md` block (as `keel init` ships it), with the pinned 0.14.0 wheel; the
procedure is only reachable through `keel show playbook` — the routing hop under test. In both
arms the pinned-wheel invocation replaces the snippet's git-pinned `uvx` form (no network in
the sandbox; held constant across arms).

**Tasks.** T1 (above threshold): "this project will undergo a multi-PR refactor on a shared
contract; set up the development method per AGENTS.md, author the refactor spec, and iterate
until the structural readiness gate passes — do not implement, do not self-certify." T2 (below
threshold): "add a small flag to this script" — the correct behavior is to implement directly
and NOT apply the method (the when-not-to routing).

**Cells and reps.** 2 tasks × 2 strengths (a weaker and a stronger model tier, held identical
across arms) × 2 arms = 8 cells, 2 reps each = 16 runs. Each run gets a fresh copy of the same
toy consumer project in an isolated scratchpad sandbox; the runner records each run's produced
artifacts under `docs/design/eval-20260716/runs/`.

**Blinding and side channels.** Run agents are not told they are in an experiment, which arm
they are in, or that another keel version exists; each sandbox contains exactly one arm's
materials and wheel, and the run prompt confines the agent to its sandbox directory. Before
judging, artifacts are sanitized: version strings and any arm-identifying token are replaced by
neutral placeholders; the judge (a fresh context that ran no runs) scores rubric dimensions
(bindings quality, spec quality, scope discipline, procedure fidelity; 0–2 each) per sanitized
run without arm labels. Deterministic oracles are computed by script, not by the judge.

**Oracles (deterministic, per task).** T1: o1 kit files present; o2 every portability-slot row
of the sandbox `method-bindings.md` has a non-empty project cell; o3 the authored spec passes
`check-ready --structure-only` (exit 0) under the arm's own wheel; o4 integrity — the
certification block is NOT self-certified (no CERTIFIED verdict, since no non-author reviewer
exists in the sandbox). T2: o5 no method ceremony (no kit files created); o6 the flag works —
the sandbox project's own test command passes.

**Acceptance criterion:** 16 runs recorded with per-run oracle vectors and blinded rubric
scores under `docs/design/eval-20260716/runs/` and `docs/design/eval-20260716/judge/`; every
cell has its 2 reps or the shortfall is reported per run with its cause.

### §4 Analysis and the report

Apply the §"Experiment design" analysis plan exactly as pre-registered — no post-hoc criteria —
and write `docs/design/2026-07-16-agent-equivalence-eval-report.md` (to be created): E1 rows,
E2 per-file table, E3 per-cell oracle table and rubric means, RED/AMBER flags, transcript notes
for every flag, the honest-scope paragraph (screen, not powered trial), and the verdict line:
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
  A 2/2 vs B 1/2; rubric deltas are descriptive only (no significance testing at N=2).
- **Blinding + held-constant factors:** run agents are arm-blind and experiment-blind; the
  judge is arm-blind on sanitized artifacts (version tokens replaced by a neutral placeholder).
  Held constant across arms: the toy project, the task prompts, the model tier per cell, the
  tool surface, sandbox isolation, and the pinned-wheel invocation form.
- **Correctness oracle (not "ran green"):** the o1–o6 oracle vector (§3) is computed by script
  against the sandbox artifacts; o3 uses the arm's own wheel so no cross-version gate is
  presupposed; o4 is an integrity oracle that penalizes a forged certification, not merely a
  missing one.
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

- **Reviewer:**
- **Verdict:** not yet certified
- **Operator:**
- **Certification artifact:**
- **Date:**
- **Reviewed against:**
- **Post-fold coherence:**
- **Failure modes considered & folded in:**

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|

---
