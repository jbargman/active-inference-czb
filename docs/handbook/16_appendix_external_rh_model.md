# Chapter 16 (appendix): an external comfort-zone model built on required deceleration

*Part of the WaymoActiveInference handbook. Added 2026-09-02 ({{R6}} round). **Early work,
and external to this project.** A colleague's working document proposes a comfort-zone
boundary defined through the driver's habitual control capability, with the required
deceleration as its cut-in cue; a separate LLM-assisted analysis, commissioned by Jonas
and kept in its own repository, implemented that model and fitted it to the same second
cut-in study this project used at gate R.2. This appendix reads that work in the context
of ours: where the two agree, where they disagree, and what each can learn from the
other. It is not a replication (the external results were not re-run here), and it is
not part of this project's evidence chain. The external material lives outside this
repository, reached through the shortcut in `OthersWork/`; that folder is deliberately
not part of the standing context for sessions on this project (see `handover.md` §5),
and nothing in the project's cards, gate records or claims depends on it.*

{{R6}}**Sources.** The colleague's document, "Operationalization of a Summala-like comfort zone
boundary" (working document, 2026, unpublished; with a companion HTML simulator), and the
analysis note "The habitual-control resolvability model of the comfort zone boundary:
method description, assessment, and a first fit to the cut-in video study" (prepared for
Jonas by Claude Fable 5.1, 2026-09-01, revised 09-02), with its scripts and tracked outputs.
Numbers quoted from the external analysis are quoted as that note reports them; numbers
from this project name their tracked output. One number was computed for this appendix
(section 16.5) and has its own script.

## 16.1 What the external model proposes

{{R6}}The document starts from five phenomena a comfort-zone account must explain (a margin from
danger without extra motives; a graded discomfort signal rising sharply in a narrow region;
context- and driver-dependence; anticipation, including with no kinematic change; the same
signal in passengers) and defines the boundary through *habitual-control resolvability*: the
probability that at least one action from the driver's habitual repertoire keeps the
situation acceptable. For a cut-in the dominant control is braking, and the quantity
becomes

> R_h = P(a_req ≤ a_h),   a_req = Δv² / (2 d),   d = g₀ − g_min − Δv τ,

with a_h the habitual deceleration limit, g_min a minimum acceptable gap, τ a response
delay, and log a_req taken as Gaussian with spread σ, so that R_h = Φ((log a_h − u(x))/σ)
and the boundary is the locus R_h = θ, which inverts to a closed-form boundary gap
g_CZB(Δv). A lateral extension gates this by w, the probability that the intruder comes
within a minimum lateral clearance over a look-ahead horizon, as a mixture
R_h = (1 − w) + w Φ(·): before the vehicle "binds", resolvability has a floor at 1 − w and
the gap does not matter.

{{R6}}Read against this handbook's vocabulary, this is a **demand-based** criticality axis
(chapter 11): the same family as the released model's safety term, which asks whether
ordinary braking would still suffice if the lead did its worst, and as the required
deceleration this project scored as a comparator at gate R.2. Its distinctive additions are
the two margins (g_min and τ), the explicit habitual limit, and a psychometric reading of
the boundary as the θ-quantile of a cumulative normal on a log stimulus.

## 16.2 What the external analysis found

{{R6}}The external analysis fitted the model to the second cut-in study (144 participants,
CP2–CP5 cells for the fits, CP1 held aside), trial-level maximum likelihood with lapse
terms, and compared it held out against single-cue probits under two fold schemes, one of
them the leave-one-starting-TTC-out scheme this project registered so that scores would be
comparable. Its findings, as it states them:

- {{R6}}**The full model ties a gap threshold held out and does not beat it** (leave-one-TTC-out
  0.149 against 0.147; leave-one-Δv-out 0.149 against 0.152, weighted RMSE on cell means).
  Under its own pre-stated rule the kinematic content is not credited.
- {{R6}}**Without margins the cue is worse than chance** (DRAC alone 0.299 against chance 0.283);
  the minimum gap does almost all the work, fitting at g_min ≈ 11.5 m, and τ adds nothing
  once g_min is free. The fitted σ is 1.09 log units, wide enough to flatten the kinematic
  shape into a soft shoulder above a hard wall.
- {{R6}}**The lateral gate makes a correct out-of-sample prediction.** The 90 pre-encroachment
  (CP1) cells are flat, as the mixture form predicts and the ungated form does not; with one
  per-driver parameter they are predicted to a weighted RMSE of 0.028 with no CP1 trial in
  the fit. Replacing the mixture by an additive lateral term is worse and loses the floor.
- {{R6}}**A nested test rejects the braking equation's exponent on this paradigm.** Freeing the
  exponent on Δv (the mechanism's value is 2) fits 0.39, bootstrap 0.23 to 0.56, with 2 and
  also 1 (the TTC weighting) excluded in every resample. With that exponent the rest of the
  model behaves as the document says it should (margins ≈ 2 m and 0.4 s, no lapse floor,
  CP1 predicted from the population fit, held out 0.104). The note presents this as a
  diagnosis, not a repaired model, because Δv^0.39/(2d) is not a deceleration.
- {{R6}}**One per-driver parameter is reliable** (split-half r = 0.88 across the two showings of
  each clip), but it is a response criterion confounded with θ, not a capability: a tenth
  of participants have a fitted "habitual limit" above 8 m/s².

## 16.3 Where the two lines of work agree

{{R6}}Two pipelines, built independently on the same data, with different fitters (cell-level
weighted least squares here; trial-level maximum likelihood there), different model
families, and different authors, land on the same three conclusions.

{{R6}}**Gap first, speed a modest second.** This project's registered comparison
(`replication/czb/out/cutin2_field_vs_gap.md`) scored the log-gap threshold at 0.152,
TTC at 0.168 and required deceleration at 0.289; the external ladder scores its gap probit
at 0.147, TTC at 0.201 and DRAC at 0.299. Both then find that the best description is gap
with a weak dependence on closing speed: card EL.1 (`out/cutin2_two_axis.md`) finds an
equally weighted linear rule in log gap and log TTC at 0.114, which is a threshold on
gap/√Δv; the external unconstrained probit finds an effective cue of gap/Δv^0.42 at 0.111,
and its free-exponent test puts the Δv exponent at 0.39. The exponent on speed that the
video responses carry is about 0.4 to 0.5, against 1 for TTC and 2 for any deceleration
measure. That two groups reached this number by different routes is, the way I read it,
the most useful thing in this appendix.

{{R6}}**Physics-first cues fail for the same reason.** The pipeline review of gate R.2
(`docs/r2_pipeline_review.md`) found the released preference field's counterfactual
magnitude four to six times more sensitive to either vehicle's speed than to the gap, so
it orders matched-TTC cells by absolute speed where participants order them by distance.
The external note finds the same for a_req: the Δv² numerator puts far too much weight on
closing speed, and the fit compensates by widening σ and leaning on the wall at g_min. The
released safety term and the colleague's a_req are the same kind of object, and the data
reject both in the same direction.

{{R6}}**A per-driver level is the reliable object.** The external per-driver shift has split-half
reliability 0.88 within the cut-in; this project's per-scenario split-half reliabilities
are 0.93 to 0.98 and the per-driver level is about 69% shared across four scenarios
(`out/cross_scenario_consistency.md`). Both analyses conclude that the elicited quantity
is a criterion, not a capability: the external note says its a_h absorbs θ; this project's
level c_i is defined as a criterion from the start.

## 16.4 Where they differ, and what each can take from the other

{{R6}}**The anticipatory gate: theirs helps, ours hurt.** Both constructions gate the
longitudinal cue by a predicted lateral encroachment. The external gate projects the
clearance forward over a fixed horizon (3 s, fixed as unidentifiable) and, after onset, is
already 0.66 to 1.00 in every design cell, so it switches the cue on early and stays on;
its one clear success is the flat CP1 floor. This project's lane-entry weight
(`docs/lane_entry_note.md`) projects the overlap to the moment of longitudinal closure,
which depends on TTC; on slow lane changes at short starting TTC it suppresses the deficit
in cells whose mean response is 0.75, and the pipeline review attributes about 44% of the
field's loss to that gate. The lesson runs one way: an encroachment gate should anticipate
on a fixed horizon, not on the closure time. It would be a small change to the lane-entry
weight, and it is recorded as a query rather than made, because nothing in the comparator
program now depends on the field.

{{R6}}**The margin: a wall or a slope.** The external model's best-determined quantity is a hard
minimum gap (g_min ≈ 11.5 m, bootstrap 10.6 to 12.7), below which no habitual braking
suffices; this project's best form is a smooth threshold on gap/√Δv with no wall. Section
16.5 puts the walled cue on this project's registered pipeline so that the two forms meet
on identical folds.

{{R6}}**Within- versus between-driver spread.** The external note splits its population σ into a
within-driver 0.80 and a between-driver 1.16 (log units on log a_h) and warns that the
boundary is a different quantile under each reading. This project's stage-1 estimator
separates the same two things by construction (a per-trial lapse and probit spread
against a hierarchical per-driver level with σ_pop 0.200 on the log level scale,
`out/stage1_summary.md`), and the ellipse note's population-A/population-B distinction
(`docs/czb_ellipse_design_note.md` §1) is the same warning in this project's terms. The
two parametrizations are not numerically comparable and should not be quoted against each
other.

{{R6}}**Scope.** The external work is one scenario, one study, and one response (the binary
intervention, with perceived safety and expected braking as correlates). It makes no
cross-scenario claim and does not test transfer; the scenario-agnostic ambition of its
definition (a different dominant control per scenario class) is stated, not tested. This
project's surviving claim is cross-scenario and field-free; its cut-in cue is now the
linear rule of EL.1. Neither line of work has naturalistic data, and both say so.

{{R6}}**Independence.** The external analysis chose one of its fold schemes to match this
project's registered one and cites this project's R.2 output; the two are therefore not
blind to each other on the fold design, though they are on the models and fitters. The
agreement in section 16.3 should be read with that in mind.

## 16.5 One cross-check on this project's pipeline

{{R6}}To meet the walled cue on identical ground, `replication/czb/cutin2_external_cue.py`
(pre-stated rule in its docstring) fits log a_req with g_min free inside each training
fold, and with g_min and τ free, on the registered R.2 cells, fitter and
leave-one-starting-TTC-out folds, against the registered log-gap threshold and the EL.1
linear rule. Result (`out/cutin2_external_cue.md`):

{{R6}}Held-out wRMSE: log gap 0.152; the EL.1 linear rule 0.114; log a_req with g_min free 0.171; with g_min and τ free 0.195. The fitted wall is 9.0 to 10.1 m across the six training folds. linear minus best walled = -0.0573: **the linear rule in log gap and log TTC STANDS as the better cue on this pipeline**. On this pipeline the smooth two-axis rule is clearly the better description; the external fit's tie with a gap threshold used a trial-level likelihood and lapse terms, so the two pipelines' numbers for the walled cue are not directly comparable, but the ordering against the gap threshold is the same in both. The decision it feeds is which functional form card EL.2 carries for the cut-in (query EXT.Q1).

## 16.6 What this appendix does not do

{{R6}}It does not re-run the external analysis, check its code, or verify its references (the
note itself marks them as from memory and unverified). It does not adopt any external
number into this project's claims. And it does not settle the exponent question: both
analyses are on frozen video with no self-motion, and both say that whether drivers in a
moving vehicle weight closing speed as a deceleration cue implies is a question for a
different paradigm. The colleague's document and the external note remain the sources for
anything said about the external model; this appendix is a reading of them, dated, and
marked as early.
