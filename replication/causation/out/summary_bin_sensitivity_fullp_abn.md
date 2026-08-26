# Bin-count sensitivity of the equivalence readout

Reference n = 5000. Wu et al. (2026) Eq. 4 gives N = 20 at this size; the
full-population tables were produced with N = 5. Both statistics tighten with
finer bins: theta because it is a worst-bin maximum, Theta because it is a
lower bound on twice the total-variation distance that becomes exact only as
the partition is refined. Note also that theta is a maximum over bins and is
therefore biased upward under resampling, so its bootstrap HDI can sit above
the point estimate; the bias grows with N.


## Condition B (active_inference), n_syn = 103857

| metric | N=5 theta | N=10 theta | N=20 theta | N=5 Theta | N=10 Theta | N=20 Theta |
|---|---|---|---|---|---|---|
| P_inj | 0.148 [0.085, 0.273] | 0.241 [0.170, 0.425] | 0.275 [0.347, 0.773] | 0.091 | 0.091 | 0.165 |
| v_rel [m/s] | 0.148 [0.085, 0.273] | 0.241 [0.170, 0.425] | 0.275 [0.347, 0.773] | 0.091 | 0.091 | 0.165 |
| t_nr [s] | 0.419 [0.331, 0.596] | 0.636 [0.552, 0.931] | 0.636 [0.574, 1.033] | 0.296 | 0.353 | 0.389 |
| a_l,min [m/s^2] | 0.314 [0.136, 0.573] | 0.314 [0.238, 1.000] | 0.786 [0.622, 1.000] | 0.096 | 0.100 | 0.118 |
| a_f,min [m/s^2] | 1.058 [1.000, 1.359] | 3.983 [2.490, 4.112] | 3.983 [3.300, 4.693] | 0.802 | 1.094 | 1.233 |

## Condition C (cbm), n_syn = 701777

| metric | N=5 theta | N=10 theta | N=20 theta | N=5 Theta | N=10 Theta | N=20 Theta |
|---|---|---|---|---|---|---|
| P_inj | 0.209 [0.148, 0.343] | 0.255 [0.214, 0.487] | 0.352 [0.334, 0.754] | 0.150 | 0.150 | 0.168 |
| v_rel [m/s] | 0.209 [0.148, 0.343] | 0.255 [0.214, 0.487] | 0.352 [0.334, 0.754] | 0.150 | 0.150 | 0.168 |
| t_nr [s] | 0.460 [0.383, 0.640] | 0.623 [0.560, 0.989] | 0.699 [0.565, 1.261] | 0.378 | 0.428 | 0.459 |
| a_l,min [m/s^2] | 0.254 [0.070, 0.461] | 0.254 [0.167, 1.000] | 0.591 [0.428, 1.000] | 0.070 | 0.070 | 0.077 |
| a_f,min [m/s^2] | 1.380 [1.000, 1.413] | 2.165 [1.908, 2.196] | 4.456 [4.251, 5.168] | 0.702 | 1.062 | 1.151 |
