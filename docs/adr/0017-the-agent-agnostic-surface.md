# ADR-0017: the agent-agnostic surface — the CLI is the portable entry; agent artifacts are shims

- **Status:** Accepted
- **Date:** 2026-07-16
- **Relates to:** ADR-0001 (plugin+engine repo), ADR-0003 (thinness & consumer-agnosticism),
  ADR-0012 (publication boundary)

## Context

keel ships the method two ways (ADR-0001): a Claude Code plugin and a `keel` CLI. An audit of
the delivery surface (2026-07-16) found the method's *content* — the doctrine, the apply-method
playbook, the pre-mortem prompt — reachable only through the Claude Code plugin or a full repo
checkout:

- The skill, the slash commands, and the agent resolve every asset through
  `${CLAUDE_PLUGIN_ROOT}`, an environment variable only Claude Code sets.
- A `uvx` / `uv add` install carries the template kit (package data under
  `src/keel/templates/`) but **not** `docs/doctrine.md` — the CLI-only install, the natural
  agnostic path, delivers the gates without the method's source of truth.
- Discovery is plugin-only: nothing a non-Claude agent reads (its `AGENTS.md`, its repo files)
  routes it into the method.
- `hooks/hooks.json` is an empty placeholder — nothing behavioral to port.

ADR-0003 deliberately deferred "full slot-ification" until keel met its real portability test —
a second consumer outside the original toolchain. The maintainer now wants keel usable from
**any** AI agent; that test has arrived.

## Decision

The **CLI becomes the single portable entry point**; agent-specific artifacts become **thin
shims** over content packaged with the engine.

1. **The method corpus ships as package data.** A byte-identical mirror of `docs/doctrine.md`
   lives at `src/keel/method/doctrine.md` (with a deterministic freshness gate holding the two
   equal), joined by an agent-neutral `playbook.md` (the apply-method procedure with no
   Claude-specific constructs). The pre-mortem prompt is already packaged
   (`src/keel/templates/pre-mortem-prompt.md`) and drift-guarded against the bundled agent.
2. **`keel show <asset>` exposes the corpus.** `keel show doctrine | playbook | pre-mortem`
   prints packaged content; any agent that can run a shell gets the full method from one
   entry: `uvx --from git+https://github.com/grimaldost/keel@<tag> keel show <asset>`.
3. **Claude artifacts thin down to routers.** The `apply-method` skill keeps its discovery
   frontmatter and delegates the procedure to `keel show playbook`; the slash commands swap
   `${CLAUDE_PLUGIN_ROOT}/<file>` content reads for `keel show` invocations.
   `${CLAUDE_PLUGIN_ROOT}` survives only as the plugin's *bundle locator*
   (`uvx --from ${CLAUDE_PLUGIN_ROOT} keel …`), which is inherent to plugin distribution.
   The bundled `pre-mortem-review` agent stays standalone-full: it *is* the dispatched prompt,
   so it must be self-contained, and its existing marker/clause drift guard
   (`tests/test_premortem_agent.py`) already holds it to the packaged prompt.
4. **The generic adapter is an `AGENTS.md` snippet, not N per-agent formats.** The kit gains
   `method-agents-snippet.md`, a block a consumer pastes into its `AGENTS.md` (the cross-agent
   instruction convention) that routes any agent to the bindings sheet, the doctrine, and the
   gates.
5. **Enforcement stays at the git/CI layer for consumers.** The deterministic gates run as
   ordinary commands (pre-commit, CI, or in-session) — agent-independent by construction; keel
   ships no agent-runtime hook.

**Deferred, named (ADR-0003's rule — no cited motivating failure yet):**

- **An MCP server wrapping the gates.** A shell-less agent cannot run the consumer's own
  quality gates (`ruff`/`pytest`/…) either, so MCP alone would not make the method *run* there;
  wrap the gates when a real shell-less consumer demands it.
- **Per-agent adapter generators** (Gemini CLI extensions, Cursor rules, Copilot instruction
  files). The `AGENTS.md` snippet covers the common path; add a format when a real consumer on
  that agent reports the snippet insufficient.
- **The hooks slot** stays an empty placeholder, as decided in the 0.12.0 round (T2g).

## Alternatives considered

- **Ship per-agent adapters now** — rejected: speculative generality; N ecosystems to track
  against ADR-0003's thinness invariant, with zero consumers requesting them.
- **Ship the MCP server now** — rejected for the reason named above: it broadens *invocation*
  but not *usability*, since the method's enforcement layer needs a shell anyway. Left as the
  first candidate to un-defer.
- **Duplicate the full skill text and drift-guard it** (the premortem-pair pattern) — rejected:
  the pair pattern exists because a dispatched agent prompt must be standalone; a *skill*
  routes, so a single packaged source with a thin router removes the drift class instead of
  guarding it.
- **Move `docs/doctrine.md` into the package and leave a pointer** — rejected: the doctrine is
  the named source of truth (`AGENTS.md` conflict policy) with many inbound references; a
  committed byte-identical mirror with a deterministic freshness gate is cheap and keeps every
  existing reference valid.

## Consequences

- **New invariant:** the packaged doctrine mirror is byte-identical to `docs/doctrine.md`,
  held by a freshness test; a PR editing the doctrine re-copies the mirror in the same PR
  (the per-change freshness rule the doctrine itself prescribes for committed mirrors).
- The CLI surface grows by one read-only command (`show`), pinned in `docs/cli-reference.md`
  by the existing CLI↔reference sync test.
- The portability claim becomes concrete and honest: *any agent that can run a shell* can
  apply the method from a git-pinned `uvx` invocation; agents without a shell are named out of
  scope until the MCP deferral is revisited.
- The Claude plugin remains fully supported — thinner, with less content to drift.
- Easier: one source of truth per asset; onboarding a new agent costs a paste of the snippet.
  Harder: skill/command edits now happen in the packaged playbook (one indirection), and
  doctrine edits carry a mirror re-copy.
