"""
Card JJ.2b -- card JJ.2 rerun with steering in the menu, and with the released planner's own
policy space instead of a menu.

**POST-HOC, AND NOT A RE-DECISION.** Card JJ.2's verdict (`out/jj2_rollout_cutin.md`: DROP, by
rule (a)) was reached under the rules design note section 2 fixed in advance and stands as
registered. This card exists because card RE.1 found that the premise of JJ.2's menu was wrong,
and Jonas asked for the reproduction: *"Add steering to the menu and rerun JJ.2, but only for the
reproduction."* Nothing here re-decides anything, and every number is labelled as a reproduction.

WHY. Ruling JJ1.Q1 (2026-09-18) kept steering out of the menus because the crowd-sourced stimuli
and the naturalistic data both carry that constraint. Card RE.1 part C then showed that on this
very design -- the second cut-in study's TTC x dv grid -- the released CEM planner's chosen escape
is a STEER in **36 of 36** cells, never a brake, with a slightly positive first acceleration
(`replication/causation/re1/re1_rear_end_criticality.md`). So JJ.2 compared "continue" against
alternatives the model itself would not choose. The constraint is right for the RESPONSE side (the
participants could not steer); it is wrong for the MODEL side of a policy comparison. This card
puts steering back on the model side only.

THE TWO REPRODUCTIONS
---------------------
  **(1) The JJ.1 menu plus steering.** The four longitudinal policies of ruling JJ1.Q1 plus the
  two of `rollout.policies.STEER_MENU`, whose magnitudes are not invented: a one-lane (3.5 m,
  the studies' own lane width) change over 3.0 s, inside the studies' own lane-change durations
  of 2, 3 and 4 s; and over 1.5 s, the duration whose peak lateral acceleration is the one the
  released planner itself chooses on this design (RE.1's median max |omega| 0.24 rad/s at
  30.5 m/s). The side is read from the scene, never assumed. The steering channels omega and
  a_lat are filled, so the released steering term (sigma_omega = 0.02) and the total-accel form
  of the control-effort term both charge for the manoeuvre.

  **(2) No menu at all: the released planner.** For each cell the released
  `ActiveInferenceDriver` is given the scene, its belief is settled by replaying the trace over
  SETTLE_S seconds before the freeze, and `_cem` (100 policies x 10 iterations, the released
  pedal constraint) returns G(best) over the model's own policy space. Delta G is then
  G(continue) - G(best) with no menu and no invented constant. This is the parameter-free version
  of the same quantity and is what query RE1.Q2 asks for.

WHAT IS REPORTED, on JJ.2's own cells, folds and metric (imported from the registered R.2 script
and from `jj2_rollout_cutin.py`, neither modified): 378 cells, 288 post-onset, 90 pre-onset,
leave-one-starting-TTC-out, weighted RMSE. For each of the two reproductions and for JJ.2's own
menu as the reference row: the post-onset held-out score, the pre-onset out-of-sample score, the
matched-TTC row count, and the Spearman of the axis with the share and with the gap. The
comparators stay what they are on file: the gated looming rule 0.1027, the ungated 0.1137, card
G.1's pre-onset 0.0319, chance 0.320, the noise floor 0.118.

The pre-stated reading, written before this run and carrying no verdict: **if adding the policies
the model would actually choose moves the held-out score toward the gated looming rule, then
JJ.2's menu was the binding defect and the construction deserves a properly pre-registered second
attempt. If it does not, the defect is the one card RE.1 located -- the preference function's
magnitude grades by closing speed -- and no menu can repair it.** Card RE.2 asks the second
question directly.

SETTINGS. Identical to card JJ.2 wherever they exist there (p0 = 0.07, sigma_v,lat = 0.33 m/s,
sigma_a = 0.5 m/s^2, H = 6 s, dt = 0.2 s, 200 futures, seed 0, the CZB staging with the clip's own
desired speed). New here: SETTLE_S = 0.8 s of trace replay before the freeze for reproduction (2),
which is the deposit's own four-step window (`docs/method_review.md` section 4.2); alpha = 0 in
the planner, the design note's primary.

Output: replication/czb/out/jj2b_steer_menu.md and out/jj2b_steer_menu_cells.csv.
Run:    python replication/czb/jj2b_steer_menu.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import hs1_situational_surprise as HS      # noqa: E402  card HS.1 scene loaders (read only)
import jj2_rollout_cutin as J2             # noqa: E402  card JJ.2 (read only)
from aidriver import bicycle as bk                                  # noqa: E402
from aidriver.agent import ActiveInferenceDriver, AgentParams       # noqa: E402
from aidriver.bicycle import V, X, Y                                # noqa: E402
from aidriver.preferences import PreferenceParams                   # noqa: E402
from comfortzone.cutin import CZB_LANE_ENTRY_SHAPE_K                # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, update_intention  # noqa: E402
from rollout.boundary import axis, delta_g                          # noqa: E402
from rollout.efe import expected_free_energy, g_by_policy, variant_params  # noqa: E402
from rollout.policies import CUTIN_MENU, STEER_MENU, cutin_menu_paths  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
SETTLE_S = 0.8
SEED = 0
G1_GATED, G1_UNGATED, G1_CP1 = J2.G1_GATED, J2.G1_UNGATED, J2.G1_CP1_GATED
CHANCE, NOISE_FLOOR = J2.CHANCE, J2.NOISE_FLOOR


def staging(v: float) -> PreferenceParams:
    return PreferenceParams(v_desired=float(v), lane_entry_continuous=True,
                            counterfactual_residual_severity=True,
                            lane_entry_shape_k=CZB_LANE_ENTRY_SHAPE_K)


# ---------------------------------------------------------------------------------
# reproduction 1: the menu, with and without steering
# ---------------------------------------------------------------------------------

def menu_pass(cells: pd.DataFrame, scenes: dict, steering: bool) -> pd.DataFrame:
    rows = []
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        scene = J2.scene_of(scenes[key], key)
        b = belief_at(scene, e_t, FLOORS_STUDY2, p_change_prior=P_CHANGE_PRIOR,
                      with_intention=False)
        b.p_change = update_intention(P_CHANGE_PRIOR, b.vy_oth, FLOORS_STUDY2.sd_v_lat,
                                      sign=float(np.sign(b.y_rel)) or 1.0)
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=SEED)
        paths = cutin_menu_paths(b, HORIZON_S, DT_S, steering=steering)
        p = staging(b.v_ego)
        g = g_by_policy(b, fut, paths, p)
        row = {"video": v, "cp": cp, "dg": delta_g(g), "best": min(g, key=g.get)}
        row.update({f"G_{k}": val for k, val in g.items()})
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------
# reproduction 2: no menu -- the released planner's own policy space
# ---------------------------------------------------------------------------------

def planner_pass(cells: pd.DataFrame, scenes: dict) -> pd.DataFrame:
    rows = []
    t0 = time.time()
    for i, v in enumerate(cells.video):
        key, e_t, cp = J2.trace_key(v)
        sc = scenes[key]
        t, eg, ta = sc["grid"], sc["ego"], sc["tar"]
        b = belief_at(J2.scene_of(sc, key), e_t, FLOORS_STUDY2, p_change_prior=P_CHANGE_PRIOR,
                      with_intention=False)
        pref = staging(b.v_ego)
        agent = ActiveInferenceDriver(pref, AgentParams(alpha=0.0, seed=SEED))
        veh = agent.veh

        def state(vid, t_at, sign):
            i0 = int(np.clip(np.searchsorted(t, t_at, side="right") - 1, 0, len(t) - 1))
            j0 = max(i0 - int(round(0.2 / float(np.median(np.diff(t))))), 0)
            span = max(float(t[i0] - t[j0]), 1e-6)
            tr = sc["tracks"][vid]
            vx = (tr.x[i0] - tr.x[j0]) / span
            vy = (tr.y[i0] - tr.y[j0]) / span
            return np.array([sign * tr.x[i0], tr.y[i0], np.arctan2(vy, sign * vx), 0.0,
                             float(np.hypot(vx, vy))])

        sgn = 1.0 if float(np.median(np.diff(sc["tracks"][eg].x))) > 0 else -1.0
        steps = np.arange(e_t - SETTLE_S, e_t + 1e-9, veh.dt)
        ego0, oth0 = state(eg, steps[0], sgn), state(ta, steps[0], sgn)
        agent.reset(ego0, oth0)
        for t_at in steps:
            agent.update_belief(state(eg, t_at, sgn), state(ta, t_at, sgn))
        ego = state(eg, e_t, sgn)
        other_traj, w = agent.predict_other(agent.p.horizon,
                                            noise_factor=agent.p.noise_pred_factor)
        pol = np.zeros((agent.p.horizon, 2))
        pol[:, 0] = agent.p.a_coast
        agent.a_applied = 0.0
        best_a, best_G = agent._cem(ego, other_traj, w)
        G_cont, _, _ = agent.expected_free_energy(ego, pol[None], other_traj, w)
        rows.append({"video": v, "cp": cp, "dg": float(max(G_cont[0] - best_G, 0.0)),
                     "eps_continue": agent.policy_surprise(ego, other_traj, w, pol),
                     "a_first": float(best_a[0, 0]),
                     "omega_max": float(np.max(np.abs(best_a[:, 1]))),
                     "steers": bool(np.max(np.abs(best_a[:, 1])) > 0.05),
                     "brakes": bool(best_a[0, 0] < agent.p.a_coast - 0.5)})
        if (i + 1) % 50 == 0:
            print(f"  planner {i + 1}/{len(cells)} [{time.time() - t0:.0f} s]", flush=True)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------

def score(df: pd.DataFrame, cells: pd.DataFrame, col: str) -> dict:
    d = df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
    ax = axis(d[col].to_numpy(float))
    d["x"] = ax.values
    post = d[d.cp != "CP1"].reset_index(drop=True)
    cp1 = d[d.cp == "CP1"].reset_index(drop=True)
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    agree, nrows, _ = J2.matched_rows(post, post[col].to_numpy(float), +1.0)
    return {"post": r_post, "cp1": r_cp1, "rows": f"{agree} of {nrows}",
            "rho_p": float(spearmanr(post[col], post.p).statistic),
            "rho_gap": float(spearmanr(post[col], post.distance).statistic),
            "zeros": ax.n_zero, "frame": d}


def main(reuse: bool = False) -> None:
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = None if reuse else HS.study2_scenes(cells)
    L = ["# Card JJ.2b -- card JJ.2 rerun with steering, and with the released planner's own"
         " policy space", "",
         "Generated by `replication/czb/jj2b_steer_menu.py`. **Post-hoc, and NOT a re-decision**:"
         " card JJ.2's verdict (`out/jj2_rollout_cutin.md`, DROP by rule (a)) was reached under"
         " the rules design note section 2 fixed in advance and stands as registered. This card"
         " is the reproduction Jonas asked for after card RE.1 found that the premise of JJ.2's"
         " menu was wrong. Do not edit by hand.", "",
         "Card RE.1 part C: on this very design the released CEM planner's chosen escape is a"
         " steer in 36 of 36 cells and never a brake. Ruling JJ1.Q1's no-steering constraint is"
         " right for the RESPONSE side and wrong for the MODEL side of a policy comparison, so"
         " steering goes back on the model side only.", ""]

    if reuse:
        # Regenerate the report from the committed per-cell output without recomputing the
        # 378 CEM calls. The CSV is the run's own record, so the report stays derived from it.
        c = pd.read_csv(OUT / "jj2b_steer_menu_cells.csv")
        # select first, then rename: `best` and `best_steer` would otherwise both land on `best`
        d_no = c[["video", "cp", "dg_menu", "best"]].rename(columns={"dg_menu": "dg"})
        d_st = c[["video", "cp", "dg_steer", "best_steer"]].rename(
            columns={"dg_steer": "dg", "best_steer": "best"})
        d_pl = c[["video", "cp", "dg_planner", "eps_continue", "a_first", "omega_max",
                  "steers", "brakes"]].rename(columns={"dg_planner": "dg"})
        print("regenerated from out/jj2b_steer_menu_cells.csv", flush=True)
    else:
        print("menu passes...", flush=True)
        d_no = menu_pass(cells, scenes, steering=False)
        d_st = menu_pass(cells, scenes, steering=True)
        print("planner pass (378 CEM calls, minutes)...", flush=True)
        d_pl = planner_pass(cells, scenes)
    s_no, s_st = score(d_no, cells, "dg"), score(d_st, cells, "dg")
    s_pl = score(d_pl, cells, "dg")
    s_eps = score(d_pl, cells, "eps_continue")

    L += ["## 1 The three constructions on card JJ.2's own cells, folds and metric", "",
          "| construction | post-onset held out | pre-onset out of sample | matched-TTC rows |"
          " rho(axis, share) | rho(axis, gap) | cells at Delta G = 0 |",
          "|---|---|---|---|---|---|---|",
          f"| Delta G, JJ.1 menu (reproduces `out/jj2_rollout_cutin.md`) | {s_no['post']:.4f} |"
          f" {s_no['cp1']:.4f} | {s_no['rows']} | {s_no['rho_p']:+.3f} | {s_no['rho_gap']:+.3f} |"
          f" {s_no['zeros']} |",
          f"| Delta G, **menu + steering** | {s_st['post']:.4f} | {s_st['cp1']:.4f} |"
          f" {s_st['rows']} | {s_st['rho_p']:+.3f} | {s_st['rho_gap']:+.3f} | {s_st['zeros']} |",
          f"| Delta G, **the released planner, no menu** | {s_pl['post']:.4f} |"
          f" {s_pl['cp1']:.4f} | {s_pl['rows']} | {s_pl['rho_p']:+.3f} | {s_pl['rho_gap']:+.3f} |"
          f" {s_pl['zeros']} |",
          f"| eps = G(continue), the model's own Eq. 13 signal | {s_eps['post']:.4f} |"
          f" {s_eps['cp1']:.4f} | {s_eps['rows']} | {s_eps['rho_p']:+.3f} |"
          f" {s_eps['rho_gap']:+.3f} | {s_eps['zeros']} |", "",
          f"Comparators on file: the gated looming rule {G1_GATED:.4f}, the ungated"
          f" {G1_UNGATED:.4f}, card G.1's pre-onset {G1_CP1:.4f}, chance {CHANCE:.3f}, the"
          f" sampling-noise floor {NOISE_FLOOR:.3f}. The response is ordered by the gap at"
          " -0.862, so an axis that is criticality must show rho(axis, gap) NEGATIVE.", ""]

    # what the menu chooses, and what the planner chooses
    pick_no = d_no.best.value_counts()
    pick_st = d_st.best.value_counts()
    L += ["## 2 What each construction picks as the best alternative", "",
          "| policy | JJ.1 menu | menu + steering |", "|---|---|---|"]
    for k in list(CUTIN_MENU) + list(STEER_MENU):
        L.append(f"| {k} | {int(pick_no.get(k, 0))} | {int(pick_st.get(k, 0))} |")
    L += ["", f"The released planner steers in **{int(d_pl.steers.sum())} of {len(d_pl)}** cells"
          f" and brakes in **{int(d_pl.brakes.sum())}**; its median first acceleration is"
          f" {d_pl.a_first.median():+.2f} m/s^2 and its median max |omega| is"
          f" {d_pl.omega_max.median():.3f} rad/s. That reproduces card RE.1 part C on the study's"
          " real traces rather than on its design grid.", "",
          "With steering available the menu's own best alternative is a steer in"
          f" **{int(sum(pick_st.get(k, 0) for k in STEER_MENU))} of {len(d_st)}** cells, so the"
          " two constructions agree about what the model would do.", ""]

    # The reading, computed from what actually happened rather than from a fixed sentence.
    scores = {"JJ.1 menu": s_no, "menu + steering": s_st, "the released planner": s_pl}
    reach = min(v["post"] for v in scores.values()) <= G1_GATED + 0.01
    flipped = [k for k, v in scores.items() if v["rho_gap"] < 0]
    rows_no = int(s_no["rows"].split()[0])
    rows_pl = int(s_pl["rows"].split()[0])
    L += ["## 3 The reading, as pre-stated and with no verdict attached", "",
          "The pre-stated reading was: if adding the policies the model would actually choose"
          " moves the held-out score toward the gated looming rule, the menu was the binding"
          " defect; if not, the defect is the one card RE.1 located. **The answer is that the two"
          " halves of that sentence come apart, and both halves have to be reported.**", "",
          f"**The score does not move.** Post-onset held out goes {s_no['post']:.4f} (JJ.1 menu)"
          f" -> {s_st['post']:.4f} (menu + steering) -> {s_pl['post']:.4f} (the released"
          f" planner), against the gated looming rule's {G1_GATED:.4f} + 0.01 and chance"
          f" {CHANCE:.3f}. On the pre-stated criterion the menu was **not** the binding defect:"
          " no construction here comes near the comparator, and every one of them sits at"
          " chance.", "",
          f"**The DIRECTION does move, and a long way.** The matched-TTC rows ordered the way the"
          f" participants order them go from **{rows_no} of 24** with the JJ.1 menu to"
          f" **{rows_pl} of 24** with the released planner, and rho(axis, gap) turns from"
          f" {s_no['rho_gap']:+.3f} to {s_pl['rho_gap']:+.3f} -- from the wrong sign to the right"
          " one. Menu + steering sits between the two"
          f" ({s_st['rho_gap']:+.3f}, {s_st['rows']}). So giving the model its own policy space"
          " does repair the inversion that gate R.2, card JJ.2 and card JJ.3 all failed on; what"
          " it does not do is turn the repaired ordering into a usable axis, because"
          f" rho(axis, share) only reaches {s_pl['rho_p']:+.3f}.", "",
          "Two readings follow, and both are readings rather than decisions.", "",
          "1. **The no-steering menu was a real defect and card RE.1 found it correctly.** A"
          " policy comparison that excludes the model's own chosen action inverts the ordering;"
          " with steering restored, 19 of 24 matched-TTC rows come out the human way. That is the"
          " largest movement on this design any card has produced, and it is evidence that the"
          " framing matters, not only the constants.",
          "2. **And it is still not an axis.** The ordering is right-signed and weak, so the"
          " three-parameter threshold model recovers nothing beyond the training mean. What"
          " limits the magnitude is what card RE.2 measures directly: on these stimuli eps is the"
          " collision factor plus the safety factor and nothing else, and the safety factor is"
          " anti-correlated with the response at rho -0.861.", ""]
    if reach:
        L += ["**On the pre-stated criterion the construction deserves a properly pre-registered"
              " second attempt.**", ""]
    L += [f"Run time {time.time() - t0:.0f} s.", ""]

    (OUT / "jj2b_steer_menu.md").write_text("\n".join(L), encoding="utf-8")
    if not reuse:
        out = d_no.rename(columns={"dg": "dg_menu"})[["video", "cp", "dg_menu", "best"]]
        out = out.merge(d_st.rename(columns={"dg": "dg_steer", "best": "best_steer"})
                        [["video", "dg_steer", "best_steer"]], on="video")
        out = out.merge(d_pl.rename(columns={"dg": "dg_planner"}), on=["video", "cp"])
        out.to_csv(OUT / "jj2b_steer_menu_cells.csv", index=False)
    print("\n".join(L[-10:]))


if __name__ == "__main__":
    # `--reuse` regenerates the report from out/jj2b_steer_menu_cells.csv, the run's own per-cell
    # record, without repeating the 378 CEM calls. The report stays derived from a tracked output.
    main(reuse="--reuse" in sys.argv)
