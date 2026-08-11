# Glossary

The working vocabulary keel's docs, gates, and templates use. One line each; the mechanism docs
stay the source of truth.

- **Part A / Part B** — the DoR gate's two halves: deterministic well-formedness checks a script
  asserts (A1–A12, R1) vs. correctness externalized to a blind reviewer's recorded certification
  (B1, B2). ADR-0002.
- **A1…A12, R1, B1, B2, W1, W2** — the individual checks `keel check-ready` runs (W1 and W2 are
  WARN-only: they report, they never fail the gate); the authoritative list is
  `definition-of-ready.md`'s "Reference: what `check_spec_ready` asserts" block.
- **dozes** — a verify-when-present check meeting its absent trigger: not skipped by error, asleep
  by design (e.g. A12 with no fold-ledger rows, A10 with no Enforcement-status table).
- **verify-when-present vs. deliberate tightening** — the two retro-compatibility classes: a check
  that fires only when its structure exists (B2, A10) vs. one that newly requires structure
  (R1's ledger-on-claimed-fold) and says so.
- **verdict tokens** — `CERTIFIED` · `CONDITIONAL-CERTIFY` (requires a named `Operator:`) ·
  `NEEDS-REVISION`; parsed leading-token, so trailing prose or an identity suffix is inert. An
  Operator-discharged conditional stays `CONDITIONAL-CERTIFY` (the *operator close*,
  `definition-of-ready.md` Part B).
- **fold** — applying a pre-mortem finding's `smallest_fix` back into the spec; a *verified hop*:
  each fix is re-grounded first, and the post-fold re-read hunts the fold's own errors.
- **fold ledger** — one row per folded finding (`finding · target · path:line · confirmed`,
  optional verified snippet) so the post-fold delta is reviewable (A12/R1).
- **certification artifact** — the saved pre-mortem output (`<spec-stem>.premortem.md`) the
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
- **spec kind** — the header's `Kind: series | single-change` declaration. `single-change` relaxes
  the Part-A structural trio to absent-ok and moves the acceptance-criterion floor to the document;
  a present section is still checked in full, and an unreadable kind relaxes nothing.
- **widen-only** — a gate change that accepts strictly more than before (e.g. B1 learning the
  operator-accepted conditional), so no green spec turns red.
