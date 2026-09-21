import sys, os
import numpy as np, pandas as pd
R = r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, R + r"\replication\czb"); sys.path.insert(0, R + r"\src")
os.chdir(os.environ["SCR"])
from generative.uncertainty import cv_prediction_errors, fit_growth, fit_growth_accel, growth_residual
import gm1a_lead_acceleration as G
d=G.load_scenarios()
H=G.HORIZONS
def wsd(vals,ws):
    flat=np.concatenate(vals); wv=np.concatenate([np.full(len(v),w) for v,w in zip(vals,ws)])
    mu=np.average(flat,weights=wv); return np.sqrt(np.average((flat-mu)**2,weights=wv))
def forms(sd):
    s0l,s1=fit_growth(H,sd); s0q,sa=fit_growth_accel(H,sd)
    return dict(s1=s1,sigma_a=sa,s0q=s0q,r_lin=growth_residual(H,sd,s0l,s1,False),r_quad=growth_residual(H,sd,s0q,sa,True))
A=-0.5
modes={"card":[], "fixed_origins":[], "future_unconditioned":[]}
W={k:[] for k in modes}
zero=[];tot=0
for sid,g in d.groupby("id",sort=False):
    t=g.t.to_numpy(float); v=g.v_l.to_numpy(float); w=float(g.weight.iloc[0])
    x=np.concatenate([[0.0],np.cumsum(0.5*(v[1:]+v[:-1])*np.diff(t))])
    k=G.phase_split(t,v,A)
    if k>=G.MIN_SAMPLES:
        e=cv_prediction_errors(t[:k],x[:k],np.zeros(k),H,window_s=0.3); modes["card"].append(e); W["card"].append(w)
        # fixed origins: only origins valid at the 3 s horizon, used at every horizon
        n3=len(e[3.0][0])
        if n3>0:
            modes["fixed_origins"].append({h:(e[h][0][:n3],e[h][1][:n3]) for h in H}); W["fixed_origins"].append(w)
        # origins in benign phase, targets anywhere in the scenario
        ef=cv_prediction_errors(t,x,np.zeros(len(t)),H,window_s=0.3)
        # origins valid: index< k and velocity finite; cv_prediction_errors drops invalid so recompute mask manually
        from generative.uncertainty import backward_velocity
        vx=backward_velocity(t,x,0.3); out={}
        for h in H:
            kk=np.searchsorted(t,t+h-1e-9); ok=(kk<len(t))&np.isfinite(vx)&(np.arange(len(t))<k)
            k2=np.where(ok,kk,0); ex=x[k2]-(x+vx*h); out[h]=(ex[ok],ex[ok]*0)
        modes["future_unconditioned"].append(out); W["future_unconditioned"].append(w)
for name,per in modes.items():
    sd=[wsd([p[h][0] for p in per if len(p[h][0])],[w for p,w in zip(per,W[name]) if len(p[h][0])]) for h in H]
    n=[sum(len(p[h][0]) for p in per) for h in H]
    print(name,"n_scen",len(per),"n",n); print("   wsd",np.round(sd,3)); print("   ",{k:round(v,4) for k,v in forms(sd).items()})
    if name=="card":
        e3=np.concatenate([p[2.5][0] for p in per]); print("   frac |err@2.5s|<1mm:",np.mean(np.abs(e3)<1e-3), "kurtosis-ish: sd",e3.std(),"q99",np.quantile(np.abs(e3),0.99))
        # scenario bootstrap of card estimate
        rng=np.random.default_rng(1); res=[]
        idx=np.arange(len(per))
        for _ in range(200):
            ii=rng.integers(0,len(per),len(per))
            sdb=[wsd([per[i][h][0] for i in ii if len(per[i][h][0])],[W[name][i] for i in ii if len(per[i][h][0])]) for h in H]
            f=forms(sdb); res.append((f["sigma_a"],f["r_lin"]<f["r_quad"]))
        res=np.array(res,float); print("   scenario bootstrap sigma_a 95%:",np.percentile(res[:,0],[2.5,97.5]),"P(linear wins)",res[:,1].mean())
# how synthetic: distribution of benign accelerations
a_all=[]
for sid,g in d.groupby("id",sort=False):
    t=g.t.to_numpy(float); v=g.v_l.to_numpy(float); a_all.append(np.gradient(v,t))
a=np.concatenate(a_all); print("all accel: frac |a|<1e-6",np.mean(np.abs(a)<1e-6),"frac |a|<0.01",np.mean(np.abs(a)<0.01),"sd all",a.std())
w=d.groupby("id").weight.first(); print("weights: min/med/max",w.min(),w.median(),w.max(),"eff n",w.sum()**2/(w**2).sum())
