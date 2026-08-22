"""
Analyse the output of the authors' model (run via `run_rear_end_single.py`).

Extracts the brake response time using the same definition as the paper -- following
Markkula et al., fit a piecewise-linear function to the recorded speed and take the instant
where the first constant segment turns into a falling one -- and plots the trajectory.

Run:  python replication/analyze_rear_end.py [results_*.pkl]
"""
import glob
import os
import pickle
import sys

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")
os.makedirs(FIG, exist_ok=True)

BLUE, RED, GREY = "#2B6CB0", "#C53030", "#4A5568"

# column layout of the authors' `eta` state vector, inferred from the simulation code
EGO_X, EGO_Y, EGO_TH, EGO_DELTA, EGO_V = 0, 1, 2, 3, 4
OV_X, OV_Y, OV_TH, OV_DELTA, OV_V, OV_A = 5, 6, 7, 8, 9, 10


def brake_response_time(t, v, v0_tol=0.05):
    """
    Brake onset by piecewise-linear fit: the last instant at which speed is still within
    `v0_tol` of its initial value, interpolated against the following falling segment.

    Returns (onset_time, fitted_deceleration).
    """
    v = np.asarray(v, dtype=float)
    v0 = v[0]
    below = np.where(v < v0 - v0_tol)[0]
    if len(below) == 0:
        return np.nan, np.nan
    k = below[0]
    if k == 0:
        return t[0], np.nan
    # linear interpolation of the crossing of v0 - v0_tol
    t0, t1 = t[k - 1], t[k]
    y0, y1 = v[k - 1], v[k]
    onset = t0 if y1 == y0 else t0 + (t1 - t0) * ((v0 - v0_tol) - y0) / (y1 - y0)
    # deceleration over the following second
    j = min(k + int(round(1.0 / (t[1] - t[0]))), len(v) - 1)
    decel = (v[j] - v[k]) / (t[j] - t[k]) if j > k else np.nan
    return onset, decel


def other_brake_onset(t, a_ov):
    idx = np.where(np.asarray(a_ov, dtype=float) < -0.1)[0]
    return t[idx[0]] if len(idx) else np.nan


def analyse(path):
    with open(path, "rb") as f:
        blob = pickle.load(f)
    data, Config = blob["data"], blob["Config"]
    eta = data["eta"]                       # (batch, T, 14)
    dt = Config["dt"]
    T = eta.shape[1]
    t = np.arange(T) * dt

    print(f"\n=== {os.path.basename(path)}")
    print(f"    v0 = {Config['v_ego']:.0f} m/s, batch = {eta.shape[0]}, "
          f"T = {T} steps ({T*dt:.1f} s), runtime {blob['runtime_s']/60:.1f} min")

    rows = []
    for b in range(eta.shape[0]):
        v_ego = eta[b, :, EGO_V]
        y_ego = eta[b, :, EGO_Y]
        a_ov = eta[b, :, OV_A]
        t_ov = other_brake_onset(t, a_ov)
        onset, decel = brake_response_time(t, v_ego)
        rt = onset - t_ov
        gap = eta[b, :, OV_X] - eta[b, :, EGO_X]
        rows.append((t_ov, onset, rt, decel, float(np.max(np.abs(y_ego))), float(gap.min())))
        print(f"    run {b}: lead brakes {t_ov:.1f}s | ego brake onset {onset:.1f}s | "
              f"RT = {rt:.2f}s | decel {decel:5.2f} m/s^2 | "
              f"max |lateral| {np.max(np.abs(y_ego)):.2f} m | min gap {gap.min():.1f} m")

    rts = np.array([r[2] for r in rows])
    print(f"    mean brake response time = {np.nanmean(rts):.2f} s "
          f"(paper reports 1.4 s for v0=15 m/s, 1.5 s time gap)")

    fig, axes = plt.subplots(3, 1, figsize=(8.4, 7.6), sharex=True)
    for b in range(eta.shape[0]):
        lab = "ego" if b == 0 else None
        axes[0].plot(t, eta[b, :, EGO_V], color=BLUE, lw=1.6, alpha=0.85, label=lab)
        axes[1].plot(t, eta[b, :, EGO_Y], color=BLUE, lw=1.6, alpha=0.85)
        axes[2].plot(t, eta[b, :, OV_X] - eta[b, :, EGO_X], color=BLUE, lw=1.6, alpha=0.85)
    axes[0].plot(t, eta[0, :, OV_V], color=GREY, lw=2, ls="--", label="lead")
    axes[0].set_ylabel("speed [m/s]"); axes[0].legend(fontsize=9)
    axes[1].set_ylabel("ego lateral position [m]")
    axes[1].axhline(3.65, color=GREY, ls=":", lw=1)
    axes[2].set_ylabel("separation [m]")
    axes[2].set_xlabel("time [s]")

    t_ov = rows[0][0]
    for ax in axes:
        ax.axvline(t_ov, color=GREY, lw=1.2, alpha=0.7)
        for r in rows:
            ax.axvline(r[1], color=RED, lw=0.9, ls="--", alpha=0.5)
    axes[0].set_title("Authors' active-inference model, front-to-rear scenario\n"
                      f"v0 = {Config['v_ego']:.0f} m/s, time gap 1.5 s; "
                      f"grey = lead brakes, red dashed = ego brake onset")
    fig.tight_layout()
    out = os.path.join(FIG, "replication_rear_end.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("    wrote", os.path.abspath(out))


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "results_*.pkl")))
    if not paths:
        print("no results files; run replication/run_rear_end_single.py first")
        sys.exit(1)
    for p in paths:
        analyse(p)
