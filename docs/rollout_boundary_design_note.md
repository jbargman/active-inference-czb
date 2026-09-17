# Card JJ.1: the rollout formulation of the comfort-zone boundary, a design note

*2026-09-17, authorized by Jonas the same evening (JJ.Q1: "go as proposed"). Step 1 of the JJ program
(`docs/active_inference_program.md` §10): the construction in full, every parameter with its motivation,
and the pre-stated rules of cards JJ.2 to JJ.4. **Stop for review before coding**: nothing below has
been implemented or run, and the rules become binding only when Jonas has read them. Where a value is
a placeholder to be replaced by a measured one, it says so. Opinions are marked.*

## 0 What is being built, in one paragraph

At the moment a clip is frozen, roll out a small menu of the ego's options against a fan of the other
road user's predicted futures, score every imagined future with the released preference function, and
take as the criticality quantity the gap in expected free energy between "continue" and the best
alternative, **ΔG, in nats**. Fit the same three-parameter threshold model the project fits on every
axis, with **no gate term**, and score it held out against the current best (the gated looming rule)
on the second cut-in study, then on the left turn and the cyclist overtake with one level in nats. If
ΔG needs a gate to reach the pre-onset cells, or a scenario-specific horizon to reach the left turn,
the construction has failed at what it was for and the report says so.

## 1 The construction

### 1.1 The freeze, and the belief about the present

The freeze time t₀ is the end of the shown window: the response moment e_t of the second cut-in study
(`replication/czb/cutin2_gate.py` conventions); the clip end for study 1's cut-in and overtake; the
decision moment 13.5 s for the left turn (B3.Q1, `src/comfortzone/ltap.py::T_DECISION_S`).

The belief b(s₀) is a Gaussian over the two vehicles' positions, speeds and the other's lateral rate,
read from the traces exactly as cards G.1 and PC.1 read them: the lateral rate as a backward difference
over 0.3 s (second study) or 1.0 s (first study), the same windows those cards used and for the same
reason (the stimuli's sample spacing). Its standard deviations are the studies' jitter floors as
measured by card HS.1 (`replication/czb/out/hs1_situational_surprise.md`, read by the script, never
typed in). The trap HS.1 fell into, choosing a spread before measuring the floor, is what this step
prevents.

**A latent intention, for the cut-in only.** The belief carries P(changing lanes) = p_t:

- prior p₀ before any lateral motion. Motivation: card G.1's fitted gate sits at 0.063 to 0.070 in every
  pre-onset cell (`out/cutin2_gate.md` §4), and the pre-onset intervention share is 0.023 (§2). A prior
  of **0.07** is the first value; the sweep {0.02, 0.07, 0.20} is reported, and the value is chosen by
  this motivation, not by the held-out score (§2, rule d).
- update from the lateral rate: a likelihood ratio between "keeping" (lateral rate ~ N(0, σ_keep), with
  σ_keep the jitter floor of the rate, since G.1 §0 measured the pre-onset rate at −0.010 to 0.003 m/s)
  and "changing" (lateral rate ~ N(−v_lc, σ_lc), with v_lc = **1.2 m/s**, motivated by G.1 §0's
  post-onset mean of −1.137 m/s and by a 3.65 m lane crossed in about 3 s; σ_lc = 0.4 m/s, the spread
  of that same column, to be read from the traces by the script). The posterior after the shown
  window is p_t. This is the Bayesian ramp of figure 5 in the program document.

For the left turn and the overtake there is no intention variable: the oncoming car and the cyclist do
what they are seen to do.

### 1.2 The fan: the predictive distribution over the other's futures

Three predictors, a ladder. JJ.2 to JJ.4 use the first; the second is a secondary in JJ.2; the third
waits for JJ.7.

**P0, constant-velocity Gaussian with growth.** Body-frame lateral position y(τ) ~ N(y₀ + ẏ₀ τ,
σ_y² + (σ_v,lat τ)²) and longitudinal position x(τ) ~ N(x₀ + v₀ τ, σ_x² + (½ σ_a τ²)²), for τ up to the
horizon; under "changing", the lateral rate is v_lc toward the ego's lane until the lane center is
reached, then held. The mixture weight is p_t. Growth constants, placeholders until JJ.5 measures them
on highD (`docs/generative_model_framework.md` component C3):

| constant | first value | motivation | sweep |
|---|---|---|---|
| σ_v,lat | 0.33 m/s | G.1's fitted gate spread 0.99 m over its 3 s horizon, read as lateral-rate uncertainty times horizon | {0.1, 0.33, 0.6} |
| σ_a (longitudinal) | 0.5 m/s² | the pedal-effort tolerance of the released preference is 0.1 m/s²; ordinary highway speed variation is larger; **unverified**, replaced by C3's measurement | {0.25, 0.5, 1.0} |
| horizon H | 6 s | the released model's planning horizon (30 steps of 0.2 s) | {3, 6} |
| samples per policy | 200 | enough for a standard error of ΔG below 5% of its cell-to-cell spread (checked in the property tests, not assumed) | — |

Common random numbers across policies: every policy is scored against the *same* 200 sampled futures
of the other, so ΔG is a difference between paired scores and its Monte Carlo noise is small.

**P1, the released norm tournament, open loop.** `src/common/dynamics.py::forward_tar_agent` run for
30 steps without observations, with the scenario's norm geometry: the rear-end norms as released, and
the crossing norm of `docs/cutin_norm_proposal.md` (`src/comfortzone/norms.py`) as the alternative. This
is what the released model would imagine; it is scenario-specific in content (handbook chapter 7) and
is reported as a secondary in JJ.2.

**P2, a learned predictor** (JJ.7): not in this card.

### 1.3 The policy menu

The menu is the scenario's *instructed alternatives*, which is the one scenario-specific element and is
read from each study's instructions rather than chosen:

| scenario | policies (the ego's) | notes |
|---|---|---|
| cut-in (studies 1 and 2) | continue (hold speed, hold lane); ease off (−1 m/s²); brake (−3 m/s²); brake hard (−6 m/s²) | 6 m/s² is the released model's assumed worst-case lead deceleration; steering away is added only if the study's road has a free lane on the far side, to be read from the study context files |
| left turn | proceed (the ego's recorded turn, reading P of card PC.1); wait (stop before the crossing at −3 m/s²) | the "own planned path" that alone opened PC.1's gate |
| cyclist overtake | continue the pass at the shown clearance; abort (fall back behind the cyclist at −2 m/s²) | the overtake's instructed choice |

Ego rollouts are deterministic per policy (the ego knows its own plan); all uncertainty is in the fan.
The released model's pedal constraints and jerk limits are not modeled: the policies are
constant-acceleration segments, and this simplification is recorded.

### 1.4 Scoring: expected free energy in the released model's own form

For each policy π and each sampled future, the six preference terms of `src/aidriver/preferences.py`
are evaluated at every step τ on the imagined observation (relative position, speeds, the ego's own
speed, acceleration and lateral position), and

> G(π) = Σ_τ [ max_o log p(o) − E_futures log p(o_τ | π) ] ≥ 0,

the residual information of the pragmatic value over the horizon, which is exactly the quantity the
released model accumulates (Paper Eq. 13; `notes/02_active_inference_overview.md` §2). Two variants, both
run in every card because the cost of the second is one flag and one column:

- **Variant A, released:** all six terms, including the safety term's worst-case counterfactual, as the
  paper has them and as the mirror implements them. Primary, on Jonas's ruling (JJ.Q2, 2026-09-17).
- **Variant B, expected outcome:** the safety term switched off (behind a flag defaulting to the released
  behavior, rule 3 of the standing rules); collisions are scored where they happen in the sampled
  futures, by the released collision term with its severity factor. This is the reference the pipeline
  review pointed at (`docs/r2_pipeline_review.md` §5). Promoted to primary only by rule (c) of §2.

The desired speed in the speed term is the ego's speed in the clip (the handout's lesson, §4: at the
default 15 m/s against an ego at 30 m/s the speed term swamps everything). Epistemic value α = 0 in
the primary analysis, the authors' validated configuration; α > 0 is a secondary, with the caveat
`HANDOFF.md` §4 recorded: under looming perception a closer approach sharpens the observation, so
epistemic value alone pulls toward approaching.

### 1.5 The criticality quantity and the response model

> ΔG(t₀) = G(continue) − min_π G(π) ≥ 0.

The axis is log ΔG. If any cell has ΔG = 0 exactly (no sampled future collides under continue, or
every alternative costs more control effort than it saves), the report counts those cells and uses
log(ΔG + ΔG_min/2) with ΔG_min the smallest positive value across cells, stated in the report; the
sensitivity to that choice is reported as a table.

The response model is unchanged in form: share who intervene = lapse + (1 − lapse) × Φ((log ΔG −
log c) / σ). Three free parameters, the same as every axis competition since gate R.2. **No gate
term.** For the per-driver levels (JJ.3) the stage-1 hierarchical estimator is used unchanged with log ΔG
as its axis (`replication/czb/stage1_looming.py` as the pattern).

### 1.6 Where this differs from the falsified field, stated so the difference can be checked

| | the field (gate R.2) | ΔG |
|---|---|---|
| evaluated on | the present state, pointwise | imagined futures over the horizon |
| the other's future | one worst case (lead brakes at 6 m/s²) inside the safety term; one straight line inside the lane-entry gate | a fan under a normative predictor with uncertainty and a latent intention |
| the ego | the no-action trajectory | a menu; the quantity is relative to the best alternative |
| the onset | a projection to the moment of closure | the belief about intention |
| the unit | preference units, one scenario's geometry | nats, every scenario |

## 2 Pre-stated rules for card JJ.2: rollouts on the cut-in (second study)

Cells, folds and metric exactly as the registered gate R.2 script defines them, imported and not
modified: 378 cells, 288 post-onset and 90 pre-onset, leave-one-starting-TTC-out folds, weighted RMSE,
the chance reference 0.320 and the noise floor 0.118 (`out/cutin2_field_vs_gap.md`). Comparators, on
file: the ungated looming rule 0.1137 (`out/cutin2_gate.md` §1, model c), the gated looming rule 0.1027
(model k), G.1's pre-onset out-of-sample 0.0319 gated and 0.4832 ungated (§2).

- **(a) Post-onset held-out.** ΔG's three-parameter threshold model, held out, within **0.01 of the
  gated looming rule's 0.1027**. The gated rule is the fair comparator because ΔG claims to contain the
  gate; the ungated 0.1137 is reported beside it.
- **(b) Pre-onset out of sample.** The full post-onset fit applied to the 90 pre-onset cells scores
  below **0.05**, with no gate term. This is the emergence claim, and it is the rule most likely to
  fail.
- **(c) The review's ordering constraint.** Within the 24 matched-TTC rows, the sign of ΔG's rank
  correlation with the response is positive in at least as many rows as the gap's is negative
  (`docs/r2_pipeline_review.md` §4 gives the gap's count). If variant A fails (c) and variant B passes
  it, variant B is promoted to primary and the report says the released safety counterfactual is what
  failed, again.
- **(d) Sensitivity, never selection.** p₀, σ_v,lat, σ_a and H are fixed at the first values of §1
  before the run; every sweep value is reported as a table; none is chosen by its score. A reader who
  prefers a swept value can see what it would have given.
- **(e) Monte Carlo.** ΔG's standard error across seeds is reported per cell; the verdict is
  invalid if it exceeds 5% of the between-cell spread of log ΔG.

Verdict, written before the run: **adopt** ΔG as the primary axis if (a), (b) and (e) hold; **keep as a
comparator** if (a) and (e) hold and (b) fails, with the gated looming rule staying primary; **drop** if
(a) fails. Rule (c) decides the variant, not the verdict.

**What counts as a failure of the card rather than of the model:** a measured jitter floor that makes
the lateral-rate likelihood ratio uninformative within the 0.3 s window (report, and fall back to the
1.0 s window with the change dated); any cell whose traces end before t₀ (excluded and counted, as
PC.1 did).

## 3 Pre-stated rules for card JJ.3: transfer in nats (first study)

**Left turn** (18 cells, `out/ltap_two_axis.md`; distance alone 0.0558 held out, leave-one-PET-out).
The perceived arrival of the oncoming car carries the released looming model's distance-dependent
noise (handbook chapter 3: constant noise in the angular channel, `decoder.py`), so that the arrival at
70 km/h from farther away is less certain than at 50 km/h.

- **(a)** ΔG's threshold model within 0.01 of distance alone (0.0558), same folds.
- **(b) Direction of the speed effect.** In the *predicted* shares, the 70 km/h cell is below the
  50 km/h cell at every matched PET, as the data are (`docs/lateral_and_uncertainty_note.md` §1). This is
  the uncertainty mechanism's own prediction, and it is reported whether or not (a) holds.
- **(c) No horizon parameter.** The horizon is the released 6 s; if the "proceed" rollout's conflict at
  a PET of 4 s (oncoming car arriving 4 s after the ego clears) does not register within it, the report
  says the emergence claim fails on the left turn at that PET rather than extending the horizon.

**Cyclist overtake** (15 cells, `out/transfer_overtake_summary.md`).

- **(d)** Intervention graded in clearance in the predicted shares across the three clearance levels,
  which the field could not produce (`out/overtake_field_check.md`), with the held-out score reported
  against the lateral-clearance rule of card B.1.

**The trait on one scale.** Per-driver levels on log ΔG fitted on the cut-in and on the left turn for
the 43 drivers seen in both (card TR.1's set, `out/driver_levels.md`): Spearman correlation with its
bootstrap interval, against TR.1's +0.647 in mixed units and against the reliability ceiling. Pre-stated
reading: a correlation within the interval of TR.1's is "the same trait on one scale, no rescaling";
a correlation clearly above it would be the first evidence that the common unit adds information; below
it, that ΔG loses per-driver signal that the scenario-specific axes keep. **EL.Q4 is answered by this
card only if the first or second reading obtains.**

## 4 Pre-stated rules for card JJ.4: precision as spread

Two refits of the stage-1 estimator, each replacing free spreads by a precision tied to the stimulus:

- **Medium.** One spread for the video left turn and one for the track (card TT.1's data,
  `external/02_LTAPOD_DBIN/`), the ratio free, against the two free spreads already on file (0.86 s and
  0.20 s). Trivially equivalent as a fit; the content is the second step: the ratio predicted from the
  perceptual model (angular noise on a monocular frozen frame against a moving binocular view) is
  reported beside the fitted ratio. **Unverified constants** for the perceptual side are marked and
  sourced in the script or the step is reported as not yet possible.
- **Apparent size.** The truck and car cut-ins of study 1 at matched TTC, the roadmap's E.2: a model
  with one spread per stimulus class against one shared spread. Rule: the two-spread model earns its
  place if it improves held-out log-likelihood by more than 2 units under LOPO; the direction (truck
  sharper) is reported either way.
- **The gate's spread, derived.** G.1's s_l = 0.990 m against σ_v,lat × 3 s with σ_v,lat measured from
  the traces' lateral-rate jitter plus P0's growth constant; reported as a computed value beside the
  fitted one. Agreement within a factor of 1.5 is the pre-stated reading for "the gate's spread is a
  computed uncertainty".

## 5 Software plan

New package `src/rollout/`, nothing in `src/aidriver/preferences.py` changed (variant B is a flag
defaulting to the released behavior):

| module | contents | property tests (`tests/test_rollout.py`, `check()` style) |
|---|---|---|
| `belief.py` | the Gaussian belief at the freeze; the intention posterior | prior recovered when the rate is at the jitter floor; posterior → 1 for a rate at −v_lc sustained over the window; symmetric under sign convention |
| `predictor.py` | P0 with growth and the intention mixture; P1 as a wrapper on `forward_tar_agent` | zero growth reproduces G.1's projection exactly (the step limit); the sample mean matches the analytic mean to Monte Carlo error; common random numbers give identical fans across policies |
| `policies.py` | the menus; constant-acceleration rollouts | continue holds speed; brake hard reaches 0 at v/6 s; the left-turn "proceed" reproduces PC.1's reading P path to within its residual |
| `efe.py` | G(π) from `preferences.py` terms; variants A and B; α | G ≥ 0; identical policies give identical G; a certain collision under continue and none under brake gives ΔG > 0 growing as the gap shrinks; with p₀ = 0 and a lane-keeping other, ΔG = 0 |
| `boundary.py` | ΔG per cell; log axis with the zero rule; the standard error across seeds | the zero rule applies only when a zero exists; SE reported |

Scripts, one per card, in `replication/czb/`: `je2_rollout_cutin.py` (imports the registered R.2
script's cell construction, folds and metric; writes `out/je2_rollout_cutin.md` plus per-cell CSV),
`je3_rollout_transfer.py` (→ `out/je3_rollout_transfer.md`), `je4_precision_spread.py`
(→ `out/je4_precision_spread.md`). Each writes its main report before any bootstrap (rule 10 of the
handover). The suite grows by one file, `tests/test_rollout.py`, and the handover's §0 list is updated.

Cost, in compute: 378 cells × 4 policies × 200 futures × 30 steps of six preference terms is of the
order of 10⁷ term evaluations, seconds in NumPy. In work: the package and tests two to three days; JJ.2
one day of runs and writing; JJ.3 two days (the left-turn and overtake menus and the looming noise on
the arrival); JJ.4 one day.

## 6 What could go wrong, stated before the run

- The released preference costs are enormous (collision −10 000, road edge −15 000); ΔG in nats will
  be in the thousands and log ΔG's spread across cells may be dominated by how many sampled futures
  collide. That is the intended mechanism, but it means the Monte Carlo rule (e) is not a formality.
- Variant A may pass (a) and fail (c): the released safety term inside the rollouts would then order
  by absolute speed as it did pointwise. The card's design anticipates this with variant B.
- The intention update may be too slow within 0.3 s of shown lateral motion to lift ΔG in the earliest
  post-onset cells (CP2), in which case ΔG behaves like the ungated rule there; the report gives the
  pre- and post-onset fits separately so this is visible.
- On the left turn, the released looming noise may be too small at 60 m to grade the arrival, in which
  case rule 3(b) fails for a reason that is about the noise constant, not the mechanism; the report
  says which.
- The passenger's alternatives in the video may not be the menu's; a scenario offset would then be
  absorbed into the level and is not separable within this design.

## 7 Queries

@JJ1.Q1(judgment, jonas): The steer-away policy on the cut-in depends on whether the studies' road has a
free lane on the far side; the context files will say. If it does not, the menu is four longitudinal
policies. Confirm that a menu without a steering option is acceptable for the cut-in, or name the
alternative.

@JJ1.Q2(minor, review): σ_a = 0.5 m/s² for longitudinal growth is unverified and is the constant JJ.5
component C3 replaces. Until then it is a placeholder with a sweep; flagged so no report quotes it as
measured.

@JJ1.Q3(judgment, jonas): JJ.4's medium contrast needs perceptual constants (angular noise for a frozen
monocular frame against a moving view) that this project has not sourced. Accept that JJ.4 reports the
fitted ratio and marks the predicted ratio "not yet possible" if no source is found, rather than
inventing constants?
