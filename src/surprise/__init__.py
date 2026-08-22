"""
surprise -- a library of computational surprise measures for driver behaviour modelling.

Organised by the taxonomy of Modirshanechi, Brea & Gerstner (2022, J. Math. Psych. 110:102712)
and the driving-domain operationalisation of Dinparastdjadid, Supeene & Engstrom (2023,
"Measuring surprise in the wild", arXiv:2305.07733).

Three families, distinguished by *what is compared with what*:

  probabilistic mismatch  observation  vs  prior belief      -> `probabilistic`
  belief mismatch         posterior belief vs prior belief   -> `belief`
  observation mismatch    observation  vs  point prediction  -> `observation`

Plus the preference-relative quantity used inside the active-inference collision-avoidance
model, which is the same mathematics applied to a *preference* prior rather than a
*predictive* prior -> `pragmatic`.

All measures operate on the `Distribution` protocol in `surprise.distributions`, so the same
metric code works on a Gaussian, a Gaussian mixture (e.g. the output of a trajectory
predictor), or a particle set (e.g. the belief of a particle-filter active-inference agent).

Quick start
-----------
>>> import numpy as np
>>> from surprise import GaussianMixture, residual_information, bayesian_surprise
>>> prior = GaussianMixture(weights=[0.7, 0.3], means=[[0.0], [3.0]], covs=[[[1.0]], [[1.0]]])
>>> residual_information(0.0, prior)          # at the mode -> ~0
>>> residual_information(6.0, prior)          # far tail   -> large
"""

from .distributions import (
    Distribution,
    Gaussian,
    GaussianMixture,
    ParticleSet,
    Categorical,
)
from .probabilistic import (
    shannon_surprise,
    surprisal,
    residual_information,
    macedo_s8,
    bayes_factor_surprise,
    state_prediction_error,
)
from .belief import (
    bayesian_surprise,
    antithesis,
    postdictive_surprise,
    confidence_corrected_surprise,
    commitment,
)
from .observation import (
    absolute_error_surprise,
    squared_error_surprise,
    unsigned_reward_prediction_error,
)
from .pragmatic import (
    pragmatic_value,
    residual_information_of_pragmatic_value,
    EvidenceAccumulator,
)
from .timeseries import surprise_time_series, SurpriseConfig

__all__ = [
    # distributions
    "Distribution", "Gaussian", "GaussianMixture", "ParticleSet", "Categorical",
    # probabilistic mismatch
    "shannon_surprise", "surprisal", "residual_information", "macedo_s8",
    "bayes_factor_surprise", "state_prediction_error",
    # belief mismatch
    "bayesian_surprise", "antithesis", "postdictive_surprise",
    "confidence_corrected_surprise", "commitment",
    # observation mismatch
    "absolute_error_surprise", "squared_error_surprise",
    "unsigned_reward_prediction_error",
    # preference-relative / active inference
    "pragmatic_value", "residual_information_of_pragmatic_value", "EvidenceAccumulator",
    # time series driver
    "surprise_time_series", "SurpriseConfig",
]

__version__ = "0.1.0"
