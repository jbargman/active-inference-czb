"""Projected conflict between two road users: the scenario-agnostic gate of card PC.1.

Design: `docs/projected_conflict_gate_note.md` (2026-09-16), written before this module. In one
paragraph: each road user's path is projected over a horizon [0, t_enc], the other road user's
always by constant-velocity extrapolation from a velocity window, the ego's either the same way
(reading K) or as its recorded future (reading P); each body is an oriented rectangle and its
corridor is the union of its positions along the projected path; the clearance is the smallest
edge-to-edge distance, over the horizon, between one body and the other's corridor, in either
ordering; the gate is Phi((m - c) / s), card G.1's form, and at the response moment it is the
maximum over the shown clip (persistence). Conflict here means same space, not same time: it is
a path crossing, and whether the two arrive together is what the axis measures.

Everything is computed on the trace's own time grid, in the world frame, with no assumption
about lanes, headings or which road user does what. The ego is whichever track the caller
names, by the scenario's own role rule (the loaders carry those rules; this module never
assigns roles).

Correction before any run (2026-09-16, from the property tests): the corridor is the projected
PATH over an extended span (`T_PATH`, 20 s: longer than any clip's remaining length, 600 m at
30 m/s), while the BODY positions that are tested against the other's corridor run over the
horizon [0, t_enc] only. The first draft bounded both by the horizon, and then a car ahead that
is not caught within the horizon fell outside the ego's corridor, which is not what G.1's gate
(a lane strip unbounded ahead) computes. The asymmetry is the meaning of the horizon: it limits
how far ahead the other road user's MOTION is trusted, not how far the ego's path extends. For the
same reason there is one ordering, by role: the other's positions within the horizon against the
ego's path; the reverse would extrapolate the other's lateral motion for the whole path span.

Reduction (note section 2.4): for a straight ego and a target ahead, closing laterally at a
constant rate, c = l0 + ldot * t_enc, which is the argument of G.1's gate.
`tests/test_conflict.py` checks it numerically.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

T_PATH = 20.0     # s, the span of the path corridor; see the module docstring


# ---------------------------------------------------------------------------------
# geometry: oriented rectangles and the distance between convex polygons
# ---------------------------------------------------------------------------------

def body_polygon(x: float, y: float, heading: float, length: float, width: float) -> np.ndarray:
    """The four corners [4, 2] of a rectangle centred at (x, y), long axis along `heading`."""
    c, s = np.cos(heading), np.sin(heading)
    hl, hw = 0.5 * length, 0.5 * width
    local = np.array([[hl, hw], [hl, -hw], [-hl, -hw], [-hl, hw]])
    rot = np.array([[c, -s], [s, c]])
    return local @ rot.T + np.array([x, y])


def _segments(poly: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return poly, np.roll(poly, -1, axis=0)


def _point_segment_distance(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Distance from points p [n, 2] to segments a->b [m, 2], as an [n, m] array."""
    ab = b - a                                                   # [m, 2]
    ap = p[:, None, :] - a[None, :, :]                           # [n, m, 2]
    denom = np.maximum(np.sum(ab * ab, axis=-1), 1e-12)          # [m]
    t = np.clip(np.sum(ap * ab[None], axis=-1) / denom[None], 0.0, 1.0)
    closest = a[None] + t[..., None] * ab[None]
    return np.linalg.norm(p[:, None, :] - closest, axis=-1)


def _point_in_convex(p: np.ndarray, poly: np.ndarray) -> np.ndarray:
    """Whether each point p [n, 2] lies inside the convex polygon (either winding)."""
    a, b = _segments(poly)
    ab = b - a
    ap = p[:, None, :] - a[None, :, :]
    cross = ab[None, :, 0] * ap[..., 1] - ab[None, :, 1] * ap[..., 0]   # [n, m]
    return np.all(cross >= -1e-9, axis=1) | np.all(cross <= 1e-9, axis=1)


def _segments_intersect(a1, b1, a2, b2) -> bool:
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2 = orient(a1, b1, a2), orient(a1, b1, b2)
    o3, o4 = orient(a2, b2, a1), orient(a2, b2, b1)
    return (o1 * o2 < 0) and (o3 * o4 < 0)


def polygon_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Edge-to-edge distance between two convex polygons; 0 when they touch or overlap.

    For convex polygons the minimum is attained at a vertex of one and an edge of the other,
    unless they overlap (a vertex inside the other, or crossing edges), where it is zero.
    """
    if np.any(_point_in_convex(p, q)) or np.any(_point_in_convex(q, p)):
        return 0.0
    pa, pb = _segments(p)
    qa, qb = _segments(q)
    for i in range(len(pa)):
        for j in range(len(qa)):
            if _segments_intersect(pa[i], pb[i], qa[j], qb[j]):
                return 0.0
    d1 = _point_segment_distance(p, qa, qb).min()
    d2 = _point_segment_distance(q, pa, pb).min()
    return float(min(d1, d2))


# ---------------------------------------------------------------------------------
# projected paths
# ---------------------------------------------------------------------------------

@dataclass
class Body:
    """One road user's world-frame trajectory and dimensions on a uniform time grid."""
    t: np.ndarray
    x: np.ndarray
    y: np.ndarray
    heading: np.ndarray        # rad, world frame
    length: float
    width: float


@dataclass
class ProjectedPath:
    """Positions and headings of a body over a horizon, on the projection grid."""
    tau: np.ndarray            # s from the evaluation moment, tau[0] = 0, up to T_PATH
    x: np.ndarray
    y: np.ndarray
    heading: np.ndarray

    def polygons(self, length: float, width: float, t_max: float | None = None) -> list[np.ndarray]:
        """The body's polygons along the path, all of them (the corridor) or up to t_max (the
        positions within the horizon)."""
        keep = np.ones(len(self.tau), bool) if t_max is None else self.tau <= t_max + 1e-9
        return [body_polygon(xi, yi, hi, length, width)
                for xi, yi, hi, k in zip(self.x, self.y, self.heading, keep) if k]


def _index_at(t: np.ndarray, t_at: float) -> int:
    return int(np.clip(np.searchsorted(t, t_at, side="right") - 1, 0, len(t) - 1))


def kinematic_path(body: Body, t_at: float, v_window: float, dt: float, t_path: float = T_PATH) -> ProjectedPath:
    """Reading K: constant-velocity extrapolation from the velocity over the last `v_window` s,
    over the path span `t_path`.

    The heading of the projected body is the direction of that velocity (the recorded heading
    when the body is stationary), as `surprise.situational._heading_axes` does.
    """
    i = _index_at(body.t, t_at)
    j = _index_at(body.t, t_at - v_window)
    span = float(body.t[i] - body.t[j])
    if span < 0.5 * v_window:
        raise ValueError(f"velocity window {v_window} s not available at t = {t_at} "
                         f"(trace starts at {body.t[0]}); evaluate later or shorten the window")
    vx = (body.x[i] - body.x[j]) / span
    vy = (body.y[i] - body.y[j]) / span
    tau = np.arange(0.0, t_path + 0.5 * dt, dt)
    speed = float(np.hypot(vx, vy))
    head = float(np.arctan2(vy, vx)) if speed > 1e-3 else float(body.heading[i])
    return ProjectedPath(tau=tau, x=body.x[i] + vx * tau, y=body.y[i] + vy * tau,
                         heading=np.full_like(tau, head))


def planned_path(body: Body, t_at: float, dt: float, t_path: float = T_PATH,
                 v_window: float = 1.0) -> ProjectedPath:
    """Reading P: the body's recorded future over the path span, continued past the end of the
    trace at the velocity over its last `v_window` seconds. The heading along the path is the
    direction of the recorded motion, so the traces' heading convention never enters; the
    recorded heading is used only where the body is stationary.

    [2026-09-16, after card PC.1's first run: the continuation took its velocity from the last two
    samples, which on a jittered trace is dominated by the jitter (a 0.004 m lateral step over
    0.033 s is 0.12 m/s, 2.4 m of drift over the path span), and the cut-in's |cK - cP| check
    reached 1.6 m on an ego that drives straight. The velocity is now taken over the same window
    the kinematic reading uses.]"""
    i = _index_at(body.t, t_at)
    tau = np.arange(0.0, t_path + 0.5 * dt, dt)
    tq = body.t[i] + tau
    x, y = np.interp(tq, body.t, body.x), np.interp(tq, body.t, body.y)
    beyond = tq > body.t[-1]
    if np.any(beyond):
        k = _index_at(body.t, body.t[-1] - v_window)
        span = max(float(body.t[-1] - body.t[k]), 1e-9)
        vx_end, vy_end = (body.x[-1] - body.x[k]) / span, (body.y[-1] - body.y[k]) / span
        x = np.where(beyond, body.x[-1] + vx_end * (tq - body.t[-1]), x)
        y = np.where(beyond, body.y[-1] + vy_end * (tq - body.t[-1]), y)
    vx, vy = np.gradient(x, dt), np.gradient(y, dt)
    moving = np.hypot(vx, vy) > 1e-3
    head = np.where(moving, np.arctan2(vy, vx), np.interp(tq, body.t, body.heading))
    return ProjectedPath(tau=tau, x=x, y=y, heading=head)


# ---------------------------------------------------------------------------------
# corridor clearance and the gate
# ---------------------------------------------------------------------------------

def _min_distance(polys_a, centres_a, polys_b, centres_b, r) -> float:
    """Smallest polygon distance over all pairs, pruned by the centre distance: a pair's distance
    is at least the centre distance minus both half-diagonals."""
    centre = np.linalg.norm(centres_a[:, None, :] - centres_b[None, :, :], axis=-1)
    order = np.argsort(centre, axis=None)
    best = np.inf
    for flat in order:
        i, j = divmod(int(flat), len(polys_b))
        if centre[i, j] - r >= best:
            break
        d = polygon_distance(polys_a[i], polys_b[j])
        if d < best:
            best = d
        if best <= 0.0:
            return 0.0
    return float(best)


def corridor_clearance(ego: Body, ego_path: ProjectedPath, other: Body, other_path: ProjectedPath,
                       t_enc: float) -> float:
    """The clearance of the note's section 2.2 (as corrected): the smallest edge-to-edge distance
    between the other road user's body at any time tau in [0, t_enc] and the ego's whole path
    corridor.

    One ordering, by role. The ego's corridor is the union of its polygons along its projected
    path over the path span (where I am going, all the way); the other's positions are trusted
    over the horizon only (where it will be soon). The reverse ordering, the ego's positions
    against the other's extended path, would extrapolate the other's lateral motion far beyond
    the horizon, which is what the horizon exists to prevent, and it is not what G.1 computes;
    the property tests showed it breaking the reduction. Same space, not same time.
    """
    r = 0.5 * (np.hypot(ego.length, ego.width) + np.hypot(other.length, other.width))
    ego_all = ego_path.polygons(ego.length, ego.width)
    oth_hor = other_path.polygons(other.length, other.width, t_max=t_enc)
    ce = np.column_stack([ego_path.x, ego_path.y])
    n_o = len(oth_hor)
    co = np.column_stack([other_path.x[:n_o], other_path.y[:n_o]])
    return _min_distance(oth_hor, co, ego_all, ce, r)


def gate(c, m: float, s: float):
    """Card G.1's form: the probability that the clearance falls below m."""
    return norm.cdf((m - np.asarray(c, float)) / s)


def persistent(values: np.ndarray) -> np.ndarray:
    """The persistence rule: the running maximum over the shown clip."""
    return np.maximum.accumulate(np.asarray(values, float))


def clearance_series(ego: Body, other: Body, times: np.ndarray, reading: str, t_enc: float,
                     v_window: float, dt: float) -> np.ndarray:
    """c at each evaluation moment in `times`, under reading 'K', 'P' or 'KP' (the union:
    the smaller clearance of the two ego readings). The other road user is always K."""
    out = np.empty(len(times))
    for k, t_at in enumerate(times):
        other_path = kinematic_path(other, t_at, v_window, dt)
        cs = []
        if reading in ("K", "KP"):
            cs.append(corridor_clearance(ego, kinematic_path(ego, t_at, v_window, dt), other, other_path, t_enc))
        if reading in ("P", "KP"):
            cs.append(corridor_clearance(ego, planned_path(ego, t_at, dt, v_window=v_window), other, other_path, t_enc))
        out[k] = min(cs)
    return out


def g1_reduction(l0: float, ldot: float, t_enc: float) -> float:
    """The clearance G.1's gate uses: the lateral clearance extrapolated t_enc ahead."""
    return l0 + ldot * t_enc
