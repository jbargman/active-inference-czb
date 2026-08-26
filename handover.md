# handover.md — restart a session here

> **A later arc exists.** `handover_2026-08-26.md` covers the 2026-08-25 → 08-26 work: the
> equivalence/ROPE revision and the decisions taken about it, the severity-versus-timing
> diagnosis, the new human dataset in `external/01_studies/`, and the start of the cut-in
> scenario. Read this file first for standing context, then that one. Where the two
> disagree on the equivalence statistics, the later file wins. That arc is a single commit
> on `main`, so a net diff will not show the sequence of corrections inside it — its §8
> explains which ones to look for.

Written 2026-08-25, superseding the 2026-08-23 version. This is the **session entry
point**; it captures the 2026-08-23 → 2026-08-25 work arc (the method review, the
crash-causation study through its full-population results, handbook revision round 2).
The older `HANDOFF.md` remains the deep research context (scope decisions, environment
constraints, parameter traps) — this file does not repeat it, and where its §6 open-item
list disagrees with §5 below, this file wins.

## 0 What "load handover.md to prepare for this session" means

When Jonas says that (optionally adding "do not start implementing anything until I say
so"), do exactly this:

1. Read this file in full.
2. Read `HANDOFF.md` (especially §2 scope decisions, §3 environment constraints, §4
   parameter choices and the two traps, §7 resumption pitfalls), then `README.md`.
3. Do **not** re-read papers or re-derive documented findings — `notes/01–05`,
   `docs/method_review.md`, `docs/crash_causation_plan.md`,
   `docs/crash_causation_results.md`, and `docs/handbook/` hold them.
4. Reply with a short statement of where the project stands and what the plausible next
   steps are, then **stop and wait**. No implementation, no file changes, no commits,
   until Jonas says what he wants.

House style for anything written for Jonas: the `jonas-academic-writing` skill (US
English, markdown as source of truth, Word generated for his comments, PDFs from
markdown, no period at the end of a heading, hedge opinions as opinions).

## 1 Where the project stands in one paragraph

The project's goal is unchanged: a method for driver **comfort-zone boundaries** using
active inference; that method is built, property-tested, and validated end to end on the
authors' OSF output (median onset error 0.0 s), waiting on human data
(`docs/data_requirements.pdf` is the document to hand to data owners). Since the last
handover, two large pieces were added. A **method review** of the published model against
its code and deposit (`docs/method_review.md`, written to be sendable to an author). A
complete **crash-causation study** (`docs/crash_causation_results.md` is the document of
record): the Bärgman et al. (2024) mechanisms plus Wu et al.'s abnormal-acceleration mode
as five switchable components around two response processes (CBM and an active-inference
tier-1 surrogate), run on all 5 000 QUADRIS seeds with digitized real input
distributions and compared with the Wu binning/ROPE framework. Headlines: the attentive
active-inference driver avoids 67% of the crash population; its conditions are *closer*
to the reference than the CBM control (severity θ 0.148 vs 0.209, ROPE 0.10, from a
factor-14 miss at the study's start); the tier-2 closed loop validated the timing
surrogate (median |diff| 0.55 s, zero-start convention arbitrated); and the **glance-gate
finding** — the model gates evidence, not inference, and brakes mid-glance once a
conflict is registered, diverging testably from the CBM. The 15-chapter handbook carries
these lessons as revision round 2 (dark blue) and awaits Jonas's Word review; a one-off
authors' edition and a combined single-document build exist.

## 2 What exists beyond what HANDOFF.md and the notes describe

| Area | State | Where |
|---|---|---|
| Crash-causation results | **document of record**, full population, figures, arbiter verdict, exposure quantification | `docs/crash_causation_results.md` (+ Word/PDF); plan and reading notes in `docs/crash_causation_plan.md` (its §11 is superseded history) |
| Causation code | five components (glances with three placements, decel cap, no-response, abnormal-acceleration), two response models behind one interface, restartable runners; 39 property tests in `tests/test_causation.py` (suite total 103) | `src/causation/`, `src/quadris/`, `src/equivalence/` (reusable Wu ROPE testing), `replication/causation/` |
| Digitized input data | SHRP2 glance distribution and max-deceleration histogram from B24's published figures; two-route calibration checks built into the script | `replication/causation/digitize_b24.py` → `replication/causation/data/` |
| Full-population outputs | summaries/configs/logs tracked; the 60–270 MB `cond_*_fullp*.csv` are **gitignored** — regenerate with the exact commands in `replication/causation/out/log_fullp*.txt` | `replication/causation/out/summary_fullp.md`, `summary_fullp_abn.md` |
| Tier-2 closed loop | adapter (lead replay, forcible gaze schedule via `I_factor`, checkpointing, seed restart); 44 seed runs incl. the both-stationary batch; arbiter analysis | `replication/causation/tier2_rear_end.py`, `tier2_compare.py`, `tier2/arbiter_comparison.csv` |
| Handbook | round-2 revisions folded in (marks: {{R1}} dark red, {{R2}} dark blue, colored by `build_handbook.py`); combined single Word/PDF for a colleague via `build_combined.py` | `docs/handbook/`; combined outputs in `word/` and `pdf/` |
| Authors' edition | one-off 13-chapter de-CZB'd handbook to share with the papers' authors; frozen by design (its README explains) | `docs/handbook_authors/` |
| Email draft | the pre-filter-set request to Jian Wu, ready for Jonas to edit and send | `docs/email_jian_draft.md` |
| Method review | review of the published method vs code and deposit; sendable | `docs/method_review.md` (+ Word/PDF); numbers regenerated by `replication/review_osf.py` |
| **Equivalence/ROPE calibration** (2026-08-26) | the ROPE sits at the reference's noise floor (a perfect model passes ~50% at N=5, never at N=20); Θ=0.05 derived from an aggregate-error bound; uniform ω=1 shown to be the *strictest* reading, not the neutral one; explicit threshold proposals; written to be sendable to Jian Wu | `docs/equivalence_rope_note.md` (+ Word/PDF); bin sweep by `replication/causation/bin_sensitivity.py` |
| **Severity-vs-timing dissociation** (2026-08-26) | why severity matches while t_nr and a_f,min do not: response timing changes crash *count*, not *severity*; θ misreads a lattice (t_nr, 25 distinct values) and an atom (a_f,min, 48% at zero) | `docs/severity_vs_timing.md` (+ Word/PDF); figures by `replication/causation/make_dissociation_figure.py`, numbers by `severity_vs_timing.py` |
| **New human data** (arrived 2026-08-25) | clip-rating + button-press study: 80 participants, 4 scenarios, 67 kinematic traces. The button press is a *timed CZB crossing*, not a proxy, and the ego never responds | `external/01_studies/`; proposal in `docs/czb_study1_data_plan.md` (+ Word/PDF) |

## 3 Decisions and conventions from this arc (beyond HANDOFF and the style skill)

- **"The handbook" means the internal one** (`docs/handbook/`); the authors' edition is
  frozen. Revision rounds are color-marked; next round would be {{R3}}.
- **Pre-response counterfactual**: original follower profile with braking removed from
  the lead's onset (`pre_response_speed="no_brake"`); clamp-from-start differs by only a
  few percent.
- **Glance placement**: renewal process for active-inference conditions (theoretically
  required for an accumulating response), anchored overshot for the CBM (where it is
  Markkula's shortcut and performs better).
- **Accumulator start**: zero, **arbitrated** by the tier-2 closed loop (20/24 seeds;
  scope: windows opening near the conflict). The stationary variant stays in the outputs
  as tested-and-rejected. Do **not** fold the +0.42 s surrogate offset into a
  calibration — the untuned-surrogate argument is in the results doc §5.
- **Desired speed for external seeds**: the speed the original follower later reached.
  The both-stationary queue seeds are attentive-unreachable regardless (a finding —
  results doc §9); they crash only through the abnormal/no-response components.
- **Severity metric**: relative speed at impact is the assumption-free primitive
  (deposit delta-v assumed equal masses); report it alongside P_inj.
- **Never claim exposure-level results from crash-conditioned seeds**: ESS 44.7 of
  5 000, 295 unreachable — the B-versus-C contrast is robust to the critique, absolute
  rates are not (results doc §7).
- Verify by two independent routes; long jobs restartable; generated artifacts never
  hand-edited; token rules per the `github-token-handoff` skill — all unchanged.

## 4 Machine and environment notes (2026-08-25)

- Unchanged from HANDOFF §3 and the old handover: OneDrive locks (write `-vN` names),
  Python 3.14 with torch-cpu, pandoc, no gh CLI/LaTeX/GPU, PowerPoint COM never
  `.Quit()`, Git Bash `/tmp` ≠ Windows temp, big files via the Write tool.
- **Tier-2 cost is wildly variable**: 3 minutes to 4 hours per seed (batch 4), median
  ~10 minutes uncontended, with no clean predictor. Measure before extrapolating;
  everything is checkpointed and seed-restartable.
- Tier-1 full-population runs: minutes to ~1 h per condition; the 1000-draw bootstrap
  assessment can dominate. Run conditions as parallel background processes.
- Stopping a background shell pipeline can orphan its Python child briefly (it dies
  after its next checkpoint write); and never pipe a background runner through `tail` —
  it buffers everything and blinds progress monitoring.
- GitHub: files > 100 MB cannot be pushed; the fullp CSVs are gitignored for this
  reason. Push works via the repo-local credential helper (token rules in the skill).

## 5 Open items, in the order I would take them

1. **Jonas reviews the handbook** (Word in `docs/handbook/word/`, rounds R1+R2 colored;
   the combined document is for his colleague). Then: comments into markdown, {{R3}},
   rebuild.
2. **Send the Jian email** (`docs/email_jian_draft.md`) — the pre-filter set is the
   study's most valuable single ask; the method review and results doc are sendable
   companions to the respective authors.
3. **The CZB transfer test on the new data** — data arrived 2026-08-25 in
   `external/01_studies/`, so this is no longer blocked on acquisition. The proposal, and
   an argument with Jonas's initial sketch, is `docs/czb_study1_data_plan.md`: build the
   cut-in *preference function* (cheap) rather than the full closed-loop cut-in scenario
   (expensive) first, fit the boundary to right-censored button-press times rather than to
   braking (there is no braking in this data — the press *is* the boundary crossing), then
   fit on cut-in and predict LTAP/cyclist/truck overtake. Awaiting Jonas's scope decision.
4. **The a_f,min lever**: every configuration fails the braking-distribution metric — but
   `docs/severity_vs_timing.md` now shows roughly a third of the reported θ is a
   quantile-binning artifact at the 48% zero atom, and the real difference is a
   redistribution *within* braking crashes (too many moderate, too few hard) traceable to
   the discrete deceleration draw (375 distinct values against the reference's 1 853) plus
   the shared jerk-ramp execution model. The unpulled lever is still the execution model.
5. **Unexercised half of the gaze system**: the model *choosing* glances by epistemic
   pricing (handbook ch08 Proposal 1's second half); the forced-schedule route is done.
6. Smaller, unchanged from before: OSF oncoming + intersection analyses (the held-out
   scenario), deck unification and the teaching deck (post handbook review), 13 papers
   needing the Chalmers proxy, process-draw increase if tighter HDIs are ever needed.

## 6 If something here contradicts the repository

Trust the repository and the tracked notes over this file, and say so out loud — this
file was written 2026-08-25 and does not update itself.
