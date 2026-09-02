# Review of the decisive pipeline: the R.2 field-versus-gap comparison

*2026-09-02, tier-1 session, at Jonas's instruction ("an adversarial review of the
decisive-test pipeline"). The headline negative result of the project rests on
`replication/czb/cutin2_field_vs_gap.py`, the covariate code in `src/comfortzone/`
and the preference terms in `src/aidriver/preferences.py`. The C1 covariate-window
defect (closed 2026-08-29) showed that this code can hide sign-reversing errors, and
gate R.2 ran shortly after that fix. This document records what was re-derived, what
was found, and what it changes. Every number quoted comes from a committed script with
a tracked output: the registered `out/cutin2_field_vs_gap.md`, and the new post-hoc
`out/cutin2_lane_gate_diagnostic.md` (script
`replication/czb/cutin2_lane_gate_diagnostic.py`). Nothing here re-decides the gate;
the pre-registered verdict stands as registered.*

## 0 The outcome in one paragraph

The verdict is sound and, as far as I can tell, not an artifact of the pipeline. An
independent fitting route reproduces every registered number to the third decimal, and
a cell bootstrap puts the field-minus-gap difference at +0.17 to +0.22 against a
pre-registered margin of 0.01. The review's substantive contribution is a decomposition
of *why* the field loses, which the gate record did not have: about 44% of the loss is
the lane-entry gate, a construction this project added on 2026-08-27, which suppresses
the deficit in exactly the cells participants respond to most, because it makes the
conflict depend on the lateral pace of the cut-in and participants do not; the
remaining 56% is the longitudinal magnitude itself, the released model's worst-case
counterfactual, which in this study's regime orders matched-TTC cells by the absolute
speeds of the two vehicles rather than by the gap. Both failures are interpretable,
both are properties of the field rather than of the code, and each gives the R2.Q5
exploration a concrete empirical constraint on what a replacement reference must do.

## 1 What was checked, and how

1. **The registered script, line by line**: the cell construction (participant means
   per video, then weighted cell means), the CP1 exclusion, the four covariates and
   their signs, the log transforms, the fold construction, the metric, the chance and
   noise-floor references, and the decision rule.
2. **The field covariate's provenance**: `cutin_predictors` and `cutin_params` in
   `src/comfortzone/cutin.py`, the shown-window accumulation, and the six preference
   terms with their gates in `src/aidriver/preferences.py`, read against the values
   the study's cells actually take (the deficit on these cells is almost entirely the
   safety term; the control-effort term contributes the ~1 000-unit jitter floor the
   registered report's section 5 already documents).
3. **An independent fit**: the same three-parameter threshold model fitted by a dense
   grid over threshold and spread with the lapse solved in closed form, instead of the
   registered multi-start L-BFGS-B, on the same cells, folds and metric.
4. **A decomposition**: the field recomputed with the lane-entry gate forced to 1, raw
   and with the ego-speed jitter removed, and the registered comparison re-run on it.
5. **Local sensitivities** of the safety magnitude to gap, lead speed and ego speed at
   four of the study's cells, to read the within-row failure mechanistically.
6. **The trace-versus-annotation discrepancies** of the registered report's section 0,
   located by design cell.

## 2 The verdict is numerically robust

| covariate | grid fit wRMSE | registered wRMSE |
|---|---|---|
| field | 0.3508 | 0.3471 |
| gap (log) | 0.1531 | 0.1522 |
| TTC (log) | 0.1679 | 0.1679 |
| required deceleration (log) | 0.2890 | 0.2888 |

Field minus gap: +0.198 by the grid, +0.195 as registered; cell-bootstrap 95% interval
[+0.174, +0.222]. The differences between the two routes are at the third decimal and
come from the flatness of the threshold objective on the field's heavy-tailed scale; at
a margin of 0.01 they do not matter. Per fold, the field's worst transfer is to the
2 s starting-TTC level held out (wRMSE 0.469), where the thresholds fitted on the
milder levels sit above the most critical cells' deficits and predict low intervention
where the data are at 0.67 to 0.94. That is the extrapolation a grouped fold is meant
to test, and the gap threshold transfers to the same fold at 0.155.

One model-free number settles that this is not a fitting question: on the 288 decisive
cells the field covariate's rank correlation with the cell response is +0.14, against
the gap's +0.86 and TTC's +0.81. No threshold model can order cells that the covariate
does not order.

## 3 Where the loss comes from: two separable mechanisms

The field covariate on these cells is, to a good approximation,

> deficit = gate(lateral state) × magnitude(longitudinal counterfactual) + jitter floor

with the gate the lane-entry weight and the magnitude the residual relative speed in the
released model's counterfactual "lead brakes at 6 m/s² to a stop; I react after 1 s and
brake at 8 m/s²". The two can be separated.

### 3.1 The lane-entry gate, about 44% of the loss

With the gate forced to 1 from the first post-onset frame, the field's held-out wRMSE
falls from 0.352 to 0.265 (0.273 with the ego speed smoothed), and its model-free rank
correlation with the response rises from +0.14 to +0.45. That recovers +0.087 of the
+0.199 deficit against the gap threshold.

The mechanism is visible in single cells. At starting TTC 2 s, clip point 5, delta
velocity 21 km/h, participants intervene at 0.85, 0.92 and 0.92 for the 2, 3 and 4 s
lane-change durations; the field gives 10 005, 4 205 and 171. The lane-entry weight is
the lateral overlap *predicted at the moment of longitudinal closure*, projected at the
current lateral closing rate over the longitudinal TTC. With the gap closing in under a
second and the target moving laterally at the pace of a 4 s lane change, the projection
says the target will not have entered the lane by the time the gap closes, so the
conflict geometry barely applies. Sixty-four of the 288 cells have a gate below 0.9 at
the shown-window end, all of them at starting TTC 2 s (3 and 4 s lane changes) and 3 s
(4 s lane changes), and their mean response is 0.75 against 0.51 elsewhere: the gate
acts precisely where participants respond most. This is also why the registered field
is non-monotone in starting TTC (median deficit 3 208 at 2 s against 7 179 at 3 s)
while the response is monotone.

The study's own context file records that lane-change duration is confounded with
lateral position at clip end. The data say participants do not use it: at matched
starting TTC, clip point and delta velocity the response is flat across duration. The
field's gate says the opposite, because it is a collision-geometry criterion, and a
collision genuinely does depend on where the target will be when the gap closes. The
way I read it, participants respond to *encroachment having begun*, not to the
projected overlap at closure.

### 3.2 The counterfactual magnitude, about 56% of the loss

The gate-free field still loses to the gap threshold by 0.113 and to TTC, and it orders
only a minority of matched-TTC rows in the observed direction (mean rank correlation
−0.28 against the gap's −0.73). The registered report's sign derivation already
attributes this to the counterfactual-residual term; the sensitivities make the
mechanism explicit. At the study's cells the magnitude moves by about a third of a
metre per second per metre of gap, and by one and a half to two metres per second per
metre per second of *either vehicle's speed*. The reason is the counterfactual itself:
the available distance is the gap plus the lead's stopping distance from its current
speed minus the ego's reaction distance, and in this regime (ego at 110 to 130 km/h,
gaps 4 to 80 m) the counterfactual is violated in nearly every cell, so the term
measures how bad the worst case would be, which the absolute speeds set far more than
the current gap does.

The study then realizes its delta-velocity levels partly through the ego speed (30.7
m/s in the 21 km/h clips, 36.5 m/s in the 42 km/h clips, the target at 25.0 m/s in
both). At matched TTC 0.8 s the 42 km/h cell, with the larger gap, scores 30.7 against
the 21 km/h cell's 23.1; holding both speeds fixed, the larger gap alone would give
21.5, the direction the data take. So within a matched-TTC row the field ranks cells by
how fast the vehicles are going, and participants rank them by how far apart they are.

### 3.3 What this does and does not change about "kinematic content ruled out"

Nothing in the verdict changes. Both mechanisms are properties of the field as
specified, not of the code: the gate computes what it was designed to compute, and the
magnitude is the released term made continuous. What the decomposition adds is scope.
The gate is a project construction, so its share of the loss is a verdict on our
2026-08-27 lane-entry note rather than on the published model; the magnitude's share
is a verdict on the published safety term's counterfactual as a comfort criterion. I
have not run the released binary gate on this study, but its geometry (a target is "in
lane" only within 1.15 vehicle widths) would, as far as I can see, suppress the same
slow-lane-change cells at least as hard; a cheap check if anyone wants the sentence in
a paper to say "released gate" rather than "our gate".

## 4 Smaller findings

- **Optimizer sensitivity.** Re-running the registered fit on the same cells in a
  different row order moves the field's wRMSE by up to 0.005 (0.3471 to 0.3516), which
  is the multi-start L-BFGS-B landing in different local optima of a flat objective. It
  is irrelevant at the margin, but it means the registered numbers are not bit-for-bit
  reproducible under permutation. A denser start grid or the closed-form-lapse grid
  would make them so; not worth changing a registered script for.
- **Trace versus annotation.** The registered report's maximum TTC discrepancy of 1.9 s
  sits entirely in the 7 km/h clips, where a closing speed of 1.9 m/s turns
  centimetre-per-second differences into seconds of TTC (median discrepancy 1.2 s at
  7 km/h, 0.07 s at 42 km/h). The gap discrepancy is a near-constant 0.7 to 1.9 m
  offset from where the gap is measured. Since the design scalars enter at their
  annotated values and the field at the trace's, and the participants saw the rendered
  trace, any such discrepancy handicaps the design scalars, not the field.
- **The noise floor** is computed from participants per cell, while block-1 videos are
  seen twice by the same participant; the floor is therefore slightly conservative
  (higher than the true sampling noise). The gap threshold's 0.152 against a floor of
  0.118 is, if anything, closer to the floor than stated.
- **A sign slip in the record's gloss of the within-row counts.** The registered
  report's section 5 states, correctly, that the smoothed field's rank correlation with
  the response is *negative* in 14 of 24 matched-TTC rows. The gate record, the scope
  map and the handover gloss this as "orders 14 of 24 rows in the observed direction".
  For a criticality measure the observed direction is *positive* (more deficit, more
  intervention; the gap's direction is negative because it is a distance), so the
  field orders 10 of 24 rows like the data and is anti-ordered in 14. The slip is in
  the wording, not the numbers, and it understates the field's failure; corrected in
  place with a dated note in the gate record and in the 60-minute talk's build script
  (the built 60-minute deck is not regenerated, per query TALK.Q2, so its slide 36
  still carries the old wording until Jonas rebuilds or edits it). Removing the gate makes the within-row ordering worse still (6 to 7 of 24),
  because the gate's suppression of slow-lane-change cells happened to work against the
  magnitude's speed ordering in some rows; the row statistic is the wrong place to read
  the gate's effect, the held-out score is.

## 5 What it means for the surprise-without-the-field question

Jonas's open question at R2.Q5 is whether the surprise elements can stand on their own
as a scenario-agnostic metric with the preference field dropped, and the scope map
names the crux: every surprise measure needs a reference distribution, and the field
was ours. This review gives that exploration two empirical constraints, stated as
constraints on any candidate reference rather than as findings about surprise:

1. **It must engage at encroachment onset, independent of the lateral pace.** The
   participants' response is flat across lane-change duration at matched time since
   onset, TTC and delta velocity. A reference that predicts the target's lateral
   trajectory and asks "will it be in my lane when the gap closes" is the thing that
   failed in section 3.1.
2. **Within matched TTC it must order by gap, not by absolute speed.** A reference built
   on a worst-case stopping counterfactual inherits the speed dependence of section
   3.2. The comfort response looks, on this data, like a distance judgment at a given
   closing rate.

Stated as an opinion: what failed is a *worst-case counterfactual* reference, which may
well be the right reference for a collision-avoidance model, since a collision does
depend on where the target will be and how fast everyone is going, and the wrong one
for a comfort measure, which the data suggest is triggered earlier and by simpler
scene quantities. That is consistent with the project's standing reading that comfort
and dread are different level sets, and it suggests the two need different references,
not one field read at two levels.

## 6 What was done, and what is recommended

- The decomposition is committed as `replication/czb/cutin2_lane_gate_diagnostic.py`
  with its tracked report; a dated note in `docs/r2_gate_decisions.md` §1 points to it.
- No change to the registered script, its report, or the verdict.
- Optional, cheap: the released binary gate on the same cells (section 3.3), if a
  manuscript needs to attribute the gate's share to the published model rather than to
  our continuous form.
- The R2.Q5 note should start from the two constraints in section 5.

## 7 Where I may be wrong

- The "44% / 56%" split is one decomposition of a non-additive quantity (the gate
  multiplies the magnitude), read off the held-out score; another order of removal
  would give different shares. The qualitative reading, that both mechanisms matter and
  that the gate acts on the most-responded cells, does not depend on it.
- The sensitivities are finite differences at four cells; the counterfactual is
  piecewise and the numbers would differ at cells where it is not violated (the 7 s
  starting-TTC clips, where the gate-free magnitude is near zero).
- I read the participants' flatness across lane-change duration as "they do not use
  it"; the study's context file notes duration is a between-subjects factor, so that
  flatness is a between-groups comparison and carries the usual caveat.
- The trace-versus-annotation argument assumes participants saw video rendered from
  the deposited traces; I have not verified the rendering pipeline.
