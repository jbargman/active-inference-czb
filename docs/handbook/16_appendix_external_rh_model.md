# Chapter 16 (appendix): an external comfort-zone model built on required deceleration

*Part of the WaymoActiveInference handbook. Added 2026-09-02 ({{R6}} round), restructured the
same day after Jonas asked for a plainer statement of what each approach is better at.
**Early work, and external to this project.** A colleague's working document proposes a
comfort-zone boundary defined through the driver's habitual control capability, with the
required deceleration as its cut-in cue; a separate LLM-assisted analysis, commissioned by
Jonas and kept in its own repository, implemented that model and fitted it to the same second
cut-in study this project used at gate R.2. This appendix compares that work with ours. It
is not a replication (the external results were not re-run here) and it is not part of this
project's evidence chain. The external material lives outside this repository, reached
through the shortcut in `OthersWork/`; that folder is deliberately not part of the standing
context for sessions on this project (`handover.md` §5), and nothing in the project's cards,
gate records or claims depends on it. Where this appendix quotes an external number it says
so; every number of ours names its tracked output.*

## 16.1 The two approaches in one paragraph each

{{R6}}**Theirs.** The boundary is where the driver can no longer resolve the situation with
routine control. For a cut-in the routine control is braking, so the cue is the required
deceleration a_req = Δv² / 2(g₀ − g_min − Δv τ), with a minimum acceptable gap g_min and a
response delay τ as the driver's margins and a habitual limit a_h as the driver's capability;
the boundary is the θ-quantile of a cumulative normal on log a_req. A lateral gate w, the
probability that the intruder will come within a minimum clearance over a fixed 3 s
look-ahead, multiplies the whole thing: before the intruder "binds", the gap does not
matter. Fitted to the second cut-in study (trial-level maximum likelihood, lapse terms, two
held-out fold schemes) by the external analysis.

{{R6}}**Ours, as it stands after 2026-09-02.** The boundary is a per-driver threshold (a level)
on one criticality axis, applied when a gate says the situation counts. On the cut-in the
axis is the optical expansion rate of the other vehicle, θ̇ ≈ W Δv / g² (card EL.1 found the
equal-weighted log gap and log TTC rule; card EL.1b confirmed it is θ̇ fitted directly,
`replication/czb/out/cutin2_looming.md`); the gate is the same fixed-horizon clearance
projection as theirs, credited on our pipeline (card G.1, `out/cutin2_gate.md`); the level is
the hierarchical per-driver quantity of the stage-1 estimator, shared across scenarios
(`out/cross_scenario_consistency.md`). This replaced the active-inference preference field,
which lost at gate R.2. Fitted with cell-level weighted least squares on the same study,
leave-one-starting-TTC-out folds, rules committed before each run.

## 16.2 What each is better at

{{R6}}The table is the appendix. Numbers are held-out weighted RMSE on the 288 post-onset cells
unless stated; lower is better; the measured sampling-noise floor is 0.118. "Ours" and
"theirs" use different fitters (cell-level least squares against trial-level likelihood),
so numbers compare across pipelines only in their ordering; within each column they are
exact.

| question | ours | theirs | who is better, and why |
|---|---|---|---|
| Describing where the cut-in boundary is | θ̇ threshold **0.113**; gated **0.103** (3 and 6 parameters) | full model **0.149** (8 parameters), a tie with a gap threshold (0.147) | **Ours.** At the noise floor with fewer parameters; their model as written does not beat gap alone. On our pipeline their walled a_req scores 0.171 (`out/cutin2_external_cue.md`) |
| Knowing when the situation starts to count (the gate) | not part of our model until 2026-09-02; our field's closure-time gate *hurt* (about 44% of the field's loss) | fixed-horizon gate predicts the pre-onset cells out of sample (0.03) | **Theirs first.** We imported the idea and it passed the same test on our rule (G.1: pre-onset cells 0.032 out of sample, and the post-onset fit improves) |
| Evidence across scenarios | four scenarios; one per-driver level shared at 69% of the reliability ceiling; transfer tests; left-turn and ellipse constructions | one scenario, one study; scenario-agnostic ambition stated, not tested | **Ours.** Theirs has no cross-scenario claim yet |
| A per-driver measurement | per-scenario split-half reliability 0.93–0.98 | one per-driver parameter, split-half 0.88 | **Equal.** Different designs; both find the per-driver criterion to be the reliable object |
| A mechanism behind the cue | none claimed: a psychometric threshold on a perceptual variable | required deceleration with named margins, a closed-form boundary | **Theirs as a story, but its equation fails.** Their own nested test rejects the Δv² exponent (fitted 0.39, bootstrap 0.23–0.56) on this paradigm |
| The speed dependence | θ̇ ∝ Δv / g², so gap ∝ √Δv | free exponent on Δv: 0.39; unconstrained probit: gap / Δv^0.42 | **Equal, and the same number.** Two pipelines find a speed exponent of about 0.4–0.5 against 1 for TTC and 2 for any deceleration cue |
| Physics-first cues | the field's counterfactual: 4–6× too sensitive to speed (pipeline review) | a_req with no margins: worse than chance; margins carry the fit | **Both fail in the same direction** |
| Real driving | nothing; frozen video only | nothing; frozen video only | **Neither.** Both say so |

## 16.3 The one thing the comparison settled

{{R6}}Their speed exponent of about 0.4 had no mechanism (their note's open blocker asked
what the cue could be, and offered a perceptual compression of closing speed as one reading).
Our EL.1 rule supplies it without any compression: a threshold on the optical expansion rate
implies gap ∝ √Δv exactly, because θ̇ ≈ W Δv / g². Their gap / Δv^0.42 and our gap / Δv^0.5
are the same cue seen from two sides, and it is the classic looming variable of the visual
control literature (and the quantity the active-inference model's own perception stage
computes). One contrast with that literature is worth stating: in a driving simulator, Xue
et al. (2018) found inverse tau (θ̇ / θ = 1 / TTC) the better cue for brake onset; on this
video paradigm the order reverses (θ̇ 0.113 against 1/TTC 0.168). Whether that is the
paradigm or the task is the question naturalistic onsets would settle.

## 16.4 Where they differ, in more detail

{{R6}}**The margin: a wall or a slope.** Their best-determined quantity is a hard minimum gap
(g_min ≈ 11.5 m, bootstrap 10.6 to 12.7), below which no habitual braking suffices; ours is a
smooth threshold with no wall. Put on our registered pipeline with the wall fitted inside
each fold, their cue scores 0.171 against our rule's 0.114 (`out/cutin2_external_cue.md`,
walls 9–12 m), so the wall does not substitute for the second axis on this data.

{{R6}}**The gate, and what we changed.** Both constructions gate the longitudinal cue by a
predicted lateral encroachment. Theirs projects the clearance forward over a fixed horizon;
ours projected the overlap to the moment of longitudinal closure, which depends on TTC and
suppressed the field exactly where participants respond most. Card F.1
(`out/cutin2_field_horizon_gate.md`) put the fixed horizon into the field's own gate: the
field improves from 0.347 to 0.261, the first field variant to beat chance, which confirms
the attribution; it stays far behind the gap (0.152), so the field is still ruled against.
Card G.1 put the same gate in front of our rule, where it belongs: the pre-onset cells are
predicted out of sample (0.032) and the post-onset fit improves (0.103). The fitted gate is
softer than theirs (s_l ≈ 1.0 m against ≈ 0.3 m); both analyses agree that the design
samples only "closed" and "open", so the gate's shape is unidentified either way.

{{R6}}**Within- versus between-driver spread.** Their population σ splits into a within-driver
0.80 and a between-driver 1.16 (log units on log a_h), with the warning that the boundary is
a different quantile under each reading. Our stage-1 estimator separates the same two things
by construction (a per-trial lapse and probit spread against a hierarchical per-driver level),
and the ellipse note's population-A / population-B distinction is the same warning in our
terms. The parametrizations are not numerically comparable.

{{R6}}**Independence.** The external analysis chose one of its fold schemes to match our
registered one and cites our R.2 output, so the two are not blind on the fold design; they
are on the models and the fitters. The convergence in 16.3 should be read with that in mind.

## 16.5 What this appendix does not do

{{R6}}It does not re-run the external analysis, check its code, or verify its references (the
external note marks them as from memory). It does not adopt any external number into this
project's claims; the two ideas we took from it, the fixed-horizon gate and the reading of
the speed exponent, each passed a pre-stated test on our own pipeline before entering the
model. And it does not settle the exponent question for real driving: both analyses are on
frozen video with no self-motion, and both say so. The colleague's document and the external
note remain the sources for anything said about the external model; this appendix is a
reading of them, dated, and marked as early.
