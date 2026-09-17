"""P0: the fan of the other road user's futures, in the freeze frame.

Card JJ.1, brief section 3.2; construction and constants in
`docs/rollout_boundary_design_note.md` section 1.2. Constant-velocity Gaussian with growth and
a latent lane-change intention.

Per sample, all drawn once and held constant over the sample's horizon -- which is what
"growth linear in tau for the position sd, in tau^2 for acceleration" means:

  intention   ~ Bernoulli(p_change)
  position offsets (dx0, dy0) ~ N(0, sd_pos)            the belief's measurement floor
  lateral perturbation eps_vlat ~ N(0, SD_VLAT)         only under "keeping"
  longitudinal acceleration eps_a ~ N(0, SD_A)

  x(tau) = x0 + dx0 + v0 tau + 0.5 eps_a tau^2          (speed floored at 0, then held)
  keeping  : u(tau) = max(u0 + dy0s + (sign * (vy0 + eps_vlat)) tau, min(u0, LANE_EDGE))
  changing : u(tau) = max(u0 + dy0s - V_LC tau, 0)

with u the lateral distance measured positive on the other's own side of the ego's lane centre
(u = sign(y_rel) * y). The clip under "keeping" is the lane the other is keeping: it may drift,
but it does not cross into the ego's lane, and it never comes closer to the ego's lane centre
than it already is (post-onset cells start with the vehicle part-way in). Under "changing" the
lateral motion stops at the ego's lane centre, u = 0.

**Common random numbers are a design requirement, not an optimization** (design note section
1.2): one `Futures` object is built per cell and handed to every policy, so Delta G is a
difference between paired scores.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .belief import Belief, V_LC_MPS

# --- growth constants (design note section 1.2, with their motivation) -------------------
SD_VLAT = 0.33      # m/s; G.1's fitted gate spread 0.99 m over its 3 s horizon, as a rate
SD_VLAT_SWEEP = (0.1, 0.33, 0.6)
SD_A = 0.5          # m/s^2; UNVERIFIED placeholder, query JJ1.Q2, replaced by GM.1's C3
SD_A_SWEEP = (0.25, 0.5, 1.0)
HORIZON_S = 6.0     # s; the released model's planning horizon (30 steps of 0.2 s)
HORIZON_SWEEP = (3.0, 6.0)
DT_S = 0.2          # s; the released model's step
N_SAMPLES = 200     # enough for the Monte Carlo rule (e); checked, never assumed
LANE_EDGE_M = 1.75  # m; half the studies' 3.5 m lane (comfortzone.cutin.LANE_WIDTH_STUDY)


@dataclass
class Futures:
    """The other road user's sampled futures in the freeze frame, [n, T] each."""
    tau: np.ndarray        # [T], the step times from the freeze, tau[0] = dt (not 0)
    x: np.ndarray
    y: np.ndarray
    v: np.ndarray          # speed |(vx, vy)|, what the preference terms are given as v_other
    vx: np.ndarray         # signed longitudinal rate in the frame
    vy: np.ndarray         # signed lateral rate in the frame
    heading: np.ndarray    # rad in the freeze frame
    changing: np.ndarray   # [n] bool, the drawn intention
    seed: int = 0

    @property
    def n(self) -> int:
        return self.x.shape[0]


def horizon_steps(horizon_s: float = HORIZON_S, dt: float = DT_S) -> np.ndarray:
    """tau = dt, 2 dt, ..., horizon. The freeze itself (tau = 0) is not a step of the rollout:
    nothing is decided there, and the released model's horizon is 30 steps of 0.2 s."""
    n = int(round(horizon_s / dt))
    return dt * np.arange(1, n + 1, dtype=float)


def sample_futures(belief: Belief, horizon_s: float = HORIZON_S, dt: float = DT_S,
                   n: int = N_SAMPLES, sd_vlat: float = SD_VLAT, sd_a: float = SD_A,
                   seed: int = 0, v_lc: float = V_LC_MPS) -> Futures:
    """The fan. One `numpy.random.default_rng(seed)`; the same object goes to every policy."""
    rng = np.random.default_rng(seed)
    tau = horizon_steps(horizon_s, dt)
    T = len(tau)
    sign = belief.toward_sign

    changing = rng.random(n) < belief.p_change
    dx0 = rng.normal(0.0, belief.sd_pos, n) if belief.sd_pos > 0 else np.zeros(n)
    dy0 = rng.normal(0.0, belief.sd_pos, n) if belief.sd_pos > 0 else np.zeros(n)
    eps_vlat = rng.normal(0.0, sd_vlat, n) if sd_vlat > 0 else np.zeros(n)
    eps_a = rng.normal(0.0, sd_a, n) if sd_a > 0 else np.zeros(n)

    # --- longitudinal: constant velocity plus a constant acceleration perturbation --------
    # Worked in the direction of travel so that an oncoming body (vx < 0 in the frame) decays
    # to a standstill rather than reversing; s0 carries the direction back into the frame.
    vx0 = belief.vx_oth if abs(belief.vx_oth) > 1e-9 else belief.v_oth * np.cos(belief.oth_heading)
    s0 = 1.0 if vx0 >= 0 else -1.0
    speed0 = abs(vx0)
    t_stop = np.where(eps_a < 0, speed0 / np.where(eps_a < 0, -eps_a, 1.0), np.inf)
    te = np.minimum(tau[None, :], np.maximum(t_stop, 0.0)[:, None])   # travel stops at a standstill
    x = (belief.x_rel + dx0)[:, None] + s0 * (speed0 * te + 0.5 * eps_a[:, None] * te ** 2)
    vx = s0 * np.maximum(speed0 + eps_a[:, None] * te, 0.0)

    # --- lateral: the intention mixture ---------------------------------------------------
    u0 = sign * belief.y_rel + sign * dy0                          # positive on the other's side
    keep_rate = sign * (belief.vy_oth + eps_vlat)
    u_keep = u0[:, None] + keep_rate[:, None] * tau[None, :]
    bound = np.minimum(sign * belief.y_rel, LANE_EDGE_M)           # never further in than now
    u_keep = np.maximum(u_keep, bound)
    u_chg = np.maximum(u0[:, None] - v_lc * tau[None, :], 0.0)
    u = np.where(changing[:, None], u_chg, u_keep)
    y = sign * u
    vy = np.gradient(y, tau, axis=1) if T > 1 else np.zeros_like(y)

    v = np.hypot(vx, vy)                        # the speed the preference terms are given
    heading = np.arctan2(vy, vx)                # rad in the freeze frame
    return Futures(tau=tau, x=x, y=y, v=v, vx=vx, vy=vy, heading=heading, changing=changing,
                   seed=seed)


def analytic_lateral_mean(belief: Belief, tau: float, v_lc: float = V_LC_MPS) -> float:
    """E[y(tau)] under the mixture, before any clipping -- the reference of property test (5).

    Exact only where neither clip binds, which is why the test evaluates it on a scene whose
    lateral geometry keeps both branches inside their bounds.
    """
    sign = belief.toward_sign
    u0 = sign * belief.y_rel
    u_keep = u0 + sign * belief.vy_oth * tau
    u_chg = max(u0 - v_lc * tau, 0.0)
    p = belief.p_change
    return float(sign * (p * u_chg + (1.0 - p) * u_keep))
