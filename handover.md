# handover.md — start every session here

*Rewritten 2026-09-03 for a less capable model; updated 2026-09-13; **updated 2026-09-17** after the
arc of 2026-09-16 → 09-17 (GZ2.Q2, card PC.1, the software overview). Dated records, newest first:
**`handover_2026-09-17.md`**, `handover_2026-09-13.md`, `handover_2026-09-03.md`,
`handover_2026-09-02.md`. This file says what the project is, what the model now is and what it
rests on, what the rules are, what is waiting on Jonas, what to do in what order, and when to stop
and ask. It does not repeat the science; the documents it points to do that. Where this file and
the repository disagree, the repository wins, and you should say so in your reply.*

> ## RESUME HERE — model switch, 2026-09-17 evening, nothing authorized
>
> Jonas is moving to a more capable model. State: tree clean apart from his own
> `docs/handout_schumann_2026-09.docx` (Word edits; never stage or rebuild onto it); suite green at
> 31/33/40/96/62/20/28/27/16/30 (ten files, §0 step 2); nothing pushed since commit `ff0507a` (push only
> when he asks, with `git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin main`).
> The dated record of the day is **`handover_2026-09-17.md`**, parts 1 and 2. What the day settled:
>
> 1. **GZ2.Q2, done.** The released model's spontaneous re-plan in steady following is suppressed by the
>    assumed noise on the lateral and heading channels, through the belief update (GZ2.Q3 open, minor).
> 2. **Card PC.1, done, not adopted.** One fixed-horizon projected-conflict gate does not generalize; the
>    anticipation horizon is the scenario's own. **PC1.Q4 for Jonas.**
> 3. **Cards EX.1 and EX.2, done.** Exposure shifts the criterion, not the gate, at population level only;
>    **first exposure is now the primary setting** for the levels (cut-in median 0.034 rad/s, left-turn
>    video PET_50 2.42 s against the track's 2.45 s). **EX2.Q1 for Jonas** (handbook and deck numbers).
> 4. **highD and inD requested; plan written** (`docs/naturalistic_data_plan.md`), NAT.Q1–Q4 answered;
>    starts only on access and his word. Comfort-zone cards first, then NM.1.
> 5. **Perspectives for a colleague (JJ)** (worklog, 2026-09-17 evening): eight cognitive framings with
>    tests; recommended range-frequency theory, a starting-point diffusion model, affordance boundaries.
>    References unverified. May become cards or a literature search.
> 6. **The six points (JJ) answered** (late evening): `docs/active_inference_program.md` (+ docx, pdf, eight
>    figures). Proposes a policy-comparison quantity dG in nats as the axis, with rollouts of the ego's policies
>    against a predictive fan; ten cards under prefix JJ. Jonas ruled on JJ.Q1–Q6 the same evening (§13 of that
>    document): **JJ.1 is authorized and written** (`docs/rollout_boundary_design_note.md`); on 2026-09-18 Jonas
>    read it and said **"go", with the implementation by a less expensive model**: the implementer's brief is
>    **`handover_jj1_implementation.md`** (start there if you are that model). Both preference variants run; no
>    steering in the menus; the interpretability benchmark stays ours. He will add more of JJ's input over several
>    sessions: extend the program document, do not start a new one. **Never name the colleague or the company in
>    any document; the code is JJ.**
> 7. **The generative-model framework** (`docs/generative_model_framework.md`; `src/generative/`, 28 checks;
>    card GM.0 done, `out/gm0/`): prepared on highD/inD, to run at VCC through the interface. GM.Q1 (yes), GM.Q2
>    (Jonas applies for exiD) and GM.Q3 (stop at C1–C4 for now) are ruled; the schema revision is drafted in
>    `transfer/schema_revision_proposal.md` and **not sent**. Open for Jonas: **JJ.Q5, JJ1.Q4, JJ1.Q5, GM.Q4,
>    ATTR.Q1.** The VCC track stays paused.
>
> Quick wins if he asks: EX2.Q2 (refit TT.1 with the session term, ~15 min) turns the indicative "video
> at first exposure sits within 0.03 s of the track" into a result with an interval. §1 below quotes the
> pooled numbers with dated notes; §4's queue predates this arc.

> **The arc of 2026-09-13, in four lines** (full record in `handover_2026-09-13.md`). Surprise as the onset
> of a response was tested and did not replace the anticipatory gate (card HS.1); Farewell's emergency
> braking levels do not carry over to comfort judgments (PT.1); a crossing norm for cut-ins is proposed
> (PN.1); switching the dormant gaze system on showed that the released configuration does not hold
> sustained car following (GZ.1). **The VCC track is paused.** Jonas meets Julian Schumann the week
> after 2026-09-13; the handout and his private questions are ready for his review (HO.Q1).
> Earlier and still open from the authors'-edition review: **AH.Q1**, **AH.Q3** (for Jonas), **AH.Q2**
> (for review).

## 0 What to do when a session starts

1. Read this file in full. Then read `docs/czb_work_orders.md` §2 (the standing rules)
   and the card or note named for the task at hand. Do not read the papers or the handbook
   unless the card says to; do not open `OthersWork/` (§5).
2. Run the test suite exactly like this, and confirm 31, 33, 40, 96, 62, 20, 28, 27, 16, 30 and 28 passed:
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
   ```
   (`pytest` reports fewer and is *not* the suite; the files are scripts that count checks. The
   tenth file, `test_conflict.py`, was added with card PC.1 on 2026-09-16; the eleventh,
   `test_generative.py`, with the generative-model framework on 2026-09-17.)
3. Run `git status` and `git log --oneline -5`. The tree should be clean. If it is not,
   stop and report what is uncommitted before doing anything.
4. If Jonas said "load handover.md" and nothing else: reply with a short statement of
   where things stand (four or five sentences from §1) and the table in §3, then stop and
   wait. Do not start a card until he names one.
5. If Jonas named a task: find it in §4, check its "after" condition against §3, and if the
   condition is met, do it. If it is not met, say which query blocks it and stop.

## 1 Where the project stands, in plain terms

**What it set out to do.** Measure drivers' comfort-zone boundaries (CZB) with one scalar
borrowed from a published active-inference driver model: its preference field. Two
pre-registered tests on human video data went against that scalar (gates R.1 and R.2,
`docs/r2_gate_decisions.md`); a review explained why (`docs/r2_pipeline_review.md`).

**What the model is now** (handbook chapter 13, "the measurement vocabulary", defines every
term; the concepts deck animates each one):

> share who intervene = lapse + (1 − lapse) × **GATE** × Φ((**AXIS** − **LEVEL**) / spread)

- **The gate** says whether the other vehicle counts yet: the probability that its lateral
  clearance, projected 3 s ahead at its current closing rate, falls below a minimum. Fitted
  on post-onset cells it predicted the pre-onset cells out of sample (card G.1,
  `replication/czb/out/cutin2_gate.md`: 0.032; m_lat 0.149 m, s_l 0.990 m). The gate is the
  part that changes between scenarios. **Tested 2026-09-13 and not a substitute: surprise as
  the onset** (card HS.1, `out/hs1_situational_surprise.md`). A parameter-free gate at the
  surprise onset keeps every pre-onset cut-in clip closed (0.036) but scores 0.145 post-onset
  against G.1's 0.103; in the cyclist overtake and the left turn participants respond *before*
  any surprise registers, whether taken about the other road user or about the whole situation.
  The reading on file (HS1.Q3, answered "go" 2026-09-16): what starts a response is anticipated conflict,
  which is what G.1's projection computes. **Tested as one construction for every scenario on
  2026-09-17 (card PC.1, `out/pc1_projected_conflict.md`) and not adopted:** a projected path conflict
  with one fixed horizon reproduces G.1 on the cut-in only as a step (credited by 0.0001), is open
  throughout the overtake, and is closed on the left turn at every horizon to 6 s where people respond
  to a car still five to seven seconds from the crossing. The anticipation horizon is the scenario's
  own (PC1.Q4, for Jonas). Also tested and lost on these judgments:
  accumulating looming from the onset (0.196 against a state threshold's 0.144), and the
  own-lane norm's trust withdrawal as the onset (0.288, card PN.1).
- **The axis** is the number read off the scene. On the cut-in it is the **optical expansion
  rate** (how fast the other car grows in the eye, θ̇ ≈ W Δv / gap²): held-out error 0.113
  against 0.152 for gap alone and 0.347 for the field, at the noise floor 0.118
  (`out/cutin2_looming.md`, card EL.1b; it is the equal-weighted log-gap/log-TTC rule of
  card EL.1, `out/cutin2_two_axis.md`). On the left turn it is the oncoming vehicle's
  **distance** (0.056; time 0.112; the looming rate ties distance at 0.054 because the
  scenario has one speed per cell; no second axis earns its place; card B.3.v2,
  `out/ltap_two_axis.md`).
- **The level** is where one driver says "now" on the axis; drivers' levels form a
  population whose percentile is the deliverable. On the cut-in the stage-1 estimator on the
  gated looming axis (card G1.Q1, `out/stage1_looming.md`) gives median 0.032 rad/s (1.8°/s) pooled
  over all showings [2026-09-17: at first exposure, now primary, 0.034 rad/s and 80th percentile
  0.071 rad/s; card EX.2, `out/ex2_first_exposure_levels.md`],
  80th percentile 0.066 rad/s, spread 0.87 log units; it beats the old field axis by 14.9
  held-out log-likelihood units and is now the primary. A 5-point percentile step moves the
  implied trigger by 0.24 s against 0.52 s from the level's own uncertainty.
- **The trait**: the per-driver level is largely the same person across four scenarios
  (about 69% of the reliability ceiling, `out/cross_scenario_consistency.md`). Since
  **card TR.1** (`out/driver_levels.md`, `out/driver_levels.csv`) this also holds of the
  *fitted* levels, not just the model-free propensity: over the 43 drivers who appear in both,
  the cut-in level (rad/s) and the left-turn level (s of PET) agree at Spearman **+0.647**
  (bootstrap +0.407 to +0.798) against **+0.659** for the model-free propensity on the same
  drivers. Two of the four scenarios only — the truck overtake has no axis or gate (B.2
  unstarted) and the cyclist overtake's level is not fitted (B.1.Q1). The two levels are never
  put on one scale; that is EL.2, gated on EL.Q4.

**Jonas's standing ruling on genericity (2026-09-03).** The *machinery* is scenario-agnostic —
gate, axis, level, percentile over driver levels — and the *axis* is scenario-specific and may
be multi-dimensional. Every scenario runs the EL.1-style second-axis test with its pre-stated
0.01 held-out margin before its axis is fixed; a one-dimensional axis is a finding, never an
assumption. On the cut-in a second axis DID earn its place (gap 0.1522 against the 2-D rule
0.1137); it is *named* one-dimensionally only because the fitted weight came out at 0.497, at
which weight the rule is algebraically the looming rate. On the left turn it did not
(+0.0018, inside the margin), because that design holds one oncoming speed per cell.

**The real-driving anchor** (handbook appendix 17, `out/ltapod_testtrack.md`, card TT.1).
Jonas's 2013 test-track study of real left turns (`external/02_LTAPOD_DBIN/`), fitted with the
same model as the video left turn at 50 km/h: median comfort boundary 2.45 s on the track,
2.18 s on video (−0.27 s, SE 0.20, inside the design resolution); the video-fitted
population applied to the track with nothing refitted scores 0.200 against the track's own
0.231 and chance 0.289 — it carries over; drivers are four times sharper in the car
(within-driver spread 0.20 s against 0.86 s); the graded ratings' slopes match. The paper's
numbers reproduce from its protocol. The dread (hurried) boundary is parked by Jonas's
decision. Not tested on the track: the axis and the gate (one speed, fixed decision moment).

**A colleague's parallel analysis** (handbook appendix 16): a required-deceleration model on
the same cut-in data, fitted by another LLM session. Both approaches find gap first with a
speed exponent of about 0.4–0.5 (which is what a looming threshold implies), both reject
deceleration-type cues, both find a reliable per-driver criterion. Their fixed-horizon gate
is where our gate came from. The folder `OthersWork/` is gitignored and is not context.

**Presentations** (`presentation/talk/README.md`): the 60-minute talk, the 15–20 minute
project-group deck, the 10–15 minute status deck, and the concepts deck, now at
**`ai_czb_concepts_talk-v8.pptx`** (19 slides, 12 animated, notes budget 29.1 min) after three
review rounds with Jonas on 2026-09-03. Animation S1 (the belief cloud) is built; S2–S7 are
specified in the shot list.

*The concepts deck's animations are embedded as H.264 `.mp4` through `add_movie`, not as GIFs,
so PowerPoint gives a scrub bar and a pause that resumes.* Three rules were learned the hard
way and are now enforced in `make_concept_animations.save()`; break any of them and the videos
go wrong silently:
1. **Render once, then transcode.** Never call `anim.save()` twice on one `FuncAnimation`. The
   second pass replays from frame 0 with the artists still holding the first pass's final
   state, and these frame functions only ADD to their artists — so every `.mp4` opened with the
   whole animation already drawn while the `.gif` was fine.
2. **The poster is the FIRST frame, taken from the GIF** (`Image.open(gif); im.seek(0)`). A
   last-frame poster makes the slide wipe itself when played; re-calling `fn(0)` produces a
   hybrid still for the same artist-state reason.
3. **Verify the video, not the slide still.** The still comes from the poster and can be right
   while the video is wrong. Extract frame 0 of each `.mp4` with ffmpeg and diff it against
   frame 0 of the `.gif`. Do not compare frame counts — GIF encoders merge identical
   consecutive frames, so a 112-frame animation may be stored as 7.

The full set of lessons, written for the `chalmers-slide-generation-jonas` skill, is
`docs/skill_additions_video.md`; Jonas intends to fold it into the skill.

## 2 The rules that bind every session (long form: `docs/czb_work_orders.md` §2)

1. **Every number you quote comes from a committed script with a tracked output.** No
   numbers from an interactive session; if you computed something to decide, write the
   script, run it, commit it, quote its output file.
2. **The suite passes before and after every card** (§0 step 2). New behavior gets new
   property checks in the same `check(...)` style.
3. **Never change a default in `src/aidriver/preferences.py`** (new behavior behind a flag
   that defaults off; `lane_entry_horizon_s` is the example). **Never modify a script whose
   docstring says "pre-registered"** (`cutin2_field_vs_gap.py` above all; also the cards of
   2026-09-02); write a new script that imports it.
4. **Pre-state before you run.** Models, folds, metric and the decision rule go in the
   script's docstring before the run. If you must change something after a run (a bound, a
   bug, a resource cut), say so in the docstring with the date and record both numbers in
   the worklog; never quietly rerun.
5. **Documents:** US English; the `.md` is the source of truth; build with
   `pandoc docs/X.md -o docs/X.docx --from markdown --resource-path docs` and
   `python docs/build_pdf.py docs/X.md`; handbook chapters with
   `python docs/handbook/build_handbook.py NN` then `python docs/handbook/build_combined.py`;
   no period at the end of a heading; opinions marked as opinions; never invent a reference.
   `PermissionError` on a build means the file is open in Word or PowerPoint: write a `-vN`
   copy and say so.
6. **Questions go in the worklog, not in chat, and do not stop the work.** Append an entry
   to `replication/czb/out/worklog.md` in the form of the last entries, write each question
   as `@<CARD>.Q<n>(<severity>, <who>): ...` (`blocker` / `judgment` / `minor`; `jonas` /
   `review`), then run `python replication/czb/collect_queries.py`. Continue with everything
   that does not depend on the answer.
7. **Commit at the end of each card** with a message saying what changed and why, ending
   with the `Co-Authored-By` line the recent commits use. Do not push unless Jonas asks.
8. **Presentations:** never rerun a deck build script onto a file Jonas may have edited
   (copy and augment instead; see `presentation/talk/README.md`). Render on a *copy* in the
   scratchpad through PowerPoint COM; never call `$ppt.Quit()`.
9. **Editing files: use the Write and Edit tools, not shell heredocs.** Every shell-heredoc
   edit that carried a `\n` inside a string literal in this arc produced a literal newline
   and a syntax error, and the last one cost an hour. Read the target lines first, then Edit.
10. **Long runs:** launch in the background with output redirected to a log in
    `replication/czb/out/`, and have the script write its main report *before* any bootstrap
    so the pre-stated decision never waits on the slow part. Before calling a run stuck,
    check its CPU time (`Get-Process python | select CPU, StartTime`); a 200-resample
    bootstrap that refits a multi-start model per fold takes hours on 18 cells. Background
    agents die when the usage limit hits; their scripts do not, so relaunch the script.

## 3 What is waiting on Jonas, and what each answer unblocks

The register is `replication/czb/out/query_register.md` (compiled from the worklog; 66 open before
the gaze card's queries were added on 2026-09-13). Do not start a gated item until its query is
answered in the worklog with a `RESOLVED <id>:` line.

**Raised by the 2026-09-13 overnight batch, for Jonas** (details in the worklog entry of that date
and in `handover_2026-09-13.md`):

| query | question, in one line | unblocks |
|---|---|---|
| HS1.Q3 (**answered 2026-09-16: go**) | Should card PC.1 (a scenario-agnostic projected-conflict gate) be the next card? Jonas: "go with 1, and then 2" | §4 items 0a, 0b-now |
| GZ2.Q3 (minor, review) | The mechanism inside the belief update by which looser assumed lateral noise empties the imagined futures of collisions: record the filter's effective sample size and the reference plan's unsafe share (two 14-step runs) | nothing; only if the finding goes to Julian as more than "the lateral senses" |
| **PC1.Q4** (judgment) | Card PC.1's result: which reading to carry forward — a scenario-specific anticipation horizon for the gate (generic machinery, scenario parameter, like the axis), or G.1's gate on the cut-in only, with no gate where the other road user counts from the outset (overtake, left turn)? | the wording of "the gate" in handbook chapter 13 and the concepts deck; whether PC1.Q5's signed clearance is worth adding |
| **EX2.Q1** (judgment) | Card EX.2 makes first exposure the primary setting: cut-in median 0.032 → 0.034 rad/s, 80th 0.066 → 0.071; left-turn video PET_50 2.18 → 2.42 s, video-to-track offset −0.27 → about −0.03 s. Dated notes in handbook ch. 13 and appendix 17, and update the concepts deck's numbers? | the document sweep; the deck |
| EX1.Q1–Q3 (minor / judgment, review) | the 0.5 reliability convention; A4's threshold shift is uninterpretable because the axis weight was refitted per showing; the left-turn change is confounded with the session | nothing |
| PC1.Q1–Q3, Q5, Q6 (judgment / minor) | the planned reading's use of the recorded future as "what the participant knew"; persistence; the engaged-cell margin; a signed clearance to restore G.1's graded gate; the 0.6 m residual between the two readings on the cut-in | nothing |
| **GZ2.Q1** (judgment) | Wording of the sustained-following finding in the handout and private questions: confirm | printing the handout |
| **GZ1.Q1** (judgment) | The released configuration does not hold sustained car following (it brakes after 3–5 s with nothing happening, some repeats to a stop, with gaze choice on or off and with the authors' own scripted lead). It is in the handout as a question for Julian: keep it? | the handout's glance question |
| **GZ1.Q3** (judgment) | Fitting the model's own glances to SHRP2 is a model-design task first (a reason to look away, a noise-dependent cost, a non-instant look-back), then days of simulation. Pursue, or ask Julian first? | any gaze-fitting card |
| **HO.Q1** (minor) | Before printing the handout for Julian: complete three references shown as "[initials]", and confirm the wording for the data sources and the colleague credited with the gate | printing `docs/handout_schumann_2026-09.pdf` |
| **PT1.Q1** (judgment) | May the reading "Farewell's emergency-braking level sits near the quarter point of our comfort curve" be said to Julian? It compares shapes, not one quantity | the handout's section 3.5 wording |
| HS1.Q1, PN1.Q1 (judgment) | σ0 = 0.1 m as the noticeable positional discrepancy is not a verified threshold; the crossing norm's 0.5 m/s lower bound is unverified against naturalistic lane-change durations | nothing blocks; both are stated as unverified |
| HS1.Q2, HS1.Q4, HS1.Q5, PN1.Q2 (review) | retire card Q5.1; a study-2 manoeuvre-onset bug in `load_cutin_trace`; study-1 longitudinal position jitter; retire the old `cutin_norm_weight` | housekeeping |

**Answered by Jonas on 2026-09-03** (do not re-ask): **Q5.Q1** yes, the two-object framing
stands, so card Q5.1 is unblocked. **EL.Q1** population **B** — the percentile is over drivers'
boundary levels throughout, which makes EL.2 the deliverable and EL.3 a check. **EL1.Q1** yes,
adopt the two-scalar wording, with the standing genericity ruling in §1 as the caveat.

| query | question, in one line | unblocks |
|---|---|---|
| **EL.Q4** (judgment) | The old EL.Q2 restated after Jonas said it was opaque: each scenario's axis is in different units (rad/s, s, m), so what does EL.2 divide by to share one population? Recommendation on file — normalise by each scenario's between-driver spread, with the design-span version reported as a sensitivity | **card EL.2**, the largest blocked item |
| **G1R.Q3** (judgment) | The paperwork half of the old G1R.Q1 (its generic half is settled by the §1 ruling): dated notes in the roadmap and scope map saying the deliverable is a percentile over driver levels on *each scenario's own axis*; regenerate card C's report on the looming axis? | the document sweep in §4 item 6 |
| DECK.Q1 (**resolved 2026-09-03 by verification**) | The Xue et al. (2018) citation is real (*Accid. Anal. Prev.* 118, 114–124; reference 10 of the Nature Communications paper) and its abstract says τ⁻¹ fitted better than θ̇ for both threshold and accumulator models. The deck's wording stands | nothing; the deck may be shown as worded |
| **DECK.Q4** (judgment) | The deck's title slide names the model "a gated threshold model of the comfort-zone boundary", filling Jonas's placeholder. Accept or rename | one string in `build_concepts_talk.py` |
| C.Q2 (judgment) | Should the percentile deliverable stay on the deficit axis? **Stale** — G1.Q1 already moved it to looming. Flagged to Jonas as closable; he has not ruled | nothing |
| ANIM.Q1 (minor) | Build order for animations S2–S7; a labeled synthetic figure acceptable? | §4 item 4 |
| TT.Q1, TT.Q3, TT.Q4 (judgment / minor) | Go = not intervening on video?; 26 versus the paper's 22 participants; the orientation of the video's PS rating | wording in appendix 17; a small rerun if TT.Q3 says drop four drivers |
| TT.Q2 | which PET the dread boundary lives on | parked by Jonas; do nothing |
| B3.Q1 (resolved by assumption) | the Random LTAP clip ends at 13.5 s | re-run `ltap_two_axis.py` only if Jonas gives another number (`T_DECISION_S` in `src/comfortzone/ltap.py`) |
| REV.Q1–Q3, TALK.Q1–Q3, Q5.Q2–Q3, EXT.Q1–Q3, F1.Q1, G1.Q2, G1R.Q2, DECK.Q3 | wording, attribution, small options | nothing; answer when convenient |

## 4 The queue, in order, with what "done" means

0a. ~~**GZ2.Q2: which state channel suppresses the spontaneous re-plan.**~~ **Done 2026-09-16**: parts C, D
   and E in the same script; the lateral and heading channels (`y_sd`, `theta_sd`, `delta_sd`, `w_sd`)
   carry it, through the belief update and not the planner's sampled observations (D3); the in-path
   exemption is not the mechanism (E0/E2, share 1.000 in both); open as GZ2.Q3. The original brief follows
   for the record. Authorized 2026-09-16.
   Context: card GZ.2 (`replication/causation/gz2_following_braking.py`, report
   `replication/causation/gz2/gz2_following_braking.md`, worklog entry of 2026-09-16) showed that in
   steady following (15 m/s, 1.5 s headway, lead at constant speed) the released model re-plans by
   itself at step 13 and brakes, driven entirely by the collision-and-safety shortfall (0.0764
   evidence per step). ×100 noise on the three looming channels changes nothing (condition C2, 0.0757);
   ×100 on the seven state channels stops it (C3, 0.0023, no re-plan). **Do:** add two part-C
   conditions to the same script, in its docstring before running, T = 14, batch 4, same readings:
   **D1** ×100 on the ego-longitudinal channels only (`x_sd`, `v_sd`, `a_sd`) and **D2** ×100 on the
   lateral and heading channels only (`y_sd`, `theta_sd`, `delta_sd`, `w_sd`). Mechanism in the script:
   list the keys under `_decoder_x100`; conditions whose tag starts with a letter other than B run
   `PART_B_STEPS` = 14 steps — extend that test to include `D`. Reading: whichever of D1/D2 lands near
   C3's 0.0023 carries the effect; then check the route (the planner scores futures on observations
   sampled with this noise, `BeliefReward(sample_mean=False)`, `src/common/belief_reward.py`). Run in the
   background (`python replication/causation/gz2_following_braking.py --only D1`, then D2, then
   `--report`); steps take 5–100 s depending on machine load. **Done** = report regenerated, worklog
   paragraph with `RESOLVED GZ2.Q2`, commit, and one line added to the handout's "Why it brakes"
   bullet and the private questions' point 6 — rebuilding their PDFs as `-v3` copies if the originals
   are locked, and never touching `docs/handout_schumann_2026-09.docx`.

0b-now. ~~**THEN — card PC.1, authorized 2026-09-16**~~ **Done 2026-09-17**; see the banner and the worklog.
   The construction is `src/comfortzone/conflict.py` (30 property checks), the design note has a result
   section (§6b), and the verdict is: not adopted. The original steps follow for the record. Steps: (1) write
   `docs/projected_conflict_gate_note.md`: the construction (the ego's predicted path against the other
   road user's predicted path, both extrapolated over a fixed horizon from recent motion; the gate is
   the probability that the two come within a minimum clearance, generalizing card G.1's
   `Phi((m_lat - (l0 + ldot*t_enc))/s_l)`), how it reduces exactly to G.1 on the cut-in, what it
   computes in the cyclist overtake (ego pulling out toward a steady cyclist) and the left turn (ego
   turning across an oncoming car), and the pre-stated rule; (2) implement in `src/comfortzone/` with
   property tests in the `check()` style, including the reduction to G.1; (3) a script in the style of
   `replication/czb/hs1_situational_surprise.py` (whose scene loaders `scene_tracks` and
   `study2_scenes`, and first-study jitter settings, can be imported) scoring it on the cut-in with
   G.1's two criteria (CP1 out of sample < 0.05; post-onset held-out ≤ 0.1027 + 0.01) and reporting
   when the gate opens in the overtake and left-turn cells against when participants respond. Watch
   the two traps card HS.1 hit: measure each study's jitter floor before choosing any spread, and
   restrict every statistic to what participants were shown.

0. **Do not run card Q5.1 as pre-stated** (query HS1.Q2, 2026-09-13). Its predictor spread
   cannot register a lane change at all (a fixed-horizon constant-velocity predictor sees at most
   a·h²/2; at its settings a lane change would need ~5.6 m/s² of lateral acceleration), and its
   tests 1 and 2 are answered, with corrected settings, by card HS.1. The proposed replacement
   is item 0b.

0b. **Card PC.1 (authorized 2026-09-16, not started) — a scenario-agnostic projected-conflict gate.**
   HS1.Q3 answered "go". Card HS.1's reading is that the response starts at *anticipated* conflict. PC.1 would
   generalize G.1's gate from "lateral clearance projected 3 s ahead" to "the ego's path against
   the other road user's predicted path", computed the same way in all four scenarios, and test
   it with G.1's criteria on the cut-in plus the overtake and left-turn cells where surprise came
   too late. Write the design note first; pre-state the rule; no per-scenario geometry.

1. **Card EL.2 — one level per driver across every scenario's rule**
   (`docs/czb_ellipse_design_note.md` §6). After **EL.Q4** (EL.Q1 is answered: population B).
   Card **TR.1** (`out/driver_levels.md`) is the diagnostic that motivates it and is already
   done — per-driver fitted levels for the two scenarios that have a current rule, each in its
   own units, agreeing at Spearman +0.647. EL.2 is what puts them on one scale, which is
   exactly what EL.Q4 must settle first. The cut-in's form is the
   gated looming rule (G.1 + EL.1b), the left turn's is distance (B.3.v2), the cyclist
   overtake's is lateral clearance (B.1); the level population is shared. Deliverable: a
   script in the EL.1 style with a pre-stated rule, output `out/el2_shared_level.md`.
2. ~~**Card Q5.1 — world surprise on the data in hand**~~ Superseded 2026-09-13; see item 0.
3. **Card B.2 — the truck overtake.** No construction note exists. Write one first in the
   pattern of `docs/ltap_construction_note.md` (measure the traces with a committed script,
   name the gate for the scenario, state both routes, pre-state the comparison), and stop
   for review before coding.
4. **Animations S2 → S7** (`presentation/talk/animation_shot_list.md`). After ANIM.Q1. S1 is
   built (`make_belief_animation.py`); the concept animations (`make_concept_animations.py`)
   are the pattern for captions inside the frames.
5. **The looming accumulator — the R.1 follow-up.** R.1 rejected *our* deficit-driven
   accumulator; the standard architecture accumulates looming (Xue et al. 2018; Markkula
   2021). Write a design note first (what is accumulated, the anticipation confound of
   repeated clips, the pre-stated rule), then a card. Judgment-heavy: leave to a capable
   session if one is available.
6. **The document sweep** after G1R.Q1 and EL1.Q1: dated notes in
   `docs/czb_validation_roadmap.md` and `docs/active_inference_scope_map.md` moving the
   percentile deliverable to the looming axis; regenerate card C's sensitivity report on it;
   update the status and short decks' notes where they say "gap leads".
7. **PAUSED by Jonas, 2026-09-11 — do not work on this until he starts a new VCC round.**
   Everything below is the state it was left in, for when he does.
   **Naturalistic data, at Volvo Cars, without moving it.** The data request
   (`docs/data_requirements.md`) stands; appendix 17 gives the first offset number (a quarter
   of a second on the left turn). The data will stay at VCC, with no shared repository; the
   way of working is the **split-site protocol** (`docs/split_site_protocol.md`, PDF for
   VCC's sign-off; the rules in `transfer/transfer_policy.yaml`; the tool
   `transfer/bundle.py`; the interface `transfer/interface_schema.yaml` with a synthetic
   fixture; the brief for either site's LLM `transfer/SITE_LLM_BRIEF.md`; the generic method
   is the `split-site-collaboration` skill, mirrored in `docs/skills/`). Waiting on VCC's
   sign-off (query SS.Q1).
   **Card NDS.1 is done** (2026-09-09): `src/comfortzone/interface.py` reads the interface
   into the gated-looming pipeline by the video cards' own definitions of gap, clearance and
   looming rate; `replication/czb/nds1_interface_smoke.py` → `out/nds1_interface_smoke.md`
   runs it end to end on the synthetic fixture, all four pre-stated criteria met;
   `tests/test_interface.py` has 28 property checks. **It found five gaps in the interface
   schema** (NDS.Q2–NDS.Q5), two of them severe enough to make the fitted levels wrong by a
   factor of about two. **The next step is one action: revise
   `transfer/interface_schema.yaml` with Jonas's rulings and send the corrected schema to
   VCC before their adapter is written** — decision 6 of the protocol offers them that
   review, and after the adapter exists a change is expensive.

Not to be started without a new instruction: **anything on the VCC track** (the schema
revision NDS.Q2–Q5, the policy fix SS.Q5, any bundle, anything sent to VCC — paused by Jonas
2026-09-11; its queries stay open in the register, parked rather than stale); any handbook chapter rewrite beyond dated
notes, manuscript text, any change to a pre-registered script, card EL.3, the dread
boundary (TT.Q2), anything in `OthersWork/`.

## 5 When to stop and ask instead of proceeding

Write the query (§2 rule 6), finish what does not depend on it, and end the turn if nothing
else remains. Stop whenever:

- a step would change a default in `src/aidriver/preferences.py`, a pre-registered script,
  or a tracked output by hand;
- a result contradicts a document (report both numbers and which file each came from; do
  not "fix" the document);
- a card's "after" query is unanswered;
- a decision rule written in advance would need reinterpreting to reach a verdict;
- you would need a parameter value with no motivation you can write down;
- a deck or document may have been hand-edited by Jonas since it was built;
- the task is about scope or positioning of a paper.

**Do not read `OthersWork/` as context.** It is a shortcut to a colleague's external analysis;
what the project takes from it is in handbook appendix 16. Open it only when Jonas asks for
work on it. **Do not use the observed PET column of the test-track data as the stimulus**;
SetPET is the stimulus (appendix 17 and TT.Q2 say why).

## 6 The documents that matter, by purpose

| purpose | file |
|---|---|
| the model in plain words, every term defined | handbook `docs/handbook/13_glossary.md` ("the measurement vocabulary"); the concepts deck `presentation/talk/build_concepts_talk.py` |
| **the software in blocks, for jumping into the work** | `docs/software_overview.md` (+ docx, pdf; 2026-09-16): the repository as six engines with inputs and outputs, one figure per block naming the files, a "where to go for a question" table, the tests and the rules |
| the cut-in's axis, gate and level (the three cards) | `replication/czb/out/cutin2_looming.md`, `out/cutin2_gate.md`, `out/stage1_looming.md`; the field attribution `out/cutin2_field_horizon_gate.md` |
| the left turn | `docs/ltap_construction_note.md` (§5b has the result), `replication/czb/out/ltap_two_axis.md`, `src/comfortzone/ltap.py` |
| the real-driving anchor | handbook `docs/handbook/17_appendix_test_track.md`, `replication/czb/out/ltapod_testtrack.md`, `notes/06_bargman2015_ltapod_testtrack.md`, `external/README.md` |
| the external analysis, read in our terms | handbook `docs/handbook/16_appendix_external_rh_model.md` |
| the decisive negative result and its scope | `docs/r2_gate_decisions.md`, `docs/r2_pipeline_review.md`, `replication/czb/out/cutin2_field_vs_gap.md` |
| what survives (the trait, the boundary distribution) | `replication/czb/out/cross_scenario_consistency.md` (model-free), **`out/driver_levels.md` + `.csv` (card TR.1: the same question of the fitted levels)**, `out/stage1_summary.md` (the old deficit axis, superseded), `out/percentile_sensitivity.md` |
| **the authors' edition of the handbook, and its review** | `docs/handbook_authors/` (2026-08-24, **revised 2026-09-03**; does not track the internal handbook — see its README), `docs/method_review.md` (2026-08-23), `docs/authors_handbook_review_brief.md` (the starting brief), and the worklog entry of 2026-09-03 (evening, capable session) listing every revision; **the authors' reply (2026-09-11)**, private, at `correspondence/2026-09-11_authors_reply_to_method_review.md` — read it before writing anything to the authors; for the September 2026 conference meeting with Julian Schumann, the paper handout `docs/handout_schumann_2026-09.md` (+ PDF) and Jonas's private question list `correspondence/2026-09_meeting_schumann_questions.md` (+ PDF) |
| **how the decks and their animations are built** | `presentation/talk/README.md`, and **`docs/skill_additions_video.md`** — the video pipeline and its traps, written to be folded into the `chalmers-slide-generation-jonas` skill |
| the design notes | `docs/surprise_without_the_field.md`, `docs/czb_ellipse_design_note.md`, `docs/ltap_construction_note.md`, `docs/lane_entry_note.md`, `docs/overtake_construction_note.md` |
| the cards and the standing rules | `docs/czb_work_orders.md` |
| the worklog (source of truth for decisions and queries) and the register | `replication/czb/out/worklog.md`, `out/query_register.md` |
| the decks and the animations | `presentation/talk/README.md`, `presentation/talk/animation_shot_list.md` |
| **working with Volvo Cars without moving the data** | `docs/split_site_protocol.md` (+ PDF, the sign-off document), `transfer/README.md`, `transfer/transfer_policy.yaml`, `transfer/SITE_LLM_BRIEF.md`, `tests/test_transfer.py`; the skill mirror `docs/skills/split-site-collaboration.SKILL.md` |
| **the 2026-09-13 overnight cards** | situational surprise as the onset: `src/surprise/situational.py`, `replication/czb/out/hs1_situational_surprise.md`; Farewell's emergency levels against comfort judgments: `out/pt1_farewell_thresholds.md`; the cut-in norm: `src/comfortzone/norms.py`, `out/pn1_cutin_norm.md`, **`docs/cutin_norm_proposal.md`** (+ PDF, for Julian); the dormant gaze system switched on: `replication/causation/gz1/gz1_gaze_choice_probe.md` (and `gz1/thw1.5/`); the arc's record `handover_2026-09-13.md` |
| **the naturalistic path: reading the interface, and what the schema still lacks** | `src/comfortzone/interface.py`, `transfer/interface_schema.yaml`, **`replication/czb/out/nds1_interface_smoke.md`** (card NDS.1: the convention gap quantified, and the five schema gaps), `tests/test_interface.py` |
| the data and its traps | `docs/czb_study1_data_plan.md`; the study's `DATA_DICTIONARY.md` under `external/01_studies/` (read its gotchas first); `external/README.md` for the test-track file's columns |
| the deep research context and environment (older) | `HANDOFF.md`, then the dated handovers `handover_2026-08-26.md` → `handover_2026-09-03.md` in order |

## 7 Environment notes

Windows 11, Python 3.14 with torch CPU-only, pandoc on PATH, no LaTeX, no GPU. `gh` is installed and logged in (2026-09-16; see the banner for pushing).
The repository lives in OneDrive: an open Word or PowerPoint file is locked, so write a
versioned copy rather than fight the lock. `external/` and `papers/` (except their READMEs)
and `OthersWork/` are not tracked. The `.pptx` decks are gitignored; their build scripts,
figures and GIFs are tracked. A hierarchical stage-1 fit takes 5–35 minutes; a
leave-one-driver-out set of refits a similar time; run them in the background with a log
and a waiter, never through a pipe to `tail`.
