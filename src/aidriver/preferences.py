"""
The preference function p(o) -- the heart of the model, and the object that defines the
driver's comfort zone.

Implemented to match Schumann et al. (2026) *Supplementary Information* section 2.4
(Eqs. 44-52), which is considerably more specific than Eq. 11 of the main article:

    p(o) = N(v_ego | v_0, sigma_v)          desired speed
         * N(a_long,ego | 0, sigma_a)       minimal longitudinal control input
         * N(omega_ego | 0, sigma_omega)    minimal steering input
         * p_lat(y_ego)                     lane keeping            (triangular, Eq. 45/46)
         * p_coll(o)                        collision + inverse-tau (Eq. 47/48)
         * p_safe(o)                        braking-margin          (Eq. 49/50/51)

Working in logs throughout, so `log p(o)` is a sum of independent terms and the pragmatic
value decomposes additively -- which is what lets us attribute comfort-zone violation to a
specific cause (too fast / too close / off-lane / no escape margin).

Two things in the SI that are easy to miss and that matter a great deal:

  * `p_coll` is not only a collision cost. When there is *no* collision and the other vehicle
    is ahead, it is a Gaussian preference over **inverse tau**, tau^-1 = phi_dot / phi, with
    mean 0.2 s^-1 (i.e. TTC ~ 5 s) and sd 0.125 s^-1. This is the smooth term that shapes
    ordinary car following; without it there is no gradient pulling the driver towards a
    comfortable following distance, and the model only reacts once a collision is predicted.
  * `p_coll` is defined recursively as a running minimum over the horizon, so every timestep
    after a collision stays punished (the model has no collision mechanics and vehicles would
    otherwise phase through each other).

Parameter note: the SI gives g_LL = -5000 whereas Table 1 of the main article gives -15000.
We follow the SI, since the SI defines the functional form these constants enter.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .bicycle import BicycleParams

LOG_2PI = np.log(2 * np.pi)


def _log_gauss(x, mu, sd):
    return -0.5 * ((x - mu) / sd) ** 2 - np.log(sd) - 0.5 * LOG_2PI


@dataclass
class PreferenceParams:
    # --- desired speed -------------------------------------------------------------
    v_desired: float = 15.0
    sigma_v: float = 0.5            # m/s
    # --- control effort ------------------------------------------------------------
    sigma_a: float = 0.1            # m/s^2
    sigma_omega: float = 0.02       # 1/s
    # --- inverse tau (comfortable time-to-collision) -------------------------------
    tau_inv_mu: float = 0.2         # s^-1  (TTC ~ 5 s), from Markkula et al.
    tau_inv_sd: float = 0.125       # s^-1
    # --- road geometry -------------------------------------------------------------
    lane_width: float = 3.65        # w
    lane_centre: float = 0.0
    # --- costs (log-probability units; SI parameter list) -------------------------
    g_lane_boundary: float = -1000.0   # g_LC
    g_leave_road: float = -5000.0      # g_LL  (SI value; Table 1 of the article says -15000)
    g_collision: float = -10000.0      # g_C   at 10 m/s relative impact speed
    collision_ref_speed: float = 10.0
    severity_floor: float = 0.2        # SI: cost factor is 0.2 + 0.8 * dv / 10
    # --- safety margin (p_safe) ----------------------------------------------------
    a_other_min: float = -6.0       # a_OV,min -- calibrated per scenario (see module notes)
    a_max: float = 8.0              # |a_max| the ego can achieve
    response_time: float = 1.0      # t_react [s]
    # --- vehicle -------------------------------------------------------------------
    vehicle: BicycleParams = field(default_factory=BicycleParams)

    def max_log_preference(self) -> float:
        """
        max_o log p(o): every factor at its own maximum.

        The three Gaussian factors contribute -log(sigma sqrt(2 pi)) each; p_lat is 1
        (log 0) at the lane centre; p_safe is 1 when the margin holds; p_coll is normalised
        so that its maximum is also 0. This constant is what makes the residual information
        of the pragmatic value zero-floored.
        """
        return (
            -np.log(self.sigma_v) - 0.5 * LOG_2PI
            - np.log(self.sigma_a) - 0.5 * LOG_2PI
            - np.log(self.sigma_omega) - 0.5 * LOG_2PI
        )


# --------------------------------------------------------------------------------------
# individual factors
# --------------------------------------------------------------------------------------
def log_speed_pref(v, p: PreferenceParams):
    return _log_gauss(v, p.v_desired, p.sigma_v)


def log_accel_pref(a, p: PreferenceParams):
    return _log_gauss(a, 0.0, p.sigma_a)


def log_steer_pref(omega, p: PreferenceParams):
    return _log_gauss(omega, 0.0, p.sigma_omega)


def _y_rel(y, p: PreferenceParams):
    """
    Relative lateral position y_rel (SI Eq. 52) for a lane centred on the x-axis: measured
    from the lane centre while inside the lane, clamped while straddling the marker, then
    measured from the neighbouring lane.

        y_rel = y                 |y| <= (w-d)/2
              = (w-d)/2           (w-d)/2 < |y| <= (w+d)/2       [straddling the marker]
              = |y| - w           (w+d)/2 < |y|

    Applied symmetrically about the lane centre.
    """
    w, d = p.lane_width, p.vehicle.width
    ya = np.abs(np.asarray(y, dtype=float) - p.lane_centre)
    lo, hi = (w - d) / 2.0, (w + d) / 2.0
    return np.where(ya <= lo, ya, np.where(ya <= hi, lo, ya - w))


def log_lateral_pref(y, p: PreferenceParams):
    """
    Lane-keeping preference p_lat (SI Eqs. 45/46) -- a *triangular* function, not a step:

        T(x | x0, p1, p2) ∝ exp( |x| / x0 * p1 )   for |x| <= x0
                            exp( p2 )              otherwise

    with x0 = (w - d)/2, p1 = g_LC, p2 = g_LL.

    In logs: exactly 0 at the lane centre, falling linearly to g_LC at the lane edge, then
    flat at g_LL once off the road. Being exactly zero mid-lane is essential -- it is what
    keeps the pragmatic deficit at zero inside the comfort zone.
    """
    x0 = (p.lane_width - p.vehicle.width) / 2.0
    x = np.abs(_y_rel(y, p))
    return np.where(x <= x0, x / max(x0, 1e-9) * p.g_lane_boundary, p.g_leave_road)


def _severity(v_ego, v_other, theta_ego, theta_other, p: PreferenceParams):
    """
    Collision severity factor (SI Eq. 48):  0.2 + 0.8 * (v_ego - v_nu cos(dtheta)) / 10.

    Linear in closing speed with a floor of 0.2, so even a very low-speed collision costs
    20% of g_C. (A purely quadratic scaling would make a gentle crash cheaper than sustained
    hard braking, and the model would choose to crash -- observed while developing this.)
    """
    dv = (np.asarray(v_ego, dtype=float)
          - np.asarray(v_other, dtype=float)
          * np.cos(np.asarray(theta_ego, dtype=float)
                   - np.asarray(theta_other, dtype=float)))
    return p.severity_floor + (1.0 - p.severity_floor) * dv / p.collision_ref_speed


def inverse_tau(dx, v_ego, v_other, p: PreferenceParams):
    """
    Inverse tau, tau^-1 = phi_dot / phi -- for an object at longitudinal gap d closing at
    v_rel, the standard result is tau^-1 = v_rel / d. Positive means closing.
    """
    d = np.maximum(np.asarray(dx, dtype=float) - p.vehicle.length, 1e-3)
    return (np.asarray(v_ego, dtype=float) - np.asarray(v_other, dtype=float)) / d


def log_collision_pref(obs: dict, p: PreferenceParams):
    """
    p_coll (SI Eqs. 47/48). Three regimes:

      * **collision** -- |dy| <= 1.15 d and |dx| <= 1.15 (lf+lr):
            log f = g_C * (0.2 + 0.8 * dv / 10)
      * **other vehicle behind or alongside** (dx <= lf+lr): no cost.
      * **other vehicle ahead, no collision**: a Gaussian preference over inverse tau,
            tau^-1 ~ N(0.2 s^-1, 0.125 s^-1),
        normalised so that its maximum is 0. This is what makes ordinary following
        comfortable at TTC ~ 5 s.

    The running minimum over the horizon (Eq. 47) is a property of a rollout, not of a single
    observation, so it is applied separately by `apply_running_min`.
    """
    veh = p.vehicle
    dx = np.asarray(obs["dx"], dtype=float)          # x_other - x_ego
    dy = np.asarray(obs["dy"], dtype=float)
    v = np.asarray(obs["v"], dtype=float)
    v_other = np.asarray(obs.get("v_other", 0.0), dtype=float)
    th = np.asarray(obs.get("theta", 0.0), dtype=float)
    th_o = np.asarray(obs.get("theta_other", 0.0), dtype=float)
    tau_inv = np.asarray(obs["tau_inv"], dtype=float)

    collided = (np.abs(dy) <= 1.15 * veh.width) & (np.abs(dx) <= 1.15 * veh.length)
    ahead = dx > veh.length

    log_coll = p.g_collision * _severity(v, v_other, th, th_o, p)
    log_tau = (_log_gauss(tau_inv, p.tau_inv_mu, p.tau_inv_sd)
               - (-np.log(p.tau_inv_sd) - 0.5 * LOG_2PI))   # max normalised to 0
    return np.where(collided, log_coll, np.where(ahead, log_tau, 0.0))


def required_deceleration(obs: dict, p: PreferenceParams):
    """
    a_ego,req (SI Eq. 51): the deceleration the ego would need, *after* a reaction time, to
    avoid a collision if the lead vehicle braked at a_nu,test = min(a_other, a_OV,min).

        v_ego,react = v_ego + min(a_ego, 0) * t_react
        d_ego,react = [ x_nu - v_nu^2 / (2 a_nu,test) ]
                      - [ x_ego + v_ego t_react + 0.5 min(a_ego,0) t_react^2 ]
        a_ego,req   = -0.5 * max(v_ego,react, 0)^2 / max( d_ego,react - 1.15 (lf+lr), 0 )

    Returns a *negative* number (a deceleration), -inf when the gap has already closed.
    The comfort-zone boundary in the model's own terms is a_ego,req = -a_max: beyond it, no
    achievable braking avoids the crash.
    """
    veh = p.vehicle
    v = np.asarray(obs["v"], dtype=float)
    a = np.minimum(np.asarray(obs.get("a", 0.0), dtype=float), 0.0)
    dx = np.asarray(obs["dx"], dtype=float)
    v_other = np.asarray(obs.get("v_other", 0.0), dtype=float)
    a_other = np.minimum(np.asarray(obs.get("a_other", 0.0), dtype=float), 0.0)

    a_test = np.minimum(a_other, p.a_other_min)
    t = p.response_time

    v_react = v + a * t
    d_react = (dx - v_other ** 2 / (2.0 * a_test)) - (v * t + 0.5 * a * t ** 2)
    denom = np.maximum(d_react - 1.15 * veh.length, 0.0)

    with np.errstate(divide="ignore", invalid="ignore"):
        a_req = -0.5 * np.maximum(v_react, 0.0) ** 2 / denom
    return np.where(denom > 0, a_req, -np.inf)


def log_safety_pref(obs: dict, p: PreferenceParams):
    """
    p_safe (SI Eqs. 49/50) -- **the comfort-zone term**.

    Applies only in a car-following geometry C_brake (same lane, other vehicle ahead, same
    direction of travel), and then costs

        0.5 * g_C * (0.2 + 0.8 * dv / 10)      if a_ego,req < -a_max
        0                                       otherwise

    i.e. it is an *indicator*: the driver is penalised precisely when the counterfactual
    "lead brakes hard, I react after 1 s" would require more deceleration than is physically
    available. That boundary -- a_ego,req = -a_max -- is the model's own operationalisation
    of a comfort-zone boundary, and `comfortzone` builds on it.
    """
    veh = p.vehicle
    dx = np.asarray(obs["dx"], dtype=float)
    dy = np.asarray(obs["dy"], dtype=float)
    v = np.asarray(obs["v"], dtype=float)
    v_other = np.asarray(obs.get("v_other", 0.0), dtype=float)
    th = np.asarray(obs.get("theta", 0.0), dtype=float)
    th_o = np.asarray(obs.get("theta_other", 0.0), dtype=float)

    c_brake = ((np.abs(dy) <= 1.15 * veh.width)
               & (dx >= veh.length)
               & (np.sign(v) * np.sign(v_other * np.cos(th_o)) >= 0))
    unsafe = c_brake & (required_deceleration(obs, p) < -p.a_max)
    return np.where(unsafe, 0.5 * p.g_collision * _severity(v, v_other, th, th_o, p), 0.0)


# --------------------------------------------------------------------------------------
# full preference
# --------------------------------------------------------------------------------------
def log_preference_terms(obs: dict, p: PreferenceParams) -> dict:
    """
    Six additive log-preference terms.

    `obs` keys (all broadcastable to a common shape):
        v, a, omega        ego speed / longitudinal acceleration / steering rate
        y                  ego lateral position
        dx, dy             other vehicle position relative to the ego
        v_other, a_other   other vehicle speed / acceleration
        theta, theta_other headings (optional, default 0)
        tau_inv            inverse tau (optional; derived from dx, v, v_other if absent)
    """
    obs = dict(obs)
    if "tau_inv" not in obs:
        obs["tau_inv"] = inverse_tau(obs["dx"], obs["v"], obs.get("v_other", 0.0), p)
    terms = {
        "speed": log_speed_pref(np.asarray(obs["v"], dtype=float), p),
        "accel": log_accel_pref(np.asarray(obs.get("a", 0.0), dtype=float), p),
        "steer": log_steer_pref(np.asarray(obs.get("omega", 0.0), dtype=float), p),
        "lateral": log_lateral_pref(np.asarray(obs.get("y", p.lane_centre), dtype=float), p),
        "collision": log_collision_pref(obs, p),
        "safety": log_safety_pref(obs, p),
    }
    shape = np.broadcast_shapes(*[np.shape(v) for v in terms.values()])
    return {k: np.broadcast_to(v, shape).astype(float) for k, v in terms.items()}


def log_preference(obs: dict, p: PreferenceParams) -> np.ndarray:
    return sum(log_preference_terms(obs, p).values())


def apply_running_min(log_coll: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    SI Eq. 47:  p_coll(o_tau) = min{ p_coll(o_{tau-1}), min_nu f_coll(o_tau, nu) }.

    In log space this is a running minimum along the horizon, which keeps every timestep
    after a collision punished. Without it the model can "phase through" the other vehicle
    and pay only for the instant of contact.
    """
    return np.minimum.accumulate(log_coll, axis=axis)


def pragmatic_deficit(obs: dict, p: PreferenceParams) -> np.ndarray:
    """
    Per-observation residual information of the pragmatic value:

        eps(o) = max_o' log p(o')  -  log p(o)     >= 0

    Zero at the driver's preferred observation, growing as the situation departs from it.
    Summed over a planning horizon this is the evidence signal of Eq. 13; evaluated
    pointwise over a state space it is the **comfort-zone scalar field** (see
    `comfortzone.field`).
    """
    return np.maximum(p.max_log_preference() - log_preference(obs, p), 0.0)


def safety_margin(obs: dict, p: PreferenceParams) -> np.ndarray:
    """
    Signed comfort-zone margin in units of deceleration [m/s^2]:

        m = a_ego,req + a_max

    m > 0 : the counterfactual hard-braking lead can still be avoided -> inside the comfort
            zone
    m = 0 : the model's own comfort-zone boundary (p_safe switches on here)
    m < 0 : more braking would be required than is available -> dread zone

    Expressed this way the boundary is scenario independent: it is the same surface whether
    you approach it by closing the gap, raising speed, or lowering assumed braking capability.
    """
    return required_deceleration(obs, p) + p.a_max
