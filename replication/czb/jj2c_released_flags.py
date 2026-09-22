"""
Card JJ.2c -- card JJ.2 with the RELEASED preference flags, and the fit's sign free.

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22.

WHY. Every rollout card of the 09-18 to 09-22 arc staged the preference with two of this
project's own flags, `counterfactual_residual_severity=True` (the ramp form of the braking-margin
term) and `lane_entry_continuous=True` (the lateral weighting of the tau^-1 term), and called the
result "released" (`docs/review_2026-09-22.md` §3). The review's checks (section 1) showed that
the released STEP form of the braking-margin term orders the cells the human way within every
closing speed where the ramp form does not, so what "the released model" does on this design is
not on file. The review also showed (section 2) that fixing the fit's sign at +1 on an
anti-ordered axis returns a constant prediction, so both signs are reported.

WHAT IS COMPUTED. Card JJ.2's own `cell_delta_g` and scoring, imported. Two stagings:
  **released**  `PreferenceParams(v_desired=v_ego)` and nothing else: the released form of every
                term (step braking margin, no lateral weighting of tau^-1).
  **project**   card JJ.2's staging, which must reproduce its 0.3202 (rule 0, within 0.0005).
Both on card JJ.1's fan as built (JJ.2's fan; the corrected fan of S1.6 changed nothing for JJ.2's
arm) at seed 0, n = 200; the same 378 cells, folds and metric.

THE RULES. Card JJ.2's, verbatim, applied to the released staging at sign +1 (more Delta G, more
response, which is what the quantity claims): (a) within 0.01 of the gated looming rule's 0.1027,
(b) pre-onset below 0.05 with no gate term, (c) positive within-row ordering in 24 of 24
matched-TTC rows. Verdict: ADOPT if (a) and (b); COMPARATOR if (a) and not (b); DROP if (a) fails.
The sign -1 score is reported beside it and credits nothing.

PREDICTION. DROP survives: the reviewer's approximate recomputation with the released flags gave
rho(share) -0.152, rho(gap) +0.482 and 0 of 24 rows. Post-onset about 0.32 at +1 (a constant
again) and 0.27 to 0.30 at -1.

Output: replication/czb/out/jj2c_released_flags.md, out/jj2c_released_flags_cells.csv
Run:    python replication/czb/jj2c_released_flags.py
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
import hs1_situational_surprise as HS      # noqa: E402
import jj2_rollout_cutin as J2             # noqa: E402  card JJ.2 (read only)
from aidriver.preferences import PreferenceParams  # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, update_intention  # noqa: E402
from rollout.boundary import axis, delta_g  # noqa: E402
from rollout.efe import g_by_policy  # noqa: E402
from rollout.policies import CUTIN_MENU, ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
JJ2_SCORE, REPRO_TOL = 0.3202, 0.0005
G1_GATED, G1_UNGATED, G1_CP1 = 0.1027, 0.1137, 0.0319
GAP_RULE, CHANCE = 0.1522, 0.320


def run(cells: pd.DataFrame, scenes: dict, released: bool) -> pd.DataFrame:
    rows = []
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        b = belief_at(J2.scene_of(scenes[key], key), e_t, FLOORS_STUDY2,
                      p_change_prior=P_CHANGE_PRIOR, with_intention=False)
        b.p_change = update_intention(P_CHANGE_PRIOR, b.vy_oth, FLOORS_STUDY2.sd_v_lat,
                                      sign=float(np.sign(b.y_rel)) or 1.0)
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=0)
        paths = {k: ego_rollout(b, k, HORIZON_S, DT_S) for k in CUTIN_MENU}
        p = (PreferenceParams(v_desired=b.v_ego) if released else
             PreferenceParams(v_desired=b.v_ego, lane_entry_continuous=True,
                              counterfactual_residual_severity=True,
                              lane_entry_shape_k=J2.CZB_LANE_ENTRY_SHAPE_K))
        g = g_by_policy(b, fut, paths, p)
        rows.append({"video": v, "cp": cp, "dg": delta_g(g), "G_continue": g["continue"],
                     "best": min(g, key=g.get)})
    return pd.DataFrame(rows)


def score(df: pd.DataFrame, cells: pd.DataFrame) -> dict:
    d = df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
    ax = axis(d.dg.to_numpy(float))
    d["x"] = ax.values
    post = d[d.cp != "CP1"].reset_index(drop=True)
    cp1 = d[d.cp == "CP1"].reset_index(drop=True)
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    y, w, f = post.p.to_numpy(float), post.n.to_numpy(float), post.ttc_start.to_numpy(float)
    x = post.x.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for k in np.unique(f):
        th = R.fit(x[f != k], y[f != k], w[f != k], -1.0)
        pred[f == k] = R.predict(th, x[f == k], -1.0)
    agree, nrows, _ = J2.matched_rows(post, post.dg.to_numpy(float), +1.0)
    return {"post": r_post, "neg": R.wrmse(y, pred, w), "cp1": r_cp1, "rows": agree,
            "n_rows": nrows, "rho_p": float(spearmanr(post.dg, post.p).statistic),
            "rho_gap": float(spearmanr(post.dg, post.distance).statistic), "zeros": ax.n_zero}


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = HS.study2_scenes(cells)
    proj = run(cells, scenes, released=False)
    rel = run(cells, scenes, released=True)
    sp, sr = score(proj, cells), score(rel, cells)
    rel.merge(proj[["video", "dg"]].rename(columns={"dg": "dg_project"}), on="video").to_csv(
        OUT / "jj2c_released_flags_cells.csv", index=False)
    repro = abs(sp["post"] - JJ2_SCORE) <= REPRO_TOL
    a = sr["post"] <= G1_GATED + 0.01
    b = sr["cp1"] < 0.05
    verdict = "ADOPT" if a and b else ("COMPARATOR" if a else "DROP")
    L = ["# Card JJ.2c -- card JJ.2 with the released preference flags", "",
         "Generated by `replication/czb/jj2c_released_flags.py`; the stagings, the rules and the"
         " prediction were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "## 0 Reproduction", "",
         f"Card JJ.2's staging here: {sp['post']:.4f} against its {JJ2_SCORE:.4f}, within"
         f" {REPRO_TOL}: **{'PASS' if repro else 'FAIL'}**.", "",
         "## 1 The two stagings", "",
         "| staging | post-onset held out, sign +1 | sign -1 | pre-onset | matched-TTC rows |"
         " rho(dG, share) | rho(dG, gap) | zero cells |", "|---|---|---|---|---|---|---|---|"]
    for lab, s in (("**released** (`PreferenceParams(v_desired=v_ego)`, nothing else)", sr),
                   ("the project's staging (card JJ.2: ramp braking margin, continuous lane"
                    " entry)", sp)):
        L.append(f"| {lab} | {s['post']:.4f} | {s['neg']:.4f} | {s['cp1']:.4f} |"
                 f" {s['rows']} of {s['n_rows']} | {s['rho_p']:+.3f} | {s['rho_gap']:+.3f} |"
                 f" {s['zeros']} |")
    L += ["", f"Comparators: gated looming {G1_GATED}, ungated {G1_UNGATED}, gap {GAP_RULE},"
          f" chance {CHANCE}; card G.1's pre-onset {G1_CP1}.", "",
          "## 2 The verdict on card JJ.2's rules, released staging", "",
          f"**{verdict}.** Rule (a) {sr['post']:.4f} against {G1_GATED + 0.01:.4f}"
          f" ({'holds' if a else 'fails'}); rule (b) {sr['cp1']:.4f} against 0.05"
          f" ({'holds' if b else 'fails'}); rule (c) {sr['rows']} of {sr['n_rows']}.", "",
          "So the statements the arc made about \"the released model\" on this design "
          + ("do carry over to the released model: Delta G is dropped there too."
             if verdict == "DROP" else "**do NOT carry over**: see the table."),
          "", f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj2c_released_flags.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
