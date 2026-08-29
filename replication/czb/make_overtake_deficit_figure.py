"""The per-criticality deficit figure for the cyclist overtake that card B.1 asked for.

Left panel: the comfort-zone deficit along each clearance condition's clip (time since
manoeuvre onset), with the C1-C5 clip-end times marked -- the visual form of the
finding in `out/overtake_field_check.md` that the field does not order the conditions
the way the clearance label does. Right panel: the 15 cells' covariate against the
observed intervention rate, one series per clearance.

Covariates under the shown-window convention (2026-08-29, `out/c1_covariate_defect.md`).

Run:  python replication/czb/make_overtake_deficit_figure.py
Output: figures/overtake_deficit_by_criticality.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from comfortzone.czb_data import (RANDOM_CLIP_LEAD_S, TIMEPOINT_OFFSET_S,  # noqa: E402
                                  overtake_stimulus_field, random_overtake_trials)
from comfortzone.overtake import RANDOM_OVERTAKE_TRACES  # noqa: E402

FIG = REPO / "figures" / "overtake_deficit_by_criticality.png"
COLORS = {"0.5m": "#c1272d", "1m": "#e69f00", "1.5m": "#0072b2"}


def main() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    for crit, path in RANDOM_OVERTAKE_TRACES.items():
        f = overtake_stimulus_field(path, accum_lead_s=RANDOM_CLIP_LEAD_S)
        m = (f.t_since_onset >= -2.0) & (f.t_since_onset <= 1.6)
        ax1.plot(f.t_since_onset[m], f.deficit[m], color=COLORS[crit],
                 label=f"clearance {crit}")
    for tp, off in TIMEPOINT_OFFSET_S.items():
        if tp == "C6":
            continue
        ax1.axvline(off, color="gray", lw=0.6, ls=":")
        ax1.text(off, ax1.get_ylim()[1] * 0.97, tp, ha="center", va="top",
                 fontsize=8, color="gray")
    ax1.set_xlabel("time since manoeuvre onset [s]")
    ax1.set_ylabel("comfort-zone deficit")
    ax1.set_title("Deficit along the clip (clip-end times C1-C5 dotted)")
    ax1.legend(frameon=False, fontsize=9)

    tr = random_overtake_trials()
    g = (tr.groupby(["criticality", "timepoint"], observed=True)
           .agg(x=("deficit_max", "first"), y=("intervene", "mean")).reset_index())
    for crit in COLORS:
        gc = g[g.criticality == crit].sort_values("timepoint")
        ax2.plot(gc.x, gc.y, "o-", color=COLORS[crit], label=f"clearance {crit}")
        for _, row in gc.iterrows():
            ax2.annotate(row.timepoint, (row.x, row.y), fontsize=7,
                         xytext=(3, 3), textcoords="offset points")
    ax2.set_xlabel("deficit_max at clip end (shown-window covariate)")
    ax2.set_ylabel("observed P(intervene)")
    ax2.set_title("The 15 cells: covariate vs response")
    ax2.legend(frameon=False, fontsize=9)

    fig.suptitle("Cyclist overtake: the field against the clearance manipulation",
                 fontsize=11)
    fig.tight_layout()
    FIG.parent.mkdir(exist_ok=True)
    fig.savefig(FIG, dpi=150)
    print(f"wrote {FIG}")
    print(g.pivot(index="timepoint", columns="criticality", values="x").round(1))


if __name__ == "__main__":
    main()
