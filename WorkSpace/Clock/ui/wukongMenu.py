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

    def __init__(self, ui_index):
        super().__init__(ui_index)
        # print(self.__class__.__name__, 'icon size', len(self.ICONS))
        self.proc = None

    def executeAction(self):
        if self.ICONS[self.current_index].name == 'start':
            print('wukong start')
            self.startWuKong()
        if self.ICONS[self.current_index].name == 'stop':
            print('wukong stop')
            self.stopWuKong()

    def _startWuKong(self, cmd):
        pass

    def startWuKong(self):
        wukongRoot = Config().get('robot.wukong.root')
        
        cmd = ['/bin/sh', '-c', '"{} {}"'.format( os.path.join(sys.path[0], 'wukong.sh'), wukongRoot ) ]
        logger.debug('Executing %s', ' '.join(cmd))
        print('Executing [%s]' % ' '.join(cmd))
        if self.proc is None:
            os.system('chmod +x "{}"'.format(cmd[0]))
            self.proc = subprocess.Popen(cmd, shell=False, cwd=wukongRoot)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pass

    def stopWuKong(self):
        if self.proc is not None:
            # self.proc.communication()
            self.proc.send_signal(signal.SIGINT)
            self.proc.terminate()
            self.proc.kill()
        pass

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
    
    pass

