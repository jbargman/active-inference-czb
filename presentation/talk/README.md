# The 60-minute talk, and the 15-20 minute project-group version

*Built 2026-09-01 from `docs/handbook/` (all 15 chapters), `docs/r2_gate_decisions.md`,
`docs/active_inference_scope_map.md`, `docs/czb_validation_roadmap.md`,
`docs/method_review.md` and the tracked analysis outputs under
`replication/czb/out/` and `replication/causation/`.*

## What is here

| File | What it is |
|---|---|
| `ai_czb_talk.pptx` | the 60-minute deck: 46 slides on the Chalmers Swedish template, every slide with speaker notes and a time budget (56 min of content, leaving room for questions in the hour) |
| `build_talk.py` | builds the 60-minute deck from scratch |
| `ai_czb_short_talk.pptx` | the 15-20 minute project-group version: 13 slides (notes budget 19.8 min; two CUTTABLE slides bring it to ~16.5) |
| `build_short_talk.py` | builds the short deck; imports the layout helpers from `build_talk.py`, so the two decks share one set of conventions |
| `make_talk_figures.py` | the talk versions of the diagrams and the two live-computed figures |
| `make_event_animation.py` | the animated demonstration, read from the OSF deposit |
| `figures/` | generated; safe to delete and rebuild |

Rebuild everything with:

```bash
python presentation/talk/make_event_animation.py && python presentation/talk/make_talk_figures.py && python presentation/talk/build_talk.py
```

## The structure the deck follows

Nine parts, matching the brief it was written for: (1) the paradigm and why we needed
a different kind of driver model; (2) the method, with the loop diagram and the six
preference terms; (3) one event through the model's eyes, **animated**; (4) what
changes between scenarios and what does not; (5) crash causation; (6) how the
comfort-zone boundary was framed in active-inference terms and why; (7) the steps
taken and what each one showed, including the two pre-registered failures; (8) where
the project stands; (9) where it goes, and the data ask. One slide covers all five
data sources.

Four slides are marked **CUTTABLE** in their speaker notes, in the order to drop them
if the talk is running long: the component table (11), the practices slide (37), the
severity-versus-timing dissociation (23), and the stack slide (40).

## The short (15-20 min) project-group version

*Built 2026-09-01 to Jonas's brief: (a) the overall idea of active inference and
surprise, (b) the CZB versions we tested, (c) where we ended up and why, (d) what we
should do now — with a short objectives slide and a short what-worked/what-did-not
summary slide, for a group of cognitive scientists, driver modelers and vehicle
safety engineers.*

13 slides: title · objectives · active inference in plain terms · the model loop ·
the event animation · the CZB level-set reading · the seven-step progression · the
R.1 timing failure · the R.2 axis verdict · what survived (the trait) · the
worked/did-not/open summary · what to do now · closing. Content is condensed from
the 60-minute deck; every number traces to the same tracked outputs. Rebuild:

```bash
python presentation/talk/build_short_talk.py
```

Notes budget 19.8 min; slides 5 (animation) and 8 (R.1) are marked CUTTABLE in that
order, bringing it to ~16.5 min. The same copy-and-augment rule below applies once
Jonas has hand-edited either deck.

## The animation

`figures/event_anim.gif` is the rear-end event of handbook chapter 02 — OSF deposit,
`Results_rear_end/Exp_7`, seed 0 — with **nothing sketched**. The vehicle states, the
executed pedal and the re-plan flag are read from the deposited arrays; the
accumulator is reconstructed from the deposited pragmatic-value components with the
run's own λ = 10^−5.95 and a threshold of 1, and it reproduces the deposit exactly:
re-plan at t = 1.4 s, brake at t = 1.6 s, final gap 2.05 m. PowerPoint plays embedded
GIFs in slideshow mode, so the slide needs no video codec and no external file.
Slide 16 carries the final frame as a static fallback.

## Figures: which are live and which are drawn

Live — regenerate if the underlying analysis moves:

- `boundary_talk.png` evaluates `src/comfortzone/field.py::critical_thw` at build time
- `cutin_before_after_talk.png` re-runs the construction of
  `replication/czb/cutin_field_check.py` on the study traces
- `event_anim.gif` / `event_static.png` read the OSF pickles
- `axis_scoreboard.png` and `trait_shared_fraction.png` are used unchanged from
  `docs/ai_scope_figures/`, and those read their numbers from tracked outputs

Drawn (schematics; every number in them is also stated with its source in the
documents): `lineage_talk.png`, `loop_talk.png`, `scenario_diff_talk.png`,
`field_claim_talk.png`, `stack_talk.png`, `progression_talk.png`.

Two talk figures deliberately differ from their handbook originals because the
handbook text has since been corrected:

- the loop diagram no longer says the accumulator is "exactly zero" while the plan
  works — the model's own expected shortfall is not (`docs/method_review.md` §4.2)
- the preference-term panel draws the closing-rate term **one-sided**, as the released
  code implements it rather than as the SI writes it

## Before rerunning this after Jonas has edited the deck

**Do not.** The build script constructs every slide from the template on each run, so
hand edits — animations above all — are not "lost", they never exist in the new file.
Once the deck has been reviewed and animated, copy the reviewed file and augment the
copy (`shutil.copyfile`, then `Presentation(dst)`), per the
`chalmers-slide-generation-jonas` skill. Supersede slides by hiding them
(`slide._element.set("show", "0")`), not by deleting them.

## Known judgment calls, for review

- **Length.** 46 slides is a lot for an hour. The budgets sum to 56 minutes with the
  dividers at 10 seconds each; the four CUTTABLE slides buy back about 5 minutes.
- **The framing of slide 41** ("the deliverable is a psychometric measurement
  instrument") is the scope map's framing, which that document itself flags as an
  interpretation rather than a gate decision. The alternative framing — a comparative
  study of criticality axes with a psychometric estimator — would change this slide
  and the closing slide.
- **The title slide** attributes the talk to Jonas alone; co-authors and the
  QUADRARUM / QUADRIS collaborators are not named anywhere in the deck yet.
- **R2.Q5 is still open**, so slide 44 presents the surprise-without-the-field
  question as a crux rather than a plan. If the exploration has run by the time the
  talk is given, that slide needs rewriting.
