"""
Card HS.1 -- situational surprise as the start of the response: the other road user's
actions alone, or the situation as a whole?

PRE-STATED before any response data was read by this script (2026-09-13).

THE QUESTION (Jonas, 2026-09-12). Card Q5.1 proposed that surprise about *what other road
users do* could mark when a situation starts to count. Jonas asked whether surprise should
instead be taken about the *situation as a whole*: in these studies the ego is automated,
and the driver experiences the ego's manoeuvre and the other road user's together; when that
joint situation turns surprising, accumulation starts. He has long held that surprise can say
WHEN a situation starts to count but not HOW CRITICAL it is, so surprise is tested here only
as the onset, never as the axis.

THE REFERENCES (src/surprise/situational.py). One constant-velocity predictor, three choices
of what it monitors:
  world     the other road users' own motion                        (card Q5.1)
  joint     the ego's own motion and the other road users', jointly  (Jonas's "system")
  relative  the other road users' position relative to the ego       (the driver's seat)
Onset = first time any monitored axis leaves its predicted band by z_on = 2 standard
deviations, searched from the start of the shown clip.

PREDICTOR SETTINGS, and why. Settled from the kinematics alone, before any response was read:
  h = 1.0 s        A fixed-horizon predictor only sees a change that leaves the band within one
                   horizon (the error after a constant acceleration a is at most a h^2 / 2;
                   module docstring). At h = 0.5 s a lane change would need ~5.6 m/s^2 of
                   lateral acceleration to register; at 1 s the study's gentlest lane change
                   (about 1 m/s^2 peak, LCD 4 s) registers at sigma0 up to ~0.25 m.
  v_window = 0.3 s The traces carry position jitter: on steady driving a one-sample velocity
                   estimate leaves up to 0.89 m of longitudinal prediction error at h = 1 s;
                   a 0.3 s window leaves at most 0.065 m longitudinal and 0.004 m lateral
                   (99.9th percentile over all 90 study-2 traces, measured 2026-09-13). 0.3 s
                   is the study's timepoint spacing and card G.1's clearance-rate window.
  sigma0 = 0.1 m   PRIMARY. The noticeable positional discrepancy. Card Q5.1's value (the
                   traces' positional resolution); at z_on = 2 the band edge is 0.2 m, three
                   times the worst jitter floor. It is NOT a verified perceptual threshold
                   (query HS1.Q1). Sweep {0.05, 0.1, 0.2, 0.4} m: the lower bound is the
                   jitter floor, the upper the point where the gentlest lane change stops
                   registering within the horizon. Verdicts are stated at the primary only.
  sigma1 = sigma_a = 0   The traces are noise-free apart from jitter, and any growth term only
                   delays onset, which the sigma0 sweep already spans.
[Design history, 2026-09-13, before any data run: the first draft used h = 0.5 s,
sigma(h) = 0.1 + 0.5 h and a one-sample velocity. The property tests showed that setting is
blind to lane changes, and the jitter measurement showed one-sample velocities are unusable
on these traces. Both changes were made on kinematics only.]

[Correction after the first run, 2026-09-13 -- TESTS B AND C ONLY. The settings above were set
from the jitter floor of the SECOND study's 30 Hz traces and applied unmeasured to the FIRST
study's 10 Hz traces. Those jitter far more along the direction of travel: positions depart from
constant motion by about 7% of each frame's advance against every clock the file records
(elapsed time, wall clock, frame index; residual sd 0.106 m for the ego at 14.3 m/s), so the
steady-driving floor at h = 1 s is 3.17 m longitudinal with a 0.3 s velocity window and 1.17 m
with 1.0 s, against 0.13 m lateral. In the first run every reference -- world included, on a
cyclist riding steadily -- "onset" at the first moment of the search window (8.61 s before the
ego's pull-out in all three overtakes, 8.3-8.7 s before the decision moment in most left turns),
on the longitudinal axis. That was jitter, not surprise, and those onsets are withdrawn.
Tests B and C now apply the SAME rule the primary was set by -- band edge at three times the
worst measured floor -- per axis, to the first study's own floor: v_window = 1.0 s (it lowers
the longitudinal floor from 3.17 to 1.17 m and leaves the lateral one unchanged),
sigma0_lat = 1.5 x 0.133 = 0.20 m, sigma0_lon = 1.5 x 1.17 = 1.8 m. The consequence is stated
plainly: on the first study the predictor is effectively blind longitudinally (a braking event
would need about 7 m/s^2 to register), so tests B and C can speak only to lateral surprise --
which is what they ask about (the ego pulling out; the ego turning). Test A is untouched and was
not rerun; its section of the report is carried over from the first run.]

TEST A -- the cut-in, second study (378 cells; CP1 = 90 pre-onset, CP2-CP5 = 288 post-onset).
Same cells, leave-one-starting-TTC-out folds and weighted RMSE as the registered R.2 script,
the EL.1 axis and G.1's code, all imported unchanged. Models on the post-onset cells:
  (c) ungated EL.1 linear rule                                 [card G.1 reported 0.1137]
  (k) card G.1's fitted clearance gate, 2 gate parameters       [card G.1 reported 0.1027]
  (s) the SURPRISE gate: P = b + (1 - b) g Phi((x - c)/sigma), g = 1 once the surprise onset
      precedes the clip end, else 0. NO gate parameter is fitted.  One per reference.
Each full post-onset fit then predicts the 90 CP1 cells out of sample.
  A1 (primary, joint): the surprise gate is CREDITED as a parameter-free replacement for G.1's
     fitted gate iff CP1 out-of-sample wRMSE < 0.05 (G.1's own criterion) AND its post-onset
     held-out wRMSE <= (k) + 0.01. Otherwise NOT CREDITED, naming the condition that failed.
  A2 world vs joint vs relative: the ego holds its lane at constant speed here, so the three
     are expected to agree; any score difference > 0.005 is reported and traced to its source.
  A3 accumulation from onset (Jonas's proposal) against a state threshold, both with the
     surprise gate, both on trace kinematics, three parameters each:
       state         x = log theta_dot(T)
       accumulation  x = log(theta(T) - theta(t_onset)), the non-leaky integral of the looming
                     rate from the surprise onset (the integral of theta_dot is theta)
     Accumulation PREFERRED iff its post-onset held-out wRMSE <= state - 0.01; state PREFERRED
     iff >= state + 0.01; otherwise a TIE.
  A4 onset latency after the kinematic manoeuvre onset, by lane-change duration. The pipeline
     review's constraint is that responses do not depend on lane-change duration at matched
     time since onset; a latency that grows with duration is reported as a cost of the
     reference, not tuned away.

TEST B -- the cyclist overtake, first study (15 cells). The automated ego pulls out around a
cyclist who holds its line (lateral span 2.24 m against 0.16 m). Pre-stated expectation: world
surprise never onsets (Q5.1's test-2 derivation), while joint and relative onset at the
ego's pull-out. Reported per cell: observed share intervening, and whether each reference's
gate is open at the clip end. Reading, stated now: if world surprise is absent while
participants intervene, surprise about other road users cannot start the response in this
scenario and a situational reference is necessary. Cells answered with the gate still closed
are reported as responses that precede the situational surprise -- for example anticipation
of a known manoeuvre. No model is fitted to 15 cells.

TEST C -- the left turn across path, first study (18 cells, one decision moment). The ego
turns; the oncoming vehicle drives steadily. Same expectation and reading as test B, against
the decision moment of 13.5 s trace time.

Output: replication/czb/out/hs1_situational_surprise.md, and out/hs1_onsets.csv.
Run:    python replication/czb/hs1_situational_surprise.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import cutin2_two_axis as T                # noqa: E402  card EL.1
import cutin2_gate as G                    # noqa: E402  card G.1
from comfortzone.cutin import _trim_teardown                              # noqa: E402
from comfortzone.ltap import T_DECISION_S, ltap_cells, trace_name        # noqa: E402
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES, load_overtake_trace  # noqa: E402
from comfortzone import czb_data                                          # noqa: E402
from surprise.situational import (                                        # noqa: E402
    REFERENCES, PredictorSettings, Track, onset_time, situational_surprise,
)

OUT = HERE / "out"
H, V_WINDOW, Z_ON = 1.0, 0.3, 2.0
SIGMA0_PRIMARY = 0.1
SIGMA0_SWEEP = (0.05, 0.1, 0.2, 0.4)
EGO_LEN = R.EGO_LEN
MANOEUVRE_DY = 0.05          # m, kinematic lateral-onset threshold on the smoothed relative offset
KIN1 = czb_data.KIN_RANDOM


def settings(sigma0: float) -> PredictorSettings:
    return PredictorSettings(h=H, sigma0=sigma0, z_on=Z_ON, v_window=V_WINDOW)


# First study (10 Hz): measured floor with a 1.0 s velocity window, 99.9th percentile maximum
# over steady segments of all overtake and left-turn traces (see the docstring's correction).
S1_FLOOR_LAT, S1_FLOOR_LON = 0.133, 1.17
S1_V_WINDOW = 1.0


def settings_study1() -> PredictorSettings:
    return PredictorSettings(h=H, sigma0=1.5 * S1_FLOOR_LAT, sigma0_lon=1.5 * S1_FLOOR_LON,
                             z_on=Z_ON, v_window=S1_V_WINDOW)


def study1_onsets(ego_id, tracks, t_from):
    s = settings_study1()
    ego = tracks[ego_id]
    others = {v: tr for v, tr in tracks.items() if v != ego_id}
    out = {}
    for ref in REFERENCES:
        ser = situational_surprise(ego, others, ref, s)
        t_on = onset_time(ser, s, t_from=t_from)
        src = ser.source.iloc[int(np.argmin(np.abs(ser.t.to_numpy() - t_on)))] if np.isfinite(t_on) else ""
        out[ref] = (t_on, src)
    return out


# ---------------------------------------------------------------------------------
# scenes: world-frame tracks for every vehicle, on a common grid
# ---------------------------------------------------------------------------------

def scene_tracks(path: Path):
    raw = pd.read_csv(path)
    parts = {int(v): _trim_teardown(g) for v, g in raw.groupby("Vehicle_ID")}
    parts = {v: g for v, g in parts.items() if len(g) > 10}
    t0 = max(g.Elapsed_Time_s.iloc[0] for g in parts.values())
    t1 = min(g.Elapsed_Time_s.iloc[-1] for g in parts.values())
    ref = next(iter(parts.values()))
    grid = ref.Elapsed_Time_s.to_numpy()
    grid = grid[(grid >= t0 - 1e-9) & (grid <= t1 + 1e-9)]
    tracks, meta = {}, {}
    for v, g in parts.items():
        tt = g.Elapsed_Time_s.to_numpy()
        tracks[v] = Track(grid, np.interp(grid, tt, g.Location_X.to_numpy()),
                          np.interp(grid, tt, g.Location_Y.to_numpy()))
        meta[v] = {"width": float(g.Width_m.iloc[0]), "length": float(g.Length_m.iloc[0]),
                   "yaw_span": float(np.ptp(np.unwrap(np.deg2rad(g.Heading.to_numpy()))))
                   if "Heading" in g else 0.0,
                   "heading": np.interp(grid, tt, np.unwrap(np.deg2rad(g.Heading.to_numpy())))
                   if "Heading" in g else None,
                   "speed": np.interp(grid, tt, g.Speed_mps.to_numpy())}
    return grid, tracks, meta


def surprise_series(ego_id, tracks, sigma0):
    """z_max series at sigma0 = 1 m for each reference; the band edge scales linearly with
    sigma0 when sigma1 = sigma_a = 0, so onsets at any sigma0 threshold the same series."""
    s1 = settings(1.0)
    ego = tracks[ego_id]
    others = {v: tr for v, tr in tracks.items() if v != ego_id}
    return {ref: situational_surprise(ego, others, ref, s1) for ref in REFERENCES}


def onset_at(series, sigma0, t_from):
    s = settings(sigma0)
    scaled = series.copy()
    scaled["z_max"] = series["z_max"] / sigma0
    return onset_time(scaled, s, t_from=t_from)


# ---------------------------------------------------------------------------------
# study 2: the cut-in
# ---------------------------------------------------------------------------------

def study2_scenes(cells: pd.DataFrame):
    """Per trace: grid, tracks, ego and target ids, surprise series, kinematic onset."""
    out = {}
    for v in cells.video:
        m = R.VIDEO_RE.match(v)
        key = f"LC_dv{m['dv']}_Tlc{m['tlc']}_TTC{int(m['ttc']):02d}"
        if key in out:
            continue
        grid, tracks, meta = scene_tracks(R.KIN / f"{key}_vehicle_states.csv")
        y_span = {vid: float(np.ptp(tr.y)) for vid, tr in tracks.items()}
        tar = max(y_span, key=y_span.get)                       # the lane changer
        # ego: of the rest, the car that ends in the target's destination lane
        rest = [vid for vid in tracks if vid != tar]
        y_end_tar = tracks[tar].y[-1]
        ego = min(rest, key=lambda vid: abs(tracks[vid].y[-1] - y_end_tar))
        out[key] = {"grid": grid, "tracks": tracks, "meta": meta, "ego": ego, "tar": tar,
                    "series": surprise_series(ego, tracks, 1.0)}
    return out


def kinematic_onset(sc, t_from):
    """Lateral manoeuvre onset from the target's offset relative to the ego: a 0.3 s backward
    moving average, departing by MANOEUVRE_DY from its median over the first 5 s of the clip.
    Used only to report latencies, never in a fit."""
    t = sc["grid"]
    yrel = sc["tracks"][sc["tar"]].y - sc["tracks"][sc["ego"]].y
    dt = float(np.median(np.diff(t)))
    k = max(1, int(round(0.3 / dt)))
    ma = pd.Series(yrel).rolling(k, min_periods=1).mean().to_numpy()
    base_mask = (t >= t_from) & (t < t_from + 5.0)
    base = float(np.median(ma[base_mask]))
    hit = np.flatnonzero((t >= t_from + 5.0) & (np.abs(ma - base) > MANOEUVRE_DY))
    return float(t[hit[0]]) if len(hit) else float("nan")


def theta_state(sc, t_at):
    """Optical angle and its rate of the target, from trace kinematics, at time t_at."""
    t = sc["grid"]
    i = int(np.clip(np.searchsorted(t, t_at, side="right") - 1, 0, len(t) - 1))
    ego, tar = sc["tracks"][sc["ego"]], sc["tracks"][sc["tar"]]
    W, L = sc["meta"][sc["tar"]]["width"], sc["meta"][sc["tar"]]["length"]
    # longitudinal separation along world x: the road's angle to x is ~0.02 m/s of drift at
    # 30 m/s, under 0.1 degree, so the along-road and world-x gaps agree to a millimetre
    gap = max(abs(tar.x[i] - ego.x[i]) - 0.5 * (L + EGO_LEN), 1e-3)
    dv = sc["meta"][sc["ego"]]["speed"][i] - sc["meta"][sc["tar"]]["speed"][i]
    theta = 2.0 * np.arctan(W / (2.0 * gap))
    theta_dot = W * dv / (gap ** 2 + W ** 2 / 4.0)
    return theta, theta_dot


# --- gated fits ----------------------------------------------------------------------

def predict_sgated(p, u, v, g):
    x = G.x_linear(p[0], u, v)
    b = 1.0 / (1.0 + np.exp(-p[1]))
    return b + (1.0 - b) * g * norm.cdf((x - p[2]) / np.exp(p[3]))


def fit_sgated(u, v, g, y, w):
    bounds = [(-8, 8), (-30, 10), (None, None), (-10, 10)]

    def obj(p):
        val = float(np.sum(w * (predict_sgated(p, u, v, g) - y) ** 2))
        return val if np.isfinite(val) else 1e12
    best, best_val = None, np.inf
    open_ = g > 0.5
    for a0 in np.linspace(-3, 3, 7):
        x0 = G.x_linear(a0, u, v)
        th0 = T.fit_reg(x0[open_], y[open_], w[open_]) if open_.sum() >= 5 else np.array([-2.0, 0.0, 0.0])
        r = minimize(obj, np.array([a0, th0[0], th0[1], th0[2]]), method="L-BFGS-B", bounds=bounds)
        if r.fun < best_val:
            best, best_val = r.x, r.fun
    return best


def predict_1d(th, x, g):
    b = 1.0 / (1.0 + np.exp(-th[0]))
    xx = np.where(g > 0.5, x, 0.0)
    return b + (1.0 - b) * g * norm.cdf((xx - th[1]) / np.exp(th[2]))


def fit_1d_gated(x, g, y, w):
    open_ = (g > 0.5) & np.isfinite(x)
    xo = x[open_]
    lo, hi = np.quantile(xo, [0.1, 0.9]) if len(xo) else (0.0, 1.0)
    spread = max(np.std(xo), 1e-6) if len(xo) else 1.0

    def obj(th):
        val = float(np.sum(w * (predict_1d(th, x, g) - y) ** 2))
        return val if np.isfinite(val) else 1e12
    best, best_val = None, np.inf
    for c0 in np.linspace(lo, hi, 5):
        for ls0 in (np.log(spread), np.log(spread / 4 + 1e-9)):
            r = minimize(obj, np.array([-2.0, c0, ls0]), method="L-BFGS-B")
            if r.fun < best_val:
                best, best_val = r.x, r.fun
    return best


def held_out(post, folds, fit, predict, cols):
    y, w = post.p.to_numpy(float), post.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        p = fit(post[tr], y[tr], w[tr])
        pred[te] = predict(p, post[te])
    return pred


def main() -> None:
    OUT.mkdir(exist_ok=True)
    L = ["# Card HS.1 -- situational surprise as the start of the response", "",
         "Generated by `replication/czb/hs1_situational_surprise.py`; references, predictor "
         "settings, tests and decision rules pre-stated in its docstring before the run. Do not "
         "edit by hand.", "",
         f"Predictor: constant velocity, h = {H} s, velocity over {V_WINDOW} s, onset at "
         f"z = {Z_ON}; sigma0 primary {SIGMA0_PRIMARY} m, sweep {list(SIGMA0_SWEEP)} m.", ""]

    # ================================================================ TEST A: study 2
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = study2_scenes(cells)
    rows = []
    for _, c in cells.iterrows():
        m = R.VIDEO_RE.match(c.video)
        key = f"LC_dv{m['dv']}_Tlc{m['tlc']}_TTC{int(m['ttc']):02d}"
        sc = scenes[key]
        s_t, e_t = R._f(m["s"]), R._f(m["e"])
        row = {"video": c.video, "trace": key, "cp": c.cp, "lcd": c.lcd, "s_t": s_t, "e_t": e_t,
               "t_kin": kinematic_onset(sc, s_t)}
        for ref in REFERENCES:
            for s0 in SIGMA0_SWEEP:
                row[f"on_{ref}_{s0}"] = onset_at(sc["series"][ref], s0, t_from=s_t + H + V_WINDOW)
        th_e, thd_e = theta_state(sc, e_t)
        row["theta_e"], row["theta_dot_e"] = th_e, thd_e
        for ref in REFERENCES:
            for s0 in SIGMA0_SWEEP:
                t_on = row[f"on_{ref}_{s0}"]
                row[f"theta_on_{ref}_{s0}"] = theta_state(sc, t_on)[0] if np.isfinite(t_on) else np.nan
        rows.append(row)
    ons = pd.DataFrame(rows)
    ons.to_csv(OUT / "hs1_onsets.csv", index=False)
    cells = cells.merge(ons, on=["video", "cp", "lcd"], how="left")

    # --- A0: sources and the kinematic onset --------------------------------------
    post_mask = cells.cp != "CP1"
    kin_rel = (cells.t_kin - cells.e_t)
    cp1 = cells[cells.cp == "CP1"]
    L += ["## Test A -- the cut-in, second study", "",
          "### A0 The kinematic manoeuvre onset against the clip ends", "",
          f"Kinematic lateral onset (target offset relative to the ego leaves its baseline by "
          f"{MANOEUVRE_DY} m) minus the CP1 clip end: median "
          f"{float(np.nanmedian(cp1.t_kin - cp1.e_t)):+.3f} s, range "
          f"{float(np.nanmin(cp1.t_kin - cp1.e_t)):+.3f} to {float(np.nanmax(cp1.t_kin - cp1.e_t)):+.3f} s "
          f"over the {len(cp1)} CP1 clips (positive = the manoeuvre starts after CP1 ends).", ""]

    # --- A4: latencies by LCD ------------------------------------------------------------
    L += ["### A4 Onset latency after the kinematic manoeuvre onset, by lane-change duration", "",
          "Median latency [s] over the 90 traces (one per trace), and how many traces never "
          "register within the clip.", "",
          "| reference | sigma0 [m] | LCD 2 s | LCD 3 s | LCD 4 s | never |", "|---|---|---|---|---|---|"]
    per_trace = ons.sort_values("cp").groupby("trace").last().reset_index()   # CP5: longest window
    for ref in REFERENCES:
        for s0 in SIGMA0_SWEEP:
            lat = per_trace[f"on_{ref}_{s0}"] - per_trace.t_kin
            cols = []
            for lcd in (2.0, 3.0, 4.0):
                sel = lat[per_trace.lcd == lcd]
                cols.append(f"{float(np.nanmedian(sel)):+.2f}" if sel.notna().any() else "never")
            never = int(per_trace[f"on_{ref}_{s0}"].isna().sum())
            L.append(f"| {ref} | {s0} | " + " | ".join(cols) + f" | {never} |")
    L.append("")

    # --- fits -------------------------------------------------------------------------------
    post = cells[post_mask].reset_index(drop=True)
    cpo = cells[~post_mask].reset_index(drop=True)
    st = G.lateral_states(cells.video)
    post = post.merge(st[["video", "l0", "ldot"]], on="video", how="left")
    cpo = cpo.merge(st[["video", "l0", "ldot"]], on="video", how="left")
    y, w = post.p.to_numpy(float), post.n.to_numpy(float)
    y1, w1 = cpo.p.to_numpy(float), cpo.n.to_numpy(float)
    folds = post.ttc_start.to_numpy(float)
    wr = G.wrmse

    pred_c, _ = G.held_out_ungated(post, folds)
    r_c = wr(y, pred_c, w)
    pred_k, _ = G.held_out_gated(post, folds)
    r_k = wr(y, pred_k, w)
    u, v = G.axes(post)
    u1, v1 = G.axes(cpo)
    p_lin, _ = T.fit_linear(u, v, y, w)
    wt = 1.0 / (1.0 + np.exp(-p_lin[0]))
    r1_c = wr(y1, R.predict(p_lin[1:], wt * u1 + (1 - wt) * v1, +1.0), w1)
    p_g = G.fit_gated(u, v, post.l0.to_numpy(float), post.ldot.to_numpy(float), y, w)
    r1_k = wr(y1, G.predict_gated(p_g, u1, v1, cpo.l0.to_numpy(float), cpo.ldot.to_numpy(float)), w1)

    def gate_col(df, ref, s0):
        on = df[f"on_{ref}_{s0}"].to_numpy(float)
        return (np.isfinite(on) & (on <= df.e_t.to_numpy(float))).astype(float)

    def surprise_gate_scores(ref, s0):
        g = gate_col(post, ref, s0)
        g1 = gate_col(cpo, ref, s0)
        pred = np.full_like(y, np.nan)
        for f in np.unique(folds):
            tr, te = folds != f, folds == f
            ut, vt = G.axes(post[tr])
            p = fit_sgated(ut, vt, g[tr], y[tr], w[tr])
            ue, ve = G.axes(post[te])
            pred[te] = predict_sgated(p, ue, ve, g[te])
        p_full = fit_sgated(u, v, g, y, w)
        return wr(y, pred, w), wr(y1, predict_sgated(p_full, u1, v1, g1), w1), float(g.mean()), float(g1.mean())

    def x_state(df):
        return np.log(np.maximum(df.theta_dot_e.to_numpy(float), 1e-9))

    def x_accum(df, ref, s0):
        d = df.theta_e.to_numpy(float) - df[f"theta_on_{ref}_{s0}"].to_numpy(float)
        return np.log(np.maximum(d, 1e-9))

    def one_d_scores(xfun, ref, s0):
        g = gate_col(post, ref, s0)
        x = xfun(post)
        pred = np.full_like(y, np.nan)
        for f in np.unique(folds):
            tr, te = folds != f, folds == f
            th = fit_1d_gated(x[tr], g[tr], y[tr], w[tr])
            pred[te] = predict_1d(th, x[te], g[te])
        return wr(y, pred, w)

    L += ["### A1-A2 The surprise gate against card G.1's fitted gate", "",
          f"Reproductions: (c) ungated {r_c:.4f} (card G.1: 0.1137); (k) G.1 gated {r_k:.4f} "
          f"(card G.1: 0.1027); CP1 out of sample (c) {r1_c:.4f} (0.4832), (k) {r1_k:.4f} (0.0319).", "",
          "| model | gate parameters fitted | sigma0 [m] | post-onset held-out wRMSE | CP1 out of sample | "
          "gate open, post-onset | gate open, CP1 |", "|---|---|---|---|---|---|---|",
          f"| (c) ungated EL.1 | - | - | {r_c:.4f} | {r1_c:.4f} | - | - |",
          f"| (k) G.1 clearance gate | 2 | - | {r_k:.4f} | {r1_k:.4f} | - | - |"]
    sweep_scores = {}
    for ref in REFERENCES:
        for s0 in SIGMA0_SWEEP:
            if ref != "joint" and s0 != SIGMA0_PRIMARY:
                continue
            ho, c1, go, g1o = surprise_gate_scores(ref, s0)
            sweep_scores[(ref, s0)] = (ho, c1)
            tag = " **primary**" if (ref == "joint" and s0 == SIGMA0_PRIMARY) else ""
            L.append(f"| (s) surprise gate, {ref}{tag} | 0 | {s0} | {ho:.4f} | {c1:.4f} | {go:.2f} | {g1o:.2f} |")
    L.append("")
    ho_p, c1_p = sweep_scores[("joint", SIGMA0_PRIMARY)]
    cond1, cond2 = c1_p < 0.05, ho_p <= r_k + 0.01
    if cond1 and cond2:
        verdict_a1 = "CREDITED: CP1 out of sample {:.4f} < 0.05 and post-onset {:.4f} <= {:.4f}.".format(c1_p, ho_p, r_k + 0.01)
    else:
        failed = [n for n, ok in (("CP1 < 0.05", cond1), (f"post-onset <= (k) + 0.01 = {r_k + 0.01:.4f}", cond2)) if not ok]
        verdict_a1 = f"NOT CREDITED: failed {', '.join(failed)} (CP1 {c1_p:.4f}, post-onset {ho_p:.4f})."
    prim = [sweep_scores[(r, SIGMA0_PRIMARY)] for r in REFERENCES]
    spread_ho = max(p[0] for p in prim) - min(p[0] for p in prim)
    spread_c1 = max(p[1] for p in prim) - min(p[1] for p in prim)
    L += [f"**A1 (pre-stated rule, joint, sigma0 {SIGMA0_PRIMARY} m): {verdict_a1}**", "",
          f"**A2:** across the three references at the primary sigma0 the post-onset scores span "
          f"{spread_ho:.4f} and the CP1 scores {spread_c1:.4f} "
          + ("(within 0.005: they agree, as expected with an ego holding its lane)."
             if max(spread_ho, spread_c1) <= 0.005 else "(more than 0.005: see A4 for which trajectory drives the onsets)."), ""]

    # --- A3 accumulation from onset ----------------------------------------------------
    L += ["### A3 Accumulation from the surprise onset against a state threshold", "",
          "Both with the surprise gate and trace kinematics, three parameters each.", "",
          "| reference | sigma0 [m] | state: log theta_dot(T) | accumulation: log(theta(T) - theta(t_on)) | difference |",
          "|---|---|---|---|---|"]
    a3 = {}
    for s0 in SIGMA0_SWEEP:
        r_state = one_d_scores(lambda df: x_state(df), "joint", s0)
        r_acc = one_d_scores(lambda df, s0=s0: x_accum(df, "joint", s0), "joint", s0)
        a3[s0] = (r_state, r_acc)
        tag = " **primary**" if s0 == SIGMA0_PRIMARY else ""
        L.append(f"| joint{tag} | {s0} | {r_state:.4f} | {r_acc:.4f} | {r_acc - r_state:+.4f} |")
    r_state, r_acc = a3[SIGMA0_PRIMARY]
    if r_acc <= r_state - 0.01:
        v3 = "ACCUMULATION PREFERRED"
    elif r_acc >= r_state + 0.01:
        v3 = "STATE THRESHOLD PREFERRED"
    else:
        v3 = "TIE"
    L += ["", f"**A3 (pre-stated rule, joint, sigma0 {SIGMA0_PRIMARY} m): {v3}** "
          f"(state {r_state:.4f}, accumulation {r_acc:.4f}).", ""]

    write_report(L, tests_bc())


def tests_bc() -> list[str]:
    s1 = settings_study1()
    B = ["## Test B -- the cyclist overtake, first study", "",
         f"First-study predictor (docstring correction): velocity over {S1_V_WINDOW} s, sigma0 "
         f"{s1.sigma0:.2f} m lateral and {s1.sigma0_lon:.2f} m longitudinal (three times the "
         f"measured 10 Hz floor, per axis). Onset search from the clip start plus h + velocity window.", ""]
    trials = czb_data.random_overtake_trials()
    ov = (trials.groupby(["criticality", "timepoint"])
          .agg(p=("intervene", "mean"), n=("intervene", "size"), t_end=("t_end", "first"))
          .reset_index())
    ov_lines = ["| clearance | timepoint | share intervening (n) | world gate | joint gate | relative gate |",
                "|---|---|---|---|---|---|"]
    ov_rows = []
    for lab, path in RANDOM_OVERTAKE_TRACES.items():
        tr = load_overtake_trace(path)
        grid, tracks, meta = scene_tracks(path)
        ego_id = max(meta, key=lambda vid: meta[vid]["width"])
        t_ego_on = float(tr.t[tr.onset_idx])
        t_from = max(grid[0], t_ego_on - czb_data.RANDOM_CLIP_LEAD_S) + H + S1_V_WINDOW
        on = study1_onsets(ego_id, tracks, t_from)
        ov_rows.append((lab, t_ego_on, on))
        for _, c in ov[ov.criticality == lab].sort_values("timepoint").iterrows():
            t_clip = t_ego_on + float(c.t_end)
            gates = ["open" if np.isfinite(on[ref][0]) and on[ref][0] <= t_clip else "closed" for ref in REFERENCES]
            ov_lines.append(f"| {lab} | {c.timepoint} | {c.p:.3f} ({int(c.n)}) | " + " | ".join(gates) + " |")
    B += ["Onsets relative to the ego's lateral onset (the study's C1 clip end), with the trajectory "
          "and axis that produced them:", "",
          "| clearance | world | joint | relative |", "|---|---|---|---|"]
    for lab, t_ego_on, on in ov_rows:
        B.append(f"| {lab} | " + " | ".join(
            (f"{on[ref][0] - t_ego_on:+.2f} s ({on[ref][1]})" if np.isfinite(on[ref][0]) else "never")
            for ref in REFERENCES) + " |")
    B += [""] + ov_lines + [""]

    C = ["## Test C -- the left turn across path, first study", ""]
    lc = ltap_cells(with_responses=True)
    lt_lines = ["| speed [km/h] | PET [s] | share intervening | world onset | joint onset | relative onset |",
                "|---|---|---|---|---|---|"]
    for _, c in lc.sort_values(["speed_kph", "pet"]).iterrows():
        path = KIN1 / f"{trace_name(float(c.pet), int(c.speed_kph))}_vehicle_states.csv"
        grid, tracks, meta = scene_tracks(path)
        ego_id = max(meta, key=lambda vid: meta[vid]["yaw_span"])
        t_from = max(grid[0], T_DECISION_S - czb_data.RANDOM_CLIP_LEAD_S) + H + S1_V_WINDOW
        on = study1_onsets(ego_id, tracks, t_from)
        lt_lines.append(f"| {int(c.speed_kph)} | {float(c.pet):.1f} | {float(c.p):.3f} | " + " | ".join(
            (f"{on[ref][0] - T_DECISION_S:+.2f} s ({on[ref][1]})" if np.isfinite(on[ref][0]) else "never")
            for ref in REFERENCES) + " |")
    t_turn = float(np.median(lc.t_onset))
    C += [f"Onsets relative to the decision moment ({T_DECISION_S} s trace time, where every clip "
          f"ends); negative = before it. The ego's own turn onset (`ltap_cells.t_onset`) is at a "
          f"median {t_turn - T_DECISION_S:+.2f} s, after the clips end.", ""]
    C += lt_lines + [""]
    return B + C


def write_report(head: list[str], bc: list[str]) -> None:
    text = "\n".join(head + bc)
    (OUT / "hs1_situational_surprise.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-bc", action="store_true",
                    help="recompute tests B and C only, carrying test A's section over unchanged")
    args = ap.parse_args()
    if args.only_bc:
        old = (OUT / "hs1_situational_surprise.md").read_text(encoding="utf-8")
        head = old.split("## Test B")[0].rstrip("\n").split("\n") + [""]
        head.insert(4, "*Tests B and C recomputed on 2026-09-13 with the first study's own jitter "
                       "floor (docstring correction); test A's section is carried over from the first run, "
                       "whose code it was produced by is unchanged.*")
        head.insert(5, "")
        write_report(head, tests_bc())
    else:
        main()
