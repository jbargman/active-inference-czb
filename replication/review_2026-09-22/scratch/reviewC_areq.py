import sys
REPO=r"C:\Users\bargman\OneDrive - Chalmers\1_Work\1_Code\WaymoActiveInference"
sys.path.insert(0, REPO+r"\src")
import numpy as np
from aidriver.preferences import PreferenceParams, required_deceleration, log_preference_terms, pragmatic_deficit
p=PreferenceParams(v_desired=30.5)
L=p.vehicle.length; print("veh length",L,"dt",p.vehicle.dt)
for thw in (0.5,1.0,1.5,3.5):
    gap=30.5*thw
    obs=dict(v=30.5,a=0.0,dx=gap+L,dy=0.0,v_other=30.5,a_other=0.0)
    obs2=dict(obs,a=-0.1)
    print(thw,gap,"a_req a=0:",float(required_deceleration(obs,p)),"a=-0.1:",float(required_deceleration(obs2,p)))
# dx read as bumper gap instead (no +L)
obs=dict(v=30.5,a=0.0,dx=15.25,dy=0.0,v_other=30.5,a_other=0.0)
print("dx=gap (no length):",float(required_deceleration(obs,p)))
# gap at which p_safe fires at 30.5 m/s, dv=0
for gap in np.arange(5,16,0.5):
    o=dict(v=30.5,a=-0.1,dx=gap+L,dy=0.0,v_other=30.5,a_other=0.0)
    if required_deceleration(o,p) < -8:
        last=gap
print("p_safe fires for gap <=",last,"m = THW",last/30.5)
# the 23 nats: coasting policy cost
dt=0.2;H=30
k=np.arange(1,H+1)
speed=0.5*((0.1*dt*k)/0.5)**2; acc=0.5*(0.1/0.1)**2*np.ones(H)
print("speed sum",speed.sum(),"accel sum",acc.sum(),"total",speed.sum()+acc.sum())
