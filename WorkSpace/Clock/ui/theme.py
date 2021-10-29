#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import pygame


_FontCache = []
_FontNames = {
    'DIGIT': "fonts/DS-DIGIT.TTF",
    'PingFang': "fonts/PingFang.ttc",
    'DIGITAL': "fonts/DIGITAL.TTF",
    'SCORE': "fonts/SCOREBOARD.TTF",
    'PROTFB' : "fonts/PRO-TFB.TTF",
    'fzpx12' : "fonts/fzpx12.TTF",
    'fzpx24' : "fonts/fzpx24.TTF"
}

class FontObj:
    size = 0
    fontName = ''
    fontPath = None
    font = None

    def __init__(self, size, fontName, fontPath):
        self.size = size
        self.fontName = ''
        self.fontPath = fontPath
        self.font = pygame.font.Font(fontPath, self.size)
        pass


def getAppFont(size, fontName):
    for f in _FontCache:
        if ("%d-%s" % (f.size, f.fontName)) == ("%d-%s" % (size, fontName)):
            return f.font
    
    newFont = FontObj(size, fontName, _FontNames[fontName])
    _FontCache.append(newFont)
    return newFont.font

print('fontfile path: ', os.getcwd(), sys.path)

# print('fontfile path: ', os.path.dirname(__file__))
# fontPath = os.path.join(sys.path[0], _FontNames['DIGIT'])
largeFont = getAppFont(82, 'DIGIT') #pygame.font.Font(fontPath, 82)
bigFont = getAppFont(52, 'DIGIT') # pygame.font.Font(fontPath, 52)
middleFont = getAppFont(40, 'DIGIT') # pygame.font.Font(fontPath, 40)
smallFont = getAppFont(30, 'DIGIT') # pygame.font.Font(fontPath, 30)
miniFont = getAppFont(26, 'DIGIT') # pygame.font.Font(fontPath, 26)
tinyFont = getAppFont(24, 'DIGIT') # pygame.font.Font(fontPath, 24)
tinyFont22 = getAppFont(22, 'DIGIT') # pygame.font.Font(fontPath, 20)

# zhFontPath = os.path.join(sys.path[0], _FontNames['PingFang'])
zhSmallFont = getAppFont(30, 'PingFang') # pygame.font.Font(zhFontPath, 30)
zhMiniFont = getAppFont(20, 'PingFang') # pygame.font.Font(zhFontPath, 20)


color_white = (255,255,255)
color_black = (0,0,0)
color_green = (0,255,0)
color_red = (255,0,0)
color_cyan = (0,255,255)
color_orange = (255,128,0)
color_msgreen = (0,255,184)
color_gray = (148,148,148)

SIDE_MENU_RECT = pygame.Rect(0, 10, 5, 115)

