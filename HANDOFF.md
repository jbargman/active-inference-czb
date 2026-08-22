# Handoff — context that is not in the other documents

Paste or reference this file after clearing a chat. Everything that *is* written down lives in
`notes/` and `docs/`; this file holds only what would otherwise be lost — scope decisions,
environment constraints, choices that were made rather than inherited, and what deliberately
was not done.

**Read this, then `README.md`. Do not re-derive the rest — it is already written.**

---

## 0 Statement to paste into a new chat

Copy the block below verbatim into a fresh session. It is the only thing that needs to be
typed; everything else follows from the files.

```text
I'm resuming the WaymoActiveInference project in this directory.

Before anything else, read HANDOFF.md in the repository root, then README.md.
HANDOFF.md holds the scope decisions, environment constraints and non-obvious
parameter choices that are recorded nowhere else. README.md maps the repository
and states what works and how well.

Everything already investigated is written up in notes/01 through notes/05 and
docs/data_requirements.pdf. Do not re-read the papers and do not re-derive
findings that are already documented — read those files instead.
notes/paper_text/ has the extracted plain text of all papers if you need to
search them.

The objective is a method for establishing driver comfort-zone boundaries using
active inference. Replicating the Schumann et al. (2026) collision-avoidance
model is instrumental, not the goal. Only papers/active-inference/ is in scope;
the other paper categories are downloaded but deliberately out of scope.

Anything you write for me follows the jonas-academic-writing conventions: US
English, markdown as the source of truth with PDFs generated from it.

When you have read those two files, give me a short statement of where the
project stands and what you think the next step should be, then stop and wait.
Do not start work until I tell you what I want.
```

If a session has been running long enough that context is thinning, the same block works as a
mid-session reset.

---

## 1 Where things stand in one paragraph

The goal is a method for establishing **driver comfort-zone boundaries** using active
inference. The Schumann et al. (2026) collision-avoidance model is the starting point, not the
objective. The comfort-zone method is built and tested but has never touched human data; the
model has been replicated in two ways with partial success; a library of surprise measures is
complete and verified. The next real step is empirical, not computational: get data (see
`docs/data_requirements.pdf`) and run the cross-scenario generalization test.

## 2 Scope decisions that came from Jonas, not from the work

- **Only `papers/active-inference/` is in scope.** The other six categories in `papers/` were
  downloaded on request but are explicitly out of scope until he says otherwise. Do not start
  reading them.
- **Comfort-zone boundaries are the objective.** Replicating the collision-avoidance model is
  instrumental. When a trade-off appears, protect the comfort-zone path.
- He is a co-author of Engström et al. (2018) *Great expectations*, the predictive-processing
  predecessor of this line, and comfort-zone/dread-zone quantification is established Chalmers
  work. The active-inference angle is a way to replace per-scenario kinematic indicators with
  one scalar field.
- **House style applies to everything written for him**: US English, no period at the end of a
  heading, never start a sentence with "And", avoid "load-bearing". The `jonas-academic-writing`
  skill has the full set. Markdown is the source of truth; PDFs are generated from it
  (`docs/build_pdf.py`).

## 3 Environment and hard constraints

| | |
|---|---|
| Python | 3.14.0 |
| torch | 2.13.0+**cpu** — `cuda.is_available()` is False |
| other | numpy 2.4.3, pandas 3.0.5, reportlab 5.0.0, PyMuPDF 1.27.2, pandoc on PATH |
| no | LaTeX, wkhtmltopdf, weasyprint, GPU |

**Compute is the binding constraint on replication.** The authors' model costs roughly **18 s
of CPU per simulated timestep per parallel run**. A 10-second scenario is a two-hour job.

**Long background jobs get terminated in this environment.** Three Track A attempts died at
29/50, 2/32 and 2/18 steps; it is not a timeout (one died after two minutes) and not memory.
The mitigations are already in the code and should not be removed:
`run_rear_end_single.py --checkpoint-every` writes a `.partial` pickle as it goes, and
`sweep_rear_end_aidriver.py` appends and fsyncs each row and skips conditions already present,
so it can be restarted with the same command. `validate.py` reads `.partial` files.

## 4 Choices that were made, not inherited from the paper

These are not in the notes because they are implementation decisions rather than findings, but
they change results and are easy to trip over.

| choice | value | why |
|---|---|---|
| `alpha` (epistemic value) | **0.0 in the sweep**, though `AgentParams` defaults to 1.0 | The paper says behavior in collision avoidance is driven mainly by pragmatic value. With looming perception the observation precision improves as distance closes, so epistemic value creates a perverse incentive to approach. Turned off for the validated runs. |
| `t_brake` in the sweep | 2.0 s, though the SI says 5 s | Response times are measured relative to the lead vehicle's braking onset, so the value only changes run length. Shortening it made the 140-run sweep feasible. |
| `warm_start_replan` | False | Warm-starting CEM from the shifted previous policy was tried; it did not reduce the response-time dispersion and slightly worsened collisions. Kept the paper's behavior. |
| `a_other_min` (preference) | −6.0 in the sweep | The paper calibrates this per scenario via a separate free-following study. −6 is the value at which the safety term is exactly zero during steady following at THW 1.5 s, which is the property the calibration exists to produce. |
| `sigma_a_init` | 0.5 m/s² | Not in the paper. Needed because the process noise (3 m/s²) as an *initial* belief leaves acceleration essentially unknown from one snapshot, making 15% of predicted futures collisions during ordinary following. |
| collision severity floor | 0.2 | This one *is* from the SI (Eq. 48); noted here only because it looks like a fudge and is not. |

### Two traps

1. **`AgentParams` defaults do not match the validated configuration.** `alpha` defaults to 1.0
   but the sweep used 0.0; `a_other_min_assumed` defaults to −4.0 while the sweep's preference
   used `a_other_min = −6.0`. Construct the agent the way `sweep_rear_end_aidriver.py` does, or
   results will not match `notes/05_validation.md`.
2. **`a_other_min_assumed` (in `AgentParams`) and `a_other_min` (in `PreferenceParams`) are
   different parameters.** The first clamps sampled decelerations during prediction; the second
   is the counterfactual `a_OV,min` in the safety term. They happen to describe the same
   physical assumption and should normally be set together.

## 5 What was deliberately not done

- **Lateral incursion and intersection scenarios.** Our `LateralIncursionScenario` is not
  faithful to the paper's setup (300 m initial separation, v0 = 17.88 m/s, turn triggered at
  TTC 5.15 s, three incursion levels). Running it against the paper's 82.3% collision rate
  would measure the difference between scenario definitions, not the model. Reasoning is in
  `notes/05_validation.md §5`. The intersection scenario is the paper's *held-out*
  generalization test and is the most interesting one to reproduce.
- **The paper's fit metrics** (Jensen-Shannon, Wasserstein, bootstrapped MAE). They compare
  model output against human datasets we do not have.
- **Ablations** (no evidence accumulation, no looming, no norms, no pedal constraints). Cheap
  once timing is right, and the strongest available check that the mechanisms do what they do in
  the original.
- **Any human data.** Every number in this repository is a property of a model.

## 6 Open items, in the order I would take them

1. **Get data and run the generalization test.** `docs/data_requirements.pdf` is written to be
   handed to a data owner. The plan: fit the boundary level *c* on the Chalmers LTAP/OD
   comfort-zone data, then apply that same *c* unchanged to the pedestrian-overtaking data. The
   second step is the actual experiment. Everything else here is preparation.
2. ~~Download the OSF deposit~~ **Done 2026-08-20.** The deposit is at
   `external/gs4bu-osfstorage-archive/` (3.1 GB, all three scenarios, 32 seeds per run).
   `replication/validate_osf.py` ran the rear-end comparison — results in `replication/osf/`
   and `notes/05_validation.md §4b`. Headlines: the authors' true RT distribution is median
   1.20 s / sd 0.66 s (Track A's two points sit inside their IQR; Track B's defect is now
   quantified); our comfort-zone calibration pipeline recovers their model's brake onsets
   from kinematics alone with median 0.0 s error (score 0.855, n = 896). Beware: the deposit
   README's axis order for the policy arrays is wrong — they are (H, timesteps, seeds, 2).
   Still untouched: the oncoming and intersection folders, and the ablation grids.
3. **Fix Track B's response-time dispersion.** Median 0.20 s, sd 1.23 s. Diagnosed in
   `notes/03_replication.md`: the closed-loop surprise signal is inflated by the control-effort
   term applied to un-smooth CEM policies. A jerk penalty between consecutive planned actions is
   the obvious thing to try; more CEM budget already did not help.
4. **Regenerate the free-following calibration** for Track A over the paper's actual parameter
   range, which should close the Fig. 3a discrepancy. This is a multi-day GPU job.
5. **13 of the 54 Waymo papers are still missing** — Taylor & Francis, Elsevier, SAE and
   Springer with no open-access mirror. Listed at the bottom of `papers/README.md`; they need
   the Chalmers library proxy. One of them is an active-inference paper: the Springer chapter
   *World model learning from demonstrations with active inference*.

## 7 Things that are easy to get wrong when resuming

- **The comfort-zone method does not depend on the closed-loop agent.** It needs only the
  preference function and recorded kinematics. Track B's response-timing defect does *not*
  invalidate it. Keep that separation — it is why the method is usable now.
- **`src/aidriver/` is not the reference implementation.** The authors' code in `external/aica/`
  is. Track B exists to make mechanisms inspectable and to supply the preference function; where
  they disagree, the authors' code wins.
- **The Supplementary Information matters more than the article** for anything to do with the
  preference function. SI §2.4, Eqs. 44–52. Two things are impossible to guess from the article
  alone: `p_lat` is triangular and lane-structured, and `p_coll` contains an inverse-tau
  preference that shapes ordinary car following.
- **`external/aica/` has exactly one local patch** (a hardcoded `device='cuda'`). Documented in
  `replication/PATCHES.md`. Do not let other edits accumulate there silently.
- **Do not quote absolute comfort-zone boundary values without stating `a_OV,min` and
  `t_react`.** They move the boundary substantially and are assumptions, not measurements.

## 8 Where everything else is written down

| | |
|---|---|
| `README.md` | map of the repository and what works how well |
| `notes/01_paper_summaries.md` | the seven papers, individually |
| `notes/02_active_inference_overview.md` | the method, the literature, the bridge to comfort zones |
| `notes/03_replication.md` | replication report, bug list, practical run notes |
| `notes/04_comfort_zone_method.md` | **the proposed method** and the study that would validate it |
| `notes/05_validation.md` | our results against the published values, model and surprise measures |
| `docs/data_requirements.pdf` | what data is needed, in what format, from which datasets |
| `papers/README.md` | all 54 Waymo papers, categorized, with what is missing |
| `notes/paper_text/` | extracted plain text of every paper, for searching |
