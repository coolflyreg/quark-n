import time
from ui.core import *
from ui.menu import *
import pygame


logger = logging.getLogger('ui.dialog')


class DialogBaseUI(BaseUI): 

    maskColor = (60, 30, 30, 128)
    title = None
    onAnimationEnd = None
    
    _animating = True
    _animationDuration = 300
    _animationTicks = -1
    _direction = 1

    def __init__(self, ui_index = 0, title = None, onAnimationEnd = None):
        super().__init__(ui_index)
        self.onAnimationEnd = onAnimationEnd
        self.title = title

    def show(self):
        ui_manager = UIManager()
        self._show()
        ui_manager.pushDialog(self)

    def replace_current(self):
        ui_manager = UIManager()
        self._show()
        ui_manager.replaceDialog(self)

    def hide(self):
        ui_manager = UIManager()
        ui_manager.popDialog()
        super().on_hidden()
        if ui_manager._currentDialog() is not None:
            ui_manager._currentDialog()._show()

    def zoomOut(self):
        self._direction = -1
        self._animationTicks = -1
        self._animating = True
        pass

    def updateContent(self, surface = None):
        pass

    def update(self, surface = None):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]

        surface2 = surface.convert_alpha()
        surface2.fill((255,255,255,0))

        pygame.draw.rect(surface2, self.maskColor, (0, 0, window_width, window_height))

        self.updateContent(surface2)

        if self._animationTicks == -1:
            self._animationTicks = (time.time() * 1000)
            return
        
        current_text = None
        if self.title is not None and self.title != '':
            current_text = zhMiniFont.render(self.title, True, color_white)

        if self._animating is True and ((time.time() * 1000) - self._animationTicks) < self._animationDuration: 
            # print('confirm menu animating')
            scale = ((time.time() * 1000) - self._animationTicks) / self._animationDuration
            if self._direction == -1:
                scale = 1 - scale
            # self._animationTicks = self._animationTicks - (time.time() * 1000)
            if current_text is not None:
                surface2.blit(current_text, (window_width / 2 - current_text.get_width() / 2, 0))
            surface2 = pygame.transform.scale(surface2, (int(surface2.get_width() * scale), int(surface2.get_height() * scale)))
            surface.blit(surface2, (window_width / 2 - surface2.get_width() / 2, window_height / 2 - surface2.get_height() / 2)) 

        else:
            self._animating = False
            if self._direction == -1:
                if (self.onAnimationEnd is not None):
                    try:
                        self.onAnimationEnd()
                    except IndexError as indexErr:
                        # print('ConfirmMenu index error', indexErr)
                        pass
            else:
                if current_text is not None:
                    surface2.blit(current_text, (window_width / 2 - current_text.get_width() / 2, 0))
                surface.blit(surface2, (0, 0))

        del surface2

        pass

    pass


class ConfirmMenu(MenuUI):
    ICONS = [
        IconAction('confirm', 'chenggong.png', '确定'),
        IconAction('cancel', 'close.png', '取消')
    ]

    onExecuteAction = None
    maskColor = (60, 30, 30, 128)

    def __init__(self, ui_index = 0, onExecuteAction = None):
        super().__init__(ui_index)
        self.onExecuteAction = onExecuteAction
        self.set_icons(self.ICONS)

    def executeAction(self):
        if (self.onExecuteAction is not None):
            try:
                self.onExecuteAction(self.ICONS[self.current_index].name)
            except IndexError as indexErr:
                logger.error('ConfirmMenu index error', indexErr)
                pass

    def zoomOut(self):
        self._direction = -1
        self._animationTicks = -1
        self._animating = True
        pass

    def update(self, surface = None):
        super().update(surface)
    pass


class ConfirmDialogUI(DialogBaseUI):
    
    menu = None
    onConfirm = None
    onCancel = None

    def __init__(self, ui_index = 0, confirmText = '请确认', onConfirm = None, onCancel = None):
        super().__init__(ui_index)
        self.menu = ConfirmMenu(onExecuteAction = lambda x: self.executeAction(x))
        self.onAnimationEnd = lambda: self.animationEnd()
        self.onConfirm = onConfirm
        self.onCancel = onCancel
        self.title = confirmText

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
        return self.menu.onKeyRelease(isLongPress, pushCount, longPressSeconds, keyIndex)

    def onKeyPush(self, pushCount, keyIndex):
        pass

    def onMouseUp(self, event):
        self.menu.onMouseUp(event)

    def animationEnd(self):
        x = self.menu.ICONS[self.menu.current_index].name
        if x == 'confirm':
            if self.onConfirm is not None:
                self.onConfirm()
            self.hide()
        if x == 'cancel':
            if self.onCancel is not None:
                self.onCancel()
            self.hide()
        pass

    def executeAction(self, x):
        self.zoomOut()

    def updateContent(self, surface = None):
        self.menu.update(surface)
        pass

    pass


class ModifyIntValueDialogUI(DialogBaseUI):
    
    def __init__(self, ui_index = 0, confirmText = '修改值', onConfirm = None, onCancel = None):
        super().__init__(ui_index)
        self.menu = ConfirmMenu(onExecuteAction = lambda x: self.executeAction(x))
        self.onAnimationEnd = lambda: self.animationEnd()
        self.onConfirm = onConfirm
        self.onCancel = onCancel
        self.title = confirmText

    pass
