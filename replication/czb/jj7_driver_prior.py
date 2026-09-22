"""
Card JJ.7 -- the comfort-zone boundary as a driver's prior over looming, gated by the predictive
lateral uncertainty: the per-driver levels restated, and the trait re-checked.

THE PRE-REGISTRATION. Written before the run, on 2026-09-22.

WHY. `docs/looming_as_free_energy.md` section 4 and card JJ.10: the measurement model IS the free
energy of the present looming observation under a driver's one-sided prior over the looming of a
lead, with the lead's status predicted by the generative model (card JJ.6e's gate, m = 0, nothing
from G.1 but sigma_lat). Card TR.1 (`driver_levels.py`) fitted each driver's LEVEL on the cut-in
(study 1, the Random design) with card G.1's gate (m_lat 0.149, s_l 0.990) and found the levels
agree with the left-turn levels at Spearman +0.647 [+0.407, +0.798] over 43 drivers. This card
refits the same hierarchical model with the DERIVED gate and reads the result in the new words:
mu is the population's median prior over looming, sigma_pop the spread of that prior across
drivers, sigma_resp its within-driver precision, and a driver's posterior-mean level is that
driver's prior. Jonas, 2026-09-22, decision 6: yes.

WHAT IS COMPUTED. `fit_stage1_looming.build_trials` (study 1's trials with x_loom, l0, ldot), the
gate column replaced by `comfort_fe.p_lead(l0, ldot, 0.33, 3.0, margin_m=0)`, fitted with
`fit_hier_lapse_gated` and `priors_log_scale` exactly as TR.1; per-driver posterior-mean levels
by TR.1's `posterior_mean_levels`; the left-turn levels read from `out/driver_levels.csv` (TR.1's
tracked output; not refitted, nothing on that side changes).

THE RULES.
  (0) Reproduction: the same fit with TR.1's gate (`w_gate`) reproduces TR.1's mu -3.4520,
      sigma_pop 0.8677, sigma_resp 0.5742 to 0.01 (TR.1's own criterion).
  (1) The derived-gate levels agree with TR.1's cut-in levels at Spearman above +0.95 over the
      43 drivers (it is the same model with the gate's margin moved by 0.149 m; anything less
      says the margin matters per driver, which would be a finding).
  (2) The trait: the derived-gate cut-in levels against TR.1's left-turn levels, Spearman inside
      TR.1's interval [+0.407, +0.798].
  Verdict: RESTATED if (0), (1), (2). Otherwise the failing rule is named; no other verdict.

PREDICTIONS. (0) exact. (1) above +0.98. (2) within 0.03 of +0.647. The hyperparameters move by
less than 0.05 in mu (the gate with m = 0 is slightly lower everywhere, so the level shifts down
a little) and less than 0.02 in the two spreads.

Output: replication/czb/out/jj7_driver_prior.md, out/jj7_driver_prior.csv
Run:    python replication/czb/jj7_driver_prior.py    (background; 5 to 35 minutes per fit)
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

import driver_levels as TR1                # noqa: E402  card TR.1 (read only)
import fit_stage1_looming as F             # noqa: E402
from rollout.comfort_fe import SIGMA_LAT, T_ANTICIPATION, p_lead  # noqa: E402

OUT = HERE / "out"
TR1_HYPER = {"mu": -3.4520, "sigma_pop": 0.8677, "sigma_resp": 0.5742}
TR1_TRAIT = (0.647, 0.407, 0.798)


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    r = F.build_trials()
    r["driver"] = r.participant
    codes, uniq = pd.factorize(r.driver)
    x = r.x_loom.to_numpy(float)
    y = r.intervene.to_numpy(float)
    g_tr1 = r.w_gate.to_numpy(float)
    g_new = np.asarray(p_lead(r.l0.to_numpy(float), r.ldot.to_numpy(float), SIGMA_LAT,
                              T_ANTICIPATION, margin_m=0.0), float)
    print(f"{len(r)} trials, {codes.max() + 1} drivers; gate mean TR.1 {g_tr1.mean():.3f},"
          f" derived {g_new.mean():.3f}; fitting TR.1's gate", flush=True)
    fit0 = F.fit_hier_lapse_gated(x, g_tr1, y, codes, F.priors_log_scale(x))
    print(f"TR.1 gate: mu {fit0['mu']:.4f} sp {fit0['sigma_pop']:.4f} sr {fit0['sigma_resp']:.4f}"
          f" [{time.time() - t0:.0f} s]; fitting the derived gate", flush=True)
    fit1 = F.fit_hier_lapse_gated(x, g_new, y, codes, F.priors_log_scale(x))
    print(f"derived gate: mu {fit1['mu']:.4f} sp {fit1['sigma_pop']:.4f} sr {fit1['sigma_resp']:.4f}"
          f" [{time.time() - t0:.0f} s]", flush=True)
    rule0 = all(abs(fit0[k] - v) <= 0.01 for k, v in TR1_HYPER.items())

    lev0 = TR1.posterior_mean_levels(x, g_tr1, y, codes, fit0, sign=+1.0)
    lev1 = TR1.posterior_mean_levels(x, g_new, y, codes, fit1, sign=+1.0)
    d = pd.DataFrame({"driver": uniq, "level_tr1_gate_log": [lev0[k] for k in range(len(uniq))],
                      "prior_log": [lev1[k] for k in range(len(uniq))]})
    d["prior_rad_s"] = np.exp(d.prior_log)
    tr1 = pd.read_csv(OUT / "driver_levels.csv")
    both = d.merge(tr1[["driver", "level_cutin_log", "level_ltap_pet_s"]], on="driver", how="inner")
    both.to_csv(OUT / "jj7_driver_prior.csv", index=False)
    rho1 = float(spearmanr(both.prior_log, both.level_cutin_log).statistic)
    rho2 = float(spearmanr(both.prior_log, both.level_ltap_pet_s).statistic)
    lo, hi = TR1.boot_spearman(both.prior_log.to_numpy(float), both.level_ltap_pet_s.to_numpy(float))
    rule1 = rho1 > 0.95
    rule2 = TR1_TRAIT[1] <= rho2 <= TR1_TRAIT[2]
    verdict = "RESTATED" if rule0 and rule1 and rule2 else "NOT RESTATED"

    L = ["# Card JJ.7 -- the boundary as a driver's prior over looming, gated by predictive"
         " lateral uncertainty", "",
         "Generated by `replication/czb/jj7_driver_prior.py`; the construction, the rules and the"
         " predictions were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "Card TR.1's hierarchical fit of study 1's cut-in trials, with card G.1's gate replaced by"
         " the derived gate of card JJ.6e (sigma_lat 0.33 m/s, 3 s, no margin), read as: mu the"
         " population's median prior over the looming of a lead, sigma_pop its spread across"
         " drivers, sigma_resp its within-driver precision, and each driver's posterior-mean level"
         " that driver's prior.", "",
         "## 0 Reproduction of card TR.1", "",
         "| hyperparameter | TR.1's gate, this run | TR.1 on file | the derived gate |",
         "|---|---|---|---|"]
    for k, lab in (("mu", "mu, log rad/s"), ("sigma_pop", "sigma_pop"), ("sigma_resp", "sigma_resp")):
        L.append(f"| {lab} | {fit0[k]:+.4f} | {TR1_HYPER[k]:+.4f} | {fit1[k]:+.4f} |")
    L += ["", f"Rule 0 {'PASSES' if rule0 else 'FAILS'} (0.01). Population median prior over"
          f" looming: {np.exp(fit1['mu']):.4f} rad/s (TR.1's gate: {np.exp(fit0['mu']):.4f}).", "",
          "## 1 The per-driver priors", "",
          f"{len(both)} drivers in both scenarios. Spearman of the derived-gate priors with TR.1's"
          f" cut-in levels: **{rho1:+.3f}** (rule 1: above +0.95, {'holds' if rule1 else 'fails'})."
          f" With TR.1's left-turn levels (the trait): **{rho2:+.3f}** [{lo:+.3f}, {hi:+.3f}]"
          f" against TR.1's +0.647 [+0.407, +0.798] (rule 2: {'holds' if rule2 else 'fails'}).", "",
          f"| percentile of drivers | prior over looming [rad/s] |", "|---|---|"]
    for q in (10, 25, 50, 75, 90):
        L.append(f"| {q} | {np.percentile(both.prior_rad_s, q):.4f} |")
    L += ["", "## 2 The verdict", "",
          f"**{verdict}.** " + ("The comfort-zone boundary on the cut-in is, in these words, a"
          " driver's prior over the looming of a lead; its population is the deliverable's"
          " percentile; the gate that says when the prior applies is the generative model's"
          " predictive lateral uncertainty; and the prior is the same person's across two"
          " scenarios to the extent TR.1 found. Nothing new is fitted; the words change, and the"
          " change is now backed by cards JJ.6e, JJ.8 and JJ.10 rather than assumed."
          if verdict == "RESTATED" else "The failing rule is named above."), "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj7_driver_prior.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
