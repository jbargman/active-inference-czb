# Proposed revision of the data interface (schema version 2), to go to Volvo Cars when the track resumes

*2026-09-18. Collects, in one place, every change to `transfer/interface_schema.yaml` that the project's
work since 2026-09-03 has found necessary: the five gaps card NDS.1 found (queries NDS.Q2 to NDS.Q5,
`replication/czb/out/nds1_interface_smoke.md`) and the extension the generative-model framework needs
(`docs/generative_model_framework.md` §4; Jonas's ruling GM.Q1 of 2026-09-18: yes). **The VCC track is
paused (2026-09-11); this is a draft for Jonas, not a document sent to anyone.** The schema file itself is
unchanged until the revision is agreed; decision 6 of the split-site protocol offers VCC review of the
schema before their adapter is written, and after the adapter exists a change is expensive.*

## 1 Corrections found by card NDS.1

| # | change | why | query |
|---|---|---|---|
| 1 | replace `ref_point` by `ego_ref_point` and `oth_ref_point`, each in {front_bumper, rear_axle, cog} | the ego's position comes from its own signals, the partner's from radar or camera; they are referenced differently | NDS.Q2 |
| 2 | add `ego_front_overhang` and `oth_front_overhang` [m] (NaN if unknown), or state that positions are delivered at the vehicle centre | a rear-axle position cannot be converted to a bumper position without the overhang; the loader refuses rather than guesses | NDS.Q2 |
| 3 | state one lateral frame for `ego_y` and `oth_y` (both relative to the ego's lane centre, or both absolute) | the gate needs their difference; mixed frames make the clearance wrong by the ego's own lane offset | NDS.Q3 |
| 4 | add `brake_onset_criterion` in {pedal_switch, decel_threshold, other} and, for decel_threshold, `brake_onset_a_th` [m/s²] and `brake_onset_t_min` [s] | the axis value at the onset is the observation; the criterion sets the level | NDS.Q4 |
| 5 | require `valid = 1` at `t_brake_onset`, or add `valid_at_onset` to the metadata | the observation may otherwise be read from an interpolated partner track | NDS.Q5 |

## 2 Extension for the generative-model framework

| # | change | why |
|---|---|---|
| 6 | a new `scenario` value **`exposure_adjacent`**: windows of fixed length (proposed 10 s) with a vehicle in the adjacent lane and **no lane change**, sampled at random from trips at a stated ratio to the cut-in events (proposed 10 exposure windows per cut-in); `t_conflict_onset` NaN, `t_brake_onset` NaN | the lane-change initiation hazard (component C1) needs the population that could have cut in and did not; without it initiation and occurrence are confounded |
| 7 | optional time-series columns **`oth_lead_gap`** [m] and **`oth_lead_dv`** [m/s] (the partner's gap and closing rate to the vehicle ahead of it in its own lane; NaN when none is tracked), and **`oth_indicator`** in {0, 1, NaN} | the hazard's first feature is the partner's reason to change lanes; the indicator where the sensor set reports it |
| 8 | for `cut_in` events, define `t_conflict_onset` as the moment the partner's lateral offset from its lane centre first stays beyond a band (proposed 0.3 m), and write the band into `events.csv` as `lc_onset_band_m` | the onset must mean the same at both sites; the line crossing is later for slower lane changes |
| 9 | a sampling rule for exposure windows written into the schema (which trips, which road types, which traffic densities) and applied identically at both sites | a hazard fitted on exposure sampled where lane changes are likely is biased |

## 3 Export rule additions

Component C1's outputs (coefficient table with standard errors, calibration table by decile with counts,
constant-hazard baseline, event and exposure counts) fit the existing `allowed_outputs`. One addition:
"fitted model coefficients with standard errors and the counts they rest on" under `allowed_outputs`, and
"model weights of any learned predictor" under a new heading `steward_decision`, to be ruled on at
sign-off (GM.Q3, JJ.Q3).

## 4 What stays

Everything else in schema version 1. The synthetic fixture (`transfer/make_synthetic_fixture.py`) should
gain scripted lateral motion for its cut-in events and a few `exposure_adjacent` windows so that the
rehearsal (card GM.0) covers components C1 and C2 (query GM.Q4).
