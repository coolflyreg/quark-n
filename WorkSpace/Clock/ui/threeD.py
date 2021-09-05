#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import logging.config
from ui.core import UIManager, BaseUI
from ui.theme import *
from utils.GIFImage import GIFImage
from system.config import Config
import pygame
import math
import ctypes
from .component.cube import Cube
from .component.wave import Wave
from .component.globe import Globe
from utils.stepper import Stepper

logger = logging.getLogger('ui.welcome')


class ThreeDUI(BaseUI):

    showTick = 0

    anim_tick = 0
    showType = Stepper(minVal=0, maxVal=2, step=1, currentVal=0)
    
    object3Ds = [Cube(), Wave(), Globe()]
    isLeftMouseDown = False
    isMouseMoved = False

    def __init__(self, ui_index):
        super().__init__(ui_index)
        windowSize = UIManager().getWindowSize()
        self.canvasWidth = windowSize[0]
        self.canvasHeight = windowSize[1]

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
        if not isLongPress and pushCount == 1:
            self.showType.next()
        if isLongPress and longPressSeconds == 2:
            pass

    def onMouseDown(self, event):
        # print('onMouseDown', event)
        if event.button == 1:
            self.isLeftMouseDown = True
        self.object3Ds[self.showType.current()].mouseDown(event)
        pass

    def onMouseMove(self, event):
        # print('onMouseMove', event)
        if event.buttons[0]:
            self.isMouseMoved = True
        self.object3Ds[self.showType.current()].mouseMove(event)
        pass
    
    def onMouseUp(self, event):
        # print('onMouseUp', event)
        if event.button == 1:
            self.isLeftMouseDown = False
            if self.isMouseMoved is False:
                self.showType.next()
            self.isMouseMoved = False

        self.object3Ds[self.showType.current()].mouseUp(event)
        pass

    def onMouseWheel(self, event):
        self.object3Ds[self.showType.current()].mouseWheel(event)

    def on_shown(self):
        self.showTick = (time.time() * 1000)
        pass

    def on_hidden(self):
        pass

    def update(self, surface = None):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)

        # self.logger.debug('update {} {}'.format(self.rotationAngle, self.pointMap.A.value()))
        # if ((time.time() * 1000) - self.anim_tick) > 100:
        anim_tick = (time.time() * 1000)
        self.object3Ds[self.showType.current()].draw(surface)
        self.object3Ds[self.showType.current()].animationFrame()
        
        pass

    pass