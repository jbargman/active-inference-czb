"""
Card PT.1 -- do the looming levels of naturalistic emergency braking carry over to comfort
judgments? Farewell's thresholds, fixed rather than fitted, on the second cut-in study.

PRE-STATED before the run (2026-09-13).

WHY. Jonas asked (2026-09-12) whether the released model's perception switch should be a
graded 0-1 transition "from the 0.2 inverse tau". Two numbers need keeping apart:
  * the released model's looming DETECTION threshold, 0.00215 rad/s on the expansion rate --
    below it expansion is invisible (`encoder.py`);
  * Markkula et al. (2016)'s observed demarcation in 116 crashes and 241 near-crashes: few
    drivers braked before looming reached tau^-1 = 0.2 s^-1 (theta_dot about 0.02 rad/s) and
    most within a second after -- a RESPONSE level, which its authors read as the transition
    from slow to fast evidence accumulation.
The second is about ten times the first. Before deciding where a graded 0.2 transition could
sit in the model, this card asks the empirical question the data in hand can answer: is
Farewell's level also where people's comfort judgments turn, when it is imposed rather than
fitted?

WHAT IS RUN. The 288 post-onset cells, leave-one-starting-TTC-out folds, weighted RMSE and
covariates of card EL.1b (`cutin2_looming.py`, imported), one-dimensional probit thresholds
P = b + (1 - b) Phi((x - c)/sigma):
  (h)  x = log theta_dot, c FITTED                   [EL.1b reported 0.1129]
  (h0) x = log theta_dot, c FIXED at log(0.02 rad/s) [Farewell's theta_dot cut-off]
  (i)  x = log(1/TTC),    c FITTED                   [EL.1b reported 0.1679]
  (i0) x = log(1/TTC),    c FIXED at log(0.2 s^-1)   [Farewell's tau^-1 demarcation]
The fixed variants fit only the lapse b and the spread sigma.

DECISION RULE, per axis: Farewell's level CARRIES OVER to these judgments iff the fixed
variant's held-out wRMSE is within 0.01 of the fitted one; otherwise it DOES NOT, and the
direction (fitted threshold above or below Farewell's) is reported with its fold range.
Not a test of the model's perception: every post-onset cell here is far above the model's own
detection threshold (reported), so nothing in this data can speak to that switch.

Reference: Markkula, G., Engström, J., Lodin, J., Bärgman, J., & Victor, T. (2016). A farewell
to brake reaction times? Kinematics-dependent brake response in naturalistic rear-end
emergencies. Accident Analysis and Prevention, 95, 209-226.
https://doi.org/10.1016/j.aap.2016.07.007 -- read from the authors' accepted version.

Output: replication/czb/out/pt1_farewell_thresholds.md
Run:    python replication/czb/pt1_farewell_thresholds.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R      # noqa: E402
import cutin2_two_axis as T          # noqa: E402
import cutin2_looming as LM          # noqa: E402

OUT = HERE / "out"
FAREWELL_THETA_DOT = 0.02    # rad/s
FAREWELL_TAU_INV = 0.2       # 1/s
MODEL_DETECTION = 0.00215    # rad/s, the released model's looming threshold
KPH = 1000.0 / 3600.0


def predict_fixed(th, x, c):
    b = 1.0 / (1.0 + np.exp(-th[0]))
    return b + (1.0 - b) * norm.cdf((x - c) / np.exp(th[1]))


def fit_fixed(x, y, w, c):
    spread = max(np.std(x), 1e-6)
    best, best_val = None, np.inf
    for ls0 in (np.log(spread), np.log(spread / 4 + 1e-9), np.log(spread * 2)):
        for b0 in (-4.0, -2.0):
            r = minimize(lambda th: float(np.sum(w * (predict_fixed(th, x, c) - y) ** 2)),
                         np.array([b0, ls0]), method="L-BFGS-B")
            if r.fun < best_val:
                best, best_val = r.x, r.fun
    return best


def held_out_fixed(x, y, w, folds, c):
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        pred[te] = predict_fixed(fit_fixed(x[tr], y[tr], w[tr], c), x[te], c)
    return pred


def fold_thresholds(x, y, w, folds):
    out = []
    for f in np.unique(folds):
        tr = folds != f
        out.append(float(T.fit_reg(x[tr], y[tr], w[tr])[1]))
    return out


def main() -> None:
    cells_all = pd.read_csv(OUT / "cutin2_cells.csv")
    cells = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    folds = cells.ttc_start.to_numpy(float)
    gap = cells.distance.to_numpy(float)
    dv = cells.dv_kph.to_numpy(float) * KPH
    W, _ = LM.widths_for(cells)
    theta_dot = W * dv / (gap ** 2 + W ** 2 / 4.0)
    x_h = np.log(theta_dot)
    x_i = -np.log(cells.ttc_true.to_numpy(float))

    rows = {}
    rows["h"] = T.wrmse(y, LM.held_out_1d(x_h, y, w, folds), w)
    rows["h0"] = T.wrmse(y, held_out_fixed(x_h, y, w, folds, np.log(FAREWELL_THETA_DOT)), w)
    pred_i, _ = T.held_out(cells, folds, "ttc")
    rows["i"] = T.wrmse(y, pred_i, w)
    rows["i0"] = T.wrmse(y, held_out_fixed(x_i, y, w, folds, np.log(FAREWELL_TAU_INV)), w)

    c_h = float(T.fit_reg(x_h, y, w)[1])
    c_i = float(T.fit_reg(x_i, y, w)[1])
    fh = np.exp(fold_thresholds(x_h, y, w, folds))
    fi = np.exp(fold_thresholds(x_i, y, w, folds))
    chance = float(np.sqrt(np.average((y - np.average(y, weights=w)) ** 2, weights=w)))
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))

    L = ["# Card PT.1 -- Farewell's looming levels, fixed, on comfort judgments", "",
         "Generated by `replication/czb/pt1_farewell_thresholds.py`; models, folds and decision "
         "rule pre-stated in its docstring. Same 288 post-onset cells, folds and metric as card "
         "EL.1b. Do not edit by hand.", "",
         "| model | threshold | free parameters | held-out wRMSE |", "|---|---|---|---|",
         f"| (h) log theta_dot | fitted: {np.exp(c_h):.4f} rad/s (folds {fh.min():.4f}-{fh.max():.4f}) | 3 | {rows['h']:.4f} |",
         f"| (h0) log theta_dot | fixed: {FAREWELL_THETA_DOT} rad/s (Farewell) | 2 | {rows['h0']:.4f} |",
         f"| (i) log 1/TTC | fitted: {np.exp(c_i):.3f} s^-1 (folds {fi.min():.3f}-{fi.max():.3f}) | 3 | {rows['i']:.4f} |",
         f"| (i0) log 1/TTC | fixed: {FAREWELL_TAU_INV} s^-1 (Farewell) | 2 | {rows['i0']:.4f} |",
         f"| chance (full-sample mean, for orientation) | - | - | {chance:.4f} |",
         f"| sampling-noise floor | - | - | {noise:.4f} |", ""]

    for ax, fit_key, fix_key, c_fit, c_far, unit in (
            ("looming rate", "h", "h0", np.exp(c_h), FAREWELL_THETA_DOT, "rad/s"),
            ("inverse tau", "i", "i0", np.exp(c_i), FAREWELL_TAU_INV, "s^-1")):
        d = rows[fix_key] - rows[fit_key]
        verdict = "CARRIES OVER" if d <= 0.01 else "DOES NOT CARRY OVER"
        side = "above" if c_fit > c_far else "below"
        L.append(f"**{ax}: {verdict}** -- fixed minus fitted {d:+.4f}; the fitted threshold "
                 f"{c_fit:.4g} {unit} is {side} Farewell's {c_far} {unit} "
                 f"(ratio {c_fit / c_far:.2f}).")
        L.append("")
    # --- not part of the decision: where the fitted curves cross lower shares --------------
    th_h = T.fit_reg(x_h, y, w)
    th_i = T.fit_reg(x_i, y, w)
    L += ["## Not part of the pre-stated decision: the lower part of the fitted curves", "",
          "The probit threshold is the 50% point of the judgment curve, while Farewell's level "
          "marks where emergency braking *begins* (few before, most within a second after). The "
          "levels at which the full-sample fitted curves reach lower shares of intervention "
          "(above the fitted lapse) are:", "",
          "| share intervening | looming rate [rad/s] | inverse tau [s^-1] |", "|---|---|---|"]
    for q in (0.10, 0.25, 0.50):
        xh = th_h[1] + np.exp(th_h[2]) * norm.ppf(q)
        xi = th_i[1] + np.exp(th_i[2]) * norm.ppf(q)
        L.append(f"| {q:.0%} | {np.exp(xh):.4f} | {np.exp(xi):.3f} |")
    L += ["", f"Fitted spreads: {np.exp(th_h[2]):.3f} (log theta_dot), {np.exp(th_i[2]):.3f} "
          f"(log 1/TTC); lapses {1 / (1 + np.exp(-th_h[0])):.3f} and {1 / (1 + np.exp(-th_i[0])):.3f}.", ""]

    L += [f"For orientation: the looming rate over these 288 cells runs from "
          f"{theta_dot.min():.4f} to {theta_dot.max():.3f} rad/s, so every cell lies above the "
          f"released model's detection threshold of {MODEL_DETECTION} rad/s "
          f"(the smallest by a factor {theta_dot.min() / MODEL_DETECTION:.1f}). "
          f"This data cannot inform that switch.", ""]
    (OUT / "pt1_farewell_thresholds.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
