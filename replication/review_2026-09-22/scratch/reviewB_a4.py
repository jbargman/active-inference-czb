import sys, os
import numpy as np, pandas as pd
R = r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, R + r"\replication\czb"); sys.path.insert(0, R + r"\src")
os.chdir(os.environ["SCR"])
import fit_stage1_looming as F
from comfortzone.czb_data import BUTTON_CLIP_START_S, KIN_BUTTON
from comfortzone.cutin import load_cutin_trace
b = pd.read_pickle("press_levels.pkl")
print("BUTTON_CLIP_START_S",BUTTON_CLIP_START_S)
rows=[]
for cls in ("CutInCar","CutInTruck"):
  for k in (4,5,6,7,8):
    p=KIN_BUTTON/f"{cls}_{k}TTC_vehicle_states.csv"; tr=load_cutin_trace(p); f=F.looming_field(p)
    t=f.t.to_numpy(); i=tr.onset_idx
    y=np.abs(f.y_rel.to_numpy()); l0=f.l0.to_numpy()
    i_l0=int(np.argmax(l0<=0)) if (l0<=0).any() else -1
    i_end=int(np.argmax(y<0.1)) if (y<0.1).any() else -1
    g=f.gap_m.to_numpy(); v=f.v_rel.to_numpy()
    sub=b[(b.scenario==("cutin_car" if cls=="CutInCar" else "cutin_truck"))&(b.criticality_label==f"TTC{k}")]
    tp=BUTTON_CLIP_START_S+sub.press_time_s.median()
    ip=np.searchsorted(t,tp)
    rows.append(dict(clip=f"{cls}{k}",t_on=t[i],gap_on=g[i],ttc_on=g[i]/v[i],y_on=y[i],t_l0=t[i_l0],gap_l0=g[i_l0],ttc_l0=g[i_l0]/v[i_l0],t_ctr=t[i_end],ttc_ctr=g[i_end]/v[i_end],gap0=g[0],len=getattr(tr,"tar_len",np.nan),t_medpress=tp,gap_medpress=g[min(ip,len(g)-1)],mean_level=sub.level.mean()))
d=pd.DataFrame(rows); print(d.round(2).to_string())
car=d.iloc[:5]; tk=d.iloc[5:]
for col in ("gap_on","gap_l0"):
    ci=np.interp(tk[col],car[col],car.mean_level)
    print(col,"truck - car(interp at same",col,"):",np.round(tk.mean_level.to_numpy()-ci,3),"(last values extrapolated flat if outside", car[col].max(),")")
