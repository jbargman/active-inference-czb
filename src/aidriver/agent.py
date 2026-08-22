"""
A compact, readable re-implementation of the active-inference collision-avoidance agent of
Schumann et al. (2026), Nat. Commun. 17:5009.

This is *not* a fork of the authors' code (which lives in `external/aica`, is PyTorch/GPU
oriented and ~22 kLOC). It is an independent NumPy implementation of the same architecture,
written so that each mechanism in the paper is one obvious function and can be ablated,
inspected, or reused for comfort-zone work. Where the two differ, the authors' code is the
reference; differences are listed in `notes/03_replication.md`.

Architecture (Fig. 2 of the paper), per timestep:

    a) observe  -> update belief q(s) about the other vehicle          [particle filter,
                                                                        looming perception]
    b) predict  -> roll the belief forward under norm-biased dynamics  [norm-conditioned PF]
    c) evaluate -> accumulate surprise about the current policy        [residual information
                                                                        of pragmatic value]
    d) plan     -> extend the policy, or fully re-plan if E >= 1       [CEM + pedal
                                                                        constraints]
    e) select   -> pick the policy minimising expected free energy     [pragmatic + epistemic]
    f) act      -> apply the first action to the world
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import bicycle as bk
from .bicycle import BicycleParams, DELTA, THETA, V, X, Y
from .preferences import (
    PreferenceParams, apply_running_min, inverse_tau, log_collision_pref,
    log_preference_terms, pragmatic_deficit, safety_margin,
)


# --------------------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------------------
@dataclass
class AgentParams:
    # planning (Table 1)
    horizon: int = 30                  # H  (x dt = 6 s)
    n_particles: int = 75              # N
    n_policies: int = 100              # M
    cem_iters: int = 10                # K
    elite_frac: float = 0.1            # beta
    a_sample_sd: float = 5.0           # initial CEM std on acceleration [m/s^2]
    omega_sample_sd: float = 0.1       # initial CEM std on steering rate [1/s]

    # belief / prediction noise
    sigma_a_belief: float = 3.0        # sigma_a,0   other vehicle accel noise, belief update
    sigma_omega_belief: float = 0.4575 # sigma_omega,0
    noise_pred_factor: float = 0.2     # extra factor applied during EFE prediction only
    # Assumed bound on how hard the other vehicle might brake. The authors calibrate this
    # (`a_tar_min`, via a free-following analysis) so that ordinary car following is stable:
    # without it, unbounded sampled decelerations make *every* following situation look like
    # a predicted collision, the agent panics, and the surprise signal never returns to zero.
    a_other_min_assumed: float = -4.0  # [m/s^2]
    # Spread of the *initial* belief about the other vehicle's acceleration. This is not the
    # same as the process noise sigma_a_belief: a driver entering a following situation has
    # been watching the lead vehicle for some time and believes it is holding its speed. If
    # the initial belief is as wide as the process noise (3 m/s^2), a single snapshot leaves
    # acceleration essentially unknown, ~15% of predicted futures are collisions, and the
    # model treats perfectly ordinary following as an emergency.
    sigma_a_init: float = 0.5          # [m/s^2]

    # perception
    use_looming: bool = True
    looming_threshold: float = 0.00215  # phi_dot_0 [rad/s]
    # Perceptual noise on the optical variables. These must be of the order of human visual
    # resolution (~1 arcmin ~ 3e-4 rad) and of the looming detection threshold; setting them
    # orders of magnitude smaller makes the likelihood a delta function, the particle filter
    # degenerates to a single particle, and the belief becomes an arbitrary sample rather
    # than a distribution.
    sigma_phi: float = 3e-4             # observation noise on visual angle [rad]
    sigma_phidot: float = 1e-3          # observation noise on looming [rad/s]
    sigma_y_obs: float = 0.20           # lateral position observation noise [m]
    resample_ess_frac: float = 0.5      # resample when N_eff < frac * N
    roughening: float = 0.05            # post-resampling jitter on control dims

    # norm conditioning
    use_norms: bool = True
    norm_horizon: int = 20             # H_n
    norm_softness: float = 0.5         # [m] softness of the lane-keeping norm
    norm_floor: float = 1e-3           # minimum normative weight (never fully rule out)

    # evidence accumulation
    drift_rate: float = 10 ** -5.95    # lambda
    evidence_threshold: float = 1.0
    use_evidence_accumulation: bool = True

    # pedal constraint
    use_pedals: bool = True
    pedal_hold_steps: int = 1          # 0.2 s at dt = 0.2 s
    a_coast: float = -0.1              # a_0, acceleration with no pedal pressed

    # epistemic value
    alpha: float = 1.0                 # 0 disables epistemic value
    warm_start_replan: bool = False    # see `step` (True was tried; no benefit)

    seed: int | None = 0


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def _logsumexp(a, axis=None):
    m = np.max(a, axis=axis, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)
    return np.squeeze(m + np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True)), axis=axis)


def lane_norm_compliance(y, lane_centre: float, lane_width: float, softness: float):
    """
    Normative probability of a lateral position: 1 inside your own lane, decaying smoothly
    outside it. This is the only traffic norm the rear-end and lateral-incursion scenarios
    need ("vehicles stay in their lane unless there is evidence otherwise"); the paper
    likewise implements only the scenario-relevant norms.
    """
    d = np.abs(np.asarray(y, dtype=float) - lane_centre) - lane_width / 2.0
    return 1.0 / (1.0 + np.exp(d / softness))


def apply_pedal_constraint(a_seq: np.ndarray, a_prev: np.ndarray, p: AgentParams,
                           dt: float) -> np.ndarray:
    """
    One foot, two pedals (Schumann et al., Supp. 2.3).

    A driver cannot jump from throttle to brake instantaneously: the transition must pass
    through the coasting acceleration a_0 and hold there for ~0.2 s. We enforce this by
    detecting sign changes across a_0 in the planned acceleration sequence and inserting the
    hold. Removing this (`use_pedals=False`) is one of the paper's ablations and makes the
    model brake unrealistically early/fast.

    a_seq : (..., H) planned accelerations
    a_prev: (...,)   acceleration currently being applied
    """
    if not p.use_pedals:
        return a_seq
    a = a_seq.copy()
    prev = np.asarray(a_prev, dtype=float)
    hold = np.zeros(a.shape[:-1], dtype=int)
    for k in range(a.shape[-1]):
        cur = a[..., k]
        crossing = ((prev > p.a_coast) & (cur < p.a_coast)) | \
                   ((prev < p.a_coast) & (cur > p.a_coast))
        start_hold = crossing & (hold == 0)
        hold = np.where(start_hold, p.pedal_hold_steps, hold)
        holding = hold > 0
        cur = np.where(holding, p.a_coast, cur)
        hold = np.maximum(hold - 1, 0)
        a[..., k] = cur
        prev = cur
    return a


# --------------------------------------------------------------------------------------
# the agent
# --------------------------------------------------------------------------------------
class ActiveInferenceDriver:
    """
    Parameters
    ----------
    pref
        Preference function parameters -- the driver's goals, and hence its comfort zone.
    params
        Model/algorithm parameters.
    veh
        Vehicle and timestep parameters.

    Usage
    -----
    >>> agent = ActiveInferenceDriver(pref, params)                      # doctest: +SKIP
    >>> agent.reset(ego_state, other_state)                              # doctest: +SKIP
    >>> action, info = agent.step(ego_state, observed_other_state)       # doctest: +SKIP
    """

    def __init__(self, pref: PreferenceParams, params: AgentParams | None = None,
                 veh: BicycleParams | None = None):
        self.pref = pref
        self.p = params or AgentParams()
        self.veh = veh or pref.vehicle
        self.rng = np.random.default_rng(self.p.seed)

        self.belief = None          # (N, 7): other [x,y,theta,delta,v, a_ctrl, omega_ctrl]
        self.policy = None          # (H, 2) current plan
        self.evidence = 0.0
        self.a_applied = 0.0
        self.t = 0
        self.log = []

    # ---------------------------------------------------------------- (a) perception
    def reset(self, ego_state: np.ndarray, other_state: np.ndarray):
        N = self.p.n_particles
        s = np.tile(np.asarray(other_state, dtype=float), (N, 1))
        ctrl = np.zeros((N, 2))
        self.belief = np.concatenate([s, ctrl], axis=1)
        # initial spread on the other vehicle's control inputs
        self.belief[:, 5] += self.rng.normal(0, self.p.sigma_a_init, N)
        self.belief[:, 6] += self.rng.normal(0, self.p.sigma_omega_belief * 0.1, N)
        self.belief[:, 5] = np.clip(self.belief[:, 5],
                                    self.p.a_other_min_assumed, self.veh.a_max)
        self.w_belief = np.full(N, 1.0 / N)
        # particles are initialised *at* the first observed state, so the first belief
        # update must not propagate them again (that would introduce a one-step lag and
        # systematically bias the inferred acceleration)
        self._first_update = True
        self.policy = np.zeros((self.p.horizon, 2))
        self.policy[:, 0] = self.p.a_coast
        self.evidence = 0.0
        self.a_applied = 0.0
        self.t = 0
        self.log = []

    def update_belief(self, ego_state: np.ndarray, other_obs: np.ndarray):
        """
        Bayesian belief update with looming-based perception.

        Particles are advanced by the transition model, then weighted by the likelihood of
        the observation. With `use_looming`, the observation is the pair (phi, phi_dot) --
        visual angle and its rate -- rather than position and speed. Two consequences fall
        out of the geometry:
          * position/speed uncertainty grows with distance;
          * a closing speed producing |phi_dot| below threshold is not perceived at all, so
            the particles keep their prior (constant-speed) belief and detection is delayed.
        """
        p, veh = self.p, self.veh
        b = self.belief.copy()

        # predict step: propagate particles from t-1 to t under their own control inputs
        # plus process noise (skipped on the very first update, see `reset`)
        if self._first_update:
            self._first_update = False
        else:
            u = b[:, 5:7].copy()
            u[:, 0] += self.rng.normal(0, p.sigma_a_belief, len(b))
            u[:, 1] += self.rng.normal(0, p.sigma_omega_belief, len(b))
            u[:, 0] = np.clip(u[:, 0], p.a_other_min_assumed, veh.a_max)
            b[:, :5] = bk.step(b[:, :5], u, veh)
            b[:, 5:7] = u

        # likelihood of the observation under each particle
        if p.use_looming:
            gap_o = np.abs(other_obs[X] - ego_state[X]) - veh.length
            close_o = ego_state[V] - other_obs[V]
            phi_o = bk.visual_angle(gap_o, veh.width)
            phid_o = bk.looming_rate(gap_o, close_o, veh.width)
            if abs(phid_o) < p.looming_threshold:
                phid_o = 0.0            # sub-threshold looming is not perceived

            gap_p = np.abs(b[:, X] - ego_state[X]) - veh.length
            close_p = ego_state[V] - b[:, V]
            phi_p = bk.visual_angle(gap_p, veh.width)
            phid_p = bk.looming_rate(gap_p, close_p, veh.width)
            phid_p = np.where(np.abs(phid_p) < p.looming_threshold, 0.0, phid_p)

            loglik = (-0.5 * ((phi_p - phi_o) / p.sigma_phi) ** 2
                      - 0.5 * ((phid_p - phid_o) / p.sigma_phidot) ** 2)
            # lateral position is perceived directly (it is not a looming cue)
            loglik += -0.5 * ((b[:, Y] - other_obs[Y]) / p.sigma_y_obs) ** 2
        else:
            sd = np.array([0.5, 0.10, 0.05, 0.05, 0.5])
            loglik = -0.5 * (((b[:, :5] - other_obs) / sd) ** 2).sum(axis=1)

        w = self.w_belief * np.exp(loglik - loglik.max())
        if w.sum() <= 0 or not np.isfinite(w.sum()):
            w = np.ones(len(b))
        w /= w.sum()

        # Resample only when the effective sample size collapses (Engstrom et al. 2024 use
        # N_eff <= N/2). Resampling every step throws away diversity for no benefit and is a
        # classic route to particle impoverishment.
        n_eff = 1.0 / np.sum(w ** 2)
        if n_eff < p.resample_ess_frac * len(b):
            idx = self._systematic_resample(w)
            b = b[idx]
            w = np.full(len(b), 1.0 / len(b))
            # roughening: re-inject diversity on the control dimensions after resampling
            if p.roughening > 0:
                b[:, 5] += self.rng.normal(0, p.roughening * p.sigma_a_belief, len(b))
                b[:, 6] += self.rng.normal(0, p.roughening * p.sigma_omega_belief, len(b))
                b[:, 5] = np.clip(b[:, 5], p.a_other_min_assumed, veh.a_max)

        self.belief = b
        self.w_belief = w
        return w

    def _systematic_resample(self, w):
        N = len(w)
        pos = (self.rng.random() + np.arange(N)) / N
        return np.searchsorted(np.cumsum(w), pos).clip(0, N - 1)

    # -------------------------------------------------- (b) norm-conditioned prediction
    def predict_other(self, n_steps: int, noise_factor: float = 1.0):
        """
        Predict the other vehicle's future trajectories -- the norm-conditioned particle
        filter.

        Purely kinematic sampling is far too pessimistic (any adjacent vehicle *might* swerve
        in), so trajectories are re-weighted by a normative probability: vehicles are
        expected to stay in their lane. Crucially the weight is **upper-bounded by the
        other vehicle's current compliance**, so as soon as it is observed violating the norm
        the model stops trusting norms for it and admits the full kinematically-plausible
        long tail. That single mechanism is what lets one model be relaxed in normal driving
        and appropriately alarmed during an incursion.

        Returns
        -------
        traj : (N, n_steps, 5)
        w    : (N,) normalised particle weights after norm conditioning
        """
        p, veh = self.p, self.veh
        N = len(self.belief)
        s = self.belief[:, :5].copy()
        u0 = self.belief[:, 5:7].copy()

        sa = p.sigma_a_belief * noise_factor
        sw = p.sigma_omega_belief * noise_factor

        # Per-step transition noise, as in the paper (s_tau,n ~ p(s_tau | s_tau-1,n, a_tau-1)).
        # Distinct kinematically-plausible futures come from the *belief* spread in u0, which
        # persists across the horizon; making the added noise persistent as well was tried and
        # inflates the predicted speed spread to +/-6 m/s over 4 s, which makes the safety
        # term fire during ordinary following.
        traj = np.empty((N, n_steps, 5))
        for k in range(n_steps):
            u = u0.copy()
            u[:, 0] = np.clip(u[:, 0] + self.rng.normal(0, sa, N),
                              p.a_other_min_assumed, veh.a_max)
            u[:, 1] = u[:, 1] + self.rng.normal(0, sw, N)
            s = bk.step(s, u, veh)
            traj[:, k] = s

        if not p.use_norms:
            return traj, self.w_belief.copy()

        # normative probability now, in the short term, and at the medium-term horizon
        lane_c = self.pref.lane_centre
        lw = self.pref.lane_width
        pn_now = lane_norm_compliance(self.belief[:, Y], lane_c, lw, p.norm_softness)
        k_short = 0
        k_med = min(p.norm_horizon, n_steps) - 1
        pn_short = lane_norm_compliance(traj[:, k_short, Y], lane_c, lw, p.norm_softness)
        pn_med = lane_norm_compliance(traj[:, k_med, Y], lane_c, lw, p.norm_softness)

        # projected normative probability (paper Eq. 4): harmonic-style combination of the
        # short- and medium-term compliance, capped by the *current* compliance
        harm = 2.0 * pn_short * pn_med / np.maximum(pn_short + pn_med, 1e-12)
        pn = np.minimum(pn_now, harm)
        pn = np.maximum(pn, p.norm_floor)

        w = self.w_belief * pn
        w = w / w.sum()
        return traj, w

    # ------------------------------------------------------- (e) EFE of a policy set
    def _observations(self, ego_traj, other_traj, actions, other_accel=None):
        """
        Build the observation dict for the preference function from rolled-out trajectories.

        ego_traj  : (M, H, 5)
        other_traj: (N, H, 5)
        actions   : (M, H, 2)
        Returns arrays shaped (M, N, H).
        """
        ex = ego_traj[:, None, :, X]
        ey = ego_traj[:, None, :, Y]
        eth = ego_traj[:, None, :, THETA]
        ev = ego_traj[:, None, :, V]
        ox = other_traj[None, :, :, X]
        oy = other_traj[None, :, :, Y]
        oth = other_traj[None, :, :, THETA]
        ov = other_traj[None, :, :, V]

        dx = ox - ex
        dy = oy - ey
        shape = np.broadcast_shapes(dx.shape, ey.shape, actions[:, None, :, 0].shape)

        a = actions[:, None, :, 0]
        omega = actions[:, None, :, 1]
        oa = np.zeros_like(dx) if other_accel is None else other_accel[None, :, None]

        obs = {
            "v": np.broadcast_to(ev, shape),
            "a": np.broadcast_to(a, shape),
            "omega": np.broadcast_to(omega, shape),
            "y": np.broadcast_to(ey, shape),
            "theta": np.broadcast_to(eth, shape),
            "dx": np.broadcast_to(dx, shape),
            "dy": np.broadcast_to(dy, shape),
            "v_other": np.broadcast_to(ov, shape),
            "a_other": np.broadcast_to(oa, shape),
            "theta_other": np.broadcast_to(oth, shape),
        }
        obs["tau_inv"] = inverse_tau(obs["dx"], obs["v"], obs["v_other"], self.pref)
        return obs

    def _log_pref_sum(self, obs):
        """
        Total log-preference per (policy, particle, timestep), with the SI Eq. 47 running
        minimum applied to the collision factor along the horizon so that a collision keeps
        being punished for the rest of the rollout.
        """
        terms = log_preference_terms(obs, self.pref)
        terms["collision"] = apply_running_min(terms["collision"], axis=-1)
        return sum(terms.values()), terms

    def expected_free_energy(self, ego_state, actions, other_traj, w):
        """
        G(pi) = -SUM_tau [ pragmatic(tau) + alpha * epistemic(tau) ]

        Pragmatic value is the particle-weighted mean log-preference of the predicted
        observations (Eq. 8). Epistemic value uses the posterior-predictive-entropy minus
        expected-ambiguity decomposition (Eq. 7/9); with a fixed-precision observation model
        the ambiguity term is constant, so what remains is the *spread* of predicted
        observations -- policies that would reveal more about the world score higher.
        """
        ego_traj = bk.rollout(ego_state, actions, self.veh)          # (M, H, 5)
        obs = self._observations(ego_traj, other_traj, actions)
        logp, _ = self._log_pref_sum(obs)                            # (M, N, H)

        prag = np.einsum("mnh,n->m", logp, w)                        # sum over H, weighted N

        if self.p.alpha != 0.0:
            # Epistemic value = posterior predictive entropy - expected ambiguity (Eq. 7).
            # Under a Gaussian observation model with per-state precision, this reduces to
            #     g_epist = 0.5 * log(1 + var_belief / sigma_obs^2),
            # i.e. the expected information gain about the other vehicle's position. The
            # observation precision is *distance dependent* because perception is by looming:
            # d(phi)/dd = -W/(d^2 + W^2/4), so a fixed angular error maps to a positional
            # error that grows with the square of distance.
            sep = obs["dx"]
            mean = np.einsum("mnh,n->mh", sep, w)
            var = np.einsum("mnh,n->mh", (sep - mean[:, None, :]) ** 2, w)
            d = np.maximum(np.abs(mean), 1.0)
            sigma_d = self.p.sigma_phi * (d ** 2 + self.veh.width ** 2 / 4.0) / self.veh.width
            epist = 0.5 * np.log1p(np.maximum(var, 0.0) /
                                   np.maximum(sigma_d ** 2, 1e-12)).sum(axis=1)
        else:
            epist = np.zeros(len(actions))

        return -(prag + self.p.alpha * epist), ego_traj, obs

    # ------------------------------------------------------------- (d) policy sampling
    def _cem(self, ego_state, other_traj, w, init_mean=None):
        """
        Cross-entropy-method MPC with a bounded number of evaluated policies -- the model's
        bounded-rationality mechanism. Sample M policies, keep the beta*M with lowest EFE,
        refit a Gaussian, repeat K times, then take the single best sample.
        """
        p = self.p
        H, M = p.horizon, p.n_policies
        n_elite = max(2, int(p.elite_frac * M))

        mean = np.zeros((H, 2)) if init_mean is None else init_mean.copy()
        std = np.stack([np.full(H, p.a_sample_sd), np.full(H, p.omega_sample_sd)], axis=1)

        best_a, best_G = None, np.inf
        for _ in range(p.cem_iters):
            cand = mean[None] + std[None] * self.rng.standard_normal((M, H, 2))
            cand[..., 0] = np.clip(cand[..., 0], -self.veh.a_max, self.veh.a_max)
            cand[..., 1] = np.clip(cand[..., 1], -self.veh.omega_max, self.veh.omega_max)
            cand[..., 0] = apply_pedal_constraint(cand[..., 0], self.a_applied, p, self.veh.dt)

            G, _, _ = self.expected_free_energy(ego_state, cand, other_traj, w)
            order = np.argsort(G)
            elite = cand[order[:n_elite]]
            if not np.all(np.isfinite(G)):
                G = np.nan_to_num(G, nan=np.inf, posinf=np.inf)
                order = np.argsort(G)
            if best_a is None or G[order[0]] < best_G:
                best_G, best_a = G[order[0]], cand[order[0]].copy()
            mean = elite.mean(axis=0)
            std = elite.std(axis=0) + 1e-3
        return best_a, best_G

    # -------------------------------------------------------- (c) surprise accumulation
    def policy_surprise(self, ego_state, other_traj, w, policy):
        """
        eps_t = H * max_o log p(o) - SUM_tau g_pragm(o_tau | current policy)   (Eq. 13)

        The residual information of the pragmatic value: how far short of the best-possible
        future the *current* plan now falls. Zero while the plan still delivers what the
        driver wants -- so nothing accumulates during comfortable driving.
        """
        ego_traj = bk.rollout(ego_state, policy[None], self.veh)
        obs = self._observations(ego_traj, other_traj, policy[None])
        logp, _ = self._log_pref_sum(obs)                        # (1, N, H)
        prag = float(np.einsum("mnh,n->m", logp, w)[0])
        eps = self.p.horizon * self.pref.max_log_preference() - prag
        return max(eps, 0.0)

    # ------------------------------------------------------------------------- step
    def step(self, ego_state: np.ndarray, other_obs: np.ndarray):
        """
        One control cycle. Returns (action, info).

        `info` records the internals that matter for analysis: accumulated evidence, whether
        a re-plan was triggered, the surprise signal, and the safety margin -- the last being
        the comfort-zone quantity.
        """
        p = self.p
        self.update_belief(ego_state, other_obs)

        # prediction used for evaluating the *current* policy and for planning
        other_traj, w = self.predict_other(p.horizon, noise_factor=p.noise_pred_factor)

        eps = self.policy_surprise(ego_state, other_traj, w, self.policy)

        replanned = False
        if p.use_evidence_accumulation:
            self.evidence += p.drift_rate * eps
            if self.evidence >= p.evidence_threshold:
                replanned = True
                self.evidence = 0.0
        else:
            replanned = True

        if replanned:
            # (d.ii) full re-plan. The paper resamples from scratch; we optionally warm-start
            # from the shifted previous policy, which cuts CEM jitter (and hence the control
            # effort that jitter contributes to the surprise signal) without changing what is
            # being optimised. Set `warm_start_replan=False` for the paper's behaviour.
            init = None
            if self.p.warm_start_replan and self.policy is not None:
                init = np.vstack([self.policy[1:], self.policy[-1:]])
            self.policy, G = self._cem(ego_state, other_traj, w, init_mean=init)
        else:
            # (d.i) extend: drop the executed action, plan only the new final one
            shifted = np.vstack([self.policy[1:], self.policy[-1:]])
            self.policy, G = self._cem(ego_state, other_traj, w, init_mean=shifted)

        action = self.policy[0].copy()
        self.a_applied = float(action[0])

        gap = float(other_obs[X] - ego_state[X] - self.veh.length)
        margin = float(safety_margin({
            "v": ego_state[V], "a": self.a_applied,
            "dx": other_obs[X] - ego_state[X], "dy": other_obs[Y] - ego_state[Y],
            "v_other": other_obs[V], "a_other": float(np.sum(self.w_belief
                                                             * self.belief[:, 5])),
            "theta": ego_state[THETA], "theta_other": other_obs[THETA],
        }, self.pref))

        info = {
            "t": self.t,
            "evidence": float(self.evidence),
            "surprise": float(eps),
            "replanned": bool(replanned),
            "EFE": float(G),
            "gap": gap,
            "safety_margin": margin,
            "belief_mean_v": float(np.sum(self.w_belief * self.belief[:, V])),
            "belief_sd_v": float(np.sqrt(np.sum(
                self.w_belief * (self.belief[:, V]
                                 - np.sum(self.w_belief * self.belief[:, V])) ** 2))),
            "belief_mean_a": float(np.sum(self.w_belief * self.belief[:, 5])),
        }
        self.log.append(info)
        self.t += 1
        return action, info
