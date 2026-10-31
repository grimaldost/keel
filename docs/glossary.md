# Glossary

The working vocabulary keel's docs, gates, and templates use. One line each; the mechanism docs
stay the source of truth.

- **Part A / Part B** — the DoR gate's two halves: deterministic well-formedness checks a script
  asserts (A0–A13, R1) vs. correctness externalized to a blind reviewer's recorded certification
  (B1, B2). ADR-0002.
- **program / series / task; wave** — the three nested scopes of `concepts.md`: a *program*
  is a named undertaking spanning several series, closed by a written decision; a *series*
  is the governed set of tasks under one spec and one gate set, whose Decompose artifact is
  the series file (`series.toml`); a *task* is one briefed, gated unit of work, inside a
  series one single-concern PR. A *wave* is the batch of a series' tasks that ships
  together (the spec template's `Wave` column: "the batch it ships with"); it is ordered,
  it is not a scope, and keel's "wave estimate", "wave budget" and "three governed waves"
  are the wave's — in that last phrase each wave was a whole series.
- **phase** — one of the eight lifecycle phases of `phases-reference.md`, and nothing else.
  A larger stretch of work is a program or a series; a numbered step of one plan or skill
  is cited with that document ("step 2 of the build plan"); an orchestrator's own keys that
  happen to be spelled `phase` — a budget role, a check-scope tag — are called by what they
  do.
- **round** — one repetition of a *pass*, where a pass is a named kind of review (the
  DESIGN pass and the SERIES pass; a triage pass): a pre-mortem round's
  artifact is `<spec-stem>.premortem.md` (round 1) or `<spec-stem>.premortem-r<N>.md`
  (round N); how many rounds a pass takes is sized by *the round economy*. A *work round*
  (doctrine §3, *subset of phases*) labels which phases a series or task ran and adds no
  scope; "the next round" in the doctrine is the next series.
- **sibling citation** — the identifier rule for text that names more than one repository,
  already applied in `backlog.md` ("a sibling project's backlog row is cited by its stable
  ID"). A row that carries its owner's token where its repository writes it (`KEEL-B57`,
  `CONV-B52`) is cited verbatim everywhere; a bare identifier (`ADR-0003`) stays bare inside
  its own repository and takes the owner token and a hyphen outside it (`KEEL-ADR-0003`); the
  closed list of owner tokens is kept by the project that uses them (keel's is in
  `docs/backlog.md`). Gate output codes (A0…A13, B1, B2, R1, W1…W11, D1, D2) are not
  identifiers in this sense and are cited as
  "check A12", never `KEEL-A12` — `KEEL-B1` would name both a Part-B check and a backlog
  row. Enumerations local to one document (a pre-mortem's FM-n, a triage's T1a or E11a, a
  spec's §n, a round's r3, a plan's Part B) are cited together with their document.
- **A0…A13, R1, B1, B2, W1…W11** — the individual checks `keel check-ready` runs (the W-letters are
  WARN-only: they report, they never fail the gate); the authoritative list is
  `definition-of-ready.md`'s "Reference: what `check_spec_ready` asserts" block. Every finding the
  gate emits names its check in a field (`Violation.check`, `Warning.check`), never as a message
  prefix — `where` is a coordinate and collides across checks, so a count keyed on it fuses them.
  Cited as `check <code>`; see *sibling citation*.
- **D1, D2** — the Decompose exit gate's pair, run by `keel decompose-check` at the 3→4 boundary
  over the `### Series review` record: B1/B2's shape applied to the SERIES pass, whose subject is
  the generated series rather than the spec. A separate catalogue from the DoR letters because it
  is a separate gate, at a boundary `check-ready` runs before.
  Cited as `check <code>`; see *sibling citation*.
- **DESIGN pass / SERIES pass** — the two blind pre-mortems: the first reads the spec and closes
  Specify (B1/B2), the second reads the GENERATED series against the spec and closes Decompose
  (D1/D2). Same reviewer contract, different artifact.
- **dozes** — a verify-when-present check meeting its absent trigger: not skipped by error, asleep
  by design (e.g. A12 with no fold-ledger rows, A13 with no requirements register).
- **verify-when-present vs. deliberate tightening** — the two retro-compatibility classes: a check
  that fires only when its structure exists (B2, A13) vs. one that newly requires structure
  (R1's ledger-on-claimed-fold) and says so.
- **verdict tokens** — `CERTIFIED` · `CONDITIONAL-CERTIFY` (requires a named `Operator:`) ·
  `NEEDS-REVISION`; parsed leading-token, so trailing prose or an identity suffix is inert. An
  Operator-discharged conditional stays `CONDITIONAL-CERTIFY` (the *operator close*,
  `definition-of-ready.md` Part B).
- **fold** — applying a pre-mortem finding's `smallest_fix` back into the spec; a *verified hop*:
  each fix is re-grounded first, and the post-fold re-read hunts the fold's own errors.
- **fold ledger** — one row per folded finding (`finding · target · path:line · confirmed`,
  optional verified snippet) so the post-fold delta is reviewable (A12/R1).
- **certification artifact** — the saved pre-mortem output (`<spec-stem>.premortem.md`; round N at `<spec-stem>.premortem-r<N>.md`) the
  certification names; B2 verifies existence, verdict agreement, and `Spec-hash:` currency.
- **spec-hash** — the canonical hash `keel spec-hash` prints: sha256 of the spec with its
  certification section's lines removed, so recording the certification never invalidates it.
- **the round economy** — the doctrine's sizing rule for pre-mortem arcs: two rounds vs. one pass
  vs. a targeted confirmatory pass (ADR-0014).
- **rising bar** — on round ≥2 a finding blocks only if it corrupts the decision the spec gates;
  nice-to-haves fold as advisories.
- **re-gate / resolution audit** — round ≥2's posture: audit each prior finding
  (RESOLVED / PARTIALLY-RESOLVED / UNRESOLVED) before hunting fold-introduced defects.
- **DC1…DC3, DC4-B** — the grounding axes (doctrine sharpening 5): ground the verification, model
  the mechanical consumers, verify the transformation, and standing cross-artifact consistency.
- **one home (the directives)** — `pre-mortem-prompt.md` carries the pre-mortem directive text and
  the bundled agent reads it at run start; the drift guard that used to pin the two copies together
  retired with the duplication (ADR-0017). What is pinned now is non-duplication.
- **the kit** — the packaged templates `keel init` copies (`src/keel/templates/`); its stamp — the
  spec header's `- **Kit:** X.Y.Z` line, or a legacy `<!-- keel kit X.Y.Z -->` comment — lets
  `check-ready` warn on kit↔gate skew, and on an unstamped spec (W1).
- **finding IDs vs. promotion IDs** — two namespaces in the feedback loop: a report's stable
  `<file-stem>#<n>` findings (what triage cites as evidence) vs. a triage doc's own `T1a`-style
  promotion rows (what statuses track). Don't conflate them.
- **subset of phases** — a round runs a named subset of the 8 phases (`- **Phases:** Decide+Specify
  (Decompose: skipped)`); the unused phases are named-as-skipped, not faked (doctrine §3, A4).
  A round in this sense is a *work round*; see *round*.
- **spec kind** — the header's `Kind: series | single-change` declaration. `single-change` relaxes
  the Part-A structural trio to absent-ok and moves the acceptance-criterion floor to the document;
  a present section is still checked in full, and an unreadable kind relaxes nothing.
- **widen-only** — a gate change that accepts strictly more than before (e.g. B1 learning the
  operator-accepted conditional), so no green spec turns red.
