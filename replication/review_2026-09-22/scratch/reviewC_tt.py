import sys, os
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, REPO+r"\replication\czb"); sys.path.insert(0, REPO+r"\src")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import re2_preference_family as R2
cells = pd.read_csv(R2.OUT/"cutin2_cells.csv")
scenes = R2.HS.study2_scenes(cells)
built = R2.build_cells(cells, scenes)
base = {"a_other_min": -6.0, "response_time": 1.0, "a_max": 8.0, "tau_inv_mu": 0.2,
        "collision_ref_speed": 10.0, "counterfactual_residual_severity": True}
tt = R2.term_table(base, built)
tt["v_ego"]=[x[2].v_ego for x in built]; tt["v_oth"]=[x[2].v_oth for x in built]
tt["x_rel"]=[x[2].x_rel for x in built]; tt["y_rel"]=[x[2].y_rel for x in built]
tt["p_change"]=[x[2].p_change for x in built]
tt = tt.merge(cells[["video","p","n","ttc_start","ttc_true","distance","dv_kph","lcd"]], on="video")
tt.to_csv("tt_base.csv", index=False)
# also step form and released-raw
for name, th in {"step": dict(base, counterfactual_residual_severity=False),
                 "ramp_ref1e6": dict(base, collision_ref_speed=1e6),
                 "step_ref1e6": dict(base, collision_ref_speed=1e6, counterfactual_residual_severity=False)}.items():
    t2 = R2.term_table(th, built)
    t2.to_csv(f"tt_{name}.csv", index=False)
print("done")
