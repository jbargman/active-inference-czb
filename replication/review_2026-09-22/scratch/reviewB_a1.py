import sys, os
import numpy as np, pandas as pd
R = r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, R + r"\replication\czb"); sys.path.insert(0, R + r"\src")
os.chdir(os.environ["SCR"])
import jj4_precision_spread as J4
b, notes = J4.press_levels()
b.to_pickle("press_levels.pkl")
print(notes, len(b), b.driver.nunique())
print(b.columns.tolist())
# RE.3 recompute
csv = pd.read_csv(R + r"\replication\czb\out\re3_apparent_size.csv")
d = csv.diff_log_theta_dot.to_numpy()
print("RE3 mean", d.mean(), "sd", d.std(ddof=1), "n", len(d), "t-int", d.mean()-2.018*d.std(ddof=1)/np.sqrt(len(d)), d.mean()+2.018*d.std(ddof=1)/np.sqrt(len(d)))
rng = np.random.default_rng(20260918)
boot = np.array([np.mean(d[rng.integers(0, len(d), len(d))]) for _ in range(2000)])
print("boot", np.percentile(boot,[2.5,97.5]))
# per-TTC class difference (driver-paired)
cell = b.groupby(["driver","cls","criticality_label"])["level"].mean().reset_index()
piv = cell.pivot_table(index=["driver","criticality_label"], columns="cls", values="level").dropna()
dd = (piv[1]-piv[0]).reset_index()
per_ttc = dd.groupby("criticality_label")[0].agg(["mean","std","size"])
per_ttc["se"] = per_ttc["std"]/np.sqrt(per_ttc["size"])
print(per_ttc)
m = per_ttc["mean"].to_numpy()
print("over clips: mean", m.mean(), "sd", m.std(ddof=1), "se", m.std(ddof=1)/np.sqrt(5), "t4 int", m.mean()-2.776*m.std(ddof=1)/np.sqrt(5), m.mean()+2.776*m.std(ddof=1)/np.sqrt(5))
# two-way bootstrap: drivers and TTC pairs
W = dd.pivot(index="driver", columns="criticality_label", values=0)
Wv = W.to_numpy()
bs=[]
for _ in range(4000):
    i = rng.integers(0, Wv.shape[0], Wv.shape[0]); k = rng.integers(0,5,5)
    bs.append(np.nanmean(np.nanmean(Wv[i][:,k],axis=0)))
print("driver x clip-pair bootstrap", np.percentile(bs,[2.5,97.5]))
