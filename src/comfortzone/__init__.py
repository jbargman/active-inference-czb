"""
comfortzone -- establishing driver comfort-zone boundaries from an active-inference
preference function.

The idea
--------
In traffic psychology (Naatanen & Summala's zero-risk theory; Ljung Aust & Engstrom; the
Chalmers LTAP/OD and pedestrian-overtaking work) the *comfort zone* is a dynamic
spatiotemporal envelope around the vehicle inside which the driver feels comfortable. The
*comfort-zone boundary* (CZB) is the limit drivers do not cross voluntarily without extra
motives; the *dread-zone boundary* is the further limit they do not cross even with them.
These are normally quantified per scenario, in terms of a chosen kinematic indicator
(minimum TTC, THW, lateral clearance).

Active inference offers a scenario-independent alternative. The driver's preference function
p(o) already encodes what states the driver wants to be in, and

    eps(o) = max_o' log p(o')  -  log p(o)     >= 0

is exactly zero at the preferred observation and grows as the situation departs from it
(residual information; Dinparastdjadid et al. 2023). So:

    the comfort zone       = { x : eps(x) <= c }
    the comfort-zone bdry  = { x : eps(x) =  c }      a *level set* of a scalar field
    the dread zone         = states from which no policy restores preferred observations

The kinematic indicators used in the classical literature then become *projections* of this
one surface, which is a principled explanation of why they differ between scenarios.

Three ways to get a boundary, in increasing generality:

  1. `critical_gap` / `critical_thw` -- closed form. Schumann et al.'s own p_safe term is an
     indicator on `a_ego,req < -a_max`; solving that equality gives the boundary analytically.
     Exact, instant, and directly interpretable, but specific to car-following geometry.
  2. `boundary_level_set` -- numeric contour of the eps field on any 2-D slice of the state
     space. General; handles lateral position, headings, multiple preference terms at once.
  3. `calibrate_level` -- fit the threshold c to observed human behaviour, so the boundary is
     empirically anchored rather than assumed.

See `notes/04_comfort_zone_method.md` for the method write-up.
"""
from .field import (
    INTERACTION_TERMS,
    ComfortField,
    comfort_field,
    critical_gap,
    critical_thw,
    margin_field,
)
from .boundary import (
    boundary_level_set,
    boundary_curve,
    dread_zone_boundary,
)
from .calibrate import (
    calibrate_level,
    exceedance_events,
)

__all__ = [
    "INTERACTION_TERMS", "ComfortField", "comfort_field", "critical_gap", "critical_thw", "margin_field",
    "boundary_level_set", "boundary_curve", "dread_zone_boundary",
    "calibrate_level", "exceedance_events",
]
