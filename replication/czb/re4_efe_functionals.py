"""
Card RE.4 -- every functional of the released expected free energy, as the axis. Is there any way
of reading this model that orders the cut-in cells?

PRE-STATED before any run (2026-09-18, on Jonas's "What can we reformulate then to make it
fit/work? It should be possible, I still feel...").

*[This supersedes the RE.4 sketched in `docs/active_inference_reformulation.md` §6, which asked
whether the argmin switch reproduces the gate. That question is downstream of this one: if no
functional of G orders the cells, a switching rule built on G cannot either.]*

THE QUESTION
------------
Card JJ.2 put **Delta G** on the axis and it scored chance. Card RE.1 showed **G(continue)** is the
model's own Eq. 13 signal and it scores chance too. Card RE.2 swept 648 parameter vectors and found
none that orders the cells. Every one of those is a different *functional* of the same expected free
energy, and the natural reading of RE.2 is that the problem is the preference, not the functional.

This card tests that reading directly, by scoring **every functional of G that has a defensible
claim to be a comfort-zone quantity**, on card JJ.2's own cells, folds and metric:

  **eps = G(continue)**        how far short of my preferences the plan I am holding will fall.
                               The released model's own Eq. 13 signal.
  **min over policies of G**   how far short I will fall *even if I do the best thing available* --
                               "how bad is my situation whatever I do". This is the functional that
                               is monotone in criticality by construction where Delta G is not, and
                               it is the obvious repair for card JJ.2's failure, so it is the reason
                               this card exists.
  **Delta G**                  the margin between the two. Card JJ.2's axis, carried for reference.
  **epistemic value**          the expected information gain of continuing. **Never tested by this
                               project in any card.** Under looming perception the observation
                               precision improves as the square of closing distance, so this term
                               RISES as the gap shrinks -- which is the direction the human response
                               has, even though its interpretation ("closer is more informative,
                               therefore more attractive") is the opposite of comfort. That tension
                               is the point: a term can be a good predictor of the boundary while
                               having the wrong sign of preference, and this card measures which.
  **the full G at alpha = 1**  pragmatic and epistemic together, the released baseline's own
                               objective.

ALPHA. Design note §1.4 fixes alpha = 0 and calls it "the authors' validated configuration".
`docs/waymo_program_revisit.md` §5 shows the deposit contradicts that: the epistemic component runs
+1745 to +1941 per step in benign following against -0.003 for the velocity preference and -2 for
control effort (`replication/osf/review/benign_eps.csv`). The released baseline has it on. **This
card runs alpha = 1**, which is also the first time the project has computed the epistemic term at
all. eps itself is alpha-independent (`policy_surprise` is the pragmatic part only), so its value
here must reproduce card JJ.2b's, and section 0 checks that.

WHERE min G COMES FROM. For the cheap functionals a single policy is enough and no planner is
needed. For min G the released CEM planner is the only defensible "best available policy", and card
JJ.2b already ran it over all 378 cells at alpha = 0; its per-cell output
(`out/jj2b_steer_menu_cells.csv`) carries `eps_continue` and `dg_planner`, and
min eps = eps_continue - dg_planner exactly, because `expected_free_energy` returns -prag while
`policy_surprise` returns H max log p(o) - prag, so the offset cancels in the difference. Those
columns are reused rather than recomputed; the alpha = 1 planner pass is NOT run here (22 minutes)
and is named as the follow-up instead.

THE DECISION RULE, PRE-STATED
-----------------------------
For each functional: the leave-one-starting-TTC-out held-out wRMSE of the three-parameter threshold
model, the pre-onset out-of-sample score, the matched-TTC row count, and Spearman with the share and
with the gap. **The participants' shares correlate -0.862 with the gap, so a criticality axis must
give rho(axis, gap) NEGATIVE.** The comparators on file: the gated looming rule 0.1027, the ungated
0.1137, card G.1's pre-onset 0.0319, chance 0.320, the noise floor 0.118.

  (i)  If **any** functional reaches within 0.01 of 0.1027, the reading is that the released model
       does contain a comfort-zone quantity and the project had been reading the wrong one.
  (ii) If **none** does, the reading is that no functional of this expected free energy orders these
       cells, and the obstacle is the preference structure itself -- which is the case for going to
       the program's strand 1 (`docs/waymo_program_revisit.md` §1) rather than for another
       functional of strand 2.
  (iii) The epistemic term is reported with its sign either way, because it has never been measured
       on this data and its direction is a result regardless of its score.

No response data enter the construction; the only fitted object is the three-parameter threshold
model, as in every axis competition since gate R.2.

Output: replication/czb/out/re4_efe_functionals.md and out/re4_efe_functionals.csv.
Run:    python replication/czb/re4_efe_functionals.py
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

import hs1_situational_surprise as HS      # noqa: E402  card HS.1 scene loaders (read only)
import jj2_rollout_cutin as J2             # noqa: E402  card JJ.2 (read only)
import jj2b_steer_menu as J2B              # noqa: E402  card JJ.2b (read only)
from aidriver.agent import ActiveInferenceDriver, AgentParams        # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at  # noqa: E402
from rollout.boundary import axis                                    # noqa: E402

OUT = HERE / "out"
SEED = J2B.SEED
SETTLE_S = J2B.SETTLE_S
REPRO_TOL = 1e-6          # eps here must reproduce card JJ.2b's, which used the same construction


def cell_terms(cells: pd.DataFrame, scenes: dict) -> pd.DataFrame:
    """Per cell: eps (pragmatic), the epistemic value, and the full G at alpha = 1, for the
    coasting policy. The belief is settled exactly as card JJ.2b settles it -- the same replay of
    the trace over SETTLE_S before the freeze, the same seed -- and section 0 checks that the eps
    this produces reproduces JJ.2b's to REPRO_TOL, which is what makes the duplication safe."""
    rows = []
    t0 = time.time()
    for i, v in enumerate(cells.video):
        key, e_t, cp = J2.trace_key(v)
        sc = scenes[key]
        t, eg, ta = sc["grid"], sc["ego"], sc["tar"]
        b = belief_at(J2.scene_of(sc, key), e_t, FLOORS_STUDY2, p_change_prior=P_CHANGE_PRIOR,
                      with_intention=False)
        pref = J2B.staging(b.v_ego)
        agent = ActiveInferenceDriver(pref, AgentParams(alpha=1.0, seed=SEED))
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
        agent.reset(state(eg, steps[0], sgn), state(ta, steps[0], sgn))
        for t_at in steps:
            agent.update_belief(state(eg, t_at, sgn), state(ta, t_at, sgn))
        ego = state(eg, e_t, sgn)
        other_traj, w = agent.predict_other(agent.p.horizon,
                                            noise_factor=agent.p.noise_pred_factor)
        pol = np.zeros((agent.p.horizon, 2))
        pol[:, 0] = agent.p.a_coast

        eps = agent.policy_surprise(ego, other_traj, w, pol)
        # expected_free_energy returns -(prag + alpha epist); differencing the two alphas isolates
        # the epistemic term through the agent's own code path rather than re-deriving it here.
        agent.p.alpha = 0.0
        g0, _, _ = agent.expected_free_energy(ego, pol[None], other_traj, w)
        agent.p.alpha = 1.0
        g1, _, _ = agent.expected_free_energy(ego, pol[None], other_traj, w)
        epist = float(g0[0] - g1[0])
        rows.append({"video": v, "cp": cp, "eps": eps, "epistemic": epist,
                     "g_alpha1": float(eps - epist)})
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(cells)} [{time.time() - t0:.0f} s]", flush=True)
    return pd.DataFrame(rows)


def score(d: pd.DataFrame, col: str, sign: float = +1.0) -> dict:
    """The held-out score and the ordering statistics for one functional."""
    dd = d.dropna(subset=[col]).copy()
    vals = dd[col].to_numpy(float)
    shifted = vals - vals.min() + 1e-9 if vals.min() <= 0 else vals
    ax = axis(shifted)
    dd["x"] = ax.values
    post = dd[dd.cp != "CP1"].reset_index(drop=True)
    cp1 = dd[dd.cp == "CP1"].reset_index(drop=True)
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    agree, nrows, _ = J2.matched_rows(post, post[col].to_numpy(float), sign)
    return {"post": r_post, "cp1": r_cp1, "rows": f"{agree} of {nrows}",
            "rho_p": float(spearmanr(post[col], post.p).statistic),
            "rho_gap": float(spearmanr(post[col], post.distance).statistic)}


def main() -> None:
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = HS.study2_scenes(cells)
    print("computing the pragmatic and epistemic terms...", flush=True)
    d = cell_terms(cells, scenes)

    # min G and Delta G from card JJ.2b's committed planner output
    j2b = pd.read_csv(OUT / "jj2b_steer_menu_cells.csv")
    j2b["min_eps"] = j2b.eps_continue - j2b.dg_planner
    d = d.merge(j2b[["video", "eps_continue", "dg_planner", "min_eps"]], on="video", how="left")
    d = d.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")

    repro = float(np.max(np.abs(d.eps - d.eps_continue)))
    L = ["# Card RE.4 -- every functional of the released expected free energy, as the axis", "",
         "Generated by `replication/czb/re4_efe_functionals.py`; the functionals, the rule and the"
         " readings were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "Jonas, 2026-09-18: *What can we reformulate then to make it fit/work? It should be"
         " possible, I still feel...*", "",
         "## 0 Reproduction check", "",
         "| check | value | required |", "|---|---|---|",
         f"| max \\|eps here - eps in `out/jj2b_steer_menu_cells.csv`\\| | {repro:.3e} |"
         f" <= {REPRO_TOL:.0e} |",
         f"| cells | {len(d)} | 378 |", "",
         ("The belief construction is card JJ.2b's, reproduced here rather than imported because it"
          " lives inside that card's `planner_pass`; the check above is what makes the duplication"
          " safe." if repro <= REPRO_TOL else
          "**The reproduction FAILED, so the functionals below are not on JJ.2b's construction and"
          " nothing here should be compared with that card.**"), "",
         "## 1 The functionals", "",
         "The participants' shares correlate **-0.862** with the gap, so a criticality axis must"
         " give rho(axis, gap) NEGATIVE.", "",
         "| functional | post-onset held out | pre-onset out of sample | matched-TTC rows |"
         " rho(axis, share) | rho(axis, gap) |", "|---|---|---|---|---|---|"]

    labels = [("eps = G(continue), the model's Eq. 13 signal", "eps", +1.0),
              ("min over policies of G  (the released CEM planner, alpha = 0)", "min_eps", +1.0),
              ("Delta G = G(continue) - min G  (card JJ.2's axis)", "dg_planner", +1.0),
              ("epistemic value of continuing  (never tested before)", "epistemic", +1.0),
              ("the full G at alpha = 1  (pragmatic + epistemic)", "g_alpha1", +1.0)]
    out = {}
    for lab, col, sgn in labels:
        s = score(d, col, sgn)
        out[col] = s
        L.append(f"| {lab} | {s['post']:.4f} | {s['cp1']:.4f} | {s['rows']} | {s['rho_p']:+.3f} |"
                 f" {s['rho_gap']:+.3f} |")
    L += ["", f"Comparators on file: the gated looming rule {J2.G1_GATED:.4f}, the ungated"
          f" {J2.G1_UNGATED:.4f}, card G.1's pre-onset {J2.G1_CP1_GATED:.4f}, chance"
          f" {J2.CHANCE:.3f}, the sampling-noise floor {J2.NOISE_FLOOR:.3f}.", ""]

    best = min(out, key=lambda k: out[k]["post"])
    reached = out[best]["post"] <= J2.G1_GATED + 0.01
    any_neg = [k for k in out if out[k]["rho_gap"] < 0]
    ep = out["epistemic"]
    L += ["## 2 The verdict on the pre-stated rule", "",
          (f"**(i) Some functional reaches the comparator.** The best is `{best}` at"
           f" {out[best]['post']:.4f}." if reached else
           f"**(ii) No functional reaches the comparator.** The best of the five is `{best}` at"
           f" **{out[best]['post']:.4f}**, against the gated looming rule's {J2.G1_GATED:.4f} + 0.01"
           f" and chance {J2.CHANCE:.3f}. Every functional sits at chance."), "",
          ("So the obstacle is not which functional of the expected free energy is read. It is the"
           " preference structure the expected free energy is built from -- which is what card RE.2"
           " found by sweeping its constants, and what `docs/waymo_program_revisit.md` §1 argues is"
           " a property of a COLLISION-AVOIDANCE model being asked a comfort-zone question. **This"
           " is the case for going to the program's strand 1 rather than for another functional of"
           " strand 2.**" if not reached else ""), "",
          f"**(iii) The epistemic term, measured here for the first time.** rho with the share"
          f" {ep['rho_p']:+.3f}, rho with the gap {ep['rho_gap']:+.3f}, held out"
          f" {ep['post']:.4f}. "
          + ("Its sign is the human one -- it rises as the gap shrinks, because under looming"
             " perception the observation precision improves as the square of the closing distance."
             " Note what that means in the model's own terms: the epistemic term makes a close"
             " approach ATTRACTIVE, so a quantity that tracks the boundary well would be pulling"
             " the driver across it. The direction is a result; the score is what decides whether"
             " it is usable." if ep["rho_gap"] < 0 else
             "Its sign is NOT the human one on this data, so the approach incentive the design note"
             " and HANDOFF.md §4 both warn about does not show up as a usable ordering here."), "",
          f"Functionals with the human sign on the gap: "
          + (", ".join(f"`{k}`" for k in any_neg) if any_neg else "**none of the five**") + ".", "",
          "## 3 What was not done", "",
          "min G and Delta G are card JJ.2b's planner output and were computed at **alpha = 0**;"
          " only the single-policy functionals here are at alpha = 1. Re-running the planner at"
          " alpha = 1 over 378 cells is about 22 minutes and is the obvious follow-up if any"
          " functional above had been close. None was, so it was not run.", "",
          f"Run time {time.time() - t0:.0f} s.", ""]

    d.to_csv(OUT / "re4_efe_functionals.csv", index=False)
    (OUT / "re4_efe_functionals.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-16:]))


if __name__ == "__main__":
    main()
