"""Recreate core numeric tables from supplied records/predictions, without fits.

Run this file from a review package containing inputs/ and raw_predictions/.
No TeX, network, experiment training or optional deep-learning import.
"""
import csv,hashlib,json,re
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent;I=ROOT/'inputs';O=ROOT/'reproduced_tables';O.mkdir(exist_ok=True)
def read(name):return json.loads((I/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def export(name,records,descriptors):
    rows=[]
    for rec in records:
        values=rec.get('cohort_values',rec.get('values'))
        estimate=rec.get('mean',rec.get('mean_R2'))
        if values is not None:
            computed=float(np.mean(values));assert abs(computed-estimate)<2e-7,(name,computed,estimate);estimate=computed
        row={k:rec.get(k,'') for k in descriptors};row['n']=rec.get('n',rec.get('n_cohorts',rec.get('n_targets','')))
        row['mean']=estimate;row['ci95_low']=rec.get('ci95',[None,None])[0];row['ci95_high']=rec.get('ci95',[None,None])[1]
        if 'raw_p' in rec:row['raw_p']=rec['raw_p']
        if 'Holm_p' in rec:row['Holm_p']=rec['Holm_p']
        rows.append(row)
    if not rows:return
    fields=list(dict.fromkeys(k for v in rows for k in v))
    with (O/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    def esc(s):
        s=str(s)
        for a,b in [('&',r'\&'),('_',r'\_'),('%',r'\%')]:s=s.replace(a,b)
        return s
    body=[]
    for v in rows:
        label=' / '.join(str(v[k]) for k in descriptors if v.get(k,'')!='')
        estimate='' if v['mean'] is None else f"{v['mean']:.6f}"
        ci='' if v['ci95_low'] is None else f"[{v['ci95_low']:.6f}; {v['ci95_high']:.6f}]"
        body.append(esc(label)+' & '+str(v['n'])+' & '+estimate+' & '+ci+r' \\')
    tex=r'\begin{longtable}{p{.56\linewidth}rrr}'+'\n'+r'\toprule Condition / model / endpoint & n & Mean & 95\% interval\\\midrule'+'\n'+'\n'.join(body)+'\n'+r'\bottomrule\end{longtable}'+'\n'
    (O/(name+'.tex')).write_text(tex,encoding='utf-8')

manifest=read('SOURCE_SHA256.json')
for name,digest in manifest.items():assert sha(I/name)==digest,name
s=read('E48_E50_TAM_SONUC_OZETI.json');q=read('E54_TAM_DEGERLENDIRME.json');z=read('E55_IKINCI_TUR_ESLENMIS_OZET.json');m=read('E56_UCUNCU_TUR_OZET.json');t=read('E57_DORDUNCU_TUR_OZET.json')
cells={'SWISS_ISO','SWISS_ANISO','CIRCLE_ISO','MASS_LEAD'}
export('01_simulation_methods',[v for v in s['summary'] if v['cell'] in cells],['cell','method','budget'])
export('02_distance_structure',q['geometry'],['cell','method','metric'])
export('03_map_ablation',m['summary'],['control','metric'])
export('04_output_budgets',z['budget_summary'],['cell','method','budget','metric'])
export('05_calibration_changes',z['calibration_changes'],['cell','method','budget','metric','contrast'])
export('06_crossed_frames',[v for v in q['performance'] if v['target_map'] in ['O','T']],['cell','source_frame','target_map','metric'])
export('07_mass_noise',q['mass_noise'],['noise_sd'])
export('08_local_references',[dict(stats,cell=v['cell'],reference=key) for v in t['personal_references'] for key,stats in v.items() if key in ['local48','transfer0','local_minus_transfer']],['cell','reference'])
export('09_old_primary_families',[dict(v,family=k,mean=v['mean_difference']) for k,rows in s['families'].items() for v in rows],['family','name'])
new=read('E58_ES_ENERJI_OZET.json');eeg=read('E59_RT_KISI_ICI_OZET.json')
export('10_energy_matched',new['summary'],['ratio','method','mapping','calibration','metric'])
export('11_energy_contrasts',new['contrasts'],['ratio','contrast'])
export('12_new_planned_tests',new['planned_two_test_family'],['name'])
export('13_local_EEG_RT',eeg['summary'],['group','scope','method','metric'])
export('14_local_EEG_RT_contrasts',eeg['contrasts'],['group','scope','contrast'])

# Recalculate original valid real-EEG cells from stored predictions. Corrected
# history predictions replace the explicitly invalid old history cells.
arrays={}
for name in ['EEG_original.npz','EEG_corrected_history.npz']:
    with np.load(ROOT/'raw_predictions'/name,allow_pickle=False) as f:arrays.update({k:f[k].copy() for k in f.files})
assert len(arrays)==480
rawrows=[]
for key,a in arrays.items():
    person=int(key.split('_',1)[0]);method,budget=key.split('_',1)[1].rsplit('_',1);y,pred=a[:,0],a[:,1];sse=float(np.sum((y-pred)**2));den=float(np.sum((y-y.mean())**2))
    rawrows.append(dict(subject=person,method=method,budget=int(budget),R2=1-sse/den,MAE_ms=float(np.mean(abs(np.exp(y)-np.exp(pred)))*1000)))
old_eeg=read('E49_OPEN_EEG_SONUC_OZETI.json');lookup={(v['method'],v['budget']):v for v in old_eeg['summary']};ee=[]
for key in sorted(lookup):
    rr=[v for v in rawrows if (v['method'],v['budget'])==key];assert len(rr)==10
    mean=float(np.mean([v['R2'] for v in rr]));assert abs(mean-lookup[key]['mean_R2'])<1e-10
    ee.append(dict(method=key[0],budget=key[1],n_targets=10,mean=mean,ci95=lookup[key]['ci95']))
export('15_open_EEG_transfer',ee,['method','budget'])
with (O/'15_open_EEG_person_predictions_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rawrows[0]));w.writeheader();w.writerows(rawrows)
report=dict(status='PASS_TABLES_REPRODUCED_WITHOUT_MODEL_FITTING_OR_TEX',tables=15,EEG_cells_recomputed=480,old_results_unchanged=True,LaTeX_compilation=False,files={p.name:sha(p) for p in O.iterdir() if p.is_file()})
(O/'REPRODUCTION_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(status=report['status'],tables=15,EEG_cells_recomputed=480)))
