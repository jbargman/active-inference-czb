"""
Card NC.3o -- are "gentle" and "hard" two levels on ONE observation? A prediction the free-energy
reading makes and the separate threshold curves do not.

THE PRE-REGISTRATION. Written 2026-09-25, before this was computed.

WHY. `docs/looming_as_free_energy.md` and the two-boundary work (NC.3h to NC.3n) read the comfort
zone as two preferences over the same observation: a gentle level and a hard level, with one
precision of perceiving the observation. If so, the three-way answer nothing / gently / hard is an
ORDERED model on one axis with one spread: P(at least gentle) = Phi((x - c1)/s), P(hard) =
Phi((x - c2)/s), c2 > c1 -- three parameters predicting two shares per cell. The alternative is two
unrelated boundaries, each with its own spread (four parameters). Jonas, 2026-09-25: "Can you run 7?
If so do it." This is the part of that list the trusted data can test.

DATA. The second study only (card AC.1: its serial dependence is small, +0.047; the first study's
Button design is heavily dependent within scenario, +0.32, and was validation-only under decision
8). Its third question is the EXPECTED VEHICLE ACTION (0 nothing, 1 gently, 2 hard). 288 post-onset
cells; axis log looming (card EL.1b, `jj6_belief_gate.looming_axis`), which NC.3l found best for the
hard judgment; the registered folds (leave-one-starting-TTC-out); weights the cell counts.

MODELS, fitted by binomial likelihood on both shares per cell:
  O   ordered: c1, c2 (> c1), one spread s                                     3 parameters
  S   separate: (c1, s1) for "at least gentle", (c2, s2) for "hard"             4 parameters
  O-TTC  the ordered model on -log TTC, for the axis comparison                 3 parameters
Metric: held-out weighted RMSE over the two shares stacked (576 values).

THE RULE. TWO LEVELS ON ONE OBSERVATION is SUPPORTED if O's held-out score is within 0.005 of S's
or better; NOT SUPPORTED if S beats O by more than 0.005 (the spreads differ: two distinct
processes). Reported beside it: the fitted levels in rad/s, their ratio, and where the INTERVENTION
level (card JJ.10, 0.032 rad/s) falls between c1 and c2.

PREDICTIONS. SUPPORTED (O within 0.005 of S); gentle level about 0.03 to 0.05 rad/s, hard about 0.11
(NC.3n: 0.114), ratio about 3; the intervention level near the gentle one. O on looming beats O on
TTC by 0.03 or more.

Output: replication/czb/out/nc3o_two_levels_one_observation.md
Run:    python replication/czb/nc3o_two_levels_one_observation.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cutin2_field_vs_gap as R   # noqa: E402
import jj6_belief_gate as J6      # noqa: E402

OUT = HERE / "out"
INT_LEVEL = 0.0320


def shares(th, x, model):
    if model == "S":
        c1, ls1, c2, ls2 = th
        return norm.cdf((x - c1) / np.exp(ls1)), norm.cdf((x - c2) / np.exp(ls2))
    c1, dc, ls = th
    s = np.exp(ls)
    return norm.cdf((x - c1) / s), norm.cdf((x - (c1 + np.exp(dc))) / s)


def nll(th, x, k1, k2, n, model):
    p1, p2 = shares(th, x, model)
    p1, p2 = np.clip(p1, 1e-9, 1 - 1e-9), np.clip(p2, 1e-9, 1 - 1e-9)
    return -float(np.sum(k1 * np.log(p1) + (n - k1) * np.log(1 - p1) + k2 * np.log(p2) + (n - k2) * np.log(1 - p2)))


def fit(x, k1, k2, n, model):
    best, val = None, np.inf
    for c0 in np.quantile(x, [0.3, 0.5, 0.7]):
        starts = ([np.array([c0, 0.0, c0 + 1.0, 0.0])] if model == "S"
                  else [np.array([c0, 0.0, 0.0]), np.array([c0, -1.0, 0.3])])
        for th0 in starts:
            r = minimize(nll, th0, args=(x, k1, k2, n, model), method="L-BFGS-B")
            if r.fun < val:
                best, val = r.x, r.fun
    return best


def held_out(x, k1, k2, n, folds, model):
    p1h, p2h = np.full(len(x), np.nan), np.full(len(x), np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        th = fit(x[tr], k1[tr], k2[tr], n[tr], model)
        p1h[te], p2h[te] = shares(th, x[te], model)
    y = np.concatenate([k1 / n, k2 / n])
    pr = np.concatenate([p1h, p2h])
    w = np.concatenate([n, n])
    return float(np.sqrt(np.average((pr - y) ** 2, weights=w)))


def main() -> None:
    tr = pd.read_csv(R.TRIALS, low_memory=False)
    tr = tr[~tr.video.str.contains("dummy") & tr.CZB_2.isin([0, 1, 2])]
    g = tr.groupby("video").agg(n=("CZB_2", "size"), k1=("CZB_2", lambda v: int(np.sum(v >= 1))),
                                k2=("CZB_2", lambda v: int(np.sum(v == 2)))).reset_index()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")[["video", "cp", "ttc_start", "ttc_true", "distance", "dv_kph"]]
    d = cells.merge(g, on="video")
    d["x_loom"] = J6.looming_axis(d)
    d = d[d.cp != "CP1"].reset_index(drop=True)
    x, xt = d.x_loom.to_numpy(float), -np.log(d.ttc_true.to_numpy(float))
    k1, k2, n, f = d.k1.to_numpy(float), d.k2.to_numpy(float), d.n.to_numpy(float), d.ttc_start.to_numpy(float)
    rO, rS, rOT = held_out(x, k1, k2, n, f, "O"), held_out(x, k1, k2, n, f, "S"), held_out(xt, k1, k2, n, f, "O")
    thO, thS = fit(x, k1, k2, n, "O"), fit(x, k1, k2, n, "S")
    g1, g2 = float(np.exp(thO[0])), float(np.exp(thO[0] + np.exp(thO[1])))
    verdict = "SUPPORTED" if rO <= rS + 0.005 else "NOT SUPPORTED"
    y = np.average(np.concatenate([k1 / n, k2 / n]), weights=np.concatenate([n, n]))
    chance = float(np.sqrt(np.average((np.concatenate([np.full(len(n), np.average(k1 / n, weights=n)),
                                                        np.full(len(n), np.average(k2 / n, weights=n))])
                                       - np.concatenate([k1 / n, k2 / n])) ** 2, weights=np.concatenate([n, n]))))
    L = ["# Card NC.3o -- gentle and hard as two levels on one observation (second study)", "",
         "Generated by `replication/czb/nc3o_two_levels_one_observation.py`; pre-stated in its"
         " docstring before the run. Do not edit by hand.", "",
         "The second study's question: \"What would you expect your vehicle to do, assuming you do not"
         " intervene?\" (nothing / gently / hard). 288 post-onset cells; the two shares \"at least"
         " gently\" and \"hard\" per cell.", "",
         "| model | parameters | held out (both shares, registered folds) |", "|---|---|---|",
         f"| **O: two levels, one spread, on looming** | 3 | **{rO:.4f}** |",
         f"| S: two independent boundaries on looming | 4 | {rS:.4f} |",
         f"| O on -log TTC | 3 | {rOT:.4f} |",
         f"| chance (each share's mean) | - | {chance:.4f} |", "",
         f"**{verdict}** (O minus S {rO - rS:+.4f}; rule: O within 0.005 of S or better).", "",
         f"Model O's levels: gentle **{g1:.4f} rad/s**, hard **{g2:.4f} rad/s** (ratio {g2 / g1:.2f}),"
         f" spread {np.exp(thO[2]):.2f} log units. Model S's spreads: {np.exp(thS[1]):.2f} (gentle),"
         f" {np.exp(thS[3]):.2f} (hard). The intervention level (JJ.10, {INT_LEVEL}) sits"
         f" {'between the two' if g1 <= INT_LEVEL <= g2 else ('below the gentle level' if INT_LEVEL < g1 else 'above the hard level')}"
         f" ({INT_LEVEL / g1:.2f} times the gentle level).", ""]
    (OUT / "nc3o_two_levels_one_observation.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
