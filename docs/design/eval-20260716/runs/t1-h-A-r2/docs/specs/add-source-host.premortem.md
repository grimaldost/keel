# Pre-mortem review — Add source-host field to tempo record contract

- **Spec path:** `docs/specs/add-source-host.md`
- **Reviewer:** pre-mortem-review agent (blind, non-author pass)
- **Date:** 2026-07-16
- **Verdict:** CERTIFIED (after two-pass review and fixes)

## Review Process

This spec underwent a two-pass pre-mortem review:

1. **Initial pass (NEEDS-REVISION):** Found 2 BLOCKERS and 6 MAJORS, indicating critical implementation hazards.
2. **Follow-up pass (CERTIFIED):** All 8 findings were adequately resolved through targeted spec edits; no new blockers or majors introduced.

## Issues Found & Resolved

| Issue | Severity | Finding | Fix Applied | Status |
|-------|----------|---------|-------------|--------|
| PM-001 | BLOCKER | Gate command hardcoded to /tmp/... path | Changed to relative path `./bin/keel check-ready docs/specs/add-source-host.md` | RESOLVED |
| PM-002 | BLOCKER | rsplit instruction breaks MESSAGE-with-spaces parsing | Changed to `split(None, 3)` with explicit test case | RESOLVED |
| PM-003 | MAJOR | Missing edge case in acceptance criterion | Added explicit test: `parse_line("...message with spaces...")` | RESOLVED |
| PM-004 | MAJOR | Source-host validation order unspecified | Defined order: type check → semantic check → error message format | RESOLVED |
| PM-005 | MAJOR | Ambiguous handling intent in §3 (ignore vs compute?) | Clarified: source-host is IGNORED in count_by_level; unpacking only | RESOLVED |
| PM-006 | MAJOR | DoD contradicted breaking change claim | Updated DoD to acknowledge breaking change explicitly | RESOLVED |
| PM-007 | MAJOR | Test coverage criterion too vague | Specified: coverage for `make_record()`, `parse_line()`, new test cases | RESOLVED |
| PM-008 | MAJOR | Line-number references become stale | Replaced with function-name notation (e.g., `src/tempo/contract.py::make_record()`) | RESOLVED |

## Follow-up Verification

The follow-up pass verified each resolved issue:
- Gate command: relative path confirmed ✓
- Parsing logic: split(None, 3) verified correct for spaces in MESSAGE ✓
- Edge cases: explicit acceptance criteria for spaces, empty string, None, integers ✓
- Validation: order (after level, before return) and error message format specified ✓
- Handling clarity: §3 unambiguously states source-host is ignored ✓
- DoD changes: breaking change acknowledged in both context and DoD ✓
- Test scope: functions explicitly named in coverage criterion ✓
- References: all use function names and module paths, not line numbers ✓

## No Unresolved Issues

The second pass found zero new BLOCKER, MAJOR, or blocking MINOR issues. All prior findings are resolved and confirmed adequate. The spec is ready for implementation.

---

This spec is ready to proceed to Decompose phase. All execution blockers have been eliminated. Numbered sections are clear, acceptance criteria are testable, and PR↔section mapping is 1:1 with no scope creep.

Reviewer: pre-mortem-review agent (two-pass, certified 2026-07-16)
Spec-hash: (to be recorded by operator at merge)

PREMORTEM-VERDICT: CERTIFIED pre-mortem-review-agent-2026-07-16
