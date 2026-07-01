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
is Part B's job).

- [ ] Every section is numbered (§1, §2, …).
- [ ] Every numbered section has a **non-trivial** acceptance criterion.
- [ ] No `TBD` / `TODO` / `FIXME` / `???` anywhere in the spec.
- [ ] PR ↔ section manifest exists; every section is covered by **exactly one** PR
      and every PR cites **exactly one** section (a bijection).
- [ ] Every path in the concept→module map exists, or is explicitly marked "to be
      created" **and** claimed by a numbered section.
- [ ] Every `path:line` anchor resolves (file + line exist) and any quoted snippet matches.
- [ ] Every cited `docs/adr/NNNN-…` uses a number free on the base (no collision).
- [ ] Every `**Model-on:**` / `**Reuse:**` reference present resolves — the path exists
      (and the symbol, for `path::symbol`) (A9).
- [ ] Every in-text `§N` reference resolves to a numbered section (A8); the `§` glyph
      denotes this spec's own sections — a cross-document reference names the document.
- [ ] When an `Enforcement status` table is present, no prose claims an invariant
      "enforced" / "guaranteed" that the table marks review-only / planned / absent (A10).
- [ ] Every `path:lo-hi` range anchor closes (string/comment-aware) every bracket it opens (A11) —
      a citation cannot truncate a collection literal mid-structure.
- [ ] A certification that claims a non-trivial fold carries a `### Fold ledger` with a resolving
      `artifact:line` row per finding (R1); when rows are present each anchor resolves (A12); a clean
      certify (folded in: none) dozes.

### Reference: what `check_spec_ready` asserts

```
A1 fail unless >=1 "### §N" heading under "Numbered sections", all numbered
A2 fail unless each §N has a non-trivial "Acceptance criterion" (present, >=5 words)
A3 fail if regex (TBD|TODO|FIXME|\?\?\?) matches the spec body
A4 parse the PR<->section manifest: fail unless bijection(PRs, sections), full coverage
A5 each concept->module path: fail unless exists(path) or ("to be created" and claimed by a §)
A6 each `path:line` anchor: fail unless file exists, line in range, and any quoted snippet matches
A7 each cited `docs/adr/NNNN-...md`: fail unless that number is free on the base or names that ADR
A8 each bare intra-spec `§N` reference: fail unless it names a numbered section (skips `§N.M`, headings, doc-cued refs)
A9 each `**Model-on:**`/`**Reuse:**` reference present: fail unless the path exists (and the symbol, for `path::symbol`)
A10 when an Enforcement-status table is present: fail if prose claims an invariant "enforced"/"guaranteed" whose row is not enforced
A11 each `path:lo-hi` range anchor: fail unless it closes (string/comment-aware) every bracket it opens (single-line `path:line` anchors stay A6)
A12 when a `### Fold ledger` sub-table is present: fail unless each row's `artifact:line` confirmation anchor resolves
R1 a certification claiming a non-trivial fold must carry a `### Fold ledger` with >=1 resolving row (a deliberate tightening, not verify-when-present; a clean certify dozes)
B1 fail unless a "## Pre-mortem certification" block records Verdict: CERTIFIED (or CONDITIONAL-CERTIFY + a named Operator) + a Reviewer
```
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
- [ ] Every invariant the work touches is named in "Invariants touched", each with an ADR.
- [ ] Every concept maps to a module in the concept→module map.
- [ ] Every non-obvious design choice has an ADR (alternatives recorded).
- [ ] The spec is internally consistent (no section contradicts another).
- [ ] A post-fold coherence re-read was performed and recorded (`Post-fold coherence:` in
      the certification): each folded finding is applied consistently across all sections,
      and any scope-narrowing finding had its dependent counts re-derived.
- [ ] *(eval/experiment specs)* each measured criterion carries a one-line baseline expectation —
      will the control / `bare` arm plausibly pass it? — and the reviewer flagged ceiling/floor risk:
      a procedurally-perfect spec still measures nothing if its criteria cannot vary across arms.
- [ ] *(eval/experiment specs)* instrument defeatability — the reviewer asked the cheapest way an
      agent sidesteps the planted difficulty (a tool, a shortcut, a grep) so the run measures nothing;
      an instrument trivially bypassed yields a null for a reason the design never controlled (distinct
      from the ceiling/floor question above).
- [ ] *(eval/experiment specs)* feasibility-grounding ran FIRST — before internal-validity attacks, the
      reviewer grounded the headline's key variable against the empirical record it needs (prior-run
      data/ledger, the reused instrument); if that record cannot supply the variation the study measures,
      the study is null on these instruments and the rest of the review short-circuits.
- [ ] *(eval/experiment specs)* the experimental design is named, not just the subject: the estimand +
      unit of analysis (per-item delta vs aggregate); enough reps to detect the minimum effect worth
      detecting — a 1-rep delta is noise (a power question, distinct from feasibility above: power is
      whether N can detect the effect, feasibility is whether the record supplies the variable); blinding
      + held-constant factors; and a correctness oracle distinct from "ran green" (distinct from the
      baseline-expectation item).
- [ ] *(eval/experiment specs)* the causal path the study assumes is traced against code from BOTH ends:
      the measured path actually READS what the treatment changes (a treatment the measured call recomputes
      live or never reads is inert — mis-built, not null; distinct from feasibility), and the measured
      unit's capabilities beyond the intended input (tools, network, filesystem + cwd, prior/session state)
      include no side channel to the ground truth (a side channel CONFOUNDS the result — distinct from
      defeatability's null).
- [ ] *(eval/experiment specs)* every isolation / safety / leakage invariant the spec asserts names a
      buildable enforcement mechanism claimed by a numbered §/PR — not a bare assertion, and not a smoke
      that tests a jail no PR creates.
- [ ] *(eval/experiment specs)* the analysis plan is pre-registered — fixed before results are seen, not
      chosen after (the spec-template advertises this axis as DoR-gated; this is that gate).

**Gate result:** Ready ✅ only when Part A is well-formed **and** the Part B
pre-mortem certification is recorded. `keel check-ready` enforces both halves; the
remaining Part B items are the reviewer's evidence-backed certification, not a
self-signed checkbox. The gate verifies the certification was *recorded* by a named
non-author reviewer — not that the reviewer was truly blind or right; that residual
trust is named, not hidden (ADR-0002).
