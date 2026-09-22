"""
Card JJ.6 -- the intention belief as the gate: does card JJ.1's fan reproduce card G.1's fitted
gate, so that the gated looming rule can be written with the gate DERIVED and nothing fitted but
the response model?

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22.

WHERE THE CARD COMES FROM
-------------------------
Jonas, 2026-09-22: *"Continue pursuing the possibility of using active inference for CZBs. It may
be that a looming threshold fits the data better, but if we can explain it in terms of fundamental
free energy it is more anchored in fundamental science, but we should not just assume it works --
we have to probe the different ways to think about it."*

Card G.1's gated looming rule (0.1027 held out, 0.0319 pre-onset) has two fitted gate parameters,
m_lat = 0.149 m and s_l = 0.990 m, in Phi((m_lat - (l0 + ldot * 3 s)) / s_l): the probability that
the other's lateral clearance, projected 3 s ahead, falls below a minimum. Card JJ.1's fan gives a
belief over the other's futures with a latent lane-change intention (posterior 0.07 pre-onset, 1.0
post-onset, `rollout.belief.update_intention`). Read as "the probability that the other's body is
in my lane within T seconds", `rollout.looming_pref.p_in_lane` (card JJ.6, 5 property checks), the
fan IS a gate with nothing fitted. This card puts the two side by side. If they agree, the gate
half of the measurement model has been derived from the active-inference construction: the gate
is the belief over the other's intention, propagated through the predictive model.

WHAT IS COMPUTED
----------------
Per cell, on the corrected fan (`keep_body_in_lane=True`; JJ.1's fan is reported beside it), seed
0, n = 200: p_in_lane(T) for T in {1, 2, 3, 4, 6} s. The axis is card EL.1b's looming rate exactly
as `cutin2_looming.py` computes it -- theta_dot = W dv / (gap^2 + W^2/4) with W from each cell's
own trace (`widths_for`), gap = `distance`, dv from `dv_kph` -- and its log. The response model is
card G.1's `predict_gated` with the gate COLUMN replaced by the fan's value and only (lapse, level,
spread) fitted (`s15_comfort_threshold.fit_gated`, which is the registered fitter's starts and
objective with a fixed multiplier on the core). Cells, folds and metric are the registered R.2
script's, via card JJ.2's `held_out_scores`-style loop. Comparators, on file: card G.1's gated rule
0.1027 / pre-onset 0.0319 (`out/cutin2_gate.md`); the ungated looming rate 0.1130 / 0.4832
(`out/cutin2_looming.md` (h); `out/cutin2_gate.md` section 2); G.1's gate values themselves,
recomputed from `cutin2_gate.lateral_states` and `gate(0.149, log 0.990, l0, ldot)`.

THE RULES
---------
  (a) post-onset held out within 0.01 of the gated looming rule's 0.1027, at the primary T = 3 s
      (card G.1's own horizon; not chosen by score);
  (b) the full post-onset fit applied to the 90 pre-onset cells scores below 0.05, with nothing
      fitted on those cells;
  (c) the per-cell rank correlation between p_in_lane(3 s) and G.1's gate, reported; no criterion.
  VERDICT: **DERIVED** if (a) and (b) at T = 3 s. **DERIVED AT ANOTHER HORIZON** if (a) and (b)
  hold at some other T and not at 3 s (all T reported; none chosen by score; the report says
  which). **NOT DERIVED** otherwise, with the failing rule named.
  Rule 0: the ungated looming axis as computed here reproduces `cutin2_looming.md` (h)'s 0.1130
  within 0.0005; otherwise the axis is not EL.1b's and the card stops.

PREDICTIONS
-----------
  (a) holds at every T >= 2 s: post-onset the posterior is 1.0 and the fan's changers are in the
      lane within about 1.5 s, so the gate is 1 and the score is the ungated looming rate's 0.1130,
      inside the margin (0.1127 needed -- so it may miss by 0.0003 and the report must say so
      honestly if it does; the ungated rule itself sits 0.0103 above the gated one).
  (b) holds at T = 3 s. Pre-onset the posterior is 0.07 and the changers reach the lane within
      3 s, so p_in_lane(3 s) is about 0.07 in every pre-onset cell -- a constant -- and G.1's own
      gate at those cells is 0.063 to 0.070 (`out/cutin2_gate.md` section 3), also nearly
      constant. So (b) should hold and (c) should be LOW pre-onset (two near-constants), which is
      the honest reading: the belief gate matches G.1's gate in level, not in its grading.
  At T = 1 s, (a) fails: the changers have not all reached the lane, so the gate is graded
      post-onset where the data want it open.
  The gate half is therefore derivable, with one caveat the docstring states in advance: the
  intention posterior is binary on these cells, so the derivation shows the gate's LEVEL comes
  from the prior and its OPENING from the lateral-rate likelihood, and does not test a graded
  belief. That test needs intermediate lateral evidence (query S16.Q2).

Output: replication/czb/out/jj6_belief_gate.md, out/jj6_belief_gate_cells.csv
Run:    python replication/czb/jj6_belief_gate.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402
import cutin2_gate as CG                   # noqa: E402  card G.1 (read only)
import cutin2_looming as CL                # noqa: E402  card EL.1b (read only)
import cutin2_two_axis as T                # noqa: E402
import jj5_looming_preference as J5        # noqa: E402  (its `beliefs`)
import s15_comfort_threshold as S15        # noqa: E402  (its fixed-gate fitter)
from rollout.looming_pref import p_in_lane  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
G1_GATED, G1_CP1, UNGATED_H, UNGATED_CP1 = 0.1027, 0.0319, 0.1130, 0.4832
MARGIN_A, CP1_CRIT, REPRO_TOL = 0.01, 0.05, 0.0005
HORIZONS = (1.0, 2.0, 3.0, 4.0, 6.0)
T_PRIMARY = 3.0
G1_M_LAT, G1_S_L = 0.149, 0.990


def looming_axis(cells: pd.DataFrame) -> np.ndarray:
    W, _ = CL.widths_for(cells)
    gap = cells.distance.to_numpy(float)
    dv = cells.dv_kph.to_numpy(float) * 1000.0 / 3600.0
    return np.log(W * dv / (gap ** 2 + W ** 2 / 4.0))


def score_gated(d: pd.DataFrame, x: np.ndarray, g: np.ndarray) -> dict:
    post_m = (d.cp != "CP1").to_numpy()
    y, w, f = d.p.to_numpy(float), d.n.to_numpy(float), d.ttc_start.to_numpy(float)
    xp, gp, yp, wp, fp = x[post_m], g[post_m], y[post_m], w[post_m], f[post_m]
    pred = np.full_like(yp, np.nan)
    for k in np.unique(fp):
        th = S15.fit_gated(xp[fp != k], gp[fp != k], yp[fp != k], wp[fp != k])
        pred[fp == k] = S15.predict_gated(th, xp[fp == k], gp[fp == k])
    th = S15.fit_gated(xp, gp, yp, wp)
    pred1 = S15.predict_gated(th, x[~post_m], g[~post_m])
    return {"post": R.wrmse(yp, pred, wp), "cp1": R.wrmse(y[~post_m], pred1, w[~post_m]),
            "level": float(np.exp(th[1])), "pred1_mean": float(np.average(pred1, weights=w[~post_m]))}


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    x = looming_axis(cells)
    post = cells[cells.cp != "CP1"].reset_index(drop=True)
    pred_u = CL.held_out_1d(x[(cells.cp != "CP1").to_numpy()], post.p.to_numpy(float),
                            post.n.to_numpy(float), post.ttc_start.to_numpy(float))
    ungated = T.wrmse(post.p.to_numpy(float), pred_u, post.n.to_numpy(float))
    rule0 = abs(ungated - UNGATED_H) <= REPRO_TOL
    print(f"rule 0: {ungated:.4f} -> {rule0}", flush=True)

    lat = CG.lateral_states(cells.video)
    g1 = np.asarray(CG.gate(G1_M_LAT, np.log(G1_S_L), lat.l0.to_numpy(float),
                            lat.ldot.to_numpy(float)), float)
    bel = J5.beliefs(cells)
    rows = []
    for v, (b, cp) in bel.items():
        ego = ego_rollout(b, "continue", HORIZON_S, DT_S)
        row = {"video": v, "cp": cp, "p_change": b.p_change}
        for corrected, tag in ((True, "c"), (False, "j")):
            fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                                 sd_a=SD_A, seed=0, keep_body_in_lane=corrected)
            for h in HORIZONS:
                row[f"g{tag}_{h:g}"] = p_in_lane(b, ego, fut, h)
        rows.append(row)
    d = pd.DataFrame(rows).merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance",
                                        "dv_kph"]], on="video")
    d["x_looming"] = x
    d["gate_g1"] = g1
    d.to_csv(OUT / "jj6_belief_gate_cells.csv", index=False)
    is_cp1 = (d.cp == "CP1").to_numpy()

    res = {(tag, h): score_gated(d, x, d[f"g{tag}_{h:g}"].to_numpy(float))
           for tag in ("c", "j") for h in HORIZONS}
    res_g1 = score_gated(d, x, g1)
    print("scores done", flush=True)

    def ok(s):
        return s["post"] <= G1_GATED + MARGIN_A, s["cp1"] < CP1_CRIT

    a3, b3 = ok(res[("c", T_PRIMARY)])
    other = [h for h in HORIZONS if h != T_PRIMARY and all(ok(res[("c", h)]))]
    if a3 and b3:
        verdict = "DERIVED"
    elif other:
        verdict = "DERIVED AT ANOTHER HORIZON (" + ", ".join(f"{h:g} s" for h in other) + ")"
    else:
        verdict = "NOT DERIVED"

    L = ["# Card JJ.6 -- the intention belief as the gate", "",
         "Generated by `replication/czb/jj6_belief_gate.py`; the construction, the rules and the"
         " predictions were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "Card G.1's gate is a fitted function of the other's lateral clearance and rate. Card"
         " JJ.1's fan, read as \"the probability that the other's body is in my lane within T"
         " seconds\" (`rollout.looming_pref.p_in_lane`), is a gate with nothing fitted. This card"
         " puts the two side by side on card EL.1b's looming axis, fitting only the response"
         " model's three parameters.", "",
         "## 0 Rule 0 and the gate values", "",
         f"The ungated looming axis reproduces `cutin2_looming.md` (h): {ungated:.4f} against"
         f" {UNGATED_H} -> **{'PASS' if rule0 else 'FAIL'}**.", "",
         "| gate | pre-onset mean (min-max) | post-onset mean (min-max) | rank correlation with"
         " G.1's gate, pre-onset / post-onset / all |", "|---|---|---|---|"]
    for lab, col in [("card G.1's fitted gate", "gate_g1")] + [
            (f"the belief, corrected fan, T = {h:g} s", f"gc_{h:g}") for h in HORIZONS]:
        v = d[col].to_numpy(float)
        rho = lambda m: (f"{spearmanr(v[m], g1[m]).statistic:+.3f}"  # noqa: E731
                         if np.std(v[m]) > 0 and np.std(g1[m]) > 0 else "const")
        L.append(f"| {lab} | {v[is_cp1].mean():.3f} ({v[is_cp1].min():.3f}-{v[is_cp1].max():.3f})"
                 f" | {v[~is_cp1].mean():.3f} ({v[~is_cp1].min():.3f}-{v[~is_cp1].max():.3f}) |"
                 f" {rho(is_cp1)} / {rho(~is_cp1)} / {rho(np.ones(len(v), bool))} |")
    L += ["", "## 1 The scores", "",
          "| gate on the looming axis | post-onset held out | pre-onset, out of sample | median"
          " level [rad/s] | pre-onset predicted mean (observed 0.023) |", "|---|---|---|---|---|"]
    L.append(f"| card G.1's fitted gate, refitted here with (lapse, level, spread) only |"
             f" {res_g1['post']:.4f} | {res_g1['cp1']:.4f} | {res_g1['level']:.4f} |"
             f" {res_g1['pred1_mean']:.3f} |")
    L.append(f"| no gate (card EL.1b) | {ungated:.4f} | {UNGATED_CP1} (on file) | - | - |")
    for tag, lab in (("c", "the belief, corrected fan"), ("j", "the belief, JJ.1's fan as built")):
        for h in HORIZONS:
            s = res[(tag, h)]
            mark = " **(primary)**" if (tag == "c" and h == T_PRIMARY) else ""
            L.append(f"| {lab}, T = {h:g} s{mark} | {s['post']:.4f} | {s['cp1']:.4f} |"
                     f" {s['level']:.4f} | {s['pred1_mean']:.3f} |")
    L += ["", f"Comparators on file: card G.1's gated rule {G1_GATED} / {G1_CP1}; rule (a) needs"
          f" {G1_GATED + MARGIN_A:.4f} or below, rule (b) below {CP1_CRIT}.", "",
          "## 2 The verdict on the pre-stated rules", "",
          f"**{verdict}.** At T = {T_PRIMARY:g} s: rule (a) {res[('c', T_PRIMARY)]['post']:.4f}"
          f" ({'holds' if a3 else 'fails'}), rule (b) {res[('c', T_PRIMARY)]['cp1']:.4f}"
          f" ({'holds' if b3 else 'fails'}).", "",
          ("The gate half of the measurement model follows from the active-inference"
           " construction: the belief over the other's intention, propagated through the"
           " predictive model, gates the looming axis as well as card G.1's fitted gate does,"
           " with nothing fitted but the response model. The caveat stated in advance stands: on"
           " these cells the intention posterior is binary, so what is derived is the gate's"
           " level (from the prior) and its opening (from the lateral-rate likelihood); a graded"
           " belief is untested (query S16.Q2)."
           if verdict.startswith("DERIVED") else
           "The belief gate does not reproduce card G.1's gate on this design at the pre-stated"
           " rules; the table says where it falls short."), "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj6_belief_gate.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
