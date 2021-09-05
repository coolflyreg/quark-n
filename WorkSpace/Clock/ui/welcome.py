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

logger = logging.getLogger('ui.welcome')

class WelcomeUI(BaseUI):

    showTick = 0
    launcher_img = None

    def on_shown(self):
        target_index = int(Config().get('user-interface.launcher.current'))
        images = Config().get('user-interface.launcher.images')
        if len(images) > 0 and target_index < len(images):
            self.launcher_img = GIFImage(os.path.join(sys.path[0], images[target_index]))
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
        if self.launcher_img is None:
            welcomeTxt = bigFont.render('WELCOME', True, color_white)
            welcome2Txt = bigFont.render('QUARK-N', True, color_white)
            surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, 10))
            surface.blit(welcome2Txt, (window_width / 2 - welcome2Txt.get_width() / 2, 60))
            if ((time.time() * 1000) - self.showTick) > 1000:
                from .clock import ClockUI
                ui = UIManager().get(ClockUI.__name__)
                ui.show()
                pass
            
            # print("render welcome text")
        else:
            self.launcher_img.render(surface, (int(window_width/2-self.launcher_img.get_width()/2), int(window_height/2-self.launcher_img.get_height()/2)))
            # print("render welcome img")
            if ((time.time() * 1000) - self.showTick) > 1600:
                from .clock import ClockUI
                ui = UIManager().get(ClockUI.__name__)
                ui.show()
                pass
            pass
        pass

    pass