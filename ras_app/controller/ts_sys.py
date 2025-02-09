from system_int import system_interface
import time
import numpy as np
import subprocess
from cgroupspy import trees
from pymemcache.client.base import Client
import os
import psutil
import requests as req
import sys
import docker
import tarfile
from io import BytesIO
import re
from stats import ConfInterval
from log_handler import LogHandler
        

class ts_sys(system_interface):
    
    sysRootPath = None
    sys = None
    client = None
    croot = None
    cgroups = None
    period = 1000
    keys = ["think", "e1_bl", "e1_ex", "t1_hw"]
    javaCmd=None
    dck_client = None
    containers = None
    
    systemLogHandler = None
    
    def __init__(self, sysRootPath):
        
        try:
            self.javaCmd = os.environ['JAVA_HOME'] + "/bin/java"
        except:
            raise ValueError("Need to setup JAVA_HOME env variable")
        
        self.sysRootPath = sysRootPath
        self.systemLogHandler = LogHandler(30)
        #if(isCpu):
        #    self.initCgroups()
        self.dck_client = docker.from_env()
    
    def startClient(self, pop):
        r=Client("localhost:11211")
        r.set("stop","0")
        r.set("started","0")
        r.close()
        
        
        subprocess.Popen([self.javaCmd, "-Xmx4G",
                         "-Djava.compiler=NONE", "-jar",
                         '%sras_teastore/target/ras_teastore-0.0.1-SNAPSHOT-jar-with-dependencies.jar' % (self.sysRootPath),
                         '--initPop', '%d' % (pop), '--jedisHost','localhost', '--webuiHost','localhost:8080',
                         '--queues','[\"think\", \"e1_bl\", \"e1_ex\", \"t1_hw\"]'])
        
        self.waitClient()
        
        self.client = self.findProcessIdByName("teastore-0.0.1")[0]
        
    
    def stopClient(self):
        if(self.client!=None):
            r=Client("localhost:11211")
            r.set("stop","1")
            r.close()
            
            try:
                self.client.wait(timeout=2)
            except psutil.TimeoutExpired as e:
                print("terminate client forcibly")
                self.client.terminate()
                self.client.kill()
                self.client=None
        
    def getNetworkCne(self):
        net=None
        try:
            net=self.dck_client.networks.get("teastore-network")
        except docker.errors.NotFound:
            net=self.dck_client.networks.create("teastore-network")
        return net
    
    def waitRunning(self,cnt):
        while(cnt.status!="running"):
            time.sleep(0.2)
            cnt.reload()
        print("Cnt %s is running"%(cnt.name))
    
    def startSys(self):
        #cpuEmu = 0 if(isCpu) else 1
        
        self.sys = []
        subprocess.Popen(["memcached","-c","2048","-t","20"])
        self.waitMemCached()
        self.sys.append(self.findProcessIdByName("memcached")[0])
        
        self.containers = dict()
        self.containers["registry"] = (self.dck_client.containers.run(image="giuliogarbi/teastore-registry",
                              auto_remove=True,
                              detach=True,
                              name="registry",
                              network="teastore-network",
                              stop_signal="SIGINT"))
        self.waitRunning(self.containers["registry"])
        self.containers["db"] = (self.dck_client.containers.run(image="giuliogarbi/teastore-db",
                              auto_remove=True,
                              detach=True,
                              name="db",
                              network="teastore-network",
                              stop_signal="SIGINT"))
        self.waitRunning(self.containers["db"])
        self.containers["persistence"] = (self.dck_client.containers.run(image="giuliogarbi/teastore-persistence",
                              auto_remove=True,
                              detach=True,
                              name="persistence",
                              network="teastore-network",
                              stop_signal="SIGINT",
                              environment={"HOST_NAME":"persistence", "REGISTRY_HOST": "registry", "DB_HOST": "db", "DB_PORT": "3306"}))
        self.waitRunning(self.containers["persistence"])
        for h in ["auth","image","recommender"]:
            self.containers[h] = (self.dck_client.containers.run(image="giuliogarbi/teastore-"+h,
                                  auto_remove=True,
                                  detach=True,
                                  name=h,
                                  network="teastore-network",
                                  stop_signal="SIGINT",
                                  environment={"HOST_NAME":h, "REGISTRY_HOST": "registry"}))
            self.waitRunning(self.containers[h])
        self.containers["webui"] = (self.dck_client.containers.run(image="giuliogarbi/teastore-webui",
                                  auto_remove=True,
                                  detach=True,
                                  name="webui",
                                  network="teastore-network",
                                  stop_signal="SIGINT",
                                  ports={"8080/tcp":8080},
                                  environment={"HOST_NAME":"webui", "REGISTRY_HOST": "registry"}))
        self.waitRunning(self.containers["webui"])
    
    def findProcessIdByName(self,processName):
        
        
        '''
        Get a list of all the PIDs of a all the running process whose name contains
        the given string processName
        '''
        listOfProcessObjects = []
        # Iterate over the all the running process
        for proc in psutil.process_iter():
           if(proc.status()=="zombie"):
               continue
           try:
               pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
               # Check if process name contains the given name string.
               if processName.lower() in pinfo['name'].lower() or processName.lower() in " ".join(proc.cmdline()).lower():
                   listOfProcessObjects.append(proc)
           except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess):
               pass
        if(len(listOfProcessObjects)!=1):
            print(len(listOfProcessObjects))
            raise ValueError("process %s not found!"%processName)
        return listOfProcessObjects;
    
    def stopSystem(self):
        if(self.containers is not None):
            for c in self.containers.values():
                print("killing %s"%(c.name))
                c.kill()
        if(self.sys is not None):
            for i in range(len(self.sys),0,-1):
                proc=self.sys[i-1]
                print("killing %s"%(proc.name()+" "+"".join(proc.cmdline())))
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except psutil.TimeoutExpired as e:
                    proc.kill()
                
                
        self.sys=None
    
    def getstate(self, monitor):

        N = int((len(self.keys) - 2) / 2)
        str_state = [monitor.get(self.keys[i]) for i in range(len(self.keys))]
        estate = [float(str_state[i]) for i in range(len(self.keys))]
        try:
            astate = [float(str_state[0].decode('UTF-8'))]
            gidx = 1;
            for i in range(0, N):
                astate.append(float(str_state[gidx].decode('UTF-8')) + float(str_state[gidx + 1].decode('UTF-8')))
                if(float(str_state[gidx]) < 0 or float(str_state[gidx + 1]) < 0):
                    raise ValueError("Error! state < 0")
                gidx += 2
        except:
            print(time.asctime())
            for i in range(len(self.keys)):
                print(str_state[i], self.keys[i])
        
        return [astate,estate]
    
    def waitWebui(self, webui_addr):
        print("waitig for webui ready")
        limitTrials = 10000
        limitSuccess = 10
        atpt=0
        succ=0
        while(atpt<limitTrials and succ < limitSuccess):
            try:
                r = req.get('http://'+webui_addr+"/tools.descartes.teastore.webui/")
                succ += 1
                print("webui replies")
                time.sleep(1)
            except:
                time.sleep(1)
            finally:
                atpt+=1
        
        if(succ >= limitSuccess):
            print("webui is ready")
        else:
            raise ValueError("error while connceting to tier1")
    
    def waitClient(self):
        connected=False
        limit=10000
        atpt=0
        base_client = Client(("localhost", 11211))
        while(atpt<limit and (base_client.get("started")==None or base_client.get("started").decode('UTF-8')=="0")):
           time.sleep(0.2)
           atpt+=1
        
        time.sleep(2)
            
        
    def waitMemCached(self):
        connected = False
        base_client = Client(("localhost", 11211))
        for i in range(1000):
            try:
                base_client.get('some_key')
                connected = True
                base_client.close()
                break
            except ConnectionRefusedError:
                time.sleep(0.2)
        base_client.close()
        
        if(connected):
            print("connected to memcached")
        else:
            raise ValueError("Impossible to connected to memcached")
        
        time.sleep(0.5)
    
    
    def initCgroups(self): 
        self.cgroups={"tier1":{"name":"t1","cg":None}}
        
        p= subprocess.Popen(["cgget", "-g", "cpu,cpuset:t1"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if(str(err).find("Cgroup does not exist") != -1):
            subprocess.check_output(["sudo", "cgcreate", "-g", "cpu,cpuset:t1","-a","%s:%s"%(os.getlogin(),os.getlogin()),
                                     "-t","%s:%s"%(os.getlogin(),os.getlogin())])
    
    def setU(self,RL,cnt_name):
        
        if(self.cgroups[cnt_name]["cg"]== None or self.cgroups[cnt_name]["cg"]["cpu"]== None):
            print("get cgrop for %s"%(self.cgroups[cnt_name]["name"]))
            
            if(self.cgroups[cnt_name]["cg"]== None):
                self.cgroups[cnt_name]["cg"]={}
                
            self.cgroups[cnt_name]["cg"]["cpu"] = trees.Tree().get_node_by_path('/cpu/%s'%(self.cgroups[cnt_name]["name"]))
            
        quota=int(np.round(RL * self.period))
    
        self.cgroups[cnt_name]["cg"]["cpu"].controller.cfs_period_us=self.period
        self.cgroups[cnt_name]["cg"]["cpu"].controller.cfs_quota_us = quota
    
    def setCpuset(self,cpus,cnt_name):
    
        if(self.cgroups[cnt_name]["cg"]== None or self.cgroups[cnt_name]["cg"]["cpuset"]== None):
            print("get cgrop for %s"%(self.cgroups[cnt_name]["name"]))
            
            if(self.cgroups[cnt_name]["cg"]== None):
                self.cgroups[cnt_name]["cg"]={}
                
            self.cgroups[cnt_name]["cg"]["cpuset"] = trees.Tree().get_node_by_path('/cpuset/%s'%(self.cgroups[cnt_name]["name"]))
    
        self.cgroups[cnt_name]["cg"]["cpuset"].controller.cpus=cpus
        self.cgroups[cnt_name]["cg"]["cpuset"].controller.mems=[0]
        
    
    def getLogs(self):
        logs = dict()
        for name in ["persistence","auth","image","webui","recommender"]:
            c = self.containers[name]
            logsTxt = []
            try:
                bits, stat = c.get_archive("/usr/local/tomcat/accesslogs")
                with BytesIO() as f:
                    for chunk in bits:
                        f.write(chunk)
                    f.seek(0)
                    with tarfile.open(fileobj=f, mode='r') as tf:
                        logfiles = [fname for fname in tf.getnames() if re.match(r'accesslogs/.+', fname)]
                        for fname in logfiles:
                            with tf.extractfile(fname) as logfile:
                                logsTxt.append((logfile.read()))
            except docker.errors.NotFound:
                pass
            logs[name] = logsTxt
        return logs
    
    def getRT(self,monitor,taskname):
        #qui si deve estendere per prendere tutti i response time
        RT=monitor.get("rt_"+taskname)
        CIlow=monitor.get("lowCI_rt_"+taskname)
        CIup=monitor.get("upCI_rt_"+taskname)
        N=monitor.get("batches_rt_"+taskname)
        if(RT is not None):
            RT=float(RT.decode('UTF-8'))/10**9
        if(CIlow is not None):
            CIlow=float(CIlow.decode('UTF-8'))/10**9
        if(CIup is not None):
            CIup=float(CIup.decode('UTF-8'))/10**9
        if(N is not None):
            N=int(N.decode('UTF-8'))
        
        return ConfInterval(RT, (CIlow, CIup), N)
    
    def getThr(self,monitor,taskname):
        #qui si deve estendere per prendere tutti i response time
        Thr=monitor.get("thr_"+taskname)
        CIlow=monitor.get("lowCI_thr_"+taskname)
        CIup=monitor.get("upCI_thr_"+taskname)
        N=monitor.get("batches_thr_"+taskname)
        if(Thr is not None):
            Thr=float(Thr.decode('UTF-8'))
        if(CIlow is not None):
            CIlow=float(CIlow.decode('UTF-8'))
        if(CIup is not None):
            CIup=float(CIup.decode('UTF-8'))
        if(N is not None):
            N=int(N.decode('UTF-8'))
        
        return ConfInterval(Thr, (CIlow, CIup), N)
       
            
if __name__ == "__main__":
    try:
        nCli = int(sys.argv[1])
        mre = float(sys.argv[2])
        ts_sys = ts_sys("../")
        #    jvm_sys.setCpuset([2],"tier1") 
        
        for i in range(1):
            
            
            ts_sys.startSys()
            ts_sys.waitWebui('localhost:8080')
            ts_sys.startClient(nCli)
            
            startTimeObservation = time.time()
            
            g = Client("localhost:11211")
            g.set("t1_hw","1")
            g.set("t1_sw","1")
            #jvm_sys.setU(1.0,"tier1")
            #jvm_sys.setCpuset([2],"tier1")    
            mnt = Client("localhost:11211")
            
            X=[]
            acceptableStats = False
            print("-"*85)
            while not acceptableStats:
                time.sleep(20)
                endTimeObservation = time.time()
                # state=jvm_sys.getstate(mnt)
                # print(state[0],i)
                # X.append(state[0][0])
                #
                # if(isCpu):
                #     jvm_sys.setU(10,"tier1")
                logs = ts_sys.getLogs()
                ts_sys.systemLogHandler.addLogs(logs, startTimeObservation, endTimeObservation)
                startTimeObservation = endTimeObservation
                rtOutCli=ts_sys.getRT(mnt,"Client")
                thrOutCli=ts_sys.getThr(mnt,"Client")
                ts_sys.systemLogHandler.updateStats()
                rtCI = ts_sys.systemLogHandler.getRT()
                thrCI = ts_sys.systemLogHandler.getThr()
                
                acceptableStats = rtOutCli.isAcceptable(minBatches=31, maxRelError=mre) and \
                    thrOutCli.isAcceptable(minBatches=31, maxRelError=mre) and \
                    all(ci.isAcceptable(minBatches=31, maxRelError=mre) for ci in rtCI.values())
                print(acceptableStats, nCli)
                print('rt',"Client", rtOutCli.mean, rtOutCli.CI, rtOutCli.Nbatches, 'max(CI)-mean:', rtOutCli.getRelError()*100,'%')
                for (ms_ep, ci) in rtCI.items():
                    print('rt', ms_ep, ci.mean, ci.CI, ci.Nbatches, 'max(CI)-mean:', ci.getRelError()*100,'%')
                print('thr',"Client", thrOutCli.mean, thrOutCli.CI, thrOutCli.Nbatches, 'max(CI)-mean:', thrOutCli.getRelError()*100,'%')
                for (ms_ep, ci) in thrCI.items():
                    print('thr', ms_ep, ci.mean, ci.CI, ci.Nbatches, 'max(CI)-mean:', ci.getRelError()*100,'%')
                sys.stdout.flush()
                print("-"*85)
            
           
            mnt.close()
            
            #print(np.mean(X))
    finally:
        ts_sys.stopClient()
        ts_sys.stopSystem()
        g.close()
        
