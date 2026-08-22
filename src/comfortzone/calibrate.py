"""
Anchoring the comfort-zone boundary in observed behaviour.

A level set is only a comfort-zone boundary if the level `c` means something. Two ways to
fix it, both implemented here:

  1. **Behavioural**: the boundary is where drivers start to act. In the active-inference
     model, action is triggered when accumulated evidence crosses threshold, so
     `calibrate_level` finds the c whose exceedances best coincide with observed response
     onsets.
  2. **Distributional**: the boundary is a quantile of the eps values drivers actually accept
     in normal driving -- the classical CZB approach (e.g. the 95th percentile of accepted
     minimum-TTC), transferred to the scalar field.

Both take a set of trajectories; neither requires the closed-loop model to run, only the
preference function.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from aidriver.preferences import PreferenceParams, pragmatic_deficit


def exceedance_events(deficit_series: np.ndarray, level: float,
                      min_separation: int = 1) -> np.ndarray:
    """
    Indices at which a deficit time series crosses `level` upwards.

    `min_separation` suppresses repeated crossings within that many samples, so a noisy
    signal hovering at the boundary counts as one exceedance rather than many.
    """
    y = np.asarray(deficit_series, dtype=float)
    above = y > level
    onsets = np.where(np.diff(above.astype(int)) == 1)[0] + 1
    if len(onsets) <= 1 or min_separation <= 1:
        return onsets
    keep = [onsets[0]]
    for o in onsets[1:]:
        if o - keep[-1] >= min_separation:
            keep.append(o)
    return np.array(keep)


@dataclass
class CalibrationResult:
    level: float
    score: float
    levels: np.ndarray
    scores: np.ndarray
    method: str

    def __repr__(self):
        return (f"CalibrationResult(level={self.level:.4g}, "
                f"score={self.score:.4g}, method={self.method!r})")


def calibrate_level(deficit_series_list, onset_indices,
                    levels=None, tolerance: int = 3,
                    method: str = "onset") -> CalibrationResult:
    """
    Fit the comfort-zone threshold c to observed behaviour.

    Parameters
    ----------
    deficit_series_list
        One eps(t) series per trial/trajectory, computed from the driver's preference
        function along the recorded kinematics.
    onset_indices
        The observed response onset sample index for each trial (e.g. brake onset extracted
        by the piecewise-linear fit of Markkula et al.), or None for trials with no response.
    levels
        Candidate thresholds. Defaults to a log-spaced sweep over the observed eps range.
    tolerance
        A predicted exceedance counts as matching an observed onset if it falls within this
        many samples.
    method
        "onset"   -- maximise agreement between first exceedance and observed onset
                     (F1 over trials, with timing tolerance).
        "quantile"-- ignore onsets; return the given quantile of eps over all samples that
                     did *not* trigger a response (pass it via `tolerance` as a percentage,
                     e.g. tolerance=95).

    Returns
    -------
    CalibrationResult
    """
    series = [np.asarray(s, dtype=float) for s in deficit_series_list]

    if method == "quantile":
        pooled = np.concatenate([s[np.isfinite(s)] for s in series])
        q = float(np.percentile(pooled, tolerance))
        return CalibrationResult(level=q, score=np.nan,
                                 levels=np.array([q]), scores=np.array([np.nan]),
                                 method="quantile")

    pooled = np.concatenate([s[np.isfinite(s)] for s in series])
    pooled = pooled[pooled > 0]
    if levels is None:
        lo = max(np.percentile(pooled, 1), 1e-6)
        hi = max(np.percentile(pooled, 99.9), lo * 10)
        levels = np.logspace(np.log10(lo), np.log10(hi), 200)
    levels = np.asarray(levels, dtype=float)

    scores = np.empty(len(levels))
    for i, c in enumerate(levels):
        tp = fp = fn = 0
        for s, onset in zip(series, onset_indices):
            ex = exceedance_events(s, c)
            first = ex[0] if len(ex) else None
            if onset is None:
                fp += 1 if first is not None else 0
            elif first is None:
                fn += 1
            elif abs(int(first) - int(onset)) <= tolerance:
                tp += 1
            else:
                fp += 1
                fn += 1
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        scores[i] = 0.0 if (prec + rec) == 0 else 2 * prec * rec / (prec + rec)

    best = int(np.argmax(scores))
    return CalibrationResult(level=float(levels[best]), score=float(scores[best]),
                             levels=levels, scores=scores, method="onset")


def deficit_along_trajectory(ego: np.ndarray, other: np.ndarray,
                             p: PreferenceParams,
                             actions: np.ndarray | None = None) -> np.ndarray:
    """
    Evaluate the comfort-zone field along a recorded trajectory pair.

    `ego`, `other` are (T, 5) arrays of [x, y, theta, delta, v]; `actions` is an optional
    (T, 2) array of [a, omega]. Returns eps(t), the input to `calibrate_level`.

    This is the bridge from naturalistic or simulator data to the comfort-zone field: no
    model roll-out is needed, only the driver's preference function evaluated on what
    actually happened.
    """
    ego = np.asarray(ego, dtype=float)
    other = np.asarray(other, dtype=float)
    T = len(ego)
    if actions is None:
        dt = p.vehicle.dt
        a = np.gradient(ego[:, 4], dt)
        omega = np.gradient(ego[:, 3], dt)
    else:
        a, omega = actions[:, 0], actions[:, 1]
    a_other = np.gradient(other[:, 4], p.vehicle.dt)

    obs = {
        "v": ego[:, 4], "a": a, "omega": omega, "y": ego[:, 1],
        "theta": ego[:, 2], "theta_other": other[:, 2],
        "dx": other[:, 0] - ego[:, 0], "dy": other[:, 1] - ego[:, 1],
        "v_other": other[:, 4], "a_other": a_other,
    }
    return pragmatic_deficit(obs, p)
