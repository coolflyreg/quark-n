#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import logging
import logging.config
import pygame
import subprocess
from ui.core import UIManager, BaseUI
from ui.menu import IconAction, MenuUI
from ui.theme import *
from system.config import Config

logger = logging.getLogger('ui.menu')


class WuKongMenuUI(MenuUI):

    ICONS = [
        IconAction('start', 'chenggong.png', '启动'),
        IconAction('stop', 'close.png', '停止')
    ]

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

    def startWuKong(self):
        wukongRoot = Config().get('robot.wukong.root')
        
        cmd = ['su', '-', 'pi', '-c', '"sudo /usr/bin/python {}"'.format(os.path.join(wukongRoot, 'wukong.py'))]
        logger.debug('Executing %s', ' '.join(cmd))
        print('Executing [%s]' % ' '.join(cmd))
        if self.proc is None:
            self.proc = subprocess.Popen(cmd)#, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pass

    def stopWuKong(self):
        if self.proc is not None:
            self.proc.terminate()
        pass

    def update(self):
        super().update()

        if self.proc is not None:
            if self.proc.poll() is not None:
                print('WuKong Process is exited with code:', self.proc.poll())
                self.proc = None
            

        pass
    
    pass