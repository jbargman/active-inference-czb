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
