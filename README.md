<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/keel-hero-dark.svg">
  <img alt="keel" src="assets/keel-hero-light.svg" width="100%">
</picture>

[![ci](https://img.shields.io/github/actions/workflow/status/grimaldost/keel/ci.yml?branch=main&style=flat-square&label=ci&labelColor=2A3238)](https://github.com/grimaldost/keel/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.11%2B-255691?style=flat-square&labelColor=2A3238)](pyproject.toml)
[![license](https://img.shields.io/badge/license-MIT-255691?style=flat-square&labelColor=2A3238)](LICENSE)

The *method*: push control flow out of an agent's in-session context into durable
artifacts (numbered ADRs, numbered spec sections, the wave/PR DAG) and deterministic
machines (gates, hooks). **Enforced discipline beats intended discipline** — the method's
wager, designed to and so far observed to, never measured to beat a disciplined baseline
(see [`docs/evidence.md`](docs/evidence.md)).

keel ships that method two ways: a **Claude Code plugin** (the `apply-method` skill, four
`/keel-*` slash commands, a pre-mortem agent, and the template kit — see
[`docs/plugin-reference.md`](docs/plugin-reference.md)) and a **`keel` CLI** (the
deterministic gates — see [`docs/cli-reference.md`](docs/cli-reference.md)).

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

The full first loop, with the exact commands in order:
[`docs/getting-started.md`](docs/getting-started.md).

## Status

The Definition-of-Ready gate (`keel check-ready`) is live — the full Part A
well-formedness set plus the recorded blind pre-mortem certification (B1)
and its saved-artifact verification (B2, with `keel spec-hash`). The
command set, and each command's status, is the table in
[`docs/cli-reference.md`](docs/cli-reference.md) — pinned by tests, where
this paragraph's hand-kept copy is the one that drifted. Current version
and capability history: [`CHANGELOG.md`](CHANGELOG.md).

## Learn more

- [docs/getting-started.md](docs/getting-started.md) — the first full loop, with the exact commands
- [docs/README.md](docs/README.md) — the full reading ladder
- [docs/doctrine.md](docs/doctrine.md) — the method itself
- [AGENTS.md](AGENTS.md) / [CONTRIBUTING.md](CONTRIBUTING.md) — working on keel itself

MIT — see [LICENSE](LICENSE).
