import numpy as np, pandas as pd
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
d=pd.read_csv(REPO+r"\replication\czb\out\jj3_rollout_cells.csv")
ov=d[d.scenario=="overtake"]
print(ov[["cell","p","y_offset_m","y_rel","v_ego","v_cyc","dg_A","dg_B","G_A_continue","G_A_abort"]].to_string())
dl=pd.read_csv(REPO+r"\replication\czb\out\jj3_driver_levels.csv")
from scipy.stats import spearmanr
rng=np.random.default_rng(0); a=dl.level_cutin_log_dg.to_numpy(); b=dl.level_ltap_log_dg.to_numpy()
bs=[]
for _ in range(4000):
    i=rng.integers(0,len(a),len(a)); bs.append(spearmanr(a[i],b[i]).statistic)
print("rho",spearmanr(a,b).statistic,"boot CI",np.nanpercentile(bs,[2.5,97.5]))
print("ltap level distinct (3dp):",len(np.unique(b.round(3))), " n within 10.95-10.99:",((b>10.95)&(b<10.99)).sum())
