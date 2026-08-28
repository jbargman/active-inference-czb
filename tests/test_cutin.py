"""
Property tests for the continuous lane-entry forms (src/aidriver/preferences.py flags)
and the cut-in module (src/comfortzone/cutin.py).

Run: python tests/test_cutin.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aidriver.preferences import (PreferenceParams, inverse_tau, lane_entry_shape,
                                  lane_entry_weight,
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


def test_lane_entry_shape():
    """The S-shaped remap of the overlap fraction (2026-08-28, `lane_entry_shape_k`).

    The properties that make it a refinement of the linear ramp rather than a different
    model: the endpoints stay exact (so the released-limit identities survive), k = 0 is
    the identity (so linear is nested and testable), the curve is monotone, and the
    negative branch really is the inverse of the positive one rather than a duplicate of
    it -- the last is checked because the natural construction gets it wrong.
    """
    u = np.linspace(0.0, 1.0, 201)
    for k in (0.0, 0.5, 4.0, 8.0, 20.0, -4.0, -8.0):
        g = lane_entry_shape(u, k)
        check(f"shape k={k}: endpoints exact",
              abs(g[0]) < 1e-12 and abs(g[-1] - 1.0) < 1e-12, f"{g[0]:.2e}, {g[-1]-1:.2e}")
        check(f"shape k={k}: monotone non-decreasing", np.all(np.diff(g) >= -1e-12))
        check(f"shape k={k}: stays in [0, 1]", g.min() >= -1e-12 and g.max() <= 1 + 1e-12)

    check("shape k=0 is the identity (linear ramp nested)",
          np.allclose(lane_entry_shape(u, 0.0), u, atol=1e-12))
    check("negative k is the functional inverse of positive k",
          np.allclose(lane_entry_shape(lane_entry_shape(u, 6.0), -6.0), u, atol=1e-9))
    check("k and -k are NOT the same curve",
          not np.allclose(lane_entry_shape(u, 4.0), lane_entry_shape(u, -4.0), atol=1e-3))
    check("positive k is below the linear ramp in the lower half (slow start)",
          np.all(lane_entry_shape(u[1:100], 6.0) < u[1:100]))
    check("symmetric about the midpoint",
          np.allclose(lane_entry_shape(u, 6.0) + lane_entry_shape(1 - u, 6.0), 1.0, atol=1e-12))


def test_lane_entry_shape_defaults_preserve_released_behavior():
    """k defaults to 0, so every previously computed weight is bit-identical."""
    p_def = PreferenceParams(lane_entry_continuous=True)
    check("lane_entry_shape_k defaults to 0", p_def.lane_entry_shape_k == 0.0)
    p_k = PreferenceParams(lane_entry_continuous=True, lane_entry_shape_k=6.0)
    same, differ = 0, 0
    for dy in np.linspace(0.0, 4.0, 25):
        o = obs_following(dy=float(dy), dx=25.0, v=25.0, v_other=15.0, vy=-0.5)
        w0, wk = lane_entry_weight(o, p_def), lane_entry_weight(o, p_k)
        # endpoints (0 and 1) must agree; interior values must be free to move
        if w0 in (0.0, 1.0):
            same += int(np.isclose(w0, wk, atol=1e-12))
        else:
            differ += int(not np.isclose(w0, wk, atol=1e-9))
    check("shaped weight agrees with linear at the saturated ends", same > 0)
    check("shaped weight differs from linear in the interior", differ > 0)



def test_overtake_loader():
    """The cyclist-overtake loader (card B.1, 2026-08-28).

    The load-bearing test is the first one: the edge-to-edge clearance at the pass must
    reproduce the study's own criticality labels. It is what distinguishes the correct
    lateral coordinate (`Location_Y`) from the plausible-looking wrong one (`Offset`),
    which inverts the ordering and would silently reverse the criticality axis.
    """
    from comfortzone.overtake import (NOMINAL_CLEARANCE_M, RANDOM_OVERTAKE_TRACES,
                                      clearance_at_pass, edge_clearance,
                                      load_overtake_trace)
    traces = {}
    for lab, path in RANDOM_OVERTAKE_TRACES.items():
        if not path.exists():
            check(f"overtake trace {lab} present", False, "missing stimulus file")
            return
        traces[lab] = load_overtake_trace(path)

    for lab, tr in traces.items():
        c = clearance_at_pass(tr)
        check(f"overtake {lab}: clearance at pass matches the label",
              abs(c - NOMINAL_CLEARANCE_M[lab]) < 0.02, f"{c:.3f} vs {NOMINAL_CLEARANCE_M[lab]}")
        check(f"overtake {lab}: ego is the car, target the cyclist",
              0.4 < tr.tar_wid < 0.8, f"target width {tr.tar_wid:.2f}")
        check(f"overtake {lab}: onset precedes the pass",
              tr.onset_idx < tr.complete_idx)
        check(f"overtake {lab}: target leads at onset (ego approaches from behind)",
              tr.x_tar[tr.onset_idx] > 0)

    # criticality ordering: tighter label => less clearance at every shared timepoint
    labs = ["0.5m", "1m", "1.5m"]
    fin = [clearance_at_pass(traces[l]) for l in labs]
    check("clearance at the pass is ordered by label", fin[0] < fin[1] < fin[2])
    # and the bodies overlap laterally well before the pass in every condition
    check("bodies laterally overlap early in every condition",
          all(edge_clearance(traces[l])[traces[l].onset_idx] < 0 for l in labs))


def test_overtake_uses_the_cutin_field_code():
    """The transfer test is only meaningful if both scenarios share the field code."""
    from comfortzone.czb_data import overtake_stimulus_field
    from comfortzone.overtake import RANDOM_OVERTAKE_TRACES
    path = RANDOM_OVERTAKE_TRACES["1m"]
    if not path.exists():
        check("overtake field computable", False, "missing stimulus file")
        return
    f = overtake_stimulus_field(path)
    for col in ("deficit", "deficit_max", "a_req", "p_lane", "t_since_onset"):
        check(f"overtake field exposes `{col}` (same columns as the cut-in)",
              col in f.columns)
    check("deficit_max is non-decreasing", np.all(np.diff(f.deficit_max.to_numpy()) >= -1e-9))
    check("t_since_onset is zero at onset",
          abs(float(f.t_since_onset.to_numpy()[np.argmin(np.abs(f.t_since_onset.to_numpy()))])) < 1e-9)


def test_czb_shape_constant_is_staged_not_default():
    """k = 12 applies on the CZB path only; released behavior keeps k = 0 (2026-08-28)."""
    from comfortzone.cutin import CZB_LANE_ENTRY_SHAPE_K, cutin_params, load_cutin_trace
    from comfortzone.czb_data import RANDOM_CUTIN_TRACES
    check("released default keeps the linear ramp",
          PreferenceParams().lane_entry_shape_k == 0.0)
    check("the CZB constant is 12", CZB_LANE_ENTRY_SHAPE_K == 12.0)
    path = RANDOM_CUTIN_TRACES["TTC4"]
    if not path.exists():
        check("cut-in trace present for staging check", False, "missing stimulus file")
        return
    tr = load_cutin_trace(path)
    check("CZB staging applies k = 12 by default",
          cutin_params(tr).lane_entry_shape_k == CZB_LANE_ENTRY_SHAPE_K)
    # an explicitly supplied params object must win, or the k sweep is unreproducible
    check("an explicit k is respected by the staging function",
          cutin_params(tr, PreferenceParams(lane_entry_shape_k=4.0)).lane_entry_shape_k == 4.0)


def test_lane_entry_bidirectional():
    """Outward lateral projection, added for card B.1 and defaulting OFF (2026-08-28).

    Tested rather than trusted because it is a tested-and-REJECTED variant: it is kept
    in the codebase so the overtake finding is reproducible, and the thing most likely
    to go wrong is that it silently becomes the default.
    """
    p_off = PreferenceParams(lane_entry_continuous=True)
    p_on = PreferenceParams(lane_entry_continuous=True, lane_entry_bidirectional=True)
    check("lane_entry_bidirectional defaults to False", p_off.lane_entry_bidirectional is False)
    check("outward clamp defaults to one study lane width", p_off.lane_entry_max_dy_m == 3.5)

    # object moving laterally AWAY: the unidirectional form ignores it, the new one does not
    away = obs_following(dy=0.6, dx=30.0, v=25.0, v_other=15.0, vy=+1.5)
    w_off = float(lane_entry_weight(away, p_off))
    w_on = float(lane_entry_weight(away, p_on))
    check("moving away is invisible to the released form but not to the bidirectional one",
          w_on < w_off, f"off {w_off:.3f}, on {w_on:.3f}")

    # an object moving TOWARD our lane must behave identically under both
    toward = obs_following(dy=3.0, dx=30.0, v=25.0, v_other=15.0, vy=-1.0)
    check("inward motion is unaffected by the flag",
          np.isclose(float(lane_entry_weight(toward, p_off)),
                     float(lane_entry_weight(toward, p_on)), atol=1e-12))
    # and with no lateral motion at all, the two forms must agree exactly
    still = obs_following(dy=2.0, dx=30.0, v=25.0, v_other=15.0, vy=0.0)
    check("static geometry is unaffected by the flag",
          np.isclose(float(lane_entry_weight(still, p_off)),
                     float(lane_entry_weight(still, p_on)), atol=1e-12))
    # the outward projection is clamped, so the weight cannot go below zero
    fleeing = obs_following(dy=0.1, dx=60.0, v=30.0, v_other=15.0, vy=+8.0)
    check("clamped outward projection keeps the weight in [0, 1]",
          0.0 <= float(lane_entry_weight(fleeing, p_on)) <= 1.0)


def test_covariate_window():
    """The shown-clip covariate window (2026-08-29, closing blocker B2.Q1).

    The claims under test, from replication/czb/out/c1_covariate_defect.md: the C1
    covariate no longer includes the manoeuvre-onset frame (whose lane-entry
    projection inverted the criticality ordering), the running max no longer
    accumulates trace-start frames the participant never saw, and everything the
    participants DID see is untouched -- the C2+ cut-in covariates are bit-identical
    to the whole-trace convention.
    """
    from comfortzone.czb_data import (C1_COV_END_S, RANDOM_CLIP_LEAD_S,
                                      RANDOM_CUTIN_TRACES, stimulus_field)
    path = RANDOM_CUTIN_TRACES["TTC8"]
    if not path.exists():
        check("cut-in trace present for window check", False, "missing stimulus file")
        return
    check("C1 window ends before the central-difference reach of the onset frame",
          -0.2 < C1_COV_END_S < -0.1, C1_COV_END_S)

    # TTC8 is the sharpest case: onset frame deficit 2907 through p_lane ~ 1.
    f_old = stimulus_field(path)
    f_new = stimulus_field(path, accum_lead_s=RANDOM_CLIP_LEAD_S)

    def cov(f, t_end):
        idx = int(np.searchsorted(f.t_since_onset.to_numpy(), t_end, side="right")) - 1
        return float(f.deficit_max.iloc[max(idx, 0)])

    old_c1, new_c1 = cov(f_old, 0.0), cov(f_new, C1_COV_END_S)
    check("the old C1 covariate carried the onset-frame spike", old_c1 > 1000, old_c1)
    check("the new C1 covariate is at the normal-driving noise level", new_c1 < 10, new_c1)
    # C2..C6 must be untouched by the window change
    same = all(np.isclose(cov(f_old, 0.3 * k), cov(f_new, 0.3 * k), rtol=0, atol=1e-9)
               for k in range(1, 6))
    check("C2-C6 covariates are bit-identical under the shown-clip window", same)
    # both window arguments at once is a caller error
    try:
        stimulus_field(path, accum_start_s=5.0, accum_lead_s=10.0)
        check("giving both window arguments raises", False)
    except ValueError:
        check("giving both window arguments raises", True)


def test_covariate_window_trials():
    """The trial tables built on the window: the C1 inversion is gone, and the
    overtake condition that inherited a trace-start artifact floor is freed of it."""
    from comfortzone.czb_data import random_cutin_trials, random_overtake_trials
    try:
        cut = random_cutin_trials()
    except FileNotFoundError:
        check("study data present for trial-table check", False, "missing study files")
        return
    c1 = (cut[cut.timepoint == "C1"].groupby("criticality", observed=True)
          .deficit_max.first())
    check("cut-in C1 covariates are all at noise level", bool((c1 < 10).all()),
          dict(c1.round(2)))
    spread = float(c1.max() - c1.min())
    check("the 1500-unit C1 inversion is gone (spread < 5 units)", spread < 5.0, spread)

    ovt = random_overtake_trials()
    legacy = random_overtake_trials(legacy_covariates=True)
    m15 = ovt[(ovt.criticality == "1.5m") & (ovt.timepoint == "C1")].deficit_max.iloc[0]
    l15 = legacy[(legacy.criticality == "1.5m")
                 & (legacy.timepoint == "C1")].deficit_max.iloc[0]
    check("the 1.5m overtake trace-start floor (230.9) is excluded",
          m15 < 10 < l15, f"legacy {l15:.1f} -> {m15:.2f}")


if __name__ == "__main__":
    for fn in [test_lane_entry_weight, test_residual_severity, test_collision_tau_gating,
               test_norm_weight_categories, test_lane_entry_shape,
               test_lane_entry_shape_defaults_preserve_released_behavior,
               test_overtake_loader, test_overtake_uses_the_cutin_field_code,
               test_czb_shape_constant_is_staged_not_default,
               test_lane_entry_bidirectional,
               test_covariate_window, test_covariate_window_trials]:
        fn()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(1 if FAIL else 0)
