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

## Pre-registration for the gate hit-rate ledger (KEEL-B07)

Written before any data arrived, so a later reading cannot be fitted to the numbers it finds.
`keel gate-health` reports the counts; this section fixes in advance what each count would mean.

**What the ledger will show, expected.** Zero fires *with* material: A7, A9, A1, A4, A2. Zero
*material* until the header stamp and resolved kind reach real specs: A0, W1. Live: A6, A12, R1,
A5; W2, W3, B2, and B1 as a record rather than a rejecter. Uninformative by construction until
A10's three reproduced defeats are fixed: A10. Directional: W3 arriving should lower A6 fires per
run, and cause-grouping should pull violations-per-cause below 3.

**Dispositions the ledger fires on its own** — pre-registered, so they are not re-argued later:

| trigger | disposition |
|---|---|
| A7 or A9 reaches ≥40 candidates across ≥15 distinct revisions in ≥3 repos with zero fires, **and** its positive control passes | demote to WARN, recorded with the ledger figures |
| either fires once in the field | the demotion rule is cancelled and the row returns to KEEP |
| A0 or W1 material stays 0 after 10 forward runs | the authoring surface is the defect, not the check — reopen the header stamp, do not touch the check |
| B1's certify rate reaches 100% **and** the fraction of certifications followed by a further spec edit falls | the reviewer, not the check, has stopped working — a reviewer that never returns a non-certify verdict is measuring nothing, and nothing would otherwise notice |
| A8 needs a third false-positive widening | A8 re-enters review as fitted-to-noise |

Two demotions were argued for during the design of this instrument and are **not** taken here:
A7 has 33–34 material units across 18 specs and A9 has 12 across 7, and the standing bar is ≥40
across ≥15 revisions in ≥3 repos. Neither clears it. Honest still-unmeasured beats a forced
verdict, and the table above is what turns that into a decision the data can make by itself.

**What the ledger cannot answer.** Whether a check is *worth* its author-side cost, and whether a
gated spec produces a better wave. It counts opportunity and fires. The rest is §ADR-0015's
retired claim, and this instrument does not reopen it.

## The comparative claim is retired (ADR-0015)

The controlled experiment against a disciplined baseline (designed 2026-06-06, maintainer-local) never
ran. At the ADR-0013 deadline keel retired the comparative headline instead of running it: the best
available instrument evidence — the public `fathom` eval harness (`github.com/grimaldost/fathom`, its
ledgers committed) — shows current strong models at the correctness ceiling on every self-contained task
bank tried (0/180 correctness failures at n=45 on the two hardest banks), so a matched-pair run at
authoring-feasible task scale cannot distinguish the method from a disciplined baseline; it would return
a null by instrument, not a verdict. What stands is observational only: *designed to, and so far observed
to*. The observational ledger (per wave: failure modes predicted → materialized → catch cost) continues
in the maintainer-local field corpus.

**Reopening path (named, unscheduled — not a deferral):** a coordination-scale fathom bank — ≥8 matched
task pairs above the doctrine §6 blast-radius trigger (≈80–100 trials), the keel arm mounted as a plugin,
blind verifier-first scoring, an estimated $150–400 token-priced matrix on top of an 8–12-unit authoring
series (priced design: maintainer-local, 2026-07). No date is attached and no run is owed; the comparative
claim stays retired unless that run happens and favours the method, and this document records the outcome
either way.
