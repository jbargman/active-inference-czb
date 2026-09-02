"""Attribution experiment: does a FIXED-HORIZON lane-entry gate recover the R.2 loss?

NOT a re-decision and NOT a model change. The pre-registered verdict in
`cutin2_field_vs_gap.md` stands as registered; `cutin2_field_vs_gap.py` is untouched and
is imported here as `R` so that the data path, the threshold family, the folds and the
metric are literally the registered ones. Written 2026-09-02, and everything below the
line "THE DECISION RULE" was committed to this docstring before the comparison was run.

The question
------------
At review gate R.2 the field lost to a gap threshold on the second cut-in study (field
held-out wRMSE 0.3471 -- quoted in the task brief as 0.3468, the difference is a
third-decimal fitting-route wobble and immaterial at the margins used here -- against the
gap's 0.1522, chance 0.3202, log-gap the winner). The pipeline review
(`docs/r2_pipeline_review.md`, `out/cutin2_lane_gate_diagnostic.md`) attributed about 44%
of that loss (+0.087 of the +0.199 deficit) to the PROJECT'S OWN lane-entry gate: the
weight `lane_entry_weight` projects the cut-in vehicle's lateral overlap to the moment of
LONGITUDINAL CLOSURE, which suppresses the deficit for slow lane changes at short starting
TTC -- exactly the cells participants respond to most. Forcing the gate to 1 recovered
that share; but "gate := 1" is not a model, it is the absence of one.

A colleague's external model uses a fixed-horizon anticipation instead: the lateral
clearance is extrapolated over a fixed encounter horizon t_enc = 3 s (not to the closure
time), and the gate is the probability that the predicted clearance falls below a
minimum, w = Phi((m_lat - l0 - ldot t_enc) / s_l). That gate produced the right pre-onset
floor in their data. This script asks whether substituting THAT anticipation for ours
recovers the gate's share of the loss.

What is substituted, and the reading of "fixed horizon"
-------------------------------------------------------
Only the projection time. `PreferenceParams.lane_entry_horizon_s` (added 2026-09-02,
default None = the existing closure-time projection, bit-identical) replaces tau_lon by a
fixed T in the one line where the lateral offset is extrapolated:

    |dy|_pred = max( |dy| - max(lateral closing rate, 0) * T , 0 )

The existing overlap-to-weight mapping, the 1.15 inflation, the inward clamp and the shape
constant k = 12 are all kept. The colleague's Phi(.) softening of the threshold is NOT
imported: their gate differs from ours in two ways at once (fixed horizon, and a
probit over a clearance minimum with two free parameters l0, s_l), and this experiment
isolates the ONE difference the pipeline review implicated. Our overlap ramp already plays
the role of their Phi -- it is a smooth, parameter-free map from predicted clearance to a
weight in [0, 1] -- so the substitution is horizon-for-tau_lon and nothing else. This is
the reading closest to "extrapolate the lateral position 3 s ahead at the current lateral
velocity, then apply the existing overlap-to-weight mapping", which is the reading the
task specifies where the two constructions are ambiguous.

One consequence is worth stating in advance, because it is the mechanism the experiment is
testing: under the closure-time projection a target with no longitudinal closing gets
tau_lon = inf and hence NO anticipation at all (the projection is defined to 0 there),
while under a fixed horizon it is still projected 3 s ahead. The gate therefore stops
collapsing on the slow-closure cells.

T = 3.0 s is the colleague's value, taken as given. It is not swept: a swept horizon
would be a fitted parameter on the response data this comparison is scored against.

Everything else identical to the registration
---------------------------------------------
* Cells: `R.cell_table()` -- 378 videos, participant means first, weighted by
  participants; the field covariate `deficit_max` is the running maximum of the
  comfort-zone deficit over the SHOWN window, `cutin_params` staging (clip's own desired
  speed, continuous lane entry, counterfactual residual severity, k = 12).
* The horizon covariate mirrors `R.video_covariates` exactly, with the flag set on the
  `PreferenceParams` that `cutin_params(tr)` returns; the covariate is then substituted
  into the `deficit_max` column, which is the same substitution the registered report's
  section 5 makes for the ego-smoothing sensitivity.
* Restriction to CP2-CP5 (`cp != "CP1"`), primary folds = leave-one-starting-TTC-out,
  metric = pooled weighted RMSE via `R.held_out` / `R.wrmse`, each covariate at the better
  of its raw and log scales.
* The registered field and the registered gap are re-scored here by the same route; they
  must reproduce 0.3471 and 0.1522, which is also the check that adding the flag left the
  flag-off path bit-identical.

THE DECISION RULE (pre-stated, before running)
----------------------------------------------
Let RMSE_h be the horizon-gated field's held-out wRMSE on the primary folds, at its
better scale.

* **Credited**: the horizon gate is credited with removing the lane-entry gate's share of
  the loss if RMSE_h <= 0.3468 - 0.05 = 0.2968, i.e. an improvement of at least 0.05 from
  the registered field. The 0.05 margin is set at roughly half of the +0.087 the pipeline
  review attributed to the gate, so a genuine recovery of "the gate's share" clears it and
  a third-decimal wobble does not.
* **Not credited**: RMSE_h > 0.2968. The colleague's anticipation is then not the missing
  piece either, and the gate's share of the loss is not recoverable by changing the
  projection time.
* **The field is still ruled against** if RMSE_h > 0.1522 + 0.01 = 0.1622, whatever
  happens above. This is EXPECTED, and it is not a second bite at the R.2 verdict: the
  counterfactual magnitude is the other ~56% of the loss (+0.113 of +0.199 in the
  diagnostic), and nothing here touches it. "Credited" and "still ruled against" are
  therefore both live at once, and that combination is the informative outcome: it would
  say the gate is a real and fixable defect of the project's construction while the
  field's longitudinal content still loses on this study.

No decision is attached to: the within-matched-TTC-row Spearman correlations (reported as
`R.main` section 3 reports them, with the count of rows the covariate orders like the data
-- POSITIVE rho, since the deficit is a criticality measure and larger should mean more
intervention), the CP1 pre-onset floor, or the gate-level diagnostics.

Run:  python replication/czb/cutin2_field_horizon_gate.py
Output: replication/czb/out/cutin2_field_horizon_gate.md
Log:    replication/czb/out/log_cutin2_field_horizon_gate.txt
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

import cutin2_field_vs_gap as R  # noqa: E402  (the registered script; never modified)
from comfortzone.cutin import cutin_params, cutin_predictors, load_cutin_trace  # noqa: E402

OUT = HERE / "out"
T_ENC = 3.0                 # the colleague's fixed encounter horizon [s]
REG_FIELD = 0.3471          # registered field wRMSE (out/cutin2_field_vs_gap.md)
REG_FIELD_BRIEF = 0.3468    # the value the task brief quotes; the rule is stated on it
REG_GAP = 0.1522            # registered gap threshold wRMSE
CREDIT_MARGIN = 0.05
RULED_MARGIN = 0.01


def video_covariates_horizon(t_enc: float) -> pd.DataFrame:
    """`R.video_covariates` with the fixed-horizon lane-entry gate.

    Mirrors the registered function line for line (same trial file, same video-name
    parse, same one-field-per-trace caching, same shown-window running maximum); the only
    difference is `lane_entry_horizon_s` set on the `PreferenceParams` that
    `cutin_params(tr)` returns. `cutin_predictors` re-stages through `cutin_params`, which
    respects a supplied `p`, so the flag survives to `lane_entry_weight`.
    """
    d = pd.read_csv(R.TRIALS, low_memory=False)
    vids = sorted(v for v in d.video.unique() if "dummy" not in v)
    fields: dict[str, pd.DataFrame] = {}
    rows = []
    for v in vids:
        m = R.VIDEO_RE.match(v)
        if m is None:
            raise ValueError(f"unparseable video name: {v}")
        dv, tlc, ttc, cp = m["dv"], m["tlc"], int(m["ttc"]), int(m["cp"])
        s_t, e_t = R._f(m["s"]), R._f(m["e"])
        key = f"LC_dv{dv}_Tlc{tlc}_TTC{ttc:02d}"
        if key not in fields:
            tr = load_cutin_trace(R.KIN / f"{key}_vehicle_states.csv")
            p = replace(cutin_params(tr), lane_entry_horizon_s=float(t_enc))
            fields[key] = cutin_predictors(tr, p)
        f = fields[key]
        t = f.t.to_numpy()
        shown = (t >= s_t) & (t <= e_t + 1e-9)
        i_end = int(np.searchsorted(t, e_t, side="right")) - 1
        rows.append({
            "video": v,
            "deficit_horizon": float(f.deficit.to_numpy()[shown].max()),
            "p_lane_end_h": float(f.p_lane.iloc[i_end]),
            "p_lane_max_h": float(f.p_lane.to_numpy()[shown].max()),
        })
    return pd.DataFrame(rows)


def score(cells, folds, col, label, lines):
    """Best-of-raw-and-log held-out wRMSE for `col`, through the registered code path.

    `col` is substituted into `deficit_max` and scored as the registered "field" model, so
    the sign, the log1p transform, the fold loop, the fitter and the metric are all the
    registered ones (the same substitution `R.main` section 5 uses).
    """
    c = cells.copy()
    c["deficit_max"] = c[col].to_numpy(float)
    y, w = c.p.to_numpy(float), c.n.to_numpy(float)
    best = None
    for log_scale in (False, True):
        pred, chance = R.held_out(c, folds, "field", log_scale)
        r = R.wrmse(y, pred, w)
        rho = float(spearmanr(pred, y).statistic)
        lines.append(f"| {label} | {'log' if log_scale else 'raw'} | {r:.4f} | {rho:+.3f} |")
        if best is None or r < best[0]:
            best = (r, "log" if log_scale else "raw", rho, chance)
    return best


def score_design(cells, folds, name, label, lines):
    """Same, for a registered design scalar (gap / TTC), by name in `R.MODELS`."""
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    best = None
    for log_scale in (False, True):
        pred, chance = R.held_out(cells, folds, name, log_scale)
        r = R.wrmse(y, pred, w)
        rho = float(spearmanr(pred, y).statistic)
        lines.append(f"| {label} | {'log' if log_scale else 'raw'} | {r:.4f} | {rho:+.3f} |")
        if best is None or r < best[0]:
            best = (r, "log" if log_scale else "raw", rho, chance)
    return best


def main() -> None:
    cells_all, _pm = R.cell_table()
    cov = video_covariates_horizon(T_ENC)
    cells_all = cells_all.merge(cov, on="video", how="left")
    if cells_all.deficit_horizon.isna().any():
        raise RuntimeError("videos without a horizon-gated field covariate")

    cells = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    folds = cells.ttc_start.to_numpy()
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))

    L = ["# A fixed-horizon lane-entry gate: attribution experiment on the R.2 loss", "",
         "Generated by `replication/czb/cutin2_field_horizon_gate.py`. Post-hoc"
         " attribution, NOT a re-decision and NOT a model change: the pre-registered"
         " verdict in `cutin2_field_vs_gap.md` stands as registered, and that script is"
         " imported unmodified for the data path, fits, folds and metric. The decision"
         " rule below was written into this script's docstring before it was run. Do not"
         " edit by hand.", "",
         "## 0 What was substituted", "",
         f"Only the lane-entry gate's projection time: `lane_entry_horizon_s = {T_ENC:.1f}`"
         " s replaces the longitudinal closure time tau_lon in",
         "",
         "    |dy|_pred = max( |dy| - max(lateral closing rate, 0) * T , 0 )",
         "",
         "leaving the overlap-to-weight mapping, the 1.15 inflation, the inward clamp and"
         " the CZB shape constant k = 12 exactly as they are. The colleague's probit"
         " softening (two free parameters l0, s_l over a clearance minimum) is NOT"
         " imported -- our overlap ramp already maps predicted clearance smoothly to a"
         " weight in [0, 1], parameter-free, so the substitution isolates the one"
         " difference the pipeline review implicated. Reading of \"fixed horizon\":"
         " extrapolate the lateral position T seconds ahead at the current lateral"
         " velocity, then apply the existing mapping.", "",
         "The mechanism under test, stated before the run: under the closure-time"
         " projection a target with no longitudinal closing gets tau_lon = infinity and"
         " therefore no anticipation at all, while a fixed horizon still projects it 3 s"
         " ahead. The gate should stop collapsing on the slow-closure cells.", "",
         f"{len(cells_all)} lane-change videos; {len(cells)} CP2-CP5 cells;"
         f" participants per cell {int(cells.n.min())}-{int(cells.n.max())}.", ""]

    # --- 1 the primary comparison -------------------------------------------------
    L += ["## 1 Primary comparison (CP2-CP5, leave-one-starting-TTC-out)", "",
          "| model | scale | held-out wRMSE | Spearman rho |", "|---|---|---|---|"]
    b_reg = score(cells, folds, "deficit_max", "field (as registered)", L)
    b_hor = score(cells, folds, "deficit_horizon",
                  f"field, fixed horizon T = {T_ENC:.1f} s", L)
    b_gap = score_design(cells, folds, "gap", "gap threshold", L)
    b_ttc = score_design(cells, folds, "ttc", "TTC", L)
    chance = R.wrmse(y, b_gap[3], w)
    L += [f"| chance (train mean) | - | {chance:.4f} | - |",
          f"| sampling-noise floor | - | {noise:.4f} | - |", ""]

    L += ["Reproduction check (the flag is OFF for the registered rows, so these are also"
          " the check that adding the flag left the existing path bit-identical):", "",
          "| quantity | this run | registered | delta |", "|---|---|---|---|",
          f"| field, best scale | {b_reg[0]:.4f} | {REG_FIELD:.4f} |"
          f" {b_reg[0] - REG_FIELD:+.4f} |",
          f"| gap threshold, best scale | {b_gap[0]:.4f} | {REG_GAP:.4f} |"
          f" {b_gap[0] - REG_GAP:+.4f} |",
          f"| chance (train mean) | {chance:.4f} | 0.3202 | {chance - 0.3202:+.4f} |", ""]

    improvement = REG_FIELD_BRIEF - b_hor[0]
    credited = b_hor[0] <= REG_FIELD_BRIEF - CREDIT_MARGIN
    still_ruled = b_hor[0] > REG_GAP + RULED_MARGIN
    L += ["## 2 The pre-stated decision", "",
          f"* Horizon-gated field: **{b_hor[0]:.4f}** ({b_hor[1]} scale), against the"
          f" registered field's {REG_FIELD_BRIEF:.4f} (the brief's value; this run"
          f" reproduces {b_reg[0]:.4f}).",
          f"* Improvement from the registered field: **{improvement:+.4f}** against the"
          f" pre-stated margin of {CREDIT_MARGIN:.2f}.",
          f"* **{'CREDITED' if credited else 'NOT CREDITED'}**: the horizon gate"
          f" {'is' if credited else 'is not'} credited with removing the lane-entry"
          f" gate's share of the loss.",
          f"* Against the gap threshold's {REG_GAP:.4f} + {RULED_MARGIN:.2f}:"
          f" dRMSE = {b_hor[0] - b_gap[0]:+.4f}, so the field"
          f" {'REMAINS RULED AGAINST' if still_ruled else 'is no longer ruled against'}"
          " on this study -- as pre-stated, the counterfactual magnitude is the other"
          " ~56% of the loss and nothing here touches it.",
          f"* Against chance ({chance:.4f}): the horizon-gated field is"
          f" {'better' if b_hor[0] < chance else 'no better'}"
          f" ({b_hor[0] - chance:+.4f}); the registered field was"
          f" {b_reg[0] - chance:+.4f}.", ""]

    # --- 3 within-row orderings ----------------------------------------------------
    L += ["## 3 Within-row orderings at matched TTC_true (descriptive, no decision)", "",
          "Reported as `cutin2_field_vs_gap.py` section 3 reports them. The deficit is a"
          " criticality measure, so a row is ordered LIKE THE DATA when rho is POSITIVE"
          " (more deficit, more intervention); the gap is ordered like the data when rho"
          " is negative (more gap, less intervention).", "",
          "| TTC_true [s] | cells | rho(field registered, P) | rho(field horizon, P) |"
          " rho(gap, P) | rho(a_req, P) |", "|---|---|---|---|---|---|"]
    n_rows = pos_reg = pos_hor = neg_gap = 0
    rho_reg_all, rho_hor_all, rho_gap_all = [], [], []
    for ttc, g in cells.groupby("ttc_true"):
        if len(g) < 4:
            continue
        rf = float(spearmanr(g.deficit_max, g.p).statistic)
        rh = float(spearmanr(g.deficit_horizon, g.p).statistic)
        rg = float(spearmanr(g.distance, g.p).statistic)
        ra = float(spearmanr(g.a_req, g.p).statistic)
        n_rows += 1
        pos_reg += rf > 0
        pos_hor += rh > 0
        neg_gap += rg < 0
        rho_reg_all.append(rf)
        rho_hor_all.append(rh)
        rho_gap_all.append(rg)
        L.append(f"| {ttc:.1f} | {len(g)} | {rf:+.2f} | {rh:+.2f} | {rg:+.2f} |"
                 f" {ra:+.2f} |")
    L += ["",
          f"Rows ordered like the data: field (as registered) **{pos_reg} of {n_rows}**"
          f" (positive rho), field with the fixed horizon **{pos_hor} of {n_rows}**,"
          f" gap {neg_gap} of {n_rows} (negative rho).",
          "",
          f"Mean rank correlation: registered field {np.mean(rho_reg_all):+.2f},"
          f" horizon-gated field {np.mean(rho_hor_all):+.2f},"
          f" gap {np.mean(rho_gap_all):+.2f}.", ""]

    # --- 4 what the gate actually did ----------------------------------------------
    lowg = cells[cells.p_lane_end < 0.9]
    lowg_h = cells[cells.p_lane_end_h < 0.9]
    L += ["## 4 What the substitution did to the gate and the covariate (descriptive)",
          "",
          "| quantity | closure-time gate (registered) | fixed horizon"
          f" T = {T_ENC:.1f} s |", "|---|---|---|",
          f"| CP2-CP5 cells with gate < 0.9 at the shown-window end | {len(lowg)} |"
          f" {len(lowg_h)} |",
          f"| mean gate at the shown-window end | {cells.p_lane_end.mean():.3f} |"
          f" {cells.p_lane_end_h.mean():.3f} |",
          f"| median field covariate | {cells.deficit_max.median():.0f} |"
          f" {cells.deficit_horizon.median():.0f} |",
          f"| model-free Spearman(covariate, P) | "
          f"{float(spearmanr(cells.deficit_max, cells.p).statistic):+.3f} |"
          f" {float(spearmanr(cells.deficit_horizon, cells.p).statistic):+.3f} |", ""]

    L += ["Median covariate by clip point and starting TTC, the horizon-gated field"
          " (compare the same table for the registered field in"
          " `cutin2_lane_gate_diagnostic.md` section 2):", "",
          "| clip point | " + " | ".join(f"TTC {int(t)}"
                                         for t in sorted(cells.ttc_start.unique())) + " |",
          "|---" * (1 + cells.ttc_start.nunique()) + "|"]
    for cp in sorted(cells.cp.unique()):
        row = [f"| {cp} "]
        for t in sorted(cells.ttc_start.unique()):
            g = cells[(cells.cp == cp) & (cells.ttc_start == t)]
            row.append(f"| {g.deficit_horizon.median():.0f} " if len(g) else "| - ")
        L.append("".join(row) + "|")
    L.append("")

    # --- 5 CP1 pre-onset floor (no decision) ---------------------------------------
    cp1 = cells_all[cells_all.cp == "CP1"].reset_index(drop=True)
    L += ["## 5 CP1 pre-onset floor (no decision)", "",
          "The colleague's fixed-horizon gate was adopted because it produced the right"
          " pre-onset floor in their data. CP1 is the pre-encroachment baseline here,"
          f" where the observed P(intervene) is {cp1.p.min():.3f}-{cp1.p.max():.3f}.", "",
          f"{len(cp1)} CP1 cells. Registered field covariate"
          f" {cp1.deficit_max.min():.1f}-{cp1.deficit_max.max():.1f}"
          f" (rho with P {float(spearmanr(cp1.deficit_max, cp1.p).statistic):+.3f});"
          f" horizon-gated {cp1.deficit_horizon.min():.1f}-{cp1.deficit_horizon.max():.1f}"
          f" (rho {float(spearmanr(cp1.deficit_horizon, cp1.p).statistic):+.3f});"
          f" mean gate at the CP1 window end {cp1.p_lane_end.mean():.3f} ->"
          f" {cp1.p_lane_end_h.mean():.3f}.", "",
          "Note the ~1 000-unit ego-speed jitter floor documented in section 5 of the"
          " registered report sits under every CP1 covariate; it is not removed here,"
          " because the primary comparison above is the registered one and smoothing is"
          " a separate, already-reported sensitivity.", ""]

    cells_all[["video", "cp", "ttc_start", "ttc_true", "distance", "dv_kph", "lcd", "p",
               "n", "deficit_max", "deficit_horizon", "p_lane_end", "p_lane_end_h",
               "p_lane_max_h"]].to_csv(OUT / "cutin2_horizon_cells.csv", index=False)
    (OUT / "cutin2_field_horizon_gate.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
