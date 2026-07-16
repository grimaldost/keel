# Pre-mortem pass — round 1 (saved artifact, B2)

- Spec: docs/design/2026-07-16-agent-agnostic-surface-spec.md
- Date: 2026-07-16
- Reviewer: pre-mortem-review@0.13.1 (fresh subagent, round 1 — non-author)
- Spec-hash: 1899f2e1433c1f209e2ce8450ba0a8e319b78b16087c0c0565cb9ca42db9327b

---

I have completed grounding. Here is my certification artifact.

---

## Pre-mortem review — the agent-agnostic surface (any-agent keel)

Reviewed against: `docs/design/2026-07-16-agent-agnostic-surface-spec.md` @ working tree; ADR-0017; and the cited source at each anchor. I did not author this spec. I read every referenced file, verified every `path:line` anchor and its snippet, empirically built the wheel to test the packaging claim, and simulated the per-PR gate interactions across PR01→PR06.

```yaml
findings:
  - id: FM-1
    severity: MAJOR
    evidence: commands/keel-check-ready.md:12
    summary: >
      §4 adds a repo-wide guard "no ${CLAUDE_PLUGIN_ROOT}/ path-form remains in skills/ or
      commands/", but its own edit list omits commands/keel-check-ready.md, which carries a
      path-form (`${CLAUDE_PLUGIN_ROOT}/docs/installation.md`) at line 12. The new pytest item
      fails inside PR04's own gate; every prior pass certified the spec green while the series
      stalls at execution.
    smallest_fix: >
      In §4, add commands/keel-check-ready.md to the edited files and convert its line-12
      cross-reference `${CLAUDE_PLUGIN_ROOT}/docs/installation.md` to plain `docs/installation.md`
      (leave line 9's `uvx --from ${CLAUDE_PLUGIN_ROOT}` locator, which is var+space, not
      path-form); and sweep the sibling: ensure §4's own thinned SKILL.md when-not-to summary at
      current line 27 drops its `${CLAUDE_PLUGIN_ROOT}/docs/doctrine.md §6` path-form too.
    disconfirming_test: >
      `grep -rn '\${CLAUDE_PLUGIN_ROOT}/' skills/ commands/` after the §4 edits — the guard passes
      iff this returns nothing; today it returns keel-check-ready.md:12 (plus the SKILL body §4
      rewrites).
    consumed_input: >
      The guard scans the raw bytes of every file under commands/; commands/keel-check-ready.md
      is in that scan surface and is NOT in §4's edit set (verified by reading §4's file list and
      grepping the tree).
    target_section: "section 4"

  - id: FM-2
    severity: MINOR
    evidence: docs/installation.md:19
    summary: >
      §6's new "Any agent" install one-liner is "the pinned uvx one-liner"; the existing
      install.md examples pin @v0.11.1. If the implementer copies that pin, the agnostic entry
      point resolves to a release WITHOUT `keel show`, so `keel show doctrine` errors on a fresh
      any-agent install even though every in-tree gate is green.
    smallest_fix: >
      §6 must specify the any-agent one-liner pins the 0.14.0 tag (the release that first ships
      `keel show`), not the repo's existing v0.11.1 example pin.
    disconfirming_test: >
      Read the tag in the "Any agent" block §6 adds; it must be >= v0.14.0.
    target_section: "section 6"

  - id: FM-3
    severity: MINOR
    evidence: tests/test_method_corpus_sync.py (to be created; §1 acceptance)
    summary: >
      The headline portability path is `uvx --from git+… keel show` reading method/*.md from a
      BUILT WHEEL, but every gate the spec names runs against the editable install
      (.venv keel.pth → /home/user/keel/src), so `files('keel')/'method'/…` resolves to the
      source tree and passes regardless of what the wheel contains. No gate builds a wheel; a
      future packaging change (a non-.md file in method/, a build-backend exclude) would break the
      real target while all gates stay green.
    smallest_fix: >
      §1 or §6 DoD: add one assertion that builds the wheel and asserts
      `keel/method/doctrine.md` is in its namelist (or state in DoD that the wheel path is
      accepted as unverified by the gate set, per the maintainer's risk call).
    disconfirming_test: >
      `uv build --wheel` then unzip -l the wheel — method/doctrine.md present? (I ran this for the
      current tree against templates/: they ship; method/ ships by the identical default rule.)
    target_section: "section 1"

  - id: FM-4
    severity: MINOR
    evidence: docs/design/2026-07-16-agent-agnostic-surface-spec.md:168
    summary: >
      §3's acceptance "`uv run keel show doctrine` output is byte-equal to
      src/keel/method/doctrine.md" is fragile to typer.echo/print appending a trailing newline; a
      naive `typer.echo(read_asset(name))` yields text+'\n', which is NOT byte-equal to a file
      that already ends in a newline.
    smallest_fix: >
      §3: state that `keel show <asset>` writes the asset text with no added trailing newline
      (e.g. sys.stdout.write, or echo(..., nl=False)), so the byte-equal acceptance is reachable.
    disconfirming_test: >
      `uv run keel show doctrine | cmp - src/keel/method/doctrine.md` exits 0.
    target_section: "section 3"

cleared:
  - claim: "src/keel/method/*.md ships in the wheel by the same mechanism as templates/*.md"
    cite: "built keel-0.13.1-py3-none-any.whl — keel/templates/*.md ARE in the namelist; method/ is a sibling .md-only dir under src/keel/, packaged by uv_build's default whole-module inclusion. OBSERVED, not inferred."
  - claim: "every path:line anchor in the spec resolves with a matching snippet (A6)"
    cite: "verified each: pyproject.toml:23, AGENTS.md:17, skills/apply-method/SKILL.md:15, tests/test_premortem_agent.py:25, hooks/hooks.json:2, tests/test_plugin_manifest.py:51 & :112, docs/cli-reference.md:23, src/keel/cli.py:136, src/keel/templates.py:22, commands/keel-check-ready.md:9, docs/installation.md:36 — all snippets are whitespace-normalized substrings of their lines (check_ready.py:705-715)."
  - claim: "version-site consistency is seven sites; §6 bumps all seven"
    cite: "tests/test_plugin_manifest.py:42-51 enumerates exactly 7 sites (plugin.json, pyproject, __init__, CHANGELOG newest, agent identity line, spec-template kit stamp, SKILL version line); §4 keeps SKILL's `ships with keel X.Y.Z` line, §6 bumps all — consistent per-PR."
  - claim: "the §4 retarget of the routing-clause guard is accounted for"
    cite: "tests/test_plugin_manifest.py:108-112 asserts 'established format IS the binding' in SKILL; §4 rewrites that assertion in the same PR (PR04) that thins SKILL, and §2 pins the clause in the playbook — no orphaned gate."
  - claim: "CLI↔reference sync only requires adding a `keel show` row"
    cite: "tests/test_cli.py:77-84 checks `f'keel {n}' in reference` for each registered command name (one direction); test_help_lists_all_commands (line 70-74) uses a fixed subset not including show, so adding show breaks neither."
  - claim: "PR dependency order is sound (show depends on doctrine+playbook existing)"
    cite: "PR01 creates method/doctrine.md, PR02 creates method/playbook.md, PR03 wires read_asset over both + templates/pre-mortem-prompt.md (already present) — all three assets exist by PR03."
  - claim: "the spec passes its own Part A DoR (A5 to-be-created + A6)"
    cite: "every concept→module path without '(to be created)' exists (cli.py, test_cli.py, SKILL.md, the three commands, installation.md, README.md, CHANGELOG.md); each '(to be created)' path is claimed by its § (check_ready.py:637); B1 pre-mortem cert is what this artifact supplies."
```

### Prose

The series is fundamentally coherent: ADR-0017 and the spec agree on shape, the packaging mechanism the whole thing rests on is real (I built the wheel — `keel/templates/*.md` ship, so the sibling `keel/method/*.md` ships identically), the anchors all resolve, and the PR ordering respects the dependency chain (doctrine → playbook → `keel show` → skill-thinning → snippet → bump).

The one execution-blocking defect is **FM-1**: §4 introduces a repo-wide purity guard over `commands/` but the spec's §4 edit list forgets `commands/keel-check-ready.md`, which still carries a `${CLAUDE_PLUGIN_ROOT}/docs/installation.md` path-form at line 12. The spec author explicitly reasoned that `${CLAUDE_PLUGIN_ROOT}` survives "only as the `uvx --from` bundle locator" and cited that file's line 9 — but did not read line 12 of the same file, which uses the variable in path-form for a doc cross-reference. This is the classic per-PR-gate-trips-its-own-PR failure the SERIES pass hunts: PR04's acceptance criterion ("the new path-form guard passes") is false against the real tree, so the wave halts at PR04 on a spec certified clean. The fix is a two-line scope edit (add the file to §4 and de-plugin-root its line-12 reference).

The remaining three are MINOR: a stale version pin the agnostic one-liner must avoid (FM-2), the absence of any wheel-build gate behind the headline portability claim (FM-3 — real today by empirical build, but green gates would mask a future regression), and a trailing-newline hazard in the byte-equal acceptance for `keel show` (FM-4). None of these three corrupts the decision the spec gates; FM-1 does, because it deterministically breaks a named PR's gate.

Recommended verdict: fold FM-1 (the blocker) plus the three MINOR fixes, then this is ready. Because a MAJOR remains, this is not a bare CONDITIONAL-CERTIFY.

Unverified-offline: 1
PREMORTEM-VERDICT: NEEDS-REVISION pre-mortem-review@0.13.1 (fresh subagent, round 1)
