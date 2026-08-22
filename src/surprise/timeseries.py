"""
Applying surprise measures to a stream of predictions -- the "in the wild" use case.

This implements the bookkeeping of Dinparastdjadid, Supeene & Engstrom (2023): a generative
model emits, at each time t, a belief about each future time t+k. Surprise then needs two
timing parameters:

    history window h -- how far back the prior was generated
    lookahead      z -- (belief-mismatch only) which future time both beliefs are about

    probabilistic mismatch:  observation at t   vs  belief made at t-h about t
    belief mismatch:         belief made at t about t+z  vs  belief made at t-h about t+z

Effects reported in the paper: larger h gives larger and earlier peaks (prior and posterior
are more different); the effect of z is not monotone and is scenario-dependent, so it is
worth sweeping.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import numpy as np

from .belief import antithesis, bayesian_surprise
from .distributions import Distribution
from .probabilistic import residual_information, shannon_surprise


@dataclass
class SurpriseConfig:
    """
    Parameters
    ----------
    dt
        Timestep of the prediction stream [s].
    history_window
        h in seconds. Converted to an integer number of steps.
    lookahead
        z in seconds, for belief-mismatch measures.
    measures
        Which measures to compute. Any of
        {"surprisal", "residual_information", "bayesian_surprise", "antithesis"}.
    n_samples
        Monte-Carlo sample count for the belief-mismatch measures.
    """
    dt: float = 0.1
    history_window: float = 1.0
    lookahead: float = 0.2
    measures: Sequence[str] = ("surprisal", "residual_information",
                               "bayesian_surprise", "antithesis")
    n_samples: int = 20000
    seed: int | None = 0


def surprise_time_series(
        beliefs: Mapping[int, Mapping[int, Distribution]],
        observations: Sequence,
        config: SurpriseConfig | None = None) -> dict:
    """
    Compute surprise time series from a stream of predictive beliefs.

    Parameters
    ----------
    beliefs
        Nested mapping ``beliefs[t_made][t_about] -> Distribution``, where both indices are
        integer timestep indices. This mirrors the output of a trajectory predictor run at
        each timestep: at time `t_made` it emits distributions over the agent's state at
        each future time `t_about`.
    observations
        Sequence of actual observations, indexed by timestep. `observations[t]` is what
        actually happened at time t (e.g. the road user's position, or its lateral /
        longitudinal component in a body frame).
    config
        Timing and measure selection.

    Returns
    -------
    dict with key "t" (timestep indices) and one array per requested measure. Entries are
    NaN where the required prior/posterior pair does not exist (start of the record).

    Notes
    -----
    For lateral / longitudinal decomposition, transform positions into the responder's body
    frame *before* building the distributions, and call this once per component -- that is
    how the paper produces separate lateral and longitudinal surprise signals.
    """
    cfg = config or SurpriseConfig()
    rng = np.random.default_rng(cfg.seed)
    h = int(round(cfg.history_window / cfg.dt))
    z = int(round(cfg.lookahead / cfg.dt))

    times = sorted(beliefs.keys())
    out = {"t": np.asarray(times, dtype=int)}
    for m in cfg.measures:
        out[m] = np.full(len(times), np.nan)

    for i, t in enumerate(times):
        prior_t = t - h

        # --- probabilistic mismatch: observation at t vs belief made at t-h about t ---
        if prior_t in beliefs and t in beliefs[prior_t] and t < len(observations):
            prior = beliefs[prior_t][t]
            x = observations[t]
            if "surprisal" in cfg.measures:
                out["surprisal"][i] = float(np.asarray(shannon_surprise(x, prior)).ravel()[0])
            if "residual_information" in cfg.measures:
                out["residual_information"][i] = float(
                    np.asarray(residual_information(x, prior)).ravel()[0])

        # --- belief mismatch: belief(t -> t+z) vs belief(t-h -> t+z) ---
        t_about = t + z
        if (prior_t in beliefs and t in beliefs
                and t_about in beliefs.get(prior_t, {})
                and t_about in beliefs.get(t, {})):
            prior = beliefs[prior_t][t_about]
            posterior = beliefs[t][t_about]
            if "bayesian_surprise" in cfg.measures:
                out["bayesian_surprise"][i] = bayesian_surprise(
                    posterior, prior, n_samples=cfg.n_samples, rng=rng)
            if "antithesis" in cfg.measures:
                out["antithesis"][i] = antithesis(
                    posterior, prior, n_samples=cfg.n_samples, rng=rng)

    return out


def peak_summary(series: dict, measure: str, dt: float = 0.1) -> dict:
    """Convenience: peak value and its time for one measure, ignoring NaNs."""
    y = series[measure]
    if np.all(np.isnan(y)):
        return {"measure": measure, "peak": np.nan, "t_peak": np.nan, "frac_zero": np.nan}
    idx = int(np.nanargmax(y))
    finite = y[np.isfinite(y)]
    return {
        "measure": measure,
        "peak": float(y[idx]),
        "t_peak": float(series["t"][idx] * dt),
        "frac_zero": float(np.mean(np.isclose(finite, 0.0))),
    }
