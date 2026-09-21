import numpy as np, pandas as pd
from scipy.stats import spearmanr, norm
from scipy.optimize import minimize
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
df=pd.read_csv(REPO+r"\replication\czb\out\jj2_rollout_cutin_cells.csv")
print(df.columns.tolist()); print(len(df))
post=df[df.cp!="CP1"].reset_index(drop=True); cp1=df[df.cp=="CP1"].reset_index(drop=True)
print("zeros A",(df.dg_A<=0).sum(),"zeros B",(df.dg_B<=0).sum())
print("median",df.dg_A.median(),df.dg_B.median(), df.dg_A.min(), df.dg_A.max(), df.dg_B.max())
for c in ["dg_A","dg_B"]:
    print(c,"rho P",spearmanr(post[c],post.p).statistic,"rho dist",spearmanr(post[c],post.distance).statistic, "rho log", spearmanr(np.log(post[c]+1e-9),post.p).statistic)
print("rho P-distance",spearmanr(post.p,post.distance).statistic)
print(df.groupby("cp")[["dg_A","dg_B","p_change","p"]].describe().T.to_string())
print("p_change unique", np.unique(df.p_change.round(4)))
print(post[["dg_A"]].describe())
print(np.quantile(np.log(post.dg_A),[0,.05,.25,.5,.75,.95,1]))
# matched rows
def rows(col,direction):
    rs=[spearmanr(g[col],g.p).statistic for _,g in post.groupby("ttc_true") if len(g)>=6]
    return sum(direction*r>0 for r in rs),len(rs),np.mean(rs)
print("rows dg_A",rows("dg_A",1),"dg_B",rows("dg_B",1),"gap",rows("distance",-1))
# fit
def predict(th,x,s):
    b,c,ls=th; b=1/(1+np.exp(-b)); return b+(1-b)*norm.cdf(s*(x-c)/np.exp(ls))
def fit(x,y,w,s):
    lo,hi=np.quantile(x,[.1,.9]); sp=max(np.std(x),1e-6); best=None;bv=np.inf
    for c0 in np.linspace(lo,hi,5):
        for ls0 in (np.log(sp),np.log(sp/4+1e-9)):
            r=minimize(lambda th: float(np.sum(w*(predict(th,x,s)-y)**2)),np.array([-2.,c0,ls0]),method="L-BFGS-B")
            if r.fun<bv: best,bv=r.x,r.fun
    return best
def wr(y,p,w): return float(np.sqrt(np.average((p-y)**2,weights=w)))
def ho(x,s,d=post):
    y=d.p.to_numpy(float);w=d.n.to_numpy(float);f=d.ttc_start.to_numpy(float);pred=np.full_like(y,np.nan);ch=pred.copy()
    for k in np.unique(f):
        tr,te=f!=k,f==k; th=fit(x[tr],y[tr],w[tr],s); pred[te]=predict(th,x[te],s); ch[te]=np.average(y[tr],weights=w[tr])
    return wr(y,pred,w),wr(y,ch,w),pred
for c in ["dg_A","dg_B"]:
    x=np.log(post[c].to_numpy(float)+ (0 if (df[c]>0).all() else df[c][df[c]>0].min()/2))
    for s in (+1,-1):
        r,ch,pred=ho(x,s); print(c,"sign",s,"heldout",round(r,4),"chance",round(ch,4),"pred sd",pred.std().round(4), "pred range",pred.min().round(3),pred.max().round(3))
x=np.log(post.distance.to_numpy(float)); print("gap -1",ho(x,-1)[:2])
xa=np.log(post.dg_A.to_numpy(float)); th=fit(xa,post.p.to_numpy(float),post.n.to_numpy(float),1); print("full fit A theta",th, "pred post range",predict(th,xa,1).min(),predict(th,xa,1).max())
print("cp1 score", wr(cp1.p.to_numpy(float),predict(th,np.log(cp1.dg_A.to_numpy(float)),1),cp1.n.to_numpy(float)), "cp1 mean p",np.average(cp1.p,weights=cp1.n),"post mean p",np.average(post.p,weights=post.n))
