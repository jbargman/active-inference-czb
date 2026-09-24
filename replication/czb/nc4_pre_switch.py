"""
Card NC.4 -- the gate on real traffic: do highD followers respond BEFORE the cutter reaches their
lane, and does the gate predict which ones do?

THE PRE-REGISTRATION. Written 2026-09-25, before any pre-switch response was scored.

WHERE THE CARD COMES FROM. `docs/naturalistic_data_plan.md` §3, NC.4 ("How far ahead do real
drivers anticipate?"). Card NC.3 read the follower at the lane switch, where the gate is open by
construction, so it tested only the axis and the level. Card JJ.9 measured the gate's lateral
uncertainty on highD. Jonas, 2026-09-25: "can we get this?" -- yes; this card.

WHAT IS COMPUTED. highD closing cut-ins as card NC.3 defines them (the lane-switch frame q), with
the follower tracked from q - 2 s to q + 3 s. At the PRE-SWITCH MOMENT k = q - 1 s: bumper gap,
closing speed, the cutter's width, looming theta_dot (card EL.1b's formula); the cutter's
edge-to-edge lateral clearance to the follower l0 = |yc_i - yc_j| - (h_i + h_j)/2 and its rate
ldot over the preceding 0.32 s. Censored: the follower already below -1.0 m/s^2 at k; the follower
changing lane before q + 3 s. EARLY RESPONSE: a qualifying episode (a_th 1.0 m/s^2, T_min 0.12 s,
card NC.0b-lat's timing-valid setting) starting in [k, q) -- before the cutter's centre crosses.
THREE PREDICTORS of an early response, nothing fitted:
  core   the video intervention curve on looming at k (card JJ.10, level 0.0320 rad/s, spread
         1.293, no lapse);
  gate   card JJ.9's EMPIRICAL highD gate at k, P_highD(e > l0 + ldot x 3 s), from JJ.9's cached
         error distribution;
  both   gate x core -- the free-energy reading F's mixture form (card JJ.10).

THE RULE. The GATE CONTRIBUTES on real traffic if the AUC of gate x core for early responses
exceeds the AUC of core alone, with a 95% bootstrap interval over recordings (200) excluding zero.
Reported beside it: the AUC of the gate alone, the calibration (predicted mean against observed
early-response rate, and by quintile of gate x core), and the share of all responses within 3 s of
the switch that start BEFORE it.

PREDICTIONS. Early responses are a minority of responses (10 to 30%). The gate contributes: a
cutter already moving fast toward the lane at 1 s before the switch opens it; the difference in
AUC +0.03 to +0.10. Calibration: gate x core underpredicts early responses little, since both
parts are measured on real data or transferred within 20%.

Output: replication/czb/out/nc4_pre_switch.md (aggregates only)
Run:    python replication/czb/nc4_pre_switch.py
"""
from __future__ import annotations

import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nc3_highd_cutins as N  # noqa: E402

OUT = HERE / "out"
CACHE = Path(r"C:\JonasLocal\D_Data_derived\nc4_events.pkl")
JJ9 = Path(r"C:\JonasLocal\D_Data_derived\jj9_samples.npz")
FPS, BACK, AHEAD, LEAD_K, RATE = 25, 50, 75, 25, 8
A_TH, RUN = 1.0, 3
INT_LEVEL, INT_SPREAD, T = 0.0320, 1.293, 3.0


def extract(rec: int):
    tr = pd.read_csv(N.HIGHD / f"{rec:02d}_tracks.csv",
                     usecols=["frame", "id", "x", "y", "width", "height", "xVelocity", "xAcceleration",
                              "precedingId", "laneId"])
    meta = pd.read_csv(N.HIGHD / f"{rec:02d}_tracksMeta.csv", usecols=["id", "drivingDirection", "class"])
    tr = tr.merge(meta, on="id").sort_values(["id", "frame"]).reset_index(drop=True)
    tr["v"] = tr.xVelocity.abs()
    tr["a"] = tr.xAcceleration * np.where(tr.drivingDirection == 1, -1.0, 1.0)
    tr["yc"] = tr.y + tr.height / 2
    arr = {k: {c: g[c].to_numpy() for c in ("frame", "x", "yc", "width", "height", "v", "a", "precedingId",
                                             "laneId", "drivingDirection")} | {"cls": g["class"].iloc[0]}
           for k, g in tr.groupby("id")}
    rows = []
    for j, g in arr.items():
        if g["cls"] != "Car":
            continue
        fr, p, lane = g["frame"], g["precedingId"], g["laneId"]
        n = len(fr)
        for q in range(BACK, n - AHEAD):
            i = p[q]
            if i <= 0 or i == p[q - 1] or i not in arr or lane[q - BACK] != lane[q]:
                continue
            I = arr[i]
            m = np.searchsorted(I["frame"], fr[q])
            if m >= len(I["frame"]) or I["frame"][m] != fr[q] or m < BACK:
                continue
            if I["laneId"][m] != lane[q] or I["laneId"][m - 25] == lane[q]:
                continue
            k, mk = q - LEAD_K, m - LEAD_K
            d2 = g["drivingDirection"][k] == 2
            gap = (I["x"][mk] - (g["x"][k] + g["width"][k])) if d2 else (g["x"][k] - (I["x"][mk] + I["width"][mk]))
            dv = g["v"][k] - I["v"][mk]
            if gap <= 0 or dv <= 0:
                continue
            if np.any(lane[q:q + AHEAD] != lane[q]):
                continue
            if g["a"][k] < -A_TH:
                continue
            clear = lambda kk, mm: abs(I["yc"][mm] - g["yc"][kk]) - (I["height"][mm] + g["height"][kk]) / 2  # noqa: E731
            l0 = clear(k, mk)
            ldot = (l0 - clear(k - RATE, mk - RATE)) / (RATE / FPS)
            W = I["height"][mk]
            st = N.runs_start(g["a"][k:q + AHEAD + 8] < -A_TH, RUN)
            idx = np.flatnonzero(st[:LEAD_K + AHEAD])
            first = idx[0] - LEAD_K if len(idx) else np.nan          # relative to the switch, frames
            rows.append({"rec": rec, "gap": gap, "dv": dv, "W": W, "l0": l0, "ldot": ldot,
                         "early": bool(len(idx) and idx[0] < LEAD_K), "any": bool(len(idx)),
                         "onset_rel_s": first / FPS if np.isfinite(first) else np.nan})
    return rows


def auc(score, y):
    from scipy.stats import rankdata
    r = rankdata(score)
    n1, n0 = y.sum(), len(y) - y.sum()
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    if CACHE.exists():
        ev = pd.read_pickle(CACHE)
    else:
        with ProcessPoolExecutor(max_workers=12) as ex:
            ev = pd.DataFrame([r for rr in ex.map(extract, range(1, 61)) for r in rr])
        ev.to_pickle(CACHE)
    e_sorted = np.sort(np.load(JJ9)["X"][:, 0])
    surv = lambda x: 1.0 - np.searchsorted(e_sorted, np.asarray(x, float), side="right") / len(e_sorted)  # noqa: E731
    loom = (ev.W * ev.dv / (ev.gap ** 2 + ev.W ** 2 / 4)).to_numpy(float)
    ev["core"] = norm.cdf((np.log(loom) - np.log(INT_LEVEL)) / INT_SPREAD)
    ev["gate"] = surv(ev.l0.to_numpy(float) + ev.ldot.to_numpy(float) * T)
    ev["both"] = ev.core * ev.gate
    y = ev.early.to_numpy(bool)
    A = {k: auc(ev[k].to_numpy(float), y) for k in ("core", "gate", "both")}
    rng = np.random.default_rng(20260925)
    recs = ev.rec.unique()
    diffs = []
    for _ in range(200):
        idx = np.concatenate([np.flatnonzero(ev.rec.to_numpy() == r) for r in rng.choice(recs, len(recs))])
        yy = y[idx]
        if yy.sum() in (0, len(yy)):
            continue
        diffs.append(auc(ev.both.to_numpy(float)[idx], yy) - auc(ev.core.to_numpy(float)[idx], yy))
    ci = np.percentile(diffs, [2.5, 97.5])
    verdict = "the GATE CONTRIBUTES" if ci[0] > 0 else "the gate does NOT contribute detectably"
    q = pd.qcut(ev.both, 5, labels=False, duplicates="drop")
    cal = ev.assign(q=q).groupby("q").agg(n=("early", "size"), obs=("early", "mean"), pred=("both", "mean"),
                                          gate=("gate", "mean"))
    resp = ev[ev["any"]]
    L = ["# Card NC.4 -- the gate on real traffic: responses before the lane switch", "",
         "Generated by `replication/czb/nc4_pre_switch.py`; pre-stated in its docstring before the run."
         " Aggregates only. Do not edit by hand.", "",
         f"{len(ev):,} closing cut-ins (closing at 1 s before the switch; follower not braking then, not"
         f" changing lane). Early responses (>= 1.0 m/s^2 starting in the last second before the switch):"
         f" **{y.sum()}** ({y.mean():.1%}). Of the {len(resp)} responses within 3 s after the switch or"
         f" 1 s before it, **{np.mean(resp.early):.0%} start before the switch**; response onset relative"
         f" to the switch, median {resp.onset_rel_s.median():+.2f} s.", "",
         "| predictor at 1 s before the switch | AUC for an early response |", "|---|---|",
         f"| core: the video curve on looming | {A['core']:.3f} |",
         f"| gate: card JJ.9's empirical highD gate | {A['gate']:.3f} |",
         f"| **gate x core (the free-energy reading)** | **{A['both']:.3f}** |", "",
         f"gate x core minus core: {A['both'] - A['core']:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}] (bootstrap over"
         f" recordings). **{verdict}.**", "",
         "Calibration by quintile of gate x core:", "",
         "| quintile | events | mean gate | predicted | observed early-response rate |", "|---|---|---|---|---|"]
    for k, r in cal.iterrows():
        L.append(f"| {int(k) + 1} | {int(r.n)} | {r.gate:.3f} | {r.pred:.3f} | {r.obs:.3f} |")
    L += ["", f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nc4_pre_switch.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
