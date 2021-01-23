#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import logging.config
import pygame
from ui.core import UIManager, BaseUI
from ui.theme import *
from utils.stepper import Stepper
from utils.sysinfo import *

logger = logging.getLogger('ui.clock')

class ClockUI(BaseUI):

    showTick = 0
    NET_STATS = []
    INTERFACE = 'wlan0'

    sysInfoRect = pygame.Rect(0, 0, UIManager().getWindowSize()[0], 30)
    sysInfoShowType = Stepper(0, 2, 1, 0)

    timeRect = pygame.Rect(0, 31, UIManager().getWindowSize()[0], 58)
    timeShowType = Stepper(0, 1, 1, 0)

    dateRect = pygame.Rect(0, 88, UIManager().getWindowSize()[0], 24)
    dateShowType = Stepper(0, 0, 1, 0)

    netRect = pygame.Rect(0, 113, UIManager().getWindowSize()[0], 22)
    netShowType = Stepper(0, 1, 1, 0)

    prevSecondIntValue = 0
    RX_RATE = 0
    TX_RATE = 0

    cputemp = None

    months = ['January', 'February', 'March', 'April', 'May', 
    'June', 'July', 'August', 'September', 'October', 'November', 'December']
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]

    def rx(self):
        ifstat = open('/proc/net/dev').readlines()
        for interface in  ifstat:
            if self.INTERFACE in interface:
                stat = float(interface.split()[1])
                self.NET_STATS[0:] = [stat]

    def tx(self):
        ifstat = open('/proc/net/dev').readlines()
        for interface in  ifstat:
            if self.INTERFACE in interface:
                stat = float(interface.split()[9])
                self.NET_STATS[1:] = [stat]

    def on_shown(self):
        self.showTick = pygame.time.get_ticks()
        self.cputemp = cputempf()
        self.rx()
        self.tx()
        pass

    def on_hidden(self):
        pass

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds):
        if not isLongPress and pushCount == 1:
            self.sysInfoShowType.next()
            self.timeShowType.next()
            self.dateShowType.next()
            self.netShowType.next()

    def onMouseDown(self, event):
        if self.sysInfoRect.collidepoint(pygame.mouse.get_pos()):
            self.sysInfoShowType.next()
        elif self.timeRect.collidepoint(pygame.mouse.get_pos()):
            self.timeShowType.next()
        elif self.dateRect.collidepoint(pygame.mouse.get_pos()):
            self.dateShowType.next()
        elif self.netRect.collidepoint(pygame.mouse.get_pos()):
            self.netShowType.next()

    def update(self):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)

        now = datetime.now()
        today = datetime.today()

        minute = now.strftime('%M')
        second = now.strftime('%S')
        hour = int(now.strftime('%H'))
        month = now.strftime('%m')
        date = now.strftime('%d')
        year = now.strftime("%Y")
        day = today.weekday()
        day = self.days[day]
        secondIntValue = int(second)
        # RX_RATE = 0.0
        # TX_RATE = 0.0
        if self.prevSecondIntValue != secondIntValue:
            # mouseLastMotion = mouseLastMotion - 1
            rxstat_o = list(self.NET_STATS)
            self.rx()
            self.tx()
            RX = float(self.NET_STATS[0])
            RX_O = rxstat_o[0]
            TX = float(self.NET_STATS[1])
            TX_O = rxstat_o[1]
            self.RX_RATE = round((RX - RX_O)/1024/1024,3)
            self.TX_RATE = round((TX - TX_O)/1024/1024,3)

        cpuUse = str(getCpuUsage()) # getCPUuse()
        memInfo = get_mem_info()
        memStr = "MEM {0}M".format(memInfo['free'])
        memUse = str(memInfo['percent'])
        dskInfo = get_disk_info()
        dskStr = "DSK {0}".format(dskInfo['free'])
        dskUse = str(dskInfo['percent'])

        if secondIntValue % 5 == 0:
            self.cputemp = cputempf()

        am = 'AM'
        
        if self.timeShowType.current() == 0 and hour > 12:
            hour = hour-12
            am = 'PM'

        shour = str(hour)
        if len(shour) == 1:
            shour = '0' + shour
        timeStr = shour + ':' + minute
        timeText = largeFont.render(timeStr, True, color_green)
        secondText = middleFont.render(second, True, color_green)
        monthText = smallFont.render(year + '-' + month + '-' + date, True, color_green)
        yearText = smallFont.render(year, True, color_green)
        amText = middleFont.render(am, True, color_green)
        dayText = smallFont.render( day, True, color_green)

        if self.sysInfoShowType.current() == 0:
            sysText = smallFont.render(self.cputemp, True, color_white)
            sysUseText = smallFont.render(cpuUse + '%', True, color_white)
        if self.sysInfoShowType.current() == 1:
            sysText = smallFont.render(memStr, True, color_white)
            sysUseText = smallFont.render(memUse + '%', True, color_white)
        if self.sysInfoShowType.current() == 2:
            sysText = smallFont.render(dskStr, True, color_white)
            sysUseText = smallFont.render(dskUse, True, color_white)
        netSpeedInText = tinyFont.render('' + str(self.RX_RATE) + ' M/s', True, color_green if self.RX_RATE > 0 else color_white)
        netSpeedOutText = tinyFont.render('' + str(self.TX_RATE) + ' M/s', True, color_green if self.TX_RATE > 0 else color_white)

        ip = get_host_ip()
        ipText = miniFont.render(ip, True, color_white)
        
        surface.blit(sysText, (10,0))
        surface.blit(sysUseText, (window_width - sysUseText.get_width() - 2,0))
        surface.blit(timeText, (4,16))
        surface.blit(secondText, (190, 52))
        surface.blit(monthText, (15,86))
        # surface.blit(yearText, (145,120))
        if self.timeShowType.current() == 0:
            surface.blit(amText,(190,22))
        surface.blit(dayText,(170,86))

        if self.netShowType.current() == 1:
            surface.blit(netSpeedOutText, (window_width - netSpeedOutText.get_width(), 112))
            surface.blit(netSpeedInText, (window_width / 2 - netSpeedInText.get_width(), 112))
        else:
            surface.blit(ipText,(10, 112))
            surface.blit(netSpeedOutText, (window_width - netSpeedOutText.get_width(), 112))
        
        self.prevSecondIntValue = secondIntValue
        # welcomeTxt = bigFont.render(ClockUI.__name__, True, color_white)
        # surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, window_height / 2 - welcomeTxt.get_height() / 2))
        pass

    pass