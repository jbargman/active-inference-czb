"""
Extracting boundaries from a comfort-zone field.

A comfort-zone boundary is a level set of the residual-information field eps(x). These
helpers pull that contour out numerically, so the same code works for any pair of state
variables and any preference function -- unlike the closed form in `field.critical_gap`,
which is specific to car-following geometry.
"""
from __future__ import annotations

import numpy as np

from .field import ComfortField


def boundary_level_set(field: ComfortField, level: float,
                       which: str = "deficit") -> list:
    """
    Extract the contour {x : field == level} as a list of (x, y) polylines.

    Uses matplotlib's contour engine when available (robust marching squares); falls back to
    a per-column bracketing search otherwise, which is adequate for the monotone fields that
    arise here.

    Parameters
    ----------
    field : ComfortField
    level : the threshold c defining the boundary
    which : "deficit" (residual information) or "margin" (braking margin, level 0 = the
            model's own p_safe boundary)
    """
    Z = getattr(field, which)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cs = ax.contour(field.x, field.y, Z, levels=[level])
        paths = []
        for seg in cs.allsegs[0]:
            if len(seg) > 1:
                paths.append(np.asarray(seg))
        plt.close(fig)
        return paths
    except Exception:
        return [boundary_curve(field, level, which=which)]


def boundary_curve(field: ComfortField, level: float,
                   which: str = "deficit") -> np.ndarray:
    """
    Single-valued boundary: for each x, the first y at which the field crosses `level`.

    Returns an (N, 2) array of (x, y); y is NaN where no crossing exists in the grid. This is
    the practical form when the boundary is a function (e.g. critical gap vs speed).
    """
    Z = getattr(field, which)
    out = np.full((len(field.x), 2), np.nan)
    out[:, 0] = field.x
    for i in range(len(field.x)):
        col = Z[:, i]
        s = np.sign(col - level)
        idx = np.where(np.diff(s) != 0)[0]
        if len(idx) == 0:
            continue
        k = idx[0]
        y0, y1 = field.y[k], field.y[k + 1]
        f0, f1 = col[k] - level, col[k + 1] - level
        out[i, 1] = y0 if f1 == f0 else y0 + (y1 - y0) * (-f0) / (f1 - f0)
    return out


def dread_zone_boundary(field: ComfortField) -> np.ndarray:
    """
    The dread-zone boundary: where the braking margin reaches zero, i.e. where the required
    deceleration equals the maximum available and no policy restores the preferred outcome.

    In the traffic-psychology sense the dread zone is the limit drivers will not cross *even
    with extra motives* -- which maps naturally onto "physically no longer recoverable"
    rather than merely "uncomfortable".
    """
    return boundary_curve(field, level=0.0, which="margin")
