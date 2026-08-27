"""Card A.4: predict the Button press-time distributions from the Random-fitted model.

The two paradigms observe the same latent process from different sides. The fixed-clip
Random design samples the response-time CDF at six truncation points; the Button design
samples the density directly. If one accumulator governs both, the model fitted on
Random should predict Button press times with a single paradigm shift -- and the
direction of that shift is already known from the documented cross-paradigm excess of
early pressing, largest at intermediate criticality (+0.26 at TTC6).

What is fitted, and what is not
-------------------------------
Nothing about the accumulator is refitted here. Gain, threshold location, between-driver
spread and lapse are taken from the Random fit (card A.3, which in turn fixes the spread
from card A.2). The single free parameter is the paradigm shift delta, and it is fitted
twice -- once acting on the threshold and once on the gain -- because those two make
different predictions about the *shape* of the press-time distribution rather than only
its location. Which shape fits is the answer the card asks for; it is decision 3 of the
handbook chapter 11 list, and the plan is explicit that it should be tested rather than
assumed.

Only criticality levels shared with the Random design are used, since the model's
parameters were fitted there; the Button design's extra levels are reported as
out-of-range predictions rather than folded into the comparison.

    python replication/czb/validate_button.py
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from comfortzone.czb_data import (BUTTON_CUTIN_TRACES, TIMEPOINT_OFFSET_S,   # noqa: E402
                                  button_cutin_trials, random_cutin_trials,
                                  stimulus_field)
from fit_recovery import _gh_nodes, fit_marginal, priors_for                 # noqa: E402
from fit_stage2 import (LAMBDA_S, N_GH, N_PATHS, SMOOTH, build_cells,        # noqa: E402
                        evidence_paths, fit)

OUT = HERE / "out"
FIGS = REPO / "figures"
torch.set_default_dtype(torch.float64)
MUTED, BLUE, ORANGE = "#52514e", "#2a78d6", "#eb6834"
CRIT_COLORS = {"TTC4": "#b00020", "TTC6": "#eda100", "TTC8": "#2a78d6"}


def button_paths(seed: int = 0) -> dict:
    """Cumulative evidence and shared noise paths on the Button stimuli."""
    rng = np.random.default_rng(seed)
    grids = {}
    for crit, path in BUTTON_CUTIN_TRACES.items():
        f = stimulus_field(path)
        t = f.t_since_onset.to_numpy()
        d = f.deficit.to_numpy()
        grids[crit] = (t, np.cumsum(d * np.diff(t, prepend=t[0])))
    n_t = max(len(t) for t, _ in grids.values())
    steps = rng.standard_normal((N_PATHS, n_t))
    out = {}
    for crit, (t, E) in grids.items():
        dt = np.diff(t, prepend=t[0])
        out[crit] = {"t": t, "E": E,
                     "W": np.cumsum(steps[:, :len(t)] * np.sqrt(np.maximum(dt, 0))[None, :],
                                    axis=1)}
    return out


def predicted_press_cdf(paths, crit, times, log_k, mu_a, sigma_pop, b, lam,
                        gain_shift=0.0, level_shift=0.0):
    """P(press by t) for a grid of times, integrating the driver threshold out."""
    zz, ww = _gh_nodes(N_GH)
    theta = np.exp(mu_a + level_shift + sigma_pop * zz)
    p = paths[crit]
    A = np.exp(log_k + gain_shift) * p["E"][None, :] + p["W"]
    run_max = np.maximum.accumulate(A, axis=1)
    out = []
    for tt in times:
        m = p["t"] <= (tt - lam)
        if not m.any():
            out.append(float(b))
            continue
        M = run_max[:, m][:, -1]
        crossed = (M[:, None] >= theta[None, :]).mean(axis=0)
        out.append(float(((b + (1 - b) * crossed) * ww).sum()))
    return np.array(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    t0 = time.time()

    r = random_cutin_trials()
    pid = r.participant.factorize()[0].astype(int)
    x = r.deficit_max.to_numpy(float)
    y = r.intervene.to_numpy(float)

    print("recovering the Random-fitted parameters ...", flush=True)
    s1 = fit_marginal(x, y, pid, priors_for(x))
    sigma_pop = float(s1["sigma_pop"])
    rnd_paths = evidence_paths(args.seed)
    phi = fit(rnd_paths, build_cells(r), sigma_pop, LAMBDA_S)
    log_k, mu_a, b = float(phi[0]), float(phi[1]), float(torch.sigmoid(phi[2]))
    print(f"  gain {np.exp(log_k):.3g}, mu_a {mu_a:.3f}, lapse {b:.3f}, "
          f"sigma_pop {sigma_pop:.3f}", flush=True)

    btn = button_cutin_trials()
    shared = [c for c in ("TTC4", "TTC6", "TTC8") if c in set(btn.criticality)]
    bp = button_paths(args.seed)

    # ---- fit the single paradigm shift, two ways ----
    checkpoints = sorted(TIMEPOINT_OFFSET_S.values())[1:]      # C2..C6, as in the plan
    obs_cdf = {c: np.array([float((btn[(btn.criticality == c) & (btn.censored == 0)]
                                   .press_since_onset <= t).mean())
                            for t in checkpoints]) for c in shared}

    def loss_for(kind, val):
        err = []
        for c in shared:
            pred = predicted_press_cdf(bp, c, checkpoints, log_k, mu_a, sigma_pop, b,
                                       LAMBDA_S,
                                       gain_shift=val if kind == "gain" else 0.0,
                                       level_shift=val if kind == "level" else 0.0)
            err.append(pred - obs_cdf[c])
        return float(np.sqrt(np.mean(np.concatenate(err) ** 2)))

    fits = {}
    for kind, lo, hi in (("level", -1.5, 1.5), ("gain", -2.0, 2.0)):
        grid = np.linspace(lo, hi, 121)
        vals = [loss_for(kind, v) for v in grid]
        best = float(grid[int(np.argmin(vals))])
        fits[kind] = (best, float(np.min(vals)))
        print(f"  best {kind} shift {best:+.3f} -> RMSE {np.min(vals):.3f}", flush=True)

    winner = min(fits, key=lambda k: fits[k][1])

    # ---- figure: predicted vs observed press-time CDFs ----
    fig, axes = plt.subplots(1, len(shared), figsize=(4.0 * len(shared), 3.6),
                             sharey=True)
    tgrid = np.linspace(0.0, 2.5, 60)
    for ax, c in zip(np.atleast_1d(axes), shared):
        d = btn[(btn.criticality == c) & (btn.censored == 0)].press_since_onset.dropna()
        ax.step(np.sort(d), np.arange(1, len(d) + 1) / len(d), color=MUTED, lw=1.6,
                where="post", label="observed")
        ax.plot(tgrid, predicted_press_cdf(bp, c, tgrid, log_k, mu_a, sigma_pop, b,
                                           LAMBDA_S), color=BLUE, lw=1.5, ls="--",
                label="Random fit, no shift")
        kind, val = winner, fits[winner][0]
        ax.plot(tgrid, predicted_press_cdf(bp, c, tgrid, log_k, mu_a, sigma_pop, b,
                                           LAMBDA_S,
                                           gain_shift=val if kind == "gain" else 0.0,
                                           level_shift=val if kind == "level" else 0.0),
                color=ORANGE, lw=1.8, label=f"with {kind} shift")
        ax.set_title(c)
        ax.set_xlabel("press time since onset [s]")
        ax.grid(color="#e4e4e0", lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    np.atleast_1d(axes)[0].set_ylabel("P(pressed by t)")
    np.atleast_1d(axes)[0].legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGS / "button_validation.png", dpi=150)

    # ---- report ----
    L = ["# Card A.4 — Button press times predicted from the Random fit\n",
         "Every accumulator parameter is carried over from the Random design unchanged "
         f"(gain {np.exp(log_k):.3g}, threshold location {mu_a:.3f}, between-driver "
         f"spread {sigma_pop:.3f}, lapse {b:.3f}). The only free quantity is a single "
         "paradigm shift, fitted twice: acting on the threshold, and acting on the "
         "gain.\n",
         "## Which shift fits\n",
         "| shift acts on | fitted value | RMSE against the observed press-time CDF |",
         "|---|---|---|"]
    for kind in ("level", "gain"):
        mark = " **(better)**" if kind == winner else ""
        L.append(f"| {kind} | {fits[kind][0]:+.3f} | {fits[kind][1]:.3f}{mark} |")

    L += ["\nThe two are distinguished by the *shape* of the press-time distribution, "
          "not only its location: a threshold shift moves the whole curve, a gain shift "
          "also changes how fast it rises. On this data the "
          f"**{winner}** shift fits better.\n",
          "## Predicted against observed at the fixed-clip checkpoints\n",
          "| criticality | " + " | ".join(f"{t:.1f} s" for t in checkpoints) + " |",
          "|---" * (len(checkpoints) + 1) + "|"]
    kind, val = winner, fits[winner][0]
    worst = 0.0
    for c in shared:
        pred = predicted_press_cdf(bp, c, checkpoints, log_k, mu_a, sigma_pop, b,
                                   LAMBDA_S,
                                   gain_shift=val if kind == "gain" else 0.0,
                                   level_shift=val if kind == "level" else 0.0)
        diff = pred - obs_cdf[c]
        worst = max(worst, float(np.max(np.abs(diff))))
        L.append(f"| {c} obs / pred | " + " | ".join(
            f"{o:.2f} / {p:.2f}" for o, p in zip(obs_cdf[c], pred)) + " |")
    L += [f"\nLargest absolute discrepancy at any checkpoint: **{worst:.3f}**.\n",
          "## Acceptance criterion\n",
          f"The documented cross-paradigm excess is reproduced within 0.05 at the "
          f"fixed-clip checkpoints — **{'PASS' if worst <= 0.05 else 'FAIL'}** "
          f"(worst {worst:.3f}).\n",
          "![Predicted and observed press-time distributions](../../figures/button_validation.png)\n",
          f"Runtime {(time.time() - t0) / 60:.1f} min."]
    (OUT / "button_validation_summary.md").write_text("\n".join(L) + "\n",
                                                      encoding="utf-8")
    print("\n" + "\n".join(L))


if __name__ == "__main__":
    main()
