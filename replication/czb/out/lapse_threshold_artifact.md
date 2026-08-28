# Is the lapse-threshold correlation real? (query R.1.Q2)

The fitted per-driver lapse and boundary level correlate at Spearman **-0.727** on the real data, while the model treats them as independent. This asks whether that is a trait correlation or an artifact of estimating two quantities that trade off against each other from the same limited per-driver data. Simulations use the parameters fitted on the real data, so each simulated driver carries the same amount of information as a real one; 12 replicates per arm.

| truth | recovered rho, mean | sd | min | max |
|---|---|---|---|---|
| driver effects independent (rho = 0) | **-0.272** | 0.155 | -0.610 | -0.125 |
| genuinely correlated (rho = -0.7) | -0.652 | 0.081 | -0.792 | -0.496 |
| *observed on the real data* | *-0.727* | - | - | - |

## Reading

**The estimator manufactures a substantial part of this on its own.** With the driver effects truly independent it still recovers -0.272 on average — 37% of the observed magnitude — because the two effects trade off: each driver's excess pressing has to be split between the lapse and the threshold, which forces the two estimation errors to have opposite signs. This is the same phenomenon as the classic negative correlation between a fitted intercept and slope. Any reading of the raw -0.727 that ignores this overstates the trait correlation.

**But it does not account for all of it.** The observed value sits 2.9 sd below the independent arm's mean and is more negative than 12 of the 12 independent replicates, while sitting 0.9 sd from the mean of the arm simulated with a genuine rho = -0.7 (-0.652) — comfortably inside it. The data are therefore consistent with a real correlation of roughly the size the naive estimate suggests, arrived at through a mixture of a real effect and an artifact worth about -0.272.

**Practical conclusion**: query R.1.Q2 stays open, the correlated-effects variant in card A.2.v2 is still needed, and its fitted correlation must be judged against the artifact baseline of -0.272 rather than against zero — a fit returning, say, -0.3 would be evidence of *no* real correlation, not of a moderate one.


## What follows either way

The practical question is not whether the correlation is real but whether the deliverable moves. If it is an artifact, the independence assumption is harmless and the percentile table stands as reported. If it is real, the correlated-effects fit in card A.2.v2 is the check, under the rule fixed at review gate R.1: escalate if the 80th percentile moves by more than the current CI half-width (~250 deficit units).

Runtime 9.7 min.
