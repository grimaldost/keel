# ADR-0016: field-hardening — moving recurring gaps to their enforcing layer

- **Status:** Accepted
- **Date:** 2026-07-10
- **Relates to:** ADR-0011 (the enforcement gap — the gate must enforce what it documents; this ADR
  applies the same escalation rule to five residual gaps), ADR-0002 (form/correctness split — the
  operator close respects it), ADR-0003 (thinness — the loop-close and router decisions defer to it),
  ADR-0004/0007 (structured pre-mortem findings — the coupling slot extends the schema), ADR-0014
  (the certification artifact — the operator close prescribes the missing half of its round economy)

## Context

The post-0.12.0 field round (five reports across three consumer projects plus keel's own release, plus
two promotions orphaned since 2026-06-28; triaged in `docs/feedback/2026-07-09-post-0120-field-triage.md`,
maintainer-local) surfaced no keel-attributable miss and no vacuous gate. The friction had moved to the
margins, and a root-cause pass (seven analyses, each adversarially verified) found the same shape under
most of it: a recurring failure was being patched at an **advisory or distributed layer** that
structurally cannot hold it. The escalation rule keel already states for a skill — a constraint that
needs caps to hold needs a gate, not louder prose — applied to itself. Each decision below moves one
recurring gap down one enforcement rung.

## Decision

### 1. One shared text-segmentation layer for the Part-A prose scanners

**Problem.** `check-ready` had exactly one shared masking pass (`_mask_fenced`); below it, every
scanner re-decided inline-code and table-cell handling locally, in five divergent idioms. Three field
failures were three of those loci — an inline-code span wrapped across a line break (A3 false-fires),
a required fold-ledger cell containing a backticked type union with a `|` (A12 mis-parses and emits a
misleading message), a slash-joined cross-document section range (A8 loses the doc cue) — and probes
proved two more checks (A4, A5) carried the identical latent defect. This is the fourth recurrence of
a false-positive class past a shipped fix (the panel's false-positive cluster → the 0.11.x fence
layers), because each prior fix hardened the *fence* layer and none of these spots is fence-reachable:
a table cell cannot be fenced, a wrapped span defeats per-line stripping, a cue token is prose.

**Decision.** Add a shared segmentation layer of two primitives beside `_mask_fenced` — a prose view
that space-fills inline-code spans (line-wrapped spans included, paragraph-bounded) and a
backtick/escape-aware table-row splitter — and route the prose scanners (A3's angle idiom, A8) and
*both* table parsers (feeding A4/A5/A10/A12) through them. Masks replace with spaces, never delete, so
line numbers and offsets stay true. This is **named views, not one view forced on all**: the anchor
scanners (A6/A9/A11, ADR references) deliberately keep the unmasked view, because their tokens live
inside backticks. Preferred over three targeted patches because the same masking decision was being
made independently at five loci and patches would leave the A4/A5 siblings live for a fifth recurrence.

**Named residual.** A10's own two masking idioms and the `_words` helper are **not** migrated this
round — A10 must see code content to judge an "enforced" claim, so its unwrap semantics differ from
blanking. The layer reduces five idioms to three, not one; full convergence is deferred deliberately
and recorded here so "distributed masking" is not silently left surviving at one scanner.

**Honest note.** Two behaviours flip at syntax edges no test pinned: a backticked `§N` glyph mention
no longer trips A8, and a genuine intra-spec section dangler immediately after a dash/comma-joined
cross-document section run is now read as part of the range (a lenient false-negative, the natural
reading). Both are named in the CHANGELOG. The field/digest observation that the *en-dash* range form
"passes today" was coincidental — it fails today too; the cue loss is joiner-agnostic.

### 2. The operator close — prescribing the discharge of a CONDITIONAL-CERTIFY

**Problem.** 0.10.0–0.12.0 shipped the operator-accepted CONDITIONAL-CERTIFY *state* fully mechanized
(B1 acceptance, B2 artifact agreement, structured conditions, the round economy) but never prescribed
its *close* — what the caller records after the Operator applies the bounded fix. The close is
derivable only by reasoning through the gate: flipping the recorded verdict to CERTIFIED without a new
pass fails B2's verdict-agreement check, and keeping the as-reviewed spec-hash makes B2's mismatch WARN
expected on exactly this path. So every operator re-derived it — two consumer waves bought confirm
rounds (~0.5M subagent tokens) to dodge the ambiguity, a greenfield project improvised the correct
close, and keel's own release parked the reasoning in a report. A second, active defect compounded it:
the save-protocol's "run spec-hash after the final fold" wording, read literally on the operator path,
instructs recomputing the hash *after* discharge — which silences the honest WARN and records a hash of
a revision the reviewer never read.

**Decision.** Prescribe the close once, in `definition-of-ready.md` Part B (the one prescriptive kit
file that travels to plugin-only consumers), as a named "operator close": the recorded verdict **stays**
CONDITIONAL-CERTIFY with the named Operator and a discharge note (each discharged condition a fold-ledger
row); the B1 WARN — and, *whenever discharging a condition edits the spec body*, B2's earlier-revision
WARN — are the expected honest state, not defects to silence (ADR-0002); the close's own recording never
moves the hash. A confirm re-gate is **optional**, priced by the round economy (ADR-0014): taken only
when a condition outgrew its named bound or touches an irreversible/shared-contract surface — which is
what displaces the improvised confirm rounds. Everything else is a one-clause reference to that block
(`keel-premortem.md`, doctrine, spec-template, glossary, getting-started), and the ambiguous
save-protocol wording is **corrected**, not appended to. The B2 mismatch WARN gains a suffix *only*
when the recorded verdict is an operator-accepted CONDITIONAL-CERTIFY — the one channel that reaches
consumers holding an older kit copy; B1's WARN is left untouched, so its pressure on *undischarged*
conditionals stays. The pre-mortem prompt and agent are **not** touched: the close is the caller's step
by shipped contract.

### 3. The reflection loop closes — promotions land, and open rows are swept

**Problem.** `reflection-triage.md` ended at "record what was promoted," on two assumptions that fail
structurally: that the promotion targets are editable from the triaging context (false when the method
runs from an installed plugin — the promotions get recorded project-side where the method never looks),
and that a recorded promotion is discoverable by whoever can build it (false even in keel's own repo —
a triage doc's open rows are never "untriaged," so nothing obligated a later pass to consume them, and
three promotions sat orphaned for ten days).

**Decision.** Restructure the terminal step from "record" to "land," with two branches: targets
editable in-context are applied directly; targets out of reach ride a dated method-promotions handoff
into the method's registered feedback intake — the same channel the session's feedback report already
travels — with only a pointer left project-side. CHANGELOG entries are named as the method repo's, at
build time. Add a **sweep rule**: the open (`proposed`/`watch`) rows of every prior triage doc in the
sink are input to the next pass, and a row closes only when a later doc lists its doc as input. The
row-status vocabulary is defined inside the template (it previously lived only in the out-of-kit generic
skill — the exact loss the failure named), and the handoff doc's heading must *not* begin `# Triage`
(or its own rows would be re-orphaned by the H1-based detection). **No `keel init` / CLI change**: the
editable branch already has structure (`init` copies the kit), the plugin branch needs a route not a
file, and a bindings row naming the method's upstream address would edge keel toward tracking a consumer
(ADR-0003).

### 4. Three cross-artifact predicates gain a structural home

Three promotions carried from the 2026-06-28 cycle, each a still-absent hole in a keel surface:

- **A predicted coupling names the input the dependent consumes.** The pre-mortem's grounding
  directives enumerated claim classes (reuse, existence, capability-source, generated-output) but had
  no class for a predicted cross-artifact *coupling* — so a phantom coupling once shipped as a MUST
  while a structurally identical real one was true; the discriminator (what the dependent actually
  reads) was required nowhere. Add a required-when-coupling `consumed_input:` field to the pre-mortem
  findings schema (prompt ⊕ agent, on the `blast_radius:` precedent, drift-guarded): a coupling that
  cannot name its consumed input downgrades to a hypothesis with a disconfirming test rather than an
  asserted MUST. Its counterweight is 0.12.0's both-directions trigger, which widened coupling emission
  without supplying this discriminator. The originally-paired review-checklist item is dropped: phase-7
  review reads PR diffs, where no coupling predictions exist to verify (and the checklist's existing
  "coupling smell" is code-boundary coupling, a homonym) — one home, per the promote-to-exactly-one
  rule.
- **Referenced artifacts are version-control-tracked at the Review gate.** A durable spec once got
  `.gitignore`d out of a design-foundation commit while passing every content check, because no phase
  asked whether the referenced file was itself tracked. Add one deterministic line to
  `definition-of-done.md`: every artifact the spec or its ADRs reference is `git ls-files`-present.
  **Named residual:** the DoD is the pre-merge Review gate, so a design-only round that names the DoD
  phase skipped does not run this predicate for exactly the round class that produced the defect — it
  is caught at the next execution round's DoD at latest (the references persist).
- **The router reads the project's bindings before the packaged templates.** `keel init` already ships
  a bindings record with a spec-format slot, but neither entry path consumed it, so a contributor on an
  established project re-discovered the de-facto format by globbing. Make the record load-bearing on the
  read side: an apply-method entry step reads the bindings first and, if absent but prior artifacts
  exist, binds from them and writes the record. No new CLI; the `bind-check` stub stays out of scope
  (it is test-pinned).

### 5. Self-explaining gate messages and mechanized release guards over advisory prose

- **The gate's messages are the always-current teaching surface.** Rather than a generator syncing
  template guidance from the checks (a build step keel does not have, for a two-sentence drift across
  twelve releases), the A6 anchor-snippet failure states its own parse ("interpreted `<token>` … as a
  snippet to match against line N"), and the spec-template gains the three missing contract lines
  (repo-root anchor form, the adjacency rule, the A5 body-claim requirement) pinned by needle tests so
  they cannot drift out silently. A claim-supporting anchor **should** carry a snippet (template prose
  only; the gating half stays parked pending a second report). A guard test asserts the shipped template
  carries no gate-parseable anchor token, so example anchors cannot themselves trip A6.
- **The CHANGELOG heading chain is machine-checked.** A release edit once replaced the previous
  release's heading instead of inserting above it, and only the blind audit caught it — the
  version-consistency test reads the newest heading only. The new test's load-bearing layer is not the
  obvious "strict descending order + no duplicates" (which *passes* on the actual broken file — a
  destroyed heading still leaves a descending chain) but the **absorption signature**: a `### kind`
  repeating inside one release section. The shape assert also rejects a Keep-a-Changelog `## [Unreleased]`
  heading — a deliberate deviation (keel cuts releases directly; the newest-heading version site assumes
  it), pinned by the test. The two remaining release-flow disciplines (the cross-vendor enrichment panel
  is a recorded decision when skipped; the four gates run unpiped) stay prose in `CONTRIBUTING.md` and
  `AGENTS.md` — they are the recorded-decision half the triage scoped as non-mechanizable.

## Consequences

- Five recurring gaps each move down one enforcement rung: distributed masking → a shared layer;
  a derived-but-undocumented close → one authoritative block; a terminal "record" → a structured
  land-and-sweep; unclassified claims → a required schema slot and a deterministic predicate;
  audit-only catches → a CI test and self-explaining messages.
- The pre-mortem findings schema grows one field; the drift-guard marker count moves 33 → 34, in one
  commit touching both mirrored files.
- The template kit changes (DoR operator close, spec-template contract lines, reflection-triage
  restructure, DoD tracking line) ride one kit-stamp bump; consumers on older copies pick them up on
  the next `keel init`, and the kit-skew WARN tells them to.
- These are field-hardening decisions, not a new capability surface: old green specs stay green (every
  new gate behaviour is a WARN, a message change, or a false-positive removal), and the honest
  false-positive/false-negative flips are enumerated in the CHANGELOG.
