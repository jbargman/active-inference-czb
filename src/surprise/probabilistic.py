"""
Probabilistic-mismatch surprise: how unlikely was the observation under the prior belief?

These compare a single *observation* against a *distribution*. In Modirshanechi et al.'s
semantic taxonomy most of these are "prediction surprise" (how unpredicted was it), except
Bayes-factor surprise which is "change-point detection surprise" (has the world changed?).

References
----------
Shannon (1948); Macedo et al. (2004) for S8; Glaescher et al. (2010) for state prediction
error; Liakoni et al. (2021) for Bayes-factor surprise; Dinparastdjadid, Supeene & Engstrom
(2023) for residual information; Modirshanechi, Brea & Gerstner (2022) for the taxonomy and
the equivalence results.
"""
from __future__ import annotations

import numpy as np

from .distributions import Distribution


def _scalarise(out: np.ndarray, x):
    """Return a plain float when a single observation was passed, else the array.

    Keeps the API ergonomic: `residual_information(1.5, prior)` gives a float, while
    `residual_information(np.array([[1.0],[2.0]]), prior)` gives an array of two values.
    """
    out = np.asarray(out, dtype=float)
    a = np.asarray(x, dtype=object if isinstance(x, str) else float)
    single = (
        isinstance(x, (str, int, float, np.integer, np.floating))
        or (isinstance(x, np.ndarray) and x.ndim <= 1)
        or (isinstance(x, (list, tuple)) and not any(
            isinstance(v, (list, tuple, np.ndarray)) for v in x))
    )
    if single and out.size == 1:
        return float(out.ravel()[0])
    return out


def shannon_surprise(x, prior: Distribution) -> np.ndarray:
    """
    Shannon surprise / surprisal:  S(x) = -log p(x).

    Caveats for continuous distributions (Dinparastdjadid et al. 2023):
      * **no zero floor** -- returns a positive value even when the most likely outcome
        occurs, which contradicts human surprise reports (Macedo et al. 2004) and makes it
        awkward to accumulate as evidence;
      * on a density this is a log-*density*, not a log-probability, so it is only defined
        up to the choice of units and can be negative.
    Prefer `residual_information` for continuous beliefs.
    """
    return _scalarise(-np.asarray(prior.logpdf(x), dtype=float), x)


#: alias -- the literature uses both names
surprisal = shannon_surprise


def residual_information(x, prior: Distribution) -> np.ndarray:
    """
    Residual information (Dinparastdjadid, Supeene & Engstrom 2023, Eq. 6):

        h_r(x; P) = log( max_x' P(x') ) - log( P(x) )

    The difference in information content between the observed outcome and the most likely
    outcome. Three properties that make it the measure of choice here:

      * **zero floor** -- exactly 0 when the mode is observed;
      * **parameterless on continuous distributions** -- discretising into bins of size eps
        and letting eps -> 0 leaves the formula unchanged (the eps cancels in the ratio), so
        the categorical definition transfers to densities without modification;
      * **information-theoretically meaningful** -- it is a difference of information
        contents, unlike the ad-hoc S8.

    This is the quantity the active-inference collision-avoidance model accumulates as
    evidence for re-planning (applied to the *pragmatic value*; see `surprise.pragmatic`).
    """
    mode = prior.mode()
    log_max = float(np.asarray(prior.logpdf(mode), dtype=float).ravel()[0])
    return _scalarise(log_max - np.asarray(prior.logpdf(x), dtype=float), x)


def macedo_s8(x, prior: Distribution, eps: float | None = None) -> np.ndarray:
    """
    Macedo et al. (2004) measure S8:  S8(x) = log2( 1 + max_x' P(x') - P(x) ).

    Has the zero-floor property but no information-theoretic interpretation, and for a
    continuous distribution it depends on the bin width `eps` (tending to 0 as eps -> 0).
    Included for comparison; `eps` converts densities to approximate bin masses.
    """
    p_x = np.asarray(prior.pdf(x), dtype=float)
    p_max = float(np.asarray(prior.pdf(prior.mode()), dtype=float).ravel()[0])
    if eps is not None:
        p_x = p_x * eps ** getattr(prior, "ndim", 1)
        p_max = p_max * eps ** getattr(prior, "ndim", 1)
    return _scalarise(np.log2(1.0 + p_max - p_x), x)


def bayes_factor_surprise(x, prior_naive: Distribution, belief: Distribution) -> np.ndarray:
    """
    Bayes-factor surprise (Liakoni et al. 2021; Modirshanechi et al. 2022 Eq. 5):

        S_BF(x) = P(x | prior pi^0) / P(x | current belief pi^t)

    Semantically different from the rest: it does not ask "was that unlikely?" but "should I
    reset my belief?" -- i.e. it is a change-point statistic that modulates learning rate.
    Note the direction: for fixed current-belief likelihood, surprise *increases* with the
    naive-prior likelihood, the opposite of Shannon surprise.

    In a driving context this is the natural measure for "has this road user's behaviour
    regime changed?" (e.g. a lead vehicle switching from free-flow to braking), as opposed
    to "was this particular position unlikely?".
    """
    lp0 = np.asarray(prior_naive.logpdf(x), dtype=float)
    lpt = np.asarray(belief.logpdf(x), dtype=float)
    return _scalarise(np.exp(lp0 - lpt), x)


def state_prediction_error(x, prior: Distribution) -> np.ndarray:
    """
    State prediction error (Glaescher et al. 2010):  S_SPE(x) = 1 - P(x).

    Defined for discrete distributions. Modirshanechi et al. (2022, Prop. 3) show it is a
    strictly increasing function of Shannon surprise,

        S_SPE = 1 - exp( -S_Sh ),

    so it is *indistinguishable* from surprisal for ranking purposes -- included for
    completeness and for reproducing analyses that report it.
    """
    return _scalarise(1.0 - np.asarray(prior.pdf(x), dtype=float), x)
