"""
Response models: when does the follower start braking, given the pre-response kinematics
and a glance schedule. Both return the brake-onset time (first deceleration) or NaN.

ActiveInferenceResponse (tier 1) — the verified half of the active inference driver:
    eps(t) = residual information of the pragmatic value, evaluated pointwise on the seed
    kinematics with the code-form preference function (src/aidriver/preferences.py);
    E(t) = sum lambda * w(t) * eps(t) * dt, decision at E >= threshold, brake onset after the
    pedal delay. w(t) is the evidence gate: 1 with eyes on road, `glance_evidence_weight`
    with eyes off (0 = the CBM's "no accumulation while looking away").
    `ai_onset_method = "level"` uses the OSF-calibrated level set instead (onset at the first
    eyes-on instant with eps >= level).
    What tier 1 does not have: the closed-loop planner, so the imagined-future spread that
    lets the full model's accumulator drift before an event is absent, and the execution is
    the CBM's ramp (see simulate.execute_braking).

CBMResponse — Bärgman et al. (2024) §2.2.1:
    anchor at the first instant with tau^-1 >= 0.2 s^-1 on the pre-response path; brake onset
    = max(anchor, eyes back on road) + fixed delay (0.5 s).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from aidriver.preferences import PreferenceParams
from aidriver.bicycle import BicycleParams
from comfortzone.calibrate import deficit_along_trajectory
from quadris.load import VEHICLE_LENGTH
from .config import CausationConfig
from .glances import GlanceSchedule
from .simulate import PreResponseKinematics


class ResponseModel(Protocol):
    name: str
    def prepare(self, pre: PreResponseKinematics, cfg: CausationConfig) -> None: ...
    def onset(self, pre: PreResponseKinematics, schedule: GlanceSchedule, cfg: CausationConfig) -> float: ...
    def describe(self) -> dict: ...


def predicted_collision_deficit(t: np.ndarray, gap: np.ndarray, v_f: np.ndarray, v_l: np.ndarray,
                                horizon_s: float = 6.0, dt_h: float = 0.2, g_c: float = -10000.0,
                                floor: float = 0.2, ref_speed: float = 10.0,
                                length_margin: float = 0.0) -> np.ndarray:
    """
    The prediction channel of the active inference driver, reduced to its mean: from every
    instant, roll both vehicles forward with their current accelerations held constant (speeds
    floored at zero) over the planning horizon (H = 30 steps of 0.2 s), find the first
    predicted impact, and charge the collision cost g_C * severity for that step and every
    later step of the horizon (the running minimum of SI Eq. 47). Returned as a positive
    deficit in log units, to be added to the pointwise field. The authors' model does this
    with 75 noisy particles; this is the zero-noise version.
    """
    n = len(t); dt = float(np.median(np.diff(t)))
    a_f = np.gradient(v_f, dt); a_l = np.gradient(v_l, dt)
    K = int(round(horizon_s / dt_h))
    out = np.zeros(n)
    g = gap.copy(); vf = v_f.copy(); vl = v_l.copy()
    hit = np.zeros(n, dtype=bool); k_hit = np.full(n, K + 1); dv_hit = np.zeros(n)
    for k in range(1, K + 1):
        vf_n = np.maximum(vf + a_f * dt_h, 0.0); vl_n = np.maximum(vl + a_l * dt_h, 0.0)
        g = g + 0.5 * (vl + vl_n) * dt_h - 0.5 * (vf + vf_n) * dt_h
        vf, vl = vf_n, vl_n
        new = (~hit) & (g <= length_margin)
        k_hit[new] = k; dv_hit[new] = np.maximum(vf[new] - vl[new], 0.0); hit |= new
    sev = floor + (1 - floor) * dv_hit / ref_speed
    out[hit] = -g_c * sev[hit] * (K - k_hit[hit] + 1)
    return out


def anchor_time(pre: PreResponseKinematics, cfg: CausationConfig) -> float:
    """Time at which tau^-1 first reaches the anchor value on the pre-response path."""
    return pre.first_time(pre.tau_inv >= cfg.cbm_anchor_tau_inv)


@dataclass
class ActiveInferenceResponse:
    name: str = "active_inference_tier1"
    a_other_min: float = -6.0        # as in the OSF calibration (PreferenceParams default)
    eps: np.ndarray = None

    def prepare(self, pre: PreResponseKinematics, cfg: CausationConfig) -> None:
        p = PreferenceParams(v_desired=float(pre.v_f[0]), a_other_min=self.a_other_min,
                             vehicle=BicycleParams(dt=cfg.dt))
        n = len(pre.t)
        ego = np.column_stack([pre.x_f, np.zeros(n), np.zeros(n), np.zeros(n), pre.v_f])
        other = np.column_stack([pre.x_l + VEHICLE_LENGTH, np.zeros(n), np.zeros(n), np.zeros(n), pre.v_l])
        self.eps = deficit_along_trajectory(ego, other, p, actions=np.zeros((n, 2)))
        if cfg.ai_prediction == "constant_accel":
            self.eps = self.eps + predicted_collision_deficit(pre.t, pre.gap, pre.v_f, pre.v_l,
                                                              horizon_s=cfg.ai_horizon_s)
        # after the no-response impact the field is meaningless; freeze it there
        if np.isfinite(pre.t_crash_noresponse):
            self.eps[pre.t > pre.t_crash_noresponse] = np.nan

    def onset(self, pre: PreResponseKinematics, schedule: GlanceSchedule, cfg: CausationConfig) -> float:
        w = schedule.evidence_weight(pre.t, cfg.glance_evidence_weight)
        eps = np.nan_to_num(self.eps, nan=0.0) * w
        if cfg.ai_onset_method == "level":
            hit = eps >= cfg.ai_level
            t_dec = pre.first_time(hit)
        else:
            E = np.cumsum(cfg.ai_lambda * eps * cfg.dt)
            t_dec = pre.first_time(E >= cfg.ai_threshold)
        if not np.isfinite(t_dec):
            return np.nan
        t_on = t_dec + cfg.ai_pedal_delay
        # cannot start braking before the eyes are back (foot transfer can overlap the glance end)
        return float(t_on)

    def describe(self) -> dict:
        return dict(model=self.name, a_other_min=self.a_other_min,
                    field="code-form preference function, pointwise on seed kinematics, plus the "
                          "zero-noise constant-acceleration prediction channel (cfg.ai_prediction)")


@dataclass
class CBMResponse:
    name: str = "cbm"

    def prepare(self, pre: PreResponseKinematics, cfg: CausationConfig) -> None:
        self.t_anchor = anchor_time(pre, cfg)

    def onset(self, pre: PreResponseKinematics, schedule: GlanceSchedule, cfg: CausationConfig) -> float:
        if not np.isfinite(self.t_anchor):
            return np.nan
        t_back = self.t_anchor
        for s, e in schedule.intervals:
            if s <= self.t_anchor < e:
                t_back = max(t_back, e)
        return float(t_back + cfg.cbm_delay)

    def describe(self) -> dict:
        return dict(model=self.name, anchor="tau_inv>=0.2", delay_s="cfg.cbm_delay")


def make_response(cfg: CausationConfig) -> ResponseModel:
    return {"active_inference": ActiveInferenceResponse, "cbm": CBMResponse}[cfg.response_model]()
