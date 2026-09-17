"""The ego's policy menus and their deterministic rollouts, in the freeze frame.

Card JJ.1, brief section 3.3; menus and accelerations in
`docs/rollout_boundary_design_note.md` section 1.3. The menu is the scenario's *instructed
alternatives*, which is the one scenario-specific element of the construction, and it is read
from each study's instructions rather than chosen. **No steering policy** (Jonas's ruling
JJ1.Q1, 2026-09-18): the crowd-sourced stimuli and the naturalistic data both carry that
constraint.

Every policy is a constant-acceleration segment from the freeze, speed clipped at zero, and is
deterministic: the ego knows its own plan, and all uncertainty is in the fan. The released
model's pedal constraints and jerk limits are not modeled; the design note records that
simplification.

Two scenarios need a path rather than a straight line, and both take it from the recorded ego:

* **left turn** -- "proceed" is card PC.1's reading P (`conflict.planned_path` of the ego body
  at the decision moment), and "wait" follows the same geometry with a -3 m/s^2 speed profile,
  its travelled arc length clamped at the distance to the crossing point x_conf. Stopping
  *along the road* rather than driving straight on is what "stop before the crossing" means.
* **cyclist overtake** -- "continue" is the recorded pass at the shown clearance; "abort" falls
  back at -2 m/s^2 (floored at the cyclist's speed: you end up following, not reversing) and
  returns laterally to the lane centre over ABORT_RETURN_S.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .predictor import DT_S, HORIZON_S, horizon_steps

# --- the menus (design note section 1.3) -------------------------------------------------
# 6 m/s^2 is the released model's assumed worst-case lead deceleration (a_OV,min).
CUTIN_MENU = {"continue": 0.0, "ease_off": -1.0, "brake": -3.0, "brake_hard": -6.0}
LTAP_WAIT_A = -3.0            # m/s^2, the left turn's "wait"
OVERTAKE_ABORT_A = -2.0       # m/s^2, the overtake's "abort"
ABORT_RETURN_S = 2.0          # s, the lateral return to the lane centre on "abort"
CONTINUE = "continue"         # the policy Delta G is measured from, on every scenario
LTAP_CONTINUE = "proceed"


@dataclass
class EgoPath:
    """The ego's deterministic rollout in the freeze frame, [T] each."""
    tau: np.ndarray
    x: np.ndarray
    y: np.ndarray
    v: np.ndarray          # speed [m/s]
    a: np.ndarray          # longitudinal acceleration [m/s^2], zero once stopped
    heading: np.ndarray    # rad in the freeze frame
    y_lane: np.ndarray     # lateral position relative to the EGO'S LANE CENTRE [m]
    name: str = ""


def const_accel(v0: float, a: float, tau: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Distance, speed and acceleration of a constant-acceleration segment, speed clipped at 0."""
    t_stop = -v0 / a if a < 0 else np.inf
    te = np.minimum(tau, max(t_stop, 0.0)) if np.isfinite(t_stop) else tau
    s = v0 * te + 0.5 * a * te ** 2
    v = np.maximum(v0 + a * te, 0.0)
    acc = np.where(te < tau - 1e-12, 0.0, a) if np.isfinite(t_stop) else np.full_like(tau, a)
    return s, v, acc


def ego_rollout(belief, policy: str, horizon_s: float = HORIZON_S, dt: float = DT_S,
                menu: dict[str, float] | None = None, y_lane_offset: float = 0.0) -> EgoPath:
    """The straight-road rollout: a constant-acceleration segment, no steering, y = 0.

    `y_lane_offset` is the ego's lateral displacement from its own lane centre at the freeze
    (zero on the cut-in, where the stimulus ego holds its lane), so that the preference
    function's lane-keeping term sees the real offset while the frame keeps its origin.
    """
    menu = menu if menu is not None else CUTIN_MENU
    if policy not in menu:
        raise KeyError(f"policy {policy!r} not in the menu {sorted(menu)}")
    tau = horizon_steps(horizon_s, dt)
    s, v, a = const_accel(float(belief.v_ego), float(menu[policy]), tau)
    zero = np.zeros_like(tau)
    return EgoPath(tau=tau, x=s, y=zero, v=v, a=a, heading=zero.copy(),
                   y_lane=np.full_like(tau, y_lane_offset), name=policy)


# ---------------------------------------------------------------------------------------
# path-following rollouts (the left turn and the overtake)
# ---------------------------------------------------------------------------------------

def _arc_length(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    d = np.hypot(np.diff(x), np.diff(y))
    return np.concatenate([[0.0], np.cumsum(d)])


def follow_path(path_x: np.ndarray, path_y: np.ndarray, path_s: np.ndarray, s_of_tau: np.ndarray,
                tau: np.ndarray, v: np.ndarray, a: np.ndarray, y_lane: np.ndarray,
                name: str) -> EgoPath:
    """Place the ego at arc length `s_of_tau` along a polyline, with its heading tangent."""
    x = np.interp(s_of_tau, path_s, path_x)
    y = np.interp(s_of_tau, path_s, path_y)
    eps = 0.05
    xf = np.interp(s_of_tau + eps, path_s, path_x)
    yf = np.interp(s_of_tau + eps, path_s, path_y)
    xb = np.interp(np.maximum(s_of_tau - eps, path_s[0]), path_s, path_x)
    yb = np.interp(np.maximum(s_of_tau - eps, path_s[0]), path_s, path_y)
    heading = np.arctan2(yf - yb, xf - xb)
    return EgoPath(tau=tau, x=x, y=y, v=v, a=a, heading=heading, y_lane=y_lane, name=name)


def ltap_rollout(belief, policy: str, path_x: np.ndarray, path_y: np.ndarray,
                 s_recorded: np.ndarray, s_conf: float, horizon_s: float = HORIZON_S,
                 dt: float = DT_S) -> EgoPath:
    """The left turn's menu: "proceed" (the recorded turn) and "wait" (stop before x_conf).

    `path_x, path_y` are the recorded ego path in the freeze frame on the rollout's own tau
    grid extended over the path span; `s_recorded` is the arc length the ego actually covers by
    each tau; `s_conf` the arc length to the crossing point.

    `y_lane` is zero for both policies: the ego is on its own intended path throughout, and the
    released lane-keeping term -- a straight-road construct -- would otherwise charge "proceed"
    the road-edge cost simply for turning. Query JJ3.Q1 records the decision.
    """
    tau = horizon_steps(horizon_s, dt)
    path_s = _arc_length(path_x, path_y)
    if policy == LTAP_CONTINUE:
        s_of_tau = np.asarray(s_recorded, float)
        v = np.gradient(s_of_tau, tau)
        a = np.gradient(v, tau)
    elif policy == "wait":
        s_free, v, a = const_accel(float(belief.v_ego), LTAP_WAIT_A, tau)
        s_of_tau = np.minimum(s_free, s_conf)
        v = np.where(s_free <= s_conf + 1e-9, v, 0.0)
        a = np.where(s_free <= s_conf + 1e-9, a, 0.0)
    else:
        raise KeyError(f"policy {policy!r} not in the left turn's menu ['proceed', 'wait']")
    return follow_path(path_x, path_y, path_s, s_of_tau, tau, v, a,
                       np.zeros_like(tau), policy)


def overtake_rollout(belief, policy: str, path_x: np.ndarray, path_y: np.ndarray,
                     s_recorded: np.ndarray, y_lane_recorded: np.ndarray,
                     y_lane_offset: float, v_cyclist: float,
                     horizon_s: float = HORIZON_S, dt: float = DT_S) -> EgoPath:
    """The overtake's menu: "continue" the pass at the shown clearance, or "abort"."""
    tau = horizon_steps(horizon_s, dt)
    path_s = _arc_length(path_x, path_y)
    if policy == CONTINUE:
        s_of_tau = np.asarray(s_recorded, float)
        v = np.gradient(s_of_tau, tau)
        a = np.gradient(v, tau)
        return follow_path(path_x, path_y, path_s, s_of_tau, tau, v, a,
                           np.asarray(y_lane_recorded, float), policy)
    if policy != "abort":
        raise KeyError(f"policy {policy!r} not in the overtake's menu ['continue', 'abort']")
    # Fall back behind the cyclist: -2 m/s^2 floored at the cyclist's speed (following, not
    # reversing), and return laterally to the lane centre over ABORT_RETURN_S.
    v_floor = max(float(v_cyclist), 0.0)
    v0 = float(belief.v_ego)
    t_floor = (v0 - v_floor) / abs(OVERTAKE_ABORT_A) if v0 > v_floor else 0.0
    te = np.minimum(tau, t_floor)
    s_of_tau = v0 * te + 0.5 * OVERTAKE_ABORT_A * te ** 2 + v_floor * np.maximum(tau - t_floor, 0.0)
    v = np.where(tau <= t_floor, v0 + OVERTAKE_ABORT_A * tau, v_floor)
    a = np.where(tau <= t_floor, OVERTAKE_ABORT_A, 0.0)
    frac = np.clip(1.0 - tau / ABORT_RETURN_S, 0.0, 1.0)
    y_lane = y_lane_offset * frac
    # In the frame the ego runs straight ahead (the frame's x-axis is its direction of travel
    # at the freeze) and moves laterally from its current offset back to the lane centre.
    return EgoPath(tau=tau, x=s_of_tau, y=y_lane - y_lane_offset, v=v, a=a,
                   heading=np.zeros_like(tau), y_lane=y_lane, name=policy)
