"""
Component C2 -- how a lane change is EXECUTED once begun: its onset, duration, peak lateral speed
and straddling time. These are the distributions the crossing norm of `docs/cutin_norm_proposal.md`
needs (its 0.5 and 3.0 m/s bounds were declared unverified there) and the execution part of the
lane-change futures in the rollout predictor.

Conventions:

* `y_rel` is the lane-changing vehicle's lateral position relative to the center of the lane it
  STARTED in, positive toward the destination lane; `relative_lateral` builds it from interface
  columns (the partner's start position is the median of its first `settle_s` seconds);
* onset = the first moment from which |y_rel| stays above `band_m`; the band is a parameter, first
  value 0.3 m (three times the 0.1 m "noticeable discrepancy" of card HS.1, itself unverified),
  and every report states it;
* crossing = the first moment |y_rel| >= lane_width / 2 (the body center crosses the line);
* completion = the first moment |y_rel| >= lane_width - band_m;
* straddling time = the time during which the body overlaps the lane line, |y_rel - w/2| < oth_wid/2.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .uncertainty import backward_velocity


def relative_lateral(t, oth_y, ego_y, settle_s: float = 0.5) -> np.ndarray:
    """Partner lateral position relative to its own start, positive toward the ego's lane."""
    t = np.asarray(t, float)
    oth_y = np.asarray(oth_y, float)
    ego_y = np.asarray(ego_y, float)
    m = t <= t[0] + settle_s
    y0 = float(np.median(oth_y[m]))
    e0 = float(np.median(ego_y[m]))
    sign = -np.sign(y0 - e0) if y0 != e0 else 1.0
    return (oth_y - y0) * sign


def lane_change_metrics(t, y_rel, lane_width: float, oth_wid: float = 1.85,
                        band_m: float = 0.3, window_s: float = 0.3) -> dict:
    """Onset, crossing, completion, duration, peak lateral speed and straddling time of one
    lane change; NaN where the event does not occur in the trace."""
    t = np.asarray(t, float)
    y = np.asarray(y_rel, float)
    dev = np.abs(y)
    beyond = dev > band_m
    # suffix_all[i] is True when every sample from i onward is beyond the band
    suffix_all = np.flip(np.cumprod(np.flip(beyond.astype(int)))).astype(bool)
    cand = np.where(suffix_all)[0]
    t_onset = float(t[cand[0]]) if len(cand) else np.nan
    cross = np.where(dev >= lane_width / 2)[0]
    t_cross = float(t[cross[0]]) if len(cross) else np.nan
    done = np.where(dev >= lane_width - band_m)[0]
    t_done = float(t[done[0]]) if len(done) else np.nan
    vy = backward_velocity(t, y, window_s)
    if np.isfinite(t_onset):
        seg = (t >= t_onset) & (t <= (t_done if np.isfinite(t_done) else t[-1]))
        peak = float(np.nanmax(np.abs(vy[seg]))) if np.any(np.isfinite(vy[seg])) else np.nan
    else:
        peak = np.nan
    dt = float(np.median(np.diff(t))) if len(t) > 1 else np.nan
    straddle = float(np.sum(np.abs(dev - lane_width / 2) < oth_wid / 2) * dt)
    return {
        "t_onset_s": t_onset, "t_cross_s": t_cross, "t_complete_s": t_done,
        "duration_s": (t_done - t_onset) if np.isfinite(t_done) and np.isfinite(t_onset) else np.nan,
        "peak_v_lat_mps": peak, "straddle_s": straddle,
        "completed": bool(np.isfinite(t_done)), "band_m": band_m,
    }


def lane_change_summary(metrics: list[dict]) -> pd.DataFrame:
    """One aggregate row over a list of `lane_change_metrics` results."""
    df = pd.DataFrame(metrics) if metrics else pd.DataFrame()
    n = int(len(df))
    comp = df[df["completed"]] if n else df

    def q(col, p):
        v = comp[col].to_numpy(float) if len(comp) else np.array([])
        v = v[np.isfinite(v)]
        return float(np.quantile(v, p)) if len(v) else np.nan

    return pd.DataFrame([{
        "n": n, "n_completed": int(len(comp)),
        "duration_q10_s": q("duration_s", 0.1), "duration_q50_s": q("duration_s", 0.5),
        "duration_q90_s": q("duration_s", 0.9),
        "peak_v_lat_q10_mps": q("peak_v_lat_mps", 0.1), "peak_v_lat_q50_mps": q("peak_v_lat_mps", 0.5),
        "peak_v_lat_q90_mps": q("peak_v_lat_mps", 0.9),
        "straddle_q50_s": q("straddle_s", 0.5),
    }])


def crossing_speed_bounds(metrics: list[dict], lo_q: float = 0.05, hi_q: float = 0.99) -> dict:
    """The crossing norm's lateral-speed band read from data: quantiles of the peak lateral speed
    over completed lane changes. Replaces the proposal's 0.5 and 3.0 m/s once fitted."""
    v = np.array([m["peak_v_lat_mps"] for m in metrics if m.get("completed")], float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return {"n": 0, "v_lo_mps": np.nan, "v_hi_mps": np.nan, "lo_q": lo_q, "hi_q": hi_q}
    return {"n": int(len(v)), "v_lo_mps": float(np.quantile(v, lo_q)),
            "v_hi_mps": float(np.quantile(v, hi_q)), "lo_q": lo_q, "hi_q": hi_q}
