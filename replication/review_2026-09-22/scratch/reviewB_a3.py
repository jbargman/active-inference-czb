import sys, os
import numpy as np, pandas as pd
R = r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, R + r"\replication\czb"); sys.path.insert(0, R + r"\src")
os.chdir(os.environ["SCR"])
import jj4_precision_spread as J4
import fit_stage1_looming as F
from comfortzone.czb_data import BUTTON_CLIP_START_S, KIN_BUTTON
from comfortzone.cutin import load_cutin_trace
b = pd.read_pickle("press_levels.pkl")
on={}; flds={}
for (scn,lab),g in b.groupby(["scenario","criticality_label"]):
    stem=("CutInCar" if scn=="cutin_car" else "CutInTruck")+f"_{lab[3:]}TTC"
    p=KIN_BUTTON/f"{stem}_vehicle_states.csv"; tr=load_cutin_trace(p)
    on[(scn,lab)]=float(tr.t[tr.onset_idx]); flds[(scn,lab)]=F.looming_field(p)
b["t_on"]=[BUTTON_CLIP_START_S+pt-on[(s,l)] for s,l,pt in zip(b.scenario,b.criticality_label,b.press_time_s)]
def getcol(col):
    out=[]
    for s,l,pt in zip(b.scenario,b.criticality_label,b.press_time_s):
        f=flds[(s,l)]; i=int(np.clip(np.searchsorted(f.t.to_numpy(),BUTTON_CLIP_START_S+pt,side="right")-1,0,len(f)-1))
        out.append(float(f[col].iloc[i]))
    return np.array(out)
b["gap"]=getcol("gap_m"); b["vrel"]=getcol("v_rel")
with np.errstate(all="ignore"):
    b["logttc"]=np.log(b.gap/b.vrel); b["loggap"]=np.log(b.gap)
def run(sub,col,label):
    sub=sub[np.isfinite(sub[col])]
    codes=pd.factorize(sub.driver)[0]
    lev=sub[col].to_numpy(float); cls=sub.cls.to_numpy(int); cell=sub.cell.to_numpy(int)
    f2=J4.fit_gauss(lev,cls,cell,codes,True)
    drivers=np.sort(b.driver.unique()); rng=np.random.default_rng(J4.SEED)
    folds=list(rng.permutation(drivers)[:15])
    s2=sub.assign(level=lev)
    d=J4.lopo_gauss(s2,True,folds)-J4.lopo_gauss(s2,False,folds)
    print(f"{label:40s} n={len(sub)} sd car {f2['sd'][0]:.4f} truck {f2['sd'][1]:.4f} ratio {f2['sd'][1]/f2['sd'][0]:.2f}  LOPO15 diff {d:+.2f}")
run(b,"level","log theta_dot, all (card)")
run(b,"t_on","press time since onset [s], all")
run(b,"logttc","log TTC at press, all")
run(b,"loggap","log gap at press, all")
post=b[b.t_on>0]
run(post,"level","log theta_dot, post-onset presses")
run(post,"t_on","press time since onset, post-onset")
post2=b[b.t_on>0.3]
run(post2,"level","log theta_dot, >0.3s after onset")
print(b.groupby("cls").t_on.describe())
# clip kinematics at onset
for k,f in flds.items():
    t=f.t.to_numpy(); i=np.searchsorted(t,on[k]); 
    print(k, "gap@onset %.1f vrel %.2f  TTC %.2f ; +2s gap %.1f vrel %.2f"%(f.gap_m.iloc[i],f.v_rel.iloc[i],f.gap_m.iloc[i]/f.v_rel.iloc[i],f.gap_m.iloc[min(i+20,len(f)-1)],f.v_rel.iloc[min(i+20,len(f)-1)]))
