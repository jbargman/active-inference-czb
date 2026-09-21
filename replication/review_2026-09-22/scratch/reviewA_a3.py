import sys, numpy as np, pandas as pd
sys.dont_write_bytecode=True
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0,REPO+r"\src")
from rollout.belief import update_intention, FLOORS_STUDY2, FLOORS_STUDY1
for fl in (FLOORS_STUDY2, FLOORS_STUDY1):
    print(fl.name)
    for vy in (-1.2,-0.3,-0.05,-0.02,-0.012,-0.01,0.0,0.012,0.02,0.05,0.3,1.0):
        print("  vy",vy,"p",round(update_intention(0.07,vy,fl.sd_v_lat,sign=1.0),4))
df=pd.read_csv(REPO+r"\replication\czb\out\jj2_rollout_cutin_cells.csv")
print(df.groupby("cp").vy_oth.describe().to_string())
