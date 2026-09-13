"""
Property tests for the cut-in norms (src/comfortzone/norms.py, card PN.1).

Claims: the own-lane norm reproduces the released structure (normal only with the body inside
its own lane, 0.001 just outside, 1e-5 off the road); the crossing norm agrees with it wherever
the vehicle is inside a lane or off the road, and differs only while straddling, where lateral
speed decides; a normally paced lane change is never abnormal under the crossing norm and always
abnormal under the own-lane norm; lingering, drifting back and swerving are abnormal.

Run: python tests/test_norms.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from comfortzone.norms import (  # noqa: E402
    crossing_norm, lateral_speed_compliance, own_lane_norm,
)

PASS, FAIL = [], []
LW, D = 3.5, 1.88


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def main():
    alw = 0.5 * (LW - D)
    # --- 1 released structure --------------------------------------------------------
    w = own_lane_norm(np.array([0.0, alw - 0.01, alw + 0.01, LW, LW + alw + 0.2 * D + 0.1]), LW, D)
    check("own-lane norm: 1 inside its lane, 0.001 in the neighbouring lane, 1e-5 off the road",
          np.allclose(w, [1, 1, 0.001, 0.001, 1e-5]), str(w))

    # --- 2 the two norms agree outside the straddling band ---------------------------------
    offs = np.array([0.0, 0.5, LW, LW + 0.5, -3.0, LW + 3.0])
    v = np.array([1.5] * len(offs))
    wc, wo = crossing_norm(offs, v, LW, D), own_lane_norm(offs, LW, D)
    same = [0, 1, 4, 5]
    check("crossing norm agrees with the released norm in its own lane and off the road",
          np.allclose(wc[same], wo[same]))
    check("crossing norm treats the destination lane as normal", np.allclose(wc[[2, 3]], 1.0))

    # --- 3 a normally paced lane change ------------------------------------------------------
    for lcd in (2.0, 3.0, 4.0, 6.0):
        t = np.linspace(0, lcd, 400)
        y = LW / 2 * (1 - np.cos(np.pi * t / lcd))
        vy = np.gradient(y, t)
        straddle = (y >= alw) & (y <= LW - alw)
        wc = crossing_norm(y, vy, LW, D)
        wo = own_lane_norm(y, LW, D)
        check(f"LCD {lcd:.0f} s: never abnormal under the crossing norm while straddling",
              wc[straddle].min() > 0.99, f"min {wc[straddle].min():.3f}, lateral speed "
              f"{vy[straddle].min():.2f}-{vy[straddle].max():.2f} m/s")
        check(f"LCD {lcd:.0f} s: abnormal under the own-lane norm once the body leaves its lane",
              wo[straddle].max() <= 0.001 + 1e-12)

    # --- 4 what is abnormal ----------------------------------------------------------------
    mid = np.array([LW / 2])
    check("lingering on the line (0 m/s) is abnormal", crossing_norm(mid, np.array([0.0]), LW, D)[0] < 0.05)
    check("drifting back toward its own lane is abnormal",
          crossing_norm(mid, np.array([-1.0]), LW, D)[0] < 0.05)
    check("swerving across at 5 m/s is abnormal", crossing_norm(mid, np.array([5.0]), LW, D)[0] < 0.05)
    grid = lateral_speed_compliance(np.linspace(-2, 6, 200))
    check("compliance is 1 on the band, floored at sqrt(0.001), never above 1",
          grid.max() <= 1.0 and np.isclose(grid.min(), np.sqrt(0.001)))
    left = lateral_speed_compliance(np.linspace(-2, 0.5, 100))
    check("compliance rises monotonically up to v_lo", bool(np.all(np.diff(left) >= -1e-12)))

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
