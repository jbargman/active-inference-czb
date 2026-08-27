# Card A.3 — the accumulator layer

Evidence is the per-frame deficit series; a linear accumulator with Brownian noise integrates it from clip start, and the response is the first crossing of the driver's threshold before the clip's deadline less the motor latency. The between-driver spread is fixed at card A.2's value and not refitted, so the accumulator cannot absorb it; the noise scale is pinned at 1 for identification. Free: gain, threshold location, lapse.

## Fit

| | RMSE on the 18-cell surface | correlation |
|---|---|---|
| accumulator, in sample | 0.182 | 0.775 |
| accumulator, leave-one-criticality-out | **0.236** | 0.603 |
| stage-1 static threshold, same folds | 0.161 | — |

## Pre-registered decision rule

Held-out RMSE **0.236** against the rule fixed before fitting (<= 0.11 closes the gap; > 0.13 is failure): **FAIL**.

For context on the same held-out scheme: the one-scalar static field reaches 0.147, Jonas's two-dimensional state rule 0.120, and the scenario-specific design regression about 0.10 — the last being an upper-bound reference rather than a portable model.

## Motor-latency sensitivity

| lambda [s] | in-sample RMSE | gain k | threshold location mu_a |
|---|---|---|---|
| 0.15 | 0.172 | 0.00143 | 1.703 |
| **0.25 (nominal)** | 0.182 | 0.00148 | 1.631 |
| 0.35 | 0.191 | 0.00155 | 1.564 |

## Degeneracy check

At TTC6's latest deadline the accumulated drift is 9.57 against a noise sd of 1.10, a ratio of 8.73. The card's stop condition is a gain so large that the accumulator collapses to a deterministic threshold; that has not happened — noise remains a material part of the crossing probability, so the model is genuinely stochastic.

## Per-cell fit, and a specification problem this exposes

| criticality | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| TTC4 obs / pred | 0.12 / 0.19 | 0.30 / 0.19 | 0.73 / 0.23 | 0.77 / 0.43 | 0.87 / 0.68 | 0.92 / 0.87 |
| TTC6 obs / pred | 0.07 / 0.19 | 0.09 / 0.19 | 0.31 / 0.27 | 0.45 / 0.45 | 0.51 / 0.65 | 0.80 / 0.83 |
| TTC8 obs / pred | 0.05 / 0.19 | 0.07 / 0.20 | 0.22 / 0.24 | 0.27 / 0.35 | 0.37 / 0.49 | 0.37 / 0.64 |

**The in-sample RMSE (0.182) is itself worse than the stage-0 static two-parameter probit's 0.125 on the same cells.** An accumulator that fits worse in sample than the simpler model it is meant to extend indicates a misspecification, not a refuted mechanism, and the pre-registered verdict above should not be read as evidence against the framework until that is resolved.

The specific suspect, found while writing this card rather than by the fit: the clips begin 15.1 s before the lane change, and through that window the deficit is essentially zero while the Wiener noise keeps accumulating. The running maximum of that noise alone has a standard deviation of about 3.9, comparable to the entire post-onset drift, so the threshold is forced upward simply to avoid predicting pre-onset responses and every post-onset prediction is distorted by it. Two symptoms are visible above: the fitted lapse collapses toward zero where the observed pre-onset rate is 0.081, and the predicted surface is too flat across criticality. The length of that pre-onset window is a property of how the stimulus was presented, not of the driver, so a model whose fit depends on it is wrong in a way that matters. The standard remedies -- a leaky accumulator, or starting accumulation where there is evidence to accumulate -- are model-design decisions rather than parameter choices, so they are referred rather than made here.

Runtime 8.4 min.
