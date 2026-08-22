# Active inference for driver modeling — method overview

This is the synthesis: what the method actually is, where it came from, how it is used for driver
behavior, what it buys you over the alternatives, where it is weak, and how it connects to
comfort-zone boundaries. Sources are the seven papers in `papers/active-inference/` (summarized in
`01_paper_summaries.md`) plus the online material listed at the end.

---

## 1. The core idea in one page

Active inference comes from computational neuroscience (Friston and colleagues; the free-energy
principle). Its claim is that perception, learning and action are all the *same* operation:
minimizing **free energy**, which is a tractable upper bound on **surprise** (negative log evidence)
— the extent to which the agent's sensory observations depart from what its internal model expects.

Two objectives, two roles:

| Objective | Minimised over | Role |
|---|---|---|
| **Variational free energy (VFE)** | beliefs `Q(s)` | perception / state estimation |
| **Expected free energy (EFE)** | policies `π` | action selection / planning |

An agent that can plan picks the policy with the lowest **expected** free energy:

```
G(π) = − E_Q(o|π)[ log P(o) ]                          ← pragmatic value  (goal seeking)
       − E_Q(s,o|π) D_KL[ Q(s|o,π) ‖ Q(s|π) ]          ← epistemic value  (information seeking)
```

The whole trick is in `P(o)`, the **preference prior**: a distribution over observations in which
the observations the agent *wants* are also the ones it deems *most probable*. Because preference is
encoded as probability, "achieving my goal" and "not being surprised" are literally the same
quantity. The agent is not maximizing a reward that sits outside its model — it is acting to make
its own predictions come true.

The epistemic term decomposes usefully:

```
E_Q(o|π) D_KL[Q(s|o,π)‖Q(s|π)] = H[Q(o|π)] − E_Q(s|π) H[P(o|s)]
                                  posterior      expected ambiguity
                                  predictive
                                  entropy
```

— i.e. value a policy for producing a *variety* of observations (potential to learn), but discount
it if those observations are *unreliable* in the states visited (darkness, occlusion, a glance away
from the road). Epistemic value is exactly *expected Bayesian surprise*.

**The consequence that matters for driving:** pragmatic and epistemic value are in the *same
currency*. The progress-vs-caution trade-off that traffic psychology has described qualitatively for
fifty years (risk homeostasis, zero-risk theory, task-capability interface) does not need an
arbitration mechanism — it falls out of a single scalar objective. That is the central selling point
of Engström et al. (2024).

---

## 2. How the Waymo/TU-Delft program instantiates it

Nothing in the framework says *how* to compute any of this for a continuous, high-dimensional,
partially observable driving scene. The program's engineering answer, stable across the papers:

| Component | Choice | Why |
|---|---|---|
| Generative model | discrete-time POMDP, bicycle-model dynamics | tractable, interpretable |
| Belief `Q(s)` | **particle filter** (N≈75), non-parametric | handles multimodality (pedestrian present / absent; will cut in / won't) |
| Belief update | Bayes; later KDE→GMM representation | GMM version allows belief to move *outside* the initial particle spread |
| Prediction | roll particles forward with noise on *others'* controls | generates the long tail of other-agent behavior |
| Policy search | **CEM** MPC (M≈100 policies, K≈10 iterations, elite β=0.1) | derivative-free, works with mixed discrete/continuous actions |
| EFE estimation | sample-based averaging over particles | avoids intractable integrals |
| Horizon | 4 s (Engström) → 6 s / H=30 at Δt=0.2 s (Schumann) | |

**Bounded rationality is deliberate, and the results depend on it.** The number of evaluated policies is capped;
CEM sometimes returns a sub-optimal policy; Wei et al. put an explicit KL information-processing
cost in the value function. Humans are not optimal planners, and a model that plans optimally
reproduces the wrong behavior.

### The three additions that make it work for safety-critical behavior (Schumann et al.)

1. **Looming perception** — observe `φ, φ̇`, not distance and speed. Distance-dependent uncertainty
   and a detection threshold (`φ̇₀ = 0.00215 s⁻¹`) come out for free, so detection delay is
   *derived* rather than fitted.
2. **Norm-conditioned prediction** — bias predicted other-agent trajectories toward norm compliance,
   but cap the trust by *current* observed compliance, so the model is relaxed in normal driving and
   opens up to the kinematic long tail the instant someone violates a norm. This single mechanism
   resolves the "either paranoid or oblivious" dilemma of purely kinematic prediction.
3. **Surprise accumulation → re-planning** — the model plans *incrementally* by default and does a
   *full re-plan* only when accumulated surprise crosses a threshold. This is where response timing
   comes from.

### The response-timing mechanism, stated precisely (this is the piece to reuse)

Evidence accumulates as
```
E_t = E_{t−1} + λ · ε_t ,        replan when E_t ≥ 1
ε_t = H·max_o log p(o) − Σ_{τ=t+1}^{t+H} g_pragm( q̃_o(o_τ | π_t, q(s_t)) )   ≥ 0
```
`ε_t` is the **residual information of the pragmatic value**: how far short of the best-possible
expected observations the *current* policy now falls. If the current plan still delivers the
preferred future, `ε = 0` and nothing accumulates — a genuine zero-floor, so an unfolding but
still-comfortable situation does not drive the agent toward action. `λ` is the drift rate in
drift-diffusion terms; it is by far the model's most sensitive parameter.

This is a **direct computational bridge** between the surprise literature and the classic
response-time literature: the drift rate of a DDM is being supplied by an information-theoretic
quantity computed from the agent's own generative model, rather than being a free parameter fitted
per scenario. And because `ε_t` depends on the predicted future under the current policy, response
timing becomes *kinematics-dependent* automatically — which is the empirical finding (Markkula et
al.) that fixed reaction-time models cannot reproduce.

---

## 3. Surprise: the measurement layer

`Measuring surprise in the wild` and the Modirshanechi et al. taxonomy give a clean structure. Three
families, by *what is compared with what*:

- **Probabilistic mismatch** — observation vs prior belief. (Shannon surprisal, S8, **residual
  information**, Bayes-factor surprise, state prediction error.)
- **Belief mismatch / information gain** — posterior belief vs prior belief. (**Bayesian surprise**
  = KL, postdictive surprise, **antithesis**.)
- **Observation mismatch** — actual vs predicted observation. (absolute / squared error, unsigned
  RPE.)

Modirshanechi et al. add a fourth semantic axis — *change-point detection* surprise (Bayes-factor
surprise, differences in Shannon surprise), designed to modulate learning rate rather than to
express puzzlement — and *confidence-corrected* surprise (Faraji et al.), which scales the violation
by how confident the agent was.

Two properties decide which measure is usable in practice, and they are the reason the Waymo group
invented two new ones:

- **Zero-floor** — is the measure zero when the most-expected thing happens? Surprisal is not
  (it returns `−log P(mode) > 0`), which is both empirically wrong and practically awkward if you
  are going to *accumulate* it. Residual information is.
- **Parameterlessness on continuous distributions** — surprisal and S8 need a bin size ε and are
  sensitive to it (surprisal diverges as ε→0; S8 vanishes). Residual information's ε cancels, so the
  categorical formula transfers unchanged to densities.

Belief-mismatch measures have a distinct advantage for *early* detection: they compare predicted
futures, so they implicitly see higher derivatives — a hard brake changes the predicted future
position long before it changes the current position. But plain KL fires on *unsurprising*
information gain (mode-narrowing and mode-removal), which is what **antithesis** exists to suppress
by integrating only where a previously-unexpected outcome became more likely.

Two timing parameters run through all of it: the **history window `h`** (how stale the prior is) and
the **lookahead `z`** (which future time the two beliefs are about). Larger `h` gives larger, earlier
peaks; the effect of `z` is not monotone and is scenario-dependent.

---

## 4. What this buys you, versus the alternatives

| | Mechanistic models (looming/DDM, TTC rules) | ML behavior models | Active inference |
|---|---|---|---|
| Generalizes across scenarios | ✗ one model per scenario | ✓ | ✓ (demonstrated on 3, one held out) |
| Covers timing + selection + execution | ✗ usually one | ✓ | ✓ |
| Interpretable | ✓ | ✗ | ✓ (traces to beliefs and preferences) |
| Handles safety-critical tail | ✓ (if built for it) | ✗ under-represented in data | ✓ (norm-conditioned long tail) |
| Uncertainty-driven behavior (occlusion, glances) | ✗ mostly | implicit | ✓ explicitly, as epistemic value |
| Needs a hand-built generative model | ✓ | ✗ | ✓ ← **the cost** |

The honest reading: active inference is not a better curve-fit than a learned model — it is a
*narrative* that unifies mechanisms that were previously separate, and the unification is
computationally central rather than decorative. The price is that someone must specify the
generative model and the preference function, and 13 parameters got hand-tuned.

**Known weaknesses to keep in view:**
- *Unsophisticated inference* — future beliefs are not conditioned on counterfactual future
  observations, so the agent cannot reason about how its own beliefs will change.
- *Non-reactive others* — the other vehicle ignores the ego, so there is no negotiation, no
  interaction, no social layer. (The "shared schema"/communication strand is flagged as ongoing on
  the 2024 poster and does not appear to be published.)
- *Hand-coded norms per scenario.*
- *Falsifiability* — with a free preference function and 13 tuned parameters, "EFE minimisation
  explains it" risks being unfalsifiable. The held-out intersection scenario is the strongest
  counter-argument and should be the template for any extension we make.
- *Computational cost* — particle filter × CEM × horizon is expensive; the reference code is
  written for GPU.

---

## 5. The bridge to comfort-zone boundaries

This is where the whole thing points for our purposes, so it is worth being precise about the
correspondence.

**Comfort-zone boundary (CZB)** in the traffic-psychology tradition (Näätänen & Summala's zero-risk
theory; Ljung Aust & Engström; the Chalmers LTAP/OD and pedestrian-overtaking work): a dynamic
spatiotemporal envelope around the vehicle inside which the driver feels comfortable. The
*comfort-zone boundary* is the limit drivers do not cross voluntarily **without extra motives**; the
*dread-zone boundary* is the further limit they do not cross **even with** extra motives. "Extra
motives" (being late, angry, frightened) are what make a driver accept normally-unacceptable
discomfort.

The active-inference reading of that:

| Traffic-psychology construct | Active-inference counterpart |
|---|---|
| Comfort zone | region of state space where the current policy still achieves preferred observations → `ε_t ≈ 0` |
| Comfort-zone **boundary** | iso-surface where accumulated surprise starts to drive behavioral change, i.e. where `ε_t` departs from zero / `E_t` approaches threshold |
| Dread-zone boundary | where `p_safe`/`p_coll` collapse — states from which the preferred outcome is no longer reachable under any policy |
| Extra motives | reshaping of the preference prior `P(o)` (e.g. tighter, higher-precision speed preference when hurried) |
| Comfort-zone exceedance → evasive action | accumulated evidence crosses threshold → **full policy re-plan** |

Three things make this more than an analogy:

1. **`p_safe` is already a comfort-zone term.** In Schumann et al. the preference function contains
   an explicit factor penalizing states from which *a collision would become unavoidable if the lead
   vehicle braked hard and I responded after 1 s*. That is a safety-margin envelope written as a
   probability — a computable comfort-zone boundary, already inside the model.
2. **Residual information gives a zero-floored, parameterless scalar** that is exactly zero inside
   the comfort zone and grows as you leave it. That is precisely what a CZB metric needs: quiet in
   normal driving, monotone in discomfort, no arbitrary bin size.
3. **The boundary becomes a level set, not a threshold on one kinematic variable.** Classic CZB work
   quantifies boundaries in terms of a chosen indicator (min TTC, THW, lateral clearance) per
   scenario. A surprise/pragmatic-value formulation gives a *scenario-independent* scalar field over
   the state space; the CZB is a level set of it. The kinematic indicators then become
   *projections* of that surface — which would explain why they differ per scenario, and give a
   principled way to compare boundaries across scenarios.

**The practical method this suggests** (to be built and tested here):

> Define the comfort-zone boundary as the level set `{x : g_prag(x) = c}` — equivalently
> `{x : ε(x) = c}` — of the residual information of the pragmatic value under a driver's preference
> prior, evaluated over the reachable state space. Calibrate `c` against observed behavior: the
> boundary is where humans start to act (evidence crosses threshold). The dread-zone boundary is the
> level set beyond which no policy can restore preferred observations.

Note the two distinct uses of "surprise" that must not be conflated, because the library needs both:
- **surprise about the world** (another road user did something unexpected) — measured against a
  *predictive* generative model; this is `Measuring surprise in the wild`, and it is what conflict
  detection and response-onset need;
- **surprise about one's own preferred state** (I am in a situation I do not want to be in) —
  measured against the *preference prior*; this is `ε_t` in the collision-avoidance model, and it is
  what comfort-zone boundaries need.
They are the same mathematical object (residual information of a log-probability) applied to two
different distributions. Keeping that distinction explicit in the code is worth doing.

---

## 6. Online research — what is out there beyond these papers

- **pymdp** (Heins et al., JOSS 2022; `infer-actively/pymdp`) — the reference Python library for
  active inference, but **discrete state spaces only** (categorical POMDPs, A/B/C/D matrices). Good
  for learning the formalism and for toy grid-worlds; *not* usable for continuous vehicle dynamics.
  Our setting needs the particle-filter/CEM style of the Waymo papers, which is why they wrote their
  own. Useful cross-check: pymdp's EFE decomposes into *risk* + *ambiguity*, a slightly different
  (but equivalent-family) split from the pragmatic/epistemic form used in the driving papers.
- **Modirshanechi, Brea & Gerstner (2022), "A taxonomy of surprise definitions"**, J. Math. Psych.
  110:102712 — the rigorous map: 10 measures, 18 definitions, 4 semantic categories (prediction,
  change-point detection, confidence-correction, information gain). Includes the proofs of when
  measures are *indistinguishable* (e.g. state prediction error is a strictly increasing function of
  Shannon surprise, `S_SPE = 1 − exp(−S_Sh)`; absolute error = 2×SPE for one-hot categorical
  observations; squared error ↔ Shannon surprise for isotropic Gaussians). Directly informs which
  metrics are worth implementing separately and which are redundant.
- **Liakoni et al. (2021), Bayes-factor surprise** (*Neural Computation* 33:269) — surprise as a
  learning-rate modulator; `S_BF = P(y|prior π⁰) / P(y|current belief π^t)`. Conceptually distinct
  from the others: it asks "has the world changed?" not "was that unlikely?".
- **Faraji, Preuschoff & Gerstner (2018), confidence-corrected surprise** — scales violation by
  belief confidence (negative entropy).
- **Kolekar, de Winter & Abbink (2020), driver's risk field** and **da Lio et al. (2023), affordance
  competition** — the nearest non-active-inference computational relatives; worth reading as
  baselines to compare a CZB method against.
- **Engström, Bärgman, Nilsson, Seppelt, Markkula, Piccinini & Victor (2018), "Great expectations:
  a predictive processing account of automobile driving"**, *Theor. Issues Ergon. Sci.* 19:156–194 —
  the conceptual predecessor of this whole line, and the natural citation for framing CZB work in
  predictive-processing terms.
- Chalmers CZB literature to connect to: the LTAP/OD comfort-zone/dread-zone quantification
  (*Transp. Res. F*, 2015) and the pedestrian-overtaking CZB work (*AAP*, 2019) — both quantify
  boundaries per scenario from naturalistic/field data, which is exactly the empirical target a
  surprise-based level-set formulation would have to reproduce.

**Sources:**
[pymdp (JOSS)](https://joss.theoj.org/papers/10.21105/joss.04098) ·
[pymdp arXiv](https://arxiv.org/abs/2201.03904) ·
[pymdp tutorial](https://github.com/infer-actively/pymdp/blob/master/docs/notebooks/active_inference_from_scratch.ipynb) ·
[A taxonomy of surprise definitions](https://infoscience.epfl.ch/server/api/core/bitstreams/136c49b3-6739-4fa5-8fa5-7bbc42d3f588/content) ·
[Surprise: a unified theory (bioRxiv)](https://www.biorxiv.org/content/10.1101/2021.11.01.466796v1) ·
[Bayes Factor Surprise](https://direct.mit.edu/neco/article/33/2/269/95646/Learning-in-Volatile-Environments-With-the-Bayes) ·
[Resolving uncertainty on the fly (Frontiers)](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2024.1341750/full) ·
[Active inference collision avoidance (Nat Commun)](https://www.nature.com/articles/s41467-026-73345-0) ·
[Quantifying comfort-zone and dread-zone boundaries (LTAP/OD)](https://www.sciencedirect.com/science/article/pii/S1369847815001540) ·
[Chalmers copy of the same](https://publications.lib.chalmers.se/records/fulltext/225573/local_225573.pdf) ·
[How do drivers overtake pedestrians?](https://www.sciencedirect.com/science/article/pii/S0001457519305391) ·
[Great expectations](https://www.tandfonline.com/doi/full/10.1080/1463922X.2017.1306148)
