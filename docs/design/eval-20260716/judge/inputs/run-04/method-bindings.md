# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports. The
`acme-ledger` column is a worked example (a fictional project) — replace it
with your project.

## Portability slots

| Slot (what it must provide) | `acme-ledger` binding (example) | This project |
|---|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` | `docs/adr/` — `docs/adr/NNNN-slug.md`, numbered sequentially, using `adr-template.md` |
| **Spec format** — numberable sections, acceptance criteria | committed spec + `docs/llm/TASK_PROMPT_TEMPLATE.md` | project root, `*.spec.md` — one committed spec per round, scaffolded from `spec-template.md` via `keel new-spec`. Kept at the repo root (not `docs/specs/`) because `check-ready`'s anchor resolution falls back to the spec file's own parent directory when no `.git` is present (`_resolve_base` in keel's `check_ready.py`), and this project has no `.git`; a spec nested under `docs/` would break every `path:line` anchor. |
| **Guardrails + gate commands** — deterministic pass/fail | `docs/llm/GUARDRAILS.md`, `scripts/check_*.py`, `ruff`/`mypy`/`pytest` | `python3 -m unittest discover -s tests -v` (the project's only configured gate — no `ruff`/`mypy` config exists in this repo; do not claim them until they are added) |
| **Review checklist** — project-specific, blocking | `.pr-pilot/injections/review_checklist.md` (or your orchestrator's equivalent) | `review-checklist.md` (project root) — generic items + a `tempo`-specific section |
| **Reflection sink** — feeds the next round | a reflections hook → `reflections.jsonl` → your memory store | `reflections.jsonl` (project root, created on first reflection) → swept by `reflection-triage.md` |

## Upgrade bindings

| Upgrade | What it must provide | `acme-ledger` binding (example / planned) | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `keel check-ready` | `definition-of-ready.md` (project root) + `<KEEL-CLI> check-ready <path>` |
| **Pre-mortem** | a stateless adversarial pass | keel's bundled `pre-mortem-review` agent / a pre-series hook | a fresh subagent (no access to this session's context) given `<KEEL-CLI> show pre-mortem`, run manually per round — no orchestrator hook is wired |
| **Wave budget** | forecast + drift gate | `[budget]` in `series.toml` + post-PR hook | `series.toml` (per series, from `series-toml-skeleton.md`) + `<KEEL-CLI> budget-drift` run manually after each PR (no post-PR hook wired) |
| **Edit-time invariant hook** | block edits that violate a boundary | `toolkit/acme-contributor/hooks/pre-edit-boundary.py` | none — not wired in this project; boundary discipline is manual/review-only until one is added |

## Orchestrator

| | `acme-ledger` | This project |
|---|---|---|
| Series runner | a `series.toml` orchestrator (e.g. pr-pilot) — or the series table as a manual checklist | none — `series.toml` used as a manual checklist |
| Single-unit discipline | a process-discipline pack (e.g. humblepowers) | none — manual brainstorm → plan → TDD → review per PR |
| Cross-series memory | a consolidating memory store (journals → distilled guidance) | none — `reflections.jsonl` + `reflection-triage.md` only, no consolidating store yet |
| Capacity dispatch | a task→(model, effort) routing policy (e.g. humblepowers' choosing-models) — otherwise the scorer's tier heuristics | none — falls back to the scorer's own tier heuristics named in `series-toml-skeleton.md` |

*A slot left unbound is a method-not-fully-applied warning. Bind every row before
running a series under the method.*

## Notes on unbound rows (honest gaps, not filled to look complete)

This is a small, two-module toolkit (`src/tempo/`) with a single `unittest`-based test
suite and no linter, type-checker, orchestrator, or edit-time hook configured anywhere
in the repo. Several rows above are bound to "none" / "manual" rather than to a tool
that isn't actually present — inventing a `ruff`/`mypy` binding or a hook that doesn't
exist would violate the method's own grounding principle (doctrine sharpening 4). The
series runner, single-unit discipline, and cross-series memory rows stay manual
checklists per the doctrine's "each role works standalone" composition note (§5); if
this project later adopts real tooling for any of them, update this file to match.
