# Spec — Add a source-host field to the record contract

- **Date:** 2026-07-16
- **Status:** draft
- **Audience:** tempo maintainers, and any external consumer that imports `tempo.contract`
- **Output artifact(s):** `src/tempo/contract.py`, `src/tempo/parse.py`, `src/tempo/report.py`, `tests/test_tempo.py`, `CHANGELOG.md`, `README.md`

## Context

`src/tempo/contract.py:1` `"""The shared record contract: every tempo record is (epoch_seconds, level, message).` states the record shape, and `src/tempo/contract.py:3` `Imported by parse.py, report.py, and external consumers - changing this tuple shape or the` names exactly who depends on it: the parser, the reporter, and consumers outside this repo. We need every record to carry a `source_host` field. `docs/adr/0001-source-host-field.md` records the decision this spec implements: extend the contract with an optional field first, decouple the reporter from fixed-arity unpacking before the shape changes under it, migrate the parser and the reporter, publish migration guidance for external consumers, and only then make the field required. That ADR's "Consequences" section is the invariant this spec's section ordering exists to protect.

## Goal

Add a `source_host` field to every tempo record, rolled out across the parser, the reporter, and documented for external consumers, without any PR in the wave leaving the reporter unable to process the records the parser produces.

## Gate commands

`python3 -m unittest discover -s tests -v` (`README.md:6` `python3 -m unittest discover -s tests -v`) — the only gate command established in this project; `AGENTS.md:4` `python3 -m unittest discover -s tests` names the same command without `-v`. This project has no `ruff` or `mypy` configuration wired in (both binaries are present on `PATH` but neither is invoked by any established project command), so neither is part of this spec's gate — see Non-goals.

## Non-goals

- No change to `LEVELS` or the level-validation raise in `make_record` (`src/tempo/contract.py:10-11`) — out of scope for this wave.
- No new persistence, storage, or schema layer — the contract stays a plain tuple, per `docs/adr/0001-source-host-field.md`'s rejection of a dict/dataclass representation.
- No migration of already-written historical log lines — only lines parsed after §3/§4 land pick up the new format; existing log files are not rewritten.
- No host validation, canonicalization, or allow-list — `source_host` is accepted as an opaque string (or `None`), unchecked.
- No performance work.
- No code changes to any external consumer — this repository contains none in-tree. §6 delivers migration guidance (a CHANGELOG entry and a README update) for consumers outside this repository; it does not touch their code.
- No `ruff`/`mypy` configuration is added as part of this wave.

## Invariants touched

- **Record contract shape** — the record's field count and order (`docs/adr/0001-source-host-field.md`).
- **Consumer arity independence** — no in-repo consumer of a contract record may unpack it at fixed arity, an invariant this ADR creates precisely because the shape is about to change (`docs/adr/0001-source-host-field.md`, "Consequences").

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| Record contract shape (4 fields, `source_host` eventually required) | planned | none yet — `make_record` gains the field with a default in §2 and only requires it starting in §7; see the Enforcement status note in §7 |
| Consumer arity independence (no fixed-arity record unpacking) | planned | none yet — a reviewer greps the diff for a fixed-arity `for a, b, c in records` pattern per PR until a guardrail script exists; not automated in this wave |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| Record contract shape (optional, then required, `source_host` field) | `src/tempo/contract.py` |
| Arity-independent record consumption | `src/tempo/report.py` |
| Log-line parsing of the host token (new format + back-compat) | `src/tempo/parse.py` |
| Per-host record aggregation | `src/tempo/report.py` |
| Contract-change release notes and migration guidance | `CHANGELOG.md` (to be created) |
| Record-format description for readers | `README.md` |
| Regression coverage for the new field and both line formats | `tests/test_tempo.py` |

## Numbered sections

### §1 Decouple the reporter from fixed-arity record unpacking
`src/tempo/report.py:8` `for _, level, _ in records:` unpacks every record assuming it is exactly a 3-tuple. Change `count_by_level` to index-based access (`record[1]` for the level) so it tolerates both the current 3-field record and the 4-field record §2 introduces, landing this decoupling strictly before the arity change it protects against (`docs/adr/0001-source-host-field.md`, "Consequences"). **Acceptance criterion:** `count_by_level` produces identical, correct counts for a mix of 3-element and 4-element input records in a parametrized test, and no line in `report.py` unpacks a record via a fixed-arity tuple assignment.

### §2 Add an optional `source_host` field to the contract
Extend `make_record` in `src/tempo/contract.py:9-12` with a fourth parameter, `source_host=None`, so it returns `(int(epoch_seconds), level, message, source_host)`, and update the module docstring at `src/tempo/contract.py:1` to describe the 4-field shape and the optional-then-required rollout named in `docs/adr/0001-source-host-field.md`. Existing 3-argument calls keep working unchanged (host defaults to `None`). **Acceptance criterion:** `make_record(epoch, level, msg)` returns a 4-tuple with `None` in the fourth position, and `make_record(epoch, level, msg, host)` returns `host` in that position.

### §3 Parse the source host from the new line format
Update `parse_line` in `src/tempo/parse.py:6-8` to parse the 4-token format `EPOCH LEVEL HOST MESSAGE` — host is a single whitespace-free token, and the message keeps consuming the rest of the line via `maxsplit` — and pass the parsed host through to `make_record`. Update the module docstring at `src/tempo/parse.py:1` to describe the new format alongside the old one. **Acceptance criterion:** parsing `"1700000000 INFO web-1 started"` yields a record whose host field equals `"web-1"` and whose message field equals `"started"`.

### §4 Keep back-compatible parsing of the old 3-token format
`parse_line` also accepts the pre-existing 3-token format (`EPOCH LEVEL MESSAGE`, no host token), producing a record with `source_host=None`, so a log source that has not yet been updated to emit a host keeps parsing correctly during the rollout. **Acceptance criterion:** parsing `"1700000000 INFO started"` (no host token) still succeeds, yields a record with host `None`, and both the 3-token and 4-token formats are covered by tests.

### §5 Report per-host counts
Add a `count_by_host` function to `src/tempo/report.py` (alongside `count_by_level`, `src/tempo/report.py:6-10`) that aggregates records by their `source_host` field, so the reporter actually consumes the new field rather than merely tolerating its presence. **Reuse:** `src/tempo/report.py::count_by_level` — reuse its dict-accumulation pattern. **Acceptance criterion:** `count_by_host` returns a mapping from host value (including `None` for host-less records) to a count, tested against a mix of hosted and host-less records.

### §6 Document the contract change for external consumers
Add `CHANGELOG.md` (to be created) recording the `source_host` addition: the two rollout phases (§2's optional field, §7's required field), and explicit migration guidance for any external consumer that unpacks a record at fixed arity, referencing `src/tempo/contract.py:3` `Imported by parse.py, report.py, and external consumers - changing this tuple shape or the` as the reason such consumers are in scope for this notice. Update `README.md:3-4` to mention the `source_host` field in the record-format description. **Acceptance criterion:** `CHANGELOG.md` exists with a dated entry naming the field, both rollout phases, and migration guidance for fixed-arity unpacking; `README.md`'s record-format description mentions `source_host`.

### §7 Cutover: make `source_host` required
Once §1–§6 have landed, remove the `None` default from `make_record`'s `source_host` parameter in `src/tempo/contract.py` and remove the 3-token back-compat branch §4 added to `parse_line`, so the record shape is fixed at 4 required fields going forward — the target state the Enforcement status table's "Record contract shape" row describes. This PR also flips that table row's Status column from `planned` to the fully-enforced state, since Python's own signature check now rejects a call missing the argument. **Acceptance criterion:** `make_record(epoch, level, msg)` (3 positional arguments) raises `TypeError`, and `parse_line` given a 3-token line raises rather than silently defaulting the host.

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |
| PR03 | §3 | yes |
| PR04 | §4 | yes |
| PR05 | §5 | yes |
| PR06 | §6 | yes |
| PR07 | §7 | yes |

## Definition of Done (this spec)

- Generated / mirrored / snapshot artifacts downstream of touched surfaces: none — this project has no generated mirrors, golden fixtures, or lockfiles.
- Release notes: `CHANGELOG.md` (created in §6) carries the `source_host` entry in the same wave that introduces and requires the field — release-notes-in-wave, not a terminal cleanup.
- Every section's acceptance criterion is met and covered by a test in `tests/test_tempo.py`.
- `python3 -m unittest discover -s tests -v` passes after every PR in the manifest.

## Pre-mortem certification

- **Reviewer:**
- **Verdict:** not yet certified
- **Operator:**
- **Certification artifact:**
- **Date:**
- **Reviewed against:**
- **Post-fold coherence:**
- **Failure modes considered & folded in:**

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|
