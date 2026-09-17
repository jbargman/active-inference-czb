"""
Card EX.2 -- the level fits with a shared exposure term, reported at first exposure.

PRE-STATED before the run (2026-09-17). Nothing below was changed after the first run unless a dated
note says so.

WHY. Card EX.1 (`out/ex1_exposure_split.md`) found that repeated exposure does not teach a pre-onset
anticipation but does shift the criterion, at the population level only (per-driver reliability 0.35):
on the second cut-in study post-onset responding rises +0.027 on a second showing; on the study-1 left
turn responding falls about 9 points over four showings, mostly across the session boundary, and the
boundary distance shrinks from 87 m to 77 m. The level fits the deliverable rests on -- stage 1
(`fit_stage1_looming.py` -> `out/stage1_looming.md`, study-1 cut-in) and the per-driver levels of card
TR.1 (`driver_levels.py`, study-1 cut-in and the 50 km/h video left turn) -- pool all four showings.
Jonas (2026-09-17) asked for the route proposed in the session: first measure the effect on study 1's
cut-in, which EX.1 did not cover, then keep all data, add ONE shared exposure term on the level, and
report the level at the first-exposure setting next to the pooled one. Nothing here edits a
pre-registered script or overwrites its outputs; this card imports them.

DATA. Study 1, Random design, the 43 drivers who completed all sessions. The cut-in: 3 096 trials, 3
stimuli x 6 timepoints x 4 showings, two showings per session (`fit_stage1_looming.build_trials`,
joined row for row to the joint file for `Session_Nr` and `Trial_Nr`; the join is asserted). The left
turn at 50 km/h: 1 548 trials, 9 PET levels x 4 showings (exactly as `driver_levels.py` selects them).

STEP 1 -- IS THE EFFECT THERE ON STUDY 1'S CUT-IN? (no model)
  Showing index per driver x stimulus x timepoint, ordered by session then `Trial_Nr` (dictionary
  gotcha 4). P(intervene) by showing, pre-onset (C1) and post-onset (C2-C6) separately; the session-2
  minus session-1 difference, pooled and per onset group, with a 2 000-resample cluster bootstrap by
  driver (seed 20260917), 95% percentile intervals.
  RULE N: the effect is NEGLIGIBLE if the pooled session difference's interval lies entirely inside
  [-0.03, +0.03]. Motivation: 0.03 is the size of the smallest exposure effect already shown to exist
  in this paradigm (EX.1, second cut-in study, post-onset +0.027). An interval that straddles the bound
  is "not shown negligible".

STEP 2 -- THE REFITS REPRODUCE THEIR CARDS (gate)
  Without the exposure term, the estimator must reproduce stage 1's L-gated row (mu -3.4520, sigma_pop
  0.8677, sigma_resp 0.5742) and TT.1's video 50 km/h fit (PET_50 2.18 s, sigma_pop 1.36 s, sigma_resp
  0.86 s) to 0.01, the tolerance TR.1 used. Otherwise the run stops and reports.

STEP 3 -- THE EXTENDED ESTIMATOR RECOVERS A KNOWN SHIFT (gate)
  The model: P(intervene) = b_i + (1 - b_i) * gate * Phi((x - c_i - beta * e) / sigma_resp), with
  c_i = mu + sigma_pop * z_i the level at e = 0, e the exposure of the trial, and beta shared by all
  drivers. Everything else is `fit_stage1_looming.fit_hier_lapse_gated` unchanged: the same 48 x 48
  Gauss-Hermite product grid, priors, optimizer and Laplace covariance, with one added prior
  beta ~ Normal(0, 1) on the covariate's scale. Motivation for the prior: weak; a session shift of one
  unit is a factor of 2.7 on the looming rate or a full second of PET, far above EX.1's measured
  shifts, so the prior does not constrain an effect of that size.
  Recovery: data simulated on the left-turn design (the real drivers, trials, x and sessions) from the
  step-2 pooled left-turn parameters with beta = +0.30 (seed 20260917) and fitted with e = session.
  Rule: |beta_hat - 0.30| < 2 SE and |mu_hat - mu_true| < 2 SE, with finite SEs. Otherwise the run stops.

STEP 4 -- THE EXPOSURE TERM ON THE REAL DATA
  Primary exposure variable: e = session (0 for session 1, 1 for session 2). Motivation: EX.1 placed the
  left-turn change at the session boundary, with within-session changes not reliable (B1, B3), and in
  study 1 showing and session are confounded by design (EX1.Q3). Sensitivity, no verdict: e = showing
  index 0-3 (level reported at e = 0, the first showing).
  Reported per scenario: pooled fit (step 2) and session-term fit side by side -- mu, sigma_pop,
  sigma_resp, lapse, beta with its Laplace 95% interval, the difference in negative log posterior; the
  population percentiles 5, 20, 50, 80, 95 at the first-exposure setting (e = 0) and pooled; for the
  cut-in the median level's implied trigger onset (`fit_stage1_looming.onset_time_theta`) averaged over
  the three stimuli, at first exposure against pooled, in seconds, beside stage 1's 0.244 s per
  5-point percentile step; for the left turn PET_50 in seconds.
  RULE A (which setting is the deliverable's primary):
    Left turn: the first-exposure setting is primary if beta's 95% interval excludes 0; otherwise pooled.
    Cut-in: the first-exposure setting is primary if step 1 did NOT find the effect negligible AND beta's
      95% interval excludes 0; otherwise pooled stays primary.
  If a Laplace SE is not finite the term is reported without a verdict and pooled stays primary.

STEP 5 -- PER-DRIVER LEVELS AT FIRST EXPOSURE (card TR.1 again)
  Each driver's posterior-mean level with the session term (TR.1's quadrature, on the session-1 scale),
  both scenarios; the oriented Spearman between the two with TR.1's driver bootstrap, against TR.1's
  +0.647 (bootstrap +0.407 to +0.798). No verdict: the question is whether the trait survives the
  correction, reported as the two numbers.

Output: replication/czb/out/ex2_first_exposure_levels.md, out/ex2_driver_levels_first_exposure.csv
Run:    python replication/czb/ex2_first_exposure_levels.py   (background; several hierarchical fits)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import fit_stage1_looming as F                         # noqa: E402  card G1.Q1 (read only)
import driver_levels as D                              # noqa: E402  card TR.1 (read only)
import ltapod_testtrack as TT                          # noqa: E402  card TT.1 (read only)
from fit_recovery import NORMAL, _gh_nodes             # noqa: E402
from fit_stage1 import NODE_CHUNK, N_GH_2D             # noqa: E402
from comfortzone.czb_data import load_joint            # noqa: E402

OUT = HERE / "out"
SEED = 20260917
N_BOOT = 2000
NEGLIGIBLE = 0.03
REPRO_TOL = 0.01
BETA_TRUE = 0.30
STEP_S_PER_5PCT = 0.244        # out/stage1_looming.md section 5, for comparison only
TR1_RHO = (0.647, 0.407, 0.798)


# ---------------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------------

def cutin_trials():
    r = F.build_trials()
    j = load_joint()
    jr = j[(j.design == "Random") & (j.scenario == "cutin_car")].reset_index(drop=True)
    r = r.reset_index(drop=True)
    assert len(jr) == len(r), (len(jr), len(r))
    assert (jr.criticality_label.to_numpy() == r.criticality.to_numpy()).all()
    assert (jr.timepoint.to_numpy() == r.timepoint.to_numpy()).all()
    assert (jr.intervene.to_numpy(float) == r.intervene.to_numpy(float)).all()
    r["session"] = jr.Session_Nr.to_numpy(int)
    r["trial_nr"] = jr.Trial_Nr.to_numpy(int)
    r["driver"] = r.participant
    order = r.sort_values(["driver", "session", "trial_nr"]).index
    show = r.loc[order].groupby(["driver", "criticality", "timepoint"]).cumcount()
    r.loc[order, "show"] = show.to_numpy()
    r["show"] = r.show.astype(int)
    return r


def ltap_trials():
    j = load_joint()
    v = j[(j.design == "Random") & (j.scenario == "ltap") & (j.ltap_speed == 50)].copy()
    v["pet"] = v.criticality_label.str.replace("PET", "").astype(float)
    v["driver"] = v.Exp_Subject_Id
    v["session"] = v.Session_Nr.astype(int)
    v = v.reset_index(drop=True)
    order = v.sort_values(["driver", "session", "Trial_Nr"]).index
    v.loc[order, "show"] = v.loc[order].groupby(["driver", "criticality_label"]).cumcount().to_numpy()
    v["show"] = v.show.astype(int)
    return v


# ---------------------------------------------------------------------------------
# the estimator with a shared exposure shift on the level
# ---------------------------------------------------------------------------------

def _marginal_e(phi, xt, gt, yt, et, pidt, n_drivers, z1, z2, lw):
    mu, sigma_pop = phi[0], torch.exp(phi[1])
    sigma_resp, b_loc, sigma_b, beta = torch.exp(phi[2]), phi[3], torch.exp(phi[4]), phi[5]
    xe = xt - beta * et
    acc = torch.full((n_drivers, len(z1)), -np.inf)
    for s in range(0, len(z1), NODE_CHUNK):
        e = min(s + NODE_CHUNK, len(z1))
        c = mu + sigma_pop * z1[s:e]
        b = torch.sigmoid(b_loc + sigma_b * z2[s:e])
        p = b + (1.0 - b) * gt[:, None] * NORMAL.cdf((xe[:, None] - c[None, :]) / sigma_resp)
        p = p.clamp(1e-12, 1.0 - 1e-12)
        ll = yt[:, None] * torch.log(p) + (1.0 - yt[:, None]) * torch.log1p(-p)
        acc[:, s:e] = torch.zeros(n_drivers, e - s).index_add(0, pidt, ll)
    return torch.logsumexp(acc + lw[None, :], dim=1)


def _nlp_e(phi, xt, gt, yt, et, pidt, n_drivers, pr, z1, z2, lw):
    sigma_pop, sigma_b = torch.exp(phi[1]), torch.exp(phi[4])
    ll = _marginal_e(phi, xt, gt, yt, et, pidt, n_drivers, z1, z2, lw).sum()
    lp = -0.5 * ((phi[0] - pr.mu_loc) / pr.mu_scale) ** 2
    lp = lp - 0.5 * (sigma_pop / pr.sigma_pop_scale) ** 2 + phi[1]
    lp = lp - 0.5 * ((phi[2] - pr.sigma_resp_loc) / pr.sigma_resp_scale) ** 2
    lp = lp - 0.5 * (torch.sigmoid(phi[3]) / 0.3) ** 2
    lp = lp - 0.5 * (sigma_b / 1.0) ** 2 + phi[4]
    lp = lp - 0.5 * (phi[5] / 1.0) ** 2                       # beta ~ Normal(0, 1)
    return -(ll + lp)


def fit_exposure(x, g, y, e, pid, pr) -> dict:
    xt, gt, yt, et = (torch.as_tensor(np.asarray(a, float).copy()) for a in (x, g, y, e))
    pidt = torch.as_tensor(pid, dtype=torch.long)
    n_drivers = int(pid.max() + 1)
    zz, ww = _gh_nodes(N_GH_2D)
    z1 = torch.as_tensor(np.repeat(zz, N_GH_2D))
    z2 = torch.as_tensor(np.tile(zz, N_GH_2D))
    lw = torch.as_tensor(np.log(np.outer(ww, ww).ravel()))
    init = np.array([pr.mu_loc, np.log(0.4), pr.sigma_resp_loc, np.log(0.09 / 0.91), np.log(0.5), 0.0])
    phi = torch.tensor(init, requires_grad=True)
    opt = torch.optim.LBFGS([phi], max_iter=250, tolerance_grad=1e-9, tolerance_change=1e-13,
                            history_size=40, line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        loss = _nlp_e(phi, xt, gt, yt, et, pidt, n_drivers, pr, z1, z2, lw)
        loss.backward()
        return loss

    opt.step(closure)
    with torch.no_grad():
        val = float(_nlp_e(phi, xt, gt, yt, et, pidt, n_drivers, pr, z1, z2, lw))
    H = torch.autograd.functional.hessian(
        lambda t: _nlp_e(t, xt, gt, yt, et, pidt, n_drivers, pr, z1, z2, lw), phi)
    try:
        cov = torch.linalg.inv(H).numpy()
        se = np.sqrt(np.clip(np.diag(cov), 0.0, None))
        ok = bool(np.all(np.isfinite(se)))
    except Exception:
        cov, se, ok = np.full((6, 6), np.nan), np.full(6, np.nan), False
    t = phi.detach().numpy()
    return {"mu": t[0], "se_mu": se[0], "sigma_pop": np.exp(t[1]), "sigma_resp": np.exp(t[2]),
            "b": float(torch.sigmoid(phi[3]).detach()), "sigma_b": np.exp(t[4]),
            "beta": t[5], "se_beta": se[5], "neg_log_post": val, "se_ok": ok, "cov": cov, "phi": t}


def levels_with_offset(x, g, y, e, codes, fit, sign):
    """Card TR.1's posterior-mean level per driver, with the exposure shift removed (level at e = 0)."""
    beta = fit.get("beta", 0.0)
    return D.posterior_mean_levels(np.asarray(x, float) - beta * np.asarray(e, float), g, y, codes, fit, sign=sign)


def simulate(x, g, e, codes, f, beta, rng):
    n = int(codes.max() + 1)
    z1, z2 = rng.standard_normal(n), rng.standard_normal(n)
    c = f["mu"] + f["sigma_pop"] * z1
    b = 1 / (1 + np.exp(-(f["phi"][3] + f["sigma_b"] * z2)))
    p = b[codes] + (1 - b[codes]) * g * norm.cdf((x - beta * e - c[codes]) / f["sigma_resp"])
    return (rng.random(len(x)) < p).astype(float)


# ---------------------------------------------------------------------------------

def boot_counts(n, rng):
    idx = rng.integers(0, n, size=(N_BOOT, n))
    counts = np.zeros((N_BOOT, n))
    np.add.at(counts, (np.repeat(np.arange(N_BOOT), n), idx.ravel()), 1.0)
    return counts


def ci95(a):
    return tuple(float(v) for v in np.nanpercentile(a, [2.5, 97.5]))


def step1(r, rng):
    drivers = np.sort(r.driver.unique())
    counts = boot_counts(len(drivers), rng)
    L = ["## Step 1 -- is the exposure effect there on study 1's cut-in? (no model)", "",
         f"{r.driver.nunique()} drivers, {len(r)} trials; each stimulus x timepoint four times, showings 1-2 in "
         "session 1 and 3-4 in session 2.", "",
         "| onset | showing 1 | showing 2 | showing 3 | showing 4 | session 2 - session 1 [95% CI] | 2 - 1 | 4 - 3 |",
         "|---|---|---|---|---|---|---|---|"]
    res = {}
    for name, sub in (("pre-onset (C1)", r[r.timepoint == "C1"]), ("post-onset (C2-C6)", r[r.timepoint != "C1"]),
                      ("all", r)):
        s = sub.groupby(["driver", "show"]).intervene.agg(["sum", "count"]).unstack("show").reindex(drivers).fillna(0.0)
        ys, ns = s["sum"].to_numpy(), s["count"].to_numpy()
        p = ys.sum(0) / ns.sum(0)
        bp = (counts @ ys) / (counts @ ns)
        sess = (p[2] + p[3]) / 2 - (p[0] + p[1]) / 2
        bsess = (bp[:, 2] + bp[:, 3]) / 2 - (bp[:, 0] + bp[:, 1]) / 2
        lo, hi = ci95(bsess)
        res[name] = (sess, lo, hi)
        L.append(f"| {name} | " + " | ".join(f"{v:.3f}" for v in p)
                 + f" | {sess:+.3f} [{lo:+.3f}, {hi:+.3f}] | "
                 + f"{p[1] - p[0]:+.3f} [{ci95(bp[:, 1] - bp[:, 0])[0]:+.3f}, {ci95(bp[:, 1] - bp[:, 0])[1]:+.3f}] | "
                 + f"{p[3] - p[2]:+.3f} [{ci95(bp[:, 3] - bp[:, 2])[0]:+.3f}, {ci95(bp[:, 3] - bp[:, 2])[1]:+.3f}] |")
    sess, lo, hi = res["all"]
    negligible = (lo > -NEGLIGIBLE) and (hi < NEGLIGIBLE)
    L += ["", f"**Rule N (pre-stated): the pooled session difference {sess:+.3f} [{lo:+.3f}, {hi:+.3f}] "
          + (f"lies inside +/-{NEGLIGIBLE}: NEGLIGIBLE." if negligible
             else f"does not lie inside +/-{NEGLIGIBLE}: NOT SHOWN NEGLIGIBLE.") + "**", ""]
    return L, negligible


def fit_row(name, f, with_beta):
    ci_b = (f["beta"] - 1.96 * f["se_beta"], f["beta"] + 1.96 * f["se_beta"]) if with_beta else None
    return (f"| {name} | {f['mu']:+.4f} ({f['se_mu']:.4f}) | {f['sigma_pop']:.4f} | {f['sigma_resp']:.4f} | "
            f"{f['b']:.4f} | " + (f"{f['beta']:+.4f} [{ci_b[0]:+.4f}, {ci_b[1]:+.4f}]" if with_beta else "-")
            + f" | {f['neg_log_post']:.2f} | {'yes' if f['se_ok'] else 'NO'} |")


def main() -> None:
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    head = ["# Card EX.2 -- the level fits with a shared exposure term, reported at first exposure", "",
            "Generated by `replication/czb/ex2_first_exposure_levels.py`; steps, gates and rules pre-stated in its "
            "docstring before the run. Do not edit by hand.", ""]

    r = cutin_trials()
    v = ltap_trials()
    L1, negligible = step1(r, rng)
    print("step 1 done", flush=True)
    L = head + L1

    # step 2: reproduce
    xc, gc, yc = r.x_loom.to_numpy(float), r.w_gate.to_numpy(float), r.intervene.to_numpy(float)
    cc, uc = pd.factorize(r.driver)
    prc = F.priors_log_scale(xc)
    fc0 = F.fit_hier_lapse_gated(xc, gc, yc, cc, prc)
    print(f"cut-in pooled: mu {fc0['mu']:.4f} [{time.time() - t0:.0f}s]", flush=True)
    xv, gv, yv = -v.pet.to_numpy(float), np.ones(len(v)), v.intervene.to_numpy(float)
    cv, uv = pd.factorize(v.driver)
    fv0 = TT.fit_threshold(v.pet.to_numpy(float), yv, v.driver.to_numpy())
    prv = F.priors_log_scale(xv)
    print(f"left turn pooled: PET50 {fv0['pet50']:.4f} [{time.time() - t0:.0f}s]", flush=True)
    checks = [("cut-in mu (log theta_dot)", fc0["mu"], -3.4520), ("cut-in sigma_pop", fc0["sigma_pop"], 0.8677),
              ("cut-in sigma_resp", fc0["sigma_resp"], 0.5742), ("left turn PET_50 [s]", fv0["pet50"], 2.18),
              ("left turn sigma_pop [s]", fv0["sigma_pop"], 1.36), ("left turn sigma_resp [s]", fv0["sigma_resp"], 0.86)]
    L += ["## Step 2 -- the pooled refits reproduce their cards", "",
          "| quantity | this run | the card | difference |", "|---|---|---|---|"]
    worst = 0.0
    for name, got, want in checks:
        L.append(f"| {name} | {got:+.4f} | {want:+.4f} | {got - want:+.4f} |")
        worst = max(worst, abs(got - want))
    L += ["", f"Largest disagreement {worst:.4f} against the tolerance {REPRO_TOL}. -> "
          + ("proceed." if worst <= REPRO_TOL else "**STOPPED as pre-stated.**"), ""]
    if worst > REPRO_TOL:
        (OUT / "ex2_first_exposure_levels.md").write_text("\n".join(L), encoding="utf-8")
        return

    # step 3: recovery
    ev = (v.session.to_numpy(int) - 1).astype(float)
    ysim = simulate(xv, gv, ev, cv, fv0, BETA_TRUE, rng)
    fsim = fit_exposure(xv, gv, ysim, ev, cv, prv)
    ok_b = fsim["se_ok"] and abs(fsim["beta"] - BETA_TRUE) < 2 * fsim["se_beta"]
    ok_m = fsim["se_ok"] and abs(fsim["mu"] - fv0["mu"]) < 2 * fsim["se_mu"]
    L += ["## Step 3 -- the extended estimator recovers a known shift (synthetic, left-turn design)", "",
          "| parameter | true | recovered (SE) | within 2 SE |", "|---|---|---|---|",
          f"| beta | {BETA_TRUE:+.3f} | {fsim['beta']:+.3f} ({fsim['se_beta']:.3f}) | {'yes' if ok_b else 'NO'} |",
          f"| mu | {fv0['mu']:+.3f} | {fsim['mu']:+.3f} ({fsim['se_mu']:.3f}) | {'yes' if ok_m else 'NO'} |",
          f"| sigma_pop | {fv0['sigma_pop']:.3f} | {fsim['sigma_pop']:.3f} | - |", "",
          "-> " + ("proceed." if ok_b and ok_m else "**STOPPED as pre-stated.**"), ""]
    print(f"recovery: beta {fsim['beta']:.3f} ({fsim['se_beta']:.3f}) [{time.time() - t0:.0f}s]", flush=True)
    if not (ok_b and ok_m):
        (OUT / "ex2_first_exposure_levels.md").write_text("\n".join(L), encoding="utf-8")
        return

    # step 4: session term, and the showing-index sensitivity
    ec = (r.session.to_numpy(int) - 1).astype(float)
    fc1 = fit_exposure(xc, gc, yc, ec, cc, prc)
    print(f"cut-in session: beta {fc1['beta']:.4f} ({fc1['se_beta']:.4f}) [{time.time() - t0:.0f}s]", flush=True)
    fv1 = fit_exposure(xv, gv, yv, ev, cv, prv)
    print(f"left turn session: beta {fv1['beta']:.4f} ({fv1['se_beta']:.4f}) [{time.time() - t0:.0f}s]", flush=True)
    fc2 = fit_exposure(xc, gc, yc, r.show.to_numpy(float), cc, prc)
    fv2 = fit_exposure(xv, gv, yv, v.show.to_numpy(float), cv, prv)
    print(f"showing-index fits done [{time.time() - t0:.0f}s]", flush=True)

    hdr = ["| fit | mu, level at e = 0 (SE) | sigma_pop | sigma_resp | lapse | beta [95% CI] | neg log posterior | SEs finite |",
           "|---|---|---|---|---|---|---|---|"]
    L += ["## Step 4 -- the exposure term on the real data", "",
          "### The cut-in (axis log theta_dot; level in log rad/s)", ""] + hdr + [
          fit_row("pooled (stage 1, no term)", fc0, False), fit_row("session term (primary)", fc1, True),
          fit_row("showing-index term (sensitivity)", fc2, True), "",
          "### The left turn at 50 km/h (axis -PET; level in -s of PET)", ""] + hdr + [
          fit_row("pooled (TT.1, no term)", fv0, False), fit_row("session term (primary)", fv1, True),
          fit_row("showing-index term (sensitivity)", fv2, True), ""]

    # percentiles and the seconds
    zq = {q: norm.ppf(q / 100) for q in (5, 20, 50, 80, 95)}
    L += ["### Population percentiles, pooled against first exposure (session 1)", "",
          "| scenario | setting | 5th | 20th | 50th | 80th | 95th |", "|---|---|---|---|---|---|---|"]
    for name, f0, f1, conv, unit in (("cut-in", fc0, fc1, np.exp, "rad/s"), ("left turn", fv0, fv1, lambda z: -z, "s of PET")):
        for setting, f in (("pooled", f0), ("first exposure", f1)):
            L.append(f"| {name} [{unit}] | {setting} | " + " | ".join(
                f"{conv(f['mu'] + f['sigma_pop'] * zq[q]):.4f}" for q in (5, 20, 50, 80, 95)) + " |")
    fields = r.attrs.get("fields") or F.build_trials().attrs["fields"]
    crits = ("TTC4", "TTC6", "TTC8")
    on0 = np.nanmean([F.onset_time_theta(fields[c], fc0["mu"]) for c in crits])
    on1 = np.nanmean([F.onset_time_theta(fields[c], fc1["mu"]) for c in crits])
    on2 = np.nanmean([F.onset_time_theta(fields[c], fc1["mu"] + fc1["beta"]) for c in crits])
    L += ["", f"Cut-in, the median level's implied trigger onset averaged over the three stimuli (seconds since "
          f"manoeuvre onset): pooled {on0:+.3f} s, first exposure {on1:+.3f} s, session 2 {on2:+.3f} s. "
          f"First exposure minus pooled: **{on1 - on0:+.3f} s**, against {STEP_S_PER_5PCT} s for one 5-point "
          "percentile step (stage 1).",
          f"Left turn, PET_50: pooled {-fv0['mu']:.3f} s, first exposure {-fv1['mu']:.3f} s, session 2 "
          f"{-(fv1['mu'] + fv1['beta']):.3f} s. First exposure minus pooled: **{-fv1['mu'] + fv0['mu']:+.3f} s** of PET.", ""]

    def excl0(f):
        return f["se_ok"] and (abs(f["beta"]) > 1.96 * f["se_beta"])
    lt_primary = "first exposure" if excl0(fv1) else "pooled"
    ci_primary = "first exposure" if (not negligible and excl0(fc1)) else "pooled"
    L += [f"**Rule A (pre-stated).** Left turn: beta's interval {'excludes' if excl0(fv1) else 'includes'} 0 -> "
          f"**{lt_primary}** is primary. Cut-in: step 1 {'NEGLIGIBLE' if negligible else 'NOT SHOWN NEGLIGIBLE'}, "
          f"beta's interval {'excludes' if excl0(fc1) else 'includes'} 0 -> **{ci_primary}** is primary.", ""]

    # step 5: per-driver levels at first exposure
    lc = levels_with_offset(xc, gc, yc, ec, cc, fc1, +1.0)
    lv = levels_with_offset(xv, gv, yv, ev, cv, fv1, -1.0)
    dc = pd.DataFrame({"driver": uc, "level_cutin_log_first_exposure": [lc[k] for k in range(len(uc))]})
    dv = pd.DataFrame({"driver": uv, "level_ltap_pet_s_first_exposure": [lv[k] for k in range(len(uv))]})
    lc0 = D.posterior_mean_levels(xc, gc, yc, cc, fc0, sign=+1.0)
    lv0 = D.posterior_mean_levels(xv, gv, yv, cv, fv0, sign=-1.0)
    dc["level_cutin_log_pooled"] = [lc0[k] for k in range(len(uc))]
    dv["level_ltap_pet_s_pooled"] = [lv0[k] for k in range(len(uv))]
    both = dc.merge(dv, on="driver").sort_values("driver").reset_index(drop=True)
    both.to_csv(OUT / "ex2_driver_levels_first_exposure.csv", index=False)
    rho1 = -spearmanr(both.level_cutin_log_first_exposure, both.level_ltap_pet_s_first_exposure).statistic
    lo1, hi1 = D.boot_spearman(both.level_cutin_log_first_exposure.to_numpy(), both.level_ltap_pet_s_first_exposure.to_numpy())
    rho0 = -spearmanr(both.level_cutin_log_pooled, both.level_ltap_pet_s_pooled).statistic
    same_c = spearmanr(both.level_cutin_log_pooled, both.level_cutin_log_first_exposure).statistic
    same_v = spearmanr(both.level_ltap_pet_s_pooled, both.level_ltap_pet_s_first_exposure).statistic
    L += ["## Step 5 -- per-driver levels at first exposure (card TR.1 again)", "",
          f"{len(both)} drivers in both scenarios. Signs oriented so that positive means the same person, as TR.1.", "",
          "| quantity | value |", "|---|---|",
          f"| oriented Spearman, levels at first exposure | {rho1:+.3f} (bootstrap {-hi1:+.3f} to {-lo1:+.3f}) |",
          f"| oriented Spearman, pooled levels recomputed here | {rho0:+.3f} |",
          f"| card TR.1 on file | {TR1_RHO[0]:+.3f} (bootstrap {TR1_RHO[1]:+.3f} to {TR1_RHO[2]:+.3f}) |",
          f"| rank agreement of each driver's level, pooled against first exposure: cut-in | {same_c:+.3f} |",
          f"| same, left turn | {same_v:+.3f} |", "",
          f"Runtime {(time.time() - t0) / 60:.1f} min."]
    (OUT / "ex2_first_exposure_levels.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
