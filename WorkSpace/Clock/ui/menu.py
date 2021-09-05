#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import logging.config
import pygame
from ui.core import UIManager, BaseUI
from ui.theme import *

logger = logging.getLogger('ui.menu')

class IconAction(object):

    name = None
    img = None
    text = None

    def __init__(self, name, img, text):
        self.name = name
        self.img = img
        self.text = text

    pass

class MenuUI(BaseUI):

    showTick = 0
    ICONS = [
        IconAction('clock', 'clock.png', '数字时钟'),
        IconAction('wukong', 'wukong.png', '孙悟空'),
        IconAction('camera', 'camera.png', '相机'),
        IconAction('album', 'img.png', '相册'),
        IconAction('video', 'disk.png', '视频'),
        # IconAction('statistics', 'statisticalchart.png', '陀螺仪'),
        IconAction('calendar', 'calendar.png', '3D界面'),
        # IconAction('maillist', 'maillist.png'),
        IconAction('splash', 'computer.png', '启动画面'),
        IconAction('set', 'set.png', '设置'),
        IconAction('close', 'close.png', '关闭')
    ]
    ICON_IMGS = []
    current_index = 0
    target_index = 0
    animating = False
    animationRemain = 0
    animationDuration = 400 # 执行时间
    animationPrevTick = 0
    direction = 1  # 1 往左移动，-1 往右移动

    smallIconSize = (40, 40)
    normalIconSize = (100, 100)
    drawBackground = False    

    def __init__(self, ui_index):
        super().__init__(ui_index)
        # print(self.__class__.__name__, 'icon size', len(self.ICONS))

    def set_icons(self, icons):
        self.ICONS = icons
        icon_imgs = []
        for iconAct in self.ICONS:
            icon_imgs.append(
                pygame.transform.scale(
                    pygame.image.load(
                        os.path.join(sys.path[0], 'images/icon_set3', iconAct.img))
                    , self.normalIconSize))
        self.current_index = 0
        self.target_index = 0
        self.ICON_IMGS = icon_imgs

    def on_shown(self):
        self.showTick = (time.time() * 1000)
        self.logger.debug('icon size on shown %d', len(self.ICONS))
        # if len(self.ICON_IMGS) == 0:
        self.ICON_IMGS = []
        for iconAct in self.ICONS:
            self.ICON_IMGS.append(
                pygame.transform.scale(
                    pygame.image.load(
                        os.path.join(sys.path[0], 'images/icon_set3', iconAct.img))
                    , self.normalIconSize))
        pass

    def on_hidden(self):
        pass

    def moveToLeft(self):
        self.direction = -1
        self.animating = True
        self.animationRemain = self.animationDuration
        self.animationPrevTick = (time.time() * 1000)

        if (self.target_index - 1) < 0:
            self.target_index = len(self.ICON_IMGS) - 1
        else:
            self.target_index = self.target_index - 1
    
    def moveToRight(self):
        self.direction = 1
        self.animating = True
        self.animationRemain = self.animationDuration
        self.animationPrevTick = (time.time() * 1000)

        if (self.target_index + 1) >= len(self.ICON_IMGS):
            self.target_index = 0
        else:
            self.target_index = self.target_index + 1

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
        if not isLongPress and pushCount == 1:
            if self.animating:
                return True
            if keyIndex == 1:
                self.moveToLeft()
            else:
                self.moveToRight()
            return True
        if isLongPress:
            if longPressSeconds == 2 and keyIndex == 0:
                # print('current_index', self.current_index, ', animating', self.animating)
                if self.animating:
                    return True
                self.executeAction()
                return True
        return False

    def onKeyPush(self, pushCount, keyIndex):
        pass

    def onMouseUp(self, event):
        # print('menu onMouseUp', event.pos)
        if self.animating:
            return
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        # leftRect = pygame.Rect(5, window_height / 2 - self.smallIconSize[1] / 2, self.smallIconSize[0], self.smallIconSize[1])
        # rightRect = pygame.Rect(window_width - self.smallIconSize[1] - 5, window_height / 2 - self.smallIconSize[1] / 2, self.smallIconSize[0], self.smallIconSize[1])
        # centerRect = pygame.Rect(window_width / 2 - self.normalIconSize[0] / 2, window_height / 2 - self.normalIconSize[1] / 2, self.normalIconSize[0], self.normalIconSize[1])

        leftRect = pygame.Rect(5, 5, self.smallIconSize[0], window_height - 10)
        rightRect = pygame.Rect(window_width - self.smallIconSize[1] - 5, 5, self.smallIconSize[0], window_height - 10)
        centerRect = pygame.Rect(window_width / 2 - self.normalIconSize[0] / 2, 5, self.normalIconSize[0], window_height - 10)

        if leftRect.collidepoint(event.pos):
            # print("click left icon")
            self.moveToLeft()
            return
        if rightRect.collidepoint(event.pos):
            # print("click right icon")
            self.moveToRight()
            return
        if centerRect.collidepoint(event.pos) or SIDE_MENU_RECT.collidepoint(event.pos):
            # print("click center icon")
            self.executeAction()
            return
        pass

    def executeAction(self):
        if self.ICONS[self.current_index].name == 'clock':
            from ui.clock import ClockUI
            UIManager().get(ClockUI.__name__).show()
            
        if self.ICONS[self.current_index].name == 'wukong':
            from .wukongMenu import WuKongMenuUI
            UIManager().get(WuKongMenuUI.__name__).show()
            
        if self.ICONS[self.current_index].name == 'camera':
            from .camera import CameraUI
            UIManager().get(CameraUI.__name__).show()

        if self.ICONS[self.current_index].name == 'album':
            from .album import AlbumUI
            UIManager().get(AlbumUI.__name__).show()

        if self.ICONS[self.current_index].name == 'video':
            from .video import VideoUI
            UIManager().get(VideoUI.__name__).show()

        # if self.ICONS[self.current_index].name == 'statistics':
        #     from .mpu6050 import MPU6050UI
        #     UIManager().get(MPU6050UI.__name__).show()

        if self.ICONS[self.current_index].name == 'calendar':
            from .threeD import ThreeDUI
            UIManager().get(ThreeDUI.__name__).show()

        if self.ICONS[self.current_index].name == 'splash':
            from ui.launchers import LaunchersUI
            UIManager().get(LaunchersUI.__name__).show()

        if self.ICONS[self.current_index].name == 'close':
            os.system("ttyecho -n /dev/tty1 echo 'User exited LCD UI'")
            UIManager().quit(send_signal=True)

    def onMpu(self, activities):
        if self.animating:
            return True
        if activities['isPosActivityOnZ'] > 1:
            self.executeAction()
            return True
        if activities['isNegActivityOnX'] > activities['isPosActivityOnX']:
            self.moveToLeft()
            return True
        elif activities['isNegActivityOnX'] < activities['isPosActivityOnX']:
            self.moveToRight()
            return True
        
        return False

    def update(self, surface = None):
        if surface is None:
            surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        if self.__class__.__name__ == MenuUI.__name__ or self.drawBackground is True:
            surface.fill(color_black)

        escapedTime = (time.time() * 1000) - self.animationPrevTick
        self.animationPrevTick = (time.time() * 1000)
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
            step_x = - int(total_run_x * percent) * self.direction
            center_step_x = - int((window_width / 2 - self.smallIconSize[0] / 2 - 5) * percent) * self.direction
            smallSize = ( int((self.normalIconSize[0] - self.smallIconSize[0]) * percent + self.smallIconSize[0]), int((self.normalIconSize[1] - self.smallIconSize[1]) * percent + self.smallIconSize[1]) )
            normalSize = ( int(self.normalIconSize[0] - (self.normalIconSize[0] - self.smallIconSize[0]) * percent), int(self.normalIconSize[1] - (self.normalIconSize[1] - self.smallIconSize[1]) * percent) )

        right2_img = None
        left2_img = None
        if icon_index > 0:
            left_img = pygame.transform.scale(self.ICON_IMGS[icon_index - 1], self.smallIconSize if self.direction == 1 else smallSize)
        else:
            left_img = pygame.transform.scale(self.ICON_IMGS[len(self.ICON_IMGS) - 1], self.smallIconSize if self.direction == 1 else smallSize)

        if (icon_index + 1) < len(self.ICON_IMGS):
            right_img = pygame.transform.scale(self.ICON_IMGS[icon_index + 1], smallSize if self.direction == 1 else self.smallIconSize)
        else:
            right_img = pygame.transform.scale(self.ICON_IMGS[0], smallSize if self.direction == 1 else self.smallIconSize)

        if self.animating:
            if self.direction == 1:
                if (icon_index + 2) < len(self.ICON_IMGS):
                    right2_img = pygame.transform.scale(self.ICON_IMGS[icon_index + 2], self.smallIconSize)
                elif (icon_index + 1) < len(self.ICON_IMGS):
                    right2_img = pygame.transform.scale(self.ICON_IMGS[0], self.smallIconSize)
                elif len(self.ICON_IMGS) > 1:
                    right2_img = pygame.transform.scale(self.ICON_IMGS[1], self.smallIconSize)
            if self.direction == -1:
                if (icon_index - 2) >= 0:
                    left2_img = pygame.transform.scale(self.ICON_IMGS[icon_index - 2], self.smallIconSize)
                elif (icon_index - 1) >= 0:
                    left2_img = pygame.transform.scale(self.ICON_IMGS[len(self.ICON_IMGS) - 1], self.smallIconSize)
                elif len(self.ICON_IMGS) > 1:
                    left2_img = pygame.transform.scale(self.ICON_IMGS[len(self.ICON_IMGS) - 2], self.smallIconSize)

        current_text = None
        if not self.animating:
            current_img = self.ICON_IMGS[icon_index]
            current_text = zhMiniFont.render(self.ICONS[icon_index].text, True, color_white)
        else:
            current_img = pygame.transform.scale(self.ICON_IMGS[icon_index], normalSize)

        surface.blit(left_img, (5 + step_x, window_height / 2 - left_img.get_height() / 2))
        surface.blit(right_img, (window_width - right_img.get_width() - 5 + step_x, window_height / 2 - right_img.get_height() / 2))
        if self.animating:
            if right2_img is not None:
                surface.blit(right2_img, (window_width - right2_img.get_width() - 5 + step_x + total_run_x, window_height / 2 - right2_img.get_height() / 2))
            if left2_img is not None:
                surface.blit(left2_img, ( - total_run_x + step_x + 5 , window_height / 2 - left2_img.get_height() / 2))
            # surface.blit(current_img, (window_width / 2 - current_img.get_width() / 2 + step_x - window_width / 2, window_height / 2 - current_img.get_height() / 2))
            pass
        
        surface.blit(current_img, (window_width / 2 - current_img.get_width() / 2 + center_step_x, window_height / 2 - current_img.get_height() / 2))
        # print(smallSize, normalSize)
        if current_text is not None:
            surface.blit(current_text, (window_width / 2 - current_text.get_width() / 2 + center_step_x, window_height - current_text.get_height() - 5))

        if self.animationRemain <= 0:
            self.animating = False
            self.current_index = self.target_index
        if ((time.time() * 1000) - self.showTick) > 1000:
            # from .clock import ClockUI
            # ui = UIManager().get(ClockUI.__name__)
            # ui.show()
            pass
        pass

    pass