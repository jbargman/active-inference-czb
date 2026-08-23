"""
Deposit-level checks behind docs/method_review.md (review of Schumann et al. 2026).

Reads the 28 baseline rear-end runs in the OSF deposit (external/gs4bu-osfstorage-archive)
and writes four tables to replication/osf/review/:

  offroad.csv      when and on which side the ego leaves the road, per condition
  perception.csv   perception delay (belief about lead acceleration) vs the looming-threshold
                   prediction, per condition
  benign_eps.csv   surprise per step before the lead brakes, its composition, and the evidence
                   accumulated before onset, per condition
  figure_conditions.txt  re-plan and brake response-time distributions for the two conditions
                   shown in the paper's Fig. 3a and 3b

Needs replication/osf/baseline_conditions.csv and seeds.csv (from validate_osf.py).
Pickle layout (verified): eta (S, T, 14) true state with columns
  0 x_ego, 1 y_ego, 2 theta_ego, 3 delta_ego, 4 v_ego, 5 x_tar, 6 y_tar, 7 theta_tar,
  8 delta_tar, 9 v_tar, 10 a_tar, 11 w_tar, 12 t_to_brake, 13 j_brake;
b (S, T, 75, 14) belief particles with a two-column gaze one-hot prefix, so a_tar is column 12;
v (S, T, 8) pragmatic-value components per executed step in the order
  [v, a, w, lane, heading, gaze, collision/safety, epistemic] (reward.forward_sep + epistemic).

Usage: python replication/review_osf.py
"""
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OSF = REPO / "external" / "gs4bu-osfstorage-archive" / "Results_rear_end" / "Results_rear_end"
OUT = REPO / "replication" / "osf" / "review"
BASE = REPO / "replication" / "osf" / "baseline_conditions.csv"
SEEDS = REPO / "replication" / "osf" / "seeds.csv"

W, D, DT = 3.65, 1.72, 0.2          # lane width, vehicle width, time step (setups)
PHI0 = 0.00215                       # looming threshold (rad/s)
LAM = 10 ** -5.95                    # evidence drift rate
LEAD_ON = -0.1                       # lead acceleration marking braking onset
A_BEL = -0.5                         # belief mean of lead acceleration counted as "perceived"
N_PRE = 4                            # steps before lead onset (onset is step 4 = 0.8 s)


def load(exp: int) -> dict:
    with open(OSF / "Exp_{}".format(exp) / "Exp_{}.pkl".format(exp), "rb") as f:
        return pickle.load(f)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(BASE)
    offroad, perception, benign = [], [], []

    for _, r in base.iterrows():
        exp = int(r.exp)
        d = load(exp)
        eta = d["eta"].astype(np.float64)
        b = d["b"].astype(np.float64)
        v = d["v"].astype(np.float64)
        S, T = eta.shape[:2]
        y, x, ve = eta[:, :, 1], eta[:, :, 0], eta[:, :, 4]
        xt, vt, at = eta[:, :, 5], eta[:, :, 9], eta[:, :, 10]
        onset = np.array([int(np.argmax(at[s] < LEAD_ON)) for s in range(S)])

        # --- road departures (authors' definition, Analysis_rear_end.py:843)
        right = y < -0.5 * (W - D)
        left = y > W + 0.5 * (W - D)
        off = right | left
        first = np.array([int(np.argmax(off[s])) if off[s].any() else -1 for s in range(S)])
        n_off = int((first >= 0).sum())
        offroad.append(dict(
            exp=exp, v0=r.v0, thw0=r.thw0, x0=r.x_tar, lead_onset_s=float(np.median(onset)) * DT,
            n_seeds=S, n_off_road=n_off, frac_off_road=round(n_off / S, 3),
            n_before_onset=int(sum(1 for s in range(S) if 0 <= first[s] <= onset[s])),
            n_right=int(sum(1 for s in range(S) if first[s] >= 0 and right[s, first[s]])),
            n_left=int(sum(1 for s in range(S) if first[s] >= 0 and left[s, first[s]])),
            t_off_median_s=float(np.median(first[first >= 0])) * DT if n_off else np.nan,
            max_abs_y_before_onset=float(np.max([np.abs(y[s, :onset[s] + 1]).max() for s in range(S)])),
            max_abs_dv_before_onset=float(np.max([np.abs(ve[s, onset[s]] - ve[s, 0]) for s in range(S)])),
        ))

        # --- perception delay vs looming-threshold prediction
        a_bel = b[:, :, :, 12].mean(2)
        delays, dv_perc, dv_pred = [], [], []
        for s in range(S):
            idx = np.where((a_bel[s] < A_BEL) & (np.arange(T) >= onset[s]))[0]
            if len(idx) == 0:
                continue
            p = int(idx[0])
            delays.append((p - onset[s]) * DT)
            dv_perc.append(ve[s, p] - vt[s, p])
            dx0 = xt[s, onset[s]] - x[s, onset[s]]
            dv_pred.append(PHI0 * (dx0 ** 2 + D ** 2 / 4) / D)
        perception.append(dict(
            exp=exp, v0=r.v0, thw0=r.thw0, x0=r.x_tar, n=len(delays),
            delay_median_s=float(np.median(delays)), delay_min_s=float(np.min(delays)),
            delay_max_s=float(np.max(delays)), n_seeds_at_median=int(np.sum(np.isclose(delays, np.median(delays)))),
            dv_at_perception=float(np.median(dv_perc)), dv_threshold_predicted=float(np.median(dv_pred)),
        ))

        # --- surprise before the lead brakes
        prag = -v[:, :, :7].sum(-1)           # residual information of the pragmatic value
        coll = -v[:, :, 6]
        pre = prag[:, :N_PRE]
        benign.append(dict(
            exp=exp, v0=r.v0, thw0=r.thw0,
            eps_pre_median=float(np.median(pre)),
            collision_term_share=float(np.median(coll[:, :N_PRE]) / np.median(pre)),
            E_at_onset_median=float(np.median(LAM * pre.sum(1))),
            benign_steps_to_replan=float(np.median(1.0 / (LAM * pre.mean(1)))),
            epistemic_median=float(np.median(v[:, :N_PRE, 7])),
            velocity_term_median=float(np.median(v[:, :N_PRE, 0])),
            effort_term_median=float(np.median(v[:, :N_PRE, 1])),
        ))
        print("Exp_{} done".format(exp))

    pd.DataFrame(offroad).to_csv(OUT / "offroad.csv", index=False)
    pd.DataFrame(perception).round(4).to_csv(OUT / "perception.csv", index=False)
    pd.DataFrame(benign).round(4).to_csv(OUT / "benign_eps.csv", index=False)

    # --- the two figure conditions
    seeds = pd.read_csv(SEEDS)
    lines = []
    for exp, label in [(10, "Fig. 3a condition (15 m/s, 1.5 s gap)"), (4, "Fig. 3b condition (25 m/s, 1.0 s gap)")]:
        s = seeds[seeds.exp == exp]
        base_row = base[base.exp == exp].iloc[0]
        lines.append("{} = Exp_{}".format(label, exp))
        lines.append("  re-plan after onset : median {:.2f}  IQR {:.2f}-{:.2f}  min {:.2f}  max {:.2f}".format(
            s.rt_replan.median(), s.rt_replan.quantile(.25), s.rt_replan.quantile(.75), s.rt_replan.min(), s.rt_replan.max()))
        lines.append("  brake RT (a<=-1)    : median {:.2f}  IQR {:.2f}-{:.2f}  min {:.2f}  max {:.2f}  n={}".format(
            s.rt_brake.median(), s.rt_brake.quantile(.25), s.rt_brake.quantile(.75), s.rt_brake.min(), s.rt_brake.max(), int(s.rt_brake.notna().sum())))
        lines.append("  brake RT value counts: {}".format(s.rt_brake.round(2).value_counts().sort_index().to_dict()))
        lines.append("  outcomes (deposit)  : leave road {:.3f}, collision {:.3f}, overtaking {:.3f}, brake only {:.3f}, brake+steer {:.3f}".format(
            base_row.leave_road, base_row.collision, base_row.overtaking_post, base_row.braking_post, base_row.brake_steer_post))
    (OUT / "figure_conditions.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
