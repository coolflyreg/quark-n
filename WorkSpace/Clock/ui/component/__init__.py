# -*- coding: UTF-8 -*-
import math
from ui.core import UIManager
from ui.theme import *

class Point3D(object):
    x = 0
    y = 0
    z = 0
    __it = None
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
    def get_x(self):
        return self.x
    def set_x(self, x):
        self.x = x
    def get_y(self):
        return self.y
    def set_y(self, y):
        self.y = y
    def get_z(self):
        return self.z
    def set_z(self, z):
        self.z = z
    def value(self):
        return (self.x, self.y, self.z)
    def __next__(self):   #__next__用于返回下一个，返回下一个才能被称之为迭代器。
        return self.__it.__next__()
    def __iter__(self):   #__iter__用于返回自身，返回自身才能被调用。
        return iter([self.x, self.y, self.z])
        # return self.__it


class Point3DMap(object):
    A = None
    B = None
    C = None
    D = None
    E = None
    F = None
    G = None
    H = None
    __list = None
    def __init__(self, A, B, C, D, E, F, G, H):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.E = E
        self.F = F
        self.G = G
        self.H = H
    def __next__(self):   #__next__用于返回下一个，返回下一个才能被称之为迭代器。
        return self.__it.__next__()
    def __iter__(self):   #__iter__用于返回自身，返回自身才能被调用。
        if self.__list is None:
            self.__list = [self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.H]
        return self.__list.__iter__()


class Line(object):
    def __init__(self, a, b, c, d, z, start, end, gap):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.z = z
        self.start = start
        self.end = end
        self.gap = gap
        self.pointList = []
        self.computePointList()
    
    def computePointList(self):
        self.pointList = []
        # for (let i = self.start; i <= self.end; i = i + self.gap):
        for i in range(self.start, self.end + 1, self.gap):
            x = i
            y = self.a * math.sin((self.b * x + self.c) / 180 * math.pi) + self.d
            offset = i
            self.pointList.append({
                'x': x,
                'y': y,
                'z': self.z,
                'originX': x,
                'offset': offset,
                'canvasX': 0,
                'canvasY': 0
            })

    def updatePointList(self, rotationAngleSpeed, visual): 
        # self.pointList.forEach(item => {
        for item in self.pointList:
            x = item['x']
            # // let y = item.y
            z = item['z']
            item['x'] = x * math.cos(rotationAngleSpeed / 180 * math.pi) - z * math.sin(rotationAngleSpeed / 180 * math.pi)
            item['z'] = z * math.cos(rotationAngleSpeed / 180 * math.pi) + x * math.sin(rotationAngleSpeed / 180 * math.pi)
            item['y'] = self.a * math.sin((self.b * item['originX'] + self.c + item['offset']) / 180 * math.pi) + self.d
            item['canvasX'] = (item['x'] - visual.x) * visual.z / (visual.z - z)
            item['canvasY'] = (item['y'] - visual.y) * visual.z / (visual.z - z)


class Object3D(object):

    visual = Point3D(0, 0, 300) # x, y, z
    pointMap = Point3DMap(
                A = Point3D(-50, 50, 50),
                B = Point3D(-50, 50, -50),
                C = Point3D(50, 50, -50),
                D = Point3D(50, 50, 50),
                E = Point3D(-50, -50, 50),
                F = Point3D(-50, -50, -50),
                G = Point3D(50, -50, -50),
                H = Point3D(50, -50, 50)
            )

    def transformCoordinatePoint(self, p, offsetX = None, offsetY = None):
        windowSize = UIManager().getWindowSize()
        if offsetX is None: 
            offsetX = windowSize[0] / 2
        if offsetY is None:
            offsetY = windowSize[1] / 2

        return Point3D (
            x = (p.x - self.visual.x) * self.visual.z / (self.visual.z - p.z) + offsetX,
            y = (p.y - self.visual.y) * self.visual.z / (self.visual.z - p.z) + offsetY
        )

    def mouseDown(self, event):
        pass

    def mouseMove(self, event):
        pass

    def mouseUp(self, event):
        pass

    def mouseWheel(self, event):
        pass