import pandas as pd, numpy as np
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
d=pd.read_csv(REPO+r"\replication\causation\re1\re1_cells.csv")
print(d.groupby(["part","mode"]).size())
b=d[d.part=="B2"]
b=b.assign(ratio=b.eps_hi/b.eps_lo)
print(b[["tag","eps_lo","eps","eps_hi","ratio","collide_frac"]].head(12).to_string())
print("median hi/lo ratio", b.ratio.median(), "max", b.ratio.max())
b1=d[d.part=="B1"]; print(b1[["tag","eps","eps_lo","eps_hi","term_speed","term_accel","term_collision","term_safety"]].to_string())
