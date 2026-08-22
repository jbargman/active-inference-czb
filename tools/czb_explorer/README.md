# Comfort-zone boundary explorer

An interactive page for playing with the closed-form comfort-zone boundary of the
active-inference driver model (handbook chapters 07 and 11): move the assumptions —
assumed worst-case lead braking, reaction-time budget, comfort deceleration limit — and
watch the boundary move, as headway-vs-speed curves, as contours on the
required-deceleration field, and as numbers. Presets reproduce the handbook's
extra-motive examples; Snapshot freezes the current curves in grey for before/after
comparison.

Tier 1 of the tool plan in `notes/TODO_understanding_pack.md`: static, client-side only,
genuinely real-time. Tiers 2 (norm-tournament sandbox) and 3 (precomputed closed-loop
browser) are future work.

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
