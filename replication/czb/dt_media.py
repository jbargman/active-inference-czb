"""
Figures and a video for `docs/display_transform_explained.md` (the display transform, explained).

Illustration, not a card: every number drawn comes from the transform (`src/comfortzone/display.py`,
spec defaults), the second study's cells and one of its traces, and card DT.2's left-turn stimuli.
The one clip shown is the second study's LC_dv21_Tlc2p0_TTC04 (closing 21 km/h, 4 s TTC at the start
of the shown window, 2 s lane change); its five response moments (CP1-CP5) are marked.

Drawing conventions (for the pictures only): camera at the ego's front bumper (the pipeline's
convention, `camera_to_front_m` = 0) and 1.2 m above the road; the cut-in car's rear face 1.45 m
high; lane 3.5 m wide. The time series use the pipeline's centred looming formula (card EL.1b).

Output: figures/display_transform/*.png, figures/display_transform/display_transform_clip.mp4
Run:    python replication/czb/dt_media.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
from comfortzone import display as D  # noqa: E402
from comfortzone.cutin import cutin_predictors  # noqa: E402
import cutin2_field_vs_gap as R  # noqa: E402
import cutin2_looming as CL  # noqa: E402
import dt2_ltap_display as DT2  # noqa: E402

OUT = REPO / "figures" / "display_transform"
KPH = 1000 / 3600
CLIP = "LC_dv21_Tlc2p0_TTC04"
HC, HCAR, LANE = 1.2, 1.45, 3.5
LEVEL_R, FAREWELL = 0.0320, 0.02          # card JJ.10 (rendered), Farewell's emergency onset
C_REAL, C_PART = "#1f77b4", "#d62728"


def clip_series(g):
    tr = R.load_cutin_trace(R.KIN / f"{CLIP}_vehicle_states.csv")
    p = cutin_predictors(tr)
    t, gap, dv, y = (p[c].to_numpy(float) for c in ("t", "gap_m", "v_rel", "y_rel"))
    W = float(tr.tar_wid)
    m = gap > 2.5
    t, gap, dv, y = t[m], gap[m], dv[m], y[m]
    real, part = D.perceived(gap, dv, W, None), D.perceived(gap, dv, W, g)
    cells = pd.read_csv(HERE / "out" / "cutin2_cells.csv")
    cps = cells[cells.video.str.startswith(CLIP)]
    ends = [float(v.split("_E")[1].replace(".mp4", "").replace("p", ".")) for v in cps.video]
    return dict(t=t, gap=gap, dv=dv, y=y, W=W, real=real, part=part, cps=list(zip(cps.cp, ends)))


def view_polys(gap, y, W, k):
    """Screen-direction outlines (deg) of the car's rear face and the lane lines, for gain k."""
    ang = lambda Y, X: np.degrees(np.arctan(k * Y / X))   # noqa: E731  (same formula for elevation)
    car = [(ang(y - W / 2, gap), ang(-HC, gap)), (ang(y + W / 2, gap), ang(-HC, gap)),
           (ang(y + W / 2, gap), ang(-HC + HCAR, gap)), (ang(y - W / 2, gap), ang(-HC + HCAR, gap))]
    X = np.geomspace(1.5, 400, 200)
    lines = [(ang(np.full_like(X, Y0), X), ang(np.full_like(X, -HC), X)) for Y0 in (-LANE / 2, LANE / 2, 1.5 * LANE)]
    return car, lines


def fig_looming_vs_ttc(g):
    cells = pd.read_csv(HERE / "out" / "cutin2_cells.csv")
    cells = cells[cells.cp != "CP1"]
    W = float(np.median(CL.widths_for(cells)[0]))
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    dv = np.linspace(0.3, 13, 200)
    sc = ax[0].scatter(cells.dv_kph * KPH, cells.distance, c=cells.p, cmap="viridis", s=18, vmin=0, vmax=1)
    for T in (2, 4, 8):
        ax[0].plot(dv, T * dv, color="k", lw=1)
        xl = min(dv[-1], 85.0 / T)
        ax[0].text(xl, T * xl, f"TTC {T} s ", va="bottom", ha="right", fontsize=8)
    for L_, ls in ((0.01, ":"), (0.032, "-"), (0.1, "--")):
        ax[0].plot(dv, np.sqrt(np.maximum(W * dv / L_ - W ** 2 / 4, 0)), color=C_PART, ls=ls, lw=1.4,
                   label=f"looming {L_} rad/s")
    ax[0].set(xlim=(0, 13), ylim=(0, 90), xlabel="closing speed [m/s]", ylabel="gap [m]",
              title="Same TTC = straight line; same looming = curve")
    ax[0].legend(fontsize=8, loc="upper left")
    fig.colorbar(sc, ax=ax[0], label="share who would intervene (study 2)")
    # two situations, same TTC, different looming
    t = np.linspace(0, 3.9, 200)
    for g0, v, lab in ((10.0, 2.5, "near and slow: 10 m at 2.5 m/s"), (40.0, 10.0, "far and fast: 40 m at 10 m/s")):
        gg = g0 - v * t
        ax[1].plot(t, W * v / (gg ** 2 + W ** 2 / 4), lw=2, label=f"{lab} (TTC {g0 / v:.0f} s at t = 0)")
    ax[1].set(yscale="log", xlabel="time [s]", ylabel="looming [rad/s]",
              title="Both reach the car at the same moment,\nbut the near one looms 4x faster throughout")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_looming_vs_ttc.png", dpi=140)
    plt.close(fig)


def fig_geometry(g):
    k = D.gain(g)
    fig, ax = plt.subplots(1, 3, figsize=(16, 5.2), gridspec_kw={"width_ratios": [1, 1.3, 1.6]})
    X, Y, W = 20.0, 0.0, 1.9
    a = ax[0]
    a.plot([0, 30], [0, 30], "k-", lw=0.8)
    a.plot([0, 30], [0, -30], "k-", lw=0.8)
    a.add_patch(Rectangle((X, -W / 2), 1.2, W, color="grey"))
    a.plot([0, X], [0, W / 2], color=C_REAL, lw=1)
    a.plot([0, X], [0, -W / 2], color=C_REAL, lw=1)
    a.text(3, 22, f"rendering camera\n{g.virtual_hfov_deg:.0f} deg field of view", fontsize=9)
    a.text(8, -12, f"car {X:.0f} m ahead\nsubtends {np.degrees(2 * np.arctan(W / 2 / X)):.1f} deg", fontsize=9)
    a.set(xlim=(-1, 32), ylim=(-31, 31), aspect="equal", title="1  The virtual world is rendered", xticks=[], yticks=[])
    a = ax[1]
    Sw, d = D.image_width_cm(g), g.viewing_distance_cm
    a.plot([0, 0], [-Sw / 2, Sw / 2], "k-", lw=4)
    a.plot([d, 0], [0, Sw / 2], "k-", lw=0.8)
    a.plot([d, 0], [0, -Sw / 2], "k-", lw=0.8)
    Fc = D.focal_cm(g)
    img = Fc * W / X
    a.plot([0, 0], [-img / 2, img / 2], color="grey", lw=8)
    a.plot([d, 0], [0, img / 2], color=C_PART, lw=1)
    a.plot([d, 0], [0, -img / 2], color=C_PART, lw=1)
    a.plot(d, 0, "ko")
    a.text(8, 26, f"participant's eye\n{d:.0f} cm from a {Sw:.0f} cm wide image:\nthe image fills {D.display_hfov_deg(g):.0f} deg",
           fontsize=9)
    a.text(2, -img / 2 - 6, f"the car on screen\nsubtends {np.degrees(2 * np.arctan(img / 2 / d)):.1f} deg", fontsize=9)
    a.set(xlim=(-5, d + 5), ylim=(-35, 42), aspect="equal", title="2  ... and viewed on a monitor", xticks=[], yticks=[])
    a = ax[2]
    a.plot([0, 60], [0, 60], "k-", lw=0.8, alpha=0.3)
    a.plot([0, 60], [0, -60], "k-", lw=0.8, alpha=0.3)
    Xe = X / k
    a.add_patch(Rectangle((Xe, -W / 2), 1.2, W, color="grey"))
    a.add_patch(Rectangle((X, -W / 2), 1.2, W, fill=False, ls=":", ec="grey"))
    a.plot([0, Xe], [0, W / 2], color=C_PART, lw=1)
    a.plot([0, Xe], [0, -W / 2], color=C_PART, lw=1)
    a.text(2, 20, f"what reached the eye = the same car\n{Xe:.0f} m away (x {1 / k:.2f}),\nclosing {1 / k:.2f} times faster:\nsame TTC, {k:.2f} x the looming",
           fontsize=9)
    a.set(xlim=(-1, 60), ylim=(-31, 31), aspect="equal", title="3  The equivalent world", xticks=[], yticks=[])
    fig.tight_layout()
    fig.savefig(OUT / "fig2_geometry.png", dpi=140)
    plt.close(fig)


def fig_timeseries(s, g):
    fig, ax = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    t = s["t"]
    for a, key, lab in ((ax[0], "theta", "angular size [deg]"), (ax[1], "theta_dot", "looming [rad/s]")):
        f = np.degrees if key == "theta" else (lambda v: v)
        a.plot(t, f(s["real"][key]), color=C_REAL, lw=2, label="a driver in the virtual car (what we computed so far)")
        a.plot(t, f(s["part"][key]), color=C_PART, lw=2, label="the participant's eye (monitor)")
        a.set(yscale="log", ylabel=lab)
    ax[1].axhline(LEVEL_R, color=C_REAL, ls="--", lw=1, label=f"the video curve's level, rendered looming ({LEVEL_R})")
    ax[1].axhline(LEVEL_R * D.gain(g), color=C_PART, ls="--", lw=1,
                  label=f"the same level as the participant saw it ({LEVEL_R * D.gain(g):.4f})")
    ax[1].axhline(FAREWELL, color="k", ls=":", lw=1, label="real-world emergency-braking onset (Farewell, 0.02)")
    for key, col, lab in (("real", C_REAL, "virtual car"), ("part", C_PART, "participant")):
        tau = s[key]["theta"] / np.gradient(s[key]["theta"], t)
        ax[2].plot(t, tau, color=col, lw=2 if key == "real" else 4, alpha=1 if key == "real" else 0.4,
                   label=f"optical TTC (theta / theta_dot), {lab}")
    ax[2].plot(t, s["gap"] / s["dv"], "k:", lw=1, label="kinematic TTC = gap / closing speed")
    ax[2].set(ylabel="TTC [s]", xlabel="time in the trace [s]", ylim=(0, 25))
    for a in ax:
        for cp, e in s["cps"]:
            a.axvline(e, color="grey", lw=0.5)
        a.legend(fontsize=8, loc="upper left")
    ax[0].set_title(f"One study-2 clip ({CLIP}): grey lines = the five moments participants answered at")
    fig.tight_layout()
    fig.savefig(OUT / "fig3_clip_timeseries.png", dpi=140)
    plt.close(fig)


def fig_ltap(g):
    k = D.gain(g)
    obs = DT2.read_observed()
    c = pd.read_csv(HERE / "out" / "ltap_cells.csv")
    c = c[c.speed_kph == 50].sort_values("pet")
    pet, r, rdot, W = (c[x].to_numpy(float) for x in ("pet", "range_ego_onc", "range_rate", "w_onc"))
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].plot(pet, r, "o-", color=C_REAL, label="distance on the video (rendered) = what a track driver sees")
    ax[0].plot(pet, r / k, "o-", color=C_PART, label="distance the participant's eye implies (x 2.36)")
    tr_r = np.exp(DT2.at_pet(pet, np.log(r), obs["track"]))
    ax[0].axhline(tr_r, color="k", ls="--", lw=1)
    ax[0].text(0, tr_r + 3, f"test-track boundary ({obs['track']:.2f} s PET): {tr_r:.0f} m", fontsize=8)
    ax[0].axvline(obs["first"], color="grey", lw=1)
    ax[0].text(obs["first"] + 0.05, 180, f"observed video\nboundary\n{obs['first']:.2f} s PET", fontsize=8)
    pred = DT2.interp_pet(pet, np.log(r / k), np.log(tr_r))
    ax[0].set(xlabel="design PET [s]", ylabel="distance to the oncoming car [m]",
              title=f"Judged on perceived distance, the video boundary would be where red meets\n"
                    f"the dashed line: at PET {pred:.1f} s, outside the design. It was at {obs['first']:.2f} s")
    ax[0].legend(fontsize=8, loc="lower right")
    ax[1].plot(pet, c.tta, "o-", color="k", label="time to arrival (same for both)")
    ax[1].axvline(obs["track"], color="k", ls="--", lw=1, label=f"test track {obs['track']:.2f} s")
    ax[1].axvline(obs["first"], color="grey", lw=1, label=f"video (first exposure) {obs['first']:.2f} s")
    ax[1].set(xlabel="design PET [s]", ylabel="time to arrival [s]",
              title="Time is not changed by the display:\ntrack and video agree")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_ltap.png", dpi=140)
    plt.close(fig)


def video(s, g):
    k = D.gain(g)
    t = s["t"]
    fr = np.arange(np.searchsorted(t, 5.0), len(t), 2)
    fig = plt.figure(figsize=(13, 7.2))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1])
    a_real, a_part = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    a_top = fig.add_subplot(gs[0, 2])
    a_loom, a_ttc = fig.add_subplot(gs[1, :2]), fig.add_subplot(gs[1, 2])
    hd = np.degrees(np.arctan(np.tan(np.radians(g.virtual_hfov_deg / 2))))
    vd = np.degrees(np.arctan(np.tan(np.radians(g.virtual_hfov_deg / 2)) * g.screen_aspect_h / g.screen_aspect_w))
    hp, vp = D.display_hfov_deg(g) / 2, np.degrees(np.arctan(D.image_width_cm(g) * g.screen_aspect_h / g.screen_aspect_w / 2 / g.viewing_distance_cm))
    for a, ttl, (h, v), kk in ((a_real, "a driver sitting in the virtual car", (hd, vd), 1.0),
                               (a_part, "the participant's eye, looking at the monitor", (hp, vp), k)):
        a.set(xlim=(50, -50), ylim=(-32, 32), aspect="equal", title=ttl, xlabel="direction [deg]")
        frame = Rectangle((-h, -v), 2 * h, 2 * v, fc="#eef3f7", ec="k", lw=1)
        a.add_patch(frame)
        a.plot([-h, h], [0, 0], color="#9ab", lw=0.8)
        _, lines = view_polys(20, 0, 1.9, kk)
        for xl, yl in lines:
            ln, = a.plot(xl, yl, color="#667", lw=1)
            ln.set_clip_path(frame)
    polys = [Polygon(np.zeros((4, 2)), color=C_REAL), Polygon(np.zeros((4, 2)), color=C_PART)]
    a_real.add_patch(polys[0])
    a_part.add_patch(polys[1])
    a_part.text(0, -30, "grey = the room around the monitor", ha="center", fontsize=8)
    a_part.set_facecolor("#cfcfcf")
    # top-down: the real car and the equivalent-world car
    a_top.set(xlim=(-8, 8), ylim=(0, 1.05 * s["gap"][fr[0]] / k), title="seen from above", xlabel="lateral [m]", ylabel="ahead of the camera [m]")
    for yy in (-LANE / 2, LANE / 2, 1.5 * LANE):
        a_top.axvline(-yy, color="#667", lw=0.8)
    car_r = Rectangle((0, 0), 1.9, 4.5, color=C_REAL, label="the car in the virtual world")
    car_p = Rectangle((0, 0), 1.9, 4.5, color=C_PART, alpha=0.6, label=f"where it seemed to be (x {1 / k:.2f})")
    a_top.add_patch(car_r)
    a_top.add_patch(car_p)
    a_top.legend(fontsize=7, loc="upper left")
    a_loom.plot(t, s["real"]["theta_dot"], color=C_REAL, lw=2, label="looming, virtual car")
    a_loom.plot(t, s["part"]["theta_dot"], color=C_PART, lw=2, label="looming, participant")
    a_loom.axhline(LEVEL_R, color=C_REAL, ls="--", lw=1, label=f"video level, rendered ({LEVEL_R})")
    a_loom.axhline(LEVEL_R * k, color=C_PART, ls="--", lw=1, label=f"same level as seen ({LEVEL_R * k:.4f})")
    a_loom.axhline(FAREWELL, color="k", ls=":", lw=1, label="Farewell's emergency onset (real world)")
    for cp, e in s["cps"]:
        a_loom.axvline(e, color="grey", lw=0.5)
    a_loom.set(yscale="log", xlabel="time [s]", ylabel="looming [rad/s]", xlim=(t[fr[0]], t[-1]))
    a_loom.legend(fontsize=8, loc="upper left")
    tau_r = s["real"]["theta"] / np.gradient(s["real"]["theta"], t)
    tau_p = s["part"]["theta"] / np.gradient(s["part"]["theta"], t)
    a_ttc.plot(t, tau_r, color=C_REAL, lw=2, label="virtual car")
    a_ttc.plot(t, tau_p, color=C_PART, lw=5, alpha=0.4, label="participant")
    a_ttc.set(xlabel="time [s]", ylabel="optical TTC [s]", ylim=(0, 25), xlim=(t[fr[0]], t[-1]),
              title="TTC from the optics: identical")
    a_ttc.legend(fontsize=8)
    cur = [a_loom.axvline(t[fr[0]], color="k"), a_ttc.axvline(t[fr[0]], color="k")]
    dots = [a_loom.plot([], [], "o", color=C_REAL)[0], a_loom.plot([], [], "o", color=C_PART)[0]]
    txt = fig.suptitle("")

    def draw(i):
        j = fr[i]
        for poly, kk in zip(polys, (1.0, k)):
            car, _ = view_polys(s["gap"][j], s["y"][j], s["W"], kk)
            poly.set_xy(np.array(car))
        car_r.set_xy((-s["y"][j] - 0.95, s["gap"][j]))
        car_p.set_xy((-s["y"][j] - 0.95, s["gap"][j] / k))
        for c_ in cur:
            c_.set_xdata([t[j], t[j]])
        dots[0].set_data([t[j]], [s["real"]["theta_dot"][j]])
        dots[1].set_data([t[j]], [s["part"]["theta_dot"][j]])
        txt.set_text(f"t = {t[j]:5.1f} s   gap {s['gap'][j]:5.1f} m   TTC {s['gap'][j] / s['dv'][j]:5.1f} s   |   "
                     f"car subtends {np.degrees(s['real']['theta'][j]):4.1f} deg in the virtual car, "
                     f"{np.degrees(s['part']['theta'][j]):4.1f} deg on the monitor   |   looming "
                     f"{s['real']['theta_dot'][j]:.4f} vs {s['part']['theta_dot'][j]:.4f} rad/s")
        return polys + [car_r, car_p, txt] + cur + dots

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    anim = animation.FuncAnimation(fig, draw, frames=len(fr), blit=False)
    anim.save(OUT / "display_transform_clip.mp4", writer=animation.FFMpegWriter(fps=15, bitrate=2400), dpi=110)
    for i, name in ((int(len(fr) * 0.35), "fig5_frame_early.png"), (int(len(fr) * 0.8), "fig5_frame_late.png")):
        draw(i)
        fig.savefig(OUT / name, dpi=110)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    g = D.load_geometry()
    s = clip_series(g)
    fig_looming_vs_ttc(g)
    fig_geometry(g)
    fig_timeseries(s, g)
    fig_ltap(g)
    video(s, g)
    print("written:", *sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
