"""
Card GZ.2 -- why does the released model brake during steady car following? (query GZ1.Q2)

PRE-STATED before the run (2026-09-16).

THE OBSERVATION (card GZ.1, `replication/causation/gz1/thw1.5/`). Steady following at 15 m/s,
1.5 s headway, lead at constant speed, released configuration with gaze choice off: every
released-noise condition starts braking at step 16 (3.2 s), and 3 of 4 repeats brake to a
standstill, also with the authors' own scripted lead. With perception noise x100 (perc_noise_factor
1.0) the car follows steadily at 14-15 m/s. The cause was left open.

WHAT IS RECORDED, per step and repeat, from the planner itself (`mpc_discrete.py`, unmodified):
  * the per-term rewards of the plan being followed (`returns_initial`) and, when a full re-plan
    happens, of the plan that replaces it (`returns_optimized`) -- each summed over the 30-step
    horizon and averaged over particles, in the order v, a, omega, y, theta, gaze,
    collision-and-safety, epistemic;
  * the accumulated evidence after the step (`evidence`), and whether a full re-plan happened
    (the executed plan differs from the reference plan);
  * the executed acceleration, the ego speed and the gap;
  * the belief about the lead: weighted mean and spread of its acceleration over the particles.

THE CONDITIONS (T = 25 steps, 5 s; batch 4; everything else as GZ.1's control G0c):
  B0  released configuration (perc_noise_factor 0.01)          -- brakes in GZ.1
  B1  perception noise x100 (perc_noise_factor 1.0)             -- does not brake in GZ.1
  B2  released, epistemic value off (alpha = 0)                 -- an ablation, because perception
      noise changes the epistemic term most, and the epistemic term is excluded from the evidence
      but included when a plan is chosen.

QUESTIONS AND PRE-STATED READINGS:
  Q1  Does braking begin at the first evidence-triggered full re-plan? READING: if in B0 the first
      step with an executed acceleration below -1 m/s^2 is the step of, or the step after, the first
      full re-plan in each repeat, the braking is a re-plan decision, not a drift of the patched plan.
  Q2  What accumulates the evidence? The evidence increment is 10^EA_fac times minus the sum of the
      pragmatic terms of the followed plan. READING: the term with the largest share of that sum over
      the steps before the first re-plan is what drives the re-plan.
  Q3  What makes the new plan brake? READING: at the first re-plan, the per-term change from the
      followed plan to the chosen plan shows which terms the planner traded: the terms that improve
      most are what braking buys, the terms that worsen are what it costs.
  Q4  Why does B1 not brake? READING: if B1 never re-plans within 25 steps, the difference is in the
      evidence (Q2's term, compared between B0 and B1); if it re-plans without braking, the
      difference is in the choice (Q3's terms, compared).
  Q5  B2: if B2 does not brake, the epistemic term is needed for the braking choice; if it brakes like
      B0, the braking is pragmatic.

PART B, pre-stated 2026-09-16 after part A answered Q1-Q5. Part A left one thing open: why 100x
perception noise cuts the evidence rate 25-fold (0.0029 against 0.0764 per step) when the belief about
the lead's acceleration is about as spread in both. Two facts from the code narrow it: with looming
perception on, the lead's position, speed and acceleration are observed only through the looming angle
and its derivatives, and the planner scores imagined futures on observations SAMPLED with perception
noise (`BeliefReward(sample_mean=False)`). Three short runs (T = 14 steps, enough for B0 to reach its
re-plan), batch 4:
  C1  released, but the collision-and-safety term reduced to the inverse-tau preference alone
      (`Loom_reward = 'V4'`: same preference width, no collision or safety check)
  C2  released, but only the three looming-angle noise scales x100
  C3  released, but only the seven state-channel noise scales x100
READINGS (evidence per step before any re-plan, against B0's 0.0764 and B1's 0.0029):
  C1 near 0 -> the collision and safety checks produce the shortfall; C1 near B0 -> the inverse-tau
  preference does. C2 near B1 -> noise on the looming channels is what suppresses it; C3 near B1 -> noise
  on the state channels is. Both or neither -> reported as found.

Nothing is fitted and no default is changed. The authors' files are not edited: the scenario reuses
card GZ.1's lead-replay setup, which GZ.1's adapter check G0x showed behaves like the authors' own
scripted lead in this regime.

Output: replication/causation/gz2/gz2_following_braking.md, gz2/<cond>.pkl, gz2/log_<cond>.txt
Run:    python replication/causation/gz2_following_braking.py [--only B0]
"""
from __future__ import annotations

import argparse
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "replication"))

import tier2_rear_end as T2                                                 # noqa: E402
from run_rear_end_single import build_model_params, build_initial_state   # noqa: E402
from src.utils.simulation import find_parameters                          # noqa: E402

OUT = HERE / "gz2"
DT = 0.2
V = 15.0
THW = 1.5
GAP = THW * V
T_STEPS = 25
BATCH = 4
TERMS = ["v", "a", "omega", "y", "theta", "gaze", "collision_safety", "epistemic"]
I_A_TAR = 2 + 5 + 5          # belief state: gaze (2), ego (5), target (5), target controls (a, w)
CONDITIONS = {
    "B0": {"perc_noise_factor": 0.01},
    "B1": {"perc_noise_factor": 1.0},
    "B2": {"perc_noise_factor": 0.01, "alpha": 0.0},
    # part B
    "C1": {"perc_noise_factor": 0.01, "Loom_reward": "V4"},
    "C2": {"perc_noise_factor": 0.01, "_decoder_x100": ["LA_sd", "d_LA_sd", "dd_LA_sd"]},
    "C3": {"perc_noise_factor": 0.01, "_decoder_x100": ["x_sd", "y_sd", "theta_sd", "delta_sd",
                                                        "v_sd", "a_sd", "w_sd"]},
}
PART_B_STEPS = 14


def run_condition(tag: str, overrides: dict) -> dict:
    out_path = OUT / f"{tag}.pkl"
    if out_path.exists():
        with open(out_path, "rb") as f:
            return pickle.load(f)

    overrides = dict(overrides)
    scale_keys = overrides.pop("_decoder_x100", [])
    t_steps = PART_B_STEPS if tag.startswith("C") else T_STEPS
    model_params = build_model_params()
    model_params.update(overrides)
    initial_state = build_initial_state()
    x_tar = GAP + initial_state["lf"] + initial_state["lr"]
    initial_state.update(v_ego=V, v_tar=V, x_tar=x_tar)
    v_diff, a_tar_min = find_parameters(V, model_params["EA_fac"], model_params["noise_pred_fac"],
                                        model_params["H"], model_params["d_phi_thres"], x_tar / V)
    model_params["v_diff"] = v_diff
    model_params["a_tar_min_intensity"] = -a_tar_min / initial_state["a_max"]

    torch.manual_seed(0)
    sim = T2.sim_rear_end
    Config, config = sim.set_config(initial_state, model_params, a_tar_brake=6.0)
    Config["v_ego_des"] = V + v_diff
    config["reward"]["v_mu"] = Config["v_ego_des"]
    config["T"] = Config["T"] = t_steps
    config["rollout_batch_size"] = BATCH
    config["init_state"]["t_brake"] = 1e6
    config["init_state"]["j_brake"] = 0.0
    for k in scale_keys:
        config["decoder"][k] = config["decoder"][k] * 100.0

    a_lead = np.zeros(T_STEPS + 1)
    saved_dyn, saved_run = sim.Dynamics_true, sim.run_simulation
    rec = {k: [] for k in ("ref", "opt", "evidence", "replanned", "acc", "speed", "gap",
                           "a_tar_mean", "a_tar_sd")}

    def replay_factory(**kw):
        return T2.DynamicsLeadReplay(a_lead, **kw)

    def run_simulation(cfg, agent, env, eta, b, w):
        agent.reset(b, w)
        o = env.reset(eta)
        env.dynamics.reset_clock()
        eta = env.state.clone()
        pl = agent.planner
        for t in range(1, cfg["T"] + 1):
            t0 = time.time()
            with torch.no_grad():
                a_disc, a_cont = agent.choose_action(o, verbose=False)
            ref = pl.returns_initial.detach().cpu().numpy().reshape(BATCH, -1)
            opt = pl.returns_optimized.detach().cpu().numpy().reshape(BATCH, -1)
            replanned = ~np.all(np.isclose(a_cont.detach().cpu().numpy(),
                                           pl.a_cont_initial.detach().cpu().numpy()), axis=(0, 2))
            ev = pl.evidence.detach().cpu().numpy().reshape(-1) if torch.is_tensor(pl.evidence) \
                else np.full(BATCH, float(pl.evidence))
            bw = (agent.w / agent.w.sum(-1, keepdim=True)).detach()
            a_t = agent.b[..., I_A_TAR].detach()
            m = (a_t * bw).sum(-1)
            sd = torch.sqrt(((a_t - m.unsqueeze(-1)) ** 2 * bw).sum(-1))
            o = env.step(a_disc[0], a_cont[0])
            rec["ref"].append(ref)
            rec["opt"].append(opt)
            rec["evidence"].append(ev)
            rec["replanned"].append(replanned)
            rec["acc"].append(a_cont[0, :, 0].detach().cpu().numpy())
            rec["speed"].append(eta[:, 4].detach().cpu().numpy())
            rec["gap"].append((eta[:, 5] - eta[:, 0]).detach().cpu().numpy()
                              - initial_state["lf"] - initial_state["lr"])
            rec["a_tar_mean"].append(m.cpu().numpy())
            rec["a_tar_sd"].append(sd.cpu().numpy())
            eta = env.state.clone()
            print(f"{tag} step {t}/{cfg['T']} {time.time() - t0:.1f} s  replanned "
                  f"{int(replanned.sum())}/{BATCH}  acc {np.round(rec['acc'][-1], 2)}  "
                  f"evidence {np.round(ev, 2)}", flush=True)
        return {k: np.stack(v, axis=1) for k, v in rec.items()}   # [batch, T, ...]

    sim.Dynamics_true, sim.run_simulation = replay_factory, run_simulation
    try:
        t_start = time.time()
        data = sim.simulate(config, torch.device("cpu"))
        runtime = time.time() - t_start
    finally:
        sim.Dynamics_true, sim.run_simulation = saved_dyn, saved_run

    if scale_keys:
        overrides["decoder_x100"] = scale_keys
    result = {"tag": tag, "overrides": overrides, "runtime_s": runtime, "data": data,
              "evidence_fac": 10 ** model_params["EA_fac"], "v_des": V + v_diff,
              "a_tar_min": float(a_tar_min)}
    with open(out_path, "wb") as f:
        pickle.dump(result, f)
    return result


def first(idx_bool):
    hit = np.flatnonzero(idx_bool)
    return int(hit[0]) if len(hit) else None


def report(results: dict) -> str:
    L = ["# Card GZ.2 -- why the released model brakes during steady car following", "",
         "Generated by `replication/causation/gz2_following_braking.py`; conditions, questions and "
         "readings pre-stated in its docstring. Do not edit by hand.", "",
         f"Steady following at {V} m/s, {THW} s headway, lead at constant speed, {T_STEPS} steps "
         f"(part B: {PART_B_STEPS}), batch {BATCH}. Step k is time (k - 1) x {DT} s; the first step is k = 1.", ""]
    for tag, r in results.items():
        d = r["data"]
        L += [f"## {tag}: {r['overrides']}", "",
              f"Desired speed {r['v_des']:.2f} m/s; assumed worst-case lead braking "
              f"{r['a_tar_min']:.2f} m/s^2; evidence factor {r['evidence_fac']:.3g}.", "",
              "| repeat | first full re-plan (step) | first braking < -1 m/s^2 (step) | min speed [m/s] | "
              "min gap [m] | re-plans |", "|---|---|---|---|---|---|"]
        firsts = []
        for b in range(d["acc"].shape[0]):
            fr = first(d["replanned"][b])
            fb = first(d["acc"][b] < -1.0)
            firsts.append((fr, fb))
            L.append(f"| {b} | {fr + 1 if fr is not None else 'none'} | "
                     f"{fb + 1 if fb is not None else 'none'} | {d['speed'][b].min():.2f} | "
                     f"{d['gap'][b].min():.2f} | {int(d['replanned'][b].sum())} |")
        L.append("")

        # Q2: what accumulates the evidence, up to (not including) the first re-plan
        ef = r["evidence_fac"]
        shares = np.zeros(len(TERMS) - 1)
        n_steps = 0
        for b, (fr, _) in enumerate(firsts):
            stop = fr if fr is not None else d["ref"].shape[1]
            if stop <= 0:
                continue
            pragm = -d["ref"][b, :stop, :7]          # positive = shortfall contributed
            shares += pragm.sum(0)
            n_steps += stop
        tot = shares.sum()
        L += ["**Q2, what accumulates the evidence** (followed plan, pragmatic terms, summed over the "
              "steps before each repeat's first re-plan; share of the total shortfall and the mean "
              "evidence increment per step it contributes):", "",
              "| term | share | evidence per step |", "|---|---|---|"]
        for i, name in enumerate(TERMS[:7]):
            share = shares[i] / tot if tot > 0 else float("nan")
            L.append(f"| {name} | {share:.3f} | {ef * shares[i] / max(n_steps, 1):.4f} |")
        L += ["", f"Total evidence per step before the first re-plan: "
              f"{ef * tot / max(n_steps, 1):.4f} (the re-plan fires at 1).", ""]

        # Q3: what the new plan traded, at each repeat's first re-plan
        L += ["**Q3, what the first re-plan traded** (chosen minus followed plan, per term; positive = "
              "the chosen plan is better on that term):", "",
              "| repeat | step | executed accel | " + " | ".join(TERMS) + " |",
              "|---|---|---|" + "---|" * len(TERMS)]
        for b, (fr, _) in enumerate(firsts):
            if fr is None:
                continue
            diff = d["opt"][b, fr] - d["ref"][b, fr]
            L.append(f"| {b} | {fr + 1} | {d['acc'][b, fr]:+.2f} | "
                     + " | ".join(f"{x:+.0f}" for x in diff) + " |")
        L.append("")

        # belief about the lead
        L += ["**The belief about the lead's acceleration** (weighted over particles, mean over repeats):", "",
              "| step | 1 | 5 | 10 | 15 | 20 | 25 |", "|---|---|---|---|---|---|---|"]
        cols = [0, 4, 9, 14, 19, 24]
        cols = [c for c in cols if c < d["a_tar_mean"].shape[1]]
        L.append("| mean [m/s^2] | " + " | ".join(f"{d['a_tar_mean'][:, c].mean():+.3f}" for c in cols) + " |")
        L.append("| spread [m/s^2] | " + " | ".join(f"{d['a_tar_sd'][:, c].mean():.3f}" for c in cols) + " |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(CONDITIONS), default=None)
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    for tag, ov in CONDITIONS.items():
        if args.only and tag != args.only:
            continue
        p = OUT / f"{tag}.pkl"
        if args.report:
            if p.exists():
                results[tag] = pickle.load(open(p, "rb"))
            continue
        print(f"=== {tag}: {ov}", flush=True)
        results[tag] = run_condition(tag, ov)
    if not args.only or args.report:
        text = report(results)
        (OUT / "gz2_following_braking.md").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
