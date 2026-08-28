# Method bindings — keel (keel-on-keel)

keel applies its own method to itself; this sheet binds each slot to the concrete mechanism this
repository actually uses. It is also the worked example the kit's `method-bindings.md` template
asks every consumer to fill — a real one, not the fictional `acme-ledger`.

## Portability slots

| Slot (what it must provide) | keel's binding |
|---|---|
| **ADR home** — a numbered decision log | `docs/adr/` (ADR-0001…, one file per decision) |
| **Spec format** — numberable sections, acceptance criteria | `docs/design/<date>-<name>-spec.md` from `spec-template.md`. Honest note: `docs/design/` is maintainer-local and not published (ADR-0012) — the public record of each round is the CHANGELOG entry, the ADRs, and the tests it lands |
| **Guardrails + gate commands** — deterministic pass/fail | `uv run ruff format --check .` · `uv run ruff check .` · `uv run ty check src` · `uv run pytest`, run unpiped (CONTRIBUTING.md; CI runs these plus `uv lock --check` for the committed lock). The first three also run at commit time via `.githooks/pre-commit` (`git config core.hooksPath .githooks`) |
| **Review checklist** — blocking | the starter `src/keel/templates/review-checklist.md`, applied as-is |
| **Reflection sink** — feeds the next round | `docs/feedback/` (maintainer-local, ADR-0012) + `src/keel/templates/reflection-triage.md`; triage docs open `# Triage —` |

## Upgrade bindings

| Upgrade | keel's binding |
|---|---|
| **DoR gate** | `keel check-ready` on the release spec (Part A in the author loop via `--structure-only`, full gate before decompose) |
| **Pre-mortem** | the bundled `pre-mortem-review` agent, blind, arc sized per the doctrine's round economy; artifact saved as `<spec-stem>.premortem.md` (B2) |
| **Wave budget** | not bound — release waves run in-session (manual-checklist mode); no engine, no per-PR cost table |
| **Edit-time invariant hook** | not bound — no `hooks/` directory ships at all (the empty `hooks.json` placeholder was deleted; it claimed a machine it never had). The suite's arrangement and version-consistency tests hold these invariants at gate time instead |

## Invoking the kit

| | keel |
|---|---|
| Gate command | `uv run keel <command>` from the repo root — keel develops against its own tree, so there is no cache path to pin and no bundle to resolve. Where a policy blocks the console script, `uv run python -m keel <command>` is the same entry point without the shim. |

## Orchestrator

| | keel |
|---|---|
| Series runner | in-session manual-checklist mode: one commit per spec section, all four gates after each |
| Single-unit discipline | red→green per section (a failing test precedes each gate-behavior change) |
| Cross-series memory | `docs/feedback/` reports → periodic triage → promotions into templates/gates/ADRs (CONTRIBUTING.md's loop) |
| Capacity dispatch | not bound — release waves run in-session at one tier; no per-PR routing |

*Three slots are consciously unbound (wave budget, edit-time hook, capacity dispatch) — named,
not faked, per the subset-of-phases doctrine.*
