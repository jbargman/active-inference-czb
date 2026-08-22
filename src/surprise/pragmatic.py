"""
Preference-relative surprise: how far is the expected future from the preferred one?

This module holds the quantity that drives response timing in the active-inference collision
avoidance model (Schumann et al. 2026, Nat. Commun. 17:5009), and -- because it is zero
inside the driver's comfort zone and grows monotonically as the situation deteriorates -- the
natural scalar for defining **comfort-zone boundaries**.

The distinction that matters
----------------------------
There are two different things called "surprise" in this literature and the library keeps
them apart:

  * *surprise about the world* -- another road user did something unexpected. Measured
    against a **predictive** belief. That is `surprise.probabilistic` / `surprise.belief`,
    and it is what conflict detection and response-onset detection need.
  * *surprise about one's own preferred state* -- "I am heading somewhere I do not want to
    be". Measured against the **preference prior** p(o). That is this module, and it is what
    comfort-zone boundaries need.

Mathematically they are the same object (residual information of a log-probability); only the
distribution differs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np


# --------------------------------------------------------------------------------------
# Pragmatic value
# --------------------------------------------------------------------------------------
def pragmatic_value(observations, log_preference: Callable[[np.ndarray], np.ndarray],
                    weights=None) -> float:
    """
    Pragmatic value of a predicted observation distribution (Engstrom et al. 2024, Eq. 1;
    Schumann et al. 2026, Eqs. 6/8):

        g_pragm( q(o) ) = E_q(o) [ log p(o) ]

    approximated with a particle set as  (1/N) SUM_o log p(o).

    Parameters
    ----------
    observations
        Array of predicted observations, shape (N, dim) -- the particles representing
        q(o_tau | pi, q(s_t)) at one future timestep.
    log_preference
        Callable returning log p(o) for an array of observations. This *is* the driver's
        preference function; see `PreferenceFunction` for the product form used in the paper.
    weights
        Optional particle weights (normalised internally). Uniform if omitted.
    """
    o = np.atleast_2d(np.asarray(observations, dtype=float))
    lp = np.asarray(log_preference(o), dtype=float)
    if weights is None:
        return float(np.mean(lp))
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    return float(np.sum(w * lp))


def residual_information_of_pragmatic_value(
        rollout_observations: Sequence[np.ndarray],
        log_preference: Callable[[np.ndarray], np.ndarray],
        max_log_preference: float,
        weights: Sequence | None = None) -> float:
    """
    The evidence signal of the collision-avoidance model (Schumann et al. 2026, Eq. 13):

        eps_t = H * max_o log p(o)  -  SUM_{tau=t+1}^{t+H} g_pragm( q(o_tau | pi_t) )

    "the difference between the highest pragmatic value possible and the actual pragmatic
    value of a policy". If the current policy would deliver the most preferred observations,
    eps = 0 and no evidence accumulates -- a genuine zero floor. If it leads somewhere
    undesired, evidence accrues fast.

    This is `residual_information` from `surprise.probabilistic`, applied to the preference
    prior and summed over the planning horizon. It is non-negative by construction (the
    per-step pragmatic value cannot exceed the per-step maximum).

    Parameters
    ----------
    rollout_observations
        Length-H sequence of arrays of shape (N, dim): predicted observation particles at
        each step of the planning horizon under the current policy.
    log_preference
        log p(o).
    max_log_preference
        max_o log p(o), the log-density at the most preferred observation. For the product-
        of-factors preference used in the paper this is the sum of each factor's maximum.
    weights
        Optional per-timestep particle weights.

    Returns
    -------
    float, >= 0
    """
    H = len(rollout_observations)
    total = 0.0
    for i, obs in enumerate(rollout_observations):
        w = None if weights is None else weights[i]
        total += pragmatic_value(obs, log_preference, weights=w)
    eps = H * float(max_log_preference) - total
    # numerically, tiny negative values can appear if max_log_preference is slightly
    # under-estimated; clamp at zero to preserve the zero-floor property
    return float(max(eps, 0.0))


# --------------------------------------------------------------------------------------
# Evidence accumulation
# --------------------------------------------------------------------------------------
@dataclass
class EvidenceAccumulator:
    """
    Surprise-based re-planning (Schumann et al. 2026, Eq. 12):

        E_t = E_{t-1} + lambda * eps_t ,     re-plan when E_t >= threshold

    A drift-diffusion-style accumulator in which the drift rate is supplied by an
    information-theoretic quantity computed from the agent's own generative model, rather
    than being fitted per scenario. This is why the resulting response times are
    *kinematics-dependent* -- eps_t depends on the predicted future under the current policy.

    `lambda` is the model's single most sensitive parameter (paper value 10^-5.95); the
    threshold is 1 by convention, with the scale absorbed into lambda.

    On crossing the threshold the accumulator resets to 0 and the agent re-plans its whole
    policy (the IWAI poster states the reset explicitly).

    Examples
    --------
    >>> acc = EvidenceAccumulator(drift_rate=10 ** -5.95)
    >>> for eps in eps_series:                      # doctest: +SKIP
    ...     if acc.step(eps):
    ...         replan()
    """

    drift_rate: float = 10 ** -5.95     # lambda
    threshold: float = 1.0
    reset_on_trigger: bool = True
    initial: float = 0.0
    evidence: float = field(init=False)
    history: list = field(init=False, default_factory=list)
    trigger_times: list = field(init=False, default_factory=list)
    _t: int = field(init=False, default=0)

    def __post_init__(self):
        self.evidence = float(self.initial)

    def step(self, epsilon: float) -> bool:
        """Accumulate one timestep of surprise. Returns True if a re-plan is triggered."""
        self.evidence += self.drift_rate * float(epsilon)
        self.history.append(self.evidence)
        triggered = self.evidence >= self.threshold
        if triggered:
            self.trigger_times.append(self._t)
            if self.reset_on_trigger:
                self.evidence = 0.0
        self._t += 1
        return triggered

    def run(self, epsilon_series) -> np.ndarray:
        """Run over a whole series; returns a boolean array of re-plan triggers."""
        return np.array([self.step(e) for e in epsilon_series], dtype=bool)

    def reset(self):
        self.evidence = float(self.initial)
        self.history.clear()
        self.trigger_times.clear()
        self._t = 0

    def response_time(self, dt: float, onset_index: int = 0) -> float | None:
        """
        Time from `onset_index` to the first threshold crossing, in seconds.
        Returns None if the threshold was never reached.
        """
        after = [t for t in self.trigger_times if t >= onset_index]
        if not after:
            return None
        return (after[0] - onset_index) * dt
