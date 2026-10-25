import json
import re
import tomllib
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifests_parse_and_name_keel():
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    market = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    assert plugin['name'] == 'keel'
    assert any(p['name'] == 'keel' for p in market['plugins'])


def declared_version_sites() -> dict[str, str]:
    """Each version site's path and the pattern that reads it, from `railform.toml`.

    The registry is `[version].sites` there: `railform version-sites` (run by the `railform` CI job
    on every leg) holds the sites to one version, and `--bump` writes them. What it cannot see is
    a pattern that reads the wrong literal, so that is what this module still checks.
    """
    frame = tomllib.loads((ROOT / 'railform.toml').read_text(encoding='utf-8'))
    return {site['path']: site['pattern'] for site in frame['version']['sites']}


def test_each_patterned_site_reads_the_field_its_parser_would():
    # The registry is regexes, because a bump must WRITE them; a regex that reads the wrong field
    # would pass `railform version-sites` as long as every site agreed on the wrong literal. The
    # two structured sites are parsed properly here and compared, so the pattern cannot quietly
    # point at some other version literal.
    sites = declared_version_sites()
    plugin_text = (ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8')
    pyproject_text = (ROOT / 'pyproject.toml').read_text(encoding='utf-8')
    plugin = json.loads(plugin_text)
    pyproject = tomllib.loads(pyproject_text)
    plugin_match = re.search(sites['.claude-plugin/plugin.json'], plugin_text)
    pyproject_match = re.search(sites['pyproject.toml'], pyproject_text)
    assert plugin_match is not None
    assert pyproject_match is not None
    assert plugin_match.group(1) == plugin['version']
    assert pyproject_match.group(1) == pyproject['project']['version']


def test_changelog_heading_chain_is_intact():
    # F1 (0.12.0 pre-cut audit; repaired in e5ede82): a release edit REPLACED the previous
    # release's heading instead of inserting above it, so the 0.11.1 entry read as absorbed into
    # 0.12.0's section — and only the blind audit caught it, because the version-site check
    # reads the NEWEST heading only and the broken chain was still strictly descending. Three
    # layers, one per failure shape:
    #   shape — every H2 is a strict `## [x.y.z] - YYYY-MM-DD` heading, except one bare
    #     `## [Unreleased]` allowed as the FIRST H2: changes merged between releases collect there
    #     without moving a version site, and the release cut renames it. The newest-heading
    #     version site above reads the first SemVer heading, so it skips that one; any other
    #     non-SemVer H2, or an `[Unreleased]` below a release, is a violation.
    #   order — strict descending SemVer with no duplicates, comparing parsed integer tuples (not
    #     strings, since '0.10.0' < '0.9.0' lexically) — catches an entry pasted below an older
    #     release, a double-pasted heading, a typo'd version.
    #   absorption — no `### kind` repeats inside one release section: replacing a heading merges
    #     two bodies (`### Changed` twice under one release) — the assertion that actually fails on
    #     the originating F1 file; the order layer alone passes it.
    heading = re.compile(r'^## \[([0-9]+\.[0-9]+\.[0-9]+)\] - [0-9]{4}-[0-9]{2}-[0-9]{2}$')
    lines = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8').splitlines()
    versions: list[tuple[int, int, int]] = []
    section = 'preamble'
    kinds: list[str] = []
    for line in lines:
        if line == '## [Unreleased]' and not versions and section == 'preamble':
            section, kinds = 'Unreleased', []
            continue
        if line.startswith('## '):
            match = heading.match(line)
            assert match is not None, f'malformed release heading: {line!r}'
            major, minor, patch = match.group(1).split('.')
            versions.append((int(major), int(minor), int(patch)))
            section, kinds = match.group(1), []
        elif line.startswith('### '):
            kind = line.removeprefix('### ').strip()
            assert kind not in kinds, (
                f'`### {kind}` repeats inside the [{section}] section — a release edit likely '
                'replaced the previous heading and absorbed its entry (the F1 class)'
            )
            kinds.append(kind)
    assert len(versions) >= 2, 'parse rot: fewer than two release headings found'
    for newer, older in pairwise(versions):
        assert newer > older, (
            f'headings not in strict descending SemVer order: {newer} before {older}'
        )


def frontmatter(path: Path) -> dict[str, str]:
    """The `key: value` lines between a file's opening `---` pair; {} when it has none."""
    lines = path.read_text(encoding='utf-8').splitlines()
    if not lines or lines[0].strip() != '---':
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == '---':
            return fields
        key, sep, value = line.partition(':')
        if sep and key.strip() and not key.startswith(' '):
            fields[key.strip()] = value.strip()
    return {}


def test_referenced_assets_exist():
    assert (ROOT / 'skills' / 'apply-method' / 'SKILL.md').exists()
    assert (ROOT / 'agents' / 'pre-mortem-review.md').exists()
    assert (ROOT / 'commands' / 'keel-check-ready.md').exists()


def test_every_command_is_left_to_the_person_who_types_it():
    # 0.22.0 deleted `/keel-apply`, `/keel-premortem` and `/keel-triage`: none ran once in the
    # 2026-07-26..09-26 field window (493 keel invocations, 488 of them the CLI), and each one's
    # work already had a home the model reaches without it — the `apply-method` skill, the
    # `pre-mortem-review` agent, the `reflection-triage.md` template. A command that stays is a
    # person's entry point, so the model must not run it on its own: a skill the model can reach
    # and a command a person types are two surfaces, and one file should not be both.
    commands = sorted((ROOT / 'commands').glob('*.md'))
    assert commands, 'commands/ enumerated empty'
    model_invocable = [
        path.name
        for path in commands
        if frontmatter(path).get('disable-model-invocation') != 'true'
    ]
    assert not model_invocable, (
        f"commands the model can invoke on its own: {model_invocable} — a command is a person's "
        'entry point; set `disable-model-invocation: true`, or make it a skill'
    )


def test_frontmatter_reads_only_the_opening_block(tmp_path):
    page = tmp_path / 'page.md'
    page.write_text('---\nname: x\nlist:\n  - y: 1\n---\nbody: not a field\n', encoding='utf-8')
    assert frontmatter(page) == {'name': 'x', 'list': ''}
    page.write_text('no front matter\n---\nname: x\n---\n', encoding='utf-8')
    assert frontmatter(page) == {}
    page.write_text('---\nname: x\n', encoding='utf-8')
    assert frontmatter(page) == {}, 'an unterminated block is not front matter'


def test_no_empty_hooks_placeholder(hooks_json=ROOT / 'hooks' / 'hooks.json'):
    # KEEL-B29. `hooks/hooks.json` shipped `{"hooks": {}}` — a slot reserved for an edit-time hook
    # that never arrived, absent from the plugin-reference entry-point table and from that table's
    # coverage test, while the doctrine names hooks as one of the two deterministic machines: the
    # repo's own A10 failure class, in its own tree.
    #
    # The 0.12.0 decision (T2g) kept it because "whether the plugin loader tolerates its absence is
    # unverifiable offline". It is verifiable by inspection, and now verified: four installed,
    # loading plugins in this operator's environment ship no `hooks/` directory at all. The empty
    # placeholder is deleted; a hooks.json that exists must declare a real hook, so the placeholder
    # cannot come back while a genuine edit-time hook still can.
    if hooks_json.exists():
        declared = json.loads(hooks_json.read_text(encoding='utf-8')).get('hooks')
        assert declared, 'hooks/hooks.json declares no hook — an empty placeholder claims a machine'


def test_plugin_reference_documents_every_entry_point():
    # The CLI half has had a coverage test since F9/ARCH-10; the plugin half had none, and two of
    # the four slash commands were named in no published doc at all. Same shape as
    # test_cli_reference_documents_every_command: every shipped entry point appears in the
    # published reference, so a new one cannot land undocumented.
    # All three entry-point directories are globbed, not listed by hand — docs/extension-points.md
    # tells a contributor that adding under `commands/`, `skills/` or `agents/` requires a row
    # here, and a hardcoded list would leave that claim unenforced for two of the three.
    # The command match requires the table's backticked form (`` `/name` `` or `` `/name <arg>` ``)
    # rather than a bare substring: `f'/{name}' in reference` passes vacuously for any name that
    # is a prefix of an existing one (`/keel-check` matches inside `/keel-check-ready`), and an
    # `\b` anchor does not close that hole either, since `-` is already a word boundary.
    reference = (ROOT / 'docs' / 'plugin-reference.md').read_text(encoding='utf-8')
    commands = sorted(p.stem for p in (ROOT / 'commands').glob('*.md'))
    skills = sorted(p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md'))
    agents = sorted(p.stem for p in (ROOT / 'agents').glob('*.md'))
    assert commands and skills and agents, 'an entry-point directory enumerated empty'
    missing = [
        f'/{name}' for name in commands if not re.search(rf'`/{re.escape(name)}(?=[ `])', reference)
    ]
    missing += [
        name for name in skills + agents if not re.search(rf'`{re.escape(name)}`', reference)
    ]
    assert not missing, f'plugin-reference.md is missing: {missing}'


def test_apply_method_routes_through_bindings():
    # §8 (c1-T4): the router consumes the project's bindings record on the already-established
    # path instead of pointing every entry at the packaged templates.
    skill = (ROOT / 'skills' / 'apply-method' / 'SKILL.md').read_text(encoding='utf-8')
    assert 'established format IS the binding' in skill
