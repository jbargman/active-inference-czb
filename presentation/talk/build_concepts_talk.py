"""Build the concepts deck: one animated slide per term of the measurement vocabulary.

    python presentation/talk/make_concept_animations.py     # the five GIFs (needs out/stage1_looming.md)
    python presentation/talk/build_concepts_talk.py [--out presentation/talk/ai_czb_concepts_talk.pptx]

Brief (Jonas, 2026-09-02): slides, preferably animated, that explain the different concepts:
the axis, the level, the gate, how we test (held out, noise floor), the percentile
deliverable, and the trait; with the deficit axis explained against the looming axis. Little
text on the slides; the notes carry the explanation; the handbook's glossary (chapter 13,
"the measurement vocabulary") holds the same definitions in writing.

Nine slides, seven animated (five new GIFs from make_concept_animations.py, the model
animation and the trait animation from make_status_animations.py). Budget about 12 minutes.

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

    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H)); _plain(bg, PURPLE)
    rule(s, 2.3, 6.8, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.7, 29.0, 5.0, [("The concepts, one at a time", 40, WHITE, True),
                                  ("axis · level · gate · how we test · the deliverable · the trait", 22, TEAL, True, 8)], spacing=1.15)
    text(s, 2.3, 14.4, 29.0, 2.4, [("Jonas Bärgman  ·  Chalmers University of Technology", 17, WHITE, False),
                                   ("each slide is one moving picture; the words are in the notes and in handbook chapter 13", 13.5, MUTED, False, 8)], spacing=1.15)
    notes(s, 0.3, "A vocabulary deck: one animated slide per term. Use any subset. The definitions are written down in the handbook's glossary, chapter 13, 'the measurement vocabulary'.")

    # the pieces
    s = head(prs, "The model has three parts; each slide explains one", kicker="the map")
    cw = 9.9; y = BODY_TOP + 0.6
    for i, (t_, body_, col) in enumerate([
        ("GATE", "does this vehicle count yet? A weight from 0 to 1, from its lateral clearance projected 3 s ahead", BLUE),
        ("AXIS", "the number read off the scene: on the cut-in, how fast the other car grows in the eye", PURPLE),
        ("LEVEL", "where one driver says \"now\" on the axis; the population of levels gives the percentile", DEEPTEAL)]):
        x = MARGIN + i * (cw + 0.75)
        panel(s, x, y, cw, 8.6, BEIGE); rule(s, x + 0.8, y + 0.7, 2.4, col, 4.0)
        text(s, x + 0.8, y + 1.2, cw - 1.6, 7.0, [(t_, 24, col, True, 0), (body_, 14, INK, False, 10)], spacing=1.2)
    text(s, MARGIN, 14.2, BODY_W, 2.4, [("P(intervene) = lapse + (1 − lapse) × GATE × Φ((AXIS − LEVEL) / spread)", 17, INK, True)], align=PP_ALIGN.CENTER)
    notes(s, 1.0, """
One equation, three parts. The gate says whether the situation counts yet; the axis is the
number the boundary is a threshold on; the level is that threshold, one per driver. The
spread is how sharply a driver switches, and the lapse is the share of answers that ignore
the stimulus. Everything in the project's claims is a statement about one of these three.
""")

    concept(prs, "1  the axis",
            "The AXIS: the number that should rise as the situation gets worse",
            "concept_axis.gif",
            "One real stimulus, two candidate axes. The field's deficit (top) steps and depends on the lane-change speed; the optical expansion rate (bottom) ramps and does not.",
            2.0, """
An axis is whatever number we read off the scene at each moment and put the boundary on.
The project tested five: the active-inference field's deficit, gap, time to collision,
required deceleration, and the optical expansion rate.

Top panel: the deficit, the field's departure from the preferred state, with the project's
lane-entry gate. It is zero, then steps up, and steps later for the slower lane change,
because its gate waits until it predicts overlap at the moment of closure. Participants did
not respond that way: they were flat across lane-change duration at short TTC.

Bottom panel: the expansion rate, how fast the car grows in the eye. It ramps, and it is
nearly identical for both lane changes. On 288 cells held out it scores 0.113 against 0.152
for gap alone and 0.347 for the field (out/cutin2_looming.md, out/cutin2_field_vs_gap.md).
Say plainly: the axis is an empirical choice, decided by prediction, not by theory.
""")

    concept(prs, "2  the level",
            "The LEVEL: where each driver says \"now\", and the population of levels",
            "concept_level.gif",
            "Study 1, 43 drivers. Dots: design cells with the gate open. Curve: the population response. Ticks and histogram: each driver's threshold. The percentile is read off the histogram.",
            2.0, """
The level is one driver's threshold on the axis: the expansion rate at which their chance of
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

    concept(prs, "3  the gate",
            "The GATE: does this vehicle count yet?",
            "concept_gate.gif",
            "Same stimulus. Solid: the car now. Dashed: where it will be in 3 s at its current sideways speed. w rises from 0.07 to 1 as the projection enters the lane.",
            1.5, """
Before the lane change starts, the car is in its own lane and drivers do not respond,
whatever the gap. The gate is the model's way of saying "not yet": the probability that the
vehicle will come within a minimum clearance over a 3 s look-ahead, from its clearance now
and its closing rate. Two parameters, fitted on post-onset cells only; then it predicted the
90 pre-onset cells out of sample to 0.032 (card G.1, out/cutin2_gate.md), and it improved the
post-onset fit too. The idea came from the colleague's analysis (handbook appendix 16).

The gate is where scenario knowledge enters. On a left turn it is "will the oncoming car
reach the crossing before I clear it". The axis and the level are what we claim carry over.
""")

    concept(prs, "4  how we test",
            "HOW WE TEST: predict cells the model never saw, and compare with the noise floor",
            "concept_heldout.gif",
            "Second cut-in study, 288 cells, six starting-TTC groups. Each fold fits on five groups and scores the sixth. The dashed line is the error a perfect model would still show.",
            2.0, """
Two habits make a number a result. First, held-out scoring: the model is fitted on five of
the six starting-TTC groups and scored on the sixth, so that a good score means the rule
transfers across the design's main axis rather than bending to it. Second, the noise floor:
each cell mean is an average of 12 to 24 people, so it carries binomial sampling error, and
averaging that over the cells gives the error a perfect model would still show, 0.118 here.
A model at the floor cannot be improved on this data; two models at the floor cannot be told
apart. The rules for what counts as a win are written in the script before the run.
""")

    concept(prs, "5  the deliverable",
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

    concept(prs, "6  the trait",
            "The TRAIT: the same driver, four scenarios",
            "status_trait.gif",
            "Study 1, 43 drivers who saw all four scenarios; each line is one driver's criticality-adjusted propensity to intervene, no model in the loop.",
            1.5, """
The claim that makes a level worth having: it is largely the same person across scenarios.
Per-driver propensity, adjusted for how critical each cell was, correlates at 0.50 to 0.74
across all six scenario pairs, about 69% of the reliability ceiling
(out/cross_scenario_consistency.md). The remaining third is scenario-specific, which is what
the gate is for, and why transfer tests are scored against 0.69 rather than against 1.
""")

    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H)); _plain(bg, PURPLE)
    rule(s, 2.3, 6.4, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.3, 29.2, 8.0, [("The vocabulary, in one line each", 26, WHITE, True),
                                  ("Axis: the number read off the scene.  Level: where one driver says now.  Gate: whether it counts yet.  "
                                   "Held out: scored on cells never fitted.  Noise floor: the best any model can do.  "
                                   "Percentile: the share of drivers who would already have acted.  Trait: the same driver across scenarios.",
                                   17, TEAL, True, 16)], spacing=1.35)
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
