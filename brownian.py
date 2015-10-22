"""
File: brownian.py
Author: Evan Smith
Date Created: 10/17/15
Date Last Modified: 10/22/15
Python Version: 2.7.10
Description: Several statistical functions and classes used to efficiently handle continuous Brownian variables
"""
import numpy as np
from scipy.stats import norm
from bintrees import RBTree


class BrownianVariableHistory(object):
    ''' Represents the set of known time value pairs for a particular brownian variable '''

    def __init__(self):
        self._historyTree = RBTree()

    def insertData(self, t, val):
        '''
        Inserts a data point into the history object

        t   (float): time
        val (float): value
        '''
        self._historyTree.insert(t, val)

    def getMartingaleRelevantPoints(self, t):
        '''
        Returns 2 data points. The first will be the data point with the largest 't' in the history that is still
        smaller than the given user provided argument 't'. The second will be the datapoint with the smallest 't'
        that is still larger than the user provided 't'. If one or both of the data points do not exist, this
        function will return None in that data point's place.

        t       (float): time
        returns ((t1,val1), (t2,val2)) where t1, t2, val1, val2 are floats : 2 data points

        Ex: bh.getMartingaleRelevantPoints(3.1) == ((3.0, 0.07), (3.5, 0.21))
            bh.getMartingaleRelevantPoints(3.6) == ((3.5, 0.21), None)
        '''
        leftPoint = self._historyTree.prev_item(t)
        rightPoint = self._historyTree.succ_item(t)
        return leftPoint, rightPoint


class BrownianVariable(object):

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

        returns scipy.stats.rv_continuous : distribution
        '''
        leftDataPoint, rightDataPoint = self.self._history.getMartingaleRelevantPoints()
        if not (leftDataPoint or rightDataPoint):
            # should only happen if the history invariant has been violated
            raise Exception('Brownian History Corruption Error')

        elif not rightDataPoint:
            # find the probability distribution given past data
            prevT, prevVal = leftDataPoint
            mean = ((t - prevT) * self._drift + prevVal)
            standardDev = ((t - prevT)**0.5 * self._sigma)
            return norm(loc=mean, scale=standardDev)

        elif not leftDataPoint:
            # run back the clock, and finding a probability distribution of the
            # past given the future
            futrT, futrVal = rightDataPoint
            mean = ((t - futrT) * self._drift + futrVal)
            standardDev = ((futrT - t)**0.5 * self._sigma)
            return norm(loc=mean, scale=standardDev)

        else:
            # given past and future data, get the probability distribution of a brownian variable sometime in
            # the present
            prevT, prevVal = leftDataPoint
            futrT, futrVal = rightDataPoint

            meanLeft = ((t - prevT) * self._drift + prevVal)
            meanRight = ((t - futrT) * self._drift + futrVal)
            standardDevLeft = ((t - prevT)**0.5 * self._sigma)
            standardDevRight = ((futrT - t)**0.5 * self._sigma)

            # new probability distribution is equal to the scaled
            # multiplication of the two normal distributions, which happens to
            # be itself normal
            mean = (standardDevLeft**(-2) * meanLeft + standardDevRight**(-2)
                    * meanRight) / (standardDevLeft**(-2) + standardDevRight**(-2))
            standardDev = ((standardDevLeft**2 * standardDevRight**2) /
                           (standardDevLeft**2 + standardDevRight**2))**0.5
                           
            return norm(loc=mean, scale=standardDev)

    def getValue(self, t, storeInHistory=True):
        '''
        Gets a value from the probability density function for a particular time t
        given the history of past values. This function will also add this data
        point to the history if storeInHistory is true

        storeInHistory (bool) : true if the generated value should be inserted into the history
        returns (float) : value
        '''
        distr = self.getPossibleValueDistr(t)
        val = distr.rvs()
        if storeInHistory:
            self._history.insertData(t, val)
        return val
