import sys
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, REPO+r"\src")
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from aidriver.preferences import PreferenceParams, required_deceleration, residual_delta_v, log_safety_pref
sp=lambda a,b: round(float(spearmanr(a,b).statistic),3)
base=pd.read_csv("tt_base.csv")
meta=base[["video","cp","p","distance","dv_kph","ttc_true","ttc_start","v_ego","v_oth","x_rel","y_rel","lcd"]]
for nm in ["base","step","ramp_ref1e6","step_ref1e6"]:
    t=pd.read_csv(f"tt_{nm}.csv")[["video","collision","safety"]].merge(meta,on="video")
    post=t[t.cp!="CP1"]
    tot=post.collision+post.safety
    print(nm,"| safety range",round(t.safety.min(),1),round(t.safety.max(),1),"| rho(safety,p)",sp(post.safety,post.p),"rho(coll,p)",sp(post.collision,post.p),"rho(total,p)",sp(tot,post.p),"rho(total,gap)",sp(tot,post.distance),"| rho(safety,ttc_true)",sp(post.safety,post.ttc_true))
post=base[base.cp!="CP1"].copy()
# pointwise p_safe at the freeze, gate forced on (dy=0), released step and project ramp
L=4.2
for form in (False,True):
    P=PreferenceParams(counterfactual_residual_severity=form)
    obs=dict(v=post.v_ego.values,a=0.0,dx=post.distance.values+L,dy=0.0,v_other=post.v_oth.values,a_other=0.0)
    s=-log_safety_pref(obs,P)
    areq=-required_deceleration(obs,P)
    print("pointwise", "ramp" if form else "step", "rho(-logp_safe,p)",sp(s,post.p),"nonzero",int((s>0).sum()),"| rho(|a_req|,p)",sp(areq,post.p),"rho(|a_req|,gap)",sp(areq,post.distance))
    for dv,g in post.assign(s=s,areq=areq).groupby("dv_kph"):
        print("   dv",dv,"rho(s,p)",sp(g.s,g.p) if g.s.nunique()>1 else None,"rho(|a_req|,p)",sp(g.areq,g.p))
print("x_rel vs distance check:", (post.x_rel-post.distance).describe()[["min","max"]].to_dict())
# horizon-sum safety per pre-collision step
post["safety_per_ttc"]=post.safety/np.minimum(post.ttc_true,6.0)
print("rho(safety/min(ttc,6), p)",sp(post.safety_per_ttc,post.p),"rho(safety, min(ttc,6))",sp(post.safety,np.minimum(post.ttc_true,6)))
