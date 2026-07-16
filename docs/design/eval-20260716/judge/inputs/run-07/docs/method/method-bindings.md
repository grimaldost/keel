# Method bindings — tempo

The method is project-agnostic; this file binds each slot and upgrade to a
concrete mechanism in THIS project. Filling it is how the method ports. The
`acme-ledger` column is a worked example (a fictional project) — replaced here
with tempo's own mechanisms.

## Portability slots

| Slot (what it must provide) | `acme-ledger` binding (example) | This project |
|---|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` | `docs/adr/` (this round: `docs/adr/0001-source-host-field.md`) |
| **Spec format** — numberable sections, acceptance criteria | committed spec + `docs/llm/TASK_PROMPT_TEMPLATE.md` | committed spec at the project root (e.g. `0001-source-host-field.md`), stamped from `docs/method/spec-template.md` — kept at the root rather than under `docs/specs/` because this project has no `.git`: `keel check-ready`'s anchor resolver (`_resolve_base`) walks up from the spec for a `.git` directory and, finding none, falls back to the spec's own parent directory as the repo-root it resolves `path:line` anchors and the concept→module map against; a spec nested under `docs/specs/` would resolve `src/tempo/...` anchors against `docs/specs/src/tempo/...` and fail every one. This is a real gap, not a style choice — see the note below. |
| **Guardrails + gate commands** — deterministic pass/fail | `docs/llm/GUARDRAILS.md`, `scripts/check_*.py`, `ruff`/`mypy`/`pytest` | `python3 -m unittest discover -s tests` (per `AGENTS.md`/`README.md`) — this project has no ruff/mypy config; the test suite is the only deterministic gate that exists today |
| **Review checklist** — project-specific, blocking | `.pr-pilot/injections/review_checklist.md` (or your orchestrator's equivalent) | `docs/method/review-checklist.md`, applied manually (no orchestrator injection wired) |
| **Reflection sink** — feeds the next round | a reflections hook → `reflections.jsonl` → your memory store | `docs/method/reflections.jsonl` (created on first reflection; no automated hook — appended manually per round) |

## Upgrade bindings

| Upgrade | What it must provide | `acme-ledger` binding (example / planned) | This project |
|---|---|---|---|
| **DoR gate** | spec-readiness check before decompose | `definition-of-ready.md` + `keel check-ready` | `docs/method/definition-of-ready.md` + `<KEEL-CLI> check-ready <spec>` (Part A: `--structure-only`; Part B requires a certified, non-author pre-mortem before the full gate passes) |
| **Pre-mortem** | a stateless adversarial pass | keel's bundled `pre-mortem-review` agent / a pre-series hook | manual pass using `docs/method/pre-mortem-prompt.md`, run by a fresh reviewer who did not author the spec (no bundled pre-mortem agent installed in this project) — output saved as `<spec-stem>.premortem.md` alongside the spec at the project root |
| **Wave budget** | forecast + drift gate | `[budget]` in `series.toml` + post-PR hook | not yet applicable — this round covers Decide + Specify + Decompose only (the PR↔section manifest is filled in the spec); Route & Budget is the next phase, deferred to the execution wave. A `series.toml` with a `[budget]` block per `docs/method/series-toml-skeleton.md` is created then, translating PR01-PR06 and their tiers |
| **Edit-time invariant hook** | block edits that violate a boundary | `toolkit/acme-contributor/hooks/pre-edit-boundary.py` | absent — no hook infrastructure exists in this project; invariant enforcement is review-only until one is built (tracked honestly, not fabricated) |

## Orchestrator

| | This project |
|---|---|
| Series runner | none installed — the series/PR manifest in the spec serves as a manual checklist |
| Single-unit discipline | none installed — this `AGENTS.md` + the keel templates are the whole discipline pack |
| Cross-series memory | none installed — `docs/method/reflections.jsonl` is the only durable record until one is bound |
| Capacity dispatch | none installed — PR tiers in `series-toml-skeleton.md` are chosen by hand at Decompose time |

*A slot left unbound is a method-not-fully-applied warning. This project has three
slots bound to "manual"/"absent" rather than a mechanism — that is an honest
gap, not a fabricated tool, and is itself a candidate reflection for a future round.
Bind every row before running a series under the method; the current round
(Decide + Specify + Decompose, per the spec header) does not require
Route/Implement/Gate/Review/Reflect bindings to be resolved yet.*

## Known gap: no `.git` in this project

`keel check-ready` resolves every `path:line` anchor, the concept→module map, and ADR
citations against a "repo root" it finds by walking up from the spec for a `.git`
directory; absent one, it falls back to the spec's own parent directory
(`check_ready.py:_resolve_base`). This project has no `.git`, so specs authored under
this binding must live at the project root (not `docs/specs/`) for anchors to resolve —
confirmed empirically: the spec at `docs/specs/0001-source-host-field.md` failed every
`src/tempo/...` anchor until moved to `0001-source-host-field.md` at the root. If this
project is ever placed under version control, specs can move back under `docs/specs/`
without any other change. Until then, this binding is the honest workaround, not a
long-term home for specs.
