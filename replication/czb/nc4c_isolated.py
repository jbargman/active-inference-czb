"""
Card NC.4c -- the gate on real traffic with the follower's OWN leader ruled out as the cause.

THE PRE-REGISTRATION. Written 2026-09-25, after card NC.4b, before this was computed.

WHY. Card NC.4b: 2 s and 3 s before the lane switch the empirical highD gate (card JJ.9) is graded
(mean 0.35 and 0.06), yet it does not predict early responses (AUC 0.488 and 0.515), and
multiplying the looming curve by it makes discrimination WORSE (-0.075 [-0.129, -0.027] and -0.061
[-0.104, -0.020]); the gate x core curve also predicts almost no early responses where 0.5 to 10%
occur. The obvious confound: before the switch the follower still has its OWN leader in its lane,
and an early brake may answer that leader, not the cutter. This card removes it.

WHAT IS COMPUTED. Card NC.4's events at k = q - 2 s (the primary; q - 3 s beside it), re-extracted
with, at k, the follower's own leader (highD's precedingId at k, which is not the cutter): its
existence, bumper gap, closing speed and inverse TTC, and the minimum of that leader's acceleration
over [k, q). ISOLATED events: the follower has no own leader at k, or its own leader is not
closing (inverse TTC <= 0.05 s^-1, i.e. TTC above 20 s or opening) AND that leader does not brake
below -1.0 m/s^2 in [k, q). Card NC.4's predictors and rule on the isolated events.

THE RULE. As NC.4 and NC.4b: the GATE CONTRIBUTES if AUC(gate x core) - AUC(core) > 0 with a 95%
bootstrap interval over recordings excluding zero; SATURATED if the gate's mean exceeds 0.9 in
four of five quintiles; and here also: the early responses are ATTRIBUTABLE TO THE CUTTER only if,
on the isolated events, the core (looming to the cutter) still has AUC above 0.6.

PREDICTIONS. Isolation removes about half the events and most early responses; on what remains the
gate CONTRIBUTES (the earlier result was the own leader's doing) -- but with few responses the
interval will be wide. If the gate still does not contribute on isolated events, the real
followers' early responses are not governed by the lateral forecast of JJ.9: they anticipate more
than the lateral motion warrants, as the lab participants did.

Output: replication/czb/out/nc4c_isolated.md (aggregates only)
Run:    python replication/czb/nc4c_isolated.py
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
import nc4_pre_switch as M    # noqa: E402

OUT = HERE / "out"
CACHE = Path(r"C:\JonasLocal\D_Data_derived\nc4c_events_{k}.pkl")
FPS, AHEAD, RATE, A_TH, RUN = 25, 75, 8, 1.0, 3


def extract(args):
    rec, LEAD_K = args
    BACK = LEAD_K + 25
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
            if gap <= 0 or dv <= 0 or np.any(lane[q:q + AHEAD] != lane[q]) or g["a"][k] < -A_TH:
                continue
            clear = lambda kk, mm: abs(I["yc"][mm] - g["yc"][kk]) - (I["height"][mm] + g["height"][kk]) / 2  # noqa: E731
            l0 = clear(k, mk)
            ldot = (l0 - clear(k - RATE, mk - RATE)) / (RATE / FPS)
            # the follower's own leader at k
            o = p[k]
            own = {"own": False, "own_invtau": np.nan, "own_brakes": False}
            if o > 0 and o != i and o in arr:
                O = arr[o]
                mo = np.searchsorted(O["frame"], fr[k])
                if mo < len(O["frame"]) and O["frame"][mo] == fr[k]:
                    og = (O["x"][mo] - (g["x"][k] + g["width"][k])) if d2 else (g["x"][k] - (O["x"][mo] + O["width"][mo]))
                    own = {"own": True,
                           "own_invtau": float((g["v"][k] - O["v"][mo]) / og) if og > 0 else np.inf,
                           "own_brakes": bool(np.any(O["a"][mo:mo + LEAD_K] < -A_TH))}
            st = N.runs_start(g["a"][k:q + AHEAD + 8] < -A_TH, RUN)
            idx = np.flatnonzero(st[:LEAD_K + AHEAD])
            rows.append({"rec": rec, "gap": gap, "dv": dv, "W": I["height"][mk], "l0": l0, "ldot": ldot,
                         "early": bool(len(idx) and idx[0] < LEAD_K), **own})
    return rows


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    e_sorted = np.sort(np.load(M.JJ9)["X"][:, 0])
    surv = lambda x: 1.0 - np.searchsorted(e_sorted, np.asarray(x, float), side="right") / len(e_sorted)  # noqa: E731
    rng = np.random.default_rng(20260925)
    L = ["# Card NC.4c -- the gate on real traffic, the follower's own leader ruled out", "",
         "Generated by `replication/czb/nc4c_isolated.py`; pre-stated in its docstring before the run."
         " Aggregates only. Do not edit by hand.", ""]
    for k in (50, 75):
        path = Path(str(CACHE).format(k=k))
        if path.exists():
            ev = pd.read_pickle(path)
        else:
            with ProcessPoolExecutor(max_workers=12) as ex:
                ev = pd.DataFrame([r for rr in ex.map(extract, [(rec, k) for rec in range(1, 61)]) for r in rr])
            ev.to_pickle(path)
        iso = (~ev.own) | ((ev.own_invtau <= 0.05) & (~ev.own_brakes))
        L += [f"## {k / 25:g} s before the switch{' (primary)' if k == 50 else ''}", "",
              f"{len(ev):,} closing cut-ins; with an own leader at the moment: {int(ev.own.sum()):,}; ISOLATED"
              f" (no own leader, or it is not closing and does not brake): **{int(iso.sum()):,}**.", "",
              "| set | events | early responses | AUC core | AUC gate | AUC gate x core | gate x core - core [95%] | mean gate | verdict |",
              "|---|---|---|---|---|---|---|---|---|"]
        for lab, sub in (("isolated", ev[iso]), ("not isolated", ev[~iso])):
            sub = sub.copy()
            loom = (sub.W * sub.dv / (sub.gap ** 2 + sub.W ** 2 / 4)).to_numpy(float)
            sub["core"] = norm.cdf((np.log(loom) - np.log(M.INT_LEVEL)) / M.INT_SPREAD)
            sub["gate"] = surv(sub.l0.to_numpy(float) + sub.ldot.to_numpy(float) * M.T)
            sub["both"] = sub.core * sub.gate
            y = sub.early.to_numpy(bool)
            if y.sum() < 5:
                L.append(f"| {lab} | {len(sub)} | {int(y.sum())} | - | - | - | too few | - | - |")
                continue
            A = {c: M.auc(sub[c].to_numpy(float), y) for c in ("core", "gate", "both")}
            recs = sub.rec.unique()
            diffs = []
            for _ in range(200):
                idx = np.concatenate([np.flatnonzero(sub.rec.to_numpy() == r) for r in rng.choice(recs, len(recs))])
                yy = y[idx]
                if yy.sum() in (0, len(yy)):
                    continue
                diffs.append(M.auc(sub.both.to_numpy(float)[idx], yy) - M.auc(sub.core.to_numpy(float)[idx], yy))
            ci = np.percentile(diffs, [2.5, 97.5])
            qg = sub.assign(q=pd.qcut(sub.both, 5, labels=False, duplicates="drop")).groupby("q").gate.mean()
            sat = int((qg > 0.9).sum()) >= 4
            v = ("SATURATED" if sat else "GATE CONTRIBUTES" if ci[0] > 0 else "gate does not contribute")
            if A["core"] <= 0.6:
                v += "; NOT attributable to the cutter"
            L.append(f"| {lab} | {len(sub):,} | {int(y.sum())} ({y.mean():.1%}) | {A['core']:.3f} | {A['gate']:.3f} |"
                     f" {A['both']:.3f} | {A['both'] - A['core']:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}] |"
                     f" {sub.gate.mean():.3f} | {v} |")
        L.append("")
        print(f"{k} done [{time.time() - t0:.0f} s]", flush=True)
    L += [f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "nc4c_isolated.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
