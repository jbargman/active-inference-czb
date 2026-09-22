"""
Card JJ.6e -- the gate as predictive uncertainty about the other's lateral motion, with no
intention variable: is card G.1's gate the fan's P(in my path within T) under a single Gaussian
rate hypothesis?

THE PRE-REGISTRATION. Written before the run, on 2026-09-22, after JJ.6 to JJ.6d.

WHY. JJ.6d showed the intention-filter gate is binary or slow at every keeping spread; its
post-onset grading never matches G.1's. In the deciding cells (CP2 of the 4 s lane changes) the
intention is certain and G.1's gate is still 0.76: the vehicle is far out and slow. G.1's gate
grades on HOW SOON the other's body reaches the ego's, not on whether it intends to. Written out,
G.1's gate is Phi((m_lat - (l0 + ldot T)) / s_l) with T = 3 s, and a predictor that projects the
CURRENT lateral rate with Gaussian uncertainty sigma over T gives

    P(l0 + (ldot + e) T < m_lat),  e ~ N(0, sigma^2)   =   Phi((m_lat - l0 - ldot T) / (sigma T)),

so **G.1's gate is that predictor's P(in path within T) with s_l = sigma T**, exactly; and
pre-onset, with ldot at the floor and l0 about 1.6 m, it is Phi(-1.6 / (3 sigma)), which at
sigma = 0.33 m/s is 0.053 -- G.1's 0.063 to 0.070 with no intention prior at all. The intention
mixture of card JJ.1's fan, with changers moving deterministically at 1.2 m/s, is what made the
belief gate binary.

DECLARED CIRCULARITY. SD_VLAT = 0.33 m/s in the predictor was itself set from G.1's fitted s_l
(0.99 m over 3 s, as a rate: design note section 1.2). So this card does not derive G.1's gate
from independent constants; it shows that G.1's two fitted parameters ARE the parameters of a
Gaussian predictive model of the other's lateral motion (its rate uncertainty and the ego's body
margin), read at the 3 s horizon, and that the fan machinery reproduces the gate when the
intention mixture is removed. The value of that is the meaning, and the test is the identity.

WHAT IS COMPUTED. (1) The analytic gate Phi((m - l0 - ldot T)/(sigma T)) with m = G.1's m_lat
0.149 m, sigma = SD_VLAT, T = 3 s, on G.1's own lateral states (l0, ldot): must equal G.1's gate
column to 1e-9 (an identity, checked). (2) The same with m = 0 (no fitted margin): the gate with
NOTHING taken from G.1 but sigma. (3) Through the fan: `sample_futures` with p_change = 0 (a
single hypothesis), the clip at the lane edge removed by setting `keep_body_in_lane=True` AND the
"never further in than now" bound left as is (it binds only on straddling vehicles, which are in
the path anyway), and `share_in_path`-style Monte Carlo P(|dy| <= 1.15 w within T) with the fan's
own dy; n = 200, seed 0. Since the fan's keeper rate is the observed rate plus N(0, SD_VLAT),
this is (1) up to the body-width convention and Monte Carlo error. All three scored on the
looming axis with the fixed-gate fitter, as JJ.6.

THE RULES. JJ.6's: (a) within 0.01 of 0.1027 and (b) pre-onset below 0.05, for reading (2) --
the one with no fitted margin -- at T = 3 s. Verdict DERIVED (with the circularity above stated
in the same sentence) / NOT DERIVED. Rule 0: reading (1) reproduces G.1's column to 1e-9 and its
scores 0.1023 / 0.0318 to 0.0005.

PREDICTIONS. (1) identity, exact. (2) m = 0 shifts every gate value down slightly (0.149 m less
clearance to cover); post-onset 0.103 to 0.106, pre-onset 0.03 to 0.05: DERIVED, probably. (3)
within Monte Carlo error of (2) at 200 futures (about 0.03 in the gate); scores within 0.003.
If (2) fails (b), the 0.149 m margin is doing real work pre-onset and the reading needs the ego's
body width as a constant, which it may take from the vehicle dimensions rather than from a fit.

Output: replication/czb/out/jj6e_predictive_gate.md, out/jj6e_predictive_gate_cells.csv
Run:    python replication/czb/jj6e_predictive_gate.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import jj6_belief_gate as J6               # noqa: E402
from aidriver.preferences import PreferenceParams  # noqa: E402
from rollout.looming_pref import p_in_lane  # noqa: E402
from rollout.efe import observations  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
T = J6.T_PRIMARY


def p_in_path_mc(belief, ego, fut, horizon_s: float) -> float:
    """Monte Carlo P(the other's body overlaps the ego's body laterally, ahead, within T)."""
    obs = observations(belief, ego, fut)
    dx, dy = np.asarray(obs["dx"], float), np.asarray(obs["dy"], float)
    within = fut.tau[None, :] <= horizon_s + 1e-9
    half = 0.5 * (belief.ego_wid + belief.oth_wid)
    hit = within & (dx > 0) & (np.abs(dy) <= half + J6.G1_M_LAT)
    return float(hit.any(axis=1).mean())


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    x = J6.looming_axis(cells)
    lat = J6.CG.lateral_states(cells.video)
    l0, ldot = lat.l0.to_numpy(float), lat.ldot.to_numpy(float)
    g1 = np.asarray(J6.CG.gate(J6.G1_M_LAT, np.log(J6.G1_S_L), l0, ldot), float)
    g_ident = norm.cdf((J6.G1_M_LAT - l0 - ldot * T) / (SD_VLAT * T))
    g_zero = norm.cdf((0.0 - l0 - ldot * T) / (SD_VLAT * T))
    ident_ok = bool(np.max(np.abs(g_ident - g1)) < 1e-9)
    print(f"identity max |diff| {np.max(np.abs(g_ident - g1)):.2e}; s_l {J6.G1_S_L} vs sigma T"
          f" {SD_VLAT * T}", flush=True)

    bel = J6.J5.beliefs(cells)
    g_mc = []
    for v, (b, cp) in bel.items():
        b.p_change = 0.0
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=0, keep_body_in_lane=True)
        g_mc.append(p_in_path_mc(b, ego_rollout(b, "continue", HORIZON_S, DT_S), fut, T))
    g_mc = np.asarray(g_mc)

    d = cells[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "lcd"]].copy()
    d["l0"], d["ldot"] = l0, ldot
    d["gate_g1"], d["gate_ident"], d["gate_m0"], d["gate_fan"] = g1, g_ident, g_zero, g_mc
    d["x_looming"] = x
    d.to_csv(OUT / "jj6e_predictive_gate_cells.csv", index=False)
    is_cp1 = (d.cp == "CP1").to_numpy()

    res = {k: J6.score_gated(d, x, d[c].to_numpy(float))
           for k, c in (("G.1", "gate_g1"), ("identity", "gate_ident"), ("m = 0", "gate_m0"),
                        ("fan", "gate_fan"))}
    rule0 = ident_ok and abs(res["identity"]["post"] - 0.1023) <= 0.0005 \
        and abs(res["identity"]["cp1"] - 0.0318) <= 0.0005
    a = res["m = 0"]["post"] <= J6.G1_GATED + J6.MARGIN_A
    b_ = res["m = 0"]["cp1"] < J6.CP1_CRIT
    verdict = "DERIVED" if a and b_ else "NOT DERIVED"
    s_l_from_sigma = SD_VLAT * T
    L = ["# Card JJ.6e -- the gate as predictive uncertainty about the other's lateral motion", "",
         "Generated by `replication/czb/jj6e_predictive_gate.py`; the identity, the readings, the"
         " rules, the predictions and the circularity were pre-stated in its docstring before the"
         " run. Do not edit by hand.", "",
         "## 0 The identity", "",
         f"G.1's gate Phi((m_lat - (l0 + ldot 3 s)) / s_l) with s_l = {J6.G1_S_L} m, against the"
         f" Gaussian-rate predictor's Phi((m_lat - l0 - ldot T) / (sigma T)) with sigma = SD_VLAT ="
         f" {SD_VLAT} m/s and T = 3 s, so sigma T = {s_l_from_sigma:.2f} m: max |difference| over"
         f" the 378 cells {np.max(np.abs(g_ident - g1)):.1e}; scores {res['identity']['post']:.4f} /"
         f" {res['identity']['cp1']:.4f} against 0.1023 / 0.0318. **Rule 0 {'PASSES' if rule0 else 'FAILS'}.**",
         "",
         "**Declared circularity:** SD_VLAT was set from G.1's s_l (design note section 1.2), so"
         " the identity says what G.1's parameters ARE, not that they were derived from"
         " elsewhere: s_l is the predictor's lateral-rate uncertainty times the anticipation"
         " horizon, and m_lat is a body margin.", "",
         "## 1 The readings", "",
         "| gate | pre-onset mean | post-onset mean | rho with G.1's gate (post-onset) | post-onset"
         " held out | pre-onset, out of sample | median level [rad/s] |", "|---|---|---|---|---|---|---|"]
    for k, c in (("G.1", "gate_g1"), ("identity", "gate_ident"), ("m = 0", "gate_m0"), ("fan", "gate_fan")):
        v = d[c].to_numpy(float)
        rho = spearmanr(v[~is_cp1], g1[~is_cp1]).statistic if np.std(v[~is_cp1]) > 0 else float("nan")
        lab = {"G.1": "card G.1's fitted gate", "identity": "(1) the predictor, m = G.1's 0.149 m",
               "m = 0": "**(2) the predictor, m = 0: nothing from G.1 but sigma**",
               "fan": "(3) through the fan, p_change = 0, Monte Carlo"}[k]
        L.append(f"| {lab} | {v[is_cp1].mean():.3f} | {v[~is_cp1].mean():.3f} | {rho:+.3f} |"
                 f" {res[k]['post']:.4f} | {res[k]['cp1']:.4f} | {res[k]['level']:.4f} |")
    L += ["", "## 2 The verdict on the pre-stated rules, reading (2)", "",
          f"**{verdict}.** Rule (a) {res['m = 0']['post']:.4f} ({'holds' if a else 'fails'}), rule"
          f" (b) {res['m = 0']['cp1']:.4f} ({'holds' if b_ else 'fails'}).", "",
          ("The gate of the measurement model is the predictive uncertainty of a Gaussian model"
           " of the other's lateral motion, read against the ego's body at a 3 s horizon: its"
           " spread is the rate uncertainty times the horizon and its opening pre-onset is the"
           " tail of that uncertainty, with no intention variable. The circularity stated above"
           " stands: sigma came from G.1. What is new is that the two fitted gate parameters"
           " have this meaning, and that card JJ.1's intention mixture, with changers at a fixed"
           " 1.2 m/s, is what kept the belief gate from grading (JJ.6 to JJ.6d)."
           if verdict == "DERIVED" else
           "The predictor without G.1's margin does not pass; the table says which rule."), "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj6e_predictive_gate.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
