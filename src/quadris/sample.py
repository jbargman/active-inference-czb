"""Stratified, weight-proportional seed sampling."""
from __future__ import annotations

import numpy as np

from .load import Seed

SPEED_BANDS = ((0.0, 10.0), (10.0, 15.0), (15.0, np.inf))   # follower initial speed [m/s]


def sample_seeds(seeds: list[Seed], n: int, rng: np.random.Generator | int = 0,
                 bands=SPEED_BANDS, replace: bool = False) -> list[Seed]:
    """
    Draw n seeds with probability proportional to the QUADRIS weight, stratified by the
    follower's initial speed band so that the sub-10 m/s third of the data (outside the
    active inference model's tuned range) is represented in proportion to its weight.
    The allocation per band is proportional to the band's total weight.
    """
    rng = np.random.default_rng(rng)
    w = np.array([s.weight for s in seeds], float)
    v0 = np.array([s.v_f0 for s in seeds], float)
    out: list[Seed] = []
    alloc = []
    for lo, hi in bands:
        m = (v0 >= lo) & (v0 < hi)
        alloc.append(w[m].sum())
    alloc = np.array(alloc) / sum(alloc)
    counts = np.floor(alloc * n).astype(int)
    counts[np.argmax(alloc)] += n - counts.sum()
    for (lo, hi), k in zip(bands, counts):
        idx = np.where((v0 >= lo) & (v0 < hi))[0]
        if k == 0 or len(idx) == 0:
            continue
        p = w[idx] / w[idx].sum()
        pick = rng.choice(idx, size=min(k, len(idx)) if not replace else k, replace=replace, p=p)
        out.extend(seeds[i] for i in pick)
    return out
