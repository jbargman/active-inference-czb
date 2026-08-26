"""Scenario-difference flow chart for handbook chapter 04.

    python docs/handbook/make_scenario_diagram.py

Writes docs/handbook/figures/scenario_diff.png. Kept separate from make_diagrams.py
because that script loads the OSF deposit and is slow; this one draws only.

The chart answers "what has to change to add a scenario": everything in src/common/ is
shared untouched, decoder_true.py is identical across the three released scenarios, and
the real work is three places inside reward.py plus the target's script in
dynamics_true.py. The dashed column is the proposed cut-in scenario.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)

INK = "#222222"
PURPLE = "#472CBE"
BLUE = "#36B7F6"
TEAL = "#2BAe9A"
PINK = "#C95B9B"
GREY = "#6B7280"
BEIGE = "#F0EDE6"
AMBER = "#E8A33D"


def box(ax, x, y, w, h, text, fc, ec=None, fs=8.2, tc=INK, ls="solid", weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                fc=fc, ec=ec or fc, lw=1.3, linestyle=ls, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=3, linespacing=1.35, weight=weight)


def arrow(ax, p, q, color=GREY, ls="solid", lw=1.2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11,
                                 color=color, lw=lw, linestyle=ls, zorder=1,
                                 shrinkA=2, shrinkB=2))


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.4, 7.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    ax.text(.5, .975, "Adding a scenario: what is shared, what changes",
            ha="center", fontsize=13.5, color=INK, weight="bold")
    ax.text(.5, .944, "one driver, many worlds — the driver's algorithm is never edited",
            ha="center", fontsize=9.5, color=GREY, style="italic")

    # ---- shared core, as a full-width banner ------------------------------
    box(ax, .02, .845, .96, .075,
        "SHARED — src/common/, never edited per scenario\n"
        "particle filter  ·  CEM planner  ·  looming transform  ·  evidence accumulator  ·  "
        "bicycle dynamics  ·  expected free energy",
        BEIGE, ec=GREY, fs=8.8)

    # ---- column headers --------------------------------------------------
    cols = [(.325, "rear-end", PURPLE, "solid"),
            (.505, "oncoming", BLUE, "solid"),
            (.685, "intersection\n(files named 'side')", TEAL, "solid"),
            (.875, "cut-in  (proposed)", AMBER, "dashed")]
    W = .168
    for x, name, col, ls in cols:
        box(ax, x - W / 2, .765, W, .058, name, "white", ec=col, fs=8.6, tc=col,
            ls=ls, weight="bold")
        arrow(ax, (x, .845), (x, .825), color="#C9C7C1", lw=1.0)

    # ---- the three files -------------------------------------------------
    rows = [
        (.625, .125, "decoder_true.py", "what can be seen",
         ["IDENTICAL", "IDENTICAL", "IDENTICAL", "reuse\n(check partial-lane\ntarget + truck dims)"]),
        (.440, .160, "dynamics_true.py", "what really happens\n(the other vehicle's script)",
         ["brake countdown\n+ jerk ramp\n162 lines",
          "gradient-descent\nincursion optimizer\n665 lines",
          "solve steering rate\nfor the turn\n354 lines",
          "REPLAY recorded\ntrajectories\n(or adapt oncoming)"]),
        (.240, .175, "reward.py", "what counts as normal here\n(the driver's preferences)",
         ["lane geometry: 2-lane\n+ lane-change bookkeeping\nnorms: position only",
          "lane geometry: oncoming lane\nnorms: position + SPEED\n(braking = violation)",
          "lane geometry: as rear-end\nnorms: road mask + corner\n+ red light",
          "lane geometry: as rear-end\nnorms: position +\nMANOEUVRE PROGRESS"]),
    ]
    for y, h, fname, role, cells in rows:
        box(ax, .02, y, .19, h, "{}\n\n{}".format(fname, role), "white", ec=INK, fs=8.5)
        for (x, _, col, ls), txt in zip(cols, cells):
            fc = "#EAF6EE" if txt == "IDENTICAL" else "#F6F6F4"
            box(ax, x - W / 2, y, W, h, txt, fc, ec=col, fs=7.6, ls=ls)
        arrow(ax, (.212, y + h / 2), (.325 - W / 2 - .004, y + h / 2))

    # ---- the punchline ---------------------------------------------------
    box(ax, .02, .025, .96, .19,
        "The scenario's scientific content lives in reward.py::get_weights — the driver's prior over what the OTHER road user\n"
        "normally does. Rear-end: stay in your lane. Oncoming: stay in your lane AND keep your speed. Intersection: stay on the\n"
        "road AND obey the light. Cut-in needs something none of them has — a norm that depends on the other vehicle's\n"
        "MANOEUVRE PROGRESS: adjacent lane is normal, straddling is transiently normal, completed is normal at a judged headway.\n\n"
        "One driver-side parameter also changes: w_sd_model (assumed steering variability of the other vehicle) is 0.0045 for\n"
        "rear-end and 0.4575 for both lateral scenarios. A cut-in target steers, so it takes the lateral value.",
        "#FBF7EE", ec=AMBER, fs=8.6)

    fig.tight_layout()
    out = FIGS / "scenario_diff.png"
    fig.savefig(out, dpi=170, facecolor="white")
    print("wrote", out)


if __name__ == "__main__":
    main()
