import numpy as np, pandas as pd
from scipy.stats import spearmanr
sp=lambda a,b: round(float(spearmanr(a,b).statistic),3)
base=pd.read_csv("tt_base.csv")
meta=base[["video","cp","p","distance","dv_kph","ttc_true","ttc_start","lcd"]]
for nm in ["base","step"]:
    t=pd.read_csv(f"tt_{nm}.csv")[["video","collision","safety"]].merge(meta,on="video")
    post=t[t.cp!="CP1"].copy(); post["tot"]=post.collision+post.safety
    print(nm)
    for dv,g in post.groupby("dv_kph"):
        print("  dv",dv,"rho(tot,p)",sp(g.tot,g.p),"rho(coll,p)",sp(g.collision,g.p),"rho(safety,p)",sp(g.safety,g.p),"rho(safety,ttc)",sp(g.safety,g.ttc_true),"rho(p,ttc)",sp(g.p,g.ttc_true))
    # matched ttc_true rows
    rs=[(sp(g.tot,g.p),sp(g.collision,g.p),sp(g.safety,g.p)) for _,g in post.groupby("ttc_true") if len(g)>=4]
    a=np.array(rs); print("  matched-ttc rows ordered like data: total",(a[:,0]>0).sum(),"coll",(a[:,1]>0).sum(),"safety",(a[:,2]>0).sum(),"of",len(a))
    # safety per unit time
    print("  mean safety by ttc_true bin:"); print(post.groupby(pd.cut(post.ttc_true,[0,1.5,2.5,3.5,4.5,7]),observed=True).safety.mean().round(0).to_dict())
