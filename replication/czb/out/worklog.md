# CZB work-order log

One paragraph per completed card, appended in order, per the session pattern in
`docs/czb_work_orders.md` §4. Each entry states the card, what was produced, whether the
acceptance criteria were met, and anything a successor should know.

## 2026-08-27 — Card S.1: draft the `perform-research` skill

Drafted `C:/Users/bargman/.claude/skills/perform-research/SKILL.md` (210 lines, within
the card's ~300-line limit). Contents follow the card's five required areas —
reproducibility, verification, documentation, the between-model handover protocol, and
statistical practice — each written as rules already in force in this repository rather
than as new proposals, with the 2026-08-26 paired-difference overstatement used as the
worked cautionary tale for the "no in-session-only numbers" rule. The research step
covered Anthropic's skill-authoring guidance (fetched and verified: frontmatter limits,
sub-500-line body, one-level-deep references, matching freedom to task fragility, no
time-sensitive content), Sandve et al. (2013) *Ten Simple Rules for Reproducible
Computational Research* (fetched and verified; rules 1, 2, 4, 6, 7 and 9 are the ones
borrowed), the published `softaworks/agent-toolkit` session-handoff skill (verified
structure — its section set and its no-unresolved-placeholders validation rule are
borrowed), and LangChain's handoff documentation, a context-rot discussion and the
Center for Open Science preregistration pages (read via search summaries only, and
marked unverified in the draft accordingly). Frontmatter validated against the
documented constraints: name 16 characters, lowercase and hyphens, no reserved words;
description 737 characters, third person, states both what the skill covers and when to
use it. Acceptance criteria met: the file exists, is under the line limit, cites its
sources, and ends with an explicit "for Jonas's review" note. The card's stop condition
was exercised rather than guessed around — seven items where I could not tell whether a
practice is project law or one session's habit are listed as open questions in the
draft's §7 (scope, name form, one-card-per-session strictness, whether an executing
session may ever write interpretation, whether two-route verification is a hard
requirement, whether full-suite testing stays non-negotiable as suites grow, and whether
the skill should ship a session-start script). **Note for Jonas:** placing the file
under `~/.claude/skills/` makes it discoverable to sessions immediately, so the body's
first line marks it as an unapproved draft; if you want it genuinely inert until you
have read it, move the directory aside and restore it after review. No repository code
was touched; the full test suite (123 tests across four files) passed before and after.

## 2026-08-27 — Card S.1 (revision v2): the skill reworked after Jonas's comments

Jonas read v1 and made one structural objection and several additions. The objection:
the escalation conditions were too strict for how he actually works — he often queues a
batch of tasks and is unavailable (overnight), and a session that stops to ask wastes
the batch. The skill was rebuilt around that. Renamed to `performing-research`
(Anthropic's gerund convention, which he approved), so the old `perform-research`
directory was removed. New §1 states the interruption budget explicitly — his time is
the scarce resource, and the resolution is *flag and continue, do not stop and ask*.
New §2 defines interactive versus batch mode: in batch mode nothing blocks the queue,
with a single carve-out for actions that cannot be undone and were never authorized
(sending mail, publishing, deleting others' work, spending money, using credentials) —
those are skipped and tagged, not performed, and the queue still moves. New §3 defines
the flagging convention he asked for: `@REVIEW` (a more capable model should assess) and
`@JONAS` (only he can settle it), each with severity `(blocker|judgment|minor)`, both
greppable, both required in the per-item worklog entry *and* the end-of-session summary,
with the rule that a tag never substitutes for making the best defensible choice. §4 is
the session checklist he suggested trying. §5 is his new rule that every parameter value
carries a motivation, with weak motivations tagged `@JONAS` (this coincides with the
no-voodoo-constants guidance in Anthropic's skill docs, cited). §6 is his other addition:
when a core component comes from a paper, propose replicating a published result to
verify the implementation — grounded in what that practice already caught here (OSF
deposit agreement at 0.0 s median onset error; the paper's worked example not matching
its own deposit; thirteen code-versus-SI differences). §10 answers his question about
model tiers: the ranking was taken from the bundled `claude-api` skill rather than from
memory — tier 1 Fable 5 / Mythos 5, tier 2 Opus 5, tier 3 Sonnet 5, tier 4 Haiku 4.5 —
with the operational consequence that a tier-1 session has nobody above it, so it must
resolve rather than defer and must self-review its own quoted numbers. His other answers
are folded in: scope is all research tasks, the handover chain applies within a
repository or chat, smaller items may share a session, two-route verification is not
mandatory. Two of his answers asked what the implications were rather than settling the
question, so §14 carries proposals instead of rules: (a) an executing session **may**
write interpretation but tags it `@REVIEW(judgment)` as unreviewed — refusing outright
would gut batch mode — with the stricter "no verdict prose" kept only for designated
verdict cards; (b) full test suite at session start and before every commit, targeted
subset between items inside a batch, so nothing broken is ever committed while per-item
cost stays low. File is 292 lines, within the card's limit; frontmatter validated
(name 19 characters, description 817 of 1024). @JONAS(judgment): the skill is still a
draft and still lives outside version control — its revisions are not tracked the way
the handbook's rounds are; a canonical copy in a repository is offered in §14. Full
suite (123 tests) green before and after; no repository code touched.

## 2026-08-27 — Card S.1 (v3): skill approved and made active

Jonas approved the skill and the batch-mode carve-out as written, and added one general
rule: APA style for all citations and reference lists unless he says otherwise. That is
now §9 of the skill, and §13 was rewritten as a proper APA reference list with the
in-text citations converted to author-date form; the verification status of each source
is kept as a note beneath it, since the provenance rule requires distinguishing what was
fetched in full from what was read only as a search summary. The DRAFT banner is
replaced by an active status line. He also asked for the skill to be tracked, so it is
now mirrored at `docs/skills/performing-research.SKILL.md`, byte-identical and verified
by `diff`, with `docs/skills/README.md` recording that the live user-level copy stays
authoritative, that the mirror must be updated in the same commit, and why the mirror is
deliberately not laid out as `.claude/skills/` (a second active copy would compete with
the live one). He will say when he edits the live copy. No tags outstanding from this
revision; the skill is 318 lines, still within the card's limit. No repository code
touched.

## 2026-08-27 — Card A.1: synthetic-recovery harness

Built `replication/czb/fit_recovery.py`; results in `out/recovery_summary.md`, run log in
`out/log_recovery.txt`. Criteria 2 (shrinkage beats unshrunk per-driver MLEs on RMSE, on
both axes) and 3 (runtime, 6.1 min against a 10-minute limit) **pass**. Criterion 1
**fails as recorded**, and was not loosened: over 20 simulated datasets the population
median and between-driver sd are recovered within 2 Laplace SEs on 18/20 and 18/20 for
`deficit_max`, the primary axis, and on only 8/20 and 4/20 for `a_req_max`.

Two findings, both load-carrying. **First, the estimation method in the plan is wrong as
written.** "MAP plus Laplace" implemented literally — maximizing the joint posterior over
hyperparameters and driver effects together — recovers the median and the lapse but
inflates the between-driver sd by a factor of about 2.6 (1.289 against a truth of 0.500)
with coverage 0/20, because the joint mode of a hierarchical posterior is not its
marginal mode; sigma_pop and the driver effects trade along a funnel. Integrating the
driver effects out by Gauss-Hermite quadrature, one dimension per driver, and applying
Laplace only to the four hyperparameters gives bias −0.021 and coverage 18/20. Since the
deliverable is a population percentile and a percentile is made of the spread, the
literal reading would have produced a materially wrong headline. Both estimators are kept
in the script and both are reported, because the size of the bias is the result.
`docs/czb_fitting_plan.md` §3 now carries a dated correction pointing at the evidence.
@REVIEW(judgment): changing the estimator prescribed by a planning document is a
methodological decision, not an implementation detail, and should be confirmed.

**Second, `a_req_max` cannot support a threshold fit as currently constructed**, and the
reason is the covariate rather than the estimator: two pre-onset cells sit at exactly 0
while the other sixteen bunch into 8.48–11.65, so 73% of the covariate's range is an
empty gap in which driver thresholds are mutually indistinguishable (the deficit axis's
largest gap is 30%). The C1 anchor is separately compromised there — TTC8's pre-onset
cell reads 8.48, close to the most critical cells rather than to zero, which is the
lane-gate leak already recorded in `docs/czb_fitting_plan.md` §4.
@REVIEW(blocker): this does not block card A.2, which proceeds on the primary deficit
axis, but it does block the truck check in fitting-plan §4 — the check whose entire
purpose is to let the allowed-deceleration axis rescue the framing where the dread field
is silent. The fix is upstream, in the field construction, not in the fitting code.

Two smaller notes. The Gauss-Hermite node count was set by measurement, not convention:
`--check-quadrature` shows estimates still moving at 30 and 60 nodes and settling near
150, where 150 and 250 agree to 0.003 in the median and 0.0007 in the sd; the default is
150. And the between-driver sd used as the simulation truth (0.50) was calibrated so the
simulated spread of per-driver intervention rates matches the observed 0.235 — the sweep
is printed by `--calibrate` and quoted in the summary, so the choice is checkable.
Full suite (123 tests) green before and after.

## 2026-08-27 — Card A.2: stage-1 hierarchical fit

`replication/czb/fit_stage1.py`, summary in `out/stage1_summary.md`. All three acceptance
criteria pass: four fits converged with usable standard errors, the summary renders, and
LOPO separates the bias variants while being reported as weak rather than decisive.
Runtime 4.4 h, almost all of it the two-dimensional quadrature in the hierarchical-lapse
folds.

The headline: on the primary deficit axis the population median boundary level is 5 043
(group lapse) or 5 352 (hierarchical lapse), against the stage-0 pilot's 5 200 — the
hierarchical fit is the better of the two held out, by +0.6 log-likelihood units. The
80th-percentile level is 6 379 [6 128, 6 630], equivalent to a required deceleration of
about 11.0 m/s² and a steady-following time headway at 20 m/s of 0.27 s. The ordered
braking-expectation model puts the comfort level at 3 703 (a_req 8.81, THW 0.50 s) and
the dread level at 6 397 (a_req 11.02, THW 0.27 s), separated by 2 694 deficit units
(SE 70).

@A.2.Q1(judgment): the card specified 43 leave-one-participant-out folds; 15 evenly
spaced folds were used instead, identical across all four variants so the comparison
stays like-for-like. 43 folds was budgeted before the cost of the two-dimensional
quadrature was known — the full design would have run about twelve hours. This costs
precision in the held-out difference, not validity.
@A.2.Q2(blocker): the bias-variant choice is not cosmetic. Moving from a group-level to a
hierarchical lapse shrinks the between-driver spread from 0.341 to 0.209 — a 39%
reduction in exactly the quantity a percentile is made of — while the held-out likelihood
separates the two variants by only +0.6 units over 3 096 trials. The deliverable
therefore depends materially on a choice the data barely constrains. This is the A.2
review gate and it should not be settled by the executing session. The direction also
contradicts the leakage argument in `docs/czb_validation_roadmap.md` §5.1, which
anticipated a *wider* spread under shrinkage; the fitted per-driver lapse spread is large
(sd 2.76 on the logit scale), so the hierarchical lapse is absorbing variation the group
model attributed to the threshold.
@A.2.Q3(judgment): the pre-onset predictive under-shoots systematically and in a graded
way — observed 0.122/0.070/0.052 against predicted 0.017/0.024/0.041 for TTC4/6/8, so the
sign pattern runs opposite to criticality. Real pre-onset responses rise with the
criticality of a clip that has not yet begun to develop, which a lapse floor cannot
express and which points at anticipation from the repeated stimulus set. The card's stop
condition asks whether this holds under *both* bias variants; only the better-fitting
variant was checked, so that comparison is still owed.
@A.2.Q4(minor): the two-dimensional quadrature is stable to about 5% in the
between-driver spread across 32/48/72 nodes per dimension (0.199/0.209/0.198), not to the
third decimal the one-dimensional case reaches. Adequate for a model comparison, not for
a quoted spread.
@A.2.Q5(minor): the translation from deficit units to required deceleration interpolates
each clip's own mapping and takes the median across the three stimuli; it is an
approximation, and it returns nothing at the 95th percentile because that level exceeds
the range any Random stimulus reaches. The THW column inherits both caveats.

## 2026-08-27 — Card A.3: the accumulator layer

`replication/czb/fit_stage2.py`, summary in `out/stage2_summary.md`. Against the rule
fixed before fitting (held-out RMSE at most 0.11 closes the gap, above 0.13 is failure),
the accumulator reaches **0.236** leave-one-criticality-out — worse than the static
stage-1 threshold's 0.161 on identical folds. Recorded as **FAIL**, not loosened.

@A.3.Q1(blocker): the verdict should not be read as evidence against the framework,
because the accumulator is misspecified in a way I can name. Its *in-sample* RMSE, 0.182,
is worse than the stage-0 static two-parameter probit's 0.125 on the same cells — a model
that fits worse in sample than the simpler model it extends is broken, not refuted. The
cause: the clips begin 15.1 s before the lane change, and Wiener noise accumulates
through that empty window, whose running maximum alone has a standard deviation near 3.9,
comparable to the entire post-onset drift. The per-cell table shows the consequence
directly — the model predicts 0.19 at C1 for *all three* criticality levels, where the
observed rates are 0.12/0.07/0.05 — and the fitted lapse collapses toward zero to
compensate. The length of that pre-onset window is a property of stimulus presentation,
not of drivers. The remedies (a leaky accumulator, or beginning accumulation where there
is evidence) are model-design decisions, so they are referred rather than made.
@A.3.Q2(judgment): the card's own stop condition — a gain so large that the accumulator
degenerates to a deterministic threshold — did not fire: the drift-to-noise ratio is 8.7,
so noise still does real work. Latency sensitivity is mild and monotone (in-sample RMSE
0.172/0.182/0.191 at lambda = 0.15/0.25/0.35 s), with the threshold location absorbing
the shift as expected.

## 2026-08-27 — Card A.4: Button press times from the Random fit

`replication/czb/validate_button.py`, summary in `out/button_validation_summary.md`,
figure `figures/button_validation.png`. Every accumulator parameter carried over from the
Random design unchanged; the only free quantity is one paradigm shift, fitted twice.
Acceptance criterion **FAIL**: the worst checkpoint discrepancy is 0.297 against a
tolerance of 0.05.

@A.4.Q1(blocker): this card is contingent on A.3 and cannot be read on its own — it
inherits the misspecified accumulator, so the magnitude of the miss carries no
information about the paradigm.
@A.4.Q2(judgment): what does survive, because it does not depend on the flawed
magnitudes, is the *form* and *direction* of the paradigm effect. A shift acting on the
threshold fits better than one acting on the gain (RMSE 0.148 against 0.169), and its
sign is negative (−0.250) — a lower boundary in the button paradigm, meaning earlier
pressing. That is what the documented cross-paradigm excess says, and decision 3 of the
handbook chapter 11 list asked exactly this question. The magnitude should be refitted
once the accumulator is repaired.

## 2026-08-27 — Card R.1: the review gate, run at tier 1

Executed on the strongest available model per the card; there is nobody to defer to, so
every referred decision was decided here, with committed evidence. Full suite (123
tests) green before and after. Verification pass first: every headline number in the
three stage summaries traces to its committed script's tracked log (`log_stage1.txt`,
`log_stage2.txt`, `log_button.txt`); the percentile table was independently reproduced
by a second script (below) to the last digit. One cosmetic finding the executing
session did not report: the logged stage-1 run crashed at its final console print
(cp1252 versus "≥") *after* writing the summary — numbers unaffected; the print is now
encoding-safe.

**The A.2.Q2 decision: hierarchical lapse is the primary variant** (population median
5 352, between-driver σ 0.209; the group variant is kept as the upper sensitivity
bracket). Evidence in `bias_variant_diagnostics.md` (script
`bias_variant_diagnostics.py`, log `log_bias_variant.txt`), three questions with
readings stated before the numbers: (1) per-driver pre-onset heterogeneity is real —
sd of per-driver C1 rates 0.204 against a shared-rate binomial's 0.078, Monte Carlo
p < 0.0001 — so a single group-level lapse is misspecified as data description;
(2) the leakage signature is present — under the group variant fitted thresholds track
pre-onset behavior at Spearman −0.622, and dropping the C1 cells moves the group σ
0.341 → 0.281; (3) the no-C1 hierarchical refit (σ 0.104) is an identifiability
artifact, not an estimate — without pre-onset cells the per-driver lapse is unanchored.
The executing session's claim that the observed direction *contradicts* roadmap §5.1
was a misreading — §5.1 predicted the group model shows the wider σ under leakage,
which is exactly what happened; corrected in the work orders and resolved below.
Two caveats attached to the deliverable: fitted b_i and c_i correlate at −0.700 while
the model assumes independence (the trait-correlation conjecture of §5.1), so card
A.2.v2 fits a correlated-effects variant under a pre-stated escalation rule; and the
percentile is specification-sensitive (80th: 6 379 hier vs 6 717 group; 95th: 7 543 vs
8 832), so any quoted percentile names its variant.

**Two defects found in `fit_stage1.py`'s validation code** (the fits are unaffected):
the hierarchical LOPO integrated both random effects on the same quadrature nodes —
the diagonal of the 2D integral, asserting perfect rank correlation — so the stored
+0.6 (deficit) and +14.3 (a_req) separations are approximations; and the C1 predictive
used the hier variant's *median* lapse (0.017) where the population mean (0.107) is
required, which manufactured most of the reported pre-onset undershoot. Both fixed in
place; card A.2.v2 regenerates the stored summary. The proper C1 check under both
variants (the owed A.2.Q3 work) shows the population-level undershoot largely
disappears under the hierarchical variant, while the *gradient* misfit is real and
model-independent: observed C1 rates fall with TTC (0.122/0.070/0.052) where every
covariate-driven prediction rises — anticipation from the repeated stimulus set,
inexpressible by any lapse floor.

**The A.3.Q1 decision and the verdict: FAIL, final and quotable.** The chosen remedy
was accumulation gated at manoeuvre onset (observable — the stimulus's first lateral
motion; the pre-onset window is a presentation property), with the leaky accumulator
held in reserve as it would alter the very time-integration claim under test. The v2
re-run then failed differently: its ML solution abandoned the evidence (gain 1.2e-4,
drift-to-noise 0.73, criticality-flat surface), and a committed grid scan
(`fit_stage2.py --scan`) verified this was the global optimum, not an optimizer
failure. Diagnosis: the carded model pinned the between-driver spread but carried no
counterpart to stage 1's within-driver response variability (σ_resp ≈ 970 ≈ 0.18 of
the median), leaving Wiener noise as the only flattening degree of freedom. v3 added
that missing variability (σ_trial, fitted ≈ 1.0) and was pre-committed as the final
iteration: in-sample 0.178 against the static probit's 0.125, held-out 0.267 against
the pre-registered ≤ 0.11 / > 0.13 rule — **FAIL**, now structural rather than
artifactual: criticality-graded responding at C1–C2 where at most 0.05–0.15 s of
post-onset evidence exists under any plausible motor latency, plus a late-cell
criticality gradient shallower than integrated evidence implies. Records: v1 in
`log_stage2.txt` (summary superseded in place), v2 in `log_stage2_v2.txt`, v3 in
`log_stage2_v3.txt` and `stage2_summary.md`. Consequence folded into the plan: B.4
transfers the static stage-1 model; the accumulator is out.

**A.4 re-run under v3** (`log_button_v3.txt`, `button_validation_summary.md`): FAIL
(worst checkpoint discrepancy 0.310), inheriting the accumulator. What survives of
A.4.Q2 shrinks: the *direction* of the paradigm effect is confirmed (level shift
−0.175, gain shift +0.167 — both mean earlier pressing in the Button paradigm, as the
documented cross-paradigm excess says), but the *form* is no longer distinguished —
under the properly specified model the two shifts fit identically (RMSE 0.163 both).
Handbook ch. 11's decision 3 (level versus rate) is therefore still open, and closed
only by a better response model, not by this data plus this accumulator.

**Housekeeping**: `collect_queries.py` now parses the skill-v4 `(severity, audience)`
form and stops query text at RESOLVED lines; `fit_stage1.py`'s console output is
encoding-safe. The A.1 entry's two pre-convention review tags are hereby numbered so
the register can carry them: A.1.Q1 is the estimator change (joint MAP → marginal
quadrature), A.1.Q2 is the a_req-axis identification failure.

@A.1.Q1(judgment, review): retroactive numbering of the A.1 entry's estimator-change
tag — changing the plan's prescribed estimator was a methodological decision needing
confirmation.

@A.1.Q2(blocker, review): retroactive numbering of the A.1 entry's covariate tag — the
`a_req_max` axis cannot support a threshold fit as constructed (73% of its range is an
empty gap; the C1 anchor leaks at TTC8). Does not block the deficit-axis work; blocks
the truck check of fitting-plan §4, whose purpose is to let the allowed-deceleration
axis rescue the framing where the dread field is silent. The fix is upstream, in the
field construction.

RESOLVED A.1.Q1: the estimator change is confirmed at the gate — the joint mode of a hierarchical posterior is not its marginal mode (funnel geometry), the 2.6-fold spread inflation with zero coverage is decisive, and marginal Gauss-Hermite quadrature with Laplace on the hyperparameters is the standard treatment. The plan carries the dated correction.
RESOLVED A.2.Q1: 15 evenly spaced LOPO folds accepted — identical folds across variants keep the comparison like-for-like, and the R.1 decision does not rest on the LOPO number (which was additionally defective for the hier variants; card A.2.v2 regenerates it).
RESOLVED A.2.Q2: hierarchical lapse is the primary variant; group-level kept as the upper sensitivity bracket. Per-driver lapse heterogeneity is decisively real (p < 0.0001) and the group variant leaks pre-onset propensity into the thresholds (ρ = −0.622; σ 0.341 → 0.281 when C1 is dropped). The claimed contradiction with roadmap §5.1 was a misreading — the observed ordering is the one §5.1 predicted under leakage. Evidence: `bias_variant_diagnostics.md`.
RESOLVED A.2.Q3: the owed both-variant check was run with the lapse distribution integrated properly. The population-level undershoot was mostly an artifact of the median-lapse defect; the criticality-graded pre-onset pattern is real under both variants, is anticipation from the repeated stimulus set, and stays a recorded limitation (query R.1.Q3).
RESOLVED A.2.Q4: accepted as a standing caveat — the 2D quadrature is stable to ~5% in σ; any quoted spread carries that resolution. Node counts unchanged.
RESOLVED A.2.Q5: accepted as a standing caveat — the deficit-to-deceleration translation is an approximation and honestly returns NaN above the stimulus range; the THW column inherits both caveats.
RESOLVED A.3.Q1: remedy decided (accumulation gated at manoeuvre onset; leaky accumulator held in reserve, argued in `fit_stage2.py` and the fitting plan §2), a second misspecification found and repaired (missing trial-level threshold variability, v3), and the verdict recorded: FAIL, final and quotable — see the R.1 entry above and `stage2_summary.md`.
RESOLVED A.3.Q2: noted, with one correction — the v1 degeneracy check computed the noise sd from time-since-onset (≈1.1) while its own noise had accumulated since clip start (≈4.0), so the quoted drift-to-noise 8.7 was overstated (true v1 ratio ≈2.4). The v2/v3 code computes it from accumulated noise time; no conclusion changed (the stop condition had not fired under either reading).
RESOLVED A.4.Q1: confirmed and acted on — A.4 was re-run under the final v3 accumulator; the verdict remains FAIL (worst 0.310) and is attributable to the accumulator, whose within-scenario inadequacy is now the recorded A.3 finding rather than an open contingency.
RESOLVED A.4.Q2: partially sustained — the paradigm effect's direction (earlier pressing in Button) is confirmed under v3, but the form claim is withdrawn: level and gain shifts fit identically (RMSE 0.163 both) under the repaired model, so handbook ch. 11 decision 3 stays open pending a better response model.

@R.1.Q1(judgment, jonas): the headline percentile is specification-sensitive and every
quoted percentile must name its variant — 80th percentile 6 379 [6 128, 6 630] under
the decided hierarchical-lapse variant against 6 717 [6 201, 7 234] under the group
variant; at the 95th the gap is 7 543 versus 8 832. The gate decided hierarchical
(evidence above); this query exists so the sensitivity is seen, not to reopen the
decision.

@R.1.Q2(judgment, review): the fitted per-driver lapse and threshold correlate at
ρ = −0.700 while the model assumes independence. Card A.2.v2 fits the
correlated-effects variant with a pre-stated rule: if it moves the 80th percentile by
more than the current CI half-width (~250 deficit units), escalate before any
percentile is quoted downstream.

@R.1.Q3(minor, jonas): the anticipation phenomenon — criticality-graded responding
before and just after onset, visible at C1–C2 under every model — is a property of the
repeated-exposure fixed-clip paradigm and contaminates any mechanistic response model
fitted to this surface. Worth carrying into the design of the coming dataset
(naive-exposure or catch-trial structure would separate anticipation from boundary
crossing).

## 2026-08-28 — Card B.1 and the R.1 follow-ups, on the executing model

Batch session; Jonas unavailable, so every judgment call was made and recorded rather
than deferred. Full suite green before (123) and after (173 — 50 new property tests).
Six committed scripts, six tracked outputs. The R.1 queries were kept open as instructed
and are repeated in the summary.

**Card B.1 — the cyclist-overtake field is built, and the card's premise failed.**
`src/comfortzone/overtake.py` loads the three Random traces and hands them to the cut-in's
own predictor code, so both scenarios share one field implementation — a transfer test in
which the scenarios were computed by different code would not test transfer. The loader
validates against the study's own labels: edge-to-edge clearance at the pass comes out
0.506 / 1.004 / 1.501 m for the traces labelled 0.5 / 1 / 1.5. Three corrections to the
card, all documented in `docs/overtake_construction_note.md`: roles must be taken from the
instructed vehicle because the cut-in's lateral-span rule is not merely uninformative here
but **inverted** (the ego moves 2.24 m laterally, the cyclist 0.16 — so the cut-in rule
calls the car the target, which is the mechanism behind review finding 1.5); the lateral
coordinate is `Location_Y`, since `Offset` reproduces 0.94 / 0.45 / 0.05 m and **inverts
the criticality ordering**, a trap that would have produced a confident and entirely
spurious transfer failure; and the cyclist's width is in the trace (0.582 m) rather than
assumed at 0.6. The card's substantive premise — "the rear-end field applies nearly
unchanged" — does not hold: over the 15 cells the field orders the human response at
Spearman +0.402 while the clearance label alone orders it at −0.833. The cause is visible
rather than inferred: `p_lane` never leaves 0.843–1.000 across the whole response window
in all three conditions, so the manipulated variable is invisible to the field. What
varies here is not whether lateral overlap will occur — it will not, in any condition —
but the size of the lateral **comfort margin** at the pass, and passing a cyclist at 0.5 m
is uncomfortable precisely while being uncontroversially collision-free.

**The onset anchor was settled from the data, per Jonas's suggestion.** Ck = onset +
0.3 (k−1) s with onset = the ego's lane-change start (same absolute 0.03 m threshold the
cut-in loader uses). The alternative anchor, counting back from the pass, is ruled out:
under the onset anchor the three conditions are physically identical at C1 (clearance
spread 0.000 m), matching their nearly flat C1 rates (0.221 / 0.203 / 0.169), whereas a
pass-anchored C1 would differ by 0.55 m and predict a strong ordering the data does not
show. The residual C1 ordering that does remain is the anticipation signature of R.1.Q3,
now seen in a second scenario.

**Two candidate repairs to the lateral machinery were built, tested and reported.**
`lane_entry_bidirectional` (default off) lets the lateral projection run outward as well
as inward — the released form and the 2026-08-27 continuous form both clamp it to inward
motion, which is harmless in a cut-in and discards the whole signal in an overtake. It
over-corrects: linear extrapolation of a still-developing lateral move over a ~2.2 s
closure says the ego will have cleared in every condition, so `p_lane` collapses to 0 by
C3 and the cells end up ordered **negatively** (−0.537). Kept as a tested-and-rejected
variant. The S-ramp changes nothing here, because a shape function on a saturated input
is a no-op. @B.1.Q3(judgment, review): the indicated fix is a lateral-clearance *comfort*
term in the preference function, which is a structural change and therefore a review
decision, not one this card takes.

**Jonas's sigmoid proposal: direction supported, magnitude modest, and it corroborates
the lane-entry decision.** `lane_entry_shape(u, k)` is a normalized logistic with
g(0) = 0, g(1) = 1 exactly for every k and g(u; 0) = u, so the published linear ramp is
nested at k = 0 and the default of 0 leaves every published number untouched. Swept on the
cut-in surface with the stage-0 probit refitted at each k
(`out/lane_entry_shape_check.md`): RMSE 0.1189 linear, best **0.1154 at k ≈ +12**, and the
reflected shape is worse (0.1211 at k = −8). So the proposal's direction is right and
there is a genuine interior optimum rather than a drift to the grid edge, but the gain is
2.9% of the linear form's error. The by-product is worth more: the k → ∞ limit is a step
at half overlap, effectively the released binary gate, and it is the worst member of the
family by a wide margin (0.1457) — which corroborates the 2026-08-27 decision to make lane
entry continuous, independently of having picked a linear ramp. One bug found and fixed in
my own first implementation: the natural normalized-logistic construction is *even* in k,
so k and −k silently gave the same curve; the negative branch is now the explicit
functional inverse, and a property test checks it.

**The transfer test Jonas asked for works, and the baseline correction is what makes it
work.** `transfer_cutin_to_overtake.py`, fitting stage 1 on the cut-in (median 5 352,
σ 0.209, response sd 970) and scoring the 15 overtake cells: frozen transfer RMSE **0.176**
against chance 0.158 — worse than chance; freeing **only the lapse** gives **0.129**, past
chance and within 0.016 of the full-refit ceiling (0.113); the roadmap's secondary uniform
level shift gives 0.110. The pre-onset rate is 0.081 in the cut-in and 0.198 in the
overtake, so a no-shift primary is mis-specified at the baseline before the boundary is
consulted. The lapse is identified by that scenario's C1 cells alone, which end where the
field is zero by construction and therefore carry no boundary information — unlike a level
shift, which absorbs the quantity under test. Recommendation folded into roadmap §2 step 4
and work-order card B.4: free the lapse in the primary, keep the level shift secondary.

**LTAP re-scoped, and a field-independent bound established.** Jonas asked for LTAP to be
included and for a way to compare it at least partially. Two findings. First, LTAP is the
*richest* transfer target rather than the hardest: 3 096 trials, 18 well-filled cells
(9 PET × 2 speeds, 172 trials each), intervention range 0.110–0.907 — wider than the
cyclist overtake, whose 1.5 m condition is flat across all five timepoints and which
therefore carries roughly two informative levels. Its two-speed axis is exactly the
identifying variation roadmap §0b wants for `t_react` and `a_OV,min`; note that
intervention is *lower* at 70 km/h than at 50 at every PET (PET2: 0.360 vs 0.605), which a
construction should explain rather than assume. It has no `timepoint`, so it gives a
criticality × speed surface, not a criticality × time one. Added as card B.3.v2. Second,
the partial comparison Jonas asked for does not need a field at all: every participant saw
all four scenarios, so the one-scalar claim's central prediction can be tested directly.
`cross_scenario_consistency.py` finds per-driver criticality-adjusted propensity
correlating **+0.50 to +0.74** across the six scenario pairs, which is **0.53–0.78 of the
split-half reliability ceiling** (per-scenario reliabilities 0.93–0.98), mean **0.69**.
That is the strongest evidence for the one-scalar framing that does not depend on any
field construction — and it caps stage B, since about a third of reliable per-driver
variance is scenario-specific and no one-scalar model can explain it.

@B.1.Q1(judgment, jonas): the Random-design third question (`CZB_2`) for the cyclist
overtake is recorded as **undocumented, "to be confirmed"**, in the study's own context
file, and carries 0/1 where the cut-in carries 0/1/2. The ordered comfort/dread model is
therefore not fitted on this scenario and only the intervention response transfers.
Jonas's question — "for the cut-in it is a decision, but in one more dimension, much
should still transfer, right?" — is answered yes: `CZB_1` is identically defined in both
scenarios and is what carries the boundary; only the dread level is cut-in-specific.
Confirming the wording with the QUADRARUM group would restore a second level here.

@B.1.Q2(judgment, jonas): should `lane_entry_shape_k` be fitted? Doing so makes it the
first fitted parameter upstream of the boundary, which weakens the "no fitted constants in
the field" property the stage-0 result rests on. My recommendation is to leave it at 0 for
the primary analysis and report k ≈ 12 as a sensitivity, because a 2.9% RMSE gain does not
buy back the rhetorical cost; if it is ever fitted it must be frozen at its cut-in value
before any transfer scenario is scored.

@B.1.Q4(minor, review): the cyclist-overtake surface has a narrow dynamic range
(0.140–0.686) and one flat condition, so RMSE differences of a few hundredths between
transfer models are not decisive. LTAP is the better-powered venue for B.4's headline.

## 2026-08-28 — Jonas's follow-ups: the k decision, the literature, and the R.2 gate

Interactive session turned batch. Five items from Jonas: lock the sigmoid decision,
investigate the distance/time literature he half-remembered, find evidence for a lateral
term (he suggested Kolekar), say what to do about the R.1 judgement queries, and hand a
new plan to the more capable model. Full suite green before (173) and after (177).

**The lane-entry shape is locked at k = 12, on the CZB staging path only.** Jonas chose
option 2 of the three offered — adopt the S-shape, choose the value once, freeze it — so
`comfortzone.cutin.CZB_LANE_ENTRY_SHAPE_K = 12.0` is applied by `cutin_params`, while
`PreferenceParams.lane_entry_shape_k` still defaults to 0 and the causation work and every
released-behavior comparison are untouched. The constant is documented as *calibrated, not
parameter-free*: it was chosen against the cut-in response surface, which gives it the same
standing as the released model's own per-scenario a_OV,min, and the thing it must never
become is a per-scenario knob. The optimum is flat between k = 8 (RMSE 0.1156) and k = 12
(0.1154), so the choice is insensitive; 12 is the measured minimum and is taken unrounded
to avoid a second undocumented choice. One implementation subtlety worth recording: the
staging function must respect an explicitly supplied params object, or the k sweep that
justified the constant becomes unreproducible — `cutin_params` now only supplies the
default when `p is None`, and a property test pins that. **Consequence that must not be
lost**: the constant changes the covariate in 3 of the 18 cut-in cells (TTC4/C2 +26%,
TTC6/C1 −27%, TTC8/C1 +8%; the other fifteen are at saturated overlap and are
bit-identical), and those three are the early partially-overlapping cells that identify
the lapse. Every stage-1 number and the whole percentile table must therefore be
regenerated before being quoted again; card A.2.v2 now says so and asks for the old and
new tables side by side.

**The distance–time anomaly has a literature and a mechanism, and it is the same problem
as the lateral gap.** Five papers read (three as full text extracted from PDF, two at
publisher/abstract level; verification status is recorded per source in the note).
Zgonnikov, Abbink & Markkula (2024) modelled our exact LTAP scenario and found gap
acceptance depends on time-to-arrival **and** distance, needing a generalized gap measure.
Wang, Srinivasan, Jokinen, Oulasvirta & Markkula (2024) supply the mechanism Jonas
remembered — bounded-optimal decisions under noisy visual perception, where perceptual
noise makes time-to-arrival estimates more dispersed in some conditions than others and
the rational response to a noisier estimate is a more conservative one; their model
reproduces *greater gap acceptance at higher speed for matched time-to-arrival*, which is
our LTAP finding exactly. Mohammad, Farah & Zgonnikov found a third scenario needs a
speed-dependent *initial bias*, which is a useful warning that where the term enters
(drift, bound, or starting point) is not determined by the phenomenon. Bontje et al.
(2026) confirm that traffic accumulators conventionally drive the drift with looming or
TTC rather than with a comfort deficit, and list leaky accumulation and collapsing bounds
as the standard architectures — so our A.3 FAIL was of one specific accumulator using an
unconventional evidence variable, and the assessment's broader claim may need narrowing.
Kolekar, de Winter & Abbink (2020) give the lateral machinery: the Driver's Risk Field is a
2D field whose Gaussian cross-section widens with arc length and steering angle, multiplied
by a per-object cost and thresholded — "keep a scalar below a threshold" is our claim, with
the lateral dimension already in it, validated on overtaking and obstacle avoidance.

**The synthesis, written up as `docs/lateral_and_uncertainty_note.md`:** our field
evaluates the deficit along a *single predicted trajectory*, and both failures follow from
that one fact. A point estimate cannot express that a collision-free pass at 0.5 m is
uncomfortable (you need probability mass off the predicted path), and it cannot express
that a distant conflict is judged differently from a near one at matched time (you need
the estimate's dispersion to grow with distance). The proposal is to take the deficit in
expectation over a predictive distribution rather than at its mean — which is not a bolt-on
but a return to the framework's own form, since expected free energy is already an
expectation under a predictive distribution that the released model collapses because its
scenarios are longitudinal. Two honest caveats are recorded in the note: it adds at least
one parameter upstream of the boundary, and the *sign* of the distance effect under an
expected-deficit model is a derivation I sketched but did not do. That derivation is the
first task of the new gate, before any code.

@R.2.Q1(blocker, review): the expected-deficit proposal is the session's main design
output and is unverified. Derive the sign of the distance effect for our preference
function's actual cost asymmetry before implementing anything; if E[d] falls rather than
rises as the predictive variance widens, the mechanism predicts the opposite of the
observed LTAP effect and the proposal fails as an explanation, in which case a lateral
comfort term has to be motivated on its own terms.

**R.1.Q2 tested rather than argued: Jonas's artefact instinct is half right, and the half
that is right matters.** Final numbers, computed under the newly locked k = 12: the
independent arm recovers rho = **-0.272** (sd 0.143) from data with no correlation at all
-- 37% of the observed magnitude -- while the arm simulated with a genuine -0.7 recovers
-0.652. The observed **-0.727** is 2.9 sd below the independent arm's mean and more
negative than all twelve of its replicates, while sitting 0.9 sd from the correlated
arm's mean. So a real correlation of roughly the naive size is the best explanation,
reached through a mixture of a real effect and an artifact worth about -0.27; the
correlated-effects fit in card A.2.v2 must be judged against that baseline rather than
against zero, since a fitted -0.3 would be evidence of *no* real correlation.

**A worked example of why the k regeneration warning matters.** This script was first run
before the k = 12 lock and gave observed -0.700 with an artifact baseline of -0.288;
re-running it after the lock gave -0.727 and -0.272. Nothing else changed. The shift is
small but it is not noise -- the run is seeded and otherwise deterministic -- and it
lands exactly where card A.2.v2 predicts, because the three cells k = 12 alters are the
early partially-overlapping ones that identify the lapse, and this statistic is about the
lapse. It is a concrete demonstration that every lapse- and percentile-related number
computed before 2026-08-28 needs regenerating, not just re-labelling.

Two process notes. The script's auto-generated interpretation originally branched on an
arbitrary -0.3 threshold and, at -0.288, printed "near zero, the estimator does not
manufacture this pattern" -- the numbers were right and the prose contradicted them,
which is precisely what committing generated artifacts is supposed to prevent. The branch
was replaced with a quantitative comparison and the report regenerated. And the first
run's numbers reached Jonas in chat before the lock; the committed report is the
authoritative version.

Method: `lapse_threshold_artifact.py` simulates from the fitted model with
the two driver effects drawn independently, refits with the same estimator, and measures the
recovered correlation. The estimator manufactures a substantial negative correlation from
data that has none — the mechanism being that a driver's excess pressing has to be split
between the lapse and the threshold, forcing the two errors to opposite signs, the same
phenomenon as the classic intercept–slope anticorrelation. So the raw −0.727 overstates
whatever is really there. But it does not explain it away: the observed value is more
negative than any of the twelve independent replicates and sits inside the arm simulated
with a genuine −0.7. Reading: some of the correlation is real, the correlated-effects
variant in card A.2.v2 is still needed, and its result should be interpreted against the
artefact baseline rather than against zero. Numbers in `out/lapse_threshold_artifact.md`.

**R.1.Q1 answered as a convention, not an analysis.** Every percentile is quoted as a
triple — value, interval, and the specification that produced it (bias variant and k).
Folded into card A.2.v2 as a reporting requirement rather than left as an open query.

**R.1.Q3 settled by Jonas and turned into a plan.** His position: designing the
anticipation bias away is hard and constrains the stimulus design too much, so live with
it and correct for it once NDS data exists. Recorded as a fifth NDS use in roadmap §4c,
with the operational consequence spelled out: the paradigm offset δ stops being a constant
and becomes a small function of criticality, identified by the difference in *slope*
between the naturalistic and study-1 surfaces rather than in their level. Making that a
concrete estimator is part of the new gate.

**A new review gate, card R.2**, hands the design decisions to the capable model with the
reading done and the tests pre-registered: derive the sign first; then test on LTAP, whose
two-speed design separates time from distance by construction; then on the cyclist
overtake, where the prediction is that cell ordering improves materially on Spearman +0.402
without the model being given the clearance; and only then decide whether to adopt the
DRF's functional form wholesale or re-derive it. The gate also owns the question of whether
the A.3 verdict's wording needs narrowing in the light of Bontje et al.

@R.2.Q2(judgment, jonas): B.1.Q1 is brought forward to R.2 as instructed — the
Random-design third question for the cyclist overtake is undocumented in the study's own
materials, and one email to the QUADRARUM group would restore a second fitted level in
that scenario. It is the cheapest outstanding gain in the transfer programme and it needs
Jonas, since it is outward-facing.

## 2026-08-28 (later) — the two discriminating tests, and the second cut-in study

Two tasks from Jonas: run the two tests proposed for R.1.Q2, and scope the newly arrived
`02_Cut-in` and `03_CAMP` datasets. Both done; three findings, one of which changes how an
existing query should be read. Full suite green (177) before and after; no source changed.

**Test A: the response floor is largely a person trait.** Per-driver pre-onset (C1) rate
in the cut-in against the cyclist overtake, measured directly with no model in between,
correlates at Spearman **+0.546** (p = 1.5e-4) against a split-half reliability ceiling of
0.901 — 61% of the reliable signal is shared. A floor that travels with the person across
two quite different scenarios is a property of the responder, which supports the
response-style and anticipation accounts over a scenario-specific lapse.

**Test B: null, but the null is uninformative and that is the finding.** Standardising
trial order within participant x scenario x session (dictionary gotcha 4), the mean
within-participant slope of C1 responding is **+0.005 (SE 0.052)**, 95% CI
[-0.097, +0.108]. Pressed on its power, the test collapses: a participant contributes 24
pre-onset trials and presses on a median of **one**, 17 of 43 have no variation at all and
drop out, and those 17 are the low-floor participants (mean C1 rate 0.059 against the
retained group's 0.192), so the trend is measured only on the higher-floor half of the
sample. The smallest slope detectable at ~80% power is 0.146, while the exposure effect
that actually exists — measured in test E below, on a design built for the question — is
**+0.027**. The test could not have detected an effect five times larger than the real
one. So the correct conclusion is *study 1 cannot address anticipation*, not *anticipation
is absent*, and Jonas's expectation is neither supported nor contradicted here. Reported
this way in `out/response_style_and_anticipation.md`; my first pass through this stated
the null as if it were evidence of absence, which it is not, and the report was corrected
before commit.

**Test C, not planned, and the most consequential thing here: C1 is not a null scene.**
The project has treated the C1 cells as carrying no boundary information, on the grounds
that the clip ends at manoeuvre onset. Checked against the traces, that is false. At C1
the three criticality conditions differ by a factor of two in the car-following state —
gap 10.5 / 16.0 / 21.5 m, time headway 0.34 / 0.52 / 0.70 s — and they differ in the
direction that matches behaviour, tightest gap giving the most intervention
(0.122 / 0.070 / 0.052). That is not anticipation of a manoeuvre; it is an ordinary
response to an ordinary car-following situation. **And the field orders those cells
backwards**, assigning deficit 1 / 1509 / 2907 — the lowest deficit to the tightest gap.
The lane gate is the obvious suspect, since the lead is still fully in the adjacent lane
at C1, but the mechanism is not diagnosed here. The consequence is concrete and affects
two open queries: the lapse floor is being fitted to cells that carry real boundary
signal, using a covariate that ranks them wrongly, so part of the lapse-threshold
correlation is a **mis-assignment** rather than a trait, an estimator artifact, or the
paradigm. This is a fifth explanation for R.1.Q2, was on nobody's list, and is the only
one that is a defect in our own construction. It also weakens R.1.Q3's premise: the graded
pre-onset responding it attributes to repeated exposure is at least partly a response to a
genuinely graded pre-onset scene.

**The second cut-in study is the dataset review gate R.2 needs.** 10 944 trials, 168
participants, same three response variables as study 1 including the ordered
expected-braking question. Its delta-velocity factor is crossed with time-to-collision and
the two multiply into distance by construction (`distance = TTC x DV`), so matched-TTC
cells span gaps from 1.6 m to 78 m — a factor of six, in the scenario whose field we
already have, against LTAP's factor of 1.4 in a scenario whose field we do not.

**Test D, the distance-versus-time question, answered.** Forming participant means first
(DV and CP subsets are between-subjects), then over the TTC x DV cells: **all 24 matched-TTC
rows run negative** — at identical time-to-collision, a larger gap means less intervention,
by as much as 0.042 against 0.818 at TTC_true = 4.7 s. Across all cells, gap orders the
response at rho = **-0.887**, time-to-collision at **-0.807**, and required deceleration
`DV / (2 TTC)` at only **+0.238**. The last is the one to dwell on: its sign is what a
demand-based model wants, but its magnitude is negligible, so the quantity our safety
terms are built from barely orders these cells while gap orders them almost perfectly.
This is direct evidence for the R.2 proposition and it is far stronger than the LTAP
observation that prompted it. What it cannot do is separate gap from closing speed or from
headway, which are perfectly confounded at matched TTC by construction — the study's own
documentation says so.

**Test E: repeated exposure does move responding, which study 1 could not show.** Every
block-1 clip is shown twice to the same participant. Over 3 456 clip-participant pairs,
P(intervene) is 0.547 on the first showing and **0.575** on the second, a difference of
**+0.027 (SE 0.007)**, about four standard errors. So Jonas's anticipation account is
supported after all — by the dataset with the design to test it, in the direction he
predicted — even though the within-session order test on study 1 was null. The effect is
small, and it is a shift in overall responding rather than specifically a pre-onset shift.

`03_CAMP` is described only (19 files) and no use is proposed, per Jonas's steer.

@B2.Q1(blocker, review): the C1 finding above is a defect in the field, not in the data,
and it invalidates the interpretation of the lapse in every fit run so far. Diagnose why
the field inverts the pre-onset ordering, then decide whether C1 joins the boundary fit
with a corrected covariate or is dropped and the lapse identified elsewhere. Until then
the fitted lapse should not be described as a response floor, and the percentile table
inherits the uncertainty.

@B2.Q2(judgment, review): the second cut-in study should be promoted from "new data" to
the primary venue for the R.2 distance-versus-time decision, ahead of building the LTAP
field. It is the same scenario as our existing construction, the manipulation is six times
larger, and the ordered braking question is present so the comfort/dread pair transfers.
The LTAP field remains worth building for the transfer test, but it is no longer on the
critical path for the modelling question.

@B2.Q3(minor, jonas): the second study's TTC 5/6/7 levels are between-subjects and its
DV and CP subsets are split-half, so any use of it must form participant means before
aggregating. This is already done in `cutin2_scope.py` and is flagged so it is not lost
when someone fits it properly.

## 2026-08-28 (end of arc) — the collinearity finding, and the documentation round

Closing the arc at Jonas's request: summarize, re-document, update the handover, and say
what the stronger model should do. One new finding, and it is the one that reframes the
rest.

**Study 1's cut-in design has one longitudinal degree of freedom.** Relative speed is
constant at 2.78 m/s across all 18 cells, so time-to-collision is gap divided by a
constant and **correlation(gap, TTC) = 1.0000**; headway and required deceleration are
fixed functions of the same number. Every longitudinal result fitted on study 1 — the
stage-0 correlation of 0.90, the boundary level 5 352, the percentile table — is
therefore equally consistent with a driver who thresholds the preference field and one
who thresholds the gap. Nothing computed is wrong and the boundary is well estimated on
its own scale, but none of it is evidence for the field's kinematic content, because the
design contains no contrast that separates it from the simplest alternative. Reproduced
in `cutin2_scope.py` §0. This should have been noticed several sessions ago; the cost is
that estimator refinement was done on a design that cannot discriminate the estimator's
model. Folded into the assessment (§3.2), the handover chain, and card R.2 as its new
first task.

**Documentation round.** New `handover_2026-08-28.md` covering the arc; `handover.md`
rewritten to point at review gate R.2 with the collinearity finding first;
`docs/active_inference_for_czb_assessment.md` §3.2 sharpened, since the claim it makes
about within-scenario fit was understated rather than wrong; card R.2 rewritten around
five prioritized decisions with the first being "is the preference field the right scalar
at all"; README updated. Word and PDF rebuilt for every changed document. Suite 177 green.

**What the stronger model is being asked to do**, in priority order, is recorded in card
R.2: (1) fit the existing field to the second cut-in study against a one-parameter gap
threshold on identical held-out folds, pre-registered, because that is now the live
question; (2) diagnose the C1 inversion, which blocks the interpretation of every fit;
(3) decide the lateral term, with Kolekar et al.'s risk field as the strongest donor;
(4) rule on whether the project's headline becomes the field-independent transfer trait
(~69% shared) if (1) goes against the field; (5) decide whether the A.3 wording needs
narrowing in the light of Bontje et al. The card also carries the warning that the
unified "one mechanism explains both findings" story was tried and does not survive its
own sign check.

@B2.Q4(blocker, review): the gap-versus-field comparison on the second cut-in study is
the single most consequential outstanding analysis in the project, and it is cheap. Until
it is run, no document should describe the field as validated against human data on the
longitudinal dimension — the wording throughout has been adjusted to say "well estimated
on its own scale" instead, but the distinction is easy to lose.

## 2026-08-28 (audit) — verifying the arc before handing over

Jonas asked for a pass over the whole session to check that nothing important was left
unpursued before a clean and a model switch. Five real gaps found, all closed; two
recorded as known and deliberately not closed.

**Closed.** (1) `stage2_summary.md` cited `out/log_stage2_v2.txt` as evidence that the v2
optimum was global, and that file contains the v2 *fit* log, not a scan — a provenance
claim pointing at a file that does not support it. The committed `--scan` was actually run
(`out/log_stage2_scan.txt`) and the citation corrected; while fixing it the claim itself
was softened, since a coarse grid shows the optimizer succeeded rather than proving a
global optimum. (2) `lane_entry_bidirectional` and `lane_entry_max_dy_m` had no property
tests, against the standing rule that new behaviour gets tests — six checks added,
including that the flag stays off by default, since the variant is kept only so a rejected
result stays reproducible and the failure mode is that it silently becomes default.
(3) `docs/czb_fitting_plan.md` §4 still framed the deficit-versus-a_req axis choice as
open on study 1, where it is undecidable; it now carries the collinearity note and the
second study's +0.238 for required deceleration. (4) Two undocumented facts about
`02_Cut-in` recorded in the work orders: the annotated file has **144** participants, not
the 168 its context document states, and there is exactly one attention-check trial per
participant with answers splitting 124/16/4, so ~20 gave a non-modal answer and whoever
fits it must decide explicitly about exclusion. (5) All eight new scripts verified to
import cleanly from a bare checkout.

**A consequence caught during the audit, and it matters.** Re-running stage 2 after the
k = 12 lock re-fits stage 1, and the between-driver spread comes back **0.194 against the
0.209** fitted under k = 0 — about 7%. Every percentile quoted in the handover chain is
therefore a pre-k=12 number. They are left as written because they are what the committed
outputs currently say, but both handovers and card A.2.v2 now flag it and give the
expected size of the shift, so a regeneration that moves things much further is a signal
that something else changed.

**Verified not blocked.** The existing cut-in loader reads the second study's traces
correctly (ego 28.7 m/s, target width 1.88 m, onset detected at frame 51 of 600), so
review gate R.2's first task — fitting the field against a gap threshold on that data —
needs no pipeline work first.

**Left open deliberately**, and recorded in `handover_2026-08-28.md` §8b: the handbook
contains none of this arc and would still tell a reader the accumulator is untested; card
C has never been run and now depends on A.2.v2; no per-criticality deficit figure was
produced for the overtake; and the query identifiers are inconsistently formed (`B2.Qn`
alongside `B.1.Qn`), which stands as a wart because raised identifiers are never
rewritten.

## 2026-08-29 — Card B.2.v2 item 1: the C1 covariate defect, diagnosed and fixed (tier 1, batch)

Blocker B2.Q1 is closed, and the inversion turned out to be a covariate-window error,
not a preference-function or data error. Two distinct defects, both diagnosed
frame-by-frame in `replication/czb/c1_covariate_defect.py` (report:
`out/c1_covariate_defect.md`). First, the C1 covariate lookup included the
manoeuvre-onset frame: at that frame the target has moved at most 6 cm, but the
lane-entry projection's lever arm is the longitudinal TTC, so the same sliver of
lateral motion projects to near-full predicted overlap at the LARGEST gap — p_lane
0.000 / 0.318 / 0.997 for TTC4 / TTC6 / TTC8 — and that backwards-ordered gate
multiplies a correctly-ordered p_safe magnitude into the observed 1 / 1509 / 2907
inversion. The frame at -0.1 s is also contaminated, because its central-difference
lateral-velocity estimate uses the onset frame. Second, the running max accumulated
from the trace start, ~15-17 s before onset, while the shown clips are ~10 s ("a T2
clip of ~10 s shows ~9.7 s of normal driving", the study's own context file): a
2 m/s^2 differentiation blip at trace second 1.2 in the 1.5 m overtake — never shown
to any participant — put a floor of 230.9 deficit units under every cell of that
condition. Fix in `comfortzone.czb_data`: running maxima accumulate only over the
shown window (`RANDOM_CLIP_LEAD_S` = 10 s before onset for Random; the documented
clip start for Button), and C1's covariate window ends at `C1_COV_END_S` = -0.15 s
(one and a half frames before onset — a resolution guard excluding the onset frame
and the frame whose velocity estimate touches it, motivated in the module comment).
`legacy_covariates=True` reproduces the old numbers. Effects: cut-in C1 covariates
1.26 / 1509 / 2907 -> 0.98 / 1.57 / 1.35 (noise level, no longer ordered); cut-in
C2-C6 bit-identical; overtake C1 and the 1m/1.5m C2 cells lose their artifact floors.
Lead-time sensitivity flat over 8-12 s. Eight property tests added (test_cutin.py,
79 -> 87 checks, all green). Decision taken at gate level (tier 1): **C1 stays in the
fit** with the corrected covariate and identifies the lapse, exactly as the model
assumes; the fitted lapse may again be described as a response floor once A.2.v2
regenerates under this convention.
@B2.Q5(judgment, review): the real condition ordering in C1 behaviour (0.122 / 0.070 /
0.052, tightest gap most intervention) is NOT captured by the corrected field — the
lane gate zeroes the adjacent-lane longitudinal proximity signal by construction.
Recorded as a structural limitation feeding R.2's field-versus-gap question, not
patched; an ungated tau-preference would order these cells correctly (only TTC4's
TTC 3.78 s is inside the 5 s preferred-TTC bound) but that is a preference-function
change and belongs to the R.2 lateral/proximity decision.
@B2.Q6(minor, review): stage 1, the transfer test, and the percentile table were all
fitted on the pre-fix covariates; every C1-dependent number (lapse, lapse-threshold
correlation, transfer-with-freed-lapse) carries this regeneration debt in addition to
the k = 12 debt. A.2.v2 and the B.4 re-run settle both at once.
RESOLVED B2.Q1: covariate-window error, two mechanisms (onset-frame inclusion
amplified by the TTC-lever projection; whole-trace accumulation of unseen frames).
Fixed in czb_data with the shown-clip window; C1 joins the fit with the corrected
covariate; evidence in out/c1_covariate_defect.md.

## 2026-08-29 — Card A.2.v2: stage 1 regenerated under k = 12 + the covariate fix (tier 1, batch)

Run as committed, with `fit_hier_corr` added per the card. Specification per the
R.1.Q1 convention: hierarchical lapse, k = 12, shown-window covariates (the B2.Q1
fix), product-grid LOPO, lapse-integrated C1 predictive. Results
(`out/stage1_summary.md`, log `out/log_stage1_v2.txt`, 28 min):

**The percentile table survives regeneration essentially unchanged** — 50th
5352 -> 5400 (+0.9%), 80th 6379 -> 6390 (+0.2%), 95th 7543 -> 7503 (-0.5%); the
k = 12 shift (which alone moved sigma_pop 0.209 -> 0.194) and the C1-covariate fix
(which removes the inverted 1509/2907 C1 covariates) largely offset, landing at
sigma_pop 0.200, median 5400. Within the card's expected-magnitude band, so no
anomaly flag. **The LOPO comparison, regenerated on the product grid, now separates
the bias variants decisively**: hierarchical beats group by +52.7 held-out
log-likelihood units (was +0.6 under the defective diagonal integration) — the R.1
decision is confirmed with real evidence rather than a coin-flip margin.
**The correlated-effects variant converged with usable SEs**: rho = -0.717
(SE 0.128), moving the 80th percentile by 17 deficit units against the pre-stated
escalation threshold of ~254 (the CI half-width) — **the hierarchical variant stands
as primary**, correlated reported as robustness. Against the artifact baseline of
-0.27, the fitted -0.717 confirms R.1.Q2's reading: a real trait correlation of
roughly the naive size, not an estimator artifact. The C1 predictive is now flat
(0.100 for all three conditions) against the observed 0.122 / 0.070 / 0.052 — the
expected signature of B2.Q5 (real proximity gradient the lane-gated field cannot
express), no longer contaminated by the covariate inversion.
RESOLVED R.1.Q2: the correlated-effects variant was fit; rho = -0.717 (SE 0.128)
against the -0.27 artifact baseline — part of the correlation is a real trait, and
it does not move the deliverable (80th percentile shifts 17 units, rule says stand).
@A2v2.Q1(minor, review): the k = 12 sweep re-run under the corrected covariates
(out/lane_entry_shape_check.md regenerated) keeps its optimum at k = 12 (RMSE
0.1162, k = 8 at 0.1166, flat optimum as before) — Jonas's constant survives the
covariate fix; recorded so the decision's evidence base is current.
@A2v2.Q2(minor, review): the -0.27 artifact baseline was computed under the pre-fix
covariates; with C1 covariates now ~0 the lapse/threshold trade-off structure
changed, so `lapse_threshold_artifact.py` should be regenerated before the -0.717 is
quoted in a manuscript. The conclusion is robust at this distance (0.45 gap) but the
baseline number itself is stale. Deferred tonight for CPU (two long jobs were queued).
@A2v2.Q3(minor, jonas): the run also re-fitted the ordered braking-expectation model
under the new covariates — comfort 3703 -> 3418, dread 6397 -> 6572, separation delta
2694 -> 3154 (+17%). These moved more than the intervention percentiles because the
ordered model's lapse is group-level (per its 5-parameter spec) and the C1 fix
changes what the lapse absorbs. Nothing downstream quotes the old values except the
handover chain, which will be regenerated; flagged because the comfort level moved
-8% and anything Jonas remembers from 08-27 about "comfort ~3700" is now ~3400.

## 2026-08-29 — Review gate R.2, run at tier 1: the field ruled against, and the restatement

The gate's record is `docs/r2_gate_decisions.md` (with Word/PDF); this entry carries
the queries. The five card questions were answered in order. (1) **The field versus a
gap threshold on the second cut-in study, pre-registered** (models, folds, decision
rule committed before the run, commit e9203c6): the pre-registered rule fired at
dRMSE = +0.195 — the field scores 0.347 held-out wRMSE, worse than chance 0.320,
while the log-gap threshold scores 0.152 against a sampling-noise floor of 0.118;
TTC 0.168; required deceleration 0.289. Robust to the attention-check exclusion
(+0.202) and to a post-hoc trace-noise repair (the 30 Hz ego-speed dither puts a
~1000-unit accel-term floor under every field covariate; smoothed, the field scores
0.356 — verdict unchanged, and its within-row orderings stay sign-inconsistent, 14
of 24 rows negative against the data's 24 of 24). **The field is ruled against on
its own scenario.** (2) The C1 defect was closed earlier tonight (B2.Q1 entry
above). (3) The lateral term is NOT built: the R.2.Q1 sign derivation
(`out/expected_deficit_sign.md`) shows the expected-deficit mechanism is a
second-order, sign-unstable modulation where the data show a first-order monotone
gap effect, and grafting a lateral term onto a rejected longitudinal core would
build on sand; the DRF is re-positioned from donor to comparator. The note's
pre-registered LTAP/overtake tests of the proposal are cancelled, with the dated
note in `docs/lateral_and_uncertainty_note.md` §6. (4) **The headline becomes the
trait claim** — one scalar per driver, ~69% of reliable signal shared across
scenarios, boundary percentiles stable across specification changes (A.2.v2: 50th
+0.9%), transfer working with a freed lapse — with the criticality axis an open
question on which gap (log) currently leads. The elliptical/2D comparator program
moves from fallback to primary for the axis question, which is the fallback the
project recorded in advance. (5) The A.3 wording is narrowed in the assessment per
Bontje et al. (dated note). The transfer test was re-run under the new
specification: freed-lapse RMSE 0.136 (chance 0.158, ceiling 0.120) — the story
survives regeneration.
RESOLVED B2.Q4: the comparison was run, pre-registered; the field lost decisively;
the wording rule ("well estimated on its own scale", never "validated") is now
backed by the analysis and extended: the field's kinematic content is ruled out as
fitted on the longitudinal dimension.
RESOLVED B2.Q2: the second study was promoted and used as the primary venue; LTAP
stays off the critical path for the modelling question.
RESOLVED B2.Q5: amended before resolution — the second study's 90 CP1 cells are
FLAT (rates 0.000-0.115, rho(gap) = -0.04, gaps 3.9-82 m), so drivers do not
respond to adjacent-lane proximity pre-encroachment, and study 1's C1 gradient is
better read as exposure-driven anticipation (supported by the 0.547 -> 0.575
second-showing effect); the lane-gated flat floor is supported at pre-encroachment.
The structural point (the field cannot express such a response) stands but is moot
under the section-1 verdict.
RESOLVED R.2.Q1: the sign derivation was done before any implementation, on the
actual preference function over the study's own range; the mechanism fails for the
distance effect (direction inconsistent across rows, magnitude second-order) and
survives only for the lateral direction, which is not being built (gate §3).
RESOLVED R.1.Q1: adopted as the reporting convention in A.2.v2 (value, CI, and
specification on every quoted percentile; spec header on the summary).
RESOLVED R.1.Q3: Jonas's live-with-and-correct position is turned into the
concrete estimator recorded in `docs/czb_validation_roadmap.md` §4c item 5, with
the B2.Q5-derived caution that delta_1 absorbs paradigm and field misspecification
jointly.
@R2.Q4(judgment, jonas): with the field ruled against, should cards B.2 (truck) and
B.3 (LTAP) remain FIELD constructions, or become constructions of the comparator
class (per-scenario 2D state rules + the elliptical joint percentile) that the
restated program needs? My recommendation: the latter; the LTAP construction note
(B.3.v2) should be written for arrival-time separation + oncoming distance as
observables, not for the preference field. Nothing is built until you rule.
@R2.Q5(judgment, jonas): how the assessment document and any manuscript position
the active-inference contribution after this gate. My recommendation: the honest
paper is stronger, not weaker — a validated-model-derived field, a pre-registered
falsification of its kinematic content against human data, and a surviving
cross-scenario trait claim; but that is a positioning call only you can make.
@R2.Q6(judgment, jonas): the handbook still describes the field, the accumulator
and the CZB path as of 2026-08-27 and now also predates this gate. Options: a
one-page dated correcting note inserted now ({{R3}} not yet started), or waiting
for your Word review. Recommendation: the note, since a reader today would learn a
claim the data have since overturned.
@R2.Q7(minor, review): two study-2 data-quality facts for whoever touches those
traces: the ego speed carries ~0.1 m/s dither at 30 Hz (smoothing sensitivity is
report §5), and `load_cutin_trace`'s 0.03 m onset threshold misdetects onset on
these traces (fires at t = 1.7 on slow drift against a true onset near 15.1) — the
2026-08-28 audit's "onset detected at frame 51" was wrong as a validation claim,
though nothing used it; the field-vs-gap runner takes its windows from the video
filename stamps instead.
@R2.Q8(minor, review): `out/transfer_overtake_summary.md` (generated) still says a
lateral-comfort term "is the obvious next model step" — written before this gate;
superseded by gate §3. Left as-is because generated outputs are never hand-edited;
the script's reading text should be updated if that summary is ever regenerated
for another purpose.

RESOLVED B.1.Q2: settled by Jonas on 2026-08-28 — k is a calibrated constant fixed at
12 on the CZB staging path, never fitted and never per-scenario (argument in
docs/overtake_construction_note.md §5); the 2026-08-29 re-sweep under the corrected
covariates keeps the optimum at k = 12, so the decision's evidence base is current.
RESOLVED B.1.Q3: answered at gate R.2 (2026-08-29, docs/r2_gate_decisions.md §3) — no
lateral-clearance comfort term is added to the preference function: the expected-
deficit mechanism fails the sign derivation on the distance axis, and the field's
longitudinal core was ruled against by the pre-registered comparison, so a lateral
graft would refine a rejected core. The DRF is a comparator for the restated
program, not a donor.

RESOLVED B2.Q6: the regeneration debt was paid the same night it was raised — card
A.2.v2 regenerated stage 1 and the percentile table under the corrected covariates
(shifts under 1%), and the cut-in -> overtake transfer was re-run (freed-lapse 0.136
against chance 0.158, ceiling 0.120). The only stale lapse-related number left is
the artifact baseline, tracked separately as A2v2.Q2.

## 2026-08-29 (later) — Card C: percentile sensitivity, first run (tier 1, batch)

`replication/czb/percentile_sensitivity.py` -> `out/percentile_sensitivity.md` +
`figures/percentile_sensitivity.png`. Specification: the A.2.v2 configuration,
refitted live (hier lapse, k = 12, shown-window covariates); onset = first crossing
of the running-max deficit by the percentile level, per Random stimulus. Findings:
**(1) the percentile choice and the estimation uncertainty are of comparable size**
— one 5-point step moves the trigger onset by ~0.27 s on average (max 1.03 s near
the tail on TTC4) against ~0.53 s of onset shift across a level's own 95% CI — so
neither dominates, which answers the standing concern (the docs/czb note that "the
percentile choice may matter more than estimating a true CZB") with "they are
comparable on this stimulus set, both around a third of a second per step".
**(2) The reachability finding matters more**: TTC8 never reaches even the 50th
percentile level (clip max 4 315 against median 5 400) and TTC6 tops out near the
75th, so at population-median strictness two of the three stimuli would never
trigger at all — percentile choice is not only WHEN but WHETHER. Comfort (3 418)
is reached by all three stimuli; dread (6 572) only by TTC4.
@C.Q1(minor, review): onset times for levels below ~2 900 on TTC8 (and ~1 500 on
TTC6) would be distorted by the manoeuvre-onset projection spike that the covariate
series still carries at t = 0 (the B2.Q1 fix corrected the TRIAL windows, not the
series); all levels used here sit above it, so no reported number is affected —
recorded so nobody later reads sub-comfort onsets off this table without checking.
@C.Q2(judgment, jonas): given R.2, should the percentile deliverable stay on the
deficit axis at all, or migrate to whatever axis the comparator program settles on?
The sensitivity machinery here transfers to any monotone axis unchanged; nothing
in this card locks the axis in.

RESOLVED A2v2.Q2: `lapse_threshold_artifact.py` was regenerated under the new
covariates the same night (26 min; log `out/log_lapse_artifact_v2.txt`). The
artifact baseline moves -0.272 -> -0.280, the observed raw correlation -0.727 ->
-0.720, and the correlated arm recovers -0.636 — every conclusion unchanged, and
A.2.v2's fitted rho = -0.717 now sits 1.0 sd inside the genuinely-correlated arm
against a current baseline. One nit: the regenerated report's closing line still
says "R.1.Q2 stays open [and] the A.2.v2 variant is still needed" — generated
prose written for the pre-A.2.v2 state of the world; the numbers above it are
current, and R.1.Q2 is resolved in this log.

## 2026-08-29 (morning) — R2.Q6 executed: the handbook status note (Jonas's ruling)

Jonas ruled "yes, update" on R2.Q6 and postponed the smaller queries; R2.Q4, R2.Q5
and C.Q2 were explained to him in chat and remain open awaiting his ruling. The
handbook now carries a round-5 status correction in dark orange ({{R5}}, new color in
`build_handbook.py`; the handover's "next round would be R3" was stale — rounds R3
and R4 already exist in the chapters, so this is round 5). Three insertions, all
marked: a revision-round paragraph in chapter 00 (what moved and where the record
is); the main status note at the top of chapter 11 (the four results in order —
boundary well estimated on its own scale; the accumulator's pre-registered FAIL,
scoped to its architecture; the study-1 collinearity and the second study's
pre-registered verdict against the field; the surviving trait claim and the
restated headline); and a short note heading chapter 04's cut-in section (the
construction it plans was built, fitted, and ruled out; pointer to chapter 11).
The chapters' original text is kept as written — the notes say how to read it, per
the correct-in-place convention. Word and PDF rebuilt for all chapters and the
combined document (no OneDrive locks fired).
RESOLVED R2.Q6: Jonas ruled to update now rather than wait for his Word review;
done as above.

## 2026-08-29 (morning, before reboot) — Jonas rules on R2.Q4/Q5 and C.Q2

Recorded verbatim-in-substance from chat, minutes before his machine rebooted.
RESOLVED R2.Q4: B.2 (truck) and B.3 (LTAP) are built as COMPARATOR-class
constructions (per-scenario 2D state rules + the CZB ellipse), per the
recommendation — but the field alternative must stay documented, with the pros
and cons of each route written down (his condition). The construction notes for
B.2/B.3 must therefore carry a short both-routes section, not silently drop the
field.
R2.Q5 partially ruled, stays open in narrowed form: Jonas is not ready to settle
the positioning. His counter-question: have we really explored active inference
at its fullest — in particular, can the SURPRISE elements be kept on their own,
with surprise defined as a scenario-AGNOSTIC metric, even if the full preference
field is dropped? Direction: go with the comparator program for now, but explore
the scenario-agnosticism options of the surprise family further (the
src/surprise library is validated and scenario-independent by construction; what
was ruled out is the preference-field deficit as the criticality axis, not
surprise as a family). Positioning of any paper waits on that exploration.
C.Q2 stays OPEN by his ruling, and he explicitly wants the CZB ellipse explored
— the elliptical joint-percentile construction moves from "comparator we score
against" to "deliverable candidate to develop".

## 2026-08-29 (later) — the scope-map overview document

Not a card: Jonas asked, after his R2.Q4-Q6 rulings, for a standalone overview of what
the project uses of the active-inference paradigm, what it does not, and which paradigms
the surviving method actually consists of. Written as `docs/active_inference_scope_map.md`
with six figures generated by `docs/make_ai_scope_figures.py` into `docs/ai_scope_figures/`;
the two data figures parse their numbers from `out/cutin2_field_vs_gap.md` and
`out/cross_scenario_consistency.md` rather than carrying literals, so a regenerated
analysis moves the figure. No new analysis was run; the document only collects and
re-states what the gate records, the assessment document and the code already establish.
Quoted numbers were re-derived from the tracked outputs before use, which surfaced one
disagreement.
@SCOPE.Q1(minor, jonas): `docs/active_inference_for_czb_assessment.md` section 3.3 quotes
the A.3 accumulator verdict as in-sample "best 0.178 vs 0.125" and held-out "0.267",
where the tracked output `out/stage2_summary.md` (v3, final at R.1) gives 0.169 and
0.255 against a rule of <= 0.11 (> 0.13 is failure). The assessment document appears to
quote a pre-v3 iteration. The scope map uses the output's numbers and flags the
disagreement in place; the assessment document should be corrected in place with a dated
note rather than rewritten. The FAIL verdict is unaffected.

## 2026-09-01 — the 15-20 minute project-group deck

Not a card: Jonas asked (going to bed; batch mode) for a shorter presentation for the
project group (cognitive science, driver modeling, vehicle safety engineering), 15-20
minutes, covering (a) the idea of active inference and surprise, (b) the CZB versions
tested, (c) where we ended up and why, (d) what to do now — with a short objectives
slide and a short what-worked/what-did-not summary slide. Built as
`presentation/talk/build_short_talk.py` → `ai_czb_short_talk.pptx`: 13 slides, notes
budget 19.8 min, two CUTTABLE slides (animation, R.1) bringing it to ~16.5. Content is
condensed from the 60-minute deck (`build_talk.py`, built earlier the same day by
another session); every quoted number traces to the same tracked outputs
(`out/cutin2_field_vs_gap.md`, `out/cross_scenario_consistency.md`,
`out/stage1_summary.md`, `out/stage2_summary.md`, `docs/r2_gate_decisions.md`). All 13
slides rendered to PNG and inspected; one panel-overflow and one figure/kicker count
mismatch fixed. Full property-test suite green before and after (31+33+40+87 = 191; no
source files touched). The earlier session had left `presentation/talk/` untracked
with no worklog entry; this session committed those files alongside (the short deck
imports its helpers and reuses its figures), with `presentation/talk/*.pptx` added to
.gitignore to match the existing deck convention.
@TALK.Q1(minor, jonas): both decks attribute the talk to Jonas alone; co-authors and
the QUADRARUM/QUADRIS collaborators are not named. The 60-minute deck's README already
flags this; it matters more for the short deck, since the project group audience
likely includes those collaborators.
@TALK.Q2(judgment, jonas): the 60-minute deck file `ai_czb_talk.pptx` has an mtime
(08:35) later than its build script (07:47), so it may carry a hand save. Its script
had a figure/text mismatch ("Six steps" against the seven-row progression figure);
fixed count-free in `build_talk.py` ("The steps, and where each one landed"), but the
deck was deliberately NOT rebuilt — per the copy-and-augment rule — so the built
60-minute deck still shows "Six steps" until Jonas confirms it carries no hand edits
and rebuilds, or edits the two strings in place.
@TALK.Q3(minor, jonas): the short deck's closing one-liner ("the axis entered a fair,
pre-registered competition and lost; what survived is the thing worth building on")
and the "not a failed project" summary panel are editorial framings consistent with
the gate record and the scope map, but Jonas may want them plainer; both are single
strings in `build_short_talk.py`.

## 2026-09-02 — adversarial review of the R.2 decisive pipeline

Not a card: Jonas asked what to do with remaining top-tier budget and accepted the
proposal (1) the R2.Q5 surprise-without-the-field note, with (2) an adversarial review of
the decisive field-versus-gap pipeline alongside. (2) was run first, since a defect there
would change how (1) is framed. Read line by line: `cutin2_field_vs_gap.py`, its report,
`comfortzone.cutin`, `comfortzone.czb_data`, and the safety/collision/lane-entry terms in
`aidriver.preferences`. New tracked diagnostic `replication/czb/cutin2_lane_gate_diagnostic.py`
→ `out/cutin2_lane_gate_diagnostic.md` (log `out/log_lane_gate_diagnostic.txt`); review
document `docs/r2_pipeline_review.md` (+ Word/PDF); dated note in `docs/r2_gate_decisions.md`
§1. Findings: the verdict reproduces by an independent grid fit with closed-form lapse
(field 0.3508 vs registered 0.3471; gap 0.1531 vs 0.1522), cell-bootstrap interval on the
difference +0.174..+0.222 against the 0.01 margin; model-free Spearman of the field with
the response +0.14 vs the gap's +0.86, so no fit could rescue it. The loss decomposes:
forcing the lane-entry gate to 1 recovers 0.087 of the 0.199 deficit (~44%) — the gate
(a project construction) suppresses the deficit in the 64 slow-lane-change cells at
starting TTC 2-3 s whose mean response is 0.75, where participants are flat across
lane-change duration; the remaining ~56% is the released counterfactual magnitude, whose
local sensitivity to either vehicle's speed is 4-6x its sensitivity to gap, so it orders
matched-TTC cells by absolute speed where participants order by gap (the study realizes
DV partly via ego speed: 30.7 vs 36.5 m/s). Verdict unchanged; scope statement sharpened.
Also found: the gate record's gloss "orders 14 of 24 rows in the observed direction" was a
sign slip — the registered report counts rows where rho(field, P) is NEGATIVE, i.e. the
field is anti-ordered in 14 and ordered like the data in 10; corrected in place (dated) in
the gate record and in `presentation/talk/build_talk.py` slide 36 (deck not rebuilt, per
TALK.Q2). Minor: the registered L-BFGS-B numbers move by up to 0.005 under row
permutation (flat objective; irrelevant at the margin); the trace-vs-annotation TTC
discrepancies sit in the 7 km/h clips (1.9 m/s closing speed) and handicap the design
scalars, not the field. Suite 191 green; no source files changed.
@REV.Q1(minor, jonas): should a manuscript attribute the gate's ~44% share to "our
continuous lane-entry form" or to the published model's lane gate? The released binary
gate was not run on study 2; by its geometry it should suppress the same cells at least
as hard, and the check is cheap (one flag in `cutin_params`). Not run without a ruling,
since it would add a fifth model to a registered comparison.
@REV.Q2(minor, jonas): the built 60-minute deck's slide 36 still reads "the field orders
14 of 24 rows in the observed direction"; the correct wording ("only 10 of 24, anti-ordered
in 14") is in the build script. Rebuild if the deck carries no hand edits (see TALK.Q2), or
edit the one line in PowerPoint.
@REV.Q3(judgment, jonas): the review's section 5 reads the two failure mechanisms as
constraints on any replacement reference for the surprise exploration (engage at
encroachment onset independent of lateral pace; order matched-TTC cells by gap, not by
absolute speed), and offers the opinion that a worst-case counterfactual may be the right
reference for collision avoidance and the wrong one for comfort. The R2.Q5 note is being
written on that basis; say so if the framing should be different.
