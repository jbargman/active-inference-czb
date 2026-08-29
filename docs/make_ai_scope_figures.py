"""Generate the diagrams for `docs/active_inference_scope_map.md`.

    python docs/make_ai_scope_figures.py

Everything lands in docs/ai_scope_figures/. The two data figures (3 and 4) read
their numbers from the tracked outputs of committed analyses rather than from
literals in this file, so a regenerated analysis moves the figure:

  fig3  replication/czb/out/cutin2_field_vs_gap.md   (card R.2 task 1, pre-registered)
  fig4  replication/czb/out/cross_scenario_consistency.md

Figures 1, 2, 5 and 6 are schematics; they carry no numbers that are not also
stated, with their sources, in the document itself.

Palette follows docs/handbook/make_diagrams.py so the two figure sets read as one.
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FIGS = HERE / "ai_scope_figures"
FIGS.mkdir(exist_ok=True)
OUT = REPO / "replication" / "czb" / "out"

INK = "#222222"
PURPLE = "#472CBE"
BLUE = "#36B7F6"
TEAL = "#2BAE9A"
PINK = "#C95B9B"
GREY = "#6B7280"
BEIGE = "#F0EDE6"
PAPER = "#FBFAF7"

# status colors, used consistently across every figure in this set
LOAD = TEAL      # load-bearing: a claim rests on it
COMP = BLUE      # comparator / candidate: kept to be scored against
DEAD = PINK      # tested and ruled against
OFF = GREY       # present in the framework, switched off here


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


# ---------------------------------------------------------------------------
# 1. The stack, and the slice each workstream takes
# ---------------------------------------------------------------------------
def fig_stack():
    """Nine components of the active-inference stack against two workstreams."""
    rows = [
        ("Generative model of the world",
         "state transitions, observation model", "some", "on"),
        ("Belief updating / state estimation",
         "particle filter over the other agent's state", "off", "on"),
        ("Policy space and policy search",
         "CEM over candidate acceleration/steering plans", "off", "on"),
        ("Expected free energy, pragmatic part",
         "E[log p(o)] of a rolled-out policy", "off", "on"),
        ("Expected free energy, epistemic part",
         "information gain; the gaze half; alpha", "off", "off"),
        ("Preference distribution  p(o)",
         "six log-preference terms: speed, accel, steer,\n"
         "lateral, collision, safety", "on", "on"),
        ("Residual information (surprise family)",
         "eps = max log p(o') - log p(o) >= 0, a true zero", "on", "on"),
        ("Evidence accumulation to a bound",
         "integrate eps until threshold -> response onset", "part", "on"),
        ("Closed-loop action",
         "execute, re-plan, feed back into the world", "off", "on"),
    ]
    n = len(rows)
    H = 1.02 * n + 2.2
    fig, ax = _fig(12.2, H)
    x0, w = 0.35, 7.5
    cx = [8.55, 10.55]
    cw = 1.55

    ax.text(x0, H - 0.42, "THE ACTIVE-INFERENCE STACK", fontsize=11.5,
            fontweight="bold", color=INK, va="center")
    ax.text(x0, H - 0.85, "everything the framework offers, top to bottom",
            fontsize=8.6, color=GREY, va="center")
    for i, lab in enumerate(["CZB method\n(the deliverable)",
                             "Closed-loop agent\n(crash causation)"]):
        ax.text(cx[i] + cw / 2, H - 0.60, lab, ha="center", va="center",
                fontsize=9.0, fontweight="bold", color=INK, linespacing=1.35)

    marks = {"on": (LOAD, "used"), "part": (PINK, "tested,\nfailed"),
             "some": (COMP, "in part"), "off": (OFF, "not used")}
    for i, (title, sub, a, b) in enumerate(rows):
        y = H - 1.35 - (i + 1) * 1.02
        col = marks[a][0]
        box(ax, x0, y, w, 0.90, title, sub, col,
            fill="white" if a != "off" else PAPER, title_size=9.6, sub_size=7.9)
        for j, s in enumerate((a, b)):
            c, lab = marks[s]
            ax.add_patch(FancyBboxPatch((cx[j], y), cw, 0.90,
                                        boxstyle="round,pad=0.04",
                                        facecolor=c if s != "off" else "white",
                                        edgecolor=c, linewidth=1.4))
            ax.text(cx[j] + cw / 2, y + 0.45, lab, ha="center", va="center",
                    fontsize=7.9, color="white" if s != "off" else GREY,
                    fontweight="bold" if s != "off" else "normal",
                    linespacing=1.2)

    ax.text(x0, 0.42,
            "The CZB method takes a deliberately thin slice: a calibrated preference "
            "distribution, read pointwise through a surprise measure. \"In part\" at the "
            "top means the other\nvehicle's motion is predicted in closed form (the "
            "lane-entry weight) while the ego's own is not. The crash-causation workstream "
            "runs the whole loop, so\n\"we do not use planning\" is true of the deliverable, "
            "not of the repository.",
            fontsize=8.4, color=GREY, va="center", linespacing=1.45)
    fig.tight_layout()
    fig.savefig(FIGS / "stack_scope.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Preference distribution -> deficit -> two roles
# ---------------------------------------------------------------------------
def fig_pipeline():
    fig, ax = _fig(12.4, 6.4)

    terms = ["speed", "accel", "steer", "lateral", "collision", "safety"]
    ax.text(1.25, 5.95, "PREFERENCE DISTRIBUTION  p(o)", ha="center", fontsize=9.6,
            fontweight="bold", color=INK)
    ax.text(1.25, 5.62, "six additive log terms, parameters inherited\n"
                        "from the published model - none refitted",
            ha="center", fontsize=7.9, color=GREY, linespacing=1.3)
    for i, t in enumerate(terms):
        y = 4.85 - i * 0.52
        c = PURPLE if t in ("collision", "safety") else BLUE
        ax.add_patch(FancyBboxPatch((0.35, y), 1.8, 0.42, boxstyle="round,pad=0.03",
                                    facecolor="white", edgecolor=c, linewidth=1.4))
        ax.text(1.25, y + 0.21, "log p_" + t, ha="center", va="center",
                fontsize=8.6, color=INK)
    ax.text(1.25, 2.02, "the two lower terms carry the\nconflict geometry (counterfactual\n"
                        "hard-braking lead, lane overlap)",
            ha="center", va="top", fontsize=7.6, color=GREY, linespacing=1.35)

    box(ax, 2.75, 3.20, 1.85, 1.35, "SUM", "log p(o) =\nsum of the six", INK)
    arrow(ax, (2.20, 3.88), (2.72, 3.88))

    box(ax, 5.05, 3.20, 2.55, 1.35, "RESIDUAL INFORMATION",
        "eps(o) = max log p(o') - log p(o)\n>= 0, zero when comfortable", PURPLE)
    arrow(ax, (4.62, 3.88), (5.02, 3.88))

    ax.add_patch(FancyBboxPatch((5.05, 2.55), 2.55, 0.52, boxstyle="round,pad=0.03",
                                facecolor="white", edgecolor=DEAD, linewidth=1.6,
                                linestyle="--"))
    ax.text(6.32, 2.81, "kinematic ordering ruled against (R.2)", ha="center",
            va="center", fontsize=7.8, color=DEAD, fontweight="bold")

    # the two roles
    box(ax, 8.35, 4.55, 3.65, 1.35, "ROLE 1 - THE BOUNDARY",
        "the level set  eps(o) = c  is the comfort-zone\n"
        "boundary; c is one number per driver", TEAL)
    box(ax, 8.35, 2.55, 3.65, 1.35, "ROLE 2 - THE TIMING",
        "accumulate eps over time to a bound;\n"
        "crossing predicts when the driver acts", DEAD)
    ax.add_patch(FancyBboxPatch((8.35, 1.90), 3.65, 0.52, boxstyle="round,pad=0.03",
                                facecolor="white", edgecolor=DEAD, linewidth=1.6,
                                linestyle="--"))
    ax.text(10.17, 2.16, "FAIL at review gate R.1 (as specified)", ha="center",
            va="center", fontsize=7.8, color=DEAD, fontweight="bold")

    arrow(ax, (7.65, 4.10), (8.32, 4.90), color=TEAL, rad=-0.15)
    arrow(ax, (7.65, 3.66), (8.32, 3.30), color=DEAD, rad=0.15)

    ax.add_patch(FancyBboxPatch((8.35, 0.45), 3.65, 1.10, boxstyle="round,pad=0.05",
                                facecolor=BEIGE, edgecolor="none"))
    ax.text(10.17, 1.30, "THE DUAL-ROLE ARGUMENT", ha="center", va="center",
            fontsize=8.8, fontweight="bold", color=INK)
    ax.text(10.17, 0.82, "one scalar was to do both jobs. That was the\n"
                         "distinctive claim - and it is the half that broke.",
            ha="center", va="center", fontsize=7.8, color=GREY, linespacing=1.35)
    fig.tight_layout()
    fig.savefig(FIGS / "field_pipeline.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. The axis scoreboard (data: cutin2_field_vs_gap.md)
# ---------------------------------------------------------------------------
def _read_axis_scores():
    txt = (OUT / "cutin2_field_vs_gap.md").read_text(encoding="utf-8")
    head = txt.split("### Folds: leave-one-video-out")[0]
    m = re.search(r"Best-scale scores: (.+?)\.\s", head)
    scores = {}
    for part in m.group(1).split(","):
        name, val = part.strip().split()
        scores[name] = float(val)
    chance = float(re.search(r"\| chance \(train mean\) \| - \| ([0-9.]+)", head).group(1))
    floor = float(re.search(r"\| sampling-noise floor \| - \| ([0-9.]+)", head).group(1))
    return scores, chance, floor


def fig_axes():
    scores, chance, floor = _read_axis_scores()
    label = {"gap": "longitudinal gap (log)", "ttc": "TTC (log)",
             "areq": "required deceleration (log)",
             "field": "active-inference preference field"}
    order = sorted(scores, key=scores.get)
    vals = [scores[k] for k in order]
    cols = [DEAD if k == "field" else (LOAD if k == "gap" else COMP) for k in order]

    fig, ax = plt.subplots(figsize=(10.4, 4.3))
    y = list(range(len(order)))
    ax.barh(y, vals, color=cols, height=0.58, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([label[k] for k in order], fontsize=9.5)
    ax.invert_yaxis()
    for i, v in enumerate(vals):
        ax.text(v + 0.006, i, "{:.3f}".format(v), va="center", fontsize=9.2,
                color=INK, fontweight="bold")

    lab_y = -0.72
    ax.axvline(chance, color=INK, ls="--", lw=1.4, zorder=4)
    ax.text(chance, lab_y, "chance {:.3f}".format(chance), ha="center", fontsize=8.4,
            color=INK, fontweight="bold")
    ax.axvline(floor, color=GREY, ls=":", lw=1.4, zorder=4)
    ax.text(floor, lab_y, "noise floor {:.3f}".format(floor), ha="center",
            fontsize=8.4, color=GREY)

    ax.set_xlabel("held-out weighted RMSE on the second cut-in study - lower is better\n"
                  "(matched 3-parameter threshold models, leave-one-starting-TTC-out folds)",
                  fontsize=9.0, color=GREY, linespacing=1.5)
    ax.set_xlim(0, max(vals) * 1.18)
    ax.set_title("Which scalar orders the human response?",
                 fontsize=11.5, fontweight="bold", color=INK, loc="left", pad=30)
    ax.grid(axis="x", color="#E5E7EB", zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    fig.savefig(FIGS / "axis_scoreboard.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. The claim that survived (data: cross_scenario_consistency.md)
# ---------------------------------------------------------------------------
def _read_shared_fractions():
    txt = (OUT / "cross_scenario_consistency.md").read_text(encoding="utf-8")
    block = txt.split("## Shared fraction")[1]
    pairs = re.findall(r"\| (\S+ vs \S+) \| \+?([0-9.]+) \| ([0-9.]+) \| \+?([0-9.]+) \|",
                       block)
    mean = float(re.search(r"Mean ratio across the six pairs: \*\*\+?([0-9.]+)\*\*",
                           block).group(1))
    return [(p, float(r), float(c), float(x)) for p, r, c, x in pairs], mean


def fig_trait():
    pairs, mean = _read_shared_fractions()
    pairs = sorted(pairs, key=lambda t: -t[3])
    fig, ax = plt.subplots(figsize=(10.4, 4.5))
    y = list(range(len(pairs)))
    ax.barh(y, [p[3] for p in pairs], color=LOAD, height=0.58, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([p[0].replace(" vs ", "  <->  ") for p in pairs], fontsize=9.5)
    ax.invert_yaxis()
    for i, p in enumerate(pairs):
        ax.text(1.30, i, "r = {:+.2f}   ceiling {:.2f}".format(p[1], p[2]),
                va="center", ha="right", fontsize=8.6, color=GREY)

    lab_y = -0.72
    ax.axvline(mean, color=PURPLE, ls="--", lw=1.6, zorder=4)
    ax.text(mean, lab_y, "mean {:.2f}".format(mean), ha="center", fontsize=8.8,
            color=PURPLE, fontweight="bold")
    ax.axvline(1.0, color=INK, ls=":", lw=1.3, zorder=4)
    ax.text(1.0, lab_y, "one identical trait", ha="center", fontsize=8.4, color=INK)

    ax.set_xlim(0, 1.32)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("observed cross-scenario correlation as a fraction of the "
                  "split-half reliability ceiling\n"
                  "(43 participants seen in all four scenarios; no field used anywhere "
                  "in this analysis)",
                  fontsize=9.0, color=GREY, linespacing=1.5)
    ax.set_title("What survived: one comfort-zone level per driver",
                 fontsize=11.5, fontweight="bold", color=INK, loc="left", pad=30)
    ax.grid(axis="x", color="#E5E7EB", zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    fig.savefig(FIGS / "trait_shared_fraction.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. What the method actually consists of now
# ---------------------------------------------------------------------------
def fig_composition():
    cols = [
        ("LOAD-BEARING", LOAD,
         "a claim currently rests on it",
         [("Psychometrics: threshold + lapse",
           "probit on a criticality axis, per-trial lapse\n"
           "rate; the estimator behind every fitted number"),
          ("Hierarchical Bayes / latent trait",
           "one shrunk random effect per driver; the\n"
           "population whose percentiles are the deliverable"),
          ("Held-out model comparison",
           "leave-one-condition-out and LOPO folds, rules\n"
           "pre-registered; this is what does the ruling"),
          ("Comfort-zone boundary theory",
           "the zero-risk lineage: the object being\n"
           "measured, and why a scalar level means anything")]),
        ("COMPARATOR / CANDIDATE", COMP,
         "kept to be scored against, or newly promoted",
         [("Kinematic surrogate measures",
           "gap, TTC, required deceleration - currently the\n"
           "best within-scenario criticality axis"),
          ("Per-scenario 2D state rules",
           "the comparator-class constructions for truck\n"
           "(B.2) and LTAP (B.3), ruled 2026-08-29"),
          ("The CZB ellipse",
           "joint Mahalanobis percentile over per-scenario\n"
           "observables - now a deliverable candidate"),
          ("Risk-field models (the DRF)",
           "an independently validated instance of\n"
           "\"keep one scalar below a threshold\"")]),
        ("FALSIFIED", DEAD,
         "tested on this data, rejected, kept as a finding",
         [("The preference field as the axis",
           "held-out worse than chance on the design built\n"
           "to separate it; R.2, pre-registered"),
          ("Deficit-driven accumulation",
           "non-leaky, fixed bound, deficit drift: FAIL at\n"
           "R.1. Says nothing about the family"),
          ("The expected-deficit lateral term",
           "sign derivation inconsistent within matched-TTC\n"
           "rows; never built")]),
        ("PRESENT BUT SWITCHED OFF", OFF,
         "in the repository, not in the deliverable",
         [("EFE planning and policy search",
           "runs in the crash-causation closed loop;\n"
           "deliberately absent from the field method"),
          ("Epistemic value / gaze choice",
           "alpha = 0 throughout; the authors' own ablation\n"
           "found it inert longitudinally"),
          ("Belief updating / particle filter",
           "the field is evaluated on observed kinematics\n"
           "directly, which is what makes it cheap")]),
    ]
    W, H = 14.2, 7.5
    fig, ax = _fig(W, H)
    cw, x0, gap = 3.24, 0.32, 0.22
    for k, (title, color, sub, items) in enumerate(cols):
        x = x0 + k * (cw + gap)
        ax.add_patch(FancyBboxPatch((x, 6.45), cw, 0.82, boxstyle="round,pad=0.04",
                                    facecolor=color, edgecolor="none"))
        ax.text(x + cw / 2, 7.04, title, ha="center", va="center", fontsize=9.4,
                fontweight="bold", color="white")
        ax.text(x + cw / 2, 6.70, sub, ha="center", va="center", fontsize=7.4,
                color="white", linespacing=1.25)
        y = 6.30
        for name, desc in items:
            h = 1.14
            y -= h + 0.18
            box(ax, x, y, cw, h, name, desc, color, title_size=8.7, sub_size=7.2)
    ax.text(x0, 0.32,
            "Read across: the project is no longer \"an active-inference method\". It is a "
            "psychometric latent-trait measurement of a comfort-zone level, whose "
            "criticality axis is an\nopen competition - one that the active-inference field "
            "entered, was scored on a design built to separate it from the alternatives, "
            "and lost.",
            fontsize=8.4, color=GREY, va="center", linespacing=1.5)
    fig.tight_layout()
    fig.savefig(FIGS / "paradigm_composition.png", dpi=200, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. The open question: surprise needs a reference distribution
# ---------------------------------------------------------------------------
def fig_reference_crux():
    fig, ax = _fig(12.4, 5.6)
    ax.text(0.35, 5.25, "EVERY SURPRISE MEASURE NEEDS SOMETHING TO BE SURPRISED "
                        "RELATIVE TO", fontsize=11.0, fontweight="bold", color=INK,
            va="center")
    ax.text(0.35, 4.86, "the open question R2.Q5: can the surprise family stand on its "
                        "own as a scenario-agnostic metric once the preference field "
                        "is dropped?",
            fontsize=8.6, color=GREY, va="center")

    box(ax, 0.35, 3.15, 3.05, 1.30, "SURPRISE MEASURE",
        "residual information, Bayesian surprise,\n"
        "antithesis, S8, ... - the src/surprise\n"
        "library, validated and interface-agnostic", PURPLE)
    ax.add_patch(FancyBboxPatch((0.35, 2.50), 3.05, 0.50, boxstyle="round,pad=0.03",
                                facecolor=LOAD, edgecolor="none"))
    ax.text(1.87, 2.75, "unaffected by the R.2 verdict", ha="center", va="center",
            fontsize=7.9, color="white", fontweight="bold")

    box(ax, 4.05, 3.15, 2.55, 1.30, "REFERENCE DISTRIBUTION",
        "the slot the measure is taken\nagainst - and the slot the\n"
        "preference field used to fill", INK, fill=BEIGE, ls="--")
    arrow(ax, (3.45, 3.80), (4.02, 3.80), color=PURPLE)

    cands = [
        ("was: the preference distribution p(o)",
         "calibrated and scenario-agnostic by construction -\n"
         "and its kinematic content is now ruled out", DEAD),
        ("a learned model of normal driving",
         "surprise as departure from what this population\n"
         "normally does; needs naturalistic data", COMP),
        ("a per-driver predictive belief",
         "surprise about the world rather than about\n"
         "preference; the library already serves it", COMP),
    ]
    for i, (name, desc, c) in enumerate(cands):
        y = 3.50 - i * 1.20
        box(ax, 7.25, y, 4.80, 1.02, name, desc, c,
            fill=PAPER if c == DEAD else "white", title_size=8.8, sub_size=7.4,
            ls="--" if c == DEAD else "-")
        arrow(ax, (6.62, 3.80), (7.22, y + 0.51), color=c,
              rad=0.0 if i == 1 else (-0.12 if i == 0 else 0.12))
    ax.text(0.35, 0.45,
            "The falsified object is the preference-field deficit as the criticality "
            "axis - not the surprise family, and not the measurement library.\n"
            "Naming what fills the empty slot is the first task of the exploration, "
            "because without a reference there is no measure.",
            fontsize=8.4, color=GREY, va="center", linespacing=1.5)
    fig.tight_layout()
    fig.savefig(FIGS / "reference_crux.png", dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_stack()
    fig_pipeline()
    fig_axes()
    fig_trait()
    fig_composition()
    fig_reference_crux()
    print("wrote:", *(p.name for p in sorted(FIGS.glob("*.png"))))
