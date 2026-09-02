"""Animations that explain the measurement concepts one at a time (build_concepts_talk.py).

    python presentation/talk/make_concept_animations.py

Five GIFs, every number from tracked data or a tracked output; captions inside the frames.

    concept_axis.gif        AXIS: two candidate criticality axes on one real cut-in stimulus
                            (study 2, LC_dv21_Tlc3p0_TTC04, and the 4 s lane change at the same
                            TTC): the field's comfort-zone deficit (with the project's lane-entry
                            gate) against the optical expansion rate. One steps, one ramps.
    concept_level.gif       LEVEL: study 1's 15 gate-open cells (P vs theta_dot, from
                            out/stage1_looming.md table 1), the fitted population response curve,
                            then 43 drivers' thresholds drawn one at a time from the fitted
                            population (mu, sigma_pop of the L-gated fit), the histogram, and the
                            50th / 80th percentile markers.
    concept_gate.gif        GATE: the lateral clearance, its projection 3 s ahead, and the gate
                            weight w rising from ~0.07 to 1 on the same stimulus; parameters
                            fixed from out/cutin2_gate.md.
    concept_heldout.gif     HOW WE TEST: leave-one-starting-TTC-out on the 288 study-2 cells,
                            fold by fold, predicted vs observed accumulating, the running error,
                            and the sampling-noise floor.
    concept_percentile.gif  THE DELIVERABLE: which percentile of drivers' levels, and what it
                            costs in seconds on the TTC4 and TTC6 stimuli (table 5 of
                            out/stage1_looming.md), with the level's own CI.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIGS = HERE / "figures"
CZB = REPO / "replication" / "czb"
OUT = CZB / "out"
sys.path.insert(0, str(CZB))
sys.path.insert(0, str(REPO / "src"))
import cutin2_two_axis as T                                                  # noqa: E402
import cutin2_field_vs_gap as R                                              # noqa: E402
from comfortzone.cutin import cutin_params, cutin_predictors, load_cutin_trace  # noqa: E402

PURPLE, TEAL, PINK, BLUE, INK, GREY, BEIGE, AMBER = ("#472CBE", "#1B8F7A", "#B03E82", "#36B7F6",
                                                     "#222222", "#6A6A6A", "#F0EDE6", "#C47A14")
KPH = 1000.0 / 3600.0
STUDY2 = REPO / "external/01_studies/01_Studies/02_Cut-in"
FPS = 8
W_CAR = 1.882


def caption(fig, text, y=0.04, size=14.5):
    return fig.text(0.5, y, text, ha="center", va="center", fontsize=size, color=INK, wrap=True,
                    bbox=dict(boxstyle="round,pad=0.5", fc=BEIGE, ec="none"))


def save(fig, frames, name, fps=FPS, durations=None):
    anim = FuncAnimation(fig, frames["fn"], frames=frames["n"], interval=1000 / fps, blit=False)
    out = FIGS / name
    anim.save(str(out), writer=PillowWriter(fps=fps))
    plt.close(fig)
    if durations is not None:
        from PIL import Image
        im = Image.open(out)
        fr, dur = [], []
        try:
            while True:
                fr.append(im.copy()); dur.append(durations(len(fr) - 1)); im.seek(im.tell() + 1)
        except EOFError:
            pass
        fr[0].save(out, save_all=True, append_images=fr[1:], duration=dur, loop=0, disposal=2)
    print("wrote", out)
    return out


def onset_from_stamps(trace):
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    mine = cells[cells.video.str.startswith(trace + "_CP1")]
    e1 = float(mine.video.iloc[0].split("_E")[1].replace(".mp4", "").replace("p", "."))
    return e1 + 0.066


def trace_signals(trace):
    tr = load_cutin_trace(STUDY2 / "02_Kinematics" / f"{trace}_vehicle_states.csv")
    f = cutin_predictors(tr, cutin_params(tr))
    W = float(tr.tar_wid)
    gap, vrel = f.gap_m.to_numpy(), f.v_rel.to_numpy()
    thd = np.degrees(W * np.maximum(vrel, 0) / (gap ** 2 + W ** 2 / 4))
    l0 = np.abs(f.y_rel.to_numpy()) - W        # both cars 1.882 m wide (cutin2_gate.md)
    return f.t.to_numpy(), f.deficit.to_numpy(), thd, l0, gap, onset_from_stamps(trace)


# ---------------------------------------------------------------------------------
# 1  AXIS: deficit versus looming on one stimulus (two lane-change durations)
# ---------------------------------------------------------------------------------
def make_axis_gif():
    A = trace_signals("LC_dv21_Tlc2p0_TTC02")
    B = trace_signals("LC_dv21_Tlc4p0_TTC02")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12.8, 7.2), dpi=100, sharex=True)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.2, hspace=0.25)
    fig.suptitle("The AXIS: the number read off the scene. Two candidates, two stimuli (DV 21 km/h, TTC 2 s; 2 s and 4 s lane changes)",
                 fontsize=14.5, color=INK, y=0.96)
    t0, t1 = -2.5, 1.3          # the clips end at onset + 1.13 s (CP5); after ~2 s the TTC 2 s stimuli reach the ego
    for ax, lab in ((ax1, "field deficit (with lane-entry gate)"), (ax2, "expansion rate [deg/s]")):
        ax.set_xlim(t0, t1); ax.axvspan(t0, 0, color="#EEEEEE", zorder=0)
        ax.set_ylabel(lab, fontsize=11.5); ax.spines[["top", "right"]].set_visible(False)
    ax2.set_xlabel("time from lane-change onset [s]", fontsize=12)
    ax1.set_ylim(0, 1.15 * max(A[1][(A[0] - A[5] > t0) & (A[0] - A[5] < t1)].max(),
                               B[1][(B[0] - B[5] > t0) & (B[0] - B[5] < t1)].max()))
    ax2.set_ylim(0, 1.15 * max(A[2][(A[0] - A[5] > t0) & (A[0] - A[5] < t1)].max(),
                               B[2][(B[0] - B[5] > t0) & (B[0] - B[5] < t1)].max()))
    lines = {}
    for key, sig, col, ls, name in (("A1", A, PINK, "-", "2 s lane change"), ("B1", B, PINK, "--", "4 s lane change")):
        lines[key], = ax1.plot([], [], color=col, lw=2.6, ls=ls, label=name)
    for key, sig, col, ls, name in (("A2", A, TEAL, "-", "2 s lane change"), ("B2", B, TEAL, "--", "4 s lane change")):
        lines[key], = ax2.plot([], [], color=col, lw=2.6, ls=ls, label=name)
    ax1.legend(loc="upper left", fontsize=11, frameon=False); ax2.legend(loc="upper left", fontsize=11, frameon=False)
    ax1.text(t0 / 2, ax1.get_ylim()[1] * 0.9, "before onset", ha="center", color=GREY, fontsize=11)
    cap = caption(fig, "")
    grid = np.arange(t0, t1, 0.1)

    def fn(i):
        tt = grid[min(i, len(grid) - 1)]
        for key, sig in (("A1", A), ("B1", B), ("A2", A), ("B2", B)):
            t_rel = sig[0] - sig[5]
            m = (t_rel >= t0) & (t_rel <= tt)
            y = sig[1] if key.endswith("1") else sig[2]
            lines[key].set_data(t_rel[m], y[m])
        if tt < 0:
            cap.set_text("Before the lane change both axes are quiet. An axis is just a number that should rise as the situation gets worse")
        elif tt < 1.0:
            cap.set_text("The field's deficit switches on as a step and treats the slow lane change very differently from the fast one (its gate waits for predicted overlap); the jitter is simulator speed dither")
        else:
            cap.set_text("The expansion rate ramps smoothly and is nearly the same for both lane changes, which is how participants responded: flat across lane-change speed (gate R.2, card EL.1)")
        return list(lines.values())

    return save(fig, {"fn": fn, "n": len(grid) + 2 * FPS}, "concept_axis.gif")


# ---------------------------------------------------------------------------------
# 2  LEVEL: cells, the population curve, drivers' thresholds, percentiles
# ---------------------------------------------------------------------------------
def parse_stage1():
    txt = (OUT / "stage1_looming.md").read_text(encoding="utf-8")
    rows = re.findall(r"\| (TTC\d) \| (C\d) \| (\d+) \| ([0-9.]+) \| ([0-9.]+) \| ([-0-9.]+) \| ([0-9.]+) \|", txt)
    cells = pd.DataFrame(rows, columns=["crit", "tp", "n", "p", "thd", "x", "w"]).astype(
        {"n": int, "p": float, "thd": float, "x": float, "w": float})
    g = re.search(r"\| L-gated \| `log\(theta_dot\)` \| gated \| ([-0-9.]+) \(SE [0-9.]+\) \| ([0-9.]+) \(SE [0-9.]+\) \| ([0-9.]+) \|", txt)
    mu, sig_pop, sig_resp = float(g.group(1)), float(g.group(2)), float(g.group(3))
    pct = {int(m.group(1)): float(m.group(2)) for m in re.finditer(r"\| L-gated \| (\d+)th \| [-0-9.]+ \| \[[^\]]+\] \| ([0-9.]+) \|", txt)}
    return cells, mu, sig_pop, sig_resp, pct


def make_level_gif():
    cells, mu, sig_pop, sig_resp, pct = parse_stage1()
    open_ = cells[cells.tp != "C1"]
    rng = np.random.default_rng(0)
    n_drv = 43
    levels = mu + sig_pop * rng.standard_normal(n_drv)
    xs = np.linspace(-5.2, -1.6, 300)
    pop_curve = np.mean([norm.cdf((xs - c) / sig_resp) for c in (mu + sig_pop * rng.standard_normal(2000))], axis=0)
    fig, (ax, axh) = plt.subplots(2, 1, figsize=(12.8, 7.2), dpi=100, sharex=True, height_ratios=[2.2, 1])
    fig.subplots_adjust(left=0.09, right=0.97, top=0.88, bottom=0.2, hspace=0.12)
    fig.suptitle("The LEVEL: where each driver says \"now\" on the axis, and the population of levels (study 1, 43 drivers)",
                 fontsize=14.5, color=INK, y=0.96)
    ax.set_xlim(xs[0], xs[-1]); ax.set_ylim(0, 1.02)
    ax.set_ylabel("P(intervene)", fontsize=12); ax.spines[["top", "right"]].set_visible(False)
    ticks = [0.01, 0.02, 0.05, 0.1, 0.2]
    axh.set_xticks(np.log(ticks)); axh.set_xticklabels([f"{np.degrees(v):.1f}°/s" for v in ticks], fontsize=11)
    axh.set_xlabel("optical expansion rate (log scale)", fontsize=12)
    axh.set_ylabel("drivers", fontsize=12); axh.spines[["top", "right"]].set_visible(False)
    axh.set_ylim(0, 14)
    pts, = ax.plot([], [], "o", color=PURPLE, ms=9, alpha=0.85)
    curve, = ax.plot([], [], color=INK, lw=2.4)
    ticks_art = [ax.plot([], [], color=TEAL, lw=1.2, alpha=0.7)[0] for _ in range(n_drv)]
    bars = axh.bar(np.linspace(xs[0], xs[-1], 25), np.zeros(25), width=(xs[-1] - xs[0]) / 25 * 0.9, color=TEAL, alpha=0.8)
    pct_lines = {}
    for q, col in ((50, PURPLE), (80, PINK)):
        pct_lines[q] = (ax.axvline(np.log(pct[q]), color=col, lw=2.2, ls="--"),
                        ax.text(np.log(pct[q]) + 0.03, 0.5 if q == 50 else 0.8, "", color=col, fontsize=12, fontweight="bold"))
        pct_lines[q][0].set_visible(False)
    cap = caption(fig, "")
    n_cells = len(open_)
    phase1, phase2, phase3 = n_cells, n_cells + 2 * FPS, n_cells + 2 * FPS + n_drv
    n_frames = phase3 + 3 * FPS
    edges = np.linspace(xs[0], xs[-1], 26)

    def fn(i):
        k = min(i + 1, n_cells)
        pts.set_data(open_.x.to_numpy()[:k], open_.p.to_numpy()[:k])
        if i >= phase1:
            curve.set_data(xs, pop_curve)
        if i >= phase2:
            m = min(i - phase2 + 1, n_drv)
            for j in range(n_drv):
                if j < m:
                    ticks_art[j].set_data([levels[j], levels[j]], [0, 0.5])
            h, _ = np.histogram(levels[:m], bins=edges)
            for b, v in zip(bars, h):
                b.set_height(v)
        if i >= phase3:
            for q, (ln, tx) in pct_lines.items():
                ln.set_visible(True)
                tx.set_text(f"{q}th percentile: {np.degrees(pct[q]):.1f}°/s")
        if i < phase1:
            cap.set_text("Each dot is one design cell with the gate open: the share of drivers who said \"I would intervene\" against how fast the car was growing")
        elif i < phase2:
            cap.set_text("The population response curve: a cumulative normal on the log axis, averaged over drivers (the stage-1 fit, out/stage1_looming.md)")
        elif i < phase3:
            cap.set_text("Behind the curve, each driver has one threshold. The fit estimates their spread: median 1.8°/s, spread 0.87 log units")
        else:
            cap.set_text("The deliverable is a percentile of this distribution: the 80th is the growth rate at which 80% of drivers would already have acted")
        return [pts, curve]

    return save(fig, {"fn": fn, "n": n_frames}, "concept_level.gif")


# ---------------------------------------------------------------------------------
# 3  GATE: clearance, projection, weight
# ---------------------------------------------------------------------------------
def make_gate_gif():
    txt = (OUT / "cutin2_gate.md").read_text(encoding="utf-8")
    m_lat = float(re.search(r"\| m_lat \[m\] \| - \| ([0-9.]+) \|", txt).group(1))
    s_l = float(re.search(r"\| s_l \[m\] \| - \| ([0-9.]+) \|", txt).group(1))
    t, deficit, thd, l0, gap, t_on = trace_signals("LC_dv21_Tlc3p0_TTC04")
    dt = float(np.median(np.diff(t)))
    k = max(int(round(0.3 / dt)), 1)
    ldot = np.concatenate([np.zeros(k), (l0[k:] - l0[:-k]) / (k * dt)])
    w = norm.cdf((m_lat - l0 - ldot * 3.0) / s_l)
    t0, t1 = t_on - 2.5, t_on + 2.3
    idx = np.where((t >= t0) & (t <= t1))[0][::3]
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.2], left=0.09, right=0.97, top=0.88, bottom=0.2, hspace=0.35)
    ax_road = fig.add_subplot(gs[0]); ax_w = fig.add_subplot(gs[1])
    fig.suptitle("The GATE: will this vehicle become my problem? Clearance now, clearance 3 s ahead, and the weight w",
                 fontsize=14.5, color=INK, y=0.96)
    ax_road.set_xlim(-8, 45); ax_road.set_ylim(-6, 6); ax_road.set_aspect("equal"); ax_road.axis("off")
    for yy in (-5.55, -1.85, 1.85, 5.55):
        ax_road.plot([-8, 45], [yy, yy], color="#BBBBBB", lw=1.2, ls="--" if abs(yy) < 2 else "-")
    ax_road.add_patch(Rectangle((-4.6, -0.9), 4.6, 1.8, fc=PURPLE, ec="none"))
    car = Rectangle((0, 0), 4.6, W_CAR, fc=PINK, ec="none"); ghost = Rectangle((0, 0), 4.6, W_CAR, fc="none", ec=PINK, ls="--", lw=1.5)
    ax_road.add_patch(car); ax_road.add_patch(ghost)
    lab = ax_road.text(0, -4.9, "", fontsize=11, color=INK)
    ax_w.set_xlim(t0 - t_on, t1 - t_on); ax_w.set_ylim(0, 1.05)
    ax_w.set_xlabel("time from lane-change onset [s]", fontsize=12); ax_w.set_ylabel("gate weight w", fontsize=12)
    ax_w.axvspan(t0 - t_on, 0, color="#EEEEEE", zorder=0); ax_w.spines[["top", "right"]].set_visible(False)
    wl, = ax_w.plot([], [], color=BLUE, lw=3); wd, = ax_w.plot([], [], "o", color=BLUE, ms=9)
    ax_w.text(t1 - t_on - 0.05, 0.55, f"w = Φ((m_lat − clearance − 3 s × closing rate) / s_l),  m_lat {m_lat:.2f} m, s_l {s_l:.2f} m",
              ha="right", fontsize=10.5, color=GREY)
    cap = caption(fig, "")
    tr = load_cutin_trace(STUDY2 / "02_Kinematics" / "LC_dv21_Tlc3p0_TTC04_vehicle_states.csv")

    def fn(i):
        j = idx[i]
        y_now = float(tr.y_tar[j]); y_proj = y_now + float(np.gradient(tr.y_tar, tr.t)[j]) * 3.0
        car.set_xy((gap[j], y_now - W_CAR / 2)); ghost.set_xy((gap[j], y_proj - W_CAR / 2))
        lab.set_x(min(max(gap[j] - 4, 0), 30)); lab.set_text(f"clearance now {max(l0[j], 0):.2f} m, in 3 s {max(l0[j] + ldot[j] * 3, 0):.2f} m")
        tt = t[idx[: i + 1]] - t_on
        wl.set_data(tt, w[idx[: i + 1]]); wd.set_data([tt[-1]], [w[j]])
        if tt[-1] < 0:
            cap.set_text("Before onset the car is not closing sideways: projected 3 s ahead it is still clear, and w stays near 0.07")
        elif w[j] < 0.9:
            cap.set_text("Once it starts moving over, the projection (dashed) reaches into the lane and w rises: the gap starts to count")
        else:
            cap.set_text("Fully committed: w ≈ 1 and the response depends on the axis alone. Fitted on post-onset cells, this gate predicted the pre-onset cells out of sample (card G.1)")
        return [wl, wd]

    return save(fig, {"fn": fn, "n": len(idx)}, "concept_gate.gif")


# ---------------------------------------------------------------------------------
# 4  HOW WE TEST: leave-one-starting-TTC-out and the noise floor
# ---------------------------------------------------------------------------------
def make_heldout_gif():
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    c = cells[cells.cp != "CP1"].reset_index(drop=True)
    y, w = c.p.to_numpy(float), c.n.to_numpy(float)
    gap, dv = c.distance.to_numpy(float), c.dv_kph.to_numpy(float) * KPH
    x = np.log(W_CAR * dv / (gap ** 2 + W_CAR ** 2 / 4))
    folds = c.ttc_start.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))
    pred = np.full_like(y, np.nan)
    order = sorted(np.unique(folds))
    for f in order:
        tr, te = folds != f, folds == f
        th = T.fit_reg(x[tr], y[tr], w[tr])
        pred[te] = R.predict(th, x[te], +1.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 7.2), dpi=100, width_ratios=[1.3, 1])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.2, wspace=0.3)
    fig.suptitle("HOW WE TEST: fit on five starting-TTC groups, predict the sixth, repeat; then compare with the noise floor",
                 fontsize=14.5, color=INK, y=0.96)
    ax1.set_xlim(-6, -0.5); ax1.set_ylim(0, 1.02); ax1.set_xlabel("log optical expansion rate", fontsize=12); ax1.set_ylabel("P(intervene)", fontsize=12)
    ax1.spines[["top", "right"]].set_visible(False)
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1); ax2.set_xlabel("predicted (never seen in fitting)", fontsize=12); ax2.set_ylabel("observed", fontsize=12)
    ax2.plot([0, 1], [0, 1], color="#CCCCCC", lw=1); ax2.spines[["top", "right"]].set_visible(False)
    train_pts, = ax1.plot([], [], "o", color="#BBBBBB", ms=6)
    test_pts, = ax1.plot([], [], "o", color=PINK, ms=9)
    curve, = ax1.plot([], [], color=INK, lw=2)
    sc_done, = ax2.plot([], [], "o", color=PURPLE, ms=6, alpha=0.7)
    sc_now, = ax2.plot([], [], "o", color=PINK, ms=9)
    txt = ax2.text(0.04, 0.93, "", fontsize=12.5, color=INK)
    cap = caption(fig, "")
    hold = 2 * FPS
    n_frames = hold * (len(order) + 1)

    def fn(i):
        k = min(i // hold, len(order))
        if k < len(order):
            f = order[k]; tr, te = folds != f, folds == f
            th = T.fit_reg(x[tr], y[tr], w[tr])
            xs = np.linspace(-6, -0.5, 200)
            train_pts.set_data(x[tr], y[tr]); test_pts.set_data(x[te], y[te]); curve.set_data(xs, R.predict(th, xs, +1.0))
            done = np.isin(folds, order[:k]); sc_done.set_data(pred[done], y[done]); sc_now.set_data(pred[te], y[te])
            m = np.isin(folds, order[: k + 1])
            err = T.wrmse(y[m], pred[m], w[m])
            txt.set_text(f"held out so far: {int(m.sum())} cells, wRMSE {err:.3f}")
            cap.set_text(f"Fold {k + 1} of 6: the cells with starting TTC {f:.0f} s (pink) are held out; the model is fitted on the grey ones and scored on the pink ones")
        else:
            th = T.fit_reg(x, y, w)
            xs = np.linspace(-6, -0.5, 200)
            train_pts.set_data(x, y); test_pts.set_data([], []); curve.set_data(xs, R.predict(th, xs, +1.0))
            sc_done.set_data(pred, y); sc_now.set_data([], [])
            err = T.wrmse(y, pred, w)
            txt.set_text(f"all 288 cells held out: wRMSE {err:.3f}\nsampling-noise floor {noise:.3f}")
            cap.set_text("The floor is the error a perfect model would still show, because each cell is a noisy average of 12-24 people. A model at the floor cannot be improved on this data")
        return [train_pts, test_pts, curve, sc_done, sc_now]

    return save(fig, {"fn": fn, "n": n_frames}, "concept_heldout.gif")


# ---------------------------------------------------------------------------------
# 5  THE DELIVERABLE: percentile -> trigger onset, with the CI
# ---------------------------------------------------------------------------------
def make_percentile_gif():
    txt = (OUT / "stage1_looming.md").read_text(encoding="utf-8")
    rows = re.findall(r"\| (\d+)th \| ([0-9.]+) \| ([-0-9.]+|nan) \| ([-0-9.]+|nan) \| ([-0-9.]+|nan) \| ([0-9.]+|nan) \| ([0-9.]+|nan) \| ([0-9.]+|nan) \|", txt)
    tab = pd.DataFrame(rows, columns=["pct", "level", "on4", "on6", "on8", "ci4", "ci6", "ci8"]).astype(float)
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.86, bottom=0.22)
    fig.suptitle("THE DELIVERABLE: choose a percentile of drivers' levels; here is what it costs in seconds (study 1 stimuli)",
                 fontsize=14.5, color=INK, y=0.96)
    ax.set_xlim(48, 97); ax.set_ylim(-1.2, 3.0)
    ax.set_xlabel("percentile of drivers' levels used as the trigger", fontsize=12)
    ax.set_ylabel("implied trigger onset [s after lane-change onset]", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    l4, = ax.plot([], [], "-o", color=PURPLE, lw=2.5, ms=7, label="TTC 4 s stimulus")
    l6, = ax.plot([], [], "-o", color=TEAL, lw=2.5, ms=7, label="TTC 6 s stimulus")
    band4 = ax.fill_between([], [], [], color=PURPLE, alpha=0.15)
    ax.legend(loc="upper left", fontsize=12, frameon=False)
    note = ax.text(96, 2.8, "", ha="right", fontsize=12, color=INK)
    cap = caption(fig, "")
    n = len(tab); hold = FPS

    def fn(i):
        k = min(i // hold + 1, n)
        d = tab.iloc[:k]
        l4.set_data(d.pct, d.on4); l6.set_data(d.pct, d.on6)
        nonlocal band4
        band4.remove()
        band4 = ax.fill_between(d.pct, d.on4 - d.ci4 / 2, d.on4 + d.ci4 / 2, color=PURPLE, alpha=0.15)
        p = int(d.pct.iloc[-1])
        note.set_text(f"{p}th percentile: level {np.degrees(d.level.iloc[-1]):.1f}°/s; TTC8 stimulus never crosses")
        if k < n:
            cap.set_text("Each 5-point step of the percentile moves the trigger by about 0.24 s; the shaded band is the level's own estimation uncertainty (about 0.52 s)")
        else:
            cap.set_text("On this axis the estimate's uncertainty, not the percentile choice, is the bottleneck: more drivers would help more than settling the percentile")
        return [l4, l6]

    return save(fig, {"fn": fn, "n": hold * n + 3 * FPS}, "concept_percentile.gif")


if __name__ == "__main__":
    make_axis_gif()
    make_level_gif()
    make_gate_gif()
    make_heldout_gif()
    make_percentile_gif()
