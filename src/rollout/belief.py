"""The belief at the freeze: the scene read into a Gaussian, plus the latent intention.

Card JJ.1, step 1 of the implementer's brief (`handover_jj1_implementation.md` section 3.1);
construction and every constant's motivation in `docs/rollout_boundary_design_note.md` section 1.1.

The frame
---------
Everything downstream lives in **the freeze frame**: a fixed rigid frame whose origin is the
ego's position at t0 and whose x-axis is the direction of the ego's motion at t0. It does not
move with the ego afterwards -- the ego's policies move the ego within it, and the relative
position `dx, dy` is formed in `efe.py`. On the studies' straight roads the frame's x-axis is
the road; on the left turn it is the ego's heading at the decision moment, which is a fixed
direction like any other, so the oncoming car still travels in a straight line in it.

The jitter floors
-----------------
Not typed from memory: they are card HS.1's measurements, and `verify_floors()` reads them back
out of the docstring of `replication/czb/hs1_situational_surprise.py` and fails if the numbers
there ever change. The lines cited, verbatim from that docstring:

  second study, 30 Hz, 0.3 s velocity window
    "a 0.3 s window leaves at most 0.065 m longitudinal and 0.004 m lateral"
    (99.9th percentile over all 90 study-2 traces, prediction error at h = 1 s, so the implied
    velocity floors are 0.065 m/s longitudinal and 0.004 m/s lateral)
    "sigma0 = 0.1 m   PRIMARY. The noticeable positional discrepancy." -- the position floor.

  first study, 10 Hz, 1.0 s velocity window
    "the steady-driving floor at h = 1 s is 3.17 m longitudinal with a 0.3 s velocity window
     and 1.17 m with 1.0 s, against 0.13 m lateral"   -> velocity floor 1.17 m/s longitudinal;
     the lateral one is given to three figures on the sigma0_lat line below, 0.133 m/s
    "sigma0_lat = 1.5 x 0.133 = 0.20 m, sigma0_lon = 1.5 x 1.17 = 1.8 m"  -> position floors

The two velocity windows (0.3 s and 1.0 s) are cards G.1's and PC.1's, for the studies' sample
spacings, and are not tuned here.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
HS1_SCRIPT = REPO / "replication" / "czb" / "hs1_situational_surprise.py"

# --- the velocity windows (cards G.1 and PC.1; the studies' sample spacings) -------------
WINDOW_STUDY2_S = 0.3        # s, 30 Hz traces: card G.1's clearance-rate window
WINDOW_STUDY1_S = 1.0        # s, 10 Hz traces: card HS.1's corrected window

# --- the intention likelihood (design note section 1.1) ---------------------------------
P_CHANGE_PRIOR = 0.07        # card G.1's fitted gate at the pre-onset cells (0.063-0.070)
P_CHANGE_PRIOR_SWEEP = (0.02, 0.07, 0.20)
V_LC_MPS = 1.2               # G.1's post-onset lateral mean -1.137 m/s; 3.65 m lane in ~3 s
SD_LC_MPS = 0.4              # the spread of that same column


@dataclass(frozen=True)
class Floors:
    """One study's measured jitter floors (card HS.1). Positions in m, rates in m/s."""
    name: str
    window_s: float
    sd_pos_lon: float
    sd_pos_lat: float
    sd_v_lon: float
    sd_v_lat: float

    @property
    def sd_pos(self) -> float:
        """The position floor used for the fan's sigma_x, sigma_y: the larger of the two."""
        return max(self.sd_pos_lon, self.sd_pos_lat)


# Card HS.1's measurements, cited line by line in the module docstring and checked by
# `verify_floors()` against that script's own docstring.
FLOORS_STUDY2 = Floors(name="study2", window_s=WINDOW_STUDY2_S,
                       sd_pos_lon=0.1, sd_pos_lat=0.1,      # sigma0 = 0.1 m, PRIMARY
                       sd_v_lon=0.065, sd_v_lat=0.004)
FLOORS_STUDY1 = Floors(name="study1", window_s=WINDOW_STUDY1_S,
                       sd_pos_lon=1.8, sd_pos_lat=0.20,     # sigma0_lon, sigma0_lat
                       sd_v_lon=1.17, sd_v_lat=0.133)

# The exact substrings of card HS.1's docstring each floor is read from. `verify_floors()`
# fails if any of them stops being there, which is the mechanism that keeps this module from
# quoting a floor that the card no longer reports.
FLOOR_CITATIONS = (
    "a 0.3 s window leaves at most 0.065 m longitudinal and 0.004 m lateral",
    "sigma0 = 0.1 m   PRIMARY",
    "floor at h = 1 s is 3.17 m longitudinal with a 0.3 s velocity window and 1.17 m",
    "sigma0_lat = 1.5 x 0.133 = 0.20 m, sigma0_lon = 1.5 x 1.17 = 1.8 m",
    "sigma0_lat = 1.5 x 0.133 = 0.20 m, sigma0_lon = 1.5 x 1.17 = 1.8 m",
)


def hs1_docstring() -> str:
    """Card HS.1's module docstring, read from the file (never imported: that script loads
    study data at call time and is pre-registered)."""
    tree = ast.parse(HS1_SCRIPT.read_text(encoding="utf-8"))
    return ast.get_docstring(tree) or ""


def verify_floors() -> list[str]:
    """Return the citations that are NO LONGER present in card HS.1's docstring (empty =
    every floor above is still the one that card measured)."""
    doc = hs1_docstring()
    return [c for c in FLOOR_CITATIONS if c not in doc]


# ---------------------------------------------------------------------------------------
# the scene and the belief
# ---------------------------------------------------------------------------------------

@dataclass
class Scene:
    """Two road users' world-frame traces on a common time grid, with their dimensions.

    This is the one adapter every scenario loader produces; nothing below knows which study
    a scene came from. `heading` is in radians in the world frame and is used only where a
    body is stationary (positions give the heading otherwise), exactly as
    `comfortzone.conflict.planned_path` does.
    """
    t: np.ndarray
    ego_x: np.ndarray
    ego_y: np.ndarray
    ego_heading: np.ndarray
    ego_speed: np.ndarray
    oth_x: np.ndarray
    oth_y: np.ndarray
    oth_heading: np.ndarray
    oth_speed: np.ndarray
    ego_len: float
    ego_wid: float
    oth_len: float
    oth_wid: float
    name: str = ""


@dataclass
class Frame:
    """The freeze frame: origin at the ego's position at t0, x-axis along its motion there."""
    x0: float
    y0: float
    heading: float

    def to_frame(self, x, y) -> tuple[np.ndarray, np.ndarray]:
        c, s = np.cos(-self.heading), np.sin(-self.heading)
        dx, dy = np.asarray(x, float) - self.x0, np.asarray(y, float) - self.y0
        return c * dx - s * dy, s * dx + c * dy

    def heading_in_frame(self, h) -> np.ndarray:
        return np.asarray(h, float) - self.heading


@dataclass
class Belief:
    """The Gaussian belief about the present at the freeze, in the freeze frame."""
    x_rel: float      # other's longitudinal position relative to the ego, centre to centre [m], + ahead
    y_rel: float      # other's lateral position relative to the ego [m]
    v_ego: float
    v_oth: float      # speeds along the road [m/s]
    vy_oth: float     # other's lateral rate [m/s], backward difference over `window_s`
    sd_pos: float     # measurement sd of positions (the jitter floor) [m]
    sd_vy: float      # measurement sd of the lateral rate (the jitter floor) [m/s]
    p_change: float   # P(other is changing lanes into the ego's lane)
    ego_len: float
    ego_wid: float
    oth_len: float
    oth_wid: float
    # --- context the scoring needs, beyond the brief's list ------------------------------
    frame: Frame | None = None
    oth_heading: float = 0.0      # the other's heading in the freeze frame [rad]
    vx_oth: float = 0.0           # the other's longitudinal rate in the frame [m/s]
    t0: float = 0.0
    floors: Floors | None = None
    name: str = ""

    @property
    def toward_sign(self) -> float:
        """`sign` of the design note's likelihood: the change is toward the ego's lane when
        the other's lateral rate is -v_lc * sign(y_rel)."""
        s = float(np.sign(self.y_rel))
        return s if s != 0.0 else 1.0


def _index_at(t: np.ndarray, t_at: float) -> int:
    return int(np.clip(np.searchsorted(t, t_at, side="right") - 1, 0, len(t) - 1))


def belief_at(scene: Scene, t0: float, floors: Floors, p_change_prior: float = P_CHANGE_PRIOR,
              with_intention: bool = True) -> Belief:
    """Read the scene at t0 into a belief, and update the intention over the window.

    The ego's direction of motion at t0 is taken over the same velocity window as every rate
    (one-sample velocities are unusable on these traces: card HS.1's docstring).
    """
    t = np.asarray(scene.t, float)
    if t0 < t[0] + floors.window_s - 1e-9:
        raise ValueError(f"{scene.name}: the {floors.window_s} s window is not available at "
                         f"t0 = {t0} (trace starts at {t[0]:.3f})")
    i = _index_at(t, t0)
    j = _index_at(t, t0 - floors.window_s)
    span = float(t[i] - t[j])
    if span < 0.5 * floors.window_s:
        raise ValueError(f"{scene.name}: velocity window {floors.window_s} s not available at {t0}")

    vx_e = (scene.ego_x[i] - scene.ego_x[j]) / span
    vy_e = (scene.ego_y[i] - scene.ego_y[j]) / span
    speed_e = float(np.hypot(vx_e, vy_e))
    head = float(np.arctan2(vy_e, vx_e)) if speed_e > 1e-3 else float(scene.ego_heading[i])
    frame = Frame(float(scene.ego_x[i]), float(scene.ego_y[i]), head)

    ox, oy = frame.to_frame(scene.oth_x, scene.oth_y)
    x_rel, y_rel = float(ox[i]), float(oy[i])
    vx_o = float((ox[i] - ox[j]) / span)
    vy_o = float((oy[i] - oy[j]) / span)

    p_change = p_change_prior
    if with_intention:
        p_change = update_intention(p_change_prior, vy_o, floors.sd_v_lat,
                                    sign=float(np.sign(y_rel)) or 1.0)

    return Belief(x_rel=x_rel, y_rel=y_rel,
                  v_ego=float(scene.ego_speed[i]), v_oth=float(scene.oth_speed[i]),
                  vy_oth=vy_o, sd_pos=floors.sd_pos, sd_vy=floors.sd_v_lat,
                  p_change=p_change,
                  ego_len=scene.ego_len, ego_wid=scene.ego_wid,
                  oth_len=scene.oth_len, oth_wid=scene.oth_wid,
                  frame=frame, oth_heading=float(frame.heading_in_frame(scene.oth_heading[i])),
                  vx_oth=vx_o, t0=float(t[i]), floors=floors, name=scene.name)


def _log_gauss(x: float, mu: float, sd: float) -> float:
    sd = max(float(sd), 1e-12)
    return float(-0.5 * ((x - mu) / sd) ** 2 - np.log(sd))


def update_intention(p0: float, vy_obs: float, sd_vy: float, v_lc: float = V_LC_MPS,
                     sd_lc: float = SD_LC_MPS, sign: float = 1.0,
                     one_sided: bool = True) -> float:
    """One Bayesian update of P(changing lanes into the ego's lane) from the lateral rate.

    Likelihoods, exactly as the design note fixes them: N(vy | 0, sd_vy) for "keeping" and
    N(vy | -v_lc * sign, sd_lc) for "changing", `sign` chosen so that the change is toward the
    ego's lane. `sd_vy` is the measured jitter floor of the rate, so on these simulator-clean
    traces "keeping" is a very sharp likelihood.

    `one_sided` (default True) -- IMPLEMENTATION DECISION of 2026-09-18, query JJ1.Q6, taken
    because property test (1) of the brief requires it and the design note's own words support
    it. The log-likelihood ratio is clipped below at zero, so the update can only RAISE the
    probability of a change and never lower it below the prior. The reason is what p0 is: the
    design note calls it "the prior BEFORE ANY LATERAL MOTION" and motivates its value by
    card G.1's fitted gate sitting at 0.063-0.070 in *every* pre-onset cell -- that is, p0 is
    already the belief held while no lateral motion is seen, so an observation at the jitter
    floor must return it rather than drive it to 1e-12. Without the clip the pre-onset cells
    would carry p_change ~ 1e-40 instead of 0.07 (the traces' lateral floor is 0.004 m/s) and
    the emergence claim of rule (b) would be tested against a construction the design note did
    not describe. `one_sided=False` restores the plain ratio and is reported as a sensitivity.
    """
    p0 = float(np.clip(p0, 1e-12, 1 - 1e-12))
    lr = _log_gauss(vy_obs, -v_lc * sign, sd_lc) - _log_gauss(vy_obs, 0.0, sd_vy)
    if one_sided:
        lr = max(lr, 0.0)
    logit = np.log(p0 / (1.0 - p0)) + lr
    return float(1.0 / (1.0 + np.exp(-np.clip(logit, -700.0, 700.0))))
