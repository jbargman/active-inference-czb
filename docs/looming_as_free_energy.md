# Looming as free energy: the ways to read it, and what each predicts

*2026-09-22, on Jonas's instruction: "Continue pursuing the possibility of using active inference
for CZBs. It may be that a looming threshold fits the data better, but if we can explain it in
terms of fundamental free energy it is more anchored in fundamental science, but we should not
just assume it works: we have to probe the different ways to think about it." A design note, not
a result; the cards it proposes are pre-stated and run separately, and section 6 records their
outcomes as they arrive. Opinions are marked.*

## 1 What is on the table

The measurement model that fits the second cut-in study is

> share who intervene = lapse + (1 − lapse) × GATE × Φ((log θ̇ − log θ̇₀) / σ),

with θ̇ the optical expansion rate of the cut-in vehicle at the response moment (card EL.1b), the
gate the probability that the vehicle's lateral clearance projected 3 s ahead falls below a
minimum (card G.1), and θ̇₀ and σ a level and a spread. It scores 0.1027 held out; the
active-inference constructions of the 09-18 to 09-22 arc scored 0.29 to 0.32. The question is not
which fits better; it is whether the model that fits *is* an active-inference model written in
different words, and if so, which of the several possible readings it is, because the readings
make different predictions.

Card JJ.6 settled one part on 2026-09-22: **the gate is the belief.** Card JJ.1's fan, read as
"the probability that the other's body is in my lane within T seconds", reproduces G.1's gate
where it is closed (pre-onset 0.0354 against 0.0318, nothing fitted) and fails to reproduce its
grading where it opens, because the intention posterior is binary on these cells. So the gate has
an active-inference reading already: a posterior over the other's intention, propagated through
the predictive model. What follows concerns the other three parts, the axis, the level and the
spread, and one structural question, the horizon.

## 2 Four readings

**Reading A, the horizon-summed expected free energy.** The standard form: G(π) = Σ_τ E_q[−log
C(o_τ)] + epistemic terms, over a planning horizon, with C a prior preference over observations.
Cards JJ.2, JJ.2c, RE.4b, S1.6, JJ.5 and JJ.5b all read the data this way, with the preference
being the released collision and braking-margin terms, the released τ⁻¹ term, or an admissibility
constraint. **All are anti-ordered with the response**, and the checks of the review found why: a
one-sided preference summed over the horizon of a `continue` policy that drives through the lead
counts the number of steps before contact, which grows with TTC, while participants respond to
proximity. JJ.5b removed the sum (per-step rate, maximum, first step) and the inversion went with
it (ρ(gap) +0.662 → −0.228), but no axis appeared, because the released term is a TTC quantity.
**This reading is the one the data reject, and the rejection is structural: not the constants,
not the functional, the horizon sum itself.** (Opinion: it should be said plainly to JJ, because it
is the difference between a planning model and a comfort-zone model.)

**Reading B, the free energy of the present observation.** In the continuous-time formulation
action minimises the free energy of *current* sensory states, F ≈ ½ ((θ̇ − μ)/σ_o)² + …, where μ
is what the generative model predicts and σ_o the sensory precision. With a prior expectation that
looming stays at or below a level θ̇₀ (a one-sided prior: −log C(θ̇) = ½ ((θ̇ − θ̇₀)/σ_c)² for
θ̇ > θ̇₀, else 0), the prediction error is (θ̇ − θ̇₀)₊ and the reflex that cancels it is to brake.
A driver responds when the error is non-zero. If the driver's belief about θ̇ (through sensory
noise) or about θ̇₀ (a population of levels) is log-normal, P(respond) = Φ((log θ̇ − log θ̇₀)/σ).
**This reading IS the threshold model**, with the level the mean of the prior over looming and the
spread its precision (or the sensory precision; §3 says how to tell). It has no horizon, so it
cannot be inverted by one, and it is gated by the belief of card JJ.6 because the prior over
looming applies to a vehicle that is, or is about to be, in the ego's path. It is the reading I
recommend (opinion), because nothing in it is fitted that the measurement model does not already
fit, and the two fitted quantities acquire a meaning.

**Reading C, the one-step expected free energy, a decision.** Keep the preference of B but let
the driver *compare policies* at the present step: G(continue) = ½((θ̇ − θ̇₀)/σ_c)²₊, G(brake) = the
effort cost e = ½(a/σ_a)² (the released control-effort term), and choose brake when G(continue) >
G(brake). Deterministically that is a threshold at θ̇* = θ̇₀ + σ_c √(2e): the effort term raises
the level, which is a substantive prediction (a driver with a higher tolerance for braking effort
responds earlier). With the softmax policy posterior of active inference, P(brake) =
σ(γ (G(continue) − G(brake))), a *logistic in the squared excess*, not a probit in log θ̇. Readings
B and C therefore differ in the link function, and that is testable on the cells (card JJ.8). If
the data cannot tell them apart, the difference is philosophical; if they can, one is right.

**Reading D, surprise and epistemic value.** −log p(θ̇ | model), the surprise of the looming
observation under a generative model that predicts the other holds course, and the information
gain about the other's intention. On this design both are gates, not axes: the stimulus vehicles
hold constant speed, so the looming a course-holding model predicts is the looming observed
(surprise is zero post-onset), and the intention posterior jumps from 0.07 to 1 in every cell
(card JJ.6), so the information gain is one constant post-onset and another pre-onset. Card HS.1
tested situational surprise as the onset on 2026-09-13 and it lost to the anticipatory gate;
JJ.6 is the epistemic reading done properly, and it is the gate. **Nothing more to test here on
these data**; on naturalistic data, where the other's speed varies, reading D becomes an axis
candidate again.

## 3 What the readings predict differently, and the cards that test them

| question | reading B | reading C | card |
|---|---|---|---|
| the link function | probit in log θ̇ | logistic in the squared excess (θ̇ − θ̇₀)²₊, with an effort offset | **JJ.8**: fit both with three parameters on the fixed looming axis and G.1's frozen gate; rule: held-out difference below 0.005 is "indistinguishable on this design" |
| the scale of the spread | multiplicative (a spread in log θ̇: a prior over levels, or Weber-like sensory noise) | additive if the noise is sensory in absolute θ̇ (the released agent's `sigma_phidot` is absolute, 1e-3 rad/s) | **JJ.8** also fits the probit in θ̇ (not log); the registered R.2 script scored raw against log scales for its other axes, never for looming |
| what the spread is | prior precision or sensory precision, indistinguishable on one study | | JJ.4's two results bear on it: the truck's criterion is sharper (a wider vehicle gives a larger θ̇ at the same gap, so *absolute* sensory noise predicts a smaller spread in log θ̇ for the truck by the width ratio, about 1.3, where JJ.4 found 1.55 with about half attributable to axis geometry per the review); and drivers are sharper in the car than at a screen (sensory precision, or the criterion's) |
| the effort offset | none | the level rises with the driver's effort tolerance | needs per-driver effort data; not testable here, noted for the naturalistic plan |
| the horizon | none | none | reading A is the one with a horizon and is rejected (§2) |

Card JJ.8 is the one that costs an hour and settles something. The rest is for the record.

## 4 The mapping, written out

For reading B with a log-normal population of levels, θ̇₀ ~ LogNormal(m, σ), and a deterministic
response when θ̇ > θ̇₀: P(respond | θ̇) = P(log θ̇₀ < log θ̇) = Φ((log θ̇ − m)/σ). The measurement
model's `level` is exp(m), the population median of the prior's mean over looming, and `spread` is
σ, the population spread of that mean. Card TR.1's per-driver levels are then per-driver priors,
and their consistency across scenarios (+0.647) is the claim that a driver carries one prior over
looming into every scenario. The percentile deliverable is a percentile of that prior over
drivers. Nothing new is fitted; the words change.

For reading C with the same population and a softmax posterior with precision γ:
P(brake | θ̇) = ∫ σ(γ [½((θ̇ − θ̇₀)/σ_c)²₊ − e]) dP(θ̇₀). With γ → ∞ this is reading B's probit with
the level shifted by σ_c √(2e). With finite γ the curve is flatter at the top (a driver who is far
past the level still hesitates with probability σ(−γ·large) → 0, so not flatter there; flatter at
the bottom: P(brake) = σ(−γ e) > 0 below the level, which the lapse parameter absorbs). The
distinguishing feature is the shape between: quadratic growth of the argument in θ̇ − θ̇₀ against
linear in log θ̇. On a design spanning θ̇ from 0.004 to 1.1 rad/s (two and a half decades) the two
are not close, so JJ.8 has power.

## 5 What would make me give up the active-inference reading (opinion)

Not a worse score: reading B fits by construction. It would be a *prediction that fails*: JJ.8
finding the logistic-in-squared-excess link clearly better than the probit (then the decision
reading C wins and the reflex reading B is wrong) is fine either way, both are active inference.
What would hurt is the gate: if a graded intention belief (card JJ.6b) cannot reproduce G.1's
graded gate however the likelihood is made consistent with the generative model, then the gate
the data want is not a belief about intention but a geometric projection, and the active-inference
account of emergence is decorative. And on naturalistic data, where reading D becomes an axis
candidate, a looming-surprise axis that scores no better than the looming level would say the
generative model adds nothing to the preference.

## 6 Outcomes, as they arrive

*(appended by the cards; do not edit the sections above to match)*
