# Chapter 5: normal driving versus critical events

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance tags
as in chapter 0.*

## There is no emergency mode

The most useful single fact in this chapter: the model has **no mode switch**. No flag
flips from "normal" to "critical"; no emergency sub-model wakes up. The loop of chapter 03
runs identically at every timestep of every drive. What differs between everyday following
and a hard conflict is *which parts of the machinery are doing the work* — the same
objective, evaluated in a different region of the landscape. That is a substantive claim
about drivers, inherited from the zero-risk tradition: emergency response is ordinary
regulation, pushed hard.

The regimes still look completely different from outside, and it is worth being precise
about why.

## Normal driving: the quiet regime

In steady following (chapter 02, t < 0.8 s), four things characterize the model's state:

- {{R1}}**The surprise account drifts, slowly.** The current plan delivers the preferred future
  in most imagined rollouts, but the imagined spread always contains a few futures that end
  too close, so something accumulates even in steady following: in the authors' own runs,
  from 2% of the threshold per 0.8 s at a 3.5 s gap to 44% at a 0.5 s gap, all of it from
  the collision and safety-margin terms [OSF; `docs/method_review.md` §4.2]. What *is*
  exactly zero is the field evaluated on the realized state (chapter 11) — not "small",
  exactly zero — and that is what makes the comfort zone a defined region rather than a
  fuzzy one. The model's own accumulator, by contrast, would re-plan on its own after 2–7 s
  of uneventful following at gaps of 2 s or less; the published simulations do not show
  this only because they start 0.8 s before the lead brakes.
- **Planning is incremental.** The plan is shifted and cheaply patched each step; the
  expensive candidate-generation machinery is dormant. Most timesteps of a normal drive
  never trigger a single full re-plan.
- **Trust is extended.** The other vehicle has been behaving normally, so predictions
  concentrate on norm-following futures; the long tail of "what if they do something
  wild" is present but carries little weight (chapter 06).
- {{R1}}**Behavior is shaped by the gentle terms — in the realized state.** Speed
  preference, pedal smoothness, and lane centering — the low-stakes preference terms — are
  what the driver's actual state is scored against, and on that state the collision and
  safety-margin terms are satisfied. In the imagined futures they are not quite silent
  (first bullet), and in the published runs the driver never acts on the gentle terms at
  all before the event: it follows a fixed reference plan until its first re-plan, so what
  "normal driving" looks like as *behavior* in this model has not actually been exercised
  in the published simulations [Code: `EA_init = False`; `docs/method_review.md` §6.2].

What normal driving *is*, in this model: the region of the state space where preferred
futures remain reachable without doing anything unusual. Keeping the vehicle inside that
region is what the quiet machinery continuously accomplishes.

## A critical event: the same machinery, loud

When the world breaks the pattern (chapter 02, t ≥ 0.8 s), each of the four quiet
properties inverts, in a fixed causal order:

1. **Trust is withdrawn first.** The other vehicle's observed behavior stops matching its
   norms; the norm-conditioning releases the prediction tail, and imagined futures fan out
   to include the bad ones. This happens in the belief/prediction machinery *before* any
   decision is made — expectation revision precedes action, as the predictive-processing
   account says it should.
2. **The heavy preference terms wake.** Predicted futures now touch collision and eroded
   safety margins; the terms that were silent begin to dominate the scoring.
3. **The surprise account fills.** The incumbent plan's expected outcome falls short of
   the best achievable; the shortfall is deposited step by step. This is where response
   *time* comes from — not from sluggish senses but from evidence integration.
4. **One expensive re-plan fires**, and the chosen escape is executed with the same
   bounded planner as always.

## The choice of escape is a property of the landscape, not a rule

Nothing in the code says "brake below 60 km/h, steer above". Yet the authors' own runs
show exactly that structure emerging [OSF] — across the baseline rear-end grid:

| Initial speed | braking only | steering involved | still behind the lead at rest |
|---|---|---|---|
| 10 m/s | 86% | 0% | the norm |
| 15 m/s | 34% | 54% | mixed |
| 20 m/s | 1% | 96% | rare |
| 25 m/s | 0% | 40% (most leave the road instead) | rare |

The gradient has a physical reading: at low speed, comfortable braking removes the
kinetic energy in time and never violates the pedal-smoothness preference much; at high
speed the deceleration needed to stop behind the lead becomes so severe that a lane
change, despite its own preference costs, scores better. The maneuver choice falls out of
comparing imagined futures under one preference landscape — which is why our
re-implementation reproduced this relation even while its response timing was broken
(`notes/05_validation.md`): choice rests on the preference function, timing on the
accumulator. They are separable claims, and the model gets them right or wrong separately.

{{R1}}The 25 m/s row also shows something the paper does not mention: at the highest speed,
more than half of all runs (58%, averaged over the gap grid; 72% at the shortest gap and
still 53% at the longest) end by leaving the road, almost always during the avoidance
maneuver and mostly to the left, through and beyond the adjacent lane [OSF;
`docs/method_review.md` §4.1]. At a 3.5 s gap this is not desperation — moderate braking
would do — so it is best read as a failure of the lane-change control at speed rather than
as a human-like choice. The paper describes the model as "favoring swerving" at higher
speeds [Paper]; the deposit shows where most of those swerves end.

## What this means for using the model

- **Response time is not a parameter you set** — it is a prediction that emerges from the
  interplay of perception noise, norm trust, the accumulator rate, and the preference
  landscape. To move it, you move those (chapter 09 lists which moves what).
- **The normal-driving regime is not free** — the same machinery that produces crisp
  emergency behavior must also idle plausibly, and misconfigured preferences show up first
  as fidgety normal driving (our re-implementation's main defect is exactly an idle that
  is not quiet enough; `notes/03_replication.md`).
- **For comfort-zone research, the quiet regime is the object of study.** The boundary of
  the comfort zone is precisely where the quiet regime ends — where the surprise deposits
  first depart from zero. Chapter 11 builds on this identification, and it is why the
  method needs only the preference function, not the full loop.

---

## Notes for the mathematically curious

{{R1}}**Level 1 — one objective, two regimes.** The expected-free-energy score of the incumbent
policy decomposes over preference terms. In the quiet regime the per-step residual ε —
best-achievable minus incumbent *expected* pragmatic value — is small relative to the
loud regime but not zero: the expectation runs over 75 noisy rollouts × 30 steps, and the
collision and safety-margin terms of the worst few dominate it (5 × 10³ to 10⁵ per step
in the deposit). E therefore drifts at rate λε even before any event. In the loud regime ε
jumps by a factor of 3–4, E integrates it, and the re-plan at E ≥ 1 is a drift-diffusion
first-passage with a model-supplied drift and a non-zero starting point. Maneuver choice is the argmax
over candidate policies of the same score; no separate decision rule exists.

**Level 2 — the numbers above.** Maneuver mix: mean over the 28 baseline rear-end
conditions grouped by initial speed, from the authors' `Analysis_rear_end.xlsx`
(`braking_post`, `overtaking_post`, `brake_steer_post`, `leave_road`, `collision`) [OSF];
our extraction is `replication/osf/baseline_conditions.csv`. The separability claim —
preference-dependent relations reproduced while accumulator-dependent ones failed — is
quantified in `notes/05_validation.md` §2–§4b: 2 of 6 published relations reproduced by
our re-implementation, and its response-time distribution (median 0.20 s, sd 1.23 s)
against the authors' own (median 1.20 s, sd 0.66 s) [OSF].
