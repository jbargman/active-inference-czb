import numpy as np, pandas as pd
from scipy.stats import spearmanr, binomtest
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
d=pd.read_csv(REPO+r"\replication\czb\out\jj2b_steer_menu_cells.csv")
c=pd.read_csv(REPO+r"\replication\czb\out\cutin2_cells.csv")[["video","p","n","ttc_start","ttc_true","distance","dv_kph"]]
d=d.merge(c,on="video"); post=d[d.cp!="CP1"].reset_index(drop=True)
def rows(col,direction=1):
    rs=np.array([spearmanr(g[col],g.p).statistic for _,g in post.groupby("ttc_true") if len(g)>=6])
    return int((direction*rs>0).sum()),len(rs),round(float(rs.mean()),3),round(float(np.median(rs)),3), int((np.abs(rs)<0.3).sum())
for col in ["dg_menu","dg_steer","dg_planner","eps_continue"]:
    print(col,"rows(agree,n,mean rho,median rho,n |rho|<0.3)",rows(col),"rho share",round(spearmanr(post[col],post.p).statistic,3),"rho gap",round(spearmanr(post[col],post.distance).statistic,3),"zeros",int((d[col]<=0).sum()),"range",round(d[col].min()),round(d[col].median()),round(d[col].max()))
print(d.best.value_counts().to_dict(), d.best_steer.value_counts().to_dict(), "steers",d.steers.sum(),"brakes",d.brakes.sum(), "a_first med",d.a_first.median().round(3),"omega med",d.omega_max.median().round(3))
print("binom 19/24 p=",binomtest(19,24,0.5).pvalue)
