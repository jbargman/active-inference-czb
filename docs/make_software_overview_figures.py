"""Generate the block diagrams for `docs/software_overview.md`.

    python docs/make_software_overview_figures.py

Everything lands in docs/software_overview_figures/. The figures are schematics of the
repository's structure: every box names files that exist, and the document states the same
paths in words. No numbers are drawn that are not also stated, with their sources, in the
document. Palette and helpers follow docs/make_ai_scope_figures.py and
docs/handbook/make_diagrams.py so the three figure sets read as one.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
FIGS = HERE / "software_overview_figures"
FIGS.mkdir(exist_ok=True)

INK = "#222222"
PURPLE = "#472CBE"
BLUE = "#36B7F6"
TEAL = "#2BAE9A"
PINK = "#C95B9B"
ORANGE = "#E08A2E"
GREY = "#6B7280"
BEIGE = "#F0EDE6"
PAPER = "#FBFAF7"


def _fig(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def box(ax, x, y, w, h, title, sub, color, fill="white", ls="-", title_size=9.5,
        sub_size=7.4, mono=None):
    """A rounded box: bold title, grey subtitle, optional monospace file line at the bottom."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                facecolor=fill, edgecolor=color, linewidth=1.7, linestyle=ls))
    ax.text(x + w / 2, y + h - 0.16, title, ha="center", va="top", fontsize=title_size,
            fontweight="bold", color=INK)
    if sub:
        ax.text(x + w / 2, y + h - 0.50, sub, ha="center", va="top", fontsize=sub_size,
                color=GREY, linespacing=1.25)
    if mono:
        ax.text(x + w / 2, y + 0.12, mono, ha="center", va="bottom", fontsize=6.6,
                color=color, family="monospace")


def arrow(ax, xy0, xy1, color=INK, lw=1.5, rad=0.0, label=None, off=(0, 0.12), fs=7.6,
          style="-|>"):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle=style, mutation_scale=13, lw=lw,
                                 color=color, connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((xy0[0] + xy1[0]) / 2 + off[0], (xy0[1] + xy1[1]) / 2 + off[1], label,
                ha="center", va="center", fontsize=fs, color=color)


def strip(ax, x, y, w, h, title, color=BEIGE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", facecolor=color,
                                edgecolor="none"))
    ax.text(x + 0.18, y + h - 0.16, title, fontsize=8.6, fontweight="bold", color=INK, va="top")


# ---------------------------------------------------------------------------
# 1. The map: the whole repository in blocks
# ---------------------------------------------------------------------------

def fig_map():
    fig, ax = _fig(12.4, 8.0)

    # inputs, left column
    strip(ax, 0.2, 0.9, 2.55, 6.85, "INPUTS (external/, papers/)")
    box(ax, 0.35, 5.85, 2.25, 1.2, "The papers", "7 active-inference papers\n+ the SI; plain text\nfor searching",
        GREY, mono="papers/  notes/paper_text/")
    box(ax, 0.35, 4.4, 2.25, 1.25, "The authors' code", "PyTorch reference model;\none logged patch",
        PURPLE, mono="external/aica/")
    box(ax, 0.35, 2.95, 2.25, 1.25, "The OSF deposit", "every published run,\nper timestep, 3.1 GB",
        PURPLE, mono="external/gs4bu-...")
    box(ax, 0.35, 1.1, 2.25, 1.65, "Human data", "video studies (cut-in,\novertake, left turn),\n"
        "the 2013 test track,\nQUADRIS seeds", TEAL, mono="external/01_Studies/ ...")

    # engines, middle
    strip(ax, 3.1, 0.9, 5.6, 6.85, "ENGINES (src/) AND THEIR RUNNERS (replication/)")
    box(ax, 3.3, 5.55, 2.5, 1.5, "1  The reference model", "run the authors' model on\none condition; compare\n"
        "with the deposit", PURPLE, mono="replication/*.py")
    box(ax, 6.0, 5.55, 2.5, 1.5, "2  Our readable mirror", "NumPy re-implementation;\nthe preference\n"
        "function p(o)", BLUE, mono="src/aidriver/")
    box(ax, 3.3, 3.65, 2.5, 1.5, "3  Surprise library", "three families of surprise\n+ the accumulator,\n"
        "one interface", ORANGE, mono="src/surprise/")
    box(ax, 6.0, 3.65, 2.5, 1.5, "4  Comfort-zone method", "gate x axis x level;\nthe cards and\n"
        "their outputs", TEAL, mono="src/comfortzone/  replication/czb/")
    box(ax, 3.3, 1.75, 2.5, 1.5, "5  Crash causation", "QUADRIS seeds, glance and\ndeceleration components,\n"
        "equivalence testing", PINK, mono="src/{quadris,causation,equivalence}/")
    box(ax, 6.0, 1.75, 2.5, 1.5, "6  Split-site transfer", "bundles between sites\nthat share no data;\n"
        "the interface schema", GREY, mono="transfer/  src/comfortzone/interface.py")

    # outputs, right column
    strip(ax, 9.05, 0.9, 3.15, 6.85, "OUTPUTS")
    box(ax, 9.2, 5.55, 2.85, 1.5, "Tracked results", "one report per card;\nthe worklog and the\nquery register",
        INK, mono="replication/czb/out/  .../causation/")
    box(ax, 9.2, 3.65, 2.85, 1.5, "Documents", "handbook, design notes,\nreviews, handovers;\n"
        "md -> docx + pdf", INK, mono="docs/  notes/  handover*.md")
    box(ax, 9.2, 1.75, 2.85, 1.5, "Decks and tools", "four talks with animations;\nthree browser explorers",
        INK, mono="presentation/talk/  tools/czb_explorer/")

    # arrows: inputs -> engines
    arrow(ax, (2.6, 5.0), (3.3, 6.3), color=PURPLE, rad=-0.2)
    arrow(ax, (2.6, 3.6), (3.3, 6.0), color=PURPLE, rad=-0.35)
    arrow(ax, (2.6, 2.0), (6.0, 4.2), color=TEAL, rad=-0.15)
    arrow(ax, (2.6, 1.6), (3.3, 2.3), color=TEAL, rad=0.1)
    # engines -> engines
    arrow(ax, (7.25, 5.55), (7.25, 5.15), color=BLUE, label="p(o)", off=(0.35, 0))
    arrow(ax, (5.8, 4.4), (6.0, 4.4), color=ORANGE)
    arrow(ax, (4.55, 3.65), (4.55, 3.25), color=ORANGE)
    arrow(ax, (7.25, 3.65), (7.25, 3.25), color=TEAL)
    # engines -> outputs
    arrow(ax, (8.5, 4.4), (9.2, 6.0), color=INK, rad=-0.2)
    arrow(ax, (8.5, 2.5), (9.2, 5.8), color=INK, rad=-0.3)
    arrow(ax, (10.6, 5.55), (10.6, 5.15), color=INK)
    arrow(ax, (10.6, 3.65), (10.6, 3.25), color=INK)

    # the floor: tests and conventions
    ax.add_patch(FancyBboxPatch((0.2, 0.12), 12.0, 0.62, boxstyle="round,pad=0.04",
                                facecolor="white", edgecolor=INK, linewidth=1.4, linestyle="--"))
    ax.text(6.2, 0.43, "THE FLOOR: ten property-test scripts (tests/), the standing rules (docs/czb_work_orders.md "
            "section 2), the worklog and its query register, one commit per card",
            ha="center", va="center", fontsize=8.2, color=INK)
    fig.tight_layout()
    fig.savefig(FIGS / "map.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. The reference model as a loop, with the file behind each stage
# ---------------------------------------------------------------------------

def fig_reference_loop():
    fig, ax = _fig(12.0, 5.4)
    strip(ax, 0.2, 4.45, 11.6, 0.8, "THE WORLD: bicycle-model vehicles and the other vehicle's script")
    ax.text(6.0, 4.62, "external/aica/src/<scenario>/dynamics_true.py, decoder_true.py   "
            "(observation noise here is the assumed noise x0.001)", ha="center", fontsize=7.4,
            color=GREY, family="monospace")
    stages = [
        (0.35, 2.35, 2.05, 1.7, "SENSE", "the lead as an optical\nangle and its rates\n(looming), not meters",
         BLUE, "decoder.py"),
        (2.7, 2.35, 2.05, 1.7, "BELIEVE", "75 particles; weights\nfrom the assumed\nobservation noise",
         PURPLE, "encoder.py  particle_filter.py"),
        (5.05, 2.35, 2.05, 1.7, "PREDICT", "roll each particle 6 s\nahead; other vehicle\nbiased toward norms",
         TEAL, "dynamics.py"),
        (7.4, 2.35, 2.05, 1.7, "EVALUATE", "score plans on sampled\nobservations: six\npreference terms + info",
         PINK, "belief_reward.py  reward.py"),
        (9.75, 2.35, 1.95, 1.7, "ACT", "execute the first\nstep of the kept plan",
         INK, "mpc_discrete.py"),
    ]
    for s in stages:
        box(ax, *s[:7], mono=s[7])
    arrow(ax, (1.4, 4.45), (1.4, 4.05), color=BLUE)
    for x in (2.4, 4.75, 7.1, 9.45):
        arrow(ax, (x, 3.2), (x + 0.3, 3.2))
    arrow(ax, (10.7, 4.05), (10.7, 4.45))
    box(ax, 3.4, 0.35, 5.2, 1.45, "THE EVIDENCE ACCUMULATOR (the surprise gate)",
        "each step add 10^EA_fac x the shortfall of the plan being followed; cross 1 -> full re-plan.\n"
        "Card GZ.2: in steady following the shortfall is the collision-and-safety term alone",
        PURPLE, ls="--", mono="mpc_discrete.py: evidence, returns_initial, returns_optimized")
    arrow(ax, (8.4, 2.3), (7.6, 1.85), color=PURPLE, rad=-0.25)
    arrow(ax, (4.2, 1.85), (3.6, 2.3), color=PURPLE, rad=-0.25, label="re-plan", off=(-0.75, -0.05))
    ax.text(0.3, 0.55, "Config -> run -> pickle:\nsrc/utils/simulation.py\nsimulation_<scenario>.py",
            fontsize=7.2, color=GREY, family="monospace", va="bottom")
    ax.text(11.7, 0.55, "Our mirror, same stages,\nNumPy, readable:\nsrc/aidriver/agent.py",
            fontsize=7.2, color=BLUE, family="monospace", va="bottom", ha="right")
    fig.tight_layout()
    fig.savefig(FIGS / "reference_loop.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Replication: how a run is made and checked
# ---------------------------------------------------------------------------

def fig_replication():
    fig, ax = _fig(14.4, 4.6)
    # Track A, the authors' code
    box(ax, 0.3, 2.5, 2.4, 1.6, "One condition", "speed, gap, lead braking;\nthe paper's 28-cell grid\n"
        "is far too costly on CPU", GREY, mono="run_rear_end_single.py")
    box(ax, 3.2, 2.5, 2.4, 1.6, "The authors' simulate()", "unmodified; about 18 s\nof CPU per step; a\n"
        ".partial checkpoint as it goes", PURPLE, mono="external/aica/simulation_*.py")
    box(ax, 6.1, 2.5, 2.4, 1.6, "A run pickle", "true state, observations,\nbelief, plans, per-term\n"
        "values, per step", INK, mono="replication/*.pkl")
    box(ax, 9.0, 2.5, 2.7, 1.6, "Compare", "response times, maneuvers,\ncollisions against the paper\n"
        "and against the deposit", TEAL, mono="validate.py  validate_osf.py")
    for x in (2.7, 5.6, 8.5):
        arrow(ax, (x, 3.3), (x + 0.5, 3.3))
    ax.text(0.3, 4.3, "TRACK A: the authors' code, one condition at a time", fontsize=8, color=PURPLE,
            fontweight="bold")
    # Track B, our mirror
    box(ax, 0.3, 0.35, 2.4, 1.5, "Our mirror", "the NumPy agent, same\nmechanisms, readable",
        BLUE, mono="src/aidriver/agent.py")
    box(ax, 3.2, 0.35, 2.4, 1.5, "The 28-cell sweep", "140 runs; appends and\nfsyncs each row, restartable",
        BLUE, mono="sweep_rear_end_aidriver.py")
    box(ax, 6.1, 0.35, 2.4, 1.5, "Sweep outputs", "2 of 6 published relations\nreproduce; timing not trusted",
        BLUE, mono="sweep_aidriver.csv  results_*.pkl")
    for x in (2.7, 5.6):
        arrow(ax, (x, 1.1), (x + 0.5, 1.1), color=BLUE)
    arrow(ax, (8.5, 1.1), (9.6, 2.5), color=BLUE, rad=-0.2)
    ax.text(0.3, 2.05, "TRACK B: our re-implementation, swept", fontsize=8, color=BLUE, fontweight="bold")
    # the deposit feeds the comparison; the review hangs off the deposit
    box(ax, 9.0, 0.35, 2.7, 1.5, "The OSF deposit", "the same pickles for every\npublished run, 32 seeds;\n"
        "the ground truth", PURPLE, mono="external/gs4bu-osfstorage-archive/")
    arrow(ax, (10.35, 1.85), (10.35, 2.5), color=PURPLE)
    box(ax, 12.0, 0.35, 2.2, 1.5, "The review of the paper", "deposit-level checks:\nroad departures, the\n"
        "accumulator in following", PINK, mono="review_osf.py\n-> docs/method_review.md")
    arrow(ax, (11.7, 1.1), (12.0, 1.1), color=PINK)
    fig.tight_layout()
    fig.savefig(FIGS / "replication_flow.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. The comfort-zone pipeline
# ---------------------------------------------------------------------------

def fig_czb_pipeline():
    fig, ax = _fig(12.4, 6.4)
    strip(ax, 0.2, 4.9, 12.0, 1.3, "THE MODEL, IN ONE LINE (handbook chapter 13)")
    ax.text(6.2, 5.35, "share who intervene  =  lapse + (1 - lapse) x GATE x Phi((AXIS - LEVEL) / spread)",
            ha="center", fontsize=11, color=INK, family="monospace", fontweight="bold")
    ax.text(6.2, 5.02, "GATE: does the other vehicle count yet?    AXIS: the number read off the scene    "
            "LEVEL: where one driver says 'now'    percentile over drivers' levels = the deliverable",
            ha="center", fontsize=7.4, color=GREY)

    box(ax, 0.3, 2.7, 2.3, 1.75, "Human data", "clip ratings and button\npresses: two cut-in studies,\n"
        "cyclist overtake, left turn;\nthe 2013 test track", TEAL, mono="external/01_Studies/  02_LTAPOD_DBIN/")
    box(ax, 2.95, 2.7, 2.3, 1.75, "Loaders", "one module per scenario\nturns traces and responses\n"
        "into cells: stimulus,\nn, share who intervened", TEAL, mono="src/comfortzone/cutin.py\novertake.py  ltap.py  czb_data.py")
    box(ax, 5.6, 2.7, 2.3, 1.75, "Axis and gate", "looming rate (cut-in),\ndistance (left turn);\n"
        "a 3 s projected-clearance\ngate in front", TEAL, mono="cutin2_looming.py  cutin2_gate.py\nltap_two_axis.py")
    box(ax, 8.25, 2.7, 2.3, 1.75, "Level", "hierarchical fit of each\ndriver's level; held out\n"
        "by driver and by cell", TEAL, mono="fit_stage1_looming.py\ndriver_levels.py")
    box(ax, 10.9, 2.7, 1.3, 1.75, "Percentile", "over drivers'\nlevels", TEAL, mono="percentile_\nsensitivity.py")
    for x in (2.6, 5.25, 7.9, 10.55):
        arrow(ax, (x, 3.6), (x + 0.35, 3.6), color=TEAL)

    box(ax, 0.3, 0.35, 3.6, 1.8, "Every card is a pre-registered script",
        "models, folds, metric and the decision rule in the\ndocstring before the run; the report is generated,\n"
        "never edited; the worklog gets a paragraph and queries", INK, ls="--",
        mono="replication/czb/<card>.py -> out/<card>.md")
    box(ax, 4.25, 0.35, 3.6, 1.8, "What was tried and ruled out",
        "the field itself as the axis (R.2); surprise as\nthe onset (HS.1); Farewell's levels (PT.1);\n"
        "the own-lane norm as the onset (PN.1)", PINK, ls="--",
        mono="docs/r2_gate_decisions.md\nout/hs1_*.md  out/pt1_*.md  out/pn1_*.md")
    box(ax, 8.2, 0.35, 4.0, 1.8, "What survives",
        "the per-driver level is a trait across scenarios\n(TR.1); video and real turns agree (TT.1);\n"
        "the static field and its closed-form boundary", TEAL, ls="--",
        mono="out/driver_levels.md  out/ltapod_testtrack.md\nsrc/comfortzone/field.py")
    fig.tight_layout()
    fig.savefig(FIGS / "czb_pipeline.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. The surprise library
# ---------------------------------------------------------------------------

def fig_surprise():
    fig, ax = _fig(12.0, 4.4)
    box(ax, 0.3, 1.3, 2.6, 2.2, "Distributions", "Gaussian, Gaussian mixture,\nparticle set, categorical;\n"
        "one protocol so every\nmeasure runs on all four", ORANGE, mono="distributions.py")
    fam = [
        (3.4, 2.85, "Probabilistic mismatch", "observation vs prior belief:\nsurprisal, residual information,\nBayes factor",
         "probabilistic.py"),
        (3.4, 1.3, "Belief mismatch", "posterior vs prior belief:\nBayesian, antithesis,\nconfidence-corrected",
         "belief.py"),
        (6.5, 2.85, "Observation mismatch", "observation vs point prediction:\nabsolute, squared, unsigned RPE",
         "observation.py"),
        (6.5, 1.3, "Preference-relative", "expected future vs preferred:\npragmatic value, and the\naccumulator that times a response",
         "pragmatic.py"),
    ]
    for x, y, t, s, m in fam:
        box(ax, x, y, 2.85, 1.35, t, s, ORANGE, mono=m)
    for y in (3.5, 1.95):
        arrow(ax, (2.9, y), (3.4, y), color=ORANGE)
    box(ax, 9.75, 2.85, 2.0, 1.35, "Streams", "any measure over a\nsequence of predictions", ORANGE,
        mono="timeseries.py")
    box(ax, 9.75, 1.3, 2.0, 1.35, "Situational", "when a situation stops\nunfolding as expected\n(card HS.1)",
        ORANGE, mono="situational.py")
    arrow(ax, (9.35, 3.5), (9.75, 3.5), color=ORANGE)
    arrow(ax, (9.35, 1.95), (9.75, 1.95), color=ORANGE)
    ax.text(6.0, 0.55, "Used by: the crash-causation response model (block 5), the R.1 accumulator test, card HS.1. "
            "Tests check the claims: the zero floor, invariance to discretization, the published equivalences.",
            ha="center", fontsize=7.6, color=GREY)
    fig.tight_layout()
    fig.savefig(FIGS / "surprise_families.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Crash causation
# ---------------------------------------------------------------------------

def fig_causation():
    fig, ax = _fig(12.0, 4.6)
    box(ax, 0.3, 2.5, 2.3, 1.7, "QUADRIS seeds", "5 000 synthetic rear-end\ncrashes: lead profile,\n"
        "follower state, weight", PINK, mono="src/quadris/")
    box(ax, 3.0, 2.5, 2.6, 1.7, "Causation components", "off-road glances, a\ndeceleration cap, no\n"
        "response; each switchable", PINK, mono="src/causation/{glances,decel,config}.py")
    box(ax, 6.0, 2.5, 2.6, 1.7, "Two response processes", "active-inference accumulator\non the field (tier 1);\n"
        "the CBM's fixed delay", PINK, mono="src/causation/response.py")
    box(ax, 9.0, 2.5, 2.7, 1.7, "Generated crashes", "per seed x schedule x bin;\nrestartable runner",
        PINK, mono="src/causation/runner.py\nreplication/causation/run_quadris.py")
    for x in (2.6, 5.6, 8.6):
        arrow(ax, (x, 3.35), (x + 0.4, 3.35), color=PINK)
    box(ax, 6.0, 0.35, 2.6, 1.6, "Equivalence test", "Wu et al. binning and ROPE;\ngeneric, reusable,\n"
        "knows nothing of driving", PINK, mono="src/equivalence/")
    arrow(ax, (10.35, 2.5), (8.6, 1.15), color=PINK, rad=0.2)
    box(ax, 9.0, 0.35, 2.7, 1.6, "Tier 2: the closed loop", "the authors' agent on the\nsame seeds, lead replayed;\n"
        "also the gaze probes GZ.1, GZ.2", PURPLE, mono="tier2_rear_end.py  gz1_*.py  gz2_*.py")
    box(ax, 0.3, 0.35, 5.3, 1.6, "Results and their reading", "docs/crash_causation_plan.md -> results.md; "
        "the severity-timing\ndissociation and the ROPE calibration are separate notes", INK, ls="--",
        mono="docs/severity_vs_timing.md  docs/equivalence_rope_note.md")
    fig.tight_layout()
    fig.savefig(FIGS / "causation_flow.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 7. The split-site transfer
# ---------------------------------------------------------------------------

def fig_transfer():
    fig, ax = _fig(12.0, 4.4)
    strip(ax, 0.2, 0.3, 4.8, 3.9, "CHALMERS (this repository)", color=PAPER)
    strip(ax, 7.0, 0.3, 4.8, 3.9, "VOLVO CARS (their repository, their data)", color=PAPER)
    box(ax, 0.4, 2.3, 2.1, 1.4, "Shared layer", "model code, scripts,\ndocuments, fixtures,\naggregate results",
        GREY, mono="transfer_policy.yaml says what")
    box(ax, 2.7, 2.3, 2.1, 1.4, "Synthetic fixture", "twelve made-up events\nin the interface shape",
        GREY, mono="make_synthetic_fixture.py")
    box(ax, 0.4, 0.5, 4.4, 1.4, "The reader", "turns interface files into the gated-looming\npipeline's inputs "
        "(card NDS.1)", TEAL, mono="src/comfortzone/interface.py  nds1_interface_smoke.py")
    box(ax, 7.2, 2.3, 2.1, 1.4, "Raw data", "never moves; per-event\nderived data never moves",
        PINK, mono="stays at VCC")
    box(ax, 9.5, 2.3, 2.1, 1.4, "Their adapter", "writes the interface\nshape from their data",
        GREY, mono="interface_schema.yaml")
    box(ax, 7.2, 0.5, 4.4, 1.4, "The same reader and scripts", "run at VCC on real events;\nonly aggregate "
        "results come back", TEAL, mono="validate_interface.py checks before any script reads")
    box(ax, 5.15, 1.5, 1.7, 1.5, "Bundles", "zip + manifest +\nreview sheet;\nchanged files only,\nby hash",
        INK, mono="bundle.py")
    arrow(ax, (4.8, 3.0), (5.15, 2.6), color=INK, rad=0.1)
    arrow(ax, (6.85, 2.6), (7.2, 3.0), color=INK, rad=0.1)
    arrow(ax, (7.2, 1.2), (6.85, 1.7), color=INK, rad=0.1, label="aggregates\nonly", off=(0.55, -0.15))
    arrow(ax, (5.15, 1.7), (4.8, 1.2), color=INK, rad=0.1)
    ax.text(6.0, 0.15, "Paused by Jonas 2026-09-11 until a new VCC round starts; the protocol and tooling are ready "
            "(docs/split_site_protocol.md)", ha="center", fontsize=7.4, color=GREY)
    fig.tight_layout()
    fig.savefig(FIGS / "transfer_flow.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 8. The working cycle: how a card runs
# ---------------------------------------------------------------------------

def fig_work_cycle():
    fig, ax = _fig(12.0, 4.2)
    steps = [
        (0.3, "Pick the card", "handover.md section 4;\nits 'after' query\nmust be answered", GREY,
         "handover.md  docs/czb_work_orders.md"),
        (2.65, "Pre-state", "models, folds, metric,\ndecision rule in the\ndocstring, then run", INK,
         "replication/czb/<card>.py"),
        (5.0, "Generated report", "written by the script;\nnever hand-edited;\nlong runs in the background", INK,
         "out/<card>.md  (+ .csv, .pkl)"),
        (7.35, "Worklog + queries", "one paragraph per card;\n@CARD.Qn(severity, who);\nregister compiled by script", PURPLE,
         "out/worklog.md  collect_queries.py"),
        (9.7, "Suite green, commit", "ten test scripts before\nand after; one commit\nper card; push on request", TEAL,
         "tests/*.py"),
    ]
    for x, t, s, c, m in steps:
        box(ax, x, 1.6, 2.1, 1.85, t, s, c, mono=m)
    for x in (2.4, 4.75, 7.1, 9.45):
        arrow(ax, (x, 2.5), (x + 0.25, 2.5))
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 11.5, 0.9, boxstyle="round,pad=0.04", facecolor=BEIGE,
                                edgecolor="none"))
    ax.text(6.05, 0.75, "Rules that bind every session (docs/czb_work_orders.md section 2): numbers only from committed "
            "scripts; never change a default in src/aidriver/preferences.py;\nnever edit a pre-registered script; "
            "questions go in the worklog and do not stop the work; markdown is the source, docx and pdf are built from it",
            ha="center", va="center", fontsize=7.4, color=INK, linespacing=1.4)
    fig.tight_layout()
    fig.savefig(FIGS / "work_cycle.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_map()
    fig_reference_loop()
    fig_replication()
    fig_czb_pipeline()
    fig_surprise()
    fig_causation()
    fig_transfer()
    fig_work_cycle()
    print("wrote", sorted(p.name for p in FIGS.glob("*.png")))
