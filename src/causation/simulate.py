"""
Kinematics for tier 1: the follower before its response (constant speed, as in the CBM
where the evasive maneuver is removed), and the braking execution after the onset.

Coordinates: follower front bumper at x = 0 at t = 0; gap = lead rear bumper - follower
front bumper (bumper-to-bumper, as QUADRIS's d). Crash when gap <= 0.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from quadris.load import Seed, VEHICLE_LENGTH


@dataclass
class PreResponseKinematics:
    t: np.ndarray
    x_f: np.ndarray
    v_f: np.ndarray
    x_l: np.ndarray
    v_l: np.ndarray
    gap: np.ndarray
    tau_inv: np.ndarray          # (v_f - v_l) / gap, >= 0 when closing, on the pre-response path
    t_crash_noresponse: float    # impact time if the follower never responds (nan if none)
    t_lead_onset: float          # first time the lead decelerates below -0.1 m/s^2 (nan if never)

    def first_time(self, mask: np.ndarray) -> float:
        i = np.argmax(mask)
        return float(self.t[i]) if mask.any() else np.nan


def pre_response(seed: Seed, dt: float, t_extra: float, mode: str = "original") -> PreResponseKinematics:
    """
    mode = "constant": the follower holds its initial speed until it responds (the CBM
           convention of Bärgman et al. 2024, where the evasive maneuver is removed).
    mode = "original": the follower follows the generator's own pre-response speed profile
           (modified IDM car following in QUADRIS) and holds its last speed beyond the
           recorded series. Needed for the creeping/queue seeds in which the generator's
           follower accelerates into a lead that never brakes; with a constant speed those
           seeds cannot crash at all. Tier 1 has no car-following model of its own.
    """
    t_end = seed.t_crash_orig + t_extra
    t = np.arange(0.0, t_end + dt / 2, dt)
    v_l = seed.lead_speed(t)
    x_l = seed.lead_position(t)
    if mode == "constant" or seed.v_f_orig is None:
        v_f = np.full_like(t, seed.v_f0)
    else:
        v_f = np.interp(t, seed.t, seed.v_f_orig, left=seed.v_f_orig[0], right=seed.v_f_orig[-1])
    x_f = np.concatenate([[0.0], np.cumsum(0.5 * (v_f[1:] + v_f[:-1]) * dt)])
    gap = x_l - x_f
    with np.errstate(divide="ignore", invalid="ignore"):
        tau_inv = np.where(gap > 0.01, (v_f - v_l) / np.maximum(gap, 0.01), np.inf)
    crash = gap <= 0
    t_crash = float(t[np.argmax(crash)]) if crash.any() else np.nan
    a_l = np.gradient(v_l, dt)
    onset = a_l < -0.1
    t_on = float(t[np.argmax(onset)]) if onset.any() else np.nan
    return PreResponseKinematics(t, x_f, v_f, x_l, v_l, gap, tau_inv, t_crash, t_on)


@dataclass
class Outcome:
    crashed: bool
    t_impact: float            # nan if avoided
    v_rel_impact: float        # follower - lead at impact [m/s], 0 if avoided
    t_onset: float             # brake onset (first deceleration), nan if never
    a_f_min: float             # harshest follower deceleration actually applied [m/s^2]
    min_gap: float
    t: np.ndarray
    v_f: np.ndarray
    gap: np.ndarray


def execute_braking(pre: PreResponseKinematics, t_onset: float | None, d_max: float,
                    jerk: float, dt: float) -> Outcome:
    """From t_onset the follower ramps its deceleration at `jerk` (negative) toward -d_max,
    holds it, and stops; the lead follows its profile. Before t_onset the follower keeps its
    speed. t_onset None/nan = no response."""
    t, v_l, x_l = pre.t, pre.v_l, pre.x_l
    n = len(t)
    v_f = np.empty(n); x_f = np.empty(n); a = np.zeros(n)
    v_f[0], x_f[0] = pre.v_f[0], 0.0
    responding = t_onset is not None and np.isfinite(t_onset)
    a_cur = 0.0
    crashed, t_imp, v_rel = False, np.nan, 0.0
    for i in range(1, n):
        if responding and t[i] >= t_onset and v_f[i - 1] > 0:
            a_cur = max(a_cur + jerk * dt, -d_max)
            v_new = max(v_f[i - 1] + a_cur * dt, 0.0)
        elif responding and t[i] >= t_onset:
            a_cur = 0.0; v_new = 0.0
        else:
            v_new = pre.v_f[i]            # pre-response profile (constant or generator's)
            a_cur = (v_new - v_f[i - 1]) / dt
        a[i] = (v_new - v_f[i - 1]) / dt
        x_f[i] = x_f[i - 1] + 0.5 * (v_f[i - 1] + v_new) * dt
        v_f[i] = v_new
        gap_i = x_l[i] - x_f[i]
        if gap_i <= 0 and not crashed:
            crashed, t_imp, v_rel = True, float(t[i]), float(v_f[i] - v_l[i])
            v_f[i:] = v_f[i]; x_f[i:] = x_f[i]
            break
    gap = x_l - x_f
    a_min = float(a.min()) if responding else 0.0
    return Outcome(crashed, t_imp, max(v_rel, 0.0), float(t_onset) if responding else np.nan,
                   a_min, float(gap[: (np.argmax(gap <= 0) + 1) if crashed else n].min()), t, v_f, gap)
