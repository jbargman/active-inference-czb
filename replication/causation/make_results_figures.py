"""
Figures for docs/crash_causation_results.md.

    python replication/causation/make_results_figures.py            # uses --tag real
    python replication/causation/make_results_figures.py --tag ""   # stand-in outputs

Reads replication/causation/out/ (reference_all.csv, cond_<X><tag>.csv/.json) and
replication/causation/data/ (the digitized Bärgman et al. 2024 distributions), writes
PNGs to docs/causation_figures/.

fig_inputs.png   digitized SHRP2 glance PDF and max-deceleration PMF vs the stand-ins
fig_metrics.png  weighted distributions of the Wu et al. metrics: QUADRIS reference
                 vs conditions B (active inference) and C (CBM control)
fig_timing.png   attentive response onset relative to the tau^-1 = 0.2 anchor
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
from causation import CausationConfig                      # noqa: E402
from causation.runner import aggregate                     # noqa: E402
from causation.glances import standin_shrp2_glances, GlanceDistribution   # noqa: E402
from causation.decel import standin_shrp2_max_decel, DecelerationDistribution  # noqa: E402

OUT = HERE / "out"
DATA = HERE / "data"
FIGS = REPO / "docs" / "causation_figures"

# categorical slots, fixed order (dataviz reference palette, light mode)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e4e4e0", "grid.linewidth": 0.6,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "legend.frameon": False,
})


def load_cond(tag: str, c: str):
    df = pd.read_csv(OUT / f"cond_{c}{tag}.csv")
    cfg = CausationConfig.condition(c)
    share = cfg.no_response_share if cfg.no_response_on else 0.0
    return aggregate(df, share)


def whist(ax, x, w, bins, color, label, fill=False):
    h, edges = np.histogram(x, bins=bins, weights=w, density=True)
    xs = np.repeat(edges, 2)[1:-1]
    ys = np.repeat(h, 2)
    if fill:
        ax.fill_between(xs, ys, color=color, alpha=0.25, linewidth=0)
    ax.plot(xs, ys, color=color, linewidth=1.8, label=label)


def fig_inputs():
    g_real = GlanceDistribution.from_csv(DATA / "b24_fig1_glances_shrp2.csv")
    g_stand = standin_shrp2_glances()
    d_real = DecelerationDistribution.from_csv(DATA / "b24_fig3_decel.csv")
    d_stand = standin_shrp2_max_decel()

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 2.7), constrained_layout=True)

    def cond(g):        # conditional-on-off-road probabilities
        return g.durations, g.probability / g.probability.sum()

    t, p = cond(g_real)
    a.bar(t, p, width=0.088, color=BLUE, label="digitized Fig. 1 (SHRP2)")
    t2, p2 = cond(g_stand)
    xs = np.repeat(np.append(t2 - 0.05, t2[-1] + 0.05), 2)[1:-1]
    a.plot(xs, np.repeat(p2, 2), color=ORANGE, linewidth=1.8, label="stand-in (lognormal)")
    a.set_xlim(0, 4)
    a.set_xlabel("off-road glance duration [s]")
    a.set_ylabel("probability per 0.1 s bin")
    a.set_title("Glance durations, conditional on off-road", fontsize=9.5, loc="left")
    a.legend(fontsize=8)

    b.bar(d_real.decel, d_real.probability, width=1.32, color=BLUE,
          label="digitized Fig. 3 (45 crashes)")
    b.plot(d_stand.decel, d_stand.probability, color=ORANGE, linewidth=1.8,
           marker="o", markersize=4, label="stand-in")
    b.set_xlabel("maximum deceleration [m/s²]")
    b.set_ylabel("probability")
    b.set_title("Maximum driver deceleration", fontsize=9.5, loc="left")
    b.legend(fontsize=8)
    fig.savefig(FIGS / "fig_inputs.png", dpi=200)
    plt.close(fig)


def fig_metrics(tag: str):
    ref = pd.read_csv(OUT / "reference_all.csv")
    B = load_cond(tag, "B")
    C = load_cond(tag, "C")
    panels = [
        ("dv_lead", "lead delta-v [m/s]", np.linspace(0, 12, 25)),
        ("t_nr", "no-return time before impact [s]", np.linspace(-1.8, 0, 25)),
        ("a_f_min", "follower min acceleration [m/s²]", np.linspace(-11, 0.5, 24)),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6), constrained_layout=True)
    for ax, (colname, xlabel, bins) in zip(axes, panels):
        whist(ax, ref[colname], ref.omega, bins, BLUE, "QUADRIS reference", fill=True)
        for cond_df, color, label in ((B, ORANGE, "B: active inference"),
                                      (C, AQUA, "C: CBM control")):
            g = cond_df[cond_df.w_crash > 0]
            whist(ax, g[colname], g.w_crash, bins, color, label)
        ax.set_xlabel(xlabel)
    axes[0].set_ylabel("weighted density")
    axes[0].legend(fontsize=7.5)
    fig.savefig(FIGS / "fig_metrics.png", dpi=200)
    plt.close(fig)


def fig_timing(tag: str):
    B = load_cond(tag, "B")
    att = B[(~B.no_response) & (B.schedule.str.startswith("attentive") | (B.schedule == "no glance"))]
    per_seed = att.groupby("seed_id").rt_vs_anchor.first().dropna()
    fig, ax = plt.subplots(figsize=(4.6, 2.6), constrained_layout=True)
    bins = np.arange(-1.0, 4.01, 0.25)
    ax.hist(per_seed, bins=bins, color=ORANGE, alpha=0.85)
    top = ax.get_ylim()[1]
    ax.axvline(0.5, color=AQUA, linewidth=2.2)
    ax.text(0.44, top * 0.97, "CBM: fixed 0.5 s", color=INK, fontsize=8.5,
            ha="right", va="top")
    med = float(per_seed.median())
    ax.axvline(med, color=INK, linewidth=1.0, linestyle="--")
    ax.text(med + 0.08, top * 0.72, f"median {med:.2f} s", color=INK, fontsize=8.5)
    ax.set_title("Attentive brake onsets, condition B (active inference)",
                 fontsize=9.5, loc="left")
    ax.set_xlabel("brake onset relative to the τ⁻¹ = 0.2 s⁻¹ anchor [s]")
    ax.set_ylabel("seeds")
    fig.savefig(FIGS / "fig_timing.png", dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="real")
    args = ap.parse_args()
    tag = ("_" + args.tag) if args.tag else ""
    FIGS.mkdir(exist_ok=True)
    fig_inputs()
    fig_metrics(tag)
    fig_timing(tag)
    print("wrote", FIGS)


if __name__ == "__main__":
    main()
