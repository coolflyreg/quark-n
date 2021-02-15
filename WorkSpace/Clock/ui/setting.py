#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import time
import logging
import logging.config
from ui.core import UIManager, BaseUI
from ui.theme import *

logger = logging.getLogger('ui.setting')

class SettingUI(BaseUI):

    showTick = 0

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
        welcomeTxt = bigFont.render('WELCOME', True, color_white)
        welcome2Txt = bigFont.render('QUARK-N', True, color_white)
        surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, 10))
        surface.blit(welcome2Txt, (window_width / 2 - welcome2Txt.get_width() / 2, 60))
        if ((time.time() * 1000) - self.showTick) > 1000:
            from .clock import ClockUI
            ui = UIManager().get(ClockUI.__name__)
            ui.show()
            pass
        pass

    pass