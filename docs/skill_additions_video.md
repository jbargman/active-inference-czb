# Proposed additions to `chalmers-slide-generation-jonas`

*Written 2026-09-03 from the concepts-deck work (v2 → v8). Everything here cost real time
today and none of it is in the skill. The skill already covers click-build animations
(`<p:timing>`, `pptx_anim.py`), `PermissionError`, `picture_fit`, and render-to-verify — this
is the missing chapter on **data-driven animations embedded as video**.*

Suggested placement: a new section after "Animations — the rebuild destroys them unless you
carry them over", titled **"Moving figures: embed video, not GIF"**. The last part (§7) belongs
in "Gotchas that cost real time"; §8 belongs in "Verify by rendering".

---

## 0 Offer a moving figure whenever the point is a process

*Jonas, 2026-09-03: "consider creating videos when it is possible."*

Default to a still. But when the thing being explained **unfolds** — a quantity building up, a
distribution filling in, a threshold being crossed, one factor separating from another over
time — a short built-up animation carries it far better than a static chart, and this audience
responds to them. The concepts deck ended at 12 animated slides of 19 and the animations are
what Jonas reviews first.

Signals that a slide wants a moving figure:

- the caption would otherwise say "first … then … finally";
- the figure has a *before* and an *after* state and the interesting part is the transition;
- you are tempted to draw three small multiples of the same axes;
- the point is that two things which look different are actually the same, or vice versa.

Signals it does not: a table; a scoreboard of final numbers; a slide the audience will read
rather than watch; anything where the still already says it in one glance.

Cost is real — a build plus an encode is minutes per figure, and the whole set can be 30–45
minutes — so propose it, do not assume it. And every animation still has to survive being
paused on its first frame, because that is what a printed deck shows (§3).

## 0b Font sizes: bigger than feels right in the notebook

*Jonas, 2026-09-03: "the font size needs to be larger than what you used ... in both figures
and videos."*

A matplotlib default that looks fine at 100% in an editor is too small once the figure is
scaled into a slide and projected to the back of a room. Today's concepts-deck figures used
roughly 9.5–12 pt for tick labels and annotations and 14–15 pt for titles at a 12.8 × 7.2 in
canvas; **that is about one step too small throughout.**

Working rule for a full-width slide figure at 12.8 × 7.2 in:

| element | today (too small) | use |
|---|---|---|
| in-frame caption | 14.5 | 17–18 |
| figure title | 14–15 | 17–19 |
| axis label | 11–12 | 14–15 |
| tick label | 9.5–11 | 13–14 |
| in-plot annotation, legend | 9–10.5 | 12–13 |
| small provenance note | 8.5–9 | 11 |

Set them once at the top rather than per-call:

```python
plt.rcParams.update({"font.size": 13, "axes.titlesize": 17, "axes.labelsize": 14,
                     "xtick.labelsize": 13, "ytick.labelsize": 13, "legend.fontsize": 12})
```

Two consequences to plan for, because raising sizes without them makes things worse: labels
that fitted before will now collide (re-check every annotation position by rendering, §8), and
long tick labels may need rotation or fewer ticks. Prefer fewer, larger labels to more, smaller
ones — a projected figure with six legible ticks beats one with twelve unreadable ones.

Historical note for this project: the concepts-deck animations up to v8 were **not** re-rendered
at the larger sizes, by Jonas's explicit instruction. Apply the rule to new figures.

## 1 Embed `.mp4`, not `.gif` — a GIF has no controls

PowerPoint plays an embedded GIF as an *image*: there is no scrub bar, and pausing it restarts
it from the first frame. For anything the presenter may want to step through, that is unusable.
An embedded H.264 `.mp4` gets PowerPoint's own media controls — a slider, and a pause that
resumes where it stopped.

```python
slide.shapes.add_movie(str(mp4), left, top, width, height,
                       poster_frame_image=str(poster), mime_type="video/mp4")
```

Keep a `.gif` fallback path: other consumers (a handbook, a web page, a README) still want one,
and `add_picture` is the right call when no `.mp4` sits beside it.

## 2 Render the animation ONCE, then transcode

**This is the expensive lesson.** Do not call `anim.save()` twice on the same `FuncAnimation`
to get both a `.gif` and an `.mp4`. The second call replays the frame function from frame 0,
but the artists still hold the first pass's final state — and a frame function that only *adds*
to its artists (the normal way to write a build-up: `line.set_data(x[:k], y[:k])`, `bars`
growing, points accumulating) never clears them. The second render therefore opens with the
entire animation already drawn.

The failure is invisible in the file you check most: the GIF is correct, so every still you
extract looks right while the video is wrong.

```python
def gif_to_mp4(gif: Path, fps: int) -> Path:
    """Transcode the finished GIF; write the poster from its FIRST frame."""
    mp4, poster = gif.with_suffix(".mp4"), gif.with_suffix(".png")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(gif),
         "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-r", str(fps),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
         "-movflags", "+faststart", str(mp4)],
        check=True)
    with Image.open(gif) as im:
        im.seek(0)
        im.convert("RGB").save(poster)
    return mp4
```

`yuv420p` and even dimensions are what PowerPoint will play; `+faststart` matters if the deck
is ever streamed.

## 3 The poster frame must be the FIRST frame

The poster is what shows in normal (non-slideshow) view. A *last*-frame poster is tempting —
a printed deck then shows the finished picture — but it makes the slide wipe itself the moment
the video is played, because playback starts at frame 0. The user reads that as "it has the
dots, removes them and adds them again".

Take the poster from the GIF's frame 0. Do **not** re-call `fn(0)` on the live figure to
produce it: same artist-state bug as §2, and it yields a hybrid still matching neither end of
the animation (everything final except the one artist frame 0 happens to set).

## 4 Verify the video, not the still

A rendered slide still comes from the *poster*. It can be perfect while the video is wrong.
Check the artefact the audience sees:

```python
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-vframes", "1", str(f0)])
a = np.asarray(Image.open(gif).convert("RGB"), float)     # GIF frame 0
b = np.asarray(Image.open(f0).convert("RGB"), float)      # MP4 frame 0
assert np.abs(a - b).mean() < 6                           # H.264 quantisation only
```

Then look at an early frame (`-vf "select=eq(n\,3)"`) of each animation and confirm it is
*building*, not already built.

**Do not compare frame counts.** GIF encoders merge identical consecutive frames into one with
a longer duration, so a 112-frame animation can be stored as 7 GIF frames and expand back to
112 in the `.mp4`. That is correct. Compare duration, or frame 0, or an early frame.

## 5 Drawing rules for build-up figures

- **A quantity that rises toward zero must not be a zero-anchored bar.** `log θ̇` climbs from
  −6 toward 0 as a situation sharpens; drawn as a bar from zero it *shrinks* as the thing it
  measures grows. Use a marker on a number line, with the threshold as a vertical rule.
- **Never hard-code axis limits on derived data.** A `set_ylim(-2.8, 2.8)` on z-scores clipped
  the most interesting driver, whose z was 3.14. Derive: `lim = 1.12 * abs(Z).max()`.
- **`ax.collections.clear()` no longer works** (matplotlib's `ArtistList` is read-only). Create
  one scatter up front and update it: `sc.set_offsets(np.c_[x, y]); sc.set_sizes(s)`.
- **Put growing legends, stat boxes and annotations where the data will not arrive.** A box
  placed in empty space on frame 0 is often under the curve by the last frame. Check the final
  frame, not the first, when positioning them.
- **Ticks and labels belong outside a bundle of connecting lines**, not between two columns of
  a parallel-coordinates plot.

## 6 Combining-mark glyphs do not render

`θ̇` (theta + U+0307) renders as a displaced blob in matplotlib's default font *and* in the
Chalmers template font. In figures use mathtext: `TH = r"$\dot{\theta}$"`. On slides, write the
quantity in words ("the optical expansion rate"), or spell it "theta-dot".

## 7 Rebuild economics

A full animation rebuild (render + encode) took ~45 minutes for nine figures; regenerating only
the posters and `.mp4`s from the already-correct tracked GIFs took seconds. When a defect is in
the derived artefacts and not in the animation, transcode — it is the identical operation the
build performs.

Run long builds in the background with output to a log, and track progress with **file mtimes**:
Python buffers stdout when redirected, so the log stays empty until the process exits.

## 8 Render slides to PNG for every layout change

Already in the skill for layout; it applies just as hard to figure-bearing slides. Every one of
these was caught only by looking: a stat box sitting on top of two density curves, two median
labels 0.27 s apart printed on each other, percentile labels colliding in a histogram panel,
and a legend over the top-left data points.

Render on a **copy** in a scratch directory through COM, and never call `$ppt.Quit()`.

## 9 Two content habits worth stating

- **Put the takeaway on the slide, not only in the animation's last phase.** A caption reading
  "takeaway on the picture" fails for anyone who pauses early or reads the deck. The axis slide
  drew a question from Jonas that its own final frame answers.
- **Pre-empt the obvious objection in the speaker notes.** If a figure invites a wrong reading
  ("the top curve is clearly the better signal"), answer it in the notes; that is where the
  presenter needs it, in the room.
- **Define jargon on the picture.** "Cell" appeared on six slides before anyone said what one
  was; the fix was a heading inside the figure, not a line in the notes.
