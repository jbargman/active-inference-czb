# A norm for a vehicle changing into our lane: a proposal to discuss

*Jonas Bärgman, Chalmers University of Technology, September 2026, drafted with assistance
from Claude (Anthropic). A proposal for discussion with Julian Schumann, not a result. The
functions are in `src/comfortzone/norms.py` with property tests in `tests/test_norms.py`, and
the offline check on recorded lane changes is `replication/czb/pn1_cutin_norm.py`
(output `replication/czb/out/pn1_cutin_norm.md`). Nothing here has been run in the closed loop.*

## 1 The problem, as we understand it

In the released model the norms tell the driver what other road users normally do, and they
shape its predictions from the inside: every particle's next state is drawn from a small
tournament of candidate moves weighted by norm compliance now, one step ahead and four seconds
ahead under held controls, with the overall weight the lower of "now" and the future average.
While the other vehicle behaves normally, its imagined futures lean toward normal behavior;
once it is observed misbehaving, the "now" weight collapses for every candidate at once and the
imagined futures fan out. That collapse is, as we read it, the model's moment of withdrawing
trust.

The three released norm sets are positional. Rear-end: the lead's body inside our lane.
Oncoming: inside its own lane, and at its speed. Intersection: the road geometry and the light.
None was written for a vehicle that is *legitimately* partway between two lanes, and a cut-in
is exactly that for a few seconds.

- Under the rear-end norm as written, a vehicle waiting in the adjacent lane is already a gross
  violation, before any lane change begins.
- Under the oncoming form, applied to the cutting-in vehicle's own lane, trust is withdrawn when
  its body leaves that lane. On the 90 recorded lane changes of our second cut-in study this
  happens a median 0.53, 0.73 and 0.93 s after the lane change first registers, for lane changes
  lasting 2, 3 and 4 s. The moment grows with the pace of the manoeuvre.
- That pace dependence is what the human data speak against: at matched time since onset, the
  share of participants who would intervene does not depend on how fast the lane change goes.
  Used as the onset of the response in our comfort-zone model, the own-lane withdrawal moment
  scored a held-out error of 0.288, against 0.103 for the anticipatory gate we use now, and
  failed both of the criteria we had set in advance.

## 2 The proposal: a crossing norm

Keep the released structure and add one dimension, only for the straddling band:

| where the vehicle is | weight |
|---|---|
| its body inside its own lane, or inside the destination lane | 1 |
| straddling the boundary | lateral-speed compliance: 1 while crossing toward the destination lane at 0.5 to 3.0 m/s, falling off quadratically over 0.5 m/s outside that band, floored at √0.001 |
| off the road | 0.001 × 0.01, as released |

So a vehicle crossing at an ordinary pace stays normal; one that stalls on the line, drifts back,
or swerves across faster than any ordinary lane change does not.

**Why lateral speed rather than elapsed time.** Our first instinct was a "plausible duration"
for straddling. That would need a clock in the particle state, threaded through the belief
machinery. The target's state already carries position, heading and speed, so its lateral speed
v·sin θ is available to `get_weights` as it stands, and the function stays a drop-in
replacement.

**The values, and how firm they are.** The floor and the violation factors are the released
code's own. The upper bound of 3.0 m/s sits just above the fastest peak lateral speed among our
recorded lane changes, about 2.7 m/s at a 2 s duration. The lower bound of 0.5 m/s means a
3.5 m lane change slower than about 7 s counts as lingering; we have not checked that against
naturalistic lane-change durations, and it is the value we are least sure of.

**What we checked.** On the recorded lane changes, every straddling moment shown to participants
keeps a weight of 1.000 under the crossing norm, while the own-lane norm drops to 0.001 at each
of them. A caveat on coverage: the clips of the slowest lane changes end before the vehicle's
body reaches the line, so the shown straddling moments come from the 2 s and 3 s durations
only.

## 3 How it might play out inside the model

This is our reading, and the part we most want to check with you.

With the crossing norm, trust is not withdrawn during an ordinary cut-in. What would make the
driver respond is then the rest of the machinery, working on anticipation. The four-second
held-control projection carries a crossing vehicle into our lane, where it is normal again, so
the tournament leans toward futures in which the lane change *completes*. In those imagined
futures the collision and safety terms engage before the vehicle has actually arrived.

That seems close to what our human data asked for independently. Our comfort-zone gate projects
the lateral clearance 3 s ahead at its current rate and opens as the projection falls below a
minimum; fitted on clips after the lane change began, it predicted the clips before it out of
sample. The model's four-second held projection is a similar construction.

## 4 Alternatives we considered

- **A straddling clock.** Normal for a plausible duration, then abnormal. Closer to the verbal
  idea, but it needs new state in every particle.
- **Inferred intention.** Particles carry a discrete "changing lanes / keeping lane" hypothesis,
  and the norm is conditional on it. The richest option, and a larger change to the belief
  machinery.
- **No norm change, a wider lateral noise dial.** Setting the target's assumed steering
  variability to the lateral scenarios' 0.4575 lets imagined futures contain lane changes, but
  without a norm for straddling, trust would still be withdrawn at the line.

## 5 What a closed-loop test would take

A cut-in scenario whose other vehicle replays recorded trajectories, the crossing norm as its
`get_weights`, and the lateral scenarios' steering variability. The questions would be whether
trust is withdrawn during ordinary lane changes (it should not be), whether it is withdrawn when
a vehicle stalls or swerves (it should be), and whether response timing then stops depending on
lane-change pace. On our CPU-only hardware a single scenario takes minutes to hours, which is why
this has not been run.

## 6 Questions for you

1. Is the collapse of the "now" weight the right reading of "trust withdrawn", and did you look
   at it as a response onset?
2. Would you write the cut-in norm on lateral speed, on a clock, or on inferred intention?
3. Is a norm that stays normal during an ordinary lane change in the spirit of the model, or
   should a lane change into our lane always be somewhat abnormal?
4. Were the lateral scenarios' norms and the 0.4575 steering variability tuned together?
