import numpy as np
import scipy.stats as st

class ConfInterval:
    def __init__(self, mean, CI, Nbatches):
        self.mean = mean
        self.CI = CI
        self.Nbatches = Nbatches
        
    def isAcceptable(self, minBatches=30, maxAbsError=None, maxRelError=None):
        maxAbsError = float('inf') if maxAbsError is None else maxAbsError
        maxRelError = float('inf') if maxRelError is None else maxRelError
        
        if self.CI is None or self.mean is None or self.Nbatches is None:
            return False
        
        absError = abs(self.CI[1]-self.mean)
        relError = absError/abs(self.mean)
        
        return self.Nbatches >= minBatches and absError <= maxAbsError and relError <= maxRelError
    
    def getRelError(self):
        if self.CI is None or self.mean is None:
            return float('NaN')
        absError = abs(self.CI[1]-self.mean)
        relError = absError/abs(self.mean)
        return relError 

class BatchMeans:
    def __init__(self, batchSize):
        self.unprocessedSamples = []
        self.lastBatchSum = 0.0
        self.lastBatchLen = 0
        self.totalNumCompletedBatches = 0
        self.meanOfBatch = [] # skip first batch
        self.lastMOB_N = -1;
        self.batchSize = batchSize;
        self.CI = ConfInterval(float('NaN'), (float('NaN'), float('NaN')), 0)
        self.confLvl = 0.95
        
    def add(self, x):
        self.unprocessedSamples.append(x)
        
    def processSamples(self): 
        newSamples = self.unprocessedSamples
        self.unprocessedSamples = []
        for x in newSamples:
            self.lastBatchSum += x
            self.lastBatchLen += 1
            if self.lastBatchLen == self.batchSize:
                if self.totalNumCompletedBatches > 0:
                    lastBatchMean = self.lastBatchSum/self.batchSize
                    self.meanOfBatch.append(lastBatchMean)
                self.lastBatchSum = 0
                self.lastBatchLen = 0
                self.totalNumCompletedBatches += 1
    
    def updateStats(self):
        self.processSamples()
        self.computeCI()
    
    def computeCI(self):
        if self.lastMOB_N != len(self.meanOfBatch):
            self.lastMOB_N = len(self.meanOfBatch)
            if len(self.meanOfBatch) >= 2:
                mean = np.mean(self.meanOfBatch)
                CI = st.t.interval(self.confLvl, len(self.meanOfBatch) - 1, loc=np.mean(self.meanOfBatch), scale=st.sem(self.meanOfBatch))
                self.CI = ConfInterval(mean, CI, self.totalNumCompletedBatches)
            else:
                self.CI = ConfInterval(float('NaN'), (float('NaN'), float('NaN')), self.totalNumCompletedBatches)