# Method bindings — <project name>

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports. The
`acme-ledger` column is a worked example (a fictional project) — replace it
with your project.

## Portability slots

| Slot (what it must provide) | `acme-ledger` binding (example) | This project |
|---|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` | |
| **Spec format** — numberable sections, acceptance criteria | committed spec + `docs/llm/TASK_PROMPT_TEMPLATE.md` | |
| **Guardrails + gate commands** — deterministic pass/fail | `docs/llm/GUARDRAILS.md`, `scripts/check_*.py`, `ruff`/`mypy`/`pytest` | |
| **Review checklist** — project-specific, blocking | `.pr-pilot/injections/review_checklist.md` (or your orchestrator's equivalent) | |
| **Reflection sink** — feeds the next round | a reflections hook → `reflections.jsonl` → your memory store | |

## Upgrade bindings

| Upgrade | What it must provide | `acme-ledger` binding (example / planned) | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `keel check-ready` | |
| **Pre-mortem** | a stateless adversarial pass | keel's bundled `pre-mortem-review` agent / a pre-series hook | |
| **Wave budget** | forecast + drift gate | `[budget]` in `series.toml` + post-PR hook | |
| **Edit-time invariant hook** | block edits that violate a boundary | `plugins/acme-contributor/hooks/pre-edit-boundary.py` | |

## Invoking the kit

The one binding that rots on its own: bind the **command**, resolved, never a
version-pinned path. A binding that pins `…/cache/keel/keel/0.15.0` names a directory the
next plugin update deletes, and the operator guesses the correction mid-session.

| | This project |
|---|---|
| Gate command | |

Forms that resolve instead of pinning — record whichever this project uses in the row above:

- In a Claude Code session, `${CLAUDE_PLUGIN_ROOT}` already IS the serving bundle's path:
  `uvx --from ${CLAUDE_PLUGIN_ROOT} keel <command>`. Nothing to resolve, nothing to pin.
- Outside one, resolve the newest installed copy rather than naming a version:
  `uvx --from "$(ls -d ~/.claude/plugins/cache/keel/keel/* | sort -V | tail -1)" keel <command>`.
- Where an application-control policy blocks console-script executables, the module form
  sidesteps the shim entirely — same path, `python -m keel` instead of the entry point:
  `uv run --no-project --with "<that path>" python -m keel <command>`.

The install routes and the reason the module form exists live in `docs/installation.md`; this
file records only which one this project runs.

## Orchestrator

| | `acme-ledger` |
|---|---|
| Series runner | a `series.toml` orchestrator (e.g. pr-pilot) — or the series table as a manual checklist |
| Single-unit discipline | a process-discipline pack (e.g. humblepowers) |
| Cross-series memory | a consolidating memory store (journals → distilled guidance) |
| Capacity dispatch | a task→(model, effort) routing policy (e.g. humblepowers' choosing-models) — otherwise the scorer's tier heuristics |

*A slot left unbound is a method-not-fully-applied warning. Bind every row before
running a series under the method.*
