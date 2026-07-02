# Evidence status

What this public repository can and cannot substantiate about the method's central claim. Written to
keep the doctrine honest: keel holds consumer specs to "every cited referent resolves," so its own
public claims must not lean on files a reader cannot open (ADR-0012).

## The claim

The method's wager (`docs/doctrine.md` §1): *enforced discipline beats intended discipline* — pushing
control flow into durable artifacts and deterministic machines produces higher cohesion at scale than a
careful generic agentic flow. This is **designed to, and so far observed to**, not **measured to beat** a
disciplined baseline.

## What is public and verifiable in this repo

- **The mechanisms.** The gates (`src/keel/`), templates, doctrine, ADRs, and their tests are all here.
  You can read exactly what is enforced, run the suite, and confirm the gate does what it documents
  (ADR-0011). "A promoted check ships with a regression test" is machine-checkable in-tree.
- **The self-application.** keel's own releases are governed by keel (specs, ADRs, CHANGELOG, the
  dogfood re-run of `check-ready` on each release spec). The commit and ADR history is public.
- **Honest limits, in-tree.** Where a discipline is *not* mechanized (gate hit-rate tracking,
  fail-closed reflection triage), the docs now say so (`CONTRIBUTING.md`, doctrine §2) rather than
  claiming enforcement keel does not ship.

## What is NOT public (maintainer-local, unpublished)

The field-report corpus (`docs/feedback/`) and the release/design specs (`docs/design/`) are gitignored
because they contain detail from **real consumer projects**; publishing them would breach the same
consumer boundary ADR-0003 keeps keel behind. So a public reader **cannot** independently verify:

- the "validated on three governed waves" observation;
- the cost figures (~$347 as ~41% of an $853 program; the ~$417 confounded-run anecdote);
- the "Origin" citations in `CHANGELOG.md` (they name maintainer-local reports).

Treat these as the maintainer's honest field notes, not as independently checkable public evidence.

## The gap keel owes itself

The controlled experiment against a disciplined baseline (`docs/design/2026-06-06-keel-validation-experiment.md`,
maintainer-local) was designed but has not run. Until it does, the comparative headline is a wager. keel
has committed to **run a scoped version under its own measurement lane and publish the result, or
retire the comparative claim by ADR, by 0.13.0** (ADR-0013). This document will be updated with the
outcome.
