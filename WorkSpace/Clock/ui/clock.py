#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from datetime import datetime
import logging
import logging.config
import pygame
from system.config import Config
from ui.core import UIManager, BaseUI
from ui.theme import *
from utils.stepper import Stepper
from utils.sysinfo import *
from utils import runAsync, clampPercent

logger = logging.getLogger('ui.clock')

class ClockUI(BaseUI):

    showTick = 0
    NET_STATS = []
    INTERFACE = 'wlan0'

    sysInfoShowType = Stepper(0, 2, 1, 0)
    timeShowType = Stepper(0, 1, 1, 0)
    dateShowType = Stepper(0, 0, 1, 0)
    netShowType = Stepper(0, 1, 1, 0)

    windowSize = UIManager().getWindowSize()
    window_width = windowSize[0]
    window_height = windowSize[1]
    if window_width == 320:
        sysInfoRect = pygame.Rect(0, 0, UIManager().getWindowSize()[0], int(window_height * (30 / 135)))
        timeRect = pygame.Rect(0, int(window_height * (31 / 135)), UIManager().getWindowSize()[0], int(window_height * (58 / 135)))
        dateRect = pygame.Rect(0, int(window_height * (88 / 135)), UIManager().getWindowSize()[0], int(window_height * (24 / 135)))
        netRect = pygame.Rect(0, int(window_height * (113 / 135)), UIManager().getWindowSize()[0], int(window_height * (22 / 135)))
    else:
        sysInfoRect = pygame.Rect(0, 0, UIManager().getWindowSize()[0], 30)
        timeRect = pygame.Rect(0, 31, UIManager().getWindowSize()[0], 58)
        dateRect = pygame.Rect(0, 88, UIManager().getWindowSize()[0], 24)
        netRect = pygame.Rect(0, 113, UIManager().getWindowSize()[0], 22)

    prevSecondIntValue = 0
    RX_RATE = 0
    TX_RATE = 0

    lastCpuInfo = readCpuInfo()
    cpuUse = 0
    cpuUseRemain = 0
    memInfo = get_mem_info()
    dskInfo = get_disk_info()
    hostIp = get_host_ip()

    animation_values = {}
    
    cputemp = None

    hide_second_symbol = False

    months = ['January', 'February', 'March', 'April', 'May', 
    'June', 'July', 'August', 'September', 'October', 'November', 'December']
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]
    # days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日' ]

    def getAnimationValue(self, key, currentValue, stepValue):
        if self.animation_values.__contains__(key):
            if (currentValue > (self.animation_values[key] + stepValue)):
                self.animation_values[key] = self.animation_values[key] + stepValue
            elif (currentValue < (self.animation_values[key] - stepValue)):
                self.animation_values[key] = self.animation_values[key] - stepValue
            else:
                self.animation_values[key] = currentValue
        else:
            self.animation_values[key] = currentValue
        return self.animation_values[key]

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
        # if int(Config().get('user-interface.clock.style')) is not None:
        style = int(Config().get('user-interface.clock.style', 2))
        if style < 1 or style > 2:
            self.ui_style = 2
        else:
            self.ui_style = style
        # else:
        #     self.ui_style = 2
        self.showTick = pygame.time.get_ticks()
        cputempStr, cpuTempValue = cputempf()
        self.cputemp = cputempStr
        self.cputempValue = cpuTempValue
        self.rx()
        self.tx()
        self.lastCpuInfo = readCpuInfo()
        pass

    def on_hidden(self):
        pass

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
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
    
    def onTouchEnd(self, event):
        if self.sysInfoRect.collidepoint(event):
            self.sysInfoShowType.next()
        elif self.timeRect.collidepoint(event):
            self.timeShowType.next()
        elif self.dateRect.collidepoint(event):
            self.dateShowType.next()
        elif self.netRect.collidepoint(event):
            self.netShowType.next()
        pass

    def drawMeterIndicator(self, surface, percentValue, right = False):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]

        indicator_merge_space = 4
        w_height = window_height
        if window_height == 320:
            indicator_merge_space = 10
            indicator_line_count = 22
        if window_height == 240:
            indicator_merge_space = 6
            indicator_line_count = 26
        if window_height == 135:
            indicator_line_count = 19
            # w_height -= 1

        value_step = 100 / indicator_line_count

        indicator_line_space = 2
        indicator_line_height = (w_height - indicator_merge_space - indicator_line_space * indicator_line_count + indicator_line_space) / indicator_line_count
        top_count = 4 # 最上方长条的数量
        base_width = indicator_line_height
        normal_width_step = 1
        for y_index in range(indicator_line_count, -1, -1):
            if y_index >= (indicator_line_count - top_count):
                width = (2 * (top_count - (indicator_line_count - y_index)) * (top_count - (indicator_line_count - y_index))) + (y_index * normal_width_step + base_width)
                if y_index == indicator_line_count:
                    fill_color = (255,0,0)
                elif y_index == indicator_line_count - 1:
                    fill_color = (255,128,0)
                elif y_index == indicator_line_count - 2:
                    fill_color = (255,198,0)
                elif y_index == indicator_line_count - 3:
                    fill_color = (255,255,0)
                elif y_index == indicator_line_count - 4:
                    fill_color = (184,255,0)
            else:
                width = normal_width_step * y_index + base_width
                fill_color = (0,255,0)
            y = y_index * indicator_line_height - indicator_merge_space / 2 + (y_index * indicator_line_space + indicator_line_space)

            pygame.draw.rect(surface, (128,128,200), (0 if right == False else (window_width - width), window_height - y, width, indicator_line_height), 1)

            if (percentValue / value_step) >= y_index:
                surface.fill(fill_color, (0 if right == False else (window_width - width), window_height - y, width, indicator_line_height))

    def update(self, surface = None):
        if self.ui_style == 1:
            self.update_style_1(surface)
        if self.ui_style == 2:
            self.update_style_2(surface)

    def update_style_2(self, surface = None):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)
        # surface.fill((255,255,255))

        # gether data
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
            if len(self.NET_STATS) > 0:
                RX = float(self.NET_STATS[0])
                RX_O = rxstat_o[0]
                TX = float(self.NET_STATS[1])
                TX_O = rxstat_o[1]
                self.RX_RATE = round((RX - RX_O)/1024/1024,3)
                self.TX_RATE = round((TX - TX_O)/1024/1024,3)
            else:
                RX = 0.0
                RX_O = 0
                TX = 0.0
                TX_O = 0
                self.RX_RATE = 0
                self.TX_RATE = 0

            self.memInfo = get_mem_info()
            self.dskInfo = get_disk_info()
            self.hostIp = get_host_ip()

            cpuInfo = readCpuInfo()
            self.cpuUse = round(calcCpuUsage(self.lastCpuInfo, cpuInfo), 1) # getCPUuse()
            self.lastCpuInfo = cpuInfo

            self.hide_second_symbol = not self.hide_second_symbol

        cpuUse = str(self.cpuUse)
        memInfo = self.memInfo
        # memStr = "MEM {0}M".format(memInfo['free'])
        memUse = memInfo['percent']
        dskInfo = self.dskInfo
        # dskStr = "DSK {0}".format(dskInfo['free'])
        dskUse = dskInfo['used_percent']

        if secondIntValue % 5 == 0:
            cputempStr, cpuTempValue = cputempf()
            self.cputemp = cputempStr
            self.cputempValue = cpuTempValue

        shour = str(hour)
        if len(shour) == 1:
            shour = '0' + shour
        timeStr = shour + ':' + minute
        timeStr = '88:88'

        # timeText = largeFont.render(timeStr, True, color_green)
        secondText = self.get_cache('secondText_{}'.format(second), lambda: middleFont.render(second, True, color_green))
        # amText = self.get_cache('amText_{}'.format(am), lambda: middleFont.render(am, True, color_green))

        rxStr = '' + str(self.RX_RATE) + ' M/s'
        txStr = '' + str(self.TX_RATE) + ' M/s'

        ip = self.hostIp
        # ip = '192.168.255.255'
        ipText = self.get_cache('ip_{}'.format(ip), lambda: miniFont.render(ip, True, color_white))

        # end - gether data

        sysTitle = ''
        if self.sysInfoShowType.current() == 0: # cpu
            sysTitle = 'CPU'
            self.drawMeterIndicator(surface, self.getAnimationValue('cpuUse', self.cpuUse, 5))
            self.drawMeterIndicator(surface, clampPercent(self.cputempValue, 20, 100), right = True)
        if self.sysInfoShowType.current() == 1: # memory
            sysTitle = 'MEMORY'
            # print(memInfo)
            self.drawMeterIndicator(surface, self.getAnimationValue('memUse', memUse, 5))
            self.drawMeterIndicator(surface, memInfo['swap']['used'] / memInfo['swap']['total'] * 100, right = True)
        if self.sysInfoShowType.current() == 2: #disk
            sysTitle = 'DISK'
            # print(dskUse, dskInfo['free'], dskInfo['total'], dskInfo['free_percent'], dskInfo['used_percent'])
            self.drawMeterIndicator(surface, self.getAnimationValue('dskUse', dskUse, 5))
            self.drawMeterIndicator(surface, dskInfo['free_percent'], right = True)

        sysText = self.get_cache('sysText_{}'.format(sysTitle), lambda: smallFont.render(sysTitle, True, color_white))

        if window_width == 320:
            netSpeedInText = self.get_cache('rxStr_{}'.format(rxStr), lambda: tinyFont.render(rxStr, True, color_green if self.RX_RATE > 0 else color_white))
            netSpeedOutText = self.get_cache('txStr_{}'.format(txStr), lambda: tinyFont.render(txStr, True, color_green if self.TX_RATE > 0 else color_white))
            timeFontSize = 100
            timeSpText = self.get_cache('timeText_{}'.format(':'), lambda: getAppFont(timeFontSize, 'DIGIT').render(':', True, color_green)) # largeFont
            timeHourText = self.get_cache('timeHourText_{}'.format(shour), lambda: getAppFont(timeFontSize, 'DIGIT').render(shour, True, color_green)) # largeFont
            timeMinuteText = self.get_cache('timeMinuteText_{}'.format(minute), lambda: getAppFont(timeFontSize, 'DIGIT').render(minute, True, color_green)) # largeFont

            surface.blit(sysText,((window_width - sysText.get_width()) / 2, -6))
            monthText = self.get_cache('monthText_{} {}'.format(year + '-' + month + '-' + date, day), lambda: middleFont.render(year + '-' + month + '-' + date + ' ' + day, True, color_green))
            y = (window_height - timeMinuteText.get_height()) / 2
            # surface.blit(timeText, ((window_width - timeText.get_width()) / 2, y))
            surface.blit(timeHourText, ((window_width / 2 - timeHourText.get_width() - timeSpText.get_width() / 2), y))
            surface.blit(timeMinuteText, ((window_width / 2 + timeSpText.get_width() / 2), y))
            if self.hide_second_symbol is True:
                surface.blit(timeSpText, ((window_width - timeSpText.get_width()) / 2, y))
            # surface.blit(secondText, (190, 52))
            x = (window_width - monthText.get_width()) / 2
            surface.blit(monthText, (x, y + timeMinuteText.get_height()))

            surface.blit(ipText,((window_width - ipText.get_width()) / 2, 28))
            surface.blit(netSpeedInText, (window_width - netSpeedInText.get_width() - 14, window_height - netSpeedInText.get_height() + 2))
            surface.blit(netSpeedOutText, ((window_width - 14) / 2 - netSpeedOutText.get_width(), window_height - netSpeedOutText.get_height() + 2))
            
        else:
            netSpeedInText = self.get_cache('rxStr_{}'.format(rxStr), lambda: tinyFont22.render(rxStr, True, color_green if self.RX_RATE > 0 else color_white))
            netSpeedOutText = self.get_cache('txStr_{}'.format(txStr), lambda: tinyFont22.render(txStr, True, color_green if self.TX_RATE > 0 else color_white))
            timeFontSize = 64
            timeSpText = self.get_cache('timeText_{}'.format(':'), lambda: getAppFont(timeFontSize, 'DIGIT').render(':', True, color_green)) # largeFont
            timeHourText = self.get_cache('timeHourText_{}'.format(shour), lambda: getAppFont(timeFontSize, 'DIGIT').render(shour, True, color_green)) # largeFont
            timeMinuteText = self.get_cache('timeMinuteText_{}'.format(minute), lambda: getAppFont(timeFontSize, 'DIGIT').render(minute, True, color_green)) # largeFont

            surface.blit(sysText,((window_width - sysText.get_width()) / 2, -6))
            # dayText = self.get_cache('dayText_{}'.format(day), lambda: smallFont.render(day, True, color_green))
            monthText = self.get_cache('monthText_{} {}'.format(year + '-' + month + '-' + date, day), lambda: smallFont.render(year + '-' + month + '-' + date + ' ' + day, True, color_green))
            y = (window_height - timeMinuteText.get_height()) / 2
            # surface.blit(timeText, ((window_width - timeText.get_width()) / 2, y))
            surface.blit(timeHourText, ((window_width / 2 - timeHourText.get_width() - timeSpText.get_width() / 2), y))
            surface.blit(timeMinuteText, ((window_width / 2 + timeSpText.get_width() / 2), y))
            if self.hide_second_symbol is True:
                surface.blit(timeSpText, ((window_width - timeSpText.get_width()) / 2, y))
            # surface.blit(secondText, (190, 52))
            x = (window_width - monthText.get_width()) / 2
            surface.blit(monthText, (x, y + timeMinuteText.get_height() - 12))

            surface.blit(ipText,((window_width - ipText.get_width()) / 2, 18))
            surface.blit(netSpeedInText, (window_width - netSpeedInText.get_width() - 14, window_height - netSpeedInText.get_height() + 2))
            surface.blit(netSpeedOutText, ((window_width - 14) / 2 - netSpeedOutText.get_width(), window_height - netSpeedOutText.get_height() + 2))

        self.prevSecondIntValue = secondIntValue
        pass

    def update_style_1(self, surface = None):
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
            if len(self.NET_STATS) > 0:
                RX = float(self.NET_STATS[0])
                RX_O = rxstat_o[0]
                TX = float(self.NET_STATS[1])
                TX_O = rxstat_o[1]
                self.RX_RATE = round((RX - RX_O)/1024/1024,3)
                self.TX_RATE = round((TX - TX_O)/1024/1024,3)
            else:
                RX = 0.0
                RX_O = 0
                TX = 0.0
                TX_O = 0
                self.RX_RATE = 0
                self.TX_RATE = 0

            self.memInfo = get_mem_info()
            self.dskInfo = get_disk_info()
            self.hostIp = get_host_ip()

            cpuInfo = readCpuInfo()
            self.cpuUse = str(round(calcCpuUsage(self.lastCpuInfo, cpuInfo), 1)) # getCPUuse()
            self.lastCpuInfo = cpuInfo

        cpuUse = self.cpuUse
        memInfo = self.memInfo
        memStr = "MEM {0}M".format(memInfo['free'])
        memUse = str(memInfo['percent'])
        dskInfo = self.dskInfo
        dskStr = "DSK {0}".format(dskInfo['free'])
        dskUse = str(dskInfo['percent'])

        if secondIntValue % 5 == 0:
            cputempStr, cpuTempValue = cputempf()
            self.cputemp = cputempStr
            self.cputempValue = cpuTempValue

        am = 'AM'
        
        if self.timeShowType.current() == 0 and hour > 12:
            hour = hour-12
            am = 'PM'

        shour = str(hour)
        if len(shour) == 1:
            shour = '0' + shour
        timeStr = shour + ':' + minute
        # timeText = largeFont.render(timeStr, True, color_green)
        secondText = self.get_cache('secondText_{}'.format(second), lambda: middleFont.render(second, True, color_green))
        amText = self.get_cache('amText_{}'.format(am), lambda: middleFont.render(am, True, color_green))

        if self.sysInfoShowType.current() == 0:
            sysText = self.get_cache('sysText_{}'.format(self.cputemp), lambda: smallFont.render(self.cputemp, True, color_white))
            sysUseText = self.get_cache('sysUseText_{}'.format(self.cputemp), lambda: smallFont.render(str(cpuUse) + '%', True, color_white))
        if self.sysInfoShowType.current() == 1:
            sysText = self.get_cache('sysText_{}'.format(memStr), lambda: smallFont.render(memStr, True, color_white))
            sysUseText = self.get_cache('sysUseText_{}'.format(memUse), lambda: smallFont.render(memUse + '%', True, color_white))
        if self.sysInfoShowType.current() == 2:
            sysText = self.get_cache('sysText_{}'.format(dskStr), lambda: smallFont.render(dskStr, True, color_white))
            sysUseText = self.get_cache('sysUseText_{}'.format(dskUse), lambda: smallFont.render(dskUse, True, color_white))
        rxStr = '' + str(self.RX_RATE) + ' M/s'
        txStr = '' + str(self.TX_RATE) + ' M/s'
        netSpeedInText = self.get_cache('rxStr_{}'.format(rxStr), lambda: tinyFont.render(rxStr, True, color_green if self.RX_RATE > 0 else color_white))
        netSpeedOutText = self.get_cache('txStr_{}'.format(txStr), lambda: tinyFont.render(txStr, True, color_green if self.TX_RATE > 0 else color_white))

        ip = self.hostIp
        ipText = self.get_cache('ip_{}'.format(ip), lambda: miniFont.render(ip, True, color_white))

        if window_width == 320:
            timeText = self.get_cache('timeText_{}'.format(timeStr), lambda: getAppFont(120, 'DIGIT').render(timeStr, True, color_green)) # largeFont
            # yearText = self.get_cache('yearText_{}'.format(year), lambda: getAppFont(50, 'DIGIT').render(year, True, color_green))
            dayText = self.get_cache('dayText_{}'.format(day), lambda: getAppFont(36, 'PingFang').render(day, True, color_green))
            monthText = self.get_cache('monthText_{}'.format(year + '-' + month + '-' + date), lambda: getAppFont(46, 'DIGIT').render(year + '-' + month + '-' + date, True, color_green))
            surface.blit(sysText, (10,0))
            surface.blit(sysUseText, (window_width - sysUseText.get_width() - 2,0))
            surface.blit(timeText, (6, int(window_height * (16 / 135))))
            surface.blit(secondText, (window_width - secondText.get_width(), int(window_height * (52 / 135))))
            surface.blit(monthText, (15, int(window_height * (86 / 135))))
            # surface.blit(yearText, (145,120))
            if self.timeShowType.current() == 0:
                surface.blit(amText,(window_width - amText.get_width(), int(window_height * (22 / 135))))
            surface.blit(dayText,(window_width - dayText.get_width(), int(window_height * (86 / 135))))

            if self.netShowType.current() == 1:
                surface.blit(netSpeedInText, (window_width - netSpeedInText.get_width(), window_height - 23))
                surface.blit(netSpeedOutText, (window_width / 2 - netSpeedOutText.get_width(), window_height - 23))
            else:
                surface.blit(ipText,(10, window_height - 23))
                surface.blit(netSpeedInText, (window_width - netSpeedInText.get_width(), window_height - 23))
        else:
            timeText = self.get_cache('timeText_{}'.format(timeStr), lambda: getAppFont(82, 'DIGIT').render(timeStr, True, color_green)) # largeFont
            # yearText = self.get_cache('yearText_{}'.format(year), lambda: smallFont.render(year, True, color_green))
            dayText = self.get_cache('dayText_{}'.format(day), lambda: getAppFont(24, 'PingFang').render(day, True, color_green))
            monthText = self.get_cache('monthText_{}'.format(year + '-' + month + '-' + date), lambda: smallFont.render(year + '-' + month + '-' + date, True, color_green))
            surface.blit(sysText, (10,0))
            surface.blit(sysUseText, (window_width - sysUseText.get_width() - 2,0))
            surface.blit(timeText, (4,16))
            surface.blit(secondText, (190, 52))
            surface.blit(monthText, (15,86))
            # surface.blit(yearText, (145,120))
            if self.timeShowType.current() == 0:
                surface.blit(amText,(190,22))
            surface.blit(dayText,(window_width - dayText.get_width(),86))

            if self.netShowType.current() == 1:
                surface.blit(netSpeedInText, (window_width - netSpeedInText.get_width(), window_height - 23))
                surface.blit(netSpeedOutText, (window_width / 2 - netSpeedOutText.get_width(), window_height - 23))
            else:
                surface.blit(ipText,(10, window_height - 23))
                surface.blit(netSpeedInText, (window_width - netSpeedInText.get_width(), window_height - 23))
        
        self.prevSecondIntValue = secondIntValue
        # welcomeTxt = bigFont.render(ClockUI.__name__, True, color_white)
        # surface.blit(welcomeTxt, (window_width / 2 - welcomeTxt.get_width() / 2, window_height / 2 - welcomeTxt.get_height() / 2))

        # pygame.draw.rect(surface, (255,255,255), self.sysInfoRect, 1)
        # pygame.draw.rect(surface, (255,255,255), self.timeRect, 1)
        # pygame.draw.rect(surface, (255,255,255), self.dateRect, 1)
        # pygame.draw.rect(surface, (255,255,255), self.netRect, 1)
        pass

    pass
