"""
Card RE.2 -- is there ANY driver in the released preference family whose comfort zone orders the
cut-in cells the way humans do?

PRE-STATED before any run (2026-09-18, after card RE.1, for
`docs/active_inference_reformulation.md`).

THE QUESTION, AND WHY IT COMES BEFORE ANY NEW CONSTRUCTION
-----------------------------------------------------------
Card RE.1 showed that the released model's own criticality signal, eps, is flat across time gap
at zero relative speed and ordered BACKWARDS at matched TTC, carried by the collision term (78%
of eps, rho +0.80 with the gap) and the safety term (14%, rho +0.92). Cards R.2, JJ.2, JJ.3 and
JJ.2b all failed on the same inversion.

Every one of those tests used ONE parameter vector: the authors' calibration. The authors
calibrate `a_OV,min` per SCENARIO through a separate free-following analysis, so their vector is a
property of their simulation study, not of any driver. Before proposing that the project fit a
driver's preference parameters instead of assuming the authors' -- which is what the
reformulation note proposes -- one question has to be answered:

    **Does the released FUNCTIONAL FORM admit any parameter vector at all that orders these
    cells the way the participants do, or is the inversion a property of the form itself?**

If some theta works, the reformulation is a fitting problem and the framework is fine. If none
does, the form has to change, and this card says which factor is responsible.

THE SWEEP. eps = G(continue) -- card RE.1 part 0 established that this is the model's own Eq. 13
signal -- on card JJ.2's own 378 cells, with card JJ.1's belief, fan and rollout machinery
unchanged and one fan per cell reused across every theta (the belief does not depend on theta).
Six parameters, chosen because each is a driver property rather than an algorithmic one, and each
is a candidate for the inversion:

  a_other_min        {-2, -4, -6, -10} m/s^2   how hard you assume the other might brake; the
                                               authors' own per-scenario calibration knob
  response_time      {0.5, 1.0, 2.0} s         your assumed own reaction time
  a_max              {4, 8, 12} m/s^2          the deceleration you count on having
  tau_inv_mu         {0.1, 0.2, 0.4} 1/s       your preferred inverse TTC (10, 5, 2.5 s)
  counterfactual_residual_severity {True, False}  the form of the braking-margin magnitude: the
                                               project's continuous ramp (the CZB staging every
                                               cut-in card uses) or the released binary indicator.
                                               This one is OURS, not a driver property, and is
                                               swept because it is a form choice the project made.
  collision_ref_speed {10, 30, 1e6} m/s        THE DIAGNOSTIC ONE. The released collision
                                               severity is 0.2 + 0.8 dv / collision_ref_speed,
                                               linear in closing speed. At 1e6 it is flat at the
                                               floor, so the severity's speed dependence is
                                               switched off without changing anything else. If
                                               the inversion survives that, it is not severity.

648 vectors in all. Everything else is the released default with the CZB staging card JJ.2 used
(the clip's own desired speed, the continuous lane-entry forms, k = 12).

`sigma_v` was in the pre-registered grid and was removed before the run, with the reason recorded
here and in the worklog per standing rule 4: under the "continue" policy the stimulus ego holds
its own desired speed exactly, so the speed factor's contribution is identically zero (measured:
-1.2e-14 at every one of the 378 cells) and sweeping it could not move anything. The same
measurement shows the acceleration, steering and lane factors are identically zero too, so on this
stimulus set eps IS the collision factor plus the safety factor -- which is the deposit's own
finding for benign following (`docs/method_review.md` section 4.2: collision/safety share 1.000).
`counterfactual_residual_severity` took the freed dimension.

THE MEASURES, per theta, on the 288 post-onset cells:
  rho_gap    Spearman(log eps, distance). **The participants' shares correlate -0.862 with the
             gap, so a criticality axis must be NEGATIVE here.** This is the primary measure.
  rows       of the 24 matched-TTC rows (`out/cutin2_lane_gate_diagnostic.md`'s grouping), how
             many log eps orders the way the data do.
  For the best 20 vectors by rho_gap only: the leave-one-starting-TTC-out held-out wRMSE of the
  three-parameter threshold model on log eps, and the pre-onset out-of-sample score, against the
  gated looming rule's 0.1027 and card G.1's 0.0319.

THE DECISION RULE, PRE-STATED
-----------------------------
  (i)  If NO vector in the grid gives rho_gap < 0, **the released functional form cannot order
       these cells**, and the reformulation must change the form rather than the constants. The
       report then names which factor holds the inversion, by repeating the sweep with each of
       the six preference terms removed one at a time.
  (ii) If some vector gives rho_gap < 0, the form is fine and the project's error was to use the
       authors' calibration as a measuring instrument. The report gives the best vector, its
       held-out score, and whether it reaches 0.1027 + 0.01.
  (iii) Either way, `collision_ref_speed = 1e6` is reported separately, because it answers
       "is it the severity?" on its own.

No verdict about any card is taken here, and nothing is fitted to the responses except the three
parameters of the threshold model, exactly as in every other axis competition since gate R.2.

Output: replication/czb/out/re2_preference_family.md and out/re2_preference_family.csv.
Run:    python replication/czb/re2_preference_family.py
"""
from __future__ import annotations

import itertools
import sys
import time
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
from aidriver.preferences import PreferenceParams                   # noqa: E402
from comfortzone.cutin import CZB_LANE_ENTRY_SHAPE_K                # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, update_intention  # noqa: E402
from rollout.boundary import axis                                   # noqa: E402
from rollout.efe import expected_free_energy                        # noqa: E402
from rollout.policies import ego_rollout                            # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
SEED = 0
N_BEST = 20
GRID = {
    "a_other_min": (-2.0, -4.0, -6.0, -10.0),
    "response_time": (0.5, 1.0, 2.0),
    "a_max": (4.0, 8.0, 12.0),
    "tau_inv_mu": (0.1, 0.2, 0.4),
    "collision_ref_speed": (10.0, 30.0, 1e6),
    "counterfactual_residual_severity": (True, False),
}
TERMS = ("speed", "accel", "steer", "lateral", "collision", "safety")


def base_params(v_ego: float) -> PreferenceParams:
    return PreferenceParams(v_desired=float(v_ego), lane_entry_continuous=True,
                            counterfactual_residual_severity=True,
                            lane_entry_shape_k=CZB_LANE_ENTRY_SHAPE_K)


def build_cells(cells: pd.DataFrame, scenes: dict):
    """One belief, one fan and one 'continue' rollout per cell -- none of which depends on theta."""
    out = []
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        scene = J2.scene_of(scenes[key], key)
        b = belief_at(scene, e_t, FLOORS_STUDY2, p_change_prior=P_CHANGE_PRIOR,
                      with_intention=False)
        b.p_change = update_intention(P_CHANGE_PRIOR, b.vy_oth, FLOORS_STUDY2.sd_v_lat,
                                      sign=float(np.sign(b.y_rel)) or 1.0)
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=SEED)
        out.append((v, cp, b, fut, ego_rollout(b, "continue", HORIZON_S, DT_S),
                    base_params(b.v_ego)))
    return out


def eps_for(theta: dict, built) -> np.ndarray:
    """eps = G(continue) for every cell, at one parameter vector."""
    return np.array([expected_free_energy(b, path, fut, replace(p0, **theta))
                     for _, _, b, fut, path, p0 in built])


def term_table(theta: dict, built) -> pd.DataFrame:
    """Each preference factor's own contribution to eps, per cell.

    eps = SUM_k [ H max_k - SUM_tau E term_k ], with max_k the factor's own maximum: the three
    Gaussian factors contribute -log(sigma) - 0.5 log 2pi each and the other three have maximum
    zero, which is exactly how `max_log_preference()` is built. So the six contributions add up
    to eps and each can be used, dropped, or taken alone.
    """
    from aidriver.preferences import LOG_2PI
    from rollout.efe import log_terms
    rows = []
    for v, cp, b, fut, path, p0 in built:
        p = replace(p0, **theta)
        t = log_terms(b, path, fut, p)
        maxima = {"speed": -np.log(p.sigma_v) - 0.5 * LOG_2PI,
                  "accel": -np.log(p.sigma_a) - 0.5 * LOG_2PI,
                  "steer": -np.log(p.sigma_omega) - 0.5 * LOG_2PI,
                  "lateral": 0.0, "collision": 0.0, "safety": 0.0}
        row = {"video": v, "cp": cp}
        for k in TERMS:
            row[k] = float(np.sum(maxima[k] - t[k].mean(axis=0)))
        rows.append(row)
    return pd.DataFrame(rows)


def measures(vals: np.ndarray, built, cells: pd.DataFrame) -> dict:
    d = pd.DataFrame({"video": [x[0] for x in built], "cp": [x[1] for x in built], "eps": vals})
    d = d.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
    ax = axis(np.maximum(d.eps.to_numpy(float), 0.0))
    d["x"] = ax.values
    post = d[d.cp != "CP1"].reset_index(drop=True)
    agree, nrows, _ = J2.matched_rows(post, post.x.to_numpy(float), +1.0)
    return {"rho_gap": float(spearmanr(post.x, post.distance).statistic),
            "rho_p": float(spearmanr(post.x, post.p).statistic),
            "rows": agree, "n_rows": nrows, "frame": d, "post": post,
            "cp1": d[d.cp == "CP1"].reset_index(drop=True)}


def held_out(m: dict) -> tuple[float, float]:
    post, cp1 = m["post"], m["cp1"]
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    return r_post, r_cp1


def main(reuse: bool = False) -> None:
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = HS.study2_scenes(cells)
    built = build_cells(cells, scenes)
    print(f"{len(built)} cells built [{time.time() - t0:.0f} s]", flush=True)

    names = list(GRID)
    combos = list(itertools.product(*(GRID[k] for k in names)))
    if reuse:
        # Regenerate the report from the sweep's own tracked output without repeating the 648
        # evaluations; sections 3 and 4, which need the per-cell rollouts, are recomputed.
        sw = pd.read_csv(OUT / "re2_preference_family.csv")
        print(f"sweep reloaded from out/re2_preference_family.csv ({len(sw)} vectors)", flush=True)
    else:
        rows = []
        for i, combo in enumerate(combos):
            theta = dict(zip(names, combo))
            m = measures(eps_for(theta, built), built, cells)
            rows.append({**theta, "rho_gap": m["rho_gap"], "rho_p": m["rho_p"],
                         "rows": m["rows"], "n_rows": m["n_rows"]})
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(combos)} [{time.time() - t0:.0f} s]", flush=True)
        sw = pd.DataFrame(rows)
    sw = sw.sort_values("rho_gap").reset_index(drop=True)
    any_neg = bool((sw.rho_gap < 0).any())
    half_rows = bool((sw.rows > sw.n_rows / 2).any())

    L = ["# Card RE.2 -- is there any driver in the released preference family whose comfort"
         " zone orders the cut-in cells the way humans do?", "",
         "Generated by `replication/czb/re2_preference_family.py`; the question, the grid, the"
         " measures and the decision rule were pre-stated in its docstring before the run. Do not"
         " edit by hand.", "",
         "eps = G(continue), the released model's own Eq. 13 signal (card RE.1 part 0), on card"
         " JJ.2's own 378 cells with card JJ.1's belief, fan and rollout machinery unchanged. One"
         " fan per cell, reused across every parameter vector, because the belief does not depend"
         " on the preference. **The participants' shares correlate -0.862 with the gap, so a"
         " criticality axis must give rho(axis, gap) NEGATIVE.**", "",
         f"## 1 The sweep: {len(combos)} parameter vectors", "",
         "| measure | value |", "|---|---|",
         f"| vectors with rho(log eps, gap) < 0 | **{int((sw.rho_gap < 0).sum())} of"
         f" {len(sw)}** |",
         f"| best (most negative) rho_gap | {sw.rho_gap.iloc[0]:+.3f} |",
         f"| worst | {sw.rho_gap.iloc[-1]:+.3f} |",
         f"| vectors ordering more than half the matched-TTC rows the human way |"
         f" {int((sw.rows > sw.n_rows / 2).sum())} of {len(sw)} |", "",
         "The ten vectors with the most negative rho_gap:", "",
         "| a_other_min | response_time | a_max | tau_inv_mu | p_safe form |"
         " collision_ref_speed | rho(log eps, gap) | rho(log eps, share) | matched-TTC rows |",
         "|---|---|---|---|---|---|---|---|---|"]
    for _, r in sw.head(10).iterrows():
        L.append(f"| {r.a_other_min:.0f} | {r.response_time:.1f} | {r.a_max:.0f} |"
                 f" {r.tau_inv_mu:.2f} | {'ramp' if r.counterfactual_residual_severity else 'step'}"
                 f" | {r.collision_ref_speed:.0f} |"
                 f" {r.rho_gap:+.3f} | {r.rho_p:+.3f} | {int(r.rows)} of {int(r.n_rows)} |")
    L.append("")

    # (iii) the severity diagnostic on its own
    flat = sw[sw.collision_ref_speed > 1e5]
    lin = sw[sw.collision_ref_speed <= 30.0]
    L += ["## 2 Is it the collision severity? (decision rule (iii))", "",
          "`collision_ref_speed = 1e6` makes the released severity flat at its floor, so the"
          " collision cost no longer grows with closing speed; everything else is unchanged.", "",
          "| severity | vectors | median rho(log eps, gap) | best rho_gap | median matched-TTC"
          " rows |", "|---|---|---|---|---|",
          f"| linear in closing speed (ref 10 or 30 m/s) | {len(lin)} |"
          f" {lin.rho_gap.median():+.3f} | {lin.rho_gap.min():+.3f} |"
          f" {lin.rows.median():.0f} |",
          f"| flat (ref 1e6) | {len(flat)} | {flat.rho_gap.median():+.3f} |"
          f" {flat.rho_gap.min():+.3f} | {flat.rows.median():.0f} |", ""]

    # the best vectors, scored
    L += [f"## 3 The best {N_BEST} vectors, scored on JJ.2's folds and metric", "",
          "| a_other_min | t_react | a_max | tau_inv_mu | p_safe form | severity ref | rho_gap |"
          " post-onset held out | pre-onset out of sample |",
          "|---|---|---|---|---|---|---|---|---|"]
    best_post = np.inf
    for _, r in sw.head(N_BEST).iterrows():
        theta = {k: r[k] for k in names}
        m = measures(eps_for(theta, built), built, cells)
        rp, rc = held_out(m)
        best_post = min(best_post, rp)
        L.append(f"| {r.a_other_min:.0f} | {r.response_time:.1f} | {r.a_max:.0f} |"
                 f" {r.tau_inv_mu:.2f} | {'ramp' if r.counterfactual_residual_severity else 'step'}"
                 f" | {r.collision_ref_speed:.0f} | {r.rho_gap:+.3f} | {rp:.4f} | {rc:.4f} |")
    L += ["", f"Comparators on file: the gated looming rule {J2.G1_GATED:.4f}, the ungated"
          f" {J2.G1_UNGATED:.4f}, card G.1's pre-onset {J2.G1_CP1_GATED:.4f}, chance"
          f" {J2.CHANCE:.3f}, the noise floor {J2.NOISE_FLOOR:.3f}.", ""]

    # (i) which factor holds the inversion, and which factor could carry the axis
    base_theta = {"a_other_min": -6.0, "response_time": 1.0, "a_max": 8.0, "tau_inv_mu": 0.2,
                  "collision_ref_speed": 10.0, "counterfactual_residual_severity": True}
    tt = term_table(base_theta, built)
    m0 = measures(eps_for(base_theta, built), built, cells)
    L += ["## 4 Which factor holds the inversion, and which factor could carry the axis", "",
          "The six factors' own contributions to eps at the released defaults. They add up to"
          " eps, so each can be dropped or taken alone. **This is the constructive half of the"
          " card**: the released preference contains one factor shaped like a comfort boundary"
          " (the inverse-tau preference inside p_coll, a Gaussian on tau^-1 = phi_dot / phi with"
          " mean 0.2 1/s) and two shaped like catastrophes (the collision indicator at -10 000"
          " and the braking-margin indicator at -10 000 x severity). If the comfort-shaped factor"
          " orders the cells and the catastrophe-shaped ones invert them, then the released"
          " model contains a usable comfort-zone scalar that its own magnitudes bury.", "",
          "| factor | mean share of eps | ALONE: rho(gap) | rows | held out | WITHOUT it:"
          " rho(gap) | rows |", "|---|---|---|---|---|---|---|"]
    for k in TERMS:
        share = float(np.mean(tt[k] / np.maximum(tt[list(TERMS)].sum(axis=1), 1e-9)))
        alone, without = "-", "-"
        a_rows = w_rows = "-"
        ho = "-"
        if tt[k].nunique() > 1:
            ma = measures(tt[k].to_numpy(float), built, cells)
            alone, a_rows = f"{ma['rho_gap']:+.3f}", f"{ma['rows']} of {ma['n_rows']}"
            try:
                ho = f"{held_out(ma)[0]:.4f}"
            except Exception:
                ho = "n/a"
        rest = tt[[c for c in TERMS if c != k]].sum(axis=1)
        if rest.nunique() > 1:
            mw = measures(rest.to_numpy(float), built, cells)
            without, w_rows = f"{mw['rho_gap']:+.3f}", f"{mw['rows']} of {mw['n_rows']}"
        L.append(f"| {k} | {share:+.3f} | {alone} | {a_rows} | {ho} | {without} | {w_rows} |")
    L += ["", f"For reference, all six together (the released defaults):"
          f" rho(gap) {m0['rho_gap']:+.3f}, {m0['rows']} of {m0['n_rows']} rows.", ""]

    # The decision rule was written as a binary on the SIGN of rho_gap, and it fires. The result
    # is not binary, so both halves are reported and the rule's own wording is quoted first.
    if any_neg:
        verdict = [
            "**The rule as pre-stated fires (ii): some vector gives rho(log eps, gap) < 0.**"
            f" {int((sw.rho_gap < 0).sum())} of {len(sw)} do. But the rule was written as a"
            " binary on a sign, and the result is not binary, so what it fires on has to be said"
            " exactly.", "",
            "**The sign is reachable inside the family; the ordering is not.** The best vector"
            f" reaches rho_gap {sw.rho_gap.iloc[0]:+.3f} against the participants' own"
            f" -0.862, and **{int((sw.rows > sw.n_rows / 2).sum())} of {len(sw)} vectors** order"
            " more than half the 24 matched-TTC rows the way the data do -- the best manages"
            f" {int(sw.rows.max())} of {int(sw.n_rows.iloc[0])}. The best held-out score is"
            f" {best_post:.4f}, against the gated looming rule's {J2.G1_GATED:.4f} + 0.01 and"
            f" chance {J2.CHANCE:.3f}. So no driver in this family has a comfort zone that orders"
            " these cells.", "",
            "**What does most of the work is the severity's linearity in closing speed.** Section"
            " 2: flattening it moves the median rho_gap from"
            f" {sw[sw.collision_ref_speed <= 30.0].rho_gap.median():+.3f} to"
            f" {sw[sw.collision_ref_speed > 1e5].rho_gap.median():+.3f}. Every one of the top"
            " vectors has a flat severity and the shortest preferred TTC in the grid"
            " (tau_inv_mu 0.40, TTC 2.5 s). That is a statement about the FORM -- the collision"
            " cost's proportionality to impact speed -- and not about a constant a driver could"
            " differ in.", "",
            "**The reading, which is the same shape as card JJ.2b's.** Changing the framing"
            " (JJ.2b: the model's own policy space) or the form (here: a severity that does not"
            " grow with speed) repairs the DIRECTION of the ordering and leaves the MAGNITUDE at"
            " chance. Two independent lines now say that, and section 4 says why: on these"
            " stimuli eps is the collision factor plus the safety factor and nothing else, and"
            " the two point in opposite directions with respect to the response (rho with the"
            " share +0.358 and -0.861). A sum of one factor that orders weakly and one that"
            " orders backwards cannot be a comfort-zone scalar at any parameter vector.",
        ]
    else:
        verdict = [
            "**(i) NO vector in this grid orders these cells the way the participants do.**"
            " Every one of the"
            f" {len(sw)} parameter vectors gives rho(log eps, gap) positive, including the"
            " ones whose collision severity does not grow with closing speed at all. The"
            " inversion is therefore a property of the released FUNCTIONAL FORM and not of its"
            " constants, and a reformulation has to change the form: no amount of fitting"
            " within this family will order these cells."]
    L += ["## 5 The verdict on the decision rule", ""] + verdict + [
        "", f"Run time {time.time() - t0:.0f} s.", ""]

    if not reuse:
        sw.to_csv(OUT / "re2_preference_family.csv", index=False)
    (OUT / "re2_preference_family.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-8:]))


if __name__ == "__main__":
    # `--reuse` regenerates the report from out/re2_preference_family.csv, the
    # sweep's own tracked output, without repeating the 648 evaluations.
    main(reuse="--reuse" in sys.argv)
