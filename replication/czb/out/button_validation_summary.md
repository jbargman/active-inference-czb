# Card A.4 — Button press times predicted from the Random fit

Every accumulator parameter is carried over from the Random design unchanged (gain 0.00148, threshold location 1.631, between-driver spread 0.341, lapse 0.000). The only free quantity is a single paradigm shift, fitted twice: acting on the threshold, and acting on the gain.

## Which shift fits

| shift acts on | fitted value | RMSE against the observed press-time CDF |
|---|---|---|
| level | -0.250 | 0.148 **(better)** |
| gain | +0.133 | 0.169 |

The two are distinguished by the *shape* of the press-time distribution, not only its location: a threshold shift moves the whole curve, a gain shift also changes how fast it rises. On this data the **level** shift fits better.

## Predicted against observed at the fixed-clip checkpoints

| criticality | 0.3 s | 0.6 s | 0.9 s | 1.2 s | 1.5 s |
|---|---|---|---|---|---|
| TTC4 obs / pred | 0.36 / 0.29 | 0.65 / 0.35 | 0.77 / 0.57 | 0.88 / 0.80 | 0.94 / 0.94 |
| TTC6 obs / pred | 0.31 / 0.29 | 0.44 / 0.36 | 0.57 / 0.54 | 0.64 / 0.74 | 0.74 / 0.89 |
| TTC8 obs / pred | 0.18 / 0.29 | 0.27 / 0.34 | 0.36 / 0.45 | 0.40 / 0.59 | 0.44 / 0.73 |

Largest absolute discrepancy at any checkpoint: **0.297**.

## Acceptance criterion

The documented cross-paradigm excess is reproduced within 0.05 at the fixed-clip checkpoints — **FAIL** (worst 0.297).

![Predicted and observed press-time distributions](../../figures/button_validation.png)

Runtime 3.2 min.
