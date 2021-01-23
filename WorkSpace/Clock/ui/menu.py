#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import logging
import logging.config
import pygame
from ui.core import UIManager, BaseUI
from ui.theme import *

logger = logging.getLogger('ui.menu')

class MenuUI(BaseUI):

    showTick = 0
    ICONS = ['clock.png', 'calendar.png', 'camera.png', 'maillist.png', 'set.png']
    ICON_IMGS = []
    current_index = 0
    target_index = 0
    animating = False
    animationRemain = 0
    animationDuration = 400 # 执行时间
    animationPrevTick = 0

    smallIconSize = (40, 40)
    normalIconSize = (100, 100)

    def on_shown(self):
        self.showTick = pygame.time.get_ticks()
        if len(self.ICON_IMGS) == 0:
            for imgName in self.ICONS:
                self.ICON_IMGS.append(
                    pygame.transform.scale(
                        pygame.image.load(
                            os.path.join(sys.path[0], 'images/icon_set3', imgName))
                        , self.normalIconSize))
        pass

    def on_hidden(self):
        pass

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds):
        if not isLongPress and pushCount == 1:
            if self.animating:
                return True
            if (self.target_index + 1) >= len(self.ICON_IMGS):
                self.target_index = 0
            else:
                self.target_index = self.target_index + 1
            
            print('onKeyRelease current_index', self.current_index, ', animating', self.animating)
            self.animating = True
            self.animationRemain = self.animationDuration
            self.animationPrevTick = pygame.time.get_ticks()
            return True
        if isLongPress:
            if longPressSeconds == 2:
                print('current_index', self.current_index, ', animating', self.animating)
                if self.current_index == 0 and not self.animating:
                    from ui.clock import ClockUI
                    UIManager().get(ClockUI.__name__).show()
                return True
        return False

    def onKeyPush(self, pushCount):
        pass

    def update(self):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)

        escapedTime = pygame.time.get_ticks() - self.animationPrevTick
        self.animationPrevTick = pygame.time.get_ticks()
        percent = 1.0 - self.animationRemain / self.animationDuration
        self.animationRemain = self.animationRemain - escapedTime
        total_run_x = (self.normalIconSize[0] / 2 + self.smallIconSize[0] / 2 - 5)

        icon_index = self.current_index
        if not self.animating:
            smallSize = self.smallIconSize
            normalSize = self.normalIconSize
            step_x = 0
            center_step_x = 0
        else:
            step_x = - int(total_run_x * percent)
            center_step_x = - int((window_width / 2 - self.smallIconSize[0] / 2 - 5) * percent)
            smallSize = ( int((self.normalIconSize[0] - self.smallIconSize[0]) * percent + self.smallIconSize[0]), int((self.normalIconSize[1] - self.smallIconSize[1]) * percent + self.smallIconSize[1]) )
            normalSize = ( int(self.normalIconSize[0] - (self.normalIconSize[0] - self.smallIconSize[0]) * percent), int(self.normalIconSize[1] - (self.normalIconSize[1] - self.smallIconSize[1]) * percent) )

        if icon_index > 0:
            left_img = pygame.transform.scale(self.ICON_IMGS[icon_index - 1], self.smallIconSize)
        else:
            left_img = pygame.transform.scale(self.ICON_IMGS[len(self.ICON_IMGS) - 1], self.smallIconSize)

        if (icon_index + 1) < len(self.ICON_IMGS):
            right_img = pygame.transform.scale(self.ICON_IMGS[icon_index + 1], smallSize)
        else:
            right_img = pygame.transform.scale(self.ICON_IMGS[0], smallSize)

        if (icon_index + 2) < len(self.ICON_IMGS) and self.animating:
            right2_img = pygame.transform.scale(self.ICON_IMGS[icon_index + 2], self.smallIconSize)
        else:
            right2_img = pygame.transform.scale(self.ICON_IMGS[0], self.smallIconSize)

        if not self.animating:
            current_img = self.ICON_IMGS[icon_index]
        else:
            current_img = pygame.transform.scale(self.ICON_IMGS[icon_index], normalSize)

        surface.blit(left_img, (5 + step_x, window_height / 2 - left_img.get_height() / 2))
        surface.blit(right_img, (window_width - right_img.get_width() - 5 + step_x, window_height / 2 - right_img.get_height() / 2))
        if self.animating:
            surface.blit(right2_img, (window_width - right2_img.get_width() - 5 + step_x + total_run_x, window_height / 2 - right2_img.get_height() / 2))
            # surface.blit(current_img, (window_width / 2 - current_img.get_width() / 2 + step_x - window_width / 2, window_height / 2 - current_img.get_height() / 2))
        
        surface.blit(current_img, (window_width / 2 - current_img.get_width() / 2 + center_step_x, window_height / 2 - current_img.get_height() / 2))
        # print(smallSize, normalSize)

        if self.animationRemain <= 0:
            self.animating = False
            self.current_index = self.target_index
        if (pygame.time.get_ticks() - self.showTick) > 1000:
            # from .clock import ClockUI
            # ui = UIManager().get(ClockUI.__name__)
            # ui.show()
            pass
        pass

    pass