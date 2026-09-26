"""
Figures (and the few numbers quoted beside them) for the left-turn chapter of
`docs/display_transform_explained.md`: the video LTAP/OD study against the 2013 test track under the
display transform (card DT.2).

Illustration, not a card: it re-draws card DT.2's comparison and the data behind it. Numbers that
the chapter quotes and DT.2 did not print (the effective gain with the POOLED video boundary, the
perceived looming at the track boundary, the view angles) are written to
`replication/czb/out/dt_ltap_media_numbers.md`.

Scene drawing (schematic): the ego's and the oncoming car's paths are the stimulus trace's own
(PET 2.5 s, 50 km/h, the design cell nearest the track boundary); the lane edges (3.5 m lanes) and
the side road the ego turns into (10 m wide, to the left, centred on the ego's exit path) are
inferred from those paths, since the traces carry no road geometry. Camera 1.2 m above the road at
the ego's position (the pipeline's convention).

Output: figures/display_transform/fig6_ltap_scene.png ... fig10_ltap_gain.png,
        replication/czb/out/dt_ltap_media_numbers.md
Run:    python replication/czb/dt_ltap_media.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
from comfortzone import display as D  # noqa: E402
from comfortzone import ltap as LT  # noqa: E402
import dt2_ltap_display as DT2  # noqa: E402
import pt1_farewell_thresholds as P1  # noqa: E402

OUT = REPO / "figures" / "display_transform"
NUM = HERE / "out" / "dt_ltap_media_numbers.md"
HC, LANE = 1.2, 3.5
C_REAL, C_PART, C_TRACK = "#1f77b4", "#d62728", "#2ca02c"


def stimuli():
    c = pd.read_csv(HERE / "out" / "ltap_cells.csv")
    return c.sort_values(["speed_kph", "pet"]).reset_index(drop=True)


def camera_frame(pet=2.5, spd=50):
    """Ego camera pose at the decision moment and the scene in camera coordinates (X ahead, Y left)."""
    raw = pd.read_csv(LT.RANDOM_LTAP_TRACES[(pet, spd)])
    tr = LT.load_ltap_trace(LT.RANDOM_LTAP_TRACES[(pet, spd)])
    parts = {int(v): g.sort_values("Elapsed_Time_s").reset_index(drop=True) for v, g in raw.groupby("Vehicle_ID")}
    e, o = parts[tr.ego_id], parts[tr.onc_id]
    i = int(np.searchsorted(e.Elapsed_Time_s.to_numpy(), tr.t_dec))
    E = np.array([e.Location_X[i], e.Location_Y[i]])
    h = np.radians(e.Yaw[i])
    u, n = np.array([np.cos(h), np.sin(h)]), np.array([-np.sin(h), np.cos(h)])
    # the traces' yaw convention is mirrored: orient "left" so the oncoming lane is on the left
    # (right-hand traffic; the ego turns left across it)
    op = o[["Location_X", "Location_Y"]].to_numpy()
    n = n * np.sign(np.median((op - E) @ n))
    cam = lambda P: np.stack([(P - E) @ u, (P - E) @ n], axis=-1)   # noqa: E731
    return dict(tr=tr, e=e, o=o, i=i, E=E, u=u, n=n, cam=cam)


def fig_scene(f, k):
    e, o, i = f["e"], f["o"], f["i"]
    ep = f["cam"](e[["Location_X", "Location_Y"]].to_numpy())
    op = f["cam"](o[["Location_X", "Location_Y"]].to_numpy())
    oi = f["cam"](o[["Location_X", "Location_Y"]].to_numpy()[i])
    y_onc = float(np.median(op[:, 1]))
    x_exit = float(ep[-1, 0])
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.axhspan(-LANE / 2, y_onc + LANE / 2, color="#e9e9e9")
    ax.add_patch(Rectangle((x_exit - 5, y_onc + LANE / 2), 10, 40, color="#e9e9e9"))
    ax.plot(ep[:, 0], ep[:, 1], color="k", lw=1.5, label="ego's path (turns left)")
    ax.plot(op[:, 0], op[:, 1], color=C_REAL, lw=1, ls="--", label="oncoming car's path")
    ax.plot(0, 0, "ks", ms=8)
    ax.text(0, -3.2, "ego at the decision\nmoment (camera)", ha="center", va="top", fontsize=8)
    ax.plot(*oi, "o", color=C_REAL, ms=9, label=f"oncoming car: {np.hypot(*oi):.0f} m ahead (what a driver sees)")
    ax.plot(oi[0] / k, oi[1], "o", color=C_PART, ms=9,
            label=f"where the monitor made it appear: {np.hypot(oi[0] / k, oi[1]):.0f} m (x {1 / k:.2f} in depth)")
    ax.annotate("", xy=(oi[0] / k, oi[1] + 2), xytext=(oi[0], oi[1] + 2), arrowprops=dict(arrowstyle="->", color=C_PART))
    xc = f["tr"].x_conf
    conf = f["cam"](np.array([xc, f["tr"].y_band]))
    ax.plot(*conf, "kx", ms=9, mew=2, label="conflict point")
    ax.set(xlim=(-12, 250), ylim=(-8, 45), aspect="equal", xlabel="ahead of the ego [m]", ylabel="left [m]",
           title="The left turn at the decision moment (design PET 2.5 s, 50 km/h; road layout schematic)")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "fig6_ltap_scene.png", dpi=140)
    plt.close(fig)
    return oi, y_onc, x_exit, conf


def fig_views(f, k, oi, y_onc, x_exit, conf):
    tr = f["tr"]
    H = float(f["o"].Height_m.iloc[0])
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.9))
    out = {}
    for a, kk, ttl, col in ((axs[0], 1.0, "a driver in the car (and on the test track)", C_REAL),
                            (axs[1], k, "the participant's eye, looking at the monitor", C_PART)):
        az = lambda Y, X: np.degrees(np.arctan(kk * Y / X))          # noqa: E731
        X = np.geomspace(3, 600, 300)
        for Y0, lw in ((-LANE / 2, 1), (y_onc + LANE / 2, 1), ((y_onc - LANE / 2 + LANE / 2) / 1.0, 0.6)):
            a.plot(az(np.full_like(X, Y0), X), az(np.full_like(X, -HC), X), color="#667", lw=lw)
        Ys = np.linspace(y_onc + LANE / 2, 60, 100)
        for Xe in (x_exit - 5, x_exit + 5):
            a.plot(az(Ys, np.full_like(Ys, Xe)), az(np.full_like(Ys, -HC), np.full_like(Ys, Xe)), color="#667", lw=1)
        W = tr.w_onc
        xs = [az(oi[1] - W / 2, oi[0]), az(oi[1] + W / 2, oi[0])]
        ys = [az(-HC, oi[0]), az(-HC + H, oi[0])]
        a.add_patch(Rectangle((xs[0], ys[0]), xs[1] - xs[0], ys[1] - ys[0], color=col))
        a.axhline(0, color="#9ab", lw=0.8)
        a.set(xlim=(22, -6), ylim=(-6, 3), aspect="equal", title=ttl, xlabel="direction [deg] (left is left)")
        out[kk] = (abs(xs[1] - xs[0]), az(oi[1], oi[0]), az(conf[1], conf[0]))
        a.text(21, -2.6 if kk == 1.0 else -1.0, "side road the ego turns into", fontsize=7, va="bottom")
        a.text(3.0, 1.0, "oncoming lane (left of centre)", fontsize=7, ha="center")
        a.text(21, 2.2, f"oncoming car {abs(xs[1] - xs[0]):.2f} deg wide, {az(oi[1], oi[0]):.1f} deg left", fontsize=8)
    axs[0].set_ylabel("elevation [deg]")
    fig.suptitle("Same moment, same scene: the monitor shrinks everything by the same factor, so where the car is "
                 "relative to the intersection does not change", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig7_ltap_views.png", dpi=140)
    plt.close(fig)
    return out


def fig_video_evidence(c):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    for spd, mk in ((50, "o-"), (70, "s--")):
        s = c[c.speed_kph == spd]
        ax[0].plot(s.tta, s.p, mk, label=f"oncoming at {spd} km/h")
        ax[1].plot(s.d_onc, s.p, mk, label=f"oncoming at {spd} km/h")
    ax[0].set(xlabel="oncoming car's time to the conflict point [s]", ylabel="share who would intervene",
              title="Against TIME the two speeds do not line up")
    ax[1].set(xlabel="oncoming car's distance to the conflict point [m]",
              title="Against DISTANCE they lie much closer together")
    for a in ax:
        a.set_ylim(0, 1)
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig8_ltap_video_axis.png", dpi=140)
    plt.close(fig)


def fig_track_video(c, obs):
    r = pd.read_csv(HERE / "out" / "ltapod_runs.csv", low_memory=False)
    r = r[(r.cond == "comfort") & (~r.removed.astype(bool))].copy()
    r["bin"] = (np.round(r.SetPET * 2) / 2).clip(-0.5, 5.0)
    g = r.groupby("bin").agg(nogo=("go", lambda v: 1 - np.mean(v)), n=("go", "size")).reset_index()
    s = c[c.speed_kph == 50]
    fig, ax = plt.subplots(figsize=(8, 4.3))
    ax.scatter(g.bin, g.nogo, s=np.sqrt(g.n) * 25, color=C_TRACK, alpha=0.7,
               label=f"test track 2013: share who waited (No-Go), {len(r)} runs, {r.ParticipantNumber.nunique()} drivers; dot size = runs")
    ax.plot(s.pet, s.p, "o-", color=C_REAL, label="video: share who would intervene (1548 answers, 43 participants)")
    ax.axvline(obs["track"], color=C_TRACK, ls="--", lw=1, label=f"track boundary {obs['track']:.2f} s")
    ax.axvline(obs["first"], color=C_REAL, ls="--", lw=1, label=f"video boundary {obs['first']:.2f} s (first exposure)")
    ax.set(xlabel="PET [s] (SetPET on the track, design PET on video)", ylabel="share not turning / intervening",
           ylim=(-0.03, 1.03), title="Left turn at 50 km/h: the video reproduces the test track")
    ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "fig9_ltap_track_video.png", dpi=140)
    plt.close(fig)
    return len(r), r.ParticipantNumber.nunique()


def fig_gain(c, obs, k):
    s = c[c.speed_kph == 50].sort_values("pet")
    pet = s.pet.to_numpy(float)
    r, rdot, W = (s[x].to_numpy(float) for x in ("range_ego_onc", "range_rate", "w_onc"))
    crit = {"egocentric distance": (np.log(r), -1.0), "distance to the conflict point": (np.log(s.d_onc.to_numpy(float)), -1.0),
            "looming at the eye": (np.log(D.looming(r, rdot, W)), 1.0)}
    ks = np.linspace(0.2, 1.3, 111)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    keff = {}
    for (name, (lx, e)), ls in zip(crit.items(), ("-", "--", ":")):
        target = DT2.at_pet(pet, lx, obs["track"])
        pred = [DT2.interp_pet(pet, lx + e * np.log(kk), target) for kk in ks]
        ax.plot(ks, pred, ls, lw=2, label=f"shared {name}")
        keff[name] = {w: float(np.exp((target - DT2.at_pet(pet, lx, obs[w])) / e)) for w in ("first", "pooled")}
    ax.axhline(obs["track"], color="grey", lw=0.8, label="shared time to arrival (any gain)")
    ax.axhspan(obs["first"] - 1.96 * obs["first_se"], obs["first"] + 1.96 * obs["first_se"], color=C_REAL, alpha=0.15,
               label=f"observed video boundary, first exposure {obs['first']:.2f} s (95%)")
    ax.axhline(obs["pooled"], color=C_REAL, lw=0.8, ls="-.", label=f"observed, pooled {obs['pooled']:.2f} s")
    ax.axvline(k, color=C_PART, lw=1)
    ax.text(k + 0.01, -2.3, f"the geometric\nshrinking k = {k:.2f}", color=C_PART, fontsize=8)
    ax.axvline(1.0, color="k", lw=0.8)
    ax.text(1.01, -2.3, "no shrinking", fontsize=8)
    ax.set(xlabel="display gain acting on the participants' criterion", ylabel="predicted video boundary [s of PET]",
           ylim=(-2.6, 4.6), title="Which display gain makes video and track agree? About 1, not 0.42")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "fig10_ltap_gain.png", dpi=140)
    plt.close(fig)
    lo = np.exp(DT2.at_pet(pet, np.log(D.looming(r, rdot, W)), obs["track"]))
    return keff, lo


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    g = D.load_geometry()
    k = D.gain(g)
    obs = DT2.read_observed()
    c = stimuli()
    f = camera_frame()
    oi, y_onc, x_exit, conf = fig_scene(f, k)
    views = fig_views(f, k, oi, y_onc, x_exit, conf)
    fig_video_evidence(c)
    n_runs, n_drv = fig_track_video(c, obs)
    keff, loom_track = fig_gain(c, obs, k)
    L = ["# Numbers quoted beside the left-turn figures (display transform)", "",
         "Generated by `replication/czb/dt_ltap_media.py`. Do not edit by hand.", "",
         f"Gain k = {k:.4f}. Track comfort runs {n_runs}, drivers {n_drv}.", "",
         "Effective gain that reconciles track and video (point estimate):", "",
         "| criterion | with the first-exposure video boundary | with the pooled video boundary |", "|---|---|---|"]
    for name, v in keff.items():
        L.append(f"| {name} | {v['first']:.2f} | {v['pooled']:.2f} |")
    L += ["", f"Looming of the oncoming car at the ego's eye at the track boundary: {loom_track:.4f} rad/s on the"
          f" track (real optics); on the monitor at the same moment {loom_track * k:.4f} rad/s (x k). The released"
          f" model's looming-detection threshold (card PT.1's constant): {P1.MODEL_DETECTION} rad/s.", "",
          f"Views at the decision moment (design PET 2.5 s, 50 km/h; oncoming {np.hypot(*oi):.1f} m ahead):"
          f" the car is {views[1.0][0]:.2f} deg wide at {views[1.0][1]:.2f} deg left for a driver, {views[k][0]:.2f}"
          f" deg wide at {views[k][1]:.2f} deg left on the monitor; the conflict point at {views[1.0][2]:.2f} and"
          f" {views[k][2]:.2f} deg. Ratio car direction / conflict-point direction: {views[1.0][1] / views[1.0][2]:.3f}"
          f" (driver), {views[k][1] / views[k][2]:.3f} (monitor).", ""]
    NUM.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
