# CLI reference

Run via `uvx --from <repo> keel <command>` or, installed, `keel <command>` — or
`python -m keel <command>` where an application-control policy blocks the
console-script executable.

| Command | Purpose | Exit codes | Status |
|---|---|---|---|
| `keel check-ready <spec> [--structure-only]` | Definition-of-Ready gate (Part A + pre-mortem cert); `--structure-only` runs Part A only, for the author loop. Both exit paths end with one summary line — `keel <version> — N checks applicable, M fired` — so a verdict names the copy that produced it and a vacuous run does not read as a thorough one. When the local gate ledger records a newer keel than the running copy, one extra line `WARN: keel <newest> has run on this machine; this is keel <running> — upgrade (uv tool upgrade keel) or run the plugin's copy` prints first; it is not a check, has no letter, and never changes the exit code. Before the verdict it also judges the vocabulary block: on the spec's walk (its folder up to the git top level; outside git, up to the first folder holding an instruction file) it finds the nearest folder whose `AGENTS.md` or `CLAUDE.md` carries keel's vocabulary block, resolves the vocabulary there as `keel vocabulary --write` does, and judges every instruction file present in that folder. One whose block digest differs from the resolved one prints `WARN: the vocabulary block in <file> is stale (block <a>, resolved <b>) — run keel vocabulary --write`, and one without a block prints `WARN: the vocabulary block in <file> is missing (resolved <b>) — run keel vocabulary --write`; a current file prints nothing. It stays silent when no block is found, when the project is not bound, and when no project file applies and no user-level file is present (`KEEL_VOCABULARY=off` included), since such a machine cannot judge a block that depends on a user-level file; the last two are decided before any instruction file is read; a project's own noun list is judged on any machine. A fault on this path (a malformed vocabulary file, an unreadable or undecodable instruction file) prints one line instead, `WARN: the vocabulary block could not be judged — <defect>`, naming the file. Like the upgrade line, it has no check letter, is not written to the ledger, and never changes the exit code | 0 pass, 1 fail, 2 not-runnable | **real** |
| `keel decompose-check <spec>` | Decompose exit gate (the 3→4 boundary): the generated series was read by a fresh non-author reviewer before anything ran it. Reads the `### Series review` block inside `## Pre-mortem certification` — D1 the record (reviewer, terminal verdict, saved artifact), D2 the artifact's agreement — which is B1/B2's shape one boundary later, over the artifact the DoR gate structurally cannot see. A spec declaring `Kind: single-change` or `Phases: … (Decompose: skipped)` has no series to review: the gate passes with no applicable check, which reads as `n/a` and not as a clean run | 0 pass, 1 fail, 2 not-runnable | **real** |
| `keel spec-hash <spec>` | Print the canonical certification hash (the spec minus its certification section and its header `Status:` line — an `## Amendment` section is NOT removed, so an amendment still moves the hash; B2 recomputes without it to tell an addition from an edit, W7; when the body did change and an `## Amendment`, or the latest `### Amendment review` subsection of the certification, carries a `- **Edits sections:** §N, …` line, W5 names that declared edit, and says it is recorded, not verified) — what a saved pre-mortem artifact records as `Spec-hash:` (B2) | 0 ok, 2 not-runnable | **real** |
| `keel re-anchor <spec> [--check] [--body] [--by-content <git-ref>]` | Repoint drifted anchors from the snippets that identify them. The fold ledger by default — it sits inside the span `spec-hash` removes, so the repair cannot invalidate the certification it serves; `--body` also rewrites prose anchors and says that the hash moves, and is refused on a spec that carries a recorded certification (CERTIFIED or CONDITIONAL-CERTIFY): drift after certification goes through an `## Amendment`. A weak snippet off its claimed line, a range anchor, or a snippet on no line is reported and left alone. `--by-content <git-ref>` repairs from the tree instead of the snippet: it reads the line each anchor cited AS OF that ref and repoints to where that content sits now, so the snippet-less (and unbackticked) row the template emits is repairable, and a range moves both ends. A line inside a hunk changed or deleted since the ref is reported, never guessed at, and so is a run that cannot read the ref at all: outside a git repository, with a ref that names no commit, or with no runnable git, each row says which | 0 ok, 2 refused or not runnable | **real** |
| `keel new-spec <target> [--force]` | Stamp `spec-template.md` to a new spec path (the author on-ramp) | 0 ok, 2 exists | **real** |
| `keel gate-health [--since] [--repo]` | Read back the local hit-rate ledger: per check, applicable runs / candidates, distinct revisions and repos with an opportunity / distinct revisions it fired on / causes / fire rate (revisions fired on over revisions with an opportunity), split by author-loop vs full-gate runs. Rows keel's own test suite wrote are left out and counted | 0 | **real** |
| `keel show <name> [--list]` | Print a body from the serving kit — `checks` (the Part-A reference block), `directive` (the dispatched pre-mortem prompt), or any template by stem. A projection read at run time, never a copy, so it cannot drift from the shipped file | 0 ok, 2 unknown name | **real** |
| `keel vocabulary [PATH] [--json] [--write] [--check] [--file FILE]…` | Print the work-unit vocabulary that applies to `PATH` (default: the current directory), resolved in three layers — keel's own nouns, a user-level file (`KEEL_VOCABULARY`, else the XDG config folder) whose additions apply only when an instruction file on the directory's walk carries keel's vocabulary block, and a project `.keel/vocabulary.toml` at the git top level that replaces both or declares the project not bound. Prints the resolved path, each layer with its source (keel's version, or the file's path and schema), the scope, each noun with its layer, axis, senses (each with its glossary phrase) and any reading and definition, the allowed terms, the rule, the retired nouns with their replacements, the notes, and the 64-hex digest — or `not bound — <reason>` in place of the nouns and digest. `--json` prints the same as one object with the keys `path`, `in_scope`, `layers`, `nouns`, `allowed`, `rule`, `retired`, `notes`, `not_bound` and `digest`. `--write` resolves with scope assumed and writes the vocabulary block — `<!-- keel:vocabulary begin digest=<first 12 hex> -->`, a line of the noun names, the rule, a line naming `keel vocabulary`, `<!-- keel:vocabulary end -->` — into the root's `AGENTS.md` and, when one exists, its `CLAUDE.md`; the root is `PATH`'s git top level, else `PATH` itself, never the current directory. `AGENTS.md` is created when absent, and the command says so (unlike `keel init`, which never creates one: `--write` is an explicit request to place the block). An existing block is replaced in place, every byte outside it kept and the file's newline style (CRLF or LF) kept; a file without one gets it appended after a blank line. It refuses, changing nothing, a file whose first five lines, the block's own lines left out, say `GENERATED` or `do not hand-edit` (put the block in that file's generator), a file with a malformed block (two begin markers, a begin marker without an end, or a begin marker whose digest is not 12 lowercase hex digits), a file it cannot write (a read-only file, or a new one in a folder it cannot write), and a not-bound project, naming its reason; a write that still fails puts back the files already written and exits 2. `--check` resolves the same way and judges each file's block digest against the resolved one, printing both when they differ, and for a malformed block the repair (leave exactly one begin and one end marker, or remove both); on a not-bound project it prints `not bound — <reason>`, as there is nothing to judge. It judges against the vocabulary as resolved on this machine, so it is no CI gate for a block that depends on a user-level file. `--file FILE`, repeatable, names the files `--write` or `--check` uses instead of `AGENTS.md` and `CLAUDE.md` (a relative one against the current directory); `--write` with `--check`, `--json` with either, and `--file` without either are usage errors | Print and `--json`: 0 resolved, a not-bound project included; 2 a malformed vocabulary file, an unreadable instruction file, or a PATH that is not a directory. `--write`: 0 written or unchanged; 2 refused, changing nothing (a generated file, a malformed block, a file that cannot be written, an unreadable or undecodable instruction file, a `--file` whose folder does not exist, a not-bound project, a malformed vocabulary file, a PATH that is not a directory). `--check`: 0 every file current, a not-bound project included; 1 a file absent, without a block, with a stale one, or with a malformed one (two begin markers, a begin marker without an end, or a digest that is not 12 lowercase hex digits); 2 a malformed vocabulary file, an unreadable or undecodable instruction file, a `--file` whose folder does not exist, or a PATH that is not a directory. Usage errors, each 2: `--write` with `--check`, `--json` with either, `--file` without either | **real** |
| `keel init <target> [--force]` | Copy the full template kit into a project, then point the project's `AGENTS.md` at it. The project root is the git top level of `<target>`, else the current directory (only when `<target>` is inside it). When the root has an `AGENTS.md` that does not already carry it, init appends one line naming the method and the bindings file relative to that root — `This project applies the keel method; its bindings are in docs/method/method-bindings.md.` for `keel init docs/method` — and prints what it did; with no `AGENTS.md` it creates none and says so. The step also runs when the copy refuses because the kit already exists, so a second run leaves `AGENTS.md` as it was | 0 ok, 2 exists | **real** |
| `keel bind-check <bindings>` | Every portability slot in a method-bindings sheet is bound to something concrete. The binding column is resolved by HEADER (`This project` when the table has one, else the last column), and `not bound — <reason>` WARNs rather than fails — a named deferral is a decision, a blank is a gap (ADR-0018) | 0 ok, 1 unbound, 2 no sheet | **real** |
| `keel survey <dir>` | Sweep a design directory: which spec-shaped documents carry no certification? Spec-shaped means a numbered-sections or PR-manifest heading; triage docs, ADR drafts, pre-mortem artifacts and registers are listed and never counted | 0 ok, 1 an uncertified spec, 2 not a directory | **real** |
| `keel budget-drift <series> <actuals>` | Wave cost drift past threshold | 0 / 1 / 2 | stub |
| `keel --version` | Print the installed keel version and exit | 0 | **real** |

`check-ready` exit 2 (not-runnable) covers a missing path, a directory (use `keel survey` for
a directory) and an undecodable (non-UTF-8) spec — distinct from exit 1, which means the spec
has real violations.

An anchor that leaves the repository (`../sibling/path.py:12`) resolves normally when the
sibling is checked out beside this repo. When it is not, it FAILS rather than falling back to
the basename search: expanding it would repoint the citation at an unrelated in-repo file of
the same name and warn that the expansion is unique, which reads as resolved.

## The gate hit-rate ledger

`keel check-ready` appends one JSONL line per run to a **local** ledger, and `keel gate-health`
reads it back. DoR runs only: `decompose-check` writes no line yet, because the record's `mode` is
a closed enum over the DoR gate's two modes and a third one is a schema bump — so D1/D2 have no
hit-rate to read, and `gate-health` lists the DoR catalogue rather than implying otherwise. It records ids, counts, verdict buckets and hashes — never spec text: the writer
only accepts fields that are ints, bools, closed enums, hex digests or slugs, so a free-text field
is unrepresentable, and the spec is identified by a digest because stems name a project's roadmap.
Nothing is uploaded.

Location, in order: `$KEEL_GATE_LEDGER` → `$XDG_STATE_HOME/keel/gate-ledger.jsonl` →
`~/.keel/gate-ledger.jsonl`. **Set `KEEL_GATE_LEDGER=off` to disable it.** It is user-level rather
than per-repo on purpose: the question a hit-rate answers is how a check behaves across every repo
it runs in, and one repo rarely holds enough specs to answer it.

Each check reports three states, not two — `candidates == 0` means no construct of that shape was
present (**n/a**), `candidates > 0` with no fires means the check looked and found nothing
(**clean**), and only the second is evidence. Writing is fail-open: a full disk or a read-only
home changes what is recorded and never the 0/1/2 exit codes.

`gate-health` reads the field and only the field. A row written by keel 0.21.0 or older whose
repo is a pytest `tmp_path` directory (the test's name cut to 30 characters, then a counter, as in
`test_check_ready_passes_on_rea0`) came from keel's own test suite, before 0.21.0's hermetic
conftest kept the suite out of the real ledger; those rows are left out and their count is
printed, except under `--repo`, which reads the repository it names whole. A revision is a spec's
content (the row's `rev`), counted once however often and from however many directories it ran,
and `candidates` counts once per revision; `repos` counts the directory names runs recorded, so two
worktrees of one repository count twice. These are the units `docs/evidence.md`'s pre-registered
dispositions are written in.

**The hash's scope is pinned per gate MINOR**, exactly as W1's kit-skew semantics are. Changing
what `spec_hash` covers invalidates every `Spec-hash:` already recorded in a saved pre-mortem
artifact, which surfaces as a one-time wave of W5 "certified against an earlier revision"
warnings — expected, not a defect, and re-recorded by re-running `keel spec-hash` on the current
spec. 0.14.0 → 0.15.0 is such a change: the header `Status:` line left the hashed span, so
that W2's advice ("update the Status field") stopped invalidating the certification the same run
had just verified.

The one still-stubbed command (`keel budget-drift`) prints an actionable message and exits 2
(ADR-0003); its recorded disposition is removal, sequenced behind a bound orchestrator's live
measurement window (backlog KEEL-B30).

*This table is pinned by `tests/test_cli.py` — every registered command appears here.*
