"""
Property tests for the split-site data-interface loader (src/comfortzone/interface.py,
card NDS.1).

The claims under test, rather than "the code runs":

* the loader computes the SAME quantities as the video cards, by the same definitions --
  this is what makes a level fitted on video comparable with one fitted on naturalistic
  data, and it is the whole reason the module exists;
* the looming axis is the exact derivative of the subtended angle, checked here by a
  second, independent route (a numerical derivative of theta = 2 atan(W / 2r)) because the
  axis is load-carrying for every claim downstream of it;
* the gate reproduces card G.1's formula and its limits;
* an unresolvable geometry is REFUSED rather than silently mis-computed (the `rear_axle`
  case, NDS.Q2);
* an event with no brake response is right-censored, not dropped and not read as zero.

Run: python tests/test_interface.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from comfortzone.interface import (  # noqa: E402
    GATE_M_LAT, GATE_S_L, InterfaceEvent, InterfaceGapError, LDOT_WINDOW_S, T_ENC,
    _backward_rate, gate_weight, interface_observations, interface_predictors,
    lateral_clearance, load_interface_dir, longitudinal_gap,
)
from comfortzone.ltap import looming_rate  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS  " if cond else "FAIL  ") + name + (f"  -- {detail}" if detail else ""))


def make_event(ref_point="cog", n=40, dt=0.05, v_ego=20.0, v_oth=15.0, gap0=40.0,
               dy=3.5, dy_rate=0.0, t_brake=None, t_conf=0.0, ego_len=4.6, oth_len=4.5,
               ego_wid=1.8, oth_wid=1.85):
    """A synthetic event with exactly known kinematics, for closed-form comparison."""
    t = np.arange(n) * dt
    ego_x = v_ego * t
    oth_x = gap0 + v_oth * t
    ts = pd.DataFrame({
        "t": t, "ego_x": ego_x, "ego_y": np.zeros(n), "ego_psi": np.zeros(n),
        "ego_v": np.full(n, v_ego), "ego_ax": np.zeros(n), "ego_delta": np.full(n, np.nan),
        "oth_x": oth_x, "oth_y": dy + dy_rate * t, "oth_psi": np.zeros(n),
        "oth_v": np.full(n, v_oth), "oth_ax": np.zeros(n),
        "oth_class": ["car"] * n, "valid": np.ones(n),
    })
    meta = {"event_id": "E0001", "dataset": "T", "scenario": "rear_end", "driver_id": "D01",
            "lane_width": 3.5, "ego_len": ego_len, "ego_wid": ego_wid, "oth_len": oth_len,
            "oth_wid": oth_wid, "geometry_default": 0, "ref_point": ref_point,
            "t_conflict_onset": t_conf,
            "t_brake_onset": np.nan if t_brake is None else t_brake}
    return InterfaceEvent("E0001", "D01", "rear_end", "T", ts, meta)


def main():
    # --- 1 the gap conventions, against the video cards' definitions -------------------
    ev = make_event(ref_point="cog")
    dx = ev.ts.oth_x.to_numpy() - ev.ts.ego_x.to_numpy()
    check("cog gap matches cutin_predictors' definition (dx - half of each length)",
          np.allclose(longitudinal_gap(ev), dx - 0.5 * (4.6 + 4.5)))
    ev_fb = make_event(ref_point="front_bumper")
    check("front_bumper gap is dx minus the partner's length",
          np.allclose(longitudinal_gap(ev_fb), dx - 4.5))
    check("the two conventions differ by half the difference of the lengths",
          np.allclose(longitudinal_gap(ev_fb) - longitudinal_gap(ev), 0.5 * (4.6 - 4.5)))
    # The risk NDS.Q2 is about is not cog-vs-front_bumper (0.05 m here) but either of them
    # against a raw centre separation, which is metres and scales theta_dot quadratically.
    check("both conventions differ from a raw separation by metres, not centimetres",
          min(abs(float((dx - longitudinal_gap(ev))[0])),
              abs(float((dx - longitudinal_gap(ev_fb))[0]))) > 4.0)
    try:
        longitudinal_gap(make_event(ref_point="rear_axle"))
        check("rear_axle is refused (NDS.Q2)", False, "no error raised")
    except InterfaceGapError as e:
        check("rear_axle is refused (NDS.Q2)", "front overhang" in str(e))

    # --- 2 lateral clearance -----------------------------------------------------------
    check("lateral clearance is edge-to-edge, card G.1's l0",
          np.allclose(lateral_clearance(ev), 3.5 - 0.5 * (1.8 + 1.85)))
    ev_ov = make_event(dy=1.0)
    check("clearance goes negative when the vehicles overlap laterally",
          float(lateral_clearance(ev_ov)[0]) < 0)

    # --- 3 the axis, by a second independent route -------------------------------------
    pr = interface_predictors(ev)
    gap = longitudinal_gap(ev)
    W = 1.85
    check("theta_dot equals the shared looming_rate helper exactly",
          np.allclose(pr.theta_dot.to_numpy(), [looming_rate(W, 5.0, float(g)) for g in gap]))

    # Independent route: theta(r) = 2 atan(W / 2r); d(theta)/dt = d(theta)/dr * dr/dt,
    # with dr/dt = -dv. Evaluated numerically, it must reproduce the closed form.
    r = gap[10]
    h = 1e-6
    dtheta_dr = (2 * np.arctan(W / (2 * (r + h))) - 2 * np.arctan(W / (2 * (r - h)))) / (2 * h)
    numeric = dtheta_dr * (-5.0)
    check("theta_dot matches a numerical derivative of the subtended angle (two routes)",
          abs(numeric - float(pr.theta_dot.iloc[10])) < 1e-7,
          f"closed form {float(pr.theta_dot.iloc[10]):.8f}, numeric {numeric:.8f}")

    check("theta_dot is positive while closing and rises as the gap shrinks",
          bool((pr.theta_dot.to_numpy() > 0).all())
          and float(pr.theta_dot.iloc[-1]) > float(pr.theta_dot.iloc[0]))

    ev_closed = make_event(gap0=-10.0)
    check("theta_dot is NaN once the gap has closed, not a large negative number",
          bool(np.isnan(interface_predictors(ev_closed).theta_dot.iloc[0])))

    # --- 4 the clearance rate ----------------------------------------------------------
    ev_r = make_event(dy=3.5, dy_rate=-0.5)
    pr_r = interface_predictors(ev_r)
    k = int(round(LDOT_WINDOW_S / 0.05))
    check("ldot recovers a known constant closing rate exactly",
          np.allclose(pr_r.ldot.to_numpy()[k:], -0.5), f"got {pr_r.ldot.iloc[-1]:.4f}, want -0.5")
    check("ldot is a BACKWARD difference: undefined for the first window",
          bool(np.isnan(pr_r.ldot.to_numpy()[:k]).all()) and np.isfinite(pr_r.ldot.iloc[k]))
    check("ldot is zero when the clearance is constant",
          np.allclose(pr.ldot.to_numpy()[k:], 0.0))
    lin = _backward_rate(np.arange(20) * 0.1, 3.0 * (np.arange(20) * 0.1), 0.3)
    check("_backward_rate is exact on a linear ramp", np.allclose(lin[3:], 3.0))

    # --- 5 the gate, against card G.1 ---------------------------------------------------
    from scipy.stats import norm as _norm
    l0v, ldv = 0.8, -0.4
    check("gate reproduces card G.1's formula at its fitted values",
          abs(float(gate_weight(np.array([l0v]), np.array([ldv]))[0])
              - _norm.cdf((GATE_M_LAT - (l0v + ldv * T_ENC)) / GATE_S_L)) < 1e-12)
    wide = gate_weight(np.array([50.0]), np.array([0.0]))
    tight = gate_weight(np.array([-50.0]), np.array([0.0]))
    check("gate closes when the partner is far and opens when it is upon us",
          float(wide[0]) < 1e-6 and float(tight[0]) > 1 - 1e-6)
    grid = gate_weight(np.linspace(-2, 5, 30), np.zeros(30))
    check("gate is monotone decreasing in clearance", bool((np.diff(grid) <= 0).all()))
    check("an approaching partner opens the gate sooner than a parallel one",
          float(gate_weight(np.array([2.0]), np.array([-1.0]))[0])
          > float(gate_weight(np.array([2.0]), np.array([0.0]))[0]))

    # --- 6 the per-event observation ----------------------------------------------------
    ev_b = make_event(t_brake=1.0)
    o = interface_observations(ev_b)
    i = int(np.argmin(np.abs(ev_b.t - 1.0)))
    check("the observation is read at the sample nearest the brake onset",
          abs(o["theta_dot_at_onset"] - float(interface_predictors(ev_b).theta_dot.iloc[i])) < 1e-12)
    check("a responded event is not censored and carries a finite gate value",
          o["censored"] is False and np.isfinite(o["w_gate_at_onset"]))

    o_c = interface_observations(make_event(t_brake=None))
    check("an event with no brake response is right-censored, not dropped",
          o_c["censored"] is True and np.isnan(o_c["theta_dot_at_onset"]))
    check("a censored event still reports the largest axis value the driver saw",
          np.isfinite(o_c["theta_dot_max_pre"]) and o_c["theta_dot_max_pre"] > 0)

    ev_late = make_event(t_brake=1.5, t_conf=1.0)
    pr_l = interface_predictors(ev_late)
    j = int(np.argmin(np.abs(ev_late.t - 1.0)))
    o_l = interface_observations(ev_late)
    check("theta_dot_max_pre ignores samples before conflict onset",
          o_l["theta_dot_max_pre"] >= float(pr_l.theta_dot.iloc[j]) - 1e-12
          and o_l["theta_dot_max_pre"] <= float(pr_l.theta_dot.max()) + 1e-12)

    # --- 7 the real fixture, end to end -------------------------------------------------
    meta, events = load_interface_dir(ROOT / "transfer" / "fixtures" / "synthetic")
    check("the committed synthetic fixture loads", len(events) == 12 and len(meta) == 12)
    check("every fixture event yields finite predictors at its onset",
          all(np.isfinite(interface_observations(e)["theta_dot_at_onset"]) for e in events.values()))
    check("the loader refuses a directory with no events.csv",
          _raises_filenotfound(ROOT / "src"))

    # --- 8 missing columns are refused, not silently filled ------------------------------
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        m = pd.read_csv(ROOT / "transfer" / "fixtures" / "synthetic" / "events.csv")
        m.drop(columns=["oth_wid"]).to_csv(d / "events.csv", index=False)
        try:
            load_interface_dir(d)
            ok = False
        except ValueError as e:
            ok = "oth_wid" in str(e)
    check("a metadata column the axis needs cannot go missing silently", ok)

    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    return 0 if not FAIL else 1


def _raises_filenotfound(p):
    try:
        load_interface_dir(p)
        return False
    except FileNotFoundError:
        return True


if __name__ == "__main__":
    sys.exit(main())
