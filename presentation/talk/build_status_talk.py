"""Build the 10-15 minute "where we are now" deck on the Chalmers template.

    python presentation/talk/make_status_animations.py      # first, the GIFs
    python presentation/talk/build_status_talk.py [--out presentation/talk/ai_czb_status_talk.pptx]

Brief (Jonas, 2026-09-02): a separate presentation explicitly on where we are now - what
the model we have is based on, what it means, how we can know that it means that, and
what we can do next. Little text on the slides; the notes field carries the talk; moving
illustrations with captions wherever possible.

Ten slides, four of them animated (GIFs from make_status_animations.py and the event
animation from make_event_animation.py). Every number is read from a tracked output and
the notes say which. Budgets sum to about 12.5 minutes.

IMPORTANT for a later session: do NOT rerun this script onto a file Jonas has hand-edited;
copy and augment instead (chalmers-slide-generation-jonas skill).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_talk import (  # noqa: E402
    BEIGE, BLUE, BODY_TOP, BODY_W, DEEPPINK, DEEPTEAL, GREY, INK, MARGIN, MUTED, PURPLE,
    SLIDE_H, SLIDE_W, TEAL, WHITE, _plain, blank, drop_existing_slides, ensure_template,
    find_figure, head, notes, panel, picture_fit, rule, text,
)


def gif(slide, name, x, y, box_w, box_h):
    path = find_figure(name)
    if path is None:
        return None
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(Cm(box_w) / iw, Cm(box_h) / ih)
    w, h = int(iw * scale), int(ih * scale)
    return slide.shapes.add_picture(str(path), Cm(x) + (Cm(box_w) - w) // 2,
                                    Cm(y) + (Cm(box_h) - h) // 2, width=w, height=h)


def caption(slide, line, y=17.05):
    # keeps clear of the template's logo at bottom right: 25.5 cm wide, left-aligned
    text(slide, MARGIN, y, 25.5, 1.6, [(line, 12, GREY, False)], align=PP_ALIGN.LEFT)


def box(slide, x, y, w, h, title, lines, colour):
    panel(slide, x, y, w, h, BEIGE)
    rule(slide, x + 0.8, y + 0.7, 1.6, colour)
    runs = [(title, 17, INK, True, 0)]
    for ln in lines:
        runs.append((ln, 13, INK, False, 6))
    text(slide, x + 0.8, y + 1.1, w - 1.6, h - 1.5, runs, spacing=1.2)


def build(out: Path) -> None:
    prs = Presentation(str(ensure_template()))
    drop_existing_slides(prs)

    # -- 1 title -----------------------------------------------------------
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H))
    _plain(bg, PURPLE)
    rule(s, 2.3, 6.8, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.7, 29.0, 5.0,
         [("Where we are now", 40, WHITE, True),
          ("the comfort-zone model we have, what it rests on, and what comes next",
           24, TEAL, True, 8)], spacing=1.15)
    text(s, 2.3, 14.4, 29.0, 2.4,
         [("Jonas Bärgman  ·  Chalmers University of Technology", 17, WHITE, False),
          ("10-15 minutes  ·  four animated slides; let each run once before speaking to it",
           13.5, MUTED, False, 8)], spacing=1.15)
    notes(s, 0.3, """
One sentence: this is a status talk. Four questions, in order: what the model we now
have is based on, what it means, how we know it means that, and what we do next. Most
slides are one moving picture with a caption; the words are here in the notes.
""")

    # -- 2 where we came from ---------------------------------------------
    s = head(prs, "Where we came from: a driver model in which surprise times the response",
             kicker="1  what it is based on")
    gif(s, "event_anim.gif", MARGIN, 3.8, BODY_W, 12.9)
    caption(s, "A published active-inference driver model (Schumann et al., 2026), on its own deposited "
               "output: beliefs update in one step; the plan is kept until accumulated surprise crosses a "
               "threshold; then it brakes.")
    notes(s, 1.5, """
Let it loop once. The starting point of the project was this model: a driver that predicts,
compares the prediction with what it prefers, and acts when the accumulated mismatch, the
surprise, crosses a threshold. Our hypothesis was that its preference function could be read
as a comfort-zone field: zero inside the comfortable region, so leaving the zone is a
defined event, and one scalar doing two jobs, locating the boundary and timing the response.

Both halves were tested against human data with rules fixed in advance, and both failed
(gates R.1 and R.2, docs/r2_gate_decisions.md). That is the background; the rest of this
talk is what we have instead, and it is more than we expected.
""")

    # -- 3 the model we have -----------------------------------------------
    s = head(prs, "Where we are: a gate, an axis, and one level per driver",
             kicker="2  what the model is, on one real cut-in")
    gif(s, "status_model.gif", MARGIN, 3.8, BODY_W, 12.9)
    caption(s, "Study 2 stimulus, real kinematics. Gate: nothing counts until the car starts to move over. "
               "Axis: how fast it grows in your eyes. Level: where each driver says \"now\".")
    notes(s, 2.5, """
This is the model in one picture, on a real stimulus from the second cut-in study (trace
LC_dv21_Tlc3p0_TTC04; presentation/talk/make_status_animations.py). Three parts.

The GATE: before the lane change starts, the car is in its own lane and drivers do not
respond, whatever the gap. The grey region. The gate is the scenario-specific part: "will
this vehicle become my problem". It has now been tested (card G.1, out/cutin2_gate.md): a
gate that projects the lateral clearance 3 s ahead, fitted only on post-onset cells,
predicts the 90 pre-onset cells out of sample to 0.032 (observed mean 0.023), and it
improves the post-onset fit too (0.103 against 0.114).

The AXIS: once the gate is open, what orders the response is one scalar. Card EL.1 found it
on 288 cells: gap and time-to-collision weighted exactly equally on the log scale
(replication/czb/out/cutin2_two_axis.md, fitted weight 0.47-0.51 in every fold). Gap times
TTC is the vehicle's width divided by its optical expansion rate, so that rule IS "how fast
the car grows in your eyes", the classic looming variable. The lower panel plots it.

The LEVEL: each driver has one threshold on that axis; the dotted lines are the quartiles of
the population response curve fitted to the same 288 cells (a strict driver acts early, a
lenient one late). The next question is whether that level is the same person across
scenarios; slide 7 says it largely is.

Say plainly: this is a descriptive model, a psychometric threshold with a gate. It is not
the active-inference field. It is what survived the tests.
""")

    # -- 4 what it rests on -----------------------------------------------
    s = head(prs, "What it rests on", kicker="1  the data and the tests")
    cw = 9.9
    box(s, MARGIN, BODY_TOP + 0.4, cw, 8.8, "Two human studies", [
        "Study 1: 4 scenarios, video clips, a button press for \"now I would act\"; 43 drivers saw all four",
        "Study 2: a cut-in study built so that gap and time-to-collision can be told apart (288 cells)",
    ], BLUE)
    box(s, MARGIN + cw + 0.75, BODY_TOP + 0.4, cw, 8.8, "Rules fixed before each run", [
        "models, folds and the decision rule committed to the repository first",
        "held-out scoring against chance and against the measured noise floor",
    ], DEEPTEAL)
    box(s, MARGIN + 2 * (cw + 0.75), BODY_TOP + 0.4, cw, 8.8, "Two eliminations", [
        "surprise accumulation as the timing mechanism: failed (gate R.1)",
        "the preference field as the criticality axis: lost to gap (gate R.2)",
    ], DEEPPINK)
    text(s, MARGIN, 14.0, BODY_W, 2.6,
         [("Everything on the previous slide is what remains after those two eliminations, "
           "measured with the same rules", 15, PURPLE, True)], align=PP_ALIGN.CENTER)
    notes(s, 1.2, """
Three things the model rests on. The data: two video studies (docs/czb_study1_data_plan.md;
replication/czb/out/cutin2_scope.md), no naturalistic driving yet, and say so. The
discipline: every comparison scored held out with rules fixed before the run, against
chance and against the sampling-noise floor, so a result cannot be argued with afterwards.
And the two eliminations: the timing half at R.1 and the axis half at R.2, both documented
in docs/r2_gate_decisions.md. The point of the slide is the last line: the model on slide 3
is not a proposal, it is a residue. Everything else was tried and lost.
""")

    # -- 5 what it means ---------------------------------------------------
    s = head(prs, "What it means", kicker="3  three sentences")
    y = BODY_TOP + 0.6
    for i, (lead, body_, col) in enumerate([
        ("Each driver carries one comfort-zone level,", " and it is largely the same person in a cut-in, a left turn, and two overtakes.", DEEPTEAL),
        ("In a cut-in, the boundary is a threshold on how fast the other car grows in the eye,", " not on distance, time, or required deceleration alone.", PURPLE),
        ("A gate decides when the axis applies,", " and the gate is the part that changes between scenarios.", BLUE),
    ]):
        rule(s, MARGIN, y + i * 3.9, 1.6, col)
        text(s, MARGIN, y + 0.35 + i * 3.9, BODY_W, 3.2,
             [(lead, 19, col, True), (body_, 19, INK, False)], spacing=1.2)
    notes(s, 1.0, """
Read the three sentences, slowly, and add the numbers from the notes only if asked.

One: the per-driver level correlates +0.50 to +0.74 across all six scenario pairs, about
69% of the reliability ceiling (replication/czb/out/cross_scenario_consistency.md).

Two: the equal-weight rule on gap and TTC scores 0.114 held out against 0.152 for gap alone
and 0.168 for TTC; the noise floor is 0.118 (out/cutin2_two_axis.md). And gap x TTC equals
width over optical expansion rate, so the cue is looming: fitted directly, the 1D looming-rate
threshold scores 0.113 (card EL.1b, out/cutin2_looming.md; threshold 0.034 rad/s, about 1.9
degrees per second of apparent growth).

Three: the gate is where scenario knowledge enters; the axis and the level are what we
claim carry over. That split is the whole design of the program now.
""")

    # -- 6 how we know (i) ------------------------------------------------
    s = head(prs, "How we know (i): the scalars were made to compete, held out",
             kicker="4  the scoreboard")
    gif(s, "status_scoreboard.gif", MARGIN, 3.8, BODY_W, 12.9)
    caption(s, "Second cut-in study, 288 post-onset cells, leave-one-starting-TTC-out folds; models, folds "
               "and the rule committed before the run (gate R.2 and card EL.1).")
    notes(s, 2.0, """
Let the bars appear. Each is a three-parameter threshold model on one scalar, same fitter,
same folds, scored on cells it never saw. The field we started from is worse than
predicting the mean; the physics-first cue, required deceleration, is poor; TTC is useful;
gap alone is the best single scalar; and gap and TTC together, equally weighted, reach the
noise floor, which nothing can beat except by luck.

Two things make this "knowing" rather than "finding": the rule was written before the
numbers existed, and the noise floor was measured, so we know how good a model could
possibly be. Sources: replication/czb/out/cutin2_field_vs_gap.md and out/cutin2_two_axis.md.

If asked about the colleague's required-deceleration model: an independent analysis on the
same data, different fitter and family, reached the same ordering and the same speed
exponent of about 0.4; that convergence is in handbook appendix 16.
""")

    # -- 7 how we know (ii) -----------------------------------------------
    s = head(prs, "How we know (ii): the same drivers, four scenarios, no model in the loop",
             kicker="4  the trait")
    gif(s, "status_trait.gif", MARGIN, 3.8, BODY_W, 12.9)
    caption(s, "Study 1, 43 drivers who saw all four scenarios; each line is one driver's criticality-adjusted "
               "propensity to intervene. No field, no fitted model: a per-driver mean per scenario.")
    notes(s, 1.5, """
Watch the lines keep their order. This is the cheapest and strongest result we have: a per-
driver propensity, criticality-adjusted, with no model at all, correlates across scenarios
at 0.53 to 0.78 of the split-half reliability ceiling, mean 0.69
(replication/czb/out/cross_scenario_consistency.md). The reliability within a scenario is
0.93 to 0.98, so this is a strong trait, not a weak one.

The other third is scenario-specific, which is why the gate exists and why every transfer
test is scored against 0.69, not against perfection.
""")

    # -- 8 how we know (iii) ----------------------------------------------
    s = head(prs, "How we know (iii): what would have changed our mind, and did not",
             kicker="4  the checks")
    cw = 15.0
    box(s, MARGIN, BODY_TOP + 0.4, cw, 9.6, "Checks that passed", [
        "the decisive result reproduced by an independent fit (bootstrap +0.17 to +0.22 against a 0.01 margin)",
        "the noise floor measured, and the best rule sits on it",
        "a colleague's independent pipeline lands on the same cue and the same speed exponent",
    ], DEEPTEAL)
    box(s, MARGIN + cw + 1.2, BODY_TOP + 0.4, cw, 9.6, "What we still cannot say", [
        "anything about real driving: both studies are frozen video, no self-motion",
        "the absolute trigger for a fleet: 43 crowdsourced participants support method, not policy",
        "whether the gate's shape is right: the studies sample only \"closed\" and \"open\"",
    ], DEEPPINK)
    notes(s, 1.2, """
The left column is the evidence that the result is real: the pipeline review
(docs/r2_pipeline_review.md) re-derived the decisive comparison with a different fitter and
bootstrapped the difference; the floor is measured; and an external analysis of a
required-deceleration model on the same data (handbook appendix 16) converges on gap first
with a speed exponent of about 0.4.

The right column is what we volunteer before anyone asks. Video, not driving: in a moving
car the literature finds inverse tau, one over TTC, beats the expansion rate; here it is the
reverse, and the difference is exactly the paradigm question naturalistic data would settle.
""")

    # -- 9 what next -------------------------------------------------------
    s = head(prs, "What we can do next: one card per part of the model",
             kicker="5  next steps")
    cw = 9.9
    y = BODY_TOP + 0.4
    for i, (title, lines, col) in enumerate([
        ("GATE", ["done today: the fixed-horizon gate predicts the pre-onset cells out of sample (card G.1, 0.032)",
                  "then the left turn: the gate is \"will the oncoming car reach the crossing\" (B.3.v2)"], BLUE),
        ("AXIS", ["done today: the looming-rate threshold scores 0.113 on its own, the identity holds (EL.1b)",
                  "the left turn separates time from distance by design: is it looming there too?"], PURPLE),
        ("LEVEL", ["map one level per driver onto every scenario's rule (EL.2)",
                   "naturalistic onsets: measure the video-to-driving offset instead of assuming it"], DEEPTEAL),
    ]):
        x = MARGIN + i * (cw + 0.75)
        panel(s, x, y, cw, 9.4, BEIGE)
        rule(s, x + 0.8, y + 0.7, 2.4, col, 4.0)
        runs = [(title, 22, col, True, 0)]
        for ln in lines:
            runs.append(("–  " + ln, 13, INK, False, 8))
        text(s, x + 0.8, y + 1.2, cw - 1.6, 7.8, runs, spacing=1.2)
    text(s, MARGIN, 14.4, BODY_W, 2.4,
         [("None of this needs anyone to run a simulation: every candidate is computed from kinematics, "
           "and the data request for owners of naturalistic or test-track data exists", 14, GREY, False)],
         align=PP_ALIGN.CENTER)
    notes(s, 1.5, """
One card per part. The gate: the colleague's fixed-horizon gate predicted the pre-onset cells
out of sample, and card G.1 (run 2026-09-02) does the same in front of our rule: CP1 out of
sample 0.032, post-onset 0.103. Next is the left-turn
scenario where the gate is "will the oncoming car reach the crossing before I clear it"
(docs/ltap_construction_note.md). The axis: the looming identity gets its own check with
real widths (EL.1b), and the left turn is the scenario that separates time from distance by
design, so it will tell whether looming is the cue there too (the geometry says probably
not). The level: card EL.2 maps one level per driver onto each scenario's rule; and
naturalistic onsets would measure the video-to-driving offset, which is the single largest
upgrade available.
""")

    # -- 10 closing --------------------------------------------------------
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H))
    _plain(bg, PURPLE)
    rule(s, 2.3, 6.4, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.3, 29.2, 8.0,
         [("Where we are, in one line", 26, WHITE, True),
          ("One level per driver, shared across scenarios; in a cut-in the boundary is how fast the "
           "other car grows in the eye; a gate says when that counts. Everything else was tried "
           "and lost, by rules we wrote first.", 19, TEAL, True, 16)], spacing=1.3)
    text(s, 2.3, 16.9, 29.2, 1.6,
         [("jonas.bargman@chalmers.se   ·   every number in the notes names its tracked output in the repository",
           13, MUTED, False)])
    notes(s, 0.3, """
Land it and open for questions with slide 9 back up.
""")

    prs.save(str(out))
    total = 0.0
    for slide in prs.slides:
        note = slide.notes_slide.notes_text_frame.text
        if note.startswith("["):
            total += float(note[1:note.index(" min")])
    print("wrote {}  ({} slides, notes budget {:.1f} min)".format(out, len(prs.slides._sldIdLst), total))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "ai_czb_status_talk.pptx")
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
