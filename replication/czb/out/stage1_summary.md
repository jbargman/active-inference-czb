# Card A.2 — stage-1 hierarchical fit of the boundary level

3096 Random cut-in trials, 43 drivers, 18 cells. Driver effects integrated out by quadrature and Laplace applied to the hyperparameters only, per card A.1. Priors unchanged from A.1 so its recovery evidence carries over.

## The four fits

| axis | lapse | median level exp(mu) | sigma_pop | sigma_resp | lapse b | LOPO log-lik |
|---|---|---|---|---|---|---|
| `deficit_max` | group | 5043 (SE 210) | 0.341 | 1069 | 0.029 | -430.1 |
| `deficit_max` | hier | 5352 (SE 107) | 0.209 | 969.7 | 0.017 (sd 2.76) | -429.5 |
| `a_req_max` | group | 10.15 (SE 0.181) | 0.116 | 0.918 | 0.042 | -464.0 |
| `a_req_max` | hier | 10.29 (SE 0.129) | 0.089 | 0.9006 | 0.012 (sd 3.02) | -449.7 |

On the primary axis the hierarchical lapse is favoured by +0.6 log-likelihood units held out (hierarchical wins); on `a_req_max` the winner is hier. A difference of a few units over 3 096 trials is not a decisive separation, and is reported as such.

## Population percentiles of the boundary level (primary axis, hier lapse)

The deliverable. Deficit units, with delta-method 95% intervals, and the equivalent required deceleration and steady-following time headway at 20 m/s.

| percentile | level (deficit) | 95% CI | equivalent a_req [m/s²] | THW* at 20 m/s [s] |
|---|---|---|---|---|
| 50th | 5352 | [5143, 5560] | 10.34 | 0.33 |
| 55th | 5494 | [5291, 5696] | 10.41 | 0.33 |
| 60th | 5642 | [5442, 5842] | 10.48 | 0.32 |
| 65th | 5800 | [5598, 6001] | 10.56 | 0.31 |
| 70th | 5970 | [5761, 6180] | 10.66 | 0.30 |
| 75th | 6160 | [5935, 6385] | 10.77 | 0.29 |
| 80th | 6379 | [6128, 6630] | 11.00 | 0.27 |
| 85th | 6644 | [6352, 6935] | 11.36 | 0.25 |
| 90th | 6992 | [6636, 7348] | 11.89 | 0.21 |
| 95th | 7543 | [7066, 8020] | nan | nan |

## Comfort and dread levels, from the ordered braking expectation

| quantity | value | in a_req units | THW* at 20 m/s |
|---|---|---|---|
| comfort (expect ≥ gentle braking) | 3703 | 8.81 | 0.50 |
| dread (expect hard braking) | 6397 | 11.02 | 0.27 |

Separation delta = 2694 deficit units (SE 70); between-driver sd 0.241.

## Pre-onset (C1) posterior predictive — the lapse check

| criticality | observed P(intervene) | predicted | difference |
|---|---|---|---|
| TTC4 | 0.122 | 0.017 | -0.105 |
| TTC6 | 0.070 | 0.024 | -0.046 |
| TTC8 | 0.052 | 0.041 | -0.011 |

## Acceptance criteria

1. All four fits converge with usable standard errors — **PASS**.
2. The summary renders — **PASS** (this file).
3. LOPO distinguishes the bias variants, or states that it cannot — **PASS**: it separates them by +0.6 units on the primary axis, which is reported as weak rather than decisive.

Runtime 266.9 min.

**Carried forward**: the `a_req_max` rows are reported for completeness but should not be interpreted — card A.1 showed that axis cannot locate a threshold as currently constructed (73% of its range is an empty gap, and its pre-onset anchor leaks at TTC8).
