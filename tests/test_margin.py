"""
Property tests for the demanded deceleration (src/comfortzone/margin.py, card S1.5).

Claims: with no standoff the "stops" counterfactual IS the released `required_deceleration`
(sign flipped); at one lead speed the assumed lead braking and the standoff are the same
parameter; the demand grows as the gap shrinks, as the standoff grows and as the reaction time
grows; it is infinite exactly when no room is left; the "holds" counterfactual is zero when the
ego is not closing, reduces to dv^2 / (2 net gap) with no reaction time, and never exceeds the
"stops" demand's wall limit; the "stops" demand tends to that wall limit as the assumed lead
braking hardens.

Run: python tests/test_margin.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidriver.preferences import PreferenceParams, required_deceleration  # noqa: E402
from comfortzone.margin import (  # noqa: E402
    RELEASED_CLEARANCE, RELEASED_LENGTH_M, demanded_deceleration, equivalent_standoff,
    lead_stopping_credit,
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def main():
    rng = np.random.default_rng(0)
    n = 2000
    dx = rng.uniform(6.0, 120.0, n)
    v = rng.uniform(5.0, 40.0, n)
    vl = rng.uniform(0.0, 40.0, n)
    a = rng.uniform(-3.0, 1.0, n)
    ao = rng.uniform(-8.0, 1.0, n)

    # --- 1 the released function, exactly ------------------------------------------------
    p = PreferenceParams()
    check("the released vehicle length is the module's constant",
          abs(p.vehicle.length - RELEASED_LENGTH_M) < 1e-12, f"{p.vehicle.length}")
    for a_ov, t_r in ((-6.0, 1.0), (-10.0, 0.5), (-4.0, 2.0)):
        pp = PreferenceParams(a_other_min=a_ov, response_time=t_r)
        obs = {"v": v, "a": a, "dx": dx, "v_other": vl, "a_other": np.zeros(n)}
        rel = -np.asarray(required_deceleration(obs, pp), float)
        mine = demanded_deceleration(dx, v, vl, lead="stops", a_lead=a_ov, t_react=t_r,
                                     standoff=0.0, a_ego=a)
        same = np.where(np.isfinite(rel), np.isclose(rel, mine, rtol=1e-12, atol=1e-12),
                        ~np.isfinite(mine))
        check(f"standoff 0 is the released required_deceleration (a_OV {a_ov:g}, t {t_r:g})",
              bool(np.all(same[v + np.minimum(a, 0) * t_r > 0])),
              f"max abs diff {np.max(np.abs(rel[np.isfinite(rel)] - mine[np.isfinite(rel)])):.2e}")
    # the released function lets a_other below a_other_min harden the test; this module takes the
    # assumed braking as given, so the two agree only while the lead is not already braking harder
    obs = {"v": v, "a": a, "dx": dx, "v_other": vl, "a_other": ao}
    rel = -np.asarray(required_deceleration(obs, p), float)
    mine = demanded_deceleration(dx, v, vl, a_lead=-6.0, a_ego=a)
    soft = ao >= -6.0
    check("agreement holds wherever the lead is not already braking harder than a_lead",
          bool(np.all(np.isclose(rel[soft], mine[soft]) | ~np.isfinite(rel[soft]))))

    # --- 2 the identity: assumed lead braking == standoff at one lead speed ----------------
    v1 = 24.98
    s_eq = equivalent_standoff(v1, -6.0, -10.0)
    check("equivalent standoff of -10 at -6 for a 24.98 m/s lead is 20.80 m",
          abs(s_eq - (v1 ** 2 / 12.0 - v1 ** 2 / 20.0)) < 1e-12 and abs(s_eq - 20.80) < 0.01,
          f"{s_eq:.3f} m")
    d_a = demanded_deceleration(dx, v, v1, a_lead=-10.0, standoff=0.0)
    d_b = demanded_deceleration(dx, v, v1, a_lead=-6.0, standoff=s_eq)
    fin = np.isfinite(d_a)
    check("(-10, no standoff) and (-6, equivalent standoff) give the same demand, cell by cell",
          bool(np.all(np.isfinite(d_b) == fin) and np.allclose(d_a[fin], d_b[fin], rtol=1e-10)))
    d_c = demanded_deceleration(dx, v, vl, a_lead=-6.0, standoff=s_eq)
    d_d = demanded_deceleration(dx, v, vl, a_lead=-10.0, standoff=0.0)
    both = np.isfinite(d_c) & np.isfinite(d_d)
    check("the identity FAILS when lead speeds differ (it is a property of the design, not of"
          " the formula)", not np.allclose(d_c[both], d_d[both], rtol=1e-3))
    check("the stopping credit is v^2 / (2 |a|)",
          np.isclose(lead_stopping_credit(30.0, -6.0), 75.0))

    # --- 3 monotone in the three things a driver could vary --------------------------------
    for kw in ({"lead": "stops"}, {"lead": "holds"}):
        base = demanded_deceleration(dx, v, vl, **kw)
        nearer = demanded_deceleration(dx - 1.0, v, vl, **kw)
        further_out = demanded_deceleration(dx, v, vl, standoff=3.0, **kw)
        slower = demanded_deceleration(dx, v, vl, t_react=1.5, **kw)
        ok = lambda hi, lo: bool(np.all((hi >= lo) | ~np.isfinite(lo)))  # noqa: E731
        check(f"{kw['lead']}: a smaller gap never lowers the demand", ok(nearer, base))
        check(f"{kw['lead']}: a larger standoff never lowers the demand", ok(further_out, base))
        check(f"{kw['lead']}: a longer reaction time never lowers the demand", ok(slower, base))
        check(f"{kw['lead']}: the demand is never negative", bool(np.all(base >= 0)))

    # --- 4 no room left -------------------------------------------------------------------
    room = 1.15 * RELEASED_LENGTH_M
    check("holds: infinite exactly when the net gap after the reaction is gone",
          np.isinf(demanded_deceleration(room + 10.0, 30.0, 20.0, lead="holds", t_react=1.0))
          and np.isfinite(demanded_deceleration(room + 10.01, 30.0, 20.0, lead="holds",
                                                t_react=1.0)))
    check("stops: infinite when the stopping point is already behind the ego",
          np.isinf(demanded_deceleration(5.0, 30.0, 0.0, lead="stops", t_react=1.0)))

    # --- 5 the holds counterfactual ---------------------------------------------------------
    check("holds: zero when the ego is not closing",
          bool(np.all(demanded_deceleration(dx, np.minimum(v, vl), vl, lead="holds") == 0)))
    gap_net = 30.0
    got = demanded_deceleration(gap_net + room, 30.0, 22.0, lead="holds", t_react=0.0)
    check("holds: dv^2 / (2 net gap) with no reaction time",
          np.isclose(got, 8.0 ** 2 / (2 * gap_net)), f"{float(got):.4f}")
    check("RELEASED_CLEARANCE is the released 1.15", RELEASED_CLEARANCE == 1.15)

    # --- 6 the wall limit -------------------------------------------------------------------
    wall = 0.5 * v ** 2 / np.maximum(dx - v * 1.0 - room, 1e-12)
    wall = np.where(dx - v * 1.0 - room > 0, wall, np.inf)
    hard = demanded_deceleration(dx, v, vl, a_lead=-1e9)
    fin = np.isfinite(wall)
    roomy = dx - v * 1.0 - room > 1.0     # away from the pole, where a 1e-6 m credit is visible
    check("stops: as the assumed lead braking hardens the demand tends to the wall's",
          bool(np.allclose(hard[roomy], wall[roomy], rtol=1e-6)))
    holds = demanded_deceleration(dx, v, vl, lead="holds")
    check("holds never demands more than stopping behind a wall at the lead's position",
          bool(np.all((holds <= wall + 1e-9) | ~fin)))

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
