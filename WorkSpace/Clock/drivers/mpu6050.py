
# -*- coding: UTF-8 -*-
import smbus
import math
import time
from core import Singleton


class Activites(object):
    isOverflow      = False
    isFreeFall      = False
    isInactivity    = False
    isActivity      = False
    isPosActivityOnX = False
    isPosActivityOnY = False
    isPosActivityOnZ = False
    isNegActivityOnX = False
    isNegActivityOnY = False
    isNegActivityOnZ = False
    isDataReady      = False

    def __init__(self):
        self.isOverflow = False
        self.isFreeFall = False
        self.isInactivity = False
        self.isActivity = False
        self.isDataReady = False

        self.isNegActivityOnX = False
        self.isPosActivityOnX = False

        self.isNegActivityOnY = False
        self.isPosActivityOnY = False

        self.isNegActivityOnZ = False
        self.isPosActivityOnZ = False

class Vector(object):
    XAxis = 0.0
    YAxis = 0.0
    ZAxis = 0.0

    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.XAxis = x
        self.YAxis = y
        self.ZAxis = z

class mpu6050(metaclass=Singleton):
    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = None
    inited = False
    ra = Vector()  # Raw Accel
    rg = Vector()  # Raw Gyro
    na = Vector()  # Normalized vectors
    ng = Vector()  # Normalized vectors
    tg = Vector()  # Threshold for Gyro
    dg = Vector()  # Delta for Gyro
    th = Vector()  # Threshold
    dpsPerDigit = 0.0
    rangePerDigit = 0.0
    actualThreshold = 0.0
    useCalibrate = False

    a = Activites()

    # Scale Modifiers
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Pre-defined ranges
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    TEMP_OUT0 = 0x41

    GYRO_XOUT0 = 0x43
    GYRO_YOUT0 = 0x45
    GYRO_ZOUT0 = 0x47

    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    MPU6050_ADDRESS                 = (0x68) # 0x69 when AD0 pin to Vcc

    MPU6050_REG_ACCEL_XOFFS_H       = (0x06)
    MPU6050_REG_ACCEL_XOFFS_L       = (0x07)
    MPU6050_REG_ACCEL_YOFFS_H       = (0x08)
    MPU6050_REG_ACCEL_YOFFS_L       = (0x09)
    MPU6050_REG_ACCEL_ZOFFS_H       = (0x0A)
    MPU6050_REG_ACCEL_ZOFFS_L       = (0x0B)
    MPU6050_REG_GYRO_XOFFS_H        = (0x13)
    MPU6050_REG_GYRO_XOFFS_L        = (0x14)
    MPU6050_REG_GYRO_YOFFS_H        = (0x15)
    MPU6050_REG_GYRO_YOFFS_L        = (0x16)
    MPU6050_REG_GYRO_ZOFFS_H        = (0x17)
    MPU6050_REG_GYRO_ZOFFS_L        = (0x18)
    MPU6050_REG_CONFIG              = (0x1A)
    MPU6050_REG_GYRO_CONFIG         = (0x1B) # Gyroscope Configuration
    MPU6050_REG_ACCEL_CONFIG        = (0x1C) # Accelerometer Configuration
    MPU6050_REG_FF_THRESHOLD        = (0x1D)
    MPU6050_REG_FF_DURATION         = (0x1E)
    MPU6050_REG_MOT_THRESHOLD       = (0x1F)
    MPU6050_REG_MOT_DURATION        = (0x20)
    MPU6050_REG_ZMOT_THRESHOLD      = (0x21)
    MPU6050_REG_ZMOT_DURATION       = (0x22)
    MPU6050_REG_INT_PIN_CFG         = (0x37) # INT Pin. Bypass Enable Configuration
    MPU6050_REG_INT_ENABLE          = (0x38) # INT Enable
    MPU6050_REG_INT_STATUS          = (0x3A)
    MPU6050_REG_ACCEL_XOUT_H        = (0x3B)
    MPU6050_REG_ACCEL_XOUT_L        = (0x3C)
    MPU6050_REG_ACCEL_YOUT_H        = (0x3D)
    MPU6050_REG_ACCEL_YOUT_L        = (0x3E)
    MPU6050_REG_ACCEL_ZOUT_H        = (0x3F)
    MPU6050_REG_ACCEL_ZOUT_L        = (0x40)
    MPU6050_REG_TEMP_OUT_H          = (0x41)
    MPU6050_REG_TEMP_OUT_L          = (0x42)
    MPU6050_REG_GYRO_XOUT_H         = (0x43)
    MPU6050_REG_GYRO_XOUT_L         = (0x44)
    MPU6050_REG_GYRO_YOUT_H         = (0x45)
    MPU6050_REG_GYRO_YOUT_L         = (0x46)
    MPU6050_REG_GYRO_ZOUT_H         = (0x47)
    MPU6050_REG_GYRO_ZOUT_L         = (0x48)
    MPU6050_REG_MOT_DETECT_STATUS   = (0x61)
    MPU6050_REG_MOT_DETECT_CTRL     = (0x69)
    MPU6050_REG_USER_CTRL           = (0x6A) # User Control
    MPU6050_REG_PWR_MGMT_1          = (0x6B) # Power Management 1
    MPU6050_REG_WHO_AM_I            = (0x75) # Who Am I
    
    # mpu6050_dhpf_t
    MPU6050_DHPF_HOLD             = 0b111
    MPU6050_DHPF_0_63HZ           = 0b100
    MPU6050_DHPF_1_25HZ           = 0b011
    MPU6050_DHPF_2_5HZ            = 0b010
    MPU6050_DHPF_5HZ              = 0b001
    MPU6050_DHPF_RESET            = 0b000
    # end of mpu6050_dhpf_t

    # mpu6050_dlpf_t
    MPU6050_DLPF_6                = 0b110
    MPU6050_DLPF_5                = 0b101
    MPU6050_DLPF_4                = 0b100
    MPU6050_DLPF_3                = 0b011
    MPU6050_DLPF_2                = 0b010
    MPU6050_DLPF_1                = 0b001
    MPU6050_DLPF_0                = 0b000
    # end of mpu6050_dlpf_t

    MPU6050_DELAY_3MS             = 0b11
    MPU6050_DELAY_2MS             = 0b10
    MPU6050_DELAY_1MS             = 0b01
    MPU6050_NO_DELAY              = 0b00

    # mpu6050_clockSource_t
    MPU6050_CLOCK_KEEP_RESET      = 0b111
    MPU6050_CLOCK_EXTERNAL_19MHZ  = 0b101
    MPU6050_CLOCK_EXTERNAL_32KHZ  = 0b100
    MPU6050_CLOCK_PLL_ZGYRO       = 0b011
    MPU6050_CLOCK_PLL_YGYRO       = 0b010
    MPU6050_CLOCK_PLL_XGYRO       = 0b001
    MPU6050_CLOCK_INTERNAL_8MHZ   = 0b000
    # end of mpu6050_clockSource_t

    # mpu6050_dps_t
    MPU6050_SCALE_2000DPS         = 0b11
    MPU6050_SCALE_1000DPS         = 0b10
    MPU6050_SCALE_500DPS          = 0b01
    MPU6050_SCALE_250DPS          = 0b00
    # end of mpu6050_dps_t
    
    # mpu6050_range_t
    MPU6050_RANGE_16G             = 0b11
    MPU6050_RANGE_8G              = 0b10
    MPU6050_RANGE_4G              = 0b01
    MPU6050_RANGE_2G              = 0b00
    # end of mpu6050_range_t

    def __init__(self):
        pass
    
    def init(self, address, bus=0, scale = 0b11, a_range = 0b00):
        '''
        mpu6050_dps_t scale
        mpu6050_range_t range
        '''
        if self.inited is True:
            return
        self.inited = True
        self.address = address
        self.bus = smbus.SMBus(bus)
        # Wake up the MPU-6050 since it starts in sleep mode
        # self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
        self.sum_data = [0, 0, 0, 0, 0, 0]
        
        # Reset calibrate values
        self.dg.XAxis = 0
        self.dg.YAxis = 0
        self.dg.ZAxis = 0
        self.useCalibrate = False

        # Reset threshold values
        self.tg.XAxis = 0
        self.tg.YAxis = 0
        self.tg.ZAxis = 0
        self.actualThreshold = 0

        # Check MPU6050 Who Am I Register
        if self.readRegister8(self.MPU6050_REG_WHO_AM_I) != 0x68:
            return False

        # Set Clock Source
        self.setClockSource(self.MPU6050_CLOCK_PLL_XGYRO)

        # Set Scale & Range
        self.setScale(scale)
        self.setRange(a_range)

        # Disable Sleep Mode
        self.setSleepEnabled(False)

        return True

    def is_inited(self):
        return self.inited

    # I2C communication methods

    def read_i2c_word(self, register):
        """Read two i2c registers and combine them.
        register -- the first register to read from.
        Returns the combined read results.
        """
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    def read_i2c_byte(self, register):
        """Read one i2c registers.
        register -- the register to read from.
        Returns the combined read results.
        """
        # Read the data from the registers
        value = self.bus.read_byte_data(self.address, register)

        return value

    def readRegister16(self, cmd):
        value = self.bus.read_word_data(self.address, cmd)
        return value

    def writeRegister16(self, cmd, val):
        self.bus.write_word_data(self.address, cmd, val)

    def readRegister8(self, cmd):
        value = self.read_i2c_byte(cmd)
        return value

    def writeRegister8(self, cmd, val):
        self.bus.write_byte_data(self.address, cmd, val)
        pass

    def readRegisterBit(self, reg, pos): # -> bool
        '''
        reg: uint8
        pos: uint8
        '''
        value = self.readRegister8(reg)
        return ((value >> pos) & 1)

    def writeRegisterBit(self, reg, pos, state):
        '''
        reg: uint8
        pos: uint8
        state: bool
        '''
        value = self.readRegister8(reg)
        if state is True:
            value |= (1 << pos)
        else:
            value &= ~(1 << pos)
        self.writeRegister8(reg, value)

    # MPU-6050 Settings
    def setClockSource(self, clock_source):
        value = self.readRegister8(self.MPU6050_REG_PWR_MGMT_1)
        value &= 0b11111000
        value |= clock_source
        self.writeRegister8(self.MPU6050_REG_PWR_MGMT_1, value)

    def getClockSource(self): # -> mpu6050_clockSource_t
        value = self.readRegister8(self.MPU6050_REG_PWR_MGMT_1)
        value &= 0b00000111
        return value

    def setScale(self, scale):
        '''
        scale: mpu6050_dps_t
        '''
        if scale == self.MPU6050_SCALE_250DPS:
            self.dpsPerDigit = .007633
        elif scale == self.MPU6050_SCALE_500DPS:
            self.dpsPerDigit = .015267
        elif scale == self.MPU6050_SCALE_1000DPS:
            self.dpsPerDigit = .030487
        elif scale == self.MPU6050_SCALE_2000DPS:
            self.dpsPerDigit = .060975

        value = self.readRegister8(self.MPU6050_REG_GYRO_CONFIG)
        value &= 0b11100111
        value |= (scale << 3)
        self.writeRegister8(self.MPU6050_REG_GYRO_CONFIG, 0x00)
        self.writeRegister8(self.MPU6050_REG_GYRO_CONFIG, value)

    def getScale(self): # -> mpu6050_dps_t
        value = self.readRegister8(self.MPU6050_REG_GYRO_CONFIG)
        value &= 0b00011000
        value >>= 3
        return value

    def setRange(self, a_range):
        '''
        mpu6050_range_t range
        '''
        if a_range == self.MPU6050_RANGE_2G:
            self.rangePerDigit = .000061
        elif a_range == self.MPU6050_RANGE_4G:
            self.rangePerDigit = .000122
        elif a_range == self.MPU6050_RANGE_8G:
            self.rangePerDigit = .000244
        elif a_range == self.MPU6050_RANGE_16G:
            self.rangePerDigit = .0004882

        value = self.readRegister8(self.MPU6050_REG_ACCEL_CONFIG)
        value &= 0b11100111
        value |= (a_range << 3)
        self.writeRegister8(self.MPU6050_REG_ACCEL_CONFIG, 0x00)
        self.writeRegister8(self.MPU6050_REG_ACCEL_CONFIG, value)

    def getRange(self): # -> mpu6050_range_t
        '''
        mpu6050_range_t
        '''
        value = self.readRegister8(self.MPU6050_REG_ACCEL_CONFIG)
        value &= 0b00011000
        value >>= 3
        return value

    def setDHPFMode(self, dhpf):
        '''
        dhpf: mpu6050_dhpf_t 
        '''
        value = self.readRegister8(self.MPU6050_REG_ACCEL_CONFIG)
        value &= 0b11111000
        value |= dhpf
        self.writeRegister8(self.MPU6050_REG_ACCEL_CONFIG, value)

    def setDLPFMode(self, dlpf):
        '''
        dlpf: mpu6050_dlpf_t
        '''
        value = self.readRegister8(self.MPU6050_REG_CONFIG)
        value &= 0b11111000
        value |= dlpf
        self.writeRegister8(self.MPU6050_REG_CONFIG, value)

    def getAccelPowerOnDelay(self): # -> mpu6050_onDelay_t
        value = self.readRegister8(self.MPU6050_REG_MOT_DETECT_CTRL)
        value &= 0b00110000
        return (value >> 4)

    def setAccelPowerOnDelay(self, delay):
        '''
        mpu6050_onDelay_t delay
        '''
        value = self.readRegister8(self.MPU6050_REG_MOT_DETECT_CTRL)
        value &= 0b11001111
        value |= (delay << 4)
        self.writeRegister8(self.MPU6050_REG_MOT_DETECT_CTRL, value)

    def getIntStatus(self): # -> uint8_t
        return self.readRegister8(self.MPU6050_REG_INT_STATUS)

    def getIntZeroMotionEnabled(self):
        return self.readRegisterBit(self.MPU6050_REG_INT_ENABLE, 5)

    def setIntZeroMotionEnabled(self, state):
        '''
        bool state
        '''
        self.writeRegisterBit(self.MPU6050_REG_INT_ENABLE, 5, state)

    def getIntMotionEnabled(self):
        return self.readRegisterBit(self.MPU6050_REG_INT_ENABLE, 6)

    def setIntMotionEnabled(self, state):
        '''
        bool state
        '''
        self.writeRegisterBit(self.MPU6050_REG_INT_ENABLE, 6, state)

    def getIntFreeFallEnabled(self):
        return self.readRegisterBit(self.MPU6050_REG_INT_ENABLE, 7)

    def setIntFreeFallEnabled(self, state):
        '''
        bool state
        '''
        self.writeRegisterBit(self.MPU6050_REG_INT_ENABLE, 7, state)

    def getMotionDetectionThreshold(self): # -> uint8_t
        return self.readRegister8(self.MPU6050_REG_MOT_THRESHOLD)

    def setMotionDetectionThreshold(self, threshold):
        '''
        uint8_t threshold
        '''
        self.writeRegister8(self.MPU6050_REG_MOT_THRESHOLD, threshold)

    def getMotionDetectionDuration(self): # -> uint8_t
        return self.readRegister8(self.MPU6050_REG_MOT_DURATION)

    def setMotionDetectionDuration(self, duration):
        '''
        uint8_t duration
        '''
        self.writeRegister8(self.MPU6050_REG_MOT_DURATION, duration)

    def getZeroMotionDetectionThreshold(self): # -> uint8_t
        return self.readRegister8(self.MPU6050_REG_ZMOT_THRESHOLD)

    def setZeroMotionDetectionThreshold(self, threshold):
        '''
        uint8_t threshold
        '''
        self.writeRegister8(self.MPU6050_REG_ZMOT_THRESHOLD, threshold)

    def getZeroMotionDetectionDuration(self): # -> uint8_t
        return self.readRegister8(self.MPU6050_REG_ZMOT_DURATION)

    def setZeroMotionDetectionDuration(self, duration):
        '''
        uint8_t duration
        '''
        self.writeRegister8(self.MPU6050_REG_ZMOT_DURATION, duration)

    def getFreeFallDetectionThreshold(self): # -> uint8_t
        return self.readRegister8(self.MPU6050_REG_FF_THRESHOLD)

    def setFreeFallDetectionThreshold(self, threshold):
        '''
        uint8_t threshold
        '''
        self.writeRegister8(self.MPU6050_REG_FF_THRESHOLD, threshold)

    def getFreeFallDetectionDuration(self): # -> uint8_t
        return self.readRegister8(self.MPU6050_REG_FF_DURATION)

    def setFreeFallDetectionDuration(self, duration):
        '''
        uint8_t duration
        '''
        self.writeRegister8(self.MPU6050_REG_FF_DURATION, duration)

    def getSleepEnabled(self): # -> bool
        return self.readRegisterBit(self.MPU6050_REG_PWR_MGMT_1, 6)

    def setSleepEnabled(self, state):
        '''
        bool state
        '''
        self.writeRegisterBit(self.MPU6050_REG_PWR_MGMT_1, 6, state)

    def getI2CMasterModeEnabled(self):
        return self.readRegisterBit(self.MPU6050_REG_USER_CTRL, 5)

    def setI2CMasterModeEnabled(self, state):
        '''
        bool state
        '''
        self.writeRegisterBit(self.MPU6050_REG_USER_CTRL, 5, state)

    def getI2CBypassEnabled(self):
        return self.readRegisterBit(self.MPU6050_REG_INT_PIN_CFG, 1)

    def setI2CBypassEnabled(self, state):
        '''
        bool state
        '''
        return self.writeRegisterBit(self.MPU6050_REG_INT_PIN_CFG, 1, state)

    def getGyroOffsetX(self): # -> int16_t;
        return self.readRegister16(self.MPU6050_REG_GYRO_XOFFS_H)

    def setGyroOffsetX(self, offset):
        '''
        int16_t offset
        '''
        self.writeRegister16(self.MPU6050_REG_GYRO_XOFFS_H, offset)

    def getGyroOffsetY(self): # -> int16_t;
        return self.readRegister16(self.MPU6050_REG_GYRO_YOFFS_H)

    def setGyroOffsetY(self, offset):
        '''
        int16_t offset
        '''
        self.writeRegister16(self.MPU6050_REG_GYRO_YOFFS_H, offset)

    def getGyroOffsetZ(self): # -> int16_t;
        return self.readRegister16(self.MPU6050_REG_GYRO_ZOFFS_H)

    def setGyroOffsetZ(self, offset):
        '''
        int16_t offset
        '''
        self.writeRegister16(self.MPU6050_REG_GYRO_ZOFFS_H, offset)

    def getAccelOffsetX(self): # -> int16_t
        return self.readRegister16(self.MPU6050_REG_ACCEL_XOFFS_H)

    def setAccelOffsetX(self, offset):
        '''
        int16_t offset
        '''
        self.writeRegister16(self.MPU6050_REG_ACCEL_XOFFS_H, offset)

    def getAccelOffsetY(self): # -> int16_t
        '''
        int16_t offset
        '''
        return self.readRegister16(self.MPU6050_REG_ACCEL_YOFFS_H)

    def setAccelOffsetY(self, offset):
        '''
        int16_t offset
        '''
        self.writeRegister16(self.MPU6050_REG_ACCEL_YOFFS_H, offset)

    def getAccelOffsetZ(self): # -> int16_t
        '''
        int16_t offset
        '''
        return self.readRegister16(self.MPU6050_REG_ACCEL_ZOFFS_H)

    def setAccelOffsetZ(self, offset):
        '''
        int16_t offset
        '''
        self.writeRegister16(self.MPU6050_REG_ACCEL_ZOFFS_H, offset)

    def calibrateGyro(self, samples = 50):
        '''
        Calibrate algorithm
        uint8_t samples = 50
        '''
        # Set calibrate
        self.useCalibrate = True

        # Reset values
        sumX = 0.0
        sumY = 0.0
        sumZ = 0.0
        sigmaX = 0.0
        sigmaY = 0.0
        sigmaZ = 0.0

        # Read n-samples
        # for (uint8_t i = 0; i < samples; ++i):
        for i in range(samples):
            self.readRawGyro()
            sumX += self.rg.XAxis
            sumY += self.rg.YAxis
            sumZ += self.rg.ZAxis

            sigmaX += self.rg.XAxis * self.rg.XAxis
            sigmaY += self.rg.YAxis * self.rg.YAxis
            sigmaZ += self.rg.ZAxis * self.rg.ZAxis
            # delay(5)
            # time.sleep(0.001)

        # Calculate delta vectors
        self.dg.XAxis = sumX / samples
        self.dg.YAxis = sumY / samples
        self.dg.ZAxis = sumZ / samples

        # Calculate threshold vectors
        self.th.XAxis = math.sqrt((sigmaX / samples) - (self.dg.XAxis * self.dg.XAxis))
        self.th.YAxis = math.sqrt((sigmaY / samples) - (self.dg.YAxis * self.dg.YAxis))
        self.th.ZAxis = math.sqrt((sigmaZ / samples) - (self.dg.ZAxis * self.dg.ZAxis))

        # If already set threshold, recalculate threshold vectors
        if self.actualThreshold:
            self.setThreshold(self.actualThreshold)

    def setThreshold(self, multiple = 1):
        '''
        uint8_t multiple = 1
        '''
        if multiple > 0:
            # If not calibrated, need calibrate
            if self.useCalibrate is False:
                self.calibrateGyro()

            # Calculate threshold vectors
            self.tg.XAxis = self.th.XAxis * multiple
            self.tg.YAxis = self.th.YAxis * multiple
            self.tg.ZAxis = self.th.ZAxis * multiple
        else:
            # No threshold
            self.tg.XAxis = 0
            self.tg.YAxis = 0
            self.tg.ZAxis = 0

        # Remember old threshold value
        self.actualThreshold = multiple

    def getThreshold(self): # -> uint8_t
        return self.actualThreshold

    def readRawAccel(self): # -> Vector
        # values = self.bus.read_i2c_block_data(self.address, self.MPU6050_REG_ACCEL_XOUT_H, 6)
        x = self.readRegister16(self.MPU6050_REG_ACCEL_XOUT_H)
        y = self.readRegister16(self.MPU6050_REG_ACCEL_YOUT_H)
        z = self.readRegister16(self.MPU6050_REG_ACCEL_ZOUT_H)
        # xha = values[0]
        # xla = values[1]
        # yha = values[2]
        # yla = values[3]
        # zha = values[4]
        # zla = values[5]

        # self.ra.XAxis = xha << 8 | xla
        # self.ra.YAxis = yha << 8 | yla
        # self.ra.ZAxis = zha << 8 | zla
        self.ra.XAxis = x
        self.ra.YAxis = y
        self.ra.ZAxis = z
        # print('raw accel values',values, (x,y,z), (xha << 8 | xla,yha << 8 | yla,zha << 8 | zla))

        return self.ra

    def readNormalizeAccel(self, useG = False): # -> Vector

        self.readRawAccel()

        self.na.XAxis = self.ra.XAxis * self.rangePerDigit
        self.na.YAxis = self.ra.YAxis * self.rangePerDigit
        self.na.ZAxis = self.ra.ZAxis * self.rangePerDigit

        if useG:
            self.na.XAxis = self.na.XAxis * self.GRAVITIY_MS2
            self.na.YAxis = self.na.YAxis * self.GRAVITIY_MS2
            self.na.ZAxis = self.na.ZAxis * self.GRAVITIY_MS2

        return self.na

    def readScaledAccel(self):  # -> Vector
        self.readRawAccel()

        self.na.XAxis = self.ra.XAxis * self.rangePerDigit
        self.na.YAxis = self.ra.YAxis * self.rangePerDigit
        self.na.ZAxis = self.ra.ZAxis * self.rangePerDigit

        return self.na

    def readRawGyro(self): # -> Vector
        values = self.bus.read_i2c_block_data(self.address, self.MPU6050_REG_GYRO_XOUT_H, 6)
        xha = values[0]
        xla = values[1]
        yha = values[2]
        yla = values[3]
        zha = values[4]
        zla = values[5]

        self.rg.XAxis = xha << 8 | xla
        self.rg.YAxis = yha << 8 | yla
        self.rg.ZAxis = zha << 8 | zla

        # x = self.readRegister16(self.MPU6050_REG_GYRO_XOUT_H)
        # y = self.readRegister16(self.MPU6050_REG_GYRO_YOUT_H)
        # z = self.readRegister16(self.MPU6050_REG_GYRO_ZOUT_H)
        
        # self.rg.XAxis = x
        # self.rg.YAxis = y
        # self.rg.ZAxis = z

        return self.rg


    def readNormalizeGyro(self): # -> Vector
        self.readRawGyro()
        if self.useCalibrate:
            self.ng.XAxis = (self.rg.XAxis - self.dg.XAxis) * self.dpsPerDigit
            self.ng.YAxis = (self.rg.YAxis - self.dg.YAxis) * self.dpsPerDigit
            self.ng.ZAxis = (self.rg.ZAxis - self.dg.ZAxis) * self.dpsPerDigit
        else:
            self.ng.XAxis = self.rg.XAxis * self.dpsPerDigit
            self.ng.YAxis = self.rg.YAxis * self.dpsPerDigit
            self.ng.ZAxis = self.rg.ZAxis * self.dpsPerDigit

        if self.actualThreshold:
            if math.abs(self.ng.XAxis) < self.tg.XAxis:
                self.ng.XAxis = 0
            if math.abs(self.ng.YAxis) < self.tg.YAxis:
                self.ng.YAxis = 0
            if math.abs(self.ng.ZAxis) < self.tg.ZAxis:
                self.ng.ZAxis = 0
        return self.ng

    # MPU-6050 Methods

    def get_temp(self):
        """Reads the temperature from the onboard temperature sensor of the MPU-6050.
        Returns the temperature in degrees Celcius.
        """
        raw_temp = self.read_i2c_word(self.TEMP_OUT0)

        # Get the actual temperature using the formule given in the
        # MPU-6050 Register Map and Descriptions revision 4.2, page 30
        actual_temp = (raw_temp / 340.0) + 36.53

        return actual_temp

    def set_accel_range(self, accel_range):
        """Sets the range of the accelerometer to range.
        accel_range -- the range to set the accelerometer to. Using a
        pre-defined range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range)

    def read_accel_range(self, raw=False):
        """Reads the range the accelerometer is set to.
        If raw is True, it will return the raw value from the ACCEL_CONFIG
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    def get_accel_data(self, g=False):
        """Gets and returns the X, Y and Z values from the accelerometer.
        If g is True, it will return the data in g
        If g is False, it will return the data in m/s^2
        Returns a dictionary with the measurement results.
        """
        x = self.read_i2c_word(self.ACCEL_XOUT0) - self.sum_data[0]
        y = self.read_i2c_word(self.ACCEL_YOUT0) - self.sum_data[1]
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        accel_scale_modifier = None
        accel_range = self.getRange() << 3 # self.read_accel_range(True)

        if accel_range == self.ACCEL_RANGE_2G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G
        elif accel_range == self.ACCEL_RANGE_4G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_4G
        elif accel_range == self.ACCEL_RANGE_8G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_8G
        elif accel_range == self.ACCEL_RANGE_16G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unkown range {} - accel_scale_modifier set to self.ACCEL_SCALE_MODIFIER_2G".format(accel_range))
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}

    def set_gyro_range(self, gyro_range):
        """Sets the range of the gyroscope to range.
        gyro_range -- the range to set the gyroscope to. Using a pre-defined
        range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyro_range)

    def read_gyro_range(self, raw=False):
        """Reads the range the gyroscope is set to.
        If raw is True, it will return the raw value from the GYRO_CONFIG
        register.
        If raw is False, it will return 250, 500, 1000, 2000 or -1. If the
        returned value is equal to -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.GYRO_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == self.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == self.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    def get_gyro_data(self):
        """Gets and returns the X, Y and Z values from the gyroscope.
        Returns the read values in a dictionary.
        """
        x = self.read_i2c_word(self.GYRO_XOUT0) - self.sum_data[3]
        y = self.read_i2c_word(self.GYRO_YOUT0) - self.sum_data[4]
        z = self.read_i2c_word(self.GYRO_ZOUT0) - self.sum_data[5]
        # 原始数据转弧度制
        x *= 0.0010653
        y *= 0.0010653
        z *= 0.0010653

        return {'x': x, 'y': y, 'z': z}

    def read_activites(self): # -> Activites
        data = self.read_i2c_byte(self.MPU6050_REG_INT_STATUS)

        self.a.isOverflow = ((data >> 4) & 1)
        self.a.isFreeFall = ((data >> 7) & 1)
        self.a.isInactivity = ((data >> 5) & 1)
        self.a.isActivity = ((data >> 6) & 1)
        self.a.isDataReady = ((data >> 0) & 1)

        data = self.read_i2c_byte(self.MPU6050_REG_MOT_DETECT_STATUS)

        self.a.isNegActivityOnX = ((data >> 7) & 1)
        self.a.isPosActivityOnX = ((data >> 6) & 1)

        self.a.isNegActivityOnY = ((data >> 5) & 1)
        self.a.isPosActivityOnY = ((data >> 4) & 1)

        self.a.isNegActivityOnZ = ((data >> 3) & 1)
        self.a.isPosActivityOnZ = ((data >> 2) & 1)

        return {
            'isOverflow' : self.a.isOverflow,
            'isFreeFall' : self.a.isFreeFall,
            'isInactivity' : self.a.isInactivity,
            'isDataReady' : self.a.isDataReady,
            'isNegActivityOnX' : self.a.isNegActivityOnX,
            'isPosActivityOnX' : self.a.isPosActivityOnX,
            'isNegActivityOnY' : self.a.isNegActivityOnY,
            'isPosActivityOnY' : self.a.isPosActivityOnY,
            'isNegActivityOnZ' : self.a.isNegActivityOnZ,
            'isPosActivityOnZ' : self.a.isPosActivityOnZ
        }

    def calibration(self):

        n = 200
        for i in range(n):
            self.sum_data[0] += self.read_i2c_word(self.ACCEL_XOUT0)
            self.sum_data[1] += self.read_i2c_word(self.ACCEL_YOUT0)
            self.sum_data[2] += self.read_i2c_word(self.ACCEL_ZOUT0)

            self.sum_data[3] += self.read_i2c_word(self.GYRO_XOUT0)
            self.sum_data[4] += self.read_i2c_word(self.GYRO_YOUT0)
            self.sum_data[5] += self.read_i2c_word(self.GYRO_ZOUT0)
            time.sleep(0.001)

        for i in range(6):
            self.sum_data[i] /= n

    def get_all_data(self):
        """Reads and returns all the available data."""
        temp = self.get_temp()
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()

        return [accel, gyro, temp]

if __name__ == "__main__":
    mpu = mpu6050(0x68)
    mpu.set_gyro_range(0x18)  # 2000deg/s
    mpu.calibration()
    while (True):
        accel_data = mpu.get_accel_data()
        gyro_data = mpu.get_gyro_data()
        print('accel_data x = {:>10.6f}, y = {:>10.6f} , z = {:>10.6f}'.format(accel_data['x'], accel_data['y'], accel_data['z']), 
            'gyro_data x = {:>10.6f}, y = {:>10.6f} , z = {:>10.6f}'.format(gyro_data['x'], gyro_data['y'], gyro_data['z']), end='\r')
