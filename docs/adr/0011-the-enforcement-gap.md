# ADR-0011: the enforcement gap — the gate must enforce what it documents

- **Status:** Accepted
- **Date:** 2026-07-01
- **Extends:** ADR-0002 (DoR form/correctness split), ADR-0004 (grounded referents), ADR-0005 (the verification spine)

## Context

A six-lens blind skeptic panel (`docs/feedback/2026-07-01-skeptic-panel-fable5.md`, Fable 5 at max
effort; two lenses ran the CLI against adversarial specs in a scratch repo) found the Definition-of-
Ready gate **enforced materially less than it documented**, and **false-failed ordinary prose** — the
two ways a gate loses an adopter's trust.

Confirmed against source and reproduced:

1. **Fence-blindness (a BLOCKER-class hole).** `check_ready` parsed fenced code as live structure. A
   fenced example `## Pre-mortem certification / Verdict: CERTIFIED` shadowed a real recorded
   `Verdict: REJECTED` (the gate printed `OK`, exit 0) — the one non-structural promise, flipped. The
   mirror: a spec that quoted the code it removes (a `# TODO`, a `### heading`) false-failed.
2. **Documented teeth exceeding implemented teeth.** A4's "bijection" never parsed the PR side (one
   PR citing two sections passed; a §N in a comment cell miscounted); R1's "≥1 resolving row" was
   satisfied by a `<3`-cell ledger row; A10 was defeated by a line-wrap, by a backticked invariant
   name (the inline-code strip deleted the key), and by common-word "negation" tokens; A2 counted
   words to end-of-section so an empty criterion followed by prose passed, and the template's own
   `<...>` placeholders were not a checked class (a one-edit `new-spec` stamp passed the whole gate);
   A9 accepted a function-local as a top-level symbol; A11 missed a tail-truncated range; B1 took the
   first `Verdict:` line and ignored an appended `RETRACTED`.
3. **False positives on ordinary prose.** A backticked `host:port`, URL, or `path:line:col` parsed as
   an anchor; the snippet regex spanned newlines so adjacent anchors ate each other; `ADR-0002 §4` and
   `RFC 9110 §15` failed A8; a directory or non-UTF-8 spec crashed with a raw traceback at exit 1
   (indistinguishable from "spec has violations").

These are the DC1/DC2 failure classes ADR-0005 named, now found **in keel's own gate** rather than in
a consumer spec. The gate's design was sound; its implementation under-delivered the design.

## Decision

**The gate enforces what it documents.** The mechanizable half of the panel's findings ships in
`check_ready.py`, each with a regression test (the ADR-0005 gate-health rule):

- **Fence-awareness** (`_mask_fenced`): fenced blocks are masked (line-count preserved) before
  section-splitting and every line scan, so an illustrative example cannot forge the verdict and a
  quoted marker cannot false-fail. This is the load-bearing fix; everything else composes on top.
- **A4** parses the "Implements section" column only — one section per PR row, one PR per section.
- **R1/A12** treat a `<3`-cell ledger row as a violation, not a silent skip.
- **A6** rejects `host:port`/URL/IP false matches (the anchor path token carries no colon), keeps a
  same-line snippet that is not itself anchor-shaped, resolves known extension-less files, and rejects
  backslash/absolute (non-portable) paths; a directory anchor resolves via `is_file()` (no crash).
- **A2** counts only the criterion's paragraph; **A3** flags a leftover `<...>` placeholder outside code.
- **A10** scans across a wrap, keeps a backticked key, and uses real negation cues.
- **A9** requires a column-0 symbol; **A11** also fires on a tail-truncated range; **A8** treats
  standards ids (ADR-/RFC-/PEP-) as cross-document; **B1** rejects a second (appended) Verdict line.
- **Exit codes:** a directory or undecodable spec is not-runnable (exit 2) via `format_error`.

**The drift guard states its guarantee honestly** (ADR-0005's "neither can silently drift again" was
an over-claim): it now checks marker *presence* AND verbatim *clause-identity* for a pinned set, and
its docstring names both limits. A live prompt↔agent divergence the marker check had missed (the
agent's DC1 bullet had dropped "and sibling repos") is fixed.

## Alternatives considered

- **Rewrite the parser structurally (a real markdown AST) instead of masking + regex.** Rejected for
  0.11.0 as too large a blast radius for a release whose job is to close known holes; masking removes
  the whole fenced-content class cheaply, and the regex hardening is local and tested. A structural
  parse is recorded as the standing direction if the false-positive tail continues (ADR-0013).
- **Mechanize the self-certification hole (B1 is author-typable) here.** Deferred to ADR-0013 — it
  needs the pre-mortem to emit a saved artifact the gate can validate, a design change, not a fix.
- **Leave the false-positives (host:port, RFC §) as documented syntax quirks.** Rejected: they fire on
  standard service/spec prose with a misleading message, and the fix is precise and tested.

## Consequences

- The gate now means what its reference block says; 24 regression tests pin the fixes, one per hole.
- **Widen-and-tighten, mixed.** Most fixes are widen-only (fewer false positives) or catch-more
  (fence, bijection, ledger) and do not retro-break a well-formed spec. Two can newly fail a
  previously-green spec: a leftover `<...>` placeholder (A3) and an absolute/backslash anchor (A6) —
  both are real defects the gate should have caught, so this is teeth, not regression.
- **Extends ADR-0002/0004/0005**; it does not supersede them. The form/correctness split holds — every
  fix here is still *form*; correctness stays with the blind pre-mortem.
