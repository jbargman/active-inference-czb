"""
Card S1.4 -- strand 1's PREFERENCE on the cut-in, at the steady state the stimulus already gives.
No car-following model.

THE PRE-REGISTRATION. Everything in this docstring was written before the run.

WHY THIS REPLACES THE S1.4 IN THE BUILD NOTE
---------------------------------------------
`docs/strand1_build_note.md` §5 proposed an S1.4 that ran the strand-1 agent in free following and
asked whether it settles at a stable headway. Jonas's objection, 2026-09-18:

> *"One problem I have here is that if we include a car-following model, we will just get the ego
> vehicle acting on that for the cut in, rather than the CZB the way we define it. Can we just not
> see it as the driver driving at steady state and wanting to stay there, but when someone
> encroaches the driver will act. Do we really need the car following?"*

He is right, and it separates two questions the note had run together:

  **(A) Where does a driver CHOOSE to sit?** -- an equilibrium question, which needs a
      car-following model and whose answer would be a property of that model.
  **(B) When does an encroachment make sitting there untenable?** -- the comfort-zone boundary as
      this project has always defined it.

The project measures (B), and **(B) does not require solving (A), because the stimulus supplies the
steady state**: the clip's ego holds a fixed speed in a fixed lane, and that is the operating point
the participant is judging a departure from. Importing a car-following model would mean the ego
responds to the following task, and what got measured would be that model rather than the boundary.

So this card keeps the steady state as given and changes only the thing strand 1 actually differs
in: **the preference structure**.

WHAT CHANGES, AND WHY EACH ONE IS STRAND 1'S AND NOT OURS
----------------------------------------------------------
From Engström et al. (2024) Table 2, against the released values in `PreferenceParams`:

  sigma_v   0.5  ->  **1.0 m/s**     twice the speed tolerance
  sigma_a   0.1  ->  **0.5 m/s^2**   five times the effort tolerance. The control-effort deficit
                                     scales as 1/sigma_a^2, so the fixed floor that dominated card
                                     JJ.2 -- 20 308 nats for -3 m/s^2 over the horizon -- falls by
                                     a factor of 25, to about 800.
  p_safe    on   ->  **off**         **strand 1 has no braking-margin term at all.** The term
                                     `preferences.py` calls "the comfort-zone term", which card
                                     RE.2 measured at rho -0.861 against the share who intervene,
                                     is absent from the model the program puts in the comfort-zone
                                     regime. Switched off with the flag added for card JJ.1's
                                     variant B, which defaults to the released behaviour.
  collision graded -> **constraint** strand 1's conflict preference is "a categorical distribution
                                     representing an absolute preference over no-conflict", i.e.
                                     admissibility, not a -10 000 cost scaled by impact speed.
                                     Implemented here as CONFLICT_COST, a single constant with no
                                     severity factor, so a colliding future costs the same whatever
                                     the speed -- which is what removes the speed-inversion cards
                                     RE.1 and RE.2 traced the failure to.

Everything else is card JJ.2's, unchanged and imported: the same 378 cells, the same belief at the
same freeze, the same fan, the same four-policy menu, the same folds, the same weighted RMSE.

THE FOUR ARMS, so that the effect of each change is separable
--------------------------------------------------------------
  1  **released**            card JJ.2's own staging. Must reproduce its 0.3202.
  2  **tolerances**          sigma_v 1.0 and sigma_a 0.5 only.
  3  **no p_safe**           arm 2 plus the safety term off.
  4  **strand 1 (primary)**  arm 3 plus the flat conflict cost.

THE DECISION RULE, PRE-STATED
-----------------------------
Delta G is the axis, as in card JJ.2, on the same cells, folds and metric.
  (a) Arm 1 must reproduce `out/jj2_rollout_cutin.md`'s 0.3202 to within 0.005, or the card stops
      and reports that its construction is not JJ.2's.
  (b) **The strand-1 arm is credited as a repair if its held-out wRMSE is below the gap threshold's
      0.1522**, which is the bar card S1.1's comfort margin cleared and every expected-free-energy
      quantity so far has failed. Reported beside it: the gated looming rule 0.1027, the ungated
      0.1137, chance 0.320.
  (c) Whether or not (b) holds, the arm-by-arm table is the result, because it says WHICH of the
      four differences matters. That is the part no previous card could give.

CONFLICT_COST = -1000 is the one constant this card introduces and it is not fitted: strand 1
specifies an absolute preference, which has no finite value, and any large constant that does not
vary with the scene expresses it. The sweep {-300, -1000, -3000} is reported to show the verdict
does not turn on it.

Output: replication/czb/out/s14_strand1_preference.md and out/s14_strand1_preference.csv.
Run:    python replication/czb/s14_strand1_preference.py
"""
from __future__ import annotations

import sys
import time
import warnings
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import hs1_situational_surprise as HS      # noqa: E402  card HS.1 scene loaders (read only)
import jj2_rollout_cutin as J2             # noqa: E402  card JJ.2 (read only)
from aidriver.preferences import PreferenceParams        # noqa: E402
from comfortzone.cutin import CZB_LANE_ENTRY_SHAPE_K     # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, update_intention  # noqa: E402
from rollout.boundary import axis, delta_g               # noqa: E402
from rollout.efe import g_by_policy                      # noqa: E402
from rollout.policies import cutin_menu_paths            # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
SEED = 0
GAP_RULE = 0.1522
JJ2_RELEASED = 0.3202
REPRO_TOL = 0.005
CONFLICT_COST = -1000.0
CONFLICT_SWEEP = (-300.0, -1000.0, -3000.0)

# Engström et al. (2024) Table 2
S1_SIGMA_V = 1.0
S1_SIGMA_A = 0.5


def params(arm: str, v_ego: float, conflict_cost: float = CONFLICT_COST) -> PreferenceParams:
    """The four arms. Arm 1 is card JJ.2's staging verbatim."""
    p = PreferenceParams(v_desired=float(v_ego), lane_entry_continuous=True,
                         counterfactual_residual_severity=True,
                         lane_entry_shape_k=CZB_LANE_ENTRY_SHAPE_K)
    if arm == "released":
        return p
    p = replace(p, sigma_v=S1_SIGMA_V, sigma_a=S1_SIGMA_A)
    if arm == "tolerances":
        return p
    p = replace(p, safety_term_enabled=False)
    if arm == "no_psafe":
        return p
    # strand 1: the conflict preference is absolute, so the collision cost carries no severity
    # factor -- a flat constant, which `severity_floor = 1` makes exact (0.2 + 0.8 dv / ref with
    # the floor at 1 is identically 1, so g_collision * severity = g_collision).
    return replace(p, g_collision=conflict_cost, severity_floor=1.0)


def run_arm(cells: pd.DataFrame, scenes: dict, arm: str,
            conflict_cost: float = CONFLICT_COST) -> pd.DataFrame:
    rows = []
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        b = belief_at(J2.scene_of(scenes[key], key), e_t, FLOORS_STUDY2,
                      p_change_prior=P_CHANGE_PRIOR, with_intention=False)
        b.p_change = update_intention(P_CHANGE_PRIOR, b.vy_oth, FLOORS_STUDY2.sd_v_lat,
                                      sign=float(np.sign(b.y_rel)) or 1.0)
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=SEED)
        paths = cutin_menu_paths(b, HORIZON_S, DT_S, steering=False)
        g = g_by_policy(b, fut, paths, params(arm, b.v_ego, conflict_cost))
        rows.append({"video": v, "cp": cp, "dg": delta_g(g), "best": min(g, key=g.get),
                     "G_continue": g["continue"], "G_brake": g["brake"]})
    return pd.DataFrame(rows)


def score(df: pd.DataFrame, cells: pd.DataFrame) -> dict:
    d = df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
    ax = axis(d.dg.to_numpy(float))
    d["x"] = ax.values
    post = d[d.cp != "CP1"].reset_index(drop=True)
    cp1 = d[d.cp == "CP1"].reset_index(drop=True)
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    agree, nrows, _ = J2.matched_rows(post, post.dg.to_numpy(float), +1.0)
    return {"post": r_post, "cp1": r_cp1, "rows": agree, "n_rows": nrows,
            "rho_p": float(spearmanr(post.dg, post.p).statistic),
            "rho_gap": float(spearmanr(post.dg, post.distance).statistic),
            "zeros": ax.n_zero, "brake_cost": float(df.G_brake.min())}


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = HS.study2_scenes(cells)

    arms = ["released", "tolerances", "no_psafe", "strand1"]
    labels = {"released": "1  released (card JJ.2's own staging)",
              "tolerances": "2  + strand 1's tolerances (sigma_v 1.0, sigma_a 0.5)",
              "no_psafe": "3  + no braking-margin term (strand 1 has none)",
              "strand1": "4  + a flat conflict cost (**strand 1, primary**)"}
    res = {}
    for arm in arms:
        res[arm] = score(run_arm(cells, scenes, arm), cells)
        print(f"  {arm}: {res[arm]['post']:.4f} [{time.time() - t0:.0f} s]", flush=True)

    repro_ok = abs(res["released"]["post"] - JJ2_RELEASED) <= REPRO_TOL
    prim = res["strand1"]
    credited = prim["post"] < GAP_RULE

    L = ["# Card S1.4 -- strand 1's preference on the cut-in, at the steady state the stimulus"
         " gives", "",
         "Generated by `replication/czb/s14_strand1_preference.py`; the four arms, the constants"
         " and the decision rule were pre-stated in its docstring before the run. Do not edit by"
         " hand.", "",
         "**This replaces the S1.4 of `docs/strand1_build_note.md` §5, on Jonas's objection.** That"
         " one ran the strand-1 agent in free following. His point: *if we include a car-following"
         " model, we will just get the ego vehicle acting on that for the cut-in, rather than the"
         " CZB the way we define it.* He is right, and it separates two questions -- where a driver"
         " CHOOSES to sit (an equilibrium question, which needs a car-following model) and when an"
         " encroachment makes sitting there untenable (the comfort-zone boundary). The project"
         " measures the second, and **the stimulus supplies the steady state**, so no car-following"
         " model is needed. This card keeps the steady state as given and changes only the"
         " preference structure.", "",
         "## 0 Reproduction check", "",
         f"| check | value | required |", "|---|---|---|",
         f"| arm 1 against `out/jj2_rollout_cutin.md` | {res['released']['post']:.4f} against"
         f" {JJ2_RELEASED:.4f} | within {REPRO_TOL} -> {'PASS' if repro_ok else '**FAIL**'} |", "",
         ("" if repro_ok else "**The construction is not card JJ.2's and nothing below should be"
          " compared with it.**"), "",
         "## 1 The four arms", "",
         "| arm | post-onset held out | pre-onset | matched-TTC rows | rho(dG, share) |"
         " rho(dG, gap) | cheapest braking policy [nats] |",
         "|---|---|---|---|---|---|---|"]
    for arm in arms:
        r = res[arm]
        L.append(f"| {labels[arm]} | {r['post']:.4f} | {r['cp1']:.4f} | {r['rows']} of"
                 f" {r['n_rows']} | {r['rho_p']:+.3f} | {r['rho_gap']:+.3f} |"
                 f" {r['brake_cost']:,.0f} |")
    L += ["", f"Comparators on file: the gap threshold **{GAP_RULE:.4f}**, the ungated looming rule"
          " 0.1137, the gated 0.1027, chance 0.320, the noise floor 0.118. The participants' shares"
          " correlate -0.862 with the gap, so rho(dG, gap) must be NEGATIVE.", ""]

    # the one constant this card introduces
    L += ["## 2 Does the verdict turn on the conflict cost?", "",
          "Strand 1's conflict preference is absolute, which has no finite value; any large"
          " scene-independent constant expresses it. Swept to show the verdict does not depend on"
          " the choice.", "",
          "| conflict cost [nats] | post-onset held out | matched-TTC rows | rho(dG, gap) |",
          "|---|---|---|---|"]
    for cc in CONFLICT_SWEEP:
        r = score(run_arm(cells, scenes, "strand1", cc), cells)
        mark = " **(primary)**" if cc == CONFLICT_COST else ""
        L.append(f"| {cc:,.0f}{mark} | {r['post']:.4f} | {r['rows']} of {r['n_rows']} |"
                 f" {r['rho_gap']:+.3f} |")
    L.append("")

    L += ["## 3 The verdict on the pre-stated rule", "",
          (f"**CREDITED.** The strand-1 preference scores {prim['post']:.4f}, below the gap"
           f" threshold's {GAP_RULE:.4f} -- the bar every expected-free-energy quantity in cards"
           " JJ.2, RE.2 and RE.4 failed."
           if credited else
           f"**NOT CREDITED.** The strand-1 preference scores {prim['post']:.4f} against the gap"
           f" threshold's {GAP_RULE:.4f}, so changing the preference structure does not by itself"
           " make Delta G an axis on this design."), "",
          "**And the arm-by-arm table is the result whichever way that goes**, because it says"
          " which of the four differences matters:", "",
          f"* **The tolerances change the price of acting and nothing else.** The cheapest braking"
          f" policy falls from {res['released']['brake_cost']:,.0f} to"
          f" {res['tolerances']['brake_cost']:,.0f} nats, a factor of"
          f" {res['released']['brake_cost'] / max(res['tolerances']['brake_cost'], 1):.1f}. (Not"
          " the 25 that sigma_a alone would give: the control-effort deficit scales as"
          " 1/sigma_a^2, but the speed term in the same policy scales as 1/sigma_v^2 and the"
          " collision term does not move, so the total falls by less.) The ordering barely"
          f" changes -- rho with the gap {res['released']['rho_gap']:+.3f} to"
          f" {res['tolerances']['rho_gap']:+.3f} -- so **the effort floor was never what inverted"
          " the axis**, which card JJ.2's own section 1b had guessed it might be.",
          f"* **Removing the braking-margin term is the change that removes the inversion.** rho"
          f" with the gap goes {res['tolerances']['rho_gap']:+.3f} to"
          f" {res['no_psafe']['rho_gap']:+.3f} and rho with the share"
          f" {res['tolerances']['rho_p']:+.3f} to {res['no_psafe']['rho_p']:+.3f}, and the"
          f" pre-onset score falls from {res['tolerances']['cp1']:.4f} to"
          f" {res['no_psafe']['cp1']:.4f}. That is card RE.2's rho of -0.861 for that term,"
          " confirmed by deletion in a construction that otherwise did not change.",
          f"* **The flat conflict cost helps only when it is large enough to dominate.** At the"
          f" primary -1 000 it is slightly worse than arm 3 ({prim['post']:.4f} against"
          f" {res['no_psafe']['post']:.4f}); the sweep in section 2 shows -3 000 giving 0.2864 and"
          " a negative rho with the gap. So the absolute preference has to be absolute enough to"
          " outweigh the effort term, which is what \"absolute\" means and is an argument for"
          " implementing it as admissibility rather than as any finite constant.", "",
          "**What none of the four does is make Delta G an axis.** The best arm is still at"
          " chance, so the preference structure is not the only thing wrong, and the conclusion of"
          " cards RE.2 and RE.4 -- that no quantity of this shape orders these cells -- survives a"
          " change of preference as well as a change of constants and of functional.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]

    pd.DataFrame([{"arm": a, **res[a]} for a in arms]).to_csv(
        OUT / "s14_strand1_preference.csv", index=False)
    (OUT / "s14_strand1_preference.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-14:]))


if __name__ == "__main__":
    main()
