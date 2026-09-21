import sys, os
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, REPO+r"\replication\causation"); sys.path.insert(0, REPO+r"\src")
import numpy as np
import re1_rear_end_criticality as R1
from aidriver import bicycle as bk
KPH=1/3.6
for ttc,dv in [(2,7),(2,42),(4,21),(7,42)]:
    for a_prev in (0.0, -0.1):
        agent=R1.make_agent(30.5,0,mode="certain")
        ego,other,traj,w=R1.settled(agent,30.5,30.5-dv*KPH,dv*KPH*ttc)[-1]
        agent.a_applied=a_prev
        best,G=agent._cem(ego,traj,w)
        et=bk.rollout(ego,best[None],agent.veh)[0]
        print(f"ttc{ttc} dv{dv} a_prev={a_prev}: first a {best[0,0]:+.2f}, min a over H {best[:,0].min():+.2f}, mean a {best[:,0].mean():+.2f}, max|omega| {np.abs(best[:,1]).max():.2f}, final y {et[-1,1]:+.2f} m, max|y| {np.abs(et[:,1]).max():.2f}, final v {et[-1,4]:.1f}")
