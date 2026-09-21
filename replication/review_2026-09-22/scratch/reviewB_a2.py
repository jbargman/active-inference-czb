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
lev=b.level.to_numpy(float); cls=b.cls.to_numpy(int); cell=b.cell.to_numpy(int)
codes = pd.factorize(b.driver)[0]
f1=J4.fit_gauss(lev,cls,cell,codes,False); f2=J4.fit_gauss(lev,cls,cell,codes,True)
print("sd shared", f1["sd"], "two", f2["sd"])
# reproduce 15-fold
drivers=np.sort(b.driver.unique()); rng=np.random.default_rng(J4.SEED)
folds=list(rng.permutation(drivers)[:15])
def per_driver(held_list):
    out=[]
    for held in held_list:
        tr=b[b.driver!=held]; c=pd.factorize(tr.driver)[0]
        h=b[b.driver==held]
        r=[]
        for two in (False,True):
            f=J4.fit_gauss(tr.level.to_numpy(float),tr.cls.to_numpy(int),tr.cell.to_numpy(int),c,two)
            r.append(J4.loglik_driver(h.level.to_numpy(float),h.cls.to_numpy(int),h.cell.to_numpy(int),f))
        out.append((held,len(h),r[0],r[1],r[1]-r[0]))
    return pd.DataFrame(out,columns=["driver","n","ll1","ll2","d"])
allp=per_driver(list(drivers))
allp.to_csv("jj4_perdriver.csv",index=False)
sub=allp[allp.driver.isin(folds)]
print("15-fold: ll1",sub.ll1.sum(),"ll2",sub.ll2.sum(),"diff",sub.d.sum())
print("all 43: diff",allp.d.sum(), "n pos",(allp.d>0).sum(),"n neg",(allp.d<0).sum())
print(allp.d.describe())
print(allp.sort_values("d").head(6)); print(allp.sort_values("d").tail(6))
d=allp.d.to_numpy(); bs=[d[rng.integers(0,43,43)].sum() for _ in range(4000)]
print("bootstrap over drivers, sum over 43:",np.percentile(bs,[2.5,97.5]))
d15=sub.d.to_numpy(); bs=[d15[rng.integers(0,15,15)].sum() for _ in range(4000)]
print("bootstrap 15:",np.percentile(bs,[2.5,97.5]), "npos15",(d15>0).sum())
# residual shape / outliers
m=f2["driver_mean"][codes]; r=lev-m-f2["offset"][cell]
from scipy import stats
for k in (0,1):
    rk=r[cls==k]; print("class",k,"sd",rk.std(),"MAD*1.4826",stats.median_abs_deviation(rk)*1.4826,"kurt",stats.kurtosis(rk),"IQR/1.349",(np.percentile(rk,75)-np.percentile(rk,25))/1.349,"frac |r|>3sd",np.mean(np.abs(rk)>3*rk.std()))
# per-cell: residual sd, and press time sd, slope of x_loom at median press
b["res"]=r
rows=[]
for (scn,lab),g in b.groupby(["scenario","criticality_label"]):
    stem=("CutInCar" if scn=="cutin_car" else "CutInTruck")+f"_{lab[3:]}TTC"
    p=KIN_BUTTON/f"{stem}_vehicle_states.csv"
    f=F.looming_field(p); tr=load_cutin_trace(p)
    t=f.t.to_numpy(); x=f.x_loom.to_numpy()
    tp=BUTTON_CLIP_START_S+g.press_time_s.to_numpy(float)
    q25,q50,q75=np.percentile(tp,[25,50,75])
    xi=lambda tt: np.interp(tt,t[np.isfinite(x)],x[np.isfinite(x)])
    slope=(xi(q75)-xi(q25))/(q75-q25)
    # driver-demeaned press-time sd
    gt=g.assign(tp=tp)
    rows.append(dict(cell=stem,n=len(g),onset=float(tr.t[tr.onset_idx]),t_med=q50,press_sd=tp.std(),
        press_iqr=q75-q25,slope_q=slope,res_sd=g.res.std(),res_mad=stats.median_abs_deviation(g.res)*1.4826,
        frac_pre_onset=np.mean(tp<float(tr.t[tr.onset_idx])), w=f.attrs["w_tar"], dt=np.median(np.diff(t)), tmax=t.max(), n_nonfinite=int((~np.isfinite(x)).sum())))
print(pd.DataFrame(rows).round(3).to_string())
