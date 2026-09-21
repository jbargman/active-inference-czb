"""
Property tests for admissibility (src/rollout/admissible.py, card S1.6).

Claims: the collision test is the released box, so wherever it fires the released collision term
is the collision cost and wherever it does not the term is not; the comfort cost is zero for
`continue` at the desired speed and rises with every step of deceleration, so the cheapest
admissible policy IS the mildest admissible deceleration; a lane-keeping other leaves `continue`
admissible and the price at exactly zero; a certain collision under `continue` makes it
inadmissible and the price positive, larger at a short gap than at a long one; loosening alpha
never raises the price; a delay before braking never lowers it; when nothing is admissible the
price is one menu step beyond the hardest policy and is flagged; a zero delay reproduces the
constant-acceleration rollout.

Run: python tests/test_admissible.py
"""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidriver.preferences import PreferenceParams, log_collision_pref  # noqa: E402
from rollout.admissible import (A_MAX_RELEASED, MENU_STEP, brake_menu, collides,  # noqa: E402
                                comfort_cost, delayed_rollout, price_of_safety)
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, Belief  # noqa: E402
from rollout.efe import observations  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import sample_futures  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def cutin_belief(**kw) -> Belief:
    base = dict(x_rel=25.0, y_rel=3.5, v_ego=30.0, v_oth=25.0, vy_oth=0.0,
                sd_pos=FLOORS_STUDY2.sd_pos, sd_vy=FLOORS_STUDY2.sd_v_lat,
                p_change=P_CHANGE_PRIOR, ego_len=4.2, ego_wid=1.72, oth_len=4.6, oth_wid=1.88,
                vx_oth=25.0, floors=FLOORS_STUDY2, name="synthetic cut-in")
    base.update(kw)
    return Belief(**base)


def strand1(v: float) -> PreferenceParams:
    return PreferenceParams(v_desired=v, sigma_v=1.0, sigma_a=0.5, safety_term_enabled=False)


def main():
    p = strand1(30.0)

    # --- the menu ------------------------------------------------------------------------
    menu = brake_menu()
    check("the menu runs from continue to the released a_max in steps of 0.25",
          menu["continue"] == 0.0 and min(menu.values()) == -A_MAX_RELEASED
          and len(menu) == int(A_MAX_RELEASED / MENU_STEP) + 1, f"{len(menu)} policies")

    # --- the collision test is the released box ---------------------------------------------
    b = cutin_belief(p_change=1.0, vy_oth=-1.2)
    fut = sample_futures(b, seed=0)
    ego = ego_rollout(b, "continue")
    obs = observations(b, ego, fut)
    obs["tau_inv"] = np.zeros_like(obs["dx"])
    pc = replace(p, g_collision=-12345.0, severity_floor=1.0)
    term = log_collision_pref(obs, pc)
    box = np.isclose(term, -12345.0)
    check("wherever the released collision term charges the collision cost, `collides` fires,"
          " and nowhere else", bool(np.array_equal(box.any(axis=1), collides(ego, fut, p))),
          f"{int(box.any(axis=1).sum())} of {fut.n} futures collide under continue")

    # --- the comfort cost ------------------------------------------------------------------
    check("continue at the desired speed costs nothing", comfort_cost(ego, p) == 0.0)
    costs = [comfort_cost(delayed_rollout(b, a, 0.0), p) for a in sorted(menu.values(), reverse=True)]
    check("the comfort cost rises with every step of deceleration",
          bool(np.all(np.diff(costs) > 0)), f"{costs[1]:.1f} ... {costs[-1]:.1f} nats")
    r0, r1 = delayed_rollout(b, -3.0, 0.0), ego_rollout(b, "p", menu={"p": -3.0})
    check("a zero delay reproduces the constant-acceleration rollout",
          np.allclose(r0.x, r1.x) and np.allclose(r0.v, r1.v) and np.allclose(r0.a, r1.a))
    rd = delayed_rollout(b, -3.0, 1.0)
    check("a delayed brake holds speed through the delay and has travelled further",
          np.allclose(rd.v[rd.tau <= 1.0], 30.0) and bool(np.all(rd.x >= r0.x - 1e-9))
          and abs(rd.v[-1] - (30.0 - 3.0 * 5.0)) < 1e-9)
    stop = delayed_rollout(cutin_belief(v_ego=10.0), -8.0, 0.0)
    check("a policy that reaches a standstill stays there with zero effort",
          stop.v[-1] == 0.0 and stop.a[-1] == 0.0 and abs(stop.x[-1] - 10.0 ** 2 / 16.0) < 1e-9)

    # --- the price of safety ------------------------------------------------------------------
    keep = cutin_belief(p_change=0.0)
    res_jj1 = price_of_safety(keep, sample_futures(keep, seed=0), p)
    check("CARD JJ.1'S FAN: an other that is CERTAIN to keep its lane still collides with a"
          " passing ego in a sizeable share of futures (its centre is clipped at the ego's lane"
          " edge, inside the released collision box)",
          0.10 < res_jj1.p_collide_continue < 0.30 and not res_jj1.continue_admissible,
          f"P(collide | continue) = {res_jj1.p_collide_continue:.3f}")
    fk = sample_futures(keep, seed=0, keep_body_in_lane=True)
    res = price_of_safety(keep, fk, p)
    check("with the other's BODY keeping its lane, continue is admissible and the price is"
          " exactly zero", res.continue_admissible and res.price == 0.0 and res.a_star == 0.0
          and res.p_collide_continue == 0.0)
    changing = cutin_belief(p_change=1.0, vy_oth=-1.2)
    f0 = sample_futures(changing, seed=3)
    f1 = sample_futures(changing, seed=3, keep_body_in_lane=True)
    check("the flag changes nothing for a future that is changing lanes (same draws, same paths)",
          np.array_equal(f0.x, f1.x) and np.array_equal(f0.y, f1.y))
    check("the flag moves only the clip: the longitudinal draws are identical under keeping",
          np.array_equal(sample_futures(keep, seed=0).x, fk.x)
          and float(np.abs(fk.y).min()) >= 1.75 + 0.5 * keep.oth_wid - 1e-12)

    near = cutin_belief(p_change=1.0, vy_oth=-1.2, x_rel=15.0)
    far = cutin_belief(p_change=1.0, vy_oth=-1.2, x_rel=30.0)
    rn = price_of_safety(near, sample_futures(near, seed=0), p)
    rf = price_of_safety(far, sample_futures(far, seed=0), p)
    check("a certain lane change ahead makes continue inadmissible and the price positive",
          not rn.continue_admissible and rn.price > 0 and not rf.continue_admissible
          and rf.price > 0, f"a* {rn.a_star:g} at 15 m, {rf.a_star:g} at 30 m")
    check("the price is larger at the shorter gap", rn.price > rf.price and rn.a_star > rf.a_star)
    check("the cheapest admissible policy is the mildest admissible deceleration",
          all(s > 0 for k, s in rf.p_collide.items() if -brake_menu()[k] < rf.a_star)
          and rf.p_collide[f"brake_{rf.a_star:.2f}"] == 0.0)

    loose = price_of_safety(far, sample_futures(far, seed=0), p, alpha=0.10)
    check("loosening alpha never raises the price", loose.price <= rf.price)
    late = price_of_safety(far, sample_futures(far, seed=0), p, delay_s=1.0)
    check("a delay before braking never lowers the price",
          late.none_admissible or late.a_star >= rf.a_star, f"a* {late.a_star:g}")

    hopeless = cutin_belief(p_change=1.0, vy_oth=-1.2, x_rel=6.0, y_rel=0.5, v_ego=40.0)
    rh = price_of_safety(hopeless, sample_futures(hopeless, seed=0), p)
    beyond = comfort_cost(delayed_rollout(hopeless, -(A_MAX_RELEASED + MENU_STEP), 0.0),
                          strand1(40.0))
    rh2 = price_of_safety(hopeless, sample_futures(hopeless, seed=0), strand1(40.0))
    check("when nothing is admissible the price is one menu step beyond the hardest policy",
          rh.none_admissible and np.isnan(rh.a_star) and abs(rh2.price - beyond) < 1e-9)

    mixed = cutin_belief(p_change=0.07, x_rel=15.0)
    fm = sample_futures(mixed, seed=0, keep_body_in_lane=True)
    r_abs = price_of_safety(mixed, fm, p, alpha=0.0)
    r_tol = price_of_safety(mixed, fm, p, alpha=0.20)
    check("at the prior, continue collides in about the prior's share of futures: inadmissible"
          " at alpha 0 and admissible at alpha 0.20 -- the gate is alpha against P(change)",
          0.0 < r_abs.p_collide_continue < 0.20 and not r_abs.continue_admissible
          and r_tol.continue_admissible and r_tol.price == 0.0,
          f"P(collide | continue) = {r_abs.p_collide_continue:.3f}")

    try:
        price_of_safety(mixed, fm, p, alpha=1.0)
        ok = False
    except ValueError:
        ok = True
    check("alpha outside [0, 1) is refused", ok)

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
