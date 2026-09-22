"""
Card JJ.6b -- the intention update made consistent with the predictor's own model of "keeping".

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22,
after card JJ.6's result was seen.

WHY. Card JJ.6 found the belief gate is BINARY on these cells -- 0.085 in every pre-onset cell and
1.000 in every post-onset cell at every horizon -- so it reproduces card G.1's gate where that gate
is closed (pre-onset 0.0354 against 0.0318) but not where G.1's gate GRADES (post-onset 0.55 to
1.0), and it missed rule (a) by 0.0003 for that reason. The binary posterior has one cause in the
code: `rollout.belief.update_intention` scores the "keeping" hypothesis with the MEASUREMENT
jitter floor of the lateral rate (sd 0.004 m/s on the second study), while the predictor
(`rollout.predictor.sample_futures`) lets a keeping vehicle drift laterally at SD_VLAT = 0.33 m/s.
The belief update and the generative model disagree about what keeping looks like, and any lateral
rate above the floor -- the slowest post-onset rate is 0.48 m/s -- is therefore certain evidence of
a change. Made consistent, the keeping likelihood is N(vy | 0, sqrt(SD_VLAT^2 + floor^2)), the
same drift the fan draws from. This is a consistency correction, not a tuned constant: SD_VLAT is
card JJ.1's own (motivated from G.1's gate spread as a rate) and appears in no new place.

WHAT IS COMPUTED. Card JJ.6, imported and unchanged, with `beliefs` replaced by one that calls
`update_intention` with sd_keep = sqrt(SD_VLAT^2 + FLOORS_STUDY2.sd_v_lat^2) = 0.330 m/s; the
"changing" likelihood stays N(vy | -1.2, 0.4) as in JJ.1; the one-sided clip stays. Everything
else is JJ.6's: the corrected fan, seed 0, n = 200, the looming axis, the fixed-gate fitter, the
horizons, the rules, the comparators.

THE RULES. Card JJ.6's, verbatim: (a) within 0.01 of 0.1027 at T = 3 s; (b) pre-onset below 0.05;
verdict DERIVED / DERIVED AT ANOTHER HORIZON / NOT DERIVED. Rule 0: the pre-onset posterior must
stay at the prior (the clip guarantees it; checked).

PREDICTIONS. Hand arithmetic on the likelihood ratio at the post-onset rates: at vy = -0.48 m/s
the ratio is below 1 and the clip returns the prior (0.07); at -0.88 the posterior is about 0.6;
at -1.05 about 0.9; above -1.2 about 1. So the belief gate grades across the post-onset cells from
0.07 to 1.0, wider than G.1's 0.55 to 1.0, and the slow early cut-ins (CP2 at the longest lane
change) are gated nearly shut where participants already respond at 0.3 to 0.8. I expect (a) to
FAIL, and by more than 0.0003 -- 0.115 to 0.13 -- because a consistent belief is too slow to
open on a 0.3 s window of evidence, and (b) to hold. If that is what happens, the reading is that
the human gate opens on LESS evidence than a consistent Bayesian update of this generative model
allows, which points at the likelihood's window (0.3 s) or at a lateral POSITION channel, which
G.1's gate has (l0) and the intention update does not. Rank correlation of the graded gate with
G.1's post-onset gate: positive, 0.4 to 0.8.

Output: replication/czb/out/jj6b_consistent_belief.md, out/jj6b_consistent_belief_cells.csv
Run:    python replication/czb/jj6b_consistent_belief.py
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

import hs1_situational_surprise as HS      # noqa: E402
import jj2_rollout_cutin as J2             # noqa: E402
import jj6_belief_gate as J6               # noqa: E402  card JJ.6 (read only)
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, update_intention  # noqa: E402
from rollout.looming_pref import p_in_lane  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
SD_KEEP = float(np.hypot(SD_VLAT, FLOORS_STUDY2.sd_v_lat))


def beliefs_consistent(cells):
    scenes = HS.study2_scenes(cells)
    out = {}
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        b = belief_at(J2.scene_of(scenes[key], key), e_t, FLOORS_STUDY2,
                      p_change_prior=P_CHANGE_PRIOR, with_intention=False)
        b.p_change = update_intention(P_CHANGE_PRIOR, b.vy_oth, SD_KEEP,
                                      sign=float(np.sign(b.y_rel)) or 1.0)
        out[v] = (b, cp, b.vy_oth)
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    x = J6.looming_axis(cells)
    lat = J6.CG.lateral_states(cells.video)
    g1 = np.asarray(J6.CG.gate(J6.G1_M_LAT, np.log(J6.G1_S_L), lat.l0.to_numpy(float),
                               lat.ldot.to_numpy(float)), float)
    bel = beliefs_consistent(cells)
    rows = []
    for v, (b, cp, vy) in bel.items():
        ego = ego_rollout(b, "continue", HORIZON_S, DT_S)
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=0, keep_body_in_lane=True)
        row = {"video": v, "cp": cp, "vy_oth": vy, "p_change": b.p_change}
        for h in J6.HORIZONS:
            row[f"gc_{h:g}"] = p_in_lane(b, ego, fut, h)
        rows.append(row)
    d = pd.DataFrame(rows).merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance",
                                        "dv_kph", "lcd"]], on="video")
    d["x_looming"] = x
    d["gate_g1"] = g1
    d.to_csv(OUT / "jj6b_consistent_belief_cells.csv", index=False)
    is_cp1 = (d.cp == "CP1").to_numpy()
    rule0 = bool(np.allclose(d.p_change[is_cp1], P_CHANGE_PRIOR, atol=1e-6))

    res = {h: J6.score_gated(d, x, d[f"gc_{h:g}"].to_numpy(float)) for h in J6.HORIZONS}

    def ok(s):
        return s["post"] <= J6.G1_GATED + J6.MARGIN_A, s["cp1"] < J6.CP1_CRIT

    a3, b3 = ok(res[J6.T_PRIMARY])
    other = [h for h in J6.HORIZONS if h != J6.T_PRIMARY and all(ok(res[h]))]
    verdict = ("DERIVED" if a3 and b3 else
               "DERIVED AT ANOTHER HORIZON (" + ", ".join(f"{h:g} s" for h in other) + ")" if other
               else "NOT DERIVED")
    post = d[~is_cp1]
    L = ["# Card JJ.6b -- the intention update consistent with the predictor's model of keeping",
         "",
         "Generated by `replication/czb/jj6b_consistent_belief.py`; the change, the rules and the"
         " predictions were pre-stated in its docstring before the run. Do not edit by hand.", "",
         f"The keeping likelihood's spread is {SD_KEEP:.3f} m/s (the predictor's SD_VLAT"
         f" {SD_VLAT} combined with the jitter floor {FLOORS_STUDY2.sd_v_lat}) instead of the"
         " floor alone. Nothing else differs from card JJ.6.", "",
         "## 0 Rule 0 and the posterior", "",
         f"Pre-onset posterior at the prior in every cell: **{'PASS' if rule0 else 'FAIL'}**."
         f" Post-onset posterior: mean {post.p_change.mean():.3f}, range"
         f" {post.p_change.min():.3f} to {post.p_change.max():.3f}; by the study's lane-change"
         " duration (LCD, s), the median posterior and the median lateral rate:", "",
         "| LCD [s] | cells | median lateral rate [m/s] | median posterior | median belief gate,"
         " 3 s | median G.1 gate |", "|---|---|---|---|---|---|"]
    for lcd, g in post.groupby("lcd"):
        L.append(f"| {lcd:g} | {len(g)} | {g.vy_oth.median():+.3f} | {g.p_change.median():.3f} |"
                 f" {g['gc_3'].median():.3f} | {g.gate_g1.median():.3f} |")
    rho = spearmanr(post["gc_3"], post.gate_g1).statistic
    L += ["", f"Rank correlation of the belief gate (3 s) with G.1's gate over the 288 post-onset"
          f" cells: **{rho:+.3f}**.", "",
          "## 1 The scores", "",
          "| gate on the looming axis | post-onset held out | pre-onset, out of sample | median"
          " level [rad/s] |", "|---|---|---|---|",
          f"| card G.1's fitted gate (JJ.6's refit) | 0.1023 | 0.0318 | 0.0301 |",
          "| the binary belief (card JJ.6, any T) | 0.1130 | 0.0354 | 0.0336 |"]
    for h in J6.HORIZONS:
        s = res[h]
        mark = " **(primary)**" if h == J6.T_PRIMARY else ""
        L.append(f"| the consistent belief, T = {h:g} s{mark} | {s['post']:.4f} | {s['cp1']:.4f} |"
                 f" {s['level']:.4f} |")
    L += ["", "## 2 The verdict on the pre-stated rules", "",
          f"**{verdict}.** At T = {J6.T_PRIMARY:g} s: rule (a) {res[J6.T_PRIMARY]['post']:.4f}"
          f" ({'holds' if a3 else 'fails'}), rule (b) {res[J6.T_PRIMARY]['cp1']:.4f}"
          f" ({'holds' if b3 else 'fails'}).", "", f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj6b_consistent_belief.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
