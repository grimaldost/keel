"""`keel re-anchor`: the correction the gate already computes, applied instead of described.

The load-bearing property is not that it rewrites — it is WHAT it refuses. A repair that guesses
is worse than the manual `sed` it replaces, because the row then passes the gate while pointing
somewhere the fold never happened. Every refusal below is a case where the correction would be a
guess, and each is reported by name rather than silently skipped.
"""

from typer.testing import CliRunner

from keel.check_ready import check_spec_ready, spec_hash
from keel.cli import app
from keel.reanchor import reanchor

runner = CliRunner()

MODULE = '\n'.join(
    [
        '"""A tiny module."""',
        '',
        'import re',
        '',
        '',
        'def load_orders(rows):',
        '    """Keep the rows that carry every column."""',
        '    return [row for row in rows if row]',
        '',
        '',
        'def rollup(orders):',
        '    """Total per key."""',
        '    return len(orders)',
        '',
    ]
)

SPEC_HEAD = """# Spec — widget

- **Status:** ready (DoR passed)

## Numbered sections

### §1 Add the widget
Introduce the widget. **Acceptance criterion:** the widget exists and a unit test
asserts it returns a Widget instance.

## Pre-mortem certification

- **Reviewer:** review-panel (non-author)
- **Verdict:** CERTIFIED
- **Date:** 2026-08-28
- **Failure modes considered & folded in:** one

### Fold ledger

| Finding | Target | Confirmed at | Applied? |
|---|---|---|---|
"""


def _spec(tmp_path, rows, body_extra=''):
    (tmp_path / '.git').mkdir(exist_ok=True)
    (tmp_path / 'mod.py').write_text(MODULE, encoding='utf-8')
    spec = tmp_path / 'spec.md'
    head = SPEC_HEAD.replace('Introduce the widget.', f'Introduce the widget.{body_extra}')
    spec.write_text(head + rows, encoding='utf-8')
    return spec


DRIFTED = '| FM-1 | §1 | `mod.py:3` `def load_orders(rows):` | yes |\n'


def test_a_drifted_row_is_repointed(tmp_path):
    spec = _spec(tmp_path, DRIFTED)
    report = reanchor(spec)
    assert [(r.anchor, r.corrected) for r in report.applied] == [('mod.py:3', 'mod.py:6')]
    assert '`mod.py:6`' in spec.read_text(encoding='utf-8')


def test_the_repair_leaves_the_certified_hash_unmoved(tmp_path):
    # The whole reason the ledger is the default scope: it sits inside the span `spec_hash`
    # removes, so repairing it cannot invalidate the certification it serves.
    spec = _spec(tmp_path, DRIFTED)
    before = spec_hash(spec)
    reanchor(spec)
    assert spec_hash(spec) == before


def test_the_repair_is_idempotent(tmp_path):
    spec = _spec(tmp_path, DRIFTED)
    reanchor(spec)
    after_first = spec.read_text(encoding='utf-8')
    second = reanchor(spec)
    assert not second.applied
    assert spec.read_text(encoding='utf-8') == after_first


def test_the_repair_clears_the_warning_it_answers(tmp_path):
    spec = _spec(tmp_path, DRIFTED)
    assert any(w.check == 'W6' for w in check_spec_ready(spec).warnings)
    reanchor(spec)
    assert not any(w.check == 'W6' for w in check_spec_ready(spec).warnings)


def test_a_weak_snippet_is_refused_by_name(tmp_path):
    spec = _spec(tmp_path, '| FM-1 | §1 | `mod.py:1` `import re` | yes |\n')
    report = reanchor(spec)
    assert not report.applied
    assert report.refused and 'too short' in report.refused[0].refused


def test_a_snippet_on_no_line_is_refused_by_name(tmp_path):
    spec = _spec(tmp_path, '| FM-1 | §1 | `mod.py:3` `def nothing_like_this(rows):` | yes |\n')
    report = reanchor(spec)
    assert not report.applied
    assert report.refused and 'on no line' in report.refused[0].refused


def test_a_range_row_is_never_touched(tmp_path):
    # A range's snippet could have sat anywhere inside the window, so the shift is
    # underdetermined; the gate keeps failing it and this pass leaves it alone.
    rows = '| FM-1 | §1 | `mod.py:1-4` `def load_orders(rows):` | yes |\n'
    spec = _spec(tmp_path, rows)
    before = spec.read_text(encoding='utf-8')
    report = reanchor(spec)
    assert not report.applied
    assert spec.read_text(encoding='utf-8') == before


def test_body_anchors_are_left_alone_by_default(tmp_path):
    extra = ' See `mod.py:3` `def load_orders(rows):`.'
    spec = _spec(tmp_path, DRIFTED, body_extra=extra)
    before_hash = spec_hash(spec)
    report = reanchor(spec)
    assert [r.corrected for r in report.applied] == ['mod.py:6']
    assert 'See `mod.py:3`' in spec.read_text(encoding='utf-8')
    assert spec_hash(spec) == before_hash


def test_body_flag_repoints_the_body_and_moves_the_hash(tmp_path):
    extra = ' See `mod.py:3` `def load_orders(rows):`.'
    spec = _spec(tmp_path, DRIFTED, body_extra=extra)
    before_hash = spec_hash(spec)
    reanchor(spec, body=True)
    assert 'See `mod.py:6`' in spec.read_text(encoding='utf-8')
    assert spec_hash(spec) != before_hash


def test_check_mode_writes_nothing(tmp_path):
    spec = _spec(tmp_path, DRIFTED)
    before = spec.read_text(encoding='utf-8')
    report = reanchor(spec, write=False)
    assert report.applied
    assert spec.read_text(encoding='utf-8') == before


def test_cli_reports_each_repair_and_each_refusal(tmp_path):
    rows = DRIFTED + '| FM-2 | §1 | `mod.py:1` `import re` | yes |\n'
    spec = _spec(tmp_path, rows)
    result = runner.invoke(app, ['re-anchor', str(spec), '--check'])
    assert result.exit_code == 0
    assert 'would repoint mod.py:3 -> mod.py:6' in result.output
    assert 'left mod.py:1 alone' in result.output


def test_cli_says_so_when_there_is_nothing_to_do(tmp_path):
    spec = _spec(tmp_path, '| FM-1 | §1 | `mod.py:6` `def load_orders(rows):` | yes |\n')
    result = runner.invoke(app, ['re-anchor', str(spec)])
    assert result.exit_code == 0
    assert 'nothing to repoint' in result.output


def test_cli_body_flag_warns_that_the_hash_moved(tmp_path):
    extra = ' See `mod.py:3` `def load_orders(rows):`.'
    spec = _spec(tmp_path, DRIFTED, body_extra=extra)
    result = runner.invoke(app, ['re-anchor', str(spec), '--body'])
    assert 'spec-hash` has moved' in result.output


def test_cli_missing_spec_exits_two(tmp_path):
    assert runner.invoke(app, ['re-anchor', str(tmp_path / 'nope.md')]).exit_code == 2
