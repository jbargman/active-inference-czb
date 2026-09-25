"""The display transform: from the rendered kinematics of a video clip to what the viewer saw.

The specification, the parameters and the reasoning are in `docs/display_transform.md`; this
module reads its YAML front matter, so the parameters live in one place. In short: a pinhole
rendering with horizontal field of view HFOV_v, shown on a flat screen whose image is I_w wide and
viewed from distance d, gives the viewer exactly the optical array of an equivalent world in which
every distance along the line of sight is divided by the gain k = (I_w / 2) / (d tan(HFOV_v / 2)).
Lateral positions, sizes and lateral speeds are unchanged; TTC is invariant; looming shrinks by
about k.

Every function takes a geometry `g`; `g=None` means "no transform" and returns the rendered-world
value, so a caller can run the same analysis with and without by passing `active_geometry()` or
`load_geometry()` / `None`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

SPEC = Path(__file__).resolve().parents[2] / "docs" / "display_transform.md"
ENV = "CZB_DISPLAY_TRANSFORM"


@dataclass(frozen=True)
class Geometry:
    screen_diagonal_in: float = 23.0
    screen_aspect_w: float = 16.0
    screen_aspect_h: float = 9.0
    viewing_distance_cm: float = 60.0
    virtual_hfov_deg: float = 90.0
    image_width_fraction: float = 1.0
    camera_to_front_m: float = 0.0


def _front_matter(path: Path) -> dict:
    import yaml
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    marks = [i for i, ln in enumerate(lines) if ln.strip() == "---"]
    if len(marks) < 2 or marks[0] != 0:
        raise ValueError(f"{path}: no YAML front matter")
    return yaml.safe_load("\n".join(lines[1:marks[1]]))


def load_geometry(path: str | Path | None = None, **overrides) -> Geometry:
    """The geometry from the spec's YAML block, with keyword overrides."""
    spec = _front_matter(Path(path) if path else SPEC)
    p = {k: float(v) for k, v in spec["parameters"].items()}
    unknown = set(overrides) - set(Geometry.__dataclass_fields__)
    if unknown:
        raise TypeError(f"unknown display parameters: {sorted(unknown)}")
    return replace(Geometry(**p), **{k: float(v) for k, v in overrides.items()})


def active_geometry(path: str | Path | None = None) -> Geometry | None:
    """The spec's geometry if the switch (env CZB_DISPLAY_TRANSFORM) is 'on', else None."""
    return load_geometry(path) if os.environ.get(ENV, "off").strip().lower() == "on" else None


def screen_width_cm(g: Geometry) -> float:
    a_w, a_h = g.screen_aspect_w, g.screen_aspect_h
    return g.screen_diagonal_in * 2.54 * a_w / np.hypot(a_w, a_h)


def image_width_cm(g: Geometry) -> float:
    return g.image_width_fraction * screen_width_cm(g)


def focal_cm(g: Geometry) -> float:
    return image_width_cm(g) / 2.0 / np.tan(np.radians(g.virtual_hfov_deg) / 2.0)


def gain(g: Geometry | None) -> float:
    """k = F / d: tan(seen direction) = k tan(rendered direction). 1.0 for no transform."""
    return 1.0 if g is None else focal_cm(g) / g.viewing_distance_cm


def display_hfov_deg(g: Geometry) -> float:
    return float(np.degrees(2.0 * np.arctan(image_width_cm(g) / (2.0 * g.viewing_distance_cm))))


def seen_direction(alpha, g: Geometry | None):
    """The direction [rad] in which the viewer sees a point rendered at azimuth alpha [rad]."""
    return np.arctan(gain(g) * np.tan(np.asarray(alpha, float)))


def perceived(gap, dv, W, g: Geometry | None) -> dict:
    """Convention (a): the equivalent world's distance, closing speed, angular size, looming, TTC.

    gap: bumper gap [m] as the pipeline uses it; dv: closing speed [m/s]; W: target width [m].
    With g=None these are the rendered world's values (the pipeline's so far).
    """
    k = gain(g)
    e = 0.0 if g is None else g.camera_to_front_m
    r = np.asarray(gap, float) + e
    dv = np.asarray(dv, float)
    W = np.asarray(W, float)
    r_p, dv_p = r / k, dv / k
    with np.errstate(divide="ignore", invalid="ignore"):
        ttc = r_p / dv_p
    return {"r": r_p, "dv": dv_p, "theta": 2.0 * np.arctan(W / (2.0 * r_p)),
            "theta_dot": W * dv_p / (r_p ** 2 + W ** 2 / 4.0), "ttc": ttc}


def looming(gap, dv, W, g: Geometry | None = None):
    """Card EL.1b's looming rate, W dv / (r^2 + W^2/4); perceived when a geometry is given."""
    return perceived(gap, dv, W, g)["theta_dot"]


def offaxis_theta(gap, y, W, g: Geometry | None = None):
    """Angular width of a rear face of width W centred at lateral offset y (exact, any azimuth)."""
    k = gain(g)
    e = 0.0 if g is None else g.camera_to_front_m
    r_p = (np.asarray(gap, float) + e) / k
    y = np.asarray(y, float)
    return np.arctan((y + W / 2.0) / r_p) - np.arctan((y - W / 2.0) / r_p)


def ttc_at_true_speed(theta_dot_p, dv, W):
    """Convention (b): the TTC at which a real driver closing at dv on a W-wide car receives theta_dot_p."""
    theta_dot_p, dv, W = (np.asarray(v, float) for v in (theta_dot_p, dv, W))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.sqrt(np.maximum(W * dv / theta_dot_p - W ** 2 / 4.0, 0.0))
        return r / dv


def transform_level(level, gap, dv, W, g: Geometry | None):
    """A looming LEVEL fitted on rendered looming, in perceived looming, at representative kinematics.

    Uses the exact perceived/rendered ratio at (gap, dv, W); in the small-angle limit it is k.
    """
    ratio = looming(gap, dv, W, g) / looming(gap, dv, W, None)
    return np.asarray(level, float) * ratio
