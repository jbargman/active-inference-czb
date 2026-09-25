---
# Machine-readable part. `src/comfortzone/display.py` reads THIS block (the YAML between the first
# two '---' lines); change a value here and every script that uses the transform follows.
transform: display_minification
version: 1
date: 2026-09-25
applies_to:            # stimuli shown as video on a participant's own desktop monitor
  - study1_cutin_video  # first crowd-sourced study (Random, Sequence and Button paradigms)
  - study2_cutin_video  # second crowd-sourced study
does_not_apply_to:      # optical input was the real world
  - highD
  - inD
  - test_track
parameters:
  screen_diagonal_in: 23.0      # monitor diagonal [inch]; "typically a standard 23-inch screen"
  screen_aspect_w: 16           # monitor aspect ratio, width part
  screen_aspect_h: 9            # monitor aspect ratio, height part
  viewing_distance_cm: 60.0     # eye to screen [cm]
  virtual_hfov_deg: 90.0        # horizontal field of view of the rendering camera [deg]
  image_width_fraction: 1.0     # shown image width / screen width (1.0 = full-screen video)
  camera_to_front_m: 0.0        # rendering camera to the ego's front bumper [m]; 0.0 keeps the
                                # pipeline's convention (card EL.1b: the observer at the bumper)
switch:
  env_var: CZB_DISPLAY_TRANSFORM
  values: ["off", "on"]
  default: "off"                # "off" reproduces every result so far exactly
---

# The display transform: from rendered kinematics to what the participants saw

*Written 2026-09-25 (night) at Jonas's request. The YAML block above is the single source of the
parameters; the code is `src/comfortzone/display.py`, its property checks `tests/test_display.py`,
and the comparison with the untransformed analyses is card DT.1
(`replication/czb/dt1_display_transform.py` → `replication/czb/out/dt1_display_transform.md`).*

## 1 The problem

The participants of the two crowd-sourced cut-in studies watched rendered clips on a desktop monitor
(about 60 cm away, typically a 23-inch 16:9 screen). The rendering camera had a 90° horizontal field
of view; the monitor, at that distance, fills only about 46° of the participant's. The picture is
therefore **minified**: every object subtends a smaller visual angle, and expands more slowly, than it
would have from the driver's seat of the virtual world. Every optical variable we computed so far
(the angular size θ and the looming rate θ̇ of card EL.1b) is the *rendered world's*, not the
*participant's*. Real-world data (highD, inD, the test track) carry the real optical variables. To
compare the two, the video's variables must be put in the participant's terms.

## 2 The geometry (exact)

Notation, all derived from the parameters above:

| symbol | definition | value with the defaults |
|---|---|---|
| S_w | screen width = diagonal × 2.54 × a_w / √(a_w² + a_h²) [cm] | 50.92 cm |
| I_w | image width = image_width_fraction × S_w [cm] | 50.92 cm |
| F | the rendering's focal length in screen units = (I_w / 2) / tan(HFOV_v / 2) [cm] | 25.46 cm |
| d | viewing distance [cm] | 60 cm |
| **k** | **the display gain F / d** | **0.4243** |
| HFOV_d | the horizontal angle the image fills for the viewer = 2 atan(I_w / (2d)) | 45.98° |

A pinhole camera maps a scene point at camera coordinates (X forward, Y lateral, Z up) to the screen
point (F·Y/X, F·Z/X). A viewer whose eye sits at distance d on the perpendicular through the image
centre sees that screen point in the direction

  tan β_Y = (F/d) · Y/X = Y / (X/k),  tan β_Z = Z / (X/k).

This is **exactly** the direction in which the viewer would see a scene point at (X/k, Y, Z). So:

> **The participant's optical array is that of an equivalent world in which every distance along the
> line of sight is multiplied by 1/k and nothing else changes** (lateral and vertical coordinates,
> object sizes, lateral speeds unchanged).

It holds at every azimuth, not only near the centre, and needs no small-angle approximation.
Assumptions: a flat screen; the eye centred in front of the image at distance d; square pixels (the
vertical field of view follows from the horizontal one); monocular optics (binocular disparity,
accommodation and the screen's own flatness cues are not modelled; they all say "a flat picture 60 cm
away" and are ignored here, as in the display literature's geometric-field-of-view account).

## 3 The transform of the kinematic variables

With r = gap + camera_to_front_m, the camera-to-target distance along the line of sight, and dv the
closing speed (dr/dt = −dv):

| variable | rendered world (so far) | as perceived (transform "on") | ratio perceived/rendered |
|---|---|---|---|
| distance r | r | r_p = r / k | 1/k = 2.36 |
| closing speed dv | dv | dv_p = dv / k | 1/k = 2.36 |
| lateral position, lateral clearance l0, lateral rate | y, l0, l̇ | unchanged | 1 |
| target width W | W | unchanged | 1 |
| angular size θ = 2 atan(W / 2r) | θ | θ_p = 2 atan(W k / 2r) | ≈ k (exactly k in the small-angle limit) |
| **looming θ̇ = W·dv / (r² + W²/4)** | θ̇ | **θ̇_p = W·dv_p / (r_p² + W²/4) = k·W·dv / (r² + k²W²/4)** | ≈ k; exactly k·(r² + W²/4)/(r² + k²W²/4) |
| TTC = r / dv | TTC | TTC_p = r_p / dv_p = TTC | **1 (invariant)** |
| inverse tau θ̇/θ | τ⁻¹ | ≈ τ⁻¹ (exact in the small-angle limit) | ≈ 1 |
| accelerations along the line of sight | a | a / k | 2.36 |

With `camera_to_front_m` = 0 (the default) the perceived variables are obtained by feeding the
pipeline's own formula (card EL.1b) with **gap / k and dv / k**. Off-axis (a target at lateral offset
y), the rear face's perceived angular width is atan((y + W/2)/r_p) − atan((y − W/2)/r_p); the pipeline
has always used the centred form, and this transform does not change that choice (`display.py`
offers the off-axis form for later use).

## 4 What this does and does not do to the results — read this before using it

1. **Looming-based levels shrink by k ≈ 0.42.** A comfort-zone level fitted on the video's looming,
   e.g. the intervention level 0.0320 rad/s (card JJ.10), becomes about 0.0136 rad/s of *perceived*
   looming. This is the level to compare with real-world looming (highD's 0.0388; Farewell's 0.02).
2. **TTC and inverse tau do not change.** Optical tau is invariant under magnification; the equivalent
   world scales distance and closing speed by the same factor. Every TTC-based result (the hard
   boundary on TTC, card NC.3j's 3.3 s, card NC.3l's 1.64 s, the TTC comparators) stands as it is.
   The transform does NOT, by itself, "offset things toward higher TTCs".
3. **The offset toward higher TTC appears when the perceived looming is carried to a real driver at
   the TRUE closing speed.** A real driver closing at the video's dv on a car of width W receives the
   participant's perceived looming θ̇_p at the distance r_b = √(W·dv / θ̇_p − W²/4), i.e. at
   TTC_b = r_b / dv ≈ TTC / √k = **1.54 × TTC**. That is convention (b) below, and it is the sense in
   which the video's boundary lies at a *higher real-world TTC* once the display is accounted for.
4. **Within-video model comparisons barely change.** Every probit-on-log-looming model absorbs a
   constant factor into its level (log θ̇_p = log θ̇ + log k + a small correction at short range), so
   held-out scores move only through that correction; spreads, gates (lateral, unchanged) and rank
   correlations (per-driver transfer, card TR.1) are unaffected.

### Two conventions for "the equivalent real-world situation"

| convention | what is matched | distance | closing speed | TTC | use it for |
|---|---|---|---|---|---|
| (a) optical (the default "on") | θ and θ̇ both, same W | r / k | dv / k | TTC | comparing optical variables (looming, angular size) with real-world data |
| (b) at true speed | θ̇ only, same W, true dv | √(W·dv/θ̇_p − W²/4) | dv | ≈ TTC / √k | stating a video boundary as a real-world TTC at the video's own speeds |

Convention (a) is exact about what reached the eye. Convention (b) assumes the participants knew the
true closing speed from somewhere other than the optics (e.g. the ego's speed from the instructions);
whether they did is not known, so (b) is reported beside (a), never in its place.

## 5 How to use it

- **Switch.** `CZB_DISPLAY_TRANSFORM=on` (environment) turns it on for code that asks
  `display.active_geometry()`; unset or `off` gives `None` and every function is the identity. Card
  DT.1 does not rely on the environment: it runs each analysis twice, explicitly.
- **Parameters.** Edit the YAML block at the top of this file, or pass overrides:
  `display.load_geometry(viewing_distance_cm=70)`.
- **Functions** (`src/comfortzone/display.py`): `gain(g)`, `display_hfov_deg(g)`,
  `perceived(gap, dv, W, g)` → dict of r_p, dv_p, θ_p, θ̇_p, TTC_p; `looming(gap, dv, W, g=None)`
  (the EL.1b formula, perceived when g is given); `offaxis_theta(gap, y, W, g)`;
  `ttc_at_true_speed(theta_dot_p, dv, W)` (convention b); `transform_level(level, gap, dv, W, g)`.
- **Pre-registered scripts are not modified** (standing rule). New analyses that must hold for both
  take a geometry argument; DT.1 re-runs the existing ones by importing their functions.

## 6 Open points for Jonas

- The parameters are the stated defaults; if the studies' logs carry screen resolution or window
  size, `image_width_fraction` is the one most likely to be below 1 (a video in a browser window).
- Where was the rendering camera (the driver's eye, the bumper)? `camera_to_front_m` = 0 keeps the
  pipeline's convention; a driver's eye is about 1.5–2.5 m behind the bumper, which matters at the
  shortest gaps (TTC and looming both).
- Literature (to verify before citing): minifying the geometric field of view relative to the display
  field of view makes distances look larger and speeds faster in driving simulators (e.g. Diels &
  Parkes, 2010, on geometric field of view and perceived speed).
