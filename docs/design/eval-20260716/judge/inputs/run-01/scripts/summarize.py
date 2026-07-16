#!/usr/bin/env python3
"""Summarize log files: count records per level."""

import sys
from pathlib import Path

# Add src to path to import tempo modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from tempo.parse import parse_line
from tempo.report import count_by_level


def main():
    if len(sys.argv) != 2:
        print('Usage: python3 summarize.py <log-file>', file=sys.stderr)
        sys.exit(1)

    log_file = sys.argv[1]

    try:
        with open(log_file) as f:
            records = [parse_line(line) for line in f if line.strip()]
    except FileNotFoundError:
        print(f'Error: file not found: {log_file}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error reading file: {e}', file=sys.stderr)
        sys.exit(1)

    counts = count_by_level(records)
    for level, count in counts.items():
        print(f'{level}: {count}')


if __name__ == '__main__':
    main()
