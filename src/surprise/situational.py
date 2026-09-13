"""
Situational surprise: when does a traffic situation stop unfolding as expected?

Card HS.1 (2026-09-13), from Jonas's question of 2026-09-12: can surprise be taken about the
*situation as a whole* -- the automated ego and the other road users jointly -- rather than
about the other road users' actions only, and can its onset serve as the start of evidence
accumulation?

One predictor, three references
-------------------------------
Every reference uses the same minimal, scenario-agnostic predictive model: each monitored
trajectory is extrapolated at constant velocity from h seconds earlier, with a Gaussian
predictive spread sigma(h) = sigma0 + sigma1 * h + sigma_a * h^2 / 2 on each axis of the
trajectory's own direction of travel (longitudinal, lateral). sigma1 is uncertainty about
velocity, sigma_a about acceleration.

**A property worth knowing before choosing the spread** (found by the property tests,
2026-09-13, before any data was touched). A fixed-horizon constant-velocity predictor only
registers a change that leaves the predicted band *within one horizon*: the error after a
step dv in velocity is at most dv * h, and after a constant acceleration a it is at most
a * h^2 / 2. With h = 0.5 s and sigma(h) = 0.35 m -- the lower end of card Q5.1's sweep --
a smooth lane change would need about 5.6 m/s^2 of lateral acceleration to register at
2 sigma, several times what real lane changes use. Card Q5.1 expected onset "within one
frame" of the manoeuvre with those settings; its own spread made that impossible. Onset
latency after a constant acceleration a is sqrt(2 z_on sigma(h) / a), so any predictor with
non-zero spread detects gentle manoeuvres later than sharp ones. The standardized error
z = error / sigma is computed per axis, and the residual information of a Gaussian
normalized to its mode is z^2 / 2. What differs between the references is only WHAT is
monitored:

* ``world``    -- the other road users' own motion. Surprise about the world: the
                  Dinparastdjadid et al. (2023) construction, and card Q5.1's reference.
* ``joint``    -- the ego's own motion AND every other road user's, the maximum over all.
                  Surprise of the system: the ego's automated manoeuvre counts as much as the
                  other vehicle's.
* ``relative`` -- each other road user's position RELATIVE TO THE EGO, extrapolated at
                  constant relative velocity and resolved in the ego's direction of travel.
                  The situation as it presents itself from the driver's seat.

``joint`` and ``relative`` are two formalizations of Jonas's "holistic" surprise. They agree
when one party moves steadily and differ when both change together: two vehicles swerving in
parallel are jointly surprising but relatively unremarkable.

Onset is the first time any monitored axis exceeds ``z_on`` standard deviations. The default
``z_on = 2`` is a conventional "outside the expected region" criterion (about 95% two-sided
for a Gaussian), not a fitted value.

What this module is not
-----------------------
It is not a model of what a driver expects. A constant-velocity extrapolation treats any
manoeuvre as a departure, including a planned, perfectly ordinary one. That is the point of
using the minimal reference first: if even this does the job, a richer one may not be needed;
where it fails, the failure says what the reference must know.

References
----------
Dinparastdjadid, A., Supeene, I., & Engström, J. (2023). *Measuring surprise in the wild*
(arXiv:2305.07733). arXiv. https://arxiv.org/abs/2305.07733
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

REFERENCES = ("world", "joint", "relative")


@dataclass(frozen=True)
class PredictorSettings:
    """Constant-velocity predictor. Each value's motivation is stated where it is chosen
    (the HS.1 script); defaults are that script's pre-stated primary setting."""
    h: float = 1.0          # prediction horizon [s]
    sigma0: float = 0.1     # positional spread at zero horizon [m]
    sigma1: float = 0.0     # growth per second of horizon, from velocity uncertainty [m/s]
    sigma_a: float = 0.0    # growth from acceleration uncertainty [m/s^2]
    z_on: float = 2.0       # onset criterion [standard deviations]
    v_window: float | None = None   # backward window for the velocity estimate [s]; None =
                                    # one sample. Real traces carry position jitter that a
                                    # one-sample difference turns into phantom velocity.
    sigma0_lon: float | None = None  # per-axis override of sigma0 on the longitudinal axis;
                                     # None = sigma0. Some traces jitter along the direction of
                                     # travel far more than across it.

    @property
    def sigma(self) -> float:
        return self.sigma0 + self.sigma1 * self.h + 0.5 * self.sigma_a * self.h ** 2


@dataclass
class Track:
    """One road user's world-frame trajectory on a uniform time grid."""
    t: np.ndarray
    x: np.ndarray
    y: np.ndarray


def _heading_axes(vx: np.ndarray, vy: np.ndarray):
    """Unit vectors along and across the direction of travel; world x when stationary."""
    speed = np.hypot(vx, vy)
    moving = speed > 1e-3
    ux = np.where(moving, vx / np.where(moving, speed, 1.0), 1.0)
    uy = np.where(moving, vy / np.where(moving, speed, 1.0), 0.0)
    return (ux, uy), (-uy, ux)


def cv_standardized_error(t: np.ndarray, x: np.ndarray, y: np.ndarray,
                          s: PredictorSettings, frame_vxy=None):
    """Per-sample standardized constant-velocity prediction error, (z_lon, z_lat).

    The prediction for sample i is made from sample i - k (k = round(h / dt)): position there
    plus velocity there times the elapsed time, velocity by a one-sample backward difference.
    `frame_vxy` optionally supplies the velocity that defines the axes (the ego's, for the
    relative reference); otherwise the trajectory's own velocity at i - k is used. Samples
    with no prediction available are NaN.
    """
    t = np.asarray(t, float)
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(t)
    z_lon = np.full(n, np.nan)
    z_lat = np.full(n, np.nan)
    if n < 3:
        return z_lon, z_lat
    dt = float(np.median(np.diff(t)))
    k = max(1, int(round(s.h / dt)))
    m = 1 if s.v_window is None else max(1, int(round(s.v_window / dt)))
    if n <= k + m:
        return z_lon, z_lat
    j = np.arange(k + m, n)                 # target samples
    i0 = j - k                              # prediction origin
    vx = (x[i0] - x[i0 - m]) / (t[i0] - t[i0 - m])
    vy = (y[i0] - y[i0 - m]) / (t[i0] - t[i0 - m])
    el = t[j] - t[i0]
    ex = x[j] - (x[i0] + vx * el)
    ey = y[j] - (y[i0] + vy * el)
    if frame_vxy is None:
        fvx, fvy = vx, vy
    else:
        fvx, fvy = frame_vxy[0][i0], frame_vxy[1][i0]
    (ax, ay), (bx, by) = _heading_axes(fvx, fvy)
    growth = s.sigma1 * el + 0.5 * s.sigma_a * el ** 2
    sig_lat = s.sigma0 + growth
    sig_lon = (s.sigma0 if s.sigma0_lon is None else s.sigma0_lon) + growth
    z_lon[j] = (ex * ax + ey * ay) / sig_lon
    z_lat[j] = (ex * bx + ey * by) / sig_lat
    return z_lon, z_lat


def _velocity(t, x, y, v_window=None):
    """Backward-difference velocity (only the past), over `v_window` seconds if given."""
    n = len(t)
    dt = float(np.median(np.diff(t))) if n > 1 else 1.0
    m = 1 if v_window is None else max(1, int(round(v_window / dt)))
    vx = np.zeros(n)
    vy = np.zeros(n)
    if n > m:
        vx[m:] = (x[m:] - x[:-m]) / (t[m:] - t[:-m])
        vy[m:] = (y[m:] - y[:-m]) / (t[m:] - t[:-m])
        vx[:m], vy[:m] = vx[m], vy[m]
    return vx, vy


def situational_surprise(ego: Track, others: dict, reference: str,
                         s: PredictorSettings = PredictorSettings()) -> pd.DataFrame:
    """Surprise series for one scene under one reference.

    Returns a frame with `t`, `z_max` (the largest absolute standardized error over every
    monitored axis), `ri` (= z_max^2 / 2, residual information of the worst axis) and
    `source` (which trajectory and axis produced the maximum). Every track must share the
    ego's time grid.
    """
    if reference not in REFERENCES:
        raise ValueError(f"reference must be one of {REFERENCES}, got {reference!r}")
    t = np.asarray(ego.t, float)
    parts: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    if reference in ("world", "joint"):
        for name, tr in others.items():
            parts[str(name)] = cv_standardized_error(t, tr.x, tr.y, s)
    if reference == "joint":
        parts["ego"] = cv_standardized_error(t, ego.x, ego.y, s)
    if reference == "relative":
        evx, evy = _velocity(t, np.asarray(ego.x, float), np.asarray(ego.y, float), s.v_window)
        for name, tr in others.items():
            rx = np.asarray(tr.x, float) - np.asarray(ego.x, float)
            ry = np.asarray(tr.y, float) - np.asarray(ego.y, float)
            parts[str(name)] = cv_standardized_error(t, rx, ry, s, frame_vxy=(evx, evy))

    n = len(t)
    z_max = np.full(n, np.nan)
    source = np.array([""] * n, dtype=object)
    for name, (zl, zt) in parts.items():
        for axis, z in (("lon", zl), ("lat", zt)):
            a = np.abs(z)
            better = np.isfinite(a) & (~np.isfinite(z_max) | (a > z_max))
            z_max[better] = a[better]
            source[better] = f"{name}:{axis}"
    return pd.DataFrame({"t": t, "z_max": z_max, "ri": 0.5 * z_max ** 2, "source": source})


def onset_time(series: pd.DataFrame, s: PredictorSettings = PredictorSettings(),
               t_from: float = -np.inf) -> float:
    """First time at or after `t_from` at which z_max reaches z_on; NaN if never."""
    t = series["t"].to_numpy(float)
    z = series["z_max"].to_numpy(float)
    hit = np.flatnonzero((t >= t_from) & np.isfinite(z) & (z >= s.z_on))
    return float(t[hit[0]]) if len(hit) else float("nan")
