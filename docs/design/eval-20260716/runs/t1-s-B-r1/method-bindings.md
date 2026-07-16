# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports. The
`acme-ledger` column is a worked example (a fictional project) — replace it
with your project.

## Portability slots

| Slot (what it must provide) | `acme-ledger` binding (example) | This project |
|---|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` | `docs/adr/` — `NNNN-slug.md`, stamped from `docs/adr/adr-template.md` |
| **Spec format** — numberable sections, acceptance criteria | committed spec + `docs/llm/TASK_PROMPT_TEMPLATE.md` | `NNNN-slug.md` at the repo root, stamped with `keel new-spec <path>` — root, not a subdirectory, because `check-ready` resolves `path:line` anchors as repo-root-relative against the spec's `.git` root, falling back to the spec file's own parent directory when there is no `.git` (this sandbox has none, per its own operating constraints); a spec anywhere but the root would resolve every anchor against the wrong base |
| **Guardrails + gate commands** — deterministic pass/fail | `docs/llm/GUARDRAILS.md`, `scripts/check_*.py`, `ruff`/`mypy`/`pytest` | `python3 -m unittest discover -s tests -v` (the only gate command established in `AGENTS.md`/`README.md`; this project has no `ruff`/`mypy` config wired in yet, so those are not bound as gates — a future spec section may add them) |
| **Review checklist** — project-specific, blocking | `.pr-pilot/injections/review_checklist.md` (or your orchestrator's equivalent) | `review-checklist.md` (repo root) |
| **Reflection sink** — feeds the next round | a reflections hook → `reflections.jsonl` → your memory store | `reflections.jsonl` (repo root) — appended by hand after each PR/round; triaged with `reflection-triage.md` |

## Upgrade bindings

| Upgrade | What it must provide | `acme-ledger` binding (example / planned) | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `keel check-ready` | `definition-of-ready.md` (repo root) + `./bin/keel check-ready <spec>` (`--structure-only` for the author loop, full form before decompose) |
| **Pre-mortem** | a stateless adversarial pass | keel's bundled `pre-mortem-review` agent / a pre-series hook | `pre-mortem-prompt.md` (repo root), run manually by a fresh reviewer (agent session or human) who did not author the spec — no orchestrator bound, so this is a manual step |
| **Wave budget** | forecast + drift gate | `[budget]` in `series.toml` + post-PR hook | `series-toml-skeleton.md` (repo root) as a manual checklist — no `series.toml` orchestrator is bound in this project, so the `[budget]` block is tracked by hand per wave |
| **Edit-time invariant hook** | block edits that violate a boundary | `plugins/acme-contributor/hooks/pre-edit-boundary.py` | none bound — this project has no edit-time hook mechanism; invariant enforcement relies on the review checklist and the DoD gate until one is added |

## Orchestrator

| | `acme-ledger` | This project |
|---|---|---|
| Series runner | a `series.toml` orchestrator (e.g. pr-pilot) — or the series table as a manual checklist | none bound — `series-toml-skeleton.md` used as a manual checklist |
| Single-unit discipline | a process-discipline pack (e.g. humblepowers) | none bound — AGENTS.md + this method's phases stand in |
| Cross-series memory | a consolidating memory store (journals → distilled guidance) | none bound — `reflections.jsonl` + `reflection-triage.md` stand in as the manual form |
| Capacity dispatch | a task→(model, effort) routing policy (e.g. humblepowers' choosing-models) — otherwise the scorer's tier heuristics | none bound — falls back to the tier heuristics named in `series-toml-skeleton.md` |

*A slot left unbound is a method-not-fully-applied warning. Bind every row before
running a series under the method.*

## Notes for this project (tempo)

- This is a first application of the method to `tempo`; no prior spec or ADR existed before
  this round (the source-host-field refactor spec is `0001-source-host-field.md` at the repo
  root, and its supporting decision is `docs/adr/0001-source-host-field.md`).
- Several upgrade/orchestrator rows are intentionally unbound (no `series.toml` runner, no
  edit-time hook, no capacity-dispatch policy): the doctrine is explicit that a missing binding
  degrades the method to a manual checklist at that scope rather than blocking it. The DoR/DoD
  gates and the pre-mortem — the load-bearing slots for this refactor — are bound and concrete.
