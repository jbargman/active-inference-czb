# Chapter 4: the scenario playbook — what actually changes, and the switching checklist

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. This chapter's
core evidence is a column-by-column diff of the authors' own setup tables for all three
scenarios (`Setups_*.xlsx` in the OSF deposit, 65 parameters per run) [OSF], plus a file-level
diff of the per-scenario code [Code].*

## The headline: the driver barely changes; the world does

The published model runs three scenarios: **rear-end** (a braking lead vehicle),
**oncoming** (an opposite-direction vehicle drifting into our lane), and **intersection**
(a crossing vehicle turning across our path — the held-out one). Diffing the authors' own
setup tables across all baseline runs of the three scenarios gives an unambiguous answer to
"what is different, exactly": of 65 configuration parameters, everything describing the
*driver* — perception noise, looming threshold, preference weights, planning budget,
evidence accumulation, particle counts — is **identical across all three scenarios**, with
exactly one exception described below. What changes is the *world*: geometry, initial
speeds, and the other vehicle's scripted behavior [OSF].

The same conclusion appears at the file level. Each scenario is a package of three files,
and only three [Code]:

| File | Job | In plain terms |
|---|---|---|
| `dynamics_true.py` | the world's actual physics and the other vehicle's script | what really happens |
| `decoder_true.py` | how the true state becomes the driver's observations | what can be seen |
| `reward.py` | the preference terms and norms that are scenario-shaped | what counts as normal here |

Everything else — the particle filter, the planner, the looming transform, the evidence
accumulator — lives in `src/common/` and is shared untouched. The way we read it, this is
the model's strongest structural claim: *one driver, many worlds*. It is also what makes
the held-out intersection test meaningful — the driver that handled the rear-end scenario
was dropped into a new world, not re-engineered for it.

## The full diff, in five groups

**1. Stage-setting (different by definition).** Initial positions, speeds, headings, the
desired speed, and the episode length. Rear-end: both at 10–25 m/s in the same lane, gaps
giving 0.67–3.5 s headway. Oncoming: both at 17.88 m/s (40 mph), the other vehicle
202.7 m away in the opposite lane. Intersection: ego approaching at 14.7–16.3 m/s from
36–40 m out; the crossing vehicle either waiting at the junction or rolling at 6.8 m/s
[OSF].

**2. The other vehicle's script (the heart of a scenario).** Rear-end: a countdown, then
brake at a scripted intensity (the per-condition `a_tar_min_intensity` and
`brake_intensity` columns). Oncoming: a time-to-collision trigger (`ttc_trigger`), then a
lateral incursion to a target intrusion depth (`rel_target`) — implemented, notably, as the
script *optimizing* its own steering trajectory to hit that target. Intersection: a
TTC-triggered turn across our path. These script parameters exist **only** in their own
scenario's table — they are the scenario [OSF] [Code].

**3. The one driver-side change: assumed steering variability.** `w_sd_model` — how much
steering wobble the driver's internal model attributes to the *other* vehicle when
imagining its futures — is 0.0045 in rear-end and 0.4575 in both lateral scenarios, a
factor of one hundred [OSF]. This is not a perception setting; it is an assumption inside
the driver's head about what kind of agent it is facing: a lead in a queue does not steer,
an oncoming or crossing vehicle might. It is the single number by which the driver was
told what type of situation it is in. Whether a future version could *infer* this rather
than be told is, to us, an open and interesting question [Speculation].

**4. Scenario-shaped preference and norms (inside `reward.py`).** The preference terms for
speed, pedals, and collision are shared; what is scenario-shaped is the **lane structure**:
what "in my lane", "in the oncoming lane", and "off the road" mean geometrically, and what
the *other* vehicle counts as doing normally (its norms — chapter 07 details all three).
Rear-end's version even contains hand-built bookkeeping that penalizes dawdling mid-lane
or aborting a lane change; oncoming's version treats hard braking by the other vehicle as
a norm violation alongside leaving its lane; intersection's draws the geometry of running
a red light and cutting the corner [Code].

**5. Calibrated safety assumptions.** The safety-margin preference asks "would ordinary
braking still save me if the other vehicle did its worst?" — which requires assuming what
"its worst" is. That assumed worst-case deceleration is calibrated per scenario against a
free-following study rather than shared [SI]. Our replication found this to be the
sharpest practical edge: the calibration table shipped with the code does not span all
operating ranges, and outside its range the parameter saturates and the model turns
uniformly over-cautious (`notes/03_replication.md`).

## The switching checklist

To move the model to a new scenario — a cut-in, a cyclist overtake, a pedestrian crossing —
these are the decisions, in the order we would take them. Items 1–3 are mechanical; items
4–7 are modeling judgments that deserve explicit argument in any write-up.

1. **Stage the world.** Geometry, lanes, initial states, desired speed, episode length.
   (`Setups` columns; scenario `dynamics_true.py`)
2. **Script the other agent.** Trigger condition and maneuver, with its intensity as a
   sweepable condition parameter. (`dynamics_true.py`)
3. **Check observability.** Does the driver see the new agent through the same looming
   channel? A pedestrian subtends different angles than a truck; the decoder's geometry
   (vehicle dimensions) must match. (`decoder_true.py`)
4. **Draw the lane structure into the preferences.** Define what lateral positions mean —
   own lane, oncoming, shoulder — for *this* road. This is hand geometry today; there is
   no map format. (`reward.py`, lateral term)
5. **Write the other agent's norms.** What does *normal* behavior look like for that agent
   here, as regions in its state space with graded compliance weights? This is the most
   judgment-heavy step, and it directly shapes how paranoid or trusting predictions are.
   (`reward.py::get_weights`; chapter 06)
6. **Set the assumed variability.** Choose `w_sd_model` (and its longitudinal sibling) for
   the new agent type — the "what might this thing do" dial. (item 3 above)
7. **Re-calibrate the safety assumption.** Fit the assumed worst-case deceleration for the
   new context, and confirm the calibration covers the intended speed range — the failure
   mode our replication hit. ([SI]; `notes/03_replication.md`)
8. **Define the measurements.** Response-onset definition, collision definition, and the
   condition grid, so results are comparable with the published ones. (analysis scripts)

The honest summary of effort: steps 1–3 are days, steps 4–7 are where the scenario's
scientific content lives, and skipping the argument for any of 4–7 produces a model that
runs but persuades nobody.

---

## Notes for the mathematically curious

**Level 1 — why one driver can serve three worlds.** The agent's objective (expected free
energy over a 6 s horizon) never mentions the scenario; scenario enters only through (i)
the generative process being simulated, (ii) the lateral/lane geometry inside the
preference distribution, and (iii) the norm-compliance weighting inside the prediction
step. Since all three are data to the same algorithm, transferring the driver is exactly
transferring those three objects.

**Level 2 — the diff, precisely.** Baseline-run comparison across the three `Setups`
tables: differing columns are {initial state: `x_ego, v_ego, x_tar, y_tar, theta_tar,
v_tar, v_ego_des, T`}, {script: `a_tar_min_intensity, brake_intensity` (rear-end);
`ttc_trigger, rel_target` (oncoming); `ttc_trigger` (intersection)}, {driver-side:
`w_sd_model` = 0.0045 vs 0.4575}, and `num_plans` = 1000 in oncoming's extended-budget
sensitivity runs vs 100 baseline. All remaining ~50 columns are identical across
scenarios, including every preference weight (`v_ego_sd_des, a_ego_sd_des, w_ego_sd_des,
lane_change_cost, road_leave_cost, collision_cost`), every perception noise, the looming
threshold, `N_norm, H_norm, alpha`, and the evidence-accumulation settings (`EA_mode,
EA_fac` = λ, `EA_init`) [OSF]. Oncoming's target script solves a small optimal-control
problem for the incursion (gradient descent on a steering sequence to reach the scripted
lateral target at the scripted time; `src/oncoming/dynamics_true.py`) [Code].
