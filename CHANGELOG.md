# Changelog

All notable changes to keel. Format: Keep a Changelog; versioning: SemVer.

## [0.4.0] - 2026-06-09

### Added

- `check-ready` Part A gains three checks (extending ADR-0002; each verified *when present*,
  never required, so existing specs do not retro-break):
  - **A8** — every bare intra-spec `§N` reference resolves to a numbered section; skips
    sub-decimal `§N.M`, `###` heading lines, and doc-cued refs ("doctrine §6"). The `§` glyph
    is reserved for a spec's own sections (§3).
  - **A9** — every `**Model-on:**` / `**Reuse:**` reference resolves: the path exists and, for
    `path::symbol`, the symbol is a top-level def/class/assignment or `__all__` entry (§2).
  - **A10** — when a spec carries an Enforcement-status table, no prose may claim an invariant
    "enforced"/"guaranteed" while its row is review-only/planned/absent (§4).
- `spec-template` gains the `**Model-on:**`/`**Reuse:**` notation, an Enforcement-status table,
  and a `Post-fold coherence:` certification field.
- `ADR-0004`: structured pre-mortem findings & the verified fold.

### Changed

- `pre-mortem-prompt` emits a structured findings list (`id`/`severity`/`evidence`/
  `smallest_fix`/`target_section`), folds from it mechanically, then runs a post-fold coherence
  re-read + a fold-consistency rule; the "top 5" cap is lifted to all BLOCKER/MAJOR + notable
  MINOR; grounding-of-referents directives added (§1).
- `definition-of-ready` documents A8/A9/A10, the two conventions, and the post-fold step;
  `doctrine` gains a "ground referents, verify the fold" sharpening (§5).

### Origin

- The 2026-06-09 backlog triage (`docs/feedback/2026-06-09-backlog-triage.md`) — the "spine"
  slice (clusters T1, T4, T5, T8d). Spec: `docs/design/2026-06-09-keel-0.4.0-spec.md`, DoR-
  certified by a blind pre-mortem (3 BLOCKER + 3 MAJOR + 2 MINOR folded). Each new gate ships a
  regression test in `tests/test_check_ready.py`; the dogfood (`check-ready` on the 0.4.0 spec)
  was re-run after the checks landed and stays green.

## [0.3.0] - 2026-06-06

### Added

- `check-ready` code-grounds a spec's claims: backticked `path:line` anchors must resolve
  (file + line exist) and any quoted snippet must match the file (§1); a cited
  `docs/adr/NNNN-slug.md` must use a number free on the base or naming that exact ADR (§2).
- `spec-template` gains an explicit "Gate commands" field and an anchor / next-free-ADR
  convention (§2).
- `ADR-0003`: keel thinness & consumer-agnosticism — feedback flows up, residue is declined
  not tracked, doctrine names roles with tools as reference bindings, `budget_drift`/`bindings`
  stay deferred with their stubs + contract intact (§7).
- A validation-experiment design (`docs/design/2026-06-06-keel-validation-experiment.md`) for
  the still-pending controlled test (§5).

### Changed

- Doctrine §6 "when to use" is now a countable, blast-radius-keyed trigger (≥5 PRs, a
  ≥~50-dependent chokepoint, additive-on-a-shared-contract, a boundary crossing, or a
  >1-quarter lifetime), not the vague "large, cohesive, long-lived" (§3).
- Gate-integrity standard: a tool-wrapping gate must assert the tool ran to completion, not
  just error-count ≤ baseline; DoD + review-checklist + CONTRIBUTING carry it, with the
  gate-decay / ships-a-test / fail-closed-triage conventions (§4).
- Doctrine §1 value claim recalibrated to "validated on three governed waves; controlled
  experiment pending" (§5); a third sharpening records feedback-flows-up + method/engine
  separate ledgers (§6); doctrine §4 + concepts read role-first (§7).

### Origin

- The 2026-06-05 review-panel triage (Clusters 2–5) + the 2026-06-06 field-feedback waves
  from a production consumer (triage findings F1–F5). Spec DoR-certified by a blind
  pre-mortem (development history kept local).

### Notes

- `bind-check` and `budget-drift` remain stubs (ADR-0003 defers them; contract intact).

## [0.2.1] - 2026-06-05

### Fixed

- `/keel-check-ready` invoked `uvx --from . keel`, which assumed the shell was inside
  the keel repo and broke when run from another project; it now calls the installed
  `keel check-ready` CLI directly — the plugin works cross-project.
- `apply-method` skill listed only 6 of the 10 templates `keel init` copies; it now
  describes the full kit.
- `pyproject.toml` bounds the `uv_build` backend (`>=0.5,<0.12`), silencing the
  unbounded-requirement build warning (note: current `uv-build` is 0.11.x, so the
  bound is `<0.12`, not the `<0.11` the warning suggested).

## [0.2.0] - 2026-06-05

### Added

- `keel check-ready`: the Definition-of-Ready gate is now real (`check_spec_ready`).
  Part A asserts well-formedness — numbered sections; non-trivial acceptance criteria;
  no `TBD`/`TODO`/`FIXME`/`???`; a PR↔section bijection with full coverage;
  concept→module paths that exist or are "to be created" and claimed by a section.
  Part B (B1) requires a recorded blind pre-mortem certification, so the gate never
  passes on structure alone.
- `ADR-0002`: DoR gates well-formedness, not correctness; correctness is externalized
  to a required, non-author pre-mortem certification (a `## Pre-mortem certification`
  block, now in `spec-template.md`).

### Changed

- `definition-of-ready.md`: Part B reworded from "a reader signs" to "a fresh,
  non-author reviewer certifies, with evidence"; the pre-mortem promoted Recommended →
  required; the "symmetric to the Definition of Done" framing dropped.
- `pre-mortem-prompt.md` now writes the certification block and is required;
  `doctrine.md` §7 updated to match.
- `cli`: `check-ready` maps a missing spec to exit 2 (not runnable), distinct from
  exit 1 (violations); stdout/stderr are forced to UTF-8 so non-ASCII violation
  labels (→, ↔) print on a legacy cp1252 console instead of crashing.

### Origin

- Cluster 1 of the 2026-06-05 design review-panel triage
  (`docs/feedback/2026-06-05-review-panel-triage.md`). Clusters 2–5 remain queued.

### Notes

- `bind-check` and `budget-drift` remain stubs (interface pinned by contract tests).

## [0.1.0] - 2026-06-05

### Added

- Initial scaffold: repo-that-is-a-plugin-with-engine (mirrors pr-pilot).
- `keel` CLI: `check-ready`, `bind-check`, `budget-drift` (stubbed) and `init` (real).
- Claude Code plugin: `apply-method` skill, `/keel-*` commands, `pre-mortem-review` agent, template kit.
- Doctrine + docs ladder; ADR log (ADR-0001); feedback intake; CONTRIBUTING.

### Notes

- Gate algorithms are stubbed (interface pinned by contract tests); logic lands in a later
  release via the feedback → triage → release loop.
