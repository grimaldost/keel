# Installation

## Plugin (Claude Code)

```
/plugin marketplace add grimaldost/keel
/plugin install keel
```

Installs the `apply-method` skill, the four `/keel-*` commands, the `pre-mortem-review`
agent, and the template kit. Each entry point, its argument and what it does:
`docs/plugin-reference.md`.

## CLI

Self-contained (no install), runs the bundled engine:

```
uvx --from git+https://github.com/grimaldost/keel keel --help
```

Persistent binary on PATH (so a bare `keel` works, e.g. from a slash command):

```
uv tool install git+https://github.com/grimaldost/keel
```

Or add it as a project dependency straight from the repository:

```
uv add git+https://github.com/grimaldost/keel
```

None of these pins a revision; uv resolves a `git+` URL with no `@<ref>` against the
repository's default branch (uv's documented behaviour), so what you get moves as that
branch moves. To hold gate semantics still across a series, append `@<ref>` — a tag that
exists (`git ls-remote --tags https://github.com/grimaldost/keel`) or a commit SHA.
Tagging currently lags the shipped version, so run that command and check the ref
resolves before pinning to it.

Requires Python >= 3.11 and `uv`. The `/keel-check-ready` slash command runs the
engine straight from the installed plugin bundle
(`uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`), so it works with only the plugin
installed — no separate CLI step needed.

Where an application-control policy blocks console-script executables (`keel.exe`
on a locked-down Windows machine), the module entry point sidesteps the shim:
`python -m keel <command>` (or `uv run python -m keel <command>` in a uv project)
is equivalent to `keel <command>`.
