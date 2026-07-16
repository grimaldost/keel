#!/usr/bin/env python3
"""Print the count of tempo records per level for a given log file.

Usage:
    scripts/summarize.py <log-file>

Each line of the log file is expected in the 'EPOCH LEVEL MESSAGE' format
parsed by tempo.parse.parse_line. Reuses tempo.report.count_by_level for the
actual tallying, so this script is just a thin CLI wrapper.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from tempo.parse import parse_line
from tempo.report import count_by_level


def summarize(path):
    with open(path, encoding='utf-8') as f:
        records = [parse_line(line) for line in f if line.strip()]
    return count_by_level(records)


def main(argv):
    if len(argv) != 2:
        print(f'usage: {argv[0]} <log-file>', file=sys.stderr)
        return 2

    counts = summarize(argv[1])
    for level in sorted(counts):
        print(f'{level} {counts[level]}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
