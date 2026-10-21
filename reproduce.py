"""Portable recorded-result entry point; no implicit fitting or downloads."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def call(relative, *args):
    subprocess.run([sys.executable, '-B', str(ROOT / relative), *args], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', nargs='?', choices=['all', 'verify', 'tables', 'predictions', 'refit'], default='all')
    parser.add_argument('--analysis', choices=['local-rt', 'energy'])
    parser.add_argument('--output')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.command == 'refit':
        if not args.analysis or not args.output:
            parser.error('refit requires --analysis and a new --output directory')
        extra = ['--dry-run'] if args.dry_run else []
        call('scripts/refit_recorded.py', '--analysis', args.analysis, '--output', args.output, *extra)
        return
    if args.analysis or args.output or args.dry_run:
        parser.error('--analysis, --output and --dry-run are refit options only')
    if args.command in ['all', 'verify']:
        call('scripts/verify_package.py')
    if args.command in ['all', 'tables']:
        call('reproduce_tables.py')
        call('scripts/reproduce_additional_tables.py')
    if args.command in ['all', 'predictions']:
        call('scripts/check_saved_predictions.py')


if __name__ == '__main__':
    main()
