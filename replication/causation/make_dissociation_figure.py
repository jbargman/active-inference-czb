"""Figures for docs/severity_vs_timing.md.

fig_dissociation.png  severity CDFs for reference/A/B/C against their crash rates:
                      timing changes how MANY crashes, components change how HARD
fig_metric_shapes.png why theta misreads three of the four metrics: a smooth variable,
                      a discrete lattice, and two distributions with a large atom at zero

    python replication/causation/make_dissociation_figure.py
"""
from __future__ import annotations

import json
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
from causation.runner import aggregate                                    # noqa: E402
from equivalence.binned import quantile_bin_edges                         # noqa: E402

OUT = HERE / "out"
FIGS = REPO / "docs" / "causation_figures"

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED = "#0b0b0b", "#52514e"
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e4e4e0", "grid.linewidth": 0.6,
    "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
})


def load(c: str, tag: str, ref: pd.DataFrame):
    df = pd.read_csv(OUT / f"cond_{c}{tag}.csv")
    cfg = json.loads((OUT / f"cond_{c}{tag}.json").read_text())["config"]
    a = aggregate(df,
                  no_response_share=cfg.get("no_response_share", 0.0) if cfg.get("no_response_on") else 0.0,
                  abnormal_share=cfg.get("abnormal_share", 0.0) if cfg.get("abnormal_on") else 0.0)
    pc = a.groupby("seed_id").p_crash_seed.first()
    wp = float((pc * ref.set_index("seed_id").omega.reindex(pc.index)).sum() / ref.omega.sum())
    return a[a.w_crash > 0], wp


def wcdf(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float)
    m = np.isfinite(x); x, w = x[m], w[m]
    o = np.argsort(x)
    return x[o], np.cumsum(w[o]) / w[o].sum()


def main() -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    ref = pd.read_csv(OUT / "reference_all.csv")
    wr = ref.omega.to_numpy()
    v_ref = 2.0 * ref.dv_lead.to_numpy()

    conds = [("A", "_fullp", "A: attentive, cap only", AQUA),
             ("C", "_fullp", "C: CBM control", ORANGE),
             ("B", "_fullp", "B: active inference", BLUE)]
    loaded = {c: load(c, t, ref) for c, t, _, _ in conds}

    # ---------------- figure 1: the dissociation ---------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.2),
                                   gridspec_kw={"width_ratios": [1.55, 1]})
    x, y = wcdf(v_ref, wr)
    ax1.plot(x, y, color=MUTED, lw=3.0, alpha=.55, label="QUADRIS reference", zorder=1)
    for c, t, lbl, col in conds:
        g, wp = loaded[c]
        x, y = wcdf(g.v_rel_impact.to_numpy(), g.w_crash.to_numpy())
        ax1.plot(x, y, color=col, lw=1.7, label=f"{lbl}  (p={wp:.3f})", zorder=2)
    ax1.set_xlim(0, 14)
    ax1.set_xlabel("relative speed at impact [m/s]  (severity)")
    ax1.set_ylabel("weighted cumulative share")
    ax1.set_title("Severity distributions are nearly the same...", fontsize=10)
    ax1.legend(fontsize=8.5, loc="lower right")

    names = [lbl.split(":")[0] for _, _, lbl, _ in conds]
    rates = [loaded[c][1] for c, _, _, _ in conds]
    cols = [col for _, _, _, col in conds]
    bars = ax2.bar(names, rates, color=cols, width=.62)
    for b, r in zip(bars, rates):
        ax2.text(b.get_x() + b.get_width() / 2, r + .006, f"{r:.3f}", ha="center", fontsize=9)
    ax2.set_ylabel("weighted crash probability")
    ax2.set_title("...while crash rates differ 4.7-fold", fontsize=10)
    ax2.set_ylim(0, .34)
    fig.suptitle("Response timing changes how many crashes happen, not how severe they are",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_dissociation.png", dpi=170)
    print("wrote", FIGS / "fig_dissociation.png")

    # ---------------- figure 2: metric shapes ------------------------------
    gB, _ = loaded["B"]
    panels = [
        ("severity: v_rel [m/s]", v_ref, wr, gB.v_rel_impact.to_numpy(), gB.w_crash.to_numpy(),
         "smooth and continuous\n-> theta is meaningful"),
        ("urgency: t_nr [s]", ref.t_nr.to_numpy(), wr, gB.t_nr.to_numpy(), gB.w_crash.to_numpy(),
         "discrete 0.05 s lattice\n-> theta measures quantization"),
        ("follower brake: a_f,min [m/s$^2$]", ref.a_f_min.to_numpy(), wr,
         gB.a_f_min.to_numpy(), gB.w_crash.to_numpy(),
         "48% atom at zero\n-> quantile bins collapse"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.9))
    for ax, (name, r, w1, s, w2, note) in zip(axes, panels):
        m1, m2 = np.isfinite(r), np.isfinite(s)
        lo = np.percentile(np.concatenate([r[m1], s[m2]]), 1)
        hi = np.percentile(np.concatenate([r[m1], s[m2]]), 99)
        bins = np.linspace(lo, hi, 70)
        ax.hist(r[m1], bins=bins, weights=w1[m1] / w1[m1].sum(), color=MUTED, alpha=.45,
                label="QUADRIS reference")
        ax.hist(s[m2], bins=bins, weights=w2[m2] / w2[m2].sum(), histtype="step", lw=1.7,
                color=BLUE, label="condition B")
        e = quantile_bin_edges(r[m1], 5, w1[m1])
        for v in e[1:-1]:
            ax.axvline(float(v), color=ORANGE, lw=1.0, ls=":")
        ax.set_title(name, fontsize=10)
        ax.set_ylabel("weighted share")
        ax.text(.03, .97, note, transform=ax.transAxes, va="top", fontsize=8.5, color=MUTED)
    axes[0].legend(fontsize=8.5, loc="upper right")
    fig.suptitle("The same statistic on three different kinds of distribution "
                 "(dotted = the reference's 5 quantile bin edges)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_metric_shapes.png", dpi=170)
    print("wrote", FIGS / "fig_metric_shapes.png")


if __name__ == "__main__":
    main()
