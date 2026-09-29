# handover.md — start every session here

*Rewritten 2026-09-29 at the end of the 2026-09-22 to 2026-09-29 session. This is the standing
entry point. The dated records, newest first:*
- *`handover_2026-09-29.md`: the last arc, including what that session may have got wrong. Read it
  second.*
- *`handover_2026-09-28_standing_superseded.md`: this file as it stood before.*
- *`docs/review_2026-09-22.md`: the review. Read it before quoting anything from 09-18 to 09-22.*
- *`handover_2026-09-22.md`, `handover_2026-09-22_standing_superseded.md` (the fullest account of the
  measurement model, the test-track anchor and the decks), `handover_2026-09-17.md`,
  `handover_2026-09-13.md`, `handover_2026-09-03.md`.*

*The current state in plain words, for any reader, is `docs/handbook/18_where_czb_stands.md`.*

*Precedence: the repository beats any handover file, and the latest dated file beats earlier ones.
Where this file and the repository disagree, the repository wins, and you say so in your reply.*

## 0 What to do when a session starts

1. Read this file in full, then `handover_2026-09-29.md`, then `docs/czb_work_orders.md` §2 (the
   standing rules), then the card named for the task (§4). Do not read the papers or `OthersWork/`
   unless the card says to. Load the `performing-research` skill; it asks you to check that
   `docs/skills/performing-research.SKILL.md` matches the live copy, and to commit the difference if
   it does not.
2. Run the suite exactly like this and confirm 31, 33, 40, 96, 62, 20, 28, 27, 16, 30, 33, 35, 24,
   19, 24, 9 and 18 passed (seventeen files; `pytest` is *not* the suite):
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
   python tests/test_comfort_fe.py
   python tests/test_display.py
   ```
3. `git status` and `git log --oneline -5`. The tree should be clean apart from untracked `.log`
   files under `replication/czb/out/`. If anything else is uncommitted, stop and report it.
4. If Jonas said only "load handover.md": reply with five sentences from §1 and the table in §3,
   then stop and wait.
5. If he named a card: find it in §4, check its "after" condition, and do it if the condition is met.
   If it is not, say which query blocks it and stop. If he said "work through §4", do the cards in
   order in batch mode (`performing-research` skill §2): never block, raise queries, and report card
   by card.

## 1 Where the project stands

*Every number is from a committed script with a tracked output; the cards are named. Opinions are
marked. The long form is `docs/handbook/18_where_czb_stands.md`.*

**The aim.** Measure drivers' comfort-zone boundaries (CZB) with an active-inference driver model.
If a plain looming threshold fits better, explain that threshold in free-energy terms rather than
assume the framework fits (Jonas: "we should not just assume it works - we have to probe the
different ways to think about it").

**The measurement model** (second cut-in study, 288 post-onset cells, leave-one-starting-TTC-out):

> share who intervene = lapse + (1 − lapse) × GATE × Φ((log θ̇ − log θ̇₀) / σ)

- θ̇ is the cut-in vehicle's looming (card EL.1b).
- The gate is the probability that its sideways clearance projected 3 s ahead falls below a minimum
  (card G.1).
- Held-out scores: gated 0.103, looming alone 0.113, gap 0.152, TTC 0.168, chance 0.320. Before the
  lane change begins, the gated rule scores 0.032.
- The intervention curve: lapse 0.037, level 0.0320 rad/s, spread 1.29 (card JJ.10).
- The per-driver level is a trait: +0.65 across scenarios (card TR.1), +0.64 as a carried prior
  (card JJ.7).

**The free-energy reading, tested part by part.**
- The boundary is a prior over the looming of a lead. Additive sensory noise is rejected (JJ.8).
- The gate is the generative model's predictive uncertainty about the other's sideways motion
  (JJ.6e). Its σ was measured on real lane-keeping in highD, 0.125 m/s, and with nothing fitted it
  still predicts the video (0.1115 / 0.0340, card JJ.9).
- The two combine as F = P(lead) × excess (JJ.10).
- What the released model computes, a horizon-summed expected free energy, is ordered against the
  participants: across cells the sum counts the steps before contact, and within rows of equal TTC it
  is dominated by its value at contact (the review's check; JJ.12). It is a collision-avoidance
  quantity. The released planner brakes and steers from the first step on the video cells (P.1).

**Naturalistic data** (highD and inD, since 2026-09-24).
- The video curve transfers to real cut-ins in level (highD 1.21×).
- The axis does not transfer: real braking follows inverse TTC slightly better than looming (AUC 0.739
  against 0.713; NC.3, NC.3c). This is query NC3C.Q1.
- Hard braking (at least 2.5 m/s²) is too rare on the motorway to test.
- Gentle and hard are two levels on one looming axis in the second study (NC.3o). Real followers
  match the gentle curve at 1.08 m/s² (NC.3h).
- Real early responses before the lane switch follow looming to the cutter, not the lateral gate
  (NC.4c).
- The released model does not hold real steady following: it brakes in 56% of runs where the
  humans never brake (NM.1; also GZ.1, GZ.2).
- Its margin is silent over about 98% of real following (NM.2).
- Its response-time relation has the right direction on real data (NM.3).

**Which video data to trust** (card AC.1). The second study is the reference (serial dependence
+0.05). The first study's Button design is not a primary source (+0.32 within scenario); the Random
design is AC1.Q1.

**The monitor** (cards DT.1, DT.1b, DT.2; `docs/display_transform_explained.md`). The crowd-sourced
participants saw the rendering shrunk by k = 0.42: TTC is unchanged, looming × 0.42.
- If they judged the looming at their eye, three comparisons with real data reverse: the boundary
  falls below Farewell's emergency level, highD's level is 2.9× the video's, and the gentle match is
  at 0.66 m/s².
- But the left turn against the 2013 test track needs an effective gain of 0.99 [0.84, 1.05], so the
  participants judged as if the scene had not been shrunk.
- **Report cross-domain looming numbers both ways until the per-participant display test (DT2.Q1,
  card DT.3) decides.**

**In one sentence** (opinion): the comfort-zone boundary is a prior over the looming of a lead,
gated by the generative model's uncertainty about whether the object is one. What is unsettled is
whether real drivers' comfort braking lives on looming or on inverse TTC, and whether the video's
looming levels can be put next to real-world ones.

**Paused:** the VCC track. **Not sent:** the note to JJ, the email to Julian, and the authors' new
version. **Parked, Jonas asked to be reminded:** extending card JJ.4 (EX2.Q2, 15 min).

## 2 The rules that bind every session (long form: `docs/czb_work_orders.md` §2)

1. **Every number you quote comes from a committed script with a tracked output.** No result strings
   typed into a report generator; no numbers from an interactive session.
2. **The suite passes before and after every card** (§0 step 2). New behavior gets new property
   checks in the `check(...)` style, testing the claim.
3. **Never change a default in `src/aidriver/preferences.py` or in `src/rollout/`**; new behavior
   goes behind a flag that defaults off. **Never modify a script whose docstring says
   "pre-registered" or "pre-stated"**; write a new one that imports it.
4. **Pre-state, then commit, then run.** The card's script, with models, folds, metric, decision rule
   and predictions in its docstring, is committed **in its own commit before it runs**. Anything
   changed after a run is dated in the docstring, and both numbers go in the worklog.
5. **"Released" means `PreferenceParams(v_desired=v_ego)` and nothing else.** Say which staging you
   ran.
6. **Documents:** US English; the `.md` is the source. Build with
   `pandoc docs/X.md -o docs/X.docx --from markdown --resource-path docs` and
   `python docs/build_pdf.py docs/X.md`. The handbook has its own builders
   (`docs/handbook/build_handbook.py`, `build_combined.py`); revision marks `{{Rn}}` go at the start
   of a paragraph, and round 8 is the latest. No period at the end of a heading; opinions marked;
   never invent a reference. `PermissionError` means the file is open: write a `-vN` copy and say so.
   Never rebuild or stage `docs/handout_schumann_2026-09.docx`. The authors' edition that was sent
   (`docs/handbook_authors/aif_driver_model_handbook.md`) is never edited; newer versions are made by
   a script beside it.
7. **Questions go in the worklog, not in chat, and do not stop the work.** Each question is one
   paragraph, `@<CARD>.Q<n>(<severity>, <who>): ...`, followed by a blank line (the collector ends a
   query at the first blank line). Then run `python replication/czb/collect_queries.py`. Record
   answers as `RESOLVED <CARD>.Q<n>: ...`.
8. **Commit at the end of each card** with explicit paths (never `git add -A`) and the
   `Co-Authored-By` line. **Push only when Jonas asks**; the route is
   `git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin main`.
9. **Edit files with the Write and Edit tools**; shell heredocs have repeatedly broken on quotes and
   escapes. Read the target lines first.
10. **Long runs** go to the background with a log in `replication/czb/out/` (the `.log` files stay
    untracked). Check CPU time before calling a run stuck.
11. **The code for the colleague is JJ.** Not the name, not the company, not in commits.
12. **Naturalistic data stay outside the repository** (`C:\JonasLocal\D_Data`, caches in
    `C:\JonasLocal\D_Data_derived`). Only aggregates are committed, under the levelXdata licence.
13. **Cross-domain looming numbers are reported both ways** (rendered and display-corrected) until
    DT2.Q1 is answered. Within-study results and TTC results need no correction.

## 3 What is waiting on Jonas

The register is `replication/czb/out/query_register.md` (159 open, 8 blockers; 66 resolved). Do not
start a gated card until its query has a `RESOLVED` line. The ones that decide the most:

| query | the question | unblocks |
|---|---|---|
| **DT2.Q1** (blocker) | the per-participant display data for the subset that has it (screen or window size in pixels, physical size, displayed video size, any viewing distance) | card DT.3 |
| **DT1.Q1** (blocker) | confirm the display parameters (60 cm, 23-inch 16:9, 90°, full-screen video, camera position) | the corrected numbers |
| **NC3C.Q1** (blocker) | is the video's button press or real braking the operationalisation of the boundary (looming against inverse TTC)? | what the paper and the note to JJ may say |
| **AC1.Q1** (blocker) | how far to trust the first study's Random design | quoting TR.1, EX.2 and the left-turn video levels as final |
| HB.Q1 | send the authors' new version (2026-09-28), an addendum, or nothing; after Julian's reply | the authors |
| NC3H.Q1 | Malin Svärd's 99th percentile of deceleration at 110–130 km/h | the hard-braking anchor |
| NC1.Q1 | run the left-turn redesign (card NC.1b)? | card NC.1b |
| NC4C.Q1 | what gates real early responses (Jonas: people predict the traffic) | card NC.4d proceeds with the cheap candidate |
| EL.Q4 | (blocks the deliverable since 2026-09-03) | card EL.2 |
| JJ12.Q1 | the graded past accumulator | card JJ.13 |

**Outward-facing, waiting:** `correspondence/2026-09-25_draft_email_julian.md` (not sent; point 4
marked display-uncorrected) and `docs/note_for_jj_horizon_sum.md` (not sent; "do not send as it
stands").

## 4 The plan: cards, in order

### Card DT.3 — the per-participant display test (after: DT2.Q1, the data)

For each participant with display information, compute the gain k_i with
`comfortzone.display.load_geometry(...)`. Take their own level on the rendered-looming axis: a
per-driver fit as in card TR.1 or JJ.7, second study first. Pre-state: regress log level on log k_i
with a bootstrap over participants. **Slope −1**: they judged the looming at their eye, so the
transform applies. **Slope 0**: they judged a scene-relative quantity or TTC, so it does not.
Report the slope's interval against both, and the share of between-driver level variance explained
by log k_i. Pixel sizes alone give relative k_i, which is enough for the slope. Say so if the spread
of k_i is too small to separate −1 from 0; that is a result.

### Card NC.4d — the cutter's own leader as the gate (after: nothing; cheap)

Jonas's reading of NC4C.Q1: real drivers predict the traffic, for example a cutter closing on a
slower car in its own lane. Import `nc4c_isolated.py`'s extraction. At k = 2 s before the switch,
add the cutter's inverse TTC to *its* leader. Pre-state: this motive gate CONTRIBUTES if AUC(motive ×
core) − AUC(core) > 0 with a 95% bootstrap over recordings excluding zero, on the isolated events.
About an hour on the caches.

### Card NC.1b — left-turn gap acceptance timed at the conflict point (after: NC1.Q1)

Card NC.1 lost most accepted gaps because the oncoming vehicle was not yet in view at the decision
moment. Redesign with the critical-gap method: per turner, the gaps between successive oncoming
vehicles passing the conflict point (always in view), rejected gaps and the accepted one, then a
maximum-likelihood critical gap. Across oncoming speeds, ask whether acceptance follows time or
distance. It also decides reading A against B of card DT.2: do real drivers judge left-turn gaps by
distance, as the video participants did?

### Card D.2 — the horizon-sum sentence (after: nothing; small)

Add JJ.12's within-row mechanism, as a dated note, to `docs/looming_as_free_energy.md` and
`docs/note_for_jj_horizon_sum.md`. Both give only the across-cell one (see
`handover_2026-09-29.md` §5). Rebuild both. Do not send the note.

### Card NC.5-tau, the video half (after: nothing)

The released τ⁻¹ term, pointwise, on the second study with JJ.9's empirical gate, against 0.1027. The
highD half is done (blind by its floor). Pre-state a rule in the form NC.5-tau's highD half used.

### Card JJ.13 — the free energy with a memory (after: JJ12.Q1)

Accumulate JJ.10's F = P(lead) × excess over the past from the clip start. P(lead) comes from JJ.6e's
closed form at each step, and the level is fitted as the response model's level. It needs the
per-cell time series from the traces (`hs1_situational_surprise.study2_scenes`, and
`cutin2_gate.lateral_states`' method per step). Rule: JJ.2's (a) and (b). Prediction:
indistinguishable from the instantaneous rule on this design (closing is constant). The card's value
is a memory that naturalistic data can test. Half a day.

### Card JJ.11 — the gate's horizon (after: nothing; small)

Sweep T in {1, 2, 3, 4, 6} s in the closed form, with σT held at 0.99 m and, separately, with σ held
at 0.33. Report both curves and choose nothing; the product is whether T is identifiable here.

### Card EX2.Q2 — the 15-minute one (parked; Jonas asked to be reminded)

Extending card JJ.4, as in `handover_2026-09-22_standing_superseded.md`.

### Not for this model without a new instruction

Anything on the VCC track. Any rewrite of handbook chapters beyond dated notes. Card EL.2 (after
EL.Q4; it is the deliverable and a capable session should run it). Rebuilding the lateral factor. Any
email or message to anyone, including sending the authors' version or the note to JJ.

## 5 When to stop and ask instead of proceeding

Write the query (§2 rule 7), finish what does not depend on it, and end the turn if nothing else
remains. Stop whenever:
- a step would change a default, a pre-stated script or a tracked output by hand;
- a result contradicts a document (report both numbers and both files, and do not "fix" the
  document);
- a card's "after" query is unanswered;
- a pre-stated rule would need reinterpreting to reach a verdict;
- a parameter value has no motivation you can write down;
- a deck or document may have been hand-edited by Jonas;
- the task is about the scope or positioning of a paper;
- the action is outward-facing (email, publishing, anything sent to anyone).

**Do not read `OthersWork/`.** **Do not use the observed PET column of the test-track data as the
stimulus** (SetPET is the stimulus).

## 6 The documents that matter, by purpose

| purpose | file |
|---|---|
| **the current state, in plain words** | `docs/handbook/18_where_czb_stands.md` (the combined handbook: `docs/handbook/word/handbook_combined.docx`) |
| the last arc, and what it may have got wrong | `handover_2026-09-29.md` |
| the review, and its checks | `docs/review_2026-09-22.md`; `replication/czb/out/review_2026_09_22_checks.md` |
| the free-energy account | `docs/looming_as_free_energy.md`; `docs/active_inference_program.md` §14 (the card table); `src/rollout/comfort_fe.py` |
| the naturalistic data | `docs/naturalistic_data_plan.md`; handbook appendix 15.6; the NC, NM and JJ.9 outputs in `replication/czb/out/` |
| the monitor | `docs/display_transform.md` (spec and parameters), `docs/display_transform_explained.md` (figures, video, the left turn), `out/dt1_display_transform.md`, `out/dt1b_display_sensitivity.md`, `out/dt2_ltap_display.md` |
| the released model on real traffic | `out/nm1_replayed_following.md`, `out/nm1b_figure.md`, `out/nm2_following_preference.md`, `out/nm3_response_time.md`; `replication/causation/gz1/`, `gz2/` |
| the authors | `correspondence/` (their reply of 09-11; the draft to Julian); `docs/handbook_authors/` (the sent edition; `review_2026-09-28.md`; the new version `aif_driver_model_handbook_2026-09-28.md`, made by `make_version_2026_09_28.py`) |
| the real-driving anchor | handbook appendix 17; `out/ltapod_testtrack.md`; `out/dt2_ltap_display.md` |
| the worklog (source of truth) and the register | `replication/czb/out/worklog.md`, `out/query_register.md` |
| the cards and the standing rules | `docs/czb_work_orders.md` |
| the decisive negative results | `docs/r2_gate_decisions.md`, `docs/r2_pipeline_review.md`, `out/cutin2_field_vs_gap.md` |
| the decks | `presentation/talk/README.md` |
| Volvo Cars without moving the data (paused) | `docs/split_site_protocol.md`, `transfer/` |
| the data and its traps | `docs/czb_study1_data_plan.md`; `external/01_studies/DATA_DICTIONARY.md`; `external/README.md`; handbook appendix 15 |

## 7 Environment notes

- Windows 11; Python 3.14 with torch CPU-only; pandoc and ffmpeg on PATH; PyMuPDF for looking at PDF
  pages (no poppler, no LaTeX); no GPU. `gh` is installed and logged in.
- The repository lives in OneDrive: an open Word or PowerPoint file is locked. `external/`, `papers/`
  (except READMEs) and `OthersWork/` are not tracked; `.pptx` decks and the handbook's
  `word/`/`pdf/` builds are not tracked.
- Timings: a full rollout pass over the 378 cells, 1–3 minutes; the CEM planner, hours; the released
  model behind highD leads, about 20 minutes per episode batch of six; a hierarchical stage-1 fit,
  5–35 minutes. Run anything longer than a minute in the background with a log.
- The prompt log for this project is at `OneDrive - Chalmers\1_Work\Promptlogs\` (`prompt-log`
  skill).
