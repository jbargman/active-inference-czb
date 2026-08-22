"""
Kinematic bicycle model -- the state transition function p(s'|s,a) of the generative model.

Matches the parameterisation used by Schumann et al. (2026): state [x, y, theta, delta, v],
action [a, omega] (longitudinal acceleration and steering *rate*), vehicle 4.2 x 1.72 m with
lf = lr = 2.1 m, a_max = 8 m/s^2, omega_max = 1.22 rad/s, dt = 0.2 s.

Everything is vectorised over a leading "particle" axis so that a whole belief can be
propagated in one call.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

X, Y, THETA, DELTA, V = 0, 1, 2, 3, 4
STATE_DIM = 5


@dataclass
class BicycleParams:
    lf: float = 2.1
    lr: float = 2.1
    width: float = 1.72
    a_max: float = 8.0
    omega_max: float = 1.22
    delta_max: float = np.pi / 4
    v_max: float = 60.0
    dt: float = 0.2

    @property
    def length(self) -> float:
        return self.lf + self.lr


def step(s: np.ndarray, u: np.ndarray, p: BicycleParams, dt: float | None = None) -> np.ndarray:
    """
    Advance states `s` (..., 5) by actions `u` (..., 2) for one timestep.

    Uses the centre-of-gravity kinematic bicycle model with slip angle
        beta = arctan( lr / (lf + lr) * tan(delta) ).
    Speed is clamped at zero: a braking vehicle stops rather than reversing, which matters
    because collision-avoidance scenarios routinely brake to a standstill.
    """
    dt = p.dt if dt is None else dt
    s = np.asarray(s, dtype=float)
    u = np.asarray(u, dtype=float)

    a = np.clip(u[..., 0], -p.a_max, p.a_max)
    omega = np.clip(u[..., 1], -p.omega_max, p.omega_max)

    x, y, theta, delta, v = (s[..., i] for i in range(STATE_DIM))

    delta_n = np.clip(delta + omega * dt, -p.delta_max, p.delta_max)
    v_n = np.clip(v + a * dt, 0.0, p.v_max)

    beta = np.arctan(p.lr / p.length * np.tan(delta_n))
    theta_n = theta + (v_n / p.lr) * np.sin(beta) * dt
    x_n = x + v_n * np.cos(theta_n + beta) * dt
    y_n = y + v_n * np.sin(theta_n + beta) * dt

    return np.stack([x_n, y_n, theta_n, delta_n, v_n], axis=-1)


def rollout(s0: np.ndarray, actions: np.ndarray, p: BicycleParams) -> np.ndarray:
    """
    Roll a state forward under a sequence of actions.

    Parameters
    ----------
    s0       : (..., 5)
    actions  : (..., H, 2)

    Returns
    -------
    (..., H, 5) -- states at each of the H steps (excluding s0).
    """
    H = actions.shape[-2]
    s = s0
    out = []
    for k in range(H):
        s = step(s, actions[..., k, :], p)
        out.append(s)
    return np.stack(out, axis=-2)


# --------------------------------------------------------------------------------------
# Perception: looming
# --------------------------------------------------------------------------------------
def visual_angle(distance: np.ndarray, width: float) -> np.ndarray:
    """
    Visual angle phi subtended by an object of given width at a given distance:
        phi = 2 * arctan( W / (2 d) ).
    """
    d = np.maximum(np.asarray(distance, dtype=float), 1e-3)
    return 2.0 * np.arctan(width / (2.0 * d))


def looming_rate(distance: np.ndarray, closing_speed: np.ndarray, width: float) -> np.ndarray:
    """
    Optical expansion rate phi_dot = d(phi)/dt.

    With phi = 2 arctan(W / 2d) and d_dot = -closing_speed,
        phi_dot = W * closing_speed / (d^2 + W^2/4).

    This is the quantity the model actually observes. Two consequences that the model relies
    on, both emerging from the geometry rather than being fitted:
      * uncertainty about distance and speed grows with distance, because a fixed error in
        phi maps to a larger error in d as d grows;
      * below a detection threshold phi_dot_0 (~0.00215 rad/s) a closing speed is simply not
        perceptible, which delays detection of a lead vehicle's braking.
    """
    d = np.maximum(np.asarray(distance, dtype=float), 1e-3)
    return width * np.asarray(closing_speed, dtype=float) / (d ** 2 + width ** 2 / 4.0)


def looming_detectable(distance, closing_speed, width, threshold: float = 0.00215) -> np.ndarray:
    """Whether the looming signal exceeds the human detection threshold."""
    return np.abs(looming_rate(distance, closing_speed, width)) >= threshold
