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
   assessment.
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
   applies nearly unchanged.
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
