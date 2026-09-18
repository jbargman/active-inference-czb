# Building the strand-1 agent, a design note

*2026-09-18, on Jonas's ruling S11.Q3: "Yes, absolutely build it properly." Strand 1 is Engström,
Wei, McDonald, Garcia, O'Kelly & Johnson (2024), *Resolving uncertainty on the fly: modeling
adaptive driving behavior as active inference*, Front. Neurorobot. 18:1341750 — the model
`docs/waymo_program_revisit.md` §1 identifies as the program's own home for the comfort-zone
regime, where this project has been using strand 2's collision-avoidance model instead.*

**Status: a design note. Nothing is authorized and nothing is built.** Every specification below is
quoted or paraphrased from the paper with its location; every judgment is marked. The rules in §5
become binding only when Jonas has read them.

---

## 0 The code situation, because it changes the shape of the work

**There is no code release.** The paper's data availability statement reads, in full: the original
contributions are in the article and supplementary material, and further inquiries should be
directed to the corresponding author. No repository, no Zenodo DOI, nothing in the SI beyond the
model description.

Two consequences:

1. **Ask first.** The corresponding author is Engström, whom Jonas has already spoken to about this
   work (prompt log, 2026-08-22). If he has the code, this note's §5 becomes a port and the
   fidelity of a reconstruction stops being something we have to defend in every later claim.
   Query **S12.Q1**.
2. **A reconstruction is feasible anyway**, and §2 says why: the paper specifies the algorithm in
   prose and gives the preference priors and their defaults in Table 2, and almost all of the
   machinery already exists in `src/aidriver/`.

*[The one repository that does exist in this line, `github.com/ran-weii/interactive_inference` (Wei
et al. 2023), is cloned to `external/interactive_inference` and is **not** this model — it is the
learned inverse-RL branch, it needs the INTERACTION dataset, and it carries no LICENSE file, so it
may be read and not copied. `external/README.md` records that.]*

---

## 1 What strand 1 is, precisely

**The objective** (paper Eq. 1–2), the same shape as strand 2's:

> G(π) = −E_Q(o|π)[log P(o)] − E_Q(s,o|π) D_KL[Q(s|o,π) ‖ Q(s|π)]

pragmatic plus epistemic, in one currency, with the action taken from the first step of the policy
minimising it.

**The state space** (Table 1) carries something strand 2 has no analogue of: a **discrete context
variable** `I` — whether a pedestrian is present behind the occlusion — alongside a discrete
conflict indicator `C`, the pedestrian's position and the ego's kinematics. The context is what the
epistemic term buys information about.

**The preference priors and their defaults** (Table 2), quoted:

| preference prior | specification | default |
|---|---|---|
| speed keeping | Gaussian centred at the speed limit | μ = 10 m/s, **σ = 1 m/s** |
| lane keeping | triangular, centred at 0, bounded at the lane boundaries | — |
| acceleration | Gaussian centred at zero, x and y | μ = 0, **σ = 0.5 m/s²** |
| conflict | **categorical, an absolute preference over "no conflict"** | — |

The paper adds that these "were set by hand and no systematic model optimization was performed",
and that the purpose was to demonstrate the principles rather than to achieve optimal performance.

**The implementation**: an SIR particle filter with systematic resampling when N_eff < N/2; EFE by
propagating particles through the transition and observation models; the posterior predictive
entropy by **KDE**; policies by **CEM**; a planning horizon of 4 s; a 200 ms step.

**The two demonstrations**: the occlusion scenario (slow down while uncertain, speed up once the
line of sight resolves it, and move laterally to reach the line of sight sooner — an *epistemic
action*), and visual time-sharing with a secondary task.

---

## 2 What we already have, and what has to be new

| piece | where it is | state |
|---|---|---|
| kinematic bicycle model, rollout | `src/aidriver/bicycle.py` | reusable as is |
| SIR particle filter with ESS resampling and roughening | `src/aidriver/agent.py` | reusable; strand 1 has **no norm conditioning**, so the norm branch is switched off rather than replaced |
| CEM planner with the pedal constraint | `agent._cem` | reusable; the horizon changes from 30 steps to 4 s |
| EFE with a pragmatic and an epistemic part | `agent.expected_free_energy` | reusable in shape; the epistemic term must change (below) |
| triangular lane-keeping prior | `preferences.log_lateral_pref` | reusable — strand 1 uses the same form |
| Gaussian speed and acceleration priors | `preferences.log_speed_pref`, `log_accel_pref` | reusable; the σ values change |
| **a categorical conflict preference** | — | **new**: an absolute preference, i.e. an admissibility constraint, not a graded cost |
| **a discrete context variable in the belief** | — | **new**: `I`, with its own observation model and the line-of-sight geometry |
| **KDE posterior predictive entropy** | — | **new**: strand 2 uses a closed-form Gaussian approximation; strand 1 uses a KDE and the difference is not cosmetic when the belief is multimodal, which is exactly what a context variable makes it |

*[Opinion: the honest estimate is that the reusable fraction is large but the three new pieces are
where the model's behaviour comes from, so "we already have most of it" would be the wrong thing to
tell anybody.]*

---

## 3 The differences from the released model, which are the whole argument

| | strand 2 (Nature, collision avoidance) | strand 1 (Frontiers, uncertainty) |
|---|---|---|
| σ_v, speed tolerance | 0.5 m/s | **1.0 m/s** — twice as tolerant |
| σ_a, effort tolerance | 0.1 m/s² | **0.5 m/s²** — five times as tolerant |
| collision | −10 000 log units × a severity linear in impact speed | **categorical, absolute "no conflict"** |
| braking margin (`p_safe`) | indicator on a_req < −a_max, × −10 000 × severity | **does not exist** |
| inverse-τ preference | one-sided Gaussian on τ⁻¹ inside `p_coll` | not present |
| road edge | −15 000 | triangular, bounded at the lane boundaries |
| epistemic value | α = 1, closed-form Gaussian approximation | KDE, and it is the point of the model |
| belief | norm-conditioned particle filter, hand-written per-scenario norms | SIR particle filter, no norm conditioning |
| context | none | a discrete context variable the epistemic term resolves |
| horizon | 30 steps × 0.2 s = 6 s | 4 s |

**Read the first four rows together and the reformulation note's central proposal is in the
authors' own table.** `docs/active_inference_reformulation.md` §4 item 3 argued that the catastrophe
factors belong in the *admissibility of a policy* rather than as a cost ten thousand times the
comfort terms, and that the comfort terms need tolerances wide enough to do work. Strand 1 does
exactly both. And **strand 1 has no braking-margin term at all** — the term card RE.2 measured at
ρ = −0.861 against the share who intervene, and which `preferences.py` calls "the comfort-zone
term", does not exist in the model the program puts in the comfort-zone regime. Its role is played
by the conflict constraint together with the acceleration prior, which is precisely "can I avoid
this without harsh braking", which is card S1.1's comfort margin.

---

## 4 What the comfort zone becomes here

In strand 2 the comfort-zone boundary was sought as a **level set of a scalar field** evaluated on a
frozen scene. Three cards have now shown that cannot work: RE.2 (no constants), RE.4 (no
functionals), and the flat ε of RE.1.

In strand 1 the natural object is different: the agent **equilibrates**. Given its preferences and
its uncertainty it settles at a speed and a spacing — the paper's own occlusion result is a speed
that dips while uncertain and recovers when the uncertainty resolves. So:

> **The comfort-zone boundary is the operating point a driver's preferences and uncertainty settle
> at, and a driver's comfort zone is the set of states from which they do not have to leave that
> operating point.**

This is why §2 of `docs/waymo_program_revisit.md` stops being an obstacle. That section found that
our stimuli pin four of the six released preference factors at exactly zero, because the ego never
acts. An equilibrium is not evaluated on a frozen scene — it is **simulated**, and a simulated agent
does act, so its speed, effort and lane terms come alive. The frozen clip then plays its proper
role: a participant saying "I would intervene here" is a datum about where *their* operating point
is, not a regression target for a field.

---

## 5 The build, as a card ladder with pre-stated rules

Each card can kill the next. Nothing below is authorized.

**S1.3 — the agent, and the paper's own Scenario 1.** Build the strand-1 preference (the four
priors of §1, behind flags defaulting to the released behaviour, standing rule 3), the categorical
conflict constraint, the context variable and the KDE epistemic term, in `src/strand1/` with
property tests in the `check()` style. Then reproduce the paper's occlusion scenario.
**Rule:** the speed trace must show the dip while uncertain and the recovery after the line of
sight, and switching the epistemic term off must remove the lateral move toward the line of sight.
Those are the paper's two qualitative claims and they are what a reconstruction has to earn.

**S1.4 — free following, and this is the cheap one that can stop the line.** Card GZ.1 found the
*released* configuration does not hold sustained car following: it brakes after 3–5 s with nothing
happening. Run the strand-1 agent behind a constant-speed lead for 60 s at several headways.
**Rule:** no spontaneous braking below −0.5 m/s² in 60 s at a 1.5 s headway, and a settling headway
that is finite and repeatable across seeds. If a comfort-zone model cannot sit still behind a lead
it cannot have a comfort zone, and the line stops here.

**S1.5 — the boundary as an equilibrium.** Sweep the driver's own constants — the acceleration
tolerance σ_a and the assumed worst case — and read off the settling headway and speed.
**Rule:** the settling headway must move monotonically with the effort tolerance, and the range it
covers across plausible drivers must contain the headways the studies' participants accept. If the
model equilibrates but always at 0.3 s or always at 4 s, it is not measuring this population.

**S1.6 — the cut-in.** Run the agent through the second study's own stimuli and compare the moment
it acts with the moment participants say they would.
**Rule:** the project's standing one — held-out wRMSE on the 378 cells, the registered folds and
metric, against the gated looming rule's 0.1027 and the gap's 0.1522.

**S1.7 — per-driver.** Only if S1.6 holds: fit the driver's preference constants per participant,
with Wei et al.'s (2023) identifiability treatment adopted rather than rediscovered
(`docs/waymo_program_revisit.md` §4). **Rule:** card TR.1's Spearman interval [+0.407, +0.798] for
the per-driver levels across two scenarios.

---

## 6 What would falsify this, and one thing that already limits it

**Falsification.** S1.4 is the cheapest and the most likely to fail: an agent that cannot hold a
following distance has no comfort zone. After that, S1.5 — a model that equilibrates but not in the
human range is measuring something else. After that, S1.6 on the project's own metric.

**The limit that is already known, and it is not about the model.** Card S1.2 found that the second
cut-in study is the **only** design in this project that varies gap and closing speed independently:
study 1's cut-in is one-dimensional (all four axes tried there are rank-identical, Spearman
+1.0000), the left turn holds one oncoming speed per cell, the overtake varies lateral clearance.
So S1.6 can be run on exactly one design, and any result there cannot be confirmed by transfer
within the data we have. That is an argument for a new stimulus set (query WP.Q2) or for the
naturalistic data, independent of anything strand 1 does.

---

## 7 Queries

- **S13.Q1 (judgment, jonas):** build order. S1.4 is the cheap killer and needs only the preference
  and the planner, not the context variable or the KDE. Build the minimum for S1.4 first and only
  then the occlusion scenario for S1.3, or reproduce the paper first so that the reconstruction is
  validated before anything is claimed from it? *[Opinion: S1.3 first. A result from an unvalidated
  reconstruction of somebody else's model is worth very little, and S1.3 is the only card here that
  checks the reconstruction against something the authors published.]*
- **S13.Q2 (judgment, jonas):** the strand-1 defaults were "set by hand" by the authors for a
  demonstration. Do we take them as given for S1.4 and S1.5, or is the first thing to do a
  sensitivity over them? They are not calibrated to anything, so treating them as a reference the
  way the project has treated the Nature constants would repeat the mistake
  `docs/waymo_program_revisit.md` §1 describes.
- **S13.Q3 (minor, review):** strand 1 has no norm conditioning at all, while this project has built
  a cut-in norm (card PN.1, `src/comfortzone/norms.py`). Does the strand-1 build leave norms out, as
  the paper does, or is the norm the natural place to put Jonas's "expecting and accepting a closing
  speed as long as it is far away"? The second is a bigger model than the paper's.
- **S13.Q4 (judgment, review):** the KDE epistemic term is the one piece where a reconstruction can
  differ from the original silently, because it is an approximation choice inside a term whose scale
  the released model already gets wrong (`docs/method_review.md` §6.4). What check would make it
  trustworthy short of having the authors' code?
