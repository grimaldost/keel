# PR01 — Extend contract.py with source_host field

**Spec section:** spec-add-source-host-field.md §1

Implement the contract extension to add `source_host` as the fourth element of the record tuple.

## Acceptance criterion (from spec)

`make_record()` creates a 4-tuple with source_host in position [3];
`mypy src/` passes with explicit tuple type annotations; existing LEVELS validation persists;
ValueError is raised if source_host is empty or not a string.

## Implementation notes

- Modify `src/tempo/contract.py:1-13` (the entire contract module)
- Update `make_record(epoch_seconds, level, message, source_host)` signature
- Validate source_host as a non-empty string
- Update module docstring to reflect the new tuple shape
- Keep LEVELS validation unchanged

## Checklist

- [ ] make_record() accepts source_host parameter
- [ ] Record is created as 4-tuple with source_host in position [3]
- [ ] source_host is validated (non-empty string)
- [ ] Module docstring updated
- [ ] mypy src/ passes
- [ ] All tests pass (pytest tests/ -v)
