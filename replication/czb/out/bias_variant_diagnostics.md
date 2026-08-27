# Card R.1 — bias-variant diagnostics (the A.2.Q2 decision)

Three questions, each with its reading stated in the script docstring before the numbers were seen. All fits use card A.1/A.2's estimator and priors unchanged; the no-C1 refits reuse the full-data priors so the comparison isolates the change in data.

## 1 Per-driver pre-onset heterogeneity against a shared rate

Pooled C1 rate 0.081. Observed sd of per-driver C1 rates **0.204** against a shared-rate binomial's 0.078 (95th percentile 0.095); Monte Carlo p = 0.0000 (4000 replicates, seed 0).

## 2 Leakage signatures

| quantity | value |
|---|---|
| Spearman rho, per-driver C1 rate vs fitted c_i (group variant) | -0.622 |
| Spearman rho, per-driver C1 rate vs fitted c_i (hier variant) | -0.444 |
| Spearman rho, fitted b_i vs fitted c_i (hier variant) | -0.700 |
| Spearman rho, per-driver C1 rate vs post-onset rate | +0.619 |

Under leakage, the group variant's thresholds should track pre-onset behavior (negative rho: pressing early at C1 pulls the fitted threshold down); the hierarchical variant gives that behavior somewhere else to go.

## 3 The C1 predictive under both variants, integrated properly

The stage-1 report's C1 table used the hierarchical variant's *median* lapse (0.017); the population-averaged predictive integrates the lapse distribution, whose mean is **0.107** against an observed pooled pre-onset rate of 0.081.

| criticality | observed | group predicts | hier predicts |
|---|---|---|---|
| TTC4 | 0.122 | 0.030 | 0.107 |
| TTC6 | 0.070 | 0.068 | 0.113 |
| TTC8 | 0.052 | 0.115 | 0.129 |

## 4 Where the spread lives: refits without the C1 cells

| fit | sigma_pop, full data | sigma_pop, C1 excluded |
|---|---|---|
| group lapse | 0.341 | 0.281 |
| hierarchical lapse | 0.209 | 0.104 |

## 5 What the choice does to the deliverable

| percentile | group variant | hierarchical variant |
|---|---|---|
| 50th | 5043 [4630, 5455] | 5352 [5143, 5560] |
| 80th | 6717 [6201, 7234] | 6379 [6128, 6630] |
| 95th | 8832 [7662, 10002] | 7543 [7066, 8020] |

Runtime 8.6 min.
