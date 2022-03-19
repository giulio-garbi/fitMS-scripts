from stats import BatchMeans
import re

class LogHandler:
    def __init__(self, batch_size):
        self.rt = dict()
        self.batch_size = batch_size
        
    def newRT(self, ms_ep, rtS):
        if ms_ep not in self.rt:
            self.rt[ms_ep] = BatchMeans(self.batch_size)
        self.rt[ms_ep].add(rtS)
        
    def addLogs(self, logFilePerMserv, exitTimeFromS, exitTimeToS):
        for (ms,logFiles) in logFilePerMserv.items():
            for log in logFiles:
                if len(log)>0:
                    for line in log.splitlines():
                        mtc = re.search(br'end_ms:(?P<end_ms>\d+) rt_usec:(?P<rt_usec>\d+) code:.+ req:"(?P<req>.+)"', line)
                        if mtc is not None:
                            exitTimeS = float(mtc.group('end_ms'))/1000.0
                            if exitTimeS >= exitTimeFromS and exitTimeS < exitTimeToS:
                                rtS = int(mtc.group('rt_usec'))/1000000.0
                                endpoint = mtc.group('req').decode('utf-8')
                                epParts = endpoint.split(" ")
                                if epParts[0] == 'GET':
                                    #GET method: remove querystring
                                    epParts[1] = epParts[1].split("?")[0]
                                ms_ep = ms+"-"+epParts[0]+"_"+epParts[1]
                                self.newRT(ms_ep, rtS)
                        else:
                            print("Invalid log line:", line)
                            
    def updateStats(self):
        for b in self.rt.values():
            b.updateStats()
            
    def getRT(self):
        return {k:self.rt[k].CI for k in self.rt}