# Method

How I build with Claude Code: the thesis, the phases, and where each one lives.
This is a spine — it **names and links**; it does not restate the mechanism
docs, which stay the source of truth. Reference bindings below are drawn from a
production consumer, fictionalized here as `acme-ledger`.

## 1. Thesis

Two agentic development flows can have the identical shape — brainstorm → spec →
plan → implement (TDD) → review → finish — and still produce very different
quality. The shape is not the differentiator. **What differs is where the
discipline and the control flow live.**

This method pushes control flow *out* of any single agent's accumulating
in-session context and *into* two places: durable, addressable artifacts
(numbered ADRs, numbered spec sections, the wave/PR DAG) and deterministic
machines (quality gates, an edit-time hook, a series orchestrator). A generic
flow runs the same control flow *through* the model's in-session judgment — the
weakest point, because that is exactly where an LLM struggles: noticing it has
drifted, knowing when it is done, recognizing that "while I'm here…" is scope
creep.

The two are equivalent on a 200-line task and unequal on a 20-PR refactor.
Cohesion at scale is a coordination problem. This method solves it the way a
distributed system does — one source of truth (the numbered spec), stateless
workers (a per-PR subagent that reads its section fresh and carries no drift),
enforced invariants (gates and hooks). A generic flow solves it the way one
careful person does — hold the whole thing in working memory and stay
disciplined. The person degrades over a long enough task; the system does not.

**Enforced discipline beats intended discipline.** A generic flow *has* the same
capabilities — checkpointed plans, fresh-context subagents, durable specs,
verification before completion — but they are opt-in, chosen mid-session. This
method makes them mandatory, external, and deterministic. That gap is the point.

**Evidence status (calibration).** This is the method's wager, not a proven theorem.
It is validated on **three governed waves** (kernel / authenticator / compute
rounds on a production consumer, reported through the feedback intake), where a
blind pre-mortem caught cross-PR
blockers before code and the §↔PR bijection made salvages tractable. A controlled
experiment against a disciplined baseline is still pending
(`docs/design/2026-06-06-keel-validation-experiment.md`): until it runs, read the
claims here as "designed to, and so far observed to," not "measured to beat" a careful
generic flow.

| What governs quality | Generic agentic flow | This method |
|---|---|---|
| Scope / the plan | In-session plan; agent judges step size | Numbered spec sections, pre-committed; each commit cites one |
| Context | Accumulates over the session → drifts | Reset per PR; the subagent reads its section fresh |
| Invariants | Agent remembers to check | Machine-enforced: edit-time hook + guardrail scripts + gates |
| Review | Generic review | 15-item project checklist, injected, blocking |
| Scope discipline | Agent restraint | Complexity scoring as a forcing function — a vague PR can't be scored |
| Learning across rounds | None by default | Reflections → cross-project memory → next round's checklist |

## 2. Principles

Each principle is one face of the thesis: take a governance dimension out of the
agent's head and pin it to an artifact or a machine.

- **Scope → numbered spec sections.** The agent implements a *section*; it does
  not decide the boundary. The boundary was set by a different process at a
  different time.
- **Context → reset per PR.** Each worker reads its section fresh and carries no
  accumulated drift.
- **Invariants → machines, not memory.** An edit-time hook, guardrail scripts,
  and deterministic gates enforce the boundaries so the agent doesn't have to
  remember them.
- **Cheapest adequate tool.** Each PR is complexity-scored to a model tier; cost
  is tracked per unit and per wave.
- **Fail closed.** Gates block, review blocks, and there is an explicit salvage
  round — nothing green-lights itself.
- **Close the loop.** Reflections are extracted to cross-project memory and feed
  the next round's checklist, so a class of bug bites once. A promoted check ships
  with a regression test, and a gate that never fires is itself a triage input —
  gates decay, so their hit-rate is tracked.

Sharpenings (each one face of the thesis; numbered, not counted in the heading):

1. **Externalization relocates judgment; it does not remove it.** Stateless
   workers will faithfully and coherently build a wrong spec — coherently wrong
   is still wrong. The quality burden moves earlier, onto spec and ADR authoring,
   and its stakes rise. Spec quality becomes the single point of failure. This is
   why the Definition-of-Ready gate (§7) is the highest-leverage upgrade, not a
   nice-to-have.
2. **Keep the coordinate system current.** A spec frozen at t0 while reality
   diverges by PR12 makes workers measure against a stale spec. ADR supersession
   and amending spec sections mid-wave is the mechanism; a frozen source of truth
   re-introduces staleness as a different failure mode.
3. **Feedback flows up; keel never reaches down.** A project that applies the method
   reports *up* into keel's feedback intake; keel extracts the project-agnostic lesson and
   declines the project- or engine-specific residue (the reporter owns it, and keel does not
   track or modify a consumer). Keep method-correctness and engine/execution-resilience as
   separate ledgers — a healthy method must not be blamed for an orchestrator fault, nor an
   executor fix smuggled into a method gate.
4. **Ground referents, and verify the fold.** Code-grounding extends past factual anchors to
   *referents* — a "reuse the proven X" target, a "model-on" file, a claimed-existing seam, a
   superseded prior decision — each verified against the current code or register, never
   trusted from the prose ("proven" means proven on the original caller's shapes, not yours).
   And the fold of pre-mortem findings back into the spec is itself a **verified hop**:
   structured findings are folded mechanically, then a post-fold coherence re-read catches the
   half-applied finding no gate can see; and each proposed fix is re-grounded as a hypothesis before
   it is folded, since applying a wrong fix verbatim ships the bug it named. `check-ready` mechanizes the slices it can (A8 §-refs,
   A9 reuse-targets, A10 enforcement-claim honesty); the rest stays a pre-mortem prompt and an
   attested re-read (ADR-0004).
5. **Ground the verification, model the mechanical consumers, verify the transformation.**
   Sharpening 4 grounds the *referent* and verifies the fold; sharpening 5 extends it one level out,
   across the three axes the field showed dominate once Part A holds. **(DC1) Ground the
   verification, not just the referent:** a claim the author "verified" is still wrong if the view
   was partial (exemplars, not the population), stale, moved (an external dep's SHA shifted), or
   wrong-shaped (a line-anchor blind to indented code) — and a verifier's own script gets the same
   scrutiny as the spec. **(DC2) Model the mechanical consumers:** the spec models the logical
   design, but the in-place toolchain, the autofixer, and staged files consume the artifact too — a
   staged `.py` pollutes `mypy .`, a diff-shape rule contradicts isort. **(DC3) Verify the
   transformation:** the fold/fix is an unverified, instance-scoped delta — a per-finding ledger and
   class-not-instance scope close it. What is mechanizable ships as a gate (A11 anchor ranges, A12
   fold-ledger anchors); the rest is a pre-mortem directive or routed out — ADR-0002's
   form/correctness split and ADR-0004's grounding/fold, held one level up (ADR-0005).

These operating notes carry sharpening 5 into practice:

- **Two-pass cadence (DESIGN ⊕ SERIES), blast-radius-scaled.** For a wave touching enforcement or a
  shared contract, run two blind pre-mortems: a DESIGN pass (contract / radius / vacuity / projected
  verification) and a SERIES pass (execution mechanics, prompt-internal contradictions, staging×gate
  interactions — and it attacks the DESIGN pass's folds). One pass suffices only when the wave is
  docs-only / zero-behaviour-change AND the first pass is CERT-clean AND no executable gate changes.
- **Verification convergence.** Hardened verification must terminate: a pass STOPS when it surfaces
  zero new BLOCKER/MAJOR findings, and a `CONDITIONAL-CERTIFY` (ready modulo a named ≤N-line fix)
  avoids forcing a full extra round (`pre-mortem-prompt.md`). Unbounded verification is the cost
  centre the spine would otherwise create.
- **Cost-of-defect (why the left-shift pays).** Field accounting prices a correctness defect caught
  late at roughly 30× its design-time cost (~$347, 41% of one $853 program, vs ~$3 caught at design).
  This is the quantified form of the §1 evidence-status note — the economic case for spending the
  pre-mortem/gate budget up front.
- **Cross-artifact completeness & the pre-cut audit.** Per-wave gates verify each wave internally;
  whether artifacts that must AGREE actually do — the design's named reviewer-subset vs the
  executable command, a generated mirror vs the surface a later PR mutates, the cumulative CHANGELOG
  vs every wave's new surface — is a cross-artifact property no per-wave gate sees (a consistency
  gate checks cross-references, not completeness). Two practices close it: release-notes land IN the
  wave that adds the surface or changes behaviour, and a cross-cutting blind audit (the consumer's
  DoD#9-style panel: boundaries · API-surface · contracts · release-docs) runs once before a release
  cut. The pre-mortem carries the per-wave directives (`pre-mortem-prompt.md`); the executable diff
  and the release-notes mechanization route to the orchestrator (pr-pilot).

## 3. Phases

Each phase has an artifact, an entry gate (Ready), and an exit gate (Done).

| Phase | Artifact | Entry gate (Ready) | Exit gate (Done) |
|---|---|---|---|
| 1 Decide | Numbered ADR | A choice with non-obvious trade-offs is identified | ADR written, numbered, Accepted; alternatives + decision + consequences recorded |
| 2 Specify | Committed spec w/ numbered sections + concept DAG | Relevant ADRs exist; scope bounded | Every concept maps to a module; every invariant touched is named; sections numbered so commits can cite them |
| 3 Decompose | Wave/PR DAG (`series.toml`) | Spec sections stable | Each PR cites exactly one section; one concern per PR; deps expressed as a DAG |
| 4 Route & Budget | Per-PR complexity score → model tier; wave cost estimate | PR prompts precise enough to score | Each PR has a tier; wave has an estimated cost vs all-Opus baseline |
| 5 Implement | Branch/diff per PR | PR prompt + its spec section in hand; fresh context | Single-concern change; no invariant violated (edit-time hook did not block) |
| 6 Gate | Deterministic gate results | Implementation believes it is done | ruff format/check, mypy, pytest, guardrail scripts all pass (fail-closed) |
| 7 Review | Reviewer verdict vs 15-item checklist | Gates green | APPROVE (or salvage round closed); no blocking checklist item open |
| 8 Reflect | Reflection entries → memory | PR merged | Reflections extracted; any recurring trap promoted to a checklist item / guardrail for next round |

## 4. Mechanism map

Where each phase is implemented. The `acme-ledger` column is an **example binding**
(a fictionalized production consumer), not part of the agnostic contract — another
project binds its own tools in `method-bindings.md`. Paths are references, not
links (this doc lives in a different repo).

| Phase | System | `acme-ledger` reference |
|---|---|---|
| Decide | ADR log | `docs/adr/` |
| Specify | Spec + prompt template | committed spec + `docs/llm/TASK_PROMPT_TEMPLATE.md` |
| Decompose | orchestrated series (e.g. pr-pilot) | `docs/llm/PR_ORCHESTRATION.md`, `pr-series/`, `series.toml` |
| Route & Budget | scorer + model tiers | the orchestrator's `model-tiers` / `pr-prompt-scorer` skills |
| Implement | conventions + edit-time hook + TDD | `AGENTS.md`, `plugins/acme-contributor/hooks/pre-edit-boundary.py`, a TDD discipline skill |
| Gate | guardrails + gate commands | `docs/llm/GUARDRAILS.md`, `scripts/check_*.py`, `docs/llm/DEV_WORKFLOW.md` |
| Review | reviewer + checklist | `.pr-pilot/injections/review_checklist.md`, the orchestrator's reviewer, `/review-pr` |
| Reflect | reflection hook → memory | a reflections hook → `reflections.jsonl` → a consolidating memory store |

Three **roles** implement the phases, at three scopes — each filled by a reference-binding
tool a project swaps in `method-bindings.md`:

- **Single-unit discipline** — brainstorm → plan → TDD → review → finish for one unit of
  work. *Reference binding:* a process-discipline pack (e.g. humblepowers).
- **Series orchestration** — a series of units (the wave/PR DAG, gates between phases, model
  routing, injections, reflection extraction). *Reference binding:* a `series.toml`
  orchestrator (e.g. pr-pilot).
- **Cross-series memory** — the loop across series (journals → meditation → doctrine; this
  doc is the doctrine tier). *Reference binding:* a consolidating memory store.

## 5. Composition

The three systems are nested instances of one method: **task ⊂ series ⊂
program.** The discipline pack governs the task; the orchestrator governs the
series of tasks; the memory store governs across series. One method, three
scopes — and each role works standalone: a missing binding degrades the method
to manual checklists at that scope, never to a broken one.

## 6. When to use it (and when not to)

The method is bought with cost and structure — multiple agents, gates, reviews,
salvage rounds. The trigger is **blast radius, not PR count**: a 4-PR wave on a
kernel imported by 142 modules earned the full ceremony (field evidence in the
feedback intake), while a 200-line script does not. Apply
the method when **any** of these hold — each checkable before you start:

- it spans **≥ 5 PRs / units of work**; or
- it touches a **chokepoint imported by ≥ ~50 modules** (a high-blast-radius dependency); or
- it is **additive-only on a shared contract** with many consumers (a public API, a schema,
  a redaction rule); or
- it **crosses a layer or module boundary**; or
- the corpus will be **maintained beyond ~1 quarter**.

Otherwise it is pure overhead — a throwaway script or a single short artifact below the
coordination threshold. (This doc was written inline by one writer.) The method applies its
own scope discipline to itself.

## 7. Portability checklist

To run this method in a new project, fill these slots (SP2 provides a template
for each):

- [ ] an ADR home (a `docs/adr/`-style log)
- [ ] a spec format with numberable sections
- [ ] a guardrails doc + deterministic quality-gate commands
- [ ] a project-specific review checklist
- [ ] a reflection sink that feeds the next round

**Known gaps → SP3.** The top upgrade is a **Definition-of-Ready gate** (`keel
check-ready`, shipped 0.2.0): it gates spec *well-formedness* deterministically and
externalizes spec *correctness* to a required, blind pre-mortem certification — not a
check "symmetric to" the Definition-of-Done (DoD has an executable oracle; DoR does
not). It addresses the last soft spot — spec and prompt quality (per sharpening 1 and
ADR-0002).
