#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import threading
from ruamel.yaml import YAML
import logging
import logging.config

import pygame
import time
import signal
from periphery import GPIO
from periphery import LED
import _thread
from system.config import Config

from utils import *

from server import service
from ui.core import UIManager
from drivers.mpu6050 import mpu6050

logger = logging.getLogger('App')

logger.debug('debug log')
logger.info('info log')
logger.warn('warn log')
logger.error('error log')
logger.critical('critical log')

##############
### periphery init
##############

class GPIOKeyState:
    gpio_key = None
    prev_gpio_state = -1
    gpio_push_state = False
    gpio_push_start = 0
    gpio_push_count = 0

    LongPressSeconds = (2,5,10)
    LongPressSecondsState = [False, False, False]

    def __init__(self, gpio_key):
        self.gpio_key = gpio_key
        self.prev_gpio_state = -1
        self.gpio_push_state = False
        self.gpio_push_start = 0
        self.gpio_push_count = 0
        self.LongPressSeconds = (2,5,10)
        self.LongPressSecondsState = [False, False, False]
    pass

gpio_keys = []
gpio_key1 = GPIO("/dev/gpiochip1", 3, "in")
gpio_keys.append(GPIOKeyState(gpio_key1))
try:
    gpio_key2 = GPIO("/dev/gpiochip1", 4, "in")
    gpio_keys.append(GPIOKeyState(gpio_key2))
except: 
    pass

ledUser = LED("usr_led", True)

##############
### pid file init
##############
def writePid():
    pid = str(os.getpid())
    f = open(Config().get('monitor.pid-file', '/run/ui_clock.pid'), 'w')
    f.write(pid)
    f.close()

writePid()

##############
### pygame init
##############
if not os.getenv('SDL_FBDEV'):
    os.putenv('SDL_FBDEV', Config().get('display.device'))#利用quark自带tft屏幕显示
# if not os.getenv('fbcon'):
#     os.putenv('fbcon', 'map:1')#利用quark自带tft屏幕显示
# if not os.getenv('SDL_VIDEODRIVER'):
    # os.putenv('SDL_VIDEODRIVER', 'DirectFB')#利用quark自带tft屏幕显示
# if not os.getenv('SDL_RENDER_DRIVER'):
#     os.putenv('SDL_RENDER_DRIVER', 'fbcon')


logger.debug('pygame initing')
pygame.init()
logger.debug('pygame inited')
pygame.mixer.quit()

from ui.theme import *
game_clock = pygame.time.Clock()

# if pygame.version.vernum.major == 2:
pygame.display.init()
display_info = pygame.display.Info()
w = display_info.current_w
h = display_info.current_h
window_size=(w,h)

game_surface = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
pygame.mouse.set_visible( False )
mouseLastMotion = 0


# num_devices = pygame._sdl2.touch.get_num_devices()
# logger.debug('Touch Device Count %d' % num_devices)

##############
### UIManager init
##############
uiManager = UIManager()
uiManager.setWindowSize(window_size)
uiManager.setSurface(game_surface)
uiManager.init()

def gotoMenu():
    from ui.menu import MenuUI
    uiManager.closeAllDialog()
    uiManager.replace(uiManager.get(MenuUI.__name__), root=True)

def flashLed():
    # logger.debug('flash led')
    ledUser.write(ledUser.max_brightness)
    time.sleep(0.1)
    ledUser.write(0)
    time.sleep(0.1)
    ledUser.write(ledUser.max_brightness)
    time.sleep(0.1)
    ledUser.write(0)
    time.sleep(0.1)
    ledUser.write(ledUser.max_brightness)

##############
### MPU 6050
##############
if bool(Config().get('user-interface.mpu-motion')) is True:
    mpu = mpu6050()
    mpu.init(mpu.MPU6050_ADDRESS, scale=mpu.MPU6050_SCALE_2000DPS, a_range=mpu.MPU6050_RANGE_16G)
    # mpu.set_gyro_range(0x18)
    mpu.setAccelPowerOnDelay(mpu.MPU6050_DELAY_3MS)
    mpu.setIntFreeFallEnabled(False);  
    mpu.setIntZeroMotionEnabled(True)
    mpu.setIntMotionEnabled(True)
    mpu.setDHPFMode(mpu.MPU6050_DHPF_5HZ)
    mpu.setMotionDetectionThreshold(3)
    mpu.setMotionDetectionDuration(5)
    mpu.setZeroMotionDetectionThreshold(4)
    mpu.calibration()
    mpu.calibrateGyro(100)
lastCheckMpuTicks = 0
lastRecordMpuTicks = 0

mpu6050_motion = {
    'isNegActivityOnX': 0,
    'isPosActivityOnX': 0,
    'isNegActivityOnY': 0,
    'isPosActivityOnY': 0,
    'isNegActivityOnZ': 0,
    'isPosActivityOnZ': 0
}

def resetMpuMotion():
    global mpu6050_motion, lastRecordMpuTicks
    lastRecordMpuTicks = (time.time() * 1000)
    mpu6050_motion['isNegActivityOnX'] = 0
    mpu6050_motion['isPosActivityOnX'] = 0
    mpu6050_motion['isNegActivityOnY'] = 0
    mpu6050_motion['isPosActivityOnY'] = 0
    mpu6050_motion['isNegActivityOnZ'] = 0
    mpu6050_motion['isPosActivityOnZ'] = 0

def recordMpuMotion(activities):
    global mpu6050_motion, lastRecordMpuTicks
    mpu6050_motion['isNegActivityOnX'] += activities['isNegActivityOnX']
    mpu6050_motion['isPosActivityOnX'] += activities['isPosActivityOnX']
    mpu6050_motion['isNegActivityOnY'] += activities['isNegActivityOnY']
    mpu6050_motion['isPosActivityOnY'] += activities['isPosActivityOnY']
    mpu6050_motion['isNegActivityOnZ'] += activities['isNegActivityOnZ']
    mpu6050_motion['isPosActivityOnZ'] += activities['isPosActivityOnZ']

    if activities['isNegActivityOnX'] or activities['isPosActivityOnX'] or activities['isNegActivityOnY'] or activities['isPosActivityOnY'] or activities['isNegActivityOnZ'] or activities['isPosActivityOnZ']:
        lastRecordMpuTicks = (time.time() * 1000)
        return True
    return False

def checkMPU():
    global mpu, lastCheckMpuTicks, lastRecordMpuTicks, mpu6050_motion

    if bool(Config().get('user-interface.mpu-motion')) is False:
        return

    mpu.get_all_data()
    activities = mpu.read_activites()
    recorded = recordMpuMotion(activities)
    handled = False
    current_ticks = (time.time() * 1000)
    if mpu6050_motion['isNegActivityOnZ'] > 3 or mpu6050_motion['isPosActivityOnZ'] > 3:
        handled = True
        gotoMenu()
    elif (current_ticks - lastCheckMpuTicks) > 500:
        logger.debug('ui activities {}'.format(mpu6050_motion))
        handled = uiManager.current().onMpu(activities = mpu6050_motion)

    if handled is True:
        resetMpuMotion()
        lastCheckMpuTicks = current_ticks
    elif (current_ticks - lastRecordMpuTicks) > 300:
        lastCheckMpuTicks = (time.time() * 1000)
        resetMpuMotion()

    if recorded:
        logger.debug('motion {}'.format(mpu6050_motion))

    pass

##############
### GPIO Key behaviour
##############
# prev_gpio_state = -1
# gpio_push_state = False
# gpio_push_start = 0
# gpio_push_count = 0

# LongPressSeconds = (2,5,10)
# LongPressSecondsState = [False, False, False]


def checkGPIOKey(onPush, onRelease, onLongPress):
    # global prev_gpio_state, gpio_push_state, gpio_push_start, gpio_push_count, LongPressSeconds, LongPressSecondsState
    global gpio_keys
    # if gpio_key is None:
    #     return 0
    if gpio_keys is None or len(gpio_keys) == 0:
        return 0
    for gpio_key_state_obj in gpio_keys:
        index = gpio_keys.index(gpio_key_state_obj)
        gpio_key = gpio_key_state_obj.gpio_key
        gpio_state = gpio_key.read()
        if gpio_key_state_obj.prev_gpio_state == -1:
            gpio_key_state_obj.prev_gpio_state = gpio_state
            return 0
        
        escaped_push_time = pygame.time.get_ticks() - gpio_key_state_obj.gpio_push_start
        long_press_second = int(escaped_push_time / 1000)
        
        if gpio_state != gpio_key_state_obj.prev_gpio_state:
            if gpio_key_state_obj.prev_gpio_state == 1: # push
                gpio_key_state_obj.gpio_push_state = True
                gpio_key_state_obj.gpio_push_start = pygame.time.get_ticks()
                if escaped_push_time < 400:
                    gpio_key_state_obj.gpio_push_count = gpio_key_state_obj.gpio_push_count + 1
                if onPush is not None:
                    onPush(gpio_key_state_obj.gpio_push_count + 1, index)
            if gpio_key_state_obj.prev_gpio_state == 0: # release
                gpio_key_state_obj.gpio_push_state = False
                gpio_key_state_obj.LongPressSecondsState = [False, False, False]
                if onRelease is not None:
                    onRelease(escaped_push_time > 2000, gpio_key_state_obj.gpio_push_count + 1, long_press_second, index)
            gpio_key_state_obj.prev_gpio_state = gpio_state
            return 1
        if gpio_key_state_obj.gpio_push_state:
            if escaped_push_time > 2000: # long press
                # gpio_key_state_obj.gpio_push_state = False
                # gpio_key_state_obj.prev_gpio_state = 0
                if onLongPress is not None and long_press_second in gpio_key_state_obj.LongPressSeconds:
                    idx = gpio_key_state_obj.LongPressSeconds.index(long_press_second)
                    if not gpio_key_state_obj.LongPressSecondsState[idx]:
                        runAsync(flashLed)
                        gpio_key_state_obj.LongPressSecondsState[idx] = True
                        onLongPress(long_press_second, index)
            pass
        
        if escaped_push_time > 400 and not gpio_key_state_obj.gpio_push_state:
            gpio_key_state_obj.gpio_push_count = 0
            # gpio_key_state_obj.gpio_push_state = False

    return 0

def gpioKeyPush(pushCount, keyIndex):
    logger.debug('gpioKeyPush pushCount %d on key[%d]', pushCount, keyIndex)
    ledUser.write(ledUser.max_brightness)
    uiManager.current().onKeyPush(pushCount, keyIndex)
    pass

def gpioKeyRelease(isLongPress, pushCount, longPressSeconds, keyIndex):
    logger.debug('gpioKeyRelease isLongPress %d pushCount %d longPressSeconds %d on key[%d]', isLongPress, pushCount, longPressSeconds, keyIndex)
    if uiManager.current().onKeyRelease(isLongPress, pushCount, longPressSeconds, keyIndex):
        return
    # if not isLongPress and pushCount == 1:
        # pass
    if isLongPress: 
        if longPressSeconds > 2 and longPressSeconds < 5:
            gotoMenu()
            pass
    ledUser.write(0)
    pass

def gpioKeyLongPress(escapedSeconds, keyIndex):
    # ledUser.write(0)
    logger.debug('long press %d on key[%d]', escapedSeconds, keyIndex)
    if escapedSeconds == 2:
        pass
    elif escapedSeconds == 5:
        pass
    elif escapedSeconds == 10:
        os.system("ttyecho -n /dev/tty1 PS1=\"\"")
        os.system("ttyecho -n /dev/tty1 clear")
        os.system("ttyecho -n /dev/tty1 systemctl poweroff -i")
        os.kill()
        logger.info("Power Off")
        pass
        
    pass

def mouseIsVisible():
    global mouseLastMotion
    return ((time.time() * 1000) - mouseLastMotion) < 3000

def drawLongPressStateView(escaped_push_time, current_x, bg_color):
    powerTxt = bigFont.render('POWER', True, color_black)
    offTxt = bigFont.render('OFF', True, color_black)
    power_x = w / 2 - powerTxt.get_width() / 2
    offTxt_x = w / 2 - offTxt.get_width() / 2
    okTxt = None
    ok_x = 5
    powerOffRemain = None
    nextTxt = None
    screenTxt = None

    long_press_second = int(escaped_push_time / 1000)

    if current_x > power_x and escaped_push_time >= 5000:
        powerOffRemain = miniFont.render(str(10 - long_press_second), True, color_black)
        pass
    else:
        powerTxt = None
    if current_x > offTxt_x and escaped_push_time >= 5000:
        pass
    else:
        offTxt = None
    if current_x > ok_x and escaped_push_time >= 2000 and escaped_push_time < 3000:
        okTxt = miniFont.render('YES', True, color_black)
        # okTxt = pygame.transform.rotate(okTxt, 270)
    if current_x > ok_x and escaped_push_time >= 3000 and escaped_push_time < 5000:
        nextTxt = miniFont.render('MENU', True, color_black)
        screenTxt = miniFont.render('VIEW', True, color_black)

    pygame.draw.rect(game_surface, bg_color, (0, 0, current_x, window_size[1]))
    if powerTxt is not None:
        game_surface.blit(powerTxt, (power_x, 8), area=(0, 0, current_x - power_x, powerTxt.get_height()))
        if powerOffRemain is not None:
            game_surface.blit(powerOffRemain, (0,0))
    if offTxt is not None:
        game_surface.blit(offTxt, (offTxt_x, 65), area=(0, 0, current_x - offTxt_x, offTxt.get_height()))
    if okTxt is not None:
        game_surface.blit(okTxt, (ok_x, 25), area=(0, 0, current_x - ok_x, okTxt.get_height()))
    if nextTxt is not None:
        game_surface.blit(nextTxt, (ok_x, 25), area=(0, 0, current_x - ok_x, nextTxt.get_height()))
        game_surface.blit(screenTxt, (ok_x, 25 + screenTxt.get_height()), area=(0, 0, current_x - ok_x, screenTxt.get_height()))


current_PowerOff_x = 0
def drawLongPressState():
    global current_PowerOff_x, gpio_keys
    escaped_push_time = pygame.time.get_ticks() - gpio_keys[0].gpio_push_start
    if gpio_keys[0].gpio_push_state and escaped_push_time > 400:
        current_x = w * (escaped_push_time / 10000)
        current_PowerOff_x = current_x
    elif current_PowerOff_x > 0:
        current_PowerOff_x = current_PowerOff_x - 60
        if (current_PowerOff_x < 0):
            current_PowerOff_x = 0

    if mouseIsVisible():
        pos = pygame.mouse.get_pos()
        if SIDE_MENU_RECT.collidepoint(pos):
            from ui.menu import MenuUI
            if uiManager.current().__class__.__name__ == MenuUI.__name__:
                escaped_push_time = 2500
            else:
                escaped_push_time = 3500
            current_PowerOff_x = w * (escaped_push_time / 10000)
        pass

    if (current_PowerOff_x > 0):
        drawLongPressStateView(escaped_push_time, current_PowerOff_x, (255, 0, 0) if escaped_push_time < 2000 else (0, 255, 0))
    pass

##############
### signal handler
##############
def _signal_handler(signal, frame):
    print('_signal_handler', signal, frame)
    global uiManager, ledUser, gpio_keys
    service.stop_server()
    # time.sleep(1)
    # logger.debug('threading.active_count() = %d', threading.active_count())
    # dumpThreads('_signal_handler')
    uiManager.quit()
    if ledUser is not None:
        ledUser.close()
        ledUser = None
    if gpio_keys is not None :
        for gpio_key_state_obj in gpio_keys:
            if gpio_key_state_obj.gpio_key is not None:
                gpio_key_state_obj.gpio_key.close()
                gpio_key_state_obj.gpio_key = None
    pidFile = Config().get('monitor.pid-file', '/run/ui_clock.pid')
    if (os.path.exists(pidFile) and os.path.isfile(pidFile)):
        os.remove(pidFile)
    
##############
### main loop
##############
def main():
    from ui.menu import MenuUI
    global uiManager
    global mouseLastMotion

    surface2 = uiManager.surface.convert_alpha()
    surface2.fill((255,255,255,0))

    MenuUI_name = MenuUI.__name__
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    service.run(uiManager)

    while uiManager.isRunning():
        for event in pygame.event.get():
            # logger.debug('event = {}'.format(event))
            if event.type == pygame.QUIT:
                uiManager.quit()
                return
                pass
            elif event.type == pygame.MOUSEMOTION:
                mouseLastMotion = (time.time() * 1000)
                uiManager.current().onMouseMove(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseLastMotion = (time.time() * 1000)
                uiManager.current().onMouseDown(event)
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                mouseLastMotion = (time.time() * 1000)
                if mouseIsVisible():
                    pos = pygame.mouse.get_pos()
                    if SIDE_MENU_RECT.collidepoint(pos):
                        if uiManager.current().__class__.__name__ == MenuUI_name:
                            pass
                        else:
                            gotoMenu()
                            continue
                uiManager.current().onMouseUp(event)
                pass

        pygame.mouse.set_visible( mouseIsVisible() )

        checkGPIOKey(gpioKeyPush, gpioKeyRelease, gpioKeyLongPress)

        checkMPU()

        if not uiManager.isRunning():
            break

        uiManager.update()
        
        drawLongPressState()

        pygame.display.update()
        game_clock.tick(30)

    pygame.quit()
