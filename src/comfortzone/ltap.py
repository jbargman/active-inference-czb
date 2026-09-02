"""Left-turn-across-path (LTAP) stimulus traces for the two-axis comparison (card B.3.v2).

Written 2026-09-02 for `docs/ltap_construction_note.md` section 2 (the comparator-class
construction). The scenario: the ego approaches a T-junction, slows, and turns left across
the path of an oncoming vehicle that holds its heading at a constant 13.9 m/s (50 km/h) or
19.4 m/s (70 km/h). Nine design PET levels (0 to 4 s in 0.5 s steps) x two speeds = the 18
Random-design traces this module loads.

The module is deliberately NOT a field computation. Unlike the cut-in and the overtake
(`overtake.py`, which produces a `CutInTrace` so that both scenarios share
`cutin_predictors`), the released model has no term that applies to a turning ego -- the
construction note's section 3 documents that route and argues against building it -- so
what is loaded here is scene geometry: two observables per trace at one decision moment,
plus the cross-check quantities that let the numbers be reconciled with
`replication/czb/ltap_geometry.py`.

Why the cut-in and overtake loaders cannot be reused
----------------------------------------------------
`load_cutin_trace` assigns roles by lateral span and `load_overtake_trace` by vehicle
width. Both are wrong here. The lateral-span rule is *inverted*: the ego swings ~80 m
laterally through the turn while the oncoming holds its line, so it would pick the turning
ego as the "target". The width rule is uninformative: both bodies are ordinary cars (1.88 m
ego, 2.01 m oncoming). This is the third role rule in the project, and for the same reason
as the first two -- the instructed vehicle is the one performing the manoeuvre, and what
identifies it differs by scenario. Here the ego is the vehicle **whose heading changes**
(measured yaw span 359.6 deg, i.e. the turn carries the raw `Yaw` column across its own
wrap point) and the oncoming is the one with constant heading (yaw span below 1.2 deg on
all 18 traces).

ASSUMPTIONS, each stated so it can be overturned by one number
--------------------------------------------------------------
1. **The decision moment is t = 13.5 s of trace time** (`T_DECISION_S`), and every
   covariate is read there. This resolves query **B3.Q1** *by assumption*, per the ruling
   of 2026-09-02: the Random-design clip's end time is not recorded in the joint file
   (`video_clip_name` is Button-only), and the assumption is that the Random LTAP clip
   ends at the same moment as the Button clips, 13.5 s, which is 0.4-0.6 s before turn
   onset (measured onset 13.92-14.12 s). **One number from Jonas overturns this**: if the
   Random clips run to a different time, change `T_DECISION_S` and every covariate moves
   with it. What survives such a change is the ordering of the cells (the oncoming's
   distance and time-to-arrival are monotone in trace time within each trace and the design
   is balanced across speeds); what does not survive is any absolute distance, TTA or
   looming rate quoted from this module.
   The trace grid is ~0.1004 s, so the sample actually used is the first at or after
   13.5 s (13.515-13.516 s on these traces); `searchsorted` picks it, exactly as
   `ltap_geometry.py` picks the onset sample.
2. **The conflict band is +-1 m** (`BAND_HALF_M`) around the oncoming's median
   `Location_Y`, and the conflict point is the ego's mean `Location_X` while inside it.
   The design's own conflict-zone extent is not documented. A wider or narrower band shifts
   t_in, t_out and hence t_sep by nearly the same amount in every trace (construction note
   section 4), so the between-condition differences are unaffected but the absolute
   arrival-time separation is not.
3. **Turn onset is 1 deg of unwrapped heading change** from the trace's first frame
   (`ONSET_YAW_DEG`), the same rule `ltap_geometry.py` used.
4. **Front bumper = `Location_X` + `Length_m` / 2.** The oncoming travels in +X on every
   trace (it starts near X = -258 m and the conflict point is near X = 0), so its front
   bumper is the +X end. `Front_Bumper_S` (a road-frame arc length) is deliberately not
   used: it is not in the same frame as the ego's `Location_X`.
5. **The looming rate is referenced to the conflict point, not to the ego's eyepoint.**
   `theta_dot = W_onc * v_onc / (D^2 + W_onc^2 / 4)` is the exact derivative of
   theta = 2 atan(W / (2 D)) with dD/dt = -v_onc, the same form the cut-in's looming card
   (`replication/czb/cutin2_looming.py`) uses, with the range to the conflict point in
   place of the gap. It is what card B.3.v2 registers. It is NOT the optical expansion the
   driver sees, because at t_dec the ego is still short of the conflict point: the true
   ego-to-oncoming range is 55-151 m against D = 41-138 m, and the range closes at
   v_onc plus the ego's own approach speed. `theta_dot_ego`, computed from that range and
   its central difference, is carried alongside as a diagnostic; on this design the two are
   monotonically related, so they cannot be told apart by an ordering argument, only by a
   fit.
6. **No teardown trimming.** `ltap_geometry.py` used the raw per-vehicle groups and its
   numbers are the note's; this module reproduces them, so it does not trim either
   (`geometry_crosscheck` is the assertion that it does).

What is measured per trace (`LtapTrace`)
----------------------------------------
Cross-check quantities, identical in definition to `ltap_geometry.py`: `t_onset`, `t_in`,
`t_out`, `x_conf`, `t_onc_arrival`, `dist_at_onset`, `tta_at_onset`.
The construction note's two observables, at `t_dec`:
  * `d_onc` (D)      -- the oncoming's front-bumper distance to the conflict point [m];
  * `t_sep`          -- the arrival-time separation, (oncoming arrival) - (ego exit from
                        the band) [s]. Because the ego's script is identical in all 18
                        traces, this is the design PET plus a near-constant offset
                        (0.70-1.21 s, mean 0.96 s); it is the note's *time* axis and is a
                        property of the trace rather than of the decision moment.
Plus `v_onc`, `tta = d_onc / v_onc`, `theta_dot`, and the diagnostics named above.

Criticality orientation (data dictionary gotcha 2: for LTAP smaller = more critical) is
-log D and -log t_sep, and +log theta_dot; the two-axis comparison is
`replication/czb/ltap_two_axis.py`.

Run nothing here; this is a loader. See `docs/ltap_construction_note.md`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
STUDY = REPO / "external/01_studies/01_Studies/01_Sequence_Random_ButtonPress"
KIN_RANDOM = STUDY / "Kinematics/Sequence_Random_Study"
JOINT = STUDY / "Random_Button_Joint.csv"
#: `replication/czb/ltap_geometry.py`'s tracked output, for `geometry_crosscheck`.
GEOMETRY_CSV = REPO / "replication/czb/out/ltap_geometry.csv"

#: The decision moment: assumption B3.Q1 (see the module docstring). Seconds of trace time.
T_DECISION_S = 13.5
#: Half-width of the conflict band around the oncoming's lateral position [m].
BAND_HALF_M = 1.0
#: Unwrapped heading change marking turn onset [deg].
ONSET_YAW_DEG = 1.0
#: The design grid.
DESIGN_PET_S = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
DESIGN_SPEED_KPH = (50, 70)
#: Nominal oncoming speeds, from the design (measured: 13.878 and 19.436 m/s).
NOMINAL_ONC_SPEED_MPS = {50: 13.9, 70: 19.4}

NAME_RE = re.compile(r"IntersectionLeftTurnPET([\d.]+)(-70kph)?")


def trace_name(pet: float, speed_kph: int) -> str:
    """The stimulus name for one design cell, exactly as the files are named."""
    return f"IntersectionLeftTurnPET{pet:g}" + ("-70kph" if speed_kph == 70 else "")


#: The 18 Random-design LTAP stimuli, keyed by (design PET [s], oncoming speed [km/h]).
RANDOM_LTAP_TRACES = {
    (pet, spd): KIN_RANDOM / f"{trace_name(pet, spd)}_vehicle_states.csv"
    for spd in DESIGN_SPEED_KPH for pet in DESIGN_PET_S
}


@dataclass
class LtapTrace:
    """One LTAP stimulus, measured. Times are trace time [s]; see the module docstring."""

    name: str
    pet_design: float
    speed_kph: int
    # roles
    ego_id: int
    onc_id: int
    yaw_span_ego_deg: float
    yaw_span_onc_deg: float
    dt: float
    # the manoeuvre and the conflict point (cross-check quantities)
    t_onset: float
    v_ego_onset: float
    v_ego_approach: float
    t_in: float
    t_out: float
    x_conf: float
    y_band: float
    t_onc_arrival: float
    dist_at_onset: float
    tta_at_onset: float
    # the observables at the decision moment
    t_dec: float
    d_onc: float
    v_onc: float
    tta: float
    t_sep: float
    theta_dot: float
    w_onc: float
    # diagnostics for assumption 5
    range_ego_onc: float
    range_rate: float
    theta_dot_ego: float
    v_ego_dec: float

    @property
    def pet_measured(self) -> float:
        """`ltap_geometry.py`'s name for the same quantity as `t_sep`."""
        return self.t_sep


def looming_rate(width_m: float, closing_mps: float, range_m: float) -> float:
    """d/dt of theta = 2 atan(W / (2 r)) at fixed closing speed: W v / (r^2 + W^2/4).

    The exact derivative, not the small-angle form; identical in definition to the cut-in's
    looming card so the two scenarios' fourth model is the same quantity.
    """
    return float(width_m * closing_mps / (range_m ** 2 + width_m ** 2 / 4.0))


def load_ltap_trace(path: str | Path, t_dec: float = T_DECISION_S) -> LtapTrace:
    """Read one LTAP stimulus, assign roles by yaw span, and measure the observables.

    `t_dec` is the decision moment (assumption B3.Q1, module docstring): the covariates are
    read at the first sample at or after it. Everything else is a property of the whole
    trace.
    """
    path = Path(path)
    m = NAME_RE.match(path.name.replace("_vehicle_states.csv", ""))
    if m is None:
        raise ValueError(f"{path.name}: not an LTAP stimulus name")
    pet, spd = float(m.group(1)), (70 if m.group(2) else 50)

    raw = pd.read_csv(path)
    parts = {int(v): g.sort_values("Elapsed_Time_s").reset_index(drop=True)
             for v, g in raw.groupby("Vehicle_ID")}
    if len(parts) != 2:
        raise ValueError(f"{path.name}: expected two vehicles, found {len(parts)}")

    # Roles by yaw span: the ego turns, the oncoming holds its heading. Deliberately NOT by
    # lateral span (which is inverted here) nor by width (both bodies are cars).
    span = {v: float(g.Yaw.max() - g.Yaw.min()) for v, g in parts.items()}
    ego_id = max(span, key=span.get)
    onc_id = [v for v in parts if v != ego_id][0]
    e, o = parts[ego_id], parts[onc_id]

    t = e.Elapsed_Time_s.to_numpy(float)
    dt = float(np.median(np.diff(t)))

    # Turn onset: 1 deg of unwrapped heading change from the first frame.
    yaw = np.unwrap(np.deg2rad(e.Yaw.to_numpy(float)))
    onset = int(np.argmax(np.abs(yaw - yaw[0]) > np.deg2rad(ONSET_YAW_DEG)))
    t_onset = float(t[onset])

    # The conflict band: +-1 m around the oncoming's lateral position. The ego's entry and
    # exit are the first and last frames inside it; the conflict point is its mean
    # longitudinal position while inside.
    y_band = float(o.Location_Y.median())
    ey, ex = e.Location_Y.to_numpy(float), e.Location_X.to_numpy(float)
    inband = (ey > y_band - BAND_HALF_M) & (ey < y_band + BAND_HALF_M)
    if not inband.any():
        raise ValueError(f"{path.name}: the ego never enters the conflict band")
    i_in = int(np.argmax(inband))
    i_out = int(len(inband) - 1 - np.argmax(inband[::-1]))
    t_in, t_out = float(t[i_in]), float(t[i_out])
    x_conf = float(ex[i_in:i_out + 1].mean())

    ot = o.Elapsed_Time_s.to_numpy(float)
    ox, oy = o.Location_X.to_numpy(float), o.Location_Y.to_numpy(float)
    ov = o.Speed_mps.to_numpy(float)
    half = float(o.Length_m.iloc[0]) / 2.0
    w_onc = float(o.Width_m.iloc[0])

    # The oncoming's arrival: the first frame at which its front bumper reaches x_conf.
    reach = ox + half >= x_conf
    t_arr = float(ot[int(np.argmax(reach))]) if reach.any() else float("nan")

    pre = ot < t_onset
    v_pre = float(np.median(ov[pre])) if pre.any() else float("nan")
    dist_at_onset = float(x_conf - (ox[int(np.searchsorted(ot, t_onset))] + half))

    # --- the decision moment -------------------------------------------------------
    i_dec = int(np.searchsorted(ot, t_dec))
    if i_dec >= len(ot):
        raise ValueError(f"{path.name}: t_dec {t_dec} is past the end of the trace")
    d_onc = float(x_conf - (ox[i_dec] + half))
    v_onc = float(ov[i_dec])
    rng = float(np.hypot(ox[i_dec] - ex[i_dec], oy[i_dec] - ey[i_dec]))
    r_series = np.hypot(ox - ex, oy - ey)
    rate = float(-np.gradient(r_series, ot)[i_dec])   # positive = closing

    return LtapTrace(
        name=path.name.replace("_vehicle_states.csv", ""), pet_design=pet, speed_kph=spd,
        ego_id=ego_id, onc_id=onc_id,
        yaw_span_ego_deg=span[ego_id], yaw_span_onc_deg=span[onc_id], dt=dt,
        t_onset=t_onset, v_ego_onset=float(e.Speed_mps.iloc[onset]),
        v_ego_approach=(float(np.median(e.Speed_mps[t < t_onset - 3.0]))
                        if (t < t_onset - 3.0).any() else float("nan")),
        t_in=t_in, t_out=t_out, x_conf=x_conf, y_band=y_band, t_onc_arrival=t_arr,
        dist_at_onset=dist_at_onset, tta_at_onset=dist_at_onset / v_pre,
        t_dec=float(ot[i_dec]), d_onc=d_onc, v_onc=v_onc, tta=d_onc / v_onc,
        t_sep=t_arr - t_out, theta_dot=looming_rate(w_onc, v_onc, d_onc), w_onc=w_onc,
        range_ego_onc=rng, range_rate=rate,
        theta_dot_ego=looming_rate(w_onc, rate, rng),
        v_ego_dec=float(e.Speed_mps.to_numpy(float)[i_dec]),
    )


def ltap_traces(t_dec: float = T_DECISION_S) -> list[LtapTrace]:
    """All 18 Random-design LTAP stimuli, in (speed, PET) order."""
    out = []
    for (pet, spd), path in sorted(RANDOM_LTAP_TRACES.items(), key=lambda kv: kv[0][::-1]):
        if not path.exists():
            raise FileNotFoundError(path)
        out.append(load_ltap_trace(path, t_dec))
    return out


def random_ltap_responses() -> pd.DataFrame:
    """P(intervene) and n per (design PET, oncoming speed) cell of the Random design.

    Built exactly as `replication/czb/ltap_geometry.py` builds it: the joint file's
    `criticality_label` is the truth on the Random side (the data dictionary's gotcha 3
    concerns the Button side, where nine labels map to five videos).
    """
    j = pd.read_csv(JOINT, low_memory=False)
    r = j[(j.scenario == "ltap") & (j.design == "Random")].copy()
    r["pet"] = r.criticality_label.str.replace("PET", "").astype(float)
    return (r.groupby(["pet", "ltap_speed"]).intervene.agg(["mean", "count"]).reset_index()
            .rename(columns={"ltap_speed": "speed_kph", "mean": "p", "count": "n"}))


def ltap_cells(t_dec: float = T_DECISION_S, with_responses: bool = True) -> pd.DataFrame:
    """The 18-cell table: geometry at the decision moment, joined to the responses."""
    rows = []
    for tr in ltap_traces(t_dec):
        rows.append({
            "trace": tr.name, "pet": tr.pet_design, "speed_kph": tr.speed_kph,
            "t_dec": tr.t_dec, "d_onc": tr.d_onc, "v_onc": tr.v_onc, "tta": tr.tta,
            "t_sep": tr.t_sep, "theta_dot": tr.theta_dot, "w_onc": tr.w_onc,
            "range_ego_onc": tr.range_ego_onc, "range_rate": tr.range_rate,
            "theta_dot_ego": tr.theta_dot_ego, "v_ego_dec": tr.v_ego_dec,
            "t_onset": tr.t_onset, "v_ego_onset": tr.v_ego_onset,
            "v_ego_approach": tr.v_ego_approach, "t_in": tr.t_in, "t_out": tr.t_out,
            "x_conf": tr.x_conf, "t_onc_arrival": tr.t_onc_arrival,
            "dist_at_onset": tr.dist_at_onset, "tta_at_onset": tr.tta_at_onset,
            "yaw_span_ego_deg": tr.yaw_span_ego_deg,
            "yaw_span_onc_deg": tr.yaw_span_onc_deg,
        })
    cells = pd.DataFrame(rows)
    if with_responses:
        cells = cells.merge(random_ltap_responses(), on=["pet", "speed_kph"], how="left")
        if cells.p.isna().any():
            raise RuntimeError("design cells without a Random-design response")
    return cells


#: The columns `ltap_geometry.py` also measures, mapped loader name -> geometry name.
CROSSCHECK_COLUMNS = {
    "t_onset": "t_onset", "t_in": "t_in", "t_out": "t_out", "x_conf": "x_conf",
    "t_onc_arrival": "t_onc_arrival", "t_sep": "pet_measured",
    "dist_at_onset": "dist_at_onset", "tta_at_onset": "tta_at_onset",
    "v_ego_onset": "v_ego_onset", "v_ego_approach": "v_ego_approach",
}


def geometry_crosscheck(cells: pd.DataFrame | None = None) -> pd.DataFrame:
    """Max absolute difference, per column, against `out/ltap_geometry.csv`.

    The construction note's numbers come from `ltap_geometry.py`; this loader recomputes
    them by a separate code path and the two must agree. Returns one row per checked
    column with the max |difference| over the 18 traces.
    """
    if cells is None:
        cells = ltap_cells()
    ref = pd.read_csv(GEOMETRY_CSV)
    m = cells.merge(ref, on="trace", suffixes=("", "_ref"))
    if len(m) != len(ref):
        raise RuntimeError(f"trace names do not match: {len(m)} of {len(ref)}")
    rows = []
    for mine, theirs in CROSSCHECK_COLUMNS.items():
        col = theirs if theirs != mine else f"{mine}_ref"
        d = (m[mine].to_numpy(float) - m[col].to_numpy(float))
        rows.append({"quantity": mine, "geometry column": theirs,
                     "max abs difference": float(np.max(np.abs(d)))})
    return pd.DataFrame(rows)
