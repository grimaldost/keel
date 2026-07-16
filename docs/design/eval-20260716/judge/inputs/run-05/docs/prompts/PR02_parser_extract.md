# PR02 — Update parser to extract source_host from input

**Spec section:** spec-add-source-host-field.md §2

Implement the parser update to extract source_host from the new input format.

## Acceptance criterion (from spec)

`parse_line('1700000000 INFO myhost started')` yields
`(1700000000, 'INFO', 'started', 'myhost')` in the correct positions; spaces in MESSAGE are
preserved; `mypy src/` passes; existing tests adapted to new format pass.

## Implementation notes

- Modify `src/tempo/parse.py:6-8` (the parse_line function)
- Change input format from "EPOCH LEVEL MESSAGE" to "EPOCH LEVEL SOURCE_HOST MESSAGE"
- Extract source_host as the third whitespace-delimited token
- Preserve spaces in MESSAGE (split on first 3 spaces only)
- Pass source_host to make_record()

## Checklist

- [ ] parse_line() expects new format with source_host
- [ ] source_host extracted correctly from input
- [ ] Spaces in MESSAGE are preserved
- [ ] parse_line calls make_record with source_host parameter
- [ ] mypy src/ passes
- [ ] All tests pass (pytest tests/ -v)
