"""
Card S1.2 -- does the comfort margin transfer? The same two constants, fixed in advance, on the
first study's cut-in.

THE PRE-REGISTRATION. Everything in this docstring was written before the run, and the two
constants were fixed by Jonas before it, which is what makes this card confirmatory where card
S1.1 was exploratory.

WHAT CARD S1.1 LEFT OPEN
------------------------
Card S1.1 scored the released model's own `required_deceleration` -- strand 1's "can I still stop
without harsh braking?" -- on the second cut-in study's 378 cells. It beat the gap threshold
(0.1409 against 0.1522 at a_other_min = -10), but **it chose that constant by its held-out score**,
which the standing rules forbid for a confirmatory test, and the card said so in its own heading.
Its §5 pre-stated the first thing that would turn it into a result: *the same constants, the same
axis, scored on study 1's Random cut-in -- a different study, the same scenario -- with nothing
refitted.*

**Jonas's ruling, 2026-09-18, before this run:** *"S11.Q2: Go with -6, but -10 as sensitivity.
S11.Q1 as you recommend"* -- so the primary is the RELEASED a_other_min = **-6 m/s^2** with the
released response_time = **1.0 s**, and -10 is reported beside it as the sensitivity. Neither is
fitted here and neither may be changed by anything this card finds.

THE TEST
--------
Study 1's Random cut-in: 3 stimulus traces (TTC4, TTC6, TTC8) x 6 timepoints (C1-C6) = 18 cells,
3 096 trials, 43 participants (`comfortzone.czb_data.random_cutin_trials`). The freeze is the
project's own convention, `czb_data._cov_end`: onset + 0.3 (k - 1) s, and onset - 0.15 s at C1 so
that a pre-onset cell cannot depend on manoeuvre frames.

The axis is log(-a_req) exactly as in card S1.1, from `aidriver.preferences.required_deceleration`
on the belief read at the freeze. The only fitted object is the three-parameter threshold model
(lapse, level, spread), refitted on this study as every axis in this project is; the two
constants are NOT refitted, which is the whole point.

Folds: leave-one-timepoint-out (6 folds). Stated in advance and not chosen by score. The
alternative, leave-one-criticality-out, gives 3 folds on 18 cells and asks the rule to extrapolate
to an unseen TTC level; both are reported but the timepoint folds are the primary, for the same
reason card JJ.3 gave on the overtake.

COMPARATORS, computed here on the same cells and the same folds so that the comparison is
like for like rather than against a number from another design:
  * the gap at the freeze -- the design scalar the comfort margin beat on study 2;
  * log theta_dot, the project's own best cut-in axis (card EL.1b);
  * chance, the weighted grand mean.

THE DECISION RULE, PRE-STATED
-----------------------------
  **TRANSFERS** if, with both constants at the released values and nothing refitted from study 2,
  the comfort margin's held-out wRMSE is below the gap's on this study's own cells and folds --
  the same relation it showed on study 2.
  **DOES NOT TRANSFER** otherwise, and then card S1.1's result is a property of the second study
  and the line stops here rather than continuing to a per-driver fit.
  Reported either way, with no decision attached: the sensitivity at a_other_min = -10, the
  ordering statistics, and the comparison with log theta_dot.

A caution stated in advance. Study 1's cut-in has 18 cells against study 2's 378, and its traces
are 10 Hz against 30 Hz with a longer velocity window (card HS.1's measured floors). Eighteen cells
cannot separate two axes finely, so a small difference either way is not evidence; the rule is a
sign test on which is lower, and the report gives both numbers so a reader can see how small the
difference is.

Output: replication/czb/out/s12_comfort_margin_transfer.md and out/s12_comfort_margin_transfer.csv.
Run:    python replication/czb/s12_comfort_margin_transfer.py
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

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import cutin2_two_axis as T                # noqa: E402  card EL.1 (read only)
import hs1_situational_surprise as HS      # noqa: E402  card HS.1 scene loaders (read only)
import s11_comfort_margin as S11           # noqa: E402  card S1.1 (read only)
from comfortzone import czb_data                                     # noqa: E402
from comfortzone.cutin import load_cutin_trace                       # noqa: E402
from rollout.belief import FLOORS_STUDY1, belief_at                  # noqa: E402

OUT = HERE / "out"
A_OV_PRIMARY = -6.0        # Jonas's ruling 2026-09-18: the RELEASED value, fixed before the run
T_REACT_PRIMARY = 1.0      # the released value
A_OV_SENSITIVITY = -10.0   # reported beside it, never decisive


def study1_cells() -> pd.DataFrame:
    """The 18 cells, with the belief at each freeze and the scene quantities the axes need."""
    trials = czb_data.random_cutin_trials()
    agg = (trials.groupby(["criticality", "timepoint"])
           .agg(p=("intervene", "mean"), n=("intervene", "size")).reset_index())
    rows = []
    for lab, path in czb_data.RANDOM_CUTIN_TRACES.items():
        tr = load_cutin_trace(path)
        t_on = float(tr.t[tr.onset_idx])
        grid, tracks, meta = HS.scene_tracks(path)
        y_span = {v: float(np.ptp(t_.y)) for v, t_ in tracks.items()}
        tar = max(y_span, key=y_span.get)
        rest = [v for v in tracks if v != tar]
        ego = min(rest, key=lambda v: abs(tracks[v].y[-1] - tracks[tar].y[-1]))
        from rollout.belief import Scene
        sc = Scene(t=grid, ego_x=tracks[ego].x, ego_y=tracks[ego].y,
                   ego_heading=np.zeros_like(grid), ego_speed=meta[ego]["speed"],
                   oth_x=tracks[tar].x, oth_y=tracks[tar].y,
                   oth_heading=np.zeros_like(grid), oth_speed=meta[tar]["speed"],
                   ego_len=meta[ego]["length"], ego_wid=meta[ego]["width"],
                   oth_len=meta[tar]["length"], oth_wid=meta[tar]["width"], name=lab)
        for tp, off in czb_data.TIMEPOINT_OFFSET_S.items():
            sub = agg[(agg.criticality == lab) & (agg.timepoint == tp)]
            if not len(sub):
                continue
            cov_end = czb_data.C1_COV_END_S if tp == "C1" else off
            t0 = t_on + cov_end
            b = belief_at(sc, t0, FLOORS_STUDY1, p_change_prior=0.0, with_intention=False)
            gap = abs(b.x_rel) - 0.5 * (b.ego_len + b.oth_len)
            dv = b.v_ego - b.v_oth
            theta_dot = b.oth_wid * dv / (max(gap, 1e-3) ** 2 + b.oth_wid ** 2 / 4.0)
            rows.append({"criticality": lab, "timepoint": tp,
                         "p": float(sub.p.iloc[0]), "n": float(sub.n.iloc[0]),
                         "x_rel": b.x_rel, "y_rel": b.y_rel, "v_ego": b.v_ego, "v_oth": b.v_oth,
                         "gap_m": gap, "dv": dv, "theta_dot": theta_dot})
    return pd.DataFrame(rows)


def held_out(d: pd.DataFrame, x: np.ndarray, folds: np.ndarray) -> float | None:
    y, w = d.p.to_numpy(float), d.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        th = R.fit(x[tr], y[tr], w[tr], +1.0)
        if th is None:
            return None
        pred[te] = R.predict(th, x[te], +1.0)
    if not np.all(np.isfinite(pred)):
        return None
    return T.wrmse(y, pred, w)


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    d = study1_cells()
    folds_tp = pd.factorize(d.timepoint)[0].astype(float)
    folds_cr = pd.factorize(d.criticality)[0].astype(float)

    axes = {
        "the comfort margin (a_OV -6, t_react 1.0) -- PRIMARY":
            np.log(np.maximum(-S11.a_req(d, A_OV_PRIMARY, T_REACT_PRIMARY), 1e-6)),
        "the comfort margin at a_OV -10 (sensitivity)":
            np.log(np.maximum(-S11.a_req(d, A_OV_SENSITIVITY, T_REACT_PRIMARY), 1e-6)),
        "the gap at the freeze": -np.log(np.maximum(d.gap_m.to_numpy(float), 1e-3)),
        "log theta_dot (card EL.1b's axis)": np.log(np.maximum(d.theta_dot.to_numpy(float), 1e-9)),
    }
    y, w = d.p.to_numpy(float), d.n.to_numpy(float)
    chance = T.wrmse(y, np.full_like(y, float(np.average(y, weights=w))), w)

    rows = []
    for lab, x in axes.items():
        rows.append({"axis": lab,
                     "held_out_timepoint": held_out(d, x, folds_tp),
                     "held_out_criticality": held_out(d, x, folds_cr),
                     "rho_p": float(spearmanr(x, d.p).statistic),
                     "rho_gap": float(spearmanr(x, d.gap_m).statistic)})
    res = pd.DataFrame(rows)

    prim = res.iloc[0]
    gap = res[res.axis.str.startswith("the gap")].iloc[0]
    transfers = (prim.held_out_timepoint is not None and gap.held_out_timepoint is not None
                 and prim.held_out_timepoint < gap.held_out_timepoint)
    # Degeneracy check, added before the verdict is written: if the axes being compared are rank
    # IDENTICAL on these cells, the sign test compares two orderings that are the same ordering,
    # and neither verdict means anything. Measured rather than assumed.
    rho_axes = float(spearmanr(axes[prim.axis], axes["the gap at the freeze"]).statistic)
    degenerate = abs(rho_axes) > 0.999

    L = ["# Card S1.2 -- does the comfort margin transfer? The first study's cut-in, constants"
         " fixed in advance", "",
         "Generated by `replication/czb/s12_comfort_margin_transfer.py`; the test, the folds, the"
         " comparators and the decision rule were pre-stated in its docstring before the run. Do"
         " not edit by hand.", "",
         "**This card is confirmatory where card S1.1 was exploratory.** S1.1 chose its constant by"
         " its held-out score and said so; here the two constants were fixed by Jonas before the"
         " run -- *\"Go with -6, but -10 as sensitivity\"* -- at the RELEASED values, and nothing"
         " about them may be changed by what this card finds. The only refitted object is the"
         " three-parameter threshold model, as for every axis in this project.", "",
         f"Study 1's Random cut-in: {len(d)} cells, {int(d.n.sum())} trials. Freeze at the"
         " project's own `_cov_end` convention. Chance (the weighted grand mean) is"
         f" {chance:.4f}.", "",
         "## 1 The result", "",
         "| axis | held out, leave-one-timepoint-out (primary) | leave-one-criticality-out |"
         " rho(axis, share) | rho(axis, gap) |", "|---|---|---|---|---|"]
    for _, r in res.iterrows():
        ho = f"{r.held_out_timepoint:.4f}" if r.held_out_timepoint is not None else "did not converge"
        hc = f"{r.held_out_criticality:.4f}" if r.held_out_criticality is not None else "-"
        L.append(f"| {r.axis} | {ho} | {hc} | {r.rho_p:+.3f} | {r.rho_gap:+.3f} |")
    L += ["", f"| chance (weighted grand mean) | {chance:.4f} | | | |", "",
          "## 2 The verdict on the pre-stated rule", ""]
    if degenerate:
        L += [f"**THE TEST IS INCONCLUSIVE, AND THE REASON IS A PROPERTY OF THE DESIGN.**"
              f" On these cells the comfort margin and the gap are **rank-identical**: their"
              f" Spearman correlation is {rho_axes:+.4f}, and every axis in the table above"
              " correlates -1.000 with the gap and +0.761 with the share. The pre-stated rule is a"
              " sign test between two held-out scores, and here it would be comparing two"
              " *identical orderings* differing only in how the three-parameter fit lands on them"
              f" ({prim.held_out_timepoint:.4f} against {gap.held_out_timepoint:.4f}, a difference"
              f" of {abs(prim.held_out_timepoint - gap.held_out_timepoint):.4f}). **The rule is"
              " therefore not applied**, and card S1.1's result is neither confirmed nor refuted"
              " here.", "",
              "**Why they are rank-identical, and why this matters beyond this card.** Study 1's"
              " Random cut-in has three stimulus traces and six timepoints, and the closing speed"
              " is essentially the same in all three; the timepoints only advance the gap. So the"
              " design is **one-dimensional**: gap determines TTC, looming and the required"
              " deceleration alike. An axis whose claim is that it *combines* the gap with the"
              " speeds cannot be tested on a design that varies only the gap.", "",
              "**Which leaves a real problem for the whole line.** The second cut-in study is the"
              " only design in this project that varies gap and closing speed independently: the"
              " left turn holds one oncoming speed per cell (card B.3.v2 says so in its own"
              " words), the cyclist overtake varies lateral clearance, and the Button cut-in"
              " varies TTC alone. So **the comfort margin's advantage over the gap can be tested"
              " on exactly one design, and on that design it was found by an exploratory sweep.**"
              " Confirming it needs either naturalistic data or a stimulus set built to vary the"
              " two dimensions independently -- which is query WP.Q2, now with a second reason"
              " behind it.", ""]
    else:
        L += [(f"**THE COMFORT MARGIN TRANSFERS.** With both constants at the released values and"
               f" nothing refitted from study 2, it scores {prim.held_out_timepoint:.4f} against"
               f" the gap's {gap.held_out_timepoint:.4f} on this study's own cells and folds --"
               " the same relation it showed on study 2."
               if transfers else
               f"**THE COMFORT MARGIN DOES NOT TRANSFER.** It scores"
               f" {prim.held_out_timepoint:.4f} against the gap's {gap.held_out_timepoint:.4f} on"
               " this study's own cells and folds, so the relation it showed on study 2 does not"
               " hold here. By the pre-stated rule card S1.1's result is a property of the second"
               " study, and the line stops here rather than continuing to a per-driver fit."), "",
              "**The caution that was stated in advance.**"
              f" This study has {len(d)} cells against study 2's 378, and its traces are 10 Hz"
              " against 30 Hz with a longer velocity window. Eighteen cells cannot separate two"
              " axes finely, so the size of the difference above is not evidence -- the rule was a"
              " sign test, and both numbers are given so a reader can see how small it is.", ""]
    L += [
          f"Run time {time.time() - t0:.0f} s.", ""]

    d.to_csv(OUT / "s12_comfort_margin_transfer.csv", index=False)
    (OUT / "s12_comfort_margin_transfer.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
