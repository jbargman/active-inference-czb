# Surprise without the field: what the question means, what can answer it, and a card to run

*2026-09-02, tier-1 session, for query R2.Q5 as Jonas narrowed it on 2026-08-29: before
the active-inference contribution is positioned in any paper, explore whether the
**surprise** elements can be kept on their own, with surprise defined as a
**scenario-agnostic** metric, even if the preference field is dropped. This is a design
note, not an analysis: nothing new is computed here, and every number quoted comes from
a tracked output named at the point of quotation. It ends with one executable card
(Q5.1) for the cheaper tier, with its decision rules stated in advance, and with what I
think each outcome would mean for positioning. Opinions are marked as such.*

## 0 The answer in one paragraph

The way I read it, "surprise without the field" is a well-posed question only once one
says what the surprise is relative to, because every member of the surprise family is an
operator on a reference distribution and the operator itself carries almost no content:
for any non-negative score there is a reference under which that score *is* residual
information. Scenario-agnosticism is therefore a property of the reference, not of the
operator, and there are exactly two classes of reference that are scenario-agnostic by
construction. One is a **predictive model of what other road users normally do**, which
makes surprise a statement about the world (the Waymo construction). The other is a
**population distribution of the states drivers normally accept**, which makes surprise
a statement about the ego's situation relative to its peers, and which turns out to be
the CZB ellipse under another name: the Mahalanobis joint percentile is residual
information under a Gaussian population reference. The first cannot be the comfort-zone
criticality axis on its own, because it is zero by construction in scenarios where the
other agent behaves normally and the discomfort comes from the ego's own trajectory (the
cyclist overtake, one of the four scenarios on which the per-driver trait is shared).
It may still do a job the field was supposed to do and the gap threshold cannot: define
*when the stimulus begins*, independent of the lateral pace of the manoeuvre, which is
one of the two constraints the pipeline review extracted from the data. So the
candidate answer to R2.Q5 is not "surprise as the axis" but "surprise as the onset,
population percentile as the level": two references, not one field read at two levels.
Card Q5.1 tests the onset half on data already in hand, with no preference function
anywhere in the computation.

## 1 What the project's surprise was, and what exactly was falsified

The project used one member of one family. Residual information,

> h(x; P) = log max<sub>x′</sub> P(x′) − log P(x) ≥ 0,

applied to the **preference prior** p(o) of the published model (Schumann et al., 2026)
gives the pragmatic deficit: surprise about one's own preferred state. Evaluated
pointwise along a recorded trajectory it was the comfort-zone field; accumulated over
time it was the response-timing mechanism. Both readings have been tested on human data
and both failed their pre-registered rules (`docs/r2_gate_decisions.md`; the
accumulator at gate R.1, `replication/czb/out/stage2_summary.md`; the axis at gate R.2,
`replication/czb/out/cutin2_field_vs_gap.md`).

The pipeline review (`docs/r2_pipeline_review.md`) says what failed more precisely, and
it matters here. The field on the decisive cells was, to a good approximation, a
lane-entry gate times a worst-case counterfactual magnitude. The gate, a project
construction, made the deficit depend on the lateral pace of the cut-in when
participants do not (their response is flat across 2, 3 and 4 s lane changes at matched
time since onset, TTC and delta velocity); the magnitude, the published model's
"lead brakes at 6 m/s², I react after 1 s" counterfactual, ordered matched-TTC cells by
the vehicles' absolute speeds when participants order them by gap. Neither failure is a
failure of the residual-information operator, which did what it does: it reported how
far the state was from the reference's mode. Both are failures of the **reference**.

What was *not* used is worth listing, because it is what R2.Q5 asks about. The library
`src/surprise/` implements three further families (Modirshanechi et al., 2022;
Dinparastdjadid et al., 2023): probabilistic mismatch of an observation against a
predictive belief (surprisal, residual information, Bayes-factor surprise), belief
mismatch between a prior and a posterior belief (Bayesian surprise, postdictive
surprise, antithesis, confidence-corrected surprise), and observation mismatch against a
point prediction. All of them take a *predictive* distribution about the world as their
reference. None of them has been evaluated against any behavioral data in this project.
The library is validated on its own terms (31 property tests) and works unchanged on
Gaussians, mixtures, particle sets and categoricals; that is a statement about
software, not about drivers.

## 2 Why the reference is the whole question

A short argument that I think settles what "keep surprise, drop the field" can and
cannot mean.

Take any non-negative score s(x) on states, for instance "gap threshold exceedance",
s = max(c − gap, 0). Define a reference P(x) ∝ exp(−s(x)). Then residual information
under P is h(x; P) = s(x) − min s = s(x). So the surprise family with a *free* reference
reproduces every threshold model there is, including the log-gap threshold that beat the
field. It follows that a proposal of the form "replace the preference prior by a
different hand-built prior over the ego's states" is a relabeling of a threshold model,
and gains nothing from the surprise vocabulary except the zero floor, which the
threshold model already has. I would not put such a proposal in a paper under the
surprise name, and I do not think Jonas's question is asking for it.

The content of a surprise measure comes entirely from constraints on the reference that
one is not free to choose: that it is a genuine *predictive* distribution, estimated
from how road users actually behave, or a genuine *population* distribution, estimated
from what drivers actually accept. Under either constraint the reference is fixed by
data rather than by the analyst, the operator then has something to say, and, decisively
for R2.Q5, both constraints are **scenario-agnostic in form**. A predictor of other
agents' motion does not know what scenario it is in; a population distribution of
accepted states can be estimated for any scenario by the same recipe. The preference
prior, by contrast, was scenario-agnostic in its six terms but scenario-specific in what
the two conflict terms encode, which is where it lost.

The rest of this note takes the two constrained references in turn.

## 3 Reference A: a predictive model of the world

### 3.1 What it is

This is the construction of Dinparastdjadid et al. (2023): a generative model emits, at
each time t, a belief about each other agent's state at future times; surprise is the
observation's residual information under the belief made h seconds earlier
(probabilistic mismatch), or the divergence between the belief made at t − h and the
belief made at t about the same future time t + z (belief mismatch; the paper's own
measure, antithesis, is the one that stays zero when nothing unexpected happens). The
library implements exactly this bookkeeping (`surprise.timeseries.surprise_time_series`),
including the two timing parameters, which the paper reports must be swept because the
effect of z is not monotone.

Two facts about this reference decide what it can do for us.

**It is scenario-agnostic by construction.** The same predictor, run on the other agent's
recorded positions in a body frame, yields a lateral and a longitudinal surprise series
in a cut-in, a left turn across path, a truck drifting laterally, or a cyclist being
passed. Nothing in it needs the hand geometry that every field construction has needed
(lane gates, crossing zones, co-occupancy rules).

**It is zero wherever the other agent does nothing unexpected.** That is not a defect;
it is what "surprise about the world" means. But it means that in the cyclist overtake,
where the cyclist rides steadily and the ego chooses how close to pass, world surprise is
identically zero at every clearance, while participants intervene at 0.14 to 0.69
across the 15 cells (`replication/czb/out/transfer_overtake_summary.md`). The same holds
for any scenario in which discomfort arises from the ego's own trajectory. Since the
per-driver comfort-zone level is shared at about 0.69 of the reliability ceiling across
all four scenarios *including* the overtake
(`replication/czb/out/cross_scenario_consistency.md`), whatever the shared trait is, it
is not sensitivity to world surprise alone. This is, as far as I can tell, a derivation
rather than a finding, and it rules out reference A as the sole criticality axis before
anything is run.

### 3.2 What it may still do: define the onset

The pipeline review extracted two constraints from the second cut-in study on any
reference that would replace the field. The first was that the response engages when
encroachment *begins*, independent of how fast the lateral motion proceeds. A
belief-mismatch surprise about the target's lateral position has precisely that
property: its onset is the first frame at which the target's lateral motion departs
from the prediction, which does not depend on the pace of the motion, while its
*magnitude* does (a faster lane change is a larger departure). The field's gate had the
opposite property: its onset depended on the pace, through the projection to closure.

So the honest role of reference A, in my reading, is the one the Waymo paper itself
proposes for it: to define when the stimulus begins (their second application,
response-time modeling, "solving the when-do-you-start-the-clock problem"), and, in
combination with a proximity condition, to define when a conflict exists (their first
application: conflict = surprise ∧ spatiotemporal proximity). Neither of those is the
criticality axis. The axis, on the decisive data, is proximity, currently best
represented by the log gap and next by TTC; the surprise says when the axis starts to
count. That is a coherent two-object account, and it is consistent with the trait
finding: the shared per-driver level is a proximity tolerance, and the scenario-specific
third of the variance may in part be how surprising the different scenarios' other
agents are.

### 3.3 What predictor, given what we have

We have no learned predictor of normal driving, and the stimuli are simulator-scripted,
so the reference cannot be fitted to the study clips themselves without circularity. The
stand-in that costs nothing and is standard in the trajectory-prediction literature as
the baseline is a **constant-velocity Gaussian predictor**: the other agent's future
body-frame position is Gaussian around its constant-velocity extrapolation, with
standard deviation growing with the horizon. This has two parameters per axis (the
uncertainty at zero horizon and its growth rate), plus the paper's h and z. Every one of
them needs a stated motivation before the card runs; the card below states them as
sweeps with the paper's advice as the motivation, and requires the report to show the
sensitivity rather than one chosen value. A constant-velocity reference is also honest
about what it claims: it encodes only "road users keep doing what they are doing", which
is the weakest possible norm and is the same in every scenario.

Two better references exist and are named for the record. A predictor learned from
naturalistic data, which is what the NDS access is partly for (`docs/czb_validation_roadmap.md`
§4c); and the published model's own norm-shaped prediction machinery, run open-loop on
recorded kinematics (the particle filter and the norm weighting without the planner),
which would make the reference the model's beliefs rather than a kinematic prior. The
second inherits the per-scenario hand-written norms of handbook chapter 07, and so is
scenario-agnostic in machinery but not in content; it is the natural follow-up if the
constant-velocity stand-in shows the onset property and nothing more.

## 4 Reference B: a population distribution of accepted states, which is the ellipse

The second scenario-agnostic reference is the distribution of states drivers routinely
accept: steady-state headways at speed, accepted lateral clearances, accepted arrival-time
separations. Surprise relative to that reference asks "how unusual is my present state
among the states drivers normally tolerate", which is a sensible reading of what a
comfort-zone boundary is, and the roadmap already lists its estimation as one of the
uses of naturalistic data (§4c, use 3: "drivers should mostly live inside their own
comfort zones").

A small identity shows that this reference is not a new proposal but the one Jonas has
already promoted. If the population of accepted states in a scenario's chosen
observables is modeled as Gaussian with mean μ and covariance Σ, residual information is

> h(x) = ½ (x − μ)ᵀ Σ⁻¹ (x − μ) = ½ d²(x),

half the squared Mahalanobis distance, and the joint percentile of the CZB ellipse is the
χ² probability of d²(x), a monotone function of h. So the **CZB ellipse is the surprise
family with a population reference**: the operator (residual information) and the
per-driver level are shared across scenarios, and only the reference (μ, Σ, and the
choice of observables) is per-scenario. That is exactly the division of labor the
scope map's crux asked for, and it gives the ellipse a reading that the multivariate
"exceed both percentiles" rule never had: the level set is the set of states equally
unusual relative to what drivers accept.

Two consequences for the ellipse design note (queued as the next design task): the
per-scenario observables should be the ones whose population distribution can actually
be estimated (from the study cells now, from NDS later), and the Gaussian assumption is
a choice that the library does not force, since residual information under a mixture or
a particle set is available unchanged if a scenario's accepted-state distribution is
not elliptical.

## 5 What this implies for positioning, stated as options

I would not settle the positioning before card Q5.1 has run, but the options can be
written down now, and the first sentence of each is true whatever the card shows.

1. **Active inference supplied a candidate axis, and the axis was falsified.** True on
   the record. The paper is then a comparative study of criticality axes with a
   psychometric estimator, and the surprise family appears only in the history.
2. **Surprise about the world defines the stimulus onset; a population percentile
   defines the level.** True as a construction; whether it is *supported* is what Q5.1
   tests (onset independence from lateral pace on study 2; zero on the overtake by
   construction). If supported, the surprise family keeps an honest, testable role and
   the paper can say so without claiming the axis.
3. **Surprise relative to the population is the boundary.** True as an identity (§4);
   its empirical standing is the ellipse program's, not a separate claim.

What none of the options can say, in my opinion, is that one scalar does two jobs. That
claim is gone with the field, and the two-reference account is the replacement: onset
and level are different objects with different references, and they happen to share an
operator.

## 6 Card Q5.1: world surprise on the data in hand, with no preference function

*For the cheaper tier, after review of this note. Standing rules of
`docs/czb_work_orders.md` §2 apply. Nothing in `src/aidriver/preferences.py` is touched
or called.*

**Build.** `replication/czb/world_surprise.py`, importing only `surprise.*` and the
trace loaders. For each stimulus trace (study 1's four scenarios; study 2's 108 cut-in
traces; the 15 CAMP rear-end clips as a check on lead braking), compute at every frame
t the other agent's body-frame position and a constant-velocity Gaussian belief made at
t − h about t (probabilistic mismatch, residual information) and about t + z (belief
mismatch, antithesis), with σ(k) = σ₀ + σ₁ k Δt on each axis. Report lateral and
longitudinal series separately, as the paper does.

**Parameters, each with its motivation.** h ∈ {0.5, 1.0, 2.0} s and z ∈ {0, 1, 2} s,
swept because the paper reports the h effect as monotone and the z effect as not, and
gives no scenario-independent recommendation; σ₀ = 0.1 m on both axes (the traces'
positional resolution, from the simulator's 10 Hz output); σ₁ ∈ {0.5, 1.0, 2.0} m/s, the
range over which a constant-velocity extrapolation's error grows in the
trajectory-prediction literature (marked *unverified*: I have not checked a source for
this range in this session, and the card should either cite one or treat the sweep as
the motivation). No parameter is fitted to any response.

**Test 1, onset (the constraint from the review).** For every study-2 trace, the first
frame at which the lateral belief-mismatch surprise exceeds zero, against the
manoeuvre-onset frame from the filename stamps. Pre-stated expectation: the onset lag is
within one frame and does not depend on lane-change duration (2, 3, 4 s) at any
starting TTC or delta velocity. Report the lag table by (LCD, TTC, DV). A dependence on
LCD of more than one frame falsifies the onset claim of §3.2 for this reference.

**Test 2, the overtake is zero by construction.** On the three cyclist-overtake traces,
the world-surprise series on the cyclist. Pre-stated expectation: identically zero (up to
σ₀) at every clearance. This is a check that the derivation of §3.1 holds in the code,
not a hypothesis; a nonzero series would mean the cyclist's motion is not what the
context files describe and the derivation must be re-examined.

**Test 3, does surprise carry any axis information beyond gap.** On the 288 decisive
cells of study 2, a new comparison script (not the registered one, which is not to be
modified) with the registered fit, folds and metric, adding two covariates: the running
maximum of the longitudinal residual-information surprise over the shown window, and its
product with the inverse gap at the window end (the paper's "surprise and proximity"
conflict condition made continuous). Decision rule, stated now: if the surprise-alone
covariate's held-out wRMSE is more than 0.01 above the gap's 0.152, surprise is not the
axis on this data (expected, per §3.1); if the product covariate is within 0.01 of the
gap or below it, the two-object account of §3.2 is supported at the level of the axis
and should be carried into the ellipse design; if the product is more than 0.01 above the
gap, the onset role survives only if Test 1 passed, and surprise contributes nothing to
the level.

**Test 4, the CAMP check.** On the eight braking-lead clips, the longitudinal surprise
onset against the scripted brake onset at simulation time 10 s; on the seven
constant-speed clips, the expectation is a flat series. This is the rear-end analogue of
Test 1 and the one scenario where the published model's own home ground and a human
press time coexist in our data.

**Output.** `out/world_surprise.md` with the four tests, the parameter sweep as tables,
one figure per scenario (the series with the onset marked), and the card's verdicts
against the rules above. Suite before and after. Property tests for the predictor (zero
surprise on a constant-velocity trace; onset at the first frame of a step in lateral
velocity; invariance to the body-frame choice) in `tests/test_surprise.py`'s style.

**What is deliberately not in the card.** Any per-scenario geometry, any preference term,
any fit of the predictor to responses, and any claim about LTAP or the truck beyond
computing their series for inspection: the LTAP trace loader is B.3.v2's job and the
truck's B.2's, and this card should not front-run their construction notes. If the
generic loader written for this card is good enough for those scenarios, that is a
finding to hand to those cards, not a license to score them here.

## 7 Where I may be wrong

- The argument of §2 (a free reference makes the operator vacuous) is exact, but it
  could be read as too dismissive of the *practical* content the library adds: the zero
  floor, the parameter-free treatment of densities, and correct handling of mixtures and
  particle sets. Those are real, and they are why the library is worth keeping
  regardless of how R2.Q5 is settled. They are not, in my view, scientific claims about
  drivers.
- §3.1's derivation that world surprise is zero on the overtake assumes the cyclist's
  motion is steady in the traces. Test 2 checks this in code before anything is read
  into it.
- The constant-velocity stand-in is the weakest possible reference, and a negative
  result on Test 3 with it would not rule out a learned predictor; it would only say
  that "keeps doing what it is doing" carries no axis information beyond gap on this
  design. A positive result would be the more informative outcome, and I expect the
  negative one.
- The identity in §4 is for a Gaussian population; if a scenario's accepted-state
  distribution is strongly non-elliptical the ellipse and the surprise reading part ways,
  and the surprise reading is the more general of the two.
- The onset property of belief-mismatch surprise (§3.2) depends on h and on the
  predictor's uncertainty growth; with a very wide σ₁ the onset is delayed, which is
  why Test 1 sweeps rather than chooses.

## References

Dinparastdjadid, A., Supeene, I., & Engström, J. (2023). *Measuring surprise in the
wild* (arXiv:2305.07733). arXiv. https://arxiv.org/abs/2305.07733 — read from the
source PDF by an earlier session; summary in `notes/01_paper_summaries.md` §2.

Engström, J., Bärgman, J., Nilsson, D., Seppelt, B., Markkula, G., Piccinini, G. B., &
Victor, T. (2018). Great expectations: A predictive processing account of automobile
driving. *Theoretical Issues in Ergonomics Science, 19*(2), 156–194. — as cited in the
project's notes; not re-verified in this session.

Modirshanechi, A., Brea, J., & Gerstner, W. (2022). A taxonomy of surprise definitions.
*Journal of Mathematical Psychology, 110*, Article 102712.
https://doi.org/10.1016/j.jmp.2022.102712 — verified in earlier project documents.

Schumann, J. F., Engström, J., Johnson, A., O'Kelly, M., Messias, J., Kober, J., &
Zgonnikov, A. (2026). Active inference as a model of collision avoidance behavior in
human drivers. *Nature Communications, 17*, Article 5009.
https://doi.org/10.1038/s41467-026-73345-0 — the replicated paper.
