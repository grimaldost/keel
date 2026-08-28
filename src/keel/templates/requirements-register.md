# Requirements register — <programme name>

The owner's orders, transcribed. This file exists because an order was the one load-bearing
input to the method with no durable artifact: it lived in a chat message, survived a context
compaction as a paraphrase, and the mechanism it named was then replaced by a different one —
which read as an ordinary design decision, because nothing a blind reviewer could open said
otherwise. Four good pre-mortems audited the spec against the code and the data contracts and
none could audit it against the ask.

Keep this file in the programme's own repo (`docs/requirements/` is the usual home), name it
in each spec's header (`- **Requirements:** docs/requirements/<file>.md`), and account for
every entry in that spec's `## Requirements ledger`. `keel check-ready` reads this file and
fails a spec that leaves an entry unaccounted (A13).

## What belongs here

An order that constrains **mechanism**, not just outcome — "read the sources through the
config layer", "the landing zone stays out of the library", "no new dependencies". An outcome
the spec is free to reach any way it likes is a goal, and goals live in the spec.

Write it **verbatim**, in the owner's own words, in the owner's own language. A paraphrase is
where an order dies: once the wording is gone, a substitution reads as a choice and there is
nothing left to diff a spec against. Quote it; add your reading underneath if the wording is
ambiguous, marked as your reading.

## Entries

Each entry opens with a line-initial `RR-<n>` id — a heading, a list item or a table cell, so
the ids a reader sees as entries are the ids the gate reads. Ids are stable and never reused:
a withdrawn order is marked withdrawn, not deleted, because specs already cite it.

### RR-01 — <a few words naming the order>

- **Given:** <date, and where it was said — the session, the message, the review>
- **Order (verbatim):** "<the owner's exact words>"
- **Reading:** <only if the wording needs one; say that it is your reading, not theirs>
- **Status:** live | withdrawn <date + who withdrew it>

### RR-02 — <the next one>

- **Given:**
- **Order (verbatim):** "<…>"
- **Status:** live

## How a spec accounts for an entry

One ledger row per entry, in the spec, with exactly one of four dispositions:

| Disposition | Means | The obligation it carries |
|---|---|---|
| `§N` | this spec's section N satisfies the order | §N must exist in the spec |
| `DEFERRED — <trigger>` | not this spec; here is what reopens it | the trigger is named, so the deferral can expire |
| `OUT-OF-SCOPE` | the order does not bear on this spec | none — but it is a decision, written down |
| `DEVIATED — ratified by <operator>: <what they said>` | the spec does something the order rules out | the owner said so, and the spec records who and what |

**DEVIATED is the state a session cannot grant itself.** The other three are the author's call.
This one is not: a deviation from the owner's own order needs the owner's answer, and the gate
fails a DEVIATED row that names no ratification. If asking is not possible right now, the
honest disposition is not a self-ratified deviation — it is a spec that does not yet pass the
gate, which is the state that gets the question asked.
