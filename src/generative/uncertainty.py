"""
Component C3 -- how far a constant-velocity prediction of another road user drifts from what it
then does, as a function of the horizon. This is the width of the fan the rollout formulation
(`docs/rollout_boundary_design_note.md` section 1.2) needs, and it replaces the unverified growth
constants there with measured ones.

Definitions:

* velocity is a BACKWARD difference over `window_s`, the same construction the video cards use for
  the lateral rate (card G.1: 0.3 s), so that "what a driver could have extrapolated at time t"
  uses only what was visible up to t;
* the prediction error at horizon h is x(t + h) - [x(t) + v(t) h], evaluated at every t for which
  both the window and the target exist; lateral and longitudinal separately;
* the growth model is sd(h)^2 = s0^2 + (s1 h)^2, fitted by least squares on sd^2 against h^2.

A caution the property tests make explicit: measurement jitter alone produces growth, because a
velocity read from two jittered positions carries an error of about sqrt(2) * sigma / window that
is then multiplied by h. On tracks with known jitter the measured s1 must be compared with that
floor before any of it is attributed to the road user's behavior.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def backward_velocity(t, x, window_s: float) -> np.ndarray:
    """Backward-difference velocity over `window_s`; NaN where the window is not available."""
    t = np.asarray(t, float)
    x = np.asarray(x, float)
    j = np.searchsorted(t, t - window_s + 1e-9, side="right") - 1
    ok = j >= 0
    jj = np.where(ok, j, 0)
    dtj = t - t[jj]
    ok &= dtj > 0
    v = np.full(len(t), np.nan)
    v[ok] = (x[ok] - x[jj[ok]]) / dtj[ok]
    return v


def cv_prediction_errors(t, x, y, horizons_s, window_s: float = 0.3) -> dict:
    """Constant-velocity prediction errors per horizon.

    Returns {h: (err_lon, err_lat)} with one entry per horizon, arrays of the errors at every
    valid origin time. `x` is the longitudinal and `y` the lateral coordinate of the road user
    whose motion is predicted, in any fixed frame.
    """
    t = np.asarray(t, float)
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    vx = backward_velocity(t, x, window_s)
    vy = backward_velocity(t, y, window_s)
    dt = float(np.median(np.diff(t))) if len(t) > 1 else np.nan
    out = {}
    for h in horizons_s:
        k = np.searchsorted(t, t + h - 1e-9, side="left")
        ok = (k < len(t)) & np.isfinite(vx) & np.isfinite(vy)
        kk = np.where(ok, k, 0)
        ok &= np.abs(t[kk] - (t + h)) <= dt / 2 + 1e-9
        ex = x[kk] - (x + vx * h)
        ey = y[kk] - (y + vy * h)
        out[float(h)] = (ex[ok], ey[ok])
    return out


def pool_errors(per_track: list[dict]) -> dict:
    """Merge the per-track dictionaries of `cv_prediction_errors` into one."""
    pooled: dict = {}
    for d in per_track:
        for h, (ex, ey) in d.items():
            if h not in pooled:
                pooled[h] = ([], [])
            pooled[h][0].append(ex)
            pooled[h][1].append(ey)
    return {h: (np.concatenate(a) if a else np.array([]), np.concatenate(b) if b else np.array([]))
            for h, (a, b) in pooled.items()}


def growth_table(errors_by_h: dict, n_tracks: int) -> pd.DataFrame:
    """One row per horizon: n, sd and the 90th percentile of |error| on each axis."""
    rows = []
    for h in sorted(errors_by_h):
        ex, ey = errors_by_h[h]
        n = int(min(len(ex), len(ey)))
        rows.append({
            "horizon_s": h, "n": n, "n_tracks": int(n_tracks),
            "sd_lon_m": float(np.std(ex)) if n > 1 else np.nan,
            "sd_lat_m": float(np.std(ey)) if n > 1 else np.nan,
            "q90_abs_lon_m": float(np.quantile(np.abs(ex), 0.9)) if n > 0 else np.nan,
            "q90_abs_lat_m": float(np.quantile(np.abs(ey), 0.9)) if n > 0 else np.nan,
        })
    return pd.DataFrame(rows)


def fit_growth(horizons_s, sd) -> tuple[float, float]:
    """Least-squares fit of sd(h)^2 = s0^2 + (s1 h)^2; returns (s0, s1), each >= 0."""
    h = np.asarray(horizons_s, float)
    s = np.asarray(sd, float)
    ok = np.isfinite(h) & np.isfinite(s)
    if ok.sum() < 2:
        return (np.nan, np.nan)
    A = np.column_stack([np.ones(ok.sum()), h[ok] ** 2])
    coef, *_ = np.linalg.lstsq(A, s[ok] ** 2, rcond=None)
    a, b = coef
    return (float(np.sqrt(max(a, 0.0))), float(np.sqrt(max(b, 0.0))))


def fit_growth_accel(horizons_s, sd) -> tuple[float, float]:
    """Least-squares fit of sd(h)^2 = s0^2 + (0.5 sigma_a h^2)^2; returns (s0, sigma_a), each >= 0.

    The sibling of `fit_growth` for the LONGITUDINAL axis, added 2026-09-18 for card GM.1a. The
    rollout fan's two axes do not grow the same way (`docs/rollout_boundary_design_note.md`
    section 1.2): the lateral position sd grows linearly in the horizon, because the perturbation
    is a constant lateral VELOCITY, while the longitudinal one grows quadratically, because the
    perturbation is a constant ACCELERATION. `fit_growth` fits the first form and so cannot return
    the fan's sigma_a at all; this fits the second and does.

    Fitting both and comparing the residuals is a test of the fan's FORM, not only of its
    constants: if a set of tracks is better described by the linear form, the constant-acceleration
    perturbation is the wrong model for them however its constant is chosen.
    """
    h = np.asarray(horizons_s, float)
    s = np.asarray(sd, float)
    ok = np.isfinite(h) & np.isfinite(s)
    if ok.sum() < 2:
        return (np.nan, np.nan)
    A = np.column_stack([np.ones(ok.sum()), h[ok] ** 4])
    coef, *_ = np.linalg.lstsq(A, s[ok] ** 2, rcond=None)
    a, b = coef
    return (float(np.sqrt(max(a, 0.0))), float(2.0 * np.sqrt(max(b, 0.0))))


def growth_residual(horizons_s, sd, s0: float, slope: float, quadratic: bool) -> float:
    """Root-mean-square residual of a fitted growth curve, in metres, for comparing the two forms
    on the same horizons. `slope` is s1 for the linear form and sigma_a for the quadratic one."""
    h = np.asarray(horizons_s, float)
    s = np.asarray(sd, float)
    ok = np.isfinite(h) & np.isfinite(s)
    if not ok.any() or not np.isfinite(s0) or not np.isfinite(slope):
        return float("nan")
    grow = (0.5 * slope * h[ok] ** 2) if quadratic else (slope * h[ok])
    pred = np.sqrt(s0 ** 2 + grow ** 2)
    return float(np.sqrt(np.mean((pred - s[ok]) ** 2)))


def jitter_growth_floor(sigma_m: float, window_s: float) -> float:
    """The slope s1 [m/s] that pure white position jitter of `sigma_m` produces through the
    backward-difference velocity: sqrt(2) * sigma / window. Compare a measured s1 with this
    before reading any of it as behavior."""
    return float(np.sqrt(2.0) * sigma_m / window_s)
