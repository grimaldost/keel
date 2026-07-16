# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports.

## Portability slots

| Slot (what it must provide) | This project |
|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` |
| **Spec format** — numberable sections, acceptance criteria | committed spec (per `spec-template.md`) with numbered sections §1, §2, etc. |
| **Guardrails + gate commands** — deterministic pass/fail | `python3 -m unittest discover -s tests -v`, `python3 -m py_compile src/tempo/*.py` |
| **Review checklist** — project-specific, blocking | `review-checklist.md` (this file) |
| **Reflection sink** — feeds the next round | `reflections.md` (per-wave reflection log) |

## Upgrade bindings

| Upgrade | What it must provide | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `keel check-ready` |
| **Pre-mortem** | a stateless adversarial pass | `<KEEL-CLI> read pre-mortem` prompt + fresh-context reviewer |
| **Wave budget** | forecast + drift gate | manual tracking in this spec (no automated orchestrator) |
| **Edit-time invariant hook** | block edits that violate a boundary | none (no pre-edit hook implemented) |

## Orchestrator

| | This project |
|---|---|
| Series runner | manual series table (no pr-pilot orchestrator) |
| Single-unit discipline | fresh-context agent per PR, reading its spec section |
| Cross-series memory | `reflections.md` consolidated across waves |
| Capacity dispatch | no per-PR tier routing; all PRs assumed same effort tier |

*All slots are bound. No gaps in method application for this initial wave.*
