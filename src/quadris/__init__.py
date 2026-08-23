"""
QUADRIS rear-end pre-crash scenarios: loading, sampling, and scenario metrics.

Data: github.com/JianWu09/QUADRIS-project-Pre-crash-near-crash-database (MIT).
  Synthetic_crash_scenarios.csv  5000 model-generated rear-end crashes, 20 Hz, columns
                                 id, t, v_f, v_l, d, lead_delta_v, weight
  Combined_incidents.csv         132 crashes + 82 near-crashes (SHRP2, CISS) described by the
                                 lead-vehicle profile parameters [v_c, a_1, a_2, tau_s, tau_1,
                                 tau_2] of Wu et al. (2024) and a weight; no follower state

This package knows nothing about driver models. It provides seeds (lead profile + follower
initial state + weight), a stratified weighted sampler, and the scenario metrics of
Wu et al. (2026): lead delta-v, P_inj, t_nr, a_min.
"""
from .load import Seed, load_synthetic, load_incidents, QUADRIS_DIR
from .sample import sample_seeds
from .metrics import delta_v_lead, p_inj_mais2, no_return_time, min_accel

__all__ = ["Seed", "load_synthetic", "load_incidents", "QUADRIS_DIR", "sample_seeds",
           "delta_v_lead", "p_inj_mais2", "no_return_time", "min_accel"]
