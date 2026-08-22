# Chapter 12: the code map — from concept to file, class, and parameter

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Paths under
`external/aica/` are the authors' released code [Code] — the reference implementation and
ground truth. Paths under `src/` are this project's code. Parameter names are the columns
of the OSF `Setups_*.xlsx` tables, which double as the complete configuration record of
every published run [OSF].*

## The two implementations, and which to use when

| | The reference (`external/aica/`) | Our mirror (`src/aidriver/`) |
|---|---|---|
| Language | PyTorch, written for GPU | NumPy, written to be read |
| Status | ground truth; ran the published results | preferences verified against the SI; closed-loop timing not yet trusted |
| Use for | any result you intend to compare or publish | understanding mechanisms; static/preference work |
| Cost | ~18 s CPU per simulated timestep here | interactive |
| Local changes | exactly one patch, logged in `replication/PATCHES.md` — keep it that way | ours to change |

The comfort-zone machinery (`src/comfortzone/`) is a third thing: not a model
implementation at all, but the static method of chapter 11, depending only on the
preference function and recorded kinematics.

## The reference implementation, oriented in one table

Top level: one `simulation_<scenario>.py` runner and one `Analysis_<scenario>.py` per
scenario (plus `_SA` sensitivity variants); the runners assemble a configuration
dictionary, call the shared machinery, and write the pickle/xlsx outputs mirrored in the
OSF deposit.

| Concept (chapter) | File in `src/common/` | What to look for |
|---|---|---|
| World physics | `bicycle.py`, `environment.py` | bicycle model both vehicles share |
| Looming senses (03) | `decoder.py`, `encoder.py` | observation construction; the looming transform; the off-gaze noise factor `I_factor` |
| Belief cloud (06) | `particle_filter.py`, `kde.py`, `distributions.py` | weighting, resampling; the KDE/mixture belief representation |
| Imagined futures + norm trust (06) | `dynamics.py` | `forward_tar_agent`, `normative_probability`; the `N_norm`/`H_norm` sampling and the trust cap |
| Scoring, pragmatic + epistemic (03) | `belief_reward.py` | expected-free-energy assembly over particles |
| The planner and the surprise gate (03, 05) | `mpc_discrete.py` | CEM loop; evidence accumulation; the hard-coded "avoid off gaze" line (08) |
| Gaze dynamics (08) | `dynamics.py` (gaze block) | two-state gaze, switching probability `p` |
| Run orchestration | `src/utils/simulation.py`, `saving.py` | how a config becomes a run becomes a pickle |

Per scenario (chapter 04): `src/<scenario>/dynamics_true.py` (the world and the other
vehicle's script), `decoder_true.py` (true-state → observations), `reward.py` (the
preference terms with the scenario's lane geometry, and `get_weights` — the norm
geometry of chapters 06–07). The rear-end scenario used for the published grid lives in
`src/rear_end_test/`.

## The parameters that matter most, by name

All 65 configuration columns are in every `Setups_*.xlsx`; these are the ones the
handbook's chapters keep returning to:

| Column | Plain meaning | Chapter |
|---|---|---|
| `v_ego_sd_des`, `a_ego_sd_des`, `w_ego_sd_des` | tolerances of the speed / pedal / steering preferences | 07 |
| `lane_change_cost`, `road_leave_cost`, `collision_cost` | the hard costs | 07 |
| `a_sd_model`, `w_sd_model` | assumed other-agent variability (the scenario-type dial) | 04, 06 |
| `N_norm`, `H_norm`, `weigh_particles`, `full_violation_factor` | norm-conditioning strength and geometry factors | 06 |
| `alpha` | weight of epistemic value | 03 |
| `EA_mode`, `EA_fac`, `EA_init` | evidence accumulation on/off, rate λ, starting level | 02, 05 |
| `use_looming_perception`, `looming_threshold` | the visual channel and its detection floor | 03, 08 |
| `x_sd_perc` … `w_sd_perc` | perception noise scales | 03, 08 |
| `num_plans`, `H` | planning budget and horizon | 03 |
| `road_gaze_preference`, `x_ego`…`v_tar`, `T` | gaze preference (0 in all published runs); stage-setting | 08, 04 |
| ablation columns | the seven Figure-6 switches | 09 |

## This project's code

| Package | What it is | Trust level |
|---|---|---|
| `src/aidriver/` | readable NumPy mirror of the agent: `preferences.py` (the six terms, SI-verified), `agent.py` (belief + CEM loop), `scenarios.py`, `params.py` | preferences verified; closed-loop timing not trusted (`notes/05_validation.md`) — see also the two parameter traps in `HANDOFF.md` §4 |
| `src/surprise/` | the surprise-measure library (three families + the two Waymo measures), one interface across belief types | property-tested, 31 tests |
| `src/comfortzone/` | the CZB method: `field.py` (field, closed-form boundary), `boundary.py` (level sets), `calibrate.py` (field along recorded kinematics; level fitting) | cross-checked closed form; end-to-end dry run on the OSF data |
| `replication/` | Track A runner + sweep + `validate_osf.py` (the OSF comparison harness of chapter 09, rung 3) | outputs in `replication/osf/` |
| `tests/` | 57 property tests — the rung-0 suite | all passing |

## The data that goes with the code

The OSF deposit (`external/gs4bu-osfstorage-archive/`) is the third leg: per-run
configuration tables (`Setups_*.xlsx`), outcome summaries (`Analysis_*.xlsx`), and
per-timestep pickles (true states `eta`, observations `o`, beliefs `b` with weights `w`,
planned and reference policies `a_cont` / `a_cont_init`, pragmatic-value components `v`)
for every published run of all three scenarios, ablations included. One recorded erratum:
the deposit README's stated axis order for the policy arrays is wrong — they are (horizon,
timesteps, seeds, 2), not (horizon, seeds, timesteps, 2); `eta`'s shape disambiguates
(`notes/05_validation.md` §4b) [OSF].

Practical rules when working here: mine the deposit before simulating (chapter 09);
never edit `external/` beyond the logged patch; keep every new result paired with its
full parameter record the way the `Setups` tables do; and remember the environment kills
long jobs — the restartable runners and their checkpoint files exist for that reason
(`HANDOFF.md` §3).

## Five first exercises

For a new person's first afternoon — each is under an hour, needs no GPU, and touches a
different limb of the system. In rough order:

1. **Meet the model's output.** Load one OSF pickle (`Results_rear_end/Exp_7/Exp_7.pkl`),
   plot speed, gap, and executed acceleration for a few seeds. You are reproducing
   chapter 02's figure; the axis-order erratum above is the only trap.
2. **Run the cheap demos.** `python demo_comfort_zone.py` and `python demo_surprise.py`
   — the static machinery end to end, minutes, no closed loop.
3. **Move a boundary.** In a notebook, call `comfortzone.critical_thw` across speeds;
   then change the assumed worst-case braking and the reaction-time budget and watch
   chapter 07's tables reappear. This is rung 1 of the validation ladder in miniature.
4. **Score a trajectory.** Take the `eta` kinematics from exercise 1, run
   `calibrate.deficit_along_trajectory`, and find the first exceedance against the
   fitted level from `replication/osf/calibration.json`. You have just reproduced the
   core of the comfort-zone pipeline (chapter 11).
5. **Watch the trust cap work.** Run `docs/handbook/make_diagrams.py` and modify the
   `norm_tournament` starting position and geometry factors — the fastest way to build
   intuition for chapter 06, and safe, because it is an illustrative reimplementation.

A sixth, when a spare two hours of CPU exists: run
`replication/run_rear_end_single.py` for one short condition with
`--checkpoint-every`, to experience the reference loop's cost and the restart machinery
firsthand.
