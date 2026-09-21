import sys, os
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, REPO+r"\replication\czb"); sys.path.insert(0, REPO+r"\src")
import numpy as np, pandas as pd
import hs1_situational_surprise as HS
from aidriver.preferences import PreferenceParams, log_lateral_pref
cells=pd.read_csv(REPO+r"\replication\czb\out\cutin2_cells.csv")
sc=HS.study2_scenes(cells.head(40))
ys=[]
for k,s in list(sc.items())[:6]:
    y=s["tracks"][s["ego"]].y; yt=s["tracks"][s["tar"]].y
    print(k,"ego y median",np.median(y),"range",y.min(),y.max(),"| target y start/end",yt[0],yt[-1])
    ys.append(np.median(y))
p=PreferenceParams()
print("log_lateral_pref at those y:",[float(log_lateral_pref(y,p)) for y in ys], "x30 =",[30*float(log_lateral_pref(y,p)) for y in ys])
