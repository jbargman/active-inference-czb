# The second cut-in study: what it adds

10944 trials, 144 participants; 7488 trials after dropping the CP1 baseline. Perceived safety, an intervention binary, and the same three-level expected-braking question as study 1. Participant-level means are formed first throughout, because the DV and CP subsets are between-subjects.

## 0 Why study 1 could not have answered this, and what that costs

Across all 18 cells of the study-1 Random cut-in design the relative speed is constant at 2.78 m/s, so time-to-collision is gap divided by a constant and **correlation(gap, TTC) = 1.0000**. Time headway and required deceleration are likewise fixed functions of the same one number. The longitudinal dimension of that design has a single degree of freedom.

The consequence is uncomfortable and worth stating plainly. Every longitudinal result obtained on study 1 — the stage-0 correlation of 0.90, the stage-1 boundary level, the population percentile — is equally consistent with a driver who thresholds the preference field and with a driver who thresholds **the gap**. Those fits are not wrong, and the boundary is well estimated on its own scale; but they cannot be used as evidence that the field's kinematic content is the right description, because no contrast in that design distinguishes it from the simplest possible alternative. The second cut-in study breaks the collinearity, which is why it can decide what study 1 cannot.

## 1 The test only this dataset can run

At matched time-to-collision, the delta-velocity factor moves the longitudinal gap by a factor of six. If the response were a function of time alone, each row below would be flat.

| TTC_true [s] | cells | lowest P(intervene) | highest | rho(distance, P) |
|---|---|---|---|---|
| 0.8 | 6 | 0.897 | 0.986 | -0.09 |
| 1.1 | 6 | 0.861 | 0.932 | -0.37 |
| 1.4 | 6 | 0.757 | 0.986 | -0.94 |
| 1.7 | 6 | 0.541 | 0.797 | -0.94 |
| 1.8 | 6 | 0.622 | 0.932 | -0.77 |
| 2.1 | 6 | 0.608 | 0.892 | -0.89 |
| 2.4 | 6 | 0.397 | 0.868 | -0.89 |
| 2.7 | 6 | 0.351 | 0.736 | -1.00 |
| 2.8 | 6 | 0.382 | 0.809 | -0.89 |
| 3.1 | 6 | 0.431 | 0.806 | -0.94 |
| 3.4 | 6 | 0.206 | 0.662 | -0.71 |
| 3.7 | 6 | 0.194 | 0.597 | -0.94 |
| 3.8 | 6 | 0.154 | 0.667 | -0.78 |
| 4.1 | 6 | 0.333 | 0.864 | -0.90 |
| 4.4 | 6 | 0.077 | 0.750 | -0.94 |
| 4.7 | 6 | 0.042 | 0.818 | -0.71 |
| 4.8 | 6 | 0.042 | 0.708 | -0.99 |
| 5.1 | 6 | 0.042 | 0.500 | -0.37 |
| 5.4 | 6 | 0.000 | 0.458 | -1.00 |
| 5.7 | 6 | 0.000 | 0.423 | -0.66 |
| 5.8 | 6 | 0.000 | 0.375 | -0.66 |
| 6.1 | 6 | 0.083 | 0.577 | -1.00 |
| 6.4 | 6 | 0.000 | 0.400 | -0.82 |
| 6.7 | 6 | 0.000 | 0.308 | -0.94 |

The rows are emphatically not flat, and 100% of them run negative: **at matched time-to-collision, a larger gap means less intervention**. Time alone does not determine the response.

## 2 Which single scalar orders the cells best

| predictor | Spearman rho against P(intervene) |
|---|---|
| time-to-collision | -0.807 |
| longitudinal gap | -0.887 |
| required deceleration `DV / (2 TTC)` | +0.238 |

**The required-deceleration row is the one to look at**, and it should be read carefully: at +0.238 its sign is the one a demand-based model wants (more braking required, more intervention), but its magnitude is negligible beside the gap's -0.887. The honest statement is not that drivers respond backwards to demand, but that **required deceleration barely orders these cells at all while gap orders them almost perfectly** — and gap edges out even time-to-collision. A field whose safety terms are built from required deceleration and inverse tau is therefore leaning on the weakest of the three scalars available here.

## 3 What it does not settle

Distance and delta velocity are perfectly confounded at matched TTC by construction (`distance = TTC x DV`), and the study's own documentation says so. This dataset can therefore show that a time measure is insufficient; it cannot say whether the missing ingredient is gap, closing speed, headway, or the perceptual uncertainty that scales with them. Separating those needs a design that breaks the product, or a model that predicts different signs for them.

## 4 A clean anticipation test, which study 1 cannot support

Every clip in block 1 is shown **twice** to the same participant. That is the exposure manipulation R.1.Q3 needs and study 1 lacks: identical stimulus, identical participant, second viewing.

| quantity | value |
|---|---|
| repeated clip-participant pairs | 3456 |
| P(intervene), first showing | 0.547 |
| P(intervene), second showing | 0.575 |
| **difference** | **+0.027** (SE 0.007) |

A reliable shift on the second showing of an identical clip is direct evidence that repeated exposure changes responding, which is what R.1.Q3 asserts.

## 5 `03_CAMP`, described only

19 files. Top level: `aggregate_trials.csv`, `aggregate_trials_clean.csv`, `camp_constdv_30_10_vehicle_states.csv`, `camp_constdv_30_20_vehicle_states.csv`, `camp_constdv_60_15_vehicle_states.csv`, `camp_constdv_60_30_vehicle_states.csv`, `camp_constdv_60_50_vehicle_states.csv`, `camp_crowdsourcing_context_v2.md`, and 11 more.

No use is proposed. Jonas flagged known problems with this dataset and nothing above depends on it.

