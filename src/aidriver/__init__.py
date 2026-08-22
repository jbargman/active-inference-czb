"""
aidriver -- a compact NumPy re-implementation of the active-inference driver model of
Schumann et al. (2026), built for readability, ablation and comfort-zone analysis.

See `agent.ActiveInferenceDriver` for the model and `scenarios` for the test cases.
"""
from .bicycle import BicycleParams, step, rollout, visual_angle, looming_rate
from .preferences import (
    PreferenceParams, log_preference, log_preference_terms, pragmatic_deficit,
    safety_margin,
)
from .agent import ActiveInferenceDriver, AgentParams
from .scenarios import RearEndScenario, LateralIncursionScenario, ScenarioResult

__all__ = [
    "BicycleParams", "step", "rollout", "visual_angle", "looming_rate",
    "PreferenceParams", "log_preference", "log_preference_terms", "pragmatic_deficit",
    "safety_margin",
    "ActiveInferenceDriver", "AgentParams",
    "RearEndScenario", "LateralIncursionScenario", "ScenarioResult",
]
