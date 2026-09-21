import sys, os, dataclasses
import numpy as np, pandas as pd
R = r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, R + r"\replication\czb"); sys.path.insert(0, R + r"\src")
os.chdir(os.environ["SCR"])
import fit_stage1_looming as F, ltapod_testtrack as TT
from comfortzone.czb_data import load_joint
j=load_joint()
v=j[(j.design=="Random")&(j.scenario=="ltap")&(j.ltap_speed==50)&j.intervene.notna()].copy()
v["pet"]=v.criticality_label.str.replace("PET","").astype(float)
d=TT.load_track(); s=d[(~d.removed)&(d.cond=="comfort")]
print("video: PET levels",sorted(v.pet.unique()),"timepoints",v.timepoint.unique()[:10],"trials/driver",v.groupby("Exp_Subject_Id").size().describe()[["min","50%","max"]].tolist())
print("video P(intervene) by pet x timepoint"); print(v.pivot_table(index="pet",columns="timepoint",values="intervene",aggfunc="mean").round(2))
print("track: SetPET distribution",s.SetPET.describe().round(2).to_dict()); print("trials/driver",s.groupby("ParticipantNumber").size().describe()[["min","50%","max"]].tolist())
print("track drivers with both go and no-go:",(s.groupby("ParticipantNumber").go.nunique()==2).sum(),"of",s.ParticipantNumber.nunique())
def fit(pet,y,drv,mod=None):
    x=-pet.astype(float); codes,_=pd.factorize(drv); pr=F.priors_log_scale(x)
    if mod: pr=dataclasses.replace(pr,**mod)
    f=F.fit_hier_lapse_gated(x,np.ones_like(x),y.astype(float),codes,pr); return f,pr
def rep(label,modv=None,modt=None):
    fv,pv=fit(v.pet.to_numpy(),v.intervene.to_numpy(),v.Exp_Subject_Id.to_numpy(),modv)
    ft,pt=fit(s.SetPET.to_numpy(),1-s.go.to_numpy(),s.ParticipantNumber.to_numpy(),modt)
    se=np.hypot(np.sqrt(fv["cov"][2,2]),np.sqrt(ft["cov"][2,2])); lr=np.log(fv["sigma_resp"]/ft["sigma_resp"])
    print(f"{label:35s} prior centres v {np.exp(pv.sigma_resp_loc):.2f} t {np.exp(pt.sigma_resp_loc):.2f} | sr v {fv['sigma_resp']:.3f} (sp {fv['sigma_pop']:.2f}, b {fv['b']:.3f}) t {ft['sigma_resp']:.3f} (sp {ft['sigma_pop']:.2f}, b {ft['b']:.3f}) ratio {np.exp(lr):.2f} [{np.exp(lr-1.96*se):.2f},{np.exp(lr+1.96*se):.2f}] se_log v {np.sqrt(fv['cov'][2,2]):.3f} t {np.sqrt(ft['cov'][2,2]):.3f}")
rep("as card")
rep("wide sigma_resp prior (sd 2)",dict(sigma_resp_scale=2.0),dict(sigma_resp_scale=2.0))
rep("wide sr + wide sigma_pop (2.0)",dict(sigma_resp_scale=2.0,sigma_pop_scale=2.0),dict(sigma_resp_scale=2.0,sigma_pop_scale=2.0))
rep("common sr prior centre 0.5",dict(sigma_resp_loc=np.log(0.5)),dict(sigma_resp_loc=np.log(0.5)))
