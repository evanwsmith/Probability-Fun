"""
File: brownian.py
Author: Evan Smith
Date Created: 10/17/15
Date Last Modified: 10/17/15
Python Version: 2.7.10
Description: Several statistical functions and classes used to efficiently handle continuous Brownian variables
"""
import numpy as np

class DataPoint(object):
    ''' Represents a data point in 2D space '''
    def __init__(self, t, val):
        '''
        t   (float): time
        val (float): value
        '''
        self.t = t
        self.val = val

class BrownianVariableHistory(object):
    ''' Represents the set of known time value pairs for a particular brownian variable '''
    def __init__(self):
        pass

    def insertData(self, t, val):
        '''
        Inserts a data point into the history object

        t   (float): time
        val (float): value
        '''
        self._insertDataPoint(DataPoint(t, val))

    def getMartingaleRelevantPoints(self, t):
        '''
        Returns 2 data points. The first will be the data point with the largest 't' in the history that is still
        smaller than the given user provided argument 't'. The second will be the datapoint with the smallest 't'
        that is still larger than the user provided 't'. If one or both of the data points do not exist, this
        function will return None that data point's place.

        t       (float): time
        returns ((t1,val1), (t2,val2)) where t1, t2, val1, val2 are floats : 2 data points

        Ex: bh.getMartingaleRelevantPoints(3.1) == ((3.0, 0.07), (3.5, 0.21))
            bh.getMartingaleRelevantPoints(3.6) == ((3.5, 0.21), None)
        '''
        raise Exception('Not Yet Implemented Error')

    def _insertDataPoint(self, dataPoint):
        '''
        Inserts a data point object into the history object

        t   (float): time
        val (float): value
        '''
        raise Exception('Not Yet Implemented Error')

class BrownianVariable(object):
    def __init__(self, sigma, startTime=0, startVal=0, drift=0, history=BrownianHistory()):
        pass

    def getHistory(self):
        '''
        Gets a reference to the underlying history object containing all observed values
        of the brownian variable

        returns BrownianVariableHistory : history object
        '''
        raise Exception('Not Yet Implemented Error')

    def getPossibleValueDistr(self, t):
        '''
        Gets a numpy distribution object representing the pdf of the brownian value at a given t

        returns BrownianVariableHistory : history object
        '''
        raise Exception('Not Yet Implemented Error')

    def getValue(self, t, storeInHistory=true):
        '''
        Gets a value from the probability density function for a particular time t
        given the history of past values. This function will also add this data
        point to the history if storeInHistory is true

        storeInHistory (bool) : true if the generated value should be inserted into the history
        returns (float) : value
        '''
        raise Exception('Not Yet Implemented Error')
