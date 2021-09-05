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

logger = logging.getLogger('ui.album')

class AlbumUI(BaseUI):

    showTick = 0
    current_img = None
    fileObjs = []
    target_index = 0

    def on_shown(self):
        target_index = 0
        pic_path = Config().get('camera.dest_path', '/home/pi/Pictures/')
        if os.path.exists(pic_path) and os.path.isdir(pic_path):
            self.fileObjs = os.listdir(pic_path)
        if len(self.fileObjs) > 0 and target_index < len(self.fileObjs):
            filepath = os.path.join(pic_path, self.fileObjs[target_index])
            self.loadFile(filepath)

        self.target_index = target_index
        self.showTick = (time.time() * 1000)
        pass

    def loadFile(self, path):
        if os.path.exists(path) is False:
            self.current_img = None
            return
        if os.path.isfile(path):
            if path.lower().endswith('.png') or path.lower().endswith('.jpg') or path.lower().endswith('.jpeg') or path.lower().endswith('.bmp'):
                self.current_img = pygame.transform.scale(pygame.image.load(path), UIManager().getWindowSize())
            elif path.lower().endswith('.gif'):
                self.current_img = GIFImage(path)
            else:
                self.current_img = pygame.image.load(os.path.join(sys.path[0], 'images/icon_set3', 'doc.png'))
        else:
            self.current_img = pygame.image.load(os.path.join(sys.path[0], 'images/icon_set3', 'folder.png'))
            pass

    def onMouseUp(self, event):
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        leftRect = pygame.Rect(3, 5, window_width / 2 - 3, window_height - 10)
        rightRect = pygame.Rect(window_width / 2, 5, window_width / 2, window_height - 10)
        if len(self.fileObjs) == 0:
            return
        if leftRect.collidepoint(event.pos):
            if (self.target_index - 1) < 0:
                self.target_index = len(self.fileObjs) - 1
            else:
                self.target_index = self.target_index - 1
        if rightRect.collidepoint(event.pos):
            if (self.target_index + 1) >= len(self.fileObjs):
                self.target_index = 0
            else:
                self.target_index = self.target_index + 1
        pic_path = Config().get('camera.dest_path', '/home/pi/Pictures/')
        filepath = os.path.join(pic_path, self.fileObjs[self.target_index])
        self.loadFile(filepath)
        pass


    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
        if not isLongPress and pushCount == 1:
            if keyIndex == 1:
                if (self.target_index - 1) < 0:
                    self.target_index = len(self.fileObjs) - 1
                else:
                    self.target_index = self.target_index - 1
            else:
                if (self.target_index + 1) >= len(self.fileObjs):
                    self.target_index = 0
                else:
                    self.target_index = self.target_index + 1

            
            if len(self.fileObjs) > 0 and self.target_index < len(self.fileObjs):
                pic_path = Config().get('camera.dest_path', '/home/pi/Pictures/')
                filepath = os.path.join(pic_path, self.fileObjs[self.target_index])
                self.loadFile(filepath)

            return True
        # if isLongPress:
        #     if longPressSeconds == 2:
        #         return True
        #     pass
        return False

    def on_hidden(self):
        pass

    def update(self, surface = None):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)

        if len(self.fileObjs) == 0:
            welcomeTxt = bigFont.render('No', True, color_white)
            welcome2Txt = bigFont.render('Images', True, color_white)
            surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, 10))
            surface.blit(welcome2Txt, (window_width / 2 - welcome2Txt.get_width() / 2, 60))
        else:
            if self.current_img is not None:
                if self.current_img.__class__.__name__ == pygame.Surface.__name__:
                    surface.blit(self.current_img, (window_width / 2 - self.current_img.get_width() / 2, window_height / 2 - self.current_img.get_height() / 2))
                else:
                    self.current_img.render(surface, (window_width / 2 - self.current_img.get_width() / 2, window_height / 2 - self.current_img.get_height() / 2))

        page = '{}/{}'.format(self.target_index + 1, len(self.fileObjs))
        pageText = miniFont.render(page, True, color_green)
        surface.blit(pageText, (window_width / 2 - pageText.get_width() / 2, window_height - pageText.get_height()))
        pass

    pass