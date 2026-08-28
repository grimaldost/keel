"""Serve the kit's own bodies from the CLI — a projection of the shipped files, never a copy.

The field round that motivated this recorded three asks for text that already ships in the exact
version the operator was running: the round->=2 re-gate posture (in the dispatched directive), the
one-verdict-per-artifact idiom (in the spec template's certification block), and the module-form
invocation recipe (in the installation doc). None was an absence. Each was a delivery that never
arrived, because the method's text lives in files a session dispatches or scaffolds but never
reads back — while the CLI is, by a wide margin, the surface a session does reach.

So `show` adds no text. It reads the shipped file at run time and prints it, which is what keeps
one home: a projection cannot drift from its source, and a copy would. `docs/doctrine.md` is
deliberately not servable — it is outside the built distribution (a wheel carries only
`src/keel/**`), so serving it would mean copying it into the package, which is the duplication
this module exists to avoid.
"""

from keel.errors import format_error
from keel.templates import list_templates, templates_root

# Names that are not a template stem. Each resolves to a span of a shipped file, so the file stays
# the single home and this table stays a routing decision rather than content.
_DERIVED = {
    'directive': 'the fenced prompt dispatched on every pre-mortem pass',
    'checks': 'the Part-A reference block: what `check_spec_ready` asserts, check by check',
}


def available() -> dict[str, str]:
    """Every name `show` serves, mapped to a one-line description of what it prints."""
    names = {path.stem: f'the kit template `{path.name}`' for path in list_templates()}
    return dict(sorted({**names, **_DERIVED}.items()))


def _fenced_block(text: str, name: str, source: str) -> str:
    """The first fenced span of a body — the reference block, read rather than restated."""
    parts = text.split('```')
    if len(parts) < 3:
        raise LookupError(
            format_error(
                what=f'`{name}` is served from a fenced block in {source}, and none was found.',
                why='The projection reads the shipped file at run time; it holds no copy to fall '
                'back on, which is what keeps the file the single home.',
                fix=f'Check that {source} still carries its fenced block.',
            )
        )
    return parts[1].strip('\n')


def body(name: str) -> str:
    """The text `keel show <name>` prints, read from the serving bundle."""
    if name == 'checks':
        source = templates_root() / 'definition-of-ready.md'
        return _fenced_block(source.read_text(encoding='utf-8'), name, 'definition-of-ready.md')
    if name == 'directive':
        source = templates_root() / 'pre-mortem-prompt.md'
        text = source.read_text(encoding='utf-8')
        return _fenced_block(text.split('## Prompt', 1)[-1], name, 'pre-mortem-prompt.md')
    template = templates_root() / f'{name}.md'
    if not template.is_file():
        known = ', '.join(available())
        raise LookupError(
            format_error(
                what=f'`{name}` is not a body this kit serves.',
                why='`show` prints only what the installed bundle actually carries, so a name it '
                'does not know is a name whose text would have to be invented.',
                fix=f'Run `keel show --list`, or pick one of: {known}.',
            )
        )
    return template.read_text(encoding='utf-8').rstrip('\n')
