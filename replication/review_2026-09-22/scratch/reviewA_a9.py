import sys, numpy as np
sys.dont_write_bytecode=True
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0,REPO+r"\src"); sys.path.insert(0,REPO+r"\replication\czb")
import hs1_situational_surprise as HS
from aidriver.preferences import PreferenceParams
from comfortzone import czb_data
from comfortzone.conflict import Body, planned_path
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES, load_overtake_trace
from rollout.belief import FLOORS_STUDY1, Scene, belief_at
from rollout.efe import log_terms, relative_position
from rollout.policies import overtake_rollout
from rollout.predictor import DT_S, HORIZON_S, horizon_steps, sample_futures
def staging(v): return PreferenceParams(v_desired=float(v),lane_entry_continuous=True,counterfactual_residual_severity=True,lane_entry_shape_k=12.0)
ends={"C1":-0.15,"C2":0.3,"C3":0.6,"C4":0.9,"C5":1.2}
for lab,path in RANDOM_OVERTAKE_TRACES.items():
    tr=load_overtake_trace(path); t_on=float(tr.t[tr.onset_idx]); y_lane0=float(tr.y_ego[0])
    grid,tracks,meta=HS.scene_tracks(path)
    ego_id=max(meta,key=lambda v:meta[v]["width"]); cyc=[v for v in tracks if v!=ego_id][0]
    def head(v):
        h=meta[v].get("heading"); return np.asarray(h,float) if h is not None else np.zeros_like(grid)
    sc=Scene(t=grid,ego_x=tracks[ego_id].x,ego_y=tracks[ego_id].y,ego_heading=head(ego_id),ego_speed=meta[ego_id]["speed"],oth_x=tracks[cyc].x,oth_y=tracks[cyc].y,oth_heading=head(cyc),oth_speed=meta[cyc]["speed"],ego_len=meta[ego_id]["length"],ego_wid=meta[ego_id]["width"],oth_len=meta[cyc]["length"],oth_wid=meta[cyc]["width"],name=lab)
    body=Body(t=grid,x=tracks[ego_id].x,y=tracks[ego_id].y,heading=head(ego_id),length=meta[ego_id]["length"],width=meta[ego_id]["width"])
    for tp,ce in ends.items():
        t0=t_on+ce
        b=belief_at(sc,t0,FLOORS_STUDY1,p_change_prior=0.0,with_intention=False)
        pp=planned_path(body,t0,DT_S,v_window=1.0); px,py=b.frame.to_frame(pp.x,pp.y)
        s=np.concatenate([[0.],np.cumsum(np.hypot(np.diff(px),np.diff(py)))]); tau=horizon_steps(HORIZON_S,DT_S); s_tau=np.interp(tau,pp.tau,s)
        y_off=float(np.interp(t0,sc.t,sc.ego_y)-y_lane0); y_rec=y_off+np.interp(s_tau,s,py)
        fut=sample_futures(b,seed=0)
        out={}
        for pol in ("continue","abort"):
            pa=overtake_rollout(b,pol,px,py,s_tau,y_rec,y_off,b.v_oth)
            tm=log_terms(b,pa,fut,staging(b.v_ego))
            out[pol]={k:round(float(-v.mean(axis=0).sum())) for k,v in tm.items()}
            if pol=="continue":
                dx,dy=relative_position(pa,fut)
                box=(np.abs(dy)<=1.15*1.72)&(np.abs(dx)<=1.15*4.2)
                out["share_box_hit"]=round(float(box.any(axis=1).mean()),3)
                k=np.argmin(np.abs(dx).mean(axis=0)); out["alongside_tau"]=round(float(tau[k]),1); out["median|dy|_alongside"]=round(float(np.median(np.abs(dy[:,k]))),2); out["min|dy|_alongside"]=round(float(np.abs(dy[:,k]).min()),2)
        print(lab,tp,"trace_end-t0",round(grid[-1]-t0,2),"y_rel",round(b.y_rel,2),"vy_oth",round(b.vy_oth,3),out)
