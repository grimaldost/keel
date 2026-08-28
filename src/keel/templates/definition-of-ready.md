# Definition of Ready (DoR gate)

The exit gate of **Specify** / entry gate of **Decompose**. A series may not be
decomposed or run until DoR passes. Rationale: once workers are stateless and gates
deterministic, spec quality is the single point of failure (method sharpening 1) —
so spec quality gets its own gate.

DoR is **not** symmetric to the Definition of Done in mechanism, and we no longer
claim it is. DoD checks behaviour against an executable oracle (tests, types); DoR
has no oracle for "is this approach right?". So DoR splits in two: a deterministic
**Part A** (well-formedness — a script asserts it) and an externalized **Part B**
(correctness — certified by a fresh reviewer, a judgment moved to a different
context, not a machine verdict). `keel check-ready` enforces both halves: it passes
only when the spec is well-formed AND a blind pre-mortem certification is recorded
(ADR-0002). It never green-lights a spec on structure alone.

## Part A — well-formedness checks (a script asserts these)

These assert *form*, not *correctness* — a well-formed spec can still be wrong (that
is Part B's job). You do not check them by hand: `keel check-ready <spec>` is the script,
and the block below is the contract it enforces, check by check. A prose restatement of
that block used to sit here; it was a lossy paraphrase of the same facts, and a reader
who trusted it over the block trusted the older of two copies.

### Reference: what `check_spec_ready` asserts

```
A0 the header's `Kind:` declaration, when present, must read `series` or `single-change` — an
   unknown kind is a violation naming the offending token, and relaxes nothing. `single-change`
   relaxes A1/A4/A5 to absent-ok (a present section is still checked in full) and moves A2 to
   document scope — this line is the only home for that relaxation
A1 fail unless >=1 "### §N" heading under "Numbered sections", all numbered
A2 fail unless each §N has a non-trivial "Acceptance criterion" (present, >=5 words), counted
   in the paragraph immediately after the marker
A3 fail on a TBD/TODO/FIXME/??? token, or a leftover `<...>` angle placeholder — the angle idiom is matched on the prose view (inline-code spans space-filled, wrapped spans included), so backticked `<target>` syntax is exempt while a bare `<title>` is caught
A4 parse the PR<->section manifest: fail unless bijection(PRs, sections), full coverage — also absent-ok when the header declares `- **Phases:** ... (Decompose: skipped)` (ADR-0014)
A5 each concept->module path: fail unless exists(path) or ("to be created" and claimed by a §)
A6 each `path:line` anchor: fail unless file exists, line in range, and any quoted snippet (the backticked token right after the anchor) matches
A7 each cited `docs/adr/NNNN-...md`: fail unless that number is free on the base or names that ADR
A8 each bare intra-spec `§N` reference: fail unless it names a numbered section — detection on the prose view (a backticked `§N` mention is exempt); skips `§N.M`, headings, and doc-cued refs including a joined range (`ADR-0103 §3/§4`, an en-dash range)
A9 each `**Model-on:**`/`**Reuse:**` reference present: fail unless the path exists (and the symbol, for `path::symbol`)
A10 when an Enforcement-status table is present: fail if prose claims an invariant "enforced"/"guaranteed" whose row is not enforced
A11 each `path:lo-hi` range anchor: the file and `hi` line must resolve; for a `.py`/`.pyi` anchor it must additionally close (string/comment-aware) every bracket it opens (single-line `path:line` anchors stay A6)
A12 when a `### Fold ledger` sub-table is present: fail unless each row carries an `artifact:line` — or `artifact:lo-hi` — confirmation that resolves, read from whichever cell IS one rather than a fixed column; A11's bracket rule holds for a range cell; a row wider than its own header is a column break and fails as one
A13 when the header declares `- **Requirements:** <path>`: that register must resolve, and every `RR-<n>` order it declares needs a `## Requirements ledger` row disposing it to a §N, `DEFERRED — <trigger>`, `OUT-OF-SCOPE`, or `DEVIATED — ratified by <operator>`; silent with no register declared, and a self-ratified DEVIATED fails
R1 a certification claiming a non-trivial fold must carry a `### Fold ledger` with >=1 resolving row (a deliberate tightening, not verify-when-present; a clean certify dozes)
B1 fail unless a "## Pre-mortem certification" block records Verdict: CERTIFIED (or CONDITIONAL-CERTIFY + a named Operator) + a Reviewer
B2 when the certification names a `Certification artifact:`: the field's LEADING path token is the artifact (trailing prose — a round note, a prior-round path — is ignored); fail unless the file exists and its last line-anchored PREMORTEM-VERDICT token agrees with the recorded Verdict
W1 (warn) the header's `- **Kit:** X.Y.Z` stamp (or a legacy `<!-- keel kit X.Y.Z -->` comment) from a different kit MAJOR.MINOR than the running gate warns of kit<->gate skew; a patch difference is silent, and an UNSTAMPED spec warns too
W2 (warn) a header `Status:` still reading `draft` while a CERTIFIED / CONDITIONAL-CERTIFY certification is recorded warns that the coordinate system is stale; silent when there is no Status field, when Status has moved past draft, or when nothing is certified. The header `Status:` line is excluded from `spec_hash`, so obeying this warning cannot invalidate the certification the same run verified
W3 (warn) an anchor that does not resolve as written but whose basename matches exactly ONE repo file OUTSIDE a vendored tree resolves to that file and warns, naming the expansion; ambiguity, no match, or a match only inside a vendored tree still fails, naming the twin (A6/A11/A12)
W4 (warn) B2's adoption nudge: the certification names no artifact at all
W5 (warn) the named artifact's recorded `Spec-hash:` no longer matches ("certified against an earlier revision"), suffixed with the operator-close pointer when the recorded verdict is an operator-accepted CONDITIONAL-CERTIFY
```
*(Every finding names its check in a field, never as a `W1: ` message prefix — the id is what
makes a check's fires countable, and `where` collides across checks by design.)*
*(A2/A5 detect absence/triviality, not semantic wrongness — Part A cannot judge
"right." That is Part B.)*

## Part B — correctness, certified (a fresh, non-author reviewer certifies, with evidence)

Not mechanizable as form. Externalized: a reviewer who did **not** author the spec
runs the pre-mortem (`pre-mortem-prompt.md`) and records a verdict in the spec's
`## Pre-mortem certification` block. This is **required**, not recommended — it is the
only check aimed at "this approach is wrong," the dominant defect class once workers
are stateless.

- [ ] A pre-mortem pass has been run by a non-author reviewer, and the certification
      block records `Verdict: CERTIFIED` — or `CONDITIONAL-CERTIFY` with a named `Operator:`
      (operator-accepted, ready modulo a named fix; `check-ready` passes with a WARN, not EXIT 1).
      *(`keel check-ready` enforces this — B1.)*
- [ ] The pass's returned output is saved (`<spec-stem>.premortem.md`, with a `Spec-hash:` from
      `keel spec-hash`) and named in the certification's `Certification artifact:` field.
      *(`keel check-ready` verifies a named artifact — B2, verify-when-present: existence, verdict
      agreement, hash currency; forgery cost, not blindness proof.)*
- [ ] Every invariant the work touches is named in "Invariants touched", each with an ADR.
- [ ] Every concept maps to a module in the concept→module map.
- [ ] Every non-obvious design choice has an ADR (alternatives recorded).
- [ ] The spec is internally consistent (no section contradicts another).
- [ ] A post-fold coherence re-read was performed and recorded (`Post-fold coherence:` in
      the certification): each folded finding is applied consistently across all sections,
      and any scope-narrowing finding had its dependent counts re-derived.
- [ ] *(eval/experiment specs only)* the seven items on the measurement profile
      (`pre-mortem-profiles.md`) are certified, feasibility first. They gate the axes the spec's
      `## Experiment design (Part B)` section names, and they are dispatched only for that kind —
      a code spec neither reads them nor pays for them.

### The operator close (discharging a CONDITIONAL-CERTIFY)

When the final pass returns `CONDITIONAL-CERTIFY` and the named Operator applies the bounded
`conditions:` themselves, the sanctioned close is:

- **The recorded `Verdict:` stays `CONDITIONAL-CERTIFY`**, with the named `Operator:` and a discharge
  note on the verdict line (e.g. `CONDITIONAL-CERTIFY — COND-1 discharged by the Operator, <date>`);
  record each discharged condition as a fold-ledger row so A12 anchors the fix to a real line. Do not
  rewrite the verdict to `CERTIFIED`: no pass returned that token, and B2 fails a recorded Verdict
  that disagrees with the saved artifact's.
- **The artifact's `Spec-hash:` stays the hash of the spec the final pass read.** The close's own
  recording never moves the hash — a certification-block edit (the discharge note, a fold-ledger row)
  is masked from the hash by design. But if discharging a condition edits the **spec body**, the
  saved hash no longer matches, and B2's "certified against an earlier revision" WARN is then the
  *expected honest state* of this close, not a defect to silence (ADR-0002) — never recompute the
  hash after discharge to quiet it, which would record a revision the reviewer never read. The B1
  operator-accepted WARN stands the same way.
- **A confirm re-gate is optional**, priced by the round economy (ADR-0014): take one only when a
  condition outgrew its named ≤2-line bound, or the fix touches an irreversible / shared-contract
  surface. A confirm round bought only to flip the token to `CERTIFIED` is over-process — the close
  already records who accepted what, and the gate passes with its WARNs standing. When a confirm
  re-gate IS taken and returns `CERTIFIED`, its saved output becomes the certification artifact
  (latest-wins) and the recorded verdict flips with it — the ordinary close, not this one.

**Gate result:** Ready ✅ only when Part A is well-formed **and** the Part B
pre-mortem certification is recorded. `keel check-ready` enforces both halves; the
remaining Part B items are the reviewer's evidence-backed certification, not a
self-signed checkbox. The gate verifies the certification was *recorded* by a named
non-author reviewer — not that the reviewer was truly blind or right; that residual
trust is named, not hidden (ADR-0002).
