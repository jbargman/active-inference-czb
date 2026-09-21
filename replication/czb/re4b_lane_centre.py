"""
Card RE.4b -- card RE.4's three agent-side functionals with the ego ON the road.

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22.

WHY. The review of 2026-09-22 (`out/review_2026_09_22_checks.md` section 4) found that card RE.4
handed the released agent the ego's WORLD lateral position (5.95 to 6.05 m) while the preference's
lane centre stayed at its default of 0 m. The ego was therefore off the road in all 378 cells: the
lateral term alone is 15 000 nats a step, 450 000 over the horizon, and RE.4's epsilon runs 450 018
to 660 185. The same lane centre also places the lane the OTHER vehicle is expected to keep
(`agent.py`, the lane norm), so the belief and the predicted fan were wrong as well as the cost.
Card RE.4's conclusion -- "no functional of the released expected free energy orders these cells"
-- is one of the three legs of the arc's claim that nothing repairs the released model, and on
that construction it was never tested.

WHAT IS COMPUTED. Card RE.4's own `cell_terms` and `score`, imported and unchanged. The one change:
the preference each cell is staged with gets `lane_centre` = the ego's recorded lateral position at
the freeze, so the stimulus ego sits at its lane centre, which is what `rollout.efe` (cards JJ.2,
RE.2, S1.4) has assumed all along. This is done by wrapping the two functions RE.4 calls
(`belief_at`, to read the scene's ego position at the freeze; `J2B.staging`, to apply it), so not
one line of RE.4 is edited.

THREE of RE.4's five functionals are recomputed: epsilon = G(continue), the epistemic term, and the
full G at alpha = 1. The other two (min G and Delta G from the CEM planner) come from card JJ.2b's
committed planner output, which has the same defect; rerunning the planner is a separate, slower
card and is NOT done here (query RE4B.Q1).

THE RULE. RE.4's bar, unchanged: a functional is credited if its post-onset held-out score is below
the gap threshold's 0.1522, fitted with the sign its definition implies (+1: more free energy, more
response). Because the review also found that a fixed sign can turn an anti-ordered axis into a
constant prediction (`out/review_2026_09_22_checks.md` section 2), the score with the sign reversed
is reported beside it; it informs the reading and cannot credit anything.

SANITY CHECK, required before any score is read: the smallest epsilon across cells must be below
10 000 nats (it was 450 018). If it is not, the ego is still off the road and the card stops.

PREDICTION. Epsilon becomes, in effect, card JJ.2's G(continue) computed by the agent's own code:
anti-ordered with the response (JJ.2: rho -0.648), so about 0.32 at sign +1 and about 0.25 at sign
-1. NOT CREDITED. I have no prediction for the epistemic term, whose RE.4 value (rho -0.502) was
measured on a belief built around the wrong lane.

Output: replication/czb/out/re4b_lane_centre.md, out/re4b_lane_centre.csv
Run:    python replication/czb/re4b_lane_centre.py
"""
from __future__ import annotations

import sys
import time
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import hs1_situational_surprise as HS      # noqa: E402
import re4_efe_functionals as RE4          # noqa: E402  card RE.4 (read only)
from rollout.boundary import axis          # noqa: E402

OUT = HERE / "out"
GAP_RULE = 0.1522
EPS_SANITY = 10_000.0
RE4_REPORTED = {"eps": (450_017.8, 660_185.2)}   # out/re4_efe_functionals.csv, min and max

_lane = {"centre": 0.0}
_belief_at, _staging = RE4.belief_at, RE4.J2B.staging


def belief_at_recording(scene, t0, *a, **kw):
    i0 = int(np.clip(np.searchsorted(scene.t, t0, side="right") - 1, 0, len(scene.t) - 1))
    _lane["centre"] = float(scene.ego_y[i0])
    return _belief_at(scene, t0, *a, **kw)


def staging_on_the_road(v_ego):
    return replace(_staging(v_ego), lane_centre=_lane["centre"])


def held_out(post: pd.DataFrame, x: np.ndarray, sign: float) -> float:
    y, w, f = post.p.to_numpy(float), post.n.to_numpy(float), post.ttc_start.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for k in np.unique(f):
        th = R.fit(x[f != k], y[f != k], w[f != k], sign)
        pred[f == k] = R.predict(th, x[f == k], sign)
    return R.wrmse(y, pred, w)


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    RE4.belief_at = belief_at_recording
    RE4.J2B.staging = staging_on_the_road
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    d = RE4.cell_terms(cells, HS.study2_scenes(cells))
    d = d.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
    d.to_csv(OUT / "re4b_lane_centre.csv", index=False)

    sane = bool(d.eps.min() < EPS_SANITY)
    L = ["# Card RE.4b -- card RE.4's agent-side functionals with the ego on the road", "",
         "Generated by `replication/czb/re4b_lane_centre.py`; the change, the rule and the"
         " prediction were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "Card RE.4 gave the released agent the ego's world lateral position (about 6 m) with the"
         " lane centre at its default of 0 m, so the ego was off the road in every cell"
         " (`out/review_2026_09_22_checks.md` section 4). Here each cell's preference is staged"
         " with the lane centre at the ego's own recorded position; nothing else in RE.4's code"
         " path changes.", "",
         "## 0 Sanity check", "",
         f"Epsilon now runs **{d.eps.min():,.1f} to {d.eps.max():,.1f} nats** (card RE.4:"
         f" {RE4_REPORTED['eps'][0]:,.1f} to {RE4_REPORTED['eps'][1]:,.1f}). Required: a minimum"
         f" below {EPS_SANITY:,.0f}. **{'PASS' if sane else 'FAIL -- the card stops here'}.**", ""]
    if not sane:
        (OUT / "re4b_lane_centre.md").write_text("\n".join(L), encoding="utf-8")
        return

    L += ["## 1 The three functionals", "",
          f"Credited below the gap threshold's {GAP_RULE:.4f} at sign +1. The sign -1 column"
          " informs the reading and credits nothing. Comparators: looming 0.1137 ungated, chance"
          " 0.320.", "",
          "| functional | post-onset held out, sign +1 | sign -1 | pre-onset | matched-TTC rows |"
          " rho(share) | rho(gap) | card RE.4's sign +1 score, ego off the road |",
          "|---|---|---|---|---|---|---|---|"]
    old = pd.read_csv(OUT / "re4_efe_functionals.csv")
    labels = [("eps = G(continue), the model's Eq. 13 signal", "eps"),
              ("the epistemic term", "epistemic"),
              ("the full G at alpha = 1", "g_alpha1")]
    credited = []
    for lab, col in labels:
        s = RE4.score(d, col, +1.0)
        dd = d.copy()
        vals = dd[col].to_numpy(float)
        dd["x"] = axis(vals - vals.min() + 1e-9 if vals.min() <= 0 else vals).values
        post = dd[dd.cp != "CP1"].reset_index(drop=True)
        neg = held_out(post, post.x.to_numpy(float), -1.0)
        s_old = RE4.score(old, col, +1.0)
        if s["post"] < GAP_RULE:
            credited.append(lab)
        L.append(f"| {lab} | {s['post']:.4f} | {neg:.4f} | {s['cp1']:.4f} | {s['rows']} |"
                 f" {s['rho_p']:+.3f} | {s['rho_gap']:+.3f} | {s_old['post']:.4f} |")
    L += ["",
          "## 2 The verdict on the pre-stated rule", "",
          ("**CREDITED: " + "; ".join(credited) + ".**" if credited else
           "**NOT CREDITED.** With the ego on the road, none of the three agent-side functionals"
           " reaches the gap threshold. Card RE.4's conclusion now rests on a valid construction"
           " for these three; its two planner-side functionals (min G and Delta G from card"
           " JJ.2b's planner run) remain untested, because that run has the same defect (query"
           " RE4B.Q1)."), "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "re4b_lane_centre.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-12:]))


if __name__ == "__main__":
    main()
