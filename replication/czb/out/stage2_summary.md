# Card A.3 (v3) — the accumulator layer

Evidence is the per-frame deficit series; a linear accumulator with Brownian noise integrates it from manoeuvre onset (noise gated at onset, per the R.1 decision on query A.3.Q1), and the response is the first crossing of the driver's threshold before the clip's deadline less the motor latency. The between-driver spread is fixed at card A.2's value on the hierarchical-lapse variant (the R.1 decision on query A.2.Q2) and not refitted, so the accumulator cannot absorb it; a trial-level threshold spread sigma_trial is free (v3) -- the accumulator analogue of stage 1's response sd sigma_resp, combined with the pinned between-driver part in quadrature. The noise scale is pinned at 1 for identification. Free: gain, threshold location, lapse, sigma_trial.

## Fit

| | RMSE on the 18-cell surface | correlation |
|---|---|---|
| accumulator, in sample | 0.169 | 0.820 |
| accumulator, leave-one-criticality-out | **0.255** | 0.541 |
| stage-1 static threshold, same folds | 0.169 | — |

## Pre-registered decision rule

Held-out RMSE **0.255** against the rule fixed before fitting (<= 0.11 closes the gap; > 0.13 is failure): **FAIL**.

For context on the same held-out scheme: the one-scalar static field reaches 0.147, Jonas's two-dimensional state rule 0.120, and the scenario-specific design regression about 0.10 — the last being an upper-bound reference rather than a portable model.

## Motor-latency sensitivity

| lambda [s] | in-sample RMSE | gain k | threshold location mu_a | sigma_trial |
|---|---|---|---|---|
| 0.15 | 0.169 | 0.000657 | 0.921 | 0.883 |
| **0.25 (nominal)** | 0.169 | 0.724 | 8.003 | 1.198 |
| 0.35 | 0.187 | 0.000355 | -0.034 | 1.357 |

## Degeneracy check

At TTC6's latest deadline the accumulated drift is 4638.46 against a noise sd of 1.10, a ratio of 4230.79. The card's stop condition is a gain so large that the accumulator collapses to a deterministic threshold; **it has happened**: the drift dominates the noise by more than an order of magnitude, so crossing is effectively deterministic and the fitted noise is doing no work. Reported rather than tuned away.

## Per-cell fit, and a specification problem this exposes

| criticality | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| TTC4 obs / pred | 0.12 / 0.15 | 0.30 / 0.15 | 0.73 / 0.28 | 0.77 / 0.49 | 0.87 / 0.66 | 0.92 / 0.74 |
| TTC6 obs / pred | 0.07 / 0.15 | 0.09 / 0.16 | 0.31 / 0.34 | 0.45 / 0.49 | 0.51 / 0.58 | 0.80 / 0.66 |
| TTC8 obs / pred | 0.05 / 0.15 | 0.07 / 0.17 | 0.22 / 0.28 | 0.27 / 0.41 | 0.37 / 0.49 | 0.37 / 0.58 |

**Specification check**: the in-sample RMSE (0.169) against the stage-0 static two-parameter probit's 0.125 on the same cells. An accumulator that fits worse in sample than the simpler model it extends is misspecified, not refuted. Two such misspecifications were found and repaired at review gate R.1, each argued from structure before refitting: v1 integrated noise through the 15.1 s pre-onset window, a property of stimulus presentation rather than of drivers (in-sample 0.182; worklog query A.3.Q1); v2 gated the noise at onset but carried no counterpart to stage 1's within-driver response variability, so its maximum-likelihood solution abandoned the evidence (gain 1.2e-4, drift-to-noise 0.73, a criticality-flat surface; the fitted solution beats every point of a coarse grid over gain, threshold and lapse, so it is the optimizer finding a genuine optimum rather than failing -- `--scan`, log in `out/log_stage2_scan.txt`). v3 adds that missing variability as sigma_trial and is the final iteration at this gate: its verdict stands as recorded, whichever way it falls. The reserve remedy, a leaky accumulator, remains unexercised: it bounds pre-onset noise the way the onset gate does, but also discounts early post-onset evidence -- altering the time-integration claim under test -- and costs a free parameter.

Runtime 14.0 min.
