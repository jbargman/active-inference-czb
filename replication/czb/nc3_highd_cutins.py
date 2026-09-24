"""
Cards NC.0b and NC.3, first pass -- a deceleration detector calibrated on steady following, and
whether the video-fitted cut-in curve predicts when real highD followers respond.

THE PRE-REGISTRATION. Written before the run, on 2026-09-24, before any highD cut-in or
following episode was looked at. `docs/naturalistic_data_plan.md` §2 (NC.0b) and §3 (NC.3) are
the specification; this card is a compressed first pass of both, and says below where it
departs from them.

THE DETECTOR (NC.0b, the plan's own rule). A response is an episode in which the follower's
longitudinal acceleration (along its direction of travel) stays below -a_th for at least T_min.
Grids a_th in {0.5, 1.0, 1.5, 2.0} m/s^2, T_min in {0.3, 0.5, 1.0} s (NAT.Q1, Jonas 2026-09-17;
Delta-v_min not used, as the plan's primary). The false-positive rate is measured on STEADY
FOLLOWING: non-overlapping 3 s windows in which the follower keeps the same preceding vehicle
and lane, the preceding vehicle's |longitudinal acceleration| stays below 0.3 m/s^2, and the
follower is not already below -a_th at the window's start; a false positive is a qualifying
episode starting in the window. Primary: for T_min in ascending order, the smallest a_th with
a false-positive rate under 5%; the first T_min for which one exists. DEPARTURE: the plan's
synthetic-latency validation is not done here, so, by the plan's own stop rule, NO timing claim
is made: the response is "responded within 3 s, yes or no".

THE EVENTS (NC.3). A cut-in: a follower j whose preceding vehicle changes at frame f to a
vehicle i that is in j's lane at f and was in another lane 1 s before, while j itself kept its
lane over that second. At f (the frame highD first lists i as j's leader: i's centre has just
crossed into the lane): bumper gap g (from x, the box length and the driving direction), closing
speed dv = |v_j| - |v_i|, i's width W (highD's "height"), and the looming rate
theta_dot = W dv / (g^2 + W^2/4), exactly as card EL.1b. j must be tracked from f - 1 s to
f + 3 s. Censored and counted: j already below -a_th at f; j changing lane within 3 s. The
primary set is CLOSING cut-ins (dv > 0), the video study's design; opening cut-ins are reported
as a baseline response rate. Response: a qualifying episode starting in [f, f + 3 s].

THE GATE, said in advance: at f the cutter is already half in the lane, so card JJ.9's empirical
gate and card G.1's are both about 1. This card tests the AXIS and the LEVEL, not the gate.

THE PREDICTIONS UNDER TEST, nothing refitted: the video population curve
P = lapse + (1 - lapse) Phi((log theta_dot - log theta_0) / s), primary with card JJ.10's mixture
fit (lapse 0.037, theta_0 0.0320 rad/s, s 1.293; the second cut-in study) and secondary with card
JJ.7's population (lapse 0, theta_0 exp(-3.4632) = 0.0313, s = sqrt(0.8650^2 + 0.5695^2) = 1.036;
the first study, first-exposure-free).

THE RULES.
  (a) TRANSFER, as card TT.1 scored the video population on the track: events binned in deciles of
      theta_dot; weighted RMSE of predicted against observed response rate over the bins; the video
      curve TRANSFERS if it beats chance (the overall rate in every bin). Reported beside it: a
      refit of the same three-parameter curve on highD, held out by recording (5 folds, recording
      id mod 5), and the refit's level against the video level as a ratio.
  (b) THE AXIS CARRIES OVER if the AUC of log theta_dot for the response exceeds both the AUC of
      -log gap and of -log TTC, each difference with a 95% bootstrap interval over recordings
      (200 resamples) excluding zero.
  Rule 0: at least 100 closing cut-ins after censoring, else the card reports the census and stops.

PREDICTIONS. Detector: a_th 1.0 or 1.5 m/s^2 at T_min 0.3 or 0.5 s. Closing cut-ins: a few
thousand; response rate 10 to 25%. (a): the video curve predicts far MORE responses than real
followers make (participants press a button at a comfort boundary; real followers often coast or
tolerate), so it FAILS (a) by level while the refit's level is 2 to 5 times the video's; the refit
beats chance. (b): looming beats TTC; against the gap, uncertain -- on real traffic dv and gap
vary independently, which is the design the video study lacked.

Output: replication/czb/out/nc3_highd_cutins.md, out/nc3_highd_cutins_bins.csv (aggregates);
per-event values cached outside the repository (highD licence).
Run:    python replication/czb/nc3_highd_cutins.py
"""
from __future__ import annotations

import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import norm, rankdata

HERE = Path(__file__).resolve().parent
HIGHD = Path(r"C:\JonasLocal\D_Data\highD-dataset-v1.0\data")
CACHE = Path(r"C:\JonasLocal\D_Data_derived\nc3_events.pkl")
OUT = HERE / "out"
FPS = 25
A_GRID = (0.5, 1.0, 1.5, 2.0)
T_GRID = (0.3, 0.5, 1.0)
WIN = 3 * FPS
PRE = 1 * FPS
LEAD_STEADY = 0.3
VIDEO = {"JJ.10 mixture (study 2)": (0.037, 0.0320, 1.293),
         "JJ.7 population (study 1)": (0.0, float(np.exp(-3.4632)), float(np.hypot(0.8650, 0.5695)))}


def runs_start(below: np.ndarray, min_len: int) -> np.ndarray:
    """bool per frame: a run of `below` of at least min_len frames starts here."""
    out = np.zeros(len(below), bool)
    i, n = 0, len(below)
    while i < n:
        if below[i]:
            j = i
            while j < n and below[j]:
                j += 1
            if j - i >= min_len:
                out[i] = True
            i = j
        else:
            i += 1
    return out


def process(rec: int):
    tr = pd.read_csv(HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "x", "width", "height", "xVelocity", "xAcceleration",
                              "precedingId", "laneId"])
    meta = pd.read_csv(HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection", "class"])
    tr = tr.merge(meta, on="id").sort_values(["id", "frame"]).reset_index(drop=True)
    sgn = np.where(tr.drivingDirection == 1, -1.0, 1.0)
    tr["v"] = np.abs(tr.xVelocity)
    tr["a"] = tr.xAcceleration * sgn
    by = {k: g for k, g in tr.groupby("id")}
    arr = {k: {c: g[c].to_numpy() for c in ("frame", "x", "width", "height", "v", "a",
                                             "precedingId", "laneId", "drivingDirection")}
           for k, g in by.items()}
    starts = {}
    for k, g in arr.items():
        starts[k] = {(a, t): runs_start(g["a"] < -a, max(3, int(round(t * FPS))))
                     for a in A_GRID for t in T_GRID}
    fp = {(a, t): [0, 0] for a in A_GRID for t in T_GRID}
    events = []
    for j, g in arr.items():
        fr, p, lane = g["frame"], g["precedingId"], g["laneId"]
        n = len(fr)
        # --- steady following windows, non-overlapping ------------------------------------
        k = 0
        while k + WIN < n:
            lead = p[k]
            if lead > 0 and np.all(p[k:k + WIN] == lead) and np.all(lane[k:k + WIN] == lane[k]) \
                    and lead in arr:
                L = arr[lead]
                m = np.searchsorted(L["frame"], fr[k])
                if m + WIN <= len(L["frame"]) and L["frame"][m] == fr[k] and \
                        np.all(np.abs(L["a"][m:m + WIN]) < LEAD_STEADY):
                    for key in fp:
                        if g["a"][k] < -key[0]:
                            continue
                        fp[key][1] += 1
                        fp[key][0] += int(starts[j][key][k:k + WIN].any())
                    k += WIN
                    continue
            k += FPS
        # --- cut-ins ----------------------------------------------------------------------
        for q in range(PRE, n - WIN):
            i = p[q]
            if i <= 0 or i == p[q - 1] or i not in arr or lane[q - PRE] != lane[q]:
                continue
            I = arr[i]
            m = np.searchsorted(I["frame"], fr[q])
            if m >= len(I["frame"]) or I["frame"][m] != fr[q] or m < PRE:
                continue
            if I["laneId"][m] != lane[q] or I["laneId"][m - PRE] == lane[q]:
                continue
            d1 = g["drivingDirection"][q]
            if d1 == 2:
                gap = I["x"][m] - (g["x"][q] + g["width"][q])
            else:
                gap = g["x"][q] - (I["x"][m] + I["width"][m])
            if gap <= 0:
                continue
            dv = g["v"][q] - I["v"][m]
            W = I["height"][m]
            lc = bool(np.any(lane[q:q + WIN] != lane[q]))
            row = {"rec": rec, "gap": gap, "dv": dv, "W": W, "v": g["v"][q], "lc": lc,
                   "truck_follower": False}
            for key in fp:
                row[f"pre_{key[0]}_{key[1]}"] = bool(g["a"][q] < -key[0])
                row[f"resp_{key[0]}_{key[1]}"] = bool(starts[j][key][q:q + WIN].any())
            events.append(row)
    return rec, fp, events


def auc(score, y):
    r = rankdata(score)
    n1 = y.sum()
    n0 = len(y) - n1
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def curve(th, x):
    return expit(th[0]) + (1 - expit(th[0])) * norm.cdf((x - th[1]) / np.exp(th[2]))


def fit_curve(x, y):
    best, val = None, np.inf
    for c0 in np.quantile(x, [0.3, 0.5, 0.7, 0.9]):
        for ls in (0.0, 0.7):
            def nll(th):
                pp = np.clip(curve(th, x), 1e-9, 1 - 1e-9)
                return -float(np.sum(y * np.log(pp) + (1 - y) * np.log(1 - pp)))
            r = minimize(nll, np.array([-3.0, c0, ls]), method="L-BFGS-B")
            if r.fun < val:
                best, val = r.x, r.fun
    return best


def binned_wrmse(pred, y, bins):
    df = pd.DataFrame({"p": pred, "y": y, "b": bins})
    g = df.groupby("b").agg(p=("p", "mean"), y=("y", "mean"), n=("y", "size"))
    return float(np.sqrt(np.average((g.p - g.y) ** 2, weights=g.n))), g


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    if CACHE.exists():
        fp_all, ev = pd.read_pickle(CACHE)
    else:
        recs = sorted(int(p_.name[:2]) for p_ in HIGHD.glob("*_tracks.csv"))
        with ProcessPoolExecutor(max_workers=12) as ex:
            res = list(ex.map(process, recs))
        fp_all = {key: [sum(r[1][key][0] for r in res), sum(r[1][key][1] for r in res)]
                  for key in res[0][1]}
        ev = pd.DataFrame([e for r in res for e in r[2]])
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        pd.to_pickle((fp_all, ev), CACHE)
    print(f"{len(ev)} candidate cut-ins [{time.time() - t0:.0f} s]", flush=True)

    fp_rate = {k: v[0] / max(v[1], 1) for k, v in fp_all.items()}
    primary = None
    for t in T_GRID:
        ok = [a for a in A_GRID if fp_rate[(a, t)] < 0.05]
        if ok:
            primary = (min(ok), t)
            break
    L = ["# Cards NC.0b and NC.3, first pass -- the detector, and real highD cut-ins", "",
         "Generated by `replication/czb/nc3_highd_cutins.py`; the detector rule, the events, the"
         " predictions and the rules were pre-stated in its docstring before the run. Aggregates"
         " only (highD licence). Do not edit by hand.", "",
         "## 0 The detector (NC.0b): false-positive rate on steady following", "",
         f"Steady-following windows of 3 s: {fp_all[(0.5, 0.3)][1]:,}.", "",
         "| a_th [m/s^2] | " + " | ".join(f"T_min {t:g} s" for t in T_GRID) + " |",
         "|---|" + "---|" * len(T_GRID)]
    for a in A_GRID:
        L.append(f"| {a:g} | " + " | ".join(f"{fp_rate[(a, t)]:.3f}" for t in T_GRID) + " |")
    if primary is None:
        L += ["", "**No setting keeps the false-positive rate under 5%. The card stops.**"]
        (OUT / "nc3_highd_cutins.md").write_text("\n".join(L), encoding="utf-8")
        return
    a_th, t_min = primary
    L += ["", f"**Primary: a_th = {a_th:g} m/s^2, T_min = {t_min:g} s** (false-positive rate"
          f" {fp_rate[primary]:.3f}). No timing claim is made (the plan's stop rule; latency not"
          " validated here).", ""]

    pre, resp = f"pre_{a_th}_{t_min}", f"resp_{a_th}_{t_min}"
    n_all = len(ev)
    n_pre, n_lc = int(ev[pre].sum()), int((~ev[pre] & ev.lc).sum())
    e = ev[~ev[pre] & ~ev.lc].copy()
    e["closing"] = e.dv > 0
    c = e[e.closing].copy()
    o = e[~e.closing]
    c["theta_dot"] = c.W * c.dv / (c.gap ** 2 + c.W ** 2 / 4)
    c["ttc"] = c.gap / c.dv
    y = c[resp].to_numpy(bool)
    L += ["## 1 The census", "",
          "| set | events | responded within 3 s |", "|---|---|---|",
          f"| candidate cut-ins | {n_all:,} | - |",
          f"| censored: follower already decelerating | {n_pre:,} | - |",
          f"| censored: follower changes lane within 3 s | {n_lc:,} | - |",
          f"| **closing (dv > 0), the primary set** | **{len(c):,}** | {y.mean():.3f} |",
          f"| opening (dv <= 0), baseline | {len(o):,} | {o[resp].mean():.3f} |", "",
          f"Closing cut-ins: median gap {c.gap.median():.1f} m, median dv {c.dv.median():.2f} m/s,"
          f" median looming {c.theta_dot.median():.4f} rad/s (the video's cells: 0.0036 to 1.1,"
          " median 0.0436).", ""]
    if len(c) < 100:
        L += ["**Rule 0 fails: fewer than 100 closing cut-ins. The card stops.**"]
        (OUT / "nc3_highd_cutins.md").write_text("\n".join(L), encoding="utf-8")
        return

    x = np.log(c.theta_dot.to_numpy(float))
    bins = pd.qcut(x, 10, labels=False, duplicates="drop")
    chance = np.full(len(y), y.mean())
    r_chance, _ = binned_wrmse(chance, y, bins)
    preds, rows = {}, []
    for lab, (lap, th0, s) in VIDEO.items():
        preds[lab] = lap + (1 - lap) * norm.cdf((x - np.log(th0)) / s)
    folds = c.rec.to_numpy() % 5
    ho = np.full(len(y), np.nan)
    for f in np.unique(folds):
        th = fit_curve(x[folds != f], y[folds != f])
        ho[folds == f] = curve(th, x[folds == f])
    th_full = fit_curve(x, y)
    r_ho, g_ho = binned_wrmse(ho, y, bins)
    L += ["## 2 Rule (a): does the video curve transfer?", "",
          "| prediction | binned weighted RMSE (deciles of looming) | predicted overall rate |",
          "|---|---|---|"]
    res_a = {}
    for lab, pr in preds.items():
        r, _ = binned_wrmse(pr, y, bins)
        res_a[lab] = r
        L.append(f"| the video curve, {lab}, nothing refitted | {r:.4f} | {pr.mean():.3f} |")
    L += [f"| the same curve REFIT on highD, held out by recording | {r_ho:.4f} | {np.nanmean(ho):.3f} |",
          f"| chance (the overall rate) | {r_chance:.4f} | {y.mean():.3f} |", "",
          f"highD refit: lapse {expit(th_full[0]):.3f}, level {np.exp(th_full[1]):.4f} rad/s, spread"
          f" {np.exp(th_full[2]):.3f}; the level is **{np.exp(th_full[1]) / VIDEO['JJ.10 mixture (study 2)'][1]:.2f}"
          " times** the video's.", ""]
    prim_lab = "JJ.10 mixture (study 2)"
    transfers = res_a[prim_lab] < r_chance
    _, g_tab = binned_wrmse(preds[prim_lab], y, bins)
    tab = pd.DataFrame({"bin": g_tab.index, "n": g_tab.n.values,
                        "looming_median": [float(np.exp(np.median(x[bins == b]))) for b in g_tab.index],
                        "observed": g_tab.y.values, "video_pred": g_tab.p.values,
                        "highd_refit_heldout": g_ho.p.values})
    tab = tab[tab.n >= 5]
    tab.to_csv(OUT / "nc3_highd_cutins_bins.csv", index=False)
    L += ["| looming decile median [rad/s] | events | observed | video curve | highD refit, held out |",
          "|---|---|---|---|---|"]
    for _, r in tab.iterrows():
        L.append(f"| {r.looming_median:.4f} | {int(r.n)} | {r.observed:.3f} | {r.video_pred:.3f} |"
                 f" {r.highd_refit_heldout:.3f} |")

    # --- rule (b): the axis --------------------------------------------------------------
    s_loom, s_gap, s_ttc = x, -np.log(c.gap.to_numpy(float)), -np.log(c.ttc.to_numpy(float))
    A = {"looming": auc(s_loom, y), "gap": auc(s_gap, y), "TTC": auc(s_ttc, y)}
    rng = np.random.default_rng(20260924)
    recs = c.rec.to_numpy()
    ur = np.unique(recs)
    boot = []
    for _ in range(200):
        pick = rng.choice(ur, len(ur))
        idx = np.concatenate([np.flatnonzero(recs == r_) for r_ in pick])
        yy = y[idx]
        if yy.sum() in (0, len(yy)):
            continue
        boot.append((auc(s_loom[idx], yy) - auc(s_gap[idx], yy),
                     auc(s_loom[idx], yy) - auc(s_ttc[idx], yy)))
    boot = np.array(boot)
    ci_g, ci_t = np.percentile(boot[:, 0], [2.5, 97.5]), np.percentile(boot[:, 1], [2.5, 97.5])
    axis_ok = ci_g[0] > 0 and ci_t[0] > 0
    L += ["", "## 3 Rule (b): does the axis carry over?", "",
          "| axis | AUC for the response |", "|---|---|"]
    for k, v in A.items():
        L.append(f"| {k} | {v:.3f} |")
    L += ["", f"Looming minus gap {A['looming'] - A['gap']:+.3f} [{ci_g[0]:+.3f}, {ci_g[1]:+.3f}];"
          f" looming minus TTC {A['looming'] - A['TTC']:+.3f} [{ci_t[0]:+.3f}, {ci_t[1]:+.3f}]"
          " (bootstrap over recordings).", "",
          "## 4 The verdicts on the pre-stated rules", "",
          f"* **(a) the video curve {'TRANSFERS' if transfers else 'does NOT transfer'}**:"
          f" {res_a[prim_lab]:.4f} against chance {r_chance:.4f}.",
          f"* **(b) the axis {'CARRIES OVER' if axis_ok else 'does NOT carry over'}**: both"
          " differences' intervals must exclude zero.", "",
          "Stated in advance and repeated: the response here is a real deceleration of at least"
          f" {a_th:g} m/s^2 for {t_min:g} s; the video's is a button press at a comfort boundary."
          " The mapping between the two is an assumption (the plan's §6).", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nc3_highd_cutins.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
