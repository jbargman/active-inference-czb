"""
Property tests for the left-turn-across-path loader (src/comfortzone/ltap.py, card B.3.v2).

The checks are the ones `docs/ltap_construction_note.md` section 2 lists, plus the
cross-check against `replication/czb/out/ltap_geometry.csv` (the note's own numbers, from a
separate code path).

TWO of the note's claims are NOT true of the stimuli as measured, and the checks below say
so rather than being tuned until they pass. Both are properties of the stimulus set, not of
the loader:

* **Turn onset spans 0.201 s, not 0.2 s.** Onset is quantised to the trace's ~0.1004 s
  sample grid, so "within 0.2 s" means "within two samples"; the span is exactly two
  samples plus 0.001 s of grid drift. The check allows half a sample of slack and prints
  the measured span.
* **The 70 km/h distance is NOT within 5% of 19.4/13.9 times the 50 km/h distance at every
  PET.** Eight of nine levels are (worst 3.6%); PET 1.0 is +6.3% at the decision moment
  (+7.0% at turn onset), because that pair's oncoming start positions differ by ~4.5 m more
  than the speed ratio -- the same imperfection that makes PET 1.0 the worst-matched pair
  on time (TTA 0.227 s apart, against 0.008-0.216 s elsewhere; the note's section 0 claims
  0.2 s). The PET 1.0 exception is asserted explicitly, so if the stimulus set or the
  decision moment changes, this test breaks and the exception has to be re-read.

A third claim in the B.3.v2 card brief is corrected here: the looming rate of the oncoming
at 70 km/h is **smaller**, not larger, than at 50 km/h at matched PET. At matched
time-to-arrival, D = v * TTA, so theta_dot = W v / D^2 = W / (v TTA^2): faster oncoming,
more distant at the same TTA, expands more slowly. Looming and distance therefore agree in
direction on this design (both call the 70 km/h cells milder, which is also the direction
the responses go); they are separated by their *shape*, not by their sign, which is what
`replication/czb/ltap_two_axis.py` fits.

Run: python tests/test_ltap.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from comfortzone.ltap import (BAND_HALF_M, DESIGN_PET_S, NOMINAL_ONC_SPEED_MPS,  # noqa: E402
                              RANDOM_LTAP_TRACES, T_DECISION_S, geometry_crosscheck,
                              load_ltap_trace, ltap_cells, looming_rate)

PASS, FAIL = [], []
_CELLS = None


def check(name, cond, detail=""):
    (PASS if bool(cond) else FAIL).append(name)
    print("{}  {}{}".format("PASS" if cond else "FAIL", name, ("  -- " + str(detail)) if detail else ""))


def cells():
    """The 18-cell table, loaded once."""
    global _CELLS
    if _CELLS is None:
        _CELLS = ltap_cells()
    return _CELLS


def by_pet(c, pet):
    a = c[(c.pet == pet) & (c.speed_kph == 50)].iloc[0]
    b = c[(c.pet == pet) & (c.speed_kph == 70)].iloc[0]
    return a, b


def test_stimuli_present():
    missing = [str(p) for p in RANDOM_LTAP_TRACES.values() if not p.exists()]
    check("all 18 LTAP stimulus files present", not missing, missing[:3])


def test_roles_by_yaw_span():
    """Roles on all 18 traces: the ego turns (yaw span > 200 deg), the oncoming holds
    heading (< 5 deg). The two other role rules in the project are also exercised here,
    because both would get this scenario wrong -- the lateral-span rule (cut-in) inverts
    the assignment and the width rule (overtake) is uninformative."""
    c = cells()
    check("18 traces loaded", len(c) == 18, len(c))
    check("ego yaw span > 200 deg on every trace", bool((c.yaw_span_ego_deg > 200).all()),
          f"min {c.yaw_span_ego_deg.min():.1f} deg")
    check("oncoming yaw span < 5 deg on every trace", bool((c.yaw_span_onc_deg < 5).all()),
          f"max {c.yaw_span_onc_deg.max():.3f} deg")
    check("the two roles are never the same vehicle",
          bool((c.yaw_span_ego_deg > c.yaw_span_onc_deg).all()))

    # the rules that would be wrong here, measured rather than asserted
    inverted, uninformative = 0, 0
    for (pet, spd), path in sorted(RANDOM_LTAP_TRACES.items()):
        raw = pd.read_csv(path)
        tr = load_ltap_trace(path)
        lat = raw.groupby("Vehicle_ID").Location_Y.agg(lambda s: s.max() - s.min())
        wid = raw.groupby("Vehicle_ID").Width_m.first()
        inverted += int(int(lat.idxmax()) == tr.ego_id)      # cut-in would call the ego "target"
        uninformative += int(int(wid.idxmax()) == tr.onc_id)  # overtake would call the oncoming "ego"
    check("the cut-in lateral-span rule would invert the roles on all 18 traces",
          inverted == 18, f"{inverted}/18")
    check("the overtake width rule would pick the oncoming as ego on all 18 traces",
          uninformative == 18, f"{uninformative}/18")


def test_turn_onset_is_common():
    """The ego's script is identical in all 18 traces, so turn onset must be too.

    The note claims 0.2 s; the measured span is 0.201 s, which is two samples of the
    ~0.1004 s grid plus its drift. The tolerance is therefore 0.2 s + half a sample.
    """
    c = cells()
    dt = float(np.median(pd.Series([load_ltap_trace(RANDOM_LTAP_TRACES[(0.0, 50)]).dt])))
    span = float(c.t_onset.max() - c.t_onset.min())
    check("turn onset within 0.2 s across traces (2 samples of the 0.1 s grid)",
          span <= 0.2 + 0.5 * dt,
          f"span {span:.3f} s = {span / dt:.2f} samples, {c.t_onset.min():.3f}-{c.t_onset.max():.3f} s")
    check("the note's literal 0.2 s span is exceeded, by one grid drift only",
          0.2 < span < 0.2 + dt, f"{span:.4f} s")
    check("the ego's approach speed is the same in every trace",
          float(c.v_ego_approach.max() - c.v_ego_approach.min()) < 0.1,
          f"{c.v_ego_approach.min():.2f}-{c.v_ego_approach.max():.2f} m/s")


def test_decision_moment_precedes_the_turn():
    """Assumption B3.Q1: the clip ends at 13.5 s, 0.4-0.6 s before the turn begins."""
    c = cells()
    lead = c.t_onset - c.t_dec
    check("the decision moment precedes turn onset in every trace", bool((lead > 0).all()),
          f"lead {lead.min():.2f}-{lead.max():.2f} s")
    # the note rounds the lead to "0.4-0.6 s"; measured 0.3999-0.601 s, so the bounds are 0.35-0.65
    check("the lead is the note's 0.4-0.6 s (bound 0.65)", 0.35 <= lead.min() and lead.max() <= 0.65,
          f"{lead.min():.3f}-{lead.max():.3f} s")
    check("the covariate sample is the first at or after t = 13.5 s",
          bool(((c.t_dec >= T_DECISION_S) & (c.t_dec < T_DECISION_S + 0.11)).all()),
          f"{c.t_dec.min():.3f}-{c.t_dec.max():.3f} s")


def test_tsep_monotone_in_design_pet():
    """Measured arrival-time separation is monotone in design PET at each speed."""
    c = cells()
    for spd in (50, 70):
        g = c[c.speed_kph == spd].sort_values("pet")
        d = np.diff(g.t_sep.to_numpy(float))
        check(f"t_sep is strictly increasing in design PET at {spd} km/h",
              bool(np.all(d > 0)), f"steps {np.round(d, 3).tolist()}")
    off = c.t_sep - c.pet
    check("t_sep is the design PET plus a near-constant offset",
          0.6 < off.min() and off.max() < 1.3 and float(off.std()) < 0.2,
          f"offset {off.min():.2f}-{off.max():.2f} s, mean {off.mean():.2f}, sd {off.std():.2f}")


def test_distance_scales_with_the_speed_ratio():
    """D(70) = D(50) * 19.4/13.9 within 5% at each PET -- with one documented exception.

    The design gives the two speeds the same time-to-arrival at each PET, so their
    distances must differ by the speed ratio. PET 1.0 is the level where the stimulus set
    does not manage it (see the module docstring).
    """
    c = cells()
    target = NOMINAL_ONC_SPEED_MPS[70] / NOMINAL_ONC_SPEED_MPS[50]
    devs = {}
    for pet in DESIGN_PET_S:
        a, b = by_pet(c, pet)
        devs[pet] = (b.d_onc / a.d_onc) / target - 1.0
        if pet == 1.0:
            continue
        check(f"D(70)/D(50) is within 5% of 19.4/13.9 at PET {pet:g}",
              abs(devs[pet]) < 0.05, f"{100 * devs[pet]:+.2f}%")
    check("PET 1.0 is the design's one off-ratio level (documented exception, +6.3%)",
          0.05 < devs[1.0] < 0.07, f"{100 * devs[1.0]:+.2f}%")
    worst = max(abs(v) for k, v in devs.items() if k != 1.0)
    check("every other level is within 4%", worst < 0.04, f"worst {100 * worst:+.2f}%")


def test_tta_matched_across_speeds():
    """The design's whole value: time matched across speeds while distance is not."""
    c = cells()
    diffs = {}
    for pet in DESIGN_PET_S:
        a, b = by_pet(c, pet)
        diffs[pet] = b.tta - a.tta
        check(f"TTA is matched across speeds within 0.25 s at PET {pet:g}",
              abs(diffs[pet]) < 0.25, f"{diffs[pet]:+.3f} s")
    check("the worst TTA mismatch is PET 1.0, the off-ratio level",
          max(diffs, key=lambda k: abs(diffs[k])) == 1.0,
          f"{diffs[1.0]:+.3f} s against {max(abs(v) for k, v in diffs.items() if k != 1.0):.3f} s elsewhere")
    # and distance is NOT matched: that is the separation the scenario is for
    rat = [by_pet(c, p)[1].d_onc / by_pet(c, p)[0].d_onc for p in DESIGN_PET_S]
    check("distance is separated from time by roughly the speed ratio",
          min(rat) > 1.3 and max(rat) < 1.5, f"ratios {min(rat):.2f}-{max(rat):.2f}")


def test_looming_direction_at_matched_pet():
    """The card's brief has this backwards, and the algebra settles it.

    At matched time-to-arrival D = v * TTA, so theta_dot = W v / (D^2 + W^2/4) is
    approximately W / (v TTA^2): the faster oncoming, being further away at the same TTA,
    expands MORE SLOWLY. Looming and distance thus make the same directional prediction on
    this design (the 70 km/h cells are milder on both), which is also the direction the
    responses go; the fourth model earns or loses its place on shape, not on sign.
    """
    c = cells()
    smaller = 0
    for pet in DESIGN_PET_S:
        a, b = by_pet(c, pet)
        smaller += int(b.theta_dot < a.theta_dot)
        pred = (a.v_onc / b.v_onc) * (a.tta / b.tta) ** 2
        check(f"looming ratio 70/50 matches W/(v TTA^2) at PET {pet:g}",
              abs((b.theta_dot / a.theta_dot) / pred - 1.0) < 0.01,
              f"measured {b.theta_dot / a.theta_dot:.4f}, predicted {pred:.4f}")
    check("theta_dot at 70 km/h is SMALLER than at 50 km/h at every matched PET "
          "(the card brief says larger; it is not)", smaller == 9, f"{smaller}/9")
    check("the ego-referenced looming rate agrees in direction",
          bool(all(by_pet(c, p)[1].theta_dot_ego < by_pet(c, p)[0].theta_dot_ego
                   for p in DESIGN_PET_S)))
    # the formula itself, against a hand-computed value
    check("looming_rate is the exact derivative of 2 atan(W/2D)",
          abs(looming_rate(2.0, 10.0, 50.0) - 2.0 * 10.0 / (2500.0 + 1.0)) < 1e-15)


def test_geometry_crosscheck():
    """The loader must reproduce `ltap_geometry.py`'s per-trace numbers exactly."""
    d = geometry_crosscheck(cells())
    worst = float(d["max abs difference"].max())
    check("every geometry quantity reproduces ltap_geometry.csv to 1e-9",
          worst < 1e-9, f"max |difference| {worst:.2e} over {len(d)} quantities")
    for _, r in d.iterrows():
        if r["max abs difference"] > 1e-9:
            check(f"  {r['quantity']} reproduces", False, r["max abs difference"])


def test_responses_join():
    """The 18 design cells each carry a Random-design response, 172 trials each."""
    c = cells()
    check("every cell has a response", not c.p.isna().any())
    check("172 trials in every cell", bool((c.n == 172).all()), sorted(c.n.unique()))
    check("P(intervene) spans the range the note quotes",
          abs(c.p.max() - 0.907) < 0.002 and abs(c.p.min() - 0.110) < 0.002,
          f"{c.p.min():.3f}-{c.p.max():.3f}")
    for spd in (50, 70):
        g = c[c.speed_kph == spd].sort_values("pet")
        check(f"P(intervene) falls with design PET at {spd} km/h (Spearman < -0.9)",
              float(pd.Series(g.p.to_numpy()).corr(pd.Series(g.pet.to_numpy()),
                                                   method="spearman")) < -0.9)
    lower = [by_pet(c, p)[1].p < by_pet(c, p)[0].p for p in DESIGN_PET_S]
    check("intervention is lower at 70 km/h at every PET level", all(lower),
          f"{sum(lower)}/9")


def test_conflict_geometry():
    """The band, the conflict point and the arrival are consistent with the note."""
    c = cells()
    check("the ego is inside the band for about half a second",
          bool(((c.t_out - c.t_in) > 0.4).all() and ((c.t_out - c.t_in) < 1.0).all()),
          f"{(c.t_out - c.t_in).min():.2f}-{(c.t_out - c.t_in).max():.2f} s")
    check("the oncoming arrives after the ego has cleared the band",
          bool((c.t_onc_arrival > c.t_out).all()))
    check("the conflict point is the same place in every trace (band +-1 m)",
          float(c.x_conf.max() - c.x_conf.min()) < 2 * BAND_HALF_M,
          f"x_conf {c.x_conf.min():.2f}-{c.x_conf.max():.2f} m")
    check("D exceeds the distance at turn onset (the clip ends earlier)",
          bool((c.d_onc > c.dist_at_onset).all()),
          f"by {(c.d_onc - c.dist_at_onset).min():.1f}-{(c.d_onc - c.dist_at_onset).max():.1f} m")
    check("the ego has not reached the conflict point at the decision moment",
          bool((c.range_ego_onc > c.d_onc).all()),
          f"range {c.range_ego_onc.min():.1f}-{c.range_ego_onc.max():.1f} m "
          f"vs D {c.d_onc.min():.1f}-{c.d_onc.max():.1f} m")
    check("the oncoming holds a constant speed within each speed level",
          float(c[c.speed_kph == 50].v_onc.std()) < 0.01
          and float(c[c.speed_kph == 70].v_onc.std()) < 0.01,
          f"{c[c.speed_kph == 50].v_onc.mean():.3f} / {c[c.speed_kph == 70].v_onc.mean():.3f} m/s")


if __name__ == "__main__":
    for fn in [test_stimuli_present, test_roles_by_yaw_span, test_turn_onset_is_common,
               test_decision_moment_precedes_the_turn, test_tsep_monotone_in_design_pet,
               test_distance_scales_with_the_speed_ratio, test_tta_matched_across_speeds,
               test_looming_direction_at_matched_pet, test_geometry_crosscheck,
               test_responses_join, test_conflict_geometry]:
        fn()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(1 if FAIL else 0)
