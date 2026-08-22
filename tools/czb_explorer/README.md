# Comfort-zone explorer tools

Three static, client-side pages sharing one navigation bar — run and deploy them
together (see Run it below):

- **`index.html` — boundary explorer (tier 1).** An interactive page for playing with the closed-form comfort-zone boundary of the
active-inference driver model (handbook chapters 07 and 11): move the assumptions —
assumed worst-case lead braking, reaction-time budget, comfort deceleration limit — and
watch the boundary move, as headway-vs-speed curves, as contours on the
required-deceleration field, and as numbers. Presets reproduce the handbook's
extra-motive examples; Snapshot freezes the current curves in grey for before/after
comparison.

- **`norms.html` — norm-tournament sandbox (tier 2).** How the driver model imagines
  other vehicles: the swarm's norm-biased sampling rule, live. Drag the other vehicle
  across the lane edge and watch trust being extended, revoked, and regained; every
  factor of the tournament (candidates, foresight, geometry weights) is a slider.
  The math (`norm_math.js`) is an illustrative lateral-only reimplementation of
  `forward_tar_agent` (handbook ch. 06); its qualitative properties are checked by
  `test_norms.mjs`.
- **`model_browser.html` — model browser (tier 3).** The closed loop is far too slow
  for live sliders (~18 s CPU per simulated timestep), so this page browses what the
  authors already ran: all 224 rear-end runs of the OSF deposit — the baseline grid
  plus all seven Figure-6 ablations — as per-condition response-time histograms,
  outcome bars, and a collision grid, each comparable against baseline; plus rate
  tables for the oncoming and intersection scenarios. Data (`data_model.js`, ~130 KB)
  is precomputed by `build_data.py` from the deposit and committed, so the pages work
  without the 3.1 GB archive.

This completes all three tiers of the tool plan in `notes/TODO_understanding_pack.md`.

## Run it

**Locally, no install:** double-click `index.html` (everything is client-side;
no server needed), or, if you prefer serving it:

```bash
python -m http.server 8080 -d tools/czb_explorer
# -> http://localhost:8080
```

**Docker (for deployment elsewhere):**

```bash
docker build -t czb-explorer tools/czb_explorer
docker run --rm -p 8080:80 czb-explorer
# -> http://localhost:8080
```

The image is nginx serving three static files; it runs on any container host. The
folder also works as-is on any static-site host (GitHub Pages included).

## Trusting the numbers

The page re-implements the closed form (`src/comfortzone/field.py::critical_gap`) in
JavaScript. Two guards keep the two implementations honest — the same
two-independent-routes discipline that once caught a sign error in the Python version
(handbook chapter 09, rung 0):

- `generate_reference.py` exports 700 ground-truth cases from the Python code into
  `reference.js`; the page checks itself against them on every load and shows a
  green/red badge top right.
- `node test_node.mjs` runs the same comparison headlessly, plus an inverse-property
  check (the required-deceleration field must exactly invert the boundary).

After changing either implementation: regenerate the reference, re-run the test.

```bash
python tools/czb_explorer/generate_reference.py
node tools/czb_explorer/test_node.mjs
```

## The one rule of use

Boundary values shown are conditional on the slider assumptions. Never quote a critical
headway from this page without stating the assumed worst-case lead braking and the
reaction-time budget it was read at (`HANDOFF.md` §7).
