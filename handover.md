# handover.md — restart a session here

Written 2026-08-23. This is the **session entry point**; it captures everything from the
2026-08-19 → 2026-08-23 work arc that a fresh chat needs. The older `HANDOFF.md` remains
valid and is the deep research context (scope decisions, parameter traps, environment
constraints) — this file does not repeat it.

## 0 What "load handover.md to prepare for this session" means

When Jonas says that (optionally adding "do not start implementing anything until I say
so"), do exactly this:

1. Read this file in full.
2. Read `HANDOFF.md` (especially §2 scope decisions, §3 environment constraints, §4
   parameter choices and the two traps, §7 resumption pitfalls), then `README.md`.
3. Do **not** re-read papers or re-derive documented findings — `notes/01–05`,
   `docs/handbook/`, and `replication/osf/report.md` hold them.
4. Reply with a short statement of where the project stands and what the plausible next
   steps are, then **stop and wait**. No implementation, no file changes, no commits,
   until Jonas says what he wants.

House style for anything written for Jonas: the `jonas-academic-writing` skill (US
English, markdown as source of truth, Word generated for his comments, PDFs from
markdown, no period at the end of a heading, hedge opinions as opinions).

## 1 Where the project stands in one paragraph

The comfort-zone method is built, property-tested, and has passed its first end-to-end
test: run on the authors' own OSF simulation output (896 rear-end trials), it recovers
the reference model's brake onsets from kinematics alone with median 0.0 s error
(`notes/05_validation.md` §4b). The 15-chapter understanding handbook
(`docs/handbook/`) is drafted and awaiting Jonas's Word comments. A 31-slide seminar
deck exists. A three-page interactive tool suite (boundary explorer, norm sandbox, OSF
model browser) is built, tested, and dockerized. The repository is on GitHub with
working push and issue rights. The decisive next scientific step is unchanged: human
data and the cross-scenario transfer test (`docs/data_requirements.pdf` is the document
to hand to data owners).

## 2 What exists beyond what HANDOFF.md describes

| Area | State | Where |
|---|---|---|
| OSF deposit | downloaded (3.1 GB, untracked), validated against; policy-array axis order in its README is wrong — (H, timesteps, seeds, 2) | `external/gs4bu-osfstorage-archive/`, erratum in `notes/05` §4b |
| Distribution-level validation | done: RT distributions (their median 1.20 s, sd 0.66 s), Track B defect quantified, CZB pipeline dry run (score 0.855, median onset error 0.0 s; level c weakly identified — steep field) | `replication/validate_osf.py`, `replication/osf/`, `notes/05` §4b |
| Seminar deck | 31 slides incl. OSF results, speaker notes with time budgets and audience flags | `presentation/build_deck.py` → **`czb_talk_v2.pptx` is current**; `czb_talk.pptx` is a stale earlier build kept only because PowerPoint locked it — delete it and rebuild to one name when convenient |
| Understanding handbook | 15 chapters drafted (ch 00–14; ch 10 = calibration/fitting added last), figures scripted, Word + PDF generated; **awaiting Jonas's review** | `docs/handbook/`; tracker: `notes/TODO_understanding_pack.md` |
| Interactive tools | all three tiers: boundary explorer (JS verified vs Python, 700 cases), norm-tournament sandbox (property-tested), OSF model browser (224 runs incl. all 7 ablations, precomputed 130 KB data file); Docker image smoke-tested | `tools/czb_explorer/` |
| Git / GitHub | repo initialized, 3 commits pushed; `.gitignore` excludes external/ (3.1 GB + authors' clone), papers/ PDFs, paper_text/, generated Word/PDF/pptx; restore instructions in `external/README.md` | remote: `https://github.com/jbargman/active-inference-czb.git` (private) |
| Credentials | fine-grained token (Contents RW, Issues RW) in `C:\temp\.github_token`, ACL-restricted; repo-local git credential helper reads it at use time; push + issue create/close verified (test issue #1, closed) | the **`github-token-handoff` skill** has the full convention — load it for anything token-related |

## 3 Working agreements from this arc (beyond the style skill)

- **Provenance tags** in all handbook/analysis writing: [Paper] [SI] [Code] [OSF]
  [Speculation] — speculation always explicitly ours.
- **Verify by two independent routes** where possible (closed form vs numeric field; JS
  vs Python reference; render-and-look for every slide and PDF page). This habit has
  caught real errors twice (sign error; test-margin bug).
- **Never quote absolute boundary values without the assumptions** (assumed worst-case
  lead braking, reaction-time budget) — HANDOFF §7 rule, embedded in the tool's footer.
- **Long jobs die in this environment**: everything batch is written restartable
  (append + fsync + skip-done). Keep it that way (HANDOFF §3).
- **Generated artifacts are never hand-edited**: markdown/scripts are the source;
  Jonas's reviewed Word copies stay untouched, comments go back into the markdown, and
  revision rounds are color-marked per the writing skill.
- The token file and its usage rules: see the `github-token-handoff` skill. Never print
  the token; no `git credential fill`; no `curl -v`.

## 4 Machine and environment notes (2026-08-23)

- Repo path: `C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference`
  (OneDrive — beware file locks from open Office apps; write `-vN` names when locked).
- Available: Python 3.14 (numpy/pandas/matplotlib/reportlab/PyMuPDF/openpyxl/torch-cpu),
  pandoc, node v24, Chrome (headless screenshots for page verification), Docker,
  PowerPoint via COM. Absent: `gh` CLI, LaTeX, GPU.
- PowerPoint COM attaches to the running instance — **never call `.Quit()`** if Jonas
  may have PowerPoint open (it would close his session); render via
  `SaveCopyAs(dir, 18)` and `Close()` only.
- Git Bash `/tmp` is not Windows Python's temp — pass explicit Windows paths between
  tools. Very large heredocs fail (spawn limit) — use the Write tool for big files.
- The Chalmers deck template's Titelsida/Kapitel layouts render empty via python-pptx —
  `build_deck.py` draws title and section slides manually; keep doing that.

## 5 Open items, in the order I would take them

1. **Jonas reviews the handbook** (Word files in `docs/handbook/word/`). Then: work
   comments into the markdown, color-mark the round, rebuild Word + PDF.
2. **Human data acquisition** — the actual research step (HANDOFF §6 item 1;
   `docs/data_requirements.pdf` is ready to send).
3. **Deck unification** — delete stale `presentation/czb_talk.pptx`, rebuild to one
   filename once no PowerPoint lock; consider folding handbook figures in.
4. **Teaching deck** (deferred by agreement until handbook review).
5. **Post-review handbook figures** — scenario-geometry panels (ch 04), validation
   ladder (ch 09).
6. **OSF oncoming + intersection analyses** — the deposit folders are untouched beyond
   rate tables; the intersection is the held-out scenario and scientifically the most
   interesting (HANDOFF §6 item 2 note).
7. **Track B timing fix** (jerk penalty on CEM policies) — still optional; the CZB path
   does not depend on it (HANDOFF §6 item 3).
8. Remaining smaller: 13 papers need the Chalmers library proxy (HANDOFF §6 item 5);
   free-following recalibration is a GPU-scale job (item 4).

## 6 If something here contradicts the repository

Trust the repository and the tracked notes over this file, and say so out loud —
this file was written 2026-08-23 and does not update itself.
