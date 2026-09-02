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
    path = find_figure(name)
    if path is None:
        return None
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(Cm(box_w) / iw, Cm(box_h) / ih)
    w, h = int(iw * scale), int(ih * scale)
    return slide.shapes.add_picture(str(path), Cm(x) + (Cm(box_w) - w) // 2, Cm(y) + (Cm(box_h) - h) // 2, width=w, height=h)


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
            "Left: one cell of 16 people, true chance one half, asked again and again. Right: all 288 cells under a model that knows every true rate. Its error is the floor, 0.118.",
            1.5, """
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
