"""Cut-in scenario support for the comfort-zone method.

This is the (a1) object of `docs/czb_study1_data_plan.md`: the *preference-function* side
of a cut-in scenario, which is all the comfort-zone method needs. It deliberately does not
build a closed-loop cut-in agent (that is (a2), expensive, and not required to locate a
boundary).

Scope and conventions, all deliberate:

* **Parameters are unchanged from the released scenarios.** Nothing here introduces a new
  fitted constant. Lane width, vehicle dimensions and every preference weight come from
  `PreferenceParams`; the one scenario-typed dial, the assumed steering variability of the
  other vehicle, takes the lateral-scenario value (see `CUTIN_W_SD_MODEL`). The intent is
  that any later disagreement with data is attributable to structure, not to tuning.
* **The acceleration column of the study traces is not used.** It is unsigned and its
  definition could not be established (`docs/czb_study1_data_plan.md` section 1.2), so
  longitudinal acceleration is obtained by differentiating speed. Predictors are built from
  positions, speeds, headings and their derivatives only.
* **The ego does not respond** in the stimulus clips, so the comfort-zone field along a clip
  is a fixed function of time: compute it once per stimulus and reuse it for every
  participant and repetition.

Nothing in this module is fitted to the button-press or clip-rating responses; it produces
the *predictor* series those responses will later be regressed against.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from aidriver.preferences import (PreferenceParams, log_preference_terms,
                                  pragmatic_deficit, required_deceleration)

# The one scenario-typed driver parameter (handbook ch. 04): assumed steering variability
# of the other vehicle. 0.0045 in rear-end, 0.4575 in both lateral scenarios. A cut-in
# target steers by definition, so it takes the lateral value.
CUTIN_W_SD_MODEL = 0.4575

# Study trace conventions, verified against the files.
TRACE_HZ = 10.0
LANE_WIDTH_STUDY = 3.5          # lane centres at y = -1.85 and -5.35 in the cut-in traces
TRUCK_DIMS = (16.5, 2.55)       # length, width [m] -- traces report Length_m = 0 for trucks


# --------------------------------------------------------------------------------------
# 1. Reading and conditioning a stimulus trace
# --------------------------------------------------------------------------------------

@dataclass
class CutInTrace:
    """One stimulus clip, conditioned and role-assigned."""
    t: np.ndarray               # trace time [s]
    v_ego: np.ndarray           # ego speed [m/s]
    a_ego: np.ndarray           # ego longitudinal acceleration [m/s^2], from d(speed)/dt
    y_ego: np.ndarray           # ego lateral position [m]
    x_tar: np.ndarray           # target longitudinal position, ego-relative [m], + is ahead
    y_tar: np.ndarray           # target lateral position, ego-relative [m]
    v_tar: np.ndarray
    a_tar: np.ndarray
    tar_len: float
    tar_wid: float
    onset_idx: int              # first index of the lane change
    complete_idx: int           # index at which the lane change completes
    name: str = ""

    @property
    def dt(self) -> float:
        return float(np.median(np.diff(self.t)))

    @property
    def progress(self) -> np.ndarray:
        """Manoeuvre progress in [0, 1]: 0 before onset, 1 once the change completes."""
        p = np.zeros_like(self.t)
        if self.complete_idx > self.onset_idx:
            span = self.complete_idx - self.onset_idx
            p[self.onset_idx:self.complete_idx] = np.arange(span) / span
        p[self.complete_idx:] = 1.0
        return p


def _trim_teardown(g: pd.DataFrame) -> pd.DataFrame:
    """Drop the simulator's first and last frames.

    At t = 0 every vehicle reports a near-zero speed before jumping to its true value, and
    the trailing frames collapse toward zero as the simulation is torn down. Both produce
    accelerations of 100-250 m/s^2 if left in. Trim to the contiguous run of frames whose
    speed is a plausible fraction of the vehicle's median.
    """
    g = g.sort_values("Elapsed_Time_s").reset_index(drop=True)
    s = g.Speed_mps.to_numpy()
    ok = s > 0.5 * np.median(s)
    if not ok.any():
        return g.iloc[0:0]
    i0 = int(np.argmax(ok))
    i1 = len(ok) - 1 - int(np.argmax(ok[::-1]))
    return g.iloc[i0:i1 + 1].reset_index(drop=True)


def load_cutin_trace(path: str | Path, is_truck: bool = False) -> CutInTrace:
    """Read one `*_vehicle_states.csv` cut-in stimulus and assign roles.

    Roles are assigned geometrically rather than by ID: the *target* is the vehicle whose
    lateral position changes most (it performs the lane change); the *ego* is the vehicle
    that stays in the destination lane and is behind the target. Any third vehicle present
    (the traces carry a lead in the adjacent lane) is ignored for now.
    """
    path = Path(path)
    raw = pd.read_csv(path)
    parts = {int(v): _trim_teardown(g) for v, g in raw.groupby("Vehicle_ID")}
    parts = {v: g for v, g in parts.items() if len(g) > 10}
    if len(parts) < 2:
        raise ValueError(f"{path.name}: fewer than two usable vehicles after trimming")

    def y_span(g):
        return float(g.Location_Y.max() - g.Location_Y.min())

    tar_id = max(parts, key=lambda v: y_span(parts[v]))
    # ego: of the remaining, the one ending in the same lane as the target ends in
    y_end_tar = float(parts[tar_id].Location_Y.iloc[-1])
    others = [v for v in parts if v != tar_id]
    ego_id = min(others, key=lambda v: abs(float(parts[v].Location_Y.median()) - y_end_tar))

    e, tg = parts[ego_id], parts[tar_id]
    n = min(len(e), len(tg))
    e, tg = e.iloc[:n], tg.iloc[:n]
    t = e.Elapsed_Time_s.to_numpy()

    v_ego = e.Speed_mps.to_numpy()
    v_tar = tg.Speed_mps.to_numpy()
    a_ego = np.gradient(v_ego, t)          # never the Acceleration_mps2 column: see module docstring
    a_tar = np.gradient(v_tar, t)

    # The cut-in traces run in -X (Location_X decreases), so the vehicle with the *lower*
    # X is ahead. Multiplying the raw offset by the sign of the ego's own displacement
    # makes x_tar positive when the target leads, whichever way the scenario is laid out.
    heading_sign = np.sign(np.median(np.diff(e.Location_X.to_numpy())))
    x_tar = heading_sign * (tg.Location_X.to_numpy() - e.Location_X.to_numpy())
    y_tar = tg.Location_Y.to_numpy() - e.Location_Y.to_numpy()

    y_t = tg.Location_Y.to_numpy()
    y0, y1 = y_t[0], y_t[-1]
    frac = (y_t - y0) / (y1 - y0) if abs(y1 - y0) > 1e-6 else np.zeros_like(y_t)
    onset = int(np.argmax(frac > 0.02))
    complete = int(np.argmax(frac > 0.98)) if (frac > 0.98).any() else len(frac) - 1

    length = float(tg.Length_m.iloc[0])
    width = float(tg.Width_m.iloc[0])
    if is_truck or length <= 0.01:         # truck bounding boxes are broken in the traces
        length, width = TRUCK_DIMS

    return CutInTrace(t=t, v_ego=v_ego, a_ego=a_ego, y_ego=e.Location_Y.to_numpy(),
                      x_tar=x_tar, y_tar=y_tar, v_tar=v_tar, a_tar=a_tar,
                      tar_len=length, tar_wid=width,
                      onset_idx=onset, complete_idx=complete, name=path.stem)


# --------------------------------------------------------------------------------------
# 2. The cut-in norm: what the driver expects the other vehicle to be doing
# --------------------------------------------------------------------------------------

def cutin_norm_weight(y_rel: np.ndarray, progress: np.ndarray, lane_width: float,
                      straddle_tolerance: float = 1.0,
                      w_offlane: float = 0.05) -> np.ndarray:
    """Normative plausibility of the target's lateral state during a cut-in.

    This is the cut-in analogue of `reward.py::get_weights` in the released scenarios, and
    it is the one genuinely new piece of scenario content (handbook ch. 04): none of the
    three released norms is time-dependent. A vehicle in the adjacent lane is normal; a
    vehicle straddling the boundary is *transiently* normal, because a lane change is a
    legal manoeuvre, but only for a plausible duration; a vehicle that has completed the
    change is normal again.

    `straddle_tolerance` is the fraction of the manoeuvre over which straddling stays fully
    normal before the weight decays. It is a structural choice, not a fitted parameter, and
    is set to 1.0 here so that no penalty is applied during a normally-paced lane change --
    the deliberately neutral starting point.

    Returns weights in (0, 1]; 1 means "entirely as expected".
    """
    y_rel = np.asarray(y_rel, float)
    progress = np.asarray(progress, float)
    in_lane = np.abs(y_rel) < 0.5 * lane_width
    adjacent = np.abs(np.abs(y_rel) - lane_width) < 0.5 * lane_width
    w = np.full(y_rel.shape, w_offlane, dtype=float)
    w[adjacent] = 1.0
    w[in_lane] = 1.0
    straddling = ~(in_lane | adjacent)
    excess = np.clip(progress - straddle_tolerance, 0.0, 1.0)
    w[straddling] = np.maximum(w_offlane, 1.0 - excess[straddling])
    return w


# --------------------------------------------------------------------------------------
# 3. The predictor series
# --------------------------------------------------------------------------------------

def cutin_obs(trace: CutInTrace, p: PreferenceParams) -> dict:
    """Observation dict along the clip, in the form `log_preference_terms` expects.

    Built from positions, speeds and headings only -- no acceleration column, per the
    module docstring.
    """
    return {
        "v": trace.v_ego,
        "a": trace.a_ego,
        "omega": np.zeros_like(trace.t),      # the stimulus ego does not steer
        "a_lat": np.zeros_like(trace.t),
        "y": np.full_like(trace.t, p.lane_centre),
        "dx": trace.x_tar,
        "dy": trace.y_tar,
        "v_other": trace.v_tar,
        "a_other": trace.a_tar,
    }


def cutin_deficit(trace: CutInTrace, p: PreferenceParams | None = None,
                  apply_norm: bool = True) -> np.ndarray:
    """The comfort-zone pressure along a cut-in clip.

    This is the scalar the boundary is a level set of: the pragmatic deficit of the
    preference function, optionally scaled by how normal the target's behavior is. A
    boundary crossing is the first time this exceeds a level `c`, and `c` is what gets
    fitted to the clip-rating and button-press responses.
    """
    p = p or PreferenceParams()
    d = pragmatic_deficit(cutin_obs(trace, p), p)
    if apply_norm:
        w = cutin_norm_weight(trace.y_tar, trace.progress, LANE_WIDTH_STUDY)
        d = d / np.clip(w, 1e-3, None)     # less normal target -> more pressure
    return np.asarray(d, float)


def cutin_predictors(trace: CutInTrace, p: PreferenceParams | None = None) -> pd.DataFrame:
    """Every candidate predictor for the boundary, as one tidy frame.

    Jonas's list: relative distances, speeds and angles plus derivatives, looming, the
    deceleration required to avoid a collision with some margin, and TTC.
    """
    p = p or PreferenceParams()
    obs = cutin_obs(trace, p)
    terms = log_preference_terms(obs, p)
    v_rel = trace.v_ego - trace.v_tar
    ego_len = p.vehicle.lf + p.vehicle.lr
    gap = trace.x_tar - 0.5 * (trace.tar_len + ego_len)
    with np.errstate(divide="ignore", invalid="ignore"):
        ttc = np.where(v_rel > 1e-3, gap / v_rel, np.inf)
        thw = np.where(trace.v_ego > 1e-3, gap / trace.v_ego, np.inf)
    out = pd.DataFrame({
        "t": trace.t,
        "progress": trace.progress,
        "gap_m": gap,
        "v_rel": v_rel,
        "ttc_s": ttc,
        "thw_s": thw,
        "y_rel": trace.y_tar,
        "dy_rel_dt": np.gradient(trace.y_tar, trace.t),
        "a_req": required_deceleration(obs, p),
        "norm_weight": cutin_norm_weight(trace.y_tar, trace.progress, LANE_WIDTH_STUDY),
        "deficit": cutin_deficit(trace, p),
    })
    for k, v in terms.items():
        out["pref_" + k] = v
    return out
