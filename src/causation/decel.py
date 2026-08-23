"""
Component 3 — low deceleration: the driver's maximum braking as a distribution.

Bärgman et al. (2024) Fig. 3: maximum deceleration from 45 SHRP2 rear-end crashes with a
braking plateau, used in 1.5 m/s^2 bins. The data are not in this repository;
`standin_shrp2_max_decel()` is a labelled stand-in. In the closed-loop model (tier 2) the
same object clamps the planner's action space to [-d_max, a_max].
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class DecelerationDistribution:
    decel: np.ndarray          # bin centers [m/s^2], positive magnitudes
    probability: np.ndarray
    source: str

    @classmethod
    def from_csv(cls, path: str | Path) -> "DecelerationDistribution":
        df = pd.read_csv(path).sort_values("decel_ms2")
        p = df.probability.to_numpy(float)
        return cls(df.decel_ms2.to_numpy(float), p / p.sum(), "csv:{}".format(Path(path).name))

    def describe(self) -> dict:
        return dict(source=self.source, bins=self.decel.tolist(), probability=np.round(self.probability, 4).tolist(),
                    mean_ms2=float((self.decel * self.probability).sum()))


def standin_shrp2_max_decel() -> DecelerationDistribution:
    """STAND-IN, not data: six 1.5 m/s^2 bins from 1.5 to 9 m/s^2 with a hump at 4.5–6 m/s^2,
    roughly the shape reported for SHRP2 rear-end crashes (Bärgman et al. 2024 Fig. 3).
    Replace with the real bins. Every result produced with this object must say so."""
    centers = np.array([2.25, 3.75, 5.25, 6.75, 8.25])
    p = np.array([0.09, 0.22, 0.33, 0.26, 0.10])
    return DecelerationDistribution(centers, p / p.sum(), "STAND-IN 5-bin hump, mean {:.2f} m/s^2".format((centers * p).sum() / p.sum()))


def fixed_decel(a: float) -> DecelerationDistribution:
    return DecelerationDistribution(np.array([a]), np.array([1.0]), "fixed {} m/s^2".format(a))
