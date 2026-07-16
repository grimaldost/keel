#!/usr/bin/env python3
"""Summarize a log file: count records per level."""

import sys
from pathlib import Path

# Add src directory to path so we can import tempo modules
src_path = Path(__file__).resolve().parent.parent / 'src'
sys.path.insert(0, str(src_path))

from tempo.parse import parse_line
from tempo.report import count_by_level


def main():
    if len(sys.argv) < 2:
        print('Usage: summarize.py <logfile>', file=sys.stderr)
        sys.exit(1)

    log_file = sys.argv[1]

    try:
        records = []
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    records.append(parse_line(line))

        counts = count_by_level(records)
        for level in sorted(counts.keys()):
            print(f'{level}: {counts[level]}')
    except FileNotFoundError:
        print(f'Error: File not found: {log_file}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
