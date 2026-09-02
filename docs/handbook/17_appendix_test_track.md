# Chapter 17 (appendix): the test-track anchor — the video paradigm against real turns

*Part of the WaymoActiveInference handbook. Added 2026-09-02 ({{R6}} round). **Early
results, one scenario, one evening's analysis.** Everything in the measurement program so
far rests on drivers judging video clips. This appendix reports the first comparison with
real driving: Jonas's 2013 test-track study of left turns across the path of an oncoming
balloon car (Bärgman, Smith & Werneke, 2015; the paper and its run protocol are described in
`notes/06_bargman2015_ltapod_testtrack.md` and `external/README.md`), fitted with the same
model the project fits to the video LTAP study. Every number comes from
`replication/czb/out/ltapod_testtrack.md` (script `replication/czb/ltapod_testtrack.py`, tests
pre-stated in its docstring). The dread-zone (hurried) condition is parked by Jonas's
decision: the manipulated PET is not what a hurried driver faced, since they accelerated, and
the project's PET convention is the manipulated one.*

## 17.1 The two studies

{{R6}}**The test track (2013).** Twenty-six participants drove an instrumented car toward a
T-junction, were released to full control about 20 m before it, and decided to turn left
before or after a balloon car approaching at a constant 50 km/h. The manipulated variable
is SetPET, the post-encroachment time a reference trajectory would produce; four preset
values, then a staircase that brackets each driver's Go / No-Go switch. Comfort condition:
218 usable runs (112 Go), after removing training runs and the 13 runs the experimenters
repeated.

{{R6}}**The video study (study 1, Random design).** Forty-three participants judged frozen
video clips of the same manoeuvre at nine design PET levels and two oncoming speeds, 172
trials per cell, answering whether they would intervene (brake or yield). Only the 50 km/h
cells are used here, 1 548 trials.

{{R6}}**The mapping** assumed throughout: a Go on the track is the same decision as *not*
intervening on video (query TT.Q1 asks Jonas to confirm). Both are read against the design
PET: SetPET on the track, the clip's PET on video.

## 17.2 The same model on both

{{R6}}The model is the project's stage-1 estimator without a gate: each driver has a level
c_i on the PET axis, the levels are drawn from a population with a median and a spread, and
a driver's probability of intervening (track: of *not* going) is a lapse plus a cumulative
normal of the distance from their level. Fitted by the same code on both datasets.

| | test track (real turns) | video (50 km/h clips) |
|---|---|---|
| drivers, trials | 26, 218 | 43, 1 548 |
| median comfort boundary, PET | **2.45 s** (SE 0.04) | **2.18 s** (SE 0.20) |
| between-driver spread of levels | 0.89 s | 1.36 s |
| within-driver spread (how sharply one driver switches) | 0.20 s | 0.86 s |
| lapse | 0.000 | 0.016 |
| the paper's own boundary (observed PET at the last comfortable Go) | 2.17 s here; 2.26 s in the paper | — |

{{R6}}**The boundary.** Video minus track is −0.27 s (SE 0.20), inside the 0.5 s resolution
the video design has and the pre-stated test used: on this scenario **the video paradigm
reproduces the real comfort boundary**, with the clip judgments slightly bolder. The
sensitivity runs move the track's number by at most 0.25 s (2.20 s with the repeated runs
included; 2.44 s without the negative SetPETs). The paper's own statistic reproduces from the
protocol (2.17 s against the published 2.26 s; the hurried boundary 1.49 against 1.50; the
ratio 0.68 against 0.69), so the data are the paper's data.

{{R6}}**Sharpness is the real difference.** A driver who has to turn switches from Go to
No-Go within about 0.2 s of PET; a viewer judging a frozen clip is four times less certain.
The spread of levels across drivers is also smaller on the track. The way I read it, the
video measures the same boundary with more noise per judgment, not a different boundary.

## 17.3 Does the video model carry over to the track?

{{R6}}The video-fitted population, applied to the track's Go / No-Go cells with nothing
refitted, scores a weighted RMSE of 0.200 against chance 0.289 and against the track's own
population fit 0.231; the track's cells have a sampling-noise floor of 0.108 because
many SetPET levels hold only one to five runs. Under the pre-stated margins the video model
**carries over**. It even scores better than the track's own population curve on those
noisy cells, which says less about the video than about the cells: a curve fitted to
trial-level likelihood with a 0.2 s within-driver spread is sharper than a handful of runs
per SetPET can reward. The reverse transfer, track to video, scores 0.149 against the
video's own 0.039 and chance 0.223: the track's sharp curve is too sharp for clip judgments.

## 17.4 How the track model performs on its own terms

{{R6}}Held out one driver at a time (13 drivers, 109 runs), the model's log-likelihood is
−54.3 against −75.9 for predicting the training mean: +0.20 per held-out run, a driver the
model never saw predicted better than chance from the population alone. The per-driver level
the estimator returns correlates at r = 1.00 with the model-free bracket midpoint the
staircase gives directly, and at only r = 0.38 with the paper's observed PET at the last Go
(over 22 drivers). The second number is the more interesting one: the level is a
*decision* quantity, read off the manipulated PET, whereas the observed PET also carries how
the driver then executed the turn (on comfortable Go runs they turned about half a second
more slowly than the reference), so the two measure different things. On the track the
estimator adds little over the staircase, because the staircase already brackets each
driver to 0.2 s; its value is on video, where one driver's judgments spread over 0.9 s and
the hierarchy is what makes a per-driver level estimable at all.

## 17.5 The graded signal

{{R6}}After every run drivers rated how comfortable the turn was (or would have been); after
every clip video participants rated perceived safety. Z-scored within dataset and regressed
on PET with driver-clustered errors, the two slopes are −0.31 and −0.40 per second and their
intervals overlap. On the track this holds only when *every* run is rated: on Go runs alone
the rating is flat against PET, because a driver who chose to go had already judged the turn
acceptable. That selection effect is worth remembering wherever a rating is collected only
after an action.

## 17.6 What this does and does not establish

{{R6}}**Established, on one scenario.** The level-on-an-axis construction transfers from video
to real turns without a change of form; the video's boundary is within a quarter of a second
of the real one; the graded rating behaves the same way. The methods are worth keeping.

{{R6}}**Not tested here.** The *axis* question (the track has one oncoming speed, so time,
distance and looming are one variable) and the *gate* (the decision moment is fixed by the
approach script). Both remain video-only findings. The dread boundary is parked (query
TT.Q2). The two populations differ (Volvo and Autoliv employees in 2013 against crowdsourced
participants in 2026), the paper reports 22 usable drivers where the protocol holds 26
(TT.Q3), and the balloon car is not a car. One scenario is one scenario; the cut-in, where
the axis question was decided, has no real-driving counterpart yet.
