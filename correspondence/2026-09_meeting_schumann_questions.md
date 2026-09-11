# Questions for Julian Schumann, conference meeting, September 2026

*Private preparation for Jonas; not to be handed over. The paper handout for Julian is
`docs/handout_schumann_2026-09.md` (PDF beside it); its section 6 carries eight of these
questions in collegial form, marked [H1]–[H8] below. Everything else here is for asking
verbally. It draws on the authors' reply of 2026-09-11
(`correspondence/2026-09-11_authors_reply_to_method_review.md`), which was written by
Julian's co-author on behalf of both.*

## If there are only fifteen minutes

1. **The road departures — his reading.** The co-author's letter said our interpretation was
   one-sided and offered to explain at the conference. Asking first, and listening, is
   probably the best way to open.
2. **Comfort or collision?** Was the safety-margin counterfactual meant to describe comfort at
   all? [H1]
3. **Where a driver trait would live in the model.** [H3]
4. **The gate from inside the model** — the norm tournament's collapse of trust as the onset. [H5]
5. **Interest in a joint look at cut-in data.** [H8]

## Opening

- Thank him for the reply and for the correction he is preparing. The letter came from his
  co-author; he may not have seen its exact wording, so the safest reference is to the
  substance ("we heard that the issues were reporting or undiscussed simplifications, and
  that our reading of the road departures was one-sided").
- The handout can be given at the start; it sets out what we did so the conversation can go
  to the open issues.

## Follow-ups to our review and his reply (verbal only)

a. **Road departures at 25 m/s.** Our reading is in `docs/method_review.md` §4.1 (closing
   sentence marked opinion) and the authors' edition, chapter 05. What is the other side:
   intended behavior, a known limitation of the lane-change control at speed, or something
   in how departures are classified?

b. **The mislabeled scenario in a figure caption.** Does it account for the Fig. 3 worked
   example not matching the deposit, and for the Fig. 3b explanation reading reversed
   (`method_review.md` §4.3)? That is our guess, not something they said.

c. **The correction.** Timeline, and what it covers, so that we can add dated notes to our
   documents when it is out (the list is in the filed reply).

d. **Which is "the model" where the code and the SI differ?** For example the one-sided
   inverse-tau term, the total-acceleration control-effort term, and the off-road cost of
   −15 000 against the SI's −5 000 (`method_review.md` §5). The reply calls the SI issues
   typos, which suggests the code is the reference; worth confirming, since our mirror
   follows the code.

e. **The accumulator's starting point** is, in their words, a simplification. What would he
   use for continuous driving? [H7]

f. **Perception noise above the looming threshold** is about 10⁻⁵ in the released
   configuration, which makes perception effectively exact once the threshold is crossed
   (`method_review.md` §6.3). Deliberate? [H6]

## Comfort-zone boundaries

1. **Comfort or collision** [H1]. *Why we ask:* our pre-registered test ruled the deficit out as
   a comfort measure on the second cut-in study, and about half of that loss is the worst-case
   counterfactual (`docs/r2_pipeline_review.md` §3.2–3.3). If the term was only ever meant for
   collision avoidance, the result is not a criticism of it, and a comfort reference is a
   separate construction.
2. **The inverse-tau preference** [H2]: mean 0.2 s⁻¹ and sd 0.125 s⁻¹; in the code the sd is
   derived from the collision cost, 0.25 / (log₁₀(10 000) − 2). Where do the values come from?
   Neither is among the paper's listed parameters (`method_review.md` §6.1).
3. **Where a stable trait lives** [H3]. We find one per-driver level shared across four
   scenarios at about 69% of the reliability ceiling (`out/cross_scenario_consistency.md`),
   and fitted cut-in and left-turn levels agree at +0.65 (`out/driver_levels.md`). Which
   parameter would he map that onto: t_react, the assumed worst-case braking, λ, a tolerance?
4. **Calibrating the assumed worst-case braking.** The free-following table covers steady
   headways only up to about 1.0–2.1 s depending on speed (`method_review.md` §6.2). Would
   naturalistic following headways be the natural calibration source?
5. **Looming as the cue.** Our video data prefer the expansion rate; Xue et al. (2018) found
   inverse tau better for brake onsets in a simulator. Does he have a view on which, and on
   accumulating looming rather than a threshold on it?
6. **Surprise as the onset** [H5]. `docs/surprise_without_the_field.md` argues that world
   surprise could define when a situation starts to count. His norm tournament already
   computes a version of that (the candidate-independent "now" weight collapsing). Would he
   use it that way?

## Cut-in

1. **Norms for a vehicle partway into the lane** [H4]: a progress-dependent norm, since a lane
   change is legitimate but only for a plausible duration.
2. **The binary lateral tests** (3 widths for perception, 1.15 for the preference terms). Did
   they try a graded version, and does the oncoming incursion avoid the issue only because it
   crosses quickly?
3. **The steering-noise dial.** `w_sd_model` is 0.0045 in the rear-end scenario and 0.4575 in
   the two lateral ones, a factor of 100 (`method_review.md` §5 item 4, §9 question 4). Is the
   rear-end value intentional, and would he start a cut-in from the lateral value?
4. **Their own plans or data.** Do they (TU Delft, Waymo) have human cut-in response data, or a
   cut-in scenario planned? Would a cut-in make a sensible second held-out test?
5. **Running the loop.** What does a scenario cost them on GPU, and is there a faster
   implementation? [H8]

## Crash causation

1. **Beliefs coasting through a glance** [H6]. Intended? And why the planner's hard-coded
   "avoid off gaze" in this paper: only to isolate avoidance behavior?
2. **Glance choice by epistemic value.** Is the machinery from Engström et al. (2024) ready to
   switch on (`road_gaze_preference` ≠ 0) in this code base, or would he advise against it?
3. **The accumulation rate.** λ = 10^−5.95 in the released rear-end setup. Which human data set
   it? Our onsets came out slower and more variable than the fixed-delay rule (median 1.25 s
   against 0.50 s after the anchor); does that match his expectation?
4. **The pointwise surrogate** [H8]. Our open-loop approximation matched the closed loop to a
   median 0.55 s over 23 scenarios. Would he accept it for population-scale studies?
5. **Reactive other agents.** Any plans for other road users that respond to the driver?

## What we could offer

- The surprise-measure library, the NumPy mirror of the preference terms (following the code),
  and the OSF validation harness.
- A joint analysis of the cut-in data, if the data owners agree; the two video studies come
  from a related project and are not ours to share.

## Worth avoiding

- Re-arguing the review. The numbers are not in dispute and the interpretation is what they
  offered to discuss; the aim is to hear it.
