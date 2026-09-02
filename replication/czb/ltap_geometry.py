"""The LTAP stimuli, measured: geometry per trace and what the response surface says (B.3.v2 prep).

Written 2026-09-02 for the B.3.v2 construction note (`docs/ltap_construction_note.md`).
No model, no fit: this script reads the 18 left-turn-across-path traces (9 PET levels x
2 oncoming speeds) and the Random-design responses, and tabulates the quantities the
construction note argues from, so that every number in the note comes from a tracked
output.

What is measured per trace
--------------------------
* Roles: the EGO is the vehicle whose heading changes (it turns left); the ONCOMING is the
  one with constant heading. Vehicle IDs differ per file, so roles are assigned by yaw
  span -- a third role rule, after the cut-in's lateral-span rule and the overtake's
  vehicle-dimension rule, and for the same reason: the instructed vehicle is the one
  performing the manoeuvre.
* Turn onset: the first frame at which the ego's unwrapped yaw departs from its initial
  value by more than 1 degree.
* The conflict band: +-1 m around the oncoming vehicle's median lateral position; the
  ego's entry and exit frames are the first and last frames inside it, and the conflict
  point is the ego's mean longitudinal position while inside.
* The oncoming's arrival: the first frame at which its front bumper reaches the conflict
  point. Measured PET = arrival minus the ego's exit.
* At turn onset: the oncoming's distance to the conflict point and its time-to-arrival.

What is checked against the responses
-------------------------------------
The Random design gives P(intervene) per (PET, speed) cell (172 trials each). Two
one-axis predictions are compared, model-free: if the response depends on TIME only,
cells at the same PET should match across speeds; if it depends on DISTANCE only, the
70 km/h cell at PET p should match the 50 km/h cell at whatever PET puts the oncoming at
the same distance. The table reports both mismatches.

Run: python replication/czb/ltap_geometry.py    Output: out/ltap_geometry.md
"""
from __future__ import annotations

import glob
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STUDY = REPO / "external/01_studies/01_Studies/01_Sequence_Random_ButtonPress"
KIN = STUDY / "Kinematics/Sequence_Random_Study"
JOINT = STUDY / "Random_Button_Joint.csv"
OUT = HERE / "out"
NAME_RE = re.compile(r"IntersectionLeftTurnPET([\d.]+)(-70kph)?")


def measure(path: str) -> dict:
    name = os.path.basename(path).replace("_vehicle_states.csv", "")
    m = NAME_RE.match(name)
    pet, spd = float(m.group(1)), (70 if m.group(2) else 50)
    d = pd.read_csv(path)
    parts = {v: g.sort_values("Elapsed_Time_s").reset_index(drop=True)
             for v, g in d.groupby("Vehicle_ID")}
    yawspan = {v: float(g.Yaw.max() - g.Yaw.min()) for v, g in parts.items()}
    ego = max(yawspan, key=yawspan.get)
    onc = [v for v in parts if v != ego][0]
    e, o = parts[ego], parts[onc]
    t = e.Elapsed_Time_s.to_numpy()
    yaw = np.unwrap(np.deg2rad(e.Yaw.to_numpy()))
    onset = int(np.argmax(np.abs(yaw - yaw[0]) > np.deg2rad(1.0)))
    t_on = float(t[onset])
    y_onc = float(o.Location_Y.median())
    ey, ex = e.Location_Y.to_numpy(), e.Location_X.to_numpy()
    inband = (ey > y_onc - 1.0) & (ey < y_onc + 1.0)
    i_in = int(np.argmax(inband))
    i_out = int(len(inband) - 1 - np.argmax(inband[::-1]))
    t_in, t_out = float(t[i_in]), float(t[i_out])
    x_conf = float(ex[i_in:i_out + 1].mean())
    ox, ot, ov = o.Location_X.to_numpy(), o.Elapsed_Time_s.to_numpy(), o.Speed_mps.to_numpy()
    half = float(o.Length_m.iloc[0]) / 2.0
    reach = ox + half >= x_conf
    t_arr = float(ot[int(np.argmax(reach))]) if reach.any() else np.nan
    pre = ot < t_on
    v_on = float(np.median(ov[pre])) if pre.any() else np.nan
    dist_on = float(x_conf - (ox[int(np.searchsorted(ot, t_on))] + half))
    return dict(trace=name, pet=pet, speed_kph=spd, ego_id=int(ego),
                v_ego_approach=float(np.median(e.Speed_mps[t < t_on - 3.0])) if (t < t_on - 3.0).any() else np.nan,
                t_onset=t_on, v_ego_onset=float(e.Speed_mps.iloc[onset]),
                t_in=t_in, t_out=t_out, x_conf=x_conf, v_onc=v_on, t_onc_arrival=t_arr,
                pet_measured=t_arr - t_out, dist_at_onset=dist_on, tta_at_onset=dist_on / v_on)


def main() -> None:
    rows = [measure(f) for f in sorted(glob.glob(str(KIN / "IntersectionLeftTurnPET*_vehicle_states.csv")))]
    g = pd.DataFrame(rows).sort_values(["speed_kph", "pet"]).reset_index(drop=True)

    j = pd.read_csv(JOINT, low_memory=False)
    r = j[(j.scenario == "ltap") & (j.design == "Random")].copy()
    r["pet"] = r.criticality_label.str.replace("PET", "").astype(float)
    resp = (r.groupby(["pet", "ltap_speed"]).intervene.agg(["mean", "count"]).reset_index()
            .rename(columns={"ltap_speed": "speed_kph", "mean": "p", "count": "n"}))
    g = g.merge(resp, on=["pet", "speed_kph"], how="left")

    L = ["# The LTAP stimuli, measured", "",
         "Generated by `replication/czb/ltap_geometry.py`. Do not edit by hand. Roles by yaw"
         " span (the ego turns); turn onset at 1 degree of heading change; conflict band"
         " +-1 m around the oncoming's lateral position; the oncoming arrives when its front"
         " bumper reaches the ego's mean position inside the band.", "",
         "## Per trace", "",
         "| trace | PET (design) | oncoming speed | ego approach speed | turn onset [s] | ego speed at onset | ego in band [s] | ego out [s] | oncoming arrival [s] | PET measured [s] | oncoming distance at onset [m] | oncoming time-to-arrival at onset [s] | P(intervene) | n |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, x in g.iterrows():
        L.append(f"| {x.trace} | {x.pet:.1f} | {x.speed_kph:.0f} km/h | {x.v_ego_approach:.1f} | "
                 f"{x.t_onset:.2f} | {x.v_ego_onset:.1f} | {x.t_in:.2f} | {x.t_out:.2f} | "
                 f"{x.t_onc_arrival:.2f} | {x.pet_measured:.2f} | {x.dist_at_onset:.1f} | "
                 f"{x.tta_at_onset:.2f} | {x.p:.3f} | {int(x.n)} |")
    L.append("")

    # invariants worth stating
    L += ["## What is the same across all 18 traces", "",
          f"Turn onset {g.t_onset.min():.2f}-{g.t_onset.max():.2f} s; ego speed at onset "
          f"{g.v_ego_onset.min():.1f}-{g.v_ego_onset.max():.1f} m/s; ego in the oncoming lane "
          f"{g.t_in.min():.2f}-{g.t_in.max():.2f} to {g.t_out.min():.2f}-{g.t_out.max():.2f} s; "
          f"oncoming speed {g[g.speed_kph == 50].v_onc.median():.1f} m/s at 50 km/h and "
          f"{g[g.speed_kph == 70].v_onc.median():.1f} m/s at 70 km/h, constant. The ego's script "
          "is the same in every trace; only the oncoming's start position (per PET) and speed "
          "vary. Measured PET exceeds the design value by a near-constant offset (the band "
          "definition here is +-1 m; the design's conflict-zone extent is not documented), "
          f"mean offset {(g.pet_measured - g.pet).mean():.2f} s, range "
          f"{(g.pet_measured - g.pet).min():.2f}-{(g.pet_measured - g.pet).max():.2f} s.", ""]

    # the two one-axis predictions
    L += ["## Time or distance? Two one-axis predictions against the Random responses", "",
          "At a given design PET the oncoming's time-to-arrival at turn onset is matched across"
          " speeds while its distance differs by the speed ratio. A TIME-only response predicts"
          " equal P across speeds at matched PET; a DISTANCE-only response predicts the 70 km/h"
          " cell to match the 50 km/h cell at the PET whose distance is the same (interpolated"
          " on the 50 km/h distance-response curve).", "",
          "| PET | TTA at onset (50 / 70) [s] | distance (50 / 70) [m] | P at 50 | P at 70 | time-only prediction for 70 | distance-only prediction for 70 |",
          "|---|---|---|---|---|---|---|"]
    g50 = g[g.speed_kph == 50].sort_values("dist_at_onset")
    d50, p50 = g50.dist_at_onset.to_numpy(), g50.p.to_numpy()
    err_t, err_d = [], []
    for pet in sorted(g.pet.unique()):
        a = g[(g.pet == pet) & (g.speed_kph == 50)].iloc[0]
        b = g[(g.pet == pet) & (g.speed_kph == 70)].iloc[0]
        pred_t = a.p
        pred_d = float(np.interp(b.dist_at_onset, d50, p50, right=np.nan))
        err_t.append(b.p - pred_t)
        err_d.append(b.p - pred_d)
        L.append(f"| {pet:.1f} | {a.tta_at_onset:.2f} / {b.tta_at_onset:.2f} | "
                 f"{a.dist_at_onset:.1f} / {b.dist_at_onset:.1f} | {a.p:.3f} | {b.p:.3f} | "
                 f"{pred_t:.3f} | {pred_d:.3f} |")
    et, ed = np.array(err_t), np.array(err_d)
    L += ["", f"Mean signed error of the time-only prediction: {np.nanmean(et):+.3f} (RMS "
          f"{np.sqrt(np.nanmean(et ** 2)):.3f}); of the distance-only prediction: "
          f"{np.nanmean(ed):+.3f} (RMS {np.sqrt(np.nanmean(ed ** 2)):.3f}), over the PET levels "
          "where the distance interpolation is inside the 50 km/h range (NaN otherwise). A"
          " negative signed error means the 70 km/h cells intervene LESS than the prediction.", ""]

    g.to_csv(OUT / "ltap_geometry.csv", index=False)
    (OUT / "ltap_geometry.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
