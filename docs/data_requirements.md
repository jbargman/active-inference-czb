# Data requirements for empirical estimation of comfort-zone boundaries

**Active inference approach to driver comfort-zone boundaries**

Chalmers University of Technology — WaymoActiveInference project

Version 1.0, 18 August 2026

---

## 1 Purpose and objectives

This document specifies exactly what data is needed to take the comfort-zone boundary method
described in `notes/04_comfort_zone_method.md` from a construction to an empirical result. It
is written so that it can be handed to a data owner, or used as a checklist when assessing
whether an existing dataset is usable.

The objectives the data must support are, in order:

**Primary objective.** Calibrate the comfort-zone boundary level *c* against observed driver
response onsets, and test whether a single *c*, fitted on one scenario type, predicts response
onsets in held-out scenario types. This is the claim that distinguishes the method from
conventional per-scenario indicator thresholds, and it is the reason more than one scenario
type is required.

**Secondary objective.** Estimate the preference-function parameters that determine whose
comfort zone is being described — desired speed, preferred inverse tau, assumed reaction time,
and the assumed worst-case deceleration of the conflict partner — rather than adopting the
values published by Schumann et al. (2026), which were tuned for their simulation study and
not for any particular driver population.

**Tertiary objective.** Test whether "extra motives" in the sense of Näätänen and Summala move
the boundary by the amount the method predicts. This requires either an experimental
manipulation of time pressure, or observational data in which a proxy for hurry is recorded.

The authors of this document have not found any published work that estimates a comfort-zone
boundary as a level set of a preference-derived scalar field, so there is no prior data
specification to inherit. The requirements below are derived from the computation itself.

## 2 What the computation actually needs

The comfort-zone field is

```
eps(t) = max_o log p(o) - log p(o(t))
```

where p(o) is the driver's preference function over observations. Evaluating this along a
recorded event requires only the observation vector at each time step. No model roll-out is
performed, no particle filter is run, and no GPU is required. The function that consumes the
data is `comfortzone.calibrate.deficit_along_trajectory`.

This matters for data procurement: the method needs *kinematics and geometry*, not driver
state, not video, and not any signal that is expensive to obtain or ethically sensitive.

## 3 Required signals

Sampling rate at least 10 Hz; 20 to 50 Hz preferred. All signals must share one time base.

### 3.1 Ego vehicle

| Signal | Symbol | Unit | Required | Used by | Notes |
|---|---|---|---|---|---|
| Time | t | s | yes | all | monotonic, uniform step preferred |
| Longitudinal position | x | m | yes | collision, safety | any fixed frame, see §4 |
| Lateral position | y | m | yes | lateral | signed offset from lane center is acceptable and often better |
| Heading | psi | rad | yes | collision severity | relative to lane direction |
| Speed | v | m/s | yes | speed, safety, tau | accuracy 0.1 m/s or better |
| Longitudinal acceleration | a_x | m/s^2 | yes | control effort, safety | measured or differentiated from v |
| Road-wheel steering angle | delta | rad | preferred | control effort | steering wheel angle plus ratio is acceptable |
| Steering rate | omega | 1/s | derived | control effort | differentiate delta if not recorded |
| Yaw rate | r | rad/s | fallback | control effort | only if no steering signal exists |

### 3.2 Conflict partner

| Signal | Symbol | Unit | Required | Used by | Notes |
|---|---|---|---|---|---|
| Longitudinal position | x_p | m | yes | collision, safety, tau | same frame as ego |
| Lateral position | y_p | m | yes | collision, lateral relevance | this is the signal most often missing or poor |
| Heading | psi_p | rad | yes | collision severity | cos(psi - psi_p) enters the severity factor |
| Speed | v_p | m/s | yes | safety, tau | |
| Acceleration | a_p | m/s^2 | yes | safety | may be differentiated from v_p, see §7.2 |
| Object class | — | — | yes | interpretation | car, truck, motorcycle, pedestrian, cyclist |

If more than one road user is present, supply all of them that are plausibly relevant; the
preference function takes a minimum over conflict partners.

### 3.3 Vehicle geometry

| Quantity | Unit | Required | Notes |
|---|---|---|---|
| Ego length, width | m | yes | enters the collision box and the 1.15 L term |
| Partner length, width | m | yes | default values by class are acceptable if unknown, but flag them |
| Position reference point | — | yes | front bumper center, rear axle center, or center of gravity — see §4.3 |

### 3.4 Road geometry

| Quantity | Unit | Required | Notes |
|---|---|---|---|
| Lane width | m | yes | the lateral preference is defined relative to it |
| Lateral offset of ego from lane center | m | yes | may be given directly instead of absolute y |
| Number of lanes, and travel direction of each | — | yes | same-direction and opposite-direction lanes are treated differently |
| Distance to road edge | m | preferred | needed for the off-road term |
| Curvature | 1/m | optional | not used in the current implementation |

### 3.5 Event annotations

| Quantity | Unit | Required | Notes |
|---|---|---|---|
| Brake response onset | s | yes for the primary objective | this is the label the boundary level is fitted to |
| Steering response onset | s | preferred | needed for scenarios avoided by steering |
| Conflict onset | s | yes | when the partner's behavior created the conflict |
| Event outcome | — | preferred | crash, near-crash, conflict, or normal |
| Scenario type | — | yes | required for the generalization test |

## 4 Coordinate frames, units, and sign conventions

Ambiguity here is the most common source of silent error, so the conventions are stated
explicitly.

### 4.1 Frame

A right-handed frame with **x forward along the lane** and **y to the left**. Heading is
positive counterclockwise. Either a fixed world frame or the ego frame is acceptable, provided
both road users are expressed in the same one.

### 4.2 Relative quantities

The implementation uses

```
dx = x_partner - x_ego        positive when the partner is ahead
dy = y_partner - y_ego        positive when the partner is to the left
```

If a dataset provides range and azimuth instead, converting is straightforward, but the
azimuth accuracy determines the quality of dy, which is often the limiting factor (§7.1).

### 4.3 Position reference point

State which point on the vehicle the coordinates refer to. The safety term contains a
1.15 (l_f + l_r) clearance allowance that assumes positions are vehicle *centers*. Supplying
front-bumper positions without saying so shifts every boundary by roughly half a vehicle
length, which is comparable to the effect being measured.

### 4.4 Units

SI throughout: meters, seconds, radians, m/s, m/s^2. If the source uses km/h, degrees, or
feet, convert once at ingest and record that the conversion happened.

## 5 Duration and coverage per event

Each event should include:

- **At least 5 s before conflict onset.** This baseline is used to estimate the driver's
  normal following behavior, which is how the desired speed and preferred inverse tau are
  estimated for the secondary objective. Without it, those parameters must be assumed.
- **At least 10 s after conflict onset**, or until the conflict resolves, whichever is
  shorter.
- **No gaps in the partner track** during the conflict. If dropouts occur, flag them per
  sample rather than interpolating silently.

## 6 File format

Two files per dataset: one time series file per event, and one metadata table covering all
events. Comma-separated text is sufficient; Parquet is preferable for large sets.

### 6.1 Time series file, one per event

File name `<event_id>.csv`. Column names exactly as below; extra columns are ignored.

```
t,ego_x,ego_y,ego_psi,ego_v,ego_ax,ego_delta,
oth_x,oth_y,oth_psi,oth_v,oth_ax,oth_class,valid
0.00,0.00,0.02,0.001,15.24,0.05,0.002,26.90,0.01,0.000,15.11,0.00,car,1
0.05,0.76,0.02,0.001,15.24,0.03,0.001,27.66,0.01,0.000,15.11,0.00,car,1
0.10,1.52,0.02,0.001,15.25,0.02,0.001,28.41,0.01,0.000,15.11,0.00,car,1
...
```

`valid` is 1 when the partner track is measured and 0 when it is interpolated or missing.

### 6.2 Metadata table, one row per event

```
event_id,dataset,scenario,driver_id,lane_width,n_lanes_same,n_lanes_opposite,
ego_len,ego_wid,oth_len,oth_wid,ref_point,
t_conflict_onset,t_brake_onset,t_steer_onset,outcome,notes
E0001,SIM_LTAPOD,ltap_od,D07,3.50,1,1,4.62,1.83,4.40,1.80,cog,
      6.20,7.85,NaN,near_crash,
E0002,NDS_REAR,rear_end,D07,3.65,2,0,4.62,1.83,4.90,1.90,front_bumper,
      12.40,13.55,NaN,conflict,radar lateral position poor
```

Use `NaN` for a response that did not occur. Do not use 0.

### 6.3 Optional per-driver table

If individual differences are of interest, a per-driver table with age, sex, annual mileage,
and any experimental condition assignment.

## 7 Data quality: the failure modes that matter

These are the problems that have the largest effect on the estimated boundary, in order.

### 7.1 Lateral position of the conflict partner

Radar-based naturalistic driving data typically has good range and range rate but poor lateral
position. The lateral preference term, the collision box, and the condition that restricts the
safety term to same-lane partners all depend on `dy`. If lateral accuracy is worse than
roughly 0.5 m, the same-lane and adjacent-lane cases cannot be separated reliably, and the
method degrades to a purely longitudinal analysis. That is still usable for the primary
objective in rear-end scenarios, but it rules out the cross-scenario generalization test.

### 7.2 Partner acceleration

The safety term uses `a_test = min(a_partner, a_OV_min)`, so a noisy `a_partner` propagates
directly into the boundary. Differentiating speed at 10 Hz with a low-pass filter is normally
adequate. Verify by checking that the differentiated acceleration during steady following is
centered on zero with a standard deviation below about 0.3 m/s^2. Report the filter used.

### 7.3 Time synchronization

Vehicle CAN signals and external perception are often logged by different systems. An offset
of 100 ms shifts the estimated response time by the same amount, which is a large fraction of
the effect being studied. Confirm synchronization, and state the residual uncertainty.

### 7.4 Response onset definition

Different datasets define onsets differently, and mixing definitions across scenario types
would confound the generalization test. Use one definition throughout. Two acceptable options:

1. **Piecewise-linear fit to the speed trace**, taking the instant at which the first constant
   segment turns into a falling one. This is the definition used by Markkula et al. and
   adopted by Schumann et al., so results are comparable with the published values.
2. **Threshold crossing**, typically -1 m/s^2 longitudinal acceleration for braking and 5
   degrees of steering wheel angle for steering.

Whichever is used, record it in the metadata and apply it identically to every scenario.

### 7.5 Missing lane geometry

Naturalistic data often lacks lane width and lane assignment. A constant nominal lane width
can be substituted, but then the lateral term becomes approximate and any boundary that
depends on lateral position should be treated as indicative rather than estimated.

## 8 Sample size

These are working estimates based on the shape of the fitting problem, not on a formal power
analysis; a power analysis should be run once pilot variance is known.

| Purpose | Events needed | Notes |
|---|---|---|
| Fit one boundary level *c* by onset matching | 30 to 50 per scenario type | the fit criterion is flat near its optimum, so precision improves slowly beyond this |
| Cross-scenario generalization test | at least 2 scenario types, preferably 3, with 30+ each | this is the primary objective |
| Distributional calibration without onset labels | 200+ events | uses an acceptance quantile instead of onsets |
| Individual differences in *c* | 10+ events per driver, 20+ drivers | |
| Extra-motive manipulation | 20+ events per condition per driver | within-subject design strongly preferred |

## 9 Candidate datasets

Suitability below refers to the primary objective unless stated otherwise. Access status
should be confirmed; the assessment here is based on published descriptions rather than on
inspection of the data.

| Dataset | Kinematics | Partner lateral | Lane geometry | Onset labels | Suitability |
|---|---|---|---|---|---|
| Chalmers LTAP/OD comfort-zone study | good | good | known | likely | **highest** — boundaries already quantified conventionally, so it directly tests whether the level set reproduces an existing result |
| Chalmers pedestrian-overtaking field test and UDRIVE analysis | good | good | known | may need re-extraction | **high** — a different geometry, which is what the generalization test requires |
| Driving simulator, new collection | perfect | perfect | perfect | perfect | **high** — the only route to the tertiary objective, since time pressure can be manipulated |
| SHRP2 naturalistic driving study | good | moderate to poor | partial | yes, for near-crashes | high for rear-end; the dataset underlying the deceleration comparison in Schumann et al. |
| UDRIVE | good | moderate | partial | partial | high, and already used in Chalmers comfort-zone work |
| euroFOT | moderate | poor | limited | limited | moderate |
| highD, exiD, inD, rounD (levelXdata, drone) | excellent | excellent | excellent | none | good for distributional calibration only; no driver state and no onsets |
| pNEUMA (Athens, drone) | good | good | moderate | none | as above, urban |
| Waymo Open Motion Dataset | excellent | excellent | excellent | none | good for distributional calibration; also the closest match to the data the original model was built around |
| nuScenes, Argoverse 2 | good | good | good | none | short sequences limit pre-conflict baseline |
| ANNEXT | unknown | unknown | unknown | unknown | referenced by Schumann et al. as an African naturalistic dataset; the present author has not established its availability |

### 9.1 Recommended combination

If two datasets can be obtained, the combination with the most scientific value is:

1. **Chalmers LTAP/OD** — fit *c* here, where a conventional comfort-zone boundary already
   exists for comparison.
2. **Chalmers pedestrian overtaking** — apply the same *c* without refitting, and test whether
   it predicts onsets in a geometry the fit never saw.

A simulator study is the natural third component, because it is the only way to manipulate
extra motives rather than infer them.

## 10 What is not needed

Stating this explicitly reduces the burden on the data owner:

- **Video**, except where it is needed to produce or verify the onset labels
- **Driver physiological data** — heart rate, skin conductance, and similar
- **Eye tracking**, for the comfort-zone work as specified. It becomes relevant only if the
  epistemic-value component of the model is brought in later, for example to model occlusion
  handling or off-road glances
- **High-definition maps** beyond lane width, lane count, and travel direction
- **Any personally identifying information**

## 11 Minimum viable dataset

If only one thing can be obtained, the smallest set that supports a meaningful result is:

- approximately 40 rear-end conflict events,
- kinematics at 20 Hz for ego and lead vehicle, including both accelerations,
- lane width and vehicle dimensions,
- brake onset labeled by a single stated definition,
- at least 5 s of pre-conflict baseline per event.

That supports the secondary objective in full and the primary objective within one scenario
type. It does not support the generalization test, which is the claim most worth testing.

## 12 Limitations of this specification

Volunteered rather than left for a reviewer to raise:

- The specification assumes the preference function of Schumann et al. (2026), including the
  lane-structured lateral term and the counterfactual braking margin. A different preference
  function would change which signals matter, though the kinematic core would not change.
- The lateral preference is defined per scenario in the original work rather than derived from
  a map. Applying it to a new scenario type requires a modeling decision that this
  specification cannot remove.
- Response onset is treated as the behavioral marker of comfort-zone exceedance. That is the
  assumption the primary objective depends on, and it is inherited from the surprise-based
  response-timing literature rather than established independently.
- No formal power analysis has been performed; the sample sizes in §8 are working estimates.

## 13 References and verification status

Each reference is marked with how it was obtained, following the project convention.

| Reference | Status |
|---|---|
| Schumann, J. F., Engström, J., Johnson, L., O'Kelly, M., Messias, J., Kober, J. and Zgonnikov, A. (2026). Active inference as a model of collision avoidance behavior in human drivers. *Nature Communications* 17:5009. doi:10.1038/s41467-026-73345-0 | **read from source PDF**, including the Supplementary Information |
| Dinparastdjadid, A., Supeene, I. and Engström, J. (2023). Measuring surprise in the wild. arXiv:2305.07733 | **read from source PDF** |
| Engström, J., Wei, R., McDonald, A. D., Garcia, A., O'Kelly, M. and Johnson, L. (2024). Resolving uncertainty on the fly. *Frontiers in Neurorobotics* 18:1341750 | **read from source PDF** |
| Modirshanechi, A., Brea, J. and Gerstner, W. (2022). A taxonomy of surprise definitions. *Journal of Mathematical Psychology* 110:102712 | **read from source PDF** |
| Engström, J., Bärgman, J., Nilsson, D., Seppelt, B., Markkula, G., Piccinini, G. B. and Victor, T. (2018). Great expectations: a predictive processing account of automobile driving. *Theoretical Issues in Ergonomics Science* 19(2):156–194 | **verified by search** — title, journal, volume and pages confirmed; full text not read |
| Quantifying drivers' comfort-zone and dread-zone boundaries in left turn across path / opposite direction (LTAP/OD) scenarios. *Transportation Research Part F* (2015) | **verified by search** — title and journal confirmed via ScienceDirect and the Chalmers research portal; **author list not verified**, full text not read |
| How do drivers overtake pedestrians? Evidence from field test and naturalistic driving data. *Accident Analysis and Prevention* (2019) | **verified by search** — title and journal confirmed; author list not verified |
| Markkula, G. et al., brake response extraction by piecewise-linear fit | **unverified** — the method is described in Schumann et al. (2026) Methods, which cites it; the original was not consulted |
| Näätänen, R. and Summala, H. (1974, 1976), extra motives and zero-risk theory | **unverified** — referred to in secondary sources encountered during this work; originals not consulted |
| SHRP2, UDRIVE, euroFOT, highD, exiD, pNEUMA, Waymo Open Motion Dataset, nuScenes, Argoverse 2 | **unverified for this purpose** — the assessments in §9 are based on general knowledge of these datasets and should be confirmed against their documentation before procurement |

Gaps deliberately left visible rather than filled with plausible detail: the author lists for
the two Chalmers comfort-zone papers, and the availability of ANNEXT.
