"""Shot S1: the particle cloud collapses in one step; the plan takes three more.

    python presentation/talk/make_belief_animation.py

The claim on the slide: detection is not the bottleneck. The 75-particle belief
about the lead vehicle snaps onto the truth in the single 0.2 s step in which the
lead starts braking (t = 0.8 s); the accumulated surprise then needs three more
steps to reach its threshold (re-plan at t = 1.4 s), and the pedal moves at
t = 1.6 s. The 0.8 s between the world changing and the pedal moving is evidence
accumulation, not slow senses.

Source, identical to `make_event_animation.py`: the OSF deposit (osf.io/gs4bu),
rear-end scenario, `Results_rear_end/Exp_7` (10 m/s, 1.0 s initial time gap),
random seed 0. Nothing here is sketched; every number on every frame is read from
the deposited arrays.

Arrays used, and their axis order as found in the pickle (NOT as the deposit
README describes them; see docs/method_review.md and notes/05_validation.md 4b for
the policy-array erratum, and the belief-column note below):

    d["eta"]         (32 seeds, 60 steps, 14)   true state
    d["b"]           (32 seeds, 60 steps, 75 particles, 14)   belief particles
    d["w"]           (32 seeds, 60 steps, 75 particles)       particle weights
    d["v_init"]      (32 seeds, 60 steps, 8)    pragmatic-value components of the
                                                incumbent plan
    d["a_cont"]      (30 horizon, 60 steps, 32 seeds, 2)      executed plan
    d["a_cont_init"] (30 horizon, 60 steps, 32 seeds, 2)      reference plan

Two facts established by inspecting the arrays here, both of which shape the
figure and are stated on the slide:

1.  The belief particle columns are the true-state columns shifted by two:
    `b[..., j]` equals the truth in `eta[..., j - 2]` for j = 2 ... 13, with
    `b[..., 0] == 1` and `b[..., 1] == 0` constant throughout the deposit. So
    the lead's longitudinal position is `b[..., 7]`, its speed `b[..., 11]` and
    its acceleration `b[..., 12]`, against `eta[..., 5]`, `eta[..., 9]` and
    `eta[..., 10]`. (`docs/method_review.md` uses the same `b[..., 12]` for the
    believed lead acceleration, which is the one cross-check available.)

2.  `w` is exactly uniform, 1/75, at every step of every seed of this run: the
    deposit stores the belief *after* resampling, so the weights carry no
    information. Marker area is still computed as `w * 75` — the formula the
    shot list asks for — which therefore degenerates to a constant, and the
    frame says so rather than implying a weighting that is not there.

The belief panel plots believed lead *speed* against believed lead
*acceleration*, not against believed gap as the shot list's first draft asked.
Reason, from the data: the gap is effectively observed, so the particles' spread
in gap is 1.2 mm (sd) before braking and 0.5 mm after — a scatter against gap is
a vertical line at any honest scale and shows no collapse. All of the belief
uncertainty lives in the lead's motion: sd 0.475 m/s in speed and 0.068 m/s^2 in
acceleration at t = 0.6 s, collapsing to 0.001 m/s and 0.0004 m/s^2 at t = 0.8 s.
The believed gap is still shown, as a number with its spread, in the panel.

Outputs, into presentation/talk/figures/:
    belief_anim.gif     the animation for the slide
    belief_static.png   the final frame as a static PNG fallback
"""

from __future__ import annotations

import pickle
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image, ImageSequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIGS = HERE / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

PKL = (REPO / "external" / "gs4bu-osfstorage-archive" / "Results_rear_end"
       / "Results_rear_end" / "Exp_7" / "Exp_7.pkl")

SEED = 0
DT = 0.2
LAMBDA = 10.0 ** -5.95        # EA_fac in Setups_rear_end.xlsx row 7
THRESHOLD = 1.0
CAR_LEN = 4.2                 # lf + lr
CAR_WID = 1.72                # d
LANE_W = 3.65

# Belief-column offset established in the docstring: b[..., j] <-> eta[..., j-2]
B_X_EGO, B_X_TAR, B_V_TAR, B_A_TAR = 2, 7, 11, 12
E_X_EGO, E_V_EGO, E_X_TAR, E_V_TAR, E_A_TAR = 0, 4, 5, 9, 10

INK = "#222222"
PURPLE = "#472CBE"
BLUE = "#36B7F6"
TEAL = "#1B8F7A"
PINK = "#C95B9B"
GREY = "#6B7280"
BEIGE = "#F0EDE6"
ROAD = "#E8E6E0"

N_STEPS = 20                  # 4.0 s: the ego is stopped by t = 3.4 s
FPS = 4                       # base rate; one frame per simulated 0.2 s step

# Pillow drops a GIF frame that is byte-identical to its predecessor, so a hold
# cannot be made by repeating frames. Holds are set as per-frame durations
# instead (ms), keyed by step index: the two steps the talk stops on, and the
# one-second hold on the final frame that the shot list's conventions ask for.
BASE_MS = 1000 // FPS
HOLD_MS = {4: 1000,           # t = 0.8 s, the step the cloud collapses
           7: 1000,           # t = 1.4 s, the re-plan
           N_STEPS - 1: 1500}  # the final frame

SRC = ("source: OSF deposit gs4bu, Results_rear_end/Exp_7 (10 m/s, 1.0 s initial time "
       "gap), seed 0  |  particles b[seed, t, :, {7, 11, 12}], weights w[seed, t, :], "
       "truth eta[seed, t, {0, 4, 5, 9, 10}]  |  accumulator from v_init, "
       "lambda = 10^-5.95, threshold 1")

CAP_WRAP = 134                # characters per caption line at 13.5 pt
SRC_WRAP = 205                # characters per source line at 9.6 pt


def load_event():
    """Read the one event, and the belief cloud, straight out of the deposit."""
    with open(PKL, "rb") as fh:
        d = pickle.load(fh)

    eta = d["eta"][SEED].astype(float)                  # (T, 14) true state
    b = d["b"][SEED].astype(float)                      # (T, 75, 14) particles
    w = d["w"][SEED].astype(float)                      # (T, 75) weights
    a_exec = d["a_cont"][0, :, SEED, 0].astype(float)   # executed long. accel
    v_init = d["v_init"][SEED].astype(float)            # incumbent-plan value
    replan = (np.abs(d["a_cont"] - d["a_cont_init"]) > 1e-5).any(axis=(0, 3)).T[SEED]

    # eps_t of Eq. 13: the negative sum of the first seven pragmatic components,
    # each normalized so that its maximum is zero (docs/method_review.md 4.2).
    eps = -v_init[:, :7].sum(axis=1)

    acc, evidence = 0.0, []
    for t in range(len(eps)):
        acc += LAMBDA * eps[t]
        evidence.append(acc)
        if acc >= THRESHOLD:
            acc = 0.0
    evidence = np.array(evidence)

    # Believed quantities, per particle, per step.
    p_v_tar = b[:, :, B_V_TAR]                                    # (T, 75)
    p_a_tar = b[:, :, B_A_TAR]                                    # (T, 75)
    p_gap = b[:, :, B_X_TAR] - b[:, :, B_X_EGO] - CAR_LEN         # (T, 75)

    def wmean(x):
        return (x * w).sum(axis=1)

    def wsd(x):
        m = wmean(x)[:, None]
        return np.sqrt((w * (x - m) ** 2).sum(axis=1))

    t = np.arange(len(eps)) * DT
    s = slice(0, N_STEPS)
    return {
        "t": t[s],
        "x_ego": eta[s, E_X_EGO],
        "v_ego": eta[s, E_V_EGO],
        "x_tar": eta[s, E_X_TAR],
        "v_tar": eta[s, E_V_TAR],
        "a_tar": eta[s, E_A_TAR],
        "gap": eta[s, E_X_TAR] - eta[s, E_X_EGO] - CAR_LEN,
        "a_exec": a_exec[s],
        "E": evidence[s],
        "replan": replan[s],
        "w": w[s],
        "p_v_tar": p_v_tar[s],
        "p_a_tar": p_a_tar[s],
        "p_gap": p_gap[s],
        "sd_v": wsd(p_v_tar)[s],
        "sd_a": wsd(p_a_tar)[s],
        "sd_gap": wsd(p_gap)[s],
        "m_gap": wmean(p_gap)[s],
        "n_particles": b.shape[1],
    }


def phase_text(ev, k):
    """Caption for the beige box. Every number is read from `ev`."""
    t = ev["t"][k]
    if t < 0.8:
        return ("Steady following - nothing to see, so nothing is pinned down",
                "10 m/s, {:.2f} m gap. The {:d} particles disagree about the lead's "
                "speed by {:.2f} m/s (sd) and about its deceleration by {:.2f} m/s². "
                "They agree about the gap to within {:.0f} mm: the gap is observed, "
                "the lead's intent is not.".format(
                    ev["gap"][k], ev["n_particles"], ev["sd_v"][k], ev["sd_a"][k],
                    1000 * ev["sd_gap"][k]))
    if t < 1.4:
        return ("The lead brakes - the cloud collapses in one 0.2 s step",
                "The spread in the believed lead speed went {:.3f} -> {:.3f} m/s in "
                "one step, and every particle now sits on the true {:.1f} m/s². The "
                "model knows; its plan has not changed. The accumulator is at "
                "{:.2f} of 1.".format(
                    ev["sd_v"][3], ev["sd_v"][4], ev["a_tar"][4], ev["E"][k]))
    if t < 1.6:
        return ("Evidence full - one re-plan, three steps after the cloud moved",
                "The accumulator reaches {:.2f} ≥ 1 and the planner runs once, "
                "picking braking. This is 0.6 s after the belief was already "
                "correct.".format(ev["E"][k]))
    if ev["v_ego"][k] > 0.05:
        return ("Pedal at 1.6 s, {:.1f} m/s²".format(ev["a_exec"][8]),
                "Perception cost one 0.2 s step. The remaining 0.6 s was the "
                "accumulator filling, and 0.2 s more was the plan reaching the "
                "pedal. Detection is not the bottleneck.")
    return ("Stopped {:.2f} m behind".format(ev["gap"][k]),
            "One mechanism, one scalar: the belief was right from t = 0.8 s and "
            "the response came at t = 1.6 s. The 0.8 s in between is the cost of "
            "concluding that the plan had failed.")


def draw_car(ax, x, y, color, edge, label=None, brake=False):
    """Draw one vehicle; return every artist so the frame can be torn down."""
    made = []
    body = Rectangle((x - CAR_LEN / 2, y - CAR_WID / 2), CAR_LEN, CAR_WID,
                     facecolor=color, edgecolor=edge, linewidth=1.8, zorder=4)
    ax.add_patch(body)
    made.append(body)
    if brake:
        lamp = Rectangle((x - CAR_LEN / 2 - 0.30, y - CAR_WID / 2), 0.30,
                         CAR_WID, facecolor="#E03131", edgecolor="none", zorder=5)
        ax.add_patch(lamp)
        made.append(lamp)
    if label:
        made.append(ax.text(x, y + CAR_WID / 2 + 0.35, label, ha="center",
                            va="bottom", fontsize=13.5, color=edge,
                            fontweight="bold", zorder=6))
    return made


def build_axes(ev):
    fig = plt.figure(figsize=(13.4, 7.6), dpi=110)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 2, height_ratios=[0.95, 1.50],
                          left=0.098, right=0.980, top=0.885, bottom=0.255,
                          hspace=0.58, wspace=0.20)

    ax_head = fig.add_axes([0.048, 0.900, 0.940, 0.085])
    ax_head.axis("off")

    # --- (1) the road, as in make_event_animation.py ----------------------
    ax_road = fig.add_subplot(gs[0, :])
    ax_road.set_xlim(-3, 36)
    ax_road.set_ylim(-4.6, 2.8)
    ax_road.set_yticks([])
    ax_road.set_xlabel("distance along the road [m]", fontsize=13.5)
    ax_road.tick_params(labelsize=12.5)
    ax_road.add_patch(Rectangle((-3, -LANE_W / 2), 43, LANE_W, facecolor=ROAD,
                                edgecolor="none", zorder=0))
    ax_road.axhline(LANE_W / 2, color="#B9B5AC", lw=2, zorder=1)
    ax_road.axhline(-LANE_W / 2, color="#B9B5AC", lw=2, zorder=1)
    for spine in ("top", "right", "left"):
        ax_road.spines[spine].set_visible(False)

    # --- (2) the belief cloud --------------------------------------------
    ax_bel = fig.add_subplot(gs[1, 0])
    ax_bel.set_xlim(-1.2, 11.9)
    # The band below -7 is empty by construction (the lead never exceeds
    # -6 m/s^2 in this run); it is reserved for the read-out box, which would
    # otherwise sit on top of the cloud once the lead has slowed.
    ax_bel.set_ylim(-8.8, 1.6)
    ax_bel.set_yticks([-6, -4, -2, 0])
    ax_bel.set_xlabel("believed lead speed [m/s]", fontsize=13.5)
    ax_bel.set_ylabel("believed lead accel. [m/s$^2$]", fontsize=13.5)
    ax_bel.tick_params(labelsize=12.5)
    ax_bel.grid(alpha=0.25)
    ax_bel.axhline(0.0, color=GREY, lw=1.0, ls="-", alpha=0.6)
    for spine in ("top", "right"):
        ax_bel.spines[spine].set_visible(False)
    ax_bel.set_title("{:d} belief particles".format(ev["n_particles"]),
                     fontsize=14.5, color=PURPLE, fontweight="bold", pad=8)

    # --- (3) the accumulator, as in make_event_animation.py ---------------
    ax_acc = fig.add_subplot(gs[1, 1])
    ax_acc.set_xlim(0, ev["t"][-1])
    ax_acc.set_ylim(0, 1.42)
    ax_acc.set_xlabel("time [s]", fontsize=13.5)
    ax_acc.set_ylabel("accumulated surprise", fontsize=13.5)
    ax_acc.tick_params(labelsize=12.5)
    ax_acc.grid(alpha=0.25)
    ax_acc.axhline(THRESHOLD, color=PINK, lw=2.2, ls="--")
    ax_acc.text(ev["t"][-1], 1.05, "re-plan threshold", color=PINK, fontsize=13,
                fontweight="bold", ha="right")
    for spine in ("top", "right"):
        ax_acc.spines[spine].set_visible(False)
    ax_acc.set_title("evidence that the plan has failed", fontsize=14.5,
                     color=BLUE, fontweight="bold", pad=8)

    # --- the beige caption box -------------------------------------------
    ax_cap = fig.add_axes([0.018, 0.012, 0.964, 0.212])
    ax_cap.axis("off")
    ax_cap.add_patch(FancyBboxPatch(
        (0.004, 0.05), 0.992, 0.90, boxstyle="round,pad=0.010,rounding_size=0.02",
        transform=ax_cap.transAxes, facecolor=BEIGE, edgecolor="#D8D3C7",
        linewidth=1.2, zorder=0, clip_on=False))
    ax_cap.text(0.016, 0.09, textwrap.fill(SRC, SRC_WRAP),
                transform=ax_cap.transAxes, ha="left", va="bottom",
                fontsize=9.6, color=GREY, zorder=3, linespacing=1.4)

    return fig, ax_head, ax_road, ax_bel, ax_acc, ax_cap


def render(ev, ax_head, ax_road, ax_bel, ax_acc, ax_cap, k):
    for ax in (ax_head, ax_road, ax_bel, ax_acc, ax_cap):
        for artist in list(getattr(ax, "_dyn", [])):
            artist.remove()
        ax._dyn = []

    title, sub = phase_text(ev, k)

    # --- headline ---------------------------------------------------------
    ax_head._dyn.append(ax_head.text(
        0.0, 0.5, "t = {:.1f} s   —   {}".format(ev["t"][k], title),
        transform=ax_head.transAxes, ha="left", va="center", fontsize=19,
        fontweight="bold", color=PURPLE))

    # --- the caption in the beige box ------------------------------------
    ax_cap._dyn.append(ax_cap.text(
        0.016, 0.90, textwrap.fill(sub, CAP_WRAP), transform=ax_cap.transAxes,
        ha="left", va="top", fontsize=13.5, color=INK, zorder=3,
        linespacing=1.45))

    # --- (1) the road -----------------------------------------------------
    xe, xt = ev["x_ego"][k], ev["x_tar"][k]
    ax_road._dyn.extend(draw_car(ax_road, xt, 0, "#FFFFFF", INK, "lead vehicle",
                                 brake=ev["a_tar"][k] < -0.1))
    ax_road._dyn.extend(draw_car(ax_road, xe, 0, "#DCD6F7", PURPLE,
                                 "the driver model",
                                 brake=(ev["a_exec"][k] < -1.0
                                        and ev["v_ego"][k] > 0.1)))
    ax_road._dyn.append(ax_road.annotate(
        "", xy=(xe + CAR_LEN / 2, -2.6), xytext=(xt - CAR_LEN / 2, -2.6),
        arrowprops=dict(arrowstyle="<|-|>", color=TEAL, lw=2.6,
                        mutation_scale=20)))
    gap = ev["gap"][k]
    gap_label = ("gap {:.2f} m   ({:.2f} s headway)".format(
        gap, gap / ev["v_ego"][k]) if ev["v_ego"][k] > 0.2
        else "gap {:.2f} m".format(gap))
    ax_road._dyn.append(ax_road.text(
        (xe + xt) / 2, -3.7, gap_label, ha="center", va="center", fontsize=13.5,
        color=TEAL, fontweight="bold"))

    # --- (2) the belief cloud --------------------------------------------
    pv, pa, wk = ev["p_v_tar"][k], ev["p_a_tar"][k], ev["w"][k]
    # Marker area from the weights, as the shot list asks. The deposit's weights
    # are exactly uniform (post-resampling), so this is constant; the note below
    # the panel says so rather than implying a weighting that is not there.
    sizes = 46.0 * wk * ev["n_particles"]
    ax_bel._dyn.append(ax_bel.scatter(pv, pa, s=sizes, facecolor=PURPLE,
                                      edgecolor="none", alpha=0.55, zorder=3))
    # the particles' full extent, so the collapse is visible at this scale
    lo_v, hi_v = pv.min(), pv.max()
    lo_a, hi_a = pa.min(), pa.max()
    ax_bel._dyn.append(ax_bel.add_patch(Rectangle(
        (lo_v, lo_a), max(hi_v - lo_v, 0.02), max(hi_a - lo_a, 0.02),
        facecolor="none", edgecolor=PURPLE, lw=1.6, ls="--", alpha=0.8,
        zorder=2)))
    ax_bel._dyn.append(ax_bel.scatter([ev["v_tar"][k]], [ev["a_tar"][k]],
                                      s=340, facecolor="none", edgecolor=PINK,
                                      linewidth=3.0, zorder=5))
    ax_bel._dyn.append(ax_bel.text(
        ev["v_tar"][k] + 0.35, ev["a_tar"][k] + 0.55, "true state", color=PINK,
        fontsize=13, fontweight="bold", ha="left", va="bottom", zorder=6))
    ax_bel._dyn.append(ax_bel.text(
        0.5, 0.02,
        "spread (sd):  speed {:.3f} m/s    accel {:.3f} m/s$^2$\n"
        "believed gap {:.2f} m  (sd {:.0f} mm)   —   all {:d} weights = 1/{:d}"
        .format(ev["sd_v"][k], ev["sd_a"][k], ev["m_gap"][k],
                1000 * ev["sd_gap"][k], ev["n_particles"], ev["n_particles"]),
        transform=ax_bel.transAxes, ha="center", va="bottom", fontsize=11.5,
        color=INK, zorder=6,
        bbox=dict(boxstyle="round,pad=0.34", facecolor="white",
                  edgecolor="#DDDDDD", alpha=0.92)))

    # --- (3) the accumulator ---------------------------------------------
    sl = slice(0, k + 1)
    ax_acc._dyn.append(ax_acc.bar(ev["t"][sl], ev["E"][sl], width=DT * 0.85,
                                  color=BLUE, edgecolor="none"))
    if ev["t"][k] >= 0.8:
        ax_acc._dyn.append(ax_acc.axvline(0.8, color=GREY, lw=1.8, ls=":"))
        ax_acc._dyn.append(ax_acc.text(0.72, 0.86, "belief\ncollapses", color=GREY,
                                       fontsize=12, ha="right", va="top",
                                       fontweight="bold"))
    if ev["t"][k] >= 1.4:
        ax_acc._dyn.append(ax_acc.axvline(1.4, color=PINK, lw=2.2))
        ax_acc._dyn.append(ax_acc.text(1.52, 1.20, "re-plan", color=PINK,
                                       fontsize=13, fontweight="bold"))
    if ev["t"][k] >= 1.6:
        ax_acc._dyn.append(ax_acc.axvline(1.6, color=PURPLE, lw=2.2, ls=":"))
        ax_acc._dyn.append(ax_acc.text(1.72, 0.62, "brake", color=PURPLE,
                                       fontsize=13, fontweight="bold"))
    ax_acc._dyn.append(ax_acc.axvline(ev["t"][k], color=INK, lw=1.2, alpha=0.45))


def main() -> None:
    ev = load_event()

    # The array facts the docstring asserts, re-checked on every run.
    assert ev["w"].shape[1] == 75, "expected 75 particles"
    assert np.allclose(ev["w"], 1.0 / 75.0), "deposit weights are no longer uniform"

    fig, ax_head, ax_road, ax_bel, ax_acc, ax_cap = build_axes(ev)
    for ax in (ax_head, ax_road, ax_bel, ax_acc, ax_cap):
        ax._dyn = []

    order = list(range(N_STEPS))

    def frame(i):
        render(ev, ax_head, ax_road, ax_bel, ax_acc, ax_cap, order[i])
        return []

    anim = FuncAnimation(fig, frame, frames=len(order), interval=BASE_MS,
                         blit=False)
    out_gif = FIGS / "belief_anim.gif"
    anim.save(str(out_gif), writer=PillowWriter(fps=FPS))

    # Re-save with the per-frame holds (PillowWriter can only set one duration).
    durations = [HOLD_MS.get(k, BASE_MS) for k in order]
    with Image.open(out_gif) as gif:
        frames = [f.convert("RGB") for f in ImageSequence.Iterator(gif)]
    assert len(frames) == len(order), (
        "GIF has {} frames, expected {}".format(len(frames), len(order)))
    frames[0].save(out_gif, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=False)
    print("wrote", out_gif, "({:d} frames, {:.1f} s per loop)".format(
        len(frames), sum(durations) / 1000.0))

    render(ev, ax_head, ax_road, ax_bel, ax_acc, ax_cap, N_STEPS - 1)
    fig.savefig(FIGS / "belief_static.png", dpi=170, facecolor="white")
    print("wrote", FIGS / "belief_static.png")

    k_pre, k_col, k_rep = 3, 4, 7
    print("checks, all from the deposit:")
    print("  lead brake onset      t = {:.1f} s  (a_tar {:.1f} m/s2)".format(
        ev["t"][int(np.argmax(ev["a_tar"] < -0.1))],
        ev["a_tar"][int(np.argmax(ev["a_tar"] < -0.1))]))
    print("  belief sd(v_lead)     {:.4f} m/s at t = {:.1f} s  ->  {:.4f} m/s "
          "at t = {:.1f} s".format(ev["sd_v"][k_pre], ev["t"][k_pre],
                                   ev["sd_v"][k_col], ev["t"][k_col]))
    print("  belief sd(a_lead)     {:.4f} -> {:.4f} m/s2".format(
        ev["sd_a"][k_pre], ev["sd_a"][k_col]))
    print("  belief sd(gap)        {:.4f} m at t = {:.1f} s (gap is observed)"
          .format(ev["sd_gap"][k_pre], ev["t"][k_pre]))
    print("  re-plan               t = {:.1f} s  (E = {:.2f})".format(
        ev["t"][int(np.argmax(ev["replan"]))], ev["E"][k_rep]))
    print("  first pedal <= -1     t = {:.1f} s  ({:.2f} m/s2)".format(
        ev["t"][int(np.argmax(ev["a_exec"] <= -1.0))],
        ev["a_exec"][int(np.argmax(ev["a_exec"] <= -1.0))]))
    print("  final gap             {:.2f} m".format(ev["gap"][-1]))


if __name__ == "__main__":
    main()
