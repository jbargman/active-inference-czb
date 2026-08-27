"""Card R.1: the diagnostics behind the A.2.Q2 bias-variant decision.

Card A.2 left one blocking question open (query A.2.Q2): the group-level and the
hierarchical lapse give between-driver spreads of 0.341 and 0.209 -- a 39% difference in
the quantity every percentile is made of -- while held-out likelihood separates them by
only +0.6 units. This script produces the evidence that lets the review gate decide,
rather than re-litigating the held-out comparison. It also runs the check card A.2 owed
(query A.2.Q3): the pre-onset predictive under *both* bias variants -- and runs it
correctly, because the stage-1 report's C1 check plugged in the hierarchical variant's
*median* lapse (sigmoid of the location, 0.017) where the population-averaged predictive
requires the *mean* over the lapse distribution, which with a logit-scale sd of 2.76 is
several times larger. That distinction turns out to matter.

The three questions, each with a pre-stated reading
----------------------------------------------------
1. **Is per-driver lapse heterogeneity real?** Compare the spread of per-driver
   pre-onset (C1) intervention rates with what a shared binomial rate would produce
   (Monte Carlo under the pooled rate, seed fixed). If the observed spread is far
   outside the binomial band, a single group-level lapse is misspecified as a matter of
   data, before any model comparison.
2. **Does the group model leak pre-onset behavior into the thresholds?** The roadmap
   (`docs/czb_validation_roadmap.md` section 5.1) predicted: if leakage is real, the
   group variant shows a *wider* fitted sigma_pop than the shrinkage variant, and its
   per-driver thresholds correlate with per-driver C1 rates. Both signatures are
   computed here. (Note the direction: the executing session's query A.2.Q2 read the
   observed ordering -- group 0.341 > hier 0.209 -- as *contradicting* section 5.1; it
   is in fact the ordering section 5.1 predicted under leakage.)
3. **Where does the group model's extra spread live?** Refit both variants with the C1
   cells excluded. If the group variant's sigma_pop falls toward the hierarchical value
   once the pre-onset cells are gone, the difference between the variants is C1 leakage
   and the hierarchical spread is the honest one; if it stays near 0.341, the
   hierarchical lapse is absorbing genuine threshold variation and the group spread is
   the honest one.

Parameter motivations
---------------------
* Priors: `priors_for` on the full covariate, identical for every fit in this script,
  including the no-C1 refits -- the refit comparison must isolate the change in data,
  not a change in prior scale. All other estimation settings inherit from cards A.1/A.2
  unchanged (150 Gauss-Hermite nodes in 1D, 48 per dimension in 2D), so the recovery
  evidence carries over.
* Overdispersion Monte Carlo: 4000 replicates, seed 0. 4000 puts the standard error of
  a p-value near 0.005 at p = 0.10, sufficient for a yes/no reading.

    python replication/czb/bias_variant_diagnostics.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from comfortzone.czb_data import random_cutin_trials                          # noqa: E402
from fit_recovery import NORMAL, _gh_nodes, fit_marginal, priors_for          # noqa: E402
from fit_stage1 import N_GH_2D, fit_hier_lapse, percentiles_with_ci           # noqa: E402

OUT = HERE / "out"
torch.set_default_dtype(torch.float64)

N_MC = 4000
SEED = 0


def _ncdf(z):
    from scipy.stats import norm
    return norm.cdf(z)


def overdispersion(counts: np.ndarray, n_trials: np.ndarray,
                   rng: np.random.Generator) -> dict:
    """Observed spread of per-driver C1 rates against a shared-rate binomial."""
    rates = counts / n_trials
    p_pool = counts.sum() / n_trials.sum()
    obs_sd = float(rates.std(ddof=1))
    sims = np.empty(N_MC)
    for k in range(N_MC):
        sims[k] = (rng.binomial(n_trials, p_pool) / n_trials).std(ddof=1)
    return {"p_pool": float(p_pool), "obs_sd": obs_sd,
            "sim_sd_mean": float(sims.mean()),
            "sim_sd_q95": float(np.quantile(sims, 0.95)),
            "p_value": float((sims >= obs_sd).mean())}


def hier_posterior_effects(f: dict, x, y, pid, n_drivers) -> tuple[np.ndarray, np.ndarray]:
    """Posterior mean threshold c_i and lapse b_i per driver, hierarchical variant.

    Same 2D Gauss-Hermite grid as the fit; posterior weights per driver are the
    normalized per-node likelihood times the prior weight.
    """
    phi = f["phi"]
    zz, ww = _gh_nodes(N_GH_2D)
    z1 = np.repeat(zz, N_GH_2D)
    z2 = np.tile(zz, N_GH_2D)
    lw = np.log(np.outer(ww, ww).ravel())
    c = np.exp(phi[0] + f["sigma_pop"] * z1)
    b = 1.0 / (1.0 + np.exp(-(phi[3] + f["sigma_b"] * z2)))
    p = b[None, :] + (1 - b[None, :]) * _ncdf((x[:, None] - c[None, :]) / f["sigma_resp"])
    p = np.clip(p, 1e-12, 1 - 1e-12)
    ll = y[:, None] * np.log(p) + (1 - y[:, None]) * np.log1p(-p)
    per_driver = np.zeros((n_drivers, len(z1)))
    np.add.at(per_driver, pid, ll)
    per_driver += lw[None, :]
    per_driver -= per_driver.max(axis=1, keepdims=True)
    w = np.exp(per_driver)
    w /= w.sum(axis=1, keepdims=True)
    return w @ c, w @ b


def c1_predictive_proper(f: dict, variant: str, xv: float) -> float:
    """Population-averaged P(intervene) at a pre-onset cell, integrating ALL random
    effects -- including the lapse distribution in the hierarchical variant."""
    zz, ww = _gh_nodes(150)
    c = np.exp(f["mu"] + f["sigma_pop"] * zz)
    if variant == "group":
        b = np.full_like(c, f["b"])
        p = b + (1 - b) * _ncdf((xv - c) / f["sigma_resp"])
        return float((p * ww).sum())
    # hierarchical: independent effects, so integrate on the product grid
    b_nodes = 1.0 / (1.0 + np.exp(-(f["phi"][3] + f["sigma_b"] * zz)))
    p = b_nodes[None, :] + (1 - b_nodes[None, :]) \
        * _ncdf((xv - c[:, None]) / f["sigma_resp"])
    return float((ww[:, None] * ww[None, :] * p).sum())


def spearman(a, b) -> float:
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).statistic)


def main() -> None:
    t0 = time.time()
    r = random_cutin_trials()
    pid = r.participant.factorize()[0].astype(int)
    n_drivers = int(pid.max() + 1)
    x = r.deficit_max.to_numpy(float)
    y = r.intervene.to_numpy(float)
    pre = (r.timepoint == "C1").to_numpy()
    pr = priors_for(x)

    # ---- 1: is per-driver lapse heterogeneity real? ----
    counts = np.array([y[pre & (pid == i)].sum() for i in range(n_drivers)])
    ntr = np.array([(pre & (pid == i)).sum() for i in range(n_drivers)])
    od = overdispersion(counts, ntr, np.random.default_rng(SEED))
    print(f"C1 per-driver rate sd {od['obs_sd']:.3f} vs binomial "
          f"{od['sim_sd_mean']:.3f} (95th pct {od['sim_sd_q95']:.3f}), "
          f"p = {od['p_value']:.4f}", flush=True)

    # ---- fits: both variants, full data ----
    print("fitting group variant (full data) ...", flush=True)
    fg = fit_marginal(x, y, pid, pr)
    print(f"  sigma_pop = {fg['sigma_pop']:.3f}", flush=True)
    print("fitting hierarchical variant (full data) ...", flush=True)
    fh = fit_hier_lapse(x, y, pid, pr)
    print(f"  sigma_pop = {fh['sigma_pop']:.3f}", flush=True)

    # population-mean lapse under the hierarchical variant
    zz, ww = _gh_nodes(150)
    b_mean_h = float((1.0 / (1.0 + np.exp(-(fh["phi"][3] + fh["sigma_b"] * zz))) * ww).sum())

    # ---- 2: leakage signatures ----
    ch_i, bh_i = hier_posterior_effects(fh, x, y, pid, n_drivers)
    c1_rate = counts / ntr
    post_rate = np.array([y[~pre & (pid == i)].mean() for i in range(n_drivers)])
    rho_g = spearman(c1_rate, fg["c_i"])
    rho_h = spearman(c1_rate, ch_i)
    rho_bc = spearman(bh_i, ch_i)
    rho_cp = spearman(c1_rate, post_rate)

    # ---- proper C1 predictive, both variants (the owed A.2.Q3 check) ----
    c1_rows = []
    for crit in ("TTC4", "TTC6", "TTC8"):
        m = pre & (r.criticality == crit).to_numpy()
        xv = float(x[m][0])
        c1_rows.append((crit, float(y[m].mean()),
                        c1_predictive_proper(fg, "group", xv),
                        c1_predictive_proper(fh, "hier", xv)))

    # ---- 3: refits without the C1 cells ----
    keep = ~pre
    pid_k = pid[keep]        # all 43 drivers retain their 60 post-onset trials
    print("refitting both variants without the C1 cells ...", flush=True)
    fg_nc = fit_marginal(x[keep], y[keep], pid_k, pr)
    print(f"  group   sigma_pop = {fg_nc['sigma_pop']:.3f}", flush=True)
    fh_nc = fit_hier_lapse(x[keep], y[keep], pid_k, pr)
    print(f"  hier    sigma_pop = {fh_nc['sigma_pop']:.3f}", flush=True)

    # ---- percentile consequence of the choice ----
    pcts = {}
    for name, f in (("group", fg), ("hier", fh)):
        pcts[name] = {q: (v, lo, hi) for q, v, lo, hi in percentiles_with_ci(f)}

    # ---- report ----
    L = ["# Card R.1 — bias-variant diagnostics (the A.2.Q2 decision)\n",
         "Three questions, each with its reading stated in the script docstring before "
         "the numbers were seen. All fits use card A.1/A.2's estimator and priors "
         "unchanged; the no-C1 refits reuse the full-data priors so the comparison "
         "isolates the change in data.\n",
         "## 1 Per-driver pre-onset heterogeneity against a shared rate\n",
         f"Pooled C1 rate {od['p_pool']:.3f}. Observed sd of per-driver C1 rates "
         f"**{od['obs_sd']:.3f}** against a shared-rate binomial's "
         f"{od['sim_sd_mean']:.3f} (95th percentile {od['sim_sd_q95']:.3f}); Monte Carlo "
         f"p = {od['p_value']:.4f} ({N_MC} replicates, seed {SEED}).\n",
         "## 2 Leakage signatures\n",
         "| quantity | value |", "|---|---|",
         f"| Spearman rho, per-driver C1 rate vs fitted c_i (group variant) | {rho_g:+.3f} |",
         f"| Spearman rho, per-driver C1 rate vs fitted c_i (hier variant) | {rho_h:+.3f} |",
         f"| Spearman rho, fitted b_i vs fitted c_i (hier variant) | {rho_bc:+.3f} |",
         f"| Spearman rho, per-driver C1 rate vs post-onset rate | {rho_cp:+.3f} |",
         "\nUnder leakage, the group variant's thresholds should track pre-onset "
         "behavior (negative rho: pressing early at C1 pulls the fitted threshold "
         "down); the hierarchical variant gives that behavior somewhere else to go.\n",
         "## 3 The C1 predictive under both variants, integrated properly\n",
         "The stage-1 report's C1 table used the hierarchical variant's *median* lapse "
         f"(0.017); the population-averaged predictive integrates the lapse "
         f"distribution, whose mean is **{b_mean_h:.3f}** against an observed pooled "
         f"pre-onset rate of {od['p_pool']:.3f}.\n",
         "| criticality | observed | group predicts | hier predicts |",
         "|---|---|---|---|"]
    for crit, obs, pg, ph in c1_rows:
        L.append(f"| {crit} | {obs:.3f} | {pg:.3f} | {ph:.3f} |")
    L += ["\n## 4 Where the spread lives: refits without the C1 cells\n",
          "| fit | sigma_pop, full data | sigma_pop, C1 excluded |",
          "|---|---|---|",
          f"| group lapse | {fg['sigma_pop']:.3f} | {fg_nc['sigma_pop']:.3f} |",
          f"| hierarchical lapse | {fh['sigma_pop']:.3f} | {fh_nc['sigma_pop']:.3f} |",
          "\n## 5 What the choice does to the deliverable\n",
          "| percentile | group variant | hierarchical variant |",
          "|---|---|---|"]
    for q in (50, 80, 95):
        g, h = pcts["group"][q], pcts["hier"][q]
        L.append(f"| {q}th | {g[0]:.0f} [{g[1]:.0f}, {g[2]:.0f}] "
                 f"| {h[0]:.0f} [{h[1]:.0f}, {h[2]:.0f}] |")
    L.append(f"\nRuntime {(time.time() - t0) / 60:.1f} min.")

    txt = "\n".join(L) + "\n"
    (OUT / "bias_variant_diagnostics.md").write_text(txt, encoding="utf-8")
    print(f"written to {OUT / 'bias_variant_diagnostics.md'} "
          f"({(time.time() - t0) / 60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
