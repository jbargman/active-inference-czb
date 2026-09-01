"""Build the 15-20 minute project-group version of the active-inference / CZB talk.

    python presentation/talk/build_short_talk.py [--out presentation/talk/ai_czb_short_talk.pptx]

Audience: the project group - cognitive scientists, driver modelers, and vehicle
safety engineers. They know the datasets exist but not this workstream's detail.
The brief (Jonas, 2026-09-01): (a) the overall idea of active inference and
surprise, (b) the CZB versions we tested, (c) where we ended up and why, and
(d) what we should do now - with a short objectives slide (the objective of CZB
and why active inference/surprise looked promising) and a short summary slide of
what worked and what did not, in terms the whole group can follow.

Content is condensed from build_talk.py (the 60-minute deck); every quoted number
traces to the same tracked outputs (replication/czb/out/, docs/r2_gate_decisions.md,
docs/active_inference_scope_map.md). Figures are reused from the long talk
(rebuild with make_talk_figures.py / make_event_animation.py if analyses move)
and from docs/ai_scope_figures/.

Speaker notes carry a time budget per slide; budgets sum to about 19.8 minutes.
Two slides are marked CUTTABLE in their notes (the animation, then the R.1
timing slide) - dropping both lands the talk near 16.5 minutes.

IMPORTANT for a later session: once Jonas has reviewed or animated this deck by
hand, do NOT rerun this script onto the same file - copy the reviewed deck and
augment the copy (see the chalmers-slide-generation-jonas skill).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Cm, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_talk import (  # noqa: E402  (shared helpers and theme colours)
    BEIGE, BLUE, BODY_TOP, BODY_W, DEEPPINK, DEEPTEAL, GREY, INK, MARGIN, MUTED,
    PURPLE, SLIDE_H, SLIDE_W, TEAL, WHITE, _plain, blank, body, column,
    drop_existing_slides, ensure_template, find_figure, head, notes, panel,
    picture_fit, rule, table, text,
)


def build(out: Path) -> None:
    prs = Presentation(str(ensure_template()))
    drop_existing_slides(prs)

    # -- 1  title ----------------------------------------------------------
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H))
    _plain(bg, PURPLE)
    rule(s, 2.3, 6.6, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.5, 29.0, 5.0,
         [("Active inference for comfort-zone boundaries:", 36, WHITE, True),
          ("what we tested, what held up, and where we go next",
           36, TEAL, True, 6)], spacing=1.15)
    text(s, 2.3, 13.9, 29.0, 2.6,
         [("Jonas Bärgman  ·  Chalmers University of Technology",
           17, WHITE, False),
          ("Project group update  ·  15-20 minutes", 14.5, MUTED, False, 10)],
         spacing=1.15)
    notes(s, 0.4, """
One sentence of framing: this is the short account of the active-inference
comfort-zone workstream - what we set out to measure, the versions we tested,
a pre-registered result that went against our starting hypothesis, and what we
propose to do now. The honest ending is part of the story.
""")

    # -- 2  objectives -----------------------------------------------------
    s = head(prs, "The objective, and why active inference looked like the "
                  "right tool",
             kicker="objectives")
    cw = 15.0
    panel(s, MARGIN, BODY_TOP + 0.2, cw, 9.6, BEIGE)
    text(s, MARGIN + 0.8, BODY_TOP + 0.75, cw - 1.6, 8.6,
         [("What we want from a CZB method", 16, PURPLE, True),
          ("Today, comfort-zone boundaries are measured one scenario and one "
           "indicator at a time: a minimum TTC here, a lateral clearance there, "
           "a headway somewhere else. The boundaries do not compare across "
           "scenarios, and the choice of indicator quietly assumes what the "
           "driver is regulating.", 13, INK, False, 8),
          ("The goal: one scalar comfort-zone level per driver, defined the "
           "same way in every scenario.", 13, INK, True, 8),
          ("Because the end use is a population distribution - an ADAS has to "
           "trigger at some moment, and the operational proposal is a "
           "percentile of the comfort-zone level across drivers, with an "
           "uncertainty interval.", 13, INK, False, 8)], spacing=1.22)
    panel(s, MARGIN + cw + 1.2, BODY_TOP + 0.2, cw, 9.6, BEIGE)
    text(s, MARGIN + cw + 2.0, BODY_TOP + 0.75, cw - 1.6, 8.6,
         [("Why active inference and surprise", 16, PURPLE, True),
          ("A published, behaviorally validated driver model (Schumann et al., "
           "2026) carries a preference function that scores every driving "
           "state by how far it departs from “how the drive is supposed "
           "to go”.", 13, INK, False, 8),
          ("That departure is exactly zero inside the comfortable region - so "
           "“leaving the comfort zone” becomes a defined event, not "
           "a threshold on an always-positive signal.", 13, INK, False, 8),
          ("And the same scalar times the model's responses, as accumulating "
           "surprise. One scenario-free scalar doing both jobs is what no "
           "conventional indicator offers.", 13, INK, True, 8)], spacing=1.22)
    text(s, MARGIN, 14.4, BODY_W, 2.2,
         [("The plan, in one line: ", 14.5, PURPLE, True),
          ("read the model's preference function as a comfort-zone field, fit "
           "one boundary level per driver from human data, and test whether "
           "that construction beats simpler alternatives - on a design built "
           "to tell them apart.", 14.5, INK, False)], spacing=1.2)
    notes(s, 2.0, """
This is the slide that says why the workstream existed. Two beats.

Left: the deliverable was never "a boundary" - it was a population distribution
of boundaries, because a percentile of it is what an ADAS trigger specification
needs. That requires the boundary to be one comparable number per person, which
per-scenario indicators cannot give.

Right: the attraction of the active-inference reading was concrete, not
ideological - a principled zero (leaving the zone is a defined event) and one
scalar doing two jobs (locating the boundary AND timing the response). Say
explicitly that both properties are testable, and that we tested both.
""")

    # -- 3  active inference in one slide ---------------------------------
    s = head(prs, "The idea: a driver is a prediction machine, and “"
                  "surprise” is its error signal",
             kicker="active inference, in plain terms")
    body(s, [
        "The brain continuously predicts what its senses are about to report, "
        "and treats the mismatch - the surprise - as the thing to get rid of. "
        "Surprise here is a number measuring departure from expectation, not an "
        "emotion.",
    ], size=15.5, h=2.6)
    y = 7.0
    cw = 15.0
    panel(s, MARGIN, y, cw, 3.4, BEIGE)
    text(s, MARGIN + 0.8, y + 0.6, cw - 1.6, 2.4,
         [("Change your mind", 16.5, PURPLE, True),
          ("update beliefs until they fit the evidence  =  perception",
           14, INK, False, 6)], spacing=1.2)
    panel(s, MARGIN + cw + 1.2, y, cw, 3.4, BEIGE)
    text(s, MARGIN + cw + 2.0, y + 0.6, cw - 1.6, 2.4,
         [("Change the world", 16.5, PURPLE, True),
          ("act until the world fits the beliefs  =  action",
           14, INK, False, 6)], spacing=1.2)
    text(s, MARGIN, y + 4.2, BODY_W, 4.6,
         [("The trick that makes it work is the preference prior: the model "
           "treats the futures the driver wants as the futures it expects.",
           15.5, PURPLE, True),
          ("Goal-seeking becomes surprise-avoidance - wanting and expecting in "
           "one currency. (“Free energy”, where the group has seen "
           "the term, is just the computable version of this misfit score.)",
           15, INK, False, 10),
          ("This account of driving is not an import: Engström et al. (2018) "
           "laid it out verbally in our own literature. The Schumann model is "
           "that account, made computational.", 15, INK, False, 10)],
         spacing=1.25)
    notes(s, 1.5, """
For the cognitive scientists this is home turf - keep it brisk and let the
plain-language versions stand for the safety engineers.

Two warnings worth issuing: surprise is a number, not an emotion; preference is
a description of the futures a driver treats as normal, not a choice. The
preference prior is the piece the whole comfort-zone argument hangs on, so
plant it firmly.

The Engström, Bärgman, Nilsson, Seppelt, Markkula, Piccinini and Victor (2018)
anchor matters in this room: the verbal version of the paradigm is a paper
several colleagues are on.
""")

    # -- 4  the model, one loop --------------------------------------------
    s = head(prs, "The model we adopted: one loop, run five times a second - and "
                  "surprise times the response",
             kicker="the published model")
    picture_fit(s, "loop_talk.png", MARGIN, 3.9, BODY_W, 11.6, border=False)
    text(s, MARGIN, 15.9, BODY_W, 1.8,
         [("Validated against human response times in three conflict types, "
           "one held out of tuning entirely. ", 14.5, INK, False),
          ("Response time comes from evidence accumulating that the current "
           "plan has stopped working - not from slow senses.", 14.5, PURPLE,
           True)], spacing=1.2)
    notes(s, 1.3, """
Walk the loop once, left to right, then make one point: the surprise
accumulator is where response TIME comes from. Perception is fast - in the
demonstration next, the belief update catches the lead braking within a single
0.2 s step; what takes time is concluding that the current course of action is
no longer adequate.

If asked about scope: the driver-side parameters are identical across the three
published scenarios - only the world and the other vehicle's script change -
which is exactly what made a scenario-free comfort-zone reading plausible.
""")

    # -- 5  the animation --------------------------------------------------
    s = head(prs, "One rear-end conflict through the model's eyes - every number "
                  "from the authors' own deposited output",
             kicker="demonstration")
    gif = find_figure("event_anim.gif")
    if gif is not None:
        with Image.open(gif) as im:
            iw, ih = im.size
        scale = min(Cm(BODY_W) / iw, Cm(12.9) / ih)
        s.shapes.add_picture(str(gif), Cm(MARGIN), Cm(4.0),
                             width=int(iw * scale), height=int(ih * scale))
    text(s, MARGIN, 17.2, BODY_W, 1.2,
         [("Lead brakes at t = 0.8 s; beliefs snap to it in one step; the plan "
           "is kept until accumulated surprise crosses threshold at 1.4 s; "
           "brake at 1.6 s.", 12.5, GREY, False)])
    notes(s, 2.0, """
[CUTTABLE (1st): if time is short, skip this slide - the loop slide plus its
notes carry the mechanism. Cutting it saves 2 minutes.]

PLAY THIS - it is an animated GIF and loops in slideshow mode. Narrate three
beats, not five:

1. t = 0.8: the lead brakes, and in the very next belief update the model
KNOWS - believed lead deceleration goes from 0.0 to -2.0 m/s2. Detection is
not the bottleneck.

2. t = 0.8-1.4: knowing is not yet acting. The plan is abandoned when it stops
delivering the preferred future, not when the world changes; the surprise
account fills step by step.

3. t = 1.4-1.6: one full re-plan in the whole trial, the winner is "brake,
hard", and the response arrives 0.8 s after onset. This is what "surprise
times the response" means concretely.
""")

    # -- 6  the CZB reading ------------------------------------------------
    s = head(prs, "Our move: read the preference function as a comfort-zone "
                  "field, and the boundary as one level set",
             kicker="from model to measurement")
    picture_fit(s, "field_claim_talk.png", MARGIN, 4.0, BODY_W, 10.2,
                border=False)
    text(s, MARGIN, 14.6, BODY_W, 2.8,
         [("This framing is ours, not the model authors' - and it is "
           "falsifiable in two separable halves. ", 14.5, PURPLE, True),
          ("Does accumulated surprise over the field time the human response "
           "(the timing half)? And is the field the right criticality axis - "
           "does it order situations the way drivers do (the axis half)? Each "
           "half got its own pre-registered test.", 14.5, INK, False)],
         spacing=1.2)
    notes(s, 1.5, """
Be explicit that this is our reinterpretation: the authors built a
collision-avoidance model; reading its preference function as a comfort-zone
field is the project's own move, and the thing that either earns its keep or
does not.

Practical property worth one sentence: evaluating the field along a recorded
trajectory needs only kinematics - no particle filter, no planner, microseconds
per trajectory - which is what makes it applicable to naturalistic datasets.

And the human data behind everything that follows: study 1 - 80 participants,
4 scenarios (cut-in, left turn across path, cyclist overtake, truck overtake),
video clips where the ego never responds and a button press marks "now I would
act", so the press IS a timed boundary crossing; and study 2, a second cut-in
study built later for one specific comparison.
""")

    # -- 7  the versions we tested ----------------------------------------
    s = head(prs, "The versions we tested, in the order they happened",
             kicker="seven steps, and where each landed")
    picture_fit(s, "progression_talk.png", MARGIN, 4.0, BODY_W, 12.6,
                border=False)
    notes(s, 1.8, """
Use the figure as the map and point at the rows; the colour coding is
deliberate - teal means the step delivered, pink means a test went against
us, amber means earlier evidence turned out uninformative.

The seven, one line each:

1. Dry run: the full pipeline recovered the model's own brake onsets with a
median error of 0.0 s - the machinery works (on a model's onsets, not yet a
human's).

2. Cut-in construction: the released preference function saturated - it could
not tell a critical cut-in from a mild one - so we replaced its binary lane
test with a continuous, parameter-free form that reduces to the original in
the published geometries.

3. Version 1, the full active-inference reading - field PLUS surprise
accumulator timing the button press. Pre-registered test R.1: next slide.

4. B.1, the cyclist overtake: the field's LATERAL machinery ordered the
cells against the human clearance labels - collision-oriented, not
comfort-oriented. A separate failure, before the decisive test.

5. The collinearity discovery: study 1's encouraging fit could never have
separated the field from "threshold the gap" - gap and TTC correlate 1.0000
in that design.

6. Version 2, the field as a static threshold read through a psychometric
model (probit + lapse, hierarchical per-driver level) - against
matched-complexity simple axes, on study 2, built to separate them.
Pre-registered test R.2: two slides on.

7. What survived when the rules had fired: the per-driver trait.
""")

    # -- 8  R.1 ------------------------------------------------------------
    s = head(prs, "Version 1 - surprise accumulation as the response-timing "
                  "mechanism - failed its pre-registered test",
             kicker="the timing half")
    body(s, [
        ("The rule, fixed before fitting.", "  The accumulator variants should "
         "approach the design regressions' cross-validated error: held-out "
         "RMSE at or below 0.11 passes; above 0.13 is failure."),
        ("The result.", "  Three structurally-argued accumulator variants all "
         "fit worse in sample than a static two-parameter threshold (0.169 "
         "against 0.125), and the best variant scored 0.255 held out. The "
         "rule fired."),
        ("The interpretable cause.", "  Participants responded in a "
         "criticality-graded way at truncation points where almost no "
         "post-onset evidence could exist - anticipation from having seen "
         "each clip about four times, which no evidence-gated integrator can "
         "express."),
    ], size=14.5, gap=11, h=8.2)
    panel(s, MARGIN, 13.0, BODY_W, 4.0, BEIGE)
    text(s, MARGIN + 0.9, 13.45, BODY_W - 1.8, 3.1,
         [("Scope of the verdict, narrowed deliberately.", 15, PURPLE, True),
          ("  This is a FAIL for the accumulator we specified, on a "
           "repeated-exposure stimulus set. It licenses no claim about "
           "evidence accumulation as a family - and the anticipation account "
           "is itself testable, which is one reason we want naturalistic "
           "data.", 14, INK, False)], spacing=1.25)
    notes(s, 1.3, """
[CUTTABLE (2nd): if the group knows R.1 already, compress to one sentence on
the previous slide - "the timing half failed pre-registered, traced to
anticipation from repeated exposure" - and save 1.5 minutes.]

Two points to model: the scope narrowing is accuracy, not damage control (we
tested ONE architecture); and an interpretable failure is worth more than an
uninterpretable success - the anticipation account makes its own predictions.
""")

    # -- 9  R.2 ------------------------------------------------------------
    s = head(prs, "Version 2 - the field as the criticality axis - lost to a "
                  "simple gap threshold, on a design built to decide it",
             kicker="the axis half - the decisive test")
    picture_fit(s, "axis_scoreboard.png", MARGIN, 4.0, 19.4, 9.4, border=False)
    column(s, MARGIN + 20.2, BODY_TOP + 0.4, 10.9, 10.4, "What happened", [
        ("First, a design lesson.", "  In study 1, gap and TTC correlate "
         "1.0000 - the encouraging field fit could never have been "
         "distinguished from “drivers threshold the gap”. Study 2 "
         "was built to break that: a six-fold range of gap at matched TTC."),
        ("The pre-registered comparison.", "  Matched three-parameter "
         "threshold models per axis, identical held-out folds; models, folds "
         "and decision rule committed before the run."),
        ("The field scored worse than chance", "  (0.347 against 0.320); the "
         "log-gap threshold scored 0.152 against a measured noise floor of "
         "0.118. Robust to the two checks run afterwards."),
    ], colour=DEEPPINK, size=12)
    text(s, MARGIN, 13.9, 19.4, 3.2,
         [("Consequence, now in force in every project document: ", 14.5,
           PURPLE, True),
          ("the field's kinematic content may not be described as validated "
           "against human data on the longitudinal dimension - and per the "
           "test's own pre-commitment, the project's headline claim was "
           "restated around what survives.", 14.5, INK, False)], spacing=1.2)
    notes(s, 2.3, """
Be matter-of-fact; this is the talk's centre of gravity.

Say what the verdict does and does not mean: it rules out the KINEMATIC
CONTENT of the preference field as the criticality axis, as fitted, on its own
best scenario. It does not test the lateral machinery (that failed separately
on the cyclist overtake), and it does not rule out some differently built
demand measure - though required deceleration also scored poorly (0.289).

If someone asks "isn't this just a null result": no - the alternative was
matched in complexity, the folds were grouped so the comparison is genuinely
out of sample, and the noise floor was measured, so we know the winning model
is close to as good as anything could be on this data.

Worth adding for this group: the same run caught and fixed an error of our own
(a covariate-window defect that had made the field look wrong in a way it was
not), which is the pre-registration discipline working in both directions.
""")

    # -- 10  what survived -------------------------------------------------
    s = head(prs, "What survived: each driver carries one comfort-zone level, "
                  "largely shared across scenarios",
             kicker="where we ended up")
    picture_fit(s, "trait_shared_fraction.png", MARGIN, 4.0, 19.8, 10.0,
                border=False)
    column(s, MARGIN + 20.6, BODY_TOP + 0.4, 10.5, 12.4,
           "The positive result - no field needed", [
        ("The trait.", "  Per-driver propensity correlates +0.50 to +0.74 "
         "across all six scenario pairs - on average 69% of the reliability "
         "ceiling. One comfort-zone level, substantially shared across a "
         "cut-in, a left turn, a cyclist overtake and a truck overtake."),
        ("The population distribution", "  is well estimated on its own scale "
         "and moves under 1% across specification changes - the percentile "
         "deliverable is stable."),
        ("Transfer across scenarios works", "  once each scenario keeps its "
         "own response floor (0.136 against chance 0.158; ceiling 0.120)."),
    ], colour=DEEPTEAL, size=12)
    notes(s, 1.7, """
This is the result worth building on, and it is field-free: all 43 core
participants saw all four scenarios, so "does a driver carry ONE level" is
testable with no model in the loop - and it largely holds.

Say why the ceiling matters: split-half reliability within a scenario is
0.93-0.98, so 69% of the ceiling is a strong trait signal, not a weak one.

The settled wording of the project claim: each driver carries a scalar
comfort-zone threshold that is substantially shared across scenarios; the
right criticality axis is an open empirical question, on which simple scene
scalars - gap ahead of TTC - currently lead.
""")

    # -- 11  summary: worked / did not ------------------------------------
    s = head(prs, "Summary: what worked, and what did not",
             kicker="the honest ledger")
    cw = 9.9
    column(s, MARGIN, BODY_TOP + 0.4, cw, 10.6, "Worked", [
        ("The trait finding.", "  One comfort-zone level per driver, ~69% "
         "shared across four scenarios - the project's headline result."),
        ("The measurement machinery.", "  Psychometric threshold fitting, a "
         "hierarchical per-driver level, held-out comparisons with rules "
         "fixed in advance."),
        ("Active inference as a hypothesis source.", "  It supplied a "
         "principled “zero”, a candidate axis, and the vocabulary "
         "that organized the work."),
        ("The discipline itself.", "  Pre-registration made two negative "
         "results reportable instead of arguable - and caught one error of "
         "our own."),
    ], colour=DEEPTEAL, size=11.5)
    column(s, MARGIN + cw + 0.75, BODY_TOP + 0.4, cw, 10.6, "Did not work", [
        ("The preference field as criticality axis.", "  Lost to a simple gap "
         "threshold on a design built to decide it - worse than chance, "
         "pre-registered."),
        ("Surprise accumulation as response timing.", "  Failed its "
         "pre-registered criterion; traced to anticipation from repeated "
         "clip exposure."),
        ("The lateral machinery.", "  Failed separately on the cyclist "
         "overtake, before the decisive test."),
    ], colour=DEEPPINK, size=11.5)
    column(s, MARGIN + 2 * (cw + 0.75), BODY_TOP + 0.4, cw, 10.6, "Open", [
        ("The right criticality axis.", "  Gap leads within scenarios; "
         "per-scenario 2D rules and a joint-percentile ellipse are the "
         "candidates now."),
        ("Surprise without the field.", "  Does the surprise family survive "
         "as a scenario-agnostic metric once the preference field is "
         "dropped? Not yet answered."),
        ("Absolute triggers.", "  Everything so far is video-clip judgment "
         "from 43 crowdsourced participants - method development, not a "
         "fleet trigger."),
    ], colour=BLUE, size=11.5)
    panel(s, MARGIN, 15.2, BODY_W, 2.2, BEIGE)
    text(s, MARGIN + 0.9, 15.55, BODY_W - 1.8, 1.6,
         [("A pre-registered falsification of a plausible construct, plus a "
           "positive trait finding that needed no field, is a good outcome - "
           "not a failed project", 14.5, PURPLE, True)], spacing=1.2)
    notes(s, 1.7, """
This is the slide the group should remember. Walk the three columns left to
right; give the pink column the same even tone as the teal one.

If the mood needs it, say the bottom line out loud: the axis entered a fair,
pre-registered competition and lost; the competition itself, and the trait
finding, are the deliverables.
""")

    # -- 12  what now ------------------------------------------------------
    s = head(prs, "What we should do now",
             kicker="proposed next steps, in order")
    body(s, [
        ("1  Build the comparator class properly.", "  Per-scenario 2D state "
         "rules for the truck-overtake and left-turn scenarios - with the "
         "field alternative documented alongside, pros and cons written down "
         "(as agreed at the gate)."),
        ("2  Develop the CZB ellipse.", "  A joint percentile over "
         "per-scenario observables (a Mahalanobis-style construction), with "
         "the per-driver trait mapped onto it - promoted from comparator to "
         "deliverable candidate."),
        ("3  Answer the surprise question before positioning any paper.", "  "
         "Every surprise measure needs a reference distribution to be "
         "surprised relative to; in our construction the preference field WAS "
         "that reference. The exploration must say what replaces it - e.g. a "
         "learned model of normal driving - or surprise goes with the field."),
        ("4  Design the next data collection to decide, not to encourage.", "  "
         "Vary relative speed independently of gap (check the predictor "
         "correlation matrix before collecting); remove or measure the "
         "anticipation confound; and use naturalistic onsets to measure the "
         "video-paradigm offset instead of assuming it."),
    ], size=14.5, gap=12)
    panel(s, MARGIN, 14.3, BODY_W, 2.9, BEIGE)
    text(s, MARGIN + 0.9, 14.72, BODY_W - 1.8, 2.2,
         [("None of this needs anyone to run the model: ", 14, PURPLE, True),
          ("the candidate measures are computed from kinematics alone, and "
           "the data-requirements document for owners of test-track or "
           "naturalistic data exists and can be sent today.", 14, INK,
           False)], spacing=1.18)
    notes(s, 2.0, """
Items 1 and 2 are decided direction (Jonas's gate rulings); item 3 is the open
question he has flagged as blocking paper positioning; item 4 is the ask to
the group, since colleagues in this room hold or can reach relevant data.

On item 3, invite the cognitive scientists in specifically: "what should a
driver be surprised RELATIVE TO, once we drop the hand-built preference
field" is a question squarely in their court.

Leave this slide up for discussion.
""")

    # -- 13  closing -------------------------------------------------------
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H))
    _plain(bg, PURPLE)
    rule(s, 2.3, 6.2, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.1, 29.2, 8.0,
         [("The one-sentence version", 26, WHITE, True),
          ("The active-inference axis entered a fair, pre-registered "
           "competition and lost. What survived - one comfort-zone level per "
           "driver, shared across scenarios - is the thing worth building on.",
           18, TEAL, True, 18)], spacing=1.3)
    text(s, 2.3, 16.9, 29.2, 1.6,
         [("jonas.bargman@chalmers.se   ·   full detail: the project "
           "repository (gate records, analysis outputs, and the 60-minute "
           "version of this talk)", 13, MUTED, False)])
    notes(s, 0.3, """
Land it and open for discussion, ideally with the previous slide's next steps
back up on screen.
""")

    prs.save(str(out))
    total = 0.0
    for slide in prs.slides:
        note = slide.notes_slide.notes_text_frame.text
        if note.startswith("["):
            total += float(note[1:note.index(" min")])
    print("wrote {}  ({} slides, notes budget {:.1f} min)".format(
        out, len(prs.slides._sldIdLst), total))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=HERE / "ai_czb_short_talk.pptx")
    args = ap.parse_args()
    build(args.out)


if __name__ == "__main__":
    main()
