"""
Card P.1 -- the released planner on the second cut-in study, corrected: the ego on the road, the
coasting pedal state, and the whole plan examined.

THE PRE-REGISTRATION. Written before the run, on 2026-09-22. Jonas, decision 7: "Rerun."

WHY. Card JJ.2b's planner pass (and RE.1 part C, and RE.4's two planner-side functionals) had
three defects found by the review of 2026-09-22 (`docs/review_2026-09-22.md` section 2): (i) the
agent was given the ego's world lateral position (about 6 m) against a lane centre of 0, so the
ego was off the road in every cell and the lateral term added about 450 000 nats; (ii)
`agent.a_applied = 0.0` while the coasting policy is -0.1 m/s^2, so the released pedal constraint
clamped the first step of every plan to -0.1; (iii) the brake test read that first step only. The
claims "the released planner steers in 378 of 378 cells and never brakes" and "Delta G from the
planner orders 19 of 24 matched-TTC rows" are therefore untested. This card tests them.

WHAT IS COMPUTED. JJ.2b's `planner_pass`, imported, with three wraps and no edit of JJ.2b: (i)
`staging` returns its preference with `lane_centre` = the ego's recorded lateral position at the
freeze (as card RE.4b did); (ii) `a_applied` = `AgentParams.a_coast` -- this is done by
monkey-patching the agent class so that the attribute set in `planner_pass` is overridden at
`_cem` time; (iii) `brakes` is recomputed from the whole plan returned by `_cem`, which is
captured by wrapping `_cem`: a plan BRAKES if any step is below a_coast - 0.5 m/s^2 (JJ.2b's own
margin, applied to every step) and STEERS if max |omega| > 0.05 rad/s (JJ.2b's criterion). Three
planner seeds (0, 1, 2); the primary is seed 0 and rule (e) is the spread across seeds.

Scored as JJ.2b: Delta G = G(continue) - min over the planner's plans, on the registered cells,
folds and metric, sign +1 and -1; the matched-TTC rows; rho with the share and the gap. And the
counts: steers, brakes, both, neither, per seed.

THE RULES. Card JJ.2's, on Delta G at sign +1: (a) within 0.01 of 0.1027, (b) pre-onset below
0.05, (c) 24 of 24 rows; verdict ADOPT / COMPARATOR / DROP. Rule (e): the post-onset score
within 0.01 across the three seeds, else NOT STABLE. The counts have no rule; they replace the
untested claims and are reported as what the corrected planner does.

PREDICTIONS. DROP (0.30 to 0.32), as every rollout quantity. The counts: the planner brakes in a
majority of the post-onset cells within its horizon (a reviewer's rerun of four cells found 3.8
to 7.0 m/s^2) and steers in many of them as well; "never brakes" is false. Pre-onset: mostly
neither. Run time: hours (the CEM planner over 378 cells, three seeds); background with a log,
the report written after each seed so a partial result survives an interruption.

Output: replication/czb/out/p1_planner_corrected.md, out/p1_planner_corrected_cells.csv
Run:    python replication/czb/p1_planner_corrected.py
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

import hs1_situational_surprise as HS      # noqa: E402
import jj2b_steer_menu as J2B              # noqa: E402  card JJ.2b (read only)
from aidriver.agent import ActiveInferenceDriver, AgentParams  # noqa: E402

OUT = HERE / "out"
SEEDS = (0, 1, 2)
_lane = {"centre": 0.0}
_plans: list = []
_belief_at, _staging, _cem = J2B.belief_at, J2B.staging, ActiveInferenceDriver._cem


def belief_at_recording(scene, t0, *a, **kw):
    i0 = int(np.clip(np.searchsorted(scene.t, t0, side="right") - 1, 0, len(scene.t) - 1))
    _lane["centre"] = float(scene.ego_y[i0])
    return _belief_at(scene, t0, *a, **kw)


def staging_on_the_road(v):
    return replace(_staging(v), lane_centre=_lane["centre"])


def cem_coasting(self, ego, other_traj, w):
    self.a_applied = float(self.p.a_coast)          # the pedal state the ego actually holds
    best_a, best_G = _cem(self, ego, other_traj, w)
    _plans.append(np.array(best_a, float))
    return best_a, best_G


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    J2B.belief_at = belief_at_recording
    J2B.staging = staging_on_the_road
    ActiveInferenceDriver._cem = cem_coasting
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = HS.study2_scenes(cells)
    frames, res = {}, {}
    for seed in SEEDS:
        J2B.SEED = seed
        _plans.clear()
        df = J2B.planner_pass(cells, scenes)
        a_coast = AgentParams().a_coast
        df["brakes_any_step"] = [bool((p[:, 0] < a_coast - 0.5).any()) for p in _plans]
        df["a_min"] = [float(p[:, 0].min()) for p in _plans]
        df["t_first_brake"] = [float(np.argmax(p[:, 0] < a_coast - 0.5) * 0.2)
                               if (p[:, 0] < a_coast - 0.5).any() else np.nan for p in _plans]
        df["seed"] = seed
        frames[seed] = df
        res[seed] = J2B.score(df, cells, "dg")
        pd.concat(frames.values()).to_csv(OUT / "p1_planner_corrected_cells.csv", index=False)
        write_report(cells, frames, res, t0)
        print(f"seed {seed} done: {res[seed]['post']:.4f} [{time.time() - t0:.0f} s]", flush=True)


def write_report(cells, frames, res, t0):
    prim = res[0]
    posts = [r["post"] for r in res.values()]
    stable = (max(posts) - min(posts) <= 0.01) if len(posts) == len(SEEDS) else None
    a = prim["post"] <= 0.1027 + 0.01
    b = prim["cp1"] < 0.05
    verdict = ("NOT STABLE" if stable is False else "ADOPT" if a and b else "COMPARATOR" if a else "DROP")
    L = ["# Card P.1 -- the released planner on the second cut-in study, corrected", "",
         "Generated by `replication/czb/p1_planner_corrected.py`; the corrections, the rule and"
         " the predictions were pre-stated in its docstring before the run. Do not edit by hand.",
         "", f"Seeds completed: {len(res)} of {len(SEEDS)}.", "",
         "## 1 Delta G from the corrected planner", "",
         "| seed | post-onset held out, sign +1 | pre-onset | matched-TTC rows | rho(share) |"
         " rho(gap) |", "|---|---|---|---|---|---|"]
    for s, r in res.items():
        L.append(f"| {s} | {r['post']:.4f} | {r['cp1']:.4f} | {r['rows']} | {r['rho_p']:+.3f} |"
                 f" {r['rho_gap']:+.3f} |")
    L += ["", "Card JJ.2b's uncorrected planner row, for the record: 0.3161 / 0.5538 / 19 of 24 /"
          " +0.169 / -0.308.", "", "## 2 What the corrected planner does", "",
          "| seed | cells | steers | brakes within the horizon | both | neither | median first"
          " brake [s] | median min acceleration [m/s^2] |", "|---|---|---|---|---|---|---|---|"]
    for s, df in frames.items():
        for lab, m in (("pre-onset", df.cp == "CP1"), ("post-onset", df.cp != "CP1")):
            sub = df[m]
            st, br = sub.steers.to_numpy(bool), sub.brakes_any_step.to_numpy(bool)
            L.append(f"| {s}, {lab} | {len(sub)} | {int(st.sum())} | {int(br.sum())} |"
                     f" {int((st & br).sum())} | {int((~st & ~br).sum())} |"
                     f" {np.nanmedian(sub.t_first_brake) if br.any() else float('nan'):.1f} |"
                     f" {sub.a_min.median():.2f} |")
    L += ["", "## 3 The verdict on the pre-stated rules (seed 0)", "",
          f"**{verdict}.** Rule (a) {prim['post']:.4f} ({'holds' if a else 'fails'}), rule (b)"
          f" {prim['cp1']:.4f} ({'holds' if b else 'fails'}), rule (c) {prim['rows']}, rule (e)"
          f" {'holds' if stable else 'fails' if stable is False else 'pending'}.", "",
          f"Run time so far {time.time() - t0:.0f} s.", ""]
    (OUT / "p1_planner_corrected.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
