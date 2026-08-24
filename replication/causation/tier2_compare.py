"""
The arbiter analysis: closed-loop (tier-2) attentive brake onsets versus the tier-1
surrogate under its two accumulator-start conventions.

    python replication/causation/tier2_compare.py

Reads every replication/causation/tier2/seed_<id>.pkl (glance runs excluded), extracts
per-seed closed-loop onsets (median over the batch repeats; the detection rule of
tier2_rear_end.summarize), and joins the tier-1 condition-A onsets from
out/cond_A_nb.csv (zero start) and out/cond_A_nb_stat.csv (stationary start). Writes
tier2/arbiter_comparison.csv and prints the verdict table.

Comparability note: tier-1 evaluates the field on the no-brake counterfactual profile,
while the tier-2 ego drives itself from t = 0; onsets are compared in scenario time,
which both share. Seeds where either side never responds are reported, not dropped.
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))
from tier2_rear_end import summarize, OUT as T2   # noqa: E402


def main() -> None:
    rows = []
    for p in sorted(T2.glob("seed_*.pkl")):
        if "glance" in p.name:
            continue
        with open(p, "rb") as f:
            r = pickle.load(f)
        s = pd.DataFrame(summarize(r))
        rows.append(dict(seed_id=r["seed_id"], v_f0=r["v_f0"],
                         t2_onset=float(s.t_onset.median()),
                         t2_onset_iqr=float(s.t_onset.quantile(.75) - s.t_onset.quantile(.25)),
                         t2_n_responding=int(s.t_onset.notna().sum()),
                         t2_crashed=int(s.crashed.sum())))
    t2 = pd.DataFrame(rows).set_index("seed_id")

    def t1_onsets(tag):
        df = pd.read_csv(HERE / "out" / f"cond_A_{tag}.csv")
        return df.groupby("seed_id").t_onset.first()

    t2["t1_zero"] = t1_onsets("nb").reindex(t2.index)
    t2["t1_stat"] = t1_onsets("nb_stat").reindex(t2.index)
    t2["d_zero"] = t2.t2_onset - t2.t1_zero
    t2["d_stat"] = t2.t2_onset - t2.t1_stat
    both = t2.dropna(subset=["t2_onset", "t1_zero", "t1_stat"])
    closer_stat = (both.d_stat.abs() < both.d_zero.abs()).sum()
    out = T2 / "arbiter_comparison.csv"
    t2.round(3).to_csv(out)

    print(t2.round(2).sort_values("v_f0").to_string())
    print()
    print(f"seeds with onsets on all three sides: {len(both)}")
    print(f"closed-loop minus tier-1 zero-start:       median {both.d_zero.median():+.2f} s, "
          f"median |diff| {both.d_zero.abs().median():.2f} s")
    print(f"closed-loop minus tier-1 stationary-start: median {both.d_stat.median():+.2f} s, "
          f"median |diff| {both.d_stat.abs().median():.2f} s")
    print(f"stationary closer on {closer_stat}/{len(both)} seeds")
    print("wrote", out)


if __name__ == "__main__":
    main()
