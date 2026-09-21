import numpy as np, pandas as pd
from scipy.stats import spearmanr, norm
from scipy.optimize import minimize
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
d=pd.read_csv(REPO+r"\replication\czb\out\jj3_rollout_cells.csv")
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
def ho(x,y,w,f,s=1):
    pred=np.full_like(y,np.nan); ch=pred.copy()
    for k in np.unique(f):
        tr,te=f!=k,f==k; th=fit(x[tr],y[tr],w[tr],s); pred[te]=predict(th,x[te],s); ch[te]=np.average(y[tr],weights=w[tr])
    return round(wr(y,pred,w),4), round(wr(y,ch,w),4)
ov=d[d.scenario=="overtake"].reset_index(drop=True)
y,w=ov.p.to_numpy(float),ov.n.to_numpy(float)
ftp=pd.factorize(ov.timepoint)[0].astype(float); fcl=ov.clearance_m.to_numpy(float)
print("grand-mean chance",round(wr(y,np.full(len(y),np.average(y,weights=w)),w),4))
for v in "AB":
    x=np.log(ov["dg_"+v].to_numpy(float))
    print(v,"LOTO (model, fold-chance)",ho(x,y,w,ftp),"LOCO",ho(x,y,w,fcl), "rho dg-p",round(spearmanr(ov["dg_"+v],y).statistic,3))
xc=-np.log(fcl); print("clearance LOTO",ho(xc,y,w,ftp),"LOCO",ho(xc,y,w,fcl), "rho",round(spearmanr(xc,y).statistic,3))
print("rho dg_A vs clearance",spearmanr(ov.dg_A,ov.clearance_m).statistic)
# within clearance: does dG track timepoint / share?
for c,g in ov.groupby("clearance"): print(c,"rho(dg_A,p) within",round(spearmanr(g.dg_A,g.p).statistic,3))
lt=d[d.scenario=="ltap"].reset_index(drop=True)
print("ltap zeros",(lt.dg_A<=0).sum(),"of",len(lt))
dg=lt.dg_A.to_numpy(float); m=dg[dg>0].min(); x=np.log(dg+m/2)
print("ltap LOPO",ho(x,lt.p.to_numpy(float),lt.n.to_numpy(float),lt.pet.to_numpy(float)))
# G(proceed) alone as axis
print("ltap log G(proceed) LOPO",ho(np.log(lt.G_A_proceed.to_numpy(float)),lt.p.to_numpy(float),lt.n.to_numpy(float),lt.pet.to_numpy(float)), "rho",spearmanr(lt.G_A_proceed,lt.p).statistic)
dl=pd.read_csv(REPO+r"\replication\czb\out\jj3_driver_levels.csv"); print(dl.columns.tolist(), len(dl))
num=[c for c in dl.columns if dl[c].dtype!=object]
print(dl[num].corr(method="spearman").round(3).to_string())
print(dl[num].describe().T.to_string())
