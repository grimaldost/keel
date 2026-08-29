# ADR-0019: closing the July agent-surface eval branches

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Two origin branches have sat untouched since 2026-07-16, with no recorded disposition:

- `origin/dev/agent-agnostic-surface` (tip `978ac3d`, 16 commits not on main) — the 0.14.0
  agent-agnostic-surface equivalence evaluation: a certified experiment spec, the E1/E2/E3 run
  artifacts (oracle vectors, blind mapping, 16/16 runs), and the closing report
  `2026-07-16-agent-equivalence-eval-report.md`.
- `origin/claude/keel-ai-agent-compat-zz8xk8` (tip `f421871`) — an ancestor of the branch
  above; it carries nothing the other does not.

The work these branches served **shipped**: 0.14.0's agent-agnostic surface is on main and
released. What never landed anywhere durable is the eval's *conclusion* — the branch tip is the
only home of a verdict the repo's own discipline says should be citable. An unmerged branch is
not a record; it is a place a record goes to be forgotten.

## Decision

**The conclusion is folded here; the branches are closed.** The report's verdict, quoted from
`978ac3d`:

> **EQUIVALENCE-VERDICT: no-gross-degradation**

Its pre-registered layers all came back clean: E1 content-equivalence 6/6 rows, E2 gate-behavior
capture pairs byte-identical 24/24 (expected by construction — the gate engine was byte-identical
between the wheels; E2 guards packaging and invocation only), E3 blinded behavioral runs zero RED
and zero AMBER, with the only integrity failures observed sitting in the 0.13.1 *baseline* arm.
The report's own scope note is part of the record: this was an **equivalence screen, not a
powered trial** — 2 reps per cell detects gross degradation and large fidelity drops, bounds no
small delta, and makes no superiority claim in either direction (ADR-0015). Ceilinged criteria
read as uninformative, not as positive evidence.

That is the whole load the branches carry. With it recorded here, both remote branches can be
deleted:

```
git push origin --delete dev/agent-agnostic-surface
git push origin --delete claude/keel-ai-agent-compat-zz8xk8
```

Deletion discards the raw E1/E2/E3 run artifacts (they remain reachable from any clone that
fetched the branches, and from the reflog on the machine that ran the eval, for as long as those
live). That is accepted: the artifacts' evidentiary value was consumed by the report, the report's
conclusion now lives here, and re-running the screen against a current keel would need a fresh
spec anyway — a 0.14.0-era capture set cannot certify a 0.18.0 surface.

## Consequences

- The equivalence screen's verdict is citable from main without archaeology, at the honest
  strength the report itself states.
- "Which branches are live" returns to meaning something: after this ADR merges and the two
  deletions run, every remote branch is either `main` or an open PR.
- Anything that wants more than a screen-strength claim (a powered comparison, a superiority
  claim) starts from a new spec and a new ADR, not from these branches.
