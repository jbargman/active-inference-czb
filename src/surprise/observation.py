"""
Observation-mismatch surprise: how far was the observation from the point prediction?

The simplest family -- compare an actual observation with a predicted one. Modirshanechi et
al. (2022) classify these as "prediction surprise" and prove several equivalences that are
worth knowing before you report them as separate measures:

  * for one-hot categorical observations,  S_Abs = 2 * S_SPE  (their Prop. 4);
  * for isotropic Gaussians, squared error is a strictly increasing function of Shannon
    surprise (their Prop. 5, after Pathak et al. 2017);
  * for 1-D observations, S_Sq = S_Abs^2, so the two are indistinguishable (their Prop. 6).

In other words: on 1-D Gaussian-ish driving signals these carry the same ranking information
as surprisal. They are cheap and model-free, which is their real appeal -- they need only a
point prediction, not a distribution.
"""
from __future__ import annotations

import numpy as np

from .distributions import Distribution


def _prediction(prior, predicted):
    if predicted is not None:
        return np.atleast_1d(np.asarray(predicted, dtype=float))
    if prior is None:
        raise ValueError("provide either `prior` (to take its mean) or `predicted`")
    return np.atleast_1d(np.asarray(prior.mean(), dtype=float))


def absolute_error_surprise(x, prior: Distribution | None = None,
                            predicted=None) -> float:
    """
    Absolute-error surprise (Modirshanechi et al. 2022 Eq. 20):

        S_Abs = || y - E[Y] ||_1

    `predicted` overrides the prior's mean if you have a point prediction from elsewhere.
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    yhat = _prediction(prior, predicted)
    return float(np.sum(np.abs(x - yhat)))


def squared_error_surprise(x, prior: Distribution | None = None,
                           predicted=None) -> float:
    """
    Squared-error surprise (Modirshanechi et al. 2022 Eq. 20):

        S_Sq = || y - E[Y] ||_2^2
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    yhat = _prediction(prior, predicted)
    return float(np.sum((x - yhat) ** 2))


def unsigned_reward_prediction_error(reward: float, expected_reward: float) -> float:
    """
    Unsigned reward prediction error (Modirshanechi et al. 2022 Eq. 23):

        uRPE = | r - Q(s, a) |

    The reward-domain special case of absolute-error surprise. Included because it is the
    measure most often used in the decision-neuroscience literature, and because in a driving
    context "reward" can be read as pragmatic value -- which makes this the crude,
    point-estimate cousin of the residual-information-of-pragmatic-value quantity in
    `surprise.pragmatic`.
    """
    return float(abs(reward - expected_reward))
