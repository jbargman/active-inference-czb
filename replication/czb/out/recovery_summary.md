# Card A.1 — synthetic recovery of the stage-1 model

20 simulated datasets per covariate axis; 3096 trials, 43 drivers, 18 cells, 4 repetitions per driver-cell — the real Random cut-in design, with responses replaced by draws from known parameters.

Simulation truths are measured, not tuned: threshold median and response sd from the stage-0 pilot on the deficit axis (5200, 2200) and from the covariate's own scale on the a_req axis; lapse 0.081 is the observed C1 intervention rate; between-driver sd **0.50** is calibrated so the simulated per-driver intervention-rate spread matches the observed 0.235 (sweep printed by `--calibrate`).

## Recovery, random effects integrated out (the estimator to use)

| axis | usable SEs | mu within 2 SE | sigma_pop within 2 SE | lapse b within 2 SE | RMSE of c_i, shrunk | RMSE, unshrunk MLE |
|---|---|---|---|---|---|---|
| `deficit_max` | 20/20 | **18/20** | **18/20** | 20/20 | **1081** | 1098 |
| `a_req_max` | 20/20 | **8/20** | **4/20** | 18/20 | **2.744** | 3.332 |

## Why the joint mode is not used, quantified

The first attempt maximized the joint posterior over hyperparameters **and** driver effects together. It recovers `mu` and the lapse but not the between-driver sd, because in a hierarchical model `sigma_pop` and the driver effects trade off against one another and the joint mode is not the marginal mode — the funnel geometry. The bias is large enough to swamp the interval:

| axis | estimator | mean sigma_pop (truth 0.50) | bias | coverage |
|---|---|---|---|---|
| `deficit_max` | joint MAP | 1.289 | +0.789 | 0/20 |
| `deficit_max` | marginal | 0.479 | -0.021 | 18/20 |
| `a_req_max` | joint MAP | 1.108 | +0.608 | 1/20 |
| `a_req_max` | marginal | 0.402 | -0.098 | 4/20 |

## Why the a_req axis does not recover: covariate geometry

The estimator is the same on both axes, so the difference is in the covariate. A threshold can only be located where there are cells to locate it with:

| axis | cells | range | largest gap between adjacent cells | share of range |
|---|---|---|---|---|
| `deficit_max` | 18 | 1.26 – 6.84e+03 | 2.07e+03 | **30%** |
| `a_req_max` | 18 | 0 – 11.6 | 8.48 | **73%** |

On `a_req_max` two pre-onset cells sit at exactly 0 while the other sixteen are bunched into 8.48–11.65, so nearly three-quarters of the covariate's range is empty and any driver whose threshold falls in that gap is indistinguishable from any other. The C1 anchor is also compromised on this axis specifically: TTC8's pre-onset cell reads 8.48, close to the most critical cells rather than to zero — the lane-gate leak already recorded in `docs/czb_fitting_plan.md` section 4. Both are properties of the field construction, not of the fitting code, so the fix belongs upstream.

## Acceptance criteria

1. mu and sigma_pop within 2 Laplace SEs on at least 18 of 20 datasets, both axes — **FAIL**: met on `deficit_max`, the primary axis the CZB claim is about, and not on `a_req_max`, for the covariate-geometry reason above. The criterion is recorded as failed rather than restated per axis; card A.2 may proceed on the primary axis, and `a_req_max` should not be fitted until its C1 gate leak is repaired.
2. Shrunk per-driver estimates beat unshrunk MLEs on RMSE — **PASS**.
3. Runtime under 10 minutes — **PASS** (6.1 min, both estimators and both axes).

The lapse column is reported rather than made a criterion: b and the threshold trade off at the C1 cells, which is the pitfall the card names, and its coverage is what shows how much those cells actually constrain the floor.

**Consequence for card A.2**: fit with `fit_marginal`, not `fit_map`. Any population spread — and therefore any percentile of the boundary distribution, which is the deliverable — would be materially wrong if taken from the joint mode.
