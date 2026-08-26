"""Equivalence test for one metric, and a suite over several."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .binned import quantile_bin_edges, bin_proportions, theta_Theta, n_bins_rule, uniform_weights

# Wu et al. (2026) §3.4's published thresholds, for a baseline bin of weight 1 anchored at a
# 2% MAIS2+ injury risk. Kept for comparison; they are NOT this project's defaults, because
# that anchor is calibrated to a far more severe crash population than the QUADRIS seeds.
WU_THETA_THD = 0.10
WU_THETA_CAP_THD = 0.05

# This project's adopted thresholds, derived rather than inherited: they are what a 10%
# tolerance on the injury-weighted mean implies for the QUADRIS reference at N = 5.
# Derivation and the argument for 10% rather than 5% or 8%: docs/equivalence_rope_note.md
# sections 3.1, 5 and 5.2.
THETA_THD = 0.188
THETA_CAP_THD = 0.089


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
    # Aggregate diagnostics. theta and Theta constrain only the BETWEEN-bin allocation, so
    # they cannot bound the error in a weighted aggregate: a model can match every bin
    # proportion and still differ within bins, and the outermost bins are open-ended. These
    # fields let the aggregate be reported directly alongside the equivalence verdict.
    mean_ref: float = float("nan")          # weighted mean of the metric, reference
    mean_syn: float = float("nan")          # weighted mean of the metric, synthetic
    mean_syn_binned: float = float("nan")   # bin-constant approximation (what Theta bounds)
    bin_means_ref: np.ndarray | None = None

    @property
    def mean_rel_error(self) -> float:
        """Relative error of the synthetic weighted mean against the reference."""
        if not np.isfinite(self.mean_ref) or self.mean_ref == 0:
            return float("nan")
        return self.mean_syn / self.mean_ref - 1.0

    @property
    def mean_rel_error_binned(self) -> float:
        if not np.isfinite(self.mean_ref) or self.mean_ref == 0:
            return float("nan")
        return self.mean_syn_binned / self.mean_ref - 1.0

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
                     resample: str = "population",
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

    `resample` selects what carries uncertainty, and the choice changes the intervals by
    an order of magnitude. It should be made from what the reference represents, not from
    convenience:

    * "population" (default from 2026-08-26): the reference IS the target set, so bin edges
      and reference proportions are fixed and only the synthetic side is resampled. Correct
      when the claim is about these scenarios.
    * "cases": the reference is a sample from some generating process, so sampling units are
      resampled uniformly and carry their weights. Required when the claim generalizes
      beyond the reference set. On the QUADRIS reference this widens the 95% HDI upper bound
      for theta from about 0.016 to about 0.177 at N = 5 under a perfect model, because the
      crash weights are concentrated enough that 5 000 scenarios carry an effective sample
      size of roughly 950.
    * "values": legacy and defective -- it drew values with probability proportional to
      weight and then treated the resample as unweighted, giving the precision of n
      independent draws and understating the spread by about sqrt(n / ESS). Retained only to
      reproduce results published before 2026-08-26.

    Point estimates of theta and Theta are identical under all three; only the intervals
    differ. Comparisons between conditions should in any case be made as a paired difference
    with a shared reference draw, not by overlapping marginal intervals.
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

    # aggregate diagnostics (see EquivalenceResult): the weighted means, plus the
    # bin-constant approximation of the synthetic mean, which is the only thing Theta bounds
    idx_r = np.clip(np.searchsorted(edges0, ref, side="right") - 1, 0, N - 1)
    bin_means = np.array([
        float((ref[idx_r == i] * w_ref[idx_r == i]).sum() / w_ref[idx_r == i].sum())
        if (idx_r == i).any() else np.nan for i in range(N)])
    mean_ref = float((ref * w_ref).sum() / w_ref.sum())
    mean_syn = float((syn * w_syn).sum() / w_syn.sum())
    finite = np.isfinite(bin_means)
    mean_syn_binned = float((ps0[finite] * bin_means[finite]).sum()) if finite.any() else float("nan")

    ths, Ths = [], []
    if posterior_draws is not None:
        for r, s in zip(*posterior_draws):
            th, Th, *_ = stats(np.asarray(r, float), None, np.asarray(s, float), None)
            ths.append(th); Ths.append(Th)
        unc = "posterior draws"
    elif resample == "population":
        # The reference IS the target population, not a sample from one: the comparison asks
        # what a driver does in THESE scenarios. Bin edges and reference proportions are then
        # fixed, and only the synthetic side carries sampling error. This is the project's
        # convention from 2026-08-26; see docs/equivalence_rope_note.md section 2.5 for the
        # argument and for when the "cases" treatment is required instead.
        for _ in range(n_boot):
            si = rng.integers(0, len(syn), len(syn))
            th, Th, *_ = stats(ref, w_ref, syn[si], w_syn[si])
            ths.append(th); Ths.append(Th)
        unc = "synthetic-side bootstrap, reference treated as population (n={})".format(n_boot)
    elif resample == "cases":
        # Correct nonparametric bootstrap for a WEIGHTED statistic: resample the sampling
        # units (scenarios) uniformly and carry their weights. The spread then reflects the
        # weights' effective sample size, sum(w)^2/sum(w^2), which for the QUADRIS reference
        # is about 950 of 5 000 because the crash weights are concentrated.
        for _ in range(n_boot):
            ri = rng.integers(0, len(ref), len(ref))
            si = rng.integers(0, len(syn), len(syn))
            th, Th, *_ = stats(ref[ri], w_ref[ri], syn[si], w_syn[si])
            ths.append(th); Ths.append(Th)
        unc = "case bootstrap (n={})".format(n_boot)
    elif resample == "values":
        # Draws values with probability proportional to weight and then treats the resample
        # as unweighted. This gives the precision of n INDEPENDENT draws and so understates
        # the spread by roughly sqrt(n / ESS) -- a factor of about 2.4 on the QUADRIS
        # reference. Retained only to reproduce results published before 2026-08-26.
        pr_w = w_ref / w_ref.sum(); ps_w = w_syn / w_syn.sum()
        for _ in range(n_boot):
            ri = rng.choice(len(ref), len(ref), replace=True, p=pr_w)
            si = rng.choice(len(syn), len(syn), replace=True, p=ps_w)
            th, Th, *_ = stats(ref[ri], None, syn[si], None)
            ths.append(th); Ths.append(Th)
        unc = "weighted-value bootstrap, understates spread (n={})".format(n_boot)
    else:
        raise ValueError("resample must be 'cases' or 'values', got {!r}".format(resample))

    return EquivalenceResult(
        metric=metric, n_bins=N, edges=edges0, omega=om0, theta_point=th0, Theta_point=Th0,
        theta_hdi=_hdi(np.array(ths), mass), Theta_hdi=_hdi(np.array(Ths), mass),
        rope_theta=rope_theta, rope_Theta=rope_Theta, per_bin_rel=rel0, per_bin_abs=ab0,
        p_ref=pr0, p_syn=ps0, n_ref=len(ref), n_syn=len(syn), uncertainty=unc,
        mean_ref=mean_ref, mean_syn=mean_syn, mean_syn_binned=mean_syn_binned,
        bin_means_ref=bin_means)


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
