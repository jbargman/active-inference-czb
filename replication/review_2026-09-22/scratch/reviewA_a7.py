import sys, numpy as np
sys.dont_write_bytecode=True
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0,REPO+r"\src")
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES, load_overtake_trace
for lab,path in RANDOM_OVERTAKE_TRACES.items():
    tr=load_overtake_trace(path)
    names=[a for a in dir(tr) if not a.startswith("_")]
    if lab==list(RANDOM_OVERTAKE_TRACES)[0]: print(names)
    dx=np.asarray(tr.x_tar); dy=np.asarray(tr.y_tar)-np.asarray(tr.y_ego)
    inbox=np.abs(dx)<=1.15*4.2
    t=np.asarray(tr.t); ton=t[tr.onset_idx]
    print(lab,"onset t",round(ton,2),"tar wid",getattr(tr,"tar_wid",None),"tar len",getattr(tr,"tar_len",None))
    if inbox.any():
        print("   while |dx|<=4.83: |dy| min",np.abs(dy[inbox]).min().round(3),"max",np.abs(dy[inbox]).max().round(3),"  t range rel onset",round(t[inbox][0]-ton,2),round(t[inbox][-1]-ton,2), " box threshold 1.978")
    else: print("   never alongside in trace; final dx",dx[-1].round(2),"final |dy|",abs(dy[-1]).round(3), "t_end rel onset", round(t[-1]-ton,2))
