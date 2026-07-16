# Spec — widget

## Numbered sections

### §1 Add the widget
Introduce `src/widget.py`. Grounding: `README.md:1` `zzz-not-on-that-line`. **Acceptance criterion:** `src/widget.py` exposes a
make() function and a unit test asserts the returned value is a Widget.

## Concept → module map

| Concept | Module / file it lives in |
|---|---|
| widget | `src/widget.py` (to be created) |

## PR ↔ section manifest

| PR | Implements section | One concern? |
|---|---|---|
| PR01 | §1 | yes |

## Pre-mortem certification

- **Reviewer:** review-panel (non-author)
- **Verdict:** CERTIFIED
- **Failure modes considered & folded in:** none
