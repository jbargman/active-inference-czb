# Bärgman, Smith & Werneke (2015) — *Quantifying drivers' comfort-zone and dread-zone boundaries in LTAP/OD scenarios*

*Transportation Research Part F 35, 170–184. Filed 2026-09-02 as
`papers/comfort-zone-boundaries/2015 - Bargman Smith Werneke - Quantifying drivers comfort-zone
and dread-zone boundaries in LTAP-OD (TRF 35).pdf`. The study's run protocol is in
`external/02_LTAPOD_DBIN/` (not tracked; see `external/README.md`). This is the project's first
real-driving comfort-zone dataset, and it is the same manoeuvre as the video LTAP study, so it
is the paradigm comparison the roadmap has been asking for.*

**Question.** Where are drivers' comfort-zone and dread-zone boundaries when turning left
across the path of an oncoming vehicle, and how do they differ?

**Design.** Test track (Vårgårda airfield), an artificial T-intersection with barriers against
corner-cutting. The oncoming vehicle is a self-propelled full-size balloon car on a rail at a
constant 50 km/h; the subject vehicle (Volvo V50) is brought to 50 km/h by a throttle robot,
braked by a brake robot from about 60 m, and released to the driver about 20 m before the
intersection centre, after which the driver decides to turn before the balloon car (Go) or
after it (No-Go). The manipulated variable is **SetPET**: the post-encroachment time that a
reference trajectory (the average of nine pilot turns) would produce, set through the relative
start times of the two robots. Twenty-two participants (17 men; 25–61 years; Autoliv and
Volvo employees), within-subject, comfortable condition always before the hurried one.
Comfort condition: four preset SetPETs (4, 3, 2, 1 s, Latin square), then a method-of-
adjustment staircase (up 0.4 s to the first Go, down 0.2 s to the next No-Go); hurried
condition: the same staircase started 1 s below the comfort No-Go. Each run ends with five
15-point self-reports (comfort, risk, decision difficulty, hesitation, would-decide-the-same).

**Boundaries as the paper defines them.** The comfort-zone boundary is the observed PET at
the driver's last Go in the comfortable condition; the dread-zone boundary the same in the
hurried condition. The dread zone is the paper's new concept: a margin drivers will not enter
voluntarily even with extra motives.

**Results.** Median (mean) PET at the comfort boundary 2.26 (2.22) s, at the dread boundary
1.50 (1.47) s, every driver shorter when hurried (Wilcoxon Z = 3.89); maximum lateral
acceleration 3.23 against 4.12 m/s². PET_DZB ≈ −0.07 + 0.69 × PET_CZB (r² = 0.57): hurried
drivers accept about 70% of their comfortable margin, whatever it is; lateral acceleration
rises by a constant ≈ 1.1 m/s². A median split on the DBQ improves the prediction of the dread
boundary (rule-following drivers pushed further when hurried, which the authors flag as
counter-intuitive and in need of replication). Self-reports: the turn at the dread boundary
is rated less comfortable, riskier, harder and more hesitant; the "would decide the same"
item does not differ. No order effect in the four preset runs. PET data corrupted for two
drivers (20 sets of PET, 22 of lateral acceleration).

**What it is for us.** Real turns, the same manoeuvre as the video LTAP study (study 1,
Random design, 50 and 70 km/h), a manipulated PET on both, and a per-driver staircase that
brackets each driver's Go/No-Go switch. So it gives (1) the video-to-driving offset of the
comfort boundary on one scenario (the number the data-requirements document asks for), (2) a
second estimate of the between-driver spread of levels, (3) a dread boundary, which no video
study has, and (4) a graded comfort rating against PET to set beside the video's perceived-
safety rating. It cannot separate time from distance (one oncoming speed), and its
participants and era differ from the video study's. Analysis: `replication/czb/ltapod_testtrack.py`
→ `out/ltapod_testtrack.md` (card TT.1).

**Caveats the paper itself states.** Fixed condition order (habituation may shrink the dread
boundary); three to four hours in the vehicle; the staircase makes sequence effects across
drivers unassessable; PET is post-hoc, not perceived; the balloon car is not a car.
