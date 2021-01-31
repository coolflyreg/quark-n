#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import sys
import time
import logging
import signal
from queue import Queue
from core import Singleton, Event, EventDispatcher
from system.config import Config


class UIManager(metaclass=Singleton):
    """
    All UI manager
    """

    current_ui = None
    window_size = None
    surface = None
    running = True
    robotUI = None
    __ui_dict = {}
    __ui_stack = []
    __dialog_stack = []
    is_quit = False

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def setWindowSize(self, window_size):
        self.window_size = window_size

    def setSurface(self, surface):
        self.surface = surface

    def getSurface(self):
        return self.surface

    def getWindowSize(self):
        return self.window_size

    def quit(self, send_signal = False):
        if self.is_quit is True:
            return
        self.is_quit = True
        for ui_name in self.__ui_dict:
            self.__ui_dict[ui_name].on_destroy()
        self.running = False
        os.kill(os.getpid(), signal.SIGINT)

    def isRunning(self):
        return self.running

    def init(self):
        from .welcome import WelcomeUI
        from .clock import ClockUI
        from .menu import MenuUI
        from .launchers import LaunchersUI
        from .robot import RobotUI
        from .wukongMenu import WuKongMenuUI
        from .camera import CameraUI
        from .album import AlbumUI

        self.robotUI = RobotUI(0)
        self.__ui_dict[WelcomeUI.__name__]          = WelcomeUI(len(self.__ui_dict))
        self.__ui_dict[ClockUI.__name__]            = ClockUI(len(self.__ui_dict))
        self.__ui_dict[MenuUI.__name__]             = MenuUI(len(self.__ui_dict))
        self.__ui_dict[LaunchersUI.__name__]        = LaunchersUI(len(self.__ui_dict))
        self.__ui_dict[WuKongMenuUI.__name__]       = WuKongMenuUI(len(self.__ui_dict))
        self.__ui_dict[CameraUI.__name__]           = CameraUI(len(self.__ui_dict))
        self.__ui_dict[AlbumUI.__name__]            = AlbumUI(len(self.__ui_dict))

        self.__ui_dict[WelcomeUI.__name__].show()
        # self.__ui_dict[MenuUI.__name__].show()
        # self.__ui_dict[WuKongMenuUI.__name__].show()
        pass

    def update(self, surface = None):
        if not self.running:
            return
        if self._current() is not None:
            self._current().update()

        self.robotUI.update()

        if self._currentDialog() is not None:
            self._currentDialog().update()

        for ui_name in self.__ui_dict:
            if self.__ui_dict[ui_name] is not self._current():
                self.__ui_dict[ui_name].update_offscreen()

    def current(self):
        if self._currentDialog() is not None:
            return self._currentDialog()
        if self.robotUI.is_showing():
            return self.robotUI
        if len(self.__ui_stack) == 0:
            return None
        return self.__ui_stack[-1:][0]

    def _current(self):
        if len(self.__ui_stack) == 0:
            return None
        return self.__ui_stack[-1:][0]

    def push(self, ui):
        self.__ui_stack.append(ui)
        pass

    def pop(self):
        return self.__ui_stack.pop()

    def replace(self, ui, root=False):
        if root is True:
            while len(self.__ui_stack) > 1:
                self.pop()
        self.pop()
        ui.show()
        # self.push(ui)
        pass

    def _currentDialog(self):
        if len(self.__dialog_stack) == 0:
            return None
        return self.__dialog_stack[-1:][0]

    def pushDialog(self, ui):
        self.__dialog_stack.append(ui)
        pass

    def popDialog(self):
        return self.__dialog_stack.pop()

    def replaceDialog(self, ui, root=False):
        if root is True:
            while len(self.__dialog_stack) > 1:
                self.popDialog()
        self.popDialog()
        ui.show()
        # self.push(ui)
        pass

    def closeAllDialog(self):
        while len(self.__dialog_stack) > 0:
            self.popDialog()
        pass

    def get(self, ui_name):
        return self.__ui_dict[ui_name]

    def robotEvent(self, eventName, eventArgs):
        self.robotUI.event(eventName, eventArgs)

    def robotMessage(self, message):
        self.robotUI.showMessage(message)

    def robotWakeUp(self):
        self.robotUI.wakeUp()

    def robotSleep(self):
        self.robotUI.sleep()

    pass


class BaseUI:
    """
    This is ui base class
    """

    ui_index = 0

    controls = None

    def __init__(self, ui_index):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ui_index = ui_index
        self.event_dispatcher = EventDispatcher()
        self.on_create()

    def on_create(self):
        self.logger.debug('UI created: {0}'.format(self))
        pass

    def add_control(self, control):
        if self.controls is None:
            self.controls = []
        self.controls.append(control)

    def paint(self):
        pass

    def update(self, surface = None):
        pass

    def update_offscreen(self):
        pass

    def onMouseDown(self, event):
        pass
    
    def onMouseUp(self, event):
        pass

    def onMouseMove(self, event):
        pass

    def onKeyPush(self, pushCount):
        pass

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds):
        pass

    def onKeyLongPress(self, escapedSeconds):
        pass

    def _show(self):
        # print('BaseUI _show')
        self.on_shown()

    def show(self):
        # print('BaseUI show')
        ui_manager = UIManager()
        ui_manager.push(self)
        self._show()

    def replace_current(self):
        ui_manager = UIManager()
        ui_manager.replace(self)
        self._show()

    def hide(self):
        ui_manager = UIManager()
        ui_manager.pop()
        self.on_hidden()
        ui_manager.current()._show()

    def on_shown(self):
        if self.controls is not None:
            self.logger.debug('UI on_shown: {0}, controls: {1}'.format(self, self.controls))
            for c in self.controls:
                c.paint()
        pass

    def on_hidden(self):
        pass

    def on_destroy(self):
        pass

    pass


class BaseControl(BaseUI):

    owner = None
    x = 0
    y = 0
    btn = None

    def __init__(self, owner):
        super().__init__(0)
        self.owner = owner

    def init(self, x, y, btn, **kwargs):
        self.x = x
        self.y = y
        self.btn = btn

    def do_command(self):
        pass

    def process_cmds(self, cmds):
        if len(cmds) == 0 or self.btn is None:
            return False

        cmd = cmds[0]

        if cmd == 'BN:{0}'.format(self.btn):
            self.do_command()
        pass

    def on_changed(self, value):
        pass


class ControlEvent(Event):
    CHANGED = "CHANGED"