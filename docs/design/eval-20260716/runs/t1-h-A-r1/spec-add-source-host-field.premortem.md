# Pre-Mortem Review: Add source-host field to record contract

**Spec Path:** spec-add-source-host-field.md
**Spec-hash:** (computed by keel spec-hash)
**Reviewer:** pre-mortem-review agent (general-purpose)
**Date:** 2026-07-16
**Verdict:** CONDITIONAL-CERTIFY

## Summary

I have completed a grounded pre-mortem review of the refactor spec by reading and analyzing:
- Current code: contract.py (3-tuple), parse.py (input parsing), report.py (tuple unpacking), test_tempo.py (test coverage)
- Proposed spec: 4-section refactor to add source_host field
- Related: ADR-0001 (decision documented)

The spec has clear scope and intent. However, **5 MAJOR silent-failure risks** were identified in acceptance criteria that could allow bugs to ship undetected. All require only surgical edits — no design changes. No BLOCKER-level issues that aren't caught by tests.

## Findings

### MAJOR findings (5) — silent failures that could ship undetected

1. **FM-2 (MAJOR)**: Parser might pass arguments to make_record in wrong order
   - Evidence: spec §2 doesn't explicitly show `make_record(epoch, level, message, source_host)` call order
   - An implementer parsing input `EPOCH LEVEL SOURCE_HOST MESSAGE` might call `make_record(epoch, level, source_host, message)` (reversed)
   - Smallest fix: Add explicit code snippet to §2 showing correct parameter order in acceptance criterion

2. **FM-3 (MAJOR)**: Type annotations absent, mypy won't catch parameter order errors
   - Evidence: Spec §1 says "mypy passes" but only requires return-type, not parameter annotations; contract.py currently has zero type hints
   - mypy cannot validate parameter order without full type annotations
   - Smallest fix: Mandate parameter annotations in §1 acceptance: `def make_record(epoch_seconds: int, level: str, message: str, source_host: str) -> Tuple[int, str, str, str]`

3. **FM-4 (MAJOR)**: Validation for empty source_host location not specified
   - Evidence: Spec §1 says "validate" but doesn't assign to make_record(); could be only in parse_line, leaving make_record vulnerable
   - Acceptance criterion shows passing case but no ValueError test
   - Smallest fix: Add error-case to acceptance: `make_record(..., '') raises ValueError`; `make_record(..., None) raises ValueError`

4. **FM-5 (MAJOR)**: Test for empty source_host from parse_line input might be missing
   - Evidence: Spec §4 requires validation test but doesn't specify parse_line edge cases (e.g., input with <4 tokens)
   - Acceptance criterion doesn't show test like `assertRaises(ValueError, parse_line, '1700000000 INFO  message')`
   - Smallest fix: Add explicit §4 tests: `test_invalid_source_host` (direct make_record calls) and `test_invalid_input_format` (parse_line with <4 tokens)

5. **FM-6 (MINOR → folded as MAJOR risk)**: Parser split() maxsplit parameter not explicitly documented
   - Evidence: Spec §2 specifies format but shows no code; implementer might use `split(' ', 2)` (old) instead of `split(' ', 3)` (correct)
   - Smallest fix: Document: "Use `split(' ', 3)` to split at most 3 times, preserving MESSAGE containing spaces"

### BLOCKER (easily caught, not a design blocker)

- report.py:8 unpacks 3 elements `for _, level, _ in records:` but will receive 4-tuple → ValueError at runtime
- **Status:** This WILL be caught by pytest, so it's not a hidden blocker
- Spec §3 correctly requires fixing this; just lacked explicit unpacking example in acceptance criterion

### MINOR findings (4)

- **FM-7**: Type annotation syntax `level: LEVELS` is invalid (LEVELS is a frozenset, not a type); should be `level: str`
- **FM-8**: No error handling specified for malformed input (e.g., input with <4 tokens)
- **FM-9**: Definition of Done criterion "No tuple unpacking outside tested modules" is unverifiable without explicit grep/code-review step
- **FM-10**: Contract.py docstring update requirement has no template; wording could be unclear

## YAML Findings (for structured processing)

```yaml
findings:
  - id: FM-2
    severity: MAJOR
    finding: Parser might pass arguments to make_record in wrong order (source_host and message swapped)
    cause: §2 says extract and adopt signature from §1 but lacks explicit calling convention
    evidence: spec-add-source-host-field.md § 2 has no code snippet showing parameter order
    smallest_fix: Add to §2 code pattern showing make_record(epoch, level, message, source_host) parameter order explicitly

  - id: FM-3
    severity: MAJOR
    finding: Type annotations absent, mypy cannot catch parameter order errors
    cause: §1 acceptance says mypy passes but only requires return-type, not parameter annotations
    evidence: contract.py:10 has zero type hints; mypy won't validate parameter order
    smallest_fix: Mandate parameter annotations in §1 acceptance criterion - full signature with types

  - id: FM-4
    severity: MAJOR
    finding: Validation for empty source_host location not specified (could be only in parse_line)
    cause: §1 says validate but doesn't assign to make_record(); make_record could skip validation
    evidence: spec-add-source-host-field.md §1 shows passing case, no ValueError test
    smallest_fix: Add error-case to §1 acceptance - make_record(..., '') raises ValueError

  - id: FM-5
    severity: MAJOR
    finding: Test for empty source_host from parse_line input might be missing
    cause: §4 requires validation test but doesn't specify parse_line edge cases
    evidence: spec-add-source-host-field.md §4 doesn't show test for parse_line with <4 tokens
    smallest_fix: Add explicit §4 tests - test_invalid_source_host and test_invalid_input_format

  - id: FM-6
    severity: MINOR
    finding: Parser split() maxsplit parameter not explicitly documented
    cause: §2 specifies format but shows no code example
    evidence: Implementer might use split(' ', 2) or split() by mistake
    smallest_fix: Document split(' ', 3) requirement in §2 acceptance criterion
```

## Verdict: CONDITIONAL-CERTIFY

**Reasoning:** The spec has clear scope and intent, and the sections map well to implementation. However, 5 MAJOR silent-failure risks exist in acceptance criteria that could allow bugs to ship undetected:
- Parameter order confusion (reversed arguments)
- Type validation gaps (no type checking without annotations)
- Validation bypass (make_record might not validate)
- Test coverage gaps (edge cases not specified)
- Implementation ambiguity (split logic not explicit)

**All issues are surgical — no design changes needed.** The fixes involve:
1. Adding explicit type annotations to §1 acceptance
2. Showing parameter order in §2 acceptance
3. Adding error-case tests to §1 and §4 acceptance
4. Documenting split(' ', 3) in §2

After these amendments, the spec is ready for implementation.

**Condition:** The spec is ready for Decompose phase once the 5 MAJOR findings are folded back into the acceptance criteria (verification: re-run `keel check-ready` after fold and confirm Part A passes and fold ledger is recorded).

---

*This review grounded claims against contract.py, parse.py, report.py, test_tempo.py source code.*

PREMORTEM-VERDICT: CONDITIONAL-CERTIFY
