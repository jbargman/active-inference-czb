"""Load QUADRIS scenarios into seeds: lead-vehicle speed profile + follower initial state."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
QUADRIS_DIR = REPO / "external" / "quadris"
DT = 0.05                    # QUADRIS sampling interval [s]
VEHICLE_LENGTH = 4.2         # lf + lr in the active inference model [m]; d in QUADRIS is bumper-to-bumper


@dataclass
class Seed:
    """One re-simulation seed. The follower's original response is *not* part of the seed:
    only its initial state is kept, as in the SCM-based dataset of Wu et al. (2026) §3.1.3."""
    seed_id: int
    weight: float
    t: np.ndarray                  # [s], from 0, step DT
    v_lead: np.ndarray             # [m/s] lead speed profile on t
    v_f0: float                    # follower initial speed [m/s]
    d0: float                      # initial bumper-to-bumper gap [m]
    v_f_orig: np.ndarray = field(repr=False, default=None)   # generator's follower speed (reference only)
    d_orig: np.ndarray = field(repr=False, default=None)     # generator's gap (reference only)
    lead_delta_v_orig: float = np.nan                        # generator's outcome (reference only)
    source: str = "synthetic"

    @property
    def t_crash_orig(self) -> float:
        return float(self.t[-1])

    def lead_speed(self, t_query: np.ndarray) -> np.ndarray:
        """Lead speed at arbitrary times; held constant beyond the recorded profile
        (a stopped lead stays stopped, a moving lead keeps its last speed). ASSUMPTION."""
        return np.interp(t_query, self.t, self.v_lead, left=self.v_lead[0], right=self.v_lead[-1])

    def lead_position(self, t_query: np.ndarray) -> np.ndarray:
        """Lead rear-bumper position with the follower's front bumper at x = 0 at t = 0."""
        tt = np.arange(0.0, float(np.max(t_query)) + DT, DT)
        v = self.lead_speed(tt)
        x = self.d0 + np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(tt))])
        return np.interp(t_query, tt, x)


def load_synthetic(path: Path | None = None, ids: list[int] | None = None) -> list[Seed]:
    """Read Synthetic_crash_scenarios.csv into seeds."""
    path = path or QUADRIS_DIR / "Synthetic_crash_scenarios.csv"
    df = pd.read_csv(path)
    if ids is not None:
        df = df[df.id.isin(ids)]
    seeds = []
    for sid, g in df.groupby("id", sort=True):
        g = g.sort_values("t")
        seeds.append(Seed(
            seed_id=int(sid), weight=float(g.weight.iloc[0]),
            t=g.t.to_numpy(float), v_lead=g.v_l.to_numpy(float),
            v_f0=float(g.v_f.iloc[0]), d0=float(g.d.iloc[0]),
            v_f_orig=g.v_f.to_numpy(float), d_orig=g.d.to_numpy(float),
            lead_delta_v_orig=float(g.lead_delta_v.iloc[0]),
        ))
    return seeds


def load_incidents(path: Path | None = None) -> pd.DataFrame:
    """The 214 real incidents (lead-profile parameters only; cannot be simulated without a
    follower initial state). Returned as a DataFrame for exposure analyses."""
    path = path or QUADRIS_DIR / "Combined_incidents.csv"
    return pd.read_csv(path)


def lead_profile_from_params(v_c: float, a_1: float, a_2: float, tau_s: float, tau_1: float,
                             tau_2: float, dt: float = DT) -> tuple[np.ndarray, np.ndarray]:
    """Lead speed profile from the six Wu et al. (2024) parameters, defined backward from
    time zero: segment S (constant v_c for tau_s), then segment 1 (a_1 for tau_1), then
    segment 2 (a_2 for tau_2). Returned forward in time, ending at time zero. Speeds are
    floored at 0."""
    dur = tau_2 + tau_1 + tau_s
    t = np.arange(0.0, dur + dt / 2, dt)
    tb = dur - t                         # time before time zero
    v = np.where(tb <= tau_s, v_c,
        np.where(tb <= tau_s + tau_1, v_c - a_1 * (tb - tau_s),
                 v_c - a_1 * tau_1 - a_2 * (tb - tau_s - tau_1)))
    return t, np.maximum(v, 0.0)
