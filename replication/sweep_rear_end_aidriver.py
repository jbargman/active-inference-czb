"""
Run the independent re-implementation (`src/aidriver`) across the paper's front-to-rear
sweep, so its behavior can be compared with the published results quantitatively.

Paper sweep: time gaps {0.5 ... 3.5} s x speeds {10, 15, 20, 25} m/s, 32 repeats.
NOTE 2026-08-23: the SI (3.1) lists {10, 15, 25, 35} m/s, but the released code
(simulation_rear_end.py:496), the Fig. 3c caption and the OSF deposit all use
{10, 15, 20, 25}; see docs/method_review.md section 5, item 9. The earlier sweep in
replication/sweep_aidriver.csv was run on the SI grid and has not been re-run.
(896 simulations). We use fewer repeats to keep this tractable on CPU.

Extracts, per run:
  brake response time   -- first time ego acceleration falls below -1 m/s^2 after the lead
                           starts braking (comparable to the paper's piecewise-linear fit)
  min deceleration      -- the most negative acceleration reached
  inverse TTC at onset  -- max(0, v_ego - v_other) / gap, at brake onset (paper's Fig. 3e x-axis)
  maneuver             -- brake only / swerve / both, from the lateral displacement
  collision             -- box overlap

Writes replication/sweep_aidriver.csv

Run:  python replication/sweep_rear_end_aidriver.py [--repeats 5]
"""
import argparse
import csv
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from aidriver import (  # noqa: E402
    ActiveInferenceDriver, AgentParams, PreferenceParams, RearEndScenario,
)

TIME_GAPS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
SPEEDS = [10.0, 15.0, 20.0, 25.0]   # code/deposit grid, not the SI's (see module notes)
T_BRAKE = 2.0          # shortened from the SI's 5 s; response times are measured relative
                       # to this instant, so the value only affects run length


def analyse_run(res, sc):
    dt = sc.veh.dt
    t = res.t
    a = res.actions[:, 0]
    idx = np.arange(len(t))
    i_brake = int(round(T_BRAKE / dt))

    after = idx >= i_brake
    braking = after & (a < -1.0)
    if braking.any():
        k = int(idx[braking][0])
        rt = t[k] - T_BRAKE
        gap = res.other[k, 0] - res.ego[k, 0] - sc.veh.length
        v_rel = max(res.ego[k, 4] - res.other[k, 4], 0.0)
        inv_ttc = v_rel / max(gap, 1e-3)
    else:
        rt, inv_ttc = np.nan, np.nan

    min_decel = float(a.min())
    lateral = float(np.max(np.abs(res.ego[:, 1])))
    steered = lateral > 0.5
    braked = bool(braking.any())
    if braked and steered:
        maneuver = "both"
    elif braked:
        maneuver = "brake"
    elif steered:
        maneuver = "swerve"
    else:
        maneuver = "none"

    return dict(response_time=rt, min_decel=min_decel, inv_ttc_at_onset=inv_ttc,
                max_lateral=lateral, maneuver=maneuver,
                collided=int(res.collided), min_clearance=res.min_gap)


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--repeats", type=int, default=5)
    ap_.add_argument("--T", type=int, default=50)
    ap_.add_argument("--out", default=os.path.join(HERE, "sweep_aidriver.csv"))
    ap_.add_argument("--restart", action="store_true",
                     help="ignore any existing output and start over")
    args = ap_.parse_args()

    cols = ["v0", "time_gap", "repeat", "response_time", "min_decel", "inv_ttc_at_onset",
            "max_lateral", "maneuver", "collided", "min_clearance"]

    # Resume support: rows are appended as they complete, so an interrupted run loses at most
    # one simulation and can be restarted without redoing the rest. (An earlier version wrote
    # only at the end and lost ~1 h of compute when the process was killed.)
    done = set()
    if os.path.exists(args.out) and not args.restart:
        with open(args.out, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.add((float(row["v0"]), float(row["time_gap"]), int(row["repeat"])))
        print(f"resuming: {len(done)} runs already present in {args.out}")

    new_file = args.restart or not os.path.exists(args.out)
    fh = open(args.out, "w" if new_file else "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(fh, fieldnames=cols)
    if new_file:
        writer.writeheader(); fh.flush()

    t0 = time.time()
    total = len(TIME_GAPS) * len(SPEEDS) * args.repeats
    n = len(done)
    n_run = 0
    try:
        for v0 in SPEEDS:
            for gap in TIME_GAPS:
                for rep in range(args.repeats):
                    if (v0, gap, rep) in done:
                        continue
                    pref = PreferenceParams(v_desired=v0, a_other_min=-6.0)
                    params = AgentParams(horizon=20, n_particles=50, n_policies=100,
                                         cem_iters=8, seed=rep, alpha=0.0)
                    agent = ActiveInferenceDriver(pref, params)
                    sc = RearEndScenario(v0=v0, time_gap=gap, t_brake=T_BRAKE)
                    res = sc.run(agent, T=args.T)
                    r = analyse_run(res, sc)
                    r.update(v0=v0, time_gap=gap, repeat=rep)
                    writer.writerow({k: r[k] for k in cols})
                    fh.flush()
                    os.fsync(fh.fileno())
                    n += 1; n_run += 1
                    if n_run % 5 == 0 or n == total:
                        el = time.time() - t0
                        eta = el / max(n_run, 1) * (total - n) / 60
                        print(f"  {n}/{total}  elapsed {el/60:.1f} min  eta {eta:.1f} min",
                              flush=True)
    finally:
        fh.close()
    print(f"wrote {args.out} ({n} runs total, {(time.time()-t0)/60:.1f} min this session)")


if __name__ == "__main__":
    main()
