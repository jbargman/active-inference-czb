"""
Card S1.6 -- admissibility: strand 1's absolute conflict preference as a constraint on the menu,
and what that does to Delta G.

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22.

WHERE THE CARD COMES FROM
-------------------------
Card S1.4 implemented strand 1's conflict preference ("a categorical distribution representing an
absolute preference over no-conflict", Engström et al. 2024) as a large finite constant and found
the constant consequential (-300 / -1 000 / -3 000 nats gave 0.3244 / 0.3221 / 0.2864). Query
S14.Q2 proposed excluding colliding policies from the menu instead; Jonas, 2026-09-22: *"I think we
should try S14.Q2 as you seem to propose."* And, the same night, of the sentence "the minimum is
then over admissible policies only": *"what are the implications of that?"* Section 0 of the
report is the answer, with the counts that back it.

THE IMPLICATIONS, worked out before the run (`src/rollout/admissible.py` has the long form)
--------------------------------------------------------------------------------------------
Under admissibility the conflict term leaves G: a policy is allowed or it is not. G is then the
COMFORT cost alone, which for the stimulus ego under `continue` is exactly zero. So
  * while `continue` is admissible, Delta G = 0: the quantity is silent, which is a GATE;
  * once it is not, G(continue) is not finite, and what remains defined is
        C = min over admissible pi of G_comfort(pi),
    the comfort price of staying conflict-free. Over a menu of constant decelerations G_comfort
    is monotone in the deceleration, so C is a function of the MILDEST ADMISSIBLE DECELERATION
    a*. **Admissibility turns Delta G into a required deceleration in nats, taken against the
    predictive fan.** The strand-1 line and the comfort-margin line (cards S1.1, S1.5) become one;
  * the constant that S1.4 could not fix (the collision cost) is replaced by one that can be
    motivated: the tolerance alpha on the probability of conflict. alpha = 0 is the literal
    "absolute", and on a fan with unbounded support it is a statement about the sample size;
  * the verdict becomes a statement about the fan's TAILS, where card GM.1a found the fan five
    times too wide. An expected cost averages over the fan; admissibility reads its edge.

A FLAW FOUND IN CARD JJ.1'S FAN WHILE WRITING THE PROPERTY TESTS, before any score
----------------------------------------------------------------------------------
Under the "keeping" intention JJ.1 clips the other's CENTRE at the ego's lane edge, 1.75 m from the
ego's lane centre. The released collision box is |dy| <= 1.15 x 1.72 = 1.98 m. So a vehicle that is
CERTAIN to keep its lane drifts (sd 0.33 m/s over 6 s) into the box of an ego passing in its own
lane in about a fifth of the sampled futures (`tests/test_admissible.py`: 0.19 at a lateral
offset of 3.5 m, p_change = 0). Under an expected cost that is a bias; under admissibility it is
fatal, because `continue` is then never admissible beside anything. `sample_futures` gained a flag,
`keep_body_in_lane` (default False = JJ.1's fan bit for bit), which clips the centre at the lane
edge plus half the other's width, so that the other's BODY keeps its lane.

**The primary arm uses the corrected fan.** That is a choice made on geometry, before any score
was computed on either fan, and JJ.1's fan is scored beside it. Section 4 then asks the question
the flaw raises about the earlier cards: does it change card JJ.2's and S1.4's Delta G?

WHAT IS COMPUTED
----------------
Card S1.4's construction, imported and unchanged except as stated: the same 378 cells, the same
belief at the same freeze with the same intention update, the same fan constants and seed, the same
folds and metric. Preference: strand 1's tolerances (sigma_v 1.0 m/s, sigma_a 0.5 m/s^2, Engström
et al. 2024 Table 2, as S1.4), no braking-margin term, NO collision cost. Menu: `continue` and
constant decelerations to the released a_max = 8 m/s^2 in steps of 0.25 (33 policies), because the
four-policy menu of ruling JJ1.Q1 would make a* a four-level step function. Axis: log C with the
zero rule of design note section 1.5 (`rollout.boundary.axis`); log a* is reported beside it.

  PRIMARY   corrected fan, alpha = 0, no delay, n = 200 futures, seed 0.
  alpha     {0, 0.01, 0.05, 0.10, 0.20}. 0 is the literal reading and the primary; none is chosen
            by its score. 0.10 and 0.20 lie above the lane-change prior p0 = 0.07 and the others
            below it, which is the contrast that matters (prediction 2).
  delay     {0, 1.0 s}: brake from the freeze, or after the released response_time. The delayed
            arm is card S1.5's `holds` demand taken against the fan.
  fan       corrected / JJ.1's as built.
  n, seed   n in {100, 200, 400} at seed 0; seeds {0, 1, 2} at n = 200 (rule (d)).

THE RULES
---------
  (a) AXIS. Credited if the post-onset held-out score is below the gap threshold's 0.1522 -- card
      S1.4's rule (b), verbatim, since this card finishes that one. Also read against 0.1422, the
      stricter bar card S1.5 uses.
  (b) EMERGENCE. The full post-onset fit applied to the 90 pre-onset cells scores below 0.05 with
      no gate term (card JJ.2's rule (b)).
  (c) ORDERING. Positive rank correlation with the share in at least 12 of the 24 matched-TTC rows
      (card RE.2's criterion).
  (d) MONTE CARLO. alpha = 0 depends on the sample. The primary's post-onset score must stay
      within 0.01 across n in {100, 200, 400} and across seeds {0, 1, 2}; otherwise the verdict is
      reported as NOT STABLE whatever (a) to (c) say.
  VERDICT: ADOPT if (a), (b), (d). AXIS ONLY if (a), (d), not (b). **GATE ONLY** if (b) and (d) hold
      and (a) fails: the admissible set supplies the gate and its price is not the axis. NOT
      CREDITED otherwise.
  SECTION 4's RULE. Card S1.4's arms 1 (released) and 4 (strand 1, flat cost) are rescored on the
      corrected fan. If either arm's post-onset or pre-onset score moves by more than 0.01 from
      S1.4's own (0.3202 / 0.5381 and 0.3221 / 0.2790), the clip was load-bearing for JJ.2 and
      S1.4 and query S16.Q1 is a blocker on how those cards are read. JJ.2's DROP itself changes
      only if arm 1 comes within 0.01 of the gated looming rule's 0.1027 (its rule (a)).

PREDICTIONS, written before the run
-----------------------------------
What I had seen: card S1.5's primary `holds` arm, which finished while this was being written
(0.2550 held out), and the synthetic scenes of the property tests. No S1.6 quantity on any cell.
  1. Rule (a) FAILS, somewhere in 0.22 to 0.29. With the lead holding its speed in the fan's
     centre, a* is the kinematic required deceleration, and within a matched-TTC row that is
     ANTI-ordered with the response (a smaller gap at the same TTC is a smaller closing speed).
     The fan's longitudinal tail adds some sensitivity to the gap, not enough.
  2. Rule (b) FAILS at alpha below the prior 0.07 and may HOLD above it. Pre-onset, the intention
     posterior sits near the prior, so about 7% of futures change lanes; `continue` collides in
     those, which makes it inadmissible at alpha 0 to 0.05 and admissible at 0.10 and 0.20. **If
     that happens the gate has emerged as "P(lane change) exceeds my tolerance"**, which is the
     emergence card JJ.2 looked for in Delta G and did not find.
  3. JJ.1's fan, as built: `continue` inadmissible in nearly every cell at every alpha up to
     0.10, pre-onset included.
  4. Section 4: arm 1's pre-onset score improves on the corrected fan, because the lane-keeping
     futures stop colliding; whether by more than 0.01 I do not know. The post-onset score stays at
     chance.

Output: replication/czb/out/s16_admissibility.md, out/s16_admissibility_cells.csv
Run:    python replication/czb/s16_admissibility.py
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

import hs1_situational_surprise as HS      # noqa: E402  card HS.1 scene loaders (read only)
import jj2_rollout_cutin as J2             # noqa: E402  card JJ.2 (read only)
import s14_strand1_preference as S14       # noqa: E402  card S1.4 (read only)
from aidriver.preferences import PreferenceParams  # noqa: E402
from rollout.admissible import A_MAX_RELEASED, MENU_STEP, price_of_safety  # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, update_intention  # noqa: E402
from rollout.boundary import axis, delta_g  # noqa: E402
from rollout.efe import g_by_policy  # noqa: E402
from rollout.policies import cutin_menu_paths  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
GAP_RULE, GAP_RULE_STRICT = 0.1522, 0.1422
LOOMING_GATED, LOOMING_UNGATED, G1_CP1 = 0.1027, 0.1137, 0.0319   # out/cutin2_gate.md
CHANCE = 0.320
CP1_CRIT = 0.05
ROWS_CRIT = 12
MC_TOL = 0.01
S14_ARM1 = (0.3202, 0.5381)     # out/s14_strand1_preference.md section 1: post, pre-onset
S14_ARM4 = (0.3221, 0.2790)
ALPHAS = (0.0, 0.01, 0.05, 0.10, 0.20)
DELAYS = (0.0, 1.0)
N_SWEEP = (100, 200, 400)
SEEDS = (0, 1, 2)


def beliefs(cells: pd.DataFrame) -> dict:
    """The belief at each cell's freeze, read and updated exactly as card S1.4 does."""
    scenes = HS.study2_scenes(cells)
    out = {}
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        b = belief_at(J2.scene_of(scenes[key], key), e_t, FLOORS_STUDY2,
                      p_change_prior=P_CHANGE_PRIOR, with_intention=False)
        b.p_change = update_intention(P_CHANGE_PRIOR, b.vy_oth, FLOORS_STUDY2.sd_v_lat,
                                      sign=float(np.sign(b.y_rel)) or 1.0)
        out[v] = (b, cp)
    return out


def strand1_params(v_ego: float) -> PreferenceParams:
    return PreferenceParams(v_desired=float(v_ego), sigma_v=S14.S1_SIGMA_V,
                            sigma_a=S14.S1_SIGMA_A, safety_term_enabled=False)


def run(bel: dict, corrected: bool, delay: float, n: int, seed: int) -> pd.DataFrame:
    rows = []
    for v, (b, cp) in bel.items():
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=n, sd_vlat=SD_VLAT, sd_a=SD_A,
                             seed=seed, keep_body_in_lane=corrected)
        p = strand1_params(b.v_ego)
        row = {"video": v, "cp": cp, "p_change": b.p_change}
        for al in ALPHAS:
            r = price_of_safety(b, fut, p, alpha=al, delay_s=delay)
            row[f"C_{al:g}"] = r.price
            row[f"a_{al:g}"] = (A_MAX_RELEASED + MENU_STEP) if r.none_admissible else r.a_star
            row[f"none_{al:g}"] = r.none_admissible
            row[f"cont_{al:g}"] = r.continue_admissible
            row["p_collide_continue"] = r.p_collide_continue
        rows.append(row)
    return pd.DataFrame(rows)


def score(df: pd.DataFrame, cells: pd.DataFrame, col: str) -> dict:
    d = df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
    raw = d[col].to_numpy(float)
    if np.all(raw <= 0):
        return {"post": np.nan, "cp1": np.nan, "rows": 0, "n_rows": 0, "rho_p": np.nan,
                "rho_gap": np.nan, "zeros_post": int((d.cp != "CP1").sum()),
                "zeros_cp1": int((d.cp == "CP1").sum())}
    d["x"] = axis(raw).values
    post = d[d.cp != "CP1"].reset_index(drop=True)
    cp1 = d[d.cp == "CP1"].reset_index(drop=True)
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    agree, nrows, _ = J2.matched_rows(post, post[col].to_numpy(float), +1.0)
    return {"post": r_post, "cp1": r_cp1, "rows": agree, "n_rows": nrows,
            "rho_p": float(spearmanr(post[col], post.p).statistic),
            "rho_gap": float(spearmanr(post[col], post.distance).statistic),
            "zeros_post": int((post[col] <= 0).sum()), "zeros_cp1": int((cp1[col] <= 0).sum())}


def delta_g_arm(bel: dict, arm: str, corrected: bool) -> pd.DataFrame:
    """Card S1.4's Delta G for one arm, on either fan. `corrected=False` is S1.4 itself."""
    rows = []
    for v, (b, cp) in bel.items():
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=S14.SEED, keep_body_in_lane=corrected)
        g = g_by_policy(b, fut, cutin_menu_paths(b, HORIZON_S, DT_S, steering=False),
                        S14.params(arm, b.v_ego))
        rows.append({"video": v, "cp": cp, "dg": delta_g(g)})
    return pd.DataFrame(rows)


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    bel = beliefs(cells)

    prim_df = run(bel, True, 0.0, N_SAMPLES, 0)
    res = {}           # (fan, delay, alpha) -> score, at n 200 seed 0
    frames = {(True, 0.0): prim_df}
    for corrected in (True, False):
        for delay in DELAYS:
            df = frames.get((corrected, delay))
            if df is None:
                df = frames[(corrected, delay)] = run(bel, corrected, delay, N_SAMPLES, 0)
            for al in ALPHAS:
                res[(corrected, delay, al)] = score(df, cells, f"C_{al:g}")
            print(f"fan corrected={corrected} delay={delay} done", flush=True)
    prim = res[(True, 0.0, 0.0)]
    prim_a = score(prim_df, cells, "a_0")

    mc = {}
    for n in N_SWEEP:
        mc[("n", n)] = prim if n == N_SAMPLES else score(run(bel, True, 0.0, n, 0), cells, "C_0")
    for s in SEEDS:
        mc[("seed", s)] = prim if s == 0 else score(run(bel, True, 0.0, N_SAMPLES, s), cells, "C_0")
    mc_posts = [m["post"] for m in mc.values()]
    rule_d = bool(np.nanmax(mc_posts) - np.nanmin(mc_posts) <= MC_TOL)
    print("monte carlo done", flush=True)

    # --- section 4: S1.4's Delta G on the corrected fan ---------------------------------
    dg = {}
    for arm in ("released", "strand1"):
        for corrected in (False, True):
            df = delta_g_arm(bel, arm, corrected).merge(
                cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
            ax = axis(df.dg.to_numpy(float))
            df["x"] = ax.values
            post = df[df.cp != "CP1"].reset_index(drop=True)
            cp1 = df[df.cp == "CP1"].reset_index(drop=True)
            r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
            r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1,
                                              cp1.x.to_numpy(float))
            agree, nrows, _ = J2.matched_rows(post, post.dg.to_numpy(float), +1.0)
            dg[(arm, corrected)] = {"post": r_post, "cp1": r_cp1, "rows": agree, "n_rows": nrows,
                                    "rho_gap": float(spearmanr(post.dg, post.distance).statistic),
                                    "zeros": ax.n_zero}
        print(f"delta G arm {arm} done", flush=True)

    # --- the cells file -----------------------------------------------------------------
    out_cells = prim_df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance",
                                     "dv_kph"]], on="video")
    out_cells.to_csv(OUT / "s16_admissibility_cells.csv", index=False)

    # ---------------------------------------------------------------------------------
    # the report
    # ---------------------------------------------------------------------------------
    is_cp1 = (prim_df.cp == "CP1").to_numpy()
    jj1_df = frames[(False, 0.0)]

    def counts(df, al):
        c = df[f"cont_{al:g}"].to_numpy(bool)
        nn = df[f"none_{al:g}"].to_numpy(bool)
        return (int(c[is_cp1].sum()), int(c[~is_cp1].sum()), int(nn[is_cp1].sum()),
                int(nn[~is_cp1].sum()))

    def verdict(s, stable):
        a = bool(np.isfinite(s["post"]) and s["post"] < GAP_RULE)
        b = bool(np.isfinite(s["cp1"]) and s["cp1"] < CP1_CRIT)
        if not stable:
            return "NOT STABLE"
        if a and b:
            return "ADOPT"
        if a:
            return "AXIS ONLY"
        return "GATE ONLY" if b else "NOT CREDITED"

    def fmt(s):
        if not np.isfinite(s["post"]):
            return "| every cell at zero: no axis | - | - | - | - |"
        return (f"| {s['post']:.4f} | {s['cp1']:.4f} | {s['rows']} of {s['n_rows']} |"
                f" {s['rho_p']:+.3f} | {s['rho_gap']:+.3f} |")

    L = ["# Card S1.6 -- admissibility: the conflict preference as a constraint on the menu", "",
         "Generated by `replication/czb/s16_admissibility.py`; the arms, the rules and the"
         " predictions were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "Jonas's ruling S14.Q2 (2026-09-22): implement strand 1's absolute conflict preference by"
         " EXCLUDING colliding policies from the menu rather than charging them a constant. The"
         " construction is `src/rollout/admissible.py` (19 property checks in"
         " `tests/test_admissible.py`); everything else is card S1.4's, imported.", "",
         "## 0 What \"the minimum is over admissible policies only\" does to Delta G", "",
         "Jonas asked what the implications are. Four, each with its count from this run"
         " (corrected fan, no delay, 200 futures):", "",
         "1. **Delta G stops being a difference and becomes a price.** With the conflict term a"
         " constraint, G is comfort cost alone, and for the stimulus ego `continue` costs exactly"
         " zero. While `continue` is admissible Delta G = 0; once it is not, G(continue) is not"
         " finite and what remains is C, the comfort cost of the cheapest admissible policy. Over a"
         " menu of constant decelerations that is a monotone function of **the mildest admissible"
         " deceleration a\\***. Admissibility turns Delta G into a required deceleration in nats,"
         " against the predictive fan. The strand-1 line and the comfort-margin line (S1.1, S1.5)"
         " are the same line.",
         "2. **It contains a gate, and the gate is a tolerance.** `continue` is admissible when the"
         " share of futures in which it collides is at most alpha, so the quantity is silent until"
         " P(conflict) exceeds alpha. Counts of cells where `continue` is admissible, pre-onset"
         " (of 90) / post-onset (of 288): "
         + "; ".join(f"alpha {al:g}: {counts(prim_df, al)[0]} / {counts(prim_df, al)[1]}"
                     for al in ALPHAS) + ".",
         "3. **It has a ceiling, the dread regime.** Where no policy in the menu is admissible,"
         " braking cannot keep the scene conflict-free. Cells with nothing admissible, pre-onset /"
         " post-onset: "
         + "; ".join(f"alpha {al:g}: {counts(prim_df, al)[2]} / {counts(prim_df, al)[3]}"
                     for al in ALPHAS) + ".",
         "4. **It reads the fan's tails, so the fan has to be right where it was never checked.**"
         " An expected cost averages over the fan; admissibility at a small alpha is decided by its"
         " most extreme futures. Section 3 shows what that did with card JJ.1's fan as built.", "",
         "## 1 The primary: corrected fan, alpha = 0, no delay", "",
         "| axis | post-onset held out | pre-onset | matched-TTC rows | rho(share) | rho(gap) |",
         "|---|---|---|---|---|---|",
         "| **log C, the price of safety in nats (primary)** " + fmt(prim),
         "| log a*, the mildest admissible deceleration " + fmt(prim_a), "",
         f"Comparators on file: the gap threshold {GAP_RULE:.4f}, looming {LOOMING_UNGATED:.4f}"
         f" ungated and {LOOMING_GATED:.4f} gated, card G.1's pre-onset {G1_CP1:.4f}, card S1.4's"
         f" strand-1 arm {S14_ARM4[0]:.4f} / {S14_ARM4[1]:.4f}, chance {CHANCE:.3f}. Zero-price"
         f" cells: {prim['zeros_post']} of 288 post-onset and {prim['zeros_cp1']} of 90 pre-onset.",
         "",
         "## 2 The tolerance alpha, and the delay before braking", "",
         "None is chosen by its score; alpha = 0 with no delay is the primary.", "",
         "| alpha | delay [s] | post-onset held out | pre-onset | matched-TTC rows | rho(share) |"
         " rho(gap) | continue admissible, pre / post |", "|---|---|---|---|---|---|---|---|"]
    for delay in DELAYS:
        for al in ALPHAS:
            c = counts(frames[(True, delay)], al)
            mark = " **(primary)**" if (al == 0.0 and delay == 0.0) else ""
            L.append(f"| {al:g}{mark} | {delay:g} " + fmt(res[(True, delay, al)]) + f" {c[0]} / {c[1]} |")
    L += ["", "## 3 Card JJ.1's fan as built, and the Monte Carlo rule", "",
          "JJ.1's fan clips a lane-keeping other's CENTRE at the ego's lane edge, inside the"
          " released collision box, so a vehicle certain to keep its lane collides with a passing"
          " ego in about a fifth of futures. Share of futures in which `continue` collides, median"
          f" over the 90 pre-onset cells: **{np.median(jj1_df.p_collide_continue[is_cp1]):.3f}** on"
          f" JJ.1's fan against **{np.median(prim_df.p_collide_continue[is_cp1]):.3f}** on the"
          f" corrected one (the intention posterior there has median"
          f" {np.median(prim_df.p_change[is_cp1]):.3f}).", "",
          "| alpha | JJ.1's fan: post-onset held out | pre-onset | matched-TTC rows | rho(share) |"
          " rho(gap) | continue admissible, pre / post |", "|---|---|---|---|---|---|---|"]
    for al in ALPHAS:
        c = counts(jj1_df, al)
        L.append(f"| {al:g} " + fmt(res[(False, 0.0, al)]) + f" {c[0]} / {c[1]} |")
    L += ["", "Rule (d), the primary under resampling:", "",
          "| what varies | post-onset held out | pre-onset |", "|---|---|---|"]
    for (kind, val), m in mc.items():
        L.append(f"| {kind} = {val} | {m['post']:.4f} | {m['cp1']:.4f} |")
    L += ["", f"Range of the post-onset score {np.nanmax(mc_posts) - np.nanmin(mc_posts):.4f}"
          f" against the tolerance {MC_TOL}: **rule (d) {'HOLDS' if rule_d else 'FAILS'}**.", "",
          "## 4 Does the flaw in the fan change cards JJ.2 and S1.4?", "",
          "Card S1.4's Delta G (finite costs, the four-policy menu), arm 1 (released, which is card"
          " JJ.2's own staging) and arm 4 (strand 1, flat cost), on both fans.", "",
          "| arm | fan | post-onset held out | pre-onset | matched-TTC rows | rho(dG, gap) |"
          " zero cells |", "|---|---|---|---|---|---|---|"]
    for arm, lab in (("released", "1 released (JJ.2's staging)"), ("strand1", "4 strand 1")):
        for corrected in (False, True):
            s = dg[(arm, corrected)]
            L.append(f"| {lab} | {'corrected' if corrected else 'JJ.1 as built'} |"
                     f" {s['post']:.4f} | {s['cp1']:.4f} | {s['rows']} of {s['n_rows']} |"
                     f" {s['rho_gap']:+.3f} | {s['zeros']} |")
    repro = (abs(dg[("released", False)]["post"] - S14_ARM1[0]) <= 0.0005
             and abs(dg[("strand1", False)]["post"] - S14_ARM4[0]) <= 0.0005)
    moved = {arm: (abs(dg[(arm, True)]["post"] - dg[(arm, False)]["post"]),
                   abs(dg[(arm, True)]["cp1"] - dg[(arm, False)]["cp1"]))
             for arm in ("released", "strand1")}
    load_bearing = any(max(m) > 0.01 for m in moved.values())
    drop_changes = dg[("released", True)]["post"] <= LOOMING_GATED + 0.01
    L += ["",
          f"Reproduction of S1.4 on JJ.1's fan: {'exact to 0.0005' if repro else '**NOT reproduced**'}"
          f" ({dg[('released', False)]['post']:.4f} against {S14_ARM1[0]:.4f};"
          f" {dg[('strand1', False)]['post']:.4f} against {S14_ARM4[0]:.4f}).", "",
          "**By the pre-stated rule the clip "
          + ("WAS load-bearing" if load_bearing else "was NOT load-bearing")
          + " for those cards**: the largest move is "
          + "; ".join(f"arm {'1' if a == 'released' else '4'} {m[0]:.4f} post-onset and {m[1]:.4f}"
                      " pre-onset" for a, m in moved.items())
          + f", against the 0.01 criterion. Card JJ.2's DROP "
          + ("**would change**" if drop_changes else "does not change")
          + f": arm 1 on the corrected fan scores {dg[('released', True)]['post']:.4f} against the"
          f" {LOOMING_GATED + 0.01:.4f} its rule (a) required.", "",
          "## 5 The verdict on the pre-stated rules", ""]
    v = verdict(prim, rule_d)
    L += [f"**{v}.** Rule (a): {prim['post']:.4f} against {GAP_RULE:.4f}"
          f" ({'holds' if prim['post'] < GAP_RULE else 'fails'}; against the stricter"
          f" {GAP_RULE_STRICT:.4f} it {'holds' if prim['post'] < GAP_RULE_STRICT else 'fails'})."
          f" Rule (b): {prim['cp1']:.4f} against {CP1_CRIT}"
          f" ({'holds' if prim['cp1'] < CP1_CRIT else 'fails'}). Rule (c): {prim['rows']} of"
          f" {prim['n_rows']} rows ({'holds' if prim['rows'] >= ROWS_CRIT else 'fails'})."
          f" Rule (d): {'holds' if rule_d else 'fails'}.", ""]
    gate_alphas = [al for al in ALPHAS if np.isfinite(res[(True, 0.0, al)]["cp1"])
                   and res[(True, 0.0, al)]["cp1"] < CP1_CRIT]
    L += [("**Rule (b) holds at alpha = " + ", ".join(f"{a:g}" for a in gate_alphas)
           + "** (not the primary unless 0 is listed): there the admissible set supplies the gate"
           " with no gate term, as prediction 2 said it might above the lane-change prior of"
           f" {P_CHANGE_PRIOR}." if gate_alphas else
           "**Rule (b) holds at no alpha**: the admissible set does not supply the gate on this"
           " fan."), "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "s16_admissibility.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-14:]))


if __name__ == "__main__":
    main()
