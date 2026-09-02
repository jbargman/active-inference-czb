"""Card EL.2/gate: does an anticipatory lateral "binding" gate let the EL.1 rule predict
the pre-onset (CP1) cells of the second cut-in study?

THE PRE-REGISTRATION. Everything in this docstring was written before the run.

The question
------------
Card EL.1 (`cutin2_two_axis.py` -> `out/cutin2_two_axis.md`) found the best criticality
rule on the second cut-in study to be a threshold on the linear two-axis covariate

    x = w * (-log gap) + (1 - w) * (-log TTC),      w ~ 0.5 fitted,

with held-out wRMSE 0.1137 on the 288 POST-ONSET cells (cp != "CP1"), leave-one-starting-
TTC-out folds. That rule was never asked to predict the 90 PRE-ONSET cells (cp == "CP1"),
where the cut-in vehicle is still fully in its own lane and participants almost never
intervene (observed cell means 0.000-0.115, mean 0.024, flat in gap). A pure criticality
threshold has no way to stay flat there: at CP1 the gap is already small in the severe
design cells, so it must predict graded intervention.

A colleague's external model gets those cells right with an anticipatory *binding* gate on
the lateral clearance between the two vehicles:

    w_gate = Phi( (m_lat - (l0 + ldot * t_enc)) / s_l ),

i.e. the gate is open to the extent that the edge-to-edge lateral clearance, extrapolated
t_enc seconds ahead at its current rate, has fallen below m_lat. l0 is the edge-to-edge
clearance at the response moment, ldot its rate of change (negative when closing), and
t_enc = 3.0 s is FIXED (not identifiable from this design). The response model is a
mixture: before the intruder binds, the longitudinal situation does not matter.

    P = b + (1 - b) * w_gate * Phi( (x - c) / sigma )

Their fit predicted the CP1 cells out of sample at wRMSE ~0.03, with w_gate ~0.003 at CP1
and 0.66-1.00 post-onset.

Data, states, fit, folds, metric
--------------------------------
* Cells: `out/cutin2_cells.csv` (378 videos, written by the registered
  `cutin2_field_vs_gap.py`). Post-onset = the 288 cells with cp != "CP1"; CP1 = 90 cells.
* Lateral states, per video, from the study's own kinematic traces via
  `comfortzone.cutin.load_cutin_trace`, the same loader and the same trace-file mapping
  (`cutin2_field_vs_gap.VIDEO_RE`, `.KIN`) the registered scripts use:
      centre-to-centre lateral separation  lat(t) = |y_tar(t)|
      edge-to-edge clearance               l0     = lat(e_t) - (tar_wid + ego_wid) / 2
      closing rate                         ldot   = (l0(e_t) - l0(e_t - 0.3)) / 0.3
  with e_t the clip end time (the response moment) from `out/cutin2_cells.csv` / the video
  filename stamp, in trace time.
* Validation (pre-stated stop rule): the trace-derived centre-to-centre lateral is compared
  per video against the study's own `lateral_dist` column in
  `cut-in_study_aggregate_trials_annotated.csv`. If the MEDIAN absolute difference exceeds
  0.5 m the run STOPS and reports rather than fits.
* Fitter: the registered one. `cutin2_two_axis.fit_reg` for the threshold starts,
  `cutin2_field_vs_gap.predict` for the ungated response, weighted least squares on cell
  means with weights n (participants per cell), multi-start L-BFGS-B.
* Folds: leave-one-starting-TTC-out (`cells.ttc_start`), 6 folds, exactly as EL.1.
* Metric: weighted RMSE of held-out cell predictions against observed cell means.

The two models, both fitted on the 288 post-onset cells ONLY (no CP1 trial enters any fit)
------------------------------------------------------------------------------------------
  (c) the EL.1 linear rule, UNGATED:  P = b + (1 - b) * Phi((x - c)/sigma), x as above,
      w fitted jointly (`cutin2_two_axis.fit_linear`).      [must reproduce 0.1137 held out]
  (k) the GATED rule:  P = b + (1 - b) * w_gate(l0, ldot; m_lat, s_l) * Phi((x - c)/sigma),
      with m_lat in [-1, 3] m and log s_l in [-3, 2] fitted jointly with (w, b, c, sigma),
      t_enc = 3.0 s fixed. Multi-start over m_lat in {0, 0.5, 1.0, 1.5} and s_l in
      {0.3, 1.0}, crossed with the EL.1 weight starts.

Both are then used to predict the 90 CP1 cells OUT OF SAMPLE from the full post-onset fit.

THE DECISION RULE (pre-stated)
------------------------------
(i)   The gate is CREDITED if the gated rule's CP1 out-of-sample wRMSE is below 0.05 AND
      its post-onset held-out wRMSE is within 0.01 of the ungated rule -- it must not cost
      accuracy where the gate is open.
(ii)  If the UNGATED rule already predicts CP1 within 0.05, the gate is UNNECESSARY on this
      data.
(iii) If the gated rule costs more than 0.01 post-onset, the gate as specified INTERFERES
      with the open-gate cells; the fitted m_lat, s_l are reported.
Also reported, no decision attached: the fitted w_gate range on the CP1 cells and on the
post-onset cells (the external analysis: ~0.003 at CP1, 0.66-1.00 post-onset).

ASSUMPTIONS MADE (stated before the run, as instructed, and not revisited after seeing the
numbers)
------------------------------------------------------------------------------------------
1. `CutInTrace.y_tar` is ALREADY ego-relative (`load_cutin_trace` returns
   `tg.Location_Y - e.Location_Y`), so the centre-to-centre lateral separation is |y_tar|,
   not |y_tar - y_ego|. Subtracting the absolute `y_ego` a second time would be a double
   subtraction. The `lateral_dist` validation above is what tests this choice.
2. The ego width is NOT exposed on `CutInTrace` (only `tar_wid`). It is read from the trace
   CSV's `Width_m` column for the ego vehicle, identified as the vehicle whose trimmed
   `Location_Y` series is the one the loader returned as `y_ego` (exact array match, using
   the loader's own `_trim_teardown`). This reproduces the loader's role assignment rather
   than re-deriving it.
3. The response moment is the clip end time e_t, taken at the last trace sample at or
   before e_t (`searchsorted(..., "right") - 1`), matching the registered
   `video_covariates` convention; the 0.3 s backward difference is taken at the last
   sample at or before e_t - 0.3 s (~9 samples at the traces' ~30 Hz).
4. The sign convention inside the gate is the natural one: l_pred = l0 + ldot * t_enc is the
   extrapolated clearance, and the gate opens as l_pred falls below m_lat. With ldot < 0
   (closing) this is the anticipatory term as specified.
5. The lapse b is a free floor shared by both models, fitted on the post-onset cells only;
   no CP1 information (not even its mean) enters any fit.

Run: python replication/czb/cutin2_gate.py
Outputs: out/cutin2_gate.md, out/cutin2_gate_states.csv, out/log_cutin2_gate.txt
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

import cutin2_field_vs_gap as R          # noqa: E402  the registered R.2 script
import cutin2_two_axis as T              # noqa: E402  card EL.1
from comfortzone.cutin import load_cutin_trace, _trim_teardown  # noqa: E402

OUT = HERE / "out"
T_ENC = 3.0                 # s, fixed: not identifiable on this design
LAT_STOP = 0.5              # m, pre-stated stop threshold on the median lateral mismatch


# ---------------------------------------------------------------------------------
# 1. lateral states per video
# ---------------------------------------------------------------------------------

def ego_width(path: Path, tr) -> float:
    """Width_m of the ego vehicle: the vehicle whose trimmed Location_Y is `tr.y_ego`."""
    raw = pd.read_csv(path)
    best, best_d = None, np.inf
    for _, g in raw.groupby("Vehicle_ID"):
        g = _trim_teardown(g)
        y = g.Location_Y.to_numpy()
        if len(y) < len(tr.y_ego):
            continue
        d = float(np.max(np.abs(y[:len(tr.y_ego)] - tr.y_ego)))
        if d < best_d:
            best, best_d = float(g.Width_m.iloc[0]), d
    if best is None or best_d > 1e-9:
        raise RuntimeError(f"{path.name}: could not identify the ego vehicle (d={best_d})")
    return best


def lateral_states(videos) -> pd.DataFrame:
    """l0 [m] and ldot [m/s] at the response moment, one row per video."""
    cache: dict[str, tuple] = {}
    rows = []
    for v in videos:
        m = R.VIDEO_RE.match(v)
        if m is None:
            raise ValueError(f"unparseable video name: {v}")
        key = f"LC_dv{m['dv']}_Tlc{m['tlc']}_TTC{int(m['ttc']):02d}"
        if key not in cache:
            p = R.KIN / f"{key}_vehicle_states.csv"
            tr = load_cutin_trace(p)
            half = (tr.tar_wid + ego_width(p, tr)) / 2.0
            cache[key] = (tr, half)
        tr, half = cache[key]
        e_t = R._f(m["e"])
        lat = np.abs(tr.y_tar)                       # centre-to-centre [m]
        clear = lat - half                           # edge-to-edge [m]
        i = int(np.searchsorted(tr.t, e_t, side="right")) - 1
        j = int(np.searchsorted(tr.t, e_t - 0.3, side="right")) - 1
        rows.append({"video": v, "trace": key, "cp": f"CP{m['cp']}", "e_t": e_t,
                     "lat_center": float(lat[i]), "half_widths": half,
                     "l0": float(clear[i]),
                     "ldot": float((clear[i] - clear[j]) / 0.3)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------
# 2. the two models
# ---------------------------------------------------------------------------------

def axes(cells):
    return T.axes(cells)


def x_linear(a, u, v):
    wt = 1.0 / (1.0 + np.exp(-a))
    return wt * u + (1.0 - wt) * v


def gate(m_lat, log_s, l0, ldot):
    return norm.cdf((m_lat - (l0 + ldot * T_ENC)) / np.exp(log_s))


def predict_gated(p, u, v, l0, ldot):
    """p = [a, b, c, log sigma, m_lat, log s_l]."""
    x = x_linear(p[0], u, v)
    b = 1.0 / (1.0 + np.exp(-p[1]))
    core = norm.cdf((x - p[2]) / np.exp(p[3]))
    return b + (1.0 - b) * gate(p[4], p[5], l0, ldot) * core


def fit_gated(u, v, l0, ldot, y, w):
    """Joint weighted least squares, multi-start L-BFGS-B. Starts: the EL.1 weight starts
    (a0) crossed with m_lat in {0, 0.5, 1.0, 1.5} and s_l in {0.3, 1.0}; (b, c, sigma)
    seeded from the registered fitter on the corresponding ungated covariate."""
    bounds = [(-8, 8), (-30, 10), (None, None), (-10, 10), (-1.0, 3.0), (-3.0, 2.0)]

    def obj(p):
        val = float(np.sum(w * (predict_gated(p, u, v, l0, ldot) - y) ** 2))
        return val if np.isfinite(val) else 1e12

    best, best_val = None, np.inf
    for a0 in np.linspace(-3, 3, 7):
        th0 = T.fit_reg(x_linear(a0, u, v), y, w)
        for m0 in (0.0, 0.5, 1.0, 1.5):
            for s0 in (0.3, 1.0):
                p0 = np.array([a0, th0[0], th0[1], th0[2], m0, np.log(s0)])
                r = minimize(obj, p0, method="L-BFGS-B", bounds=bounds)
                if r.fun < best_val:
                    best, best_val = r.x, r.fun
    return best


def held_out_ungated(cells, folds):
    """The EL.1 linear rule on the registered folds (same code path as EL.1)."""
    return T.held_out(cells, folds, "linear")


def held_out_gated(cells, folds):
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    l0 = cells.l0.to_numpy(float)
    ldot = cells.ldot.to_numpy(float)
    pred = np.full_like(y, np.nan)
    params = []
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        u, v = axes(cells[tr])
        p = fit_gated(u, v, l0[tr], ldot[tr], y[tr], w[tr])
        u2, v2 = axes(cells[te])
        pred[te] = predict_gated(p, u2, v2, l0[te], ldot[te])
        params.append(p)
    return pred, params


def wrmse(y, pred, w):
    return float(np.sqrt(np.average((pred - y) ** 2, weights=w)))


# ---------------------------------------------------------------------------------
# 3. the run
# ---------------------------------------------------------------------------------

def main() -> None:
    cells_all = pd.read_csv(OUT / "cutin2_cells.csv")
    st = lateral_states(cells_all.video)
    st.to_csv(OUT / "cutin2_gate_states.csv", index=False,
              columns=["video", "l0", "ldot", "trace", "cp", "e_t", "lat_center",
                       "half_widths"])

    # --- pre-stated validation / stop rule -------------------------------------
    ann = pd.read_csv(R.TRIALS, low_memory=False)
    ann = ann[~ann.video.str.contains("dummy")]
    lat_ann = ann.groupby("video").lateral_dist.first()
    st["lat_annotated"] = st.video.map(lat_ann)
    err = (st.lat_center - st.lat_annotated).abs()
    med, mx = float(err.median()), float(err.max())

    L = ["# Card EL.2/gate -- an anticipatory lateral binding gate on the EL.1 rule", "",
         "Generated by `replication/czb/cutin2_gate.py`; models, folds, metric, decision"
         " rule and assumptions pre-stated in its docstring before the run. Do not edit by"
         " hand.", "",
         "## 0 Validation of the trace-derived lateral states", "",
         "Centre-to-centre lateral separation |y_tar| at the response moment e_t, against"
         " the study's own `lateral_dist` column, per video (378 videos).", "",
         "| check | median | max |", "|---|---|---|",
         f"| \\|trace centre-to-centre - annotated `lateral_dist`\\| [m] | {med:.3f} | {mx:.3f} |",
         "",
         f"Pre-stated stop rule: median > {LAT_STOP:.1f} m aborts the run. "
         f"Median {med:.3f} m -> "
         + ("**RUN ABORTED**." if med > LAT_STOP else "proceed."), ""]

    if med > LAT_STOP:
        L += ["", "The lateral states could not be reconciled with the study's own"
                  " annotation, so no fit was attempted."]
        (OUT / "cutin2_gate.md").write_text("\n".join(L), encoding="utf-8")
        print("\n".join(L))
        return

    L += ["Half the summed vehicle widths (the edge-to-edge correction) is "
          f"{st.half_widths.min():.3f}-{st.half_widths.max():.3f} m across the traces.", "",
          "| set | cells | l0 [m] mean (min-max) | ldot [m/s] mean (min-max) |",
          "|---|---|---|---|"]
    for lab, sub in (("CP1 (pre-onset)", st[st.cp == "CP1"]),
                     ("CP2-CP5 (post-onset)", st[st.cp != "CP1"])):
        L.append(f"| {lab} | {len(sub)} | {sub.l0.mean():.3f} "
                 f"({sub.l0.min():.3f} to {sub.l0.max():.3f}) | {sub.ldot.mean():.3f} "
                 f"({sub.ldot.min():.3f} to {sub.ldot.max():.3f}) |")
    L.append("")

    # --- the cells ---------------------------------------------------------------
    cells_all = cells_all.merge(st[["video", "l0", "ldot"]], on="video", how="left")
    if cells_all[["l0", "ldot"]].isna().any().any():
        raise RuntimeError("videos without lateral states")
    post = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    cp1 = cells_all[cells_all.cp == "CP1"].reset_index(drop=True)
    y, w = post.p.to_numpy(float), post.n.to_numpy(float)
    folds = post.ttc_start.to_numpy(float)
    y1, w1 = cp1.p.to_numpy(float), cp1.n.to_numpy(float)
    print(f"post-onset cells {len(post)}, CP1 cells {len(cp1)}")

    # --- held-out on the post-onset cells ---------------------------------------
    pred_c, prm_c = held_out_ungated(post, folds)
    r_c = wrmse(y, pred_c, w)
    print(f"(c) ungated held-out wRMSE {r_c:.4f}")
    pred_k, prm_k = held_out_gated(post, folds)
    r_k = wrmse(y, pred_k, w)
    print(f"(k) gated held-out wRMSE {r_k:.4f}")

    # --- full post-onset fits, then CP1 out of sample ----------------------------
    u, v = axes(post)
    p_lin, _ = T.fit_linear(u, v, y, w)
    wt_c = 1.0 / (1.0 + np.exp(-p_lin[0]))
    u1, v1 = axes(cp1)
    cp1_c = R.predict(p_lin[1:], wt_c * u1 + (1 - wt_c) * v1, +1.0)
    r1_c = wrmse(y1, cp1_c, w1)

    p_g = fit_gated(u, v, post.l0.to_numpy(float), post.ldot.to_numpy(float), y, w)
    cp1_k = predict_gated(p_g, u1, v1, cp1.l0.to_numpy(float), cp1.ldot.to_numpy(float))
    r1_k = wrmse(y1, cp1_k, w1)
    wt_k = 1.0 / (1.0 + np.exp(-p_g[0]))
    b_k = 1.0 / (1.0 + np.exp(-p_g[1]))
    b_c = 1.0 / (1.0 + np.exp(-p_lin[1]))
    m_lat, s_l = float(p_g[4]), float(np.exp(p_g[5]))
    g_cp1 = gate(p_g[4], p_g[5], cp1.l0.to_numpy(float), cp1.ldot.to_numpy(float))
    g_post = gate(p_g[4], p_g[5], post.l0.to_numpy(float), post.ldot.to_numpy(float))
    print(f"CP1 out-of-sample wRMSE: ungated {r1_c:.4f}, gated {r1_k:.4f}")
    print(f"fitted m_lat {m_lat:.4f} m, s_l {s_l:.4f} m, w {wt_k:.4f}, b {b_k:.4f}")
    print(f"w_gate CP1 {g_cp1.min():.4f}-{g_cp1.max():.4f}; "
          f"post {g_post.min():.4f}-{g_post.max():.4f}")

    # --- tables -------------------------------------------------------------------
    L += ["## 1 Post-onset (288 cells): held-out accuracy, leave-one-starting-TTC-out", "",
          "| model | free parameters | held-out wRMSE |", "|---|---|---|",
          f"| (c) EL.1 linear rule, ungated | 4 | {r_c:.4f} |",
          f"| (k) same rule with the binding gate | 6 | {r_k:.4f} |", "",
          f"EL.1 reported 0.1137 for (c); reproduced here as {r_c:.4f} "
          f"(difference {r_c - 0.1137:+.4f}). Cost of the gate where it is open: "
          f"{r_k - r_c:+.4f}.", "",
          "## 2 CP1 (90 pre-onset cells) predicted OUT OF SAMPLE", "",
          "The full post-onset fit of each model, applied to cells no fit has seen.", "",
          "| model | CP1 wRMSE | predicted mean | predicted range | observed mean | observed range |",
          "|---|---|---|---|---|---|",
          f"| (c) ungated | {r1_c:.4f} | {np.average(cp1_c, weights=w1):.3f} | "
          f"{cp1_c.min():.3f}-{cp1_c.max():.3f} | {np.average(y1, weights=w1):.3f} | "
          f"{y1.min():.3f}-{y1.max():.3f} |",
          f"| (k) gated | {r1_k:.4f} | {np.average(cp1_k, weights=w1):.3f} | "
          f"{cp1_k.min():.3f}-{cp1_k.max():.3f} | {np.average(y1, weights=w1):.3f} | "
          f"{y1.min():.3f}-{y1.max():.3f} |", "",
          "## 3 Fitted parameters (full post-onset fits)", "",
          "| parameter | (c) ungated | (k) gated |", "|---|---|---|",
          f"| w (share of -log gap) | {wt_c:.3f} | {wt_k:.3f} |",
          f"| lapse b | {b_c:.4f} | {b_k:.4f} |",
          f"| threshold c | {p_lin[2]:.3f} | {p_g[2]:.3f} |",
          f"| sigma | {np.exp(p_lin[3]):.3f} | {np.exp(p_g[3]):.3f} |",
          f"| m_lat [m] | - | {m_lat:.3f} |",
          f"| s_l [m] | - | {s_l:.3f} |",
          f"| t_enc [s] | - | {T_ENC:.1f} (fixed) |", "",
          "### Fitted gate per training fold", "",
          "| held-out starting TTC | w | m_lat [m] | s_l [m] |", "|---|---|---|---|"]
    for f, p in zip(sorted(np.unique(folds)), prm_k):
        L.append(f"| {f:.0f} s | {1.0 / (1.0 + np.exp(-p[0])):.3f} | {p[4]:.3f} | "
                 f"{np.exp(p[5]):.3f} |")
    L += ["", "## 4 The fitted gate value w_gate", "",
          "| set | min | max | mean |", "|---|---|---|---|",
          f"| CP1 (90 cells) | {g_cp1.min():.4f} | {g_cp1.max():.4f} | {g_cp1.mean():.4f} |",
          f"| post-onset (288 cells) | {g_post.min():.4f} | {g_post.max():.4f} | "
          f"{g_post.mean():.4f} |", "",
          "The external analysis reported ~0.003 at CP1 and 0.66-1.00 post-onset.", ""]

    # --- the pre-stated decision ---------------------------------------------------
    cost = r_k - r_c
    if r1_c < 0.05:
        verdict = ("(ii) the UNGATED rule already predicts the CP1 cells within 0.05 "
                   f"(wRMSE {r1_c:.4f}): the gate is UNNECESSARY on this data")
    elif cost > 0.01:
        verdict = ("(iii) the gated rule costs {:+.4f} post-onset, more than the 0.01 "
                   "margin: the gate AS SPECIFIED INTERFERES with the open-gate cells "
                   "(fitted m_lat = {:.3f} m, s_l = {:.3f} m)".format(cost, m_lat, s_l))
    elif r1_k < 0.05:
        tail = ("an improvement, so it costs nothing where the gate is open"
                if cost < 0 else "within the 0.01 margin")
        verdict = ("(i) the gate is CREDITED: CP1 out-of-sample wRMSE {:.4f} < 0.05 and "
                   "the post-onset held-out cost is {:+.4f} -- {}"
                   .format(r1_k, cost, tail))
    else:
        verdict = ("no branch credits the gate: it does not cost post-onset accuracy "
                   "({:+.4f}) but its CP1 out-of-sample wRMSE {:.4f} is not below 0.05, "
                   "and the ungated rule's is {:.4f}".format(cost, r1_k, r1_c))
    L += ["## 5 Pre-registered decision", "",
          f"Ungated CP1 wRMSE {r1_c:.4f}; gated CP1 wRMSE {r1_k:.4f}; post-onset held-out "
          f"{r_c:.4f} (ungated) vs {r_k:.4f} (gated), cost {cost:+.4f}.", "",
          f"**Decision: {verdict}.**", ""]

    (OUT / "cutin2_gate.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
