# The review of 2026-09-22: working material

The review itself is `docs/review_2026-09-22.md`. Every number it quotes comes from
`replication/czb/review_2026_09_22_checks.py` (output `replication/czb/out/review_2026_09_22_checks.md`)
or from cards S1.5 and S1.6, which were run the same night.

`scratch/` holds the four parallel reviewers' analysis scripts **exactly as they ran them**, kept as
evidence of what was looked at. They are not part of the pipeline: they carry absolute paths, they
read an `SCR` environment variable for their working directory, some depend on intermediate files
that were not kept (`press_levels.pkl`, `tt_*.csv`), and none writes a tracked output. Nothing should
be quoted from them. Where the review relies on a reviewer's result that the checks script does not
reproduce, the review says "reviewer's scratch" next to it.

| prefix | slice reviewed |
|---|---|
| `reviewA_` | the `src/rollout` package and cards JJ.2, JJ.3, JJ.2b |
| `reviewB_` | cards JJ.4, RE.3, GM.1a (the statistics) |
| `reviewC_` | cards RE.1, RE.2, RE.4 (the diagnosis) |
| reviewer D | cards S1.1, S1.2, S1.4, the three argument documents, the handover and the query register; it wrote no scripts of its own beyond one-off recomputations |
