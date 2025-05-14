#!/usr/bin/env python3
"""
political_compass_runner.py

Runs political_compass.py on every JSON in a given directory,
skipping any whose `filename` is already recorded in summary.csv.
Supports a dry-run mode that invokes the processing script with its --dry-run flag.
"""
import os
import sys
import csv
import subprocess
import argparse
import argcomplete

# Path to the master summary CSV created by political_compass.py
SUMMARY_CSV = "csv_results/summary.csv"


def get_done_filenames():
    """
    Read SUMMARY_CSV and return a set of all 'filename' values already processed.
    """
    done = set()
    if os.path.exists(SUMMARY_CSV):
        with open(SUMMARY_CSV, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                done.add(row['filename'])
    return done


def main():
    parser = argparse.ArgumentParser(
        description='Run political_compass.py on each JSON in a directory, skipping those already done.'
    )
    parser.add_argument(
        'directory',
        help='Path to the directory containing result JSON files'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action=argparse.BooleanOptionalAction,
        help='Invoke political_compass.py with --dry-run rather than normal mode'
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a directory.", file=sys.stderr)
        sys.exit(1)

    done = get_done_filenames()
    json_files = [f for f in os.listdir(args.directory) if f.endswith('.json')]

    if not json_files:
        print(f"No JSON files found in {args.directory}")
        return

    # Process each JSON file in sorted order
    for fname in sorted(json_files):
        base = os.path.splitext(fname)[0]
        if base in done:
            print(f"Skipping {fname}  (already in summary.csv)")
            continue

        fullpath = os.path.join(args.directory, fname)
        # Construct command
        if args.dry_run:
            cmd = [sys.executable, 'political_compass.py', fullpath, '--dry-run']
        else:
            cmd = [sys.executable, 'political_compass.py', fullpath]

        print(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {fname}: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
