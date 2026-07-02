# ADR-0012: the publication boundary — public claims must not cite private evidence

- **Status:** Accepted
- **Date:** 2026-07-01
- **Relates to:** ADR-0003 (thinness & consumer-agnosticism)

## Context

The skeptic panel (`docs/feedback/2026-07-01-skeptic-panel-fable5.md`, findings ARCH-2 / CS-7 / E2)
found that **every load-bearing empirical claim in the public repo cites evidence the repo
gitignores.** `docs/feedback/*` (except its README) and `docs/design/` are excluded (`.gitignore`),
yet the public doctrine cites them: the "validated on three governed waves" note, the ~$417
confounded-run figure, the 30× / $347 / $853 cost accounting, and every CHANGELOG "Origin" line point
at paths that 404 in a fresh clone. A tool whose own method demands that every cited path resolve (A6)
ships a front page whose citations dangle — by its own grounding rule, un-groundable.

The gitignore is deliberate and correct: those reports are dogfooding history against **real consumer
projects** and carry project detail that should not be published. The defect is not that the evidence
is private; it is that the **public documents cite it as if it were public.**

## Decision

**A published document may not cite an unpublished path as evidence.** The evidence corpus stays
maintainer-local (privacy). To close the dangling-citation gap:

1. A published `docs/evidence.md` states what the public repo can and cannot substantiate: the method
   is validated observationally on three governed waves and a field-report corpus that is
   **maintainer-local and unpublished**; the controlled experiment is pending (ADR-0013); the cost
   figures come from one program retro. It labels the evidence base honestly rather than pointing at
   files a reader cannot open.
2. `docs/doctrine.md`'s evidence-status and cost notes gain a one-line "(sources maintainer-local,
   unpublished; see `docs/evidence.md`)" qualifier, so the strongest public claims are honestly framed.
3. **Standing rule:** new public docs cite either a committed path or an explicitly-labelled
   "(maintainer-local, unpublished)" source — never a gitignored path as if it resolved. CHANGELOG
   "Origin" lines are grandfathered (they are historical provenance, not a live claim to verify) but
   should carry the label going forward.

## Alternatives considered

- **Commit redacted/fictionalized versions of the load-bearing reports** (as done for the
  `acme-ledger` worked example). Rejected for now: faithful redaction of dozens of consumer reports is
  a large, error-prone effort, and a summary digest (`docs/evidence.md`) gives a public reader the
  same honest picture without republishing consumer detail. Left open as a future option if a stronger
  public evidence base is wanted.
- **Publish the whole corpus.** Rejected: it contains real consumer-project detail (ADR-0003 keeps
  keel from reaching into consumers; publishing their field reports would breach the same boundary).
- **Do nothing (the citations are "internal").** Rejected: the panel showed a fresh clone cannot
  resolve them, and keel holds consumer specs to exactly this standard (a cited referent must resolve).

## Consequences

- The public repo stops asserting claims it points at invisible files to support; a reader gets an
  honest `docs/evidence.md` instead of a dangling path.
- The evidence base remains thin and single-operator — that limitation is now stated plainly in-tree,
  not implied by citations no one can follow. Strengthening it (running the experiment, publishing a
  redacted digest) is tracked in ADR-0013.
- No change to the gitignore or to the method: this is a documentation-honesty boundary, consistent
  with ADR-0003's "keel does not expose consumer detail."
