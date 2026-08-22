"""
Surprise measures applied to a driving scenario.

Part 1 reproduces the *structure* of Dinparastdjadid, Supeene & Engstrom (2023): a
generative model emits a belief about a road user's future position at each timestep; four
surprise measures are computed from that stream; the two novel measures (residual
information, antithesis) are compared with the two classical ones (surprisal, Bayesian
surprise) on a lateral cut-in.

Since we have no trained trajectory predictor here, the generative model is a small
hand-built stand-in with the right qualitative structure: a Gaussian mixture over future
lateral position whose components are "stays in lane" and "changes lane", with weights that
update as evidence accumulates. That is enough to demonstrate the measures' behaviour --
notably the zero-floor and the silencing of unsurprising information gain.

Part 2 runs the active-inference driver agent on a rear-end conflict and plots the internal
surprise / evidence / re-plan signals against behaviour.

Produces:
  figures/surprise_cutin.png
  figures/surprise_parameters.png
  figures/ai_rear_end.png

Run:  python demo_surprise.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from surprise import (  # noqa: E402
    GaussianMixture, antithesis, bayesian_surprise, residual_information, shannon_surprise,
)

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIG, exist_ok=True)

BLUE, RED, GREEN, GREY = "#2B6CB0", "#C53030", "#2F855A", "#4A5568"

DT = 0.1
T = 80
T_CUTIN = 4.0          # s, when the neighbouring vehicle starts moving across
LANE_W = 3.65


def true_lateral(t):
    """Actual lateral position of the cutting-in vehicle (starts one lane to the right)."""
    if t < T_CUTIN:
        return LANE_W
    s = min((t - T_CUTIN) / 2.0, 1.0)
    return LANE_W * (1 - (3 * s ** 2 - 2 * s ** 3))     # smoothstep across


def predictor(t_made, t_about):
    """
    Stand-in generative model: a two-component GMM over lateral position at `t_about`, made
    at `t_made`.

    Component 1 -- stays in its lane; component 2 -- completes a lane change. The mixture
    weight on "changing" rises once lateral motion has actually been observed, and the
    per-component variance grows with prediction horizon, exactly as a learned predictor's
    would.
    """
    horizon = max(t_about - t_made, 0.0)
    y_now = true_lateral(t_made)
    y_prev = true_lateral(max(t_made - 0.3, 0.0))
    lateral_rate = (y_now - y_prev) / 0.3

    # evidence for a lane change: observed inward lateral speed
    w_change = 1.0 / (1.0 + np.exp(-(-lateral_rate - 0.15) / 0.10))
    w_change = float(np.clip(w_change, 0.02, 0.98))

    mu_stay = y_now + 0.0 * horizon
    mu_change = max(y_now - abs(lateral_rate if lateral_rate else 0.9) * horizon, 0.0)
    if w_change < 0.1:
        mu_change = max(y_now - 0.9 * horizon, 0.0)

    sd = 0.12 + 0.28 * horizon
    return GaussianMixture(weights=[1 - w_change, w_change],
                           means=[[mu_stay], [mu_change]],
                           covs=[[[sd ** 2]], [[sd ** 2]]])


def build_stream():
    times = np.arange(T) * DT
    beliefs = {i: {} for i in range(T)}
    for i, tm in enumerate(times):
        for j in range(T):
            ta = times[j]
            if 0 <= ta - tm <= 3.0:
                beliefs[i][j] = predictor(tm, ta)
    obs = np.array([true_lateral(t) for t in times])
    return times, beliefs, obs


def compute_series(times, beliefs, obs, h=1.0, z=0.2):
    hi, zi = int(round(h / DT)), int(round(z / DT))
    rng = np.random.default_rng(0)
    out = {k: np.full(T, np.nan) for k in
           ["surprisal", "residual_information", "bayesian_surprise", "antithesis"]}
    for i in range(T):
        pi = i - hi
        if pi >= 0 and i in beliefs.get(pi, {}):
            prior = beliefs[pi][i]
            out["surprisal"][i] = float(shannon_surprise(float(obs[i]), prior))
            out["residual_information"][i] = float(residual_information(float(obs[i]), prior))
        ta = i + zi
        if pi >= 0 and ta in beliefs.get(pi, {}) and ta in beliefs.get(i, {}):
            out["bayesian_surprise"][i] = bayesian_surprise(
                beliefs[i][ta], beliefs[pi][ta], n_samples=8000, rng=rng)
            out["antithesis"][i] = antithesis(
                beliefs[i][ta], beliefs[pi][ta], n_samples=8000, rng=rng)
    return out


def fig_cutin(times, obs, series):
    fig, axes = plt.subplots(3, 1, figsize=(8.6, 8.0), sharex=True)

    axes[0].plot(times, obs, color=GREY, lw=2.2)
    axes[0].axhline(LANE_W / 2, color=GREY, ls=":", lw=1)
    axes[0].set_ylabel("lateral position [m]")
    axes[0].set_title("Surprise measures on a lateral cut-in\n"
                      "(grey line = lane boundary; dashed vertical = cut-in onset)")

    axes[1].plot(times, series["surprisal"], color=GREY, lw=1.8, label="surprisal")
    axes[1].plot(times, series["residual_information"], color=RED, lw=2.2,
                 label="residual information")
    axes[1].axhline(0, color="k", lw=0.8)
    axes[1].set_ylabel("probabilistic mismatch")
    axes[1].legend(fontsize=9)

    axes[2].plot(times, series["bayesian_surprise"], color=GREY, lw=1.8,
                 label="Bayesian surprise (KL)")
    axes[2].plot(times, series["antithesis"], color=BLUE, lw=2.2, label="antithesis")
    axes[2].axhline(0, color="k", lw=0.8)
    axes[2].set_ylabel("belief mismatch")
    axes[2].set_xlabel("time [s]")
    axes[2].legend(fontsize=9)

    for ax in axes:
        ax.axvline(T_CUTIN, color=RED, ls="--", lw=1.3, alpha=0.7)
    fig.tight_layout()
    out = os.path.join(FIG, "surprise_cutin.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("wrote", out)


def fig_parameters(times, beliefs, obs):
    """Effect of history window h and lookahead z, as in Fig. 5 of the paper."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    for h, c in zip([0.5, 1.0, 2.0], [GREY, BLUE, RED]):
        s = compute_series(times, beliefs, obs, h=h, z=0.2)
        axes[0].plot(times, s["antithesis"], color=c, lw=2.0, label=f"h = {h:.1f} s")
    axes[0].set_title("varying history window h  (z = 0.2 s)")
    axes[0].set_xlabel("time [s]"); axes[0].set_ylabel("antithesis")
    axes[0].legend(fontsize=9)

    for z, c in zip([0.2, 1.0, 2.0], [GREY, BLUE, RED]):
        s = compute_series(times, beliefs, obs, h=1.0, z=z)
        axes[1].plot(times, s["antithesis"], color=c, lw=2.0, label=f"z = {z:.1f} s")
    axes[1].set_title("varying lookahead z  (h = 1.0 s)")
    axes[1].set_xlabel("time [s]")
    axes[1].legend(fontsize=9)

    for ax in axes:
        ax.axvline(T_CUTIN, color=RED, ls="--", lw=1.2, alpha=0.6)
    fig.tight_layout()
    out = os.path.join(FIG, "surprise_parameters.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("wrote", out)


def fig_active_inference():
    """Run the active-inference agent on a rear-end conflict and plot its internals."""
    from aidriver import ActiveInferenceDriver, AgentParams, PreferenceParams, RearEndScenario

    pref = PreferenceParams(v_desired=15.0, a_other_min=-6.0)
    ap = AgentParams(horizon=20, n_particles=50, n_policies=100, cem_iters=8,
                     seed=0, alpha=0.0)
    agent = ActiveInferenceDriver(pref, ap)
    sc = RearEndScenario(v0=15.0, time_gap=1.5, t_brake=3.0)
    res = sc.run(agent, T=45)

    t = res.t
    eps = np.array([i["surprise"] for i in res.info])
    ev = np.array([i["evidence"] for i in res.info])
    rp = np.array([i["replanned"] for i in res.info])
    margin = np.array([i["safety_margin"] for i in res.info])

    fig, axes = plt.subplots(4, 1, figsize=(8.6, 9.4), sharex=True)
    axes[0].plot(t, res.ego[:, 4], color=BLUE, lw=2, label="ego")
    axes[0].plot(t, res.other[:, 4], color=GREY, lw=2, ls="--", label="lead")
    axes[0].set_ylabel("speed [m/s]"); axes[0].legend(fontsize=9)
    axes[0].set_title("Active-inference agent, front-to-rear conflict\n"
                      "grey line = lead brakes; red marks = full policy re-plan")

    axes[1].plot(t, res.actions[:, 0], color=BLUE, lw=2)
    axes[1].set_ylabel("ego accel [m/s$^2$]")

    axes[2].semilogy(t, np.maximum(eps, 1e-2), color=RED, lw=2)
    axes[2].set_ylabel(r"surprise $\varepsilon_t$")

    axes[3].plot(t, ev, color=GREEN, lw=2)
    axes[3].axhline(1.0, color=GREY, ls=":", lw=1.5)
    axes[3].set_ylabel("accumulated evidence $E_t$")
    axes[3].set_xlabel("time [s]")

    for ax in axes:
        ax.axvline(sc.t_brake, color=GREY, lw=1.2, alpha=0.7)
        for tt in t[rp]:
            ax.axvline(tt, color=RED, lw=0.9, alpha=0.35)
    fig.tight_layout()
    out = os.path.join(FIG, "ai_rear_end.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print("wrote", out)

    idx = np.arange(len(t))
    after = idx >= int(sc.t_brake / sc.veh.dt)
    braking = after & (res.actions[:, 0] < -1.0)
    onset = t[braking][0] if braking.any() else np.nan
    print(f"  lead brakes at {sc.t_brake:.1f}s, ego brake onset {onset:.1f}s "
          f"(response {onset - sc.t_brake:.1f}s), collided={res.collided}, "
          f"min clearance {res.min_gap:.2f} m, {rp.sum()} re-plans")


if __name__ == "__main__":
    times, beliefs, obs = build_stream()
    series = compute_series(times, beliefs, obs)
    fig_cutin(times, obs, series)
    fig_parameters(times, beliefs, obs)

    print("\nzero-floor check on the real stream:")
    for k in ["surprisal", "residual_information", "bayesian_surprise", "antithesis"]:
        y = series[k][np.isfinite(series[k])]
        print(f"  {k:22s} min={y.min():9.3f}  max={y.max():9.3f}  "
              f"frac|.|<1e-6={np.mean(np.abs(y) < 1e-6):.2f}")

    fig_active_inference()
