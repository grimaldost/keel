# PR03 — Update reporter to handle 4-tuple records

**Spec section:** spec-add-source-host-field.md §3

Implement the reporter update to correctly handle the new 4-tuple record structure.

## Acceptance criterion (from spec)

`count_by_level()` accepts 4-tuples and returns correct counts;
`mypy src/` passes; the reporter's output shape is unchanged from caller perspective (counts
are still `{level: count}` dicts).

## Implementation notes

- Modify `src/tempo/report.py:6-10` (the count_by_level function)
- Update tuple unpacking to handle 4-tuple: `epoch, level, msg, host = record`
- Preserve counting behavior (source_host does not change the counting logic)
- Ensure caller-visible output (count dicts) remains unchanged

## Checklist

- [ ] count_by_level() handles 4-tuple records
- [ ] Tuple unpacking correctly extracts all 4 elements
- [ ] Counting logic is unchanged
- [ ] count_by_level returns {level: count} dicts as before
- [ ] mypy src/ passes
- [ ] All tests pass (pytest tests/ -v)
