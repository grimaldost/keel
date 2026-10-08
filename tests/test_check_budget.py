"""The Definition-of-Ready catalogue grows only when something pays for the new check (0.22.0).

`DOR_CHECK_IDS` went from 25 ids to 28 between 0.20.0 and 0.21.0 — W8, W9 and W10, three warnings,
none removed — and nothing in the suite asked what any of them displaced. One check per finding is
how a gate grows until nobody reads its output. A new id now passes in one of two ways:

- **it is paid for in the same change**: an id leaves the catalogue, or an existing id is demoted
  to warn-only (its reference-block line gains `(warn)`), one for one;
- **it is pre-registered**: a row in `docs/evidence.md`'s tables names it in its first cell, which
  is the disposition the gate ledger will fire for it, written before its data arrives.

"The same change" is the diff against the merge-base with `origin/main`, read from git. CI checks
out full history (`fetch-depth: 0`); a checkout with no `origin/main` skips and says why, rather
than passing in silence. The rule is what is held, not today's count: removing a check or demoting
one never fails here.
"""

import ast
import re
import subprocess
from pathlib import Path

import pytest

from keel.models import DOR_CHECK_IDS

ROOT = Path(__file__).resolve().parents[1]
MODELS = 'src/keel/models.py'
DOR_SHEET = 'src/keel/templates/definition-of-ready.md'
EVIDENCE = ROOT / 'docs' / 'evidence.md'
_ID = r'[A-Z]\d+'
_WARN_LINE_RE = re.compile(rf'^({_ID}) \(warn\)', re.MULTILINE)


def catalogue(models_source: str) -> frozenset[str]:
    """The `DOR_CHECK_IDS` literal in a revision of `src/keel/models.py`."""
    for node in ast.parse(models_source).body:
        if (
            isinstance(node, ast.Assign)
            and any(getattr(target, 'id', None) == 'DOR_CHECK_IDS' for target in node.targets)
            and isinstance(node.value, ast.Call)
            and node.value.args
        ):
            return frozenset(ast.literal_eval(node.value.args[0]))
    raise ValueError('DOR_CHECK_IDS is not a module-level frozenset literal')


def warn_only(sheet: str) -> frozenset[str]:
    """Ids whose reference-block line in `definition-of-ready.md` reads `<id> (warn)`."""
    parts = sheet.split('```')
    return frozenset(_WARN_LINE_RE.findall(parts[1])) if len(parts) >= 3 else frozenset()


def preregistered(evidence: str) -> frozenset[str]:
    """Ids named in the first cell of a table row in `docs/evidence.md`."""
    ids: set[str] = set()
    for line in evidence.splitlines():
        cells = line.split('|')
        if line.lstrip().startswith('|') and len(cells) > 2:
            ids.update(re.findall(rf'\b{_ID}\b', cells[1]))
    return frozenset(ids)


def unpaid(
    base: frozenset[str],
    base_warn: frozenset[str],
    live: frozenset[str],
    live_warn: frozenset[str],
    registered: frozenset[str],
) -> tuple[list[str], int]:
    """(new ids no pre-registered row names, ids removed or demoted that can pay for them)."""
    owed = sorted(live - base - registered)
    credit = len(base - live) + len((base & live) & (live_warn - base_warn))
    return owed, credit


# --- the rule, on synthetic catalogues ------------------------------------------

BASE = frozenset({'A1', 'A2', 'W1'})
BASE_WARN = frozenset({'W1'})


def test_an_unpaid_new_id_is_owed():
    owed, credit = unpaid(BASE, BASE_WARN, BASE | {'W2'}, BASE_WARN | {'W2'}, frozenset())
    assert (owed, credit) == (['W2'], 0)


def test_a_removal_pays_for_a_new_id():
    live = (BASE - {'A2'}) | {'A3'}
    owed, credit = unpaid(BASE, BASE_WARN, live, BASE_WARN, frozenset())
    assert len(owed) <= credit


def test_a_demotion_to_warn_pays_for_a_new_id():
    owed, credit = unpaid(BASE, BASE_WARN, BASE | {'A3'}, BASE_WARN | {'A2'}, frozenset())
    assert (owed, credit) == (['A3'], 1)


def test_a_preregistered_row_admits_a_new_id():
    owed, _ = unpaid(BASE, BASE_WARN, BASE | {'A3'}, BASE_WARN, frozenset({'A3'}))
    assert owed == []


def test_two_new_ids_need_two_payments():
    owed, credit = unpaid(BASE, BASE_WARN, BASE | {'A3', 'A4'}, BASE_WARN | {'A2'}, frozenset())
    assert len(owed) > credit


def test_shrinking_never_owes():
    owed, credit = unpaid(BASE, BASE_WARN, frozenset({'A1'}), frozenset(), frozenset())
    assert owed == [] and credit == 2


def test_the_readers_parse_the_shipped_files():
    # The integration test below reads git revisions of these files through these three readers,
    # so they are held to the files as they ship: a reader that parses nothing would pass the
    # budget vacuously.
    assert catalogue((ROOT / MODELS).read_text(encoding='utf-8')) == DOR_CHECK_IDS
    warns = warn_only((ROOT / DOR_SHEET).read_text(encoding='utf-8'))
    assert {f'W{n}' for n in range(1, 11)} <= warns, sorted(warns)
    assert warns < DOR_CHECK_IDS, 'the warn reader matched every line, failing checks included'
    assert {'A7', 'A9'} <= preregistered(EVIDENCE.read_text(encoding='utf-8'))
    assert preregistered('| trigger | disposition |\n|---|---|\nA7 in prose, not a row\n') == set()


def failing_ids(source: str) -> frozenset[str]:
    """Check ids a module passes as a literal to `Violation(...)`: the findings that fail a spec."""
    ids: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'Violation':
            check = node.args[2] if len(node.args) > 2 else None
            for keyword in node.keywords:
                if keyword.arg == 'check':
                    check = keyword.value
            if isinstance(check, ast.Constant) and isinstance(check.value, str):
                ids.add(check.value)
    return frozenset(ids)


def test_a_warn_marker_is_backed_by_the_code():
    # The budget credits a demotion from the sheet's `(warn)` marker, so the marker has to mean
    # what it says: a check the gate still raises as a Violation cannot read `(warn)`, or an edit
    # to the sheet alone would pay for a new check.
    raised = failing_ids((ROOT / 'src' / 'keel' / 'check_ready.py').read_text(encoding='utf-8'))
    marked = warn_only((ROOT / DOR_SHEET).read_text(encoding='utf-8'))
    assert {'A1', 'A6', 'B1'} <= raised, 'the Violation reader found nothing; it is vacuous'
    assert not raised & marked, (
        f'{sorted(raised & marked)} read `(warn)` in definition-of-ready.md but still fail a spec'
    )


# --- the rule, on this change ---------------------------------------------------


def _git(*args: str) -> str | None:
    try:
        done = subprocess.run(
            ['git', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=False
        )
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def test_a_new_check_id_is_paid_for_or_preregistered():
    merge_base = _git('merge-base', 'HEAD', 'origin/main')
    if merge_base is None:
        pytest.skip(
            'no merge-base with origin/main (a shallow or remote-less checkout), so there is no '
            '"same change" to read; CI checks out full history and runs this'
        )
    base_models = _git('show', f'{merge_base.strip()}:{MODELS}')
    base_sheet = _git('show', f'{merge_base.strip()}:{DOR_SHEET}')
    assert base_models is not None and base_sheet is not None, 'the merge-base lacks the catalogue'
    owed, credit = unpaid(
        catalogue(base_models),
        warn_only(base_sheet),
        DOR_CHECK_IDS,
        warn_only((ROOT / DOR_SHEET).read_text(encoding='utf-8')),
        preregistered(EVIDENCE.read_text(encoding='utf-8')),
    )
    assert len(owed) <= credit, (
        f'DOR_CHECK_IDS gains {owed} against origin/main, and this change removes or demotes '
        f'{credit}. Pay for each new id in the same change — remove a check, or demote one to '
        '`(warn)` — or pre-register the disposition the ledger will fire for it: a row in '
        "docs/evidence.md's table whose first cell names the id."
    )
