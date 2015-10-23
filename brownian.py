"""
File: brownian.py
Author: Evan Smith
Date Created: 10/17/15
Date Last Modified: 10/22/15
Python Version: 2.7.10
Description: Several statistical functions and classes used to efficiently
             handle continuous Brownian variables
"""
from scipy.stats import norm
from bintrees import RBTree


class BrownianVariableHistory(object):
    ''' Represents the set of known time value pairs for a particular Brownian variable '''

    def __init__(self):
        self._historyTree = RBTree()

    def insertData(self, t, val):
        '''
        Inserts a data point into the history object

        t (float) : time
        val (float) : value
        '''
        self._historyTree.insert(t, val)

    def getMartingaleRelevantPoints(self, t):
        '''
        Returns 2 data points. The first will be the data point with the
        largest 't' in the history that is still smaller than the given user
        provided argument 't'. The second will be the datapoint with the
        smallest 't' that is still larger than the user provided 't'. If one
        or both of the data points do not exist, this function will return
        None in that data point's place.

        t (float) : time
        returns ((t1,val1), (t2,val2)) where t1, t2, val1, val2 are floats : 2 data points

        Ex: bh.getMartingaleRelevantPoints(3.1) == ((3.0, 0.07), (3.5, 0.21))
            bh.getMartingaleRelevantPoints(3.6) == ((3.5, 0.21), None)
        '''
        if self._historyTree.is_empty():
            return None, None

        leftPoint = None
        rightPoint = None
        if self._historyTree.min_key() <= t:
            leftPoint = self._historyTree.floor_item(t)
        if self._historyTree.max_key() >= t:
            rightPoint = self._historyTree.ceiling_item(t)
        return leftPoint, rightPoint


class BrownianVariable(object):
    ''' Random variable that has a Brownian motion '''

    def __init__(self, sigma, startTime=0, startVal=0, drift=0, history=BrownianVariableHistory()):
        self._sigma = sigma
        self._sigmastartTime = startTime
        self._startVal = startVal
        self._drift = drift
        self._history = history
        # add the seed point into the history
        self._history.insertData(startTime, startVal)

    def getHistory(self):
        '''
        Gets a reference to the underlying history object containing all observed values
        of the brownian variable

        returns BrownianVariableHistory : history object
        '''
        return self._history

    def getPossibleValueDistr(self, t):
        '''
        Gets a scipy distribution object representing the pdf of the brownian value at a given t

        t (float) : time
        returns (scipy.stats.rv_continuous) : probability distribution
        '''
        leftDataPoint, rightDataPoint = self._history.getMartingaleRelevantPoints(t)
        if not (leftDataPoint or rightDataPoint):
            # should only happen if the history invariant has been violated
            raise Exception('Brownian History Corruption Error')

        prevT, prevVal = None, None
        if leftDataPoint:
            prevT, prevVal = leftDataPoint
            if prevT == t:
                return norm(loc=prevVal, scale=0)

        futrT, futrVal = None, None
        if rightDataPoint:
            futrT, futrVal = rightDataPoint
            if futrT == t:
                return norm(loc=futrVal, scale=0)

        mean, standardDev = None, None
        if not rightDataPoint:
            # find the probability distribution given past data
            mean, standardDev = self._getDistribution(
                t, prevT, prevVal, self._sigma, self._drift)
        elif not leftDataPoint:
            # run back the clock, and finding a probability distribution of the
            # past given the future
            mean, standardDev = self._getDistribution(
                t, futrT, futrVal, self._sigma, self._drift)
        else:
            # given past and future data, get the probability distribution of a
            # brownian variable sometime in between
            mean, standardDev = self._getSandwichDistribution(
                t, prevT, prevVal, futrT, futrVal, self._sigma, self._drift)
        return norm(loc=mean, scale=standardDev)

    @staticmethod
    def _getSandwichDistribution(t, baseTLeft, baseValLeft, baseTRight, baseValRight, sigma, drift):
        '''
        Gets a value probability distribution of a Brownian variable given two reference points

        t (float) : time
        baseTLeft (float) : reference point 1 time
        baseValLeft (float) : reference point 1 value
        baseTRight (float) : reference point 2 time
        baseValRight (float) : reference point 2 value
        sigma (float) : standard deviation
        drift (float) : drift rate
        returns (float, float) : (mean, standardDev) of the resulting distribution
        '''
        meanLeft, standardDevLeft = BrownianVariable._getDistribution(
            t, baseTLeft, baseValLeft, sigma, drift)
        meanRight, standardDevRight = BrownianVariable._getDistribution(
            t, baseTRight, baseValRight, sigma, drift)

        # new probability distribution is equal to the scaled
        # multiplication of the two normal distributions, which happens to
        # be itself normal
        mean = (standardDevLeft**(-2) * meanLeft + standardDevRight**(-2)
                * meanRight) / (standardDevLeft**(-2) + standardDevRight**(-2))
        standardDev = ((standardDevLeft**2 * standardDevRight**2) /
                       (standardDevLeft**2 + standardDevRight**2))**0.5
        return mean, standardDev

    @staticmethod
    def _getDistribution(t, baseT, baseVal, sigma, drift):
        '''
        Gets a value probability distribution of a Brownian variable given a
        single reference point

        t (float) : time
        baseT (float) : reference point time
        baseVal (float) : reference point value
        sigma (float) : standard deviation
        drift (float) : drift rate
        returns (float, float) : (mean, standardDev) of the resulting distribution
        '''
        mean = ((t - baseT) * drift + baseVal)
        standardDev = (abs(t - baseT)**0.5 * sigma)
        return mean, standardDev

    def getValue(self, t, storeInHistory=True):
        '''
        Gets a value from the probability density function for a particular time t
        given the history of past values. This function will also add this data
        point to the history if storeInHistory is true

        t (float) : time
        storeInHistory (bool) : true if the generated value should be inserted into the history
        returns (float) : value
        '''
        distr = self.getPossibleValueDistr(t)
        val = distr.rvs()
        if storeInHistory:
            self._history.insertData(t, val)
        return val

    def getValues(self, tList):
        '''
        Gets values of the brownian variable for all times listed in tList

        tList (list of floats) : list of times
        returns (list of floats) : values
        '''
        # Let's sort for optimal performance creating the distribtions
        sortedIdxs = [e[0]
                      for e in sorted(enumerate(tList), key=lambda x: x[1])]
        retVals = [None] * len(tList)
        for i in sortedIdxs:
            retVals[i] = self.getValue(tList[i], storeInHistory=True)
        return retVals
