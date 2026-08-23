"""
Crash-causation components around a driver response model — rear-end scenarios only.

Implements the four mechanisms of Bärgman, Svärd, Lundell & Hartelius (2024, TRF 104) as
separately switchable components, and two response models to put them around:

  * ActiveInferenceResponse  surprise accumulation on the comfort-zone field of the active
                             inference driver (tier 1: open-loop timing on the seed kinematics)
  * CBMResponse              the CBM's own process: fixed delay after the eyes return,
                             anchored at tau^-1 = 0.2 s^-1

Everything is configured through one `CausationConfig`; `CausationConfig()` with all
components off must reproduce the plain attentive driver. Each component carries
`enabled` and `describe()`, and the runner writes every description into its output.

Design note: the assessment of the generated crashes against a reference (the Wu et al.
equivalence framework) is NOT here — it lives in `src/equivalence/` and is reused unchanged.
"""
from .config import CausationConfig
from .glances import GlanceDistribution, GlanceSchedule, overshot_distribution, standin_shrp2_glances
from .decel import DecelerationDistribution, standin_shrp2_max_decel
from .response import ActiveInferenceResponse, CBMResponse, ResponseModel
from .simulate import PreResponseKinematics, execute_braking, Outcome
from .runner import run_seed, run_condition

__all__ = ["CausationConfig", "GlanceDistribution", "GlanceSchedule", "overshot_distribution",
           "standin_shrp2_glances", "DecelerationDistribution", "standin_shrp2_max_decel",
           "ActiveInferenceResponse", "CBMResponse", "ResponseModel", "PreResponseKinematics",
           "execute_braking", "Outcome", "run_seed", "run_condition"]
