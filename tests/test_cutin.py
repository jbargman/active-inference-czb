"""
Property tests for the continuous lane-entry forms (src/aidriver/preferences.py flags)
and the cut-in module (src/comfortzone/cutin.py).

Run: python tests/test_cutin.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aidriver.preferences import (PreferenceParams, inverse_tau, lane_entry_weight,
                                  log_safety_pref, log_collision_pref,
                                  required_deceleration, residual_delta_v)  # noqa: E402
from comfortzone.cutin import cutin_norm_weight                          # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if bool(cond) else FAIL).append(name)
    print("{}  {}{}".format("PASS" if cond else "FAIL", name, ("  -- " + str(detail)) if detail else ""))


def obs_following(dy=0.0, dx=20.0, v=25.0, v_other=15.0, vy=0.0, **kw):
    o = {"v": v, "a": 0.0, "dx": dx, "dy": dy, "v_other": v_other, "a_other": 0.0,
         "vy_other": vy}
    o.update(kw)
    return o


def test_lane_entry_weight():
    p = PreferenceParams()
    w = p.vehicle.width
    check("fully in lane (dy=0) gives P_lane = 1",
          lane_entry_weight(obs_following(dy=0.0), p) == 1.0)
    check("adjacent lane, no lateral motion, gives P_lane = 0 when not closing",
          lane_entry_weight(obs_following(dy=3.65, v=15.0, v_other=15.0), p) == 0.0)
    # instantaneous overlap ramps monotonically as |dy| shrinks
    dys = np.linspace(3.0, 0.0, 40)
    ws = np.array([float(lane_entry_weight(obs_following(dy=d, v=15.0, v_other=15.0), p))
                   for d in dys])
    check("P_lane is monotone non-decreasing as the target centres", np.all(np.diff(ws) >= -1e-12))
    check("P_lane is continuous through overlap onset (no jump > 0.2 on a fine grid)",
          np.max(np.abs(np.diff(ws))) < 0.2, f"max step {np.max(np.abs(np.diff(ws))):.3f}")
    # the released binary gate is the limit: overlap onset at 1.15 * width for equal widths
    check("overlap onset coincides with the released box threshold 1.15w",
          lane_entry_weight(obs_following(dy=1.15 * w + 0.01, v=15.0, v_other=15.0), p) == 0.0
          and lane_entry_weight(obs_following(dy=1.15 * w - 0.05, v=15.0, v_other=15.0), p) > 0.0)
    # anticipation: approaching laterally raises P_lane before any overlap
    still = float(lane_entry_weight(obs_following(dy=3.0, vy=0.0), p))
    approaching = float(lane_entry_weight(obs_following(dy=3.0, vy=-1.5), p))
    check("lateral approach raises P_lane before overlap begins", approaching > still)
    # and the anticipatory weight is higher when overlap will begin well before closure
    slow_close = float(lane_entry_weight(obs_following(dy=3.0, vy=-1.5, dx=60.0), p))
    check("earlier lateral entry relative to longitudinal closure weighs higher",
          slow_close >= approaching)


def test_residual_severity():
    p = PreferenceParams(counterfactual_residual_severity=True, lane_entry_continuous=True)
    p0 = PreferenceParams()
    # residual delta-v is zero exactly where the crash is avoidable
    safe = obs_following(dx=200.0)
    check("dv_resid = 0 when a_req >= -a_max",
          residual_delta_v(safe, p) == 0.0 and required_deceleration(safe, p) > -p.a_max)
    # ramps continuously from the boundary: tighten the gap through the a_req = -a_max point
    dxs = np.linspace(150.0, 10.0, 200)
    dv = np.array([float(residual_delta_v(obs_following(dx=d), p)) for d in dxs])
    check("dv_resid is monotone as the gap tightens", np.all(np.diff(dv) >= -1e-9))
    started = dv > 0
    check("dv_resid starts at zero and ramps (first positive value < 1.5 m/s)",
          started.any() and dv[np.argmax(started)] < 1.5, f"first {dv[np.argmax(started)]:.2f}")
    # the safety term under the flags is continuous in time-like sweeps and recovers the
    # released *location* of the boundary: it is nonzero exactly where the released
    # indicator fires (in-lane geometry)
    on_released = np.array([float(log_safety_pref(obs_following(dx=d), p0)) for d in dxs])
    on_cont = np.array([float(log_safety_pref(obs_following(dx=d), p)) for d in dxs])
    check("continuous safety term is nonzero exactly where the released indicator fires",
          np.array_equal(on_cont < 0, on_released < 0))
    check("continuous safety term never exceeds ~the released step scale",
          np.all(on_cont >= 1.05 * on_released.min() * dv.max() / 10))
    # lateral gating: same longitudinal state, target out of lane -> no cost
    out = obs_following(dx=15.0, dy=3.65, vy=0.0, v=25.0, v_other=15.0)
    # not closing laterally, but closing longitudinally: anticipation weight is 0
    check("out-of-lane target with no lateral motion costs nothing even when closing",
          float(log_safety_pref(out, p)) == 0.0)


def test_collision_tau_gating():
    p = PreferenceParams(lane_entry_continuous=True)
    p0 = PreferenceParams()

    def with_tau(o, pp):
        o = dict(o)
        o["tau_inv"] = inverse_tau(o["dx"], o["v"], o["v_other"], pp)
        return o

    # in-lane: gated tau term equals released tau term
    o = with_tau(obs_following(dy=0.0, dx=18.0, v=25.0, v_other=15.0), p)
    check("in-lane tau^-1 preference is unchanged by the gate",
          float(log_collision_pref(o, p)) == float(log_collision_pref(o, p0)))
    # adjacent lane, closing fast longitudinally: released charges, gated does not
    o2 = with_tau(obs_following(dy=3.65, dx=18.0, v=25.0, v_other=15.0), p)
    check("passing an adjacent-lane vehicle costs nothing under the gate",
          float(log_collision_pref(o2, p)) == 0.0 and float(log_collision_pref(o2, p0)) < 0.0)


def test_norm_weight_categories():
    # regression (2026-08-27): the straddling category used to be empty by construction
    lane = 3.5
    prog = np.array([0.5])
    w_in = cutin_norm_weight(np.array([0.0]), prog, lane)
    w_adj = cutin_norm_weight(np.array([lane]), prog, lane)
    w_straddle = cutin_norm_weight(np.array([lane / 2]), prog, lane, straddle_tolerance=0.0)
    w_far = cutin_norm_weight(np.array([2.5 * lane]), prog, lane)
    check("in-lane and adjacent are fully normal", w_in[0] == 1.0 and w_adj[0] == 1.0)
    check("straddling engages the time-dependence when tolerance < progress",
          w_straddle[0] < 1.0)
    check("far off-corridor is w_offlane", w_far[0] == 0.05)
    w_straddle_neutral = cutin_norm_weight(np.array([lane / 2]), prog, lane)
    check("neutral default (tolerance 1.0) applies no straddling penalty",
          w_straddle_neutral[0] == 1.0)


if __name__ == "__main__":
    for fn in [test_lane_entry_weight, test_residual_severity, test_collision_tau_gating,
               test_norm_weight_categories]:
        fn()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(1 if FAIL else 0)
