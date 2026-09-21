import sys, numpy as np
sys.dont_write_bytecode=True
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0,REPO+r"\src")
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES, load_overtake_trace
for lab,path in RANDOM_OVERTAKE_TRACES.items():
    tr=load_overtake_trace(path); t=np.asarray(tr.t); ton=t[tr.onset_idx]
    for rel in (-0.15,0.3,0.6,0.9,1.2,2.0,3.0,3.6,4.2):
        i=int(np.argmin(np.abs(t-(ton+rel))))
        print(lab,"t",rel,"x_tar",round(float(tr.x_tar[i]),2),"y_tar",round(float(tr.y_tar[i]),3),"y_ego",round(float(tr.y_ego[i]),3))
