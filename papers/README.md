# Waymo safety research papers

Source: https://waymo.com/safety/research/ (54 papers, fetched 2026-08-17).
Downloaded with `download.sh` from `manifest.tsv`; per-paper status in `results.tsv`.

| Category | Downloaded | Missing |
|---|---|---|
| Active inference (primary focus) | 6 | 1 |
| Driver behaviour modelling (closely related) | 8 | 0 |
| Collision-avoidance simulation / counterfactuals | 2 | 1 |
| Crash-rate benchmarks & retrospective safety performance | 11 | 1 |
| Safety case, safety readiness & governance | 9 | 1 |
| Injury risk, VRUs & Safe System | 4 | 8 |
| Conflict typology & scenarios | 1 | 1 |

## Active inference (primary focus)  (`active-inference/`)

Engström/Wei/Schumann line of work modelling human driving as active inference. Start here.

- ✅ **2025** — Active inference as a unified model of collision avoidance behavior in human drivers  
  <active-inference/2025 - Active inference as a unified model of collision avoidance behavior in human drivers.pdf>
- ✅ **2024** — Active inference as a general framework for modeling human driving behavior (IWAI poster, Engstrom et al.)  
  <active-inference/2024 - Active inference as a general framework for modeling human driving behavior (IWAI poster, Engstrom et al.).pdf>
- ✅ **2024** — Active inference-based modeling of human driver collision avoidance behavior (IWAI poster, Schumann et al.)  
  <active-inference/2024 - Active inference-based modeling of human driver collision avoidance behavior (IWAI poster, Schumann et al.).pdf>
- ✅ **2024** — Resolving uncertainty on the fly - modeling adaptive driving behavior as active inference  
  <active-inference/2024 - Resolving uncertainty on the fly - modeling adaptive driving behavior as active inference.pdf>
- ✅ **2023** — An active inference model of car following  
  <active-inference/2023 - An active inference model of car following.pdf>
- ✅ **2023** — Measuring surprise in the wild  
  <active-inference/2023 - Measuring surprise in the wild.pdf>
- ❌ **2023** — World model learning from demonstrations with active inference  
  <https://link.springer.com/content/pdf/10.1007/978-3-031-28719-0_9.pdf>

## Driver behaviour modelling (closely related)  (`driver-behavior-modeling/`)

Affordances, uncertainty, response timing, evasive manoeuvres — the conceptual/empirical basis the active-inference models build on. 'Looking for an out', 'Field of Safe Motion' and 'Resolving space-sharing conflicts' are the closest to the active-inference work.

- ✅ **2026** — Resolving space-sharing conflicts in road user interactions through uncertainty reduction  
  <driver-behavior-modeling/2026 - Resolving space-sharing conflicts in road user interactions through uncertainty reduction.pdf>
- ✅ **2026** — The Field of Safe Motion - Operationalizing affordances in the field of safe travel using reachability analysis  
  <driver-behavior-modeling/2026 - The Field of Safe Motion - Operationalizing affordances in the field of safe travel using reachability analysis.pdf>
- ✅ **2025** — Automated brake onset detection in naturalistic driving data  
  <driver-behavior-modeling/2025 - Automated brake onset detection in naturalistic driving data.pdf>
- ✅ **2025** — Being good (at driving) - Characterizing behavioral expectations on automated and human driven vehicles  
  <driver-behavior-modeling/2025 - Being good (at driving) - Characterizing behavioral expectations on automated and human driven vehicles.pdf>
- ✅ **2025** — Looking for an out - Affordances, uncertainty and collision avoidance behavior of human drivers  
  <driver-behavior-modeling/2025 - Looking for an out - Affordances, uncertainty and collision avoidance behavior of human drivers.pdf>
- ✅ **2024** — Characterising vulnerable road user evasive manoeuvring in real-world crashes  
  <driver-behavior-modeling/2024 - Characterising vulnerable road user evasive manoeuvring in real-world crashes.pdf>
- ✅ **2024** — Kinematic characterization of micro-mobility vehicles during evasive maneuvers  
  <https://arxiv.org/pdf/2312.14717>
- ✅ **2024** — Modeling road user response timing in naturalistic traffic conflicts  
  <https://arxiv.org/pdf/2208.08651>

## Collision-avoidance simulation / counterfactuals  (`collision-avoidance-simulation/`)

ADS re-simulated in reconstructed fatal crashes; human reference models (NIEON etc.).

- ✅ **2026** — Collision avoidance effectiveness of an ADS using a human driver behavior reference model in reconstructed fatal collisions  
  <collision-avoidance-simulation/2026 - Collision avoidance effectiveness of an ADS using a human driver behavior reference model in reconstructed fatal collisi.pdf>
- ✅ **2026** — Collision avoidance testing of the Waymo automated driving system  
  <collision-avoidance-simulation/2026 - Collision avoidance testing of the Waymo automated driving system.pdf>
- ❌ **2021** — Waymo simulated driving behavior in reconstructed fatal crashes  
  <https://doi.org/10.1016/j.aap.2021.106454>

## Crash-rate benchmarks & retrospective safety performance  (`crash-rate-benchmarks/`)

Waymo vs human crash rates at 1M/7.1M/25M/56.7M miles; benchmark methodology; RAVE checklist.

- ✅ **2026** — Building scientific consensus on the crash safety performance of automated driving systems  
  <crash-rate-benchmarks/2026 - Building scientific consensus on the crash safety performance of automated driving systems.pdf>
- ❌ **2026** — High-resolution urban fatal crash rate benchmarks for automated driving system assessment  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2026.2684002>
- ✅ **2025** — Comparison of Waymo rider-only crash rates by crash type to human benchmarks at 56.7 million miles  
  <https://arxiv.org/pdf/2505.01515>
- ✅ **2025** — Dynamic benchmarks - Spatial and temporal alignment for ADS performance evaluation  
  <crash-rate-benchmarks/2025 - Dynamic benchmarks - Spatial and temporal alignment for ADS performance evaluation.pdf>
- ✅ **2025** — From stoplights to on-ramps - A comprehensive set of crash rate benchmarks  
  <crash-rate-benchmarks/2025 - From stoplights to on-ramps - A comprehensive set of crash rate benchmarks.pdf>
- ✅ **2024** — Benchmarks for retrospective automated driving system crash rate analysis  
  <https://arxiv.org/pdf/2312.13228>
- ✅ **2024** — Comparative safety performance of autonomous and human drivers - A real-world case study  
  <https://europepmc.org/articles/PMC11305169?pdf=render>
- ✅ **2024** — Comparison of Waymo rider-only crash data to human benchmarks at 7.1 million miles  
  <https://arxiv.org/pdf/2312.12675>
- ✅ **2024** — Do autonomous vehicles outperform latest-generation human-driven vehicles (Swiss Re, 25M miles)  
  <crash-rate-benchmarks/2024 - Do autonomous vehicles outperform latest-generation human-driven vehicles (Swiss Re, 25M miles).pdf>
- ✅ **2024** — RAVE checklist - Recommendations for overcoming challenges in retrospective studies  
  <https://arxiv.org/pdf/2408.07758>
- ✅ **2023** — Safety performance of the Waymo rider-only automated driving system at one million miles  
  <crash-rate-benchmarks/2023 - Safety performance of the Waymo rider-only automated driving system at one million miles.pdf>
- ✅ **2020** — Waymo public road safety performance data  
  <crash-rate-benchmarks/2020 - Waymo public road safety performance data.pdf>

## Safety case, safety readiness & governance  (`safety-case-and-governance/`)

Safety case assessment, absence of unreasonable risk, SMS, standards landscape, fatigue risk, safety reports.

- ✅ **2026** — Assessing a safety case - Bottom-up guidance for claims and evidence evaluation  
  <safety-case-and-governance/2026 - Assessing a safety case - Bottom-up guidance for claims and evidence evaluation.pdf>
- ✅ **2025** — Building a credible case for safety - Waymo's approach for the determination of absence of unreasonable risk  
  <https://arxiv.org/pdf/2306.01917>
- ✅ **2025** — Determining absence of unreasonable risk - Approval guidelines for an ADS deployment  
  <https://arxiv.org/pdf/2505.09880>
- ❌ **2025** — Developing a safety management system for the automated vehicle industry  
  <https://doi.org/10.4271/2025-01-8673>
- ✅ **2023** — ADS standardization landscape - Making sense of its status  
  <safety-case-and-governance/2023 - ADS standardization landscape - Making sense of its status.pdf>
- ✅ **2023** — Challenges for the evaluation of automated driving systems  
  <safety-case-and-governance/2023 - Challenges for the evaluation of automated driving systems.pdf>
- ✅ **2023** — Interpreting safety outcomes - Waymo's performance evaluation in the context of a broader determination of safety readiness  
  <safety-case-and-governance/2023 - Interpreting safety outcomes - Waymo's performance evaluation in the context of a broader determination of safety readin.pdf>
- ✅ **2022** — Waymo's fatigue risk management framework  
  <safety-case-and-governance/2022 - Waymo's fatigue risk management framework.pdf>
- ✅ **2021** — Waymo safety report  
  <safety-case-and-governance/2021 - Waymo safety report.pdf>
- ✅ **2020** — Waymo's safety methodologies and safety readiness determinations  
  <safety-case-and-governance/2020 - Waymo's safety methodologies and safety readiness determinations.pdf>

## Injury risk, VRUs & Safe System  (`injury-risk-and-vru/`)

Injury risk curves (pedestrian, cyclist, motorcyclist), seat belts, speed compliance, TARGET setting.

- ❌ **2025** — A mechanistic approach to modeling omnidirectional motorcyclist injury risk  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2025.2570829>
- ❌ **2025** — Potential safety benefits associated with speed limit compliance in San Francisco and Phoenix  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2025.2538726>
- ✅ **2025** — Ride-hailing in the Safe System - Increased seat belt compliance and late model year vehicles  
  <injury-risk-and-vru/2025 - Ride-hailing in the Safe System - Increased seat belt compliance and late model year vehicles.pdf>
- ✅ **2025** — TARGET setting for high severity collisions  
  <https://tsr.international/TSR/article/download/27552/24424>
- ❌ **2024** — Baseline vulnerable road user injury risk in multiple U.S. dense-urban driving environments  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2024.2364050>
- ❌ **2024** — Bridging the gap - Mechanistic-based cyclist injury risk curves  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2024.2400276>
- ❌ **2024** — Representative cyclist collision injury risk distributions for a dense-urban US ODD  
  <https://doi.org/10.4271/2024-01-2645>
- ✅ **2023** — Descriptive analysis of cyclist dooring events using data from NEISS  
  <injury-risk-and-vru/2023 - Descriptive analysis of cyclist dooring events using data from NEISS.pdf>
- ❌ **2023** — Passenger and heavy vehicle collisions with pedestrians  
  <https://doi.org/10.1016/j.aap.2023.107139>
- ✅ **2023** — Representative pedestrian collision injury risk distributions  
  <injury-risk-and-vru/2023 - Representative pedestrian collision injury risk distributions.pdf>
- ❌ **2022** — Methodology for determining maximum injury potential  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2022.2125231>
- ❌ **2021** — An omni-directional model of injury risk in planar crashes  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2021.1955108>

## Conflict typology & scenarios  (`conflict-typology-and-scenarios/`)

Conflict typology framework; functional scenarios for intersection collisions.

- ❌ **2023** — Determination of functional scenarios for intersection collisions  
  <https://doi.org/10.1016/j.aap.2023.107326>
- ✅ **2023** — Framework for a conflict typology including contributing factors  
  <conflict-typology-and-scenarios/2023 - Framework for a conflict typology including contributing factors.pdf>

## Missing (need library / institutional access)

No open-access copy found (Unpaywall + arXiv checked). Taylor & Francis blocks scripted downloads even for OA articles; fetch these via the Chalmers library proxy and drop them into the category folder.

- [active-inference] 2023 — World model learning from demonstrations with active inference  
  <https://link.springer.com/content/pdf/10.1007/978-3-031-28719-0_9.pdf>
- [crash-rate-benchmarks] 2026 — High-resolution urban fatal crash rate benchmarks for automated driving system assessment  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2026.2684002>
- [collision-avoidance-simulation] 2021 — Waymo simulated driving behavior in reconstructed fatal crashes  
  <https://doi.org/10.1016/j.aap.2021.106454>
- [safety-case-and-governance] 2025 — Developing a safety management system for the automated vehicle industry  
  <https://doi.org/10.4271/2025-01-8673>
- [injury-risk-and-vru] 2025 — A mechanistic approach to modeling omnidirectional motorcyclist injury risk  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2025.2570829>
- [injury-risk-and-vru] 2025 — Potential safety benefits associated with speed limit compliance in San Francisco and Phoenix  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2025.2538726>
- [injury-risk-and-vru] 2024 — Baseline vulnerable road user injury risk in multiple U.S. dense-urban driving environments  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2024.2364050>
- [injury-risk-and-vru] 2024 — Representative cyclist collision injury risk distributions for a dense-urban US ODD  
  <https://doi.org/10.4271/2024-01-2645>
- [injury-risk-and-vru] 2024 — Bridging the gap - Mechanistic-based cyclist injury risk curves  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2024.2400276>
- [injury-risk-and-vru] 2023 — Passenger and heavy vehicle collisions with pedestrians  
  <https://doi.org/10.1016/j.aap.2023.107139>
- [injury-risk-and-vru] 2022 — Methodology for determining maximum injury potential  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2022.2125231>
- [injury-risk-and-vru] 2021 — An omni-directional model of injury risk in planar crashes  
  <https://www.tandfonline.com/doi/pdf/10.1080/15389588.2021.1955108>
- [conflict-typology-and-scenarios] 2023 — Determination of functional scenarios for intersection collisions  
  <https://doi.org/10.1016/j.aap.2023.107326>
