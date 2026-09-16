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

PART C, pre-stated 2026-09-16 (query GZ2.Q2, authorized by Jonas) before its runs. Part B found that
x100 on the seven state-channel scales (C3) suppresses the re-plan and x100 on the three looming scales
(C2) does not. Which state channels carry it? What the seven scales act on, read from
`external/aica/src/common/decoder.py` (`compute_obs_dist`) and `simulation_benign.py`: they are the
generative model's ASSUMED observation noise, used in the particle filter's likelihood and in the
planner's sampled observations; the environment's true observation noise is these values x0.001
(`Decoder_true`), so x100 does not make the world noisier, it makes the model expect noise.
  * x_sd, v_sd  -- ego and target position and speed in the planner's observations (state layout);
                   the ego's position and speed in the belief update (looming layout, where the target
                   is seen through the looming angle and its derivatives)
  * a_sd        -- the target's acceleration in the planner's observations only
  * y_sd, theta_sd, delta_sd -- the target's lateral position, heading and steering angle in the
                   planner's observations (the ego's are clamped to 1e-6 there); both vehicles' in the
                   belief update
  * w_sd        -- the target's steering rate, in both
Two runs, T = 14, batch 4, everything else as B0:
  D1  released, but x_sd, v_sd, a_sd x100            (the longitudinal channels)
  D2  released, but y_sd, theta_sd, delta_sd, w_sd x100 (the lateral and heading channels)
READINGS (evidence per step before any re-plan, against B0's 0.0764 and C3's 0.0023): whichever of
D1/D2 lands near C3 carries the effect. Both near B0 -> the channels act only together; both near C3 ->
either group suffices; either way reported as found. The ROUTE is then checked in part D.

PART D, pre-stated 2026-09-16 after part C's readings were fixed and before its run. The scales reach
the accumulated evidence by two routes: (i) the belief update (the particle filter's likelihood, so a
wider or narrower belief about the two cars), and (ii) the planner's scoring of imagined futures, which
draws an observation per particle from the assumed noise (`BeliefReward(sample_mean=False)`,
`src/common/belief_reward.py`) and evaluates the collision-and-safety term on that draw. One run:
  D3  released, but the group found in part C x100 in the PLANNER'S decoder only -- a copy of the
      decoder with the scaled noise is installed in `agent.planner.reward.ig_estimator.decoder`
      after the agent is built; the encoder keeps the released decoder, so the belief update is
      untouched. Same T = 14, batch 4.
READING: D3 near the part-C suppressor -> route (ii), the sampled observations in planning, carries it;
D3 near B0 -> route (i), the belief update, carries it; in between -> both, reported with the two numbers.
The recorded belief spread about the lead's acceleration is reported alongside as the check that the
encoder was indeed untouched in D3.

PART E, pre-stated 2026-09-16 after parts C and D were read (D2 suppresses, D3 does not: the route is
the belief update) and before its runs. The collision and safety checks in `reward.py` apply only where
the imagined lead is in the ego's path (`test_looming_viability(o, perc=False)`: |y_ego - y_tar| <
1.15 d) and both cars are heading the same way (`following`, the sign of cos(theta)); elsewhere they
are switched off. Hypothesis: with the assumed observation noise on the lateral and heading channels
x100, the particle filter can no longer pin the two cars' lateral state, the belief spreads laterally
under the model's own process noise, and the imagined lead leaves the path before the safety check
can fail. Two runs, T = 14, batch 4, recording per step the weighted belief spread of y and theta for
both cars and the weighted share of particles in which the lead is in the path and following:
  E0  released (B0's settings), recording added
  E2  D2's settings (the four lateral and heading scales x100), recording added
READING: the in-path-and-following share near 1 in E0 and clearly lower in E2, with the lateral
spreads larger in E2 -> the mechanism is the loosened lateral belief exempting the imagined lead from
the checks; share near 1 in both -> the route is in the belief update but not through this exemption,
reported as unexplained.

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
    # part C (GZ2.Q2): C3's seven channels split into longitudinal and lateral-heading groups
    "D1": {"perc_noise_factor": 0.01, "_decoder_x100": ["x_sd", "v_sd", "a_sd"]},
    "D2": {"perc_noise_factor": 0.01, "_decoder_x100": ["y_sd", "theta_sd", "delta_sd", "w_sd"]},
    # part D (the route): the part-C group scaled in the planner's decoder only. Part C's result
    # (2026-09-16): D2 suppresses (0.0025 per step, no re-plan), D1 does not (re-plans at step 13-14
    # like B0), so the group is the lateral and heading channels.
    "D3": {"perc_noise_factor": 0.01, "_planner_decoder_x100": ["y_sd", "theta_sd", "delta_sd", "w_sd"]},
    # part E (the mechanism): B0's and D2's settings with the belief's lateral spread recorded
    "E0": {"perc_noise_factor": 0.01},
    "E2": {"perc_noise_factor": 0.01, "_decoder_x100": ["y_sd", "theta_sd", "delta_sd", "w_sd"]},
}
PART_B_STEPS = 14            # parts B to E (tags C*, D*, E*) run 14 steps; part A (B*) runs T_STEPS
# belief columns: gaze (2), ego x y theta delta v (2..6), target x y theta delta v (7..11), a_tar, w_tar
I_Y_EGO, I_TH_EGO, I_Y_TAR, I_TH_TAR = 3, 4, 8, 9
# index of each noise scale in the decoder's three sd vectors (decoder.py: o_state_sd, o_ctrl_sd, o_loom_sd)
DECODER_SD_INDEX = {"x_sd": [("o_state_sd", 0)], "y_sd": [("o_state_sd", 1), ("o_loom_sd", 3)],
                    "theta_sd": [("o_state_sd", 2), ("o_loom_sd", 4)],
                    "delta_sd": [("o_state_sd", 3), ("o_loom_sd", 5)], "v_sd": [("o_state_sd", 4)],
                    "a_sd": [("o_ctrl_sd", 0)], "w_sd": [("o_ctrl_sd", 1), ("o_loom_sd", 6)],
                    "LA_sd": [("o_loom_sd", 0)], "d_LA_sd": [("o_loom_sd", 1)], "dd_LA_sd": [("o_loom_sd", 2)]}


def scaled_decoder_copy(decoder, keys, factor=100.0):
    """A deep copy of the authors' Decoder with the named noise scales multiplied, for part D."""
    import copy
    dec = copy.deepcopy(decoder)
    for k in keys:
        for vec, i in DECODER_SD_INDEX[k]:
            v = getattr(dec, vec).clone()
            v[i] = v[i] * factor
            setattr(dec, vec, v)
    return dec


def run_condition(tag: str, overrides: dict) -> dict:
    out_path = OUT / f"{tag}.pkl"
    if out_path.exists():
        with open(out_path, "rb") as f:
            return pickle.load(f)

    overrides = dict(overrides)
    scale_keys = overrides.pop("_decoder_x100", [])
    planner_keys = overrides.pop("_planner_decoder_x100", [])
    if "_planner_decoder_x100" in CONDITIONS[tag] and not planner_keys:
        raise SystemExit(f"{tag}: the planner-only group is set after part C has run (docstring, part D)")
    t_steps = PART_B_STEPS if tag[0] in "CDE" else T_STEPS
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
                           "a_tar_mean", "a_tar_sd",
                           # part E: the belief's lateral spread and the share of particles in which
                           # the lead is in the ego's path and heading the same way (reward.py's
                           # looming_viable and following, evaluated on the belief itself)
                           "y_ego_sd", "th_ego_sd", "y_tar_sd", "th_tar_sd", "in_path_share")}

    def wsd(x, bw):
        m = (x * bw).sum(-1)
        return torch.sqrt(((x - m.unsqueeze(-1)) ** 2 * bw).sum(-1))

    def replay_factory(**kw):
        return T2.DynamicsLeadReplay(a_lead, **kw)

    def run_simulation(cfg, agent, env, eta, b, w):
        agent.reset(b, w)
        o = env.reset(eta)
        env.dynamics.reset_clock()
        eta = env.state.clone()
        pl = agent.planner
        if planner_keys:
            # part D: the planner scores imagined futures on observations drawn from THIS decoder;
            # the encoder (agent.encoder) keeps the shared released one, so the belief update is untouched
            assert pl.reward.ig_estimator.decoder is agent.encoder.decoder
            pl.reward.ig_estimator.decoder = scaled_decoder_copy(agent.encoder.decoder, planner_keys)
            assert pl.reward.ig_estimator.decoder is not agent.encoder.decoder
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
            b = agent.b.detach()
            d_width = agent.encoder.decoder.d
            in_path = (torch.abs(b[..., I_Y_EGO] - b[..., I_Y_TAR]) < 1.15 * d_width) \
                & (torch.sign(torch.cos(b[..., I_TH_EGO])) * torch.sign(torch.cos(b[..., I_TH_TAR])) >= 0)
            rec["y_ego_sd"].append(wsd(b[..., I_Y_EGO], bw).cpu().numpy())
            rec["th_ego_sd"].append(wsd(b[..., I_TH_EGO], bw).cpu().numpy())
            rec["y_tar_sd"].append(wsd(b[..., I_Y_TAR], bw).cpu().numpy())
            rec["th_tar_sd"].append(wsd(b[..., I_TH_TAR], bw).cpu().numpy())
            rec["in_path_share"].append((in_path.to(bw.dtype) * bw).sum(-1).cpu().numpy())
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
    if planner_keys:
        overrides["planner_decoder_x100"] = planner_keys
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
        if "in_path_share" in d:
            # part E: the belief's lateral spread and the in-path share (mean over repeats)
            cols = [0, 2, 4, 6, 9, 13]
            cols = [c for c in cols if c < d["in_path_share"].shape[1]]
            L += ["**The belief's lateral state** (weighted over particles, mean over repeats; the last row "
                  "is the share of particles in which the lead is in the ego's path and both head the same "
                  "way, which is where `reward.py` applies the collision and safety checks):", "",
                  "| step | " + " | ".join(str(c + 1) for c in cols) + " |", "|---|" + "---|" * len(cols)]
            for key, name in (("y_ego_sd", "ego y spread [m]"), ("th_ego_sd", "ego heading spread [rad]"),
                              ("y_tar_sd", "lead y spread [m]"), ("th_tar_sd", "lead heading spread [rad]"),
                              ("in_path_share", "in-path-and-following share")):
                L.append(f"| {name} | " + " | ".join(f"{d[key][:, c].mean():.3f}" for c in cols) + " |")
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
