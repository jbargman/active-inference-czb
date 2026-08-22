"""
Replication driver: run ONE front-to-rear configuration of the Schumann et al. (2026)
active-inference collision-avoidance model, using the authors' own code.

The authors' `simulation_rear_end.py` runs a 7 (time gap) x 4 (speed) x 128 (ablation
combinations) sweep with 32 repeats -- far too much for CPU. This script reuses their
`simulate()` path for a single initial condition so the model can actually be run and
inspected here.

Defaults reproduce the Nature Communications Fig. 3a case:
    v0 = 15 m/s, bumper-to-bumper time gap 1.5 s  -> braking-only avoidance.
Fig. 3b case is v0 = 25 m/s, time gap 1.0 s -> brake + swerve.

Usage:
    python replication/run_rear_end_single.py --v0 15 --gap 1.5 --T 40 --batch 4
"""
import argparse
import os
import pickle
import sys
import time

import numpy as np
import torch

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "external", "aica")
REPO = os.path.abspath(REPO)
sys.path.insert(0, REPO)
# the authors' code uses relative paths for Results_following/*.xlsx
os.chdir(REPO)

from src.utils.simulation import find_parameters  # noqa: E402


def load_authors_module(filename):
    """Import the authors' simulation script without running its trailing side effects.

    `simulation_rear_end.py` ends with module-level `import Analysis_rear_end` /
    `import visualization_rear_end`, which immediately try to read result files that do
    not exist until after a full sweep has been run. So we exec the source only up to the
    `if __name__ == "__main__":` guard, which gives us `set_config` and `simulate` with
    the authors' code completely unmodified.
    """
    import types
    path = os.path.join(REPO, filename)
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    marker = 'if __name__ == "__main__":'
    idx = src.find(marker)
    if idx == -1:
        raise RuntimeError(f"could not find __main__ guard in {filename}")
    mod = types.ModuleType(filename[:-3])
    mod.__file__ = path
    exec(compile(src[:idx], path, "exec"), mod.__dict__)
    return mod


sim_rear_end = load_authors_module("simulation_rear_end.py")


def make_checkpointing_run_simulation(out_path, every=5):
    """Drop-in replacement for the authors' `run_simulation` that saves as it goes.

    The upstream loop accumulates everything in memory and returns only at the end, so a run
    that is interrupted leaves nothing behind -- we lost a 29/50-step run that way, even
    though the brake response we wanted to measure had already happened by step 15. This
    version writes a partial pickle every `every` steps, so an interrupted run is still
    usable. The simulation itself is unchanged.
    """
    import pickle as _pickle

    import torch as _torch
    from tqdm import tqdm as _tqdm

    def run_simulation(config, agent, env, eta, b, w):
        agent.reset(b, w)
        o = env.reset(eta)
        eta = env.state.clone()

        keys = ["eta", "o", "b", "w", "a_disc", "a_cont", "a_cont_init", "v_init", "v"]
        data = {k: [] for k in keys}

        def stack(d):
            return {k: _torch.stack(v, dim=1).detach().cpu().numpy() if v else None
                    for k, v in d.items()}

        for t in _tqdm(range(1, config["T"] + 1)):
            with _torch.no_grad():
                a_disc, a_cont = agent.choose_action(o, verbose=config["planner"]["verbose"])
            o_next = env.step(a_disc[0], a_cont[0])

            data["eta"].append(eta)
            data["o"].append(o)
            data["b"].append(agent.encoder.b.clone())
            data["w"].append(agent.encoder.w.clone())
            data["a_disc"].append(a_disc)
            data["a_cont"].append(a_cont)
            data["a_cont_init"].append(agent.planner.a_cont_initial.clone())
            data["v_init"].append(agent.planner.returns_initial.clone())
            data["v"].append(agent.planner.returns_optimized.clone())

            o = o_next
            eta = env.state.clone()

            if every and (t % every == 0 or t == config["T"]):
                with open(out_path + ".partial", "wb") as f:
                    _pickle.dump({"data": stack(data), "steps_done": t,
                                  "T_target": config["T"]}, f)

        return stack(data)

    return run_simulation


def build_model_params():
    """Full model, all mechanisms on -- the parameter set from Table 1 of the paper."""
    return {
        # Perception
        "a_sd_model": 3.0,          # sigma_a,0  noise on other vehicle's accel (belief update)
        "Loom_perc": True,          # looming-based perception
        "d_phi_thres": 0.00215,     # looming detection threshold [rad/s]
        "Loom_change_obs": -1,
        "perc_noise_factor": 0.01,
        # Planning
        "noise_pred_fac": 0.2,      # extra noise factor during EFE calculation
        "num_plan": 100,            # M, number of policies evaluated
        "a_sd_plan": 5,             # CEM initial accel std [m/s^2]
        "sample_steering_rate": True,
        "use_pedals": True,         # one-foot pedal constraint (0.2 s hold)
        "H": 30,                    # prediction horizon (x dt=0.2 s -> 6 s)
        "plan_ignore_w": True,
        "plan_smooth_delta": True,
        # Preference function p(o)
        "pref_v_sd": 0.5,           # sigma_v
        "pref_a_sd": 0.1,           # sigma_a
        "pref_w_sd": 0.02,          # sigma_omega
        "lane_cost": -15000,        # g_LL leaving the road
        "lane_change_cost": -1000,  # g_LC lane boundary / opposing lane
        "coll_cost": -10000,        # g_C  collision at 10 m/s relative
        "road_pref": 0,
        "Loom_reward": "V7",
        "weigh_particles": 0.001,
        "full_violation_factor": 0.01,
        "unpunished_heading": 85,
        "collision_cost_adjusted": True,
        "N_norm": 32,               # samples for norm bias
        "H_norm": 20,               # normative projection horizon
        "alpha": 1.0,               # epistemic value on
        # Evidence accumulation
        "EA_mode": "Surprise",
        "EA_init": False,
        "EA_fac": -5.95,            # log10(lambda), drift rate
    }


def build_initial_state():
    return {
        "lane_width": 3.65,
        "d": 1.72,      # vehicle width
        "lf": 2.1,
        "lr": 2.1,
        "a_max": 8,
        "w_max": 1.22,
        "x_ego": 0.0, "y_ego": 0.0, "theta_ego": 0.0, "delta_ego": 0.0, "v_ego": 0.0,
        "x_tar": 0.0, "y_tar": 0.0, "theta_tar": 0.0, "delta_tar": 0.0, "v_tar": 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v0", type=float, default=15.0, help="initial speed of both vehicles [m/s]")
    ap.add_argument("--gap", type=float, default=1.5, help="bumper-to-bumper time gap [s]")
    ap.add_argument("--T", type=int, default=40, help="number of 0.2 s steps to simulate")
    ap.add_argument("--batch", type=int, default=4, help="rollout batch size (parallel repeats)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--checkpoint-every", type=int, default=5,
                    help="save a .partial pickle every N steps (0 disables)")
    args = ap.parse_args()

    model_params = build_model_params()
    initial_state = build_initial_state()

    v_tar = args.v0
    a_tar_brake = 6.0                      # lead vehicle braking deceleration [m/s^2]
    x_tar = v_tar * args.gap + initial_state["lf"] + initial_state["lr"]
    thw_des = x_tar / v_tar

    initial_state["v_ego"] = v_tar
    initial_state["x_tar"] = x_tar
    initial_state["v_tar"] = v_tar

    # the authors calibrate the ego's desired speed offset and its assumption about the
    # other vehicle's minimum acceleration from a prior free-following analysis
    v_diff, a_tar_min = find_parameters(
        v_tar, model_params["EA_fac"], model_params["noise_pred_fac"],
        model_params["H"], model_params["d_phi_thres"], thw_des,
    )
    model_params["v_diff"] = v_diff
    model_params["a_tar_min_intensity"] = -a_tar_min / initial_state["a_max"]
    print(f"calibrated: v_diff={v_diff:.4f} m/s, a_tar_min={a_tar_min:.4f} m/s^2")

    torch.manual_seed(args.seed)
    Config, config = sim_rear_end.set_config(initial_state, model_params, a_tar_brake)
    config["T"] = args.T
    Config["T"] = args.T
    config["rollout_batch_size"] = args.batch

    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    print(f"torch {torch.__version__} on {device}; "
          f"v0={v_tar} m/s, gap={args.gap} s, T={args.T} steps ({args.T * 0.2:.1f} s), "
          f"batch={args.batch}")

    # save partial results as the run proceeds (see make_checkpointing_run_simulation)
    out_pre = args.out or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"results_rear_end_v{int(v_tar)}_gap{args.gap}.pkl",
    )
    if args.checkpoint_every:
        sim_rear_end.run_simulation = make_checkpointing_run_simulation(
            out_pre, every=args.checkpoint_every)

    t0 = time.time()
    data = sim_rear_end.simulate(config, device)
    dt_run = time.time() - t0
    print(f"simulation finished in {dt_run:.1f} s")

    out = out_pre
    with open(out, "wb") as f:
        pickle.dump({"data": data, "Config": Config, "config": config,
                     "runtime_s": dt_run}, f)
    print("saved ->", out)

    # quick summary: ego speed / accel traces
    eta = data["eta"]          # [batch, T, state]
    print("eta shape:", eta.shape)
    np.set_printoptions(precision=2, suppress=True)


if __name__ == "__main__":
    main()
