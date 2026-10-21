"""Translate four main research figures using audited, unchanged summary data.

No model fitting, new inference or LaTeX compilation is performed.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parent.parent
P=ROOT/"EEG_MAKALE"
D=P/"ingilizce_20261020"
F=P/"latex_makale/figures"
QA=D/"figure_qa"
QA.mkdir(exist_ok=True)
sp=P/"jnm_tam_revizyon_20261019/E48_E50_TAM_SONUC_OZETI.json"
rp=P/"jnm_tam_revizyon_20261019/E49_OPEN_EEG_SONUC_OZETI.json"
S=json.loads(sp.read_text(encoding="utf-8"))
R=json.loads(rp.read_text(encoding="utf-8"))
assert S["status"]=="COMPLETE_AUDITED"
lookup={(r["cell"],r["method"],r["budget"]):r for r in S["summary"]}
real={(r["method"],r["budget"]):r for r in R["summary"]}
audit={"purpose":"English labeling of existing figures; unchanged scores and CIs",
       "LaTeX_compiled":False,"new_simulations":False,
       "source_files":[{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in [sp,rp]],
       "figures":[]}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,
    "pdf.fonttype":42,"ps.fonttype":42,"axes.spines.top":False,
    "axes.spines.right":False,"axes.grid":True,"grid.alpha":.14,
    "axes.titlesize":11,"axes.labelsize":10})
COL={"GEO":"#245a81","GEO_WHITE":"#6696ac","PCA":"#d47727",
     "PCA_FULL":"#348873","RBF":"#805d9b"}
cells=["SWISS_ISO","SWISS_ANISO","CIRCLE_ISO","MASS_LEAD"]
titles=["Isometric surface","Anisotropic surface","Circle","Population + lead field"]

def save(fig,name,rows):
    pdf=F/(name+".pdf")
    fig.savefig(pdf,bbox_inches="tight",metadata={
        "Title":name,"Subject":"Existing audited results with English labels",
        "Creator":"Matplotlib; reproducible data visualization"})
    fig.savefig(QA/(name+".png"),dpi=160,bbox_inches="tight",facecolor="white")
    audit["figures"].append({"file":str(pdf),"sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),
                            "plotted_rows":rows})
    plt.close(fig)

def dot(ax,y,values,color,seed):
    rng=np.random.default_rng(seed)
    ax.scatter(values,y+rng.uniform(-.09,.09,len(values)),s=13,
               color=color,alpha=.30,linewidths=0)

def point(ax,y,mean,interval,color):
    assert interval[0] <= mean <= interval[1]
    ax.errorbar(mean,y,xerr=np.array([[mean-interval[0]],[interval[1]-mean]]),
                fmt="o",color=color,markersize=4.5,capsize=2.5,lw=1.35)

fig,ax=plt.subplots(figsize=(10,3.7))
ax.axis("off")
boxes=[
(.015,.49,.295,.39,"1  Geometry","True distances\nand representation distances"),
(.3525,.49,.295,.39,"2  Correspondence","Input-assisted map\nand true-correspondence reference"),
(.69,.49,.295,.39,"3  Prediction","Source decoder\nand target-label budget")]
for x,y,w,h,title,body in boxes:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.008",
        facecolor="#edf3f7",edgecolor=COL["GEO"],lw=1.1))
    ax.text(x+w/2,y+h*.76,title,ha="center",va="center",fontsize=11,weight="bold")
    ax.text(x+w/2,y+h*.36,body,ha="center",va="center",fontsize=9.6,linespacing=1.5)
ax.text(.5,.37,"Three endpoints; their relationships are tested separately.",
        ha="center",fontsize=10)
ax.text(.5,.22,"Simulations: known states and independent repetitions of the same inputs",
        ha="center",fontsize=10)
ax.text(.5,.07,"Open EEG: held-out subjects and recordings; measured response times",
        ha="center",fontsize=10)
save(fig,"en_fig01_framework",[])

methods=["GEO","GEO_WHITE","PCA","PCA_FULL","RBF"]
names={"GEO":"Isomap","GEO_WHITE":"Whitened Isomap","PCA":"Signal-rank PCA",
       "PCA_FULL":"Full PCA*","RBF":"Direct RBF"}
fig,axs=plt.subplots(2,2,figsize=(10,7.4),layout="constrained")
rows=[]
for panel,ax,cell,title in zip("ABCD",axs.flat,cells,titles):
    for y,method in enumerate(methods):
        rr=lookup[cell,method,0]
        assert len(rr["cohort_values"])==20
        dot(ax,y,rr["cohort_values"],COL[method],y)
        point(ax,y,rr["mean_R2"],rr["ci95"],COL[method])
        rows.append({k:rr[k] for k in ["cell","method","budget","mean_R2","ci95","cohort_values"]})
    ax.set_yticks(range(len(methods)),[names[m] for m in methods])
    ax.invert_yaxis()
    ax.axvline(0,color="black",ls=":",lw=.8)
    ax.set_title(panel+"  "+title,loc="left",pad=10)
    ax.set_xlabel("Between-repeat report-difference $R^2$\nNo target labels")
save(fig,"en_fig02_methods",rows)

fig,ax=plt.subplots(figsize=(8,4.8),layout="constrained")
rows=[]
for y,cell in enumerate(cells):
    for shift,method in [(-.19,"GEO"),(0,"PCA"),(.19,"PCA_FULL")]:
        rr=next(r for r in S["posthoc_global_probes"] if
            (r["cell"],r["method"],r["measure"])==(cell,method,"global128point_rho"))
        point(ax,y+shift,rr["mean_value"],rr["ci95"],COL[method])
        rows.append(rr)
ax.set_yticks(range(4),titles)
ax.invert_yaxis()
ax.set_xlabel(r"Spearman $\rho$ on 128 common probes")
for method,label in [("GEO","Isomap"),("PCA","Signal-rank PCA"),("PCA_FULL","Full PCA")]:
    ax.plot([],[],color=COL[method],marker="o",label=label)
ax.legend(frameon=False,loc="upper center",bbox_to_anchor=(.5,-.16),ncol=3)
save(fig,"en_fig03_distances",rows)

rnames={"GEO_INPUT":"Isomap, input-assisted","PCA_SHARED":"Shared PCA",
        "EA_RF":"Direct EA predictor","EA_RBF":"Direct EA/RBF",
        "CEBRA_EA":"CEBRA-input","IVAE_EA":"iVAE-input",
        "IPSID":"IPSID, trial history","RIEM":"Riemannian tangent",
        "INPUT_ONLY":"Input only","MEAN":"Available mean"}
fig,axs=plt.subplots(1,2,figsize=(10,5.2),layout="constrained")
rows=[]
for panel,ax,budget in zip("AB",axs,[0,32]):
    for y,method in enumerate(rnames):
        rr=real[method,budget]
        v=[r["logRT_R2"] for r in R["person_rows"] if r["method"]==method and r["budget"]==budget]
        assert len(v)==10
        dot(ax,y,v,COL["GEO"],y)
        point(ax,y,rr["mean_R2"],rr["ci95"],COL["GEO"])
        rows.append({"method":method,"budget":budget,"mean_R2":rr["mean_R2"],
                     "ci95":rr["ci95"],"person_values":v})
    ax.set_yticks(range(len(rnames)),list(rnames.values()))
    ax.invert_yaxis()
    ax.axvline(0,color="black",lw=.8,ls=":")
    ax.set_xlabel(r"Log response-time $R^2$")
    ax.set_title(panel+"  "+str(budget)+" target labels",loc="left",pad=10)
save(fig,"en_fig04_open_eeg",rows)
(D/"ENGLISH_FIGURE_AUDIT.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),
    encoding="utf-8")
print(json.dumps({"status":"FOUR_ENGLISH_FIGURES_SAVED","new_simulations":False,
                  "LaTeX_compiled":False,"figures":[r["file"] for r in audit["figures"]]}))
