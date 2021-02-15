import math
from . import Point3D, Point3DMap, Object3D
import pygame
from ui.theme import *

class Globe(Object3D):

    globeRadius = 100
    longitudeLineCount = 18
    latitudeLineCount = 17
    pointSize = 3
    rotationSpeed = 1

    visual = Point3D(0, 0, 1000) # x, y, z
    pointList = []
    offsetAngle = 0
    enable = False
    mouseOffsetX = 0
    mouseOffsetY = 0
    offsetX = 0
    offsetY = 0
    offsetZ = 0

    def __init__(self):
        self.createPoint()
        pass

    def createPoint(self):
        self.pointList = []
        for i in range(self.latitudeLineCount):
            y = math.cos(180 / (self.latitudeLineCount + 1) * (i + 1) / 180 * math.pi) * self.globeRadius
            radius = math.sin(180 / (self.latitudeLineCount + 1) * (i + 1) / 180 * math.pi) * self.globeRadius
            temp = []
            for j in range(self.longitudeLineCount):
                angle = 360 / self.longitudeLineCount * j
                x = radius * math.cos(angle / 180 * math.pi)
                z = radius * math.sin(angle / 180 * math.pi)
                temp.append({
                    'originX': x,
                    'originY': y,
                    'originZ': z,
                    'x': x,
                    'y': y,
                    'z': z,
                    'radius': radius,
                    'size': 4
                })
            self.pointList.append(temp)

    def draw(self, surface):
        isFirst = True
        for longitude in self.pointList:
            for item in longitude:
                p = self.transformCoordinatePoint(Point3D(item['x'], item['y']))
                center_x = p.x
                center_y = p.y
                r = item['size']
                sAngle = 0
                eAngle = 2 * math.pi
                pygame.draw.arc(surface, color_white if isFirst is False else color_green, (center_x - r / 2, center_y - r / 2, r*2, r*2), sAngle, eAngle)
                isFirst = False

    def animationFrame(self):
        for longitude in self.pointList:
            for item in longitude:
                index = longitude.index(item)
                originX = item['originX']
                originY = item['originY']
                originZ = item['originZ']
                z = originZ * math.cos(self.offsetY / 180 * math.pi) - originX * math.sin(self.offsetY / 180 * math.pi)
                x = originX * math.cos(self.offsetY / 180 * math.pi) + originZ * math.sin(self.offsetY / 180 * math.pi)
                originZ = z
                originX = x
                # // z = item.z
                # // x = item.x
                z = originZ * math.cos(self.offsetX / 180 * math.pi) - originY * math.sin(self.offsetX / 180 * math.pi)
                y = originY * math.cos(self.offsetX / 180 * math.pi) + originZ * math.sin(self.offsetX / 180 * math.pi)
                originZ = z
                originY = y
                # // z = item.z
                # // y = item.y
                x = originX * math.cos(self.offsetZ / 180 * math.pi) - originY * math.sin(self.offsetZ / 180 * math.pi)
                y = originY * math.cos(self.offsetZ / 180 * math.pi) + originX * math.sin(self.offsetZ / 180 * math.pi)
                item['size'] = self.pointSize * self.visual.z / (self.visual.z - z)
                item['x'] = x
                item['y'] = y
                item['z'] = z

    def mouseDown(self, event):
        # print('mouseDown', event)
        if event.button == 1:
            self.enable = True
            self.mouseOffsetY = event.pos[0]
            self.mouseOffsetX = event.pos[1]

    def mouseMove(self, event):
        # print('mouseMove', event)
        if event.buttons[0] and self.enable is True:
            self.offsetY = self.offsetY + (event.pos[0] - self.mouseOffsetY)
            self.offsetX = self.offsetX + (event.pos[1] - self.mouseOffsetX)
            self.mouseOffsetX = event.pos[1] % 360
            self.mouseOffsetY = event.pos[0] % 360

    def mouseUp(self, event):
        # print('mouseUp', event)
        if event.button == 1:
            self.enable = False
        if event.button == 4: # wheel up
            self.globeRadius += 10
            if self.globeRadius > 1000:
                self.globeRadius = 1000
            self.createPoint()
            # self.visual.z += 100
            # if self.visual.z > 10000:
            #     self.visual.z = 10000
            pass
        if event.button == 5: # wheel down
            self.globeRadius -= 10
            if self.globeRadius < 20:
                self.globeRadius = 20
            self.createPoint()

            # self.visual.z -= 100
            # if self.visual.z < 1000:
            #     self.visual.z = 1000
            pass

