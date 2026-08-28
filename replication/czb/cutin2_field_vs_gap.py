"""R.2 task 1 (blocker B2.Q4): the field versus a gap threshold on the second cut-in study.

THE PRE-REGISTRATION. Everything in this docstring was written and committed before the
comparison was run (2026-08-29, review gate R.2, tier-1 session). The decision rule is
stated here so the result cannot be argued with after the fact.

The question
------------
Study 1's longitudinal design is degenerate (correlation(gap, TTC) = 1.0000), so no fit
on it can distinguish "the driver thresholds the preference field" from "the driver
thresholds the gap". The second cut-in study crosses delta velocity with TTC, so
matched-TTC cells span a six-fold range of gap. This script fits the existing field to
that study and compares it against a gap threshold on identical held-out folds.

Data and units of analysis
--------------------------
* `cut-in_study_aggregate_trials_annotated.csv`: 10 944 trials, 144 participants (the
  file's own count; the context document's 168 predates exclusions). Filler trials
  (design factors NaN) are dropped.
* The cell is the **video** (378 lane-change clips). Participant means are formed per
  video first (a block-1 video is seen twice by the same participant), then the cell
  response is the mean of participant means, weighted in fitting by the number of
  participants contributing. This respects the between-subjects DV / CP / LCD / TTC5-7
  subsets (query B2.Q3).
* **Primary analysis: CP2-CP5 cells only** (the post-onset development the R.2 question
  is about). CP1 cells (pre-encroachment baseline) are held aside as a diagnostic: a
  pure gap threshold predicts graded intervention at CP1 wherever the gap is small
  (down to 3.9 m at DV07/TTC2), while the lane-gated field predicts a flat floor.
  Whichever way that contrast comes out is reported, and it does not enter the primary
  decision.
* Attention checks: the primary analysis keeps all 144 participants (one non-modal
  answer on a single catch question is weak grounds for exclusion; the correct answer
  is not documented). Sensitivity: the primary contrast re-run excluding the 20
  participants whose attention answer is non-modal (!= 5).

The field covariate
-------------------
`deficit_max`: the running maximum of the comfort-zone deficit over the SHOWN window
[S, E] encoded in the video filename, computed by the exact code path used for study 1
(`cutin_predictors` with `cutin_params` staging: clip's own desired speed, continuous
lane entry, counterfactual residual severity, k = 12) on the study's kinematic traces.
The shown-window convention follows the B2.Q1 fix (out/c1_covariate_defect.md).
Onset detection is NOT used: these traces drift laterally pre-onset, which defeats
`load_cutin_trace`'s 0.03 m absolute threshold (misdetects onset at trace t = 1.7
against a true onset near 15.1); the window and every criticality variable come from
the filename stamps and the annotated file instead. Verified in section 0 of the
report: the trace gap at E matches the annotated `distance` column, and gap / closing
speed at the CP1 endpoint matches the design's starting TTC.

The competing models
--------------------
Four scalar-threshold families, IDENTICAL in form and differing only in the covariate:

    P(intervene | cell) = b + (1 - b) * Phi(s * (x - c) / sigma)

with lapse b, threshold c, spread sigma fitted per model (3 parameters each), and s the
sign that makes larger-x mean more intervention (+1 for deficit and required
deceleration, -1 for gap and TTC):

    field   x = deficit_max            (the model under test)
    gap     x = distance               (the simplest alternative)
    ttc     x = TTC_true               (the time measure)
    areq    x = DV / (2 * TTC_true)    (the demand measure the field is built from)

Each covariate is also fitted on the log scale (log(x + 1) for deficit; log(x) for the
strictly positive others), and each model's score is the better of its two scales --
symmetric, so neither the field's heavy tail nor the gap's skew decides the contrast
by functional-form accident.

Fitting: weighted least squares on the cell surface (weights = participants per cell),
scipy L-BFGS-B with multiple starts; identical code path for every model.

Folds and metric
----------------
* **Primary folds: leave-one-starting-TTC-out** (6 folds, grouping all videos of one
  TTC_sec level). Grouped folds are the project's convention (A.3 used
  leave-one-criticality-out) and test transfer across the design's main axis.
* Secondary: leave-one-video-out (378 folds), reported for completeness.
* Metric: weighted RMSE between held-out cell predictions and observed cell means,
  pooled over folds; Spearman rho alongside. Two references: chance (the training
  folds' weighted mean carried to the held-out cells) and the sampling-noise floor
  (the binomial SE of each cell mean, aggregated with the same weights -- no model can
  beat it except by luck).

THE DECISION RULE (pre-stated)
------------------------------
On the primary folds, with dRMSE = RMSE_field - RMSE_gap (each model at its better
scale):

* dRMSE < -0.01  : the field beats the gap threshold; its kinematic content survives
                   the one test study 1 could not run.
* |dRMSE| <= 0.01: indistinguishable. The conclusion defaults to parsimony: the gap
                   threshold is one directly observable scene scalar, so the field's
                   kinematic content is NOT supported as the mechanism (it merely
                   fails less than it might have).
* dRMSE > +0.01  : the field is ruled against on its own scenario, and the project's
                   claim must be restated around what survives (the cross-scenario
                   trait; the boundary as a well-estimated scale) rather than around
                   the field as a mechanism.

The 0.01 margin is the resolution below which RMSE differences on 15-cell surfaces
were already treated as non-decisive in this project (query B.1.Q4); stated here
before either number is known.

Also reported (no decision attached): the within-row orderings -- Spearman(field, P)
within matched-TTC_true rows, where the scope report's model-free finding was that gap
orders every row negatively while required deceleration barely orders them at all.

Run:  python replication/czb/cutin2_field_vs_gap.py
Output: replication/czb/out/cutin2_field_vs_gap.md (+ csv of the cell table)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from comfortzone.cutin import cutin_params, cutin_predictors, load_cutin_trace  # noqa: E402

STUDY2 = REPO / "external/01_studies/01_Studies/02_Cut-in"
TRIALS = STUDY2 / "cut-in_study_aggregate_trials_annotated.csv"
KIN = STUDY2 / "02_Kinematics"
OUT = HERE / "out"
KPH = 1000.0 / 3600.0
EGO_LEN = 4.6          # study-1 convention: bicycle lf + lr; used only for gap validation

VIDEO_RE = re.compile(
    r"LC_dv(?P<dv>\d+)_Tlc(?P<tlc>\dp\d)_TTC0?(?P<ttc>\d+)_CP(?P<cp>\d)"
    r"_S(?P<s>\d+p\d+)_E(?P<e>\d+p\d+)")


def _f(tok: str) -> float:
    return float(tok.replace("p", "."))


def video_covariates() -> pd.DataFrame:
    """One row per lane-change video: the field covariate over the shown window,
    plus trace-derived validation quantities."""
    d = pd.read_csv(TRIALS, low_memory=False)
    vids = sorted(v for v in d.video.unique() if "dummy" not in v)
    fields: dict[str, pd.DataFrame] = {}
    rows = []
    for v in vids:
        m = VIDEO_RE.match(v)
        if m is None:
            raise ValueError(f"unparseable video name: {v}")
        dv, tlc, ttc, cp = m["dv"], m["tlc"], int(m["ttc"]), int(m["cp"])
        s_t, e_t = _f(m["s"]), _f(m["e"])
        key = f"LC_dv{dv}_Tlc{tlc}_TTC{ttc:02d}"
        if key not in fields:
            tr = load_cutin_trace(KIN / f"{key}_vehicle_states.csv")
            fields[key] = cutin_predictors(tr, cutin_params(tr))
        f = fields[key]
        t = f.t.to_numpy()
        shown = (t >= s_t) & (t <= e_t + 1e-9)
        i_end = int(np.searchsorted(t, e_t, side="right")) - 1
        rows.append({
            "video": v, "trace": key, "dv_kph": float(dv), "lcd_s": _f(tlc),
            "ttc_start": float(ttc), "cp": cp, "s_t": s_t, "e_t": e_t,
            "deficit_max": float(f.deficit.to_numpy()[shown].max()),
            "gap_trace": float(f.gap_m.iloc[i_end]),
            "vrel_trace": float(f.v_rel.iloc[i_end]),
            "p_lane_end": float(f.p_lane.iloc[i_end]),
        })
    return pd.DataFrame(rows)


def cell_table() -> tuple[pd.DataFrame, pd.DataFrame]:
    """The fitting table: one row per video with data, participant means first.
    Returns (cells, per-participant means) -- the latter for the sensitivity rerun."""
    d = pd.read_csv(TRIALS, low_memory=False)
    d = d[d.group.notna()].copy()                      # drop fillers
    att = d.groupby("Exp_Subject_Id").attention1.max()  # one nonzero row each
    d["att_ok"] = d.Exp_Subject_Id.map(att) == 5
    pm = (d.groupby(["Exp_Subject_Id", "video", "att_ok"])
            .agg(p=("CZB_1", "mean"),
                 ttc_true=("TTC_true", "first"), distance=("distance", "first"),
                 dv_kph=("DV_kph", "first"), cp=("CP", "first"),
                 lcd=("LCD_sec", "first"))
            .reset_index())
    cov = video_covariates()
    pm = pm.merge(cov[["video", "deficit_max", "gap_trace", "vrel_trace",
                       "p_lane_end", "ttc_start"]], on="video", how="left")
    if pm.deficit_max.isna().any():
        raise RuntimeError("videos without a computed field covariate")

    def agg(g):
        return pd.Series({
            "p": g.p.mean(), "n": len(g),
            "deficit_max": g.deficit_max.iloc[0], "distance": g.distance.iloc[0],
            "ttc_true": g.ttc_true.iloc[0], "dv_kph": g.dv_kph.iloc[0],
            "cp": g.cp.iloc[0], "lcd": g.lcd.iloc[0],
            "ttc_start": g.ttc_start.iloc[0],
            "gap_trace": g.gap_trace.iloc[0], "vrel_trace": g.vrel_trace.iloc[0],
            "p_lane_end": g.p_lane_end.iloc[0],
        })
    cells = pm.groupby("video").apply(agg, include_groups=False).reset_index()
    cells["a_req"] = cells.dv_kph * KPH / (2.0 * cells.ttc_true)
    return cells, pm


# ---------------------------------------------------------------------------------
# the model family: P = b + (1 - b) * Phi(s * (x - c) / sigma)
# ---------------------------------------------------------------------------------

def predict(theta, x, sign):
    b, c, log_sig = theta
    b = 1.0 / (1.0 + np.exp(-b))                 # lapse in (0, 1) via logit
    z = sign * (x - c) / np.exp(log_sig)
    return b + (1.0 - b) * norm.cdf(z)


def fit(x, y, w, sign):
    """Weighted least squares with multi-start L-BFGS-B; returns best theta."""
    lo, hi = np.quantile(x, [0.1, 0.9])
    spread = max(np.std(x), 1e-6)
    best, best_val = None, np.inf
    for c0 in np.linspace(lo, hi, 5):
        for ls0 in (np.log(spread), np.log(spread / 4 + 1e-9)):
            th0 = np.array([-2.0, c0, ls0])
            r = minimize(lambda th: float(np.sum(w * (predict(th, x, sign) - y) ** 2)),
                         th0, method="L-BFGS-B")
            if r.fun < best_val:
                best, best_val = r.x, r.fun
    return best


MODELS = {          # covariate column, sign, log-transform
    "field": ("deficit_max", +1.0),
    "gap": ("distance", -1.0),
    "ttc": ("ttc_true", -1.0),
    "areq": ("a_req", +1.0),
}


def covariate(cells, name, log_scale):
    col, sign = MODELS[name]
    x = cells[col].to_numpy(float)
    if log_scale:
        x = np.log1p(x) if name == "field" else np.log(np.maximum(x, 1e-9))
    return x, sign


def held_out(cells, fold_ids, name, log_scale):
    """Pooled held-out predictions under the given fold grouping."""
    x, sign = covariate(cells, name, log_scale)
    y = cells.p.to_numpy(float)
    w = cells.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    chance = np.full_like(y, np.nan)
    for f in np.unique(fold_ids):
        tr, te = fold_ids != f, fold_ids == f
        th = fit(x[tr], y[tr], w[tr], sign)
        pred[te] = predict(th, x[te], sign)
        chance[te] = np.average(y[tr], weights=w[tr])
    return pred, chance


def wrmse(y, pred, w):
    return float(np.sqrt(np.average((pred - y) ** 2, weights=w)))


def run_comparison(cells, fold_ids, label, lines):
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))
    lines.append(f"### Folds: {label}\n")
    lines.append("| model | scale | held-out wRMSE | Spearman rho |")
    lines.append("|---|---|---|---|")
    scores = {}
    for name in MODELS:
        for log_scale in (False, True):
            pred, chance = held_out(cells, fold_ids, name, log_scale)
            r = wrmse(y, pred, w)
            rho = float(spearmanr(pred, y).statistic)
            scores[(name, log_scale)] = r
            lines.append(f"| {name} | {'log' if log_scale else 'raw'} | {r:.4f} | "
                         f"{rho:+.3f} |")
    _, chance = held_out(cells, fold_ids, "gap", False)
    lines.append(f"| chance (train mean) | - | {wrmse(y, chance, w):.4f} | - |")
    lines.append(f"| sampling-noise floor | - | {noise:.4f} | - |")
    lines.append("")
    best = {name: min(scores[(name, False)], scores[(name, True)]) for name in MODELS}
    lines.append("Best-scale scores: "
                 + ", ".join(f"{k} {v:.4f}" for k, v in best.items()) + ".\n")
    return best


def main() -> None:
    cells_all, pm = cell_table()
    lines = ["# The field versus a gap threshold on the second cut-in study (R.2 task 1)",
             "",
             "Generated by `replication/czb/cutin2_field_vs_gap.py`. The design, models,"
             " folds and decision rule were pre-registered in the script's docstring and"
             " committed before this comparison was run. Do not edit by hand.",
             ""]

    # --- section 0: validation of the trace-derived covariates ---------------------
    v = cells_all
    gap_err = (v.gap_trace - EGO_LEN / 2.0 - v.distance).abs()
    ttc_trace = v.gap_trace / np.maximum(v.vrel_trace, 1e-9)
    ttc_err = (ttc_trace - v.ttc_true).abs()
    lines += ["## 0 Two-route validation of the stimulus computation\n",
              "| check | median | max |", "|---|---|---|",
              f"| trace gap at E (center, minus lr) vs annotated `distance` [m] | "
              f"{gap_err.median():.2f} | {gap_err.max():.2f} |",
              f"| trace gap/closing-speed at E vs annotated `TTC_true` [s] | "
              f"{ttc_err.median():.2f} | {ttc_err.max():.2f} |",
              "",
              f"{len(v)} lane-change videos with data; participants per video "
              f"{int(v.n.min())}-{int(v.n.max())}.\n"]

    # --- primary: CP2-CP5 ----------------------------------------------------------
    cells = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    lines.append("## 1 Primary comparison (CP2-CP5)\n")
    fold_primary = cells.ttc_start.to_numpy()
    best = run_comparison(cells, fold_primary, "leave-one-starting-TTC-out (primary)",
                          lines)
    d_rmse = best["field"] - best["gap"]
    verdict = ("the field beats the gap threshold" if d_rmse < -0.01 else
               "indistinguishable -> parsimony: the field's kinematic content is NOT "
               "supported as the mechanism" if abs(d_rmse) <= 0.01 else
               "the field is ruled against on its own scenario")
    lines.append(f"**Pre-registered decision**: dRMSE = RMSE_field - RMSE_gap = "
                 f"{d_rmse:+.4f} -> **{verdict}**.\n")
    run_comparison(cells, np.arange(len(cells)), "leave-one-video-out (secondary)",
                   lines)

    # --- sensitivity: attention-modal participants only ----------------------------
    pm_ok = pm[pm.att_ok]
    def agg2(g):
        return pd.Series({"p": g.p.mean(), "n": len(g)})
    c2 = pm_ok.groupby("video").apply(agg2, include_groups=False).reset_index()
    c2 = c2.merge(cells_all.drop(columns=["p", "n"]), on="video")
    c2 = c2[c2.cp != "CP1"].reset_index(drop=True)
    lines.append("## 2 Sensitivity: excluding non-modal attention answers\n")
    best2 = run_comparison(c2, c2.ttc_start.to_numpy(),
                           "leave-one-starting-TTC-out, attention-modal only", lines)
    lines.append(f"dRMSE under the exclusion: {best2['field'] - best2['gap']:+.4f}.\n")

    # --- within-row orderings ------------------------------------------------------
    lines.append("## 3 Within-row orderings at matched TTC_true (descriptive)\n")
    lines.append("| TTC_true [s] | cells | rho(field, P) | rho(gap, P) | rho(a_req, P) |")
    lines.append("|---|---|---|---|---|")
    for ttc, g in cells.groupby("ttc_true"):
        if len(g) < 4:
            continue
        rf = float(spearmanr(g.deficit_max, g.p).statistic)
        rg = float(spearmanr(g.distance, g.p).statistic)
        ra = float(spearmanr(g.a_req, g.p).statistic)
        lines.append(f"| {ttc:.1f} | {len(g)} | {rf:+.2f} | {rg:+.2f} | {ra:+.2f} |")
    lines.append("")

    # --- CP1 diagnostic ------------------------------------------------------------
    cp1 = cells_all[cells_all.cp == "CP1"].reset_index(drop=True)
    lines.append("## 4 CP1 diagnostic (pre-registered as no-decision)\n")
    lines.append("A gap threshold predicts graded intervention at CP1 wherever the gap "
                 "is small; the lane-gated field predicts a flat floor.\n")
    rho_gap = float(spearmanr(cp1.distance, cp1.p).statistic)
    rho_field = float(spearmanr(cp1.deficit_max, cp1.p).statistic)
    lines += [f"{len(cp1)} CP1 cells; P(intervene) range "
              f"{cp1.p.min():.3f}-{cp1.p.max():.3f}; "
              f"rho(gap, P) = {rho_gap:+.3f}; rho(field covariate, P) = "
              f"{rho_field:+.3f}; field covariate range "
              f"{cp1.deficit_max.min():.1f}-{cp1.deficit_max.max():.1f}.\n"]

    cells_all.to_csv(OUT / "cutin2_cells.csv", index=False)
    (OUT / "cutin2_field_vs_gap.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
