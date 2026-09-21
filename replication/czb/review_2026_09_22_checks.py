"""
The review of 2026-09-22: the checks behind its findings, from committed code and tracked data.

Jonas asked for a deep review of everything done since a Fable-class model last reviewed the work,
which is the arc of 2026-09-18 to 09-22 (cards JJ.2 to S1.4, executed by a less capable model).
Four reviewers read the arc in parallel; their scratch analyses are kept as run in
`replication/review_2026-09-22/scratch/`. **This script re-derives the findings that change how a
card is read, so that every number the review document quotes comes from a committed script with a
tracked output** (standing rule 1). It fits nothing new and changes no card; it imports the cards'
own functions and reads their tracked outputs. It is a review instrument, not a card: there is no
decision rule, and each section says what it shows.

Sections
  1  Card RE.2's rho = -0.861 ("the braking-margin term is inverted"): what was correlated, and why
     it is negative.
  2  Card JJ.2's 0.3202: the score of a constant, because the fit's sign was fixed at +1.
  3  Card RE.1 part C, "the planner never brakes": the pedal constraint at step 0.
  4  Card RE.4: the ego's lateral position against the lane centre the agent was given.
  5  Card GM.1a: the growth form and sigma_a on fixed origins, and without conditioning on the
     future.
  6  Card RE.3: the truck-car offset clip pair by clip pair, and resampling the pairs too.
  7  Literals: result strings typed into scripts rather than computed.

Output: replication/czb/out/review_2026_09_22_checks.md
Run:    python replication/czb/review_2026_09_22_checks.py
"""
from __future__ import annotations

import re
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
OUT = HERE / "out"
SEED = 20260922


def sp(a, b) -> float:
    return float(spearmanr(a, b).statistic)


# ---------------------------------------------------------------------------------
def section_1(L: list) -> None:
    import re2_preference_family as R2
    from aidriver.preferences import PreferenceParams, required_deceleration

    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    built = R2.build_cells(cells, R2.HS.study2_scenes(cells))
    base = {"a_other_min": -6.0, "response_time": 1.0, "a_max": 8.0, "tau_inv_mu": 0.2,
            "collision_ref_speed": 10.0, "counterfactual_residual_severity": True}
    meta = cells[["video", "p", "n", "ttc_true", "distance", "dv_kph"]]
    tt = R2.term_table(base, built).merge(meta, on="video")
    tt["v_ego"] = [b[2].v_ego for b in built]
    tt["v_oth"] = [b[2].v_oth for b in built]
    tt["x_rel"] = [b[2].x_rel for b in built]
    post = tt[tt.cp != "CP1"].copy()
    step = R2.term_table(dict(base, counterfactual_residual_severity=False), built).merge(
        meta, on="video")
    step = step[step.cp != "CP1"]

    obs = {"v": post.v_ego.to_numpy(float), "a": 0.0, "dx": post.x_rel.to_numpy(float),
           "dy": 0.0, "v_other": post.v_oth.to_numpy(float), "a_other": 0.0}
    post["areq"] = -np.asarray(required_deceleration(obs, PreferenceParams()), float)
    post["safety_rate"] = post.safety / np.minimum(post.ttc_true, 6.0)

    L += ["## 1 Card RE.2's rho = -0.861: what it is a correlation of, and why it is negative", "",
          "The arc's through-line is that \"the released braking-margin term is inverted against"
          " the human response (rho = -0.861)\". Recomputed here with card RE.2's own functions"
          " (`build_cells`, `term_table`) at the released constants, 288 post-onset cells:", "",
          "| quantity | Spearman rho with the share who intervene |", "|---|---|",
          f"| the braking-margin term's contribution to G(continue), SUMMED over the 6 s horizon"
          f" (what RE.2 correlated) | **{sp(post.safety, post.p):+.3f}** |",
          f"| the same sum divided by the time to contact, min(TTC, 6 s) |"
          f" {sp(post.safety_rate, post.p):+.3f} |",
          f"| the required deceleration itself at the freeze, released constants |"
          f" **{sp(post.areq, post.p):+.3f}** |", "",
          f"The summed contribution correlates **{sp(post.safety, post.ttc_true):+.3f} with the"
          " TTC**. The term applies only while the lead is ahead, and the `continue` ego drives"
          " THROUGH the lead, so the horizon sum largely counts the steps before contact: a longer"
          " TTC means more steps charged. That is accounting, not preference. The quantity under"
          " the term orders the cells the human way, at every closing speed:", "",
          "| closing speed [km/h] | rho(summed term, share) | rho(required deceleration, share) |"
          " rho(total epsilon, share), project's ramp form | the same, released step form |",
          "|---|---|---|---|---|"]
    for dv, g in post.groupby("dv_kph"):
        gs = step[step.dv_kph == dv]
        L.append(f"| {dv:g} | {sp(g.safety, g.p):+.3f} | {sp(g.areq, g.p):+.3f} |"
                 f" {sp(g.collision + g.safety, g.p):+.3f} |"
                 f" {sp(gs.collision + gs.safety, gs.p):+.3f} |")
    L += ["",
          "**Reading.** \"Inverted\" is not a property of the braking-margin term. It is a property"
          " of (i) summing a pre-contact charge over the horizon of a policy that drives through"
          " the lead, and (ii) the project's own ramp form of the term"
          " (`counterfactual_residual_severity=True`, which every card of the arc ran with and"
          " labelled \"released\"): with the released step form the total orders the cells the"
          " human way within every closing speed. What does survive is card JJ.2's rule (c): across"
          " closing speeds at matched TTC the quantity is ordered the wrong way, because its"
          " severity grows with closing speed while participants respond to proximity.", ""]


# ---------------------------------------------------------------------------------
def section_2(L: list) -> None:
    import cutin2_field_vs_gap as R
    df = pd.read_csv(OUT / "jj2_rollout_cutin_cells.csv")
    post = df[df.cp != "CP1"].reset_index(drop=True)
    cp1 = df[df.cp == "CP1"].reset_index(drop=True)
    y, w, f = post.p.to_numpy(float), post.n.to_numpy(float), post.ttc_start.to_numpy(float)
    x = np.log(post.dg_A.to_numpy(float))
    rows = []
    for sign in (+1.0, -1.0):
        pred = np.full_like(y, np.nan)
        for k in np.unique(f):
            th = R.fit(x[f != k], y[f != k], w[f != k], sign)
            pred[f == k] = R.predict(th, x[f == k], sign)
        rows.append((sign, R.wrmse(y, pred, w), float(pred.min()), float(pred.max())))
    th = R.fit(x, y, w, +1.0)
    L += ["## 2 Card JJ.2's 0.3202 is the score of a constant", "",
          "Recomputed from `out/jj2_rollout_cutin_cells.csv` with the registered fitter. Card JJ.2"
          " fixed the threshold model's sign at +1 (more Delta G, more response). Delta G is"
          f" ANTI-ordered with the response (rho {sp(post.dg_A, post.p):+.3f}), so the best +1 fit"
          " puts the level above every cell and predicts one number everywhere:", "",
          "| sign of the fit | post-onset held out | smallest / largest held-out prediction |",
          "|---|---|---|"]
    for sign, r, lo, hi in rows:
        L.append(f"| {sign:+.0f} | {r:.4f} | {lo:.3f} / {hi:.3f} |")
    L += ["",
          f"Full-sample fit at +1: level {th[1]:.2f} against the largest log Delta G"
          f" {x.max():.2f}. So \"0.3202 = chance\" means *the fit gave up*, not *the axis carries no"
          " information*; with the sign free the same axis scores the second row, still far from"
          " the gap's 0.1522, so **the DROP verdict stands as pre-stated**. Two things do not:"
          " rule (b)'s pre-onset 0.5381 is that constant against a pre-onset mean share of"
          f" {np.average(cp1.p, weights=cp1.n):.3f} and tests nothing about emergence; and the ten"
          " identical 0.3202 rows of the sensitivity table are the same constant ten times, so"
          " they do not show that the result is \"a property of the quantity rather than of any"
          " constant\".", "",
          f"All 90 pre-onset Delta G values ({cp1.dg_A.min():,.0f} to {cp1.dg_A.max():,.0f}) lie"
          f" below all 288 post-onset ones ({post.dg_A.min():,.0f} to {post.dg_A.max():,.0f}): the"
          " lane-change prior scales the whole quantity, which is a gate of a kind and was not"
          " reported.", ""]


# ---------------------------------------------------------------------------------
def section_3(L: list) -> None:
    from aidriver.agent import AgentParams, apply_pedal_constraint
    plan = np.full((1, 30), -5.0)
    a0 = apply_pedal_constraint(plan.copy(), 0.0, AgentParams(), 0.2)[0, :4]
    a1 = apply_pedal_constraint(plan.copy(), -0.1, AgentParams(), 0.2)[0, :4]
    src = (REPO / "replication/causation/re1_rear_end_criticality.py").read_text(encoding="utf-8")
    hits = [f"line {i + 1}: `{ln.strip()}`" for i, ln in enumerate(src.splitlines())
            if re.search(r"a_applied\s*=\s*0\.0|a_best_first|acts_brake\s*=", ln)][:6]
    L += ["## 3 Card RE.1 part C, \"the released planner steers in 36 of 36 cells and never"
          " brakes\"", "",
          "The released pedal constraint limits the first step of a plan by the acceleration"
          " currently applied. A plan of constant -5 m/s^2 comes back as:", "",
          f"* with `a_applied = 0.0` (what the card passed): first four steps"
          f" {np.round(a0, 2).tolist()}",
          f"* with `a_applied = -0.1` (the coasting policy the card's ego was actually holding):"
          f" {np.round(a1, 2).tolist()}", "",
          "The card's brake test reads the FIRST step only. The relevant lines of"
          " `replication/causation/re1_rear_end_criticality.py`: " + "; ".join(hits) + ".", "",
          "**Reading.** With the first step clamped near the coasting value, \"never brakes\" is"
          " what the test returns for any plan, including one that brakes at 5 m/s^2 from the"
          " second step on. The claim, and card JJ.2b's \"378 of 378\" which uses the same test,"
          " should read: *the planner's chosen plans were not examined beyond their first step*."
          " A reviewer's rerun of four cells found braking of 3.8 to 7.0 m/s^2 within the horizon"
          " (scratch, `reviewC/planc.py`; not reproduced here because the planner run is slow).", ""]


# ---------------------------------------------------------------------------------
def section_4(L: list) -> None:
    import hs1_situational_surprise as HS
    from aidriver.preferences import PreferenceParams, log_lateral_pref
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    sc = HS.study2_scenes(cells)
    ys = np.array([float(np.median(s["tracks"][s["ego"]].y)) for s in sc.values()])
    p = PreferenceParams()
    per_step = np.array([float(log_lateral_pref(y, p)) for y in ys])
    src = (HERE / "re4_efe_functionals.py").read_text(encoding="utf-8")
    uses_world_y = bool(re.search(r"lane_centre", src))
    L += ["## 4 Card RE.4: where the ego was, against the lane centre the agent was given", "",
          f"Across the {len(ys)} traces of the second cut-in study the ego's recorded lateral"
          f" position is {ys.min():.2f} to {ys.max():.2f} m in world coordinates. The released"
          f" preference's lane centre defaults to {p.lane_centre:g} m, where the lateral term is"
          f" {per_step.min():,.0f} to {per_step.max():,.0f} nats PER STEP, i.e."
          f" {30 * per_step.min():,.0f} to {30 * per_step.max():,.0f} over the 30-step horizon.",
          "",
          f"`re4_efe_functionals.py` {'mentions' if uses_world_y else 'never sets'} `lane_centre`."
          " The card's own report gives epsilon between about 450,000 and 660,000 nats in every"
          " cell, which is this constant plus everything else. `rollout.efe` (cards JJ.2, RE.2,"
          " S1.4) passes a lane-RELATIVE y and is not affected.", "",
          "**Reading.** In card RE.4, and in the planner rows of card JJ.2b that use the same agent"
          " call, the ego is off the road in every cell. Four of RE.4's five functionals and"
          " JJ.2b's \"19 of 24\" are therefore measurements of how much off-road cost a plan"
          " recovers, and carry no information about the cut-in. RE.4's conclusion (\"no"
          " functional of the expected free energy orders the cells\") is **untested**, not"
          " established.", ""]


# ---------------------------------------------------------------------------------
def section_5(L: list) -> None:
    import gm1a_lead_acceleration as G
    from generative.uncertainty import (backward_velocity, cv_prediction_errors, fit_growth,
                                        fit_growth_accel, growth_residual)
    d = G.load_scenarios()
    H = G.HORIZONS

    def wsd(vals, ws):
        flat = np.concatenate(vals)
        wv = np.concatenate([np.full(len(v), w) for v, w in zip(vals, ws)])
        mu = np.average(flat, weights=wv)
        return float(np.sqrt(np.average((flat - mu) ** 2, weights=wv)))

    def forms(per, ws):
        sd = [wsd([p[h] for p in per if len(p[h])], [w for p, w in zip(per, ws) if len(p[h])])
              for h in H]
        s0l, s1 = fit_growth(H, sd)
        s0q, sa = fit_growth_accel(H, sd)
        return sa, growth_residual(H, sd, s0l, s1, False), growth_residual(H, sd, s0q, sa, True)

    rows = []
    for thr in (-0.3, -0.5, -1.0):
        card, fixed, uncond, ws = [], [], [], []
        for _, g in d.groupby("id", sort=False):
            t, v = g.t.to_numpy(float), g.v_l.to_numpy(float)
            x = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
            k = G.phase_split(t, v, thr)
            if k < G.MIN_SAMPLES:
                continue
            e = cv_prediction_errors(t[:k], x[:k], np.zeros(k), H, window_s=0.3)
            n3 = len(e[H[-1]][0])
            vx = backward_velocity(t, x, 0.3)
            un = {}
            for h in H:
                kk = np.searchsorted(t, t + h - 1e-9)
                ok = (kk < len(t)) & np.isfinite(vx) & (np.arange(len(t)) < k)
                un[h] = (x[np.where(ok, kk, 0)] - (x + vx * h))[ok]
            card.append({h: e[h][0] for h in H})
            fixed.append({h: e[h][0][:n3] for h in H})
            uncond.append(un)
            ws.append(float(g.weight.iloc[0]))
        for name, per in (("the card's pooling", card), ("fixed origins", fixed),
                          ("benign origins, targets unconditioned", uncond)):
            sa, rl, rq = forms(per, ws)
            rows.append((thr, name, sa, rl, rq))
    L += ["## 5 Card GM.1a: the growth form, and sigma_a", "",
          "Recomputed with the card's own loader, phase split and fitting functions. \"Fixed"
          " origins\" uses, at every horizon, only the origins that are valid at the longest one"
          " (the card pools a different, shrinking set of origins per horizon). \"Targets"
          " unconditioned\" keeps benign origins but lets the target fall after braking onset,"
          " which is the uncertainty a predictive fan has to carry: the card's benign slice ENDS"
          " at the onset, so every one of its pairs is conditioned on the lead not braking.", "",
          "| onset threshold [m/s^2] | origins | fitted sigma_a [m/s^2] | residual, linear form [m]"
          " | residual, quadratic form [m] | better form |", "|---|---|---|---|---|---|"]
    for thr, name, sa, rl, rq in rows:
        L.append(f"| {thr:g} | {name} | {sa:.3f} | {rl:.4f} | {rq:.4f} |"
                 f" {'linear' if rl < rq else '**quadratic**'} |")
    L += ["",
          "**Reading.** \"The fan's form is wrong, linear growth fits better\" is an artefact of"
          " pooling different origins at different horizons; on fixed origins the quadratic form"
          " the design note specifies fits better. And 0.098 m/s^2 is not \"the fan is five times"
          " too wide\": it is sigma_a conditional on no braking within the horizon, it moves with"
          " the analyst's onset threshold, and without the conditioning the same data give a value"
          " near or above the assumed 0.5. Design note section 1.2 should not be changed on card"
          " GM.1a's evidence, and the recommendation in query GM1A.Q1 should not be adopted.", ""]


# ---------------------------------------------------------------------------------
def section_6(L: list) -> None:
    import jj4_precision_spread as J4
    b, _ = J4.press_levels()
    cell = b.groupby(["driver", "cls", "criticality_label"])["level"].mean().reset_index()
    piv = cell.pivot_table(index=["driver", "criticality_label"], columns="cls",
                           values="level").dropna()
    dd = (piv[1] - piv[0]).reset_index()
    per = dd.groupby("criticality_label")[0].agg(["mean", "std", "size"])
    per["se"] = per["std"] / np.sqrt(per["size"])
    W = dd.pivot(index="driver", columns="criticality_label", values=0).to_numpy()
    rng = np.random.default_rng(SEED)
    drv = [np.nanmean(W[rng.integers(0, len(W), len(W))]) for _ in range(4000)]
    two = [np.nanmean(np.nanmean(W[rng.integers(0, len(W), len(W))][:, rng.integers(0, W.shape[1],
                                                                                     W.shape[1])],
                                 axis=0)) for _ in range(4000)]
    L += ["## 6 Card RE.3: the truck-car offset, clip pair by clip pair", "",
          "Card RE.3's interval [-0.1922, -0.0721] resamples the 43 drivers and treats the five"
          " truck/car clip pairs as fixed. The offset by pair, driver-paired"
          " (`jj4_precision_spread.press_levels`):", "",
          "| TTC label | truck - car, log looming level | SE over drivers | drivers |",
          "|---|---|---|---|"]
    for lab, r in per.iterrows():
        L.append(f"| {lab} | {r['mean']:+.3f} | {r['se']:.3f} | {int(r['size'])} |")
    lo_d, hi_d = np.percentile(drv, [2.5, 97.5])
    lo_t, hi_t = np.percentile(two, [2.5, 97.5])
    L += ["",
          f"Resampling drivers only: [{lo_d:+.3f}, {hi_d:+.3f}]. Resampling drivers AND clip pairs:"
          f" **[{lo_t:+.3f}, {hi_t:+.3f}]**.", "",
          "**Reading.** The offset changes sign across the five pairs, by many driver standard"
          " errors, so the clips are a source of variance the card held fixed. With the pairs"
          " resampled the interval " + ("covers" if lo_t < 0 < hi_t else "does not cover")
          + " zero, and card RE.3's pre-stated rule would then return \"perceptual\", not"
          " \"neither\". The reviewer also found that at the same TTC label the truck's cut-in"
          " starts earlier and at a larger gap than the car's (scratch, `reviewB/a4.py`), so"
          " \"matched TTC\" is not matched. \"Neither perceptual nor configurational\", and the"
          " width exponent 1.42 [1.24, 1.63], should not be quoted.", ""]


# ---------------------------------------------------------------------------------
def section_7(L: list) -> None:
    targets = [("replication/czb/re2_preference_family.py", r"0\.861"),
               ("replication/causation/re1_rear_end_criticality.py", r"7e-16"),
               ("replication/czb/s14_strand1_preference.py", r"0\.2864")]
    L += ["## 7 Result strings typed into scripts rather than computed", "",
          "Standing rule 1 asks that every quoted number come from a committed script with a"
          " tracked output. These scripts WRITE the number as literal text into their report:", "",
          "| script | literal | lines |", "|---|---|---|"]
    for path, pat in targets:
        src = (REPO / path).read_text(encoding="utf-8").splitlines()
        lines = [str(i + 1) for i, ln in enumerate(src) if re.search(pat, ln)]
        L.append(f"| `{path}` | {pat.replace(chr(92), '')} | {', '.join(lines) or 'not found'} |")
    rep = (REPO / "replication/causation/re1/re1_rear_end_criticality.md").read_text(
        encoding="utf-8").splitlines()
    ident = [ln.strip() for ln in rep if "1e-09" in ln or "relative difference" in ln.lower()][:3]
    L += ["",
          "Card RE.1's identity \"to 7e-16\" is the sharpest case. Its tracked report says: "
          + " / ".join(f"*{ln}*" for ln in ident)
          + ". The identity holds for practical purposes, but the pre-stated criterion FAILED and"
          " the number that spread to the commit message, the worklog, the handover and the"
          " reformulation note is not the one the run produced.", ""]


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    L = ["# The review of 2026-09-22: the checks behind its findings", "",
         "Generated by `replication/czb/review_2026_09_22_checks.py`. It imports the cards' own"
         " functions and reads their tracked outputs; it fits nothing new and changes no card. The"
         " review itself is `docs/review_2026-09-22.md`. Do not edit by hand.", ""]
    for fn in (section_1, section_2, section_3, section_4, section_5, section_6, section_7):
        try:
            fn(L)
        except Exception as exc:                       # a failed check is reported, not hidden
            L += [f"## {fn.__name__} FAILED TO RUN", "", f"`{type(exc).__name__}: {exc}`", ""]
        print(f"{fn.__name__} done at {time.time() - t0:.0f} s", flush=True)
        (OUT / "review_2026_09_22_checks.md").write_text("\n".join(L), encoding="utf-8")
    L += [f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "review_2026_09_22_checks.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
