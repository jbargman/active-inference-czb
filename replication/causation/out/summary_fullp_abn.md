# Tier-1 results: 5000 seeds, pre-response = no_brake

Generated 2026-08-26. Distributions: glances and decelerations are STAND-INS unless the .json says otherwise.

| condition | response | components | seeds crashing (any bin) | weighted crash prob | avoided seeds | mean P_inj (Eq.10 weights) | mean P_inj reference |
|---|---|---|---|---|---|---|---|
| B | active_inference | glances,decel_cap,no_response,abnormal_accel | 3854/5000 | 0.280 | 1146 | 0.007 | 0.006 |
| C | cbm | glances,decel_cap,no_response,abnormal_accel | 4705/5000 | 0.059 | 295 | 0.007 | 0.006 |

  condition C: attentive onset relative to the tau^-1 = 0.2 anchor, median 0.50 s (IQR 0.50–0.50); seeds with no attentive response: 0


**Condition B vs reference (Wu Eq. 10 weights)**

| metric | stat | ROPE | point | 95% HDI | equivalent | n_ref / n_syn | bins |
|---|---|---|---|---|---|---|---|
| P_inj | θ | [0, 0.188] | 0.148 | [0.110, 0.204] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.091 | [0.068, 0.117] | no | | |
| v_rel [m/s] | θ | [0, 0.188] | 0.148 | [0.110, 0.204] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.091 | [0.068, 0.117] | no | | |
| dv_lead [m/s] | θ | [0, 0.188] | 0.148 | [0.110, 0.204] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.091 | [0.068, 0.117] | no | | |
| t_nr [s] | θ | [0, 0.188] | 0.419 | [0.367, 0.471] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.296 | [0.271, 0.323] | no | | |
| a_l,min [m/s^2] | θ | [0, 0.188] | 0.314 | [0.254, 0.370] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.096 | [0.074, 0.121] | no | | |
| a_f,min [m/s^2] | θ | [0, 0.188] | 1.058 | [1.000, 1.100] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.802 | [0.787, 0.815] | no | | |

Uncertainty: synthetic-side bootstrap, reference treated as population (n=1000).

**Weighted aggregates — Condition B vs reference (Wu Eq. 10 weights)**

| metric | reference mean | synthetic mean | rel. error | binned approx. | rel. error (binned) |
|---|---|---|---|---|---|
| P_inj | 0.0061507 | 0.0069258 | +12.6% | 0.0059873 | -2.7% |
| v_rel [m/s] | 4.7875 | 4.8624 | +1.6% | 4.7614 | -0.5% |
| dv_lead [m/s] | 2.3937 | 2.4312 | +1.6% | 2.3807 | -0.5% |
| t_nr [s] | -0.18766 | -0.19862 | +5.8% | -0.20959 | +11.7% |
| a_l,min [m/s^2] | -1.9809 | -2.195 | +10.8% | -2.1702 | +9.6% |
| a_f,min [m/s^2] | -2.3786 | -2.3709 | -0.3% | -2.2573 | -5.1% |

θ and Θ bound only the between-bin allocation; a gap between the two relative-error columns is within-bin and is invisible to them.

Per-bin diagnostics, P_inj:

| bin | edges | P_ref | P_syn | ω | \|ΔP/P_ref\|·ω | \|ΔP\|·ω |
|---|---|---|---|---|---|---|
| 1 | -inf – 0.00264 | 0.200 | 0.174 | 1.00 | 0.128 | 0.026 |
| 2 | 0.00264 – 0.0033 | 0.200 | 0.205 | 1.00 | 0.024 | 0.005 |
| 3 | 0.0033 – 0.00431 | 0.201 | 0.212 | 1.00 | 0.056 | 0.011 |
| 4 | 0.00431 – 0.00735 | 0.199 | 0.229 | 1.00 | 0.148 | 0.030 |
| 5 | 0.00735 – inf | 0.200 | 0.180 | 1.00 | 0.099 | 0.020 |

**Condition B vs reference (exposure weights, omega / p_c under C)**

| metric | stat | ROPE | point | 95% HDI | equivalent | n_ref / n_syn | bins |
|---|---|---|---|---|---|---|---|
| P_inj | θ | [0, 0.188] | 2.508 | [2.305, 2.669] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 1.003 | [0.922, 1.067] | no | | |
| v_rel [m/s] | θ | [0, 0.188] | 2.508 | [2.305, 2.669] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 1.003 | [0.922, 1.067] | no | | |
| dv_lead [m/s] | θ | [0, 0.188] | 2.508 | [2.305, 2.669] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 1.003 | [0.922, 1.067] | no | | |
| t_nr [s] | θ | [0, 0.188] | 1.353 | [1.158, 1.555] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.639 | [0.562, 0.726] | no | | |
| a_l,min [m/s^2] | θ | [0, 0.188] | 1.537 | [1.446, 1.637] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 0.936 | [0.880, 0.996] | no | | |
| a_f,min [m/s^2] | θ | [0, 0.188] | 2.308 | [2.191, 2.409] | no | 5000 / 103857 | 5 |
| | Θ | [0, 0.089] | 1.118 | [1.062, 1.167] | no | | |

Uncertainty: synthetic-side bootstrap, reference treated as population (n=1000).

**Weighted aggregates — Condition B vs reference (exposure weights, omega / p_c under C)**

| metric | reference mean | synthetic mean | rel. error | binned approx. | rel. error (binned) |
|---|---|---|---|---|---|
| P_inj | 0.0061507 | 0.0030151 | -51.0% | 0.0031336 | -49.1% |
| v_rel [m/s] | 4.7875 | 1.6972 | -64.5% | 1.8256 | -61.9% |
| dv_lead [m/s] | 2.3937 | 0.84859 | -64.5% | 0.91279 | -61.9% |
| t_nr [s] | -0.18766 | -0.094714 | -49.5% | -0.1074 | -42.8% |
| a_l,min [m/s^2] | -1.9809 | -0.57605 | -70.9% | -0.55221 | -72.1% |
| a_f,min [m/s^2] | -2.3786 | -0.75834 | -68.1% | -0.72478 | -69.5% |

θ and Θ bound only the between-bin allocation; a gap between the two relative-error columns is within-bin and is invisible to them.

Per-bin diagnostics, P_inj:

| bin | edges | P_ref | P_syn | ω | \|ΔP/P_ref\|·ω | \|ΔP\|·ω |
|---|---|---|---|---|---|---|
| 1 | -inf – 0.00264 | 0.200 | 0.701 | 1.00 | 2.508 | 0.501 |
| 2 | 0.00264 – 0.0033 | 0.200 | 0.135 | 1.00 | 0.324 | 0.065 |
| 3 | 0.0033 – 0.00431 | 0.201 | 0.078 | 1.00 | 0.609 | 0.122 |
| 4 | 0.00431 – 0.00735 | 0.199 | 0.056 | 1.00 | 0.717 | 0.143 |
| 5 | 0.00735 – inf | 0.200 | 0.029 | 1.00 | 0.857 | 0.172 |

**Condition C vs reference (Wu Eq. 10 weights)**

| metric | stat | ROPE | point | 95% HDI | equivalent | n_ref / n_syn | bins |
|---|---|---|---|---|---|---|---|
| P_inj | θ | [0, 0.188] | 0.209 | [0.176, 0.244] | no | 5000 / 701777 | 5 |
| | Θ | [0, 0.089] | 0.150 | [0.132, 0.166] | no | | |
| v_rel [m/s] | θ | [0, 0.188] | 0.209 | [0.176, 0.244] | no | 5000 / 701777 | 5 |
| | Θ | [0, 0.089] | 0.150 | [0.132, 0.166] | no | | |
| dv_lead [m/s] | θ | [0, 0.188] | 0.209 | [0.176, 0.244] | no | 5000 / 701777 | 5 |
| | Θ | [0, 0.089] | 0.150 | [0.132, 0.166] | no | | |
| t_nr [s] | θ | [0, 0.188] | 0.460 | [0.423, 0.496] | no | 5000 / 701777 | 5 |
| | Θ | [0, 0.089] | 0.378 | [0.359, 0.393] | no | | |
| a_l,min [m/s^2] | θ | [0, 0.188] | 0.254 | [0.209, 0.292] | no | 5000 / 701777 | 5 |
| | Θ | [0, 0.089] | 0.070 | [0.055, 0.087] | yes | | |
| a_f,min [m/s^2] | θ | [0, 0.188] | 1.380 | [1.340, 1.422] | no | 5000 / 701777 | 5 |
| | Θ | [0, 0.089] | 0.702 | [0.690, 0.713] | no | | |

Uncertainty: synthetic-side bootstrap, reference treated as population (n=1000).

**Weighted aggregates — Condition C vs reference (Wu Eq. 10 weights)**

| metric | reference mean | synthetic mean | rel. error | binned approx. | rel. error (binned) |
|---|---|---|---|---|---|
| P_inj | 0.0061507 | 0.0067886 | +10.4% | 0.0058431 | -5.0% |
| v_rel [m/s] | 4.7875 | 4.7751 | -0.3% | 4.6934 | -2.0% |
| dv_lead [m/s] | 2.3937 | 2.3875 | -0.3% | 2.3467 | -2.0% |
| t_nr [s] | -0.18766 | -0.2094 | +11.6% | -0.22132 | +17.9% |
| a_l,min [m/s^2] | -1.9809 | -2.1036 | +6.2% | -2.0931 | +5.7% |
| a_f,min [m/s^2] | -2.3786 | -3.2139 | +35.1% | -3.0722 | +29.2% |

θ and Θ bound only the between-bin allocation; a gap between the two relative-error columns is within-bin and is invisible to them.

Per-bin diagnostics, P_inj:

| bin | edges | P_ref | P_syn | ω | \|ΔP/P_ref\|·ω | \|ΔP\|·ω |
|---|---|---|---|---|---|---|
| 1 | -inf – 0.00264 | 0.200 | 0.158 | 1.00 | 0.209 | 0.042 |
| 2 | 0.00264 – 0.0033 | 0.200 | 0.221 | 1.00 | 0.107 | 0.021 |
| 3 | 0.0033 – 0.00431 | 0.201 | 0.217 | 1.00 | 0.083 | 0.017 |
| 4 | 0.00431 – 0.00735 | 0.199 | 0.236 | 1.00 | 0.186 | 0.037 |
| 5 | 0.00735 – inf | 0.200 | 0.167 | 1.00 | 0.166 | 0.033 |