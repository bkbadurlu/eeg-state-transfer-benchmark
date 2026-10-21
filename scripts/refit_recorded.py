"""Refit existing plans in a new, isolated folder without altering records."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / 'eeg_replication_tools'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--analysis', required=True, choices=['local-rt', 'energy'])
    p.add_argument('--output', required=True)
    p.add_argument('--dry-run', action='store_true', help='Check the plan and describe the operation without writing or fitting.')
    args = p.parse_args()
    dest = Path(args.output).resolve()
    if dest.exists():
        p.error('Output already exists. Choose a new path; no files will be cleared.')
    if dest == ROOT or ROOT in dest.parents and not (ROOT / 'scratch_refits') in dest.parents:
        p.error('Inside the repository use a new scratch_refits/ subdirectory.')
    ancestor = dest.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    reserve = 3 * 1024**3 + 512 * 1024**2 + 256 * 1024**2
    if shutil.disk_usage(ancestor).free <= reserve:
        p.error('Insufficient free space for 3 GiB + 512 MiB reserve + output allowance.')
    entry = 'e59_time_blocked_local_rt_20261020.py' if args.analysis == 'local-rt' else 'e58_energy_matched_anisotropy_20261020.py'
    plan = 'E59_PLAN_20261020.json' if args.analysis == 'local-rt' else 'E58_PLAN_20261020.json'
    record = json.loads((CODE / plan).read_text(encoding='utf-8'))
    if record['code_sha256'] != hashlib.sha256((CODE / entry).read_bytes()).hexdigest():
        raise SystemExit('Original plan/source hash does not match.')
    if args.dry_run:
        print(json.dumps(dict(status='PASS_REFIT_PLAN_DRY_RUN', analysis=args.analysis, output=str(dest), creates_output=False, fits=False)))
        return
    dest.mkdir(parents=True)
    target = dest / 'eeg_replication_tools'
    target.mkdir()
    if args.analysis == 'local-rt':
        names = ['e59_time_blocked_local_rt_20261020.py', 'E59_PLAN_20261020.json']
    else:
        names = [q.name for q in CODE.glob('*.py')] + ['E58_PLAN_20261020.json', 'E48_PROTOCOL_20261019.json']
    for name in names:
        shutil.copy2(CODE / name, target / name)
    if args.analysis == 'local-rt':
        data = target / 'E49_open_EEG_v1'
        data.mkdir()
        for q in (CODE / 'E49_open_EEG_v1').glob('sub-*_run-*_features.*'):
            if q.suffix in ['.json', '.npz']:
                shutil.copy2(q, data / q.name)
        entry, plan = 'e59_time_blocked_local_rt_20261020.py', 'E59_PLAN_20261020.json'
    else:
        shutil.copytree(CODE / 'revision_public_resources_20261019', target / 'revision_public_resources_20261019')
        entry, plan = 'e58_energy_matched_anisotropy_20261020.py', 'E58_PLAN_20261020.json'
    record = json.loads((target / plan).read_text(encoding='utf-8'))
    digest = hashlib.sha256((target / entry).read_bytes()).hexdigest()
    if record['code_sha256'] != digest:
        raise SystemExit('Original plan/source hash does not match.')
    subprocess.run([sys.executable, '-B', str(target / entry), 'run'], cwd=dest, check=True)


if __name__ == '__main__':
    main()
