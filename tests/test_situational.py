"""
Property tests for situational surprise (src/surprise/situational.py, card HS.1).

The claims tested, rather than "the code runs":

* steady motion is not surprising under any reference;
* onset latency follows the closed forms -- z*sigma/dv after a velocity step and
  sqrt(2*z*sigma/a) after a constant acceleration -- and a change that cannot leave the
  predicted band within one horizon never registers (two routes: analytic against numeric);
* the three references monitor what they say they monitor -- `world` is blind to the ego's
  own manoeuvre, `joint` sees it, `relative` sees it through the changing configuration;
* `joint` and `relative` differ exactly where they should: two vehicles swerving in
  parallel are jointly surprising and relatively unremarkable;
* the scene's placement and orientation in the world do not change anything;
* a longitudinal event shows on the longitudinal axis, a lateral one on the lateral axis.

The first version of these tests (2026-09-13) used card Q5.1's spread settings and failed
five checks; the failures were the property recorded in the module docstring, not bugs, and
the tests now state it as a claim.

Run: python tests/test_situational.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from surprise.situational import (  # noqa: E402
    PredictorSettings, Track, cv_standardized_error, onset_time, situational_surprise,
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


DT = 0.02
T = np.arange(0, 12, DT)


def straight(v=20.0, y0=0.0, x0=0.0):
    return Track(T, x0 + v * T, np.full_like(T, y0))


def swerve(t_s=5.0, vy=1.0, v=20.0, y0=0.0, x0=0.0):
    """Constant forward speed; a step to lateral speed vy at t_s."""
    y = y0 + np.where(T > t_s, vy * (T - t_s), 0.0)
    return Track(T, x0 + v * T, y)


def lat_accel(t_s=5.0, ay=1.0, v=20.0, y0=0.0, x0=0.0):
    y = y0 + np.where(T > t_s, 0.5 * ay * (T - t_s) ** 2, 0.0)
    return Track(T, x0 + v * T, y)


def rotate(tr, ang, dx=0.0, dy=0.0):
    c, s = np.cos(ang), np.sin(ang)
    return Track(tr.t, c * tr.x - s * tr.y + dx, s * tr.x + c * tr.y + dy)


def main():
    s = PredictorSettings()          # h 1.0 s, sigma0 0.1 m

    # --- 1 steady motion ---------------------------------------------------------------
    ego, lead = straight(20.0), straight(15.0, x0=30.0)
    for ref in ("world", "joint", "relative"):
        z = situational_surprise(ego, {"lead": lead}, ref, s).z_max.to_numpy()
        check(f"{ref}: steady motion is not surprising", np.nanmax(z) < 1e-6,
              f"max z {np.nanmax(z):.2e}")

    # --- 2 onset latency, closed forms vs numeric --------------------------------------
    for vy in (0.1, 0.5, 2.0):
        ser = situational_surprise(straight(), {"o": swerve(vy=vy, x0=30.0)}, "world", s)
        lat = onset_time(ser, s) - 5.0
        analytic = s.z_on * s.sigma / vy
        if analytic <= s.h:
            ok, want = abs(lat - analytic) <= DT + 1e-9, f"{analytic:.3f} s"
        else:
            ok, want = np.isnan(lat), "never (the step leaves the band only after h)"
        check(f"velocity step {vy} m/s: latency matches z*sigma/dv", ok,
              f"numeric {lat:.3f} s, analytic {want}")
    for ay in (0.1, 0.5, 2.0):
        ser = situational_surprise(straight(), {"o": lat_accel(ay=ay, x0=30.0)}, "world", s)
        lat = onset_time(ser, s) - 5.0
        analytic = np.sqrt(2 * s.z_on * s.sigma / ay)
        if analytic <= s.h:
            ok, want = abs(lat - analytic) <= 2 * DT + 1e-9, f"{analytic:.3f} s"
        else:
            ok, want = np.isnan(lat), "never (a*h^2/2 < z*sigma)"
        check(f"lateral acceleration {ay} m/s^2: latency matches sqrt(2 z sigma / a)", ok,
              f"numeric {lat:.3f} s, analytic {want}")
    old = PredictorSettings(h=0.5, sigma0=0.1, sigma1=0.5)
    ser = situational_surprise(straight(), {"o": lat_accel(ay=2.0, x0=30.0)}, "world", old)
    check("card Q5.1's lowest setting cannot see a 2 m/s^2 lane change at all",
          np.isnan(onset_time(ser, old)),
          f"a*h^2/2 = {2.0 * 0.25 / 2:.2f} m < 2 sigma = {2 * old.sigma:.2f} m")

    # --- 3 what each reference monitors ------------------------------------------------
    ego_sw = swerve(vy=1.5)
    steady_other = straight(15.0, x0=30.0, y0=3.5)
    ser_w = situational_surprise(ego_sw, {"o": steady_other}, "world", s)
    ser_j = situational_surprise(ego_sw, {"o": steady_other}, "joint", s)
    ser_r = situational_surprise(ego_sw, {"o": steady_other}, "relative", s)
    t_w, t_j, t_r = onset_time(ser_w, s), onset_time(ser_j, s), onset_time(ser_r, s)
    check("world is blind to the ego's own manoeuvre", np.isnan(t_w))
    check("joint registers the ego's manoeuvre", np.isfinite(t_j) and t_j >= 5.0)
    check("relative registers it through the changing configuration",
          np.isfinite(t_r) and t_r >= 5.0)
    k = int(np.argmin(np.abs(T - t_j)))
    check("joint attributes it to the ego's lateral axis", ser_j.source.iloc[k] == "ego:lat",
          f"source at onset {ser_j.source.iloc[k]}")

    # --- 4 joint and relative differ where they should --------------------------------
    both = swerve(vy=1.5, x0=30.0, y0=3.5)
    t_j2 = onset_time(situational_surprise(ego_sw, {"o": both}, "joint", s), s)
    z_r2 = situational_surprise(ego_sw, {"o": both}, "relative", s).z_max.to_numpy()
    check("two vehicles swerving in parallel are jointly surprising", np.isfinite(t_j2))
    check("... and relatively unremarkable", np.nanmax(z_r2) < 1e-6,
          f"max relative z {np.nanmax(z_r2):.2e}")

    # --- 5 placement and orientation do not matter ------------------------------------
    other = swerve(vy=1.0, x0=30.0, y0=3.5)
    base = {ref: situational_surprise(ego_sw, {"o": other}, ref, s).z_max.to_numpy()
            for ref in ("world", "joint", "relative")}
    for ang in (0.7, -2.1):
        for ref in base:
            z = situational_surprise(rotate(ego_sw, ang, 100, -40),
                                     {"o": rotate(other, ang, 100, -40)}, ref, s).z_max.to_numpy()
            ok = np.allclose(np.nan_to_num(z), np.nan_to_num(base[ref]), atol=1e-6)
            check(f"{ref}: invariant to rotating the scene by {ang} rad and moving it", ok)

    # --- 6 axes --------------------------------------------------------------------------
    x_brake = 30.0 + 15.0 * T - np.where(T > 5.0, 0.5 * 4.0 * (T - 5.0) ** 2, 0.0)
    zl, zt = cv_standardized_error(T, x_brake, np.zeros_like(T), s)
    check("a braking lead shows on the longitudinal axis, not the lateral one",
          np.nanmax(np.abs(zl)) > s.z_on and np.nanmax(np.abs(zt)) < 1e-6,
          f"lon {np.nanmax(np.abs(zl)):.1f}, lat {np.nanmax(np.abs(zt)):.1e}")
    zl2, zt2 = cv_standardized_error(T, other.x, other.y, s)
    check("a swerve shows on the lateral axis, not the longitudinal one",
          np.nanmax(np.abs(zt2)) > s.z_on and np.nanmax(np.abs(zl2)) < 0.2 * s.z_on,
          f"lon {np.nanmax(np.abs(zl2)):.3f}, lat {np.nanmax(np.abs(zt2)):.1f}")

    # --- 6b per-axis spread ---------------------------------------------------------------
    rng = np.random.default_rng(0)
    jit_x = 20.0 * T + rng.normal(0.0, 0.3, len(T))          # 0.3 m longitudinal jitter
    noisy = Track(T, jit_x, np.where(T > 5.0, 0.5 * 1.0 * (T - 5.0) ** 2, 0.0))
    iso = PredictorSettings(sigma0=0.1, v_window=1.0)
    per_axis = PredictorSettings(sigma0=0.1, sigma0_lon=3.0, v_window=1.0)
    t_iso = onset_time(situational_surprise(straight(), {"o": noisy}, "world", iso), iso)
    t_ax = onset_time(situational_surprise(straight(), {"o": noisy}, "world", per_axis), per_axis)
    check("longitudinal jitter fires a single spread at once", np.isfinite(t_iso) and t_iso < 5.0,
          f"onset {t_iso:.2f} s")
    check("a wide longitudinal spread leaves the lateral manoeuvre detectable, and only it",
          np.isfinite(t_ax) and 5.0 <= t_ax <= 6.0, f"onset {t_ax:.2f} s")

    # --- 7 onset search window ---------------------------------------------------------
    ser = situational_surprise(straight(), {"o": other}, "world", s)
    check("onset search respects its start time", np.isnan(onset_time(ser, s, t_from=11.9)))

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
