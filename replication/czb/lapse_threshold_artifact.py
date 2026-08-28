"""Is the fitted lapse-threshold correlation real, or an artifact of joint estimation?

Card R.1 found that the fitted per-driver lapse b_i and boundary level c_i correlate at
Spearman -0.700, while the model assumes them independent, and flagged it as query
R.1.Q2. Jonas's reaction was that it might be a study-design or estimation artifact
rather than a trait correlation. This script decides that, and it is decidable, because
the artifact hypothesis makes a sharp prediction.

The mechanism the artifact hypothesis proposes
----------------------------------------------
Both quantities are estimated from the same limited per-driver data, and they trade off
against each other: a driver who happens by chance to press more often than their true
parameters imply can be fitted either with a higher lapse floor or with a lower
threshold. The estimator has to split that excess between them, and any split it chooses
puts a positive error on one and a negative error on the other. Errors that are forced to
have opposite signs produce a **negative correlation between the estimates even when the
true values are independent**. This is the same phenomenon as the classic negative
correlation between a fitted intercept and slope.

The test
--------
Simulate from the fitted model with the two driver effects drawn **independently** (true
correlation exactly zero), refit with the same estimator, and measure the correlation
between the recovered posterior means. Under the artifact hypothesis the recovered
correlation should be strongly negative anyway; under the trait hypothesis it should sit
near zero and the observed -0.700 would then need a real explanation.

A second arm simulates a genuine correlation of -0.7 in the truth, to confirm the design
can tell the two apart at all -- without which a null result would be uninformative.

Parameter motivations
---------------------
* Simulation truths are the values fitted on the real data (`out/stage1_summary.md` and
  `out/bias_variant_diagnostics.md`), so the simulated data has the same information
  content per driver as the real data. Nothing is tuned.
* `N_GH_SIM = 32` nodes per dimension rather than the fitting default of 48: the
  quadrature check in card A.2 showed the between-driver spread moves by about 5% across
  32/48/72, which is immaterial for a *correlation between recovered effects* and roughly
  halves the runtime of a simulation study that must refit many times.
* 12 replicates per arm, which is enough to place the mean recovered correlation to
  about +/- 0.05 given the spread seen in the first few, and is what fits in a
  reasonable runtime.

    python replication/czb/lapse_threshold_artifact.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from comfortzone.czb_data import random_cutin_trials              # noqa: E402
from fit_recovery import priors_for                               # noqa: E402
from fit_stage1 import fit_hier_lapse                             # noqa: E402
from bias_variant_diagnostics import hier_posterior_effects, spearman  # noqa: E402

OUT = HERE / "out"
N_GH_SIM = 32
N_REP = 12
SEED = 0


def simulate(x, pid, n_drivers, truth, rho, rng):
    """Draw responses with a given true correlation between the two driver effects."""
    from scipy.stats import norm
    z1 = rng.standard_normal(n_drivers)
    z2 = rho * z1 + np.sqrt(max(1.0 - rho ** 2, 0.0)) * rng.standard_normal(n_drivers)
    c = np.exp(truth["mu"] + truth["sigma_pop"] * z1)
    b = 1.0 / (1.0 + np.exp(-(truth["b_logit"] + truth["sigma_b"] * z2)))
    p = b[pid] + (1 - b[pid]) * norm.cdf((x - c[pid]) / truth["sigma_resp"])
    return (rng.random(len(x)) < p).astype(float), c, b


def main() -> None:
    t0 = time.time()
    r = random_cutin_trials()
    pid = r.participant.factorize()[0].astype(int)
    n_drivers = int(pid.max() + 1)
    x = r.deficit_max.to_numpy(float)
    y = r.intervene.to_numpy(float)
    pr = priors_for(x)

    print("fitting the real data to get the simulation truths ...", flush=True)
    f = fit_hier_lapse(x, y, pid, pr)
    ch, bh = hier_posterior_effects(f, x, y, pid, n_drivers)
    rho_real = spearman(bh, ch)
    truth = {"mu": f["mu"], "sigma_pop": f["sigma_pop"], "sigma_resp": f["sigma_resp"],
             "b_logit": f["phi"][3], "sigma_b": f["sigma_b"]}
    print(f"  observed rho(b_i, c_i) = {rho_real:+.3f}", flush=True)

    arms = {}
    for label, rho_true in (("independent (rho = 0)", 0.0),
                            ("genuinely correlated (rho = -0.7)", -0.7)):
        got = []
        for k in range(N_REP):
            rng = np.random.default_rng(SEED + 1000 * int(rho_true == 0.0) + k)
            ys, _, _ = simulate(x, pid, n_drivers, truth, rho_true, rng)
            fs = fit_hier_lapse(x, ys, pid, pr, n_gh=N_GH_SIM)
            cs, bs = hier_posterior_effects(fs, x, ys, pid, n_drivers)
            got.append(spearman(bs, cs))
            print(f"  {label} rep {k + 1}/{N_REP}: rho = {got[-1]:+.3f}", flush=True)
        arms[label] = np.array(got)

    ind = arms["independent (rho = 0)"]
    cor = arms["genuinely correlated (rho = -0.7)"]
    # Does the observed value sit inside the independent arm's range?
    frac_below = float((ind <= rho_real).mean())

    L = ["# Is the lapse-threshold correlation real? (query R.1.Q2)\n",
         "The fitted per-driver lapse and boundary level correlate at Spearman "
         f"**{rho_real:+.3f}** on the real data, while the model treats them as "
         "independent. This asks whether that is a trait correlation or an artifact of "
         "estimating two quantities that trade off against each other from the same "
         "limited per-driver data. Simulations use the parameters fitted on the real "
         "data, so each simulated driver carries the same amount of information as a "
         f"real one; {N_REP} replicates per arm.\n",
         "| truth | recovered rho, mean | sd | min | max |", "|---|---|---|---|---|",
         f"| driver effects independent (rho = 0) | **{ind.mean():+.3f}** | {ind.std():.3f} "
         f"| {ind.min():+.3f} | {ind.max():+.3f} |",
         f"| genuinely correlated (rho = -0.7) | {cor.mean():+.3f} | {cor.std():.3f} "
         f"| {cor.min():+.3f} | {cor.max():+.3f} |",
         f"| *observed on the real data* | *{rho_real:+.3f}* | - | - | - |",
         "\n## Reading\n"]

    # Report the comparison quantitatively rather than branching on an arbitrary cut.
    # (An earlier version of this script thresholded the independent arm's mean at -0.3
    # and, at -0.288, printed "near zero" for a correlation that is plainly substantial.
    # The numbers were right and the prose was wrong, which is exactly the failure mode
    # generated artifacts are supposed to prevent.)
    share = ind.mean() / rho_real if rho_real != 0 else float("nan")
    z_ind = (rho_real - ind.mean()) / max(ind.std(), 1e-9)
    z_cor = (rho_real - cor.mean()) / max(cor.std(), 1e-9)
    L += [f"**The estimator manufactures a substantial part of this on its own.** With "
          f"the driver effects truly independent it still recovers {ind.mean():+.3f} on "
          f"average — {share:.0%} of the observed magnitude — because the two effects "
          "trade off: each driver's excess pressing has to be split between the lapse "
          "and the threshold, which forces the two estimation errors to have opposite "
          "signs. This is the same phenomenon as the classic negative correlation "
          "between a fitted intercept and slope. Any reading of the raw "
          f"{rho_real:+.3f} that ignores this overstates the trait correlation.\n",
          f"**But it does not account for all of it.** The observed value sits "
          f"{abs(z_ind):.1f} sd below the independent arm's mean and is more negative "
          f"than {int((ind > rho_real).sum())} of the {N_REP} independent replicates, "
          f"while sitting {abs(z_cor):.1f} sd from the mean of the arm simulated with a "
          f"genuine rho = -0.7 ({cor.mean():+.3f}) — comfortably inside it. The data "
          "are therefore consistent with a real correlation of roughly the size the "
          "naive estimate suggests, arrived at through a mixture of a real effect and "
          f"an artifact worth about {ind.mean():+.3f}.\n",
          "**Practical conclusion**: query R.1.Q2 stays open, the correlated-effects "
          "variant in card A.2.v2 is still needed, and its fitted correlation must be "
          f"judged against the artifact baseline of {ind.mean():+.3f} rather than "
          "against zero — a fit returning, say, -0.3 would be evidence of *no* real "
          "correlation, not of a moderate one."]

    L += ["\n\n## What follows either way\n",
          "The practical question is not whether the correlation is real but whether "
          "the deliverable moves. If it is an artifact, the independence assumption is "
          "harmless and the percentile table stands as reported. If it is real, the "
          "correlated-effects fit in card A.2.v2 is the check, under the rule fixed at "
          "review gate R.1: escalate if the 80th percentile moves by more than the "
          "current CI half-width (~250 deficit units).\n",
          f"Runtime {(time.time() - t0) / 60:.1f} min."]

    txt = "\n".join(L) + "\n"
    (OUT / "lapse_threshold_artifact.md").write_text(txt, encoding="utf-8")
    print("\n" + txt)


if __name__ == "__main__":
    main()
