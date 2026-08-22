"""
Driving scenarios -- the generative *process* (the real world), as opposed to the agent's
generative *model*.

Two of the three paradigmatic scenarios from Schumann et al. (2026):

  * `RearEndScenario`      -- lead vehicle brakes hard (front-to-rear conflict)
  * `LateralIncursionScenario` -- oncoming vehicle cuts across the ego's path

The other vehicle is *non-reactive* to the ego, exactly as in the paper (a stated limitation:
it means there is no negotiation or interaction).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import bicycle as bk
from .bicycle import BicycleParams, DELTA, THETA, V, X, Y


@dataclass
class ScenarioResult:
    t: np.ndarray
    ego: np.ndarray            # (T, 5)
    other: np.ndarray          # (T, 5)
    actions: np.ndarray        # (T, 2)
    info: list                 # per-step agent info dicts
    collided: bool
    min_gap: float


class _BaseScenario:
    veh: BicycleParams

    def initial_states(self):
        raise NotImplementedError

    def other_action(self, t: int, other_state: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def run(self, agent, T: int = 50, verbose: bool = False) -> ScenarioResult:
        self._a_other = 0.0
        ego, other = self.initial_states()
        agent.reset(ego, other)

        E, O, A, I = [], [], [], []
        collided = False
        min_gap = np.inf

        for t in range(T):
            E.append(ego.copy())
            O.append(other.copy())

            action, info = agent.step(ego, other)
            A.append(action.copy())
            I.append(info)

            ego = bk.step(ego, action, self.veh)
            other = bk.step(other, self.other_action(t, other), self.veh)

            gap = self._gap(ego, other)
            min_gap = min(min_gap, gap)
            if self._collision(ego, other):
                collided = True
                if verbose:
                    print(f"  collision at t={t * self.veh.dt:.1f}s")
                break

        return ScenarioResult(
            t=np.arange(len(E)) * self.veh.dt,
            ego=np.array(E), other=np.array(O), actions=np.array(A),
            info=I, collided=collided, min_gap=float(min_gap),
        )

    def _gap(self, ego, other):
        """Box clearance: negative iff the vehicles overlap, so it is consistent with
        `_collision` (a Euclidean centre distance is not)."""
        dx = abs(other[X] - ego[X])
        dy = abs(other[Y] - ego[Y])
        return float(max(dx - self.veh.length, dy - self.veh.width))

    def _collision(self, ego, other):
        return self._gap(ego, other) < 0.0


@dataclass
class RearEndScenario(_BaseScenario):
    """
    Front-to-rear: both vehicles at `v0` in the same lane, separated by `time_gap` seconds
    bumper-to-bumper. At `t_brake` the lead vehicle brakes at `a_brake` until stopped.

    Paper cases: (v0=15, gap=1.5) -> braking only; (v0=25, gap=1.0) -> brake + swerve.

    Per the Supplementary Information the lead vehicle drives straight for 5 s, then applies
    a jerk of -10 m/s^3 until reaching -6 m/s^2, holding that until standstill.
    """
    v0: float = 15.0
    time_gap: float = 1.5
    a_brake: float = -6.0
    jerk: float = -10.0
    t_brake: float = 5.0
    lane_centre: float = 0.0
    veh: BicycleParams = field(default_factory=BicycleParams)
    _a_other: float = 0.0

    def initial_states(self):
        gap = self.v0 * self.time_gap
        ego = np.array([0.0, self.lane_centre, 0.0, 0.0, self.v0])
        other = np.array([gap + self.veh.length, self.lane_centre, 0.0, 0.0, self.v0])
        return ego, other

    def other_action(self, t, other_state):
        if t * self.veh.dt >= self.t_brake and other_state[V] > 0.05:
            # ramp in the deceleration at the specified jerk rather than stepping to it
            self._a_other = max(self._a_other + self.jerk * self.veh.dt, self.a_brake)
        elif other_state[V] <= 0.05:
            self._a_other = 0.0
        return np.array([self._a_other, 0.0])


@dataclass
class LateralIncursionScenario(_BaseScenario):
    """
    Opposite-direction lateral incursion: an oncoming vehicle in the adjacent (opposing) lane
    suddenly steers across into the ego's lane at `t_incursion`.

    The interesting property for us is that *before* the incursion the situation is entirely
    normal -- the norm-conditioned prediction keeps the agent relaxed -- and the surprise
    signal is near zero. It rises only once the norm is violated.
    """
    v0: float = 15.0
    v_other: float = 15.0
    initial_distance: float = 90.0
    t_incursion: float = 2.0
    incursion_steer_rate: float = 0.10      # [1/s]
    incursion_duration: float = 1.2         # [s]
    lane_width: float = 3.65
    lane_centre: float = 0.0
    veh: BicycleParams = field(default_factory=BicycleParams)

    def initial_states(self):
        ego = np.array([0.0, self.lane_centre, 0.0, 0.0, self.v0])
        # oncoming: in the left lane, heading towards the ego (theta = pi)
        other = np.array([self.initial_distance, self.lane_centre + self.lane_width,
                          np.pi, 0.0, self.v_other])
        return ego, other

    def other_action(self, t, other_state):
        tt = t * self.veh.dt
        if self.t_incursion <= tt < self.t_incursion + self.incursion_duration:
            # steer towards the ego's lane (negative y direction in the oncoming frame)
            return np.array([0.0, self.incursion_steer_rate])
        return np.array([0.0, 0.0])
