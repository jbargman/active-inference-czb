"""
Card JJ.8 -- the link and the scale: which free-energy reading of the looming threshold do the
cells prefer?

THE PRE-REGISTRATION. Written before the run, on 2026-09-22.

WHERE THE CARD COMES FROM. `docs/looming_as_free_energy.md` sections 2 to 4. Reading B (the free
energy of the present observation, a reflex on the prediction error (theta_dot - theta_dot_0)_+
with a log-normal population of levels) IS the measurement model: a probit in log theta_dot.
Reading C (a one-step expected-free-energy decision between continue and brake, with a softmax
policy posterior) is a LOGISTIC IN THE SQUARED EXCESS with an effort offset. And the spread's
scale separates multiplicative noise (a prior over levels, or Weber-like sensory noise: a spread
in log theta_dot) from additive sensory noise (the released agent's `sigma_phidot` is absolute:
a spread in theta_dot). All three are fitted here on the same axis, the same frozen gate and the
same cells, and compared held out. Nothing else in the measurement model changes.

THE MODELS, all of the form  P = lapse + (1 - lapse) * GATE * core(theta_dot), with GATE card G.1's
gate at its fitted values (JJ.6e showed what it is) and theta_dot card EL.1b's looming rate:
  B-log   core = Phi((log theta_dot - c) / sigma)                   3 parameters  [the model]
  B-lin   core = Phi((theta_dot - c) / sigma)                       3 parameters  [additive noise]
  C       core = logistic(kappa * (theta_dot - theta_0)_+^2 - e)    4 parameters  [the decision:
          kappa = gamma / (2 sigma_c^2), e = gamma * effort; at theta_dot <= theta_0 the core is
          logistic(-e), a floor the lapse also absorbs]
  C-log   core = logistic(kappa * (log theta_dot - c)_+^2 - e)      4 parameters  [the decision on
          a log-scaled preference, so that the link and the scale are not confounded]
Fitted by weighted least squares on the cell shares with multi-start L-BFGS-B (the registered
fitter's objective), held out on the registered folds, weights n. The 4-parameter models pay for
their parameter through the held-out score, which is the comparison's point.

THE RULE. Held-out differences from B-log below 0.005 are INDISTINGUISHABLE on this design (the
project's margin for "the same"); a model 0.01 or more better than B-log is PREFERRED, and a
model 0.01 or more worse is REJECTED as a reading of these data; between 0.005 and 0.01 the
report says "slightly" and draws no conclusion. Pre-onset scores are reported for completeness
and decide nothing (the gate is the same in every model).

PREDICTIONS. B-log 0.1023 (the refit of JJ.6e). B-lin worse by more than 0.01: the axis spans
0.004 to 1.1 rad/s and an additive spread cannot be narrow at the low end and wide at the high
end at once; REJECTED, which would say the spread is multiplicative (a prior over levels, or
Weber-like noise). C within 0.005 of B-log if the fitted e is large (a sharp decision with a
high floor), otherwise worse by 0.005 to 0.01: the squared argument rises too fast above the
level to reproduce the probit's shoulder. C-log within 0.005 of B-log. So my expectation is
that the data cannot tell the reflex reading from the decision reading, and can tell
multiplicative from additive: the spread is a spread of LEVELS.

Output: replication/czb/out/jj8_link_and_scale.md, out/jj8_link_and_scale_cells.csv
Run:    python replication/czb/jj8_link_and_scale.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402
import jj6_belief_gate as J6               # noqa: E402

OUT = HERE / "out"
SAME, PREFER = 0.005, 0.01


def core(model: str, th: np.ndarray, td: np.ndarray) -> np.ndarray:
    if model == "B-log":
        return norm.cdf((np.log(td) - th[1]) / np.exp(th[2]))
    if model == "B-lin":
        return norm.cdf((td - th[1]) / np.exp(th[2]))
    if model == "C":
        exc = np.maximum(td - th[1], 0.0)
        return expit(np.exp(th[2]) * exc ** 2 - np.exp(th[3]))
    if model == "C-log":
        exc = np.maximum(np.log(td) - th[1], 0.0)
        return expit(np.exp(th[2]) * exc ** 2 - np.exp(th[3]))
    raise ValueError(model)


def predict(model, th, td, g):
    b = expit(th[0])
    return b + (1.0 - b) * g * core(model, th, td)


def starts(model: str, td: np.ndarray):
    x = np.log(td) if model.endswith("log") else td
    lo, hi = np.quantile(x, [0.1, 0.9])
    spread = max(np.std(x), 1e-6)
    out = []
    for c0 in np.linspace(lo, hi, 5):
        if model.startswith("B"):
            for ls0 in (np.log(spread), np.log(spread / 4 + 1e-9)):
                out.append(np.array([-2.0, c0, ls0]))
        else:
            for lk in (np.log(1.0 / spread ** 2), np.log(10.0 / spread ** 2), np.log(0.1 / spread ** 2)):
                for le in (np.log(1.0), np.log(4.0)):
                    out.append(np.array([-2.0, c0, lk, le]))
    return out


def fit(model, td, g, y, w):
    best, best_val = None, np.inf
    for th0 in starts(model, td):
        r = minimize(lambda th: float(np.sum(w * (predict(model, th, td, g) - y) ** 2)), th0,
                     method="L-BFGS-B")
        if np.isfinite(r.fun) and r.fun < best_val:
            best, best_val = r.x, r.fun
    return best


def score(model, d):
    post_m = (d.cp != "CP1").to_numpy()
    td, g = d.theta_dot.to_numpy(float), d.gate_g1.to_numpy(float)
    y, w, f = d.p.to_numpy(float), d.n.to_numpy(float), d.ttc_start.to_numpy(float)
    tp, gp, yp, wp, fp = td[post_m], g[post_m], y[post_m], w[post_m], f[post_m]
    pred = np.full_like(yp, np.nan)
    for k in np.unique(fp):
        th = fit(model, tp[fp != k], gp[fp != k], yp[fp != k], wp[fp != k])
        pred[fp == k] = predict(model, th, tp[fp == k], gp[fp == k])
    th = fit(model, tp, gp, yp, wp)
    pred1 = predict(model, th, td[~post_m], g[~post_m])
    return {"post": R.wrmse(yp, pred, wp), "cp1": R.wrmse(y[~post_m], pred1, w[~post_m]),
            "theta": th, "pred_post": pred}


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    d = cells[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph"]].copy()
    d["theta_dot"] = np.exp(J6.looming_axis(cells))
    lat = J6.CG.lateral_states(cells.video)
    d["gate_g1"] = np.asarray(J6.CG.gate(J6.G1_M_LAT, np.log(J6.G1_S_L), lat.l0.to_numpy(float),
                                         lat.ldot.to_numpy(float)), float)
    models = ("B-log", "B-lin", "C", "C-log")
    res = {}
    for m in models:
        res[m] = score(m, d)
        print(f"{m}: {res[m]['post']:.4f} / {res[m]['cp1']:.4f}", flush=True)
    post = d[d.cp != "CP1"].copy()
    for m in models:
        post[f"pred_{m}"] = res[m]["pred_post"]
    post.to_csv(OUT / "jj8_link_and_scale_cells.csv", index=False)

    def label(m):
        diff = res[m]["post"] - res["B-log"]["post"]
        if m == "B-log":
            return "the reference"
        if abs(diff) < SAME:
            return "INDISTINGUISHABLE"
        if diff <= -PREFER:
            return "**PREFERRED**"
        if diff >= PREFER:
            return "REJECTED"
        return "slightly " + ("better" if diff < 0 else "worse")

    def params(m):
        th = res[m]["theta"]
        b = expit(th[0])
        if m == "B-log":
            return f"lapse {b:.3f}, level {np.exp(th[1]):.4f} rad/s, spread {np.exp(th[2]):.3f} log units"
        if m == "B-lin":
            return f"lapse {b:.3f}, level {th[1]:.4f} rad/s, spread {np.exp(th[2]):.4f} rad/s"
        if m == "C":
            return (f"lapse {b:.3f}, theta_0 {th[1]:.4f} rad/s, kappa {np.exp(th[2]):.3g} s^2/rad^2,"
                    f" e {np.exp(th[3]):.2f} (floor logistic(-e) = {expit(-np.exp(th[3])):.3f})")
        return (f"lapse {b:.3f}, level {np.exp(th[1]):.4f} rad/s, kappa {np.exp(th[2]):.3g},"
                f" e {np.exp(th[3]):.2f} (floor {expit(-np.exp(th[3])):.3f})")

    L = ["# Card JJ.8 -- the link and the scale of the looming threshold", "",
         "Generated by `replication/czb/jj8_link_and_scale.py`; the models, the rule and the"
         " predictions were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "Four response models on card EL.1b's looming axis with card G.1's gate frozen (what"
         " that gate is: card JJ.6e). B-log is the measurement model, the reflex reading of"
         " `docs/looming_as_free_energy.md`; B-lin the same with additive noise; C the one-step"
         " expected-free-energy decision with a softmax policy posterior; C-log that decision on"
         " a log-scaled preference.", "",
         "| model | parameters | post-onset held out | pre-onset | difference from B-log |"
         " reading | full-sample fit |", "|---|---|---|---|---|---|---|"]
    for m in models:
        L.append(f"| **{m}** | {3 if m.startswith('B') else 4} | {res[m]['post']:.4f} |"
                 f" {res[m]['cp1']:.4f} | {res[m]['post'] - res['B-log']['post']:+.4f} |"
                 f" {label(m)} | {params(m)} |")
    L += ["", f"Rule: below {SAME} indistinguishable; {PREFER} or more better preferred, {PREFER} or"
          " more worse rejected.", "", "## The reading", "",
          f"* Multiplicative against additive: B-lin is {label('B-lin').strip('*')}"
          f" ({res['B-lin']['post'] - res['B-log']['post']:+.4f}).",
          f"* Reflex against decision: C is {label('C').strip('*')}"
          f" ({res['C']['post'] - res['B-log']['post']:+.4f}); C-log is {label('C-log').strip('*')}"
          f" ({res['C-log']['post'] - res['B-log']['post']:+.4f}).", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj8_link_and_scale.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
