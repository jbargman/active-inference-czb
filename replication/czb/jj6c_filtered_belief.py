"""
Card JJ.6c -- the intention as a filtered changepoint: evidence accumulated over the track, and a
gate that is prospective.

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22,
after cards JJ.6 and JJ.6b were seen.

WHY. JJ.6: a binary belief (one 0.3 s window against the jitter floor) reproduces card G.1's gate
where it is closed and not where it grades. JJ.6b: the same window against the predictor's own
keeping model grades in the right order (rho +0.882 with G.1's gate) but is too slow -- the 4 s
lane changes are gated at 0.30 where G.1 says 0.94 and participants respond -- so the lapse
absorbs their responses and the pre-onset score collapses (0.3232). One window of rate evidence
is less than the human uses; G.1's gate reads the lateral POSITION, which is the evidence
accumulated since the onset. The principled construction is a filter over the whole track, and
it settles the awkward one-sided clip of `update_intention` at the same time:

  * the intention is a two-state changepoint: a keeping vehicle starts a change at each window
    with hazard h, and a change is absorbing within a clip (`rollout.belief.filter_intention`);
  * the likelihoods are card JJ.1's, with the keeping spread the predictor's own (JJ.6b), and the
    ratio is two-sided: evidence for keeping may lower the belief, and the hazard keeps it from
    vanishing, which is what the clip was for;
  * **the gate is prospective**: P(changing now, or starting to within the horizon T) =
    p_now + (1 - p_now)(1 - (1 - h)^(T / window)) (`prospective_change`). The design note's p0 was
    "the belief before any lateral motion" and G.1's pre-onset gate is 0.063 to 0.070; here that
    is not a prior but the hazard's consequence over 3 s: h is fixed by p0 = 0.07 and T = 3 s
    (`hazard_for`, h = 0.00723 per 0.3 s window). **No new constant enters.**
  Property checks: `tests/test_looming_pref.py` section 4 (six checks).

WHAT IS COMPUTED. Card JJ.6, imported, with `beliefs` replaced: for each cell the other's lateral
rate over non-overlapping 0.3 s windows from the clip's start to the freeze
(`lateral_rate_track`), filtered with sd_keep = sqrt(SD_VLAT^2 + floor^2) = 0.330 m/s and the
hazard above; the fan is then drawn with b.p_change = the prospective gate at T = 3 s (so the
fan's changers are the share the filter believes will be in the lane within 3 s), and
`p_in_lane(T)` read off it as in JJ.6. Reported beside it: the prospective gate ITSELF as the gate
column (no fan), at T in {1, 2, 3, 4, 6} s, which is the same quantity without the fan's
geometry and the cheaper thing to carry forward if it scores the same.

THE RULES. Card JJ.6's, verbatim, on the fan reading at T = 3 s: (a) within 0.01 of 0.1027; (b)
pre-onset below 0.05; DERIVED / DERIVED AT ANOTHER HORIZON / NOT DERIVED. Rule 0: the pre-onset
prospective gate is within 0.005 of p0 in every cell (it should be, by construction; if it is not,
the track has lateral motion before the onset and the card says so).

PREDICTIONS. Hand arithmetic (the filter on synthetic tracks, in the property tests): a quiet
track gives 0.070; one window at -0.77 m/s gives 0.12, two 0.34, three 0.77; at -1.5 m/s one
window gives 0.99. The post-onset cells sit 0.3 to 1.2 s after the onset (CP2 to CP5 are 0.3 s
apart), so the 4 s lane changes (rate about -0.77) will be gated 0.12 -> 0.34 -> 0.77 -> 0.95 across
CP2 to CP5 where G.1's gate runs about 0.55 -> 1.0, and the 2 s and 3 s changes will be near 1
from CP2. So: (b) holds (pre-onset gate = p0 exactly, as JJ.6's 0.0354); (a) lands between JJ.6's
0.1130 and G.1's 0.1023 -- I predict 0.106 to 0.112, and call it a coin toss against the 0.1127
bar. Rank correlation with G.1's post-onset gate above +0.8. If (a) fails, the residual is the
CP2 cells of the slow lane changes, where G.1's projection of the POSITION (the vehicle has
already moved about 0.2 m) opens the gate before one window of rate can; a filter that also reads
the lateral position (the belief's y_rel against the lane edge) would be the next construction,
and it is the one G.1's gate actually is.

Output: replication/czb/out/jj6c_filtered_belief.md, out/jj6c_filtered_belief_cells.csv
Run:    python replication/czb/jj6c_filtered_belief.py
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
import jj6b_consistent_belief as J6B       # noqa: E402  (SD_KEEP)
from rollout.belief import (FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, filter_intention,  # noqa: E402
                            hazard_for, lateral_rate_track, prospective_change)
from rollout.looming_pref import p_in_lane  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
WINDOW = FLOORS_STUDY2.window_s
HAZARD = hazard_for(P_CHANGE_PRIOR, J6.T_PRIMARY, WINDOW)


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    x = J6.looming_axis(cells)
    lat = J6.CG.lateral_states(cells.video)
    g1 = np.asarray(J6.CG.gate(J6.G1_M_LAT, np.log(J6.G1_S_L), lat.l0.to_numpy(float),
                               lat.ldot.to_numpy(float)), float)
    scenes = HS.study2_scenes(cells)
    rows = []
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        scene = J2.scene_of(scenes[key], key)
        track, sign = lateral_rate_track(scene, e_t, FLOORS_STUDY2)
        p_now = filter_intention(track, J6B.SD_KEEP, HAZARD, sign=sign)
        b = belief_at(scene, e_t, FLOORS_STUDY2, with_intention=False)
        b.p_change = prospective_change(p_now, HAZARD, J6.T_PRIMARY, WINDOW)
        ego = ego_rollout(b, "continue", HORIZON_S, DT_S)
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=0, keep_body_in_lane=True)
        row = {"video": v, "cp": cp, "n_windows": len(track), "vy_last": track[-1],
               "p_now": p_now}
        for h in J6.HORIZONS:
            row[f"gp_{h:g}"] = prospective_change(p_now, HAZARD, h, WINDOW)
            row[f"gc_{h:g}"] = p_in_lane(b, ego, fut, h)
        rows.append(row)
    d = pd.DataFrame(rows).merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance",
                                        "dv_kph", "lcd"]], on="video")
    d["x_looming"] = x
    d["gate_g1"] = g1
    d.to_csv(OUT / "jj6c_filtered_belief_cells.csv", index=False)
    is_cp1 = (d.cp == "CP1").to_numpy()
    rule0 = bool(np.all(np.abs(d["gp_3"][is_cp1] - P_CHANGE_PRIOR) <= 0.005))

    res = {(tag, h): J6.score_gated(d, x, d[f"g{tag}_{h:g}"].to_numpy(float))
           for tag in ("c", "p") for h in J6.HORIZONS}

    def ok(s):
        return s["post"] <= J6.G1_GATED + J6.MARGIN_A, s["cp1"] < J6.CP1_CRIT

    a3, b3 = ok(res[("c", J6.T_PRIMARY)])
    other = [h for h in J6.HORIZONS if h != J6.T_PRIMARY and all(ok(res[("c", h)]))]
    verdict = ("DERIVED" if a3 and b3 else
               "DERIVED AT ANOTHER HORIZON (" + ", ".join(f"{h:g} s" for h in other) + ")" if other
               else "NOT DERIVED")
    post = d[~is_cp1]
    L = ["# Card JJ.6c -- the intention as a filtered changepoint, and a prospective gate", "",
         "Generated by `replication/czb/jj6c_filtered_belief.py`; the construction, the rules and"
         " the predictions were pre-stated in its docstring before the run. Do not edit by hand.",
         "",
         f"A two-state changepoint filter over the other's lateral-rate track (windows of {WINDOW}"
         f" s from the clip's start), keeping spread {J6B.SD_KEEP:.3f} m/s (the predictor's own),"
         f" hazard {HAZARD:.5f} per window fixed by p0 = {P_CHANGE_PRIOR} within"
         f" {J6.T_PRIMARY:g} s; the gate is P(changing now, or within T). No new constant.", "",
         "## 0 Rule 0 and the posterior", "",
         f"Pre-onset prospective gate within 0.005 of p0 in every cell: **{'PASS' if rule0 else 'FAIL'}**"
         f" (mean {d['gp_3'][is_cp1].mean():.4f}). Windows filtered per cell: {d.n_windows.min()} to"
         f" {d.n_windows.max()}.", "",
         "| LCD [s] | CP | cells | median rate, last window [m/s] | median P(now) | median"
         " prospective gate, 3 s | median fan gate, 3 s | median G.1 gate |",
         "|---|---|---|---|---|---|---|---|"]
    for (lcd, cp), g in post.groupby(["lcd", "cp"]):
        L.append(f"| {lcd:g} | {cp} | {len(g)} | {g.vy_last.median():+.3f} | {g.p_now.median():.3f}"
                 f" | {g['gp_3'].median():.3f} | {g['gc_3'].median():.3f} | {g.gate_g1.median():.3f} |")
    L += ["", f"Rank correlation with G.1's gate over the 288 post-onset cells: prospective"
          f" {spearmanr(post['gp_3'], post.gate_g1).statistic:+.3f}, fan"
          f" {spearmanr(post['gc_3'], post.gate_g1).statistic:+.3f}.", "",
          "## 1 The scores", "",
          "| gate on the looming axis | post-onset held out | pre-onset, out of sample | median"
          " level [rad/s] |", "|---|---|---|---|",
          "| card G.1's fitted gate (JJ.6's refit) | 0.1023 | 0.0318 | 0.0301 |",
          "| the binary belief (JJ.6) | 0.1130 | 0.0354 | 0.0336 |",
          "| the one-window consistent belief (JJ.6b) | 0.1779 | 0.3232 | 0.0506 |"]
    for tag, lab in (("c", "the filtered belief through the fan"),
                     ("p", "the prospective gate itself, no fan")):
        for h in J6.HORIZONS:
            s = res[(tag, h)]
            mark = " **(primary)**" if (tag == "c" and h == J6.T_PRIMARY) else ""
            L.append(f"| {lab}, T = {h:g} s{mark} | {s['post']:.4f} | {s['cp1']:.4f} |"
                     f" {s['level']:.4f} |")
    L += ["", "## 2 The verdict on the pre-stated rules", "",
          f"**{verdict}.** At T = {J6.T_PRIMARY:g} s: rule (a) {res[('c', J6.T_PRIMARY)]['post']:.4f}"
          f" ({'holds' if a3 else 'fails'}; the bar {J6.G1_GATED + J6.MARGIN_A:.4f}), rule (b)"
          f" {res[('c', J6.T_PRIMARY)]['cp1']:.4f} ({'holds' if b3 else 'fails'}).", "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj6c_filtered_belief.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
