"""
Property tests for the released looming preference read alone (src/rollout/looming_pref.py,
card JJ.5), the lane-overlap gate (card JJ.6) and the changepoint filter over the intention
(`rollout.belief`, card JJ.6c).

Claims: the term is the released one-sided tau^-1 Gaussian, max-normalised to zero, so it is zero
whenever the closing rate is below 1/5 s and equals the released code's value above it; under the
in-path reading a lane-keeping other costs exactly zero and a certain lane change costs more than
zero; the cost falls with the gap and with braking; it is read before contact only, so driving
through the lead does not send it to infinity; the fan's intention prior scales it (the gate);
the released "none" reading charges an adjacent-lane vehicle; the continuous reading agrees with
the in-path one where the other is fully in or fully out of the lane.

Run: python tests/test_looming_pref.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidriver.preferences import LOG_2PI, PreferenceParams, _log_gauss  # noqa: E402
from rollout.belief import (FLOORS_STUDY2, P_CHANGE_PRIOR, Belief, filter_intention,  # noqa: E402
                            hazard_for, prospective_change)
from rollout.looming_pref import eps_tau, log_tau_term, p_in_lane, share_in_path  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import sample_futures  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def belief(**kw) -> Belief:
    base = dict(x_rel=25.0, y_rel=3.5, v_ego=30.0, v_oth=25.0, vy_oth=0.0,
                sd_pos=FLOORS_STUDY2.sd_pos, sd_vy=FLOORS_STUDY2.sd_v_lat,
                p_change=P_CHANGE_PRIOR, ego_len=4.2, ego_wid=1.72, oth_len=4.6, oth_wid=1.88,
                vx_oth=25.0, floors=FLOORS_STUDY2, name="synthetic cut-in")
    base.update(kw)
    return Belief(**base)


def main():
    p = PreferenceParams(v_desired=30.0)

    # --- 1 the term itself -----------------------------------------------------------------
    n, T = 3, 4
    obs = {"dx": np.full((n, T), 30.0), "dy": np.zeros((n, T)), "v": np.full((n, T), 30.0),
           "v_other": np.array([[30.0] * T, [27.0] * T, [20.0] * T])}
    lt = log_tau_term(obs, p, "in_path")
    tau_inv = (30.0 - obs["v_other"]) / (30.0 - p.vehicle.length)
    expect = np.where(tau_inv > p.tau_inv_mu,
                      _log_gauss(tau_inv, p.tau_inv_mu, p.tau_inv_sd)
                      + np.log(p.tau_inv_sd) + 0.5 * LOG_2PI, 0.0)
    check("closing slower than 1/5 s costs nothing; faster costs the released one-sided"
          " Gaussian, max-normalised to zero", np.allclose(lt, expect) and lt[0, 0] == 0.0
          and lt[2, 0] < 0.0, f"row costs {lt[:, 0].round(2).tolist()}")
    obs2 = dict(obs, dy=np.full((n, T), 3.5))
    check("a vehicle ahead in the next lane is not in the path: zero under in_path, charged under"
          " none", np.all(log_tau_term(obs2, p, "in_path") == 0.0)
          and np.allclose(log_tau_term(obs2, p, "none"), expect))
    obs3 = dict(obs, dx=np.array([[30.0, 10.0, 4.0, 1.0]] * n))
    lt3 = log_tau_term(obs3, p, "in_path")
    check("read before contact only: once the released box is entered that step and every later"
          " one are zero", np.all(lt3[:, 2:] == 0.0) and lt3[2, 1] < lt3[2, 0])

    # --- 2 on the fan ------------------------------------------------------------------------
    keep = belief(p_change=0.0)
    fk = sample_futures(keep, seed=0, keep_body_in_lane=True)
    check("a lane-keeping other costs exactly zero under in_path",
          eps_tau(keep, ego_rollout(keep, "continue"), fk, p) == 0.0
          and share_in_path(keep, ego_rollout(keep, "continue"), fk, p) == 0.0)
    e_none = eps_tau(keep, ego_rollout(keep, "continue"), fk, p, "none")
    check("the released reading charges the same lane-keeping vehicle, and heavily, because the"
          " ego passes it", e_none > 1e4, f"{e_none:.0f} nats")

    chg = belief(p_change=1.0, vy_oth=-1.2)
    fc = sample_futures(chg, seed=0, keep_body_in_lane=True)
    e_cont = eps_tau(chg, ego_rollout(chg, "continue"), fc, p)
    e_brake = eps_tau(chg, ego_rollout(chg, "brake"), fc, p)
    check("a certain lane change ahead costs more than zero, and braking removes most of it",
          e_cont > 0 and e_brake < 0.1 * e_cont, f"{e_cont:.1f} -> {e_brake:.2f} nats")
    far = belief(p_change=1.0, vy_oth=-1.2, x_rel=60.0)
    e_far = eps_tau(far, ego_rollout(far, "continue"), sample_futures(far, seed=0,
                                                                        keep_body_in_lane=True), p)
    check("the cost falls with the gap", e_far < e_cont, f"{e_cont:.1f} at 25 m, {e_far:.1f} at 60 m")
    through = belief(p_change=1.0, vy_oth=-1.2, x_rel=8.0)
    e_thr = eps_tau(through, ego_rollout(through, "continue"),
                    sample_futures(through, seed=0, keep_body_in_lane=True), p)
    check("driving through the lead does not send the cost to infinity",
          np.isfinite(e_thr) and e_thr < 1e5, f"{e_thr:.0f} nats")

    mixed = belief(p_change=P_CHANGE_PRIOR)
    fm = sample_futures(mixed, seed=0, keep_body_in_lane=True)
    e_mix = eps_tau(mixed, ego_rollout(mixed, "continue"), fm, p)
    s_mix = share_in_path(mixed, ego_rollout(mixed, "continue"), fm, p)
    check("at the prior the cost is the certain-change cost scaled by about the share of futures"
          " in the path: the intention belief IS the gate",
          0.0 < s_mix < 0.2 and 0.3 < e_mix / (s_mix * e_cont) < 3.0,
          f"share {s_mix:.3f}, ratio {e_mix / (s_mix * e_cont):.2f}")

    pc = PreferenceParams(v_desired=30.0, lane_entry_continuous=True, lane_entry_shape_k=12.0)
    e_in = eps_tau(chg, ego_rollout(chg, "continue"), fc, pc, "in_path")
    e_c = eps_tau(chg, ego_rollout(chg, "continue"), fc, pc, "continuous")
    check("the continuous reading agrees with in_path to within a third on a certain change (they"
          " differ only while the body straddles the line)", abs(e_c - e_in) < 0.34 * e_in,
          f"{e_in:.1f} against {e_c:.1f}")

    # --- 3 the lane-overlap gate (card JJ.6) -------------------------------------------------
    fk6 = sample_futures(keep, seed=0, keep_body_in_lane=True)
    check("a certain keeper is never in the ego's lane",
          p_in_lane(keep, ego_rollout(keep, "continue"), fk6, 3.0) == 0.0)
    fc6 = sample_futures(chg, seed=0, keep_body_in_lane=True)
    check("a certain changer is in the lane within 3 s in every future, and in none within 0.2 s",
          p_in_lane(chg, ego_rollout(chg, "continue"), fc6, 3.0) == 1.0
          and p_in_lane(chg, ego_rollout(chg, "continue"), fc6, 0.2) == 0.0)
    pm = p_in_lane(mixed, ego_rollout(mixed, "continue"), fm, 6.0)
    check("at the prior the gate is about the prior", abs(pm - P_CHANGE_PRIOR) < 0.04, f"{pm:.3f}")
    check("the gate never falls as the horizon grows",
          all(p_in_lane(chg, ego_rollout(chg, "continue"), fc6, h1)
              <= p_in_lane(chg, ego_rollout(chg, "continue"), fc6, h2)
              for h1, h2 in ((0.5, 1.0), (1.0, 2.0), (2.0, 4.0))))
    obs4 = dict(obs, dy=np.full((n, T), 2.5), w_other=np.full((n, T), 1.88))
    check("lane_overlap charges a body straddling the line that the collision box does not",
          np.all(log_tau_term(obs4, p, "in_path") == 0.0)
          and np.allclose(log_tau_term(obs4, p, "lane_overlap"), expect))

    # --- 4 the changepoint filter (card JJ.6c) --------------------------------------------
    h = hazard_for(P_CHANGE_PRIOR, 3.0, 0.3)
    check("the hazard reproduces the prospective prior over the horizon exactly",
          abs(prospective_change(0.0, h, 3.0, 0.3) - P_CHANGE_PRIOR) < 1e-12, f"h = {h:.5f}")
    quiet = filter_intention([0.0] * 30, 0.33, h)
    check("a long quiet track leaves P(changing now) near zero and the prospective gate at the"
          " prior", quiet < 1e-3 and abs(prospective_change(quiet, h, 3.0, 0.3) - P_CHANGE_PRIOR) < 2e-3)
    p1 = filter_intention([0.0] * 20 + [-0.77], 0.33, h)
    p3 = filter_intention([0.0] * 20 + [-0.77] * 3, 0.33, h)
    check("evidence accumulates: three windows of a slow lane change convince where one does not",
          p1 < 0.1 and p3 > 0.7, f"{p1:.3f} -> {p3:.3f}")
    check("a fast lane change convinces in one window",
          filter_intention([0.0] * 20 + [-1.5], 0.33, h) > 0.99)
    check("the sign convention: motion away from the ego is evidence for keeping",
          filter_intention([0.0] * 20 + [+0.77] * 3, 0.33, h) < 1e-3)
    check("the filter never leaves [0, 1] and the prospective gate never falls below P(now)",
          all(0 <= filter_intention(np.random.default_rng(1).normal(0, 2, 40), 0.33, h) <= 1
              for _ in range(3)) and prospective_change(0.5, h, 3.0, 0.3) >= 0.5)

    try:
        log_tau_term(obs, p, "other")
        ok = False
    except ValueError:
        ok = True
    check("an unknown gate is refused", ok)

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
