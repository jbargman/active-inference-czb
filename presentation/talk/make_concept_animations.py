"""Animations that explain the measurement concepts one at a time (build_concepts_talk.py).

    python presentation/talk/make_concept_animations.py

Eight GIFs, every number from tracked data or a tracked output; captions inside the frames.
Extended 2026-09-03 on Jonas's ask for a slide describing the components of log theta_dot:
`concept_components.gif` takes the axis apart into log W - log gap - log TTC.
Revised 2026-09-02 evening after Jonas's review of the first version: the axis slide now
shows what participants did next to the two candidate axes and states the takeaway; the gate
projection is drawn as an arrow with a smoothed closing rate instead of a jumping ghost; the
held-out slide names its dots in plain words; a noise-floor animation with a popular-science
explanation was added; and a "whole model" animation brings the pieces together on one
study-1 clip against what participants did.

    concept_axis.gif        AXIS: the field's deficit against the optical expansion rate on
                            two study-2 stimuli (DV 21 km/h, starting TTC 2 s, lane change in
                            2 s and in 4 s), with the participants' intervention rates for the
                            same two stimuli (out/cutin2_cells.csv).
    concept_components.gif  WHAT THE AXIS IS MADE OF: log theta_dot = log W - log gap - log TTC
                            assembled on one study-2 clip, against the fitted level of
                            out/cutin2_looming.md (Jonas, 2026-09-03).
    concept_level.gif       LEVEL: study 1's 15 post-onset cells, the population response
                            curve, 43 drivers' thresholds from the fitted population (L-gated fit
                            in out/stage1_looming.md), the histogram, the 50th/80th percentiles.
    concept_gate.gif        GATE: clearance now, the 3 s projection as an arrow (closing rate =
                            0.3 s backward difference, as in card G.1), and the weight w.
    concept_noise.gif       NOISE FLOOR: one cell of 16 people whose true rate is one half,
                            drawn again and again; then all 288 cells under a perfect model.
    concept_heldout.gif     HOW WE TEST: leave-one-starting-TTC-out, fold by fold, then the floor.
    concept_percentile.gif  THE DELIVERABLE: percentile -> onset on the TTC4/TTC6 stimuli with
                            the level's CI (table 5 of out/stage1_looming.md).
    concept_whole.gif       THE WHOLE MODEL: study 1's TTC4 clip; gate w(t), axis theta_dot(t),
                            the model's population prediction P(t), and the six observed cell
                            means (table 1 of out/stage1_looming.md).
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
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.patches import FancyArrowPatch, Rectangle
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
from comfortzone.czb_data import RANDOM_CUTIN_TRACES                         # noqa: E402

PURPLE, TEAL, PINK, BLUE, INK, GREY, BEIGE, AMBER = ("#472CBE", "#1B8F7A", "#B03E82", "#36B7F6",
                                                     "#222222", "#6A6A6A", "#F0EDE6", "#C47A14")
KPH = 1000.0 / 3600.0
STUDY2 = REPO / "external/01_studies/01_Studies/02_Cut-in"
FPS = 8
W_CAR = 1.882
# The combining dot of "theta-dot" does not render in the default font; mathtext does.
TH = r"$\dot{\theta}$"


def caption(fig, text, y=0.04, size=14.5):
    return fig.text(0.5, y, text, ha="center", va="center", fontsize=size, color=INK, wrap=True,
                    bbox=dict(boxstyle="round,pad=0.5", fc=BEIGE, ec="none"))


def save(fig, fn, n, name, fps=FPS):
    """Write the animation three ways: .gif, .mp4 and a poster .png of the LAST frame.

    Jonas, 2026-09-03: an embedded GIF gives no scrub bar in PowerPoint, and pausing it
    restarts it from the beginning. An embedded H.264 .mp4 gets PowerPoint's own media
    controls -- play/pause that resumes, and a slider. The poster frame is what shows in
    normal (non-slideshow) view, so the slide is no longer blank on paper: it shows the
    finished picture. GIFs are still written, both as a fallback and because the handbook
    and the other decks link to them.
    """
    anim = FuncAnimation(fig, fn, frames=n, interval=1000 / fps, blit=False)
    out = FIGS / name
    anim.save(str(out), writer=PillowWriter(fps=fps))
    mp4 = out.with_suffix(".mp4")
    # yuv420p + even dimensions is what PowerPoint (and everything else) will play.
    anim.save(str(mp4), writer=FFMpegWriter(fps=fps, codec="libx264", bitrate=-1,
                                            extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]))
    fn(n - 1)                                   # leave the figure on its final frame
    fig.savefig(str(out.with_suffix(".png")), dpi=100)
    plt.close(fig)
    print("wrote", out, "+ .mp4 + .png poster")
    return out


def onset_from_stamps(trace):
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    mine = cells[cells.video.str.startswith(trace + "_CP1")]
    e1 = float(mine.video.iloc[0].split("_E")[1].replace(".mp4", "").replace("p", "."))
    return e1 + 0.066


def signals(path, onset_t):
    """t, deficit, theta_dot [deg/s], clearance l0, gap, lateral position y_tar, closing rate ldot."""
    tr = load_cutin_trace(path)
    f = cutin_predictors(tr, cutin_params(tr))
    W = float(tr.tar_wid)
    gap, vrel = f.gap_m.to_numpy(), f.v_rel.to_numpy()
    thd = np.degrees(W * np.maximum(vrel, 0) / (gap ** 2 + W ** 2 / 4))
    l0 = np.abs(f.y_rel.to_numpy()) - W
    t = f.t.to_numpy()
    dt = float(np.median(np.diff(t)))
    k = max(int(round(0.3 / dt)), 1)
    ldot = np.concatenate([np.zeros(k), (l0[k:] - l0[:-k]) / (k * dt)])   # backward 0.3 s difference (G.1)
    return dict(t=t, deficit=f.deficit.to_numpy(), thd=thd, l0=l0, gap=gap, y=tr.y_tar, ldot=ldot,
                vrel=vrel, W=W, onset=onset_t, tr=tr)


def looming_threshold_rad():
    """The full-sample fitted threshold on log(theta_dot), from the tracked EL.1b output."""
    txt = (OUT / "cutin2_looming.md").read_text(encoding="utf-8")
    c = float(re.search(r"threshold c on log\(theta_dot\) = ([-0-9.]+)", txt).group(1))
    return c, float(re.search(r"theta_dot at threshold = ([0-9.]+) rad/s", txt).group(1))


def parse_testtrack():
    """Section 1's model-free table, the two fits, and T6's transfer row, from card TT.1."""
    txt = (OUT / "ltapod_testtrack.md").read_text(encoding="utf-8")
    rows = []
    for m in re.finditer(r"^\| (-?[0-9.]+) \| (?:([0-9.]+) \((\d+)\)|–) \| (?:([0-9.]+) \((\d+)\)|–) \|$",
                         txt, re.MULTILINE):
        pet, tp, tn, vp, vn = m.groups()
        rows.append(dict(pet=float(pet),
                         track=float(tp) if tp else np.nan, track_n=int(tn) if tn else 0,
                         video=float(vp) if vp else np.nan, video_n=int(vn) if vn else 0))
    tab = pd.DataFrame(rows)

    def fit(label):
        m = re.search(r"\| " + label + r" \| PET_50 ([0-9.]+) s \(SE ([0-9.]+)\); sigma_pop ([0-9.]+) s "
                      r"\(SE [0-9.]+\); sigma_resp ([0-9.]+) s", txt)
        return dict(pet50=float(m.group(1)), se=float(m.group(2)),
                    sig_pop=float(m.group(3)), sig_resp=float(m.group(4)))

    t6 = re.search(r"\| track cells \| ([0-9.]+) \| ([0-9.]+) \| ([0-9.]+) \| ([0-9.]+) \|", txt)
    transfer = dict(chance=float(t6.group(1)), own=float(t6.group(2)),
                    other=float(t6.group(3)), floor=float(t6.group(4)))
    return tab, fit("track comfort"), fit("video 50 km/h"), transfer


# ---------------------------------------------------------------------------------
# 3b THE TRAIT, WITH THE MODEL  (Jonas, 2026-09-03: "slide 4 but with the current model")
# ---------------------------------------------------------------------------------
def make_traitmodel_gif():
    """Card TR.1: each driver's FITTED level in the two scenarios that have a current rule.

    The trait slide shows a model-free propensity across four scenarios. This is the same
    question asked of the model: one fitted level per driver per scenario. Two scenarios,
    not four, and the two that are missing are drawn as empty strips with the reason on
    them, because "to the extent possible" is the honest headline.

    The two levels are in different units and are NEVER put on one scale (that is EL.2,
    gated on EL.Q4). The shared vertical axis is each driver's PERCENTILE RANK within their
    own scenario, which no convention is needed to compute; each strip is labelled with its
    own real units at the 10th, 50th and 90th.
    """
    d = pd.read_csv(OUT / "driver_levels.csv")
    txt = (OUT / "driver_levels.md").read_text(encoding="utf-8")
    m = re.search(r"\| fitted LEVEL, this card \| ([-+0-9.]+) \| ([-+0-9.]+) to ([-+0-9.]+) \|", txt)
    rho, lo, hi = float(m.group(1)), float(m.group(2)), float(m.group(3))
    mp = re.search(r"\| model-free propensity, the slide-4 rule \| ([-+0-9.]+) \|", txt)
    rho_p = float(mp.group(1))

    # "Acts early" is a LOW looming level but a LONG PET, so the left turn is ranked on -PET
    # to put "acts early" at the same end of both strips. Stated on the figure.
    # Both strips are oriented so that the CAUTIOUS driver is at the top: a LOW looming level
    # (acts while the car is still growing slowly) and a LONG PET level (wants a bigger gap).
    rank = lambda a: 100.0 * (pd.Series(a).rank(method="average") - 0.5) / len(a)
    y_c = rank(-d.level_cutin_log.to_numpy()).to_numpy()
    y_v = rank(d.level_ltap_pet_s.to_numpy()).to_numpy()
    n = len(d)

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    ax = fig.add_axes([0.10, 0.20, 0.87, 0.63])
    fig.suptitle("The same driver, with the MODEL: each person's fitted level, scenario by scenario",
                 fontsize=15, color=INK, y=0.955)
    ax.set_xlim(-0.55, 3.55); ax.set_ylim(-8, 108)
    ax.set_ylabel("where this driver sits among the 43\n(percentile within that scenario)", fontsize=11.5)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["CUT-IN\ngated looming level\n[rad/s]",
                        "LEFT TURN (video)\nPET level\n[s]",
                        "CYCLIST OVERTAKE\n—", "TRUCK OVERTAKE\n—"], fontsize=11)
    for lab, col in zip(ax.get_xticklabels(), (PURPLE, TEAL, GREY, GREY)):
        lab.set_color(col)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(-0.5, 103, "the CAUTIOUS driver is at the top of both strips: acts while the car is still growing slowly, "
                       "and wants a longer gap before turning", fontsize=10, color=GREY)

    for xx in (2, 3):
        ax.axvspan(xx - 0.42, xx + 0.42, color="#F3F3F3", zorder=0)
    ax.text(2, 55, "no per-driver level:\nthe study's third\nquestion for this\nscenario is\nundocumented\n(B.1.Q1)",
            ha="center", va="center", fontsize=10.5, color=GREY)
    ax.text(3, 55, "no axis and no gate\nyet: the construction\nnote has not been\nwritten (card B.2)",
            ha="center", va="center", fontsize=10.5, color=GREY)

    # real-unit ticks on each strip, so the percentile axis does not hide the numbers
    # Unit ticks go on the OUTSIDE of each strip (cut-in left, left turn right) so that the
    # bundle of connecting lines between the two strips never runs over them.
    for xx, vals, fmt_, col, side in ((0, np.exp(d.level_cutin_log.to_numpy()), "%.3f", PURPLE, -1),
                                      (1, d.level_ltap_pet_s.to_numpy(), "%.1f", TEAL, +1)):
        yy = y_c if xx == 0 else y_v
        order = np.argsort(yy)
        for q in (10, 50, 90):
            v = np.interp(q, yy[order], vals[order])
            ax.plot([xx + side * 0.30, xx + side * 0.24], [q, q], color=col, lw=1.4)
            ax.text(xx + side * 0.33, q, fmt_ % v, ha="right" if side < 0 else "left",
                    va="center", fontsize=9.5, color=col)

    lines = [ax.plot([], [], color=GREY, lw=1.0, alpha=0.55, zorder=2)[0] for _ in range(n)]
    pts_c, = ax.plot([], [], "o", color=PURPLE, ms=8, alpha=0.9, zorder=3)
    pts_v, = ax.plot([], [], "o", color=TEAL, ms=8, alpha=0.9, zorder=3)
    stat = ax.text(0.72, 0.10, "", fontsize=12, color=INK, ha="center", va="center",
                   transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.6", fc=BEIGE, ec="none"))
    stat.set_visible(False)
    cap = caption(fig, "")

    p1 = n; p2 = p1 + n; n_frames = p2 + 4 * FPS

    def fn(i):
        k = min(i + 1, n)
        pts_c.set_data(np.zeros(k), y_c[:k])
        if i < p1:
            cap.set_text("Each dot is one driver's FITTED level on the cut-in — not a raw response rate, but where the model puts that person's threshold")
        else:
            j = min(i - p1 + 1, n)
            pts_v.set_data(np.ones(j), y_v[:j])
            for q in range(j):
                lines[q].set_data([0, 1], [y_c[q], y_v[q]])
            cap.set_text("The same 43 people on the left turn, fitted with that scenario's own rule. Flat lines mean the model found the same person twice")
        if i >= p2:
            stat.set_visible(True)
            stat.set_text("the fitted LEVEL agrees across scenarios at %+.2f  (95%% %+.2f to %+.2f)\n"
                          "the model-free propensity of the trait slide, same drivers: %+.2f"
                          % (rho, lo, hi, rho_p))
            cap.set_text("Two of four scenarios: the other two have no per-driver level to compute yet. The units differ and are never merged — that is card EL.2, and it waits on a decision")
        return [pts_c, pts_v] + lines

    return save(fig, fn, n_frames, "concept_traitmodel.gif")


# ---------------------------------------------------------------------------------
# 8  THE TEST TRACK AGAINST THE VIDEO  (Jonas, 2026-09-03: "demonstrate the difference")
# ---------------------------------------------------------------------------------
def make_trackvideo_gif():
    """Card TT.1 as one picture: the same left turn judged on video and driven on a track.

    Everything is parsed from out/ltapod_testtrack.md. Left: what people did, paradigm by
    paradigm, against the manipulated PET. Right: the two fitted populations of per-driver
    comfort boundaries, on the same axis, with the medians marked. Then the transfer result.
    """
    tab, trk, vid, tr = parse_testtrack()
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], left=0.075, right=0.975,
                          top=0.845, bottom=0.235, wspace=0.26)
    ax_r = fig.add_subplot(gs[0]); ax_p = fig.add_subplot(gs[1])
    fig.suptitle("Frozen video against a real car: the same left turn, two paradigms (card TT.1)",
                 fontsize=15, color=INK, y=0.955)

    ax_r.set_xlim(-0.3, 6.3); ax_r.set_ylim(-0.03, 1.05)
    ax_r.set_xlabel("PET the turn was set up for [s]", fontsize=11.5)
    ax_r.set_ylabel("share who went / would not have intervened", fontsize=11.5)
    ax_r.spines[["top", "right"]].set_visible(False)
    ax_r.set_title("what people did", fontsize=12.5, color=INK)
    # One scatter, updated in place: ax.collections is read-only in this matplotlib.
    trk_pts = ax_r.scatter([], [], color=PINK, alpha=0.55, zorder=3,
                           label="test track: drove it (2013, 26 drivers)")
    vid_pts, = ax_r.plot([], [], "-s", color=BLUE, lw=2.2, ms=8, label="video: judged a frozen clip (43 drivers, 50 km/h)")
    ax_r.legend(loc="lower right", fontsize=10, frameon=False)      # the data rises left to right
    ax_r.text(-0.2, 1.02, "marker size = runs in that cell (1 to 32)", ha="left", fontsize=9, color=GREY)

    ax_p.set_xlim(-0.3, 6.3); ax_p.set_ylim(0, 0.72)
    ax_p.set_xlabel("each driver's own comfort boundary [s of PET]", fontsize=11.5)
    ax_p.set_ylabel("density of drivers", fontsize=11.5)
    ax_p.spines[["top", "right", "left"]].set_visible(False); ax_p.set_yticks([])
    ax_p.set_title("the fitted population of boundaries", fontsize=12.5, color=INK)
    grid = np.linspace(-0.3, 6.3, 400)
    curve_t, = ax_p.plot([], [], color=PINK, lw=2.8)
    curve_v, = ax_p.plot([], [], color=BLUE, lw=2.8)
    med_t = ax_p.axvline(trk["pet50"], color=PINK, lw=2.0, ls="--"); med_t.set_visible(False)
    med_v = ax_p.axvline(vid["pet50"], color=BLUE, lw=2.0, ls="--"); med_v.set_visible(False)
    # The two medians are 0.27 s apart, so centred labels would sit on top of each other:
    # push the track's to the right of its line and the video's to the left of its own.
    lab_t = ax_p.text(trk["pet50"] + 0.12, 0.50, "", color=PINK, fontsize=11, ha="left", fontweight="bold")
    lab_v = ax_p.text(vid["pet50"] - 0.12, 0.44, "", color=BLUE, fontsize=11, ha="right", fontweight="bold")
    # Upper right: the only corner of this panel the two densities leave empty.
    score = ax_p.text(0.98, 0.97, "", fontsize=10.5, color=INK, transform=ax_p.transAxes,
                      va="top", ha="right", bbox=dict(boxstyle="round,pad=0.5", fc=BEIGE, ec="none"))
    cap = caption(fig, "")

    tt = tab.dropna(subset=["track"]); vv = tab.dropna(subset=["video"])
    p1 = 2 * FPS; p2 = p1 + 2 * FPS; p3 = p2 + 2 * FPS; n_frames = p3 + 4 * FPS

    def fn(i):
        if i < p1:                                            # the video curve draws first
            k = max(int((i + 1) / p1 * len(vv)), 1)
            vid_pts.set_data(vv.pet.to_numpy()[:k], vv.video.to_numpy()[:k])
            cap.set_text("On video, 43 drivers judged a frozen left turn: the longer the gap the turn was set up for, the fewer would have intervened")
        else:
            vid_pts.set_data(vv.pet, vv.video)
        if p1 <= i < p2:                                      # then the track's own runs
            k = max(int((i - p1 + 1) / (p2 - p1) * len(tt)), 1)
            sub = tt.iloc[:k]
            trk_pts.set_offsets(np.c_[sub.pet, sub.track])
            trk_pts.set_sizes(18 + 9 * sub.track_n.to_numpy())
            cap.set_text("On the test track in 2013, 26 drivers actually drove the turn. Far noisier: many of these points are one or two runs")
        elif i >= p2:
            trk_pts.set_offsets(np.c_[tt.pet, tt.track])
            trk_pts.set_sizes(18 + 9 * tt.track_n.to_numpy())
        if i >= p2:                                           # the two fitted populations
            f = min((i - p2 + 1) / (p3 - p2), 1.0)
            curve_t.set_data(grid, f * norm.pdf(grid, trk["pet50"], trk["sig_pop"]))
            curve_v.set_data(grid, f * norm.pdf(grid, vid["pet50"], vid["sig_pop"]))
            if f >= 1.0:
                med_t.set_visible(True); med_v.set_visible(True)
                lab_t.set_text("track %.2f s" % trk["pet50"]); lab_v.set_text("video %.2f s" % vid["pet50"])
            cap.set_text("Fit the SAME model to both. The median comfort boundary lands at %.2f s on the track and %.2f s on video — %.2f s apart, inside the design resolution"
                         % (trk["pet50"], vid["pet50"], trk["pet50"] - vid["pet50"]))
        if i >= p3:
            score.set_text(
                "Video model scored on the TRACK, nothing refitted\n"
                "     %.3f     against the track's own fit %.3f\n"
                "     and chance %.3f  →  it carries over\n\n"
                "But within-driver spread is %.2f s on the track\nand %.2f s on video: four times sharper in the car"
                % (tr["other"], tr["own"], tr["chance"], trk["sig_resp"], vid["sig_resp"]))
            cap.set_text("The video paradigm reproduces the real boundary to a quarter of a second — but a frozen clip is a blunter instrument for one person's own threshold")
        return [vid_pts, curve_t, curve_v]

    return save(fig, fn, n_frames, "concept_trackvideo.gif")


def gate_params():
    txt = (OUT / "cutin2_gate.md").read_text(encoding="utf-8")
    return (float(re.search(r"\| m_lat \[m\] \| - \| ([0-9.]+) \|", txt).group(1)),
            float(re.search(r"\| s_l \[m\] \| - \| ([0-9.]+) \|", txt).group(1)))


def parse_stage1():
    txt = (OUT / "stage1_looming.md").read_text(encoding="utf-8")
    rows = re.findall(r"\| (TTC\d) \| (C\d) \| (\d+) \| ([0-9.]+) \| ([0-9.]+) \| ([-0-9.]+) \| ([0-9.]+) \|", txt)
    cells = pd.DataFrame(rows, columns=["crit", "tp", "n", "p", "thd", "x", "w"]).astype(
        {"n": int, "p": float, "thd": float, "x": float, "w": float})
    g = re.search(r"\| L-gated \| `log\(theta_dot\)` \| gated \| ([-0-9.]+) \(SE [0-9.]+\) \| ([0-9.]+) \(SE [0-9.]+\) \| ([0-9.]+) \| ([0-9.]+) \(sd", txt)
    mu, sig_pop, sig_resp, lapse = float(g.group(1)), float(g.group(2)), float(g.group(3)), float(g.group(4))
    pct = {int(m.group(1)): float(m.group(2)) for m in re.finditer(r"\| L-gated \| (\d+)th \| [-0-9.]+ \| \[[^\]]+\] \| ([0-9.]+) \|", txt)}
    return cells, mu, sig_pop, sig_resp, lapse, pct


# ---------------------------------------------------------------------------------
# 1  AXIS
# ---------------------------------------------------------------------------------
def make_axis_gif():
    A = signals(STUDY2 / "02_Kinematics" / "LC_dv21_Tlc2p0_TTC02_vehicle_states.csv", onset_from_stamps("LC_dv21_Tlc2p0_TTC02"))
    B = signals(STUDY2 / "02_Kinematics" / "LC_dv21_Tlc4p0_TTC02_vehicle_states.csv", onset_from_stamps("LC_dv21_Tlc4p0_TTC02"))
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    hum = cells[(cells.dv_kph == 21) & (cells.ttc_start == 2) & cells.lcd.isin([2, 4])].copy()
    hum["cpn"] = hum.cp.str[2].astype(int)
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.6, 1], left=0.09, right=0.97, top=0.86, bottom=0.2, hspace=0.3, wspace=0.28)
    ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[1, 0], sharex=ax1); ax3 = fig.add_subplot(gs[:, 1])
    fig.suptitle("The AXIS: which candidate tells two stimuli apart the way participants did?  (DV 21 km/h, TTC 2 s: a 2 s and a 4 s lane change)",
                 fontsize=13.5, color=INK, y=0.955)
    t0, t1 = -2.5, 1.3
    for ax, lab in ((ax1, "field deficit\n(active-inference candidate)"), (ax2, "expansion rate [deg/s]\n(looming candidate)")):
        ax.set_xlim(t0, t1); ax.axvspan(t0, 0, color="#EEEEEE", zorder=0)
        ax.set_ylabel(lab, fontsize=11); ax.spines[["top", "right"]].set_visible(False)
    ax2.set_xlabel("time from lane-change onset [s]", fontsize=12)
    sel = lambda S: (S["t"] - S["onset"] > t0) & (S["t"] - S["onset"] < t1)
    ax1.set_ylim(0, 1.15 * max(A["deficit"][sel(A)].max(), B["deficit"][sel(B)].max()))
    ax2.set_ylim(0, 1.15 * max(A["thd"][sel(A)].max(), B["thd"][sel(B)].max()))
    lines = {}
    for key, S, ax, col, ls, name in (("A1", A, ax1, PINK, "-", "2 s lane change"), ("B1", B, ax1, PINK, "--", "4 s lane change"),
                                      ("A2", A, ax2, TEAL, "-", "2 s lane change"), ("B2", B, ax2, TEAL, "--", "4 s lane change")):
        lines[key], = ax.plot([], [], color=col, lw=2.6, ls=ls, label=name)
    ax1.legend(loc="upper left", fontsize=10.5, frameon=False); ax2.legend(loc="upper left", fontsize=10.5, frameon=False)
    ax1.text(t0 / 2, ax1.get_ylim()[1] * 0.9, "before onset", ha="center", color=GREY, fontsize=11)
    ax3.set_xlim(0.5, 5.5); ax3.set_ylim(0, 1.05); ax3.set_xticks([1, 2, 3, 4, 5]); ax3.set_xticklabels(["CP1\n(before)", "CP2", "CP3", "CP4", "CP5"], fontsize=10.5)
    ax3.set_ylabel("share of participants who said \"I would intervene\"", fontsize=11); ax3.spines[["top", "right"]].set_visible(False)
    ax3.set_title("what participants did", fontsize=12, color=INK)
    h2 = hum[hum.lcd == 2].sort_values("cpn"); h4 = hum[hum.lcd == 4].sort_values("cpn")
    p2, = ax3.plot([], [], "-o", color=INK, lw=2.2, ms=9, label="2 s lane change")
    p4, = ax3.plot([], [], "--s", color=INK, lw=2.2, ms=8, mfc="white", label="4 s lane change")
    ax3.legend(loc="lower right", fontsize=10.5, frameon=False)
    take = fig.text(0.5, 0.115, "", ha="center", fontsize=13, color=PURPLE, fontweight="bold")
    cap = caption(fig, "")
    grid = np.arange(t0, t1, 0.1)
    n_curve = len(grid)
    n_frames = n_curve + 5 * 3 + 4 * FPS

    def fn(i):
        tt = grid[min(i, n_curve - 1)]
        for key, S in (("A1", A), ("B1", B), ("A2", A), ("B2", B)):
            t_rel = S["t"] - S["onset"]; m = (t_rel >= t0) & (t_rel <= tt)
            lines[key].set_data(t_rel[m], (S["deficit"] if key.endswith("1") else S["thd"])[m])
        if i < n_curve:
            cap.set_text("Two candidate axes on the same two stimuli. The field says the slow lane change is no problem at all; the expansion rate says the two are alike")
        else:
            k = min((i - n_curve) // 3 + 1, 5)
            p2.set_data(h2.cpn.to_numpy()[:k], h2.p.to_numpy()[:k]); p4.set_data(h4.cpn.to_numpy()[:k], h4.p.to_numpy()[:k])
            cap.set_text("Participants intervened at about 0.9 for BOTH lane changes from CP2 on. The candidate to keep is the one that agrees with them")
            if k == 5:
                take.set_text("Takeaway: the expansion rate matches what people did; the field's deficit does not (it lost at gate R.2)")
        return list(lines.values()) + [p2, p4]

    return save(fig, fn, n_frames, "concept_axis.gif")


# ---------------------------------------------------------------------------------
# 1b  WHAT THE AXIS IS MADE OF  (Jonas, 2026-09-03: "describe the components of log theta_dot")
# ---------------------------------------------------------------------------------
def make_components_gif():
    """The axis taken apart: log theta_dot = log W - log gap - log TTC, on one real clip.

    The identity is exact for the small-angle expansion rate theta_dot = W*dv/gap^2, since
    gap*TTC = gap^2/dv = W/theta_dot. The left column plots the two ingredients and the
    quantity they make; the right column assembles the three log contributions into the
    total and compares it with the fitted level. The dashed marker on the total bar is the
    EXACT expansion rate W*dv/(gap^2 + W^2/4) that card EL.1b scored, so the slide shows
    for itself how little the small-angle step costs at these distances.
    """
    S = signals(STUDY2 / "02_Kinematics" / "LC_dv21_Tlc2p0_TTC02_vehicle_states.csv",
                onset_from_stamps("LC_dv21_Tlc2p0_TTC02"))
    c_log, c_rad = looming_threshold_rad()
    W = S["W"]
    t_rel = S["t"] - S["onset"]
    t0, t1 = -2.5, 1.3
    m = (t_rel >= t0) & (t_rel <= t1)
    tt, gap, vrel = t_rel[m], S["gap"][m], S["vrel"][m]
    ttc = gap / np.maximum(vrel, 1e-6)
    thd_small = W * vrel / gap ** 2                       # the small-angle form the identity uses
    thd_exact = np.radians(S["thd"][m])                   # W*dv/(gap^2 + W^2/4), as scored in EL.1b

    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(3, 2, width_ratios=[1.15, 1], left=0.085, right=0.975,
                          top=0.845, bottom=0.20, hspace=0.32, wspace=0.30)
    fig.suptitle("What the AXIS is made of:   log " + TH + "  =  log W  −  log gap  −  log TTC",
                 fontsize=15.5, color=INK, y=0.955)

    ax_g = fig.add_subplot(gs[0, 0])
    ax_t = fig.add_subplot(gs[1, 0], sharex=ax_g)
    ax_d = fig.add_subplot(gs[2, 0], sharex=ax_g)
    for ax, lab, col, ymax in ((ax_g, "gap [m]", BLUE, 1.1 * gap.max()),
                               (ax_t, "TTC [s]", AMBER, 1.1 * ttc.max()),
                               (ax_d, TH + " [deg/s]", TEAL, 1.15 * np.degrees(thd_exact).max())):
        ax.set_xlim(t0, t1); ax.set_ylim(0, ymax)
        ax.axvspan(t0, 0, color="#EEEEEE", zorder=0)
        ax.set_ylabel(lab, fontsize=11.5, color=col)
        ax.spines[["top", "right"]].set_visible(False)
    ax_d.set_xlabel("time from lane-change onset [s]", fontsize=11.5)
    ax_d.axhline(np.degrees(c_rad), color=PURPLE, lw=1.2, ls=":")
    ax_d.text(t1 - 0.05, np.degrees(c_rad), "fitted level", ha="right", va="bottom",
              fontsize=9.5, color=PURPLE)
    lg, = ax_g.plot([], [], color=BLUE, lw=2.6)
    lt, = ax_t.plot([], [], color=AMBER, lw=2.6)
    ld, = ax_d.plot([], [], color=TEAL, lw=2.6)

    ax_b = fig.add_subplot(gs[:, 1])
    labels = ["log W\n(the car's width)", "− log gap\n(how far away)", "− log TTC\n(how fast it closes)"]
    cols = [GREY, BLUE, AMBER]
    ypos = np.array([3.0, 2.0, 1.0])
    bars = ax_b.barh(ypos, [0, 0, 0], height=0.55, color=cols)
    ax_b.set_yticks(list(ypos) + [-0.55]); ax_b.set_yticklabels(labels + [TH + "\non its axis"], fontsize=11)
    ax_b.set_xlim(-6.2, 1.6); ax_b.set_ylim(-1.35, 3.7)
    ax_b.axvline(0, color=INK, lw=1.0, ymin=0.30)
    ax_b.axhline(0.30, color=GREY, lw=0.8)
    # The total is a marker on a number line, not a bar: criticality rises to the RIGHT, so
    # the marker crosses the level from the left. A bar anchored at zero would shrink instead.
    ax_b.plot([-6.2, 1.6], [-0.55, -0.55], color=INK, lw=1.4, zorder=1)
    ax_b.plot([c_log, c_log], [-0.95, -0.15], color=PURPLE, lw=2.0, ls=":", zorder=2)
    ax_b.text(c_log, -1.06, "the fitted level\n%.4f rad/s" % c_rad, ha="center", va="top",
              fontsize=9.5, color=PURPLE)
    tot_mk, = ax_b.plot([], [], "v", color=TEAL, ms=15, zorder=4)
    exact_mk, = ax_b.plot([], [], "|", color=INK, ms=16, mew=2.0, zorder=5)
    ax_b.text(-6.1, -0.20, "black tick = exact " + TH + ", no small-angle step (it sits under the marker)",
              fontsize=8.5, color=GREY, ha="left", va="bottom")
    ax_b.tick_params(axis="y", length=0)
    ax_b.set_xlabel("log " + TH + "   [log units, " + TH + " in rad/s]", fontsize=11)
    ax_b.spines[["top", "right", "left"]].set_visible(False)
    ax_b.set_title("the three parts, adding up", fontsize=12, color=INK)
    vals = [ax_b.text(0, y, "", va="center", fontsize=10.5, color=INK) for y in ypos]
    tot_lab = ax_b.text(0, -0.30, "", va="bottom", ha="center", fontsize=11.5, color=TEAL, fontweight="bold")
    cap = caption(fig, "")

    grid = np.arange(t0, t1, 0.05)
    n_frames = len(grid) + 3 * FPS

    def fn(i):
        k = min(i, len(grid) - 1)
        upto = tt <= grid[k]
        lg.set_data(tt[upto], gap[upto]); lt.set_data(tt[upto], ttc[upto])
        ld.set_data(tt[upto], np.degrees(thd_exact)[upto])
        j = int(np.argmax(np.cumsum(upto)))                       # last sample shown
        parts = [np.log(W), -np.log(gap[j]), -np.log(ttc[j])]
        total = sum(parts)
        for b, v in zip(bars, parts):
            b.set_width(v)
        for txt, y, v in zip(vals, ypos, parts):
            txt.set_position((v + (0.12 if v >= 0 else -0.12), y))
            txt.set_ha("left" if v >= 0 else "right")
            txt.set_text("%+.2f" % v)
        tot_mk.set_data([total], [-0.55])
        exact_mk.set_data([np.log(thd_exact[j])], [-0.55])
        tot_lab.set_position((total, -0.42)); tot_lab.set_text("%+.2f" % total)
        if grid[k] < 0:
            cap.set_text("One real clip. The gap shrinks and the time to collision shrinks; add their two logs and you get how fast the car grows in the eye")
        elif grid[k] < 0.6:
            cap.set_text("Only two things vary: how far away it is, and how fast it is closing. The width is a constant, so it only shifts where the level sits")
        else:
            cap.set_text("The two logs enter with EQUAL weight — which is exactly what the fit chose on its own (w = 0.497). The marker passes the level when a typical driver says \"now\"")
        return list(bars) + [lg, lt, ld, tot_mk, exact_mk, tot_lab] + vals

    return save(fig, fn, n_frames, "concept_components.gif")


# ---------------------------------------------------------------------------------
# 2  LEVEL
# ---------------------------------------------------------------------------------
def make_level_gif():
    cells, mu, sig_pop, sig_resp, lapse, pct = parse_stage1()
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
    ax.set_ylabel("share who said \"I would intervene\"", fontsize=12); ax.spines[["top", "right"]].set_visible(False)
    ticks = [0.01, 0.02, 0.05, 0.1, 0.2]
    axh.set_xticks(np.log(ticks)); axh.set_xticklabels([f"{np.degrees(v):.1f}°/s" for v in ticks], fontsize=11)
    axh.set_xlabel("how fast the other car grows in the eye (log scale)", fontsize=12)
    axh.set_ylabel("drivers", fontsize=12); axh.spines[["top", "right"]].set_visible(False); axh.set_ylim(0, 14)
    pts, = ax.plot([], [], "o", color=PURPLE, ms=9, alpha=0.85)
    curve, = ax.plot([], [], color=INK, lw=2.4)
    ticks_art = [ax.plot([], [], color=TEAL, lw=1.2, alpha=0.7)[0] for _ in range(n_drv)]
    edges = np.linspace(xs[0], xs[-1], 26)
    bars = axh.bar(0.5 * (edges[:-1] + edges[1:]), np.zeros(25), width=(xs[-1] - xs[0]) / 25 * 0.9, color=TEAL, alpha=0.8)
    # Jonas, 2026-09-03: carry the dashed percentile lines down into the histogram as well,
    # so that "the percentile is read off the distribution of levels" is visible rather than
    # asserted. The two panels already share an x-axis, so the lines align by construction.
    pct_lines = {}
    for q, col, yy in ((50, PURPLE, 0.62), (80, PINK, 0.9)):
        top = ax.axvline(np.log(pct[q]), color=col, lw=2.2, ls="--")
        bot = axh.axvline(np.log(pct[q]), color=col, lw=2.2, ls="--")
        lab = ax.text(np.log(pct[q]) + 0.03, yy, "", color=col, fontsize=12, fontweight="bold")
        blab = axh.text(np.log(pct[q]) - 0.04, 11.6, "", color=col, fontsize=11.5,
                        fontweight="bold", ha="right")
        pct_lines[q] = (top, lab, bot, blab)
        top.set_visible(False); bot.set_visible(False)
    cap = caption(fig, "")
    n_cells = len(open_); phase1 = n_cells; phase2 = n_cells + 2 * FPS; phase3 = phase2 + n_drv; n_frames = phase3 + 3 * FPS

    def fn(i):
        k = min(i + 1, n_cells)
        pts.set_data(open_.x.to_numpy()[:k], open_.p.to_numpy()[:k])
        if i >= phase1:
            curve.set_data(xs, pop_curve)
        if i >= phase2:
            m = min(i - phase2 + 1, n_drv)
            for j in range(m):
                ticks_art[j].set_data([levels[j], levels[j]], [0, 0.5])
            h, _ = np.histogram(levels[:m], bins=edges)
            for b, v in zip(bars, h):
                b.set_height(v)
        if i >= phase3:
            for q, (ln, tx, bln, btx) in pct_lines.items():
                ln.set_visible(True); bln.set_visible(True)
                tx.set_text(f"{q}th percentile: {np.degrees(pct[q]):.1f}°/s")
                btx.set_text(f"{q}% of drivers ←")
        if i < phase1:
            cap.set_text("Each dot is one design cell after the lane change has started: the share who said \"I would intervene\" against how fast the car was growing")
        elif i < phase2:
            cap.set_text("The population response curve: a cumulative normal on the log axis, averaged over drivers (the stage-1 fit, out/stage1_looming.md)")
        elif i < phase3:
            cap.set_text("Behind the curve, each driver has one threshold, their LEVEL. The fit estimates the spread of levels: median 1.8°/s, spread 0.87 log units")
        else:
            cap.set_text("The deliverable is a percentile of this distribution: the 80th percentile is the growth rate at which 80% of drivers would already have acted")
        return [pts, curve]

    return save(fig, fn, n_frames, "concept_level.gif")


# ---------------------------------------------------------------------------------
# 3  GATE
# ---------------------------------------------------------------------------------
def make_gate_gif():
    m_lat, s_l = gate_params()
    S = signals(STUDY2 / "02_Kinematics" / "LC_dv21_Tlc3p0_TTC04_vehicle_states.csv", onset_from_stamps("LC_dv21_Tlc3p0_TTC04"))
    t, l0, ldot, gap, y, t_on = S["t"], S["l0"], S["ldot"], S["gap"], S["y"], S["onset"]
    w = norm.cdf((m_lat - l0 - ldot * 3.0) / s_l)
    t0, t1 = t_on - 2.5, t_on + 2.3
    idx = np.where((t >= t0) & (t <= t1))[0][::3]
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.2], left=0.09, right=0.97, top=0.88, bottom=0.2, hspace=0.35)
    ax_road = fig.add_subplot(gs[0]); ax_w = fig.add_subplot(gs[1])
    fig.suptitle("The GATE: does this vehicle count yet?  Its clearance now, where it will be in 3 s, and the weight w",
                 fontsize=14.5, color=INK, y=0.96)
    ax_road.set_xlim(-8, 45); ax_road.set_ylim(-6, 6); ax_road.set_aspect("equal"); ax_road.axis("off")
    ax_road.add_patch(Rectangle((-8, -1.85), 53, 3.7, fc="#F3F0FF", ec="none", zorder=0))
    ax_road.text(44, -1.6, "my lane", ha="right", fontsize=10, color=PURPLE)
    for yy in (-5.55, -1.85, 1.85, 5.55):
        ax_road.plot([-8, 45], [yy, yy], color="#BBBBBB", lw=1.2, ls="--" if abs(yy) < 2 else "-")
    ax_road.add_patch(Rectangle((-4.6, -0.9), 4.6, 1.8, fc=PURPLE, ec="none"))
    ax_road.text(-2.3, -1.6, "you", ha="center", fontsize=10.5, color=PURPLE)
    car = Rectangle((0, 0), 4.6, W_CAR, fc=PINK, ec="none"); ax_road.add_patch(car)
    arrow = FancyArrowPatch((0, 0), (0, 0), arrowstyle="-|>", mutation_scale=22, color=PINK, lw=2.2, ls="--")
    ax_road.add_patch(arrow)
    lab = ax_road.text(0, -4.9, "", fontsize=11, color=INK)
    ax_w.set_xlim(t0 - t_on, t1 - t_on); ax_w.set_ylim(0, 1.05)
    ax_w.set_xlabel("time from lane-change onset [s]", fontsize=12); ax_w.set_ylabel("gate weight w  (0 = ignore, 1 = counts fully)", fontsize=11.5)
    ax_w.axvspan(t0 - t_on, 0, color="#EEEEEE", zorder=0); ax_w.spines[["top", "right"]].set_visible(False)
    wl, = ax_w.plot([], [], color=BLUE, lw=3); wd, = ax_w.plot([], [], "o", color=BLUE, ms=9)
    ax_w.text(t1 - t_on - 0.05, 0.55, f"w = Φ((m_lat − clearance in 3 s) / s_l),  m_lat {m_lat:.2f} m, s_l {s_l:.2f} m  (card G.1)",
              ha="right", fontsize=10.5, color=GREY)
    cap = caption(fig, "")
    dt = float(np.median(np.diff(t))); k = max(int(round(0.3 / dt)), 1)
    yv_s = np.concatenate([np.zeros(k), (S["tr"].y_tar[k:] - S["tr"].y_tar[:-k]) / (k * dt)])

    def fn(i):
        j = idx[i]
        y_now = float(y[j]); y_proj = float(np.clip(y_now + yv_s[j] * 3.0, -0.3, 5.5))
        car.set_xy((gap[j], y_now - W_CAR / 2))
        arrow.set_positions((gap[j] + 2.3, y_now), (gap[j] + 2.3, y_proj))
        lab.set_x(min(max(gap[j] - 4, 0), 30)); lab.set_text(f"clearance now {max(l0[j], 0):.2f} m,  in 3 s at this sideways speed {max(l0[j] + ldot[j] * 3, 0):.2f} m")
        tt = t[idx[: i + 1]] - t_on
        wl.set_data(tt, w[idx[: i + 1]]); wd.set_data([tt[-1]], [w[j]])
        if tt[-1] < 0:
            cap.set_text("Before onset the car is not moving sideways: even 3 s ahead it is still clear of my lane, so w stays near 0.07 and nothing counts yet")
        elif w[j] < 0.9:
            cap.set_text("As it starts to move over, the arrow (where it will be in 3 s) reaches into my lane and w rises: the gap starts to count")
        else:
            cap.set_text("Committed: w ≈ 1, the response depends on the axis alone. Fitted on post-onset cells, this gate predicted the pre-onset cells out of sample (card G.1)")
        return [wl, wd]

    return save(fig, fn, len(idx), "concept_gate.gif")


# ---------------------------------------------------------------------------------
# 4  NOISE FLOOR
# ---------------------------------------------------------------------------------
def make_noise_gif():
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    c = cells[cells.cp != "CP1"].reset_index(drop=True)
    y, w = c.p.to_numpy(float), c.n.to_numpy(float)
    noise = float(np.sqrt(np.average(y * (1 - y) / np.maximum(w, 1), weights=w)))
    rng = np.random.default_rng(1)
    n_people, p_true, n_draws = 16, 0.5, 24
    draws = rng.random((n_draws, n_people)) < p_true
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 0.9, 1.3], left=0.06, right=0.97, top=0.85, bottom=0.2, wspace=0.35)
    ax_p = fig.add_subplot(gs[0]); ax_h = fig.add_subplot(gs[1]); ax_s = fig.add_subplot(gs[2])
    fig.suptitle("The NOISE FLOOR: the error a perfect model would still show, because each cell is a handful of people",
                 fontsize=14.5, color=INK, y=0.95)
    ax_p.set_xlim(-0.5, 3.5); ax_p.set_ylim(-1.9, 4.3); ax_p.set_aspect("equal"); ax_p.axis("off")
    # Jonas, 2026-09-03: "it is not obvious what a cell is". Say it on the picture, in the
    # study's own terms (glossary chapter 13: one design condition, its share and its n).
    ax_p.set_title("A CELL = one clip, frozen at one moment,\nanswered by 12–24 people",
                   fontsize=12.5, color=INK, fontweight="bold")
    ax_p.text(1.5, 3.85, "here: 16 people whose true chance of \"yes\" is exactly 50%",
              ha="center", fontsize=10.5, color=GREY)
    dots = [ax_p.add_patch(plt.Circle((k % 4, 3 - k // 4), 0.36, fc="#DDDDDD", ec="none")) for k in range(n_people)]
    frac_txt = ax_p.text(1.5, -0.7, "", ha="center", fontsize=12.5, color=INK)
    ax_p.text(1.5, -1.55, "one speed × one starting TTC × one lane-change duration\n× one freeze point  →  one cell.  This study has 288 of them",
              ha="center", fontsize=10, color=PURPLE)
    ax_h.set_xlim(0, 1); ax_h.set_ylim(0, 8); ax_h.set_xlabel("observed share of \"yes\"", fontsize=11.5); ax_h.set_ylabel("how many draws", fontsize=11.5)
    ax_h.axvline(0.5, color=PINK, lw=2, ls="--"); ax_h.text(0.52, 7.4, "truth 0.50", color=PINK, fontsize=11)
    ax_h.spines[["top", "right"]].set_visible(False)
    edges = np.linspace(0, 1, 17)
    bars = ax_h.bar(0.5 * (edges[:-1] + edges[1:]), np.zeros(16), width=1 / 16 * 0.9, color=BLUE)
    sd_txt = ax_h.text(0.03, 6.6, "", fontsize=11, color=INK)
    ax_s.set_xlim(0, 1); ax_s.set_ylim(0, 1); ax_s.plot([0, 1], [0, 1], color="#CCCCCC", lw=1)
    ax_s.set_xlabel("a PERFECT model's prediction (the true rate)", fontsize=11.5); ax_s.set_ylabel("what 12-24 people would actually say", fontsize=11.5)
    ax_s.spines[["top", "right"]].set_visible(False); ax_s.set_title("all 288 cells, one simulated study", fontsize=12, color=INK)
    sc, = ax_s.plot([], [], "o", color=PURPLE, ms=5, alpha=0.6)
    rmse_txt = ax_s.text(0.03, 0.9, "", fontsize=12, color=INK)
    sim = rng.binomial(w.astype(int), y) / w        # a perfect model predicts y; people answer binomially
    cap = caption(fig, "")
    hold = 4; n1 = hold * n_draws; n2 = n1 + 2 * FPS; n_frames = n2 + 3 * FPS
    order = rng.permutation(len(y))

    def fn(i):
        if i < n1:
            d = i // hold
            for k, dot in enumerate(dots):
                dot.set_facecolor(TEAL if draws[d, k] else "#DDDDDD")
            frac = draws[: d + 1].mean(axis=1)
            frac_txt.set_text(f"draw {d + 1}: {draws[d].sum()} of 16 said yes = {draws[d].mean():.2f}")
            h, _ = np.histogram(frac, bins=edges)
            for b, v in zip(bars, h):
                b.set_height(v)
            if d >= 3:
                sd_txt.set_text(f"spread so far: sd {frac.std():.2f}")
            cap.set_text("Ask 16 people whose true chance of saying yes is exactly one half. You will not get 8. Ask another 16: a different number. That scatter is sampling noise")
        else:
            m = min(int((i - n1) / (2 * FPS) * len(y)) + 1, len(y))
            sel = order[:m]
            sc.set_data(y[sel], sim[sel])
            rmse = float(np.sqrt(np.average((sim[sel] - y[sel]) ** 2, weights=w[sel])))
            rmse_txt.set_text(f"error of the perfect model: {rmse:.3f}" + (f"\nexpected: {noise:.3f} = the noise floor" if i >= n2 else ""))
            if i < n2:
                cap.set_text("Now every cell: even a model that knows each cell's TRUE rate is off by the sampling noise of the 12-24 people who saw that clip")
            else:
                cap.set_text(f"Average that noise over the 288 cells and you get {noise:.3f}. No model can score below it except by luck, so a model at the floor is as good as this data can show")
        return [sc]

    return save(fig, fn, n_frames, "concept_noise.gif")


# ---------------------------------------------------------------------------------
# 5  HOW WE TEST
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
    fits = {}
    for f in order:
        tr, te = folds != f, folds == f
        fits[f] = T.fit_reg(x[tr], y[tr], w[tr]); pred[te] = R.predict(fits[f], x[te], +1.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 7.2), dpi=100, width_ratios=[1.3, 1])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.84, bottom=0.2, wspace=0.3)
    fig.suptitle("HOW WE TEST: fit the rule on five groups of cells, predict the sixth it never saw, repeat; then compare with the floor",
                 fontsize=14, color=INK, y=0.96)
    ax1.set_xlim(-6, -0.5); ax1.set_ylim(0, 1.02); ax1.set_xlabel("how fast the car grows (log)", fontsize=12); ax1.set_ylabel("share who said \"I would intervene\"", fontsize=12)
    ax1.spines[["top", "right"]].set_visible(False); ax1.set_title("fitting", fontsize=12, color=INK)
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1); ax2.set_xlabel("what the rule PREDICTED for cells it never saw", fontsize=11.5); ax2.set_ylabel("what participants ACTUALLY said in those cells", fontsize=11.5)
    ax2.plot([0, 1], [0, 1], color="#CCCCCC", lw=1); ax2.text(0.62, 0.55, "perfect prediction", color=GREY, fontsize=10, rotation=38)
    ax2.spines[["top", "right"]].set_visible(False); ax2.set_title("scoring", fontsize=12, color=INK)
    train_pts, = ax1.plot([], [], "o", color="#BBBBBB", ms=6, label="cells used to fit the rule")
    test_pts, = ax1.plot([], [], "o", color=PINK, ms=9, label="cells held out (not used)")
    curve, = ax1.plot([], [], color=INK, lw=2, label="the fitted rule")
    ax1.legend(loc="upper left", fontsize=10.5, frameon=False)
    sc_done, = ax2.plot([], [], "o", color=PURPLE, ms=6, alpha=0.7, label="held-out cells from earlier folds")
    sc_now, = ax2.plot([], [], "o", color=PINK, ms=9, label="this fold's held-out cells")
    ax2.legend(loc="lower right", fontsize=10.5, frameon=False)
    txt = ax2.text(0.04, 0.9, "", fontsize=12.5, color=INK)
    cap = caption(fig, "")
    hold = 2 * FPS; n_frames = hold * (len(order) + 1)
    xs = np.linspace(-6, -0.5, 200)

    def fn(i):
        k = min(i // hold, len(order))
        if k < len(order):
            f = order[k]; tr, te = folds != f, folds == f
            train_pts.set_data(x[tr], y[tr]); test_pts.set_data(x[te], y[te]); curve.set_data(xs, R.predict(fits[f], xs, +1.0))
            done = np.isin(folds, order[:k]); sc_done.set_data(pred[done], y[done]); sc_now.set_data(pred[te], y[te])
            m = np.isin(folds, order[: k + 1]); err = T.wrmse(y[m], pred[m], w[m])
            txt.set_text(f"held out so far: {int(m.sum())} cells, error {err:.3f}")
            cap.set_text(f"Fold {k + 1} of 6: the cells with starting TTC {f:.0f} s (pink) are set aside; the rule is fitted on the grey ones, then asked to predict the pink ones")
        else:
            th = T.fit_reg(x, y, w)
            train_pts.set_data(x, y); test_pts.set_data([], []); curve.set_data(xs, R.predict(th, xs, +1.0))
            sc_done.set_data(pred, y); sc_now.set_data([], [])
            txt.set_text(f"all 288 cells held out: error {T.wrmse(y, pred, w):.3f}\nnoise floor {noise:.3f}")
            cap.set_text("Every cell has now been predicted by a rule that never saw it. The error, 0.113, sits on the noise floor: this is as good as the data can show")
        return [train_pts, test_pts, curve, sc_done, sc_now]

    return save(fig, fn, n_frames, "concept_heldout.gif")


# ---------------------------------------------------------------------------------
# 6  THE DELIVERABLE
# ---------------------------------------------------------------------------------
def make_percentile_gif():
    txt = (OUT / "stage1_looming.md").read_text(encoding="utf-8")
    rows = re.findall(r"\| (\d+)th \| ([0-9.]+) \| ([-0-9.]+|nan) \| ([-0-9.]+|nan) \| ([-0-9.]+|nan) \| ([0-9.]+|nan) \| ([0-9.]+|nan) \| ([0-9.]+|nan) \|", txt)
    tab = pd.DataFrame(rows, columns=["pct", "level", "on4", "on6", "on8", "ci4", "ci6", "ci8"]).astype(float)
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.86, bottom=0.22)
    fig.suptitle("THE DELIVERABLE: choose a percentile of drivers' levels as the trigger; here is what it costs in seconds (study 1 stimuli)",
                 fontsize=14, color=INK, y=0.96)
    ax.set_xlim(48, 97); ax.set_ylim(-1.2, 3.0)
    ax.set_xlabel("percentile of drivers' levels used as the trigger", fontsize=12)
    # Jonas, 2026-09-03: "what is zero on the y-axis, how can it be before the lateral motion
    # starts?" Zero is the lane-change onset, and the crossing IS before it on the TTC 4 s
    # stimulus, because this curve is the AXIS crossing with the gate deliberately left off
    # (out/stage1_looming.md section 5 says so in as many words). Label it and shade it.
    ax.set_ylabel("when the axis crosses the level, GATE OFF\n[s from the start of the lateral motion]", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhspan(-1.2, 0, color="#EEEEEE", zorder=0)
    ax.axhline(0, color=INK, lw=1.2)
    ax.text(96.5, 0.06, "0 = the lane change starts (the car begins to move sideways)",
            ha="right", va="bottom", fontsize=11, color=INK)
    ax.text(96.5, -0.12, "below the line: the car is already growing fast enough for this driver — but the GATE is still shut,\n"
                         "so the model predicts (and participants showed) almost no intervention until the lateral motion begins",
            ha="right", va="top", fontsize=10.5, color=GREY)
    l4, = ax.plot([], [], "-o", color=PURPLE, lw=2.5, ms=7, label="TTC 4 s stimulus")
    l6, = ax.plot([], [], "-o", color=TEAL, lw=2.5, ms=7, label="TTC 6 s stimulus")
    band = ax.fill_between([], [], [], color=PURPLE, alpha=0.15)
    ax.legend(loc="upper left", fontsize=12, frameon=False)
    note = ax.text(96, 2.8, "", ha="right", fontsize=12, color=INK)
    cap = caption(fig, "")
    n = len(tab); hold = FPS

    def fn(i):
        nonlocal band
        k = min(i // hold + 1, n); d = tab.iloc[:k]
        l4.set_data(d.pct, d.on4); l6.set_data(d.pct, d.on6)
        band.remove(); band = ax.fill_between(d.pct, d.on4 - d.ci4 / 2, d.on4 + d.ci4 / 2, color=PURPLE, alpha=0.15)
        note.set_text(f"{int(d.pct.iloc[-1])}th percentile: level {np.degrees(d.level.iloc[-1]):.1f}°/s;  the TTC 8 s stimulus never crosses")
        cap.set_text("Each 5-point step of the percentile moves the trigger by about 0.24 s; the shaded band is the level's own estimation uncertainty, about 0.52 s"
                     if k < n else "On this axis the estimate's uncertainty, not the percentile choice, is the bottleneck: more drivers would help more than settling the percentile")
        return [l4, l6]

    return save(fig, fn, hold * n + 3 * FPS, "concept_percentile.gif")


# ---------------------------------------------------------------------------------
# 7  THE WHOLE MODEL on study 1's TTC4 clip, against what participants did
# ---------------------------------------------------------------------------------
def make_whole_gif():
    m_lat, s_l = gate_params()
    cells, mu, sig_pop, sig_resp, lapse, pct = parse_stage1()
    obs = cells[cells.crit == "TTC4"].sort_values("tp")
    tr = load_cutin_trace(RANDOM_CUTIN_TRACES["TTC4"])
    S = signals(RANDOM_CUTIN_TRACES["TTC4"], float(tr.t[tr.onset_idx]))
    t, thd, l0, ldot, gap, y, t_on = S["t"], S["thd"], S["l0"], S["ldot"], S["gap"], S["y"], S["onset"]
    w = norm.cdf((m_lat - l0 - ldot * 3.0) / s_l)
    rng = np.random.default_rng(0)
    lev = mu + sig_pop * rng.standard_normal(3000)
    with np.errstate(divide="ignore"):
        xlog = np.log(np.maximum(np.radians(thd), 1e-9))
    resp = np.array([norm.cdf((xx - lev) / sig_resp).mean() for xx in xlog])
    P = lapse + (1 - lapse) * w * resp
    obs_t = np.array([-0.15] + [0.3 * (k - 1) for k in range(2, 7)])     # C1 at -0.15 s; Ck at onset + 0.3 (k-1)
    t0, t1 = t_on - 2.0, t_on + 1.8
    idx = np.where((t >= t0) & (t <= t1))[0][::3]
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    gs = fig.add_gridspec(3, 2, width_ratios=[1.15, 1], height_ratios=[0.7, 1, 1], left=0.08, right=0.97, top=0.9, bottom=0.2, hspace=0.5, wspace=0.28)
    ax_road = fig.add_subplot(gs[0, :]); ax_g = fig.add_subplot(gs[1, 0]); ax_a = fig.add_subplot(gs[2, 0]); ax_p = fig.add_subplot(gs[1:, 1])
    fig.suptitle("THE WHOLE MODEL on one study-1 clip (TTC 4 s): gate × axis × the population of levels, against what 43 drivers did",
                 fontsize=13.5, color=INK, y=0.96)
    ax_road.set_xlim(-8, 60); ax_road.set_ylim(-6, 6); ax_road.set_aspect("auto"); ax_road.axis("off")
    for yy in (-5.55, -1.85, 1.85, 5.55):
        ax_road.plot([-8, 60], [yy, yy], color="#BBBBBB", lw=1.2, ls="--" if abs(yy) < 2 else "-")
    ax_road.add_patch(Rectangle((-4.6, -0.9), 4.6, 1.8, fc=PURPLE, ec="none")); ax_road.text(-2.3, -3.6, "you", ha="center", fontsize=10, color=PURPLE)
    car = Rectangle((0, 0), 4.6, W_CAR, fc=PINK, ec="none"); ax_road.add_patch(car)
    for ax, lab, col in ((ax_g, "GATE w", BLUE), (ax_a, "AXIS [deg/s]", TEAL)):
        ax.set_xlim(t0 - t_on, t1 - t_on); ax.axvspan(t0 - t_on, 0, color="#EEEEEE", zorder=0); ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylabel(lab, fontsize=11, color=col)
    ax_g.set_ylim(0, 1.05); ax_a.set_ylim(0, 1.15 * thd[idx].max()); ax_a.set_xlabel("time from lane-change onset [s]", fontsize=11)
    ax_a.axhline(np.degrees(pct[50]), color=TEAL, lw=1, ls=":"); ax_a.text(t1 - t_on - 0.05, np.degrees(pct[50]), "median level", ha="right", va="bottom", fontsize=9.5, color=TEAL)
    lg, = ax_g.plot([], [], color=BLUE, lw=2.6); la, = ax_a.plot([], [], color=TEAL, lw=2.6)
    ax_p.set_xlim(t0 - t_on, t1 - t_on); ax_p.set_ylim(0, 1.02); ax_p.axvspan(t0 - t_on, 0, color="#EEEEEE", zorder=0)
    ax_p.set_xlabel("time from lane-change onset [s]", fontsize=11); ax_p.set_ylabel("share who would intervene", fontsize=11.5); ax_p.spines[["top", "right"]].set_visible(False)
    lp, = ax_p.plot([], [], color=PURPLE, lw=3, label="the model: gate × axis × the population of levels")
    po, = ax_p.plot([], [], "o", color=INK, ms=9, label="what participants said (C1–C6)")
    ax_p.legend(loc="upper left", fontsize=9.5, frameon=False)
    cap = caption(fig, "")

    def fn(i):
        j = idx[i]; tt = t[idx[: i + 1]] - t_on
        car.set_xy((gap[j], float(y[j]) - W_CAR / 2))
        lg.set_data(tt, w[idx[: i + 1]]); la.set_data(tt, thd[idx[: i + 1]]); lp.set_data(tt, P[idx[: i + 1]])
        shown = obs_t <= tt[-1]
        po.set_data(obs_t[shown], obs.p.to_numpy()[shown])
        if tt[-1] < 0:
            cap.set_text("Before onset: the gate is near zero, so however fast the car grows, the model predicts almost nobody intervenes, and almost nobody did (C1)")
        elif tt[-1] < 0.7:
            cap.set_text("The gate opens as the car moves over; the axis climbs; the model's share rises as the axis passes more and more drivers' levels")
        else:
            cap.set_text("The purple curve is the whole model, fitted on all of study 1; the dots are this clip's six cells. Gate × axis × level, and nothing else")
        return [lg, la, lp, po]

    return save(fig, fn, len(idx), "concept_whole.gif")


if __name__ == "__main__":
    make_axis_gif(); make_components_gif(); make_level_gif(); make_gate_gif(); make_noise_gif()
    make_heldout_gif(); make_percentile_gif(); make_whole_gif(); make_trackvideo_gif()
