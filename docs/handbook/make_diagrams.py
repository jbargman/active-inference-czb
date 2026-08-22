"""Generate the handbook's diagrams and data figures.

    python docs/handbook/make_diagrams.py

Everything lands in docs/handbook/figures/. Regenerate after changing this
script; chapters reference the files by name. The walkthrough figures are drawn
from the authors' own simulation output (OSF deposit), experiment Exp_7 seed 0
of the rear-end scenario — chosen in notes/TODO_understanding_pack.md.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)

OSF_EXP = (REPO / "external" / "gs4bu-osfstorage-archive" / "Results_rear_end"
           / "Results_rear_end" / "Exp_7" / "Exp_7.pkl")
SEED = 0
DT = 0.2

INK = "#222222"
PURPLE = "#472CBE"
BLUE = "#36B7F6"
TEAL = "#2BAe9A"
PINK = "#C95B9B"
GREY = "#6B7280"
BEIGE = "#F0EDE6"


# ---------------------------------------------------------------------------
# 1. The perception-action loop
# ---------------------------------------------------------------------------

def box(ax, x, y, w, h, title, sub, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                facecolor="white", edgecolor=color, linewidth=1.8))
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top",
            fontsize=10.5, fontweight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.62, sub, ha="center", va="top",
            fontsize=8.2, color=GREY, linespacing=1.25)


def arrow(ax, xy0, xy1, color=INK, style="-|>", lw=1.6, rad=0.0, label=None,
          label_offset=(0, 0.14), fontsize=8.5):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle=style, mutation_scale=14,
                                 lw=lw, color=color,
                                 connectionstyle="arc3,rad={}".format(rad)))
    if label:
        mx, my = (xy0[0] + xy1[0]) / 2 + label_offset[0], (xy0[1] + xy1[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", fontsize=fontsize, color=color)


def loop_diagram():
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 5.6)
    ax.axis("off")

    # world strip
    ax.add_patch(FancyBboxPatch((0.25, 4.55), 11.0, 0.85, boxstyle="round,pad=0.05",
                                facecolor=BEIGE, edgecolor="none"))
    ax.text(0.55, 4.97, "THE WORLD", fontsize=10, fontweight="bold", color=INK, va="center")
    ax.text(3.1, 4.97, "the two vehicles, the road — and the other vehicle's scripted behavior",
            fontsize=8.5, color=GREY, va="center")

    boxes = [
        (0.45, 2.7, 2.0, 1.3, "SENSE", "optical angles and\ntheir rates (looming),\nnot meters and m/s", BLUE),
        (2.95, 2.7, 2.0, 1.3, "BELIEVE", "a cloud of 75\nhypotheses about the\nstate of the world", PURPLE),
        (5.45, 2.7, 2.0, 1.3, "PREDICT", "roll each hypothesis\nforward 6 s, biased\ntoward norm-following", TEAL),
        (7.95, 2.7, 1.9, 1.3, "EVALUATE", "score candidate plans\nagainst the preferred\nfuture, pick the best", PINK),
        (10.25, 2.7, 1.1, 1.3, "ACT", "execute the\nfirst step of\nthe kept plan", INK),
    ]
    for b in boxes:
        box(ax, *b)

    arrow(ax, (1.45, 4.5), (1.45, 4.06), color=BLUE)          # world -> sense
    arrow(ax, (2.45, 3.35), (2.95, 3.35), color=INK)
    arrow(ax, (4.95, 3.35), (5.45, 3.35), color=INK)
    arrow(ax, (7.45, 3.35), (7.95, 3.35), color=INK)
    arrow(ax, (9.85, 3.35), (10.25, 3.35), color=INK)
    arrow(ax, (10.8, 4.06), (10.8, 4.5), color=INK)            # act -> world

    # surprise gate underneath
    ax.add_patch(FancyBboxPatch((3.6, 0.55), 4.6, 1.15, boxstyle="round,pad=0.06",
                                facecolor="white", edgecolor=PURPLE, linewidth=1.8,
                                linestyle="--"))
    ax.text(5.9, 1.48, "THE SURPRISE ACCUMULATOR", ha="center", fontsize=10,
            fontweight="bold", color=PURPLE)
    ax.text(5.9, 1.12, "each step, add how far the current plan now falls short of the preferred future;\n"
                       "while the plan still works this is exactly zero — when the total crosses threshold: re-plan",
            ha="center", fontsize=8.2, color=GREY, linespacing=1.3)

    arrow(ax, (8.6, 2.65), (7.6, 1.75), color=PURPLE, rad=-0.25)
    arrow(ax, (4.2, 1.75), (3.6, 2.65), color=PURPLE, rad=-0.25,
          label="re-plan when\nthreshold crossed", label_offset=(-1.25, -0.1))

    fig.tight_layout()
    fig.savefig(FIGS / "loop.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. The walkthrough figure (real data, Exp_7 seed 0)
# ---------------------------------------------------------------------------

def walkthrough():
    with open(OSF_EXP, "rb") as f:
        d = pickle.load(f)
    s = SEED
    eta = d["eta"][s].astype(float)
    a_exec = d["a_cont"][0, :, s, 0].astype(float)
    replan = (np.abs(d["a_cont"][:, :, s, :] - d["a_cont_init"][:, :, s, :]) > 1e-5).any(axis=(0, 2))
    T = min(30, eta.shape[0])
    t = np.arange(T) * DT
    gap = eta[:T, 5] - eta[:T, 0] - 4.2

    lead_on = 0.8
    replan_t = float(np.flatnonzero(replan[:T])[0] * DT)
    brake_t = float(np.flatnonzero((a_exec[:T] <= -1.0) & (t >= lead_on))[0] * DT)

    fig, axes = plt.subplots(4, 1, figsize=(8.6, 8.6), sharex=True)

    def moments(ax):
        for x, c, in [(lead_on, GREY), (replan_t, PURPLE), (brake_t, PINK)]:
            ax.axvline(x, color=c, lw=1.1, ls=":" if x == lead_on else "--", alpha=0.85)

    ax = axes[0]
    ax.plot(t, eta[:T, 4], color=BLUE, lw=2, label="our driver (ego)")
    ax.plot(t, eta[:T, 9], color=INK, lw=2, ls="--", label="lead vehicle")
    ax.set_ylabel("speed [m/s]")
    ax.legend(fontsize=8, loc="lower left")
    moments(ax)

    ax = axes[1]
    ax.plot(t, gap, color=TEAL, lw=2)
    ax.set_ylabel("gap [m]")
    ax.set_ylim(0, 11)
    moments(ax)

    ax = axes[2]
    ax.plot(t, eta[:T, 10], color=INK, lw=2, ls="--", label="lead's actual braking")
    ax.plot(t, a_exec[:T], color=BLUE, lw=2, label="our driver's executed pedal")
    ax.set_ylabel("acceleration [m/s²]")
    ax.legend(fontsize=8, loc="lower right")
    moments(ax)

    ax = axes[3]
    ax.step(t, replan[:T].astype(int), where="post", color=PURPLE, lw=2)
    ax.set_ylabel("full re-plan")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["no", "YES"])
    ax.set_xlabel("time [s]")
    moments(ax)

    for x, lab, c, dy in [(lead_on, "lead starts braking", GREY, 0),
                          (replan_t, "surprise crosses threshold → re-plan", PURPLE, 1),
                          (brake_t, "brake reaches the wheels", PINK, 2)]:
        axes[1].annotate(lab, xy=(x, 10.6 - dy * 1.35), xytext=(x + 0.1, 10.6 - dy * 1.35),
                         fontsize=7.8, color=c, va="top", annotation_clip=False)

    fig.suptitle("One rear-end event, from the authors' own simulation output "
                 "(10 m/s, gap 10 m)", fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(FIGS / "walkthrough_event.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. The lineage strip (for chapter 01)
# ---------------------------------------------------------------------------

def lineage():
    fig, ax = plt.subplots(figsize=(11.5, 2.9))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 2.9)
    ax.axis("off")

    steps = [
        ("Unconscious inference", "Helmholtz, 1860s\nperception is a guess\nbuilt from expectations", GREY),
        ("The Bayesian brain", "1990s–2000s\nbeliefs updated by evidence,\nweighted by reliability", BLUE),
        ("Predictive processing", "2000s–2010s\nthe brain runs a prediction\nmachine; driving version:\nGreat expectations (2018)", TEAL),
        ("Active inference", "2010s\nadd action: behave so that\npredictions come true", PURPLE),
        ("This driver model", "Engström 2024, Wei 2024,\nSchumann 2026\ncollision avoidance,\nbenchmarked on humans", PINK),
    ]
    w, gap0 = 2.0, 0.32
    x = 0.25
    for i, (title, sub, c) in enumerate(steps):
        box(ax, x, 0.55, w, 1.85, title, sub, c)
        if i < len(steps) - 1:
            arrow(ax, (x + w + 0.02, 1.5), (x + w + gap0 - 0.02, 1.5), color=INK)
        x += w + gap0

    fig.tight_layout()
    fig.savefig(FIGS / "lineage.png", dpi=200)
    plt.close(fig)





# ---------------------------------------------------------------------------
# 4. The norm tournament (chapter 06) - illustrative reimplementation
# ---------------------------------------------------------------------------

def norm_tournament():
    """Lateral-only reimplementation of dynamics.forward_tar_agent's sampling
    rule, to show the fan with and without the norm bias. Illustrative: real
    geometry factors, simplified dynamics (lateral random walk)."""
    rng = np.random.default_rng(7)
    LANE = 3.65
    D = 1.72
    AW = 0.5 * (LANE - D)         # actual_lane_width half-extent, rear-end style
    WP, FVF = 1e-3, 1e-2
    N_NORM, H_NORM = 32, 20
    SIGMA = 0.12                   # per-step lateral move scale
    STEPS, NTRAJ = 20, 120         # 4 s fans

    def W(y):
        y = np.abs(y)
        w = np.full_like(y, WP * FVF, dtype=float)
        w[y < AW + 0.2 * D] = WP
        w[y < AW] = 1.0
        return w

    def fan(y0, biased):
        trajs = np.zeros((NTRAJ, STEPS + 1))
        trajs[:, 0] = y0
        for i in range(NTRAJ):
            y = y0
            for t in range(STEPS):
                cand = y + SIGMA * rng.standard_normal(N_NORM)
                if biased:
                    w_now = W(np.full(N_NORM, y))
                    w_next = W(cand)
                    w_long = W(y + (cand - y) * H_NORM)
                    w_fut = 2 * w_next * w_long / (w_next + w_long)
                    w = np.minimum(w_now, w_fut)
                    w = w / w.sum()
                    y = rng.choice(cand, p=w)
                else:
                    y = cand[0]
                trajs[i, t + 1] = y
        return trajs

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    t = np.arange(STEPS + 1) * DT
    for ax, y0, title in [
            (axes[0], 0.0, "Compliant target (in lane): the swarm leans normative"),
            (axes[1], AW + 0.35, "Already violating: the fan opens — and leans back toward normal")]:
        for tr in fan(y0, biased=False):
            ax.plot(t, tr, color=GREY, lw=0.5, alpha=0.25)
        for tr in fan(y0, biased=True):
            ax.plot(t, tr, color=PURPLE, lw=0.6, alpha=0.35)
        for edge, c in [(AW, TEAL), (AW + 0.2 * D, PINK)]:
            ax.axhline(edge, color=c, lw=1.0, ls="--")
            ax.axhline(-edge, color=c, lw=1.0, ls="--")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("imagined time ahead [s]")
    axes[0].set_ylabel("other vehicle's lateral position [m]")
    axes[0].set_ylim(-3.2, 3.2)
    from matplotlib.lines import Line2D
    axes[0].legend(handles=[
        Line2D([], [], color=PURPLE, lw=1.5, label="norm-biased sampling (as in the model)"),
        Line2D([], [], color=GREY, lw=1.5, label="raw noise (bias off)"),
        Line2D([], [], color=TEAL, lw=1.2, ls="--", label="lane extent"),
        Line2D([], [], color=PINK, lw=1.2, ls="--", label="marginal band")],
        fontsize=7.5, loc="lower left")
    fig.suptitle("The norm tournament inside each particle's motion "
                 "(illustrative lateral-only reimplementation of the sampling rule)",
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIGS / "norm_tournament.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. The six preference terms (chapter 07)
# ---------------------------------------------------------------------------

def preference_terms():
    import sys
    sys.path.insert(0, str(REPO / "src"))
    from comfortzone.field import critical_gap
    from aidriver import PreferenceParams, BicycleParams

    fig, axes = plt.subplots(2, 3, figsize=(11, 6.2))

    def gauss(ax, mu, sd, lo, hi, xlabel, title, color=PURPLE):
        x = np.linspace(lo, hi, 400)
        ax.plot(x, np.exp(-0.5 * ((x - mu) / sd) ** 2), color=color, lw=2)
        ax.set_xlabel(xlabel)
        ax.set_title(title, fontsize=9.5)
        ax.set_yticks([0, 1])

    gauss(axes[0, 0], 15, 0.5, 12, 18, "speed [m/s]",
          "Speed: near desired (here 15), tight")
    gauss(axes[0, 1], 0, 0.1, -0.6, 0.6, "acceleration [m/s²]",
          "Pedal effort: mostly gentle", BLUE)
    gauss(axes[0, 2], 0, 0.02, -0.12, 0.12, "steering rate [rad/s]",
          "Steering effort: mostly still", BLUE)
    gauss(axes[1, 0], 0.2, 0.125, -0.3, 0.9, "inverse tau [1/s]",
          "Closing rate: shapes everyday headway", TEAL)

    ax = axes[1, 1]
    y = np.linspace(-2.6, 2.6, 500)
    half_in = 0.5 * (3.65 - 1.72)
    tri = np.clip(1 - np.abs(y) / half_in, 0, 1)
    pref = np.where(np.abs(y) <= half_in, 0.15 + 0.85 * tri, 0.02)
    ax.plot(y, pref, color=TEAL, lw=2)
    ax.axvline(half_in, color=PINK, ls="--", lw=1)
    ax.axvline(-half_in, color=PINK, ls="--", lw=1)
    ax.set_xlabel("lateral offset in lane [m]")
    ax.set_title("Lane position: triangular, lane-structured\n(geometry per scenario)",
                 fontsize=9.5)
    ax.set_yticks([0, 1])

    ax = axes[1, 2]
    p = PreferenceParams(v_desired=15.0, vehicle=BicycleParams())
    gaps = np.linspace(2, 60, 400)
    star = float(critical_gap(15.0, 15.0, p, a_required=8.0))
    ax.plot(gaps, np.where(gaps >= star, 1.0, 0.05), color=PINK, lw=2)
    ax.axvline(star, color=INK, ls=":", lw=1)
    ax.text(star + 1, 0.5, "boundary gap\n(closed form)", fontsize=8, color=INK)
    ax.set_xlabel("gap to lead [m]  (15 m/s following)")
    ax.set_title("Safety margin: a counterfactual step\n(collision term not shown)",
                 fontsize=9.5)
    ax.set_yticks([0, 1])

    for ax in axes.flat:
        ax.set_ylabel("preference (relative)", fontsize=8)
    fig.suptitle("The six preference terms — the driver's own 'normal', term by term "
                 "(shapes to scale; parameter values from the shipped configuration)",
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIGS / "preference_terms.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    loop_diagram()
    walkthrough()
    lineage()
    norm_tournament()
    preference_terms()
    print("wrote", ", ".join(p.name for p in sorted(FIGS.glob("*.png"))))
