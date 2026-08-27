"""Card A.3: the accumulator layer, and the pre-registered test it exists to settle.

The static threshold of stage 1 cannot express the one feature the human surface most
clearly has: at a fixed criticality, the probability of intervening keeps rising with
exposure time. That gradient is the accumulator's signature, and it was visible in the
stage-0 residual, in the perceived-safety ratings, and in the response surface itself
before any accumulator was fitted. This card asks whether adding one -- with no
per-scenario parameters -- closes the within-scenario gap to the kinematic comparators.

The model
---------
Evidence is the per-frame comfort-zone deficit along the clip (the series, not its
running maximum). A linear accumulator integrates it under Brownian noise, and a
response occurs when the accumulation first crosses the driver's threshold:

    A_i(t) = k * INT deficit(s) ds + W(t),            W a Wiener process, sd 1 per sqrt(s)
    responds by T  <=>  max_{s <= T} A_i(s) >= theta_i
    theta_i = exp(mu_a + sigma_pop * z_i),            z_i ~ Normal(0, 1)

with the observed response P = b + (1 - b) P(crossed by T_eff), and T_eff = t_end - lam
the clip's end shifted by the motor latency: a participant can only report an
intervention they would have made inside the clip.

**A trial-level threshold variability sigma_trial is free** *(v3, 2026-08-27, decided
at review gate R.1 after the v2 run)*: stage 1 needed a within-driver response sd of
~970 deficit units (~0.18 of the median level on the log scale) to reproduce the
surface's shallow criticality gradient; the v2 accumulator pinned the between-driver
spread (rightly) but carried NO counterpart to that within-driver variability, leaving
Wiener noise as the only flattening degree of freedom -- so its maximum-likelihood
solution abandoned the evidence (fitted gain 1.2e-4, drift-to-noise 0.73, a
criticality-flat surface; verified to be the global optimum by a committed grid scan,
`--scan`). The repair is the accumulator analogue of stage 1's sigma_resp: the
effective log-threshold spread is sqrt(sigma_pop^2 + sigma_trial^2) with sigma_pop
still pinned at card A.2's between-driver value and sigma_trial free. At cell level,
driver- and trial-level threshold variability are indistinguishable; the pinned part
keeps the between-driver interpretation, the free part restores the response
variability the static model always had.

**Accumulation is gated at manoeuvre onset** *(v2, 2026-08-27, decided at review gate
R.1)*: the deficit is exactly zero before onset, so the drift is unaffected, but the
Wiener noise now also accumulates only from onset. The v1 run integrated noise from
clip start, through a 15.1 s pre-onset window whose length is a property of stimulus
presentation, not of drivers; the running maximum of that noise alone had sd ~3.9,
comparable to the entire post-onset drift, which forced the threshold up, collapsed
the lapse to zero, and flattened the predicted surface across criticality (in-sample
RMSE 0.182, worse than the stage-0 static probit's 0.125 -- worklog query A.3.Q1).
The gate is observable to the driver -- onset is the stimulus's first lateral motion
(the pipeline's 0.03 m detection threshold) -- so this is evidence-gated accumulation,
not oracle knowledge. The pre-onset responses that do occur are anticipation and
lapse, which the b floor carries, exactly as in stage 1. The alternative remedy, a
leaky accumulator, was considered at the gate and held in reserve: a leak bounds
pre-onset noise the same way (OU stationarity) but also discounts early post-onset
evidence, which alters the very time-integration claim under test, and it adds a free
parameter. `--ungated-noise` reproduces the v1 model.

Identification and what is fixed, with reasons
----------------------------------------------
* The noise scale is fixed at 1. Gain, threshold and noise are jointly identified only
  up to one common scale, so one must be pinned; pinning the noise leaves the gain and
  the threshold location free, which are the interpretable pair.
* `sigma_pop` is fixed at the value card A.2 fitted on this same axis, not refitted.
  The claim under test concerns the time gradient, and re-fitting the between-driver
  spread here would let the accumulator absorb it. As of v2 the value comes from the
  **hierarchical-lapse** stage-1 fit, per the R.1 decision on query A.2.Q2; the
  stage-2 lapse b stays a single population-level floor because the fit is at cell
  level, where only the population-averaged floor is expressible.
* Motor latency lam = 0.25 s, per `docs/czb_validation_roadmap.md` section 5.3, with
  sensitivity refits at 0.15 and 0.35 s reported alongside; the bracket matters more
  than the point value because lam trades against the threshold location.
* 2 000 simulated paths per criticality level, drawn once with a fixed seed and reused
  at every optimizer step (common random numbers), so the objective is deterministic
  rather than a noisy target. At p = 0.5 the Monte Carlo standard error is 0.011, below
  the third decimal of the surface being fitted.
* The crossing indicator is smoothed by a logistic of width 0.05, which is 4% of the
  path-to-path spread of the running maximum -- sharp enough to approximate the
  indicator, smooth enough to differentiate.

Pre-registered decision rule (card A.3, fixed before the fit)
--------------------------------------------------------------
Held-out RMSE on the 18-cell surface, leave-one-criticality-out:
  <= 0.11  the accumulator closes the gap (the 2D state rule reaches 0.120 and the
           scenario-specific design regression about 0.10);
  >  0.13  failure, reported as evidence against the framework;
  between  neither, reported as such.
The static stage-1 threshold on the same folds is the baseline to beat.

    python replication/czb/fit_stage2.py
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from comfortzone.czb_data import (RANDOM_CUTIN_TRACES, TIMEPOINT_OFFSET_S,   # noqa: E402
                                  random_cutin_trials, stimulus_field)
from fit_recovery import _gh_nodes, fit_marginal, priors_for                 # noqa: E402
from fit_stage1 import fit_hier_lapse                                        # noqa: E402

OUT = HERE / "out"
torch.set_default_dtype(torch.float64)

N_PATHS = 2000
SMOOTH = 0.05
LAMBDA_S = 0.25
LAMBDA_SENSITIVITY = (0.15, 0.35)
N_GH = 150
CRITS = ("TTC4", "TTC6", "TTC8")


def evidence_paths(seed: int = 0, ungated: bool = False) -> dict:
    """Cumulative evidence per criticality level, and shared noise paths.

    Returns, per criticality: the time grid since onset, the cumulative integral of the
    deficit from clip start, `N_PATHS` Wiener paths on the same grid, and `tau`, the
    accumulated noise time. The paths are drawn once and shared across every criticality
    level and optimizer step. Noise increments are gated at manoeuvre onset (t > 0)
    unless `ungated`, which reproduces the v1 model.
    """
    rng = np.random.default_rng(seed)
    out = {}
    grids = {}
    for crit, path in RANDOM_CUTIN_TRACES.items():
        f = stimulus_field(path)
        t = f.t_since_onset.to_numpy()
        d = f.deficit.to_numpy()
        dt = np.diff(t, prepend=t[0])
        grids[crit] = (t, np.cumsum(d * dt))
    n_t = max(len(t) for t, _ in grids.values())
    # One Wiener path bank, truncated per grid; identical draws across criticalities so
    # differences between them are stimulus differences, not sampling noise.
    steps = rng.standard_normal((N_PATHS, n_t))
    for crit, (t, E) in grids.items():
        dt = np.diff(t, prepend=t[0])
        gate = np.ones_like(t, dtype=bool) if ungated else (t > 0.0)
        dtau = np.maximum(dt, 0.0) * gate
        w = np.cumsum(steps[:, :len(t)] * np.sqrt(dtau)[None, :], axis=1)
        out[crit] = {"t": t, "E": E, "W": w, "tau": np.cumsum(dtau)}
    return out


def cell_cross_prob(paths: dict, log_k: torch.Tensor, theta: torch.Tensor,
                    crit: str, t_end: float, lam: float) -> torch.Tensor:
    """P(accumulator has crossed theta by the clip's effective deadline), per theta."""
    p = paths[crit]
    T_eff = t_end - lam
    m = p["t"] <= T_eff
    if not m.any():                       # deadline precedes the clip: no evidence yet
        return torch.zeros_like(theta)
    E = torch.as_tensor(p["E"][m])
    W = torch.as_tensor(p["W"][:, m])
    A = torch.exp(log_k) * E[None, :] + W
    M = A.max(dim=1).values                              # running max = max over path
    return torch.sigmoid((M[:, None] - theta[None, :]) / SMOOTH).mean(dim=0)


def surface(paths, phi, sigma_pop, lam, cells):
    """Predicted P(intervene) for each cell, integrating the threshold spread out.

    The log-threshold spread combines the pinned between-driver sigma_pop with the
    free trial-level sigma_trial (v3): at cell level the two are indistinguishable,
    so one quadrature over their quadrature-sum covers both.
    """
    log_k, mu_a, logit_b, log_st = phi[0], phi[1], phi[2], phi[3]
    b = torch.sigmoid(logit_b)
    s_eff = torch.sqrt(torch.as_tensor(sigma_pop) ** 2 + torch.exp(log_st) ** 2)
    zz, ww = _gh_nodes(N_GH)
    theta = torch.exp(mu_a + s_eff * torch.as_tensor(zz))
    wt = torch.as_tensor(ww)
    preds = []
    for crit, tp, _, _ in cells:
        pc = cell_cross_prob(paths, log_k, theta, crit, TIMEPOINT_OFFSET_S[tp], lam)
        preds.append(((b + (1 - b) * pc) * wt).sum())
    return torch.stack(preds)


def neg_loglik(paths, phi, sigma_pop, lam, cells) -> torch.Tensor:
    p = surface(paths, phi, sigma_pop, lam, cells).clamp(1e-9, 1 - 1e-9)
    k = torch.as_tensor([c[2] for c in cells])           # successes
    n = torch.as_tensor([c[3] for c in cells])           # trials
    return -(k * torch.log(p) + (n - k) * torch.log1p(-p)).sum()


def fit(paths, cells, sigma_pop: float, lam: float, seed: int = 0) -> torch.Tensor:
    # Start grid widened at v3: the v2 optimum sat in the low-gain (noise-dominated)
    # regime, and with sigma_trial free the high-gain regime is viable, so both are
    # seeded. sigma_trial starts at log(0.18) -- stage 1's sigma_resp (~970) over the
    # median level (~5352) on the log scale, the natural magnitude for the response
    # variability the term restores.
    best = None
    for k0 in (-9.0, -8.0, -7.0, -6.0, -5.0):
        phi = torch.tensor([k0, 1.0, np.log(0.09 / 0.91), float(np.log(0.18))],
                           requires_grad=True)
        opt = torch.optim.LBFGS([phi], max_iter=200, tolerance_grad=1e-10,
                                tolerance_change=1e-14, history_size=40,
                                line_search_fn="strong_wolfe")

        def closure():
            opt.zero_grad()
            loss = neg_loglik(paths, phi, sigma_pop, lam, cells)
            loss.backward()
            return loss

        opt.step(closure)
        with torch.no_grad():
            v = float(neg_loglik(paths, phi, sigma_pop, lam, cells))
        if np.isfinite(v) and (best is None or v < best[0]):
            best = (v, phi.detach().clone())
    return best[1]


def build_cells(r):
    out = []
    for (crit, tp), g in r.groupby(["criticality", "timepoint"]):
        out.append((crit, tp, float(g.intervene.sum()), float(len(g))))
    return out


def static_baseline(r, x, pid, folds_by_crit):
    """Leave-one-criticality-out RMSE of the stage-1 static threshold, same folds."""
    from scipy.stats import norm
    pr = priors_for(x)
    y = r.intervene.to_numpy(float)
    zz, ww = _gh_nodes(N_GH)
    preds, obs = [], []
    for held in CRITS:
        tr = (r.criticality != held).to_numpy()
        pid_tr = np.unique(pid[tr], return_inverse=True)[1]
        f = fit_marginal(x[tr], y[tr], pid_tr, pr)
        c = np.exp(f["mu"] + f["sigma_pop"] * zz)
        for tp in TIMEPOINT_OFFSET_S:
            m = ((r.criticality == held) & (r.timepoint == tp)).to_numpy()
            if not m.any():
                continue
            p = f["b"] + (1 - f["b"]) * norm.cdf((float(x[m][0]) - c) / f["sigma_resp"])
            preds.append(float((p * ww).sum()))
            obs.append(float(y[m].mean()))
    return float(np.sqrt(np.mean((np.array(preds) - np.array(obs)) ** 2)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ungated-noise", action="store_true",
                    help="reproduce the v1 model: noise accumulates from clip start")
    ap.add_argument("--scan", action="store_true",
                    help="grid-scan the v2 (no sigma_trial) likelihood landscape and "
                         "exit -- the R.1 check that v2's noise-dominated optimum was "
                         "global, not an optimizer failure")
    args = ap.parse_args()
    t0 = time.time()

    if args.scan:
        r = random_cutin_trials()
        cells = build_cells(r)
        paths = evidence_paths(args.seed, ungated=args.ungated_noise)
        print("v2 landscape (sigma_trial pinned tiny), nll by (log_k, mu_a, b):")
        rows = []
        for logk in np.arange(-11.0, -3.5, 0.75):
            for mua in np.arange(-2.0, 4.5, 0.75):
                for lb in (np.log(0.05 / 0.95), np.log(0.10 / 0.90)):
                    phi = torch.tensor([logk, mua, lb, -20.0])   # sigma_trial ~ 0: v2
                    with torch.no_grad():
                        v = float(neg_loglik(paths, phi, 0.209, LAMBDA_S, cells))
                    rows.append((logk, mua, lb, v))
        for logk, mua, lb, v in sorted(rows, key=lambda t: t[3])[:8]:
            print(f"  log_k {logk:6.2f}  mu_a {mua:5.2f}  b {1/(1+np.exp(-lb)):.3f}"
                  f"  -> nll {v:.1f}")
        phi_fit = torch.tensor([np.log(0.000124), -0.431, np.log(0.13 / 0.87), -20.0])
        with torch.no_grad():
            v_fit = float(neg_loglik(paths, phi_fit, 0.209, LAMBDA_S, cells))
        print(f"  v2 fitted solution                      -> nll {v_fit:.1f}")
        return

    r = random_cutin_trials()
    pid = r.participant.factorize()[0].astype(int)
    x = r.deficit_max.to_numpy(float)
    y = r.intervene.to_numpy(float)
    cells = build_cells(r)
    paths = evidence_paths(args.seed, ungated=args.ungated_noise)

    print("refitting stage 1 (hierarchical lapse, per the R.1 decision) for sigma_pop "
          "...", flush=True)
    s1 = fit_hier_lapse(x, y, pid, priors_for(x))
    sigma_pop = float(s1["sigma_pop"])
    print(f"  sigma_pop = {sigma_pop:.3f} (fixed from here on)", flush=True)

    # ---- in-sample fit and held-out folds, at the nominal latency ----
    print("fitting the accumulator ...", flush=True)
    phi = fit(paths, cells, sigma_pop, LAMBDA_S)
    with torch.no_grad():
        pred_in = surface(paths, phi, sigma_pop, LAMBDA_S, cells).numpy()
    obs = np.array([c[2] / c[3] for c in cells])
    rmse_in = float(np.sqrt(np.mean((pred_in - obs) ** 2)))
    corr_in = float(np.corrcoef(pred_in, obs)[0, 1])

    print("leave-one-criticality-out folds ...", flush=True)
    preds_ho, obs_ho = [], []
    for held in CRITS:
        tr = [c for c in cells if c[0] != held]
        te = [c for c in cells if c[0] == held]
        ph = fit(paths, tr, sigma_pop, LAMBDA_S)
        with torch.no_grad():
            preds_ho += list(surface(paths, ph, sigma_pop, LAMBDA_S, te).numpy())
        obs_ho += [c[2] / c[3] for c in te]
    preds_ho, obs_ho = np.array(preds_ho), np.array(obs_ho)
    rmse_ho = float(np.sqrt(np.mean((preds_ho - obs_ho) ** 2)))
    corr_ho = float(np.corrcoef(preds_ho, obs_ho)[0, 1])

    base_ho = static_baseline(r, x, pid, CRITS)

    # ---- latency sensitivity ----
    sens = {}
    for lam in LAMBDA_SENSITIVITY:
        ph = fit(paths, cells, sigma_pop, lam)
        with torch.no_grad():
            pr_ = surface(paths, ph, sigma_pop, lam, cells).numpy()
        sens[lam] = (float(np.sqrt(np.mean((pr_ - obs) ** 2))),
                     float(np.exp(ph[0])), float(ph[1]), float(np.exp(ph[3])))

    # ---- degeneracy diagnostic ----
    log_k, mu_a = float(phi[0]), float(phi[1])
    crit_ref = "TTC6"
    p_ref = paths[crit_ref]
    m = p_ref["t"] <= (1.5 - LAMBDA_S)
    drift = np.exp(log_k) * p_ref["E"][m][-1]
    noise_sd = float(np.sqrt(max(p_ref["tau"][m][-1], 1e-9)))
    verdict = ("PASS" if rmse_ho <= 0.11 else
               "FAIL" if rmse_ho > 0.13 else "INCONCLUSIVE")

    variant_txt = ("from clip start (`--ungated-noise`)" if args.ungated_noise
                   else "from manoeuvre onset (noise gated at onset, per the R.1 "
                        "decision on query A.3.Q1)")
    L = [f"# Card A.3{'' if args.ungated_noise else ' (v3)'} — the accumulator layer\n",
         "Evidence is the per-frame deficit series; a linear accumulator with Brownian "
         f"noise integrates it {variant_txt}, and the response is the first crossing of "
         "the driver's threshold before the clip's deadline less the motor latency. The "
         "between-driver spread is fixed at card A.2's value on the hierarchical-lapse "
         "variant (the R.1 decision on query A.2.Q2) and not refitted, so the "
         "accumulator cannot absorb it; a trial-level threshold spread sigma_trial is "
         "free (v3) -- the accumulator analogue of stage 1's response sd sigma_resp, "
         "combined with the pinned between-driver part in quadrature. The noise scale "
         "is pinned at 1 for identification. Free: gain, threshold location, lapse, "
         "sigma_trial.\n",
         "## Fit\n",
         "| | RMSE on the 18-cell surface | correlation |", "|---|---|---|",
         f"| accumulator, in sample | {rmse_in:.3f} | {corr_in:.3f} |",
         f"| accumulator, leave-one-criticality-out | **{rmse_ho:.3f}** | {corr_ho:.3f} |",
         f"| stage-1 static threshold, same folds | {base_ho:.3f} | — |",
         "\n## Pre-registered decision rule\n",
         f"Held-out RMSE **{rmse_ho:.3f}** against the rule fixed before fitting "
         f"(<= 0.11 closes the gap; > 0.13 is failure): **{verdict}**.\n",
         "For context on the same held-out scheme: the one-scalar static field reaches "
         "0.147, Jonas's two-dimensional state rule 0.120, and the scenario-specific "
         "design regression about 0.10 — the last being an upper-bound reference rather "
         "than a portable model.\n",
         "## Motor-latency sensitivity\n",
         "| lambda [s] | in-sample RMSE | gain k | threshold location mu_a | sigma_trial |",
         "|---|---|---|---|---|",
         f"| 0.15 | {sens[0.15][0]:.3f} | {sens[0.15][1]:.3g} | {sens[0.15][2]:.3f} "
         f"| {sens[0.15][3]:.3f} |",
         f"| **0.25 (nominal)** | {rmse_in:.3f} | {np.exp(log_k):.3g} | {mu_a:.3f} "
         f"| {float(np.exp(phi[3])):.3f} |",
         f"| 0.35 | {sens[0.35][0]:.3f} | {sens[0.35][1]:.3g} | {sens[0.35][2]:.3f} "
         f"| {sens[0.35][3]:.3f} |",
         "\n## Degeneracy check\n",
         f"At {crit_ref}'s latest deadline the accumulated drift is {drift:.2f} against a "
         f"noise sd of {noise_sd:.2f}, a ratio of {drift / noise_sd:.2f}. The card's stop "
         "condition is a gain so large that the accumulator collapses to a deterministic "
         "threshold; " +
         ("that has not happened — noise remains a material part of the crossing "
          "probability, so the model is genuinely stochastic."
          if drift / noise_sd < 10 else
          "**it has happened**: the drift dominates the noise by more than an order of "
          "magnitude, so crossing is effectively deterministic and the fitted noise is "
          "doing no work. Reported rather than tuned away."),
         "\n## Per-cell fit, and a specification problem this exposes\n",
         "| criticality | " + " | ".join(f"C{i}" for i in range(1, 7)) + " |",
         "|---" * 7 + "|"]
    for crit in CRITS:
        obs_row, pred_row = [], []
        for tp in TIMEPOINT_OFFSET_S:
            idx = [i for i, c in enumerate(cells) if c[0] == crit and c[1] == tp]
            if idx:
                obs_row.append(obs[idx[0]])
                pred_row.append(pred_in[idx[0]])
        L.append(f"| {crit} obs / pred | " + " | ".join(
            f"{o:.2f} / {p:.2f}" for o, p in zip(obs_row, pred_row)) + " |")

    t_pre = float(-paths["TTC6"]["t"][0])
    static_note = (
        f"\n**Specification check**: the in-sample RMSE ({rmse_in:.3f}) against the "
        "stage-0 static two-parameter probit's 0.125 on the same cells. An accumulator "
        "that fits worse in sample than the simpler model it extends is misspecified, "
        "not refuted. Two such misspecifications were found and repaired at review "
        "gate R.1, each argued from structure before refitting: v1 integrated noise "
        f"through the {t_pre:.1f} s pre-onset window, a property of stimulus "
        "presentation rather than of drivers (in-sample 0.182; worklog query A.3.Q1); "
        "v2 gated the noise at onset but carried no counterpart to stage 1's "
        "within-driver response variability, so its maximum-likelihood solution "
        "abandoned the evidence (gain 1.2e-4, drift-to-noise 0.73, a "
        "criticality-flat surface; shown to be the global optimum by `--scan`, log in "
        "`out/log_stage2_v2.txt`). v3 adds that missing variability as sigma_trial "
        "and is the final iteration at this gate: its verdict stands as recorded, "
        "whichever way it falls. The reserve remedy, a leaky accumulator, remains "
        "unexercised: it bounds pre-onset noise the way the onset gate does, but also "
        "discounts early post-onset evidence -- altering the time-integration claim "
        "under test -- and costs a free parameter.\n")
    L += [static_note, f"Runtime {(time.time() - t0) / 60:.1f} min."]

    txt = "\n".join(L) + "\n"
    (OUT / "stage2_summary.md").write_text(txt, encoding="utf-8")
    print("\n" + txt)


if __name__ == "__main__":
    main()
