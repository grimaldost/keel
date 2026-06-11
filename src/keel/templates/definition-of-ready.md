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

### Reference: what `check_spec_ready` asserts (keel 0.3.0)

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
B1 fail unless a "## Pre-mortem certification" block records Verdict: CERTIFIED + a Reviewer
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
      block records `Verdict: CERTIFIED`. *(`keel check-ready` enforces this — B1.)*
- [ ] Every invariant the work touches is named in "Invariants touched", each with an ADR.
- [ ] Every concept maps to a module in the concept→module map.
- [ ] Every non-obvious design choice has an ADR (alternatives recorded).
- [ ] The spec is internally consistent (no section contradicts another).
- [ ] A post-fold coherence re-read was performed and recorded (`Post-fold coherence:` in
      the certification): each folded finding is applied consistently across all sections,
      and any scope-narrowing finding had its dependent counts re-derived.

**Gate result:** Ready ✅ only when Part A is well-formed **and** the Part B
pre-mortem certification is recorded. `keel check-ready` enforces both halves; the
remaining Part B items are the reviewer's evidence-backed certification, not a
self-signed checkbox. The gate verifies the certification was *recorded* by a named
non-author reviewer — not that the reviewer was truly blind or right; that residual
trust is named, not hidden (ADR-0002).
