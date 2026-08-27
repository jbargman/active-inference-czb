"""Fitting dataset construction for the CZB study-1 analysis.

Joins the behavioral responses in `external/01_studies/` (Random fixed-clip binary +
ordered braking expectation; Button right-censored press times) to the model covariates
computed along each stimulus clip by `comfortzone.cutin`. The product is one tidy trial
table per design, with the covariates the fitting needs:

* `deficit_max` -- the running maximum of the comfort-zone deficit up to the trial's end
  time. A threshold (level) model predicts intervention iff this exceeds the driver's
  level c, so the fixed-clip binary is a probit/logit in this covariate.
* `a_req_max` -- the running maximum of the *magnitude* of the required avoidance
  deceleration. The same threshold logic on the allowed-deceleration axis: a driver
  intervenes when the situation demands more braking than they consider acceptable.
  Carried alongside `deficit_max` because the mild truck cut-ins have zero dread-field
  deficit while a_req grades smoothly there (docs/lane_entry_note.md section 5) --
  which of the two axes fits better is a question for the data, not a convention.

Conventions inherited from `docs/czb_study1_data_plan.md` and the dataset's own
DATA_DICTIONARY gotchas: time since manoeuvre onset is the only cross-design time axis;
`TTC_true`/`kin_TTC_s` are never compared across designs; the Acceleration column is
never used; overshoot trials are dropped (their responses are already NA).

Timepoint convention (fixed-clip): variant Ck ends at manoeuvre onset + 0.3 (k-1) s, so
C1 ends exactly at onset -- a genuine pre-event baseline, which is why its responses
measure bias rather than the boundary.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .cutin import CutInTrace, load_cutin_trace, cutin_predictors

REPO = Path(__file__).resolve().parents[2]
STUDY = REPO / "external/01_studies/01_Studies/01_Sequence_Random_ButtonPress"
KIN_RANDOM = STUDY / "Kinematics/Sequence_Random_Study"
KIN_BUTTON = STUDY / "Kinematics/Button_Press_Study"
JOINT = STUDY / "Random_Button_Joint.csv"

# The Random design's cut-in stimuli (the CF traces; the Button design's TTC2-8 clips
# live in KIN_BUTTON without the suffix). Verified to load and role-assign correctly.
RANDOM_CUTIN_TRACES = {
    "TTC4": KIN_RANDOM / "CutInCar_4TTC_CF_vehicle_states.csv",
    "TTC6": KIN_RANDOM / "CutInCar_6TTC_CF_vehicle_states.csv",
    "TTC8": KIN_RANDOM / "CutInCar_8TTC_CF_vehicle_states.csv",
}
BUTTON_CUTIN_TRACES = {
    f"TTC{k}": KIN_BUTTON / f"CutInCar_{k}TTC_vehicle_states.csv" for k in range(2, 9)
}
# Button cut-in clips start at trace second 5 (video_clip_name encodes e.g. "5-18")
BUTTON_CLIP_START_S = 5.0

TIMEPOINT_OFFSET_S = {f"C{k}": 0.3 * (k - 1) for k in range(1, 7)}


def stimulus_field(path: str | Path, is_truck: bool = False) -> pd.DataFrame:
    """Model covariates along one stimulus clip, with running maxima.

    Columns added to `cutin_predictors`: `t_since_onset`, `deficit_max`, `a_req_max`
    (magnitude of required deceleration, clipped to finite by the trace's own support).
    """
    tr = load_cutin_trace(path, is_truck=is_truck)
    df = cutin_predictors(tr)
    df["t_since_onset"] = df.t - df.t.iloc[tr.onset_idx]
    df["deficit_max"] = np.maximum.accumulate(df.deficit.to_numpy())
    # a_req is computed from the longitudinal state alone, so before lane entry it
    # describes a counterfactual with an adjacent-lane vehicle; gate it by the lane-entry
    # weight so the running max only counts frames where the conflict geometry
    # meaningfully applies. (A refinement would use the deficit family over a grid of
    # allowed decelerations instead -- docs/czb_fitting_plan.md.)
    a_req_mag = np.abs(np.clip(df.a_req.to_numpy(), -50.0, 0.0))
    a_req_mag = np.where(df.p_lane.to_numpy() >= 0.5, a_req_mag, 0.0)
    df["a_req_max"] = np.maximum.accumulate(a_req_mag)
    df.attrs["onset_t"] = float(df.t.iloc[tr.onset_idx])
    df.attrs["name"] = tr.name
    return df


def _at_time(field: pd.DataFrame, t_since_onset: float, col: str) -> float:
    """Value of a running-max column at a time since onset (last frame at or before)."""
    idx = np.searchsorted(field.t_since_onset.to_numpy(), t_since_onset, side="right") - 1
    idx = int(np.clip(idx, 0, len(field) - 1))
    return float(field[col].iloc[idx])


def load_joint() -> pd.DataFrame:
    df = pd.read_csv(JOINT, low_memory=False)
    return df[df.get("timing_flag", pd.Series(index=df.index, dtype=object)) != "overshoot"]


def random_cutin_trials() -> pd.DataFrame:
    """One row per Random fixed-clip cut-in trial, with model covariates at clip end.

    Columns: participant, criticality, timepoint, t_end (s since onset), intervene,
    braking_expectation (ordered 0/1/2), ps (0-10), replay, deficit_max, a_req_max.
    """
    j = load_joint()
    r = j[(j.design == "Random") & (j.scenario == "cutin_car")].copy()
    fields = {c: stimulus_field(p) for c, p in RANDOM_CUTIN_TRACES.items()}

    r["t_end"] = r.timepoint.map(TIMEPOINT_OFFSET_S)
    r["deficit_max"] = [
        _at_time(fields[c], t, "deficit_max") for c, t in zip(r.criticality_label, r.t_end)]
    r["a_req_max"] = [
        _at_time(fields[c], t, "a_req_max") for c, t in zip(r.criticality_label, r.t_end)]
    out = pd.DataFrame({
        "participant": r.Exp_Subject_Id,
        "criticality": r.criticality_label,
        "timepoint": r.timepoint,
        "t_end": r.t_end,
        "intervene": r.intervene,
        "braking_expectation": r.followup_code,
        "ps": r.PS,
        "replay": r.Replay,
        "deficit_max": r.deficit_max,
        "a_req_max": r.a_req_max,
    }).reset_index(drop=True)
    return out


def button_cutin_trials() -> pd.DataFrame:
    """One row per Button cut-in trial: right-censored press time since manoeuvre onset,
    with the model covariates at the press (or at clip end for censored trials).

    `press_since_onset` is NaN for censored trials; `t_obs` is the observation end
    (press time, or clip end for censored) on the same time-since-onset axis.
    """
    j = load_joint()
    b = j[(j.design == "Button") & (j.scenario == "cutin_car")].copy()
    fields = {c: stimulus_field(p) for c, p in BUTTON_CUTIN_TRACES.items()
              if c in set(b.criticality_label)}

    onset_video_s = {c: f.attrs["onset_t"] - BUTTON_CLIP_START_S for c, f in fields.items()}
    b["press_since_onset"] = [
        (p - onset_video_s[c]) if np.isfinite(p) else np.nan
        for c, p in zip(b.criticality_label, b.press_time_s)]
    b["t_obs"] = [
        ps if np.isfinite(ps) else (dur - onset_video_s[c] if np.isfinite(dur) else np.nan)
        for c, ps, dur in zip(b.criticality_label, b.press_since_onset, b.clip_duration_s)]
    b["deficit_at_obs"] = [
        _at_time(fields[c], t, "deficit_max") if np.isfinite(t) else np.nan
        for c, t in zip(b.criticality_label, b.t_obs)]
    b["a_req_at_obs"] = [
        _at_time(fields[c], t, "a_req_max") if np.isfinite(t) else np.nan
        for c, t in zip(b.criticality_label, b.t_obs)]
    out = pd.DataFrame({
        "participant": b.Exp_Subject_Id,
        "criticality": b.criticality_label,
        "censored": b.censored,
        "press_since_onset": b.press_since_onset,
        "t_obs": b.t_obs,
        "own_braking": b.followup_code,
        "deficit_at_obs": b.deficit_at_obs,
        "a_req_at_obs": b.a_req_at_obs,
    }).reset_index(drop=True)
    return out
