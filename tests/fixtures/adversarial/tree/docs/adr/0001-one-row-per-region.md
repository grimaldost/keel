# ADR-0001 — the rollup emits one row per region

- **Status:** Accepted
- **Date:** 2026-03-02

## Decision

`rollup_by_region` returns exactly one entry per region code seen in the input, so a
downstream join never fans out.
