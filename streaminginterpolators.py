"""
File: streaminginterpolators.py
Author: Evan Smith
Date Created: 10/22/15
Date Last Modified: 10/23/15
Python Version: 2.7.10
Description: Classes to efficiently interpolate streamed data
"""
from abc import ABCMeta, abstractmethod
from bintrees import AVLTree


class StreamingInterpolatorBase(object):
    ''' Abstract base class for streaming interpolators '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def insert(self, x, val):
        ''' Register a datapoint '''
        return

    @abstractmethod
    def getInterpolatedVal(self, x):
        ''' Get the interpolated value for the given x '''
        return


class LinearStreamingInterpolator(StreamingInterpolatorBase):
    ''' Linear streaming interpolator '''

    def __init__(self):
        self._history = AVLTree()

    def insert(self, x, val):
        '''
        Register a datapoint

        x (float) : the x coordinate of the datapoint
        val (float): the rest of the datapoint
        '''
        self._history.insert(x, val)

    def getInterpolatedVal(self, x):
        '''
        Get the interpolated value for the given x

        x (float) : the x coordinate of the datapoint
        returns (float) : interpolated value
        '''
        if self._history.is_empty():
            return None

        leftX, leftVal = None, None
        rightX, rightVal = None, None
        if self._history.min_key() <= x:
            leftX, leftVal = self._history.floor_item(x)
            if leftX == x:
                return leftVal
        if self._history.max_key() >= x:
            rightX, rightVal = self._history.ceiling_item(x)
            if rightX == x:
                return rightVal

        # check if on edge
        if leftVal == None:
            return rightVal
        elif rightVal == None:
            return leftVal

        # find weighted average of the vals of the closest enclosing data
        # points
        intervalLength = abs(x - leftX) + abs(x - rightX)
        value = float(abs(x - rightX) * leftVal + abs(x - leftX)
                      * rightVal) / intervalLength
        return value


# FIXME: yea, so this is useless if restricted to 1 dimension
class NearestNeighborStreamingInterpolator(StreamingInterpolatorBase):
    ''' Nearest Neighbor 1D Streaming Interpolator '''

    def __init__(self):
        self._history = AVLTree()

    def insert(self, x, val):
        '''
        Register a datapoint

        x (float) : the x coordinate of the datapoint
        val (float): the rest of the datapoint
        '''
        self._history.insert(x, val)

    def getInterpolatedVal(self, x):
        '''
        Get the interpolated value for the given x

        x (float) : the x coordinate of the datapoint
        returns (float) : interpolated value
        '''
        if self._history.is_empty():
            return None

        # find the nearest point to the left and right
        leftX, leftVal = None, None
        rightX, rightVal = None, None
        if self._history.min_key() <= x:
            leftX, leftVal = self._history.floor_item(x)
        if self._history.max_key() >= x:
            rightX, rightVal = self._history.ceiling_item(x)

        # if there is only one neighbor, return it
        if leftVal == None:
            return rightVal
        elif rightVal == None:
            return leftVal

        # return the nearest neighbor
        if abs(x - leftX) < abs(x - rightX):
            return leftVal
        else:
            return rightVal
