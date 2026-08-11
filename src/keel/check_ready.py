"""Definition-of-Ready gate.

A spec is Ready only when it is well-formed (Part A) AND a blind pre-mortem
certification is recorded (Part B / B1), so the gate never green-lights a spec on
structure alone. See docs/design/2026-06-05-dor-gate-design.md and ADR-0002.
"""

import hashlib
import re
from pathlib import Path

from keel.errors import format_error
from keel.models import GateResult, Violation

# A3 placeholders: the four legacy tokens, plus the spec-template's angle-bracket idiom
# (`<title>`, `<the observable condition ...>`). The angle-bracket form is matched on the shared
# prose view (`_mask_inline_spans` space-fills inline-code spans, including a span hard-wrapped
# across a line break), so documented CLI syntax like `keel init <target>` in backticks is fine —
# even wrapped mid-span — while a leftover bare `<title>` heading placeholder fails (A3).
_PLACEHOLDER_RE = re.compile(r'\b(?:TBD|TODO|FIXME)\b|\?\?\?')
_ANGLE_PLACEHOLDER_RE = re.compile(r'<[a-z][^>\n]{2,}>')
_SECTION_ID_RE = re.compile(r'§\d+')
_MIN_CRITERION_WORDS = 5
# Anchor tokens are `path:line` where path carries no colon (so `host:port`, `a:b:c` grep triples,
# and `scheme://...` never parse as anchors). `_anchor_shaped` then rejects IPs/versions; the
# optional snippet must not itself be anchor-shaped (else two adjacent anchors would eat each other)
# and is same-line only ([ \t], never \n).
_ANCHOR_RE = re.compile(r'`([^`\s:]+):(\d+)`(?:[ \t]+`(?!\S*:\d+`)([^`]+)`)?')
_ANCHOR_RANGE_RE = re.compile(r'`([^`\s:]+):(\d+)-(\d+)`')
_EXT_RE = re.compile(r'\.[A-Za-z][A-Za-z0-9]*$')  # a real file extension, not `.1` of an IP/version
_KNOWN_BARE_ANCHORS = frozenset(
    {
        'Makefile',
        'Dockerfile',
        'LICENSE',
        'Rakefile',
        'Procfile',
        'Gemfile',
        'CODEOWNERS',
        'Vagrantfile',
        'Jenkinsfile',
    }
)
_ADR_REF_RE = re.compile(r'`(docs/adr/(\d+)-[^`]+\.md)`')
_MODEL_ON_RE = re.compile(r'\*\*Model-on:\*\*\s*`([^`]+)`')
_REUSE_RE = re.compile(r'\*\*Reuse:\*\*\s*`([^`]+)`')
_SECTION_REF_RE = re.compile(r'§(\d+)(?![.\d])')  # a bare §N, not a sub-decimal §N.M
# A trailing run of §N refs joined by whitespace/slash/dash/comma, stripped before the A8 cue
# lookback so a joined section range (a slash range, or an en-dash range) keeps its preceding cue.
_TRAILING_SECREFS_RE = re.compile(r'(?:§\d+[ \t/,–—-]*)+$')  # noqa: RUF001 (en/em dash joiners)
_DOC_CUES = frozenset({'doctrine', 'concepts', 'readme', 'adr', 'contributing'})
# A preceding token that names an external document, so its `§N` is a cross-document ref, not an
# intra-spec one: a *.md file, a listed cue word, or a standards identifier (ADR-12, RFC-9110,
# PEP8, ISO8601, or the same with a trailing space before the number, handled by the number-cue).
_DOC_ID_CUE_RE = re.compile(r'^(?:adr|rfc|pep|iso|sec|section)[-\s]?\d*$', re.IGNORECASE)
_CUE_STRIP = '\'"`*()[]{}.,;:'  # surrounding punctuation peeled off a preceding cue word
_CLAIM_RE = re.compile(r'\b(enforced|guaranteed)\b', re.IGNORECASE)
# A negation/deferral immediately before the claim word (checked against the text right up to the
# claim, so it survives a hard line-wrap): "not/never/no enforced", "isn't/aren't enforced",
# "to be / will be / would be enforced", "not yet / planned / once ... enforced". Applied to the
# words just before the claim, so a real over-claim ("... is fully enforced") still fires.
_NEG_RE = re.compile(
    r'\bnot\b|\bnever\b|\bno\b|n[\'’]t\b|\byet\b|\bplanned\b'  # noqa: RUF001 (curly apostrophe intended)
    r'|\bto\s+be\b|\bwill\s+be\b|\bwould\s+be\b|\bonce\b'
)
_FENCE_RE = re.compile(r'^\s{0,3}(`{3,}|~{3,})(.*)$')
_OPEN = frozenset('([{')
_CLOSE = frozenset(')]}')


def _mask_fenced(text: str) -> str:
    """Blank the contents of fenced code blocks, preserving line count so line numbers stay true.

    A spec quotes code, `# TODO` markers, example `### headings`, and even a sample certification
    block inside ``` / ~~~ fences; those are illustrative, not live spec structure. Masking them
    before section-splitting and every line scan stops a fenced example from forging the B1
    certification (a fenced `Verdict: CERTIFIED` shadowing a real REJECTED one) or a quoted marker
    from false-failing an honest spec. Each masked line becomes empty, so `splitlines()` still
    numbers the surviving lines exactly as the raw text did.

    An UNCLOSED fence masks to end-of-file: this fails *closed* (it blanks any real certification
    below the open fence, so B1 reports a missing block) — it can never forge a passing verdict.
    """
    out: list[str] = []
    fence: str | None = None  # the fence char ("`"/"~") while inside a block
    fence_len = 0
    for line in text.splitlines():
        match = _FENCE_RE.match(line)
        if fence is None:
            if match is not None:
                fence, fence_len = match.group(1)[0], len(match.group(1))
                out.append('')
            else:
                out.append(line)
            continue
        out.append('')  # inside a fence: blank every line, including the closing fence
        if (
            match is not None
            and match.group(1)[0] == fence
            and len(match.group(1)) >= fence_len
            and not match.group(2).strip()
        ):
            fence = None
    return '\n'.join(out)


_INLINE_SPAN_RE = re.compile(r'(?<!`)(`+)(?!`)((?:[^`\n]|\n(?![ \t]*\n))+?)\1(?!`)')


def _mask_inline_spans(text: str) -> str:
    """Space-fill inline-code spans — including a span hard-wrapped across a line break.

    The shared *prose* view: callers pass `_mask_fenced` output (fenced blocks already blank), and
    this pass blanks `inline code` the way a renderer treats it — a span may cross line breaks
    within a paragraph but never a blank line, so a stray unpaired backtick cannot eat the rest of
    the document. Spaces, never deletion: every line keeps its exact length, so a later violation's
    line number stays true. Consumed by the prose scanners (A3's angle idiom, A8's `§N` detection);
    the anchor scanners (A6/A9/A11, ADR refs) keep the unmasked view — their tokens are backticked.
    """
    return _INLINE_SPAN_RE.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text)


def _split_cells(line: str) -> list[str]:
    r"""Split a markdown table row on `|`, keeping a pipe inside a backtick span (or escaped `\|`).

    A table cell cannot be fenced, so the fence doctrine cannot protect a required cell that carries
    a backticked type union (`` `-> pl.DataFrame | None` ``); this splitter is the one place a
    cell's own pipes are masked, feeding every table parser (A4/A5/A10/A12). An unclosed backtick
    leaves its pipes as delimiters (fails toward today's behaviour).
    """
    protected = re.sub(
        r'`[^`]*`', lambda m: m.group(0).replace('|', '\x00'), line.replace('\\|', '\x01')
    )
    return [
        cell.replace('\x00', '|').replace('\x01', '\\|').strip()
        for cell in protected.strip().strip('|').split('|')
    ]


def _anchor_shaped(path: str) -> bool:
    """True if a matched `token:line` token is really a file anchor (not an IP, version, or URL)."""
    if '://' in path:
        return False
    name = path.replace('\\', '/').rsplit('/', 1)[-1]
    return '/' in path or bool(_EXT_RE.search(path)) or name in _KNOWN_BARE_ANCHORS


def _bad_anchor_platform(path: str) -> str | None:
    """A portability reason a resolvable-looking anchor must be rejected, or None if it is clean.

    A backslash separator or a POSIX-absolute path resolves on one OS and dangles on another, so a
    'deterministic' gate would give environment-dependent verdicts. (A drive-letter path like
    `C:/x` carries a colon and never reaches here — it is not recognized as an anchor at all.)
    """
    if '\\' in path:
        return 'use forward slashes'
    if path.startswith('/'):
        return 'anchors are repo-root-relative, not absolute'
    return None


def _read_spec_text(spec_path: Path, *, purpose: str) -> str:
    """Read a spec as UTF-8 text, or raise the not-runnable FileNotFoundError contract."""
    if not spec_path.is_file():
        raise FileNotFoundError(
            format_error(
                what=f'Spec not found (or not a readable file): {spec_path}.',
                why=f'{purpose} needs an existing spec FILE (a missing path or a '
                'directory is not runnable).',
                fix='Pass the path to a spec file written from spec-template.md.',
            )
        )
    try:
        return spec_path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError) as exc:
        raise FileNotFoundError(
            format_error(
                what=f'Spec is not readable UTF-8 text: {spec_path}.',
                why=f'{purpose} reads the spec as UTF-8 and could not decode it ({exc}).',
                fix='Save the spec as UTF-8 (the § glyph is the usual culprit on a cp1252 editor).',
            )
        ) from exc


def spec_hash(spec_path: Path) -> str:
    """B2's canonical certification hash: sha256 of the spec minus its certification section.

    The `## Pre-mortem certification` section's lines (heading included, through the next `## `
    heading or EOF) are REMOVED from the ``splitlines()`` sequence and the remainder re-joined
    with newlines — not blanked: blanked lines still contribute newline bytes, so a growing fold
    ledger would change the very hash its own recording is part of (ADR-0014). Removal plus
    splitlines normalization also makes the hash indifferent to CRLF/LF. Fenced text is masked
    only to LOCATE the section (a fenced example heading cannot shift the span); the hash is
    computed over the raw lines.
    """
    raw = _read_spec_text(spec_path, purpose='spec-hash')
    masked_lines = _mask_fenced(raw).splitlines()
    raw_lines = raw.splitlines()
    keep: list[str] = []
    in_cert = False
    for i, masked in enumerate(masked_lines):
        heading = re.match(r'^##[ \t]+(.+?)[ \t]*$', masked)
        if heading is not None:
            low = heading.group(1).lower()
            in_cert = 'pre-mortem' in low and 'certification' in low
        if not in_cert:
            keep.append(raw_lines[i])
    return hashlib.sha256('\n'.join(keep).encode('utf-8')).hexdigest()


_KIT_STAMP_RE = re.compile(r'<!--\s*keel kit (\d+)\.(\d+)\.(\d+)\s*-->')
_KIT_VERSION_RE = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')


def _kit_stamp(text: str, header: str) -> str | None:
    """The kit version a spec declares, from the header `Kit:` field or the legacy HTML comment.

    T0.3 moves the stamp into the visible header, because the HTML comment lived below the closing
    rule and every authored spec in the census had lost it at hand-copy. The comment form is still
    read — retiring it from the template does not retire it from the specs already carrying it.
    """
    declared = _field(header, 'kit')
    if declared and _KIT_VERSION_RE.match(token := _first_path_token(declared)):
        return token
    comment = _KIT_STAMP_RE.search(text)
    return '.'.join(comment.groups()) if comment is not None else None


def _kit_skew_warning(text: str, header: str) -> list[str]:
    """W1: a spec stamped from a different kit MAJOR.MINOR — or carrying no stamp — self-announces.

    WARN-only. A patch difference stays silent (gate semantics are pinned per minor). T0.3 widens
    the check to the UNSTAMPED case, which is the only one the census ever observed: no authored
    spec carried a stamp at all, so a verify-when-present skew check had zero material forever and
    could neither fire nor be defended. Runs in the Part A path so the author loop
    (--structure-only) sees it — that is where a stale kit bites first.
    """
    from keel import __version__

    stamp = _kit_stamp(text, header)
    if stamp is None:
        return [
            f'WARN: this spec is unstamped — it declares no kit version, so kit↔gate skew is '
            f'undetectable on it. Add `- **Kit:** {__version__}` to the header beside Date and '
            'Status (W1).'
        ]
    if stamp.split('.')[:2] == __version__.split('.')[:2]:
        return []
    return [
        f'WARN: spec stamped from kit {stamp}, gate is {__version__} — the kit and the gate '
        'moved apart; regenerate the spec scaffold or diff the kit before trusting old guidance.'
    ]


def check_spec_ready(spec_path: Path, *, structure_only: bool = False) -> GateResult:
    """Assert a spec is Ready: well-formed (Part A) and pre-mortem-certified (Part B).

    A pass means the spec is structurally well-formed AND carries a recorded blind
    pre-mortem certification (ADR-0002); it never passes on structure alone. With
    ``structure_only`` set, only Part A (A1-A12) runs - the author-loop mode that
    suppresses the expected B1 PENDING before a pre-mortem is recorded.
    """
    raw = _read_spec_text(spec_path, purpose='check-ready')
    # Fenced code blocks are illustrative, not live structure: mask them before any parse or scan.
    text = _mask_fenced(raw)
    # The prose view additionally space-fills inline-code spans (wrapped ones included), for the
    # scanners that must not read code (A3 angle idiom, A8 `§N` detection); offsets stay true.
    prose = _mask_inline_spans(text)
    sections = _split_top_sections(text)
    numbered_body = _find_section(sections, 'numbered', 'sections')
    subsections = _subsections(numbered_body or '')
    section_ids = [m.group(1) for title, _ in subsections if (m := re.match(r'(§\d+)\b', title))]

    first_heading = re.search(r'^##[ \t]+', text, re.MULTILINE)
    header = text[: first_heading.start()] if first_heading else text

    violations: list[Violation] = []
    warnings: list[str] = []
    warnings += _kit_skew_warning(text, header)
    # §11 (0.12.0) + KEEL-B01: two header declarations widen the *absence* tolerance of the
    # Part-A structural trio, and nothing else. `Phases: … (Decompose: skipped)` relaxes the
    # manifest (ADR-0014); `Kind: single-change` relaxes all three, because a spec that decomposes
    # into nothing has no manifest, no concept→module map and no numbered sections to write. A
    # section that IS present is still checked in full, and the declaration is content the
    # pre-mortem can challenge — not an escape hatch. An unreadable Kind relaxes nothing.
    kind, kind_violation = _declared_kind(header)
    if kind_violation is not None:
        violations.append(kind_violation)
    single_change = kind == 'single-change'
    phases = _field(header, 'phases').lower()
    decompose_skipped = 'decompose' in phases and 'skipped' in phases
    if numbered_body is not None or not single_change:
        violations += _check_numbered(subsections)
        violations += _check_acceptance(subsections)
    else:
        # With no numbered sections there is nothing for A2 to read, so the criterion floor moves
        # to the document: a relaxed spec still promises something observable.
        violations += _check_document_acceptance(text)
    violations += _check_placeholders(text, prose)
    manifest_body = _find_section(sections, 'section', 'manifest')
    if manifest_body is not None or not (decompose_skipped or single_change):
        violations += _check_manifest(manifest_body, section_ids)
    concept_body = _find_section(sections, 'concept', 'module')
    if concept_body is not None or not single_change:
        violations += _check_paths(concept_body, subsections, spec_path)
    cert = _find_section(sections, 'pre-mortem', 'certification')
    anchor_violations, anchor_warnings = _check_anchors(text, spec_path)
    violations += anchor_violations
    warnings += anchor_warnings
    range_violations, range_warnings = _check_anchor_ranges(text, spec_path)
    violations += range_violations
    warnings += range_warnings
    violations += _check_adr_numbers(text, spec_path)
    violations += _check_references(text, spec_path)
    violations += _check_section_refs(text, prose, section_ids)
    violations += _check_enforcement_claims(sections, text)
    ledger_violations, ledger_warnings = _check_fold_ledger(cert, spec_path)
    violations += ledger_violations
    warnings += ledger_warnings
    if not structure_only:
        premortem_violations, premortem_warnings = _check_premortem(cert)
        violations += premortem_violations
        warnings += premortem_warnings
        if cert is not None:
            artifact_violations, artifact_warnings = _check_certification_artifact(cert, spec_path)
            violations += artifact_violations
            warnings += artifact_warnings
        warnings += _status_currency_warning(header, cert)

    return GateResult(passed=not violations, violations=tuple(violations), warnings=tuple(warnings))


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
        cells = _split_cells(line)
        if all(set(cell) <= set('-: ') for cell in cells):
            continue
        rows.append(cells)
    return rows


def _first_table_rows(body: str) -> list[list[str]]:
    """Rows of only the FIRST contiguous markdown table in body (header kept, separator dropped).

    Unlike `_table_rows`, this stops at the first blank/non-table line after the table starts, so a
    sibling table sharing the same `### Fold ledger` subsection span is not merged in. By template
    convention the ledger is the first table under that heading; a table placed before it is
    out-of-contract.
    """
    rows: list[list[str]] = []
    started = False
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith('|'):
            started = True
            cells = _split_cells(line)
            if all(set(cell) <= set('-: ') for cell in cells):
                continue
            rows.append(cells)
        elif started:
            break
    return rows


def _words(text: str) -> list[str]:
    """Word tokens, with markdown punctuation stripped, for triviality checks."""
    return [word for word in re.sub(r'[`*:#|]', ' ', text).split() if word]


def _first_path_token(value: str) -> str:
    """The path token a path-valued field or cell names, with trailing prose ignored ('' if none).

    KEEL-B03, the one home for "which token here is the path": the first backticked token when the
    value carries one, else its first whitespace-delimited token. Field extraction used to consume
    more text than the field it names — `Certification artifact: `x.md` (round 2, round 1 at …)`
    resolved the whole remainder as a path and reddened the gate on a well-formed record. Any
    path-valued field added later reads through here rather than re-deciding it locally.
    """
    backticked = re.search(r'`([^`]+)`', value)
    if backticked:
        return backticked.group(1).strip()
    tokens = value.split()
    return tokens[0].strip('`*,;()') if tokens else ''


def _extract_path(cell: str) -> str | None:
    """The path a concept→module cell points at (first backtick token, else text)."""
    if '`' in cell:
        return _first_path_token(cell) or None
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


_SPEC_KINDS = ('series', 'single-change')
_DECLARE_SMALLER = (
    'add it, or — when this spec really is one change with nothing to decompose — declare '
    '`- **Kind:** single-change` in the header (KEEL-B01: the declaration relaxes the absent '
    'trio; a section that IS present is still checked in full)'
)


def _declared_kind(header: str) -> tuple[str, Violation | None]:
    """The header's declared spec kind, or ('' , Violation) when it names an unknown one.

    A kind keel cannot read relaxes nothing — the alternative (silently ignoring it) hands back a
    trio failure with no hint that the declaration was the problem. The violation names the
    offending token, not the row.
    """
    raw = _field(header, 'kind')
    if not raw:
        return '', None
    token = raw.split()[0].strip('`*.,;:').lower()
    if token in _SPEC_KINDS:
        return token, None
    return '', Violation(
        'Kind',
        f'declared spec kind {token!r} is not one of '
        f'{" | ".join(_SPEC_KINDS)} — it relaxes nothing as written.',
    )


_VENDOR_DIRS = frozenset({'.git', '.venv', 'node_modules', '__pycache__', 'site-packages'})


def _basename_matches(base: Path, path: str) -> list[Path]:
    """Every repo file matching the path's basename, vendor/VCS trees excluded.

    An in-tree virtualenv must not defeat exactly-one (0.12.0 §4). Called only when the anchor
    failed to resolve as written, so the rglob cost is paid only on that path.
    """
    name = path.replace('\\', '/').rsplit('/', 1)[-1]
    if not name:
        return []
    return [
        candidate
        for candidate in base.rglob(name)
        if candidate.is_file() and not (_VENDOR_DIRS & set(candidate.relative_to(base).parts[:-1]))
    ]


def _resolve_anchor(
    base: Path, path: str, line_no: int, where: str
) -> tuple[list[str] | None, Violation | None, list[str]]:
    """Resolve a `path:line` anchor: (file lines, None, warnings), else (None, Violation, []).

    KEEL-B04: a path that does not resolve as written but whose basename matches exactly one repo
    file resolves to that file, with a WARN naming the expansion — the gate already computed that
    resolution and offered it only as a hint, so a fold of keel's own reviewer's shorthand anchors
    manufactured gate failures. The expansion is a resolution, not a pass: the line range and any
    snippet are still verified against the file it found. Ambiguity (or no match) still fails, and
    the ambiguous message names the candidates.
    """
    target = base / path
    warnings: list[str] = []
    if not target.is_file():
        matches = _basename_matches(base, path)
        if len(matches) != 1:
            candidates = ''
            if matches:
                shown = ', '.join(
                    sorted(match.relative_to(base).as_posix() for match in matches)[:5]
                )
                candidates = (
                    f' {len(matches)} files share that basename ({shown}) — name the one you mean.'
                )
            return (
                None,
                Violation(
                    where,
                    f'anchor path {path!r} does not exist as a file '
                    f'(anchors are repo-root-relative, e.g. src/pkg/mod.py:42).{candidates}',
                ),
                [],
            )
        target = matches[0]
        expanded = target.relative_to(base).as_posix()
        warnings.append(
            f'WARN: anchor {path}:{line_no} resolved by unique basename match to '
            f'{expanded}:{line_no} — write anchors repo-root-relative (A6); the expansion is '
            'unique today and a second file of that name would turn this WARN into a failure.'
        )
    lines = target.read_text(encoding='utf-8', errors='replace').splitlines()
    if line_no < 1 or line_no > len(lines):
        return (
            None,
            Violation(where, f'anchor line {line_no} is out of range ({len(lines)} lines).'),
            [],
        )
    return lines, None, warnings


def _bracket_balance(lines: list[str]) -> tuple[int, bool]:
    """(net unclosed depth, ever-negative?) over Python lines, string/comment-aware.

    Single- and triple-quoted strings are skipped (a triple-quoted string spans lines), so a
    bracket inside a string or a comment does not count. This is a Python-literal notion; callers
    restrict it to `.py`/`.pyi` anchors. A net > 0 is a head-truncated citation (opens a bracket it
    never closes); an ever-negative depth is a tail-truncated one (closes a bracket opened before
    the window) — both mean the observation window stopped mid-literal.
    """
    depth = 0
    ever_negative = False
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
                if depth < 0:
                    ever_negative = True
            i += 1
        if quote is not None and len(quote) == 1:
            quote = None  # a single-quoted string does not span lines; a triple-quoted one does
    return depth, ever_negative


# --- checks ------------------------------------------------------------------


def _check_numbered(subsections: list[tuple[str, str]]) -> list[Violation]:
    """A1: there are numbered sections and every section heading is numbered."""
    if not subsections:
        return [
            Violation(
                'Numbered sections',
                'no numbered sections found: expected a "## Numbered sections" section with '
                f'"### §N <title>" subsections — {_DECLARE_SMALLER}.',
            )
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
        # Count only the criterion's own paragraph (up to the first blank line), so an EMPTY
        # criterion followed by unrelated prose cannot launder the >=5-word floor (A2).
        para = re.split(r'\n[ \t]*\n', sub_body[marker.end() :], maxsplit=1)[0]
        words = _words(para)
        if len(words) < _MIN_CRITERION_WORDS:
            violations.append(
                Violation(
                    where, f'acceptance criterion is missing or trivial ({len(words)} words).'
                )
            )
    return violations


def _check_document_acceptance(text: str) -> list[Violation]:
    """A2 at document scope: a `Kind: single-change` spec with no §N still names its criterion.

    Runs only where the numbered-sections requirement was relaxed away (KEEL-B01). Same floor as
    A2 — a present, non-trivial criterion paragraph — read over the whole spec rather than per
    section, so the relaxation buys a smaller shape and not a weaker promise.
    """
    for marker in re.finditer(r'acceptance\s+criterion', text, re.IGNORECASE):
        para = re.split(r'\n[ \t]*\n', text[marker.end() :], maxsplit=1)[0]
        if len(_words(para)) >= _MIN_CRITERION_WORDS:
            return []
    return [
        Violation(
            'Acceptance criterion',
            'a spec declared `Kind: single-change` carries no non-trivial acceptance criterion '
            f'(a present criterion of >= {_MIN_CRITERION_WORDS} words) — the declaration relaxes '
            'the structural trio, not the observable condition that means the change is done.',
        )
    ]


def _check_placeholders(text: str, prose: str) -> list[Violation]:
    """A3: no TBD/TODO/FIXME/??? token, and no leftover `<...>` template placeholder, in the spec.

    The angle-bracket idiom is matched on the shared prose view (`_mask_inline_spans`, wrapped spans
    included), so a documented `keel init <target>` stays legal — even wrapped mid-span — while a
    stamped `### §1 <title>` heading or an unfilled `<the observable condition ...>` acceptance
    criterion is caught. The legacy tokens keep scanning the fence-masked line: a backticked `TODO`
    still fires, matching the spec-template's fence-only quoting doctrine.
    """
    violations: list[Violation] = []
    for lineno, (line, masked) in enumerate(
        zip(text.splitlines(), prose.splitlines(), strict=True), 1
    ):
        for match in _PLACEHOLDER_RE.finditer(line):
            violations.append(
                Violation(f'line {lineno}', f'placeholder token {match.group(0)!r} not allowed.')
            )
        for match in _ANGLE_PLACEHOLDER_RE.finditer(masked):
            if '://' in match.group(0):  # an autolink <https://...>, not a placeholder
                continue
            violations.append(
                Violation(
                    f'line {lineno}',
                    f'unfilled template placeholder {match.group(0)!r} — replace it with real '
                    'content (angle-bracket placeholders outside `code` are not allowed).',
                )
            )
    return violations


def _check_manifest(manifest_body: str | None, section_ids: list[str]) -> list[Violation]:
    """A4: the PR↔section manifest is a true bijection — one section per PR, one PR per section.

    Both sides are checked. The section id is read ONLY from the "Implements section" column (the
    header naming it, else the second column), so a §N mentioned in a "One concern?" / "Depends on"
    comment cell neither breaks the count nor lets a PR smuggle a second section past the gate; and
    a single PR row citing two sections now fails (the scope-bundling A4 exists to forbid).
    """
    if manifest_body is None:
        return [
            Violation(
                'PR ↔ section manifest',
                f'no "## PR ↔ section manifest" section found — {_DECLARE_SMALLER}, or declare '
                '`- **Phases:** … (Decompose: skipped)` for a round that stops before Decompose.',
            )
        ]
    rows = _table_rows(manifest_body)
    header = rows[0] if rows else []
    section_col = next(
        (i for i, h in enumerate(header) if 'section' in h.lower() or 'implements' in h.lower()),
        1 if len(header) > 1 else 0,
    )
    violations: list[Violation] = []
    cited: list[str] = []
    for row in rows[1:]:
        cell = row[section_col] if section_col < len(row) else ''
        ids = _SECTION_ID_RE.findall(cell)
        cited.extend(ids)
        if len(ids) != 1:
            pr = row[0].strip() if row else '(row)'
            violations.append(
                Violation(
                    'PR ↔ section manifest',
                    f'PR row {pr!r} cites {len(ids)} sections in its section column; each PR must '
                    'implement exactly one section.',
                )
            )
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
    """A5: every concept→module path exists, or is 'to be created' and claimed by a section.

    A "to be created" path is claimed by its full repo-root-relative form, or — when a section
    body names the file by its bare basename and that basename is unique among the map's
    "to be created" rows — by the basename (0.12.0 §4: the body/map ergonomics the field hit on
    three consumers). An ambiguous basename keeps the full-path requirement.
    """
    if concept_body is None:
        return [
            Violation(
                'Concept → module map',
                f'no "## Concept → module map" section found — {_DECLARE_SMALLER}.',
            )
        ]
    base = _resolve_base(spec_path)
    section_text = '\n'.join(sub_body for _, sub_body in subsections)
    rows = [cells for cells in _table_rows(concept_body) if len(cells) >= 2]
    tbc_basenames: list[str] = [
        (_extract_path(cells[1]) or '').replace('\\', '/').rsplit('/', 1)[-1]
        for cells in rows
        if 'to be created' in cells[1].lower() and _extract_path(cells[1])
    ]
    violations: list[Violation] = []
    for cells in rows:
        module_cell = cells[1]
        if 'module' in module_cell.lower() and 'file' in module_cell.lower():
            continue
        path = _extract_path(module_cell)
        if not path:
            continue
        if 'to be created' in module_cell.lower():
            name = path.replace('\\', '/').rsplit('/', 1)[-1]
            claimed = path in section_text or (
                tbc_basenames.count(name) == 1
                and re.search(rf'(?<![\w./-]){re.escape(name)}', section_text) is not None
            )
            if not claimed:
                violations.append(
                    Violation(
                        'Concept → module map',
                        f'"to be created" path {path!r} is not claimed by any section '
                        '(name the path — or its basename, when unique — in the body of the '
                        'section that creates it).',
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


def _check_anchors(text: str, spec_path: Path) -> tuple[list[Violation], list[str]]:
    """Code-grounding: every `path:line` anchor resolves, and any quoted snippet matches."""
    base = _resolve_base(spec_path)
    violations: list[Violation] = []
    warnings: list[str] = []
    for match in _ANCHOR_RE.finditer(text):
        path, line_text, snippet = match.group(1), match.group(2), match.group(3)
        if not _anchor_shaped(path):
            continue  # a `host:port`, IP, or version literal — not a file anchor
        where = f'{path}:{line_text}'
        reason = _bad_anchor_platform(path)
        if reason is not None:
            violations.append(Violation(where, f'anchor path {path!r} is not portable ({reason}).'))
            continue
        line_no = int(line_text)
        lines, violation, resolve_warnings = _resolve_anchor(base, path, line_no, where)
        warnings += resolve_warnings
        if violation is not None:
            violations.append(violation)
            continue
        if snippet is not None and lines is not None:
            actual = ' '.join(lines[line_no - 1].split())
            if ' '.join(snippet.split()) not in actual:
                violations.append(
                    Violation(
                        where,
                        f'interpreted {snippet!r} (the backticked token after the anchor) as a '
                        f'snippet to match against line {line_no}; remove it or make it an exact '
                        'substring of that line.',
                    )
                )
    return violations, warnings


def _check_anchor_ranges(text: str, spec_path: Path) -> tuple[list[Violation], list[str]]:
    """A11: a `path:lo-hi` range anchor must close every bracket it opens (string/comment-aware).

    A range whose `hi` line leaves a bracket opened inside the range unclosed is a truncated
    citation (the observation window stops mid-literal). Verify-when-present: fires only on
    `path:lo-hi` range anchors; single-line `path:line` anchors (A6) are untouched. The
    bracket-balance is a Python-literal notion, so it runs only for `.py`/`.pyi` anchors — a range
    into a non-code file still has its file/line resolved, but is not balance-checked.
    """
    base = _resolve_base(spec_path)
    violations: list[Violation] = []
    warnings: list[str] = []
    for match in _ANCHOR_RANGE_RE.finditer(text):
        path, lo, hi = match.group(1), int(match.group(2)), int(match.group(3))
        if not _anchor_shaped(path):
            continue
        where = f'{path}:{lo}-{hi}'
        reason = _bad_anchor_platform(path)
        if reason is not None:
            violations.append(Violation(where, f'anchor path {path!r} is not portable ({reason}).'))
            continue
        lines, violation, resolve_warnings = _resolve_anchor(base, path, hi, where)
        warnings += resolve_warnings
        if violation is not None:
            violations.append(violation)
            continue
        if lo < 1 or lo > hi or lines is None:
            violations.append(Violation(where, f'anchor range {lo}-{hi} is malformed.'))
            continue
        if path.endswith(('.py', '.pyi')):
            net, ever_negative = _bracket_balance(lines[lo - 1 : hi])
            if net > 0 or ever_negative:
                violations.append(
                    Violation(
                        where,
                        f'anchor range :{lo}-{hi} does not close every bracket it opens (or closes '
                        'one opened before it) — quote the literal complete or not at all.',
                    )
                )
    return violations, warnings


_FOLD_NONE = frozenset({'', 'none', 'noneoutstanding', 'na', 'nil'})

# Anchor, optionally followed by a backticked snippet (0.12.0 §8): `path:line` `snippet`. The
# snippet makes in-range drift detectable — a bare line number survives an edit that moves content
# within range; the snippet does not.
_LEDGER_ANCHOR_RE = re.compile(r'`?([^`\s]*[./][^`\s]*):(\d+)`?(?:[ \t]+`([^`]+)`)?$')


def _ledger_anchor(cells: list[str]) -> re.Match[str] | None:
    """The first fold-ledger cell that IS an `artifact:line` confirmation, in any column.

    A12 read `cells[2]` positionally (KEEL-B03), so a ledger carrying a round, a severity or a
    disposition column failed on rows whose anchor was perfectly good and simply not third. A
    finding id (`FM-1`) or a target section (`§1`) cannot match — the token needs a `.`/`/` and a
    `:line` — so scanning left to right cannot pick up the wrong cell.
    """
    for cell in cells:
        match = _LEDGER_ANCHOR_RE.match(re.sub(r'\*', '', cell).strip())
        if match is not None:
            return match
    return None


def _fold_claimed(cert_body: str) -> bool:
    """R1 trigger: True if the certification's 'folded in' field names a non-trivial fold.

    Only the FIRST word is tested against the clean set, so an elaborated clean certify ("none found
    — the review surfaced nothing to fold") still dozes instead of demanding a ledger for a fold
    that never happened.
    """
    for line in cert_body.splitlines():
        if 'folded in' in line.lower():
            _, _, value = line.partition(':')
            # skip leading markdown junk (e.g. the bold-close `**`) to the first word with content
            normalized = (re.sub(r'[^a-z0-9]', '', w.lower()) for w in value.split())
            first = next((w for w in normalized if w), '')
            return first not in _FOLD_NONE
    return False


def _check_fold_ledger(cert_body: str | None, spec_path: Path) -> tuple[list[Violation], list[str]]:
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
        return [], []
    ledger = next(
        (sub for title, sub in _subsections(cert_body) if 'fold ledger' in title.lower()), None
    )
    table = _first_table_rows(ledger) if ledger else []
    header, rows = (table[0] if table else []), table[1:]
    if not rows:
        if _fold_claimed(cert_body):
            return [
                Violation(
                    'Fold ledger',
                    'the certification claims a fold but carries no `### Fold ledger` rows; '
                    'record one row (finding, target, artifact:line, confirmed) per finding (R1).',
                )
            ], []
        return [], []
    base = _resolve_base(spec_path)
    violations: list[Violation] = []
    warnings: list[str] = []
    for cells in rows:
        where = f'Fold ledger {cells[0].strip() if cells else "(row)"}'
        if len(cells) < 3:
            violations.append(
                Violation(
                    where,
                    'fold-ledger row is malformed — it needs finding, target, `artifact:line`, '
                    'and confirmed cells; a short row carries no resolving anchor (R1/A12).',
                )
            )
            continue
        # A row wider than its header is a column break, checked before the anchor search: with
        # the anchor read from any column (KEEL-B03) a split row can still carry a resolving
        # anchor, and the row would otherwise pass while its cells mean something else entirely.
        if header and len(cells) > len(header):
            violations.append(
                Violation(
                    where,
                    f'fold-ledger row split into {len(cells)} cells where the header has '
                    f'{len(header)} — a bare `|` inside a cell is a column break; backtick the '
                    'cell content or escape it as `\\|`.',
                )
            )
            continue
        match = _ledger_anchor(cells)
        if match is None:
            read = re.sub(r'\*', '', cells[2]).strip()
            violations.append(
                Violation(
                    where,
                    f'no cell in this fold-ledger row is an `artifact:line` confirmation — the '
                    f'confirmation column reads {read!r}. Anchor the row to `path:line`, e.g. '
                    '`docs/design/your-spec.md:142`; an optional backticked snippet after it is '
                    'verified against that line.',
                )
            )
            continue
        line_no = int(match.group(2))
        lines, violation, resolve_warnings = _resolve_anchor(base, match.group(1), line_no, where)
        warnings += resolve_warnings
        if violation is not None:
            violations.append(violation)
            continue
        snippet = match.group(3)
        if snippet is not None and lines is not None:
            actual = ' '.join(lines[line_no - 1].split())
            if ' '.join(snippet.split()) not in actual:
                violations.append(
                    Violation(
                        where,
                        f'fold-ledger snippet {snippet!r} does not match line {line_no} '
                        '(in-range drift: the anchored content moved — re-anchor the row).',
                    )
                )
    return violations, warnings


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
    # Column 0 only: the DoR contract is a *top-level* (importable) def/class/assignment, so a
    # function-local of the same name does not satisfy a `Reuse:` target.
    defs = (
        rf'^(?:async\s+)?def\s+{re.escape(name)}\b',
        rf'^class\s+{re.escape(name)}\b',
        rf'^{re.escape(name)}\s*[:=]',
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


def _check_section_refs(text: str, prose: str, section_ids: list[str]) -> list[Violation]:
    """A8: every bare intra-spec §N reference resolves to a numbered section.

    The `§` glyph is reserved for the spec's own sections; a `§N` that is part of a sub-decimal
    (`§4.5`), on a `###` heading line (a definition, not a reference), backticked (a `§9`-glyph
    mention, masked on the prose view), or preceded by a document/file cue (`doctrine §6`, or the
    trailing ref of a joined range like `ADR-0103 §3/§4`) is left alone. Detection runs on the prose
    view, so a backticked mention no longer fires; the cross-document cue lookback reads the raw
    line at the same offset (offsets are preserved), so a backticked `` `docs/doctrine.md` §6 `` cue
    still suppresses, and a trailing §-ref run is stripped first so a joined range keeps its cue.
    """
    known = set(section_ids)
    violations: list[Violation] = []
    in_references = False
    for lineno, (line, masked) in enumerate(
        zip(text.splitlines(), prose.splitlines(), strict=True), 1
    ):
        heading = re.match(r'^#{2,6}[ \t]+(.+?)[ \t]*$', line)
        if heading is not None:
            # A References section cites OTHER documents by their own section numbers; the glyph
            # there is never a claim about this spec's sections (KEEL-B03).
            in_references = 'reference' in heading.group(1).lower()
        if in_references:
            continue
        if line.lstrip().startswith('#'):  # a heading defines a section, it is not a ref
            continue
        for match in _SECTION_REF_RE.finditer(masked):
            before = _TRAILING_SECREFS_RE.sub('', line[: match.start()])
            # Punctuation-only tokens (an opening paren, a dash) are not cues and must not hide
            # the one behind them: `docs/doctrine.md` (§6) lost its document cue to the '('.
            toks = [
                stripped
                for token in re.findall(r'\S+', before)
                if (stripped := token.lower().strip(_CUE_STRIP))
            ]
            last = toks[-1] if toks else ''
            prev = toks[-2] if len(toks) >= 2 else ''
            # cross-document: a *.md file, a listed cue word, a standards id (ADR-0002, PEP8), or a
            # standards id split from its number ("RFC 9110 §15" → last='9110', prev='rfc').
            if (
                last.endswith('.md')
                or last in _DOC_CUES
                or _DOC_ID_CUE_RE.match(last) is not None
                or (
                    last.isdigit() and (prev in _DOC_CUES or _DOC_ID_CUE_RE.match(prev) is not None)
                )
            ):
                continue
            sid = f'§{match.group(1)}'
            if sid not in known:
                violations.append(
                    Violation(f'line {lineno}', f'reference {sid} resolves to no numbered section.')
                )
    return violations


def _check_enforcement_claims(sections: list[tuple[str, str]], text: str) -> list[Violation]:
    """A10: no prose claims an invariant 'enforced'/'guaranteed' that its status table denies.

    Keyed off the spec-template 'Enforcement status' table (the convention), not free-text parsing;
    checked only when that table is present. A claim word inside backticks does not fire (a quoted
    `enforced` is meta-discussion). The invariant key is matched with backtick spans kept as their
    inner text (so a backticked `key` still counts) across the wrapped neighbourhood (prev+this+next
    line), so a hard line-wrap between key and claim no longer hides an over-claim; a negation or
    deferral in the words just before the claim ("not", "never", "n't", "to be", "will be", "yet",
    "once") suppresses it.
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
    lines = text.splitlines()
    violations: list[Violation] = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith('|'):  # a status-table cell IS the status, not a prose claim
            continue
        bare = re.sub(r'`[^`]*`', '', line)  # a backticked claim word is not a claim
        claim = _CLAIM_RE.search(bare)
        if claim is None:
            continue
        # neighbourhood for the wrap fix, excluding table rows (their keys are the status source,
        # not prose to match a claim against).
        near = [ln for ln in lines[max(0, i - 1) : i + 2] if not ln.lstrip().startswith('|')]
        before = re.sub(r'`[^`]*`', '', ' '.join(lines[max(0, i - 1) : i + 1]))
        cut = before.rfind(claim.group(0))
        window_before = ' '.join(before[:cut].split()[-4:]).lower() if cut != -1 else ''
        if _NEG_RE.search(window_before):
            continue
        window = re.sub(r'`([^`]*)`', r'\1', ' '.join(near)).lower()
        for key, status in non_enforced.items():
            if key.lower() in window:
                violations.append(
                    Violation(
                        f'line {i + 1}',
                        f'claims {key!r} is "{claim.group(0)}" but its enforcement status '
                        f'is {status!r}.',
                    )
                )
    return violations


def _status_currency_warning(header: str, cert_body: str | None) -> list[str]:
    """§10 (0.12.0): a recorded certification while the header still says draft is a currency slip.

    WARN, not violation — the class recurred on release specs but it is a stale coordinate, not a
    forgery. Silent when the header carries no Status field at all (pre-template specs), when the
    Status has moved past draft, or when nothing is certified yet.
    """
    if cert_body is None:
        return []
    status = _field(header, 'status')
    if not status or status.split()[0].lower() != 'draft':
        return []
    if _verdict_head(_field(cert_body, 'verdict')) not in ('CERTIFIED', 'CONDITIONAL-CERTIFY'):
        return []
    return [
        "WARN: the header Status still says 'draft' though a certification is recorded — keep "
        'the coordinate system current (update the Status field).'
    ]


_VERDICT_TOKEN_RE = re.compile(r'\s*([A-Za-z][A-Za-z-]*)')


def _verdict_head(raw: str) -> str:
    """The leading verdict token of a Verdict value or verdict line, uppercased ('' if none).

    Leading-token semantics: hyphens are kept whole (`CONDITIONAL-CERTIFY` is one token) and
    trailing text — prose, §2's `pre-mortem-review@<version>` identity suffix — is inert.
    """
    match = _VERDICT_TOKEN_RE.match(raw)
    return match.group(1).upper() if match else ''


def _check_certification_artifact(
    cert_body: str, spec_path: Path
) -> tuple[list[Violation], list[str]]:
    """B2 (0.12.0, verify-when-present): the certification's named artifact exists and agrees.

    No artifact named (field absent, or present with an empty value — the template ships it
    empty, so a scaffolded field is absent, not broken): an adoption WARN, nothing more. An
    artifact named: it must exist and carry a line-anchored `PREMORTEM-VERDICT:` line whose LAST
    occurrence's leading token equals the recorded Verdict's (a column-0 schema quote above the
    real verdict is inert); its `Spec-hash:` — when recorded — is compared against the current
    canonical hash, and a mismatch WARNs ("certified against an earlier revision") rather than
    fails, because a post-certification edit is exactly what a mismatch looks like. B2 raises the
    forgery cost from one typed line to a consistent saved artifact; it does NOT prove a blind
    pass ran — that residual trust stays named (ADR-0002, ADR-0014).
    """
    ref = _first_path_token(_field(cert_body, 'certification artifact'))
    if not ref:
        return [], [
            'WARN: the certification names no artifact — B2 verifies one when present; save the '
            "pass's returned output per keel-premortem.md and reference it "
            '(`Certification artifact:`).'
        ]
    where = 'Certification artifact'
    target = _resolve_base(spec_path) / ref
    if not target.is_file():
        return [
            Violation(
                where,
                f'referenced artifact {ref!r} does not exist as a file — that is the leading path '
                'token of the field; the path is repo-root-relative, like an anchor, and any '
                'trailing prose (a round note, a prior-round path) is ignored.',
            )
        ], []
    artifact_text = target.read_text(encoding='utf-8', errors='replace')
    anchored = [
        line
        for line in artifact_text.splitlines()
        if line.lstrip().startswith('PREMORTEM-VERDICT:')
    ]
    if not anchored:
        return [
            Violation(
                where,
                f'artifact {ref!r} carries no line-anchored `PREMORTEM-VERDICT:` line — it does '
                "not look like a saved pre-mortem pass's output.",
            )
        ], []
    artifact_head = _verdict_head(anchored[-1].split(':', 1)[1])
    cert_head = _verdict_head(_field(cert_body, 'verdict'))
    violations: list[Violation] = []
    warnings: list[str] = []
    if artifact_head != cert_head:
        violations.append(
            Violation(
                where,
                f'artifact verdict token {artifact_head!r} disagrees with the recorded Verdict '
                f'{cert_head!r} — the saved pass is the record; re-run or re-record.',
            )
        )
    recorded_hash = _field(artifact_text, 'spec-hash')
    if recorded_hash:
        first = recorded_hash.split()[0].strip('`').lower() if recorded_hash.split() else ''
        if first != spec_hash(spec_path):
            warning = (
                'WARN: the artifact was certified against an earlier revision of this spec '
                '(Spec-hash mismatch) — re-run the pass on the current spec, or accept knowingly '
                '(B2).'
            )
            # On an operator close (an operator-accepted CONDITIONAL-CERTIFY), a condition
            # discharged after the pass moves the hash by design, so this mismatch is expected —
            # name it, but only there (a blanket clause would bless arbitrary post-cert edits).
            if cert_head == 'CONDITIONAL-CERTIFY' and _field(cert_body, 'operator'):
                warning += (
                    ' On an operator-accepted CONDITIONAL-CERTIFY this mismatch is the expected '
                    'state — a condition discharged after the pass (the operator close, '
                    'definition-of-ready.md Part B).'
                )
            warnings.append(warning)
    return violations, warnings


def _check_premortem(cert_body: str | None) -> tuple[list[Violation], list[str]]:
    """B1: a blind pre-mortem certification (a verdict + a reviewer) is recorded.

    The verdict's leading token must be CERTIFIED, or CONDITIONAL-CERTIFY paired with a named
    Operator — the operator-accepted "ready modulo a named fix" state the prompt already emits. The
    conditional verdict passes with a non-blocking WARN rather than EXIT 1, so a consciously
    accepted spec is not blocked forever; it stays a *form* check (a verdict and an owner were
    RECORDED, not that the spec is correct — ADR-0002). Returns (violations, warnings).
    """
    if cert_body is None:
        return [
            Violation(
                'Pre-mortem certification',
                'no "## Pre-mortem certification" block; a non-author pre-mortem '
                'must certify the spec (ADR-0002).',
            )
        ], []
    violations: list[Violation] = []
    warnings: list[str] = []
    verdict_lines = [
        ln
        for ln in cert_body.splitlines()
        if re.match(r'^[\-*\s]*verdict[\s*]*:', ln, re.IGNORECASE)
    ]
    if len(verdict_lines) > 1:
        violations.append(
            Violation(
                'Pre-mortem certification',
                f'certification records {len(verdict_lines)} Verdict lines; an appended or '
                'retracted verdict is ambiguous — keep exactly one (edit in place, do not append).',
            )
        )
    raw = _field(cert_body, 'verdict')
    head = _verdict_head(raw)  # the bare verdict token, hyphens kept whole
    if head == 'CERTIFIED':
        pass
    elif head == 'CONDITIONAL-CERTIFY':
        operator = _field(cert_body, 'operator')
        if operator:
            warnings.append(
                f'WARN: pre-mortem verdict is CONDITIONAL-CERTIFY, operator-accepted by '
                f'{operator!r} (ready modulo a named fix) — not a clean CERTIFIED (B1).'
            )
        else:
            violations.append(
                Violation(
                    'Pre-mortem certification',
                    'pre-mortem verdict is CONDITIONAL-CERTIFY but names no Operator; an '
                    'operator-accepted conditional certify must record an "Operator:" field (the '
                    'named owner who accepts "ready modulo a named fix").',
                )
            )
    else:
        verdict = raw or '(none)'
        violations.append(
            Violation(
                'Pre-mortem certification',
                f'pre-mortem verdict is {verdict!r}, not "CERTIFIED" — the verdict field must '
                'lead with the bare token CERTIFIED (trailing prose allowed), or '
                'CONDITIONAL-CERTIFY with a named Operator.',
            )
        )
    if not _field(cert_body, 'reviewer'):
        violations.append(
            Violation(
                'Pre-mortem certification',
                'pre-mortem certification names no reviewer (must be a non-author).',
            )
        )
    return violations, warnings
