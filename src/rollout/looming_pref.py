"""The released model's own looming preference as the pragmatic value (card JJ.5).

The released preference contains a one-sided Gaussian preference over inverse tau
(`aidriver.preferences`, `tau_inv_mu` = 0.2 s^-1, i.e. a preferred TTC of 5 s or more,
`tau_inv_sd` = 0.125; SI Eq. 48, released code `reward.py:272`): closing faster than that costs,
closing slower costs nothing. It is the model's looming term, and inside the released assembly it
sits in the collision factor, where the post-contact collision cost swamps it (card RE.2 folded
the two together). It has never been scored on its own inside a rollout.

Here it is read out alone, as the residual information of that one term, averaged over the fan
and summed over the horizon of a policy:

    eps_tau(pi) = sum_t max(0, 0 - mean over futures of log p_tau(o_t | pi))      [nats]

with log p_tau normalised so that its maximum (not closing faster than 1/5 s) is zero. The term
applies only when the other is AHEAD (dx > length, released convention) and, in the primary
reading, only in futures where the other is IN THE EGO'S PATH:

  `gate="in_path"`   (primary) the other's body overlaps the ego's lane laterally at that step,
                     |dy| <= 1.15 * ego width, the lateral extent of the released collision box.
                     A vehicle is a lead when it is in my path; in the fan, the "changing" futures
                     enter the path and the "keeping" ones do not. So E_fan[eps_tau] is
                     P(in path) x looming excess: the structure of card G.1's gated looming rule,
                     with the gate supplied by the intention belief instead of a fitted term.
  `gate="none"`      the released term as written: any vehicle ahead, in any lane, is charged.
  `gate="continuous"` the project's lane-entry weight (`lane_entry_continuous`, k = 12), card
                     JJ.2's staging, for comparison.

The term is read BEFORE CONTACT only. In the released assembly the collision term replaces it
from the first step at which the released box is entered (|dx| <= 1.15 length and |dy| <= 1.15
width); here those steps, and every later step of that future, are masked out instead. Without the
mask a `continue` policy that drives through the lead sends tau^-1 to 1/(1 mm) and the term to
1e8 nats a step, which is the horizon-through-the-lead artefact the 2026-09-22 review found
behind card RE.2's -0.861.

Nothing is fitted; the constants are the released ones. The card scores eps_tau(continue) as the
axis, and the price form  min over admissible pi of eps_tau(pi)  beside it.
"""
from __future__ import annotations

import numpy as np

from aidriver.preferences import (LOG_2PI, PreferenceParams, _log_gauss, inverse_tau,
                                  lane_entry_weight)

from .efe import observations


def log_tau_term(obs: dict, p: PreferenceParams, gate: str = "in_path") -> np.ndarray:
    """log p_tau [n, T], max-normalised to 0, gated as described in the module docstring."""
    veh = p.vehicle
    dx = np.asarray(obs["dx"], float)
    dy = np.asarray(obs["dy"], float)
    tau_inv = inverse_tau(dx, obs["v"], obs["v_other"], p)
    if p.tau_inv_one_sided:
        tau_inv = np.maximum(tau_inv, p.tau_inv_mu)
    log_tau = _log_gauss(tau_inv, p.tau_inv_mu, p.tau_inv_sd) - (-np.log(p.tau_inv_sd) - 0.5 * LOG_2PI)
    ahead = dx > veh.length
    contact = (np.abs(dx) <= 1.15 * veh.length) & (np.abs(dy) <= 1.15 * veh.width)
    before_contact = ~np.logical_or.accumulate(contact, axis=-1)
    if gate == "in_path":
        weight = (np.abs(dy) <= 1.15 * veh.width).astype(float)
    elif gate == "none":
        weight = 1.0
    elif gate == "continuous":
        weight = lane_entry_weight(obs, p)
    else:
        raise ValueError(f"gate must be 'in_path', 'none' or 'continuous', not {gate!r}")
    return np.where(ahead & before_contact, weight * log_tau, 0.0)


def eps_tau_profile(belief, ego, fut, p: PreferenceParams, gate: str = "in_path"):
    """Per step: the expected excess of the looming term [T] (>= 0), and the number of steps at
    which at least half the futures are still before contact (card JJ.5b)."""
    obs = observations(belief, ego, fut)
    lt = log_tau_term(obs, p, gate)
    veh = p.vehicle
    dx, dy = np.asarray(obs["dx"], float), np.asarray(obs["dy"], float)
    contact = (np.abs(dx) <= 1.15 * veh.length) & (np.abs(dy) <= 1.15 * veh.width)
    before = ~np.logical_or.accumulate(contact, axis=-1)
    n_pre = int(np.sum(before.mean(axis=0) >= 0.5))
    return np.maximum(0.0 - lt.mean(axis=0), 0.0), n_pre


def eps_tau(belief, ego, fut, p: PreferenceParams, gate: str = "in_path") -> float:
    """The residual information of the looming term summed over the horizon, in nats (>= 0)."""
    return float(np.sum(eps_tau_profile(belief, ego, fut, p, gate)[0]))


def share_in_path(belief, ego, fut, p: PreferenceParams) -> float:
    """The share of futures in which the other is ahead and in the ego's path at some step."""
    obs = observations(belief, ego, fut)
    veh = p.vehicle
    hit = (np.asarray(obs["dx"], float) > veh.length) & (np.abs(np.asarray(obs["dy"], float))
                                                          <= 1.15 * veh.width)
    return float(hit.any(axis=1).mean())
