"""
Property tests for the surprise library.

These check the mathematical claims made in the source papers, not just that the code runs:
zero-floor, parameterlessness, the antithesis silencing conditions, and the equivalences
proved by Modirshanechi et al. (2022).

Run:  python tests/test_surprise.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from surprise import (  # noqa: E402
    Categorical, Gaussian, GaussianMixture, ParticleSet,
    antithesis, bayes_factor_surprise, bayesian_surprise,
    absolute_error_surprise, squared_error_surprise,
    macedo_s8, residual_information, shannon_surprise, state_prediction_error,
    EvidenceAccumulator, residual_information_of_pragmatic_value,
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    detail = "" if detail == "" else str(detail)
    print(f"{'PASS' if bool(cond) else 'FAIL'}  {name}{('  -- ' + detail) if detail else ''}")


# ---------------------------------------------------------------- zero floor
def test_zero_floor():
    g = Gaussian(mean=[0.0], cov=[[2.0]])
    ri_mode = float(np.ravel(residual_information(g.mode(), g))[0])
    check("residual information is zero at the mode (Gaussian)",
          abs(ri_mode) < 1e-9, f"got {ri_mode:.3e}")

    s_mode = float(np.ravel(shannon_surprise(g.mode(), g))[0])
    check("surprisal is NON-zero at the mode (the zero-floor problem)",
          abs(s_mode) > 1e-6, f"got {s_mode:.4f}")

    c = Categorical([0.7, 0.2, 0.1], labels=["pass", "yield", "stop"])
    check("residual information is zero at the mode (categorical)",
          abs(float(np.ravel(residual_information("pass", c))[0])) < 1e-12)
    ri_tail = float(np.ravel(residual_information("stop", c))[0])
    check("residual information equals log(p_max/p_x) exactly",
          abs(ri_tail - np.log(0.7 / 0.1)) < 1e-12, f"got {ri_tail:.4f}")

    check("S8 also has the zero floor",
          abs(float(np.ravel(macedo_s8("pass", c))[0])) < 1e-12)


# ------------------------------------------------------- parameterlessness
def test_parameterless():
    """
    The paper's key claim: discretising a continuous distribution into bins of size eps and
    letting eps -> 0, residual information converges to the continuous-density formula
    unchanged, whereas surprisal diverges and S8 collapses to 0.
    """
    g = Gaussian(mean=[0.0], cov=[[1.0]])
    x = 1.5
    ri_cont = float(residual_information(x, g))

    ri_binned, sur_binned, s8_binned = [], [], []
    for eps in [1e-1, 1e-2, 1e-3, 1e-4]:
        # bin mass ~ density * eps  => ratio of masses = ratio of densities (eps cancels)
        p_x = float(np.ravel(g.pdf(x))[0]) * eps
        p_max = float(np.ravel(g.pdf(g.mode()))[0]) * eps
        ri_binned.append(np.log(p_max / p_x))
        sur_binned.append(-np.log(p_x))
        s8_binned.append(np.log2(1 + p_max - p_x))

    check("residual information is eps-invariant",
          np.allclose(ri_binned, ri_cont, atol=1e-12),
          f"binned={np.round(ri_binned, 6).tolist()} continuous={ri_cont:.6f}")
    check("surprisal diverges as eps -> 0",
          sur_binned[-1] > sur_binned[0] + 5,
          f"{sur_binned[0]:.2f} -> {sur_binned[-1]:.2f}")
    check("S8 collapses to 0 as eps -> 0",
          s8_binned[-1] < 1e-3 < s8_binned[0],
          f"{s8_binned[0]:.4f} -> {s8_binned[-1]:.6f}")


# ------------------------------------------------------------- monotonicity
def test_monotone_in_tail():
    g = Gaussian(mean=[0.0], cov=[[1.0]])
    xs = np.array([0.0, 0.5, 1.0, 2.0, 4.0])
    ri = np.array([float(np.ravel(residual_information(x, g))[0]) for x in xs])
    check("residual information increases into the tail", np.all(np.diff(ri) > 0),
          np.round(ri, 3).tolist())
    check("residual information is non-negative everywhere", np.all(ri >= -1e-12))


# ------------------------------------------------- Modirshanechi equivalences
def test_equivalences():
    c = Categorical([0.5, 0.3, 0.2])
    for lbl in [0, 1, 2]:
        spe = float(np.ravel(state_prediction_error(lbl, c))[0])
        sh = float(np.ravel(shannon_surprise(lbl, c))[0])
        if abs(spe - (1 - np.exp(-sh))) > 1e-12:
            check("SPE = 1 - exp(-Shannon)  (Modirshanechi Prop. 3)", False)
            return
    check("SPE = 1 - exp(-Shannon)  (Modirshanechi Prop. 3)", True)

    # 1-D: squared error == absolute error squared (their Prop. 6)
    g = Gaussian(mean=[1.0], cov=[[1.0]])
    x = 2.3
    a = absolute_error_surprise(x, g)
    s = squared_error_surprise(x, g)
    check("1-D: S_Sq = S_Abs^2  (Modirshanechi Prop. 6)", abs(s - a ** 2) < 1e-12)


# ------------------------------------------------------------- Bayes factor
def test_bayes_factor_direction():
    """
    S_BF increases with likelihood under the naive prior (opposite to Shannon surprise),
    because it is a change-point statistic, not an unlikeliness statistic.
    """
    belief = Gaussian(mean=[0.0], cov=[[0.25]])       # confident, narrow
    naive = Gaussian(mean=[0.0], cov=[[4.0]])         # vague prior
    x_far = 3.0
    bf = float(np.ravel(bayes_factor_surprise(x_far, naive, belief))[0])
    check("Bayes-factor surprise > 1 for an observation far from a confident belief",
          bf > 1.0, f"S_BF={bf:.3f}")
    bf_near = float(np.ravel(bayes_factor_surprise(0.0, naive, belief))[0])
    check("Bayes-factor surprise < 1 at the belief mode", bf_near < 1.0,
          f"S_BF={bf_near:.3f}")


# ---------------------------------------------------------------- antithesis
def test_antithesis_silencing():
    rng = np.random.default_rng(0)

    # (a) mode-narrowing: same mode, less uncertainty. Information gain, but NOT surprise.
    prior = Gaussian(mean=[0.0], cov=[[1.0]])
    post_narrow = Gaussian(mean=[0.0], cov=[[0.25]])
    kl_narrow = bayesian_surprise(post_narrow, prior, n_samples=40000, rng=rng)
    a_narrow = antithesis(post_narrow, prior, n_samples=40000, rng=rng)
    check("mode-narrowing: KL is clearly non-zero", kl_narrow > 0.1, f"KL={kl_narrow:.4f}")
    check("mode-narrowing: antithesis silences it", a_narrow < kl_narrow / 3,
          f"antithesis={a_narrow:.4f} vs KL={kl_narrow:.4f}")

    # (b) mode-removal: prior bimodal (indicator on: change lane or not), posterior keeps
    #     one already-expected mode. Information gain, but both outcomes were expected.
    prior_bi = GaussianMixture(weights=[0.5, 0.5], means=[[0.0], [4.0]],
                               covs=[[[0.3]], [[0.3]]])
    post_one = Gaussian(mean=[0.0], cov=[[0.3]])
    kl_rem = bayesian_surprise(post_one, prior_bi, n_samples=40000, rng=rng)
    a_rem = antithesis(post_one, prior_bi, n_samples=40000, rng=rng)
    check("mode-removal: KL is non-zero", kl_rem > 0.1, f"KL={kl_rem:.4f}")
    check("mode-removal: antithesis is (near) silent", a_rem < kl_rem / 3,
          f"antithesis={a_rem:.4f} vs KL={kl_rem:.4f}")

    # (c) genuine surprise: posterior mass moves to a region the prior thought unlikely
    post_shift = Gaussian(mean=[3.5], cov=[[0.3]])
    kl_shift = bayesian_surprise(post_shift, prior, n_samples=40000, rng=rng)
    a_shift = antithesis(post_shift, prior, n_samples=40000, rng=rng)
    check("genuine surprise: antithesis fires", a_shift > 1.0, f"antithesis={a_shift:.4f}")
    check("genuine surprise ranks above mode-narrowing under antithesis",
          a_shift > 10 * max(a_narrow, 1e-6),
          f"{a_shift:.4f} vs {a_narrow:.4f}")
    check("...whereas KL ranks them much closer together",
          (a_shift / max(a_narrow, 1e-9)) > (kl_shift / max(kl_narrow, 1e-9)),
          f"antithesis ratio={a_shift/max(a_narrow,1e-9):.1f}, "
          f"KL ratio={kl_shift/max(kl_narrow,1e-9):.1f}")


# ------------------------------------------------------ distributions sanity
def test_distributions():
    rng = np.random.default_rng(1)
    gm = GaussianMixture(weights=[0.6, 0.4], means=[[0.0], [5.0]], covs=[[[1.0]], [[1.0]]])
    s = gm.sample(200000, rng)
    check("GMM sample mean matches analytic mean",
          abs(s.mean() - gm.mean()[0]) < 0.05, f"{s.mean():.3f} vs {gm.mean()[0]:.3f}")
    integral = np.trapezoid(gm.pdf(np.linspace(-10, 15, 6000)), np.linspace(-10, 15, 6000))
    check("GMM density integrates to 1", abs(integral - 1) < 1e-3, f"{integral:.5f}")
    check("GMM mode is on the dominant component", abs(gm.mode()[0]) < 1.0,
          f"mode={gm.mode()[0]:.3f}")

    ps = ParticleSet(rng.normal(0, 1, size=(2000, 1)))
    ent = ps.entropy(20000, rng)
    check("particle-set KDE entropy near Gaussian value (1.419)",
          abs(ent - 1.419) < 0.25, f"{ent:.3f}")


# ------------------------------------------------- pragmatic / accumulation
def test_pragmatic_and_accumulation():
    """Preferred speed 15 m/s; residual information is 0 at the preference mode."""
    mu, sd = 15.0, 0.5

    def log_pref(o):
        o = np.atleast_2d(o)
        return -0.5 * ((o[:, 0] - mu) / sd) ** 2 - np.log(sd * np.sqrt(2 * np.pi))

    max_lp = -np.log(sd * np.sqrt(2 * np.pi))
    H = 30

    at_pref = [np.full((20, 1), mu) for _ in range(H)]
    eps0 = residual_information_of_pragmatic_value(at_pref, log_pref, max_lp)
    check("eps = 0 when the policy delivers the preferred observation", abs(eps0) < 1e-9,
          f"{eps0:.3e}")

    for dev in [0.5, 1.0, 3.0]:
        off = [np.full((20, 1), mu - dev) for _ in range(H)]
        e = residual_information_of_pragmatic_value(off, log_pref, max_lp)
        expected = H * 0.5 * (dev / sd) ** 2
        if abs(e - expected) > 1e-6:
            check("eps grows quadratically with deviation (Gaussian preference)", False,
                  f"dev={dev} got {e:.3f} expected {expected:.3f}")
            break
    else:
        check("eps grows quadratically with deviation (Gaussian preference)", True)

    # accumulator: constant surprise -> threshold crossing at the analytic time
    # use an exactly-representable increment (0.125) so the analytic step count is not
    # perturbed by floating-point accumulation error
    lam = 1e-3
    acc = EvidenceAccumulator(drift_rate=lam, threshold=1.0)
    eps_const = 125.0
    trig = acc.run([eps_const] * 50)
    first = int(np.argmax(trig)) if trig.any() else None
    expected_step = int(np.ceil(1.0 / (lam * eps_const))) - 1
    check("accumulator crosses threshold at the analytic step",
          first == expected_step, f"first={first} expected={expected_step}")
    check("accumulator resets after triggering", acc.evidence < 1.0)

    acc2 = EvidenceAccumulator(drift_rate=lam, threshold=1.0)
    acc2.run([0.0] * 100)
    check("zero surprise never triggers a re-plan (zero floor matters)",
          len(acc2.trigger_times) == 0)

    # higher surprise -> earlier response (the mechanism behind kinematics-dependent RT)
    times = []
    for eps in [50.0, 100.0, 200.0]:
        a = EvidenceAccumulator(drift_rate=lam, threshold=1.0)
        a.run([eps] * 200)
        times.append(a.response_time(dt=0.2, onset_index=0))
    check("stronger surprise -> shorter response time", times[0] > times[1] > times[2],
          f"{times}")


if __name__ == "__main__":
    for fn in [test_zero_floor, test_parameterless, test_monotone_in_tail,
               test_equivalences, test_bayes_factor_direction,
               test_antithesis_silencing, test_distributions,
               test_pragmatic_and_accumulation]:
        print(f"\n--- {fn.__name__} ---")
        fn()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED:", FAIL)
    sys.exit(1 if FAIL else 0)
