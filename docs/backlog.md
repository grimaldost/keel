# keel improvement backlog

- **Opened:** 2026-08-11, against the 0.13.1 tree.
- **Status:** in progress. Items land through the normal loop (CONTRIBUTING §The loop) and are
  recorded in `CHANGELOG.md` when they ship. Each item below carries its own **Status** line once
  worked; an item with none is untouched.

## Wave 2 — 2026-08-12, branch `feat/gate-empiricism` (released as 0.15.0)

The gate-empiricism wave. **KEEL-B07** shipped whole (the hit-rate ledger in three states, plus the
finding-identity work it turned out to need first), and three further rows moved without being
finished: **KEEL-B10** and **KEEL-B12** landed their kit half (`pre-mortem-profiles.md` and the DoR
items that moved into it) and left their pre-mortem-prompt half held behind KEEL-B09;
**KEEL-B33** landed in the form its cross-review note asked for — nothing cut, the delegation made
explicit — because two sibling projects now point at those files by reference. **KEEL-B25/W8** and
**KEEL-B26** were recorded in the wave's own commits and are unchanged here.

Two measurements were bought and both are recorded honestly rather than as verdicts:

- **The kit-core ablation, stage 1 of two.** 24 of 48 trials, $9.7572, saturation gate passed,
  stage 2 unbought. It does not license the cut it was bought to license, so nothing is cut — the
  candidate bodies ship as measurement assets `keel init` cannot reach. The reading is in
  `CHANGELOG.md` 0.15.0 §Measured; the short version is *two underpowered signals in opposite
  directions*, which is an instrument without power, not a null.
- **The pre-mortem directive ablation (KEEL-B09).** Run, read, and **gated** — see its Status row.
  Until the adjudication it waits on lands, the item still holds net-new directive prose.

Deliberately not taken here: everything the wave-1 table above still holds, plus **KEEL-B13**,
**KEEL-B21** and **KEEL-B23**, none of which had a reason to ride this branch's files.

## Wave 1 — 2026-08-11, branch `backlog/wave-1`

Nine items, chosen as those gated on neither a re-run of the suite's eval harness nor a sibling
project moving first: **KEEL-B02** (fold the pre-mortem directives to one source, ADR-0017),
**KEEL-B06** (body budgets), **KEEL-B01** (declared spec kind), **KEEL-B03** (one field parser),
**KEEL-B04** (the reviewer's own anchor form), **KEEL-B29** (delete the empty `hooks.json`),
**KEEL-B05** (the pre-commit half + the enforcement statement), **KEEL-B08** (changelog currency +
release tags), **KEEL-B36** (`.remember/` cleared).

Two things the wave leaves for the operator, both deliberate:

- **No release was cut.** `origin/dev/agent-agnostic-surface` already carries a
  `release: keel 0.14.0` commit, unmerged, so this branch must not claim that number. The wave's
  changes are therefore unrecorded in `CHANGELOG.md` — which KEEL-B08's own new CI job will fail
  on when this branch is opened as a PR. That is the gate working: the release entry and the
  version bump are the merge step, and they have to reconcile with the in-flight 0.14.0 first.
  *Reconciled:* the wave merged as **0.14.0** on main (PR #17), claiming the number on main's line;
  the unmerged branch renumbers when it lands.
- **Tags are local.** v0.11.1, v0.12.0, v0.13.0 and v0.13.1 were created at their release commits
  on main; `git push --tags` publishes them.

Deliberately **not** taken in this wave, each with the gate that holds it:

| Item | Gate |
|---|---|
| KEEL-B09 | has to be built as a bank on the eval harness (its cross-review note) rather than as a bespoke three-arm run. **KEEL-B07 no longer waits on it** — the hit-rate question turned out to need no agent at all, and shipped (below) |
| KEEL-B28 | the skills collection's CRAF-B29 holdout finding; only the specificity half is keel's either way |
| KEEL-B31 | the research runner's MANT-B01/B02 — deleting `scripts/external_review/` before those land replaces a working client with one that aborts |
| KEEL-B30, KEEL-B32 (series-skeleton half) | the bound orchestrator's live measurement window (CONV-B18/CONV-B33): editing the skeleton mid-window would make a near-zero reading a record of our own edit |
| KEEL-B32, KEEL-B33, KEEL-B34 | two sibling projects are about to point at this kit by reference (FATH-B37, MANT-B48); `review-checklist.md` and `definition-of-done.md`'s gate commands must not be cut before those consumers move |

`.remember/` was archived to the operator's session scratchpad before removal (it is gitignored, so
nothing in git recorded it); the `.gitignore` entry stays, because the enclosing tool can recreate
the directory and an ignored path keeps `git status` honest about the repo's own files.

This is the leverage-ordered successor to ADR-0013's deferred-call list, which is now fully
discharged (see "Reconciliation" below). It merges three inputs:

| Source tag | Input |
|---|---|
| `[triage]` | the 2026-08-11 field triage of the dogfooding corpus (maintainer-local, unpublished) |
| `[review]` | a feature-by-feature audit of the surface against the current harness baseline |
| `[research]` | two 2026-08-11 briefs: the native-capability/skills-evidence brief and the competitive-landscape brief (maintainer-local, unpublished) |
| `[cross-review]` | a 2026-08-11 consistency review of this backlog against the four sibling backlogs in the same suite (maintainer-local, unpublished) |

## How to read it

- **Now** — highest leverage; take these before anything else, roughly in order.
- **Next** — real, grounded, but sequenced behind a Now item or behind a measurement.
- **Later** — carried watches, low-severity residuals, and work that needs accumulated data first.
- **Retire / fold candidates** — features the audit sentenced. Each names its replacement.
- **Declined** — proposals decided against, recorded so they are not relitigated.

Items are not a queue: an item's ID is stable, its section is not.

## Citation convention

Per ADR-0012, a published document does not cite a gitignored path as if it resolved. Field
evidence below is cited by **report stem**, labelled as maintainer-local and unpublished, with the
consumer project's name redacted to `…` — the corpus is dogfooding history against real consumer
projects and an environment-scoped internal tool, and the stems carry that detail. Committed paths
(`src/keel/check_ready.py:820`) are cited normally and resolve in a fresh clone.

The same rule covers the `[cross-review]` rows added later in this pass. A sibling project's
backlog row is cited by its stable ID (`FATH-`, `CONV-`, `MANT-`, `CRAF-`) and nothing else: those
backlogs are maintainer-local and unpublished, and none of them resolves from a fresh clone of this
repo. The sibling tool itself is named by its role — the eval harness, the bound series
orchestrator, the research runner, the skills collection — as the rest of this document already
does.

---

## Reconciliation

### ADR-0013's four deferred calls — all discharged

| ADR-0013 item | Outcome | Residual carried here |
|---|---|---|
| 1. B2 artifact-backed certification | **Shipped** 0.12.0 (certification artifact + `Spec-hash` agreement) | The block records what was owed, never what was paid → **KEEL-B15** |
| 2. Read-only agent carrying executable mandates | **Decided** ADR-0014: `unverified-offline` generalized to every execution-requiring directive, with an `Unverified-offline: <N>` count | Nothing consumes `N` → **KEEL-B14** |
| 3. A4 vs the subset-of-phases doctrine | **Shipped** ADR-0014's `Phases: … (Decompose: skipped)` relaxation | It reaches `_check_manifest` only (`check_ready.py:577`), so the rest of the structural trio is still unconditional → **KEEL-B01** |
| 4. Run or retire the validation experiment | **Discharged** ADR-0015 (retired, unmeasured), pinned by `tests/test_claim_currency.py` | The same standard was never turned inward on keel's own most expensive artifact → **KEEL-B07**, **KEEL-B09** |

No other roadmap, backlog or plan document exists in the tree; `docs/design/` holds per-release
specs, not forward plans.

### Field asks already shipped — do not re-propose

Grounding the 2026-08-11 triage against the 0.13.1 tree closed fourteen field requests as
already-shipped. Four of them a CHANGELOG-only reconciliation would have missed, so they are
recorded here explicitly. `[triage]`

- Shared text segmentation (`_mask_inline_spans` / `_split_cells`) — 0.13.0 §1.
- The operator close for an accepted CONDITIONAL-CERTIFY — 0.13.0 §4; validated five times in the
  field this round.
- `reflection-triage.md` lands-and-sweeps — 0.13.0 §5.
- The `consumed_input` findings field — 0.13.0 §6.
- The CHANGELOG heading-chain test, including the absorption signature — 0.13.0 §2.
- The `# Triage —` H1 detection convention — 0.12.0 §7.
- The `Phases:` / ADR-0014 manifest relaxation — 0.12.0 §11.
- The kit-skew WARN — 0.12.0 §9 (silent when no stamp exists at all; that residual is **KEEL-B17**).
- The fold-ledger verified snippet — 0.12.0 §8.
- The pre-mortem finding schema is pinned, drift-marker paired (`agents/pre-mortem-review.md:77-86`).
- "A `smallest_fix` is a hypothesis, not an instruction" ships at `agents/pre-mortem-review.md:104`.
- The pending-verdict / never-pre-filled discipline, with placeholder and verdict-token checks.
- "Re-read the reused component" ships at `src/keel/templates/pre-mortem-prompt.md:35`.
- The plugin-cache and Windows invocation recipes ship (`docs/installation.md:43-48`,
  `commands/keel-check-ready.md:9-12`); the residual is discoverability only (watch W7, **KEEL-B25**).

---

## Now

### KEEL-B01 — A declared spec kind relaxes the Part-A structural trio, so the legitimate small or foreign spec stops needing an operator override

- **Cause / evidence:** the Part-A structural contract is unconditional — check-ready assumes it
  scaffolded the spec it gates, so the decomposition trio (`## Numbered sections`, the PR↔section
  manifest, the concept→module map) is hard-required regardless of spec kind or origin. Five field
  reports; a hard gate was operator-overridden three consecutive times on one artifact
  (`2026-07-17-…-premortem-checkready-host-repo`, `2026-07-23-design-round-checkready-bindings-drift`,
  `2026-07-17-…-curve-freshness-regate`, `2026-07-17-…-curve-freshness-r6r7`,
  `2026-07-23-…-v113-spec-gate`; maintainer-local, unpublished). Grounded: no spec-kind concept
  exists, and the 0.12.0 relaxation reaches `_check_manifest` (`check_ready.py:577`) only.
  `[research]` corroborates the shape — a vendor shipped the same concession as Quick Spec, and a
  method with no cheap path is abandoned on small work first and large work second.
- **Change:** a declared kind in the spec header (`series` | `single-change`) widens the shipped
  `Phases:` mechanism rather than adding a second one; a trio section that *is* present is still
  checked in full; the missing-section violation names the exact sections missing rather than the
  generic requirement. Homes: `check_ready.py` + `spec-template.md` header +
  `definition-of-ready.md` Part A reference + tests.
- **Status:** **shipped** 2026-08-11 (wave 1). `Kind: series | single-change` in the header;
  `single-change` relaxes all three trio sections to absent-ok and moves the
  acceptance-criterion floor to the document; a present section is still checked in full; an
  unknown kind fails naming the offending token; the three absence violations now name the
  exact heading and the declaration that relaxes it.
- **Effort:** M · **Source:** `[triage Q1a]` `[research]`

### KEEL-B02 — Fold the pre-mortem directives to one source before anything else edits them

- **Cause / evidence:** the directive text lives in two files that are ~90% identical
  (`agents/pre-mortem-review.md`, ~2,300 words; `src/keel/templates/pre-mortem-prompt.md`, ~2,500
  words), held together by a drift-guard test pinning a 34-marker tuple that is bumped on every
  release. The pair has only ever grown, across ADR-0004/0007/0008/0009/0010/0016 — the growth
  failure the doctrine forbids. Feature review; `[research]` names duplication and body bloat as the
  dominant defects in skill corpora and reports that compression improved functional quality.
- **Change:** make the agent body a thin identity + output-contract wrapper that Reads
  `${CLAUDE_PLUGIN_ROOT}/src/keel/templates/pre-mortem-prompt.md` at run start and applies every
  directive; the template survives because it is the copy that reaches consumers running the method
  without the plugin. Delete the drift guard with the duplication it exists to hold together (keep
  `test_agent_preserves_frontmatter` and the version-identity assertion). Then compress the
  directive block itself: feasibility / power / defeatability / side-channel are four parenthetical
  asides that fit one four-row table.
- **Disagreement:** the triage assumes the pair persists — Q3b and Q6a are both written as
  drift-marker-paired edits landing twice. The audit sentences the duplication. Resolved by
  ordering, not by choosing: fold first, then those edits land once against one file.
- **Status:** **shipped** 2026-08-11 (wave 1), recorded as ADR-0017. The template is the single
  home; the agent is a thin identity + dispatch + output-contract wrapper that Reads it; the
  34-marker drift guard is retired and replaced by a test pinning the arrangement
  (delegation, non-duplication, identity); the four eval/experiment probes' parentheticals
  became one table.
- **Effort:** M · **Source:** `[review]` `[research]`

### KEEL-B03 — One shared field-extraction parser for Part A, and violations that name the offending token

- **Cause / evidence:** Part-A field extraction consumes more text than the field it names, and a
  violation names the row rather than the token that broke it. This is post-fix recurrence one layer
  below 0.13.0 §1: masking was fixed, field extraction was not. Five reports
  (`2026-07-17-…-curve-freshness-r6r7`, `…-curve-freshness-regate`,
  `2026-07-17-…-premortem-checkready-host-repo`, `2026-07-23-…-v113-spec-gate`,
  `2026-07-11-…-mock-consumers`; maintainer-local, unpublished). Grounded: `_check_fold_ledger`
  reads `cells[2]` positionally (`check_ready.py:820`); `_check_certification_artifact`
  (`check_ready.py:1040`) strips backticks from the whole value and resolves the remainder as a path.
- **Change:** (a) one shared leading-path-token parser for path-valued fields — take the first
  backticked-or-bare path token, ignore trailing prose — applied to `Certification artifact:` and
  any path field added later, with the template showing where prior-round artifacts go; (b) A12
  resolves a row's anchor from the cell that *is* an `artifact:line`, any column, and names the
  offending token and the cell it read on failure; (c) the `§N` resolver skips a References section
  and a `(§N)` riding a cross-doc citation. Escalate to the parser; do not re-prose the template.
- **Status:** **shipped** 2026-08-11 (wave 1). `_first_path_token` is the one home for
  path-valued fields (applied to `Certification artifact:`); A12 reads the anchor from
  whichever cell IS one and names the cell it read on failure, with the column-break
  diagnostic promoted ahead of the search so it survives the widening; A8 skips a References
  section and no longer loses a cross-doc cue to an intervening `(`.
- **Effort:** M · **Source:** `[triage Q2a/b/c]`

### KEEL-B04 — Accept the anchor form keel's own reviewer emits

- **Cause / evidence:** the pre-mortem agent returns shorthand anchors, folding them into the spec
  is the natural next move, and check-ready then hard-fails each one — while already computing the
  correct resolution and offering it only as a hint (`_unique_basename_match`,
  `check_ready.py:407`; the hint at 425+). Three reports (`2026-07-17-…-curve-freshness-regate`,
  `2026-07-17-…-premortem-checkready-host-repo`, `2026-07-23-…-v113-spec-gate`; maintainer-local,
  unpublished). A prose fix for this already shipped once (2026-06-19 round); the recurrence
  justifies the mechanical rung.
- **Change:** `_resolve_anchor` accepts a unique basename match with a WARN naming the expansion,
  and fails only on ambiguity or no match — applying the resolution it already computes. Paired:
  the agent's output contract requires repo-root-relative anchors in `evidence:` and in every cited
  line, so the fold stops manufacturing gate failures.
- **Ordering:** the output-contract half lands after KEEL-B02, as a single-file edit.
- **Status:** **shipped** 2026-08-11 (wave 1). `_resolve_anchor` applies the unique-basename
  resolution with a WARN naming the expansion (W3) and still verifies the line range and any
  snippet against the file it found; ambiguity fails naming the candidates. The paired
  output-contract half landed once, in the template (ADR-0017's one home).
- **Effort:** S · **Source:** `[triage Q3a/b]`

### KEEL-B05 — Turn A10's predicate on the repo itself and close the four enforcement gaps

- **Cause / evidence:** A10 fails a spec whose prose claims an invariant enforced while its own
  status table marks it planned or absent. The repo carries exactly that failure class four times:
  `hooks/hooks.json` ships `{"hooks": {}}` while the doctrine names hooks as one of the two
  deterministic machines; `.pre-commit-config.yaml` is declared but no hook is installed in this
  checkout, and it covers two of the four Definition-of-Done gates; `keel bind-check` and
  `keel budget-drift` are documented in `docs/cli-reference.md` and always exit 2, deferred across
  thirteen releases. Feature review and operator observation. ADR-0011 is titled "the enforcement
  gap"; this is the same predicate unapplied to its author.
- **Change:** build or delete each one, and state the result in CONTRIBUTING so the claim matches
  the machine. Dispositions proposed here: `hooks.json` → **KEEL-B29**; `budget-drift` →
  **KEEL-B30**; `bind-check` → build, **KEEL-B17**; pre-commit → either install and widen to a fast
  subset of the four gates, or delete the file and name CI as the sole gate.
- **Cross-review note:** the pre-commit half of that disposition assumes a normal install, and this
  machine is not one. Application control blocks the bare shim here: a directly-invoked `pre-commit`
  binary fails, while git-invoked hooks run fine — so "no hook is installed in this checkout" is
  partly an environment fact and not only a neglected step, and a plain `pre-commit install` would
  leave the claim in CONTRIBUTING as untrue as it is now. The working form is already recorded
  elsewhere in the suite: the research runner's MANT-B11 installs the hook as a `core.hooksPath`
  script that invokes the module rather than the shim, and the operator's exemption list, which
  names a compensating control per blocked hook, is CRAF-B26. Read both before choosing between
  installing and deleting — "install" here means the hooksPath form, and if that is judged too
  house-specific to carry in a consumer-agnostic kit, then delete and name CI is the honest branch.
- **Status:** **partly shipped** 2026-08-11 (wave 1). Two of the four gaps closed:
  `hooks.json` deleted (KEEL-B29), and the pre-commit hook installed in the `core.hooksPath` +
  `uv run python -m pre_commit` form the cross-review note names, widened to three of the four
  DoD gates. CONTRIBUTING now carries an enforcement-status table — A10's predicate turned on
  its author — stating all four. The remaining two are `bind-check` (KEEL-B17) and
  `budget-drift` (KEEL-B30), both still documented stubs that exit 2.
- **Effort:** M · **Source:** `[review]` `[research]` `[cross-review]`

### KEEL-B06 — Give the two bodies that only grow an explicit budget

- **Cause / evidence:** the operator's stated rule is that a promotion adding prose names what it
  displaces. It is visibly failing: the marker count went 33 → 34 in ADR-0016 (one clause per
  finding), and the pre-mortem pair and the spec template's contract notes have only ever grown —
  the template carries roughly 60 italic gate-contract lines out of 185, and ADR-0016 deliberately
  chose to carry guidance in both the gate message and the template without giving that choice a
  budget. Feature review, which names this the single highest-leverage process change available.
- **Change:** record in CONTRIBUTING a word cap for the pre-mortem directive text and for the
  spec-template contract notes, and the rule that a new directive or note names the one it replaces
  or merges into. A budget is what makes KEEL-B02's compression hold rather than refill.
- **Status:** **shipped** 2026-08-11 (wave 1). Caps recorded in CONTRIBUTING ("Body budgets")
  and enforced by `tests/test_body_budgets.py`, which also asserts the doc and the suite carry
  the same numbers: directive block 2,050 · spec-template contract notes 925 · agent wrapper
  550. Net-new directive prose still waits on KEEL-B09.
- **Effort:** S · **Source:** `[review]` `[research]`

### KEEL-B07 — Instrument gate hit-rate so "is this check sharp or decayed ritual?" is answerable

- **Cause / evidence:** CONTRIBUTING §Gate health item 3 states that a gate firing zero times across
  N series is a triage input, and admits no hit-rate ledger exists in the tree. Without it, every
  keep verdict on the twelve Part-A checks rests on design reasoning rather than data. Feature
  review; `[research]` Gate 4 makes measurement the deciding test and names absence of evidence as
  "probably inert", not "probably fine". This is the cheapest instrumentation in the surface.
- **Change:** `check_spec_ready` appends one line per run (spec stem, date, check ids that fired,
  verdict) to a local, gitignored ledger. After ~20 real runs, cut or sharpen any check with zero
  fires and record the outcome in the CHANGELOG.
- **Status:** **shipped**. Three corrections the build made to the item as written: (a) a finding
  had no stable id — `where` collides across checks — so `Violation.check`, a `Warning` type and a
  closed catalogue came first, or nothing was countable; (b) two states are not enough, because a
  zero-fire count cannot tell *inert* from *never had an opportunity*, so each check reports a
  `Probe(candidates, fired, causes)`; (c) the spec is identified by a digest, not a stem — stems
  name the project's roadmap. `keel gate-health` reads it back, `docs/evidence.md` carries the
  pre-registration written before any data arrived, and the "cut a zero-fire check" instruction is
  superseded by the standing three-part bar (opportunity, a positive control, no open defeat).
- **Effort:** S · **Source:** `[review]` `[research]`

### KEEL-B08 — Machine-enforce CONTRIBUTING step 4, and tag released versions

- **Cause / evidence:** keel's release loop has no machine layer for "record in CHANGELOG and bump":
  the version lock proves the eight version sites agree, never that any of them moved, so a shipped
  kit or doctrine promotion can merge CI-green with no CHANGELOG entry and no bump. Grounded this
  pass: the newest git tag is `v0.9.0` while 0.10.0 through 0.13.1 shipped, and
  `.github/workflows/ci.yml` carries no CHANGELOG or tag assertion
  (`2026-07-15-unrecorded-promotions`; maintainer-local, unpublished). A singleton promoted with
  justification: a real in-repo defect with a mechanical signature and the narrowest complement of
  an existing lock. `[research]` sharpens it — "count the promotions that shipped" is the question
  the reflection loop's defensibility rests on, and an unrecorded promotion is uncountable.
- **Change:** (a) a diff touching a shipped-kit path (`src/keel/templates/**`, `docs/doctrine.md`,
  `agents/**`, `skills/**`, `commands/**`) with `CHANGELOG.md` unchanged fails CI; (b) a
  release-flow assertion that every released version carries a tag, plus a recorded decision on the
  untagged releases.
- **Status:** **shipped** 2026-08-11 (wave 1). `scripts/changelog_currency.py` + CI's
  `changelog-currency` job hold (a); `tests/test_release_flow.py` holds (b), and v0.11.1,
  v0.12.0, v0.13.0, v0.13.1 were tagged retroactively at their release commits on main
  (0.2.0/0.2.1/0.3.0 are pre-publication history with no commit to tag — recorded in
  CONTRIBUTING §Release discipline).
- **Effort:** S · **Source:** `[triage Q9a/b]` `[research]`

---

## Next

### KEEL-B09 — Measure the pre-mortem directive body's marginal effect before it grows again

- **Cause / evidence:** ~2,300 words are dispatched on every pre-mortem and no with/without
  measurement has ever been run on them. The operator owns an eval harness and has not pointed it at
  the most expensive prompt in the suite — feature review calls this the accountability gap.
  `[research]` supplies the prior: across 49 public skills, 80% produced zero improvement and three
  degraded performance by up to 10 points; software engineering is the domain where injected
  procedure helps least; self-authored skills are the worst-performing category. Unlike the
  coordination-scale comparative bank ADR-0015 correctly declined as infeasible, this measurement is
  authorable now — the unit is one spec review, not a governed wave.
- **Change:** a three-arm blind ablation over ~10 historical specs with recorded post-hoc outcomes
  (ADR-0015 §3's predicted→materialized ledger is the scoring key): arm A the full directive body,
  arm B a ~500-word core (blind non-author, cite `file:line`, severity + `smallest_fix` +
  `disconfirming_test` + verdict token), arm C a bare adversarial spec review. Score adjudicated real
  BLOCKER/MAJOR findings per spec plus false-positive rate, blind to arm. Retire every directive arm
  B matches.
- **Cross-review note:** build this as a bank on the suite's existing eval harness, not as a bespoke
  three-arm measurement. Blind scoring, confidence intervals, spend rails and an append-only ledger
  already exist there, and the arms above are a scenario matrix in that harness's own terms. The
  argument is not only economy: a fresh instrument would silently re-create two defects that harness
  has already found and priced. Arming is asserted rather than verified, so an entirely unarmed arm
  can score 100% — which happened, at cost, on a full nine-trial arm (FATH-B01); and bank validity —
  the verifier must fail on the unmodified fixture and pass on a reference solution — is prose
  rather than a gate, which has produced two ceilinged banks discovered after the spend (FATH-B02).
  Arm B here is exactly an arming claim ("the ~500-word core reached the reviewer"), and the scoring
  key is exactly a bank whose discrimination has to be shown before it is trusted, so both defects
  apply to this measurement by construction. Banking on the harness inherits the fixes as they land;
  building alongside it inherits the bugs without the reports.
- **Prior to state before the run:** the suite owns one measured result in this neighbourhood — an
  in-session structured review pass at the strong tier scored **+0** against the same strategy
  without it (FATH-B35, which folds that arm away on the strength of it). Arm C is the closest thing
  this ablation has to that arm. Record the prior in the plan: it is the effect size this design has
  to be powered to distinguish from, and if the ablation returns +0 across all three arms that is a
  reproduction rather than a surprise.
- **Ordering:** after KEEL-B02, so there is one body to ablate. This item **gates net-new directive
  prose**; a rewrite that displaces (KEEL-B13) may land without waiting for it.
- **Status:** **measured; the compression it licenses is gated, and the gate has not cleared.** The
  ablation ran on the harness as the cross-review note required. A **225-word core** scored
  identical to the full **2,429-word** body on all nine shared-ask and citation-grounding criteria,
  at **80% of the cost**, and separated on one criterion the core was never told to emit
  (a convention criterion, p = 0.0022) — which is a result about what the reviewer supplies
  unprompted, not a licence on its own. The compression is **held on the owner's blinded
  adjudication of the 18 existing finding-lists**, which is **pending**: the criteria are proxies
  for finding quality, and cutting 2,204 words of directive on a proxy without reading what the two
  arms actually found would be the same error this item exists to prevent. So: **licensed-but-gated,
  not done.** Until the adjudication lands, the body is unchanged, this row still gates net-new
  directive prose, and the 2,050-word cap in CONTRIBUTING stands where it is — the measurement is
  not a reason to raise it and not yet a reason to lower it.
- **Effort:** L · **Source:** `[review]` `[research]` `[cross-review]`

### KEEL-B10 — Move the domain lenses out of the always-on bodies into a selected profile file

- **Cause / evidence:** keel has no lane for a wave whose deliverable is data or a measurement, and
  the lane machinery it does have is already duplicated across DoR Part B and the pre-mortem prompt,
  so adding one inline would triple it. Grounded: `definition-of-ready.md:94-120` carries **seven**
  items marked *(eval/experiment specs)* ahead of the code-spec items — the triage counted five;
  the audit's count is the correct one — and `pre-mortem-prompt.md:65-66` carries two
  paragraph-length lenses. Three reports (`2026-07-11-…-w7-corpus-v3`, `2026-07-11-…-w8-probe-design`,
  `2026-07-11-…-mock-consumers`; maintainer-local, unpublished). Independently, the audit finds the
  majority reader wades through a profile that does not apply.
- **Change:** a new `src/keel/templates/pre-mortem-profiles.md` kit file selected by the declared
  spec kind (KEEL-B01); DoR Part B's seven inline eval items and the prompt's two paragraph clauses
  fold in and are **deleted** from both. Net: two smaller always-on bodies, one referenced file.
  `templates.py:list_templates` globs `*.md`, so a new kit file ships and copies for free.
- **Disagreement:** the triage frames this as a shrink; the audit's cross-cutting finding is that
  one text living in four homes is the surface's dominant defect. Both hold only if the profile file
  is the *sole* home for what it absorbs — the deletions are the load-bearing half of this item, not
  the addition. KEEL-B06's budget covers the file from the day it lands.
- **Status:** **partly shipped** 2026-08-12 (wave 2, 0.15.0). `src/keel/templates/pre-mortem-profiles.md`
  exists and is selected by kind; the DoR sheet's seven inline eval/experiment Part-B items moved
  into it and were **deleted** from Part B, which is the half that carries the load. The
  pre-mortem prompt's own eval/experiment lenses (`pre-mortem-prompt.md:67-70` — baseline
  expectation, instrument defeatability, experimental-design validity) are **not** folded yet: the
  profile sheet restates them, so that text currently has two homes, which is exactly what this
  item exists to end. The fold is a directive-body edit and waits on **KEEL-B09**'s pending
  adjudication.
- **Effort:** M · **Source:** `[triage Q7a]` `[review]`

### KEEL-B11 — A data-migration profile with a data-level gate

- **Cause / evidence:** the offline gates are strong for code and spec correctness and structurally
  blind to input-distribution defects; a unit-green suite reads as a gate and is not one
  (`2026-07-11-…-w7-corpus-v3`, `2026-07-11-…-mock-consumers`; maintainer-local, unpublished).
  `[research]` names domain-specific verification that emits evidence as the highest-leverage
  surviving practice, and dependency-ordered decomposition of migration work as one of the few
  things native fan-out explicitly does not do.
- **Change:** into KEEL-B10's file — characterize the real input distribution over the
  discriminating field before assuming a schema; name the heterogeneity axes and require a gate per
  axis; a pilot sample constructed to contain one instance per named axis; an exact reconciliation
  ledger for the write side and a cutover-discriminating check for the read side; state that a
  unit-green suite is explicitly not a data-level gate.
- **Effort:** M · **Source:** `[triage Q7b]` `[research]`

### KEEL-B12 — A measurement profile that can return "no verdict"

- **Cause / evidence:** a measurement wave can pass every offline gate and still spend the paid run
  on degenerate arms (`2026-07-11-…-w8-probe-design`, `2026-07-24-experiment-rigor-build`;
  maintainer-local, unpublished).
- **Change:** into KEEL-B10's file — a bounded real pilot before the full paid run asserting every
  arm (baselines, controls, decoys) produces well-formed non-degenerate output, and a decision rule
  that reports "no verdict" when no arm discriminates rather than a false negative.
- **Status:** **partly shipped** 2026-08-12 (wave 2, 0.15.0). `pre-mortem-profiles.md` carries the
  reviewer items that detect a degenerate design *before* the spend — feasibility-grounding first,
  a per-criterion baseline expectation with the ceiling/floor flag, and instrument defeatability.
  The two halves still missing are the ones that change what happens **after** the spend: the
  bounded real pilot as a required step, and the explicit "no verdict" terminal state. This wave's
  own kit-core ablation is the worked case for why they are wanted — it stopped at stage 1 and had
  to report an instrument without power in prose, because no sheet gave that outcome a name.
- **Effort:** S · **Source:** `[triage Q7c]`

### KEEL-B13 — Widen the population clause from the author's cleanliness claim to the design's own domain

- **Cause / evidence:** the offline gates certify the design's stated path but never enumerate its
  domain — the real input population, the declared input types of a guarded entry point, and every
  enumerated mode the spec offers — so assumptions about the space the design operates over ride
  through certification honestly declared and uncontained. Four reports
  (`2026-07-11-…-w7-corpus-v3`, `2026-07-23-…-v113-spec-gate`, `2026-07-17-…-v112-premortem`,
  `2026-07-17-…-curve-freshness-regate`; maintainer-local, unpublished). Grounded:
  `pre-mortem-prompt.md:45` scopes the clause to "green on arrival / verified clean" claims.
- **Change:** one rewritten clause replaces the current narrower wording — input-population
  distribution over the discriminating field, declared input types of every guarded entry point, and
  every enumerated mode confirmed implementable under the design's own mechanism. No fourth probe.
- **Disagreement:** the triage treats the directive body as a live surface to widen; `[research]`
  and the audit treat it as unmeasured. This item survives that tension only because it *displaces*
  — it is net-neutral on body size. Net-new directive prose waits for KEEL-B09.
- **Ordering:** after KEEL-B02 (single-file edit).
- **Effort:** S · **Source:** `[triage Q6a]`

### KEEL-B14 — DoR separates "needs a live environment" from "traceable but not yet traced", and check-ready finally reads the count

- **Cause / evidence:** ADR-0013 item 2's residual. The prompt emits `Unverified-offline: <N>` and
  nothing consumes it (`pre-mortem-prompt.md:106`), so an untraced-but-traceable assumption rides to
  certification indistinguishably from one that genuinely needs a runtime. One field round got
  within a single hop of tracing it (`2026-07-17-…-curve-freshness-regate`,
  `2026-07-11-…-mock-consumers`; maintainer-local, unpublished).
- **Change:** DoR states the distinction — only "needs a live environment" may ride open; "statically
  traceable but not yet traced" blocks until traced, which a read-only agent can do. Mechanical rung:
  check-ready reads the artifact's `Unverified-offline: N` and WARNs when N > 0 on a CERTIFIED
  verdict. Consumes a field that already ships.
- **Effort:** M · **Source:** `[triage Q6b]`

### KEEL-B15 — The certification block records what was paid, not only what was owed

- **Cause / evidence:** the block records no condition boundary, no discharge line, no
  machine-readable base commit, and no recorded tool version — `spec-template.md:150-163` carries
  none of these fields, and B2 checks artifact existence, verdict token and `Spec-hash` currency
  only. Four reports (`2026-07-26-expdisc-wave2-detector`, `2026-07-17-…-curve-freshness-regate`,
  `2026-07-13-…-urn-fold`, `2026-07-11-…-v2`; maintainer-local, unpublished). This is also where the
  declined certifier-write-access proposal (**KEEL-B37**) is answered operator-side.
- **Change:** (a) each condition carries the boundary it binds to (a named PR, a freeze or publish
  commit) and the block carries a `Condition discharge` line per condition; a CONDITIONAL-CERTIFY
  with an undischarged condition WARNs — widening the shipped `conditions:` field rather than adding
  a mechanism; (b) a machine-readable `Base:` commit, with check-ready WARNing when it is no longer
  an ancestor of the branch under gate and when the recorded kit version disagrees with the serving
  manifest.
- **Effort:** M · **Source:** `[triage Q5a/b]`

### KEEL-B16 — The spec pin travels with the series it governs

- **Cause / evidence:** no pin travels, so a running series cannot cheaply prove which spec revision
  it is executing; one field round spent a session on provenance archaeology
  (`2026-07-11-…-v2`, `2026-07-13-…-urn-fold`; maintainer-local, unpublished). `[research]` names
  spec drift — the spec consulted at execution time and checked against implementation, or not — as
  the named failure mode of this whole category.
- **Change:** `keel spec-hash` plus the repo-relative spec path recorded in the series metadata, and
  a pre-launch resolve-and-match check before any paid run. The pin's *absence* is itself the flag.
- **Note:** consistent with the audit's position that keel should own only the traceability field
  and the tier vocabulary in the series skeleton (see **KEEL-B32**) — a pin is traceability, not
  engine economics.
- **Cross-review note:** the change has two halves and only the producing half is keel's. Emitting
  `keel spec-hash` and recording the repo-relative path lands in the series file, which keel owns.
  The consumer-side half — the pre-launch resolve-and-match check *before any paid run* — executes
  in the bound series orchestrator, which today has no field to carry the pin and no backlog row
  proposing one. Name that seam explicitly in this item, including what the orchestrator is expected
  to do on a mismatch (refuse, or warn and record), or the pin reaches the series file and stops
  there: written, never read, and at execution time indistinguishable from no pin at all. The
  "absence is itself the flag" clause above only holds if something is looking. This is also, so
  far, the only proposed join key between two of the suite's ledgers — the method's certification
  records on one side and the orchestrator's per-spawn run ledger on the other — which is a second
  reason to place the field deliberately with its reader named rather than as a side effect of the
  producing change.
- **Effort:** M · **Source:** `[triage Q5c]` `[research]` `[cross-review]`

### KEEL-B17 — Build `bind-check` as the entry-time reconciliation it was always for

- **Cause / evidence:** two independent inputs converge. The audit: a documented CLI command that
  always exits 2 is keel's own enforcement gap in miniature, deferred by ADR-0003 across thirteen
  releases while ADR-0016 §4 made the bindings sheet load-bearing on the read side without giving it
  a gate; the rule it would enforce ("a slot left unbound is a method-not-fully-applied warning") is
  prose that must always hold, which by keel's own escalation rule belongs in a machine. The triage
  supplies the motivating failure ADR-0003 recorded as missing: a project's bindings-recorded house
  format and kit stamp are never reconciled against the serving kit *before* authoring, including
  the no-stamp-at-all case `_kit_skew_warning` (`check_ready.py:214`) passes silently
  (`2026-07-26-expdisc-wave2-detector`, `2026-07-23-design-round-checkready-bindings-drift`;
  maintainer-local, unpublished).
- **Change:** parse the bindings table, violate on empty "This project" cells with a
  consciously-unbound escape marker (keel's own sheet names three unbound slots), and add the
  entry-time reconciliation: house format + kit stamp vs the serving kit, reported before authoring.
  Wire it into `apply-method`'s bindings-first entry step.
- **Effort:** M · **Source:** `[triage Q1b]` `[review]`

### KEEL-B18 — An ADR recording the template-coupling boundary

- **Cause / evidence:** two host-repo reports need a decision, not a patch: which DoR checks are
  format-agnostic (B1/B2, A12, anchors, acceptance) and which are template-coupled by design, and
  whether keel certifies a spec it did not scaffold (`2026-07-17-…-premortem-checkready-host-repo`,
  `2026-07-23-design-round-checkready-bindings-drift`; maintainer-local, unpublished).
- **Change:** `docs/adr/0017-*` recording the boundary, and recording the `--content-only` mode as
  declined with its reason (**KEEL-B38**) so the question does not return as a patch.
- **Effort:** S · **Source:** `[triage Q1c]`

### KEEL-B19 — A promotion states the family it covers, not the instance that motivated it

- **Cause / evidence:** a promotion is recorded against its motivating instance and nothing sweeps
  the artifacts already in that class, so a promoted check leaves live members of its own class
  undetected — including inside the artifact that motivated it. Three reports
  (`2026-07-11-…-corpus`, `2026-07-11-…-v2`, `2026-07-11-…-v3`; maintainer-local, unpublished).
  Grounded: step 1 already sweeps prior triage docs' open rows (0.13.0 §5); neither step mentions
  family or existing members. `[research]` names the reflection→triage→promoted-check cycle as the
  least-served part of this market and the most defensible thing keel has, which is the reason to
  keep it sharp.
- **Change:** rewrite step 4's existing destination sentence in `reflection-triage.md` so a
  promotion states its family and names and audits (or schedules) the existing artifacts already in
  that class. A rewrite, not an append.
- **Constraint:** the audit's one caution on this file — the plugin-branch handoff rule (emit a
  method-promotions doc whose H1 does not begin `# Triage —`) is subtle and load-bearing and must
  survive the rewrite intact.
- **Effort:** S · **Source:** `[triage Q8a]` `[review]`

---

## Later

### KEEL-B20 — An anchor grammar that can express a legitimately non-resolving referent

- **Cause / evidence:** a second repo's source, or coordinates that are pre-move by the spec's own
  design, cannot be written as anchors — so line-precision evidence is forced into prose or the gate
  reddens by construction (`2026-07-12-…-v4-cycle`, `2026-07-26-expdisc-wave2-detector`,
  `2026-07-11-…-mock-consumers`; maintainer-local, unpublished). Grounded: `_resolve_anchor`
  requires an in-tree file and no prefix vocabulary exists.
- **Change:** (a) one declared external-evidence form (e.g. `ext:<alias>/path:line`, alias declared
  in the certification's `Reviewed against:` block) that A-checks skip and a pre-mortem can still
  resolve; (b) state the DoR gate's one-shot lifetime plainly in the Part A preamble — a certified
  spec's anchors describe the tree at certification, and a spec whose first section relocates them
  stays truthful as instructions while DoD gates from PR01. The prose half displaces an unwritten
  assumption the field derived twice.
- **Effort:** M · **Source:** `[triage Q4a/b]`

### KEEL-B21 — Every manifest row runs the full gate list before its merge

- **Cause / evidence:** a series' intermediate states are gated by less than its tip: the spec's
  Gate commands list and the PR↔section manifest are separate sections with no stated relation, and
  the field read that as a per-branch choice (`2026-07-23-…-v113-spec-gate`,
  `2026-07-06-post-0110-field-triage`; maintainer-local, unpublished). Promoted on its second report.
- **Change:** one line where the manifest is defined — a per-branch subset is not a gate. Rides
  KEEL-B01's spec-template edit so the kit stamp bumps once.
- **Effort:** S · **Source:** `[triage Q11a]`

### KEEL-B22 — `keel fix-ledger`, and a fold protocol that ends where it should

- **Cause / evidence:** fold-round ledger upkeep is manual and re-paid every round — a post-ledger
  edit shifts anchors the author then recomputes by hand, and ledger-format defects surface as
  post-pass rework instead of at the gate that owns them (four reports: `2026-07-11-…-v3`,
  `2026-07-11-…-corpus`, `2026-07-11-…-mock-consumers`, `2026-07-17-…-curve-freshness-r6r7`;
  maintainer-local, unpublished). Cheap because the 0.12.0 §8 verified-snippet mechanism ships.
- **Change:** `keel fix-ledger <spec>` re-resolves each fold-ledger row's anchor by searching its
  recorded snippet, reporting (never guessing) rows without one; plus the fold protocol's terminal
  step — dry-run check-ready on the folded spec before the confirmatory pass.
- **Ordering / tension:** adding a command while two are advertised and dead is the defect
  KEEL-B05 exists to close. Land after KEEL-B17 and KEEL-B30, not before.
- **Effort:** M · **Source:** `[triage Q10a/b]` `[review]`

### KEEL-B23 — Stop pinning template needles to exact whitespace

- **Cause / evidence:** `tests/test_templates_valid.py` pins exact prose substrings with a raw
  `assert needle in text`, so any line re-wrap silently breaks a guard test; it bit during the
  0.13.0 release build (`2026-07-10-keel-0.13.0-self-build`; maintainer-local, unpublished) and two
  independent design verifiers flagged the class.
- **Change:** normalize whitespace on both sides of the needle comparison
  (`re.sub(r'\s+', ' ', …)`) — the drift guard already does this for clause identity. Removes the
  fragility rather than warning about it.
- **Effort:** S · **Source:** `[triage Q12a]`

### KEEL-B24 — Widen the review checklist's Tests item with the adequacy question

- **Cause / evidence:** the checklist asks whether tests exist, not whether they would fail if the
  load-bearing predicate were subtly wrong (`2026-07-11-…-w7-corpus-v3`; maintainer-local,
  unpublished).
- **Change:** rewrite the existing Tests item rather than adding a sibling. Rides the same file edit
  as **KEEL-B33**.
- **Effort:** S · **Source:** `[triage Q7d]`

### KEEL-B25 — Carried watch rows (no work until a second report)

- **Cause / evidence:** the triage carries these as watches, each grounded, none yet reinforced.
  Recorded so a second report promotes rather than re-derives.
- **Rows:** W1 transport-coupled deliverables (no non-protocol bytes on a shared protocol stream);
  W2 committed-representative-evidence provenance; W4 an A6 WARN on a claim-shaped anchor carrying
  no snippet; W6 a one-line DoR-subsumption verdict on design-only rounds; W7 invocation-recipe
  discoverability — if a second report hunts, surface the recipe in the failure path, not in more
  docs; W8 `spec-hash` scope versus the gate's own advice — `_status_currency_warning`
  (`check_ready.py:1007`) tells the author to update `Status:`, and doing so invalidates the
  certification the same run just verified, narrowest fix being to exclude the header `Status:` line
  from `spec_hash` (`check_ready.py:185`) exactly as the certification section already is; W9
  multi-round pre-mortem artifacts — state that only the newest round's `Spec-hash:` binds.
- **Change:** none yet on the remaining rows. Promote each on a second report.
- **Status:** **W8 shipped** ahead of a second report — it was not a preference but a self-defeat:
  the warning's own instruction invalidated the certification the run had just verified, so the
  header `Status:` line left `spec_hash`. The recorded-hash migration it forces (a one-time W5
  wave across sibling repos) is named in `docs/cli-reference.md`, and the hash's scope is now
  pinned per gate minor, as W1's kit-skew semantics already were.
- **Effort:** S · **Source:** `[triage W1/W2/W4/W6/W7/W8/W9]`

### KEEL-B26 — Publish the ratio of author-loop runs to full-gate rejections

- **Cause / evidence:** `[research]` names this the sharpest question for the category — a gate with
  no rejections is either perfectly upstream-disciplined or vacuous. Partial evidence exists (a
  fresh stamp fails; the adversarial panel found and fixed under-enforcement; the post-0.12.0 field
  round recorded no vacuous gate) but all of it is maintainer-local or synthetic, and no public
  artifact shows a believed-ready spec being rejected.
- **Change:** answer it from KEEL-B07's ledger, split by `--structure-only` author-loop runs
  (expected to fail often and cheaply) versus full-gate runs on a spec submitted as ready. Publish
  the ratio in `docs/evidence.md`. It is the one number that strengthens the observational claim
  without reopening the comparative one ADR-0015 retired.
- **Ordering:** unblocked — KEEL-B07 shipped and `keel gate-health` already prints the split. What
  is missing is only the runs: ~20 real ones, which is a matter of using the gate, not building
  anything. Publishing the ratio before then would be publishing a number about this repo's own
  test suite.
- **Effort:** S · **Source:** `[review]` `[research]`

### KEEL-B27 — State the design contrast against the named alternatives, artifact by artifact

- **Cause / evidence:** `[research]` names the first question a reviewer asks — what does this do
  that the community-default spec framework does not, concretely, artifact by artifact — and records
  that no named framework in the category has published comparative ROI either. The audit's answer
  is already available and specific: those frameworks ship templates, checklists and analysis
  prompts; keel ships a binary that exits 1 on a malformed spec and refuses a certification whose
  saved artifact disagrees with the reviewed revision. Doctrine §1's table still frames the method
  against a generic agentic flow — the comparative posture ADR-0015 retired at the headline.
- **Change:** a short committed note (or a doctrine §1 rewrite) stating the contrast **as a design
  contrast, not a quality comparison**, and leading with `check-ready` + B2. Relabel or qualify the
  §1 table accordingly. Must not reopen the retired claim; `tests/test_claim_currency.py` is the
  guard that keeps that honest.
- **Effort:** S · **Source:** `[research]` `[review]`

### KEEL-B28 — Calibrate the `apply-method` trigger description

- **Cause / evidence:** `[research]` Gate 5 — over-broad descriptions pollute context, over-narrow
  ones never fire, and both are failures; the suite's explicit negative space is a genuine strength
  and it is testable. `apply-method` is the only routing surface keel owns, and its negative space
  ("Do NOT use for one-off scripts… below the coordination threshold") has never been measured.
- **Change:** a trigger dataset with a sealed holdout, scored for recall on prompts that should
  route into the method and specificity on near-misses that should not. Small, and it is the one
  measurement that says whether the router works at all.
- **Cross-review note:** scope this to the specificity half and the negative space, or gate it on
  the skills collection's CRAF-B29 first. That row records the same shape already measured across at
  least five skills — high recall on the phrasings a description was written against, near-zero on
  held-out paraphrases — and concludes it is a dispatch-layer ceiling that per-skill description
  tuning does not close. Run as written, the recall half of this item would most likely reproduce
  that pattern and then attribute it to `apply-method`'s wording, buying a description rewrite that
  the collection has already argued cannot work. What CRAF-B29 does *not* cover, and what is
  genuinely keel's, is the specificity question: whether "do not use below the coordination
  threshold" actually keeps the router quiet on one-off scripts and single short artifacts. That
  half is worth measuring on its own and is cheaper than the full dataset.
- **Effort:** M · **Source:** `[research]` `[cross-review]`

### KEEL-B44 — Record the series skeleton's status as a registered model-tier mirror, in its own vocabulary

- **Cause / evidence:** `src/keel/templates/series-toml-skeleton.md` pins model-tier example strings
  and is a registered site in the operator's model-refresh table (maintainer-local, unpublished),
  walked whenever a model ships — but nothing in this repo says so: not the file, not a test, not
  this backlog. It is the only registered site in the
  suite whose own project carries no row for it: the eval harness has FATH-B16 (three undated
  hand-maintained mirrors, no tripwire, no test), the bound series orchestrator has CONV-B14 (four
  sites, no age tripwire), and the skills collection has CRAF-B13 (the walk binds to prose the tools
  cannot locate). Two things make the silence worse here than a missing row usually is. First, this
  file's tiers are deliberately **model-family names** (`haiku`, `sonnet`) rather than the
  orchestrator's abstract tier words — the skeleton says so under "Tier vocabulary" — so a refresh
  that greps for the sibling vocabulary passes over this file without a hit and reports clean.
  Second, **KEEL-B32** edits this exact file, so the next hand to touch it belongs to someone with
  no reason to know it is a mirror. `[cross-review]`
- **Change:** state the mirror status where the vocabulary is already explained — one line under
  "Tier vocabulary" naming the file as a walked mirror site and repeating that the family-name
  vocabulary is deliberate and is translated at the orchestrator binding
  (`method-bindings.md`), not here. Do **not** add a lineup table, a price row or a sync date: the
  skeleton carries examples, not a lineup, and giving it a lineup would add one more site to
  re-sync in exchange for nothing. If a tripwire is wanted, the cheap one is a template test
  asserting the `tier` values are family names and not API model ids — it fails the day someone
  pastes a lineup in, which is the actual failure mode, and it costs no maintenance between
  lineup changes.
- **Ordering:** land with or before **KEEL-B32**, which touches the same file.
- **Effort:** S · **Source:** `[cross-review]`

### KEEL-B45 — Received: a shared test module is where one-concern decomposition collides with itself

- **Cause / evidence:** routed here by the eval harness, whose own backlog closes the row as a
  wave-decomposition lesson rather than a surface of its own (FATH-B44, from a
  model-selection rollout recovery). Several one-concern PRs in one wave each appended a test class
  after the same anchor in a shared test module; every one of them was correct in isolation, and the
  second to merge conflicted. It was routed to the method tooling's decomposition guidance and no
  row was opened here, so the lesson is currently held only in the project that suffered it.
- **Why it is keel's:** the collision is produced by keel's own rule, not by a lapse from it.
  Doctrine §3 requires one concern per PR and `spec-template.md`'s manifest carries a "One concern?"
  column; obeying both while several sections' tests share a module puts every PR's diff at the same
  file offset. The guidance that avoids it is placement, not scope — stack the PRs, or append at
  end-of-file rather than after a shared anchor, when a wave's PRs touch one test module.
- **Change:** one clause at the Decompose row's existing "one concern per PR" text (doctrine §3), or
  in the manifest section of `spec-template.md` — one home, not both, per KEEL-B06's budget and
  KEEL-B32's one-authoritative-home rule. This is a candidate for **KEEL-B10**'s profile file if
  that lands first and the clause reads as lane-specific rather than general. If on inspection it is
  judged ambient — the kind of thing a competent decomposition produces unprompted, which is the
  test **KEEL-B33** applies to the templates — decline it here and record the decline, so the
  routing project gets an answer either way rather than silence.
- **Effort:** S · **Source:** `[cross-review]`

---

## Retire / fold candidates

Features the audit sentenced. Each names its replacement; nothing is removed without one.

| ID | Claim | Replacement | Evidence | Effort | Source |
|---|---|---|---|---|---|
| KEEL-B29 · **shipped** 2026-08-11 | Delete `hooks/hooks.json` — it ships `{"hooks": {}}`, is absent from the plugin-reference entry-point table, and is not covered by the entry-point coverage test, while the doctrine names hooks as one of the two deterministic machines | Native hooks in `settings.json`; if a hook is wanted, the concrete candidate is a PostToolUse hook on Edit/Write to a bound spec path running `keel check-ready --structure-only` | Feature review; keel's own bindings sheet records it "not bound" | S | `[review]` |
| KEEL-B30 | Remove `keel budget-drift` — per-wave economic policy is the orchestrator's residual value, not the method layer's, and ADR-0003 records this gate was scaffolded with no cited motivating failure | The bound series orchestrator's per-phase budgets and economy readback, plus one pointer line in the series skeleton | Feature review; ADR-0003 thinness rule | S | `[review]` `[research]` |
| KEEL-B31 | Delete `scripts/external_review/` — a second bespoke multi-vendor client in a repo whose own ADR-0003 forbids engine-flavoured execution (it is gitignored for that reason), and it saves N independent reviews without comparing source provenance | The operator's existing multi-model research tool, which already does fan-out with an epistemic sidecar; keep the *practice* (a skipped enrichment panel is a recorded decision) in CONTRIBUTING | Feature review; visible drift between its README and its code | S | `[review]` `[research]` |
| KEEL-B32 | Compress five prose sites to one-line pointers — the same text has four homes, and ADR-0016 §2 already decided the operator close is prescribed once with one-clause references everywhere else | The one authoritative home in each case: `docs/getting-started.md` and doctrine §3 for `apply-method`'s setup and subset-of-phases paragraphs; the `apply-method` skill for `/keel-apply`'s body; doctrine §2 and `definition-of-ready.md` Part B for `/keel-premortem`'s round-economy and operator-close paragraphs; the kit README reduced to its slot→file and upgrade→file tables; doctrine sharpening 5 reduced to naming the axes with a pointer to `pre-mortem-prompt.md`; the series skeleton's `[budget]` block demoted to an orchestrator pointer | Feature review; `/keel-premortem` violates its own governing ADR | M | `[review]` |
| KEEL-B33 · **partly shipped** 2026-08-12 (the two consumed files, in the cross-review's form: nothing cut, ordering and delegation made explicit; `adr-template.md` untouched and now *gained* the ADR-numbering trap relocated out of the spec-template, so its cut needs re-arguing against a fuller file) | Cut ambient content from three kit templates — generic review, linter policy and ADR structure are what a strong model and native review produce unprompted | `adr-template.md` → four headings plus the two non-ambient clauses (name the invariant explicitly; never edit an Accepted ADR); `review-checklist.md` → the method-specific and trap-derived items, with generic review explicitly delegated; `definition-of-done.md` → foreground the two non-inferable traps (a wrapped tool must have run to completion; every referenced artifact is `git ls-files`-tracked) and mark the generic block as the bind-your-commands stub it is | Feature review; `[research]` measures lint leakage at 62% and skill leakage at 35% of studied repos | M | `[review]` `[research]` |
| KEEL-B34 | Fold `docs/phases-reference.md` and `docs/concepts.md` into doctrine — eleven reference docs plus doctrine plus sixteen ADRs for four commands, one skill, one agent, eleven templates and seven CLI commands | Doctrine §3 as the only home for the phase table; doctrine §5–§6 for the three-scopes framing. The glossary is the counterexample and stays — without it a reader cannot parse the gate's own messages | Feature review | M | `[review]` |
| KEEL-B35 | Delete `tests/test_gate_contracts.py` once both stubs are resolved — it exists to keep "deferred" honest, and has nothing left to pin when nothing is deferred | The built `bind-check`'s own tests (KEEL-B17); the budget-drift arm goes with the command (KEEL-B30) | Feature review | S | `[review]` |
| KEEL-B36 · **shipped** 2026-08-11 | Clear the untracked `.remember/` directory from the checkout — a hand-rolled memory-bank surface (hook error logs, dated memory files, a today/done convention) that ships with nothing and is dead weight in the tree | Native persistent auto-memory | Operator observation; not a keel feature — housekeeping, do it when the enclosing tool is next reviewed | S | `[review]` `[research]` |

The pre-mortem agent body and its 34-marker drift guard are also sentenced; that work is
**KEEL-B02** in Now, because everything else touching the directive text is sequenced behind it.

### Cross-review notes on five of these rows

Added by the 2026-08-11 cross-project pass. None of them reverses a sentence above; each adds a
sequencing or scope constraint the row could not see from inside this repo. `[cross-review]`

- **KEEL-B30 and KEEL-B32 — the tier vocabulary stays; only the budget block goes.** Both rows
  touch the series skeleton and neither separates its two contents, so "per-wave economics belong
  to the orchestrator" reads as covering the tiers too. It does not. The `[budget]` block demotes
  to an orchestrator pointer; the tier vocabulary stays here, because it is the method's own
  family-name words rather than any one orchestrator's, and translating it is the binding's job
  (see **KEEL-B44**). Say that in both rows rather than leaving it to the reader.
- **KEEL-B30 and KEEL-B32 — do not land the skeleton edit inside the orchestrator's measurement
  window.** The bound series orchestrator has a live measurement counting whether per-PR
  governance overrides are used at all (CONV-B18), and a retirement of its per-model fan-out
  gated on that count coming back near zero (CONV-B33). Both readings assume keel keeps emitting a
  tier per PR. Editing the skeleton mid-window makes a near-zero reading a record of our own edit
  rather than of the feature's merit, and would retire machinery on an artifact of our own change.
  Sequence after
  the window closes, or tell the orchestrator's owner the window is contaminated — either is fine;
  doing neither is not.
- **KEEL-B31 — sequence the deletion behind the replacement's transport work, and name the CLI.**
  The named replacement does not currently complete over its primary transport. Six invocations
  aborted at the client's idle window while the same questions succeeded 3/3 via that tool's CLI,
  and two full runs lost their synthesis stage in the same week these briefs were written. Its own
  backlog carries the fixes — progress emitted over the channel so a long run is not silence
  (MANT-B01) and the retry backoff capped below the caller's idle budget (MANT-B02), the latter
  being what actually removes the guaranteed abort. Delete `scripts/external_review/` after those
  land, and name the CLI as the working invocation path in the CONTRIBUTING note that keeps the
  practice. Otherwise this row replaces a working bespoke client with one that aborts, and the
  practice it preserves becomes unrunnable at the moment it is written down.
- **KEEL-B32, KEEL-B33 and KEEL-B34 — the kit now has two external consumers by reference.** Two
  sibling projects are retiring their hand-copied method directories and pointing at this kit
  instead (FATH-B37, MANT-B48). That turns these three rows from internal tidying into an
  interface change, and two files need naming before they are cut. `review-checklist.md` is the
  planned pointer target for the eval harness's bank check-ready guidance, which is being moved
  from a local copy to a reference here — so KEEL-B33's cut of that file removes text a consumer
  is about to depend on. Keep the method-specific and trap-derived items intact, and make the
  delegation of generic review explicit in the file rather than silent, so a consumer arriving by
  pointer can see what was delegated and what was kept. `definition-of-done.md`'s concrete gate
  commands are the other: the research runner must move its own bindings into its `CONTRIBUTING.md`
  before its retirement lands, and its backlog already records that ordering as a precondition —
  KEEL-B33's "bind-your-commands stub" framing is what makes that move clean, so the two changes
  should be visible to each other. Neither is a reason to hold these rows. Both are a reason to
  land them with the consumers' sequencing cited, and to treat the kit files as having readers
  outside this repo from now on.

---

## Declined

Recorded with reasons so they are not relitigated. Effort is not estimated for declined items.

| ID | Proposal | Why declined | Source |
|---|---|---|---|
| KEEL-B37 | Grant the certifying reviewer write access to the certification block, so it is stamped by its owner instead of hand-copied by the caller | The agent is read-only by contract (`agents/pre-mortem-review.md:104` — recording the block is the caller's step), and that boundary is what makes B2's forgery cost meaningful. The real ambiguity the proposal names — a block recording what was owed but not what was paid — is answered operator-side by **KEEL-B15**'s discharge line | `[triage]` |
| KEEL-B38 | A `--content-only` mode certifying a spec keel did not scaffold | Grounded as contradicting a shipped contract rather than merely unbuilt. The question it raises is real and gets recorded as a boundary in **KEEL-B18**'s ADR, not patched into the gate | `[triage]` |
| KEEL-B39 | Promote project-specific residue from field rounds into the kit | Stays in the consuming project's own checklist — feedback flows up, house rules do not flow down. ADR-0003 consumer-agnosticism | `[triage]` |
| KEEL-B40 | A gate on the version the DoR skill pins | Commands already resolve through the serving bundle; the spec-side half is the shipped kit-skew WARN; the authoring-side residual is **KEEL-B17** | `[triage]` |
| KEEL-B41 | Turn observed environment and harness faults into keel gates — an application-control policy intermittently blocking a built wheel on Windows, a classifier degrading after a mid-session model switch, a platform outage forcing an agent through a wrapper, session-limit resets during an external review | Routed to the operator environment; keel's ledger stays method-correctness only. The documented module-form invocation already covers the Windows case, and the one keel-side residual (a retry-once hint in the CLI error) is not worth a gate. No orchestrator or engine faults were reported this round | `[triage]` |
| KEEL-B42 | Reopen the retired comparative claim by building a comparative evidence bank | ADR-0015 retired it as unmeasured and priced the reopening ($150–400 matrix, $20–40 pilot, maintainer-local, no date); `tests/test_claim_currency.py` pins the retirement. The affordable measurement that *is* authorable now is **KEEL-B09**, whose unit is one spec review rather than a governed wave. `[research]` notes the bar applies symmetrically — no named framework in this category has published comparative ROI either | `[review]` `[research]` |
| KEEL-B43 | Grow keel into the orchestration layer — adopt or re-implement a published orchestration spec inside this repo | Out of scope by ADR-0003: keel is the method, the bound engine is the runtime, and `[research]` finds the defensible design is a thin control plane over commodity harnesses. **KEEL-B30** removes the one place this layering already leaks | `[research]` |
