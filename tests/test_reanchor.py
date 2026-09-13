"""`keel re-anchor`: the correction the gate already computes, applied instead of described.

The load-bearing property is not that it rewrites — it is WHAT it refuses. A repair that guesses
is worse than the manual `sed` it replaces, because the row then passes the gate while pointing
somewhere the fold never happened. Every refusal below is a case where the correction would be a
guess, and each is reported by name rather than silently skipped.
"""

import subprocess

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


# --- E1b: repair by content, for the shape the template actually emits -------
#
# The snippet strategy cannot touch a row the template produces: its ledger block calls the
# backticked snippet optional, so two programmes hit a drifted ledger with no snippet to repair
# from and wrote the same throwaway difflib script (8 of 35 rows wrong, then 90 of 125). The
# content the row cited is recoverable from the tree it was written against, which is what a git
# ref is; `--by-content <ref>` reads the line it cited THEN and finds where that line sits now.


def _git(tmp_path, *args):
    return subprocess.run(
        ['git', '-C', str(tmp_path), *args],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        check=True,
    )


def _committed_spec(tmp_path, rows, module=MODULE):
    """A real one-commit repo: the spec and its module as the ledger was written against them."""
    (tmp_path / 'mod.py').write_text(module, encoding='utf-8')
    spec = tmp_path / 'spec.md'
    spec.write_text(SPEC_HEAD + rows, encoding='utf-8')
    _git(tmp_path, 'init', '-q')
    _git(tmp_path, 'add', '-A')
    _git(
        tmp_path,
        '-c',
        'user.email=t@example.invalid',
        '-c',
        'user.name=test',
        'commit',
        '-qm',
        'the tree the ledger was anchored against',
    )
    return spec


SNIPPETLESS = '| FM-1 | §1 | mod.py:6 | yes |\n'


def test_by_content_repoints_a_snippetless_unbackticked_row(tmp_path):
    spec = _committed_spec(tmp_path, SNIPPETLESS)
    (tmp_path / 'mod.py').write_text('# two\n# new\n' + MODULE, encoding='utf-8')
    report = reanchor(spec, by_content='HEAD')
    assert [(r.anchor, r.corrected) for r in report.applied] == [('mod.py:6', 'mod.py:8')]
    assert '| mod.py:8 |' in spec.read_text(encoding='utf-8')


def test_by_content_repoints_a_row_anchored_into_the_spec_itself(tmp_path):
    # The measured case: a self-anchored ledger, and a later fold that inserts above it.
    rows = '| FM-1 | §1 | spec.md:7 | yes |\n'
    spec = _committed_spec(tmp_path, rows)
    spec.write_text(
        spec.read_text(encoding='utf-8').replace('# Spec', '<!-- a fold -->\n# Spec'),
        encoding='utf-8',
    )
    report = reanchor(spec, by_content='HEAD')
    assert [(r.anchor, r.corrected) for r in report.applied] == [('spec.md:7', 'spec.md:8')]


def test_by_content_repairs_a_range_row(tmp_path):
    # The one repair the snippet strategy refuses outright: both ends move by content.
    spec = _committed_spec(tmp_path, '| FM-1 | §1 | `mod.py:6-8` | yes |\n')
    (tmp_path / 'mod.py').write_text('# one\n' + MODULE, encoding='utf-8')
    report = reanchor(spec, by_content='HEAD')
    assert [(r.anchor, r.corrected) for r in report.applied] == [('mod.py:6-8', 'mod.py:7-9')]


def test_by_content_refuses_a_line_that_no_longer_exists(tmp_path):
    spec = _committed_spec(tmp_path, SNIPPETLESS)
    (tmp_path / 'mod.py').write_text(
        MODULE.replace('def load_orders(rows):', 'def load_every_order(rows):'), encoding='utf-8'
    )
    before = spec.read_text(encoding='utf-8')
    report = reanchor(spec, by_content='HEAD')
    assert not report.applied
    assert report.refused and 'changed or removed' in report.refused[0].refused
    assert spec.read_text(encoding='utf-8') == before


def test_by_content_refuses_a_ref_that_does_not_carry_the_file(tmp_path):
    spec = _committed_spec(tmp_path, '| FM-1 | §1 | later.py:2 | yes |\n')
    (tmp_path / 'later.py').write_text('one\ntwo\n', encoding='utf-8')
    report = reanchor(spec, by_content='HEAD')
    assert not report.applied
    assert report.refused and 'HEAD' in report.refused[0].refused


def test_by_content_refuses_a_snippet_the_move_would_falsify(tmp_path):
    # A row whose snippet and coordinate already disagreed: remapping the coordinate would carry
    # the disagreement forward under a repaired-looking row. Refused by name instead.
    rows = '| FM-1 | §1 | `mod.py:6` `import re` | yes |\n'
    spec = _committed_spec(tmp_path, rows)
    (tmp_path / 'mod.py').write_text('# one\n' + MODULE, encoding='utf-8')
    report = reanchor(spec, by_content='HEAD')
    assert not report.applied
    assert report.refused and 'snippet' in report.refused[0].refused


def test_by_content_check_mode_writes_nothing(tmp_path):
    spec = _committed_spec(tmp_path, SNIPPETLESS)
    (tmp_path / 'mod.py').write_text('# one\n' + MODULE, encoding='utf-8')
    before = spec.read_text(encoding='utf-8')
    report = reanchor(spec, by_content='HEAD', write=False)
    assert report.applied
    assert spec.read_text(encoding='utf-8') == before


def test_by_content_leaves_the_certified_hash_unmoved(tmp_path):
    spec = _committed_spec(tmp_path, SNIPPETLESS)
    (tmp_path / 'mod.py').write_text('# one\n' + MODULE, encoding='utf-8')
    before = spec_hash(spec)
    reanchor(spec, by_content='HEAD')
    assert spec_hash(spec) == before


def test_by_content_clears_the_a12_failure_it_answers(tmp_path):
    # The end-to-end claim: a drifted snippetless ledger fails the gate, and one pass repairs it.
    spec = _committed_spec(tmp_path, SNIPPETLESS)
    (tmp_path / 'mod.py').write_text('# one\n' + MODULE, encoding='utf-8')
    reanchor(spec, by_content='HEAD')
    result = check_spec_ready(spec)
    assert not [v for v in result.violations if v.check == 'A12'], [
        v.message for v in result.violations
    ]


def test_cli_by_content_reports_each_repair(tmp_path):
    spec = _committed_spec(tmp_path, SNIPPETLESS)
    (tmp_path / 'mod.py').write_text('# one\n' + MODULE, encoding='utf-8')
    result = runner.invoke(app, ['re-anchor', str(spec), '--by-content', 'HEAD', '--check'])
    assert result.exit_code == 0
    assert 'would repoint mod.py:6 -> mod.py:7' in result.output


def test_cli_by_content_on_an_unknown_ref_says_so(tmp_path):
    spec = _committed_spec(tmp_path, SNIPPETLESS)
    result = runner.invoke(app, ['re-anchor', str(spec), '--by-content', 'no-such-ref'])
    assert result.exit_code == 0
    assert 'no-such-ref' in result.output
