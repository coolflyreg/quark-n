#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import logging
import logging.config
from ui.core import UIManager, BaseUI
from ui.theme import *
from utils.GIFImage import GIFImage
from system.config import Config

logger = logging.getLogger('ui.launchers')

class LaunchersUI(BaseUI):

    target_index = 0
    current_img = None
    
    def on_shown(self):
        self.target_index = int(Config().get('user-interface.launcher.current'))
        self.images = Config().get('user-interface.launcher.images')
        if len(self.images) > 0 and self.target_index < len(self.images):
            self.launcher_img = GIFImage(os.path.join(sys.path[0], self.images[self.target_index]))
        print('images', self.images)
        self.showTick = pygame.time.get_ticks()
        pass

    def on_hidden(self):
        pass

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds):
        if not isLongPress and pushCount == 1:
            if (self.target_index + 1) >= len(self.images):
                self.target_index = 0
            else:
                self.target_index = self.target_index + 1
            
            if len(self.images) > 0 and self.target_index < len(self.images):
                self.launcher_img = GIFImage(os.path.join(sys.path[0], self.images[self.target_index]))

            return True
        if isLongPress:
            if longPressSeconds == 2:
                # print('current_index', self.current_index, ', animating', self.animating)
                self.saveSetting()
                return True
        return False
    
    def saveSetting(self):
        if self.launcher_img is not None:
            Config().set('user-interface.launcher.current', self.target_index)
            Config().save()

    def update(self, surface = None):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)
        if self.launcher_img is None:
            welcomeTxt = bigFont.render('No', True, color_white)
            welcome2Txt = bigFont.render('Images', True, color_white)
            surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, 10))
            surface.blit(welcome2Txt, (window_width / 2 - welcome2Txt.get_width() / 2, 60))
            pass
        else:
            self.launcher_img.render(surface, (0, -10))
        pass

    pass