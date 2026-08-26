# Chapter 8: crash-causation mechanisms — what exists, what does not, and what we propose

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. This chapter
answers question (c) of the project brief. It separates, explicitly and per section, what
is in the released model [Code] [Paper] from what is our proposal [Speculation]. Everything
under "Our proposals" is speculation by this project — not the authors' work, not
published, not validated.*

## What "crash causation" needs from a driver model

The mechanisms behind real crashes — in the human-factors reading this project comes from —
are rarely exotic: eyes off the road at the wrong moment, expectations that the situation
then violates, impaired or slowed responses, and degraded perception. A driver model useful
for causation research must be able to *produce* crashes through these mechanisms, not just
fail randomly. The answer to "can this model do that today" is: partly — and more than the
paper advertises.

## What exists in the released code today

**1. A complete, dormant gaze system [Code].** This is the chapter's most important
finding. The common code — not a fork, the code that ran the published results — carries a
two-state gaze variable (eyes on road / off road) threaded through the whole architecture:

- the *dynamics* include a gaze state with switching probabilities between on and off;
- the *observation model* multiplies perception noise by a factor (3 in the shipped configuration) when gaze is off road —
  looking away does not blind the driver, it degrades evidence quality by a set ratio;
- the *belief machinery* reserves the first two state dimensions for gaze (visible in the
  OSF belief arrays, where they sit constant [OSF]);
- the *preference vocabulary* includes a gaze term (`road_gaze_preference`, set to zero in
  all published runs [OSF]);
- and the *planner* contains the line that turns it all off: a hard-coded "avoid off gaze
  right now" [Code, `mpc_discrete.py`].

In other words: off-road glances are implemented as *actions the driver could choose*,
with an evidence price attached, and the published model was simply forbidden from
choosing them. The earlier paper in this line (Engström et al. 2024) demonstrates exactly
this machinery on uncertainty-and-looking tasks [Paper]; the collision-avoidance paper
switched it off to isolate avoidance behavior.

**2. Perception-quality causation [Code] [SI].** Observation noise scales are parameters,
and looming makes perceptual difficulty state-dependent for free: small visual angles and
low expansion rates are genuinely harder. Fog, darkness, or a small motorcycle are
representable today as noise-scale and geometry changes — with the detection threshold
producing late detection *mechanistically* rather than by adding delay.

**3. Expectation-based causation [Code] [Paper].** Chapter 06's norm trust is a
looked-but-did-not-expect mechanism already: a driver whose norms say "oncoming vehicles
stay in their lane" allocates prediction weight accordingly, and is structurally late for
the rare violator. The published high-speed rear-end runs already show crashes of exactly
this signature [OSF]. Mis-calibrated trust — the classic expectancy crash — is a parameter
setting, not a new mechanism.

**4. A response-vigor dial [Paper].** The evidence-accumulation rate λ globally scales how
fast surprise converts into action. It is the model's single most response-time-sensitive
parameter, which makes it a blunt but honest "generalized impairment" knob.

## What does not exist

No fatigue or drowsiness dynamics (nothing varies with time-on-task; no microsleep
process). No cognitive load or dual-task interference beyond the gaze dichotomy. No
alcohol/drug pharmacodynamics. No individual-differences layer — one parameter set per
run. No learning: expectations do not drift with exposure. These absences are real; the
question is how much of each can be built from the parts above.

## Our proposals

{{R1}}*Added 2026-08-23.* The proposals below have since been developed into a concrete plan,
`docs/crash_causation_plan.md`: the four mechanisms of Bärgman et al. (2024) — off-road
glances, too-close following, low deceleration, no response — as switchable components
around an active-inference response process, crashes generated from the QUADRIS rear-end
seed scenarios, and a practical-equivalence comparison with the Wu et al. framework. The
plan also records that the released code already contains the hook an off-road glance
needs (the gaze state that scales observation precision, `decoder.py`, left over from the
Engström et al. (2024) model). Read this chapter for the reasoning; read the plan for what
will actually be built.

{{R2}}*Updated 2026-08-25.* The plan has been executed: the components are built (plus a
fifth, the abnormal-acceleration follower of the QUADRIS generation paper), the input
distributions are digitized from the published figures, and the comparison against the
5 000-scenario reference has run. `docs/crash_causation_results.md` is now the document of
record; the section "What has been learned by building it" below carries what changed in
this chapter's claims.


*Everything from here to the end of the section is [Speculation]: our ideas, stated so
they can be criticized, not the authors' and not yet built or validated.*

**Proposal 1 — awaken the gaze system (glances off road).** Remove the hard-code, give
the gaze term a nonzero preference (the value of looking at the secondary task), and let
the epistemic machinery price the glance: looking away buys task reward and costs
evidence about the road, with the cost automatically largest when uncertainty about the
lead is growing. Calibrate the switching dynamics against observed glance-duration
distributions. The validation target is sharp and known: glance-conditional response
times and the off-road-glance odds ratios of naturalistic rear-end studies. If the
mechanism is right, mid-glance conflict onsets should produce the documented late, harder
responses *without any added reaction-time penalty* — the delay should fall out of missed
evidence. We consider this the single most valuable and most reachable extension: the
machinery exists, only the permission and the calibration are missing.

**Proposal 2 — drowsiness as evidence-quality decay plus vigor decay.** Represent
drowsiness as slow co-drift of three existing quantities: rising observation noise
(perceptual dulling), falling λ (slowed evidence-to-action conversion), and widening
pedal/steering tolerances (sloppier regulation), with brief forced off-gaze episodes as
microsleeps. Validation: the model should reproduce the empirical drowsiness signature —
growing lane-position variability first, delayed responses second, missed events last —
and the microsleep-timing dependence of run-off-road crashes. This is a composition of
existing dials, which is its attraction and its risk: it may be too coarse to capture
sleep-pressure dynamics, and we would validate the *signature ordering* before trusting
any absolute numbers.

**Proposal 3 — cognitive distraction as belief-update throttling.** Phone conversation
without glances ("eyes on, mind off"): keep gaze on road but reduce the weight of new
evidence in the belief update (or equivalently inflate assumed observation noise), leaving
looming geometry untouched. Prediction: normal lane keeping, normal detection of gross
events, but delayed *accumulation* — later responses to gradually developing conflicts,
the classic cognitive-distraction profile. The clean contrast with Proposal 1 (evidence
absent vs evidence discounted) is testable: the two mechanisms predict different
dependence of response delay on conflict onset timing relative to the glance.

**Proposal 4 — expectancy crashes as norm mis-calibration.** Use the existing norm
geometry deliberately: fit norm regions to what drivers at a specific junction have
learned to expect, then confront the model with the rare violator. This needs no new
machinery at all — it is a research design, not an extension — and it connects directly
to the looked-but-failed-to-see literature and to our LTAP/OD comfort-zone data.

For each proposal the validation ladder of chapter 09 applies: mechanism check in
simulation, signature check against published aggregate curves, then — only if those hold
— parameter fitting to individual data.

## What has been learned by building it

{{R2}}*Added 2026-08-25; the full account is `docs/crash_causation_results.md` [Repo].*

{{R2}}**The gaze system gates evidence, not inference — demonstrated.** Forcing off-road
glances through the code's own `I_factor` observation gate in the closed loop produced
the chapter's sharpest finding: a driver who has already registered the lead's braking
keeps responding *during* the glance, at essentially the attentive onset, even under an
effectively total observation blackout. The belief cloud coasts forward on its own
norm-shaped prediction (chapter 06) and the accumulator keeps filling from remembered,
extrapolated evidence — looking away blocks new observations, not inference. The CBM of
Bärgman et al. (2024) assumes the opposite (no accumulation while eyes are off, response
only 0.5 s after eyes return), so the two architectures diverge exactly when a glance
begins *after* conflict-onset registration, and coincide when the glance covers the
onset. This is a testable behavioral distinction that neither paper states, visible only
by running both.

{{R2}}**As a response process inside a causation model, the active-inference driver holds
its own.** With the counterfactual done right (original follower profiles with braking
removed), glances placed as a renewal process rather than anchored, and the fifth
component included, the active-inference conditions sit at the same equivalence distance
from the QUADRIS reference as the CBM control — and the two miss differently: active
inference over-produces the mildest crashes but reproduces the reference's dominant
non-braking crash character; the CBM over-produces moderate severities and cannot. Its
attentive onsets are later and far more variable than the CBM's fixed rule (median 1.25 s
versus 0.50 s after the τ⁻¹ = 0.2 s⁻¹ anchor), a difference confirmed — not an artifact —
by the closed loop.

{{R2}}**The response-timing surrogate is validated.** The cheap open-loop surrogate
(pointwise preference field plus accumulator, chapter 12) matches the full closed loop's
attentive onsets to a median absolute difference of 0.55 s across 23 scenarios spanning
1.3–35.5 m/s, with the accumulator's zero start validated against the "arriving
mid-cycle" alternative for windows that open near the conflict. Proposal 1's epistemic
half — the model *choosing* its glances by pricing them — remains unexercised; the forced-
schedule route is what has been tested.

## How strict is "practically equivalent"? Reading a ROPE

{{R3}}*Added 2026-08-26. The calibration behind this section is
`docs/equivalence_rope_note.md`; the metric-by-metric diagnosis is
`docs/severity_vs_timing.md` [Repo].*

{{R3}}The comparison in this chapter is scored with a **practical-equivalence test**, and
that test deserves explaining, because its verdict has been read more harshly than it
should be. An ordinary significance test asks whether a difference can be detected, and
with enough data the answer is always yes, since no two distributions are exactly equal.
An equivalence test reverses the question and asks whether any difference is *small enough
not to matter*. The **ROPE** — region of practical equivalence — is the written-down
definition of "small enough". Nothing statistical fixes it; it is a domain judgment about
what difference would change a decision, and the method's authors say so explicitly.

{{R3}}The machinery is simpler than the notation suggests. Sort the reference crashes by
severity and cut them into five bands each holding a fifth of the data. Pour the model's
crashes into the same bands: a perfect model puts a fifth in each. Our best configuration
puts 17.4%, 20.5%, 21.2%, 22.9% and 18.0%. Two numbers summarize the mismatch. **θ** is
the worst single band, measured against its proper share — band 4 holds 22.9% where 19.9%
belongs, an excess of 15%, so θ = 0.148. **Θ** is the total misplaced share, 0.091. In one
sentence: *no severity band may be off by more than 10% of its proper share, and no more
than 5% of all the crashes may sit in the wrong band.* For our result, the model misplaces
about three crashes in every hundred where the rule allows two.

{{R3}}**Is that hard to pass? It was, and for reasons that had nothing to do with the model.**
The instructive test is to compare the reference with *itself*: draw a large synthetic sample
from the reference distribution, so the two are identical by construction, and run the test.
Done that way, our original configuration failed much of the time at five bands and never at
the twenty bands the method's own bin rule prescribes for a reference this size. A criterion
that a perfect model cannot pass is measuring the instrument, not the thing.

{{R3}}Three choices around the threshold did that work, and each looked innocuous alone.
**First**, we weighted every severity band equally, which sounds neutral but is not: in the
method's own construction bands are weighted by how much injury risk the assessed system
leaves behind, and a weight of one corresponds to a band carrying a clinically meaningful 2%
injury risk. QUADRIS rear-end crashes are far milder than that, so equal weighting silently
held every band to a standard meant for the most consequential ones. **Second**, our
bootstrap resampled crash *values* in proportion to their weight and then treated the result
as unweighted, which claims the precision of 5 000 independent scenarios when the weights are
concentrated enough that they carry the information of roughly 950 — the intervals came out
about half as wide as they should have been. **Third**, and most consequentially, we treated
the reference as a *sample* from a larger process rather than as the target set.

{{R3}}**The resolution was to settle what the reference represents.** These 5 000 scenarios
are the ensemble the comparison is about: every condition faces the identical set, and the
conclusion concerns the driver models rather than the traffic they were drawn from. Treating
them as the target population fixes the bands and leaves only the model's own sampling noise,
which drops the noise floor to about 0.02 — comfortably below any threshold worth using. The
price is a restriction on what may be claimed: results are statements about *this* ensemble,
never about crash severity in traffic at large. Given the exposure problem described later in
this chapter, that restriction was already binding for other reasons.

{{R3}}**Where that leaves our result.** The distance is now measured against a criterion the
reference can actually resolve. Condition B's severity θ is 0.148 with a 95% interval of
[0.110, 0.204], the CBM control's is 0.209 [0.176, 0.244], and neither reaches practical
equivalence at a defensible tolerance. What *is* solid is the comparison: tested as a paired
difference, with both conditions scored against the same resampled reference, the
active-inference condition is closer on every single resample. The lesson we would carry
forward is that overlapping intervals do not settle a comparison when the two estimates share
their uncertainty — the difference is what needs the interval.

{{R3}}**The other lesson is that the same statistic does not mean the same thing on every
metric.** θ is built on bands of equal reference weight, which assumes the reference can be
cut into five equal pieces. Severity is smooth and continuous, so it can, and θ = 0.148 is
a real statement. The no-return time cannot: it lives on a 0.05 s lattice with only 25
distinct values in the whole reference, so θ largely measures whether the model lands on
the same grid points. The follower's braking cannot either: 48% of reference crashes have
essentially no braking at all, an atom too large to split, and two of the five band edges
collapse onto the same point — which is what produces the alarming θ = 1.058. Compared on
bands chosen in advance instead, the non-braking share agrees to within 5%, and the real
disagreement is a moderate redistribution *within* the braking crashes. The practical rule
we would now follow: do not apply this statistic to a metric with an atom or a lattice
without fixing the bands beforehand.

{{R3}}**A result hides inside the puzzle.** It looks paradoxical that severity nearly
matches while timing and braking do not, since severity is produced by timing and braking.
The resolution is that in this crash population they are close to independent. Conditions B
and C differ by a factor of 4.7 in how often they crash, because their response processes
differ by about 0.75 s in onset — yet their severity quartiles agree to within 0.3 m/s.
Roughly 71% of the variation in impact speed is inherited from the scenario rather than
produced by the response. Response timing decides *how many* crashes happen; the scenario,
and whether the driver brakes at all, decides *how hard* they are. The practical
consequence is worth keeping: **a driver model validated only against crash severity
distributions is close to unconstrained in its response timing**, which matters for anyone
using this kind of comparison to accept a model.

## The honest limits of the enterprise

A model that produces crashes through interpretable mechanisms is a tool for *reasoning*
about causation — counterfactuals, mechanism attribution, what-if-the-glance-had-ended-
sooner — not a certified digital twin of any driver. The proposals above inherit the
model's existing limitations (non-reactive others, hand-drawn norms, thirteen tuned
parameters), and adding impairment dials multiplies the flexibility that already worries
the framework's critics (chapter 01). Our position: build one mechanism at a time, hold
its validation target fixed in advance, and treat a failure to reproduce the signature as
a finding about the mechanism, not an invitation to add parameters.

---

## Notes for the mathematically curious

**Level 1 — why the gaze system prices glances correctly.** With gaze off road,
observation noise is multiplied by a factor ≥ 1, so the observation likelihood flattens
and the belief cloud's spread grows; epistemic value (expected uncertainty reduction) of
returning gaze to the road grows with it. A glance therefore carries an automatically
increasing price as the situation's uncertainty compounds — the model looks back *because
it is worth it*, reproducing the uncertainty-driven glance rhythm of the 2024 paper
[Paper].

**Level 2 — the implementation sites.** Gaze state: first two dimensions of the belief
state (`b[..., :2]` in the OSF arrays, constant in the published runs [OSF]); transition
probability and off-gaze noise factor: `src/common/dynamics.py` (parameter `p`,
`I_factor`) and `src/common/decoder.py` (noise multiplication under off gaze); the
hard-coded prohibition: `src/common/mpc_discrete.py` ("Avoid off gaze right now
(hardcoded)"); the preference slot: `road_gaze_preference` in every `Setups_*.xlsx`, value
0 [OSF]. Proposal 3's throttle is a likelihood tempering exponent on the observation
update; Proposal 2's λ decay acts in the accumulator E(t) = E(t−1) + λ(t)·ε(t). None of
the four proposals requires touching the planner.
