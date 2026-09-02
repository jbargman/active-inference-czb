# Animation shot list for the talks

*2026-09-02. Jonas asked for more GIF/video visualizations "in several other places,
even for subsystems", after the rear-end event animation (`figures/event_anim.gif`,
built by `make_event_animation.py` from the OSF deposit). This is the specification for
the next ones, written so a cheaper session can build each shot without re-deriving the
science. Every shot follows the rule the first one set: **nothing sketched** — every
moving quantity is read from a tracked output or a study trace, and the script that
reads it is committed next to the GIF.*

## Conventions (from the first animation and the slide skill)

- Matplotlib frames assembled with PIL into a looping GIF; 10 frames per second; a loop
  of 8–15 s; a one-second hold on the final frame. PowerPoint plays embedded GIFs in
  slideshow mode; each slide that carries one also gets the final frame as a static PNG
  fallback.
- Canvas aspect matched to the slot on the slide (the body area is 31.2 × 12.9 cm, so
  about 2.4:1); labels and ticks 13–15 pt; arrows `-|>`, `lw=4`, `mutation_scale=28`.
- Colors from the deck: purple `#472CBE` for the driver model or the quantity under
  test, teal `#61E9D2`/`#1B8F7A` for what worked or the data, pink `#D987BA`/`#B03E82`
  for what failed, blue `#36B7F6` for a comparator, grey for context.
- A caption line under every animation naming the source (file, seed, cells) and the
  parameter values that matter, exactly as the first one does.
- Inspect every frame set before it goes on a slide: legends and annotations placed
  against the data that were actually plotted, not the data one had in mind.

## The shots, in the order I would build them

### S1 — the belief cloud catching the lead's braking (subsystem: perception and beliefs)

- **Claim on the slide.** Detection is not the bottleneck: the particle cloud snaps to
  the new reality within one 0.2 s step; the response comes 0.6 s later when the plan,
  not the world, has accumulated evidence of failure.
- **Source.** The OSF deposit's per-timestep pickles for `Results_rear_end/Exp_7`,
  seed 0 (the same event as the first animation); the 75 weighted particles' believed
  lead deceleration and gap per step, the executed pedal, and the accumulator
  reconstructed as in `make_event_animation.py`.
- **What must be visible.** Left: the 75 particles as points in (believed gap, believed
  lead deceleration), weights as marker size, the true state as a hollow marker; the
  cloud is diffuse before t = 0.8 s and collapses onto −2 m/s² in one frame. Right: the
  accumulator filling, the threshold line, the re-plan mark at 1.4 s, the pedal at 1.6 s.
  A shared time cursor.
- **What the viewer should conclude.** The cloud moved at 0.8 s; the pedal moved at
  1.6 s; the 0.8 s in between is the model's response time and it is evidence, not
  perception.
- **Effort.** Small; the loader exists. Check the deposit's particle array axis order
  against `notes/05_validation.md` §4b before trusting it.

### S2 — a comfort-zone crossing in the button data (subsystem: the field and the level)

- **Claim.** What a CZB crossing looks like in human data: the field rises along the
  clip, and the presses pile up where it crosses the population's levels.
- **Source.** Study 1 Button cut-in clips TTC4 and TTC6 (`comfortzone.czb_data.button_cutin_trials`
  for press times since onset; `comfortzone.cutin.cutin_predictors` for the deficit
  series with the CZB staging); the 50th, 80th and 95th percentile levels from
  `replication/czb/out/stage1_summary.md` (5 400, 6 390, 7 503).
- **What must be visible.** Top: the clip's plan view (ego, target, lateral position from
  the trace). Middle: the running-maximum deficit against time since onset with the three
  level lines. Bottom: the empirical CDF of press times growing as the cursor moves,
  with censored trials shown as a final step. One panel per clip, side by side.
- **What the viewer should conclude.** The levels are on the field's scale; where the
  field crosses them is where presses accumulate; the 95th-percentile level is never
  reached in the milder clip (card C's "whether, not only when").
- **Caveat on the slide.** Say that the axis itself was ruled against at R.2; this shot
  shows the deliverable's scale, not the axis's validity (the standing caveat of
  `out/percentile_sensitivity.md`).

### S3 — matched-TTC rows: gap orders the response, the field does not (the R.2 verdict)

- **Claim.** On the design built to separate them, the gap orders every row and the
  field does not.
- **Source.** `replication/czb/out/cutin2_cells.csv` (288 CP2–CP5 cells: `p`, `n`,
  `distance`, `ttc_true`, `deficit_max`).
- **What must be visible.** Two scatter panels sharing a y axis (P(intervene)): left
  x = log gap, right x = field covariate. The animation steps through the 24 matched-TTC
  rows: each frame highlights one row's cells (marker size by n), draws the within-row
  rank correlation as a label, and fades previous rows to grey. End frame: all rows, the
  fitted log-gap threshold curve on the left, the fitted field threshold on the right,
  and the held-out wRMSE (0.152 / 0.347) in the corner.
- **What the viewer should conclude.** Left panel: a monotone cloud, every row sloping
  down. Right: a cloud with no slope, rows sloping either way.

### S4 — why the field fails, cell by cell (the pipeline review's mechanism)

- **Claim.** The lane-entry gate suppresses the deficit exactly where participants
  respond most, because it makes the conflict depend on the lateral pace and
  participants do not.
- **Source.** The three study-2 traces `LC_dv21_Tlc{2p0,3p0,4p0}_TTC02` and the CP5 cells
  (`out/cutin2_cells.csv`; P = 0.85, 0.92, 0.92; deficit 10 005, 4 205, 171; the
  lane-entry weight per frame from `cutin_predictors`).
- **What must be visible.** Three columns, one per lane-change duration. Top: plan view
  with the target's lateral position moving at its pace; the predicted overlap at
  closure (the gate) as a shaded bar that fills for the 2 s change and barely for the
  4 s one. Bottom: the deficit series over the shown window, and the human P(intervene)
  as a horizontal marker on a second axis. Shared cursor, 10 s window.
- **What the viewer should conclude.** The humans' marker is at the same height in all
  three columns; the field's curve is high, medium, and flat.

### S5 — the ellipse: why "exceed both" is not the same criterion (the ellipse design note)

- **Claim.** Two marginal 80th percentiles under a conjunction rule trigger on 4% of
  states; a joint 80% ellipse triggers on 20%, and allows trade-offs.
- **Source.** Synthetic, and labeled as such on the slide: a bivariate Gaussian with a
  stated correlation; no project data. (If card EL.1 has run, add a second version with
  the study-2 cells and the fitted level set.)
- **What must be visible.** A cloud of points; the two marginal 80th-percentile lines
  appear, then the rectangle they define, then the count of points outside it (4%); then
  the ellipse at χ²₂ 0.8, the count outside it (20%); then one point that is inside the
  ellipse but outside the rectangle, to show the trade-off.
- **What the viewer should conclude.** The criterion changed by a factor of five without
  anyone deciding it should.

### S6 — surprise onset is independent of the lateral pace (card Q5.1, after it runs)

- **Claim.** A belief-mismatch surprise about the target's lateral position starts at
  the same frame for the 2, 3 and 4 s lane changes; its size differs, its onset does not.
- **Source.** `replication/czb/out/world_surprise.md` and the series the card writes
  (one file per trace); the same three traces as S4.
- **What must be visible.** The target's lateral position with the constant-velocity
  prediction fan (mean and ±2σ over the lookahead) made h seconds earlier; below it the
  surprise series; three columns; a vertical line at manoeuvre onset.
- **What the viewer should conclude.** The three surprise series leave zero at the same
  frame.
- **Do not build before Q5.1 has run**; the shot depends on its parameters.

### S7 — the glance gate: braking mid-glance (subsystem: gaze, crash causation)

- **Claim.** The model gates evidence, not inference: a driver who has registered the
  lead's braking keeps responding during an off-road glance; the counterfactual-behavior
  model waits until the eyes return.
- **Source.** The crash-causation outputs: one QUADRIS seed under the glance component
  with a glance starting after the conflict is registered, for both response processes
  (`replication/causation/`; pick a seed from the summary tables in
  `docs/crash_causation_results.md` and name it on the slide). Verify which tracked
  per-seed traces exist before starting; the full-population CSVs are gitignored and
  may need regenerating from the logged commands.
- **What must be visible.** Two rows (active-inference response, CBM response): gap and
  speed over time, the glance window shaded, the brake onset marked. The accumulator
  for the active-inference row keeps filling through the shading.
- **What the viewer should conclude.** Same glance, same conflict: one row brakes inside
  the shaded window, the other 0.5 s after it ends.

## Not on the list, and why

- A full closed-loop cut-in run: the closed loop costs seconds to tens of seconds of CPU
  per step and the comfort-zone method never runs it; an animation would misrepresent
  what the deliverable does.
- Anything drawn from the handbook's schematics without data behind it (the loop, the
  preference terms): those are diagrams and should stay diagrams.
