# Spec — region rollup for tinyetl

- **Date:** 2026-08-11
- **Status:** ready (DoR passed)
- **Kit:** 0.14.0
- **Kind:** series
- **Audience:** the tinyetl maintainers and the reviewer who certifies this spec
- **Output artifact(s):** src/tinyetl/currency.py, src/tinyetl/orders.py

## Context

tinyetl reads order rows and reports totals per region. The rollup is written but the
currency handling is not, and the region vocabulary has no single home.

## Goal

Give the rollup a closed region vocabulary and a currency normaliser, so a report can
be produced from raw order rows without per-caller conversion code.

## Gate commands

`ruff format --check .`, `ruff check .`, `ty check src`, `pytest`.

## Non-goals

No change to the on-disk order format, and no new reporting surface. Historical
backfills stay out of scope.

## Invariants touched

The rollup emits one entry per region code seen (`docs/adr/0001-one-row-per-region.md`),
and the region vocabulary stays closed (`docs/adr/0002-region-codes-are-closed.md`).

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| one entry per region code | enforced | a unit test over `rollup_by_region` |
| currency codes come from a closed set | planned | the §3 normaliser, once it lands |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| order loader | `src/tinyetl/orders.py` |
| region vocabulary | `src/tinyetl/regions.py` |
| currency normaliser | `src/tinyetl/currency.py` (to be created) |

## Numbered sections

### §1 Keep the required-column filter honest

`load_orders` drops rows missing any required column; the column tuple is
`src/tinyetl/orders.py:5-10`. **Acceptance criterion:** a row missing `amount_cents`
is dropped and a unit test asserts the surviving row count.

### §2 Total amounts per region

`src/tinyetl/orders.py:18` `def rollup_by_region` sums per region code.
**Reuse:** `src/tinyetl/orders.py::rollup_by_region`
**Acceptance criterion:** two orders in one region produce one entry whose total is
their sum, asserted by a unit test.

### §3 Add the currency normaliser

A new module `src/tinyetl/currency.py` converts an amount to minor units before §2
totals it. **Acceptance criterion:** an amount given in a non-base currency is
converted before the rollup, and a unit test pins the converted total.

### §4 Close the region vocabulary

`src/tinyetl/regions.py:3` `REGION_CODES = {` is the closed set; `region_name` passes
an unknown code through. **Acceptance criterion:** an unknown region code round-trips
unchanged and a unit test asserts no invention.

### §5 Wire the rollup into the report

The report calls §2 once per run and renders the region display names from §4.
**Acceptance criterion:** the report lists one line per region, in the vocabulary's
order, asserted by an integration test.

### §6 Record the invariant status table

The status table above gains a row per invariant §3 introduces, with the gate that
holds it. **Acceptance criterion:** every invariant named in this spec has a status
row, asserted by a docs-sync check.

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |
| PR03 | §3 | yes |
| PR04 | §4 | yes |
| PR05 | §5 | yes |
| PR06 | §6 | yes |

## Definition of Done (this spec)

- Generated / mirrored / snapshot artifacts downstream of touched surfaces: none.
- The four gate commands above pass locally and in CI.

## Pre-mortem certification

- **Reviewer:** a reviewer who did not author this spec
- **Verdict:** CERTIFIED
- **Certification artifact:** `clean-series.premortem.md`
- **Date:** 2026-08-11
- **Post-fold coherence:** re-read after the fold; §2 and §5 still agree on the unit.
- **Failure modes considered & folded in:** two, both re-anchored below.

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|
| FM-1 the filter dropped valid rows | §1 | `src/tinyetl/orders.py:15` | yes |
| FM-2 an unknown code was invented | §4 | `src/tinyetl/regions.py:12` | yes |
