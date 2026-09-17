# A generative-model framework: prepared on the drone datasets, run on Volvo Cars' data without moving it

*2026-09-17, at Jonas's request (JJ.Q3, the same evening): the data that a data-driven generative model
of other road users needs is the project's largest issue, so build a framework that is prepared on
highD and inD and then run, unchanged, on Volvo Cars' naturalistic data through the split-site
protocol, returning only aggregates. This document is the design; the code skeleton is `src/generative/`
with 28 property checks in `tests/test_generative.py`, exercised end to end on the synthetic interface
fixture (`replication/czb/gm0_generative_smoke.py` → `out/gm0/`). Nothing has touched real data.
Companion: `docs/rollout_boundary_design_note.md` (card JJ.1), which consumes what this framework
produces. Opinions are marked. The VCC track is paused (2026-09-11); nothing here is sent anywhere.*

## 0 The short version

**The worry.** A learned predictor of other road users, of the kind large industrial groups train,
needs data on a scale we will never have: the drone datasets are hours, not years; Volvo Cars' data is
larger but cannot leave the company.

**The answer.** We do not need that kind of predictor. The generative model the rollout formulation
needs is **structured**: bicycle kinematics for the motion, a latent intention (keeping or changing
lane), norm-shaped noise, and uncertainty that grows with the horizon. What data must supply is a
handful of distributions, and each is estimable from data on the scale we have:

| component | what it is | what fixes it | highD alone gives |
|---|---|---|---|
| **C1** lane-change initiation | P(a vehicle in the adjacent lane starts a lane change within the next Δt, given its context) | a discrete-time hazard model on a few context features | more than 11 000 lane changes, 5 600 complete, from 110 000 vehicles (Krajewski et al., 2018): thousands of events against a large exposure population |
| **C2** lane-change execution | onset, duration, lateral speed, straddling time | quantiles over completed lane changes | 5 600 complete lane changes |
| **C3** uncertainty growth | how far a constant-velocity prediction drifts, per horizon and axis | two constants per axis, from pooled prediction errors | every track, 16.5 hours |
| **C4** the ego's normal | following headway by speed, accepted clearances, accepted gaps | binned quantiles; a Gaussian reference for the ellipse | every following pair; inD for gaps |
| C5 (optional) a learned conditional density | P(future | past, context) as a mixture | a small network | tens of thousands of tracks suffice for a small model; public motion datasets exist for a larger one (§2) |

C1 to C4 are what the rollout predictor P0 and the crossing norm consume; C5 is the ambitious end of
the ladder and the only component whose appetite for data is real.

**What Volvo Cars adds, once the track resumes.** Not more of the same. Three things the drone data
cannot give: Swedish roads and drivers; the **ego's view** of the other vehicle through the vehicle's own
sensors, which is where perceptual uncertainty lives; and **driver identity across trips**, which is
what the per-driver level and the trait need. The same framework fitted at VCC yields Swedish norms,
and the comparison with the highD norms is a finding in itself: do norms transfer between road
cultures?

**How it runs there.** The code reads the split-site interface (`transfer/interface_schema.yaml`), which
VCC's adapter produces, and writes only aggregate tables that the transfer policy's export rule allows;
the rule is enforced in code (`src/generative/aggregate.py`), so the runner cannot write a table the
bundle tool would refuse. The interface needs one extension for C1 (§4), which goes to VCC together with
the five gaps card NDS.1 found, when Jonas restarts that track.

## 1 Why a structured generative model needs little data

A trajectory predictor trained end to end has to learn everything: that cars move smoothly, that they
stay in lanes, how fast a lane change goes, how often one starts. It learns these from examples, and
rare behavior needs many examples. An active-inference agent's generative model has most of this
**written in**: the kinematics are physics, the norms are geometry, and the uncertainty is a spread
around them. The released model of Schumann et al. (2026) has no trained component at all, and the
handbook's verdict on its hand-drawn norms was that *learning them from data* is the most valuable
extension available (handbook chapter 7). That is a learning problem with a few parameters, not a few
million.

Figure 1 of the program document put it as two normals: the ego's own (the preference prior) and the
one expected of others (the norm). The framework estimates the data-fitted parts of both. What it does
not do, deliberately, is replace the structure by a network. Wei et al. (2023) tried the other route,
learning an active-inference driver's world model and preferences from car-following demonstrations,
and reported that the result was sensitive to the chosen input features and failed in situations absent
from the data. For the comfort-zone question that is a caution: keep the structure, fit the constants.

**How much is enough, component by component** (working estimates, to be checked at the census NC.0c
of the naturalistic plan):

- C3 needs hundreds of tracks: each track yields one prediction error per sample and horizon, and the
  standard deviation of the pooled errors is well determined long before the drone data run out. Its
  trap is not scarcity but jitter: a velocity read from two jittered positions carries an error of
  √2 σ / window that then grows with the horizon, so the measured growth must be compared with the
  floor that the tracks' own jitter predicts (`uncertainty.py::jitter_growth_floor`; the property test
  shows the fixture's growth slope *is* that floor, 0.138 against 0.141 m/s).
- C2 needs hundreds of complete lane changes for stable quantiles of duration and peak lateral speed;
  highD's 5 600 are ample and allow splits by speed and by vehicle class.
- C1 is the demanding one, and still modest: a logistic hazard with five or six features is well
  determined by a few thousand events against their exposure. The property test recovers a scripted
  slope within its standard error from 6 000 exposure rows. What C1 needs that the others do not is
  the **exposure population**: the adjacent-lane vehicles that did *not* change lanes. Drone data have
  it by construction (every vehicle is tracked); event-based naturalistic data do not, which is the
  interface extension of §4.
- C4 needs what any following study needs; highD's pairs are more than enough by speed bin.
- C5, if pursued, needs tens of thousands of tracks for a small mixture-density model on highD, and
  for anything larger the public motion-forecasting datasets: the Waymo Open Motion Dataset (over
  100 000 scenes of 20 s, about 570 hours; Ettinger et al., 2021), Argoverse 2 (250 000 scenarios of
  11 s, CC BY-NC-SA), the INTERACTION dataset and exiD (about 69 000 vehicles at highway ramps, dense
  with merges). All are urban or US or both, and none is an ego view; they can teach a predictor
  *general* motion, after which highD and VCC supply the *local* norms. Whether to go this way is
  query GM.Q3.

## 2 The components, precisely

### C1 Lane-change initiation: the hazard (`hazard.py`)

One of the paper's authors said to Jonas (2026-09-17) that the most important part of a cut-in model is
likely the normative, generative model of *when a vehicle starts* a lane change. In the rollout
formulation this is the prior p₀ on the latent intention, made a function of the scene. The estimator
is the person-period form of survival analysis: every exposure episode (a vehicle that could change
lanes, whether or not it does) is cut into bins of Δt; each bin is a row with the features at its
start and a flag for whether the change began in it; a censored episode contributes all its bins with
flag 0; the fit is logistic regression with an intercept. Features, in the order of expected importance
and all observable from a drone or from the ego's sensors:

1. the vehicle's own headway and closing rate to the vehicle ahead of it in its lane (the reason to
   change lanes);
2. its speed relative to the ego (the target lane's speed);
3. the gap it would enter (our headway to it, and the ego's own lead if any);
4. its lateral offset and drift within its lane;
5. an indicator signal, where the data carry one (highD does not; a vehicle's sensors may).

Outputs that leave a data site: the coefficient table with standard errors, the calibration table by
predicted-probability decile with counts, the constant-hazard baseline, and the counts of events and
exposure rows. Never an episode.

### C2 Lane-change execution (`lanechange.py`)

For each lane change: the onset (the first moment from which the lateral offset from the starting lane's
center stays beyond a band), the crossing of the line, the completion, the duration, the peak lateral
speed, and the straddling time. The band is a parameter (first value 0.3 m, three times card HS.1's
0.1 m noticeable discrepancy, itself unverified) and every report states it. Outputs: quantiles of each
over completed lane changes, and the crossing norm's lateral-speed band as data quantiles, replacing
the proposal's 0.5 and 3.0 m/s (`docs/cutin_norm_proposal.md` §2 declared the lower bound the value it
was least sure of).

### C3 Uncertainty growth (`uncertainty.py`)

Constant-velocity prediction errors of the other road user's motion at horizons 0.5 to 6 s, with the
velocity read as a backward difference over 0.3 s, the video cards' window, so that "what a driver could
have extrapolated" uses only what was visible. Pooled by scenario and by phase (before the conflict
onset, and over the whole event), then the growth model sd(h)² = s₀² + (s₁ h)² per axis. These two
constants per axis are what the rollout predictor P0 takes in place of the placeholders in the design
note (σ_v,lat first value 0.33 m/s; σ_a 0.5 m/s², unverified). Reported beside them: the jitter floor
s₁ that pure position noise would produce, so that no report attributes measurement noise to drivers.

### C4 The ego's normal (`population.py`)

Following time headway by ego-speed bin before any conflict; passing clearances by speed for the
overtake scenarios; accepted and rejected gaps at intersections from inD. As binned quantiles with the
export rule's small-cell suppression built in, and as a Gaussian reference (mean, covariance) whose
squared Mahalanobis distance is twice the residual information under it, which is the CZB ellipse's
percentile in the surprise note's reading (`docs/surprise_without_the_field.md` §4).

### The export rule in code (`aggregate.py`)

The transfer policy's forbidden columns and person columns are mirrored in code, and a property test
checks that the two lists agree so they cannot drift apart. Every table is checked before writing: an
identifier column refuses the write; rows below the minimum count are dropped and counted; a table with
no count column is refused because the rule cannot be checked on it. The run record carries the script,
the commit, the date and the parameter values, never a path.

## 3 How it runs at the two sites

![The two-site flow](ai_program_figures/two_normals.png)

*The figure of the two normals from the program document; the framework estimates the data-fitted parts
of both, at either site.*

1. **Home site, now.** The runner reads the synthetic fixture (`transfer/fixtures/synthetic/`) and
   writes `replication/czb/out/gm0/`. This is the rehearsal: every table the data site would produce is
   produced here on made-up data, and the report names what the interface cannot yet support.
2. **Home site, on highD and inD access.** The naturalistic plan's step NC.0 writes highD cut-ins to
   the interface shape as a dry run (Jonas's ruling NAT.Q2). The runner then produces C2, C3 and C4 from
   real German traffic, and C1 from highD's own tracks through a highD-specific episode builder in the
   site layer (`src/comfortzone/highd.py`, planned in NC.0). The results are the first real parameters for
   the rollout predictor and the crossing norm, versioned in a parameter file with their provenance
   (dataset label, commit, date) so that a report can say which norms it used.
3. **Data site, when the track resumes.** The same `src/generative/` travels in a bundle
   (`transfer/bundle.py`, `src/**` is allowed); VCC's adapter writes the interface; the runner writes
   `results/aggregate/generative/`; the steward reviews; the aggregates return in a bundle. Nothing
   else moves. The comparison highD against VCC is then a table of two sets of constants with intervals.
4. **Back at the home site.** The rollout cards (JJ.2, JJ.3) are rerun with the VCC constants in place
   of the highD ones, and the sensitivity of ΔG's verdict to the source of its constants is the
   cross-culture result.

## 4 What the interface must carry that it does not

The interface is event-based: one conflict, one partner, two tracks. Two of the framework's components
need more, and the request goes to VCC as one schema revision together with NDS.Q2 to NDS.Q5:

| need | why | proposed change |
|---|---|---|
| **exposure episodes** | C1 cannot be fitted on cut-ins alone; it needs the adjacent-lane vehicles that did not cut in, sampled from ordinary driving, at a stated ratio to the events | a new scenario value `exposure_adjacent`: windows of a fixed length with a vehicle in the adjacent lane and no lane change, sampled at random from trips; `t_conflict_onset` NaN |
| **the partner's own context** | C1's first feature is the partner's headway to *its* lead, and the third the gap it would enter | optional columns `oth_lead_gap` and `oth_lead_dv` (NaN when no lead is tracked), and `oth_indicator` (0/1/NaN) where the sensor set reports it |
| **the lane-change onset criterion** | C2's onset must mean the same at both sites | the band value written into the run record, and `t_conflict_onset` for cut-ins defined as the band crossing, not the line crossing |
| **a lateral frame that is shared by ego and partner** | C2 and the gate need the difference of the two lateral positions | already NDS.Q3; restated because C2 depends on it |

Until the extension exists, the runner reports C1 as "not estimable from this interface" rather than
fitting it on events alone, which would confound initiation with occurrence.

## 5 The cards

| card | what | needs | when |
|---|---|---|---|
| **GM.0** the rehearsal | the runner on the synthetic fixture; the property tests | nothing | done in this arc (`out/gm0/`) |
| GM.1 highD constants | C2, C3, C4 on highD written to the interface shape; C1 through a highD episode builder; the parameter file with provenance | NC.0 (loaders, conventions, jitter floor); access | on access |
| GM.2 inD gaps | C4's accepted and rejected gaps at intersections by conflicting class and speed | NC.0; access | on access |
| GM.3 held-out check | C1's calibration on held-out highD recordings; C3's growth on recordings not used to fit it | GM.1 | after GM.1 |
| GM.4 the interface dry run | highD cut-ins through the interface end to end, the runner producing exactly the data site's tables | GM.1; NAT.Q2 (ruled: allowed) | after GM.1 |
| GM.5 VCC | the bundle, the run, the aggregates back, the comparison | the track resumed; the schema revision signed | when Jonas restarts the track |

GM.1 feeds the rollout design note's placeholders; until it runs, JJ.2 uses the first values with their
sweeps, and says so.

## 6 What could go wrong

- **Exposure sampling** decides C1. If the exposure windows are sampled where lane changes are likely
  (dense traffic) or unlikely (free flow), the hazard is biased; the sampling rule must be written into
  the schema revision and be the same at both sites.
- **Lateral quality at the data site** (NDS.Q3) can make C2 and the lateral half of C3 unusable; the
  runner's jitter floor comparison will show it as a growth slope that equals the floor.
- **Identifiability of C1 with few events** at a data site: the coefficient table's standard errors say
  so, and the calibration table is the honest summary.
- **Domain shift** between German highways, Swedish roads and simulator stimuli is the thing the
  framework is built to *measure*, not to remove; a report that finds different norms has found
  something.
- **Model weights as derived data.** C5 is the only component that is a model rather than a table, and
  whether such a model may leave a data site is a question for the steward at sign-off (JJ.Q3 for the
  highD license).

## 7 Queries

@GM.Q1(judgment, jonas): Extend the split-site data request with exposure episodes and the partner's
own context (section 4), to go to VCC as one schema revision together with NDS.Q2 to NDS.Q5 when the
track resumes? Without it C1 cannot be fitted at VCC.

@GM.Q2(judgment, jonas): Apply for exiD as well (same provider as highD and inD; highway ramps, dense
with merges and lane changes)? It would multiply C1's and C2's events and add a merging geometry.

@GM.Q3(judgment, jonas): Pursue C5, a learned conditional density, on the public motion-forecasting
datasets (Waymo Open Motion Dataset, Argoverse 2, INTERACTION) for general motion, with highD and VCC
supplying local norms? Or stop at C1 to C4, which is my recommendation until JJ.2 has shown that the
structured predictor is worth improving.

@GM.Q4(minor, review): The synthetic fixture's six `cut_in` events carry no lateral motion (the partner
sits at a constant offset), so C2 finds no lane change and is rehearsed only through its property tests;
adding a scripted lateral trajectory to `transfer/make_synthetic_fixture.py` would let GM.0 cover C2 and
would show VCC's adapter what a cut-in event looks like in the interface shape.

## References

Ettinger, S., Cheng, S., Caine, B., et al. (2021). *Large scale interactive motion forecasting for
autonomous driving: The Waymo Open Motion Dataset* (arXiv:2104.10133). arXiv.
https://arxiv.org/abs/2104.10133

Krajewski, R., Bock, J., Kloeker, L., & Eckstein, L. (2018). The highD dataset: A drone dataset of
naturalistic vehicle trajectories on German highways for validation of highly automated driving
systems. *2018 21st International Conference on Intelligent Transportation Systems (ITSC)*.
https://arxiv.org/abs/1810.05642

Schumann, J. F., Engström, J., Johnson, L., O'Kelly, M., Messias, J., Kober, J., & Zgonnikov, A.
(2026). Active inference as a model of collision avoidance behavior in human drivers. *Nature
Communications, 17*, Article 5009. https://doi.org/10.1038/s41467-026-73345-0

Wei, R., Garcia, A., McDonald, A., Markkula, G., Engström, J., Supeene, I., & O'Kelly, M. (2023).
World model learning from demonstrations with active inference: Application to driving behavior.
Book chapter, Springer; the chapter is among the papers still missing from `papers/` (HANDOFF.md §6).

Wilson, B., Qi, W., Agarwal, T., et al. (2023). *Argoverse 2: Next generation datasets for self-driving
perception and forecasting* (arXiv:2301.00493). arXiv. https://arxiv.org/abs/2301.00493

*Dataset pages consulted for exiD and INTERACTION (counts as stated on their pages; not re-verified from
the data): the levelXdata exiD page and Zhan et al. (2019, arXiv:1910.03088).*
