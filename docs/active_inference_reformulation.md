# Reformulating the comfort-zone measurement inside active inference, a design note

> **[2026-09-22, review] Read `docs/review_2026-09-22.md` before relying on this note.** Four things
> it says do not stand: (1) "the braking-margin term is an inverted comfort-zone boundary
> (rho -0.861)": that number is a horizon-sum accounting effect under the project's ramp form of the
> term, and pointwise the required deceleration is ordered the human way (+0.633); (2) the identity
> "to 7e-16": the tracked report gives 2.5e-07 and its own criterion failed; (3) the "released
> planner" results of cards RE.1 part C and JJ.2b (never brakes; 19 of 24 rows): the test read only
> the first, clamped, step of each plan, and in JJ.2b the ego was off the road; (4) 0.2705 is not
> chance (chance is 0.320) and is the best of 20 vectors, not of 648. The note's card numbering
> (RE.3 to RE.6) also no longer matches the cards that were run. This PDF has not been rebuilt.

*2026-09-18, written after cards JJ.2, JJ.3, JJ.2b, RE.1 and RE.2, on Jonas's question: "think
more about how the problem we have possibly could be reformulated to fit in the active inference
framework. What would we have to do differently for this to work. Again, I feel that with the
right formulation and the right framing, it should work."*

**Status: a design note. Nothing here is authorized, nothing has been implemented, and the rules
in §6 become binding only when Jonas has read them.** Where a value is a placeholder it says so.
Opinions are marked as opinions. Every number quoted carries its file.

---

## 0 The answer in two paragraphs

**The framework is not what failed, and there is now direct evidence for that rather than an
argument.** Card JJ.2b gave the model its own policy space — the released planner instead of a
hand-made longitudinal menu — and the matched-TTC ordering, the thing gate R.2, card JJ.2 and
card JJ.3 all failed on, went from **0 of 24 rows** in the human direction to **19 of 24**, with
ρ(axis, gap) turning from +0.848 to −0.308. That is the largest movement any card has produced on
this design, and it came from changing the *framing*, not a constant. What it did not do is make
the axis usable: the ordering is right-signed and weak, the held-out score stays at chance, and
the reason is the second paragraph.

What failed is one identification, made at the very start and
never questioned, and card RE.2 has now bounded how much of the failure it accounts for: sweeping
648 parameter vectors over everything a driver could plausibly differ in leaves **0 of 648**
ordering even half the matched-TTC rows. So this is not a calibration problem. It is that
**the released model's braking-margin term was taken to be the comfort-zone boundary**.
`src/aidriver/preferences.py` says so in its own docstring — "that boundary, a_ego,req = −a_max,
is the model's own operationalisation of a comfort-zone boundary, and `comfortzone` builds on
it" — and every card since has measured a level set of it. Card RE.2 now measures what that term
does on the human data: its contribution to the model's criticality signal correlates **−0.861**
with the share of participants who would intervene. It is not weakly related to comfort; it is
**inverted**. Meanwhile the one factor in the released preference that has the shape of a comfort
boundary, the inverse-tau preference buried inside the collision factor, correlates **+0.358** —
the right sign — and is swamped by four orders of magnitude. The reformulation is therefore not a
new construction bolted on top; it is to stop measuring the comfort zone on the dread-zone term,
to put the comfort factor on the variable the data name, and to fit the driver's parameters
instead of assuming the authors'.

---

## 1 What we now know, with the files

| finding | number | file |
|---|---|---|
| The released criticality signal is Eq. 13's ε under the current plan, and our `G(continue)` is that same object | agree to 7e-16 | `replication/causation/re1/re1_rear_end_criticality.md` §0 |
| ΔG — best alternative minus continue — is a quantity the model never forms | the planner uses only the argmin | ibid. |
| On a certain constant-speed prediction, ε is the same at a 0.5 s headway at 110 km/h, at 3.5 s, and on an empty road | 23 nats, all three | ibid. §D |
| At matched TTC, ε is ordered backwards | ρ(ε, gap) +0.83 to +1.00 against the humans' −0.862 | ibid. §B2 |
| The released planner's escape on this design is a steer, never a brake | 36 of 36 cells, and 378 of 378 on the study's real traces | ibid. §C; `out/jj2b_steer_menu.md` §2 |
| **Giving the model its own policy space repairs the DIRECTION of the ordering** | matched-TTC rows ordered the human way go from **0 of 24** to **19 of 24**; ρ(axis, gap) from +0.848 to **−0.308** | `out/jj2b_steer_menu.md` §3 |
| ...but not the magnitude: the repaired ordering is still weak | ρ(axis, share) +0.169, held out 0.3161, still chance | ibid. |
| On the study's stimuli the speed, acceleration, steering and lane factors contribute **exactly zero** under "continue"; ε is collision + safety and nothing else | −1.2e-14 at every one of 378 cells | `replication/czb/out/re2_preference_family.md` §4 |
| The **safety factor alone** is inverted against the response | ρ(share) **−0.861**, ρ(gap) +0.810 | ibid. |
| The **collision factor alone** has the right sign but a weak ordering | ρ(share) **+0.358**, held out 0.308 | ibid. |
| No parameter vector in the released family orders the cells: 648 swept, the sign is reachable, the ordering is not | 306 of 648 give ρ(gap) < 0, best −0.267; **0 of 648** order more than half the 24 matched-TTC rows; best held out 0.2705 | ibid. §1, §5 |
| Most of what the sign responds to is the severity's linearity in closing speed | flattening it moves the median ρ(gap) from +0.296 to −0.249 | ibid. §2 |
| ΔG on the cut-in scores chance | 0.3202 against chance 0.320 | `out/jj2_rollout_cutin.md` |
| The project's own best axis is the optical expansion rate | 0.1137 ungated, 0.1027 gated, noise floor 0.118 | `out/cutin2_gate.md`, `out/cutin2_looming.md` |
| Drivers are four times sharper in the car than in front of a frozen clip | ratio 4.34 [2.38, 7.93] | `out/jj4_precision_spread.md` |
| A bigger apparent size gives a sharper criterion | truck σ_resp 0.273 against the car's 0.424, +60.6 LOPO | ibid. |

The last two matter more than they look, and §4 item 5 says why.

---

## 2 Three assumptions the project made that active inference does not require

**2.1 That the comfort-zone boundary is a level set of a scalar.** In active inference behavior
follows from `argmin_π G(π)`. There is no scalar called criticality. The line between
"comfortable" and "not" is the **switching surface** where the argmin stops being "continue", and
that surface is in general not a level set of any of the scalars this project has tried — the
pragmatic deficit (gate R.2), ε (card RE.1), ΔG (card JJ.2). Forcing a
`Φ((x − c) / σ)` response model onto it assumed a monotone scalar that the framework never
promised. *[Opinion: this is the assumption that produced the most wasted work, because it is
invisible — it looks like the neutral statistical form the project uses everywhere else.]*

**2.2 That the model's parameters are known and the scene is the unknown.** The authors calibrate
`a_OV,min` **per scenario**, through a separate free-following analysis; their parameter vector is
a property of their simulation study, not of any driver. The project then asked "does this vector's
field predict humans?", which tests someone else's calibration. The native question is the inverse:
**a driver's preferences are what a driver IS, so infer them from the responses.** The comfort-zone
boundary is then derived from the fitted parameters, per driver, per scenario, by construction.

*Card RE.2 tested this assumption on its own and the answer is only half what I expected, which
changes item 3 of §4 from a suggestion into a requirement.* Sweeping 648 vectors over the five
parameters a driver could plausibly differ in, the *sign* of the ordering is reachable — 306 of
648 give ρ(gap) < 0 — but **no vector orders even half of the 24 matched-TTC rows** and the best
held-out score is 0.2705, chance. So fitting θ instead of assuming the authors' is necessary and
**not sufficient**: within this functional form there is no driver whose comfort zone orders these
cells. The factor the sign responds to is the collision severity's proportionality to impact
speed, which is a property of the form, not a constant a driver could differ in.

**2.3 That the response is a function of the true scene.** The agent acts on its belief, and the
belief depends on the paradigm. A frozen monocular clip conveys distance and closing speed far
less precisely than a moving binocular view, and card JJ.4 has now measured exactly that:
σ_resp 0.858 s on video against 0.198 s on the test track, ratio 4.34. In the current
formulation that ratio is a nuisance parameter. In the reformulation it is **the observation
model**, and it is measured rather than fitted.

---

## 3 The reformulation

> **Measure the driver's preferences, not the scene's criticality.**
>
> P(intervene | scene, θ, paradigm) = P( argmin_π G(π; θ, b) ≠ continue ),
>
> where **b** is the belief the paradigm affords, **θ** is a small set of the driver's own
> preference parameters, and the policy set is the model's own — including steering. Fit θ per
> driver. The comfort-zone boundary is the switching surface θ induces; the deliverable, a
> percentile over drivers, is a percentile over θ, expressed in whatever scene coordinate an
> application wants.

What this buys, and each of these is a failure the current formulation has actually suffered:

- **The axis problem disappears.** No scalar has to be monotone in criticality. Card JJ.2's DROP,
  card JJ.3's left turn, gate R.2 — all three were failures of monotonicity, not of the framework.
- **The gate disappears.** The pre-onset cells are the cells where continuing wins under any
  plausible θ, so P(intervene) falls to the lapse rate. Card G.1's fitted gate, card HS.1's
  surprise gate and card PC.1's projected-conflict gate were all attempts to bolt on by hand what
  the argmin gives for free.
- **The units problem disappears.** Query **EL.Q4** — "each scenario's axis is in different units,
  so what does EL.2 divide by?" — has no content once the shared object is θ, which has its own
  units (m/s², s, rad/s) and is shared across scenarios by construction. EL.2 stops being a
  rescaling exercise and becomes a transfer test.
- **The trait test becomes a real test.** Card TR.1's +0.647 across mixed units, and card JJ.3's
  +0.261 on a two-valued axis, were both measuring through a broken instrument.

---

## 4 What would have to be done differently, item by item

**1. Stop using the braking margin as the boundary.** This is the one change that is not optional.
`safety_margin` = a_req + a_max is the boundary of **physical avoidability**, not of comfort — it
asks whether the ego could still avoid a lead braking at a_OV,min after a reaction time. The
project's own vocabulary already separates the two: the handbook's *comfort zone* and *dread
zone*, and query TT.Q2 parks "the dread boundary" as a separate object. RE.2 measures the cost of
having conflated them: ρ(share) = −0.861. **The braking margin is a good dread-zone boundary and
an inverted comfort-zone boundary**, and the project has been fitting comfort levels on it since
gate R.1.

**2. Put the comfort factor on the variable the data name.** The released preference already
contains a comfort-shaped factor: inside `log_collision_pref`, when there is no collision and the
other vehicle is ahead, a Gaussian over **inverse tau**, τ⁻¹ = φ̇/φ, with mean 0.2 s⁻¹ and sd
0.125 s⁻¹, one-sided in the released code. This is the only factor in p(o) that bounds an approach
*rate* rather than punishing a catastrophe, and it is the only one whose contribution correlates
with the human response in the right direction (+0.358). Two candidate one-parameter families,
both native to a model that already observes (φ, φ̇):

  - **τ⁻¹ preference, parameter μ_τ.** "The inverse TTC I am content with." Already in the code.
  - **θ̇ preference, parameter σ_θ̇.** A preference on the optical expansion rate itself. This is
    the project's own measured axis (card EL.1b: 0.1137 held out against the gap's 0.1522 and the
    field's 0.3471, at a noise floor of 0.118) with a population already estimated (card EX.2:
    median 0.034 rad/s, 80th percentile 0.071 rad/s at first exposure).

  They differ by a factor of the angular size: θ̇ ≈ τ⁻¹ × (W / gap). Which one wins is an open
  empirical question and not a settled one — query DECK.Q1 records that Xue et al. (2018) found
  τ⁻¹ fitting better than θ̇ for both threshold and accumulator models, while this project's own
  cut-in data prefer θ̇. **Both are one-parameter families and both should be fitted.**

**3. Give the catastrophe factors their proper role.** In the released p(o) the collision cost is
−10 000 and the road-edge cost −15 000, against a comfort factor of order 1. A model whose
comfort term is 10⁻⁴ of its catastrophe term cannot have its comfort boundary read off the sum:
the deposit's own benign-following decomposition puts the collision/safety share at 1.000
(`docs/method_review.md` §4.2), and RE.2 reproduces that at every one of 378 cells. The repair is
structural, not a reweighting: the catastrophe factors belong in the **admissibility of a policy**
(a plan that collides is not a plan), and the comfort factor belongs in the **choice among
admissible plans**. That is also how the dread zone and the comfort zone should differ formally.

**4. Make the response model the switch, not a threshold.** P(intervene) is the probability that
the argmin is not "continue", marginalised over the belief. The per-driver random effect becomes
θ_i rather than a level c_i, and the existing hierarchical estimator
(`fit_stage1_looming.fit_hier_lapse_gated`) has to be re-pointed at that likelihood. The lapse
stays; the "spread" does not — it is replaced by item 5.

**5. Put the paradigm in the observation model, where it is already measured.** The response
spread σ_resp is not a driver property and should not be fitted per scenario. Card JJ.4 measured
it as a property of the stimulus: 4.34× between the frozen clip and the car, and a sharper
criterion for the larger object (truck σ_resp 0.273 against the car's 0.424, +60.6 held-out
log-likelihood units under LOPO). Both are exactly what an observation model on (φ, φ̇) with
angular noise predicts — apparent size enters the precision. **This is the one clean positive
result of the whole JJ arc and it slots straight in.**

**6. Include steering on the model side — this one is already demonstrated.** Ruling JJ1.Q1
removed steering because the stimuli and the naturalistic data carry that constraint, which is
right for the **response** and wrong for the **model**: the released planner escapes by steering
in 378 of 378 of the study's own cells and never brakes. Card JJ.2b ran the correction and it
moved the matched-TTC ordering from 0 of 24 to **19 of 24** rows in the human direction. A policy
comparison that excludes the model's own chosen action is not a comparison, and the size of that
movement is the best evidence in the whole arc that the framing — not the framework — is what has
been wrong. Query RE1.Q2.

  Note what this does *not* fix, because it is the hinge of the whole note: with the direction
  repaired, the held-out score is still 0.3161, chance. A right-signed but weak ordering is what
  you get when the quantity being ordered is dominated by a factor that points the other way. That
  is item 1.

**7. Keep everything that is working.** The cells, the folds, the weighted RMSE, the comparators
on file, the pre-registration-before-the-run discipline, the worklog and the query register, and
the rule that transfer is the test. None of that is implicated in any of the failures above.

---

## 5 The one thing that would make this fail, and it is the project's own central claim

The central claim is that active inference reduces the comfort-zone boundary to **one** scalar per
driver, shared across scenarios. The reformulation makes that claim testable *for the first time*,
because until now every test of it was confounded by the authors' calibration. But it can still
fail, and it should be allowed to:

- A θ̇ (or τ⁻¹) preference is the right comfort factor for **approach** conflicts. The left turn's
  axis is the oncoming vehicle's distance (card B.3.v2: 0.0558; looming ties at 0.0542 only
  because that design holds one speed per cell, so looming is unidentified there rather than
  rejected), and the cyclist overtake's is lateral clearance (card B.1). A single approach-rate
  factor will not carry the overtake, and the released lateral factor could not grade clearance
  at all (`out/overtake_field_check.md`: ρ +0.402 against the clearance label's −0.833).
- So the honest form of the claim is **two** comfort factors, not one: a longitudinal
  approach-rate factor and a lateral clearance factor, with the driver's parameters in both. If
  the two turn out to be independent across drivers, the "one scalar" claim is false and the
  elliptical joint-percentile fallback is what the deliverable becomes — which is the fallback
  already on file.

*[Opinion: I think two factors is the likely outcome, and I think it is a better result than one,
because it is what the scenario set actually supports and it still gives a single per-driver
object — a point in a two-dimensional preference space — for the percentile.]*

---

## 6 The order of tests, and the rules, pre-stated

Nothing below is authorized. Each is small, and each can kill the next.

**RE.3 — is the boundary perceptual or configurational? DONE, 2026-09-18.** *[The RE.3 first
written here was to fit the threshold model on a θ̇ preference factor. That was a re-labelling, not
a test: a preference on θ̇ reproduces card EL.1b's own 0.1137 by construction. Jonas's question
about the normative model replaced it with a real one.]*

  On the second cut-in study the normative and the perceptual accounts are **observationally
  identical** — both give a curve in the (gap, closing speed) plane — so that study cannot separate
  them. One design here can, and the data are in hand: the truck and car cut-ins of study 1 at
  matched TTC. Writing the criterion as a constant value of `W^a Δv / gap²`, the class offset on
  log θ̇ is exactly (1 − a)·log(W_truck/W_car): **0** if the boundary is perceptual, **+0.304** if
  it is a width-blind configuration norm.

  **Measured: −0.1285 [−0.1922, −0.0721], implied a = 1.42 [1.24, 1.63]** — the interval excludes
  both, so the verdict is *neither* (`replication/czb/out/re3_apparent_size.md`). The criterion
  weights apparent size **more** heavily than optical expansion alone. The width-blind
  configuration norm is what this rules out most firmly, four standard errors in the wrong
  direction.

  **And the part that needs data, now registered with a number.** Card EL.1's full-sample w = 0.497
  puts the comfort boundary's slope in the (log gap, log Δv) plane at **1.988**, against 2 for
  constant looming and 1 for constant TTC. The pre-registered prediction is that the iso-density
  contours of p(gap, Δv | a lane change into my lane) in naturalistic data have that slope. That
  turns the naturalistic request into a test rather than an exploration.

**RE.4 — does the switch reproduce the gate?** With the catastrophe factors as admissibility and
the comfort factor as the objective, compute P(argmin ≠ continue) on the 90 pre-onset cells with
nothing refitted. Rule: **below 0.05, card G.1's own criterion**, and with no gate term anywhere.
This is the emergence claim, restated where it belongs.

**RE.5 — one driver, two scenarios.** Fit θ per driver on the cut-in; predict the left turn with
nothing refitted. Rule: **within 0.01 of card B.3.v2's 0.0558**, and the per-driver Spearman
inside card TR.1's interval [+0.407, +0.798]. This is the central claim.

**RE.6 — the observation model, not a free spread.** Refit RE.5 with σ fixed from card JJ.4's
measured 4.34× rather than free. Rule: **the held-out log-likelihood must not fall by more than 2
units**, the same margin JJ.4 used, or the precision story is decoration.

Only after RE.3 to RE.6 would anything be worth writing to the authors, and query RE1.Q1 asks
Jonas about that separately.

---

## 7 What it costs

RE.3 is a day: the factor contributions already exist in `re2_preference_family.term_table`, and a
θ̇ preference is one function in `preferences.py` behind a flag defaulting off, with property
tests. RE.4 is a day on top, because the admissibility form has to be written and the switch
probability Monte-Carloed over the belief. RE.5 is the expensive one — a hierarchical fit whose
per-driver parameter enters through a simulation rather than a closed form, which is days, not
hours, and may need a different estimator (the current one integrates a one-dimensional level by
Gauss-Hermite; θ entering through `argmin` is not that). RE.6 is hours once RE.5 exists.

*[Opinion: RE.3 is worth doing regardless of what Jonas decides about the rest, because it is
cheap and because a negative result there would close the whole line honestly. It is the single
highest-value next card in the project right now.]*

---

## 8 Queries

- **REF.Q1 (judgment, jonas):** the central proposal is to stop treating the braking margin as the
  comfort-zone boundary, which is the identification this project has been built on since gate
  R.1 and which is stated as such in `preferences.py` and in the handbook. RE.2 measures it at
  ρ(share) = −0.861. Adopt the separation (braking margin = dread boundary; an approach-rate
  factor = comfort boundary), or is there a reading in which the braking margin should still be
  the comfort boundary and the video paradigm is what is wrong?
- **REF.Q2 (judgment, jonas):** authorize RE.3 alone, the whole ladder RE.3 to RE.6, or none? RE.3
  is a day and would close the line honestly if it fails.
- **REF.Q3 (judgment, review):** §5 argues the honest claim is two comfort factors, longitudinal
  and lateral, not one. That changes the deliverable from a percentile on one scalar to a joint
  percentile on two — which is the elliptical fallback already on file. Confirm that this is a
  permissible outcome rather than a failure of the project's premise.
- **REF.Q4 (minor, review):** a θ̇ preference factor would be a genuine addition to the released
  p(o), not a re-parameterisation. It must go behind a flag defaulting to the released behavior
  (standing rule 3) and it must never be called the authors' model in any document.
- **REF.Q5 (judgment, jonas):** if RE.3 succeeds, the result is that the published model contains
  a usable comfort-zone factor that its own magnitudes bury. That is a constructive finding about
  the paper and a natural thing to put to Julian in September. It interacts with RE1.Q1; both
  should be answered together.
