"""0.11.0 regressions: the enforcement-gap release (six-lens skeptic-panel findings).

Each test pins one fix that closes the gap between what the DoR gate DOCUMENTS and what it
ENFORCED before 0.11.0 — a fenced example forging the verdict, a half-implemented bijection, an
over-matching anchor regex, and the rest. Cluster/finding ids in comments trace to
docs/feedback/2026-07-01-skeptic-panel-fable5.md.
"""

import pytest

from keel.check_ready import check_spec_ready
from tests.test_check_ready import _ENFORCE_TABLE, READY_SPEC, _ledger, _write


def test_fenced_certification_cannot_forge_verdict_b1(tmp_path):
    # C2/G1: a fenced example `Verdict: CERTIFIED` must not shadow a real REJECTED verdict.
    forged = READY_SPEC.replace(
        '- **Verdict:** CERTIFIED', '- **Verdict:** REJECTED - two blocking findings stand'
    ).replace(
        '## Numbered sections',
        '## Example\n\n```markdown\n## Pre-mortem certification\n'
        '- **Reviewer:** ghost\n- **Verdict:** CERTIFIED\n```\n\n## Numbered sections',
    )
    result = check_spec_ready(_write(tmp_path, forged))
    assert not result.passed
    assert any('CERTIFIED' in v.message for v in result.violations)


def test_fenced_todo_is_ignored_a3(tmp_path):
    # C2/G1: a `# TODO` quoted inside a fence is illustrative, not a live placeholder.
    good = READY_SPEC + '\n## Notes\n\n```python\n# TODO: delete the shim before merge\n```\n'
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_fenced_heading_does_not_break_numbering_a1(tmp_path):
    # C2/G1: a fenced `### heading` inside a section body is not parsed as an unnumbered section.
    good = READY_SPEC.replace(
        'and a unit test asserts it returns a Widget instance.',
        'and a unit test asserts it returns a Widget instance.\n\n```\n### Not a real section\n```',
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_pr_citing_two_sections_fails_a4(tmp_path):
    # C3/G3: one PR row citing two sections is the scope-bundling the bijection forbids.
    bad = READY_SPEC.replace('| PR01 | §1 | yes |\n| PR02 | §2 | yes |', '| PR01 | §1, §2 | yes |')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('exactly one section' in v.message for v in result.violations)


def test_section_token_in_comment_column_ignored_a4(tmp_path):
    # C4/G13: a §N inside a comment cell must not break the bijection count.
    good = READY_SPEC.replace('| PR01 | §1 | yes |', '| PR01 | §1 | yes (sets up for §2) |')
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_two_cell_ledger_row_fails_a12(tmp_path):
    # C3/G4: a <3-cell ledger row carries no resolving anchor and must fail (not silently skip).
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('a\nb\n', encoding='utf-8')
    bad = READY_SPEC.replace(
        '- **Failure modes considered & folded in:** none outstanding',
        '- **Failure modes considered & folded in:** 1 finding folded.',
    ) + _ledger('| FM-1 | §1 |\n')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('malformed' in v.message.lower() for v in result.violations)


def test_host_port_and_url_are_not_anchors_a6(tmp_path):
    # C4/G6/CS-5: a backticked host:port or URL is ordinary prose, not a path:line anchor.
    good = READY_SPEC.replace(
        'Introduce `src/widget.py`.',
        'Introduce `src/widget.py`. It binds `127.0.0.1:8080` and `http://localhost:9000`.',
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_adjacent_anchors_both_checked_a6(tmp_path):
    # C4/CODE-01: two adjacent valid anchors both resolve; neither becomes the other's snippet.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'a.py').write_text('x\n', encoding='utf-8')
    (tmp_path / 'b.py').write_text('y\n', encoding='utf-8')
    good = READY_SPEC.replace('Introduce `src/widget.py`.', 'Compare `a.py:1` `b.py:1`.')
    assert check_spec_ready(_write(tmp_path, good)).passed
    bad = READY_SPEC.replace('Introduce `src/widget.py`.', 'Compare `a.py:1` `b.py:99`.')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('b.py' in v.where for v in result.violations)


def test_bare_extensionless_anchor_recognized_a6(tmp_path):
    # C3/G5: a known extension-less filename (Makefile) is a real anchor, verified not ignored.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'Makefile').write_text('all:\n\techo hi\n', encoding='utf-8')
    bad = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`, see `Makefile:99`.'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('Makefile' in v.where for v in result.violations)


def test_backslash_anchor_rejected_a6(tmp_path):
    # C9/G10/CODE-12: a backslash anchor resolves on Windows only - reject as non-portable.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'sub').mkdir()
    (tmp_path / 'sub' / 'x.py').write_text('a\nb\n', encoding='utf-8')
    bad = READY_SPEC.replace('Introduce `src/widget.py`.', 'Introduce `sub\\x.py:2`.')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('portable' in v.message for v in result.violations)


def test_absolute_anchor_rejected_a6(tmp_path):
    # C9: a POSIX-absolute anchor is machine-local - reject it.
    bad = READY_SPEC.replace('Introduce `src/widget.py`.', 'Introduce `/etc/hosts:1`.')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('portable' in v.message for v in result.violations)


def test_angle_placeholder_fails_a3(tmp_path):
    # C3/CS-2: a leftover `<title>` template placeholder outside code fails A3.
    bad = READY_SPEC.replace('### §1 Add the widget module', '### §1 <title>')
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('placeholder' in v.message.lower() for v in result.violations)


def test_backticked_angle_is_not_a_placeholder_a3(tmp_path):
    # C3/CS-2: documented CLI syntax `keel init <target>` in backticks is legal.
    good = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py` via `keel init <target>`.'
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_empty_criterion_with_trailing_prose_fails_a2(tmp_path):
    # C3/G8: an empty acceptance criterion followed by unrelated prose no longer launders A2.
    bad = READY_SPEC.replace(
        '**Acceptance criterion:** `src/widget.py` exposes `make()`\n'
        'and a unit test asserts it returns a Widget instance.',
        '**Acceptance criterion:**\n\nSome unrelated design notes about the layout follow here.',
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('criterion' in v.message.lower() for v in result.violations)


def test_wrapped_overclaim_fires_a10(tmp_path):
    # C3/G7: a hard-wrapped over-claim (key and 'enforced' on different lines) still fires.
    bad = READY_SPEC + _ENFORCE_TABLE + '\nThe boundary-rule is fully\nenforced by construction.\n'
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('boundary-rule' in v.message for v in result.violations)


def test_backticked_key_overclaim_fires_a10(tmp_path):
    # C3/CODE-04: a backticked invariant name in the over-claim is still matched.
    bad = READY_SPEC + _ENFORCE_TABLE + '\nThe `boundary-rule` is enforced at every commit.\n'
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('boundary-rule' in v.message for v in result.violations)


def test_reuse_function_local_symbol_fails_a9(tmp_path):
    # C3/G16: a function-local of the reuse name is not an importable top-level symbol.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text(
        'def outer():\n    helper = 1\n    return helper\n', encoding='utf-8'
    )
    bad = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`. **Reuse:** `mod.py::helper`'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('helper' in v.message for v in result.violations)


def test_range_tail_truncation_fails_a11(tmp_path):
    # C3/G15: a range citing the TAIL of a literal (closes a brace opened above) is truncated too.
    (tmp_path / '.git').mkdir()
    (tmp_path / 'mod.py').write_text('CONFIG = {\n    "a": 1,\n    "b": 2,\n}\n', encoding='utf-8')
    bad = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Introduce `src/widget.py`, see `mod.py:3-4`.'
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('mod.py:3-4' in v.where for v in result.violations)


def test_two_verdict_lines_fail_b1(tmp_path):
    # C3/G9: an appended (retracted) verdict is ambiguous - exactly one Verdict line is allowed.
    bad = READY_SPEC.replace(
        '- **Verdict:** CERTIFIED',
        '- **Verdict:** CERTIFIED\n- **Verdict:** RETRACTED 2026-07-02 - defect found post-cert',
    )
    result = check_spec_ready(_write(tmp_path, bad))
    assert not result.passed
    assert any('Verdict lines' in v.message for v in result.violations)


def test_none_found_prose_dozes_r1(tmp_path):
    # C4/G11: an elaborated clean certify ("none found - ...") is not a claimed fold.
    good = READY_SPEC.replace(
        '- **Failure modes considered & folded in:** none outstanding',
        '- **Failure modes considered & folded in:** none found - the review surfaced nothing',
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_doc_id_section_refs_pass_a8(tmp_path):
    # C4/ARCH-6/G14: 'ADR-0002 §4' and 'RFC 9110 §15' are cross-document, not dangling intra-refs.
    good = READY_SPEC.replace(
        'Introduce `src/widget.py`.', 'Per ADR-0002 §4 and RFC 9110 §15, introduce `src/widget.py`.'
    )
    result = check_spec_ready(_write(tmp_path, good))
    assert result.passed, [v.message for v in result.violations]


def test_directory_spec_raises_not_runnable(tmp_path):
    # C5/G2: a directory argument is not runnable (exit 2), not a crash or a false 'violations'.
    with pytest.raises(FileNotFoundError):
        check_spec_ready(tmp_path)


def test_non_utf8_spec_raises_not_runnable(tmp_path):
    # C5/CODE-03: an undecodable spec is not runnable (exit 2), not a raw UnicodeDecodeError.
    spec = tmp_path / 'spec.md'
    spec.write_bytes(b'\xff\xfe\x00\x01 not utf-8 text')
    with pytest.raises(FileNotFoundError):
        check_spec_ready(spec)
