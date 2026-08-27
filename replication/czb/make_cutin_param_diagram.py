"""Diagram of the cut-in geometry and the continuous lane-entry quantities.

Produces docs/czb_figures/cutin_parameters.png for the parameter-reference section of
docs/lane_entry_note.md: a top-down view of the geometry with every symbol placed on it,
and the resulting weight and severity curves along a real stimulus clip.

    python replication/czb/make_cutin_param_diagram.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrow, Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from comfortzone.cutin import load_cutin_trace, cutin_predictors  # noqa: E402

BLUE, ORANGE, GREEN, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
plt.rcParams.update({
    "font.size": 9.0, "axes.edgecolor": MUTED, "figure.facecolor": "white",
    "legend.frameon": False,
})


def draw_geometry(ax):
    lane_w, y_ego_lane, y_adj_lane = 3.5, 0.0, 3.5
    ego = dict(x=2.0, y=y_ego_lane, L=4.2, W=1.72)
    tar = dict(x=24.0, y=2.3, L=5.0, W=1.8)          # mid lane change

    for y in (-lane_w / 2, lane_w / 2, 3 * lane_w / 2):
        ax.axhline(y, color=MUTED, lw=1.0 if abs(y) != lane_w / 2 else 1.4,
                   ls="-" if abs(y) != lane_w / 2 else (0, (6, 4)))
    ax.text(38.5, y_ego_lane, "ego lane", va="center", ha="right", color=MUTED, fontsize=8)
    ax.text(38.5, y_adj_lane, "adjacent lane", va="center", ha="right", color=MUTED, fontsize=8)

    for v, col, name in ((ego, BLUE, "ego"), (tar, ORANGE, "target")):
        ax.add_patch(Rectangle((v["x"] - v["L"] / 2, v["y"] - v["W"] / 2), v["L"], v["W"],
                               fc=col, ec="none", alpha=0.75))
        ax.text(v["x"], v["y"], name, ha="center", va="center", color="white", fontsize=8)

    # speeds
    ax.add_patch(FancyArrow(ego["x"] + ego["L"] / 2 + .5, ego["y"], 4.5, 0, width=.06,
                            head_width=.5, color=BLUE))
    ax.text(ego["x"] + ego["L"] / 2 + 2.6, ego["y"] + .7, "$v_{ego}$", color=BLUE)
    ax.add_patch(FancyArrow(tar["x"] + tar["L"] / 2 + .5, tar["y"], 3.0, 0, width=.06,
                            head_width=.5, color=ORANGE))
    ax.text(tar["x"] + tar["L"] / 2 + 2.0, tar["y"] + .7, "$v_{tar}$", color=ORANGE)
    ax.add_patch(FancyArrow(tar["x"] - tar["L"] / 2 - 1.0, tar["y"] + .8, 0, -1.6,
                            width=.05, head_width=.45, color=GREEN))
    ax.text(tar["x"] - tar["L"] / 2 - 2.3, tar["y"] - .2,
            r"$v_y = \dot{\Delta y}$", color=GREEN, ha="right")

    # dy
    ax.annotate("", xy=(tar["x"] + tar["L"] / 2 + 6.5, tar["y"]),
                xytext=(tar["x"] + tar["L"] / 2 + 6.5, ego["y"]),
                arrowprops=dict(arrowstyle="<->", color=MUTED))
    ax.text(tar["x"] + tar["L"] / 2 + 7.0, (tar["y"] + ego["y"]) / 2,
            r"$\Delta y$", va="center")

    # overlap-onset band s
    s = 1.15 * 0.5 * (ego["W"] + tar["W"])
    ax.axhspan(-s, s, color=BLUE, alpha=0.06)
    for yy in (-s, s):
        ax.axhline(yy, color=BLUE, lw=0.8, ls=(0, (2, 3)), alpha=0.7)
    ax.annotate("", xy=(11.5, s), xytext=(11.5, 0),
                arrowprops=dict(arrowstyle="<->", color=BLUE, alpha=.8))
    ax.text(1.0, s + 0.45, r"$s = 1.15\,(w_e{+}w_o)/2$  (overlap begins at $|\Delta y|=s$)",
            color=BLUE, fontsize=8, va="bottom")

    # longitudinal gap
    gx0, gx1 = ego["x"] + ego["L"] / 2, tar["x"] - tar["L"] / 2
    ax.annotate("", xy=(gx1, -2.6), xytext=(gx0, -2.6),
                arrowprops=dict(arrowstyle="<->", color=MUTED))
    ax.text((gx0 + gx1) / 2, -3.4,
            r"gap $\rightarrow \tau_{lon} = \mathrm{gap}/(v_{ego}-v_{tar})$",
            ha="center", fontsize=8.5)

    ax.text(1.0, 8.6,
            r"$\tau_{lat} = (|\Delta y| - s)\,/\,\max(v_y\ \mathrm{toward\ lane},\,0)$"
            "        predicted offset at closure:  "
            r"$|\Delta y|_{pred} = \max(|\Delta y| - v_y\,\tau_{lon},\ 0)$",
            fontsize=8.5)
    ax.text(1.0, 7.3,
            r"$P_{lane} = \mathrm{clip}\!\left((s - |\Delta y|_{pred})\,/\,"
            r"(1.15\,\min(w_e,w_o)),\ 0,\ 1\right)$"
            r"        $\Delta v_{resid} = \sqrt{\max(0,\ v_{react}^2 - 2\,a_{max}\,d_{avail})}$",
            fontsize=8.5)

    ax.set_xlim(0, 39); ax.set_ylim(-4.2, 9.4)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Cut-in geometry and the lane-entry quantities (top view; not to scale)")


def draw_curves(ax):
    base = REPO / ("external/01_studies/01_Studies/01_Sequence_Random_ButtonPress/"
                   "Kinematics/Button_Press_Study")
    tr = load_cutin_trace(base / "CutInCar_6TTC_vehicle_states.csv")
    df = cutin_predictors(tr)
    t = df.t.to_numpy() - df.t.to_numpy()[tr.onset_idx]
    m = (t >= -1.0) & (t <= 2.0)
    ax.plot(t[m], df.p_lane.to_numpy()[m], color=BLUE, lw=1.6, label=r"$P_{lane}$ (0–1)")
    ax.plot(t[m], df.dv_resid.to_numpy()[m] / df.dv_resid.max(), color=ORANGE, lw=1.6,
            label=r"$\Delta v_{resid}$ (scaled)")
    ax.plot(t[m], df.deficit.to_numpy()[m] / df.deficit.to_numpy()[m].max(), color=GREEN,
            lw=1.6, label="deficit (scaled)")
    ax.axvline(0, color=MUTED, lw=0.8, ls=":")
    ax.text(0.03, 0.95, "lane-change onset", transform=ax.get_xaxis_transform(),
            fontsize=8, color=MUTED)
    ax.set_xlabel("time since lane-change onset [s]")
    ax.set_ylabel("normalized value")
    ax.grid(color="#e4e4e0", lw=0.6)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="center right", fontsize=8.5)
    ax.set_title("The same quantities along the TTC6 stimulus clip")


def main() -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.0, 7.6),
                                   gridspec_kw={"height_ratios": [1.15, 1.0]})
    draw_geometry(ax1)
    draw_curves(ax2)
    fig.tight_layout()
    out = REPO / "docs" / "czb_figures" / "cutin_parameters.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=150)
    print("wrote", out)


if __name__ == "__main__":
    main()
