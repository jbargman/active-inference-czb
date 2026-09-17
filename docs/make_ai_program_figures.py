"""Generate the schematic figures for `docs/active_inference_program.md`.

    python docs/make_ai_program_figures.py

Everything lands in docs/ai_program_figures/. All eight figures are schematics that
illustrate a construction or an argument; none carries a number from an analysis.
Where a curve is drawn it is computed from illustrative constants declared in the
function that draws it, and the document says so at the point of use.

Palette follows docs/make_ai_scope_figures.py and docs/handbook/make_diagrams.py so the
figure sets read as one.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

HERE = Path(__file__).resolve().parent
FIGS = HERE / "ai_program_figures"
FIGS.mkdir(exist_ok=True)

INK = "#222222"
PURPLE = "#472CBE"
BLUE = "#36B7F6"
TEAL = "#2BAE9A"
PINK = "#C95B9B"
GREY = "#6B7280"
BEIGE = "#F0EDE6"
PAPER = "#FBFAF7"
ORANGE = "#E08A2E"

HAVE = TEAL      # present in the current comfort-zone model
PART = ORANGE    # present in part, or present but hand-set
MISS = PINK      # absent from the current model


def _fig(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def box(ax, x, y, w, h, title, sub, color, fill="white", ls="-", title_size=10.0,
        sub_size=8.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                facecolor=fill, edgecolor=color, linewidth=1.7,
                                linestyle=ls))
    if sub:
        ax.text(x + w / 2, y + h - 0.20, title, ha="center", va="top",
                fontsize=title_size, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 0.52, sub, ha="center", va="top",
                fontsize=sub_size, color=GREY, linespacing=1.3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=INK)


def arrow(ax, xy0, xy1, color=INK, lw=1.6, rad=0.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle=style, mutation_scale=13,
                                 lw=lw, color=color,
                                 connectionstyle="arc3,rad={}".format(rad)))


def car(ax, x, y, w, h, color, alpha=1.0, zorder=3):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.02", facecolor=color,
                                edgecolor=INK, linewidth=0.8, alpha=alpha,
                                zorder=zorder))


# ---------------------------------------------------------------------------
# 1. The stack against the current model, and which of JJ's points each row serves
# ---------------------------------------------------------------------------
def fig_stack_gap():
    rows = [
        ("Generative model of others",
         "how the other road user will move; the norms live here",
         PART, "a 3 s constant-rate lateral projection, one scenario", "1 2 4 5"),
        ("Beliefs and uncertainty",
         "a spread of hypotheses about the present, updated by evidence",
         MISS, "a point value read off the scene", "3 4"),
        ("Rollout of the ego's own policies",
         "what happens if I keep going, ease off, brake, steer",
         MISS, "none; the axis is pointwise", "1 2"),
        ("Preferences  p(o)",
         "how my drive is supposed to go, as a distribution",
         PART, "a per-driver level on one axis; the field was falsified as axis", "1 5"),
        ("Expected free energy over policies",
         "pragmatic shortfall plus ambiguity, minus information gain",
         MISS, "none", "1 3"),
        ("Epistemic value",
         "acting to see better: easing off, looking, waiting",
         MISS, "none", "3"),
        ("Evidence accumulation, re-planning",
         "response timing from accumulated shortfall",
         PART, "tested as specified and rejected (R.1); untested on a rollout quantity",
         "1"),
        ("Learning from data",
         "norms, predictors, preferences fitted to how people drive",
         MISS, "none; the norm geometry is hand-drawn", "5 6"),
        ("Interaction between agents",
         "the other reacts to me; joint futures",
         MISS, "none; the video stimuli are scripted", "2"),
    ]
    n = len(rows)
    H = 0.98 * n + 2.3
    fig, ax = _fig(13.2, H)
    x0, w = 0.35, 5.6
    xs, ws = 6.25, 5.0
    xj, wj = 11.5, 1.35

    ax.text(x0, H - 0.42, "WHAT ACTIVE INFERENCE OFFERS", fontsize=11.5,
            fontweight="bold", color=INK, va="center")
    ax.text(xs, H - 0.42, "WHAT THE COMFORT-ZONE MODEL HAS TODAY", fontsize=11.5,
            fontweight="bold", color=INK, va="center")
    ax.text(xs, H - 0.82, "share who intervene = lapse + (1 - lapse) x gate x Phi((axis - level) / spread)",
            fontsize=8.4, color=GREY, va="center", family="monospace")
    ax.text(xj + wj / 2, H - 0.55, "JJ's\npoints", ha="center", va="center",
            fontsize=9.0, fontweight="bold", color=INK, linespacing=1.3)

    for i, (title, sub, status, have, pts) in enumerate(rows):
        y = H - 1.30 - (i + 1) * 0.98
        box(ax, x0, y, w, 0.86, title, sub, status, title_size=9.4, sub_size=7.7)
        ax.add_patch(FancyBboxPatch((xs, y), ws, 0.86, boxstyle="round,pad=0.05",
                                    facecolor=PAPER, edgecolor=status, linewidth=1.4))
        ax.text(xs + ws / 2, y + 0.43, have, ha="center", va="center", fontsize=8.0,
                color=INK, wrap=True)
        ax.text(xj + wj / 2, y + 0.43, pts, ha="center", va="center", fontsize=9.5,
                color=PURPLE, fontweight="bold")

    leg = [(HAVE, "present"), (PART, "present in part, or hand-set"), (MISS, "absent")]
    for k, (c, lab) in enumerate(leg):
        xx = 0.35 + k * 3.1
        ax.add_patch(Rectangle((xx, 0.32), 0.32, 0.26, facecolor=c, edgecolor=c))
        ax.text(xx + 0.45, 0.45, lab, va="center", fontsize=8.4, color=INK)
    ax.text(9.9, 0.45, "Points: 1 rollouts  2 joint futures  3 uncertainty  4 cut-in probability  5 norms  6 data-driven",
            va="center", fontsize=7.6, color=GREY, ha="left")
    fig.tight_layout()
    fig.savefig(FIGS / "stack_gap.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Point 1: rollouts of the ego's own policies against the other's futures
# ---------------------------------------------------------------------------
def fig_rollouts():
    """Illustrative constants only: a cut-in seen from above, and EFE curves that are
    hand-shaped logistic functions of time. Nothing here is a fitted quantity."""
    fig = plt.figure(figsize=(12.6, 5.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.25)
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor("white")
    ax.set_xlim(-2, 60)
    ax.set_ylim(-4.2, 4.2)
    ax.set_yticks([])
    ax.set_xlabel("distance ahead of the ego [m]", fontsize=9)
    for yy in (-1.85, 1.85):
        ax.axhline(yy, color=GREY, lw=0.8, ls=(0, (6, 4)))
    ax.axhline(-3.7, color=INK, lw=1.2)
    ax.axhline(3.7, color=INK, lw=1.2)
    rng = np.random.default_rng(3)
    t = np.linspace(0, 4, 40)
    # the other vehicle: 25 m ahead in the left lane, drifting toward our lane
    for k in range(40):
        vlat = rng.normal(-0.45, 0.22)
        vlon = rng.normal(2.0, 2.2)
        x = 25 + vlon * t + rng.normal(0, 0.15) * t
        y = 2.4 + vlat * t
        y = np.clip(y, -0.9, 3.3)
        ax.plot(x, y, color=BLUE, lw=0.9, alpha=0.35, zorder=2)
    car(ax, 25, 2.4, 4.2, 1.7, BLUE)
    ax.text(25, 3.45, "the other road user, and where it might be", ha="center",
            fontsize=8.2, color=INK)
    # ego policies
    car(ax, 0, 0, 4.2, 1.7, TEAL)
    ax.text(0, -1.45, "ego", ha="center", va="top", fontsize=8.2, color=INK)
    ax.plot([2, 55], [0, 0], color=TEAL, lw=2.2, zorder=4)
    ax.text(50, 0.5, "continue", color=TEAL, fontsize=8.6, fontweight="bold")
    ax.plot([2, 30], [0, 0], color=ORANGE, lw=2.2, ls="--", zorder=4)
    ax.text(27, -0.9, "brake", color=ORANGE, fontsize=8.6, fontweight="bold")
    xs = np.linspace(2, 52, 30)
    ax.plot(xs, -2.3 * (1 - np.exp(-(xs - 2) / 12)), color=PURPLE, lw=2.2,
            ls=":", zorder=4)
    ax.text(44, -3.3, "steer right", color=PURPLE, fontsize=8.6, fontweight="bold")
    ax.set_title("Roll out each of my policies against the fan of their futures",
                 fontsize=10, color=INK, loc="left")

    ax2 = fig.add_subplot(gs[1])
    tt = np.linspace(0, 4, 200)
    g_cont = 0.3 + 6.0 / (1 + np.exp(-(tt - 2.0) * 2.4))
    g_brake = 1.8 + 0.25 * tt
    g_steer = 2.6 + 0.10 * tt
    ax2.plot(tt, g_cont, color=TEAL, lw=2.4, label="continue")
    ax2.plot(tt, g_brake, color=ORANGE, lw=2.2, ls="--", label="brake")
    ax2.plot(tt, g_steer, color=PURPLE, lw=2.2, ls=":", label="steer right")
    ix = np.argmax(g_cont > g_brake)
    tc = tt[ix]
    ax2.axvline(tc, color=INK, lw=1.0)
    ax2.annotate("comfort-zone boundary:\n'continue' stops being\nthe least-cost policy",
                 xy=(tc, g_brake[ix]), xytext=(tc + 0.25, 5.4), fontsize=8.4,
                 color=INK, arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0))
    ax2.fill_between(tt[:ix], 0, 7.5, color=TEAL, alpha=0.06)
    ax2.text(tc / 2, 7.1, "comfort zone", ha="center", fontsize=8.6, color=TEAL,
             fontweight="bold")
    ax2.set_xlabel("time as the situation develops [s]", fontsize=9)
    ax2.set_ylabel("expected free energy of the policy [nats]", fontsize=9)
    ax2.set_ylim(0, 7.5)
    ax2.set_xlim(0, 4)
    ax2.legend(fontsize=8, loc="lower right", frameon=False)
    ax2.set_title("Choose the policy with the least expected free energy",
                  fontsize=10, color=INK, loc="left")
    for a in (ax, ax2):
        a.tick_params(labelsize=8)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.text(0.01, 0.01,
             "Schematic with illustrative curves. The per-driver level becomes a "
             "threshold on the gap between 'continue' and the best alternative, in nats, "
             "the same unit in every scenario.",
             fontsize=8.0, color=GREY)
    fig.savefig(FIGS / "rollouts.png", dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Point 2: marginal, ego-conditioned and joint prediction
# ---------------------------------------------------------------------------
def fig_joint():
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.0))
    titles = ["Marginal: as if I were not there",
              "Ego-conditioned: my plan, their reply",
              "Joint: the whole scene at once"]
    subs = ["what the released model does (scripted other);\nwhat a frozen video can show",
            "predict others first, then match my rollout\n(Tolstaya et al., 2021)",
            "both agents minimize free energy together\n(Schumann et al., 2026 preprint)"]
    rng = np.random.default_rng(7)
    for k, ax in enumerate(axes):
        ax.set_xlim(-2, 50)
        ax.set_ylim(-4.2, 4.2)
        ax.axis("off")
        for yy in (-1.85, 1.85):
            ax.axhline(yy, color=GREY, lw=0.8, ls=(0, (6, 4)))
        ax.axhline(-3.7, color=INK, lw=1.0)
        ax.axhline(3.7, color=INK, lw=1.0)
        t = np.linspace(0, 4, 40)
        car(ax, 0, 0, 4.2, 1.7, TEAL)
        car(ax, 22, 2.4, 4.2, 1.7, BLUE)
        if k == 0:
            for _ in range(25):
                y = 2.4 + rng.normal(-0.55, 0.3) * t
                x = 22 + rng.normal(2, 2) * t
                ax.plot(x, np.clip(y, -1.4, 3.3), color=BLUE, lw=0.9, alpha=0.35)
            ax.plot([2, 48], [0, 0], color=TEAL, lw=2.2)
        elif k == 1:
            # two ego plans, each with its own reply fan
            for _ in range(14):
                y = 2.4 + rng.normal(-0.75, 0.25) * t
                x = 22 + rng.normal(2, 2) * t
                ax.plot(x, np.clip(y, -1.4, 3.3), color=BLUE, lw=0.9, alpha=0.35)
            for _ in range(14):
                y = 2.4 + rng.normal(-0.15, 0.2) * t
                x = 22 + rng.normal(3, 2) * t
                ax.plot(x, np.clip(y, -1.4, 3.3), color=ORANGE, lw=0.9, alpha=0.35)
            ax.plot([2, 30], [0, 0], color=BLUE, lw=2.2, ls="--")
            ax.text(31, -0.2, "I ease off:\nthey come in", color=BLUE, fontsize=7.8,
                    va="center")
            ax.plot([2, 48], [0.35, 0.35], color=ORANGE, lw=2.2)
            ax.text(36, 1.0, "I hold speed: they wait", color=ORANGE, fontsize=7.8)
        else:
            for _ in range(20):
                vl = rng.normal(-0.5, 0.3)
                y = 2.4 + vl * t
                x = 22 + rng.normal(2, 2) * t
                ax.plot(x, np.clip(y, -1.4, 3.3), color=BLUE, lw=0.9, alpha=0.3)
                # ego's reply in the same sample
                xe = 2 + (11 + 2.0 * vl) * t
                ax.plot(xe, np.zeros_like(t), color=TEAL, lw=0.9, alpha=0.3)
            ax.text(24, -3.2, "each sample couples both agents", color=INK, fontsize=7.8,
                    ha="center")
        ax.set_title(titles[k], fontsize=9.6, color=INK, loc="left")
        ax.text(-2, -5.2, subs[k], fontsize=8.0, color=GREY, va="top", linespacing=1.3)
    fig.subplots_adjust(bottom=0.22, wspace=0.08)
    fig.savefig(FIGS / "joint_vs_conditional.png", dpi=200, facecolor="white",
                bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Point 3: uncertainty makes the conflict probability graded, and sets the spread
# ---------------------------------------------------------------------------
def fig_uncertainty():
    """Illustrative constants: a lateral clearance closing at a constant rate, and two
    assumed uncertainty growth rates. The conflict probability is the Gaussian mass below
    zero clearance at each time. Right panel: psychometric slopes as precision."""
    from scipy.stats import norm
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.9))
    t = np.linspace(0, 3.5, 200)
    l0, ldot = 1.6, -0.6
    mean = l0 + ldot * t
    ax = axes[0]
    for sig1, col, lab in ((0.05, PINK, "almost no uncertainty"),
                           (0.45, BLUE, "uncertainty grows with the horizon")):
        sd = 0.05 + sig1 * t
        ax.fill_between(t, mean - 2 * sd, mean + 2 * sd, color=col, alpha=0.15)
        ax.plot(t, mean, color=INK, lw=1.2)
    ax.axhline(0, color=INK, lw=1.0, ls="--")
    ax.text(0.1, -0.25, "zero clearance: conflict", fontsize=8, color=INK)
    ax.set_xlabel("time ahead [s]", fontsize=9)
    ax.set_ylabel("predicted lateral clearance [m]", fontsize=9)
    ax.set_title("The same projection, two beliefs", fontsize=9.8, loc="left")
    ax.set_ylim(-1.2, 2.6)

    ax = axes[1]
    for sig1, col, lab in ((0.05, PINK, "almost no uncertainty"),
                           (0.45, BLUE, "uncertainty grows with the horizon")):
        sd = 0.05 + sig1 * t
        p = norm.cdf(-mean / sd)
        ax.plot(t, p, color=col, lw=2.2, label=lab)
    ax.set_xlabel("time ahead [s]", fontsize=9)
    ax.set_ylabel("probability of conflict by then", fontsize=9)
    ax.set_title("A step becomes a grade", fontsize=9.8, loc="left")
    ax.legend(fontsize=7.8, frameon=False, loc="upper left")
    ax.set_ylim(0, 1.02)

    ax = axes[2]
    x = np.linspace(-3, 3, 200)
    for s, col, lab in ((0.35, TEAL, "high precision (on the track)"),
                        (1.2, ORANGE, "low precision (frozen video)")):
        ax.plot(x, norm.cdf(x / s), color=col, lw=2.2, label=lab)
    ax.axvline(0, color=GREY, lw=0.8)
    ax.text(0.08, 0.06, "level", fontsize=8, color=GREY)
    ax.set_xlabel("axis minus level (arbitrary units)", fontsize=9)
    ax.set_ylabel("share who intervene", fontsize=9)
    ax.set_title("The spread is a precision", fontsize=9.8, loc="left")
    ax.legend(fontsize=7.8, frameon=False, loc="upper left")
    for a in axes:
        a.tick_params(labelsize=8)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.text(0.01, -0.02,
             "Schematic with illustrative constants. Left and middle: the fitted gate spread "
             "(0.99 m in card G.1) could be a computed quantity, uncertainty about the "
             "lateral rate times the horizon. Right: the four-times-sharper track drivers "
             "read as a precision difference.",
             fontsize=7.9, color=GREY)
    fig.tight_layout()
    fig.savefig(FIGS / "uncertainty.png", dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Point 4: the cut-in probability as a belief about intention
# ---------------------------------------------------------------------------
def fig_cutin_probability():
    """Illustrative constants: a Bayesian ramp on the cut-in hypothesis against the
    released model's trust cap (a step at the lane line) and a fixed-horizon projection."""
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.0), gridspec_kw=dict(width_ratios=[1.2, 1]))
    ax = axes[0]
    t = np.linspace(-2, 3, 300)
    prior = 0.07
    ramp = prior + (1 - prior) / (1 + np.exp(-(t - 0.9) * 3.2))
    ramp[t < 0] = prior
    ax.plot(t, ramp, color=PURPLE, lw=2.4, label="belief that it is changing lanes (Bayesian ramp)")
    step = np.where(t < 1.6, 0.02, 1.0)
    ax.plot(t, step, color=PINK, lw=2.0, ls="--", label="released norm: trust withdrawn at the lane line")
    proj = np.clip(prior + 0.31 * np.clip(t, 0, None) ** 1.6, 0, 1)
    ax.plot(t, proj, color=BLUE, lw=2.0, ls=":", label="fixed-horizon kinematic projection (card G.1)")
    ax.axvline(0, color=GREY, lw=0.9)
    ax.text(0.05, 0.5, "lateral motion\nbegins", fontsize=8, color=GREY)
    ax.axhline(prior, color=GREY, lw=0.7, ls=(0, (2, 3)))
    ax.text(-1.95, prior + 0.03, "prior: this vehicle might cut in", fontsize=8, color=GREY)
    ax.set_xlabel("time from the first lateral motion [s]", fontsize=9)
    ax.set_ylabel("probability of a cut-in", fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7.6, frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.78))
    ax.set_title("Three ways to say 'it is coming'", fontsize=9.8, loc="left")

    ax = axes[1]
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    box(ax, 0.3, 5.9, 9.4, 1.6, "cues that carry intention, not only kinematics",
        "a slower vehicle ahead of it in its own lane; its speed relative to us;\n"
        "the gap we are leaving; the indicator; its position and drift in the lane",
        PURPLE, title_size=9.0, sub_size=7.7)
    box(ax, 0.3, 3.4, 4.4, 1.9, "a norm for lane changing",
        "how often, from where, how fast people\nchange lanes (learned from highD)",
        TEAL, title_size=8.8, sub_size=7.4)
    box(ax, 5.3, 3.4, 4.4, 1.9, "a latent intention in the belief",
        "particles carry 'keeping' or 'changing';\nevidence moves the weights",
        BLUE, title_size=8.8, sub_size=7.4)
    box(ax, 0.3, 0.6, 9.4, 2.0, "the gate becomes a probability that is inferred",
        "pre-onset response = P(cut-in) x consequence; onset independent of the lane change's pace;\n"
        "study 1's pre-onset false alarms already rise with proximity (0.117, 0.071, 0.046 at TTC 4, 6, 8 s)",
        PURPLE, fill=PAPER, title_size=9.0, sub_size=6.9)
    arrow(ax, (5.0, 5.9), (2.5, 5.35), color=GREY)
    arrow(ax, (5.0, 5.9), (7.5, 5.35), color=GREY)
    arrow(ax, (2.5, 3.4), (4.0, 2.65), color=GREY)
    arrow(ax, (7.5, 3.4), (6.0, 2.65), color=GREY)
    for s in ("top", "right"):
        axes[0].spines[s].set_visible(False)
    axes[0].tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(FIGS / "cutin_probability.png", dpi=200, facecolor="white",
                bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Point 5: two normals, and the boundary where they meet
# ---------------------------------------------------------------------------
def fig_two_normals():
    fig, ax = _fig(12.6, 4.6)
    box(ax, 0.4, 2.6, 5.4, 1.45, "MY normal: the preference prior",
        "how my drive is supposed to go: speed, gentle pedals,\n"
        "in my lane, no one too close, no collision.\n"
        "Reference B in the surprise note: the states drivers accept.",
        TEAL, title_size=10.0, sub_size=8.2)
    box(ax, 6.8, 2.6, 5.4, 1.45, "THEIR normal: the norm for others",
        "what that road user will do if it behaves as people do:\n"
        "stays in lane, holds speed, changes lanes at an ordinary pace.\n"
        "Reference A in the surprise note: the predictive model.",
        BLUE, title_size=10.0, sub_size=8.2)
    box(ax, 3.2, 0.4, 6.2, 1.15, "the comfort-zone boundary",
        "where THEIR predicted deviation from their normal, rolled into my future,\n"
        "starts to violate MY normal under my current plan",
        PURPLE, fill=PAPER, title_size=10.0, sub_size=8.2)
    arrow(ax, (3.1, 2.6), (5.2, 1.55), color=TEAL, lw=2.0)
    arrow(ax, (9.5, 2.6), (7.4, 1.55), color=BLUE, lw=2.0)
    ax.text(6.3, 2.1, "both are estimable from naturalistic data (highD, inD)",
            ha="center", fontsize=8.6, color=GREY)
    ax.text(0.4, 4.35, "Two normative models, two jobs, one boundary",
            fontsize=11, fontweight="bold", color=INK, va="center")
    fig.tight_layout()
    fig.savefig(FIGS / "two_normals.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 7. Point 6: learned models, and reading their mechanisms when the answer is known
# ---------------------------------------------------------------------------
def fig_learned_probes():
    fig, ax = _fig(12.8, 5.6)
    ax.text(0.4, 5.3, "Two uses of data-driven models, and one benchmark we can offer",
            fontsize=11, fontweight="bold", color=INK, va="center")
    # Row A: predictor as generative model
    box(ax, 0.4, 3.6, 3.2, 1.25, "naturalistic tracks",
        "highD: 110 000 vehicles\ninD: intersections", GREY, title_size=9.2, sub_size=7.8)
    box(ax, 4.2, 3.6, 3.6, 1.25, "a learned predictor of others",
        "mixture density or small transformer:\nP(future | past, context)", BLUE,
        title_size=9.2, sub_size=7.8)
    box(ax, 8.4, 3.6, 4.0, 1.25, "the generative model for points 1 to 5",
        "the fan the rollouts use; surprise about the world;\ncut-in probability; norms as its content",
        PURPLE, title_size=9.2, sub_size=7.8)
    arrow(ax, (3.6, 4.22), (4.2, 4.22))
    arrow(ax, (7.8, 4.22), (8.4, 4.22))
    # Row B: end-to-end on human judgments, then probe
    box(ax, 0.4, 1.0, 3.2, 1.35, "human judgments",
        "study 2: 10 944 trials, 378 clips;\nthe answer is known: gate x looming",
        GREY, title_size=9.2, sub_size=7.8)
    box(ax, 4.2, 1.0, 3.6, 1.35, "a small network, end to end",
        "raw kinematic trace in,\nshare who intervene out", ORANGE,
        title_size=9.2, sub_size=7.8)
    box(ax, 8.4, 1.0, 4.0, 1.35, "read its mechanism",
        "linear probes for gap, TTC, looming rate, clearance;\n"
        "sparse features; causal patching; symbolic regression",
        TEAL, title_size=9.2, sub_size=7.8)
    arrow(ax, (3.6, 1.67), (4.2, 1.67))
    arrow(ax, (7.8, 1.67), (8.4, 1.67))
    ax.text(10.4, 0.55,
            "Does the toolkit recover W dv / g^2 when we know that is the answer?\n"
            "A benchmark for the interpretability work on large driving models.",
            ha="center", fontsize=8.2, color=INK, linespacing=1.35)
    ax.text(0.4, 5.0, "A. the data-driven part of an active-inference agent",
            fontsize=9.2, color=INK, fontweight="bold")
    ax.text(0.4, 2.55, "B. the data-driven model of the human, opened up", fontsize=9.2,
            color=INK, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "learned_probes.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 8. The program: cards, phases and dependencies
# ---------------------------------------------------------------------------
def fig_program():
    fig, ax = _fig(13.0, 7.6)
    ax.text(0.4, 7.25, "The program in cards: what can start now, what waits for data",
            fontsize=11, fontweight="bold", color=INK, va="center")
    cols = [("Phase 0: data in hand", 0.4, TEAL),
            ("Phase 1: on highD / inD access", 4.7, BLUE),
            ("Phase 2: learned models, interpretability", 9.0, ORANGE)]
    for lab, x, c in cols:
        ax.text(x + 1.9, 6.85, lab, ha="center", fontsize=9.6, fontweight="bold", color=c)
    cards0 = [("JJ.1  design note", "the rollout formulation of the boundary;\npolicy menu, predictor, dG, pre-stated rules"),
              ("JJ.2  rollouts on the cut-in", "study 2; emergent gate and axis in nats;\nagainst looming 0.113 and G.1's CP1 0.032"),
              ("JJ.3  transfer in nats", "left turn (own planned path) and overtake;\none level, no EL.Q4 rescaling"),
              ("JJ.4  precision as spread", "spread against perceptual uncertainty:\ntruck vs car, video vs track; derive s_l")]
    cards1 = [("JJ.5  norms from data", "lane keeping, lane-change kinematics,\nfollowing; replaces hand-set values"),
              ("JJ.6  cut-in probability", "fit on highD; plug in as the gate on\nstudy 2; then inside the rollouts"),
              ("JJ.7  learned predictor", "mixture density / small transformer;\nsurprise with a real reference (Q5.1)"),
              ("JJ.8  interactivity", "conditional vs marginal prediction on\nhighD cut-ins and inD turns")]
    cards2 = [("JJ.9  known-mechanism benchmark", "small net on study 2; probes, sparse\nfeatures, patching, symbolic regression"),
              ("JJ.10  LLM as judge", "zero-shot 'would you intervene' on\nstudy-2 cells; exploratory; data-sharing query"),
              ("later: epistemic value, sophistication", "E.2 on the truck cut-in; waiting to see;\nthe joint two-agent model on inD")]
    for k, (cards, (lab, x, c)) in enumerate(zip((cards0, cards1, cards2), cols)):
        for i, (t, s) in enumerate(cards):
            y = 5.3 - i * 1.42
            box(ax, x, y, 3.8, 1.22, t, s, c, title_size=8.9, sub_size=7.5)
    # dependencies
    arrow(ax, (2.3, 5.30), (2.3, 5.12), color=TEAL)             # JJ.1 -> JJ.2
    arrow(ax, (2.3, 3.88), (2.3, 3.70), color=TEAL)             # JJ.2 -> JJ.3
    arrow(ax, (6.6, 5.30), (6.6, 5.12), color=BLUE)             # JJ.5 -> JJ.6
    arrow(ax, (4.2, 4.49), (4.7, 4.49), color=GREY)             # JJ.2 -> JJ.6
    arrow(ax, (4.2, 3.07), (4.7, 3.07), color=GREY)             # JJ.3 -> JJ.7 (the axis to predict)
    arrow(ax, (8.5, 3.07), (8.5, 3.85), color=BLUE, rad=0.3)    # JJ.7 -> JJ.6
    ax.text(0.4, 0.55,
            "Arrows: what a card needs from another. JJ.1 to JJ.4 need nothing that is not on disk. "
            "JJ.9 can start now in parallel. Nothing starts before Jonas names it.",
            fontsize=8.2, color=GREY)
    fig.tight_layout()
    fig.savefig(FIGS / "program.png", dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_stack_gap()
    fig_rollouts()
    fig_joint()
    fig_uncertainty()
    fig_cutin_probability()
    fig_two_normals()
    fig_learned_probes()
    fig_program()
    print("wrote:", *(p.name for p in sorted(FIGS.glob("*.png"))))
