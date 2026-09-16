"""
Property tests for the projected-conflict gate (src/comfortzone/conflict.py, card PC.1).

Claims, from docs/projected_conflict_gate_note.md section 5 (as corrected on 2026-09-16): the
polygon distance is exact on known pairs and zero on overlap; the corridor clearance reduces to
card G.1's l0 + ldot * t_enc for a straight ego and a laterally closing target ahead, whether or
not the target is caught within the horizon (section 2.4); c is zero when a body crosses the
other's path within the horizon and positive when the crossing comes later; the two orderings
agree on a symmetric pair; persistence never lowers the gate; a turning planned path opens
against a straight oncoming car while the kinematic reading stays closed (the left-turn
prediction in miniature); a body ahead in the lane is in the corridor however far ahead, and a
body beside the lane is not (the overtake prediction in miniature); the gate is G.1's form; a
velocity window with no data raises rather than projecting a stationary body.

Run: python tests/test_conflict.py
"""
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from comfortzone.conflict import (  # noqa: E402
    Body, body_polygon, clearance_series, corridor_clearance, g1_reduction, gate, kinematic_path,
    persistent, planned_path, polygon_distance,
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def straight(x0, y0, v, t, heading=0.0, length=4.6, width=1.88, vy=0.0):
    return Body(t=t, x=x0 + v * t * np.cos(heading), y=y0 + v * t * np.sin(heading) + vy * t,
                heading=np.full_like(t, heading), length=length, width=width)


def kk(ego, other, t_at, t_enc, vw, dt):
    """Clearance under the kinematic reading for both bodies."""
    return corridor_clearance(ego, kinematic_path(ego, t_at, vw, dt), other,
                              kinematic_path(other, t_at, vw, dt), t_enc)


def main():
    t = np.arange(0.0, 30.0, 0.1)
    DT = 0.1
    T_AT = 1.0        # every evaluation happens at least one velocity window into the trace

    # --- 1 polygon distance ------------------------------------------------------------
    a = body_polygon(0, 0, 0.0, 4.0, 2.0)
    b = body_polygon(10, 0, 0.0, 4.0, 2.0)
    check("polygon distance: two aligned rectangles 10 m apart, edge to edge 6 m",
          abs(polygon_distance(a, b) - 6.0) < 1e-9, f"{polygon_distance(a, b)}")
    c = body_polygon(0, 3.0, 0.0, 4.0, 2.0)
    check("polygon distance: lateral offset 3 m, widths 2 m, clearance 1 m",
          abs(polygon_distance(a, c) - 1.0) < 1e-9)
    d = body_polygon(1.0, 0.5, 0.3, 4.0, 2.0)
    check("polygon distance: overlapping rectangles give 0", polygon_distance(a, d) == 0.0)
    e = body_polygon(0, 0, np.pi / 2, 4.0, 2.0)
    check("polygon distance: crossing rectangles (no vertex inside) give 0",
          polygon_distance(body_polygon(-3, 0, 0.0, 10.0, 0.5), e) == 0.0)
    f = body_polygon(6.0, 6.0, np.pi / 4, 2.0, 2.0)
    check("polygon distance: symmetric in its arguments",
          abs(polygon_distance(a, f) - polygon_distance(f, a)) < 1e-12)

    # --- 2 the reduction to G.1 (note section 2.4) -----------------------------------------
    ego = straight(0.0, 0.0, 20.0, t)
    for l0, ldot in ((1.6, -0.2), (1.0, -0.1), (0.4, -0.05)):
        # target 20 m ahead at the same speed (never caught), closing laterally at ldot
        y_tar = l0 + 0.5 * (1.88 + 1.88)
        tar = Body(t=t, x=20.0 + 20.0 * t, y=y_tar + ldot * t, heading=np.zeros_like(t),
                   length=4.6, width=1.88)
        # an oriented body yawed by atan(ldot / v) protrudes half its length times the sine of
        # that yaw beyond G.1's axis-aligned lateral clearance (0.023 m at ldot -0.2, v 20)
        yaw = 2.3 * abs(np.sin(np.arctan2(ldot, 20.0)))
        for t_enc in (3.0, 5.0):
            c_ours = kk(ego, tar, T_AT, t_enc, 0.3, DT)
            c_g1 = g1_reduction(l0 + ldot * T_AT, ldot, t_enc)
            check(f"reduction to G.1: l0 {l0}, ldot {ldot}, t_enc {t_enc}: c = l0 + ldot t_enc "
                  f"(ours {c_ours:.4f}, G.1 {c_g1:.4f}, yaw protrusion {yaw:.3f})",
                  c_g1 > 0.05 and abs(c_ours - (c_g1 - yaw)) < 0.005)
    # the same with a slower target that IS caught within the horizon: still G.1's value
    tar2 = Body(t=t, x=20.0 + 12.0 * t, y=1.6 + 1.88 - 0.2 * t, heading=np.zeros_like(t),
                length=4.6, width=1.88)
    c2 = kk(ego, tar2, T_AT, 3.0, 0.3, DT)
    yaw2 = 2.3 * abs(np.sin(np.arctan2(-0.2, 12.0)))
    check("reduction to G.1 with the target caught within the horizon (c = 1.4 - 0.6 = 0.8)",
          abs(c2 - (0.8 - yaw2)) < 0.005, f"{c2:.4f}")
    try:
        kinematic_path(ego, 0.0, 0.3, DT)
        check("a velocity window with no data raises", False)
    except ValueError:
        check("a velocity window with no data raises", True)

    # --- 3 crossing within the horizon gives zero; a later crossing gives positive ---------
    ego = straight(0.0, 0.0, 10.0, t)       # at t = 1 the ego is at x = 10
    crosser = Body(t=t, x=np.full_like(t, 25.0), y=-20.0 + 10.0 * t, heading=np.full_like(t, np.pi / 2),
                   length=4.6, width=1.88)   # crosses y = 0 at t = 2, one second into the horizon
    check("a body crossing the ego's path within the horizon gives c = 0",
          kk(ego, crosser, T_AT, 3.0, 0.3, DT) == 0.0)
    late = Body(t=t, x=np.full_like(t, 25.0), y=-50.0 + 10.0 * t, heading=np.full_like(t, np.pi / 2),
                length=4.6, width=1.88)      # crosses y = 0 at t = 5, after the horizon
    c_late = kk(ego, late, T_AT, 3.0, 0.3, DT)
    check("a crossing after the horizon gives c > 0 (motion is trusted only over the horizon)",
          abs(c_late - (10.0 - 0.94 - 2.3)) < 0.02, f"{c_late:.2f}")
    check("the same crossing within a longer horizon gives c = 0", kk(ego, late, T_AT, 6.0, 0.3, DT) == 0.0)
    # same space, not same time: the crosser passes x = 35 at t = 1.5, the ego reaches it at t = 3.5
    later = Body(t=t, x=np.full_like(t, 35.0), y=-15.0 + 10.0 * t, heading=np.full_like(t, np.pi / 2),
                 length=4.6, width=1.88)
    check("a crossing of the ego's path at a different time still gives c = 0",
          kk(ego, later, T_AT, 3.0, 0.3, DT) == 0.0)
    far = Body(t=t, x=np.full_like(t, 150.0), y=-15.0 + 10.0 * t, heading=np.full_like(t, np.pi / 2),
               length=4.6, width=1.88)
    check("a crossing of the ego's path far ahead (within the path span) still gives c = 0",
          kk(ego, far, T_AT, 3.0, 0.3, DT) == 0.0)

    # --- 4 the roles: parallel bodies give the same clearance from either seat; a body whose
    #       lateral motion would cross the ego's path only after the horizon does not count ------
    b1 = straight(0.0, 0.0, 10.0, t)
    b2 = straight(0.0, 5.0, 10.0, t)
    c12 = kk(b1, b2, T_AT, 3.0, 0.3, DT)
    c21 = kk(b2, b1, T_AT, 3.0, 0.3, DT)
    check("parallel bodies 5 m apart: clearance 3.12 m from either seat",
          abs(c12 - c21) < 1e-9 and abs(c12 - (5.0 - 1.88)) < 1e-6, f"{c12:.4f} {c21:.4f}")
    drifter = Body(t=t, x=30.0 + 10.0 * t, y=5.0 - 0.2 * t, heading=np.zeros_like(t), length=4.6, width=1.88)
    c_dr = kk(b1, drifter, T_AT, 3.0, 0.3, DT)
    check("a body ahead drifting toward the ego's path, but not reaching it within the horizon, keeps its "
          "clearance at the horizon end (the reverse ordering would have made it 0)",
          abs(c_dr - (5.0 - 0.2 * 4.0 - 1.88 - 2.3 * abs(np.sin(np.arctan2(-0.2, 10.0))))) < 0.005, f"{c_dr:.3f}")

    # --- 5 persistence and the gate --------------------------------------------------------
    g = gate(np.array([2.0, 0.0, 1.0, 3.0]), 0.15, 0.99)
    check("gate is G.1's form Phi((m - c)/s)",
          np.allclose(g, norm.cdf((0.15 - np.array([2.0, 0.0, 1.0, 3.0])) / 0.99)))
    check("persistence is the running maximum and never lowers the gate",
          np.allclose(persistent(g), [g[0], g[1], g[1], g[1]]) and np.all(persistent(g) >= g))

    # --- 6 the left turn in miniature: P opens, K stays closed ------------------------------
    # the ego drives along +x in the right lane (y = 0), and at t = 10 s turns left across the
    # oncoming lane (y = 3.5); the oncoming car drives along -x in that lane
    turn_t = 10.0
    ph = np.clip((t - turn_t) / 2.0, 0, np.pi / 2)
    x_e = np.where(t < turn_t, 5.0 * t, 5.0 * turn_t + np.sin(ph) * 2.0 / np.pi * 6.0)
    y_e = np.where(t < turn_t, 0.0, (1 - np.cos(ph)) * 8.0)
    ego_lt = Body(t=t, x=x_e, y=y_e, heading=np.zeros_like(t), length=4.6, width=1.88)
    onc = Body(t=t, x=200.0 - 14.0 * t, y=np.full_like(t, 3.5), heading=np.full_like(t, np.pi),
               length=4.6, width=1.88)
    t_dec = 9.6
    onc_path = kinematic_path(onc, t_dec, 1.0, DT)
    cK = corridor_clearance(ego_lt, kinematic_path(ego_lt, t_dec, 1.0, DT), onc, onc_path, 3.0)
    cP = corridor_clearance(ego_lt, planned_path(ego_lt, t_dec, DT), onc, onc_path, 3.0)
    check("left turn in miniature: the kinematic reading stays closed before the turn (c > m)",
          cK > 1.0, f"cK {cK:.3f}")
    check("left turn in miniature: the planned reading opens (c = 0) because the ego crosses the oncoming lane",
          cP == 0.0, f"cP {cP:.3f}")
    ser = clearance_series(ego_lt, onc, np.array([t_dec]), "KP", 3.0, 1.0, DT)
    check("the union takes the smaller clearance", ser[0] == min(cK, cP))

    # --- 7 the overtake in miniature: a body ahead in the lane is in the path ------------------
    ego_ov = straight(0.0, 0.0, 14.0, t)
    cyc = Body(t=t, x=20.0 + 5.0 * t, y=np.full_like(t, 0.3), heading=np.zeros_like(t), length=1.8, width=0.58)
    check("overtake in miniature: a cyclist 11 m ahead in the lane is in the ego's path, c = 0",
          kk(ego_ov, cyc, T_AT, 3.0, 1.0, DT) == 0.0)
    cyc_far = Body(t=t, x=90.0 + 5.0 * t, y=np.full_like(t, 0.3), heading=np.zeros_like(t), length=1.8, width=0.58)
    check("overtake in miniature: a cyclist 81 m ahead in the lane is still in the path, c = 0",
          kk(ego_ov, cyc_far, T_AT, 3.0, 1.0, DT) == 0.0)
    cyc_side = Body(t=t, x=20.0 + 5.0 * t, y=np.full_like(t, 3.0), heading=np.zeros_like(t), length=1.8, width=0.58)
    c_side = kk(ego_ov, cyc_side, T_AT, 3.0, 1.0, DT)
    check("overtake in miniature: a cyclist beside the path has the lateral edge clearance (1.77 m)",
          abs(c_side - (3.0 - 0.94 - 0.29)) < 0.02, f"{c_side:.3f}")

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    main()
