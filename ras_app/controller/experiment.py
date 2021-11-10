import subprocess
import time
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from cgroupspy import trees
from jvm_sys import jvm_sys
from pymemcache.client.base import Client
import traceback
        

isCpu=True
sys = jvm_sys("../",isCpu)
nstep = 500
stime = 0.1
tgt=2
S=[]
nrep=4
tgt_v=[]
queue=[]

try:
    for rep in range(nrep):
        
        sys.startSys(isCpu)
        optS=None
        pop=np.random.randint(low=10, high=100)
        r=Client("localhost:11211")
        sys.startClient(pop)
        time.sleep(0.5)
    
        for i in tqdm(range(nstep)):
            state=sys.getstate(r)[0] 
            
            optS=[float(state[1])/tgt]
            
            r.set("t1_hw",optS[0])
            if(isCpu):
                sys.setU(optS[0],"tier1")
            
            queue.append(state[0])
            S.append(optS[0])
            tgt_v.append((1)/(1+0.1*tgt)*pop)
            #print(state,optS,tgt_v)
            time.sleep(stime)
        
        sys.stopClient()
        sys.stopSystem()
        
    plt.figure()
    plt.plot(queue,label="queuelength")
    plt.plot(tgt_v,color='r',linestyle='--',label="tgt")
    #plt.axhline(y=tgt_v, color='r', linestyle='--',label="tgt")
    plt.legend()
    plt.savefig("rt.pdf")
    
    plt.figure()
    plt.plot(S,label="cores")
    plt.savefig("core.pdf")
    
except Exception as ex:
    traceback.print_exception(type(ex), ex, ex.__traceback__)
    sys.stopClient()
    sys.stopSystem()

