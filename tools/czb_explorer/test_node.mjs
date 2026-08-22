/* Node test: the JS closed form must match the Python reference exactly
 * (within float round-trip), and aRequired must invert criticalGap.
 *
 *     node tools/czb_explorer/test_node.mjs
 */
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const CZB = require("./czb_math.js");
const REF = require("./reference.js");

let maxErr = 0;
let maxThwErr = 0;
for (const c of REF.cases) {
  const dx = CZB.criticalGap(c.v, c.v, c.aOvMin, c.tReact, c.aReq);
  const thw = CZB.criticalThw(c.v, c.v, c.aOvMin, c.tReact, c.aReq);
  maxErr = Math.max(maxErr, Math.abs(dx - c.dx));
  maxThwErr = Math.max(maxThwErr, Math.abs(thw - c.thw));
}
console.log(`boundary: ${REF.cases.length} cases, max |dx err| = ${maxErr.toExponential(2)} m, max |thw err| = ${maxThwErr.toExponential(2)} s`);

// Inverse property: aRequired(v, criticalGap(..., aReq)) === aReq
let maxInvErr = 0;
for (const c of REF.cases) {
  const dx = CZB.criticalGap(c.v, c.v, c.aOvMin, c.tReact, c.aReq);
  const back = CZB.aRequired(c.v, dx, c.v, c.aOvMin, c.tReact);
  if (isFinite(back)) maxInvErr = Math.max(maxInvErr, Math.abs(back - c.aReq));
}
console.log(`inverse property: max |aReq err| = ${maxInvErr.toExponential(2)} m/s^2`);

const ok = maxErr < 1e-4 && maxThwErr < 1e-4 && maxInvErr < 1e-6;
console.log(ok ? "PASS" : "FAIL");
process.exit(ok ? 0 : 1);
