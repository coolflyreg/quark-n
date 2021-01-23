#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import logging
import logging.config
import pygame
import time
from system.config import Config
from ui.core import UIManager
from periphery import GPIO
from periphery import LED
import _thread

# print('fontfile path: ', os.getcwd(), sys.path)
os.chdir(sys.path[0])
if bool(Config().get('debug.remote')):
    import pydevd
    pydevd.settrace('192.168.1.88', port=31000, stdoutToServer=True, stderrToServer=True)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('main')

gpio_key = GPIO("/dev/gpiochip1", 3, "in")
ledUser = LED("usr_led", True)

def runAsync(work):
    # loop = asyncio.get_event_loop()
    # task = asyncio.ensure_future(work)
    # result = loop.run(task)
    _thread.start_new_thread(work, ())
    pass

if not os.getenv('SDL_FBDEV'):
    os.putenv('SDL_FBDEV', Config().get('display.device'))#利用quark自带tft屏幕显示

pygame.init()
from ui.theme import *
game_clock = pygame.time.Clock()

display_info = pygame.display.Info()
w = display_info.current_w
h = display_info.current_h
window_size=(w,h)

game_surface = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
pygame.mouse.set_visible( False )

uiManager = UIManager()
uiManager.setWindowSize(window_size)
uiManager.setSurface(game_surface)
uiManager.init()

prevSecondIntValue = 0
prev_gpio_state = -1
current_gpio_state = 0
gpio_push_state = False
gpio_push_start = 0
gpio_push_count = 0

LongPressSeconds = (2,5,10)
LongPressSecondsState = [False, False, False]

def flashLed():
    # print('flash led')
    ledUser.write(255)
    time.sleep(0.1)
    ledUser.write(0)
    time.sleep(0.1)
    ledUser.write(255)
    time.sleep(0.1)
    ledUser.write(0)
    time.sleep(0.1)
    ledUser.write(255)

def checkGPIOKey(onPush, onRelease, onLongPress):
    global prev_gpio_state, gpio_push_state, gpio_push_start, gpio_push_count, LongPressSeconds, LongPressSecondsState
    gpio_state = gpio_key.read()
    if prev_gpio_state == -1:
        prev_gpio_state = gpio_state
        return 0
    
    escaped_push_time = pygame.time.get_ticks() - gpio_push_start
    long_press_second = int(escaped_push_time / 1000)
    
    if gpio_state != prev_gpio_state:
        if prev_gpio_state == 1: # push
            gpio_push_state = True
            gpio_push_start = pygame.time.get_ticks()
            if escaped_push_time < 400:
                gpio_push_count = gpio_push_count + 1
            if onPush is not None:
                onPush(gpio_push_count + 1)
        if prev_gpio_state == 0: # release
            gpio_push_state = False
            LongPressSecondsState = [False, False, False]
            if onRelease is not None:
                onRelease(escaped_push_time > 2000, gpio_push_count + 1, long_press_second)
        prev_gpio_state = gpio_state
        return 1
    if gpio_push_state:
        if escaped_push_time > 2000: # long press
            # gpio_push_state = False
            # prev_gpio_state = 0
            if onLongPress is not None and long_press_second in LongPressSeconds:
                idx = LongPressSeconds.index(long_press_second)
                if not LongPressSecondsState[idx]:
                    runAsync(flashLed)
                    LongPressSecondsState[idx] = True
                    onLongPress(long_press_second)
        pass
    
    if escaped_push_time > 400 and not gpio_push_state:
        gpio_push_count = 0
        # gpio_push_state = False

    return 0

def gpioKeyPush(pushCount):
    print('gpioKeyPush pushCount', pushCount)
    ledUser.write(255)
    uiManager.current().onKeyPush(pushCount)
    pass

def gpioKeyRelease(isLongPress, pushCount, longPressSeconds):
    print('gpioKeyRelease isLongPress', isLongPress, 'pushCount', pushCount, 'longPressSeconds', longPressSeconds)
    if uiManager.current().onKeyRelease(isLongPress, pushCount, longPressSeconds):
        return
    # if not isLongPress and pushCount == 1:
        # sysInfoShowType.next()
        # timeShowType.next()
        # dateShowType.next()
        # netShowType.next()
        # pass
    if isLongPress: 
        if longPressSeconds > 2 and longPressSeconds < 5:
            from ui.menu import MenuUI
            uiManager.get(MenuUI.__name__).show()
            pass
    ledUser.write(0)
    pass

def gpioKeyLongPress(escapedSeconds):
    # ledUser.write(0)
    print('long press', escapedSeconds)
    if escapedSeconds == 2:
        # sysInfoShowType.set_current(0)
        # timeShowType.set_current(0)
        # dateShowType.set_current(0)
        # netShowType.set_current(0)
        pass
    elif escapedSeconds == 5:
        pass
    elif escapedSeconds == 10:
        os.system("ttyecho -n /dev/tty1 PS1=\"\"")
        os.system("ttyecho -n /dev/tty1 clear")
        os.system("ttyecho -n /dev/tty1 systemctl poweroff -i")
        os.kill()
        # print("Power Off")
        pass
        
    pass

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

    pygame.draw.rect(game_surface, bg_color, (0, 0, current_x, 135))
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
    global current_PowerOff_x
    escaped_push_time = pygame.time.get_ticks() - gpio_push_start
    if gpio_push_state and escaped_push_time > 400:
        current_x = w * (escaped_push_time / 10000)
        current_PowerOff_x = current_x
    elif current_PowerOff_x > 0:
        current_PowerOff_x = current_PowerOff_x - 60
        if (current_PowerOff_x < 0):
            current_PowerOff_x = 0

    if (current_PowerOff_x > 0):
        drawLongPressStateView(escaped_push_time, current_PowerOff_x, (255, 0, 0) if escaped_push_time < 2000 else (0, 255, 0))
    pass

running = True
def main():
    global running
    
    mouseLastMotion = 0

    while True:
        for event in pygame.event.get():
            # print('pygame event', event)
            if event.type == pygame.QUIT:
                # running = False
                # pygame.quit()
                pass
            elif event.type == pygame.MOUSEMOTION:
                # print('pygame event', event)
                mouseLastMotion = 3
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # print('pygame event', event)
                uiManager.current().onMouseDown(event)
                # running = False
                # pygame.quit()
                pass
            # elif event.type == pygame.KEYDOWN:
            #     running = False
            #     pygame.quit()

        pygame.mouse.set_visible( mouseLastMotion > 0 )

        checkGPIOKey(gpioKeyPush, gpioKeyRelease, gpioKeyLongPress)

        if not running:
            break

        uiManager.update()
        
        drawLongPressState()

        pygame.display.update()
        game_clock.tick(60)
    pass


if __name__ == '__main__':
    main()