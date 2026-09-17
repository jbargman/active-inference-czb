"""
Card JJ.2 -- Delta G on the second cut-in study: does a policy-comparison quantity in nats
order the cells the way the participants' shares do, and reach the pre-onset cells with no
gate?

THE PRE-REGISTRATION. Everything in this docstring was written before the run.

The construction is card JJ.1's (`docs/rollout_boundary_design_note.md`, authorized 2026-09-18),
implemented in `src/rollout/` with 27 property tests in `tests/test_rollout.py`. At the response
moment of each stimulus clip the scene is read into a belief, a fan of 200 futures of the
cut-in vehicle is sampled under a constant-velocity Gaussian predictor with a latent lane-change
intention, four ego policies are rolled out against that same fan (common random numbers), each
is scored with the released preference function in its residual-information form, and

    Delta G = G(continue) - min over the menu G(pi)   >= 0,  in nats,

with the axis log Delta G and the zero rule of design note section 1.5. Nothing in the rollouts
is fitted to the responses; the only fitted object is the three-parameter threshold model every
axis in this project is given,

    share who intervene = lapse + (1 - lapse) * Phi((log Delta G - log c) / sigma),

with NO gate term.

CELLS, FOLDS, METRIC -- exactly as the registered gate R.2 script defines them, imported and not
modified: 378 cells (`out/cutin2_cells.csv`, written by `cutin2_field_vs_gap.py`), 288 post-onset
(cp != "CP1") and 90 pre-onset, leave-one-starting-TTC-out folds (`ttc_start`, 6 folds), weighted
RMSE on cell means with weights n. The chance reference is 0.320 and the sampling-noise floor
0.118 (`out/cutin2_field_vs_gap.md`). Comparators, on file: the ungated looming rule 0.1137
(`out/cutin2_gate.md` section 1, model c), the gated looming rule 0.1027 (model k), card G.1's
pre-onset out-of-sample 0.0319 gated and 0.4832 ungated (section 2).

THE PRE-STATED RULES, copied verbatim from design note section 2
-----------------------------------------------------------------
  (a) Post-onset held-out. Delta G's three-parameter threshold model, held out, within 0.01 of
      the gated looming rule's 0.1027. The gated rule is the fair comparator because Delta G
      claims to contain the gate; the ungated 0.1137 is reported beside it.
  (b) Pre-onset out of sample. The full post-onset fit applied to the 90 pre-onset cells scores
      below 0.05, with no gate term. This is the emergence claim, and it is the rule most likely
      to fail.
  (c) The review's ordering constraint. Within the 24 matched-TTC rows, the sign of Delta G's
      rank correlation with the response is positive in at least as many rows as the gap's is
      negative (`docs/r2_pipeline_review.md` section 4 gives the gap's count). If variant A
      fails (c) and variant B passes it, variant B is promoted to primary and the report says
      the released safety counterfactual is what failed, again.
  (d) Sensitivity, never selection. p0, sigma_v,lat, sigma_a and H are fixed at the first values
      of section 1 before the run; every sweep value is reported as a table; none is chosen by
      its score. A reader who prefers a swept value can see what it would have given.
  (e) Monte Carlo. Delta G's standard error across seeds is reported per cell; the verdict is
      invalid if it exceeds 5% of the between-cell spread of log Delta G.

  Verdict, written before the run: ADOPT Delta G as the primary axis if (a), (b) and (e) hold;
  KEEP AS A COMPARATOR if (a) and (e) hold and (b) fails, with the gated looming rule staying
  primary; DROP if (a) fails. Rule (c) decides the variant, not the verdict.

  What counts as a failure of the card rather than of the model: a measured jitter floor that
  makes the lateral-rate likelihood ratio uninformative within the 0.3 s window (report, and
  fall back to the 1.0 s window with the change dated); any cell whose traces end before t0
  (excluded and counted, as PC.1 did).

The gap's count for rule (c) is 24 of 24 (`out/cutin2_lane_gate_diagnostic.md` section 2, the
row "gap"), so rule (c) requires Delta G to be positively ordered in all 24 rows. The row
grouping is the diagnostic's: the 288 post-onset cells grouped by `ttc_true`, rows with at least
6 cells. It is reproduced here rather than imported because the diagnostic holds it inline in
its `main()` and has no function to import; section 0 of the report checks the reproduction by
recovering the gap's own 24 of 24 from it (query JJ2.Q1).

SETTINGS, each with its motivation (design note section 1; none is chosen by its score)
---------------------------------------------------------------------------------------
  freeze t0            the response moment e_t of each video, card G.1's convention
                       (`cutin2_gate.lateral_states`, parsed from the video name by R.VIDEO_RE)
  velocity window      0.3 s, the second study's sample spacing; card G.1's clearance-rate window
  jitter floors        card HS.1's measurements, read out of its docstring by
                       `rollout.belief.verify_floors` and not typed in
  p0 = 0.07            card G.1's fitted gate at the pre-onset cells (0.063-0.070); sweep
                       {0.02, 0.07, 0.20}
  v_lc = 1.2 m/s       G.1's post-onset lateral mean -1.137 m/s; a 3.65 m lane in about 3 s
  sd_lc = 0.4 m/s      the spread of that same column
  sigma_v,lat = 0.33   G.1's fitted gate spread 0.99 m over its 3 s horizon, as a rate; sweep
                       {0.1, 0.33, 0.6}
  sigma_a = 0.5 m/s^2  UNVERIFIED placeholder (query JJ1.Q2); sweep {0.25, 0.5, 1.0}
  H = 6 s, dt = 0.2 s  the released model's planning horizon, 30 steps; sweep H {3, 6}
  n = 200 futures      checked by property test (18) and by rule (e), never assumed
  policies             continue 0, ease off -1, brake -3, brake hard -6 m/s^2; no steering
                       (Jonas's ruling JJ1.Q1)
  preference staging   `cutin_params`: the desired speed is the clip's own ego speed and the
                       continuous lane-entry forms are on, with the CZB shape constant k = 12
  collision            the released box test on dx, dy (the road is straight and both bodies are
                       aligned with it); the polygon test is used only on the left turn, JJ.3
  seeds                the primary run uses seed 0 per cell; rule (e) uses seeds 0-4

Output: replication/czb/out/jj2_rollout_cutin.md and out/jj2_rollout_cutin_cells.csv.
Run:    python replication/czb/jj2_rollout_cutin.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402  registered R.2 script (read only)
import hs1_situational_surprise as HS      # noqa: E402  card HS.1 scene loaders (read only)
from aidriver.preferences import PreferenceParams  # noqa: E402
from comfortzone.cutin import CZB_LANE_ENTRY_SHAPE_K  # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, Scene, belief_at, verify_floors  # noqa: E402
from rollout.boundary import axis, delta_g, mc_standard_error  # noqa: E402
from rollout.efe import g_by_policy, variant_params  # noqa: E402
from rollout.policies import CUTIN_MENU, ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"

# --- comparators and criteria, all on file --------------------------------------------
G1_GATED = 0.1027          # out/cutin2_gate.md section 1, model k
G1_UNGATED = 0.1137        # ibid., model c
G1_CP1_GATED = 0.0319      # ibid., section 2
G1_CP1_UNGATED = 0.4832    # ibid.
CHANCE = 0.320             # out/cutin2_field_vs_gap.md
NOISE_FLOOR = 0.118        # ibid.
MARGIN_A = 0.01            # rule (a)
CP1_CRIT = 0.05            # rule (b)
GAP_ROWS = 24              # rule (c): out/cutin2_lane_gate_diagnostic.md, the "gap" row
MC_FRACTION = 0.05         # rule (e)
ZERO_SHARE_STOP = 0.10     # the brief's stop condition on Delta G = 0 cells
MIN_ROW_CELLS = 6          # the diagnostic's matched-TTC row rule
SEEDS = (0, 1, 2, 3, 4)


# ---------------------------------------------------------------------------------
# 1. scenes and Delta G
# ---------------------------------------------------------------------------------

def trace_key(video: str) -> tuple[str, float, str]:
    m = R.VIDEO_RE.match(video)
    if m is None:
        raise ValueError(f"unparseable video name: {video}")
    return (f"LC_dv{m['dv']}_Tlc{m['tlc']}_TTC{int(m['ttc']):02d}", R._f(m["e"]), f"CP{m['cp']}")


def scene_of(sc: dict, key: str) -> Scene:
    """The two-body scene: the ego and the lane changer, as `study2_scenes` identifies them.

    The traces carry a third vehicle (a lead in the adjacent lane); every card on this study
    ignores it, and so does this one. There is no Heading column, so the headings are zero and
    the direction of travel is read from the positions, as card PC.1 does.
    """
    eg, ta, grid = sc["ego"], sc["tar"], sc["grid"]
    return Scene(t=grid,
                 ego_x=sc["tracks"][eg].x, ego_y=sc["tracks"][eg].y,
                 ego_heading=np.zeros_like(grid), ego_speed=sc["meta"][eg]["speed"],
                 oth_x=sc["tracks"][ta].x, oth_y=sc["tracks"][ta].y,
                 oth_heading=np.zeros_like(grid), oth_speed=sc["meta"][ta]["speed"],
                 ego_len=sc["meta"][eg]["length"], ego_wid=sc["meta"][eg]["width"],
                 oth_len=sc["meta"][ta]["length"], oth_wid=sc["meta"][ta]["width"], name=key)


def cell_delta_g(scene: Scene, e_t: float, p0: float, sd_vlat: float, sd_a: float,
                 horizon_s: float, seed: int, variants=("A",), n: int = N_SAMPLES,
                 one_sided: bool = True) -> dict:
    """Delta G (and the per-policy G) for one cell, for each requested variant."""
    from rollout.belief import update_intention
    b = belief_at(scene, e_t, FLOORS_STUDY2, p_change_prior=p0, with_intention=False)
    b.p_change = update_intention(p0, b.vy_oth, FLOORS_STUDY2.sd_v_lat,
                                  sign=float(np.sign(b.y_rel)) or 1.0, one_sided=one_sided)
    fut = sample_futures(b, horizon_s=horizon_s, dt=DT_S, n=n, sd_vlat=sd_vlat, sd_a=sd_a,
                         seed=seed)
    paths = {k: ego_rollout(b, k, horizon_s=horizon_s, dt=DT_S) for k in CUTIN_MENU}
    base = PreferenceParams(v_desired=b.v_ego, lane_entry_continuous=True,
                            counterfactual_residual_severity=True,
                            lane_entry_shape_k=CZB_LANE_ENTRY_SHAPE_K)
    out = {"p_change": b.p_change, "x_rel": b.x_rel, "y_rel": b.y_rel, "vy_oth": b.vy_oth,
           "v_ego": b.v_ego, "v_oth": b.v_oth}
    for var in variants:
        g = g_by_policy(b, fut, paths, variant_params(base, var))
        out[f"dg_{var}"] = delta_g(g)
        for k, v in g.items():
            out[f"G_{var}_{k}"] = v
    return out


def run_pass(cells: pd.DataFrame, scenes: dict, p0: float = P_CHANGE_PRIOR,
             sd_vlat: float = SD_VLAT, sd_a: float = SD_A, horizon_s: float = HORIZON_S,
             seed: int = 0, variants=("A",), one_sided: bool = True) -> pd.DataFrame:
    """One full pass over the 378 cells at one setting."""
    rows = []
    for v in cells.video:
        key, e_t, cp = trace_key(v)
        row = cell_delta_g(scene_of(scenes[key], key), e_t, p0, sd_vlat, sd_a, horizon_s,
                           seed, variants, one_sided=one_sided)
        row.update({"video": v, "trace": key, "e_t": e_t, "cp": cp})
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------
# 2. the response model (the registered fitter, on log Delta G, no gate)
# ---------------------------------------------------------------------------------

def held_out_scores(cells: pd.DataFrame, x: np.ndarray) -> tuple[float, np.ndarray]:
    """Leave-one-starting-TTC-out held-out wRMSE of the three-parameter threshold model."""
    y, w = cells.p.to_numpy(float), cells.n.to_numpy(float)
    folds = cells.ttc_start.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        th = R.fit(x[tr], y[tr], w[tr], +1.0)
        pred[te] = R.predict(th, x[te], +1.0)
    return R.wrmse(y, pred, w), pred


def full_fit_and_cp1(post: pd.DataFrame, x_post: np.ndarray, cp1: pd.DataFrame,
                     x_cp1: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    th = R.fit(x_post, post.p.to_numpy(float), post.n.to_numpy(float), +1.0)
    pred1 = R.predict(th, x_cp1, +1.0)
    return R.wrmse(cp1.p.to_numpy(float), pred1, cp1.n.to_numpy(float)), pred1, th


def matched_rows(post: pd.DataFrame, col: np.ndarray, direction: float) -> tuple[int, int, float]:
    """The diagnostic's matched-TTC statistic: rows ordered like the data, and the mean rho."""
    d = post.copy()
    d["_x"] = col
    rs = [float(spearmanr(g._x, g.p).statistic) for _, g in d.groupby("ttc_true")
          if len(g) >= MIN_ROW_CELLS]
    agree = sum(1 for r in rs if direction * r > 0)
    return agree, len(rs), float(np.mean(rs))


# ---------------------------------------------------------------------------------
# 3. the run
# ---------------------------------------------------------------------------------

def main() -> None:
    t_start = time.time()
    cells_all = pd.read_csv(OUT / "cutin2_cells.csv")
    missing = verify_floors()

    L = ["# Card JJ.2 -- Delta G, the rollout axis, on the second cut-in study", "",
         "Generated by `replication/czb/jj2_rollout_cutin.py`; construction, settings and the"
         " rules (a) to (e) pre-stated in its docstring and in"
         " `docs/rollout_boundary_design_note.md` section 2, before the run. Do not edit by"
         " hand.", "",
         "## 0 Implementation checks", ""]

    # --- cells ---------------------------------------------------------------------
    post_all = cells_all[cells_all.cp != "CP1"]
    cp1_all = cells_all[cells_all.cp == "CP1"]
    counts_ok = (len(cells_all) == 378 and len(post_all) == 288 and len(cp1_all) == 90)
    L += [f"| check | value | expected |", "|---|---|---|",
          f"| cells / post-onset / pre-onset | {len(cells_all)} / {len(post_all)} / "
          f"{len(cp1_all)} | 378 / 288 / 90 |",
          f"| starting-TTC folds | {len(np.unique(cells_all.ttc_start))} | 6 |"]
    if not counts_ok:
        L += ["", "**The registered cell construction did not reproduce; the run stops here.**"]
        (OUT / "jj2_rollout_cutin.md").write_text("\n".join(L), encoding="utf-8")
        print("\n".join(L))
        return

    # --- the jitter floors ----------------------------------------------------------
    L.append(f"| card HS.1's jitter-floor citations still present | "
             f"{'all four' if not missing else 'MISSING: ' + '; '.join(missing)} | all four |")

    # --- scenes and their coverage of the freeze ------------------------------------
    scenes = HS.study2_scenes(cells_all)
    short = []
    for v in cells_all.video:
        key, e_t, _ = trace_key(v)
        g = scenes[key]["grid"]
        if e_t > g[-1] + 1e-9 or e_t < g[0] + FLOORS_STUDY2.window_s - 1e-9:
            short.append(v)
    L.append(f"| cells whose trace ends before the freeze (excluded) | {len(short)} | 0 |")
    if short:
        cells_all = cells_all[~cells_all.video.isin(short)].reset_index(drop=True)

    # --- the matched-TTC row grouping, checked against the gap's own count -----------
    post_chk = cells_all[cells_all.cp != "CP1"].reset_index(drop=True)
    gap_agree, n_rows, gap_rho = matched_rows(post_chk, post_chk.distance.to_numpy(float), -1.0)
    L += [f"| matched-TTC rows (post-onset, >= {MIN_ROW_CELLS} cells) | {n_rows} | {GAP_ROWS} |",
          f"| the gap's rows ordered like the data (rule (c)'s reference) | {gap_agree} of "
          f"{n_rows} (mean rho {gap_rho:+.2f}) | {GAP_ROWS} of {GAP_ROWS} |", ""]
    rows_ok = (n_rows == GAP_ROWS and gap_agree == GAP_ROWS)
    L.append("Row grouping reproduces `out/cutin2_lane_gate_diagnostic.md`: "
             + ("**yes**." if rows_ok else "**NO** -- rule (c) is reported but not decided"
                                           " (query JJ2.Q1).") )
    L.append("")

    # --- the primary pass -----------------------------------------------------------
    print("primary pass...", flush=True)
    df = run_pass(cells_all, scenes, variants=("A", "B"))
    df = df.merge(cells_all[["video", "p", "n", "ttc_start", "ttc_true", "distance",
                             "dv_kph", "lcd"]], on="video", how="left")
    df.to_csv(OUT / "jj2_rollout_cutin_cells.csv", index=False)

    results = {}
    for var in ("A", "B"):
        dg = df[f"dg_{var}"].to_numpy(float)
        ax = axis(dg)
        df[f"x_{var}"] = ax.values
        post = df[df.cp != "CP1"].reset_index(drop=True)
        cp1 = df[df.cp == "CP1"].reset_index(drop=True)
        r_post, _ = held_out_scores(post, post[f"x_{var}"].to_numpy(float))
        r_cp1, pred1, th = full_fit_and_cp1(post, post[f"x_{var}"].to_numpy(float),
                                            cp1, cp1[f"x_{var}"].to_numpy(float))
        agree, nr, rho = matched_rows(post, post[f"dg_{var}"].to_numpy(float), +1.0)
        results[var] = {"axis": ax, "r_post": r_post, "r_cp1": r_cp1, "theta": th,
                        "agree": agree, "n_rows": nr, "rho": rho,
                        "a_ok": r_post <= G1_GATED + MARGIN_A, "b_ok": r_cp1 < CP1_CRIT,
                        "c_ok": agree >= gap_agree,
                        "zeros": ax.n_zero, "pred_cp1": pred1}

    zero_share = results["A"]["zeros"] / len(df)
    L += ["## 1 Delta G at the primary settings", "",
          f"p0 = {P_CHANGE_PRIOR}, sigma_v,lat = {SD_VLAT} m/s, sigma_a = {SD_A} m/s^2, "
          f"H = {HORIZON_S:.0f} s, dt = {DT_S} s, {N_SAMPLES} futures, seed 0.", "",
          "| quantity | variant A (released) | variant B (no p_safe) |", "|---|---|---|"]
    for lab, key, fmt in (("Delta G median, nats", "med", "{:.0f}"),
                          ("Delta G range, nats", "rng", "{}"),
                          ("cells with Delta G = 0", "zeros", "{}")):
        vals = []
        for var in ("A", "B"):
            dg = df[f"dg_{var}"].to_numpy(float)
            vals.append({"med": f"{np.median(dg):.0f}",
                         "rng": f"{dg.min():.0f} to {dg.max():.0f}",
                         "zeros": f"{results[var]['zeros']}"}[key])
        L.append(f"| {lab} | {vals[0]} | {vals[1]} |")
    L += [f"| P(changing) at the pre-onset cells | "
          f"{df[df.cp == 'CP1'].p_change.min():.3f} to {df[df.cp == 'CP1'].p_change.max():.3f} | "
          "same (the belief does not depend on the variant) |",
          f"| P(changing) post-onset | {df[df.cp != 'CP1'].p_change.min():.3f} to "
          f"{df[df.cp != 'CP1'].p_change.max():.3f} | same |", "",
          f"The zero rule of design note section 1.5 was "
          + ("applied" if results["A"]["axis"].zero_rule_applied else "NOT applied (no cell has"
             " Delta G = 0)") + ". The brief's stop condition is more than 10% of cells at "
          f"Delta G = 0: {zero_share:.1%} -> "
          + ("**STOP**." if zero_share > ZERO_SHARE_STOP else "proceed."), ""]

    L += ["### The rules", "",
          "| rule | criterion | variant A | variant B |", "|---|---|---|---|",
          f"| (a) post-onset held-out | <= {G1_GATED:.4f} + {MARGIN_A:.2f} = "
          f"{G1_GATED + MARGIN_A:.4f} | {results['A']['r_post']:.4f} "
          f"{'PASS' if results['A']['a_ok'] else 'FAIL'} | {results['B']['r_post']:.4f} "
          f"{'PASS' if results['B']['a_ok'] else 'FAIL'} |",
          f"| (b) pre-onset out of sample | < {CP1_CRIT:.2f} | {results['A']['r_cp1']:.4f} "
          f"{'PASS' if results['A']['b_ok'] else 'FAIL'} | {results['B']['r_cp1']:.4f} "
          f"{'PASS' if results['B']['b_ok'] else 'FAIL'} |",
          f"| (c) matched-TTC rows ordered like the data | >= {gap_agree} of {n_rows} | "
          f"{results['A']['agree']} of {results['A']['n_rows']} (mean rho "
          f"{results['A']['rho']:+.2f}) {'PASS' if results['A']['c_ok'] else 'FAIL'} | "
          f"{results['B']['agree']} of {results['B']['n_rows']} (mean rho "
          f"{results['B']['rho']:+.2f}) {'PASS' if results['B']['c_ok'] else 'FAIL'} |", "",
          f"Comparators on file: the gated looming rule {G1_GATED:.4f} and the ungated"
          f" {G1_UNGATED:.4f} post-onset; card G.1's pre-onset out-of-sample"
          f" {G1_CP1_GATED:.4f} gated and {G1_CP1_UNGATED:.4f} ungated; chance {CHANCE:.3f};"
          f" the sampling-noise floor {NOISE_FLOOR:.3f}.", ""]

    # --- 1b where the ordering comes from (reported, no decision attached) -----------
    post = df[df.cp != "CP1"].reset_index(drop=True)
    L += ["### Where Delta G's ordering comes from (reported, no decision attached)", "",
          "Spearman rank correlations on the 288 post-onset cells. The response is ordered by"
          " the gap (rho(P, distance) = "
          f"{spearmanr(post.p, post.distance).statistic:+.3f}), so an axis that claims to be"
          " criticality must fall with distance.", "",
          "| quantity | rho with the share P | rho with distance | rho with dv | rho with TTC |",
          "|---|---|---|---|---|"]
    diag_cols = [("Delta G, variant A", "dg_A"), ("Delta G, variant B", "dg_B"),
                 ("G(continue), A", "G_A_continue"), ("G(brake), A", "G_A_brake"),
                 ("G(brake hard), A", "G_A_brake_hard"), ("G(ease off), A", "G_A_ease_off")]
    post["_minG_A"] = post[[f"G_A_{k}" for k in CUTIN_MENU]].min(axis=1)
    diag_cols.append(("min over the menu, A", "_minG_A"))
    for lab, col in diag_cols:
        v = post[col].to_numpy(float)
        L.append(f"| {lab} | {spearmanr(v, post.p).statistic:+.3f} | "
                 f"{spearmanr(v, post.distance).statistic:+.3f} | "
                 f"{spearmanr(v, post.dv_kph).statistic:+.3f} | "
                 f"{spearmanr(v, post.ttc_true).statistic:+.3f} |")
    # what a level on G(continue) alone would give -- a diagnostic, not the card's axis
    r_cont, _ = held_out_scores(post, np.log(post.G_A_continue.to_numpy(float)))
    cp1d = df[df.cp == "CP1"].reset_index(drop=True)
    r_cont_cp1, _, _ = full_fit_and_cp1(post, np.log(post.G_A_continue.to_numpy(float)),
                                        cp1d, np.log(cp1d.G_A_continue.to_numpy(float)))
    L += ["", "Two readings follow from this table and are stated as readings, not decisions.",
          "", "1. **Delta G is a value-of-action quantity, and it collapses where no action"
          " helps.** It is large where braking would avert a collision that continuing would"
          " cause, and small both where nothing is going to happen and where the gap is already"
          " too small for any policy in the menu to avoid contact: there the best alternative's"
          " G rises with G(continue) and the difference closes. The menu's own cost is the"
          " other half of the mechanism -- braking at -3 m/s^2 costs a fixed"
          f" {post.G_A_brake.min():.0f} nats of control effort over the horizon whatever the"
          " scene is doing (sigma_a = 0.1 m/s^2 in the released preference), so the minimum is"
          " floored.",
          "", "2. **The released magnitude still grades with speed rather than with the gap.**"
          " That is the R.2 pipeline review's finding (`docs/r2_pipeline_review.md` section 3)"
          " reappearing inside the rollouts, and it is what rule (c) counts: the axis is"
          " anti-ordered within matched-TTC rows, where the design varies the gap and the speed"
          " together.",
          "", f"A level on log G(continue) alone -- the rollout's own criticality without the"
          f" policy comparison, which is NOT this card's axis -- scores {r_cont:.4f} held out"
          f" post-onset and {r_cont_cp1:.4f} at the pre-onset cells, against the gated looming"
          f" rule's {G1_GATED:.4f} and {G1_CP1_GATED:.4f}. It is reported so that the policy"
          " comparison and the preference function are not blamed for one another.", ""]

    # --- write the main report before the slow parts (handover rule 10) --------------
    (OUT / "jj2_rollout_cutin.md").write_text("\n".join(L), encoding="utf-8")
    print(f"main report written at {time.time() - t_start:.0f} s", flush=True)

    # --- rule (d): the sweeps -------------------------------------------------------
    print("sweeps...", flush=True)
    sweeps = []
    grid = ([("p0", v) for v in (0.02, 0.07, 0.20)]
            + [("sigma_v,lat", v) for v in (0.1, 0.33, 0.6)]
            + [("sigma_a", v) for v in (0.25, 0.5, 1.0)]
            + [("H", v) for v in (3.0, 6.0)])
    for name, value in grid:
        kw = dict(p0=P_CHANGE_PRIOR, sd_vlat=SD_VLAT, sd_a=SD_A, horizon_s=HORIZON_S)
        kw[{"p0": "p0", "sigma_v,lat": "sd_vlat", "sigma_a": "sd_a", "H": "horizon_s"}[name]] = value
        primary = value == {"p0": P_CHANGE_PRIOR, "sigma_v,lat": SD_VLAT, "sigma_a": SD_A,
                            "H": HORIZON_S}[name]
        d = df if primary else run_pass(cells_all, scenes, variants=("A",), **kw)
        if primary:
            d = df.copy()
        else:
            d = d.merge(cells_all[["video", "p", "n", "ttc_start", "ttc_true"]], on="video",
                        how="left")
        ax = axis(d["dg_A"].to_numpy(float))
        d["x_A"] = ax.values
        po = d[d.cp != "CP1"].reset_index(drop=True)
        c1 = d[d.cp == "CP1"].reset_index(drop=True)
        r_post, _ = held_out_scores(po, po.x_A.to_numpy(float))
        r_cp1, _, _ = full_fit_and_cp1(po, po.x_A.to_numpy(float), c1, c1.x_A.to_numpy(float))
        ag, nr, _ = matched_rows(po, po.dg_A.to_numpy(float), +1.0)
        sweeps.append({"constant": name, "value": value, "primary": primary,
                       "post": r_post, "cp1": r_cp1, "rows": f"{ag} of {nr}",
                       "zeros": ax.n_zero})
        print(f"  {name} = {value}: post {r_post:.4f}, CP1 {r_cp1:.4f}", flush=True)

    L += ["## 2 Rule (d) -- sensitivity, never selection", "",
          "Variant A. Each constant is swept alone, the other three held at their motivated"
          " first values. The primary row is marked; no value here is chosen by its score.", "",
          "| constant | value | post-onset held-out | pre-onset out of sample | matched-TTC rows"
          " | cells at Delta G = 0 |", "|---|---|---|---|---|---|"]
    for s in sweeps:
        mark = " **(primary)**" if s["primary"] else ""
        L.append(f"| {s['constant']} | {s['value']}{mark} | {s['post']:.4f} | {s['cp1']:.4f} | "
                 f"{s['rows']} | {s['zeros']} |")
    L.append("")

    # --- rule (e): the Monte Carlo standard error -----------------------------------
    print("seed sweep...", flush=True)
    dg_seeds = {0: df["dg_A"].to_numpy(float)}
    for s in SEEDS[1:]:
        d = run_pass(cells_all, scenes, seed=s, variants=("A",))
        dg_seeds[s] = d["dg_A"].to_numpy(float)
        print(f"  seed {s} done", flush=True)
    stack = np.column_stack([dg_seeds[s] for s in SEEDS])
    se_dg = np.array([mc_standard_error(stack[i]) for i in range(stack.shape[0])])
    se_log = se_dg / np.maximum(stack.mean(axis=1), 1e-12)     # se on the log axis
    med_se = float(np.median(se_log))
    spread = float(np.std(results["A"]["axis"].values, ddof=1))
    e_ok = med_se <= MC_FRACTION * spread
    L += ["## 3 Rule (e) -- the Monte Carlo standard error", "",
          f"Delta G across {len(SEEDS)} seeds per cell, variant A at the primary settings. The"
          " standard error is compared on the axis the model is fitted on, so it is divided by"
          " the cell's own Delta G.", "",
          "| quantity | value |", "|---|---|",
          f"| median per-cell SE of log Delta G | {med_se:.4f} |",
          f"| between-cell spread of log Delta G (sd) | {spread:.4f} |",
          f"| {MC_FRACTION:.0%} of that spread | {MC_FRACTION * spread:.4f} |",
          f"| rule (e) | {'PASS' if e_ok else 'FAIL -- the verdict is invalid'} |",
          f"| worst cell's SE of log Delta G | {np.nanmax(se_log):.4f} |", ""]

    # --- the verdict ---------------------------------------------------------------
    var_primary = "A"
    promoted = (not results["A"]["c_ok"]) and results["B"]["c_ok"]
    if promoted:
        var_primary = "B"
    r = results[var_primary]
    if not r["a_ok"]:
        verdict = "**DROP.** Rule (a) fails: Delta G does not reach the gated looming rule."
    elif not e_ok:
        verdict = "**The verdict is invalid**: rule (e) fails, so no reading is taken."
    elif r["b_ok"]:
        verdict = ("**ADOPT** Delta G as the primary axis: rules (a), (b) and (e) hold.")
    else:
        verdict = ("**KEEP AS A COMPARATOR.** Rules (a) and (e) hold and (b) fails, so the"
                   " gated looming rule stays primary.")
    L += ["## 4 The verdict, in the design note's own words", "",
          f"Deciding variant: **{var_primary}**"
          + (" -- variant A failed rule (c) and variant B passed it, so variant B is promoted"
             " to primary and the released safety counterfactual is what failed, again."
             if promoted else " (the released six terms, Jonas's ruling JJ.Q2)."), "",
          verdict, "",
          f"Rules at the deciding variant: (a) {r['r_post']:.4f} against"
          f" {G1_GATED + MARGIN_A:.4f}; (b) {r['r_cp1']:.4f} against {CP1_CRIT:.2f};"
          f" (c) {r['agree']} of {r['n_rows']} against {gap_agree}; (e)"
          f" {med_se:.4f} against {MC_FRACTION * spread:.4f}.", "",
          f"Run time {time.time() - t_start:.0f} s.", ""]

    (OUT / "jj2_rollout_cutin.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[-14:]))


if __name__ == "__main__":
    main()
