# PR04 — Extend tests to validate source_host

**Spec section:** spec-add-source-host-field.md §4

Implement comprehensive tests for the new source_host field and updated tuple structure.

## Acceptance criterion (from spec)

`pytest tests/ -v` passes all tests including new source_host validation tests; test_parse_and_count is updated to use new format and verifies source_host
is present in records; a new test validates source_host rejection of empty/None values.

## Implementation notes

- Modify `tests/test_tempo.py:12-16` (update existing tests)
- Add test fixtures that use the new 4-tuple structure
- Update existing test_parse_and_count to use new input format
- Add tests for source_host validation (non-empty string, not None)
- Add tests for parser extraction of source_host from input
- Verify all tests pass against the new contract shape

## Checklist

- [ ] Test fixtures use new 4-tuple record structure
- [ ] test_parse_and_count updated to parse new format
- [ ] source_host validation tests added
- [ ] Parser extraction tests added
- [ ] All tests assert correct source_host presence and values
- [ ] mypy src/ passes
- [ ] All tests pass (pytest tests/ -v)
