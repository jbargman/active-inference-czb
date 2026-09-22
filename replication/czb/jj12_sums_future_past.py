"""
Card JJ.12 -- sums over the future and sums over the past: why a steeper cost near contact does
not rescue the horizon sum, and whether a Farewell-style accumulator of looming over the PAST
orders the cells.

THE PRE-REGISTRATION. Written before the run, on 2026-09-23.

WHERE THE CARD COMES FROM. Jonas, 2026-09-23: *"why not use inv tau (or inv TTC) here, should
that not flip it so that we get more the closer, in the way that e.g. the farewell-to-reaction-
time paper does? As we are talking exponential, the shorter clip reduction will be dwarfed by the
exponential increase of inv tau, or?"*

THE ARITHMETIC, written before any number. The design holds the closing speed dv constant over a
clip, so gap(t) = g_now - dv t. The decisive comparison in these data is WITHIN A MATCHED-TTC ROW
(same TTC, different gap, hence different dv = gap / TTC); the participants respond more to the
nearer, slower-closing car (card R.2's review; JJ.2's rule (c)). Closed forms for a sum to
contact, with contact at the released box g_min = 1.15 L (L the ego length, 4.2 m):
  sum of tau^-1        = ln(g_now / g_min)                    grows with the starting gap
  sum of (tau^-1)^2    = dv (1/g_min - 1/g_now)               ~ dv / g_min: proportional to dv
  sum of theta_dot     = W (1/g_min - 1/g_now)                ~ W / g_min: nearly constant
  sum of theta_dot^2   = W^2 dv/3 (g_min^-3 - g_now^-3)       ~ dv: proportional to dv
Inverse tau itself is 1/TTC, one number per row, so no function of it alone can order a row; and
the steeper the cost, the more the sum is dominated by its value at contact, which scales with
dv, which within a row is BACKWARDS (the nearer car closes slower). The blow-up near contact does
dwarf the step-count effect; what it leaves is a closing-speed axis.
A sum over the PAST is a different object (Markkula et al. 2016, "A farewell to brake reaction
times?": looming accumulated from the onset to a bound). From a start gap g_s to now,
  accumulated theta_dot  = W (1/g_now - 1/g_s),
and within a row 1/g_now = 1/(dv TTC) is larger for the nearer car: ordered the human way.

WHAT IS COMPUTED, per cell of the second cut-in study (`out/cutin2_cells.csv`; W from each cell's
own trace via `cutin2_looming.widths_for`, dv from `dv_kph`, g_now = `distance`, L = 4.2 m):
  FUTURE (analytic, to contact)    F1 sum tau^-1, F2 sum (tau^-1)^2, F3 sum theta_dot, F4 sum theta_dot^2
  PAST (analytic, constant closing)
    P1 from the clip start: g_s = g_now + dv (E - S), the shown window, 10 s in every cell;
    P2 from the lane-change onset: g_s = g_now + dv (k - 1) 0.3 s for CP k (CP1 is the onset, so
       P2 = 0 there: a STEP gate by construction, said in advance);
    P3 = P1 with the fitted level subtracted, W (1/g_now - 1/g_s) - theta_0 (E - S), theta_0 =
       0.0336 rad/s (`out/cutin2_looming.md`; a fitted constant, so P3 is a sensitivity, not a
       candidate), floored at 0.
  JJ.5's empirical sum over the fan (`out/jj5_looming_preference_cells.csv`, eps_in_path) is
  reported beside F1 to F4 for reference.
Each is scored as an axis (log, the zero rule of `rollout.boundary.axis`) with the registered
three-parameter threshold model, sign +1 and -1, on the registered cells, folds and metric; the
matched-TTC rows; rho with the share and with the gap; pre-onset out of sample.

THE RULE. Card JJ.2's, on P1 at sign +1 (the accumulator as an axis): (a) within 0.01 of the
gated looming rule's 0.1027, (b) pre-onset below 0.05 with no gate term, (c) at least 12 of 24
rows (card RE.2's criterion, as JJ.5). Verdict: ADOPT / AXIS (a, not b) / NOT CREDITED. The
future sums have no rule; they are the answer to the question and are read against the arithmetic.

PREDICTIONS. F1: rho(gap) positive, 0 to 3 of 24 rows, score 0.25 to 0.32. F2 and F4: rows 0 of
24 (proportional to dv), score near chance. F3: nearly constant across cells (W / g_min), score
near chance, rows near 12 of 24 by noise. P1: ordered the human way in most rows (18 or more of
24), post-onset 0.11 to 0.14 (it is a monotone-ish transform of the looming rate on this design;
whether it beats the instantaneous looming rate's 0.1130 I cannot say), pre-onset fails (about
0.48: no gate). P2: pre-onset passes by construction (all zero, predicted at the lapse), post-onset
0.13 to 0.18 (the elapsed time since onset adds variation the response does not follow). So I
expect AXIS at best for P1, and the honest statement that on this design the past accumulator
and the instantaneous looming threshold cannot be separated, because closing is constant and the
accumulated looming is a fixed function of the current looming and the gap.

Output: replication/czb/out/jj12_sums_future_past.md, out/jj12_sums_future_past_cells.csv
Run:    python replication/czb/jj12_sums_future_past.py
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
import cutin2_looming as CL                # noqa: E402
import jj2_rollout_cutin as J2             # noqa: E402
from rollout.boundary import axis          # noqa: E402

OUT = HERE / "out"
L_EGO, G_MIN = 4.2, 1.15 * 4.2
THETA_0 = 0.0336        # out/cutin2_looming.md, the full-sample fitted level (a sensitivity only)
CP_STEP = 0.3
G1_GATED, CP1_CRIT, ROWS_CRIT = 0.1027, 0.05, 12


def score(d, col):
    raw = d[col].to_numpy(float)
    if np.all(raw <= 0):
        return None
    dd = d.assign(x=axis(raw).values)
    post = dd[dd.cp != "CP1"].reset_index(drop=True)
    cp1 = dd[dd.cp == "CP1"].reset_index(drop=True)
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    y, w, f = post.p.to_numpy(float), post.n.to_numpy(float), post.ttc_start.to_numpy(float)
    x = post.x.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for k in np.unique(f):
        th = R.fit(x[f != k], y[f != k], w[f != k], -1.0)
        pred[f == k] = R.predict(th, x[f == k], -1.0)
    agree, nrows, _ = J2.matched_rows(post, post[col].to_numpy(float), +1.0)
    return {"post": r_post, "neg": R.wrmse(y, pred, w), "cp1": r_cp1, "rows": agree, "n": nrows,
            "rho_p": float(spearmanr(post[col], post.p).statistic),
            "rho_gap": float(spearmanr(post[col], post.distance).statistic),
            "zeros": int((post[col] <= 0).sum())}


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    W, _ = CL.widths_for(cells)
    d = cells[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph"]].copy()
    dv = d.dv_kph.to_numpy(float) / 3.6
    g = d.distance.to_numpy(float)
    shown = np.array([R._f(R.VIDEO_RE.match(v)["e"]) - R._f(R.VIDEO_RE.match(v)["s"])
                      for v in d.video])
    k = d.cp.str[2:].astype(int).to_numpy()
    d["W"], d["shown_s"] = W, shown
    d["theta_dot"] = W * dv / (g ** 2 + W ** 2 / 4)
    gm = np.minimum(g, G_MIN * 1.0001)             # cells already at contact: no future
    d["F1_sum_invtau"] = np.log(np.maximum(g, G_MIN) / G_MIN)
    d["F2_sum_invtau2"] = dv * (1 / G_MIN - 1 / np.maximum(g, G_MIN))
    d["F3_sum_theta"] = W * (1 / G_MIN - 1 / np.maximum(g, G_MIN))
    d["F4_sum_theta2"] = W ** 2 * dv / 3 * (G_MIN ** -3 - np.maximum(g, G_MIN) ** -3)
    g_clip = g + dv * shown
    g_onset = g + dv * (k - 1) * CP_STEP
    d["P1_past_clip"] = W * (1 / g - 1 / g_clip)
    d["P2_past_onset"] = W * (1 / g - 1 / g_onset)
    d["P3_past_clip_excess"] = np.maximum(W * (1 / g - 1 / g_clip) - THETA_0 * shown, 0.0)
    j5 = pd.read_csv(OUT / "jj5_looming_preference_cells.csv")[["video", "eps_in_path"]]
    d = d.merge(j5, on="video", how="left")
    d.to_csv(OUT / "jj12_sums_future_past_cells.csv", index=False)

    cols = [("F1 sum of tau^-1 to contact", "F1_sum_invtau"),
            ("F2 sum of (tau^-1)^2 to contact", "F2_sum_invtau2"),
            ("F3 sum of theta_dot to contact", "F3_sum_theta"),
            ("F4 sum of theta_dot^2 to contact", "F4_sum_theta2"),
            ("card JJ.5's empirical sum over the fan (reference)", "eps_in_path"),
            ("**P1 looming accumulated over the shown clip (10 s)**", "P1_past_clip"),
            ("P2 looming accumulated since the lane-change onset", "P2_past_onset"),
            ("P3 = P1 with the fitted level subtracted (sensitivity)", "P3_past_clip_excess"),
            ("the instantaneous looming rate (card EL.1b, reference)", "theta_dot")]
    res = {c: score(d, c) for _, c in cols}
    p1 = res["P1_past_clip"]
    a, b, c_ = p1["post"] <= G1_GATED + 0.01, p1["cp1"] < CP1_CRIT, p1["rows"] >= ROWS_CRIT
    verdict = "ADOPT" if a and b else ("AXIS" if a else "NOT CREDITED")
    L = ["# Card JJ.12 -- sums over the future and sums over the past", "",
         "Generated by `replication/czb/jj12_sums_future_past.py`; the arithmetic, the quantities,"
         " the rule and the predictions were pre-stated in its docstring before the run. Do not"
         " edit by hand.", "",
         "Within a matched-TTC row inverse tau is one number, so nothing built on it alone can"
         " order the row; a sum to contact of any cost that grows near contact is dominated by its"
         " value at contact, which scales with the closing speed dv, and within a row the nearer"
         " car closes slower. A sum over the PAST is a different object and is scored here too.",
         "", "| quantity | post-onset held out, +1 | sign -1 | pre-onset | matched-TTC rows |"
         " rho(share) | rho(gap) | zero cells |", "|---|---|---|---|---|---|---|---|"]
    for lab, c in cols:
        s = res[c]
        L.append(f"| {lab} | " + ("every cell at zero |" * 1 + " - | - | - | - | - | - |" if s is None else
                 f"{s['post']:.4f} | {s['neg']:.4f} | {s['cp1']:.4f} | {s['rows']} of {s['n']} |"
                 f" {s['rho_p']:+.3f} | {s['rho_gap']:+.3f} | {s['zeros']} |"))
    L += ["", "Comparators: gated looming rule 0.1027 / 0.0319, ungated 0.1130 / 0.4832, gap"
          " 0.1522, TTC 0.1679, chance 0.320.", "",
          "## The verdict on P1 (the accumulator as an axis)", "",
          f"**{verdict}.** Rule (a) {p1['post']:.4f} ({'holds' if a else 'fails'}), rule (b)"
          f" {p1['cp1']:.4f} ({'holds' if b else 'fails'}), rule (c) {p1['rows']} of {p1['n']}"
          f" ({'holds' if c_ else 'fails'}).", "",
          "## Reading", "",
          f"The four future sums: F1 rho(gap) {res['F1_sum_invtau']['rho_gap']:+.3f}, F2"
          f" {res['F2_sum_invtau2']['rho_gap']:+.3f}, F3 {res['F3_sum_theta']['rho_gap']:+.3f}, F4"
          f" {res['F4_sum_theta2']['rho_gap']:+.3f}; matched-TTC rows {res['F1_sum_invtau']['rows']},"
          f" {res['F2_sum_invtau2']['rows']}, {res['F3_sum_theta']['rows']},"
          f" {res['F4_sum_theta2']['rows']} of 24. The past accumulator P1: rows"
          f" {p1['rows']} of 24, rho(gap) {p1['rho_gap']:+.3f}.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj12_sums_future_past.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
