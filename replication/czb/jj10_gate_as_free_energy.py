"""
Card JJ.10 -- the continuous gate as a free-energy component: does the gate act on the
probability of responding (a mixture) or on the quantity judged (an expected free energy)?

THE PRE-REGISTRATION. Written before the run, on 2026-09-22.

WHERE THE CARD COMES FROM. Jonas: *"Is there any way to frame the continuous gate in terms of a
free energy component? Intuitively it seems logical, but I do not know how."* The framing
(`src/rollout/comfort_fe.py`, 9 property checks): a driver's prior over looming applies to a
LEAD; whether the object is a lead is predicted, not observed; the free energy of the present
observation is the expectation of the looming prediction error over the predictive distribution
of the other's lateral motion, F = P(lead) * excess(theta_dot), with P(lead) card JJ.6e's gate.
The gate is the predictive probability that the looming prior applies. Two response models
follow and they differ:
  **mixture**   P(respond) = lapse + (1 - lapse) P(lead) Phi((log theta_dot - m) / s). The driver
                resolves "is it a lead" and then judges. This IS the gated looming rule of cards
                G.1 / EL.1b (identity, property test): the gate multiplies the PROBABILITY.
  **expected**  P(respond) = lapse + (1 - lapse) Phi((log(P(lead) theta_dot) - m) / s). The driver
                judges the expected looming of a lead: the gate multiplies the QUANTITY.
Both fit (lapse, m, s) and nothing else; P(lead) has sigma_lat = 0.33 m/s, T = 3 s, m = 0 (JJ.6e's
reading (2), no fitted margin), so the comparison is between forms, not parameter counts.

CELLS, FOLDS, METRIC: the registered R.2 script's, as every card. Axis: card EL.1b's looming rate
(`jj6_belief_gate.looming_axis`); lateral states from `cutin2_gate.lateral_states`.

THE RULE. Held-out difference below 0.005: the forms are INDISTINGUISHABLE on this design; 0.01
or more: the better form is PREFERRED and the other REJECTED as the reading of the gate; between:
"slightly", no conclusion. Pre-onset (rule (b), below 0.05) is reported for both and decides
nothing by itself, but a form that fails it while the other passes is noted as such.

PREDICTIONS. Mixture: 0.1028 / 0.0462 (JJ.6e reading (2), reproduced). Expected: pre-onset
better than the mixture (the gate at 0.05 shifts the argument by log 0.05 = -3.0, three spreads,
so the pre-onset cells sit far below the level and are predicted at the lapse; the mixture
multiplies a core that is already small), post-onset slightly worse (0.105 to 0.110): where the
gate is partly open the expected form lowers the argument rather than the probability, and the
probit's slope then makes the response fall more steeply than the participants' does. I expect
"indistinguishable" or "slightly worse" for the expected form, and if so the honest statement is
that the gate's mode of action cannot be told on this design and the mixture stays as the
measurement model, with the expected-free-energy form as its free-energy reading. If the
expected form is PREFERRED, the comfort-zone boundary is a threshold on the expected looming of
a lead, one quantity, which is the simpler active-inference statement.

Output: replication/czb/out/jj10_gate_as_free_energy.md, out/jj10_gate_as_free_energy_cells.csv
Run:    python replication/czb/jj10_gate_as_free_energy.py
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
from rollout.comfort_fe import SIGMA_LAT, T_ANTICIPATION, expected_looming, p_lead  # noqa: E402

OUT = HERE / "out"
SAME, PREFER = 0.005, 0.01


def predict(form, th, td, g):
    b = expit(th[0])
    if form == "mixture":
        return b + (1 - b) * g * norm.cdf((np.log(td) - th[1]) / np.exp(th[2]))
    x = np.log(np.maximum(g * td, 1e-300))
    return b + (1 - b) * norm.cdf((x - th[1]) / np.exp(th[2]))


def fit(form, td, g, y, w):
    x = np.log(td) if form == "mixture" else np.log(np.maximum(g * td, 1e-300))
    lo, hi = np.quantile(x, [0.1, 0.9])
    spread = max(np.std(x), 1e-6)
    best, val = None, np.inf
    for c0 in np.linspace(lo, hi, 5):
        for ls0 in (np.log(spread), np.log(spread / 4 + 1e-9)):
            r = minimize(lambda th: float(np.sum(w * (predict(form, th, td, g) - y) ** 2)),
                         np.array([-2.0, c0, ls0]), method="L-BFGS-B")
            if np.isfinite(r.fun) and r.fun < val:
                best, val = r.x, r.fun
    return best


def score(form, d):
    post_m = (d.cp != "CP1").to_numpy()
    td, g = d.theta_dot.to_numpy(float), d.p_lead.to_numpy(float)
    y, w, f = d.p.to_numpy(float), d.n.to_numpy(float), d.ttc_start.to_numpy(float)
    tp, gp, yp, wp, fp = td[post_m], g[post_m], y[post_m], w[post_m], f[post_m]
    pred = np.full_like(yp, np.nan)
    for k in np.unique(fp):
        th = fit(form, tp[fp != k], gp[fp != k], yp[fp != k], wp[fp != k])
        pred[fp == k] = predict(form, th, tp[fp == k], gp[fp == k])
    th = fit(form, tp, gp, yp, wp)
    pred1 = predict(form, th, td[~post_m], g[~post_m])
    return {"post": R.wrmse(yp, pred, wp), "cp1": R.wrmse(y[~post_m], pred1, w[~post_m]),
            "theta": th, "pred": pred, "pred1": pred1}


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    d = cells[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph"]].copy()
    d["theta_dot"] = np.exp(J6.looming_axis(cells))
    lat = J6.CG.lateral_states(cells.video)
    d["l0"], d["ldot"] = lat.l0.to_numpy(float), lat.ldot.to_numpy(float)
    d["p_lead"] = p_lead(d.l0, d.ldot, SIGMA_LAT, T_ANTICIPATION)
    d["expected_looming"] = expected_looming(d.theta_dot, d.l0, d.ldot)
    res = {f: score(f, d) for f in ("mixture", "expected")}
    post_m = (d.cp != "CP1").to_numpy()
    for f in res:
        d.loc[post_m, f"pred_{f}"] = res[f]["pred"]
        d.loc[~post_m, f"pred_{f}"] = res[f]["pred1"]
    d.to_csv(OUT / "jj10_gate_as_free_energy_cells.csv", index=False)
    diff = res["expected"]["post"] - res["mixture"]["post"]
    if abs(diff) < SAME:
        verdict = "INDISTINGUISHABLE"
    elif diff <= -PREFER:
        verdict = "the EXPECTED form is PREFERRED"
    elif diff >= PREFER:
        verdict = "the MIXTURE is PREFERRED; the expected form is REJECTED"
    else:
        verdict = "slightly " + ("better" if diff < 0 else "worse") + " for the expected form; no conclusion"

    def params(f):
        th = res[f]["theta"]
        return f"lapse {expit(th[0]):.3f}, level {np.exp(th[1]):.4f} rad/s, spread {np.exp(th[2]):.3f}"

    L = ["# Card JJ.10 -- the continuous gate as a free-energy component", "",
         "Generated by `replication/czb/jj10_gate_as_free_energy.py`; the framing, the two forms,"
         " the rule and the predictions were pre-stated in its docstring before the run. Do not"
         " edit by hand.", "",
         "The free energy of the present observation under a prior over the looming of a LEAD,"
         " with the lead's status predicted by the generative model, is F = P(lead) x excess."
         " The gate is the predictive probability that the prior applies. Two response models"
         " follow: the gate on the probability (the mixture, which is the gated looming rule) and"
         " the gate on the quantity (a threshold on the expected looming of a lead).", "",
         "| form | post-onset held out | pre-onset | full-sample fit |", "|---|---|---|---|"]
    for f, lab in (("mixture", "**mixture**: P(lead) x Phi(log looming)"),
                   ("expected", "**expected**: Phi(log(P(lead) x looming))")):
        L.append(f"| {lab} | {res[f]['post']:.4f} | {res[f]['cp1']:.4f} | {params(f)} |")
    L += ["", f"Difference (expected - mixture) {diff:+.4f}; rule: below {SAME} indistinguishable,"
          f" {PREFER} or more decides. **{verdict}.**", "",
          "## Reading", "",
          ("The gate's mode of action cannot be told on this design: the mixture stays as the"
           " measurement model, and the expected-free-energy form is its reading in active-"
           "inference terms, one quantity F = P(lead) x excess that the driver acts to reduce."
           if verdict == "INDISTINGUISHABLE" else
           "The comfort-zone boundary is a threshold on the expected looming of a lead, one"
           " quantity; the gate multiplies what is judged, not the probability of judging."
           if "EXPECTED" in verdict else
           "The gate multiplies the probability of responding, not the quantity judged: the driver"
           " resolves whether the object is a lead and then judges its looming. The expected-"
           "free-energy form is not how these participants combine the two."
           if "MIXTURE" in verdict else "No conclusion at this margin."), "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj10_gate_as_free_energy.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
