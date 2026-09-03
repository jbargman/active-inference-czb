"""Build the concepts deck: one animated slide per term of the measurement vocabulary.

    python presentation/talk/make_concept_animations.py     # the GIFs (needs out/stage1_looming.md)
    python presentation/talk/build_concepts_talk.py [--out presentation/talk/ai_czb_concepts_talk.pptx]

Brief (Jonas, 2026-09-02): slides, preferably animated, that explain the concepts, with the
deficit axis explained against the looming axis, and a vocabulary in the handbook (chapter 13,
"the measurement vocabulary"). Revised the same evening on his review: lead with the trait
right after the map ("to entice the listener"), state the takeaway on the axis slide, say
"after the lane change has started" instead of "gate open", draw the gate's projection as an
arrow, add a noise-floor slide with a popular-science explanation before the held-out slide,
name the held-out slide's dots plainly, and end with the whole model brought together and one
slide on what is next.

Thirteen slides, nine animated. Budget about 15 minutes.

IMPORTANT for a later session: do NOT rerun this script onto a file Jonas has hand-edited.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_talk import (  # noqa: E402
    BEIGE, BLUE, BODY_TOP, BODY_W, DEEPPINK, DEEPTEAL, GREY, INK, MARGIN, MUTED, PURPLE,
    SLIDE_H, SLIDE_W, TEAL, WHITE, _plain, blank, drop_existing_slides, ensure_template,
    find_figure, head, notes, panel, rule, text,
)


def gif(slide, name, x, y, box_w, box_h):
    """Embed the animation as a MOVIE when an .mp4 sits beside the .gif, else as a picture.

    Jonas, 2026-09-03: an embedded GIF has no scrub bar, and pausing it restarts it from the
    beginning. PowerPoint gives an embedded H.264 .mp4 its own media controls -- a slider,
    and a pause that resumes where it stopped. The poster frame is the animation's LAST
    frame, so the slide shows the finished picture in normal view instead of empty axes.
    """
    path = find_figure(name)
    if path is None:
        return None
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(Cm(box_w) / iw, Cm(box_h) / ih)
    w, h = int(iw * scale), int(ih * scale)
    left, top = Cm(x) + (Cm(box_w) - w) // 2, Cm(y) + (Cm(box_h) - h) // 2
    mp4, poster = path.with_suffix(".mp4"), path.with_suffix(".png")
    if mp4.exists():
        return slide.shapes.add_movie(str(mp4), left, top, w, h,
                                      poster_frame_image=str(poster) if poster.exists() else None,
                                      mime_type="video/mp4")
    return slide.shapes.add_picture(str(path), left, top, width=w, height=h)


def caption(slide, line, y=17.05):
    text(slide, MARGIN, y, 25.5, 1.6, [(line, 12, GREY, False)], align=PP_ALIGN.LEFT)


def concept(prs, kicker, title, gif_name, cap, minutes, script):
    s = head(prs, title, kicker=kicker)
    gif(s, gif_name, MARGIN, 3.8, BODY_W, 12.9)
    caption(s, cap)
    notes(s, minutes, script)
    return s


def build(out: Path) -> None:
    prs = Presentation(str(ensure_template()))
    drop_existing_slides(prs)

    # 1 title
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H)); _plain(bg, PURPLE)
    rule(s, 2.3, 6.8, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.7, 29.0, 5.0, [("The concepts, one at a time", 40, WHITE, True),
                                  ("trait · axis · level · gate · noise floor · how we test · the deliverable · the whole model", 20, TEAL, True, 8)], spacing=1.15)
    text(s, 2.3, 14.4, 29.0, 2.4, [("Jonas Bärgman  ·  Chalmers University of Technology", 17, WHITE, False),
                                   ("each slide is one moving picture; the words are in the notes and in handbook chapter 13", 13.5, MUTED, False, 8)], spacing=1.15)
    notes(s, 0.3, "A vocabulary deck: one animated slide per term. The written definitions are in the handbook's glossary, chapter 13, 'the measurement vocabulary'.")

    # 2 the map
    s = head(prs, "The model has three parts; the slides explain them one by one", kicker="the map")
    cw = 9.9; y = BODY_TOP + 0.6
    for i, (t_, body_, col) in enumerate([
        ("GATE", "does this vehicle count yet? A weight from 0 to 1, from where it will be 3 s from now", BLUE),
        ("AXIS", "the number read off the scene: on the cut-in, how fast the other car grows in the eye", PURPLE),
        ("LEVEL", "where one driver says \"now\" on the axis; the population of levels gives the percentile", DEEPTEAL)]):
        x = MARGIN + i * (cw + 0.75)
        panel(s, x, y, cw, 8.6, BEIGE); rule(s, x + 0.8, y + 0.7, 2.4, col, 4.0)
        text(s, x + 0.8, y + 1.2, cw - 1.6, 7.0, [(t_, 24, col, True, 0), (body_, 14, INK, False, 10)], spacing=1.2)
    text(s, MARGIN, 14.2, BODY_W, 2.4, [("share who intervene = lapse + (1 − lapse) × GATE × Φ((AXIS − LEVEL) / spread)", 17, INK, True)], align=PP_ALIGN.CENTER)
    notes(s, 1.0, """
One equation, three parts. The gate says whether the situation counts yet; the axis is the
number the boundary is a threshold on; the level is that threshold, one per driver. The
spread is how sharply a driver switches, and the lapse is the share of answers that ignore
the stimulus. Everything in the project's claims is a statement about one of these three.
Before the parts, the result that makes them worth having: the next slide.
""")

    # 3b the same, with the model (Jonas, 2026-09-03: "something like slide 4 but with the
    # current model, to the extent possible") -- card TR.1, out/driver_levels.md
    TRAIT_MODEL = dict(
        kicker="the same result, with the model",
        title="The same picture, but now each driver's FITTED level",
        gif="concept_traitmodel.gif",
        cap="Card TR.1. The two scenarios that have a settled current-model rule and per-driver data; each strip in its own units, drivers ranked within their own scenario. The other two scenarios have no per-driver level to compute yet.",
        minutes=1.8,
        script="""
The slide before used no model at all. This one asks the same question of the model we have.

For each driver, fit their LEVEL: on the cut-in, the expansion rate at which that person says
"now", in radians per second; on the left turn, the gap in seconds of PET that person wants
before turning. Two different scenarios, two different rules, two different units, one
threshold per person in each.

Then ask whether it is the same person. It is: the fitted levels agree across drivers at
Spearman 0.65, with a bootstrap interval of 0.41 to 0.80. Put that next to the model-free
number on the previous slide, recomputed on exactly these drivers and these two scenarios,
and it is 0.66. The model has not lost the trait, and it has not invented it either: it
recovers what the raw responses already showed, but now in physical units you could put on a
vehicle.

Two honest limits, both on the slide. First, two scenarios, not four. The cyclist overtake's
third question is undocumented in the study's own materials, so we do not fit a level there;
the truck overtake has no axis and no gate yet, because its construction note has not been
written. Second, the two strips are never merged into one scale. Merging them is exactly card
EL.2, and it needs a decision about what to normalise by that I have asked for and not yet
had. Everything on this slide is a rank, so nothing here depends on that decision.

The median driver acts at about 0.027 radians per second on the cut-in and wants about 2.4
seconds on the left turn, and the middle 80% of drivers spans 0.011 to 0.089 and 0.5 to 3.8.
That spread is the thing a percentile deliverable is a choice about.
""")

    # 2b every term in the equation (Jonas, 2026-09-03: "we need to explain the terms")
    s = head(prs, "Every term in that equation, in one line",
             kicker="the map, term by term")
    text(s, MARGIN, BODY_TOP - 0.5, BODY_W, 1.6,
         [("share who intervene = lapse + (1 − lapse) × GATE × Φ((AXIS − LEVEL) / spread)", 18, INK, True)],
         align=PP_ALIGN.CENTER)
    rows = [("share who intervene", "what we predict and what we observe: of the people shown this exact situation, the fraction who said they would act", INK),
            ("lapse", "the share of answers that ignore the stimulus altogether — a mis-click, a misread, someone answering \"yes\" to everything. Fitted, and small here (about 1.6%)", GREY),
            ("GATE", "does this vehicle count yet? 0 to 1. On the cut-in: will its lateral clearance drop below a minimum within 3 s at its current closing rate", BLUE),
            ("AXIS", "the one number read off the scene at this moment. On the cut-in, how fast the other car grows in the eye — the optical expansion rate, taken apart two slides from now", PURPLE),
            ("LEVEL", "where THIS driver says \"now\" on that axis. One value per driver; the population of them is the deliverable", DEEPTEAL),
            ("spread", "how sharply one driver switches from \"no\" to \"yes\" as the axis rises. Small = a crisp threshold; large = a gradual one", DEEPPINK),
            ("Φ", "the cumulative normal — the S-shaped curve that turns \"how far past my level am I\" into a probability between 0 and 1", GREY)]
    yy = BODY_TOP + 1.6
    for term, gloss, col in rows:
        panel(s, MARGIN, yy, BODY_W, 1.42, BEIGE)
        text(s, MARGIN + 0.5, yy + 0.24, 5.4, 1.1, [(term, 14, col, True)])
        text(s, MARGIN + 6.2, yy + 0.24, BODY_W - 6.9, 1.1, [(gloss, 12, INK, False)])
        yy += 1.60
    notes(s, 1.5, """
Jonas asked for this slide, and he was right to: the equation was on the map with three of
its six symbols unexplained.

Read it left to right. The share who intervene is what we predict and what we observe. The
lapse is the floor: a few answers ignore the stimulus entirely, and if you do not allow for
them the model bends its threshold to chase them. It is fitted, and here it is small.

Then the three parts proper. The gate is a yes/no-ish weight: does this vehicle count yet.
The axis is the number the boundary lives on. The level is where one particular driver sits
on that axis — the quantity this whole project exists to measure.

Two more. The spread is how sharply one driver switches: it is a property of the person and
the paradigm, and it is much larger on video than in a real car, which is a slide near the
end. And Phi is just the S-curve that turns "how far past my level" into a probability.

Everything the project claims is a statement about one of these terms.
""")

    # 3 the trait (leads)
    concept(prs, "first, the result worth having",
            "The same driver, four scenarios: one comfort-zone level per person",
            "status_trait.gif",
            "Study 1, 43 drivers who saw all four scenarios; each line is one driver's criticality-adjusted propensity to intervene, no model in the loop.",
            1.5, """
Start here because it is the reason the rest matters. Take the 43 drivers who saw all four
scenarios. For each, compute how much more or less often than average they said "I would
intervene", after adjusting for how critical each clip was. Draw that number across the four
scenarios. The lines mostly keep their order: a driver who acts early in the cut-in acts early
in the left turn and in both overtakes. Across all six scenario pairs the correlation is 0.50
to 0.74, about 69% of the ceiling that measurement noise allows
(out/cross_scenario_consistency.md). No model was used. So there is one level per person to
measure; the rest of the deck is how.
""")

    concept(prs, TRAIT_MODEL["kicker"], TRAIT_MODEL["title"], TRAIT_MODEL["gif"],
            TRAIT_MODEL["cap"], TRAIT_MODEL["minutes"], TRAIT_MODEL["script"])

    # 4 axis
    concept(prs, "1  the axis",
            "The AXIS: which candidate tells two stimuli apart the way participants did?",
            "concept_axis.gif",
            "Two study-2 stimuli, same speed and starting TTC, lane change in 2 s or 4 s. Left: the two candidate axes. Right: what participants did. Takeaway on the picture.",
            2.0, """
An axis is whatever number we read off the scene at each moment and put the boundary on.
The picture asks one question: which candidate agrees with people?

Top left: the active-inference field's deficit. It jumps to a high value for the fast lane
change and stays near zero for the slow one, because its gate waits for a predicted overlap
that the slow lane change never quite reaches in time. Bottom left: the optical expansion
rate, how fast the car grows in the eye. Nearly identical for both.

Right: participants intervened at about 0.9 in both cases from the first post-onset frame
on. The field says the slow lane change is no problem; people disagreed. The expansion rate
says the two are alike; people agreed. On all 288 cells held out, the expansion rate scores
0.113 against 0.347 for the field (out/cutin2_looming.md, out/cutin2_field_vs_gap.md).

The takeaway is on the slide: the axis is an empirical choice, decided by agreement with
people, not by how decisive a curve looks. A step is not better than a ramp; matching the
data is better.
""")

    # 4b the axis taken apart (Jonas, 2026-09-03)
    concept(prs, "1  the axis, taken apart",
            "The axis is not a new quantity: it is how far away, and how fast it closes",
            "concept_components.gif",
            "One study-2 clip (DV 21 km/h, TTC 2 s, 2 s lane change). Left: the two ingredients and what they make. Right: the three log contributions adding up, against the fitted level.",
            1.7, """
This is the same axis as the slide before, taken apart. Nobody should have to take "optical
expansion rate" on faith.

Write the expansion rate the way the geometry gives it: a car of width W, at a gap g, closing
at dv, grows in the eye at about W times dv over g squared. Now notice that g squared over dv
is just gap times time-to-collision. So the expansion rate is the width divided by (gap x
TTC), and taking logs turns the product into a sum: log expansion rate = log W - log gap -
log TTC.

Three parts, and only two of them move. The width of the car in front is a constant here -
one value, 1.882 metres, across all ninety traces - so it does no work except to shift where
the level sits. What is left is exactly two things: how far away the other car is, and how
fast it is closing on you. Nothing else.

The bar on the right is the punchline. The two logs enter with EQUAL weight, one-for-one. We
did not impose that. Card EL.1 fitted a free weight on the two logs, and it came back 0.497,
in every held-out fold between 0.474 and 0.512. The data picked the halfway point, and the
halfway point is the looming rate.

The black tick under the marker is the exact expansion rate, without the small-angle step
used to derive the identity. At these distances the two are on top of each other; card EL.1b
scored the exact one (out/cutin2_looming.md), so nothing here rests on the approximation.
""")

    # 4c why this quantity
    s = head(prs, "Why THIS quantity, and not gap, or time to collision",
             kicker="1  the axis, motivated")
    cw = 9.9; ytop = BODY_TOP + 0.4
    for i, (title, lines, col) in enumerate([
        ("IT IS WHAT THE EYE GETS",
         ["expansion rate is available directly on the retina: no estimate of distance, and no estimate of speed, has to be made first",
          "gap and TTC each need a quantity the eye does not measure; their product does not"], BLUE),
        ("THE MODEL ALREADY ASSUMED IT",
         ["the active-inference model's own perception stage observes the visual angle and its rate, with a detection threshold (src/aidriver/bicycle.py)",
          "its preference field lost at gate R.2 — but the quantity it perceives with survived"], PURPLE),
        ("TWO PIPELINES LANDED ON IT",
         ["a threshold on expansion rate implies gap grows as the square root of closing speed",
          "a colleague's independent model, different cue and different fitter, fitted that exponent at 0.39–0.42 against our implied 0.5 (appendix 16)"], DEEPTEAL)]):
        x = MARGIN + i * (cw + 0.75)
        panel(s, x, ytop, cw, 9.4, BEIGE); rule(s, x + 0.8, ytop + 0.7, 2.4, col, 4.0)
        runs = [(title, 17, col, True, 0)] + [("–  " + ln, 12.5, INK, False, 8) for ln in lines]
        text(s, x + 0.8, ytop + 1.2, cw - 1.6, 7.8, runs, spacing=1.2)
    text(s, MARGIN, 14.3, BODY_W, 2.6,
         [("And one honest mark against it: in a driving simulator, Xue et al. (2018) found inverse TTC the better cue for brake onset. "
           "On this video paradigm the order reverses (0.113 against 0.168). Which of the two is the paradigm and which is the task, only naturalistic onsets will say",
           13, GREY, False)], align=PP_ALIGN.CENTER)
    notes(s, 1.6, """
Jonas asked for the motivation, so here it is in three columns, and one caveat.

First, it is what the eye actually gets. Expansion rate is an optical quantity: it is on the
retina. Gap is not — you have to infer distance. Closing speed is not either. The striking
thing is that the two quantities you cannot see combine into one you can.

Second — and this is the part I like — the active-inference model already assumed it. Its
perception stage does not observe gap and speed; it observes the visual angle and how fast
that angle is growing, and it has a detection threshold below which closing is simply not
perceptible. So when the axis comparison picked the expansion rate, it picked the model's own
observable. The preference field lost at gate R.2; the perceptual front end did not.

Third, two independent analyses landed on the same cue. A threshold on expansion rate implies
that the accepted gap grows as the square root of closing speed. A colleague, fitting a
completely different model with a different cue and a different fitter, got a speed exponent
of 0.39 to 0.42 where ours implies 0.5. Their exponent had no mechanism; ours supplies one.

The caveat at the bottom is real and belongs on the slide. Xue and colleagues, in a simulator
with real self-motion, found inverse TTC better than expansion rate for brake onset. Our
frozen-video paradigm reverses that order. I do not know which is the paradigm and which is
the task, and I would not claim to. That reference comes from a colleague's note and we have
not verified it ourselves.
""")

    # 5 level
    concept(prs, "2  the level",
            "The LEVEL: where each driver says \"now\", and the population of levels",
            "concept_level.gif",
            "Study 1, 43 drivers. Dots: cells after the lane change has started. Curve: the population response. Ticks and histogram: each driver's threshold. The percentile is read off the histogram.",
            2.0, """
The level is one driver's threshold on the axis: the growth rate at which their chance of
intervening passes one half. We never see a single driver's curve cleanly, so the estimator
is hierarchical: each driver's level is a draw from a population with a median and a spread,
and the population is what the data pin down (out/stage1_looming.md).

Median 0.032 rad/s, about 1.8 degrees of apparent width per second; spread 0.87 log units,
so the 80th percentile is at 3.8 degrees per second. A percentile of this distribution is the
deliverable: the 80th percentile is the state at which 80% of drivers would already have
acted. That is what an ADAS trigger specification needs.

If asked what the old deficit axis was: the same construction on the field's departure
from preference, median 5 400 units; it lost to this one by 14.9 log-likelihood units held out.
""")

    # 6 gate
    concept(prs, "3  the gate",
            "The GATE: does this vehicle count yet?",
            "concept_gate.gif",
            "Same stimulus. The arrow shows where the car will be in 3 s at its current sideways speed. w rises from 0.07 to 1 as that projection reaches into my lane.",
            1.5, """
Before the lane change starts, the car is in its own lane and drivers do not respond,
whatever the gap. The gate is the model's way of saying "not yet": from the car's clearance
now and how fast that clearance is shrinking (measured over the last 0.3 s), project 3 s
ahead; w is the probability that the projection comes within a minimum clearance. Two
parameters, fitted on post-onset cells only; the gate then predicted the 90 pre-onset cells
out of sample to 0.032 (card G.1, out/cutin2_gate.md), and improved the post-onset fit too.
The idea came from the colleague's analysis (handbook appendix 16).

The gate is where scenario knowledge enters. On a left turn it is "will the oncoming car
reach the crossing before I clear it". The axis and the level are what we claim carry over.
""")

    # 7 noise floor
    concept(prs, "4  the noise floor",
            "The NOISE FLOOR: the error a perfect model would still show",
            "concept_noise.gif",
            "A CELL is one clip frozen at one moment, answered by 12–24 people; this study has 288. Left: one such cell, true chance one half, asked again and again. Right: all 288 under a model that knows every true rate — its error is the floor, 0.118.",
            1.7, """
First, what a cell is, because the word is everywhere in this deck and nowhere defined.

The studies are factorial. Each stimulus is one combination of closing speed, starting time
to collision and lane-change duration; each clip is frozen at one of five moments; and each
of those freeze points was answered by 12 to 24 participants. One combination, frozen at one
moment, is a CELL, and what we record for it is two numbers: the share who said they would
intervene, and how many people that share is based on. The second cut-in study has 378 cells,
288 of them after the lane change has started. Every fit in this project is to cell means,
weighted by how many people saw each one.

That second number is the whole point of this slide.

Popular-science version: flip 16 fair coins. You expect 8 heads; you rarely get exactly 8.
Ask 16 people whose true chance of saying "yes" is one half, and the same thing happens: the
observed share scatters around 0.5 with a spread of about 0.12. Each of our cells is 12 to 24
people, so every observed cell mean carries that scatter.

Now imagine a model that knows each cell's true rate exactly. Compare it with what the
12 to 24 people actually said: it is still off, by the sampling scatter. Average that over
the 288 cells and you get 0.118. That is the noise floor: the error the best possible model
would show. A model at the floor cannot be improved on this data, and two models both at the
floor cannot be told apart. It is computed from the observed cell means and counts, so it is
measured, not assumed.
""")

    # 8 how we test
    concept(prs, "5  how we test",
            "HOW WE TEST: predict cells the rule never saw, then compare with the floor",
            "concept_heldout.gif",
            "Second cut-in study, 288 cells in six starting-TTC groups. Grey: cells used for fitting. Pink: cells set aside. Right: what the rule predicted for the set-aside cells against what people said.",
            2.0, """
Held-out scoring: the rule is fitted on five of the six starting-TTC groups and asked to
predict the sixth, which it never saw. Left panel: grey cells are used for the fit, pink
cells are set aside, the black curve is the fitted rule. Right panel: for the set-aside cells,
the rule's prediction on the horizontal axis against what participants actually said on the
vertical; a perfect prediction sits on the diagonal. Repeat six times so every cell has been
predicted blind. The error, 0.113, sits on the floor from the previous slide. Grouping the
folds by starting TTC matters: a good score means the rule transfers across the design's
main axis rather than bending to it. The rules for what counts as a win are written in the
script before the run.
""")

    # 9 deliverable
    concept(prs, "6  the deliverable",
            "THE DELIVERABLE: a percentile, and what it costs in seconds",
            "concept_percentile.gif",
            "Study 1 stimuli. Each 5-point step of the percentile moves the implied trigger by about 0.24 s; the band is the level's own uncertainty, about 0.52 s (out/stage1_looming.md, section 5).",
            1.5, """
Choosing the percentile is a policy question: the 50th percentile triggers when half the
drivers would already have acted, the 80th when most would. This slide says what that choice
costs in seconds on two of the study's stimuli, against the estimation uncertainty of the
level itself. On the looming axis the estimate's uncertainty is the larger of the two, so the
bottleneck is data, not policy: more drivers would tighten the band. On the old deficit axis
the two were comparable. And the mildest stimulus never crosses the median level, so the
percentile also decides whether mild situations trigger at all.
""")

    # 10 whole model, on a study-2 clip (gate/axis/level)
    concept(prs, "7  the whole model (i)",
            "Bringing it together: gate, axis and level on one real cut-in",
            "status_model.gif",
            "Study 2 stimulus, real kinematics. Gate: nothing counts until the car starts to move over. Axis: how fast it grows in your eyes. Level: where each driver says \"now\".",
            1.5, """
The three parts on one clip. Grey: the gate is closed. Then the axis climbs, and the dotted
lines are three drivers' levels, the quartiles of the population: a strict driver acts first,
the median driver next, a lenient one last. That is the whole model qualitatively; the next
slide puts the numbers on it and compares with people.
""")

    # 11 whole model against people
    concept(prs, "7  the whole model (ii)",
            "Bringing it together: the model's prediction over time against what 43 drivers did",
            "concept_whole.gif",
            "Study 1, TTC 4 s clip. Gate w(t), axis θ̇(t), and the model's share who would intervene (purple) from the fitted population; dots are the clip's six observed cells.",
            2.0, """
The whole equation on one study-1 clip, with the fitted numbers: the gate from card G.1, the
axis from the trace, and the population of levels from the stage-1 fit
(out/stage1_looming.md). The purple curve is the model's predicted share who would intervene
at each moment; the dots are what the 43 drivers actually said at the six frozen moments of
this clip. Before onset the gate holds the prediction near zero; as the car moves over, the
gate opens and the axis passes more and more drivers' levels. The model was fitted on all 18
cells of study 1, so this is a fit, not a held-out prediction; the held-out evidence is the
earlier slide. What the picture shows is that gate × axis × level, and nothing else, is the
model.
""")

    # 11b frozen video against a real car (Jonas, 2026-09-03: "demonstrate the difference
    # between the test-track study and the video study, quite late, preferably with a video")
    concept(prs, "8  does any of this survive real driving?",
            "Frozen video against a real car: the same left turn, two paradigms",
            "concept_trackvideo.gif",
            "Jonas's 2013 test-track study (26 drivers who actually drove the turn) against the video left turn at 50 km/h, both fitted with the same model. Card TT.1, out/ltapod_testtrack.md.",
            2.2, """
Everything so far is frozen video: people watched a clip and said what they would do. The
obvious objection is that watching is not driving. This slide is the one test we have against
real driving.

In 2013 we ran a test-track study of exactly this manoeuvre: 26 drivers, in a real car, turning
left across a real oncoming vehicle, with the gap staircased run by run. The video study asked
43 drivers to judge the same manoeuvre frozen on a screen. Same manoeuvre, same manipulated
quantity, two very different paradigms.

Left: what people did. The video curve is smooth because each point is 172 judgments; the
track points are ragged because many are one or two runs. Real driving is expensive.

Right: fit the same hierarchical model to both. The median comfort boundary comes out at
2.45 seconds on the track and 2.18 on video. A quarter of a second apart, inside the design
resolution, and the standard error on the video estimate is 0.20 alone.

Then the strong test. Take the population fitted on video, refit nothing at all, and score it
on the track's data: 0.200, against the track's own fit at 0.231 and chance at 0.289. The
video model predicts real driving better than the track's own fit does, which sounds odd until
you remember the track has 218 runs and the video has 1548 judgments.

Where the paradigms genuinely differ is sharpness. The within-driver spread is 0.20 seconds
on the track and 0.86 on video: in a real car a driver's own boundary is four times crisper.
For a population percentile that is tolerable. For one person's threshold it is not, and it is
the honest limit of the video work.

Two things this does NOT test, and I want to say so: the track had one oncoming speed and one
decision moment, so it tests neither the axis nor the gate.
""")

    # 12 what next
    s = head(prs, "What is next: one line per part", kicker="8  next steps")
    cw = 9.9; y = BODY_TOP + 0.4
    for i, (title, lines, col) in enumerate([
        ("GATE", ["done: it predicts the pre-onset cells out of sample (G.1)",
                  "next: the left turn, where the gate is \"will the oncoming car reach the crossing\" (B.3.v2)"], BLUE),
        ("AXIS", ["done: the cut-in's axis is the expansion rate (EL.1, EL.1b)",
                  "next: is it the axis on the left turn too, or is that arrival time and distance? (B.3.v2)"], PURPLE),
        ("LEVEL", ["done: the per-driver level re-estimated on the new axis (G1.Q1)",
                   "next: one level per driver across every scenario's rule (EL.2); naturalistic onsets to measure the video-to-driving offset"], DEEPTEAL)]):
        x = MARGIN + i * (cw + 0.75)
        panel(s, x, y, cw, 9.4, BEIGE); rule(s, x + 0.8, y + 0.7, 2.4, col, 4.0)
        runs = [(title, 22, col, True, 0)] + [("–  " + ln, 13, INK, False, 8) for ln in lines]
        text(s, x + 0.8, y + 1.2, cw - 1.6, 7.8, runs, spacing=1.2)
    text(s, MARGIN, 14.4, BODY_W, 2.4, [("Two things no card can fix: both studies are frozen video, and 43 drivers support a method, not a fleet trigger. Naturalistic data is the next real step",
                                          14, GREY, False)], align=PP_ALIGN.CENTER)
    notes(s, 1.0, """
One line per part. The gate and the axis are settled on the cut-in and are being tested on
the left turn, which separates time from distance by design. The level has been re-estimated
on the new axis; mapping one level per driver onto every scenario's rule is card EL.2. The
two limits at the bottom are the honest ones: video, and 43 people.
""")

    # 13 closing
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H)); _plain(bg, PURPLE)
    rule(s, 2.3, 6.4, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.3, 29.2, 8.0, [("The vocabulary, in one line each", 26, WHITE, True),
                                  ("Trait: the same driver across scenarios.  Axis: the number read off the scene.  Level: where one driver says now.  "
                                   "Gate: whether it counts yet.  Noise floor: the best any model can do.  Held out: scored on cells never fitted.  "
                                   "Percentile: the share of drivers who would already have acted.", 17, TEAL, True, 16)], spacing=1.35)
    text(s, 2.3, 16.9, 29.2, 1.6, [("handbook chapter 13, \"the measurement vocabulary\", has the written definitions with their sources", 13, MUTED, False)])
    notes(s, 0.3, "Close on the one-line definitions; point to chapter 13 for the written versions.")

    prs.save(str(out))
    total = sum(float(sl.notes_slide.notes_text_frame.text[1:sl.notes_slide.notes_text_frame.text.index(" min")])
                for sl in prs.slides if sl.notes_slide.notes_text_frame.text.startswith("["))
    print("wrote {}  ({} slides, notes budget {:.1f} min)".format(out, len(prs.slides._sldIdLst), total))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "ai_czb_concepts_talk.pptx")
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
