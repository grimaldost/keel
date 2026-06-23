# Changelog

All notable changes to keel. Format: Keep a Changelog; versioning: SemVer.

## [0.9.0] - 2026-06-23

### Added

- **The eval-spec DoR profile gains the experimental-design axes** (`definition-of-ready.md`, Part B) plus a
  **measurement-design** pre-mortem directive carried in BOTH `pre-mortem-prompt.md` and the bundled
  `pre-mortem-review` agent (pinned by the `unit of analysis` drift-guard marker): estimand + unit of
  analysis; reps / power & the minimum effect worth detecting (a 1-rep delta is noise — a **power** question,
  distinct from 0.8.0 **feasibility**, which asks whether the record supplies the variable at all); blinding +
  held-constant factors; a correctness oracle distinct from "ran green".
- **The subset-of-phases framing** (`docs/doctrine.md` §3 + `apply-method`): a design / experiment / triage
  round runs a named **subset** of the 8 phases (a Decide+Specify subset), the unused phases named-as-skipped,
  not faked. A measurement/experiment spec is a recognized artifact with its own validity bar.
- **A `disconfirming_test` field** in the pre-mortem output contract (prompt ⊕ agent, pinned by the
  `disconfirming` marker): each predicted failure mode names the cheapest observation that would retire it —
  distinct from `smallest_fix` (prevents the mode) and from stress-test-predictions (attacks the spec's claims).
- `ADR-0009`: keel beyond the multi-PR wave.

### Changed

- The drift guard pins the MARKERS tuple length at 24 (each new marker lands with its count bump in the same
  change). The cross-vendor pre-mortem panel (OpenRouter, gitignored maintainer tooling) joined the release
  pre-mortem for the first time this release, as non-blocking enrichment.

## [0.8.0] - 2026-06-19

### Added

- The pre-mortem grounding directive reaches two steps further, carried **byte-identical** in BOTH
  `pre-mortem-prompt.md` and the bundled `pre-mortem-review` agent, each pinned by a distinctive marker
  in the drift guard: **generated-artifact behavior on the target** (a claim about how a generated
  artifact behaves — generated SQL/DDL, a rendered template, codegen output — is unverified until that
  output is executed or parsed on the real target/dialect; reading the generator's source is a
  hypothesis, flagged unverified-offline by the read-only reviewer), and **feasibility-grounding first**
  (before hardening internal validity, ground the study's headline against the empirical record it needs
  — prior-run data/ledger; a null short-circuits the round). The feasibility axis also lands as a DoR
  Part-B eval-spec item (`definition-of-ready.md`).
- The pre-mortem output contract: the read-only agent **RETURNS** its findings ending with a
  machine-greppable `PREMORTEM-VERDICT: <token>` line, and **the caller folds and records** (the agent
  cannot write) — clarified in the agent, the prompt, and `commands/keel-premortem.md`.
- `ADR-0008`: the grounding directive reaches the generated and the feasible.

### Changed

- The **Cross-PR generated artifacts** directive is sharpened with the **un-deferrable-when-gated**
  clause: when a freshness gate asserts a committed/generated artifact in sync on EVERY change to its
  source, the regenerate-after-the-last-mutating-PR option does not apply — each PR perturbing the
  source regenerates its slice in that same PR.
- `spec-template.md` records the **ledger-is-first-table** convention; doctrine's sharpening 4/5 and
  two-pass notes carry the generated-output and feasibility grounding clauses.
- The drift guard pins the MARKERS tuple length (now 22) so a marker added to the files but dropped
  from the guard (or vice-versa) is caught.

### Fixed

- **A12 fold-ledger parser over-reach (a false positive):** a non-ledger table sharing the
  `### Fold ledger` subsection span was parsed as ledger rows and demanded an `artifact:line`. A12 now
  reads only the **first contiguous table** in that subsection (`_first_table_rows`).
- The **absent-numbered-sections** error now names the `## Numbered sections` parent AND the `### §N`
  child shape (keeping its `no ` prefix so the CLI template pointer still fires); the A6 anchor error
  teaches repo-root-relative paths, and the A5 "to be created" error teaches that the path must also
  appear in the creating section's body.

## [0.7.0] - 2026-06-17

### Added

- The pre-mortem gains four directives, carried **verbatim and byte-identical** in BOTH
  `pre-mortem-prompt.md` and the bundled `pre-mortem-review` agent, each pinned by a distinctive marker
  in the drift guard (`tests/test_premortem_agent.py`): a **rising-bar / convergence** rule (round ≥2 the
  BLOCKER/MAJOR bar rises — a finding blocks only if it plausibly corrupts the decision the spec gates;
  a round of only nice-to-haves is CERTIFY-with-advisories, not another full round); **source-ground
  capability claims** (any reuse/capability/existence claim is verified against the symbol's source or
  tests, not a consumer API doc alone — the claim twin of 0.6.1's fix re-grounding); a first-class
  **SERIES-pass checklist** (base-branch content reality, per-PR gate × contract-test interactions,
  cross-prompt contract drift); and **instrument defeatability** for eval/experiment specs (the cheapest
  way an agent sidesteps the planted difficulty so the run measures nothing).
- A DoR Part-B eval-spec **instrument-defeatability** item (`definition-of-ready.md`), a sibling axis to
  the 0.6.0 ceiling/floor discriminating-power item.
- `ADR-0007`: pre-mortem convergence & grounding.

### Changed

- **B1** now records an operator-accepted **CONDITIONAL-CERTIFY**: the verdict passes when its leading
  token is `CERTIFIED` (unchanged) **or** `CONDITIONAL-CERTIFY` paired with a named `Operator:` field —
  the latter passes with a non-blocking **WARN** (a new `warnings` channel on `GateResult`, printed before
  `OK`), never EXIT=1, so a consciously-accepted "ready modulo a named fix" spec is not blocked forever.
  Widen-only: a bare `CERTIFIED` passes exactly as before with no warning; a `CONDITIONAL-CERTIFY` with no
  Operator still fails. `spec-template.md` gains the `Operator:` Verdict field and `definition-of-ready.md`
  describes the widened B1, so the state is recordable end to end. (closes the doctrine↔gate gap)
- The `check-ready` **structural pointer** now fires on an absent OR **malformed-shape** top-level
  structure (an un-numbered heading, a non-bijection manifest, an empty manifest), not only an absent one —
  while staying quiet on a coverage slip or an A5 path-grounding failure (content, not shape; ADR-0006's
  author-loop-quiet decision preserved). The **A12 fold-ledger** error now teaches the accepted form with a
  concrete `path:line` example.
- `docs/doctrine.md`: sharpening 4 gains the source-grounding clause; the convergence operating note gains
  the rising-bar rule + the operator-accepted conditional verdict; the two-pass cadence note records the
  first-class SERIES checklist.

### Origin

- The 2026-06-17 post-0.6.0/0.6.1 field triage (`docs/feedback/2026-06-17-post-061-field-triage.md`, 3
  reports on keel 0.6.1). Spec: `docs/design/2026-06-17-keel-0.7.0-spec.md`, DoR-certified by a two-pass
  blind pre-mortem (DESIGN + SERIES; 2 MAJOR + 8 MINOR folded across 10 findings, both passes resolving
  CONDITIONAL-CERTIFY → CERTIFIED). B1 widens only; `check-ready` was re-run on the 0.7.0 spec after §2/§5
  landed (the N8e re-dogfood rule).

### Routed out / carried

- → pr-pilot: the program-level convergence budget, the catch-cost telemetry denominator, and the
  orchestrator-constraint SERIES checks (one-sink-per-dataset, base-branch targeting).
- Held at `watch` (single LOW report): the calibration/threshold ceiling-direction eval note (T5b).

## [0.6.1] - 2026-06-15

### Changed

- The pre-mortem **fold step now re-grounds each proposed fix before applying it**: a `smallest_fix`
  is a hypothesis, not an instruction — verify it against the code, since folding a wrong fix verbatim
  ships the bug it named. Carried verbatim in both `pre-mortem-prompt.md` and the bundled
  `pre-mortem-review` agent, pinned by the drift guard (`tests/test_premortem_agent.py`); doctrine
  sharpening 4 gains the clause.

### Origin

- keel-on-keel: the 0.6.0 self-build (`docs/feedback/2026-06-14-keel-0.6.0-self-build.md`) caught a
  DESIGN-pass proposed fix (`certified\b`) with a hyphen-boundary hole that would have shipped the
  `CERTIFIED-NOT`-passes bug if folded verbatim. A sub-threshold refinement (no spec/two-pass
  ceremony, per doctrine §6); extends the verified fold (ADR-0004) and sharpening 5.

## [0.6.0] - 2026-06-14

### Added

- `keel new-spec <path>` — stamps `spec-template.md` as a single-file scaffold (refuses overwrite
  without `--force`), and `check-ready` now appends a one-line pointer to the template when a
  top-level structure is entirely absent (A1/A4/A5) — the on-ramp the field flagged (4 runs to green).
- Pre-mortem **cross-artifact-completeness** directives, carried verbatim in BOTH `pre-mortem-prompt`
  and the bundled `pre-mortem-review` agent: a cross-PR generated-artifact-invalidation bullet (a
  later PR mutates a mirror's source surface → re-run the generator, test the full tree), an
  intent→executable bullet (a test the DESIGN names for the reviewer subset must appear in the
  executable command), and a stress-test-recorded-predictions bullet (a "predicted signal" is a claim
  to attack — could it floor/ceiling?). A DoR Part-B discriminating-power item for eval/experiment
  specs; a `spec-template` release-notes-in-wave Definition-of-Done item; a `doctrine` operating note
  blessing the cross-cutting pre-cut blind audit.
- `ADR-0006`: the adoption surface & cross-artifact completeness.

### Changed

- **A2** matches `acceptance\s+criterion`, so a hard-wrapped `**Acceptance criterion:**` marker is
  found (widen-only; a self-hit in the 0.5.0 build and a field miss).
- **B1** accepts the verdict's leading token (`CERTIFIED` + trailing prose), capturing a hyphenated
  compound whole so `CERTIFIED-NOT` still fails; the error states the bare-token contract (widen-only,
  with a regression test that the hole stays closed).
- `tests/test_premortem_agent.py` rises to distinctive per-directive markers, pinning the new
  directives so the agent ⇄ prompt fidelity invariant holds as the directive set grows.

### Origin

- The 2026-06-14 post-0.5.0 field triage (`docs/feedback/2026-06-14-post-050-field-triage.md`, 5
  reports). Spec: `docs/design/2026-06-14-keel-0.6.0-spec.md`, DoR-certified by a two-pass blind
  pre-mortem (DESIGN + SERIES; 1 BLOCKER + 7 MAJOR + 6 MINOR folded across 14 findings). A2/B1 widen
  only; `check-ready` was re-run on the 0.6.0 spec after they landed (the N8e re-dogfood rule).

### Routed out / carried

- → pr-pilot: the REVIEW-command-vs-design diff + full-tree generated-mirror freshness; the per-wave
  FIRE release-notes line + predicted-vs-invariant tagging; the eval-run cost denominator.
- Carried (no new field evidence this round): R2 program convergence budget, R3 observational ledger,
  R4 cost-intensity dial, R5 DC4-A disk-truth axis.

## [0.5.0] - 2026-06-13

### Added

- `check-ready` Part A gains two checks (extending ADR-0002/0004; each verified *when present*, so
  existing specs do not retro-break):
  - **A11** — a `path:lo-hi` range anchor must close (string/comment-aware) every bracket it opens,
    so a citation cannot silently truncate a collection literal. Single-line `path:line` anchors
    stay A6; both now share an extracted `_resolve_anchor` helper (a behaviour-preserving refactor).
  - **A12** — when a `### Fold ledger` sub-table is present in the certification block, every row's
    `artifact:line` confirmation anchor must resolve (it records the fold against a real line; the
    fold's correctness stays Part B).
  - **R1** — a certification that *claims* a non-trivial fold must carry a `### Fold ledger` with >=1
    resolving row (a deliberate DoR tightening, **not** verify-when-present; a clean certify dozes) —
    closes the DC3 "skip the ledger by omission" hole at the gate (ADR-0005).
- `keel --version`; `check-ready --structure-only` (Part A only, for the author loop).
- `tests/test_premortem_agent.py`: a drift guard holding the bundled `pre-mortem-review` agent and
  `pre-mortem-prompt.md` to a shared contract-marker set (the `agent ⇄ prompt fidelity` invariant).
- `ADR-0005`: the verification spine.

### Changed

- The bundled `pre-mortem-review` agent is rewritten to carry the current contract (structured
  findings, grounding-of-referents, verified fold) — it had drifted back to the 0.2.0 "top 5" prose,
  so the plugin's out-of-box pre-mortem lagged keel's own doctrine.
- `pre-mortem-prompt` gains the DC1/DC2/DC3 directive layer (ground the verification incl. a
  verifier's own script; staged-files × in-place-gates and diff-shape × lint; the per-finding fold
  ledger + class-not-instance scope) and an operational convergence / stopping rule.
- `spec-template` gains anchor-range guidance, a `### Fold ledger` block, a `Reviewed against:` SHA
  field, and removal/retype + counting guidance; `definition-of-ready` documents A11/A12; `doctrine`
  gains sharpening 5 (ground the verification, model the mechanical consumers, verify the
  transformation) plus the two-pass-cadence, convergence, and cost-of-defect notes.

### Origin

- The 2026-06-13 post-0.4.0 field triage (`docs/feedback/2026-06-13-post-040-field-triage.md`, 19
  reports) + a four-lens review distilled the residual misses to three root causes (DC1/DC2/DC3) and
  a keystone agent-drift defect. Spec: `docs/design/2026-06-13-keel-0.5.0-spec.md`, DoR-certified by
  a two-lens blind pre-mortem (4 BLOCKER + 7 MAJOR + 5 MINOR folded). Each new gate ships a
  regression test; `check-ready` was re-run on the 0.5.0 spec after the checks landed (FM-6 re-dogfood).

### Routed out / declined

- → pr-pilot: silent engine-loss + the watchdog, the cost model, scaffold employer-identity defaults.
- Held at `watch`: N6b cardinal-vs-enumeration lint (false-positive risk). Deferred as a standalone
  repo script: N9a publish-readiness sweep (repo tooling, not a method gate — thinness, ADR-0003).

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
