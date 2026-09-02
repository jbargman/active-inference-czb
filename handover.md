# handover.md — start every session here

*Rewritten 2026-09-03 for a less capable model, by the tier-1 session that ran the
2026-09-01 → 09-03 arc (dated record: `handover_2026-09-03.md`; the previous arc's record:
`handover_2026-09-02.md`). This file says what the project is, what the model now is and
what it rests on, what the rules are, what is waiting on Jonas, what to do in what order,
and when to stop and ask. It does not repeat the science; the documents it points to do
that. Where this file and the repository disagree, the repository wins, and you should say
so in your reply.*

## 0 What to do when a session starts

1. Read this file in full. Then read `docs/czb_work_orders.md` §2 (the standing rules)
   and the card or note named for the task at hand. Do not read the papers or the handbook
   unless the card says to; do not open `OthersWork/` (§5).
2. Run the test suite exactly like this, and confirm 31, 33, 40, 96 and 62 passed:
   ```bash
   python tests/test_surprise.py
   python tests/test_comfortzone.py
   python tests/test_causation.py
   python tests/test_cutin.py
   python tests/test_ltap.py
   ```
   (`pytest` reports fewer and is *not* the suite; the files are scripts that count checks.)
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
  part that changes between scenarios.
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
  gated looming axis (card G1.Q1, `out/stage1_looming.md`) gives median 0.032 rad/s (1.8°/s),
  80th percentile 0.066 rad/s, spread 0.87 log units; it beats the old field axis by 14.9
  held-out log-likelihood units and is now the primary. A 5-point percentile step moves the
  implied trigger by 0.24 s against 0.52 s from the level's own uncertainty.
- **The trait**: the per-driver level is largely the same person across four scenarios
  (about 69% of the reliability ceiling, `out/cross_scenario_consistency.md`).

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
project-group deck, the 10–15 minute status deck, and the concepts deck (`-v2`: one animated
slide per term; Jonas reviewed v1 and v2 answers his points; v2 awaits his look). Animation
S1 (the belief cloud) is built; S2–S7 are specified in the shot list.

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

The register is `replication/czb/out/query_register.md` (40 open). Do not start a gated item
until its query is answered in the worklog with a `RESOLVED <id>:` line.

| query | question, in one line | unblocks |
|---|---|---|
| **EL.Q1**, EL.Q2 (judgment) | Is the ellipse's percentile over observed states or over drivers' levels; which scale convention? | card EL.2 |
| **Q5.Q1** (judgment) | Is "surprise defines the onset, a population percentile defines the level" the working framing? | card Q5.1 |
| **G1R.Q1** (judgment) | Amend the roadmap and scope map to the looming axis; regenerate card C's report on it? | the document sweep in §4 item 6 |
| **EL1.Q1** (judgment) | Adopt the wording "gap leads among single scalars; a two-scalar rule (= looming) reaches the noise floor"? | the same sweep |
| ANIM.Q1 (minor) | Build order for animations S2–S7; a labeled synthetic figure acceptable? | §4 item 4 |
| TT.Q1, TT.Q3, TT.Q4 (judgment / minor) | Go = not intervening on video?; 26 versus the paper's 22 participants; the orientation of the video's PS rating | wording in appendix 17; a small rerun if TT.Q3 says drop four drivers |
| TT.Q2 | which PET the dread boundary lives on | parked by Jonas; do nothing |
| B3.Q1 (resolved by assumption) | the Random LTAP clip ends at 13.5 s | re-run `ltap_two_axis.py` only if Jonas gives another number (`T_DECISION_S` in `src/comfortzone/ltap.py`) |
| REV.Q1–Q3, TALK.Q1–Q3, Q5.Q2–Q3, EXT.Q1–Q3, F1.Q1, G1.Q2, G1R.Q2 | wording, attribution, small options | nothing; answer when convenient |

## 4 The queue, in order, with what "done" means

1. **Card EL.2 — one level per driver across every scenario's rule**
   (`docs/czb_ellipse_design_note.md` §6). After EL.Q1 and EL.Q2. The cut-in's form is the
   gated looming rule (G.1 + EL.1b), the left turn's is distance (B.3.v2), the cyclist
   overtake's is lateral clearance (B.1); the level population is shared. Deliverable: a
   script in the EL.1 style with a pre-stated rule, output `out/el2_shared_level.md`.
2. **Card Q5.1 — world surprise on the data in hand** (`docs/surprise_without_the_field.md`
   §6). After Q5.Q1. Uses only `src/surprise/` and the trace loaders.
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
7. **Naturalistic data.** The data request (`docs/data_requirements.md`) stands; appendix 17
   gives the first offset number (a quarter of a second on the left turn). Nothing to run
   until data arrive.

Not to be started without a new instruction: any handbook chapter rewrite beyond dated
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
| the cut-in's axis, gate and level (the three cards) | `replication/czb/out/cutin2_looming.md`, `out/cutin2_gate.md`, `out/stage1_looming.md`; the field attribution `out/cutin2_field_horizon_gate.md` |
| the left turn | `docs/ltap_construction_note.md` (§5b has the result), `replication/czb/out/ltap_two_axis.md`, `src/comfortzone/ltap.py` |
| the real-driving anchor | handbook `docs/handbook/17_appendix_test_track.md`, `replication/czb/out/ltapod_testtrack.md`, `notes/06_bargman2015_ltapod_testtrack.md`, `external/README.md` |
| the external analysis, read in our terms | handbook `docs/handbook/16_appendix_external_rh_model.md` |
| the decisive negative result and its scope | `docs/r2_gate_decisions.md`, `docs/r2_pipeline_review.md`, `replication/czb/out/cutin2_field_vs_gap.md` |
| what survives (the trait, the boundary distribution) | `replication/czb/out/cross_scenario_consistency.md`, `out/stage1_summary.md` (the old deficit axis, superseded), `out/percentile_sensitivity.md` |
| the design notes | `docs/surprise_without_the_field.md`, `docs/czb_ellipse_design_note.md`, `docs/ltap_construction_note.md`, `docs/lane_entry_note.md`, `docs/overtake_construction_note.md` |
| the cards and the standing rules | `docs/czb_work_orders.md` |
| the worklog (source of truth for decisions and queries) and the register | `replication/czb/out/worklog.md`, `out/query_register.md` |
| the decks and the animations | `presentation/talk/README.md`, `presentation/talk/animation_shot_list.md` |
| the data and its traps | `docs/czb_study1_data_plan.md`; the study's `DATA_DICTIONARY.md` under `external/01_studies/` (read its gotchas first); `external/README.md` for the test-track file's columns |
| the deep research context and environment (older) | `HANDOFF.md`, then the dated handovers `handover_2026-08-26.md` → `handover_2026-09-03.md` in order |

## 7 Environment notes

Windows 11, Python 3.14 with torch CPU-only, pandoc on PATH, no LaTeX, no `gh`, no GPU.
The repository lives in OneDrive: an open Word or PowerPoint file is locked, so write a
versioned copy rather than fight the lock. `external/` and `papers/` (except their READMEs)
and `OthersWork/` are not tracked. The `.pptx` decks are gitignored; their build scripts,
figures and GIFs are tracked. A hierarchical stage-1 fit takes 5–35 minutes; a
leave-one-driver-out set of refits a similar time; run them in the background with a log
and a waiter, never through a pipe to `tail`.
