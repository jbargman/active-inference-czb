"""
Practical equivalence testing for synthetic datasets — the binning-based statistics and
ROPE decision of Wu, Sander, Flannagan & Bärgman (2026), "Practical validation of synthetic
pre-crash scenarios" (extending Wu et al. 2025, IAVVC).

This package is deliberately self-contained and generic: it takes one-dimensional samples
(with optional weights) for a reference and a synthetic dataset and returns the two
statistics theta (worst weighted bin deviation) and Theta (aggregate weighted deviation),
their uncertainty intervals, and the equivalence decision against a ROPE. It knows nothing
about driving, seeds, or causation models, so it can be reused for any metric.

Uncertainty: the paper fits Bayesian distribution models and evaluates the statistics on
paired posterior draws. Here the default is a weighted bootstrap of both samples (model-free);
a hook is left for plugging in posterior draws from the authors' `bayes-binned-equivalence`
code when that is available. The two are not identical and the report says which was used.

CONSERVATISM WARNING: theta is a maximum over bins, so its bootstrap distribution has a
noise floor of roughly sqrt(2 (1-1/N) / (P_bin n_eff)) even for identical distributions —
about 0.3 for a 100-sample reference with five bins, i.e. no dataset can pass the 0.10 ROPE
against so small a reference under bootstrap uncertainty. Use as large a reference as is
available (the QUADRIS reference costs no simulation, so use all 5 000), or plug in the
paper's parametric posterior draws.
"""
from .binned import (quantile_bin_edges, bin_proportions, theta_Theta, n_bins_rule,
                     uniform_weights)
from .test import EquivalenceResult, equivalence_test, MetricSpec, run_metric_suite
from .report import results_table, aggregate_table

__all__ = ["quantile_bin_edges", "bin_proportions", "theta_Theta", "n_bins_rule",
           "uniform_weights", "EquivalenceResult", "equivalence_test", "MetricSpec",
           "run_metric_suite", "results_table", "aggregate_table"]
