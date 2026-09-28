"""
Make the 2026-09-28 version of the authors' edition from the edition the authors received
(`aif_driver_model_handbook.md`, revised 2026-09-03), which is left untouched.

Every addition is marked twice: a visible label ("New in this version, 28 September 2026: not in the
edition you received") and the round mark {{R8}}, which the Word and PDF builds turn into color. The
one passage that is reworded (the 25 m/s road departures) quotes the wording the authors received.
The content is items 1-5 of `review_2026-09-28.md`; every number there is from a tracked output.

Run:  python docs/handbook_authors/make_version_2026_09_28.py
Out:  aif_driver_model_handbook_2026-09-28.md, .docx, .pdf (beside this script)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent
SRC = HERE / "aif_driver_model_handbook.md"
OUT = HERE / "aif_driver_model_handbook_2026-09-28.md"
LABEL = "**New in this version, 28 September 2026: not in the edition you received.**"
M = "{{R8}}"


def new_para(text: str) -> str:
    return f"{M}{LABEL} {text}"


BANNER = f"""{M}**This is a newer version than the one you received.** The edition sent to you is dated
3 September 2026. This version, dated 28 September 2026, adds five passages based on work done
since then, four of them using naturalistic traffic data (the highD dataset) that we did not have
before. Every addition begins with the label "New in this version, 28 September 2026: not in the
edition you received" and is set in color in the Word and PDF files. Nothing in the edition you
received has been removed. One sentence has been reworded (the reading of the 25 m/s road
departures, chapter 5), and the wording you received is quoted beside it. The additions are in:

- {M}chapter 3, "The looming channel, tested against human judgments": the naturalistic check that the
  earlier text said was missing;
- {M}chapter 5, "Normal driving: the quiet regime": the model in sustained following, now observed
  rather than extrapolated;
- {M}chapter 5, "What this means for using the model": the response-time relation on real motorway
  data;
- {M}chapter 5, the 25 m/s road departures: a softer reading;
- {M}chapter 7, Part A: how often the safety-margin and inverse-tau terms act in real traffic.

"""

ITEM1 = new_para("""In sustained following the drift does trigger re-plans, and the re-plans
brake. Behind a lead holding a constant speed, the released configuration began braking after 3.2 s
at a 1.5 s headway and after 4.6 s at 2.0 s, with or without gaze choice and with the scenario's own
scripted lead; some repeats braked to a standstill; with perception noise raised a hundredfold it
followed steadily. Behind real leads replayed from the highD dataset, in 18 five-second episodes in
which the lead's acceleration never exceeded 0.5 m/s² in magnitude, it braked by at least 1 m/s² in
56% of runs, typically 2.5–5 s in and often at −6 to −7 m/s², while the drivers of the same episodes
did not brake at all (their lowest acceleration −0.63 m/s²). The episodes were staged with the
released calibration (`find_parameters`), which returned the same values for all 18 (desired-speed
offset 0, assumed lead braking −8 m/s²) [Study]. The published scenarios never exercise this regime,
and nothing in them is wrong because of it; it matters for any use of the model with a run-in longer
than a few seconds. What makes braking win at the first re-plan, and why noisier perception
suppresses it, we have not established [Opinion].""")

ITEM2 = f"""- {M}{LABEL} **The response-time relation holds in direction on real motorway data.** On
  1,033 lead-deceleration events in the highD dataset, the log of the follower's response time rises
  with the log of the initial time gap, and more steeply the harder the lead brakes: slopes +0.23,
  +0.40 and +0.45 for mild, moderate and hard lead decelerations, against +0.59 in the deposited
  runs. Real responses are about three times slower (median 2.2–3.1 s at 1–2 s gaps against 0.8 s).
  Most of that is the data: few motorway events are emergencies (32 leads braked at 3 m/s² or more),
  and real lead braking takes about 2 s to build up where the scenario's takes a tenth of that. With
  so few hard events this is descriptive, not a test [Study]."""

ITEM3 = new_para("""**How often the terms act on real traffic.** Evaluated on about a million
car-following samples from the highD dataset, the calibrated safety-margin term is violated in 1.7%
of steady following and the inverse-tau term in 0.05%. The headway at which the margin starts to
cost, at equal speeds, lies at or below the fifth percentile of real headways in four of five speed
bands (0.70 s at 40–70 km/h down to 0.05 s above 130 km/h, against real fifth percentiles of
0.54–0.67 s). On 2,208 real closing cut-ins, at the moment the cutting-in car enters the lane, 99.5%
have a time to collision of 5 s or more, where the one-sided inverse-tau term sits at its floor and
costs nothing; real followers nevertheless brake in some of those cases, mostly gently. Both terms are
shaped for avoiding collisions, which is what the model is for, and leave most of ordinary driving to
the gentler terms [Study].""")

ITEM4 = new_para("""Naturalistic onsets now point to the task or the paradigm. On 2,208 real
closing cut-ins in the highD dataset, whether the follower brakes within 3 s is predicted slightly
better by inverse time to collision than by the expansion rate (area under the ROC curve 0.739
against 0.713; difference 0.026, 95% interval 0.006 to 0.043), at every braking threshold we tried
and at short and long gaps alike. So video judgments follow the expansion rate, while executed
braking in real traffic follows inverse tau, as Xue et al. found in the simulator [Study]. The
model's perceptual front end and its inverse-tau preference may each be right for its own job
[Opinion].""")

OLD5 = """and beyond the adjacent lane [OSF]. At a 3.5 s gap moderate braking would suffice, so we
read these departures as a property of the lane-change control at speed rather than as a
deliberate trade-off [Opinion]; either way, analyses at 25 m/s should track road
departure as its own outcome class."""

NEW5 = f"""and beyond the adjacent lane [OSF]. At a 3.5 s gap moderate braking would suffice.

{M}{LABEL} *(Reworded; the edition you received read: "we read these departures as a property of
the lane-change control at speed rather than as a deliberate trade-off [Opinion]".)* Whether these
departures are best read as a property of the lane-change control at speed or as a trade-off the
preference landscape makes on purpose is a question of reading on which we would defer to the
authors [Opinion]; either way, analyses at 25 m/s should track road departure as its own outcome
class."""


def replace_once(s: str, old: str, new: str) -> str:
    if s.count(old) != 1:
        raise SystemExit(f"anchor not found exactly once: {old[:70]!r}")
    return s.replace(old, new)


def main() -> None:
    s = SRC.read_text(encoding="utf-8")
    s = replace_once(s, "## What this handbook is\n", BANNER + "## What this handbook is\n")
    s = replace_once(s, """*Revised 3 September 2026. The first edition""",
                     f"""{M}*Version of 28 September 2026: beyond the edition you received (see the notice below).*

*Revised 3 September 2026. The first edition""")
    s = replace_once(s, """  scenarios outside the published three. Stated so they can be checked; not the authors'
  claims, and not yet peer reviewed""",
                     f"""  scenarios outside the published three. Stated so they can be checked; not the authors'
  claims, and not yet peer reviewed

  {M}*New in this version:* since 28 September, [Study] also covers naturalistic motorway data (the
  highD dataset: 60 drone recordings of German motorways)""")
    # item 4: chapter 3, after the looming passage
    s = replace_once(s, "against a braking lead) is open; naturalistic onsets would settle it [Opinion].\n",
                     "against a braking lead) is open; naturalistic onsets would settle it [Opinion].\n\n" + ITEM4 + "\n")
    # item 1: chapter 5, after the drift bullet
    s = replace_once(s, "  drift is a real property with small near-conflict consequences; designs with long\n"
                        "  benign run-ins are where it would bite [Study].\n",
                     "  drift is a real property with small near-conflict consequences; designs with long\n"
                     "  benign run-ins are where it would bite [Study].\n\n  " + ITEM1.replace("\n", "\n  ") + "\n")
    # item 5: the road departures
    s = replace_once(s, OLD5, NEW5)
    # item 2: chapter 5, a new bullet after "Response time is not a parameter you set"
    anchor = "  landscape. To move it, you move those (chapter 09 lists which moves what).\n"
    s = replace_once(s, anchor, anchor + ITEM2 + "\n")
    # item 3: chapter 7, end of Part A
    s = replace_once(s, "\n## Part B: normal for the others — the three scenarios in detail",
                     "\n" + ITEM3 + "\n\n## Part B: normal for the others — the three scenarios in detail")
    OUT.write_text(s, encoding="utf-8")
    print(f"wrote {OUT.name}: {s.count(M)} marked paragraphs")

    sys.path.insert(0, str(DOCS / "handbook"))
    sys.path.insert(0, str(DOCS))
    from build_handbook import color_revisions   # noqa: E402  (knows the {{R8}} color)
    docx = OUT.with_suffix(".docx")
    subprocess.run(["pandoc", str(OUT), "-o", str(docx), "--from", "markdown", "--resource-path", str(HERE)],
                   check=True)
    print(f"docx: {docx.name}, {color_revisions(docx)} paragraphs colored")
    subprocess.run([sys.executable, str(DOCS / "build_pdf.py"), str(OUT)], check=True)


if __name__ == "__main__":
    main()
