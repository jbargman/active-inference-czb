/* Property tests for the norm-tournament sandbox math.
 *
 *     node tools/czb_explorer/test_norms.mjs
 *
 * The tournament has no closed form to check against; these verify the
 * qualitative claims of handbook chapter 06 hold in the implementation:
 * the bias keeps a compliant target's fan in lane, the trust cap makes a
 * gross violator's early fan open like raw noise, and re-entering
 * hypotheses are recaptured (homing).
 */
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const NORM = require("./norm_math.js");

const p = { ...NORM.defaults, nTraj: 300 };
const aw = NORM.halfLane(p);
let failures = 0;
const check = (name, cond, detail) => {
  console.log((cond ? "PASS " : "FAIL ") + name + "  (" + detail + ")");
  if (!cond) failures++;
};

// 0. weight function values
check("weight core/band/gross",
  NORM.weight(0, p) === 1 &&
  NORM.weight(aw + 0.1 * p.d, p) === p.wp &&
  NORM.weight(aw + 0.5 * p.d, p) === p.wp * p.fvf,
  "1 / " + p.wp + " / " + p.wp * p.fvf);

const inLane = (tr) => Math.abs(tr[tr.length - 1]) < aw;
const frac = (fans, f) => fans.filter(f).length / fans.length;
const stdAt = (fans, t) => {
  const ys = fans.map((tr) => tr[t]);
  const m = ys.reduce((a, b) => a + b, 0) / ys.length;
  return Math.sqrt(ys.reduce((a, y) => a + (y - m) ** 2, 0) / ys.length);
};

// 1. compliant start: the bias keeps the fan in lane
{
  const biased = NORM.fan(0, true, p, 42);
  const raw = NORM.fan(0, false, p, 43);
  const fb = frac(biased, inLane), fr = frac(raw, inLane);
  const spread = stdAt(biased, p.steps) / stdAt(raw, p.steps);
  check("compliant: biased fan is far tighter and at least as in-lane",
        spread < 0.5 && fb >= fr && fb > 0.98,
        "final spread ratio " + spread.toFixed(2) + ", in-lane biased " +
        fb.toFixed(2) + " vs raw " + fr.toFixed(2));
}

// 2. gross violator: trust cap opens the early fan like raw noise
{
  const y0 = aw + 0.2 * p.d + 0.3;
  const biased = NORM.fan(y0, true, p, 44);
  const raw = NORM.fan(y0, false, p, 45);
  const ratio = stdAt(biased, 2) / stdAt(raw, 2);
  check("violator: early fan opens (trust cap)", ratio > 0.6 && ratio < 1.6,
        "step-2 spread ratio " + ratio.toFixed(2));
}

// 3. homing: re-entering hypotheses are recaptured
{
  const y0 = aw + 0.2 * p.d + 0.3;
  const biased = NORM.fan(y0, true, p, 46);
  const raw = NORM.fan(y0, false, p, 47);
  const fb = frac(biased, inLane), fr = frac(raw, inLane);
  check("violator: biased fan homes to lane", fb > fr + 0.1,
        "biased " + fb.toFixed(2) + " vs raw " + fr.toFixed(2));
}

console.log(failures === 0 ? "PASS (all)" : failures + " FAILURES");
process.exit(failures === 0 ? 0 : 1);
