"""Vector graphical abstract tied to the implemented geometry and retained data.

No generative image model. No new scientific condition, fit selection, or test.
One frozen example is replayed and validated by prepare_graphical_evidence.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import numpy as np
import fitz
from reportlab import rl_config
from reportlab.graphics import renderPDF,renderSVG
from reportlab.graphics.shapes import Drawing,Line,Circle,Rect,String,Polygon,PolyLine,STATE_DEFAULTS
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import registerFont,stringWidth
from reportlab.pdfbase.ttfonts import TTFont

H=Path(__file__).resolve().parent
P=H.parent/"EEG_MAKALE"
D=P/"grafik_ozet_dogrulama_20261021"
assert shutil.disk_usage(P).free>3*1024**3+512*1024**2
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((D/"EVIDENCE_REPLAY_AUDIT.json").read_text(encoding="utf-8"))
cache=D/"GRAPHIC_NUMERIC_INPUTS.npz"
assert sha(cache)==audit["figure_cache_sha256"]
for path,expected in audit["source_hashes"].items():
    assert sha(Path(path))==expected,path
with np.load(cache,allow_pickle=False) as f:V={k:f[k].copy() for k in f.files}
registerFont(TTFont("EditorialSans",r"C:\Windows\Fonts\arial.ttf"))
registerFont(TTFont("EditorialSansBold",r"C:\Windows\Fonts\arialbd.ttf"))
registerFont(TTFont("EditorialSerif",r"C:\Windows\Fonts\georgia.ttf"))
registerFont(TTFont("EditorialSerifItalic",r"C:\Windows\Fonts\georgiai.ttf"))
rl_config.canvas_basefontname="EditorialSans"
STATE_DEFAULTS["fontName"]="EditorialSans"
W,HGT=780,448
d=Drawing(W,HGT)
C={"ink":"#243039","muted":"#627079","line":"#D8DFE2","mesh":"#A6B6BD",
   "paper":"#FFFFFF","sheet":"#F0F3F4","blue":"#285B70","copper":"#B36E51",
   "pale":"#F7F8F8"}
def col(s):return HexColor(C.get(s,s))
bounds=[]
def text(x,y,s,size=14,color="ink",font="EditorialSans",anchor="start"):
    width=stringWidth(s,font,size)
    left=x if anchor=="start" else x-width/2 if anchor=="middle" else x-width
    assert 0<=left and left+width<=W,(s,left,width)
    bounds.append({"text":s,"x":left,"y":y,"width":width,"size":size,"font":font})
    d.add(String(x,y,s,fontName=font,fontSize=size,fillColor=col(color),textAnchor=anchor))
def mathtext(x,y,parts,size=16,color="ink",anchor="middle"):
    # Each tuple is (string, relative font size, relative baseline).
    widths=[stringWidth(s,"EditorialSerifItalic",size*scale) for s,scale,offset in parts]
    total=sum(widths)
    xx=x-total/2 if anchor=="middle" else x
    for (s,scale,offset),width in zip(parts,widths):
        text(xx,y+size*offset,s,size*scale,color,"EditorialSerifItalic")
        xx+=width
def line(x1,y1,x2,y2,color="line",lw=.8,dash=None):
    d.add(Line(x1,y1,x2,y2,strokeColor=col(color),strokeWidth=lw,
               strokeDashArray=dash,strokeLineCap=1))
def path(points,color="ink",lw=1,dash=None):
    d.add(PolyLine(np.asarray(points).flatten().tolist(),strokeColor=col(color),
                  fillColor=None,strokeWidth=lw,strokeDashArray=dash,strokeLineCap=1))
def dot(x,y,r=3.5,color="blue",fill=True,lw=1.3):
    d.add(Circle(float(x),float(y),r,fillColor=col(color) if fill else col("paper"),
                 strokeColor=None if fill else col(color),strokeWidth=lw))
def arrow(x1,y1,x2,y2,color="muted",lw=1,head=4):
    line(x1,y1,x2,y2,color,lw)
    a=math.atan2(y2-y1,x2-x1)
    d.add(Polygon([x2,y2,x2-head*math.cos(a-.5),y2-head*math.sin(a-.5),
                   x2-head*math.cos(a+.5),y2-head*math.sin(a+.5)],
                  fillColor=col(color),strokeColor=None))

# Panel a is the EXACT generator embedding, with an orthographic display camera.
# Its highlighted curve is the known intrinsic geodesic between actual probes.
theta=np.linspace(1.5*np.pi,4.5*np.pi,180)
ts=np.linspace(1.5*np.pi,4.5*np.pi,17)
hs=np.linspace(-1,1,7)
def phi(t,h):
    return np.column_stack([t*np.cos(t)/10,h,t*np.sin(t)/10])
az,el=np.deg2rad([32,34])
camera=np.array([[np.cos(az),0,-np.sin(az)],
                 [-np.sin(az)*np.sin(el),np.cos(el),-np.cos(az)*np.sin(el)]])
assert np.allclose(camera@camera.T,np.eye(2),atol=1e-14)
corners=phi(np.tile(theta,2),np.repeat([-1.,1.],len(theta)))@camera.T
lo,hi=corners.min(0),corners.max(0)
scale=min(225/(hi[0]-lo[0]),111/(hi[1]-lo[1]))
def project3(xyz):
    return (np.asarray(xyz)@camera.T-(lo+hi)/2)*scale+np.array([140,269.5])
def screen(t,h):return project3(phi(np.asarray(t),np.asarray(h)))

d.add(Rect(0,0,W,HGT,fillColor=col("paper"),strokeColor=None))
text(28,416,"Geometry, correspondence and prediction",26,font="EditorialSerif")
text(29,391,"Controlled surface example and open auditory EEG",14.5,"muted")
line(28,375,752,375,"line",.7)
for x,letter,title in [(28,"a","Geometry"),(286,"b","Correspondence"),(552,"c","Prediction")]:
    text(x,350,letter,15,"muted","EditorialSerifItalic")
    text(x+20,350,title,18,font="EditorialSansBold")

for i in range(len(ts)-1):
    poly=screen(np.array([ts[i],ts[i+1],ts[i+1],ts[i]]),np.array([-1,-1,1,1]))
    d.add(Polygon(poly.flatten().tolist(),fillColor=col("sheet"),strokeColor=None))
for h in hs:path(screen(theta,np.repeat(h,len(theta))),"mesh",.55)
for t in ts:path(screen(np.array([t,t]),np.array([-1.,1.])),"mesh",.55)
for h in [-1,1]:path(screen(theta,np.repeat(h,len(theta))),"mesh",.9)
gp=project3(V["true_geodesic_xyz"])
path(gp,"blue",2.1)
for q in [gp[0],gp[-1]]:dot(*q,r=3.5,fill=False,lw=1.5)
text(140,199,"Known folded surface",14.2,anchor="middle")
text(140,180,"True intrinsic geodesic",12.4,"muted",anchor="middle")

# Panel b: reconstructed original Isomap coordinates and the original fitted
# input-assisted affine map. One common isotropic display transform; no Procrustes
# adjustment, manual rotation, rescaling each cloud, or visually selected pair.
src=V["source_coordinates"]
tgt=V["target_mapped_coordinates"]
both=np.r_[src,tgt]
lo2,hi2=both.min(0),both.max(0)
scale2=min(204/(hi2[0]-lo2[0]),106/(hi2[1]-lo2[1]))
def project2(z):
    return (z-(lo2+hi2)/2)*scale2+np.array([405,269])
a,b=project2(src),project2(tgt)
for q in b:dot(*q,r=1.65,fill=False,lw=.65)
for q in a:dot(*q,r=1.5)
chosen=0
line(*a[chosen],*b[chosen],"ink",1.1,[3,2])
dot(*a[chosen],r=4.0)
dot(*b[chosen],r=4.0,fill=False,lw=1.6)
dot(302,337,r=2.3)
text(310,332,"Source",11.8)
dot(393,337,r=2.3,fill=False,lw=1)
text(401,332,"Mapped target",11.8)
text(405,199,"Isomap + input-assisted map",13.6,anchor="middle")
text(405,180,"First cohort · 128 common probes",11.8,"muted",anchor="middle")

# Panel c: the implemented feature/history-based decoder and additive residual
# calibration, including vector outputs. b denotes the target-report budget.
dot(561,280,r=3.7)
mathtext(561,257,[("H, U",1,0)],size=16)
arrow(573,280,587,280,"muted",1.1)
d.add(Rect(591,257,40,47,fillColor=col("pale"),strokeColor=col("muted"),strokeWidth=.8))
mathtext(611,273,[("f",1,0),("s",.6,-.22)],size=26)
arrow(637,280,652,280,"muted",1.1,3)
text(644,295,"p",13.7,font="EditorialSerifItalic",anchor="middle")
d.add(Rect(658,260,85,40,fillColor=col("paper"),strokeColor=col("muted"),strokeWidth=.8))
mathtext(700.5,274,[("p + ê",1,0),("b",.62,-.22),("(p)",1,0)],size=15.4)
arrow(748,280,757,280,"muted",1,2.5)
mathtext(758,255,[("ŷ",1,0),("b",.62,-.22)],size=18)
text(611,320,"Source decoder",12.2,"muted",anchor="middle")
arrow(700,230,700,252,"muted",.9,3.5)
text(700,216,"Target reports",12.1,"muted",anchor="middle")
text(700,198,"b = 0, 12, 48",12.1,"muted",anchor="middle")
text(650,180,"Residual output calibration",13.2,anchor="middle")

line(28,163,752,163,"line",.7)
text(28,140,"Isometric surface",16.5,font="EditorialSansBold")
text(28,118,"20 cohorts · no target labels",12.5,"muted")
dot(288,143,r=3.4)
text(298,138,"Isomap",12.5)
dot(379,143,r=3.4,color="copper")
text(389,138,"PCA",12.5)
text(28,83,"Between-repeat R²",14)
text(28,41,"Absolute-output R²",14)
xf=lambda v:185+275*v/.45
for y,values in [(87,V["displayed_repeat_means"]),(45,V["displayed_absolute_means"])]:
    x1,x2=map(xf,values)
    line(x1,y,x2,y,"mesh",1.3)
    for xx,val,color in [(x1,values[0],"blue"),(x2,values[1],"copper")]:
        dot(xx,y,r=4,color=color)
        text(xx,y+10,f"{val:.3f}",15,color,anchor="middle")

line(499,25,499,145,"line",.7)
text(521,140,"Open auditory EEG",16.5,font="EditorialSansBold")
text(521,118,"3 sources → 10 targets",12.5,"muted")
times=V["eeg_times_ms"];values=V["eeg_bin_means_uV"]
eeg_scale=12/max(float(np.max(abs(values))),1e-12)
trace=np.c_[523+times/200*97,84+values*eeg_scale]
line(523,84,620,84,"line",.5)
path(trace,"blue",1.2)
for q in trace:dot(*q,r=1.5)
text(570,62,"Cz · 0–200 ms",11.6,"muted",anchor="middle")
arrow(630,84,661,84,"muted",1)
d.add(Circle(688,84,15,fillColor=None,strokeColor=col("ink"),strokeWidth=1.1))
line(688,84,688,94,"ink",1.1)
line(688,84,695,81,"ink",1.1)
text(717,79,"RT",15.3)
text(521,29,"No reliable transfer gain",14.8,font="EditorialSansBold")

pdf=D/"graphical_abstract.pdf"
svg=D/"graphical_abstract.svg"
png=D/"graphical_abstract.png"
renderPDF.drawToFile(d,str(pdf),title="Geometry, correspondence and prediction",author="")
renderSVG.drawToFile(d,str(svg))
s=svg.read_text(encoding="utf-8")
s=s.replace("font-family: EditorialSansBold;","font-family: Arial; font-weight: bold;")
s=s.replace("font-family: EditorialSerifItalic;","font-family: Georgia; font-style: italic;")
s=s.replace("EditorialSans","Arial").replace("EditorialSerif","Georgia")
svg.write_text(s,encoding="utf-8")
fonts=[]
with fitz.open(pdf) as doc:
    assert len(doc)==1
    txt=doc[0].get_text()
    for val in ["0.392","0.168","0.222","0.382"]:assert val in txt
    for f in doc[0].get_fonts(full=True):
        fonts.append({"name":f[3],"embedded":bool(doc.extract_font(f[0])[3])})
    assert all(f["embedded"] for f in fonts)
    doc[0].get_pixmap(matrix=fitz.Matrix(4,4),alpha=False).save(png)
    sc=13/2.54*150/W
    doc[0].get_pixmap(matrix=fitz.Matrix(sc,sc),alpha=False).save(D/"review_at_13cm_150dpi.png")

caption=(
    "Graphical abstract. (a) The implemented folded-surface generator is "
    "phi(theta,h)=(theta cos(theta)/10,h,theta sin(theta)/10), with theta in "
    "[1.5pi,4.5pi] and h in [-1,1]. The surface is shown by orthographic projection. "
    "The highlighted curve is the true intrinsic geodesic between fixed common "
    "probes 0 and 32, computed as a straight line in (arc(theta),h) and mapped back "
    "to the surface; it is not a path recovered by Isomap. "
    "(b) Actual reconstructed two-dimensional Isomap coordinates for the first "
    "original isometric cohort (seed 1800), first source (6000) and first target "
    "(6003). Filled circles are source coordinates; open circles are target "
    "coordinates after the original input-assisted affine map. The same display "
    "translation and isotropic scale apply to both. The dashed segment connects "
    "the same fixed probe 0; state truth is used only for this diagnostic pairing, "
    "not to fit the learned map. All 128 common-state probes are shown; the example "
    "was fixed by cohort/person order rather than performance. Replayed rho, "
    "coordinate NRMSE and top-five retrieval match the archived diagnostic. "
    "(c) H is the history of aligned observation representations, U is known input "
    "history, and p=f_s(H,U) is the fixed source decoder prediction. Target budget "
    "b fits the implemented affine residual correction, yielding "
    "yhat_b=p+ehat_b(p); ehat_0=0. Simulation budgets are 0/12/48; the EEG analysis "
    "used 0/12/32. The scalar drawing denotes a vector-capable correction; it does "
    "not replace the regularized residual fit by an independently fitted direct affine model. "
    "Lower left: unchanged descriptive means from the initial 20-cohort isometric "
    "analysis, two targets averaged per cohort and no target reports. Blue: Isomap; "
    "copper: signal-rank PCA. Both rows use the same 0–0.45 R² display scale. "
    "Lower right: the eight actual retained Cz bin means from the first eligible "
    "target-tone trial of OpenNeuro ds003061 v1.1.2 subject 004, recording 3 "
    "(row 23); straight lines join bin centers. This is not raw continuous EEG or "
    "a synthetic waveform. The vertical display scale is linear; time is in ms. "
    "The three-source/ten-target response-time result concerns the previously "
    "reported full analysis, not this illustrative trial. Clock and operator "
    "symbols encode the analysis rather than experimental observations. "
    "AI-assisted reproducible drawing code was used; no generative image model. "
    "Human author approval remains pending.\n")
(D/"TECHNICAL_FIGURE_PROVENANCE.txt").write_text(caption,encoding="utf-8")
short_caption=(
    "Graphical abstract. (a) The implemented folded surface and its true intrinsic "
    "geodesic, shown in orthographic projection. (b) Reconstructed Isomap coordinates "
    "and input-assisted affine alignment for the fixed first isometric cohort. "
    "Filled/open circles indicate source/mapped target; the dashed segment links "
    "one common-state probe, using truth only for evaluation. (c) The source decoder "
    "uses aligned representation and known-input histories (H,U); target reports "
    "fit an additive affine residual correction. Lower panels show the original "
    "20-cohort isometric means without target reports (Isomap versus signal-rank "
    "PCA), and eight retained Cz bin means from one held-out EEG trial. The surface "
    "is simulated; the EEG features are measured. AI-assisted reproducible drawing "
    "code was used; no generative image model.\n")
(D/"graphical_abstract_caption.txt").write_text(short_caption,encoding="utf-8")
provenance={
    "status":"DRAWN_FROM_IMPLEMENTED_EQUATIONS_AND_CHECKED_EXAMPLE",
    "date_local":"2026-10-21","language":"English",
    "source_main_sha256":sha(P/"latex_makale/main.tex"),
    "evidence_audit_sha256":sha(D/"EVIDENCE_REPLAY_AUDIT.json"),
    "cache_sha256":sha(cache),"drawing_code_sha256":sha(Path(__file__)),
    "panel_a":"Exact generator mesh; known intrinsic geodesic, not an inferred biological surface",
    "panel_b":"Original learned coordinates/map replayed; fixed first cohort/persons; no illustrative camera transformations",
    "panel_b_display":{"isotropic_scale":float(scale2),"common_center":((lo2+hi2)/2).tolist(),"highlight_probe":0},
    "panel_c":"Exact feature-history decoder and additive affine residual calibration; vector-capable",
    "EEG_trace":"Actual saved Cz bin means; no generated sine",
    "EEG_vertical_scale_pt_per_uV":eeg_scale,"displayed_EEG_points":trace.tolist(),
    "generative_image_model_used":False,"AI_assisted_drawing_code":True,
    "new_experimental_condition":False,"new_hypothesis_test":False,"LaTeX_compiled":False,
    "page_points":[W,HGT],"preview_pixels":[W*4,HGT*4],"fonts":fonts,"text_bounds":bounds,
    "files":{p.name:sha(p) for p in [pdf,svg,png,D/"graphical_abstract_caption.txt",
                                    D/"TECHNICAL_FIGURE_PROVENANCE.txt"]}}
(D/"GRAPHICAL_ABSTRACT_PROVENANCE.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"status":provenance["status"],"pdf":str(pdf),"png":str(png),
                  "LaTeX_compiled":False,"fonts_embedded":True}))
