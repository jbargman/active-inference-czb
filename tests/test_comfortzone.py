"""
Tests for the comfort-zone module and the SI-faithful preference function.

The important one is `test_closed_form_matches_field`: the analytic critical gap and the
numeric level set of the deficit field are two independent routes to the same boundary, so
they must agree. A sign error in the closed form was caught exactly this way.

Run:  python tests/test_comfortzone.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from aidriver import PreferenceParams  # noqa: E402
from aidriver.preferences import (  # noqa: E402
    apply_running_min, log_lateral_pref, log_preference_terms, pragmatic_deficit,
    required_deceleration, safety_margin,
)
from comfortzone import (  # noqa: E402
    boundary_curve, comfort_field, critical_gap, critical_thw, dread_zone_boundary,
)
from comfortzone.calibrate import (  # noqa: E402
    calibrate_level, deficit_along_trajectory, exceedance_events,
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if bool(cond) else FAIL).append(name)
    detail = "" if detail == "" else str(detail)
    print(f"{'PASS' if bool(cond) else 'FAIL'}  {name}{('  -- ' + detail) if detail else ''}")


def obs(dx, v=15.0, vo=15.0, y=0.0, a=0.0, ao=0.0):
    return {"v": np.array([v]), "a": np.array([a]), "omega": np.array([0.0]),
            "y": np.array([y]), "dx": np.array([float(dx)]), "dy": np.array([0.0]),
            "v_other": np.array([vo]), "a_other": np.array([ao]),
            "theta": np.array([0.0]), "theta_other": np.array([0.0])}


# --------------------------------------------------------------- preference function
def test_preference_shape():
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)

    lat_centre = float(np.ravel(log_lateral_pref(0.0, p))[0])
    check("lane-keeping cost is exactly zero at the lane centre", abs(lat_centre) < 1e-12)

    edge = (p.lane_width - p.vehicle.width) / 2.0
    lat_edge = float(np.ravel(log_lateral_pref(edge, p))[0])
    check("lane-keeping cost equals g_LC at the lane edge (triangular, SI Eq. 46)",
          abs(lat_edge - p.g_lane_boundary) < 1e-9, f"{lat_edge:.1f} vs {p.g_lane_boundary}")

    # SI Eq. 52 makes y_rel *lane structured*: in the front-to-rear scenario both lanes run
    # the same way, so sitting in the centre of the adjacent lane is also cost-free, and
    # g_LL only applies once |y_rel| exceeds the half-lane width again.
    lat_adj = float(np.ravel(log_lateral_pref(p.lane_width, p))[0])
    check("lane-keeping cost returns to zero at the adjacent lane centre (SI Eq. 52)",
          abs(lat_adj) < 1e-9, f"{lat_adj:.3f}")
    y_off = p.lane_width + (p.lane_width - p.vehicle.width) / 2.0 + 0.5
    lat_off = float(np.ravel(log_lateral_pref(y_off, p))[0])
    check("off-road cost saturates at g_LL beyond the last lane",
          abs(lat_off - p.g_leave_road) < 1e-9, f"{lat_off:.1f} at y={y_off:.2f}")

    # free driving with no vehicle ahead: every factor is at its maximum
    o_free = obs(-500.0)          # other vehicle behind -> p_coll factor is 1
    d_free = float(np.ravel(pragmatic_deficit(o_free, p))[0])
    check("deficit is exactly 0 in free driving with no vehicle ahead", d_free < 1e-9,
          f"{d_free:.3e}")

    # The tau^-1 term. The released code (reward.py:272) clamps tau^-1 to at least 0.2 s^-1
    # before the Gaussian, so steady following (tau^-1 = 0) costs nothing; the SI's
    # symmetric form leaves a constant residual 0.5 (mu/sd)^2 = 1.28 whenever a vehicle is
    # ahead. Both forms are kept (docs/method_review.md section 5, item 2); the default is
    # the code's.
    d_ahead = float(np.ravel(pragmatic_deficit(obs(1e4), p))[0])
    check("[code form] a vehicle far ahead at equal speed costs exactly zero",
          d_ahead < 1e-9, f"{d_ahead:.3e}")
    d_follow = float(np.ravel(pragmatic_deficit(obs(26.7), p))[0])
    check("[code form] steady following inside the margin has zero deficit",
          d_follow < 1e-9, f"{d_follow:.3e}")
    from aidriver.preferences import log_preference_terms
    o_close = obs(26.7, v=18.0)          # closing at 3 m/s over ~22.5 m: tau^-1 = 0.13
    c_close = float(np.ravel(log_preference_terms(o_close, p)["collision"])[0])
    check("[code form] closing slower than TTC 5 s costs nothing in the tau^-1 term",
          abs(c_close) < 1e-9, f"{c_close:.3e}")
    o_fast = obs(26.7, v=23.0)           # closing at 8 m/s: tau^-1 = 0.36 > 0.2
    c_fast = float(np.ravel(log_preference_terms(o_fast, p)["collision"])[0])
    check("[code form] closing faster than TTC 5 s is penalised in the tau^-1 term",
          c_fast < -1e-3, f"{c_fast:.3f}")

    p_si = p.si_variant()
    expected = 0.5 * (p_si.tau_inv_mu / p_si.tau_inv_sd) ** 2
    d_si = float(np.ravel(pragmatic_deficit(obs(26.7), p_si))[0])
    check("[SI form] steady following leaves the constant tau^-1 residual 1.28",
          abs(d_si - expected) < 1e-6, f"{d_si:.3f} vs {expected:.3f}")
    check("[SI form] g_LL is the SI's -5000; code form uses Table 1's -15000",
          p_si.g_leave_road == -5000.0 and p.g_leave_road == -15000.0)

    # control-effort term, released-code form: positive a doubled, total acceleration
    from aidriver.preferences import log_accel_pref
    la_neg = float(log_accel_pref(-1.0, p)); la_pos = float(log_accel_pref(1.0, p))
    check("[code form] +1 m/s^2 costs as much as -2 m/s^2 (positive accel doubled)",
          abs(la_pos - float(log_accel_pref(-2.0, p))) < 1e-12 and la_pos < la_neg)
    la_lat = float(log_accel_pref(0.0, p, a_lat=1.0))
    check("[code form] lateral acceleration enters the effort term",
          abs(la_lat - la_neg) < 1e-12, f"{la_lat:.3f} vs {la_neg:.3f}")
    check("[SI form] effort term is N(a_long | 0, sigma_a) only",
          abs(float(log_accel_pref(1.0, p_si)) - float(log_accel_pref(-1.0, p_si))) < 1e-12
          and abs(float(log_accel_pref(0.0, p_si, a_lat=1.0)) - float(log_accel_pref(0.0, p_si))) < 1e-12)


def test_running_min():
    x = np.array([[0.0, -5.0, 0.0, 0.0]])
    out = apply_running_min(x, axis=-1)
    check("collision penalty persists after the collision timestep (SI Eq. 47)",
          np.allclose(out, [[0, -5, -5, -5]]), out.tolist())


# ------------------------------------------------------------------ boundary geometry
def test_required_deceleration_monotone():
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    dxs = np.array([12.0, 15.0, 20.0, 30.0, 60.0])
    a_req = np.array([float(np.ravel(required_deceleration(obs(d), p))[0]) for d in dxs])
    check("required deceleration eases as the gap grows", np.all(np.diff(a_req) > 0),
          np.round(a_req, 2).tolist())
    m = np.array([float(np.ravel(safety_margin(obs(d), p))[0]) for d in dxs])
    check("safety margin increases with gap and changes sign",
          np.all(np.diff(m) > 0) and m[0] < 0 < m[-1], np.round(m, 2).tolist())


def test_closed_form_matches_field():
    """
    The analytic boundary and the numeric zero-crossing of the margin field must coincide.
    """
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    v = np.linspace(8, 30, 45)
    dx = np.linspace(1, 120, 1200)
    f = comfort_field(p, "v", v, "dx", dx, couple={"v_other": "v"})

    numeric = dread_zone_boundary(f)[:, 1]
    analytic = critical_gap(v, v, p)          # default a_required = a_max
    ok = np.isfinite(numeric)
    err = np.max(np.abs(numeric[ok] - analytic[ok]))
    check("closed-form critical gap matches the numeric margin level set",
          err < 0.2, f"max abs error {err:.3f} m over {ok.sum()} speeds")


def test_thw_values_are_plausible():
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    thw_limit = float(critical_thw(15.0, 15.0, p, a_required=8.0))
    thw_comfort = float(critical_thw(15.0, 15.0, p, a_required=4.0))
    check("critical THW at the physical braking limit is well under 1 s",
          0.3 < thw_limit < 1.0, f"{thw_limit:.2f} s")
    check("critical THW at comfortable braking is in the observed CZB range (1-2.5 s)",
          1.0 < thw_comfort < 2.5, f"{thw_comfort:.2f} s")
    check("a comfort boundary is more conservative than a dread boundary",
          thw_comfort > thw_limit)

    # when the assumed lead deceleration equals the required limit, THW* -> t_react
    p2 = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    thws = [float(critical_thw(v, v, p2, a_required=6.0)) for v in [10, 20, 30]]
    check("THW* is ~t_react and speed-invariant when a_OV,min equals the braking limit",
          max(thws) - min(thws) < 0.1 and abs(np.mean(thws) - p2.response_time) < 0.15,
          np.round(thws, 3).tolist())


def test_extra_motives_shrink_the_zone():
    """
    'Extra motives' should enter as a change to the *preference*, not the physics, and should
    shrink the comfort zone (accept smaller margins).
    """
    calm = PreferenceParams(v_desired=15.0, a_other_min=-6.0, response_time=1.0)
    hurried = PreferenceParams(v_desired=15.0, a_other_min=-6.0, response_time=0.6)
    thw_calm = float(critical_thw(15.0, 15.0, calm, a_required=4.0))
    thw_hurry = float(critical_thw(15.0, 15.0, hurried, a_required=4.0))
    check("a shorter assumed reaction time shrinks the comfort zone",
          thw_hurry < thw_calm, f"{thw_hurry:.2f} < {thw_calm:.2f}")

    trusting = PreferenceParams(v_desired=15.0, a_other_min=-3.0)
    thw_trust = float(critical_thw(15.0, 15.0, trusting, a_required=4.0))
    check("assuming the lead brakes less hard also shrinks the comfort zone",
          thw_trust < thw_calm, f"{thw_trust:.2f} < {thw_calm:.2f}")


# --------------------------------------------------------------------- field / calib
def test_field_shapes_and_monotonicity():
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    v = np.linspace(10, 25, 20)
    dx = np.linspace(5, 80, 60)
    f = comfort_field(p, "v", v, "dx", dx, couple={"v_other": "v"})
    check("field has the expected shape", f.deficit.shape == (len(dx), len(v)),
          f.deficit.shape)
    check("deficit is non-negative everywhere", np.all(f.deficit >= 0))
    col = f.deficit[:, len(v) // 2]
    check("deficit decreases with increasing gap", col[0] > col[-1],
          f"{col[0]:.1f} -> {col[-1]:.1f}")
    check("all six preference terms are exposed for attribution",
          set(f.terms) == {"speed", "accel", "steer", "lateral", "collision", "safety"},
          sorted(f.terms))


def test_exceedance_and_calibration():
    eps = np.array([0, 0, 0, 1, 1, 200, 300, 5, 0, 0, 400, 10], dtype=float)
    ex = exceedance_events(eps, level=100.0)
    check("exceedance detection finds upward crossings", list(ex) == [5, 10], list(ex))
    ex2 = exceedance_events(eps, level=100.0, min_separation=8)
    check("min_separation merges nearby crossings", list(ex2) == [5], list(ex2))

    # synthetic calibration: onsets 2 samples after eps crosses 100
    rng = np.random.default_rng(0)
    series, onsets = [], []
    for _ in range(30):
        s = np.zeros(40)
        k = rng.integers(8, 25)
        s[k:] = 500.0
        series.append(s)
        onsets.append(k + 2)
    res = calibrate_level(series, onsets, tolerance=3)
    check("calibration recovers a level that reproduces the onsets", res.score > 0.9,
          repr(res))


def test_trajectory_evaluation():
    p = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    T = 40
    dt = p.vehicle.dt
    ego = np.zeros((T, 5)); other = np.zeros((T, 5))
    ego[:, 4] = 15.0
    other[:, 4] = 15.0
    ego[:, 0] = np.arange(T) * 15.0 * dt
    other[:, 0] = ego[:, 0] + 40.0
    # lead decelerates from halfway
    for t in range(T // 2, T):
        other[t, 4] = max(15.0 - 6.0 * (t - T // 2) * dt, 0.0)
        other[t, 0] = other[t - 1, 0] + other[t, 4] * dt
    eps = deficit_along_trajectory(ego, other, p)
    check("trajectory deficit is finite and non-negative",
          np.all(np.isfinite(eps)) and np.all(eps >= 0))
    check("trajectory deficit rises after the lead brakes",
          eps[-1] > eps[0], f"{eps[0]:.2f} -> {eps[-1]:.2f}")


if __name__ == "__main__":
    for fn in [test_preference_shape, test_running_min,
               test_required_deceleration_monotone, test_closed_form_matches_field,
               test_thw_values_are_plausible, test_extra_motives_shrink_the_zone,
               test_field_shapes_and_monotonicity, test_exceedance_and_calibration,
               test_trajectory_evaluation]:
        print(f"\n--- {fn.__name__} ---")
        fn()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED:", FAIL)
    sys.exit(1 if FAIL else 0)
