"""Replay one fixed, existing surface example for scientifically literal artwork.

This is figure-data reconstruction, not a new experiment or parameter search.
No training of deep models, outcome fitting, hypothesis tests or downloads.
Original source/results/protocols are read-only and are checked afterwards.
"""
from pathlib import Path
import hashlib
import json
import shutil
import time
import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import spearmanr

H=Path(__file__).resolve().parent
P=H.parent/"EEG_MAKALE"
D=P/"grafik_ozet_dogrulama_20261021"
D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert shutil.disk_usage(P).free>3*1024**3+512*1024**2+32*1024**2
source=H/"e48_revision_core.py"
diagnostic=H/"E54_review_validation_v1/cohort_00/SWISS_ISO/result.json"
protocol=H/"E48_PROTOCOL_20261019.json"
main=P/"latex_makale/main.tex"
eeg=H/"E49_open_EEG_v1/sub-004_run-3_features.npz"
eegmeta=eeg.with_suffix(".json")
summary=P/"jnm_tam_revizyon_20261019/E48_E50_TAM_SONUC_OZETI.json"
absolute=P/"latex_makale/main.tex"
protected=[source,diagnostic,protocol,main,eeg,eegmeta,summary]
before={str(p):sha(p) for p in protected}
cache=D/"GRAPHIC_NUMERIC_INPUTS.npz"
if cache.exists():
    meta=json.loads((D/"EVIDENCE_REPLAY_AUDIT.json").read_text(encoding="utf-8"))
    assert meta["source_hashes"]==before,"Figure cache is stale"
    print(json.dumps({"status":"EXISTING_CHECKED_FIGURE_DATA_REUSED","cache":str(cache)}))
    raise SystemExit

print("Reconstructing fixed original cohort 0; source 6000 and first target 6003.",flush=True)
start=time.monotonic()
import e48_revision_core as r
world=r.World("SWISS_ISO",1800)
ref,target=6000,6003
people=[ref,target]
train={p:world.blocks(p,range(48),truth=True) for p in people}
x=np.concatenate([b["x"] for b in train[ref][:12]]).astype(float)
ev=np.linalg.eigvalsh(np.cov(x.T))
rank=int(np.clip(np.sum(ev>1.5*np.median(ev[:len(ev)//2])),2,17))
assert rank==3
reps={}
for p in people:
    x=np.concatenate([b["x"] for b in train[p]]).astype(float)
    pc=r.pca_fit(x,rank)
    graph=r.graph_fit(r.pca_apply(pc,x),481000+world.seed*31+p)
    reps[p]={"pca":pc,"graph":graph}
    print("Replayed original unsupervised encoder for subject",p,flush=True)
def encode(p,x):
    return r.graph_apply(reps[p]["graph"],r.pca_apply(reps[p]["pca"],x.astype(float)))
pool={p:world.blocks(p,range(2000,2048)) for p in people}
encoded={p:[{"GEO":encode(p,b["x"])} for b in pool[p]] for p in people}
# fit_alignment depends only on the first-source reference and each person's
# response signatures; including only this pair leaves that map unchanged.
maps=r.fit_alignment(pool,encoded,[ref])
print("Replayed original input-assisted affine map; no state labels used in fitting.",flush=True)
probes=world.blocks(ref,range(6000,6004),truth=True,repeat=0)
tt=np.linspace(39,150,32,dtype=int)
truth=np.concatenate([b["truth"][tt] for b in probes])
src=np.concatenate([encode(ref,b["x"])[tt] for b in probes])
raw=[]
for b in probes:
    z=b["truth"]
    phi=np.c_[z[:,0]*np.cos(z[:,0])/10,z[:,1],z[:,0]*np.sin(z[:,0])/10]
    x=phi@world.observation(target).T
    x+=np.random.default_rng(np.random.SeedSequence([513900,world.seed,target,b["trial"]])).normal(0,.12,x.shape)
    raw.append(encode(target,x.astype("float32"))[tt])
raw=np.concatenate(raw)
mapped=r.apply_map(maps[target]["GEO"],raw)
metric=world.metric(truth)
up=np.triu_indices(128,1)
rho=float(spearmanr(metric[up],cdist(raw,raw)[up]).statistic)
norm=float(np.sum((src-src.mean(0))**2))
nrmse=float(np.sqrt(np.sum((mapped-src)**2)/norm))
order=np.argsort(cdist(mapped,src),axis=1)
top5=float(np.mean(np.any(order[:,:5]==np.arange(128)[:,None],axis=1)))
old=json.loads(diagnostic.read_text(encoding="utf-8"))
old_geo=next(q for q in old["geometry"] if q["person"]==target and q["method"]=="GEO")
old_match=next(q for q in old["correspondence"] if q["person"]==target and q["map"]=="INPUT")
assert abs(rho-old_geo["rho"])<1e-10,(rho,old_geo)
assert abs(nrmse-old_match["normalized_coordinate_RMSE"])<1e-6,(nrmse,old_match)
assert abs(top5-old_match["top5"])<1e-12

# Use two fixed probes for the TRUE intrinsic geodesic on the known generator.
# In the (arc(theta), height) coordinates the metric is Euclidean.
def arc(t):
    return .05*(t*np.sqrt(1+t*t)+np.arcsinh(t))
endpoints=truth[[0,32]].astype(float)
fraction=np.linspace(0,1,300)
intrinsic=np.array([arc(endpoints[:,0]),endpoints[:,1]]).T
line_intrinsic=(1-fraction[:,None])*intrinsic[0]+fraction[:,None]*intrinsic[1]
from scipy.optimize import brentq
thetas=np.array([brentq(lambda a:arc(a)-desired,1.5*np.pi,4.5*np.pi,
                        xtol=1e-13) for desired in line_intrinsic[:,0]])
path_state=np.c_[thetas,line_intrinsic[:,1]]
geodesic=np.c_[thetas*np.cos(thetas)/10,path_state[:,1],thetas*np.sin(thetas)/10]
intrinsic_error=float(np.max(abs(arc(thetas)-line_intrinsic[:,0])))
assert intrinsic_error<1e-11
phi_probes=np.c_[truth[:,0]*np.cos(truth[:,0])/10,truth[:,1],truth[:,0]*np.sin(truth[:,0])/10]

# Actual retained early-EEG features. Selection is first eligible held-out trial,
# not an attractive trace or a correctly predicted behavioral outcome.
with np.load(eeg,allow_pickle=False) as f:
    channels=f["channels"].tolist()
    eligible=f["quality"]&(f["onset"]>=8)&(f["kind"]=="oddball")&np.isfinite(f["rt"])&(f["rt"]>=.25)&(f["rt"]<=1.2)
    ix=int(np.flatnonzero(eligible)[0])
    channel=channels.index("Cz")
    values=f["x"][ix].reshape(8,17)[:,channel].astype(float)
    onset=float(f["onset"][ix])
    rt=float(f["rt"][ix])
meta=json.loads(eegmeta.read_text(encoding="utf-8"))
fs=float(meta["sampling_frequency"])
nwin=int(round(.2*fs))
bins=np.array_split(np.arange(nwin),8)
times=np.array([b.mean()/fs*1000 for b in bins])
assert len(values)==len(times)==8 and np.isfinite(values).all()

# Reported means are read from the existing audited JSON / manuscript, not typed
# into a new plot as invented values.
ss=json.loads(summary.read_text(encoding="utf-8"))
means={q["method"]:q["mean_R2"] for q in ss["summary"]
       if q["cell"]=="SWISS_ISO" and q["budget"]==0 and q["method"] in ["GEO","PCA"]}
assert round(means["GEO"],3)==.392 and round(means["PCA"],3)==.168
text=absolute.read_text(encoding="utf-8")
abs_table=text.split(r"\textit{(b) Absolute reports}",1)[1]
import re
line=re.search(r"Isometric surface\s*&\s*([\d.]+)\s*/\s*([\d.]+)",abs_table)
assert line
absmeans=[float(line.group(1)),float(line.group(2))]
assert absmeans==[.222,.382]
np.savez_compressed(cache,truth=truth,phi_probes=phi_probes,source_coordinates=src,
    target_raw_coordinates=raw,target_mapped_coordinates=mapped,
    map_matrix=maps[target]["GEO"]["matrix"],map_offset=maps[target]["GEO"]["offset"],
    true_geodesic_states=path_state,true_geodesic_xyz=geodesic,
    geodesic_endpoint_indices=np.array([0,32]),eeg_times_ms=times,eeg_bin_means_uV=values,
    displayed_repeat_means=np.array([means["GEO"],means["PCA"]]),
    displayed_absolute_means=np.array(absmeans))
assert before=={str(p):sha(p) for p in protected},"Protected source/result changed"
audit={"status":"EXISTING_EXAMPLE_REPLAY_MATCHES_ARCHIVED_DIAGNOSTICS",
       "date_local":"2026-10-21","selection_rule":"First original cohort 0, first source 6000, first target 6003; probe 0 highlighted; geodesic endpoints 0 and32. Not selected by performance.",
       "cohort":0,"world_seed":1800,"source_subject":ref,"target_subject":target,
       "probe_programs":[6000,6001,6002,6003],"probe_times":tt.tolist(),"probe_count":128,
       "rank":rank,"alignment":"Original input-assisted affine response-signature map; no true state or report labels in its fit",
       "replay":{"rho":rho,"coordinate_NRMSE":nrmse,"top5":top5},
       "archived_reference":{"rho":old_geo["rho"],"coordinate_NRMSE":old_match["normalized_coordinate_RMSE"],"top5":old_match["top5"]},
       "true_surface":{"formula":"(theta*cos(theta)/10, h, theta*sin(theta)/10)",
                      "theta_range_pi":[1.5,4.5],"height_range":[-1,1],
                      "geodesic_computation":"Straight line in (arc(theta),h); invert arc numerically",
                      "intrinsic_straight_line_max_error":intrinsic_error,
                      "not_an_estimated_Isomap_path":True},
       "EEG":{"source_npz":str(eeg),"subject":4,"recording":3,"row_index":ix,
              "onset_seconds":onset,"RT_seconds":rt,"channel":"Cz",
              "sampling_frequency":fs,"time_ms":times.tolist(),"bin_means_uV":values.tolist(),
              "representation":"Eight actual retained 0–200ms channel bin means; straight segments join points; not raw continuous EEG or a synthetic sine",
              "selection":"First quality/eligibility-passing target-tone trial in recording order"},
       "repeat_means":means,"absolute_means":{"GEO":absmeans[0],"PCA":absmeans[1]},
       "source_hashes":before,"figure_cache_sha256":sha(cache),
       "new_hypothesis_test":False,"new_experimental_condition":False,"deep_training":False,
       "original_files_modified":False,"LaTeX_compiled":False,
       "seconds":time.monotonic()-start}
(D/"EVIDENCE_REPLAY_AUDIT.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"status":audit["status"],"seconds":audit["seconds"],
                  "replayed_NRMSE":nrmse,"EEG_row":ix,"cache":str(cache)}),flush=True)
