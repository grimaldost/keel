# Candidate core bodies — measurement assets, not the kit

These are **candidates**, not templates. `keel init` does not copy this directory (the copier
globs the kit directory non-recursively), and nothing here is part of what a consumer receives.
They exist so an ablation can measure one thing: **is the kit's prose necessary to produce a spec
that keel's own gate accepts?**

Each file is the sibling one directory up with material **removed and nothing rewritten** —
`tests/test_core_variants.py` asserts that every line here appears, in order, in the original. The
diff is therefore exactly the ablation's independent variable, and cannot quietly become a
rewrite that measures wording instead of presence.

## What each core drops, and what a null on it would license

| file | dropped | the checks that go unnamed |
|---|---|---|
| `spec-template.md` | the A10 enforcement-claim note, the A9 reuse-notation note, the A11 anchor-range note | A9, A10, A11 |
| `definition-of-ready.md` | the Part-B items beyond the certification requirement and the operator close (invariants named, concepts mapped, ADRs for non-obvious choices, internal consistency, post-fold coherence, the measurement-profile pointer) | none — these are reviewer items, not gate predicates |

A run in which the core matches the full body licenses cutting that **prose**. It licenses nothing
about the **checks**: a check's value is a question about the check, answered by its positive
control and its hit rate, not by whether an agent still complied without being told. The three
checks the core stops naming keep running and keep rejecting either way.

## What changed under this design before it was measured

The contrast these arms carry is much smaller than it was when the ablation was designed, and the
reason matters for reading any result off them. Most of the reduction the "core" was supposed to
demonstrate turned out to be **information-preserving relocation** — facts that had a better home
in doctrine, in the ADR template, in the Definition of Done, in the kind-selected profile sheet —
and a relocation owes no measurement, so it shipped without one. What is left between full and
core is only the material that genuinely disappears from the author's view.

So the honest framing for whoever runs this: the independent variable is a couple of hundred
words, not a couple of thousand. Read the per-criterion table rather than a headline pass rate,
check the saturation gate before buying the full matrix, and if every arm passes everything,
report the bank as having had no power rather than reporting a null.
