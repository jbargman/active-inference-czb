"""
Property tests for the rollout formulation of the comfort-zone boundary (src/rollout/, card
JJ.1).

The eighteen claims of `handover_jj1_implementation.md` section 6, in its order, plus the
citation check that keeps the jitter floors tied to card HS.1's own docstring and a check that
the one new preference flag leaves the released behavior bit-identical.

Belief: the posterior is the prior at the jitter floor; a sustained lane-change rate drives it
above 0.95; mirroring the scene's lateral sign changes nothing. Predictor: zero growth
reproduces the constant-velocity projection (the G.1 limit); the sample mean matches the
analytic mean; one seed gives one fan; a change stops at the ego's lane centre. Policies:
continue holds speed; brake hard reaches zero at v/6 s; the left turn's proceed reproduces
`conflict.planned_path`. Scoring: G >= 0; identical policies score identically; a lane-keeping
other with no perturbation gives Delta G = 0; a certain collision under continue and none under
brake gives Delta G > 0, larger at a 10 m gap than at 30 m; variant B differs only in the
safety term; the flag at its default is bit-identical. Boundary: the zero rule applies only
when a zero exists; the Monte Carlo standard error falls as 1/sqrt(n).

Run: python tests/test_rollout.py
"""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidriver.preferences import (PreferenceParams, log_preference_terms,  # noqa: E402
                                  apply_running_min)
from comfortzone.conflict import Body, planned_path  # noqa: E402
from rollout.belief import (Belief, FLOORS_STUDY1, FLOORS_STUDY2, Frame, Scene,  # noqa: E402
                            P_CHANGE_PRIOR, SD_LC_MPS, V_LC_MPS, belief_at,
                            update_intention, verify_floors)
from rollout.boundary import axis, delta_g, mc_standard_error  # noqa: E402
from rollout.efe import expected_free_energy, g_by_policy, log_terms  # noqa: E402
from rollout.policies import (CUTIN_MENU, LTAP_CONTINUE, EgoPath, ego_rollout,  # noqa: E402
                              ltap_rollout)
from rollout.predictor import (DT_S, HORIZON_S, SD_VLAT, Futures, analytic_lateral_mean,  # noqa: E402
                               horizon_steps, sample_futures)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def cutin_belief(**kw) -> Belief:
    """A study-2-like cut-in at the freeze: the other ahead and to the left, closing."""
    base = dict(x_rel=25.0, y_rel=3.5, v_ego=30.0, v_oth=28.0, vy_oth=0.0,
                sd_pos=FLOORS_STUDY2.sd_pos, sd_vy=FLOORS_STUDY2.sd_v_lat,
                p_change=P_CHANGE_PRIOR, ego_len=4.2, ego_wid=1.72, oth_len=4.6, oth_wid=1.88,
                vx_oth=28.0, floors=FLOORS_STUDY2, name="synthetic cut-in")
    base.update(kw)
    return Belief(**base)


def cutin_params(v: float) -> PreferenceParams:
    """The CZB staging: the clip's own desired speed and the continuous lane-entry forms."""
    return PreferenceParams(v_desired=v, lane_entry_continuous=True,
                            counterfactual_residual_severity=True, lane_entry_shape_k=12.0)


def main():
    # --- 0 the floors are still card HS.1's -------------------------------------------
    missing = verify_floors()
    check("the jitter floors are read from card HS.1's own docstring and still match it",
          not missing, f"missing citations: {missing}")

    # --- belief ------------------------------------------------------------------------
    # (1)
    p1 = update_intention(P_CHANGE_PRIOR, FLOORS_STUDY2.sd_v_lat, FLOORS_STUDY2.sd_v_lat, sign=1.0)
    p1b = update_intention(P_CHANGE_PRIOR, 0.0, FLOORS_STUDY2.sd_v_lat, sign=1.0)
    check("(1) a lateral rate at the jitter floor leaves the posterior at the prior",
          abs(p1 - P_CHANGE_PRIOR) < 1e-3 and abs(p1b - P_CHANGE_PRIOR) < 1e-3,
          f"{p1:.6f} and {p1b:.6f} against {P_CHANGE_PRIOR}")
    # (2)
    p2 = update_intention(P_CHANGE_PRIOR, -V_LC_MPS, FLOORS_STUDY2.sd_v_lat, sign=1.0)
    check("(2) a sustained rate of -v_lc toward the ego drives the posterior above 0.95",
          p2 > 0.95, f"{p2:.6f}")
    # (3)
    p3 = update_intention(P_CHANGE_PRIOR, +V_LC_MPS, FLOORS_STUDY2.sd_v_lat, sign=-1.0)
    check("(3) mirroring the scene's lateral sign leaves the posterior unchanged",
          abs(p3 - p2) < 1e-12, f"{p3:.6f} against {p2:.6f}")
    # and the mirror holds at a half-finished change too
    for vy in (-0.2, -0.6, -1.0):
        a = update_intention(P_CHANGE_PRIOR, vy, FLOORS_STUDY1.sd_v_lat, sign=1.0)
        b = update_intention(P_CHANGE_PRIOR, -vy, FLOORS_STUDY1.sd_v_lat, sign=-1.0)
        if abs(a - b) > 1e-12:
            check(f"(3b) mirror at vy = {vy}", False, f"{a} vs {b}")
            break
    else:
        check("(3b) the mirror holds at every partial lateral rate, on study 1's floor too", True)
    # the one-sided clip is the documented decision (JJ1.Q6); the plain ratio is available
    p_plain = update_intention(P_CHANGE_PRIOR, 0.0, FLOORS_STUDY2.sd_v_lat, sign=1.0,
                               one_sided=False)
    check("(1b) the unclipped ratio is available as the sensitivity and does NOT return the prior",
          p_plain < 0.01 * P_CHANGE_PRIOR, f"{p_plain:.3e} against the prior {P_CHANGE_PRIOR}")

    # belief_at on a synthetic scene: a straight ego, the other closing laterally
    t = np.arange(0.0, 20.0, 1.0 / 30.0)
    sc = Scene(t=t, ego_x=30.0 * t, ego_y=np.zeros_like(t), ego_heading=np.zeros_like(t),
               ego_speed=np.full_like(t, 30.0),
               oth_x=50.0 + 28.0 * t, oth_y=3.5 - 0.5 * np.maximum(t - 5.0, 0.0),
               oth_heading=np.zeros_like(t), oth_speed=np.full_like(t, 28.0),
               ego_len=4.2, ego_wid=1.72, oth_len=4.6, oth_wid=1.88, name="synthetic")
    b_pre = belief_at(sc, 4.0, FLOORS_STUDY2)
    b_post = belief_at(sc, 8.0, FLOORS_STUDY2)
    check("(1c) belief_at: pre-onset the posterior is the prior; post-onset it has risen",
          abs(b_pre.p_change - P_CHANGE_PRIOR) < 1e-9 and b_post.p_change > 0.5,
          f"{b_pre.p_change:.4f} then {b_post.p_change:.4f}")
    check("(1d) belief_at reads the geometry in the freeze frame (x_rel 50 m + 2 s of closing,"
          " y_rel 3.5 m, vy -0.5 m/s)",
          abs(b_pre.x_rel - (50.0 - 2.0 * 4.0)) < 0.2 and abs(b_pre.y_rel - 3.5) < 1e-6
          and abs(b_post.vy_oth + 0.5) < 1e-6,
          f"x_rel {b_pre.x_rel:.2f}, y_rel {b_pre.y_rel:.3f}, vy {b_post.vy_oth:.4f}")

    # --- predictor ---------------------------------------------------------------------
    # (4) the G.1 limit
    b4 = cutin_belief(sd_pos=0.0, p_change=0.0, vy_oth=-0.2)
    f4 = sample_futures(b4, sd_vlat=0.0, sd_a=0.0, n=25, seed=7)
    tau = f4.tau
    x_cv = b4.x_rel + b4.vx_oth * tau
    y_cv = b4.y_rel + b4.vy_oth * tau
    check("(4) with zero growth, no intention and a straight other every sample is the "
          "constant-velocity projection (the G.1 limit)",
          np.allclose(f4.x, x_cv[None, :], atol=1e-12) and np.allclose(f4.y, y_cv[None, :], atol=1e-12),
          f"max |dx| {np.abs(f4.x - x_cv).max():.2e}, max |dy| {np.abs(f4.y - y_cv).max():.2e}")
    # (5) the sample mean at tau = 3 s against the analytic mean
    b5 = cutin_belief(y_rel=3.5, vy_oth=-0.1, p_change=0.4, sd_pos=0.0)
    n5 = 20000
    f5 = sample_futures(b5, n=n5, seed=11)
    k3 = int(np.argmin(np.abs(f5.tau - 3.0)))
    mean_obs = float(f5.y[:, k3].mean())
    mean_an = analytic_lateral_mean(b5, 3.0)
    se = float(f5.y[:, k3].std(ddof=1) / np.sqrt(n5))
    check("(5) the sample mean of y at tau = 3 s matches the analytic mean within 3 standard errors",
          abs(mean_obs - mean_an) <= 3.0 * se,
          f"{mean_obs:.4f} against {mean_an:.4f}, 3 SE = {3 * se:.4f}")
    # (6) common random numbers
    fa = sample_futures(b5, n=200, seed=3)
    fb = sample_futures(b5, n=200, seed=3)
    check("(6) the same seed gives a bit-identical fan",
          np.array_equal(fa.x, fb.x) and np.array_equal(fa.y, fb.y)
          and np.array_equal(fa.v, fb.v) and np.array_equal(fa.changing, fb.changing))
    # (7) a change stops at the ego's lane centre
    b7 = cutin_belief(p_change=1.0, sd_pos=0.0)
    f7 = sample_futures(b7, n=50, seed=5)
    u = b7.toward_sign * f7.y
    check("(7) under 'changing' the lateral position stops at the ego's lane centre and never "
          "crosses it", u.min() >= -1e-12 and abs(u[:, -1]).max() < 1e-12,
          f"min u {u.min():.2e}, final u max {abs(u[:, -1]).max():.2e}")
    # and 'keeping' never enters the ego's lane
    b7b = cutin_belief(p_change=0.0, sd_pos=0.0)
    f7b = sample_futures(b7b, n=500, seed=5, sd_vlat=SD_VLAT)
    u_keep = b7b.toward_sign * f7b.y
    check("(7b) under 'keeping' the other never crosses the lane boundary toward the ego",
          u_keep.min() >= 1.75 - 1e-9, f"min u {u_keep.min():.4f}")

    # --- policies ----------------------------------------------------------------------
    b = cutin_belief()
    paths = {k: ego_rollout(b, k) for k in CUTIN_MENU}
    # (8)
    check("(8) 'continue' holds speed to 1e-12",
          np.max(np.abs(paths["continue"].v - b.v_ego)) < 1e-12,
          f"{np.max(np.abs(paths['continue'].v - b.v_ego)):.2e}")
    # (9)
    ph = paths["brake_hard"]
    t_stop = b.v_ego / 6.0
    k = int(np.argmax(ph.v <= 0.0))
    check("(9) 'brake_hard' from v reaches zero at v/6 s within one step",
          abs(ph.tau[k] - t_stop) <= DT_S + 1e-9, f"zero at {ph.tau[k]:.2f} s, v/6 = {t_stop:.2f} s")
    check("(9b) the speed is clipped at zero and the distance stops growing",
          ph.v.min() >= 0.0 and abs(ph.x[-1] - ph.x[k]) < 1e-9)
    # (10) the left turn's proceed reproduces conflict.planned_path
    tt = np.arange(0.0, 25.0, 0.1)
    ang = np.clip((tt - 10.0) / 6.0, 0.0, 1.0) * (np.pi / 2)
    ex = np.cumsum(np.cos(ang) * 10.0 * 0.1)
    ey = np.cumsum(np.sin(ang) * 10.0 * 0.1)
    ego_body = Body(t=tt, x=ex, y=ey, heading=ang, length=4.2, width=1.72)
    pp = planned_path(ego_body, 13.5, DT_S, v_window=1.0)
    frame = Frame(float(np.interp(13.5, tt, ex)), float(np.interp(13.5, tt, ey)),
                  float(np.interp(13.5, tt, ang)))
    px, py = frame.to_frame(pp.x, pp.y)
    s_rec = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(px), np.diff(py)))])
    tau_r = horizon_steps(HORIZON_S, DT_S)
    s_at_tau = np.interp(tau_r, pp.tau, s_rec)
    b10 = cutin_belief(v_ego=10.0, x_rel=60.0, y_rel=0.0, vx_oth=-15.0, v_oth=15.0)
    path10 = ltap_rollout(b10, LTAP_CONTINUE, px, py, s_at_tau, s_conf=20.0)
    ref_x = np.interp(tau_r, pp.tau, px)
    ref_y = np.interp(tau_r, pp.tau, py)
    err = float(max(np.abs(path10.x - ref_x).max(), np.abs(path10.y - ref_y).max()))
    check("(10) the left turn's 'proceed' reproduces conflict.planned_path of the ego body",
          err < 1e-9, f"max |error| {err:.2e} m")
    path10w = ltap_rollout(b10, "wait", px, py, s_at_tau, s_conf=8.0)
    s_w = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(path10w.x), np.diff(path10w.y)))])
    check("(10b) 'wait' stops before the crossing point and stays there",
          s_w.max() <= 8.0 + 1e-6 and path10w.v[-1] == 0.0, f"arc {s_w.max():.3f} m")

    # --- scoring -----------------------------------------------------------------------
    p = cutin_params(b.v_ego)
    fut = sample_futures(b, n=100, seed=2)
    g = g_by_policy(b, fut, paths, p)
    # (11)
    check("(11) G >= 0 for every policy", all(v >= 0.0 for v in g.values()),
          ", ".join(f"{k} {v:.1f}" for k, v in g.items()))
    # (12)
    paths12 = dict(paths)
    paths12["continue_again"] = ego_rollout(b, "continue")
    g12 = g_by_policy(b, fut, paths12, p)
    check("(12) two identical policies give identical G",
          g12["continue"] == g12["continue_again"],
          f"{g12['continue']:.9f} vs {g12['continue_again']:.9f}")
    # (13) no intention, a lane-keeping other, no perturbation -> Delta G = 0
    b13 = cutin_belief(p_change=0.0, vy_oth=0.0, sd_pos=0.0, x_rel=60.0, v_oth=30.0, vx_oth=30.0)
    f13 = sample_futures(b13, sd_vlat=0.0, sd_a=0.0, n=20, seed=4)
    paths13 = {k: ego_rollout(b13, k) for k in CUTIN_MENU}
    g13 = g_by_policy(b13, f13, paths13, cutin_params(b13.v_ego))
    check("(13) with p_change = 0, a lane-keeping other and no perturbation, Delta G = 0 exactly",
          delta_g(g13) == 0.0, f"Delta G = {delta_g(g13):.6e}; " +
          ", ".join(f"{k} {v:.3f}" for k, v in g13.items()))
    # (14) a certain collision under continue and none under brake
    # A stationary obstacle in lane at 5 m/s, where braking genuinely avoids the collision at
    # both gaps (at 30 m/s nothing in the menu can, and the contrast would be between two
    # certain collisions rather than the one the claim is about).
    dgs = {}
    for gap in (10.0, 30.0):
        b14 = cutin_belief(x_rel=gap, y_rel=0.0, v_ego=5.0, v_oth=0.0, vx_oth=0.0,
                           p_change=0.0, sd_pos=0.0)
        f14 = sample_futures(b14, sd_vlat=0.0, sd_a=0.0, n=20, seed=6)
        p14 = {k: ego_rollout(b14, k) for k in CUTIN_MENU}
        dgs[gap] = delta_g(g_by_policy(b14, f14, p14, cutin_params(b14.v_ego)))
    check("(14) a certain collision under 'continue' and none under braking gives Delta G > 0, "
          "and Delta G at a 10 m gap exceeds Delta G at 30 m",
          dgs[10.0] > 0.0 and dgs[10.0] > dgs[30.0],
          f"10 m {dgs[10.0]:.1f}, 30 m {dgs[30.0]:.1f}")
    # (15) variant B differs only in the safety term
    tA = log_terms(b, paths["continue"], fut, p)
    tB = log_terms(b, paths["continue"], fut, replace(p, safety_term_enabled=False))
    same = all(np.array_equal(tA[k], tB[k]) for k in tA if k != "safety")
    check("(15) variant B differs from variant A only in the safety term",
          same and not np.array_equal(tA["safety"], tB["safety"])
          and np.all(tB["safety"] == 0.0),
          f"other five identical: {same}")
    # (16) the flag at its default is bit-identical to the committed behavior
    from comfortzone.cutin import cutin_obs, cutin_params as stage_params, load_cutin_trace
    from comfortzone.czb_data import RANDOM_CUTIN_TRACES
    from aidriver.preferences import (inverse_tau, log_accel_pref, log_collision_pref,
                                      log_lateral_pref, log_safety_pref, log_speed_pref,
                                      log_steer_pref)
    tr = load_cutin_trace(RANDOM_CUTIN_TRACES["TTC4"])
    pp = stage_params(tr)
    obs = cutin_obs(tr, pp)
    terms = log_preference_terms(obs, pp)
    obs2 = dict(obs)
    obs2["tau_inv"] = inverse_tau(obs2["dx"], obs2["v"], obs2["v_other"], pp)
    ref = {
        "speed": log_speed_pref(np.asarray(obs2["v"], float), pp),
        "accel": log_accel_pref(np.asarray(obs2["a"], float), pp,
                                a_lat=np.asarray(obs2["a_lat"], float)),
        "steer": log_steer_pref(np.asarray(obs2["omega"], float), pp),
        "lateral": log_lateral_pref(np.asarray(obs2["y"], float), pp),
        "collision": log_collision_pref(obs2, pp),
        "safety": log_safety_pref(obs2, pp),
    }
    bitwise = all(np.array_equal(np.broadcast_to(ref[k], terms[k].shape), terms[k]) for k in ref)
    check("(16) the new flag at its default leaves log_preference_terms bit-identical to the "
          "released six terms on cutin_obs of one study-1 trace",
          pp.safety_term_enabled and bitwise,
          f"default {pp.safety_term_enabled}, bitwise {bitwise}")

    # (19) the weighted fan (card RE.1: the released model's particle fan carries weights)
    n19 = fut.n
    g_flat = expected_free_energy(b, paths["continue"], fut, p)
    g_unif = expected_free_energy(b, paths["continue"], fut, p, weights=np.ones(n19))
    g_skew = expected_free_energy(b, paths["continue"], fut, p,
                                  weights=np.arange(1.0, n19 + 1.0))
    # not bit-exact: np.mean and the einsum sum in a different order, which on ~10^4 nats
    # leaves a few units in the last place.
    check("(19) uniform weights reproduce the unweighted fan, and a non-uniform one does not",
          abs(g_flat - g_unif) < 1e-6 and abs(g_skew - g_flat) > 1.0,
          f"{g_flat:.9f} / {g_unif:.9f} / {g_skew:.9f}")
    w_one = np.zeros(n19); w_one[3] = 1.0
    one_fut = Futures(tau=fut.tau, x=fut.x[3:4], y=fut.y[3:4], v=fut.v[3:4], vx=fut.vx[3:4],
                      vy=fut.vy[3:4], heading=fut.heading[3:4], changing=fut.changing[3:4])
    check("(19b) a weight of 1 on one sample equals scoring that sample alone",
          abs(expected_free_energy(b, paths["continue"], fut, p, weights=w_one)
              - expected_free_energy(b, paths["continue"], one_fut, p)) < 1e-9)

    # (20-23) the steering policies (card JJ.2b)
    from rollout.policies import (LANE_CHANGE_D, STEER_MENU, SWERVE_T, cutin_menu_paths,
                                  steer_rollout)
    from rollout.efe import observations
    sp = steer_rollout(b, "steer")
    sw_ = steer_rollout(b, "swerve")
    check("(20) a steering policy moves AWAY from the intruder and reaches one lane width",
          np.sign(sp.y[-1]) == -np.sign(b.y_rel)
          and abs(abs(sp.y[-1]) - LANE_CHANGE_D) < 1e-9,
          f"y_end {sp.y[-1]:+.3f} against y_rel {b.y_rel:+.2f}")
    b_mirror = cutin_belief(y_rel=-b.y_rel)
    sp_m = steer_rollout(b_mirror, "steer")
    check("(21) mirroring the scene's lateral sign mirrors the escape",
          np.allclose(sp_m.y, -sp.y, atol=0) and np.allclose(sp_m.omega, -sp.omega, atol=0))
    peak = LANE_CHANGE_D / 2 * (np.pi / SWERVE_T) ** 2
    # the grid samples tau at 0.2 s, so the discrete maximum is the sample nearest the analytic
    # peak (here tau = 1.4 s, |cos| = 0.978), not the peak itself
    check("(22) the swerve's peak lateral acceleration is D/2 (pi/T)^2 to the grid's resolution, "
          "and its yaw rate is near the 0.24 rad/s the released planner chooses on this design "
          "(card RE.1 part C)",
          abs(np.abs(sw_.a_lat).max() - peak) / peak < 0.05
          and 0.15 <= np.abs(sw_.omega).max() <= 0.30,
          f"a_lat {np.abs(sw_.a_lat).max():.2f} against {peak:.2f}, "
          f"|omega| {np.abs(sw_.omega).max():.3f}")
    obs_st = observations(b, sw_, fut)
    obs_br = observations(b, paths["brake"], fut)
    check("(23) the steering channels reach the preference function, and a non-steering policy "
          "still passes exact zeros",
          np.abs(obs_st["omega"]).max() > 0.1 and np.abs(obs_st["a_lat"]).max() > 1.0
          and np.all(obs_br["omega"] == 0.0) and np.all(obs_br["a_lat"] == 0.0))
    t_st = log_terms(b, sw_, fut, p)
    t_br = log_terms(b, paths["brake"], fut, p)
    check("(23b) and the released steering term charges for the manoeuvre",
          t_st["steer"].mean() < t_br["steer"].mean(),
          f"{t_st['steer'].mean():.1f} against {t_br['steer'].mean():.1f}")
    m_no = cutin_menu_paths(b, steering=False)
    m_st = cutin_menu_paths(b, steering=True)
    check("(23c) cutin_menu_paths without steering is the ruling JJ1.Q1 menu unchanged",
          set(m_no) == set(CUTIN_MENU) and set(m_st) == set(CUTIN_MENU) | set(STEER_MENU)
          and np.array_equal(m_no["continue"].x, m_st["continue"].x))

    # --- boundary ----------------------------------------------------------------------
    # (17)
    a_no = axis(np.array([1.0, 2.0, 4.0]))
    a_yes = axis(np.array([0.0, 2.0, 4.0]))
    check("(17) the zero rule is applied only when a zero exists",
          (not a_no.zero_rule_applied) and a_no.offset == 0.0
          and a_yes.zero_rule_applied and a_yes.n_zero == 1 and a_yes.offset == 1.0,
          f"offsets {a_no.offset} and {a_yes.offset}")
    check("(17b) without a zero the axis is exactly log Delta G",
          np.allclose(a_no.values, np.log([1.0, 2.0, 4.0]), atol=0))
    # (18) the standard error falls as 1/sqrt(n)
    b18 = cutin_belief(x_rel=18.0, y_rel=3.5, vy_oth=-0.8, p_change=0.6)
    p18 = cutin_params(b18.v_ego)
    ses = {}
    for n in (50, 200, 800):
        vals = []
        for s in range(8):
            f = sample_futures(b18, n=n, seed=100 + s)
            pp18 = {k: ego_rollout(b18, k) for k in CUTIN_MENU}
            vals.append(delta_g(g_by_policy(b18, f, pp18, p18)))
        ses[n] = mc_standard_error(vals)
    r1 = ses[50] / ses[200] / 2.0
    r2 = ses[200] / ses[800] / 2.0
    check("(18) the Monte Carlo standard error falls as 1/sqrt(n) across n in {50, 200, 800} "
          "within a factor of 1.5",
          1 / 1.5 <= r1 <= 1.5 and 1 / 1.5 <= r2 <= 1.5,
          f"SE {ses[50]:.1f}/{ses[200]:.1f}/{ses[800]:.1f}, ratios/2 {r1:.2f} and {r2:.2f}")

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    main()
