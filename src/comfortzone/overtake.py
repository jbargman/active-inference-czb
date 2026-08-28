"""Cyclist-overtake stimulus traces for the CZB transfer test (card B.1, 2026-08-28).

The transfer test asks whether a boundary level fitted on one scenario predicts another
with nothing refitted. That only means something if the *field* is computed by the same
code in both scenarios, so this module deliberately produces a `CutInTrace` and hands it
to the existing `cutin_predictors` machinery rather than growing a parallel field. What
differs between the two scenarios is which vehicle does what, and that is entirely a
loading question -- the preference function sees only relative quantities.

Why the cut-in loader cannot be reused directly
-----------------------------------------------
`load_cutin_trace` assigns roles by lateral span: the vehicle that moves sideways is the
target, and the ego is the one that holds its lane. In an overtake that rule is not
merely uninformative, it is **inverted** -- here the *ego* is the vehicle that moves
sideways (it pulls out to pass) while the cyclist holds its line. Measured on the three
Random traces: ego lateral span 2.24 m against the cyclist's 0.16 m, so the cut-in rule
picks the car as "target" and the cyclist as "ego", which is the mis-assignment recorded
as review finding 1.5 in `handover_2026-08-27.md`. Roles here are therefore taken from
the *instructed* vehicle, per the card, and identified by vehicle dimensions: the
participant is the car driver, and the cyclist is unambiguous at 0.58 m wide against the
car's 1.88 m.

Two conventions worth recording, both established from the data rather than assumed
-----------------------------------------------------------------------------------
* **The lateral coordinate is `Location_Y`, not `Offset`.** Both columns are populated
  and both look plausible. `Location_Y` reproduces the study's own clearance labels
  exactly -- edge-to-edge gap at the passing moment comes out 0.506 / 1.004 / 1.501 m
  for the traces labelled 0.5 / 1 / 1.5 m -- while `Offset` (a within-lane coordinate
  that changes reference when the ego crosses the lane boundary) *inverts* the ordering,
  giving 0.94 / 0.45 / 0.05 m. A field built on `Offset` would run the criticality axis
  backwards and produce a confident, entirely spurious transfer failure. The label check
  is cheap and is asserted in `overtake_field_check.py` for exactly this reason.
* **Onset is the ego's lane-change start**, on the same absolute 0.03 m displacement
  threshold the cut-in loader uses. The alternative anchor (counting back from the
  passing moment) is ruled out by the responses: under the onset anchor the three
  conditions are physically identical at C1 (clearance spread 0.000 m), matching their
  nearly flat C1 intervention rates (0.221 / 0.203 / 0.169); a pass-anchored C1 would
  differ by 0.55 m and predict a strong ordering that the data does not show.

The timepoint grid then follows the cut-in convention unchanged, Ck = onset + 0.3 (k-1)
seconds, which the study's own dictionary gives for the cut-in and which the overtake
shares (`Clips_Overtake`, C1-C5). See `docs/overtake_construction_note.md`.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .cutin import CutInTrace, _trim_teardown

REPO = Path(__file__).resolve().parents[2]
STUDY = REPO / "external/01_studies/01_Studies/01_Sequence_Random_ButtonPress"
KIN_RANDOM = STUDY / "Kinematics/Sequence_Random_Study"

# Criticality = the cyclist's side clearance, and smaller is more critical (the data
# dictionary's gotcha 2: for cut-in, cyclist and LTAP smaller = more critical; only the
# truck scenario reverses).
RANDOM_OVERTAKE_TRACES = {
    "0.5m": KIN_RANDOM / "overtake_0.5m_vehicle_states.csv",
    "1m": KIN_RANDOM / "overtake_1m_vehicle_states.csv",
    "1.5m": KIN_RANDOM / "overtake_1.5m_vehicle_states.csv",
}

# Nominal edge-to-edge clearance at the pass, from the label, for the validation check.
NOMINAL_CLEARANCE_M = {"0.5m": 0.5, "1m": 1.0, "1.5m": 1.5}

ONSET_DY_M = 0.03          # absolute lateral displacement marking manoeuvre onset


def load_overtake_trace(path: str | Path) -> CutInTrace:
    """Read one cyclist-overtake stimulus and assign roles by instructed vehicle.

    Returns a `CutInTrace` so that every downstream field computation is shared with the
    cut-in scenario. `onset_idx` is the ego's lane-change start and `complete_idx` the
    moment of minimum longitudinal gap (the pass), which is where the manoeuvre's
    lateral geometry stops developing.
    """
    path = Path(path)
    raw = pd.read_csv(path)
    parts = {int(v): _trim_teardown(g) for v, g in raw.groupby("Vehicle_ID")}
    parts = {v: g for v, g in parts.items() if len(g) > 10}
    if len(parts) < 2:
        raise ValueError(f"{path.name}: fewer than two usable vehicles after trimming")

    # Roles by instructed vehicle: the participant drives the car, which is the widest
    # body in the trace; the cyclist is the narrowest. Deliberately NOT by lateral span.
    ego_id = max(parts, key=lambda v: float(parts[v].Width_m.iloc[0]))
    tar_id = min(parts, key=lambda v: float(parts[v].Width_m.iloc[0]))
    if ego_id == tar_id:
        raise ValueError(f"{path.name}: could not separate car from cyclist by width")

    e, tg = parts[ego_id], parts[tar_id]
    n = min(len(e), len(tg))
    e, tg = e.iloc[:n], tg.iloc[:n]
    t = e.Elapsed_Time_s.to_numpy()

    v_ego = e.Speed_mps.to_numpy()
    v_tar = tg.Speed_mps.to_numpy()
    a_ego = np.gradient(v_ego, t)          # never the Acceleration_mps2 column
    a_tar = np.gradient(v_tar, t)

    heading_sign = np.sign(np.median(np.diff(e.Location_X.to_numpy())))
    x_tar = heading_sign * (tg.Location_X.to_numpy() - e.Location_X.to_numpy())
    y_tar = tg.Location_Y.to_numpy() - e.Location_Y.to_numpy()

    # Onset: the EGO's lateral departure, same absolute threshold as the cut-in loader.
    y_e = e.Location_Y.to_numpy()
    moved = np.abs(y_e - y_e[0]) > ONSET_DY_M
    onset = int(np.argmax(moved)) if moved.any() else len(y_e) - 1
    # "Complete" = the pass: minimum longitudinal separation.
    complete = int(np.argmin(np.abs(x_tar)))

    return CutInTrace(t=t, v_ego=v_ego, a_ego=a_ego, y_ego=y_e,
                      x_tar=x_tar, y_tar=y_tar, v_tar=v_tar, a_tar=a_tar,
                      tar_len=float(tg.Length_m.iloc[0]),
                      tar_wid=float(tg.Width_m.iloc[0]),
                      onset_idx=onset, complete_idx=complete, name=path.stem)


def edge_clearance(trace: CutInTrace, ego_width: float = 1.88) -> np.ndarray:
    """Edge-to-edge lateral gap [m] between the two bodies, negative when they overlap."""
    return np.abs(trace.y_tar) - 0.5 * (ego_width + trace.tar_wid)


def clearance_at_pass(trace: CutInTrace, ego_width: float = 1.88) -> float:
    """The clearance the study's criticality label names, for validating the loader."""
    return float(edge_clearance(trace, ego_width)[trace.complete_idx])
