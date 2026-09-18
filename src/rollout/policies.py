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

# --- steering (added 2026-09-18, card JJ.2b; NOT part of the JJ.1 menus) -------------------
# Ruling JJ1.Q1 kept steering out of the menus because the crowd-sourced stimuli and the
# naturalistic data both carry that constraint. Card RE.1 then showed that on this very design
# the released CEM planner's chosen escape is a STEER in 36 of 36 cells and never a brake
# (`replication/causation/re1/re1_rear_end_criticality.md` part C), so a menu without steering
# is not the comparison the model itself makes. These two policies exist for the model side of
# that comparison only; the response data still carry the no-steering constraint.
#
# Neither magnitude is invented. The lateral profile is the minimum-jerk-like sinusoid
#     y(tau) = -s * D/2 * (1 - cos(pi tau / T)),  held at -s * D after T,
# away from the intruder (s is the intruder's side), whose peak lateral acceleration is
# D/2 * (pi/T)^2.
#   LANE_CHANGE_D     one lane, the studies' own 3.5 m (`comfortzone.cutin.LANE_WIDTH_STUDY`)
#   STEER_T           3.0 s, inside the studies' own lane-change durations (LCD 2, 3, 4 s)
#   SWERVE_T          1.5 s, the duration whose peak lateral acceleration, 7.3 m/s^2 at the
#                     study's 30.5 m/s, is the one the released planner itself chooses on this
#                     design (RE.1 part C: median max |omega| 0.24 rad/s, and a_lat = v omega)
LANE_CHANGE_D = 3.5
STEER_T = 3.0
SWERVE_T = 1.5
STEER_MENU = {"steer": STEER_T, "swerve": SWERVE_T}
CUTIN_MENU_STEER = dict(CUTIN_MENU)     # the JJ.1 menu plus the two steering policies
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
    # The two steering channels the released preference reads. Both default to zero, which is
    # every policy written before 2026-09-18 and the ruling JJ1.Q1 menus; a steering policy
    # fills them, and then the released steering term (sigma_omega = 0.02) and the total-accel
    # form of the control-effort term both charge for the manoeuvre, as they should.
    omega: np.ndarray | None = None       # yaw rate [1/s]
    a_lat: np.ndarray | None = None       # lateral acceleration [m/s^2]

    def __post_init__(self):
        if self.omega is None:
            self.omega = np.zeros_like(self.tau)
        if self.a_lat is None:
            self.a_lat = np.zeros_like(self.tau)


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


def steer_rollout(belief, policy: str, horizon_s: float = HORIZON_S, dt: float = DT_S,
                  y_lane_offset: float = 0.0, d: float = LANE_CHANGE_D) -> EgoPath:
    """A lane change AWAY from the other road user, holding speed (card JJ.2b).

    The side is read from the scene, never assumed: the intruder sits at `belief.y_rel`, so the
    escape is toward -sign(y_rel). Speed is held, because the released planner's own escape on
    this design holds or slightly raises speed (RE.1 part C, median first acceleration +0.35 to
    +0.91 m/s^2); a policy that brakes AND steers is a different thing and is not in this menu.
    """
    if policy not in STEER_MENU:
        raise KeyError(f"policy {policy!r} not in the steering menu {sorted(STEER_MENU)}")
    T = STEER_MENU[policy]
    tau = horizon_steps(horizon_s, dt)
    s = -belief.toward_sign          # away from the intruder
    u = np.clip(tau / T, 0.0, 1.0)
    y = s * 0.5 * d * (1.0 - np.cos(np.pi * u))
    ydot = np.where(tau < T, s * 0.5 * d * (np.pi / T) * np.sin(np.pi * u), 0.0)
    yddot = np.where(tau < T, s * 0.5 * d * (np.pi / T) ** 2 * np.cos(np.pi * u), 0.0)
    v0 = float(belief.v_ego)
    heading = np.arctan2(ydot, v0)
    omega = np.gradient(heading, tau)
    return EgoPath(tau=tau, x=v0 * tau, y=y, v=np.full_like(tau, v0), a=np.zeros_like(tau),
                   heading=heading, y_lane=y_lane_offset + y, name=policy,
                   omega=omega, a_lat=yddot)


def cutin_menu_paths(belief, horizon_s: float = HORIZON_S, dt: float = DT_S,
                     steering: bool = False, y_lane_offset: float = 0.0) -> dict[str, EgoPath]:
    """The cut-in menu as a dict of rollouts: the four longitudinal policies of ruling JJ1.Q1,
    and with `steering=True` the two of card JJ.2b as well."""
    paths = {k: ego_rollout(belief, k, horizon_s, dt, y_lane_offset=y_lane_offset)
             for k in CUTIN_MENU}
    if steering:
        paths.update({k: steer_rollout(belief, k, horizon_s, dt, y_lane_offset=y_lane_offset)
                      for k in STEER_MENU})
    return paths


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


def ltap_wait_accel(v0: float, s_stop: float, a_nominal: float = LTAP_WAIT_A,
                    a_max: float = 8.0) -> tuple[float, bool]:
    """The deceleration "wait" actually needs, and whether the nominal -3 m/s^2 sufficed.

    The design note fixes the left turn's "wait" as "stop before the crossing at -3 m/s^2". In
    these stimuli the two halves of that sentence are not both satisfiable: at the decision
    moment the ego is about 7.8 m/s with about 7 m of path left before the conflict band, which
    needs about 4.2 m/s^2. What the policy IS -- the ego waits, it does not enter the
    intersection -- is the part that cannot be given up without turning "wait" into a policy
    that gets hit, so the deceleration is raised to whatever just stops the ego clear, capped at
    the ego's achievable `a_max`, and the report gives the value per cell. Query JJ3.Q2.
    """
    need = v0 * v0 / (2.0 * max(s_stop, 1e-6))
    if need <= abs(a_nominal):
        return a_nominal, True
    return -min(need, a_max), False


def ltap_rollout(belief, policy: str, path_x: np.ndarray, path_y: np.ndarray,
                 s_recorded: np.ndarray, s_conf: float, horizon_s: float = HORIZON_S,
                 dt: float = DT_S, a_wait: float = LTAP_WAIT_A) -> EgoPath:
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
        s_free, v, a = const_accel(float(belief.v_ego), a_wait, tau)
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
