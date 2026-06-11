# ADR-0001: keel as a plugin+engine repo

- **Status:** Accepted
- **Date:** 2026-06-05

## Context

The method existed as a loose, non-git markdown folder with no delivery surface, versioning,
onboarding, or feedback intake. It is to be team-shared and registry-distributed.

## Decision

Package keel as a single repo that is simultaneously a Claude Code plugin and a Python engine,
mirroring `pr-pilot`. The plugin delivers agent-facing doctrine (skill, commands, agent,
template kit); the engine (`src/keel/` + `keel` CLI) delivers the deterministic gates. The
deterministic gate logic ships stubbed first, with its interface pinned by contract tests.

## Alternatives considered

- **Plugin-only** (no Python engine): rejected — gates would be loose scripts, not first-class
  or unit-tested, and there is no clean CLI/API for CI consumers.
- **Engine-first** (CLI, thin plugin): rejected for now — front-loads an engine whose gate
  logic does not yet exist; weaker agent ergonomics.

## Consequences

- Templates live as package data at `src/keel/templates/` so `keel init` resolves them when
  installed (refines the original root-`templates/` sketch).
- keel must hold itself to its own Definition-of-Done (CI: ruff + ty + pytest + manifest /
  template contract tests).
- New capability arrives via the feedback → triage → release loop, recorded in CHANGELOG.
