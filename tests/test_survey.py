"""`keel survey`: which spec-shaped documents in a design directory carry no certification?

The field failure: a phase with a clear blast radius was specified in four hand-written documents
with no Definition-of-Ready and no pre-mortem, and nothing accused — doctrine's invocation trigger
exists only as prose to be remembered, at the moment memory is worst.

The load-bearing property is the PREDICATE. A design directory also holds triage documents, ADR
drafts, saved pre-mortem artifacts and requirements registers, none of which want a certification;
without a stated predicate the sweep either false-fails on all of them or becomes advisory prose.
"""

from typer.testing import CliRunner

from keel.cli import app
from keel.survey import survey

runner = CliRunner()

SPEC = """# Spec — widget

## Numbered sections

### §1 Add it
Introduce it. **Acceptance criterion:** it exists and a test asserts it.
"""

CERTIFIED = (
    SPEC
    + """
## Pre-mortem certification

- **Reviewer:** a non-author
- **Verdict:** CERTIFIED
"""
)

NOT_A_SPEC = """# Triage — the field backlog

Clusters by underlying cause. No numbered sections, no manifest, no certification wanted.
"""

REGISTER = """# Requirements register — a programme

### RR-01 — an order

- **Order (verbatim):** "do the thing"
"""


def _dir(tmp_path, **files):
    for name, text in files.items():
        (tmp_path / f'{name}.md').write_text(text, encoding='utf-8')
    return tmp_path


def test_a_certified_spec_is_reported_with_its_verdict(tmp_path):
    rows = survey(_dir(tmp_path, spec=CERTIFIED))
    assert [(r.path.name, r.spec_shaped, r.verdict) for r in rows] == [
        ('spec.md', True, 'CERTIFIED')
    ]


def test_an_uncertified_spec_is_the_finding(tmp_path):
    rows = survey(_dir(tmp_path, spec=SPEC))
    assert rows[0].spec_shaped and not rows[0].certified


def test_non_specs_are_listed_and_never_counted(tmp_path):
    rows = survey(_dir(tmp_path, triage=NOT_A_SPEC, orders=REGISTER, spec=CERTIFIED))
    shaped = {r.path.name for r in rows if r.spec_shaped}
    assert shaped == {'spec.md'}
    assert {r.path.name for r in rows} == {'triage.md', 'orders.md', 'spec.md'}


def test_a_manifest_alone_is_spec_shaped(tmp_path):
    manifest = '# Spec\n\n## PR ↔ section manifest\n\n| PR | Implements section |\n|---|---|\n'
    rows = survey(_dir(tmp_path, only_manifest=manifest))
    assert rows[0].spec_shaped


def test_a_certification_heading_without_a_verdict_is_not_certified(tmp_path):
    pending = SPEC + '\n## Pre-mortem certification\n\n- **Verdict:** not yet certified\n'
    rows = survey(_dir(tmp_path, spec=pending))
    assert rows[0].spec_shaped and not rows[0].certified


def test_cli_exits_one_only_when_a_spec_is_uncertified(tmp_path):
    _dir(tmp_path, triage=NOT_A_SPEC, spec=CERTIFIED)
    assert runner.invoke(app, ['survey', str(tmp_path)]).exit_code == 0
    (tmp_path / 'draft.md').write_text(SPEC, encoding='utf-8')
    result = runner.invoke(app, ['survey', str(tmp_path)])
    assert result.exit_code == 1
    assert 'draft.md: SPEC, no certification recorded' in result.output
    assert 'triage.md: not a spec' in result.output
    assert '1 without a recorded certification' in result.output


def test_cli_on_a_file_is_not_runnable(tmp_path):
    spec = tmp_path / 'spec.md'
    spec.write_text(SPEC, encoding='utf-8')
    result = runner.invoke(app, ['survey', str(spec)])
    assert result.exit_code == 2
    assert 'check-ready' in result.output


def test_an_empty_directory_passes(tmp_path):
    assert runner.invoke(app, ['survey', str(tmp_path)]).exit_code == 0
