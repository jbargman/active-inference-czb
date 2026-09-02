"""Cross-check of an external cue on the registered R.2 pipeline: required deceleration
with a minimum-gap wall (2026-09-02).

Context. A colleague's comfort-zone-boundary proposal (external to this project; see
`docs/handbook/16_appendix_external_rh_model.md`) defines the boundary through the
required deceleration with a minimum acceptable gap g_min and a response delay tau:

    a_req = dv^2 / (2 (gap - g_min - dv tau)),   +inf where the denominator is <= 0.

Its own analysis (external repository, model L1/L3) found that g_min ~ 11.5 m does the
work and tau is not identified. This project's registered R.2 comparison scored plain
required deceleration (g_min = tau = 0) at held-out wRMSE 0.289, and card EL.1 found an
equally weighted linear rule in log gap and log TTC at 0.114. The question here: on the
registered pipeline (same 288 cells, WLS on cell means, leave-one-starting-TTC-out folds,
same threshold model), where does the walled a_req cue land, with g_min fitted inside
each training fold?

Models (identical folds, identical fitter, `cutin2_two_axis.fit_reg`):
  (a) 1D log gap            [the registered reference, 0.1522]
  (c) linear 2D rule        [EL.1, 0.1137]
  (f) log a_req with g_min free, tau = 0     one extra parameter, g_min in [0, 30 m]
  (g) log a_req with g_min and tau free      two extra parameters, tau in [0, 1.5] s
Cells whose denominator is <= 0 get x = +large (the cue is monotone, so this is the
"unresolvable" end); the threshold model handles it as a saturated cell. g_min is bounded
to [0, 30 m] so the wall may exceed some cells' gaps, as in the external fit (g_min ~ 11.5 m
with the smallest design gap at 1.6 m).

Correction, same day: the first run bounded g_min BELOW the smallest design gap (an
implementation slip, not a design choice), which forbade the external wall and scored the
cue at 0.2585 / 0.2534. The bound was corrected to [0, 30 m] and the script re-run; the
models, folds, fitter and decision rule are unchanged. Both numbers are in the worklog.

DECISION RULE (pre-stated): report held-out wRMSE with the EL.1 margin 0.01. If (f) or
(g) is within 0.01 of (c), the two cue families are indistinguishable on this data and
the appendix says so; if (c) beats (f)/(g) by more than 0.01, the linear rule stands as
the better cue on this pipeline; if (f)/(g) beats (c) by more than 0.01, the external cue
is the better one and card EL.2 should carry it as a candidate form.

Run: python replication/czb/cutin2_external_cue.py    Output: out/cutin2_external_cue.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cutin2_field_vs_gap as R  # noqa: E402
import cutin2_two_axis as T      # noqa: E402

OUT = HERE / "out"
KPH = 1000.0 / 3600.0
BIG = 50.0   # log a_req assigned where d <= 0 (a_req = +inf); far above any finite value


def x_areq(cells, g_min, tau):
    gap = cells.distance.to_numpy(float)
    dv = cells.dv_kph.to_numpy(float) * KPH
    d = gap - g_min - dv * tau
    with np.errstate(divide="ignore", invalid="ignore"):
        x = np.where(d > 0, 2 * np.log(dv) - np.log(2.0) - np.log(d), BIG)
    return x


def fit_walled(cells, y, w, free_tau):
    """Inner parameters (g_min, tau) fitted jointly with the threshold model by WLS."""
    gmax = 30.0
    best, best_val = None, np.inf
    taus = (0.0, 0.3, 0.8) if free_tau else (0.0,)
    for g0 in np.linspace(0.0, gmax, 6):
        for t0 in taus:
            x0 = x_areq(cells, g0, t0)
            th0 = T.fit_reg(x0, y, w)
            if th0 is None:
                continue

            def obj(p):
                g, t = p[0], (p[1] if free_tau else 0.0)
                x = x_areq(cells, g, t)
                return T.finite(float(np.sum(w * (R.predict(p[2:] if free_tau else p[1:], x, +1.0) - y) ** 2)))
            p0 = np.concatenate([[g0, t0], th0]) if free_tau else np.concatenate([[g0], th0])
            bnds = ([(0.0, gmax), (0.0, 1.5)] if free_tau else [(0.0, gmax)]) + [(-30, 10), (None, None), (-10, 10)]
            r = minimize(obj, p0, method="L-BFGS-B", bounds=bnds)
            if r.fun < best_val:
                best, best_val = r.x, r.fun
    return best


def held_out_walled(cells, folds, free_tau):
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    params = []
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        p = fit_walled(cells[tr].reset_index(drop=True), y[tr], w[tr], free_tau)
        g, t = p[0], (p[1] if free_tau else 0.0)
        th = p[2:] if free_tau else p[1:]
        pred[te] = R.predict(th, x_areq(cells[te].reset_index(drop=True), g, t), +1.0)
        params.append((g, t))
    return pred, params


def main() -> None:
    cells_all = pd.read_csv(OUT / "cutin2_cells.csv")
    cells = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    folds = cells.ttc_start.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))

    L = ["# An external cue on the registered pipeline: required deceleration with a minimum-gap wall", "",
         "Generated by `replication/czb/cutin2_external_cue.py`; models, folds and decision rule"
         " pre-stated in its docstring. Same 288 CP2-CP5 cells, fitter and leave-one-starting-TTC-out"
         " folds as R.2 and EL.1. Do not edit by hand.", "",
         "| model | free parameters | held-out wRMSE | Spearman(pred, P) |", "|---|---|---|---|"]
    score = {}
    pa, _ = T.held_out(cells, folds, "gap")
    score["gap"] = T.wrmse(y, pa, w)
    L.append(f"| (a) 1D log gap | 3 | {score['gap']:.4f} | {float(spearmanr(pa, y).statistic):+.3f} |")
    pc, _ = T.held_out(cells, folds, "linear")
    score["linear"] = T.wrmse(y, pc, w)
    L.append(f"| (c) linear 2D rule in log gap and log TTC (EL.1) | 4 | {score['linear']:.4f} | "
             f"{float(spearmanr(pc, y).statistic):+.3f} |")
    pf, prm_f = held_out_walled(cells, folds, free_tau=False)
    score["walled"] = T.wrmse(y, pf, w)
    L.append(f"| (f) log a_req with g_min free (tau = 0) | 4 | {score['walled']:.4f} | "
             f"{float(spearmanr(pf, y).statistic):+.3f} |")
    pg, prm_g = held_out_walled(cells, folds, free_tau=True)
    score["walled_tau"] = T.wrmse(y, pg, w)
    L.append(f"| (g) log a_req with g_min and tau free | 5 | {score['walled_tau']:.4f} | "
             f"{float(spearmanr(pg, y).statistic):+.3f} |")
    L += [f"| sampling-noise floor | - | {noise:.4f} | - |", ""]

    best_w = min(score["walled"], score["walled_tau"])
    d = score["linear"] - best_w
    if abs(d) <= 0.01:
        verdict = "the two cue families are INDISTINGUISHABLE on this pipeline (within 0.01)"
    elif d > 0.01:
        verdict = "the walled required-deceleration cue is the BETTER cue on this pipeline"
    else:
        verdict = "the linear rule in log gap and log TTC STANDS as the better cue on this pipeline"
    L += [f"**Pre-stated decision.** linear minus best walled = {d:+.4f}: **{verdict}**.", "",
          "## Fitted wall per training fold", "",
          "| held-out starting TTC | (f) g_min [m] | (g) g_min [m] | (g) tau [s] |", "|---|---|---|---|"]
    for fo, (gf, _), (gg, tg) in zip(sorted(np.unique(folds)), prm_f, prm_g):
        L.append(f"| {fo:.0f} s | {gf:.2f} | {gg:.2f} | {tg:.2f} |")
    L += ["", f"Minimum gap in the design: {cells.distance.min():.1f} m; g_min is bounded to [0, 30 m], and cells with gap - g_min - dv tau <= 0 are saturated.", ""]
    (OUT / "cutin2_external_cue.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
