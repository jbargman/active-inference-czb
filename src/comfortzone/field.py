"""
The comfort-zone scalar field, and its closed-form boundary in car-following geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from aidriver.preferences import (
    PreferenceParams, log_preference_terms, pragmatic_deficit,
    required_deceleration, safety_margin,
)


# --------------------------------------------------------------------------------------
# closed-form boundary (car following)
# --------------------------------------------------------------------------------------
def critical_gap(v_ego, v_other=None, p: PreferenceParams = None,
                 a_ego=0.0, a_other=0.0, a_required=None) -> np.ndarray:
    """
    Closed-form comfort-zone boundary for car following: the longitudinal gap `dx*` at which
    the required deceleration exactly equals the limit.

    Schumann et al.'s p_safe switches on when

        a_ego,req < -a_max ,
        a_ego,req = -0.5 * v_react^2 / ( d_react - 1.15 L ) ,
        v_react   = v_ego + min(a_ego,0) * t_react ,
        d_react   = [ dx - v_other^2 / (2 a_test) ] - [ v_ego t_react + 0.5 min(a_ego,0) t_react^2 ] ,
        a_test    = min(a_other, a_OV,min) .

    Setting a_ego,req = -a_req_limit and solving for dx:

        dx* = 1.15 L + 0.5 v_react^2 / a_req_limit
              - v_other^2 / (2 |a_test|)  +  v_ego t_react + 0.5 min(a_ego,0) t_react^2

    (the lead vehicle's own stopping distance v_other^2 / 2|a_test| *reduces* the separation
    you need, because it travels that far before stopping -- getting this sign wrong inflates
    the critical headway to ~3 s instead of ~0.7 s, which is why `tests/test_comfortzone.py`
    checks the closed form against the numeric field.)

    Parameters
    ----------
    v_ego, v_other
        Speeds [m/s]. `v_other` defaults to `v_ego` (steady following).
    a_required
        The deceleration defining the boundary. Defaults to `p.a_max`, which reproduces the
        model's own p_safe boundary. Set it lower (e.g. 4 m/s^2) to obtain a *comfort*
        boundary rather than a *physical-limit* (dread) boundary -- see the module notes:
        drivers do not voluntarily plan to brake at 8 m/s^2.

    Returns
    -------
    dx* [m], the bumper-to-bumper-plus-length critical separation of vehicle centres.
    """
    p = p or PreferenceParams()
    v_ego = np.asarray(v_ego, dtype=float)
    v_other = v_ego if v_other is None else np.asarray(v_other, dtype=float)
    a_ego = np.minimum(np.asarray(a_ego, dtype=float), 0.0)
    a_other = np.minimum(np.asarray(a_other, dtype=float), 0.0)

    lim = p.a_max if a_required is None else float(a_required)
    a_test = np.minimum(a_other, p.a_other_min)
    t = p.response_time
    L = p.vehicle.length

    v_react = np.maximum(v_ego + a_ego * t, 0.0)
    return (1.15 * L
            + 0.5 * v_react ** 2 / lim
            - v_other ** 2 / (2.0 * np.abs(a_test))
            + v_ego * t + 0.5 * a_ego * t ** 2)


def critical_thw(v_ego, v_other=None, p: PreferenceParams = None, **kw) -> np.ndarray:
    """
    The same boundary expressed as a time headway [s] -- the form the CZB literature usually
    reports, so it can be compared directly with naturalistic estimates.

        THW* = (dx* - L) / v_ego
    """
    p = p or PreferenceParams()
    v_ego = np.asarray(v_ego, dtype=float)
    dx = critical_gap(v_ego, v_other, p, **kw)
    return (dx - p.vehicle.length) / np.maximum(v_ego, 1e-6)


# --------------------------------------------------------------------------------------
# fields
# --------------------------------------------------------------------------------------
@dataclass
class ComfortField:
    """
    A comfort-zone scalar field evaluated on a regular 2-D grid.

    Attributes
    ----------
    x, y      : 1-D grids of the two varied state variables
    xname, yname : their names
    deficit   : (len(y), len(x)) residual information eps -- the comfort-zone field
    margin    : (len(y), len(x)) signed braking margin [m/s^2] (a_req + a_max)
    terms     : dict of the individual log-preference terms, same shape
    """
    x: np.ndarray
    y: np.ndarray
    xname: str
    yname: str
    deficit: np.ndarray
    margin: np.ndarray
    terms: Mapping[str, np.ndarray]

    def at(self, xv, yv):
        """Nearest-grid-point lookup of the deficit."""
        i = int(np.argmin(np.abs(self.x - xv)))
        j = int(np.argmin(np.abs(self.y - yv)))
        return float(self.deficit[j, i])


def _base_obs(p: PreferenceParams) -> dict:
    return {
        "v": p.v_desired, "a": 0.0, "omega": 0.0, "y": p.lane_centre,
        "dx": 1e4, "dy": 0.0, "v_other": p.v_desired, "a_other": 0.0,
        "theta": 0.0, "theta_other": 0.0,
    }


#: the preference terms that describe the interaction with another road user, as opposed to
#: the driver's own comfort with their speed and control inputs
INTERACTION_TERMS = ("collision", "safety")


def comfort_field(p: PreferenceParams,
                  xname: str, xgrid: Sequence[float],
                  yname: str, ygrid: Sequence[float],
                  fixed: Mapping[str, float] | None = None,
                  couple: Mapping[str, str] | None = None,
                  terms: Sequence[str] | None = None) -> ComfortField:
    """
    Evaluate the comfort-zone field over a 2-D slice of the observation space.

    Parameters
    ----------
    p
        The driver's preference function -- i.e. *whose* comfort zone this is. Changing
        `v_desired`, `tau_inv_mu`, `response_time` or `a_other_min` changes the boundary,
        which is how "extra motives" (hurry, aggression) enter: they reshape the preference,
        not the physics.
    xname, xgrid, yname, ygrid
        Which two observation variables to vary and over what values. Any keys of the
        observation dict work: "v", "dx", "dy", "y", "v_other", "a_other", "a", "omega".
    fixed
        Values for the remaining variables (defaults: ego at desired speed, mid-lane, other
        vehicle far ahead at the same speed).
    couple
        Optional {target: source} to tie one variable to another, e.g. {"v_other": "v"} for
        steady-state following where both vehicles travel at the same speed.
    terms
        Which log-preference terms contribute to the returned `deficit`. Defaults to all six.
        Pass `INTERACTION_TERMS` when mapping the comfort zone over a *speed* axis: otherwise
        the speed preference (sigma_v = 0.5 m/s) dominates the field and hides the structure
        you are looking for, because every speed other than the desired one is heavily
        penalised regardless of the traffic situation.

    Returns
    -------
    ComfortField
    """
    xg = np.asarray(xgrid, dtype=float)
    yg = np.asarray(ygrid, dtype=float)
    X, Y = np.meshgrid(xg, yg)

    obs = _base_obs(p)
    if fixed:
        obs.update(fixed)
    obs = {k: np.broadcast_to(np.asarray(v, dtype=float), X.shape).copy()
           for k, v in obs.items()}
    obs[xname] = X.copy()
    obs[yname] = Y.copy()
    for tgt, src in (couple or {}).items():
        obs[tgt] = obs[src].copy()

    all_terms = log_preference_terms(obs, p)
    if terms is None:
        deficit = pragmatic_deficit(obs, p)
    else:
        missing = set(terms) - set(all_terms)
        if missing:
            raise ValueError(f"unknown preference terms: {sorted(missing)}")
        sel = sum(all_terms[k] for k in terms)
        deficit = np.maximum(-sel, 0.0)     # each selected term has maximum 0
    return ComfortField(
        x=xg, y=yg, xname=xname, yname=yname,
        deficit=deficit,
        margin=safety_margin(obs, p),
        terms=all_terms,
    )


def margin_field(p: PreferenceParams, **kw) -> np.ndarray:
    """Convenience: just the signed braking margin over the same grid spec."""
    return comfort_field(p, **kw).margin
