"""
Distribution objects that the surprise measures operate on.

The surprise literature is written for whatever distribution is convenient in the paper at
hand -- categorical in the information-theory work, Gaussian mixtures in the trajectory-
prediction work, particle sets in the active-inference work. The metrics themselves only
ever need a handful of operations, so we define a small protocol and implement it for the
four cases we actually need.

Required operations
-------------------
    pdf(x)      density (or pmf) at x
    logpdf(x)   log density
    sample(n)   draw samples (used for Monte-Carlo integrals)
    mean()      expectation, for observation-mismatch measures
    mode()      argmax of the density, for residual information
    entropy()   Shannon (differential) entropy

`mode()` is exact for Gaussian/Categorical and approximate (grid or best-sample search) for
mixtures and particle sets -- the approximation is documented per class because residual
information depends on it directly.
"""
from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable

import numpy as np


def _as_2d(x) -> np.ndarray:
    """Coerce to shape (n_points, n_dim)."""
    a = np.asarray(x, dtype=float)
    if a.ndim == 0:
        return a.reshape(1, 1)
    if a.ndim == 1:
        return a.reshape(-1, 1) if a.size > 1 else a.reshape(1, 1)
    return a


@runtime_checkable
class Distribution(Protocol):
    """Minimal interface required by the surprise measures."""

    ndim: int

    def pdf(self, x) -> np.ndarray: ...
    def logpdf(self, x) -> np.ndarray: ...
    def sample(self, n: int, rng=None) -> np.ndarray: ...
    def mean(self) -> np.ndarray: ...
    def mode(self) -> np.ndarray: ...
    def entropy(self) -> float: ...


# --------------------------------------------------------------------------------------
# Gaussian
# --------------------------------------------------------------------------------------
class Gaussian:
    """Multivariate normal. `mode` and `entropy` are exact."""

    def __init__(self, mean, cov):
        self.mu = np.atleast_1d(np.asarray(mean, dtype=float))
        self.ndim = self.mu.size
        cov = np.asarray(cov, dtype=float)
        if cov.ndim == 0:
            cov = np.eye(self.ndim) * float(cov)
        elif cov.ndim == 1:
            cov = np.diag(cov)
        self.cov = cov
        self._chol = np.linalg.cholesky(cov)
        self._logdet = 2.0 * np.sum(np.log(np.diag(self._chol)))
        self._inv = np.linalg.inv(cov)

    def logpdf(self, x) -> np.ndarray:
        x = _as_2d(x)
        d = x - self.mu
        maha = np.einsum("ij,jk,ik->i", d, self._inv, d)
        return -0.5 * (maha + self._logdet + self.ndim * np.log(2 * np.pi))

    def pdf(self, x) -> np.ndarray:
        return np.exp(self.logpdf(x))

    def sample(self, n: int, rng=None) -> np.ndarray:
        rng = np.random.default_rng() if rng is None else rng
        return self.mu + rng.standard_normal((n, self.ndim)) @ self._chol.T

    def mean(self) -> np.ndarray:
        return self.mu.copy()

    def mode(self) -> np.ndarray:
        return self.mu.copy()

    def entropy(self) -> float:
        return 0.5 * (self.ndim * (1.0 + np.log(2 * np.pi)) + self._logdet)


# --------------------------------------------------------------------------------------
# Gaussian mixture
# --------------------------------------------------------------------------------------
class GaussianMixture:
    """
    Gaussian mixture model -- the natural representation of a trajectory predictor's belief
    about a road user's position at one future timestep (Dinparastdjadid et al. 2023).

    `mode()` is found by evaluating the density at each component mean and, optionally,
    refining on a local grid; for well-separated components this is exact, for heavily
    overlapping ones it is a good approximation. Since residual information only needs
    `max_x p(x)`, small errors here bias all values by the same additive constant within a
    timestep, which matters less than it might appear -- but use `mode_refine=True` if you
    need it tight.
    """

    def __init__(self, weights, means, covs, mode_refine: bool | None = None):
        w = np.asarray(weights, dtype=float)
        self.w = w / w.sum()
        self.mus = np.atleast_2d(np.asarray(means, dtype=float))
        self.ndim = self.mus.shape[1]
        covs = np.asarray(covs, dtype=float)
        if covs.ndim == 1:                      # one variance per component, 1-D
            covs = covs.reshape(-1, 1, 1)
        elif covs.ndim == 2 and covs.shape[1] == self.ndim and self.ndim > 1:
            covs = np.stack([np.diag(c) for c in covs])
        self.covs = covs
        self.components = [Gaussian(m, c) for m, c in zip(self.mus, self.covs)]
        # Refine by default in 1-2 D, where the grid search is cheap. Without it, taking the
        # best *component mean* as the mode slightly under-estimates max p(x) for overlapping
        # components, which makes residual information dip a little below zero -- breaking
        # the zero-floor property it exists to provide.
        self._mode_refine = (self.ndim <= 2) if mode_refine is None else mode_refine

    @classmethod
    def from_components(cls, weights, components: Sequence[Gaussian]):
        return cls(weights,
                   np.stack([c.mu for c in components]),
                   np.stack([c.cov for c in components]))

    def logpdf(self, x) -> np.ndarray:
        x = _as_2d(x)
        lp = np.stack([c.logpdf(x) for c in self.components])      # (k, n)
        return _logsumexp(lp + np.log(self.w)[:, None], axis=0)

    def pdf(self, x) -> np.ndarray:
        return np.exp(self.logpdf(x))

    def sample(self, n: int, rng=None) -> np.ndarray:
        rng = np.random.default_rng() if rng is None else rng
        idx = rng.choice(len(self.w), size=n, p=self.w)
        out = np.empty((n, self.ndim))
        for k in range(len(self.w)):
            m = idx == k
            if m.any():
                out[m] = self.components[k].sample(int(m.sum()), rng)
        return out

    def mean(self) -> np.ndarray:
        return (self.w[:, None] * self.mus).sum(axis=0)

    def mode(self) -> np.ndarray:
        cand = self.mus
        vals = self.pdf(cand)
        best = cand[int(np.argmax(vals))]
        if not self._mode_refine:
            return best
        # local refinement: coordinate grid around the best component mean
        scale = np.sqrt(np.max([np.diag(c) for c in self.covs], axis=0))
        for _ in range(3):
            grid = [np.linspace(best[d] - scale[d], best[d] + scale[d], 9)
                    for d in range(self.ndim)]
            pts = np.stack(np.meshgrid(*grid, indexing="ij"), axis=-1).reshape(-1, self.ndim)
            best = pts[int(np.argmax(self.pdf(pts)))]
            scale = scale / 4.0
        return best

    def entropy(self, n: int = 20000, rng=None) -> float:
        """Monte-Carlo estimate; a GMM has no closed-form entropy."""
        s = self.sample(n, rng)
        return float(-np.mean(self.logpdf(s)))


# --------------------------------------------------------------------------------------
# Particle set
# --------------------------------------------------------------------------------------
class ParticleSet:
    """
    Weighted particle representation of a belief -- what an active-inference agent with a
    particle filter actually holds (Engstrom et al. 2024; Schumann et al. 2026).

    Density is evaluated by kernel density estimation, so that `pdf`/`logpdf`/`entropy` are
    defined. Bandwidth defaults to Silverman's rule on the weighted sample. This is exactly
    the KDE step the papers use to turn a particle set into a usable density.
    """

    def __init__(self, particles, weights=None, bandwidth=None):
        self.x = _as_2d(particles)
        self.n, self.ndim = self.x.shape
        if weights is None:
            self.w = np.full(self.n, 1.0 / self.n)
        else:
            w = np.asarray(weights, dtype=float)
            self.w = w / w.sum()
        self.bandwidth = bandwidth if bandwidth is not None else self._silverman()
        self._h2 = self.bandwidth ** 2

    def _silverman(self) -> float:
        neff = 1.0 / np.sum(self.w ** 2)
        std = np.sqrt(np.average((self.x - self.mean()) ** 2, axis=0, weights=self.w)).mean()
        std = max(std, 1e-9)
        return float(std * (4.0 / (self.ndim + 2) / neff) ** (1.0 / (self.ndim + 4)))

    def logpdf(self, x) -> np.ndarray:
        x = _as_2d(x)
        d2 = ((x[:, None, :] - self.x[None, :, :]) ** 2).sum(axis=-1)      # (n_x, n_p)
        norm = -0.5 * self.ndim * np.log(2 * np.pi * self._h2)
        return _logsumexp(norm - 0.5 * d2 / self._h2 + np.log(self.w)[None, :], axis=1)

    def pdf(self, x) -> np.ndarray:
        return np.exp(self.logpdf(x))

    def sample(self, n: int, rng=None) -> np.ndarray:
        rng = np.random.default_rng() if rng is None else rng
        idx = rng.choice(self.n, size=n, p=self.w)
        return self.x[idx] + rng.standard_normal((n, self.ndim)) * self.bandwidth

    def mean(self) -> np.ndarray:
        return (self.w[:, None] * self.x).sum(axis=0)

    def mode(self) -> np.ndarray:
        """Highest-density particle (KDE evaluated at the particles themselves)."""
        return self.x[int(np.argmax(self.logpdf(self.x)))]

    def entropy(self, n: int = 20000, rng=None) -> float:
        s = self.sample(n, rng)
        return float(-np.mean(self.logpdf(s)))


# --------------------------------------------------------------------------------------
# Categorical
# --------------------------------------------------------------------------------------
class Categorical:
    """
    Discrete distribution over labelled outcomes -- e.g. a predictor emitting
    {pass, yield, decelerate}. This is the setting the classical information-theoretic
    measures were written for.
    """

    ndim = 1

    def __init__(self, probs, labels=None):
        p = np.asarray(probs, dtype=float)
        self.p = p / p.sum()
        self.labels = list(labels) if labels is not None else list(range(len(self.p)))
        self._index = {l: i for i, l in enumerate(self.labels)}

    def _idx(self, x):
        if isinstance(x, (list, tuple, np.ndarray)):
            return np.array([self._index[v] if v in self._index else int(v) for v in x])
        return np.array([self._index[x] if x in self._index else int(x)])

    def pdf(self, x) -> np.ndarray:
        return self.p[self._idx(x)]

    def logpdf(self, x) -> np.ndarray:
        with np.errstate(divide="ignore"):
            return np.log(self.pdf(x))

    def sample(self, n: int, rng=None) -> np.ndarray:
        rng = np.random.default_rng() if rng is None else rng
        return rng.choice(len(self.p), size=n, p=self.p)

    def mean(self) -> np.ndarray:
        return np.array([float(np.sum(self.p * np.arange(len(self.p))))])

    def mode(self):
        return self.labels[int(np.argmax(self.p))]

    def entropy(self) -> float:
        p = self.p[self.p > 0]
        return float(-np.sum(p * np.log(p)))

    def support(self):
        return self.labels


def _logsumexp(a, axis=None):
    m = np.max(a, axis=axis, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)
    out = m + np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True))
    return np.squeeze(out, axis=axis) if axis is not None else float(out)
