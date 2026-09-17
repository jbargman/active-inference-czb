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

## 2026-09-02 — the R2.Q5 design note: surprise without the field

Not a card: the first item of the plan Jonas accepted this morning. Written as
`docs/surprise_without_the_field.md` (+ Word/PDF); no new analysis, every number from a
tracked output. The argument: the surprise family is an operator on a reference
distribution, and with a free reference it reproduces any threshold model (residual
information of exp(-s) is s), so scenario-agnosticism is a property of the reference.
Two references are scenario-agnostic by construction: (A) a predictive model of what
other road users do (the construction of Dinparastdjadid et al. (2023); the library's probabilistic/belief-mismatch
families), and (B) a population distribution of accepted states — under a Gaussian, residual
information is half the squared Mahalanobis distance, so the CZB ellipse's joint percentile
IS surprise with a population reference. (A) is zero by construction where the other agent
behaves normally (the cyclist overtake), so it cannot be the criticality axis alone; it can
define the stimulus ONSET independent of lateral pace, which is one of the two constraints
the pipeline review extracted. Proposed working framing: surprise as onset, population
percentile as level — two references, not one field at two levels. Card Q5.1 (constant-
velocity Gaussian predictor, four pre-stated tests with decision rules, no preference code)
appended to `docs/czb_work_orders.md` for the cheaper tier, to run after review.
@Q5.Q1(judgment, jonas): the two-object framing (world surprise defines when the stimulus
begins; a population-percentile/ellipse level defines the boundary; one operator, two
references) is proposed as the working position for any manuscript, pending card Q5.1. It
gives up "one scalar, two jobs" explicitly. Approve, amend, or reject before Q5.1 runs, since
the card's decision rules are written to that framing.
@Q5.Q2(minor, jonas): the predictor's uncertainty-growth sweep (sigma_1 in 0.5-2.0 m/s) is
motivated by the trajectory-prediction literature from memory and marked unverified in the
note; the card should cite a source or treat the sweep itself as the motivation.
@Q5.Q3(minor, jonas): queue order — Q5.1 does not depend on B.3.v2 or the ellipse note and
touches no shared code; it could run first if the surprise question is wanted settled before
the comparator constructions. The handover queue currently puts B.3.v2 first.

## 2026-09-02 — the CZB ellipse design note, and the animation shot list

Not a card: items (3) and (4) of the plan Jonas accepted this morning. The ellipse note
(`docs/czb_ellipse_design_note.md`, + Word/PDF) reads Jonas's QUADRARUM definition (joint
percentile, (x-mu)^T Sigma^-1 (x-mu) = chi2_{2,0.8}) against what the data can identify:
two populations can be meant (observed states; drivers' boundary levels) and they differ
by his own THW argument; the response model d_s(x) vs a shared per-driver level c_i has a
scale confound between Sigma_s and c_i that the designed stimuli cannot break, so the study
data identify the shape (trade-off; only where a design varies both axes: study 2, LTAP,
CAMP) and the per-driver ordering (already 0.69 of ceiling, field-free), not the absolute
joint percentile, which needs a population reference from naturalistic data. Observables
per scenario tabulated (the B.2/B.3 construction notes own the final choice). The trait
maps on by substituting d_s for the deficit in the stage-1 estimator; the B.4 transfer runs
unchanged in form. Identity with residual-information surprise (half the squared
Mahalanobis distance) links it to the R2.Q5 note. Cards EL.1 (study 2 now), EL.2 (after
loaders), EL.3 (naturalistic) appended to the work orders. The shot list
(`presentation/talk/animation_shot_list.md`) specifies seven data-driven animations (belief
cloud; a button-data crossing; the matched-TTC rows; the lane-gate mechanism; the ellipse
vs conjunction; surprise onset after Q5.1; the glance gate) with sources and conventions,
for a cheaper session to build. No analysis run; suite 191 green; no source changes.
@EL.Q1(judgment, jonas): the QUADRARUM ellipse's "80th percentile across a population of
drivers ... upper 20% of observations" — is the percentile over pooled OBSERVED STATES
(population A, what naturalistic data estimate) or over DRIVERS' BOUNDARY LEVELS
(population B, what stage 1 estimates)? The note assumes A for the shape and B for the
level; if B was meant throughout, card EL.3 becomes a check rather than the deliverable.
@EL.Q2(minor, jonas): until a population reference exists, card EL.2 needs a convention to
pin each scenario's Sigma_s scale; the note proposes design-span normalization and calls it
arbitrary. Accept, or name a better convention.
@EL.Q3(minor, jonas): the CAMP crowdsourced replication (rear-end, last-moment HARD braking
= a dread rather than a comfort boundary; 15 clips, 119 participants) is proposed as the
third dataset for the ellipse's shape question. Is it in scope for this project, given the
standing scope decision that only the active-inference papers are in scope for now?
@ANIM.Q1(minor, jonas): the shot list's build order (S1 belief cloud first, S7 glance gate
last) and whether a clearly-labeled synthetic illustration (S5, the ellipse-vs-conjunction
count) is acceptable on a slide, given the "nothing sketched" rule for the others.

## 2026-09-02 — the B.3.v2 LTAP construction note, and the handover for a less capable model

Not a card: Jonas asked for a handover to a cheaper model and for whatever else was useful
first. Done: the LTAP construction note (`docs/ltap_construction_note.md`, + Word/PDF)
with its geometry script `replication/czb/ltap_geometry.py` → `out/ltap_geometry.md`
(+ csv). Findings from the traces: the ego is the TURNING vehicle (roles by yaw span; the
B.3.v2 card's "ego holds 13.9 m/s" was a mis-assignment, corrected by a dated note in the
card), its script is identical across all 18 traces (turn onset 13.9-14.1 s, 6.5-6.9 m/s
at onset, in the oncoming lane ~15.1-15.7 s), the oncoming runs at 13.9 or 19.4 m/s, so
at matched design PET the time-to-arrival is matched (2.5-6.7 s) and distance differs by
1.4x. Against the Random responses a time-only prediction errs by -0.203 (RMS 0.214); a
distance-only reading (interpolating the 50 km/h curve) reaches RMS 0.078 with signed
error +0.064: distance with a speed residual, i.e. the second axis LTAP is expected to
need. Comparator-class construction specified (arrival-time separation + oncoming
distance at the decision moment; leave-one-PET-out folds; the EL.1 rule); the field
route documented in §3 with pros/cons and not built. Measured PET exceeds design PET by
0.7-1.2 s under a +-1 m conflict band (definition undocumented; orderings unaffected).
Handover: `handover_2026-09-02.md` (the dated record) and `handover.md` rewritten as
the entry point for a less capable model (rules, gating queries, queue, stop conditions).
@B3.Q1(minor, jonas): the Random-design LTAP clip's end time is not recorded in the joint
file (video names are Button-only). The note assumes the Button window (0-13.5 s of trace
time, ending 0.4-0.6 s before turn onset); the B.3.v2 covariates are read at that moment.
Confirm, or give the Random clip window.

## 2026-09-02 — card EL.1 run: a second axis earns its place on the second cut-in study

Card EL.1 (`replication/czb/cutin2_two_axis.py`, pre-registered in its docstring →
`out/cutin2_two_axis.md`, log `out/log_cutin2_two_axis.txt`), run on the day it was
specified: the ellipse note's condition "after EL.Q1" was relaxed for EL.1 only, since its
within-scenario question does not depend on which population the percentile refers to
(EL.2 and EL.3 still wait). Same 288 cells, fit, folds and metric as R.2. Held-out wRMSE:
1D log gap 0.1522 (the registered number reproduced), 1D log TTC 0.1679, linear 2D rule
0.1137, quadratic form 0.1148, CAMP-style quadratic (1/TTC, ego speed) 0.1822; chance
0.3202; noise floor 0.1176 (conservative — repeated trials per participant; pipeline review
§4). Pre-stated rule fired: a second axis EARNS its place (gap minus linear +0.039); linear
and quadratic within 0.01 (−0.001), parsimony keeps the linear rule. The fitted weight on
log gap is 0.47–0.51 in all six folds (full sample 0.497): a one-for-one trade-off on the
log scale, i.e. a threshold on sqrt(gap × TTC), the geometric mean. Within matched-TTC rows
all three covariates order 24 of 24. Two implementation notes: the registered fitter
returns None when every start's objective is NaN (cells exactly at the quadratic form's
corner with sigma → 0), so the script carries `fit_reg`, the same starts and optimizer
with a finite-objective guard, which reproduces the registered 1D numbers exactly; and
model (e)'s ego speed was first defined for two DV levels only (my bug; fixed as
25.0 + DV, the traces' staging) and the script re-run. Dated notes added to the ellipse
note §6, the gate record §4 item 4, and the handover. Suite 191 green.
@EL1.Q1(judgment, jonas): the R.2 headline currently says "simple scene scalars, gap
leading". EL.1 sharpens it: gap leads among single scalars, and an equally weighted
linear rule in log gap and log TTC reaches the noise floor. Should documents and the
decks adopt the two-scalar wording, and should EL.2 carry the linear rule (not the
quadratic form) as the cut-in's form? The notes assume yes to both.
@EL1.Q2(minor, jonas): 0.1137 is below the stated noise floor 0.1176; the floor is an
overestimate (participants contribute two trials to block-1 videos), so the honest
statement is "at the floor". A corrected floor from the per-participant means is a
five-line change to the registered script's floor formula; not done, since that script is
pre-registered — it could go in EL.2's report instead.

## 2026-09-02 — handbook appendix 16: the external required-deceleration CZB analysis

Not a card: Jonas asked for an analysis, in this project's terms, of a colleague's CZB work
(a Summala-like boundary through habitual-control resolvability R_h, cut-in cue a_req =
dv^2 / 2(gap - g_min - dv tau), with a lateral mixture gate) and of another LLM session's
implementation and fit of it to the second cut-in study, reached via the shortcut in
`OthersWork/`; a handbook appendix stating it is early work; and the folder fenced off from
standing context. Done: `docs/handbook/16_appendix_external_rh_model.md` ({{R6}} round;
reading-guide rows for 15 and 16 added; R6 color in the build), `OthersWork/` gitignored
with a comment, a stop condition in `handover.md` §5 and a row in §6, a README row. One
cross-check computed here: `replication/czb/cutin2_external_cue.py` (pre-stated rule) puts
the walled a_req cue on the registered R.2 pipeline: log gap 0.1522, EL.1 linear rule
0.1137, a_req with g_min free 0.1710, with g_min and tau free 0.1951 (walls
9.0-10.1 m); verdict: linear minus best walled = -0.0573: **the linear rule in log gap and log TTC STANDS as the better cue on this pipeline**. A first run had bounded g_min below the smallest design gap (1.1 m; an
implementation slip that forbade the external ~11.5 m wall) and scored the cue at 0.2585 /
0.2534; the bound was corrected to [0, 30 m] and the script re-run with models, folds, fitter
and rule unchanged (both numbers recorded here, per the docstring). The external results were not
re-run. The appendix's substantive reading: both pipelines find gap first with a speed
exponent of about 0.4-0.5 (EL.1's gap/sqrt(dv); their gap/dv^0.42 and free exponent 0.39),
both reject deceleration-type cues for the same reason the pipeline review found for the
field's counterfactual, both find a reliable per-driver criterion; their fixed-horizon
anticipatory gate produces the CP1 floor where our closure-time lane-entry gate cost ~44%
of the field's loss.
@EXT.Q1(judgment, jonas): the two lines of work converge on "gap with a speed exponent of
about 0.4-0.5" by independent routes. Should this be stated jointly with the colleague (a
short joint note), and which functional form should card EL.2 carry for the cut-in: the
EL.1 linear rule, the walled a_req (per the cross-check), or both as candidates?
@EXT.Q2(minor, jonas): the external gate anticipates on a fixed 3 s horizon and gets the
CP1 floor; ours anticipates to the closure time and suppressed the fast-responding cells.
A fixed-horizon variant of `lane_entry_weight` is a small change; it is not made because
nothing in the comparator program depends on the field. Say if you want it as a card.
@EXT.Q3(minor, jonas): the external analysis chose its fold scheme to match our registered
one and cites our R.2 output, so the two are not blind on the fold design. The appendix
says so; confirm that wording is acceptable to the colleague before the appendix circulates.

## 2026-09-02 — three cards in parallel (EL.1b, G.1, F.1) and the status deck

Jonas asked for a 10-15 minute "where we are now" deck (little text, notes carry the talk,
moving illustrations with captions) and allowed other tasks in parallel. Three cards ran as
background agents with pre-stated rules, each in its own script; nothing pre-registered was
modified; suite 31/33/40/96 green (nine property checks added by F.1).

**EL.1b** (`replication/czb/cutin2_looming.py` -> `out/cutin2_looming.md`): the looming
identity. gap x TTC = W / theta_dot (small angle), so EL.1's equal-weight rule is a threshold
on the optical expansion rate. Fitted directly with the traces' width (1.882 m, all traces):
log theta_dot 0.1130 held out (registered folds), EL.1 linear rule 0.1137, gap 0.1522, inverse
tau 1/TTC 0.1679, optical size theta 0.1521; noise floor 0.1176. Pre-stated rule: within
0.005 -> the identity holds numerically. Threshold 0.0336 rad/s (1.9 deg/s); theta_dot over
the cells 0.0036-1.107 rad/s. Note for the literature: on this video paradigm theta_dot beats
inverse tau, the reverse of Xue et al. (2018) in a simulator.

**G.1** (`replication/czb/cutin2_gate.py` -> `out/cutin2_gate.md`, `out/cutin2_gate_states.csv`):
a fixed-horizon anticipatory gate in front of the EL.1 rule, P = b + (1-b) w_gate Phi(.),
w_gate = Phi((m_lat - l0 - ldot t_enc)/s_l), t_enc = 3 s fixed, l0 the edge-to-edge lateral
clearance at the clip end (validated against the study's lateral_dist: median 0.151 m, max
0.434 m), ldot its 0.3 s backward difference. Fitted on the 288 post-onset cells only: held
out 0.1027 (ungated 0.1137); the 90 CP1 cells predicted out of sample at 0.0319 (mean 0.032
vs observed 0.023; ungated 0.4832). m_lat 0.149 m, s_l 0.990 m (per fold 0.05-0.21 m,
0.91-1.03 m); w_gate 0.063-0.070 at CP1, 0.55-1.00 post-onset. Pre-stated rule (i) fired:
the gate is credited, and it improves the open-gate fit rather than costing it. The loader's
y_tar is already ego-relative (centre-to-centre = |y_tar|), stated in the docstring.

**F.1** (`replication/czb/cutin2_field_horizon_gate.py` -> `out/cutin2_field_horizon_gate.md`;
flag `lane_entry_horizon_s` in `src/aidriver/preferences.py`, default None = bit-identical,
frozen-grid test against commit 5062059; `test_lane_entry_horizon`, 9 checks): the field
with the lane-entry projection at a fixed 3 s horizon instead of the closure time. Held out
0.2612 (log) from the registered 0.3471 (reproduced with the flag off); improvement +0.086
> 0.05 -> credited: the closure-time gate was the project's share of the loss, and this is
the first field variant to beat chance (0.320). Against the gap (0.1522): +0.109 -> the field
remains ruled against. Within matched-TTC rows the horizon field orders 7 of 24 like the data
(registered 10 of 24): the gain is on the between-TTC axis, not the within-row axis. CP1
unchanged (pre-onset lateral velocity ~0, so the horizon adds nothing there).

**The status deck** (`presentation/talk/build_status_talk.py` -> `ai_czb_status_talk.pptx`,
10 slides, notes budget 13.0 min; `make_status_animations.py` -> `figures/status_model.gif`,
`status_scoreboard.gif`, `status_trait.gif`, each with captions in the frames, every number
parsed from tracked outputs; the event animation reused). Rendered and inspected; one bug
found and fixed on the way: `load_cutin_trace`'s onset detector fires at t ~ 1.7 s on the
study-2 traces (known; cutin2_field_vs_gap docstring), so the animation takes onset from the
CP1 clip's end stamp + 0.066 s.

Reading, in one line: the cut-in model is now gate x axis x level, with the axis the looming
rate and the gate a fixed-horizon clearance projection; both were suggested by the external
required-deceleration analysis (appendix 16) and both passed pre-stated tests here.
@G1.Q1(judgment, jonas): with the gate credited, should the stage-1 estimator (hierarchical
per-driver level) be re-run on the gated looming rule for the cut-in, and the B.4 transfer
re-scored on it? That would replace the deficit axis in the percentile deliverable (card C's
sensitivity numbers would move). The notes assume yes but nothing is re-run.
@G1.Q2(minor, jonas): the gate's fitted softness (s_l ~ 1.0 m) differs from the external fit
(~0.3 m); the design samples only floor and plateau, so the shape is unidentified either way.
Record only.
@F1.Q1(minor, jonas): the horizon flag stays default-off and undocumented outside the card;
say if the lane-entry note should get a dated section on it (three sentences).

## 2026-09-02 — animation S1 built (the belief cloud)

`presentation/talk/make_belief_animation.py` → `figures/belief_anim.gif` (+ `belief_static.png`), shot S1 of the shot list, run as a background agent; all arrays from the deposit (Exp_7, seed 0). Two findings recorded in the script and the shot list: the deposit's belief columns are the true-state columns shifted by two (b[..., j] = eta[..., j-2]), and the deposited particle weights are uniform (stored after resampling), so marker size cannot carry weight. The believed gap has ~1 mm particle spread (observed, in effect), so the cloud is drawn in believed lead speed × believed lead acceleration: sd(speed) 0.475 → 0.0012 m/s in the one step after the lead brakes, re-plan at 1.4 s, brake at 1.6 s. Referenced from the status deck's slide-2 notes as an alternative; not committed into any deck.

## 2026-09-02 — the concepts deck and the measurement vocabulary

Jonas asked what "the population's median level is 0.032 rad/s" means and what the deficit axis
is, for slides that explain the concepts (with animations, improving on the status deck), and
for a vocabulary in the handbook that makes it easy to understand. Done: handbook chapter 13
gained a section "The measurement vocabulary" (21 terms, each with its meaning first and then
the number or file it is tied to; the reading guide's row updated; chapter rebuilt);
`presentation/talk/build_concepts_talk.py` → `ai_czb_concepts_talk.pptx` (9 slides, 12.1 min in
the notes) with five new animations from `make_concept_animations.py`: the axis (the field's
deficit against the expansion rate on the TTC 2 s stimuli with 2 s and 4 s lane changes, where
the lane-entry gate's effect is visible), the level (study 1's gate-open cells, the population
curve, 43 drivers' thresholds drawn from the fitted population, the 50th/80th percentiles), the
gate (clearance now and 3 s ahead, w rising 0.07 → 1), how we test (leave-one-starting-TTC-out
fold by fold, then the noise floor), and the deliverable (percentile → onset with the level's CI,
from `out/stage1_looming.md` table 5); plus the trait animation. Every number parsed from a
tracked output. Rendered and inspected; two frame fixes (the axis window cut at the clip end,
because after ~2 s the TTC 2 s stimuli reach the ego; the held-out final frame keeps the cells).

## 2026-09-02 — the concepts deck revised on Jonas's review

Jonas's review of the first concepts deck: the axis slide looked as if the deficit were the
better axis (a step reads as decisive), the phrase "gate open" was unclear, the gate slide's
dashed car jumped, the noise floor needed its own popular-science slide before the held-out
slide, the held-out slide's dots and right-hand axes were unexplained, the trait should lead
(after the map) to entice the listener, and the deck should end with the whole model brought
together and one slide on what is next. All done in `build_concepts_talk.py` (13 slides) and
`make_concept_animations.py` (seven GIFs): the axis slide now shows the participants'
intervention rates for the two stimuli next to the two candidates and states the takeaway on
the picture; "after the lane change has started" replaces "gate open"; the gate's projection
is an arrow with the 0.3 s backward-difference closing rate; `concept_noise.gif` (16 people at
a true rate of one half drawn 24 times, then all 288 cells under a perfect model, error 0.118);
the held-out slide names its dots and axes in plain words; `concept_whole.gif` puts gate w(t),
axis theta_dot(t) and the fitted population of levels on study 1's TTC4 clip and draws the
model's share who would intervene against the clip's six observed cells (a fit, not a
held-out prediction, said so in the notes). The deck was written to `-v2` because the first
file was open in PowerPoint. Rendered and inspected.

## 2026-09-02 — card TT.1: the 2013 LTAP/OD test-track study against the video LTAP study

Jonas placed the run protocol of Bärgman, Smith & Werneke (2015, TRF 35) in
`external/02_LTAPOD_DBIN/` with column notes, and the paper in `papers/`; asked for the paper
to be filed and summarized and for the data to be used to test our models against the video
experiment. Filed as `papers/comfort-zone-boundaries/2015 - Bargman Smith Werneke - ... (TRF 35).pdf`
(new section in `papers/README.md`); summary `notes/06_bargman2015_ltapod_testtrack.md`; the
data documented in `external/README.md`. Analysis `replication/czb/ltapod_testtrack.py`
(pre-registered; T4b and T5 added after the first run, both descriptive, said so in the
docstring) → `out/ltapod_testtrack.md`, `out/ltapod_runs.csv`.

Data after the filters (Training ≠ 1; comfort = Broader or Finer; dread = DreadZone; Remove = 1
excluded in the primary analysis): comfort 218 runs / 26 drivers / 112 Go; dread 165 / 26 / 83;
SetPET < 0 on 7 comfort and 28 dread runs (3 and 7 Go). Model: the stage-1 hierarchical
threshold (`fit_stage1_looming.fit_hier_lapse_gated`, gate = 1, level linear on x = −PET),
identical code on both datasets; track response = 1 − Go; video = intervene at 50 km/h.
T1: PET_50 track 2.45 s (SE 0.04), video 2.18 s (SE 0.20), video − track −0.27 s (SE 0.20):
inside the pre-stated 0.5 s → the video paradigm REPRODUCES the test-track comfort boundary.
Sensitivities: Remove runs included 2.20 s; SetPET ≥ 0 only 2.44 s. T2: sigma_pop 0.89 s (track)
vs 1.36 s (video); sigma_resp 0.20 vs 0.86 s. T3: the hierarchical fit on the hurried runs
gives PET_50 0.18 s with lapse 0.28 — not trusted: hurried Go rates are flat (0.4–0.7) across
SetPET 0.4–2.4 s and drivers accelerated (observed − SetPET +0.31 s median on hurried Go runs,
−0.52 s in the comfort condition). T5 replicates the paper from the protocol: observed PET at
the last Go, medians 2.17 s (comfort; paper 2.26) and 1.49 s (dread; paper 1.50), ratio 0.68
(paper 0.69), every one of 26 drivers shorter when hurried; on SetPET the bracket midpoints are
2.60 s and 0.80 s. T4: on Go runs the comfort rating is flat against SetPET (+0.06 z/s; video
−0.40) — selection; T4b with a rating on every run (IfTurnHowComfortable after No-Go): −0.31
z/s (SE 0.085) against the video's −0.40 (SE 0.036), intervals overlap.
@TT.Q1(judgment, jonas): the comparison assumes "Go on the track = not intervening on video".
Confirm the video's LTAP question can be read that way (brake/yield versus turn).
@TT.Q2(judgment, jonas): for the dread boundary, SetPET is not the stimulus the hurried driver
faced (they accelerated); the paper's measure is the observed PET at the last Go. Which PET
should the project's dread boundary live on: SetPET (comparable to the video's design PET) or
observed PET (what the driver produced)? The comfort boundary barely depends on the choice
(2.45 vs 2.17); the dread boundary does (0.8 vs 1.5).
@TT.Q3(minor, jonas): the protocol has 26 participants; the paper reports 22 (two more with
corrupted PET). Were four excluded for a reason that should apply here (e.g. protocol
deviations)? The primary analysis keeps all 26; say if the four highest-numbered should be
dropped and the fit re-run.
@TT.Q4(minor, jonas): the video's PS column runs 0..10 with higher = LESS safe in the joint file
(8.2 at PET 0, 3.5 at PET 4); the data dictionary calls it perceived safety. Confirm the
orientation; T4/T4b assume it.

## 2026-09-02 — G1.Q1 executed (stage 1 on the gated looming rule); B3.Q1 resolved; B.3.v2 run

RESOLVED G1.Q1: Jonas ruled yes. `replication/czb/fit_stage1_looming.py` → `out/stage1_looming.md`
(pre-registered; run 34.9 min; the first run died with its agent at the usage limit and was
relaunched unchanged). Study 1's Random cut-in trials (3096 trials, 43 drivers, 18 cells) with
x = log(theta_dot) at the covariate time (instantaneous, not a running max) and the study-2 gate
FIXED (m_lat 0.149 m, s_l 0.990 m, t_enc 3 s); level linear on the log scale; the deficit axis
refitted on the identical code path. w_gate at C1 0.074-0.083, post-onset 0.37-1.00 (study 2:
0.06-0.07 / 0.55-1.00). LOPO log-likelihood: L-gated -363.0, D-gated -377.9, L-ungated -474.4,
D-ungated -404.9. C1 predictive mean abs error: L-gated 0.030, D-gated 0.034. Both pre-stated
conditions met: **the gated looming axis replaces the deficit axis as the stage-1 primary.**
Level: median 0.0317 rad/s (1.8 deg/s; CI 0.0285-0.0352), 80th 0.0658, 95th 0.132; sigma_pop
0.868 log units. Card C translation on this axis: one 5-point percentile step moves the implied
onset 0.244 s against 0.520 s from the level's own CI (ratio 0.5; on the deficit axis card C had
0.27 vs 0.53) -- estimation uncertainty, not the percentile choice, dominates on this axis; and
TTC8 never crosses at the median, as before. The gate is worth +111 LOPO units on the looming
axis. The transfer (B.4) was deliberately not run on this axis (the overtake does not vary
looming across clearance; EL.2's job). Assumption: the study-1 ego width equals the target's
(1.882 m, from the TTC4 trace).
@G1R.Q1(judgment, jonas): the percentile deliverable now lives on the looming axis (a level in
rad/s, or deg/s). Should `docs/czb_validation_roadmap.md` and the scope map be amended to say so
(dated notes), and should card C's report be regenerated on the new axis as the primary
sensitivity statement? Nothing is rewritten yet.
@G1R.Q2(minor, review): the lapse sd in the L-gated fit is 3.69 on the logit scale with a mean
lapse of 0.004 -- effectively "no lapse for most drivers, a few lapse-prone ones"; the prior
(HalfNormal(1.0) on the logit sd) is being pulled by the data. Record only.

RESOLVED B3.Q1 (by assumption, per Jonas's instruction to proceed): the Random-design LTAP
clip's end time is not recorded anywhere in the study material (the data dictionary says only
that fixed clips "stopped at a fixed timepoint"); the decision moment is taken as 13.5 s of
trace time, the Button window's end, 0.40-0.60 s before turn onset. A different end time shifts
every cell's oncoming distance by the same amount and changes no ordering; `T_DECISION_S` in
`src/comfortzone/ltap.py` is the one number to change.

B.3.v2 run: `src/comfortzone/ltap.py` (roles by yaw span; the loader reproduces
`out/ltap_geometry.md` to 1e-14), `tests/test_ltap.py` (62 checks, one bound widened from the
note's rounded "0.4-0.6 s" to 0.35-0.65 s after the measured lead came out 0.3999-0.601 s),
`replication/czb/ltap_two_axis.py` → `out/ltap_two_axis.md` (pre-stated; 18 cells,
leave-one-PET-level-out, the registered fitter): distance 0.0558, arrival-time separation
0.1121, linear 2D rule 0.0539 (w on -log D 0.81-0.90 across folds), quadratic form 0.0625,
the oncoming's looming rate 0.0540; chance 0.2882, noise floor 0.0325. distance minus linear = +0.0018; distance minus quadratic = -0.0067; linear minus quadratic = -0.0085; distance minus looming = +0.0018. **neither 2D model beats distance alone by 0.01: one axis suffices on this data**; -; **looming and distance are indistinguishable (within 0.01)**.
Cell bootstrap: distance minus linear mean +0.0019, 95% -0.0191 to +0.0282 (52% of resamples favour the linear rule); distance minus looming mean +0.0010, 95% -0.0219 to +0.0239 (50% of resamples favour looming). A
correction to the construction note's section 1 is recorded in the script's docstring: at
matched arrival time the faster oncoming vehicle is farther and looms LESS, so looming predicts
the observed direction (the note said the opposite). The agent that started this card was cut
off at the usage limit after the loader and tests; the comparison script and the fixes are the
tier-1 session's.

## 2026-09-02 — TT.1 extended (transfer, held-out, reliability) and handbook appendix 17

Jonas: skip the dread boundary for now (the manipulated PET is not what a hurried driver faced);
where is the test-track analysis, do the video parameters work on the track, how does the model
perform, are the methods still promising, how large are the differences; write a handbook
appendix. Added to `ltapod_testtrack.py` (pre-stated in the code before running): T6, transfer
with nothing refitted — the video-fitted population applied to the track's Go/No-Go cells scores
wRMSE 0.200 against chance 0.289, the track's own population fit 0.231, and a cell noise floor of
0.108 (many SetPET levels hold 1-5 runs): CARRIES OVER under the pre-stated 0.02 margin; the
reverse (track → video) 0.149 against the video's own 0.039 (the track's 0.2 s within-driver
spread is too sharp for clip judgments). T7, the track model on its own terms: leave-one-driver-
out over 13 drivers (109 runs) log-likelihood −54.3 vs chance −75.9 (+0.20 per run); the
estimator's per-driver level correlates r = 1.00 with the staircase's bracket midpoint and
r = 0.38 with the paper's observed PET at the last Go (22 drivers) — on the track the
staircase already is the measurement; the hierarchy earns its keep on video. Written up as
`docs/handbook/17_appendix_test_track.md` ({{R6}}; reading guide row; combined handbook
rebuilt), marked early results, one scenario. Not tested on the track: the axis (one oncoming
speed) and the gate (fixed decision moment). T3 (dread) stays in the report as run but is parked.

## 2026-09-03 — Jonas's rulings on Q5.Q1, EL.Q1 and EL1.Q1; the axis is scenario-specific and may be multi-dimensional

Jonas, in session: yes to Q5.Q1; percentiles over driver levels for EL.Q1, with "scale
convention" (EL.Q2) not understood and to be restated; on G1R.Q1 he is "still not sure how
generic (scenario agnostic) we can be here — so we do need to define the axis for each
scenario, and it can be multi-dimensional (or?) — why do we not use a multi-dimensional axis
for cut-in, was it not needed?"; yes to EL1.Q1, "but we should keep our mind open to other
(especially multi-dimensionality)".

RESOLVED Q5.Q1: Jonas ruled yes. The two-object framing is the working position for any
manuscript — world surprise defines when the stimulus begins, a population percentile over
drivers' boundary levels defines the boundary, one operator with two references. It gives up
"one scalar, two jobs" explicitly. Card Q5.1's pre-stated decision rules stand as written and
the card is unblocked.

RESOLVED EL.Q1: Jonas ruled **population B** — the percentile is taken over DRIVERS' BOUNDARY
LEVELS, not over pooled observed states. The ellipse design note's split (A for the shape, B
for the level) is superseded: B applies throughout. Consequences, both as the query predicted:
card EL.2 (one level per driver across every scenario's rule) is the deliverable, and card
EL.3 (the observed-state ellipse) becomes a check on it rather than a product. EL.2 remains
gated on EL.Q2, restated below.

RESOLVED EL1.Q1: Jonas ruled yes with a standing caveat. The documents and decks adopt the
two-scalar wording ("gap leads among single scalars; an equally weighted rule in log gap and
log TTC — which is the looming-rate threshold — reaches the noise floor"), and card EL.2
carries the EL.1 linear rule as the cut-in's form. The caveat is recorded as a standing rule
below: no scenario inherits a dimensionality, each one tests for it.

STANDING RULING (from Jonas's G1R.Q1 answer; supersedes any reading of the programme as
axis-agnostic): the *machinery* is scenario-agnostic — gate, axis, level, percentile over
driver levels — and the *axis* is scenario-specific and may be multi-dimensional. Every
scenario runs the EL.1-style second-axis test with its pre-stated 0.01 held-out margin before
its axis is fixed, and a one-dimensional axis is only ever a finding, never an assumption.
The record so far, all from tracked outputs: on the cut-in a second axis DID earn its place
(`out/cutin2_two_axis.md`: log gap alone 0.1522, linear 2D rule in log gap and log TTC 0.1137,
quadratic form 0.1148, noise floor 0.1176; gap minus linear = +0.0386, well past the margin) —
the cut-in axis is two-dimensional, and it is *named* one-dimensionally only because the
fitted weight came out at w = 0.497 across folds (0.474–0.512), at which weight the rule is
algebraically the looming rate: log θ̇ = log W − log gap − log TTC, so equal weights on the two
logs ARE log θ̇ up to a constant. `out/cutin2_looming.md` confirms this numerically — the 1D
looming axis scores 0.1130 against the 2D rule's 0.1137, a difference of −0.0007, with one
fewer free parameter. On the left turn a second axis did NOT earn its place
(`out/ltap_two_axis.md`: distance 0.0558, linear 2D 0.0539, quadratic 0.0625; distance minus
linear = +0.0018, inside the margin), and distance and looming are indistinguishable there
(+0.0018); the cell bootstrap splits 52% / 50%, so this is unresolved on 18 cells rather than
settled. The design is the reason: the left turn holds one oncoming speed per cell, so its two
candidate observables are nearly collinear and the data cannot separate them. Expect the
scenarios that vary two things independently (the truck overtake, card B.2; the cyclist
overtake's clearance against speed) to need two dimensions on their own evidence.

RESOLVED EL.Q2: superseded, not answered — Jonas said the original wording ("a convention to
pin each scenario's Sigma_s scale") did not tell him what was being asked. The question is
live under its new number EL.Q4, restated in plain terms below; the register would otherwise
carry two entries for one id, since the collector does not dedupe.

RESOLVED G1R.Q1: half answered, half renumbered. The generic half is settled by the standing
ruling above (the machinery is scenario-agnostic, the axis is scenario-specific and may be
multi-dimensional). The remaining half — whether the roadmap and scope map get dated notes and
whether card C's report is regenerated on the cut-in's looming axis — is live under its new
number G1R.Q3 below.

@EL.Q4(judgment, jonas): restated from EL.Q2, whose wording proved opaque. Card EL.2 puts
every scenario's axis into one shared population of driver levels, and the scenarios' axes are
measured in different units (rad/s on the cut-in, metres on the left turn, metres of lateral
clearance on the cyclist overtake). Before those can share one population, each scenario's
axis must be divided by something to make the numbers comparable — that divisor is the "scale
convention", the Sigma_s of the note. The note proposes normalizing each axis by the span its
own experiment designed in (the mildest to the harshest cell), and says plainly that this is
arbitrary: it makes the percentile depend on how wide a range the experimenters happened to
choose. The alternatives are (i) normalize by the between-driver spread of levels in that
scenario, which makes a percentile mean "this far out among drivers" in every scenario and is
the choice most consistent with the population-B ruling just made; (ii) normalize by an
external naturalistic spread once such data exist, which is the right answer and is not
available; (iii) keep the design span and mark the deliverable as design-relative. The
recommendation is (i) with (iii) reported alongside as a sensitivity. Accept (i), or name
another.

### Concepts deck v3 — the axis taken apart, and why that quantity

Jonas: "do we have any cognitive or behavioural motivation for the form of the axis? Also, I
think we need a slide in the concept deck that describes the components of the log thetadot
you describe above, and maybe a motivation why". Two slides added after the axis slide, built
to `presentation/talk/ai_czb_concepts_talk-v3.pptx` (15 slides, 10 animated, notes budget
21.4 min). v2's mtime (2026-09-02 22:09) equals its last GIF build, so it had not been opened
since it was built and nothing was at risk; it is left in place and superseded, and v3 is a
new file rather than a rebuild over it (README rule).

New animation `concept_components.gif` (`make_concept_animations.py::make_components_gif`,
run on the LC_dv21_Tlc2p0_TTC02 study-2 clip, the same clip as the axis slide): the left
column plots gap, TTC and the expansion rate over the clip; the right column assembles
log W − log gap − log TTC into the total and puts it on a number line against the fitted
level, which is parsed from `out/cutin2_looming.md` (c = −3.3946, 0.0336 rad/s) rather than
hardcoded. The total is drawn as a marker on a number line, not a fourth bar: log theta_dot
rises toward zero as the situation sharpens, so a bar anchored at zero would SHRINK as
criticality rose, which read backwards in the first build. A black tick shows the exact
W*dv/(gap^2 + W^2/4) that EL.1b actually scored, next to the small-angle total the identity
uses; at these gaps they coincide to within the marker, which is the honest way to show that
nothing rests on the approximation. `signals()` gained `vrel` and `W` in its returned dict
(purely additive; the other seven GIFs are unaffected and were left unrebuilt).

The motivation slide carries three columns and one caveat, all from filed material: (i) the
expansion rate is an optical quantity, available without first estimating distance or speed;
(ii) the active-inference model's own perception stage already observes the visual angle and
its rate with a detection threshold (`src/aidriver/bicycle.py::looming_rate`,
`src/aidriver/agent.py` `use_looming`, `looming_threshold = 0.00215 rad/s`) — its preference
field lost at gate R.2 but its perceptual front end did not; (iii) a threshold on the
expansion rate implies gap ∝ sqrt(dv), and the colleague's independent model fitted that
exponent at 0.39–0.42 against our implied 0.5 (handbook appendix 16.3). The caveat is Xue et
al. (2018), who found inverse TTC the better brake-onset cue in a simulator where this video
paradigm reverses the order (0.113 against 0.168).

### Card TR.1 — the trait slide with the current model; concepts deck v4

Jonas, on deck slide 4: "is it possible to create something like slide 4 but with the current
model (to the extent possible)?" Slide 4 shows a MODEL-FREE quantity — each driver's mean
residual from the cell mean, across four scenarios, no axis and no level in it. TR.1 asks the
same question of the model: one FITTED level per driver per scenario.

`replication/czb/driver_levels.py` (pre-stated in its docstring) → `out/driver_levels.md`,
`out/driver_levels.csv`, log `out/driver_levels.log`. Two scenarios, and the answer to "to
what extent" is **two of the four**: the cut-in (gated log theta_dot, the stage-1 primary
since G1.Q1) and the left turn on video at 50 km/h (−PET; B.3.v2 chose distance for this
scenario and at its single oncoming speed distance is a monotone transform of PET, so the
TT.1 video fit IS the current model here). Excluded by construction, not by choice: the truck
overtake has no axis and no gate (card B.2 unstarted, no construction note), and the cyclist
overtake's per-driver level is not fitted because that scenario's third question is
undocumented in the study's own materials (B.1.Q1). Both exclusions are drawn on the slide
with the reason, since "to the extent possible" is the honest headline.

Method: refit each scenario with the estimator its own card used (nothing re-implemented;
`F.fit_hier_lapse_gated`, and `TT.fit_threshold` which wraps it), then a pre-stated
reproduction gate before any per-driver number is used — mu, sigma_pop and sigma_resp must
match the tracked cards to 0.01. They do: cut-in −3.4520 / 0.8677 / 0.5742 exactly, left turn
2.1843 / 1.3611 / 0.8584 against the card's 2.18 / 1.36 / 0.86, worst difference 0.0043. Then
each driver's posterior-mean level by the same 48×48 Gauss-Hermite reweighting TT.1 uses in
T7. The whole run takes 41 s; no long fit was needed because the hyperparameters were only
being reproduced, not searched for from scratch.

**Result.** 43 drivers appear in both scenarios. Cut-in level median 0.0267 rad/s (10th–90th
0.0113–0.0875); left-turn level median 2.44 s of PET (0.49–3.78). Across drivers the two
fitted levels agree at Spearman **+0.647** (driver bootstrap 95% +0.407 to +0.798), against
**+0.659** (+0.408 to +0.821) for the model-free propensity recomputed on exactly these
drivers and these two scenarios. The model neither loses the trait nor invents it: it recovers
what the raw responses already showed, in physical units. No verdict is attached — the
cross-scenario claim belongs to EL.2.

Deliberately NOT done: the two levels are never put on one scale or pooled into one
population. That is EL.2, and its scale convention is the open query EL.Q4. Every number
reported is a rank statistic and so is invariant to that convention; a Pearson correlation on
raw units is not reported, because it would silently assume the convention EL.Q4 exists to
settle. New animation `concept_traitmodel` puts each strip in its own units with drivers
ranked within their own scenario, cautious driver at the top of both.

Two corrections during the build, both caught by looking at the picture: the strips were first
oriented with "acts late" at the top while the annotation said "acts early" (both are now
flipped so the cautious driver is on top; the Spearman is unchanged, and the plotted ranks
were checked to reproduce +0.647); and the left turn's unit ticks sat under the bundle of
connecting lines, so each strip's ticks now go on its outer side.

Deck built as **`ai_czb_concepts_talk-v4.pptx`** (18 slides, 11 animated, notes budget
27.1 min), not v3: the v3 build raised `PermissionError`, so Jonas had it open in PowerPoint
and the standing rule is to write a versioned copy and say so. v4 is v3 plus this one slide.

### Concepts deck v3, second pass — Jonas's six review points on v2

Jonas reviewed `ai_czb_concepts_talk-v2.pptx` and raised six things. All six are done in
`ai_czb_concepts_talk-v3.pptx` (now 17 slides, 10 animated, notes budget 25.3 min), which also
carries the two slides added earlier today. v2 remains untouched.

1. **The equation's terms.** New slide 3, "Every term in that equation, in one line": one row
   each for share who intervene, lapse, GATE, AXIS, LEVEL, spread and Φ. Three of the six
   symbols had been on the map slide with no gloss anywhere in the deck.
2. **What a cell is** (slide 10, the noise floor). The animation now carries the definition as
   its left-panel heading ("A CELL = one clip, frozen at one moment, answered by 12-24
   people") and the factorial construction underneath ("one speed × one starting TTC × one
   lane-change duration × one freeze point → one cell; this study has 288"). The slide caption
   and the speaker notes say it too; the wording follows handbook chapter 13's definition.
3. **Video format, no scrub bar** (all animated slides). PowerPoint plays an embedded GIF as
   an image: no slider, and pausing restarts it. `save()` now writes each animation three ways
   -- `.gif`, an H.264 `.mp4`, and a `.png` poster of the LAST frame -- and `gif()` in the
   build script embeds the `.mp4` through `add_movie`, falling back to the picture when no
   `.mp4` exists. PowerPoint then supplies its own transport controls. The poster also fixes
   DECK.Q2 below: in normal view a slide now shows the finished picture instead of empty axes.
   `make_status_animations.py::make_model_gif` got the same treatment, since the concepts deck
   embeds `status_model.gif` on its slide 13; the status deck still uses the GIF and is
   unaffected. Verified: 10 of the 17 slides carry a video part.
4. **The percentile lines pulled down** (slide 8, the level). The dashed 50th/80th lines now
   run through the histogram panel as well as the response panel, labelled "50% of drivers ←".
   The two panels already shared an x-axis, so they align by construction.
5. **Slide 12's y-axis** -- "what is zero, and how can it be before the lateral motion starts?"
   Zero is the lane-change onset, and the crossing genuinely is 0.80 s before it at the 50th
   percentile on the TTC4 stimulus. Not a bug: `out/stage1_looming.md` section 5 states that
   the gate is deliberately NOT applied to this crossing, so the curve is the moment the AXIS
   passes the level with the gate ignored. The axis label now says so ("when the axis crosses
   the level, GATE OFF"), zero is drawn as a line and named, the pre-onset region is shaded,
   and a note reads: below the line the car is already growing fast enough for this driver,
   but the gate is still shut, so the model predicts (and participants showed) almost no
   intervention until the lateral motion begins. No number changed.
6. **Test track against video** (new slide 15, animated, placed late as asked). New
   `concept_trackvideo.gif/.mp4` from `make_trackvideo_gif`, every number parsed out of
   `out/ltapod_testtrack.md`: the two paradigms' model-free curves (marker size = runs per
   cell, 1 to 32), then the two fitted populations of per-driver boundaries with medians
   2.45 s track and 2.18 s video, then T6's transfer -- the video-fitted population scored on
   the track's cells at 0.200 against the track's own 0.231 and chance 0.289 -- and the
   sharpness contrast, within-driver spread 0.20 s on the track against 0.86 s on video. The
   notes say what the track does NOT test: one oncoming speed and one decision moment, so
   neither the axis nor the gate.

Three drawing bugs found and fixed while building: `ax.collections.clear()` is not available
on this matplotlib (ArtistList is read-only), so the track scatter is one artist updated by
`set_offsets`/`set_sizes`; the components animation's total was a zero-anchored bar, which
SHRANK as criticality rose because log theta_dot climbs toward zero, and is now a marker on a
number line; and the "θ̇" glyph renders badly in the Chalmers template's font, so the
equation-terms slide names the quantity in words instead.

RESOLVED DECK.Q2: fixed rather than answered -- the poster frame introduced in point 3 above
is the animation's last frame, so every animated slide now shows its finished picture in
normal view. This applies to all ten.

@DECK.Q3(minor, jonas): the concepts deck now embeds ten H.264 videos and the file is
correspondingly larger. If it ever has to travel by email or be opened on a machine without
the codec, the fallback is one line in `gif()` (prefer the `.gif` again). Recording the
trade-off, not asking for a decision.

@DECK.Q1(judgment, jonas): the new motivation slide puts **Xue et al. (2018)** on a slide, but
that citation reaches us only through the colleague's external note, whose references handbook
appendix 16.5 explicitly records as unverified ("from memory"). Nothing else on the slide
depends on it, and it is the one line that would embarrass the deck if the year or the finding
is wrong. Three options: verify it before the deck is shown (a literature check, cheap); drop
the sentence and keep the caveat generic ("simulator studies with real self-motion have found
inverse TTC the better brake-onset cue"); or keep it and mark it on the slide as reported at
second hand. The notes currently say out loud that we have not verified it. Recommendation:
the generic wording now, the citation restored once verified.

@DECK.Q2(minor, jonas): the concept slides carry GIFs, and a GIF's first frame is what shows
in PowerPoint's normal (non-slideshow) view — for this animation that frame is empty axes,
since the curves draw in. The other nine animated slides behave the same way, so this is the
deck's existing idiom rather than a regression, but if you read the deck rather than present
it, every animated slide looks blank. Fixable by drawing the first frame at the clip's start
state instead of empty. Say the word and it applies to all ten.

@G1R.Q3(judgment, jonas): the narrowed remainder of G1R.Q1, whose generic half the standing
ruling above settles. What remains is the paperwork — should `docs/czb_validation_roadmap.md` and
`docs/active_inference_scope_map.md` get dated notes saying that the deliverable is a
percentile over driver levels on *each scenario's own axis* (the cut-in's being the gated
looming rule, a level in rad/s or deg/s), and should card C's sensitivity report be regenerated
on the cut-in's looming axis as the primary statement? Nothing is rewritten yet. Note that
G1.Q1's stage-1 run already carries the card C translation on the looming axis
(`out/stage1_looming.md`: a 5-point percentile step moves the implied onset 0.244 s against
0.520 s from the level's own CI), so regenerating card C is a presentation decision, not a new
result.

### Concepts deck v5 — Jonas's second review pass

Six points, all applied; `ai_czb_concepts_talk-v5.pptx`, 18 slides, 12 animated, notes budget
27.2 min. Slide numbering is unchanged from v4, so his references still resolve.

1. **Slides 9 and 16 were the same bug, and it was mine.** "Slide 9 was better before where
   the dots are added before the rest" and "something is weird with video 16 — it has the
   dots, removes them and adds them again. Why?" The animations were never reordered: frames
   extracted from `concept_level.gif` confirm dots first, histogram last, exactly as before.
   What changed was the POSTER. v3 introduced a last-frame poster, so the slide displayed the
   finished picture and PowerPoint wiped it the moment the video played, because playback
   starts at frame 0. Posters are now the FIRST frame.
   A second defect was found while fixing it: the first implementation called `fn(0)` on the
   live figure, but these frame functions only ADD to their artists and never clear them, so
   the "first frame" poster kept every other artist in its final state — a hybrid still
   matching neither end. Posters are now read from the GIF's frame 0 with PIL, which cannot
   drift from what the video actually shows.
2. **Sarang named** on the motivation slide and in three places in the notes, replacing "a
   colleague": "Sarang's independently developed model, different cue and different fitter".
3. **Title slide rewritten to Jonas's wording**: "Yet another modeling perspective", subtitle
   "Starting with active inference, developing into a gated threshold model of the
   comfort-zone boundary: the concepts one at a time", with the vocabulary sprinkled below in
   varied sizes and tints rather than listed on one line. The model name is mine to defend:
   he left it as "[what we should call this model]", and "gated threshold model" is chosen
   over anything with "looming" in it because his own standing ruling of this morning makes
   the axis scenario-specific — the cut-in's axis is looming, the left turn's is distance, so
   naming the model after one scenario's axis would contradict the ruling. See DECK.Q4.
4. **Slide 4's trait animation**: the topmost (yellow) driver ran off the top of the frame.
   The y-limits were hard-coded at ±2.8 while the largest z-score is 3.14; they now come from
   the data (±1.12 × max |z|). It is also embedded as video now, so it scrubs like the rest —
   `make_status_animations.make_trait_gif` writes .mp4 and a poster, as `make_model_gif`
   already did.

Rebuild note: the animations and .mp4 files were already correct from the earlier run — only
the posters were wrong — so the posters were regenerated directly from the tracked GIFs
rather than re-encoding nine animations for 45 minutes. That is the identical operation
`save()` now performs, so a future full rebuild reproduces them.

@DECK.Q4(judgment, jonas): the title slide now calls the model **"a gated threshold model of
the comfort-zone boundary"**, filling the placeholder in Jonas's requested subtitle. Chosen to
be scenario-agnostic, because his standing ruling makes the axis scenario-specific and
possibly multi-dimensional, so "looming" would over-name it. Alternatives if he prefers:
"a gated perceptual-threshold model" (names the mechanism, slightly more committal about
perception); "a gated threshold model of driver comfort" (drops the CZB term for a general
audience); or his own. One string in `build_concepts_talk.py`.

### Concepts deck v6 — one bug behind five of Jonas's six reports

Jonas, third review: slide 4 "shows all the lines at the same time now"; slide 6 "the right
figure shows the lines up-front, but that should be empty until the progression is shown at
the end"; slide 9 "still shows the histogram and vertical lines directly ... it should be the
blue dots first, then the sigmoid then the lines and the histogram growing"; slide 11 "the
right plot should be empty until it is played out"; slide 5 "is it not better to show the blue
dots first and then the combination of the line and the green dot".

**All five are one bug, introduced when .mp4 output was added.** `save()` called `anim.save`
twice on the same `FuncAnimation` -- once for the GIF, once for the MP4. The second call
replays the frame function from frame 0, but the artists still hold the first pass's final
state, and every frame function in this module only ADDS to its artists and never clears them.
So each MP4 opened with the entire animation already drawn. The GIFs were correct throughout,
which is why the rendered stills checked out while the videos did not -- the still was read
from the GIF and the video was not.

Fix: one render only. `gif_to_mp4()` transcodes the finished GIF to H.264 with ffmpeg and
writes the poster from the GIF's frame 0, so the still, the video and the animation are the
same pixels by construction. `make_status_animations` calls the same helper. `FFMpegWriter` is
gone from both modules.

Verified rather than assumed this time: frame 0 of every .mp4 was extracted with ffmpeg and
compared against frame 0 of its .gif -- mean absolute difference 0.14 to 0.55 grey levels
across all twelve (H.264 quantisation only; the pre-fix status_trait.mp4 opened on all 43
lines under a caption reading "Driver 1 of 43"). Frame COUNTS differ between .gif and .mp4
(e.g. heldout 7 against 112) and that is correct: GIF encoders merge identical consecutive
frames into one of longer duration, and ffmpeg expands them again at 8 fps; total duration is
preserved. Early frames of the five reported animations were then inspected directly and show
the requested order.

Slide 5's requested order was already what the code does (all cut-in dots, then each driver's
line and left-turn dot together); it only looked wrong because of the same bug. Slide 6 also
got the clarification Jonas asked for -- its right panel now reads "what participants ACTUALLY
did / raw response rates, no model of any kind", answering "is it the drivers' actual data?
Any modelling in there?"

Rebuild note: only `concept_axis` needed re-rendering (its right-panel title changed). Every
other GIF was already correct, so their .mp4 and poster were regenerated by transcoding -- the
identical operation `save()` now performs.

### Concepts deck v7 — closing the loop to an ADAS trigger (new slide 3)

Jonas: "the model today predicts 'share who intervene', but what would later then be used in
the ADAS system (e.g. the 80th percentile of what to trigger the ADAS)? Add something about
that as a slide 3 — to close the loop. Does that make sense, or should we place it later?"

It makes sense, and the answer to the placement question is early for the WHY and late for the
numbers. The quantitative version already exists as the deliverable slide (percentile against
seconds, card C's translation) and stays there; the new slide is the four-step chain with no
plot. Placed at 3, as asked. I had suggested putting it after the term-glossary slide because
it uses "level" and "percentile", but on looking at it slide 2 already defines gate, axis and
level, and the glossary only adds lapse, spread and Phi, which this slide does not use — so 3
is right and 4 would have delayed the motivation for no gain.

The chain: FIT (per stimulus, the share of drivers who would intervene — the only thing the
data can check) → INVERT (behind that share, a population of per-driver levels; median 1.8
deg/s, spread 0.87 log units, from `out/stage1_looming.md` section 3) → CHOOSE (a percentile;
named on the slide as a POLICY decision rather than a measurement — the 80th is 3.8 deg/s) →
TRIGGER (gate open and axis above the chosen level; one threshold on a quantity a forward
camera already computes).

The caveat strip is the point of the slide as much as the chain is: this is a method for
setting a threshold, not a calibrated fleet trigger. Forty-three drivers judging frozen video,
and a 5-point percentile change moves the trigger 0.24 s against 0.52 s from the level's own
uncertainty (`out/stage1_looming.md` section 5) — so the estimate, not the policy, is the
bottleneck. That is the honest reading of card C on this axis and it belongs next to the
first mention of a trigger, not only at the end.

19 slides, 12 animated, notes budget 28.8 min. Every slide after 3 shifts by one against v6.

### Concepts deck v8 — the axis slide's trap named, and the gate and noise-floor notes expanded

Jonas: "For slide 3, can you just explain to me what I am seeing. It looks like the top metric
is much clearer than the bottom one for identifying the 'value' or? What am I missing?" and
"Add a bit more explanation in slide 11, but only in the notes. I am not sure I understand it."

**Slide identification.** The description does not fit v7's slide 3 (the new four-panel ADAS
loop, no plot). A top metric against a bottom metric is the AXIS animation — top left the
field's deficit, bottom left the expansion rate — which is slide 7 in v7. His question is
exactly the trap that slide is built around, which means the takeaway was not landing: it only
appears in the animation's last phase, and the on-slide caption merely said "takeaway on the
picture". The caption now states it outright, and the notes answer the objection directly:
the top panel does discriminate more, but the two stimuli differ only in lane-change duration
and participants responded to both at about 0.9, so the field is drawing a sharp distinction
people did not draw. Across all 288 cells that costs it 0.347 against 0.113, floor 0.118.

**Slide 11 is ambiguous** between v7 (the gate) and v6 numbering (the noise floor), and he has
both files. Rather than spend a round trip asking, BOTH sets of notes were expanded — the cost
is a few paragraphs of speaker notes that are read by one person.
  - GATE: what lateral clearance is, how the 0.3 s rate and the 3 s projection combine, why w
    is a probability rather than a switch (fitted softness about a metre), why the horizon was
    fixed in advance rather than tuned, and the reason to believe it — two parameters fitted on
    post-onset cells only, then predicting the 90 unseen pre-onset cells to 0.032.
  - NOISE FLOOR: why the number exists at all (0.113 means nothing without a reference), what
    "at the floor" licenses and does not ("as good as this data can show", not "better than
    perfect"), when to stop modelling and go to new data, why the floor is the reason
    everything is scored held out (an in-sample fit can beat the floor by memorising noise),
    and the caveat that the floor is itself estimated from observed rates.

No new slides and no animation changes; 19 slides, 12 animated, notes budget 29.1 min.

### Handover updated, and the slide-skill additions written (2026-09-03 evening)

Jonas: hand the authors'-handbook review to a more capable model; update the handover for
everything else; and list what should be added to the `chalmers-slide-generation-jonas` skill,
which he will fold in himself this session.

`handover.md` updated in place (it keeps its "written for a less capable model" framing, with
a dated note that a second arc ran the same day):
  - a banner at the top handing the authors'-handbook review to a capable session and pointing
    at `docs/authors_handbook_review_brief.md`, with an instruction not to redo that scan;
  - section 1 now carries Jonas's standing genericity ruling and card TR.1's result;
  - the presentations paragraph now records the deck at v8 and states the three animation rules
    that must not be broken (render once then transcode; first-frame poster taken from the GIF;
    verify the video, not the slide still);
  - section 3's query table rewritten: Q5.Q1 / EL.Q1 / EL1.Q1 marked answered with their
    rulings, EL.Q2 and G1R.Q1 replaced by EL.Q4 and G1R.Q3, DECK.Q1 and DECK.Q4 added, C.Q2
    flagged stale;
  - section 4 gains item 0 (Q5.1 is unblocked and has nothing waiting on it) and EL.2's entry
    now points at TR.1 as the diagnostic already done.

`docs/authors_handbook_review_brief.md` is new and is the handover for the one task NOT in the
queue. It states why a delta exists at all (method_review 2026-08-23 and the authors' edition
2026-08-24 both predate R.2 and everything after), then: candidate 1, the safety term's
counterfactual is violated in nearly every cell of the second cut-in study's regime so the term
tracks absolute speeds rather than the gap (0.33 (m/s)/m of gap against 1.5-2.0 (m/s) per (m/s)
of either speed) with the scope caveat from pipeline-review section 3.3 that this is a verdict
on the term AS A COMFORT CRITERION; candidate 2, the looming perception stage is independently
vindicated by an axis comparison that had no stake in the authors' choices, with the unverified
Xue citation flagged; candidate 3, the lane-entry gate finding, marked explicitly as a property
of OUR gate and not the released one, to be put as a question or checked first. It also lists
what was never read (chapters 10 and 13 of the authors' edition, r2_gate_decisions in full) so
the capable session does not mistake a partial scan for a finished review.

`docs/skill_additions_video.md` is the proposed skill chapter: prefer a moving figure when the
point is a process; font sizes about one step larger than were used today, with a table and an
rcParams block (and a note that the v8 animations are deliberately NOT re-rendered for it);
embed .mp4 rather than .gif; render once and transcode; first-frame poster; verify the video
not the still; drawing rules for build-ups (no zero-anchored bar for a quantity rising toward
zero, no hard-coded limits on derived data, ArtistList is read-only, place annotations against
the FINAL frame); combining-mark glyphs do not render; rebuild economics; and two content
habits (put the takeaway on the slide, pre-empt the obvious objection in the notes).

@SKILL.Q1(minor, jonas): the font-size table in `docs/skill_additions_video.md` is calibrated
by eye from today's figures at 12.8 x 7.2 in, not from a projection test in a real room. If he
has a room and a projector to hand, one slide checked at the back would turn the recommendation
into a measurement.

### Correction: DECK.Q2's recorded resolution was reversed by Jonas, and the register still shows it resolved

Found in an end-of-session audit. DECK.Q2 asked what shows in PowerPoint's normal view for an
animated slide, since a GIF's first frame is empty axes and "if you read the deck rather than
present it, every animated slide looks blank". It was recorded RESOLVED on 2026-09-03 by making
the poster frame the animation's LAST frame.

**Jonas then reversed that**, on the ground that a last-frame poster makes the slide wipe itself
the moment the video is played ("it has the dots, removes them and adds them again"). Posters
are now the FIRST frame, taken from the GIF. So the register's Resolved entry for DECK.Q2
describes a design that is no longer in the code, and the underlying question — a sparse still
in normal view — is live again, now by an explicit decision rather than by oversight.

The collector keys on the first `RESOLVED <id>:` line, so DECK.Q2 stays closed rather than being
re-opened under the same number; the live form is DECK.Q5 below.

**Do not "fix" this by switching posters back to the last frame.** That trade was made
deliberately, in Jonas's favour, after he hit the wipe in the room.

@DECK.Q5(minor, jonas): the poster (what shows in normal, non-slideshow view) is the
animation's FIRST frame, which for most of these is an empty or near-empty set of axes. That is
the deliberate consequence of removing the wipe-on-play. If reading the deck on paper or
scrolling it ever matters more than playing it, the options are: a static PNG of the final frame
placed beside the video on the slide; a duplicate hidden slide carrying the final frame; or
designing each animation so frame 0 already shows the scene at rest rather than empty axes (most
work, best result). Recording the trade-off so no later session silently reverses it.

## 2026-09-03 (evening, capable session) — the authors' edition reviewed against the released code and the post-08-24 findings

Jonas: "go through the author's handbook and verify that all is now correct, and update
anything that we may have learned from working with the model — but we should not go into the
CZB perspective." Started from `docs/authors_handbook_review_brief.md`, then read the whole of
`docs/handbook_authors/aif_driver_model_handbook.md` and checked its code claims against
`external/aica/` line by line where a number or a mechanism was stated. Suite before and after:
31, 33, 40, 96, 62. No source files changed.

**Errors found in the first edition, all against the released code, all corrected in place with
a dated note.**
- *Planner elite set and iterations* (chapter 03, both the component paragraph and Level 2).
  The edition said "refine the best tenth, repeat ~10 rounds". `mpc_discrete.py:47-48`
  transforms the nominal `top_percent` = 0.1 to 0.1^(log 0.5 / log 0.1) = 0.5 and takes
  max(min(50, N/2), ceil(0.5 N)) plans, so 50 of 100 are elite; `iters` = 10 is doubled to 20
  around every `generate_optimal_plan` call (lines 374/379 and 425/431), so a full re-plan is 20
  rounds and the one-step patch (`produce_reference_plan`, H = 1) is 10. The SI's 20 and the
  paper's 10 are both right for different calls (method_review §5 item 8 already had this; the
  edition had not carried it). The internal chapter 03 had the same error; {{R7}} note added.
- *Collision severity factor* (chapter 07 Level 2). The edition wrote max(Δv/10, 0.2);
  `reward.py:299` is 0.2 + 0.8·Δv/10 on the absolute longitudinal speed difference at first
  contact, uncapped (1.8 at 20 m/s). Internal chapter 07 had the same; {{R7}} note added.
- *Safety-margin term's form* was not stated: it is an indicator, 0.5 × g_C × severity floor
  = −1000 per step when a_req < −a_max (8) or the gap closes within t_react, else 0
  (`reward.py:353-357`), and both it and the τ⁻¹ term are multiplied by
  `test_looming_viability(perc=False)` (1.15 widths; `reward.py:239,276,307`). Now stated.
- *Looming threshold*: the fixed 0.00215 is correct, but `decoder.py:170-184` carries a
  distance-dependent threshold (0.00377 at 20 m → 0.00215 at 40 m, asymptote 0.001) that
  `encoder.py:89` computes and line ~100 then overrides with the fixed config value. Dead code;
  noted in Level 2 so the authors know the reading is deliberate.
- *"tens of seconds per timestep"* softened to the measured range (internal chapter 03 {{R2}}).

**Additions from what was learned since 2026-08-24, none of it CZB-framed.** A new tag [Study]
for the project's own analyses (defined in the preamble, and in the edition's README). Chapter 04:
the line-by-line "three files" section from the internal chapter 04 {{R3}} round (no repo paths,
no figure), and a checklist note that the released lateral gates are binary (3 widths perception,
1.15 widths preference) so a partly-in-lane target is all-or-nothing. Chapter 03: the looming
rate as the best single scalar on the second cut-in study (`out/cutin2_looming.md`: 0.113 vs
gap 0.152, size 0.152, 1/TTC 0.168, a_req 0.289, floor 0.118; EL.1 weight 0.497), with the Xue
et al. (2018) caveat. Chapter 05: pre-conflict drift matters little near the conflict
(`docs/crash_causation_results.md` §5: median 0.30 s, half-start over-corrects by ~1 s).
Chapters 06 and 08: beliefs coast through a forced occlusion; the gaze gate blocks observation,
not inference (the CBM comparison left out, per the README's inventory-only rule). Chapter 07:
the safety term's indicator saturation on a cut-in (internal ch. 04: −2112 at both 10 m and
21 m at 30 m/s) and the counterfactual magnitude's absolute-speed ordering
(`docs/r2_pipeline_review.md` §3.2: ~0.33 (m/s)/m of gap vs 1.5–2.0 per m/s of speed), scoped
exactly as §3.3 scopes it, with the ~44% gate share attributed to OUR gate and the gate-free
0.26 quoted (`out/cutin2_lane_gate_diagnostic.md`). Chapter 10: the λ·g_C one-degree-of-freedom
note (method_review §6.1). Appendix 16's external numbers were NOT taken into the edition.

**DECK.Q1 verified, not ruled on.** Xue, Q., Markkula, G., Yan, X. & Merat, N. (2018), Using
perceptual cues for brake response to a lead vehicle: comparing threshold and accumulator models
of visual looming, *Accid. Anal. Prev.* 118, 114–124. It is reference 10 of the Nature
Communications paper's own list (`notes/paper_text/2026 - ...txt` line 2172), and its abstract
(PubMed 29929099; White Rose eprint 131962) states: "For all versions of the mechanistic models,
models using τ⁻¹ as the measure of looming fitted better than those using θ̇", accumulator models
fitted the RT distribution better than pure thresholds, and brake lights improved the fit. The
deck's caveat and appendix 16.3's sentence are therefore accurate as written.

RESOLVED DECK.Q1: the citation is verified against the paper's abstract (details above); the
motivation slide's wording stands, and the citation may now be treated as verified wherever it
appears (deck notes, appendix 16.3, the authors' edition chapter 03). Resolved by verification,
not by a ruling; Jonas may still prefer generic wording.

@AH.Q1(judgment, jonas): the two [Study] paragraphs (chapter 03, the looming-rate result;
chapter 07, the safety term against the raters) put unpublished human-data results in front of
the authors, stated as properties of the model rather than as CZB work. Confirm that these two
should go out with the edition, or cut them and keep only the code corrections and the
released-model findings (three files, coasting beliefs, drift, λ·g_C).

@AH.Q2(minor, review): `src/aidriver/preferences.py::log_collision_pref` docstring (near line
440) says "The released tau^-1 preference has no lateral gate at all -- any vehicle 'ahead'
triggers it". `reward.py:239` computes `looming_viable = test_looming_viability(o, perc=False)`
(1.15 widths) and line 276 multiplies the τ⁻¹ log-preference by it, so the released term IS
laterally gated. Nothing numerical depends on the docstring; not edited under rule 3. Check
and correct the docstring, and check whether `lane_entry_continuous`'s weighting of the τ⁻¹
term was motivated by that reading.

@AH.Q3(minor, jonas): the edition's README used to say "one-off, will not track". It now says
"revised only when a review of the published model warrants it". Confirm, or restore the
one-off rule and keep this revision as the last.

## 2026-09-04 (continuing the 09-03 evening session) — the split-site protocol for working with Volvo Cars without moving the data

Jonas: the naturalistic-data test will run on data at Volvo Cars (VCC) that cannot move; no
common git repository; files by e-mail; VCC's LLMs and ours must both follow the same
structure; VCC must sign off; keep the data pre-processing and ingestion scripts and all raw
data out; make it generic for other projects, "maybe a skill".

**Built.** A skill, `split-site-collaboration` (live in `~/.claude/skills/`, mirrored at
`docs/skills/split-site-collaboration.SKILL.md`), carrying the tool `scripts/bundle.py` and
four templates (policy, interface schema, sign-off document, LLM brief); and its instance here:
- `transfer/transfer_policy.yaml` — the machine-readable rule set (sites, roles, allow/never
  globs, size limits, scanned text types, allowed binaries, forbidden and warning regexes,
  the aggregation rule: min_n 5, forbidden columns, count columns, per-person rows only by
  recorded exception). Status DRAFT until VCC signs; travels inside every bundle; its hash is
  in every manifest.
- `transfer/bundle.py` — make / check / apply / scan / selftest. Make lists what changed since
  a named earlier bundle (or --all), keeps only allowed files, runs the content checks, writes
  the zip with MANIFEST.json (per-file sha256, base sha256, policy hash) and a generated
  REVIEW.md with the steward's tick list and signature line; a violation means no bundle,
  a steward exception is recorded with --override. Apply detects local edits since the
  sender's base by hash (three-way) and stops on conflict. Each site's outbox, inbox,
  manifests and log are never re-bundled. Works without PyYAML (built-in reader for the
  subset; the selftest checks it agrees with PyYAML).
- `transfer/interface_schema.yaml` — the only data shape the shared code reads, derived from
  `docs/data_requirements.md` §3–6 with pseudonymous ids and exclusions (no timestamps,
  positions, vehicle ids, free text). `transfer/validate_interface.py` checks a directory
  without printing rows; `transfer/make_synthetic_fixture.py` writes 12 made-up events
  (`transfer/fixtures/synthetic/`) so the pipeline runs where there is no data.
- `transfer/SITE_LLM_BRIEF.md` — ten rules for the assistant at either site.
- `docs/split_site_protocol.md` (+ .docx, .pdf, 4 pages) — the sign-off document: roles, the
  two layers and the interface, what crosses and what never does, the procedure, traceability,
  the LLM rules, seven decisions VCC is asked to make, change control, signature table.
- `tests/test_transfer.py` — 19 checks (the tool's own 20-check end-to-end selftest counted as
  one; policy parses identically with and without PyYAML; never-paths refused at both sites;
  shared layer allowed at both; content rules at VCC; fixture validates; broken fixtures caught).
  Suite: 31, 33, 40, 96, 62 and 19 green.

**Checked end to end on this repository.** `scan --site CTH` refuses nothing after the policy
was tightened (excluded: `tools/czb_explorer/`, the causation `cond_*.csv` outputs, the
handbook's generated pdf/word folders); a trial `make --all` produced a 15.4 MB zip of 336
files with the policy and the fixture inside and nothing from `external/`, and `check` passed.
The trial's records were deleted (no shipment is made until VCC signs).

**Design decisions to know.** Bundle size is checked on the zip (the e-mail ceiling), file size
on the raw file. PDFs and Word files are refused from the data site (they can embed data);
notebooks and logs from both. Notes across sites go in per-site append-only files
(`docs/notes_from_CTH.md` / `docs/notes_from_VCC.md`) so they never conflict. Per-driver
fitted levels — the trait result — would need a recorded steward exception under the draft
rule; that is deliberate and is decision 2 in the sign-off document.

@SS.Q1(blocker, jonas): VCC's sign-off of `docs/split_site_protocol.pdf` and policy v1,
including the seven decisions in its §8 (min_n; per-driver exceptions; figures; names; extra
path patterns; schema review; retention). Nothing is sent to VCC before this.
@SS.Q2(judgment, jonas): Chalmers's own position on the aggregation rule before it goes to
VCC — min_n 5 is a draft; and whether to ask for per-driver fitted levels as a standing
exception (the trait claim needs them) or to compute the cross-scenario correlation at VCC
and export only the statistic.
@SS.Q3(judgment, review): the shared analysis path does not yet read the interface format —
the loaders read the study traces. Next card (proposed NDS.1): an interface loader in
`src/comfortzone/` that turns an interface directory into the gated-looming pipeline's inputs,
run end to end on `transfer/fixtures/synthetic/` with property checks, so that the first
bundle to VCC is runnable on arrival. Not started.
@SS.Q4(minor, jonas): `tools/czb_explorer/` is excluded from the shared layer (a standalone web
tool with a cache CSV); say if VCC should have it.

## 2026-09-05 — incremental transfer: two defects found by testing a full round trip, and fixed

Jonas asked whether a checksum test should be added so that after the first shipment only
changed files move, or whether git handles it. Git does not and cannot: the two sites share no
history, and each site's commits describe only itself, so nothing in version control can answer
"what does the other site already have?". The tool did already work by content hash — but
testing an actual round trip (`A -> B -> A -> B` with an asymmetric role rule, the home site
able to export PDFs and the data site not) showed the baseline was computed wrongly, in two
ways that a single-direction test could never have exposed.

**Defect 1 — phantom deletions.** `make --since <id>` used that bundle's `tree` as the
baseline. A tree is what its SENDER could export under its OWN role. So when VCC bundled back,
every file only CTH's role may export (all PDFs) was absent from VCC's tree and was therefore
reported as **deleted** — while sitting untouched on VCC's disk. Applied with
`--apply-deletions`, CTH would have deleted its own documents. Reproduced: VCC's return bundle
claimed `docs/report.pdf` deleted.

**Defect 2 — redundant re-sends.** Symmetrically, on the next leg CTH's tree contained those
same PDFs, the baseline (VCC's tree) did not, so they counted as changed and were re-sent on
**every** round trip forever. Reproduced: one file edited, two files sent.

**The fix.** The baseline is no longer any single bundle's tree. It is *derived* by replaying
the manifests of every bundle exchanged with that peer, in both directions — either direction
leaves both sites holding the same content for the files it carried. Deriving it rather than
storing it means the manifests stay the single record and the state cannot drift out of step
with them. Deletions now require the file to be genuinely absent from disk at the sending site.
`--since` survives as an explicit recovery override, documented as *not* for routine use, with
the reason stated.

Two consequences needed their own machinery:
- A bundle made but never released (steward rejects it) would leave the tool believing the
  peer holds those files. `bundle.py revoke <id> --reason "..."` drops it from the replay;
  `make` now prints that reminder every time; revocations live in `transfer/revoked.json`.
- An under-send would be silent. Each manifest already carried the sender's whole exportable
  tree, so `apply` now compares this site against it and lists anything missing or differing
  (`bundle.py drift <zip>` re-runs it). `bundle.py peers` shows the believed peer state and
  what a bundle would carry now.

**Verification.** The tool's selftest grew from 20 to 32 checks, both defects included as
regressions ("a file the sender's role cannot export is NOT reported as deleted", "the
home-only file is not re-sent every round trip"), plus revoke, genuine deletion, and drift both
silent and firing. The real round trip now sends exactly the edited file, claims no deletions,
and the drift check reports the two sites matching. Suite: 19 (transfer), 31, 33, 40, 96, 62.

Documents updated to match: `transfer/README.md` (a section on how the incremental decision is
made and why git cannot make it), `transfer/SITE_LLM_BRIEF.md` (an eleventh rule on revoking an
unsent bundle; the export sequence no longer names a baseline), `docs/split_site_protocol.md`
(new §5a, a seventh procedure step, Appendix B) rebuilt to .docx and .pdf, and the skill plus
its two affected templates. Nothing about what may cross sites changed, so the policy file is
untouched and still version 1: **VCC's sign-off (SS.Q1) is unaffected by this and still open.**

## 2026-09-08 — a 60-minute talk on the published model, following the authors' handbook

Jonas asked for a presentation that describes active inference in the same way and flow as
the **authors' edition** of the handbook, about the Nature Communications paper and that
edition only, reusing what the other decks have, with videos as illustrations wherever they
make it more pedagogic.

**The deck.** `presentation/talk/ai_paper_talk.pptx`, built by `build_paper_talk.py` (which
imports the layout helpers from `build_talk.py`, so the four decks share one set of
conventions). 44 slides, notes budget 54.8 min, following the authors' edition chapter by
chapter: I 01–02, II 03–08, III 09–10, IV 11–12, with chapter 13 signposted rather than
slid. Nothing from the CZB program appears — no gate/axis/level, no R.1 or R.2. The two
`[Study]` findings that edition carries (the looming channel against human intervention
judgments, ch. 03; the glance gate blocking observation but not inference, ch. 08) are in,
labeled ours and unpublished, as that edition labels them.

**Seven videos.** Five new, in `make_paper_animations.py`; two existing GIFs (`event_anim`,
`belief_anim`) transcoded to `.mp4` so they get PowerPoint's scrub bar and a pause that
resumes. Everything that moves is read from the deposit or computed from the released
preference form; the loop's ring is a labeled schematic carrying real per-step deposits.
Every value is regenerated into `presentation/talk/paper_anim_numbers.md` at build time.

Three of the new ones reproduce claims of the authors' edition exactly, which is worth
recording as verification of that edition rather than only as deck-building:
- the maneuver mix by initial speed, from the deposit's own `Analysis_rear_end.xlsx`
  (28 baseline rows): 10 m/s braking 86% / steering 0%; 15 m/s 33% / 54%; 20 m/s 1% / 96%;
  25 m/s 0% / 40% with 58% road departure — the chapter-05 table, to the digit;
- the pre-onset accumulator drift across all 28 baseline conditions, 2.6% of the threshold
  per 0.8 s at the longest gap to 44.3% at the shortest — the chapter-05 range ("from 2%
  … to 44%"), reproduced, and monotone in headway once speed is allowed for;
- the trust cap as arithmetic: the compliant target's tournament spans a 50 000× ratio
  between heaviest and lightest ticket, the violating target's spans 1.0× — the lottery is
  exactly uniform, so the bias does dissolve without any dedicated switch, as ch. 06 says.

**Two chapter-02 numbers did NOT reproduce**, and I have not touched the document. Recomputing
`eps` from the deposit the way `make_event_animation.py` does (Exp_7, seed 0, the negative sum
of the first seven pragmatic components, λ = 10^−5.95):

| quantity | authors' edition, ch. 02 | recomputed here |
|---|---|---|
| deposit per step, quiet following | "about 68 000", 7.6% of threshold | 69 822 at t = 0.6 s, 7.8% (seed 0); 66 480, 7.5% (seed mean); **68 075 on the 8-component sum**, which is the closest match |
| the rising sequence after onset | "68 000 → 197 000 → 267 000" | 69 822 → 130 965 → 196 875 → 249 219 (t = 0.6 … 1.2 s). The 197 000 matches t = 1.0 s; **no variant produces 267 000**, and the quoted sequence skips the t = 0.8 s step |
| account at the lead's braking | "already stands at 0.31" | **0.28** at t = 0.6 s, the last step before onset (0.43 after the onset step); seed mean 0.29 |

The differences are small and do not change any argument in the chapter, so the deck quotes
the recomputed values and the animation writes them to a tracked file. The likely causes are
a different component count (7 vs 8) and whether the onset step is counted, but I could not
find a variant reproducing 267 000 or 0.31 together with the other two.

@TALK2.Q1(minor, jonas): the authors' edition ch. 02 quotes a per-step sequence
"68 000 → 197 000 → 267 000" and an account of "0.31" at the lead's braking; recomputation
from the deposit gives 69 822 → 130 965 → 196 875 → 249 219 and 0.28 (0.43 if the onset step
is included). Should the edition be corrected in a dated note, given it has already been sent
to the authors, or is there a variant I have not found? The deck currently uses the
recomputed values.

@TALK2.Q2(judgment, jonas): the video slides' posters are FIRST frames (forced by the
2026-09-03 wipe rule), so a printed hand-out shows a sparse picture with the caption carrying
the point. If this deck is ever given out to be studied rather than presented, the slide
skill's fix is a companion storyboard slide of stills per video. Want those built?

@TALK2.Q3(minor, review): the deck has no slide-number/email footer, matching `build_talk.py`
and `build_concepts_talk.py` rather than the slide skill's general house convention.

**A trap worth recording for every future deck with video.** On the first build **all seven
videos had no play effect at all** — python-pptx wrote the movie but no `<p:timing>` entry,
which degrades to click-on-object: the clicker would advance and nothing would happen. The
slide skill's `video_click_sequence.ps1` found and fixed all seven, and a second run reports
"already in the click sequence". **It has to run after every rebuild**, because the build
starts from the template again; the README now says so in the build order.

Verification: `check_slides.py` clean (0 off-slide, 0 overrun, 0 invisible — it correctly
caught white-on-accent5 in a provenance chip, now luminance-picked); `measure_render.py` over
a 44-slide PowerPoint render, 0 slides reaching the footer strip (7 did before the video
captions were raised); the seven embedded `.mp4` parts byte-for-byte the size of the files on
disk. Suite: 31, 33, 40, 96, 62.

## 2026-09-09 — card NDS.1: the shared analysis path reads the split-site interface, and the schema does not survive contact with it

Jonas asked what to do next with tokens available. NDS.1 was picked because it is the only
substantial item on the critical path to the naturalistic phase that is blocked by nothing,
and because of a sequencing argument: decision 6 of `docs/split_site_protocol.md` offers VCC
a review of `transfer/interface_schema.yaml` *before* their adapter is written, so any gap in
that schema is cheap now and expensive later. The schema had been derived from
`docs/data_requirements.md` on paper and no analysis code had ever read it. Interactive mode.
Suite green before (31, 33, 40, 96, 62, 19) and after (the same plus 28).

**Built.** `src/comfortzone/interface.py` — the one place that reads the interface shape,
computing the axis and the gate **by the video cards' own definitions**, which is what makes a
level fitted on video comparable with one fitted at VCC: edge-to-edge `gap` as in
`cutin_predictors`; `theta_dot = W*dv/(gap^2 + W^2/4)` through the shared `ltap.looming_rate`,
the exact derivative of cards EL.1b and B.3.v2; `l0`, `ldot` and
`w_gate = Phi((m_lat - (l0 + ldot*t_enc))/s_l)` as in card G.1, with G.1's fitted
`m_lat = 0.149 m`, `s_l = 0.990 m`, `t_enc = 3.0 s` carried over unrefitted. Every constant
carries its motivation in the module docstring; `LDOT_WINDOW_S = 0.3 s` is held at the video
studies' sample spacing *precisely so that* `ldot` is the same quantity the gate was fitted
against, not because 0.3 s is right for 50 Hz data.

**Run.** `replication/czb/nds1_interface_smoke.py` → `out/nds1_interface_smoke.md`, acceptance
criteria pre-stated in its docstring before the run. All four met: the 12 synthetic events load;
every onset yields a finite axis and gate value (gate median 0.980, range 0.940–0.991); the
per-driver order of the recovered levels matches the order the fixture was scripted with
(D03 < D01 < D02); and an event declaring `ref_point = rear_axle` is **refused** rather than
silently mis-computed.

**The finding.** The recovered levels sit 2.6 to 3.4 times *above* the ones the fixture was
scripted with (D01 0.0837 against 0.0300 rad/s; D02 0.1524 against 0.0450; D03 0.0521 against
0.0200). Neither side is wrong: the fixture scripts onsets on a raw centre separation and the
analysis uses an edge-to-edge gap, worth a factor of 1.98 at one worked onset (11.04 m against
15.54 m), with the fixture's 0.2 s reaction delay closing the gap further. The exact-derivative
correction is under a percent. **A level fitted under one gap convention and applied under the
other is wrong by about a factor of two, and nothing in the pipeline would announce it.** That
is the single most important thing to settle with VCC before the adapter exists.

**Five schema gaps, each found by writing the loader against it** (detail in §4 of the report).
They are one action, not five: a revision round on `transfer/interface_schema.yaml` before it
goes to VCC. The schema has not been sent (SS.Q1 holds everything), so this is still free.

@NDS.Q1(judgment, review): the estimator framing. The video paradigm's unit is a design cell —
a frozen clip and the share of raters who would intervene — and naturalistic data has no such
unit: one event, one driver, one realized onset. The module extracts the axis value AT the
onset, with no-response events right-censored at the largest axis value the driver saw, which
makes the NDS estimator a survival/threshold-crossing fit rather than a cell-share fit.
Recommended and implemented, but not settled, and it interacts with EL.Q4: whatever puts the
per-scenario levels on one scale has to accept a censored likelihood from this arm.

@NDS.Q2(blocker, jonas): `ref_point` is one column serving both vehicles, which assumes the
ego and the partner are referenced the same way. In naturalistic data they essentially never
are — ego position from the vehicle's own signals (rear axle or CoG), partner position from
radar or camera (nearest reflecting surface). Split it into `ego_ref_point` and
`oth_ref_point`. Second half of the same query: `rear_axle` cannot be converted to a bumper
position, because the interface carries total length but not the front overhang; either add
overhangs or state that positions are delivered at the vehicle centre. Blocker because the gap
convention is the factor-of-two error above.

@NDS.Q3(blocker, jonas): the lateral frame is ambiguous. The schema calls `ego_y` a "signed
lateral offset from lane center (preferred)" and `oth_y` a "partner lateral position". The gate
needs their *difference*, so both must be in one frame; if the ego's is lane-relative and the
partner's absolute, `l0` is wrong by the ego's own lane offset — which is exactly the quantity
that moves during a cut-in, so the error is largest where the gate matters most.

@NDS.Q4(judgment, jonas): `t_brake_onset` carries no criterion. Since the observation IS the
axis value at that instant, the onset definition sets the level: a pedal-switch criterion and a
deceleration-threshold criterion differ by a few tenths of a second and the gap closes
throughout. Either carry the criterion as a field or fix one in the protocol.

@NDS.Q5(minor, jonas): nothing requires `valid = 1` at the onset sample, so the partner track
may be interpolated exactly where the observation is read. The loader reports `valid_at_onset`;
the exclusion rule should be stated in the schema rather than left to each analysis.

**Housekeeping.** The `performing-research` skill mirror in `docs/skills/` had drifted from the
live copy (an older version entirely); reconciled in this commit, per that skill's own rule that
the next session loading it with the repository present fixes the mirror.

## 2026-09-11 — the authors' reply to the method review, filed

Jonas passed on a reply from one of the Nature Communications paper's authors (writing as
Julian Schumann's co-author), with the instruction: no actions, file it. Filed verbatim at
`correspondence/2026-09-11_authors_reply_to_method_review.md`, with a five-point summary and a
section on where it bears on our documents. In short: in the authors' assessment there were no
errors in the model or the simulations; every flagged item is either a reporting error (a
mislabeled scenario in a figure caption, typos in equations) or an undiscussed limitation (the
evidence-accumulation starting point, the off-road behavior); Julian Schumann will prepare an
official correction; and the analysis is judged free of hallucinated issues but one-sided in
places, the road departures being their example, with an offer to elaborate at ITSC.

**No contradiction with a documented finding of fact, recorded rather than reconciled.** Our
review never claimed a model or simulation error (`docs/method_review.md` §1: the code does what
the paper says and reproduces the deposit to the timestep). The difference is classification and
emphasis. The authors' NB2 bears on two passages already marked [Opinion]:
`docs/method_review.md` §4.1's closing sentence and the 25 m/s paragraph of the authors'
edition's chapter 05. Nothing is changed now, per Jonas; the filed note lists what to add dated
notes to when the correction is published (method_review §4.3 and §8, and the affected passages
of the authors' edition). No query raised for the letter itself, by Jonas's instruction.

**Filing it exposed a defect in the transfer policy I wrote.** A markdown file anywhere in the
repository was eligible for bundling to VCC, the letter included, because the allow lists carry
`*.md` and the matcher treats a pattern without a slash as a *basename* pattern: it matches every
markdown file at any depth, not only root-level ones as intended. Fixed for the letter with a
`never` rule for `correspondence/**` in the home role (draft v1 is unsigned, and the rule only
restricts the home site), pinned by a new check in `tests/test_transfer.py` (19 → 20). Verified:
the letter classifies `never` and no bundle would carry it. Suite 31, 33, 40, 96, 62, 20, 28.

@SS.Q5(judgment, jonas): the data role's allow list has the same `*.md` looseness, and that one
matters more. At VCC a markdown file of per-driver observations in, say, `notes/` would pass the
path check and be protected only by the content scan. The intent was root-level markdown. Two
fixes: list the root files explicitly (`README.md`, `handover.md`, and so on) in both roles, or
add an anchored-pattern syntax to `bundle.py` so `/*.md` means root only. Either changes what VCC
signs, so it should be settled before the policy goes to them with SS.Q1. Recommendation: the
explicit list, since it needs no tool change and reads plainly to a steward.

## 2026-09-11 — the VCC track paused

Jonas: "I feel we can pause the VCC part for now. I will tell you when to make a new round for
VCC." Recorded in handover §4 item 7 (marked PAUSED) and in the handover's do-not-start list, and
in the project memory, so no session resumes it unprompted. The state is preserved as left: card
NDS.1 is done; the next step, when he restarts, is the schema revision on his rulings for
NDS.Q2–Q5, plus SS.Q5. The SS.* and NDS.* queries stay open in the register — parked, not stale,
and not resolved.

## 2026-09-11 — preparation for meeting Julian Schumann at the conference

Jonas will meet the paper's authors next week, primarily Julian Schumann, and asked for (a) the
questions we would like to ask them to take the comfort-zone work, the cut-in and the crash
causation further, and (b) a four-to-five page document of what we implemented, tried, the data
used, and open issues, to give Julian on paper. Written under the `jonas-academic-writing` house
style (US English, readings stated as readings, limitations volunteered).

- **The handout**, `docs/handout_schumann_2026-09.md` (+ .docx, .pdf; 4 pages): why we started;
  the data in one table; what we built; the comfort-zone work (the idea, the two pre-registered
  tests that went against the deficit and the decomposition of the second, the looming result,
  the model as it stands, the trait, the test-track anchor); the cut-in; the crash-causation
  study; eight open issues. Every number was checked against its tracked source before quoting
  (median level 0.0317 rad/s and 1.815°/s in `out/stage1_looming.md`; the 71% between-seed
  variance in `docs/severity_vs_timing.md`; the rest as cited in the handover). The R.2 result
  is scoped as `docs/r2_pipeline_review.md` §3.3 scopes it: a statement about the counterfactual
  *as a comfort criterion*. The review and the authors' reply are deliberately not mentioned on
  paper.
- **The question list**, `correspondence/2026-09_meeting_schumann_questions.md` (+ .pdf; 2 pages),
  private and kept in `correspondence/` because it draws on the authors' letter: a
  fifteen-minute version, an opening, verbal follow-ups to the review and the reply, and
  questions by topic, each cross-referenced to the handout's open issues [H1]–[H8] and to where
  the point is documented. λ = 10^EA_fac was checked in the code (`mpc_discrete.py:62`) before
  it went into a question.
- **A fix to the shared PDF builder**, found by looking at the rendered handout: `build_pdf.py`
  guaranteed a table column fitted its header's longest word but not its body's, so "QUADRIS"
  and "Test-track" broke mid-word. Body words now count too (in the body font, capped at a
  third of the page). Regression check: the protocol, the 31-page authors' handbook and the
  data requirements rebuild to the same page counts as their committed PDFs.

@HO.Q1(minor, jonas): before printing the handout — (1) complete the three references the
repository records only as author-year tags (Bärgman, Svärd, Lundell & Hartelius, 2024; Wu,
Flannagan, Sander & Bärgman, 2025; Wu, Sander, Flannagan & Bärgman, 2026); they show as
"[initials]" and "[to be completed]" rather than guessed; (2) confirm the wording for the two
video studies ("from a related project"), for the colleague credited with the gate idea ("a
colleague's parallel analysis"), and for the naturalistic data ("planned with an industry
partner", not naming VCC while that track is paused).

## 2026-09-12 — the inverse-tau 0.2 is sourced: the handout question to Julian corrected

Jonas asked for plain explanations of eight items on the meeting question list, and pointed at
Markkula et al. (2016), "A farewell to brake reaction times?", as the likely source of the 0.2 s⁻¹
inverse-tau value. He was right, and the handout had it wrong.

**The source is stated in the SI.** SI §2.4, immediately after Eq. 48: "the mean for the normal
distribution over τ⁻¹ … is taken from Markkula et al. [6]", and [6] in the SI's reference list is
the Farewell paper (AAP 95, 209–226). The handout's question [H2] asked Julian where the 0.2 comes
from, on paper, about a value his own SI attributes to a paper Jonas co-authored. Corrected in
`docs/handout_schumann_2026-09.md` (rebuilt, still 4 pages; Markkula et al. added to the reference
list) and in the private list. `docs/method_review.md` §6.1 is not wrong — it says the value is
absent from the paper's Table 1, which holds — so it is left alone.

**What the Farewell paper says**, read from the authors' accepted version on White Rose Research
Online (eprint 102162), text extracted locally, not from search summaries: 116 crashes and 241
near-crashes, cars, trucks and buses. τ⁻¹ = 0.2 s⁻¹ is an *observed demarcation*, not a fitted
parameter — "a rather sharp demarcation at approximately τ⁻¹ = 0.2 s⁻¹" between eyes-on-threat and
eyes-off-threat events. With eyes on the threat, few drivers responded before looming reached it
and most within a second after; drivers who looked back after it was exceeded responded almost
always within 1 s, faster with urgency. The same cut-off appeared at θ̇ ≈ 0.02 rad/s and
v/τ ≈ 2 m/s², results largely unaffected by the measure (less clear for v/τ). The authors read it
not as a fixed threshold but as the transition from slow to fast evidence accumulation, with
responsiveness to looming depending on expectancy, driving style, drowsiness and visibility.
Braking patterns were very similar for cars and for trucks and buses.

**The better question**, now in both documents: the model turns an emergency brake-onset level
into the centre of a *preference*, which reads like a comfort standard; was that intended, and
where does the unattributed spread of 0.125 s⁻¹ come from (the code derives it from the collision
cost, 0.25 / (log₁₀ 10 000 − 2))? A verbal talking point only: our video cut-in level has a
population median of 0.032 rad/s (`out/stage1_looming.md`), the same variable as Farewell's
0.02 rad/s and of similar order, though scenario and response differ.

**Also verified for the explanations**, from the released code: below the looming threshold the
encoder sets the observed expansion rate to 0 with sd 2 × 0.00215 = 0.0043 rad/s; above it the sd
is 0.001 × `perc_noise_factor` 0.01 = 1e-5, a 430-fold drop (`encoder.py`, `simulation_rear_end.py`);
the angle noise is constant in angle units, not scaled by distance (`decoder.compute_obs_dist`);
the gaze factor multiplies the sd before the threshold override, so below threshold a glance
changes nothing and above it 1e-5 becomes 3e-5; vehicle width d = 1.72 m in the rear-end setup.

No new queries. The Farewell PDF was read from the tool's fetch cache and is not filed in `papers/`.

## 2026-09-13 (overnight batch) — four cards from Jonas's questions of 2026-09-12

Batch mode: Jonas went to bed after asking, in one message, whether the Farewell reading changes
our CZB thinking; whether surprise can be taken about the situation as a whole (the automated ego
and the other road users jointly) and used as the start of accumulation, and to test it; for a
progress-dependent cut-in norm proposal and anything that can be tried; whether the perception
switch should be a graded transition from 0.2 inverse tau, and to try it; whether the dormant gaze
system could be switched on and fitted to the real-world glance data of the crash-causation work;
to add the gaze x3 issue to the questions for Julian; to update the handout and his private
question document; and to create a handover. Suite green before starting (31, 33, 40, 96, 62, 20,
28). The VCC track stays paused and was not touched.

### Card HS.1 — situational surprise as the start of the response

`src/surprise/situational.py` (new): one constant-velocity predictor, three references differing
only in what is monitored — `world` (other road users; card Q5.1's reference), `joint` (the ego and
the others, Jonas's "system"), `relative` (the others relative to the ego, the driver's seat).
`tests/test_situational.py`, 27 checks, including closed-form onset latencies and the property that
separates the two holistic forms (two vehicles swerving in parallel are jointly surprising and
relatively unremarkable). `replication/czb/hs1_situational_surprise.py` → `out/hs1_situational_surprise.md`,
`out/hs1_onsets.csv`; rules pre-stated.

**Two design findings before any data run, both kinematic.** (1) A fixed-horizon constant-velocity
predictor only sees a change that leaves its band within one horizon (at most a·h²/2 after a constant
acceleration). Card Q5.1's lowest pre-stated setting (h 0.5 s, σ 0.1 + 0.5h) would need about
5.6 m/s² of lateral acceleration to register a lane change: Q5.1's own expectation of onset "within one
frame" was unreachable with its spread. (2) The study-2 traces jitter: a one-sample velocity leaves up
to 0.89 m of longitudinal prediction error on steady driving; a 0.3 s window leaves 0.065 m. Settings
fixed from those floors: h 1 s, velocity over 0.3 s, σ0 0.1 m primary, sweep 0.05–0.4 m.

**Test A (second cut-in study, 378 cells).** Reproductions exact (ungated 0.1137, G.1 gate 0.1027,
CP1 0.4832 / 0.0319). The surprise gate, with no gate parameter fitted, keeps every pre-onset cell
closed (onset a median +0.27 s after the CP1 clip end in all 90; CP1 out of sample 0.0357, passing
G.1's own criterion), but post-onset it scores 0.1453 at the primary σ0 against G.1's 0.1027:
**A1 NOT CREDITED** (post-onset criterion). Its best case, σ0 0.05 m, has the gate open in every
post-onset cell and ties the ungated rule exactly (0.1137), still 0.011 behind G.1 — so G.1's graded,
anticipatory gate carries information inside the post-onset clips that a step at the manoeuvre onset
does not. A lagging onset costs fast (0.19 at 0.2 m, 0.27 at 0.4 m). Latency after the kinematic
lateral onset at the primary: 0.08, 0.10, 0.17 s for 2, 3, 4 s lane changes. **A2:** world and joint
identical (0.1453), relative 0.1380 — the ego holds its lane, as expected. **A3 STATE THRESHOLD
PREFERRED:** accumulating looming from the surprise onset (x = log(θ(T) − θ(t_on)), the non-leaky
integral of θ̇) scores 0.1955 against 0.1442 for the state threshold, and is worse by 0.016–0.051 at
every σ0. Only this one accumulator form was tested.

**Tests B and C (first study) — a correction after the first run.** The first run applied study 2's
settings to study 1's 10 Hz traces unmeasured. Study 1's positions jitter by about 7% of each frame's
advance against every clock in the files (0.106 m residual sd for the ego at 14.3 m/s), so the
longitudinal floor is 1.2–3.2 m; every reference, world included, "onset" at the first instant of the
search window. Those onsets were jitter and are withdrawn. Rerun with the same three-times-the-floor
rule per axis on study 1's own floor: σ0 0.20 m lateral, 1.75 m longitudinal (effectively blind
longitudinally), velocity over 1 s. Test A was not rerun; its code is unchanged. The module gained a
per-axis spread (`sigma0_lon`) and two checks.

**Test B, cyclist overtake (15 cells):** world surprise never onsets (the cyclist rides steadily).
Joint and relative onset on the ego's pull-out at +1.10, +0.90, +0.70 s for 0.5, 1, 1.5 m clearance —
latest for the closest pass. Participants already intervene at C1 (0.22, 0.20, 0.17), the moment of the
ego's lateral onset, and up to 0.58 at C4 with every gate still closed. **Test C, left turn (18
cells):** no reference registers before the decision moment where every clip ends (world never except
one longitudinal blip at +0.21 s; joint and relative +0.72 to +0.92 s, the ego's turn), yet 11% to 91%
intervene, ordered by PET.

**Reading, marked opinion.** Jonas's scope is supported: surprise about other road users sees nothing
in the overtake or the left turn, so if anything starts the response it has to include the ego. But
kinematic surprise — departure from constant motion — is not what starts it: in two scenarios of three
the responses come before it, and in the third a step at the manoeuvre onset does worse than G.1's
anticipatory gate. What starts the response looks like **anticipated conflict** — the projected
encroachment G.1 computes, or the approach to a known conflict geometry — rather than surprise. The
natural next card is a scenario-agnostic projected-conflict gate (the ego's path against the other road
user's predicted path) on all four scenarios.

@HS1.Q1(judgment, jonas): σ0 = 0.1 m, the "noticeable positional discrepancy", is card Q5.1's value
and three times the measured jitter floor, not a verified perceptual threshold. The verdicts are stated
at it and the sweep shows the cost of moving it; say if a sourced value exists.
@HS1.Q2(judgment, review): card Q5.1 should not run as pre-stated — its spread settings cannot see a
lane change (above), and its tests 1 and 2 are answered, with corrected settings, by HS.1's A4 and B.
Recommend retiring Q5.1 in favour of the projected-conflict card.
@HS1.Q3(judgment, jonas): the interpretation above (anticipation rather than surprise starts the
response) and the proposed next card. It bears on how the CZB model's onset is described in any paper.
@HS1.Q4(minor, review): `comfortzone.cutin.load_cutin_trace` finds the manoeuvre onset at ~1.7 s on the
second study's traces instead of ~15 s: the road runs at a slight angle to world x, every vehicle drifts
~0.02 m/s in `Location_Y`, and the loader's 0.03 m absolute displacement rule fires on the drift. So
`progress` (and `cutin_norm_weight`) is wrong on study 2. No registered comparison uses them; not fixed.
@HS1.Q5(minor, review): the first study's longitudinal positions carry sampling jitter of ~7% of each
frame's advance. Any covariate differentiating first-study positions longitudinally is affected; the
loaders take speed from `Speed_mps`, which is clean, so nothing registered is known to be.

### Card PT.1 — Farewell's looming levels, fixed, on comfort judgments

`replication/czb/pt1_farewell_thresholds.py` → `out/pt1_farewell_thresholds.md`. Card EL.1b's 288 cells,
folds and metric. **Neither carries over:** looming rate fitted 0.0336 rad/s (folds 0.0328–0.0341),
0.1130, against 0.1526 fixed at Farewell's 0.02 rad/s; inverse tau fitted 0.327 s⁻¹ (folds
0.326–0.339), 0.1679, against 0.2242 fixed at 0.2 s⁻¹. Both fitted 50% points sit 1.6–1.7 times
Farewell's. Not part of the decision: the fitted comfort curves reach 25% at 0.0123 rad/s and 0.188 s⁻¹,
so Farewell's emergency brake-onset level sits at about the quarter point of the comfort curve — about a
quarter of raters would already intervene where naturalistic emergency braking begins. Every cell here
is far above the model's own detection threshold (0.00215 rad/s), so this data cannot speak to that
switch; the answer on the switch is a reading (detection versus response), recorded for the documents.

@PT1.Q1(judgment, jonas): the quarter-point reading. Farewell's level is where emergency braking begins
(few before, most within a second after) and our threshold is a 50% point of a judgment on frozen video,
so the comparison is of shape, not of a shared quantity. Confirm the reading may be said to Julian.

### Card PN.1 — a norm for a vehicle changing into our lane

`src/comfortzone/norms.py` (the released own-lane form and the proposed crossing norm), `tests/test_norms.py`
(16 checks), `replication/czb/pn1_cutin_norm.py` → `out/pn1_cutin_norm.md`, `out/pn1_cutin_norm_traces.csv`,
and the proposal `docs/cutin_norm_proposal.md`. **D1:** the own-lane norm withdraws trust a median
+0.53, +0.73, +0.93 s after the surprise onset for 2, 3, 4 s lane changes — it grows with the pace, as
expected. The crossing norm keeps a weight of 1.000 at every straddling moment shown to participants
(only the 2 s and 3 s durations show straddling; the slowest lane changes' clips end before the body
reaches the line). **S1 NOT CREDITED:** the own-lane withdrawal moment as the onset gate scores 0.2883
post-onset and 0.4914 on CP1 (its gate is shut in every CP2 and CP3 cell, so the fit absorbs the
responses there into a lapse near 0.5, which then predicts CP1). **Correction after the first run:**
D1's crossing-norm minimum was first taken over the whole trace after the clip start and came out 0.032,
from the simulator's last seconds after the final clip (stalled frames and a drift back as the ego
catches the target at short TTC, e.g. LC_dv14_Tlc4p0_TTC02 at 18–20 s). Now taken over the shown window;
the whole-trace value is reported beside it.

@PN1.Q1(judgment, jonas): the crossing norm's lower lateral-speed bound, 0.5 m/s (a 3.5 m lane change
slower than ~7 s counts as lingering), is unverified against naturalistic lane-change durations.
@PN1.Q2(minor, review): the older `comfortzone.cutin.cutin_norm_weight` weights straddling by `progress`,
which needs the time the lane change will complete (future information a particle cannot have), and at
its default tolerance never penalizes. Nothing uses it; recommend retiring it in favor of `norms.py`.

### Card GZ.1 — switching the dormant gaze system on (a feasibility probe)

`replication/causation/gz1_gaze_choice_probe.py` → `replication/causation/gz1/gz1_gaze_choice_probe.md`
(part a, 2.0 s headway) and `gz1/thw1.5/gz1_gaze_choice_probe.md` (part b, 1.5 s). Jonas asked whether
the hard-coded "always look at the road" could be switched off and the gaze parameters fitted to the
SHRP2 glance distribution of the crash-causation work. The switch is a one-line change on the
constructed agent (the planner's discrete proposal, `agent.planner.pi`); the authors' files are not
edited. Steady following, lead at constant speed, 15 s, 4 repeats; road_pref = log 0.8 (the SHRP2
baseline's ~80% on-road). Conditions: G0 released noise; G1 perception noise ×100; G2 released noise
with a near-blind glance (multiplier 1000); and, added after the first run, G0c (gaze choice off,
the released configuration exactly) and G0x (the same, with the authors' own scripted lead instead of
this probe's replay class).

**The finding that decides everything else: the released configuration does not hold sustained car
following.** With nothing happening, every released-noise condition starts braking at the same moment
— step 16 (3.2 s) at a 1.5 s headway, step 23 (4.6 s) at 2.0 s — with gaze choice on or off (G0c) and
with the authors' own scripted lead (G0x), and 1–3 of 4 repeats brake to a standstill. With perception
noise ×100 (G1) the car follows steadily at 14–15 m/s. This fits the review's extrapolation
(`docs/method_review.md` §4.2: the accumulator re-plans by itself within 2–7 s at gaps up to 2 s) and
adds what the re-plan does: it brakes. As far as can be found, the released repository never simulates
sustained following (the rear-end runs brake the lead 0.6 s in; `simulation_benign.py` stages an
oncoming pass). The cause of the braking, and why noisier perception suppresses it, is not established.

**Glances.** Under part b's pre-stated validity rule (glances are read only where no repeat brakes),
only G1 qualifies, and it never looks away. The released-noise glance shares (12–16%, near the 20% the
preference encodes) come from cars that are braking and are not interpreted as glance behavior. Two
observations hold regardless of the braking. First, a near-blind glance was chosen about as readily as
a mild one in both parts (15.0% against 15.7% at 2.0 s; 11.3% against 12.3% at 1.5 s), consistent with
the reading that at released noise a glance costs almost no information. Second, every glance lasted a
single 0.2 s step (longest 0.6 s) against a SHRP2 median of 0.75 s: in the code the "attentive" action
returns gaze to the road with probability 1 in one step (`dynamics.py`, B_I_0), so durations cannot
emerge from planning.

**Answer to Jonas's question, stated as a reading.** Not as it stands, and not first as a fitting
problem. Before any fit: sustained following has to be stable; a glance needs a reason (the model has no
competing task, so with realistic noise it never looks away) and a cost that depends on perception noise;
and glance duration needs a mechanism (a non-instant look-back, or a switching cost). Then road_pref, the
off-road multiplier, the noise and a look-back rate could be searched against the SHRP2 share and duration
distribution by simulation. At ~5 s per step on this CPU, one 15 s condition takes 6–17 minutes, so a
grid over three parameters with repeats is days.

**Corrections during the card, recorded in the docstring.** The first part-b note called 1.5 s "the
authors' own benign-following value" and blamed part a's braking on a headway beyond the calibration
table; both were wrong and are withdrawn there. A smoke test also caught, before the long run, that the
first draft recorded the whole planned gaze sequence instead of the executed gaze.

@GZ1.Q1(judgment, jonas): the sustained-following braking is a new observation about the released model
outside its tested regime. It is in the handout as a question for Julian; decide whether it stays before
printing.
@GZ1.Q2(judgment, review): the cause is open. The next diagnostic would decompose the pragmatic value of
the plans at the first re-plan (which term makes braking win) in G0c against G1.
@GZ1.Q3(judgment, jonas): fitting glances to SHRP2 is a model-design task first (a motive to look away, a
noise-dependent cost, a non-instant look-back), then days of simulation. A scope decision whether to
pursue it, and whether to ask Julian first.

## 2026-09-16 — card GZ.2: why the released model brakes during steady car following

Jonas asked what could move things forward with tokens left. Picked GZ1.Q2 because it needs no ruling,
runs in minutes, and he meets Julian Schumann this week. Interactive mode. Suite unchanged (no source
code touched). `replication/causation/gz2_following_braking.py` → `replication/causation/gz2/gz2_following_braking.md`,
questions and readings pre-stated in its docstring (part B added before its runs). The planner's own
bookkeeping is recorded per step (`returns_initial`, `returns_optimized`, `evidence`), nothing edited.
Steady following at 15 m/s, 1.5 s headway, batch 4. The machine was loaded (steps 7–390 s), so the runs
took about two hours of wall time.

**Part A (25 steps).**
- **Q1 — braking is a re-plan decision.** In the released configuration (B0) the evidence reaches 1 at
  step 13 (14 in one repeat) and fires a full re-plan; the new plan eases off one step and brakes at
  3–5 m/s² from the next, with no further re-plan. The braking is written into that one plan.
- **Q2 — the collision-and-safety term produces all of the evidence**, 0.0764 per step. Divided by the
  evidence factor 10^-5.95 that is a shortfall of 68 090 per step, which reproduces the 68 100 that
  `docs/method_review.md` §4.2 read from the authors' OSF deposit for the same condition — two independent
  routes, the deposit and our closed-loop run.
- **Q3 — what the re-plan buys:** +58 000 to +77 000 on collision-and-safety, paid for with speed
  (−1 300 to −3 100), pedal effort (−7 100 to −9 900), lane position (−5 800 to −16 200) and steering.
- **Q4 — perception noise ×100 (B1) acts on the evidence, not the choice:** 0.0029 per step, 25 times
  slower, no re-plan in 25 steps (the threshold would take about 60 s).
- **Q5 — epistemic value plays no part:** B2 (alpha 0) is identical to B0 in every recorded number.

**Part B (14 steps), on part A's open point.**
- **C1**, collision and safety checks removed (inverse-tau preference only): 0.0002 per step. The inverse-tau
  preference contributes nothing; the imagined collisions and failed safety checks are the whole shortfall.
- **C2**, noise ×100 on the three looming channels only: 0.0757, re-plans at step 13–14, like B0.
- **C3**, noise ×100 on the seven state channels only: 0.0023, no re-plan, like B1.
So it is the noise on the state channels that suppresses the spontaneous re-plan. With looming perception
on, the lead's longitudinal state is observed through the looming channels, so the state channels here
are the ego's own position, speed and acceleration and the lead's lateral position and heading. Which of
those carries the effect, and by what route (the planner scores imagined futures on observations sampled
with this noise), is not established.

**Reading, marked opinion.** The spontaneous re-plan the method review predicted from the deposit happens in
the closed loop, and what it does is brake. It is driven entirely by imagined collisions and failed safety
checks in steady following — the same collision-and-safety shortfall our comfort-zone field was built on —
and it disappears when the model's perception of its own state is noisier. So the released perception noise
(factor 0.01) and the evidence accumulator together make sustained following unstable. For the published
results this is invisible, because the lead brakes 0.6 s into every run.

@GZ2.Q1(judgment, jonas): the finding is worth putting to Julian as a concrete version of handout questions
3 and 9; the documents are updated to say it plainly but as our probe, not a flaw. Confirm the wording.
@GZ2.Q2(minor, review): split C3's seven channels (ego longitudinal versus the lead's lateral channels) to
find which carries the effect, and trace the route through the sampled observations. Two short runs.

## 2026-09-16 — Jonas: "go with 1, and then 2"; model switch

Jonas authorized, in order, (1) GZ2.Q2 and (2) card PC.1, then asked for a handover because he is changing
models mid-session. Nothing was run between the instruction and the handover. `handover.md` carries a
"RESUME HERE" banner and §4 items 0a and 0b-now with the exact steps for both.

RESOLVED HS1.Q3: go. Card PC.1, the scenario-agnostic projected-conflict gate, is the next card after
GZ2.Q2 (Jonas, 2026-09-16, "go with 1, and then 2"). The reading "anticipated conflict rather than surprise
starts the response" stands as the working hypothesis PC.1 tests; it is not thereby confirmed.

Note for the next session: `docs/handout_schumann_2026-09.docx` has uncommitted edits Jonas made in Word.
Leave that file alone; ask him before rebuilding the handout from its markdown.

## 2026-09-16 — GZ2.Q2: which state channel suppresses the spontaneous re-plan, and by what route

Interactive mode, new model (Fable 5.1). Suite green before (31/33/40/96/62/20/28/27/16) and after (no source
code touched; the only code change is the card's own script). Parts C, D and E added to
`replication/causation/gz2_following_braking.py`, each pre-stated in the docstring before its runs; the
report `replication/causation/gz2/gz2_following_braking.md` regenerated over all eleven conditions. Steady
following at 15 m/s, 1.5 s headway, 14 steps, batch 4, as part B. Run logs `gz2/log_D1.txt` … `log_E2.txt`.

**Part C, which channels.** C3's seven state-channel scales split into the longitudinal group (`x_sd`, `v_sd`,
`a_sd`: D1) and the lateral-and-heading group (`y_sd`, `theta_sd`, `delta_sd`, `w_sd`: D2). D1 accumulates
0.0748 per step and re-plans at step 13–14 in every repeat, like B0 (0.0764). D2 accumulates 0.0024 per
step and never re-plans, like C3 (0.0023). **The lateral and heading channels carry the whole effect.** A
note on what those scales mean, read from `decoder.py`: they are the generative model's assumed observation
noise, not the world's (the environment's decoder uses them ×0.001), so ×100 does not make the world
noisier, it makes the model expect its lateral senses to be poor.

**Part D, which route.** The scales reach the evidence in two places: the particle filter's likelihood
(the belief update) and the planner's scoring of imagined futures on observations sampled from the same
decoder (`BeliefReward(sample_mean=False)`). D3 installs the ×100 lateral scales in a copy of the decoder
used by the planner only, with the encoder untouched (asserted in the script): 0.0764 per step, re-plans at
13–14, identical to B0 in every recorded number. **The route is the belief update**, not the planner's
sampled observations.

**Part E, the mechanism — hypothesis refuted.** The collision and safety checks in `reward.py` apply only
where the imagined lead is in the ego's path and both cars head the same way; the hypothesis was that a
loosened lateral belief lets the imagined lead leave the path before the check can fail. E0 (released) and
E2 (D2's settings) recorded the belief's weighted lateral spread and the share of particles in the path and
following, per step: **1.000 in both**, lead heading spread 0.000 against 0.020 rad, lead lateral spread
0.000 against 0.002 m. The belief stays in the lane; the exemption is not the mechanism. Reported as
unexplained per the pre-stated reading. One lead in the data: in every suppressing condition the believed
lead acceleration sits higher (B1 +0.14 to +0.16, C3 +0.13, E2 +0.12 to +0.14 m/s²) than in every
non-suppressing one (B0, C2, D1, D3, E0: +0.06 to +0.08), with the truth at 0. With the released lateral
scales (heading 0.0002 rad) against the model's own lateral process noise, the filter's weights are decided
by lateral fit alone, which is a lottery with respect to the longitudinal state; with those scales ×100 the
looming channels decide instead. How that changes the share of imagined futures that fail the safety check
is the open step; it would take recording the effective sample size and the reference plan's unsafe share
per horizon step, another pair of 14-step runs.

RESOLVED GZ2.Q2: the lateral and heading channels (`y_sd`, `theta_sd`, `delta_sd`, `w_sd`) carry the
suppression, through the belief update and not through the planner's sampled observations; the step from a
loosened lateral belief to fewer imagined collisions is not the in-path exemption and remains unexplained.

Documents: one line added to the handout's "Why it brakes" bullet (`docs/handout_schumann_2026-09.md`) and
to the private questions' point 6 (`correspondence/2026-09_meeting_schumann_questions.md`), PDFs rebuilt;
`docs/handout_schumann_2026-09.docx` (Jonas's Word edits) left untouched, its markdown build is the `-v2`
docx. Also this session, on Jonas's request: `docs/software_overview.md` (+ docx, pdf, eight figures), the
software in blocks for jumping into the work, committed separately.

@GZ2.Q3(minor, review): the mechanism inside the belief update — record the particle filter's effective
sample size and the reference plan's unsafe share per horizon step in B0's and D2's settings (two 14-step
runs, ~10 min) — is worth one more part if the finding goes to Julian as more than "the lateral senses";
left undone so that card PC.1 could start.

## 2026-09-16 → 09-17 — card PC.1: the projected-conflict gate, one construction for every scenario

Authorized by Jonas on 2026-09-16 ("go with 1, and then 2"; HS1.Q3 = go). Interactive mode, then
overnight for the runs. Design note first, `docs/projected_conflict_gate_note.md` (+ docx, pdf), written
before any code; construction `src/comfortzone/conflict.py`; property tests `tests/test_conflict.py`
(30 checks; the suite is now ten files, 31/33/40/96/62/20/28/27/16/30, green before and after);
pre-stated script `replication/czb/pc1_projected_conflict.py` → `out/pc1_projected_conflict.md`,
`out/pc1_gates.csv`, `out/pc1_cutin_clearance.csv`. Two corrections to the construction were made
BEFORE any run, both found by the property tests and both dated in the note and the module: the corridor
is the ego's path over an extended span (20 s) while only the other road user's positions are limited to
the horizon (the first draft bounded both, and a cut-in car not caught within three seconds fell outside
the corridor), and the clearance has one ordering by role (the reverse extrapolated the other's lateral
motion beyond the horizon and opened the gate where G.1 leaves it closed). The left-turn prediction under
the planned reading was restated accordingly before the run. One correction was made AFTER the first run
(54 min; report kept as `out/pc1_projected_conflict_run1.md`): the planned path's continuation past the
end of a trace took its velocity from the last two jittered samples, and the cut-in's |cK − cP| check
reached 1.619 m on an ego that drives straight; fixed to the last window's velocity, one property test
added, rerun in full (167 min under load). Every verdict and every number below is identical between the
two runs except that check, 1.619 → 0.598 m (median 0.000 in both; the residual is the ego's real
lateral drift over the 20 s span under the two readings, not verified per cell: PC1.Q6).

**Test 1, the cut-in — CREDITED, by 0.0001.** Implementation check against G.1: median |c − max(l0 +
l̇·3, 0)| 0.000 m, max 0.045 m (rule: median < 0.05, max < 0.20). Post-onset held out 0.1126 against
the bound 0.1127 (G.1's gated 0.1027 + 0.01); CP1 out of sample 0.0356 (G.1: 0.0319); fitted m 0.524 m,
s 0.314 m against G.1's 0.149 / 0.990. The gate is a step: 0.952 in every post-onset cell and 0.000 in
every CP1 cell, identical at every horizon and with or without persistence. Reason: the construction
clamps a projected incursion at zero (overlap is zero clearance), so every post-onset cell, whose
extrapolated lateral clearance is negative, gets the same gate value, whereas G.1's signed extrapolation
grades them (0.55 to 1.00) and that grading is the 0.01 G.1 gains. The cut-in cannot identify the
horizon, as G.1 said.

**Test 2, the left turn — NOT CONSISTENT at any horizon, K or P.** As predicted before the run, K
(constant velocity) is closed in all 18 cells at every horizon: the ego's projected path at the decision
moment is straight and the oncoming car never enters it. P (the recorded future) opens in 2, 6, 9 and 14
of 18 cells at 3, 4, 5 and 6 s: exactly the cells whose oncoming car reaches the ego's planned crossing
within the horizon (its arrival is 2.9 to 7.1 s after the decision moment across the design). Engaged
cells (share ≥ floor + 0.2, 13 of 18): 2, 6, 9, 12 open. Cost of gating B.3.v2's distance rule
(ungated 0.0558): +0.232 at 3 s (chance is 0.288), +0.113, +0.055, +0.024 at 4, 5, 6 s. KP equals P
throughout. The left turn's response starts while the oncoming car is still five to seven seconds from
the crossing, so a three-second projected conflict is closed where people respond, and lengthening the
horizon toward those arrival times opens the gate everywhere, where it does no work; what carries the
left turn is the axis (distance), as B.3.v2 found.

**Test 3, the overtake — consistent, trivially.** Under every reading and horizon the gate opens at the
first evaluated moment (9.0 s before C1, the window's start plus the velocity window) in all three
clearances: the cyclist ahead in the lane is on the ego's straight path. Open (0.952) in all 15 cells;
the instantaneous clearance grows through the pull-out (0.00 → 0.62 m under K at 1.5 m C5) and
persistence keeps the gate open, as designed. The gate does no work in the overtake.

**Adoption (pre-stated rule): none.** No reading is credited on the cut-in and consistent on both other
scenarios at the primary horizon, nor at any horizon in the sweep. **The finding, marked opinion:** a
projected-conflict gate with one fixed horizon, computed identically in every scenario, is not the
scenario-agnostic onset. HS.1's reading that anticipated conflict starts the response survives
qualitatively in each scenario, but what is anticipated differs: a lateral incursion within about three
seconds on the cut-in, presence in the lane ahead on the overtake, an arrival five to seven seconds away
on the left turn. Either the gate's horizon is scenario-specific, which under Jonas's genericity ruling
makes it like the axis (generic machinery, scenario-specific parameter), or the gate is needed only where
the other road user does not count from the outset (the cut-in), and elsewhere the axis alone carries the
response. On the evidence in hand the second reading is the simpler.

RESOLVED HS1.Q3 (follow-up): the strong form, one fixed-horizon construction for all scenarios, is
falsified by the left turn; the weak form, that anticipation rather than surprise starts the response,
stands in every scenario.

@PC1.Q4(judgment, jonas): which reading of the result to carry forward — a scenario-specific horizon
for the gate (like the axis), or G.1's gate on the cut-in only with no gate where the other road user
counts from the outset? The handbook's chapter 13 says "the gate is the part that changes between
scenarios"; the result sharpens that to "and it is a step at the scenario's own anticipation horizon".
@PC1.Q5(minor, review): the construction clamps a projected incursion at zero; a signed clearance
(penetration depth) would restore G.1's graded post-onset gate and its 0.1027. Worth one addition only
if the construction is kept.
@PC1.Q6(minor, review): |cK − cP| max 0.598 m on the cut-in after the fix, median 0.000; the residual
is presumably the ego's real lane-keeping drift under P against a constant lateral velocity under K over
the 20 s path span; which cells, not checked.
The three design queries of the note, restated here so the register carries them:
@PC1.Q1(judgment, jonas): the planned reading P uses the ego's recorded future as "what the participant
knew the automated car would do"; is that an acceptable reading of the study instructions, or did
participants only know the scenario type? It matters less now that no reading was adopted.
@PC1.Q2(judgment, review): persistence (once counted, keeps counting) was added here, not in G.1; harmless
on the cut-in, decisive on the overtake as designed. A decay is the alternative; no data on file
distinguishes them.
@PC1.Q3(minor, review): the engaged-cell margin of 0.2 above the scenario's floor is a convention; the
left-turn verdict is the same at 0.1, 0.2 and 0.3.

## 2026-09-17 — Jonas: anticipation as a latent variable, or as an exposure-driven component? (assessment, not a card)

Jonas, after card PC.1: should the model include "either a latent variable for the anticipation, or
actually include the fact that drivers adapt over time (with anticipation) as a separate
component/variable", on the reasoning that participants repeatedly exposed to critical clips may learn an
unnatural anticipation that, trained on naturalistic data, would not be activated. No code run; the
assessment rests on results already on file. Marked opinion throughout.

What is on file. (1) Repeated exposure moves responding: in the second cut-in study every block-1 clip is
shown twice, and P(intervene) rises from 0.547 to 0.575, +0.027 (SE 0.007) over 3 456 pairs
(`out/cutin2_scope.md` §4). Whether that rise sits in the pre-onset cells (anticipation) or across all
cells (a criterion shift) was never split. (2) Study 1 cannot see it: the within-session order slope is
+0.005 with a 95% interval of about ±0.10 (`out/response_style_and_anticipation.md`, test B). (3) The
pre-onset floor is largely a person trait (+0.546 across cut-in and overtake, 61% of the reliable
signal; same file, test A). (4) Exposure per participant is heavy in study 1: each left-turn clip four
times (172 trials over 43 people), over two sessions, and the Button design always after the Random one.
(5) The one real-driving comparison, card TT.1, puts the video left-turn boundary 0.27 s more cautious than
the test track (SE 0.20), with drivers four times sharper in the car.

Assessment given. The exposure-indexed component is the better of the two, for the reason Jonas gives: it
has a value the naturalistic setting fixes (zero within-study exposure), whereas a free latent anticipation
trait has no such anchor and is hard to separate from the level on a monotone axis. Two conditions make it
sound. First, index it by exposure within the experiment (showings of the clip, trials of the scenario
type), not by the base rate of critical events; drivers' lifetime experience is legitimate anticipation
the deliverable should keep. Second, identify it only where exposure varies independently of the
stimulus: study 2's first against second showing is the clean case; study 1's session index is confounded
with design. Where it would enter the model depends on a split not yet made: if the repetition effect is
concentrated pre-onset, it belongs in the gate (it opens earlier with exposure); if it is uniform across
onset times, it belongs on the level or the lapse. The effect on file is small (+0.027), so it should be
costed in seconds of trigger onset before it is built, as card C did for the percentile. It bears on PC.1
too: the left turn's early responding could be partly learned, since each clip was seen four times.

Proposed first step if Jonas takes it up (not started): split study 2's repetition effect by onset time
and by driver, pre-stated, data in hand, minutes to run; and the same first-against-later-showing contrast
on the study-1 left turn's far cells, where the gate should be closed.

## 2026-09-17 — card EX.1: where repeated exposure acts, and whether it is a learned anticipation

Jonas: "Please run what you propose as cheap first step." Interactive mode, Claude Opus 5. Pre-stated in
`replication/czb/ex1_exposure_split.py` and committed before the run (`bbe8037`); report
`out/ex1_exposure_split.md`, per-driver values `out/ex1_driver_exposure.csv`, log `out/log_ex1.txt`
(39 min, almost all in part B's refit bootstrap). Suite green on all ten files (no source code touched).

**A correction to how an old number was read.** The +0.027 repetition effect in `out/cutin2_scope.md`
was computed on post-onset cells only (`post = d[d.CP != "CP1"]`), reproduced exactly here (3 456 pairs,
0.547 → 0.575). The worklog of 2026-08-28 and my assessment of 2026-09-17 read it as the overall effect.

**Part A, the cut-in (144 participants, 5 184 first/second-showing pairs).**
- A1: before the lane change starts (CP1) repetition changes nothing: 0.023 → 0.024, +0.001
  [−0.011, +0.013], 77 discordant pairs (enough to identify it). After onset: +0.027 [+0.010, +0.045],
  largest at CP4 (+0.045). Log-OR contrast CP1 against post-onset −0.29 [−0.86, +0.30]. **Pre-stated
  reading: R2, exposure acts uniformly (a criterion shift on the level or lapse), not on the gate.** In
  probability terms a learned pre-onset rise above about 1.3 points is excluded at a 2.3% base rate.
- A2: neither clip familiarity (+0.005 at zero lag) nor general practice (+0.064 per session, interval
  includes 0) is reliable post-onset. Reported without a verdict: on CP1 pairs the slope is −0.041
  [−0.084, −0.001], so the little pre-onset change there is shrinks with the gap between showings.
- A3: the per-driver repetition effect (mean +0.027, sd 0.107) has split-half reliability 0.352, under the
  pre-stated 0.5: **a population-level term only.**
- A4: card G.1's gated rule refitted on first showings and on second showings gives threshold −2.138
  and −2.052 (+0.086), which reads as *less* responding on the second showing, against A1. **Not
  interpretable as stated:** the fitted axis weight also moved (0.559 → 0.473), so the two thresholds are
  on different axes. The pre-stated guard withheld the looming-rate conversion but not the raw shift.
  m_lat, s_l and sigma barely move (0.158/0.138 m, 1.000/0.979 m, 0.699/0.695). EX1.Q2.

**Part B, the left turn (43 participants, 18 cells × 4 showings over two sessions).**
- B1: responding *falls* with exposure, by about the same amount in every distance band: last minus first
  −0.093 (near), −0.093 (mid), −0.089 (far), −0.092 overall [−0.133, −0.050]. Almost all of it is at the
  session boundary (showing 2 → 3: −0.065 [−0.094, −0.036]); within session 1 −0.034, within session 2
  +0.006.
- B2: the distance rule's boundary moves from 87.4 m to 77.4 m (ratio 0.885 [0.827, 0.958]); at 50 km/h
  that is 6.3 s to 5.6 s of the oncoming car's travel, at 70 km/h 4.5 s to 4.0 s. Sigma does not change
  (ratio 0.967 [0.782, 1.190]). **Pre-stated reading: L3, a general criterion shift** — toward *less*
  caution, not more. Not a learned anticipation (L1 needed far-band responding to rise; it fell).
- B3: neither familiarity nor practice within sessions is reliable (−0.019 at zero lag, +0.015 per
  session).
- B4: per-driver change (mean −0.078, sd 0.091) has split-half reliability 0.346: **population-level
  only.**

**Reading, marked opinion.** Jonas's proposal is tested in its specific form and not supported: there is
no sign that repeated critical clips teach a pre-onset anticipation, in either scenario. What exposure
does is shift the criterion a little, at the population level, and in opposite directions: the cut-in
drivers intervene 2.7 points more on a second showing within one session; the left-turn drivers
intervene about 9 points less across a session boundary days later, with the boundary distance 12%
shorter and no change in sharpness. The left-turn change is confounded with the session (a different
day) and cannot be attributed to exposure alone. Two consequences:
1. **For PC.1.** The left turn's long anticipation horizon is not learned from repetition. It is
   *largest* at the first showing (boundary 87 m, 6.3 s of the oncoming car's travel at 50 km/h) and
   shrinks with exposure. So the scenario-specific horizon of PC1.Q4 is a property of the scenario as
   first seen, not a lab artefact of repetition.
2. **For naturalistic transfer.** If an exposure term is kept, it belongs on the level (or the lapse),
   population-level, and its natural setting is "first exposure". The simplest equivalent is to fit on
   first showings only, or to carry a showing/session covariate on the level and set it to the first
   showing when predicting real driving. On the left turn that choice moves the boundary by about 10 m
   (0.7 s at 50 km/h), which is larger than TT.1's video-to-track offset of 0.27 s, though on a
   different quantity (distance at the decision moment, not post-encroachment time), so the two are not
   compared.

@EX1.Q1(minor, review): the 0.5 split-half reliability bar for a per-driver exposure parameter is a
convention; both scenarios fall at 0.35, far enough below that the verdict would survive 0.4.
@EX1.Q2(judgment, review): A4's threshold comparison is invalid because the axis weight is refitted per
showing; refit the second showing with the first showing's weight fixed (or fit both jointly with a
shared weight and a showing shift on the threshold) to get an interpretable size. The pre-stated guard
covered the conversion but not the raw shift; flagged here, not reinterpreted.
@EX1.Q3(judgment, review): the left-turn change sits at the session boundary, so exposure and session
(day, fatigue, instructions) are confounded in study 1; the cut-in study has one session and cannot
help. Any exposure term fitted on study 1 carries that confound.
@EX1.Q4(judgment, jonas): given no learned anticipation but a population-level criterion shift with
exposure, should the level fits use first showings only (or carry a first-showing setting for
naturalistic prediction)? It moves the left-turn boundary by about 10 m and the cut-in intervention rate by
about 3 points; stage-1 and TR.1 fits currently pool all showings.

## 2026-09-17 — card EX.2: the level fits with a shared exposure term, reported at first exposure

Jonas: "Do as you propose" (the middle route of the session: measure the effect on study 1's cut-in
first, then keep all data, add one shared exposure term on the level, report at first exposure).
Pre-stated in `replication/czb/ex2_first_exposure_levels.py`, committed before the run (`08e7c8d`);
report `out/ex2_first_exposure_levels.md`, per-driver levels `out/ex2_driver_levels_first_exposure.csv`,
log `out/log_ex2.txt` (10 min). No pre-registered script or its output edited. Suite green on all ten
files.

- **Step 1, the count on study 1's cut-in** (the data stage 1 uses). Session 2 minus session 1: pre-onset
  −0.008 [−0.047, +0.031], post-onset +0.027 [−0.010, +0.066], pooled +0.021 [−0.012, +0.056]. Rule N:
  NOT SHOWN NEGLIGIBLE (the interval crosses +0.03). Same direction and size as the second cut-in study's
  post-onset +0.027; again nothing before onset.
- **Step 2, reproduction gate.** Stage 1 reproduced exactly; TT.1's video fit to 0.0043 s. Proceed.
- **Step 3, recovery gate.** A synthetic session shift of +0.300 on the left-turn design came back as
  +0.275 (SE 0.092); mu within 2 SE. Proceed.
- **Step 4, the session term.** Cut-in: beta −0.145 [−0.237, −0.052] log rad/s (drivers respond at a
  lower looming rate in session 2). The first-exposure median level is 0.0341 rad/s against 0.0317
  pooled; 80th percentile 0.0709 against 0.0658. The median's implied trigger onset moves +0.136 s later
  at first exposure, about half of stage 1's 0.244 s per 5-point percentile step. Left turn: beta +0.476
  [+0.290, +0.663] s (a shorter accepted PET in session 2); PET_50 2.422 s at first exposure against
  2.184 s pooled and 1.946 s in session 2. The showing-index sensitivity fits agree in sign and implied
  first-showing level (cut-in mu −3.363, left turn −2.485). Negative log posterior falls by 4.7 (cut-in)
  and 12.5 (left turn) with the one added parameter. **Rule A: first exposure is primary in both
  scenarios.**
- **Step 5, TR.1 again.** Oriented Spearman between the two scenarios' per-driver levels at first
  exposure +0.642 (bootstrap +0.394 to +0.798) against +0.647 pooled. Driver ranks are unchanged
  (+1.000 cut-in, +0.995 left turn), as a shared term should leave them.

**Reading, marked opinion.** Exposure moves the level in opposite directions in the two scenarios, as
EX.1 found: repeated cut-ins make drivers intervene earlier, repeated left turns make them accept tighter
gaps. At first exposure the cut-in boundary is slightly less cautious and the left-turn boundary more
cautious than the pooled fits said. The trait result does not depend on the choice. **Not pre-stated,
arithmetic on committed numbers only:** TT.1's test-track median is PET_50 2.45 s (SE 0.04); the video
median moves from 2.18 s pooled (offset −0.27 s) to 2.42 s at first exposure (offset about −0.03 s). So
the video-to-track gap on the left turn is almost entirely the session-2 shift. The track drivers also
made repeated runs, and the paper reports no order effect in its four preset runs; exposure and session
(day) remain confounded in study 1 (EX1.Q3).

**What this changes on paper, not yet done.** The quoted deliverable numbers (handover §1, handbook
chapter 13 and appendix 17, the concepts deck) are the pooled ones: cut-in median 0.032 rad/s, 80th
percentile 0.066 rad/s; left-turn video 2.18 s and the −0.27 s offset. Card A.1-style rule: dated notes,
no rewrites without Jonas.
EX1.Q4 is answered by Jonas's instruction and this card:
RESOLVED EX1.Q4: keep all showings and carry a shared session term on the level, reported at the
first-exposure setting (Jonas, 2026-09-17, "do as you propose"; card EX.2, Rule A first exposure primary
in both scenarios).

@EX2.Q1(judgment, jonas): the deliverable's quoted numbers move (cut-in median 0.032 → 0.034 rad/s,
80th 0.066 → 0.071; left-turn video PET_50 2.18 → 2.42 s, and the video-to-track offset −0.27 → about
−0.03 s). May dated notes be added to handbook chapter 13 and appendix 17, and should the concepts deck's
numbers be updated? The decks may carry your hand edits.
@EX2.Q2(minor, review): the video-to-track comparison at first exposure is arithmetic, not a refit of
TT.1 with the session term; a proper version would refit TT.1's comparison with the term and propagate
both SEs.
@EX2.Q3(minor, review): the cut-in count (step 1) is not reliable on its own while the model's beta is;
the model uses trial-level covariates and driver effects, so it has more power. Both are reported.

## 2026-09-17 — Jonas requested access to highD and inD; a plan for both programs

Jonas asked for a plan to use highD and inD for the comfort-zone work and to assess the published model.
Written as `docs/naturalistic_data_plan.md` (+ docx, pdf); no data touched, no card authorized. Dataset
facts come from the levelXdata pages (highD: about 110 500 vehicles, preceding/following ids, THW, TTC,
lane-change annotation; inD: about 8 200 vehicles and 5 300 pedestrians and cyclists at four intersections,
OpenDRIVE and Lanelet2 maps; both non-commercial, no redistribution, no driver identity across
recordings). inD's frame rate and signalization are not on its page and are checks on download.

The plan revisits `docs/data_requirements.md` §9's verdict on drone data ("distributional calibration
only; no onsets"): the inD left turn needs no onset (gap accepted or rejected), the deliverable is a
population percentile that needs no driver identity, and two open questions (EX.2's first-exposure
setting; the released model's instability in steady following, GZ.1/GZ.2) are naturalistic by nature.
Cards: NC.0 ingest, conventions and jitter floor; NC.0b a validated deceleration-onset detector with a
stop rule; NC.0c census with per-card minimum counts. Comfort-zone program NC.1 (inD left-turn gap
acceptance against video first exposure 2.42 s, pooled 2.18 s and track 2.45 s; recommended first),
NC.2 (distance against time with natural speed variation), NC.3 (the video-fitted cut-in level predicting
highD follower responses), NC.4 (anticipation horizon per scenario, for PC1.Q4), NC.5 (free following
against the field's boundary), NC.6 (real cut-ins against the study-2 design space). Paper program NM.1
(the released model on replayed highD following; recommended first, overnight compute), NM.2 (the
calibrated following preference against real following, same computation as NC.5), NM.3 (response time
against urgency on lead decelerations), NM.4 (priority-road behavior at inD intersections, feasibility
first). The opposite-direction lateral incursion is not testable with either dataset.

@NAT.Q1(judgment, jonas): mapping video "would intervene" to a highD deceleration onset beyond baseline and
to an inD rejected gap.
@NAT.Q2(judgment, jonas): route highD cut-ins through the split-site interface schema as a dry run of the
paused VCC pipeline, sending nothing to Volvo Cars?
@NAT.Q3(judgment, jonas): who sees results about the published model, and when (authors' reply of
2026-09-11; the meeting with Julian Schumann).
@NAT.Q4(judgment, jonas): priority if time is short; recommended NC.1 first for the comfort-zone work and
NM.1 first for the paper.

Jonas's answers on the naturalistic plan, 2026-09-17, folded into `docs/naturalistic_data_plan.md` (§1, §2
NC.0b, §5, §6; docx and pdf rebuilt):

RESOLVED NAT.Q1: a highD response is a deceleration below an acceleration threshold held for a minimum
duration, possibly with a minimum speed drop (Jonas: "an acceleration threshold (with some duration, maybe
even change in speed)"). NC.0b pre-registers the three parameters with a sweep grid (a_th 0.5–2.0 m/s²,
T_min 0.3–1.0 s, Δv_min none–1.0 m/s), chooses the primary values from the measured noise floor and a 5%
false-positive bound before any event is scored, and reports the sweep beside every response-dependent
result. For inD, a rejected gap.
RESOLVED NAT.Q2: highD cut-ins may go through the split-site interface schema as a dry run; no highD or inD
data goes to Volvo Cars, code and results may. The transfer policy already never bundles `external/**`;
per-track derived files from either dataset are written only under `external/highD_derived/` and
`external/inD_derived/`, and reports in `replication/` carry no track ids.
RESOLVED NAT.Q3: results are nominally internal; Jonas may share parts with Julian Schumann, a colleague (JJ)
and Arkady Zgonnikov (meetings 2026-09-17 and 09-18). Reports are written so a section stands on its own and
marks what is ours and unpublished; nothing is sent by a session.
RESOLVED NAT.Q4: the comfort-zone cards first (NC.1–NC.4); of the paper cards, NM.1, pre-registered as soon
as NC.0 yields steady-following episodes and run overnight.

## 2026-09-17 (evening) — Jonas and a colleague (JJ): other cognitive perspectives on what has been found

Jonas, sitting with JJ: think about other cognitive paradigms that could frame the work so far, "very
generally". Given in chat, recorded here so it survives the model switch that followed. Marked opinion
throughout; the references are from memory and UNVERIFIED (never cite without checking).

Starting point: the project's model is a classical psychometric threshold with a lapse rate plus a
relevance gate, and this week's findings (exposure moves the level, not the spread; anticipation precedes
surprise; a perceived quantity beats the field as the axis) sit more naturally in that frame than in the
active-inference one. Eight framings, each with a reading of our results and a test:
1. Signal detection theory (Green & Swets 1966): level = criterion, spread = sensitivity; EX.1/EX.2's
   criterion-only shift is what SDT predicts of a payoff or prior change; the track's four-times-sharper
   drivers is a sensitivity difference attributable to the stimulus. Test in hand: PS ratings plus button
   presses on the same study-1 trials as a two-response SDT design.
2. Adaptation-level / range-frequency theory (Helson 1964; Parducci 1965): the criterion settles relative
   to the experienced stimulus range; the biggest threat to naturalistic transfer of the levels. Test in
   hand: the fitted level as a fraction of each study's stimulus range across the two cut-in studies;
   highD's census then places real cut-ins in that range.
3. Ecological / affordance-based control (Gibson & Crooks 1938; Lee 1976; Fajen 2005; Fajen & Devaney
   2006): the boundary as an action boundary ("can I still stop") scaled to capability, recalibrating with
   practice; the released model's safety term is an affordance boundary in disguise. Test: refit study 2 on
   required deceleration relative to a capability estimate (appendix 16's colleague model is adjacent).
4. Task-capability interface / risk allostasis / satisficing (Fuller 2005, 2011; Summala 2007; Wilde 1982):
   the per-driver trait as a target feeling of task difficulty; extra motives move the target for everyone.
   Needs a manipulation (the simulator study of the roadmap).
5. Evidence accumulation with a starting-point bias and urgency (Ratcliff 1978; Cisek et al. 2009;
   Markkula et al. 2016): anticipation before surprise = a starting point near the bound; a scenario-
   specific anticipation horizon (PC.1) = a scenario-specific urgency gain; reconciles R.1's negative
   result. Test: a starting-point diffusion fit on study 1's cut-in response times against the threshold
   model, held out.
6. Predictive processing, the other slice (Engström et al. 2018): on the left turn only the driver's own
   planned path opened the gate (PC.1's P reading), so intention, not kinematics, starts the response; the
   gate as precision on one prediction-error channel; glances (GZ.1) as uncertainty-driven sampling. The
   most direct bridge back to the authors.
7. Hazard perception and schemas (Horswill & McKenna 2004; Crundall et al. 2012): scenario-specific
   anticipation horizons as learned hazard scripts; the level may correlate with experience.
8. Intent attribution: the gate as an inference about the other driver's intention rather than a
   projection. Test on study 2: does the gate open earlier when the cut-in's onset is more legible at the
   same lateral rate?
Recommended first: 2 (decides transfer, data in hand), 5 (one mechanism for R.1 and the anticipation
findings), 3 (a cognitive reading of the safety term with a highD transfer prediction). Not authorized;
Jonas may turn any into a card or ask for a literature search.

## 2026-09-17 (late evening, capable session) — the six points from a colleague (JJ): an analysis and a program, not a card

Jonas, after a long discussion with a colleague (JJ): think deeply about JJ's comments, what it would
take for our comfort-zone work to work and be better with all the components of active inference, and
what we can do, test and develop to do what he proposes; analyse and plan only; document all, with
outside sources, illustrations and plain prose. JJ's points as relayed: (1) work with active
inference, find what is missing and add it; (2) predictions as the rollout of our own policy in the world
of the others, choose the least-free-energy policy; (3) ideally one rollout of the whole world, in practice
others first then match ours; (4) uncertainty as the core component; (5) the cut-in probability as a
central part of the cut-in algorithm; (6) normative models at the core; (7) LLMs and data-driven methods,
and understanding mechanisms by studying weights (JJ's group is putting an intern on it). Jonas has more to add
over several sessions.

Delivered: `docs/active_inference_program.md` (+ docx, pdf), eight schematic figures from
`docs/make_ai_program_figures.py` (no fitted numbers in any figure). No analysis run; the suite was
green before (31/33/40/96/62/20/28/27/16/30) and nothing in `src/` changed.

The argument, in five lines. (a) The current model is an active-inference agent with everything but the
preference threshold switched off; the falsifications on record were of slices (pointwise deficit with a
worst-case counterfactual; a non-leaky accumulator of it; trust withdrawal as onset; a fixed-horizon
projected conflict), never of an agent that predicts, rolls out and compares. (b) The one move that ties
JJ's points together: replace the pointwise axis by a policy comparison, dG = G(continue) - min over a
small menu of the ego's policies, in nats, with rollouts against a predictive fan of the other's futures;
the comfort zone is where continuing is still the least-cost policy. (c) The gate then emerges from a
prior and an inferred intention (G.1's pre-onset gate of 0.063-0.070 reads as a prior cut-in probability),
the anticipation horizon emerges from where the rolled-out paths meet and how uncertain the arrival is
(PC1.Q4), and one level in nats spans the scenarios (EL.Q4 dissolved by construction if it works).
(d) Points 3, 4 and 5 are one object: the generative model of the other road user, estimated from data,
with uncertainty growth and a latent intention; points 5 and 6 supply it from highD and inD. (e) Point 6
also gives a known-mechanism interpretability benchmark: a small end-to-end network on study 2, probed for
looming, where the answer is known.

Outside sources checked this session and cited: Schumann, Engström, Wei, Liu, Kober & Zgonnikov (2026,
arXiv:2604.19838, a joint two-agent active-inference interaction model, which is JJ's points 2 and 3
in his own group's hands); Mohammad, Mooi & Zgonnikov (2026, arXiv:2604.09609, general-purpose LLMs as
closed-loop driver agents in a merge, to appear at ITSC 2026); Tolstaya et al. (2021, conditional
behavior prediction and the interactivity score); Seff et al. (2023, MotionLM); Hwang et al. (2024,
EMMA); Friston et al. (2021, sophisticated inference); Wang et al. (2025, bounded-optimal crossing under
noisy perception); Zgonnikov, Abbink & Markkula (2024); Markkula et al. (2023); Pekkanen et al. (2018);
Shi et al. (2025, physics-informed lane-change intention on highD); Li et al. (2023) and Nanda et al.
(2023) on emergent world representations; Bricken et al. (2023) and Templeton et al. (2024) on sparse
autoencoders; Alain & Bengio (2016) on probes; Wei et al. (2023b, world-model learning, from the publisher's listing). Two cited by title only (ScienceDirect pages refused).

The honest bar, stated in the document: study 2 is at the noise floor (looming 0.113, floor 0.118), so a
rollout formulation can at best tie there; it earns its place by needing no gate for the pre-onset cells,
by transferring to the left turn and the overtake with one level, and by predictions about uncertainty
(truck against car, video against track). Ten cards proposed under prefix JJ, in three phases; none
authorized. Phase 0 (data in hand): JJ.1 design note, JJ.2 rollouts on the cut-in, JJ.3 transfer in nats,
JJ.4 precision as spread. Phase 1 (on highD/inD, after NC.0): JJ.5 norms from data, JJ.6 cut-in
probability, JJ.7 learned predictor, JJ.8 interactivity. Phase 2 (now, in parallel): JJ.9 known-mechanism
benchmark, JJ.10 LLM as judge. Recommendation (opinion): JJ.1 then JJ.2, and JJ.9 in parallel.

Queries:

@JJ.Q1(judgment, jonas): Authorize JJ.1, the design note for the rollout formulation of the comfort-zone
boundary (`docs/active_inference_program.md` §3.2, §10), as the next card? Days of work, nothing off disk;
its result decides whether JJ.2 to JJ.4 are built.

@JJ.Q2(judgment, jonas): Which preference variant is primary in JJ.2: the released six terms including the
safety counterfactual (faithful to the paper), or the expected collision outcome under the predictive fan
without the counterfactual (the theory `docs/r2_pipeline_review.md` §3.2 points at)? Recommendation: the
released form as primary, the other as the pre-stated alternative promoted only by JJ.2's rule (c).

@JJ.Q3(judgment, jonas): May a predictor trained on highD, or its weights, be shared outside the project
(JJ's group's intern, the paper's authors)? The license forbids redistributing the data; the status of derived
models needs a ruling before JJ.7 is planned for sharing.

@JJ.Q4(minor, jonas): Do study 2's cut-in stimuli contain contextual cues to intention beyond proximity (a
vehicle ahead of the cut-in vehicle in its own lane, an indicator, its speed relative to its lane)? Decides
whether JJ.6's contextual features can be tested on the video data or only on highD.

@JJ.Q5(judgment, jonas): May text descriptions of the unpublished video studies' cells be sent to an
external language-model API for JJ.10? If not, JJ.10 is dropped or run on a local model only.

@JJ.Q6(judgment, jonas): Coordination with JJ: offer the known-mechanism benchmark (JJ.9) to his intern
as a shared case, and ask which model the intern will probe, so that JJ.7's predictor can be built to be
comparable?

## 2026-09-17 (night, same session) — Jonas's rulings on JJ.Q1–Q6; card JJ.1 written; the generative-model framework; the attribution rule

Jonas answered the six queries of the previous entry the same evening, and added: the colleague whose
points the program document answers is to be referred to as **JJ** in every document, and neither the
colleague nor the company is to be named "in the reports etc." The prefix JE became JJ throughout
(program document, design note, figures, this log, the handover); the names were removed from the
program document, this log's two entries of 2026-09-17 evening, and the handover banner. Other files
that name the colleague predate the instruction and are listed as a query below.

RESOLVED JJ.Q1: go as proposed. Card JJ.1 is authorized and written: `docs/rollout_boundary_design_note.md`
(+ docx, pdf), the construction in full with every constant motivated and the pre-stated rules of JJ.2 to
JJ.4; stop for review before coding.

RESOLVED JJ.Q2: "maybe as you propose; what is the cost of testing both?" The cost is one flag on the
safety term (defaulting to the released behavior) and one extra column in every table: both variants run
in every card, the released form primary, the expected-outcome form promoted only by JJ.2's rule (c).
Written into the design note §1.4 and §2.

RESOLVED JJ.Q3: a real problem; work locally for now, then the same on VCC data if it can be had. Jonas
asked for a framework to be run on VCC data, prepared on the drone data, and said the data scale is the
project's largest issue. Answered by `docs/generative_model_framework.md` (+ docx, pdf) and
`src/generative/` (components C1 hazard, C2 lane-change execution, C3 uncertainty growth, C4 the ego's
normal; the export rule in code; the runner on the interface), `tests/test_generative.py` (28 checks;
the suite is now eleven files), and card GM.0 (`replication/czb/gm0_generative_smoke.py` →
`out/gm0/report.md`), which rehearses the runner on the synthetic fixture and passes its three pre-stated
checks, the third being that the fixture's lateral growth slope equals the jitter floor (0.138 against
0.141 m/s). The argument of the framework note: a structured generative model needs a handful of
distributions, each estimable from highD-scale data (5 600 complete lane changes, Krajewski et al.
2018); only a learned conditional density (C5) has a real appetite, and public motion datasets exist for
it. Not sent anywhere; the VCC track stays paused.

RESOLVED JJ.Q4: no such information in the stimuli that can be used today. Jonas adds that one of the
paper's authors said the most important part of a cut-in model is likely the normative (generative)
model of the probability that the cut-in vehicle initiates a lane change: that is component C1 of the
framework and the prior p0 of the design note, made a function of the scene. Jonas also reports JJ's
view that surprise lacks urgency but that urgency should not be patched on top; JJ's alternative Jonas
will try to recall. Opinion recorded in the program document §13: in the rollout form urgency is
already inside the quantity (a nearer conflict occupies more of the horizon's steps and collides at
higher relative speed in more sampled futures), which is why the released model's own accumulated
quantity is the pragmatic shortfall of the current policy over the horizon, not surprise about the
world.

RESOLVED JJ.Q5: not answered explicitly; JJ.10 (an LLM as judge) stays unauthorized until it is.

RESOLVED JJ.Q6: the colleague's group deals with its intern itself. Agreed: JJ.9 stays our own
methodological check, built for our question and not for comparability with an unknown model; if it
yields a clean result it can be offered later as a worked case, in writing.

Queries:

@JJ1.Q1(judgment, jonas): The steer-away policy on the cut-in depends on whether the studies' road has a
free lane on the far side (the context files will say). If not, the menu is four longitudinal policies.
Confirm that a menu without a steering option is acceptable for the cut-in, or name the alternative.

@JJ1.Q2(minor, review): sigma_a = 0.5 m/s^2 for longitudinal growth in the rollout predictor is an
unverified placeholder that GM.1 (component C3 on highD) replaces; flagged so that no report quotes it as
measured.

@JJ1.Q3(judgment, jonas): JJ.4's medium contrast needs perceptual constants (angular noise for a frozen
monocular frame against a moving view) that the project has not sourced. Accept that JJ.4 reports the
fitted ratio and marks the predicted ratio "not yet possible" if no source is found, rather than inventing
constants?

@GM.Q1(judgment, jonas): Extend the split-site data request with exposure episodes (adjacent-lane
vehicles that did not cut in) and the partner's own context columns (`docs/generative_model_framework.md`
§4), to go to VCC as one schema revision with NDS.Q2–Q5 when the track resumes? Without it the initiation
hazard (C1) cannot be fitted at VCC.

@GM.Q2(judgment, jonas): Apply for exiD as well (same provider as highD and inD; highway ramps, dense with
merges and lane changes)?

@GM.Q3(judgment, jonas): Pursue C5, a learned conditional density, on the public motion-forecasting
datasets for general motion with highD and VCC supplying local norms? Recommendation: not before JJ.2 has
shown the structured predictor is worth improving.

@GM.Q4(minor, review): The synthetic fixture's six `cut_in` events carry no lateral motion, so C2 finds no
lane change and is rehearsed only through its property tests; a scripted lateral trajectory in
`transfer/make_synthetic_fixture.py` would let GM.0 cover C2 and show VCC's adapter what a cut-in looks
like in the interface shape.

@ATTR.Q1(judgment, jonas): The attribution rule was applied to the new documents, this log's two
2026-09-17 evening entries and the handover banner. Files written earlier that still name the colleague:
`handover_2026-09-17.md` (part 2, §7, §10), `docs/naturalistic_data_plan.md` (§5 and §6, the sharing
ruling NAT.Q3), and the two commit messages of this session before the instruction (rewritten, since
nothing was pushed). Scrub those documents too, or leave them as the dated record they are?

## 2026-09-18 — Jonas's rulings on JJ1.Q1, JJ1.Q3, GM.Q1–Q3; JJ.1 authorized and delegated; the implementer's handover

RESOLVED JJ1.Q1: no steering in the policy menus we start with (the crowd-sourced stimuli and the
naturalistic data both carry that constraint). Design note §1.3 updated: four longitudinal policies on
the cut-in; proceed/wait on the left turn; continue/abort on the overtake.

RESOLVED JJ1.Q3: as proposed. JJ.4 reports the fitted ratio of the video and track spreads and marks the
ratio predicted from perception "not yet possible" unless a source for the perceptual constants is found.

RESOLVED GM.Q1: yes, extend the data request. Drafted as `transfer/schema_revision_proposal.md` (schema
version 2: the five NDS.1 corrections plus exposure windows, the partner's context columns, the
lane-change onset band, the sampling rule, and an export-rule line for fitted coefficients). The schema
file itself is unchanged; nothing is sent; the VCC track stays paused.

RESOLVED GM.Q2: Jonas applies for exiD.

RESOLVED GM.Q3: as proposed; stop at C1–C4 for now, keep the learned conditional density (C5) open for
when they are done.

JJ.Q5 still open. Implications if the answer is no: JJ.10 (an LLM as judge of the study-2 cells) is
exploratory and nothing else depends on it; it would run on a local model (CPU only, so a small one, with
correspondingly weak judgments) or be dropped. What would be sent if yes is the stimulus parameters of
each cell (gap, speeds, TTC, lane-change duration, timepoint), not the video, not any participant's
response; the question is whether describing unpublished stimuli to an external service counts as
sharing the related project's data.

JJ.1 read by Jonas: "go", with the implementation by a less expensive model and everything documented for
it. Written: `handover_jj1_implementation.md`, the implementer's brief: the task, the order of steps with
done criteria and stop conditions, the construction as code, every reused module and function with its
signature and what it gives, the scripts' pre-registration pattern, eighteen property tests, the
prohibitions, and the traps the designing session knows of. The design note gained §1.0 (what the
crowd-sourced video data are for in this card: the scene at the freeze from the traces, the share who
intervene from the participants, nothing in the rollouts fitted to the responses but the threshold
model's three parameters) and the rulings in §7. The program document gained the rulings in §13.

On Jonas's question about the type of generative model (answered in chat, recorded here): structured,
not learned end to end. Bicycle kinematics for motion; a latent intention (keeping or changing lane) with
a prior that the initiation hazard (C1) makes a function of the scene; the other's future as a fan whose
width grows with the horizon at rates measured from data (C3); the norms as the content of that fan
(what an ordinary lane change looks like, C2) and, in the released model's form, as the sampling bias of
its tournament; the ego's own normal as the preference function with constants calibrated on free driving
(C4). Data fix a handful of distributions; the structure is written in. A learned conditional density is
the optional last rung.

Queries:

@JJ1.Q4(judgment, jonas): The implementer's brief asks for one new flag in `src/aidriver/preferences.py`
(`safety_term_enabled`, default True = released behavior) so that variant B can switch the safety term
off without touching any default. Standing rule 3 allows new behavior behind a flag defaulting off;
confirm that this reading covers a flag defaulting to the released behavior.

@JJ1.Q5(minor, review): The brief lets the implementer skip the released norm tournament (predictor P1)
if wrapping `forward_tar_agent` open loop costs more than a day; P1 is a secondary in JJ.2. Confirm or
require it.

## 2026-09-18 (overnight, implementing session) — card JJ.1 built; card JJ.2 run: Delta G is DROPPED on the cut-in

Jonas's instruction for this session: read `handover.md`, implement what it points to, take the
decisions that come up and document them, do not stop and wait. The work is card JJ.1's
implementation, delegated by `handover_jj1_implementation.md`, and then cards JJ.2 to JJ.4 in the
order that brief fixes. The suite was green at 31/33/40/96/62/20/28/27/16/30/28 before anything
was touched, and the tree was clean apart from Jonas's own `docs/handout_schumann_2026-09.docx`,
which was never staged.

**Step 1 — the package.** `src/rollout/` with the five modules the brief names (`belief`,
`predictor`, `policies`, `efe`, `boundary`) and `tests/test_rollout.py` with the eighteen property
claims of the brief's section 6, which come to **27 checks**. The suite list in `handover.md` §0
step 2 now has twelve files and ends `python tests/test_rollout.py` → 27.

One change in `src/aidriver/preferences.py`, the one the brief asked for: the flag
`safety_term_enabled`, default True = released behavior, which is variant B of design note §1.4.
Property test (16) checks that at its default `log_preference_terms` is bit-identical to the six
released terms on `cutin_obs` of a study-1 trace, and the eleven other suite files are unchanged.
JJ1.Q4 (Jonas's confirmation that rule 3 covers a flag defaulting to the *released* behavior
rather than *off*) is still open; the brief directed the change, so it was made, and the flag is
written so that answering JJ1.Q4 "no" costs one line to revert.

The jitter floors are not typed in. `rollout.belief.verify_floors()` parses card HS.1's own module
docstring and fails if the four measured values it cites stop being there, which is the brief's
"do not type a floor from memory" made mechanical. The floors used: study 2, 0.3 s window,
position 0.1 m and lateral rate 0.004 m/s; study 1, 1.0 s window, position 1.8 m longitudinal and
0.20 m lateral, lateral rate 0.133 m/s.

**Step 2 — card JJ.2, `replication/czb/jj2_rollout_cutin.py` → `out/jj2_rollout_cutin.md` (+
`out/jj2_rollout_cutin_cells.csv`, no participant ids).** Cells, folds and metric imported from
the registered R.2 script and reproduced exactly: 378 cells, 288 post-onset, 90 pre-onset, six
leave-one-starting-TTC-out folds. No cell's trace ends before its freeze; the matched-TTC row
grouping reproduces the diagnostic's by recovering the gap's own 24 of 24. The intention update
behaves as the design note intends: P(changing) is 0.070 at every pre-onset cell and 1.000 at
every post-onset cell.

The pre-stated verdict is **DROP**, and rule (a) is what fails, at both variants:

| rule | criterion | variant A | variant B |
|---|---|---|---|
| (a) post-onset held out | <= 0.1127 | 0.3202 FAIL | 0.2976 FAIL |
| (b) pre-onset out of sample | < 0.05 | 0.5381 FAIL | 0.2495 FAIL |
| (c) matched-TTC rows | >= 24 of 24 | 0 of 24 FAIL | 3 of 24 FAIL |
| (e) Monte Carlo | median SE <= 5% of the spread | 0.0052 against 0.0574 PASS | — |

0.3202 is chance (0.320 on file): the three-parameter threshold model collapses to the training
mean, because log Delta G is *anti*-ordered with the response (Spearman -0.648 with the share,
+0.848 with the gap, where the share itself is -0.862 with the gap). Rule (d)'s sweep moves
nothing: every value of p0, sigma_v,lat and sigma_a gives the same 0.3202, and H = 3 s gives
0.3300.

Two readings, in the report's §1b and stated there as readings:

1. **Delta G is a value-of-action quantity and it collapses where no action helps.** It is large
   where braking would avert a collision that continuing would cause, and small both where nothing
   is going to happen and where the gap is already too small for anything in the menu to avoid
   contact. The menu's own cost is the other half of the mechanism: braking at -3 m/s^2 costs a
   fixed 20 308 nats of control effort over the horizon whatever the scene is doing, because
   sigma_a = 0.1 m/s^2 in the released preference, so the minimum over the menu is floored.
2. **The released magnitude still grades with speed rather than with the gap.** G(continue) alone
   correlates +0.927 with dv and only -0.350 with the share, and a level on log G(continue) —
   the rollout's criticality *without* the policy comparison, not this card's axis — also scores
   0.3202. So the policy comparison and the preference function are not to be blamed for one
   another: the R.2 pipeline review's finding reappears inside the rollouts.

Nothing was reinterpreted to reach the verdict and nothing was tuned: the rules are the design
note's, copied verbatim into the script's docstring before the run.

Queries:

@JJ1.Q6(judgment, jonas): The intention update is implemented one-sided — the log-likelihood ratio
between "changing" and "keeping" is clipped below at zero, so an observation at the jitter floor
returns the prior instead of driving it to about 1e-40. The reason is what p0 is in the design
note's own words, "the prior before any lateral motion", motivated by card G.1's fitted gate
sitting at 0.063-0.070 in *every* pre-onset cell: p0 is already the belief held while no lateral
motion is seen. Property test (1) of the brief ("with the lateral rate at the jitter floor the
posterior equals the prior to 1e-3") cannot pass otherwise, on any choice of the two spreads. The
plain ratio is available as `one_sided=False`. Confirm the clip, or say that the design note meant
the plain ratio and test (1) should be withdrawn.

@JJ2.Q1(minor, review): Rule (c)'s matched-TTC row grouping lives inline in
`cutin2_lane_gate_diagnostic.py::main()` and has no function to import, so `jj2_rollout_cutin.py`
reproduces it (post-onset cells grouped by `ttc_true`, rows with at least 6 cells) and checks the
reproduction by recovering the gap's own "24 of 24" from it. Extract it into a function in that
script for the next card that needs it, or leave the check as the guarantee?

@JJ2.Q2(judgment, jonas): Delta G's failure is structural rather than a matter of constants: a
difference between the best alternative and continuing must vanish both where nothing is wrong and
where nothing helps, so it cannot be monotone in criticality. Two repairs are available inside the
JJ program and neither is authorized: (i) take the rollout's own criticality, G(continue), as the
axis and keep the menu only for the report — it scores 0.3202 too, so it would need the preference
magnitude fixed first; (ii) keep Delta G but measure it against a *feasible* alternative only,
which is a different quantity and needs its own design note. Which, if either?

@JJ2.Q3(judgment, review): The rollout menus' control-effort floor is a real design question the
design note did not anticipate. With sigma_a = 0.1 m/s^2 the released preference charges a fixed
20 308 nats for -3 m/s^2 over 30 steps and 69 912 for -6 m/s^2, so the alternatives are never
cheap and Delta G is dominated by that constant wherever the collision cost is smaller. Is
sigma_a = 0.1 m/s^2 (the released free-driving value) the right constant to score an *evasive*
policy with, or does the menu need its own effort calibration?

@JJ2.Q4(minor, review): The design note's §5 names the scripts `je2/je3/je4_*`; the implementer's
brief names them `jj2/jj3/jj4_*`, which matches the card prefix JJ and the query prefix. The
brief's names were used. The design note's §5 should be corrected when it is next touched.

## 2026-09-18 (overnight, same session) — card JJ.3: the same construction on the left turn, the overtake and the trait

`replication/czb/jj3_rollout_transfer.py` → `out/jj3_rollout_transfer.md`, `out/jj3_rollout_cells.csv`,
`out/jj3_driver_levels.csv`. The rules of design note §3 are copied verbatim into the script's
docstring; nothing was reinterpreted. The report opens by saying that card JJ.2 dropped Delta G, so
none of these numbers is a live candidate for the axis.

**The left turn (18 cells).** Every rule fails. (a) 0.2632 held out against distance alone's 0.0558
+ 0.01; (b) the 70 km/h predicted share is below the 50 km/h one at 0 of 9 matched PETs; (c) at
PET 4 s no sampled future collides under "proceed" within the released 6 s, so — as the rule says
in advance — the report states that the emergence claim fails on the left turn at that PET, and the
horizon was not extended. The mechanism is the same one card JJ.2 found: **Delta G is zero in 16 of
the 18 cells**, because waiting costs more than proceeding everywhere but at PET 0. Waiting pays the
speed term (an ego 7.8 m/s below its own desired speed, sigma_v = 0.5 m/s) and the braking effort,
and neither depends on how critical the scene is.

**The cyclist overtake (15 cells).** Rule (d) holds at C1 to C4 — the predicted share falls with
clearance at every one — and fails at C5, where the 1.5 m cell is predicted above the 1 m cell.
Held out, leave-one-timepoint-out: Delta G 0.1580 (A) and 0.1577 (B) against the clearance rule's
0.2099 and chance 0.1626. This is the one place in the three cards where the rollout construction
does something the released field could not (`out/overtake_field_check.md`: the field ranks these
cells at +0.402 against the clearance label's -0.833), and it is a 15-cell result with a narrow
dynamic range, so it is worth no more than that.

**The trait on one scale.** Spearman +0.261 [-0.106, +0.575] between the per-driver levels on
log Delta G on study 1's cut-in and on the 50 km/h left turn, at first exposure, over the same 43
drivers, against card TR.1's +0.647 [+0.407, +0.798] in mixed units. The pre-stated reading for a
correlation below TR.1's interval is "Delta G loses per-driver signal that the scenario-specific
axes keep", and the report states it — **with a caveat placed before it**: the left turn's axis
takes two distinct values over nine cells (Delta G is zero in eight of them), so the level fitted
there is close to a per-driver response rate at PET 0 and is not what TR.1 correlated. EL.Q4 is
therefore not answered by this card.

**Two implementation decisions, both in the report and both queried.** The left turn's "wait" could
not be both "-3 m/s^2" and "stop before the crossing": at the decision moment the ego is about
7.8 m/s with about 7 m of path left before the conflict band, which needs about 4.2 m/s^2. With -3
the ego stops ON the crossing and is hit there, which is not what the word "wait" names, so the
deceleration is raised per cell to whatever just stops it clear (3.6 to 4.7 m/s^2, capped at
a_max), and the value is in the report's table. And the ego's lane offset is held at zero for both
left-turn policies, because the released lane-keeping term is a straight-road construct and would
charge "proceed" the road-edge cost for turning.

Queries:

@JJ3.Q1(judgment, review): On the left turn the ego's lateral position is passed to the preference
function as zero for both policies, so the released lane-keeping term never fires. The alternative
is to pass the real lateral position, which charges "proceed" -15 000 per step (the road-edge cost)
for leaving a straight lane it is turning out of by design, and would make the comparison
meaningless. The right fix is a lane model that follows the intended path; does that belong in this
project or is holding it at zero the standing convention for turning scenarios?

@JJ3.Q2(judgment, jonas): The design note's left-turn "wait" is "stop before the crossing at
-3 m/s^2", and in these stimuli that is not satisfiable: the ego needs about 4.2 m/s^2 at the
decision moment. The implementation kept "stop clear of the conflict band" and raised the
deceleration per cell (3.6 to 4.7 m/s^2, reported). The alternative reading — keep -3 and let the
ego stop on the crossing — makes "wait" a policy that is struck by the oncoming car, which cannot
be what the menu means. Confirm, or fix the menu with a decision moment far enough back that -3
works.

@JJ3.Q3(minor, review): The freeze for study 1's overtake and cut-in is the clip end by the
project's own `czb_data._cov_end` convention, so C1 is read at onset - 0.15 s rather than at onset.
The design note says "the clip end"; the convention exists because a C1 covariate must not depend
on manoeuvre frames (`out/c1_covariate_defect.md`). Confirm that this is the freeze the design note
meant.

@JJ3.Q4(minor, review): Rule 3(d) asks for the held-out score "against the lateral-clearance rule
of card B.1", and no such held-out score is on file — `out/overtake_field_check.md` reports rank
correlations only. The comparator was therefore computed in this card's script (a threshold on the
clearance the manoeuvre ends at, same folds, same fitter) and is labelled as computed here.

@JJ3.Q5(minor, review): The design note fixes no fold for the overtake's 15 cells. Both schemes are
reported; leave-one-timepoint-out is the primary, argued rather than scored (leave-one-clearance-out
asks a clearance rule to extrapolate to a level it has never seen, which it cannot do by
construction, so it would flatter Delta G). Both were computed after the run and the report says so.

@JJ3.Q6(judgment, review): The trait table's left-turn axis takes two distinct values over nine
cells, so the per-driver level there is barely identified and the +0.261 is not a measurement of
the trait. If the trait on one scale is still wanted after JJ.2's DROP, it needs an axis with
dynamic range on both scenarios — which is query JJ2.Q2's question again.

## 2026-09-18 (overnight, same session) — card JJ.4: precision as spread. The truck IS sharper, and the gate's spread is not measurement noise

`replication/czb/jj4_precision_spread.py` → `out/jj4_precision_spread.md`. This card does not depend
on Delta G — it asks whether the level estimator's response spread is a measured stimulus precision —
so it stands on its own after JJ.2's DROP. The three parts of design note §4 are copied verbatim into
the script's docstring.

**Medium (the video left turn against the test track).** The two fits reproduce card TT.1's numbers:
sigma_resp 0.858 s on the video (on file 0.86) and 0.198 s on the track (0.20), PET_50 2.18 and 2.45 s.
**Fitted ratio, video / track: 4.34 [2.38, 7.93]** (delta method on log sigma_resp, the two Laplace
variances in quadrature). The design note calls the constrained one-spread-each model "trivially
equivalent as a fit", and the report says plainly that the two fits therefore ARE that model. The
ratio **predicted from perception** is reported as **not yet possible**, exactly as Jonas's ruling
JJ1.Q3 fixed in advance: no source for the visual precision of distance and closing speed in a frozen
monocular clip against a moving binocular view, and no constant was invented.

**Apparent size (E.2): the two-spread model earns its place, and the truck is sharper.** Held out
under LOPO over 15 drivers, **+60.6 log-likelihood units** against the pre-stated margin of 2.
sigma_resp is **0.273 for the truck against 0.424 for the car** (ratio 0.64), on 3 417 Button cut-in
trials over TTC 4 to 8, 43 drivers. The direction is the one the roadmap predicted: a larger apparent
size gives a sharper criterion.

The rule could not be applied to the stage-1 estimator and the report says so rather than working
around it: in the Button design every cell's intervention share is 0.976 to 1.000, because that
paradigm asks WHEN you would intervene and everyone presses, so a binary threshold model has no
response variation to fit. The contrast runs instead on the Button paradigm's own response, the press
time: the observed level is log theta_dot at the press, with one offset per stimulus cell (class x
TTC, because the level drifts about one log unit from TTC4 to TTC8 and that drift is the stimulus's,
not the driver's) and the spread indexed by class only. 21 of 3 438 trials are censored and dropped.

**The gate's spread is not measurement noise.** Measured here on the 90 study-2 traces, the pre-onset
lateral-rate jitter over card G.1's 0.3 s window is a median of **0.0021 m/s**, which over the 3 s
horizon is **0.0064 m** against G.1's fitted s_l of **0.990 m** — a factor of 156. So the gate's
spread is a *predictive* uncertainty about what the other vehicle is going to do, not the traces'
resolution. Adding P0's growth constant reproduces 0.990 m to three decimals and lands at a ratio of
1.00, inside the pre-stated factor of 1.5, **and the report states the circularity before the number**:
sigma_v,lat = 0.33 m/s was itself motivated in design note §1.2 by reading 0.99 m over 3 s as a
lateral-rate uncertainty, so it had to. The line becomes a test only when component C3 of the
generative-model framework measures sigma_v,lat on highD.

Queries:

@JJ4.Q1(judgment, review): Design note §4's apparent-size contrast says "the stage-1 estimator", and
the stage-1 estimator cannot be fitted on the Button design (intervention share 0.976 to 1.000 in
every cell). The contrast was run instead on a Gaussian hierarchical model of the level at the press,
which is that paradigm's own response, with the same LOPO rule and the same margin. Confirm that this
is the contrast §4 meant, or name the Random-design construction that should replace it — the Random
design has no truck cut-in, so E.2 would then have to be dropped rather than moved.

@JJ4.Q2(minor, review): The apparent-size model carries one offset per stimulus cell (class x TTC)
rather than one per class, because the observed level drifts about one log unit from TTC4 to TTC8.
With one offset per class that drift sits inside sigma_resp and the comparison measures the design
rather than the driver. Confirm the per-cell offsets.

@JJ4.Q3(judgment, jonas): The truck's criterion is sharper than the car's by a wide margin (0.273
against 0.424 log units, +60.6 held-out log-likelihood units). Two readings are open and this card
cannot separate them: a larger apparent size really is perceived more precisely (the E.2 hypothesis),
or the looming axis is mis-scaled for a 16.5 m body, so that what looks like precision is the axis
fitting the truck better. The second can be tested by refitting the axis per class; it is not
authorized here.

@JJ4.Q4(minor, review): The gate-spread line of §4 is circular as written and the report says so.
Worth restating in the design note as "a consistency check of the note's own arithmetic until C3
measures sigma_v,lat", so that no later reader takes the 1.00 ratio for evidence.

## 2026-09-18 (overnight, same session) — card JJ.1 closed: the four steps, the three verdicts, and what is now open

All four steps of `handover_jj1_implementation.md` are done and committed, and §9 of that file is
written: the verdicts, the numbers a reader must not re-derive with their files, the queries, and
what this session may have got wrong. The suite is green at 31/33/40/96/62/20/28/27/16/30/28/27
(twelve files) before and after; `handover.md` §0 step 2 carries the twelfth file and its count, and
nothing else in `handover.md` was touched — §1 and §4 are for the reviewing session, as the brief
says. Nothing was pushed. `docs/handout_schumann_2026-09.docx` was never staged.

**The verdicts, in the design note's own words.**

- **JJ.2 — DROP.** "Drop if (a) fails." Post-onset held out 0.3202 (variant A) and 0.2976 (variant B)
  against 0.1027 + 0.01. 0.3202 is chance.
- **JJ.3, left turn — every rule fails**, including rule (c) in the form the rule itself prescribes:
  "the emergence claim fails on the left turn at that PET rather than extending the horizon".
- **JJ.3, overtake — rule (d) holds at C1 to C4 and fails at C5**; held out 0.1580 against the
  clearance rule's 0.2099 and chance 0.1626. The one thing in these three cards that the released
  field could not do.
- **JJ.3, the trait — "Delta G loses per-driver signal that the scenario-specific axes keep"**, with
  the caveat stated before the reading that the left turn's axis takes two values over nine cells.
  EL.Q4 is not answered.
- **JJ.4 — the two-spread model earns its place** (+60.6 LOPO units) and **the truck is sharper**
  (0.273 against 0.424); the video/track ratio is 4.34 [2.38, 7.93]; the perceptual prediction is not
  yet possible; the gate's spread is not measurement noise (the traces' jitter is 156 times too
  small).

**One mechanism is behind three of the four failures, and it is worth stating on its own.** Delta G is
a value-of-action quantity: large where an alternative averts what continuing would cause, and small
both where nothing is going to happen and where nothing in the menu helps any more. It therefore
cannot be monotone in criticality, and on the cut-in it is anti-ordered with the gap (-0.648 with the
share, +0.848 with the gap). The menu's own price is the other half: at the released sigma_a =
0.1 m/s^2 a -3 m/s^2 alternative costs a fixed 20 308 nats over the horizon whatever the scene is
doing, which floors the minimum, and on the left turn waiting costs more than proceeding in 16 of 18
cells. Independently of both, the released magnitude still grades by speed rather than by gap inside
the rollouts: G(continue) alone correlates +0.927 with dv and scores 0.3202 as well. So the policy
comparison and the preference function are not to be blamed for one another — which is the point of
reporting G(continue) beside Delta G — and the R.2 pipeline review's finding has reappeared one level
up, inside the imagined futures.

**What this does and does not say about the JJ program.** It says that step 1 of the program as
designed does not produce an axis, and it says why, in a way that is a property of the *quantity*
rather than of any constant: no sweep of p0, sigma_v,lat, sigma_a or H moves the cut-in score off
chance. It does not say that rollouts are the wrong idea, and JJ.4 — which needs no Delta G at all —
produced the session's one clean positive result. The queries that decide what happens next are
**JJ2.Q2** (repair Delta G, or fix the preference magnitude first?), **JJ2.Q3** (should an evasive
policy be priced with the released free-driving sigma_a?) and **JJ3.Q2** (the left turn's "wait" cannot
be both -3 m/s^2 and clear of the crossing). Fourteen queries in all were raised across the four
entries of today: JJ1.Q6, JJ2.Q1-Q4, JJ3.Q1-Q6, JJ4.Q1-Q4.

**Not done, and deliberately.** P1, the released norm tournament as a secondary predictor (JJ1.Q5
allows skipping it, and JJ.2's verdict makes a secondary moot until the primary is settled); any
change to `docs/rollout_boundary_design_note.md` or `docs/active_inference_program.md`, which are the
designing session's documents; any update to `handover.md` beyond the suite list.
