"""The adversarial positive-control corpus (T0.2) — R1(b), bought for nothing.

A check that has never fired in the field is either sharp and internalised, or broken. From the
outside those are the same observation, and the retro census left "power unproven" against most of
Part A for exactly that reason. This corpus answers it: one realistic spec that fires nothing, and
one minimal edit per check that must make exactly that check fire.

The question "can A4 catch a broken bijection inside a real spec?" is a property of
`_check_manifest`, not of an agent, so it is a pytest run and not a paid trial. Where a mutant does
NOT fire, that is a reproduced defeat and it is marked `xfail(strict=True)` with the mechanism —
three of A10's are, and until they pass no disposition may be argued from A10's silence.

Two properties, or the corpus proves nothing:

1. Every mutant is a ONE-EDIT delta from `clean-series.md`, and the assertion is set equality —
   `fired == {target}`, never `target in fired`. A mutant that trips three checks is a bad
   fixture, not a strong one.
2. `clean-series.md` is realistic (anchors into a staged tree, a real manifest, a real fold
   ledger) and is NOT a keel document: an oracle that shares vocabulary with the artifact under
   study cannot report on it.

`materialize` is deliberately reusable: the same mutants are the staged defective specs a repair
task needs, so the corpus that proves each planted defect is detectable is the corpus a later
measurement stages.
"""

import shutil
import tomllib
from pathlib import Path

import pytest

from keel import __version__
from keel.check_ready import check_spec_ready, spec_hash, spec_hash_without_amendments
from keel.models import CHECK_IDS

FIXTURES = Path(__file__).resolve().parent / 'fixtures' / 'adversarial'
CLEAN = FIXTURES / 'clean-series.md'
# The stamp the fixture carries as written. `materialize` rewrites it to the running version so
# the corpus does not go W1-noisy on every release — a mutant that edits the stamp itself is
# applied first, so its edit survives the rewrite.
FIXTURE_KIT = '- **Kit:** 0.14.0'
MUTANTS = tomllib.loads((FIXTURES / 'mutants.toml').read_text(encoding='utf-8'))['mutant']
ARTIFACT = 'clean-series.premortem.md'


def _body(mutant: dict) -> str:
    """The mutated spec text, with the fixture's find/replace applied exactly once."""
    text = CLEAN.read_text(encoding='utf-8')
    find = mutant.get('find')
    if find is None:
        return text
    assert text.count(find) == 1, (
        f'{mutant["id"]}: `find` must match the clean spec exactly once '
        f'(matched {text.count(find)}) — a fixture that edits two places is not a one-edit delta'
    )
    replace = mutant.get('replace', '')
    if repeat := mutant.get('repeat'):
        # 13-24 are the two function bodies in the staged tree's orders.py; +12 puts every one of
        # them past end-of-file, which is what one insertion above a self-anchored ledger does.
        replace = '\n'.join(
            replace.format(n=n, true_line=13 + (n - 1) % 12, shifted_line=25 + (n - 1) % 12)
            for n in range(1, repeat + 1)
        )
    return text.replace(find, replace)


def _artifact_hash(mutant: dict, spec: Path) -> str:
    """What the staged artifact records as `Spec-hash:`.

    Default: the spec exactly as written, so a mutation elsewhere never leaks a B2 hash warning
    into another mutant's result. The `@without-amendments` sentinel is the one DERIVED form a
    fixture may ask for, and W7 is why it has to exist: a literal cannot serve, because the hash
    depends on the running version rewritten into the kit stamp, and W7's claim is a relation
    between two hashes rather than a value.
    """
    asked = mutant.get('artifact_hash')
    if asked == '@without-amendments':
        return spec_hash_without_amendments(spec)
    return asked or spec_hash(spec)


def materialize(tmp_path: Path, mutant: dict) -> Path:
    """Stage the mini-repo, write the mutated spec and its pre-mortem artifact; return the spec.

    The artifact's `Spec-hash:` is computed from the spec as written, so a mutation elsewhere in
    the body never leaks a B2 hash warning into another mutant's result — unless the fixture asks
    for one (`artifact_hash`).
    """
    shutil.copytree(FIXTURES / 'tree', tmp_path, dirs_exist_ok=True)
    spec = tmp_path / CLEAN.name
    spec.write_text(_body(mutant).replace(FIXTURE_KIT, f'- **Kit:** {__version__}'), 'utf-8')
    (tmp_path / ARTIFACT).write_text(
        f'# saved pre-mortem pass\n\n'
        f'PREMORTEM-VERDICT: {mutant.get("artifact_verdict", "CERTIFIED")}\n'
        f'Spec-hash: {_artifact_hash(mutant, spec)}\n',
        encoding='utf-8',
    )
    return spec


def fired(spec: Path) -> set[str]:
    result = check_spec_ready(spec)
    return {v.check for v in result.violations} | {w.check for w in result.warnings}


def _cases():
    for mutant in MUTANTS:
        marks = (
            [pytest.mark.xfail(strict=True, reason=mutant['xfail'])] if 'xfail' in mutant else []
        )
        yield pytest.param(mutant, id=mutant['id'], marks=marks)


def test_the_clean_spec_is_the_false_positive_floor(tmp_path):
    # Every mutant is diffed against this. A corpus whose base is not silent measures the base.
    result = check_spec_ready(materialize(tmp_path, {'id': 'clean'}))
    assert result.passed, [(v.check, v.where, v.message) for v in result.violations]
    assert result.warnings == (), [(w.check, w.message) for w in result.warnings]


@pytest.mark.parametrize('mutant', list(_cases()))
def test_mutant_fires_exactly_its_target(tmp_path, mutant):
    assert fired(materialize(tmp_path, mutant)) == set(mutant['fires']), mutant['why']


def test_the_uniform_drift_reports_every_row(tmp_path):
    # 57 rows, one insertion, one cause. The count is what the report-unit change (T1.2) will be
    # measured against, so it is pinned here before that change lands.
    mutant = next(m for m in MUTANTS if m['id'] == 'A12-drift-57')
    result = check_spec_ready(materialize(tmp_path, mutant))
    assert len([v for v in result.violations if v.check == 'A12']) == 57


def test_every_finding_over_the_whole_corpus_carries_a_catalogued_id(tmp_path):
    # T0.1's proof obligation, writable only because this corpus exists: run the gate over every
    # fixture and assert no finding is anonymous. An anonymous finding is one the ledger cannot
    # count, and a check whose fires cannot be counted cannot be kept or cut on evidence.
    for index, mutant in enumerate(MUTANTS):
        spec = materialize(tmp_path / str(index), mutant)
        result = check_spec_ready(spec)
        for finding in (*result.violations, *result.warnings):
            assert finding.check in CHECK_IDS, (mutant['id'], finding)


def test_every_check_in_the_catalogue_has_a_positive_control(tmp_path):
    # The corpus is only a power probe if it covers the surface. A check with no mutant here is a
    # check whose silence in the field stays uninformative, so a gap must be a recorded decision.
    covered = {check for mutant in MUTANTS for check in mutant['fires']}
    missing = CHECK_IDS - covered
    assert missing == {'A3'}, (
        f'unexpected checks without a positive control: {sorted(missing)}. A3 is the recorded '
        'exception: its power is already proven in the field (7 fires across the 44-doc control '
        'arm), so a mutant would add nothing.'
    )
