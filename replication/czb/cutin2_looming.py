"""Follow-up to card EL.1: is the fitted linear rule the looming-rate threshold?

THE PRE-REGISTRATION. Written before the run.

Motivation
----------
EL.1 (`cutin2_two_axis.py` -> `out/cutin2_two_axis.md`) found that on the 288 CP2-CP5
cells of the second cut-in study, a linear rule x = w*(-log gap) + (1-w)*(-log TTC), with
w fitted at 0.47-0.51 in every held-out fold, scores held-out weighted RMSE 0.1137
against 0.1522 for the 1D log-gap threshold. Algebra: for a vehicle of width W at gap g
closing at speed dv, the small-angle optical expansion (looming) rate is
theta_dot ~= W*dv/g^2, so gap*TTC = g^2/dv = W/theta_dot. Equal weights on -log(gap) and
-log(TTC) therefore mean the cue is -log(gap*TTC) = log(theta_dot/W) = log(theta_dot) -
log(W); with W constant across cells this is log(theta_dot) up to an additive constant
absorbed by the fitted threshold c. This card checks that identity against the actual
optical quantities (not the small-angle approximation used only to motivate it).

Data, fit, folds, metric: identical to EL.1 and to the registered R.2 comparison
(`cutin2_field_vs_gap`): the same 288 CP2-CP5 cells from `out/cutin2_cells.csv`,
weighted least squares on the cell surface (`T.fit_reg`, a finite-objective-guarded
wrapper around the registered multi-start L-BFGS-B fitter), primary folds
leave-one-starting-TTC-out (`cells.ttc_start`), weights `cells.n`, response `cells.p`.
Nothing in `cutin2_two_axis` (T) or `cutin2_field_vs_gap` (R) is modified; both are
imported. (a) and (i) below are reproduced via `T.held_out` directly (models "gap" and
"ttc" respectively -- "ttc"'s covariate `-log(ttc_true)` is exactly `log(1/TTC)`, i.e.
inverse tau); the EL.1 linear rule is reproduced via `T.held_out(..., "linear")` rather
than hardcoded, so every number in the output traces to a function call in this run.
(h) and (j) use a hand-written held-out loop that calls the same `T.fit_reg` and
`R.predict` primitives per fold on a precomputed covariate array -- equivalent to what
`T.held_out`'s "gap"/"ttc" branches do, since `axes()` there is a deterministic,
fit-independent transform of `cells.distance` / `cells.ttc_true` and so is unaffected by
whether it is evaluated on the training subset or on the full array before splitting.

Models (all 1D thresholds P = b + (1-b) Phi(s (x - c)/sigma), s = +1, fitted by
T.fit_reg, scored by R.predict / T.wrmse):
  (a) x = -log(gap)                                    [reference; must reproduce 0.1522]
  (h) x = log(theta_dot), theta_dot = W*dv / (gap^2 + W^2/4) -- the EXACT time derivative
      of theta = 2*atan(W/(2*gap)) at fixed dv (chain rule on gap(t) with d(gap)/dt = -dv;
      no small-angle approximation), W the cut-in vehicle's own width from its trace
  (i) x = log(1/TTC) = -log(ttc_true)                  [inverse tau, cf. Xue et al. 2018;
                                                          must reproduce 0.1679]
  (j) x = log(theta) = log(2*atan(W/(2*gap)))          [optical size alone, no rate]
Also reproduced for reference: the EL.1 linear rule (c), via T.held_out(..., "linear").

W is taken from `load_cutin_trace(...).tar_wid` on the trace each cell's video belongs
to (trace name recovered from the video filename via R.VIDEO_RE, exactly as
`cutin2_field_vs_gap.video_covariates` maps video -> trace key). gap = cells.distance
(m), dv = cells.dv_kph * 1000/3600 (m/s) -- the design's closing speed, constant over
each clip's shown window by construction (the target's speed is fixed at 25 m/s and the
ego's speed is fixed per DV level; diagnostic report section 3) -- and ttc_true =
cells.ttc_true (s), exactly the columns and units EL.1 and R.2 use, so the comparison is
on the registered pipeline. Assumption (stated, not tested further here): dv is constant
over the shown window, so d(gap)/dt = -dv is exact and theta_dot above is the exact
derivative of theta, not a further approximation beyond the small-angle formula for
theta itself.

DECISION RULE (pre-stated), comparing (h)'s held-out wRMSE to the linear rule's (both
computed in this run):
  * within 0.005 of the linear rule: the equal-weight rule from EL.1 IS the looming-rate
    threshold on this data -- the algebraic identity holds numerically.
  * worse than the linear rule by more than 0.01: the small-angle identity is not exact
    enough on this design; the linear rule is preferred as the empirical form.
  * otherwise (worse by 0.005-0.01, or better by any margin): inconclusive by the
    pre-stated margins -- report the difference and lean on which side of 0.01 it falls.
The difference is reported in all cases regardless of which branch is hit.

Also reported: (a), (i), (j), the sampling-noise floor (as in T.main: sqrt of the
weighted mean of p(1-p)/n, weights n), the width(s) found, and the median/range of
theta_dot over the cells plus its value at the full-sample fitted threshold c (converted
back from the log scale via exp(c)).

Run: python replication/czb/cutin2_looming.py    Output: out/cutin2_looming.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cutin2_two_axis as T          # noqa: E402
import cutin2_field_vs_gap as R      # noqa: E402

OUT = HERE / "out"
KPH = 1000.0 / 3600.0


def trace_key_of(video: str) -> str:
    m = R.VIDEO_RE.match(video)
    if m is None:
        raise ValueError(f"unparseable video name: {video}")
    return f"LC_dv{m['dv']}_Tlc{m['tlc']}_TTC{int(m['ttc']):02d}"


def widths_for(cells: pd.DataFrame) -> np.ndarray:
    """Target-vehicle width per cell, from each cell's own trace."""
    keys = cells.video.map(trace_key_of)
    cache: dict[str, float] = {}
    out = np.empty(len(cells))
    for i, k in enumerate(keys):
        if k not in cache:
            tr = R.load_cutin_trace(R.KIN / f"{k}_vehicle_states.csv")
            cache[k] = float(tr.tar_wid)
        out[i] = cache[k]
    return out, cache


def held_out_1d(x, y, w, folds):
    """The same per-fold fit/score pattern as T.held_out's "gap"/"ttc" branches
    (T.fit_reg on the training fold, R.predict on the held-out fold), for an
    arbitrary precomputed 1D covariate array."""
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        th = T.fit_reg(x[tr], y[tr], w[tr])
        pred[te] = R.predict(th, x[te], +1.0)
    return pred


def main() -> None:
    cells_all = pd.read_csv(OUT / "cutin2_cells.csv")
    cells = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    folds = cells.ttc_start.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))

    gap = cells.distance.to_numpy(float)
    ttc = cells.ttc_true.to_numpy(float)
    dv = cells.dv_kph.to_numpy(float) * KPH
    W, width_cache = widths_for(cells)
    widths_unique = sorted(set(width_cache.values()))

    theta = 2.0 * np.arctan(W / (2.0 * gap))
    theta_dot = W * dv / (gap ** 2 + W ** 2 / 4.0)

    x_h = np.log(theta_dot)
    x_j = np.log(theta)

    L = ["# Looming-rate identity check on the second cut-in study", "",
         "Generated by `replication/czb/cutin2_looming.py`; models, folds and decision"
         " rule pre-stated in its docstring. Same 288 CP2-CP5 cells, fit, folds and"
         " metric as EL.1 (`cutin2_two_axis.py`) and the registered R.2 comparison"
         " (`cutin2_field_vs_gap.py`). Do not edit by hand.", "",
         "| model | free parameters | held-out wRMSE | Spearman(pred, P) |",
         "|---|---|---|---|"]

    scores: dict[str, float] = {}
    rhos: dict[str, float] = {}

    def row(label, key, pred, nfree):
        s = T.wrmse(y, pred, w)
        r = float(spearmanr(pred, y).statistic)
        scores[key], rhos[key] = s, r
        L.append(f"| {label} | {nfree} | {s:.4f} | {r:+.3f} |")

    pred_a, _ = T.held_out(cells, folds, "gap")
    row("(a) 1D log gap [reference]", "a", pred_a, 3)

    pred_h = held_out_1d(x_h, y, w, folds)
    row("(h) 1D log looming rate, log(theta_dot)", "h", pred_h, 3)

    pred_i, _ = T.held_out(cells, folds, "ttc")
    row("(i) 1D log inverse TTC, log(1/TTC)", "i", pred_i, 3)

    pred_j = held_out_1d(x_j, y, w, folds)
    row("(j) 1D log optical size, log(theta)", "j", pred_j, 3)

    pred_lin, _ = T.held_out(cells, folds, "linear")
    row("(c) EL.1 linear rule, w log gap + (1-w) log TTC [reference]", "lin", pred_lin, 4)

    L += [f"| sampling-noise floor | - | {noise:.4f} | - |", ""]

    diff = scores["h"] - scores["lin"]
    if abs(diff) <= 0.005:
        decision = (f"**(h) is within 0.005 of the EL.1 linear rule (diff = {diff:+.4f}):"
                    f" the equal-weight rule IS the looming-rate threshold on this data"
                    f" -- the small-angle identity holds numerically.**")
    elif diff > 0.01:
        decision = (f"**(h) is worse than the EL.1 linear rule by more than 0.01"
                    f" (diff = {diff:+.4f}): the small-angle identity is NOT exact enough"
                    f" on this design; the linear rule is preferred as the empirical"
                    f" form.**")
    else:
        decision = (f"**Inconclusive by the pre-stated margins (diff = {diff:+.4f}):"
                    f" between 0.005 and 0.01 off the linear rule.**")
    L += [f"Looming rate (h) minus EL.1 linear rule (lin): {diff:+.4f}. "
          f"Also: gap (a) minus looming rate (h) = {scores['a'] - scores['h']:+.4f}; "
          f"inverse-TTC (i) minus looming rate (h) = {scores['i'] - scores['h']:+.4f}; "
          f"optical size (j) minus looming rate (h) = {scores['j'] - scores['h']:+.4f}.",
          "", decision, ""]

    L += ["## Widths and looming rate", "",
          f"Target-vehicle width: {'a single value, ' + f'{widths_unique[0]:.3f} m, across all' if len(widths_unique) == 1 else str(len(widths_unique)) + ' distinct values,'} "
          f"{len(width_cache)} traces feeding the 288 cells "
          f"(widths: {', '.join(f'{v:.3f}' for v in widths_unique)} m).", ""]

    th_full = T.fit_reg(x_h, y, w)
    c_full = th_full[1]
    theta_dot_c = float(np.exp(c_full))
    L += [f"theta_dot over the 288 cells: median {np.median(theta_dot):.4f} rad/s, "
          f"range {theta_dot.min():.4f}-{theta_dot.max():.4f} rad/s.",
          f"Full-sample fitted threshold c on log(theta_dot) = {c_full:+.4f}, i.e. "
          f"theta_dot at threshold = {theta_dot_c:.4f} rad/s.", ""]

    (OUT / "cutin2_looming.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
