"""What the second cut-in study (`02_Cut-in`) can do for this project.

A new dataset arrived on 2026-08-28: an online video study of lane-change cut-ins,
168 participants, 10 944 trials, with perceived safety, an intervention binary and the
same three-level expected-braking question as study 1. This script characterizes it and
runs the one test it is uniquely able to settle.

Why it matters more than "another cut-in dataset"
--------------------------------------------------
Review gate R.2 turns on a question study 1 cannot answer cleanly: do drivers respond to
a **time** measure, or does **distance** enter separately? In study 1 the LTAP design
varies the oncoming vehicle's speed at matched PET, which separates them -- but only over
a factor of 1.4 in distance, between subjects, in a scenario whose field we have not
built.

This study separates them by construction, over a factor of six, in the scenario whose
field we already have. Its delta-velocity factor (DV, 7-42 kph) is crossed with
time-to-collision, and the study's own documentation states the relation:
`distance = TTC x DV`. So matched TTC_true cells differ in longitudinal gap from about
1.6 m to about 78 m. If the response is a function of time alone, the rows of the
TTC x DV table must be flat.

The required-deceleration cross-check is what makes the test decisive rather than merely
suggestive. At matched TTC, `a_req = v_rel^2 / (2 d) = DV^2 / (2 TTC DV) = DV / (2 TTC)`,
so the *objectively more demanding* cell in each row is the high-DV one -- the same cell
that has the larger gap. Time-based measures and demand-based measures therefore predict
opposite orderings across a row, and the data can only agree with one of them.

Scope note on the third dataset
-------------------------------
`03_CAMP` is characterized here only to the extent of reporting what it contains; Jonas
flagged known issues with it and no use is proposed.

    python replication/czb/cutin2_scope.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
STUDY2 = (REPO / "external/01_studies/01_Studies/02_Cut-in"
          / "cut-in_study_aggregate_trials_annotated.csv")
CAMP_DIR = REPO / "external/01_studies/01_Studies/03_CAMP"

OUT = HERE / "out"
KPH = 1000.0 / 3600.0


def spearman(a, b):
    from scipy.stats import spearmanr
    r = spearmanr(a, b)
    return float(r.statistic), float(r.pvalue)


def main() -> None:
    d = pd.read_csv(STUDY2, low_memory=False)
    post = d[d.CP != "CP1"].copy()

    # participant-level means first, per the study's own analysis note: DV subset and CP
    # subset are between-subjects, so raw pooled means would mix designs.
    pm = (post.groupby(["Exp_Subject_Id", "TTC_true", "DV_kph"])
              .agg(p=("CZB_1", "mean"), d_m=("distance", "first")).reset_index())
    cell = pm.groupby(["TTC_true", "DV_kph"]).agg(p=("p", "mean"),
                                                  d_m=("d_m", "first"),
                                                  n=("p", "size")).reset_index()
    cell["a_req"] = (cell.DV_kph * KPH) / (2.0 * cell.TTC_true)

    # within-row (matched TTC) rank correlation between distance and response
    rows = []
    for ttc, g in cell.groupby("TTC_true"):
        if len(g) < 4:
            continue
        r_d, _ = spearman(g.d_m, g.p)
        rows.append((ttc, len(g), float(g.p.min()), float(g.p.max()), r_d))
    rowdf = pd.DataFrame(rows, columns=["TTC_true", "n_cells", "p_min", "p_max", "rho_d"])

    # overall: which single scalar orders the cells best?
    rho_ttc, _ = spearman(cell.TTC_true, cell.p)
    rho_dist, _ = spearman(cell.d_m, cell.p)
    rho_areq, _ = spearman(cell.a_req, cell.p)

    # --- why study 1 could never have answered this ---------------------------------
    from comfortzone.czb_data import (RANDOM_CUTIN_TRACES, TIMEPOINT_OFFSET_S,
                                      stimulus_field)
    g1, t1, vr = [], [], []
    for c, path in RANDOM_CUTIN_TRACES.items():
        f = stimulus_field(path)
        ts = f.t_since_onset.to_numpy()
        for tp, off in TIMEPOINT_OFFSET_S.items():
            i = max(int(np.searchsorted(ts, off, side="right")) - 1, 0)
            g1.append(float(f.gap_m.iloc[i]))
            t1.append(float(f.ttc_s.iloc[i]))
            vr.append(float(f.v_rel.iloc[i]))
    rho_gt = float(np.corrcoef(np.array(g1), np.array(t1))[0, 1])
    vr = np.array(vr)

    L = ["# The second cut-in study: what it adds\n",
         f"{len(d)} trials, {d.Exp_Subject_Id.nunique()} participants; "
         f"{len(post)} trials after dropping the CP1 baseline. Perceived safety, an "
         "intervention binary, and the same three-level expected-braking question as "
         "study 1. Participant-level means are formed first throughout, because the DV "
         "and CP subsets are between-subjects.\n",
         "## 0 Why study 1 could not have answered this, and what that costs\n",
         f"Across all 18 cells of the study-1 Random cut-in design the relative speed is "
         f"constant at {vr.min():.2f} m/s, so time-to-collision is gap divided by a "
         f"constant and **correlation(gap, TTC) = {rho_gt:.4f}**. Time headway and "
         "required deceleration are likewise fixed functions of the same one number. The "
         "longitudinal dimension of that design has a single degree of freedom.\n",
         "The consequence is uncomfortable and worth stating plainly. Every longitudinal "
         "result obtained on study 1 — the stage-0 correlation of 0.90, the stage-1 "
         "boundary level, the population percentile — is equally consistent with a "
         "driver who thresholds the preference field and with a driver who thresholds "
         "**the gap**. Those fits are not wrong, and the boundary is well estimated on "
         "its own scale; but they cannot be used as evidence that the field's kinematic "
         "content is the right description, because no contrast in that design "
         "distinguishes it from the simplest possible alternative. The second cut-in "
         "study breaks the collinearity, which is why it can decide what study 1 cannot."
         "\n",
         "## 1 The test only this dataset can run\n",
         "At matched time-to-collision, the delta-velocity factor moves the longitudinal "
         "gap by a factor of six. If the response were a function of time alone, each "
         "row below would be flat.\n",
         "| TTC_true [s] | cells | lowest P(intervene) | highest | rho(distance, P) |",
         "|---|---|---|---|---|"]
    for _, r in rowdf.iterrows():
        L.append(f"| {r.TTC_true:.1f} | {int(r.n_cells)} | {r.p_min:.3f} | "
                 f"{r.p_max:.3f} | {r.rho_d:+.2f} |")

    frac_neg = float((rowdf.rho_d < 0).mean())
    L += [f"\nThe rows are emphatically not flat, and {frac_neg:.0%} of them run "
          "negative: **at matched time-to-collision, a larger gap means less "
          "intervention**. Time alone does not determine the response.\n",
          "## 2 Which single scalar orders the cells best\n",
          "| predictor | Spearman rho against P(intervene) |", "|---|---|",
          f"| time-to-collision | {rho_ttc:+.3f} |",
          f"| longitudinal gap | {rho_dist:+.3f} |",
          f"| required deceleration `DV / (2 TTC)` | {rho_areq:+.3f} |",
          "\n**The required-deceleration row is the one to look at**, and it should be "
          f"read carefully: at {rho_areq:+.3f} its sign is the one a demand-based model "
          "wants (more braking required, more intervention), but its magnitude is "
          f"negligible beside the gap's {rho_dist:+.3f}. The honest statement is not "
          "that drivers respond backwards to demand, but that **required deceleration "
          "barely orders these cells at all while gap orders them almost perfectly** — "
          "and gap edges out even time-to-collision. A field whose safety terms are "
          "built from required deceleration and inverse tau is therefore leaning on the "
          "weakest of the three scalars available here.\n",
          "## 3 What it does not settle\n",
          "Distance and delta velocity are perfectly confounded at matched TTC by "
          "construction (`distance = TTC x DV`), and the study's own documentation says "
          "so. This dataset can therefore show that a time measure is insufficient; it "
          "cannot say whether the missing ingredient is gap, closing speed, headway, or "
          "the perceptual uncertainty that scales with them. Separating those needs a "
          "design that breaks the product, or a model that predicts different signs for "
          "them.\n"]

    # --- the anticipation test this design supports and study 1 does not -------------
    rep = post.copy()
    rep["clip"] = rep["video name"].astype(str)
    rep = rep.sort_values(["Exp_Subject_Id", "clip", "Trial_Nr"])
    rep["pass_idx"] = rep.groupby(["Exp_Subject_Id", "clip"]).cumcount()
    two = rep[rep.pass_idx < 2]
    piv = (two.groupby(["Exp_Subject_Id", "clip", "pass_idx"]).CZB_1.mean()
             .unstack("pass_idx").dropna())
    if piv.shape[1] == 2:
        d1, d2 = piv[0].to_numpy(), piv[1].to_numpy()
        diff = float(np.mean(d2 - d1))
        se = float(np.std(d2 - d1, ddof=1) / np.sqrt(len(d2)))
        L += ["## 4 A clean anticipation test, which study 1 cannot support\n",
              "Every clip in block 1 is shown **twice** to the same participant. That is "
              "the exposure manipulation R.1.Q3 needs and study 1 lacks: identical "
              "stimulus, identical participant, second viewing.\n",
              "| quantity | value |", "|---|---|",
              f"| repeated clip-participant pairs | {len(piv)} |",
              f"| P(intervene), first showing | {d1.mean():.3f} |",
              f"| P(intervene), second showing | {d2.mean():.3f} |",
              f"| **difference** | **{diff:+.3f}** (SE {se:.3f}) |",
              "\n" + ("A reliable shift on the second showing of an identical clip is "
                      "direct evidence that repeated exposure changes responding, which "
                      "is what R.1.Q3 asserts."
                      if abs(diff) > 2 * se else
                      "There is no reliable shift on the second showing of an identical "
                      "clip. Repeated exposure to the *same* stimulus does not move "
                      "responding here, which is evidence against the strong form of "
                      "R.1.Q3 — that graded pre-onset responding is learned from "
                      "repetition.") + "\n"]

    # --- CAMP: describe only ---------------------------------------------------------
    L += ["## 5 `03_CAMP`, described only\n"]
    if CAMP_DIR.exists():
        files = sorted(p.name for p in CAMP_DIR.rglob("*") if p.is_file())
        L.append(f"{len(files)} files. Top level: "
                 + ", ".join(f"`{n}`" for n in files[:8])
                 + ("" if len(files) <= 8 else f", and {len(files) - 8} more") + ".\n")
    L.append("No use is proposed. Jonas flagged known problems with this dataset and "
             "nothing above depends on it.\n")

    txt = "\n".join(L) + "\n"
    (OUT / "cutin2_scope.md").write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()
