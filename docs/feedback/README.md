# Feedback intake

Each application of keel (e.g. a governed wave on a consumer project) drops one report here.

**Filename:** `<YYYY-MM-DD>-<source>.md` (e.g. `2026-06-10-acme-authenticator.md`), source slug
distinct per wave/phase so reports never clobber earlier ones.

**Format (as of 2026-06-09):** the `session-workflow:tool-feedback` skill template
(craft-collection session-workflow >= 0.2.0) is the authoritative format for this directory —
it was derived from this intake's original six sections, plus the structure triage needs:

- Header block: date · tool/version (read from the manifest, never guessed) · context · outcome.
- Sections: **What worked** · **Friction** · **Misses** · **Vacuous gates** ("none observed" is
  a valid entry) · **Proposed promotions / changes** · **Cost** (optional).
- Severity tags `[BLOCKER|HIGH|MED|LOW]` on friction, misses, and proposals.
- Every miss names the phase that should have caught it (`phase: DoR`, `phase: pre-mortem`,
  `phase: gate`, `phase: review`).
- Numbered proposals are the report's **stable finding IDs** (`<file-stem>#<n>`) — what triage
  docs and the CHANGELOG cite. Repeats of an earlier report's finding are written as
  `extends <prior-file-stem>#<n>` with the new evidence only, never restated fresh.

Reports written before 2026-06-09 predate the template and stay as-is; triage cites those by
file stem + section.

Reports are inputs to `src/keel/templates/reflection-triage.md` — triage promotes recurring
traps into durable checks and records them in `CHANGELOG.md` (see `CONTRIBUTING.md`). The
`session-workflow:feedback-triage` skill defers to that registered template when triaging this
directory.
