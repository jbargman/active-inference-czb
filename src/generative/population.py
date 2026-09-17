"""
Component C4 -- the ego's own normal: the states drivers routinely accept (following headway by
speed, passing clearance, accepted gaps). This is reference B of `docs/surprise_without_the_field.md`
and the population the CZB ellipse is a percentile of; the same distributions calibrate the
preference function's constants the way the authors calibrated the worst-case deceleration on free
following.

Two tools: a binned quantile summary with the export rule's small-cell suppression built in, and a
Gaussian reference whose squared Mahalanobis distance is twice the residual information under it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def binned_summary(values, by, edges, min_n: int = 5, quantiles=(0.1, 0.5, 0.9)) -> pd.DataFrame:
    """Quantiles of `values` within bins of `by`; bins with n < min_n keep n and get NaN quantiles."""
    values = np.asarray(values, float)
    by = np.asarray(by, float)
    edges = np.asarray(edges, float)
    ok = np.isfinite(values) & np.isfinite(by)
    values, by = values[ok], by[ok]
    idx = np.searchsorted(edges, by, side="right") - 1
    rows = []
    for b in range(len(edges) - 1):
        m = idx == b
        n = int(m.sum())
        row = {"bin_lo": float(edges[b]), "bin_hi": float(edges[b + 1]), "n": n}
        for q in quantiles:
            row[f"q{int(round(q * 100)):02d}"] = float(np.quantile(values[m], q)) if n >= min_n else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def gaussian_reference(X) -> dict:
    """Mean and covariance of accepted states; the reference for a joint percentile."""
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    mean = X.mean(axis=0)
    cov = np.atleast_2d(np.cov(X, rowvar=False))
    return {"mean": mean, "cov": cov, "inv": np.linalg.inv(cov), "n": int(len(X))}


def mahalanobis2(ref: dict, x) -> np.ndarray:
    """Squared Mahalanobis distance of rows of `x` from the reference; half of it is the
    residual information of the state under the Gaussian reference."""
    x = np.atleast_2d(np.asarray(x, float))
    d = x - ref["mean"]
    return np.einsum("ij,jk,ik->i", d, ref["inv"], d)
