# The active-inference driver model — a handbook. Chapter 0: reading guide

*Part of the WaymoActiveInference understanding pack. Markdown is the source of truth;
the Word and PDF versions are generated from it (`docs/handbook/build_handbook.py`).
Draft for comment, 2026-08-22; revised 2026-08-23.*

{{R1}}**Revision marks.** Passages in dark red were changed on 2026-08-23, after a review of the
published method against its released code and data (`docs/method_review.md`). The review
found that the authors' code differs from the Supplementary Information in several
places (the inverse-tau term is one-sided, the off-road cost is −15000, the
control-effort term has a different form), that the surprise signal is far from zero
during ordinary following in the authors' own runs, and that the paper's worked example for
the rear-end scenario does not represent the authors' deposited data. The handbook's
text has been corrected where it relied on the SI or on that example; the corrections are
marked so that a reader of the 2026-08-22 draft can see what moved.

{{R2}}**Revision round 2.** Passages in dark blue were added on 2026-08-25, after the
crash-causation study (`docs/crash_causation_plan.md`, `docs/crash_causation_results.md`)
turned several of chapter 08's proposals into built and tested machinery. The main
lessons folded back in: the dormant gaze system has now been exercised in the closed loop,
and it gates *evidence*, not *inference* — a driver who has registered the conflict keeps
accumulating toward a response during an off-road glance (chapters 06 and 08); the model
can be dropped into externally defined scenarios by replaying a recorded lead vehicle
(chapter 04); a cheap open-loop surrogate of the response timing has been validated
against the closed loop across 23 scenarios (chapters 09 and 12); and the practical cost
figures are revised (chapter 03).

{{R5}}**Status note, round 5 (2026-08-29).** Passages in dark orange are a dated status
correction, not a full revision round: the CZB work has moved decisively since the
chapters were written, and a reader of chapters 04 and 11 would otherwise learn claims
the data have since overturned. In brief: the boundary-level accumulator failed its
pre-registered test (its FAIL is final for the architecture tested); the study-1 cut-in
design turned out unable to distinguish the preference field from a plain gap threshold
(its longitudinal variables are perfectly collinear); and a second, larger cut-in study
that breaks that collinearity ruled **against** the field in a pre-registered comparison
— a simple gap threshold describes the human response surface far better. What survives,
with strong evidence, is the claim one level up: each driver carries a single
comfort-zone level that is substantially shared across scenarios (~69% of the reliable
per-driver signal). The full record is `docs/r2_gate_decisions.md`; the chapters carry
short notes at the affected points. A proper revision round awaits Jonas's review.

## What this handbook is

This handbook explains the active-inference driver model of Schumann et al. (2026, Nature
Communications) — the model this project replicates and builds on — well enough that a reader
can (1) understand how it works, (2) change it deliberately, and (3) follow the argument for
extending it into comfort-zone boundary (CZB) research. It is written for a mixed audience of
traffic-safety analysts and human-factors researchers. The main text of every chapter avoids
mathematics; each chapter ends with layered notes for readers who want the equations.

The handbook is grounded in four kinds of sources, and every substantive claim is tagged with
its provenance:

- **[Paper]** — the published article
- **[SI]** — its Supplementary Information (where most of the actual definitions live)
- **[Code]** — the authors' released code (`external/aica/`), which is the ground truth when
  the paper is ambiguous — {{R1}}and, as it turned out, also when the paper and the SI are
  unambiguous but do not match what the code does (`docs/method_review.md` §5 lists the
  differences)
- **[OSF]** — the authors' own simulation output (`external/gs4bu-osfstorage-archive/`),
  which lets us show real numbers rather than sketches
- **[Speculation]** — our own ideas and proposals, which are ours and not the authors'

## The chapters

| Part | Chapter | One line |
|---|---|---|
| I Getting oriented | 01 Where this comes from | The lineage of the idea, what "free energy" actually means, how it relates to models you already know, and the debate around it |
| | 02 One event through the model's eyes | A single rear-end conflict, told moment by moment with real numbers |
| II The machinery | 03 What the model is | Every component, its inputs and outputs, and the loop that connects them |
| | 04 Scenario playbook | Exactly what changes between scenarios, and the checklist for adding a new one |
| | 05 Normal versus critical | Why the same machinery covers everyday driving and emergencies |
| | 06 Other agents and beliefs | What the other vehicle actually does, versus what the driver model believes it might do |
| | 07 Normative driving | What defines "normal" behavior, and every knob that moves it |
| | 08 Crash causation | What exists today for glances and impairment, and our proposals (marked as such) |
| III Building on it | 09 Modify and validate | Recipes for changing the model, each with its validation ladder |
| | 10 Calibration and parameter fitting | Where every number came from, how to set new ones, identifiability, and the dos and don'ts |
| | 11 The path to comfort-zone boundaries | What exists, what has been tested, what human data would add |
| IV Reference | 12 Code map | From concept to file, class, and parameter — with five first exercises |
| | 13 Glossary | The same idea in three vocabularies, common misconceptions, and {{R6}}the measurement vocabulary (axis, level, gate, held out, noise floor, percentile, trait) in plain words |
| | 14 Appendix: the deep end | The material deliberately kept out of the main text — the free-energy principle proper, variational inference, Markov blankets, the debate literature, the discrete-state formulation — for reference |
| | 15 Appendix: the datasets | Every source a number in this handbook rests on, with the caveat that binds each |
| | 16 Appendix: an external required-deceleration model | {{R6}}Early work, external to the project: a colleague's habitual-control comfort-zone model and its fit to the cut-in study, read against our results |

## Reading paths

- **Thirty minutes, any background:** chapter 02, then the first half of chapter 01.
- **Human-factors readers:** 01 → 02 → 05 → 07 → 08 → 11. Chapter 03 on demand.
- **Analytics / modeling readers:** 02 → 03 → 04 → 06 → 09 → 10 → 12, with the
  chapter-end notes.
- **"I want to change the code":** 03 → 04 → 12 → 09 → 10, keeping 13 open in a second
  window.
- **"I care about comfort zones":** 01 → 02 → 07 → 11, then 10 before fitting anything.

## How the math is layered

Each chapter's main text is **Level 0**: components, inputs, outputs, and behavior, no
equations. At the end of a chapter:

- **Level 1** states the same content with light notation — enough to read the paper's
  figures and follow its argument.
- **Level 2** gives the actual equations with their Supplementary Information numbers, so a
  reader can go from this handbook straight into the SI or the code.

Nothing in a later chapter depends on having read the notes of an earlier one.

## One warning before you start

Two words in this literature do not mean what they usually mean, and misreading them is the
most common way to get lost. **Surprise** is not an emotion here: it is a number measuring
how far what is happening departs from what the model expected. **Preference** is not a
choice: it is a description of the futures a driver treats as normal, encoded so that
wanting something and expecting it become the same quantity. Chapter 13 collects the rest of
these false friends.


---

# Chapter 1: where this comes from

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance tags:
[Paper] article, [SI] supplementary information, [Code] authors' code, [OSF] authors' own
simulation output, [Speculation] our ideas.*

## The idea in one paragraph

Active inference starts from a simple claim: the brain is not a camera followed by a
calculator. It is a prediction machine. It continuously guesses what its senses are about to
report, compares the guess with what actually arrives, and treats the difference — the
surprise — as the thing to get rid of. There are only two ways to get rid of it: change your
mind (update your beliefs until they fit the world) or change the world (act until it fits
your beliefs). The first is perception. The second is action. Active inference says these
are not two systems but one operation running in two directions, and it builds driver models
in which detecting a braking lead vehicle and pressing the brake pedal are, literally, the
same computation.

![The lineage from Helmholtz to this driver model](figures/lineage.png)

## A short history, told through what each step added

**Unconscious inference (Helmholtz, 1860s).** Perception is not passive reception; it is a
guess constructed from expectations plus sensory evidence. A century and a half later this is
uncontroversial in perception science — the visual system demonstrably fills in, corrects,
and predicts.

**The Bayesian brain (1990s–2000s).** The guessing was given arithmetic: beliefs are held
with degrees of confidence, evidence updates them, and less reliable evidence moves them
less. The important word is *reliability* — the framework automatically trusts a clear view
more than a glimpse in fog, without a separate rule saying so.

**Predictive processing (2000s–2010s).** The update arithmetic became an architecture: the
brain runs a generative model — an internal simulation of how the world produces sensations
— and works to minimize prediction error at every level, from retinal input up to "that car
is going to cut in". For driving, this is not an imported idea: *Great expectations*
(Engström, Bärgman, Nilsson, Seppelt, Markkula, Piccinini and Victor, 2018) laid out a
predictive-processing account of automobile driving before the present model line existed.
The way we read it, the Schumann model is the computational instantiation of the account
that paper gave verbally.

**Active inference (2010s, Friston and colleagues).** Predictive processing explains
perception. Active inference adds the second direction: an agent can also reduce prediction
error by acting on the world. The trick that makes this work is the **preference prior**:
the model treats the futures the agent *wants* as the futures it *expects*. A driver who
expects to be traveling safely in their lane, and who finds the world drifting away from
that expectation, will act to pull the world back to it. Goal-seeking becomes
surprise-avoidance, one currency for both.

**This driver model (2024–2026).** The Waymo / TU Delft line (Engström et al. 2024, Wei et
al. 2024, Schumann et al. 2026) turned the framework into a runnable model of human driving
in safety-critical situations: it perceives through optical looming like a human eye,
carries realistic uncertainty about what other road users will do, plans a few seconds
ahead with bounded effort, and — the part this project cares most about — times its
responses by accumulating surprise until action becomes necessary. It reproduces human
response-time patterns in three conflict types, one of which the authors held out entirely
from tuning [Paper].

## "Free energy," demystified in one page

The term that scares people off is *free energy*. What it names is mundane: **a computable
score of how badly your model of the world is doing**, given what you are sensing. High
score, poor fit; low score, good fit. The mathematical object (Level 2 note 1) is a clever
upper bound on surprise that can be computed without knowing everything about the world —
that is its entire job.

The word "energy" is a historical accident: the formula has the same shape as a quantity in
statistical physics, so the name was borrowed. Nothing thermodynamic is meant. No heat, no
calories, no metabolic claim. A reader who mentally substitutes "model-misfit score" for
"free energy" loses nothing in this handbook and, in our experience, most of the model
literature.

Two versions of the score matter, and the split between them organizes the whole model:

- **Present-tense misfit** (variational free energy): how badly current beliefs fit current
  sensations. Minimizing it is perception — the belief update.
- **Future-tense misfit** (expected free energy): how badly a *candidate plan* is expected
  to fit the *preferred* future. Minimizing it is action selection — choose the plan whose
  imagined consequences least depart from the future the driver treats as normal.

## Anchors: models you already know, and where they sit inside this one

The model is best understood not as a rival to the models this audience already uses but as
a container that holds versions of them [Paper] [SI]:

- **Evidence-accumulation / drift-diffusion response models** (Markkula and colleagues). The
  model's response timing *is* an accumulator: a quantity builds up over time and action
  follows when it crosses a threshold. The difference is that the accumulation rate is not a
  fitted constant — it is the moment-by-moment surprise computed from the driver's own
  predictions, so response times automatically depend on kinematics, urgency, and
  expectation.
- **Looming and visual threshold models.** The model perceives the lead vehicle through
  optical size and expansion rate, with a detection threshold on expansion. Detection delay
  therefore *emerges* from perception rather than being a fitted reaction-time constant.
- **Driver risk field / safety-margin models** (Kolekar; our own comfort-zone tradition).
  The preference prior defines a landscape over states — which situations are treated as
  normal and which as increasingly unacceptable. That landscape plays the role of a risk
  field, and chapter 11 argues it can be made to *be* one.
- **Motivational theories** (zero-risk, task-capability interface, task difficulty
  homeostasis). These describe drivers as regulating toward a comfortable region. Here the
  regulation is explicit: the comfortable region is where predicted futures match preferred
  ones and surprise stays near zero.

## The debate: biology, philosophy, or engineering

Active inference arrives with a large and sometimes heated literature attached, and it is
fair for a new reader to ask what they are being asked to believe. The way we read the
field, three distinct claims travel under the same name, and they deserve different levels
of commitment:

1. **A process theory of the brain** — neurons literally implement these computations. This
   is a serious neuroscience program with real but contested evidence. Nothing in this
   handbook depends on it.
2. **A universal principle of life** — every self-organizing system, from cells upward,
   minimizes free energy; in its strongest form this is argued almost as a mathematical
   necessity. Critics respond that a principle compatible with everything predicts nothing,
   and that the strongest versions are unfalsifiable. We do not take a position here, and we
   do not need to.
3. **An engineering framework** — a recipe for building agents that carry uncertainty
   honestly, unify goal-seeking with information-seeking, and time their actions by
   surprise. This is the only claim the driver model needs, and it is testable the ordinary
   way: build the model, benchmark it against human data, hold scenarios out.

The published model is squarely a use of claim 3, and its strongest evidential card is
conventional science rather than grand theory: the intersection scenario was never used for
tuning, and the model still predicted human response patterns there [Paper]. That said, the
framework's critics raise points worth keeping in view even at level 3: with a hand-built
preference function and thirteen tuned parameters, flexibility is real, and "the model can
be made to fit" is a fair worry. The honest defense is held-out prediction and ablation —
remove a mechanism, show the behavior degrades — both of which the paper does and both of
which we can now reproduce from the authors' released data [OSF].

For contrast with the paradigms this audience grew up with:

| Paradigm | The driver is... | Where it differs from active inference |
|---|---|---|
| Stimulus–response / threshold models | a trigger waiting for a cue | no expectations; response times must be fitted per situation |
| Information processing (perceive-decide-act stages) | a pipeline | stages are separate boxes; here perception, decision, and timing share one currency |
| Ecological psychology (Gibson) | attuned to optical invariants | closer than it looks — looming *is* an optical invariant; active inference adds explicit beliefs and preferences behind the optics |
| Optimal control | a perfect planner with a cost function | here planning effort is deliberately bounded, and the "cost function" is a probability distribution, which is what lets surprise time the response |
| Reinforcement learning | a reward maximizer trained by experience | no reward signal exists here; preferences are built in, not learned, and information-seeking comes for free rather than needing exploration bonuses |

Readers who want the deep end — the free-energy principle proper, variational inference,
Markov blankets, and the debate literature on both sides — will find it in chapter 14,
which exists precisely so that this chapter does not have to be longer.

## The permission slip

You can use everything in this handbook — the model, the code, the comfort-zone method —
while remaining entirely agnostic about brains and about universal principles. The model
stands or falls on whether it predicts human driving behavior, which is an empirical
question with published, partly held-out, answers. That is the spirit in which the rest of
the handbook is written.

---

## Notes for the mathematically curious

**Level 1 — the two scores.** Surprise of an observation is its negative log-probability
under the model: rare-according-to-you means surprising-to-you. Variational free energy is
an upper bound on surprise that is computable because it involves only the agent's own
beliefs and its generative model. Expected free energy scores a candidate policy by the
surprise its predicted observations would carry under the preference distribution, plus a
term rewarding observations expected to reduce uncertainty. Action selection picks the
policy with the lowest score; the two terms are the pragmatic and epistemic values that
chapter 03 treats as components.

**Level 2 — the objective.** With beliefs Q(s), generative model P(o, s), and preference
prior P(o):

```
Perception:  minimize over Q:   F = E_Q[log Q(s) − log P(o, s)]      (≥ −log P(o))
Action:      minimize over π:   G(π) = − E[ log P(o_future) ]         (pragmatic value)
                                        − E[ information gain ]        (epistemic value)
```

The preference prior P(o) is where "wanting" enters: it is a probability distribution over
observations in which preferred observations are the probable ones. In the driver model the
distribution is a product of six independent terms (speed, acceleration, steering, lane
position, heading, collision/safety); chapter 07 walks through each. The full forms, with
the collision and safety-margin terms that matter most for comfort zones, are SI §2.4,
Eqs. 44–52 [SI]. This project's `notes/02_active_inference_overview.md` §1–§2 states the
same material with more context, and the derivation-level treatment is in chapter 14.


---

# Chapter 2: one event through the model's eyes

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Every number in
this chapter is read directly from the authors' own published simulation output [OSF]
(rear-end scenario, experiment 7, random seed 0) — nothing is sketched or idealized. The
extraction is `replication/validate_osf.py`; the figure is generated by
`docs/handbook/make_diagrams.py`.*

## The cast

Two vehicles on a straight road. **Our driver** — the model — is following a **lead
vehicle**. Both travel at 10 m/s (36 km/h), with a 10 m gap between our front bumper and
their rear bumper: exactly one second of time headway. The lead vehicle is a puppet: at a
scripted moment it will brake hard, at 6 m/s², down to a standstill. It ignores our driver
completely. Everything interesting in this chapter happens inside our driver's head.

Our driver does not know the script. What it has instead:

- **Senses.** It watches the lead vehicle the way a human eye does — as an optical
  silhouette that sits at some visual angle and grows or shrinks. It does not receive the
  gap in meters or the closing speed in m/s; it receives angles and their rates of change,
  with noise that shrinks as the target gets closer.
- **Beliefs.** A cloud of 75 simultaneous hypotheses about the current state of the world —
  where the lead is, how fast it moves, whether it is accelerating — each hypothesis
  weighted by how well it explains the last observation.
- **Preferences.** A quiet notion of how this drive is supposed to go: cruising near
  10 m/s, pedals and steering mostly still, staying in lane, no collision ever, and a
  safety margin that would still work out even if the lead braked hard.
- **A plan.** A 6-second sequence of intended pedal and steering settings, currently:
  do nothing, keep cruising.
- **A surprise account.** A running total that fills with evidence that the current plan is
  no longer delivering the preferred future — and, crucially, stays at exactly zero while
  the plan still works.

![The event, moment by moment](figures/walkthrough_event.png)

## The event, moment by moment

{{R1}}**t = 0.0 to 0.6 s — nothing happens, and that is almost the point.** Steady following.
The belief cloud tracks the lead within a whisker; the hypotheses about its acceleration
hover around zero. The plan (keep cruising) delivers the preferred future in *most*
rolled-out hypotheses — but not all. The imagined futures carry noise on the lead's
acceleration, and over a 6 s horizon a fraction of them end too close or with a collision,
so each step deposits a non-trivial amount into the surprise account even now: about
68 000 units per step in this condition, which is 7.6% of the re-plan threshold per step
[OSF: `v` components in `Exp_10`; `docs/method_review.md` §4.2]. By the time the lead
brakes, the account already stands at 0.31 of the way to a re-plan. Left alone, this driver
would re-plan spontaneously after about 2.6 s of nothing happening. The *realized* state —
the gap and the speeds as they actually are — is comfortable, and the comfort-zone field of
chapter 11 evaluated on it is exactly zero; it is the *imagined* spread that is not
silent. Keeping these two apart matters for everything that follows.

**t = 0.8 s — the lead starts braking.** The script fires: the lead's deceleration ramps
toward −6 m/s². In the very next belief update, the hypothesis cloud has already snapped to
the new reality — the believed lead deceleration jumps to −2 m/s² with almost no
spread. This is worth pausing on: the model has *detected* the braking essentially
immediately. Detection is not the bottleneck.

{{R1}}**t = 0.8 to 1.2 s — knowing is not yet acting.** The driver knows the lead is braking, but
its plan is still "keep cruising", and a plan is not abandoned just because the world
changed — it is abandoned when it stops delivering the preferred future. Each new step now
rolls the belief cloud forward and finds the planned future degrading: the predicted gap
shrinks, the predicted safety margin erodes, predicted collisions appear among the
hypotheses. The per-step deposit rises from 68 000 to 197 000 and then 267 000 [OSF]. The
account climbs from 0.31 — 0.6 s of "the plan is going stale" that has nothing to do with
sensory sluggishness, on top of the 0.8 s of pre-conflict drift that got it a third of the
way there.

**t = 1.4 s — the account is full: re-plan.** The accumulated surprise crosses its
threshold, and for exactly one timestep the model does the expensive thing: it discards the
stale plan, generates a fresh set of candidate 6-second plans, scores each against the
preferred future across the whole belief cloud, and keeps the best. The winner is
unambiguous — brake, hard. The bottom panel of the figure shows this single re-plan event;
there is precisely one in the whole trial.

**t = 1.6 s — the brake reaches the wheels.** The first step of the new plan executes:
−6.2 m/s². Response time, measured the way the paper measures it: 0.8 s from the lead's
braking onset to our driver's brake onset — of which detection took at most one 0.2 s
step, and essentially all the rest was evidence accumulation. Human rear-end response times in comparable staged conditions sit in the same
range [Paper].

**t = 1.6 to 3.4 s — riding it out.** The lead stops; our driver brakes from 10 m/s to a
standstill, easing off as the margin recovers, and comes to rest **2.05 m** behind the
lead's bumper. No collision, no swerve — at this speed the preference landscape makes
braking the cheap escape and steering the expensive one, which reverses at highway speeds
(chapter 05). After the stop, the pedal trace wanders — the plan is incrementally patched
rather than re-planned, and with both vehicles stationary the preferred future is satisfied
almost no matter what the pedal does. The surprise account has gone quiet again.

## What to take from this

1. **Detection and response are different things, and the model separates them.** The
   belief cloud caught the braking within one step; the response came 0.6 s later, when the
   *plan* — not the world — had accumulated enough evidence of failure. The way we read the
   human-factors literature, this matches it: drivers rarely miss that something moved;
   what takes time is concluding that their current course of action has stopped being
   adequate.
2. **Comfort is a zero, not a small number.** Inside the comfortable region the surprise
   deposit is exactly zero — not merely small — so "leaving the comfort zone" is a
   well-defined event rather than a threshold on an always-positive signal. The entire
   comfort-zone method (chapter 11) rests on this property.
3. **One mechanism produced the whole episode.** Steady following, detection, response
   timing, braking style, and the come-to-rest margin all came out of the same loop —
   sense, believe, predict, evaluate, act, accumulate — with no per-phase sub-model. What
   that loop is made of, component by component, is chapter 03.

## Where each part of the story is explained

| Moment in the story | The machinery behind it | Chapter |
|---|---|---|
| Optical silhouette, noise shrinking with distance | looming perception | 03, 08 |
| The 75-hypothesis cloud snapping to the braking | particle-filter beliefs | 06 |
| "How this drive is supposed to go" | the preference prior | 07 |
| The account that stays at zero | residual information, evidence accumulation | 03, 05 |
| One expensive re-plan | bounded, surprise-gated planning | 03 |
| Brake rather than swerve at 10 m/s | preference landscape vs speed | 05 |
| The silence itself as a measurable boundary | the comfort-zone method | 10 |

---

## Notes for the mathematically curious

**Level 1 — the accumulator.** At each step the model computes how far the expected outcome
of the *current* plan falls short of the best achievable expected outcome under the
preference distribution — a nonnegative quantity called the residual information of the
pragmatic value, written ε(t). It accumulates as E(t) = E(t−1) + λ·ε(t); a full re-plan
fires when E ≥ 1, and E resets. While the plan still achieves the preferred future, ε = 0
exactly, so E does not drift upward during ordinary driving. λ (the paper's evidence-
accumulation factor) is the single most response-time-sensitive parameter in the model
[Paper].

**Level 2 — this trial's numbers.** Trial: `Results_rear_end/Exp_7`, seed 0, Δt = 0.2 s
[OSF]. Lead braking onset t = 0.8 s (scripted countdown in the environment dynamics, ramp
at 10 m/s³ jerk to −6 m/s²). Belief snap: the weighted mean of the 75 particles' lead-
acceleration component moves 0.00 → −2.00 m/s² between t = 0.6 and t = 0.8, with weighted
standard deviation 0.00 — acceleration is directly observed with small noise in this
configuration; the cloud's role is carrying *future* uncertainty, not present-state
uncertainty (chapter 06). Re-plan flag: the executed policy differs from the extended
reference policy only at t = 1.4 s (`a_cont` vs `a_cont_init` in the deposit). First
executed deceleration ≤ −1 m/s² at t = 1.6 s → response time 0.8 s. Final standstill gap
2.05 m (bumper to bumper). The evidence-accumulation equation is Eq. 13 of the paper; the
preference terms it scores against are SI §2.4, Eqs. 44–52 [SI].


---

# Chapter 3: what the model is

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance:
[Paper], [SI], [Code], [OSF], [Speculation] as defined in chapter 0.*

## The loop

Everything the model does happens inside one loop, run five times per second (every
0.2 s). Chapter 02 showed the loop producing an event; this chapter names its parts.

![The perception-action loop](figures/loop.png)

Each pass: sense the world through looming vision, update a cloud of hypotheses about the
current state, roll each hypothesis a few seconds into the future, check the current plan
against the preferred future, execute the plan's next step — and deposit into the surprise
account whatever shortfall the check revealed. When the account crosses its threshold, and
only then, build a new plan from scratch.

## The components, as input → output boxes

**1. The world (the generative *process*).** What actually happens: two vehicles with
bicycle-model physics, a road, and a scripted other vehicle (chapter 06). The driver model
never sees this directly.
*Input:* both vehicles' controls. *Output:* the true state, advanced 0.2 s. [Code:
`dynamics_true.py` per scenario]

**2. The senses (looming perception).** Converts the true state into what a human eye could
report: the other vehicle's optical angle and its rate of change, plus own-vehicle signals
(speed, pedal state, lateral position). Two consequences come free: measurement noise grows
with distance, and expansion below a visual threshold (0.00215 per second [SI]) is effectively
invisible — so detection distance emerges rather than being fitted.
*Input:* true state. *Output:* a noisy observation vector. [Code: `decoder.py`,
`encoder.py`]

**3. Beliefs (the particle filter).** The model's working memory: 75 parallel hypotheses
("particles"), each a complete candidate state of the world, each weighted by how well it
explained recent observations. The cloud's *spread* is the model's honest uncertainty. When
observations are sharp the cloud is tight (chapter 02's acceleration snap); when the other
vehicle's motives are ambiguous the cloud straddles the options — for example "will brake /
will not" as two co-existing particle populations. Between observations the particles are
*moved* by the same norm-shaped transition that prediction uses (component 4) — the swarm
itself leans toward "others will behave", and observations correct it.
*Input:* previous cloud + new observation. *Output:* updated cloud. [Code:
`particle_filter.py`, `encoder.py`, `kde.py`]

**4. Prediction (imagined futures).** Every particle is rolled forward 6 s (30 steps) under
the physics model. The other vehicle's imagined controls are not raw noise: at each step
each particle holds a small tournament among candidate moves, weighted by norm compliance
— futures in which the other vehicle behaves normally (stays in lane, keeps speed) win the
sampling lottery, but only to the degree that its currently observed behavior has earned
that trust. The norms are thus *inside the swarm's motion*, in the belief update and the
roll-outs alike (chapter 06 makes this precise).
*Input:* belief cloud + a candidate plan for our own controls. *Output:* a bundle of
imagined 6-second futures. [Code: `dynamics.py`]

**5. Preferences (the landscape).** A description of how driving is supposed to go,
encoded as a probability distribution over observations: comfortable speeds, gentle pedals,
staying in lane, no collisions, and a counterfactual safety margin — "even if the lead
braked hard right now and I reacted after one second, ordinary braking would still be
enough". Six independent terms, each with interpretable knobs (chapter 07).
*Input:* an imagined future. *Output:* a score of how preferred that future is. [Code:
`reward.py` per scenario; SI §2.4]

**6. The planner (bounded, not optimal).** Holds one current plan — a 6-second control
sequence. Ordinarily the plan is only *patched*: shifted one step and locally re-optimized
cheaply. A full re-plan — propose ~100 candidate plans, score them all against the
preferred future across the belief cloud, refine the best tenth, repeat ~10 rounds — runs
only when the surprise account demands it. The budget is deliberately capped: the planner
sometimes returns a merely decent plan, which is a modeling commitment about humans, not a
bug [Paper].
*Input:* belief cloud, preferences. *Output:* the (kept or replaced) plan; its first step
goes to the vehicle. [Code: `mpc_discrete.py`]

{{R1}}**7. The surprise account (evidence accumulation).** The response-timing mechanism, and the
piece this project reuses for comfort zones. Each step it receives the gap between what the
current plan is now expected to deliver and the best that could be expected — zero only if
every imagined future works out, which in practice it never quite does (chapter 02) —
multiplied by a rate constant and added to a running total. Threshold crossed → full
re-plan → total resets.
*Input:* the plan's scored shortfall. *Output:* the re-plan trigger. [Paper Eq. 13]

## Two currencies, one ledger

The scoring in component 5 has two parts, and their shared currency is the framework's
main selling point:

- **Pragmatic value** — how well an imagined future matches the preferred one. This is
  goal-seeking: progress, comfort, safety margins.
- **Epistemic value** — how much an imagined future is expected to *teach* the model, by
  reducing the belief cloud's spread where it matters. This is information-seeking:
  looking, probing, easing off to see what the other driver does.

Both are measured in the same units and simply added, so caution and progress trade
against each other without an arbitration rule. In the published collision-avoidance runs
the pragmatic part dominates [Paper]; the epistemic part is the natural hook for glance
behavior and uncertainty-driven slowing (chapter 08).

## What is deliberately human about it

| Design choice | The human claim behind it |
|---|---|
| Looming instead of range sensors | drivers see angles, not odometry; distant threats are genuinely harder to perceive |
| A particle cloud instead of one estimate | drivers entertain multiple readings of an ambiguous scene at once |
| Norm-shaped prediction | drivers expect others to behave; trust is withdrawn when observed behavior stops earning it |
| A capped planning budget | drivers satisfice; an optimal planner reproduces the wrong behavior |
| Surprise-gated re-planning | drivers do not continuously re-decide; they act when evidence has built up that they must |

## What it is not

- It is **not learned from data**: no training set, no fitted network. Thirteen parameters
  were hand-tuned [Paper]; the rest is structure.
- It is **not an optimal controller**: bounded planning, noisy perception, and normative
  trust are all deliberate departures.
- The other vehicle is **not intelligent**: it follows a script and never reacts to our
  driver (chapter 06). There is no negotiation or interaction in the published model.
- It is **not fast**: the code is written for GPU, and on CPU one simulated timestep of a
  batched run has cost us anywhere from under a second to tens of seconds. {{R2}}Revised
  after the tier-2 campaign of 2026-08-24/25: a 45-step scenario with four parallel
  repeats has taken between 3 minutes and 4 hours on this machine, median around 10
  minutes in uncontended runs — wildly variable, with no clean predictor. Plan batches as
  restartable and measure before extrapolating. Everything in this project's comfort-zone
  method still avoids running the loop (chapter 11).

---

## Notes for the mathematically curious

**Level 1 — the loop as equations in words.** Perception: particle weights are multiplied
by the likelihood of the new observation under each particle, then normalized; particles
are refreshed by resampling when weights degenerate. Prediction: particles are pushed
through the bicycle dynamics with control noise on the other agent, reweighted by
norm-compliance (chapter 06, Level 2). Planning: cross-entropy method over control
sequences — sample, score by expected free energy, keep the elite fraction, refit the
sampling distribution, iterate. Acting: execute the first control of the incumbent plan.

**Level 2 — sizes and references.** Δt = 0.2 s; horizon H = 30 (6 s); particles N = 75;
CEM: 100 candidate plans, elite fraction 0.1, ~10 iterations; looming threshold
0.00215 s⁻¹; evidence accumulation E(t) = E(t−1) + λ·ε(t), re-plan at E ≥ 1 (Paper
Eq. 13). Observation model and looming transform: SI §2.2; belief update §2.3; preference
terms §2.4 Eqs. 44–52; planner §2.5 [SI]. Parameter values as shipped: the OSF deposit's
`Setups_*.xlsx` (65 columns per run) [OSF]. Our independent NumPy re-implementation of
components 3–7 is `src/aidriver/` — faithful to the SI for preferences, not yet trusted
for closed-loop response timing (`notes/05_validation.md`).


---

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
free-following study rather than shared [SI]. {{R1}}The calibration table shipped with the
code covers steady-state headways only up to about 1.0–2.1 s depending on speed, so for
most of the paper's own rear-end conditions the lookup saturates at the most pessimistic
value, −8 m/s² [Code: `Analysis_following.xlsx`; `docs/method_review.md` §6.2]. This is a
property of the authors' published runs as much as of ours; it does not, as an earlier
draft of this chapter said, explain a difference between our replication and theirs,
because there is none.

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

{{R2}}**A shortcut demonstrated since (2026-08-25): replaying recorded scenarios.** When the
new "scenario" is a set of externally defined trajectories rather than a scripted world —
recorded conflicts, generated seed scenarios — the other vehicle's script (step 2) can be
replaced wholesale by a *replay* of its speed profile, leaving the driver and its
generative model untouched. The crash-causation study did exactly this to run the model
on the QUADRIS rear-end seeds (`replication/causation/tier2_rear_end.py`: a dynamics
subclass swapped into the loaded module, the authors' files unedited). Two lessons came
with it. First, external seeds force a **desired-speed decision**: the driver's desired
speed must be set from the data (this project's convention: the speed the recorded
follower later reached), or a stopped follower has no motive to move at all. Second,
count **road departures** as their own outcome class from the start — the high-speed
lane-change failure mode of chapter 05 appears in replayed scenarios too.

## The three files, line by line

{{R3}}*Added 2026-08-26 from a line-level diff of `src/rear_end_test/`, `src/oncoming/` and
`src/intersection/` in the authors' code [Code]. The summary above says what changes; this
section says exactly where, because the next scenario we add will be written by editing
these three files and it matters which lines are the scenario and which are the driver.*

![What is shared and what changes when a scenario is added](figures/scenario_diff.png)

{{R3}}The chart above is the whole of this section in one picture: the shared core is never
touched, `decoder_true.py` is identical across all three released scenarios, the bulk of the
code volume sits in the other vehicle's script, and the scenario's actual content is three
places inside `reward.py`. It is generated by `docs/handbook/make_scenario_diagram.py`.

{{R3}}**A naming trap first.** The intersection scenario's files are called *side* at top
level (`simulation_side.py` sets `name = 'intersection'`, and `Analysis_side.py` analyzes
it) but *intersection* inside `src/`. Searching for one name finds half the code.

{{R3}}**`decoder_true.py` — identical in all three.** This is worth stating plainly because
it is easy to assume otherwise: the three versions differ by exactly three lines, all of
them **docstring**, where the rear-end version documents two extra state variables
(`t_brake_tar`, `j_brake_tar`) belonging to its target's brake script. There is no
functional difference. How the world becomes observations — the looming transform, the
noise model, the gaze gate — is scenario-independent in the released code. The only thing
that can make it scenario-dependent is the *vehicle dimensions* it is constructed with,
since looming angle depends on the target's width.

{{R3}}**`dynamics_true.py` — where nearly all the code volume is, and none of the driver.**
The three versions are 162, 354 and 665 lines (rear-end, intersection, oncoming). That
four-fold spread is entirely the other vehicle's script:

| scenario | what `forward_state_tar` does | supporting machinery |
|---|---|---|
| rear-end | counts down to `t_brake_tar`, then ramps deceleration at `j_brake_tar` | none — it is a few lines of arithmetic |
| intersection | steers the target through the turn geometry | `tar_loss`, `get_tar_steering_rate`, `load_steering_rate` — solves for the steering rate that tracks the intended path |
| oncoming | drives the target along a synthesized incursion trajectory | `propagate_forward`, `cost_function`, `ctrl_gradient_descent`, `optimize_control_part` — a full gradient-descent optimal-control solve |

{{R3}}**The trap in this file is the word "cost".** `src/oncoming/dynamics_true.py` contains
a function called `cost_function`, and it has nothing to do with the driver's preferences.
It is the scenario author's own objective, penalizing deviation of the target's lateral
position from a reference path (`y_needed_ref`) plus a terminal state mismatch, minimized by
gradient descent to manufacture a smooth incursion that reaches the scripted intrusion depth
at the scripted moment. Reading it as part of the driver model would be a serious
misunderstanding — it is stage machinery, not psychology.

{{R3}}**`reward.py` — the driver's preferences, and the only file where the scenario changes
the driver.** The three versions differ in exactly three places, and it is worth knowing
which:

{{R3}}**(1) The lane-geometry mapping, in `compute_features`.** A handful of lines that turn
a raw lateral coordinate into "how far am I from where I should be". Rear-end and
intersection share one version, which treats the ego as being in a two-lane road with a
viable lane to the left and snaps near-zero offsets to exactly zero. Oncoming needs a
different one because the lane to the left is the *oncoming* lane rather than a free
overtaking lane, so it distinguishes `in_other_lane` from `left_lane` and maps them
separately. This is the "draw the lane structure into the preferences" step of the checklist
below, and it is roughly six lines.

{{R3}}**(2) A lane-change bookkeeping block that exists only in rear-end.** About twenty
lines that track how long the ego has been between lanes, add a heavy penalty for an
*aborted* lane change (returning to the lane it started in after more than 1.5 timesteps of
straddling) and a growing penalty for dwelling between lanes beyond nine timesteps. Both
oncoming and intersection simply delete this. As we read it, this is hand-built shaping
rather than principle — a patch to stop the planner from discovering that hovering on the
lane line is comfortable — and it is the least principled code in the three files. Anyone
porting the model should know it is there and decide deliberately whether to keep it.

{{R3}}**(3) `get_weights` — the norms, and the real scenario content.** This function is the
driver's prior over what the *other* vehicle will normally do; the dynamics call it as
`normative_probability` when propagating beliefs about the target (chapter 06). All three
versions differ completely, and the progression is instructive:

| scenario | what counts as normal behavior for the other vehicle |
|---|---|
| rear-end | position only: in its lane, weight 1; just outside, `weigh_particles`; off road, `weigh_particles × full_violation_factor` |
| oncoming | position (relative to the *oncoming* lane centre) **and speed** — a quadratic speed norm, `1 − 2.25·(v/v_mu − 1)²`, folded in by a minimum, with the code's own comment "consider breaking to be norm violating similar to off lane" |
| intersection | a two-dimensional road-geometry mask, including a quarter-circle corner of radius `10 + ½·lane_width + ½·l`, **plus** a term that down-weights the target running the red light |

{{R3}}So the driver's assumption about what other road users do gets richer as the scenario
gets more structured: stay in your lane, then also keep your speed, then also stay on the
road and obey the light. This is where the modeling judgment lives, and it is written by
hand each time — there is no map format and no norm library.

{{R3}}**Two smaller differences.** Rear-end's version keeps several selectable looming-reward
variants (`V2`–`V7`, and a non-looming fallback) where the two lateral scenarios hardcode
`V7`; and oncoming guards its braking-feasibility term with a check that the two vehicles
are actually travelling in the same direction, which rear-end does not need. Parameters are
almost entirely shared, with `lane_width` = 3.65 m in rear-end and oncoming against 3.5 m in
intersection, and the one driver-side change already noted above (`w_sd_model`).

## What a cut-in scenario would take

{{R5}}*Status note (2026-08-29): this section was written ahead of the construction; the
construction has since been built, fitted, and tested. The stimulus-side field exists
(`src/comfortzone/cutin.py`, continuous lane entry, S-shaped ramp with k = 12), the
boundary was fitted on the study-1 responses, and a second cut-in study then ruled the
field's kinematic content **out** in a pre-registered comparison against a plain gap
threshold. The section stands as a record of the construction reasoning; the outcome and
its consequences are in chapter 11's status note and `docs/r2_gate_decisions.md`.*

{{R3}}*Added 2026-08-26, ahead of implementing it. The cut-in is the next scenario, driven by
the clip-rating and button-press dataset described in `docs/czb_study1_data_plan.md`
[Repo].*

{{R3}}**`decoder_true.py`: probably unchanged, with one thing to verify.** Since the file is
already scenario-independent, the cut-in inherits it. The check that matters is whether the
looming machinery behaves for a target that is *partially* in our lane. A cut-in target
straddles the lane boundary for 2.4–2.6 s in the recorded clips, which is a state none of
the three existing scenarios sustains: the rear-end lead is always ahead in lane, the
oncoming vehicle crosses quickly, the crossing vehicle is lateral throughout. `Length_m` for
truck assets is zero in the new dataset's traces, so dimensions must be supplied explicitly
for the truck cut-ins regardless.

{{R3}}**`dynamics_true.py`: two routes, and we would take the cheap one first.** The
principled route is to adapt oncoming's incursion optimizer — a cut-in is the same
manoeuvre with the target travelling in the same direction rather than opposing, completing
the lane change rather than partially intruding, and triggered on gap or TTC. Most of that
665-line file transfers. The cheaper route is the replay shortcut described above: the new
dataset supplies recorded trajectories for every stimulus clip, so the target's script can
be a replay and no optimizer is needed at all. For the comfort-zone work the replay route is
sufficient and is what we would build first; the optimizer earns its cost only if we want to
generate cut-ins that were never recorded.

{{R3}}**`reward.py`: the three decisions, of which one is genuinely new.** The lane-geometry
mapping can be rear-end's unchanged — the ego is in its lane with a free lane to the left,
which is exactly rear-end's world. The lane-change bookkeeping should also be kept, since an
evasive lane change is available to the ego in a cut-in just as it is in a rear-end conflict.
The norms are the new work. A cut-in demands something none of the three existing
`get_weights` functions has: a norm that is **time-dependent on the other vehicle's
manoeuvre progress**. A vehicle in the adjacent lane is normal; a vehicle straddling the
boundary is *transiently* normal, because a lane change is a legal manoeuvre, but only for a
plausible duration; a vehicle that has completed the change is normal again, but now at a
headway that must itself be judged. Rear-end's norm is purely positional and would score a
straddling vehicle as a violation throughout; intersection's is geometric; oncoming's adds
speed but not progress. Writing this term is, to us, the scientific content of the cut-in
scenario, and it is where we would expect the argument in any write-up.

{{R3}}**The dials.** `w_sd_model` should start from the lateral scenarios' 0.4575 rather than
rear-end's 0.0045 — a cut-in target steers by definition, and this is the number that tells
the driver a lane change is something the other vehicle might do. The assumed worst-case
deceleration behind the safety-margin term needs re-calibrating for the cut-in context, with
the coverage check that our replication tripped over. Both belong to items 6 and 7 of the
checklist.

## The cut-in's open problem: making lane entry continuous

{{R3}}*Added 2026-08-26 after running the first cut-in predictors against the study traces.
This is the outstanding design question for the scenario and should be settled before any
fitting; Jonas asked that it be recorded as important and returned to.*

{{R3}}**The symptom.** Running the released preference function unchanged over two cut-in
stimuli that differ greatly in criticality — TTC4, with a 10.2 m gap at manoeuvre onset, and
TTC8, with 21.3 m — produces almost identical comfort-zone pressure, and it moves as a *step*
rather than a ramp. Decomposing the six preference terms shows why. The speed term sits at a
constant −483 in both, because the stimulus ego travels at 30.5 m/s while the default desired
speed is 15 m/s; that is a scenario-staging error, fixed by setting the desired speed from
the clip. The interesting failure is the safety term, which is exactly 0 before the target
enters the lane and exactly −2112 after, **identically for both criticality levels**. Only the
collision term discriminates them at all, and it is two orders of magnitude smaller.

{{R3}}**The cause is not really a bug.** The safety term asks "if the other vehicle did its
worst, could I still stop?" At 30.5 m/s with the assumed worst-case deceleration and reaction
time, the answer is no at 10 m *and* no at 21 m — both cut-ins end at a time headway under
0.75 s. The term is correct and saturated. What it cannot do is express *degrees* of
unsafety once saturated, and it only switches on when a binary test says the target is in the
ego's lane. A cut-in spends 2.4–2.6 s partially in the lane, and that entire continuum is
invisible.

{{R3}}**What the continuous replacement should be.** Our view, offered for argument rather
than as a conclusion. The physically honest quantity is not the lane test but **lateral
overlap**: the fraction of the two vehicles' widths that coincide laterally, which runs
smoothly from 0 to 1 through the manoeuvre and is exactly what determines whether a
longitudinal closure can become a collision. Weighting the collision and safety terms by that
fraction removes the step without adding a threshold.

{{R3}}That handles the present state. The more interesting half is predictive, and it is
where a cut-in genuinely differs from the released scenarios: a driver responds to a cut-in
*before* the vehicle is in the lane, on the expectation that it will be. The natural
predictive quantity is the **time until lateral overlap begins**, τ_lat = |Δy_edge| divided by
the lateral closing rate — Jonas's "predicted time to in-lane". A collision requires lateral
overlap to have begun by the time the longitudinal gap closes, so the quantity that should
drive the response is the *comparison* of two times: τ_lat against the longitudinal
time-to-collision. When τ_lat is much shorter, the cut-in is effectively already complete and
the situation is a following conflict; when τ_lat is much longer, the ego passes before the
target arrives and there is no conflict; the interesting region is where they are comparable,
and a smooth function of their difference gives a graded response that is monotone in both
criticality and manoeuvre progress — which is what the data show.

{{R3}}**Why lane-change duration is not the right variable**, consistent with the QUADRARUM
group's finding that it did not matter empirically: duration is a property of the manoeuvre
in isolation, whereas what a driver is exposed to is the lateral closing rate *relative to*
the longitudinal closing rate. A slow lane change into a large gap and a fast one into a
small gap can share a duration and pose entirely different problems. Formulating the term as
a comparison of τ_lat with the longitudinal TTC captures that; formulating it in terms of
duration cannot.

{{R4}}**Status: settled and implemented 2026-08-27.** The full argument is
`docs/lane_entry_note.md`; the short version is that the binary gates are replaced by the
lateral overlap fraction *predicted at the moment of longitudinal closure* (projecting the
lateral offset forward at its closing rate over the longitudinal TTC, clamped at
centering), and the saturated safety magnitude by the relative speed that would *remain at
impact* under maximal braking. Both are parameter-free, both reduce exactly to the released
forms in every geometry the released scenarios sustain, and both are flag-gated in
`src/aidriver/preferences.py` (default off, so every published number is untouched). On the
study's clips the field goes from one indistinguishable step to ramps ordered by
criticality at every truncation point (`figures/cutin_field_check.png`). The note also
argues the reading on which this is not a departure from the model at all: the closed loop
already grades lane entry continuously, through rollouts that sample the other vehicle's
steering; the continuous forms are that expectation written in closed form for the
rollout-free field. One consequence worth knowing: the mild truck cut-ins have zero dread
deficit throughout the response window, so the comfort-dread distinction becomes essential
to the fitting (see the note's section 5).

{{R3}}**One caution carried over from the data.** In the new dataset the participant's
instruction differs by scenario — intervene against a cut-in, abort an overtake, yield
rather than turn — so the preference terms that should drive a boundary crossing are not the
same across scenarios. A cut-in crossing should be driven by the longitudinal safety and
collision terms; an overtake abort by the lateral clearance term. Pooling them under one
scalar without accounting for this seems to us the most likely way to produce a misleading
negative result in the transfer test.

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


---

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
  this only because they start 0.8 s before the lead brakes. {{R2}}How much this
  pre-conflict drift matters for response timing has since been measured (2026-08-25):
  for simulation windows that open a few seconds before a conflict at ordinary headways,
  very little — the closed loop's onsets match a drift-free surrogate that starts its
  account at zero to a median 0.30 s across 23 scenarios, and a
  "driver-arriving-mid-cycle" half-threshold start over-corrects by a second
  (`docs/crash_causation_results.md` §5). The drift is a real property with small
  near-conflict consequences; designs with long benign run-ins are where it would bite.
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


---

# Chapter 6: other agents, and what the driver believes about them

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance tags
as in chapter 0. This chapter answers question (e) of the project brief: what defines what
the other vehicles are doing — including whether the particle filter is how it is done.*

## Two completely different questions, easily conflated

"What is the other vehicle doing?" has two answers in this model, produced by two
unrelated pieces of machinery, and keeping them apart is the key to reading the code and
the paper correctly:

1. **What the other vehicle actually does** is decided by a *script* — simple,
   deterministic, and entirely outside the driver model.
2. **What the driver believes the other vehicle is doing and might do next** is decided by
   the belief machinery — a particle swarm whose own motion is norm-shaped, serving both
   the tracking of the present and the imagining of futures.

The particle filter is *not* how the other vehicle's behavior is generated; it is how the
driver's uncertainty about that behavior is represented. The script answers question 1;
the particle filter and the prediction roll-outs answer question 2.

## Side one: the script (the truth)

Each scenario's `dynamics_true.py` [Code] contains the other vehicle's entire behavioral
repertoire, and it is deliberately primitive:

- **Rear-end:** drive at constant speed; when a countdown expires, ramp braking to a
  scripted intensity; stop. The intensity and timing are condition parameters swept across
  runs [OSF].
- **Oncoming:** drive straight in the opposite lane; when time-to-collision falls below a
  trigger, steer into our lane to a scripted intrusion depth. The incursion trajectory is
  computed by a small optimizer so it hits the scripted depth at the scripted time — a
  fancier script, but still a script [Code].
- **Intersection:** approach or wait at the junction; on a trigger, turn across our path.

Three properties matter more than the details. The script **never reacts to our driver** —
no negotiation, no yielding, no eye contact; every published result is about unilateral
avoidance, and any interaction study would need this replaced [Paper]. The script is
**where a scenario's difficulty lives** — sweeping its intensity and timing generates the
condition grids. The script is **invisible to the driver**, who meets it only through
optics.

## Side two: the beliefs (the driver's honest ledger)

**The present: a cloud of 75 hypotheses.** The particle filter maintains 75 complete
candidate states of the world — each one a full "it could be like this": positions,
speeds, headings, and, crucially, the other vehicle's current acceleration and steering.
Each observation re-weights the hypotheses by how well they explain it; hypotheses that
keep failing get culled and replaced near ones that succeed. The cloud's spread *is* the
model's uncertainty — no separate confidence number exists.

Between observations, each particle is *moved* by the norm-shaped transition described in
the next section — the swarm drifts toward "that vehicle will keep behaving", and each
arriving observation then corrects the drift toward what actually happened. Chapter 02
showed the resulting subtlety: in the rear-end configuration the observation channel is
sharp enough that the cloud tracks the present tightly (the believed lead deceleration
snapped to the truth in one step). The cloud earns its keep elsewhere — under ambiguity.
When an oncoming vehicle wanders near the lane line, hypotheses compatible with "drifting
but staying" and "beginning an incursion" coexist with real weight on both, and the
driver's planning sees *both* futures. A single-best-estimate tracker is structurally
unable to be of two minds; the particle cloud is of two minds routinely, which we read as
one of the model's most human features.

## Where the norms live: inside the particle swarm's own motion

This section exists because it answers a question we ourselves initially got only half
right, and which one of the authors (Engström, personal communication, 2026-08) pointed
to: the normative machinery is not a layer applied *on top of* predictions — **it is
built into how every particle moves**. We have verified the following against the code
line by line [Code], and it holds for the belief update and the planner alike, because
both are served by literally the same transition object
(`src/common/dynamics.py::forward_tar_agent`; attached to the norm weights once, in the
simulation setup).

Whenever any particle's picture of the other vehicle has to advance by one timestep —
which happens both when the belief cloud is updated between observations and when
futures are imagined during planning — the particle does not simply add random noise to
the other vehicle's controls. It runs a **mini-tournament**:

1. Propose 32 candidate next moves for the other vehicle (its current controls plus
   random variation, sized by the `a_sd_model` / `w_sd_model` dials).
2. Score each candidate by norm compliance in three snapshots: where the vehicle *is*
   now, where the candidate puts it *one step* ahead, and where the candidate would put
   it *four seconds* ahead if held. The "soon" and "later" scores are averaged; the
   overall score is the *worse* of "now" and "that average" — a candidate that looks
   fine now but drifts off the road later is tainted by its future.
3. Draw **one** winner by lottery, with tickets proportional to the scores. That winner
   becomes the particle's next state.

So a compliant lead vehicle's particles overwhelmingly "choose" futures that stay in
lane at speed — the swarm itself leans normative. This is, we believe, exactly what
"the normative part is included in the particle swarm" means: norms are the sampling
bias of the swarm's own dynamics, not a filter applied afterward.

![The norm tournament, with the bias on and off](figures/norm_tournament.png)

**The trust cap falls out of the same arithmetic, elegantly.** The "now" score in step 2
is the same for all 32 candidates — it describes where the vehicle already is, which no
candidate can change. While the vehicle is behaving normally that shared score is high,
so the *differences* between candidates (their futures) decide the lottery, and the
normative bias bites (left panel of the figure: the biased fan hugs the lane while raw
noise sprays). The moment the vehicle is observed grossly misbehaving, the shared "now"
score collapses, becomes the ceiling for every candidate at once, and the lottery goes
momentarily near-uniform: the bias dissolves and the swarm fans out over everything the
vehicle could physically do. Trust is not a separate mechanism with its own parameter;
it is the min() in step 2 doing its work. Revoked on evidence, within a step or two.

The right panel shows a second-order consequence we verified in the arithmetic and think
is worth knowing: for a violating target the fan opens, *and* it leans back toward the
lane — any hypothesis that wanders back into the normal region regains its bias and is
recaptured. The swarm simultaneously entertains the long tail and expects the violator
to eventually return to normality, which strikes us as a rather human expectation to
hold [Code, our reading].

**The same tournament, two different jobs.** In the *belief update* the tournament runs
for one step and is immediately corrected by the next observation — so norms gently
shape where the cloud drifts between glances at the world, and reality has the last
word. In *planning roll-outs* the tournament runs 30 steps with no observations to
correct it — so norms shape the entire 6-second fan of imagined futures, which is where
they influence decisions. One mechanism, two exposures; the second is where the
behavioral consequences (relaxed following, late-but-not-too-late alarm) come from.

{{R2}}A third exposure has since been demonstrated (2026-08-25): **coasting through an
occlusion**. When the observation channel is degraded — an off-road glance, forced
through the code's own gaze gate — the same norm-shaped transition carries the cloud
forward essentially uncorrected, and everything downstream keeps consuming it: a driver
who saw the lead start to brake and then looked away keeps *inferring* the conflict's
development from the coasting belief, keeps accumulating evidence, and can commit to
braking mid-glance. The belief machinery is not a passive sensor buffer; it is a
short-horizon simulator that runs with or without fresh input, with behavioral
consequences chapter 08 spells out.

Two dials size the raw variation the tournament chooses among (`a_sd_model`,
`w_sd_model`): how much acceleration and steering wobble the driver attributes to
"vehicles in general". Chapter 04 showed the steering dial is the one number that
distinguishes the driver across scenarios (0.0045 for a queueing lead, 0.4575 for
oncoming and crossing traffic) [OSF]. Without the tournament, raw noise alone would
make the driver either paranoid (every future includes wild swerves) or oblivious
(noise too small to cover real incursions); the norm bias with its built-in trust cap
is the model's resolution of that dilemma [Paper].

## Why this arrangement is worth copying

- **Detection speed comes from expectation violation, not from tuned vigilance.** The
  driver is relaxed precisely because compliant futures are weighted up; it becomes alert
  precisely when compliance visibly fails. One mechanism covers both, with no
  free "alertness" parameter.
- **The uncertainty is decision-grade.** The same cloud that represents "they might brake
  / might not" is what plans are scored against, so caution scales automatically with
  genuine ambiguity — no hand-tuned safety buffer.
- **The seams are explicit.** Everything the driver assumes about others is localized in
  three places: two noise dials, one norm geometry, one trust cap. Chapter 09 uses
  exactly these seams for modifications (an inattentive-driver prior, a trusting-driver
  variant, a pedestrian norm set).

## The limits, stated plainly

The other agent has no mind: it does not perceive our driver, and the driver's model of
it contains no recursive "they see me seeing them". Cooperative and communicative
phenomena — gap negotiation, hesitation reading, signaling — are outside the published
model's scope [Paper]. The norms are hand-drawn per scenario, which is honest but does
not scale; learning them from data is, in our view, one of the most natural extension
projects this line offers [Speculation].

---

## Notes for the mathematically curious

**Level 1 — the filter.** Standard sequential importance resampling: predict each
particle through the dynamics, weight by observation likelihood, normalize, resample on
weight degeneracy. Later papers in the line replace raw particles with a kernel-density /
Gaussian-mixture representation so beliefs can move outside the initial particle support.
Prediction for planning: for each particle, sample other-agent control noise, roll the
joint state 6 s; the resulting bundle approximates the predictive distribution over
futures conditional on our candidate plan.

**Level 2 — the tournament as implemented** (`src/common/dynamics.py::forward_tar_agent`,
verified 2026-08-22) [Code]. Per particle and per transition: draw `N_norm` = 32 control
perturbations ~ N(0, `a_sd_model`/`w_sd_model`), scaled by `noise_pred_fac` = 0.2 when
called in prediction mode; for each candidate compute compliance weights from the
scenario's norm geometry (`reward.py::get_weights`) at the current state (w_now — note:
identical across candidates), one step ahead (w_next), and `H_norm` = 20 steps ≈ 4 s
ahead under held controls (w_long); combine w_future = harmonic mean(w_next, w_long);
overall w = min(w_now, w_future); normalize over the 32 candidates and sample one index
from the categorical — the sampled candidate becomes the particle's next target state.
Compliance weights: 1 inside the normal region, `weigh_particles` = 0.001 marginally
outside, times `full_violation_factor` = 0.01 for gross violations [OSF]. The trust cap
is the min() with the candidate-independent w_now: once w_now < w_future for all
candidates, every candidate carries the same weight and the categorical is uniform —
the bias vanishes without any dedicated switch. The same `Dynamics` instance is passed
to both the `Encoder` (belief update; one call per step, observation-corrected via the
KDE update) and `BeliefDynamics` (planner roll-outs; 30 uncorrected calls per imagined
future); the norm weights are attached once via `add_reward_function` in the simulation
setup [Code, `src/utils/simulation.py`]. Oncoming's norm set additionally treats speed
deviation as non-compliance (a braking oncoming vehicle is "abnormal"), chapter 07 [Code].


---

# Chapter 7: normative driving — what defines "normal", and every knob that moves it

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance tags
as in chapter 0. This chapter answers question (d) of the project brief.*

## "Normal" appears twice, and they are different objects

The model contains two separate definitions of normal driving, implemented in different
places, doing different jobs:

- **The driver's own normal** — the preference prior: how *my* drive is supposed to go.
  This shapes what the driver does. It is the comfort-zone object.
- **Normal for the others** — the norm geometry of chapter 06: what *that other vehicle*
  is expected to do. This shapes what the driver predicts, hence when it worries.

Question (d) — "how is normative driving defined for the individual scenarios, in detail"
— needs both answers. We take them in turn.

## Part A: the driver's own normal — six preference terms

The preference prior is a product of six independent terms [SI §2.4]. Each term is a
distribution over one observed quantity: it says which values are treated as unremarkable
and how quickly departures become objectionable. Because the terms multiply, the model's
"how the drive should go" is simply the six read together — and because they are
independent, every exceedance can be attributed to the term responsible (the property the
comfort-zone method exploits, chapter 11).

| Term | Plain meaning | The knobs | Turning them does |
|---|---|---|---|
| **Speed** | I intend to travel near my desired speed | desired speed; tolerance (sd 0.5 m/s) | tighter tolerance → speed held more rigidly, stronger urge to return to it after braking |
| **Pedal effort** | acceleration should be mostly gentle | tolerance (sd 0.1 m/s²) | smaller → smoother driving, later/harder emergency trade-off felt |
| **Steering effort** | the wheel should be mostly still | tolerance (sd 0.02 rad/s) | smaller → steering escapes score worse, braking favored |
| **Lane position** | stay centered in a real lane | lane geometry; lane-change cost; road-leave cost | the scenario-shaped term — see below |
| {{R1}}**Closing rate** (inverse-tau) | do not close on the vehicle ahead faster than a TTC of about 5 s | preferred inverse-tau level and width | one-sided in the released code: closing slower than that, holding the gap, or falling back costs nothing, so this term bounds the *approach rate* and does not shape the following distance itself [Code: `reward.py`; the SI's symmetric form would, and an earlier draft of this row said so] |
| **Collision & safety margin** | collisions are unacceptable, scaled by severity — and so are states from which only heroic braking would save me | collision cost; severity floor; assumed worst-case lead braking; assumed own reaction time (1 s) | the comfort-zone term — see below |

![The six preference terms](figures/preference_terms.png)

Three of the six deserve a longer look.

**The lane term is where scenarios differ.** "Centered in my lane" requires knowing what
lanes exist and which direction they serve; that geometry is hand-drawn per scenario
[Code]. Rear-end's road adds explicit costs on dawdling between lanes or aborting a lane
change — hand-built craftsmanship, not derived theory, and worth knowing about before
attributing its effects to deep principles [Code]. There is no map format: a new road
means drawing new geometry (chapter 04, checklist item 4).

**The closing-rate term defines everyday tailgating comfort.** It is easy to overlook —
the article barely mentions it — but without it the model would happily sit at a tiny,
technically-safe gap. It encodes "being close and closing feels wrong before it is
dangerous", which the way we read it is the first appearance of a comfort-zone boundary
inside the model, distinct from the safety margin [SI].

**The safety-margin term is a counterfactual, and its assumptions are the boundary's
location.** It scores the present state by a what-if: *if* the lead braked at an assumed
worst-case level *and* I responded only after an assumed reaction time, would ordinary
braking still suffice? Both assumptions are parameters — the assumed worst case is
calibrated per scenario [SI], and any absolute number quoted from this term (a critical
headway, a boundary THW) inherits them. This project's standing rule: never report a
boundary value without stating both (`HANDOFF.md` §7).

## Part B: normal for the others — the three scenarios in detail

The norm geometry that chapter 06's prediction machinery consumes, read directly from the
code [Code]:

- **Rear-end.** Normal = the lead staying within the lane's width. Graded: fully normal
  in-lane; a small factor when marginally outside; a much smaller factor further out.
  Nothing about speed — a lead may brake without becoming "abnormal", which is consistent
  with braking leads being the scenario's whole point.
- **Oncoming.** Normal = staying in *its own* lane, **and** holding its speed: the
  compliance weight falls off quadratically as its speed departs from the nominal one.
  An oncoming vehicle that brakes hard is treated as abnormal even before it crosses the
  line — the earliest warning the driver can get in this geometry.
- **Intersection.** Normal = respecting the junction's geometry: not entering our
  carriageway past the yield line ("ignoring the light"), not cutting the corner arc, not
  leaving the paved area. Drawn as literal regions of the junction plan.

The pattern worth naming: each scenario's norm set encodes *the specific way that
scenario's threat announces itself* — lane exit for oncoming, junction entry for
crossing. The way we read it, writing a new scenario's norms (checklist item 5) amounts
to answering: "what is the earliest observable sign, in this geometry, that the other
agent has stopped being ordinary?"

## Part C: how normal can be changed

Because both normals are explicit objects, changing them is parameter work, not
rearchitecting — with effects that are predictable in direction and, for the safety
margin, in closed form (chapter 11).

**Traits (stable differences between drivers).** A cautious driver: the assumed
worst-case lead braking is made more severe (they plan for worse) and the pedal tolerance
tightened. A hurried driver: higher desired speed, tighter speed tolerance, shorter
assumed reaction time. A smooth-ride chauffeur: pedal and steering tolerances tightened,
closing-rate preference widened. Each is a handful of interpretable numbers
[Speculation, though the parameter meanings are the paper's].

**States (the same driver on a bad day).** The classic "extra motives" of the
comfort-zone literature — hurry, anger, social pressure — become *temporary reshapings of
the preference prior*. This project has computed two examples end to end
(`notes/04_comfort_zone_method.md` §5): shortening the assumed reaction time 1.0 → 0.6 s
moves the comfort boundary at 15 m/s from 1.67 to 1.27 s of headway; trusting the lead
(assumed worst braking −6 → −3 m/s²) moves it to 0.42 s. The theory predicts *how much*
the boundary moves, not merely that it moves — the most falsifiable thing this framework
offers the human-factors community, in our opinion.

**Norm changes (the others' normal).** Widening the lead's normal region makes the driver
slower to worry; tightening it makes the driver jumpy. A learned, data-driven norm set —
replacing the hand geometry with distributions fitted to observed traffic — is the
extension we would rank most valuable [Speculation]. Chapter 10 gives our proposed
procedure for it, and — more generally — where every number in this chapter came from
and the discipline for setting new ones.

## Part D: what, ultimately, defines it

Honesty about provenance: the shape of every preference term is **specified by the
authors**, not derived from first principles; thirteen parameters were hand-tuned to
produce human-like behavior [Paper]; one (the assumed worst-case braking) is calibrated
against a separate free-following dataset per scenario [SI]; none are fitted to the
conflict data they are evaluated on. So "normative driving" in this model is a *stated
hypothesis about drivers' standards*, made falsifiable by its behavioral consequences —
response times, maneuver choices, headways — rather than an empirical measurement of
those standards. Fitting the preference parameters to individual human drivers, and
checking whether the fitted values are stable across scenarios, is precisely the research
program the comfort-zone work opens (chapter 11).

---

## Notes for the mathematically curious

**Level 1 — preference as log-probability.** Each term contributes a log-probability;
the six add. "Zero cost" is the mode of each distribution; the cost of a departure is
the log-density drop. The additive decomposition is what lets an exceedance be blamed on
a term: the residual ε (chapter 02) is a sum of per-term residuals.

{{R1}}**Level 2 — forms and numbers.** Speed, pedal, steering: Gaussians with sds 0.5 m/s,
0.1 m/s², 0.02 rad/s around desired speed / 0 / 0 — with two code-only twists on the
pedal term: positive accelerations are doubled before the Gaussian, and the quantity
penalized is the total acceleration √(a_lat² + a_long²), not the longitudinal component
[Code: `reward.py:166,173`; neither is in the SI]. Lane: triangular within-lane density
with hard log-costs −1000 (lane boundary) and −15000 (road edge; the SI's −5000 is a
documentation error), lane-structured per scenario (SI Eq. 52). Inverse-tau: Gaussian on
1/τ with mean 0.2 s⁻¹, sd 0.125 s⁻¹, evaluated on max(1/τ, 0.2) so that it is one-sided
[Code: `reward.py:272`; SI Eq. 48 writes it symmetric]. Our mirror (`src/aidriver/
preferences.py`) follows the code for all of these and keeps the SI forms behind flags.
Collision: cost −10000 scaled by severity = max(Δv/10 m/s, 0.2) — the floor is SI
Eq. 48, not a fudge. Safety margin (SI Eqs. 49–51): required deceleration under the
counterfactual (lead brakes at min(observed, assumed worst); own response after
t_react = 1 s), compared against the achievable 8 m/s²; the closed-form boundary this
yields is `src/comfortzone/field.py::critical_gap` and chapter 11. Norm weights: Part
B's geometries with factors 0.001 and 0.001 × 0.01 (`weigh_particles`,
`full_violation_factor`); oncoming's speed compliance 1 − 2.25 (v/v₀ − 1)², clipped
[Code]. The thirteen hand-tuned parameters are listed in the paper's methods [Paper].


---

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

{{R4}}**Where that leaves our result.** The distance is now measured against a criterion the
reference can actually resolve. Condition B's severity θ is 0.148 with a 95% interval of
[0.110, 0.204], the CBM control's is 0.209 [0.176, 0.244], and neither reaches practical
equivalence at a defensible tolerance. What holds up is the comparison: tested as a
difference, the active-inference condition is closer with a posterior probability of about
0.97 under the project's uncertainty convention, the ordering is consistent at every bin
count, and the braking aggregate corroborates it without any binning at all. (An earlier
version of this paragraph said "closer on every single resample"; that came from an
analysis that held the synthetic sides fixed and overstated the certainty — corrected
2026-08-27, results doc section 4.3b-ii.) The lesson we would carry forward is that the
difference is what needs the interval, and that *all* of its variance sources need
resampling — leaving one side fixed quietly converts strong evidence into false certainty.

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


---

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

{{R2}}**A pattern worth naming: surrogate plus arbiter (added 2026-08-25).** When a study
needs thousands of model evaluations and the loop costs minutes to hours each, build a
cheap surrogate of the quantity you need, then *arbitrate* it against the full model on a
stratified subset before letting it carry the population. The crash-causation study did
this for response onsets: an open-loop surrogate (preference field plus accumulator) was
compared with the closed loop on 23 scenarios spanning 1.3–35.5 m/s and matched to a
median absolute difference of 0.55 s — after which the surrogate ran the 5 000-scenario
comparison the loop never could. Two disciplines made the validation worth something:
the arbitration also *settled a modeling convention* (the accumulator's starting level,
which a surrogate must assume and the full model decides), and the residual offset
(+0.30 s median) was reported rather than folded back in — an untuned surrogate within a
stated error is a stronger claim than a tuned one on zero
(`docs/crash_causation_results.md` §5).

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


---

# Chapter 10: calibration and parameter fitting — how the numbers get their values

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-23. Provenance tags
as in chapter 0. Added after review discussion: chapters 07 and 09 say the model's
"normal" can be changed; this chapter covers the discipline behind setting or changing any
number in it — where the published values came from, how new values should be obtained,
and the dos and don'ts of fitting a model with this much flexibility.*

## Three ways a number gets into the model — fitting is only one of them

A natural first assumption is that a model like this is "fitted to data" the way a
regression is. It is not, and the distinction matters for anyone planning to change it.
Every number in the model arrived by one of three routes, and each route carries its own
obligations when you replace the number:

1. **Specified** — taken from physics, geometry, or an independent literature. Vehicle
   dimensions, maximum braking, the timestep; the looming detection threshold comes from
   the psychophysics literature, not from fitting [SI]. Obligation when changing:
   cite the independent source, or admit the number has become a fitted one.
2. **Calibrated on normal driving** — set so that *everyday* behavior comes out right,
   then left alone when conflicts are simulated. The flagship example is below.
   Obligation: the calibration data must be separate from the evaluation data, and the
   calibration must *cover* the conditions you will run.
3. **Tuned** — thirteen parameters were adjusted by hand until behavior looked human at
   the qualitative level [Paper]. Honest, but the route with the least protection
   against fooling yourself. Obligation: whatever was tuned must face validation it was
   not tuned toward — which is exactly the role of the held-out intersection scenario.

To answer the direct question this chapter exists for: changing the normative part is
**not** only a matter of data fitting. The preference structure and norm geometry can be
changed by hypothesis (a trusting driver, a wider normal region) with the boundary
consequences computed rather than fitted (chapter 07); they can be re-calibrated on
normal-driving data; or — the [Speculation] route we develop below — they can be learned
from observed traffic. What they cannot credibly be is tuned freely against the same
critical events one then claims the model explains (chapter 01's flexibility worry, made
operational).

## The calibration exemplar, worth copying: the free-following lookup

The single most consequential preference parameter — the assumed worst-case deceleration
of the other vehicle, which sets where the safety margin sits (chapter 07) — is neither
specified nor tuned. It is calibrated, and the mechanism deserves to be understood
because it is the pattern any extension should copy [Code, `find_parameters` in
`src/utils/simulation.py`; SI]:

1. Run (once) a large grid of *free-following* simulations — no conflict, just steady
   car-following — across speeds, accumulator rates, and candidate worst-case
   assumptions, recording the steady headway each combination settles into.
2. Invert the table: given a speed and a desired everyday headway, look up (with
   interpolation) the worst-case assumption that *produces* it.
3. Use that value, unchanged, when simulating conflicts.

The logic is quietly elegant: the paranoia parameter is disciplined by ordinary
behavior. A driver who assumed worse would follow further back *all the time*; observed
comfortable headways therefore pin down the assumption without touching any conflict
data. Calibrate on the quiet regime, predict the loud one — the same separation chapter
05 describes behaviorally, used as an inference principle.

{{R2}}Two further provenance routes earned their place in the crash-causation study
(2026-08-25). **Digitized** — a distribution extracted from a published figure when the
underlying data are unshareable; legitimate only with an independent cross-check, and the
study's two are the pattern: the glance histogram's value axis was calibrated by tick
geometry *and* by the requirement that the drawn distribution sum to one (they agreed
within 0.9%), and the deceleration counts had to sum to the paper's stated n = 45
exactly, or the extraction script fails (`replication/causation/digitize_b24.py`).
**Arbitrated** — a *convention* (not a parameter) that the model itself can decide when
the full implementation is consulted: the accumulator's starting level was resolved by
running the closed loop rather than by fitting or by argument, and the losing convention
stays in the outputs as a tested sensitivity. Conventions resolved by arbitration should
be so labeled, with the arbitration's scope stated — this one holds for windows opening
near the conflict, and says nothing about long run-ins.

{{R1}}The cautionary half of the story is ours: the shipped lookup table covers steady-state
headways only up to about 1.0–2.1 s depending on speed, and outside that range the
interpolation clamps to the table edge — the parameter silently saturates at its most
pessimistic value, −8 m/s², for most of the paper's own rear-end conditions
(`docs/method_review.md` §6.2). The authors' published runs carry the same saturation;
an earlier draft of this chapter blamed it for a replication discrepancy that turned out
not to exist. The lesson still generalizes: **a calibration is only as good as its
coverage**, and coverage failures do not announce themselves — the model still runs, just
not the way its documentation says. Checking that a calibration table brackets every
condition you intend to simulate is a one-line assertion. A second lesson from the same
episode: **the calibration is only exercised if the simulation gives it time** — with the
lead braking 0.6 s into the run and the driver following a fixed reference plan until its
first re-plan, the "stable following" the table was built to produce never occurs in the
published runs.

## Identifiability: the central danger of fitting this model

The model's parameters do not map one-to-one onto observables. Several knobs move the
same behavioral output, which means a good fit does not tell you which knob was
responsible — and a fitted value can be badly wrong while the fit looks fine:

| Observable | Moved by (at least) |
|---|---|
| Response time | accumulator rate λ, looming threshold, perception noise, prediction noise, norm trust |
| Boundary location / accepted headway | assumed worst-case braking **and** reaction-time budget (chapter 07 shows both, with numbers) |
| Maneuver choice vs speed | steering-effort tolerance, lane costs, collision severity scaling |
| "Cautiousness" overall | collision cost, severity floor, safety-margin assumptions — jointly |

This project has a live demonstration of the phenomenon: fitting the comfort-zone level
c to the reference model's own onsets gave a boundary whose *location* was recovered
with zero median error while the *level itself* was indeterminate over orders of
magnitude, because the field rises so steeply that many levels tell the same story
(`notes/05_validation.md` §4b). The fit succeeded; the parameter was still not
identified. Expect the same everywhere in this model.

The defenses are standard but non-optional:

- **Fix everything you can by routes 1 and 2** before fitting anything by route 3; every
  parameter removed from the fit is a confound removed from the interpretation.
- **Fit the smallest subset that your hypothesis is about**, holding the rest at
  reference values — and say so.
- **Probe the objective around the optimum.** If a parameter can move substantially with
  little cost to the fit (as c above), report the range, not the point; a flat direction
  is a finding about the model, not an inconvenience.
- **Prefer observables that separate the knobs.** Response time alone cannot distinguish
  λ from perception noise; response time *as a function of condition* (urgency, speed,
  visibility) begins to, because the knobs bend that curve differently. Distributions
  beat means for the same reason.

## The mechanics: how fitting actually proceeds here

There is no formula linking parameters to data — the model is a simulator, so fitting
means comparing simulated and observed behavior and searching. Three practical
consequences [Paper] [OSF]:

- **Fit summaries, not trajectories.** The paper's own comparisons use response-time
  distributions per condition, maneuver-choice proportions, and deceleration profiles,
  with distribution distances (Jensen–Shannon, Wasserstein) and regression-based error
  bands as the yardsticks. Any refit should use the same summaries first, so results
  stay comparable.
- **Respect the noise floor.** Each condition was run with 32 random seeds, and
  seed-to-seed spread is substantial; a fit that chases differences smaller than the
  seed spread is fitting noise. Simulate enough seeds to know the model's own
  variability before crediting a parameter change with an improvement.
- **Be static wherever possible.** Closed-loop simulation costs ~18 s of CPU per
  timestep here, which makes naive search infeasible. The division of labor from
  chapter 09 applies to fitting too: preference and boundary parameters can be fitted
  *statically* against recorded kinematics in milliseconds (`calibrate_level` is exactly
  such a fit); only timing-and-prediction parameters (λ, noise scales, norm trust)
  genuinely require the loop — and for those, the deposit's precomputed grids [OSF] and
  coarse-to-fine searches are the difference between a week and a year.

## Learning the norms from data

*This section is [Speculation]: our proposed procedure, not published work.*

The norm geometries of chapters 06–07 are hand-drawn. Nothing prevents estimating them
instead, and the structure of the code makes the replacement surgical (one function per
scenario). The procedure we would try:

1. **Collect** the other-agent states observed in ordinary traffic for the scenario —
   lateral positions and speeds of leads, of oncoming vehicles, of turners at the
   junction type in question. Drone datasets are well suited: large N, exact kinematics,
   no interaction with an instrumented vehicle.
2. **Estimate the density** of those states, per context, and **map density to
   compliance weight**: full weight in the high-density core, dropping toward the
   observed tails — while *keeping a hard floor* like the code's existing small factors.
   The floor is not a technicality: it is what keeps physically possible but never-yet-
   observed behavior inside the prediction fan, and deleting it would rebuild the
   oblivious-driver failure the norms exist to prevent.
3. **Validate by coverage, not by fit.** A norm set is good if the prediction fans it
   produces are *calibrated*: actual next-seconds behavior of other agents should look
   statistically like draws from the fan — rare events falling outside at about the
   advertised rate. This can be checked on held-out trajectories without running the
   full driver model, which keeps the exercise cheap.

Done this way, "normative driving" for a new scenario becomes an estimation problem with
a defined data requirement, rather than an act of judgment — with the judgment surviving
only in the floor factors and the context definition, where it belongs and can be
argued about explicitly.

## Fitting individuals

The parameters were designed as one driver; the research value for this audience is in
letting them vary. Two disciplines from the general fitting literature transfer directly
[Speculation as applied here]: fit *few* parameters per person (one or two preference
knobs; everything else population-level), and pool across drivers (a hierarchical
structure, even informally: individual estimates shrunk toward the population) so that
ten-ish events per driver — the realistic naturalistic budget
(`docs/data_requirements.pdf`) — yield stable estimates. The sharpest question this
opens is the one chapter 11's transfer test asks at the population level, asked per
person: is a driver's fitted comfort level *theirs* — stable across scenarios — or a
property of the situation? Either answer is a result.

## Dos and don'ts, collected

**Do**

- Fix by physics and literature first; calibrate on normal driving second; fit last,
  and least.
- Check calibration coverage against every condition you will run, mechanically.
- Fit distributions per condition, never grand means; simulate enough seeds to know the
  model's own spread first.
- Keep the fitted-on data and the validated-on data disjoint, and keep one scenario
  untouched end to end — the held-out discipline is the model line's own best habit.
- Re-run the ablation for any mechanism whose parameters you refit (chapter 09, rung 2):
  a refit can quietly transfer a job from one mechanism to another.
- Record complete parameter sets with every result, the way the `Setups` tables do —
  including which route (specified / calibrated / tuned / fitted) each value came by.
- Report flat directions and ranges; treat weak identification as a finding.

**Don't**

- Don't hand-tune against the data you will call validation — with this many degrees of
  freedom the fit will succeed and mean nothing.
- Don't fit λ and perception noise jointly from response times alone; they are not
  separable there (use condition structure, or fix one independently).
- Don't quote absolute boundary or headway values without the assumptions they inherit
  (chapter 07; `HANDOFF.md` §7).
- Don't delete the norm floors when estimating norms from data — the tail is the safety
  case.
- Don't let calibration tables or fitted values live outside version control and the
  parameter record; a number whose provenance is lost reverts to "tuned".

---

## Notes for the mathematically curious

**Level 1 — the fitting problem stated.** With simulator M(θ) mapping parameters to
behavior distributions and observed summaries s_obs, fitting is
argmin_θ D(s(M(θ)), s_obs) for a chosen distance D over chosen summaries s — a
simulation-based (likelihood-free) inference problem. Identifiability is the geometry of
D around the optimum: flat valleys are unidentified parameter combinations. The static
shortcut works whenever s depends on θ only through the preference field ε(·; θ)
evaluated on fixed kinematics — then the simulator drops out and the search is direct.

**Level 2 — specifics.** The free-following lookup: `find_parameters(v_tar, EA_fac,
noise_pred_fac, H, d_phi_thres, THW_des)` multi-linearly interpolates a pre-run grid
(`Analysis_following.xlsx`) to return the `a_tar_min` (and residual speed offset)
consistent with the desired steady headway; the returned value is clamped at the grid
edge — the coverage failure mode above [Code]. The paper's comparison metrics: MAE with
bootstrapped uncertainty via Bayesian linear regression on residuals,
Jensen–Shannon divergence for categorical outcomes, Wasserstein distance for
response-time distributions, with a signal-to-noise criterion for reporting [Paper]
(`notes/05_validation.md` §4). The comfort-zone level fit (`calibrate_level`) maximizes
an F1-style onset-matching score over c with a timing tolerance; its flat-maximum
behavior on steep fields is documented in `notes/05_validation.md` §4b. For norm
estimation, the coverage check in step 3 is a probability-integral-transform-style
calibration test of the prediction fan on held-out segments.


---

# Chapter 11: the path to comfort-zone boundaries

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance tags
as in chapter 0. This chapter answers the project's third goal: how the model expands into
comfort-zone boundary (CZB) research, and what is needed. Fuller technical detail:
`notes/04_comfort_zone_method.md`; validation status: `notes/05_validation.md`.*

{{R5}}**Status note (2026-08-29) — read before the rest of this chapter.** The program this
chapter proposes has since been run against human data, and the outcome changes how its
argument should be read. Four results, in the order they arrived. (1) The boundary was
fitted on the study-1 cut-in responses and the population distribution is well estimated
on its own scale (median 5 400 deficit units, between-driver spread 0.200, stable to
within 1% across specification changes). (2) The accumulator layer — the "dynamic
picture" half of this chapter's dual-role argument — **failed its pre-registered test**
(held-out 0.255 against a rule of ≤ 0.11), a verdict that is final for the architecture
tested (deficit-driven drift, non-leaky, fixed bound) and does not extend to the standard
traffic architectures never tested. (3) The study-1 cut-in design cannot distinguish the
field from a plain gap threshold — its relative speed is constant, so gap and TTC are
perfectly collinear — and a second cut-in study that breaks the collinearity **ruled
against the field** in a pre-registered comparison: the field scores worse than chance on
held-out folds where a three-parameter gap threshold approaches the sampling-noise floor.
(4) What survives, with strong field-free evidence, is this chapter's claim one level up:
**each driver carries one comfort-zone level, and about 69% of the reliable per-driver
signal is shared across all four scenarios**; a boundary fitted on the cut-in predicts
the cyclist overtake once each scenario's response floor is freed. The project's headline
is now that trait claim, with the criticality axis an open question on which the gap
currently leads; the per-scenario-indicator alternative this chapter argues against is
back as the primary comparator program. Full record and decisions:
`docs/r2_gate_decisions.md`; the fits and tests: `replication/czb/out/`. The chapter
below is kept as written — its framing argument is why the test was worth running — but
its confident present tense about the field should be read as of 2026-08-22.

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

## From one driver's boundary to a population percentile

{{R3}}*Added 2026-08-26, after reading Jonas's `On CZB as basis for ADAS adaptation`
(QUADRARUM, May 2026) and agreeing the framing with him. This section states what we think
the active-inference route buys, precisely enough to be wrong.*

{{R3}}**The end goal is a distribution, not a boundary.** An ADAS has to trigger at some
specific moment, and the operational proposal in the QUADRARUM document is to set that
moment at a percentile of the comfort-zone boundary across drivers — say the 80th, so that
crossing corresponds to entering the fifth of situations that most drivers would already
find uncomfortable. Everything in this chapter is ultimately in service of producing that
distribution with credible intervals, rather than a single number.

{{R3}}**Where the active-inference formulation earns its place.** The conventional route
estimates a percentile of an *observable* — a time-to-collision, a post-encroachment time, a
lateral clearance. That inherits a multivariate problem immediately: each scenario has its
own observables, each needs its own threshold, and combining marginal percentiles under an
"exceed both" rule silently tightens the criterion (two 80th percentiles under independence
give a 4% joint exceedance, not 20%). The QUADRARUM document works this through and proposes
an elliptical joint-percentile boundary, using Mahalanobis distance, as the principled fix.

{{R3}}The active-inference route proposes something different: estimate a per-driver
**scalar** level *c* on the preference field, which has already absorbed speed, gap, closing
rate, lateral position and the assumed worst case into one number. The population
distribution of *c* is then one-dimensional by construction, and a percentile of it is well
defined without an ellipse. The multivariate problem does not get solved so much as
dissolved — *if* the field is the right scalar.

{{R3}}**This is a falsifiable claim, and the transfer test is what falsifies it.** Fit *c* on
one scenario and predict the others with *c* unchanged. If one level per driver transfers
across a cut-in, an intersection turn and two lateral overtakes, the multivariate problem was
an artifact of choosing per-scenario observables. **If transfer fails, the field is not the
right scalar, and the fallback is the elliptical joint-percentile formulation** — which would
itself be a useful result rather than a dead end, since it would localize the failure to
specific preference terms.

{{R3}}**A conceptual convergence worth recording.** The QUADRARUM document defines the CZB as
the point at which "the satisficing condition is violated ... and behavioral regulation
becomes necessary". That is very close to what the preference function *is*: a specification
of acceptable outcomes rather than an optimum to be maximized. A driver who is inside the
comfort zone has no reason to act, not because nothing better is available, but because the
current state is good enough. The boundary being a level set of a satisficing specification
is the same idea expressed in two vocabularies, and it is the reason the preference function
— rather than the closed-loop controller — is the part of the model this chapter depends on.

{{R3}}**Comfort or dread: which boundary the data actually identifies.** The clip-based study
asks what braking the situation is expected to require: nothing, gentle, or hard. Reading
these as one ordered response gives two nested levels rather than one, and they are not
equally trustworthy. A "hard braking expected" answer is difficult to give for any reason
other than genuine perceived urgency, so it identifies the **dread-zone boundary** cleanly.
A "gentle braking" answer is compatible with a wide range of internal states and is open to
satisficing, so the comfort-zone level it implies is weakly identified. Our position, agreed
with Jonas: fit both as an ordered model so the gentle responses still contribute
information, but expect the dread level to be well determined and treat the comfort level as
a latent quantity carrying a wider posterior. Reporting the comfort boundary as a point
estimate would overstate what the data supports.

## What the fitted boundary level absorbs, and how to take it apart

{{R3}}*Added 2026-08-26 at Jonas's request, recording both the reasoning and the decisions the
analysis design still has to make.*

{{R3}}**The problem.** A boundary level fitted to observed responses is not purely a boundary.
It also absorbs everything between the boundary being crossed and the response being
recorded: the participant's motor and decision latency, their individual willingness to
report at all, whatever the response paradigm adds, and any mismatch between the field we
compute and the one the participant is actually responding to. For a *percentile* this is
mostly harmless, because every driver's estimate is displaced in the same direction and the
population ordering survives. For an *absolute* claim — "the comfort-zone boundary lies at a
time headway of x" — it is not harmless at all, and the handbook's standing warning about
never quoting absolute boundary values without stating the assumed worst-case deceleration
and reaction time applies with equal force here.

{{R3}}**Why this study can do better than absorb it.** Writing the fitted level for driver *i*
in paradigm *p* as

> c_obs(i, p) = c_true(i) + b(i) + δ(p) + λ + ε

— a true boundary, a per-driver response bias, a paradigm offset, a latency term and noise —
the question is whether the design contains contrasts that identify each piece separately.
It largely does, and by accident rather than intent:

| component | what identifies it | how good is the identification |
|---|---|---|
| c_true(i) | the criticality × timepoint response surface | good — six truncation points crossed with three criticality levels |
| b(i), response bias | the **pre-onset (C1) condition**, where nothing has happened and any reported intervention is a false alarm | good per group, weak per driver at four repetitions |
| δ(p), paradigm offset | the **same participants in both clip and button designs** | good — but confounded with session order, so it is a *combined* order-plus-modality term |
| framing shift | **supervisory versus manual sessions**, same stimuli, same people | good, and counterbalanced, unlike the paradigm contrast |
| λ, motor latency | nothing in this design | not identified — must be fixed from literature or absorbed |

{{R3}}**The decisions the design still has to make.** These are open, and we would want them
settled before fitting rather than after:

1. **Which components to model explicitly and which to absorb.** Every component added costs
   identification. Our inclination is to model b(i) and δ(p) explicitly, fix λ at a literature
   value (roughly 0.2–0.3 s for a keypress), and absorb the remainder into ε.
2. **Whether the response bias is per-driver or per-group.** Four pre-onset repetitions per
   participant is thin for an individual false-alarm rate. A hierarchical b(i) with strong
   shrinkage is the compromise; a fixed group-level bias is the safer alternative.
3. **Whether the paradigm offset acts on the level or on the accumulator.** A satisficing
   participant might be pressing at a lower boundary (shift in c) or accumulating faster
   (shift in rate). These make different predictions about the *shape* of the press-time
   distribution, not just its location, so the button data can in principle distinguish them
   — this is worth testing rather than assuming.
4. **Whether framing acts on c or on the preference parameters.** This is the interesting
   one, and it is a genuine test of the "extra motives as parameter changes" machinery of
   chapter 09: if supervising an automated system rather than driving shifts a small number
   of *named* parameters — most plausibly the assumed worst-case deceleration of the other
   vehicle, or the reaction-time budget — that is a much stronger result than a free shift in
   c, and it is falsifiable.
5. **Whether the order confound is separable at all.** It is not, within this dataset:
   Random always preceded Button. δ(p) will therefore always be a combined
   modality-plus-practice term, and should be named that way rather than called a modality
   effect. Only a counterbalanced replication could separate them.

{{R3}}**What this buys.** If the decomposition works, the population distribution used for a
percentile is a distribution over c_true rather than over c_obs, and the percentile inherits
a meaning that does not depend on the paradigm that produced it. That matters if the number
is ever to be compared against a test-track or naturalistic estimate — which, per the
QUADRARUM document's observation that measured and CZB-based thresholds may differ by only
about 0.1 s, is exactly the comparison worth being able to make.

---

## Notes for the mathematically curious

{{R3}}**Level 1 — the hierarchical boundary model.** Let ε_s(t) be the comfort-zone field
along stimulus s at time t, computed once per stimulus because the ego does not respond. For
driver i, a boundary crossing is the first time ε exceeds a level: T_{i,s} = min{t : ε_s(t) >
c_i}. The clip-based design truncates stimulus s at a known time T_s and asks for a response,
so it observes the *event* {T_{i,s} ≤ T_s}, which is the response-time CDF evaluated at T_s.
With an ordered response (nothing / gentle / hard) and two levels c_i^CZB < c_i^DZB, the
likelihood for one trial is an ordered-categorical model on max_{t ≤ T_s} ε_s(t): the
category is "nothing" below the comfort level, "gentle" between the two, "hard" above the
dread level. Drivers enter as random effects, c_i ~ Normal(μ, σ) on a log scale to keep
levels positive, and the population boundary at percentile q is then the q-th quantile of
that fitted population distribution — reported with a posterior interval, since μ and σ are
themselves estimated.

{{R3}}**Level 2 — identification, and what each design contrast buys.** Three things are
estimated jointly and would trade off if the design did not separate them. The *level* c_i is
identified by how criticality shifts the response across the 3 × 6 criticality-by-timepoint
grid. The *response bias* is identified by the pre-onset condition, where nothing has
happened and any reported intervention is a false alarm; its rate differs by criticality
level (0.117, 0.071, 0.046 for TTC4/6/8) because longitudinal proximity already differs
before the manoeuvre, so the baseline is itself informative about sensitivity to proximity
alone. The *paradigm offset* is identified by the same participants appearing in both the
clip and button designs, giving δ = c^button − c^clip; our estimate of its sign and size is
that button responses are systematically earlier, by up to 0.26 in probability at
intermediate criticality. The *framing effect* is identified by the supervisory-versus-manual
sessions at constant stimulus, and the interesting hypothesis there is that it appears as a
shift in a small number of preference parameters — most plausibly the assumed worst-case
deceleration of the other vehicle, or the reaction-time budget — rather than as a free change
in c, which would be a genuinely falsifiable prediction of the "extra motives as parameter
changes" machinery of chapter 09. A complete specification, with priors and the sampler
configuration, belongs in its own appendix once the model has actually been fitted; writing
it before then would be documenting a plan rather than a method.

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


---

# Chapter 12: the code map — from concept to file, class, and parameter

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Paths under
`external/aica/` are the authors' released code [Code] — the reference implementation and
ground truth. Paths under `src/` are this project's code. Parameter names are the columns
of the OSF `Setups_*.xlsx` tables, which double as the complete configuration record of
every published run [OSF].*

## The two implementations, and which to use when

| | The reference (`external/aica/`) | Our mirror (`src/aidriver/`) |
|---|---|---|
| Language | PyTorch, written for GPU | NumPy, written to be read |
| Status | ground truth; ran the published results | preferences verified against the SI; closed-loop timing not yet trusted |
| Use for | any result you intend to compare or publish | understanding mechanisms; static/preference work |
| Cost | ~18 s CPU per simulated timestep here | interactive |
| Local changes | exactly one patch, logged in `replication/PATCHES.md` — keep it that way | ours to change |

The comfort-zone machinery (`src/comfortzone/`) is a third thing: not a model
implementation at all, but the static method of chapter 11, depending only on the
preference function and recorded kinematics.

## The reference implementation, oriented in one table

Top level: one `simulation_<scenario>.py` runner and one `Analysis_<scenario>.py` per
scenario (plus `_SA` sensitivity variants); the runners assemble a configuration
dictionary, call the shared machinery, and write the pickle/xlsx outputs mirrored in the
OSF deposit.

| Concept (chapter) | File in `src/common/` | What to look for |
|---|---|---|
| World physics | `bicycle.py`, `environment.py` | bicycle model both vehicles share |
| Looming senses (03) | `decoder.py`, `encoder.py` | observation construction; the looming transform; the off-gaze noise factor `I_factor` |
| Belief cloud (06) | `particle_filter.py`, `kde.py`, `distributions.py` | weighting, resampling; the KDE/mixture belief representation |
| Imagined futures + norm trust (06) | `dynamics.py` | `forward_tar_agent`, `normative_probability`; the `N_norm`/`H_norm` sampling and the trust cap |
| Scoring, pragmatic + epistemic (03) | `belief_reward.py` | expected-free-energy assembly over particles |
| The planner and the surprise gate (03, 05) | `mpc_discrete.py` | CEM loop; evidence accumulation; the hard-coded "avoid off gaze" line (08) |
| Gaze dynamics (08) | `dynamics.py` (gaze block) | two-state gaze, switching probability `p` |
| Run orchestration | `src/utils/simulation.py`, `saving.py` | how a config becomes a run becomes a pickle |

Per scenario (chapter 04): `src/<scenario>/dynamics_true.py` (the world and the other
vehicle's script), `decoder_true.py` (true-state → observations), `reward.py` (the
preference terms with the scenario's lane geometry, and `get_weights` — the norm
geometry of chapters 06–07). The rear-end scenario used for the published grid lives in
`src/rear_end_test/`.

## The parameters that matter most, by name

All 65 configuration columns are in every `Setups_*.xlsx`; these are the ones the
handbook's chapters keep returning to:

| Column | Plain meaning | Chapter |
|---|---|---|
| `v_ego_sd_des`, `a_ego_sd_des`, `w_ego_sd_des` | tolerances of the speed / pedal / steering preferences | 07 |
| `lane_change_cost`, `road_leave_cost`, `collision_cost` | the hard costs | 07 |
| `a_sd_model`, `w_sd_model` | assumed other-agent variability (the scenario-type dial) | 04, 06 |
| `N_norm`, `H_norm`, `weigh_particles`, `full_violation_factor` | norm-conditioning strength and geometry factors | 06 |
| `alpha` | weight of epistemic value | 03 |
| `EA_mode`, `EA_fac`, `EA_init` | evidence accumulation on/off, rate λ, starting level | 02, 05 |
| `use_looming_perception`, `looming_threshold` | the visual channel and its detection floor | 03, 08 |
| `x_sd_perc` … `w_sd_perc` | perception noise scales | 03, 08 |
| `num_plans`, `H` | planning budget and horizon | 03 |
| `road_gaze_preference`, `x_ego`…`v_tar`, `T` | gaze preference (0 in all published runs); stage-setting | 08, 04 |
| ablation columns | the seven Figure-6 switches | 09 |

## This project's code

| Package | What it is | Trust level |
|---|---|---|
| {{R1}}`src/aidriver/` | readable NumPy mirror of the agent: `preferences.py` (the six terms, aligned with the released code since 2026-08-23; SI forms kept behind flags, every difference documented in the module notes), `agent.py` (belief + CEM loop), `scenarios.py`, `params.py` | preferences verified against code and deposit; closed-loop timing not trusted (`notes/05_validation.md`) — see also the two parameter traps in `HANDOFF.md` §4 |
| `src/surprise/` | the surprise-measure library (three families + the two Waymo measures), one interface across belief types | property-tested, 31 tests |
| `src/comfortzone/` | the CZB method: `field.py` (field, closed-form boundary), `boundary.py` (level sets), `calibrate.py` (field along recorded kinematics; level fitting) | cross-checked closed form; end-to-end dry run on the OSF data |
| {{R1}}`replication/` | Track A runner + sweep + `validate_osf.py` (the OSF comparison harness of chapter 09, rung 3) + `review_osf.py` (the deposit checks behind `docs/method_review.md`) | outputs in `replication/osf/` and `replication/osf/review/` |
| {{R2}}`src/quadris/` | QUADRIS seed handling: loading, weight-proportional stratified sampling, the Wu metrics | property-tested |
| {{R2}}`src/causation/` | the five crash-causation components and the two response processes behind one interface; the tier-1 onset surrogate is closed-loop-validated (median abs. difference 0.55 s over 23 scenarios; `docs/crash_causation_results.md` §5) | property-tested |
| {{R2}}`src/equivalence/` | reusable Wu et al. (2026) binning/ROPE equivalence testing, reproduces the paper's worked θ example | property-tested |
| {{R2}}`replication/causation/` | the study's runners: figure digitizer (`digitize_b24.py`), condition runner (`run_quadris.py`), tier-2 closed-loop adapter (`tier2_rear_end.py` — lead replay, forcible gaze schedule, checkpointing), arbiter analysis (`tier2_compare.py`) | outputs in `out/` and `tier2/` |
| {{R2}}`tests/` | 103 property tests across the three suites (31 surprise, 33 comfort zone, 39 causation/equivalence) — the rung-0 suite | all passing |

## The data that goes with the code

The OSF deposit (`external/gs4bu-osfstorage-archive/`) is the third leg: per-run
configuration tables (`Setups_*.xlsx`), outcome summaries (`Analysis_*.xlsx`), and
per-timestep pickles (true states `eta`, observations `o`, beliefs `b` with weights `w`,
planned and reference policies `a_cont` / `a_cont_init`, pragmatic-value components `v`)
for every published run of all three scenarios, ablations included. One recorded erratum:
the deposit README's stated axis order for the policy arrays is wrong — they are (horizon,
timesteps, seeds, 2), not (horizon, seeds, timesteps, 2); `eta`'s shape disambiguates
(`notes/05_validation.md` §4b) [OSF].

Practical rules when working here: mine the deposit before simulating (chapter 09);
never edit `external/` beyond the logged patch; keep every new result paired with its
full parameter record the way the `Setups` tables do; and remember the environment kills
long jobs — the restartable runners and their checkpoint files exist for that reason
(`HANDOFF.md` §3).

## Five first exercises

For a new person's first afternoon — each is under an hour, needs no GPU, and touches a
different limb of the system. In rough order:

1. **Meet the model's output.** Load one OSF pickle (`Results_rear_end/Exp_7/Exp_7.pkl`),
   plot speed, gap, and executed acceleration for a few seeds. You are reproducing
   chapter 02's figure; the axis-order erratum above is the only trap.
2. **Run the cheap demos.** `python demo_comfort_zone.py` and `python demo_surprise.py`
   — the static machinery end to end, minutes, no closed loop.
3. **Move a boundary.** In a notebook, call `comfortzone.critical_thw` across speeds;
   then change the assumed worst-case braking and the reaction-time budget and watch
   chapter 07's tables reappear. This is rung 1 of the validation ladder in miniature.
4. **Score a trajectory.** Take the `eta` kinematics from exercise 1, run
   `calibrate.deficit_along_trajectory`, and find the first exceedance against the
   fitted level from `replication/osf/calibration.json`. You have just reproduced the
   core of the comfort-zone pipeline (chapter 11).
5. **Watch the trust cap work.** Run `docs/handbook/make_diagrams.py` and modify the
   `norm_tournament` starting position and geometry factors — the fastest way to build
   intuition for chapter 06, and safe, because it is an illustrative reimplementation.

A sixth, when a spare two hours of CPU exists: run
`replication/run_rear_end_single.py` for one short condition with
`--checkpoint-every`, to experience the reference loop's cost and the restart machinery
firsthand.


---

# Chapter 13: glossary — one idea, three vocabularies

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. The middle
columns are our translations; where a mapping is loose we say so rather than force it.*

## The Rosetta stone

| Term here | Engineering / ML reading | Human-factors reading |
|---|---|---|
| Generative model | internal simulator / world model | the driver's understanding of how traffic works |
| Belief (particle cloud) | posterior state estimate with honest uncertainty | situation awareness, held with degrees of confidence |
| Observation | sensor reading | what perception currently delivers |
| Looming | angular-size channel with state-dependent noise | optical expansion, the classic visual cue |
| Surprise | negative log-likelihood of what happened | expectancy violation |
| Free energy | a computable bound on model misfit | (no native equivalent — "how badly my picture of the situation fits") |
| Preference prior | goal specification, written as a distribution | motivation; how the drive is supposed to go |
| Pragmatic value | expected goal achievement of a plan | progress and safety satisfaction |
| Epistemic value | expected information gain of a plan | the pull to look, probe, and resolve uncertainty |
| Policy | planned control sequence | intended maneuver |
| Expected free energy | plan cost = pragmatic + epistemic in one currency | the felt overall "rightness" of an intended course |
| Bounded planning (CEM) | sampled, budgeted trajectory optimization | satisficing; good-enough decision making |
| Norm (about others) | prior over other agents' trajectories, geometry-shaped | expectancy about other road users' behavior |
| Norm-conditioning trust cap | prior weight gated by observed compliance | trust extended while earned, withdrawn on evidence |
| Evidence accumulation (E, λ) | leaky-free integrator to threshold | the response-timing process of accumulator models |
| Residual information (ε) | shortfall of current plan vs best achievable, in nats | how far the situation has left "as it should be" |
| Comfort-zone field / level set | scalar cost-to-normal over states; an isocontour | the comfort-zone boundary, made scenario-free |
| Precision | inverse variance; confidence weighting | how much a cue or expectation is trusted |
| Ablation | mechanism knocked out, behavior compared | showing a mechanism matters by removing it |
| Calibration (vs fitting) | setting a parameter from separate, non-evaluation data | grounding a number in ordinary behavior before predicting rare events |
| Validation (vs fitting) | testing against data no parameter ever saw | the held-out discipline |
| Identifiability | whether data can pin a parameter down uniquely | whether two explanations of the same behavior can be told apart |
| Summary statistic | the condensed observable a simulator fit targets | the behavioral measure (RT distribution, maneuver share) standing in for raw data |

## False friends — words that do not mean what they usually mean

- **Surprise** is a *quantity*, not an emotion. A state can carry surprise the driver
  would never report feeling; the model's "surprise" is closer to *mismatch*.
- **Preference** is not a choice or a ranking; it is a probability distribution stating
  which futures are treated as unremarkable. Wanting and expecting are deliberately the
  same object.
- **Reward** appears in the code (`reward.py`) but is *not* RL reward: nothing is being
  maximized by trial-and-error learning. The file computes log-preference.
- **Norm** is not a traffic rule. It is a description of what other agents typically do,
  used for prediction — a violated norm is information, not an offense.
- **Free energy** has no thermodynamic content whatsoever (chapter 01).
- **Belief** carries no conscious commitment — it is a weighted hypothesis set.
- **Optimal** almost never applies: the planner is deliberately budgeted, and the model's
  humanlikeness partly *depends* on its suboptimality (chapter 03).
- **Agent** means the simulated driver — but in `dynamics_true.py` "target agent" is a
  scripted puppet with no agency at all (chapter 06).
- **Epistemic** does not mean abstract knowledge-seeking; operationally it is "this plan
  will let me see better".

## Frequently confused — short answers

**Is this reinforcement learning?** No. Nothing is learned from reward across episodes;
there is no training loop. The preferences are specified, the behavior is computed fresh
each run. The resemblance is only that both talk about value.

**Is it optimal control with extra words?** Closer, but two differences do real work: the
cost function is a probability distribution (which is what lets the same object define
surprise, and hence timing), and the planner is deliberately bounded (which is where the
human character of the maneuvers comes from). An optimal-control reading also has no
native account of the epistemic term.

**If the agent minimizes surprise, why doesn't it park in a dark garage?** The famous
"dark-room" objection. Because surprise is measured against the *preference prior*, and
the preference prior of a driver says "I am making progress at my desired speed". Sitting
still is maximally surprising to an agent whose expected world involves getting
somewhere. (Chapter 14 covers the debate around this answer.)

**Does the model want to be surprised (curiosity) or not (comfort)?** Both, coherently:
it avoids *pragmatic* surprise (departures from the preferred future) while seeking
observations that reduce uncertainty — the epistemic term. The two are added in one
currency, which is the framework's central accounting trick (chapter 03).

**Is the particle filter what makes the other car move?** No — the most common confusion
in this project's experience. The other car follows a script (chapter 06). The particle
filter is the *driver's uncertainty* about the world, including about that scripted car.

**Are the parameters fitted to the crash data?** Thirteen were hand-tuned; the assumed
worst-case braking is calibrated on separate free-following data; the intersection
scenario was held out entirely [Paper]. No parameter was fitted to the conflict responses
the model is evaluated on.

**Do I have to believe the brain minimizes free energy?** No. Chapter 01's permission
slip: the model stands or falls as an empirical driver model, whatever the grand theory's
fate.

**Noise or uncertainty — which is which?** Noise is in the world and the senses
(parameters); uncertainty is in the beliefs (the cloud's spread, computed). Turning noise
up raises uncertainty, but uncertainty also rises with distance, occlusion, and gaze —
that is the point of carrying it explicitly.


## {{R6}}The measurement vocabulary — the comfort-zone terms in plain words

*Added 2026-09-02 ({{R6}} round). The Rosetta stone above translates the active-inference
model's vocabulary. This section does the same for the measurement program that grew out of
it, because by now most of the project's claims are stated in these terms and several of them
("level", "axis", "deficit") sound ordinary but mean something specific here. Each entry gives
the meaning first, then the number or file it is tied to. Terms in bold within an entry have
their own entry.*

{{R6}}**Comfort-zone boundary (CZB).** The edge of the region of driving states a driver is
comfortable in: inside it they do nothing about the situation, at it they start to act. The
project's operational reading is a **level** on an **axis**, applied when a **gate** says the
situation counts. The end use is a **percentile** of the boundary across drivers.

{{R6}}**Criticality axis (the axis).** The one number read off the scene at each moment that
the boundary is a threshold on. Candidates tested: the field's **deficit**, the gap, time to
collision (TTC), required deceleration, and the **optical expansion rate**. On the cut-in the
expansion rate won (`replication/czb/out/cutin2_looming.md`, 0.113 held out against 0.152 for
gap alone). "Axis" is used because the boundary is a point on it, and because different
scenarios may need different ones.

{{R6}}**Optical expansion rate (looming rate, θ̇).** How fast the other vehicle grows in the
eye, in radians (or degrees) per second: θ̇ ≈ W Δv / g² for a vehicle of width W at gap g
closing at Δv. Equal to width divided by (gap × TTC), which is why the equal-weighted rule of
card EL.1 turned out to be this quantity. The classic looming variable of the visual-control
literature, and what the active-inference model's own perception stage computes.

{{R6}}**Deficit (the comfort-zone deficit, the deficit axis).** The active-inference candidate
for the axis: how far the current state's preference falls short of the preferred state, in
the preference function's own units, exactly zero inside the comfortable region and positive
outside. The project used its running maximum over the shown clip (`deficit_max`) and a level
on it (population median 5 400 units, `out/stage1_summary.md`). Ruled against as the axis at
gate R.2 and superseded by the expansion rate in the stage-1 fit (`out/stage1_looming.md`).

{{R6}}**Level (the per-driver level, c_i).** One driver's threshold on the axis: the value at
which their probability of intervening, with the gate open, passes one half. Estimated
hierarchically (each driver's level is a draw from a population with a median and a spread),
so that the population's percentiles have confidence intervals. On the looming axis the
population median is 0.032 rad/s (about 1.8° of apparent width per second), the 80th
percentile 0.066 rad/s.

{{R6}}**Gate (the anticipatory gate, w).** A number between 0 and 1 saying how much the
situation counts yet: the probability that the other vehicle will come within a minimum
lateral clearance over a fixed look-ahead of 3 s, from its clearance now and its closing rate.
It multiplies the response: P = lapse + (1 − lapse) × w × Φ((x − level)/spread). Near 0.07
before a cut-in starts, near 1 once the vehicle is committed. Credited on our rule in card G.1
(`out/cutin2_gate.md`) after the idea arrived through the external analysis (appendix 16).
The gate is the part of the model that changes between scenarios.

{{R6}}**Trait (the per-driver trait).** The finding that a driver's level is largely the same
person across scenarios: the per-driver, criticality-adjusted propensity to intervene
correlates at 0.50 to 0.74 across all six pairs of the four scenarios, about 69% of the
reliability ceiling, measured with no model at all (`out/cross_scenario_consistency.md`).

{{R6}}**Percentile (the percentile deliverable).** The operational output: the level that a
stated share of drivers would already have crossed, used as a trigger. The 80th percentile
means "80% of drivers would have acted by here". Card C measures what a 5-point change of the
percentile costs in seconds against what the level's own uncertainty costs (on the looming
axis 0.24 s against 0.52 s, `out/stage1_looming.md` section 5).

{{R6}}**Cell.** One design condition of a study, with the share of participants who said they
would intervene and the number who saw it. The second cut-in study has 378 cells (288 after
the cut-in has started); study 1's cut-in has 18. Fits are to cell means, weighted by n.

{{R6}}**Held out (held-out score, leave-one-X-out).** A model is fitted on part of the data and
scored on cells it never saw; the folds are grouped by a design factor (leave one starting
TTC out; leave one PET level out) so that the test is transfer across the design's main axis,
not interpolation. The score is the weighted root-mean-square error between predicted and
observed cell means. Every comparison in the project that carries a verdict is held out.

{{R6}}**Noise floor (sampling-noise floor).** The held-out error a perfect model would still
show, because each cell mean is a noisy average of 12 to 24 people: the binomial standard
error of each cell, averaged with the fitting weights (0.118 on the second cut-in study). A
model at the floor cannot be improved on that data; two models both at the floor cannot be
told apart.

{{R6}}**Chance.** The score of predicting every held-out cell by the training cells' mean
(0.320 on the second cut-in study). A model above chance is worse than knowing nothing about
the scene.

{{R6}}**Pre-registered (pre-stated).** The models, folds, metric and decision rule are written
in the script's docstring and committed before the run, so the verdict cannot be argued with
afterwards. Gates R.1 and R.2 and every card since are pre-registered; the worklog records the
few cases where a bound or an implementation slip was corrected after a run, with both numbers.

{{R6}}**Card.** One unit of work with a stated deliverable and, where it tests something, a
pre-stated rule (`docs/czb_work_orders.md`). Named by letter and number (EL.1, G.1, B.3.v2).

{{R6}}**Gate R.1, gate R.2 (review gates).** The two pre-registered tests of the original
active-inference hypothesis. R.1: does accumulated surprise over the field time the response?
It did not. R.2: is the field the right criticality axis? It lost to the gap
(`docs/r2_gate_decisions.md`). Not to be confused with the anticipatory **gate**.

{{R6}}**Timepoint (C1–C6, CP1–CP5).** The moment a video clip is frozen at, in steps of 0.3 s
from the start of the other vehicle's manoeuvre; C1 (CP1) is before it starts. The pre-onset
cells are where the **gate** is tested, because there the axis should not matter yet.

{{R6}}**Lapse.** The share of responses that do not follow the stimulus at all (a floor of
"yes" at the easiest cells, a shortfall from 1 at the hardest). Fitted per driver in the
stage-1 estimator so that heterogeneity is not mistaken for noise.

{{R6}}**LOPO (leave-one-participant-out).** The stage-1 estimator's held-out check: refit with
one driver removed and score how well that driver's responses are predicted from the
population. Used to compare axes and variants (the looming axis beats the deficit axis by
14.9 log-likelihood units).

{{R6}}**Reliability ceiling.** The highest correlation two measurements of the same thing
could show, given each one's own split-half reliability. Cross-scenario correlations of the
trait are read against it (0.93 to 0.98 within a scenario), which is why 0.69 of the ceiling
is a strong result rather than a weak one.

{{R6}}**Surprise (in the measurement program).** No longer the axis. The surprise note
(`docs/surprise_without_the_field.md`) proposes that surprise, relative to a predictive model
of what other road users normally do, defines *when a situation starts to count*, which in
these terms is the gate; the level is a percentile on the axis. One operator, two references
(query Q5.Q1).

{{R6}}**The ellipse (CZB ellipse, joint percentile).** The two-observable form of the boundary:
a quadratic form in two axes whose level set is the boundary, so that a worse value on one
axis can be offset by a better one on the other (`docs/czb_ellipse_design_note.md`). On the
cut-in the data preferred a straight line in the log plane (the linear rule), which is the
looming rate; on the left turn the comparison is card B.3.v2.


---

# Chapter 14: appendix — the deep end

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. This appendix
exists so that the main chapters could stay out of these waters. Nothing here is needed to
use the model or the comfort-zone method; everything here is where a curious reader should
go next. It is a guide with commentary, not a tutorial — each section says what the thing
is, why the main text could skip it, and where the primary treatment lives. References
marked (verified) are ones we have read in full or checked against the source; the rest
are standard works cited by title and venue for the reader to locate.*

## A. The free-energy principle proper

**What it is.** The claim beneath the framework: any system that maintains itself against
dispersion — a cell, a brain, arguably an organism-environment loop — can be described *as
if* it minimizes variational free energy, because persisting just is keeping sensory
states within expected bounds. In its strongest form the claim is presented as close to
tautological: things that exist are things that model their environment well enough to
keep existing.

**Why the main text skipped it.** The driver model uses free energy as an engineering
objective (chapter 01, claim 3). Whether the principle is a deep truth, a useful
reformulation, or an unfalsifiable framing is irrelevant to whether the model predicts
human braking — and the debate is long.

**Where to go.** Friston, "The free-energy principle: a unified brain theory?" (Nature
Reviews Neuroscience, 2010) — the canonical statement. Friston, "A free energy principle
for a particular physics" (2019 preprint) — the strongest, most mathematical form. For
the driving-adjacent reading, the introduction of Engström et al. (2024) states exactly
how much of the principle the model line actually uses (verified — the paper is in
`papers/active-inference/` with text in `notes/paper_text/`).

## B. Variational inference, in outline

**What it is.** The mathematical engine. Exact Bayesian belief updating is intractable
for any interesting model, so one optimizes an approximation: pick a family of
manageable distributions Q, and adjust Q to minimize free energy
F = E_Q[log Q(s) − log P(o, s)], which equals the true surprise −log P(o) plus the
divergence of Q from the exact posterior. Minimizing F therefore does two jobs at once —
it scores the model and it *is* the belief update. In the driver model the "family" is
the particle set: weighting and resampling are the minimization.

**Why the main text skipped it.** The particle filter can be understood operationally
(chapter 06) without the variational story; the identity above adds rigor, not intuition.

**Where to go.** Any modern treatment of variational inference (Blei, Kucukelbir &
McAuliffe, "Variational inference: a review for statisticians", JASA 2017). For the
active-inference-specific assembly, the tutorial paper of Smith, Friston & Whyte, "A
step-by-step tutorial on active inference" (Journal of Mathematical Psychology, 2022)
(verified as the standard entry point; discrete-state, see section E).

## C. Markov blankets

**What it is.** The formal device separating "a thing" from "its environment": a set of
states (sensory + active) through which all statistical influence between inside and
outside must pass. The free-energy principle's broadest claims are stated in terms of
blankets — a system's inside models its outside *because* the blanket makes their coupling
indirect.

**Why the main text skipped it.** For a driver model, the blanket is trivial: the
observation vector in, the control vector out. The concept earns its complexity only when
one asks what counts as a system at all — a philosophy-of-science question.

**Where to go.** Kirchhoff et al., "The Markov blankets of life" (Journal of the Royal
Society Interface, 2018) for the enthusiastic case; Bruineberg et al., "The Emperor's new
Markov blankets" (Behavioral and Brain Sciences, 2022) for the sharpest critique — read
together, they are the debate in miniature.

## D. The biology and philosophy debate, with references

Chapter 01 gave the three-claim structure (process theory / universal principle /
engineering framework) and took a position only on the third. The fuller reading list,
both directions:

- **For the process theory:** Friston (2010) above; Parr, Pezzulo & Friston, *Active
  Inference: The Free Energy Principle in Mind, Brain, and Behavior* (MIT Press, 2022) —
  the book-length statement, and the best single reference if the group buys one.
- **Sympathetic but independent:** Clark, "Whatever next? Predictive brains, situated
  agents, and the future of cognitive science" (Behavioral and Brain Sciences, 2013) —
  predictive processing without commitment to the strongest principle; the natural
  companion to *Great expectations* (verified — co-authored by this project's owner).
- **The critiques:** Bruineberg et al. (2022) above on blankets; Colombo & Wright, "First
  principles in the life sciences: the free-energy principle, organicism, and mechanism"
  (Synthese, 2021) on what the principle explains; the widely cited unfalsifiability
  worry is stated crisply in commentaries accompanying Clark (2013) and the BBS treatment
  of the principle.
- **The dark-room debate** (chapter 13's FAQ): Friston, Thornton & Clark, "Free-energy
  minimization and the dark-room problem" (Frontiers in Psychology, 2012).

Our position, restated for the record: the driver model's evidential standing rests on
held-out prediction and ablation [Paper] [OSF], and would be unchanged by any outcome of
this debate.

## E. The discrete-state formulation, and pymdp

**What it is.** Most of the active-inference literature — including nearly all tutorials
— works with small discrete state spaces: a handful of states, observations, and actions,
with the generative model written as labeled probability matrices (A for observation
likelihoods, B for transitions, C for preferences, D for initial beliefs). Expected free
energy is then a sum over a few dozen entries, and everything can be inspected by hand.
`pymdp` (Heins et al., Journal of Open Source Software, 2022; verified) is the reference
Python library for exactly this.

**Why the main text skipped it.** The driving problem is continuous, high-dimensional,
and long-horizon; none of the matrix machinery transfers directly, and the Waymo/TU Delft
line had to build the particle-filter/CEM architecture *because* the tutorial formulation
does not scale to it (`notes/02_active_inference_overview.md` §6). A reader who learns
the discrete formulation first must then unlearn the expectation that A, B, C, D matrices
will appear in this codebase — they never do.

**Why it is still worth a day of someone's time.** The discrete world is where the
*concepts* — preference as probability, epistemic value as expected information gain, the
pragmatic/epistemic split — can be verified by hand on paper, which some readers find is
what finally makes them click. The pymdp tutorial notebook ("active inference from
scratch") is the recommended single exercise; its risk/ambiguity decomposition of
expected free energy is an equivalent split to the pragmatic/epistemic one used here,
and mapping one onto the other is a genuinely instructive afternoon.

## F. Where the equations of this specific model live

For the reader who wants the real thing rather than any tutorial: the Supplementary
Information of Schumann et al. (2026) is self-contained and, in our experience, more
readable than the framework literature (verified — it is in `papers/active-inference/`
with extracted text in `notes/paper_text/`). The map: §2.2 observation model and looming;
§2.3 beliefs; §2.4 preferences (Eqs. 44–52 — the part this project depends on); §2.5
planning and evidence accumulation. This project's `notes/02_active_inference_overview.md`
is the bridge document between that SI and the comfort-zone program, written at Level-2
density throughout.


---

# Chapter 15 (appendix): the datasets

*Part of the WaymoActiveInference handbook. Added 2026-08-26 ({{R3}} round). Every number
quoted anywhere in this handbook comes from one of the datasets below. This appendix exists
so that a reader can check what a claim rests on without hunting through the repository, and
so that the standing caveats attached to each source are stated once rather than repeated.*

{{R3}}One rule applies across all of them and is worth stating first: **no dataset here is a
measurement of a real driver's behavior in a real conflict.** Two are model output, one is a
synthetic scenario population, one is digitized from published figures, and one is human
judgment about video. The project's decisive step remains a comparison against behavior, and
nothing in this appendix substitutes for it.

## 15.1 The authors' OSF deposit (model output)

{{R3}}**What it is.** Per-run simulation output from Schumann et al. (2026) for all three
published scenarios, 32 seeds per condition, at `external/gs4bu-osfstorage-archive/`
(3.1 GB). Contains setups, outcome analyses and per-timestep pickles.

{{R3}}**What we use it for.** The reference against which our replication is checked, the
source of the authors' true response-time distribution (median 1.20 s, sd 0.66 s), and the
896 deposited trials on which our evidence-accumulator drift rate was calibrated. Our
comfort-zone calibration recovers this model's brake onsets from kinematics alone at a
median error of 0.0 s, which is the strongest existing evidence that the method works.

{{R3}}**Caveats.** It is the *model's* behavior, not a driver's. The deposit README's stated
axis order for the policy arrays is wrong — they are (H, timesteps, seeds, 2). The oncoming
and intersection folders and the ablation grids remain untouched.

## 15.2 QUADRIS (synthetic scenario population)

{{R3}}**What it is.** 5 000 synthetic rear-end scenarios at 20 Hz, every one ending in a
collision, generated by Wu et al. (2025a) by sampling lead-vehicle profiles and initial
conditions from multivariate models fitted to SHRP2 and CISS, then simulating a follower with
a modified IDM plus the Svärd et al. brake-response model. Each scenario carries a weight
proportional to its real-world frequency times the human crash probability.

{{R3}}**What we use it for.** The reference population for the entire crash-causation study
(chapter 08): severity, urgency and braking distributions, and the equivalence comparison.

{{R3}}**Caveats, and these are severe.** Every scenario is **conditioned on having crashed**
under the generator's own driver, so re-simulating it answers "what does a different driver
do in situations that crashed for this one", not "what crashes does this driver produce in
traffic". Exposure reweighting leaves an effective sample size of 44.7 out of 5 000, and 295
scenarios never crash under the control model at all. Further, the weights are concentrated
enough that even the *crash-weighted* reference has an effective sample size of about **950**
rather than 5 000, which matters for how finely it can be binned and for how much resolution
any equivalence test against it can have (chapter 08).

## 15.3 The digitized Bärgman et al. (2024) distributions

{{R3}}**What it is.** The SHRP2 off-road glance duration distribution and the 45-crash
maximum-deceleration histogram, recovered from the published figures by
`replication/causation/digitize_b24.py`. The glance distribution is vector-exact, with two
independent axis calibrations agreeing to within 0.9%; the deceleration histogram recovers
integer counts summing to exactly 45.

{{R3}}**What we use it for.** The input distributions for the glance and deceleration
components of the causation model.

{{R3}}**Caveats.** The deceleration histogram is coarse — about a dozen distinct values from
45 crashes — and this is the direct cause of one of chapter 08's findings: our follower
produces 375 distinct minimum-acceleration values against the reference's 1 853, which shows
up as a failure to reproduce the *shape* of the braking distribution.

## 15.4 The clip-rating and button-press study (human judgment)

{{R3}}**What it is.** A crowdsourced study run by the QUADRARUM group, at
`external/01_studies/`. Participants watch first-person driving videos recorded from a
vehicle described as having an SAE Level 2 system, and report when they would intervene.
Three paradigms across two data collections:

| paradigm | when | participants | what the participant does | outcome |
|---|---|---|---|---|
| Sequence | Aug 2025 | 33 | watches clips of one event **in temporal order**, each stopping at a fixed point | perceived safety 0–10, binary intervene, a third scenario-specific question |
| Random | Jan–Feb 2026 | 47 | same, but clips **shuffled** so no progression is visible | as above |
| Button press | Jan–Feb 2026 | the same 47 | watches continuously and presses SPACE at the moment they would intervene; **the trial ends at the press** | a right-censored intervention time |

{{R3}}**The scenarios.** Four, each with a criticality manipulation:

- **Cut-in** — a car (TTC2–TTC8) or a truck (TTC4–TTC8) merges into the ego lane. Criticality
  is the time-to-collision at manoeuvre onset. In every clip the lane change begins at trace
  second 15.32 and completes 2.4–2.6 s later, and the clips start at trace second 5.0, so the
  onset always falls at video time 10.32 s. Clips are truncated at onset + 0, 0.3, 0.6, 0.9,
  1.2 and 1.5 s (labelled C1–C6, C1 being pre-onset).
- **Cyclist overtake** — the ego overtakes a cyclist at a lateral clearance of 0.5, 1.0 or
  1.5 m. Smaller is more critical.
- **Left turn across path (LTAP)** — the ego turns left across an oncoming vehicle's path at a
  post-encroachment time of 0–4 s, with the oncoming vehicle at 50 or 70 km/h. Lower PET is
  more critical; analyses restrict to 50 km/h.
- **Truck overtake** — the ego overtakes a truck displaced 0–1 m from its own lane centre
  toward the ego. **Larger is more critical here, the opposite direction to every other
  scenario.**

{{R3}}**The stimulus kinematics.** 67 trace files hold the simulator's full vehicle states at
10 Hz for every clip — positions, speeds, headings, lanes, bumper positions and bounding
boxes. This is what makes the study usable for our purposes: the comfort-zone field along a
clip can be computed exactly, and **the ego vehicle never responds** (it holds a rigorously
constant speed in the cut-in and overtake clips, and a fixed scripted profile in LTAP), so
that field is a fixed function of time, identical for every participant and repetition.

{{R3}}**Caveats, several of which any analysis depends on** — the first three are not in the
study's own documentation and were found by checking the traces:

- The `Acceleration_mps2` column is **unsigned and of undetermined meaning**. It is never
  negative in any of the 67 files; it is non-zero while a vehicle holds constant speed; and
  it matches neither longitudinal nor total acceleration magnitude at fine scale. Do not use
  it — differentiate `Speed_mps` instead.
- The **first and last frames are simulator teardown artifacts**, roughly 8.5% of rows, which
  produce derived accelerations of 100–250 m/s² if left in.
- **Truck bounding boxes are broken** (`Length_m = 0`), so truck dimensions must be supplied
  externally for any bumper-to-bumper or looming computation.
- **Design order is perfectly confounded** in the 2026 collection: every participant did
  Random before Button, never counterbalanced, so any difference between them could be
  practice or fatigue rather than modality.
- **Anticipation and satisficing.** By the button sessions participants had seen every clip
  about four times. The median press at the most critical cut-in level falls 0.10 s after
  manoeuvre onset, which is faster than a simple keypress reaction time. Separately, the
  button paradigm invites *satisficing* — pressing where one believes one would react rather
  than where the boundary actually lies. Measured against the clip-based design, the button
  paradigm is systematically earlier, by up to 0.26 in probability at intermediate
  criticality, converging at high criticality.
- The **Sequence paradigm shows substantial autocorrelation** between consecutive responses,
  which is why the Randomized design is the one carried forward.

{{R3}}**What we use it for, and the ordering that follows.** The Randomized clip-based design
is the primary source: it samples the *cumulative* response-time distribution at six known
truncation points and is the least contaminated of the three. The button-press data is used
for validation rather than fitting, because of the satisficing bias. The Sequence data is not
used for boundary estimation. Chapter 11 sets out the fitting scheme.


---

# Chapter 16 (appendix): an external comfort-zone model built on required deceleration

*Part of the WaymoActiveInference handbook. Added 2026-09-02 ({{R6}} round), restructured the
same day after Jonas asked for a plainer statement of what each approach is better at.
**Early work, and external to this project.** A colleague's working document proposes a
comfort-zone boundary defined through the driver's habitual control capability, with the
required deceleration as its cut-in cue; a separate LLM-assisted analysis, commissioned by
Jonas and kept in its own repository, implemented that model and fitted it to the same second
cut-in study this project used at gate R.2. This appendix compares that work with ours. It
is not a replication (the external results were not re-run here) and it is not part of this
project's evidence chain. The external material lives outside this repository, reached
through the shortcut in `OthersWork/`; that folder is deliberately not part of the standing
context for sessions on this project (`handover.md` §5), and nothing in the project's cards,
gate records or claims depends on it. Where this appendix quotes an external number it says
so; every number of ours names its tracked output.*

## 16.1 The two approaches in one paragraph each

{{R6}}**Theirs.** The boundary is where the driver can no longer resolve the situation with
routine control. For a cut-in the routine control is braking, so the cue is the required
deceleration a_req = Δv² / 2(g₀ − g_min − Δv τ), with a minimum acceptable gap g_min and a
response delay τ as the driver's margins and a habitual limit a_h as the driver's capability;
the boundary is the θ-quantile of a cumulative normal on log a_req. A lateral gate w, the
probability that the intruder will come within a minimum clearance over a fixed 3 s
look-ahead, multiplies the whole thing: before the intruder "binds", the gap does not
matter. Fitted to the second cut-in study (trial-level maximum likelihood, lapse terms, two
held-out fold schemes) by the external analysis.

{{R6}}**Ours, as it stands after 2026-09-02.** The boundary is a per-driver threshold (a level)
on one criticality axis, applied when a gate says the situation counts. On the cut-in the
axis is the optical expansion rate of the other vehicle, θ̇ ≈ W Δv / g² (card EL.1 found the
equal-weighted log gap and log TTC rule; card EL.1b confirmed it is θ̇ fitted directly,
`replication/czb/out/cutin2_looming.md`); the gate is the same fixed-horizon clearance
projection as theirs, credited on our pipeline (card G.1, `out/cutin2_gate.md`); the level is
the hierarchical per-driver quantity of the stage-1 estimator, shared across scenarios
(`out/cross_scenario_consistency.md`). This replaced the active-inference preference field,
which lost at gate R.2. Fitted with cell-level weighted least squares on the same study,
leave-one-starting-TTC-out folds, rules committed before each run.

## 16.2 What each is better at

{{R6}}The table is the appendix. Numbers are held-out weighted RMSE on the 288 post-onset cells
unless stated; lower is better; the measured sampling-noise floor is 0.118. "Ours" and
"theirs" use different fitters (cell-level least squares against trial-level likelihood),
so numbers compare across pipelines only in their ordering; within each column they are
exact.

| question | ours | theirs | who is better, and why |
|---|---|---|---|
| Describing where the cut-in boundary is | θ̇ threshold **0.113**; gated **0.103** (3 and 6 parameters) | full model **0.149** (8 parameters), a tie with a gap threshold (0.147) | **Ours.** At the noise floor with fewer parameters; their model as written does not beat gap alone. On our pipeline their walled a_req scores 0.171 (`out/cutin2_external_cue.md`) |
| Knowing when the situation starts to count (the gate) | not part of our model until 2026-09-02; our field's closure-time gate *hurt* (about 44% of the field's loss) | fixed-horizon gate predicts the pre-onset cells out of sample (0.03) | **Theirs first.** We imported the idea and it passed the same test on our rule (G.1: pre-onset cells 0.032 out of sample, and the post-onset fit improves) |
| Evidence across scenarios | four scenarios; one per-driver level shared at 69% of the reliability ceiling; transfer tests; left-turn and ellipse constructions | one scenario, one study; scenario-agnostic ambition stated, not tested | **Ours.** Theirs has no cross-scenario claim yet |
| A per-driver measurement | per-scenario split-half reliability 0.93–0.98 | one per-driver parameter, split-half 0.88 | **Equal.** Different designs; both find the per-driver criterion to be the reliable object |
| A mechanism behind the cue | none claimed: a psychometric threshold on a perceptual variable | required deceleration with named margins, a closed-form boundary | **Theirs as a story, but its equation fails.** Their own nested test rejects the Δv² exponent (fitted 0.39, bootstrap 0.23–0.56) on this paradigm |
| The speed dependence | θ̇ ∝ Δv / g², so gap ∝ √Δv | free exponent on Δv: 0.39; unconstrained probit: gap / Δv^0.42 | **Equal, and the same number.** Two pipelines find a speed exponent of about 0.4–0.5 against 1 for TTC and 2 for any deceleration cue |
| Physics-first cues | the field's counterfactual: 4–6× too sensitive to speed (pipeline review) | a_req with no margins: worse than chance; margins carry the fit | **Both fail in the same direction** |
| Real driving | nothing; frozen video only | nothing; frozen video only | **Neither.** Both say so |

## 16.3 The one thing the comparison settled

{{R6}}Their speed exponent of about 0.4 had no mechanism (their note's open blocker asked
what the cue could be, and offered a perceptual compression of closing speed as one reading).
Our EL.1 rule supplies it without any compression: a threshold on the optical expansion rate
implies gap ∝ √Δv exactly, because θ̇ ≈ W Δv / g². Their gap / Δv^0.42 and our gap / Δv^0.5
are the same cue seen from two sides, and it is the classic looming variable of the visual
control literature (and the quantity the active-inference model's own perception stage
computes). One contrast with that literature is worth stating: in a driving simulator, Xue
et al. (2018) found inverse tau (θ̇ / θ = 1 / TTC) the better cue for brake onset; on this
video paradigm the order reverses (θ̇ 0.113 against 1/TTC 0.168). Whether that is the
paradigm or the task is the question naturalistic onsets would settle.

## 16.4 Where they differ, in more detail

{{R6}}**The margin: a wall or a slope.** Their best-determined quantity is a hard minimum gap
(g_min ≈ 11.5 m, bootstrap 10.6 to 12.7), below which no habitual braking suffices; ours is a
smooth threshold with no wall. Put on our registered pipeline with the wall fitted inside
each fold, their cue scores 0.171 against our rule's 0.114 (`out/cutin2_external_cue.md`,
walls 9–12 m), so the wall does not substitute for the second axis on this data.

{{R6}}**The gate, and what we changed.** Both constructions gate the longitudinal cue by a
predicted lateral encroachment. Theirs projects the clearance forward over a fixed horizon;
ours projected the overlap to the moment of longitudinal closure, which depends on TTC and
suppressed the field exactly where participants respond most. Card F.1
(`out/cutin2_field_horizon_gate.md`) put the fixed horizon into the field's own gate: the
field improves from 0.347 to 0.261, the first field variant to beat chance, which confirms
the attribution; it stays far behind the gap (0.152), so the field is still ruled against.
Card G.1 put the same gate in front of our rule, where it belongs: the pre-onset cells are
predicted out of sample (0.032) and the post-onset fit improves (0.103). The fitted gate is
softer than theirs (s_l ≈ 1.0 m against ≈ 0.3 m); both analyses agree that the design
samples only "closed" and "open", so the gate's shape is unidentified either way.

{{R6}}**Within- versus between-driver spread.** Their population σ splits into a within-driver
0.80 and a between-driver 1.16 (log units on log a_h), with the warning that the boundary is
a different quantile under each reading. Our stage-1 estimator separates the same two things
by construction (a per-trial lapse and probit spread against a hierarchical per-driver level),
and the ellipse note's population-A / population-B distinction is the same warning in our
terms. The parametrizations are not numerically comparable.

{{R6}}**Independence.** The external analysis chose one of its fold schemes to match our
registered one and cites our R.2 output, so the two are not blind on the fold design; they
are on the models and the fitters. The convergence in 16.3 should be read with that in mind.

## 16.5 What this appendix does not do

{{R6}}It does not re-run the external analysis, check its code, or verify its references (the
external note marks them as from memory). It does not adopt any external number into this
project's claims; the two ideas we took from it, the fixed-horizon gate and the reading of
the speed exponent, each passed a pre-stated test on our own pipeline before entering the
model. And it does not settle the exponent question for real driving: both analyses are on
frozen video with no self-motion, and both say so. The colleague's document and the external
note remain the sources for anything said about the external model; this appendix is a
reading of them, dated, and marked as early.
