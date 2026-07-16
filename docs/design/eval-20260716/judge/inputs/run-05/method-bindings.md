# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports. The
`acme-ledger` column is a worked example (a fictional project) — replace it
with your project.

## Portability slots

| Slot (what it must provide) | `acme-ledger` binding (example) | This project |
|---|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` | `docs/adr/` |
| **Spec format** — numberable sections, acceptance criteria | committed spec + `docs/llm/TASK_PROMPT_TEMPLATE.md` | `spec-*.md` in project root (numbered sections, PR↔section manifest) |
| **Guardrails + gate commands** — deterministic pass/fail | `docs/llm/GUARDRAILS.md`, `scripts/check_*.py`, `ruff`/`mypy`/`pytest` | `python3 -m pytest tests/ -v`, `python3 -m mypy src/` (existing tests + type checking) |
| **Review checklist** — project-specific, blocking | `.pr-pilot/injections/review_checklist.md` (or your orchestrator's equivalent) | `review-checklist.md` (project root) |
| **Reflection sink** — feeds the next round | a reflections hook → `reflections.jsonl` → your memory store | `reflections.md` in project root (manual checklist of lessons) |

## Upgrade bindings

| Upgrade | What it must provide | `acme-ledger` binding (example / planned) | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `keel check-ready` | `<KEEL-CLI> check-ready spec-*.md` |
| **Pre-mortem** | a stateless adversarial pass | keel's bundled `pre-mortem-review` agent / a pre-series hook | `pre-mortem-prompt.md` (manual, non-author reviewer required) |
| **Wave budget** | forecast + drift gate | `[budget]` in `series.toml` + post-PR hook | `series-toml-skeleton.md` (manual tracking, no orchestrator) |
| **Edit-time invariant hook** | block edits that violate a boundary | `toolkit/acme-contributor/hooks/pre-edit-boundary.py` | none (contract.py is the only invariant boundary; manual review enforces) |

## Orchestrator

| | tempo |
|---|---|
| Series runner | manual checklist — no orchestrator; series table in `series-toml-skeleton.md` |
| Single-unit discipline | manual process — read spec section, implement, run gate commands, submit for review |
| Cross-series memory | `reflections.md` — manual lessons from each PR, promoted to next round's checklist |
| Capacity dispatch | manual scoring; all PRs assumed Haiku-tier (small, single-concern, contract-touching) |

*A slot left unbound is a method-not-fully-applied warning. Bind every row before
running a series under the method.*
