"""
Card JJ.6d -- sensitivity of the filtered belief gate to the keeping model's spread. A SWEEP, not
a selection: no value is chosen by its score, every value is reported, and the card's product is
the shape of the curve.

THE PRE-REGISTRATION. Written before the run, on 2026-09-22, after JJ.6, JJ.6b and JJ.6c.

WHY. JJ.6c's filtered belief orders the post-onset cells almost exactly as card G.1's gate does
(rho +0.969) but opens too slowly: at CP2 of the 4 s lane changes it believes 0.09 where G.1's
gate is 0.76. Between JJ.6 (keeping spread = the simulator's jitter floor, 0.004 m/s: binary,
0.1130 / 0.0354) and JJ.6c (the predictor's 0.33 m/s: 0.1908 / 0.3473) lies one quantity, "how
much a lane-keeping vehicle wobbles laterally", which is the ONE parameter G.1's two (m_lat, s_l)
would reduce to under this reading, with p0 fixing the hazard. This card maps the scores over
that quantity so that the next decision -- fit it, or reject the reading -- is made on the curve.

WHAT IS COMPUTED. Card JJ.6c's construction, imported, with sd_keep in {0.004, 0.02, 0.05, 0.1,
0.15, 0.2, 0.33} m/s; the prospective gate itself at T = 3 s (JJ.6c showed the fan adds nothing
to it: 0.1908 through the fan against 0.1869 without), scored as in JJ.6 on the looming axis.
Hazard as JJ.6c (p0 = 0.07 within 3 s). Reported per value: post-onset held out, pre-onset, rank
correlation with G.1's gate, and the median gate at CP2 of the 4 s changes (the cells that
decide it).

THE RULE. None on the values. The card reports whether ANY value passes JJ.6's (a) and (b)
together; if one does, the reading "the gate is a filtered intention belief with one wobble
parameter" is VIABLE and a nested-fit card follows; if none does, the reading is NOT VIABLE on
this design and the report says which rule fails at the best value.

PREDICTION. The post-onset score falls from 0.19 at 0.33 toward 0.113 as sd_keep shrinks and the
gate becomes binary, and the pre-onset score improves in the same direction; I expect a shallow
minimum between 0.02 and 0.1 m/s, around 0.105 to 0.112, with pre-onset below 0.05 there. So:
probably viable, by a small margin, and a fitted sd_keep would be about 0.05 m/s -- which is a
physically sensible wobble for a car holding its lane on a motorway (a few centimetres over a
0.3 s window) and much smaller than the predictor's 0.33, whose motivation was G.1's gate
SPREAD over 3 s, a different quantity. If viable, the predictor's SD_VLAT and the belief's
sd_keep should be the same number and both should be this one (query JJ6D.Q1).

Output: replication/czb/out/jj6d_keeping_spread.md, out/jj6d_keeping_spread.csv
Run:    python replication/czb/jj6d_keeping_spread.py
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
import jj6_belief_gate as J6               # noqa: E402
import jj6c_filtered_belief as J6C         # noqa: E402
from rollout.belief import FLOORS_STUDY2, filter_intention, lateral_rate_track, prospective_change  # noqa: E402

OUT = HERE / "out"
SD_KEEP_SWEEP = (0.004, 0.02, 0.05, 0.1, 0.15, 0.2, 0.33)


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    x = J6.looming_axis(cells)
    lat = J6.CG.lateral_states(cells.video)
    g1 = np.asarray(J6.CG.gate(J6.G1_M_LAT, np.log(J6.G1_S_L), lat.l0.to_numpy(float),
                               lat.ldot.to_numpy(float)), float)
    scenes = HS.study2_scenes(cells)
    tracks = {}
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        tracks[v] = lateral_rate_track(J2.scene_of(scenes[key], key), e_t, FLOORS_STUDY2)
    base = cells[["video", "cp", "p", "n", "ttc_start", "ttc_true", "distance", "lcd"]].copy()
    base["gate_g1"] = g1
    is_cp1 = (base.cp == "CP1").to_numpy()
    slow_cp2 = ((base.lcd == 4.0) & (base.cp == "CP2")).to_numpy()

    rows = []
    for sd in SD_KEEP_SWEEP:
        d = base.copy()
        d["gate"] = [prospective_change(filter_intention(tr, sd, J6C.HAZARD, sign=sg), J6C.HAZARD,
                                        J6.T_PRIMARY, J6C.WINDOW) for tr, sg in tracks.values()]
        s = J6.score_gated(d, x, d.gate.to_numpy(float))
        post = d[~is_cp1]
        rows.append({"sd_keep": sd, "post": s["post"], "cp1": s["cp1"], "level": s["level"],
                     "rho_g1": float(spearmanr(post.gate, post.gate_g1).statistic),
                     "gate_slow_cp2": float(d.gate[slow_cp2].median()),
                     "gate_pre": float(d.gate[is_cp1].mean()),
                     "pass_a": s["post"] <= J6.G1_GATED + J6.MARGIN_A, "pass_b": s["cp1"] < J6.CP1_CRIT})
        print(f"sd_keep {sd}: {s['post']:.4f} / {s['cp1']:.4f}", flush=True)
    sw = pd.DataFrame(rows)
    sw.to_csv(OUT / "jj6d_keeping_spread.csv", index=False)
    viable = sw[sw.pass_a & sw.pass_b]
    best = sw.loc[sw.post.idxmin()]

    L = ["# Card JJ.6d -- the filtered belief gate against the keeping model's spread (a sweep)", "",
         "Generated by `replication/czb/jj6d_keeping_spread.py`; a sensitivity sweep pre-stated in"
         " its docstring; no value is chosen by its score. Do not edit by hand.", "",
         "Card JJ.6c's changepoint filter with the prospective gate at 3 s, the hazard fixed by p0,"
         " and the keeping likelihood's spread swept. G.1's gate at CP2 of the 4 s lane changes"
         f" (the deciding cells) has median {base.gate_g1[slow_cp2].median():.3f}.", "",
         "| sd_keep [m/s] | post-onset held out | pre-onset | rho with G.1's gate | median gate,"
         " 4 s changes at CP2 | mean gate, pre-onset | (a) | (b) |", "|---|---|---|---|---|---|---|---|"]
    for _, r in sw.iterrows():
        L.append(f"| {r.sd_keep:g} | {r.post:.4f} | {r.cp1:.4f} | {r.rho_g1:+.3f} |"
                 f" {r.gate_slow_cp2:.3f} | {r.gate_pre:.3f} | {'yes' if r.pass_a else 'no'} |"
                 f" {'yes' if r.pass_b else 'no'} |")
    L += ["", f"Comparators: card G.1's gate 0.1023 / 0.0318 (JJ.6's refit); the bar for (a) is"
          f" {J6.G1_GATED + J6.MARGIN_A:.4f}, for (b) {J6.CP1_CRIT}.", "",
          "## The reading", "",
          (f"**VIABLE.** Values passing both rules: "
           + ", ".join(f"{v:g}" for v in viable.sd_keep) + " m/s. The gate reduces to one"
           " interpretable parameter, the lateral wobble of a lane-keeping vehicle, plus the"
           " hazard that p0 fixes; a nested-fit card (JJ.6e) is the next step, and the"
           " predictor's SD_VLAT should then be the same number (query JJ6D.Q1)."
           if len(viable) else
           f"**NOT VIABLE on this design.** The best value, sd_keep = {best.sd_keep:g} m/s, scores"
           f" {best.post:.4f} / {best.cp1:.4f}; rule {'(a)' if not best.pass_a else '(b)'} fails"
           " there. The filtered belief orders the cells as G.1's gate does at every spread but"
           " cannot open as early as the participants do on one window of evidence."), "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj6d_keeping_spread.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
