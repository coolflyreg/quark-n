#!/usr/bin/python3
# -*- coding: UTF-8 -*-

class Stepper(object):
    def __init__( self, minVal, maxVal,  step = 1, currentVal = None ):
        self.currentVal = currentVal
        self.minVal = minVal
        self.maxVal = maxVal
        self.step = step
        self.loop = True
        # print('min', self.minVal, 'max', self.maxVal, 'step', self.step, 'loop', self.loop, 'currentVal', self.currentVal)

    def set_loop(self, loop):
        self.loop = loop

    def next(self):
        self.currentVal = self.currentVal + self.step
        # print('self.currentVal before', self.currentVal)
        if self.step > 0:
            if self.currentVal > self.maxVal:
                if self.loop == True:
                    self.currentVal = self.minVal
                else:
                    self.currentVal = self.maxVal
                # print('self.currentVal after', self.currentVal)
        if self.step < 0:
            if self.currentVal < self.minVal:
                if self.loop == True:
                    self.currentVal = self.maxVal
                else:
                    self.currentVal = self.minVal
                # print('self.currentVal after', self.currentVal)
        return self.currentVal
    
    def current(self):
        return self.currentVal

    def set_current(self, value):
        self.currentVal = value

    pass