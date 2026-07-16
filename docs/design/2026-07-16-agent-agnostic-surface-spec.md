# Spec — The agent-agnostic surface (any-agent keel)

- **Date:** 2026-07-16
- **Status:** ready (DoR passed)
- **Audience:** the implementing wave (one PR per section) and its reviewers
- **Output artifact(s):** `src/keel/method/` (packaged corpus), `src/keel/assets.py`,
  the `keel show` command, a thinned plugin surface, `src/keel/templates/method-agents-snippet.md`,
  agnostic install/usage docs, the 0.14.0 release notes

## Context

keel ships the method as a Claude Code plugin plus a CLI (ADR-0001), but the method's *content*
is reachable only through the plugin or a repo checkout. The audit behind ADR-0017 found the
coupling concentrated in path resolution and packaging, not in the method itself:

- The skill resolved the doctrine through an environment variable only Claude Code sets —
  `${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md` in the pre-wave skill body (§4 removed the form).
- A CLI-only install carries the template kit but not the doctrine: the build packages only
  `src/keel/` (`pyproject.toml:23` `build-backend = 'uv_build'`), while the doctrine lives at
  `docs/doctrine.md` — outside the package.
- The doctrine is the named source of truth (`AGENTS.md:17` `docs/doctrine.md`), so it must not
  move; it must be *mirrored* into the package under a freshness gate.
- The pre-mortem prompt is already packaged and drift-guarded against the bundled Claude agent
  (`tests/test_premortem_agent.py:25` `pre-mortem-prompt.md`), so the portable pre-mortem needs
  no new prose — only a portable way to read it.
- The hooks slot is an empty placeholder (`hooks/hooks.json:2` `"hooks": {}`) — nothing to port.

ADR-0017 (`docs/adr/0017-the-agent-agnostic-surface.md`) decides the shape: the CLI becomes the
single portable entry point; agent-specific artifacts become thin shims; MCP and per-agent
adapters are named deferrals. This spec is that decision made executable.

## Goal

After this wave, any AI agent that can run a shell applies the full method from one pinned
entry point — install via `uvx`, read the corpus via `keel show`, route in via an `AGENTS.md`
snippet — while the Claude Code plugin keeps working, thinner.

## Gate commands

Run each unpiped, from the repo root:

- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run ty check src`
- `uv run pytest`
- DoR for this spec: `uv run keel check-ready docs/design/2026-07-16-agent-agnostic-surface-spec.md`

## Non-goals

- **No MCP server** and **no per-agent adapter generators** (Gemini CLI / Cursor / Copilot
  formats) — named deferrals with their un-defer triggers recorded in ADR-0017.
- **No removal or rename of the Claude plugin surface** — the skill, commands, agent, and
  manifests keep their names and discovery behavior; only their bodies thin.
- **No change to gate semantics** — exit codes 0/1/2, `GateResult`, and check-ready's A/B
  checks are untouched.
- **No doctrine content edits** — the packaged copy is a byte-identical mirror, not a revision.
- **No PyPI publication** — distribution stays git-pinned `uvx`/`uv add`; the
  `Private :: Do Not Upload` classifier stays.
- **No publishing of `docs/design/`** — this spec itself stays inside the publication boundary
  (ADR-0012); the public record of the wave is the CHANGELOG entry, ADR-0017, and the tests.

## Invariants touched

- **Consumer-agnosticism / thinness** (ADR-0003): keel gains no engine or per-agent knowledge;
  adapters beyond the `AGENTS.md` snippet are deferred.
- **Publication boundary** (ADR-0012): every path a public doc cites in this wave is a
  committed path.
- **Source-of-truth conflict policy** (`AGENTS.md:17` `docs/doctrine.md`): the mirror must
  never become a second truth — held byte-identical by a deterministic gate (§1).
- **Version-site consistency** (seven sites): the wave edits two sites' files (§4 skill, §6
  bump) and must keep `tests/test_plugin_manifest.py:51` `version sites disagree` green.
- **Agent ↔ prompt contract fidelity** (ADR-0005): §4 does not edit
  `agents/pre-mortem-review.md` or the packaged prompt; the marker/clause guard must stay
  green untouched.
- **CLI surface ↔ reference-table sync**: every registered command appears in
  `docs/cli-reference.md:24` `tests/test_cli.py` — §3 adds the `show` row.

## Enforcement status

| Invariant | Status | Gate/mechanism |
|---|---|---|
| consumer-agnosticism / thinness (ADR-0003) | review-only | review checklist (starter kit, applied as-is) |
| publication boundary (ADR-0012) | review-only | review checklist |
| doctrine-mirror freshness (ADR-0017) | planned | `tests/test_method_corpus_sync.py` (§1) |
| version-site consistency | enforced | `tests/test_plugin_manifest.py::test_version_is_consistent_across_all_sites` |
| agent ↔ prompt contract fidelity (ADR-0005) | enforced | `tests/test_premortem_agent.py` marker + clause guards |
| CLI surface ↔ reference-table sync | enforced | `tests/test_cli.py` (registered commands ↔ `docs/cli-reference.md`) |

## Concept → module map

| Concept introduced/changed | Module / file it lives in |
|---|---|
| packaged doctrine mirror | `src/keel/method/doctrine.md` (to be created) |
| doctrine-mirror freshness gate | `tests/test_method_corpus_sync.py` (to be created) |
| agent-neutral playbook | `src/keel/method/playbook.md` (to be created) |
| asset registry + reader | `src/keel/assets.py` (to be created) |
| `keel show` command | `src/keel/cli.py` |
| `keel show` CLI tests | `tests/test_cli.py` |
| thinned skill router | `skills/apply-method/SKILL.md` |
| de-Clauded slash commands | `commands/keel-apply.md`, `commands/keel-triage.md`, `commands/keel-premortem.md`, `commands/keel-check-ready.md` |
| consumer AGENTS.md routing snippet | `src/keel/templates/method-agents-snippet.md` (to be created) |
| agnostic install/usage docs | `docs/installation.md`, `README.md` |
| release notes + version bump | `CHANGELOG.md` |

## Numbered sections

### §1 Package the doctrine as a gated mirror

Create `src/keel/method/doctrine.md` (to be created) as a **byte-identical copy** of
`docs/doctrine.md` — `docs/doctrine.md` stays the source of truth per the conflict policy
(`AGENTS.md:17` `docs/doctrine.md`); the package ships a mirror so a CLI-only install carries
the method's thesis and phases. The directory `src/keel/method/` is package data under the
existing src layout (the same mechanism that already ships `src/keel/templates/`).

Add `tests/test_method_corpus_sync.py` (to be created), modeled on the existing drift-guard
precedent, asserting: (a) the mirror and `docs/doctrine.md` are byte-equal (read both,
compare full text — not markers), (b) the mirror is readable through
`importlib.resources.files('keel')`, the installed-package view, and (c) the **built wheel**
actually ships it: the test builds a wheel (`uv build --wheel` via subprocess, into a temp
dir) and asserts `keel/method/doctrine.md` appears in the wheel's namelist — every other gate
runs against the editable install, which resolves to the source tree and would stay green even
if a packaging change dropped `method/` from the wheel (round-1 pre-mortem FM-3). The test
docstring records the regeneration rule: **a PR that edits `docs/doctrine.md` re-copies the
mirror in the same PR** — the doctrine's own per-change freshness rule for committed mirrors,
so the gate is never deferrable to a later PR.

**Model-on:** `tests/test_premortem_agent.py`

**Acceptance criterion:** `uv run pytest tests/test_method_corpus_sync.py` passes; editing one
byte of either copy makes it fail; the wheel-namelist item fails when `keel/method/doctrine.md`
is absent from a freshly built wheel; `uv run python -c "from importlib.resources import files;
print(len((files('keel') / 'method' / 'doctrine.md').read_text(encoding='utf-8')))"` prints a
non-zero length.

### §2 Write the agent-neutral playbook

Create `src/keel/method/playbook.md` (to be created): the apply-method procedure written for
*any* agent — the entry rule (read the consumer's `method-bindings.md` first; if absent but
prior method artifacts exist, the established format IS the binding: bind the slots from what
you find and write the missing bindings file), setup (`keel init` into the target, then fill
every slot of the copied bindings sheet), the 8 phases with their gates, the subset-of-phases
rule, the when-not-to threshold, and the portable pre-mortem procedure (run the prompt from
`keel show pre-mortem` in a fresh context that did not author the spec; save the returned
output as the B2 artifact; fold and record per the certification block).

The playbook resolves every keel-owned asset through the CLI (`keel show doctrine`,
`keel init`, `keel check-ready`) and every consumer-owned artifact by project-relative path.
It contains **no** `${CLAUDE_PLUGIN_ROOT}` occurrence and **no** Claude-specific construct —
pinned by a test item added to `tests/test_method_corpus_sync.py`, plus the routing clause
relocation guard from §4.

**Acceptance criterion:** the playbook file exists as package data; a pytest item asserts the
string `${CLAUDE_PLUGIN_ROOT}` does not occur in it and the clause "established format IS the
binding" does occur in it.

### §3 Add the `keel show` command and asset registry

Create `src/keel/assets.py` (to be created): an `ASSETS` mapping from public asset names to
packaged files — `doctrine` → `method/doctrine.md`, `playbook` → `method/playbook.md`,
`pre-mortem` → `templates/pre-mortem-prompt.md` — and a `read_asset` function returning the
file text; an unknown name raises `KeyError` for the CLI layer to translate.

Wire `show` in `src/keel/cli.py` next to the existing commands (`src/keel/cli.py:138`
`@app.command('init')` is the wiring pattern): `keel show` with an asset argument writes the
asset text to stdout **without appending a trailing newline** (`typer.echo(..., nl=False)` or
`sys.stdout.write` — a default `typer.echo` adds one and breaks the byte-equal criterion;
round-1 pre-mortem FM-4) and exits 0; `keel show --list` prints one asset name per line and
exits 0; an unknown asset exits 2 with a `format_error` message naming the valid set (printing
from the CLI layer only, per the no-print-from-engine convention). Add the `show` row to the
command table in `docs/cli-reference.md`, which the CLI↔reference sync test holds to the
registered command set, and extend `tests/test_cli.py` with the three behaviors.

**Reuse:** `src/keel/templates.py::templates_root`

**Acceptance criterion:** `uv run keel show doctrine | cmp - src/keel/method/doctrine.md`
exits 0 (byte-equal, no added newline); `uv run keel show --list` names exactly the three
assets; `uv run keel show nonesuch` exits 2 and names the valid set; the CLI↔reference sync
test passes with the new row.

### §4 Thin the Claude skill and commands onto the packaged corpus

Rewrite the body of `skills/apply-method/SKILL.md` as a thin router: keep the YAML frontmatter
(discovery metadata) and the version line (a pinned version site), replace the inlined
procedure with the instruction to run `uvx --from ${CLAUDE_PLUGIN_ROOT} keel show playbook`
(bare `keel show playbook` when a persistent keel is on PATH) and follow the returned playbook,
keeping only the when-not-to threshold summary inline (the routing decision must be readable
without a tool call), that summary citing the doctrine section by plain name ("doctrine §6 via
`keel show doctrine`"), never by a plugin-root path (round-1 pre-mortem FM-1 sibling sweep).
Update `commands/keel-apply.md` and `commands/keel-triage.md` the same way: content references
of the form `${CLAUDE_PLUGIN_ROOT}/docs/…` or `${CLAUDE_PLUGIN_ROOT}/src/keel/templates/…`
become `keel show` / kit-copy references; **`commands/keel-check-ready.md` is also in the edit
set** — its cross-reference at `commands/keel-check-ready.md:12`
`${CLAUDE_PLUGIN_ROOT}/docs/installation.md` becomes the plain committed path
`docs/installation.md` (round-1 pre-mortem FM-1: the file sits inside the new guard's scan
surface, so leaving it unedited fails PR04's own gate); `commands/keel-premortem.md` gains one
line naming `keel show pre-mortem` as the portable prompt source. `${CLAUDE_PLUGIN_ROOT}`
survives **only** as the `uvx --from` bundle locator (the pattern already live at
`commands/keel-check-ready.md:9` `uvx --from ${CLAUDE_PLUGIN_ROOT} keel check-ready $ARGUMENTS`).

Retarget the routing-clause guard (`tests/test_plugin_manifest.py:112`
`established format IS the binding`) at the playbook (its clause moves there in §2), asserting
the skill routes to `keel show playbook` instead. Add a pytest item asserting no
`${CLAUDE_PLUGIN_ROOT}/` **path-form** occurrence (the variable followed by a slash) remains
in `skills/` or `commands/`. `agents/pre-mortem-review.md` is not edited.

**Acceptance criterion:** the new path-form guard passes; the version-consistency test still
finds the skill's version line; the retargeted routing guard passes against the playbook;
`agents/pre-mortem-review.md` and `src/keel/templates/pre-mortem-prompt.md` are untouched
(the marker/clause guards pass unmodified).

### §5 Ship the consumer AGENTS.md routing snippet in the kit

Create `src/keel/templates/method-agents-snippet.md` (to be created): a short, paste-ready
block for a consumer project's `AGENTS.md` that routes **any** agent into the method — read
`method-bindings.md` first and match its formats; read the doctrine via `keel show doctrine`
(or the pinned `uvx` form); scaffold specs with `keel new-spec`; gate readiness with
`keel check-ready` on the spec; run the pre-mortem per `keel show pre-mortem` in a fresh
non-author context; run the project's own gate commands from the bindings sheet. The kit
copier picks it up with no code change (`src/keel/templates.py:22`
`templates_root().glob('*.md')`). Add its row to `docs/templates-reference.md` and a
`REQUIRED_SECTIONS` entry in `tests/test_templates_valid.py` pinning its load-bearing markers
(`method-bindings.md`, `keel show doctrine`, `keel check-ready`).

**Acceptance criterion:** `keel init` into a fresh temp dir copies the snippet along with the
kit; the new `REQUIRED_SECTIONS` entry passes; `docs/templates-reference.md` gains the row.

### §6 Agnostic install/usage docs, release notes, and the 0.14.0 bump

Add an "Any agent" install path to `docs/installation.md` (the pinned `uvx` one-liner, `keel
show` as the corpus entry, the snippet paste step, and the honest scope line: any agent that
can run a shell; shell-less agents wait on the MCP deferral, ADR-0017) and a short "Any
agent" paragraph to `README.md`. The any-agent one-liner pins the tag `v0.14.0` — the first
release that ships `keel show` — never a copy of the older example pin at
`docs/installation.md:19` `@v0.11.1`, under which `keel show` does not exist (round-1
pre-mortem FM-2). The existing plugin path stays valid as documented at
`docs/installation.md:36` `uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`. Write the 0.14.0
CHANGELOG entry (release-notes-in-wave) covering the whole wave, citing ADR-0017, and bump
the version at all seven pinned sites in the same PR, keeping `tests/test_plugin_manifest.py:51`
`version sites disagree` green.

**Acceptance criterion:** the full gate set passes at version 0.14.0 (`uv run pytest` green,
newest CHANGELOG heading is 0.14.0); `docs/installation.md` and `README.md` each contain an
"Any agent" entry naming `keel show`; ADR-0017 is cited from the CHANGELOG entry.

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |
| PR02 | §2 | yes |
| PR03 | §3 | yes |
| PR04 | §4 | yes |
| PR05 | §5 | yes |
| PR06 | §6 | yes |

## Definition of Done (this spec)

- Generated / mirrored / snapshot artifacts downstream of touched surfaces, each with its
  freshness gate: `src/keel/method/doctrine.md` (mirror of `docs/doctrine.md`; freshness gate
  `tests/test_method_corpus_sync.py`, created in §1 — this wave edits the doctrine in no
  section, so no re-copy is triggered inside the wave itself); `docs/cli-reference.md` command
  table (gate: the CLI↔reference sync test, fed by §3 in the same PR that registers the
  command). No other mirrors, goldens, or lockfile-class artifacts are downstream of this
  wave's touched surfaces.
- All four quality gates plus `keel check-ready` on this spec pass at the wave's head.
- The wave runs in keel-on-keel manual-checklist mode: one commit per section, full gate set
  after each, in manifest order (PR01 → PR06); §6 is last because the version bump pins the
  wave's public surface.

## Pre-mortem certification

- **Reviewer:** pre-mortem-review@0.13.1 (fresh subagent, round 2 — non-author; round 1 by a
  distinct fresh subagent, saved as `docs/design/2026-07-16-agent-agnostic-surface-spec.premortem-r1.md`)
- **Verdict:** CERTIFIED
- **Operator:** none required (verdict is CERTIFIED, not CONDITIONAL-CERTIFY)
- **Certification artifact:** docs/design/2026-07-16-agent-agnostic-surface-spec.premortem.md
- **Date:** 2026-07-16
- **Reviewed against:** the keel working tree at the branch head (no external dependency
  SHAs reasoned against; the wheel-packaging claim was verified by building the wheel in-tree)
- **Post-fold coherence:** re-read performed after folding FM-1..FM-4 — each finding applied
  consistently across its section and the concept→module map (the §4 edit-set growth is
  mirrored in the map's slash-commands row); no dependent count changed ("three assets"
  re-derived and still exact); each claim the fold newly introduced was re-grounded against
  the tree (the line-12 path-form, the three `@v0.11.1` pins, typer's `nl=True` default)
  before round 2, and round 2 independently re-verified all of them.
- **Failure modes considered & folded in:** FM-1 (MAJOR — §4's path-form purity guard would
  fail PR04's own gate on the unedited `commands/keel-check-ready.md`; file added to the edit
  set, sibling SKILL summary de-pathed); FM-2 (MINOR — any-agent one-liner must pin v0.14.0,
  not the older example pin); FM-3 (MINOR — wheel-namelist assertion added so the portability
  claim is gated on the built wheel, not the editable install); FM-4 (MINOR — `keel show`
  writes with no trailing newline so the byte-equal acceptance is reachable). Round 2
  re-gate: all four RESOLVED, zero new findings.

### Fold ledger

| Finding | Target section | artifact:line | Confirmed |
|---|---|---|---|
| FM-1 guard scope: `commands/keel-check-ready.md` enters §4's edit set; line-12 path-form becomes a plain committed path | §4 | `docs/design/2026-07-16-agent-agnostic-surface-spec.md:191` `commands/keel-check-ready.md` | yes (round-2 audit: RESOLVED) |
| FM-1 sibling sweep: the thinned SKILL when-not-to summary cites the doctrine by plain name, never a plugin-root path | §4 | `docs/design/2026-07-16-agent-agnostic-surface-spec.md:188` `keel show doctrine` | yes (round-2 audit: RESOLVED) |
| FM-2 the any-agent one-liner pins the first tag that ships `keel show` | §6 | `docs/design/2026-07-16-agent-agnostic-surface-spec.md:232` `v0.14.0` | yes (round-2 audit: RESOLVED) |
| FM-3 wheel-namelist assertion added to the freshness test | §1 | `docs/design/2026-07-16-agent-agnostic-surface-spec.md:119` `uv build --wheel` | yes (round-2 audit: RESOLVED) |
| FM-4 `keel show` writes the asset with no added trailing newline | §3 | `docs/design/2026-07-16-agent-agnostic-surface-spec.md:165` `nl=False` | yes (round-2 audit: RESOLVED) |

---
