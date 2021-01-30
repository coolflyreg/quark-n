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

logger = logging.getLogger('ui.album')

class AlbumUI(BaseUI):

    showTick = 0
    current_img = None
    fileObjs = []

    def on_shown(self):
        target_index = 0
        pic_path = Config().get('camera.dest_path', '/home/pi/Pictures/')
        if os.path.exists(pic_path) and os.path.isdir(pic_path):
            self.fileObjs = os.listdir(Config().get('camera.dest_path', '/home/pi/Pictures/'))
        if len(self.fileObjs) > 0 and target_index < len(images):
            self.current_img = GIFImage(os.path.join(sys.path[0], images[target_index]))
        self.showTick = pygame.time.get_ticks()
        pass

    def on_hidden(self):
        pass

    def update(self):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)
        if self.launcher_img is None:
            welcomeTxt = bigFont.render('WELCOME', True, color_white)
            welcome2Txt = bigFont.render('QUARK-N', True, color_white)
            surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, 10))
            surface.blit(welcome2Txt, (window_width / 2 - welcome2Txt.get_width() / 2, 60))
            
            # print("render welcome text")
        else:
            self.current_img.render(surface, (0, -10))
        pass

    pass