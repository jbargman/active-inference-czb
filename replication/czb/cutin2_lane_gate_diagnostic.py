"""Post-hoc diagnostic of the R.2 field-versus-gap verdict: where does the field's loss come from?

NOT a re-decision. The pre-registered comparison in `cutin2_field_vs_gap.py` stands as
registered; this script decomposes its result so the verdict's *scope* can be stated
precisely (review of the decisive pipeline, 2026-09-02, tier-1 session). Two questions:

1. **Is the verdict numerically robust?** The registered script fits by multi-start
   L-BFGS-B. Here the same three-parameter threshold model is fitted by an independent
   route -- a dense grid over (threshold, spread) with the lapse solved in closed form --
   on the same cells, folds and metric, and the field-minus-gap RMSE difference is given a
   cell-bootstrap interval.

2. **Which part of the field fails?** The field covariate is the running maximum of the
   pragmatic deficit, which on these cells is almost entirely the safety term:

       gate(lateral state) x magnitude(longitudinal counterfactual)

   with `gate` the lane-entry weight (a *project* construction, 2026-08-27) and
   `magnitude` the residual relative speed under "lead brakes at a_OV,min, ego reacts
   after t_react and then brakes at a_max" (released content, made continuous). The two
   are separated by recomputing the covariate with the gate forced to 1 (monkeypatching
   `aidriver.preferences.lane_entry_weight`) and re-running the held-out comparison, raw
   and with the ego-speed jitter floor removed (section 5 of the registered report).
   Local sensitivities of the magnitude to gap, lead speed and ego speed are printed so
   the within-row (matched-TTC) failure can be read mechanistically.

Inputs: `out/cutin2_cells.csv` (the registered cell table) and the study-2 traces.
Output: `out/cutin2_lane_gate_diagnostic.md`. Run: python replication/czb/cutin2_lane_gate_diagnostic.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

import aidriver.preferences as P  # noqa: E402
import cutin2_field_vs_gap as R  # noqa: E402  (the registered script: data path, fit, folds)
from aidriver.preferences import PreferenceParams, residual_delta_v  # noqa: E402

OUT = HERE / "out"
SMOOTH_S = 0.5      # the registered report's section-5 window


# ---------------------------------------------------------------------------------
# covariates with the lane-entry gate forced to 1
# ---------------------------------------------------------------------------------

def field_covariates(gate_to_one: bool, smooth_ego_s: float | None) -> pd.DataFrame:
    if gate_to_one:
        orig = P.lane_entry_weight
        P.lane_entry_weight = lambda obs, p: np.ones(np.shape(np.asarray(obs["dy"], float)))
    try:
        return R.video_covariates(smooth_ego_s=smooth_ego_s)[["video", "deficit_max"]]
    finally:
        if gate_to_one:
            P.lane_entry_weight = orig


# ---------------------------------------------------------------------------------
# the independent fit: grid over (c, sigma), lapse in closed form
# ---------------------------------------------------------------------------------

def fit_grid(x, y, w, sign):
    """P = b + (1-b) Phi(sign (x-c)/sigma). For fixed (c, sigma) the weighted LS lapse is
    b = sum w u (y - Phi) / sum w u^2 with u = 1 - Phi, clipped to [0, 1]."""
    lo, hi = float(x.min()), float(x.max())
    span = max(hi - lo, 1e-9)
    cs = np.linspace(lo - 0.5 * span, hi + 0.5 * span, 161)
    sigs = np.exp(np.linspace(np.log(span / 200.0), np.log(span * 3.0), 81))
    best = (np.inf, None)
    for c in cs:
        for s in sigs:
            phi = norm.cdf(sign * (x - c) / s)
            u = 1.0 - phi
            b = float(np.sum(w * u * (y - phi)) / max(np.sum(w * u * u), 1e-12))
            b = min(max(b, 0.0), 1.0)
            sse = float(np.sum(w * (b + (1.0 - b) * phi - y) ** 2))
            if sse < best[0]:
                best = (sse, (b, c, s))
    return best[1]


def predict_grid(th, x, sign):
    b, c, s = th
    return b + (1.0 - b) * norm.cdf(sign * (x - c) / s)


def held_out(x, y, w, folds, sign, fitter, predictor):
    pred = np.full_like(y, np.nan)
    per_fold = {}
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        th = fitter(x[tr], y[tr], w[tr], sign)
        pred[te] = predictor(th, x[te], sign)
        per_fold[float(f)] = (th, float(np.sqrt(np.average((pred[te] - y[te]) ** 2,
                                                            weights=w[te]))))
    return pred, per_fold


def wrmse(y, pred, w):
    return float(np.sqrt(np.average((pred - y) ** 2, weights=w)))


def scale(col, x, log_scale):
    if not log_scale:
        return x
    return np.log1p(x) if col.startswith("deficit") else np.log(np.maximum(x, 1e-9))


COVS = {   # column -> sign
    "deficit_max": +1.0, "deficit_nolane": +1.0,
    "deficit_smooth": +1.0, "deficit_nolane_smooth": +1.0,
    "distance": -1.0, "ttc_true": -1.0, "a_req": +1.0,
}
LABEL = {
    "deficit_max": "field (as registered)",
    "deficit_smooth": "field, ego speed smoothed",
    "deficit_nolane": "field, lane gate := 1",
    "deficit_nolane_smooth": "field, lane gate := 1, ego smoothed",
    "distance": "gap", "ttc_true": "TTC", "a_req": "required deceleration",
}


def best_of_scales(cells, col, folds, fitter, predictor):
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    best = None
    for log_scale in (False, True):
        x = scale(col, cells[col].to_numpy(float), log_scale)
        pred, pf = held_out(x, y, w, folds, COVS[col], fitter, predictor)
        r = wrmse(y, pred, w)
        if best is None or r < best["rmse"]:
            best = {"rmse": r, "log": log_scale, "pred": pred, "per_fold": pf,
                    "rho": float(spearmanr(pred, y).statistic)}
    return best


def main() -> None:
    rng = np.random.default_rng(20260901)
    cells_all = pd.read_csv(OUT / "cutin2_cells.csv")
    for label, gate, sm in (("deficit_nolane", True, None),
                            ("deficit_nolane_smooth", True, SMOOTH_S),
                            ("deficit_smooth", False, SMOOTH_S)):
        cov = field_covariates(gate, sm).rename(columns={"deficit_max": label})
        cells_all = cells_all.merge(cov, on="video", how="left")
    cells = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    folds = cells.ttc_start.to_numpy(float)

    L = ["# Where the field's loss comes from: a decomposition of the R.2 verdict", "",
         "Generated by `replication/czb/cutin2_lane_gate_diagnostic.py`. Post-hoc, NOT a"
         " re-decision: the pre-registered verdict in `cutin2_field_vs_gap.md` stands as"
         " registered. Do not edit by hand.", ""]

    # --- 1 independent fit --------------------------------------------------------
    L += ["## 1 The registered numbers by an independent fitting route", "",
          "Same 288 CP2-CP5 cells, same leave-one-starting-TTC-out folds, same weighted"
          " RMSE; the three-parameter threshold fitted by a 161 x 81 grid over"
          " (threshold, spread) with the lapse solved in closed form, instead of the"
          " registered multi-start L-BFGS-B. Each covariate at its better scale.", "",
          "| covariate | grid fit wRMSE | registered wRMSE | scale | Spearman |",
          "|---|---|---|---|---|"]
    registered = {"deficit_max": 0.3471, "distance": 0.1522, "ttc_true": 0.1679,
                  "a_req": 0.2888}
    grid = {}
    for col in ("deficit_max", "distance", "ttc_true", "a_req"):
        g = best_of_scales(cells, col, folds, fit_grid, predict_grid)
        grid[col] = g
        L.append(f"| {LABEL[col]} | {g['rmse']:.4f} | {registered[col]:.4f} | "
                 f"{'log' if g['log'] else 'raw'} | {g['rho']:+.3f} |")
    d_grid = grid["deficit_max"]["rmse"] - grid["distance"]["rmse"]
    boots = []
    pf, pg = grid["deficit_max"]["pred"], grid["distance"]["pred"]
    for _ in range(4000):
        i = rng.integers(0, len(y), len(y))
        boots.append(wrmse(y[i], pf[i], w[i]) - wrmse(y[i], pg[i], w[i]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    L += ["", f"Field minus gap under the grid fit: dRMSE = {d_grid:+.4f} (registered"
          f" +0.1949); cell-bootstrap 95% interval [{lo:+.3f}, {hi:+.3f}] against the"
          " pre-registered margin of 0.01. Differences between the two fitting routes are"
          " at the third decimal -- the threshold objective is flat near its optimum on"
          " the field's heavy-tailed scale -- and are irrelevant at this margin.", ""]
    L += ["Per held-out fold (the fold is the starting-TTC level held out):", "",
          "| held-out TTC | field wRMSE | field (b, c, sigma) | gap wRMSE | gap (b, c, sigma) |",
          "|---|---|---|---|---|"]
    for f in sorted(grid["deficit_max"]["per_fold"]):
        tf, rf = grid["deficit_max"]["per_fold"][f]
        tg, rg = grid["distance"]["per_fold"][f]
        L.append(f"| {f:.0f} s | {rf:.3f} | ({tf[0]:.2f}, {tf[1]:.0f}, {tf[2]:.0f}) | "
                 f"{rg:.3f} | ({tg[0]:.2f}, {tg[1]:.2f}, {tg[2]:.2f}) |")
    L.append("")

    # --- 2 the gate ---------------------------------------------------------------
    L += ["## 2 The lane-entry gate's share of the loss", "",
          "The field covariate recomputed with the lane-entry weight forced to 1 -- the"
          " conflict geometry taken to apply fully from the first post-onset frame -- and"
          " the registered held-out comparison re-run (registered fit: multi-start"
          " L-BFGS-B, `cutin2_field_vs_gap.fit`). Model-free rank correlations with the"
          " cell response alongside.", "",
          "| covariate | held-out wRMSE | scale | Spearman(pred, P) | model-free Spearman(x, P) |",
          "|---|---|---|---|---|"]
    reg_fit = {}
    for col in ("deficit_max", "deficit_smooth", "deficit_nolane",
                "deficit_nolane_smooth", "distance", "ttc_true"):
        g = best_of_scales(cells, col, folds, R.fit, R.predict)
        reg_fit[col] = g
        mf = COVS[col] * float(spearmanr(cells[col], cells.p).statistic)
        L.append(f"| {LABEL[col]} | {g['rmse']:.4f} | {'log' if g['log'] else 'raw'} | "
                 f"{g['rho']:+.3f} | {mf:+.3f} |")
    chance = None
    _, chance = R.held_out(cells, folds, "gap", False)
    L += ["", f"Chance (training-fold mean carried over): {wrmse(y, chance, w):.4f}.", ""]
    total = reg_fit["deficit_max"]["rmse"] - reg_fit["distance"]["rmse"]
    gate_part = reg_fit["deficit_max"]["rmse"] - reg_fit["deficit_nolane"]["rmse"]
    L += [f"Of the field's {total:+.3f} deficit against the gap threshold, forcing the gate"
          f" to 1 recovers {gate_part:+.3f} ({100 * gate_part / total:.0f}%); the remaining"
          f" {total - gate_part:+.3f} is the longitudinal magnitude itself, which still"
          " loses to the gap threshold and to TTC.", ""]

    supp = cells[cells.p_lane_end < 0.9]
    L += ["Cells where the gate is below 0.9 at the shown-window end (the gate suppresses the"
          " deficit there):", "",
          f"{len(supp)} of {len(cells)} CP2-CP5 cells, mean P(intervene) {supp.p.mean():.3f}"
          f" against {cells[cells.p_lane_end >= 0.9].p.mean():.3f} elsewhere -- the gate"
          " acts on the most-responded cells. By starting TTC and lane-change duration:", "",
          "| starting TTC | LCD 2 s | LCD 3 s | LCD 4 s |", "|---|---|---|---|"]
    tab = supp.groupby(["ttc_start", "lcd"]).size().unstack(fill_value=0)
    for ttc in sorted(cells.ttc_start.unique()):
        row = tab.loc[ttc] if ttc in tab.index else None
        vals = [int(row.get(l, 0)) if row is not None else 0 for l in (2.0, 3.0, 4.0)]
        L.append(f"| {ttc:.0f} s | {vals[0]} | {vals[1]} | {vals[2]} |")
    L.append("")

    L += ["Median covariate by clip point and starting TTC (the registered field, then the"
          " gate-free smoothed field):", ""]
    for col in ("deficit_max", "deficit_nolane_smooth"):
        pv = cells.pivot_table(index="cp", columns="ttc_start", values=col, aggfunc="median")
        L += [f"*{LABEL[col]}*", "",
              "| clip point | " + " | ".join(f"TTC {c:.0f}" for c in pv.columns) + " |",
              "|---|" + "---|" * len(pv.columns)]
        for cp, r in pv.iterrows():
            L.append(f"| {cp} | " + " | ".join(f"{v:.0f}" for v in r) + " |")
        L.append("")
    L += ["Mean P(intervene) on the same grid:", ""]
    pv = cells.pivot_table(index="cp", columns="ttc_start", values="p", aggfunc="mean")
    L += ["| clip point | " + " | ".join(f"TTC {c:.0f}" for c in pv.columns) + " |",
          "|---|" + "---|" * len(pv.columns)]
    for cp, r in pv.iterrows():
        L.append(f"| {cp} | " + " | ".join(f"{v:.2f}" for v in r) + " |")
    L.append("")

    L += ["Within matched-TTC rows (rows with at least 6 cells): how many the covariate"
          " orders in the observed direction, and the mean rank correlation:", "",
          "| covariate | rows ordered like the data | mean rho(x, P) |", "|---|---|---|"]
    for col in ("deficit_max", "deficit_smooth", "deficit_nolane", "deficit_nolane_smooth",
                "distance"):   # TTC is constant within a matched-TTC row by construction
        rs = [float(spearmanr(g[col], g.p).statistic) for _, g in cells.groupby("ttc_true")
              if len(g) >= 6]
        agree = sum(1 for r in rs if COVS[col] * r > 0)
        L.append(f"| {LABEL[col]} | {agree} of {len(rs)} | {np.mean(rs):+.2f} |")
    fast = cells[cells.lcd == 2.0]
    L += ["", f"On the {len(fast)} cells with the 2 s lane change (gate at the window end"
          f" >= {fast.p_lane_end.min():.3f} everywhere), the registered field's model-free"
          f" rank correlation with P is {spearmanr(fast.deficit_max, fast.p).statistic:+.3f}"
          f" against the gap's {-spearmanr(fast.distance, fast.p).statistic:+.3f}.", ""]

    # --- 3 the magnitude's sensitivities ----------------------------------------------
    p = PreferenceParams(lane_entry_shape_k=12.0)
    Lveh = p.vehicle.lf + p.vehicle.lr

    def dv(v, gap, vo):
        return float(residual_delta_v({"v": v, "a": 0.0, "dx": gap + Lveh,
                                       "v_other": vo, "a_other": 0.0}, p))

    L += ["## 3 Why the magnitude orders matched-TTC cells by speed rather than by gap", "",
          "The safety magnitude is the residual relative speed `dv_resid` in the counterfactual"
          f" \"lead brakes at {p.a_other_min:.0f} m/s2 to a stop; ego reacts after"
          f" {p.response_time:.0f} s, then brakes at {p.a_max:.0f} m/s2\":", "",
          "    dv_resid^2 = v_react^2 - 2 a_max [ gap + v_lead^2 / (2 |a_lead|) - v_ego t_react - 1.15 L ]", "",
          "Local sensitivities at four cells of the study (finite differences of 1 m and"
          " 1 m/s):", "",
          "| ego speed | gap | v_rel | dv_resid | per m of gap | per m/s of lead speed | per m/s of ego speed |",
          "|---|---|---|---|---|---|---|"]
    for v, gap, vr in ((30.7, 6.2, 5.7), (30.7, 17.4, 5.7), (36.5, 11.7, 11.5),
                       (36.5, 33.0, 11.5)):
        vo = v - vr
        base = dv(v, gap, vo)
        L.append(f"| {v} m/s | {gap} m | {vr} m/s | {base:.1f} | {dv(v, gap + 1, vo) - base:+.2f} | "
                 f"{dv(v, gap, vo + 1) - base:+.2f} | {dv(v + 1, gap, vo) - base:+.2f} |")
    a = dv(36.5, 9.3, 25.0)
    b = dv(30.7, 4.7, 25.0)
    c = dv(30.7, 9.3, 25.0)
    L += ["", "The study realizes its delta-velocity levels partly through the ego speed"
          " (30.7 m/s in the 21 km/h clips, 36.5 m/s in the 42 km/h clips; the target at"
          " 25.0 m/s in both). At matched TTC 0.8 s the 42 km/h cell (gap 9.3 m) scores"
          f" dv_resid {a:.1f} against the 21 km/h cell's (gap 4.7 m) {b:.1f}; holding both"
          f" speeds at the 21 km/h cell's values, the larger gap alone would give {c:.1f}"
          " -- the direction the data take. Per metre of gap the magnitude moves by a third"
          " of a metre per second; per metre per second of either vehicle's speed it moves"
          " by one and a half to two. In this regime the counterfactual is violated"
          " everywhere, and the term measures how bad the worst case would be, which is"
          " set by the absolute speeds far more than by the current gap.", ""]

    # --- 4 trace-vs-annotation ------------------------------------------------------
    ca = cells_all.copy()
    ca["ttc_tr"] = ca.gap_trace / np.maximum(ca.vrel_trace, 1e-9)
    ca["ttc_err"] = (ca.ttc_tr - ca.ttc_true).abs()
    ca["gap_err"] = (ca.gap_trace - R.EGO_LEN / 2.0 - ca.distance).abs()
    L += ["## 4 The trace-versus-annotation discrepancies, located", "",
          "The registered report's section 0 gives a maximum TTC discrepancy of 1.9 s between"
          " the trace-derived state and the annotated design value. It sits in the 7 km/h"
          " clips, where a closing speed of 1.9 m/s turns centimetre-per-second speed"
          " differences into seconds of TTC; the gap discrepancy is a near-constant offset,"
          " a definitional difference in where the gap is measured.", "",
          "| DV [km/h] | median TTC discrepancy [s] | max | median gap discrepancy [m] | max |",
          "|---|---|---|---|---|"]
    for dvk, g in ca.groupby("dv_kph"):
        L.append(f"| {dvk:.0f} | {g.ttc_err.median():.2f} | {g.ttc_err.max():.2f} | "
                 f"{g.gap_err.median():.2f} | {g.gap_err.max():.2f} |")
    L += ["", "The design scalars enter the comparison at their annotated values and the field"
          " at the trace's, so any discrepancy handicaps the design scalars, not the field:"
          " the participants saw the rendered trace.", ""]

    (OUT / "cutin2_lane_gate_diagnostic.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
