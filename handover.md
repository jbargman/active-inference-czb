# handover.md — start every session here

*Rewritten 2026-09-22 (night) after the review of the 09-18 to 09-22 arc and the cards that
followed it. Written so that a less expensive model can execute §4's cards one at a time. Dated
records, newest first: **`docs/review_2026-09-22.md`** (the review; read it before quoting anything
from the arc), `handover_2026-09-22.md` (what the arc believed when it ended; its banner says what
the review changed), `handover_2026-09-22_standing_superseded.md` (the previous version of this
file, still the fullest account of the measurement model, the test-track anchor and the decks),
then `handover_2026-09-17.md`, `handover_2026-09-13.md`, `handover_2026-09-03.md`. Where this file
and the repository disagree, the repository wins, and you say so in your reply.*

## 0 What to do when a session starts

1. Read this file in full, then `docs/czb_work_orders.md` §2 (the standing rules), then the card
   named for the task (§4). Do not read the papers, the handbook or `OthersWork/` unless the card
   says to.
2. Run the suite exactly like this and confirm 31, 33, 40, 96, 62, 20, 28, 27, 16, 30, 33, 35, 24,
   19 and 24 passed (fifteen files; `pytest` is *not* the suite):
   ```bash
   python tests/test_surprise.py
   python tests/test_comfortzone.py
   python tests/test_causation.py
   python tests/test_cutin.py
   python tests/test_ltap.py
   python tests/test_transfer.py
   python tests/test_interface.py
   python tests/test_situational.py
   python tests/test_norms.py
   python tests/test_conflict.py
   python tests/test_generative.py
   python tests/test_rollout.py
   python tests/test_margin.py
   python tests/test_admissible.py
   python tests/test_looming_pref.py
   ```
3. `git status` and `git log --oneline -5`. The tree should be clean (four untracked `.log` files
   under `replication/czb/out/` are normal). If anything else is uncommitted, stop and report it.
4. If Jonas said only "load handover.md": reply with five sentences from §1 and the table in §3,
   then stop and wait.
5. If he named a card: find it in §4, check its "after" condition, and if it is met, do it. If it
   is not met, say which query blocks it and stop. If he said "work through §4", do the cards in
   order, batch mode (`performing-research` skill §2): never block, raise queries, report card by
   card.

## 1 Where the project stands, in plain terms

**The aim.** Measure drivers' comfort-zone boundaries (CZB) with an active-inference driver model.
The first attempt, one scalar from the published model's preference field, failed two
pre-registered tests (gates R.1, R.2). The measurement model that came out of that work and still
stands is

> share who intervene = lapse + (1 − lapse) × **GATE** × Φ((**AXIS** − **LEVEL**) / spread)

with, on the cut-in, the axis the optical expansion rate (looming), the gate the probability that
the other vehicle's lateral clearance projected 3 s ahead falls below a minimum (card G.1), and the
level a per-driver quantity whose population percentile is the deliverable. Held-out scores on the
second cut-in study, the only two-dimensional design the project has: gated looming rule
**0.1027**, ungated **0.1137**, gap threshold 0.1522, chance 0.320, noise floor 0.118; pre-onset
(the gate's test) **0.0319** gated. Every card since has been scored against these. The per-driver
level is the same person across scenarios (Spearman +0.647 between the cut-in and the left turn,
card TR.1). The full account is `handover_2026-09-22_standing_superseded.md` §1.

**The JJ program (2026-09-17).** A senior colleague from the model's author group, code **JJ**
(never name the colleague or the company in any document or commit), urged using the full
active-inference stack: rollouts of the ego's policies against a predictive fan, uncertainty as the
core, the cut-in probability as central. `docs/active_inference_program.md` answers it; card JJ.1
(`src/rollout/`) built the construction; the arc of 09-18 to 09-22 ran it (cards JJ.2 to S1.4).

**The review of that arc (2026-09-22, `docs/review_2026-09-22.md`).** Its numbers mostly reproduce;
several conclusions do not follow from them. The arc's through-line, "the released braking-margin
term is inverted against the response (ρ −0.861)", is a horizon-sum accounting effect: summing a
pre-contact cost over the horizon of a `continue` policy that drives through the lead counts the
steps before contact. Read pointwise the same quantity is ordered the human way (+0.633). Three
cards were invalid as run (RE.4 and JJ.2b: ego off the road; RE.1: only the first, clamped, plan
step examined); others were overstated (JJ.3's overtake, GM.1a, RE.3, S1.1's "beats the gap").
**What stands:** card JJ.2's DROP (ΔG does not order the cut-in cells, and card JJ.2c shows this
for the released staging too), the matched-TTC result (0 of 24 rows), and card JJ.4's direction.

**What the night's six cards then established (all pre-stated, all not credited):**

| card | quantity | result | what it teaches |
|---|---|---|---|
| S1.5 | the braking margin thresholded at a comfortable deceleration, with a standoff | on this study the assumed lead braking *is* the standoff (one lead speed); where the quantity orders the cells its level is 31 m/s² | S1.1's 0.1409 is "−6 with a 20.8 m standoff"; at the ruled −6 it is 0.2230 |
| S1.6 | admissibility: colliding policies excluded, not costed | 0.3107; the gate emerges as a tolerance on P(conflict) (90/90 pre-onset admissible at α ≥ 0.10, 0–2/288 post-onset) | ΔG becomes the comfort price of the mildest admissible deceleration; a flaw in JJ.1's fan found and fixed behind a flag |
| RE.4b | RE.4 with the ego on the road | 0.32 / 0.32 / 0.32 | RE.4's conclusion now rests on a valid construction for its agent-side functionals |
| JJ.2c | JJ.2 with the released flags | DROP, 0.3197 | JJ.2's verdict is about the released model too |
| JJ.5 | the model's own looming preference (τ⁻¹) read alone over the fan | 0.3156, ρ(gap) +0.662 | the intention belief supplies a gate in structure (8.5% → 100% of futures in the path); the horizon sum inverts the term |
| JJ.5b | the same profile per step, at its maximum, at the first step | 0.30–0.32 | removing the sum removes the inversion, not the failure: τ⁻¹ is a TTC quantity, and a TTC threshold scores 0.1679 here |

**Later the same night, Jonas kept active inference in play** ("we have to probe the different
ways to think about it"), and the gate half was settled by five more pre-stated cards
(`docs/looming_as_free_energy.md`; worklog "2026-09-22 (night, continued)"): card JJ.1's
intention belief reproduces G.1's gate where it is *closed* (JJ.6: pre-onset 0.0354, nothing
fitted) but at no keeping spread does an intention filter reproduce its post-onset grading (JJ.6b
to JJ.6d), because G.1's gate grades on how soon the other's body reaches mine, not on whether it
intends to. **JJ.6e: G.1's gate is, to 1e-16, a Gaussian-rate predictor's P(clearance < m within
3 s) with s_l = σT; with m = 0 it scores 0.1028 / 0.0462: DERIVED**, with the circularity declared
(σ = SD_VLAT was itself set from G.1's s_l). So the gate is the predictive uncertainty of the
generative model about the other's lateral motion at the anticipation horizon; the latent
intention variable is not needed for it. **JJ.8 (the link and the scale of the axis):** additive
sensory noise is rejected (+0.023: the spread is a spread of *levels*), the one-step
expected-free-energy decision on a log-scaled preference is indistinguishable from the reflex
reading but its parameters are degenerate (its level fits to 0), so only the reflex reading
(`docs/looming_as_free_energy.md` reading B: the free energy of the present looming observation
under a driver's prior) delivers a comfort-zone level with a meaning. That reading is the
measurement model restated, and the restatement is now backed by three tests rather than assumed.

**The reading that sets §4 (opinion, mine).** Every quantity built from a braking requirement or
from TTC is ordered against the participants within matched TTC, because at the same TTC a
smaller gap is a slower closing speed, and participants respond to proximity and looming
(θ̇ ∝ Δv/gap², card EL.1b). Active inference does not fix the preference; it is ours to choose.
The released agent already *observes* looming (`src/aidriver/agent.py`, `use_looming`). So the
construction that stays inside the framework is: **a prior preference over the looming
observation, with the gate supplied by the intention belief over the fan, read over a short
anticipation horizon** — the gated looming rule derived from the model's own machinery instead of
designed. Card JJ.6 tests the gate half, JJ.7 the preference half per driver.

**Parked, and Jonas asked to be reminded:** extending card JJ.4 (EX2.Q2 first, 15 min); the
"lateral factor" (now doubtful, REV22.Q2); the reference-distribution specification for the
naturalistic request. **Paused by Jonas:** the VCC track (2026-09-11). **Waiting on data:** highD
and inD (requested 2026-09-17).

## 2 The rules that bind every session (long form: `docs/czb_work_orders.md` §2)

1. **Every number you quote comes from a committed script with a tracked output.** No result
   strings typed into a report generator; no numbers from an interactive session. If you computed
   something to decide, write the script, run it, commit it, quote its output.
2. **The suite passes before and after every card** (§0 step 2). New behavior gets new property
   checks in the `check(...)` style, testing the claim.
3. **Never change a default in `src/aidriver/preferences.py` or in `src/rollout/`**; new behavior
   goes behind a flag that defaults off (`safety_term_enabled`, `keep_body_in_lane` are examples).
   **Never modify a script whose docstring says "pre-registered"**; write a new one that imports it.
4. **Pre-state, then commit, then run.** The card's script, with models, folds, metric, decision
   rule and your predictions in its docstring, is committed **in its own commit before it is
   run** (the night of 2026-09-22 did this for six cards; the arc under review did not, and its
   pre-statements could not be verified). Anything changed after a run is dated in the docstring
   and both numbers go in the worklog.
5. **"Released" means `PreferenceParams(v_desired=v_ego)` and nothing else.** The project's flags
   (`counterfactual_residual_severity`, `lane_entry_continuous`) are the project's staging; say
   which you ran.
6. **Documents:** US English; the `.md` is the source; build with
   `pandoc docs/X.md -o docs/X.docx --from markdown --resource-path docs` and
   `python docs/build_pdf.py docs/X.md`; no period at the end of a heading; opinions marked as
   opinions; never invent a reference. `PermissionError` means the file is open: write a `-vN`
   copy and say so. Never rebuild `docs/handout_schumann_2026-09.docx`; never stage it.
7. **Questions go in the worklog, not in chat, and do not stop the work.** Append an entry to
   `replication/czb/out/worklog.md` in the form of the last entries, each question as
   `@<CARD>.Q<n>(<severity>, <who>): ...` (`blocker`/`judgment`/`minor`; `jonas`/`review`), then
   run `python replication/czb/collect_queries.py`. Continue with what does not depend on it.
8. **Commit at the end of each card** with explicit paths (never `git add -A`), a message saying
   what changed and why, ending with the `Co-Authored-By` line the recent commits use. **Do not
   push unless Jonas asks**; the route is
   `git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin main`.
9. **Edit files with the Write and Edit tools, not shell heredocs.** Read the target lines first.
10. **Long runs** go to the background with a log in `replication/czb/out/` (the `.log` files stay
    untracked); the script writes its main report before any bootstrap. Check CPU time before
    calling a run stuck.
11. **The code for the colleague is JJ.** Not the name, not the company, not in commits.

## 3 What is waiting on Jonas

The register is `replication/czb/out/query_register.md` (142 open, 55 resolved). Do not start a
gated card until its query has a `RESOLVED <id>:` line in the worklog. The ones raised on
2026-09-22, blockers first:

| query | question, in one line | unblocks |
|---|---|---|
| **REV22.Q1** (blocker) | Has anything from the 09-18 to 09-22 arc been said to JJ or the authors ("inverted", "never brakes", the 0.5 s headway point without its a_OV caveat)? And: revise the three argument documents properly, or leave the dated banners? | card D.1 |
| REV22.Q4 | *Resolved by card JJ.2c the same night:* DROP carries over to the released staging | nothing |
| RE4B.Q1 | Rerun card JJ.2b's planner pass corrected (slow), or retire the released-planner comparison? | card P.1 |
| REV22.Q2 | Drop the parked "lateral factor", or rebuild it with a cyclist-sized collision box? | nothing |
| S16.Q1 | Make `keep_body_in_lane=True` the standing fan for future rollout cards? (Changes no verdict so far; §4's cards use it and say so) | nothing |
| S16.Q2 | The gate emerged as a tolerance on P(conflict); on these cells the posterior is binary. A card with intermediate lateral evidence? | card JJ.6 is the first step and needs no ruling |
| JJ5.Q1 | The "in my path" criterion: lane overlap of the other's body (recommended) rather than the collision box? | card JJ.6 (it proceeds with the recommendation if unanswered) |
| S15.Q4, S15.Q1, S15.Q2, S15.Q3 | a second proximity rule beside looming; the comfort band; the standoff citation; the Eq. 51 kinematic point | nothing |
| REV22.Q3 | The colleague's name sits in the unpushed commits `fbb9020` and `4fead53`; rewrite history before pushing? | the next push |
| REV22.Q5 | Adopt "pre-stated script in its own commit before the run" as a standing rule (§2 rule 4 already says so) | nothing |

Earlier and still open, the ones that matter most: **EL.Q4** (blocks card EL.2, the comfort-zone
deliverable, since 2026-09-03), **PC1.Q4**, **EX2.Q1**, **JJ1.Q4**, **GM.Q4**, **HO.Q1**, and the
naturalistic set (NAT.*, GM1A.Q1 — do **not** adopt GM1A.Q1's recommendation; the review found the
card's σ_a conditions on the lead not braking).

## 4 The plan: cards for a less expensive model, in order

Each card follows the pattern of `replication/czb/jj5_looming_preference.py`: a docstring that says
where the card comes from, what is computed, the rule, and the predictions; committed before the
run; a report in `out/` generated by the script; a worklog paragraph with queries; one commit.
Cells, folds and metric are always card JJ.2's (imported from `jj2_rollout_cutin.py`; 378 cells,
leave-one-starting-TTC-out, weighted RMSE), unless the card says otherwise. Scores are read against
the comparators in §1. **Budget** is a guide; if a card runs past twice its budget, stop, record
where it stands, and move on.

### ~~Card JJ.6~~ — done 2026-09-22 (JJ.6 to JJ.6e; the gate DERIVED in JJ.6e). The text below is the original brief, kept for the record; do not rerun.

### Card JJ.6 (original brief) — the intention belief as the gate

*Question.* Does card JJ.1's fan, read as "the probability that the other's body is in the ego's
lane within the next T seconds", reproduce card G.1's fitted gate, so that the gated looming rule
can be written with the gate **derived** from the intention belief and nothing fitted but the
response model's three parameters?

*Do.* (1) In `src/rollout/looming_pref.py` add `gate="lane_overlap"`: the other is in the ego's
path at a step when |dy| ≤ 1.75 + w_other/2 (the studies' 3.5 m lane; `LANE_EDGE_M` in
`predictor.py`), and a function `p_in_lane(belief, fut, T)` = the share of futures in which that
holds at some step ≤ T. Property tests: a certain keeper gives 0; a certain changer gives 1 for T
above the crossing time; the prior gives about p0 for T large. (2) Script
`replication/czb/jj6_belief_gate.py`: per cell, on the corrected fan (`keep_body_in_lane=True`,
seed 0, n = 200), compute p_in_lane at T ∈ {1, 2, 3, 4, 6} s; take the looming axis from
`out/cutin2_cells.csv` exactly as card EL.1b's `cutin2_looming.py` defines it (import, do not
retype); fit the three-parameter threshold model to **p_in_lane(T) × Φ(...)**, i.e. card G.1's
`predict_gated` with the gate column replaced by the fan's value and (m_lat, s_l) not fitted.
Primary T = 3 s (card G.1's horizon). (3) Report the per-cell correlation between p_in_lane(3 s)
and G.1's fitted gate (`cutin2_gate.gate(0.149, log 0.990, l0, ldot)` on `lateral_states`), and
the scores.

*Rule.* (a) post-onset held out within 0.01 of the gated looming rule's 0.1027 (the ungated 0.1137
is the floor: the fan gate must not hurt); (b) pre-onset below 0.05 with nothing fitted on the
pre-onset cells. Verdict: **DERIVED** if (a) and (b) at T = 3 s; **DERIVED AT ANOTHER HORIZON** if
at some other T (report all, choose none by score; say which); **NOT DERIVED** otherwise. Also
report the rank correlation of the fan gate with G.1's gate.

*Prediction to write in the docstring.* Post-onset the posterior is 1.0 and the fan gate → 1 within
1–2 s, so (a) holds at 3 s. Pre-onset the posterior is 0.07 and G.1's gate is 0.03–0.07, so (b)
is plausible but not certain: the fan's changers reach the lane within about 1.5 s, which makes
p_in_lane(3 s) ≈ p0 in every pre-onset cell, a constant, where G.1's gate grades with the lateral
rate. If (b) fails, the reason is the binary posterior (`update_intention` in `belief.py` gives
0.07 or 1.00), and that is the finding: the belief needs a graded likelihood, not the gate.

*Budget.* Half a day. Numbers to quote come only from the report.

### Card JJ.7 — the preference over the looming observation, per driver (after: nothing; JJ.6e supplies the gate in closed form, `norm.cdf((0 - l0 - ldot*3)/(0.33*3))` on `cutin2_gate.lateral_states`)

*Question.* Written as an active-inference preference prior over the looming observation
channel, with the gate from JJ.6, does the per-driver level reproduce card TR.1's trait?

*Do.* Read `out/driver_levels.md` and `driver_levels.csv` (card TR.1) and `out/stage1_looming.md`
(card G1.Q1) first. The construction: a driver's preference is a one-sided Gaussian over θ̇ with
mean θ̇_0 (the driver's level) and sd (the driver's precision, card JJ.4's reading); the pragmatic
value at the freeze is its residual, gated by JJ.6's p_in_lane; the response model is the same
threshold model. Fit θ̇_0 per driver with the same hierarchical estimator TR.1 used (import it),
on the cut-in only. Rule: the per-driver θ̇_0 agrees with TR.1's cut-in levels at Spearman above
+0.9 (it should be nearly the same fit written in different words; if it is not, say why), and
with TR.1's left-turn levels inside TR.1's interval [+0.407, +0.798] over the 43 drivers in both.
*Prediction.* Both hold, because the construction is the gated looming rule restated. The card's
value is the restatement: it is the comfort-zone boundary as a preference prior, which is what
the JJ program asked for, with the intention belief as the gate.

*Budget.* Half a day plus the fits (5–35 min each, background, log).

### Card JJ.9 — the gate's σ from lane-keeping data (after: highD access; JJ6E.Q1)

The one circular constant in JJ.6e is σ = 0.33 m/s, set from G.1's fitted s_l. Measure it: the
standard deviation of the lateral rate of vehicles holding their lane over a 0.3 s window, on
highD (`src/generative/` has the loaders; `gm1a_lead_acceleration.py` the windowing pattern).
Rule, pre-stated: if the measured σ, put into JJ.6e's closed form with m = 0, still passes (a)
and (b), the gate is a *prediction* of the generative model and no longer a restatement. Report
the gate's pre-onset value it implies (0.05 at 0.33) beside G.1's 0.067.

### Card D.1 — the documents (after REV22.Q1)

If Jonas says "revise": rewrite the through-line of `docs/active_inference_reformulation.md`,
`docs/waymo_program_revisit.md` §1 and §6, and `docs/strand1_build_note.md` §5 to say what
`docs/review_2026-09-22.md` §1–§2 says, keeping the dated banners as the record; rebuild docx and
PDF; update `docs/active_inference_program.md` §13 with the cards run (JJ.2 to JJ.5b, S1.5, S1.6)
and their verdicts in one table. If he says "banners": rebuild the three PDFs so the banners are
in them, nothing else. Either way: add S13.Q1–Q4 to the worklog as `@S13.Q1(...)` lines copied
from `handover_2026-09-22.md` §5 and §8 so the register has them (they are cited but were never
written).

*Budget.* Two hours.

### Card EX2.Q2 — the 15-minute one (after: nothing; parked item, Jonas asked to be reminded)

Refit card TT.1 (`replication/czb/ltapod_testtrack.py`) with card EX.2's session term, so that
"the video at first exposure sits within 0.03 s of the track" gets an interval. Follow
`replication/czb/ex2_first_exposure_levels.py`; report the offset with its SE. Commit.

### Card P.1 — the planner, corrected (after RE4B.Q1 = rerun)

Card JJ.2b's planner pass with (i) `lane_centre` set to the ego's recorded lateral position (as
`re4b_lane_centre.py` does by wrapping `belief_at` and `staging`), (ii) `agent.a_applied` set to
the coasting value the ego holds, and (iii) the brake test reading the whole plan (any step
below −1 m/s²), not step 0; three planner seeds; rule (e) on the seed spread. Then RE.4's two
planner-side functionals rescored. Slow (the CEM planner over 378 cells × 3 seeds; hours);
background with a log.

### Not for this model without a new instruction

Anything on the VCC track; any rewrite of handbook chapters beyond dated notes; card EL.2 (after
EL.Q4; it is the deliverable and a capable session should run it); the naturalistic plan (needs
the data); rebuilding the "lateral factor" (REV22.Q2); any email or message to anyone.

### Review gate

After JJ.6 and JJ.7, a capable model reviews before anything is written into the handbook or
the program document: verify every quoted number against the reports, check that the rules were
applied as pre-stated, and that JJ.7's "restatement" claim is not circular in a way the card did
not declare.

## 5 When to stop and ask instead of proceeding

Write the query (§2 rule 7), finish what does not depend on it, and end the turn if nothing else
remains. Stop whenever a step would change a default, a pre-registered script or a tracked output
by hand; a result contradicts a document (report both numbers and both files; do not "fix" the
document); a card's "after" query is unanswered; a pre-stated rule would need reinterpreting to
reach a verdict; a parameter value has no motivation you can write down; a deck or document may
have been hand-edited by Jonas; the task is about the scope or positioning of a paper; or the
action is outward-facing (email, publishing, anything sent to anyone).

**Do not read `OthersWork/`.** **Do not use the observed PET column of the test-track data as the
stimulus** (SetPET is the stimulus).

## 6 The documents that matter, by purpose

| purpose | file |
|---|---|
| **the review, and its checks** | `docs/review_2026-09-22.md` (+ PDF, docx); `replication/czb/review_2026_09_22_checks.py` → `out/review_2026_09_22_checks.md`; the reviewers' scratch in `replication/review_2026-09-22/` |
| the measurement model in plain words | handbook `docs/handbook/13_glossary.md`; the concepts deck; `handover_2026-09-22_standing_superseded.md` §1 |
| the software in blocks | `docs/software_overview.md` (2026-09-16; does not yet cover `src/rollout/`) |
| the cut-in's axis, gate and level | `replication/czb/out/cutin2_looming.md`, `out/cutin2_gate.md`, `out/stage1_looming.md`, `out/driver_levels.md` |
| the rollout construction | `docs/rollout_boundary_design_note.md`, `handover_jj1_implementation.md`, `src/rollout/` (`belief`, `predictor`, `policies`, `efe`, `boundary`, **`admissible`**, **`looming_pref`**), `src/comfortzone/margin.py` |
| the JJ program and the arc's argument documents (read with their banners) | `docs/active_inference_program.md`, `docs/active_inference_reformulation.md`, `docs/waymo_program_revisit.md`, `docs/strand1_build_note.md` |
| the night's cards | `out/s15_comfort_threshold.md`, `out/s16_admissibility.md`, `out/re4b_lane_centre.md`, `out/jj2c_released_flags.md`, `out/jj5_looming_preference.md`, `out/jj5b_horizon_functional.md` |
| the decisive negative results and their scope | `docs/r2_gate_decisions.md`, `docs/r2_pipeline_review.md`, `out/cutin2_field_vs_gap.md`; and now the review |
| the real-driving anchor | handbook appendix 17, `out/ltapod_testtrack.md` |
| the worklog (source of truth) and the register | `replication/czb/out/worklog.md`, `out/query_register.md` |
| the cards and the standing rules | `docs/czb_work_orders.md` |
| the decks | `presentation/talk/README.md`, `docs/skill_additions_video.md` |
| Volvo Cars without moving the data (paused) | `docs/split_site_protocol.md`, `transfer/` |
| the meeting documents | `docs/handout_schumann_2026-09.md` (+ PDF; the docx is committed and never rebuilt), `correspondence/` |
| the data and its traps | `docs/czb_study1_data_plan.md`; `external/01_studies/DATA_DICTIONARY.md`; `external/README.md` |

## 7 Environment notes

Windows 11, Python 3.14 with torch CPU-only, pandoc on PATH, no LaTeX, no GPU. `gh` is installed and
logged in. The repository lives in OneDrive: an open Word or PowerPoint file is locked. `external/`,
`papers/` (except READMEs) and `OthersWork/` are not tracked; `.pptx` decks are gitignored. A full
rollout pass over the 378 cells takes 1–3 minutes; the CEM planner pass takes hours; a hierarchical
stage-1 fit 5–35 minutes. Run anything longer than a minute in the background with a log.
