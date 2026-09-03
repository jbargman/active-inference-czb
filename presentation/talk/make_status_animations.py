"""Animations for the 10-15 minute "where we are now" deck (build_status_talk.py).

    python presentation/talk/make_status_animations.py

Three animated GIFs, every number read from tracked data or a tracked output:

    status_model.gif       the model we have, on one real cut-in stimulus (study 2, trace
                           LC_dv21_Tlc3p0_TTC04): the gate (closed until the lane change
                           starts), the axis (optical expansion rate, which card EL.1's
                           equal-weight rule is), and the level (three quantiles of the
                           population response curve fitted to the 288 post-onset cells)
    status_scoreboard.gif  the held-out scoreboard of gate R.2 and card EL.1, one bar at a
                           time, parsed from out/cutin2_field_vs_gap.md and
                           out/cutin2_two_axis.md
    status_trait.gif       43 drivers' criticality-adjusted intervention propensity across
                           the four Random-design scenarios, drawn one driver at a time;
                           the propensity is computed exactly as in
                           replication/czb/cross_scenario_consistency.py (its cell_key and
                           driver_propensity, reproduced here so that importing does not
                           re-run that script)

Each GIF carries its own caption text inside the frames, so the slide needs no text.
PowerPoint plays GIFs in slideshow mode.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIGS = HERE / "figures"
FIGS.mkdir(parents=True, exist_ok=True)
CZB = REPO / "replication" / "czb"
OUT = CZB / "out"
sys.path.insert(0, str(CZB))
sys.path.insert(0, str(REPO / "src"))

import cutin2_two_axis as T                      # noqa: E402  (fit_reg; imports R and cutin)
from comfortzone.cutin import cutin_params, cutin_predictors, load_cutin_trace  # noqa: E402
from comfortzone.czb_data import load_joint       # noqa: E402

PURPLE, TEAL, PINK, BLUE, INK, GREY, BEIGE = ("#472CBE", "#1B8F7A", "#B03E82", "#36B7F6",
                                              "#222222", "#6A6A6A", "#F0EDE6")
KPH = 1000.0 / 3600.0
STUDY2 = REPO / "external/01_studies/01_Studies/02_Cut-in"
TRACE = "LC_dv21_Tlc3p0_TTC04"
FPS = 8


def caption(fig, text, y=0.035, size=15, color=INK):
    return fig.text(0.5, y, text, ha="center", va="center", fontsize=size, color=color,
                    bbox=dict(boxstyle="round,pad=0.5", fc=BEIGE, ec="none"))


# ---------------------------------------------------------------------------------
# 1  the model on one stimulus
# ---------------------------------------------------------------------------------
def level_lines(W: float):
    """Fit the 1D log(theta_dot) threshold on the 288 post-onset cells (registered fitter)
    and return theta_dot at the 25th, 50th and 75th percentiles of the response curve."""
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    cells = cells[cells.cp != "CP1"].reset_index(drop=True)
    gap = cells.distance.to_numpy(float)
    dv = cells.dv_kph.to_numpy(float) * KPH
    thd = W * dv / (gap ** 2 + W ** 2 / 4)
    x = np.log(thd)
    th = T.fit_reg(x, cells.p.to_numpy(float), cells.n.to_numpy(float))
    b, c, ls = th
    sig = np.exp(ls)
    qs = {"lenient": 0.75, "median": 0.5, "strict": 0.25}
    return {k: float(np.exp(c + sig * norm.ppf(q))) for k, q in qs.items()}, thd, cells.p.to_numpy(float)


def make_model_gif() -> Path:
    tr = load_cutin_trace(STUDY2 / "02_Kinematics" / f"{TRACE}_vehicle_states.csv")
    f = cutin_predictors(tr, cutin_params(tr))
    W = float(tr.tar_wid)
    t = f.t.to_numpy()
    gap = f.gap_m.to_numpy()
    vrel = f.v_rel.to_numpy()
    theta = 2 * np.arctan(W / (2 * np.maximum(gap, 0.5)))
    thd = np.degrees(W * np.maximum(vrel, 0) / (gap ** 2 + W ** 2 / 4))
    # Onset from the video filename stamps: the loader's 0.03 m detector fires at t ~ 1.7 s on
    # these drifting traces (cutin2_field_vs_gap docstring); the CP1 clip ends 0.066 s before
    # onset and CP2..CP5 at +0.234, +0.534, +0.834, +1.134 s (external k1_validation; the
    # study's 0.3 s cut-point step). So onset = e_t(CP1) + 0.066.
    cells_all = pd.read_csv(OUT / 'cutin2_cells.csv')
    mine = cells_all[cells_all.video.str.startswith(TRACE + '_CP')].copy()
    mine['cpn'] = mine.cp.str[2].astype(int)
    e1 = float(mine.loc[mine.cpn == 1, 'video'].iloc[0].split('_E')[1].replace('.mp4', '').replace('p', '.'))
    t_on = e1 + 0.066
    cp_times = [e1 + 0.3 * (k - 1) for k in range(1, 6)]
    levels, cell_thd, cell_p = level_lines(W)
    levels = {k: float(np.degrees(v)) for k, v in levels.items()}

    t0, t1 = t_on - 2.5, t_on + 2.3
    sel = (t >= t0) & (t <= t1)
    idx = np.where(sel)[0][::3]                 # 30 Hz -> 10 Hz

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.25], width_ratios=[1.35, 1.0],
                          left=0.09, right=0.98, top=0.90, bottom=0.14, hspace=0.45, wspace=0.25)
    ax_road = fig.add_subplot(gs[0, 0])
    ax_eye = fig.add_subplot(gs[0, 1])
    ax_sig = fig.add_subplot(gs[1, :])
    fig.suptitle("The model we have, on one real cut-in (study 2, DV 21 km/h, 3 s lane change, TTC 4 s)",
                 fontsize=15, color=INK, x=0.5, y=0.965)

    # road panel
    ax_road.set_xlim(-8, 45); ax_road.set_ylim(-6.0, 6.0)
    ax_road.set_aspect("equal"); ax_road.axis("off")
    for yy in (-5.55, -1.85, 1.85, 5.55):
        ax_road.plot([-8, 45], [yy, yy], color="#BBBBBB", lw=1.2, ls="--" if abs(yy) < 2 else "-")
    ego = Rectangle((-4.6, -0.9), 4.6, 1.8, fc=PURPLE, ec="none")
    tar = Rectangle((0, 0), 4.6, W, fc=PINK, ec="none")
    ax_road.add_patch(ego); ax_road.add_patch(tar)
    ax_road.text(-2.3, -1.6, "you", ha="center", fontsize=11, color=PURPLE)
    lab_gap = ax_road.text(0, -4.9, "", fontsize=11, color=INK)
    ax_road.set_title("top view", fontsize=12, color=GREY, loc="left")

    # windscreen panel
    ax_eye.set_xlim(-1, 1); ax_eye.set_ylim(-0.6, 0.9); ax_eye.axis("off")
    ax_eye.add_patch(Rectangle((-1, -0.6), 2, 1.5, fc="#F7F7F7", ec="#CCCCCC"))
    ax_eye.plot([-1, 1], [0.05, 0.05], color="#CCCCCC", lw=1)
    eye_car = Rectangle((0, 0), 0.1, 0.1, fc=PINK, ec="none")
    ax_eye.add_patch(eye_car)
    ax_eye.set_title("through the windscreen", fontsize=12, color=GREY, loc="left")
    lab_eye = ax_eye.text(0, -0.5, "", ha="center", fontsize=11, color=INK)

    # signal panel
    ax_sig.set_xlim(t0 - t_on, t1 - t_on)
    ymax = float(np.nanmax(thd[sel])) * 1.15
    ax_sig.set_ylim(0, ymax)
    ax_sig.set_xlabel("time from lane-change onset [s]", fontsize=12)
    ax_sig.set_ylabel("how fast the car grows  [degrees/s]", fontsize=12)
    for k_cp, tc in enumerate(cp_times, 1):
        ax_sig.axvline(tc - t_on, color='#CCCCCC', lw=1)
        ax_sig.text(tc - t_on, 1.01, f'CP{k_cp}', ha='center', va='bottom', fontsize=9, color=GREY, transform=ax_sig.get_xaxis_transform())
    ax_sig.axvspan(t0 - t_on, 0, color="#EEEEEE", zorder=0)
    ax_sig.text((t0 - t_on) / 2, ymax * 0.92, "gate closed", ha="center", fontsize=12, color=GREY)
    ax_sig.text(0.75, ymax * 0.92, "gate open: the axis counts", ha="center", fontsize=12, color=INK)
    for k, v in levels.items():
        if v < ymax:
            ax_sig.axhline(v, color=TEAL, lw=1.4, ls=":")
            ax_sig.text(t1 - t_on - 0.05, v, f"{k} driver's level", ha="right", va="bottom",
                        fontsize=10.5, color=TEAL)
    line, = ax_sig.plot([], [], color=PURPLE, lw=3)
    dot, = ax_sig.plot([], [], "o", color=PURPLE, ms=9)
    cap = caption(fig, "")

    def frame(i):
        k = idx[i]
        tt = t[k] - t_on
        g = gap[k]
        tar.set_xy((g, float(tr.y_tar[k]) - W / 2))
        lab_gap.set_x(min(max(g - 2, 0), 30)); lab_gap.set_text(f"gap {g:.1f} m")
        s = 0.9 * float(theta[k]) / float(theta[idx[-1]])   # apparent width, normalized to the last frame
        h = s * 0.55
        eye_car.set_width(s); eye_car.set_height(h)
        eye_car.set_xy((-s / 2 + 0.55 * s * (float(tr.y_tar[k]) / 3.5), 0.05))
        lab_eye.set_text(f"apparent width {np.degrees(theta[k]):.1f}°, growing at {thd[k]:.2f}°/s")
        tt_all = t[idx[: i + 1]] - t_on
        line.set_data(tt_all, thd[idx[: i + 1]])
        dot.set_data([tt], [thd[k]])
        if tt < 0:
            cap.set_text("GATE closed: the car is in its own lane, so nothing counts yet")
        elif thd[k] < levels["strict"]:
            cap.set_text("GATE open. The AXIS is how fast the car grows in your eyes (gap × TTC, card EL.1)")
        elif thd[k] < levels["median"]:
            cap.set_text("LEVEL: a strict driver's boundary is crossed now; the median driver waits")
        elif thd[k] < levels["lenient"]:
            cap.set_text("LEVEL: the median driver's boundary is crossed; each driver carries one level")
        else:
            cap.set_text("Nearly every driver would have acted by now")
        return line, dot, cap

    anim = FuncAnimation(fig, frame, frames=len(idx), interval=1000 / FPS, blit=False)
    out = FIGS / "status_model.gif"
    anim.save(str(out), writer=PillowWriter(fps=FPS))
    # The concepts deck embeds this one as a movie (Jonas, 2026-09-03: a GIF gives no scrub
    # bar and restarts on pause), so write the .mp4 and a poster of the final frame beside
    # it. The status deck still uses the .gif and is unaffected.
    anim.save(str(out.with_suffix(".mp4")),
              writer=FFMpegWriter(fps=FPS, codec="libx264", bitrate=-1,
                                  extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]))
    # FIRST-frame poster, taken from the GIF: re-calling frame(0) would leave every artist
    # the frame function never clears in its final state (see make_concept_animations.save).
    with Image.open(out) as im:
        im.seek(0)
        im.convert("RGB").save(out.with_suffix(".png"))
    plt.close(fig)
    print("wrote", out, "levels (deg/s):", {k: round(v, 4) for k, v in levels.items()}, "W =", W)
    return out


# ---------------------------------------------------------------------------------
# 2  the scoreboard
# ---------------------------------------------------------------------------------
def scoreboard_numbers():
    r2 = (OUT / "cutin2_field_vs_gap.md").read_text(encoding="utf-8")
    prim = r2.split("## 1 Primary comparison")[1].split("### Folds: leave-one-video-out")[0]
    best = dict(re.findall(r"(field|gap|ttc|areq) ([0-9.]+)", prim.split("Best-scale scores:")[1].split(".\n")[0]))
    chance = float(re.search(r"\| chance \(train mean\) \| - \| ([0-9.]+) \|", prim).group(1))
    noise = float(re.search(r"\| sampling-noise floor \| - \| ([0-9.]+) \|", prim).group(1))
    el1 = (OUT / "cutin2_two_axis.md").read_text(encoding="utf-8")
    lin = float(re.search(r"\| \(c\) linear 2D rule[^|]*\| \d+ \| ([0-9.]+) \|", el1).group(1))
    return [("active-inference preference field", float(best["field"]), PINK),
            ("chance (predict the mean)", chance, GREY),
            ("required deceleration", float(best["areq"]), PINK),
            ("time to collision", float(best["ttc"]), BLUE),
            ("gap", float(best["gap"]), BLUE),
            ("gap × TTC  (= optical expansion rate)", lin, TEAL)], noise


def make_scoreboard_gif() -> Path:
    rows, noise = scoreboard_numbers()
    hold = 2 * FPS
    n_frames = hold * (len(rows) + 1)
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.subplots_adjust(left=0.36, right=0.96, top=0.86, bottom=0.2)
    fig.suptitle("Which scalar predicts when drivers intervene?  (second cut-in study, 288 cells, held out)",
                 fontsize=15, color=INK, y=0.95)
    ax.set_xlim(0, 0.40); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=13)
    ax.set_xlabel("held-out weighted RMSE   (lower is better; pre-registered folds)", fontsize=12)
    ax.invert_yaxis(); ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    bars = ax.barh(range(len(rows)), [0] * len(rows), color=[r[2] for r in rows][::-1], height=0.62)
    labels = [ax.text(0, i, "", va="center", fontsize=13, color=INK) for i in range(len(rows))]
    floor = ax.axvline(noise, color=INK, lw=1.5, ls="--")
    floor.set_visible(False)
    floor_txt = ax.text(noise + 0.004, -0.5, f"sampling-noise floor {noise:.3f}", fontsize=11.5, color=INK, va="center")
    floor_txt.set_visible(False)
    cap = caption(fig, "", y=0.06, size=14)
    caps = ["The field we started from: worse than predicting the mean",
            "Chance: the training folds' mean carried to the held-out cells",
            "Required deceleration (a physics-first cue): better than the field, still poor",
            "Time to collision: useful",
            "Gap alone: the best single scalar (gate R.2)",
            "Gap and TTC weighted equally: at the noise floor (card EL.1). The eye's cue: how fast the car grows",
            "Nothing can beat the dashed line except by luck"]

    def frame(k):
        step = min(k // hold, len(rows))
        for j, (name, val, col) in enumerate(rows):
            pos = len(rows) - 1 - j
            if j < step + 1 and j < len(rows):
                bars[pos].set_width(val)
                labels[pos].set_x(val + 0.005); labels[pos].set_y(pos); labels[pos].set_text(f"{val:.3f}")
        if step >= len(rows):
            floor.set_visible(True); floor_txt.set_visible(True)
        cap.set_text(caps[min(step, len(caps) - 1)])
        return bars

    anim = FuncAnimation(fig, frame, frames=n_frames, interval=1000 / FPS, blit=False)
    out = FIGS / "status_scoreboard.gif"
    anim.save(str(out), writer=PillowWriter(fps=FPS))
    plt.close(fig)
    print("wrote", out, rows, noise)
    return out


# ---------------------------------------------------------------------------------
# 3  the trait
# ---------------------------------------------------------------------------------
SCENARIOS = ["cutin_car", "cyclist_overtake", "ltap", "truck_overtake"]
SHORT = {"cutin_car": "cut-in", "cyclist_overtake": "cyclist\novertake", "ltap": "left turn\nacross path",
         "truck_overtake": "truck\novertake"}


def cell_key(d):
    parts = [d.criticality_label.astype(str)]
    if d.timepoint.notna().any():
        parts.append(d.timepoint.astype(str))
    if d.ltap_speed.notna().any():
        parts.append(d.ltap_speed.astype(str))
    out = parts[0]
    for p in parts[1:]:
        out = out + "|" + p
    return out


def driver_propensity(d):
    d = d.copy()
    d["cell"] = cell_key(d)
    d["resid"] = d.intervene - d.groupby("cell").intervene.transform("mean")
    return d.groupby("Exp_Subject_Id").resid.mean()


def make_trait_gif() -> Path:
    j = load_joint()
    r = j[(j.design == "Random") & (j.scenario.isin(SCENARIOS))].copy()
    P = pd.DataFrame({sc: driver_propensity(r[(r.scenario == sc) & r.intervene.notna()]) for sc in SCENARIOS}).dropna()
    share = re.search(r"Mean ratio across the six pairs: \*\*\+?([0-9.]+)\*\*",
                      (OUT / "cross_scenario_consistency.md").read_text(encoding="utf-8")).group(1)
    order = P["cutin_car"].rank().to_numpy()
    n = len(P)
    cols = plt.cm.viridis((order - 1) / (n - 1))
    Z = (P - P.mean()) / P.std()
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.2)
    fig.suptitle(f"One comfort-zone level per driver?  {n} drivers who saw all four scenarios (study 1, no field used)",
                 fontsize=15, color=INK, y=0.95)
    ax.set_xticks(range(4)); ax.set_xticklabels([SHORT[s] for s in SCENARIOS], fontsize=13)
    ax.set_ylabel("intervention propensity, criticality-adjusted (z)", fontsize=12)
    # Jonas, 2026-09-03: the topmost (yellow) driver ran off the top of the frame. The old
    # fixed +-2.8 was narrower than the data; take the limit from the z-scores themselves.
    lim = 1.12 * float(np.abs(Z.to_numpy()).max())
    ax.set_xlim(-0.4, 3.4); ax.set_ylim(-lim, lim)
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(0, color="#CCCCCC", lw=1)
    lines = [ax.plot([], [], color=cols[i], lw=1.8, alpha=0.85)[0] for i in range(n)]
    cap = caption(fig, "", y=0.06, size=14)
    per = 3                                        # frames per driver
    n_frames = per * n + 3 * FPS

    def frame(k):
        m = min(k // per + 1, n)
        for i in range(n):
            if i < m:
                lines[i].set_data(range(4), Z.iloc[i].to_numpy())
        if k < per * n:
            cap.set_text(f"Driver {m} of {n}: colored by how early they intervene in the cut-in, drawn across the other three scenarios")
        else:
            cap.set_text(f"The lines mostly keep their order: about {int(round(float(share) * 100))}% of the reliable per-driver signal is shared across all four scenarios")
        return lines

    anim = FuncAnimation(fig, frame, frames=n_frames, interval=1000 / FPS, blit=False)
    out = FIGS / "status_trait.gif"
    anim.save(str(out), writer=PillowWriter(fps=FPS))
    # The concepts deck embeds this as a movie too (Jonas, 2026-09-03), so write the .mp4 and
    # a FIRST-frame poster beside it, as make_concept_animations.save does.
    anim.save(str(out.with_suffix(".mp4")),
              writer=FFMpegWriter(fps=FPS, codec="libx264", bitrate=-1,
                                  extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]))
    # FIRST-frame poster, taken from the GIF: re-calling frame(0) would leave every artist
    # the frame function never clears in its final state (see make_concept_animations.save).
    with Image.open(out) as im:
        im.seek(0)
        im.convert("RGB").save(out.with_suffix(".png"))
    plt.close(fig)
    print("wrote", out, "+ .mp4 + .png poster", "drivers", n, "shared", share)
    return out


if __name__ == "__main__":
    make_model_gif()
    make_scoreboard_gif()
    make_trait_gif()
