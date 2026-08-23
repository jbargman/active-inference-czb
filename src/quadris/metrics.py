"""
Scenario metrics of Wu et al. (2026) §3.2, plus helpers.

All conventions that are assumptions rather than data are marked ASSUMPTION and collected
in docs/crash_causation_plan.md section 8 (inputs needed).
"""
from __future__ import annotations

import numpy as np

A_NR = -9.0                  # [m/s^2] braking used in the no-return-time definition (Wu 2026)
MASS_RATIO_FOLLOWER = 0.5    # ASSUMPTION: equal masses -> lead delta-v = half the impact speed


def delta_v_lead(v_rel_impact: float, mass_share_follower: float = MASS_RATIO_FOLLOWER) -> float:
    """Lead vehicle's speed change in a fully plastic rear-end impact:
    dv_lead = m_f / (m_f + m_l) * v_rel. The CSV carries no masses, so equal masses are
    assumed (ASSUMPTION; Wu et al. 2025a §III-F describe the estimate used for QUADRIS)."""
    return float(mass_share_follower * max(v_rel_impact, 0.0))


def p_inj_mais2(dv_lead_ms: float) -> float:
    """MAIS2+ injury risk of the lead driver, Wang (2022) as quoted in Wu et al. (2026) Eq. 12,
    with delta-v in m/s. Zero if no crash (dv <= 0)."""
    if dv_lead_ms <= 0:
        return 0.0
    return float(1.0 / (1.0 + np.exp(6.1818 - 0.3315 * dv_lead_ms)))


def no_return_time(t: np.ndarray, gap: np.ndarray, v_f: np.ndarray, v_l: np.ndarray,
                   a_brake: float = A_NR) -> float:
    """
    No-return time t_nr (Wu 2026): the last instant, measured relative to the impact at
    t = 0 (so t_nr <= 0), at which the follower could still avoid the collision by braking
    at a_brake from that instant, with the lead continuing its recorded profile.
    Evaluated on the trajectories as given; returns NaN if the scenario has no impact.
    """
    t = np.asarray(t, float); gap = np.asarray(gap, float)
    v_f = np.asarray(v_f, float); v_l = np.asarray(v_l, float)
    if gap[-1] > 0.05:
        return np.nan
    dt = float(np.median(np.diff(t)))
    last_ok = np.nan
    for i in range(len(t)):
        # roll the follower forward from i with constant a_brake until stopped; lead as recorded
        x_rel = gap[i]
        vf = v_f[i]
        ok = True
        for j in range(i, len(t) - 1):
            vf_next = max(vf + a_brake * dt, 0.0)
            x_rel += 0.5 * (v_l[j] + v_l[j + 1]) * dt - 0.5 * (vf + vf_next) * dt
            vf = vf_next
            if x_rel <= 0:
                ok = False
                break
            if vf == 0.0 and v_l[j + 1] >= 0.0:
                break
        if ok:
            last_ok = t[i]
        else:
            break
    # NaN if the scenario is already past the no-return point at its first sample (t_nr < -T, unknown)
    return float(last_ok - t[-1]) if not np.isnan(last_ok) else np.nan


def min_accel(t: np.ndarray, v: np.ndarray) -> float:
    """Minimum acceleration (harshest braking) along a speed profile [m/s^2]."""
    a = np.gradient(np.asarray(v, float), np.asarray(t, float))
    return float(np.min(a))
