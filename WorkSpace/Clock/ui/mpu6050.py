#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import math
import json
import time
import logging
import logging.config
from ui.core import UIManager, BaseUI
from ui.theme import *
from utils.GIFImage import GIFImage
from utils.stepper import Stepper
from system.config import Config
from drivers.mpu6050 import mpu6050
from drivers.imu import Mahony

logger = logging.getLogger('ui.mpu6050')

class MPU6050UI(BaseUI):

    showTick = 0
    launcher_img = None
    mpu = None
    arrow = None
    motion_tick = 0
    showType = Stepper(minVal=0, maxVal=2, step=1, currentVal=0)
    mpu6050_motion = {
        'isNegActivityOnX' : 0,
        'isPosActivityOnX' : 0,
        'isNegActivityOnY' : 0,
        'isPosActivityOnY' : 0,
        'isNegActivityOnZ' : 0,
        'isPosActivityOnZ' : 0
    }
    imu = Mahony()
    last_mpu_fetch = 0
    motion_dir = 0

    accel_val_range = [
        [0, 0],
        [0, 0],
        [0, 0]
    ]

    def on_shown(self):
        if self.mpu is None:
            self.mpu = mpu6050()
            if self.mpu.is_inited() is False:
                self.mpu.init(0x68, scale=self.mpu.MPU6050_SCALE_2000DPS, a_range=self.mpu.MPU6050_RANGE_16G)
                # self.mpu.set_gyro_range(0x18)
        # self.mpu.setAccelPowerOnDelay(self.mpu.MPU6050_DELAY_3MS)

        # self.mpu.setIntFreeFallEnabled(False);  
        # self.mpu.setIntZeroMotionEnabled(False)
        # self.mpu.setIntMotionEnabled(False)
        
        # self.mpu.setDHPFMode(self.mpu.MPU6050_DHPF_5HZ)
        # scaleFactor = 1
        # self.mpu.setMotionDetectionThreshold(3)
        # self.mpu.setMotionDetectionDuration(5 * scaleFactor)

        # self.mpu.setZeroMotionDetectionThreshold(4 * scaleFactor)

        target_index = int(Config().get('user-interface.launcher.current'))
        images = Config().get('user-interface.launcher.images')
        if len(images) > 0 and target_index < len(images):
            self.launcher_img = GIFImage(os.path.join(sys.path[0], images[target_index]))
        self.showTick = (time.time() * 1000)
        self.arrow = pygame.Surface((30, 30)).convert_alpha()
        self.arrow.fill((255,255,255,0))
        # pygame.draw.polygon(self.arrow, color_green, ((15, 0), (0, 15), (29, 15)))
        # pygame.draw.rect(self.arrow, color_green, (7, 15, 15, 15))

        # pygame.draw.lines(self.arrow, color_green, True, ((0, 0),(0, 29),(29, 29),(29,0)))
        pygame.draw.polygon(self.arrow, color_green, ((15, 0), (8, 8), (21, 8)))
        pygame.draw.rect(self.arrow, color_green, (12, 8, 6, 22))

        self.last_mpu_fetch = time.time()
        pass

    def on_hidden(self):
        pass

    def onKeyRelease(self, isLongPress, pushCount, longPressSeconds, keyIndex):
        if not isLongPress and pushCount == 1:
            self.showType.next()
            self.checkSettings()
        if isLongPress and longPressSeconds == 2:
            self.mpu.calibration()

    def onMouseDown(self, event):
        self.showType.next()
        # self.mpu.calibrateGyro(100)
        self.checkSettings()

    def update(self, surface = None):
        surface = UIManager().getSurface()
        windowSize = UIManager().getWindowSize()
        window_width = windowSize[0]
        window_height = windowSize[1]
        surface.fill(color_black)

        start_pos = (15, 25)
        center_pos = (start_pos[0] + 15, start_pos[1] + 15)
        start2_pos = (15, 95)
        center2_pos = (start2_pos[0] + 15, start2_pos[1] + 15)

        mpu_fetch_tick = time.time()
        delta_fetch_tick = 1 / (mpu_fetch_tick - self.last_mpu_fetch)

        mpu_data_all = self.mpu.get_all_data()
        accel_data = mpu_data_all[0]
        gyro_data = mpu_data_all[1]
        # temperature = mpu_data_all[2]
        # rawAccel = self.mpu.readNormalizeAccel() # self.mpu.readRawAccel()
        # rawGyro = self.mpu.readNormalizeGyro() # self.mpu.readRawGyro()
        # accel_data = {
        #     'x': rawAccel.XAxis,
        #     'y': rawAccel.YAxis,
        #     'z': rawAccel.ZAxis,
        # }
        # gyro_data = {
        #     'x': rawGyro.XAxis,
        #     'y': rawGyro.YAxis,
        #     'z': rawGyro.ZAxis,
        # }
        self.last_mpu_fetch = mpu_fetch_tick
        # print('accel_data x = {:>10.6f}, y = {:>10.6f} , z = {:>10.6f}'.format(accel_data['x'], accel_data['y'], accel_data['z']), 
        #     'gyro_data x = {:>10.6f}, y = {:>10.6f} , z = {:>10.6f}'.format(gyro_data['x'], gyro_data['y'], gyro_data['z']), end='\r')
        # print('temperature', temperature)
        angle = self.imu.MahonyAHRSupdateIMU(gyro_data['x'], gyro_data['y'], gyro_data['z'],
                                        accel_data['x'], accel_data['y'], accel_data['z'], delta_fetch_tick)
        # print(-angle[0], angle[1], angle[2])

        self.recordRangeXYZ(accel_data['x'], accel_data['y'], accel_data['z'])
        # self.recordRangeXYZ(gyro_data['x'], gyro_data['y'], gyro_data['z'])

        txt = zhMiniFont.render('A  x {:>13.6f} {}'.format(accel_data['x'], angle[0]), True, color_green if self.showType.current() == 0 else color_white)
        surface.blit(txt, (30, 0))
        txt = zhMiniFont.render('    y {:>13.6f} {}'.format(accel_data['y'], angle[1]), True, color_green if self.showType.current() == 1 else color_white)
        surface.blit(txt, (30, 22))
        txt = zhMiniFont.render('    z {:>13.6f} {}'.format(accel_data['z'], angle[2]), True, color_green if self.showType.current() == 2 else color_white)
        surface.blit(txt, (30, 44))
        txt = zhMiniFont.render('G  x {:>13.6f}'.format(gyro_data['x']), True, color_white)
        surface.blit(txt, (30, 66))
        txt = zhMiniFont.render('    y {:>13.6f}'.format(gyro_data['y']), True, color_white)
        surface.blit(txt, (30, 88))
        txt = zhMiniFont.render('    z {:>13.6f}'.format(gyro_data['z']), True, color_white)
        surface.blit(txt, (30, 110))

        a_angle = angle[self.showType.current()] # self.get_angle(accel_data['x'], accel_data['y'], accel_data['z'], 1)
        a_arrow = pygame.transform.rotate(self.arrow, a_angle)
        a_size = a_arrow.get_size()
        # print('a_angle', a_angle)
        surface.blit(a_arrow, (int(center_pos[0] - a_size[0] / 2), int(center_pos[1] - a_size[1] / 2)))


        activities = self.mpu.read_activites()
        # 'isOverflow' : self.a.isOverflow,
        # 'isFreeFall' : self.a.isFreeFall,
        # 'isInactivity' : self.a.isInactivity,
        # 'isDataReady' : self.a.isDataReady,
        self.mpu6050_motion['isNegActivityOnX'] = activities['isNegActivityOnX']
        self.mpu6050_motion['isPosActivityOnX'] = activities['isPosActivityOnX']
        self.mpu6050_motion['isNegActivityOnY'] = activities['isNegActivityOnY']
        self.mpu6050_motion['isPosActivityOnY'] = activities['isPosActivityOnY']
        self.mpu6050_motion['isNegActivityOnZ'] = activities['isNegActivityOnZ']
        self.mpu6050_motion['isPosActivityOnZ'] = activities['isPosActivityOnZ']
        if ((time.time() * 1000) - self.motion_tick) > 500:

            self.motion_dir = 0
            if activities['isNegActivityOnX']:
                self.motion_dir = -1
                self.motion_tick = (time.time() * 1000)
            elif activities['isPosActivityOnX']:
                self.motion_dir = 1
                self.motion_tick = (time.time() * 1000)
            elif activities['isNegActivityOnY']:
                self.motion_dir = 4
                self.motion_tick = (time.time() * 1000)
            elif activities['isPosActivityOnY']:
                self.motion_dir = 2
                self.motion_tick = (time.time() * 1000)
        
        if self.motion_dir == 0:
            pygame.draw.circle(surface, color_green, center2_pos, 15)
        else:
            a_arrow = pygame.transform.rotate(self.arrow, 90 * self.motion_dir)
            surface.blit(a_arrow, start2_pos)
        
        # txt = zhMiniFont.render('overflow={}  freeFall={}'.format(activities['isOverflow'], activities['isFreeFall']), True, color_white)
        # surface.blit(txt, (0, 0))
        # txt = zhMiniFont.render('inactivity={}  dataReady={}'.format(activities['isInactivity'], activities['isDataReady']), True, color_white)
        # surface.blit(txt, (0, 20))
        # txt = zhMiniFont.render('negActX={}  posActX={}'.format(self.mpu6050_motion['isNegActivityOnX'], self.mpu6050_motion['isPosActivityOnX']), True, color_white)
        # surface.blit(txt, (0, 40))
        # txt = zhMiniFont.render('negActY={}  posActY={}'.format(self.mpu6050_motion['isNegActivityOnY'], self.mpu6050_motion['isPosActivityOnY']), True, color_white)
        # surface.blit(txt, (0, 60))
        # txt = zhMiniFont.render('negActZ={}  posActZ={}'.format(self.mpu6050_motion['isNegActivityOnZ'], self.mpu6050_motion['isPosActivityOnZ']), True, color_white)
        # surface.blit(txt, (0, 80))
        # print('activities', json.dumps())

    pass

    def recordRangeXYZ(self,x,y,z):
        changed = False
        if x > self.accel_val_range[0][0]:
            self.accel_val_range[0][0] = x
            changed = True
        if x < self.accel_val_range[0][1]:
            self.accel_val_range[0][1] = x
            changed = True

        if y > self.accel_val_range[1][0]:
            self.accel_val_range[1][0] = y
            changed = True
        if y < self.accel_val_range[1][1]:
            self.accel_val_range[1][1] = y
            changed = True

        if z > self.accel_val_range[2][0]:
            self.accel_val_range[2][0] = z
            changed = True
        if z < self.accel_val_range[2][1]:
            self.accel_val_range[2][1] = z
            changed = True
        
        if changed:
            print(
                'max_x', self.accel_val_range[0][0],
                'min_x', self.accel_val_range[0][1],
                'max_y', self.accel_val_range[1][0],
                'min_y', self.accel_val_range[1][1],
                'max_z', self.accel_val_range[2][0],
                'min_z', self.accel_val_range[2][1],
            )

    def get_angle(self, x, y, z, dir):
        '''
        x,y,z: x, y, z方向的重力加速度分量
        dir: 要获得的角度，0：与Z的角度，1与X的角度，2与Y的角度
        返回值: 角度值，单位0.1度
        '''
        temp = 0
        res = 0
        if dir == 0:
            try:
                temp = math.sqrt((x*x + y*y)) / z
            except:
                temp = 0
            res = math.atan(temp)
            pass
        if dir == 1:
            try:
                temp = x / math.sqrt((y*y + z*z))
            except:
                temp = 0
            res = math.atan(temp)
            pass
        if dir == 2:
            try:
                temp = y / math.sqrt((x*x + z*z))
            except:
                temp = 0
            res = math.atan(temp)
            pass
        return res * 1800/3.14

    def checkSettings(self):

        print()

        print(" * Sleep Mode:                ", end='')
        print("Enabled" if self.mpu.getSleepEnabled() is True else "Disabled")

        print(" * Motion Interrupt:          ", end='')
        print("Enabled" if self.mpu.getIntMotionEnabled() is True else "Disabled")

        print(" * Zero Motion Interrupt:     ", end='')
        print("Enabled" if self.mpu.getIntZeroMotionEnabled() is True else "Disabled")

        print(" * Free Fall Interrupt:       ", end='')
        print("Enabled" if self.mpu.getIntFreeFallEnabled() is True else "Disabled")

        print(" * Motion Threshold:          ", end='')
        print(self.mpu.getMotionDetectionThreshold())

        print(" * Motion Duration:           ", end='')
        print(self.mpu.getMotionDetectionDuration())

        print(" * Zero Motion Threshold:     ", end='')
        print(self.mpu.getZeroMotionDetectionThreshold())

        print(" * Zero Motion Duration:      ", end='')
        print(self.mpu.getZeroMotionDetectionDuration())

        print(" * Clock Source:              ", end='')
        clockSource = self.mpu.getClockSource()
        if clockSource == self.mpu.MPU6050_CLOCK_KEEP_RESET:     print("Stops the clock and keeps the timing generator in reset")
        if clockSource == self.mpu.MPU6050_CLOCK_EXTERNAL_19MHZ: print("PLL with external 19.2MHz reference")
        if clockSource == self.mpu.MPU6050_CLOCK_EXTERNAL_32KHZ: print("PLL with external 32.768kHz reference")
        if clockSource == self.mpu.MPU6050_CLOCK_PLL_ZGYRO:      print("PLL with Z axis gyroscope reference")
        if clockSource == self.mpu.MPU6050_CLOCK_PLL_YGYRO:      print("PLL with Y axis gyroscope reference")
        if clockSource == self.mpu.MPU6050_CLOCK_PLL_XGYRO:      print("PLL with X axis gyroscope reference")
        if clockSource == self.mpu.MPU6050_CLOCK_INTERNAL_8MHZ:  print("Internal 8MHz oscillator")

        print(" * Accelerometer:             ", end='')
        a_range = self.mpu.getRange()
        if a_range == self.mpu.MPU6050_RANGE_16G:              print("+/- 16 g")
        elif a_range == self.mpu.MPU6050_RANGE_8G:             print("+/- 8 g")
        elif a_range == self.mpu.MPU6050_RANGE_4G:             print("+/- 4 g")
        elif a_range == self.mpu.MPU6050_RANGE_2G:             print("+/- 2 g")

        print(" * Accelerometer offsets:     ", end='')
        print(self.mpu.getAccelOffsetX(), end='')
        print(" / ", end='')
        print(self.mpu.getAccelOffsetY(), end='')
        print(" / ", end='')
        print(self.mpu.getAccelOffsetZ())

        print(" * Accelerometer power delay: ", end='')
        accelPOD = self.mpu.getAccelPowerOnDelay()
        if accelPOD == self.mpu.MPU6050_DELAY_3MS:            print("3ms")
        if accelPOD == self.mpu.MPU6050_DELAY_2MS:            print("2ms")
        if accelPOD == self.mpu.MPU6050_DELAY_1MS:            print("1ms")
        if accelPOD == self.mpu.MPU6050_NO_DELAY:             print("0ms")
    
        print()