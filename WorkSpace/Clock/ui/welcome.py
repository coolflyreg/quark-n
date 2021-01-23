#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import logging
import logging.config
from ui.core import UIManager, BaseUI
from ui.theme import *

logger = logging.getLogger('ui.welcome')

class WelcomeUI(BaseUI):

    showTick = 0

    def on_shown(self):
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
        welcomeTxt = bigFont.render('Welcome', True, color_white)
        surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, window_height / 2 - welcomeTxt.get_height() / 2))
        if (pygame.time.get_ticks() - self.showTick) > 1000:
            from .clock import ClockUI
            ui = UIManager().get(ClockUI.__name__)
            ui.show()
            pass
        pass

    pass