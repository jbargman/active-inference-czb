"""Perceived-safety ratings against the comfort-zone field, Random cut-in trials.

Jonas's question (2026-08-27): to what extent does the drivers' rating of how safe they
feel correlate with the field? The `PS` column is stored so that HIGHER values mean
LOWER perceived safety (DATA_DICTIONARY gotcha 1), i.e. it is a perceived-unsafety
rating on 0-10; the expected relation with the deficit is therefore positive.

Writes figures/ps_vs_field.png and prints the correlations.

    python replication/czb/ps_vs_field.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import pearsonr, spearmanr  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from comfortzone.czb_data import random_cutin_trials  # noqa: E402

MUTED = "#52514e"
CRIT_COLORS = {"TTC4": "#b00020", "TTC6": "#eda100", "TTC8": "#2a78d6"}
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#e4e4e0",
    "grid.linewidth": 0.6, "figure.facecolor": "white", "legend.frameon": False,
})


def main() -> None:
    r = random_cutin_trials().dropna(subset=["ps"])
    sp_t = spearmanr(r.deficit_max, r.ps)
    cells = (r.groupby(["criticality", "timepoint"])
              .agg(ps=("ps", "mean"), ps_sem=("ps", lambda s: s.std() / np.sqrt(len(s))),
                   d=("deficit_max", "first"), t_end=("t_end", "first"))
              .reset_index())
    sp_c = spearmanr(cells.d, cells.ps)
    pe_c = pearsonr(cells.d, cells.ps)
    print(f"{len(r)} trials. Trial-level Spearman rho = {sp_t.statistic:.3f}; "
          f"cell-level (18 cells) Spearman rho = {sp_c.statistic:.3f}, "
          f"Pearson r = {pe_c.statistic:.3f}")
    for crit in CRIT_COLORS:
        g = r[r.criticality == crit]
        print(f"  within {crit}: trial-level Spearman rho = "
              f"{spearmanr(g.deficit_max, g.ps).statistic:.3f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.0))

    for crit, col in CRIT_COLORS.items():
        g = cells[cells.criticality == crit].sort_values("timepoint")
        ax1.errorbar(g.d, g.ps, yerr=g.ps_sem, color=col, marker="o", ms=4, lw=1.2,
                     capsize=2, label=crit)
        ax2.errorbar(g.t_end, g.ps, yerr=g.ps_sem, color=col, marker="o", ms=4, lw=1.4,
                     capsize=2, label=f"{crit} rating")
        ax2b = ax2  # deficit on the same panel, scaled to the rating axis
    # scaled deficit overlays: map deficit range onto the rating range for shape comparison
    dmax = cells.d.max()
    for crit, col in CRIT_COLORS.items():
        g = cells[cells.criticality == crit].sort_values("timepoint")
        ax2.plot(g.t_end, g.d / dmax * 10, color=col, ls="--", lw=1.0, alpha=0.6)

    ax1.set_xlabel("comfort-zone deficit at clip end (running max)")
    ax1.set_ylabel("perceived unsafety, mean rating 0–10\n(stored as PS; higher = less safe)")
    ax1.set_title(f"18 cells: Spearman ρ = {sp_c.statistic:.2f}, Pearson r = {pe_c.statistic:.2f}")
    ax1.legend()
    ax2.set_xlabel("clip end, seconds after lane-change onset (C1–C6)")
    ax2.set_ylabel("rating (solid) / deficit scaled to 0–10 (dashed)")
    ax2.set_title("Shape over time: ratings keep rising where the deficit\n"
                  "compresses — the accumulator's signature again")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    out = REPO / "figures" / "ps_vs_field.png"
    fig.savefig(out, dpi=150)
    print("wrote", out)


if __name__ == "__main__":
    main()
