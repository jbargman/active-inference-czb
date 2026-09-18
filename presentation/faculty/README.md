# Faculty-assembly deck: how the in-depth LLM review was done

`build_llm_review_deck.py` → `LLM-in-depth-review-faculty.pptx` (3 slides, Chalmers
template, English).

Built for Jonas's faculty-assembly item on where LLMs were used in his work. The example is
the August 2026 in-depth review of Schumann et al. (2026) in Nature Communications, written
up as `docs/method_review.md`.

Sources for every fact on the slides, so the deck can be rebuilt and checked:

| slide | claim | source |
|---|---|---|
| 1 | three findings, ten code/paper differences, five questions | `docs/method_review.md` §1, §5, §9 |
| 1 | 3.1 GB deposit, 896 runs, ~10 code files | ibid. §2.1, §2.2 |
| 1 | 50 000–100 000 per step, 18–44% of the evidence | ibid. §4.2, computed by `replication/review_osf.py` |
| 2 | both prompts, verbatim with timestamps | the prompt log (the `prompt-log` skill), 2026-08-23 |
| 2 | the six days of setup | the same log, 2026-08-17 to 08-20 |
| 3 | what was not done | `docs/method_review.md` §2.3 |
| 3 | the source tags | ibid., header |

The prompts are quoted as typed, typos included — that is the point of showing them.

Rebuilt with `python presentation/faculty/build_llm_review_deck.py`. **If Jonas has edited
the .pptx by hand, do not rerun this script onto it**; copy and augment instead, per
`presentation/talk/README.md` and the `chalmers-slide-generation-jonas` skill.

Checked with the skill's `check_slides.py` (0 off-slide, 0 overrun, 0 invisible) and by
rendering all three slides to PNG through PowerPoint COM on a scratchpad copy, 2026-09-18.
Two things the render caught that the checker did not: the slide number was sitting under
the Chalmers wordmark, and slide 3 had a seven-centimetre hole between the columns and the
closing strip.
