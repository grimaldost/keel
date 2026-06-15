"""Definition-of-Ready gate.

A spec is Ready only when it is well-formed (Part A) AND a blind pre-mortem
certification is recorded (Part B / B1), so the gate never green-lights a spec on
structure alone. See docs/design/2026-06-05-dor-gate-design.md and ADR-0002.
"""

import re
from pathlib import Path

from keel.errors import format_error
from keel.models import GateResult, Violation

_PLACEHOLDER_RE = re.compile(r'\b(?:TBD|TODO|FIXME)\b|\?\?\?')
_SECTION_ID_RE = re.compile(r'§\d+')
_MIN_CRITERION_WORDS = 5
_ANCHOR_RE = re.compile(r'`([^`\s]+\.[A-Za-z0-9]+):(\d+)`(?:\s+`([^`]+)`)?')
_ADR_REF_RE = re.compile(r'`(docs/adr/(\d+)-[^`]+\.md)`')
_MODEL_ON_RE = re.compile(r'\*\*Model-on:\*\*\s*`([^`]+)`')
_REUSE_RE = re.compile(r'\*\*Reuse:\*\*\s*`([^`]+)`')
_SECTION_REF_RE = re.compile(r'§(\d+)(?![.\d])')  # a bare §N, not a sub-decimal §N.M
_DOC_CUES = frozenset({'doctrine', 'concepts', 'readme', 'adr', 'contributing'})
_CUE_STRIP = '\'"`*()[]{}.,;:'  # surrounding punctuation peeled off a preceding cue word
_CLAIM_RE = re.compile(r'\b(enforced|guaranteed)\b', re.IGNORECASE)
_NEG_TOKENS = frozenset({'not', 'never', 'to', 'be', 'will', 'once', 'no'})
_ANCHOR_RANGE_RE = re.compile(r'`([^`\s]+\.[A-Za-z0-9]+):(\d+)-(\d+)`')
_OPEN = frozenset('([{')
_CLOSE = frozenset(')]}')


def check_spec_ready(spec_path: Path, *, structure_only: bool = False) -> GateResult:
    """Assert a spec is Ready: well-formed (Part A) and pre-mortem-certified (Part B).

    A pass means the spec is structurally well-formed AND carries a recorded blind
    pre-mortem certification (ADR-0002); it never passes on structure alone. With
    ``structure_only`` set, only Part A (A1-A12) runs - the author-loop mode that
    suppresses the expected B1 PENDING before a pre-mortem is recorded.
    """
    if not spec_path.exists():
        raise FileNotFoundError(
            format_error(
                what=f'Spec not found: {spec_path}.',
                why='check-ready needs an existing spec file to gate.',
                fix='Pass the path to a spec written from spec-template.md.',
            )
        )
    text = spec_path.read_text(encoding='utf-8')
    sections = _split_top_sections(text)
    subsections = _subsections(_find_section(sections, 'numbered', 'sections') or '')
    section_ids = [m.group(1) for title, _ in subsections if (m := re.match(r'(§\d+)\b', title))]

    violations: list[Violation] = []
    violations += _check_numbered(subsections)
    violations += _check_acceptance(subsections)
    violations += _check_placeholders(text)
    violations += _check_manifest(_find_section(sections, 'section', 'manifest'), section_ids)
    violations += _check_paths(_find_section(sections, 'concept', 'module'), subsections, spec_path)
    cert = _find_section(sections, 'pre-mortem', 'certification')
    violations += _check_anchors(text, spec_path)
    violations += _check_anchor_ranges(text, spec_path)
    violations += _check_adr_numbers(text, spec_path)
    violations += _check_references(text, spec_path)
    violations += _check_section_refs(text, section_ids)
    violations += _check_enforcement_claims(sections, text)
    violations += _check_fold_ledger(cert, spec_path)
    if not structure_only:
        violations += _check_premortem(cert)

    return GateResult(passed=not violations, violations=tuple(violations))


# --- parsing -----------------------------------------------------------------


def _split_top_sections(text: str) -> list[tuple[str, str]]:
    """Split a doc into (title, body) pairs at each top-level '## ' heading."""
    matches = list(re.finditer(r'^##[ \t]+(.+?)[ \t]*$', text, re.MULTILINE))
    out: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((match.group(1).strip(), text[start:end]))
    return out


def _find_section(sections: list[tuple[str, str]], *keywords: str) -> str | None:
    """Return the body of the first section whose title contains all keywords."""
    for title, body in sections:
        low = title.lower()
        if all(keyword in low for keyword in keywords):
            return body
    return None


def _subsections(body: str) -> list[tuple[str, str]]:
    """Split a section body into (heading, sub-body) pairs at each '### ' heading."""
    matches = list(re.finditer(r'^###[ \t]+(.+?)[ \t]*$', body, re.MULTILINE))
    out: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out.append((match.group(1).strip(), body[start:end]))
    return out


def _table_rows(body: str) -> list[list[str]]:
    """Return the data rows of a markdown table (header + separator dropped)."""
    rows: list[list[str]] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line.startswith('|'):
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if all(set(cell) <= set('-: ') for cell in cells):
            continue
        rows.append(cells)
    return rows


def _words(text: str) -> list[str]:
    """Word tokens, with markdown punctuation stripped, for triviality checks."""
    return [word for word in re.sub(r'[`*:#|]', ' ', text).split() if word]


def _extract_path(cell: str) -> str | None:
    """The path a concept→module cell points at (first backtick token, else text)."""
    backticked = re.search(r'`([^`]+)`', cell)
    if backticked:
        return backticked.group(1).strip()
    cleaned = re.sub(r'\(to be created\)', '', cell, flags=re.IGNORECASE).strip()
    return cleaned or None


def _id_or_title(title: str) -> str:
    """The §N id of a section heading, or the raw title if it is not numbered."""
    match = re.match(r'(§\d+)', title)
    return match.group(1) if match else title


def _resolve_base(spec_path: Path) -> Path:
    """The directory paths are resolved against: the spec's git root, else its parent."""
    start = spec_path.resolve().parent
    for candidate in (start, *start.parents):
        if (candidate / '.git').exists():
            return candidate
    return start


def _field(body: str, name: str) -> str:
    """The value of a '- **Name:** value' line in a block, or '' if absent."""
    for line in body.splitlines():
        match = re.match(rf'^[\-*\s]*{name}[\s*]*:[\s*]*(.*?)[\s*]*$', line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''


def _resolve_anchor(
    base: Path, path: str, line_no: int, where: str
) -> tuple[list[str] | None, Violation | None]:
    """Resolve a `path:line` anchor: (file lines, None) if it resolves, else (None, Violation)."""
    target = base / path
    if not target.exists():
        return None, Violation(where, f'anchor path {path!r} does not exist.')
    lines = target.read_text(encoding='utf-8', errors='replace').splitlines()
    if line_no < 1 or line_no > len(lines):
        return None, Violation(
            where, f'anchor line {line_no} is out of range ({len(lines)} lines).'
        )
    return lines, None


def _bracket_balance(lines: list[str]) -> int:
    """Net unclosed-bracket depth over Python lines, ignoring strings and `#` comments.

    Single- and triple-quoted strings are skipped (a triple-quoted string spans lines), so a
    bracket inside a string or a comment does not count. This is a Python-literal notion; callers
    restrict it to `.py`/`.pyi` anchors.
    """
    depth = 0
    quote: str | None = None  # "'" / '"' (single) or a 3-char triple-quote opener
    for line in lines:
        i, n = 0, len(line)
        while i < n:
            if quote is not None:
                if len(quote) == 3:
                    if line[i : i + 3] == quote:
                        quote, i = None, i + 3
                        continue
                    i += 1
                    continue
                ch = line[i]
                if ch == '\\':
                    i += 2  # skip the escaped char
                    continue
                if ch == quote:
                    quote = None
                i += 1
                continue
            triple = line[i : i + 3]
            if triple in ('"""', "'''"):
                quote, i = triple, i + 3
                continue
            ch = line[i]
            if ch == '#':
                break
            if ch in ('"', "'"):
                quote = ch
            elif ch in _OPEN:
                depth += 1
            elif ch in _CLOSE:
                depth -= 1
            i += 1
        if quote is not None and len(quote) == 1:
            quote = None  # a single-quoted string does not span lines; a triple-quoted one does
    return depth


# --- checks ------------------------------------------------------------------


def _check_numbered(subsections: list[tuple[str, str]]) -> list[Violation]:
    """A1: there are numbered sections and every section heading is numbered."""
    if not subsections:
        return [
            Violation('Numbered sections', 'no numbered sections found (expected "### §1 ...").')
        ]
    violations: list[Violation] = []
    for title, _ in subsections:
        if not re.match(r'§\d+\b', title):
            violations.append(
                Violation('Numbered sections', f'section heading is not numbered: {title!r}.')
            )
    return violations


def _check_acceptance(subsections: list[tuple[str, str]]) -> list[Violation]:
    """A2: every numbered section has a present, non-trivial acceptance criterion."""
    violations: list[Violation] = []
    for title, sub_body in subsections:
        where = _id_or_title(title)
        marker = re.search(r'acceptance\s+criterion', sub_body, re.IGNORECASE)
        if marker is None:
            violations.append(Violation(where, 'missing an acceptance criterion.'))
            continue
        words = _words(sub_body[marker.end() :])
        if len(words) < _MIN_CRITERION_WORDS:
            violations.append(
                Violation(
                    where, f'acceptance criterion is missing or trivial ({len(words)} words).'
                )
            )
    return violations


def _check_placeholders(text: str) -> list[Violation]:
    """A3: no TBD / TODO / FIXME / ??? placeholder tokens anywhere in the spec."""
    violations: list[Violation] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in _PLACEHOLDER_RE.finditer(line):
            violations.append(
                Violation(f'line {lineno}', f'placeholder token {match.group(0)!r} not allowed.')
            )
    return violations


def _check_manifest(manifest_body: str | None, section_ids: list[str]) -> list[Violation]:
    """A4: the PR↔section manifest is a bijection with full section coverage."""
    if manifest_body is None:
        return [Violation('PR ↔ section manifest', 'no PR ↔ section manifest found.')]
    cited: list[str] = []
    for cells in _table_rows(manifest_body):
        cited.extend(sid for cell in cells for sid in _SECTION_ID_RE.findall(cell))
    violations: list[Violation] = []
    if not cited:
        violations.append(Violation('PR ↔ section manifest', 'manifest has no PR → section rows.'))
    for sid in section_ids:
        count = cited.count(sid)
        if count == 0:
            violations.append(
                Violation('PR ↔ section manifest', f'section {sid} is not covered by any PR.')
            )
        elif count > 1:
            violations.append(
                Violation(
                    'PR ↔ section manifest',
                    f'section {sid} is covered by {count} PRs (not a bijection).',
                )
            )
    for sid in dict.fromkeys(cited):
        if sid not in section_ids:
            violations.append(
                Violation(
                    'PR ↔ section manifest',
                    f'manifest cites {sid}, which is not a numbered section.',
                )
            )
    return violations


def _check_paths(
    concept_body: str | None, subsections: list[tuple[str, str]], spec_path: Path
) -> list[Violation]:
    """A5: every concept→module path exists, or is 'to be created' and claimed by a section."""
    if concept_body is None:
        return [Violation('Concept → module map', 'no concept → module map found.')]
    base = _resolve_base(spec_path)
    section_text = '\n'.join(sub_body for _, sub_body in subsections)
    violations: list[Violation] = []
    for cells in _table_rows(concept_body):
        if len(cells) < 2:
            continue
        module_cell = cells[1]
        if 'module' in module_cell.lower() and 'file' in module_cell.lower():
            continue
        path = _extract_path(module_cell)
        if not path:
            continue
        if 'to be created' in module_cell.lower():
            if path not in section_text:
                violations.append(
                    Violation(
                        'Concept → module map',
                        f'"to be created" path {path!r} is not claimed by any section.',
                    )
                )
        elif not (base / path).exists():
            violations.append(
                Violation(
                    'Concept → module map',
                    f'referenced path {path!r} does not exist (nor marked "to be created").',
                )
            )
    return violations


def _check_anchors(text: str, spec_path: Path) -> list[Violation]:
    """Code-grounding: every `path:line` anchor resolves, and any quoted snippet matches."""
    base = _resolve_base(spec_path)
    violations: list[Violation] = []
    for match in _ANCHOR_RE.finditer(text):
        path, line_text, snippet = match.group(1), match.group(2), match.group(3)
        where = f'{path}:{line_text}'
        line_no = int(line_text)
        lines, violation = _resolve_anchor(base, path, line_no, where)
        if violation is not None:
            violations.append(violation)
            continue
        if snippet is not None and lines is not None:
            actual = ' '.join(lines[line_no - 1].split())
            if ' '.join(snippet.split()) not in actual:
                violations.append(
                    Violation(where, f'anchor snippet {snippet!r} does not match line {line_no}.')
                )
    return violations


def _check_anchor_ranges(text: str, spec_path: Path) -> list[Violation]:
    """A11: a `path:lo-hi` range anchor must close every bracket it opens (string/comment-aware).

    A range whose `hi` line leaves a bracket opened inside the range unclosed is a truncated
    citation (the observation window stops mid-literal). Verify-when-present: fires only on
    `path:lo-hi` range anchors; single-line `path:line` anchors (A6) are untouched. The
    bracket-balance is a Python-literal notion, so it runs only for `.py`/`.pyi` anchors — a range
    into a non-code file still has its file/line resolved, but is not balance-checked.
    """
    base = _resolve_base(spec_path)
    violations: list[Violation] = []
    for match in _ANCHOR_RANGE_RE.finditer(text):
        path, lo, hi = match.group(1), int(match.group(2)), int(match.group(3))
        where = f'{path}:{lo}-{hi}'
        lines, violation = _resolve_anchor(base, path, hi, where)
        if violation is not None:
            violations.append(violation)
            continue
        if lo < 1 or lo > hi or lines is None:
            violations.append(Violation(where, f'anchor range {lo}-{hi} is malformed.'))
            continue
        if path.endswith(('.py', '.pyi')) and _bracket_balance(lines[lo - 1 : hi]) > 0:
            violations.append(
                Violation(
                    where,
                    f'anchor range :{lo}-{hi} opens a bracket it does not close — '
                    'quote the literal complete or not at all.',
                )
            )
    return violations


_FOLD_NONE = frozenset({'', 'none', 'noneoutstanding', 'na', 'nil'})


def _fold_claimed(cert_body: str) -> bool:
    """R1 trigger: True if the certification's 'folded in' field names a non-trivial fold."""
    for line in cert_body.splitlines():
        if 'folded in' in line.lower():
            _, _, value = line.partition(':')
            return re.sub(r'[^a-z0-9]', '', value.lower()) not in _FOLD_NONE
    return False


def _check_fold_ledger(cert_body: str | None, spec_path: Path) -> list[Violation]:
    """A12 + R1: a claimed fold carries a ledger, and every ledger row's anchor resolves.

    R1 (a deliberate DoR tightening, NOT verify-when-present): a certification whose 'folded in'
    field names a non-trivial fold MUST carry a `### Fold ledger` with >=1 data row — so the DC3
    transformation-verification cannot be skipped by omission. A clean certify (folded in: none)
    dozes, so it does not retro-break. A12: when ledger rows are present, each row's `artifact:line`
    confirmation must resolve (the fold was recorded against a real line); it does not judge the
    fold's correctness — that stays Part B (ADR-0002). The blank/prose-cell case is exactly what
    A6 does not catch.
    """
    if cert_body is None:
        return []
    ledger = next(
        (sub for title, sub in _subsections(cert_body) if 'fold ledger' in title.lower()), None
    )
    rows = [cells for i, cells in enumerate(_table_rows(ledger)) if i > 0] if ledger else []
    if not rows:
        if _fold_claimed(cert_body):
            return [
                Violation(
                    'Fold ledger',
                    'the certification claims a fold but carries no `### Fold ledger` rows; '
                    'record one row (finding, target, artifact:line, confirmed) per finding (R1).',
                )
            ]
        return []
    base = _resolve_base(spec_path)
    violations: list[Violation] = []
    for cells in rows:
        if len(cells) < 3:
            continue
        anchor = re.sub(r'[`*]', '', cells[2]).strip()
        where = f'Fold ledger {cells[0].strip() or "(row)"}'
        match = re.match(r'(\S+\.[A-Za-z0-9]+):(\d+)$', anchor)
        if match is None:
            violations.append(
                Violation(where, 'fold-ledger row has no resolving `artifact:line` confirmation.')
            )
            continue
        _, violation = _resolve_anchor(base, match.group(1), int(match.group(2)), where)
        if violation is not None:
            violations.append(violation)
    return violations


def _check_adr_numbers(text: str, spec_path: Path) -> list[Violation]:
    """Code-grounding: a cited ADR number must match an existing ADR of that name, or be free."""
    adr_dir = _resolve_base(spec_path) / 'docs' / 'adr'
    violations: list[Violation] = []
    for match in _ADR_REF_RE.finditer(text):
        rel, number = match.group(1), match.group(2)
        declared = Path(rel).name
        existing = [p.name for p in adr_dir.glob(f'{number}-*.md')] if adr_dir.exists() else []
        if existing and declared not in existing:
            violations.append(Violation(rel, f'ADR number {number} already used: {existing}.'))
    return violations


def _symbol_defined(target: Path, symbol: str) -> bool:
    """A9: a name is 'defined' as a top-level def/class/assignment or an __all__ entry."""
    name = symbol.split('.', 1)[0]  # a further .member is out of A9's scope
    src = target.read_text(encoding='utf-8', errors='replace')
    defs = (
        rf'^\s*(?:async\s+)?def\s+{re.escape(name)}\b',
        rf'^\s*class\s+{re.escape(name)}\b',
        rf'^\s*{re.escape(name)}\s*[:=]',
    )
    if any(re.search(pattern, src, re.MULTILINE) for pattern in defs):
        return True
    return re.search(rf'__all__[^\n]*[\'"]{re.escape(name)}[\'"]', src, re.DOTALL) is not None


def _check_references(text: str, spec_path: Path) -> list[Violation]:
    """A9: every Model-on/Reuse reference present resolves (path exists; symbol defined)."""
    base = _resolve_base(spec_path)
    violations: list[Violation] = []
    for match in _MODEL_ON_RE.finditer(text):
        rel = match.group(1).strip()
        if not (base / rel).exists():
            violations.append(Violation('Model-on', f'reference path {rel!r} does not exist.'))
    for match in _REUSE_RE.finditer(text):
        ref = match.group(1).strip()
        rel, _, symbol = ref.partition('::')
        target = base / rel
        if not target.exists():
            violations.append(Violation(f'Reuse {ref}', f'reference path {rel!r} does not exist.'))
        elif symbol and not _symbol_defined(target, symbol):
            violations.append(
                Violation(f'Reuse {ref}', f'symbol {symbol!r} is not defined in {rel}.')
            )
    return violations


def _check_section_refs(text: str, section_ids: list[str]) -> list[Violation]:
    """A8: every bare intra-spec §N reference resolves to a numbered section.

    The `§` glyph is reserved for the spec's own sections; a `§N` that is part of a
    sub-decimal (`§4.5`), on a `###` heading line (a definition, not a reference), or
    preceded by a document/file cue (`doctrine §6`) is left alone.
    """
    known = set(section_ids)
    violations: list[Violation] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith('#'):  # a heading defines a section, it is not a ref
            continue
        for match in _SECTION_REF_RE.finditer(line):
            prev = re.search(r'(\S+)\s*$', line[: match.start()])
            cue = prev.group(1).lower().strip(_CUE_STRIP) if prev else ''
            if cue.endswith('.md') or cue in _DOC_CUES:  # a cross-document reference
                continue
            sid = f'§{match.group(1)}'
            if sid not in known:
                violations.append(
                    Violation(f'line {lineno}', f'reference {sid} resolves to no numbered section.')
                )
    return violations


def _check_enforcement_claims(sections: list[tuple[str, str]], text: str) -> list[Violation]:
    """A10: no prose claims an invariant 'enforced'/'guaranteed' that its status table denies.

    Keyed off the spec-template 'Enforcement status' table (the convention), not free-text
    parsing. Checked only when that table is present. A claim word inside backticks, or one
    negated/deferred by a nearby cue ('not', 'to be', 'will be', 'once'), does not fire.
    """
    body = _find_section(sections, 'enforcement')
    if body is None:
        return []
    non_enforced: dict[str, str] = {}
    for cells in _table_rows(body):
        if len(cells) < 2:
            continue
        key = re.sub(r'[`*]', '', cells[0]).strip()
        status = cells[1].strip().lower()
        if key and 'invariant' not in key.lower() and status and status != 'enforced':
            non_enforced[key] = status
    if not non_enforced:
        return []
    violations: list[Violation] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        bare = re.sub(r'`[^`]*`', '', line)  # drop inline code: a quoted `enforced` is fine
        claim = _CLAIM_RE.search(bare)
        if claim is None:
            continue
        preceding = {word.lower().strip('.,;:') for word in bare[: claim.start()].split()[-4:]}
        if preceding & _NEG_TOKENS:  # negated or deferred: "not", "to be", "will be", "once"
            continue
        for key, status in non_enforced.items():
            if key.lower() in bare.lower():
                violations.append(
                    Violation(
                        f'line {lineno}',
                        f'claims {key!r} is "{claim.group(0)}" but its enforcement status '
                        f'is {status!r}.',
                    )
                )
    return violations


def _check_premortem(cert_body: str | None) -> list[Violation]:
    """B1: a blind pre-mortem certification (Verdict CERTIFIED + a reviewer) is recorded."""
    if cert_body is None:
        return [
            Violation(
                'Pre-mortem certification',
                'no "## Pre-mortem certification" block; a non-author pre-mortem '
                'must certify the spec (ADR-0002).',
            )
        ]
    violations: list[Violation] = []
    raw = _field(cert_body, 'verdict')
    leading = re.match(
        r'\s*([A-Za-z][A-Za-z-]*)', raw
    )  # the bare verdict token, hyphens kept whole
    if (leading.group(1).upper() if leading else '') != 'CERTIFIED':
        verdict = raw or '(none)'
        violations.append(
            Violation(
                'Pre-mortem certification',
                f'pre-mortem verdict is {verdict!r}, not "CERTIFIED" — the verdict field must '
                'lead with the bare token CERTIFIED (trailing prose is allowed).',
            )
        )
    if not _field(cert_body, 'reviewer'):
        violations.append(
            Violation(
                'Pre-mortem certification',
                'pre-mortem certification names no reviewer (must be a non-author).',
            )
        )
    return violations
