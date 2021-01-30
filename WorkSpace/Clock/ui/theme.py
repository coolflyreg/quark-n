#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import pygame

print('fontfile path: ', os.getcwd(), sys.path)
# print('fontfile path: ', os.path.dirname(__file__))
fontPath = os.path.join(sys.path[0], "fonts/DS-DIGIT.TTF")
largeFont = pygame.font.Font(fontPath, 82)
bigFont = pygame.font.Font(fontPath, 52)
middleFont = pygame.font.Font(fontPath, 40)
smallFont = pygame.font.Font(fontPath, 30)
miniFont = pygame.font.Font(fontPath, 26)
tinyFont = pygame.font.Font(fontPath, 24)

zhFontPath = os.path.join(sys.path[0], "fonts/PingFang.ttc")
zhSmallFont = pygame.font.Font(zhFontPath, 30)
zhMiniFont = pygame.font.Font(zhFontPath, 20)


color_white = (255,255,255)
color_black = (0,0,0)
color_green = (0,255,0)
color_red = (255,0,0)