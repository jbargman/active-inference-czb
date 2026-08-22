/* Lateral-only reimplementation of the norm tournament that moves every
 * particle's other-vehicle state in the driver model
 * (external/aica src/common/dynamics.py::forward_tar_agent; handbook ch. 06).
 *
 * Illustrative by design: real geometry factors and sampling rule, simplified
 * dynamics (lateral random walk). The same rule generates the handbook's
 * norm_tournament figure (docs/handbook/make_diagrams.py); test_norms.mjs
 * checks its qualitative properties.
 */

const NORM = {
  defaults: {
    lane: 3.65,      // lane width [m]
    d: 1.72,         // vehicle width [m]
    wp: 1e-3,        // weight in the marginal band (weigh_particles)
    fvf: 1e-2,       // extra factor for gross violation (full_violation_factor)
    sigma: 0.12,     // per-step lateral move scale [m]
    nNorm: 32,       // candidates per tournament (N_norm)
    hNorm: 20,       // foresight steps for the "later" score (H_norm)
    steps: 20,       // trajectory length (x 0.2 s = 4 s)
    nTraj: 120,      // fan size
  },

  halfLane(p) { return 0.5 * (p.lane - p.d); },

  /* Compliance weight of a lateral position (rear-end geometry). */
  weight(y, p) {
    const aw = this.halfLane(p);
    const a = Math.abs(y);
    if (a < aw) return 1.0;
    if (a < aw + 0.2 * p.d) return p.wp;
    return p.wp * p.fvf;
  },

  /* Deterministic PRNG so tests are reproducible. */
  rng(seed) {
    let s = seed >>> 0;
    return function () {
      s |= 0; s = (s + 0x6D2B79F5) | 0;
      let t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  },

  gauss(rand) {
    let u = 0, v = 0;
    while (u === 0) u = rand();
    while (v === 0) v = rand();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  },

  /* One tournament step: from y, return the sampled next y. */
  step(y, biased, p, rand) {
    const cand = new Array(p.nNorm);
    for (let k = 0; k < p.nNorm; k++) cand[k] = y + p.sigma * this.gauss(rand);
    if (!biased) return cand[0];
    const wNow = this.weight(y, p);           // shared by all candidates
    const w = new Array(p.nNorm);
    let sum = 0;
    for (let k = 0; k < p.nNorm; k++) {
      const wNext = this.weight(cand[k], p);
      const wLong = this.weight(y + (cand[k] - y) * p.hNorm, p);
      const wFut = (2 * wNext * wLong) / (wNext + wLong);   // harmonic mean
      w[k] = Math.min(wNow, wFut);                          // the trust cap
      sum += w[k];
    }
    let r = rand() * sum;
    for (let k = 0; k < p.nNorm; k++) {
      r -= w[k];
      if (r <= 0) return cand[k];
    }
    return cand[p.nNorm - 1];
  },

  /* A fan of trajectories from y0. Returns array of arrays (length steps+1). */
  fan(y0, biased, p, seed) {
    const rand = this.rng(seed);
    const out = [];
    for (let i = 0; i < p.nTraj; i++) {
      const tr = [y0];
      let y = y0;
      for (let t = 0; t < p.steps; t++) {
        y = this.step(y, biased, p, rand);
        tr.push(y);
      }
      out.push(tr);
    }
    return out;
  },
};

if (typeof module !== "undefined") module.exports = NORM;
if (typeof window !== "undefined") window.NORM = NORM;
