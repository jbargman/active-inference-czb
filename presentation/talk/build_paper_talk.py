"""Build the 60-minute talk on the published active-inference driver model.

    python presentation/talk/make_paper_animations.py     # the seven videos first
    python presentation/talk/build_paper_talk.py [--out presentation/talk/ai_paper_talk.pptx]

Brief (Jonas, 2026-09-08): a presentation that describes active inference in the same
way and the same flow as the AUTHORS' edition of the handbook
(docs/handbook_authors/aif_driver_model_handbook.md), about the Nature Communications
paper and that handbook only, reusing what the other decks already have, with videos as
illustrations wherever they make it more pedagogic.

So the deck follows the handbook's own four parts and thirteen chapters, in order:

    I    01 where this comes from        02 one event through the model's eyes
    II   03 what the model is            04 scenario playbook
         05 normal versus critical       06 other agents and beliefs
         07 normative driving            08 the gaze system
    III  09 modify and validate          10 calibration and parameter fitting
    IV   11 code and data map            12 glossary        (13 is signposted, not slid)

Nothing from this project's comfort-zone program appears: no CZB framing, no gate/axis/
level, no R.1 or R.2. The two [Study] findings the authors' edition carries (the looming
channel against human intervention judgments, chapter 03; the glance gate blocking
observation but not inference, chapter 08) are included and labeled as ours and
unpublished, exactly as that edition does.

Seven slides carry video (.mp4 with PowerPoint's own controls, poster = first frame):
    event_anim         chapter 02, the whole event          (existing, transcoded)
    paper_loop         chapter 03, the loop and the account (new)
    belief_anim        chapter 03/06, the belief cloud      (existing, transcoded)
    paper_regimes      chapter 05, quiet and loud           (new)
    paper_maneuver     chapter 05, the escape by speed      (new)
    paper_tournament   chapter 06, the norm tournament      (new)
    paper_preference   chapter 07, the six terms            (new)

Every number on a slide traces to docs/handbook_authors/, to the tracked outputs under
replication/osf/, or to presentation/talk/paper_anim_numbers.md, which the animation
script regenerates from the deposit at build time.

IMPORTANT for a later session: once Jonas has reviewed or animated this deck by hand, do
NOT rerun this script onto the same file - copy the reviewed deck and augment the copy
(the chalmers-slide-generation-jonas skill; presentation/talk/README.md).
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

from build_talk import (  # noqa: E402  (shared helpers, theme colours and conventions)
    BEIGE, BLUE, BODY_TOP, BODY_W, DEEPPINK, DEEPTEAL, GREY, INK, MARGIN, MUTED,
    PURPLE, SLIDE_H, SLIDE_W, TEAL, WHITE, _plain, blank, body, column,
    divider, drop_existing_slides, ensure_template, find_figure, head, notes,
    panel, picture_fit, rule, table, text,
)

EMAIL = "jonas.bargman@chalmers.se"


def movie(slide, name, x, y, box_w, box_h):
    """Embed the animation as a MOVIE when an .mp4 sits beside the .gif, else a picture.

    An embedded GIF is played by PowerPoint as an image: no scrub bar, and pausing it
    restarts it from frame 0. add_movie with an H.264 .mp4 gets PowerPoint's own media
    controls instead. The poster is the animation's FIRST frame - a last-frame poster
    makes the slide wipe itself the instant the video is played.
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
        return slide.shapes.add_movie(
            str(mp4), left, top, w, h,
            poster_frame_image=str(poster) if poster.exists() else None,
            mime_type="video/mp4")
    print("NO .mp4 BESIDE", name, "- embedding the still instead")
    return slide.shapes.add_picture(str(path), left, top, width=w, height=h)


def caption(slide, line, y=16.15):
    # measured with measure_render.py: at y = 16.95 every video slide's two-line
    # caption ran into the footer strip at 18.06 cm
    text(slide, MARGIN, y, 30.0, 1.9, [(line, 12, GREY, False)])


def video_slide(prs, kicker, title, name, cap, minutes, script):
    """A video with one caption, set once. The caption is the hand-out's only clue.

    The video makes one point per slide, so the treatment is one caption, set once and
    never changing - the frozen frame in a printed hand-out has to carry the point on
    its own.
    """
    s = head(prs, title, kicker=kicker)
    movie(s, name, MARGIN, 3.55, BODY_W, 12.40)
    caption(s, cap)
    notes(s, minutes, script)
    return s


def tag(slide, x, y, label, colour):
    """The handbook's provenance tags, drawn as a small chip.

    The text colour follows the chip's luminance: accent5 blue is light enough that
    white on it is genuinely low contrast (check_slides.py flags it, correctly).
    """
    lum = (0.299 * colour[0] + 0.587 * colour[1] + 0.114 * colour[2]) / 255.0
    p = panel(slide, x, y, 2.35, 0.78, colour)
    text(slide, x + 0.16, y + 0.13, 2.1, 0.55,
         [(label, 11, INK if lum > 0.55 else WHITE, True)], align=PP_ALIGN.CENTER)
    return p


def build(out: Path) -> None:
    prs = Presentation(str(ensure_template()))
    drop_existing_slides(prs)

    # =====================================================================
    # opening
    # =====================================================================
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H))
    _plain(bg, PURPLE)
    rule(s, 2.3, 6.5, 3.2, TEAL, 5.0)
    text(s, 2.3, 7.4, 29.0, 5.2,
         [("The active-inference driver model", 36, WHITE, True),
          ("How it works, what it is made of, and how to change it", 20, MUTED, False, 14)],
         spacing=1.14)
    text(s, 2.3, 14.6, 29.0, 2.6,
         [("A reader's walk through Schumann, Engström, Johnson, O'Kelly, Messias, "
           "Kober & Zgonnikov (2026), Nature Communications", 13, WHITE, False),
          ("Jonas Bärgman · Chalmers University of Technology · " + EMAIL,
           12.5, MUTED, False, 8)])
    notes(s, 0.3, """
Welcome. This hour is about one model: the active-inference collision-avoidance driver
model published in Nature Communications this year, and the companion handbook we wrote
while trying to understand it well enough to build on it.

I want to be clear about what this talk is and is not. It is not my model, and it is not
a critique. It is a careful outside reading, laid out in the order that we found made it
learnable. Everything I show you is either in the paper, in its Supplementary
Information, in the released code, or in the authors' own deposited simulation output -
and I will tell you which, every time.

Two places where I show results of our own, I will say so explicitly and flag that they
are unpublished.
""")

    s = head(prs, "What this talk is built from, and how to read the claims",
             kicker="orientation")
    body(s, [
        ("The article.", "Schumann et al. (2026), Nature Communications 17:5009 - the "
                         "model, three scenarios, and the held-out test"),
        ("The Supplementary Information.", "where most of the actual definitions live; "
                                           "SI §2.2-2.5, Eqs. 44-52"),
        ("The released code.", "github.com/tud-hri/Active-Inference-Collision-Avoidance - "
                               "the ground truth wherever the paper is ambiguous, and in "
                               "a few places more precise than the SI"),
        ("The OSF deposit.", "the authors' own simulation output for all three scenarios, "
                             "32 seeds per run - which is why this talk can show real "
                             "numbers instead of sketches"),
    ], y=BODY_TOP + 0.1, size=14.5)
    y0 = 12.5
    text(s, MARGIN, y0 - 0.9, BODY_W, 0.8,
         [("Every claim in the handbook carries its source as a tag:", 13, INK, True)])
    for i, (lab, col) in enumerate([("[Paper]", PURPLE), ("[SI]", BLUE),
                                    ("[Code]", DEEPTEAL), ("[OSF]", DEEPPINK),
                                    ("[Opinion]", GREY)]):
        tag(s, MARGIN + i * 2.75, y0, lab, col)
    text(s, MARGIN, y0 + 1.25, BODY_W, 1.4,
         [("[Opinion] marks our readings and judgments, so they cannot be mistaken for the "
           "authors' claims. A sixth tag, [Study], marks two findings of our own - "
           "unpublished, and flagged again when they appear.", 12.5, GREY, False)])
    notes(s, 1.2, """
Four sources, and they do not agree in every detail.

The one worth dwelling on is the deposit. The authors deposited the complete simulation
output - every run, every seed, per-timestep. That changes what a reading like this can
be: instead of arguing about what the model probably does, you can open the file and
look. Most of the numbers in this talk are the authors' own output, recomputed.

The tags matter because the sources genuinely disagree in places. Where the code and the
SI differ, I will say so, and I will tell you which one the released model actually runs.

CUTTABLE if running long: the tag row can be skipped and mentioned in passing.
""")

    s = head(prs, "Two words that do not mean what they usually mean",
             kicker="a warning before we start")
    panel(s, MARGIN, BODY_TOP + 0.3, 15.0, 5.6, BEIGE)
    text(s, MARGIN + 0.8, BODY_TOP + 0.9, 13.4, 4.6,
         [("Surprise", 20, PURPLE, True),
          ("Not an emotion. A number: how far what is happening departs from what the "
           "model expected. A state can carry surprise the driver would never report "
           "feeling. Read it as mismatch.", 14, INK, False, 10)], spacing=1.14)
    panel(s, MARGIN + 16.2, BODY_TOP + 0.3, 15.0, 5.6, BEIGE)
    text(s, MARGIN + 17.0, BODY_TOP + 0.9, 13.4, 4.6,
         [("Preference", 20, PURPLE, True),
          ("Not a choice and not a ranking. A probability distribution over futures, "
           "saying which ones are treated as unremarkable. Wanting and expecting are "
           "deliberately the same object.", 14, INK, False, 10)], spacing=1.14)
    text(s, MARGIN, 11.6, BODY_W, 4.0,
         [("And three more, for later:", 14, INK, True),
          ("Reward — the file is called reward.py, but nothing is learned by trial and "
           "error. It computes log-preference.", 13.5, INK, False, 10),
          ("Norm — not a traffic rule. A description of what other agents typically do, "
           "used for prediction. A violated norm is information, not an offense.",
           13.5, INK, False, 6),
          ("Optimal — almost never applies. The planner is deliberately budgeted, and the "
           "model's humanlikeness partly depends on its suboptimality.",
           13.5, INK, False, 6)])
    notes(s, 0.9, """
If you take nothing else from the first ten minutes, take these two.

Almost every confused conversation I have had about this literature traces back to one of
them. Someone hears "the driver is surprised" and pictures a startle response. Someone
hears "preference" and pictures a choice, or a utility ranking, and then asks how the
model decides between preferences - which is not a question this framework has, because
preferences are a distribution, not a list.

The third one, reward.py, catches code readers specifically. There is a file called
reward.py and there is no reinforcement learning anywhere in this model.
""")

    # =====================================================================
    # PART I - where this comes from
    # =====================================================================
    divider(prs, "I", "Where this comes from",
            "Handbook chapters 01 and 02: the lineage, what free energy actually means, "
            "and then one complete event through the model's eyes.")

    s = head(prs, "The idea in one paragraph", kicker="chapter 01")
    text(s, MARGIN, BODY_TOP + 0.4, 30.0, 6.0,
         [("The brain is not a camera followed by a calculator. It is a prediction "
           "machine.", 21, PURPLE, True),
          ("It continuously guesses what its senses are about to report, compares the "
           "guess with what arrives, and treats the difference — the surprise — as the "
           "thing to get rid of.", 16, INK, False, 12)], spacing=1.16)
    y = 11.4
    column(s, MARGIN, y, 14.4, 4.4, "There are only two ways to get rid of it",
           ["Change your mind — update beliefs until they fit the world. "
            "This is perception.",
            "Change the world — act until it fits your beliefs. This is action."],
           colour=PURPLE, size=14)
    column(s, MARGIN + 16.2, y, 14.4, 4.4, "Why that is the whole point",
           ["Active inference says these are not two systems but one operation running "
            "in two directions.",
            "So detecting a braking lead vehicle and pressing the brake pedal are, "
            "literally, the same computation."],
           colour=DEEPTEAL, size=14)
    notes(s, 1.2, """
This is the entire idea, and everything else in the hour is machinery for making it
runnable.

Pause on the last line, because it is the claim that makes the framework worth the
trouble. In a classical driver model, detection is one module with its own parameters,
and the response is a different module with its own parameters, and you fit them
separately. Here they are the same operation pointed in two directions. That is why the
model gets response times without a response-time parameter - which we will watch happen
in about ten minutes.
""")

    s = head(prs, "A short history, told through what each step added",
             kicker="chapter 01")
    picture_fit(s, "lineage_talk.png", MARGIN, 3.7, BODY_W, 9.0, border=False)
    text(s, MARGIN, 13.1, BODY_W, 3.6,
         [("Helmholtz (1860s) — perception is a guess built from expectation plus "
           "evidence.   The Bayesian brain (1990s) — the guessing gets arithmetic, and "
           "reliability decides how far evidence moves you.   Predictive processing "
           "(2000s) — it becomes an architecture: a generative model minimizing "
           "prediction error at every level.", 13, INK, False),
          ("Active inference (2010s) — the second direction is added, through the "
           "preference prior: the futures the agent wants are the futures it expects, so "
           "goal-seeking becomes surprise-avoidance.   This model (2024–2026) — the "
           "framework made into a runnable model of drivers in safety-critical "
           "situations.", 13, INK, False, 8)])
    notes(s, 1.5, """
Four steps, and each one adds exactly one thing.

For this audience the step worth naming is predictive processing, because it is not an
imported idea in driving research. Great Expectations - Engström, Bärgman, Nilsson,
Seppelt, Markkula, Piccinini and Victor, 2018 - laid out a predictive-processing account
of driving before this model line existed. The way we read it, and this is our reading
rather than the authors' claim, the Schumann model is the computational instantiation of
the account that paper gave verbally.

I should declare an interest: I am a co-author of that paper.
""")

    s = head(prs, "“Free energy,” demystified in one page", kicker="chapter 01")
    panel(s, MARGIN, BODY_TOP + 0.2, BODY_W, 3.1, BEIGE)
    text(s, MARGIN + 0.8, BODY_TOP + 0.65, 29.5, 2.4,
         [("A computable score of how badly your model of the world is doing, given what "
           "you are sensing. High score, poor fit. Low score, good fit.", 17, PURPLE, True)],
         spacing=1.12)
    text(s, MARGIN, 8.5, BODY_W, 1.8,
         [("The word “energy” is a historical accident — the formula has the same "
           "shape as a quantity in statistical physics, so the name was borrowed. Nothing "
           "thermodynamic is meant. Substitute “model-misfit score” and you lose "
           "nothing.", 14, INK, False)])
    y = 11.0
    column(s, MARGIN, y, 14.4, 4.8, "Present-tense misfit",
           ["How badly current beliefs fit current sensations.",
            "Minimizing it is perception — the belief update.",
            "(variational free energy)"], colour=BLUE, size=13.5)
    column(s, MARGIN + 16.2, y, 14.4, 4.8, "Future-tense misfit",
           ["How badly a candidate plan is expected to fit the preferred future.",
            "Minimizing it is action selection.",
            "(expected free energy)"], colour=DEEPPINK, size=13.5)
    notes(s, 1.5, """
This is the term that costs the framework readers, so it is worth one slide.

The split at the bottom is not decoration - it organizes the entire model. Everything on
the left is the particle filter, which we will meet in chapter 6. Everything on the right
is the planner and the accumulator. When you read the code, every file belongs to one
side or the other.

If someone in your group insists free energy means something thermodynamic: it does not,
and no argument in this model depends on the analogy.
""")

    s = head(prs, "Models you already know, and where they sit inside this one",
             kicker="chapter 01")
    body(s, [
        ("Evidence accumulation / drift-diffusion.", "The response timing IS an "
         "accumulator. The difference: the accumulation rate is not a fitted constant, it "
         "is the moment-by-moment surprise the driver's own predictions compute — so "
         "response times depend on kinematics, urgency and expectation automatically"),
        ("Looming and visual threshold models.", "The model sees optical size and "
         "expansion, with a detection threshold on expansion. Detection delay emerges "
         "from perception rather than being a fitted reaction-time constant"),
        ("Driver risk field / safety margin models.", "The preference prior is a "
         "landscape over states — which situations are normal and which are increasingly "
         "unacceptable. That landscape plays the role of a risk field"),
        ("Motivational theories.", "Zero-risk, task-capability, task-difficulty "
         "homeostasis all describe drivers regulating toward a comfortable region. Here "
         "the region is explicit: where predicted futures match preferred ones"),
    ], y=BODY_TOP, size=13.5)
    text(s, MARGIN, 15.9, BODY_W, 1.4,
         [("The model is best understood not as a rival to the models you already use, "
           "but as a container that holds versions of them", 14, PURPLE, True)])
    notes(s, 1.5, """
This slide is the one I would keep if I could keep only one from chapter 1, because it is
what makes the framework worth an hour of a busy person's time.

Each of these four is a research tradition this room knows. The claim is not that active
inference beats them. It is that it contains recognizable versions of all four, computed
from one objective - so you do not have to arbitrate between a threshold model, an
accumulator model and a risk field. They are different readings of the same machinery.

The accumulator line is the sharpest. Markkula's models have a drift rate you fit. Here
the drift rate is computed from the driver's own predictions, which means it varies
within a trial as the situation develops.
""")

    s = head(prs, "For contrast with the paradigms we grew up with", kicker="chapter 01")
    table(s, MARGIN, BODY_TOP + 0.2, [8.6, 8.2, 14.4], [
        ["Paradigm", "The driver is…", "Where it differs"],
        ["Stimulus–response / threshold", "a trigger waiting for a cue",
         "no expectations; response times must be fitted per situation"],
        ["Information processing", "a pipeline of stages",
         "stages are separate boxes; here perception, decision and timing share one currency"],
        ["Ecological psychology", "attuned to optical invariants",
         "closer than it looks — looming IS an optical invariant; this adds explicit "
         "beliefs and preferences behind the optics"],
        ["Optimal control", "a perfect planner with a cost function",
         "here planning is deliberately bounded, and the “cost function” is a "
         "probability distribution — which is what lets surprise time the response"],
        ["Reinforcement learning", "a reward maximizer trained by experience",
         "no reward signal exists; preferences are built in, not learned, and "
         "information-seeking comes for free"],
    ], size=12, row_h=2.05)
    notes(s, 1.2, """
Use whichever row matches the person asking.

The two that come up most: optimal control, and reinforcement learning.

Against optimal control, two differences do real work. The cost function is a probability
distribution, which is what lets the same object define surprise and hence timing; and the
planner is deliberately budgeted, which is where the human character of the maneuvers
comes from. An optimal-control reading also has no native account of information-seeking.

Against RL: nothing is learned across episodes. There is no training loop. The
resemblance is only that both talk about value.

CUTTABLE - this table can be left for the reader if time is short.
""")

    s = head(prs, "What are we being asked to believe?", kicker="chapter 01 · the debate")
    y = BODY_TOP + 0.3
    for i, (n, ttl, txt, col) in enumerate([
        ("1", "A process theory of the brain",
         "Neurons literally implement these computations. A serious neuroscience program "
         "with real but contested evidence. Nothing here depends on it.", GREY),
        ("2", "A universal principle of life",
         "Every self-organizing system minimizes free energy — argued in its strongest "
         "form as near-mathematical necessity. Critics: a principle compatible with "
         "everything predicts nothing. We take no position.", GREY),
        ("3", "An engineering framework",
         "A recipe for agents that carry uncertainty honestly, unify goal- and "
         "information-seeking, and time actions by surprise. This is the only claim the "
         "driver model needs — and it is testable the ordinary way.", PURPLE),
    ]):
        h = 3.55
        panel(s, MARGIN, y, BODY_W, h, BEIGE if col is PURPLE else WHITE)
        rule(s, MARGIN + 0.5, y + 0.5, 0.9, col)
        text(s, MARGIN + 0.5, y + 0.85, 28.0, h - 1.0,
             [(f"{n}.  {ttl}", 15.5, col, True),
              (txt, 13, INK, False, 6)], spacing=1.1)
        y += h + 0.35
    text(s, MARGIN, 16.6, BODY_W, 1.2,
         [("The published model is squarely a use of claim 3, and its strongest card is "
           "conventional science: the intersection scenario was never used for tuning, and "
           "the model still predicted human response patterns there", 13.5, PURPLE, True)])
    notes(s, 1.2, """
Active inference arrives with a large and sometimes heated literature attached, and it is
fair for a new reader to ask what they are signing up for. Three distinct claims travel
under one name, and they deserve different levels of commitment. This split is our
reading, not the authors'.

You can use everything in this talk while remaining completely agnostic about claims 1
and 2. I want to be emphatic about that, because in my experience the philosophy is what
stops practical people engaging.

The honest counterpoint, which I will not hide: with a hand-built preference function and
thirteen tuned parameters, "the model can be made to fit" is a fair worry. The defense is
held-out prediction and ablation - and the paper does both, and you can now reproduce
both from the deposit.
""")

    s = head(prs, "One event, from the authors' own deposited run",
             kicker="chapter 02", sub="Rear-end scenario, experiment 7, random seed 0 — "
                                      "nothing sketched or idealized")
    y = 5.2
    column(s, MARGIN, y, 9.6, 10.5, "The cast",
           ["Two vehicles, straight road, both at 10 m/s.",
            "A 10 m gap — exactly one second of headway.",
            "The lead is a puppet: at a scripted moment it brakes at 6 m/s² to a "
            "standstill, and ignores our driver completely."], colour=GREY, size=13)
    column(s, MARGIN + 10.7, y, 9.6, 10.5, "What our driver has",
           ["Senses — an optical silhouette that grows or shrinks. Not the gap in metres.",
            "Beliefs — 75 simultaneous hypotheses about the state of the world.",
            "Preferences — a quiet notion of how this drive is supposed to go.",
            "A plan — 6 seconds of intended pedal and steering. Currently: do nothing."],
           colour=PURPLE, size=13)
    column(s, MARGIN + 21.4, y, 9.6, 10.5, "And one account",
           ["A running total that fills with evidence that the current plan is no longer "
            "delivering the preferred future.",
            "It is the thing to watch. Everything interesting in the next four minutes "
            "happens inside our driver's head."], colour=DEEPPINK, size=13)
    notes(s, 0.9, """
Set the scene before playing the film, because once it is running you want them watching
the account, not reading.

The most important word on this slide is "puppet". The lead vehicle has no intelligence,
does not perceive our driver, and never reacts. Every published result in this paper is
about unilateral avoidance. That is a real scope limit and I will come back to it.

The second most important: our driver does not know the script.
""")

    video_slide(prs, "chapter 02", "The event, moment by moment", "event_anim.gif",
                "The authors' own deposit: vehicle states, executed pedal and re-plan flag "
                "read from the deposited arrays; the account reconstructed with the run's "
                "own λ = 10⁻⁵·⁹⁵ and threshold 1. Re-plan at 1.4 s, brake at 1.6 s, final "
                "gap 2.05 m.", 2.5, """
Play it once without talking, then play it again narrating.

t = 0 to 0.6 - steady following, and note the account is ALREADY climbing. Come back to
that; it surprises people.

t = 0.8 - the lead brakes. Watch the belief cloud: it has already snapped to the new
reality in the very next update. The model has detected the braking essentially
immediately. Detection is not the bottleneck.

t = 0.8 to 1.2 - knowing is not acting. The plan is still "keep cruising". A plan is not
abandoned because the world changed; it is abandoned when it stops delivering the
preferred future. The per-step deposit roughly quadruples over these steps.

t = 1.4 - the account is full. For exactly one timestep the model does the expensive
thing: discards the plan, generates fresh candidates, scores them, keeps the best. There
is precisely one re-plan in the whole trial.

t = 1.6 - the brake reaches the wheels. Response time 0.8 s, of which detection took at
most one 0.2 s step.

Then it rides it out and stops 2.05 m behind.
""")

    s = head(prs, "Three things to take from that", kicker="chapter 02")
    y = BODY_TOP + 0.2
    for n, ttl, txt in [
        ("1", "Detection and response are different things, and the model separates them",
         "The cloud caught the braking within one step; the response came 0.6 s later, "
         "when the plan — not the world — had accumulated evidence of failure. Drivers "
         "rarely miss that something moved; what takes time is concluding that their "
         "current course of action has stopped being adequate."),
        ("2", "The account drifts even in steady following",
         "The accumulated quantity is an expectation over noisy imagined futures, and it "
         "is not zero inside comfortable following. Response timing in a conflict starts "
         "from a non-zero baseline that depends on the pre-conflict gap. We will put "
         "numbers on that in chapter 05."),
        ("3", "One mechanism produced the whole episode",
         "Steady following, detection, response timing, braking style and the "
         "come-to-rest margin all came out of one loop — sense, believe, predict, "
         "evaluate, act, accumulate — with no per-phase sub-model. What that loop is made "
         "of is chapter 03."),
    ]:
        panel(s, MARGIN, y, BODY_W, 4.05, BEIGE)
        text(s, MARGIN + 0.55, y + 0.45, 1.4, 1.2, [(n, 24, PURPLE, True)])
        text(s, MARGIN + 2.2, y + 0.5, 27.8, 3.2,
             [(ttl, 15, PURPLE, True), (txt, 12.8, INK, False, 6)], spacing=1.1)
        y += 4.35
    notes(s, 1.5, """
Point 1 is the one to press with a human-factors audience, because it matches what the
literature says about drivers, and it comes out of the architecture rather than being
built in.

Point 2 is the one that surprises modelers, and it has a practical consequence: if you
run this model with a long benign run-in, the accumulator will eventually re-plan on its
own with nothing happening. The published simulations do not show it because they start
0.8 s before the lead brakes.

Point 3 is the structural claim, and the rest of the talk unpacks it.
""")

    # =====================================================================
    # PART II - what the model is
    # =====================================================================
    divider(prs, "II", "What the model is",
            "Handbook chapters 03 to 08: the loop and its components, what changes "
            "between scenarios, normal versus critical, beliefs about other agents, "
            "what defines normal, and the gaze system.")

    video_slide(prs, "chapter 03", "The loop — everything happens inside it",
                "paper_loop.gif",
                "The ring is schematic; the account on the right plays the authors' own "
                "per-step deposits from Exp_7, seed 0. Quiet following deposits about "
                "70 000 units a step, roughly 8% of the threshold; after the lead brakes, "
                "131 000, then 197 000, then 249 000.", 2.2, """
One loop, five times a second, and there is no second architecture anywhere in the model.

Walk the ring once with the video: sense the world through looming vision; update a cloud
of hypotheses; roll each hypothesis a few seconds into the future; check the current plan
against the preferred future; execute the plan's next step; and deposit whatever
shortfall the check revealed.

Then the account. The right-hand bar is not a cartoon - those are the authors' own
per-step numbers. Note that the quiet deposit is not zero. Note that when the lead brakes
nothing switches on: the same six boxes run, and the deposits simply get bigger.

When the account crosses its threshold, and only then, the model builds a new plan from
scratch. That gate is the whole response-timing mechanism.
""")

    s = head(prs, "The components, as input → output boxes", kicker="chapter 03")
    left = [
        ("1  The world", "two vehicles with bicycle physics, a road, and a scripted other "
                         "vehicle. The driver never sees this directly"),
        ("2  The senses", "true state → optical angle and its rate, plus own-vehicle "
                          "signals. Noise grows with distance; expansion below 0.00215 s⁻¹ "
                          "is invisible, so detection distance emerges"),
        ("3  Beliefs", "75 weighted hypotheses. The cloud's spread IS the model's "
                       "uncertainty — there is no separate confidence number"),
    ]
    right = [
        ("4  Prediction", "every particle rolled 6 s forward; the other vehicle's imagined "
                          "moves are norm-weighted, not raw noise"),
        ("5  Preferences", "an imagined future → a score of how preferred it is. Six "
                           "independent terms"),
        ("6  The planner", "ordinarily the plan is only patched. A full re-plan — 100 "
                           "candidates, elite half, 20 rounds — runs only when the account "
                           "demands it"),
        ("7  The account", "the shortfall × a rate constant, added to a running total. "
                           "Threshold → re-plan → reset"),
    ]
    body(s, left, x=MARGIN, y=BODY_TOP, w=15.0, size=12.5)
    body(s, right, x=MARGIN + 16.2, y=BODY_TOP, w=15.0, size=12.5)
    notes(s, 1.5, """
Seven boxes. Everything in the released code is one of these.

Two details worth flagging because they are easy to misread.

Box 6, the planner: the first edition of our handbook got this wrong and we corrected it
on 3 September. The released planner transforms its nominal elite fraction of 0.1 into
0.5 before using it, so 50 of 100 plans are elite, not 10; and it doubles its 10
iterations to 20 around a full re-plan. The SI's 20 and the paper's 10 are both right,
for different calls.

Box 6 again: the budget is deliberately capped, so the planner sometimes returns a merely
decent plan. That is a modeling commitment about humans, not a bug.
""")

    video_slide(prs, "chapters 03 and 06", "The belief cloud, catching the lead's braking",
                "belief_anim.gif",
                "The deposit's per-timestep arrays for the same run. Left: the 75 "
                "particles' believed lead speed, weights as marker size. Right: the "
                "account filling. The cloud moves at 0.8 s; the pedal moves at 1.6 s — the "
                "gap between them is evidence, not perception.", 1.9, """
This is the same event as before, but looking only at the working memory.

The point is the timing of the two panels. The cloud snaps within one 0.2 s step. The
pedal moves 0.8 s later. Everything in between is the accumulator, and that is the
model's account of response time.

Two honest caveats that are stated in the frame: the x axis is believed lead SPEED rather
than believed gap, because in this configuration the gap is effectively observed - the
particle spread is about a millimetre, so it shows no collapse worth animating. And the
deposited weights are uniform because they are post-resampling.

Where the cloud really earns its keep is ambiguity, which this scenario does not have
much of. When an oncoming vehicle wanders near a lane line, hypotheses for "drifting but
staying" and "beginning an incursion" coexist with real weight on both, and planning sees
both futures. A single-best-estimate tracker is structurally unable to be of two minds.
""")

    s = head(prs, "Two currencies, one ledger", kicker="chapter 03")
    y = BODY_TOP + 0.5
    panel(s, MARGIN, y, 15.0, 5.6, BEIGE)
    text(s, MARGIN + 0.7, y + 0.6, 13.6, 4.6,
         [("Pragmatic value", 19, PURPLE, True),
          ("How well an imagined future matches the preferred one. Goal-seeking: "
           "progress, comfort, safety margins.", 14, INK, False, 10)], spacing=1.14)
    panel(s, MARGIN + 16.2, y, 15.0, 5.6, BEIGE)
    text(s, MARGIN + 16.9, y + 0.6, 13.6, 4.6,
         [("Epistemic value", 19, DEEPTEAL, True),
          ("How much an imagined future is expected to teach the model, by reducing the "
           "cloud's spread where it matters. Information-seeking: looking, probing, "
           "easing off to see what the other driver does.", 14, INK, False, 10)],
         spacing=1.14)
    text(s, MARGIN, 12.4, BODY_W, 4.2,
         [("Both are measured in the same units and simply added.", 17, PURPLE, True),
          ("So caution and progress trade against each other without an arbitration rule — "
           "which is the framework's main selling point, and the thing that is genuinely "
           "hard to get from any of the models on the earlier slide.", 14, INK, False, 10),
          ("In the published collision-avoidance runs the pragmatic part dominates. The "
           "epistemic part is the natural hook for glance behavior — chapter 08.",
           13, GREY, False, 10)])
    notes(s, 1.2, """
If you are going to steal one idea from active inference for your own modeling, steal
this one.

The usual way to build a driver model that both makes progress and gathers information is
to write two objectives and then write a rule for arbitrating between them - and that
arbitration rule is where all the free parameters and all the arguments live. Here they
are in the same units and you add them. The trade-off is a consequence, not a setting.

In these particular runs the pragmatic term dominates, so do not oversell the epistemic
part on the strength of this paper. It does real work in the 2024 paper in this line,
which is about uncertainty and looking.
""")

    s = head(prs, "What is deliberately human about it — and what it is not",
             kicker="chapter 03")
    table(s, MARGIN, BODY_TOP, [13.0, 18.2], [
        ["Design choice", "The human claim behind it"],
        ["Looming instead of range sensors",
         "drivers see angles, not odometry; distant threats are genuinely harder to perceive"],
        ["A particle cloud instead of one estimate",
         "drivers entertain multiple readings of an ambiguous scene at once"],
        ["Norm-shaped prediction",
         "drivers expect others to behave; trust is withdrawn when behavior stops earning it"],
        ["A capped planning budget",
         "drivers satisfice; an optimal planner reproduces the wrong behavior"],
        ["Surprise-gated re-planning",
         "drivers do not continuously re-decide; they act when evidence has built up"],
    ], size=12.5, row_h=1.35)
    y = 12.1
    column(s, MARGIN, y, 15.0, 4.6, "What it is NOT",
           ["Not learned from data — no training set, no fitted network. Thirteen "
            "parameters were hand-tuned; the rest is structure.",
            "Not an optimal controller — bounded planning, noisy perception and normative "
            "trust are deliberate departures."], colour=DEEPPINK, size=12.5)
    column(s, MARGIN + 16.2, y, 15.0, 4.6, " ",
           ["The other vehicle is not intelligent — it follows a script and never reacts. "
            "No negotiation, no interaction.",
            "Not fast — written for GPU. On CPU one batched timestep has cost us anywhere "
            "from under a second to tens of seconds. [Study]"], colour=DEEPPINK, size=12.5)
    notes(s, 1.5, """
The left column is the case for the model. The right column is what you must not claim
for it.

The scripted-other-vehicle limit is the one that matters most for anyone here thinking
about interaction studies. There is no negotiation in this model, and no recursive "they
see me seeing them". Any interaction work needs that script replaced.

The speed point is ours and unpublished, and it is a practical warning: plan batches to be
restartable and measure before extrapolating. The variation between runs is wide with no
clean predictor.
""")

    s = head(prs, "One driver, many worlds", kicker="chapter 04",
             sub="Diffing the authors' own setup tables across all three scenarios — "
                 "65 parameters per run")
    panel(s, MARGIN, 5.3, BODY_W, 3.4, BEIGE)
    text(s, MARGIN + 0.8, 5.8, 29.5, 2.6,
         [("Everything describing the driver — perception noise, looming threshold, "
           "preference weights, planning budget, evidence accumulation, particle counts — "
           "is identical across all three scenarios, with exactly one exception.",
           15.5, PURPLE, True)], spacing=1.12)
    text(s, MARGIN, 9.3, BODY_W, 1.0,
         [("What changes is the world. The same conclusion appears at file level: a "
           "scenario is a package of three files, and only three.", 14, INK, False)])
    table(s, MARGIN, 10.9, [7.6, 11.0, 12.6], [
        ["File", "Job", "In plain terms"],
        ["dynamics_true.py", "the world's physics and the other vehicle's script",
         "what really happens — 162, 354 and 665 lines; the spread is all script"],
        ["decoder_true.py", "how true state becomes observations",
         "what can be seen — identical in all three but for docstrings"],
        ["reward.py", "the preference terms and the norms that are scenario-shaped",
         "what counts as normal here — the only file where the scenario changes the driver"],
    ], size=12, row_h=1.55)
    notes(s, 1.5, """
This is, we think, the model's strongest structural claim: one driver, many worlds.

The evidence is not rhetorical - it is a column-by-column diff of the authors' own setup
tables. Of 65 configuration parameters, every driver-side one is identical across
rear-end, oncoming and intersection. Every preference weight, every perception noise, the
looming threshold, the accumulation settings.

And it is what makes the held-out intersection test meaningful. The driver that handled
the rear-end scenario was dropped into a new world, not re-engineered for it.

One naming trap for anyone reading the code: the intersection scenario is called "side" at
top level and "intersection" inside src/. Searching for one name finds half the code.
""")

    s = head(prs, "The one driver-side change, and what it means",
             kicker="chapter 04")
    panel(s, MARGIN, BODY_TOP + 0.4, BODY_W, 4.4, BEIGE)
    text(s, MARGIN + 0.9, BODY_TOP + 0.95, 29.4, 3.5,
         [("w_sd_model  —  how much steering wobble the driver's internal model attributes "
           "to the OTHER vehicle when imagining its futures", 16, PURPLE, True),
          ("0.0045 in rear-end   ·   0.4575 in both lateral scenarios   ·   a factor of "
           "one hundred", 15, INK, False, 8)], spacing=1.12)
    text(s, MARGIN, 10.4, BODY_W, 5.4,
         [("This is not a perception setting. It is an assumption inside the driver's head "
           "about what kind of agent it is facing: a lead in a queue does not steer; an "
           "oncoming or crossing vehicle might.", 14.5, INK, False),
          ("It is the single number by which the driver was told what type of situation it "
           "is in.", 15, PURPLE, True, 12),
          ("Whether a future version could infer this rather than be told is, to us, an "
           "open and interesting question.  [Opinion]", 13.5, GREY, False, 12)])
    notes(s, 0.9, """
I like this slide because it is the one place where the "one driver, many worlds" claim
has to be qualified, and the qualification is itself interesting.

There is exactly one driver-side number that differs, and it is not a tuning constant -
it is a statement about what kind of thing the driver believes it is looking at. A
hundred-fold difference in assumed steering variability between "a lead in a queue" and
"an oncoming vehicle".

The obvious research question, and it is ours rather than the authors': could the model
infer the agent type from observation instead of being told? That is a genuinely
interesting extension, and it is one of the few places where the architecture has an
obvious gap that is not just missing engineering.
""")

    s = head(prs, "The switching checklist — moving to a new scenario",
             kicker="chapter 04")
    body(s, [
        ("1  Stage the world.", "geometry, lanes, initial states, desired speed, episode "
                                "length"),
        ("2  Script the other agent.", "trigger condition and maneuver, intensity as a "
                                       "sweepable parameter"),
        ("3  Check observability.", "same looming channel? A pedestrian subtends different "
                                    "angles than a truck. Note the released applicability "
                                    "tests are binary — a target partly in the lane is "
                                    "all-or-nothing to the driver"),
        ("4  Draw the lane structure into the preferences.", "what lateral positions mean "
                                                             "on this road. Hand geometry; "
                                                             "there is no map format"),
        ("5  Write the other agent's norms.", "what does normal look like for that agent "
                                              "here? The most judgment-heavy step, and it "
                                              "shapes how paranoid predictions are"),
        ("6  Set the assumed variability.", "the w_sd_model dial for the new agent type"),
        ("7  Re-calibrate the safety assumption.", "and confirm the calibration covers the "
                                                   "intended speed and headway range"),
        ("8  Define the measurements.", "response onset, collision, condition grid — so "
                                        "results stay comparable"),
    ], y=BODY_TOP, size=12.5, gap=7)
    text(s, MARGIN, 16.4, BODY_W, 1.2,
         [("Steps 1–3 are days. Steps 4–7 are where the scenario's scientific content "
           "lives, and skipping the argument for any of them produces a model that runs "
           "but persuades nobody  [Opinion]", 13, PURPLE, True)])
    notes(s, 1.2, """
This is the chapter's practical payload, and it is the slide to photograph if you are
going to port this model.

The line at the bottom is the honest summary of effort. Items 1 to 3 are mechanical. Items
4 to 7 are modeling judgments that deserve an explicit argument in any write-up, because
they are where a reviewer will push.

Item 5 is the hardest and I will come back to it in chapter 7: writing a new scenario's
norms amounts to answering "what is the earliest observable sign, in this geometry, that
the other agent has stopped being ordinary?"
""")

    s = head(prs, "There is no emergency mode", kicker="chapter 05")
    text(s, MARGIN, BODY_TOP + 0.3, BODY_W, 2.6,
         [("No flag flips from “normal” to “critical”. No emergency "
           "sub-model wakes up. The loop runs identically at every timestep of every "
           "drive.", 18, PURPLE, True)], spacing=1.14)
    y = 8.0
    column(s, MARGIN, y, 15.0, 8.4, "The quiet regime",
           ["The account drifts, slowly — the plan works in most rollouts, but the "
            "imagined spread always contains a few that end too close.",
            "Planning is incremental — the plan is shifted and patched; the expensive "
            "machinery is dormant.",
            "Trust is extended — the other vehicle has been behaving, so predictions "
            "concentrate on norm-following futures.",
            "The gentle terms shape behavior — speed, pedal smoothness, lane centring."],
           colour=DEEPTEAL, size=12.5)
    column(s, MARGIN + 16.2, y, 15.0, 8.4, "The loud regime — the same four, inverted, in "
                                           "a fixed causal order",
           ["Trust is withdrawn FIRST — the norm conditioning releases the prediction "
            "tail, before any decision is made.",
            "The heavy preference terms wake — collision and eroded safety margins begin "
            "to dominate the scoring.",
            "The account fills — this is where response time comes from.",
            "One expensive re-plan fires, executed by the same bounded planner as always."],
           colour=DEEPPINK, size=12.5)
    notes(s, 0.9, """
The most useful single fact in this chapter, and a substantive claim about drivers
inherited from the zero-risk tradition: emergency response is ordinary regulation, pushed
hard.

The ordering in the right column is worth emphasising because it is testable. Trust is
withdrawn FIRST, in the belief and prediction machinery, before any decision is made.
Expectation revision precedes action - which is what the predictive-processing account
says should happen.

The practical consequence, for anyone using the model: the normal-driving regime is not
free. The same machinery that produces crisp emergency behavior must also idle plausibly,
and misconfigured preferences show up first as fidgety normal driving.
""")

    video_slide(prs, "chapter 05", "Quiet and loud are the same machine",
                "paper_regimes.gif",
                "Left: the account through the chapter-02 run — already 0.28 full when the "
                "lead brakes. Right: all 28 baseline conditions. Pre-onset drift runs from "
                "2.6% of the threshold per 0.8 s at the longest gap to 44.3% at the "
                "shortest. Both computed from the deposit.", 2.2, """
Two panels, one claim.

On the left, the run you already know, with the account drawn out. The thing to notice is
the shaded part before the lead brakes: the account is 0.28 of the way to a re-plan before
anything has happened.

On the right is why that is not a quirk of one run. Every one of the 28 baseline
conditions, and the drift grades smoothly with the initial headway - from about 2.6% of
the threshold per 0.8 s at the longest gaps to about 44% at the shortest.

Two consequences. First, response timing in a conflict starts from a baseline the headway
already set, so the model predicts that a driver following closely responds sooner partly
because they were already part-way to a re-plan. Second, a warning: extrapolated, this
model re-plans on its own after a few seconds of uneventful following at short gaps. If
you run long benign run-ins, you will meet that.

Note the scatter is not a clean line - colour is initial speed, and speed matters too. The
shortest-headway condition is also the fastest one.
""")

    video_slide(prs, "chapter 05", "The escape is a property of the landscape, not a rule",
                "paper_maneuver.gif",
                "The authors' own 28 baseline runs. At 10 m/s: 86% braking, no steering. "
                "At 20 m/s: 96% steering. At 25 m/s: 58% of runs leave the road. Nothing "
                "in the code says “brake below 60 km/h, steer above”.", 1.9, """
Nothing in the code says brake at low speed and steer at high speed. Yet that is exactly
what the authors' own runs show, and the gradient is sharp.

The physical reading: at low speed comfortable braking removes the kinetic energy in time
and barely troubles the pedal-smoothness preference. At high speed the deceleration needed
to stop behind the lead becomes so severe that a lane change, despite its own preference
costs, scores better. The maneuver falls out of comparing imagined futures under one
landscape.

Now the honest part, and I want to put it on the slide rather than in the Q&A. At 25 m/s a
majority of the deposited runs - 58% averaged over the gap grid - end by leaving the road,
mostly during the avoidance maneuver and mostly to the left. At a 3.5 s gap moderate
braking would have sufficed. We read that as a property of the lane-change control at
speed rather than a deliberate trade-off, and that reading is ours. Either way, anyone
analysing this model at 25 m/s should track road departure as its own outcome class.
""")

    s = head(prs, "Two questions about the other vehicle, easily conflated",
             kicker="chapter 06")
    y = BODY_TOP + 0.4
    panel(s, MARGIN, y, 15.0, 6.4, BEIGE)
    text(s, MARGIN + 0.75, y + 0.6, 13.5, 5.4,
         [("1.  What it actually does", 17, PURPLE, True),
          ("Decided by a script — simple, deterministic, and entirely outside the driver "
           "model. Rear-end: a countdown, then brake. Oncoming: a TTC trigger, then an "
           "incursion. Intersection: a turn across our path.", 13.5, INK, False, 8),
          ("It never reacts to our driver. It is where a scenario's difficulty lives. And "
           "it is invisible to the driver, who meets it only through optics.",
           13, GREY, False, 8)], spacing=1.1)
    panel(s, MARGIN + 16.2, y, 15.0, 6.4, BEIGE)
    text(s, MARGIN + 16.95, y + 0.6, 13.5, 5.4,
         [("2.  What the driver believes it is doing, and might do next", 17, DEEPTEAL, True),
          ("Decided by the belief machinery — a particle swarm whose own motion is "
           "norm-shaped, serving both the tracking of the present and the imagining of "
           "futures.", 13.5, INK, False, 8),
          ("The particle filter is NOT how the other vehicle's behavior is generated. It "
           "is how the driver's uncertainty about that behavior is represented.",
           13, GREY, False, 8)], spacing=1.1)
    text(s, MARGIN, 13.6, BODY_W, 3.0,
         [("Keeping these apart is the key to reading the code and the paper correctly.",
           15.5, PURPLE, True),
          ("A trap for code readers: src/oncoming/dynamics_true.py contains a "
           "cost_function, and it has nothing to do with the driver's preferences. It is "
           "the scenario author's own objective, gradient-descended to manufacture a "
           "smooth incursion. Stage machinery, not psychology.", 13, INK, False, 10)])
    notes(s, 1.2, """
This slide exists because getting these two confused makes the whole paper unreadable.

The script answers question 1. The particle filter and the roll-outs answer question 2.
They are unrelated pieces of machinery.

The cost_function trap at the bottom is worth saying out loud to anyone who is going to
open the code. Reading it as part of the driver model would be a serious
misunderstanding. It manufactures the incursion trajectory; it is set dressing.
""")

    video_slide(prs, "chapter 06", "Where the norms live: inside the swarm's own motion",
                "paper_tournament.gif",
                "The released sampling rule, lateral-only, with its real geometry factors. "
                "Compliant target: heaviest ticket 50 000× the lightest. Violating target: "
                "1× — the lottery is uniform and the bias has dissolved.", 2.5, """
This is the mechanism we ourselves initially got only half right, so it gets the longest
video.

The normative machinery is not a layer applied on top of predictions. It is built into how
every particle moves. Whenever a particle's picture of the other vehicle advances one step
- in the belief update AND in the planning roll-outs, which are served by literally the
same transition object - it runs a mini-tournament.

Propose 32 candidate moves. Score each by norm compliance in three snapshots: where the
vehicle is now, where the candidate puts it one step ahead, and where it would be four
seconds ahead if held. Average the two future scores, then take the WORSE of "now" and
that average. Draw one winner by lottery, tickets proportional to score.

Now the elegant part, and watch the number in the corner. The "now" score is identical for
all 32 candidates - it describes where the vehicle already is, which no candidate can
change. While the vehicle behaves, that shared score is high, so the differences between
candidates decide the lottery and the bias bites: heaviest ticket 50 000 times the
lightest. The moment the vehicle is grossly misbehaving, the shared score collapses and
becomes the ceiling for every candidate at once. Ratio 1. The lottery goes uniform, and
the swarm fans out over everything the vehicle could physically do.

Trust is not a separate mechanism with its own parameter. It is that minimum doing its
work, revoked on evidence within a step or two.

And watch the fan lean back: a hypothesis that wanders into the normal region regains its
bias and is recaptured. The swarm entertains the long tail AND expects the violator to
return to normality - which strikes us as a rather human expectation to hold.
""")

    s = head(prs, "Why this arrangement is worth copying — and its limits",
             kicker="chapter 06")
    y = BODY_TOP + 0.2
    column(s, MARGIN, y, 15.0, 8.0, "Worth copying",
           ["Detection speed comes from expectation violation, not tuned vigilance. The "
            "driver is relaxed because compliant futures are weighted up, and alert "
            "because compliance visibly failed. One mechanism, no free alertness "
            "parameter.",
            "The uncertainty is decision-grade. The same cloud that represents “they "
            "might brake / might not” is what plans are scored against, so caution "
            "scales with genuine ambiguity.",
            "The seams are explicit — two noise dials, one norm geometry, one trust cap."],
           colour=DEEPTEAL, size=12.5)
    column(s, MARGIN + 16.2, y, 15.0, 8.0, "The limits, stated plainly",
           ["The other agent has no mind. It does not perceive our driver, and the "
            "driver's model of it contains no recursive “they see me seeing them”.",
            "Cooperative and communicative phenomena — gap negotiation, hesitation "
            "reading, signaling — are outside the published model's scope.",
            "The norms are hand-drawn per scenario. Honest, but it does not scale; "
            "learning them from data is one of the most natural extensions this line "
            "offers.  [Opinion]"], colour=DEEPPINK, size=12.5)
    text(s, MARGIN, 15.4, BODY_W, 1.6,
         [("One more consequence, ours and unpublished: when the observation channel is "
           "closed, the same norm-shaped transition carries the cloud forward "
           "uncorrected — the belief machinery is a short-horizon simulator, not a passive "
           "sensor buffer. Chapter 08 returns to it.  [Study]", 12.5, GREY, False)])
    notes(s, 1.2, """
The left column is what I would take into my own modeling. The right column is what the
paper does not claim and neither should you.

The coasting point at the bottom is a preview of chapter 8 and it is ours. It matters
because it changes what an occlusion or a glance does to this model - and I will show you
the consequence shortly.
""")

    s = head(prs, "“Normal” appears twice, and they are different objects",
             kicker="chapter 07")
    y = BODY_TOP + 0.6
    panel(s, MARGIN, y, 15.0, 5.0, BEIGE)
    text(s, MARGIN + 0.8, y + 0.65, 13.4, 4.0,
         [("The driver's own normal", 18, PURPLE, True),
          ("The preference prior: how MY drive is supposed to go. This shapes what the "
           "driver does.", 14, INK, False, 10)], spacing=1.12)
    panel(s, MARGIN + 16.2, y, 15.0, 5.0, BEIGE)
    text(s, MARGIN + 17.0, y + 0.65, 13.4, 4.0,
         [("Normal for the others", 18, DEEPTEAL, True),
          ("The norm geometry of chapter 06: what THAT vehicle is expected to do. This "
           "shapes what the driver predicts, hence when it worries.", 14, INK, False, 10)],
         spacing=1.12)
    text(s, MARGIN, 11.6, BODY_W, 5.0,
         [("The pattern worth naming, for the second kind:", 14.5, INK, True),
          ("Rear-end — normal is the lead staying within the lane. Nothing about speed: a "
           "lead may brake without becoming abnormal.", 13, INK, False, 8),
          ("Oncoming — normal is staying in its own lane AND holding its speed. An "
           "oncoming vehicle that brakes hard is abnormal before it crosses the line — the "
           "earliest warning this geometry allows.", 13, INK, False, 6),
          ("Intersection — normal is respecting the junction: not passing the yield line, "
           "not cutting the corner arc, not leaving the paved area.", 13, INK, False, 6),
          ("Each scenario's norm set encodes the specific way that scenario's threat "
           "announces itself.  [Opinion]", 13.5, PURPLE, True, 10)])
    notes(s, 0.9, """
Two normals, two jobs. Confusing them is the second most common way to misread the model,
after the surprise/preference pair.

The progression across the three scenarios is instructive and it is the answer to
checklist item 5. Stay in your lane; then also keep your speed; then also stay on the road
and obey the light. Each one is written by hand, and each encodes the earliest observable
sign that the other agent has stopped being ordinary.
""")

    video_slide(prs, "chapter 07", "The driver's own normal: six terms, multiplied",
                "paper_preference.gif",
                "Shapes to scale, parameters as shipped. The closing-rate term is drawn "
                "one-sided, as the released code implements it — the SI writes the "
                "symmetric form. The safety-margin term is an indicator, not a graded "
                "quantity; its boundary here is the closed form at 15 m/s.", 2.2, """
Six independent terms, multiplied. Each says which values of one observed quantity are
unremarkable and how quickly departures become objectionable.

Because they multiply, and log-multiply to a sum, any exceedance can be attributed to the
term responsible. That is a genuinely useful property when you are debugging behavior.

Two of these are drawn differently from how the SI writes them, and both differences are
in the released code rather than the paper.

The closing-rate term is ONE-SIDED as released: closing slower than a TTC of about 5 s,
holding the gap, or falling back all cost nothing. So it bounds the approach rate and does
not shape the following distance itself. The SI writes the symmetric form.

And the last panel is a step, not a slope. The safety-margin term is an indicator: when
required deceleration exceeds what the vehicle can do, a fixed penalty is charged, and
otherwise nothing.
""")

    s = head(prs, "Three of the six deserve a longer look", kicker="chapter 07")
    body(s, [
        ("The lane term is where scenarios differ.", "“Centred in my lane” needs "
         "to know what lanes exist and which direction they serve; that geometry is "
         "hand-drawn per scenario. Rear-end's version adds explicit costs on dawdling "
         "between lanes and on aborting a lane change — hand-built craftsmanship, not "
         "derived theory, and worth knowing about before attributing its effects to deep "
         "principles"),
        ("The closing-rate term defines everyday tailgating comfort.", "Easy to overlook — "
         "the article barely mentions it — but without it the model would happily sit at a "
         "tiny, technically-safe gap. It encodes “being close and closing feels wrong "
         "before it is dangerous”: a comfort standard distinct from the safety margin"),
        ("The safety-margin term is a counterfactual, and its assumptions are the "
         "boundary's location.",
         "It asks: if the lead braked at an assumed worst case, and I responded only after "
         "an assumed reaction time, would ordinary braking still suffice? Both assumptions "
         "are parameters. Any absolute number derived from this term — a critical headway, "
         "a threshold gap — inherits them and should be quoted with them"),
    ], y=BODY_TOP, size=13)
    panel(s, MARGIN, 13.6, BODY_W, 3.2, BEIGE)
    text(s, MARGIN + 0.8, 14.0, 29.4, 2.6,
         [("Two properties of the released safety-margin term matter outside the published "
           "scenarios: it is an indicator rather than a graded quantity, and it applies "
           "only while the other vehicle is ahead and within 1.15 vehicle widths — the "
           "same box the collision test uses. A vehicle ENTERING the lane is invisible to "
           "it until the box test flips, and then it switches on at full strength. "
           "[Code] [Study]", 12.5, INK, False)])
    notes(s, 1.5, """
The third one is the one to be careful with, and it is why our handbook spends a page on
it.

The term is a counterfactual with two assumptions baked in - the assumed worst-case lead
braking, and the assumed reaction time of one second. Those are not measurements. So if
anyone quotes you a critical headway derived from this model, ask what a_OV,min and t_react
were, because the number moves substantially with both.

The box at the bottom is a finding of ours and unpublished. The applicability test is
binary, so a vehicle straddling the lane boundary - which is exactly what a highway cut-in
does for a couple of seconds - is all-or-nothing to the driver. None of the three released
scenarios sustains that state, so it never bit the authors. It bit us.
""")

    s = head(prs, "What, ultimately, defines “normal” here", kicker="chapter 07")
    y = BODY_TOP + 0.6
    for lab, txt, col in [
        ("Specified by the authors",
         "The SHAPE of every preference term. Not derived from first principles.", PURPLE),
        ("Hand-tuned",
         "Thirteen parameters, tuned to produce human-like behavior.", BLUE),
        ("Calibrated",
         "One — the assumed worst-case braking — against a separate free-following "
         "dataset, per scenario.", DEEPTEAL),
        ("Never fitted to the evaluation data",
         "None are fitted to the conflict data the model is evaluated on.", DEEPPINK),
    ]:
        panel(s, MARGIN, y, BODY_W, 2.5, BEIGE)
        text(s, MARGIN + 0.8, y + 0.45, 12.0, 1.7, [(lab, 15, col, True)])
        text(s, MARGIN + 13.4, y + 0.5, 17.0, 1.7, [(txt, 13, INK, False)])
        y += 2.75
    text(s, MARGIN, 15.9, BODY_W, 1.6,
         [("So “normative driving” in this model is a stated hypothesis about "
           "drivers' standards, made falsifiable by its behavioral consequences — response "
           "times, maneuver choices, headways — rather than an empirical measurement of "
           "those standards", 14, PURPLE, True)])
    notes(s, 0.9, """
Honesty about provenance, and the bottom line is the fair way to describe what this model
claims.

It is not a measurement of what drivers accept. It is a stated hypothesis about their
standards, whose consequences are testable. That is a perfectly respectable scientific
position and it is better to say it plainly than to let a reader assume the preference
function was measured.

This slide is also the natural bridge to anyone who wants to MEASURE those standards
instead of stating them - but that is a different talk.
""")

    s = head(prs, "A complete gaze system ships in the code — switched off",
             kicker="chapter 08")
    body(s, [
        ("The dynamics", "include a two-state gaze variable (eyes on road / off road) with "
                          "switching probabilities"),
        ("The observation model", "multiplies perception noise by a factor of 3 when gaze "
                                  "is off road — looking away does not blind the driver, it "
                                  "degrades evidence quality by a set ratio"),
        ("The belief machinery", "reserves the first two state dimensions for gaze — "
                                 "visible in the OSF belief arrays, sitting constant"),
        ("The preference vocabulary", "includes a gaze term, set to zero in every published "
                                      "collision-avoidance run"),
        ("The planner", "contains the line that turns it all off: a hard-coded "
                        "“avoid off gaze right now”"),
    ], y=BODY_TOP, size=13.5)
    panel(s, MARGIN, 12.5, BODY_W, 4.3, BEIGE)
    text(s, MARGIN + 0.8, 12.95, 29.4, 3.5,
         [("Off-road glances are implemented as actions the driver COULD choose, with an "
           "evidence price attached. The collision-avoidance paper simply forbade them, to "
           "isolate avoidance behavior. The earlier paper in this line (Engström et al. "
           "2024) demonstrates exactly this machinery on uncertainty-and-looking tasks.",
           13.5, INK, False)])
    notes(s, 1.5, """
This is the slide that most surprises people who have only read the collision-avoidance
paper, and it is why chapter 8 exists.

The machinery is not in a fork or a branch. It is in the code that ran the published
results, threaded through every layer, and disabled by one hard-coded line in the planner.

Why it matters: if you want to use this architecture for crash-causation work - eyes off
road at the wrong moment - you are not building a gaze system, you are re-enabling one and
setting its preference weight. That is a much smaller project than it looks.
""")

    s = head(prs, "What we found when we exercised it — and what does not exist",
             kicker="chapter 08")
    panel(s, MARGIN, BODY_TOP, BODY_W, 5.6, BEIGE)
    text(s, MARGIN + 0.8, BODY_TOP + 0.5, 29.4, 4.8,
         [("The gate blocks new observations, not inference.  [Study]", 16, PURPLE, True),
          ("A driver that has registered the lead's braking and is then blinded keeps "
           "responding DURING the glance, at essentially the attentive onset, even under a "
           "near-total observation blackout — because the belief cloud coasts forward on "
           "its own norm-shaped prediction and the accumulator keeps filling from the "
           "extrapolated evidence.", 13.5, INK, False, 8),
          ("So the architecture predicts that a glance beginning AFTER the conflict has "
           "been registered costs little, while a glance covering the onset costs the whole "
           "detection. A model that assumes no accumulation while the eyes are off the road "
           "predicts the opposite in the first case — a testable distinction that neither "
           "description states.", 13, INK, False, 8)], spacing=1.1)
    y = 12.0
    column(s, MARGIN, y, 15.0, 4.8, "What else exists today",
           ["Perception-quality causation — noise scales are parameters, and looming makes "
            "difficulty state-dependent for free.",
            "Expectation-based causation — chapter 06's trust is already a "
            "looked-but-did-not-expect mechanism.",
            "A response-vigor dial — λ, the blunt but honest impairment knob."],
           colour=DEEPTEAL, size=12.5)
    column(s, MARGIN + 16.2, y, 15.0, 4.8, "What does not",
           ["No fatigue or drowsiness dynamics; nothing varies with time on task.",
            "No cognitive load or dual-task interference beyond the gaze dichotomy.",
            "No alcohol or drug pharmacodynamics. No individual-differences layer. No "
            "learning — expectations do not drift with exposure."],
           colour=DEEPPINK, size=12.5)
    notes(s, 0.9, """
The top box is ours, unpublished, and it is the most useful thing we found in chapter 8.

We forced off-road glance schedules on the released rear-end model, lifted the planner's
prohibition for the schedule, everything else as shipped. The result is not what a
naive reading predicts: blinding the driver after it has registered the conflict barely
delays the response, because the belief cloud is a short-horizon simulator that runs with
or without fresh input.

That is a genuine, testable behavioral distinction between this architecture and the
common assumption that accumulation pauses while the eyes are away. If you do
crash-causation work with this model, it matters a lot which of those is true.

The right-hand column is what you cannot do today, and I would rather say it than have
someone discover it three months in.
""")

    # =====================================================================
    # PART III - using it
    # =====================================================================
    divider(prs, "III", "Changing it, and knowing whether the change is right",
            "Handbook chapters 09 and 10: the seams the model is meant to be changed at, "
            "the validation ladder, and where every number came from.")

    s = head(prs, "The seams — the places the model is meant to be changed",
             kicker="chapter 09")
    table(s, MARGIN, BODY_TOP, [8.4, 12.6, 10.2], [
        ["Seam", "What it represents", "Where"],
        ["Preference knobs", "the driver's own standards; traits and states",
         "reward.py params / Setups columns"],
        ["Safety-margin assumptions", "worst case planned for; reaction time budgeted",
         "preference term + calibration table"],
        ["Norm geometry", "what others are expected to do", "reward.py::get_weights"],
        ["Assumed other-agent variability", "what kind of agent I am facing",
         "a_sd_model, w_sd_model"],
        ["Perception noise & looming", "visibility, conspicuity, sensory quality",
         "decoder noise scales, threshold"],
        ["Accumulation rate λ", "evidence-to-action vigor", "EA_fac"],
        ["Gaze system", "attention on or off the road", "dormant; chapter 08"],
        ["Scenario script", "the world and its threat", "dynamics_true.py"],
    ], size=12, row_h=1.28)
    text(s, MARGIN, 16.2, BODY_W, 1.4,
         [("A modification that does not fit one of these — one that needs the planner "
           "rewritten or a new state variable threaded through the belief machinery — is a "
           "research project, not a modification, and should be costed accordingly  "
           "[Opinion]", 13, PURPLE, True)])
    notes(s, 1.2, """
Every previous chapter located a place the model is meant to be changed. This collects
them.

The line at the bottom is the practical advice. Most things people want to do to this
model are seam work and take days. A few are not, and those take months, and the
difference is predictable in advance from this table. Knowing which one you are proposing
before you promise a delivery date is worth something.
""")

    s = head(prs, "The validation ladder — climb it, do not skip rungs",
             kicker="chapter 09")
    y = BODY_TOP - 0.1
    for n, ttl, txt, col in [
        ("0", "Property checks  (minutes)",
         "Verify the changed component against its own specification, ideally by two "
         "independent routes. Sign errors and unit slips produce plausible-looking wrong "
         "numbers that eyeballing does not catch.", GREY),
        ("1", "Mechanism check  (hours, static)",
         "The knob you turned moves the quantity it should, in the right direction, by "
         "roughly the expected amount, with other quantities still. For preference changes "
         "this needs no simulation at all.", BLUE),
        ("2", "The ablation discipline  (free, from the deposit)",
         "Show what a mechanism contributes by removing it. The deposit holds 7 × 28 = 196 "
         "ablation runs for rear-end already — check before running anything.", DEEPTEAL),
        ("3", "Distribution comparison  (also free)",
         "Any closed-loop change must reproduce the UNCHANGED behaviors — response-time "
         "distributions, maneuver mix, collision rates — against the authors' own output, "
         "not numbers read off figures.", PURPLE),
        ("4", "Human data",
         "Only rungs 0–3 make rung 4 interpretable: a mismatch can then be attributed to "
         "the mechanism under test rather than to a broken foundation.", DEEPPINK),
    ]:
        panel(s, MARGIN, y, BODY_W, 2.55, BEIGE)
        text(s, MARGIN + 0.55, y + 0.55, 1.3, 1.4, [(n, 21, col, True)])
        text(s, MARGIN + 2.1, y + 0.35, 28.6, 2.1,
             [(ttl, 14, col, True), (txt, 12.2, INK, False, 4)], spacing=1.06)
        y += 2.72
    notes(s, 1.5, """
Each rung has a cheap failure mode that the rung above cannot detect. That is the whole
argument for not skipping.

Rungs 2 and 3 are the gift of the deposit, and I do not think enough people know this.
The paper's Figure 6 ablates seven mechanisms, and the complete simulation output for
every one of those ablations is deposited - seven variants across the full rear-end grid,
already run. Before you spend a week of CPU, check whether the ablation you need is
already in Setups_rear_end.xlsx.

The columns to look for: EA_mode = None, noise_pred_fac = 0.002, use_pedals = 0,
use_looming_perception = 0, looming_threshold = 0, N_norm = 1, alpha = 0.
""")

    s = head(prs, "Three ways a number gets into this model — fitting is only one",
             kicker="chapter 10")
    y = BODY_TOP + 0.5
    for n, ttl, txt, col in [
        ("1", "Specified",
         "Taken from physics, geometry, or independent literature: vehicle dimensions, "
         "maximum braking, the timestep, the looming detection threshold. "
         "Obligation when you change it — cite the independent source, or admit the number "
         "has become a fitted one.", BLUE),
        ("2", "Calibrated",
         "Set from separate, non-evaluation data. Exactly one parameter in this model: the "
         "assumed worst-case deceleration of the other vehicle.", DEEPTEAL),
        ("3", "Tuned",
         "Hand-adjusted until behavior looked human. Thirteen parameters. Not fitted to "
         "the conflict data the model is evaluated on.", DEEPPINK),
    ]:
        panel(s, MARGIN, y, BODY_W, 3.5, BEIGE)
        text(s, MARGIN + 0.6, y + 0.5, 1.4, 1.3, [(n, 22, col, True)])
        text(s, MARGIN + 2.3, y + 0.45, 28.2, 2.9,
             [(ttl, 15.5, col, True), (txt, 12.8, INK, False, 5)], spacing=1.08)
        y += 3.8
    text(s, MARGIN, 16.2, BODY_W, 1.2,
         [("A natural first assumption is that a model like this is “fitted to "
           "data” the way a regression is. It is not, and the distinction matters for "
           "anyone planning to change it", 13.5, PURPLE, True)])
    notes(s, 1.2, """
This distinction is the thing people get wrong most often when they come to a simulator
model from a statistics background.

Each route carries a different obligation when you replace the number. If you change a
specified parameter, you owe a citation or an admission. If you change a calibrated one,
you owe a re-calibration on non-evaluation data. If you change a tuned one, you owe the
ablation and the distribution comparison from the previous slide.
""")

    s = head(prs, "The calibration exemplar, worth copying", kicker="chapter 10")
    text(s, MARGIN, BODY_TOP, BODY_W, 1.4,
         [("The most consequential preference parameter — the assumed worst-case "
           "deceleration of the other vehicle — is neither specified nor tuned. It is "
           "calibrated, and the mechanism is the pattern any extension should copy.",
           14.5, INK, False)])
    body(s, [
        ("1  Run a large grid of FREE-FOLLOWING simulations.", "No conflict — just steady "
         "car-following, across speeds, accumulator rates and candidate worst-case "
         "assumptions, recording the steady headway each settles into"),
        ("2  Invert the table.", "Given a speed and a desired everyday headway, look up "
         "the worst-case assumption that PRODUCES it"),
        ("3  Use that value, unchanged, when simulating conflicts.", ""),
    ], y=7.0, size=13.5)
    panel(s, MARGIN, 11.6, BODY_W, 5.2, BEIGE)
    text(s, MARGIN + 0.8, 12.05, 29.4, 4.4,
         [("The logic is quietly elegant: the paranoia parameter is disciplined by ordinary "
           "behavior. A driver who assumed worse would follow further back all the time, so "
           "observed comfortable headways pin down the assumption without touching any "
           "conflict data. Calibrate on the quiet regime, predict the loud one.",
           13.5, PURPLE, True),
          ("And one general lesson: a calibration is only as good as its coverage. The "
           "shipped lookup spans steady-state headways to about 1.0–2.1 s depending on "
           "speed; outside that the interpolation clamps and the parameter saturates at "
           "−8 m/s². Coverage failures do not announce themselves — the model still runs.",
           12.5, INK, False, 8)])
    notes(s, 1.2, """
I would take this pattern into almost any simulator-based modeling work, whatever the
framework.

The insight is that you can discipline a parameter that only matters in rare events by
using its consequences in common events. The assumed worst case only bites in a conflict,
but it also shifts everyday following distance - so you calibrate it on everyday following
and then predict conflicts. Chapter 5's behavioral separation between quiet and loud, used
as an inference principle.

The coverage warning is worth a one-line assertion in your own code: check that the
calibration table brackets every condition you intend to simulate. Ours did not, and
nothing complained.
""")

    s = head(prs, "Identifiability, and how fitting actually proceeds",
             kicker="chapter 10")
    y = BODY_TOP
    column(s, MARGIN, y, 15.0, 5.8, "The central danger",
           ["The parameters do not map one-to-one onto observables. Several knobs move "
            "response time in the same direction — the accumulation rate, perception "
            "noise, the norm trust, the assumed worst case.",
            "So a response-time curve alone cannot tell you which one was wrong. Two "
            "explanations of the same behavior have to be told apart by something that "
            "distinguishes them."], colour=DEEPPINK, size=12.5)
    column(s, MARGIN + 16.2, y, 15.0, 5.8, "There is no formula to invert",
           ["The model is a simulator, so fitting means comparing simulated and observed "
            "behavior, and searching.",
            "Which makes the choice of summary, and of noise floor, the whole game."],
           colour=PURPLE, size=12.5)
    body(s, [
        ("Fit summaries, not trajectories.", "The paper's own comparisons use response-time "
         "distributions per condition, maneuver-choice proportions and deceleration "
         "profiles, with distribution distances as the yardsticks. Any refit should use the "
         "same summaries first, so results stay comparable"),
        ("Respect the noise floor.", "Each condition was run with 32 seeds, and "
         "seed-to-seed spread is substantial. A fit that chases differences smaller than "
         "the seed spread is fitting noise"),
        ("Be static wherever possible.", "Preference parameters can be evaluated against "
         "recorded kinematics without running the loop. Only timing-and-prediction "
         "parameters genuinely require simulation — and for those, the deposit's "
         "precomputed grids are the difference between a week and a year"),
    ], y=11.0, size=12.5)
    notes(s, 1.2, """
Identifiability is the reason I would not trust a refit of this model presented without an
argument that the parameters could be told apart.

The practical trio at the bottom is the advice I would actually give. The middle one is
the one people skip: simulate enough seeds to know the model's own variability BEFORE
crediting a parameter change with an improvement. With 32 seeds per condition and
substantial spread, it is easy to celebrate noise.
""")

    # =====================================================================
    # PART IV - reference and close
    # =====================================================================
    divider(prs, "IV", "Where everything is",
            "Handbook chapters 11 and 12: the code and data map, and the glossary that "
            "translates between three vocabularies.")

    s = head(prs, "From concept to file", kicker="chapter 11")
    table(s, MARGIN, BODY_TOP, [10.6, 9.4, 11.2], [
        ["Concept", "File in src/common/", "What to look for"],
        ["World physics", "bicycle.py, environment.py", "the bicycle model both vehicles share"],
        ["Looming senses", "decoder.py, encoder.py",
         "observation construction; the looming transform; off-gaze noise factor I_factor"],
        ["Belief cloud", "particle_filter.py, kde.py", "weighting, resampling, the mixture "
                                                       "representation"],
        ["Imagined futures + trust", "dynamics.py",
         "forward_tar_agent, normative_probability; N_norm/H_norm and the trust cap"],
        ["Scoring (pragmatic + epistemic)", "belief_reward.py",
         "expected-free-energy assembly over particles"],
        ["Planner + surprise gate", "mpc_discrete.py",
         "the CEM loop; evidence accumulation; the hard-coded “avoid off gaze” line"],
    ], size=11.5, row_h=1.5)
    text(s, MARGIN, 14.6, BODY_W, 2.4,
         [("Per scenario: src/<scenario>/dynamics_true.py (the world and the other "
           "vehicle's script), decoder_true.py, and reward.py (the preference terms with "
           "this scenario's lane geometry, and get_weights — the norms).", 12.5, INK, False),
          ("All 65 configuration columns are in every Setups_*.xlsx, which double as the "
           "complete configuration record of every published run.", 12.5, GREY, False, 6)])
    notes(s, 0.9, """
A reference slide. Photograph it if you are going to open the code.

The one line to say out loud: the Setups tables double as the complete configuration
record of every published run. Sixty-five columns per run. That is a standard of
reproducibility worth copying regardless of what you think of the model - every result
carries its full parameter set.
""")

    s = head(prs, "The same idea, in three vocabularies", kicker="chapter 12")
    table(s, MARGIN, BODY_TOP - 0.1, [9.4, 10.6, 11.2], [
        ["Term here", "Engineering / ML reading", "Human-factors reading"],
        ["Generative model", "internal simulator / world model",
         "the driver's understanding of how traffic works"],
        ["Belief (particle cloud)", "posterior state estimate with honest uncertainty",
         "situation awareness, held with degrees of confidence"],
        ["Surprise", "negative log-likelihood of what happened", "expectancy violation"],
        ["Preference prior", "goal specification written as a distribution",
         "motivation; how the drive is supposed to go"],
        ["Epistemic value", "expected information gain of a plan",
         "the pull to look, probe and resolve uncertainty"],
        ["Norm-conditioning trust cap", "prior weight gated by observed compliance",
         "trust extended while earned, withdrawn on evidence"],
        ["Evidence accumulation (E, λ)", "leaky-free integrator to threshold",
         "the response-timing process of accumulator models"],
        ["Residual information (ε)", "shortfall of current plan vs best achievable, in nats",
         "how far the situation has left “as it should be”"],
    ], size=11.5, row_h=1.32)
    notes(s, 1.2, """
The handbook's chapter 12 is a Rosetta stone, and this is the useful half of it.

Its real job is meetings. When an engineer says "posterior state estimate" and a
human-factors researcher says "situation awareness", this table says they are pointing at
the same object in the code - and that saves a surprising amount of arguing.

The middle columns are our translations, and where a mapping is loose the handbook says so
rather than forcing it. Free energy, for instance, has no native human-factors equivalent.
""")

    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Cm(SLIDE_W), Cm(SLIDE_H))
    _plain(bg, PURPLE)
    rule(s, 2.3, 3.4, 3.2, TEAL, 5.0)
    text(s, 2.3, 4.2, 29.0, 2.4, [("What the model is, in one slide", 30, WHITE, True)])
    text(s, 2.3, 7.2, 29.6, 8.2,
         [("One loop, five times a second: sense through looming, hold 75 hypotheses, roll "
           "them forward, score them against a preference distribution, act, and deposit "
           "the shortfall into an account that triggers a re-plan when it fills.",
           16, WHITE, False),
          # the line the talk asks them to remember, so it is not the dimmest on the slide
          ("Perception and action are the same operation in two directions. Response time "
           "is not a parameter — it is what the account took to fill. The maneuver is not a "
           "rule — it is the best-scoring imagined future. Trust is not a dial — it is a "
           "minimum in the sampling weights.", 16, WHITE, False, 12),
          ("One driver, many worlds: of 65 configuration parameters, every driver-side one "
           "is identical across the three scenarios, save a single assumption about what "
           "kind of agent it faces.", 16, MUTED, False, 12)], spacing=1.16)
    text(s, 2.3, 16.3, 29.0, 1.6,
         [("The handbook: docs/handbook_authors/  ·  reading paths in its front matter  ·  "
           "corrections very welcome", 13, TEAL, False)])
    notes(s, 0.9, """
Close on this and leave it up during questions.

If someone remembers one sentence, make it the second block: response time is not a
parameter, the maneuver is not a rule, trust is not a dial. All three fall out of one
objective evaluated over imagined futures. That is what the framework buys, and it is why
it was worth the hour even for people who will never run it.

Offer the handbook. It has reading paths in the front matter - thirty minutes for any
background is chapter 2 then the first half of chapter 1; the code-changing path is 3, 4,
11, 9, 10.

And say plainly that corrections are welcome, because some of what I showed you is our
reading rather than the authors' claim, and it is tagged that way throughout.
""")

    prs.save(str(out))

    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    n_slides = n_video = 0
    total = 0.0
    for s in prs.slides:
        n_slides += 1
        if s.shapes._spTree.find(f".//{A}videoFile") is not None:
            n_video += 1
        t = s.notes_slide.notes_text_frame.text
        if t.startswith("[") and " min]" in t:
            try:
                total += float(t[1:t.index(" min]")])
            except ValueError:
                pass
    print(f"wrote {out}\n  {n_slides} slides, {n_video} carrying video, "
          f"notes budget {total:.1f} min")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "ai_paper_talk.pptx")
    a = ap.parse_args()
    build(a.out)


if __name__ == "__main__":
    main()
