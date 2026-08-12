"""The candidate core bodies: strict subsets, and invisible to `keel init`.

An ablation whose arms differ by a REWRITE measures wording. These arms differ by deletion only,
and this module holds that: every line of a core body appears, in order, in the body it was cut
from. The diff is then exactly the independent variable, and it stays that way as the originals
move.

The second half matters more than it looks: a candidate must never reach a consumer. `keel init`
copies the kit directory non-recursively, so the `core/` subdirectory is out of reach by
construction rather than by convention — but a later refactor to `rglob` would ship two competing
spec templates to every adopting project, and this is what would catch it.
"""

from keel.templates import copy_templates, list_templates, templates_root

CORE = ('spec-template.md', 'definition-of-ready.md')

# What each core stops naming — and therefore what a "core matches full" result would license
# cutting. The checks themselves are untouched: they run and reject in every arm.
DROPPED_CHECKS = {'spec-template.md': ('A9', 'A10', 'A11')}


def _lines(path) -> list[str]:
    return path.read_text(encoding='utf-8').splitlines()


def test_every_core_body_is_a_strict_line_subset_of_its_original():
    for name in CORE:
        full = _lines(templates_root() / name)
        core = _lines(templates_root() / 'core' / name)
        assert core, name
        cursor = iter(full)
        for line in core:
            assert any(candidate == line for candidate in cursor), (
                f'{name}: core line is not present in order in the original — the arms differ by '
                f'a rewrite, not a deletion, so the bank would measure wording: {line!r}'
            )


def test_every_core_body_is_actually_smaller():
    for name in CORE:
        full = (templates_root() / name).read_text(encoding='utf-8').split()
        core = (templates_root() / 'core' / name).read_text(encoding='utf-8').split()
        assert len(core) < len(full), f'{name}: the core arm is not a reduction of anything'


def test_the_core_spec_template_stops_naming_exactly_the_full_only_checks():
    # The full-only class IS the cut decision: these three letters are named in the full body and
    # not in the core, so a per-criterion gap on them is what the run is buying.
    full = (templates_root() / 'spec-template.md').read_text(encoding='utf-8')
    core = (templates_root() / 'core' / 'spec-template.md').read_text(encoding='utf-8')
    for check in DROPPED_CHECKS['spec-template.md']:
        assert check in full, check
        assert check not in core, f'{check} still named in the core body; the arms do not differ'


def test_the_core_dor_keeps_the_whole_part_a_reference_block():
    # The core drops DESCRIPTION, never the contract. A core that also thinned the reference block
    # would be measuring a weaker gate rather than a shorter body.
    full = (templates_root() / 'definition-of-ready.md').read_text(encoding='utf-8').split('```')[1]
    core = (
        (templates_root() / 'core' / 'definition-of-ready.md')
        .read_text(encoding='utf-8')
        .split('```')[1]
    )
    assert core == full


def test_candidates_are_not_part_of_the_kit(tmp_path):
    assert 'core' not in {path.parent.name for path in list_templates()}
    copied = copy_templates(tmp_path)
    assert not (tmp_path / 'core').exists(), 'keel init shipped a measurement candidate'
    names = [path.name for path in copied]
    assert len(names) == len(set(names)), f'two files claim one kit name: {names}'
