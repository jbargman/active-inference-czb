"""The single configuration object. Every switch and parameter of the causation layer."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field


@dataclass
class CausationConfig:
    # ---- response model -----------------------------------------------------------------
    response_model: str = "active_inference"     # "active_inference" | "cbm"
    # active inference (tier 1): accumulator on the comfort-zone field
    ai_lambda: float = 5.6e-6                    # drift rate on eps(t) [1/(log-unit s)]; calibrated on the OSF deposit (replication/causation/calibrate_accumulator.py): 69% of the closed-loop onsets within 0.2 s; per 0.2 s step this equals the paper's 10^-5.95
    ai_threshold: float = 1.0                    # re-plan threshold (fixed, as in the paper)
    ai_pedal_delay: float = 0.2                  # foot transfer after the decision [s] (paper: 0.2 s)
    ai_accumulator_init: str = "zero"            # "zero" (paper) | "stationary" (start at the benign level)
    ai_onset_method: str = "accumulator"         # "accumulator" | "level" (first crossing of a level on eps)
    ai_level: float = 66.9                       # level for the "level" method (OSF calibration, code-form field)
    ai_prediction: str = "constant_accel"        # "constant_accel" (mean prediction channel) | "none" (pointwise field only)
    ai_horizon_s: float = 6.0                    # planning horizon H = 30 x 0.2 s
    # CBM response (Bärgman et al. 2024 §2.2.1)
    cbm_delay: float = 0.5                       # eyes-back-on-road -> brake onset [s] (sensitivity: 0.8)
    cbm_anchor_tau_inv: float = 0.2              # [1/s]

    # ---- component 1: off-road glances --------------------------------------------------
    glances_on: bool = False
    glance_anchor: str = "tau_inv"               # "tau_inv" | "lead_onset" | "crash" | "process"
    glance_anchor_tau_inv: float = 0.2           # [1/s], Markkula et al. (2016)
    glance_evidence_weight: float = 0.0          # weight on surprise while eyes are off (0 = CBM; Svärd: partial)
    glance_obs_precision_factor: float = 1000.0  # observation sd multiplier while eyes are off (tier 2 only)
    glance_distribution: str = "standin"         # "standin" | path to a CSV with columns duration_s, probability
    glance_point_mass_on_road: float | None = None   # override the distribution's on-road share
    glance_process_on_road_mean: float | None = None  # for anchor="process": mean on-road dwell [s]; None = from the on-road share
    glance_sweep: str = "marginal"               # "marginal" (one run per overshoot, Bärgman App. C) | "joint" (duration x overshoot)

    # ---- component 2: too-close -----------------------------------------------------------
    # inherent in the seed's initial gap; nothing to switch. Kept here for the record.
    too_close_note: str = "inherent in seed initial state"

    # ---- component 3: low deceleration ---------------------------------------------------
    decel_cap_on: bool = True                    # tier 1 execution always needs a d_max; False = brake at a_max
    decel_distribution: str = "standin"          # "standin" | path to CSV with columns decel_ms2, probability
    a_max: float = 8.0                           # [m/s^2] vehicle limit
    jerk: float = -23.04                         # [m/s^3] pedal ramp (Bärgman 2024 §2.1.4)

    # ---- component 4: no response --------------------------------------------------------
    no_response_on: bool = False
    no_response_share: float = 0.10              # share of all generated crashes, mixed in post hoc (Bärgman 2024 §2.2.4)

    # ---- component 5: abnormal acceleration (Wu et al. 2025a) ----------------------------
    # distracted/non-responding followers who ignore the lead and hold a constant positive
    # acceleration; 9.2% of the QUADRIS-generation crashes, fitted mean 1.8 m/s^2. Mixed in
    # post hoc at the crash level like component 4. The paper samples an onset-time
    # distribution fitted to PCM data (parameters unpublished); "lead_onset" applies the
    # acceleration from the lead's braking onset, "start" from t = 0.
    abnormal_on: bool = False
    abnormal_share: float = 0.092
    abnormal_accel: float = 1.8                  # [m/s^2]
    abnormal_from: str = "lead_onset"            # "lead_onset" | "start"

    # ---- simulation -----------------------------------------------------------------------
    dt: float = 0.05                             # [s]
    t_extra: float = 10.0                        # simulate this long past the seed's original impact [s]
    pre_response_speed: str = "original"         # "original" | "constant" (CBM) | "no_brake" (original with braking removed from lead onset; recommended) | "no_brake_all"
    seed: int = 0

    def describe(self) -> dict:
        d = asdict(self)
        d["components_enabled"] = [k for k, v in {"glances": self.glances_on, "decel_cap": self.decel_cap_on,
                                                   "no_response": self.no_response_on,
                                                   "abnormal_accel": self.abnormal_on}.items() if v]
        return d

    @classmethod
    def condition(cls, name: str, **overrides) -> "CausationConfig":
        """Named conditions of docs/crash_causation_plan.md section 5."""
        base = dict(
            A=dict(response_model="active_inference"),
            B=dict(response_model="active_inference", glances_on=True, no_response_on=True),
            C=dict(response_model="cbm", glances_on=True, no_response_on=True),
            D=dict(response_model="active_inference", glances_on=True),
        )[name]
        return cls(**{**base, **overrides})
