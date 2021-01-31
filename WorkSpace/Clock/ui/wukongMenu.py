#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import logging
import logging.config
import subprocess
import signal
import pygame
from ui.core import UIManager, BaseUI
from ui.menu import IconAction, MenuUI
from ui.theme import *
from ui.dialog import *
from system.config import Config

logger = logging.getLogger('ui.wukongMenu')


class WuKongMenuUI(MenuUI):

    ICONS = [
        IconAction('start', 'chenggong.png', '启动'),
        IconAction('stop', 'close.png', '停止')
    ]
    drawBackground = True
    wukongIndicator = None
    is_destroy = False

    def __init__(self, ui_index):
        super().__init__(ui_index)
        # print(self.__class__.__name__, 'icon size', len(self.ICONS))
        self.proc = None

        self.wukongIndicator = pygame.transform.scale(
            pygame.image.load(
                os.path.join(sys.path[0], 'images/icon_set3', 'wukong.png')), (15, 15))
    
    def on_create(self):
        super().on_create()
        if bool(Config().get('robot.wukong.auto-start', False)) is True:
            self.startWuKong(is_auto_start = True)
        pass

    def on_shown(self):
        if self.proc is None:
            icons = [
                IconAction('start', 'chenggong.png', '启动')
            ]
        else:
            icons = [
                IconAction('stop', 'close.png', '停止')
            ]
        super().set_icons(icons)

    def executeAction(self):
        if self.ICONS[self.current_index].name == 'start':
            print('wukong start')
            self.startWuKong()
        if self.ICONS[self.current_index].name == 'stop':
            print('wukong stop')
            self.stopWuKong()

    def startWuKong(self, is_auto_start = False):
        wukongRoot = Config().get('robot.wukong.root')
        
        cmd = [os.path.join(sys.path[0], 'wukong.sh'), wukongRoot]
        logger.debug('Executing %s', ' '.join(cmd))
        print('Executing [%s]' % ' '.join(cmd))
        if self.proc is None:
            os.system('chmod +x "{}"'.format(cmd[0]))
            self.proc = subprocess.Popen(cmd, shell=False, cwd=wukongRoot)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if is_auto_start is False:
            self.hide()
        pass

    def stopWuKong(self):
        if self.proc is not None:
            # self.proc.communication()
            self.proc.send_signal(signal.SIGINT)
            self.proc.terminate()
            self.proc.kill()
            self.proc.wait()
            while self.proc.poll() is not None:
                print('WuKong Process is exited with code:', self.proc.poll())
                self.proc = None
                break
            self.killallWukong()
        if self.is_destroy is False:
            self.hide()
        pass

    def killallWukong(self):
        os.system('ps ax | grep "python wukong.py" | grep -v grep | awk \'{print "sudo kill -9 "$1}\' | bash')

    def update(self, surface = None):
        super().update()

        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]

        current_text = None
        if self.proc is not None:
            if self.proc.poll() is not None:
                print('WuKong Process is exited with code:', self.proc.poll())
                self.proc = None
            else:
                current_text = zhMiniFont.render('WuKong已启动', True, color_white)
        else:
            current_text = zhMiniFont.render('WuKong没有启动', True, color_white)

        if current_text is not None:
            surface.blit(current_text, (window_width / 2 - current_text.get_width() / 2, 0))
        pass

    def update_offscreen(self):
        if self.proc is None:
            return
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]

        indicator_pos = (window_width - self.wukongIndicator.get_width(), 0)
        surface.blit(self.wukongIndicator, indicator_pos)
        radius = 2
        pygame.draw.circle(surface, color_green, (indicator_pos[0] + self.wukongIndicator.get_width() - int(radius * 2), indicator_pos[1] + self.wukongIndicator.get_height() - int(radius * 2)), radius)

        pass

    def on_destroy(self):
        self.is_destroy = True
        self.stopWuKong()
    
    pass

