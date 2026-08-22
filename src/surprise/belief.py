"""
Belief-mismatch surprise: how much did the observation change what I believe?

These compare two *distributions* -- a prior belief and a posterior belief. In the taxonomy
of Modirshanechi et al. (2022) the KL-based ones are "information gain" (enlightenment)
surprise; confidence-corrected surprise forms its own category.

In the driving application (Dinparastdjadid et al. 2023) prior and posterior are predictions
made at two different *times* (t-h and t) about the *same* future time (t+z):

    prior     = generative model output at time t-h, about time t+z
    posterior = generative model output at time t,   about time t+z

Because they compare predicted futures, these measures implicitly see higher time
derivatives -- a hard deceleration changes the predicted future position long before it has
moved the current position much -- so they detect surprising actions *earlier* than
probabilistic-mismatch measures.
"""
from __future__ import annotations

import numpy as np

from .distributions import Distribution


def _mc_samples(dist: Distribution, n: int, rng):
    return dist.sample(n, rng)


def bayesian_surprise(posterior: Distribution, prior: Distribution,
                      n_samples: int = 20000, rng=None) -> float:
    """
    Bayesian surprise (Itti & Baldi 2009; Baldi 2002):

        S_Ba = D_KL( posterior || prior )

    Estimated by Monte Carlo over samples from the posterior:
        E_posterior[ log posterior(x) - log prior(x) ].

    Practical caveat (Dinparastdjadid et al. 2023): the posterior is formed with extra
    information, so its uncertainty almost always shrinks even when the mode does not move.
    Hence KL is essentially never zero and fires on *unsurprising* information gain
    (mode-narrowing, mode-removal). Use `antithesis` when you need discrimination.

    Note also that expected Bayesian surprise is exactly the **epistemic value** term of the
    expected free energy in active inference -- the same quantity, evaluated prospectively
    over counterfactual observations rather than retrospectively over actual ones.
    """
    rng = np.random.default_rng() if rng is None else rng
    x = _mc_samples(posterior, n_samples, rng)
    lp_post = np.asarray(posterior.logpdf(x), dtype=float)
    lp_prior = np.asarray(prior.logpdf(x), dtype=float)
    return float(np.mean(lp_post - lp_prior))


def antithesis(posterior: Distribution, prior: Distribution,
               n_samples: int = 20000, rng=None,
               expectation_threshold: float | None = None) -> float:
    """
    Antithesis (Dinparastdjadid, Supeene & Engstrom 2023, Eq. 9) -- a belief-mismatch measure
    that detects *the increased likelihood of a previously unexpected outcome*:

        C(P, x, y) = [ log P(x) < E_x'[log P(x')] ]  AND  [ P(x|y) > P(x) ]
        A(y; P)    = INTEGRAL_{C} P(x|y) log( P(x|y) / P(x) ) dx

    i.e. the KL integrand, but integrated only over the region where both

      (i) the "outside expectations" condition holds -- the outcome's information content is
          above average under the prior, equivalently log P(x) < -H[P]; and
      (ii) the "increased belief" condition holds -- the posterior raised its probability.

    Together these silence two kinds of *unsurprising* information gain:
      * **mode-narrowing** -- evidence confirming a single prior expectation;
      * **mode-removal** -- evidence for one of several already-plausible outcomes (the
        classic case: a vehicle with its indicator on either changes lane or does not; both
        were expected, so resolving between them is not surprising).

    Empirically zero far more often than plain KL, which is what gives it discriminative
    power for conflict detection.

    Parameters
    ----------
    expectation_threshold
        Overrides the "average information content" cut. The paper uses
        E_x'[log P(x')] = -H[P] and notes that parameterising this threshold is a natural
        way to tune sensitivity. Pass a log-density value to do so.

    Notes
    -----
    Implemented by Monte Carlo over posterior samples: evaluate the predicate per sample and
    discard the samples for which it is false (exactly as the paper prescribes). The result
    is therefore an estimate of the *restricted* integral, and unlike full KL it is not a
    divergence (it can be 0 for distinct distributions -- by design).
    """
    rng = np.random.default_rng() if rng is None else rng
    x = _mc_samples(posterior, n_samples, rng)
    lp_post = np.asarray(posterior.logpdf(x), dtype=float)
    lp_prior = np.asarray(prior.logpdf(x), dtype=float)

    if expectation_threshold is None:
        # E_x'[log P(x')] under the prior = -H[P]
        thr = -float(prior.entropy())
    else:
        thr = float(expectation_threshold)

    outside_expectations = lp_prior < thr
    increased_belief = lp_post > lp_prior
    mask = outside_expectations & increased_belief
    if not mask.any():
        return 0.0
    # Monte-Carlo estimate of INTEGRAL_C p_post log(p_post/p_prior) dx, with samples ~ p_post:
    # (1/N) * SUM_{i in C} (log p_post - log p_prior)
    return float(np.sum((lp_post - lp_prior)[mask]) / n_samples)


def postdictive_surprise(pred_posterior: Distribution, pred_prior: Distribution,
                         n_samples: int = 20000, rng=None) -> float:
    """
    Postdictive surprise (Kolossa et al. 2015; Modirshanechi et al. 2022 Eq. 35):

        S_Po = D_KL( P(.|pi^t) || P(.|pi^{t+1}) )

    Same idea as Bayesian surprise but measured in *observation* space rather than parameter
    space: how differently does the agent now predict the next observation, rather than how
    differently does it think about the parameters.

    Note the KL is taken with the *prior predictive* first (the reverse order from
    `bayesian_surprise`), following the source. Estimated by Monte Carlo over the prior
    predictive.
    """
    rng = np.random.default_rng() if rng is None else rng
    x = _mc_samples(pred_prior, n_samples, rng)
    lp_prior = np.asarray(pred_prior.logpdf(x), dtype=float)
    lp_post = np.asarray(pred_posterior.logpdf(x), dtype=float)
    return float(np.mean(lp_prior - lp_post))


def commitment(dist: Distribution) -> float:
    """
    Commitment / confidence of a belief (Faraji et al. 2018, Eq. 38):

        C[pi] = E_pi[ log pi(Theta) ] = -H[pi]

    i.e. negative entropy. A sharply peaked belief is highly committed.
    """
    return -float(dist.entropy())


def confidence_corrected_surprise(belief: Distribution, flat_posterior: Distribution,
                                  n_samples: int = 20000, rng=None) -> float:
    """
    Confidence-corrected surprise (Faraji, Preuschoff & Gerstner 2018; Modirshanechi et al.
    2022 Eq. 37):

        S_CC = D_KL( pi^t || pi_flat(. | y) )

    where `pi_flat(.|y)` is the normalised likelihood -- the posterior you would hold if you
    had started from a flat prior. The point is that violating a *confidently held* belief
    should be more surprising than violating a vague one; neither Shannon nor Bayesian
    surprise captures that explicitly.

    In a non-volatile environment it decomposes as
        S_CC = S_Shannon + S_Bayesian + C[pi^t] - A(y),
    i.e. Shannon plus Bayesian surprise regularised by the agent's confidence, with A(y)
    independent of the current belief.

    Parameters
    ----------
    belief
        The agent's current belief pi^t.
    flat_posterior
        The normalised likelihood pi_flat(.|y) -- construct this from the observation model
        alone, without the prior.
    """
    rng = np.random.default_rng() if rng is None else rng
    x = _mc_samples(belief, n_samples, rng)
    lp_belief = np.asarray(belief.logpdf(x), dtype=float)
    lp_flat = np.asarray(flat_posterior.logpdf(x), dtype=float)
    return float(np.mean(lp_belief - lp_flat))
