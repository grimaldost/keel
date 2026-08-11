"""Result types returned by keel gates."""

from dataclasses import dataclass

# The closed catalogue of check ids a finding may name (T0.1). A0-A12 and R1 are Part A's
# structural checks, B1/B2 the certification pair, W1-W5 the warnings:
#   W1 kit skew or an unstamped spec · W2 header Status currency · W3 basename expansion
#   W4 B2's adoption nudge (no artifact named) · W5 B2's spec-hash mismatch
# The two W4/W5 letters are new: B2's warnings were unlettered, and an uncountable warning can
# neither be measured nor defended.
CHECK_IDS = frozenset(
    {
        'A0',
        'A1',
        'A2',
        'A3',
        'A4',
        'A5',
        'A6',
        'A7',
        'A8',
        'A9',
        'A10',
        'A11',
        'A12',
        'R1',
        'B1',
        'B2',
        'W1',
        'W2',
        'W3',
        'W4',
        'W5',
    }
)


@dataclass(frozen=True, slots=True)
class Violation:
    """A single gate finding.

    `where` is a coordinate and collides across checks by design (`line N` from A3 and A8,
    `path:line` from A6/A11/A12, `Pre-mortem certification` from four B1 conditions), so `check`
    carries the identity a count needs. It defaults to '' so a consumer constructing a Violation
    outside the gate is not forced to invent an id.
    """

    where: str
    message: str
    check: str = ''


@dataclass(frozen=True, slots=True)
class Warning:
    """A single non-blocking gate finding, with the id of the check that raised it.

    The message keeps its `WARN: ` prose prefix and gains no `W1: ` string prefix — identity is a
    field, so nothing downstream re-parses a message to learn which check spoke.
    """

    check: str
    message: str


@dataclass(frozen=True, slots=True)
class Probe:
    """What one check saw on one run: three states, not two (KEEL-B07).

    A zero-fire count is ambiguous between *inert* and *never had an opportunity* — eight checks
    are verify-when-present and three more are conditionally relaxed — so a two-state count
    records the two indistinguishably and can answer neither "is this check sharp?" nor "is it
    decayed ritual?".

        candidates == 0                  n/a     — no construct of this shape was present
        candidates > 0 and fired == 0    clean   — the check looked and found nothing
        fired > 0                        fired

    `causes` is the report unit: distinct clustered causes behind `fired`, and 0 exactly when
    `fired` is 0. Until cause-grouping lands it equals `fired`, which is why the ledger line
    carries a schema version.
    """

    check: str
    candidates: int
    fired: int
    causes: int


@dataclass(frozen=True, slots=True)
class GateResult:
    """The outcome of running a gate."""

    passed: bool
    violations: tuple[Violation, ...] = ()
    warnings: tuple[Warning, ...] = ()
    probes: tuple[Probe, ...] = ()
