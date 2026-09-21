import numpy as np, pandas as pd
from scipy.stats import spearmanr
pd.set_option("display.width",250)
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
d=pd.read_csv(REPO+r"\replication\czb\out\jj3_rollout_cells.csv")
print(d.columns.tolist())
ov=d[d.scenario=="overtake"] if "scenario" in d else d
print(d.to_string(max_colwidth=18))
