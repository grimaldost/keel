# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports. The
`acme-ledger` column is a worked example (a fictional project) — replaced below
with tempo's own binding.

## Portability slots

| Slot (what it must provide) | `acme-ledger` binding (example) | This project |
|---|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` | `docs/adr/` (this repo; `docs/adr/0001-source-host-additive-expand-contract.md` is the first entry) |
| **Spec format** — numberable sections, acceptance criteria | committed spec + `docs/llm/TASK_PROMPT_TEMPLATE.md` | `spec-<date>-<slug>.md` at the repository root, stamped via `<KEEL-CLI> new-spec spec-<date>-<slug>.md`. Root, not `docs/specs/`: this project has no `.git` yet, and `check_ready.py`'s `_resolve_base` resolves a spec's `path:line` anchors against the nearest `.git` ancestor, falling back to the spec's OWN parent directory when none exists — nesting the spec under `docs/specs/` would silently rebase every anchor to `docs/specs/` instead of the repo root. Once this project is under git, specs may move to `docs/specs/` without touching this row (the git-root walk-up makes the nesting irrelevant then). |
| **Guardrails + gate commands** — deterministic pass/fail | `docs/llm/GUARDRAILS.md`, `scripts/check_*.py`, `ruff`/`mypy`/`pytest` | `python3 -m unittest discover -s tests` (per `AGENTS.md` / `README.md`) — the only gate command this project currently has; no `ruff`/`mypy`/lint config exists yet, so a spec's "Gate commands" section names this one command precisely rather than implying a broader suite |
| **Review checklist** — project-specific, blocking | `.pr-pilot/injections/review_checklist.md` (or your orchestrator's equivalent) | `docs/method/review-checklist.md` (copied by `keel init`; no orchestrator installed, so it is applied manually by whoever reviews each PR) |
| **Reflection sink** — feeds the next round | a reflections hook → `reflections.jsonl` → your memory store | `docs/method/reflection-triage.md`, run manually at the end of each wave (no `reflections.jsonl` hook wired yet — reflections are collected by hand from PR review notes) |

## Upgrade bindings

| Upgrade | What it must provide | `acme-ledger` binding (example / planned) | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `keel check-ready` | `docs/method/definition-of-ready.md` + `<KEEL-CLI> check-ready spec-<date>-<slug>.md` (Part A, `--structure-only` in the author loop before a pre-mortem is recorded); Part B is a blind pre-mortem run by a reviewer who did not author the spec, using `docs/method/pre-mortem-prompt.md`, then `<KEEL-CLI> check-ready spec-<date>-<slug>.md` (no flag) to confirm both halves |
| **Pre-mortem** | a stateless adversarial pass | keel's bundled `pre-mortem-review` agent / a pre-series hook | a fresh, non-author reviewer (human or a separately-launched agent with no prior context on this spec) running `docs/method/pre-mortem-prompt.md`; no orchestrator hook installed, so this is a manual pre-series step |
| **Wave budget** | forecast + drift gate | `[budget]` in `series.toml` + post-PR hook | not yet bound — no `series.toml` orchestrator is installed in this project; `docs/method/series-toml-skeleton.md` serves as the wave's manual PR checklist (id/section/tier per PR) until an orchestrator is adopted |
| **Edit-time invariant hook** | block edits that violate a boundary | `toolkit/acme-contributor/hooks/pre-edit-boundary.py` | not yet bound — no edit-time hook exists in this project; the contract invariant (record tuple shape, `docs/adr/0001-source-host-additive-expand-contract.md`) is enforced only by review + the DoD test gate until a hook is written |

## Orchestrator

| | `acme-ledger` | This project |
|---|---|---|
| Series runner | a `series.toml` orchestrator (e.g. pr-pilot) — or the series table as a manual checklist | none installed — the PR ↔ section manifest in each spec plus `docs/method/series-toml-skeleton.md` is the manual checklist |
| Single-unit discipline | a process-discipline pack (e.g. humblepowers) | none installed — TDD-per-PR discipline is applied by convention (`AGENTS.md`, this file) |
| Cross-series memory | a consolidating memory store (journals → distilled guidance) | none installed — `docs/method/reflection-triage.md` output is kept in `docs/adr/` / this file until a memory store exists |
| Capacity dispatch | a task→(model, effort) routing policy (e.g. humblepowers' choosing-models) — otherwise the scorer's tier heuristics | none installed — falls back to the scorer's own tier heuristics named in `docs/method/series-toml-skeleton.md` |

*A slot left unbound is a method-not-fully-applied warning, not a broken method — each
degrades to a manual checklist at that scope (doctrine §5). The wave budget and
edit-time-hook upgrades, and the orchestrator row, are explicitly unbound in this
project today; everything else above is bound.*
