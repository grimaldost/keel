# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports.

## Portability slots

| Slot (what it must provide) | This project |
|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` |
| **Spec format** — numberable sections, acceptance criteria | `spec-template.md` (committed spec with numbered §) |
| **Guardrails + gate commands** — deterministic pass/fail | `python3 -m unittest discover -s tests`, `ruff check .`, `ruff format --check .` |
| **Review checklist** — project-specific, blocking | `review-checklist.md` |
| **Reflection sink** — feeds the next round | `reflection-triage.md` (manual checklist; no automated hook) |

## Upgrade bindings

| Upgrade | This project |
|---|---|
| **DoR gate** | `definition-of-ready.md` + `./bin/keel check-ready <spec>` |
| **Pre-mortem** | `pre-mortem-prompt.md` — run in a fresh context, save output as `<spec>.premortem.md` |
| **Wave budget** | `series-toml-skeleton.md` (manual tracking, no drift gate) |
| **Edit-time invariant hook** | none (method not yet fully applied at this scope) |

## Orchestrator

| | tempo |
|---|---|
| Series runner | manual PR checklist (series table as a manual checklist; no pr-pilot integration) |
| Single-unit discipline | this AGENTS.md + spec format |
| Cross-series memory | none (first round; no memory store yet) |
| Capacity dispatch | default keel tier heuristics (no custom routing policy) |

**Unbound slots:** edit-time invariant hook, cross-series memory, orchestrator runner (pr-pilot), capacity dispatch policy.
These are method-not-fully-applied warnings — the core discipline (DoR gate + pre-mortem) is in place.
