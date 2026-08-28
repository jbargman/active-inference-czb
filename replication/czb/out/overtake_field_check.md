# Card B.1 - the cyclist-overtake field

3 clearances x C1-C5 = 15 cells, 2 580 Random trials, the same 43 participants as the cut-in. The field is computed by the cut-in's own predictor code; only role assignment and the onset definition differ (`comfortzone.overtake`).

## 1 Loader validation against the study's clearance labels

| label | edge-to-edge clearance at the pass [m] | onset t [s] | pass t [s] |
|---|---|---|---|
| 0.5m | 0.507 | 17.42 | 21.02 |
| 1m | 1.005 | 17.32 | 21.02 |
| 1.5m | 1.501 | 17.32 | 21.02 |

All three within 0.02 m of the label - **PASS**. The `Offset` column, by contrast, gives 0.94 / 0.45 / 0.05 m and inverts the criticality ordering; it must not be used as the lateral coordinate.

## 2 The observed surface

| clearance | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| 0.5m | 0.221 | 0.221 | 0.395 | 0.576 | 0.686 |
| 1m | 0.203 | 0.180 | 0.238 | 0.349 | 0.372 |
| 1.5m | 0.169 | 0.163 | 0.169 | 0.140 | 0.157 |

## 3 Does the field order the cells the way the humans do?

Spearman rho over the 15 cells, field deficit against observed intervention rate and against perceived unsafety. The `p_lane` range shows how much of the lane-entry weight's dynamic range the scenario actually uses.

| lane-entry variant | rho vs intervene | rho vs PS | p_lane min..max |
|---|---|---|---|
| unidirectional (published form) | +0.402 | +0.458 | 0.843..1.000 |
| bidirectional | +0.185 | +0.344 | 0.000..0.910 |
| unidirectional + S-ramp k=4 | +0.402 | +0.458 | 0.891..1.000 |
| unidirectional + S-ramp k=8 | +0.402 | +0.458 | 0.956..1.000 |
| bidirectional + S-ramp k=8 | -0.537 | -0.359 | 0.000..0.981 |

## 4 The comparator the field has to beat

| predictor | rho vs intervene |
|---|---|
| current edge clearance (negative = bodies overlap) | +0.186 |
| clearance the manoeuvre will end at (the label) | -0.833 |
| best field variant (bidirectional + S-ramp k=8) | -0.537 |

Sign convention: less clearance means more intervention, so a *negative* rho for a clearance predictor and a *positive* rho for the field both mean the cells are ordered correctly.

