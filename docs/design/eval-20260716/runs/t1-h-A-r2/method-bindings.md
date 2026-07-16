# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports.

## Portability slots

| Slot (what it must provide) | This project |
|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` (to be created; use `adr-template.md`) |
| **Spec format** — numberable sections, acceptance criteria | `docs/specs/` with spec-template.md format; committed spec file per wave |
| **Guardrails + gate commands** — deterministic pass/fail | `python3 -m unittest discover -s tests` (primary); ruff/mypy if added to project |
| **Review checklist** — project-specific, blocking | `review-checklist.md` (in project root) |
| **Reflection sink** — feeds the next round | `reflection-triage.md` (in project root) — entries consolidated for next round |

## Upgrade bindings

| Upgrade | What it must provide | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `./bin/keel check-ready <spec-file>` |
| **Pre-mortem** | a stateless adversarial pass | `pre-mortem-prompt.md` + agent review before DoR certification |
| **Wave budget** | forecast + drift gate | `series-toml-skeleton.md` filled per wave (manual checklist, no orchestrator) |
| **Edit-time invariant hook** | block edits that violate a boundary | deferred (would be git pre-commit hook); spec violations caught in review |

## Orchestrator

| Component | This project |
|---|---|
| Series runner | manual checklist; `series.toml` optional (no pr-pilot automation) |
| Single-unit discipline | spec-driven per-PR prompts; read spec section fresh per PR |
| Cross-series memory | `reflection-triage.md` promotes recurring lessons to next round's review-checklist.md |
| Capacity dispatch | tier scoring heuristics (manual, per PR author judgment) |

**Status:** All five slots bound. Upgrades 1–3 fully bound; upgrade 4 (edit-time hook) deferred to review phase (catch in gates + checklist). Ready to apply the method.
