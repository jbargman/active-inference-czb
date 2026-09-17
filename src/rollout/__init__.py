"""The rollout formulation of the comfort-zone boundary (card JJ.1).

At the moment a stimulus clip is frozen, roll out a small menu of the ego's options against a
fan of the other road user's predicted futures, score every imagined future with the released
preference function in its residual-information form, and take as the criticality quantity the
gap in expected free energy between "continue" and the best alternative, **Delta G, in nats**.

  `belief`     the scene at the freeze as a Gaussian, plus the latent lane-change intention
  `predictor`  P0: the fan, constant velocity with growth and the intention mixture
  `policies`   the scenarios' instructed alternatives, as deterministic rollouts
  `efe`        G(pi) from the six preference terms; variants A (released) and B (no p_safe)
  `boundary`   Delta G, the log axis with its zero rule, the Monte Carlo standard error

Design: `docs/rollout_boundary_design_note.md` (2026-09-17, authorized 2026-09-18).
Implementer's brief: `handover_jj1_implementation.md`. Property tests: `tests/test_rollout.py`.
Nothing here is fitted to any response; the cards' scripts fit the same three-parameter
threshold model every axis in this project is given.
"""
from .belief import (Belief, Floors, Frame, Scene, FLOORS_STUDY1, FLOORS_STUDY2,
                     P_CHANGE_PRIOR, belief_at, update_intention, verify_floors)
from .boundary import Axis, axis, delta_g, mc_rule_e, mc_standard_error
from .efe import expected_free_energy, g_by_policy, log_terms, observations, variant_params
from .policies import (CUTIN_MENU, EgoPath, ego_rollout, ltap_rollout, overtake_rollout)
from .predictor import Futures, sample_futures

__all__ = [
    "Belief", "Floors", "Frame", "Scene", "FLOORS_STUDY1", "FLOORS_STUDY2", "P_CHANGE_PRIOR",
    "belief_at", "update_intention", "verify_floors",
    "Axis", "axis", "delta_g", "mc_rule_e", "mc_standard_error",
    "expected_free_energy", "g_by_policy", "log_terms", "observations", "variant_params",
    "CUTIN_MENU", "EgoPath", "ego_rollout", "ltap_rollout", "overtake_rollout",
    "Futures", "sample_futures",
]
