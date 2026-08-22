# Active inference papers — individual summaries

Seven papers in `papers/active-inference/`, read in full (text extracted to `notes/paper_text/`).
Read order below is chronological, which also happens to be the order in which the modeling
program was built up.

Shorthand used throughout:
**EFE** = expected free energy, **VFE** = variational free energy, **POMDP** = partially observable
Markov decision process, **CEM** = cross-entropy method, **KDE** = kernel density estimate,
**GMM** = Gaussian mixture model.

---

## 1. Wei, Garcia, McDonald, Markkula, Engström, O'Kelly (2023) — *Learning an active inference model of driver perception and control: application to vehicle car-following*
`2023 - An active inference model of car following.pdf` — arXiv 2303.15201

**Question.** Can an active-inference driver model be *learned from data* rather than hand-tuned?

**Approach.** Frames driver perception+control as a POMDP in which the human's internal model
(transition `T(s'|s,a)`, observation `O(o|s)`) and preferences (reward) are both unknown and must be
estimated from demonstrations — an inverse RL problem under partial observability. The key
difficulty is *non-identifiability*: many (reward, internal-model) pairs rationalize the same
demonstrations. They resolve it with a structural prior assumption: (i) preferences and world-model
are independent, and (ii) the world-model parameter distribution concentrates on values with high
data log-likelihood (i.e. restrict to agents whose internal models are *reasonably accurate*). This
yields a MAP estimator solvable as a **bi-level optimization** — outer loop maximizes the posterior,
inner loop solves for the optimal policy — approximated by stochastic gradient descent with a nested
policy-optimization step. Information-processing cost is a KL term between policy and a default
policy (`c = α·D_KL(π‖π₀)`), giving a *soft* Bellman equation (contraction mapping, unique fixed
point) — so bounded rationality is built in at the value-function level rather than bolted on.

**Result.** On a naturalistic highway car-following dataset the active-inference model outperforms
behavior cloning and is competitive with IDM on aggregate measures, while remaining interpretable
(behavior traces back to perception and preferences). **But**: it is inaccurate in extreme scenarios
and shows higher online collision rates than IDM, because the dataset contains no collisions and few
extreme observations — a distribution-shift failure.

**Why it matters here.** This is the "learn the generative model from data" branch. Its failure mode
is exactly the motivation for the hand-built Schumann model: safety-critical behavior is
under-represented in naturalistic data, so learning alone cannot deliver representative collision
avoidance. Also the clearest statement in the set of *bounded rationality as an explicit
information cost*.

---

## 2. Dinparastdjadid, Supeene, Engström (2023) — *Measuring surprise in the wild*
`2023 - Measuring surprise in the wild.pdf` — arXiv 2305.07733

**This is the single most directly useful paper for the surprise-metrics library.**

**Question.** How do you *measure* surprise in real traffic, rather than in a lab?

**Approach.** Beliefs are the output of a machine-learned generative model (a MultiPath-style
trajectory predictor with a Wayformer encoder) that emits, for each agent, a weighted set of
candidate trajectories with Gaussian position uncertainty per timestep — i.e. a **GMM over future
position** at each future time. That GMM *is* the belief distribution against which surprise is
measured. Positions are decomposed into lateral/longitudinal components in a body frame, so you get
a lateral and a longitudinal surprise time series.

**Two timing parameters** (these matter a lot in practice):
- **history window `h`** — how far back the prior was generated (prior made at `t−h` about time `t`).
- **lookahead `z`** — for belief-mismatch measures, both prior (made at `t−h`) and posterior (made at
  `t`) are about the *same* future time `t+z`.

**Taxonomy used** (after Modirshanechi et al.): *probabilistic mismatch* (observation vs prior),
*belief mismatch* (prior belief vs posterior belief), *observation mismatch* (predicted vs actual
observation).

**Measures.**
- *Surprisal* `S(x;P) = −log P(x)`. Two problems for this use: (a) it is non-zero for the most likely
  outcome — no **zero-floor** — contradicting empirical human surprise reports (Macedo et al. 2004);
  (b) for continuous distributions you must bin with size ε, and the value is ε-sensitive and
  diverges as ε→0.
- *S8* (Macedo) `log₂(1 + max_x' P(x') − P(x))`. Has the zero-floor but no information-theoretic
  interpretation, and →0 as ε→0.
- **Residual information (new)** `h_r(x;P) = log(max_x' P(x')) − log P(x) = log(max_x' P(x')/P(x))`.
  Difference in information content between the observed outcome and the most likely outcome.
  Zero when the mode is observed (**zero-floor ✓**), **parameterless ✓** (the ε in the discretized
  version cancels in the limit, so the categorical formula carries over to continuous densities
  unchanged), and **information-theoretically meaningful ✓**. This is the measure that the
  Engström/Schumann response-timing models accumulate as evidence.
- *Bayesian surprise* `D_KL(P(·|y) ‖ P)` — the standard belief-mismatch measure. Problem in practice:
  the posterior is made with extra information, so uncertainty almost always shrinks even when the
  mode does not move; hence KL is essentially never zero. It fires on *unsurprising* information gain.
- **Antithesis (new)** — KL restricted to the region where an *a-priori unexpected* outcome became
  *more* likely:
  `C(P,x,y) ≡ [log P(x) < E_x'[log P(x')]] ∧ [P(x|y) > P(x)]`
  `A(y;P) = ∫_{C} P(x|y) log(P(x|y)/P(x)) dx`
  The two conditions are the "outside expectations" condition (information content below average —
  i.e. `−log P(x) > H[P]`) and the "increased belief" condition. Together they silence
  *mode-narrowing* (confirming a single expectation) and *mode-removal* (resolving between several
  plausible outcomes, e.g. the turn-signal case), which are information gain but not surprise.
  Empirically zero far more often than KL, so better discriminative power.

**Key practical advantage of belief-mismatch measures**: comparing predicted *futures* implicitly
picks up higher time-derivatives — a hard deceleration changes predicted future position a lot
before it has moved current position much — so surprising actions are detected *earlier*.

**Three named applications** (all relevant to us): (i) **traffic-conflict definition** — condition
conflicts on surprise *and* spatiotemporal proximity, which cuts false positives (an intentional
small-TTC overtake is not a conflict); this matches the ISO/TR 21974-1:2018 "not premeditated"
requirement; (ii) **response-time modeling** — surprise onset defines the stimulus onset, solving
the "when do you start the clock" problem in naturalistic conflicts; (iii) **driving-behavior
evaluation** — predictability as an AV behavior metric.

**Limitations they flag.** No *relevance filtering* — an attention-like mechanism to decide which
surprising events matter for the ego's current task (a surprising stop on a parallel road is
irrelevant). Also notes the deeper active-inference view: surprise is not only about external states
but about deviation from the agent's *preferred* state ("I'm making safe progress toward the
destination") — which is exactly the bridge to comfort-zone boundaries.

*(Note: the paper carries a Waymo patent declaration covering these techniques — relevant if this
ever goes beyond research use.)*

---

## 3. Engström, Wei, McDonald, Garcia, O'Kelly, Johnson (2024) — *Resolving uncertainty on the fly: modeling adaptive driving behavior as active inference*
`2024 - Resolving uncertainty on the fly...pdf` — Front. Neurorobot. 18:1341750

**This is the base model that everything later extends.**

**Question.** Can one principle — EFE minimisation — account for adaptive driving behavior, i.e.
the progress-vs-caution trade-off, without separate mechanisms for each phenomenon?

**Positioning.** Traffic-psychology motivational models (risk homeostasis, zero-risk theory, TCI)
capture the excitatory/inhibitory balance but are conceptual, not computational. ML models learn it
but are black boxes. The nearest computational relatives are Kolekar et al.'s (2020) driver's risk
field (zero-risk + Gibson's field of safe travel; limited to static scenarios) and da Lio et al.'s
(2023) affordance-competition model.

**Formulation.**
```
G(π) = −E_Q(o|π)[log P(o)]                              (pragmatic value)
       − E_Q(s,o|π) D_KL[Q(s|o,π) ‖ Q(s|π)]             (epistemic value)
```
with the standard identity
```
E_Q(o|π) D_KL[Q(s|o,π)‖Q(s|π)] = H[Q(o|π)] − E_Q(s|π) H[P(o|s)]
                                  ^posterior predictive   ^expected ambiguity
                                   entropy
```
Pragmatic value = goal seeking, scored by a *preference prior* `P(o)` over observations (preferred
observations have highest probability; the precision of the preference = its priority). Epistemic
value = expected Bayesian surprise = value of information; it is discounted when the state does not
generate reliable observations (darkness, occlusion). **The point**: both are in the same currency,
so the exploration/exploitation balance falls out of a single objective — no arbitration mechanism.

**Implementation.** Discrete-time POMDP with mixed discrete/continuous variables; belief `Q(s)` as a
weighted **particle filter** (SIR, systematic resampling when `N_eff ≤ N/2`); EFE computed by
propagating particles through `P(s'|s,a)` and `P(o|s)`; posterior predictive entropy approximated by
**KDE**; policies selected by **CEM** model-predictive control (sample M sequences, keep top r%,
refit, iterate K times; discrete and continuous action components fitted separately). Planning
horizon 4 s. Belief update: `Q(s_t) ∝ exp(log P(o_t|s_t) + E_Q(s_{t−1})[log P(s_t|s_{t−1},a_{t−1})])`.

**Scenario 1 — passing an occlusion.** Ego approaches a stopped bus; a pedestrian may or may not be
hidden (context variable `I`). Behavior that *emerges*: slow down while uncertain (so a stop is
feasible without harsh braking), then speed up once line of sight resolves the uncertainty; and
**move laterally left** to reach the line of sight earlier — an *epistemic action*, taken because it
unlocks pragmatic value sooner.

**Scenario 2 — visual time-sharing with a secondary task.** Uncertainty about lateral position grows
during off-road glances (wind gusts, road irregularity — the Senders 1967 occlusion paradigm);
epistemic value drives glances back to the road, traded against pragmatic value. Reproduces the
human pattern that higher visual demand shortens off-road glances. Uses a bicycle model here (point
mass in Scenario 1).

**Why it matters here.** The occlusion scenario is the cleanest demonstration that epistemic value
does real work; the visual time-sharing scenario connects directly to distraction research. Both are
*non-critical* scenarios — the comfort-zone regime, not the collision-avoidance regime.

---

## 4–5. IWAI 2024 posters
`2024 - Active inference as a general framework... (Engström et al.).pdf`
`2024 - Active inference-based modeling... (Schumann et al.).pdf`

Two-page extended abstracts; useful mainly as a **map of the program**. Engström et al. lay out
three target aspects of driving behavior: (1) managing uncertainty → the Frontiers model;
(2) responding to urgent conflicts → surprise accumulation + the Schumann collision-avoidance model;
(3) **social interaction** → *ongoing/unpublished*: model communicative acts (gesturing, honking,
intent-signalling by yielding) as **epistemic actions** that reduce uncertainty and establish a
*shared schema* for how the situation will play out (who goes first), possibly as generalized
synchrony between agents with similar generative models (Friston & Frith's "duet for one"). That
third strand appears to still be open — a genuine gap.

The Schumann poster gives the compact statement of the model: EFE
`G(π_t) = −Σ_τ [g_pragm(õ_τ) + g_epist(õ_τ, s̃_τ)]`, pragmatic value written explicitly in
*residual-information* form `g_pragm(õ_τ) = E[ln p(õ_τ)] − max_o ln p(o)`, and evidence accumulation
`E_t = E_{t−1} + λ·ε_t` with replanning at `E_t ≥ 1` then reset. Note the poster says "set `E_t=0`"
on replan.

---

## 6–7. Schumann, Engström, Johnson, O'Kelly, Messias, Kober, Zgonnikov — *Active inference as a model of collision avoidance behavior in human drivers*
`2025 - ...unified model...pdf` (arXiv 2506.02215) and
`2026 - ...(Nature Communications).pdf` (Nat Commun 17:5009, doi 10.1038/s41467-026-73345-0)

Same work; the 2026 Nature Communications article is the **version of record** (received 2 Jun 2025,
accepted 6 May 2026) and the one to cite. The arXiv preprint is longer (41 pp) only because it
inlines more figures; the Nature version has the complete Methods. **Code**:
`github.com/tud-hri/Active-Inference-Collision-Avoidance`, Zenodo `10.5281/zenodo.20049511`,
non-commercial license explicitly permitting research use and benchmarking. Data: OSF `osf.io/gs4bu`.

**Gap addressed.** Existing collision-avoidance models are *fragmented*: each covers one scenario
type (front-to-rear, merging), one explanatory factor (off-road glances, cognitive load), or one
output (response time, steering extent). ML models generalize but safety-critical behavior is
under-represented in training data. No model does response **selection + timing + execution** across
**multiple** scenarios.

**Model = Engström et al. (2024) + five new mechanisms:**

1. **Looming-based perception.** The agent does not observe kinematics directly; it observes visual
   angle `φ` and its rate `φ̇` (looming), with *constant* noise in `φ`-space. Because `∂φ/∂Δx`
   shrinks with distance, this automatically produces *distance-dependent* uncertainty about
   position and speed. A **looming threshold** `φ̇₀ = 0.00215 s⁻¹` (from the literature) means small
   relative velocities at long range are simply not perceptible → a principled mechanism for delayed
   detection of lead-vehicle braking, rather than a fitted delay.
2. **Norm-conditioned particle filter.** The transition function factorises as
   `p(s'|s,a) ∝ p_n(s') · p_o(s'|s,a)` — kinematic likelihood times a **projected normative
   probability**. Purely kinematic sampling is far too pessimistic (every adjacent vehicle might
   swerve in); humans assume others obey rules. The projected form
   `p_n(s_τ) ∝ min{ p_n(s_τ), 2·p_n(s_{τ+1})p_n(s_{τ+Hn}) / (p_n(s_{τ+1})+p_n(s_{τ+Hn})) }`
   (harmonic-mean-style combination of short- and medium-term norm compliance, `H_n = 20`) also
   penalizes states that make future norm compliance kinematically *unlikely*. **Crucially** the
   current norm compliance is an *upper bound*: once a vehicle is observed violating a norm, the
   model stops trusting norms for that vehicle and samples the full kinematically-plausible
   long tail. This is what lets one model be both non-paranoid in normal driving and appropriately
   alarmed once the incursion starts.
3. **Surprise-based re-planning (evidence accumulation).** Every step the agent extends its existing
   policy by one action (cheap, incremental). In parallel it accumulates
   `E_t = E_{t−1} + λ·ε_t` where the evidence is the **residual information of the pragmatic value**
   `ε_t = H·max_o log p(o) − Σ_{τ=t+1}^{t+H} g_pragm(q̃_o(o_τ|π_t, q(s_t))) ≥ 0`
   i.e. how far the current policy's expected observations fall short of the best possible. Below
   threshold (=1) → keep extending; at threshold → **full re-plan** of the whole policy. `λ` is the
   drift rate in evidence-accumulation terms. This is what generates human-like response *timing*
   including its kinematics dependence.
4. **Constrained policy sampling (pedal constraints).** CEM sampling of accelerations is constrained
   so that transitions between acceleration and deceleration must pass through `a₀ ≈ −0.1 m/s²` and
   **hold for 0.2 s** — one foot, two pedals. Jerk is limited. Without this the model brakes
   unrealistically fast.
5. **Modified belief update and epistemic value.** Belief update now goes via KDE→GMM (allowing
   belief shifts *outside* the range of the initial particle set, which naive
   weight-and-resample cannot do); epistemic value uses `(1/N)Σ_s p(o|s)` rather than a KDE
   evaluated at kernel centers (the latter over-approximates `q̃_o`).

**Preference function** (the pragmatic value; product of independent factors):
```
p(o) = N(v_ego|μ_v,σ_v) · N(a_long,ego|0,σ_a) · N(ω_ego|0,σ_ω) · p_lat(y_ego) · p_coll(o) · p_safe(o)
```
= desired speed, minimal control input, lateral position/lane keeping, collision avoidance (scaled by
relative impact velocity), **and `p_safe`** — avoid states from which a collision would become
unavoidable, operationalized as: *if the lead vehicle braked suddenly at `a_OV,min`, could I still
avoid it with maximum braking after a 1 s response time?* **`p_safe` is essentially a comfort-zone /
safety-margin term expressed as a preference — see the overview note.**

**Evaluation — three scenarios, one parameter set.**
- *Front-to-rear* (lead vehicle brakes hard): compared against a **meta-analysis of brake response
  times** and deceleration magnitudes from SHRP2 + ANNEXT (Markkula et al.). 28 initial conditions ×
  32 runs = 896 simulations. Reproduces the response-time/time-gap regression and the
  inverse-TTC-at-brake-onset vs deceleration relation.
- *Opposite-direction lateral incursion*: compared against a UK driving-simulator study (Johnson et
  al., Leeds), run on near-identical scenarios — so maneuver choice, collision outcome and both
  brake and steering response times can be compared distributionally.
- *Intersection right-turn-into-path* (vehicle fails to yield): **held out**. Parameters were tuned
  on the first two scenarios only, then applied unchanged to a Canadian simulator study (Ziraldo et
  al.). Fit holds up — the generalization claim.

**Fit metrics.** Mean absolute error `I` via Bayesian linear regression on residuals (response
times, decelerations); **Jensen-Shannon divergence** for categorical outcome distributions;
**Wasserstein distance** for response-time distributions; bootstrap (10 000 resamples) for
uncertainty; a **signal-to-noise ratio > 3** on the difference used as the significance heuristic.

**Parameters.** 26 essential parameters, 12 taken from the literature/prior model, 13 hand-tuned
(no exhaustive optimization — explicitly not the goal). Sensitivity analysis (one at a time,
~1 order of magnitude): sensitivity is **concentrated in the drift rate `λ = 10^−5.95` and the
collision cost `g_C = −10000`**; most other parameters are robust to coarse calibration.
Other values worth knowing: `Δt = 0.2 s`, `H = 30` (6 s horizon), `N = 75` particles, `M = 100`
policies, `K = 10` CEM iterations, `β = 0.1` elite fraction, `σ_v = 0.5 m/s`, `σ_a = 0.1 m/s²`,
`σ_ω = 0.02 s⁻¹`, `g_LL = −15000` (leave road), `g_LC = −1000` (lane boundary/opposing lane),
lane width 3.65 m, vehicle 4.2 × 1.72 m.

**Ablations** (Fig. 6) confirm each new mechanism earns its place — notably removing evidence
accumulation (equivalent to replanning every step) degrades the fit, as does removing pedal
constraints.

**Honest limitations.** Unsophisticated inference (future beliefs are not conditioned on
counterfactual future observations — no `E[surprise]` about one's own future belief updates); the
other vehicle is assumed **non-reactive** to the ego (so no true interaction/negotiation); norms are
hand-implemented per scenario rather than derived from a map; the CEM sometimes fails to find the
optimal policy (they interpret this as bounded rationality, which is convenient but arguably
post-hoc); and the Schumann poster notes the model remains *superhumanly* good at avoiding
collisions even with human-like delays.
