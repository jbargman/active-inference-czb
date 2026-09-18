"""
Card GM.1a -- sigma_a measured: how uncertain is a lead vehicle's future speed, and does it grow
the way the rollout fan says?

PRE-STATED before any run (2026-09-18, authorized by Jonas as "card 1" of the two he asked for
while the naturalistic data are not available).

THE QUESTION, AND WHY THIS CONSTANT AND NOT ANOTHER
---------------------------------------------------
The rollout fan (`docs/rollout_boundary_design_note.md` section 1.2) predicts the other road user's
longitudinal position as

    x(tau) ~ N(x0 + v0 tau,  sigma_x^2 + (0.5 sigma_a tau^2)^2),

with **sigma_a = 0.5 m/s^2 marked UNVERIFIED** in the note itself and flagged as query JJ1.Q2, to be
replaced by component C3 of the generative-model framework when naturalistic data arrive. Three
results since make it the constant worth measuring first:

  * Card RE.1 (part B1, part D): on a CERTAIN constant-speed prediction the released model's
    criticality signal is flat -- 23 nats at every time gap from 0.5 s to 3.5 s at 110 km/h, and
    the same on an empty road. The whole gradient the deposit shows in benign following (98 800 at
    a 0.5 s gap falling to 6 200 at 3.5 s, `docs/method_review.md` section 4.2) is produced by the
    share of predicted futures that COLLIDE, and that share is set by the assumed spread of the
    lead's acceleration, not by the scene. **This constant is the gradient.**
  * Card RE.1 (part A): our mirror does not reproduce the deposit's benign eps, and the reason is
    the same quantity -- ours RISES with the gap because the looming likelihood stops constraining
    the lead's acceleration at distance and the particle spread fills its clip range [-4, +8] m/s^2,
    so the collide fraction goes from 0.000 at 9 m to 0.79 at 34 m.
  * `docs/waymo_program_revisit.md` section 0: the comfort-zone regime is the program's strand 1,
    whose subject is the progress-versus-caution trade-off. There the uncertainty about what the
    other will do is not a nuisance constant at all; it is the thing being traded against.

THE DATA, AND ITS ONE LIMITATION, STATED FIRST
-----------------------------------------------
`external/quadris/Synthetic_crash_scenarios.csv` -- the QUADRIS pre-crash/near-crash database,
5 000 scenarios, about 5 s each at 20 Hz, with the follower speed `v_f`, the lead speed `v_l`, the
separation `d` and an exposure `weight` per scenario.

**QUADRIS is a conflict distribution, not a sample of ordinary driving.** Every scenario is the
run-up to a crash or near-crash, so even its quiet phase is the approach to an incident and its
lead vehicles brake more than leads in general do. Therefore **every number this card produces is an
UPPER BOUND on the corresponding quantity in ordinary driving**, and the report says so in its own
words. A bound is still a result: if even the upper bound is far below the value the released model
assumes, the released assumption is too wide, and that conclusion does not need ordinary-driving
data to be safe. The reverse -- an upper bound above the assumed value -- would say nothing.

WHAT IS MEASURED
----------------
The lead vehicle's own motion only. Its position is the integral of `v_l` (the constant of
integration cancels in every quantity below), so nothing here depends on the follower or on `d`.

  **(1) The constant-velocity prediction error against the horizon**, by
  `generative.uncertainty.cv_prediction_errors` -- the framework's own function, unchanged, with
  its backward-difference velocity over `WINDOW_S`. This is exactly what the fan claims to model.
  **(2) Both growth forms fitted to it** and compared by their residuals:
      linear      sd(h)^2 = s0^2 + (s1 h)^2            a constant VELOCITY perturbation
      quadratic   sd(h)^2 = s0^2 + (0.5 sigma_a h^2)^2 a constant ACCELERATION perturbation, the fan
  `fit_growth` and `fit_growth_accel` in `src/generative/uncertainty.py`; the second was added for
  this card with five property tests. **Comparing them is a test of the fan's FORM**, not only of
  its constant: if the lead's motion is better described by the linear form, the fan's
  constant-acceleration perturbation is the wrong model however its constant is chosen.
  **(3) The acceleration distribution directly** -- the sd of the lead's own acceleration over the
  same windows, a model-free number to put beside the fitted one.

BY PHASE, because the two regimes are different and only one of them is the comfort zone:
  **benign** -- before the lead's braking onset, the first time its acceleration falls below
  A_EVENT = -0.5 m/s^2. Motivated, not tuned: the released model's own no-pedal coast is
  -0.1 m/s^2 (`AgentParams.a_coast`), so -0.5 is clear of coasting and of numerical noise while
  still well inside anything a driver would call braking. Reported for A_EVENT in
  {-0.3, -0.5, -1.0} as a sensitivity.
  **event** -- from that onset onward.
Scenarios whose lead never brakes contribute only a benign phase; scenarios that start already
braking contribute only an event phase, and both counts are reported.

Weighted and unweighted numbers are both given: QUADRIS carries an exposure `weight` per scenario,
and a weighted sd is the estimate for driving while the unweighted one is the estimate for this
scenario set. The primary is the WEIGHTED benign sigma_a.

THE READINGS, PRE-STATED
------------------------
  (a) **The constant.** The fan's 0.5 m/s^2 against the measured benign sigma_a. If the measured
      upper bound is below 0.5, the fan is too wide and every rollout card has been carrying more
      predicted-collision mass than the data support. If it is above 0.5, this card says only that
      the conflict distribution is wider, which was expected and decides nothing.
  (b) **The form.** Whichever of the two fits has the lower RMS residual on the horizon grid, with
      both reported. A linear win would mean the fan's longitudinal perturbation should be a
      velocity, not an acceleration -- a change to the design note, not to a constant.
  (c) **The released belief, for scale.** `AgentParams.sigma_a_belief` = 3.0 m/s^2 of process noise
      per step with the particle acceleration clipped to [-4, +8], and `sigma_a_init` = 0.5 at
      reset. Reported beside the measurement without a decision attached, because those are the
      authors' constants and this card does not re-decide them.

No response data enter this card and nothing is fitted to any human judgment.

Output: replication/czb/out/gm1a_lead_acceleration.md and out/gm1a_lead_acceleration.csv.
Run:    python replication/czb/gm1a_lead_acceleration.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

from aidriver.agent import AgentParams                                   # noqa: E402
from aidriver.bicycle import BicycleParams                               # noqa: E402
from generative.uncertainty import (cv_prediction_errors, fit_growth,     # noqa: E402
                                    fit_growth_accel, growth_residual, growth_table,
                                    pool_errors)
from rollout.predictor import SD_A                                       # noqa: E402

OUT = HERE / "out"
QUADRIS = REPO / "external" / "quadris" / "Synthetic_crash_scenarios.csv"

WINDOW_S = 0.3            # the framework's own velocity window (card G.1's)
HORIZONS = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)   # the scenarios are ~5 s, so 3 s is the longest usable
A_EVENT = -0.5            # m/s^2, braking onset; see the docstring
A_EVENT_SWEEP = (-0.3, -0.5, -1.0)
MIN_SAMPLES = 20          # a phase shorter than this contributes nothing


def load_scenarios() -> pd.DataFrame:
    d = pd.read_csv(QUADRIS)
    need = {"id", "t", "v_l", "weight"}
    missing = need - set(d.columns)
    if missing:
        raise RuntimeError(f"{QUADRIS.name}: missing columns {sorted(missing)}")
    return d.sort_values(["id", "t"]).reset_index(drop=True)


def phase_split(t: np.ndarray, v: np.ndarray, a_event: float) -> int:
    """Index of the lead's braking onset, or len(t) if it never brakes."""
    if len(t) < 3:
        return len(t)
    a = np.gradient(v, t)
    hit = np.flatnonzero(a < a_event)
    return int(hit[0]) if len(hit) else len(t)


def per_scenario(d: pd.DataFrame, a_event: float):
    """Prediction errors and accelerations per scenario and phase, with the scenario's weight."""
    out = {"benign": [], "event": []}
    accel = {"benign": [], "event": []}
    weights = {"benign": [], "event": []}
    counts = {"benign": 0, "event": 0, "no_event": 0, "starts_braking": 0}
    for sid, g in d.groupby("id", sort=False):
        t = g.t.to_numpy(float)
        v = g.v_l.to_numpy(float)
        w = float(g.weight.iloc[0])
        x = np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])
        k = phase_split(t, v, a_event)
        if k >= len(t):
            counts["no_event"] += 1
        if k == 0:
            counts["starts_braking"] += 1
        a = np.gradient(v, t) if len(t) > 2 else np.array([])
        for phase, sl in (("benign", slice(0, k)), ("event", slice(k, len(t)))):
            tt, xx = t[sl], x[sl]
            if len(tt) < MIN_SAMPLES:
                continue
            counts[phase] += 1
            out[phase].append(cv_prediction_errors(tt, xx, np.zeros_like(xx), HORIZONS,
                                                   window_s=WINDOW_S))
            if len(a):
                accel[phase].append(a[sl])
            weights[phase].append(w)
    return out, accel, weights, counts


def weighted_sd(values: list[np.ndarray], weights: list[float]) -> tuple[float, float, int]:
    """Unweighted sd, weight-weighted sd (each scenario's samples carry its weight), and n."""
    if not values:
        return float("nan"), float("nan"), 0
    flat = np.concatenate(values)
    n = int(len(flat))
    if n < 2:
        return float("nan"), float("nan"), n
    unw = float(np.std(flat))
    wv = np.concatenate([np.full(len(v), w) for v, w in zip(values, weights)])
    mu = float(np.average(flat, weights=wv))
    wsd = float(np.sqrt(np.average((flat - mu) ** 2, weights=wv)))
    return unw, wsd, n


def growth_for(per_track: list[dict], weights: list[float]) -> pd.DataFrame:
    """The growth table, plus a weight-weighted sd column alongside the unweighted one."""
    g = growth_table(pool_errors(per_track), n_tracks=len(per_track))
    wsd = []
    for h in g.horizon_s:
        vals = [p[float(h)][0] for p in per_track if float(h) in p and len(p[float(h)][0])]
        ws = [w for p, w in zip(per_track, weights) if float(h) in p and len(p[float(h)][0])]
        wsd.append(weighted_sd(vals, ws)[1])
    g = g.copy()
    g["sd_lon_weighted_m"] = wsd
    return g


def main() -> None:
    t0 = time.time()
    if not QUADRIS.exists():
        raise SystemExit(f"{QUADRIS} not found; re-download per src/quadris/load.py")
    d = load_scenarios()
    ap, veh = AgentParams(), BicycleParams()

    L = ["# Card GM.1a -- sigma_a measured: the lead vehicle's acceleration uncertainty", "",
         "Generated by `replication/czb/gm1a_lead_acceleration.py`; the question, the data, its"
         " limitation, what is measured and the three readings were pre-stated in its docstring"
         " before the run. Do not edit by hand.", "",
         "**QUADRIS is a conflict distribution, not a sample of ordinary driving.** Every scenario"
         " is the run-up to a crash or near-crash, so its lead vehicles brake more than leads in"
         " general do. **Every number below is an upper bound on the corresponding quantity in"
         " ordinary driving.** A bound is still a result: if even the upper bound is far below the"
         " value the released model assumes, the assumption is too wide, and that conclusion does"
         " not need ordinary-driving data. The reverse would say nothing.", "",
         f"Source: `external/quadris/Synthetic_crash_scenarios.csv`, {d.id.nunique()} scenarios,"
         f" {len(d)} samples, {float(np.median(np.diff(d.t.to_numpy()[:3]))):.2f} s spacing."
         f" Velocity window {WINDOW_S} s (card G.1's); horizons"
         f" {', '.join(f'{h:g}' for h in HORIZONS)} s.", ""]

    rows_csv = []
    primary = {}
    for a_event in A_EVENT_SWEEP:
        per, accel, weights, counts = per_scenario(d, a_event)
        is_primary = a_event == A_EVENT
        if is_primary:
            L += ["## 1 Phases", "",
                  f"Braking onset at the primary threshold {A_EVENT} m/s^2.", "",
                  "| phase | scenarios contributing | note |", "|---|---|---|",
                  f"| benign (before onset) | {counts['benign']} | of"
                  f" {d.id.nunique()} scenarios; {counts['no_event']} never brake at all |",
                  f"| event (from onset) | {counts['event']} |"
                  f" {counts['starts_braking']} scenarios are already braking at t = 0 |", ""]
        for phase in ("benign", "event"):
            if not per[phase]:
                continue
            g = growth_for(per[phase], weights[phase])
            s0_l, s1_l = fit_growth(g.horizon_s, g.sd_lon_weighted_m)
            s0_q, sig_a = fit_growth_accel(g.horizon_s, g.sd_lon_weighted_m)
            r_lin = growth_residual(g.horizon_s, g.sd_lon_weighted_m, s0_l, s1_l, quadratic=False)
            r_qua = growth_residual(g.horizon_s, g.sd_lon_weighted_m, s0_q, sig_a, quadratic=True)
            a_unw, a_wsd, a_n = weighted_sd(accel[phase], weights[phase])
            rec = {"a_event": a_event, "phase": phase, "s0_linear_m": s0_l, "s1_mps": s1_l,
                   "s0_quad_m": s0_q, "sigma_a_mps2": sig_a, "rms_resid_linear_m": r_lin,
                   "rms_resid_quad_m": r_qua, "sd_accel_direct_mps2": a_wsd,
                   "sd_accel_direct_unweighted_mps2": a_unw, "n_accel": a_n,
                   "n_scenarios": len(per[phase])}
            rows_csv.append(rec)
            if is_primary:
                primary[phase] = (rec, g)

    # --- the primary tables ---------------------------------------------------------
    for phase in ("benign", "event"):
        if phase not in primary:
            continue
        rec, g = primary[phase]
        L += [f"## 2{'a' if phase == 'benign' else 'b'} Growth of the constant-velocity prediction"
              f" error -- {phase} phase", "",
              "| horizon [s] | n | sd [m] | weighted sd [m] | 90th pct \\|error\\| [m] |",
              "|---|---|---|---|---|"]
        for _, r in g.iterrows():
            L.append(f"| {r.horizon_s:g} | {int(r.n)} | {r.sd_lon_m:.3f} |"
                     f" {r.sd_lon_weighted_m:.3f} | {r.q90_abs_lon_m:.3f} |")
        L += ["", "| growth form | s0 [m] | slope | RMS residual [m] |", "|---|---|---|---|",
              f"| linear, a constant VELOCITY perturbation | {rec['s0_linear_m']:.3f} |"
              f" s1 = {rec['s1_mps']:.3f} m/s | {rec['rms_resid_linear_m']:.4f} |",
              f"| quadratic, a constant ACCELERATION perturbation (**the fan**) |"
              f" {rec['s0_quad_m']:.3f} | **sigma_a = {rec['sigma_a_mps2']:.3f} m/s^2** |"
              f" {rec['rms_resid_quad_m']:.4f} |",
              f"| the lead's acceleration sd, measured directly | - |"
              f" {rec['sd_accel_direct_mps2']:.3f} m/s^2 (unweighted"
              f" {rec['sd_accel_direct_unweighted_mps2']:.3f}) | - |", ""]

    # --- the readings ---------------------------------------------------------------
    b = primary.get("benign", ({}, None))[0]
    sig_b = b.get("sigma_a_mps2", float("nan"))
    below = np.isfinite(sig_b) and sig_b < SD_A
    lin_wins = (np.isfinite(b.get("rms_resid_linear_m", np.nan))
                and b["rms_resid_linear_m"] < b["rms_resid_quad_m"])
    L += ["## 3 The readings, as pre-stated", "",
          f"**(a) The constant.** The fan's placeholder is {SD_A} m/s^2 (query JJ1.Q2). The measured"
          f" benign upper bound is **{sig_b:.3f} m/s^2**. "
          + (f"That is BELOW the placeholder, so the fan has been carrying more predicted-collision"
             f" mass than even a conflict-selected dataset supports, and the released belief's"
             f" assumptions are wider still." if below else
             "That is above the placeholder, which is what a conflict-selected dataset was expected"
             " to give and decides nothing on its own."), "",
          f"**(b) The form.** RMS residual {b.get('rms_resid_linear_m', float('nan')):.4f} m for the"
          f" linear form against {b.get('rms_resid_quad_m', float('nan')):.4f} m for the quadratic"
          f" one, so the **{'linear (velocity)' if lin_wins else 'quadratic (acceleration)'} form"
          f" describes the lead's motion better**. "
          + ("The fan's longitudinal perturbation should then be a velocity rather than an"
             " acceleration, which is a change to design note section 1.2 and not to a constant."
             if lin_wins else
             "That is the form the fan already uses."), "",
          f"**(c) The released belief, for scale, with no decision attached.**"
          f" `sigma_a_belief` = {ap.sigma_a_belief} m/s^2 of process noise per step, the particle"
          f" acceleration clipped to [{ap.a_other_min_assumed:g}, {veh.a_max:g}] m/s^2, and"
          f" `sigma_a_init` = {ap.sigma_a_init} m/s^2 at reset. Those are the authors' constants"
          " and this card does not re-decide them.", "",
          "## 4 Sensitivity to the braking-onset threshold", "",
          "| onset threshold [m/s^2] | phase | scenarios | sigma_a [m/s^2] | s1 [m/s] |"
          " direct accel sd [m/s^2] |", "|---|---|---|---|---|---|"]
    for rec in rows_csv:
        L.append(f"| {rec['a_event']:g}{' **(primary)**' if rec['a_event'] == A_EVENT else ''} |"
                 f" {rec['phase']} | {rec['n_scenarios']} | {rec['sigma_a_mps2']:.3f} |"
                 f" {rec['s1_mps']:.3f} | {rec['sd_accel_direct_mps2']:.3f} |")
    L += ["", f"Run time {time.time() - t0:.0f} s.", ""]

    pd.DataFrame(rows_csv).to_csv(OUT / "gm1a_lead_acceleration.csv", index=False)
    (OUT / "gm1a_lead_acceleration.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-22:]))


if __name__ == "__main__":
    main()
