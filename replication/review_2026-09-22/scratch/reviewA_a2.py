import sys, numpy as np, pandas as pd
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0,REPO+r"\src")
sys.dont_write_bytecode=True
from aidriver.preferences import PreferenceParams
from comfortzone.cutin import CZB_LANE_ENTRY_SHAPE_K
from rollout.belief import Belief, FLOORS_STUDY2
from rollout.predictor import sample_futures
from rollout.policies import CUTIN_MENU, ego_rollout
from rollout.efe import log_terms, g_by_policy, variant_params
df=pd.read_csv(REPO+r"\replication\czb\out\jj2_rollout_cutin_cells.csv")
print(df[["x_rel","y_rel","vy_oth","v_ego","v_oth","distance","dv_kph","ttc_true"]].describe().T.to_string())
p0=PreferenceParams(); print("veh len/wid",p0.vehicle.length,p0.vehicle.width)
def cell(r, L=4.5, W=1.8, show=True):
    b=Belief(x_rel=r.x_rel,y_rel=r.y_rel,v_ego=r.v_ego,v_oth=r.v_oth,vy_oth=r.vy_oth,sd_pos=FLOORS_STUDY2.sd_pos,sd_vy=FLOORS_STUDY2.sd_v_lat,p_change=r.p_change,ego_len=L,ego_wid=W,oth_len=L,oth_wid=W,vx_oth=r.v_oth-0.0)
    # vx_oth in freeze frame is world-frame rate since frame fixed
    fut=sample_futures(b,seed=0)
    paths={k:ego_rollout(b,k) for k in CUTIN_MENU}
    base=PreferenceParams(v_desired=b.v_ego,lane_entry_continuous=True,counterfactual_residual_severity=True,lane_entry_shape_k=CZB_LANE_ENTRY_SHAPE_K)
    out={}
    for k,pa in paths.items():
        t=log_terms(b,pa,fut,base)
        mx=base.max_log_preference()
        out[k]={n:float(-(v.mean(axis=0)).sum()) for n,v in t.items()}
        out[k]["G"]=float(np.maximum(mx-sum(t.values()).mean(axis=0),0).sum())
    return out
post=df[df.cp!="CP1"]
for idx in [post.distance.idxmin(), post.distance.idxmax(), post.dg_A.idxmin(), post.dg_A.idxmax()]:
    r=df.loc[idx]
    print("\n",r.video,"dist",r.distance,"dv",r.dv_kph,"ttc",r.ttc_true,"p",r.p,"x_rel",round(r.x_rel,2),"y_rel",round(r.y_rel,2),"vy",round(r.vy_oth,3))
    print(" CSV G:",{k:round(r["G_A_"+k]) for k in CUTIN_MENU},"dg_A",round(r.dg_A))
    o=cell(r)
    for k,v in o.items(): print("  ",k,{n:round(x) for n,x in v.items()})
