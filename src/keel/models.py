"""Result types returned by keel gates."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Violation:
    """A single gate finding."""

    where: str
    message: str


@dataclass(frozen=True, slots=True)
class GateResult:
    """The outcome of running a gate."""

    passed: bool
    violations: tuple[Violation, ...] = ()
    warnings: tuple[str, ...] = ()
