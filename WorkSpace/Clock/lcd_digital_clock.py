#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from datetime import datetime
import pygame
import os
import time
from periphery import GPIO
from periphery import LED
# import asyncio
# from threading import Thread
import _thread

from utils.stepper import Stepper
from utils.sysinfo import *

DEBUG = False
if DEBUG:
    import pydevd
    pydevd.settrace('192.168.1.88', port=31000, stdoutToServer=True, stderrToServer=True)

gpio_key = GPIO("/dev/gpiochip1", 3, "in")
ledUser = LED("usr_led", True)


def runAsync(work):
    # loop = asyncio.get_event_loop()
    # task = asyncio.ensure_future(work)
    # result = loop.run(task)
    _thread.start_new_thread(work, ())
    pass

if not os.getenv('SDL_FBDEV'):
    os.putenv('SDL_FBDEV', '/dev/fb1')#利用quark自带tft屏幕显示


NET_STATS = []
INTERFACE = 'wlan0'
def rx():
    ifstat = open('/proc/net/dev').readlines()
    for interface in  ifstat:
        if INTERFACE in interface:
            stat = float(interface.split()[1])
            NET_STATS[0:] = [stat]

def tx():
    ifstat = open('/proc/net/dev').readlines()
    for interface in  ifstat:
        if INTERFACE in interface:
            stat = float(interface.split()[9])
            NET_STATS[1:] = [stat]
rx()
tx()

pygame.init()

game_clock = pygame.time.Clock()
# game_clock.tick(120)

# icon = pygame.image.load('digitalClock.png')
# pygame.display.set_icon(icon)
display_info = pygame.display.Info()
w = display_info.current_w
h = display_info.current_h
window_size=(w,h)

screen = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
pygame.mouse.set_visible( False )
mouseLastMotion = 3
# pygame.display.set_caption('Digital Clock')
print('fontfile path: ', os.path.dirname(__file__))
fontPath = os.path.dirname(__file__) + "/fonts/DS-DIGIT.TTF"
largeFont = pygame.font.Font(fontPath, 82)
bigFont = pygame.font.Font(fontPath, 52)
middleFont = pygame.font.Font(fontPath, 40)
smallFont = pygame.font.Font(fontPath, 30)
miniFont = pygame.font.Font(fontPath, 26)
tinyFont = pygame.font.Font(fontPath, 24)

# bigFont = pygame.font.SysFont('DS-Digital',130)#Comic Sans MS
# smallFont = pygame.font.SysFont('DS-Digital',30)

white = (255,255,255)
black = (0,0,0)
green = (0,255,0)
red = (255,0,0)

months = ['January', 'February', 'March', 'April', 'May', 
'June', 'July', 'August', 'September', 'October', 'November', 'December']
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]

cputemp = cputempf()
cpuUse = str(getCpuUsage())

running = True

sysInfoRect = pygame.Rect(0, 0, w, 30)
sysInfoShowType = Stepper(0, 2, 1, 0)

timeRect = pygame.Rect(0, 31, w, 58)
timeShowType = Stepper(0, 1, 1, 0)

dateRect = pygame.Rect(0, 88, w, 24)
dateShowType = Stepper(0, 0, 1, 0)

netRect = pygame.Rect(0, 113, w, 22)
netShowType = Stepper(0, 1, 1, 0)

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
    pass

def gpioKeyRelease(isLongPress, pushCount, longPressSeconds):
    print('gpioKeyRelease isLongPress', isLongPress, 'pushCount', pushCount, 'longPressSeconds', longPressSeconds)
    if not isLongPress and pushCount == 1:
        sysInfoShowType.next()
        timeShowType.next()
        dateShowType.next()
        netShowType.next()
    ledUser.write(0)
    pass

def gpioKeyLongPress(escapedSeconds):
    # ledUser.write(0)
    print('long press', escapedSeconds)
    if escapedSeconds == 2:
        sysInfoShowType.set_current(0)
        timeShowType.set_current(0)
        dateShowType.set_current(0)
        netShowType.set_current(0)
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
    powerTxt = bigFont.render('POWER',True,black)
    offTxt = bigFont.render('OFF',True,black)
    power_x = w / 2 - powerTxt.get_width() / 2
    offTxt_x = w / 2 - offTxt.get_width() / 2
    okTxt = None
    ok_x = 5
    powerOffRemain = None
    nextTxt = None
    screenTxt = None

    long_press_second = int(escaped_push_time / 1000)
    if current_x > power_x and escaped_push_time >= 5000:
        powerOffRemain = miniFont.render(str(10 - long_press_second),True,black)
        pass
    else:
        powerTxt = None
    if current_x > offTxt_x and escaped_push_time >= 5000:
        pass
    else:
        offTxt = None
    if current_x > ok_x and escaped_push_time >= 2000 and escaped_push_time < 3000:
        okTxt = miniFont.render('YES',True,black)
        # okTxt = pygame.transform.rotate(okTxt, 270)
    if current_x > ok_x and escaped_push_time >= 3000 and escaped_push_time < 5000:
        nextTxt = miniFont.render('NEXT',True,black)
        screenTxt = miniFont.render('VIEW',True,black)

    pygame.draw.rect(screen, bg_color, (0, 0, current_x, 135))
    if powerTxt is not None:
        screen.blit(powerTxt, (power_x, 8), area=(0, 0, current_x - power_x, powerTxt.get_height()))
        if powerOffRemain is not None:
            screen.blit(powerOffRemain, (0,0))
    if offTxt is not None:
        screen.blit(offTxt, (offTxt_x, 65), area=(0, 0, current_x - offTxt_x, offTxt.get_height()))
    if okTxt is not None:
        screen.blit(okTxt, (ok_x, 25), area=(0, 0, current_x - ok_x, okTxt.get_height()))
    if nextTxt is not None:
        screen.blit(nextTxt, (ok_x, 25), area=(0, 0, current_x - ok_x, nextTxt.get_height()))
        screen.blit(screenTxt, (ok_x, 25 + screenTxt.get_height()), area=(0, 0, current_x - ok_x, screenTxt.get_height()))


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

while running:
    screen.fill(black)
    
    for event in pygame.event.get():
        # print('pygame event', event)
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        elif event.type == pygame.MOUSEMOTION:
            # print('pygame event', event)
            mouseLastMotion = 3
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # print('pygame event', event)
            if sysInfoRect.collidepoint(pygame.mouse.get_pos()):
                # print('pygame click on sys', event)
                sysInfoShowType.next()
            elif timeRect.collidepoint(pygame.mouse.get_pos()):
                # print('pygame click on time', event)
                timeShowType.next()
            elif dateRect.collidepoint(pygame.mouse.get_pos()):
                # print('pygame click on date', event)
                dateShowType.next()
            elif netRect.collidepoint(pygame.mouse.get_pos()):
                # print('pygame click on net', event)
                netShowType.next()
                # print('netShowType current', netShowType.current())
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

    now = datetime.now()
    today = datetime.today()

    minute = now.strftime('%M')
    second = now.strftime('%S')
    hour = int(now.strftime('%H'))
    month = now.strftime('%m')
    date = now.strftime('%d')
    year = now.strftime("%Y")
    day = today.weekday()
    day = days[day]
    secondIntValue = int(second)
    # RX_RATE = 0.0
    # TX_RATE = 0.0
    if prevSecondIntValue != secondIntValue:
        mouseLastMotion = mouseLastMotion - 1
        rxstat_o = list(NET_STATS)
        rx()
        tx()
        RX = float(NET_STATS[0])
        RX_O = rxstat_o[0]
        TX = float(NET_STATS[1])
        TX_O = rxstat_o[1]
        RX_RATE = round((RX - RX_O)/1024/1024,3)
        TX_RATE = round((TX - TX_O)/1024/1024,3)

    cpuUse = str(getCpuUsage()) # getCPUuse()
    memInfo = get_mem_info()
    memStr = "MEM {0}M".format(memInfo['free'])
    memUse = str(memInfo['percent'])
    dskInfo = get_disk_info()
    dskStr = "DSK {0}".format(dskInfo['free'])
    dskUse = str(dskInfo['percent'])

    if secondIntValue % 5 == 0:
        cputemp = cputempf()

    am = 'AM'
    
    if timeShowType.current() == 0 and hour > 12:
        hour = hour-12
        am = 'PM'

    shour = str(hour)
    if len(shour) == 1:
        shour = '0' + shour
    timeStr = shour + ':' + minute
    timeText = largeFont.render(timeStr,True,green)
    secondText = middleFont.render(second, True, green)
    monthText = smallFont.render(year + '-' + month + '-' + date,True,green)
    yearText = smallFont.render(year,True,green)
    amText = middleFont.render(am,True,green)
    dayText = smallFont.render( day,True,green)

    if sysInfoShowType.current() == 0:
        sysText = smallFont.render(cputemp, True, white)
        sysUseText = smallFont.render(cpuUse + '%', True, white)
    if sysInfoShowType.current() == 1:
        sysText = smallFont.render(memStr, True, white)
        sysUseText = smallFont.render(memUse + '%', True, white)
    if sysInfoShowType.current() == 2:
        sysText = smallFont.render(dskStr, True, white)
        sysUseText = smallFont.render(dskUse, True, white)
    netSpeedInText = tinyFont.render('' + str(RX_RATE) + ' M/s', True, green if RX_RATE > 0 else white)
    netSpeedOutText = tinyFont.render('' + str(TX_RATE) + ' M/s', True, green if TX_RATE > 0 else white)

    ip = get_host_ip()
    ipText = miniFont.render(ip, True, white)
    
    screen.blit(sysText, (10,0))
    screen.blit(sysUseText, (w - sysUseText.get_width() - 2,0))
    screen.blit(timeText, (4,16))
    screen.blit(secondText, (190, 52))
    screen.blit(monthText, (15,86))
    # screen.blit(yearText, (145,120))
    if timeShowType.current() == 0:
        screen.blit(amText,(190,22))
    screen.blit(dayText,(170,86))

    if netShowType.current() == 1:
        screen.blit(netSpeedOutText, (w - netSpeedOutText.get_width(), 112))
        screen.blit(netSpeedInText, (w / 2 - netSpeedInText.get_width(), 112))
    else:
        screen.blit(ipText,(10, 112))
        screen.blit(netSpeedOutText, (w - netSpeedOutText.get_width(), 112))
    
    drawLongPressState()

    prevSecondIntValue = secondIntValue
    pygame.display.update()
    # time.sleep(1.0/30.0)
    game_clock.tick(60)



gpio_key.close()
ledUser.close()