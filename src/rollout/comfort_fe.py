"""The comfort-zone boundary as a free energy of the present observation (card JJ.10).

Jonas, 2026-09-22: *"Is there any way to frame the continuous gate in terms of a free energy
component? Intuitively it seems logical, but I do not know how."*

The reading (`docs/looming_as_free_energy.md`, reading B, with the gate of card JJ.6e): a driver
carries a prior over the looming of a LEAD, an object in the driver's path,

    -log C(theta_dot | lead) = 1/2 ((log theta_dot - log theta_0) / sigma_c)^2   for theta_dot > theta_0,
                             = 0                                                  otherwise,

(one-sided, on the log scale: card JJ.8 rejected the additive scale). Whether the object IS a lead
is not observed; it is predicted by the generative model of the other's lateral motion, and the
free energy of the present observation is the EXPECTATION of the prediction error over that
predictive distribution:

    F = E_pred[ 1[in my path within T] * excess(theta_dot) ] = P(lead) * excess(theta_dot),

    P(lead) = Phi((m - l0 - ldot T) / (sigma_lat T))          (card JJ.6e's gate)

So the continuous gate is the predictive probability that the looming prior applies, and F is
what the driver would minimise by acting. Two response models follow, and they differ:

  **mixture**   the driver first resolves "is it a lead" (with probability P(lead)) and then judges
                the looming: P(respond) = P(lead) * P(excess > 0). With a log-normal population of
                levels, P(excess > 0) = Phi((log theta_dot - m_level) / s_level), and this IS the
                gated looming rule of cards G.1 / EL.1b: the gate multiplies the PROBABILITY.
  **expected**  the driver judges the expected free energy itself: responds when F exceeds a
                level, i.e. when P(lead) * excess is large. The gate multiplies the QUANTITY. With
                a log-normal population of levels on that quantity: P(respond) =
                Phi((log(P(lead) * theta_dot) - m) / s), the threshold on the EXPECTED LOOMING of a
                lead (excess is monotone in theta_dot for a fixed theta_0, so the threshold can be
                put on the expected looming directly).

Both have three fitted parameters (lapse, level, spread) given sigma_lat and T; nothing else.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm

SIGMA_LAT = 0.33     # m/s, the predictor's lateral-rate uncertainty (card JJ.6e; from G.1's s_l)
T_ANTICIPATION = 3.0  # s, card G.1's horizon


def looming_excess(theta_dot, theta_0: float, sigma_c: float):
    """1/2 ((log theta_dot - log theta_0) / sigma_c)^2, zero below theta_0 [nats]."""
    z = np.maximum(np.log(np.asarray(theta_dot, float)) - np.log(theta_0), 0.0) / sigma_c
    return 0.5 * z ** 2


def p_lead(l0, ldot, sigma_lat: float = SIGMA_LAT, horizon_s: float = T_ANTICIPATION,
           margin_m: float = 0.0):
    """P(the other's body reaches the ego's within the horizon), Gaussian-rate predictor."""
    return norm.cdf((margin_m - np.asarray(l0, float) - np.asarray(ldot, float) * horizon_s)
                    / (sigma_lat * horizon_s))


def comfort_free_energy(theta_dot, l0, ldot, theta_0: float, sigma_c: float,
                        sigma_lat: float = SIGMA_LAT, horizon_s: float = T_ANTICIPATION):
    """F = P(lead) * excess, in nats: the free energy of the present observation under a prior
    over the looming of a lead, with the lead's status predicted rather than observed."""
    return p_lead(l0, ldot, sigma_lat, horizon_s) * looming_excess(theta_dot, theta_0, sigma_c)


def expected_looming(theta_dot, l0, ldot, sigma_lat: float = SIGMA_LAT,
                     horizon_s: float = T_ANTICIPATION):
    """P(lead) * theta_dot: the looming the driver expects from a lead [rad/s]."""
    return p_lead(l0, ldot, sigma_lat, horizon_s) * np.asarray(theta_dot, float)


def p_respond_mixture(theta_dot, l0, ldot, m_level: float, s_level: float, lapse: float = 0.0,
                      sigma_lat: float = SIGMA_LAT, horizon_s: float = T_ANTICIPATION):
    """The gate on the probability: lapse + (1 - lapse) P(lead) Phi((log theta_dot - m)/s)."""
    core = norm.cdf((np.log(np.asarray(theta_dot, float)) - m_level) / s_level)
    return lapse + (1.0 - lapse) * p_lead(l0, ldot, sigma_lat, horizon_s) * core


def p_respond_expected(theta_dot, l0, ldot, m_level: float, s_level: float, lapse: float = 0.0,
                       sigma_lat: float = SIGMA_LAT, horizon_s: float = T_ANTICIPATION):
    """The gate on the quantity: lapse + (1 - lapse) Phi((log(P(lead) theta_dot) - m)/s)."""
    x = np.log(np.maximum(expected_looming(theta_dot, l0, ldot, sigma_lat, horizon_s), 1e-300))
    return lapse + (1.0 - lapse) * norm.cdf((x - m_level) / s_level)
