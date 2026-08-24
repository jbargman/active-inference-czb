"""
Tier-2 adapter: run the authors' closed-loop active-inference driver (external/aica,
unmodified) on QUADRIS rear-end seeds, with the scripted lead vehicle replaced by a
replay of the seed's lead-speed profile.

Implements step 6 of docs/crash_causation_plan.md section 9:
  - lead replay: a Dynamics_true subclass whose forward_state_tar applies the seed's
    per-step lead acceleration instead of the built-in countdown-and-brake script
    (the authors' files are not edited; the class is swapped into the loaded module
    namespace, the same pattern run_rear_end_single.py uses for run_simulation)
  - gaze schedule: an optional list of off-road intervals; during one, the agent's
    stored discrete action is forced to gaze-off before the next belief update, so
    the observation-noise multiplier I_factor (decoder.py) degrades the update --
    the environment itself is unaffected, which is how the authors' gaze state works
  - checkpointing and restart: a .partial pickle every few steps, and completed seeds
    (out .pkl exists) are skipped, per the HANDOFF section 3 rule

Smoke test (default): the 5 quintile-spanning seeds of the tier-1 100-seed sample,
attentive (no glances), batch of 4 repeats, compared against tier-1's condition A
onsets in tier2/smoke_summary.md.

    python replication/causation/tier2_rear_end.py                # smoke test
    python replication/causation/tier2_rear_end.py --seed-ids 2500 4000
    python replication/causation/tier2_rear_end.py --glance 1.0 2.5   # one forced glance

Known extrapolation: seeds with initial speeds below 10 m/s sit under the authors'
calibration table (Results_following); find_parameters clips to the table edge. The
same caveat is stated in the plan, section 6 "Low speeds".
"""
from __future__ import annotations

import argparse
import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "replication"))

# importing run_rear_end_single chdirs into external/aica (their code reads
# Results_following/ by relative path) and loads their simulation module
import run_rear_end_single as rres                                        # noqa: E402
from run_rear_end_single import build_model_params, build_initial_state   # noqa: E402
from src.utils.simulation import find_parameters                          # noqa: E402
from quadris import load_synthetic, sample_seeds                          # noqa: E402
from quadris.load import Seed                                             # noqa: E402

sim_rear_end = rres.sim_rear_end
Dynamics_true = sim_rear_end.Dynamics_true

OUT = HERE / "tier2"
DT = 0.2


class DynamicsLeadReplay(Dynamics_true):
    """Dynamics_true with the target agent following a prescribed acceleration series.

    The base class scripts the lead with a countdown (t_brake) and a jerk ramp; here
    the lead's acceleration at environment step k is a_lead[k] (clamped so speed never
    goes negative), which replays the QUADRIS seed's recorded profile. Everything about
    the ego vehicle, and the agent's generative model of the lead, is untouched.
    """

    def __init__(self, a_lead: np.ndarray, **kw):
        super().__init__(**kw)
        self._a_lead = torch.tensor(a_lead, dtype=torch.float32, device=self.device)
        self._k = 0

    def reset_clock(self):
        self._k = 0

    def forward_state_tar(self, eta_agent, bicycle_agent, ctrl_agent):
        ctrl = ctrl_agent.clone()
        k = min(self._k, len(self._a_lead) - 1)
        ctrl[..., 0] = self._a_lead[k]
        ctrl[..., 1] = 0.0
        # no reversing (same guard as the base class)
        ctrl[..., 0] = torch.maximum(ctrl[..., 0], -eta_agent[..., -1] / self.dt)
        eta_next = bicycle_agent.forward(eta_agent, ctrl[..., :2])
        self._k += 1
        return eta_next, ctrl


def lead_accel_steps(seed: Seed, n_steps: int) -> np.ndarray:
    """Per-step lead acceleration at DT, from the seed's speed profile; the profile is
    held at its last speed beyond the recorded series (same convention as tier 1)."""
    t_grid = np.arange(0, (n_steps + 1) * DT, DT)
    v = seed.lead_speed(t_grid)
    return np.diff(v) / DT


GAZE_ON = torch.tensor([1.0, 0.0])
GAZE_OFF = torch.tensor([0.0, 1.0])


def run_seed(seed: Seed, T: int, batch: int, out_path: Path,
             glance_intervals: list[tuple[float, float]] | None = None,
             i_factor: float | None = None, checkpoint_every: int = 5,
             torch_seed: int = 0, device=torch.device("cpu")) -> dict:
    model_params = build_model_params()
    initial_state = build_initial_state()

    v_tar0 = float(seed.lead_speed(np.array([0.0]))[0])
    x_tar = seed.d0 + initial_state["lf"] + initial_state["lr"]
    initial_state["v_ego"] = seed.v_f0
    initial_state["x_tar"] = x_tar
    initial_state["v_tar"] = v_tar0

    # the authors calibrate v_diff and the assumed a_tar_min per initial condition;
    # their table starts at v_tar = 10 m/s -- slower seeds clip to the table edge
    thw_des = x_tar / max(v_tar0, 0.5)
    v_diff, a_tar_min = find_parameters(
        max(v_tar0, 10.0), model_params["EA_fac"], model_params["noise_pred_fac"],
        model_params["H"], model_params["d_phi_thres"], thw_des)
    model_params["v_diff"] = v_diff
    model_params["a_tar_min_intensity"] = -a_tar_min / initial_state["a_max"]

    torch.manual_seed(torch_seed)
    Config, config = sim_rear_end.set_config(initial_state, model_params, a_tar_brake=6.0)
    # desired-speed convention (decided 2026-08-25): the speed the original follower later
    # reached, not its initial speed — otherwise a stopped/creeping follower has no motive
    # to accelerate into the conflict the way the generator's follower did. For seeds whose
    # followers do not accelerate the two conventions coincide (checked: max difference
    # 0.5 m/s over the 20-seed arbiter batch).
    v_des = float(np.max(seed.v_f_orig)) if seed.v_f_orig is not None else seed.v_f0
    Config["v_ego_des"] = v_des + model_params["v_diff"]
    config["reward"]["v_mu"] = Config["v_ego_des"]
    config["T"] = Config["T"] = T
    config["rollout_batch_size"] = batch
    # the built-in lead script must never fire under replay
    config["init_state"]["t_brake"] = 1e6
    config["init_state"]["j_brake"] = 0.0
    if i_factor is not None:
        config["decoder"]["I_factor"] = i_factor

    a_lead = lead_accel_steps(seed, T)
    saved_dyn, saved_run = sim_rear_end.Dynamics_true, sim_rear_end.run_simulation

    def replay_factory(**kw):
        return DynamicsLeadReplay(a_lead, **kw)

    def run_simulation(cfg, agent, env, eta, b, w):
        agent.reset(b, w)
        o = env.reset(eta)
        env.dynamics.reset_clock()
        eta = env.state.clone()
        keys = ["eta", "o", "a_disc", "a_cont"]
        data = {k: [] for k in keys}

        def stack(d):
            return {k: torch.stack(v, dim=1).detach().cpu().numpy() if v else None
                    for k, v in d.items()}

        for t in range(1, cfg["T"] + 1):
            with torch.no_grad():
                a_disc, a_cont = agent.choose_action(o, verbose=False)
            t_now = (t - 1) * DT
            if glance_intervals and any(t0 <= t_now < t1 for t0, t1 in glance_intervals):
                # gaze off: only the belief update sees this (via I_factor); the true
                # dynamics ignore the discrete action entirely
                a_disc = a_disc.clone()
                a_disc[0] = GAZE_OFF.to(a_disc.device)
                agent.a_disc = a_disc[0]
            o = env.step(a_disc[0], a_cont[0])
            data["eta"].append(eta)
            data["o"].append(o)
            data["a_disc"].append(a_disc)
            data["a_cont"].append(a_cont)
            eta = env.state.clone()
            if checkpoint_every and (t % checkpoint_every == 0 or t == cfg["T"]):
                with open(str(out_path) + ".partial", "wb") as f:
                    pickle.dump({"data": stack(data), "steps_done": t, "T_target": cfg["T"]}, f)
        return stack(data)

    sim_rear_end.Dynamics_true = replay_factory
    sim_rear_end.run_simulation = run_simulation
    try:
        t0 = time.time()
        data = sim_rear_end.simulate(config, device)
        runtime = time.time() - t0
    finally:
        sim_rear_end.Dynamics_true = saved_dyn
        sim_rear_end.run_simulation = saved_run

    result = {"seed_id": seed.seed_id, "v_f0": seed.v_f0, "d0": seed.d0,
              "v_tar0": v_tar0, "T": T, "batch": batch, "runtime_s": runtime,
              "glance_intervals": glance_intervals, "data": data,
              "config_note": {"v_diff": v_diff, "a_tar_min": float(a_tar_min),
                              "t_brake_disabled": True, "lead": "replay"}}
    with open(out_path, "wb") as f:
        pickle.dump(result, f)
    p = Path(str(out_path) + ".partial")
    if p.exists():
        p.unlink()
    return result


def summarize(result: dict, lf_lr: float = 4.2) -> list[dict]:
    """Per batch element: brake onset (first sustained a_ego < -1 m/s^2), crash, min gap."""
    eta = result["data"]["eta"]                     # [batch, T, 14]
    rows = []
    for bi in range(eta.shape[0]):
        x_e, v_e = eta[bi, :, 0], eta[bi, :, 4]
        x_t, v_t = eta[bi, :, 5], eta[bi, :, 9]
        gap = x_t - x_e - lf_lr
        a_e = np.diff(v_e, prepend=v_e[0]) / DT
        t = np.arange(len(v_e)) * DT
        # onset = first deceleration beyond 1 m/s^2 that either persists one more step or
        # stops the vehicle -- a single-step stop is a real brake response at low speed
        braking = a_e < -1.0
        onset = np.nan
        for i in np.flatnonzero(braking):
            persists = i + 1 < len(braking) and braking[i + 1]
            stops = v_e[min(i + 2, len(v_e) - 1)] <= 0.05
            if persists or stops or i >= len(braking) - 2:
                onset = t[i]
                break
        crash = gap <= 0
        rows.append(dict(seed_id=result["seed_id"], element=bi,
                         t_onset=onset,
                         crashed=bool(crash.any()),
                         t_impact=float(t[np.argmax(crash)]) if crash.any() else np.nan,
                         v_rel_impact=float((v_e - v_t)[np.argmax(crash)]) if crash.any() else 0.0,
                         a_f_min=float(a_e.min()), min_gap=float(gap.min()),
                         y_ego_max=float(np.abs(eta[bi, :, 1]).max())))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-ids", type=int, nargs="*", default=None,
                    help="QUADRIS seed ids; default = 5 v_f0 quintiles of the tier-1 sample")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--t-extra", type=float, default=4.0,
                    help="simulate this long past the seed's original impact [s]")
    ap.add_argument("--max-T", type=int, default=60)
    ap.add_argument("--glance", type=float, nargs=2, action="append", default=None,
                    metavar=("T0", "T1"), help="forced off-road glance interval [s]")
    ap.add_argument("--i-factor", type=float, default=None,
                    help="observation-noise multiplier while gaze off (authors' default 3)")
    ap.add_argument("--rng", type=int, default=0)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    all_seeds = load_synthetic()
    sample = sample_seeds(all_seeds, 100, rng=args.rng)

    if args.seed_ids:
        chosen = [s for s in sample if s.seed_id in args.seed_ids]
        missing = set(args.seed_ids) - {s.seed_id for s in chosen}
        chosen += [s for s in all_seeds if s.seed_id in missing]
    else:
        by_v = sorted(sample, key=lambda s: s.v_f0)
        chosen = [by_v[i] for i in (0, len(by_v) // 4, len(by_v) // 2,
                                    3 * len(by_v) // 4, len(by_v) - 1)]

    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    tag = "" if not args.glance else "_glance"
    rows = []
    for s in chosen:
        T = min(int(np.ceil((s.t_crash_orig + args.t_extra) / DT)), args.max_T)
        out_path = OUT / f"seed_{s.seed_id}{tag}.pkl"
        if out_path.exists():
            print(f"seed {s.seed_id}: exists, skipping", flush=True)
            with open(out_path, "rb") as f:
                result = pickle.load(f)
        else:
            print(f"seed {s.seed_id}: v_f0={s.v_f0:.1f} m/s, d0={s.d0:.1f} m, "
                  f"T={T} steps, batch={args.batch}", flush=True)
            result = run_seed(s, T, args.batch, out_path,
                              glance_intervals=[tuple(g) for g in args.glance] if args.glance else None,
                              i_factor=args.i_factor, device=device)
            print(f"  done in {result['runtime_s']:.0f} s", flush=True)
        rows.extend(summarize(result))

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(OUT / f"smoke_results{tag}.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
