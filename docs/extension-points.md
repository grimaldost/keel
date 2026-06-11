# Extension points

Adding to keel follows its own three-way promotion rule (see `reflection-triage.md`):

- **New template / doctrine edit** — add a file to `src/keel/templates/` (and a row in
  `docs/templates-reference.md`); or amend `docs/doctrine.md`. Update `test_templates_valid.py`
  if it carries required sections.
- **New gate** — add `src/keel/<gate>.py` returning a `GateResult`, wire a `@app.command` in
  `src/keel/cli.py`, and pin it in `tests/`. Errors via `format_error`.
- **New decision** — add a numbered ADR under `docs/adr/` and index it in `docs/adr/README.md`.

Every promotion is recorded in `CHANGELOG.md` with a version bump.
