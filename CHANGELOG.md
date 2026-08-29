# Changelog

All notable changes to keel. Format: Keep a Changelog; versioning: SemVer. An entry that
moves a machine-parsed contract — the gate ledger’s schema, a CLI exit code — carries the
literal marker `(consumer-affecting)`; the changelog gate’s marker arm watches for it.

## [0.18.0] - 2026-08-29

The rest of the delivery wave, and the correction of its release record. Wave 4 landed as a
stack of six PRs appending to one release section, and v0.17.0 was tagged mid-stack at the
section-cut commit — so most of the machines that section described were not in the tag that
named them. This release ships them under their own heading, and turns the incident into
standing checks: a release tag is annotated and its section's entries are locked once the tag
exists, a release cut must move the newest heading strictly forward, and a built command can no
longer stay a "stub" in prose.

### Added

- **`keel bind-check` is built, and `check_budget_drift` is not** (ADR-0018, `bindings.py`).
  ADR-0003 deferred both "until a real failure demands it", and deferral was the live state for
  fourteen releases. Two field failures now meet that condition, both the same shape — the binding
  sheet answers when asked and never fires: a phase with a six-plus-PR blast radius across three
  repositories was specified with no Definition-of-Ready and no pre-mortem and nothing accused
  ("the bindings sheet lived in a fourth repository and is read by no mechanism at phase start"),
  and the executor was left to a conditional the session resolved by what was already in context.
  The binding column is resolved by **header** — `This project` when the table has one, else the
  last column — because the sheets that exist are three-, four- and two-column and a positional
  rule reads a worked example as a binding. **Three states, not two**: an empty cell fails, and
  `not bound — <reason>` WARNs, which is the declared idiom this repo's own sheet uses for three
  slots. An emptiness-only predicate would have failed the blank scaffold and PASSED the one real
  record — the exact inverse. Findings carry no check letter, and ADR-0018 records why: `CHECK_IDS`
  is the spec gate's catalogue, and the corpus that would have to control a new letter stages
  specs. `check_budget_drift` stays stubbed; no failure cites it and its backlog disposition is
  removal.
- **`keel survey <dir>`** (`src/keel/survey.py`): the phase-boundary sweep — which spec-shaped
  documents in a design directory carry no certification? `check-ready` cannot answer it (it gates
  one spec, and its 0/1/2 contract is pinned), so this is its own verb. **Spec-shaped** is stated
  rather than implied — a numbered-sections or PR-manifest heading — because a design directory
  also holds triage documents, ADR drafts, saved pre-mortem artifacts and requirements registers,
  and without the predicate the sweep either false-fails on all of them or becomes advisory prose.
- **`keel re-anchor <spec>`** (`src/keel/reanchor.py`, `docs/cli-reference.md`): the correction
  the gate already computes, applied instead of described. Defaults to the fold ledger, which sits
  inside the span `spec_hash` removes — so a repair cannot invalidate the certification it serves,
  and a test asserts the hash is unchanged across a default pass. `--body` also repoints prose
  anchors and says out loud that the hash has moved; `--check` writes nothing. Every refusal is
  reported by name: a repair that guesses would be worse than the manual `sed` it replaces,
  because the row would then pass the gate while pointing somewhere the fold never happened.
- **The changelog gate grows a version arm and a marker arm**
  (`scripts/changelog_currency.py`, `ci.yml`). The kit arm is unchanged. Version arm: a PR
  whose CHANGELOG gains a new newest heading must move the version strictly forward — the
  nine-site version lock then holds every site to that heading in the same CI run. Marker arm,
  advisory: a diff touching a contract-surface file (the gate ledger's schema, the CLI's
  exit-code surface) should carry the literal `(consumer-affecting)` marker on an added
  CHANGELOG line — the convention the header above now defines. Pure predicates, tested in
  `tests/test_release_flow.py`.
- **Tag discipline, as tests** (`tests/test_release_flow.py`, CONTRIBUTING). From v0.18.0 a
  release tag is annotated (`git tag -a` on the release's closing merge commit, so the tag can
  say when it was laid) and a tagged version's CHANGELOG entry set never changes after the tag
  exists — the two assertions the v0.17.0 mistag walked past. Red-proved with a throwaway
  lightweight future tag before landing.
- **A stub claim has one home** (`keel.cli.STUB_COMMANDS`, `tests/test_claim_currency.py`).
  Wave 4 built `bind-check` and merged CI-green while README, one cli-reference paragraph and
  CONTRIBUTING's enforcement table still called it a stub — `changelog_currency.py`
  deliberately excludes those paths, so nothing fired. Now the docs that enumerate stubs are
  held to the CLI's own stub set in both directions, and README stops hand-enumerating the
  check set entirely in favour of the cli-reference table a test already pins.
- **A commit-msg lane** (`.githooks/commit-msg`, `.pre-commit-config.yaml`): Conventional
  Commit subjects (the types include `release`) and no AI-attribution trailers, enforced at
  commit time through the same tracked-hooksPath pattern as the pre-commit lane.

### Changed


- **An amendment is recomputed, not declared** (W7, `check_ready.py`). `spec_hash` answered the
  question "did the certified content change?" by removing a growing list of spans, one heading
  per incident. It stops growing here, and gains nothing: when the recorded hash disagrees with the
  current one, B2 recomputes with **every** declared `## Amendment` span removed and compares that.
  Agreement proves the certified content is intact and the difference is an addition the reviewer
  never saw — a different fact from "certified against an earlier revision", and a **derived** one.
  The design this replaces was a declared `Amends spec-hash:` field, which compares two literals
  the author types: it proves nothing and lowers the forgery cost to one copy-paste, where today's
  W5 at least compares a recorded literal against a recomputed digest. Every span, not the first,
  because the release discipline makes an amendment the sanctioned form for every
  post-certification change. **One state is excluded**: an operator-accepted CONDITIONAL-CERTIFY,
  where the Definition-of-Ready sheet already calls the mismatch the expected honest state of that
  close — without the exclusion the new letter would eat a signal the method deliberately keeps.
  `spec_hash` itself is unchanged, so the amendment's own text is still hashed and the block stays
  tamper-evident; the two hashes share one implementation, because the first cut reimplemented the
  removal, dropped the two spans the canonical hash has always removed, and could never have fired.
- **A fold-ledger anchor's identity is its snippet; the line is a coordinate** (W6,
  `check_ready.py`). Nine field reports across two rounds wrote the same throwaway re-anchoring
  script — three cycles over sixteen rows in one session, one of them producing a malformed row
  from a slipped `sed`; five cycles across two specs the next day; twenty-one rows after one
  section rewrite. When a ledger row's snippet is not on the line it cites but IS on exactly one
  other line, the fold is recorded against real, locatable content and only the coordinate is
  stale: that is now a warning naming the corrected line, not a failure. Scoped three ways, because
  each exclusion is a case where the repair would be a guess — a **weak** snippet (under twelve
  non-space characters) can match a coincidental line, a **range** anchor cannot be repaired at all
  (the snippet's original offset inside the window is unrecoverable, so the shift is
  underdetermined), and a snippet on no line or on several has nothing to resolve to. **A6 prose
  anchors are untouched**: they are the author's own citations rather than a machine-repairable
  ledger, and `_snippet_delta` returns a delta precisely on the unique-match case, so downgrading
  them too would have left the drift-delta cause key with no producer at all.
- **The report unit is about findings, not about violations** (`models.py`, `check_ready.py`).
  `Warning` gains the `cause` key `Violation` already carried, `count_causes` counts both kinds,
  and `Probe.causes` is computed over every finding of a check rather than over its violations
  alone. Without it, W6 moved the census's signature case — N ledger rows drifted by one uniform
  edit — onto a path where `causes` degenerated to `fired` and the grouped note disappeared
  entirely: the exact regression 0.15.0's report unit exists to prevent, reintroduced through the
  warning door, and silent, because the only uniform-drift fixture uses out-of-range rows that stay
  violations. Whether a finding blocks and how many defects it represents are independent
  questions. Caught by the round-2 re-gate of this wave's own spec, in code that had already
  shipped to a branch.
- **What a gate must observe** (`definition-of-done.md`). A blind post-execution audit of seven
  governed series — 68 findings, three BLOCKER, about thirty minutes, no execution — answered YES
  to "could a wrong PR have gone green?", and the causes were gate-**authoring** classes nothing
  constrained. Four items join the Definition of Done's field-derived group: a red companion is a
  committed artifact the gate executes, never a transcript or a commit-message narrative (four
  series accepted prose, one of them citing a mutation that had come back green); a change that
  adds to a counted set pins that set's inventory, because a deliverable that never arrives is
  indistinguishable from one that works (a pinned deliverable vanished with both its checks green,
  and five production bindings went missing without noise); a check never regenerates in place what
  it validates (four series' drift gates rewrote the corpus over the worktree, so any red
  self-heals on the second run); and every command the spec's Gate-commands section names maps to a
  check that runs or carries a named deferral (an independent oracle existed as a wrapper that
  skipped always, in two series, and was delivered with a syntax error inside a third). The
  Definition of Done is not a capped body; these join the two field-derived items already there,
  and the generic bind-your-commands stub is untouched. The series-file half of that audit —
  gate derivation, phase-scoping, review budget — is the orchestrator's layer and is routed out
  (ADR-0003).
- **An anchor that leaves the repository fails rather than expanding to an in-repo twin**
  (`check_ready.py`). Half of the backlog row's premise was already true — the filesystem resolves
  the parent segment, so `../sibling/path.py:12` verifies its snippet when the sibling is checked
  out beside this repo. The defect was the other branch: when the sibling is absent the basename
  search rglobs THIS repository and, on a unique hit, silently retargets the citation to an
  unrelated file of the same name, with a warning reading "the expansion is unique today". That is
  the vendored-twin trap 0.16.0 closed, reached through a different door. No new letter: the
  fixture corpus stages one tree and cannot stage a sibling, so the absent-sibling case earns an
  ordinary A6 mutant instead.
- **The kind-selected sheet gets a selector** (A14, `check_ready.py`, `pre-mortem-profiles.md`,
  `spec-template.md`). `pre-mortem-profiles.md` opened by saying its material was "dispatched only
  for the kind that needs it", and no selector existed: `Kind:` declares decomposition shape, not
  subject, and the two taxonomies had been collapsed onto one field name. The sheet was selected by
  the author remembering to read it. A `- **Profile:**` header field now declares the subject axis
  — `code` | `data-pipeline` | `measurement` — and **A14** validates it. Its own letter rather than
  a widening of A0, because A0's candidate count is the `Kind:` field alone: a Profile-only header
  would have fired a check with a zero denominator, and A0's existing mutant would have satisfied
  the new detector's positive-control obligation vacuously. Verify-when-present, and the scaffold
  ships the field RESOLVED to one token — a menu is read leading-token-first, so reordering one
  silently changes what every untouched scaffold declares.
- **The data-pipeline profile**, in that dispatched-on-demand home: population characterized over
  the discriminating field before the schema is assumed, a gate per named heterogeneity axis, a
  pilot constructed to contain one instance of each, an exact write-side reconciliation and a read
  check that DISCRIMINATES, every pinned clock pair evaluated against every read predicate, and
  every staged literal checked against the closed vocabulary that owns it. Seven field reports over
  two rounds, each a defect that reached production or a paid run past a green Part A and multiple
  blind rounds. *Displacement:* the header's two declarations now share one contract note and the
  standalone measurement note is gone — the notes are at 499 of their 500-word cap, one word under
  where this wave found them and one note fewer. **The fenced directive block is not touched**: it
  carries no selector line, and adding one there is the net-new directive prose KEEL-B09 gates.
- **The shipped bindings template's Orchestrator table gains its `This project` column.** It
  carried only the worked example while the sheet's closing line said "bind every row", so those
  four rows were slots no gate could read. An existing adopter's copied two-column table is
  unaffected: the header rule reads its last column correctly.
- **A fold-ledger row has one owner.** A6 and A11 scan the whole document, so they were
  re-checking the ledger's anchors under prose semantics — the same defect reported twice, by a
  check that cannot repair it, with a second fire in the hit-rate ledger. The ledger sub-table is
  masked out of their scan, offsets preserved.
- **The gate ledger's schema moves to v3.** An A12 failure class became a warning, so A12's and
  W6's `fired` counts are not comparable across that boundary; the ledger's own contract says a
  count must never be read across a version boundary silently.
- **The Definition-of-Ready sheet's budget is split in two, because it was two bodies sharing one
  number** (`tests/test_body_budgets.py`, `CONTRIBUTING.md`). A test makes a new check letter
  MANDATORY in the sheet's reference block, while the whole sheet was capped at the size it
  happened to be — so every check the gate gains cost prose budget forever, for a lookup table
  nobody reads end to end, and the two rules would eventually deadlock. The sheet's **prose** keeps
  a word cap (950, set at what it measures); the block is capped **per check entry** at its
  measured maximum (61 words) instead of in total. A re-aim, not a raise: the catalogue may grow,
  a line may not sprawl, and a second assertion holds that nothing but a catalogued check parses as
  an entry, so the per-line cap cannot be dodged by an unlettered line.

### Fixed

- **The release record around the v0.17.0 mistag.** The tag was not moved — a public tag that
  moves is worse than a mislaid one, because every clone that fetched it keeps the old object
  silently. Instead: the entries for work the tag never contained moved from [0.17.0] into this
  section, [0.17.0] below now describes exactly what `v0.17.0` ships and says so, and the
  version-site count's stray "eight"s (two docstrings, a CI comment) now defer to
  CONTRIBUTING's "Release discipline" section, the one home of that enumeration.
- **ADR-0019** folds the July agent-surface equivalence screen's verdict
  (no-gross-degradation, at screen strength) out of an unmerged branch tip into the record,
  and closes both stale eval branches.

## [0.17.0] - 2026-08-28

The delivery wave. Every item here is a machine the method assumed it had: text it dispatches but
cannot show you, a ledger whose identity lives in the fragile half of its own anchor, a hash that
answers "did the certified content change?" by growing an exclusion list, a bindings gate deferred
since ADR-0003, and a kind-selected sheet with no selector. The wave lands as a stack of small PRs
against one release section; this entry grows as they land.

*Correction, recorded at the 0.18.0 cut: v0.17.0 was tagged at this release's section-cut
commit, and the wave's remaining PRs then merged while appending their entries here — so the
published tag did not contain most of what this section described. Those entries now live under
[0.18.0], the release that ships them; what remains below is exactly what `v0.17.0` contains.
The tag itself was not moved, and `tests/test_release_flow.py` now fails a released section
whose entries change after its tag exists (v0.18.0 onward).*

### Added

- **`keel show <name>`** (`src/keel/show.py`, `docs/cli-reference.md`): the kit's own bodies,
  printed from the serving bundle. `checks` is the Part-A reference block, `directive` is the
  fenced prompt dispatched on every pre-mortem pass, and any kit template comes back by stem.
  Three field asks in one corpus were requests for text that **already ships in the version the
  operator was running** — the round-≥2 re-gate posture, the one-verdict-per-artifact idiom, the
  module-form invocation recipe. None was an absence; each was a delivery that never arrived,
  because the method's text lives in files a session dispatches or scaffolds and never reads back,
  while a periodic post-hoc telemetry pass over the window's transcripts puts the CLI at 52 of 53
  keel invocations against one invocation of the skill that carries the method. `show` therefore
  adds **no text**: it reads the shipped file at run time, and a test asserts the projection is
  byte-identical to the sheet's block rather than restated in code, because a drifted copy of the
  directive would be worse than no command. `doctrine` is deliberately not a name — `docs/` is
  outside the built distribution, so serving it would mean copying it into the package, which is
  the duplication this command exists to avoid.
- **A coverage gate for `docs/templates-reference.md`** (`tests/test_templates_valid.py`): the
  third of three, and the one that was missing. A new command could not land undocumented and
  neither could a new plugin entry point, but a new kit template could — and `keel init` copies it
  into every adopting project. Same shape as the other two: glob the shipped set, never a
  hand-kept list.

## [0.16.0] - 2026-08-28

The conformance release: the owner's order becomes an artifact the gate can point at, and the
gate's own failure messages start naming the form they accept. Both come from the same reading of
the field round — the method's knowledge reaches a session through the CLI and the scaffold, and
anything that lives only in a template's prose or a doc page is, empirically, not delivered. A
periodic post-hoc telemetry pass over this window's session transcripts puts the CLI at 52 of 53
keel invocations, against one invocation of the skill that carries the method.

### Added

- **The requirements ledger, and DEVIATED as a state a session cannot grant itself** (A13,
  `src/keel/templates/requirements-register.md`, `check_ready.py`). A programme's opening
  instruction — the sources are read through the config layer — was replaced by hand-rolled
  readers as an unlabelled design decision. Three later specs certified Ready and four blind
  pre-mortems returned about seventy real findings; none could see the substitution, because each
  attacked the spec against the code and the data contracts and the ask existed nowhere a reviewer
  could open. The order was the one load-bearing input to this method with no durable artifact.
  Now: a register in the programme's repo holding the orders **verbatim** with stable `RR-<n>`
  ids; a `- **Requirements:**` header field naming it; a `## Requirements ledger` disposing every
  entry to a §N, `DEFERRED — <trigger>`, `OUT-OF-SCOPE`, or `DEVIATED`; and A13 failing a spec
  that leaves an entry unaccounted. A13 does not judge whether a disposition is RIGHT — that stays
  Part B (ADR-0002) — only that none is missing. **DEVIATED is the exception:** the other three
  are the author's call, and a departure from the owner's own order is not, so a DEVIATED row
  naming no ratification fails. Until the owner answers, the honest state is a spec that does not
  pass — which is the state that gets the question asked. Silent on a spec that declares no
  register: candidates 0, `n/a` in the hit-rate ledger, which is a different fact from a pass. The
  field ran this shape by hand on two specs before it was built and reported ~15 lines per spec,
  and that it was what let a post-compaction resume re-derive scope without relitigating it.
  Positive controls: an unaccounted order and a self-ratified deviation, one edit each, firing
  exactly A13.

### Changed

- **The failure path names the form the parser reads.** Three field classes, one cause: the gate
  said what was missing and never what it accepts, so the accepted form was learned by grepping a
  sibling spec. A2 now names the literal marker it searches (`acceptance criterion`) and the
  paragraph rule that makes a criterion split from its marker read as empty — a section that named
  the same idea in other words read as absent, with nothing in the message to say so. A8 names the
  cross-document escape it has honoured since 0.14.0 (a `.md` cue, a standards id); three reports
  rewrote the typographic convention out of their prose to satisfy the linter instead.
- **A unique basename match inside a vendored tree is refused, not expanded** (W3, A6/A11/A12).
  KEEL-B04 made expansion possible; in an estate that vendors its dependencies the copy is the
  likeliest unique match, so the WARN read "resolved, carry on" over the wrong file — an anchor
  that resolves to a file that exists and is wrong is worse than one that fails, because the
  warning closes the question. `dbt_packages` and `vendor` join the vendor set, and the violation
  names the twin and its directory class.
- **The invocation is a binding, and it resolves instead of pinning** (`method-bindings.md`). A
  consumer's bindings pinned `…/cache/keel/keel/0.15.0` against a cache holding 0.13.1 and 0.14.0:
  the prescribed command failed on a path that did not exist. The template never showed how to
  write that line, so every consumer improvised one, and the improvised form is the one that rots.
  Three forms that resolve — `${CLAUDE_PLUGIN_ROOT}` in-session, a newest-installed-copy
  resolution outside one, and the module form for a machine whose application-control policy
  blocks console-script executables. That last is also the second field report to hunt for a
  recipe shipped in `docs/installation.md` since 0.12.0, so it moves to the artifact the consumer
  keeps, with installation.md holding the reasons. Both forms were run from a neutral working
  directory before being written down.
- **The report-unit note stops giving anchor advice to a finding with no anchor.** Adding a check
  whose violations carry cause keys sent A12's instruction — "re-anchor the block; do not delete
  the rows" — to a reader whose defect is a requirements ledger. The note now names the count for
  every grouped check and keeps the re-anchor sentence for the checks that group by a moved
  anchor. Found by running the new gate end to end rather than by a test, which is the argument
  for running it.
- **The Part-A reference block gained a check and lost four restatements.** *Displacement*, as the
  promotion rule requires: A0's line is now the only home for what `Kind: single-change` relaxes —
  A1, A2, A4 and A5 each restated it — and W1's and W3's rationale clauses moved to the CHANGELOG
  entries that shipped them, A12 stopped repeating A11's bracket rule. The Definition-of-Ready
  sheet is 1,648 words against its 1,650 cap: one check richer, four duplications lighter, no cap
  raised.

## [0.15.0] - 2026-08-12

The gate-empiricism release: the spec gate stops being a catalogue of checks nobody had counted.
Every finding now names the check that raised it, a local ledger records opportunity as well as
fires, every check carries a positive control, and the reshaped gate is proved against the frozen
census cell for cell. The measurement bought to license the one remaining prose cut did not
license it, so no prose is cut here — the candidate bodies ship as measurement assets `keel init`
cannot reach. Design register: `docs/evidence.md` (the KEEL-B07 pre-registration and its dated
amendment, both written before any forward data).

### Added

- **Check ids on every finding** (T0.1, `models.py`): `Violation.check`, a `Warning(check,
  message)` type replacing the bare string in `GateResult`, and `models.CHECK_IDS` as the closed
  catalogue — A0–A12, R1, B1, B2, W1–W5, of which **W4** (B2's adoption nudge) and **W5** (B2's
  spec-hash mismatch) are new letters for warnings B2 already emitted and nobody could count.
  Identity is a field, never a `W1: ` message prefix: `where` is a coordinate and collides by
  design (`line N` from A3 and A8, `path:line` from A6, A11 and A12, `Pre-mortem certification`
  from four B1 conditions), so any count keyed on it fuses distinct checks. Nothing downstream is
  countable without this, which is why it came first.
- **The gate hit-rate ledger, in three states** (KEEL-B07, `src/keel/gate_ledger.py`,
  `keel gate-health`, `docs/cli-reference.md`): each check reports a `Probe(check, candidates,
  fired, causes)` — `candidates == 0` is *n/a*, `candidates > 0` with no fires is *clean*, and
  only the second is evidence. A two-state count cannot distinguish *inert* from *never had an
  opportunity*, which is the distinction eleven verify-when-present or conditionally-relaxed
  checks turn on. Privacy is a type boundary rather than a habit: the writer only ever sees a
  `LedgerLine` whose every field is an int, bool, closed enum, hex digest or slug, so a free-text
  field is unrepresentable and `Violation.message` cannot reach it by any path; the spec is a
  digest, never a stem, because stems name a project's roadmap. Local only, nothing uploaded,
  `KEEL_GATE_LEDGER=off` disables it, and writing is fail-open — the 0/1/2 exit codes are
  unchanged and pinned. `keel gate-health` reads it back per check, split by author-loop
  (`--structure-only`) and full-gate runs.
- **A positive control for every check** (T0.2, `tests/fixtures/adversarial/`): one realistic spec
  over a staged mini-repo that fires **nothing** — the false-positive floor — plus one minimal
  edit per check that must make exactly that check fire. The assertion is set equality, never
  membership: a mutant that trips three checks is a bad fixture, not a strong one. The corpus is
  not a keel document and names no keel concept, because an oracle sharing vocabulary with the
  artifact under study cannot report on it. A check that has never fired in the field is either
  sharp and internalised or broken, and from outside those are the same observation; this is what
  tells them apart, for the price of a pytest run rather than a paid trial. A coverage assertion
  requires a control per catalogued check (A3 the recorded exception — its power is already proven
  in the field).
- **`pre-mortem-profiles.md`** — the kind-selected sheet (partial KEEL-B10): material dispatched
  only for the spec kind that needs it, opening with the measurement/experiment design sheet and
  the seven Part-B reviewer items that gate it. A code spec never pays for it. Partial on purpose:
  the DoR sheet's copies moved here and were deleted, but the pre-mortem prompt's own
  eval/experiment lenses are not folded yet — that is a directive-body edit, and it waits behind
  KEEL-B09. Until it lands, those three probes have two homes, which `docs/backlog.md` records.
- **Candidate core bodies** (`src/keel/templates/core/`, `tests/test_core_variants.py`): the
  ablation arms for "is the kit's prose necessary?", built by **deletion only** — every line of a
  core body appears, in order, in the body it was cut from, so the diff is the independent
  variable and cannot quietly become a rewrite that measures wording. They are **candidates, not
  templates**: `keel init` globs the kit directory non-recursively and cannot reach the
  subdirectory, and a test pins that, because a later refactor to a recursive glob would ship two
  competing spec templates to every adopting project.
- **The pre-registration for the ledger** (`docs/evidence.md`): what each count is expected to
  show, and the dispositions the ledger fires by itself, fixed before any data arrived. Two
  demotions argued for during the instrument's design are explicitly **not** taken — A7 has 33–34
  material units across 18 specs and A9 has 12 across 7, against a standing bar of ≥40 across ≥15
  revisions in ≥3 repos.

### Changed

- **The kit stamp survives authoring, and W1 widens to the case that occurs** (T0.3): the stamp
  moves from an HTML comment below the closing rule to the visible header (`- **Kit:** X.Y.Z`)
  beside Date and Status, because a hand-copied spec dropped the comment silently — no authored
  spec in the census carried one, so W1 had zero material forever. W1 now also warns on an
  **unstamped** spec. The legacy comment form is still read: retiring it from the template does
  not retire it from the specs already carrying it. The version-consistency test follows the stamp
  to its new home.
- **`Kind:` ships resolved, not as a menu** (T0.3): the scaffold shipped `series | single-change`
  while the parser reads the leading token, so an untouched scaffold silently declared whichever
  kind was written first — reorder the menu and every untouched scaffold silently relaxes A1/A4/A5.
  The template now declares one resolved kind (`series`, which relaxes nothing) and names the
  alternative in prose; doctrine §3 carries the adoption-time rationale.
- **W2 stops invalidating the certification it warns about** (T0.4, KEEL-B25/W8): the header
  `Status:` line leaves the hashed span, exactly as the certification section already had — the
  exclusion is the header *field*, not the word, so a `Status:` line inside a numbered section is
  content and still binds. Obeying W2's advice used to move `spec_hash` and invalidate the
  `Spec-hash:` in the artifact the same run had just verified. **Migration:** every `Spec-hash:`
  already recorded in a saved pre-mortem artifact is invalidated, surfacing as a one-time wave of
  W5 "certified against an earlier revision" warnings — the expected state, not a defect, cleared
  by re-running `keel spec-hash`. The hash's scope is now documented as pinned per gate MINOR, the
  contract W1's kit-skew semantics already carried (`docs/cli-reference.md`).
- **A10's three reproduced defeats are closed** (T1.3): the invariant-key window becomes the
  claim's own paragraph (it was prev/this/next line, so a claim three lines below its subject was
  invisible), and the negation lookback stops at the nearest sentence or clause boundary (it ran
  back four words across them, so an ordinary aside — "is, once again, enforced" — read as a
  deferral). Real deferrals put their negation next to the claim and still suppress. The widening
  is fenced three ways, per the 0.11.0/0.13.0 lesson: the corpus's clean spec must stay silent,
  every mutant must still fire exactly its own check, and A10 runs over this repo's own shipped
  prose — which is where window logic tuned on synthetic fixtures goes wrong.
- **A fold-ledger confirmation may name a range** (T1.4): `artifact:lo-hi` in an A12 cell, so a
  reviewer confirming a fix that spans lines no longer has to drop the range or record a line the
  fix does not live on. A `.py`/`.pyi` range must close every bracket it opens, as A11 already
  requires, and a snippet is matched against the range rather than one line. *Displacement:* the
  two spec-template notes this widened were compressed in the same edit, not waived — the
  gate-adversarial-examples note and the fold-ledger note, so the 500-word contract-note cap held.
- **The report unit: one edit is one cause** (T1.2): a `Violation` carries a `cause` key and
  violations sharing it are one defect. One insertion above a self-anchored fold ledger produced
  **57 A12 violations** at a uniform shift; counting those as 57 findings made A12 look like the
  noisiest check in the surface and left "how many things are actually wrong here?" unanswerable.
  Anchors failing against the same target group; where a snippet lets the shift be computed, only
  anchors sharing the delta group. A violation with no key is its own cause, so nothing is silently
  merged — the grouping deliberately **under**-groups, because over-reporting is honest and
  over-grouping hides. The CLI lists every violation and adds one line naming the cause count, with
  the instruction the field asked for: re-anchor the block, do not delete the rows. `fired` still
  counts every violation; the ledger schema moves to **v2** and marks the boundary — `fired` is
  comparable across it, `causes` is not.
- **One home per fact, and the ratchets that keep it** (T0.5): eight relocations down the frequency
  gradient plus two deletions of verbatim second homes. A clause costs its words every time the
  body carrying it is dispatched, so the default disposition for prose is relocation, not deletion —
  and a relocation is information-preserving and owes no measurement. Out of the spec-template: the
  `Kind:`/`Phases:` rationale → doctrine §3; the ADR "next free number on your base" trap →
  `adr-template.md`; release-notes-in-wave → `definition-of-done.md` (it is a *done* condition); the
  experiment-design section → `pre-mortem-profiles.md`. Out of the DoR sheet: the hand-written
  Part-A checklist and the seven eval/experiment Part-B items. Contract notes **918 → 499 words**,
  the DoR sheet **2,242 → 1,619**. *Ratchets:* the contract-note cap goes **925 → 500** and the DoR
  sheet gets its first cap, at the measured **1,650** rather than the 1,300 the reshape aimed at —
  the remaining candidates are held behind a measurement that has not run, and a cap chosen to
  force an unlicensed cut would be a verdict dressed as a budget (`CONTRIBUTING.md`,
  `tests/test_body_budgets.py`).
- **The two consumed checklists foreground what they add** (T0.6, partial KEEL-B33): both files now
  have external consumers by reference, so **nothing is removed** — what changes is order and one
  framing sentence each. `definition-of-done.md` leads with the two field-derived traps (a wrapped
  tool must have RUN TO COMPLETION; every referenced artifact is `git ls-files`-tracked), neither
  inferable from a project's own toolchain, and marks the generic block as the bind-your-commands
  stub it is. `review-checklist.md` moves Gate completion to the top and states that ordinary code
  review is **delegated** to the reviewer and the linters — without that sentence a later collapse
  of the generic items reads as amputation. The ordering effect itself is unprovable here and is
  taken as a judgement with a bounded downside: zero words removed, reversal is one revert.
- **A non-change, recorded** (T0.7): a pre-mortem ablation measured *danger framing* inert in
  agent-directed prose. The kit's only agent-directed blast-radius text is not danger framing — it
  names what else the fix reaches, which is target naming, the highest-value measured property in
  that same body — and doctrine's blast-radius language routes a human decision the study never
  scoped. A measured null is scoped to what was measured; `tests/test_consumed_lines.py` pins the
  field's target-naming form so the register cannot drift later into the thing the null was about
  (`CONTRIBUTING.md`, gate-health 3a).
- **Docs against the code**: `docs/cli-reference.md` gains `keel gate-health`, the ledger section
  and the corrected `spec-hash` scope; `docs/glossary.md` carries the current check catalogue
  (A0–A12, R1, B1, B2, W1–W5), the finding-identity rule and the stamp's new home;
  `docs/doctrine.md` §3 carries the `Kind:`/`Phases:` rationale; `CONTRIBUTING.md` records the
  positive-control obligation (1a), the ledger as machine-recorded with the three-part standing bar
  for a cut, and the scoped-null rule (3a). The release-cut sweep corrected four claims this wave
  invalidated: the release now bumps **nine** version sites (the candidate core's stamp is coupled
  to the template's by the strict-subset test, and a missed bump reds the suite), **four** capped
  bodies rather than three, Part A is `A0–A12, R1` in `README.md` and `docs/glossary.md`, and the
  kit is eleven templates behind seven CLI commands in `docs/backlog.md`'s fold row.

### Removed

- **Two verbatim second homes in the spec-template** (T0.5): "Out-of-wave consumers", which declares
  itself ungated and whose home is the pre-mortem directive body, and "Counting", a verbatim copy of
  that body's own line.
- **The DoR sheet's hand-written Part-A checklist** (T0.5), which restated the fenced reference
  block in looser words. The deletion is proved rather than asserted:
  `tests/test_templates_valid.py` maps every deleted line to the check that carries it and asserts
  the surviving block still names every letter in the catalogue.

### Measured

Stated in the three-way vocabulary — proven / not-proven / not-measurable — because a gate that
holds consumer specs to "every cited referent resolves" owes its own claims the same bar.

- **A $0 retrospective census**, run before anything was built: **19 specs against three trees**,
  with a **44-document control arm** of design documents in these repos that were never authored to
  the method. It is what turned "which checks matter" from an opinion into a base rate.
- **Zero regression, proved rather than asserted**: the reshaped gate re-run against the frozen
  census — **1,083 (spec, tree, check) cells compared, 0 mismatches**, all 19 specs byte-stable
  since the census. Intended movement only: W1 material **0 → 19 specs** (0 → 57 warnings, and
  0 → 44 documents in the control arm), A10 **0 → 3 cells** on 1 spec.
- **Every widening was re-run against the control arm before being called a fix** — the standard
  the pre-registration already set for A8, applied to this wave's three (A10's paragraph window,
  W1's unstamped case, A12's ranges). Over the 44 documents the fired set is **identical, document
  for document, on all 19 checks**; the only movement is W1's intended 0 → 44.
- **The kit-core ablation is bought at stage 1 only**: **24 of 48 planned trials, $9.7572**, every
  trial completed and valid. The saturation gate passed — the deciding note-only class *was*
  exercised, so the "no arm ever fails, so no power" branch of the pre-registered cut rule does not
  fire — and **stage 2 is unbought**. So "the kit's core is sufficient" is **not measured**, not
  null: only five discordant pairs were realised, which caps the attainable evidence at p = 0.0625
  before any pair is looked at, and the observed 4:1 discordance runs *toward* the full body
  (10/18 vs 13/18 overall). One pre-registered signal runs the other way on `behaviour/unstated`
  (10/12 core vs 7/12 full, discordance 0:3) — two underpowered signals in opposite directions,
  which describes an instrument without power rather than a tie to break by preference. No
  non-inferiority margin was ever registered, so "matches" has no numeric meaning to fall back on;
  choosing one now would mean choosing it against the data. **Nothing is cut on it.**
- **What stays unmeasured**, recorded rather than papered over: **12 of 19 checks never fired under
  either gate**, so a regression in them is undetectable in this corpus — A8 the sharpest instance
  at 1,230 `§N` references across 19 specs with zero fires. A10's and A12's false-positive rates
  have **no material** in the control arm (no control document carries an Enforcement-status table
  or a fold ledger) and are recorded as *unmeasured*, not zero. A5's and R1's SHARP status each
  rests on one weak hit — A5's has a robust core of 0, R1's is dated three days *before* R1 shipped
  — so a zero-fire forward record for either is consistent with that base and is **not** a
  regression. And whether a check is worth its author-side cost remains the comparative claim
  ADR-0015 retired; this instrument counts opportunity and fires, and does not reopen it.

### Origin

- The gate audit and the $0 retrospective census over the existing spec corpus (maintainer-local —
  see `docs/evidence.md`), plus KEEL-B07 from the 2026-08-11 improvement backlog. Built on
  `feat/gate-empiricism` (PR #18); the companion eval report lives with the harness that ran it
  (`grimaldost/fathom`, `eval/keel-gate`). Regression tests **214 → 317**; every behaviour-changing
  section ships at least one, and every check ships a positive control.
- The cross-vendor enrichment panel (standing non-blocking practice since 0.9.0) **did not run** for
  this release — a recorded decision, not an omission. The adversarial read it substitutes for was
  an in-arc critique pass over the evidence write-up, which confirmed fifteen defects; three claims
  moved as a result, two of them by splitting into a proven half and an unmeasured half.

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
