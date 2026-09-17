"""
Card JJ.3 -- transfer in nats: the same rollout construction on the first study's left turn
and cyclist overtake, and the per-driver level on one scale.

THE PRE-REGISTRATION. Everything in this docstring was written before the run.

The construction is card JJ.1's (`src/rollout/`, 27 property tests), unchanged from card JJ.2
except for what each scenario's own instructions fix: the policy menu, the freeze, and whether
the collision test is the released box on dx, dy or the polygon overlap. Nothing is refitted.

CONTEXT, recorded before the rules so that no number here is read as a live candidate: card
JJ.2 (`out/jj2_rollout_cutin.md`, 2026-09-18) DROPPED Delta G on the second cut-in study -- rule
(a) failed at 0.3202 against 0.1127, which is chance, because log Delta G is anti-ordered with
the response. This card runs anyway, because it was authorized as written and because the two
scenarios test a different claim (transfer of one unit), and its numbers are to be read as what
the same construction does elsewhere.

THE PRE-STATED RULES, copied verbatim from design note section 3
-----------------------------------------------------------------
  Left turn (18 cells, `out/ltap_two_axis.md`; distance alone 0.0558 held out,
  leave-one-PET-out). The perceived arrival of the oncoming car carries the released looming
  model's distance-dependent noise (handbook chapter 3: constant noise in the angular channel,
  `decoder.py`), so that the arrival at 70 km/h from farther away is less certain than at
  50 km/h.

  (a) Delta G's threshold model within 0.01 of distance alone (0.0558), same folds.
  (b) Direction of the speed effect. In the *predicted* shares, the 70 km/h cell is below the
      50 km/h cell at every matched PET, as the data are (`docs/lateral_and_uncertainty_note.md`
      section 1). This is the uncertainty mechanism's own prediction, and it is reported whether
      or not (a) holds.
  (c) No horizon parameter. The horizon is the released 6 s; if the "proceed" rollout's conflict
      at a PET of 4 s (oncoming car arriving 4 s after the ego clears) does not register within
      it, the report says the emergence claim fails on the left turn at that PET rather than
      extending the horizon.

  Cyclist overtake (15 cells, `out/transfer_overtake_summary.md`).

  (d) Intervention graded in clearance in the predicted shares across the three clearance
      levels, which the field could not produce (`out/overtake_field_check.md`), with the
      held-out score reported against the lateral-clearance rule of card B.1.

  The trait on one scale. Per-driver levels on log Delta G fitted on the cut-in and on the left
  turn for the 43 drivers seen in both (card TR.1's set, `out/driver_levels.md`): Spearman
  correlation with its bootstrap interval, against TR.1's +0.647 in mixed units and against the
  reliability ceiling. Pre-stated reading: a correlation within the interval of TR.1's is "the
  same trait on one scale, no rescaling"; a correlation clearly above it would be the first
  evidence that the common unit adds information; below it, that Delta G loses per-driver signal
  that the scenario-specific axes keep. EL.Q4 is answered by this card only if the first or
  second reading obtains.

SETTINGS, each with its motivation
-----------------------------------
  predictor            P0 at the design note's first values: sigma_v,lat 0.33 m/s, sigma_a
                       0.5 m/s^2 (unverified, query JJ1.Q2), H 6 s, dt 0.2 s, 200 futures, seed 0
  jitter floors        card HS.1's first-study measurements, 1.0 s velocity window, read out of
                       its docstring by `rollout.belief.verify_floors`
  intention            none on the left turn and the overtake (design note section 1.1: the
                       oncoming car and the cyclist do what they are seen to do), so p_change = 0
  freeze, left turn    the decision moment T_DECISION_S = 13.5 s (assumption B3.Q1)
  freeze, overtake     the clip end of each timepoint, by the project's own convention
                       `czb_data._cov_end`: onset + 0.3 (k - 1) s, and onset - 0.15 s at C1 so
                       that a pre-onset cell cannot depend on manoeuvre frames (query JJ3.Q3)
  menus                left turn: proceed (the recorded turn, card PC.1's reading P) and wait
                       (a stop CLEAR of the conflict band the ego enters at t_in -- its front
                       bumper at the band's near edge -- at -3 m/s^2 where that suffices and at
                       the deceleration that just does where it does not, reported per cell and
                       capped at the ego's a_max. In these stimuli -3 m/s^2 and "before the
                       crossing" are not both satisfiable at the decision moment: about 7.8 m/s
                       with about 7 m of path left needs about 4.2 m/s^2. Keeping -3 would make
                       "wait" a policy that stops on the crossing and is hit there, which is not
                       what the design note's word names. Query JJ3.Q2);
                       overtake: continue (the recorded pass at the shown clearance) and abort
                       (-2 m/s^2 floored at the cyclist's speed, lateral return to the lane
                       centre over 2 s)
  collision test       left turn: the POLYGON overlap of the two oriented rectangles, because the
                       paths cross at an angle and the released box on dx, dy is a straight-road
                       construct (brief section 4.6); overtake: the released box, a straight road
  the lateral term     left turn: the ego's lane offset is held at zero for both policies. The
                       released lane-keeping term is a straight-road construct and would charge
                       "proceed" the road-edge cost (-15 000 per step) simply for turning, which
                       is a statement about the term's calibration and not about the situation.
                       Query JJ3.Q1. Overtake: the real offset from the ego's lane centre, since
                       that is where any grading in clearance has to come from (brief section 8)
  steering             omega = 0 for every policy, as in `cutin_obs` and for the same reason
  preference staging   the desired speed is the ego's own speed at the freeze; the continuous
                       lane-entry forms on, with the CZB shape constant k = 12
  variants             A (released six terms, primary) and B (no p_safe), both reported

Output: replication/czb/out/jj3_rollout_transfer.md, out/jj3_rollout_cells.csv and
        out/jj3_driver_levels.csv.
Run:    python replication/czb/jj3_rollout_transfer.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import cutin2_two_axis as T                # noqa: E402  card EL.1 (read only)
import hs1_situational_surprise as HS      # noqa: E402  card HS.1 scene loaders (read only)
import ltap_two_axis as LT                 # noqa: E402  card B.3.v2 (read only)
import driver_levels as D                  # noqa: E402  card TR.1 (read only)
import ex2_first_exposure_levels as EX     # noqa: E402  card EX.2 (read only)
import fit_stage1_looming as F             # noqa: E402  card G1.Q1 (read only)
from aidriver.preferences import PreferenceParams        # noqa: E402
from comfortzone import czb_data                          # noqa: E402
from comfortzone.conflict import Body, planned_path       # noqa: E402
from comfortzone.cutin import CZB_LANE_ENTRY_SHAPE_K, load_cutin_trace  # noqa: E402
from comfortzone.ltap import (BAND_HALF_M, T_DECISION_S, ltap_cells, ltap_traces,  # noqa: E402
                              trace_name)
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES, load_overtake_trace  # noqa: E402
from rollout.belief import FLOORS_STUDY1, Frame, Scene, belief_at  # noqa: E402
from rollout.boundary import axis, delta_g               # noqa: E402
from rollout.efe import g_by_policy, polygon_overlap, variant_params   # noqa: E402
from rollout.policies import (CUTIN_MENU, ego_rollout, ltap_rollout, ltap_wait_accel,  # noqa: E402
                              overtake_rollout)
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, horizon_steps, sample_futures  # noqa: E402

OUT = HERE / "out"
LTAP_DIST = 0.0558          # out/ltap_two_axis.md, distance alone, leave-one-PET-out
MARGIN = 0.01               # rules 3(a)
PET_C = 4.0                 # rule 3(c)'s PET
TR1_RHO = (0.647, 0.407, 0.798)     # out/driver_levels.md
SEED = 0


# ---------------------------------------------------------------------------------
# scenes
# ---------------------------------------------------------------------------------

def scene_from(grid, tracks, meta, ego_id, oth_id, name) -> Scene:
    def head(vid):
        h = meta[vid].get("heading")
        return np.asarray(h, float) if h is not None else np.zeros_like(grid)
    return Scene(t=grid,
                 ego_x=tracks[ego_id].x, ego_y=tracks[ego_id].y, ego_heading=head(ego_id),
                 ego_speed=meta[ego_id]["speed"],
                 oth_x=tracks[oth_id].x, oth_y=tracks[oth_id].y, oth_heading=head(oth_id),
                 oth_speed=meta[oth_id]["speed"],
                 ego_len=meta[ego_id]["length"], ego_wid=meta[ego_id]["width"],
                 oth_len=meta[oth_id]["length"], oth_wid=meta[oth_id]["width"], name=name)


def body_from(grid, tracks, meta, vid) -> Body:
    m = meta[vid]
    head = m["heading"] if m.get("heading") is not None else np.zeros_like(grid)
    return Body(t=grid, x=tracks[vid].x, y=tracks[vid].y, heading=np.asarray(head, float),
                length=m["length"], width=m["width"])


def cutin_roles(tracks):
    """Study 1's cut-in role rule, the loaders': the target is the vehicle that changes lane;
    the ego is the one of the rest that ends in the target's destination lane."""
    y_span = {v: float(np.ptp(tr.y)) for v, tr in tracks.items()}
    tar = max(y_span, key=y_span.get)
    rest = [v for v in tracks if v != tar]
    y_end = tracks[tar].y[-1]
    ego = min(rest, key=lambda v: abs(tracks[v].y[-1] - y_end))
    return ego, tar


def staging(v_ego: float) -> PreferenceParams:
    return PreferenceParams(v_desired=float(v_ego), lane_entry_continuous=True,
                            counterfactual_residual_severity=True,
                            lane_entry_shape_k=CZB_LANE_ENTRY_SHAPE_K)


def path_in_frame(body: Body, t_at: float, frame: Frame):
    """The recorded future of `body` from t_at, in the freeze frame, with its arc length at
    each rollout step tau. Card PC.1's reading P (`conflict.planned_path`)."""
    pp = planned_path(body, t_at, DT_S, v_window=FLOORS_STUDY1.window_s)
    px, py = frame.to_frame(pp.x, pp.y)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(px), np.diff(py)))])
    tau = horizon_steps(HORIZON_S, DT_S)
    return px, py, s, np.interp(tau, pp.tau, s), pp


# ---------------------------------------------------------------------------------
# the response model (the registered fitter, on log Delta G, no gate)
# ---------------------------------------------------------------------------------

def held_out_1d(cells: pd.DataFrame, x: np.ndarray, folds: np.ndarray, sign: float = +1.0):
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        th = R.fit(x[tr], y[tr], w[tr], sign)
        pred[te] = R.predict(th, x[te], sign)
    return T.wrmse(y, pred, w), pred


def full_predict(cells: pd.DataFrame, x: np.ndarray, sign: float = +1.0):
    th = R.fit(x, cells.p.to_numpy(float), cells.n.to_numpy(float), sign)
    return R.predict(th, x, sign), th


# ---------------------------------------------------------------------------------
# 1. the left turn
# ---------------------------------------------------------------------------------

def left_turn(variants=("A", "B")) -> tuple[list[str], pd.DataFrame]:
    lc = ltap_cells(with_responses=True).sort_values(["speed_kph", "pet"]).reset_index(drop=True)
    traces = {tr.name: tr for tr in ltap_traces()}
    rows = []
    for _, c in lc.iterrows():
        name = trace_name(float(c.pet), int(c.speed_kph))
        tr = traces[name]
        grid, tracks, meta = HS.scene_tracks(HS.KIN1 / f"{name}_vehicle_states.csv")
        ego_id = max(meta, key=lambda v: meta[v]["yaw_span"])
        onc_id = [v for v in tracks if v != ego_id][0]
        sc = scene_from(grid, tracks, meta, ego_id, onc_id, name)
        b = belief_at(sc, T_DECISION_S, FLOORS_STUDY1, p_change_prior=0.0, with_intention=False)
        ego_body = body_from(grid, tracks, meta, ego_id)
        px, py, s_all, s_tau, pp = path_in_frame(ego_body, T_DECISION_S, b.frame)
        tau_in = float(tr.t_in - b.t0)
        s_conf = float(np.interp(max(tau_in, 0.0), pp.tau, s_all)) if tau_in > 0 else 0.0
        # "before the crossing" = clear of the conflict band: the ego's front bumper stops at
        # the band's near edge (BAND_HALF_M from the oncoming car's line), so `wait` is a policy
        # that waits rather than one that stops on the crossing and is hit there.
        s_stop = max(s_conf - 0.5 * b.ego_len - BAND_HALF_M, 0.0)
        a_wait, nominal_ok = ltap_wait_accel(b.v_ego, s_stop)
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=SEED)
        paths = {p: ltap_rollout(b, p, px, py, s_tau, s_stop, a_wait=a_wait)
                 for p in ("proceed", "wait")}
        row = {"cell": f"{int(c.speed_kph)} km/h PET {float(c.pet):.1f}", "trace": name,
               "pet": float(c.pet), "speed_kph": int(c.speed_kph), "p": float(c.p),
               "n": float(c.n), "d_onc": float(c.d_onc), "t_sep": float(c.t_sep),
               "s_conf_m": s_conf, "s_stop_m": s_stop, "a_wait": a_wait,
               "wait_nominal_ok": nominal_ok, "tau_in_s": tau_in, "v_ego": b.v_ego,
               "v_onc": b.v_oth}
        for var in variants:
            g = g_by_policy(b, fut, paths, variant_params(staging(b.v_ego), var),
                            collision_mode="polygon")
            row[f"dg_{var}"] = delta_g(g, continue_name="proceed")
            for k, v in g.items():
                row[f"G_{var}_{k}"] = v
        # rule (c): does the conflict register within the released 6 s horizon?
        hit = polygon_overlap(b, paths["proceed"], fut)
        row["collide_share_proceed"] = float(hit.any(axis=1).mean())
        row["first_collision_tau"] = (float(fut.tau[hit.any(axis=0).argmax()])
                                      if hit.any() else float("nan"))
        rows.append(row)
    df = pd.DataFrame(rows)

    L = ["## 1 The left turn across path (18 cells, first study)", "",
         f"Freeze at the decision moment {T_DECISION_S} s; menu proceed / wait; the polygon"
         " collision test; the ego's lane offset held at zero for both policies (query JJ3.Q1).",
         "", "| cell | share | Delta G, A | Delta G, B | G(proceed), A | G(wait), A | futures"
         " that collide under proceed | first collision tau [s] | arc to a clear stop [m] |"
         " wait deceleration [m/s2] |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        ft = f"{r.first_collision_tau:.1f}" if np.isfinite(r.first_collision_tau) else "never"
        L.append(f"| {r.cell} | {r.p:.3f} | {r.dg_A:.0f} | {r.dg_B:.0f} | {r.G_A_proceed:.0f} | "
                 f"{r.G_A_wait:.0f} | {r.collide_share_proceed:.2f} | {ft} | {r.s_stop_m:.1f} | "
                 f"{r.a_wait:.2f}{'' if r.wait_nominal_ok else ' (raised from -3)'} |")
    L.append("")

    folds = df.pet.to_numpy(float)
    res = {}
    for var in variants:
        ax = axis(df[f"dg_{var}"].to_numpy(float))
        x = ax.values
        r_ho, pred_ho = held_out_1d(df, x, folds)
        pred_full, th = full_predict(df, x)
        df[f"x_{var}"], df[f"pred_{var}"] = x, pred_full
        res[var] = {"axis": ax, "r": r_ho, "pred": pred_full, "theta": th}
    # rule (b): the 70 km/h predicted share below the 50 km/h one at every matched PET
    b_rows, b_ok = [], True
    for pet in sorted(df.pet.unique()):
        s50 = df[(df.pet == pet) & (df.speed_kph == 50)]
        s70 = df[(df.pet == pet) & (df.speed_kph == 70)]
        if len(s50) != 1 or len(s70) != 1:
            continue
        ok = float(s70.pred_A.iloc[0]) < float(s50.pred_A.iloc[0])
        b_ok &= ok
        b_rows.append((pet, float(s50.p.iloc[0]), float(s70.p.iloc[0]),
                       float(s50.pred_A.iloc[0]), float(s70.pred_A.iloc[0]), ok))
    # rule (c)
    pet4 = df[df.pet == PET_C]
    c_ok = bool((pet4.collide_share_proceed > 0).all())

    L += ["### The rules", "",
          "| rule | criterion | variant A | variant B |", "|---|---|---|---|",
          f"| (a) held out, leave-one-PET-out | <= {LTAP_DIST:.4f} + {MARGIN:.2f} = "
          f"{LTAP_DIST + MARGIN:.4f} | {res['A']['r']:.4f} "
          f"{'PASS' if res['A']['r'] <= LTAP_DIST + MARGIN else 'FAIL'} | {res['B']['r']:.4f} "
          f"{'PASS' if res['B']['r'] <= LTAP_DIST + MARGIN else 'FAIL'} |",
          f"| (b) 70 km/h predicted below 50 km/h at every matched PET | all {len(b_rows)} PETs | "
          f"{'PASS' if b_ok else 'FAIL'} ({sum(1 for r in b_rows if r[5])} of {len(b_rows)}) | "
          "reported for A only |",
          f"| (c) the conflict registers within the released {HORIZON_S:.0f} s at PET {PET_C:.0f} s"
          f" | some sampled future collides under proceed | {'PASS' if c_ok else 'FAIL'} | same |",
          "", "Rule (b), per matched PET (variant A):", "",
          "| PET [s] | observed 50 | observed 70 | predicted 50 | predicted 70 | 70 below 50 |",
          "|---|---|---|---|---|---|"]
    for pet, o50, o70, p50, p70, ok in b_rows:
        L.append(f"| {pet:.1f} | {o50:.3f} | {o70:.3f} | {p50:.3f} | {p70:.3f} | "
                 f"{'yes' if ok else 'no'} |")
    if not c_ok:
        L += ["", f"**Rule (c): the emergence claim fails on the left turn at PET {PET_C:.0f} s.**"
              " The horizon was NOT extended; the design note fixes it at the released 6 s and"
              " this report says so instead."]
    L += ["", f"Comparator on file: distance alone, {LTAP_DIST:.4f} held out on the same folds"
          " (`out/ltap_two_axis.md`).", ""]
    return L, df


# ---------------------------------------------------------------------------------
# 2. the cyclist overtake
# ---------------------------------------------------------------------------------

def overtake(variants=("A", "B")) -> tuple[list[str], pd.DataFrame]:
    trials = czb_data.random_overtake_trials()
    cells = (trials.groupby(["criticality", "timepoint"])
             .agg(p=("intervene", "mean"), n=("intervene", "size"), t_end=("t_end", "first"))
             .reset_index())
    rows = []
    for lab, path in RANDOM_OVERTAKE_TRACES.items():
        tr = load_overtake_trace(path)
        t_on = float(tr.t[tr.onset_idx])
        y_lane0 = float(tr.y_ego[0])
        grid, tracks, meta = HS.scene_tracks(path)
        ego_id = max(meta, key=lambda v: meta[v]["width"])
        cyc_id = [v for v in tracks if v != ego_id][0]
        sc = scene_from(grid, tracks, meta, ego_id, cyc_id, lab)
        ego_body = body_from(grid, tracks, meta, ego_id)
        sub = cells[cells.criticality == lab].sort_values("timepoint")
        for _, c in sub.iterrows():
            cov_end = czb_data.C1_COV_END_S if c.timepoint == "C1" else float(c.t_end)
            t0 = t_on + cov_end
            b = belief_at(sc, t0, FLOORS_STUDY1, p_change_prior=0.0, with_intention=False)
            px, py, s_all, s_tau, pp = path_in_frame(ego_body, t0, b.frame)
            # The ego's lateral offset from its own lane centre: its lateral position at the
            # freeze against its position before the pull-out, plus what the recorded path adds
            # over the horizon (the frame's y-axis is the road normal to within the pull-out
            # angle, a few degrees).
            y_off = float(np.interp(t0, sc.t, sc.ego_y) - y_lane0)
            y_lane_rec = y_off + np.interp(s_tau, s_all, py)
            fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES,
                                 sd_vlat=SD_VLAT, sd_a=SD_A, seed=SEED)
            paths = {p: overtake_rollout(b, p, px, py, s_tau, y_lane_rec, y_off, b.v_oth)
                     for p in ("continue", "abort")}
            row = {"cell": f"{lab} {c.timepoint}", "clearance": lab,
                   "timepoint": c.timepoint, "p": float(c.p), "n": float(c.n),
                   "clearance_m": float(lab.replace("m", "")), "y_offset_m": y_off,
                   "v_ego": b.v_ego, "v_cyc": b.v_oth, "y_rel": b.y_rel}
            for var in variants:
                g = g_by_policy(b, fut, paths, variant_params(staging(b.v_ego), var))
                row[f"dg_{var}"] = delta_g(g)
                for k, v in g.items():
                    row[f"G_{var}_{k}"] = v
            rows.append(row)
    df = pd.DataFrame(rows)

    L = ["## 2 The cyclist overtake (15 cells, first study)", "",
         "Freeze at each timepoint's clip end (C1 at onset - 0.15 s, the project's own"
         " convention); menu continue / abort; the released collision test, a straight road; the"
         " ego's real lane offset in the lateral term.", "",
         "| cell | share | ego lane offset [m] | Delta G, A | Delta G, B | G(continue), A |"
         " G(abort), A |", "|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        L.append(f"| {r.cell} | {r.p:.3f} | {r.y_offset_m:+.2f} | {r.dg_A:.0f} | {r.dg_B:.0f} | "
                 f"{r.G_A_continue:.0f} | {r.G_A_abort:.0f} |")
    L.append("")

    # The design note fixes no fold for the overtake. Both schemes are reported, and which is
    # primary is argued rather than scored: leave-one-TIMEPOINT-out keeps all three clearance
    # levels in every training set, so a clearance-based covariate and Delta G are treated
    # alike, while leave-one-clearance-out asks a clearance rule to extrapolate to a level it
    # has never seen and cannot answer by construction. Both were computed after the run and
    # that is said here rather than hidden; no constant is chosen by either. Query JJ3.Q5.
    folds_tp = pd.factorize(df.timepoint)[0].astype(float)     # 5 folds, primary
    folds_cl = df.clearance_m.to_numpy(float)                  # 3 folds, secondary
    res = {}
    for var in variants:
        ax = axis(df[f"dg_{var}"].to_numpy(float))
        r_ho, _ = held_out_1d(df, ax.values, folds_tp)
        r_cl, _ = held_out_1d(df, ax.values, folds_cl)
        pred_full, th = full_predict(df, ax.values)
        df[f"x_{var}"], df[f"pred_{var}"] = ax.values, pred_full
        res[var] = {"r": r_ho, "r_cl": r_cl, "pred": pred_full}
    # the comparator: a threshold on the clearance the manoeuvre ends at (card B.1's rule)
    x_clear = -np.log(df.clearance_m.to_numpy(float))
    r_clear, _ = held_out_1d(df, x_clear, folds_tp)
    r_clear_cl, _ = held_out_1d(df, x_clear, folds_cl)
    chance_ov = T.wrmse(df.p.to_numpy(float),
                        np.full(len(df), float(np.average(df.p, weights=df.n))),
                        df.n.to_numpy(float))

    # rule (d): graded in clearance in the predicted shares, at every timepoint
    grade_rows, d_ok = [], True
    for tp in sorted(df.timepoint.unique()):
        s = df[df.timepoint == tp].sort_values("clearance_m")
        pr = s.pred_A.to_numpy(float)
        ok = bool(np.all(np.diff(pr) < 0))
        d_ok &= ok
        grade_rows.append((tp, pr, s.p.to_numpy(float), ok))
    L += ["### Rule (d) -- is intervention graded in clearance in the predicted shares?", "",
          "| timepoint | observed 0.5 / 1 / 1.5 m | predicted 0.5 / 1 / 1.5 m | strictly"
          " decreasing |", "|---|---|---|---|"]
    for tp, pr, ob, ok in grade_rows:
        L.append(f"| {tp} | " + " / ".join(f"{v:.3f}" for v in ob) + " | "
                 + " / ".join(f"{v:.3f}" for v in pr) + f" | {'yes' if ok else 'no'} |")
    L += ["", f"Rule (d): **{'PASS' if d_ok else 'FAIL'}** "
          f"({sum(1 for r in grade_rows if r[3])} of {len(grade_rows)} timepoints).", "",
          "| model | held out, leave-one-timepoint-out (primary) | held out,"
          " leave-one-clearance-out |", "|---|---|---|",
          f"| Delta G, variant A | {res['A']['r']:.4f} | {res['A']['r_cl']:.4f} |",
          f"| Delta G, variant B | {res['B']['r']:.4f} | {res['B']['r_cl']:.4f} |",
          f"| the clearance the manoeuvre ends at (card B.1's rule) | {r_clear:.4f} |"
          f" {r_clear_cl:.4f} |",
          f"| chance (the weighted grand mean) | {chance_ov:.4f} | {chance_ov:.4f} |", "",
          "The clearance comparator is computed here, not taken from a file: no held-out score"
          " for a clearance threshold on these 15 cells is on file (`out/overtake_field_check.md`"
          " reports rank correlations only). Query JJ3.Q4. The two fold schemes and why"
          " leave-one-timepoint-out is the primary are in the script's comment and in query"
          " JJ3.Q5; both were computed after the run, and neither chose a constant.", ""]
    return L, df


# ---------------------------------------------------------------------------------
# 3. the trait on one scale
# ---------------------------------------------------------------------------------

def study1_cutin_dg(variants=("A",)) -> pd.DataFrame:
    """Delta G per (criticality, timepoint) cell of study 1's Random cut-in."""
    rows = []
    for lab, path in czb_data.RANDOM_CUTIN_TRACES.items():
        tr = load_cutin_trace(path)
        t_on = float(tr.t[tr.onset_idx])
        grid, tracks, meta = HS.scene_tracks(path)
        ego_id, tar_id = cutin_roles(tracks)
        sc = scene_from(grid, tracks, meta, ego_id, tar_id, lab)
        for tp, off in czb_data.TIMEPOINT_OFFSET_S.items():
            cov_end = czb_data.C1_COV_END_S if tp == "C1" else off
            t0 = t_on + cov_end
            if t0 > sc.t[-1]:
                continue
            b = belief_at(sc, t0, FLOORS_STUDY1)
            fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES,
                                 sd_vlat=SD_VLAT, sd_a=SD_A, seed=SEED)
            paths = {k: ego_rollout(b, k) for k in CUTIN_MENU}
            row = {"criticality": lab, "timepoint": tp, "p_change": b.p_change,
                   "x_rel": b.x_rel, "y_rel": b.y_rel, "v_ego": b.v_ego}
            for var in variants:
                g = g_by_policy(b, fut, paths, variant_params(staging(b.v_ego), var))
                row[f"dg_{var}"] = delta_g(g)
            rows.append(row)
    return pd.DataFrame(rows)


def trait(lt: pd.DataFrame) -> tuple[list[str], pd.DataFrame]:
    """Per-driver levels on log Delta G, at first exposure, on the cut-in and the left turn."""
    t0 = time.time()
    cut_cells = study1_cutin_dg()
    r = EX.cutin_trials()
    v = EX.ltap_trials()
    dg_map = {(c.criticality, c.timepoint): c.dg_A for _, c in cut_cells.iterrows()}
    r = r[[(c, t) in dg_map for c, t in zip(r.criticality, r.timepoint)]].reset_index(drop=True)
    r["dg"] = [dg_map[(c, t)] for c, t in zip(r.criticality, r.timepoint)]
    lt50 = lt[lt.speed_kph == 50].set_index("pet")
    v = v[v.pet.isin(lt50.index)].reset_index(drop=True)
    v["dg"] = [float(lt50.loc[p, "dg_A"]) for p in v.pet]

    ax_c = axis(np.unique(r.dg.to_numpy(float)))
    off = ax_c.offset
    xc = np.log(r.dg.to_numpy(float) + off)
    ax_v = axis(np.unique(v.dg.to_numpy(float)))
    xv = np.log(v.dg.to_numpy(float) + ax_v.offset)
    gc, gv = np.ones(len(r)), np.ones(len(v))
    yc, yv = r.intervene.to_numpy(float), v.intervene.to_numpy(float)
    cc, uc = pd.factorize(r.driver)
    cv, uv = pd.factorize(v.driver)
    ec = (r.session.to_numpy(int) - 1).astype(float)
    ev = (v.session.to_numpy(int) - 1).astype(float)

    fc = EX.fit_exposure(xc, gc, yc, ec, cc, F.priors_log_scale(xc))
    print(f"  cut-in exposure fit: mu {fc['mu']:+.4f} [{time.time() - t0:.0f} s]", flush=True)
    fv = EX.fit_exposure(xv, gv, yv, ev, cv, F.priors_log_scale(xv))
    print(f"  left-turn exposure fit: mu {fv['mu']:+.4f} [{time.time() - t0:.0f} s]", flush=True)

    lc = EX.levels_with_offset(xc, gc, yc, ec, cc, fc, +1.0)
    lv = EX.levels_with_offset(xv, gv, yv, ev, cv, fv, +1.0)
    dc = pd.DataFrame({"driver": uc, "level_cutin_log_dg": [lc[k] for k in range(len(uc))]})
    dv = pd.DataFrame({"driver": uv, "level_ltap_log_dg": [lv[k] for k in range(len(uv))]})
    both = dc.merge(dv, on="driver").sort_values("driver").reset_index(drop=True)
    rho = float(spearmanr(both.level_cutin_log_dg, both.level_ltap_log_dg).statistic)
    lo, hi = D.boot_spearman(both.level_cutin_log_dg.to_numpy(), both.level_ltap_log_dg.to_numpy())

    t_rho, t_lo, t_hi = TR1_RHO
    within = t_lo <= rho <= t_hi
    above = rho > t_hi
    reading = ("the same trait on one scale, no rescaling" if within else
               "the common unit adds information" if above else
               "Delta G loses per-driver signal that the scenario-specific axes keep")
    L = ["## 3 The trait on one scale (card TR.1 again, in nats)", "",
         f"Per-driver levels on log Delta G at first exposure (card EX.2's exposure term, the"
         f" session index), fitted on study 1's Random cut-in ({len(r)} trials,"
         f" {r.driver.nunique()} drivers) and on the 50 km/h left turn ({len(v)} trials,"
         f" {v.driver.nunique()} drivers); {len(both)} drivers appear in both.", "",
         "| quantity | value |", "|---|---|",
         f"| Spearman rho, the two levels on one scale | **{rho:+.3f}** [{lo:+.3f}, {hi:+.3f}] |",
         f"| card TR.1, in mixed units | {t_rho:+.3f} [{t_lo:+.3f}, {t_hi:+.3f}] |",
         f"| drivers in both | {len(both)} (TR.1: 43) |",
         f"| cut-in population level (mu) | {fc['mu']:+.4f} nats-log, sigma_pop"
         f" {fc['sigma_pop']:.4f} |",
         f"| left-turn population level (mu) | {fv['mu']:+.4f} nats-log, sigma_pop"
         f" {fv['sigma_pop']:.4f} |",
         f"| distinct axis values, cut-in | {len(np.unique(np.round(xc, 9)))} over"
         f" {r.criticality.nunique() * r.timepoint.nunique()} cells |",
         f"| distinct axis values, left turn | {len(np.unique(np.round(xv, 9)))} over"
         f" {v.pet.nunique()} cells |", "",
         "**A caveat that limits the reading below, and it is stated before the reading rather"
         " than after it.** The left turn's axis is nearly degenerate: Delta G is zero in eight"
         " of the nine 50 km/h cells (section 1), because waiting costs more than proceeding"
         " everywhere but at PET 0, so after the zero rule the axis takes two distinct values"
         " over nine cells. A per-driver level fitted on a two-valued covariate is close to a"
         " per-driver response rate at PET 0, which is not what card TR.1 correlated. The"
         " correlation below is therefore evidence about THIS axis on THIS scenario and not a"
         " measurement of the trait. Query JJ3.Q6.", "",
         f"Pre-stated reading: the correlation is "
         + ("inside" if within else "above" if above else "below")
         + f" TR.1's interval, so this is **{reading}**.", "",
         "EL.Q4 is answered by this card only if the first or second reading obtains: "
         + ("it does, and the answer is that the levels share one scale in nats without a"
            " normalization constant." if (within or above) else
            "it does not, so EL.Q4 stands and the design note's normalization by each"
            " scenario's between-driver spread remains the recommendation."), "",
         "This is read with card JJ.2's DROP in mind: a per-driver level can be consistent"
         " across scenarios on an axis that does not order the cells, because consistency is a"
         " statement about drivers and ordering is a statement about cells.", ""]
    return L, both


# ---------------------------------------------------------------------------------

def main() -> None:
    t_start = time.time()
    L = ["# Card JJ.3 -- transfer in nats: the left turn, the cyclist overtake, and the trait",
         "", "Generated by `replication/czb/jj3_rollout_transfer.py`; construction, settings and"
         " the rules of `docs/rollout_boundary_design_note.md` section 3 pre-stated in its"
         " docstring before the run. Do not edit by hand.", "",
         "**Read with card JJ.2 in hand**: `out/jj2_rollout_cutin.md` DROPPED Delta G on the"
         " second cut-in study (rule (a), 0.3202 against 0.1127, which is chance). The numbers"
         " below are what the same construction does on the other two scenarios, not a live"
         " candidate for the axis.", ""]

    print("left turn...", flush=True)
    L1, lt = left_turn()
    L += L1
    (OUT / "jj3_rollout_transfer.md").write_text("\n".join(L), encoding="utf-8")

    print("overtake...", flush=True)
    L2, ov = overtake()
    L += L2
    (OUT / "jj3_rollout_transfer.md").write_text("\n".join(L), encoding="utf-8")
    pd.concat([lt.assign(scenario="ltap"), ov.assign(scenario="overtake")], ignore_index=True) \
      .to_csv(OUT / "jj3_rollout_cells.csv", index=False)
    print(f"main report written at {time.time() - t_start:.0f} s", flush=True)

    print("the trait (two hierarchical fits, minutes each)...", flush=True)
    L3, both = trait(lt)
    L += L3
    both.to_csv(OUT / "jj3_driver_levels.csv", index=False)
    L += [f"Run time {time.time() - t_start:.0f} s.", ""]
    (OUT / "jj3_rollout_transfer.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L3))


if __name__ == "__main__":
    main()
