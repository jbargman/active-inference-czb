import numpy as np, pandas as pd
from scipy.stats import spearmanr
tt=pd.read_csv("tt_base.csv")
print(tt[["v_ego","v_oth"]].describe().loc[["min","max"]])
print(tt.groupby("dv_kph")[["v_ego","v_oth"]].mean())
post=tt[tt.cp!="CP1"]
sp=lambda a,b: spearmanr(a,b).statistic
for k in ["speed","accel","steer","lateral","collision","safety"]:
    print(k, "min/max", tt[k].min(), tt[k].max())
for nm,d in [("all378",tt),("post288",post)]:
    print(nm, "rho(coll,p)",sp(d.collision,d.p),"rho(safety,p)",sp(d.safety,d.p),"rho(coll,gap)",sp(d.collision,d.distance),"rho(safety,gap)",sp(d.safety,d.distance),
          "rho(safety,dv)",sp(d.safety,d.dv_kph),"rho(p,dv)",sp(d.p,d.dv_kph),"rho(p,ttc_true)",sp(d.p,d.ttc_true),"rho(gap,dv)",sp(d.distance,d.dv_kph))
print("safety zero count post", (post.safety.abs()<1e-9).sum(), "of", len(post))
# matched dv
print("--- matched dv (post): rho(safety,p), rho(safety,gap), rho(p,gap), n")
for dv,g in post.groupby("dv_kph"):
    print(dv, round(sp(g.safety,g.p),3), round(sp(g.safety,g.distance),3), round(sp(g.p,g.distance),3), len(g), "safety nonzero", (g.safety>1e-9).sum())
print("--- matched ttc_true rows (>=4 cells): rho(safety,p)")
rs=[]
for t,g in post.groupby("ttc_true"):
    if len(g)>=4 and g.safety.nunique()>1:
        rs.append((t,sp(g.safety,g.p),sp(g.safety,g.dv_kph),sp(g.p,g.dv_kph),len(g)))
print(pd.DataFrame(rs,columns=["ttc","rho_s_p","rho_s_dv","rho_p_dv","n"]).round(3).to_string())
# matched gap bins
post=post.copy(); post["gapbin"]=pd.qcut(post.distance,6)
print("--- matched gap sextiles: rho(safety,p), rho(safety,dv), rho(p,dv)")
for b,g in post.groupby("gapbin",observed=True):
    print(b, round(sp(g.safety,g.p),3), round(sp(g.safety,g.dv_kph),3), round(sp(g.p,g.dv_kph),3), len(g))
# partial spearman of safety,p given gap
from scipy.stats import rankdata
def partial(a,b,c):
    ra,rb,rc=[rankdata(x) for x in (a,b,c)]
    ea=ra-np.polyval(np.polyfit(rc,ra,1),rc); eb=rb-np.polyval(np.polyfit(rc,rb,1),rc)
    return np.corrcoef(ea,eb)[0,1]
print("partial rho(safety,p | gap)", partial(post.safety,post.p,post.distance))
print("partial rho(safety,p | dv)", partial(post.safety,post.p,post.dv_kph))
print("partial rho(safety,p | ttc_true)", partial(post.safety,post.p,post.ttc_true))
print("partial rho(collision,p | gap)", partial(post.collision,post.p,post.distance))
