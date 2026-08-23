"""Equivalence test for one metric, and a suite over several."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .binned import quantile_bin_edges, bin_proportions, theta_Theta, n_bins_rule, uniform_weights

THETA_THD = 0.10      # ROPE thresholds of Wu 2026 §3.4 for a baseline bin of weight 1
THETA_CAP_THD = 0.05


@dataclass
class EquivalenceResult:
    metric: str
    n_bins: int
    edges: np.ndarray
    omega: np.ndarray
    theta_point: float
    Theta_point: float
    theta_hdi: tuple[float, float]
    Theta_hdi: tuple[float, float]
    rope_theta: float
    rope_Theta: float
    per_bin_rel: np.ndarray
    per_bin_abs: np.ndarray
    p_ref: np.ndarray
    p_syn: np.ndarray
    n_ref: int
    n_syn: int
    uncertainty: str = "weighted bootstrap"

    @property
    def theta_equivalent(self) -> bool:
        return self.theta_hdi[1] <= self.rope_theta

    @property
    def Theta_equivalent(self) -> bool:
        return self.Theta_hdi[1] <= self.rope_Theta

    @property
    def equivalent(self) -> bool:
        return self.theta_equivalent and self.Theta_equivalent


def _hdi(samples: np.ndarray, mass: float = 0.95) -> tuple[float, float]:
    s = np.sort(np.asarray(samples, float))
    n = len(s)
    k = max(1, int(np.floor(mass * n)))
    widths = s[k - 1:] - s[:n - k + 1] if k <= n else s[-1:] - s[:1]
    i = int(np.argmin(widths))
    return float(s[i]), float(s[min(i + k - 1, n - 1)])


def equivalence_test(ref: np.ndarray, syn: np.ndarray, *, metric: str = "",
                     w_ref: np.ndarray | None = None, w_syn: np.ndarray | None = None,
                     n_bins: int | None = None, omega: np.ndarray | Callable | None = None,
                     rope_theta: float = THETA_THD, rope_Theta: float = THETA_CAP_THD,
                     n_boot: int = 2000, mass: float = 0.95,
                     rng: np.random.Generator | int = 0,
                     posterior_draws: tuple[list[np.ndarray], list[np.ndarray]] | None = None
                     ) -> EquivalenceResult:
    """
    One metric. Bins are quantiles of the (weighted) reference; the same edges are applied
    to the synthetic sample; theta/Theta are computed on the point estimate and on
    resampled pairs to obtain 95% HDIs; equivalence holds when both HDIs lie inside their
    ROPEs (upper bound <= threshold, since both statistics are non-negative).

    `omega` may be an array of bin weights or a callable(edges, ref, w_ref) -> array; the
    default is uniform. `posterior_draws`, if given as (list of ref samples, list of syn
    samples), replaces the bootstrap with the paper's posterior-draw scheme.
    """
    ref = np.asarray(ref, float); syn = np.asarray(syn, float)
    ref = ref[np.isfinite(ref)]; syn = syn[np.isfinite(syn)]
    w_ref = np.ones_like(ref) if w_ref is None else np.asarray(w_ref, float)[: len(ref)]
    w_syn = np.ones_like(syn) if w_syn is None else np.asarray(w_syn, float)[: len(syn)]
    rng = np.random.default_rng(rng)
    N = n_bins or n_bins_rule(len(ref))

    def stats(r, wr, s, ws):
        edges = quantile_bin_edges(r, N, wr)
        om = omega(edges, r, wr) if callable(omega) else (uniform_weights(N) if omega is None else np.asarray(omega, float))
        pr, ps = bin_proportions(r, edges, wr), bin_proportions(s, edges, ws)
        th, Th, rel, ab = theta_Theta(pr, ps, om)
        return th, Th, rel, ab, edges, om, pr, ps

    th0, Th0, rel0, ab0, edges0, om0, pr0, ps0 = stats(ref, w_ref, syn, w_syn)

    ths, Ths = [], []
    if posterior_draws is not None:
        for r, s in zip(*posterior_draws):
            th, Th, *_ = stats(np.asarray(r, float), None, np.asarray(s, float), None)
            ths.append(th); Ths.append(Th)
        unc = "posterior draws"
    else:
        pr_w = w_ref / w_ref.sum(); ps_w = w_syn / w_syn.sum()
        for _ in range(n_boot):
            ri = rng.choice(len(ref), len(ref), replace=True, p=pr_w)
            si = rng.choice(len(syn), len(syn), replace=True, p=ps_w)
            th, Th, *_ = stats(ref[ri], None, syn[si], None)
            ths.append(th); Ths.append(Th)
        unc = "weighted bootstrap (n={})".format(n_boot)

    return EquivalenceResult(
        metric=metric, n_bins=N, edges=edges0, omega=om0, theta_point=th0, Theta_point=Th0,
        theta_hdi=_hdi(np.array(ths), mass), Theta_hdi=_hdi(np.array(Ths), mass),
        rope_theta=rope_theta, rope_Theta=rope_Theta, per_bin_rel=rel0, per_bin_abs=ab0,
        p_ref=pr0, p_syn=ps0, n_ref=len(ref), n_syn=len(syn), uncertainty=unc)


@dataclass
class MetricSpec:
    name: str
    ref: np.ndarray
    syn: np.ndarray
    w_ref: np.ndarray | None = None
    w_syn: np.ndarray | None = None
    critical: bool = True          # for the overall decision (Wu 2026 §2.1.4)
    kwargs: dict = field(default_factory=dict)


def run_metric_suite(specs: list[MetricSpec], **common) -> dict[str, EquivalenceResult]:
    """Run the test for every metric; the overall decision is left to the caller, who must
    state the rule in advance (all critical metrics equivalent is the strict version)."""
    return {s.name: equivalence_test(s.ref, s.syn, metric=s.name, w_ref=s.w_ref, w_syn=s.w_syn,
                                     **{**common, **s.kwargs}) for s in specs}
