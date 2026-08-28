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
