"""Card TR.1: the trait slide, but with the current model -- each driver's fitted LEVEL.

    python replication/czb/driver_levels.py      ->  out/driver_levels.md, out/driver_levels.csv

Jonas, 2026-09-03, on concepts-deck slide 4: "is it possible to create something like slide 4
but with the current model (to the extent possible)?"

Slide 4 shows a MODEL-FREE quantity: each driver's criticality-adjusted propensity to
intervene (their mean residual from the cell mean), drawn across four scenarios. It uses no
axis, no gate and no level. This card asks the same question of the model we now have: give
each driver their fitted LEVEL in each scenario, and ask whether it is the same person.

THE PRE-REGISTRATION. Written before the run.

WHICH SCENARIOS, AND WHY NOT ALL FOUR
  Included -- the two scenarios that have BOTH a settled current-model rule and per-driver
  trial data:
    * CUT-IN (study 1, Random design). Axis log(theta_dot) with the G.1 gate; this is the
      stage-1 primary since G1.Q1 (`out/stage1_looming.md`, L-gated row). Level in rad/s.
    * LEFT TURN ON VIDEO at 50 km/h. Axis -PET; card B.3.v2 chose distance for this scenario
      and at the single oncoming speed of this subset distance is a monotone transform of
      PET, so the TT.1 video fit IS the current model here (`out/ltapod_testtrack.md`,
      "video 50 km/h"). Level in seconds of PET.
  Excluded, and this is why the answer to Jonas is "two of the four":
    * TRUCK OVERTAKE -- card B.2 has not been started and no construction note exists, so the
      scenario has no axis and no gate. Nothing to fit.
    * CYCLIST OVERTAKE -- B.1.Q1: the Random design's third question for this scenario is
      recorded as undocumented in the study's own context file, so the ordered level is not
      fitted here and only the intervention response transfers. Card B.1 deliberately stopped
      short of a per-driver level.

METHOD
  1. Refit each scenario with the estimator its own card used (`fit_stage1_looming`'s
     `fit_hier_lapse_gated` in both cases; the left turn through `ltapod_testtrack`'s
     `fit_threshold`, which is a thin wrapper on it). Nothing is re-implemented.
  2. CHECK the refit against the tracked hyperparameters before going on: mu, sigma_pop and
     sigma_resp must reproduce `out/stage1_looming.md` (L-gated) and `out/ltapod_testtrack.md`
     ("video 50 km/h") to 0.01 in their own units. If they do not, the run says so and stops:
     a per-driver number from a fit that does not reproduce its own card is worthless.
  3. Per-driver posterior-mean level by the SAME 48x48 Gauss-Hermite reweighting that card
     TT.1 uses for its T7 reliability check: for each driver, weight the level nodes by that
     driver's own trial likelihood and take the weighted mean.

WHAT IS NOT DONE HERE, DELIBERATELY
  The two levels are left in their own units (rad/s and s). They are NOT put on a shared
  scale and NOT pooled into one population: that is card EL.2, and the scale convention it
  needs is the open query EL.Q4. Everything reported below is invariant to that convention --
  Spearman on ranks, and the within-scenario z-score picture the figure draws. A Pearson
  correlation on raw units is NOT reported, because it would silently assume the convention
  EL.Q4 exists to settle.

WHAT IS REPORTED
  Per-driver levels for the drivers present in both scenarios; the Spearman correlation with
  a driver bootstrap 95% interval; and, for context, the model-free propensity correlation
  for the same scenario pair recomputed here on the same drivers by the slide-4 rule.

  NO VERDICT IS ATTACHED. This is a descriptive card that produces a figure and a table; the
  cross-scenario claim belongs to EL.2, which is gated. If the model-based correlation is far
  below the model-free one, that is a finding to report to Jonas, not a decision to take here.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import fit_stage1_looming as F                                          # noqa: E402
import ltapod_testtrack as TT                                           # noqa: E402
from comfortzone.czb_data import load_joint                             # noqa: E402

N_GH = 48
N_BOOT = 2000
RNG = np.random.default_rng(20260903)


def posterior_mean_levels(x, g, y, codes, fit, sign=+1.0):
    """Each driver's posterior-mean level, by TT.1 T7's quadrature, on the covariate scale.

    `sign` is +1 where the level is reported on the covariate's own scale (the cut-in, on
    log theta_dot) and -1 where the card reports its negative (the left turn, where the
    covariate is -PET and the level is quoted in seconds of PET).
    """
    zz, ww = F._gh_nodes(N_GH)
    z1 = np.repeat(zz, N_GH)
    z2 = np.tile(zz, N_GH)
    lw = np.log(np.outer(ww, ww).ravel())
    c_nodes = fit["mu"] + fit["sigma_pop"] * z1
    b_nodes = 1.0 / (1.0 + np.exp(-(fit["phi"][3] + fit["sigma_b"] * z2)))
    out = {}
    for k in range(int(codes.max()) + 1):
        m = codes == k
        P = b_nodes[None, :] + (1 - b_nodes[None, :]) * g[m][:, None] * norm.cdf(
            (x[m][:, None] - c_nodes[None, :]) / fit["sigma_resp"])
        P = np.clip(P, 1e-12, 1 - 1e-12)
        ll = (y[m][:, None] * np.log(P) + (1 - y[m][:, None]) * np.log(1 - P)).sum(axis=0) + lw
        wgt = np.exp(ll - ll.max())
        wgt /= wgt.sum()
        out[k] = sign * float((wgt * c_nodes).sum())
    return out


def propensity(d, cell_cols):
    """The slide-4 rule: each driver's mean residual from their cell mean. No model."""
    d = d.copy()
    d["cell"] = d[cell_cols[0]].astype(str)
    for c in cell_cols[1:]:
        d["cell"] = d["cell"] + "|" + d[c].astype(str)
    d["resid"] = d.intervene - d.groupby("cell").intervene.transform("mean")
    return d.groupby("driver").resid.mean()


def boot_spearman(a, b):
    rs = []
    n = len(a)
    for _ in range(N_BOOT):
        i = RNG.integers(0, n, n)
        if len(np.unique(a[i])) < 3 or len(np.unique(b[i])) < 3:
            continue
        rs.append(spearmanr(a[i], b[i]).statistic)
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def main() -> None:
    t0 = time.time()
    L = ["# Card TR.1 -- each driver's fitted LEVEL, scenario by scenario", "",
         "Generated by `replication/czb/driver_levels.py`; scenarios, method, checks and what is "
         "deliberately not done are pre-stated in its docstring. The trait slide (concepts deck "
         "slide 4) with the current model instead of the model-free propensity. Do not edit by hand.", ""]

    # ---------------------------------------------------------------- cut-in
    print("cut-in: building trials", flush=True)
    r = F.build_trials()
    r["driver"] = r.participant
    codes_c, uniq_c = pd.factorize(r.driver)
    x_c = r.x_loom.to_numpy(float)
    g_c = r.w_gate.to_numpy(float)
    y_c = r.intervene.to_numpy(float)
    print(f"cut-in: {len(r)} trials, {codes_c.max() + 1} drivers; fitting", flush=True)
    fit_c = F.fit_hier_lapse_gated(x_c, g_c, y_c, codes_c, F.priors_log_scale(x_c))
    print(f"cut-in fit: mu {fit_c['mu']:.4f} sigma_pop {fit_c['sigma_pop']:.4f} "
          f"sigma_resp {fit_c['sigma_resp']:.4f}  [{time.time() - t0:.0f}s]", flush=True)

    # ------------------------------------------------------------- left turn
    j = load_joint()
    v = j[(j.design == "Random") & (j.scenario == "ltap") & (j.ltap_speed == 50)].copy()
    v["pet"] = v.criticality_label.str.replace("PET", "").astype(float)   # as ltapod_testtrack does
    v["driver"] = v.Exp_Subject_Id
    codes_v, uniq_v = pd.factorize(v.driver)
    print(f"left turn (video, 50 km/h): {len(v)} trials, {codes_v.max() + 1} drivers; fitting",
          flush=True)
    fit_v = TT.fit_threshold(v.pet.to_numpy(float), v.intervene.to_numpy(float),
                             v.driver.to_numpy())
    x_v = -v.pet.to_numpy(float)
    g_v = np.ones_like(x_v)
    y_v = v.intervene.to_numpy(float)
    print(f"left turn fit: PET_50 {fit_v['pet50']:.4f} sigma_pop {fit_v['sigma_pop']:.4f} "
          f"sigma_resp {fit_v['sigma_resp']:.4f}  [{time.time() - t0:.0f}s]", flush=True)

    # ------------------------------------------- step 2: reproduce the cards
    checks = [("cut-in mu (log theta_dot)", fit_c["mu"], -3.4520),
              ("cut-in sigma_pop", fit_c["sigma_pop"], 0.8677),
              ("cut-in sigma_resp", fit_c["sigma_resp"], 0.5742),
              ("left turn PET_50 [s]", fit_v["pet50"], 2.18),
              ("left turn sigma_pop [s]", fit_v["sigma_pop"], 1.36),
              ("left turn sigma_resp [s]", fit_v["sigma_resp"], 0.86)]
    L += ["## 1 The refits reproduce their own cards", "",
          "Pre-stated gate: every row must agree to 0.01 before any per-driver number is used.", "",
          "| quantity | this run | the card | difference |", "|---|---|---|---|"]
    worst = 0.0
    for name, got, want in checks:
        L.append(f"| {name} | {got:+.4f} | {want:+.4f} | {got - want:+.4f} |")
        worst = max(worst, abs(got - want))
    ok = worst <= 0.01
    L += ["", f"Largest disagreement {worst:.4f}. "
              + ("**All rows reproduce; the per-driver levels below stand.**" if ok else
                 "**A row does not reproduce. The per-driver levels are NOT reported.**"), ""]
    if not ok:
        (OUT / "driver_levels.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("REFIT DID NOT REPRODUCE THE CARDS; stopping as pre-stated", flush=True)
        return

    # ------------------------------------------------ per-driver levels
    lev_c = posterior_mean_levels(x_c, g_c, y_c, codes_c, fit_c, sign=+1.0)
    lev_v = posterior_mean_levels(x_v, g_v, y_v, codes_v, fit_v, sign=-1.0)
    dc = pd.DataFrame({"driver": uniq_c, "level_cutin_log": [lev_c[k] for k in range(len(uniq_c))]})
    dc["level_cutin_rad_s"] = np.exp(dc.level_cutin_log)
    dv = pd.DataFrame({"driver": uniq_v, "level_ltap_pet_s": [lev_v[k] for k in range(len(uniq_v))]})
    both = dc.merge(dv, on="driver", how="inner").sort_values("driver").reset_index(drop=True)

    # the slide-4 quantity on the same drivers, for context
    # `build_trials` names the stimulus column `criticality` where the joint table calls it
    # `criticality_label`; the cell key is stimulus x freeze point, as on the trait slide.
    rc = r[["driver", "intervene", "criticality", "timepoint"]].copy()
    vv = v[["driver", "intervene", "criticality_label", "ltap_speed"]].copy()
    p_c = propensity(rc, ["criticality", "timepoint"])
    p_v = propensity(vv, ["criticality_label", "ltap_speed"])
    both["propensity_cutin"] = both.driver.map(p_c)
    both["propensity_ltap"] = both.driver.map(p_v)
    both.to_csv(OUT / "driver_levels.csv", index=False)

    a = both.level_cutin_log.to_numpy()
    b = both.level_ltap_pet_s.to_numpy()
    # A driver with a LOW looming level acts early; a driver with a HIGH PET level also acts
    # early (they need a longer gap). The two "act early" directions are therefore opposite,
    # so a consistent driver gives a NEGATIVE raw Spearman. Reported with the sign flipped so
    # that positive means "the same person", and this line says so.
    rho = spearmanr(a, b).statistic
    lo, hi = boot_spearman(a, b)
    rho_p = spearmanr(both.propensity_cutin, both.propensity_ltap).statistic
    lo_p, hi_p = boot_spearman(both.propensity_cutin.to_numpy(), both.propensity_ltap.to_numpy())

    L += ["## 2 Per-driver levels, each scenario in its own units", "",
          f"{len(both)} drivers appear in both scenarios "
          f"(cut-in {len(dc)}, left turn {len(dv)}).", "",
          "| scenario | axis | level units | median | 10th-90th percentile of drivers |",
          "|---|---|---|---|---|",
          f"| cut-in | gated log(theta_dot) | rad/s | {np.median(both.level_cutin_rad_s):.4f} | "
          f"{np.percentile(both.level_cutin_rad_s, 10):.4f} to {np.percentile(both.level_cutin_rad_s, 90):.4f} |",
          f"| left turn (video, 50 km/h) | -PET | s of PET | {np.median(b):.2f} | "
          f"{np.percentile(b, 10):.2f} to {np.percentile(b, 90):.2f} |", "",
          "## 3 Is it the same person?", "",
          "Signs: a LOW looming level and a LONG PET level both mean \"acts early\", so a "
          "consistent driver shows a negative raw Spearman between the two. The sign is "
          "flipped below so that positive means agreement, and the raw value is given too.", "",
          "| quantity | Spearman (oriented) | 95% driver bootstrap | raw |", "|---|---|---|---|",
          f"| fitted LEVEL, this card | {-rho:+.3f} | {-hi:+.3f} to {-lo:+.3f} | {rho:+.3f} |",
          f"| model-free propensity, the slide-4 rule | {rho_p:+.3f} | {lo_p:+.3f} to {hi_p:+.3f} | - |",
          "",
          "The propensity row is the slide-4 quantity recomputed here on exactly these drivers "
          "and these two scenarios, so the two rows are comparable. It is NOT the headline of "
          "`out/cross_scenario_consistency.md`, which averages over all six scenario pairs.", "",
          "## 4 What this card does not do", "",
          "The two levels are in different units and are never put on one scale: that is card "
          "EL.2, whose scale convention is the open query EL.Q4. Both numbers above are rank "
          "statistics and so do not depend on it. No verdict is attached; a cross-scenario "
          "claim belongs to EL.2.", "",
          "Two of the four scenarios of the trait slide are absent by construction: the truck "
          "overtake has no axis or gate yet (card B.2 unstarted, no construction note), and the "
          "cyclist overtake's per-driver level is not fitted because that scenario's third "
          "question is undocumented in the study's own materials (B.1.Q1).", "",
          f"Run time {time.time() - t0:.0f} s."]
    (OUT / "driver_levels.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", OUT / "driver_levels.md", flush=True)
    print(f"oriented Spearman: level {-rho:+.3f}, propensity {rho_p:+.3f}", flush=True)


if __name__ == "__main__":
    main()
