"""
Component 1 — off-road glances.

A `GlanceDistribution` is an empirical distribution of off-road glance durations in 0.1 s
bins plus a point mass at zero (eyes on road), as in Bärgman et al. (2024) Fig. 1. The real
SHRP2 baseline distribution (1 791 epochs, 4 604 glances, longest 6.7 s, ~80% on-road) is not
shareable by its authors; `standin_shrp2_glances()` builds a clearly labelled parametric
stand-in with those published summary properties so that the pipeline runs. Replace it with
the real bins via `GlanceDistribution.from_csv` as soon as they are available.

Anchoring (how a glance is placed relative to the event):
  "tau_inv"    the CBM's rule: the glance overlaps the instant tau^-1 = 0.2 s^-1, with the
               overshoot beyond that instant drawn from the overshot transform (App. C of the
               paper). Cheap: one simulation per (duration, overshoot) pair, weighted by its
               probability.
  "lead_onset" anchored at the lead's braking onset (a BLOM-like alternative, for comparison)
  "crash"      anchored at the seed's original impact (conditions on the outcome; included so
               the bias it introduces can be shown, not recommended)
  "process"    no anchor: an on/off renewal process over the whole scenario, off-road
               durations from the distribution and on-road dwells exponential with a given
               mean; the glance start is independent of the event by construction. Monte
               Carlo; the reference implementation for the active inference driver, which
               does not need the 0.2 s^-1 assumption.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

BIN = 0.1


@dataclass
class GlanceDistribution:
    durations: np.ndarray      # bin centers [s], > 0, step BIN
    probability: np.ndarray    # probability of each off-road duration, summing to (1 - on_road)
    on_road: float             # point mass at zero
    source: str

    @classmethod
    def from_csv(cls, path: str | Path, on_road: float | None = None) -> "GlanceDistribution":
        """CSV with columns duration_s, probability; a row with duration_s == 0 is the on-road
        point mass (or pass `on_road`). Probabilities are renormalized."""
        df = pd.read_csv(path)
        zero = df[df.duration_s <= 0]
        off = df[df.duration_s > 0].sort_values("duration_s")
        pm = float(zero.probability.sum()) if on_road is None else on_road
        p = off.probability.to_numpy(float)
        p = p / p.sum() * (1.0 - pm)
        return cls(off.duration_s.to_numpy(float), p, pm, "csv:{}".format(Path(path).name))

    def with_on_road(self, on_road: float) -> "GlanceDistribution":
        p = self.probability / self.probability.sum() * (1.0 - on_road)
        return GlanceDistribution(self.durations, p, on_road, self.source)

    def cut(self, max_duration: float) -> "GlanceDistribution":
        """Ideal DMS of Bärgman et al. §2.1.3: remove all glances longer than max_duration,
        keep the on-road share, renormalize the remainder."""
        m = self.durations <= max_duration + 1e-9
        return GlanceDistribution(self.durations[m], self.probability[m] / self.probability[m].sum()
                                  * (1.0 - self.on_road), self.on_road, self.source + "|cut{}s".format(max_duration))

    def describe(self) -> dict:
        return dict(source=self.source, on_road=self.on_road, n_bins=len(self.durations),
                    longest_s=float(self.durations.max()),
                    mean_offroad_s=float((self.durations * self.probability).sum() / self.probability.sum()))


def standin_shrp2_glances(on_road: float = 0.80, median: float = 0.55, sigma: float = 0.75,
                          longest: float = 6.7) -> GlanceDistribution:
    """
    STAND-IN, not data. A log-normal over off-road durations discretized into 0.1 s bins,
    truncated at the published longest SHRP2 baseline glance (6.7 s), with the published
    on-road share (~80%). Median and sigma are chosen to give a plausible everyday-driving
    distribution (mean ~0.7 s, ~2% of glances above 2 s); they are NOT the SHRP2 values and
    every result produced with this object must say so.
    """
    edges = np.arange(0.0, longest + BIN / 2, BIN)
    # durations are labelled by the bin's upper edge (0.1, 0.2, ... s), as in the paper's
    # 0.1 s binning; the overshot transform relies on durations being multiples of BIN
    from math import erf, log, sqrt
    def cdf(x):
        return 0.5 * (1 + erf((log(max(x, 1e-9)) - log(median)) / (sigma * sqrt(2))))
    p = np.array([cdf(edges[i + 1]) - cdf(edges[i]) for i in range(len(edges) - 1)])
    p = p / p.sum() * (1.0 - on_road)
    return GlanceDistribution(np.round(edges[1:], 2), p, on_road,
                              "STAND-IN lognormal(median={}, sigma={}) truncated {} s".format(median, sigma, longest))


def overshot_distribution(g: GlanceDistribution) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Joint distribution of (duration d, overshoot o) under the overshot construction of
    Bärgman et al. (2024) App. C: a glance of duration d, placed uniformly with respect to
    the anchor, overshoots it by o in {0.1, ..., d} with equal probability 0.1/d each.
    Returns arrays (d, o, P(d, o)); the marginal over d is the paper's overshot distribution.
    The on-road point mass is not included (handle it as the no-glance case).
    """
    ds, os_, ps = [], [], []
    for d, p in zip(g.durations, g.probability):
        k = max(1, int(round(d / BIN)))
        for j in range(1, k + 1):
            ds.append(d); os_.append(j * BIN); ps.append(p / k)
    return np.array(ds), np.array(os_), np.array(ps)


@dataclass
class GlanceSchedule:
    """Off-road intervals [(start, end), ...] in scenario time, plus the probability of this
    schedule within its sweep (1 for Monte Carlo draws)."""
    intervals: list[tuple[float, float]]
    probability: float = 1.0
    label: str = ""

    def off_road(self, t: np.ndarray) -> np.ndarray:
        off = np.zeros_like(t, dtype=bool)
        for s, e in self.intervals:
            off |= (t >= s) & (t < e)
        return off

    def evidence_weight(self, t: np.ndarray, w_off: float) -> np.ndarray:
        return np.where(self.off_road(t), w_off, 1.0)

    def precision_factor(self, t: np.ndarray, factor: float) -> np.ndarray:
        return np.where(self.off_road(t), factor, 1.0)


def anchored_schedules(g: GlanceDistribution, t_anchor: float) -> list[GlanceSchedule]:
    """All (d, o) glances overlapping the anchor, plus the no-glance case, with probabilities
    summing to 1. The glance runs from t_anchor - (d - o) to t_anchor + o."""
    out = [GlanceSchedule([], g.on_road, "no glance")]
    d, o, p = overshot_distribution(g)
    for di, oi, pi in zip(d, o, p):
        out.append(GlanceSchedule([(t_anchor - (di - oi), t_anchor + oi)], float(pi),
                                  "d={:.1f} o={:.1f}".format(di, oi)))
    return out


def marginal_overshot_schedules(g: GlanceDistribution, t_anchor: float) -> list[GlanceSchedule]:
    """Cheaper sweep: one schedule per overshoot value (the paper's overshot distribution),
    with the glance assumed to start long before the anchor. Valid when nothing before the
    anchor matters (true for the CBM; approximately true for the tier-1 field, which is zero
    inside the comfort zone)."""
    d, o, p = overshot_distribution(g)
    out = [GlanceSchedule([], g.on_road, "no glance")]
    for oi in np.unique(o):
        pi = float(p[o == oi].sum())
        out.append(GlanceSchedule([(t_anchor - 10.0, t_anchor + oi)], pi, "o={:.1f}".format(oi)))
    return out


def process_schedules(g: GlanceDistribution, t_end: float, n_draws: int, on_road_mean: float,
                      rng: np.random.Generator) -> list[GlanceSchedule]:
    """Renewal on/off process over [0, t_end]: on-road dwell ~ Exp(mean), off-road duration
    from the distribution. Each draw has probability 1/n_draws. The on-road share of time is
    set by the mean dwell relative to the mean glance, so `on_road_mean` should be chosen to
    reproduce the distribution's on-road point mass: mean_on = mean_off * on_road/(1-on_road)."""
    out = []
    mean_off = float((g.durations * g.probability).sum() / g.probability.sum())
    if on_road_mean is None:
        on_road_mean = mean_off * g.on_road / max(1.0 - g.on_road, 1e-9)
    pd_ = g.probability / g.probability.sum()
    for k in range(n_draws):
        t = -rng.exponential(on_road_mean)           # start mid-dwell, stationary-ish
        iv = []
        while t < t_end:
            t += rng.exponential(on_road_mean)
            d = float(rng.choice(g.durations, p=pd_))
            if t < t_end:
                iv.append((max(t, 0.0), t + d))
            t += d
        out.append(GlanceSchedule(iv, 1.0 / n_draws, "process draw {}".format(k)))
    return out
