#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import time
import _thread
import logging
import logging.config
from ui.core import UIManager, BaseUI
from ui.theme import *
from utils.GIFImage import GIFImage
from system.config import Config
import pygame.camera
# from utils import *
from ui.menu import IconAction, MenuUI

logger = logging.getLogger('ui.camera')

IMG_OLD = 0
IMG_NEW = 1
IMG_TAK = 2


def runAsync(work, delay = 0):
    def _workFunc(w,d):
        if (d > 0):
            time.sleep(d)
        w()
    _thread.start_new_thread(_workFunc, (work, delay))
    pass


class CameraUI(MenuUI):

    ICONS = [
        IconAction('save', 'chenggong.png', '保存'),
        IconAction('cancel', 'close.png', '取消')
    ]

    smallIconSize = (40, 40)
    normalIconSize = (80, 80)

    showTick = 0
    current_img = None
    cam = None
    img_state = IMG_OLD
    is_cam_module_inited = False
    ask_save_pic = False

    drivers = []

    def __init__(self, ui_index):
        super().__init__(ui_index)

    def on_shown(self):
        super().on_shown()
        self.showTick = (time.time() * 1000)
        windowSize = UIManager().getWindowSize()
        # if self.cam is None:
        if self.is_cam_module_inited is False:
            pygame.camera.init()
            self.is_cam_module_inited = True
            self.drivers = pygame.camera.list_cameras()
        if self.cam is None and len(self.drivers) > 0:
            self.cam = pygame.camera.Camera(self.drivers[0], windowSize)
            logger.debug('camera class %s', self.cam.__class__.__name__)
            try:
                self.cam.start()
                logger.info('cam start success')
            except:
                logger.error('cam start failed')
                pass
            pass

    def on_hidden(self):
        try:
            self.cam.stop()
            self.cam = None
            logger.info('cam stop success')
        except:
            logger.error('cam stop failed')
            pass
        try:
            pygame.camera.quit()
            self.is_cam_module_inited = False
        except:
            print('pycamera quit failed')
            pass
        self.current_img = None
        self.img_state = IMG_OLD
        super().on_hidden()
        pass

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
        if not isLongPress and pushCount == 1:
            if len(self.drivers) == 0:
                from .menu import MenuUI
                UIManager().get(MenuUI.__name__).show()
                return True
            if self.ask_save_pic is False:
                self.ask_save_pic = True
            if self.ask_save_pic:
                super().onKeyRelease(isLongPress, pushCount, longPressSeconds, keyIndex)
            return True
        if isLongPress:
            if longPressSeconds == 2:
                if len(self.drivers) == 0:
                    from .menu import MenuUI
                    UIManager().get(MenuUI.__name__).show()
                    return True
                # print('current_index', self.current_index, ', animating', self.animating)
                if self.animating:
                    return True
                self.executeAction()
                return True
        return False

    def executeAction(self):
        if self.ask_save_pic is False:
            self.ask_save_pic = True
            return
        if self.cam is None:
            return
        if self.ICONS[self.current_index].name == 'save':
            filename = str(int(time.time())) + '_' + os.urandom(3).hex() + '.png'
            pygame.image.save(self.current_img, os.path.join(Config().get('camera.dest_path', '/home/pi/Pictures/'), filename))
            self.ask_save_pic = False
            
        if self.ICONS[self.current_index].name == 'cancel':
            self.ask_save_pic = False

    def takePicture(self):
        try:
            # print('enter takePicture')
            new_img = self.cam.get_image()
            # print('new img', new_img)
            self.current_img = new_img
            self.img_state = IMG_NEW
        except Error as e:
            logger.error('take picture error', e)

    def update(self, surface = None):

        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)

        if self.cam is None or len(self.drivers) == 0:
            welcomeTxt = bigFont.render('No', True, color_white)
            welcome2Txt = bigFont.render('Camera', True, color_white)
            surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, 10))
            surface.blit(welcome2Txt, (window_width / 2 - welcome2Txt.get_width() / 2, 60))
            return

        if self.current_img is not None:
            # print('draw ', self.current_img)
            surface.blit(pygame.transform.scale(self.current_img, (windowSize)), (0,0))
            if self.img_state == IMG_NEW:
                self.img_state = IMG_OLD
        if self.img_state == IMG_OLD and self.ask_save_pic is False:
            self.img_state = IMG_TAK
            # print('take pic ')
            a = self
            runAsync(lambda: a.takePicture())
            pass

        if (self.ask_save_pic):
            super().update()
        pass

    pass