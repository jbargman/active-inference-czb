# Chapter 3: what the model is

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. Provenance:
[Paper], [SI], [Code], [OSF], [Speculation] as defined in chapter 0.*

## The loop

Everything the model does happens inside one loop, run five times per second (every
0.2 s). Chapter 02 showed the loop producing an event; this chapter names its parts.

![The perception-action loop](figures/loop.png)

Each pass: sense the world through looming vision, update a cloud of hypotheses about the
current state, roll each hypothesis a few seconds into the future, check the current plan
against the preferred future, execute the plan's next step — and deposit into the surprise
account whatever shortfall the check revealed. When the account crosses its threshold, and
only then, build a new plan from scratch.

## The components, as input → output boxes

**1. The world (the generative *process*).** What actually happens: two vehicles with
bicycle-model physics, a road, and a scripted other vehicle (chapter 06). The driver model
never sees this directly.
*Input:* both vehicles' controls. *Output:* the true state, advanced 0.2 s. [Code:
`dynamics_true.py` per scenario]

**2. The senses (looming perception).** Converts the true state into what a human eye could
report: the other vehicle's optical angle and its rate of change, plus own-vehicle signals
(speed, pedal state, lateral position). Two consequences come free: measurement noise grows
with distance, and expansion below a visual threshold (0.00215 per second [SI]) is effectively
invisible — so detection distance emerges rather than being fitted.
*Input:* true state. *Output:* a noisy observation vector. [Code: `decoder.py`,
`encoder.py`]

**3. Beliefs (the particle filter).** The model's working memory: 75 parallel hypotheses
("particles"), each a complete candidate state of the world, each weighted by how well it
explained recent observations. The cloud's *spread* is the model's honest uncertainty. When
observations are sharp the cloud is tight (chapter 02's acceleration snap); when the other
vehicle's motives are ambiguous the cloud straddles the options — for example "will brake /
will not" as two co-existing particle populations. Between observations the particles are
*moved* by the same norm-shaped transition that prediction uses (component 4) — the swarm
itself leans toward "others will behave", and observations correct it.
*Input:* previous cloud + new observation. *Output:* updated cloud. [Code:
`particle_filter.py`, `encoder.py`, `kde.py`]

**4. Prediction (imagined futures).** Every particle is rolled forward 6 s (30 steps) under
the physics model. The other vehicle's imagined controls are not raw noise: at each step
each particle holds a small tournament among candidate moves, weighted by norm compliance
— futures in which the other vehicle behaves normally (stays in lane, keeps speed) win the
sampling lottery, but only to the degree that its currently observed behavior has earned
that trust. The norms are thus *inside the swarm's motion*, in the belief update and the
roll-outs alike (chapter 06 makes this precise).
*Input:* belief cloud + a candidate plan for our own controls. *Output:* a bundle of
imagined 6-second futures. [Code: `dynamics.py`]

**5. Preferences (the landscape).** A description of how driving is supposed to go,
encoded as a probability distribution over observations: comfortable speeds, gentle pedals,
staying in lane, no collisions, and a counterfactual safety margin — "even if the lead
braked hard right now and I reacted after one second, ordinary braking would still be
enough". Six independent terms, each with interpretable knobs (chapter 07).
*Input:* an imagined future. *Output:* a score of how preferred that future is. [Code:
`reward.py` per scenario; SI §2.4]

**6. The planner (bounded, not optimal).** Holds one current plan — a 6-second control
sequence. Ordinarily the plan is only *patched*: shifted one step and locally re-optimized
cheaply. A full re-plan — propose ~100 candidate plans, score them all against the
preferred future across the belief cloud, refine the best tenth, repeat ~10 rounds — runs
only when the surprise account demands it. The budget is deliberately capped: the planner
sometimes returns a merely decent plan, which is a modeling commitment about humans, not a
bug [Paper].
*Input:* belief cloud, preferences. *Output:* the (kept or replaced) plan; its first step
goes to the vehicle. [Code: `mpc_discrete.py`]

{{R1}}**7. The surprise account (evidence accumulation).** The response-timing mechanism, and the
piece this project reuses for comfort zones. Each step it receives the gap between what the
current plan is now expected to deliver and the best that could be expected — zero only if
every imagined future works out, which in practice it never quite does (chapter 02) —
multiplied by a rate constant and added to a running total. Threshold crossed → full
re-plan → total resets.
*Input:* the plan's scored shortfall. *Output:* the re-plan trigger. [Paper Eq. 13]

## Two currencies, one ledger

The scoring in component 5 has two parts, and their shared currency is the framework's
main selling point:

- **Pragmatic value** — how well an imagined future matches the preferred one. This is
  goal-seeking: progress, comfort, safety margins.
- **Epistemic value** — how much an imagined future is expected to *teach* the model, by
  reducing the belief cloud's spread where it matters. This is information-seeking:
  looking, probing, easing off to see what the other driver does.

Both are measured in the same units and simply added, so caution and progress trade
against each other without an arbitration rule. In the published collision-avoidance runs
the pragmatic part dominates [Paper]; the epistemic part is the natural hook for glance
behavior and uncertainty-driven slowing (chapter 08).

## What is deliberately human about it

| Design choice | The human claim behind it |
|---|---|
| Looming instead of range sensors | drivers see angles, not odometry; distant threats are genuinely harder to perceive |
| A particle cloud instead of one estimate | drivers entertain multiple readings of an ambiguous scene at once |
| Norm-shaped prediction | drivers expect others to behave; trust is withdrawn when observed behavior stops earning it |
| A capped planning budget | drivers satisfice; an optimal planner reproduces the wrong behavior |
| Surprise-gated re-planning | drivers do not continuously re-decide; they act when evidence has built up that they must |

## What it is not

- It is **not learned from data**: no training set, no fitted network. Thirteen parameters
  were hand-tuned [Paper]; the rest is structure.
- It is **not an optimal controller**: bounded planning, noisy perception, and normative
  trust are all deliberate departures.
- The other vehicle is **not intelligent**: it follows a script and never reacts to our
  driver (chapter 06). There is no negotiation or interaction in the published model.
- It is **not fast**: one simulated timestep costs roughly 18 s of CPU in our environment;
  the code is written for GPU. Everything in this project's comfort-zone method avoids
  running the loop for that reason (chapter 11).

---

## Notes for the mathematically curious

**Level 1 — the loop as equations in words.** Perception: particle weights are multiplied
by the likelihood of the new observation under each particle, then normalized; particles
are refreshed by resampling when weights degenerate. Prediction: particles are pushed
through the bicycle dynamics with control noise on the other agent, reweighted by
norm-compliance (chapter 06, Level 2). Planning: cross-entropy method over control
sequences — sample, score by expected free energy, keep the elite fraction, refit the
sampling distribution, iterate. Acting: execute the first control of the incumbent plan.

**Level 2 — sizes and references.** Δt = 0.2 s; horizon H = 30 (6 s); particles N = 75;
CEM: 100 candidate plans, elite fraction 0.1, ~10 iterations; looming threshold
0.00215 s⁻¹; evidence accumulation E(t) = E(t−1) + λ·ε(t), re-plan at E ≥ 1 (Paper
Eq. 13). Observation model and looming transform: SI §2.2; belief update §2.3; preference
terms §2.4 Eqs. 44–52; planner §2.5 [SI]. Parameter values as shipped: the OSF deposit's
`Setups_*.xlsx` (65 columns per run) [OSF]. Our independent NumPy re-implementation of
components 3–7 is `src/aidriver/` — faithful to the SI for preferences, not yet trusted
for closed-loop response timing (`notes/05_validation.md`).
