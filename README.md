# keel

The *method*: push control flow out of an agent's in-session context into durable
artifacts (numbered ADRs, numbered spec sections, the wave/PR DAG) and deterministic
machines (gates, hooks). **Enforced discipline beats intended discipline.**

keel ships that method two ways: a **Claude Code plugin** (the `apply-method` skill,
slash commands, a pre-mortem agent, and the template kit) and a **`keel` CLI** (the
deterministic gates).

## Install

Plugin:

```
/plugin marketplace add grimaldost/keel
/plugin install keel
```

CLI (self-contained, no install):

```
uvx --from git+https://github.com/grimaldost/keel keel --help
```

## Quickstart

- `keel init ./my-kit` — drop the template kit (DoR, DoD, checklists, spec/ADR templates) into a project.
- `keel check-ready spec.md` — Definition-of-Ready gate: spec well-formedness + a recorded blind pre-mortem.
- `/keel-apply` — have an agent set up and run the method here.

## Status

The Definition-of-Ready gate (`keel check-ready`) is live — the full Part A
well-formedness set (A1–A12, R1) plus the recorded blind pre-mortem
certification (B1); `bind-check` and `budget-drift` remain stubs (deferred,
ADR-0003). Current version and capability history: `CHANGELOG.md`.

## Learn more

Start at `AGENTS.md`, then `docs/doctrine.md`. MIT — see `LICENSE`.
