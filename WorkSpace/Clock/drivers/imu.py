#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import math

import numpy as np


class Mahony:
    def __init__(self):
        self.twoKpDef = 2.0 * 5.0
        self.twoKiDef = 2.0 * 0.0

        self.twoKp = self.twoKpDef
        self.twoKi = self.twoKiDef
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.integralFBx = 0.0
        self.integralFBy = 0.0
        self.integralFBz = 0.0

    def invSqrt(self, n):
        number = np.array([n])
        y = number.astype(np.float32)
        x2 = y * 0.5
        i = y.view(np.int32)
        i[:] = 0x5f3759df - (i >> 1)
        y = y * (1.5 - x2 * y * y)
        return y[0]

    def MahonyAHRSupdateIMU(self, gx, gy, gz, ax, ay, az, sampleFreq):
        recipNorm = 0
        halfvx = 0
        halfvy = 0
        halfvz = 0
        halfex = 0
        halfey = 0
        halfez = 0
        qa = 0
        qb = 0
        qc = 0
        g1 = 0
        g2 = 0
        g3 = 0
        g4 = 0
        g5 = 0

        # Compute feedback only if accelerometer measurement valid (avoids NaN in accelerometer normalisation)
        if (not ((ax == 0.0) and (ay == 0.0) and (az == 0.0))):

            # Normalise accelerometer measurement
            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az)
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm

            # Estimated direction of gravity and vector perpendicular to magnetic flux
            halfvx = self.q1 * self.q3 - self.q0 * self.q2
            halfvy = self.q0 * self.q1 + self.q2 * self.q3
            halfvz = self.q0 * self.q0 - 0.5 + self.q3 * self.q3

            # Error is sum of cross product between estimated and measured direction of gravity
            halfex = (ay * halfvz - az * halfvy)
            halfey = (az * halfvx - ax * halfvz)
            halfez = (ax * halfvy - ay * halfvx)

            # Compute and apply integral feedback if enabled
            if (self.twoKi > 0.0):
                self.integralFBx += self.twoKi * halfex * (1.0 / sampleFreq)  # integral error scaled by Ki
                self.integralFBy += self.twoKi * halfey * (1.0 / sampleFreq)
                self.integralFBz += self.twoKi * halfez * (1.0 / sampleFreq)
                gx += self.integralFBx  # apply integral feedback
                gy += self.integralFBy
                gz += self.integralFBz
            else:
                self.integralFBx = 0.0  # prevent integral windup
                self.integralFBy = 0.0
                self.integralFBz = 0.0

            # Apply proportional feedback
            gx += self.twoKp * halfex
            gy += self.twoKp * halfey
            gz += self.twoKp * halfez

        # Integrate rate of change of quaternion
        gx *= (0.5 * (1.0 / sampleFreq))  # pre-multiply common factors
        gy *= (0.5 * (1.0 / sampleFreq))
        gz *= (0.5 * (1.0 / sampleFreq))
        qa = self.q0
        qb = self.q1
        qc = self.q2
        self.q0 += (-qb * gx - qc * gy - self.q3 * gz)
        self.q1 += (qa * gx + qc * gz - self.q3 * gy)
        self.q2 += (qa * gy - qb * gz + self.q3 * gx)
        self.q3 += (qa * gz + qb * gy - qc * gx)

        # Normalise quaternion
        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3)
        self.q0 *= recipNorm
        self.q1 *= recipNorm
        self.q2 *= recipNorm
        self.q3 *= recipNorm

        g1 = 2.0 * (self.q1 * self.q3 - self.q0 * self.q2)
        g2 = 2.0 * (self.q0 * self.q1 + self.q2 * self.q3)
        g3 = self.q0 * self.q0 - self.q1 * self.q1 - self.q2 * self.q2 + self.q3 * self.q3
        g4 = 2.0 * (self.q1 * self.q2 + self.q0 * self.q3)
        g5 = self.q0 * self.q0 + self.q1 * self.q1 - self.q2 * self.q2 - self.q3 * self.q3

        pitch = -math.asin(g1) * 57.3
        roll = -math.atan2(g2, g3) * 57.3
        yaw = -math.atan2(g4, g5) * 57.3

        return [pitch, roll, yaw]


if __name__ == '__main__':
    imu = Mahony()
    angle = imu.MahonyAHRSupdateIMU(1, 1, 1, 1, 1, 1, 1)
    print(angle)