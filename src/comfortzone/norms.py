"""
Norms for a cut-in: what counts as normal behavior of a vehicle changing into our lane.

Card PN.1 (2026-09-13), a proposal to discuss with Julian Schumann. The released model's norms
(`reward.py::get_weights` in each scenario) are purely positional -- rear-end: the lead's body
inside the lane; oncoming: inside its own lane and at its speed -- and they drive the
norm tournament that shapes both the belief update and the imagined futures (handbook ch. 06).
A legal lane change leaves the vehicle's own lane by definition, so a positional norm withdraws
trust at every cut-in, and at a moment that depends on how fast the lane change goes.

Two norms are written here in the released code's own vocabulary, as functions of the target's
state only, so that either could replace `get_weights` without new state in the particles:

* `own_lane_norm`   the released form (the oncoming scenario's structure) applied to the
                    cutting-in vehicle's own lane. The baseline.
* `crossing_norm`   the proposal. In either lane, fully normal. Straddling the boundary is
                    normal WHILE CROSSING at a plausible lateral speed toward the destination
                    lane; stalling on the line, drifting back, or swerving across faster than
                    any ordinary lane change are not. Off the road is a gross violation.

Why lateral speed rather than elapsed time ("a plausible duration"): the particles carry
position, heading and speed (`dynamics.py`, target state x, y, theta, delta, v), so the lateral
speed v sin(theta) is available to `get_weights` as it stands. A straddling clock would need a
new state variable threaded through the belief machinery, which the handbook's own criterion
(ch. 09) counts as a research project rather than a modification.

Parameter values and their motivation (each a judgment, flagged where unverified):
* `weigh_particles = 0.001`, `full_violation_factor = 0.01` -- the released code's values.
* `v_lo = 0.5 m/s` -- slower than this while straddling counts as lingering. A 3.5 m lane change
  at a mean of 0.5 m/s takes 7 s. UNVERIFIED against naturalistic lane-change durations
  (query PN1.Q1).
* `v_hi = 3.0 m/s` -- faster than this counts as a swerve. It sits just above the fastest peak
  lateral speed among the second cut-in study's lane changes (about 2.7 m/s at a 2 s duration).
* `v_tol = 0.5 m/s` -- width of the quadratic fall-off outside [v_lo, v_hi], chosen for a
  smooth transition; the floor is sqrt(weigh_particles), as the released oncoming speed norm
  clips its own quadratic.
"""
from __future__ import annotations

import numpy as np

WEIGH_PARTICLES = 0.001
FULL_VIOLATION_FACTOR = 0.01


def _bands(offset, lane_width, d):
    """Positional categories for a vehicle whose own lane centre is at offset 0 and whose
    destination lane centre is at +lane_width. The released code's in-lane band is the centre
    within (lane_width - d)/2 of a lane centre, i.e. the body entirely inside the lane."""
    alw = 0.5 * (lane_width - d)
    off = np.asarray(offset, float)
    in_own = np.abs(off) < alw
    in_dest = np.abs(off - lane_width) < alw
    straddling = (off >= alw) & (off <= lane_width - alw)
    off_road = (off < -alw - 0.2 * d) | (off > lane_width + alw + 0.2 * d)
    return in_own, in_dest, straddling, off_road


def own_lane_norm(offset, lane_width: float, d: float,
                  weigh_particles: float = WEIGH_PARTICLES,
                  full_violation_factor: float = FULL_VIOLATION_FACTOR) -> np.ndarray:
    """The released structure: normal only inside the vehicle's own lane."""
    in_own, _, _, off_road = _bands(offset, lane_width, d)
    w = np.full(np.shape(offset), weigh_particles, dtype=float)
    w[in_own] = 1.0
    w[off_road] = weigh_particles * full_violation_factor
    return w


def lateral_speed_compliance(v_toward, v_lo: float = 0.5, v_hi: float = 3.0,
                             v_tol: float = 0.5,
                             weigh_particles: float = WEIGH_PARTICLES) -> np.ndarray:
    """1 inside [v_lo, v_hi]; quadratic fall-off of width v_tol outside; floored at
    sqrt(weigh_particles). Negative (moving back toward its own lane) falls off from v_lo."""
    v = np.asarray(v_toward, float)
    dist = np.where(v < v_lo, v_lo - v, np.where(v > v_hi, v - v_hi, 0.0))
    return np.clip(1.0 - (dist / v_tol) ** 2, np.sqrt(weigh_particles), 1.0)


def crossing_norm(offset, v_toward, lane_width: float, d: float,
                  v_lo: float = 0.5, v_hi: float = 3.0, v_tol: float = 0.5,
                  weigh_particles: float = WEIGH_PARTICLES,
                  full_violation_factor: float = FULL_VIOLATION_FACTOR) -> np.ndarray:
    """The proposal: either lane is normal; straddling is normal while crossing at a plausible
    lateral speed toward the destination lane; off road is a gross violation."""
    in_own, in_dest, straddling, off_road = _bands(offset, lane_width, d)
    w = np.full(np.shape(offset), weigh_particles, dtype=float)
    w[in_own | in_dest] = 1.0
    comp = lateral_speed_compliance(v_toward, v_lo, v_hi, v_tol, weigh_particles)
    w[straddling] = comp[straddling]
    w[off_road] = weigh_particles * full_violation_factor
    return w
