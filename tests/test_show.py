"""`keel show`: the kit's own bodies, projected from the shipped files.

The property that matters is not that `show` prints something — it is that what it prints is READ
from the shipped file rather than restated in code. A copy would drift, and a drifted copy of the
directive or the check reference is worse than no command at all: it would answer "what does the
method already say?" with something the method no longer says.
"""

import pytest
from typer.testing import CliRunner

from keel.cli import app
from keel.models import CHECK_IDS
from keel.show import available, body
from keel.templates import list_templates, templates_root

runner = CliRunner()


def test_every_kit_template_is_servable():
    names = available()
    for template in list_templates():
        assert template.stem in names, template.name


def test_checks_is_read_from_the_sheet_not_restated():
    # The one-home property, asserted rather than trusted: byte-for-byte the sheet's fenced block.
    sheet = (templates_root() / 'definition-of-ready.md').read_text(encoding='utf-8')
    assert body('checks') == sheet.split('```')[1].strip('\n')


def test_the_check_projection_covers_the_catalogue():
    # `show checks` is the answer to "what does the gate accept?", so it has to be complete. The
    # reference block is already asserted to name every catalogued check; this pins that the
    # PROJECTION inherits that property rather than slicing part of it away.
    printed = body('checks')
    missing = [check for check in CHECK_IDS if f'\n{check} ' not in f'\n{printed}']
    assert not missing, missing


def test_directive_is_the_dispatched_block_not_the_whole_file():
    text = (templates_root() / 'pre-mortem-prompt.md').read_text(encoding='utf-8')
    assert body('directive') == text.split('## Prompt', 1)[1].split('```')[1].strip('\n')
    assert 'Output handling' not in body('directive')


def test_a_template_is_served_whole():
    assert body('reflection-triage').startswith('# Reflection triage')


def test_an_unknown_name_names_the_ones_that_exist():
    with pytest.raises(LookupError) as exc:
        body('doctrine')
    assert 'keel show --list' in str(exc.value)
    assert 'spec-template' in str(exc.value)


def test_doctrine_is_not_servable_because_it_is_not_packaged():
    # It lives in docs/, which no wheel built from this tree carries; serving it would require
    # copying it into the package, which is the duplication this command exists to avoid.
    assert 'doctrine' not in available()


def test_cli_list_prints_every_name():
    result = runner.invoke(app, ['show', '--list'])
    assert result.exit_code == 0
    for name in available():
        assert name in result.output


def test_cli_bare_show_lists_rather_than_failing():
    assert runner.invoke(app, ['show']).exit_code == 0


def test_cli_unknown_name_exits_two():
    result = runner.invoke(app, ['show', 'nope'])
    assert result.exit_code == 2
    assert 'not a body this kit serves' in result.output
