"""
Card JJ.5 -- the released model's OWN looming preference as the pragmatic value: does the gated
looming rule fall out of the model's terms?

THE PRE-REGISTRATION. Everything in this docstring was written before the run, on 2026-09-22.

WHERE THE CARD COMES FROM
-------------------------
Jonas, 2026-09-22, after the review: *"You proposed that I give up active inference as CZB. I am
not willing to do that yet."* The review's own finding points at the test: everything built from a
BRAKING requirement is anti-ordered within matched TTC, because at the same TTC a smaller gap is a
slower closing speed, while participants respond to proximity and looming. The preference prior
in active inference is ours to choose -- and the released preference already contains a looming
term: the one-sided tau^-1 Gaussian (preferred TTC 5 s or more, `tau_inv_mu` 0.2, `tau_inv_sd`
0.125; SI Eq. 48). Card RE.2 folded it into the collision factor, where the post-contact cost
swamps it; it has never been scored on its own inside the rollout.

WHAT IS COMPUTED (`src/rollout/looming_pref.py`, 11 property checks in `tests/test_looming_pref.py`)
--------------------------------------------------------------------------------------------------
Card JJ.2's construction -- the same 378 cells, the belief at the same freeze with the same
intention update, the same fan constants, the same folds and metric -- with the pragmatic value
restricted to the looming term, read before contact, averaged over the fan and summed over the 6 s
horizon of the `continue` policy:

    eps_tau(continue) = sum_t max(0, -mean_fan log p_tau(o_t))        [nats]

Three readings of WHEN the term applies, none fitted:
  **in_path** (primary)  only in futures and at steps where the other's body overlaps the ego's
                         lane laterally (|dy| <= 1.15 ego width, the released collision box's
                         lateral extent). A vehicle is a lead when it is in my path. In the fan the
                         "changing" futures enter the path and the "keeping" ones do not, so
                         E_fan[eps_tau] has the STRUCTURE of card G.1's gated looming rule --
                         P(in path) x looming excess -- with the gate supplied by the intention
                         belief instead of a fitted term. That is the hypothesis.
  **none**               the released term as written: any vehicle ahead, in any lane. Expected to
                         fail, because a lane-keeping vehicle in the next lane is charged as the
                         ego passes it (the property tests show 1e4+ nats for a certain keeper).
  **continuous**         the project's lane-entry weight (k = 12), card JJ.2's staging.

Fan: the CORRECTED fan (`keep_body_in_lane=True`, card S1.6), because under in_path the flaw in
JJ.1's fan (a keeper's centre clipped inside the collision box) would put lane-keeping futures in
the path; JJ.1's fan is reported beside it. n = 200, seed 0; seeds 1 and 2 for rule (e).

Beside the axis, the PRICE form of card S1.6: min over admissible policies (alpha = 0, the
0.25 m/s^2 brake menu) of eps_tau(pi), reported for the primary reading only.

THE RULES -- card JJ.2's, verbatim, on the primary reading, sign +1 (more looming cost, more
response, which is what the term claims); the sign -1 score is reported and credits nothing
  (a) post-onset held out within 0.01 of the gated looming rule's 0.1027 (the fair comparator,
      because the quantity claims to contain the gate); the ungated 0.1137 reported beside it;
  (b) the full post-onset fit applied to the 90 pre-onset cells scores below 0.05, no gate term;
  (c) positive within-row ordering in at least 12 of the 24 matched-TTC rows (card RE.2's
      criterion; JJ.2's 24 of 24 was the gap's own count and no quantity has reached it);
  (e) the post-onset score is within 0.01 across seeds 0, 1, 2.
  VERDICT: **ADOPT** if (a), (b), (e): the gated looming rule has been derived from the model's own
      terms. **AXIS** if (a) and (e) hold and (b) fails: the looming preference is the axis, the
      intention belief is not the gate. **GATE** if (b) and (e) hold and (a) fails: the belief is the
      gate, the released tau^-1 shape is not the axis (then the shape -- mu, sd, one-sidedness --
      is the thing to fit, and it is a driver parameter). **NOT CREDITED** otherwise.

PREDICTIONS, written before the run
-----------------------------------
Seen: the property tests on synthetic scenes (a certain change at 25 m costs 1131 nats under
continue, 0 under brake; at the prior the cost scales with the share in the path). No JJ.5
quantity on any cell.
  1. in_path post-onset: 0.11 to 0.14. Post-onset the intention posterior is 1.0 in every cell (the
     review, checks section 2), so eps_tau is looming excess over the fan's futures with no gate
     dilution, and card EL.1b's looming rate at the freeze scores 0.113. The horizon average will
     blur it: it integrates looming over the next 6 s rather than reading it now.
  2. in_path pre-onset: 0.03 to 0.10. Pre-onset the posterior is 0.07, so the cost is scaled by
     about 14 and sits far below the fitted level; but the released term is one-sided at TTC 5 s,
     so pre-onset cells at TTC 2 to 4 s carry a large excess in the 7% of futures that change, and
     whether 7% of a large number stays under the level is the open question. (b) is the rule most
     likely to fail, as it was in JJ.2.
  3. Rule (c): 12 or more of 24. Within a row, a smaller gap at the same TTC gives a LARGER tau^-1
     excess only through the horizon (the gap closes sooner); at the freeze tau^-1 is the same in
     every cell of a row. So the ordering comes from the horizon average, and I expect it weaker
     than the looming rate's own.
  4. none: fails (a) and (b), a constant.  continuous: within 0.02 of in_path.
  5. The price form: worse than the axis post-onset (the price is a braking requirement again)
     and not better pre-onset.

Output: replication/czb/out/jj5_looming_preference.md, out/jj5_looming_preference_cells.csv
Run:    python replication/czb/jj5_looming_preference.py
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import cutin2_field_vs_gap as R            # noqa: E402
import hs1_situational_surprise as HS      # noqa: E402
import jj2_rollout_cutin as J2             # noqa: E402  card JJ.2 (read only)
from aidriver.preferences import PreferenceParams  # noqa: E402
from rollout.admissible import brake_menu, collides, delayed_rollout  # noqa: E402
from rollout.belief import FLOORS_STUDY2, P_CHANGE_PRIOR, belief_at, update_intention  # noqa: E402
from rollout.boundary import axis  # noqa: E402
from rollout.looming_pref import eps_tau, share_in_path  # noqa: E402
from rollout.policies import ego_rollout  # noqa: E402
from rollout.predictor import DT_S, HORIZON_S, N_SAMPLES, SD_A, SD_VLAT, sample_futures  # noqa: E402

OUT = HERE / "out"
G1_GATED, G1_UNGATED, G1_CP1 = 0.1027, 0.1137, 0.0319
GAP_RULE, CHANCE, NOISE_FLOOR = 0.1522, 0.320, 0.118
MARGIN_A, CP1_CRIT, ROWS_CRIT, MC_TOL = 0.01, 0.05, 12, 0.01
GATES = ("in_path", "none", "continuous")
SEEDS = (0, 1, 2)


def beliefs(cells):
    scenes = HS.study2_scenes(cells)
    out = {}
    for v in cells.video:
        key, e_t, cp = J2.trace_key(v)
        b = belief_at(J2.scene_of(scenes[key], key), e_t, FLOORS_STUDY2,
                      p_change_prior=P_CHANGE_PRIOR, with_intention=False)
        b.p_change = update_intention(P_CHANGE_PRIOR, b.vy_oth, FLOORS_STUDY2.sd_v_lat,
                                      sign=float(np.sign(b.y_rel)) or 1.0)
        out[v] = (b, cp)
    return out


def run(bel: dict, corrected: bool, seed: int, price: bool) -> pd.DataFrame:
    rows = []
    for v, (b, cp) in bel.items():
        fut = sample_futures(b, horizon_s=HORIZON_S, dt=DT_S, n=N_SAMPLES, sd_vlat=SD_VLAT,
                             sd_a=SD_A, seed=seed, keep_body_in_lane=corrected)
        p = PreferenceParams(v_desired=b.v_ego)
        pc = PreferenceParams(v_desired=b.v_ego, lane_entry_continuous=True,
                              lane_entry_shape_k=J2.CZB_LANE_ENTRY_SHAPE_K)
        ego = ego_rollout(b, "continue", HORIZON_S, DT_S)
        row = {"video": v, "cp": cp, "p_change": b.p_change,
               "share_in_path": share_in_path(b, ego, fut, p),
               "eps_in_path": eps_tau(b, ego, fut, p, "in_path"),
               "eps_none": eps_tau(b, ego, fut, p, "none"),
               "eps_continuous": eps_tau(b, ego, fut, pc, "continuous")}
        if price:
            menu = brake_menu()
            paths = {k: delayed_rollout(b, a, 0.0, HORIZON_S, DT_S) for k, a in menu.items()}
            ok = [k for k, path in paths.items() if not collides(path, fut, p).any()]
            if ok:
                best = min(ok, key=lambda k: eps_tau(b, paths[k], fut, p, "in_path"))
                row["price"] = eps_tau(b, paths[best], fut, p, "in_path")
                row["a_star"] = -menu[best]
            else:
                row["price"], row["a_star"] = np.nan, np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def score(df: pd.DataFrame, cells: pd.DataFrame, col: str) -> dict:
    d = df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance"]], on="video")
    d = d.dropna(subset=[col])
    raw = d[col].to_numpy(float)
    if np.all(raw <= 0):
        return None
    d["x"] = axis(raw).values
    post = d[d.cp != "CP1"].reset_index(drop=True)
    cp1 = d[d.cp == "CP1"].reset_index(drop=True)
    r_post, _ = J2.held_out_scores(post, post.x.to_numpy(float))
    r_cp1, _, th = J2.full_fit_and_cp1(post, post.x.to_numpy(float), cp1, cp1.x.to_numpy(float))
    y, w, f = post.p.to_numpy(float), post.n.to_numpy(float), post.ttc_start.to_numpy(float)
    x = post.x.to_numpy(float)
    pred = np.full_like(y, np.nan)
    for k in np.unique(f):
        t2 = R.fit(x[f != k], y[f != k], w[f != k], -1.0)
        pred[f == k] = R.predict(t2, x[f == k], -1.0)
    agree, nrows, _ = J2.matched_rows(post, post[col].to_numpy(float), +1.0)
    return {"post": r_post, "neg": R.wrmse(y, pred, w), "cp1": r_cp1, "rows": agree,
            "n_rows": nrows, "rho_p": float(spearmanr(post[col], post.p).statistic),
            "rho_gap": float(spearmanr(post[col], post.distance).statistic),
            "zeros_post": int((post[col] <= 0).sum()), "zeros_cp1": int((cp1[col] <= 0).sum()),
            "level": float(th[1]), "sigma": float(np.exp(th[2]))}


def fmt(s):
    if s is None:
        return "| every cell at zero | - | - | - | - | - |"
    return (f"| {s['post']:.4f} | {s['neg']:.4f} | {s['cp1']:.4f} | {s['rows']} of {s['n_rows']} |"
            f" {s['rho_p']:+.3f} | {s['rho_gap']:+.3f} |")


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time()
    cells = pd.read_csv(OUT / "cutin2_cells.csv")
    bel = beliefs(cells)
    prim_df = run(bel, True, 0, price=True)
    print("primary pass done", flush=True)
    jj1_df = run(bel, False, 0, price=False)
    print("JJ.1 fan pass done", flush=True)
    seeds = {0: prim_df}
    for s in SEEDS[1:]:
        seeds[s] = run(bel, True, s, price=False)
        print(f"seed {s} done", flush=True)
    prim_df.merge(cells[["video", "p", "n", "ttc_start", "ttc_true", "distance", "dv_kph"]],
                  on="video").to_csv(OUT / "jj5_looming_preference_cells.csv", index=False)

    res = {g: score(prim_df, cells, f"eps_{g}") for g in GATES}
    res_jj1 = {g: score(jj1_df, cells, f"eps_{g}") for g in GATES}
    price = score(prim_df, cells, "price")
    mc = {s: score(df, cells, "eps_in_path")["post"] for s, df in seeds.items()}
    prim = res["in_path"]
    rule_a = prim is not None and prim["post"] <= G1_GATED + MARGIN_A
    rule_b = prim is not None and prim["cp1"] < CP1_CRIT
    rule_c = prim is not None and prim["rows"] >= ROWS_CRIT
    rule_e = max(mc.values()) - min(mc.values()) <= MC_TOL
    if rule_a and rule_b and rule_e:
        verdict = "ADOPT"
    elif rule_a and rule_e:
        verdict = "AXIS"
    elif rule_b and rule_e:
        verdict = "GATE"
    else:
        verdict = "NOT CREDITED"
    is_cp1 = (prim_df.cp == "CP1").to_numpy()

    L = ["# Card JJ.5 -- the released model's own looming preference as the pragmatic value", "",
         "Generated by `replication/czb/jj5_looming_preference.py`; the readings, the rules and the"
         " predictions were pre-stated in its docstring before the run. Do not edit by hand.", "",
         "The released preference contains a one-sided tau^-1 Gaussian (preferred TTC 5 s or"
         " more), its looming term. Read alone, before contact, only where the other is in the"
         " ego's path, and averaged over card JJ.1's fan, its expected residual has the structure"
         " of card G.1's gated looming rule: P(in path) x looming excess, with the gate supplied"
         " by the intention belief. Nothing is fitted but the response model's three parameters."
         " Construction: `src/rollout/looming_pref.py`.", "",
         "## 0 What the fan supplies", "",
         f"Share of futures in which the other is in the ego's path (median): pre-onset"
         f" **{np.median(prim_df.share_in_path[is_cp1]):.3f}**, post-onset"
         f" **{np.median(prim_df.share_in_path[~is_cp1]):.3f}** (intention posterior medians"
         f" {np.median(prim_df.p_change[is_cp1]):.3f} and {np.median(prim_df.p_change[~is_cp1]):.3f})."
         f" Median eps_tau(continue), in_path: pre-onset {np.median(prim_df.eps_in_path[is_cp1]):.1f}"
         f" nats, post-onset {np.median(prim_df.eps_in_path[~is_cp1]):.1f} nats.", "",
         "## 1 The three readings, corrected fan, seed 0", "",
         "| reading | post-onset held out, sign +1 | sign -1 | pre-onset, no gate term |"
         " matched-TTC rows | rho(share) | rho(gap) |", "|---|---|---|---|---|---|---|"]
    for g in GATES:
        L.append(f"| **{g}**{' (primary)' if g == 'in_path' else ''} " + fmt(res[g]))
    L.append("| the price form (min over admissible policies of eps_tau), in_path " + fmt(price))
    L += ["", f"Comparators: gated looming rule {G1_GATED} (pre-onset {G1_CP1}), ungated"
          f" {G1_UNGATED}, gap {GAP_RULE}, chance {CHANCE}, noise floor {NOISE_FLOOR}.",
          (f" Zero-cost cells, in_path: {prim['zeros_post']} of 288 post-onset,"
           f" {prim['zeros_cp1']} of 90 pre-onset." if prim else ""), "",
          "## 2 Card JJ.1's fan as built", "",
          "| reading | post-onset held out, sign +1 | sign -1 | pre-onset | matched-TTC rows |"
          " rho(share) | rho(gap) |", "|---|---|---|---|---|---|---|"]
    for g in GATES:
        L.append(f"| {g} " + fmt(res_jj1[g]))
    L += ["", "## 3 Rule (e)", "", "| seed | post-onset held out, in_path |", "|---|---|"]
    for s, v in mc.items():
        L.append(f"| {s} | {v:.4f} |")
    L += ["", f"Range {max(mc.values()) - min(mc.values()):.4f} against {MC_TOL}:"
          f" rule (e) {'holds' if rule_e else 'FAILS'}.", "",
          "## 4 The verdict on the pre-stated rules", "",
          f"**{verdict}.** Rule (a): {prim['post']:.4f} against {G1_GATED + MARGIN_A:.4f}"
          f" ({'holds' if rule_a else 'fails'}; the ungated 0.1137). Rule (b): {prim['cp1']:.4f}"
          f" against {CP1_CRIT} ({'holds' if rule_b else 'fails'}). Rule (c): {prim['rows']} of"
          f" {prim['n_rows']} ({'holds' if rule_c else 'fails'}). Rule (e):"
          f" {'holds' if rule_e else 'fails'}.", "",
          {"ADOPT": "**The gated looming rule has been derived from the released model's own"
                    " terms**: the looming preference is the axis and the intention belief is"
                    " the gate, with nothing fitted but the response model.",
           "AXIS": "The looming preference is an axis on this design; the intention belief does"
                   " not supply the gate at the pre-onset cells.",
           "GATE": "The intention belief supplies the gate; the released tau^-1 shape (mu 0.2,"
                   " sd 0.125, one-sided) is not the axis. The shape is the thing to fit, and it"
                   " is a driver parameter.",
           "NOT CREDITED": "Neither the axis nor the gate falls out of the released looming term"
                           " on this design as read here."}[verdict], "",
          f"Run time {time.time() - t0:.0f} s.", ""]
    (OUT / "jj5_looming_preference.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
