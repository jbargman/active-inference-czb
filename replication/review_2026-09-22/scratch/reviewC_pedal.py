import sys
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, REPO+r"\src")
import numpy as np, pandas as pd
from aidriver.agent import apply_pedal_constraint, AgentParams
a=np.full((1,30),-5.0)
print(apply_pedal_constraint(a,0.0,AgentParams(),0.2)[0,:4])
d=pd.read_csv(REPO+r"\replication\causation\re1\re1_cells.csv")
c=d[d.part=="C"]
print(c[["tag","dG","a_best_first","omega_best_first","omega_best_max","acts_brake","acts_steer"]].describe().to_string())
print((c.a_best_first< -0.1-1e-9).sum(), "cells with first a below coast (median over 3 seeds)")
b=d[d.part=="B2"]; print(b.columns.tolist())
print(b[["tag","gap_m","dv","eps","term_collision","term_safety","collide_frac"]].to_string())
