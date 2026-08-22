/* Closed-form comfort-zone boundary for car following.
 *
 * JavaScript port of src/comfortzone/field.py::critical_gap / critical_thw
 * (Schumann et al. 2026, SI Eqs. 49-51 rearranged). The port is verified
 * against reference values generated from the Python code by
 * generate_reference.py -- run test_node.mjs, or see the in-page check badge.
 * Two independent routes to the same surface; see handbook chapter 09, rung 0.
 *
 * Conventions: decelerations are passed as the Python code takes them --
 * aOvMin is negative (m/s^2, the assumed worst-case lead braking), aReq is
 * positive (m/s^2, the deceleration defining the boundary). dx is the
 * separation of vehicle centers; bumper-to-bumper gap = dx - L.
 */

const CZB = {
  L: 4.2, // vehicle length lf + lr [m]

  criticalGap(vEgo, vOther, aOvMin, tReact, aReq, aEgo = 0.0, aOther = 0.0) {
    const L = this.L;
    aEgo = Math.min(aEgo, 0.0);
    aOther = Math.min(aOther, 0.0);
    const aTest = Math.min(aOther, aOvMin);
    const vReact = Math.max(vEgo + aEgo * tReact, 0.0);
    return (
      1.15 * L +
      (0.5 * vReact * vReact) / aReq -
      (vOther * vOther) / (2.0 * Math.abs(aTest)) +
      vEgo * tReact +
      0.5 * aEgo * tReact * tReact
    );
  },

  criticalThw(vEgo, vOther, aOvMin, tReact, aReq, aEgo = 0.0, aOther = 0.0) {
    const dx = this.criticalGap(vEgo, vOther, aOvMin, tReact, aReq, aEgo, aOther);
    return (dx - this.L) / Math.max(vEgo, 1e-6);
  },

  /* Required deceleration at a given state (steady following, aEgo = 0):
   * the field the heatmap shows. Infinity where no braking can avoid the
   * counterfactual collision (inside the dread region's core). */
  aRequired(vEgo, dx, vOther, aOvMin, tReact, aOther = 0.0) {
    const L = this.L;
    const aTest = Math.min(Math.min(aOther, 0.0), aOvMin);
    const dReact = dx + (vOther * vOther) / (2.0 * Math.abs(aTest)) - vEgo * tReact;
    const denom = dReact - 1.15 * L;
    if (denom <= 0) return Infinity;
    return (0.5 * vEgo * vEgo) / denom;
  },
};

if (typeof module !== "undefined") module.exports = CZB;
if (typeof window !== "undefined") window.CZB = CZB;
