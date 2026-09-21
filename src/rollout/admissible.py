"""Admissibility: strand 1's absolute conflict preference as a constraint, not a cost (card S1.6).

Jonas's ruling S14.Q2 (2026-09-22): implement the conflict preference of Engström et al. (2024)
-- "an absolute preference over no-conflict" -- by EXCLUDING colliding policies from the menu
rather than charging them a large finite constant, which card S1.4 showed to be consequential
(-300 / -1 000 / -3 000 nats gave 0.3244 / 0.3221 / 0.2864).

WHAT THAT DOES TO DELTA G. Card JJ.1 defined

    Delta G = G(continue) - min over the menu G(pi).

Under admissibility the conflict term leaves G altogether -- a policy is either allowed or it is
not -- so G is the COMFORT cost alone (speed and control effort; on a straight road in lane the
steering and lateral terms are zero). Then:

  * while `continue` is admissible, Delta G = 0 exactly: the stimulus ego already sits at its
    desired speed with zero effort, nothing is cheaper, and the quantity is SILENT;
  * once `continue` is inadmissible its G is not finite, so the difference is not either, and what
    remains well defined is the other half of it:

        C = min over ADMISSIBLE pi of G_comfort(pi)  -  G_comfort(continue),

    **the comfort price of staying conflict-free**. With a menu of constant decelerations,
    G_comfort rises monotonically with the deceleration, so C is a monotone function of the
    MILDEST ADMISSIBLE DECELERATION a*. Admissibility turns Delta G into a required deceleration,
    measured in nats, against the predictive fan instead of against a worst-case lead;
  * when NO policy is admissible the scene is past anything braking can do (the dread regime) and
    C is set one menu step beyond the hardest policy, and counted.

THE TOLERANCE alpha. A policy is admissible when the share of sampled futures in which it
collides within the horizon is at most alpha. alpha = 0 is the literal reading of "absolute". On a
fan with unbounded support it is also a statement about the SAMPLE: every policy collides in some
future if enough are drawn, so alpha = 0 on n futures means roughly alpha < 1/n. The card reports
that dependence rather than hiding it.

Collision is the released box (`aidriver.preferences.log_collision_pref`): |dy| <= 1.15 width and
|dx| <= 1.15 length, centre to centre in the ego's heading frame.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from aidriver.preferences import PreferenceParams, log_accel_pref, log_speed_pref

from .efe import relative_position
from .policies import EgoPath, ego_rollout
from .predictor import DT_S, HORIZON_S, Futures

A_MAX_RELEASED = 8.0          # m/s^2, `PreferenceParams.a_max`: the hardest policy in the menu
MENU_STEP = 0.25              # m/s^2; fine enough that a* is not a four-level step function,
                              # coarse against the 1 m/s^2 scale on which the cells differ


def brake_menu(a_max: float = A_MAX_RELEASED, step: float = MENU_STEP) -> dict[str, float]:
    """continue (0) and constant decelerations down to -a_max, in steps of `step`."""
    levels = np.arange(0.0, a_max + 1e-9, step)
    return {("continue" if a == 0 else f"brake_{a:.2f}"): -float(a) for a in levels}


def delayed_rollout(belief, a: float, delay_s: float, horizon_s: float = HORIZON_S,
                    dt: float = DT_S) -> EgoPath:
    """Hold speed for `delay_s`, then brake at `a` (speed clipped at zero). delay 0 is
    `ego_rollout`'s constant-acceleration segment."""
    base = ego_rollout(belief, "p", horizon_s, dt, menu={"p": 0.0})
    if a == 0.0 or delay_s >= base.tau[-1]:
        return base
    tau = base.tau
    v0 = float(belief.v_ego)
    tb = np.maximum(tau - delay_s, 0.0)
    t_stop = -v0 / a
    te = np.minimum(tb, t_stop)
    x = v0 * np.minimum(tau, delay_s) + v0 * te + 0.5 * a * te ** 2
    v = np.maximum(v0 + a * te, 0.0)
    acc = np.where((tb > 0) & (tb <= t_stop + 1e-12), a, 0.0)
    zero = np.zeros_like(tau)
    return EgoPath(tau=tau, x=x, y=zero, v=v, a=acc, heading=zero.copy(), y_lane=zero.copy(),
                   name=f"delay{delay_s:g}_a{a:g}")


def collides(ego: EgoPath, fut: Futures, p: PreferenceParams) -> np.ndarray:
    """[n] bool: does the sampled future touch the released collision box at any step?"""
    dx, dy = relative_position(ego, fut)
    veh = p.vehicle
    hit = (np.abs(dy) <= 1.15 * veh.width) & (np.abs(dx) <= 1.15 * veh.length)
    return hit.any(axis=1)


def comfort_cost(ego: EgoPath, p: PreferenceParams) -> float:
    """G_comfort(pi) in nats: the residual information of the speed and control-effort terms,
    summed over the horizon. No conflict term, no braking-margin term: strand 1 has neither as a
    cost. The ego's path is deterministic, so no expectation is needed."""
    top_v = log_speed_pref(np.asarray(p.v_desired, float), p)
    top_a = log_accel_pref(np.asarray(0.0), p)
    res = (top_v - log_speed_pref(ego.v, p)) + (top_a - log_accel_pref(ego.a, p, a_lat=ego.a_lat))
    return float(np.sum(np.maximum(res, 0.0)))


@dataclass
class Admissible:
    a_star: float              # the mildest admissible deceleration [m/s^2 >= 0]; nan if none
    price: float               # C, nats
    none_admissible: bool
    continue_admissible: bool
    p_collide_continue: float  # share of futures in which `continue` collides
    p_collide: dict            # policy -> share


def price_of_safety(belief, fut: Futures, p: PreferenceParams, alpha: float = 0.0,
                    delay_s: float = 0.0, a_max: float = A_MAX_RELEASED,
                    step: float = MENU_STEP, horizon_s: float = HORIZON_S,
                    dt: float = DT_S) -> Admissible:
    """C = min over admissible pi of G_comfort(pi) - G_comfort(continue), and a*."""
    if not 0.0 <= alpha < 1.0:
        raise ValueError("alpha must be in [0, 1)")
    menu = brake_menu(a_max, step)
    paths = {k: delayed_rollout(belief, a, delay_s, horizon_s, dt) for k, a in menu.items()}
    share = {k: float(collides(path, fut, p).mean()) for k, path in paths.items()}
    cost = {k: comfort_cost(path, p) for k, path in paths.items()}
    ok = [k for k in menu if share[k] <= alpha + 1e-12]
    g0 = cost["continue"]
    if not ok:
        beyond = delayed_rollout(belief, -(a_max + step), delay_s, horizon_s, dt)
        return Admissible(a_star=float("nan"), price=comfort_cost(beyond, p) - g0,
                          none_admissible=True, continue_admissible=False,
                          p_collide_continue=share["continue"], p_collide=share)
    best = min(ok, key=lambda k: cost[k])
    return Admissible(a_star=-menu[best], price=cost[best] - g0, none_admissible=False,
                      continue_admissible="continue" in ok,
                      p_collide_continue=share["continue"], p_collide=share)
