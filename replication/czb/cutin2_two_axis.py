"""Card EL.1: does a second axis earn its place on the second cut-in study?

Specified in `docs/czb_ellipse_design_note.md` section 6 (2026-09-02). The R.2 comparison
found the one-dimensional log-gap threshold the best criticality axis on the second cut-in
study (held-out wRMSE 0.152 against a noise floor of 0.118). The CZB ellipse is a
two-observable quadratic form; before building it across scenarios, this card asks the
within-scenario question on the one dataset that varies both candidate observables: is a
second axis (TTC, alongside gap) worth having at all, and if so is the trade-off curved?

THE PRE-REGISTRATION. Written before the run.

Data, fit, folds, metric: exactly the registered R.2 comparison's (`cutin2_field_vs_gap`:
288 CP2-CP5 cells from `out/cutin2_cells.csv`, weighted least squares on the cell surface,
multi-start L-BFGS-B for the threshold model b + (1-b) Phi(s (x - c) / sigma), primary
folds leave-one-starting-TTC-out, chance and sampling-noise floor as before). Nothing in
the registered script is modified; it is imported.

Models, each on identical folds:
  (a) 1D log gap                       x = -log(gap)                       [the reference]
  (b) 1D log TTC                       x = -log(TTC)                       [for the record]
  (c) linear 2D rule                   x = w * u + (1 - w) * v,  u = -log gap, v = -log TTC,
                                       w in [0, 1] fitted inside each fold   (one extra parameter)
  (d) quadratic form (the "ellipse")   x = sqrt(q' Q q),  q = (u, v) - q0,  q0 = the mildest
                                       design cell's (u, v) (largest gap, largest TTC), Q
                                       positive definite through a Cholesky factor with the
                                       (1,1) entry fixed at 1 (the scale is confounded with the
                                       threshold; the two free entries are the aspect and the
                                       orientation)                        (two extra parameters)
  (e) as (d) on the CAMP-style axes    q = (1/TTC, v_ego) - q0             (for comparison)
The inner parameters (w; the Cholesky entries) are fitted jointly with (b, c, sigma) by the
same weighted least squares, from a grid of starts, inside each training fold only.

DECISION RULE (pre-stated), all on held-out wRMSE, margin 0.01 as in R.2:
  * a second axis earns its place if (c) or (d) beats (a) by more than 0.01;
  * if (d) beats (c) by more than 0.01 the trade-off is curved and the quadratic form is
    preferred; if (c) and (d) are within 0.01, parsimony prefers the linear rule;
  * if neither beats (a) by 0.01, the cut-in boundary is one-dimensional in the gap on
    this data and the ellipse has nothing to add on this scenario -- a finding, not a failure.

Run: python replication/czb/cutin2_two_axis.py    Output: out/cutin2_two_axis.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cutin2_field_vs_gap as R  # noqa: E402

OUT = HERE / "out"
KPH = 1000.0 / 3600.0
LEAD_SPEED = 25.0   # m/s, the target's speed in every trace; the ego runs at 25.0 + DV
                    # (30.7 and 36.5 m/s measured at DV 21 and 42; diagnostic report section 3)


def fit_reg(x, y, w, sign=+1.0):
    """The registered fitter (`cutin2_field_vs_gap.fit`: same starts, same optimizer) with a
    finite-objective guard. The quadratic-form covariate has cells at exactly the corner
    q0 (x = 0), and an L-BFGS-B excursion to sigma -> 0 there gives 0/0 = NaN, which the
    registered fitter propagates as "no best start". The guard maps a non-finite objective
    to a large penalty; on the 1D covariates, where the guard never fires, it reproduces
    the registered numbers."""
    lo, hi = np.quantile(x, [0.1, 0.9])
    spread = max(np.std(x), 1e-6)
    best, best_val = None, np.inf

    def obj(th):
        v = float(np.sum(w * (R.predict(th, x, sign) - y) ** 2))
        return v if np.isfinite(v) else 1e12
    for c0 in np.linspace(lo, hi, 5):
        for ls0 in (np.log(spread), np.log(spread / 4 + 1e-9)):
            r = minimize(obj, np.array([-2.0, c0, ls0]), method="L-BFGS-B")
            if r.fun < best_val:
                best, best_val = r.x, r.fun
    return best


def finite(v):
    return v if np.isfinite(v) else 1e12


def wrmse(y, pred, w):
    return float(np.sqrt(np.average((pred - y) ** 2, weights=w)))


# ---------------------------------------------------------------------------------
# the models: each maps (cells, params) -> x, plus a fitter for the inner params
# ---------------------------------------------------------------------------------

def axes(cells):
    u = -np.log(cells.distance.to_numpy(float))
    v = -np.log(cells.ttc_true.to_numpy(float))
    return u, v


def fit_1d(x, y, w):
    th = fit_reg(x, y, w)
    return th, R.predict(th, x, +1.0)


def fit_linear(u, v, y, w):
    """w in [0,1] via a logistic map; joint least squares with (b, c, log sigma)."""
    def x_of(a):
        wt = 1.0 / (1.0 + np.exp(-a))
        return wt * u + (1.0 - wt) * v
    best, best_val = None, np.inf
    for a0 in np.linspace(-3, 3, 7):
        x0 = x_of(a0)
        th0 = fit_reg(x0, y, w)
        p0 = np.concatenate([[a0], th0])
        r = minimize(lambda p: finite(float(np.sum(w * (R.predict(p[1:], x_of(p[0]), +1.0) - y) ** 2))),
                     p0, method="L-BFGS-B", bounds=[(-8, 8), (-30, 10), (None, None), (-10, 10)])
        if r.fun < best_val:
            best, best_val = r.x, r.fun
    return best, x_of


def fit_quad(u, v, y, w, q0):
    """x = sqrt(q' Q q), Q = L L', L = [[1, 0], [l21, exp(l22)]]; joint least squares."""
    qu, qv = u - q0[0], v - q0[1]

    def x_of(p):
        l21, l22 = p[0], np.exp(p[1])
        a = qu                     # first row of L' q
        b_ = l21 * qu + l22 * qv   # second row
        return np.sqrt(a * a + b_ * b_ + 1e-12)
    best, best_val = None, np.inf
    for l21 in np.linspace(-2, 2, 5):
        for l22 in (np.log(0.3), 0.0, np.log(3.0)):
            x0 = x_of((l21, l22))
            th0 = fit_reg(x0, y, w)
            p0 = np.concatenate([[l21, l22], th0])
            r = minimize(lambda p: finite(float(np.sum(w * (R.predict(p[2:], x_of(p[:2]), +1.0) - y) ** 2))),
                         p0, method="L-BFGS-B", bounds=[(-10, 10), (-4, 4), (-30, 10), (None, None), (-10, 10)])
            if r.fun < best_val:
                best, best_val = r.x, r.fun
    return best, x_of


def held_out(cells, folds, model):
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    params = []
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        ctr, cte = cells[tr], cells[te]
        if model in ("gap", "ttc"):
            u, v = axes(ctr)
            x_tr = u if model == "gap" else v
            u2, v2 = axes(cte)
            x_te = u2 if model == "gap" else v2
            th = fit_reg(x_tr, y[tr], w[tr])
            pred[te] = R.predict(th, x_te, +1.0)
            params.append(th)
        elif model == "linear":
            u, v = axes(ctr)
            p, _ = fit_linear(u, v, y[tr], w[tr])
            wt = 1.0 / (1.0 + np.exp(-p[0]))
            u2, v2 = axes(cte)
            pred[te] = R.predict(p[1:], wt * u2 + (1 - wt) * v2, +1.0)
            params.append(np.concatenate([[wt], p[1:]]))
        elif model in ("quad", "quad_camp"):
            if model == "quad":
                u, v = axes(ctr)
                u2, v2 = axes(cte)
                q0 = (u.min(), v.min())          # mildest design cell: largest gap, largest TTC
            else:
                u = 1.0 / ctr.ttc_true.to_numpy(float)
                v = LEAD_SPEED + ctr.dv_kph.to_numpy(float) * KPH
                u2 = 1.0 / cte.ttc_true.to_numpy(float)
                v2 = LEAD_SPEED + cte.dv_kph.to_numpy(float) * KPH
                q0 = (u.min(), v.min())
            p, _ = fit_quad(u, v, y[tr], w[tr], q0)
            l21, l22 = p[0], np.exp(p[1])
            qu, qv = u2 - q0[0], v2 - q0[1]
            x_te = np.sqrt(qu * qu + (l21 * qu + l22 * qv) ** 2 + 1e-12)
            pred[te] = R.predict(p[2:], x_te, +1.0)
            params.append(np.concatenate([[l21, l22], p[2:]]))
    return pred, params


def main() -> None:
    cells_all = pd.read_csv(OUT / "cutin2_cells.csv")
    cells = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    folds = cells.ttc_start.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))
    _, chance = R.held_out(cells, folds, "gap", False)

    L = ["# Card EL.1 -- does a second axis earn its place on the second cut-in study?", "",
         "Generated by `replication/czb/cutin2_two_axis.py`; models, folds and decision rule"
         " pre-stated in its docstring. Same 288 CP2-CP5 cells, fit, folds and metric as the"
         " registered R.2 comparison. Do not edit by hand.", "",
         "| model | free parameters | held-out wRMSE | Spearman(pred, P) |",
         "|---|---|---|---|"]
    names = {"gap": "(a) 1D log gap", "ttc": "(b) 1D log TTC",
             "linear": "(c) linear 2D rule, w log gap + (1-w) log TTC",
             "quad": "(d) quadratic form in (log gap, log TTC)",
             "quad_camp": "(e) quadratic form in (1/TTC, ego speed)"}
    nfree = {"gap": 3, "ttc": 3, "linear": 4, "quad": 5, "quad_camp": 5}
    score, params = {}, {}
    for m in names:
        pred, prm = held_out(cells, folds, m)
        score[m] = wrmse(y, pred, w)
        params[m] = prm
        L.append(f"| {names[m]} | {nfree[m]} | {score[m]:.4f} | "
                 f"{float(spearmanr(pred, y).statistic):+.3f} |")
    L += [f"| chance (train mean) | - | {wrmse(y, chance, w):.4f} | - |",
          f"| sampling-noise floor | - | {noise:.4f} | - |", ""]

    d_lin = score["gap"] - score["linear"]
    d_quad = score["gap"] - score["quad"]
    d_qc = score["linear"] - score["quad"]
    if max(d_lin, d_quad) > 0.01:
        earns = "a second axis EARNS its place on this scenario"
        if d_qc > 0.01:
            form = "the trade-off is curved: the quadratic form is preferred"
        elif d_qc < -0.01:
            form = "the linear rule beats the quadratic form: the trade-off is straight"
        else:
            form = "linear and quadratic are within 0.01: parsimony prefers the linear rule"
    else:
        earns = ("neither 2D model beats the 1D log gap by 0.01: the cut-in boundary is "
                 "one-dimensional in the gap on this data, and the ellipse has nothing to add "
                 "on this scenario")
        form = "-"
    L += ["**Pre-registered decision.** gap minus linear = {:+.4f}; gap minus quadratic = "
          "{:+.4f}; linear minus quadratic = {:+.4f}. **{}**; {}.".format(
              d_lin, d_quad, d_qc, earns, form), ""]

    L += ["## Fitted inner parameters per fold (training folds)", "",
          "| held-out TTC | linear w on log gap | quad l21 | quad l22 | implied level-set slope d(log TTC)/d(log gap) at q0+(1,1) |",
          "|---|---|---|---|---|"]
    for f, pl, pq in zip(sorted(np.unique(folds)), params["linear"], params["quad"]):
        l21, l22 = pq[0], pq[1]
        # level set of x^2 = qu^2 + (l21 qu + l22 qv)^2 at qu = qv = 1: gradient ratio
        gu = 2 * 1 + 2 * (l21 + l22) * l21
        gv = 2 * (l21 + l22) * l22
        slope = -gu / gv if abs(gv) > 1e-9 else float("nan")
        L.append(f"| {f:.0f} s | {pl[0]:.3f} | {l21:+.3f} | {l22:.3f} | {slope:+.3f} |")
    L += ["", "The weight w is the share of log gap in the linear rule (w = 1 is the pure gap"
          " threshold; w = 0 pure TTC). A level-set slope near -1 in the (log gap, log TTC)"
          " plane means the two trade off one-for-one on the log scale; near 0 means gap alone.", ""]

    # within-row orderings of the fitted 2D covariates (descriptive), full-sample fit
    u, v = axes(cells)
    p_lin, x_lin = fit_linear(u, v, y, w)
    wt = 1.0 / (1.0 + np.exp(-p_lin[0]))
    x_l = wt * u + (1 - wt) * v
    q0 = (u.min(), v.min())
    p_q, x_q_of = fit_quad(u, v, y, w, q0)
    x_q = x_q_of(p_q[:2])
    L += ["## Within matched-TTC rows (full-sample fits, descriptive)", "",
          "| covariate | rows ordered like the data (of 24) | mean rho(x, P) |", "|---|---|---|"]
    for lab, x in (("log gap", u), ("linear 2D", x_l), ("quadratic", x_q)):
        rs = [float(spearmanr(x[g.index], g.p).statistic) for _, g in cells.groupby("ttc_true")
              if len(g) >= 6]
        L.append(f"| {lab} | {sum(r > 0 for r in rs)} | {np.mean(rs):+.2f} |")
    L += ["", f"Full-sample linear w = {wt:.3f}; quadratic (l21, l22) = ({p_q[0]:+.3f}, "
          f"{np.exp(p_q[1]):.3f}).", ""]

    (OUT / "cutin2_two_axis.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
