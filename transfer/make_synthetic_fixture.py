"""
Write a small synthetic dataset in the shape of `transfer/interface_schema.yaml`, so that the
shared analysis code can be run end to end at the home site, which holds no data, and so that
the data site can see exactly what its adapter must produce.

Nothing here is data: three drivers, two scenarios, constant-deceleration kinematics with a
fixed seed. The response onsets are scripted from a made-up per-driver level so that the
fitting code has something to recover; the values are not claims about anyone.

    python transfer/make_synthetic_fixture.py            # writes transfer/fixtures/synthetic/
    python transfer/validate_interface.py transfer/fixtures/synthetic
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "fixtures" / "synthetic"
DT = 0.05
DRIVERS = {"D01": 0.030, "D02": 0.045, "D03": 0.020}   # made-up looming-rate levels [rad/s]
W_OTH = 1.85


def rear_end_event(rng, level, v0, gap0, a_lead, t_on=2.0, T=8.0):
    t = np.arange(0.0, T + 1e-9, DT)
    oth_v = np.maximum(v0 + a_lead * np.clip(t - t_on, 0, None), 0.0)
    oth_x = gap0 + np.cumsum(oth_v) * DT
    ego_v = np.full_like(t, v0)
    ego_x = np.cumsum(ego_v) * DT
    gap = oth_x - ego_x
    theta_dot = W_OTH * (ego_v - oth_v) / np.maximum(gap, 0.5) ** 2
    cross = np.where(theta_dot >= level)[0]
    t_brake = float(t[cross[0]]) + 0.2 if len(cross) else float("nan")
    if not np.isnan(t_brake):
        m = t >= t_brake
        ego_v[m] = np.maximum(v0 - 4.0 * (t[m] - t_brake), 0.0)
        ego_x = np.cumsum(ego_v) * DT
    ego_ax = np.gradient(ego_v, DT)
    oth_ax = np.gradient(oth_v, DT)
    rows = []
    for i in range(len(t)):
        rows.append([f"{t[i]:.2f}", f"{ego_x[i]:.3f}", f"{rng.normal(0, 0.02):.3f}", "0.000",
                     f"{ego_v[i]:.3f}", f"{ego_ax[i]:.3f}", "NaN",
                     f"{oth_x[i]:.3f}", f"{rng.normal(0, 0.03):.3f}", "0.000",
                     f"{oth_v[i]:.3f}", f"{oth_ax[i]:.3f}", "car", "1"])
    return rows, t_brake


def main(out: Path = OUT) -> int:
    rng = np.random.default_rng(0)
    out.mkdir(parents=True, exist_ok=True)
    header = ["t", "ego_x", "ego_y", "ego_psi", "ego_v", "ego_ax", "ego_delta",
              "oth_x", "oth_y", "oth_psi", "oth_v", "oth_ax", "oth_class", "valid"]
    meta = []
    eid = 0
    for did, level in DRIVERS.items():
        for scenario, (v0, gap0, a_lead) in {"rear_end": (15.0, 20.0, -3.0),
                                             "cut_in": (25.0, 12.0, -1.0)}.items():
            for rep in range(2):
                eid += 1
                event_id = f"E{eid:04d}"
                rows, t_brake = rear_end_event(rng, level, v0 + rep, gap0 + 4 * rep, a_lead)
                with (out / f"{event_id}.csv").open("w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(header)
                    w.writerows(rows)
                meta.append([event_id, "SYNTH", scenario, did, "3.50", "2", "0", "4.60", "1.85",
                             "4.50", f"{W_OTH:.2f}", "0", "front_bumper", "2.00",
                             "NaN" if np.isnan(t_brake) else f"{t_brake:.2f}", "NaN", "conflict", "ok"])
    with (out / "events.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "dataset", "scenario", "driver_id", "lane_width", "n_lanes_same",
                    "n_lanes_opposite", "ego_len", "ego_wid", "oth_len", "oth_wid", "geometry_default",
                    "ref_point", "t_conflict_onset", "t_brake_onset", "t_steer_onset", "outcome",
                    "quality_flag"])
        w.writerows(meta)
    print(f"wrote {eid} synthetic events to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT))
