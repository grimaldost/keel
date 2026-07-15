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

## Orchestrator

| | `acme-ledger` |
|---|---|
| Series runner | a `series.toml` orchestrator (e.g. pr-pilot) — or the series table as a manual checklist |
| Single-unit discipline | a process-discipline pack (e.g. humblepowers) |
| Cross-series memory | a consolidating memory store (journals → distilled guidance) |
| Capacity dispatch | a task→(model, effort) routing policy (e.g. humblepowers' choosing-models) — otherwise the scorer's tier heuristics |

*A slot left unbound is a method-not-fully-applied warning. Bind every row before
running a series under the method.*
