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

### Card S.1 — draft the `perform-research` skill (first task for the next session)

- **Goal**: a reusable, iteratively updatable skill that captures how research is
  performed in this collaboration — so the working discipline survives model changes,
  session changes, and time. Jonas asked for it explicitly, drafting delegated to the
  next (cheaper) session, with the instruction to also look at what exists elsewhere
  online and borrow with attribution.
- **Build**: draft `C:\Users\bargman\.claude\skills\perform-research\SKILL.md` with
  frontmatter (name, description triggering on research execution, analysis tasks,
  fitting runs, and model handovers in this project family). Required contents, from
  this project's accumulated practice:
  1. **Reproducibility discipline**: every quoted number from a committed script with
     tracked output; regeneration commands logged; generated artifacts never
     hand-edited; the 2026-08-27 paired-difference correction as the cautionary tale.
  2. **Verification discipline**: property tests before and after every task; verify
     by two independent routes where feasible; results that contradict documented
     findings get surfaced, never silently reconciled.
  3. **Documentation discipline**: markdown as source of truth, Word/PDF generated;
     dated handover files per arc plus a standing `handover.md` entry point; decisions
     recorded with their reasoning and their location; the `jonas-academic-writing`
     conventions for anything addressed to Jonas.
  4. **Between-model handover protocol**: the entry sequence (handover chain →
     roadmap → work orders), one card per session, the escalation triggers and review
     gates (copy from `handover_2026-08-27.md` §8 — that list is the current
     authority), worklog appends, and the rule that a cheaper session executes cards
     and never improvises around a failed acceptance criterion.
  5. **Statistical practice**: uncertainty conventions stated and resampled
     completely (all variance sources); comparisons as differences; held-out
     validation for any model comparison; pre-stated decision rules for verdict
     experiments.
- **Research step**: search online for existing practice worth borrowing — multi-
  agent / multi-model handoff patterns, LLM-assisted research workflow guides,
  lab-notebook and reproducibility standards (e.g. from open-science communities),
  and any published skill/prompt libraries for research execution. Cite what is
  borrowed; mark unverified claims per house rules.
- **Accept**: the draft SKILL.md exists, is under ~300 lines, cites its sources, and
  ends with an explicit "for Jonas's review" note. **Do not treat the skill as active
  until Jonas approves it**; iterate on his comments in later sessions.
- **Stop if**: unsure whether some practice is project law or one session's habit —
  list the uncertain items in the draft for Jonas to rule on rather than guessing.

### Card R.1 — review gate after A.2/A.3/A.4 (for the stronger model)

*[Executed 2026-08-27 by a tier-1 review session. Decisions: hierarchical lapse is the
primary A.2 variant (evidence: `replication/czb/out/bias_variant_diagnostics.md`);
the A.3 accumulator is repaired by gating accumulation at manoeuvre onset, and A.3/A.4
were re-run at the gate as v2. All nine queries resolved or carried in the work log;
register regenerated. Follow-up work is card A.2.v2 below.]*

- **Goal**: close the queries the executing session raised, in severity order, and
  decide the two things it deliberately did not decide.
- **Read first**: `replication/czb/out/query_register.md` (generated — the work log is
  the source of truth), then `stage1_summary.md`, `stage2_summary.md`,
  `button_validation_summary.md`, then the three worklog entries dated 2026-08-27.
- **The two decisions that block downstream work:**
  1. **A.2.Q2 — the bias variant.** Group-level versus hierarchical lapse moves the
     between-driver spread 0.341 → 0.209, a 39% change in the quantity a percentile is
     made of, while held-out likelihood separates them by 0.6 units over 3 096 trials.
     The fitted per-driver lapse spread is large (sd 2.76, logit scale), so the
     hierarchical lapse absorbs variation the group model gave to the threshold — the
     opposite direction to the leakage argument in `docs/czb_validation_roadmap.md`
     §5.1, which should be revisited or corrected in the light of it. Deciding this
     fixes the headline percentile. *[Corrected at the gate, 2026-08-27: the claimed
     contradiction was a misreading. Roadmap §5.1 predicted that under real leakage the
     GROUP model shows the wider σ_c — which is exactly the observed ordering
     (0.341 > 0.209), so the observation confirms §5.1 rather than contradicting it.
     Decision and evidence: `replication/czb/out/bias_variant_diagnostics.md`.]*
  2. **A.3.Q1 — the accumulator's specification.** The pre-registered verdict is FAIL,
     but the in-sample fit is worse than the simpler model it extends, and the cause is
     identified: noise accumulating through 15.1 s of empty pre-onset clip. Choose the
     remedy (leaky accumulator; accumulation starting where evidence exists; or
     something else), then A.3 and A.4 are re-run and their verdicts mean something.
     Until then neither FAIL should be quoted as evidence about the framework.
- **Also verify, not just accept**: that the numbers quoted in the three summaries come
  from the committed scripts (the failure mode with precedent here is a number that
  exists only in a transcript); and that A.2's percentile table is read with its two
  minor caveats attached (A.2.Q4, A.2.Q5).
- **Owed work the executing session named**: A.2.Q3 asks for the pre-onset predictive
  under *both* bias variants; only the better-fitting one was checked.
- **Accept**: every open query either resolved with a `RESOLVED <card>.Q<n>: ...` line
  appended to the work log, or explicitly carried forward with a reason; the register
  regenerated; and if a decision changes a documented plan, that document corrected in
  place with a dated note.

### Card R.2 — review gate: the lateral term and the distance–time anomaly (for the stronger model)

*[Executed 2026-08-29 at tier 1; the record is `docs/r2_gate_decisions.md` and the
worklog entry of that date. Outcomes, against the numbered tasks below: (1) the
pre-registered field-versus-gap comparison on the second cut-in study ruled **against
the field** (held-out wRMSE 0.347 versus the log-gap threshold's 0.152, chance
0.320; robust to the attention exclusion and to a trace-noise repair) — the
project's claim is restated around the trait (task 4); (2) the C1 inversion was a
covariate-window defect, fixed (B2.Q1 closed; C1 stays in the fit); (3) the lateral
term is NOT built — the R.2.Q1 sign derivation kills the expected-deficit distance
mechanism and the section-1 verdict removes the ground for a lateral graft; the
DRF becomes a comparator, not a donor; (4) the headline becomes the one-scalar
TRAIT claim (69% shared signal, stable percentiles, freed-lapse transfer), with
the criticality axis open and gap currently leading; (5) the A.3 wording is
narrowed per Bontje et al. in the assessment. R.1.Q1/Q2/Q3 settled (see register).
Program consequences are queries R2.Q4-Q6 for Jonas.]*

*(Added 2026-08-28 at Jonas's request. This is a **design** gate, not execution: two
findings have outrun what the executing session should decide alone, and the literature
that bears on them has been read and summarized. Run at tier 1.)*

- **Read first**: `docs/lateral_and_uncertainty_note.md` (the argument and the five
  papers), then `docs/overtake_construction_note.md` §4 and §6 (where the two findings
  came from), then `replication/czb/out/overtake_field_check.md` and
  `out/transfer_overtake_summary.md`.
*[Rewritten 2026-08-28 after the B.1 arc and the arrival of `02_Cut-in`. The gate now
has a decisive dataset and a much sharper question than when it was drafted. **Read
`handover_2026-08-28.md` §1–2 first.**]*

## What this gate must decide, in priority order

**1. Is the preference field the right scalar at all?** This is now the live question,
and it was not before. In the study-1 cut-in design relative speed is constant, so
correlation(gap, TTC) = 1.0000 and every longitudinal fit is equally consistent with a
gap threshold. The second cut-in study breaks that: over 10 944 trials, gap orders the
response at ρ −0.887, TTC at −0.807, and required deceleration — the quantity our safety
terms are built from — at +0.238. **The first task is to fit the existing field to the
second cut-in study and compare it against a one-parameter gap threshold on identical
held-out folds.** If the field does not beat a gap threshold there, the honest conclusion
is that the field's kinematic content is not carrying the explanation, and the project's
claim has to be restated around what does survive (the transfer trait, §4 below) rather
than around active inference as a mechanism. Pre-register the comparison before running
it.

**2. Diagnose the C1 inversion** (blocker B2.Q1). At C1 the cut-in conditions differ
two-fold in gap and behaviour is ordered accordingly, but the field ranks them backwards
(deficit 1 / 1509 / 2907 for gaps 10.5 / 16.0 / 21.5 m). The lane gate is the obvious
suspect. Until this is fixed the fitted lapse is absorbing real boundary signal and
should not be called a response floor. Cheap, and it gates the interpretation of every
existing fit.

**3. Decide the lateral term** — the original purpose of this gate. The cyclist overtake
needs a lateral *comfort* term; `p_lane` saturates at 0.843–1.000 and the symmetric
projection over-corrects. Kolekar et al.'s Driver's Risk Field is the strongest donor:
same claim as ours ("keep a scalar below a threshold"), lateral dimension built in,
validated on overtaking. Decide whether to re-derive the spread from our own predictive
model or adopt the DRF's form (Gaussian cross-section, parabolic height to a
speed-scaled look-ahead, width linear in arc length and steering).

**4. Rule on what survives regardless.** The cross-scenario result needs no field:
~69% of the reliable per-driver signal is shared across all four scenarios. That
supports the one-scalar *trait* claim independently of whether our particular scalar is
right, and it caps any transfer test. The gate should say explicitly whether the
project's headline becomes this, if task 1 goes against the field.

**5. Narrow or confirm the A.3 wording.** Bontje et al. (2026) report that traffic
accumulators conventionally drive on looming or TTC, not a comfort deficit, and list
leaky accumulation and collapsing bounds as standard. Our FAIL was pre-registered and
stands for the accumulator we specified; decide whether the assessment's broader claim
needs narrowing.

**A caution for whoever runs this.** The sign derivation below was attempted on
2026-08-28 and produced a problem: the expectation route gives the right direction for
the lateral term but the *wrong* one for the distance effect (a more distant conflict
would get a higher expected deficit, i.e. more discomfort at larger gaps, opposite to
what is observed). So the two findings do not have one fix, and
`docs/lateral_and_uncertainty_note.md` carries a dated correction saying so. Do not
re-adopt the unified story without redoing that derivation.

- **The problem, in one line**: the field evaluates the deficit along a single predicted
  trajectory, and therefore cannot express either (a) that a collision-free pass at
  0.5 m is uncomfortable, or (b) that a distant conflict at matched time is judged
  differently from a near one.
- **The proposal to assess**: take the deficit in expectation over a predictive
  distribution, `E[d(x)]` with `x ~ N(x̂, Σ(t))`, rather than at the point estimate.
  Argued in the note as native to active inference — expected free energy is already an
  expectation under a predictive distribution, which the released model collapses to its
  mean because its scenarios are longitudinal. This is the same move as the lane-entry
  work, which is the closed form of an expectation the closed loop computes by rollout.
- **The decisions that need making**, none of which the executing session should take:
  1. **Is the sign right?** For our preference function's actual cost asymmetry, does
     E[d] rise or fall as Σ widens? Do this analytically or numerically **before any
     code**. If the sign is wrong the mechanism is not the explanation, and the
     honest outcome is a lateral term motivated on its own terms instead.
  2. **Whose functional form?** Re-derive Σ from our own predictive model, or adopt
     Kolekar et al.'s DRF shape (Gaussian cross-section, parabolic height to a
     speed-scaled look-ahead, width linear in arc length and steering angle) with its
     six constants? The DRF is independently validated on overtaking and car-following
     and is structurally the same claim as ours — "keep a scalar below a threshold" —
     so inheriting it is defensible, but it is a different model's parameterization.
  3. **How much fitting is acceptable?** Σ's scaling adds at least one parameter
     upstream of the boundary. The project's standing position is that the field
     carries no constants fitted to the responses; k = 12 (card B.1) already bends
     that, and this would bend it further. Whatever is decided, it must be calibrated
     on one scenario and frozen before any transfer scenario is scored.
  4. **Does the A.3 verdict need revisiting?** Bontje et al. (2026) report that traffic
     accumulators conventionally drive the drift with looming or TTC, not with a
     comfort deficit, and list leaky accumulation and collapsing bounds as the standard
     architectures. Our FAIL was pre-registered and stands as a statement about the
     accumulator we specified; the gate should decide whether it also licenses the
     broader claim currently in the assessment, or whether that claim needs narrowing.
- **Pre-registered tests, in order** (the note's §6): derive the sign; then LTAP, whose
  two-speed design separates time from distance by construction and where the predicted
  effect is a speed difference of the observed sign at matched PET; then the cyclist
  overtake, where the prediction is that cell ordering improves materially on the
  current Spearman +0.402 without the model being given the clearance.
- **Also settle**: R.1.Q1 (how percentiles are to be quoted — a convention, see the
  note in card A.2.v2), R.1.Q2 (on the evidence in
  `out/lapse_threshold_artifact.md`), and R.1.Q3 (Jonas's position is that the
  anticipation bias should be lived with and corrected using NDS data rather than
  designed away; the gate should turn that into a specific estimator).

### Card B.2.v2 — the second cut-in study, and the pre-onset defect it exposed

*[Executed 2026-08-29. Item 1: the C1 inversion was a covariate-window error — the
lookup included the manoeuvre-onset frame (whose lane-entry projection inverts the
ordering through its TTC lever arm) and the running max accumulated trace-start
frames never shown to participants. Fixed in `comfortzone.czb_data` (shown-window
accumulation, C1 endpoint −0.15 s); diagnosis in `out/c1_covariate_defect.md`;
decision: C1 joins the fit with the corrected covariate. Item 2: the study was
promoted and used as R.2's primary venue — the field-versus-gap comparison ran on
it (`out/cutin2_field_vs_gap.md`), attention-check handling as specified below
(kept in the primary, excluded in a sensitivity, verdict unchanged). B2.Q1/Q2/Q4/Q5
resolved; see the register.]*

*(Added 2026-08-28. The first item is a **blocker on the interpretation of every fit run
so far** and should be taken before A.2.v2; the second promotes a dataset.)*

- **The C1 defect (query B2.Q1).** The project treats the C1 cells as carrying no
  boundary information. That is false: at C1 the three cut-in conditions differ by a
  factor of two in car-following state (gap 10.5 / 16.0 / 21.5 m, THW 0.34 / 0.52 /
  0.70 s) and the behaviour is ordered accordingly (0.122 / 0.070 / 0.052), while the
  field ranks them **backwards** (deficit 1 / 1509 / 2907). Evidence:
  `replication/czb/out/response_style_and_anticipation.md` §Test C. Diagnose the
  inversion — the lane gate is the obvious suspect, since the lead is fully in the
  adjacent lane at C1 — then decide whether C1 joins the boundary fit with a corrected
  covariate or is excluded and the lapse identified elsewhere. **Until this is settled
  the fitted lapse must not be described as a response floor**, because it is absorbing
  real boundary signal, and that is a fifth explanation for the R.1.Q2 correlation that
  no earlier analysis considered.
- **Promote the second cut-in study (query B2.Q2).** `02_Cut-in`: 10 944 trials, 168
  participants, same three response variables including the ordered braking question.
  Its delta-velocity factor multiplies with TTC into distance by construction, so
  matched-TTC cells span 1.6–78 m of gap. Measured in `out/cutin2_scope.md`: all 24
  matched-TTC rows run negative, gap orders the cells at rho −0.887 against
  time-to-collision's −0.807, and required deceleration manages only +0.238. This is the
  R.2 distance-versus-time question answered far more sharply than LTAP can answer it,
  in the scenario whose field already exists. Use it as R.2's primary venue; keep the
  LTAP field for the transfer test but off the critical path.
- **Analysis constraint (query B2.Q3)**: TTC 5/6/7 are between-subjects and the DV and
  CP subsets are split-half, so participant means must be formed before aggregating.
- **Two more data-handling facts about `02_Cut-in`, found 2026-08-28 and not in its own
  documentation**: the annotated trials file carries **144 participants**, not the 168 the
  context document states, so exclusions appear to have been applied already and the
  effective n should be taken from the file rather than the prose. And there is exactly
  **one attention-check trial per participant** (`attention1` nonzero on 144 trials);
  the answers split 124 / 16 / 4 across three values, so roughly 20 participants gave a
  non-modal answer. Whoever fits this must decide explicitly whether to exclude them —
  this session did not, because the correct answer is not documented.
- **Exposure effect**: the same study shows P(intervene) rising from 0.547 to 0.575
  between the first and second showing of an identical clip (3 456 pairs, SE 0.007) —
  the direct test of R.1.Q3's mechanism that study 1 cannot support, and it comes out in
  the direction R.1.Q3 predicts.
- **Not proposed**: `03_CAMP`, per Jonas.

### Card A.2.v2 — regenerate stage 1 under the corrected validation code, and test the correlated-effects variant

*[Executed 2026-08-29 (28 min; `out/stage1_summary.md`, log `out/log_stage1_v2.txt`).
Percentiles essentially unchanged (50th 5352 → 5400, +0.9%; 80th +0.2%; 95th −0.5%;
sigma_pop 0.200) — the k = 12 and C1-covariate-fix effects largely offset, inside
the card's expected band. The product-grid LOPO now separates the bias variants
decisively (hier +52.7 units, was +0.6 under the diagonal defect). The correlated
variant converged: rho = −0.717 (SE 0.128) against the −0.27 artifact baseline —
partly real — and moves the 80th percentile 17 units against the pre-stated ~254
threshold, so **the hierarchical variant stands as primary**, correlated reported
as robustness. The ordered comfort/dread levels moved more (3703 → 3418 /
6397 → 6572; query A2v2.Q3). The artifact baseline itself is stale under the new
covariates (query A2v2.Q2).]*

*(Added at review gate R.1, 2026-08-27. Cheap-model card; long-running, overnight is
fine.)*

- **Why**: R.1 found and fixed two defects in `fit_stage1.py`'s validation code (not in
  the fits): the hierarchical LOPO integrated the two random effects on the same
  quadrature nodes (the diagonal of the 2D integral, asserting perfect rank
  correlation), and the C1 predictive plugged in the hier variant's *median* lapse
  where the population mean is required. The stored `out/stage1_summary.md` therefore
  carries a LOPO comparison and a C1 table computed under those defects. R.1 also
  found the fitted b_i and c_i correlate at Spearman −0.700 while the model assumes
  independence, and specified a correlated-effects check.
- **Build**: (a) re-run `python replication/czb/fit_stage1.py` as committed (the fixes
  are in place; 15 LOPO folds as before). (b) Add `fit_hier_corr` to
  `fit_stage1.py`: the hierarchical-lapse model with correlated effects — driver
  threshold uses z1, driver lapse uses ρ·z1 + √(1−ρ²)·z2 on the same product
  Gauss-Hermite grid, one extra hyperparameter ρ fitted as atanh(ρ) with prior
  Normal(0, 0.75) on the atanh scale (weakly informative: 95% prior mass within
  |ρ| < 0.9; motivation: the posterior-mean correlation −0.700 must be reachable
  without being presumed). Report its σ_pop, ρ, and the 50/80/95th percentiles
  alongside the two existing variants.
- **Accept**: summary regenerated; the LOPO comparison quoted under product-grid
  integration; the correlated fit either converges with usable SEs or is reported as
  not identified (also an acceptable outcome — 43 drivers is thin for a correlation).
- **Decision rule (pre-stated at R.1)**: if the correlated variant moves the 80th
  percentile by more than the hierarchical variant's current CI half-width (~250
  deficit units), escalate to review before any percentile is quoted downstream;
  otherwise the hierarchical variant stands as primary with the correlated fit
  reported as a robustness line.
- **Stop if**: the correlated variant's optimizer or Hessian fails after two honest
  attempts — report, keep the hierarchical variant primary, carry the query.
- **Added 2026-08-28, and this card must now run before any percentile is quoted**:
  the CZB staging path adopts `lane_entry_shape_k = 12` (`comfortzone.cutin.
  CZB_LANE_ENTRY_SHAPE_K`, Jonas's decision — argument in
  `docs/overtake_construction_note.md` §5). That changes the covariate in **3 of the 18
  cells** — TTC4/C2 by +26%, TTC6/C1 by −27%, TTC8/C1 by +8%; the other fifteen are
  already at saturated overlap and are bit-identical. The changed cells are the early,
  partially-overlapping ones, which are exactly the cells that identify the lapse, so
  the stage-1 fit and the whole percentile table must be regenerated under k = 12 before
  being quoted. Report the old and new percentile tables side by side, since the
  difference is the price of the k decision and should be visible. **Expected size,
  measured in passing on 2026-08-28**: the stage-2 refit under k = 12 returns a
  between-driver spread of **0.194** against the **0.209** fitted under k = 0, so the
  percentile table should move by roughly 7%. If it moves by much more than that,
  something else has changed and the run needs checking before anything is quoted.
- **The percentile-reporting convention (R.1.Q1), to adopt here**: every percentile is
  quoted as a triple — value, CI, and the specification it came from (bias variant and
  k). The summary table gets a header line naming both. This is a convention, not an
  analysis, and it is cheap to adopt now.

### Card B.3.v2 — the LTAP field (re-scoped 2026-08-28)

*(Replaces the B.3 sketch below for planning purposes; that card's construction advice
still stands. Re-scoped because the LTAP data turns out to be the richest transfer
target, not the hardest-to-justify one.)*

- **Why it moved up**: 3 096 Random trials, the same 43 participants, **18 well-filled
  cells** (9 PET levels × 2 *oncoming-vehicle* speeds, 172 trials each) and an intervention range
  of 0.110–0.907 — a wider dynamic range than the cyclist overtake (0.140–0.686) and
  comparable to the cut-in. The cyclist overtake, by contrast, has one condition
  (1.5 m) that is flat across all five timepoints, so it carries roughly two
  informative criticality levels.
- **What it uniquely offers**: the two-speed axis is the identifying variation the
  roadmap §0b wants for the *secondary* model — `t_react` scales with v_ego and
  `a_OV,min` with stopping distance, so 50 vs 70 km/h at matched PET separates them.
  Note the direction, which is worth understanding before modelling: intervention is
  **lower** at 70 km/h at every PET level (e.g. PET2: 0.605 at 50, 0.360 at 70). The
  speed manipulated is the **oncoming** vehicle's (checked in the traces); the ego holds
  13.9 m/s in both, so PET and the ego's own kinematics are matched and the effect is
  carried entirely by distance at matched time.
- **What it lacks**: no `timepoint` — there is no truncation series, so LTAP yields a
  criticality × speed surface and not a criticality × time surface. Cross-scenario
  comparison must therefore be on criticality, or per-driver (see below).
- **Build**: the construction note first, per the original B.3 card — crossing
  geometry, arrival-time separation at the conflict zone, co-occupancy gating. The
  cut-in x/y conventions are meaningless here.
- **Cheap partial comparison, available now and already run**:
  `replication/czb/cross_scenario_consistency.py` compares all four scenarios with **no
  field at all**, using the fact that every participant saw all four. Per-driver
  criticality-adjusted propensity correlates +0.50 to +0.74 across scenario pairs,
  which is 0.53–0.78 of the split-half reliability ceiling (mean 0.69).

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

*[Verdict recorded 2026-08-27 at review gate R.1: **FAIL**, final and quotable. The
gate repaired two diagnosed misspecifications (v2: noise gated at manoeuvre onset;
v3: a free trial-level threshold spread, the analogue of stage 1's σ_resp), verified
v2's degenerate optimum was global (`fit_stage2.py --scan`), and pre-committed to v3
as the last iteration. v3: in-sample 0.178 vs the static probit's 0.125; held-out
0.267 against the ≤ 0.11 / > 0.13 rule. Structural cause in `out/stage2_summary.md`.
Do not re-run this card; the accumulator question is closed for this stimulus set.]*

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

*[Re-run 2026-08-27 at review gate R.1 under the final (v3) accumulator: still FAIL
(worst checkpoint discrepancy 0.310), attributable to the accumulator's recorded A.3
inadequacy. What survives: the paradigm effect's direction (earlier pressing in
Button) is confirmed; the level-versus-rate form is NOT distinguished (both shifts
reach RMSE 0.163), so handbook ch. 11 decision 3 stays open. Do not re-run without a
new response model.]*

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
  *[Executed 2026-08-28; full account in `docs/overtake_construction_note.md`. The
  loader is `src/comfortzone/overtake.py`, validated against the study's own clearance
  labels (0.506 / 1.004 / 1.501 m against 0.5 / 1 / 1.5). Three corrections to this
  card: roles must come from the instructed vehicle because the cut-in's lateral-span
  rule is **inverted** here (the ego moves, not the target); the lateral coordinate is
  `Location_Y` — `Offset` inverts the criticality ordering; and the cyclist width is in
  the trace (0.582 m), not assumed. The card's premise did **not** hold: the field
  orders the 15 cells at Spearman +0.402 against the clearance label's −0.833, because
  `p_lane` sits at 0.843–1.000 all through the window and cannot see the manipulated
  variable. The scenario's criticality is a lateral *comfort margin*, not a collision
  geometry. Adding a lateral-clearance comfort term is a preference-function change and
  is left as a review decision.]*
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

*[Adjusted 2026-08-27 at review gate R.1: A.3's FAIL removes the accumulator from
this card. The transferred model is the stage-1 static threshold, hierarchical-lapse
variant (population median 5 352, σ 0.209), everything frozen. The three-way
comparison (one-scalar field vs per-scenario 2D rules vs elliptical joint) is
unchanged.]*

*[Adjusted again 2026-08-28, on evidence from the B.1 pilot transfer
(`docs/overtake_construction_note.md` §6). **The primary analysis should freeze the
boundary and free each scenario's lapse**, not freeze everything. The pre-onset
intervention rate is 0.081 in the cut-in against 0.198 in the cyclist overtake, so a
no-shift primary starts every transfer cell ~0.12 low for reasons unrelated to the
boundary: frozen transfer scores RMSE 0.176 against chance 0.158, while freeing only
the lapse gives 0.129 — past chance and within 0.016 of the full-refit ceiling. The
lapse is identified by that scenario's C1 cells alone, which end where the field is
zero by construction and therefore carry no boundary information; the roadmap's
secondary "one uniform level shift per scenario" does absorb the boundary and should
stay secondary. Also: score against the field-independent ceiling in
`out/cross_scenario_consistency.md` — only ~69% of the reliable per-driver signal is
shared between scenarios, so a perfect one-scalar model cannot reach 100%.]*

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

### Card Q5.1 — world surprise on the data in hand, with no preference function (2026-09-02)

Specified in full in `docs/surprise_without_the_field.md` §6 (the R2.Q5 design note);
read that note first, the card is not repeated here. In one line: a constant-velocity
Gaussian predictor of the *other* agent's body-frame position, residual information and
antithesis via `src/surprise/`, four pre-stated tests (onset independent of lane-change
duration on study 2; identically zero on the cyclist overtake; surprise-alone and
surprise × inverse-gap as added covariates under the registered R.2 fit and folds, in a
new script; the CAMP braking-lead onset check). Decision rules are in the note. Touches
no preference code and front-runs neither B.2 nor B.3. Runs after Jonas has reviewed the
note (query Q5.Q1).

### Cards EL.1–EL.3 — the CZB ellipse (2026-09-02)

Specified in full in `docs/czb_ellipse_design_note.md` §6; read that note first. EL.1
(now, study 2, no new loaders): does a second axis earn its place against the R.2-winning
1D log-gap threshold — linear 2D rule and quadratic form on identical registered folds,
decision rules in the note. EL.2 (after B.2/B.3.v2 loaders): the per-driver level shared
across the per-scenario forms via the stage-1 estimator, the B.4 transfer as amended,
with the scale-confound convention stated in the header. EL.3 (naturalistic data): the
population reference per scenario and the two percentiles side by side. Runs after Jonas
has ruled on query EL.Q1 (which population the ellipse's percentile refers to).

## 4 Suggested session pattern

One card per session, in card order within a stage; start each session with "read
`handover.md`, `docs/czb_validation_roadmap.md`, and `docs/czb_work_orders.md`, then
execute card X and nothing else"; end each with the card's report, a commit whose
message names the card, and one paragraph appended to the running log in
`replication/czb/out/worklog.md`. Review sessions (stronger model) after A.2, A.3,
and B.4 at minimum.

*[Card order after gate R.1, 2026-08-27. Stage A is closed (A.1–A.4 done; the A.3/A.4
FAILs are recorded verdicts, not open work). The remaining cards, in the order a
cheap-model session should take them:*

1. *B.1 — cyclist-overtake field construction (small, next).*
2. *C — percentile sensitivity (small, cheap; uses A.2's decided hierarchical
   variant: median 5 352, σ 0.209).*
3. *A.2.v2 — regenerate stage 1 under the corrected validation code + the
   correlated-effects check (long-running; a good overnight companion to B.1 or C).*
4. *B.2 — truck field construction; B.3 — LTAP (write its construction note first and
   have it reviewed before coding, per the card).*
5. *B.4 — the transfer test (review gate; static stage-1 model per the R.1
   adjustment).*

*Queries in `replication/czb/out/query_register.md`: A.1.Q2 (a_req axis) stays a
blocker for the truck check only; R.1.Q1–Q3 are for Jonas/review and block nothing
above.]*
