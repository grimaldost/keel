# keel — Agent Instructions

> **What is keel?** The *method*: control flow out of an agent's head, into durable
> artifacts and deterministic machines. This repo delivers it as a Claude Code plugin
> plus a `keel` CLI.

Read in this order:

1. `README.md` — what keel is, install, quickstart
2. `docs/doctrine.md` — thesis, 6 principles, 8 phases (the source of truth)
3. `docs/concepts.md` — task ⊂ series ⊂ program; the three systems
4. `docs/phases-reference.md` — each phase + its gate
5. `CONTRIBUTING.md` — how to improve keel (feedback → triage → release)

## Conflict policy

- If guidance conflicts, `docs/doctrine.md` wins over other docs.
- If docs and code diverge, code wins.

## Stack & conventions

- Python >= 3.11, `uv`, `ruff` + `ty` + `pytest`. Single-quote ruff format.
- User-facing errors use `keel.errors.format_error(what, why, fix)`.
- Gates return `keel.models.GateResult`; never `print()` from engine code.
- Templates are package data at `src/keel/templates/`.

## Quality gates (must pass)

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check src
uv run pytest
```

## How to change keel

Each recurring lesson becomes exactly one of: a template/doctrine edit, a new gate in
`src/keel/`, or an ADR in `docs/adr/`. Record it in `CHANGELOG.md` and bump the version.
See `CONTRIBUTING.md` and `src/keel/templates/reflection-triage.md`.
