# ADR-0017: one home for the pre-mortem directives

- **Status:** Accepted
- **Date:** 2026-08-11
- **Narrows:** ADR-0005 §"the verification spine" (which created the **agent ⇄ prompt fidelity**
  invariant and its drift guard), ADR-0006 §4, ADR-0007, ADR-0008, ADR-0009, ADR-0010 and
  ADR-0016 (each of which added a directive "byte-identical in both files, drift-guarded")
- **Relates to:** ADR-0003 (thinness — the template stays the consumer-facing copy), ADR-0011
  (the enforcement gap — the escalation rule this ADR applies to itself)

## Context

The pre-mortem directive text lived in two files that were ~90% identical: `agents/pre-mortem-review.md`
(~2,300 words) and `src/keel/templates/pre-mortem-prompt.md` (~2,500 words). ADR-0005 created that
arrangement deliberately — the 0.4.0 release had upgraded the template and left the agent on the
0.2.0 "top 5" prose, so the agent that actually ran lagged keel's own doctrine — and every ADR since
has added directives to *both* files under a drift guard (`tests/test_premortem_agent.py`) that
pinned a marker tuple whose length was bumped on every release, 22 → 33 → 34.

The guard held the invariant it was built for: neither copy could silently drop a pinned directive,
and after the 0.11.0 skeptic panel found a reworded-on-one-side divergence, a clause-identity layer
closed that hole too. What it could not hold is the failure the doctrine actually forbids — growth.
The pair has only ever grown, one clause per finding, across six ADRs; the guard's own marker count
is the visible record of it (KEEL-B06). And the duplication is what made growth cheap: any edit was
already a two-file edit, so a promotion never had to argue for its own displacement.

Everything else queued against the directive text (a widened population clause, a lens split, a
measured ablation) was sequenced behind this decision, because each would otherwise land twice.

## Decision

**The template is the single home of the pre-mortem directive text.** `src/keel/templates/pre-mortem-prompt.md`
carries every directive; it survives as the home rather than the agent because it is the copy that
reaches consumers running the method without the plugin (`keel init`), and an orchestrator's
pre-series hook or a manual pass reads the same file.

**The bundled agent is a thin wrapper.** `agents/pre-mortem-review.md` carries its frontmatter, its
identity line (the fifth version site), a first-action instruction to Read
`${CLAUDE_PLUGIN_ROOT}/src/keel/templates/pre-mortem-prompt.md` and apply every directive in it, a
short task statement, and the output contract a caller greps (the verdict line, the findings-schema
keys, the `Unverified-offline:` count, read-only-ness). It states what to do when the path does not
resolve — Glob for the file, and if no copy is reachable, say so in the first line rather than
inventing directives.

**The drift guard is retired with the duplication it existed to hold together.** What replaces it is
the arrangement: a test asserts the agent names the template's path, that sampled directive clauses
appear in the template and **not** in the agent, and that the identity line resolves to the running
version. Non-duplication is now the guarded property, which is the growth failure the marker tuple
could never see.

## Alternatives considered

- **Keep the pair and keep bumping the guard.** Rejected: it holds drift and licenses growth, and
  the growth is the defect actually observed. The guard also has to be edited on every directive
  change, so the cost is paid per release forever.
- **Generate the agent body from the template at build time.** Rejected: it removes the drift but
  keeps the two artifacts, adds a build step to a repo whose kit is plain markdown copied by
  `keel init`, and leaves the same prose bloat with a generator in front of it.
- **Fold the other way — the agent as the home, the template a pointer.** Rejected by ADR-0003:
  a consumer who runs the method without the plugin gets the template kit and nothing else, so a
  pointer into `agents/` would leave that consumer with no directives at all.
- **Delete the directive body outright and let a strong model review adversarially.** Not decided
  here — that is a measurement (KEEL-B09), and this ADR is what gives it one body to measure.

## Consequences

- **New invariant — one home per directive.** A directive is added, reworded or retired in
  `pre-mortem-prompt.md` and nowhere else. Re-inlining directive text into the agent is a test
  failure, not a review remark.
- The agent now depends on a file Read at run start. If that Read fails the pass still runs, under
  a reduced contract, and **says so in its first line** — a degraded pass that announces itself,
  rather than a silent one. This is the residual this decision buys, and it is named, not hidden.
- Editing a directive is a one-file edit, so a promotion can no longer hide its cost in a
  two-file diff. The complement is a body budget (KEEL-B06, landing in the same wave): CONTRIBUTING
  caps the directive body and the spec-template's contract notes, and requires a promotion to name
  what it displaces. Without the budget the compression this fold enables would simply refill.
- Six ADRs' "byte-identical in both files" clauses no longer describe the tree. They are not edited
  (an Accepted decision is superseded, never rewritten); this ADR is the record that the mechanism
  they name has been narrowed to one file.
