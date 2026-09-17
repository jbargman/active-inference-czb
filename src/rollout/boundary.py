"""Delta G, the axis, and the Monte Carlo standard error.

Card JJ.1, brief section 3.5; `docs/rollout_boundary_design_note.md` section 1.5.

    Delta G(t0) = G(continue) - min over the menu G(pi)  >= 0,

and the axis is log Delta G. The zero rule: if any cell has Delta G = 0 exactly (no sampled
future collides under continue, or every alternative costs more control effort than it saves),
the axis is log(Delta G + Delta G_min / 2) with Delta G_min the smallest positive value across
cells, and the report counts those cells and gives the sensitivity to that choice.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .policies import CONTINUE


def delta_g(g_by_policy: dict[str, float], continue_name: str = CONTINUE) -> float:
    """G(continue) - min over the menu, floored at 0 (the continue policy is in the menu)."""
    if continue_name not in g_by_policy:
        raise KeyError(f"{continue_name!r} is not in the menu {sorted(g_by_policy)}")
    return float(max(g_by_policy[continue_name] - min(g_by_policy.values()), 0.0))


@dataclass
class Axis:
    """log Delta G across cells, with the zero rule applied only where a zero exists."""
    values: np.ndarray
    zero_rule_applied: bool
    n_zero: int
    dg_min: float          # the smallest positive Delta G across cells (nan if there is none)
    offset: float          # what was added before the log (0 when the rule does not apply)


def axis(dg_by_cell) -> Axis:
    """The axis of design note section 1.5."""
    dg = np.asarray(list(dg_by_cell.values()) if isinstance(dg_by_cell, dict) else dg_by_cell,
                    dtype=float)
    zeros = dg <= 0.0
    pos = dg[~zeros]
    if not zeros.any():
        return Axis(values=np.log(dg), zero_rule_applied=False, n_zero=0,
                    dg_min=float(pos.min()) if len(pos) else float("nan"), offset=0.0)
    if len(pos) == 0:
        raise ValueError("every cell has Delta G = 0: the axis is undefined")
    dg_min = float(pos.min())
    return Axis(values=np.log(dg + dg_min / 2.0), zero_rule_applied=True,
                n_zero=int(zeros.sum()), dg_min=dg_min, offset=dg_min / 2.0)


def mc_standard_error(dg_by_seed) -> float:
    """The standard error of Delta G across seeds for one cell (sd / sqrt(n_seeds))."""
    a = np.asarray(list(dg_by_seed), dtype=float)
    if len(a) < 2:
        return float("nan")
    return float(np.std(a, ddof=1) / np.sqrt(len(a)))


def mc_rule_e(se_by_cell, log_dg: np.ndarray, fraction: float = 0.05) -> tuple[float, float, bool]:
    """Rule (e): the median per-cell standard error of Delta G against `fraction` of the
    between-cell spread of log Delta G.

    The two quantities live on different scales, so the standard error is compared on the log
    axis: se(log Delta G) ~ se(Delta G) / Delta G is what a cell's position on the axis is
    uncertain by. The caller passes the per-cell standard errors ALREADY divided by that cell's
    Delta G; this function only compares medians with the spread. Returns
    (median se, threshold, verdict-holds).
    """
    med = float(np.median(np.asarray(list(se_by_cell), dtype=float)))
    spread = float(np.std(np.asarray(log_dg, dtype=float), ddof=1))
    return med, fraction * spread, med <= fraction * spread
