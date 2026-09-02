# handover.md — start every session here

*Rewritten 2026-09-02 for a less capable model, by the tier-1 session that ran the
2026-09-01 → 09-02 arc (its dated record: `handover_2026-09-02.md`). This file says
what the project is, what the rules are, what is waiting on Jonas, what to do in what
order, and when to stop and ask. It does not repeat the science; the documents it
points to do that. Where this file and the repository disagree, the repository wins,
and you should say so in your reply.*

## 0 What to do when a session starts

1. Read this file in full. Then read `docs/czb_work_orders.md` §2 (the standing rules)
   and the cards it points you to for the task at hand. Do not read the papers or the
   handbook unless the card says to.
2. Run the test suite exactly like this, and confirm 31, 33, 40 and 96 passed:
   ```bash
   python tests/test_surprise.py
   python tests/test_comfortzone.py
   python tests/test_causation.py
   python tests/test_cutin.py
   ```
   (`pytest` reports fewer and is *not* the suite; the files are scripts.)
3. Run `git status` and `git log --oneline -5`. The tree should be clean. If it is not,
   stop and report what is uncommitted before doing anything.
4. If Jonas said "load handover.md" and nothing else: reply with a short statement of
   where things stand (three or four sentences from §1) and the list in §3, then stop
   and wait. Do not start a card until he names one.
5. If Jonas named a task: find its card (§4), check its "runs after" condition against
   §3, and if the condition is met, do the card. If it is not met, say which query
   blocks it and stop.

## 1 Where the project stands, in plain terms

The project set out to measure drivers' comfort-zone boundaries (CZB) with one scalar
borrowed from a published active-inference driver model: its preference field. Two
pre-registered tests on human data both went against that scalar. At review gate R.1
the field's accumulation over time failed to predict *when* people respond; at gate R.2
the field lost to a simple gap threshold as the criticality axis, scoring worse than
chance on the study built to separate them (`docs/r2_gate_decisions.md`). A review of
that decisive pipeline on 2026-09-02 confirmed the result and explained it: about 44%
of the loss is a lane-entry gate the project itself added, which suppresses the field
exactly where participants respond most; the rest is the published model's worst-case
counterfactual, which ranks situations by speed where people rank them by distance
(`docs/r2_pipeline_review.md`).

What survives is the project's headline: **each driver carries one comfort-zone level
that is largely shared across four scenarios** (about 69% of the reliable per-driver
signal, measured with no field at all), and **the best criticality axis on the data so
far is the longitudinal gap**, with TTC close behind. The program now builds the
*comparator class*: per-scenario two-observable rules and the CZB ellipse (a joint
percentile over two observables), with the per-driver level shared across scenarios.
Three design notes from 2026-09-02 say how: `docs/surprise_without_the_field.md` (what
"surprise" can still mean; a card to test it), `docs/czb_ellipse_design_note.md` (what
the ellipse is and what the data can identify about it; cards EL.1–EL.3), and
`docs/ltap_construction_note.md` (the left-turn scenario, which separates time from
distance by design; card B.3.v2).

Card EL.1 (a second axis on the second cut-in study) has run; its verdict is in
`replication/czb/out/cutin2_two_axis.md` and the line below.

> **EL.1 verdict (2026-09-02):** a second axis **earns its place** on the second cut-in
> study. A linear rule in log gap and log TTC scores held-out wRMSE 0.114 against the
> 1D log gap's 0.152, at the sampling-noise floor (0.118, which is conservative); the
> quadratic form scores 0.115, so parsimony keeps the linear rule. The fitted weight is
> 0.47–0.51 on log gap in every fold: the two trade off one-for-one on the log scale,
> which is a threshold on the geometric mean of gap and TTC. Consequence for the
> program: the criticality axis on the cut-in is two-dimensional and linear on the log
> scale; card EL.2 should carry the linear rule as the cut-in's form, and the R.2
> headline's "gap leads" is now "gap leads among single scalars; a two-scalar linear
> rule reaches the noise floor" (query EL1.Q1 asks Jonas to confirm that wording).
>
> **Three cards run later the same day** (records in the worklog, outputs in
> `replication/czb/out/`): **EL.1b** — the equal-weight rule IS a threshold on the optical
> expansion rate (gap × TTC = width / looming rate); fitted directly it scores 0.113, so the
> cut-in axis is the classic looming variable. **G.1** — a fixed-horizon (3 s) lateral-
> clearance gate in front of the rule predicts the pre-onset cells out of sample (0.032)
> and improves the post-onset fit (0.103): the model is now gate × axis × level. **F.1** —
> the same horizon idea in the field's lane-entry weight lifts the field from 0.347 to
> 0.261 (attribution confirmed) but it stays far behind the gap; the flag
> `lane_entry_horizon_s` defaults off and nothing depends on it.

## 2 The rules that bind every session (short form; the long form is `docs/czb_work_orders.md` §2)

1. **Every number you will quote comes from a committed script with a tracked output.**
   No numbers from an interactive session. If you computed something to decide, write
   the script, commit it, quote its output file.
2. **The suite (§0 step 2) passes before and after every card.** New behavior gets new
   property tests in the same style (`check(...)` calls that count).
3. **Never change defaults in `src/aidriver/preferences.py`.** New behavior goes behind a
   flag that defaults off. Never modify a script whose docstring says "pre-registered"
   (`replication/czb/cutin2_field_vs_gap.py` above all); write a new script that imports
   it.
4. **Documents:** US English; the `.md` is the source of truth; build Word and PDF with
   `pandoc docs/X.md -o docs/X.docx --from markdown --resource-path docs` and
   `python docs/build_pdf.py docs/X.md`; no period at the end of a heading; state
   opinions as opinions ("the way I read it", "it seems"); never invent a reference. If
   a build fails with `PermissionError`, the file is open in Word: write `X-v2.md`/`-v2.docx`
   and say so.
5. **Questions go in the worklog, not in chat, and do not stop the work.** Append an
   entry to `replication/czb/out/worklog.md` (see the last entries for the form), write
   each question as `@<CARD>.Q<n>(<severity>, <who>): ...` with severity `blocker`,
   `judgment` or `minor` and who `jonas` or `review`, then run
   `python replication/czb/collect_queries.py` to regenerate the register. Continue
   with everything that does not depend on the answer.
6. **Commit at the end of each card** with a message that says what changed and why,
   ending with the `Co-Authored-By` line the recent commits use. Do not push unless
   Jonas asks (`github-token-handoff` skill if he does).
7. **Presentations:** never rerun a deck build script onto a file Jonas may have edited
   by hand (both decks in `presentation/talk/` are at risk; see that README). Render
   decks through PowerPoint on a *copy* in the scratchpad and never call `$ppt.Quit()`.
8. **Shell:** long heredocs with mixed quotes fail to parse here. Put edit text in a
   Python script written with the Write tool and run that; commit with `git commit -F`.
   Run anything over a minute in the background with its output redirected to a log
   file in `replication/czb/out/`, and never pipe a background job through `tail`.

## 3 What is waiting on Jonas, and what each answer unblocks

The register is `replication/czb/out/query_register.md`. These are the ones that gate
work; do not start the gated card until the query is answered in the worklog.

| query | question, in one line | unblocks |
|---|---|---|
| **Q5.Q1** (judgment) | Is "surprise defines the onset, a population percentile defines the level" the working framing? | card Q5.1 |
| **EL.Q1** (judgment) | Is the ellipse's percentile over pooled observed states or over drivers' boundary levels? | card EL.2, EL.3 |
| **B3.Q1** (minor) | Where does the Random-design LTAP clip end (assumed 13.5 s, before turn onset)? | card B.3.v2's covariates |
| EL.Q2, EL.Q3 (minor) | the scale convention for EL.2; whether the CAMP rear-end data are in scope | EL.2; the CAMP part of EL.1 |
| ANIM.Q1 (minor) | build order of the animations; whether a labeled synthetic figure is acceptable | the shot list |
| REV.Q1–Q3, TALK.Q1–Q3, Q5.Q2–Q3 | wording and attribution questions | nothing; answer when convenient |

Everything else in the register predates this arc and is listed there with its status.

## 4 The queue, in order, with what "done" means

Each item has a card. Read the card and the note it points to before starting; the
note is the specification and the card is the pointer.

1. **Card B.3.v2 — the LTAP scenario** (`docs/ltap_construction_note.md` §2 and §5).
   After B3.Q1. Add to its comparison a fourth model, the oncoming vehicle's looming rate
   (width × speed / distance²), so that the cut-in's axis is tested on a crossing geometry;
   the geometry predicts it will NOT be the LTAP cue (the note's §1 residual runs the other
   way), and that contrast is worth having on the record. Deliverables: `src/comfortzone/ltap.py` (roles by yaw span; turn onset;
   conflict point; the two observables at the decision moment), property tests as
   listed in the note, `replication/czb/ltap_two_axis.py` running the note's
   pre-stated comparison with leave-one-PET-level-out folds, output
   `out/ltap_two_axis.md`. Do not write a field (preference-function) term for LTAP;
   the note's §3 explains why and it is Jonas's ruling.
2. **Card Q5.1 — world surprise on the data in hand**
   (`docs/surprise_without_the_field.md` §6). After Q5.Q1. Uses only `src/surprise/`
   and the trace loaders; four pre-stated tests; output `out/world_surprise.md`.
3. **Card EL.2 — the shared level across scenarios on the ellipse forms**
   (`docs/czb_ellipse_design_note.md` §6). After B.3.v2 and EL.Q1/EL.Q2.
4. **Animations S1 → S7** (`presentation/talk/animation_shot_list.md`). After ANIM.Q1;
   S1 (the belief cloud) can be built first regardless, following
   `presentation/talk/make_event_animation.py` as the template. Three status animations
   already exist (`make_status_animations.py`: the model on one cut-in, the scoreboard, the
   trait) and are the pattern for captions inside the frames.
5. **Card B.2 — the truck overtake.** No construction note exists yet. Write one first,
   in the pattern of `docs/ltap_construction_note.md` (measure the traces with a
   committed script, state both routes, pre-state the comparison), and stop for review
   before coding.

Not in the queue and not to be started without a new instruction: any handbook
revision (Jonas reviews it first), any manuscript text, any change to the registered
R.2 comparison, and card EL.3 (it needs naturalistic data the project does not have).

## 5 When to stop and ask instead of proceeding

Write the query (§2 rule 5), finish what does not depend on it, and end the turn if
nothing else remains. Stop whenever:

- a step would change a default in `src/aidriver/preferences.py`, a pre-registered
  script, or a tracked output by hand;
- a result contradicts a document (a number in a note, the gate record, a handover);
  report both numbers and which file each came from, and do not "fix" the document;
- a card's "runs after" query is unanswered;
- a decision rule written in advance would need reinterpreting to reach a verdict;
- you would need a parameter value with no motivation you can write down;
- a deck or document may have been hand-edited by Jonas since it was built;
- the task is about scope, positioning of a paper, or which scenario counts as in
  scope (the standing scope decision: only the active-inference papers are in scope for
  the literature; the CAMP data are a query, EL.Q3).

**Do not read `OthersWork/` as context.** It is a shortcut to a colleague's external
comfort-zone analysis (a required-deceleration model fitted to the same cut-in study by
another LLM session). It is not this project's work and nothing here depends on it. What
the project takes from it is written down once, in handbook appendix 16
(`docs/handbook/16_appendix_external_rh_model.md`); read that if a task touches it, and
open the external folder only when Jonas explicitly asks for work on it.

## 6 The documents that matter, by purpose

| purpose | file |
|---|---|
| the decisive negative result and its scope | `docs/r2_gate_decisions.md`, `docs/r2_pipeline_review.md`, `replication/czb/out/cutin2_field_vs_gap.md`, `out/cutin2_lane_gate_diagnostic.md` |
| what survives (the trait, the boundary distribution, the transfer) | `replication/czb/out/cross_scenario_consistency.md`, `out/stage1_summary.md`, `out/transfer_overtake_summary.md`, `out/percentile_sensitivity.md` |
| what the project uses of active inference, in one place | `docs/active_inference_scope_map.md` |
| the three cards of 2026-09-02 that shaped the model (looming axis, anticipatory gate, field attribution) | `replication/czb/out/cutin2_looming.md`, `out/cutin2_gate.md`, `out/cutin2_field_horizon_gate.md` |
| the three decks (60 min, 15-20 min, 10-15 min status) | `presentation/talk/README.md` |
| the three design notes of 2026-09-02 | `docs/surprise_without_the_field.md`, `docs/czb_ellipse_design_note.md`, `docs/ltap_construction_note.md` |
| the cards and the standing rules | `docs/czb_work_orders.md` |
| the worklog (source of truth for decisions and queries) and the register | `replication/czb/out/worklog.md`, `out/query_register.md` |
| the two talks and the animation shot list | `presentation/talk/README.md` |
| how earlier scenarios were built (the pattern to follow) | `docs/lane_entry_note.md`, `docs/overtake_construction_note.md` |
| the external required-deceleration analysis, read in our terms (early work; the folder itself is not context) | `docs/handbook/16_appendix_external_rh_model.md` |
| the data and its traps | `docs/czb_study1_data_plan.md`; the study's own `DATA_DICTIONARY.md` under `external/01_studies/` (read its "gotchas" before touching the joint file) |
| the deep research context, environment and parameter traps (older) | `HANDOFF.md`, then the dated handovers `handover_2026-08-26.md` → `handover_2026-09-02.md` in order |

## 7 Environment notes

Windows 11, Python 3.14 with torch CPU-only, pandoc 3.10 on PATH, no LaTeX, no `gh`,
no GPU. The repository lives in OneDrive: an open Word or PowerPoint file is locked, so
write a versioned copy rather than fighting the lock. `external/` is not tracked (the
OSF deposit, the authors' code and the study data are restored per `external/README.md`).
The full-population causation CSVs are gitignored and regenerable. The `.pptx` decks are
gitignored; their build scripts and figures are tracked. Background Python jobs die
after their next checkpoint if their shell is closed; check for orphans before
relaunching a long job.
