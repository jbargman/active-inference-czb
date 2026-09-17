"""
Component C1 -- the probability that a vehicle in the adjacent lane STARTS a lane change within the
next time bin, given its context. Julian Schumann's remark to Jonas (2026-09-17) was that this is
likely the most important part of a cut-in model; in the rollout formulation it is the prior p0 and
its dependence on the scene (`docs/rollout_boundary_design_note.md` section 1.1).

Estimator: a discrete-time logistic hazard. Every exposure episode (a vehicle that COULD change
lanes, whether or not it does) is cut into bins of `dt_bin`; each bin is a row with the features
at its start and a flag for whether the change began in that bin; rows stop after the event bin.
Censored episodes (no change while observed) contribute all their bins with flag 0. This is the
person-period form of survival analysis, and its fit is ordinary logistic regression with an
intercept, by Newton-Raphson with a small ridge for stability.

What it needs from the data that the current interface does NOT carry: episodes of adjacent-lane
vehicles that did not cut in (exposure), and the partner's own context (its headway to the vehicle
ahead of it, the gap it would enter). See `docs/generative_model_framework.md` section 4.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def person_period(episodes: list[dict], dt_bin: float) -> pd.DataFrame:
    """Expand episodes into one row per (episode, bin).

    Each episode is {"t": array, "X": array (T x k), "t_event": float or None}. Features are taken
    at the sample nearest the bin start. Rows stop after the bin containing the event.
    """
    rows = []
    for i, ep in enumerate(episodes):
        t = np.asarray(ep["t"], float)
        X = np.asarray(ep["X"], float)
        if X.ndim == 1:
            X = X[:, None]
        t_ev = ep.get("t_event")
        t_ev = None if t_ev is None or not np.isfinite(t_ev) else float(t_ev)
        b = t[0]
        while b < t[-1] - 1e-9:
            j = int(np.argmin(np.abs(t - b)))
            ev = int(t_ev is not None and b <= t_ev < b + dt_bin)
            rows.append({"episode": i, "bin_start_s": float(b), "event": ev,
                         **{f"x{c}": float(X[j, c]) for c in range(X.shape[1])}})
            if ev:
                break
            b += dt_bin
    return pd.DataFrame(rows)


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_logistic_hazard(X, y, l2: float = 1e-4, max_iter: int = 100) -> dict:
    """Logistic regression of the event flag on the features, with an intercept.

    Returns coef (intercept first), their standard errors from the observed information,
    the log-likelihood, the constant-hazard log-likelihood and the counts.
    """
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    n = len(y)
    A = np.column_stack([np.ones(n), X]) if X.shape[1] else np.ones((n, 1))
    k = A.shape[1]
    ridge = np.full(k, l2)
    ridge[0] = 0.0
    beta = np.zeros(k)
    for _ in range(max_iter):
        p = _sigmoid(A @ beta)
        grad = A.T @ (y - p) - ridge * beta
        W = p * (1 - p)
        H = -(A.T * W) @ A - np.diag(ridge)
        step = np.linalg.solve(H, grad)
        beta = beta - step
        if np.max(np.abs(step)) < 1e-9:
            break
    p = np.clip(_sigmoid(A @ beta), 1e-12, 1 - 1e-12)
    ll = float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))
    W = p * (1 - p)
    H = -(A.T * W) @ A - np.diag(ridge)
    cov = np.linalg.inv(-H)
    pbar = np.clip(y.mean(), 1e-12, 1 - 1e-12)
    ll0 = float(np.sum(y * np.log(pbar) + (1 - y) * np.log(1 - pbar)))
    return {"coef": beta, "se": np.sqrt(np.diag(cov)), "loglik": ll, "loglik_const": ll0,
            "n": int(n), "n_events": int(y.sum())}


def predict_hazard(coef, X) -> np.ndarray:
    """P(event in the bin | features) under a fitted model."""
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    A = np.column_stack([np.ones(len(X)), X]) if X.shape[1] else np.ones((len(X), 1))
    return _sigmoid(A @ np.asarray(coef, float))


def calibration_table(p, y, n_bins: int = 10, min_n: int = 5) -> pd.DataFrame:
    """Predicted against observed event rate by predicted-probability bin; bins with fewer than
    `min_n` rows have their rates suppressed (NaN) but keep their count, per the export rule."""
    p = np.asarray(p, float)
    y = np.asarray(y, float)
    edges = np.quantile(p, np.linspace(0, 1, n_bins + 1))
    edges[-1] += 1e-12
    idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        m = idx == b
        n = int(m.sum())
        ok = n >= min_n
        rows.append({"bin": b, "n": n,
                     "mean_pred": float(p[m].mean()) if ok else np.nan,
                     "mean_obs": float(y[m].mean()) if ok else np.nan})
    return pd.DataFrame(rows)
