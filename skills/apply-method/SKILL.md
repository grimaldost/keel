---
name: apply-method
description: Apply the keel method — the author's externalized development method — to a project. Use when the user wants to set up the method in a new repo, plan or run a governed multi-PR series, check whether a spec is ready to decompose (Definition of Ready), wire the quality gates, close the reflection loop, or asks "apply my method / my dev method / the method". Routes to the playbook, the templates, and the per-project bindings. Do NOT use for one-off scripts or single short artifacts — the method is overhead below the coordination threshold (see "When not to").
---

# Apply the method

This skill ships with keel 0.12.0 — authoritative doctrine is the **installed** keel's
`docs/doctrine.md`; if this copy's version lags `keel --version`, your plugin cache is stale
(reinstall) and this text may trail the substance it routes to.

The method externalizes discipline out of an agent's in-session judgment into
durable artifacts (ADRs, numbered spec sections, the PR DAG) and deterministic
machines (gates, hooks, the orchestrator). Full thesis and the 8 phases:
`${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md`. Toolkit (the packaged source):
`${CLAUDE_PLUGIN_ROOT}/src/keel/templates/`.

**Paths:** files inside the plugin are addressed as `${CLAUDE_PLUGIN_ROOT}/…` (they do
NOT exist in the consumer's project); files you create or bind live in the consumer's
project by their project-relative path. Run the CLI from the bundle with
`uvx --from ${CLAUDE_PLUGIN_ROOT} keel …` unless a persistent `keel` is on PATH.

## When NOT to use

A throwaway script or a single short artifact is below the threshold where
coordination cost pays. Implement it directly. Apply the method when the work clears
the blast-radius trigger in `${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md` §6 (≥5 PRs, a chokepoint
imported by ≥~50 modules, additive-on-a-shared-contract, a boundary crossing, or a
>1-quarter lifetime).

## Setting up the method in a new project

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md` (thesis + the 8 phases + mechanism map).
2. Run `uvx --from ${CLAUDE_PLUGIN_ROOT} keel init <target>` to copy the full template kit
   into the target project — ADR + spec templates, the DoR and DoD gates, the review
   checklist, reflection-triage, the series/budget skeleton, method-bindings, and the
   pre-mortem prompt.
3. Fill the `method-bindings.md` that step 2 just copied **into `<target>`** (the project's
   own copy, NOT the packaged template under `${CLAUDE_PLUGIN_ROOT}`) — bind each slot (ADR
   home, spec format, gates, review checklist, reflection sink) to a concrete mechanism.
   Any unbound slot = method not fully applied.

## Running a change under the method

**Entry: read the bindings first.** The project's `method-bindings.md` names its established
formats — spec format, ADR home, gate commands, review checklist; match those, not the packaged
templates. If the file is absent but prior method artifacts exist (earlier specs, an ADR log), the
established format IS the binding: locate a prior spec (glob for it, e.g. `docs/**/spec*.md`), bind
the slots from what you find, and write the missing `method-bindings.md` so the next round reads a
record instead of re-globbing. Run `keel init` only when the kit itself is absent.

Follow the phases; the gates are the load-bearing part:

- **Specify → DoR gate.** The spec is not ready to decompose until
  `definition-of-ready.md` passes (Part A deterministic + Part B certified by a
  non-author reviewer). Then run
  the `pre-mortem-prompt.md` pass and fold findings back in.
- **Decompose.** One PR per spec section (`spec-template.md` has the PR↔section
  manifest). Score each PR → model tier.
- **Route & Budget.** Fill the `[budget]` block in `series-toml-skeleton.md`;
  the drift gate watches the wave.
- **Implement → Gate → Review → DoD gate.** Merge only when
  `definition-of-done.md` is fully checked (deterministic gates + blocking review).
- **Reflect.** Run `reflection-triage.md` — sweep the sink's open rows, then promote
  recurring traps to a checklist item, a guardrail, or a spec-template/DoR change, and
  **land** each per the template's landing rule (apply in-context, or hand off to the
  method's feedback intake when you ran from the installed plugin). The series is not
  done reflecting until every promotion has landed.

## Not every round runs all 8 phases

A design, experiment, or triage round maps to a **subset** of the phases, named explicitly — e.g. an
experiment round runs Decide + Specify (with the measurement validity bar as its DoR) and skips
Decompose / Implement / Gate. Name the skipped phases; don't fake them. A **measurement / experiment
spec** is a recognized artifact with its own validity bar — the eval/experiment DoR items
(`definition-of-ready.md`): estimand + unit of analysis, reps / power & the minimum effect worth
detecting, blinding + held-constant factors, a correctness oracle distinct from "ran green", and a
pre-registered analysis plan.

## Source-of-truth boundary

Orchestration mechanics (`series.toml` schema, hooks, scoring tiers) belong to
the series orchestrator (e.g. pr-pilot, when installed) — link to its docs,
don't restate them here. This skill and the templates are the method layer;
the orchestrator is the orchestration layer. Without one, the series tables
still work as manual checklists.

---
*Deploy: this skill lives in `skills/apply-method/` within the keel plugin. It is
active whenever the keel plugin is installed in Claude Code.*
