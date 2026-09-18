# What the rest of the Waymo active-inference program already solved, and what we missed

*2026-09-18, on Jonas's instruction: "revisit the other Waymo relevant papers and consider if there
is something we missed in our way of thinking so that what we want fits into what they have done."*

**Status: a review note, not a card. Nothing here is authorized.** Every claim carries its source.
Opinions are marked. Sources are the extracted paper texts in `notes/paper_text/`, the summaries in
`notes/01_paper_summaries.md`, the deposit-derived numbers in `replication/osf/review/`, and this
project's own cards.

---

## 0 The short version

The program has **three strands**, and the IWAI 2024 poster by Engström et al. lays them out:
managing uncertainty; responding to urgent conflicts; social interaction. This project took the
model from strand 2 — Schumann et al.'s collision-avoidance model — and used it to measure the
**comfort zone**, which the program itself locates in strand 1. `notes/01_paper_summaries.md` says
so in its own words about the strand-1 scenarios: *"Both are non-critical scenarios — the
comfort-zone regime, not the collision-avoidance regime."* That sentence has been in the repository
since 2026-08-17 and nothing since has acted on it.

Four things follow, and the third and fourth are the ones I would have wanted a month ago.

---

## 1 We used the collision-avoidance model to measure comfort

Schumann et al.'s preference function is catastrophe-dominated **by design**: collision −10 000,
road edge −15 000, the braking-margin indicator −10 000 × severity. Card RE.2 measured what that
means on our stimuli: the speed, acceleration, steering and lane factors contribute **identically
zero** under "continue" (−1.2e-14 at every one of 378 cells), so ε is the collision factor plus the
safety factor and nothing else — which is also the deposit's own result for benign following
(`docs/method_review.md` §4.2, collision/safety share 1.000).

We read that as a defect. It is better read as **the model working in the regime it was built for**.
A collision-avoidance model whose comfort terms did not vanish next to its catastrophe terms would
be a badly-built collision-avoidance model.

The strand-1 model (Engström et al. 2024, *Resolving uncertainty on the fly*, Front. Neurorobot.
18:1341750) is the one whose subject is the progress-versus-caution trade-off — slowing while
uncertain, speeding up once the uncertainty resolves, moving laterally to gain line of sight. That
is a comfort-zone model in everything but name.

---

## 2 Our stimuli cannot see the comfort-zone terms at all

This one is about our design, not their model, and it is the sharpest practical finding here.

In both video studies **the ego holds a constant speed in its own lane and never acts**. So under
the "continue" policy the ego is exactly at its desired speed, exactly at zero acceleration, exactly
at zero steering, exactly at the lane centre. The four preference factors that carry the
progress-versus-caution trade-off are therefore **structurally pinned at zero**, not small — zero to
machine precision, which is what RE.2 measured without my seeing what it meant at the time.

Whatever a comfort-zone boundary is in this framework, our stimulus set cannot express the half of
it that is about what the driver gives up. A participant watching a clip has no speed to lose, no
effort to spend and no lane to leave. *[Opinion: this is the most actionable thing in this note. It
says a future study should show the ego trading something — a speed choice, a lane choice, a gap
acceptance — rather than only judging a scene it cannot act in.]*

---

## 3 The reference distribution we said does not exist, exists — in strand 1's companion paper

Card RE.1 and the R.2 pipeline review both concluded that every surprise measure needs a reference
distribution and that the field was ours. **Dinparastdjadid, Supeene & Engström (2023), *Measuring
surprise in the wild* (arXiv 2305.07733), builds exactly that reference distribution** and does it
from naturalistic data: the belief is a **learned trajectory predictor** (MultiPath-style, Wayformer
encoder) emitting a Gaussian mixture over each agent's future position per timestep, decomposed into
lateral and longitudinal components in a body frame.

Two things in that paper bear directly on where this project now stands.

**(a) The measure we have been computing is theirs, and it is the right one.** Their *residual
information*, log(max_x' P(x')) − log P(x), is what the Nature model accumulates as evidence and is
exactly what `policy_surprise` and our `G(continue)` compute (card RE.1 §0 checked the identity to
7e-16). So the measure was never the problem. **The distribution it is computed against was.** In
the 2026 model that distribution is a hand-written, per-scenario norm weight (`reward.py` /
SI Eqs. 23–27); in the 2023 paper it is learned from data.

**(b) Their conflict definition is Jonas's two-factor hypothesis, already published.** The paper's
first named application is traffic-conflict definition conditioned on **surprise *and*
spatiotemporal proximity**, and the summary in `notes/01_paper_summaries.md` records the reason:
it cuts false positives, because *an intentional small-TTC overtake is not a conflict*. That is
Jonas's "people expect and accept a closing speed as long as it is far away", in their own program,
with the ISO/TR 21974-1 "not premeditated" requirement as its justification.

So the two-factor structure is not a new proposal to be defended. It is the program's own, and this
project has been trying to do with one scalar what they do with two — one of which needs a learned
predictor we do not have.

---

## 4 Fitting a driver's preferences from data is also solved, including the trap

The reformulation note (`docs/active_inference_reformulation.md` §3) proposes inferring each
driver's preference parameters from their responses rather than assuming the authors'. **Wei,
Garcia, McDonald, Markkula, Engström & O'Kelly (2023)** did that: internal model and preferences
both estimated from demonstrations as an inverse-RL problem under partial observability.

They also name the trap the note walked past: **non-identifiability** — many (reward, internal
model) pairs rationalize the same demonstrations. Their resolution is a structural prior: preferences
and world model independent, and the world-model parameters restricted to values with high data
log-likelihood. Their reported failure mode is ours in mirror image: the model is inaccurate in
extreme scenarios because the naturalistic dataset contains no collisions.

*[Opinion: the reformulation note should not propose a per-driver preference fit without adopting
their identifiability treatment, and should cite their failure mode as the reason the video studies'
critical cells are worth having at all.]*

---

## 5 One configuration error of our own

Design note §1.4 fixes epistemic value at **α = 0** in the primary analysis and calls that "the
authors' validated configuration". The deposit says otherwise: the epistemic component runs **+1745
to +1941 per step** in benign following, against −0.003 for the velocity preference and −2 for
control effort (`replication/osf/review/benign_eps.csv`; `docs/method_review.md` §6.4, which adds
that "in the benign regime the epistemic term can outweigh the terms that are supposed to shape
following"). The released baseline has it on; the paper's ablations are *without* it.

ε itself is α-independent — `policy_surprise` computes the pragmatic part only — so cards JJ.2,
JJ.3, RE.2 and RE.3 are unaffected. What is affected is every quantity that went through the
planner: RE.1 part C and card JJ.2b's planner pass both ran α = 0.

And the direction matters for a comfort-zone question: under looming perception a closer approach
sharpens the observation, so the epistemic term **rewards proximity**. The one term that would pull
a driver toward the boundary has been switched off throughout.

---

## 6 What this changes, in order

1. **Card 1 as agreed (σ_a from QUADRIS) survives and gains motivation.** Under strand 1 the
   uncertainty about what the other will do is not a nuisance constant — it is the engine of the
   progress-versus-caution trade-off. See §7.
2. **Card 2, the data specification, should be rewritten against strand 1**, not only against the
   norm: what we need is what a learned predictor needs, which is the 2023 paper's own recipe.
3. **The reformulation note needs three corrections**: the strand-1/strand-2 point (§1), Wei et al.'s
   identifiability treatment (§4), and the α error (§5).
4. **A future stimulus design** should let the ego trade something (§2).

---

## 7 Queries

- **WP.Q1 (judgment, jonas):** should the project re-point at the strand-1 model (Engström et al.
  2024) as the comfort-zone instrument, with Schumann et al. kept for the critical regime? That is a
  larger change than anything proposed so far and it would supersede parts of the reformulation note.
- **WP.Q2 (judgment, jonas):** §2 says our stimuli structurally pin four of the six preference
  factors at zero. Is a stimulus set in which the ego trades something worth specifying now, while
  the naturalistic request is being written?
- **WP.Q3 (minor, review):** design note §1.4's "α = 0, the authors' validated configuration" is
  contradicted by the deposit. The designing session owns that document; flag or correct?
- **WP.Q4 (judgment, review):** is the learned-predictor reference of Dinparastdjadid et al. (2023)
  something this project could build on highD/exiD when the data arrive, or does it need Waymo-scale
  data to be worth anything? The answer decides whether §3 is a route or a citation.
