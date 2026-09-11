# Building on the active-inference driver model: what we have done at Chalmers, and what is open

*Jonas Bärgman, Chalmers University of Technology. Prepared for a conversation with Julian
Schumann, September 2026, and drafted with assistance from Claude (Anthropic). Work in
progress: the results below are ours, mostly unpublished, and not for citation.*

## Why we started, and what this note is

Our interest in the model of Schumann et al. (2026) comes from a question it seemed well
placed to answer: can a driver's comfort-zone boundary be measured with one quantity that
means the same thing in every scenario? The preference prior looked like that quantity. A
second interest is crash causation: whether the model can serve as the response process
inside a counterfactual crash-generation model.

This note summarizes what we implemented, what we tried, what worked and what did not, and
where we would value your view. The released code and the OSF deposit made all of it
possible, and we are grateful for how complete they are. We have tried to state our readings
as readings; you know the model far better than we do, and several of the open issues at the
end are exactly the places where we may have misunderstood it.

## 1 The data we used

| source | what it is | what we used it for |
|---|---|---|
| Your code, OSF | the released code, and the deposit for all three scenarios including the ablation grids | replication, and understanding the mechanisms |
| Video 1 | clips of four scenarios — a cut-in (by a car and by a truck), a left turn across the path of an oncoming vehicle, overtaking a cyclist, overtaking a truck — frozen at fixed moments, with the question "would you intervene?"; 80 participants, 43 of whom completed all four scenarios | per-driver boundary levels, and whether they are shared across scenarios |
| Video 2 | cut-ins only: 144 participants, 10 944 trials, 378 clips crossing speed difference with time to collision (ego 110–130 km/h, gaps 4–80 m) | the comparison of candidate criticality measures, and the gate |
| Test track | 26 drivers making real left turns in front of an oncoming car, 2013 (Bärgman et al., 2015) | a real-driving anchor for the left-turn boundary |
| QUADRIS | 5 000 synthetic rear-end pre-crash scenarios with real-world weights (Wu et al., 2025); glance and deceleration distributions digitized from Bärgman et al. (2024) | crash causation |

Both video studies come from a related project and are unpublished. Video 1's design ties
gap and time to collision together completely, which is why video 2 was needed: it crosses
them, so that clips at the same time to collision span a sixfold range of gap.

## 2 What we built

**Replication.** Your code, run on our CPU-only hardware, reproduces the deposit to the
timestep; we verified the looming-threshold mechanism across all 896 deposited rear-end
runs. We also wrote a readable NumPy mirror of the six preference terms, following the
released code wherever it differs from the SI, and a library of surprise measures along the
lines of Dinparastdjadid et al. (2023).

**A practical constraint that shaped the rest.** On CPU a single scenario ran from minutes to
hours, with no clean predictor of which. So wherever we could, we evaluated the preference
function pointwise on recorded kinematics instead of running the loop. Much of what follows
depends on that shortcut, and we come back to whether it is legitimate in section 6.

## 3 Comfort-zone boundaries: what we tried, and what the data said

**3.1 The starting idea.** The *deficit* — how far the preference of the current state falls
short of the preferred state — is zero inside the comfortable region and grows outside it.
A boundary is then a level of the deficit, a driver's boundary is their own level, and the
deliverable is a percentile of levels across drivers. It needs only the preference function
and recorded kinematics.

**3.2 Two pre-registered tests went against it.** First, accumulating the deficit over time to
time the response did not fit the repeated-clip design. We read that as a verdict on our own
accumulator (deficit-driven, non-leaky, fixed bound), not on evidence accumulation in general.
Second, and decisively, we asked whether the deficit is the right criticality measure at all.
On video 2, with the models, folds and decision rule written down before the run, the deficit
scored a held-out error of 0.347 against 0.152 for a plain gap threshold (chance 0.320; the
sampling-noise floor of the data 0.118).

A later decomposition split that loss in two. About 44% came from a construction of our own —
a continuous lane-entry weight we added for the cut-in (section 4), which suppressed the
deficit in exactly the slow lane changes people responded to most. The rest came from the
worst-case counterfactual of the safety term. In video 2's regime that counterfactual is
violated almost everywhere, so the term tracks the absolute speeds: about 0.3 m/s of change
per meter of gap, against 1.5–2 m/s per m/s of either vehicle's speed. Within clips of equal
time to collision it therefore ranks by speed, where the raters rank by gap.

We read this narrowly, as a statement about the counterfactual *used as a comfort criterion*.
For collision avoidance, where the outcome genuinely depends on where the other vehicle will
be and how fast everyone is going, it may be exactly the right reference.

**3.3 What worked: your model's perceptual front end.** Among the candidates, the optical
expansion rate dθ/dt = W·Δv/(g² + W²/4) — the quantity your perception stage computes — fitted
best: 0.113, at the noise floor, against 0.152 for gap, 0.152 for optical size, 0.168 for
inverse tau and 0.289 for required deceleration. A freely weighted rule in log gap and log time
to collision put a weight of 0.497 on the gap, which is the looming identity rather than an
approximation of it. One contrast is worth noting: Xue et al. (2018) found inverse tau the
better cue for brake onsets in a driving simulator. On our video paradigm the order reverses,
and whether that is the paradigm or the task is, as far as we can tell, open.

**3.4 The model as it stands.**

> share who intervene = lapse + (1 − lapse) × gate × Φ((axis − level) / spread)

- **The gate** says whether the other vehicle counts yet: the probability that its lateral
  clearance, projected 3 s ahead at its current rate, falls below a minimum. The idea came from
  a colleague's parallel analysis. Fitted on post-onset clips only, it predicted the pre-onset
  clips out of sample (error 0.032). The gate is the part that changes between scenarios.
- **The axis** is scenario-specific: the expansion rate for the cut-in, the oncoming vehicle's
  distance for the left turn.
- **The level** belongs to the driver. On the cut-in the population median is 0.032 rad/s
  (about 1.8° of apparent width per second), the 80th percentile 0.066 rad/s.
- **The level looks like a trait.** Without any model, each driver's propensity to intervene
  correlates at +0.50 to +0.74 across the six pairs of the four scenarios, about 69% of what
  the data's reliability allows. The fitted levels on the cut-in and the left turn agree at a
  rank correlation of +0.65 over the 43 drivers seen in both.
- **Real driving.** On the test track the median comfort boundary was 2.45 s of
  post-encroachment time, against 2.18 s on video, and the video-fitted population predicted the
  drivers' real go/no-go decisions better than chance (0.200 against 0.289) with nothing
  refitted. Drivers were far more consistent in the car: a within-driver spread of 0.20 s against
  0.86 s.

The limitations we see ourselves: both video studies show frozen clips without self-motion,
the response is a judgment rather than an executed maneuver, and the left turn is the only
scenario with a real-driving check. Naturalistic data, planned with an industry partner, is
meant to be the test.

## 4 Cut-in as a scenario

We never ran the full closed loop on a cut-in; the cost was prohibitive on our hardware. What we
did was stage cut-ins in the preference function, and that alone taught us what the scenario
asks of the model.

- **The other vehicle** can be a replay of recorded trajectories rather than a scripted
  maneuver, which avoids anything like the oncoming scenario's incursion optimizer.
- **The desired speed** has to come from the clip. At the default of 15 m/s against an ego
  speed of 30.5 m/s, the speed term dominated everything else.
- **The lateral tests are binary.** Looming is perceived within 3 vehicle widths, and the
  collision, safety and closing-rate terms apply within 1.15 widths. A cutting-in vehicle
  straddles the boundary for about 2.5 s, and none of the three published scenarios sustains
  that state. Since the safety term is also an indicator, two clips of very different urgency
  (a 10 m and a 21 m gap at 30.5 m/s) received an identical safety score, switching on as a
  step when the box test flipped.
- **Our fix, and what it cost.** We made lane entry continuous by projecting the lateral overlap
  to the moment of longitudinal closure. That is the construction behind the 44% share of the
  loss in section 3.2. Projecting over a fixed 3 s horizon instead removed that share.
- **The norms do not fit.** None of the three published norm sets suits a vehicle that is
  *transiently and legitimately* straddling the line. The cut-in seems to us to need a norm
  that depends on the maneuver's progress. We have not built one.

## 5 Crash causation

We placed your model as the response process inside the crash-causation model of Bärgman et al.
(2024), keeping its causation components as switchable parts: off-road glances placed as a
renewal process, too-close following, a deceleration cap, a no-response share, and the
abnormal-acceleration follower of Wu et al. (2025). Crashes were generated from the QUADRIS
seeds, with the follower's original speed profile minus its own braking as the counterfactual,
and compared with the QUADRIS reference by the practical-equivalence method of Wu et al. (2026).

- **Severity.** The active-inference conditions came closer to the reference crash severities
  than the original model's fixed-delay response (θ 0.148 against 0.209), despite producing
  4.7 times the crash probability. Tested as a difference the ordering holds with a probability
  of about 0.97. Neither reaches practical equivalence.
- **Braking.** Only the active-inference conditions reproduce the reference's many crashes with
  no follower braking; the weighted mean follower braking came within 0.3% of the reference,
  where the fixed-delay response over-braked by 35%.
- **Timing.** Brake onsets came a median 1.25 s after the anchor (interquartile range
  0.50–1.75 s), against the fixed 0.50 s. A cheap open-loop surrogate — the pointwise preference
  plus the accumulator — matched the full closed loop to a median of 0.55 s across 23 scenarios
  from 1.3 to 35.5 m/s.
- **The glance gate.** Forcing off-road glances through the code's own observation gate, a
  driver who had registered the lead's braking kept responding *during* the glance, close to
  the attentive onset, even under a near-total blackout. As we understand it, the belief cloud
  coasts on its own norm-shaped prediction and the accumulator keeps filling. The fixed-delay
  model assumes the opposite, so the two differ testably when a glance begins after the conflict
  has been registered.
- **A caution about validation.** In this crash population severity and timing are close to
  independent: roughly 70% of the variation in impact speed comes from the scenario rather than
  the response. A model validated only on severity may therefore be close to unconstrained in its
  response timing.

## 6 Open issues, where your view would help most

1. **Comfort or collision?** Was the safety-margin counterfactual meant to describe what drivers
   find comfortable, or only what avoids a collision? If comfort is in scope, would you model it
   as a level of the same preference, or against a different reference?
2. **The closing-rate preference.** The one-sided inverse-tau term (mean 0.2 s⁻¹, a time to
   collision of 5 s) is, as we read it, the model's closest thing to a comfort term. Where does
   the 0.2 come from, and would a preference on the expansion rate itself be a natural variant?
3. **Individual differences.** Which parameters would you use to express a stable driver trait:
   the reaction-time budget, the assumed worst-case braking, the accumulation rate, the
   tolerances? We find one per-driver level shared across scenarios, and would like to know where
   in the model it would naturally live.
4. **Cut-in norms and lateral entry.** How would you write the norm for a vehicle that is
   legitimately partway into the lane, and did you consider a graded version of the binary
   lateral tests?
5. **The gate from inside the model.** The collapse of trust in the norm tournament, when the
   observed state stops being normal, looks to us like a candidate for "when does the other
   vehicle start to count". Could it replace our fitted clearance gate, and put the onset inside
   your model?
6. **Crash causation.** Is the coasting of beliefs through a closed observation channel the
   intended behavior? Perception noise above the looming threshold is very small in the released
   configuration; for work on visibility and distraction, would you recommend distance-dependent
   uncertainty instead?
7. **Continuous driving.** For naturalistic data, where nothing marks the start of an event, what
   starting point for the accumulator would you use?
8. **Practicalities.** Is the pointwise evaluation of section 2 a fair approximation in your view,
   is there a faster implementation we should use, and would you be interested in a joint look at
   the cut-in data?

## References

Bärgman, J., Smith, K., & Werneke, J. (2015). Quantifying drivers' comfort-zone and dread-zone
boundaries in LTAP/OD scenarios. *Transportation Research Part F: Traffic Psychology and
Behaviour, 35*, 170–184.

Bärgman, J., Svärd, [initials], Lundell, [initials], & Hartelius, [initials] (2024). [Title and
source to be completed.]

Dinparastdjadid, A., Supeene, I., & Engström, J. (2023). *Measuring surprise in the wild*
(arXiv:2305.07733). arXiv. https://arxiv.org/abs/2305.07733

Schumann, J. F., Engström, J., Johnson, A., O'Kelly, M., Messias, J., Kober, J., & Zgonnikov,
A. (2026). Active inference as a model of collision avoidance behavior in human drivers.
*Nature Communications, 17*, Article 5009. https://doi.org/10.1038/s41467-026-73345-0

Wu, [initials], Flannagan, [initials], Sander, [initials], & Bärgman, J. (2025). [Title to be
completed.] *IEEE Transactions on Intelligent Transportation Systems*. arXiv:2406.15538.

Wu, [initials], Sander, [initials], Flannagan, [initials], & Bärgman, J. (2026). *Practical
validation of synthetic pre-crash scenarios* [Preprint; full reference to be completed].

Xue, Q., Markkula, G., Yan, X., & Merat, N. (2018). Using perceptual cues for brake response to
a lead vehicle: Comparing threshold and accumulator models of visual looming. *Accident Analysis
and Prevention, 118*, 114–124.
