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
