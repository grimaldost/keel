# Changelog

All notable changes to keel. Format: Keep a Changelog; versioning: SemVer.

## [0.14.0] - 2026-08-11

The backlog-wave-1 release: nine items from the 2026-08-11 improvement backlog
(`docs/backlog.md`), driven by the feedback-triage and feature-review pass. One structural
change (the pre-mortem directives folded to a single home, ADR-0017), three gate wideners
(spec kinds, the shared field parser, reviewer-form anchors), and the release loop itself
machine-enforced. Design register: ADR-0017.

### Added

- **A declared spec kind sizes the Part-A structural trio** (KEEL-B01, `check_ready.py`):
  `Kind: series | single-change`. A `single-change` spec may omit the trio sections
  (absence-ok, presence still fully checked) with the ≥5-word acceptance floor moved to
  document scope as the compensating control; an unknown kind fails naming the token, and
  each relaxed absence names the exact heading plus the relaxing declaration.
- **Reviewer-form anchor resolution** (KEEL-B04, `check_ready.py`): A12 accepts the anchor
  form keel's own pre-mortem reviewer emits, resolving a unique basename with a WARN (W3)
  that names the expansion; line range and snippet are still verified against the resolved
  file, and ambiguity fails naming the candidates.
- **Body budgets** (KEEL-B06, `CONTRIBUTING.md`, `tests/test_body_budgets.py`): explicit
  word caps for the three bodies that only grow, with a test asserting the doc and the
  suite carry the same numbers.
- **The release loop, machine-enforced** (KEEL-B08, `scripts/changelog_currency.py`,
  `tests/test_release_flow.py`, CI `changelog-currency` job): a PR that touches a
  shipped-kit path with `CHANGELOG.md` unchanged fails, and every released version carries
  its `vX.Y.Z` tag (0.11.1–0.13.1 tagged retroactively).
- **The pre-commit hook, installed in the form this environment runs** (KEEL-B05,
  `.githooks/pre-commit`): `core.hooksPath` invoking `uv run python -m pre_commit`,
  covering ruff, ruff-format and `ty check src`; pytest stays CI's, and CONTRIBUTING now
  carries an enforcement-status table stating which gates run where.

### Changed

- **One home for the pre-mortem directives** (KEEL-B02, ADR-0017):
  `src/keel/templates/pre-mortem-prompt.md` is the single source;
  `agents/pre-mortem-review.md` is a thin identity + dispatch + output-contract wrapper
  that reads the template at run start (named fallback, announced when unreachable). Total
  pre-mortem surface 4,768 → 3,111 words; the 34-marker drift guard is replaced by tests
  that pin the arrangement.
- **One field parser for Part A** (KEEL-B03, `check_ready.py`): `_first_path_token` is the
  single home for path-valued fields (a `Certification artifact:` cell no longer eats
  trailing prose); A12 names the cell it read; the column-break diagnostic runs ahead of
  the anchor search; A8 skips a References section.

### Removed

- **The empty hooks placeholder** (KEEL-B29, `hooks/hooks.json`): deleted by inspection —
  the declaration was empty and the manifest test now asserts the inverse invariant (a
  `hooks.json` that exists must declare a real hook).

## [0.13.1] - 2026-07-15

Capacity-dispatch vocabulary: the Route & Budget map names the role that owns task→model
routing, and the series skeleton's tiers are labelled in keel's own vocabulary so a reader
cannot read them as another tool's tier words. Docs and templates only — no gate, CLI, or
schema change.

### Added

- **The capacity-dispatch role in the Route & Budget map** (`docs/doctrine.md`,
  `docs/method-bindings.md`, `src/keel/templates/method-bindings.md`): the map now names the
  role that owns task→(model, effort) routing, so a series author binds it explicitly instead
  of leaving the slot implicit. Guarded by `tests/test_doctrine_bindings_currency.py`.

### Changed

- **The series skeleton labels its tiers as model-family names**
  (`src/keel/templates/series-toml-skeleton.md`, `docs/templates-reference.md`): the
  skeleton's tier pins were already family names (`haiku` / `sonnet`) — keel's own
  vocabulary, not another tool's `weak`/`mid`/`strong` — and the label now says so, so a
  reader porting a series between tools does not translate the wrong way. Guarded by
  `tests/test_templates_valid.py`.

## [0.13.0] - 2026-07-10

The field-hardening release: five recurring field gaps moved to their enforcing layer (ADR-0016),
and the headline comparative claim retired at ADR-0013's run-or-retire deadline (ADR-0015). Design
registers: ADR-0015, ADR-0016.

### Added

- **The shared text-segmentation layer** (`check_ready.py`, §1): `_mask_inline_spans` (a prose view
  that space-fills inline-code spans, wrapped-across-a-line-break included) and `_split_cells` (a
  backtick- and `\|`-aware table-row splitter) replace five divergent per-check masking idioms. A3's
  angle idiom and A8's `§N` detection read the prose view; both table parsers read `_split_cells`.
- **A CHANGELOG heading-chain test** (`tests/test_plugin_manifest.py`, §2): shape (no
  `## [Unreleased]`; releases cut directly), strict descending SemVer by parsed integer tuple, and —
  the layer that bites the 0.12.0 F1 defect — no `### kind` repeating inside one release section.
- **The operator close** (`definition-of-ready.md` Part B, §4): the sanctioned discharge of an
  operator-accepted CONDITIONAL-CERTIFY — the verdict stays CONDITIONAL-CERTIFY + named Operator + a
  discharge note; the B1 WARN and (when a discharge edits the spec body) B2's earlier-revision WARN
  are the expected honest state, never silenced by recomputing the hash; a confirm re-gate is
  optional per the round economy. B2's hash-mismatch WARN gains an operator-close pointer on that path.
- **A `consumed_input` findings-schema field** (prompt ⊕ agent, drift markers 33 → 34, §6): a
  predicted cross-artifact coupling names the concrete input the dependent consumes, or downgrades to
  a hypothesis with a disconfirming test rather than an asserted MUST.
- **A VCS-tracking Definition-of-Done line** (§7): every ADR/spec-referenced durable artifact is
  `git ls-files`-tracked, so a stray ignore rule cannot drop a referenced file from the merge.

### Changed

- **Part-A behaviour flips at syntax edges the fence doctrine could not reach** (§1): an angle
  placeholder inside a line-wrapped inline-code span no longer false-fires A3; a backticked `§N`
  glyph mention no longer fires A8; a slash- or en-dash-joined section range keeps its doc cue (A8) —
  with a named lenient direction (an intra-spec dangler immediately after a comma/dash-joined
  cross-doc run reads as part of the range); a fold-ledger, manifest, or concept cell carrying a
  backticked pipe parses correctly (A12/A4/A5); a genuinely bare pipe in a ledger cell now names the
  column break. A backticked legacy token (`` `TODO` ``) still fires, per the fence-only doctrine.
- **The A6 anchor-snippet mismatch message states its parse** (§3) — it read the backticked token
  after the anchor as a snippet; a guard test keeps the spec-template free of gate-parseable anchors.
- **`reflection-triage.md` lands and sweeps** (§5): a sweep-the-sink first step (open rows of every
  prior triage doc are input) and a two-branch "land" terminal step (apply in-context, or hand off to
  the method's feedback intake), with a row-closure rule and the CHANGELOG-owner disambiguation.
- **`apply-method` reads the project's bindings first** (§8); `keel init` runs only when the kit is
  absent.
- **The spec-template states the anchor authoring contract** (§9): repo-root-relative form, the
  adjacency rule, the claim-anchor snippet rider, and the A5 body-claim requirement — pinned by needles.
- **Release-flow guards** (§10): CONTRIBUTING + AGENTS record that gates run unpiped and that the
  release pre-mortem states whether the cross-vendor panel ran; CI gains `uv lock --check` for the
  eighth version site (`uv.lock`). The version-consistency test reads seven text sites; the release
  bumps eight (uv.lock via `uv lock`).
- **The comparative claim is retired, unmeasured** (ADR-0015, §12): doctrine §1, `docs/evidence.md`,
  and `docs/concepts.md` drop the "pending" qualifier; README's wager line points at `docs/evidence.md`;
  the fathom instrument evidence is cited by its public repository; the priced reopening path is
  recorded (maintainer-local, no date). `tests/test_claim_currency.py` pins it.

### Origin

- The 2026-07-09 post-0.12.0 field triage (maintainer-local — see `docs/evidence.md`) → ADR-0015/0016
  → the 0.13.0 spec (`docs/design/2026-07-10-keel-0.13.0-spec.md`, maintainer-local), gated by a
  two-round blind pre-mortem arc (1 BLOCKER + 2 MAJOR + 6 MINOR folded, then an operator close).
  Regression tests per behaviour-changing section (162 → 184).

## [0.12.0] - 2026-07-06

The certification-artifact release: closes ADR-0013's deferred design calls (B2, the read-only
reviewer's honesty contract, the A4 subset convention) and formalizes the round economy the
0.11.0 field wave kept hand-rolling. Design register: ADR-0014. Spec gate arc: three blind
pre-mortem rounds, 22 findings folded (1 BLOCKER — the certification hash as first designed was
unstable under fold-ledger growth — caught before any code).

### Added

- **B2 — artifact-backed certification** (`check-ready`): a certification may name its saved
  pre-mortem output (`Certification artifact:`); B2 then verifies the file exists, its last
  line-anchored `PREMORTEM-VERDICT` token agrees with the recorded Verdict (leading-token parse —
  an identity suffix is inert), and its `Spec-hash:` matches the current spec (mismatch = WARN
  "certified against an earlier revision"; no artifact named = adoption WARN). New
  `keel spec-hash` prints the canonical hash — sha256 of the spec with its certification
  section's lines **removed** (not blanked), so the hash is invariant to certification-block
  growth and CRLF/LF. Warnings now print on **both** CLI exit paths (a failing spec no longer
  hides its WARNs). `keel-premortem.md` carries the save-the-artifact protocol; honest framing
  everywhere: B2 raises forgery cost, it does not prove blindness (ADR-0002/ADR-0014).
- **The pre-mortem output contract v2** (prompt ⊕ agent, byte-identical; MARKERS 28 → 33): a
  re-gate posture for round ≥2 (audit each prior finding RESOLVED / PARTIALLY-RESOLVED /
  UNRESOLVED before hunting new ones); an optional `cleared:` list (verified-correct claims
  recorded as confirmations); a structured `conditions:` list on CONDITIONAL-CERTIFY;
  `blast_radius:` in the finding YAML when a fix touches shared/global config;
  `unverified-offline` generalized to every execution-requiring directive with an
  `Unverified-offline:` count; reviewer identity stated after the verdict token (the bundled
  agent's identity line is a version-consistency site, so a stale plugin cache self-announces);
  and the caller-records clarification — the agent stops reporting its read-only-ness as a
  deviation.
- **The round economy** (doctrine + `keel-premortem.md`, ADR-0014): two rounds when round 1 found
  a BLOCKER, the spec touches an irreversible/shared-contract surface, or the set is
  fresh-drafted from an adjudicated catalog; one pass with executor-verified folds for LOW-stakes
  reversible rounds; one targeted confirmatory pass after an upstream merge. The final pass
  always re-reads the folded spec.
- **SERIES-pass decomposition completeness** (prompt ⊕ agent): every headline property and
  referenced asset is BUILT by a named PR, and each acceptance test is ABLE to prove its
  invariant (stub vs real-process).
- **Generated-artifact freshness, both directions** (prompt ⊕ agent + spec-template): touching a
  source surface enumerates its downstream generated/mirrored/golden artifacts even when no PR
  plans regeneration; the template's DoD carries the declaration line the pre-mortem challenges.
- **Reflection-triage grounds its promotions**: a new procedure step verifies the mechanism a
  candidate promotion names against current source before it is written; emitted triage docs
  open with a `# Triage —` H1.
- **The Phases header convention** (A4, ADR-0014): `- **Phases:** Decide+Specify (Decompose:
  skipped)` relaxes the manifest requirement to absent-ok for a declared non-series round — a
  present manifest is still fully checked; nothing else relaxes.
- `docs/method-bindings.md` (keel's own filled sheet — the real worked example),
  `docs/getting-started.md` (the first full loop, exact commands), `docs/glossary.md`.
- `ADR-0014`: the certification artifact and the round economy (resolves ADR-0013 items 1–3).

### Changed

- `check-ready` fold-ledger rows may carry a verified snippet (`` `path:line` `snippet` `` — A12
  matches it against the anchored line, so in-range drift no longer decays silently), and
  non-resolving anchors with a unique repo basename get a "did you mean `<relpath>:<line>`?" hint
  (vendor/VCS trees excluded); A5 "to be created" paths are claimable by a unique basename named
  in a section body.
- `spec-template.md` ends with a kit stamp (`<!-- keel kit X.Y.Z -->`); `check-ready` WARNs on a
  kit↔gate MAJOR.MINOR mismatch — including under `--structure-only` — and stays silent on absent
  stamps; `check-ready` also WARNs when a certification is recorded while the header Status still
  says draft. `skills/apply-method/SKILL.md` states the keel version it ships with. The
  version-consistency test now reads **seven** sites.
- `CONTRIBUTING.md`: a post-certification change to an open release lands as a spec amendment
  section (panel ARCH-8); window/neighbourhood check logic is tested against the shipped
  template's own artifacts (gate-health).

### Origin

- The 2026-07-06 post-0.11.0 field triage (8 reports: two six-spec two-round gate arcs, two
  consumer waves, a greenfield build, a controlled single-round data point; maintainer-local —
  see `docs/evidence.md`) + ADR-0013's scheduled 0.12.0 items. Spec:
  `docs/design/2026-07-06-keel-0.12.0-spec.md` (maintainer-local), gated by a three-round blind
  pre-mortem arc — 22 findings folded, including a BLOCKER in the certification-hash design
  caught before any code. 38 new regression tests (124 → 162); every gate-behavior section ships
  at least one.

## [0.11.1] - 2026-07-06

Docs-only patch (the panel-tail triage's docs lane; no gate-behavior change). Sub-threshold round
per doctrine §6 — the 0.6.1 precedent.

### Changed

- Pre-ADR-0002 "signed" wording retired everywhere it survived: the DoR's Part B is "certified by a
  non-author reviewer" (`skills/apply-method/SKILL.md`, `docs/templates-reference.md`,
  `spec-template.md`).
- Private working vocabulary removed from public docs: SP2/SP3 are now "the template kit" and "the
  upgrade set" (`docs/doctrine.md` §7, `src/keel/templates/README.md`); "the FIRE step" is "the
  orchestrator's file-staging step" in `pre-mortem-prompt.md` ⊕ `agents/pre-mortem-review.md`
  (byte-identical, drift-guard markers intact); DC4-B, used by the prompt/agent, is now defined in
  doctrine sharpening 5 (standing cross-artifact consistency) — and the stale "three axes" cardinal
  was dropped rather than re-counted.
- The 30× cost-of-defect note is qualified as what it is: one program's observational retro, two
  design-time catches, no counterfactual arm, maintainer-local corpus (`docs/doctrine.md`,
  cross-referencing `docs/evidence.md`).
- `series-toml-skeleton.md` no longer points at another tool's unreachable doc; it states the
  minimal `[[pr]]` contract the method reads (`id`/`prompt`/`section`/`tier` + `[budget]`).
- `docs/installation.md` + `docs/cli-reference.md` document the `python -m keel` module entry point
  (shipped since 0.4.0) as the fallback where an application-control policy blocks console-script
  executables — field-hit on a real consumer wave.
- `spec-template.md` names the gate-adversarial-example rule: quote gate-scanned tokens (a literal
  `Verdict:` line, a bare to-do marker) only inside code fences, which the gate masks.

### Origin

- The 2026-07-02 panel-tail triage's docs-PR lane (T1a–T1g) + two post-0.11.0 field findings
  (`2026-07-03-mantis-agent-researcher-pivot`, `2026-07-02-keel-0.11.0-self-build`;
  maintainer-local corpus — see `docs/evidence.md`).

## [0.11.0] - 2026-07-01

The enforcement-gap release. A six-lens blind skeptic panel (Fable 5, max effort; two lenses ran the
CLI against adversarial specs) found the DoR gate enforced less than it documented and false-failed
ordinary prose, and that the plugin adoption chain broke for a non-author machine. This closes the
mechanizable half; the design calls are recorded and deferred (ADR-0013).

### Fixed

- **`check-ready` is now fence-aware** (`_mask_fenced`): fenced code is masked before section-splitting
  and every line scan, so a fenced example `Verdict: CERTIFIED` can no longer shadow a real recorded
  REJECTED verdict (a reproduced B1 forgery), and a quoted `# TODO` / `### heading` no longer
  false-fails an honest spec.
- **A4 is a real bijection**: the section id is read only from the "Implements section" column — one
  section per PR row, one PR per section — so one PR citing two sections fails and a `§N` in a comment
  cell no longer miscounts.
- **R1/A12**: a fold-ledger row with fewer than three cells is a violation, not a silent skip.
- **A6 anchors**: a backticked `host:port`, URL, or `path:line:col` no longer false-parses as an anchor;
  the optional snippet is same-line and not itself anchor-shaped (so two adjacent anchors are both
  checked); a known extension-less file (`Makefile`) resolves; a backslash or absolute path is rejected
  as non-portable; a directory anchor no longer crashes (`is_file()`).
- **A2 / A3**: the acceptance criterion is counted only within its own paragraph (an empty criterion
  followed by prose no longer passes), and a leftover `<...>` template placeholder outside code fails —
  so a minimally-edited `new-spec` stamp no longer passes the whole gate.
- **A10**: scans across a hard line-wrap, keeps a backticked invariant key, and uses real negation cues
  (`n't` / `yet` / `to be`) — fixing both the wrap/backtick bypass and the common-word false-fire.
- **A9 / A11 / A8 / B1**: A9 requires a column-0 (importable) symbol; A11 also fires on a tail-truncated
  range; A8 treats `ADR-`/`RFC-`/`PEP-` section references as cross-document; B1 rejects a second
  (appended, retracted) Verdict line.
- **Exit codes**: a directory or non-UTF-8 spec is not-runnable (exit 2) via a `format_error`, not a raw
  traceback at exit 1.
- **Plugin adoption**: commands and the `apply-method` skill address plugin files as
  `${CLAUDE_PLUGIN_ROOT}/…` and run the CLI from the bundle (`uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`);
  the skill binds the copied `method-bindings.md`, not the packaged master; `keel-premortem.md` carries
  the full certification-record protocol so it composes with `check-ready`; `installation.md` fixes the
  invalid `uv add --git` and documents `uv tool install` + tag pinning.
- **Drift guard**: a live prompt↔agent divergence is fixed (the agent's DC1 bullet had dropped "and
  sibling repos"), and a verbatim clause-identity check is added; the guard's guarantee is stated
  honestly (marker-presence + clause-identity, not "can never drift").

### Added

- `docs/evidence.md` and ADR-0012 (the publication boundary): public docs no longer cite gitignored
  evidence as if it resolved; the maintainer-local corpus is labelled unpublished.
- `ADR-0011` (the enforcement gap) and `ADR-0013` (deferred design calls: B2 artifact-backed
  certification and the agent-tool decision → 0.12.0; the A4 subset-of-phases relaxation → 0.12.0 or a
  real external report; the validation experiment → 0.13.0 run-or-retire).
- Self-application guards: a version-consistency test across the four sites + the newest CHANGELOG
  heading; a CLI-reference-coverage test; `_resolve_base`'s first nested-spec test; a CI matrix
  (ubuntu + windows) using `uv sync --group dev`.

### Changed

- `CONTRIBUTING.md` and `docs/doctrine.md` separate machine-enforced gate-health rules from unshipped
  maintainer disciplines (gate hit-rate tracking, fail-closed triage) — the over-claim class keel's own
  A10 gate polices in specs.
- `docs/cli-reference.md` gains `new-spec`, `--structure-only`, and `--version` (four releases stale).

### Origin

- The 2026-07-01 six-lens blind skeptic panel (`docs/feedback/2026-07-01-skeptic-panel-fable5.md`, 76
  findings across architecture / gate red-team / cold-user / epistemology / code / integration lenses;
  maintainer-local). Spec: `docs/design/2026-07-01-keel-0.11.0-spec.md`. 28 new regression tests (25 in
  `tests/test_check_ready_enforcement_gap.py` + 3 cross-artifact guards; 124 total); each of the ten
  spec sections ships at least one. Not every finding shipped — the deep design
  calls are deferred with triggers in ADR-0013, not silently dropped.

## [0.10.0] - 2026-06-28

### Added

- **The measured-unit causal-path & capability audit** — a pre-mortem directive carried in BOTH
  `pre-mortem-prompt.md` and the bundled `pre-mortem-review` agent (pinned by the `inert-treatment`,
  `side channel`, and `enforcement mechanism` drift markers) plus matching eval-spec DoR items: a
  measurement spec is attacked from BOTH ends of the causal arrow it assumes — the treatment must reach the
  measured path (else **inert**: mis-built, not null — distinct from feasibility), and the measured unit
  must have no capability beyond its intended input that is a **side channel** to the ground truth (else
  **confounded**, not null — a sharpening of instrument defeatability), and every isolation/leakage
  invariant must name a buildable **enforcement mechanism** assigned to a numbered §/PR. Closes the gap
  that cost a ~$417 confounded eval run (field reports `2026-06-27-agent-discovery-d6` /
  `-engine-eval-design`, `2026-06-26-tu-memory-eval-premortem`).
- **The re-cert hunts the fold's own newly-introduced errors** (prompt ⊕ agent, pinned by the
  `newly-introduced` marker; doctrine sharpening 4): the post-fold coherence re-read also re-grounds each
  new/reworded claim the fold added, and re-verifies a pivoted spec's new linchpin against code.
- **The `## Experiment design (Part B)` section** is now stamped (optional, self-contained) into
  `spec-template.md`, and the eval-spec DoR profile gains the **pre-registered analysis plan** axis
  (closing an inherited template-vs-DoR drift the cross-vendor panel surfaced).
- `ADR-0010`: the causal-path & capability audit.

### Changed

- The drift guard pins the MARKERS tuple length at 28 (each new marker lands with its count bump in the
  same change: §1 → 27, §2 → 28). The cross-vendor pre-mortem panel (DeepSeek-R1 + GPT-5.5 + Gemini-2.5-pro
  via OpenRouter, gitignored maintainer tooling) ran again as non-blocking enrichment; GPT-5.5 caught a
  real pre-registration drift the Claude passes missed.

### Fixed

- `check-ready` anchor recognition (A6 / A11 / A12) now accepts **dotfile and extension-less paths**
  (e.g. `.gitignore:19`, `docs/Makefile:5`). Previously the parser required a `name.ext` shape, so a
  dotfile anchor was silently ignored (A6/A11) or rejected as "no resolving `artifact:line`" (the A12
  fold ledger). An anchor path is now recognized when it is path-like — it contains a `.` or `/` — which
  still rejects a bare `N:M` (e.g. a `3:4` ratio). Surfaced by the 0.10.0 self-build's own fold ledger;
  fixed at the root with regression tests.

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
