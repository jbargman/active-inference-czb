"""Build the three-slide faculty-assembly deck on how the in-depth LLM review was done.

    python presentation/faculty/build_llm_review_deck.py

Audience: the faculty assembly, on "things where I have used LLMs in my work".
The example is the August 2026 in-depth review of Schumann et al. (2026),
*Active inference as a model of collision avoidance behavior in human drivers*,
Nature Communications 17:5009 — the review document is `docs/method_review.md`.

Written as a script rather than hand-built so it can be rebuilt when a number
changes. Every fact on the slides comes from one of three tracked sources and
the mapping is in FACTS below:

  the review itself      docs/method_review.md (sections 1, 2, 5, 9)
  the prompt log         the UserPromptSubmit hook's JSONL for this project,
                         C:/Users/bargman/OneDrive - Chalmers/1_Work/Promptlogs/
                         C--Users-bargman-OneDrive---Chalmers-1-Work-1-Code-
                         WaymoActiveInference.cw-fcdp6f4.jsonl
  the repository         external/, replication/, notes/

The prompts on slide 2 are quoted from the log, lightly trimmed for length with
an ellipsis and with the typing left as it was — that is the point of showing
them. Nothing is reconstructed from memory.

Slides, one idea each:
  1  the problem: a published model had to be trusted before it could be built on
  2  what was set up first, and the two prompts that produced the review
  3  what someone else would need to do the same

Note on the "three findings" number on slide 1: the review's section 1 lists
three findings that did not hold up, plus ten places where the released code
differs from the paper and the SI (section 5) and five questions for the authors
(section 9).
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Cm, Pt

HERE = Path(__file__).resolve().parent
SKILL = Path.home() / ".claude" / "skills" / "chalmers-slide-generation-jonas" / "resources"
TEMPLATE_POTX = SKILL / "chalmers-tekniska-ho-gskola-sv.potx"
TEMPLATE_PPTX = HERE / "_chalmers-template.pptx"

# Chalmers' own theme colours, read out of the template rather than guessed.
PURPLE = RGBColor(0x47, 0x2C, 0xBE)      # accent1
LILAC = RGBColor(0x67, 0x46, 0xEB)       # accent3
BLUE = RGBColor(0x36, 0xB7, 0xF6)        # accent5
TEAL = RGBColor(0x61, 0xE9, 0xD2)        # accent6
PINK = RGBColor(0xD9, 0x87, 0xBA)        # accent4
INK = RGBColor(0x22, 0x22, 0x22)         # dk1
BEIGE = RGBColor(0xF0, 0xED, 0xE6)       # lt2
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY = RGBColor(0x5A, 0x5A, 0x5A)

FONT = "Arial"
LAYOUT_TITLE_ONLY = 30   # Endast rubrik — we lay out our own grid on all three

EMAIL = "jonas.bargman@chalmers.se"


# -- template handling --------------------------------------------------------


def ensure_template() -> Path:
    """A .potx is a .pptx whose package declares a template content type."""
    if TEMPLATE_PPTX.exists() and TEMPLATE_PPTX.stat().st_mtime >= TEMPLATE_POTX.stat().st_mtime:
        return TEMPLATE_PPTX
    HERE.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(TEMPLATE_POTX) as zin, \
            zipfile.ZipFile(TEMPLATE_PPTX, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(b"presentationml.template.main+xml",
                                    b"presentationml.presentation.main+xml")
            zout.writestr(item, data)
    return TEMPLATE_PPTX


def drop_existing_slides(prs) -> None:
    id_list = prs.slides._sldIdLst
    for slide_id in list(id_list):
        prs.part.drop_rel(slide_id.rId)
        id_list.remove(slide_id)


def remove_empty_placeholders(slide) -> None:
    for shape in list(slide.placeholders):
        if shape.has_text_frame and not shape.text_frame.text.strip():
            shape._element.getparent().remove(shape._element)


# -- drawing helpers ----------------------------------------------------------


def _plain(shape, colour: RGBColor | None) -> None:
    if colour is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = colour
    shape.line.fill.background()
    shape.shadow.inherit = False


def text(slide, x, y, w, h, runs, *, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    """Each run is ``(text, size, colour, bold)``, optionally a fifth element
    giving the space before that paragraph in points."""
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = anchor
    frame.margin_left = frame.margin_right = 0
    frame.margin_top = frame.margin_bottom = 0
    for index, run in enumerate(runs):
        body, size, colour, bold = run[:4]
        before = run[4] if len(run) > 4 else 0
        para = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        para.alignment = align
        para.line_spacing = spacing
        if before:
            para.space_before = Pt(before)
        piece = para.add_run()
        piece.text = body
        piece.font.size = Pt(size)
        piece.font.color.rgb = colour
        piece.font.bold = bold
        piece.font.name = FONT
    return box


def headline(slide, parts, *, y=Cm(0.61), width=Cm(30.5), size=25):
    """The slide's one idea, stated. Parts are (text, colour) pairs."""
    title = slide.shapes.title
    # All four, never a subset: overriding one drops the rest of the inherited
    # geometry and the box collapses.
    title.left, title.top = Cm(1.04), y
    title.width, title.height = width, Cm(2.6)
    title.text_frame.text = ""
    title.text_frame.word_wrap = True
    para = title.text_frame.paragraphs[0]
    for body, colour in parts:
        run = para.add_run()
        run.text = body
        run.font.size = Pt(size)
        run.font.bold = True
        run.font.color.rgb = colour
        run.font.name = FONT
    return title


def column(slide, x, y, w, h, heading_text, items, *, rule=PURPLE, size=11):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Cm(1.57), Pt(3.5))
    _plain(bar, rule)
    text(slide, x, y + Cm(0.33), w, Cm(0.9), [(heading_text, 13, INK, True)])
    runs = []
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            runs.append((item[0], size, rule, True, 0 if i == 0 else 9))
            runs.append((item[1], size, INK, False, 1))
        else:
            runs.append((f"–  {item}", size, INK, False, 0 if i == 0 else 7))
    return text(slide, x, y + Cm(1.45), w, h, runs, spacing=1.12)


def quote_card(slide, x, y, w, h, stamp, body, *, accent=PURPLE):
    """A prompt, shown as it was typed. The stamp carries when it was sent."""
    card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    _plain(card, BEIGE)
    edge = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Cm(0.13), h)
    _plain(edge, accent)
    text(slide, x + Cm(0.42), y + Cm(0.22), w - Cm(0.75), Cm(0.6),
         [(stamp, 8.5, accent, True)])
    text(slide, x + Cm(0.42), y + Cm(0.86), w - Cm(0.75), h - Cm(1.1),
         [(body, 10.5, INK, False)], spacing=1.14)
    return card


def footer(slide, number: int) -> None:
    # The Chalmers wordmark sits in the bottom-right corner from about 30 cm, so
    # the slide number goes to its left rather than underneath it, where the
    # first render showed it disappearing entirely.
    text(slide, Cm(1.04), Cm(17.9), Cm(20), Cm(0.6),
         [(f"{EMAIL}", 8, GREY, False)])
    text(slide, Cm(26.0), Cm(17.9), Cm(2.6), Cm(0.6),
         [(str(number), 8, GREY, False)], align=PP_ALIGN.RIGHT)


# -- slides -------------------------------------------------------------------


def slide_problem(prs) -> None:
    """Why a review at all: we needed to build on the model, not cite it."""
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_TITLE_ONLY])
    headline(slide, [
        ("We needed to build on a published model, ", INK),
        ("so we had to know what its code actually does", PURPLE),
    ])

    text(slide, Cm(1.04), Cm(3.5), Cm(31), Cm(1.4), [
        ("Schumann et al. (2026), Nature Communications — active inference as a model of "
         "collision avoidance. Our project uses it to measure driver comfort-zone boundaries, "
         "so the model is instrumental: if it does not do what the paper says, our measurements "
         "inherit that.", 12, GREY, False),
    ], spacing=1.15)

    # The three artefacts. A review of a paper alone could not have found any of this.
    steps = [
        ("The article\n+ 17-page SI", "every equation,\nparameter and\nquantitative claim\nlisted"),
        ("The released code", "~10 files read\nline by line against\nthe equations"),
        ("The OSF deposit", "3.1 GB, 896 runs,\nre-analysed from\nthe raw pickles"),
        ("Our own\nre-implementation", "built from the SI,\nthen run against\nthe authors' code"),
    ]
    x, step_w, gap = Cm(1.04), Cm(7.5), Cm(0.42)
    for i, (head, body) in enumerate(steps):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Cm(5.5), step_w, Cm(3.4))
        _plain(box, PURPLE if i == 0 else BEIGE)
        box.adjustments[0] = 0.09
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = Cm(0.2)
        lines = [(l, 11, WHITE if i == 0 else INK, True) for l in head.split("\n")]
        lines += [(l, 9.5, WHITE if i == 0 else GREY, False) for l in body.split("\n")]
        for j, (line, size, colour, bold) in enumerate(lines):
            para = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            para.alignment = PP_ALIGN.CENTER
            run = para.add_run()
            run.text = line
            run.font.size = Pt(size)
            run.font.color.rgb = colour
            run.font.bold = bold
            run.font.name = FONT
        x = x + step_w + gap

    text(slide, Cm(1.04), Cm(9.2), Cm(31), Cm(0.8), [
        ("Four artefacts, cross-checked against each other. A review of the paper alone could "
         "not have produced any of what follows.", 10, PURPLE, True),
    ], spacing=1.1)

    column(slide, Cm(1.04), Cm(10.9), Cm(9.6), Cm(5.6), "What came out", [
        "A 9-section review document, ~9 000 words",
        "Three reported results that did not hold up in the deposit",
        "Ten places where the released code differs from the paper or SI",
        "Five questions a short reply from the authors would settle",
    ], rule=BLUE, size=10.5)
    column(slide, Cm(11.6), Cm(10.9), Cm(10.2), Cm(5.6), "Example of a finding", [
        ("The accumulator is not near zero in ordinary following",
         "In the deposited runs the model's surprise signal sits at 50 000–100 000 "
         "per step while nothing is happening, and 18–44% of the evidence that "
         "triggers the response is accumulated before the lead vehicle brakes."),
    ], rule=TEAL, size=10.5)
    column(slide, Cm(22.8), Cm(10.9), Cm(9.7), Cm(5.6), "Why it mattered to us", [
        "We had blamed our own replication for a mismatch. It was not ours",
        "The finding changed what we could use the model for",
        "Sent to one of the authors — a colleague — as a colleague would",
    ], rule=PINK, size=10.5)

    remove_empty_placeholders(slide)
    footer(slide, 1)


def slide_prompts(prs) -> None:
    """The preparation, then the two prompts that did it — quoted from the log."""
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_TITLE_ONLY])
    headline(slide, [
        ("The work was in the setup. ", INK),
        ("The prompts that produced the review were two sentences", PURPLE),
    ])

    column(slide, Cm(1.04), Cm(3.6), Cm(9.9), Cm(12.8), "First — six days of setup", [
        ("Collect and scope", "Downloaded the paper set from the publisher's page and had it "
                              "categorised; only the active-inference folder in scope."),
        ("Read before reviewing", "\"Read the papers, but also do an on-line search about "
                                  "active inference more generally... Document all your "
                                  "findings, summarizing each paper for later reference\"."),
        ("Get the artefacts", "Cloned the released code; downloaded the 3.1 GB OSF deposit."),
        ("Build it independently", "Asked for the method to be re-implemented from the SI — "
                                   "which is what later exposed that the SI and the code "
                                   "disagree."),
        ("Keep the thread", "A HANDOFF.md re-read at the start of every session, so a new "
                            "context began where the last one stopped."),
    ], rule=BLUE, size=10)

    text(slide, Cm(11.9), Cm(3.6), Cm(20.6), Cm(0.8), [
        ("Then the review itself — verbatim from my prompt log, typos and all",
         13, INK, True),
    ])

    quote_card(
        slide, Cm(11.9), Cm(4.55), Cm(20.6), Cm(3.5), "2026-08-23  15:13",
        "\"Why is the resumulation/replication of the work not matching with the results of "
        "the paper perfectly? Also, i would like you to thoroughly review the method and "
        "identify errors and gaps in relation to the claims they make in the paper "
        "(I do not think there are any, but would like you to check).\"",
        accent=PURPLE)

    quote_card(
        slide, Cm(11.9), Cm(8.3), Cm(20.6), Cm(2.6), "2026-08-23  17:31",
        "\"Please write this up as a separate document, in .md and then in a word and a pdf "
        "version. I will likely send this to one of the authors I know, so be thorough and "
        "precise, and describe what you did when reviewing.\"",
        accent=LILAC)

    # What in those two sentences did the work. This is the transferable part.
    column(slide, Cm(11.9), Cm(11.3), Cm(9.8), Cm(5.2), "Why the first one worked", [
        "It started from a concrete discrepancy, not \"review this paper\"",
        "It asked for method against claims — a checkable relation",
        "\"I do not think there are any\" — permission to come back empty",
    ], rule=TEAL, size=10)
    column(slide, Cm(22.7), Cm(11.3), Cm(9.8), Cm(5.2), "Why the second one worked", [
        "A named, real reader — an author I know — forced precision",
        "\"Describe what you did\" produced the method section, and with it the limits",
        "A document, not a chat answer: reviewable, and it can be wrong in public",
    ], rule=PINK, size=10)

    remove_empty_placeholders(slide)
    footer(slide, 2)


def slide_transfer(prs) -> None:
    """What someone else would need. Including what it does not do."""
    slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_TITLE_ONLY])
    headline(slide, [
        ("What someone else would need: ", INK),
        ("artefacts to check against, and a way to catch the model being wrong", PURPLE),
    ])

    column(slide, Cm(1.04), Cm(3.6), Cm(9.9), Cm(7.6), "Set-up, not prompting", [
        ("A working repository, not a chat", "The model ran the authors' code, re-analysed "
                                             "their deposit and compared both with our own "
                                             "build. Everything it claimed had an artefact "
                                             "behind it."),
        ("An agentic tool", "It has to be able to clone, run, read files and write documents "
                            "on its own — a chat window with a PDF pasted in cannot do this."),
        ("Time and compute", "Six days of preparation before the review prompt; the review "
                             "itself was an afternoon."),
    ], rule=BLUE, size=10.5)

    column(slide, Cm(11.6), Cm(3.6), Cm(9.9), Cm(7.6), "Prompt habits that mattered", [
        "Ask for verification against an artefact, never for an opinion of the work",
        "Give it a real reader, and say what it will be used for",
        "Say what you expect — and that finding nothing is an acceptable answer",
        "Ask it to describe its own procedure and what it did not do",
        "Make it tag every statement with its source",
        "Insist on a document you can send, in a format others can comment on",
    ], rule=TEAL, size=10.5)

    column(slide, Cm(22.2), Cm(3.6), Cm(10.3), Cm(7.6), "The honest limits", [
        "It asserted things that were wrong until checked — the value is in what it "
        "can be made to verify, not in what it says",
        "Our earlier conclusion that the mismatch was our own fault was itself an "
        "LLM conclusion, and it was wrong",
        "Scope has to be declared: one scenario of three, no re-run simulations, no "
        "human data, no contact with the authors",
        "A human sends it. I read every finding and decided what went to the author",
    ], rule=PINK, size=10.5)

    # The first render left a seven-centimetre hole between the columns and the
    # closing strip, so the strip moves up under the columns and the practical
    # question the room will actually ask — what did you run it with — gets the
    # space instead of white.
    tooling = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1.04), Cm(12.1), Cm(31.5), Cm(2.5))
    _plain(tooling, WHITE)
    tooling.line.color.rgb = RGBColor(0xD5, 0xD1, 0xC8)
    tooling.line.width = Pt(0.75)
    text(slide, Cm(1.5), Cm(12.45), Cm(30.6), Cm(1.9), [
        ("What it ran on, for anyone who wants to try it", 11.5, INK, True),
        ("An agentic coding assistant (Claude Code) working in a git repository on my own "
         "laptop, with the papers, the authors' code and the 3.1 GB deposit local to it. "
         "No special infrastructure and no Chalmers systems — but also nothing that a "
         "browser chat window could have done, because the findings come from running and "
         "re-analysing the artefacts. Every prompt I type is logged automatically, which is "
         "where slide 2 comes from.", 10.5, GREY, False, 4),
    ], spacing=1.14)

    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1.04), Cm(15.1), Cm(31.5), Cm(1.25))
    _plain(strip, BEIGE)
    tf = strip.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Cm(0.33)
    para = tf.paragraphs[0]
    for body_text, colour, bold in [
        ("Every statement in the review is tagged by source — ", INK, True),
        ("[Paper] [SI] [Code] [OSF] [Repo] [Opinion] — ", PURPLE, True),
        ("so a reader can see which claims rest on the artefacts and which are judgment",
         GREY, False),
    ]:
        run = para.add_run()
        run.text = body_text
        run.font.size = Pt(10.5)
        run.font.color.rgb = colour
        run.font.bold = bold
        run.font.name = FONT

    remove_empty_placeholders(slide)
    footer(slide, 3)


def add_notes(prs) -> None:
    """Speaker notes carry the provenance, so it travels with the file."""
    notes = [
        "Source: docs/method_review.md sections 1, 2 and 5. The three findings are in section 1; "
        "the ten code-vs-paper differences in section 5; the five questions in section 9. "
        "The deposit is osf.io/gs4bu, downloaded 2026-08-20. The 50 000-100 000 figure and the "
        "18-44% are from section 4.2, computed by replication/review_osf.py from the raw pickles. "
        "The point to land: the review was possible because the model could RUN the artefacts.",
        "Both prompts are verbatim from the prompt log, a UserPromptSubmit hook that writes one "
        "JSON line per prompt I type (project, machine, model, timestamp). Typos left in "
        "deliberately - the prompts were not crafted. The setup column is compressed from the "
        "prompts of 2026-08-17 to 08-20. If asked how long: first prompt 17 Aug, review prompt "
        "23 Aug.",
        "The limits column is the one to dwell on. The earlier wrong conclusion is in section 1 "
        "of the review: we had recorded that a discrepancy 'traces to a calibration-table "
        "limitation' - that was wrong, and the review overturned it. That is the argument for "
        "artefacts over assertions. Section 2.3 of the review lists what was not done; I did not "
        "write that list, the model did, on being asked to describe its procedure.",
    ]
    for slide, body in zip(prs.slides, notes):
        slide.notes_slide.notes_text_frame.text = body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path,
                        default=HERE / "LLM-in-depth-review-faculty.pptx")
    args = parser.parse_args()

    prs = Presentation(str(ensure_template()))
    drop_existing_slides(prs)

    slide_problem(prs)
    slide_prompts(prs)
    slide_transfer(prs)
    add_notes(prs)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(args.out))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
