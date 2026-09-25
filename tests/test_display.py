"""
Property tests for the display transform (src/comfortzone/display.py, docs/display_transform.md).

Claims: the spec's YAML block is read and gives the stated defaults (23-inch 16:9, 60 cm, 90 deg:
screen 50.92 cm wide, gain k = 0.4243, the image fills 46.0 deg); the gain is 1 when the rendered
and the displayed field of view coincide, and every function is then the identity; g=None is the
identity; the screen projection viewed from d equals the equivalent world at distance r/k at every
azimuth (not only near the centre); TTC is invariant; looming shrinks by exactly
k (r^2 + W^2/4) / (r^2 + k^2 W^2/4), which tends to k at long range; inverse tau is invariant in the
small-angle limit; convention (b) gives the real-world TTC of the perceived looming at the true
speed, about TTC / sqrt(k); overrides work and unknown parameters are refused; the environment
switch is off by default.

Run: python tests/test_display.py
"""
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from comfortzone import display as D  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def main():
    g = D.load_geometry()
    k = D.gain(g)
    check("the spec's YAML block gives the stated defaults",
          g.screen_diagonal_in == 23 and g.viewing_distance_cm == 60 and g.virtual_hfov_deg == 90
          and g.image_width_fraction == 1 and g.camera_to_front_m == 0)
    check("a 23-inch 16:9 screen is 50.92 cm wide; the gain is 0.4243; the image fills 46.0 deg",
          abs(D.screen_width_cm(g) - 50.92) < 0.01 and abs(k - 0.4243) < 1e-4
          and abs(D.display_hfov_deg(g) - 45.99) < 0.01,
          f"{D.screen_width_cm(g):.2f} cm, k {k:.4f}, {D.display_hfov_deg(g):.2f} deg")

    matched = D.load_geometry(virtual_hfov_deg=D.display_hfov_deg(g))
    gap, dv, W = np.array([3.0, 10.0, 40.0]), np.array([2.0, 5.0, 8.0]), 1.85
    check("when the rendered field of view equals the displayed one the gain is 1 and the transform"
          " is the identity", abs(D.gain(matched) - 1) < 1e-12
          and np.allclose(D.looming(gap, dv, W, matched), D.looming(gap, dv, W)))
    check("g=None is the identity (the pipeline's EL.1b formula)",
          np.allclose(D.looming(gap, dv, W, None), W * dv / (gap ** 2 + W ** 2 / 4)))

    X, Y = np.array([5.0, 20.0, 60.0, 3.0]), np.array([0.0, 3.5, -7.0, 2.9])
    F, d = D.focal_cm(g), g.viewing_distance_cm
    seen = np.arctan((F * Y / X) / d)
    equiv = np.arctan(Y / (X / k))
    check("the screen seen from d is the equivalent world at X/k, at every azimuth (to 1e-12)",
          np.allclose(seen, equiv, atol=1e-12) and np.allclose(D.seen_direction(np.arctan(Y / X), g), seen))

    p = D.perceived(gap, dv, W, g)
    check("TTC is invariant", np.allclose(p["ttc"], gap / dv))
    exact = k * (gap ** 2 + W ** 2 / 4) / (gap ** 2 + k ** 2 * W ** 2 / 4)
    ratio = p["theta_dot"] / D.looming(gap, dv, W)
    check("looming shrinks by exactly k (r^2 + W^2/4) / (r^2 + k^2 W^2/4)", np.allclose(ratio, exact),
          f"ratios {np.round(ratio, 4)}")
    check("the looming ratio tends to k at long range", abs(D.looming(500, 5, W, g) / D.looming(500, 5, W) - k) < 1e-5)
    check("the angular size shrinks by about k at long range",
          abs(p["theta"][2] / (2 * np.arctan(W / (2 * gap[2]))) - k) < 1e-3)
    check("inverse tau is invariant in the small-angle limit",
          abs((p["theta_dot"][2] / p["theta"][2]) / (D.looming(40, 8, W) / (2 * np.arctan(W / 80))) - 1) < 1e-3)

    tb = D.ttc_at_true_speed(p["theta_dot"], dv, W)
    back = D.looming(tb * dv, dv, W)
    check("convention (b): a real driver at the true speed receives the perceived looming at TTC_b",
          np.allclose(back, p["theta_dot"]))
    check("convention (b): TTC_b is about TTC / sqrt(k) at long range",
          abs(tb[2] / (gap[2] / dv[2]) - 1 / np.sqrt(k)) < 1e-3, f"{tb[2] / (gap[2] / dv[2]):.4f}")

    lv = D.transform_level(0.032, 20.0, 5.0, W, g)
    check("a level transforms by the exact ratio at its kinematics", abs(lv / 0.032 - D.looming(20, 5, W, g) / D.looming(20, 5, W)) < 1e-12)
    check("off-axis angular width reduces to the centred one at y = 0",
          np.allclose(D.offaxis_theta(gap, 0.0, W, g), p["theta"]))

    g2 = D.load_geometry(viewing_distance_cm=70, image_width_fraction=0.8)
    check("overrides change the gain as the geometry says", abs(D.gain(g2) - k * 0.8 * 60 / 70) < 1e-12)
    try:
        D.load_geometry(screen_size=24)
        check("unknown parameters are refused", False)
    except TypeError:
        check("unknown parameters are refused", True)
    e = D.load_geometry(camera_to_front_m=2.0)
    check("camera_to_front_m adds to the distance before scaling",
          np.allclose(D.perceived(gap, dv, W, e)["r"], (gap + 2.0) / k))
    old = os.environ.pop(D.ENV, None)
    try:
        off = D.active_geometry() is None
        os.environ[D.ENV] = "on"
        on = D.active_geometry() == g
    finally:
        os.environ.pop(D.ENV, None)
        if old is not None:
            os.environ[D.ENV] = old
    check("the environment switch is off by default and 'on' loads the spec", off and on)

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
