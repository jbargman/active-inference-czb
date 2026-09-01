"""Figures for the 60-minute active-inference / comfort-zone talk.

    python presentation/talk/make_talk_figures.py

Everything lands in presentation/talk/figures/. These are *talk* versions of
figures that also exist in the handbook and the scope map: bigger type, landscape
aspect ratios that fit a 16:9 slide, and, where the documents have since been
corrected, the corrected content. The animation is a separate script
(make_event_animation.py) because it reads the OSF deposit.

Palette follows docs/handbook/make_diagrams.py and docs/make_ai_scope_figures.py
so all three figure sets read as one, and matches the Chalmers theme accents.

Numbers that appear in these figures and where they come from:
  boundary.png     src/comfortzone/field.py::critical_thw, evaluated live
  axis / trait     reused unchanged from docs/ai_scope_figures (tracked outputs)
  cutin_*          replication/czb/cutin_field_check.py's construction, re-plotted
"""

from __future__ import annotations

import dataclasses as dc
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIGS = HERE / "figures"
FIGS.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO / "src"))

INK = "#222222"
PURPLE = "#472CBE"
LILAC = "#6746EB"
BLUE = "#36B7F6"
TEAL = "#2BAE9A"
PINK = "#C95B9B"
GREY = "#6B7280"
BEIGE = "#F0EDE6"
PAPER = "#FBFAF7"

plt.rcParams.update({
    "font.size": 13,
    "axes.labelsize": 14,
    "axes.titlesize": 15,
    "xtick.labelsize": 12.5,
    "ytick.labelsize": 12.5,
    "legend.fontsize": 12.5,
    "font.family": "DejaVu Sans",
})


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def box(ax, x, y, w, h, title, sub=None, color=PURPLE, fill="white", ls="-",
        title_size=13.5, sub_size=11.0, lw=2.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                facecolor=fill, edgecolor=color, linewidth=lw,
                                linestyle=ls, mutation_aspect=1.0))
    if sub:
        ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top",
                fontsize=title_size, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 0.62, sub, ha="center", va="top",
                fontsize=sub_size, color=GREY, linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold", color=INK)


def arrow(ax, xy0, xy1, color=INK, lw=2.2, rad=0.0):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle="-|>", mutation_scale=24,
                                 lw=lw, color=color,
                                 connectionstyle="arc3,rad={}".format(rad)))


def save(fig, name):
    path = FIGS / name
    fig.savefig(path, dpi=165, facecolor="white", bbox_inches="tight",
                pad_inches=0.12)
    plt.close(fig)
    print("wrote", path.name)


# ---------------------------------------------------------------------------
# 1. The lineage
# ---------------------------------------------------------------------------
def fig_lineage():
    steps = [
        ("Unconscious inference", "Helmholtz, 1860s\nperception is a guess built\n"
         "from expectations", GREY),
        ("The Bayesian brain", "1990s-2000s\nbeliefs updated by evidence,\n"
         "weighted by reliability", BLUE),
        ("Predictive processing", "2000s-2010s\nthe brain runs a prediction machine;\n"
         "driving version: Great expectations (2018)", TEAL),
        ("Active inference", "2010s\nadd action: behave so that\n"
         "predictions come true", PURPLE),
        ("This driver model", "Engstrom 2024, Wei 2024,\nSchumann 2026 - collision\n"
         "avoidance, benchmarked on humans", PINK),
    ]
    w, h = 15.4, 3.5
    fig, ax = canvas(w, h)
    bw, gap, x0 = 2.62, 0.42, 0.25
    for i, (title, sub, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        box(ax, x, 0.55, bw, 2.45, title, sub, color=color, title_size=13.0,
            sub_size=10.2)
        if i:
            arrow(ax, (x - gap + 0.02, 1.78), (x - 0.06, 1.78))
    ax.text(w / 2, 3.30, "One idea, five refinements - and only the last one is "
            "a driver model", ha="center", va="center", fontsize=13.5,
            color=GREY, style="italic")
    save(fig, "lineage_talk.png")


# ---------------------------------------------------------------------------
# 2. The perception-action loop
# ---------------------------------------------------------------------------
def fig_loop():
    w, h = 15.4, 6.4
    fig, ax = canvas(w, h)

    ax.add_patch(FancyBboxPatch((0.3, 5.05), w - 0.6, 1.0,
                                boxstyle="round,pad=0.05", facecolor=BEIGE,
                                edgecolor="#B9B5AC", linewidth=1.6))
    ax.text(1.35, 5.55, "THE WORLD", ha="center", va="center", fontsize=13.5,
            fontweight="bold", color=INK)
    ax.text(8.6, 5.55, "the two vehicles, the road - and the other vehicle's "
            "scripted behavior", ha="center", va="center", fontsize=12.5,
            color=GREY)

    stages = [
        ("SENSE", "optical angles and their\nrates (looming), not\nmeters and m/s", BLUE),
        ("BELIEVE", "75 weighted hypotheses\nabout the state of\nthe world", PURPLE),
        ("PREDICT", "roll each hypothesis\nforward 6 s, biased\ntoward norm-following", TEAL),
        ("EVALUATE", "score the current plan\nagainst the preferred\nfuture", PINK),
        ("ACT", "execute the first step\nof the plan the model\nis still holding", INK),
    ]
    bw, gap, x0 = 2.62, 0.42, 0.25
    for i, (title, sub, color) in enumerate(stages):
        x = x0 + i * (bw + gap)
        box(ax, x, 2.65, bw, 1.95, title, sub, color=color, title_size=14.5,
            sub_size=10.6)
        if i:
            arrow(ax, (x - gap + 0.02, 3.62), (x - 0.06, 3.62))
    arrow(ax, (x0 + bw / 2, 5.00), (x0 + bw / 2, 4.70), color=BLUE)
    arrow(ax, (x0 + 4 * (bw + gap) + bw / 2, 4.68),
          (x0 + 4 * (bw + gap) + bw / 2, 5.00), color=INK)

    x_eval = x0 + 3 * (bw + gap)
    ax.add_patch(FancyBboxPatch((3.35, 0.45), 9.6, 1.42,
                                boxstyle="round,pad=0.05", facecolor="white",
                                edgecolor=PURPLE, linewidth=2.4, linestyle="--"))
    ax.text(8.15, 1.60, "THE SURPRISE ACCUMULATOR", ha="center", va="center",
            fontsize=13.5, fontweight="bold", color=PURPLE)
    ax.text(8.15, 0.92, "each step, add how far the plan the driver is holding now falls "
            "short of the preferred future.\nWhen the running total crosses a threshold - "
            "and only then - build a new plan from scratch.",
            ha="center", va="center", fontsize=11.6, color=INK, linespacing=1.5)
    arrow(ax, (x_eval + 1.85, 2.60), (x_eval + 1.85, 1.95), color=PURPLE)
    ax.text(x_eval + 1.98, 2.28, "shortfall", ha="left", va="center",
            fontsize=11.2, color=PURPLE)
    arrow(ax, (x_eval + 0.55, 1.95), (x_eval + 0.55, 2.60), color=PURPLE)
    ax.text(x_eval + 0.42, 2.28, "re-plan", ha="right", va="center",
            fontsize=11.2, color=PURPLE, fontweight="bold")
    save(fig, "loop_talk.png")


# ---------------------------------------------------------------------------
# 3. The six preference terms, as the released code implements them
# ---------------------------------------------------------------------------
def fig_preference_terms():
    from aidriver import PreferenceParams
    from comfortzone.field import critical_gap

    p = PreferenceParams(v_desired=15.0)
    fig, axes = plt.subplots(2, 3, figsize=(15.2, 6.6))
    fig.patch.set_facecolor("white")

    def gauss(x, mu, sd):
        return np.exp(-0.5 * ((x - mu) / sd) ** 2)

    v = np.linspace(12, 18, 400)
    axes[0, 0].plot(v, gauss(v, 15, p.sigma_v), color=PURPLE, lw=3)
    axes[0, 0].set_title("Speed: near the desired speed")
    axes[0, 0].set_xlabel("speed [m/s]")

    a = np.linspace(-0.6, 0.6, 400)
    a_eff = np.where(a > 0, 2 * a, a)          # released code doubles positive accel
    axes[0, 1].plot(a, gauss(a_eff, 0, p.sigma_a), color=BLUE, lw=3)
    axes[0, 1].set_title("Pedal effort: gentle, and\nasymmetric in the code")
    axes[0, 1].set_xlabel("acceleration [m/s$^2$]")

    om = np.linspace(-0.12, 0.12, 400)
    axes[0, 2].plot(om, gauss(om, 0, p.sigma_omega), color=BLUE, lw=3)
    axes[0, 2].set_title("Steering effort: the wheel\nshould be mostly still")
    axes[0, 2].set_xlabel("steering rate [rad/s]")

    tau = np.linspace(-0.3, 0.9, 400)
    tau_eff = np.maximum(tau, p.tau_inv_mu)    # one-sided, as reward.py:272
    axes[1, 0].plot(tau, gauss(tau_eff, p.tau_inv_mu, p.tau_inv_sd), color=TEAL, lw=3)
    axes[1, 0].axvline(p.tau_inv_mu, color=GREY, ls=":", lw=1.8)
    axes[1, 0].set_title("Closing rate: one-sided -\nonly closing too fast costs")
    axes[1, 0].set_xlabel("inverse tau [1/s]")

    y = np.linspace(-2.6, 2.6, 800)
    half = p.lane_width / 2
    lane = np.clip(1 - np.abs(y) / half, 0, 1)
    lane = np.where(np.abs(y) <= half, lane, 0.04)
    axes[1, 1].plot(y, lane, color=TEAL, lw=3)
    for edge in (-half, half):
        axes[1, 1].axvline(edge, color=PINK, ls="--", lw=1.8)
    axes[1, 1].set_title("Lane position: triangular,\ngeometry drawn per scenario")
    axes[1, 1].set_xlabel("lateral offset in lane [m]")

    gaps = np.linspace(2, 60, 600)
    dx_star = float(critical_gap(15.0, p=p))
    safe = np.where(gaps + p.vehicle.length >= dx_star, 1.0, 0.06)
    axes[1, 2].plot(gaps, safe, color=PINK, lw=3)
    axes[1, 2].axvline(dx_star - p.vehicle.length, color=INK, ls=":", lw=1.8)
    axes[1, 2].annotate("boundary gap,\nin closed form",
                        xy=(dx_star - p.vehicle.length, 0.5), xytext=(24, 0.42),
                        fontsize=11.5, color=INK,
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.8))
    axes[1, 2].set_title("Safety margin: a counterfactual,\nand it steps")
    axes[1, 2].set_xlabel("gap to lead [m]  (following at 15 m/s)")

    for ax in axes.ravel():
        ax.set_ylim(-0.06, 1.12)
        ax.set_yticks([0, 1])
        ax.set_ylabel("preference")
        ax.grid(alpha=0.2)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    fig.suptitle("The driver's own 'normal': six independent terms, multiplied - "
                 "shapes as the released code implements them",
                 fontsize=15, y=1.005)
    fig.tight_layout()
    save(fig, "pref_terms_talk.png")


# ---------------------------------------------------------------------------
# 4. Comfort versus dread, and what a change of motive does to the boundary
# ---------------------------------------------------------------------------
def fig_boundary():
    from aidriver import PreferenceParams
    from comfortzone.field import critical_thw

    p = PreferenceParams(v_desired=15.0)
    v = np.linspace(8, 30, 200)
    comfort = critical_thw(v, p=p, a_required=4.0)
    dread = critical_thw(v, p=p, a_required=8.0)
    hurried = critical_thw(v, p=dc.replace(p, response_time=0.6), a_required=4.0)
    trusting = critical_thw(v, p=dc.replace(p, a_other_min=-3.0), a_required=4.0)

    fig, ax = plt.subplots(figsize=(13.4, 6.0))
    fig.patch.set_facecolor("white")
    ax.fill_between(v, comfort, 3.2, color=TEAL, alpha=0.10)
    ax.fill_between(v, dread, comfort, color="#F6C36B", alpha=0.22)
    ax.fill_between(v, 0, dread, color=PINK, alpha=0.16)

    ax.plot(v, comfort, color=TEAL, lw=3.4,
            label="comfort boundary  (plans around 4 m/s$^2$)")
    ax.plot(v, dread, color=PINK, lw=3.4,
            label="dread boundary  (8 m/s$^2$ - physics)")
    ax.plot(v, hurried, color=PURPLE, lw=2.6, ls="--",
            label="hurried: reaction budget 1.0 -> 0.6 s")
    ax.plot(v, trusting, color=BLUE, lw=2.6, ls="-.",
            label="trusting the lead: worst case -6 -> -3 m/s$^2$")

    # The upper-left is the legend's; above the comfort line beyond 24 m/s is free.
    ax.text(26.4, 2.66, "inside the comfort zone", color="#1B7F70", fontsize=14,
            fontweight="bold", ha="center")
    ax.text(23.0, 1.02, "uncomfortable,\nbut recoverable", color="#8A6018",
            fontsize=13, ha="center", linespacing=1.3)
    ax.text(23.0, 0.20, "dread zone", color="#A3407A", fontsize=13.5,
            fontweight="bold", ha="center")

    for value, label in ((1.667, "1.67 s"), (0.729, "0.73 s")):
        ax.plot([15], [value], "o", color=INK, ms=7, zorder=5)
        ax.annotate(label, xy=(15, value), xytext=(15.6, value + 0.13),
                    fontsize=12.5, color=INK, fontweight="bold")

    ax.set_xlabel("following speed [m/s]")
    ax.set_ylabel("time headway [s]")
    ax.set_xlim(8, 30)
    ax.set_ylim(0, 3.0)
    ax.grid(alpha=0.25)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(0.005, 0.99), frameon=False,
              fontsize=12.2)
    ax.set_title("The boundary in closed form - and the framework predicts how far "
                 "a change of motive moves it", fontsize=15, pad=12)
    fig.tight_layout()
    save(fig, "boundary_talk.png")


# ---------------------------------------------------------------------------
# 5. What is shared and what changes when a scenario is added
# ---------------------------------------------------------------------------
def fig_scenario_diff():
    w, h = 15.4, 7.4
    fig, ax = canvas(w, h)

    ax.add_patch(FancyBboxPatch((0.25, 6.25), w - 0.5, 0.95,
                                boxstyle="round,pad=0.05", facecolor=BEIGE,
                                edgecolor="#8E8A82", linewidth=1.8))
    ax.text(w / 2, 6.93, "SHARED - src/common/, never edited per scenario",
            ha="center", va="center", fontsize=13, fontweight="bold", color=INK)
    ax.text(w / 2, 6.53, "particle filter  ·  CEM planner  ·  looming transform  ·  "
            "evidence accumulator  ·  bicycle dynamics  ·  expected free energy",
            ha="center", va="center", fontsize=11.8, color=GREY)

    rows = [
        ("decoder_true.py", "what can be seen",
         ["IDENTICAL", "IDENTICAL", "IDENTICAL", "reuse\n(check partial-lane\ntarget)"]),
        ("dynamics_true.py", "what really happens\n(the other vehicle's script)",
         ["brake countdown\n+ jerk ramp\n162 lines",
          "gradient-descent\nincursion optimizer\n665 lines",
          "solve steering rate\nfor the turn\n354 lines",
          "REPLAY recorded\ntrajectories"]),
        ("reward.py", "what counts as normal here\n(the driver's preferences)",
         ["lane geometry: 2-lane\n+ lane-change bookkeeping\nnorms: position only",
          "lane geometry: oncoming lane\nnorms: position + SPEED",
          "lane geometry: as rear-end\nnorms: road mask + corner\n+ red light",
          "lane geometry: as rear-end\nnorms: position +\nMANOEUVRE PROGRESS"]),
    ]
    cols = [("rear-end", PURPLE), ("oncoming", BLUE), ("intersection", TEAL),
            ("cut-in  (added by us)", "#E08A1E")]

    left_w, col_w, cgap = 3.30, 2.74, 0.14
    x_cols = 3.72
    ax.text(0.30, 5.72, "", fontsize=1)
    for c, (name, color) in enumerate(cols):
        x = x_cols + c * (col_w + cgap)
        ax.add_patch(FancyBboxPatch((x, 5.52), col_w, 0.56,
                                    boxstyle="round,pad=0.04", facecolor="white",
                                    edgecolor=color, linewidth=2.2,
                                    linestyle="--" if c == 3 else "-"))
        ax.text(x + col_w / 2, 5.80, name, ha="center", va="center",
                fontsize=12.2, fontweight="bold", color=color)

    row_h = [0.95, 1.45, 1.65]
    y = 5.52
    for r, (fname, what, cells) in enumerate(rows):
        y -= row_h[r] + 0.16
        ax.add_patch(FancyBboxPatch((0.25, y), left_w, row_h[r],
                                    boxstyle="round,pad=0.05", facecolor="white",
                                    edgecolor=INK, linewidth=2.0))
        ax.text(0.25 + left_w / 2, y + row_h[r] - 0.26, fname, ha="center",
                va="top", fontsize=12.5, fontweight="bold", color=INK)
        ax.text(0.25 + left_w / 2, y + row_h[r] - 0.62, what, ha="center",
                va="top", fontsize=11.0, color=GREY, linespacing=1.3)
        for c, (name, color) in enumerate(cols):
            x = x_cols + c * (col_w + cgap)
            fill = "#EAF7F3" if cells[c] == "IDENTICAL" else PAPER
            ax.add_patch(FancyBboxPatch((x, y), col_w, row_h[r],
                                        boxstyle="round,pad=0.04",
                                        facecolor=fill, edgecolor=color,
                                        linewidth=2.0,
                                        linestyle="--" if c == 3 else "-"))
            ax.text(x + col_w / 2, y + row_h[r] / 2, cells[c], ha="center",
                    va="center", fontsize=10.6, color=INK, linespacing=1.35)

    ax.text(w / 2, 0.30, "Of 65 configuration parameters, every one describing the "
            "DRIVER is identical across the three published scenarios - "
            "with one exception: w_sd_model.",
            ha="center", va="center", fontsize=12.4, color=PURPLE,
            fontweight="bold")
    save(fig, "scenario_diff_talk.png")


# ---------------------------------------------------------------------------
# 6. The dual-role claim, before it was tested
# ---------------------------------------------------------------------------
def fig_field_claim():
    w, h = 15.4, 5.8
    fig, ax = canvas(w, h)

    ax.text(0.30, 5.55, "PREFERENCE DISTRIBUTION  p(o)", ha="left", va="top",
            fontsize=13.5, fontweight="bold", color=INK)
    ax.text(0.30, 5.12, "six additive log terms, parameters inherited from the\n"
            "published model - not one of them refitted by us",
            ha="left", va="top", fontsize=11.2, color=GREY, linespacing=1.35)

    terms = ["log p_speed", "log p_accel", "log p_steer", "log p_lateral",
             "log p_collision", "log p_safety"]
    for i, t in enumerate(terms):
        color = PURPLE if i >= 4 else BLUE
        box(ax, 0.30, 4.10 - i * 0.62, 2.85, 0.54, t, color=color,
            title_size=11.8, lw=1.8)
    ax.text(1.72, 0.70, "the two lower terms carry the conflict geometry",
            ha="center", va="center", fontsize=10.8, color=GREY)

    box(ax, 3.70, 2.20, 2.35, 1.40, "SUM", "log p(o) = sum\nof the six",
        color=INK, title_size=13.5, sub_size=11.0)
    arrow(ax, (3.24, 2.90), (3.64, 2.90))

    box(ax, 6.45, 2.05, 3.35, 1.70, "RESIDUAL INFORMATION",
        "eps(o) = max log p(o') - log p(o)\n>= 0, and exactly zero\n"
        "at the preferred observation",
        color=PURPLE, title_size=13.0, sub_size=11.0)
    arrow(ax, (6.10, 2.90), (6.39, 2.90))

    box(ax, 10.55, 3.35, 4.60, 1.85, "ROLE 1 - THE BOUNDARY",
        "the level set eps(o) = c is the\ncomfort-zone boundary;\n"
        "c is one number per driver",
        color=TEAL, title_size=13.0, sub_size=11.2)
    box(ax, 10.55, 0.95, 4.60, 1.85, "ROLE 2 - THE TIMING",
        "accumulate eps over time to a bound;\nthe crossing predicts\n"
        "when the driver acts",
        color=PINK, title_size=13.0, sub_size=11.2)
    arrow(ax, (9.85, 3.10), (10.49, 4.05), color=TEAL, rad=-0.2)
    arrow(ax, (9.85, 2.70), (10.49, 1.75), color=PINK, rad=0.2)

    ax.text(12.85, 0.42, "One scalar, two jobs. No conventional indicator has that "
            "property -\nand it is testable.", ha="center", va="center",
            fontsize=12.0, color=PURPLE, fontweight="bold", linespacing=1.4)
    save(fig, "field_claim_talk.png")


# ---------------------------------------------------------------------------
# 7. The stack, and the slice each workstream takes (landscape)
# ---------------------------------------------------------------------------
def fig_stack():
    rows = [
        ("Generative model of the world", "some", "on"),
        ("Belief updating / state estimation", "off", "on"),
        ("Policy space and policy search", "off", "on"),
        ("Expected free energy, pragmatic part", "off", "on"),
        ("Expected free energy, epistemic part", "off", "off"),
        ("Preference distribution  p(o)", "on", "on"),
        ("Residual information (surprise family)", "on", "on"),
        ("Evidence accumulation to a bound", "fail", "on"),
        ("Closed-loop action", "off", "on"),
    ]
    labels = {"on": ("used", TEAL, "white"), "off": ("not used", "white", GREY),
              "some": ("in part", BLUE, "white"),
              "fail": ("tested,\nfailed", PINK, "white")}

    w, h = 15.4, 7.9
    fig, ax = canvas(w, h)
    ax.text(0.30, 7.78, "THE ACTIVE-INFERENCE STACK", ha="left", va="top",
            fontsize=14, fontweight="bold", color=INK)
    ax.text(8.90, 7.78, "CZB method\n(the deliverable)", ha="center", va="top",
            fontsize=12.2, fontweight="bold", color=INK, linespacing=1.3)
    ax.text(11.95, 7.78, "Closed-loop agent\n(crash causation)", ha="center",
            va="top", fontsize=12.2, fontweight="bold", color=INK, linespacing=1.3)

    row_h, gapy = 0.56, 0.10
    y0 = 6.92
    for i, (name, czb, loop) in enumerate(rows):
        y = y0 - i * (row_h + gapy) - row_h
        highlight = czb in ("on", "some", "fail")
        ax.add_patch(FancyBboxPatch((0.30, y), 7.10, row_h,
                                    boxstyle="round,pad=0.04",
                                    facecolor="white" if highlight else PAPER,
                                    edgecolor=PURPLE if highlight else GREY,
                                    linewidth=2.2 if highlight else 1.4))
        ax.text(3.85, y + row_h / 2, name, ha="center", va="center",
                fontsize=12.2, fontweight="bold" if highlight else "normal",
                color=INK if highlight else GREY)
        for cx, key in ((8.90, czb), (11.95, loop)):
            text, fill, fg = labels[key]
            ax.add_patch(FancyBboxPatch((cx - 1.30, y), 2.60, row_h,
                                        boxstyle="round,pad=0.04",
                                        facecolor=fill, edgecolor=GREY,
                                        linewidth=1.4))
            ax.text(cx, y + row_h / 2, text, ha="center", va="center",
                    fontsize=11.0, fontweight="bold", color=fg,
                    linespacing=1.15)

    ax.text(0.30, 0.42, "The CZB method takes a deliberately thin slice: a calibrated "
            "preference distribution, read pointwise through a surprise measure.\n"
            "\"We do not do planning\" is true of the deliverable and false of the "
            "repository - the crash-causation work runs the whole loop.",
            ha="left", va="center", fontsize=11.6, color=GREY, linespacing=1.45)
    save(fig, "stack_talk.png")


# ---------------------------------------------------------------------------
# 8. The progression of findings
# ---------------------------------------------------------------------------
def fig_progression():
    steps = [
        ("Dry run on the authors' own output",
         "896 rear-end trials: one fitted level recovers the model's\n"
         "brake onsets, median timing error 0.0 s",
         TEAL, "the pipeline works\nend to end"),
        ("The cut-in construction",
         "the released terms step, identically at every criticality;\n"
         "a continuous lane-entry form replaces the binary gates",
         TEAL, "the field ramps\nwith criticality"),
        ("Gate R.1 - the accumulator",
         "three pre-argued variants all fit worse than a static probit;\n"
         "held-out 0.255 against a pre-registered rule of 0.11",
         PINK, "the timing half\nFAILS"),
        ("B.1 - the cyclist overtake",
         "the field orders the cells at +0.40 where the clearance label\n"
         "gives -0.83: the lateral machinery is collision-oriented",
         PINK, "the lateral half\nfails too"),
        ("The collinearity discovery",
         "in study 1 the relative speed is constant, so gap and TTC\n"
         "correlate 1.0000 - the design could never separate them",
         "#E08A1E", "the earlier evidence\nwas uninformative"),
        ("Gate R.2 - the field against a gap threshold",
         "study 2 breaks the collinearity: field 0.347, worse than chance\n"
         "0.320; log gap 0.152 against a noise floor of 0.118",
         PINK, "the boundary half's axis\nis RULED AGAINST"),
        ("What survived",
         "one comfort-zone level per driver, about 69% shared across\n"
         "four scenarios - measured with no field at all",
         TEAL, "the headline\nresult"),
    ]
    w, h = 15.4, 6.9
    fig, ax = canvas(w, h)

    rh, gapy = 0.80, 0.09
    top = 6.75
    ax.plot([0.95, 0.95], [top - len(steps) * (rh + gapy) + gapy + 0.25, top - 0.35],
            color="#D8D5CE", lw=4, zorder=0, solid_capstyle="round")

    y = top
    for title, body, color, verdict in steps:
        y -= rh + gapy
        ax.plot([0.95], [y + rh / 2], "o", ms=16, color=color, zorder=3,
                markeredgecolor="white", markeredgewidth=2.5)
        ax.text(1.75, y + rh - 0.02, title, ha="left", va="top",
                fontsize=14.2, fontweight="bold", color=INK)
        ax.text(1.75, y + rh - 0.36, body, ha="left", va="top", fontsize=12.2,
                color=GREY, linespacing=1.3)
        ax.add_patch(FancyBboxPatch((10.55, y + 0.04), 4.65, rh - 0.08,
                                    boxstyle="round,pad=0.05", facecolor="white",
                                    edgecolor=color, linewidth=2.0))
        ax.text(12.88, y + rh / 2, verdict, ha="center", va="center",
                fontsize=12.4, fontweight="bold", color=color, linespacing=1.3)
    save(fig, "progression_talk.png")


# ---------------------------------------------------------------------------
# 9. The cut-in construction, before and after the continuous lane-entry form
# ---------------------------------------------------------------------------
def fig_cutin_before_after():
    """Re-plot of replication/czb/cutin_field_check.py, car cut-ins only, wide."""
    from aidriver.preferences import PreferenceParams, pragmatic_deficit
    from comfortzone.cutin import (load_cutin_trace, cutin_obs, cutin_predictors)

    base = REPO / ("external/01_studies/01_Studies/01_Sequence_Random_ButtonPress/"
                   "Kinematics/Button_Press_Study")
    ttcs = [2, 3, 4, 5, 6, 7, 8]
    cmap = plt.get_cmap("viridis")

    fig, axes = plt.subplots(1, 2, figsize=(14.6, 5.4), sharex=True)
    fig.patch.set_facecolor("white")
    for k, ttc in enumerate(ttcs):
        tr = load_cutin_trace(base / "CutInCar_{}TTC_vehicle_states.csv".format(ttc),
                              is_truck=False)
        df = cutin_predictors(tr)
        d_new = df.deficit.to_numpy()
        p = PreferenceParams()
        d_old = np.asarray(pragmatic_deficit(cutin_obs(tr, p), p), float)
        t_rel = df.t.to_numpy() - df.t.to_numpy()[tr.onset_idx]
        m = (t_rel >= -1.0) & (t_rel <= 2.0)
        color = cmap(k / (len(ttcs) - 1))
        axes[0].plot(t_rel[m], d_old[m], color=color, lw=2.6,
                     label="TTC{}".format(ttc))
        axes[1].plot(t_rel[m], d_new[m], color=color, lw=2.6,
                     label="TTC{}".format(ttc))

    axes[0].set_title("Released binary gates:\none step, the same for every criticality",
                      color=PINK)
    axes[1].set_title("Continuous lane entry:\ngraded ramps, ordered by criticality once the\nmanoeuvre is under way", color=TEAL)
    for ax in axes:
        ax.axvline(0.0, color=GREY, lw=1.2, ls=":")
        ax.set_xlabel("time since lane-change onset [s]")
        ax.grid(alpha=0.25)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("comfort-zone deficit")
    axes[0].legend(fontsize=11.5, ncol=2, frameon=False, loc="upper left")
    fig.tight_layout()
    save(fig, "cutin_before_after_talk.png")


def main() -> None:
    fig_lineage()
    fig_loop()
    fig_preference_terms()
    fig_boundary()
    fig_scenario_diff()
    fig_field_claim()
    fig_stack()
    fig_progression()
    fig_cutin_before_after()


if __name__ == "__main__":
    main()
