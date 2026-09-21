import sys, numpy as np, pandas as pd
sys.dont_write_bytecode=True
from scipy.stats import spearmanr
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0,REPO+r"\src")
from aidriver.preferences import PreferenceParams
from rollout.belief import Belief, FLOORS_STUDY2
from rollout.predictor import sample_futures
from rollout.policies import CUTIN_MENU, ego_rollout
from rollout.efe import g_by_policy
from rollout.boundary import delta_g
df=pd.read_csv(REPO+r"\replication\czb\out\jj2_rollout_cutin_cells.csv")
post=df[df.cp!="CP1"].reset_index(drop=True)
def run(params_fn):
    out=[]
    for r in post.itertuples():
        b=Belief(x_rel=r.x_rel,y_rel=r.y_rel,v_ego=r.v_ego,v_oth=r.v_oth,vy_oth=r.vy_oth,sd_pos=0.1,sd_vy=0.004,p_change=r.p_change,ego_len=4.5,ego_wid=1.8,oth_len=4.5,oth_wid=1.8,vx_oth=r.v_oth)
        fut=sample_futures(b,seed=0); paths={k:ego_rollout(b,k) for k in CUTIN_MENU}
        out.append(delta_g(g_by_policy(b,fut,paths,params_fn(b.v_ego))))
    return np.array(out)
def rows(x):
    d=post.copy(); d["_x"]=x
    rs=[spearmanr(g._x,g.p).statistic for _,g in d.groupby("ttc_true") if len(g)>=6]; return sum(r>0 for r in rs),len(rs)
staged=lambda v: PreferenceParams(v_desired=v,lane_entry_continuous=True,counterfactual_residual_severity=True,lane_entry_shape_k=12.0)
released=lambda v: PreferenceParams(v_desired=v)
for nm,fn in (("CZB staging (as JJ.2)",staged),("truly released flags",released)):
    x=run(fn); print(nm,"rho vs tracked dg_A",round(spearmanr(x,post.dg_A).statistic,4),"rho share",round(spearmanr(x,post.p).statistic,3),"rho gap",round(spearmanr(x,post.distance).statistic,3),"rows",rows(x),"zeros",(x<=0).sum())
print("post-onset sd log dg_A",np.log(post.dg_A).std(ddof=1).round(4))
