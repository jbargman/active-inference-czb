# The CZB ellipse: a design note

*2026-09-02, tier-1 session, for queue item (2) of the standing handover and for
query C.Q2. Jonas promoted the elliptical joint percentile from a comparator to a
deliverable candidate on 2026-08-29 and asked for a design note on which observables
per scenario, how the Mahalanobis joint percentile is defined, and how the per-driver
trait maps onto it. This note answers those three questions, adds a fourth that the
data force (what the study data can and cannot identify about an ellipse), and ends
with three cards. Primary source for the proposal: Jonas's QUADRARUM working document
(`external/QUADRARUM/Bärgman_On_CZB_as_basis_for_ADAS_adaptation 20260501.docx`,
May 2026, not for dissemination outside QUADRARUM; quoted here only as the project's
own record). Nothing new is computed; every number comes from a tracked output named
where it is quoted. Opinions are marked as such.*

## 0 The answer in one paragraph

The ellipse as Jonas defined it is a joint percentile over a population of
*observations*: the boundary encloses 80% of where drivers are, and crossing it means
entering the outer 20% of the joint distribution. As the project can currently
estimate it, the ellipse is something related but not identical: a per-scenario
quadratic form in two criticality observables, whose level set is the boundary and
whose *level* is the per-driver trait the stage-1 estimator already measures. The two
coincide when a population reference (the mean and covariance of accepted states) is
available, which for us means naturalistic data; on the designed study stimuli that
reference does not exist, and the ellipse's overall scale is then confounded with the
level, so the study data can settle the ellipse's *shape* (the trade-off between the two
observables within a scenario) and the per-driver *ordering* (already shown to be
shared at about 0.69 of the reliability ceiling, field-free), but not the absolute
joint percentile. The way I read the evidence, the right program is therefore in three
steps: first, on the second cut-in study now, test whether a quadratic form in two
observables earns its second axis against the one-dimensional log-gap threshold that
won gate R.2 (card EL.1, no new loaders, registered fit and folds); second, once the
LTAP and truck constructions exist, map the per-driver level onto the per-scenario
forms and run the B.4 transfer with the level shared (card EL.2); third, with
naturalistic data, estimate each scenario's population reference and compare the
percentile of *drivers' boundaries* with the percentile of *observed states*, which is
the multivariate form of the question Jonas's own figure 7 asks (card EL.3). One
identity ties this to the R2.Q5 note: under a Gaussian population the ellipse's
Mahalanobis distance is exactly residual-information surprise, so the ellipse is the
surprise family with a population reference, and the onset defined there says when the
ellipse is consulted.

## 1 What was proposed, and the two populations it can refer to

Jonas's QUADRARUM document sets the problem in one page. A univariate CZB defined as
"the 80th percentile across a population of drivers, such that crossing corresponds to
entering the upper 20% of observations" is clear; extending it to two measures with a
marginal conjunction rule silently changes the criterion, since under independence
"P(joint crossing) = 0.2 × 0.2 = 0.04". His fix is to define the crossing on the joint
distribution: an elliptical boundary

> (x − μ)ᵀ Σ⁻¹ (x − μ) = χ²<sub>2, 0.8</sub>,

"where μ is the mean vector and Σ the covariance matrix", enclosing 80% of the
observations, preserving equivalence with the univariate definition, and allowing
trade-offs ("a more critical value in one dimension may still fall within the CZB if
accompanied by a more favorable value in another"). He adds that the criterion must
either be reformulated as a joint definition, relaxed per measure, or reduced to a
smaller set of dominant metrics, and that this is "a critical part of operationalizing
the QUADRARUM framework in an ADAS/product".

The definition refers to a population, and it is worth being explicit that two
different populations could be meant, because the project's estimator measures one and
naturalistic data would supply the other.

- **Population A: observed states.** The distribution of (x, y) over routine driving,
  pooled over drivers: where drivers *are*. Its 80% ellipse is what a naturalistic
  dataset would estimate directly, and it is what the QUADRARUM text reads most
  naturally as.
- **Population B: drivers' boundary levels.** The distribution over drivers of the level
  at which each stops wanting to be there: the stage-1 object c_i = exp(μ + σ<sub>pop</sub> z_i)
  (`replication/czb/out/stage1_summary.md`, median 5 400, σ<sub>pop</sub> 0.200 on
  the deficit axis). Its 80th percentile is the level that 80% of drivers would already
  have crossed, which is the trigger semantics the roadmap has used throughout.

These are not the same thing, and Jonas's own document says why in the univariate case:
the lowest observed headways "are more likely to reflect responses to having crossed
the boundary, rather than the boundary itself", so the tail of population A is
contaminated by post-crossing behavior, and attention should go to steady-state
following instead. His figure 7 then asks how much the difference between a
CZB-based threshold and a measured-data threshold matters against the choice of
percentile, and answers, for the illustrated case, that the percentile choice "is
likely to have a larger effect". Card C gave the project's univariate version of that
answer on real data: one five-point step of the percentile moves the implied trigger by
about 0.27 s against about 0.53 s from the level's own estimation uncertainty
(`replication/czb/out/percentile_sensitivity.md`); the two are comparable.

For the ellipse the distinction has a concrete consequence. Population B supplies the
*level*, and it is what the study data identify. Population A supplies the *shape*
(μ and Σ, the center and the trade-off), and the study data do not contain it, because
the stimuli were designed rather than sampled. Section 3 takes that up.

## 2 The formulation

Per scenario s, choose two observables and write them as a criticality-oriented vector
x ∈ ℝ², larger meaning more critical on each axis (for instance inverse gap and inverse
TTC, or their logs with the sign flipped). Define the scenario's distance

> d_s(x) = √( (x − μ_s)ᵀ Σ_s⁻¹ (x − μ_s) ),

with μ_s the comfortable reference state and Σ_s the trade-off matrix. The boundary of
driver i is the level set d_s(x) = c_i, and the response model is the stage-1 model with
d_s in place of the field:

> P(intervene) = b_s + (1 − b_s) Φ( (d_s(x) − c_i) / σ<sub>resp</sub> ),  c_i = exp(μ_c + σ<sub>pop</sub> z_i),

with the per-scenario lapse b_s free (the B.4 amendment of 2026-08-28: the pre-onset
baseline differs by scenario, 0.081 in the cut-in against 0.198 in the overtake, and is
identified by the pre-onset cells alone) and the level population (μ_c, σ<sub>pop</sub>)
shared across scenarios. That last clause *is* the one-scalar claim, restated without a
field: one level per driver, one form per scenario.

Two properties follow immediately. Under a Gaussian population A with the same μ_s and
Σ_s, the joint percentile of a state is the χ²₂ probability of d_s(x)², a monotone
function of d_s, so the level set at c is Jonas's ellipse at the matching percentile,
and "which percentile of drivers" (population B) and "which percentile of states"
(population A) are two readings of the same curve. And the residual-information surprise
of x under that Gaussian is ½ d_s(x)² (`docs/surprise_without_the_field.md` §4), so the
ellipse is the surprise family with a population reference, with the operator and the
level shared and only the reference per scenario; if a scenario's accepted-state
distribution is not elliptical, the library evaluates the same operator under a mixture
or a particle set unchanged, and the "ellipse" becomes whatever level set that
reference has.

## 3 What the study data can and cannot identify

This is the section the data force, and I think it decides the order of the cards.

**The scale confound.** d_s and c_i enter the response only through their ratio, so
multiplying Σ_s by a constant and dividing every c_i by its square root leaves every
prediction unchanged. Within one scenario that is harmless (the level absorbs the
scale, as it does for the field). Across scenarios it is not: if Σ_s is fitted freely
in each scenario, the shared level population can be made to fit any scenario by
rescaling, and the transfer test is empty. The level can transfer only if each
scenario's Σ_s is pinned *without reference to that scenario's responses*: from a
population reference (naturalistic data, card EL.3), or, failing that, by a stated
convention that is the same in every scenario (for example, unit Mahalanobis distance
at each axis's marginal population percentile, which again needs population A).

**The center.** μ_s is the comfortable reference. On designed stimuli it is not
estimable either; the honest study-data choice is to fix it at zero criticality (far
away, no closing), which makes d_s a norm rather than a distance from a mean, and to
say so.

**What the study data do identify.** The *orientation and aspect* of Σ_s, that is, the
trade-off between the two observables, wherever the design varies both. That is the
case in exactly three of the datasets in hand: the second cut-in study (a six-fold range
of gap at matched TTC, 288 post-onset cells), the LTAP design (nine PET levels at two
oncoming speeds, 18 cells, intervention *lower* at 70 km/h at every PET level, so the
second axis carries real signal; card B.3.v2), and the CAMP rear-end replication (15
clips crossing speed with lead deceleration and with constant closing speed; 119
participants). In the first cut-in study gap and TTC are collinear
(`replication/czb/out/cutin2_scope.md`), in the cyclist overtake only clearance varies
(the ego passes at a constant 14.3 m/s), and in the truck overtake only the truck's
lateral offset varies, so in those three the ellipse reduces to a one-dimensional
threshold and has nothing to add until a second axis is varied.

So the study program can answer "does a second axis earn its place, and with what
trade-off" per scenario, and "is the per-driver level shared" across scenarios at the
level of ordering, which the field-free trait analysis already answers at 0.69 of the
ceiling (`replication/czb/out/cross_scenario_consistency.md`). It cannot answer "what
is the 80% ellipse" in Jonas's population-A sense. That needs naturalistic data, and it
is the same data the roadmap already names for the paradigm offset (§4c, uses 1 and 3).

## 4 Observables per scenario

Proposals, each with the reason and the data that would identify the trade-off. The
construction notes for B.2 and B.3 own the final choice; this note only says what the
ellipse needs from them.

| scenario | axis 1 (longitudinal / temporal) | axis 2 | what identifies the trade-off now |
|---|---|---|---|
| cut-in (car, truck) | log gap at the window end — the R.2 winner (held-out wRMSE 0.152, noise floor 0.118) | log TTC, or closing speed — the second-best axis (0.168); the two are collinear in study 1 and separated in study 2 | study 2's 288 cells; card EL.1 |
| LTAP | arrival-time separation at the conflict zone (the PET-like quantity of the B.3.v2 card) | oncoming distance, or oncoming speed — the two-speed design shows a distance effect at matched PET | the 18 LTAP cells, once B.3.v2's loader exists |
| cyclist overtake | lateral clearance | passing speed, or time-to-pass | not identified: speed is constant in the study; one-dimensional until a design varies it |
| truck overtake | lateral clearance to the truck | the truck's lateral movement (the Button design's `truck_lateral_movement` variants) | five offsets; the movement variants only in the Button design |
| rear-end (CAMP) | inverse TTC (ΔV / range, the looming rate) | subject-vehicle speed | the 15 CAMP clips; note that Kiefer et al.'s published hard-braking model is *already* a linear rule in exactly these two, with the inverse-TTC threshold falling with speed (`external/01_studies/.../camp_crowdsourcing_context_v2.md` §2.7, quoting the 2005 paper) |

Two remarks. The rear-end row is a check that the class is not exotic: the CAMP
last-second-braking model is a two-observable rule with a speed trade-off, which is the
linear cousin of the ellipse, and the crowdsourced replication puts a human press time
in each of its 15 cells; it is the natural third dataset for card EL.1's shape question.
And the lateral axis of the cut-in is deliberately absent: the R2.Q5 note argues, from
the pipeline review's finding that participants are flat across lane-change duration,
that the lateral motion defines *when* the ellipse is consulted (the onset), not where
its boundary lies.

## 5 How the per-driver trait maps onto it

Mechanically, by substitution. The stage-1 estimator (`replication/czb/fit_stage1.py`:
per-driver threshold with hierarchical lapse, driver effects integrated out by
quadrature, Laplace on the hyperparameters, priors validated by the recovery harness of
card A.1) takes a running-maximum covariate over the shown window; give it d_s(x)'s
running maximum instead of the deficit's and it returns the level population on the d
scale with the same machinery, the same LOPO comparison of lapse variants, and the same
percentile table. The transfer test of card B.4 then runs unchanged in form: fit the
level population on the cut-in, free each scenario's lapse, score each other scenario
against chance, against its own refit ceiling, and against the field-free ceiling of
0.69 of the reliable per-driver signal, with the per-scenario linear 2D rules as the
comparator on identical folds.

What is *not* mechanical is section 3's scale: the transfer is a test of the shared
level only if each Σ_s is pinned by the same convention before the fit. Until
naturalistic data exist, the convention I would propose, stated as an opinion, is to
normalize each scenario's two axes by their ranges over that scenario's *design* (so d
is measured in design-span units) and to fit only the orientation and aspect of Σ_s;
that is arbitrary, and the transfer result should be read with that arbitrariness in
view, but it is the same arbitrariness in every scenario and it can be replaced by a
population reference without changing the code.

## 6 Cards

*Standing rules of `docs/czb_work_orders.md` §2 apply. None of these touches
`src/aidriver/preferences.py` or the registered R.2 script.*

### Card EL.1 — does a second axis earn its place on the second cut-in study

- **Script.** `replication/czb/cutin2_two_axis.py`, importing the registered script's
  `fit`, `predict`, folds and metric; the 288 CP2–CP5 cells from `out/cutin2_cells.csv`.
- **Models, all on identical folds, each at its better scale.** (a) the registered 1D
  log-gap threshold, re-run as the reference (expected 0.152); (b) a linear 2D rule,
  x = w log gap + (1 − w) log TTC with w ∈ [0, 1] fitted (one extra parameter);
  (c) the quadratic form, d² = qᵀ Q q with q = (−log gap, −log TTC) − q₀, q₀ fixed at
  the mildest design cell's values, Q positive definite via a Cholesky factor (three
  parameters, of which one is the scale confounded with the threshold and should be
  fixed to 1 by convention, leaving two); (d) the same quadratic form with the CAMP-style
  axes (1/TTC, ego speed) for comparison.
- **Decision rule, stated now.** The second axis earns its place on this scenario if
  (b) or (c) beats (a) by more than 0.01 held-out wRMSE; if (c) beats (b) by more than
  0.01 the trade-off is curved and the ellipse form is preferred; if (b) and (c) are
  within 0.01 of each other parsimony picks the linear rule; if neither beats (a) the
  cut-in boundary is one-dimensional in the gap on this data and the ellipse has
  nothing to add here, which is a finding, not a failure.
- **Report.** The table, the fitted w or Q with the implied trade-off (the slope of the
  level set in the log-gap/log-TTC plane), the within-row orderings, and the noise
  floor. No verdict prose beyond the rule.

### Card EL.2 — the level shared across scenarios, on the ellipse forms

After B.2 and B.3.v2 have their loaders and construction notes. The stage-1 estimator
on d_s(x)'s running maximum in each scenario, with the section-5 normalization
convention; the B.4 transfer as amended (level frozen, lapse free); comparators the
linear 2D rules; ceilings the per-scenario refit and the 0.69 field-free bound. Output
per the B.4 card. The convention and the confound are to be stated in the report's
header.

### Card EL.3 — the population reference, when naturalistic data arrive

Per scenario, μ_s and Σ_s from steady-state accepted states in routine driving (Jonas's
own caveats apply: steady-state following only, no overtaking-intent segments, no
post-crossing transients); then the two percentiles side by side, of observed states
and of drivers' boundaries, and the trigger each implies, across percentiles 50–95, in
the form of card C. That table is the multivariate answer to figure 7's question, and,
the way I read Jonas's document, the one QUADRARUM most needs.

## 7 Where I may be wrong

- I have read the QUADRARUM definition as a percentile of pooled observations
  (population A). If it was meant as a percentile over drivers of per-driver boundaries
  (population B), section 1's distinction still stands but the deliverable is closer to
  what the study data already give, and card EL.3 becomes a check rather than the
  deliverable.
- The claim that the study data cannot identify Σ_s's scale is exact for the response
  model above; a model with an additional observed quantity on an absolute scale (the
  Button design's press *times*, which pin when the crossing happens rather than
  whether) may partly break the confound. That is worth a look inside card EL.2 rather
  than a separate card.
- Fixing μ_s at zero criticality makes d_s a norm; if the comfortable reference is not
  at the origin (drivers may prefer a nonzero closing rate in some scenarios), the
  level set is off-center and the quadratic form with a free center needs two more
  parameters the study cells may not support.
- The proposed observables are the ones the existing analyses point to; the B.2 and
  B.3 construction notes may have better reasons for others, and this note should
  yield to them on that.
- The CAMP replication's data cleaning removed 32% of rows and the 45 mph and 0.28 g
  conditions are absent, so its use in card EL.1 is a shape check on 11 conditions, not
  a replication of the published 17.
