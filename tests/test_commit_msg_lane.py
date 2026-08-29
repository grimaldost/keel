"""The commit-msg lane's attribution pattern, held to its published claim.

The no-ai-attribution hook is a one-line grep inside .pre-commit-config.yaml, so nothing
type-checks it and a quoting slip would fail open — the hook would pass everything and CI
would never notice. This loads the exact pattern the hook runs and asserts it rejects the
trailer forms and the generation stamp, and passes an ordinary message.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _hook_pattern() -> re.Pattern[str]:
    config = (ROOT / '.pre-commit-config.yaml').read_text(encoding='utf-8')
    match = re.search(r'grep -Ei "([^"]+)"', config)
    assert match is not None, 'the no-ai-attribution hook pattern was not found'
    return re.compile(match.group(1), re.IGNORECASE)


def test_attribution_trailers_and_stamps_are_rejected():
    pattern = _hook_pattern()
    rejected = (
        'Co-Authored-By: Claude <noreply@anthropic.com>',
        'Signed-off-by: Claude',
        'Assisted-by: GPT-5',
        'Generated-by: Copilot',
        'Generated with [Claude Code](https://claude.com/claude-code)',
        'Generated with Claude',
    )
    for line in rejected:
        assert pattern.search(line), f'the hook pattern misses: {line!r}'


def test_an_ordinary_message_passes():
    pattern = _hook_pattern()
    passes = (
        'fix(release): hold the tag to its section',
        'The fold follows ADR-0018; co-authored the spec with the operator.',
        'Generated fixtures with the staging script.',
        'Signed-off-by: Grimaldo Stanzani',
    )
    for line in passes:
        assert not pattern.search(line), f'the hook pattern false-fires on: {line!r}'
