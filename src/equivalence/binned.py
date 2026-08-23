"""Binning-based statistics theta and Theta (Wu et al. 2026, Eqs. 1-4)."""
from __future__ import annotations

import numpy as np


def n_bins_rule(n_ref: int, m: int = 40, n_max: int = 20) -> int:
    """N = min(floor(n/m), N_max), m in [30, 50] recommended (Eq. 4)."""
    return int(max(1, min(n_ref // m, n_max)))


def _weighted_quantiles(x: np.ndarray, w: np.ndarray, q: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    xs, ws = x[order], w[order]
    cw = np.cumsum(ws) - 0.5 * ws
    cw /= ws.sum()
    return np.interp(q, cw, xs)


def quantile_bin_edges(ref: np.ndarray, n_bins: int, w_ref: np.ndarray | None = None) -> np.ndarray:
    """Bin edges such that each bin holds (approximately) the same share of the reference
    data (weighted if weights are given). Outer edges are -inf and +inf so that the same
    edges can be applied to a synthetic sample with a wider range."""
    ref = np.asarray(ref, float)
    w = np.ones_like(ref) if w_ref is None else np.asarray(w_ref, float)
    inner = _weighted_quantiles(ref, w, np.linspace(0, 1, n_bins + 1)[1:-1])
    return np.concatenate([[-np.inf], inner, [np.inf]])


def bin_proportions(x: np.ndarray, edges: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """Weighted share of the sample in each bin."""
    x = np.asarray(x, float)
    w = np.ones_like(x) if w is None else np.asarray(w, float)
    idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, len(edges) - 2)
    p = np.bincount(idx, weights=w, minlength=len(edges) - 1)
    return p / p.sum()


def uniform_weights(n_bins: int) -> np.ndarray:
    """Bin weights omega = 1 everywhere: the 'no system under assessment' case (Wu 2026
    §2.3 allows any weight function; uniform is the neutral choice)."""
    return np.ones(n_bins)


def theta_Theta(p_ref: np.ndarray, p_syn: np.ndarray, omega: np.ndarray,
                eps: float = 1e-12) -> tuple[float, float, np.ndarray, np.ndarray]:
    """
    theta = max_i |dP_i / P_ref,i| * omega_i      (worst weighted relative deviation, Eq. 1)
    Theta = sum_i |dP_i| * omega_i                (aggregate weighted absolute deviation, Eq. 2)
    Also returns the per-bin contributions (the paper's diagnostic, §3.5.3).
    """
    p_ref = np.asarray(p_ref, float); p_syn = np.asarray(p_syn, float)
    omega = np.asarray(omega, float)
    dP = p_syn - p_ref
    rel = np.abs(dP) / np.maximum(p_ref, eps) * omega
    absd = np.abs(dP) * omega
    return float(rel.max()), float(absd.sum()), rel, absd
