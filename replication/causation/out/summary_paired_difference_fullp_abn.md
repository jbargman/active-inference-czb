# theta_C - theta_B, metric p_inj, N = 5, 1000 draws

Point estimate 0.061 (theta_B 0.148, theta_C 0.209).

| scheme | mean | 95% HDI | P(theta_C > theta_B) |
|---|---|---|---|
| ref-only | 0.071 | [0.039, 0.110] | 0.998 |
| population | 0.055 | [-0.006, 0.110] | 0.970 |
| cases | 0.068 | [0.001, 0.147] | 0.972 |

The ref-only scheme reproduces the numbers quoted in the results doc before 2026-08-27; it omits the synthetic-side variance and overstates the certainty of the ordering. The population scheme is the project's convention.
