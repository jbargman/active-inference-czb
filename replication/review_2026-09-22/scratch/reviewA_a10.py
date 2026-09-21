import sys, numpy as np
sys.dont_write_bytecode=True
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0,REPO+r"\src"); sys.path.insert(0,REPO+r"\replication\czb")
import hs1_situational_surprise as HS
from aidriver.preferences import PreferenceParams
from comfortzone.conflict import Body, planned_path
from comfortzone.ltap import BAND_HALF_M, T_DECISION_S, ltap_traces, trace_name
from rollout.belief import FLOORS_STUDY1, Scene, belief_at
from rollout.efe import log_terms, relative_position, polygon_overlap
from rollout.policies import ltap_rollout, ltap_wait_accel
from rollout.predictor import DT_S, HORIZON_S, horizon_steps, sample_futures
import dataclasses
def staging(v): return PreferenceParams(v_desired=float(v),lane_entry_continuous=True,counterfactual_residual_severity=True,lane_entry_shape_k=12.0)
traces={tr.name:tr for tr in ltap_traces()}
for pet,spd in ((0.0,50),(0.5,50),(1.0,50),(4.0,50)):
    name=trace_name(pet,spd); tr=traces[name]
    grid,tracks,meta=HS.scene_tracks(HS.KIN1/f"{name}_vehicle_states.csv")
    ego_id=max(meta,key=lambda v:meta[v]["yaw_span"]); onc=[v for v in tracks if v!=ego_id][0]
    def head(v):
        h=meta[v].get("heading"); return np.asarray(h,float) if h is not None else np.zeros_like(grid)
    sc=Scene(t=grid,ego_x=tracks[ego_id].x,ego_y=tracks[ego_id].y,ego_heading=head(ego_id),ego_speed=meta[ego_id]["speed"],oth_x=tracks[onc].x,oth_y=tracks[onc].y,oth_heading=head(onc),oth_speed=meta[onc]["speed"],ego_len=meta[ego_id]["length"],ego_wid=meta[ego_id]["width"],oth_len=meta[onc]["length"],oth_wid=meta[onc]["width"],name=name)
    b=belief_at(sc,T_DECISION_S,FLOORS_STUDY1,p_change_prior=0.0,with_intention=False)
    body=Body(t=grid,x=tracks[ego_id].x,y=tracks[ego_id].y,heading=head(ego_id),length=meta[ego_id]["length"],width=meta[ego_id]["width"])
    pp=planned_path(body,T_DECISION_S,DT_S,v_window=1.0); px,py=b.frame.to_frame(pp.x,pp.y)
    s=np.concatenate([[0.],np.cumsum(np.hypot(np.diff(px),np.diff(py)))]); tau=horizon_steps(HORIZON_S,DT_S); s_tau=np.interp(tau,pp.tau,s)
    tau_in=float(tr.t_in-b.t0); s_conf=float(np.interp(max(tau_in,0),pp.tau,s)); s_stop=max(s_conf-0.5*b.ego_len-BAND_HALF_M,0)
    a_wait,_=ltap_wait_accel(b.v_ego,s_stop)
    print(name,"x_rel",round(b.x_rel,1),"y_rel",round(b.y_rel,2),"vx_oth",round(b.vx_oth,2),"vy_oth",round(b.vy_oth,3),"sd_pos",b.sd_pos)
    for sdp in (1.8,0.2):
        bb=dataclasses.replace(b,sd_pos=sdp)
        fut=sample_futures(bb,seed=0)
        res={}
        for pol in ("proceed","wait"):
            pa=ltap_rollout(bb,pol,px,py,s_tau,s_stop,a_wait=a_wait)
            tm=log_terms(bb,pa,fut,staging(bb.v_ego),collision_mode="polygon")
            res[pol]={k:round(float(-v.mean(axis=0).sum())) for k,v in tm.items()}
            hit=polygon_overlap(bb,pa,fut); res[pol]["poly_hit_share"]=round(float(hit.any(axis=1).mean()),3)
            dx,dy=relative_position(pa,fut); box=(np.abs(dy)<=1.15*1.72)&(np.abs(dx)<=1.15*4.2); res[pol]["box_hit_share"]=round(float(box.any(axis=1).mean()),3)
        print("  sd_pos",sdp,res)
