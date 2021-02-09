import math
from . import Point3D, Point3DMap, Object3D
import pygame
from ui.theme import *

class Cube(Object3D):

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
    rotationAngle = 1

    mouseOffsetX = 0
    mouseOffsetY = 0
    offsetX = 0
    offsetY = 0
    offsetZ = 0

    def draw(self, surface):
        # // 绘制矩形ABCD
        lines = []

        point = self.transformCoordinatePoint(self.pointMap.A)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.B)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.C)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.D)
        lines.append((point.x, point.y))
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制矩形EFGH
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.E)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.F)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.G)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.H)
        lines.append((point.x, point.y))
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线AE
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.A)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.E)
        lines.append((point.x, point.y))
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线BF
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.B)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.F)
        lines.append((point.x, point.y))
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线CD
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.C)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.G)
        lines.append((point.x, point.y))
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线DH
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.D)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.H)
        lines.append((point.x, point.y))
        pygame.draw.lines(surface, color_white, True, lines)

    def animationFrame(self):
        for point in self.pointMap:
            x = point.x
            y = point.y
            z = point.z
            # 绕Y旋转
            point.x = x * math.cos(self.rotationAngle / 180 * math.pi) - z * math.sin(self.rotationAngle / 180 * math.pi)
            point.y = y
            point.z = z * math.cos(self.rotationAngle / 180 * math.pi) + x * math.sin(self.rotationAngle / 180 * math.pi)
        for point in self.pointMap:
            x = point.x
            y = point.y
            z = point.z
            # 绕X旋转
            point.x = x
            point.y = y * math.cos(self.rotationAngle / 180 * math.pi) - z * math.sin(self.rotationAngle / 180 * math.pi)
            point.z = z * math.cos(self.rotationAngle / 180 * math.pi) + y * math.sin(self.rotationAngle / 180 * math.pi)
        for point in self.pointMap:
            x = point.x
            y = point.y
            z = point.z
            # 绕Z旋转
            point.x = x * math.cos(self.rotationAngle / 180 * math.pi) - y * math.sin(self.rotationAngle / 180 * math.pi)
            point.y = y * math.cos(self.rotationAngle / 180 * math.pi) + x * math.sin(self.rotationAngle / 180 * math.pi)
            point.z = z

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
        # if event.button == 4: # wheel up
        #     self.globeRadius += 10
        #     if self.globeRadius > 1000:
        #         self.globeRadius = 1000
        #     self.createPoint()
            # self.visual.z += 100
            # if self.visual.z > 10000:
            #     self.visual.z = 10000
            # pass
        # if event.button == 5: # wheel down
        #     self.globeRadius -= 10
        #     if self.globeRadius < 20:
        #         self.globeRadius = 20
        #     self.createPoint()
            # self.visual.z -= 100
            # if self.visual.z < 1000:
            #     self.visual.z = 1000
            # pass