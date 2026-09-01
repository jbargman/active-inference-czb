"""Animate one rear-end event from the authors' own deposited simulation output.

    python presentation/talk/make_event_animation.py

Source: the OSF deposit, rear-end scenario, Exp_7 (10 m/s, 1.0 s initial time
gap), random seed 0 — the trial chapter 02 of the handbook walks through. Nothing
here is sketched: the vehicle states, the executed pedal, the per-step surprise
deposit and the re-plan flag are all read from the deposited arrays, and the
accumulator is reconstructed with the run's own lambda (EA_fac = -5.95, so
lambda = 10^-5.95) and re-plan threshold of 1.

Outputs, into presentation/talk/figures/:
    event_anim.gif      the animation for the slide (PowerPoint plays GIFs in
                        slideshow mode)
    event_static.png    the same event as a static landscape figure, for the
                        printed deck and as a fallback

The deposit's own axis order for the policy arrays is (H, T, S, 2); the README's
(H, S, T, 2) does not match the data (docs/method_review.md).
"""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIGS = HERE / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

PKL = (REPO / "external" / "gs4bu-osfstorage-archive" / "Results_rear_end"
       / "Results_rear_end" / "Exp_7" / "Exp_7.pkl")

SEED = 0
DT = 0.2
LAMBDA = 10.0 ** -5.95        # EA_fac in Setups_rear_end.xlsx row 7
THRESHOLD = 1.0
CAR_LEN = 4.2                 # lf + lr
CAR_WID = 1.72                # d
LANE_W = 3.65

INK = "#222222"
PURPLE = "#472CBE"
BLUE = "#36B7F6"
TEAL = "#2BAE9A"
PINK = "#C95B9B"
GREY = "#6B7280"
BEIGE = "#F0EDE6"
ROAD = "#E8E6E0"

N_STEPS = 30                  # 6.0 s of the 12 s run: everything happens here
HOLD_FRAMES = 10              # frames held on the final state before looping


def load_event():
    with open(PKL, "rb") as fh:
        d = pickle.load(fh)
    eta = d["eta"][SEED].astype(float)                 # (T, 14)
    a_exec = d["a_cont"][0, :, SEED, 0].astype(float)  # executed longitudinal accel
    v_init = d["v_init"][SEED].astype(float)           # pragmatic value, incumbent plan
    replan = (np.abs(d["a_cont"] - d["a_cont_init"]) > 1e-5).any(axis=(0, 3)).T[SEED]

    # eps_t of Eq. 13: the negative sum of the first seven pragmatic components,
    # each normalized so that its maximum is zero (docs/method_review.md 4.2).
    eps = -v_init[:, :7].sum(axis=1)

    acc, evidence = 0.0, []
    for t in range(len(eps)):
        acc += LAMBDA * eps[t]
        evidence.append(acc)
        if acc >= THRESHOLD:
            acc = 0.0
    evidence = np.array(evidence)

    t = np.arange(len(eps)) * DT
    return {
        "t": t[:N_STEPS],
        "x_ego": eta[:N_STEPS, 0],
        "v_ego": eta[:N_STEPS, 4],
        "x_tar": eta[:N_STEPS, 5],
        "v_tar": eta[:N_STEPS, 9],
        "a_tar": eta[:N_STEPS, 10],
        "a_exec": a_exec[:N_STEPS],
        "eps": eps[:N_STEPS],
        "E": evidence[:N_STEPS],
        "replan": replan[:N_STEPS],
    }


def phase_text(ev, k):
    t = ev["t"][k]
    if t < 0.8:
        return ("Steady following", "10 m/s, 10 m gap - one second of headway. "
                "The plan is 'keep cruising'.")
    if t < 1.4:
        return ("The lead brakes at 6 m/s²",
                "The belief cloud caught it in one step. The plan has not changed - "
                "evidence is building that it should.")
    if t < 1.6:
        return ("Evidence full → one full re-plan",
                "The accumulator crosses its threshold. The planner runs once, "
                "and picks braking.")
    if ev["v_ego"][k] > 0.05:
        return ("Braking, 0.8 s after the lead",
                "Detection took one 0.2 s step. Everything else was evidence "
                "accumulation, not slow senses.")
    return ("Stopped, 2.05 m behind",
            "One mechanism produced the whole episode - no per-phase sub-model.")


def draw_car(ax, x, y, color, edge, label=None, brake=False):
    """Draw one vehicle; return every artist so the frame can be torn down."""
    made = []
    body = Rectangle((x - CAR_LEN / 2, y - CAR_WID / 2), CAR_LEN, CAR_WID,
                     facecolor=color, edgecolor=edge, linewidth=1.8, zorder=4)
    ax.add_patch(body)
    made.append(body)
    if brake:
        lamp = Rectangle((x - CAR_LEN / 2 - 0.30, y - CAR_WID / 2), 0.30,
                         CAR_WID, facecolor="#E03131", edgecolor="none",
                         zorder=5)
        ax.add_patch(lamp)
        made.append(lamp)
    if label:
        made.append(ax.text(x, y + CAR_WID / 2 + 0.35, label, ha="center",
                            va="bottom", fontsize=11.5, color=edge,
                            fontweight="bold", zorder=6))
    return made


def build_axes(ev):
    fig = plt.figure(figsize=(13.0, 6.4), dpi=110)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(3, 2, height_ratios=[0.40, 1.30, 1.30],
                          left=0.065, right=0.975, top=0.96, bottom=0.10,
                          hspace=0.52, wspace=0.22)

    ax_head = fig.add_subplot(gs[0, :])
    ax_head.axis("off")

    ax_road = fig.add_subplot(gs[1, :])
    ax_road.set_xlim(-3, 40)
    ax_road.set_ylim(-4.4, 3.0)
    ax_road.set_yticks([])
    ax_road.set_xlabel("distance along the road [m]", fontsize=12)
    ax_road.tick_params(labelsize=11)
    ax_road.add_patch(Rectangle((-3, -LANE_W / 2), 43, LANE_W, facecolor=ROAD,
                                edgecolor="none", zorder=0))
    ax_road.axhline(LANE_W / 2, color="#B9B5AC", lw=2, zorder=1)
    ax_road.axhline(-LANE_W / 2, color="#B9B5AC", lw=2, zorder=1)
    for spine in ("top", "right", "left"):
        ax_road.spines[spine].set_visible(False)

    ax_speed = fig.add_subplot(gs[2, 0])
    ax_speed.set_xlim(0, ev["t"][-1])
    ax_speed.set_ylim(-0.6, 11.5)
    ax_speed.set_xlabel("time [s]", fontsize=12)
    ax_speed.set_ylabel("speed [m/s]", fontsize=12)
    ax_speed.tick_params(labelsize=11)
    ax_speed.grid(alpha=0.25)
    for spine in ("top", "right"):
        ax_speed.spines[spine].set_visible(False)

    ax_acc = fig.add_subplot(gs[2, 1])
    ax_acc.set_xlim(0, ev["t"][-1])
    ax_acc.set_ylim(0, 1.32)
    ax_acc.set_xlabel("time [s]", fontsize=12)
    ax_acc.set_ylabel("accumulated surprise", fontsize=12)
    ax_acc.tick_params(labelsize=11)
    ax_acc.grid(alpha=0.25)
    ax_acc.axhline(1.0, color=PINK, lw=2, ls="--")
    ax_acc.text(ev["t"][-1], 1.06, "re-plan threshold", color=PINK, fontsize=11.5,
                fontweight="bold", ha="right")
    for spine in ("top", "right"):
        ax_acc.spines[spine].set_visible(False)

    return fig, ax_head, ax_road, ax_speed, ax_acc


def render(ev, ax_head, ax_road, ax_speed, ax_acc, k):
    for ax in (ax_head, ax_road, ax_speed, ax_acc):
        for artist in list(getattr(ax, "_dyn", [])):
            artist.remove()
        ax._dyn = []

    title, sub = phase_text(ev, k)
    ax_head._dyn.append(ax_head.text(
        0.0, 0.92, "t = {:.1f} s   —   {}".format(ev["t"][k], title),
        transform=ax_head.transAxes, ha="left", va="top", fontsize=17,
        fontweight="bold", color=PURPLE))
    ax_head._dyn.append(ax_head.text(
        0.0, 0.30, sub, transform=ax_head.transAxes, ha="left", va="top",
        fontsize=13, color=INK))

    # --- the road ---------------------------------------------------------
    xe, xt = ev["x_ego"][k], ev["x_tar"][k]
    ax_road._dyn.extend(draw_car(ax_road, xt, 0, "#FFFFFF", INK, "lead vehicle",
                                 brake=ev["a_tar"][k] < -0.1))
    ax_road._dyn.extend(draw_car(ax_road, xe, 0, "#DCD6F7", PURPLE,
                                 "the driver model",
                                 brake=(ev["a_exec"][k] < -1.0
                                        and ev["v_ego"][k] > 0.1)))
    gap = xt - xe - CAR_LEN
    ax_road._dyn.append(ax_road.annotate(
        "", xy=(xe + CAR_LEN / 2, -2.5), xytext=(xt - CAR_LEN / 2, -2.5),
        arrowprops=dict(arrowstyle="<|-|>", color=TEAL, lw=2.5,
                        mutation_scale=18)))
    gap_label = ("gap {:.2f} m   ({:.2f} s headway)".format(
        gap, gap / ev["v_ego"][k]) if ev["v_ego"][k] > 0.2
        else "gap {:.2f} m".format(gap))
    ax_road._dyn.append(ax_road.text(
        (xe + xt) / 2, -3.5, gap_label, ha="center", va="center", fontsize=12.5,
        color=TEAL, fontweight="bold"))

    # --- speeds -----------------------------------------------------------
    sl = slice(0, k + 1)
    ax_speed._dyn.extend(ax_speed.plot(ev["t"][sl], ev["v_tar"][sl], color=INK,
                                       lw=2.4, ls="--", label="lead vehicle"))
    ax_speed._dyn.extend(ax_speed.plot(ev["t"][sl], ev["v_ego"][sl], color=PURPLE,
                                       lw=2.8, label="the driver model"))
    if k == 0:
        ax_speed.legend(loc="lower left", fontsize=11, frameon=False)

    # --- the accumulator --------------------------------------------------
    ax_acc._dyn.append(ax_acc.bar(ev["t"][sl], ev["E"][sl], width=DT * 0.85,
                                  color=BLUE, edgecolor="none"))
    if ev["t"][k] >= 1.4:
        ax_acc._dyn.append(ax_acc.axvline(1.4, color=PINK, lw=2))
        ax_acc._dyn.append(ax_acc.text(1.48, 0.72, "re-plan", color=PINK,
                                       fontsize=12, fontweight="bold"))
    if ev["t"][k] >= 1.6:
        ax_acc._dyn.append(ax_acc.axvline(1.6, color=PURPLE, lw=2, ls=":"))
        ax_acc._dyn.append(ax_acc.text(1.70, 0.48, "brake", color=PURPLE,
                                       fontsize=12, fontweight="bold"))
    if ev["t"][k] >= 0.8:
        ax_acc._dyn.append(ax_acc.axvline(0.8, color=GREY, lw=1.6, ls=":"))
        ax_acc._dyn.append(ax_acc.text(0.72, 0.80, "lead brakes", color=GREY,
                                       fontsize=11, ha="right"))


def main() -> None:
    ev = load_event()
    fig, ax_head, ax_road, ax_speed, ax_acc = build_axes(ev)
    for ax in (ax_head, ax_road, ax_speed, ax_acc):
        ax._dyn = []

    order = list(range(N_STEPS)) + [N_STEPS - 1] * HOLD_FRAMES

    def frame(i):
        render(ev, ax_head, ax_road, ax_speed, ax_acc, order[i])
        return []

    anim = FuncAnimation(fig, frame, frames=len(order), interval=280, blit=False)
    out_gif = FIGS / "event_anim.gif"
    anim.save(str(out_gif), writer=PillowWriter(fps=4))
    print("wrote", out_gif)

    render(ev, ax_head, ax_road, ax_speed, ax_acc, N_STEPS - 1)
    fig.savefig(FIGS / "event_static.png", dpi=170, facecolor="white")
    print("wrote", FIGS / "event_static.png")

    # One mid-event frame, for checking the animation without opening the GIF
    # and as the poster image on the animated slide.
    render(ev, ax_head, ax_road, ax_speed, ax_acc, 7)
    fig.savefig(FIGS / "event_frame_replan.png", dpi=170, facecolor="white")
    print("wrote", FIGS / "event_frame_replan.png")

    print("checks: brake onset t = {:.1f} s, re-plan at t = {:.1f} s, "
          "final gap {:.2f} m".format(
              ev["t"][int(np.argmax(ev["a_exec"] <= -1.0))],
              ev["t"][int(np.argmax(ev["replan"]))],
              ev["x_tar"][-1] - ev["x_ego"][-1] - CAR_LEN))


if __name__ == "__main__":
    main()
