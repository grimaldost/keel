# keel method — AGENTS.md routing note

*Paste the block below the rule into your project's `AGENTS.md` (or your agent's equivalent
instructions file) and delete everything above it, including this header. It routes any coding
agent — whichever tool or vendor — into the method on every session.*

---

## Development method (keel)

This project runs under the keel method: control flow lives in durable artifacts and
deterministic gates, not in-session judgment.

- **Bindings first:** read `method-bindings.md` and match its formats (spec format, ADR home,
  gate commands, review checklist, reflection sink). An unbound slot means the method is not
  fully applied here.
- **Doctrine and procedure:** `<KEEL-CLI> read doctrine` prints the thesis, principles, and the 8
  phases; `<KEEL-CLI> read procedure` prints the full apply-method procedure.
- **Specs:** scaffold with `keel new-spec <path>`; iterate with
  `keel check-ready --structure-only <path>`. A spec is not ready to decompose until
  `keel check-ready <path>` exits 0 — well-formedness plus a recorded blind pre-mortem.
- **Pre-mortem:** run the prompt from `<KEEL-CLI> read pre-mortem` in a fresh context that did NOT
  author the spec; save its returned output as the certification artifact
  (`<spec-stem>.premortem.md`, with `Spec-hash:` from `keel spec-hash <path>`).
- **Gates:** run this project's own gate commands from `method-bindings.md` before review;
  merge only when the Definition of Done is fully checked.

Without a persistent `keel` on PATH, every command above runs pinned as
`<KEEL-CLI> <command>`.
