"""
Card PC.1 -- the projected-conflict gate: one construction for every scenario.

PRE-STATED before the run (2026-09-16), from `docs/projected_conflict_gate_note.md`, which was
written first and says why. The construction is `src/comfortzone/conflict.py` (property tests in
`tests/test_conflict.py`). In one line: each road user's path is projected over a horizon, the
other road user's by constant velocity, the ego's either by constant velocity (reading K) or as its
recorded future (reading P), or the union (KP); the clearance c is the smallest edge-to-edge distance
between one body at any time within the horizon and the other's path corridor (the path over an
extended span, 20 s; note section 2.2 as corrected 2026-09-16), in either ordering; the gate is
Phi((m - c)/s), card G.1's form; at the response moment it is the maximum over the shown clip
(persistence), the instantaneous value reported alongside.

SETTINGS, all inherited: velocity windows 0.3 s (second study, 30 Hz) and 1.0 s (first study,
10 Hz) from card HS.1's measured jitter floors; the horizon primary 3.0 s (G.1), sweep {3, 4, 5, 6} s
reported without a verdict; projection step 0.1 s; the persistence maximum on a 0.2 s evaluation
grid over the shown window plus the response moment itself; bodies from the traces' width and
length columns; roles from HS.1's scene loaders (never assigned here); the shown window is the
video name's S..E stamps (cut-in) or the ten seconds before the manoeuvre onset up to the timepoint
(first study, `RANDOM_CLIP_LEAD_S`), and no velocity window reaches before the window's start.

TEST 1, THE CUT-IN (G.1's protocol). 288 post-onset cells fit the EL.1 linear rule jointly with the
gate's m and s (G.1's starts and bounds), leave-one-starting-TTC-out; the 90 CP1 cells are predicted
out of sample from the full post-onset fit. K and P coincide on the cut-in (the ego drives straight);
K is fitted, and |cK - cP| at the response moment is reported over all 378 cells as the check.
Implementation check against G.1, before any fit is read: c at the response moment (K, 3 s) against
G.1's own max(l0 + ldot * 3, 0) from `cutin2_gate.lateral_states`. Rule: the MEDIAN absolute
difference under 0.05 m and the MAXIMUM under 0.20 m, or the run stops and reports. [The note said
0.05 m for the maximum; changed before the run, 2026-09-16, because the construction's bodies are
oriented along their motion while G.1's clearance is axis-aligned, and a car yawed 2.5 degrees in a
lane change protrudes about 0.1 m at its corner. The median rule carries the check.]
CRITERIA, G.1's: CP1 out of sample < 0.05, and post-onset held out <= 0.1027 + 0.01 = 0.1127 (G.1's
gated score, as HS.1 used). Verdict at the primary horizon and the persistent gate; the instantaneous
gate's scores and the sweep are reported without a verdict.

TEST 2, THE LEFT TURN (18 cells, decision moment 13.5 s). The cut-in's m and s frozen (full post-onset
fit at each horizon). Per cell, c and g at the decision moment under K, P, KP, instantaneous and
persistent. CONSISTENT = g >= 0.5 (persistent) in every engaged cell, engaged = share intervening
>= the scenario's lowest cell + 0.2 (margins 0.1 and 0.3 reported without a verdict). COST: B.3.v2's
distance rule (leave-one-PET-level-out; `ltap_two_axis.score(c, "dist")`, 0.056 on file) against the
same rule with the persistent gate multiplied in (HS.1's `fit_1d_gated`); the gated score must be
within 0.01 of the ungated. Where the gate is open in every cell the cost is zero by construction.
PREDICTION on file (note section 2.5, as corrected the same day before the run): K closed in all 18
cells; P and KP open only where the oncoming car's positions within the horizon reach the ego's
planned crossing, so at 3 s the low-PET cells, with more opening as the horizon lengthens.

TEST 3, THE OVERTAKE (3 clearances x 5 timepoints, C1 = the ego's lateral onset, 0.3 s steps). Same
constants frozen. Per clearance and reading: the time the gate first reaches 0.5 relative to the ego's
lateral onset, and g at each timepoint; consistency as in test 2. No cost test (no fitted rule on
file, query B1.Q1). PREDICTION: open in all 15 cells under every reading, opening before C1.

ADOPTION. A reading credited in test 1 and consistent in tests 2 and 3 at the primary horizon is
adopted, in the order K, P, KP. Consistent only at a longer horizon -> reported, adoption deferred to
Jonas. None -> the finding is stated with the scenario that breaks each reading.

[RERUN, 2026-09-16, after the first run (its report kept as out/pc1_projected_conflict_run1.md).
The first run's |cK - cP| check reached 1.619 m on the cut-in, where the ego drives straight, and the
cause was in the construction, not the data: the planned path's continuation past the end of a trace
took its velocity from the last two samples, so a jittered last sample bent the corridor. Fixed in
`conflict.planned_path` (velocity over the last window) with a new property test; nothing else
changed, no rule changed. The first run's verdicts: test 1 credited (0.1126 against <= 0.1127, CP1
0.0356); left turn K 0/18 open at every horizon, P and KP 2/6/9/14 of 18 at 3/4/5/6 s, cost +0.23 to
+0.02, not consistent; overtake open in all 15 cells under every reading; no reading adopted. The
rerun's numbers replace them below, and both sets are in the worklog.]

Output: replication/czb/out/pc1_projected_conflict.md, out/pc1_gates.csv (one row per cell, reading,
horizon), out/pc1_cutin_clearance.csv (the cut-in's c per video and horizon).
Run:    python replication/czb/pc1_projected_conflict.py   (background; about an hour)
"""
from __future__ import annotations

import sys
import time
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
import hs1_situational_surprise as HS      # noqa: E402  card HS.1: scene loaders, 1-D gated fitter
import ltap_two_axis as LT                 # noqa: E402  card B.3.v2: cells, folds, distance rule
from comfortzone import czb_data                                          # noqa: E402
from comfortzone.conflict import Body, clearance_series, gate, persistent  # noqa: E402
from comfortzone.ltap import T_DECISION_S, ltap_cells, trace_name        # noqa: E402
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES, load_overtake_trace  # noqa: E402

OUT = HERE / "out"
HORIZONS = (3.0, 4.0, 5.0, 6.0)
PRIMARY = 3.0
DT_PROJ = 0.1
EVAL_DT = 0.2
V_WINDOW_S2 = HS.V_WINDOW          # 0.3 s
V_WINDOW_S1 = HS.S1_V_WINDOW       # 1.0 s
READINGS = ("K", "P", "KP")
MARGINS = (0.1, 0.2, 0.3)
MARGIN_PRIMARY = 0.2
G1_GATED = 0.1027
CP1_CRIT = 0.05
COST = 0.01
RED_MEDIAN_STOP, RED_MAX_STOP = 0.05, 0.20
LEAD = czb_data.RANDOM_CLIP_LEAD_S


# ---------------------------------------------------------------------------------
# bodies from HS.1's scenes
# ---------------------------------------------------------------------------------

def body(grid, tracks, meta, vid) -> Body:
    m = meta[vid]
    head = m["heading"] if m.get("heading") is not None else np.zeros_like(grid)
    return Body(t=grid, x=tracks[vid].x, y=tracks[vid].y, heading=np.asarray(head, float),
                length=m["length"], width=m["width"])


def eval_grid(t_start, t_end, v_window):
    """The evaluation moments of the shown window: from its start plus the velocity window to its
    end, every EVAL_DT, plus the end itself."""
    g = np.arange(t_start + v_window, t_end - 1e-9, EVAL_DT)
    return np.append(g, t_end)


def series_all(ego, other, times, readings, v_window):
    """c per reading and horizon over the evaluation moments: {(reading, h): array}."""
    out = {}
    for rd in readings:
        for h in HORIZONS:
            out[(rd, h)] = clearance_series(ego, other, times, rd, h, v_window, DT_PROJ)
    return out


def at_moment(times, values, t_at, mode):
    """The instantaneous c at t_at (nearest evaluation moment) or the persistent minimum of c
    over the window up to t_at."""
    i = int(np.argmin(np.abs(times - t_at)))
    return float(values[i]) if mode == "inst" else float(np.min(values[: i + 1]))


# ---------------------------------------------------------------------------------
# the gated fit on the cut-in (G.1's model with c in place of l0 + ldot t_enc)
# ---------------------------------------------------------------------------------

def predict_gated_c(p, u, v, c):
    """p = [a, b_logit, threshold, log sigma, m, log s]."""
    x = G.x_linear(p[0], u, v)
    b = 1.0 / (1.0 + np.exp(-p[1]))
    core = norm.cdf((x - p[2]) / np.exp(p[3]))
    return b + (1.0 - b) * gate(c, p[4], np.exp(p[5])) * core


def fit_gated_c(u, v, c, y, w):
    bounds = [(-8, 8), (-30, 10), (None, None), (-10, 10), (-1.0, 3.0), (-3.0, 2.0)]

    def obj(p):
        val = float(np.sum(w * (predict_gated_c(p, u, v, c) - y) ** 2))
        return val if np.isfinite(val) else 1e12

    best, best_val = None, np.inf
    for a0 in np.linspace(-3, 3, 7):
        th0 = T.fit_reg(G.x_linear(a0, u, v), y, w)
        for m0 in (0.0, 0.5, 1.0, 1.5):
            for s0 in (0.3, 1.0):
                p0 = np.array([a0, th0[0], th0[1], th0[2], m0, np.log(s0)])
                r = minimize(obj, p0, method="L-BFGS-B", bounds=bounds)
                if r.fun < best_val:
                    best, best_val = r.x, r.fun
    return best


def held_out_gated_c(cells, folds, c):
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        u, v = G.axes(cells[tr])
        p = fit_gated_c(u, v, c[tr], y[tr], w[tr])
        u2, v2 = G.axes(cells[te])
        pred[te] = predict_gated_c(p, u2, v2, c[te])
    return pred


# ---------------------------------------------------------------------------------
# test 1: the cut-in
# ---------------------------------------------------------------------------------

def cutin():
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    scenes = HS.study2_scenes(cells)
    rows = []
    t0 = time.time()
    for k, (key, sc) in enumerate(scenes.items()):
        ego = body(sc["grid"], sc["tracks"], sc["meta"], sc["ego"])
        tar = body(sc["grid"], sc["tracks"], sc["meta"], sc["tar"])
        vids = [v for v in cells.video if R.VIDEO_RE.match(v) and
                f"LC_dv{R.VIDEO_RE.match(v)['dv']}_Tlc{R.VIDEO_RE.match(v)['tlc']}_TTC{int(R.VIDEO_RE.match(v)['ttc']):02d}" == key]
        stamps = [(R._f(R.VIDEO_RE.match(v)["s"]), R._f(R.VIDEO_RE.match(v)["e"])) for v in vids]
        t_start = min(s for s, _ in stamps)
        t_end = max(e for _, e in stamps)
        times = eval_grid(t_start, t_end, V_WINDOW_S2)
        ser = series_all(ego, tar, times, ("K",), V_WINDOW_S2)
        # P at the response moments only (the check that the two readings coincide)
        ends = np.array(sorted({e for _, e in stamps}))
        cP = {h: clearance_series(ego, tar, ends, "P", h, V_WINDOW_S2, DT_PROJ) for h in HORIZONS}
        for v, (s, e) in zip(vids, stamps):
            # the persistence window of this video: from its own start stamp to its end
            mask = times >= s + V_WINDOW_S2 - 1e-9
            for h in HORIZONS:
                vals = ser[("K", h)]
                i_end = int(np.argmin(np.abs(times - e)))
                rows.append({"video": v, "trace": key, "h": h,
                             "c_inst": float(vals[i_end]),
                             "c_pers": float(np.min(vals[mask & (times <= e + 1e-9)])),
                             "c_P_inst": float(cP[h][int(np.argmin(np.abs(ends - e)))])})
        print(f"cut-in trace {k + 1}/{len(scenes)} {key}: {len(times)} moments, {time.time() - t0:.0f} s",
              flush=True)
    cl = pd.DataFrame(rows)
    cl.to_csv(OUT / "pc1_cutin_clearance.csv", index=False)

    # the implementation check against G.1
    st = G.lateral_states(cells.video)
    prim = cl[cl.h == PRIMARY].set_index("video")
    c_g1 = np.maximum(st.l0.to_numpy(float) + st.ldot.to_numpy(float) * G.T_ENC, 0.0)
    diff = np.abs(prim.loc[st.video, "c_inst"].to_numpy(float) - c_g1)
    dKP = np.abs(cl.c_inst - cl.c_P_inst)
    L = ["## Test 1 -- the cut-in, second study", "",
         "### Implementation check against card G.1 (K, 3 s, instantaneous, 378 cells)", "",
         "| quantity | median | max |", "|---|---|---|",
         f"| \\|c - max(l0 + ldot x 3, 0)\\| [m] | {np.median(diff):.3f} | {diff.max():.3f} |",
         f"| \\|cK - cP\\| at the response moment, all horizons [m] | {dKP.median():.3f} | {dKP.max():.3f} |", ""]
    ok = np.median(diff) < RED_MEDIAN_STOP and diff.max() < RED_MAX_STOP
    L.append(f"Pre-stated stop rule: median >= {RED_MEDIAN_STOP} m or max >= {RED_MAX_STOP} m aborts test 1. -> "
             + ("proceed." if ok else "**TEST 1 ABORTED**; no fit read."))
    L.append("")
    if not ok:
        return L, None, cl

    post = cells[cells.cp != "CP1"].reset_index(drop=True)
    cp1 = cells[cells.cp == "CP1"].reset_index(drop=True)
    folds = post.ttc_start.to_numpy(float)
    y, w = post.p.to_numpy(float), post.n.to_numpy(float)
    y1, w1 = cp1.p.to_numpy(float), cp1.n.to_numpy(float)
    L += ["### Held-out accuracy (leave-one-starting-TTC-out) and CP1 out of sample", "",
          "| horizon [s] | gate | post-onset held-out wRMSE | CP1 out of sample | m [m] | s [m] | gate open post-onset (mean) | gate open CP1 (mean) |",
          "|---|---|---|---|---|---|---|---|"]
    frozen = {}
    for h in HORIZONS:
        for mode in ("pers", "inst"):
            col = f"c_{mode}"
            cmap = cl[cl.h == h].set_index("video")[col]
            c_post = cmap.loc[post.video].to_numpy(float)
            c_cp1 = cmap.loc[cp1.video].to_numpy(float)
            pred = held_out_gated_c(post, folds, c_post)
            ho = G.wrmse(y, pred, w)
            u, v = G.axes(post)
            p = fit_gated_c(u, v, c_post, y, w)
            u1, v1 = G.axes(cp1)
            oos = G.wrmse(y1, predict_gated_c(p, u1, v1, c_cp1), w1)
            m, s = float(p[4]), float(np.exp(p[5]))
            g_post, g_cp1 = gate(c_post, m, s), gate(c_cp1, m, s)
            L.append(f"| {h:.0f} | {'persistent' if mode == 'pers' else 'instantaneous'} | {ho:.4f} | {oos:.4f} | "
                     f"{m:.3f} | {s:.3f} | {g_post.mean():.3f} | {g_cp1.mean():.3f} |")
            if mode == "pers":
                frozen[h] = (m, s, ho, oos)
            print(f"cut-in fit h={h} {mode}: held-out {ho:.4f} CP1 {oos:.4f} m {m:.3f} s {s:.3f}", flush=True)
    m, s, ho, oos = frozen[PRIMARY]
    credited = oos < CP1_CRIT and ho <= G1_GATED + COST
    L += ["", f"G.1 on file: post-onset 0.1027 (gated), CP1 0.0319; m_lat 0.149 m, s_l 0.990 m.", "",
          f"**Test 1 (pre-stated, primary horizon {PRIMARY:.0f} s, persistent gate): "
          + ("CREDITED" if credited else "NOT CREDITED")
          + f" (CP1 {oos:.4f} against < {CP1_CRIT}; post-onset {ho:.4f} against <= {G1_GATED + COST:.4f}).**", ""]
    return L, frozen, cl


# ---------------------------------------------------------------------------------
# tests 2 and 3: the first study
# ---------------------------------------------------------------------------------

def engaged_rows(p, margin):
    return p >= p.min() + margin


def consistency_lines(name, df, frozen):
    """Per reading and horizon: the number of engaged cells with the persistent gate open."""
    L = [f"### {name}: consistency (persistent gate >= 0.5 in every engaged cell)", "",
         "| reading | horizon [s] | open cells / all | engaged (margin 0.2) open / engaged | margin 0.1 | margin 0.3 | consistent (0.2) |",
         "|---|---|---|---|---|---|---|"]
    verdict = {}
    for rd in READINGS:
        for h in HORIZONS:
            sub = df[(df.reading == rd) & (df.h == h)]
            m, s = frozen[h][0], frozen[h][1]
            g = gate(sub.c_pers.to_numpy(float), m, s)
            p = sub.p.to_numpy(float)
            parts = []
            for mg in MARGINS:
                e = engaged_rows(p, mg)
                parts.append(f"{int(np.sum(g[e] >= 0.5))} / {int(e.sum())}")
            e2 = engaged_rows(p, MARGIN_PRIMARY)
            cons = bool(np.all(g[e2] >= 0.5))
            verdict[(rd, h)] = cons
            L.append(f"| {rd} | {h:.0f} | {int(np.sum(g >= 0.5))} / {len(g)} | {parts[1]} | {parts[0]} | {parts[2]} | "
                     f"{'yes' if cons else 'no'} |")
    return L + [""], verdict


def ltap(frozen):
    lc = ltap_cells(with_responses=True).sort_values(["speed_kph", "pet"]).reset_index(drop=True)
    rows = []
    t0 = time.time()
    for k, c in lc.iterrows():
        path = HS.KIN1 / f"{trace_name(float(c.pet), int(c.speed_kph))}_vehicle_states.csv"
        grid, tracks, meta = HS.scene_tracks(path)
        ego_id = max(meta, key=lambda vid: meta[vid]["yaw_span"])
        onc_id = [v for v in tracks if v != ego_id][0]
        ego, onc = body(grid, tracks, meta, ego_id), body(grid, tracks, meta, onc_id)
        t_start = max(float(grid[0]), T_DECISION_S - LEAD)
        times = eval_grid(t_start, T_DECISION_S, V_WINDOW_S1)
        ser = series_all(ego, onc, times, READINGS, V_WINDOW_S1)
        for rd in READINGS:
            for h in HORIZONS:
                vals = ser[(rd, h)]
                rows.append({"scenario": "ltap", "cell": f"{int(c.speed_kph)} km/h, PET {float(c.pet):.1f}",
                             "p": float(c.p), "n": float(c.n), "reading": rd, "h": h,
                             "c_inst": at_moment(times, vals, T_DECISION_S, "inst"),
                             "c_pers": at_moment(times, vals, T_DECISION_S, "pers"),
                             "t_open": float("nan"), "pet": float(c.pet), "d_onc": float(c.d_onc),
                             "t_sep": float(c.t_sep), "theta_dot": float(c.theta_dot)})
        print(f"left turn {k + 1}/18: {len(times)} moments, {time.time() - t0:.0f} s", flush=True)
    df = pd.DataFrame(rows)
    m, s = frozen[PRIMARY][0], frozen[PRIMARY][1]
    L = ["## Test 2 -- the left turn across path, first study (18 cells)", "",
         f"Constants frozen from the cut-in at each horizon; at {PRIMARY:.0f} s m = {m:.3f} m, s = {s:.3f} m. "
         "Decision moment 13.5 s; the shown window is the ten seconds before it.", "",
         "| speed | PET [s] | share | cK inst | cP inst | cKP pers | gK | gP | gKP (pers) |",
         "|---|---|---|---|---|---|---|---|---|"]
    prim = df[df.h == PRIMARY]
    for cell in prim.cell.unique():
        sub = prim[prim.cell == cell].set_index("reading")
        gk, gp, gkp = (gate(sub.loc["K", "c_pers"], m, s), gate(sub.loc["P", "c_pers"], m, s),
                       gate(sub.loc["KP", "c_pers"], m, s))
        L.append(f"| {cell.split(',')[0]} | {sub.loc['K', 'pet']:.1f} | {sub.loc['K', 'p']:.3f} | "
                 f"{sub.loc['K', 'c_inst']:.2f} | {sub.loc['P', 'c_inst']:.2f} | {sub.loc['KP', 'c_pers']:.2f} | "
                 f"{gk:.3f} | {gp:.3f} | {gkp:.3f} |")
    L.append("")
    cl, verdict = consistency_lines("Left turn", df, frozen)
    L += cl
    # cost against B.3.v2's distance rule
    ung, _, _ = LT.score(lc, "dist")
    x = -np.log(lc.d_onc.to_numpy(float))
    y, w = lc.p.to_numpy(float), lc.n.to_numpy(float)
    folds = lc.pet.to_numpy(float)
    L += ["### Cost of gating B.3.v2's distance rule (leave-one-PET-level-out)", "",
          "| reading | horizon [s] | ungated wRMSE | gated wRMSE | cost | within 0.01 |", "|---|---|---|---|---|---|"]
    cost_ok = {}
    for rd in READINGS:
        for h in HORIZONS:
            sub = df[(df.reading == rd) & (df.h == h)].set_index("cell")
            g = gate(sub.loc[[f"{int(r.speed_kph)} km/h, PET {float(r.pet):.1f}" for _, r in lc.iterrows()], "c_pers"]
                     .to_numpy(float), frozen[h][0], frozen[h][1])
            pred = np.full_like(y, np.nan)
            for f in np.unique(folds):
                tr, te = folds != f, folds == f
                th = HS.fit_1d_gated(x[tr], g[tr], y[tr], w[tr])
                pred[te] = HS.predict_1d(th, x[te], g[te])
            gs = T.wrmse(y, pred, w)
            cost_ok[(rd, h)] = gs <= ung + COST
            L.append(f"| {rd} | {h:.0f} | {ung:.4f} | {gs:.4f} | {gs - ung:+.4f} | {'yes' if cost_ok[(rd, h)] else 'no'} |")
    L.append("")
    return L, df, verdict, cost_ok


def overtake(frozen):
    trials = czb_data.random_overtake_trials()
    ov = (trials.groupby(["criticality", "timepoint"])
          .agg(p=("intervene", "mean"), n=("intervene", "size"), t_end=("t_end", "first")).reset_index())
    rows, opens = [], []
    t0 = time.time()
    for lab, path in RANDOM_OVERTAKE_TRACES.items():
        tr = load_overtake_trace(path)
        t_on = float(tr.t[tr.onset_idx])
        grid, tracks, meta = HS.scene_tracks(path)
        ego_id = max(meta, key=lambda vid: meta[vid]["width"])
        cyc_id = [v for v in tracks if v != ego_id][0]
        ego, cyc = body(grid, tracks, meta, ego_id), body(grid, tracks, meta, cyc_id)
        cells = ov[ov.criticality == lab].sort_values("timepoint")
        t_last = t_on + float(cells.t_end.max())
        t_start = max(float(grid[0]), t_on - LEAD)
        times = eval_grid(t_start, t_last, V_WINDOW_S1)
        ser = series_all(ego, cyc, times, READINGS, V_WINDOW_S1)
        for rd in READINGS:
            for h in HORIZONS:
                vals = ser[(rd, h)]
                g = gate(persistent(-vals) * -1.0, frozen[h][0], frozen[h][1])   # persistent min of c
                hit = np.flatnonzero(g >= 0.5)
                t_open = float(times[hit[0]] - t_on) if len(hit) else float("nan")
                opens.append({"clearance": lab, "reading": rd, "h": h, "t_open_rel_onset": t_open,
                              "t_first_eval_rel_onset": float(times[0] - t_on)})
                for _, c in cells.iterrows():
                    t_clip = t_on + float(c.t_end)
                    rows.append({"scenario": "overtake", "cell": f"{lab} {c.timepoint}", "p": float(c.p),
                                 "n": float(c.n), "reading": rd, "h": h,
                                 "c_inst": at_moment(times, vals, t_clip, "inst"),
                                 "c_pers": at_moment(times, vals, t_clip, "pers"), "t_open": t_open})
        print(f"overtake {lab}: {len(times)} moments, {time.time() - t0:.0f} s", flush=True)
    df, op = pd.DataFrame(rows), pd.DataFrame(opens)
    m, s = frozen[PRIMARY][0], frozen[PRIMARY][1]
    L = ["## Test 3 -- the cyclist overtake, first study (15 cells)", "",
         "When the persistent gate first reaches 0.5, relative to the ego's lateral onset (C1); the "
         "evaluation starts one velocity window after the shown window opens (first column).", "",
         "| clearance | first evaluated [s] | " + " | ".join(f"{rd} {h:.0f} s" for rd in READINGS for h in HORIZONS) + " |",
         "|---|---|" + "---|" * (len(READINGS) * len(HORIZONS))]
    for lab in RANDOM_OVERTAKE_TRACES:
        sub = op[op.clearance == lab].set_index(["reading", "h"])
        first = float(sub.t_first_eval_rel_onset.iloc[0])
        L.append(f"| {lab} | {first:+.1f} | " + " | ".join(
            (f"{sub.loc[(rd, h), 't_open_rel_onset']:+.1f}" if np.isfinite(sub.loc[(rd, h), 't_open_rel_onset']) else "never")
            for rd in READINGS for h in HORIZONS) + " |")
    L += ["", f"Per cell at the primary horizon (m = {m:.3f} m, s = {s:.3f} m):", "",
          "| cell | share | cK inst | cP inst | gK pers | gP pers | gKP pers |", "|---|---|---|---|---|---|---|"]
    prim = df[df.h == PRIMARY]
    for cell in prim.cell.unique():
        sub = prim[prim.cell == cell].set_index("reading")
        L.append(f"| {cell} | {sub.loc['K', 'p']:.3f} | {sub.loc['K', 'c_inst']:.2f} | {sub.loc['P', 'c_inst']:.2f} | "
                 f"{gate(sub.loc['K', 'c_pers'], m, s):.3f} | {gate(sub.loc['P', 'c_pers'], m, s):.3f} | "
                 f"{gate(sub.loc['KP', 'c_pers'], m, s):.3f} |")
    L.append("")
    cl, verdict = consistency_lines("Overtake", df, frozen)
    return L + cl, df, verdict


# ---------------------------------------------------------------------------------

def main() -> None:
    t0 = time.time()
    head = ["# Card PC.1 -- the projected-conflict gate: one construction for every scenario", "",
            "Generated by `replication/czb/pc1_projected_conflict.py`; construction, settings, tests and rules "
            "pre-stated in its docstring and in `docs/projected_conflict_gate_note.md`. Do not edit by hand.", "",
            f"Readings of the ego's path: K (constant velocity), P (recorded future), KP (union). Horizons "
            f"{', '.join(f'{h:.0f}' for h in HORIZONS)} s, primary {PRIMARY:.0f} s. Velocity windows "
            f"{V_WINDOW_S2} s (second study) and {V_WINDOW_S1} s (first study). Projection step {DT_PROJ} s, "
            f"evaluation step {EVAL_DT} s. The persistent gate is the model's; instantaneous values are reported.", ""]
    L1, frozen, cl = cutin()
    body_lines = L1
    if frozen is None:
        (OUT / "pc1_projected_conflict.md").write_text("\n".join(head + body_lines), encoding="utf-8")
        print("\n".join(head + body_lines))
        return
    m, s, ho, oos = frozen[PRIMARY]
    credited = oos < CP1_CRIT and ho <= G1_GATED + COST
    L2, df2, v2, cost2 = ltap(frozen)
    L3, df3, v3 = overtake(frozen)
    pd.concat([df2, df3]).to_csv(OUT / "pc1_gates.csv", index=False)
    body_lines += L2 + L3
    # adoption
    body_lines += ["## Adoption (pre-stated)", "",
                   "| reading | test 1 credited | left turn consistent | left-turn cost within 0.01 | overtake consistent | adopted at 3 s |",
                   "|---|---|---|---|---|---|"]
    adopted = None
    for rd in READINGS:
        ok = credited and v2[(rd, PRIMARY)] and cost2[(rd, PRIMARY)] and v3[(rd, PRIMARY)]
        if ok and adopted is None:
            adopted = rd
        body_lines.append(f"| {rd} | {'yes' if credited else 'no'} | {'yes' if v2[(rd, PRIMARY)] else 'no'} | "
                          f"{'yes' if cost2[(rd, PRIMARY)] else 'no'} | {'yes' if v3[(rd, PRIMARY)] else 'no'} | "
                          f"{'**yes**' if adopted == rd else 'no'} |")
    longer = [(rd, h) for rd in READINGS for h in HORIZONS if h != PRIMARY
              and v2[(rd, h)] and cost2[(rd, h)] and v3[(rd, h)]]
    body_lines += ["", (f"**Adopted at the primary horizon: {adopted}.**" if adopted else
                        "**No reading is credited and consistent at the primary horizon.**")
                   + (f" Consistent at longer horizons (test 1 credited there or not is in its table): "
                      + ", ".join(f"{rd} at {h:.0f} s" for rd, h in longer) + "." if longer else ""),
                   "", f"Runtime {(time.time() - t0) / 60:.1f} min."]
    (OUT / "pc1_projected_conflict.md").write_text("\n".join(head + body_lines), encoding="utf-8")
    print("\n".join(head + body_lines))


if __name__ == "__main__":
    main()
