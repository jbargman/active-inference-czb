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
