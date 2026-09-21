"""The demanded deceleration: the braking-margin quantity read as a comfort margin (card S1.5).

Jonas, 2026-09-22, of the released braking-margin term: *"if it was fitted with a different
maximum decel and a position a bit further out, it could be CZB, or?"* The released term
(`aidriver.preferences.required_deceleration`, SI Eq. 51) asks what deceleration the ego would
need, after a reaction time, to stop short of where the lead ends up if the lead braked at
`a_other_min`; it then thresholds that at the ego's PHYSICAL maximum. This module computes the
same quantity with the two things he names made explicit, and nothing else changed:

  **a standoff** [m]   "a position a bit further out": the ego must stop `standoff` short of the
                       released stopping point (which already keeps 1.15 vehicle lengths centre to
                       centre). standoff = 0 is the released function exactly (property test 1).
  **the threshold**    is NOT in this module. It is the level of the threshold model every axis in
                       this project is given, so it is fitted, in m/s^2, and can be read against
                       what a comfortable deceleration is. That reading is card S1.5's rule 2.

Two counterfactuals about the lead, because the level can only be read as a COMFORTABLE
deceleration if the counterfactual is one a driver would hold in ordinary driving:

  `lead="stops"`   the released one: the lead brakes at `a_lead` < 0 to a standstill and the ego
                   must stop behind it. Demand = v_react^2 / (2 d_avail), with
                   d_avail = dx + v_lead^2 / (2 |a_lead|) - v t - 0.5 a t^2 - 1.15 L - standoff.
  `lead="holds"`   the lead keeps its speed and the ego must only MATCH it, `standoff` short of
                   contact. Demand = dv_react^2 / (2 d_avail) with dv the closing speed and
                   d_avail = dx - dv t - 1.15 L - standoff; zero when not closing.

Both return a non-negative magnitude in m/s^2, `inf` when there is no room left. Distances are
centre to centre, as in the released function; L is the released vehicle length lf + lr.

A NOTE ON THE RELEASED FORMULA, for whoever reads the level in m/s^2. Comparing final stopping
positions is sufficient only while the ego brakes no harder than the lead. When the demand
exceeds |a_lead| the two speeds equalise BEFORE the lead stops and the smallest gap occurs then,
so the stopping-point criterion is not conservative there. `lead="stops"` reproduces the released
formula regardless, because the card's question is about that formula; the observation is
recorded in the card's report, not corrected here.

An identity the card rests on (property test 2): under `lead="stops"` the lead's stopping
distance enters only as the constant v_lead^2 / (2 |a_lead|), so on any set of scenes that share
ONE lead speed, the assumed lead braking and the standoff are the same parameter:

    (a_lead, standoff)  ==  (a_lead', standoff')   whenever
    v_lead^2 / (2 |a_lead|) - standoff  =  v_lead^2 / (2 |a_lead'|) - standoff'.
"""
from __future__ import annotations

import numpy as np

RELEASED_LENGTH_M = 4.2      # lf + lr of `aidriver` BicycleParams (2.1 + 2.1), the released body
RELEASED_CLEARANCE = 1.15    # the released stopping point: 1.15 vehicle lengths centre to centre


def lead_stopping_credit(v_lead, a_lead: float):
    """v_lead^2 / (2 |a_lead|): how far the counterfactual lead travels before it stands still."""
    if a_lead >= 0:
        raise ValueError("a_lead must be negative under lead='stops'")
    return np.asarray(v_lead, float) ** 2 / (2.0 * abs(a_lead))


def equivalent_standoff(v_lead: float, a_lead: float, a_lead_other: float) -> float:
    """The standoff at `a_lead` that reproduces `a_lead_other` with no standoff, at ONE lead speed."""
    return float(lead_stopping_credit(v_lead, a_lead) - lead_stopping_credit(v_lead, a_lead_other))


def demanded_deceleration(dx, v_ego, v_lead, *, lead: str = "stops", a_lead: float = -6.0,
                          t_react: float = 1.0, standoff: float = 0.0, a_ego=0.0,
                          length: float = RELEASED_LENGTH_M):
    """The deceleration the situation demands [m/s^2, >= 0; inf when no room is left].

    dx is x_lead - x_ego centre to centre [m]; a_ego enters only when negative, as in the
    released function (the ego's current braking carries through its reaction time).
    """
    dx = np.asarray(dx, float)
    v = np.asarray(v_ego, float)
    vl = np.asarray(v_lead, float)
    a = np.minimum(np.asarray(a_ego, float), 0.0)
    if standoff < 0 or t_react < 0:
        raise ValueError("standoff and t_react must be non-negative")
    v_react = np.maximum(v + a * t_react, 0.0)
    travelled = v * t_react + 0.5 * a * t_react ** 2
    if lead == "stops":
        d_avail = dx + lead_stopping_credit(vl, a_lead) - travelled
        speed_to_lose = v_react
    elif lead == "holds":
        d_avail = dx + vl * t_react - travelled
        speed_to_lose = np.maximum(v_react - vl, 0.0)
    else:
        raise ValueError(f"lead must be 'stops' or 'holds', not {lead!r}")
    d_avail = d_avail - RELEASED_CLEARANCE * length - standoff
    with np.errstate(divide="ignore", invalid="ignore"):
        demand = 0.5 * speed_to_lose ** 2 / d_avail
    demand = np.where(d_avail > 0, demand, np.inf)
    return np.where(speed_to_lose > 0, demand, 0.0)
