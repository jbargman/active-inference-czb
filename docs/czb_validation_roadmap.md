# Roadmap: deciding whether the field earns its keep

*2026-08-27, evening. Jonas asked for a plan covering the two decidable claims in the
assessment ("the accumulator closes the within-scenario gap"; "the level transfers
across scenarios") and, more broadly, for rolling out everything in the assessment's
ADAS-trigger section. This document is that plan. It also records the answers Jonas gave
to the fitting plan's four questions and what they change. Companion documents:
`docs/czb_fitting_plan.md` (the model and estimation machinery),
`docs/active_inference_for_czb_assessment.md` (the argument this plan tests).*

## 0 What was already run tonight, because it was cheap

- **The overfitting question is answered.** The within-scenario comparison is not an
  in-sample artifact: under leave-one-criticality-out cross-validation (fit on two
  criticality levels, predict the third) the field gives out-of-sample corr 0.864 /
  RMSE 0.147 against the design regressions' 0.934–0.949 / 0.097–0.108, and
  leave-one-timepoint-out gives the same picture (field 0.870, regressions
  0.933–0.948). The regressions genuinely generalize better *within this scenario*,
  including when extrapolating to an unseen criticality level. The field's case
  therefore rests, exactly as stated, on the accumulator, on portability, and on
  state-based deployability — not on surface fit.
- **The perceived-safety correlation exists and is strong** (Jonas's request; figure
  `figures/ps_vs_field.png`, script `replication/czb/ps_vs_field.py`). The stored PS
  scale is perceived *unsafety* (dictionary gotcha 1: higher = less safe). Against the
  field: cell-level Spearman ρ = 0.93 (Pearson r = 0.84) over the 18 cells,
  trial-level ρ = 0.58, and within-criticality trial-level ρ = 0.64 / 0.52 / 0.39
  (TTC4/6/8). The ratings reproduce the same time-compression mismatch as the
  intervention surface: ratings keep climbing through the window where the static
  field flattens — a third independent appearance of the accumulator's signature
  (after P(intervene) and the ratings' shape, the button densities will be the
  fourth).

## 0b Amendments from the same evening's discussion

Jonas's follow-up questions changed four things; recorded here so the stages below read
correctly.

- **The named comparator is now his 2D state rule, not the design regression.** A
  probit in 1/TTC and lateral offset — both observable state variables — reaches
  held-out corr 0.921 on the cut-in surface (field 0.864; design regression 0.934,
  demoted to an upper-bound reference since its covariates are experiment clocks, not
  state). Two things should be said about the 2D rule: within this stimulus family the
  lateral-offset trajectory is nearly identical across criticality levels, so it
  spans almost the same space as the design regression; and its second observable is
  scenario-specific (lane-crossing distance for cut-in, PET for LTAP, clearance for
  overtakes), which is exactly the conventional per-scenario route whose cross-scenario
  version is the elliptical formulation. The transfer test is therefore a three-way
  comparison: one-scalar field, per-scenario 2D rules, elliptical joint.
- **The comfort and dread levels are both fitted, not fixed at 4 and 8.** Jonas's
  correction on the DZB's meaning is adopted: the dread boundary is the deceleration
  drivers do not voluntarily push beyond, a behavioral limit rather than the physical
  a_max — so 8 m/s² is an upper anchor, not the answer, and 4 may also be high for
  comfort. The ordered model fits both levels as free parameters per the hierarchy;
  the 4/8 pair survives only as the staging default for computing example fields.
- **A secondary model fits the conventions.** a_OV,min and t_react (the driver's
  *assumed* worst case and budget — distinct from motor latency) can in principle be
  identified at population level, because they enter the boundary with different
  kinematic signatures (t_react scales with v_ego, a_OV,min with the lead's stopping
  distance, a_allowed with v_react²) and the scenarios span 5.5–30.5 m/s. The primary
  analysis keeps them fixed for falsifiability; the secondary lets the data place
  them, and disagreement between the two is itself informative.
- **Epistemic value gets reconsidered on evidence, not dropped for convenience**
  (stage E below). The deposit contains the authors' own α = 0 runs: rear-end 28
  matched configurations, collision difference exactly 0.000; intersection 6 matched,
  within 0.005; **oncoming 3 matched, collisions 5.7 points lower with the term on**.
  Inert in the longitudinal scenarios, possibly useful in the lateral one
  (`replication/czb/epistemic_ablation_check.py`).

## 1 Stage A — close the within-scenario question (1–2 sessions, all data in hand)

1. **Synthetic-recovery harness** for the stage-1 hierarchical model (fitting plan
   §3). Simulate from known parameters, refit, confirm recovery. Gate for everything
   below.
2. **Stage-1 hierarchical fit** on the Random cut-in surface: per-driver c_i, the
   ordered braking-expectation thresholds, and **both bias variants** — group-level b
   and hierarchical b_i with shrinkage — compared by held-out likelihood and by
   posterior predictive on the C1 cells (the implications question; section 5.1
   below).
3. **The accumulator layer**, fitted on the same surface. Decision criterion, stated
   in advance: the accumulator variant should recover most of the gap to the design
   regressions' cross-validated RMSE (~0.10) without any per-scenario parameter. If
   it does not, that is recorded as evidence against the framework, per the
   assessment. *[Verdict recorded 2026-08-27 at review gate R.1: **FAIL**, and the
   failure is now interpretable — three structurally-argued variants (v1 noise from
   clip start, v2 onset-gated, v3 with a free trial-level threshold spread) all fit
   worse in sample than the stage-0 static probit, and v3's held-out RMSE 0.267 fails
   the pre-registered rule. Cause named in `out/stage2_summary.md`: anticipatory
   criticality-graded responding at C1–C2 where integrated evidence cannot yet exist,
   plus a late-cell criticality gradient shallower than integrated evidence implies.
   The within-scenario claim (a) is settled negative; the framework's case now rests
   on stage B.]*
4. **Button-side validation**: predict the press-time densities (2 396 trials) with
   one paradigm shift δ, fitted both as a level shift and as a rate shift; the shape
   decides. Motor latency fixed per section 5.3.

## 2 Stage B — the transfer test on data we already hold (the gate)

The Random design contains, with the same 43 participants and PS ratings throughout:
cut-in (3 × C1–C6), LTAP (8 PET levels × 2 speeds), cyclist overtake (3 clearances ×
C1–C5), truck overtake (5 lateral offsets). This is exactly the transfer design, held
in-house. What blocks it is field construction, not data:

1. **Cyclist overtake** (first, easiest): same-lane longitudinal geometry, roles fixed
   by instructed vehicle rather than lateral span (the loader mis-assigns these —
   review finding 1.5). The ego closes on a cyclist; the existing rear-end field
   applies nearly unchanged. *[Built 2026-08-28 —
   `docs/overtake_construction_note.md`. "Nearly unchanged" was wrong: the field orders
   the 15 cells at Spearman +0.402 against the clearance label's −0.833, because
   `p_lane` saturates at 0.843–1.000 and never sees the manipulated variable. The
   scenario's criticality is a lateral **comfort margin** — 0.5 m is uncomfortable while
   being uncontroversially collision-free — and the preference function's lateral
   machinery is collision-oriented. A lateral-clearance comfort term is the indicated
   model extension and is a review decision. Despite that, the pilot transfer works once
   the paradigm baseline is matched: see the amendment to step 4.]*
2. **Truck overtake / truck lateral**: the ego passes a stationary or drifting truck
   with lateral clearance as the criticality axis. Needs the lateral-clearance term
   rather than the car-following counterfactual; the preference function's lateral
   machinery (p_lat, and P_lane run "sideways") covers it, but this is a construction
   to argue, not assume.
3. **LTAP**: crossing geometry — the cut-in x/y conventions are meaningless; the
   collision-relevant quantity is arrival-time separation at the conflict zone. This
   is the intersection scenario's world model; the construction should follow the
   authors' intersection scenario the way the cut-in followed rear-end.
4. **The test itself**: fit c (and the accumulator) on cut-in only; predict the other
   three response surfaces with everything frozen. Pre-registered readout: predictive
   correlation per scenario against (a) chance, (b) a per-scenario refit ceiling, and
   (c) the elliptical fallback fitted on conventional indicators. Pre-registered
   confound control: the per-scenario *instruction* differs (intervene / abort /
   yield), so a uniform shift per scenario is permitted in a secondary analysis and
   the primary analysis allows none — both reported.
   *[Amended 2026-08-28 on evidence from the cyclist-overtake pilot. **The primary
   analysis should free each scenario's lapse floor** while keeping the boundary level
   and spread frozen. The pre-onset intervention rate is 0.081 in the cut-in and 0.198
   in the overtake, so a no-shift primary is mis-specified at the baseline before the
   boundary is even consulted: frozen transfer scores RMSE 0.176 against chance 0.158,
   whereas freeing only the lapse gives 0.129 — past chance and within 0.016 of the
   full-refit ceiling (0.113). The lapse is identified by that scenario's C1 cells
   alone, which end where the field is zero by construction, so it cannot absorb
   boundary information; a uniform *level* shift can and does, and stays secondary.
   Evidence: `replication/czb/out/transfer_overtake_summary.md`.]*
4b. **A field-independent bound on the whole stage, added 2026-08-28.** All 43
   participants saw all four Random scenarios, so the one-scalar claim's core
   prediction — that a driver carries one level — can be tested with no field at all,
   by asking whether per-driver position is stable across scenarios. It largely is:
   criticality-adjusted per-driver propensity correlates +0.50 to +0.74 across the six
   scenario pairs, which is 0.53–0.78 of the split-half reliability ceiling (mean
   **0.69**), with per-scenario reliabilities of 0.93–0.98.
   `replication/czb/cross_scenario_consistency.py`. Two consequences: this is the
   strongest evidence for the framing that does not depend on any field construction;
   and it caps step 4 — roughly a third of reliable per-driver variance is
   scenario-specific, so B.4 should be scored against ~0.69 of the signal rather than
   against perfection.

5. **A cheap preliminary before any of that**: the PS ratings exist for all four
   scenarios. Once a scenario's field exists, the cell-level rating-versus-field
   correlation (as run tonight for cut-in) is a transfer check that needs no fitting
   at all. I would run it per scenario as each field construction lands.

**Test-track data (Jonas's offer).** What would make external LTAP/OD data usable, in
order of importance — this matches `docs/data_requirements.pdf`, which was written for
exactly this handoff: (1) paired-vehicle kinematics at ≥ 10 Hz (positions and speeds of
both vehicles on a common clock and datum; headings if turning); (2) a response-onset
label per trial (brake onset, or release/steer onset, extracted however the study
defined it — the definition matters more than the choice); (3) a per-driver identifier
across trials, since the whole point is per-driver levels; (4) the staging protocol
(scripted speeds, PET/gap levels, instruction wording — the instruction confound
again); (5) vehicle dimensions. Nice to have: gaze or distraction state, and any
subjective ratings. With (1)–(3) the test-track data can serve as a *second population*
for the percentile question, not merely a replication.

## 3 Stage C — the percentile sensitivity analysis (cheap; run right after stage 1)

From the fitted population distribution of c: compute the implied trigger onset time
per stimulus for percentiles 50–95 in steps of 5, and report d(onset)/d(percentile) in
seconds alongside the estimation uncertainty of the percentile itself. Decision this
informs, stated in advance: if the trigger moves more per 5 percentile points than per
sampling-uncertainty band, the bottleneck is the percentile *choice* (a policy
question), not the estimator, and further estimator refinement is deprioritized. The
same sweep run on the comfort-versus-dread axis (a_allowed from 3 to 8 m/s²) quantifies
which of the two choices dominates.

## 4 Stage D — the comfort-versus-safety audit (the causation synergy)

For a small grid of candidate triggers (percentile × a_allowed), replay the QUADRIS
ensemble with an intervention fired at the trigger's level crossing and score
counterfactual outcomes with the existing causation machinery (crash probability,
injury-weighted severity, and — for the nuisance side — trigger rate in the
non-crashing seed majority). Output: a two-axis map (safety benefit versus nuisance
frequency) with the CZB percentiles marked on it. This is the concrete version of
"trigger set by comfort, audited by crash outcome", and it directly tests the QUADRARUM
document's ~0.1 s observation on our own ensemble. Effort: moderate — the runner,
weights and metrics all exist; the new piece is the intervention injection.

## 4b Stage E — planning and epistemic value, reconsidered on evidence

The field method's omission of expected-free-energy planning is not purely
convenience, and the distinction matters. What the field *does* include is the
predictive rollout of the **other** vehicle — the lane-entry weight is exactly the
closed-form expectation of the conflict geometry under the target's continued motion.
What it omits is rollout of the **ego's own policies**. For the study-1 stimuli that
omission is arguably correct rather than approximate: the instruction asks when doing
nothing stops being acceptable, which is the pointwise deficit of the no-action
trajectory — the thing we compute. Where policy rollout plausibly matters is where
scenarios differ in escape affordances, which is precisely the transfer set (LTAP:
yield or proceed; overtake: abort or continue). Three bounded experiments, each with a
decision rule:

1. **E.1 — closed-form versus sampled expectation** (small): Monte Carlo the released
   binary gates under the model's own steering noise along the cut-in clips and
   compare with P_lane. If the closed form tracks the sampled expectation within the
   data's resolution, the "field = rollout in closed form" reading is validated
   quantitatively rather than argued.
2. **E.2 — an uncertainty term where the data can see it** (moderate): the truck and
   car cut-ins are matched on TTC levels but differ hugely in occlusion and apparent
   size. If truck responses at matched kinematics are systematically earlier than any
   kinematic covariate explains, an epistemic/precision term earns a place in the
   field; the Button truck trials are the test bed. This is also the unexercised gaze
   half's natural entry point.
3. **E.3 — a policy-set field for the transfer scenarios** (moderate): for fixed
   clips, EFE over a small discrete policy set (a few braking levels; the instructed
   alternatives) is closed-form kinematics, not CEM — cheap. Comfort becomes "the
   best available policy is still acceptable". Decision rule: if the per-scenario
   instruction shifts (stage B.4's secondary analysis) shrink materially when the
   policy set replaces the free shift, planning has earned its way back in; if not,
   the pointwise field stands.

The ablation result in section 0b sits behind all three: epistemic value is inert in
the authors' longitudinal runs, hints at usefulness in the lateral one, and our α = 0
matches an ablation they ran themselves — so nothing above contradicts the validated
base; it extends it where the evidence points.

## 4c What the NDS access is for

Four distinct uses, in the order I would take them:

1. **Estimating the paradigm offset δ empirically.** Fit c on naturalistic brake
   onsets in lead-vehicle and cut-in events (the calibration machinery exists and
   needs only kinematics — `comfortzone.calibrate`), and compare with the study-1
   estimates. The difference *is* the paradigm-plus-context offset, measured rather
   than assumed — the single biggest upgrade available for the absolute-trigger
   question.
2. **Exposure denominators for stage D.** How often routine driving crosses a
   candidate trigger level determines the nuisance rate — the deposit ensembles
   cannot provide this; NDS is the only source that can.
3. **A percentile consistency check.** The distribution of self-selected margins in
   routine driving (steady-state THW at speed, accepted lateral clearances) against
   the fitted comfort-level distribution: drivers should mostly live inside their own
   comfort zones, and the fraction who do not is a direct calibration check.
4. **Transfer events in the wild** — naturally occurring cut-ins and LTAP conflicts
   as a held-out scenario set with no instruction at all.

## 5 The four questions: answers received 2026-08-27, and what follows

**5.1 Bias: test both, and why I leaned toward shrinkage.** Agreed — both variants run
in stage A.2 and the data decides. The reasoning behind my lean, as requested. A
group-level bias asserts every participant shares one false-alarm propensity; a
per-driver unshrunk bias estimates each from ~12 pre-onset trials, where a driver with
1 press in 12 gets b = 0.083 largely made of noise. Hierarchical shrinkage is the
middle position: each driver's estimate is pulled toward the group mean in proportion
to how little data supports it, so with thin data it *behaves* like the group model
except for genuinely extreme drivers. The reason I think the driver dimension is worth
keeping at all is a specific leakage risk: response bias and boundary level are
plausibly correlated across people (a trigger-happy participant both false-alarms at C1
and crosses early at C5). Under a group-level bias, that person's excess C1 responses
have nowhere to go except *into their fitted c_i*, biasing it low — and since the
deliverable is a population *percentile*, distortion concentrated in the tail people is
exactly the distortion that matters. The empirical implications to check when both are
run: the group model should show systematic C1 misfit for the extreme participants,
and, if the leakage is real, a wider fitted σ_c than the shrinkage model. If neither
appears, group-level wins on parsimony and we say so.

*[Resolved 2026-08-27 at review gate R.1; evidence in
`replication/czb/out/bias_variant_diagnostics.md`. Both empirical implications
appeared, confirming this section's prediction — the executing session's query A.2.Q2
had read the direction backwards. (1) Per-driver lapse heterogeneity is real beyond
argument: the sd of per-driver pre-onset rates is 0.204 against a shared-rate
binomial's 0.078 (Monte Carlo p < 0.0001), so a group-level lapse is misspecified as a
matter of data. (2) The leakage signature is present: under the group variant the
fitted thresholds track pre-onset behavior at Spearman ρ = −0.622, and excluding the
C1 cells drops the group σ from 0.341 to 0.281 — pre-onset pressing was indeed being
written into the thresholds. **Decision: the hierarchical lapse is the primary
variant** (population σ = 0.209; median 5 352); the group variant is reported as an
upper sensitivity bracket. Two caveats now attached to the deliverable: the fitted
b_i and c_i correlate at ρ = −0.700 while the model assumes independence — a
trigger-happy driver genuinely does sit lower on the boundary, exactly this section's
trait-correlation conjecture — so a correlated-effects variant is specified in card
A.2.v2 with the rule that if it moves the 80th percentile beyond the current CI
width, it must be settled before any deployment claim; and the pre-onset anticipation
gradient (observed C1 rates fall with TTC where the covariate-driven prediction
rises) holds under both variants, is inexpressible by any lapse floor, and stays a
recorded limitation.]*

**5.2 The braking-expectation question.** Per Jonas: treat `CZB_2` as the human
decision (own braking) for now; a new dataset framed that way is coming and will
supersede this reading. Consequence for stage A: the ordered model still fits two
nested levels; only the *interpretation* of the upper level (dread as "situation
demands hard braking") is held provisionally rather than asserted, and the write-up
should flag it until the new data lands.

**5.3 Motor latency: fixed at 0.25 s, with the rationale.** The accumulator models the
decision, so λ should cover only post-decision motor execution of a prepared keypress.
The chronometric literature conventionally decomposes simple reaction time (~250 ms
total for visual stimuli) into premotor and motor components, with the motor
(execution) component around 70–100 ms and the remainder perceptual-decisional; since
our accumulator absorbs the decisional part but not stimulus-to-cortex transduction,
a value between the pure motor component and full simple RT is defensible. I propose
**λ = 0.25 s, with a sensitivity re-fit at 0.15 and 0.35 s** reported alongside — the
sensitivity bracket matters more than the point choice, because λ trades one-for-one
with the population mean of c and not at all with its spread. *(Reference status, per
house rules: the 70–100 ms motor-component and ~250 ms simple-RT figures are
textbook-level values I have not verified against a source from this machine; they
should be cited properly — Luce's response-time monograph is the standard citation —
before any manuscript uses them.)*

**5.4 Sequence design: excluded, no simulation.** Per Jonas, leaning against; the new
data makes it moot. Decision 8 stands unchanged.

## 6 Order of execution and gates

| step | depends on | effort | decides |
|---|---|---|---|
| A.1 recovery harness | — | small | that the estimator works |
| A.2 hierarchical fit, both bias variants | A.1 | small | bias model; population c |
| A.3 accumulator | A.2 | moderate | claim (a): the time gradient |
| A.4 button validation | A.3 | small | paradigm shift; level vs rate |
| C percentile sensitivity | A.2 | small | where the real bottleneck is |
| B.1 cyclist field + PS check | — (parallel) | small | first transfer evidence |
| B.2–B.3 truck + LTAP fields | — (parallel) | moderate each | transfer coverage |
| B.4 the transfer test | A.3 + B.1–B.3 | small | **claim (b): the gate** |
| D safety audit | A.2, C | moderate | comfort-vs-safety divergence |
| test-track ingestion | Jonas's data | unknown | second population |

My reading of the critical path: A.1 → A.2 → A.3 is the spine; B field constructions
can proceed in parallel sessions; nothing above needs data we do not hold except the
last row.
