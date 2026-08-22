# Chapter 14: appendix — the deep end

*Part of the WaymoActiveInference handbook. Draft for comment, 2026-08-22. This appendix
exists so that the main chapters could stay out of these waters. Nothing here is needed to
use the model or the comfort-zone method; everything here is where a curious reader should
go next. It is a guide with commentary, not a tutorial — each section says what the thing
is, why the main text could skip it, and where the primary treatment lives. References
marked (verified) are ones we have read in full or checked against the source; the rest
are standard works cited by title and venue for the reader to locate.*

## A. The free-energy principle proper

**What it is.** The claim beneath the framework: any system that maintains itself against
dispersion — a cell, a brain, arguably an organism-environment loop — can be described *as
if* it minimizes variational free energy, because persisting just is keeping sensory
states within expected bounds. In its strongest form the claim is presented as close to
tautological: things that exist are things that model their environment well enough to
keep existing.

**Why the main text skipped it.** The driver model uses free energy as an engineering
objective (chapter 01, claim 3). Whether the principle is a deep truth, a useful
reformulation, or an unfalsifiable framing is irrelevant to whether the model predicts
human braking — and the debate is long.

**Where to go.** Friston, "The free-energy principle: a unified brain theory?" (Nature
Reviews Neuroscience, 2010) — the canonical statement. Friston, "A free energy principle
for a particular physics" (2019 preprint) — the strongest, most mathematical form. For
the driving-adjacent reading, the introduction of Engström et al. (2024) states exactly
how much of the principle the model line actually uses (verified — the paper is in
`papers/active-inference/` with text in `notes/paper_text/`).

## B. Variational inference, in outline

**What it is.** The mathematical engine. Exact Bayesian belief updating is intractable
for any interesting model, so one optimizes an approximation: pick a family of
manageable distributions Q, and adjust Q to minimize free energy
F = E_Q[log Q(s) − log P(o, s)], which equals the true surprise −log P(o) plus the
divergence of Q from the exact posterior. Minimizing F therefore does two jobs at once —
it scores the model and it *is* the belief update. In the driver model the "family" is
the particle set: weighting and resampling are the minimization.

**Why the main text skipped it.** The particle filter can be understood operationally
(chapter 06) without the variational story; the identity above adds rigor, not intuition.

**Where to go.** Any modern treatment of variational inference (Blei, Kucukelbir &
McAuliffe, "Variational inference: a review for statisticians", JASA 2017). For the
active-inference-specific assembly, the tutorial paper of Smith, Friston & Whyte, "A
step-by-step tutorial on active inference" (Journal of Mathematical Psychology, 2022)
(verified as the standard entry point; discrete-state, see section E).

## C. Markov blankets

**What it is.** The formal device separating "a thing" from "its environment": a set of
states (sensory + active) through which all statistical influence between inside and
outside must pass. The free-energy principle's broadest claims are stated in terms of
blankets — a system's inside models its outside *because* the blanket makes their coupling
indirect.

**Why the main text skipped it.** For a driver model, the blanket is trivial: the
observation vector in, the control vector out. The concept earns its complexity only when
one asks what counts as a system at all — a philosophy-of-science question.

**Where to go.** Kirchhoff et al., "The Markov blankets of life" (Journal of the Royal
Society Interface, 2018) for the enthusiastic case; Bruineberg et al., "The Emperor's new
Markov blankets" (Behavioral and Brain Sciences, 2022) for the sharpest critique — read
together, they are the debate in miniature.

## D. The biology and philosophy debate, with references

Chapter 01 gave the three-claim structure (process theory / universal principle /
engineering framework) and took a position only on the third. The fuller reading list,
both directions:

- **For the process theory:** Friston (2010) above; Parr, Pezzulo & Friston, *Active
  Inference: The Free Energy Principle in Mind, Brain, and Behavior* (MIT Press, 2022) —
  the book-length statement, and the best single reference if the group buys one.
- **Sympathetic but independent:** Clark, "Whatever next? Predictive brains, situated
  agents, and the future of cognitive science" (Behavioral and Brain Sciences, 2013) —
  predictive processing without commitment to the strongest principle; the natural
  companion to *Great expectations* (verified — co-authored by this project's owner).
- **The critiques:** Bruineberg et al. (2022) above on blankets; Colombo & Wright, "First
  principles in the life sciences: the free-energy principle, organicism, and mechanism"
  (Synthese, 2021) on what the principle explains; the widely cited unfalsifiability
  worry is stated crisply in commentaries accompanying Clark (2013) and the BBS treatment
  of the principle.
- **The dark-room debate** (chapter 13's FAQ): Friston, Thornton & Clark, "Free-energy
  minimization and the dark-room problem" (Frontiers in Psychology, 2012).

Our position, restated for the record: the driver model's evidential standing rests on
held-out prediction and ablation [Paper] [OSF], and would be unchanged by any outcome of
this debate.

## E. The discrete-state formulation, and pymdp

**What it is.** Most of the active-inference literature — including nearly all tutorials
— works with small discrete state spaces: a handful of states, observations, and actions,
with the generative model written as labeled probability matrices (A for observation
likelihoods, B for transitions, C for preferences, D for initial beliefs). Expected free
energy is then a sum over a few dozen entries, and everything can be inspected by hand.
`pymdp` (Heins et al., Journal of Open Source Software, 2022; verified) is the reference
Python library for exactly this.

**Why the main text skipped it.** The driving problem is continuous, high-dimensional,
and long-horizon; none of the matrix machinery transfers directly, and the Waymo/TU Delft
line had to build the particle-filter/CEM architecture *because* the tutorial formulation
does not scale to it (`notes/02_active_inference_overview.md` §6). A reader who learns
the discrete formulation first must then unlearn the expectation that A, B, C, D matrices
will appear in this codebase — they never do.

**Why it is still worth a day of someone's time.** The discrete world is where the
*concepts* — preference as probability, epistemic value as expected information gain, the
pragmatic/epistemic split — can be verified by hand on paper, which some readers find is
what finally makes them click. The pymdp tutorial notebook ("active inference from
scratch") is the recommended single exercise; its risk/ambiguity decomposition of
expected free energy is an equivalent split to the pragmatic/epistemic one used here,
and mapping one onto the other is a genuinely instructive afternoon.

## F. Where the equations of this specific model live

For the reader who wants the real thing rather than any tutorial: the Supplementary
Information of Schumann et al. (2026) is self-contained and, in our experience, more
readable than the framework literature (verified — it is in `papers/active-inference/`
with extracted text in `notes/paper_text/`). The map: §2.2 observation model and looming;
§2.3 beliefs; §2.4 preferences (Eqs. 44–52 — the part this project depends on); §2.5
planning and evidence accumulation. This project's `notes/02_active_inference_overview.md`
is the bridge document between that SI and the comfort-zone program, written at Level-2
density throughout.
