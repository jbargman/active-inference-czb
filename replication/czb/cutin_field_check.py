"""Validation of the continuous lane-entry field on the study's cut-in stimuli.

Produces the numbers and the figure behind docs/lane_entry_note.md section 5: the
comfort-zone deficit along every car and truck cut-in clip under (i) the released binary
preference function with default staging -- the configuration that could not tell TTC4
from TTC8 -- and (ii) the continuous forms with the clip's own desired speed.

    python replication/czb/cutin_field_check.py

Writes figures/cutin_field_check.png and prints a markdown-ready block.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))

from aidriver.preferences import PreferenceParams, pragmatic_deficit          # noqa: E402
from comfortzone.cutin import (load_cutin_trace, cutin_obs, cutin_params,
                               cutin_predictors)                              # noqa: E402

BASE = REPO / ("external/01_studies/01_Studies/01_Sequence_Random_ButtonPress/"
               "Kinematics/Button_Press_Study")
FIGS = REPO / "figures"

BLUE, ORANGE, MUTED = "#2a78d6", "#eb6834", "#52514e"
plt.rcParams.update({
    "font.size": 9.5, "axes.edgecolor": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#e4e4e0",
    "grid.linewidth": 0.6, "figure.facecolor": "white", "legend.frameon": False,
})

TIMEPOINTS = [0.0, 0.3, 0.6, 0.9, 1.2, 1.5]           # C1..C6, seconds after onset


def released_deficit(trace):
    """The 2026-08-26 configuration: released binary forms, default desired speed."""
    p = PreferenceParams()
    return np.asarray(pragmatic_deficit(cutin_obs(trace, p), p), float)


def main() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.4), sharex="col")
    lines = ["| stimulus | " + " | ".join(f"C{i+1} (+{t:.1f}s)" for i, t in enumerate(TIMEPOINTS))
             + " |", "|---" * 7 + "|"]

    for col, (kind, ttcs) in enumerate([("CutInCar", [2, 3, 4, 5, 6, 7, 8]),
                                        ("CutInTruck", [4, 5, 6, 7, 8])]):
        cmap = plt.get_cmap("viridis")
        for k, ttc in enumerate(ttcs):
            tr = load_cutin_trace(BASE / f"{kind}_{ttc}TTC_vehicle_states.csv",
                                  is_truck="Truck" in kind)
            df = cutin_predictors(tr)
            d_new = df.deficit.to_numpy()
            d_old = released_deficit(tr)
            t_rel = df.t.to_numpy() - df.t.to_numpy()[tr.onset_idx]
            m = (t_rel >= -1.0) & (t_rel <= 2.0)
            color = cmap(k / max(len(ttcs) - 1, 1))
            axes[0][col].plot(t_rel[m], d_old[m], color=color, lw=1.4, label=f"TTC{ttc}")
            axes[1][col].plot(t_rel[m], d_new[m], color=color, lw=1.4, label=f"TTC{ttc}")

            idx = [min(tr.onset_idx + int(tp / tr.dt), len(d_new) - 1) for tp in TIMEPOINTS]
            lines.append(f"| {kind} TTC{ttc} | " + " | ".join(f"{d_new[i]:.0f}" for i in idx) + " |")

        axes[0][col].set_title(f"{kind}: released binary forms, default staging")
        axes[1][col].set_title(f"{kind}: continuous lane entry, clip-staged")
        axes[1][col].set_xlabel("time since lane-change onset [s]")
    for ax in axes.ravel():
        ax.axvline(0.0, color=MUTED, lw=0.7, ls=":")
    axes[0][0].set_ylabel("pragmatic deficit")
    axes[1][0].set_ylabel("pragmatic deficit")
    axes[0][0].legend(fontsize=7.5, ncol=2)
    fig.tight_layout()
    FIGS.mkdir(exist_ok=True)
    out = FIGS / "cutin_field_check.png"
    fig.savefig(out, dpi=150)
    print("wrote", out, "\n")
    print("Deficit (continuous forms) at the fixed-clip truncation points:\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
