"""Claim-currency guard: the comparative headline stays retired (0.13.0 §12, ADR-0015).

A promoted decision ships with a regression test (CONTRIBUTING gate-health rule 1). ADR-0015
retired the comparative claim at ADR-0013's run-or-retire deadline; this pins that the public
docs do not quietly resurrect the "pending experiment" IOU without reopening the claim by ADR.
"""

from pathlib import Path

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
