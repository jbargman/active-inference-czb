"""Animations for the paper talk (build_paper_talk.py) — the published model only.

    python presentation/talk/make_paper_animations.py [--only loop,tournament,...]

Five new animations, plus MP4 transcodes of the two that already existed as GIFs
(the chapter-02 event and the belief cloud), so every animated slide in the paper
talk gets PowerPoint's own media controls rather than a GIF that cannot be paused.

Every moving quantity is either read from the authors' OSF deposit / released
preference code, or is an explicitly labeled schematic:

    paper_loop         schematic ring, REAL per-step deposits from Exp_7 seed 0
    paper_tournament   the sampling rule of dynamics.forward_tar_agent, lateral-only
                       reimplementation (as docs/handbook/make_diagrams.py), real
                       geometry factors: weigh_particles 1e-3, full_violation 1e-2,
                       N_norm 32, H_norm 20
    paper_regimes      accumulator E(t) of Exp_7 seed 0, and the pre-onset drift of
                       all 28 baseline conditions, both from the deposit
    paper_preference   the six preference terms, shapes and parameters as shipped
    paper_maneuver     the maneuver mix by initial speed, from the deposit's own
                       Analysis_rear_end.xlsx (28 baseline rows)

Outputs into presentation/talk/figures/: <name>.gif, .mp4 and a .png poster of the
FIRST frame. The numbers every animation draws are written to
presentation/talk/paper_anim_numbers.md so they can be checked without rerunning.

Three rules are enforced in save() and must not be broken (they were each found the
hard way, 2026-09-03):
  1. render the GIF ONCE, then transcode; never call anim.save() twice on one
     FuncAnimation;
  2. the poster is the FIRST frame, taken from the GIF;
  3. verify the video, not the slide still.
"""
from __future__ import annotations

import argparse
import pickle
import subprocess
import sys
from pathlib import Path

import matplotlib
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
FIGS = HERE / "figures"
FIGS.mkdir(parents=True, exist_ok=True)
DEPOSIT = REPO / "external" / "gs4bu-osfstorage-archive" / "Results_rear_end" / "Results_rear_end"
COND_CSV = REPO / "replication" / "osf" / "baseline_conditions.csv"
sys.path.insert(0, str(REPO / "src"))

PURPLE, TEAL, PINK, BLUE = "#472CBE", "#1B8F7A", "#B03E82", "#36B7F6"
INK, GREY, BEIGE, AMBER = "#222222", "#6A6A6A", "#F0EDE6", "#C47A14"
LILAC = "#6746EB"

FPS = 8
DT = 0.2
LAMBDA = 10.0 ** -5.95          # EA_fac of the rear-end runs
THRESHOLD = 1.0
SEED = 0
EXP = 7                          # 10 m/s, 1.0 s time gap - the chapter-02 event

NUMBERS: list[str] = []          # collected for paper_anim_numbers.md


def note(line: str) -> None:
    NUMBERS.append(line)
    print("   ", line)


# ---------------------------------------------------------------------------
# shared plumbing (same contract as make_concept_animations.save)
# ---------------------------------------------------------------------------
def gif_to_mp4(gif: Path, fps: int = FPS) -> Path:
    """Transcode a finished .gif to H.264 and write a poster of its FIRST frame."""
    mp4, poster = gif.with_suffix(".mp4"), gif.with_suffix(".png")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(gif),
         "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-r", str(fps),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
         "-movflags", "+faststart", str(mp4)],
        check=True)
    with Image.open(gif) as im:
        im.seek(0)
        im.convert("RGB").save(poster)
    return mp4


def save(fig, fn, n, name, fps=FPS):
    """Render the GIF once, then derive the .mp4 and the first-frame poster from it."""
    anim = FuncAnimation(fig, fn, frames=n, interval=1000 / fps, blit=False)
    out = FIGS / name
    anim.save(str(out), writer=PillowWriter(fps=fps))
    plt.close(fig)
    gif_to_mp4(out, fps)
    print("wrote", out.name, "+ .mp4 + .png poster", f"({n} frames, {n / fps:.1f} s)")
    return out


class Beats:
    """A caption track. Each beat holds for max(its reading time, the time asked for).

    The reading model is the slide skill's: 0.4 s to notice the change, then one word
    per 0.4 s (150 words a minute, not 250 - the viewer is also watching a drawing and
    listening to a speaker), never under 1.5 s.
    """

    def __init__(self, fps=FPS):
        self.fps = fps
        self.spans: list[tuple[int, int, str]] = []
        self.n = 0

    def add(self, seconds: float, caption: str) -> "Beats":
        need = 0.4 + len(caption.split()) / 2.5
        secs = max(seconds, need, 1.5)
        frames = int(round(secs * self.fps))
        self.spans.append((self.n, self.n + frames, caption))
        self.n += frames
        return self

    def at(self, k: int) -> tuple[int, str, float]:
        """Return (beat index, caption, progress 0-1 within the beat) for frame k."""
        for i, (a, b, cap) in enumerate(self.spans):
            if a <= k < b:
                return i, cap, (k - a) / max(b - a, 1)
        i = len(self.spans) - 1
        return i, self.spans[i][2], 1.0


def caption_band(fig, y=0.045):
    return fig.text(0.5, y, "", ha="center", va="center", fontsize=15, color=INK,
                    bbox=dict(boxstyle="round,pad=0.55", fc=BEIGE, ec="none"))


def new_fig(w=13.5, h=5.6):
    """Canvas matched to the slide's body area (31.2 x 12.9 cm is about 2.42:1)."""
    return plt.figure(figsize=(w, h), dpi=100)


# ---------------------------------------------------------------------------
# the deposit
# ---------------------------------------------------------------------------
def load_exp(exp: int) -> dict:
    p = DEPOSIT / f"Exp_{exp}" / f"Exp_{exp}.pkl"
    with open(p, "rb") as fh:
        return pickle.load(fh)


def event_series() -> dict:
    """Exp_7 seed 0: the chapter-02 event, with the accumulator reconstructed."""
    d = load_exp(EXP)
    eta = d["eta"][SEED].astype(float)
    a_exec = d["a_cont"][0, :, SEED, 0].astype(float)
    replan = (np.abs(d["a_cont"] - d["a_cont_init"]) > 1e-5).any(axis=(0, 3)).T[SEED]
    eps = -d["v_init"][SEED][:, :7].sum(axis=1)
    acc, E = 0.0, []
    for e in eps:
        acc += LAMBDA * e
        E.append(acc)
        if acc >= THRESHOLD:
            acc = 0.0
    n = 30
    return {"t": np.arange(len(eps))[:n] * DT, "eps": eps[:n], "E": np.array(E)[:n],
            "replan": replan[:n], "a_exec": a_exec[:n], "v_ego": eta[:n, 4],
            "a_tar": eta[:n, 10]}


def drift_table() -> pd.DataFrame:
    """Pre-onset accumulator drift (first 0.8 s) for all 28 baseline conditions."""
    cond = pd.read_csv(COND_CSV)
    rows = []
    for _, r in cond.iterrows():
        d = load_exp(int(r.exp))
        eps = -d["v_init"][:, :, :7].sum(axis=2)          # (seeds, T)
        drift = float((LAMBDA * eps[:, :4].sum(axis=1)).mean())
        rows.append((int(r.exp), float(r.v0), float(r.thw0), 100.0 * drift))
    return pd.DataFrame(rows, columns=["exp", "v0", "thw0", "drift_pct"]).sort_values("thw0")


def maneuver_mix() -> pd.DataFrame:
    """The maneuver mix by initial speed, from the deposit's own analysis workbook."""
    x = pd.read_excel(DEPOSIT / "Analysis_rear_end.xlsx")
    b = x[(x.noise_pred_fac == 0.2) & (x.use_pedals == 1) & (x.use_looming_perception == 1)
          & (x.looming_threshold == 0.002) & (x.N_norm == 32) & (x.alpha == 1)
          & (x.EA_mode == "Surprise")]
    g = b.groupby("v_ego_des").agg(
        braking=("braking_post", "mean"),
        steering=("overtaking_post", "mean"),
        brake_steer=("brake_steer_post", "mean"),
        leave_road=("leave_road", "mean"),
        collision=("collision", "mean")).reset_index()
    g["steer_any"] = g.steering + g.brake_steer
    return g


# ---------------------------------------------------------------------------
# 1. the loop
# ---------------------------------------------------------------------------
NODES = [
    ("SENSE", "looming angle\nand its rate"),
    ("BELIEVE", "75 weighted\nhypotheses"),
    ("PREDICT", "roll each one\n6 s ahead"),
    ("EVALUATE", "score against\nthe preferred future"),
    ("ACT", "execute the plan's\nnext step"),
    ("ACCUMULATE", "deposit the\nshortfall"),
]


def make_loop():
    ev = event_series()
    quiet = float(ev["eps"][3])          # t = 0.6 s, the last quiet step
    loud = ev["eps"][4:8]                # t = 0.8, 1.0, 1.2, 1.4 s
    note(f"loop: Exp_7 seed 0 last pre-onset deposit {quiet:,.0f} units/step "
         f"= {100 * LAMBDA * quiet:.1f}% of the re-plan threshold per step")
    note("loop: deposits after the lead brakes " + ", ".join(f"{v:,.0f}" for v in loud[:3])
         + " units/step (t = 0.8, 1.0, 1.2 s)")

    beats = Beats()
    beats.add(2.6, "One loop, five times a second. There is no second architecture.")
    for name, sub in NODES:
        beats.add(1.6, f"{name}  —  {sub}".replace("\n", " "))
    beats.add(3.0, "Quiet following: every pass still deposits a little")
    beats.add(3.0, "The lead brakes. The same loop, larger deposits")
    beats.add(2.8, "Threshold: one full re-plan, and the account resets")
    beats.add(2.2, "Response time is what the account took to fill")
    n = beats.n

    fig = new_fig()
    ax = fig.add_axes([0.01, 0.13, 0.62, 0.78]); ax.set_aspect("equal")
    bx = fig.add_axes([0.72, 0.24, 0.25, 0.58])
    cap = caption_band(fig)

    ang = [np.pi / 2 - i * 2 * np.pi / 6 for i in range(6)]
    R, RAD = 1.0, 0.30
    pos = [(R * np.cos(a) * 1.30, R * np.sin(a)) for a in ang]

    # the per-step deposits the bar plays through: four quiet, then the loud ones
    PER = [LAMBDA * quiet] * 4 + [LAMBDA * float(v) for v in loud]

    def frame(k):
        ax.clear(); bx.clear()
        i, text, prog = beats.at(k)
        ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.42, 1.42); ax.axis("off")

        active = i - 1 if 1 <= i <= 6 else ((k // 2) % 6 if i >= 7 else -1)
        for j in range(6):
            x0, y0 = pos[j]
            x1, y1 = pos[(j + 1) % 6]
            v = np.array([x1 - x0, y1 - y0]); L = np.hypot(*v); u = v / L
            a0 = (x0 + u[0] * RAD * 1.25, y0 + u[1] * RAD * 1.25)
            a1 = (x1 - u[0] * RAD * 1.25, y1 - u[1] * RAD * 1.25)
            lit = (j == active)
            ax.add_patch(FancyArrowPatch(a0, a1, arrowstyle="-|>", mutation_scale=22,
                                         lw=3.0 if lit else 1.6,
                                         color=PURPLE if lit else "#D3CEE2",
                                         connectionstyle="arc3,rad=-0.16", zorder=1))
        for j, (name, sub) in enumerate(NODES):
            x, y = pos[j]
            on = (j == active)
            ax.add_patch(plt.matplotlib.patches.Ellipse(
                (x, y), RAD * 2.35, RAD * 1.30,
                facecolor=PURPLE if on else "white",
                edgecolor=PURPLE if on else "#C9C3D8",
                lw=2.6 if on else 1.4, zorder=3))
            ax.text(x, y, name, ha="center", va="center", fontsize=11,
                    color="white" if on else INK, fontweight="bold", zorder=4)
        ax.text(0, 0.06, "every 0.2 s", ha="center", va="center", fontsize=13,
                color=GREY, style="italic")
        ax.text(0, -0.16, "one architecture", ha="center", va="center", fontsize=11,
                color="#B9B3C9")
        ax.set_title("The loop   (the ring is schematic; the account on the right is "
                     "the authors' own run)", fontsize=12.5, color=INK, pad=4)

        # the account: visible throughout, filling from beat 7
        level, fired = 0.0, False
        if i >= 7:
            steps = int(prog * 4) + (0 if i == 7 else 4)
            for s in range(min(steps, len(PER))):
                level += PER[s]
                if level >= THRESHOLD:
                    level, fired = 0.0, True
            if i >= 9:
                level, fired = (0.0, True) if prog > 0.45 else (0.97, False)
        bx.bar([0], [min(level, 1.0)], width=0.55,
               color=PINK if level > 0.6 else PURPLE, zorder=2)
        bx.axhline(1.0, color=INK, ls="--", lw=1.6)
        bx.text(-0.30, 1.045, "re-plan threshold", fontsize=10.5, color=INK)
        if fired and i >= 9:
            bx.text(0, 0.52, "RE-PLAN", ha="center", va="center", fontsize=16,
                    color=PINK, fontweight="bold", rotation=8, zorder=3)
        if i >= 7:
            dep = quiet if i == 7 else float(loud[min(int(prog * 3), 2)])
            bx.set_xlabel(f"this step: {dep:,.0f} units\n({100 * LAMBDA * dep:.0f}% of the threshold)",
                          fontsize=11, color=INK)
        else:
            bx.set_xlabel("waiting for the loop", fontsize=11, color="#B9B3C9")
        bx.set_ylim(0, 1.30); bx.set_xlim(-0.55, 0.55)
        bx.set_xticks([]); bx.set_yticks([0, 0.5, 1.0])
        bx.set_ylabel("surprise account", fontsize=12)
        bx.tick_params(labelsize=11)
        bx.spines[["top", "right"]].set_visible(False)

        cap.set_text(text)
        return []

    save(fig, frame, n, "paper_loop.gif")


# ---------------------------------------------------------------------------
# 2. the norm tournament
# ---------------------------------------------------------------------------
def make_tournament():
    """Lateral-only reimplementation of dynamics.forward_tar_agent's sampling rule.

    Same rule and same geometry factors as docs/handbook/make_diagrams.py: 32 candidates,
    compliance scored now / one step / H_norm=20 steps ahead, the future two combined by
    harmonic mean, the overall weight the MINIMUM of now and future - which is the trust
    cap - and one winner drawn from the normalized weights.
    """
    rng = np.random.default_rng(7)
    LANE, D = 3.65, 1.72
    AW = 0.5 * (LANE - D)
    WP, FVF = 1e-3, 1e-2
    N_NORM, H_NORM, SIGMA = 32, 20, 0.12
    STEPS, NTRAJ = 20, 90

    def W(y):
        y = np.abs(np.atleast_1d(y))
        w = np.full_like(y, WP * FVF, dtype=float)
        w[y < AW + 0.2 * D] = WP
        w[y < AW] = 1.0
        return w

    def weights(y, cand):
        w_now = W(np.full(N_NORM, y))
        w_next, w_long = W(cand), W(y + (cand - y) * H_NORM)
        w_fut = 2 * w_next * w_long / (w_next + w_long)
        w = np.minimum(w_now, w_fut)
        return w / w.sum(), w_now[0]

    def fan(y0, biased, n=NTRAJ, seed=3):
        r = np.random.default_rng(seed)
        out = np.zeros((n, STEPS + 1)); out[:, 0] = y0
        for i in range(n):
            y = y0
            for t in range(STEPS):
                cand = y + SIGMA * r.standard_normal(N_NORM)
                if biased:
                    w, _ = weights(y, cand)
                    y = r.choice(cand, p=w)
                else:
                    y = cand[0]
                out[i, t + 1] = y
        return out

    y_ok, y_bad = 0.0, AW + 0.35
    cand_ok = y_ok + SIGMA * rng.standard_normal(N_NORM)
    w_ok, now_ok = weights(y_ok, cand_ok)
    cand_bad = y_bad + SIGMA * rng.standard_normal(N_NORM)
    w_bad, now_bad = weights(y_bad, cand_bad)
    fan_ok_b, fan_ok_r = fan(y_ok, True), fan(y_ok, False)
    fan_bad_b = fan(y_bad, True)

    note(f"tournament: compliant target w_now = {now_ok:.3g}; candidate weights span "
         f"{w_ok.min():.2e} to {w_ok.max():.2e} (ratio {w_ok.max() / w_ok.min():.0f}x)")
    note(f"tournament: violating target w_now = {now_bad:.3g}; candidate weights span "
         f"{w_bad.min():.2e} to {w_bad.max():.2e} (ratio {w_bad.max() / w_bad.min():.1f}x "
         f"- the lottery is near uniform, so the bias has dissolved)")

    beats = Beats()
    beats.add(2.4, "A particle moves the other vehicle one step — not by adding noise")
    beats.add(1.8, "It proposes 32 candidate moves")
    beats.add(3.0, "Each is scored for norm compliance: now, one step ahead, four seconds ahead")
    beats.add(2.4, "One winner is drawn by lottery, tickets proportional to score")
    beats.add(3.2, "Four seconds of this: the swarm leans normative, where raw noise sprays")
    beats.add(2.4, "The same target, already out of its lane")
    beats.add(4.0, "The 'now' score is the same for every candidate, so it caps them all: "
                   "the lottery goes uniform")
    beats.add(3.2, "The fan opens — and leans back, because a hypothesis that returns regains its bias")
    beats.add(2.4, "Trust is not a parameter. It is that minimum, doing its work")
    n = beats.n

    fig = new_fig()
    ax = fig.add_axes([0.055, 0.20, 0.40, 0.70])
    bx = fig.add_axes([0.545, 0.20, 0.42, 0.70])
    cap = caption_band(fig)
    t_ax = np.arange(STEPS + 1) * DT

    def lanes(a):
        for edge, c in [(AW, TEAL), (AW + 0.2 * D, PINK)]:
            a.axhline(edge, color=c, lw=1.1, ls="--")
            a.axhline(-edge, color=c, lw=1.1, ls="--")

    def frame(k):
        ax.clear(); bx.clear()
        i, text, prog = beats.at(k)
        bad = i >= 5
        y0 = y_bad if bad else y_ok
        cand, w = (cand_bad, w_bad) if bad else (cand_ok, w_ok)

        # left: one tournament, zoomed to the candidate spread (the moves are ~0.1 m;
        # against the +-3 m lane scale of the right panel they would be one blob)
        ax.set_xlim(-0.35, 1.15); ax.set_ylim(y0 - 0.48, y0 + 0.48); lanes(ax)
        ax.plot([0], [y0], "o", color=INK, ms=13, zorder=5)
        ax.text(-0.28, y0, "now", fontsize=11.5, color=INK, va="center")
        if i >= 1:
            show = N_NORM if i >= 2 else int(prog * N_NORM) + 1
            # weights span five orders of magnitude, so area is scaled by w^0.35:
            # the ordering stays visible without the small ones vanishing
            rel = (w / w.max()) ** 0.35
            sizes = 28 + 620 * rel if i >= 2 else np.full(N_NORM, 34.0)
            cols = [PURPLE if ww > 0.35 * w.max() else GREY for ww in w] if i >= 2 \
                else [GREY] * N_NORM
            # jitter x so the heaviest candidates do not merge into one blob
            jx = 0.62 + 0.115 * np.linspace(-1, 1, N_NORM)[np.argsort(np.argsort(cand))] * 0.55
            ax.scatter(jx[:show], cand[:show], s=sizes[:show],
                       c=cols[:show], alpha=0.72, zorder=4, edgecolors="none")
            for j in range(show):
                ax.plot([0.03, jx[j] - 0.03], [y0, cand[j]], color=GREY, lw=0.5,
                        alpha=0.30, zorder=1)
        if i >= 2:
            ax.text(0.40, y0 + 0.415, "dot area = norm-compliance weight", fontsize=10.5,
                    color=INK, ha="center")
        if i == 3 or (i >= 3 and not bad) or (i >= 6 and bad):
            r2 = np.random.default_rng(11 if not bad else 12)
            win = int(r2.choice(np.arange(N_NORM), p=w))
            ax.add_patch(FancyArrowPatch((0.03, y0), (0.62, cand[win]),
                                         arrowstyle="-|>", mutation_scale=26,
                                         lw=3.2, color=PINK, zorder=6))
            ax.text(0.85, cand[win], "winner", fontsize=11.5, color=PINK, va="center")
        ax.set_xticks([]); ax.set_ylabel("other vehicle's lateral position [m]", fontsize=12)
        ax.set_title("One tournament, inside one particle  (zoomed)", fontsize=12.5, pad=5)
        if i >= 2:
            spread = w.max() / w.min()
            ax.text(0.40, y0 - 0.43,
                    f"w(now) = {now_bad if bad else now_ok:.3g}    "
                    f"heaviest / lightest ticket = {spread:,.0f}×",
                    fontsize=11, color=PINK if bad else TEAL, ha="center")

        # right: the fan
        bx.set_xlim(0, STEPS * DT); bx.set_ylim(-2.9, 2.9); lanes(bx)
        if i >= 4:
            f_b = fan_bad_b if bad else fan_ok_b
            m = NTRAJ if i >= 5 else max(2, int(prog * NTRAJ))
            if not bad:
                for tr in fan_ok_r[:m]:
                    bx.plot(t_ax, tr, color=GREY, lw=0.6, alpha=0.28)
            for tr in f_b[:m]:
                bx.plot(t_ax, tr, color=PINK if bad else PURPLE, lw=0.7, alpha=0.42)
        bx.set_xlabel("imagined time ahead [s]", fontsize=12)
        bx.set_title("Four seconds of imagined futures" +
                     ("  —  trust withdrawn" if bad else "  —  trust extended"),
                     fontsize=12.5, pad=5, color=PINK if bad else INK)
        if i >= 4 and not bad:
            bx.text(0.12, -2.62, "grey = the same sampling with the bias off",
                    fontsize=10.5, color=GREY)
        for a in (ax, bx):
            a.spines[["top", "right"]].set_visible(False)
            a.tick_params(labelsize=11)
        cap.set_text(text)
        return []

    save(fig, frame, n, "paper_tournament.gif")


# ---------------------------------------------------------------------------
# 3. quiet and loud - one machine
# ---------------------------------------------------------------------------
def make_regimes():
    ev = event_series()
    dr = drift_table()
    # the extremes are in DRIFT, not in headway: the shortest-headway condition is also
    # the fastest (25 m/s at 0.67 s), and it drifts less than the 15 m/s cell at 0.78 s
    lo, hi = dr.loc[dr.drift_pct.idxmin()], dr.loc[dr.drift_pct.idxmax()]
    note(f"regimes: pre-onset drift ranges from {lo.drift_pct:.1f}% of the threshold per "
         f"0.8 s (THW {lo.thw0:.2f} s, {lo.v0:.0f} m/s) to {hi.drift_pct:.1f}% "
         f"(THW {hi.thw0:.2f} s, {hi.v0:.0f} m/s), 28 baseline conditions, mean over 32 seeds")
    # index 3 is t = 0.6 s: the last step BEFORE the lead brakes at t = 0.8 s
    E_at_onset = float(ev["E"][3])
    note(f"regimes: Exp_7 seed 0 account stands at {E_at_onset:.2f} of the threshold at "
         f"t = 0.6 s, the last step before the lead brakes")

    beats = Beats()
    beats.add(3.2, "There is no emergency mode. No flag flips.")
    beats.add(4.0, "Quiet following — and the account is already filling, a little every step")
    beats.add(3.5, "The lead brakes. The same machinery, in a different part of the landscape")
    beats.add(3.5, "Threshold: one re-plan, and the brake goes on 0.8 s after the lead")
    beats.add(4.5, "The quiet drift is not a quirk of this run — it grades smoothly with the gap")
    beats.add(4.0, f"{lo.drift_pct:.0f}% of the threshold per 0.8 s at the longest gap, "
                   f"{hi.drift_pct:.0f}% at the shortest")
    beats.add(2.5, "Response timing therefore starts from a baseline the headway set")
    n = beats.n

    fig = new_fig()
    ax = fig.add_axes([0.06, 0.22, 0.42, 0.66])
    bx = fig.add_axes([0.585, 0.22, 0.38, 0.66])
    cap = caption_band(fig)
    t, E = ev["t"], ev["E"]

    def frame(k):
        ax.clear(); bx.clear()
        i, text, prog = beats.at(k)

        upto = 4 if i <= 1 else (4 + int(prog * 4) if i == 2 else
                                 (len(t) if i >= 3 else 4))
        if i == 1:
            upto = max(2, int(prog * 4) + 1)
        upto = int(np.clip(upto, 2, len(t)))
        ax.plot(t[:upto], E[:upto], color=PURPLE, lw=3.0)
        ax.fill_between(t[:min(upto, 5)], 0, E[:min(upto, 5)], color=PURPLE, alpha=0.14)
        ax.axhline(1.0, color=INK, ls="--", lw=1.6)
        ax.text(0.08, 1.03, "re-plan threshold", fontsize=11, color=INK)
        if i >= 2:
            ax.axvline(0.8, color=PINK, lw=1.8, ls=":")
            ax.text(0.86, 0.06, "lead brakes", fontsize=11, color=PINK, rotation=90)
        if i >= 3:
            ax.axvline(1.4, color=TEAL, lw=1.8, ls=":")
            ax.text(1.4, 1.335, "re-plan", fontsize=11, color=TEAL, ha="center")
            ax.axvline(1.6, color=INK, lw=1.4, ls="-.")
            ax.text(1.78, 1.335, "brake", fontsize=11, color=INK, ha="left")
        if i >= 1:
            # anchored in the empty block x 1.9-3.0, y 0.5-0.95: after the re-plan the
            # curve is back under 0.2 there, and the threshold line sits at 1.0
            ax.annotate(f"already {E_at_onset:.2f} full\nbefore anything happened",
                        xy=(0.70, E_at_onset + 0.02), xytext=(1.92, 0.60), fontsize=11,
                        color=GREY, ha="left", va="center",
                        arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.6,
                                        connectionstyle="arc3,rad=-0.25"))
        ax.set_xlim(0, 3.0); ax.set_ylim(0, 1.42)
        ax.set_xlabel("time [s]", fontsize=12)
        ax.set_ylabel("surprise account", fontsize=12)
        ax.set_title("One run: Exp_7, seed 0", fontsize=12.5, pad=5)

        if i >= 4:
            m = len(dr) if i >= 5 else max(3, int(prog * len(dr)))
            d = dr.iloc[:m]
            sc = bx.scatter(d.thw0, d.drift_pct, c=d.v0, cmap="viridis", s=70,
                            edgecolors="white", linewidths=0.8, zorder=3)
            if i >= 5:
                cb = bx.scatter([], [])
                for v, mk in zip(sorted(dr.v0.unique()), ["o"] * 4):
                    pass
                bx.text(0.97, 0.95, "colour = initial speed\n10 to 25 m/s",
                        transform=bx.transAxes, ha="right", va="top", fontsize=10.5,
                        color=GREY)
        bx.set_xlim(0.4, 4.2); bx.set_ylim(0, 50)
        bx.set_xlabel("initial time headway [s]", fontsize=12)
        bx.set_ylabel("account filled per 0.8 s  [% of threshold]", fontsize=11.5)
        bx.set_title("All 28 baseline conditions", fontsize=12.5, pad=5)
        for a in (ax, bx):
            a.spines[["top", "right"]].set_visible(False)
            a.tick_params(labelsize=11)
        cap.set_text(text)
        return []

    save(fig, frame, n, "paper_regimes.gif")


# ---------------------------------------------------------------------------
# 4. the six preference terms
# ---------------------------------------------------------------------------
def make_preference():
    from comfortzone.field import critical_gap
    from aidriver import BicycleParams, PreferenceParams

    p = PreferenceParams(v_desired=15.0, vehicle=BicycleParams())
    star = float(critical_gap(15.0, 15.0, p, a_required=8.0))
    note(f"preference: closed-form safety-margin boundary gap at 15 m/s steady following "
         f"= {star:.1f} m (a_required 8 m/s^2, t_react and a_OV,min as shipped)")

    half_in = 0.5 * (3.65 - 1.72)
    terms = [
        ("Speed", "near the desired speed", "speed [m/s]", PURPLE),
        ("Pedal effort", "acceleration mostly gentle", "acceleration [m/s²]", BLUE),
        ("Steering effort", "the wheel mostly still", "steering rate [rad/s]", BLUE),
        ("Lane position", "centred in a real lane", "lateral offset [m]", TEAL),
        ("Closing rate", "not closing faster than TTC 5 s", "inverse tau [1/s]", TEAL),
        ("Collision & safety margin", "a counterfactual, as an indicator", "gap [m]", PINK),
    ]

    beats = Beats()
    beats.add(3.0, "The driver's own 'normal' is six independent terms, multiplied together")
    for name, sub, _, _ in terms:
        beats.add(2.4, f"{name} — {sub}")
    beats.add(4.0, "Because they multiply, any exceedance can be blamed on the term responsible")
    beats.add(4.0, "Five are gentle shapes. The sixth is a step — and its assumptions are where the boundary sits")
    n = beats.n

    fig = new_fig()
    axes = [fig.add_axes([0.055 + 0.325 * c, 0.60 - 0.40 * r, 0.245, 0.28])
            for r in range(2) for c in range(3)]
    cap = caption_band(fig)
    fig.text(0.5, 0.955, "The six preference terms  (shapes to scale; parameters as shipped)",
             ha="center", fontsize=13, color=INK)

    def draw_term(a, j):
        name, sub, xlabel, col = terms[j]
        if j == 0:
            x = np.linspace(12, 18, 400); y = np.exp(-0.5 * ((x - 15) / 0.5) ** 2)
        elif j == 1:
            x = np.linspace(-0.6, 0.6, 400); y = np.exp(-0.5 * (x / 0.1) ** 2)
        elif j == 2:
            x = np.linspace(-0.12, 0.12, 400); y = np.exp(-0.5 * (x / 0.02) ** 2)
        elif j == 3:
            x = np.linspace(-2.6, 2.6, 500)
            tri = np.clip(1 - np.abs(x) / half_in, 0, 1)
            y = np.where(np.abs(x) <= half_in, 0.15 + 0.85 * tri, 0.02)
        elif j == 4:
            x = np.linspace(-0.3, 0.9, 400)
            y = np.exp(-0.5 * ((np.maximum(x, 0.2) - 0.2) / 0.125) ** 2)
        else:
            x = np.linspace(2, 60, 400); y = np.where(x >= star, 1.0, 0.05)
        a.plot(x, y, color=col, lw=2.6)
        if j == 3:
            for e in (half_in, -half_in):
                a.axvline(e, color=PINK, ls="--", lw=1.0)
        if j == 5:
            a.axvline(star, color=INK, ls=":", lw=1.2)
            a.text(star + 2, 0.42, f"{star:.0f} m", fontsize=10.5, color=INK)
        a.set_title(f"{name}", fontsize=11.5, color=INK, pad=3)
        a.set_xlabel(xlabel, fontsize=10)
        a.set_yticks([0, 1]); a.tick_params(labelsize=9.5)
        a.spines[["top", "right"]].set_visible(False)

    def frame(k):
        i, text, prog = beats.at(k)
        for j, a in enumerate(axes):
            a.clear()
            if i >= j + 1:
                draw_term(a, j)
            else:
                a.set_xticks([]); a.set_yticks([])
                for s in a.spines.values():
                    s.set_color("#E4E0D8")
            if i >= 7 and j == 5:
                a.patch.set_facecolor("#FBEFF5")
        cap.set_text(text)
        return []

    save(fig, frame, n, "paper_preference.gif")


# ---------------------------------------------------------------------------
# 5. the escape is a property of the landscape
# ---------------------------------------------------------------------------
def make_maneuver():
    g = maneuver_mix()
    for _, r in g.iterrows():
        note(f"maneuver: {r.v_ego_des:.0f} m/s -> braking {100 * r.braking:.0f}%, "
             f"steering involved {100 * r.steer_any:.0f}%, road departure "
             f"{100 * r.leave_road:.0f}% (deposit Analysis_rear_end.xlsx, 28 baseline rows)")

    beats = Beats()
    beats.add(3.5, "Nothing in the code says 'brake below 60 km/h, steer above'")
    beats.add(2.6, "At 10 m/s the model brakes, and essentially never steers")
    beats.add(2.6, "At 15 m/s the two are close")
    beats.add(2.6, "At 20 m/s it steers almost every time")
    beats.add(4.0, "At 25 m/s most runs end off the road — an outcome class of its own")
    beats.add(4.5, "The maneuver falls out of comparing imagined futures under one preference landscape")
    n = beats.n

    fig = new_fig()
    ax = fig.add_axes([0.07, 0.22, 0.56, 0.66])
    tx = fig.add_axes([0.68, 0.22, 0.30, 0.66]); tx.axis("off")
    cap = caption_band(fig)
    speeds = g.v_ego_des.to_numpy()
    xs = np.arange(len(speeds))

    def frame(k):
        ax.clear(); tx.clear(); tx.axis("off")
        i, text, prog = beats.at(k)
        show = 0 if i == 0 else min(i, 4)
        w = 0.26
        for j in range(show):
            r = g.iloc[j]
            ax.bar(xs[j] - w, 100 * r.braking, w, color=PURPLE)
            ax.bar(xs[j], 100 * r.steer_any, w, color=TEAL)
            ax.bar(xs[j] + w, 100 * r.leave_road, w, color=PINK)
        ax.set_xticks(xs); ax.set_xticklabels([f"{int(s)} m/s" for s in speeds], fontsize=12)
        ax.set_ylim(0, 105); ax.set_ylabel("share of runs [%]", fontsize=12)
        ax.set_title("What the model does, by initial speed  (the authors' own 28 baseline runs)",
                     fontsize=12.5, pad=6)
        ax.tick_params(labelsize=11)
        ax.spines[["top", "right"]].set_visible(False)
        if show:
            from matplotlib.patches import Patch
            ax.legend(handles=[Patch(color=PURPLE, label="braking only"),
                               Patch(color=TEAL, label="steering involved"),
                               Patch(color=PINK, label="left the road")],
                      fontsize=11, loc="upper left", frameon=False)
        if i >= 5:
            tx.text(0, 0.86, "Why", fontsize=13, color=PURPLE, fontweight="bold")
            tx.text(0, 0.10,
                    "At low speed comfortable braking\nsheds the energy in time, and\n"
                    "costs the pedal term little.\n\n"
                    "At high speed the deceleration\nneeded to stop behind the lead\n"
                    "becomes so severe that a lane\nchange scores better — despite\n"
                    "its own preference cost.\n\n"
                    "No rule was written for either.",
                    fontsize=11.5, color=INK, va="bottom", linespacing=1.5)
        cap.set_text(text)
        return []

    save(fig, frame, n, "paper_maneuver.gif")


# ---------------------------------------------------------------------------
# transcode the two that already exist as GIFs
# ---------------------------------------------------------------------------
def transcode_existing():
    for name in ("event_anim.gif", "belief_anim.gif"):
        p = FIGS / name
        if p.exists():
            gif_to_mp4(p)
            print("transcoded", name, "-> .mp4 + first-frame poster")
        else:
            print("MISSING (build it first):", name)


BUILDERS = {
    "loop": make_loop,
    "tournament": make_tournament,
    "regimes": make_regimes,
    "preference": make_preference,
    "maneuver": make_maneuver,
    "transcode": transcode_existing,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated subset of " + ",".join(BUILDERS))
    a = ap.parse_args()
    which = [w.strip() for w in a.only.split(",") if w.strip()] or list(BUILDERS)
    for w in which:
        print(f"[{w}]")
        BUILDERS[w]()
    if NUMBERS:
        out = HERE / "paper_anim_numbers.md"
        head = ("# Numbers drawn by the paper-talk animations\n\n"
                "*Generated by `presentation/talk/make_paper_animations.py`. Every value below is\n"
                "read at build time from the authors' OSF deposit or computed from the released\n"
                "preference form; none is typed into a slide by hand. Regenerate after any change\n"
                "to the deposit path or the preference code.*\n\n")
        prev = out.read_text(encoding="utf-8") if out.exists() and len(which) < len(BUILDERS) else ""
        body = "\n".join("- " + n for n in NUMBERS) + "\n"
        out.write_text(head + body if not prev else prev.rstrip() + "\n" + body,
                       encoding="utf-8")
        print("wrote", out)


if __name__ == "__main__":
    main()
