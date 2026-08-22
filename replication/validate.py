"""
Validation: compare our results against the values reported in Schumann et al. (2026).

Compares three things:
  PAPER    -- values stated in the Nature Communications article and its SI
  TRACK A  -- the authors' own code, run here (replication/results_*.pkl)
  TRACK B  -- the independent re-implementation (replication/sweep_aidriver.csv)

Produces the tables printed below and figures/validation_rear_end.png, which reproduces the
structure of the paper's Fig. 3c/3d/3e so the qualitative relations can be checked directly.

Run:  python replication/validate.py
"""
import glob
import os
import pickle
import re
import sys

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")
os.makedirs(FIG, exist_ok=True)
BLUE, RED, GREEN, ORANGE, GREY = "#2B6CB0", "#C53030", "#2F855A", "#C05621", "#4A5568"

EGO_X, EGO_Y, EGO_V = 0, 1, 4
OV_X, OV_V, OV_A = 5, 9, 10


# ----------------------------------------------------------------- paper reference values
PAPER = {
    "fig3a_perception_delay_s": 0.6,
    "fig3a_evidence_delay_s": 0.6,
    "fig3a_pedal_delay_s": 0.2,
    "fig3a_response_time_s": 1.4,
    "fig3a_maneuver": "brake only",
    "fig3b_maneuver": "brake + swerve",
    "rt_short_gap_s": 1.0,          # "approx. 1 s" over gaps 0.5-1.5 s
    "rt_trend": "increases approximately linearly with time gap",
    "collisions_at": "only at the shortest time gap (0.5 s)",
    "maneuver_speed_trend": "braking at low speed, swerving/both at high speed",
    "maneuver_gap_trend_15ms": "P(brake only) increases with time gap",
    "decel_trend": "deceleration magnitude increases with inverse TTC at brake onset",
    "n_simulations": 896,
    "incursion_collision_medium_pct": 82.3,
    "incursion_collision_shallow_pct": 6.3,
    "incursion_human_rt_range_s": (3.5, 4.5),
}


# ----------------------------------------------------------------------------- Track A
def brake_onset(t, v, tol=0.05):
    v = np.asarray(v, float)
    below = np.where(v < v[0] - tol)[0]
    if len(below) == 0 or below[0] == 0:
        return np.nan
    k = below[0]
    t0, t1, y0, y1 = t[k - 1], t[k], v[k - 1], v[k]
    return t0 if y1 == y0 else t0 + (t1 - t0) * ((v[0] - tol) - y0) / (y1 - y0)


def load_track_a():
    out = []
    paths = sorted(glob.glob(os.path.join(HERE, "results_*.pkl")))
    # include partial checkpoints, but only where a completed run of the same condition is
    # absent -- a brake response happens in the first few seconds, so a truncated run is
    # still informative
    finished = {os.path.basename(p) for p in paths}
    for pp in sorted(glob.glob(os.path.join(HERE, "results_*.pkl.partial"))):
        if os.path.basename(pp)[:-len(".partial")] not in finished:
            paths.append(pp)

    for path in paths:
        with open(path, "rb") as f:
            blob = pickle.load(f)
        partial = path.endswith(".partial")
        if partial:
            # a checkpoint stores only `data`; recover the condition from the file name
            m = re.search(r"results_rear_end_v(\d+)_gap([\d.]+)\.pkl", path)
            Config = {"dt": 0.2, "v_ego": float(m.group(1)), "lf": 2.1, "lr": 2.1,
                      "x_tar": float(m.group(1)) * float(m.group(2)) + 4.2}
            print(f"    (using partial checkpoint: {blob['steps_done']}"
                  f"/{blob['T_target']} steps)")
        else:
            Config = blob["Config"]
        eta = blob["data"]["eta"]
        dt = Config["dt"]
        t = np.arange(eta.shape[1]) * dt
        v0 = Config["v_ego"]
        gap_s = (Config["x_tar"] - Config["lf"] - Config["lr"]) / v0
        for b in range(eta.shape[0]):
            a_ov = eta[b, :, OV_A]
            i = np.where(a_ov < -0.1)[0]
            t_lead = t[i[0]] if len(i) else np.nan
            onset = brake_onset(t, eta[b, :, EGO_V])
            lat = float(np.max(np.abs(eta[b, :, EGO_Y])))
            k = int(np.argmin(np.abs(t - onset))) if np.isfinite(onset) else 0
            j = min(k + int(round(1.0 / dt)), eta.shape[1] - 1)
            decel = ((eta[b, j, EGO_V] - eta[b, k, EGO_V]) / (t[j] - t[k])
                     if j > k else np.nan)
            braked = np.isfinite(onset)
            if braked and lat > 0.5:
                man = "both"
            elif braked:
                man = "brake"
            elif lat > 0.5:
                man = "swerve"
            else:
                man = "none yet" if partial else "none"
            out.append(dict(v0=v0, time_gap=round(gap_s, 2), run=b,
                            response_time=onset - t_lead, min_decel=decel,
                            max_lateral=lat, maneuver=man))
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- reporting
def section(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main():
    section("1. Front-to-rear, v0 = 15 m/s, time gap 1.5 s  (the paper's Fig. 3a case)")
    a = load_track_a()
    print(f"{'source':<28} {'response time':>14} {'decel [m/s2]':>13} {'maneuver':>16}")
    print(f"{'PAPER (Fig. 3a)':<28} {PAPER['fig3a_response_time_s']:>13.2f}s "
          f"{'-3 to -5':>13} {PAPER['fig3a_maneuver']:>16}")

    a15 = a[(a.v0 == 15) & (np.isclose(a.time_gap, 1.5, atol=0.35))]
    if len(a15):
        n_both = int((a15.maneuver == "both").sum())
        man_a = f"{a15.maneuver.mode()[0]} ({n_both}/{len(a15)} swerved)"
        print(f"{'TRACK A (authors code)':<28} {a15.response_time.mean():>13.2f}s "
              f"{a15.min_decel.mean():>13.2f} {man_a:>16}")

    b = None
    csv = os.path.join(HERE, "sweep_aidriver.csv")
    if os.path.exists(csv):
        b = pd.read_csv(csv)
        b15 = b[(b.v0 == 15) & (np.isclose(b.time_gap, 1.5))]
        if len(b15):
            print(f"{'TRACK B (ours)':<28} {b15.response_time.mean():>13.2f}s "
                  f"{b15.min_decel.mean():>13.2f} "
                  f"{b15.maneuver.mode()[0]:>16}")
    else:
        print("  (Track B sweep not found -- run replication/sweep_rear_end_aidriver.py)")

    section("2. Track A: all conditions run")
    if len(a):
        print(a.to_string(index=False,
                          float_format=lambda x: f"{x:7.2f}"))

    if b is None:
        return

    section("3. Track B vs paper: response time as a function of time gap")
    print("PAPER: ~1 s and roughly flat for gaps 0.5-1.5 s, then increasing "
          "approximately linearly")
    piv = b.pivot_table(index="time_gap", columns="v0", values="response_time",
                        aggfunc="mean")
    print("\nmean brake response time [s], rows = time gap, cols = v0 [m/s]")
    print(piv.to_string(float_format=lambda x: f"{x:6.2f}"))
    short = b[b.time_gap <= 1.5].response_time
    long_ = b[b.time_gap >= 3.0].response_time
    print(f"\n  gaps <= 1.5 s : mean {short.mean():.2f} s (paper ~1.0 s)")
    print(f"  gaps >= 3.0 s : mean {long_.mean():.2f} s")
    corr = b[["time_gap", "response_time"]].dropna().corr().iloc[0, 1]
    print(f"  correlation(time gap, response time) = {corr:+.3f}  "
          f"(paper: positive, approximately linear)")

    section("4. Track B vs paper: collisions")
    print(f"PAPER: {PAPER['collisions_at']}")
    coll = b.groupby("time_gap").collided.mean() * 100
    print("\ncollision rate [%] by time gap")
    print(coll.to_string(float_format=lambda x: f"{x:5.1f}"))

    section("5. Track B vs paper: evasive maneuver choice (paper Fig. 3c)")
    print(f"PAPER: {PAPER['maneuver_speed_trend']}")
    print(f"PAPER: at 15 m/s, {PAPER['maneuver_gap_trend_15ms']}")
    b["brake_only"] = (b.maneuver == "brake").astype(float)
    piv2 = b.pivot_table(index="time_gap", columns="v0", values="brake_only",
                         aggfunc="mean") * 100
    print("\nP(brake only) [%], rows = time gap, cols = v0 [m/s]")
    print(piv2.to_string(float_format=lambda x: f"{x:5.0f}"))

    section("6. Track B vs paper: deceleration vs inverse TTC at brake onset (Fig. 3e)")
    print(f"PAPER: {PAPER['decel_trend']}")
    d = b[["inv_ttc_at_onset", "min_decel"]].dropna()
    d = d[np.isfinite(d.inv_ttc_at_onset) & (d.inv_ttc_at_onset < 5)]
    if len(d) > 3:
        r = d.corr().iloc[0, 1]
        sl, ic = np.polyfit(d.inv_ttc_at_onset, d.min_decel, 1)
        print(f"\n  n = {len(d)},  correlation = {r:+.3f}  "
              f"(paper: negative -- harder braking at higher inverse TTC)")
        print(f"  fit: min_decel = {sl:.2f} * invTTC + {ic:.2f}")

    section("7. Not attempted")
    print("  Lateral incursion scenario: the paper reports collision rates of "
          f"{PAPER['incursion_collision_medium_pct']}% (medium) and "
          f"{PAPER['incursion_collision_shallow_pct']}% (shallow),")
    print("  and human response times of "
          f"{PAPER['incursion_human_rt_range_s'][0]}-{PAPER['incursion_human_rt_range_s'][1]} s.")
    print("  Our lateral-incursion scenario is not set up faithfully (the paper uses a 300 m")
    print("  initial distance, v0 = 17.88 m/s, and a turn triggered at TTC = 5.15 s with three")
    print("  incursion levels), and Track B's closed loop is not yet reliable enough for the")
    print("  comparison to measure anything but our own implementation gap.")
    print("  Intersection scenario: not attempted.")

    # ------------------------------------------------------------------ figure
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.4))
    colors = {10.0: BLUE, 15.0: GREEN, 25.0: ORANGE, 35.0: RED}

    for v0, grp in b.groupby("v0"):
        m = grp.groupby("time_gap").response_time.mean()
        axes[0].plot(m.index, m.values, "o-", color=colors.get(v0, GREY),
                     label=f"{v0:.0f} m/s")
    axes[0].axhline(PAPER["fig3a_response_time_s"], color=GREY, ls="--", lw=1.5)
    axes[0].text(0.55, PAPER["fig3a_response_time_s"] + 0.05,
                 "paper, v=15, gap=1.5", fontsize=8, color=GREY)
    axes[0].set_xlabel("initial time gap [s]"); axes[0].set_ylabel("brake response time [s]")
    axes[0].set_title("(a) response time vs time gap\npaper Fig. 3d")
    axes[0].legend(fontsize=8, title="$v_0$")

    for v0, grp in b.groupby("v0"):
        m = grp.groupby("time_gap").brake_only.mean() * 100
        axes[1].plot(m.index, m.values, "o-", color=colors.get(v0, GREY),
                     label=f"{v0:.0f} m/s")
    axes[1].set_xlabel("initial time gap [s]"); axes[1].set_ylabel("P(brake only) [%]")
    axes[1].set_title("(b) maneuver choice\npaper Fig. 3c")
    axes[1].legend(fontsize=8, title="$v_0$")

    for v0, grp in b.groupby("v0"):
        g = grp[["inv_ttc_at_onset", "min_decel"]].dropna()
        g = g[np.isfinite(g.inv_ttc_at_onset) & (g.inv_ttc_at_onset < 5)]
        axes[2].scatter(g.inv_ttc_at_onset, g.min_decel, s=16, alpha=0.6,
                        color=colors.get(v0, GREY), label=f"{v0:.0f} m/s")
    if len(d) > 3:
        xs = np.linspace(0, min(d.inv_ttc_at_onset.max(), 2.0), 20)
        axes[2].plot(xs, sl * xs + ic, color="k", lw=1.6, ls="--", label="fit")
    axes[2].set_xlabel(r"inverse TTC at brake onset [s$^{-1}$]")
    axes[2].set_ylabel("lowest acceleration [m/s$^2$]")
    axes[2].set_title("(c) braking magnitude\npaper Fig. 3e")
    axes[2].legend(fontsize=8)

    fig.suptitle("Track B (independent re-implementation) against the structure of "
                 "Schumann et al. (2026) Fig. 3", fontsize=11)
    fig.tight_layout()
    out = os.path.join(FIG, "validation_rear_end.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("\nwrote", os.path.abspath(out))


if __name__ == "__main__":
    main()
