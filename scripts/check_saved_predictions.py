"""Recompute recorded scores. No model imports, fitting or new inference."""
import csv
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / 'eeg_replication_tools'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    rows = []
    max_error = 0.0
    counts = {}

    def check(scope, key, expected, actual):
        nonlocal max_error
        error = abs(float(expected) - float(actual))
        if not np.isfinite(error) or error > 2e-6:
            raise AssertionError((scope, key, expected, actual, error))
        max_error = max(max_error, error)
        counts[scope] = counts.get(scope, 0) + 1
        rows.append(dict(scope=scope, key=key, recorded=float(expected), recomputed=float(actual), absolute_error=error))

    for folder in ['E48_full_revision_v1', 'E50_corrected_dynamics_v1', 'E51_global_geometry_v1']:
        files = sorted((CODE / folder).glob('cohort_*/*/paired_predictions.npz'))
        if len(files) != 152:
            raise AssertionError((folder, 'expected 152 completed cells', len(files)))
        for p in files:
            record = read(p.with_name('result.json'))
            lookup = {f"{v['person']}_{v['method']}_{v['budget']}": v for v in record['rows']}
            with np.load(p, allow_pickle=False) as data:
                if set(data.files) != set(lookup):
                    raise AssertionError(('prediction/result keys differ', str(p)))
                for key, a in data.items():
                    truth, pred, wrong = a[:, :2], a[:, 2:4], a[:, 4:6]
                    energy = float(np.sum(truth**2))
                    row = lookup[key]
                    check(folder, str(p.relative_to(CODE)) + ':' + key, row['private_R2'], 1 - float(np.sum((truth-pred)**2)) / energy)
                    if 'wrong_EEG_R2' in row:
                        check(folder + ':wrong_EEG', str(p.relative_to(CODE)) + ':' + key, row['wrong_EEG_R2'], 1 - float(np.sum((truth-wrong)**2)) / energy)

    files = sorted((CODE / 'E58_energy_matched_v1').glob('cohort_*/ratio_*/predictions.npz'))
    if len(files) != 80:
        raise AssertionError(('expected 80 energy-matched cells', len(files)))
    for p in files:
        record = read(p.with_name('result.json'))
        lookup = {f"{v['person']}_{v['method']}_{v['mapping']}_{v['calibration']}": v for v in record['rows']}
        with np.load(p, allow_pickle=False) as data:
            if set(data.files) != set(lookup):
                raise AssertionError(('prediction/result keys differ', str(p)))
            for key, a in data.items():
                truth, pred = a[0], a[1]
                delta, dpred = truth[1]-truth[0], pred[1]-pred[0]
                whole, phole = np.concatenate(truth), np.concatenate(pred)
                check('E58:private', str(p.relative_to(CODE)) + ':' + key, lookup[key]['private_R2'], 1-float(np.sum((delta-dpred)**2))/float(np.sum(delta**2)))
                check('E58:absolute', str(p.relative_to(CODE)) + ':' + key, lookup[key]['absolute_R2'], 1-float(np.sum((whole-phole)**2))/float(np.sum((whole-whole.mean(0))**2)))

    for person in range(1, 14):
        folder = CODE / 'E59_local_RT_v1' / f'subject_{person:02d}'
        record = read(folder / 'result.json')
        lookup = {(v['scope'], v['method']): v for v in record['rows']}
        with np.load(folder / 'predictions.npz', allow_pickle=False) as data:
            for key, a in data.items():
                method, tag = key.rsplit('_', 1)
                scope = 'run2_to_run3' if tag == 'run3' else 'run2_nested_forward'
                y, yp = a[:, 0], a[:, 1]
                check('E59', f'{person}:{key}', lookup[scope, method]['R2'], 1-float(np.sum((y-yp)**2))/float(np.sum((y-y.mean())**2)))

    # Original and corrected history EEG archives: corrected keys supersede old.
    arrays = {}
    for name in ['EEG_original.npz', 'EEG_corrected_history.npz']:
        with np.load(ROOT / 'raw_predictions' / name, allow_pickle=False) as data:
            arrays.update({k: data[k].copy() for k in data.files})
    if len(arrays) != 480:
        raise AssertionError(('expected 480 valid EEG cells', len(arrays)))
    grouped = {}
    for key, a in arrays.items():
        _, rest = key.split('_', 1)
        method, budget = rest.rsplit('_', 1)
        y, yp = a[:, 0], a[:, 1]
        grouped.setdefault((method, int(budget)), []).append(1-float(np.sum((y-yp)**2))/float(np.sum((y-y.mean())**2)))
    for record in read(ROOT / 'inputs' / 'E49_OPEN_EEG_SONUC_OZETI.json')['summary']:
        key = record['method'], record['budget']
        check('E49:valid_mean', str(key), record['mean_R2'], np.mean(grouped[key]))

    out = ROOT / 'outputs'
    out.mkdir(exist_ok=True)
    with (out / 'prediction_score_checks.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = dict(status='PASS_RECORDED_PREDICTION_SCORES', checks_by_scope=counts, maximum_absolute_error=max_error, valid_EEG_cells=480,
                  note='Arithmetic checks include historical prototype rows for integrity; use the corrected audited summaries for inference.', new_fits=False, new_tests=False)
    (out / 'PREDICTION_REPRODUCTION_AUDIT.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
