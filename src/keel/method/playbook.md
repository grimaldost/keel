# The keel playbook — applying the method from any agent

This playbook ships inside the keel package; read it any time with `keel show playbook`. It is
the agent-neutral apply-method procedure: what to read, what to run, and which gate decides
each phase. The doctrine — thesis, principles, the 8 phases, the mechanism map — is the source
of truth: read it with `keel show doctrine`.

Every command below assumes `keel` is runnable. Without a persistent install, the pinned form
is equivalent: `uvx --from git+https://github.com/grimaldost/keel@<tag> keel <command>` — pin a
tag so gate semantics don't shift under you (see `docs/installation.md` in the keel repository).

## When NOT to apply the method

A throwaway script or a single short artifact is below the threshold where coordination cost
pays — implement it directly. Apply the method when the work clears the blast-radius trigger in
doctrine §6 (read it via `keel show doctrine`): it spans ≥5 PRs / units of work, or touches a
chokepoint imported by ≥~50 modules, or is additive-only on a shared contract with many
consumers, or crosses a layer/module boundary, or will be maintained beyond ~1 quarter.

## Entry: read the bindings first

The project's `method-bindings.md` names its established formats — spec format, ADR home, gate
commands, review checklist, reflection sink; match those, not the packaged templates. If the
file is absent but prior method artifacts exist (earlier specs, an ADR log), the
established format IS the binding: locate a prior spec (glob for it, e.g. `docs/**/spec*.md`),
bind the slots from what you find, and write the missing `method-bindings.md` so the next round
reads a record instead of re-globbing. Run `keel init` only when the kit itself is absent.

## Setting up the method in a new project

1. Read the doctrine (`keel show doctrine`): the thesis, the 8 phases, the mechanism map.
2. Run `keel init <target>` to copy the full template kit into the target project — ADR + spec
   templates, the DoR and DoD gates, the review checklist, reflection-triage, the series/budget
   skeleton, method-bindings, the pre-mortem prompt, and the `AGENTS.md` routing snippet.
3. Fill the `method-bindings.md` the previous step copied INTO the target (the project's own
   copy, not the packaged template) — bind each slot (ADR home, spec format, gates, review
   checklist, reflection sink) to a concrete mechanism. Any unbound slot = method not fully
   applied.
4. Paste the copied `method-agents-snippet.md` block into the project's `AGENTS.md` (or its
   equivalent agent-instructions file), so every future agent session routes into the method.

## Running a change under the method

Follow the phases; the gates are the load-bearing part:

- **Specify → DoR gate.** Scaffold with `keel new-spec <path>`; iterate in the author loop with
  `keel check-ready --structure-only <path>` (Part A, well-formedness). The spec is not ready
  to decompose until the full `keel check-ready <path>` passes — which requires the pre-mortem
  below (Part B).
- **Pre-mortem (the externalized correctness pass).** Print the prompt with
  `keel show pre-mortem` and run it in a FRESH context that did not author the spec — a second
  agent session, a subagent with a clean context, or another operator. Save the pass's returned
  output verbatim to the sibling `<spec-stem>.premortem.md`, prepending a short header: the
  spec path, the date, the reviewer, and `Spec-hash:` from `keel spec-hash <path>`. Then fold:
  re-ground each `smallest_fix` against the code first (it is a hypothesis, not an
  instruction), fold it into its target section, run a post-fold coherence re-read, and record
  the certification block (Reviewer, Verdict, Certification artifact, fold ledger).
  `keel check-ready` passes only once the certification is recorded.
- **Decompose.** One PR per spec section (the spec template carries the PR↔section manifest).
  Score each PR to a capacity tier per the project's dispatch binding.
- **Route & Budget.** Fill the `[budget]` block in the copied `series-toml-skeleton.md`; the
  drift gate watches the wave.
- **Implement → Gate → Review → DoD gate.** Fresh context per PR, reading its section. Merge
  only when the copied `definition-of-done.md` is fully checked (the project's deterministic
  gate commands from `method-bindings.md`, plus the blocking review checklist).
- **Reflect.** Run the copied `reflection-triage.md` — sweep the sink's open rows, promote each
  recurring trap to exactly one durable home (a checklist item, a guardrail/gate, or a
  spec-template/DoR change), and land every promotion per the template's landing rule.

## Not every round runs all 8 phases

A design, experiment, or triage round maps to a subset of the phases, named explicitly — e.g.
an experiment round runs Decide + Specify (with the measurement validity bar as its DoR) and
skips Decompose / Implement / Gate. Name the skipped phases; don't fake them. A measurement /
experiment spec is a recognized artifact with its own validity bar — the eval/experiment items
in the copied `definition-of-ready.md`.

## Source-of-truth boundary

Orchestration mechanics (series schemas, hooks, scoring tiers) belong to the project's series
orchestrator, when one is bound — link to its docs, don't restate them. This playbook and the
templates are the method layer; the orchestrator is the orchestration layer. Without one, the
series tables still work as manual checklists.
