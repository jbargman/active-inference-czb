# Work orders: executing the CZB roadmap with a smaller model

*2026-08-27. Jonas asked whether the roadmap's execution can move to a less expensive
model, and what would facilitate that. This document is the facilitation: task cards
precise enough that a capable but cheaper session can execute them without design
judgment, with acceptance criteria that make success checkable and stop conditions
that route genuine judgment calls back to Jonas or a stronger review session. The
recommendation on when to use which model is in section 1; the cards follow.*

## 1 Recommendation on the model split

My honest view: most of the remaining work is well-specified implementation against
existing patterns, and a cheaper model executes that reliably *if* the specification
carries the judgment. The split I would use:

- **Cheaper model, per these cards**: A.1, A.2, A.4, B.1–B.3 constructions, C, E.1,
  document rebuilds, and all reruns.
- **Stronger model (or Jonas)**: interpreting A.2's bias-model comparison, A.3's
  pass/fail verdict, B.4's transfer readout, anything where a card's stop condition
  fires, and a periodic review pass over completed cards (the pattern that caught the
  paired-difference overstatement is worth keeping: execute cheap, review strong).
- Do not hand a cheaper session an open question ("does this look right?") — hand it
  a card. When a card's acceptance criterion cannot be met, the correct output is a
  short failure report, not an improvisation.

## 2 Standing rules for every card (read first, they are load conditions)

1. **Every number that will be quoted anywhere must come from a committed script**
   with its output file tracked. No in-session-only analyses — this rule exists
   because an uncommitted analysis produced an overstated headline once already
   (results doc §4.3b-ii, corrected 2026-08-27).
2. **Run `python tests/test_surprise.py`, `test_comfortzone.py`, `test_causation.py`,
   `test_cutin.py` before and after each card**; all must pass. New behavior gets new
   property tests in the same check() style.
3. **Never modify `src/aidriver/preferences.py` defaults** — released behavior is
   frozen; new behavior goes behind flags defaulting off.
4. **House style** for anything written for Jonas: US English, markdown as source,
   Word + PDF generated (`pandoc` + `docs/build_pdf.py`), no period ending a heading,
   opinions hedged as opinions. OneDrive locks: if a build fails with PermissionError,
   write a `-vN` name and say so.
5. **Environment**: Python 3.14, torch CPU-only, no LaTeX/GPU/gh. Long jobs
   checkpointed and restartable; background runners never piped through `tail`.
6. **Provenance discipline**: cite only verified references; mark anything unverified.

## 3 Task cards

### Card A.1 — synthetic-recovery harness

- **Goal**: prove the stage-1 estimator recovers known parameters before touching
  real data.
- **Build**: `replication/czb/fit_recovery.py`. Simulate the Random cut-in design
  (43 participants × 18 cells × 4 repetitions) from the generative model in
  `docs/czb_fitting_plan.md` §2 stage 1: c_i ~ LogNormal(μ, σ), lapse floor b
  (both variants), P = b + (1−b)·Φ((x − c_i)/σ_resp) with x = the cell's
  `deficit_max` from `comfortzone.czb_data.random_cutin_trials()`. Fit by MAP in
  torch (L-BFGS) with Laplace SEs; also fit the a_allowed parameterization (threshold
  on `a_req_max`).
- **Accept**: over 20 simulated datasets, population μ and σ recovered within 2
  Laplace SEs in ≥ 18; per-driver c_i shrinkage visible (posterior means closer to
  truth than raw per-driver MLEs in RMSE). Runtime under 10 minutes total.
- **Pitfalls**: identifiability of (c, σ_resp) scale — fix σ_resp's prior scale from
  the pilot (≈ 2 200 deficit units); lapse and threshold trade off at C1 — check the
  recovery specifically at b.
- **Stop if**: recovery fails after two honest attempts — report the failure mode,
  do not loosen the acceptance criterion.

### Card A.2 — stage-1 hierarchical fit, both bias variants

- **Goal**: the population distribution of the boundary level, and the bias-model
  decision.
- **Build**: `replication/czb/fit_stage1.py`, reusing A.1's model code on the real
  trials. Fit all four combinations: {deficit axis, a_req axis} × {group-level b,
  hierarchical b_i}. The ordered braking-expectation response enters as two nested
  thresholds (fitting plan §2); both levels free per roadmap §0b.
- **Report** (`replication/czb/out/stage1_summary.md`): population μ, σ with SEs;
  percentile table (50–95 in steps of 5) of the population distribution with CIs;
  held-out log-likelihood (leave-one-participant-out, 43 folds); posterior predictive
  P(intervene) per C1 cell against observed; fitted comfort and dread levels
  translated to a_allowed units and to steady-following THW at 20 m/s via
  `comfortzone.field.critical_thw`.
- **Accept**: all four fits converge; the summary table renders; LOPO likelihood
  distinguishes the bias variants or states that it cannot.
- **Stop if**: the C1 cells misfit under both bias variants (systematic sign pattern
  across criticalities) — that is the anticipation-leak question and needs review.

### Card A.3 — the accumulator layer (review gate on its verdict)

- **Goal**: the pre-registered test: does time-integration close the within-scenario
  gap?
- **Build**: `replication/czb/fit_stage2.py`. Evidence = the per-frame deficit series
  (not the running max) from `stimulus_field`; linear accumulator with gain and
  noise, threshold from A.2's c_i; P(crossed by clip end) per trial via the
  closed-form Gaussian first-passage approximation or 200-path simulation per cell
  (cells share stimuli, so simulate per cell, not per trial). Motor latency fixed at
  0.25 s; sensitivity refits at 0.15 and 0.35 s.
- **Accept / decision rule (pre-stated)**: held-out (leave-one-criticality-out) RMSE
  on the 18-cell surface ≤ 0.11 counts as closing the gap (the 2D state rule's 0.120
  and the design ceiling's ~0.10 bracket the target); > 0.13 counts as failure and
  is reported as evidence against the framework per the assessment.
- **Stop if**: the fitted gain wants to be so large the accumulator degenerates to
  the static threshold — report, since that itself answers the question.

### Card A.4 — button-side validation

- **Goal**: predict the press-time densities from the Random-fitted model with one
  paradigm shift.
- **Build**: `replication/czb/validate_button.py` on
  `czb_data.button_cutin_trials()`. Fit δ once as a threshold shift and once as a
  gain shift; compare predicted vs observed press-time distributions per criticality
  (QQ plots to `figures/`, one page) and report which shape fits.
- **Accept**: the documented cross-paradigm excess (+0.26 at TTC6) is reproduced by
  the shifted model within 0.05 at the fixed-clip checkpoints.

### Cards B.1–B.3 — transfer-scenario field constructions

Template for each: a loader in `src/comfortzone/<scenario>.py` following `cutin.py`'s
structure (role assignment appropriate to the scenario — **by instructed vehicle, not
lateral span**), a field check script in `replication/czb/` producing a
per-criticality deficit figure, property tests, and the PS-versus-field correlation
(the `ps_vs_field.py` pattern) as the acceptance readout.

- **B.1 cyclist overtake** (first): ego closes on a cyclist in lane; rear-end field
  nearly unchanged; criticality = lateral clearance 0.5/1/1.5 m, so the lateral term
  matters — use the actual clearance in `dy`, widths from the trace (cyclist ≈ 0.6 m).
  Accept: deficit ordered by clearance at C2–C5; cell-level PS Spearman ρ reported.
- **B.2 truck overtake / truck lateral**: ego passes a truck with clearance variants;
  the conflict is lateral, so P_lane runs on the *lateral closing* induced by the
  truck's drift (`truck_lateral_movement` traces) and the clearance term carries the
  statics. Accept: same criteria; also record whether the zero-deficit issue appears.
- **B.3 LTAP**: crossing geometry. Build arrival-time separation at the conflict
  zone (the intersection scenario's construction): compute each vehicle's time to the
  crossing-region entry/exit from the traces, and gate the collision/safety terms by
  predicted co-occupancy (the P_lane idea with lateral overlap replaced by zone
  co-occupancy). This card has real design content — **write the construction note
  first (1 page, the lane-entry-note pattern) and get it reviewed before coding**.
- **Stop for all three if**: a trace family's geometry does not fit the template
  (e.g. missing vehicle, broken dimensions beyond the documented truck case).

### Card B.4 — the transfer test (review gate; do not run before A.3 and B.1–B.3)

- Fit on cut-in only (A.2/A.3 configuration frozen); predict each transfer scenario's
  response surface with no refit. Primary: no per-scenario shift. Secondary: one
  instruction shift per scenario. Comparators on identical folds: per-scenario 2D
  state rules (1/TTC-analogue + the scenario's own second observable), and — once
  specified with Jonas — the elliptical joint on the same observables.
- Output: one table, per scenario × model: held-out corr and RMSE against (a) chance
  and (b) the per-scenario-refit ceiling. No verdict prose from the executing
  session; the verdict is a review task.

### Card C — percentile sensitivity

- `replication/czb/percentile_sensitivity.py` from A.2's population distribution:
  implied trigger onset per stimulus for percentiles 50–95 (step 5) × a_allowed on
  the fitted comfort–dread range; report d(onset)/d(5 percentile points) in seconds
  against the percentile's own CI width. One figure, one table.

### Card E.1 — closed-form versus sampled lane-entry expectation

- Monte Carlo the released binary gates under steering noise (heading random walk,
  σ_ω = `CUTIN_W_SD_MODEL`, the model's own dt) along the 12 cut-in clips; compare
  the sampled conflict-probability with `lane_entry_weight`. Accept: max absolute
  difference reported per clip; agreement within ~0.15 through the response window
  validates the closed form, larger structured disagreement goes to review.

### Cards E.2, E.3 and D

Deliberately not carded for cheap execution: E.2 (uncertainty term) and E.3
(policy-set field) involve model design, and D (safety audit) touches the causation
runner's intervention injection. These get cards after their design notes exist.

## 4 Suggested session pattern

One card per session, in card order within a stage; start each session with "read
`handover.md`, `docs/czb_validation_roadmap.md`, and `docs/czb_work_orders.md`, then
execute card X and nothing else"; end each with the card's report, a commit whose
message names the card, and one paragraph appended to the running log in
`replication/czb/out/worklog.md`. Review sessions (stronger model) after A.2, A.3,
and B.4 at minimum.
