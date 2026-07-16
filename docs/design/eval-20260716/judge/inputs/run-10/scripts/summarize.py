#!/usr/bin/env python3
"""Print the count of tempo log records per level for a given log file.

Usage:
    scripts/summarize.py path/to/log/file

Reuses tempo.parse.parse_line to parse each line into a contract record and
tempo.report.count_by_level to tally records per level.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from tempo.parse import parse_line
from tempo.report import count_by_level


def summarize(log_path):
    records = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(parse_line(line))
    return count_by_level(records)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log_file', help='Path to the log file to summarize')
    args = parser.parse_args(argv)

    counts = summarize(args.log_file)
    for level in sorted(counts):
        print(f'{level}: {counts[level]}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
