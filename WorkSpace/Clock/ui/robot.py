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

logger = logging.getLogger('ui.robot')

class RobotMessage(object):

    text = None
    renderedText = []
    totalHeight = 0
    color = color_white
    offset_line = 0

    def __init__(self, text, color):
        self.renderedText = []
        self.text = text
        self.color = color
        self.offset_line = 0
        usedFont = zhSmallFont
        txtSize = zhSmallFont.size(text)

        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]

        calcHeight = (txtSize[0] / window_width * txtSize[1]) + txtSize[1]
        # logger.debug('txtSize %d', txtSize)
        # logger.debug('calc height %d', calcHeight)
        loop = 0
        usedFontSize = 30
        while txtSize[0] > window_width and (calcHeight + 15) > (window_height):
            # usedFontSize = usedFontSize * ((window_height - 15) / calcHeight)
            usedFontSize = usedFontSize - 2
            # logger.debug('usedFontSize %d, %d', usedFontSize, int(usedFontSize))
            usedFont = pygame.font.Font(zhFontPath, int(usedFontSize))
            usedFont.set_bold(True)
            txtSize = usedFont.size(text)
            calcHeight = round(txtSize[0] / window_width * txtSize[1]) + txtSize[1]

            # logger.debug('  txtSize %d', txtSize)
            # logger.debug('  calc height %d', calcHeight)
            loop = loop + 1
            if (loop > 20 or usedFontSize <= 12):
                break

        txtSize_height = txtSize[1]
        if (txtSize[0] <= window_width):
            self.renderedText.append(usedFont.render(self.text, True, self.color))
            self.totalHeight = self.totalHeight + self.renderedText[0].get_height()
        else:
            start = 0
            end = 0
            while end <= len(self.text):
                txtSize = usedFont.size(self.text[start: end + 1])
                if txtSize[0] > window_width:
                    self.renderedText.append(usedFont.render(self.text[start : end], True, self.color))
                    start = end
                    self.totalHeight = self.totalHeight + txtSize[1]
                    # logger.debug('self.renderedText[len(self.renderedText) - 1].get_height()', self.renderedText[len(self.renderedText) - 1].get_height(), txtSize[1])
                else:
                    end = end + 1

                pass
            if end > start:
                self.renderedText.append(usedFont.render(self.text[start : end], True, self.color))
                self.totalHeight = self.totalHeight + self.renderedText[len(self.renderedText) - 1].get_height()

        # logger.debug('self.renderedText length %d', len(self.renderedText))

    def show(self, surface):
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        if (self.totalHeight > window_height + 15):
            y = 15
        else:
            y = window_height / 2 - self.totalHeight / 2 + 15
        for txt in self.renderedText[self.offset_line:]:
            if (y > window_height):
                break
            surface.blit(txt, (window_width / 2 - txt.get_width() / 2, y))
            y = y + txt.get_height()
        pass

    def get_height(self):
        return self.totalHeight

    def triggerOffset(self):
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        if (self.totalHeight > window_height - 15):
            # self.offset_line = self.offset_line + 1
            if (self.totalHeight - self.offset_line * self.renderedText[0].get_height()) > (window_height - 15):
                self.offset_line = self.offset_line + 1
                # logger.debug('    self.offset_line %d', self.offset_line)
            else:
                self.offset_line = 0
                # logger.debug('    self.offset_line %d', self.offset_line)

    pass

class RobotUI(BaseUI):

    wakeUpTime = -1000000
    maskColor = (0, 0, 0, 128)
    message = None
    font = None
    showDuration = 10000

    def __init__(self, ui_index):
        super().__init__(ui_index)
        self.font = zhSmallFont
        self.showDuration = Config().get('robot.show_delay', 10000)

    def on_shown(self):
        pass

    def on_hidden(self):
        pass

    def is_showing(self):
        return (time.time() * 1000 - self.wakeUpTime) < self.showDuration

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
        if not isLongPress and pushCount == 1:
            self.wakeUpTime = time.time() * 1000
            if self.message is not None:
                self.message.triggerOffset()
            return True
        # if isLongPress:
        #     if longPressSeconds == 2:
        #         # logger.debug('current_index', self.current_index, ', animating', self.animating)
        #         if self.animating:
        #             return True
        #         self.executeAction()
        #         return True
        return False

    def update(self, surface = None):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]

        if self.is_showing() is False:
            if self.message is not None:
                self.message = None
            return
        self.logger.debug('update wakeUpTime={}, current={}'.format(self.wakeUpTime, time.time() * 1000))
        surface2 = surface.convert_alpha()
        surface2.fill((255,255,255,0))
        
        # msgTxt = None
        # if self.font is not None:
        #     msgTxt = self.font.render(self.message, True, color_white)

        pygame.draw.rect(surface2, self.maskColor, (0, 0, window_width, window_height))


        if self.message is not None:
            # surface2.blit(msgTxt, (window_width / 2 - msgTxt.get_width() / 2, (window_height / 2 - msgTxt.get_height() / 2)))
            if self.message.get_height() > (window_height - 15):
                self.drawFace(surface2, 0.1)
            else:
                face_height = window_height / 2 - self.message.get_height() / 2
                self.drawFace(surface2, (face_height * 1.6) / (window_height - 15))
            self.message.show(surface2)
        else:        
            self.drawFace(surface2)

        surface.blit(surface2, (0,0))

        pass

    def showMessage(self, message):
        self.wakeUpTime = time.time() * 1000
        logger.debug('robot showMessage: {}'.format(message))
        self.message = RobotMessage(message, color_white)
        pass

    def event(self, eventName, args):
        self.wakeUpTime = time.time() * 1000
        logger.debug('robot event', eventName, args)
        if 'think' == eventName:
            self.message = RobotMessage('(Thinking...) {}'.format(args), color_white)
        pass
    
    def wakeUp(self):
        self.wakeUpTime = time.time() * 1000
        logger.debug('robot wakeUp')
        if self.message is not None:
            self.message = None
        pass

    def sleep(self):
        self.wakeUpTime = 0
        logger.debug('robot sleep')
        if self.message is not None:
            self.message = None
        pass

    def drawFace(self, surface, scale = 1, x = 0, y = 0):
        winSize = UIManager().getWindowSize()
        surfaceSize = UIManager().getWindowSize()
        faceSurface = pygame.Surface(surfaceSize)
        faceSurface = faceSurface.convert_alpha()
        faceSurface.fill((255,255,255,0))
        eyeBG_c = (255,255,255,250)
        eyeA_c = (81,143,237,250)
        # draw left eye
        pygame.draw.ellipse(faceSurface, eyeBG_c, (35,27,65,80))
        pygame.draw.ellipse(faceSurface, eyeA_c, (47,42,41,50))

        # draw right eye
        pygame.draw.ellipse(faceSurface, eyeBG_c, (140,27,65,80))
        pygame.draw.ellipse(faceSurface, eyeA_c, (152,42,41,50))

        surfaceSize = (int(surfaceSize[0] * scale), int(surfaceSize[1] * scale))
        if scale != 1:
            #logger.debug('face scale', scale)
            faceSurface = pygame.transform.scale(faceSurface, surfaceSize)
            x = winSize[0] / 2 - surfaceSize[0] / 2

        surface.blit(faceSurface, (x,y))
		
		
        pass

    pass