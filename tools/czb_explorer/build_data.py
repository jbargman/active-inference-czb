"""Build data_model.js for the model browser (tier 3) from the OSF deposit.

    python tools/czb_explorer/build_data.py

Extracts, for every rear-end experiment (28 baseline + 196 ablation runs),
per-seed response times and outcomes from the per-timestep pickles, and joins
the outcome rates from the authors' Analysis tables; adds rate-only tables for
the oncoming and intersection scenarios. Emits a single static data_model.js
so the browser page needs neither the 3.1 GB deposit nor a backend.

Restartable: per-seed extraction is appended to _cache/seeds_all.csv with
fsync, and already-extracted experiments are skipped (long jobs get killed in
this environment; HANDOFF.md section 3). Re-run the same command to resume.

Onset definitions as in replication/validate_osf.py: lead onset = first lead
deceleration < -0.1 m/s^2; brake onset = first executed deceleration
<= -1 m/s^2 at or after lead onset; re-plan onset = first step where the
executed policy departs from the extended reference policy. For the
no-evidence-accumulation ablation the re-plan onset is not meaningful (the
model re-plans continuously); the page labels it accordingly.
"""

from __future__ import annotations

import json
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OSF = REPO / "external" / "gs4bu-osfstorage-archive"
RE = OSF / "Results_rear_end" / "Results_rear_end"
CACHE = HERE / "_cache"
CACHE.mkdir(exist_ok=True)
DT = 0.2
LEAD_THRESHOLD = -0.1
BRAKE_THRESHOLD = -1.0


def ablation_label(row) -> str:
    if str(row["EA_mode"]) != "Surprise":
        return "no evidence accumulation"
    if row["noise_pred_fac"] < 0.01:
        return "no prediction noise"
    if row["use_pedals"] == 0:
        return "no pedal constraints"
    if row["use_looming_perception"] == 0:
        return "no looming perception"
    if row["looming_threshold"] < 0.001:
        return "no looming threshold"
    if row["N_norm"] == 1:
        return "no norm conditioning"
    if row["alpha"] == 0:
        return "no epistemic value"
    return "baseline"


def first_index(mask: np.ndarray) -> int:
    hits = np.flatnonzero(mask)
    return int(hits[0]) if hits.size else -1


def extract_all() -> pd.DataFrame:
    out_csv = CACHE / "seeds_all.csv"
    setups = pd.read_excel(RE / "Setups_rear_end.xlsx")
    done: set[int] = set()
    if out_csv.exists():
        done = set(pd.read_csv(out_csv)["exp"].unique().tolist())
    header_needed = not out_csv.exists()

    for i, row in setups.iterrows():
        exp = int(row["Unnamed: 0"])
        if exp in done:
            continue
        pkl = RE / "Exp_{0}".format(exp) / "Exp_{0}.pkl".format(exp)
        if not pkl.exists():
            print("missing", pkl.name, flush=True)
            continue
        with open(pkl, "rb") as f:
            d = pickle.load(f)
        eta = d["eta"].astype(np.float64)                     # (S, T, 12+)
        # policy arrays are (H, T, S, 2); see notes/05_validation.md section 4b
        a_exec = d["a_cont"][0, :, :, 0].astype(np.float64).T   # (S, T)
        replan = (np.abs(d["a_cont"] - d["a_cont_init"]) > 1e-5).any(axis=(0, 3)).T
        n_seeds, n_t = eta.shape[0], eta.shape[1]
        records = []
        for s in range(n_seeds):
            lead_on = first_index(eta[s, :, 10] < LEAD_THRESHOLD)
            if lead_on < 0:
                continue
            steps = np.arange(n_t)
            brake_on = first_index((a_exec[s] <= BRAKE_THRESHOLD) & (steps >= lead_on))
            replan_on = first_index(replan[s] & (steps >= lead_on))
            records.append({
                "exp": exp, "seed": s,
                "rt_brake": (brake_on - lead_on) * DT if brake_on >= 0 else np.nan,
                "rt_replan": (replan_on - lead_on) * DT if replan_on >= 0 else np.nan,
            })
        chunk = pd.DataFrame.from_records(records)
        chunk.to_csv(out_csv, mode="a", header=header_needed, index=False)
        header_needed = False
        with open(out_csv, "a") as f:
            f.flush()
            os.fsync(f.fileno())
        print("extracted Exp_{0} ({1} seeds)".format(exp, len(records)), flush=True)

    return pd.read_csv(out_csv)


def emit(seeds: pd.DataFrame) -> None:
    setups = pd.read_excel(RE / "Setups_rear_end.xlsx")
    analysis = pd.read_excel(RE / "Analysis_rear_end.xlsx")

    experiments = []
    for i, srow in setups.iterrows():
        exp = int(srow["Unnamed: 0"])
        arow = analysis.iloc[i]
        sub = seeds[seeds["exp"] == exp]
        rb = sub["rt_brake"].dropna().round(2).tolist()
        rr = sub["rt_replan"].dropna().round(2).tolist()
        experiments.append({
            "exp": exp,
            "ablation": ablation_label(srow),
            "v0": float(srow["v_ego_des"]),
            "thw0": float(arow["Initial THW"]),
            "rates": {
                "collision": float(arow["collision"]),
                "leave_road": float(arow["leave_road"]),
                "braking_post": float(arow["braking_post"]),
                "overtaking_post": float(arow["overtaking_post"]),
                "brake_steer_post": float(arow["brake_steer_post"]),
                "braking_pre": float(arow["braking_pre"]),
            },
            "rt_brake": rb,
            "rt_replan": rr,
        })

    oncoming = []
    df = pd.read_excel(OSF / "Results_oncoming" / "Results_oncoming"
                       / "Analysis_oncoming.xlsx")
    for _, r in df.iterrows():
        oncoming.append({
            "ablation": ablation_label(r), "rel_target": float(r["rel_target"]),
            "num_plans": int(r["num_plans"]),
            "collision": float(r["collision"]),
            "pass_center": float(r["ego_pass_via_center"]),
            "pass_shoulder": float(r["ego_pass_via_shoulder"]),
        })

    intersection = []
    df = pd.read_excel(OSF / "Results_intersection" / "Results_intersection"
                       / "Analysis_intersection.xlsx")
    for _, r in df.iterrows():
        intersection.append({
            "ablation": ablation_label(r), "v0": float(r["v_ego_des"]),
            "v_tar": float(r["v_tar"]), "x_ego": round(float(r["x_ego"]), 1),
            "collision": float(r["Collision"]),
            "braked": float(r["braked"]), "steered": float(r["steered"]),
        })

    payload = {
        "source": "external/gs4bu-osfstorage-archive (Schumann et al. 2026 OSF deposit)",
        "generated_by": "tools/czb_explorer/build_data.py",
        "onset_note": ("brake onset: first executed decel <= -1 m/s^2 after lead onset; "
                       "re-plan onset: first policy departure from reference. dt = 0.2 s."),
        "rear_end": experiments,
        "oncoming": oncoming,
        "intersection": intersection,
    }
    out = HERE / "data_model.js"
    out.write_text(
        "/* Generated by build_data.py from the OSF deposit - do not edit. */\n"
        "const MODEL_DATA = " + json.dumps(payload) + ";\n"
        "if (typeof module !== 'undefined') module.exports = MODEL_DATA;\n"
        "if (typeof window !== 'undefined') window.MODEL_DATA = MODEL_DATA;\n",
        encoding="utf-8")
    n_rt = sum(len(e["rt_brake"]) for e in experiments)
    print("wrote {0} ({1:.0f} KB): {2} rear-end experiments, {3} RT values, "
          "{4} oncoming rows, {5} intersection rows".format(
              out.name, out.stat().st_size / 1024, len(experiments), n_rt,
              len(oncoming), len(intersection)))


if __name__ == "__main__":
    emit(extract_all())
    print("ALL DONE")
