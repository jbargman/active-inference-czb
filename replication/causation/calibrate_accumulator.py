"""
Calibrate the tier-1 accumulator (src/causation/response.py, ActiveInferenceResponse) on
the authors' deposited rear-end runs, so that its attentive brake onsets reproduce the
closed-loop model's.

For each of the 896 baseline trials: build the pre-response path (the deposit's ego
trajectory up to its executed brake onset is a zero-control reference plan, i.e. constant
speed; it is extended at constant speed beyond the onset), compute eps_tier1(t) with the
same function the causation runner uses (pointwise code-form field + zero-noise prediction
channel), and find the drift rate lambda whose first threshold crossing (+ 0.2 s pedal)
best matches the deposit's brake onset (first executed a <= -1 m/s^2, seeds.csv).

Writes replication/causation/accumulator_calibration.json and prints the table.
Usage: python replication/causation/calibrate_accumulator.py
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from causation.config import CausationConfig                      # noqa: E402
from causation.response import ActiveInferenceResponse            # noqa: E402
from causation.simulate import PreResponseKinematics              # noqa: E402

OSF = REPO / "external" / "gs4bu-osfstorage-archive" / "Results_rear_end" / "Results_rear_end"
SEEDS = REPO / "replication" / "osf" / "seeds.csv"
OUT = REPO / "replication" / "causation" / "accumulator_calibration.json"
DT, L = 0.2, 4.2


def pre_from_deposit(eta_s: np.ndarray, onset_idx: int) -> PreResponseKinematics:
    T = eta_s.shape[0]
    t = np.arange(T) * DT
    x_l, v_l = eta_s[:, 5] - L, eta_s[:, 9]           # lead rear bumper, front bumper of ego at x_ego + ... use center minus L
    x_f, v_f = eta_s[:, 0].copy(), eta_s[:, 4].copy()
    # beyond the executed onset, continue the ego at constant speed (counterfactual no response)
    k = max(onset_idx, 1)
    v0 = v_f[:k].mean()
    v_f[k:] = v0
    x_f[k:] = x_f[k - 1] + v0 * DT * np.arange(1, T - k + 1)
    gap = x_l - x_f
    with np.errstate(divide="ignore", invalid="ignore"):
        tau_inv = np.where(gap > 0.01, (v_f - v_l) / np.maximum(gap, 0.01), np.inf)
    crash = gap <= 0
    t_crash = float(t[np.argmax(crash)]) if crash.any() else np.nan
    a_l = np.gradient(v_l, DT)
    t_on = float(t[np.argmax(a_l < -0.1)]) if (a_l < -0.1).any() else np.nan
    return PreResponseKinematics(t, x_f, v_f, x_l, v_l, gap, tau_inv, t_crash, t_on)


def main() -> None:
    seeds = pd.read_csv(SEEDS)
    seeds = seeds[seeds.brake_onset_idx >= 0]
    cfg = CausationConfig(dt=DT)
    eps_list, onset_list, lead_on = [], [], []
    for exp, g in seeds.groupby("exp"):
        with open(OSF / "Exp_{}".format(exp) / "Exp_{}.pkl".format(exp), "rb") as f:
            eta = pickle.load(f)["eta"].astype(np.float64)
        for _, r in g.iterrows():
            s = int(r.seed)
            pre = pre_from_deposit(eta[s], int(r.brake_onset_idx))
            m = ActiveInferenceResponse(); m.prepare(pre, cfg)
            eps_list.append(np.nan_to_num(m.eps, nan=0.0)); onset_list.append(int(r.brake_onset_idx)); lead_on.append(int(r.lead_onset_idx))
        print("Exp_{} done".format(exp))
    onset = np.array(onset_list); lead_on = np.array(lead_on)
    rows = []
    for lam in np.logspace(-7, -3, 81):
        pred = []
        for e in eps_list:
            E = np.cumsum(lam * e * DT)
            i = int(np.argmax(E >= 1.0)) if (E >= 1.0).any() else -1
            pred.append(i + int(round(cfg.ai_pedal_delay / DT)) if i >= 0 else -1)
        pred = np.array(pred)
        ok = pred >= 0
        err = (pred[ok] - onset[ok]) * DT
        rows.append(dict(lam=lam, n_pred=int(ok.sum()), median_err=float(np.median(err)) if ok.any() else np.nan,
                         mad=float(np.median(np.abs(err))) if ok.any() else np.nan,
                         within_0p2=float(np.mean(np.abs(err) <= 0.2 + 1e-9)) if ok.any() else 0.0,
                         within_0p6=float(np.mean(np.abs(err) <= 0.6 + 1e-9)) if ok.any() else 0.0))
    df = pd.DataFrame(rows)
    # pick: maximize the share within 0.2 s, tie-break on MAD
    best = df.sort_values(["within_0p2", "mad"], ascending=[False, True]).iloc[0]
    # also the level method on the same eps
    lv_rows = []
    for lev in np.logspace(0, 5, 51):
        pred = np.array([int(np.argmax(e >= lev)) if (e >= lev).any() else -1 for e in eps_list])
        ok = pred >= 0; err = (pred[ok] - onset[ok]) * DT
        lv_rows.append(dict(level=lev, within_0p2=float(np.mean(np.abs(err) <= 0.2 + 1e-9)) if ok.any() else 0.0,
                            mad=float(np.median(np.abs(err))) if ok.any() else np.nan, median_err=float(np.median(err)) if ok.any() else np.nan))
    lv = pd.DataFrame(lv_rows); best_lv = lv.sort_values(["within_0p2", "mad"], ascending=[False, True]).iloc[0]
    # benign-phase eps level (before the lead onset) for the record
    pre_eps = np.concatenate([e[: k] for e, k in zip(eps_list, lead_on)])
    res = dict(n_trials=len(eps_list), lambda_best=float(best.lam), within_0p2=float(best.within_0p2),
               within_0p6=float(best.within_0p6), median_err_s=float(best.median_err), mad_s=float(best.mad),
               level_best=float(best_lv.level), level_within_0p2=float(best_lv.within_0p2), level_mad_s=float(best_lv.mad),
               eps_before_lead_onset_median=float(np.median(pre_eps)), eps_before_lead_onset_max=float(np.max(pre_eps)),
               pedal_delay_s=cfg.ai_pedal_delay, eps_definition="pointwise code-form field + zero-noise constant-acceleration prediction channel, H=6 s")
    OUT.write_text(json.dumps(res, indent=2))
    pd.set_option("display.width", 200)
    print(df[df.lam.between(best.lam / 10, best.lam * 10)].to_string(index=False))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
