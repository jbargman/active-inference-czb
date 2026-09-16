# Meeting Julian Schumann, September 2026: your questions, with notes

*Private preparation for Jonas; not to be handed over. Revised 2026-09-13 after the overnight
work on your questions of 2026-09-12. The paper handout for Julian is
`docs/handout_schumann_2026-09.md` (PDF beside it); its section 6 carries the main questions in
collegial form, marked [H1]–[H10] below. The one-sheet norm proposal
`docs/cutin_norm_proposal.md` (PDF beside it) can be given if the cut-in comes up. This file draws
on the authors' reply of 2026-09-11 (`correspondence/2026-09-11_authors_reply_to_method_review.md`),
written by Julian's co-author on behalf of both.*

*How each item is laid out: **Ask** is what to say. **Plain words** is what it is about. **Why it
matters** is what it changes for us. **Listen for** is how he might answer, and what to follow up
with. Every number is from a tracked output in the repository; the file is named where it helps.*

## 0 Before the meeting: what the last few days change for our own thinking

Your question was whether what we now know changes our thinking about CZB thresholds or the
modeling. As I read the results, in six ways. All are fresh and not yet reviewed by you.

1. **The comfort boundary sits above where emergency braking begins, on the same variable.** On
   the second cut-in study, the share of raters who would intervene passes 50% at a looming rate of
   0.034 rad/s, or an inverse tau of 0.33 s⁻¹. That is 1.6–1.7 times the level at which Farewell's
   drivers began emergency braking (0.02 rad/s, 0.2 s⁻¹). Fixed at Farewell's values, both fits
   get clearly worse (`replication/czb/out/pt1_farewell_thresholds.md`). Farewell's level sits
   near the *quarter point* of our comfort curve: about a quarter of raters would already
   intervene where naturalistic emergency braking typically begins. For thresholds, as I read it,
   the percentile we choose decides whether a CZB-based trigger comes before or after typical
   emergency braking; the crossover is somewhere near the 25th percentile. The caveat is real:
   a judgment on frozen video against an executed brake, so the comparison is of shape.
2. **The model already has a natural home for our driver level.** Its closing-rate preference is
   centered on Farewell's emergency level. A per-driver center for that preference, on inverse tau
   or on the looming rate, would express our one-level-per-driver trait as a single interpretable
   model parameter. This is worth putting to Julian directly (A3, A6).
3. **What starts the response looks like anticipated conflict, not surprise.** Your scope is
   right: surprise about the other road user alone sees nothing in the cyclist overtake or the
   left turn, so whatever starts the response has to include the ego. But surprise in the plain
   sense — the situation departing from steady motion — comes *after* participants respond in two
   scenarios of three, and on the cut-in a step at the maneuver onset does worse than our
   anticipatory gate (`out/hs1_situational_surprise.md`). What seems to start it is the *predicted*
   encroachment — our 3 s projected-clearance gate — or the approach to a known conflict. The next
   card I would propose is a scenario-agnostic projected-conflict gate: the ego's path against the
   other road user's predicted path, on all four scenarios. That would give one gate without
   per-scenario geometry, which is what you have been after.
4. **On these judgments, a state threshold beats accumulation.** Accumulating looming from the
   onset fitted clearly worse than a threshold on the looming rate at the clip end (0.196 against
   0.144). Accumulation may still matter for *executed* responses, as in Farewell; these frozen-clip
   judgments behave like judgments of a state. Only one accumulator form was tried.
5. **The model's norms may already contain our gate.** A positional norm withdraws trust later for
   slower lane changes, which is exactly what the data say drivers do not do. With a norm that keeps
   an ordinary lane change "normal", the model's own four-second held-control projection would do
   the anticipating — a close relative of our fitted gate (`out/pn1_cutin_norm.md`,
   `docs/cutin_norm_proposal.md`). If Julian agrees, our gate could be described as the empirical
   counterpart of that projection.
6. **The released model does not hold sustained following, and its glances cannot yet be fitted.**
   Switching gaze choice on is one line. The probe then found something bigger: with nothing
   happening, the released configuration starts braking after 3.2 s (1.5 s headway) or 4.6 s (2.0 s),
   often to a standstill, with gaze choice on or off and with the authors' own scripted lead; with
   100× perception noise it follows steadily (`replication/causation/gz1/`). For our work this matters
   wherever a run-in is long — naturalistic data above all. On glances: a near-blind glance was chosen
   as readily as a mild one (consistent with a glance costing almost no information at released noise),
   and every glance lasted one 0.2 s step because looking back is instantaneous in the code. So fitting
   to SHRP2 is a design task before it is a fitting task (D2).
   **Why it brakes (card GZ.2, 2026-09-16, `replication/causation/gz2/`).** Not a mystery any more:
   the evidence accumulator re-plans by itself at about 2.6 s, fed entirely by imagined collisions and
   failed safety checks (68 090 per step, the same value our method review read from their deposit),
   and the new plan buys safety margin by braking. The inverse-tau preference and epistemic value play no
   part. Noise on the car's *state* channels (not the looming channels) slows the accumulation 30-fold
   and prevents it. For us this is the most useful single result of the week: the same shortfall our
   comfort-zone field was built on makes the released model unstable in plain following.

## 1 If there are only fifteen minutes

1. **The road departures — his reading.** His co-author said our interpretation was one-sided and
   offered to explain. Asking first, and listening, is probably the best way to open.
2. **Comfort or collision** (A2).
3. **Where a driver trait would live** (A6), with the inverse-tau preference as the concrete
   candidate (A3).
4. **The norm for a car changing into our lane** (B1), handing over the proposal sheet.
5. **Perception noise and the glance multiplier** (A4), which he may not know about.

## 2 Opening

- Thank him for the reply and for the correction he is preparing. The letter came from his
  co-author, and he may not have seen its exact wording, so the safest reference is to its
  substance: the issues were reporting errors or undiscussed simplifications, and our reading of
  the road departures was one-sided.
- Give the handout at the start; it covers what we did, so the conversation can go to the
  questions.

## 3 The published model

**A1 Road departures at 25 m/s** (verbal only)
- **Ask:** "Your co-author mentioned our reading of the road departures was one-sided. What is the
  other side?"
- **Plain words:** at 25 m/s, over half of the deposited runs end off the road, mostly to the left
  and during the avoidance maneuver, even at a 3.5 s gap where braking would do. We read that as a
  quirk of lane-change control at speed.
- **Why it matters:** only for how we describe it. It is marked as opinion in our review
  (`docs/method_review.md` §4.1) and in chapter 05 of the authors' edition.
- **Listen for:** "intended: leaving the road is a legitimate escape" (then ask whether human data
  support it at that speed); "a limitation of the lateral control" (then ask whether the correction
  will mention it); "a classification issue" (then ask which runs count as departures in Fig. 3c).

**A2 Comfort or collision** [H1]
- **Ask:** "Was the safety-margin term meant to capture what drivers find comfortable, or only what
  avoids a collision?"
- **Plain words:** the term asks *if the lead braked as hard as it plausibly could and I reacted
  after a second, could I still stop?* That is a collision question. At 110–130 km/h the answer is
  no in almost every clip, so the term ends up ranking clips by speed, while people rank them by
  distance.
- **Why it matters:** if collision only, our negative result is a misuse, not a criticism, and a
  comfort reference is separate work. If comfort was intended too, our result bears on it.
- **Listen for:** "collision only" (follow up: would he see comfort as a different preference, or a
  different level of the same one?); "both" (follow up: how would he square that with the speed
  ordering?).

**A3 The inverse-tau preference** [H2]
- **Ask:** "The closing-rate preference takes its center from Markkula et al. (2016), where
  emergency braking begins. Did you intend it as a comfort standard? And where does the spread of
  0.125 s⁻¹ come from?"
- **Plain words:** the model dislikes closing faster than an inverse tau of 0.2 s⁻¹. The SI says
  that value comes from Farewell, which is about emergency brake onsets. As a preference it acts
  more like "how fast is it comfortable to close". The spread has no stated source; in the code it
  is derived from the collision cost.
- **Why it matters:** if it is meant as comfort, it is the model's own comfort-zone parameter, and
  our data put the comfort 50% point at 0.33 s⁻¹. Do not frame that as "your value is wrong";
  frame it as two levels of one variable.
- **Listen for:** "we just needed a sensible TTC preference" (follow up: would a per-driver center
  be natural?); "it is comfort-like on purpose" (follow up: our comfort curve crosses 25% near
  0.19 s⁻¹ and 50% near 0.33 s⁻¹ — does that fit his intuition?).
- **Talking point, only if it helps:** our video cut-in level has a population median of
  0.032 rad/s on the looming rate, the same variable as Farewell's 0.02 rad/s cut-off.

**A4 Perception noise, and the glance multiplier** [H3]
- **Ask:** "Above the looming threshold the observation noise is 0.001 × 0.01 = 10⁻⁵. Was the
  0.01 factor deliberate? And the gaze multiplier of 3 is applied before the threshold override —
  was that the intended order?"
- **Plain words:** the model sees the angle of the car ahead and its growth rate. Below the
  detection threshold the observed growth is set to zero with a spread of 0.0043 rad/s. Above it
  the spread drops to 10⁻⁵, 430 times smaller, which makes perception essentially exact: closing at
  5 m/s, the threshold is crossed at 63 m and the driver then knows the distance to about ±2 cm.
  Looking away multiplies the noise by 3, but *before* the threshold rule, so below threshold a
  glance changes nothing and above it 10⁻⁵ becomes 3×10⁻⁵ — still tiny.
- **Why it matters:** with near-exact perception a glance costs almost no information, so there is
  little reason for a driver to look back. For crash causation with glances, that is the central
  mechanism. It likely also explains why response times barely vary within a condition.
- **Listen for:** "0.01 was tuned to match response times" (follow up: would larger noise break
  the fit?); "an oversight" (follow up: does the correction cover it?); "the order does not matter
  in the published runs" (agree — gaze was switched off — but it matters as soon as gaze is on).
- **Our probe, if relevant:** see D2.

**A5 A graded perception switch** [H4]
- **Ask:** "The looming detection threshold and the lateral applicability tests are on/off
  switches. Did you consider graded versions? And would you keep Farewell's 0.2 out of perception?"
- **Plain words:** two switches. One decides whether growth of the car ahead is visible at all
  (0.00215 rad/s). The other decides whether a car counts as in our path (within 3 widths for
  perception, 1.15 widths for the preferences). Both jump from nothing to everything.
- **Your question from last night, answered as I read it:** a smooth 0–1 transition is clearly
  more realistic for both. But centring perception on Farewell's 0.2 would conflate two things:
  0.00215 rad/s is where growth becomes *visible*, while Farewell's level (about 0.02 rad/s, ten
  times higher) is where drivers *respond*. Put 0.2 into perception and the model would be blind
  until it should already be braking, and accumulation would then add a second delay. Farewell's
  own reading is a transition from slow to fast accumulation, so the natural place for a smooth
  0.2 transition is the accumulation gain (or the preference, where it already is). A psychometric
  detection function belongs at the detection level. Our video data cannot test the switch itself
  (every clip is far above 0.00215 rad/s); what they can test is in A3.
- **Listen for:** "binary for simplicity" (follow up: would a graded detection reintroduce
  response-time variability?); "we tried graded detection" (follow up: what did it do?).

**A6 Where a stable driver trait would live** [H5]
- **Ask:** "We find one comfort level per driver shared across scenarios. Which parameter would you
  make per-driver?"
- **Plain words:** each driver's propensity to intervene correlates at +0.50 to +0.74 across the
  four scenarios, about 69% of the correlation the data's reliability allows. The **reliability
  ceiling** is the highest correlation two noisy measures of *the same* trait could reach
  (√(reliability₁ × reliability₂)); ours is close to 1 because each scenario measures drivers very
  consistently (split-half 0.93–0.98), so 69% of it is a strong result, and the remaining 31% is
  genuinely scenario-specific rather than noise.
- **Why it matters:** if he names a parameter, the trait becomes a model quantity rather than a
  curve fit.
- **Listen for:** t_react, the assumed worst-case braking, the accumulation rate λ, or a preference
  center. Follow up with A3's per-driver inverse-tau center, and with Farewell's point that
  responsiveness to looming depends on expectancy, style, drowsiness and visibility.

## 4 The cut-in

**B1 A norm for a car changing into our lane** [H6] — the proposal sheet
- **Ask:** "How would you write the norm for a vehicle that is legitimately partway into our lane?
  Here is what we would propose."
- **Plain words:** the model's predictions give more weight to futures where the other car behaves
  normally. The released norms are about position only. A car crossing the lane line is
  immediately "abnormal", so trust is withdrawn at every legal lane change — and later for a slow
  lane change than a fast one (+0.53, +0.73, +0.93 s after the change registers, for 2, 3, 4 s
  changes). The proposal: straddling the line is normal *while crossing* at a plausible lateral
  speed (0.5–3.0 m/s toward our lane); stalling, drifting back or swerving are not. It needs only
  the particle state the model already carries.
- **Why it matters:** with it, the model's own four-second projection would anticipate the car
  arriving in our lane, which is close to what our human data asked for.
- **Listen for:** "lateral speed is fine" (follow up: would he test it in the loop, or would we?);
  "intention inference is better" (follow up: is that a larger change to the belief machinery?);
  "a lane change into your lane should stay somewhat abnormal" (follow up: then how does he avoid
  the pace-dependent withdrawal?).

**B2 The steering-noise dial** (verbal)
- **Ask:** "The assumed steering variability of the other car is 0.0045 in the rear-end scenario and
  0.4575 in the other two. Is the rear-end value intentional, and would you start a cut-in from
  0.4575?"
- **Plain words:** when imagining the future, the model adds random variation to the other car's
  steering. The rear-end code has an extra factor 0.01, so that driver assumes the car ahead never
  steers — harmless for a braking lead, blinding for a cut-in. Our review asked this; the reply did
  not address it.
- **Listen for:** "a lead in a queue does not steer, so 0.01 is deliberate" (reasonable; then ask
  whether the paper will say so); "a leftover" (then ask whether the correction covers it).

**B3 The binary lateral tests** [H7]
- **Ask:** "The collision and safety terms apply only within 1.15 vehicle widths. Did you consider
  weighting them by lateral overlap?"
- **Plain words:** with the other car's center 1.99 m to the side, the safety term is completely
  off; at 1.97 m it is completely on. In the published scenarios nothing sits near that boundary
  for long; a cut-in straddles it for about 2.5 s. We built a graded version, and it helped, but
  our first projection (to the moment the gap closes) caused 44% of the deficit's loss; a fixed 3 s
  projection removed that share.

**B4 Their data and plans** [H10] (verbal)
- **Ask:** "Do you, or Waymo, have human cut-in response data, or a cut-in scenario planned? Would a
  joint look make sense?"
- **Note:** the two video studies come from a related project and are not ours to share.

## 5 When a situation starts to count

**C1 The onset from inside the model** [H8]
- **Ask:** "When the norm tournament's 'now' weight collapses, the model effectively stops trusting
  the other car. Did you look at that moment as a response onset? We tested surprise as an onset,
  and it came too late."
- **Plain words:** our comfort model has a *gate* — whether the other car counts yet — separate from
  how critical the situation is. We tried to replace our fitted gate with surprise, taken both about
  the other car alone and about the whole situation including the automated ego. On the cut-in,
  surprise registers the lane change 0.08–0.17 s after it starts and keeps all pre-onset clips
  closed, but a step at that moment fits worse than our anticipatory gate (0.145 against 0.103).
  On the cyclist overtake, surprise about the cyclist never registers (it rides steadily), and
  whole-situation surprise registers the ego's pull-out 0.7–1.1 s after it starts, while 17–58% of
  raters already intervene. On the left turn nothing registers before the clips end, yet 11–91%
  intervene.
- **Why it matters:** it suggests that what starts a response is *anticipation* of a conflict, not
  surprise. If the model's own projection does that, the onset could come from the model.
- **Listen for:** "surprise is for the unexpected; anticipation is planning" (agree; follow up: is
  the four-second held projection the model's anticipation?); "the accumulator is the onset" (follow
  up: our judgments fit a state threshold better than accumulated looming — does he expect
  accumulation to matter only for executed responses?).
- **Worth being careful about:** these are fresh and unreviewed; the surprise predictor is the
  simplest possible one (constant velocity). Say "our first attempt", not "surprise fails".

## 6 Crash causation and glances

**D1 Beliefs coasting through a glance** [H9]
- **Ask:** "When we forced glances away, a driver who had registered the braking kept responding
  during the glance. Is that coasting intended?"
- **Plain words:** looking away blocks new observations, but the belief keeps moving forward on its
  own prediction and the accumulator keeps filling, so the response continues. The fixed-delay
  crash model assumes the opposite.
- **Listen for:** "yes, that is the point of a generative model" (follow up: would the 2024 paper's
  glance machinery produce the same?).

**D2 Could the model choose its own glances, fitted to real glance data?** [H9]
- **Your question from last night:** could we switch off the hard-coded "always look at the road"
  and fit the gaze parameters to the SHRP2 glance distribution from our crash-causation work?
- **What we found:** the planner's override is one line and can be lifted without editing their
  files. Four things came out of nine 15 s runs (`replication/causation/gz1/`, both reports):
  1. *Sustained following is unstable in the released configuration.* With nothing happening, the car
     starts braking at the same moment in every released-noise run — 3.2 s at a 1.5 s headway, 4.6 s at
     2.0 s — with gaze choice on or off, and with the authors' own scripted lead instead of our replay;
     1–3 of 4 repeats stop. With 100× perception noise it follows steadily. Our review predicted the
     re-plan (§4.2). *The cause, found 2026-09-16 (GZ.2):* one evidence-triggered re-plan at step 13,
     fed only by imagined collisions and safety failures; the new plan brakes to buy margin. Noise on the
     state channels, not the looming channels, prevents it. Which state channel is not yet known.
  2. *With realistic noise the model never looks away.* Nothing in it gives a reason to — there is no
     competing task — and looking away now costs information.
  3. *At released noise a near-blind glance is chosen as readily as a mild one* (15.0% against 15.7%).
     That fits the ×3-before-threshold point in A4: a glance costs almost nothing. These shares come
     from braking runs, so they are not read as glance behavior.
  4. *Glances never last.* Every glance was one 0.2 s step, against a SHRP2 median of 0.75 s. In the
     code, choosing "attentive" returns the eyes to the road with probability 1 in one step.
- **Plain words on your question:** not as it stands. The model is not trained, so "fitting" means
  searching road_pref, the off-road multiplier, the noise and a look-back rate by simulation against the
  SHRP2 share and durations. Before that is meaningful it needs a stable following regime, a reason to
  look away, a cost that depends on perception noise, and a way for glances to last. Then it is days of
  CPU per grid.
- **Ask:** "Is sustained following something you have looked at? When we let the planner choose, the
  released configuration braked after a few seconds with nothing happening. And how would you give the
  model a reason to look away, and a reason to stay away?"
- **Listen for:** "the rear-end runs never needed it" (follow up: would the 2024 paper's configuration
  hold it?); "the accumulator's starting point" (follow up: it re-plans by itself — is braking the
  intended outcome of that re-plan? and if the perception noise was tuned, was steady following part of
  what it was tuned against?); "a secondary task is the motive" (follow up: is that in any
  released code?). Be careful to present point 1 as something we saw in a quick probe, not a flaw.

**D3 Continuous driving** (verbal)
- **Ask:** "For naturalistic data, where nothing marks the start of an event, what starting point
  for the accumulator would you use?"
- **Plain words:** the published runs start the accumulator at zero 0.6 s before the lead brakes.
  In ordinary following it drifts upward and would re-plan by itself after 2–7 s at gaps of 2 s or
  less.

**D4 Practicalities** [H10]
- **Ask:** "Is evaluating the preference pointwise on recorded kinematics a fair approximation, and
  is there a faster implementation?"
- **Plain words:** a full scenario takes minutes to hours on our CPU; our cheap surrogate matched
  the closed loop's brake onsets to a median of 0.55 s over 23 scenarios.

## 7 What we could offer

- The surprise library (now with situational surprise), the NumPy mirror of the preference terms,
  the OSF validation harness, and the norm functions.
- A joint analysis of cut-in data, if the data owners agree.

## 8 Worth avoiding

- Re-arguing the review. The numbers are not in dispute; the interpretation is what they offered to
  discuss.
- Presenting the overnight results as settled. They are one night old.
