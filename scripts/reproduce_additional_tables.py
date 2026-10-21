"""Export later recorded summaries without new inference or model fitting."""
import csv
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'inputs'
OUT = ROOT / 'reproduced_tables'


def read(name):
    return json.loads((INPUT / name).read_text(encoding='utf-8'))


def export(name, records):
    if not records:
        return
    fields = list(dict.fromkeys(k for row in records for k in row))
    with (OUT / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()} for row in records)


def main():
    OUT.mkdir(exist_ok=True)
    q = read('E54_TAM_DEGERLENDIRME.json')
    exports = {}
    for name, key in [('16_point_correspondence', 'point_correspondence'), ('17_covariance_controls', 'covariance_controls'), ('18_sensory_control', 'sensory_control')]:
        data = q[key]
        exports[name] = data if isinstance(data, list) else [data]
    pooled = read('ROUND6_POOLED_ISOMETRIC.json')['comparisons']
    for row in pooled:
        a, b = np.array(row['old_values']), np.array(row['new_values'])
        assert abs(float(a.mean())-row['old_mean']) < 1e-10
        assert abs(float(b.mean())-row['new_mean']) < 1e-10
        assert abs(float(np.r_[a,b].mean())-row['combined_mean']) < 1e-10
    exports['19_pooled_isometric_heterogeneity'] = [{k: v for k,v in row.items() if k not in ['old_values', 'new_values']} for row in pooled]
    e = read('E58_ES_ENERJI_OZET.json')
    energy = e['energy_summary']
    exports['20_energy_matching_checks'] = energy if isinstance(energy, list) else [energy]
    for name, records in exports.items():
        export(name, records)
    print(json.dumps(dict(status='PASS_ADDITIONAL_RECORDED_SUMMARIES', additional_tables=len(exports), pooled_cohorts=40, new_fits=False, new_tests=False)))


if __name__ == '__main__':
    main()
