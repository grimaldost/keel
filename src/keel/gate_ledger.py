"""The gate hit-rate ledger (KEEL-B07): one JSONL line per `check-ready` run, local only.

CONTRIBUTING has claimed for eleven minor versions that a gate firing zero times across N series
is a triage input, while admitting no such ledger exists. Every keep verdict on the Part-A checks
has therefore rested on design reasoning rather than data, and absence of evidence reads as
*probably inert*, not *probably fine*.

Three design commitments, each load-bearing:

**Three states.** A `Probe` records candidates, fires and causes, so `n/a` (no construct of that
shape was present) is distinguishable from `clean` (the check looked and found nothing). Without
that split, the eight verify-when-present checks and the three conditionally-relaxed ones report
zeroes that mean two different things.

**Privacy by construction, not by memory.** `_append` only ever sees a `LedgerLine`, and every one
of its fields is an int, a bool, a closed enum, a hex digest, or a slug — `serialize` rejects
anything else, so a free-text field is unrepresentable and no code path can pass a
`Violation.message` in. The spec is identified by a digest, never by its stem: stems name the
project's roadmap.

**Telemetry never colours the verdict.** Writing is fail-open on OSError and the 0/1/2 exit codes
are a documented contract, so a full disk or a read-only home changes what is recorded and nothing
else.

User-level by default (`$KEEL_GATE_LEDGER` → `$XDG_STATE_HOME/keel/` → `~/.keel/`), because the
question is "how does this check behave across every repo I run it in", and `KEEL_GATE_LEDGER=off`
turns it off. Local only; nothing is uploaded.
"""

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from keel import __version__
from keel.check_ready import (
    _declared_kind,
    _field,
    _find_section,
    _read_spec_text,
    _resolve_base,
    _split_top_sections,
    _verdict_head,
    spec_hash,
)
from keel.models import CHECK_IDS, GateResult

# v2: `causes` became the grouped report unit (anchors against one target, or sharing one drift
# delta, are one cause). `fired` is unchanged, so the two eras remain comparable on it — but a
# `causes` figure must never be read across the boundary without checking `v`.
SCHEMA_VERSION = 2

_SLUG_RE = re.compile(r'^[A-Za-z0-9._-]{1,64}$')
_HEX_RE = re.compile(r'^[0-9a-f]{4,64}$')
_TS_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
_VERSION_RE = re.compile(r'^\d+\.\d+\.\d+$')
_MODES = frozenset({'full', 'structure-only'})
_KINDS = frozenset({'series', 'single-change', 'undeclared'})
# The recorded verdict is bucketed, not quoted: a real verdict line carries trailing prose (a
# discharge note, a reviewer identity), and quoting it would put free text in the record.
_VERDICTS = frozenset({'CERTIFIED', 'CONDITIONAL-CERTIFY', 'OTHER', 'NONE'})


@dataclass(frozen=True, slots=True)
class LedgerLine:
    """One run. Every field is a closed shape; see `serialize` for the rejecting encoder."""

    ts: str
    gate: str
    kit: str
    repo: str
    spec: str
    rev: str
    lines: int
    kind: str
    mode: str
    passed: bool
    exit_code: int
    probes: dict[str, tuple[int, int, int]]
    warns: dict[str, int]
    cert_present: bool
    verdict: str
    operator: bool


def _check_shape(value: str, pattern: re.Pattern[str], field: str) -> str:
    if not isinstance(value, str) or pattern.match(value) is None:
        raise ValueError(f'ledger field {field!r} does not match its closed shape: {value!r}')
    return value


def _check_enum(value: str, allowed: frozenset[str], field: str) -> str:
    if value not in allowed:
        raise ValueError(f'ledger field {field!r} is not one of {sorted(allowed)}: {value!r}')
    return value


def serialize(line: LedgerLine) -> str:
    """Encode one line, rejecting anything a closed shape does not admit.

    This is the privacy mechanism. "Remember not to log content" decays; a serializer that cannot
    represent free text does not.
    """
    for check in (*line.probes, *line.warns):
        if check not in CHECK_IDS:
            raise ValueError(f'ledger names an uncatalogued check: {check!r}')
    payload = {
        'v': SCHEMA_VERSION,
        'ts': _check_shape(line.ts, _TS_RE, 'ts'),
        'gate': _check_shape(line.gate, _VERSION_RE, 'gate'),
        'kit': _check_shape(line.kit, _VERSION_RE, 'kit'),
        'repo': _check_shape(line.repo, _SLUG_RE, 'repo'),
        'spec': _check_shape(line.spec, _HEX_RE, 'spec'),
        'rev': _check_shape(line.rev, _HEX_RE, 'rev'),
        'lines': int(line.lines),
        'kind': _check_enum(line.kind, _KINDS, 'kind'),
        'mode': _check_enum(line.mode, _MODES, 'mode'),
        'passed': bool(line.passed),
        'exit': int(line.exit_code),
        'probes': {check: [int(n) for n in counts] for check, counts in line.probes.items()},
        'warns': {check: int(count) for check, count in line.warns.items()},
        'cert': {
            'present': bool(line.cert_present),
            'verdict': _check_enum(line.verdict, _VERDICTS, 'verdict'),
            'operator': bool(line.operator),
        },
    }
    return json.dumps(payload, separators=(',', ':'), sort_keys=False)


def line_for_run(spec_path: Path, result: GateResult, *, structure_only: bool) -> LedgerLine:
    """Build the record for one run. Counts, ids and verdict buckets only — never spec text."""
    base = _resolve_base(spec_path)
    resolved = spec_path.resolve()
    try:
        relative = resolved.relative_to(base).as_posix()
    except ValueError:  # a spec outside its own resolved base; the digest still needs a key
        relative = resolved.name
    repo = base.name or 'unnamed'
    raw = _read_spec_text(spec_path, purpose='gate-ledger')
    text = raw
    first_heading = re.search(r'^##[ \t]+', text, re.MULTILINE)
    header = text[: first_heading.start()] if first_heading else text
    kind = _declared_kind(header)[0] or 'undeclared'
    cert = _find_section(_split_top_sections(text), 'pre-mortem', 'certification')
    verdict = _verdict_head(_field(cert, 'verdict')) if cert is not None else ''
    return LedgerLine(
        ts=datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        gate=__version__,
        kit=__version__,
        repo=repo if _SLUG_RE.match(repo) else 'unnamed',
        spec=hashlib.sha256(f'{repo}/{relative}'.encode()).hexdigest()[:8],
        rev=spec_hash(spec_path)[:8],
        lines=len(text.splitlines()),
        kind=kind if kind in _KINDS else 'undeclared',
        mode='structure-only' if structure_only else 'full',
        passed=result.passed,
        exit_code=0 if result.passed else 1,
        probes={p.check: (p.candidates, p.fired, p.causes) for p in result.probes},
        warns={
            check: sum(1 for w in result.warnings if w.check == check)
            for check in sorted({w.check for w in result.warnings})
        },
        cert_present=cert is not None,
        verdict=verdict if verdict in _VERDICTS else ('OTHER' if cert is not None else 'NONE'),
        operator=bool(cert is not None and _field(cert, 'operator')),
    )


def ledger_path() -> Path | None:
    """Where the ledger lives, or None when it is switched off."""
    override = os.environ.get('KEEL_GATE_LEDGER', '').strip()
    if override.lower() == 'off':
        return None
    if override:
        return Path(override)
    state = os.environ.get('XDG_STATE_HOME', '').strip()
    if state:
        return Path(state) / 'keel' / 'gate-ledger.jsonl'
    return Path.home() / '.keel' / 'gate-ledger.jsonl'


def record_run(spec_path: Path, result: GateResult, *, structure_only: bool) -> None:
    """Append one line, fail-open. A telemetry fault must never reach the gate's exit code."""
    path = ledger_path()
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = serialize(line_for_run(spec_path, result, structure_only=structure_only))
        with path.open('a', encoding='utf-8') as handle:
            handle.write(encoded + '\n')
    except OSError:
        pass


def read_lines(path: Path) -> list[dict]:
    """Parse the ledger, skipping any line a partial write left unreadable (append-only file)."""
    if not path.is_file():
        return []
    out: list[dict] = []
    for raw in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if not raw.strip():
            continue
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return out
