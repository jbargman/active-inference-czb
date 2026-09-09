"""
Card NDS.1 -- read the split-site data interface into the gated-looming pipeline's inputs.

The shared analysis path has until now read the video studies' own stimulus files
(`cutin.py`, `ltap.py`, `overtake.py`). Naturalistic data will arrive at Volvo Cars in the
shape of `transfer/interface_schema.yaml` instead, produced there by an adapter that never
leaves that site. This module is the one place that reads that shape, so that every
scenario's analysis can run at either site without any other change.

**It computes the same quantities, by the same definitions, as the video cards.** That is
the whole point: a level fitted on video and a level fitted on naturalistic data are only
comparable if the axis and the gate mean the same thing. Specifically

    gap    = (oth_x - ego_x) resolved to EDGE-TO-EDGE, exactly as `cutin_predictors`
             does with `x_tar - 0.5 * (tar_len + ego_len)`
    dv     = ego_v - oth_v, positive when closing
    theta_dot = looming_rate(W, dv, gap) = W*dv / (gap^2 + W^2/4)   [ltap.looming_rate]
             -- the EXACT derivative of theta = 2 atan(W / 2r), identical in definition to
             cards EL.1b (`out/cutin2_looming.md`) and B.3.v2
    l0     = |oth_y - ego_y| - (ego_wid + oth_wid)/2, the edge-to-edge lateral clearance
             of card G.1 (`out/cutin2_gate.md`)
    ldot   = (l0(t) - l0(t - LDOT_WINDOW_S)) / LDOT_WINDOW_S, a BACKWARD difference
    w_gate = Phi((m_lat - (l0 + ldot * T_ENC)) / s_l)               [card G.1]

**Parameter values and their motivation** (skill rule: no value without a stated reason):

* `LDOT_WINDOW_S = 0.3` -- card G.1 measured the clearance closing rate over 0.3 s because
  that is the video stimuli's sample spacing. Naturalistic data is sampled faster, so the
  window is a free choice here; it is fixed at 0.3 s so that `ldot` is *the same quantity*
  as the one the fitted `m_lat = 0.149 m`, `s_l = 0.990 m` were fitted against. Changing it
  would silently re-scale the gate. Not tuned.
* `T_ENC = 3.0` -- the gate's look-ahead, fixed (not identifiable from the video design) in
  card G.1 and imported unchanged.
* `GATE_M_LAT = 0.149`, `GATE_S_L = 0.990` -- the values card G.1 fitted on the second
  cut-in study (`out/cutin2_gate.md` section 3). They are defaults for *carrying the video
  gate over* to naturalistic data; refitting on naturalistic data is a later card, and the
  transfer of these values unchanged is exactly the test worth running.

**What this module does NOT do.** It does not fit anything, and it does not decide the
estimator. The video paradigm's unit is a design cell -- a frozen clip and the share of
raters who said they would intervene -- and naturalistic data has no such unit: one event
has one driver and one realized brake onset. The observation this module extracts is
therefore the axis value AT the brake onset, with events that carry no brake response
returned as right-censored (the driver did not cross their level during the event). That
is a design decision, recorded as query NDS.Q1, not a settled estimator.

Run the smoke test: python replication/czb/nds1_interface_smoke.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from .ltap import looming_rate

# --- parameters, each motivated in the module docstring -------------------------------
LDOT_WINDOW_S = 0.3     # card G.1's clearance-rate window, kept so ldot is the same quantity
T_ENC = 3.0             # card G.1's fixed gate look-ahead
GATE_M_LAT = 0.149      # card G.1 fitted, out/cutin2_gate.md section 3
GATE_S_L = 0.990        # card G.1 fitted, out/cutin2_gate.md section 3

REQUIRED_TS_COLUMNS = ["t", "ego_x", "ego_y", "ego_psi", "ego_v", "ego_ax",
                       "oth_x", "oth_y", "oth_psi", "oth_v", "oth_ax", "oth_class", "valid"]
REQUIRED_META_COLUMNS = ["event_id", "dataset", "scenario", "driver_id", "lane_width",
                         "ego_len", "ego_wid", "oth_len", "oth_wid", "geometry_default",
                         "ref_point", "t_conflict_onset", "t_brake_onset"]


class InterfaceGapError(ValueError):
    """The longitudinal gap cannot be resolved from what the interface carries.

    Raised for `ref_point = rear_axle`: converting a rear-axle position to a bumper
    position needs the front overhang (rear axle to front bumper), and the interface
    carries only the total length. See NDS.Q2.
    """


@dataclass
class InterfaceEvent:
    """One event, exactly as the interface delivers it, plus its metadata row."""
    event_id: str
    driver_id: str
    scenario: str
    dataset: str
    ts: pd.DataFrame                      # the time-series columns, verbatim
    meta: dict = field(default_factory=dict)

    @property
    def t(self) -> np.ndarray:
        return self.ts["t"].to_numpy(float)

    @property
    def dt(self) -> float:
        return float(np.median(np.diff(self.t)))

    @property
    def has_brake_response(self) -> bool:
        v = self.meta.get("t_brake_onset")
        return v is not None and np.isfinite(v)


# --------------------------------------------------------------------------------------
# 1. Reading
# --------------------------------------------------------------------------------------

def load_interface_dir(path: str | Path) -> tuple[pd.DataFrame, dict[str, InterfaceEvent]]:
    """Read an interface directory into its metadata table and its events.

    Reads only; it never writes, and it never prints a data row -- the same discipline
    `transfer/validate_interface.py` follows, because this code runs at the data site.
    """
    path = Path(path)
    meta_path = path / "events.csv"
    if not meta_path.exists():
        raise FileNotFoundError(f"{meta_path} not found: an interface directory needs events.csv")
    meta = pd.read_csv(meta_path)
    missing = [c for c in REQUIRED_META_COLUMNS if c not in meta.columns]
    if missing:
        raise ValueError(f"events.csv lacks required column(s) {missing}")

    events: dict[str, InterfaceEvent] = {}
    for _, row in meta.iterrows():
        eid = str(row["event_id"])
        ts_path = path / f"{eid}.csv"
        if not ts_path.exists():
            raise FileNotFoundError(f"{eid}: time-series file {ts_path.name} not found")
        ts = pd.read_csv(ts_path)
        miss = [c for c in REQUIRED_TS_COLUMNS if c not in ts.columns]
        if miss:
            raise ValueError(f"{eid}: time series lacks required column(s) {miss}")
        events[eid] = InterfaceEvent(
            event_id=eid, driver_id=str(row["driver_id"]), scenario=str(row["scenario"]),
            dataset=str(row["dataset"]), ts=ts, meta=row.to_dict())
    return meta, events


# --------------------------------------------------------------------------------------
# 2. The observables, by the video cards' definitions
# --------------------------------------------------------------------------------------

def longitudinal_gap(ev: InterfaceEvent) -> np.ndarray:
    """Edge-to-edge longitudinal gap [m], resolved for the event's `ref_point`.

    `cog` -- positions are vehicle centres, so the gap is the centre separation less half
    of each length, which is what `cutin_predictors` computes.
    `front_bumper` -- ego's front bumper to the partner's rear bumper is the raw separation
    less the partner's length (the ego's own length is already excluded by its reference).
    `rear_axle` -- NOT resolvable: see `InterfaceGapError` and NDS.Q2.
    """
    ref = str(ev.meta.get("ref_point", "")).strip()
    dx = ev.ts["oth_x"].to_numpy(float) - ev.ts["ego_x"].to_numpy(float)
    ego_len = float(ev.meta["ego_len"])
    oth_len = float(ev.meta["oth_len"])
    if ref == "cog":
        return dx - 0.5 * (ego_len + oth_len)
    if ref == "front_bumper":
        return dx - oth_len
    raise InterfaceGapError(
        f"{ev.event_id}: ref_point={ref!r} cannot be resolved to an edge-to-edge gap. "
        f"'rear_axle' needs the front overhang (rear axle to front bumper), which the "
        f"interface does not carry; only total length is present. See NDS.Q2.")


def lateral_clearance(ev: InterfaceEvent) -> np.ndarray:
    """Edge-to-edge lateral clearance [m], card G.1's `l0`, positive when separated."""
    dy = np.abs(ev.ts["oth_y"].to_numpy(float) - ev.ts["ego_y"].to_numpy(float))
    return dy - 0.5 * (float(ev.meta["ego_wid"]) + float(ev.meta["oth_wid"]))


def gate_weight(l0: np.ndarray, ldot: np.ndarray,
                m_lat: float = GATE_M_LAT, s_l: float = GATE_S_L,
                t_enc: float = T_ENC) -> np.ndarray:
    """Card G.1's anticipatory gate: Phi((m_lat - (l0 + ldot*t_enc)) / s_l)."""
    return norm.cdf((m_lat - (l0 + ldot * t_enc)) / s_l)


def interface_predictors(ev: InterfaceEvent, m_lat: float = GATE_M_LAT,
                         s_l: float = GATE_S_L) -> pd.DataFrame:
    """Per-sample predictors for one event: the axis, the gate and their inputs.

    Columns mirror `cutin_predictors` where the quantity is the same, so a reader moving
    between the video and naturalistic paths sees the same names.
    """
    t = ev.t
    gap = longitudinal_gap(ev)
    v_rel = ev.ts["ego_v"].to_numpy(float) - ev.ts["oth_v"].to_numpy(float)
    W = float(ev.meta["oth_wid"])

    # theta_dot is only defined while the partner is ahead and the gap is positive; a
    # closed or negative gap is a collision, not a looming rate.
    safe_gap = np.where(gap > 1e-3, gap, np.nan)
    theta_dot = np.array([looming_rate(W, float(dv), float(g)) if np.isfinite(g) else np.nan
                          for dv, g in zip(v_rel, safe_gap)])

    l0 = lateral_clearance(ev)
    ldot = _backward_rate(t, l0, LDOT_WINDOW_S)
    with np.errstate(divide="ignore", invalid="ignore"):
        ttc = np.where(v_rel > 1e-3, safe_gap / v_rel, np.inf)

    return pd.DataFrame({
        "t": t,
        "gap_m": gap,
        "v_rel": v_rel,
        "ttc_s": ttc,
        "theta_dot": theta_dot,
        "l0": l0,
        "ldot": ldot,
        "w_gate": gate_weight(l0, ldot, m_lat, s_l),
        "valid": ev.ts["valid"].to_numpy(float),
    })


def _backward_rate(t: np.ndarray, y: np.ndarray, window_s: float) -> np.ndarray:
    """(y(t) - y(t - window)) / window, by index lookup on a uniform grid.

    A backward difference, not a centred one: the gate must be computable from the past
    only, since it is meant to describe what the driver could know at that moment.
    """
    dt = float(np.median(np.diff(t))) if len(t) > 1 else np.nan
    if not np.isfinite(dt) or dt <= 0:
        return np.full_like(y, np.nan, dtype=float)
    k = max(1, int(round(window_s / dt)))
    out = np.full_like(y, np.nan, dtype=float)
    if len(y) > k:
        out[k:] = (y[k:] - y[:-k]) / (k * dt)
    return out


# --------------------------------------------------------------------------------------
# 3. One observation per event: the axis value where the driver acted
# --------------------------------------------------------------------------------------

def interface_observations(ev: InterfaceEvent, m_lat: float = GATE_M_LAT,
                           s_l: float = GATE_S_L) -> dict:
    """The per-event observation for a threshold model.

    With a brake response: the axis value at the onset sample -- the driver's realized
    crossing. Without one: right-censored at the largest axis value the event reached
    after conflict onset, since the driver saw that much and did not act.

    `theta_dot_max_pre` is the maximum over the window from conflict onset to the brake
    onset (or to the end of the event when censored), which is what a running-maximum
    estimator of the video kind would use.
    """
    pr = interface_predictors(ev, m_lat, s_l)
    t = pr["t"].to_numpy(float)
    t_conf = float(ev.meta.get("t_conflict_onset", np.nan))
    t_brake = float(ev.meta.get("t_brake_onset", np.nan))

    after_conflict = np.isfinite(t_conf) & (t >= t_conf) if np.isfinite(t_conf) else np.ones_like(t, bool)
    censored = not np.isfinite(t_brake)

    if censored:
        window = after_conflict
        idx = None
    else:
        idx = int(np.argmin(np.abs(t - t_brake)))
        window = after_conflict & (t <= t[idx])

    td = pr["theta_dot"].to_numpy(float)
    td_window = np.where(window, td, np.nan)
    with np.errstate(all="ignore"):
        td_max = float(np.nanmax(td_window)) if np.any(np.isfinite(td_window)) else np.nan

    row = {
        "event_id": ev.event_id, "driver_id": ev.driver_id, "scenario": ev.scenario,
        "dataset": ev.dataset,
        "censored": censored,
        "t_brake_onset": t_brake,
        "theta_dot_at_onset": np.nan if censored else float(td[idx]),
        "theta_dot_max_pre": td_max,
        "gap_at_onset": np.nan if censored else float(pr["gap_m"].to_numpy(float)[idx]),
        "v_rel_at_onset": np.nan if censored else float(pr["v_rel"].to_numpy(float)[idx]),
        "w_gate_at_onset": np.nan if censored else float(pr["w_gate"].to_numpy(float)[idx]),
        "valid_at_onset": np.nan if censored else float(pr["valid"].to_numpy(float)[idx]),
        "geometry_default": int(ev.meta.get("geometry_default", 0)),
        "quality_flag": ev.meta.get("quality_flag", ""),
    }
    return row


def interface_observation_table(events: dict[str, InterfaceEvent], **kw) -> pd.DataFrame:
    """`interface_observations` over a whole directory, one row per event."""
    return pd.DataFrame([interface_observations(ev, **kw) for ev in events.values()])
