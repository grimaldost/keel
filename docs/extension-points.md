# Extension points

Adding to keel follows its own three-way promotion rule (see `reflection-triage.md`):

- **New template / doctrine edit** — add a file to `src/keel/templates/` (and a row in
  `docs/templates-reference.md`); or amend `docs/doctrine.md`. Update `test_templates_valid.py`
  if it carries required sections.
- **New gate** — add `src/keel/<gate>.py` returning a `GateResult`, wire a `@app.command` in
  `src/keel/cli.py`, and pin it in `tests/`. Errors via `format_error`.
- **New plugin entry point** — add the file under `commands/` (or `skills/` / `agents/`) and a row
  in `docs/plugin-reference.md`;
  `test_plugin_manifest.py::test_plugin_reference_documents_every_entry_point` globs all three
  directories and fails if a shipped entry point is missing from that table.
- **New decision** — add a numbered ADR under `docs/adr/` and index it in `docs/adr/README.md`.

Every promotion is recorded in `CHANGELOG.md` with a version bump.
