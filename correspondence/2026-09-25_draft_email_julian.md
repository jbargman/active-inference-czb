# DRAFT — email to Julian Schumann about the naturalistic-data results

*Drafted 2026-09-25 (night) by Claude at Jonas's request ("create an email to send to Julian about
the results"). **NOT SENT.** Jonas edits and sends it himself, or not. Every number is from a
committed script with a tracked output, named in the notes after the email; the email itself keeps
file names out. Bracketed text is for Jonas to decide or fill in.*

---

**Subject:** highD results on your model's following and response-time relations — and a question

Dear Julian,

[Thank you again for the conversation at ITSC / Thank you and your co-author for the kind reply
earlier this month.] We have now got the highD and inD datasets, and I wanted to share what we see
when your released model's preferences and relations meet real motorway traffic, before any of it
goes further. All of it is preliminary and pre-registered card by card; I would value your reading,
especially where you think we have misread the model.

**1. Response time against urgency (the paper's central validation).** On about a thousand highD
lead-deceleration events, the log of the follower's response time rises with the log of the initial
time headway, and more steeply the harder the lead brakes: slopes +0.23, +0.40 and +0.45 for mild,
moderate and hard lead decelerations, against +0.59 in your deposit. So the direction holds on real
motorway data and approaches your slope as the events get more severe. The level does not: median
response times at 1–2 s headway are 2.2–3.1 s in highD against 0.8 s in the model. Our reading is
that the model's relation is an emergency relation and highD contains very few emergencies (only 32
lead decelerations of 3 m/s² or more), so by our own rule this is descriptive only. exiD or rounD
may add harder events.

**2. The calibrated following preference on real following.** On about a million highD
car-following samples, the braking-margin term of the released preference fires in 1.7% of steady
following, and the τ⁻¹ term in 0.05%. The margin's boundary headway at equal speeds (0.70 s at
40–70 km/h down to 0.05 s above 130 km/h) lies at or below the 5th percentile of real headways
(0.55–0.67 s) in four of five speed bands, far below the medians (1.3–1.7 s). In other words the
preference is silent over about 98% of real following and does not say where drivers choose to
follow — which may be exactly as intended for a collision-avoidance model, but it matters for us,
since we are trying to measure comfort boundaries with it.

**3. The released model behind real leads.** We had earlier seen, with your own scripted constant-speed lead, that the released
configuration starts braking after about 3 s of steady following at 1.5–2 s headway, and follows
steadily with more perception noise. Replaying real highD leads confirms
this: in 18 steady-following episodes (the lead's acceleration below 0.5 m/s² throughout), staged
with your `find_parameters` calibration, the model brakes by at least 1 m/s² in 56% of runs within
5 s, typically 2.5–5 s in and often hard (−6 to −7 m/s²); the human drivers in the same episodes
never did. It brakes more at 60–80 km/h than at 95–108 km/h. Is there a run-in or a setting you
use for long following that we are missing?

**4. Where the comfort zone lies relative to the model's preferences.** In our cut-in video studies
the share of people who would intervene follows the looming rate of the cutting-in vehicle, and
passes 50% at about 0.03 rad/s. On highD's real cut-ins that same curve, with nothing refitted,
predicts which followers brake gently (around 1 m/s², about the 99th percentile of deceleration at
these speeds); hard braking (2.5 m/s²) is too rare on the motorway to test. Real followers do
respond at TTC well beyond 5 s, where the released τ⁻¹ preference costs nothing. Two things
surprised us: on real cut-ins inverse TTC predicts the response slightly better than looming does,
while on video looming wins clearly; and real followers start braking for a closing car in the
adjacent lane before its lateral motion makes a cut-in likely.

**A question.** Would you see a per-driver centre of the closing-rate preference (on τ⁻¹ or on the
looming rate) as a legitimate way to express a comfort level inside your model, or does it bend the
preference away from what it was built for? That is the step our project hangs on.

[Offer: happy to share the scripts and aggregate tables; the per-sample data stay local under the
highD licence.]

Best regards,
Jonas

---

## Notes for Jonas (not part of the email)

- **2026-09-26: point 4 is display-uncorrected.** Card DT.1 (the desktop-monitor transform,
  `docs/display_transform.md`) lowers the video's looming level from about 0.03 to about 0.014
  rad/s and the matching braking from about 1 to about 0.66 m/s². Rewrite point 4 once the display
  parameters are confirmed (query DT1.Q1). Points 1–3 are unaffected (real data and the model only).

- **Sources.** Point 1: `replication/czb/out/nm3_response_time.md` (card NM.3, DESCRIPTIVE ONLY
  by its own rule). Point 2: `out/nm2_following_preference.md` (NM.2, verdict MIXED by the letter
  of the rule). Point 3: `out/nm1_replayed_following.md` (NM.1) and `replication/causation/gz1/`,
  GZ.2 (the scripted-lead braking). Point 4: NC.3, NC.3c, NC.3h, NC.3o, NC.5-tau, NC.4c in
  `out/worklog.md` entries of 2026-09-24 and 2026-09-25.
- **What is left out on purpose.** The free-energy reading of our own measurement model, the
  planner rerun (P.1: the released planner brakes and steers in nearly all of the video study's
  cells), the first study's serial-dependence problem, and the hard-boundary history. Each is
  either ours rather than his, or not settled.
- **Tone.** The authors' reply of 2026-09-11 said the earlier analysis was read "one-sidedly" in
  places. This draft states each result as what the data show against the model's intended scope,
  and point 2 says outright that silence may be by design.
- **Do not attach** `docs/handout_schumann_2026-09.docx` (never rebuilt or restaged).
- **Naming.** No colleague or company is named; keep it so if you edit.
