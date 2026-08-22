# Chapter 9: modifying the model, and knowing whether the modification is right

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance tags
as in chapter 0.*

## The seams

The previous chapters located every place the model is *meant* to be changed. Collected in
one table:

| Seam | What it represents | Where | Chapter |
|---|---|---|---|
| Preference knobs | the driver's own standards; traits and states | `reward.py` params / `Setups` columns | 07 |
| Safety-margin assumptions | worst case planned for; reaction time budgeted | preference term + calibration table | 07, 04 |
| Norm geometry | what others are expected to do | `reward.py::get_weights` | 06, 07 |
| Assumed other-agent variability | what kind of agent I am facing | `a_sd_model`, `w_sd_model` | 04, 06 |
| Perception noise & looming | visibility, conspicuity, sensory quality | decoder noise scales, threshold | 03, 08 |
| Accumulation rate λ | evidence-to-action vigor | `EA_fac` | 05, 08 |
| Gaze system | attention on or off the road | dormant; chapter 08 | 08 |
| Scenario script | the world and its threat | `dynamics_true.py` | 04 |

A modification that does not fit one of these seams — one that needs the planner rewritten
or a new state variable threaded through the belief machinery — is a research project, not
a modification, and should be costed accordingly.

This chapter is about *what* to change and how to know the change behaves; the companion
question — how the new parameter values themselves should be obtained, and the
identifiability traps in fitting them — is chapter 10.

## The validation ladder

The question "how would we validate it" has, in our view, one good general answer: climb,
and do not skip rungs. Each rung has a cheap failure mode that the rung above cannot
detect.

**Rung 0 — property checks (minutes).** Verify the changed component against its own
specification, ideally by two independent routes. This project's cautionary tale: our
closed-form comfort boundary and the numeric field disagreed on first comparison — a sign
error had inflated a headway boundary from 0.7 s to a *plausible-looking* 3.2 s. Only the
two-routes check caught it; eyeballing would not have (`notes/04_comfort_zone_method.md`
§3). Every preference change should re-run the property suite (`tests/`, 57 tests).

**Rung 1 — mechanism check (hours, static).** Confirm the proximal effect: the knob you
turned moves the quantity it is supposed to move, in the right direction, by roughly the
expected amount, with other quantities still. For preference changes this needs no
simulation at all — the static field machinery (`src/comfortzone/`) evaluates the changed
preference on recorded or constructed states in microseconds, which is the reason chapter
11's method deliberately avoids the closed loop.

**Rung 2 — the ablation discipline (days of CPU, or free from the deposit).** Show what
the mechanism *contributes* by removing it. The paper's own Figure 6 does this for seven
mechanisms, and — the practical gift — the OSF deposit contains the complete simulation
output for every one of those ablations, seven variants × the full rear-end grid, already
run [OSF]. Before running anything: check whether the ablation you need is already in
`Setups_rear_end.xlsx` (no evidence accumulation; no prediction noise; no pedal
constraints; no looming perception; no looming threshold; no norm conditioning; no
epistemic value). A new mechanism should ship with its own ablation the same way: the
model with and without it, same grid, same seeds.

**Rung 3 — distribution comparison against the reference (free, thanks to the deposit).**
Any closed-loop change must reproduce the *unchanged* behaviors: response-time
distributions, maneuver mix, collision rates, per condition, against the authors' own
output — not against numbers read off figures. The comparison harness exists
(`replication/validate_osf.py`); a modified model earns trust by matching the baseline
where it should match and departing only where its mechanism says it should depart.

**Rung 4 — human data.** Only rungs 0–3 make rung 4 interpretable: when the modified
model meets human data (response-time curves, glance statistics, comfort-zone onsets),
any mismatch can be attributed to the mechanism under test rather than to a broken
foundation. For the comfort-zone program specifically, rung 4 is the cross-scenario
transfer test of chapter 11.

## Worked example: the recipes for this project's live proposals

| Change | Seam | Rung 1 observable | Rung 2 ablation | Rung 3 must-not-move | Rung 4 target |
|---|---|---|---|---|---|
| Hurried-driver state | t_react, desired speed | boundary shifts by closed-form amount | vs baseline params | maneuver mix at baseline | simulator time-pressure study |
| Trusting-driver state | assumed worst-case braking | boundary shift (large; chapter 07) | same | detection timing | headway distributions |
| Glances (ch. 08 P1) | gaze system | belief spread grows during glance | gaze locked on | on-road-gaze runs identical to baseline | glance-conditional RTs |
| Cognitive load (ch. 08 P3) | update throttle | slower belief convergence, same asymptote | throttle = 1 | lane keeping | gradual-conflict RTs |
| New scenario | script + norms + lane geometry | scripted threat plays out as drawn | — | driver params untouched (ch. 04) | that scenario's human data |

## Practical constraints that shape all of this

- **The closed loop is expensive.** ~18 s of CPU per simulated timestep here; a 10-second
  scenario is a two-hour job, a grid is a cluster job or a GPU. Consequences: prefer rung
  1's static evaluation wherever the question allows; mine the deposit before simulating
  anything (rungs 2–3 are often free); and when simulating, use the restartable runners —
  long jobs get killed in this environment, and the checkpoint/resume machinery exists for
  that reason (`HANDOFF.md` §3).
- **Keep the reference implementation clean.** The authors' code carries exactly one local
  patch, documented in `replication/PATCHES.md`. Modifications belong in forks or in our
  re-implementation — never silently in `external/aica/` — so that "the reference model"
  stays a fixed point all comparisons share.
- **Two implementations, two roles.** The authors' code is ground truth; our NumPy mirror
  (`src/aidriver/`) exists to make mechanisms inspectable and is currently trustworthy for
  preference-dependent behavior but not for closed-loop response timing
  (`notes/05_validation.md`). Rung 1 work can use the mirror; rungs 2–3 should use the
  reference.
- **Construct configurations from the validated ones.** Defaults in our mirror do not all
  match the validated sweep configuration; two parameters in particular are near-namesakes
  with different jobs (`HANDOFF.md` §4, "two traps"). Start every new configuration from a
  known-good one, and record the full parameter set with the results the way the authors'
  `Setups` tables do.

---

## Notes for the mathematically curious

**Level 1 — why rung 1 is often static.** Preference changes alter the field
ε(x) = max log p(o) − log p(o(x)) pointwise; their first-order behavioral consequences
(boundary locations, term attributions) are properties of that field and need no dynamics.
Only changes that alter *timing* (λ, perception noise, gaze) or *prediction* (norms,
variability dials) require the loop.

**Level 2 — the ablation columns.** In every `Setups_*.xlsx`: `EA_mode = None` (no
evidence accumulation — the model re-plans continuously), `noise_pred_fac = 0.002` (no
prediction noise), `use_pedals = 0`, `use_looming_perception = 0`, `looming_threshold = 0`,
`N_norm = 1` (no norm conditioning), `alpha = 0` (no epistemic value) [OSF]. The deposit
holds 7 × 28 = 196 ablation runs for rear-end alongside the 28 baseline ones; oncoming
and intersection carry the same structure at their grid sizes. Rung 3's comparison
statistics and onset definitions are in `replication/validate_osf.py` and
`notes/05_validation.md` §4b.
