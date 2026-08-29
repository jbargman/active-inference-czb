# Review gate R.2: the decisions

*2026-08-29, run at tier 1 in an overnight batch session, per the card in
`docs/czb_work_orders.md`. The gate's five questions are answered in the card's
priority order. Everything quantitative below comes from committed scripts with
tracked outputs; the two decisive analyses were pre-registered (models, folds, and
decision rules committed before the runs — commit e9203c6). Where a decision is a
scope call that belongs to Jonas, it is routed to him as a query rather than taken
here.*

## 1 Is the preference field the right scalar? No — ruled against, pre-registered

The comparison the card put first (`replication/czb/cutin2_field_vs_gap.py` →
`out/cutin2_field_vs_gap.md`): the existing field, computed on the second cut-in
study's traces by the exact study-1 code path (k = 12, continuous forms, shown-window
covariates), against a gap threshold of identical model form (lapse + probit, three
parameters each), on identical leave-one-starting-TTC-out folds, decision rule stated
before the run.

| model (best scale) | held-out wRMSE | Spearman |
|---|---|---|
| **gap (log)** | **0.1522** | +0.841 |
| TTC (log) | 0.1679 | +0.805 |
| required deceleration (log) | 0.2888 | −0.158 |
| **field** | **0.3471** | −0.424 |
| chance (train mean) | 0.3202 | — |
| sampling-noise floor | 0.1176 | — |

The pre-registered rule fired at dRMSE = +0.195: **the field is ruled against on its
own scenario** — it scores worse than chance on grouped folds while a
three-parameter gap threshold approaches the sampling-noise floor. The verdict is
robust to excluding the 20 non-modal attention-check participants (+0.202) and to a
post-hoc repair of a trace-noise handicap discovered after the registered run (the
30 Hz ego-speed dither puts a ~1 000-unit control-effort floor under every field
covariate; with the ego speed smoothed the field scores 0.3564 and the verdict is
unchanged). Within matched-TTC rows the smoothed field orders only 14 of 24 rows in
the observed direction (mean ρ −0.10) where the data order 24 of 24 (gap ρ −0.887) —
and the sign derivation below shows that inconsistency is structural, not noise.

Two consequences, both now in force. No document may describe the field as validated
against human data on the longitudinal dimension (blocker B2.Q4's wording rule,
now backed by the analysis it was waiting for). And per the card's own
pre-commitment, the project's claim is restated around what survives (§4).

## 2 The C1 inversion: a covariate defect, found, fixed, and reinterpreted

Blocker B2.Q1 is closed (`replication/czb/c1_covariate_defect.py` →
`out/c1_covariate_defect.md`). The inversion was not in the data or the preference
function but in the covariate window: the C1 lookup included the manoeuvre-onset
frame, where the lane-entry projection — whose lever arm is the longitudinal TTC —
turns at most 6 cm of lateral motion into near-full predicted overlap at the largest
gap (p_lane 0.000 / 0.318 / 0.997 for gaps 10.5 / 16.0 / 21.5 m); and the running
maxima accumulated from the trace start, ~5–16 s before the shown clip, letting a
startup blip floor every 1.5 m overtake cell at 230.9 units. The fix matches the
covariate window to the shown clip (`RANDOM_CLIP_LEAD_S`, `C1_COV_END_S` in
`comfortzone.czb_data`, with property tests). **Decision: C1 stays in the fit** with
the corrected (~1-unit) covariates and identifies the lapse, exactly as the model
assumes.

The second study then revises the interpretation I gave the residual C1 behaviour
when raising B2.Q5. Study 1's three C1 cells are ordered by gap
(0.122 / 0.070 / 0.052), which I read as an ordinary proximity response the
lane-gated field cannot express. The second study's 90 CP1 cells span gaps of
3.9–82 m and are **flat** (rates 0.000–0.115, ρ(gap) = −0.04): drivers do not, in
fact, respond to adjacent-lane longitudinal proximity before encroachment. The
lane-gated flat floor is *supported* at pre-encroachment, and the study-1 C1
gradient is better read as exposure-driven anticipation — study 1 shows 3 conditions
~24 times each (learnable), study 2 spreads exposure over 72 distinct clips, and its
own repeat manipulation shows the learning directly (P(intervene) 0.547 → 0.575 on
the second showing of an identical clip). This is R.1.Q3's account, now with the
mechanism's direct test behind it.

## 3 The lateral term: not built, and the sign derivation that decided it

The gate's original question — re-derive Σ or adopt the Driver's Risk Field — is
answered *neither*, for two reasons that arrived in order.

First, R.2.Q1's instruction was to derive the sign of the distance effect under the
expected-deficit proposal before writing model code. Done numerically on the actual
preference function (`replication/czb/expected_deficit_sign.py` →
`out/expected_deficit_sign.md`), over the second study's own delta-velocity range:
the point field's within-row direction at matched TTC is **inconsistent** — ρ(gap,
d) = +1.00 at TTC 2–3 s, −1.00 at TTC 5–7 s, through the counterfactual-residual
term — and distance-scaled perceptual noise shifts E[d] by at most ~10% with
inconsistent sign. The observed effect is first-order and monotone (24 of 24 rows).
The expected-deficit mechanism therefore **fails as the explanation of the
distance–time anomaly**, per the note's own stop rule; it remains directionally
right only for the lateral-clearance problem.

Second, with §1's verdict, a lateral extension would graft a comfort term onto a
longitudinal core the data have rejected. The pre-registered LTAP and overtake tests
of the expectation proposal (`docs/lateral_and_uncertainty_note.md` §6 steps 2–3)
are therefore **not run**. Kolekar et al.'s DRF is re-positioned: no longer a donor
of a lateral term for our field, but a member of the comparator class for the
restated program (§4) — it is an independently validated instance of "keep one
scalar below a threshold", which is the claim that survives.

## 4 What survives, and what the headline becomes

The card asked the gate to say this explicitly, so: **the project's headline result
is the trait claim, not the field.** What stands, each with its evidence:

1. **A driver carries one comfort-zone level across scenarios.** Per-driver
   criticality-adjusted propensity correlates +0.50 to +0.74 across all six scenario
   pairs, 0.53–0.78 of the reliability ceiling, mean ~0.69 — measured with no field
   at all (`out/cross_scenario_consistency.md`). About a third of reliable
   per-driver variance is scenario-specific, which caps every transfer test.
2. **The boundary distribution is well estimated on its own scale, and it is
   stable.** A.2.v2 regenerated the percentile table under k = 12 + the covariate
   fix: the 50th/80th/95th percentiles moved +0.9% / +0.2% / −0.5%
   (`out/stage1_summary.md`). The lapse–threshold correlation is partly a real trait
   (fitted ρ = −0.717, SE 0.128, against an estimator-artifact baseline of −0.27)
   and does not move the deliverable.
3. **Transfer works once the per-scenario lapse is freed** (re-run under the new
   spec this session; `out/transfer_overtake_summary.md`).
4. **The best within-scenario criticality axis on the decisive dataset is the
   longitudinal gap** (log scale), with TTC close behind and required deceleration
   nowhere — which is a statement about *any* demand-based axis, not only ours.

The restated claim, recommended wording: *each driver carries a scalar comfort-zone
threshold that is substantially shared across scenarios; the right criticality axis
is an open empirical question on which simple scene scalars currently beat the
active-inference preference field, whose kinematic content is ruled out as fitted.*
The elliptical-joint / per-scenario 2D comparator program moves from fallback to
primary for the axis question — this is the fallback position the project recorded
in advance, now triggered by its stated condition.

Program consequences routed to Jonas (queries R.2.Q4–Q6 in the register): whether
B.2/B.3 stay field constructions or become comparator-class constructions; how the
assessment document and any manuscript position the active-inference contribution
(the framing, the calibration pipeline, and the falsification itself are all real
contributions); and whether the handbook's CZB chapters wait for his Word review or
get a correcting note now.

## 5 The A.3 verdict's wording: narrowed

Done in place (`docs/active_inference_for_czb_assessment.md`, dated note): the FAIL
stands for the accumulator we specified — deficit-driven drift, non-leaky, fixed
bound, on this repeated-exposure stimulus set — and licenses no claim about
evidence accumulation as a family, whose standard traffic architectures (looming or
TTC drift, leaky accumulation, collapsing bounds; Bontje et al., 2026) were never
tested.

## 6 The R.1 queries the gate was asked to settle

- **R.1.Q1** (percentile quoting): adopted as a convention in A.2.v2 — every
  percentile is quoted as value, CI, and specification (bias variant, k, covariate
  window); the summary header names the full spec.
- **R.1.Q2** (lapse–threshold correlation): settled by the correlated-effects fit —
  ρ = −0.717 (SE 0.128) against the −0.27 artifact baseline; partly real, does not
  move the 80th percentile beyond the pre-stated rule; hierarchical stays primary.
- **R.1.Q3** (anticipation): turned into a concrete estimator, recorded in
  `docs/czb_validation_roadmap.md` §4c item 5 — a joint study+NDS fit sharing the
  boundary population, with a criticality-dependent paradigm offset
  δ(x) = δ0 + δ1(x − x̄) identified by the slope difference; with the caution that
  δ1 absorbs paradigm *and* field misspecification, which the comparison cannot
  separate.

## References

Bontje, F., van Waveren, F., van Maanen, L., Nallapu, B., Markkula, G., &
Zgonnikov, A. (2026). *Knowing when to move: Evidence accumulation models of human
behavior in traffic* (arXiv:2606.00727). arXiv. https://arxiv.org/abs/2606.00727

Kolekar, S., de Winter, J., & Abbink, D. (2020). Human-like driving behaviour
emerges from a risk-based driver model. *Nature Communications, 11*, Article 4850.
https://doi.org/10.1038/s41467-020-18353-4
