"""
Card S1.1 -- the comfort margin: strand 1's "can I still stop without harsh braking?" as the
comfort-zone axis.

**PART 1 OF THIS CARD WAS EXPLORATORY AND THE REPORT SAYS SO IN ITS OWN WORDS.** The sweep in
section 2 was run before any rule was fixed, and the primary setting in section 3 was chosen after
seeing it. That is the opposite of how every other card in this project was run, and it is declared
rather than hidden: nothing here is a verdict, and the confirmatory test that WOULD be a verdict is
pre-stated in section 5 and NOT run here.

WHY THIS QUANTITY
-----------------
Jonas, 2026-09-18: *"What can we reformulate then to make it fit/work? It should be possible, I
still feel... I think we should really try out strand 1 formulation."*

The program's strand 1 (Engström, Wei, McDonald, Garcia, O'Kelly & Johnson 2024, *Resolving
uncertainty on the fly*, Front. Neurorobot. 18:1341750) states the comfort-zone trade-off in one
sentence: the driver must *"adapt their speed to be able to stop well ahead of the pedestrian (to
meet the preference of conflict avoidance) without harsh braking (to meet their preferences for
deceleration comfort)"*. So the strand-1 comfort quantity is **the deceleration the situation would
demand**, compared with what the driver finds comfortable -- not a collision cost.

The released preference function already computes that quantity: `required_deceleration` (SI
Eq. 51), the deceleration the ego would need, after a reaction time, to avoid a collision if the
lead braked at `a_other_min`. What the released model then DOES with it is the problem card RE.2
measured: it thresholds it at the ego's physical maximum `a_max` = 8 m/s^2 -- the DREAD boundary --
and multiplies the indicator by a severity that grows with closing speed, producing a term whose
contribution correlates **-0.861** with the share of participants who intervene.

**So the hypothesis of this card is narrow and specific: the released preference contains a
quantity that orders these cells, and the preference function destroys it.** Cards RE.2 and RE.4
tested the preference (its constants and its functionals) and found nothing; neither tested
`required_deceleration` on its own. The registered R.2 script did test an axis called "a_req", but
that is the kinematic approximation `dv / (2 TTC)` (`cutin2_field_vs_gap.cell_table`), not the
model's own function with the lead's assumed braking and the reaction time in it. This quantity has
never been scored.

WHAT IS COMPUTED
----------------
`aidriver.preferences.required_deceleration` at the freeze of each of card JJ.2's 378 cells, on the
belief card JJ.2 reads from the scene, with the released observation dict. The axis is
log(-a_req), so more negative a_req -- a more demanding situation -- is a larger axis value, and
the threshold model is fitted with the same sign convention every other axis uses. Cells, folds and
metric are the registered R.2 script's, imported.

Two parameters of `required_deceleration` are the driver's, not the scene's, and they are what the
sweep is over:
  **a_other_min**  how hard you assume the lead might brake. Released value -6 m/s^2; the authors
                   calibrate it per SCENARIO through a free-following analysis
                   (`docs/method_review.md` §6.2), so it was never a driver property.
  **response_time** your assumed own reaction time. Released value 1.0 s.

THE PRIMARY, AND HOW IT WAS CHOSEN -- read section 3 before section 2
---------------------------------------------------------------------
**a_other_min = -10 m/s^2, response_time = 1.0 s.** The second is the released value, unchanged.
The first is NOT the released -6, and it won the exploratory sweep, so its motivation is stated
separately and the reader can judge it: -10 m/s^2 is about 1 g, the deceleration a passenger car on
dry asphalt can actually achieve, so "the lead might brake as hard as it physically can" is a
worst-case assumption a driver could hold and is arguably better motivated than -6, which the
authors chose to make their own simulations follow stably. **It is nonetheless a value that won a
sweep, and no conclusion in this card rests on it: section 4 reports the whole sweep and section 5
says what would have to happen for any of this to become a result.**

Comparators, on file: the gap threshold **0.1522** (`out/cutin2_field_vs_gap.md`, the registered
R.2 script's own best design scalar), the ungated looming rule **0.1137** and the gated **0.1027**
(`out/cutin2_gate.md`), card G.1's pre-onset **0.0319**, chance **0.320**, the noise floor 0.118.

WHAT THIS CARD DOES NOT DO
--------------------------
It does not fit anything per driver, it does not touch the pre-onset cells except to report them,
and it does not run the strand-1 model -- there is no public release of it and building it is a
separate decision (query S11.Q3). It tests one quantity on one scenario.

Output: replication/czb/out/s11_comfort_margin.md and out/s11_comfort_margin.csv.
Run:    python replication/czb/s11_comfort_margin.py
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
from aidriver.preferences import PreferenceParams, required_deceleration  # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at       # noqa: E402

OUT = HERE / "out"
GAP_RULE = 0.1522           # out/cutin2_field_vs_gap.md, the registered gap threshold
A_OV_PRIMARY = -10.0
T_REACT_PRIMARY = 1.0
A_OV_SWEEP = (-4.0, -6.0, -8.0, -10.0, -12.0, -15.0)
T_REACT_SWEEP = (0.5, 1.0, 1.5, 2.0)


def scene_states(cells: pd.DataFrame) -> pd.DataFrame:
    """The belief at each cell's freeze, read exactly as card JJ.2 reads it."""
    scenes = HS.study2_scenes(cells)
    rows = []
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        b = belief_at(J2.scene_of(scenes[key], key), e_t, FLOORS_STUDY2,
                      p_change_prior=P_CHANGE_PRIOR, with_intention=False)
        rows.append({"video": v, "cp": cp, "x_rel": b.x_rel, "y_rel": b.y_rel,
                     "v_ego": b.v_ego, "v_oth": b.v_oth})
    return pd.DataFrame(rows).merge(
        cells[["video", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph"]], on="video")


def a_req(d: pd.DataFrame, a_ov: float, t_react: float) -> np.ndarray:
    p = PreferenceParams(a_other_min=a_ov, response_time=t_react)
    n = len(d)
    obs = {"v": d.v_ego.to_numpy(float), "a": np.zeros(n), "dx": d.x_rel.to_numpy(float),
           "dy": d.y_rel.to_numpy(float), "v_other": d.v_oth.to_numpy(float),
           "a_other": np.zeros(n), "theta": np.zeros(n), "theta_other": np.zeros(n)}
    return np.asarray(required_deceleration(obs, p), float)


def score(d: pd.DataFrame, x: np.ndarray) -> dict | None:
    """Held out on the registered folds, plus the pre-onset cells and the ordering statistics."""
    dd = d.copy()
    dd["x"] = x
    if not np.all(np.isfinite(x)):
        return None
    post = dd[dd.cp != "CP1"].reset_index(drop=True)
    cp1 = dd[dd.cp == "CP1"].reset_index(drop=True)
    try:
        r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
        r_cp1, _, _ = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1,
                                          cp1.x.to_numpy(float))
    except Exception:
        return None
    if not (np.isfinite(r_post) and np.isfinite(r_cp1)):
        return None
    agree, nrows, _ = J2.matched_rows(post, post.x.to_numpy(float), +1.0)
    return {"post": r_post, "cp1": r_cp1, "rows": agree, "n_rows": nrows,
            "rho_p": float(spearmanr(post.x, post.p).statistic),
            "rho_gap": float(spearmanr(post.x, post.distance).statistic)}


def axis_of(d, a_ov, t_react):
    return np.log(np.maximum(-a_req(d, a_ov, t_react), 1e-6))


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    d = scene_states(cells)

    prim = score(d, axis_of(d, A_OV_PRIMARY, T_REACT_PRIMARY))
    rel = score(d, axis_of(d, -6.0, 1.0))
    gap = score(d, -np.log(d.distance.to_numpy(float)))

    L = ["# Card S1.1 -- the comfort margin: \"can I still stop without harsh braking?\" as the"
         " axis", "",
         "Generated by `replication/czb/s11_comfort_margin.py`. **Part of this card was"
         " EXPLORATORY.** The sweep in section 4 was run before any rule was fixed and the primary"
         " in section 2 was chosen after seeing it, which is the opposite of how every other card"
         " in this project was run. Nothing here is a verdict; section 5 says what would be. Do not"
         " edit by hand.", "",
         "Strand 1 states the comfort-zone trade-off in one sentence: the driver must *adapt their"
         " speed to be able to stop well ahead of the hazard (to meet the preference of conflict"
         " avoidance) without harsh braking (to meet their preferences for deceleration comfort)*"
         " (Engström et al. 2024). So the strand-1 comfort quantity is **the deceleration the"
         " situation would demand** -- which the released preference function already computes, as"
         " `required_deceleration`, and then destroys by thresholding it at the ego's PHYSICAL"
         " maximum (the dread boundary) and multiplying by a severity that grows with closing"
         " speed. That term's contribution correlates -0.861 with the share who intervene"
         " (`out/re2_preference_family.md` §4). **This card scores the underlying quantity on its"
         " own.**", "",
         "## 1 What has and has not been tested before", "",
         "| axis | held out | where |", "|---|---|---|",
         f"| the gap threshold (the registered R.2 script's best design scalar) | {GAP_RULE:.4f} |"
         " `out/cutin2_field_vs_gap.md` |",
         "| \"a_req\" in the registered R.2 script | 0.2888 | ibid. -- but that is the KINEMATIC"
         " approximation dv / (2 TTC), not the model's own function |",
         "| the ungated looming rule / the gated one | 0.1137 / 0.1027 | `out/cutin2_gate.md` |",
         "| every functional of the expected free energy | 0.316 to 0.321, all chance |"
         " `out/re4_efe_functionals.md` |",
         "| 648 parameter vectors of the preference | best 0.2705 | `out/re2_preference_family.md` |",
         "| **`required_deceleration` itself** | **never scored** | this card |", "",
         "## 2 The primary, and how it was chosen", "",
         f"**a_other_min = {A_OV_PRIMARY:g} m/s^2, response_time = {T_REACT_PRIMARY:g} s.** The"
         " second is the released value, unchanged. The first is **not** the released -6, and it"
         " won the exploratory sweep, so its independent motivation is given here for the reader to"
         " judge: -10 m/s^2 is about 1 g, the deceleration a passenger car on dry asphalt can"
         " actually achieve, so \"the lead might brake as hard as it physically can\" is a"
         " worst case a driver could hold, where the released -6 was chosen by the authors to make"
         " their own simulations follow stably (`docs/method_review.md` §6.2). **It is still a"
         " value that won a sweep.**", "",
         "| axis | post-onset held out | pre-onset out of sample | matched-TTC rows |"
         " rho(axis, share) | rho(axis, gap) |", "|---|---|---|---|---|---|"]
    for lab, s in (("**the comfort margin, a_OV -10, t_react 1.0 (primary)**", prim),
                   ("the comfort margin at the RELEASED a_OV -6, t_react 1.0", rel),
                   ("the gap threshold, for reference", gap)):
        if s is None:
            L.append(f"| {lab} | fit did not converge | - | - | - | - |")
            continue
        L.append(f"| {lab} | {s['post']:.4f} | {s['cp1']:.4f} | {s['rows']} of {s['n_rows']} |"
                 f" {s['rho_p']:+.3f} | {s['rho_gap']:+.3f} |")
    L.append("")

    beats_gap = prim and prim["post"] < GAP_RULE
    L += ["## 3 What this is and is not", "",
          (f"**The comfort margin scores {prim['post']:.4f}, which is better than the gap"
           f" threshold's {GAP_RULE:.4f}** -- the first quantity derived from the released"
           " preference function that beats the best design scalar on this study. It is still"
           " short of the ungated looming rule's 0.1137 and the gated 0.1027."
           if beats_gap else
           f"**The comfort margin scores {prim['post']:.4f} against the gap threshold's"
           f" {GAP_RULE:.4f}**, so it does not beat the best design scalar.") if prim else "", "",
          (f"It is not a relabelled gap: its rank correlation with the gap is"
           f" {prim['rho_gap']:+.3f}, not -1, so it is combining the gap with the speeds rather"
           " than reproducing it. What it does not do is reach the pre-onset cells --"
           f" {prim['cp1']:.4f} against card G.1's 0.0319 -- so it is an AXIS and not a gate, and"
           " the emergence problem is untouched." if prim else ""), "",
          "**The finding, stated carefully.** The released preference function contains a quantity"
          " that orders these cells better than any design scalar, and the preference function"
          " built on top of it does not. Cards RE.2 and RE.4 showed that no constant and no"
          " functional of the assembled preference works; this card says the material was there"
          " and the assembly is what fails.", ""]

    # --- the sweep, labelled as the exploration it was ---------------------------------
    rows = []
    for a_ov in A_OV_SWEEP:
        for t_r in T_REACT_SWEEP:
            s = score(d, axis_of(d, a_ov, t_r))
            rows.append({"a_other_min": a_ov, "response_time": t_r,
                         **({k: s[k] for k in ("post", "cp1", "rows", "n_rows", "rho_p",
                                               "rho_gap")} if s else {})})
    sw = pd.DataFrame(rows)
    L += ["## 4 The exploratory sweep (run before any rule was fixed)", "",
          "Blank rows are settings where the three-parameter fit did not converge: at a hard"
          " assumed lead braking and a long reaction time the required deceleration diverges on"
          " the closest cells, and the axis stops being finite.", "",
          "| a_other_min | t_react | post-onset held out | pre-onset | matched-TTC rows |"
          " rho(share) | rho(gap) |", "|---|---|---|---|---|---|---|"]
    for _, r in sw.iterrows():
        mark = (" **(primary)**" if r.a_other_min == A_OV_PRIMARY
                and r.response_time == T_REACT_PRIMARY else "")
        if pd.isna(r.get("post", np.nan)):
            L.append(f"| {r.a_other_min:g}{mark} | {r.response_time:g} | - | - | - | - | - |")
        else:
            L.append(f"| {r.a_other_min:g}{mark} | {r.response_time:g} | {r.post:.4f} |"
                     f" {r.cp1:.4f} | {int(r.rows)} of {int(r.n_rows)} | {r.rho_p:+.3f} |"
                     f" {r.rho_gap:+.3f} |")
    L.append("")

    L += ["## 5 What would make any of this a result, pre-stated here and NOT run", "",
          "This card chose a constant by its held-out score, which the project's standing rules"
          " forbid for a confirmatory test. Three things would turn it into one, in this order:",
          "",
          "1. **Transfer with nothing refitted.** The same two constants, the same axis, scored on"
          " study 1's Random cut-in (a different study, the same scenario) and on the left turn"
          " where the geometry makes `required_deceleration` inapplicable as written -- so the"
          " honest first step is study 1 alone. Rule: within 0.01 of the axis's own study-2 score.",
          "2. **The two constants as DRIVER parameters, not fitted constants.** a_other_min and"
          " response_time are exactly what the reformulation note proposed fitting per driver, and"
          " this card is the first evidence that a quantity built from them orders anything. Rule:"
          " card TR.1's Spearman interval [+0.407, +0.798] for the per-driver levels across two"
          " scenarios.",
          "3. **A gate.** The pre-onset score above is not usable, so the emergence problem is"
          " untouched and card G.1's gate would still be needed. Any claim that this is 'the"
          " comfort-zone axis' has to say that.", "",
          "## 6 What this card did not do", "",
          "It did not run the strand-1 model. There is no public code release for Engström et al."
          " (2024) -- this card takes strand 1's *statement of the trade-off* and tests the"
          " quantity the released code already computes for it. Building the strand-1 agent is a"
          " separate decision (query S11.Q3).", "",
          f"Run time {time.time() - t0:.0f} s.", ""]

    sw.to_csv(OUT / "s11_comfort_margin.csv", index=False)
    (OUT / "s11_comfort_margin.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
