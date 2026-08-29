"""Claim-currency guard: the comparative headline stays retired (0.13.0 §12, ADR-0015).

A promoted decision ships with a regression test (CONTRIBUTING gate-health rule 1). ADR-0015
retired the comparative claim at ADR-0013's run-or-retire deadline; this pins that the public
docs do not quietly resurrect the "pending experiment" IOU without reopening the claim by ADR.
"""

from pathlib import Path

from keel.cli import STUB_COMMANDS, app

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def test_pending_experiment_iou_is_gone():
    for rel in ('docs/doctrine.md', 'docs/concepts.md'):
        assert 'still pending' not in _read(rel), f'{rel} still carries the pending-experiment IOU'


def test_claim_is_stated_retired():
    assert 'retired' in _read('docs/evidence.md')
    assert 'retired' in _read('docs/doctrine.md')


def test_adr_0015_is_cited_where_the_claim_lives():
    for rel in ('docs/doctrine.md', 'docs/concepts.md', 'docs/evidence.md'):
        assert 'ADR-0015' in _read(rel), f'{rel} does not cite ADR-0015'
    assert (ROOT / 'docs' / 'adr' / '0015-retiring-the-comparative-claim.md').exists()


def test_readme_points_at_evidence():
    assert 'evidence.md' in _read('README.md'), 'README wager line has no evidence.md pointer'


def test_docs_do_not_call_a_built_command_a_stub():
    # The wave-4 drift class: `bind-check` was built (ADR-0018) and merged CI-green while
    # README, CONTRIBUTING's enforcement table and one cli-reference paragraph still called it
    # a stub — scripts/changelog_currency.py deliberately excludes those paths, so nothing
    # fired. The stub set has one home (keel.cli.STUB_COMMANDS); a line in these docs that
    # says "stub" while naming a command outside that set is the drift.
    built = {c.name for c in app.registered_commands if c.name} - STUB_COMMANDS
    assert built, 'no registered commands outside the stub set — parse rot'
    for rel in ('README.md', 'docs/cli-reference.md', 'CONTRIBUTING.md'):
        for number, line in enumerate(_read(rel).splitlines(), start=1):
            if 'stub' not in line.lower():
                continue
            offenders = [name for name in built if f'`{name}`' in line or f'`keel {name}' in line]
            assert not offenders, f'{rel}:{number} calls a built command a stub: {offenders}'


def test_declared_stubs_are_documented_as_stubs():
    # The other direction: a command cannot join STUB_COMMANDS silently — the cli-reference
    # table must say "stub" on its row, so shrinking the set forces the docs current (caught
    # above) and growing it forces the admission into the published reference.
    lines = _read('docs/cli-reference.md').splitlines()
    for name in sorted(STUB_COMMANDS):
        assert any(f'`keel {name}' in line and 'stub' in line.lower() for line in lines), (
            f'`{name}` is in keel.cli.STUB_COMMANDS but docs/cli-reference.md never says so'
        )
