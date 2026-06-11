---
name: apply-method
description: Apply the keel method — the author's externalized development method — to a project. Use when the user wants to set up the method in a new repo, plan or run a governed multi-PR series, check whether a spec is ready to decompose (Definition of Ready), wire the quality gates, close the reflection loop, or asks "apply my method / my dev method / the method". Routes to the playbook, the templates, and the per-project bindings. Do NOT use for one-off scripts or single short artifacts — the method is overhead below the coordination threshold (see "When not to").
---

# Apply the method

The method externalizes discipline out of an agent's in-session judgment into
durable artifacts (ADRs, numbered spec sections, the PR DAG) and deterministic
machines (gates, hooks, the orchestrator). Full thesis and the 8 phases:
`docs/doctrine.md`. Toolkit: `src/keel/templates/`.

## When NOT to use

A throwaway script or a single short artifact is below the threshold where
coordination cost pays. Implement it directly. Apply the method when the work clears
the blast-radius trigger in `docs/doctrine.md` §6 (≥5 PRs, a chokepoint imported by
≥~50 modules, additive-on-a-shared-contract, a boundary crossing, or a >1-quarter lifetime).

## Setting up the method in a new project

1. Read `docs/doctrine.md` (thesis + the 8 phases + mechanism map).
2. Run `keel init <target>` to copy the full template kit from `src/keel/templates/`
   into the target project — ADR + spec templates, the DoR and DoD gates, the review
   checklist, reflection-triage, the series/budget skeleton, method-bindings, and the
   pre-mortem prompt.
3. Fill `src/keel/templates/method-bindings.md` — bind each slot (ADR home, spec
   format, gates, review checklist, reflection sink) to a concrete mechanism.
   Any unbound slot = method not fully applied.

## Running a change under the method

Follow the phases; the gates are the load-bearing part:

- **Specify → DoR gate.** The spec is not ready to decompose until
  `definition-of-ready.md` passes (Part A deterministic + Part B signed). Then run
  the `pre-mortem-prompt.md` pass and fold findings back in.
- **Decompose.** One PR per spec section (`spec-template.md` has the PR↔section
  manifest). Score each PR → model tier.
- **Route & Budget.** Fill the `[budget]` block in `series-toml-skeleton.md`;
  the drift gate watches the wave.
- **Implement → Gate → Review → DoD gate.** Merge only when
  `definition-of-done.md` is fully checked (deterministic gates + blocking review).
- **Reflect.** Run `reflection-triage.md` — promote recurring traps to a
  checklist item, a guardrail, or a spec-template/DoR change. The series is not
  done reflecting until this is done.

## Source-of-truth boundary

Orchestration mechanics (`series.toml` schema, hooks, scoring tiers) belong to
the series orchestrator (e.g. pr-pilot, when installed) — link to its docs,
don't restate them here. This skill and the templates are the method layer;
the orchestrator is the orchestration layer. Without one, the series tables
still work as manual checklists.

---
*Deploy: this skill lives in `skills/apply-method/` within the keel plugin. It is
active whenever the keel plugin is installed in Claude Code.*
