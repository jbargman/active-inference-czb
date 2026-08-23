# Chapter 11: the path to comfort-zone boundaries

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance tags
as in chapter 0. This chapter answers the project's third goal: how the model expands into
comfort-zone boundary (CZB) research, and what is needed. Fuller technical detail:
`notes/04_comfort_zone_method.md`; validation status: `notes/05_validation.md`.*

## Why this model, for this problem

Comfort-zone boundaries are quantified today per scenario, per indicator: a minimum-TTC
distribution for one conflict type, a lateral clearance for another, a headway for a
third. Three costs come with that practice: boundaries cannot be compared across
scenarios; the choice of indicator smuggles in a modeling assumption; and a quantile
describes behavior without explaining when or why drivers act (chapter 01's anchors).

The active-inference model offers a replacement with one move. Its preference prior
(chapter 07) already scores every driving state by how far it departs from "how this
drive is supposed to go" — a single scalar landscape over the state space, decomposable
into named causes. Define the comfort zone as the region where that departure is
(essentially) zero, and the **comfort-zone boundary as a level set** — one line of
constant departure — of that one field. The per-scenario indicators then stop being
separate theories: a TTC threshold, a headway, a clearance are different *projections* of
the same surface, which is, the way we read it, why they never agreed across scenarios in
the first place.

{{R1}}Two properties make the field the right one rather than an arbitrary score (chapter 02
showed both live): it is **exactly zero inside the comfortable region**, so leaving the
zone is a defined event; and it is **built from the same preference function whose
expected shortfall times the model's responses**, so the boundary (static picture) and
the decision to act (dynamic picture) come from one object, not two glued theories. One
honest qualification, added after the method review: the model's own accumulated quantity
is the shortfall *expected over noisy imagined futures*, and that expectation is not zero
inside the zone — it grades smoothly with the gap (from 99 000 to 5 000 per step across
the authors' rear-end conditions) and would trigger spontaneous re-plans in uneventful
following [OSF; `docs/method_review.md` §4.2]. The field used here is the same preference
evaluated *pointwise on the realized state*, which is what recorded human kinematics give
us and what has the exact zero. The two agree on where the boundary lies; they differ on
what happens well inside it, and the authors' gap-graded expectation is, if anything,
independent evidence that their preference function encodes a comfort zone.

The classic constructs map without remainder: the *dread-zone* boundary is where no
achievable action restores the preferred future (a physics fact, one parameter away from
the comfort boundary — the deceleration a driver is prepared to plan around); *extra
motives* are temporary reshapings of the preference prior, with computed, falsifiable
boundary shifts (chapter 07, Part C).

## What exists and works today

Built in this project, tested against the model (all numbers inherit the stated
assumptions — assumed worst-case lead braking −6 m/s², reaction time 1 s — and must be
quoted with them):

- **The field and its decomposition** over any two-dimensional slice of the state space,
  with every exceedance attributable to a named preference term (`src/comfortzone/`).
- **A closed-form boundary for car following**, cross-checked against the numeric level
  set to 0.000 m over 45 speeds — the two-independent-routes discipline of chapter 09,
  which caught a sign error that had produced a plausible wrong boundary.
- **Comfort versus dread as one parameter.** At 15 m/s: dread boundary at 0.73 s headway
  (8 m/s² — physics), comfort boundary at 1.67 s (4 m/s² — the hardest braking a driver
  plans around). The comfort boundary lands at 1.5–2.3 s across ordinary speeds — inside
  the range of observed following headways, which is a sanity check, not a validation.
- **Extra motives, quantified**: hurried (reaction budget 1.0 → 0.6 s) moves the 15 m/s
  boundary 1.67 → 1.27 s; trusting the lead (−6 → −3 m/s²) moves it to 0.42 s. The
  framework predicts *how much*, which is what makes it falsifiable.
- **Calibration from recorded kinematics alone.** The field along a recorded trajectory
  needs only the kinematics and the preference function — no particle filter, no planner,
  no GPU, microseconds per trajectory. This is the design decision that makes the method
  applicable to naturalistic datasets now, independent of the closed-loop model's open
  issues (chapters 05, 09).

## What has already been tested, and what it showed

Using the authors' own simulation output as a stand-in driver [OSF]: across 896 rear-end
trials, the full pipeline — field from kinematics, one boundary level fitted to response
onsets — recovered the reference model's brake onsets with **median timing error 0.0 s**
(interquartile range 0.2 s, onset-matching score 0.855). The machinery works end to end
on data it was not built from.

Two honest caveats travel with that result. The onsets were a *model's*, not humans' —
this validates the pipeline, not the psychology. The fitted level itself was weakly
identified: the rear-end field rises so steeply at the boundary that very different
levels score almost alike — boundary *location* robust, level not yet disciplined.
Scenarios where the field rises gently (lateral clearance) are exactly where the level
will be pinned down, which is one more reason the decisive test is cross-scenario.

## The decisive test

The claim that earns or loses everything: **one boundary level, fitted once, transfers
across scenarios**. Per-scenario indicator thresholds cannot even express this claim; the
level-set formulation stakes itself on it.

1. Take conflict events with extracted response onsets in at least two scenario types —
   the Chalmers LTAP/OD comfort-zone data and the pedestrian-overtaking data are the
   intended pair, with geometry different enough to be a real test.
2. Compute the field along every trajectory (kinematics only).
3. Fit the level on one scenario, matching first exceedance to observed onset.
4. **Apply it unchanged to the other scenario.** This step is the experiment.
5. Compare against per-scenario indicator thresholds fitted with the same freedom, and
   check the decomposition blames the right term in each scenario (safety margin in
   following; lateral in overtaking) — an attribution check the indicators cannot take.

Either outcome is worth having. Transfer succeeds: the formulation is doing real work,
and a scenario-free comfort-zone metric exists. Transfer fails: the preference function
is scenario-specific — which the paper's own supplementary material concedes is possible
— and we will know *precisely how*, term by term, which is itself a publishable
characterization of what drivers' standards share across situations.

## What is needed

- **Data**, per the specification written for data owners (`docs/data_requirements.pdf`):
  paired-vehicle kinematics at ≥ 10 Hz, response-onset labels extracted the standard way,
  30–50 events per scenario type, at least two types. No model runs are required of the
  data owner.
- **A simulator study for extra motives** — the only design that *manipulates* motives
  rather than inferring them, and the only direct test of the predicted boundary shifts.
- **Individual-differences extension** (10+ events per driver): is the fitted level a
  person? Are the preference parameters? Chapter 07's trait reading becomes measurable
  here.
- Nothing from the expensive closed loop. The path to CZB deliberately runs through the
  verified static half of the model (chapters 05, 09) — response-*time* prediction can
  join later, when the closed-loop issues are resolved, as a bonus rather than a
  dependency.

---

## Notes for the mathematically curious

**Level 1 — definitions.** Field: ε(x) = max_o log p(o) − log p(o(x)) ≥ 0, the residual
information of the pragmatic value at state x. Comfort zone {x : ε(x) ≤ c}; boundary the
level set ε = c; dread boundary where required deceleration exceeds the achievable
maximum. Calibration: choose c to maximize onset-matching (first upward crossing vs
labeled onset within tolerance) across events; `calibrate_level` implements an F1-style
score.

**Level 2 — the closed form and its numbers.** For steady following the safety-margin
term yields the boundary gap in closed form (SI Eqs. 49–51 rearranged;
`src/comfortzone/field.py::critical_gap`): the required-deceleration condition solved for
separation, containing the assumed worst-case lead deceleration, the reaction-time
budget, and the effective vehicle length. Special case worth testing empirically: when
the assumed lead deceleration equals one's own braking limit, the critical headway
collapses to the reaction time, speed-invariant. The OSF dry-run statistics, the weak
identification of c, and the transfer-check numbers are `notes/05_validation.md` §4b and
`replication/osf/`; the study design in full is `notes/04_comfort_zone_method.md` §7–7b.
