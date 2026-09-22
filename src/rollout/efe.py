"""G(pi): expected free energy of a policy, in the released model's own form.

Card JJ.1, brief section 3.4; `docs/rollout_boundary_design_note.md` section 1.4.

    G(pi) = sum over tau [ max_o log p(o)  -  E_futures log p(o_tau | pi) ]  >= 0,

the residual information of the pragmatic value over the horizon -- exactly the quantity the
released model accumulates (Paper Eq. 13; `notes/02_active_inference_overview.md` section 2).
The six terms are `aidriver.preferences.log_preference_terms` with the collision term's running
minimum along the horizon (SI Eq. 47) applied first, so every step after an imagined collision
stays punished.

Two variants, both run in every card (Jonas's ruling JJ.Q2, 2026-09-17):

  A  released -- all six terms, including p_safe's worst-case counterfactual. **Primary.**
  B  expected outcome -- `PreferenceParams.safety_term_enabled = False`; collisions are scored
     where they happen in the sampled futures, by p_coll with its severity factor.

Epistemic value is not in this card (alpha = 0, the authors' validated configuration). The hook
is `ALPHA`, which must stay 0.0 until a card authorizes otherwise.

Geometry, and where the polygon test replaces the released collision box
------------------------------------------------------------------------
`dx, dy` are the other's position relative to the ego **along the policy's own rollout**, and on
a turning ego they are rotated into the ego's instantaneous heading, because that is the frame
the released terms are written in. The released collision test is a box test on `dx, dy` in that
frame, which is exact where both bodies are aligned with the road and wrong where the paths
cross at an angle. `collision_mode="polygon"` therefore replaces it on the left turn: the
imagined collision is an overlap of the two oriented rectangles at the same tau, and where it
occurs the collision term takes the released magnitude g_C * severity. Each report says which
mode it used.

Steering: `omega = 0` for every policy. The menus carry no steering (ruling JJ1.Q1) and the
released steering term (sigma_omega = 0.02) would otherwise charge the left turn's "proceed"
thousands of nats a step for turning, which is a statement about the term's straight-road
calibration and not about the situation. `cutin_obs` sets omega = 0 for the same reason.
"""
from __future__ import annotations

import numpy as np

from aidriver.preferences import (PreferenceParams, apply_running_min, inverse_tau,
                                  log_collision_pref, log_preference_terms,
                                  _severity)
from comfortzone.conflict import body_polygon, polygon_distance

from .belief import Belief
from .policies import EgoPath
from .predictor import Futures

ALPHA = 0.0          # epistemic value: not in this card; the hook, not the implementation
TERMS = ("speed", "accel", "steer", "lateral", "collision", "safety")


def variant_params(p: PreferenceParams, variant: str) -> PreferenceParams:
    """Variant A is `p` unchanged; variant B switches the safety term off."""
    from dataclasses import replace
    if variant.upper() == "A":
        return p
    if variant.upper() == "B":
        return replace(p, safety_term_enabled=False)
    raise ValueError(f"variant must be 'A' or 'B', not {variant!r}")


def relative_position(ego: EgoPath, fut: Futures) -> tuple[np.ndarray, np.ndarray]:
    """dx, dy [n, T]: the other's position relative to the ego, in the ego's heading frame."""
    dx = fut.x - ego.x[None, :]
    dy = fut.y - ego.y[None, :]
    h = ego.heading[None, :]
    c, s = np.cos(-h), np.sin(-h)
    return c * dx - s * dy, s * dx + c * dy


def observations(belief: Belief, ego: EgoPath, fut: Futures) -> dict:
    """The observation dict `log_preference_terms` expects, broadcast to [n, T]."""
    dx, dy = relative_position(ego, fut)
    n, T = dx.shape
    tau = fut.tau
    vy_other = np.gradient(dy, tau, axis=1) if T > 1 else np.zeros_like(dy)
    ones = np.ones((n, 1))
    return {
        "v": ones * ego.v[None, :],
        "a": ones * ego.a[None, :],
        # Zero for every menu of ruling JJ1.Q1 (`EgoPath` defaults them), and the real yaw rate
        # and lateral acceleration for card JJ.2b's steering policies, so that the released
        # steering term and the total-accel form of the control-effort term both charge for a
        # manoeuvre that steers.
        "omega": ones * ego.omega[None, :],
        "a_lat": ones * ego.a_lat[None, :],
        "y": ones * ego.y_lane[None, :],
        "dx": dx,
        "dy": dy,
        "v_other": fut.v,
        "a_other": np.gradient(fut.v, tau, axis=1) if T > 1 else np.zeros_like(fut.v),
        "theta": ones * ego.heading[None, :],
        "theta_other": fut.heading,
        "vy_other": vy_other,
        "w_other": np.full((n, T), belief.oth_wid),
    }


def polygon_overlap(belief: Belief, ego: EgoPath, fut: Futures) -> np.ndarray:
    """[n, T] bool: do the two oriented rectangles overlap at the same tau?

    Pruned by the centre distance: a pair can only touch when the centres are within the sum of
    the half-diagonals, which on these scenes leaves a handful of exact tests per cell.
    """
    n, T = fut.x.shape
    r = 0.5 * (np.hypot(belief.ego_len, belief.ego_wid) + np.hypot(belief.oth_len, belief.oth_wid))
    centre = np.hypot(fut.x - ego.x[None, :], fut.y - ego.y[None, :])
    out = np.zeros((n, T), bool)
    idx = np.argwhere(centre <= r)
    for i, k in idx:
        pe = body_polygon(ego.x[k], ego.y[k], ego.heading[k], belief.ego_len, belief.ego_wid)
        po = body_polygon(fut.x[i, k], fut.y[i, k], fut.heading[i, k],
                          belief.oth_len, belief.oth_wid)
        out[i, k] = polygon_distance(pe, po) <= 0.0
    return out


def log_terms(belief: Belief, ego: EgoPath, fut: Futures, p: PreferenceParams,
              collision_mode: str = "released") -> dict:
    """The six log-preference terms [n, T], with the collision running minimum applied."""
    obs = observations(belief, ego, fut)
    terms = log_preference_terms(obs, p)
    coll = terms["collision"]
    if collision_mode == "polygon":
        hit = polygon_overlap(belief, ego, fut)
        if hit.any():
            sev = _severity(obs["v"], obs["v_other"], obs["theta"], obs["theta_other"], p)
            coll = np.where(hit, p.g_collision * sev, coll)
    elif collision_mode == "polygon_only":
        # Added 2026-09-22, card JJ.3b: the polygon test REPLACES the released box instead of
        # being added on top of it ("polygon" above is a union, so it can never shrink the box).
        # The non-collision part of the term is taken from the released function with the box
        # forced off (dy pushed far out), then the oriented-polygon hits are overlaid.
        far = dict(obs)
        far["dy"] = np.full_like(np.asarray(obs["dy"], float), 1e6)
        if "tau_inv" not in far:
            far["tau_inv"] = inverse_tau(far["dx"], far["v"], far.get("v_other", 0.0), p)
        coll = log_collision_pref(far, p)
        hit = polygon_overlap(belief, ego, fut)
        if hit.any():
            sev = _severity(obs["v"], obs["v_other"], obs["theta"], obs["theta_other"], p)
            coll = np.where(hit, p.g_collision * sev, coll)
    elif collision_mode != "released":
        raise ValueError(f"collision_mode must be 'released', 'polygon' or 'polygon_only', not"
                         f" {collision_mode!r}")
    terms = dict(terms)
    terms["collision"] = apply_running_min(coll, axis=-1)
    return terms


def expected_free_energy(belief: Belief, ego: EgoPath, fut: Futures, p: PreferenceParams,
                         collision_mode: str = "released",
                         weights: np.ndarray | None = None) -> float:
    """G(pi) in nats, >= 0 by construction.

    `weights` [n] gives the fan a non-uniform weight over samples; None (the default) averages
    uniformly, which is what P0's own fan wants because its samples are drawn from the belief.
    It exists so that the released model's PARTICLE fan, which carries importance weights, can
    be scored by exactly this function -- card RE.1's part 0 uses it to show that this quantity
    IS `aidriver.agent.ActiveInferenceDriver.policy_surprise`, the model's Eq. 13 signal.
    """
    terms = log_terms(belief, ego, fut, p, collision_mode)
    logp = sum(terms.values())                       # [n, T]
    if weights is None:
        mean = logp.mean(axis=0)
    else:
        w = np.asarray(weights, float)
        mean = np.einsum("nt,n->t", logp, w / w.sum())
    residual = p.max_log_preference() - mean
    return float(np.sum(np.maximum(residual, 0.0)))


def g_by_policy(belief: Belief, fut: Futures, paths: dict[str, EgoPath], p: PreferenceParams,
                collision_mode: str = "released",
                weights: np.ndarray | None = None) -> dict[str, float]:
    """G for every policy on the SAME fan (common random numbers)."""
    return {name: expected_free_energy(belief, path, fut, p, collision_mode, weights)
            for name, path in paths.items()}
