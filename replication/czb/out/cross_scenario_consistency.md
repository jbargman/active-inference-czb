# Is the boundary level a stable per-driver trait across scenarios?

43 participants seen in all four Random scenarios. Per driver and scenario: mean residual intervention propensity after removing each design cell's mean, so scenarios of different difficulty are comparable. No field is used anywhere in this script -- the test is deliberately independent of every field construction.

## Per-scenario reliability (the ceiling any correlation is read against)

| scenario | trials | design cells | split-half reliability |
|---|---|---|---|
| cut-in | 3096 | 18 | 0.973 |
| cyclist | 2580 | 15 | 0.962 |
| LTAP | 3096 | 18 | 0.981 |
| truck | 860 | 5 | 0.929 |

## Cross-scenario correlation of per-driver propensity

Observed Pearson r below the diagonal; the reliability ceiling sqrt(rel_a x rel_b) above it.

| | cut-in | cyclist | LTAP | truck |
|---|---|---|---|---|
| cut-in | — | *0.968* | *0.977* | *0.951* |
| cyclist | +0.698 | — | *0.971* | *0.945* |
| LTAP | +0.714 | +0.645 | — | *0.955* |
| truck | +0.710 | +0.737 | +0.504 | — |

## Shared fraction of the reliable signal

Observed correlation divided by the reliability ceiling — how much of the per-driver signal that *could* be shared actually is.

| pair | observed r | ceiling | ratio |
|---|---|---|---|
| cut-in vs cyclist | +0.698 | 0.968 | +0.72 |
| cut-in vs LTAP | +0.714 | 0.977 | +0.73 |
| cut-in vs truck | +0.710 | 0.951 | +0.75 |
| cyclist vs LTAP | +0.645 | 0.971 | +0.66 |
| cyclist vs truck | +0.737 | 0.945 | +0.78 |
| LTAP vs truck | +0.504 | 0.955 | +0.53 |

Mean ratio across the six pairs: **+0.69**.

## How to read this

A ratio near 1 would mean per-driver position is essentially the same trait in every scenario — the strongest possible non-field evidence for the one-scalar claim. A ratio near 0 would mean the scenarios rank drivers independently, in which case no field construction can make a single fitted level transfer, and the elliptical per-scenario fallback is the honest route. Intermediate values say a common trait exists but does not exhaust the per-driver variation, which would put an upper bound on how well any one-scalar transfer test can possibly do — a bound worth knowing before B.4 is scored.

