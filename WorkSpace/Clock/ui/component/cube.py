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

    def draw(self, surface):
        # self.ctx.clearRect(0, 0, self.canvasWidth, self.canvasHeight)
        # surface.fill(color_black)

        # // 绘制矩形ABCD
        # self.ctx.beginPath()
        lines = []

        point = self.transformCoordinatePoint(self.pointMap.A)
        # self.ctx.moveTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.B)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.C)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.D)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        # self.ctx.closePath()
        # self.ctx.stroke()
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制矩形EFGH
        # self.ctx.beginPath()
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.E)
        # self.ctx.moveTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.F)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.G)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.H)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        # self.ctx.closePath()
        # self.ctx.stroke()
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线AE
        # self.ctx.beginPath()
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.A)
        # self.ctx.moveTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.E)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        # self.ctx.stroke()
        # self.ctx.closePath()
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线BF
        # self.ctx.beginPath()
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.B)
        # self.ctx.moveTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.F)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        # self.ctx.stroke()
        # self.ctx.closePath()
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线CD
        # self.ctx.beginPath()
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.C)
        # self.ctx.moveTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.G)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        # self.ctx.stroke()
        # self.ctx.closePath()
        pygame.draw.lines(surface, color_white, True, lines)

        # // 绘制直线DH
        # self.ctx.beginPath()
        lines = []
        point = self.transformCoordinatePoint(self.pointMap.D)
        # self.ctx.moveTo(point.x, point.y)
        lines.append((point.x, point.y))
        point = self.transformCoordinatePoint(self.pointMap.H)
        # self.ctx.lineTo(point.x, point.y)
        lines.append((point.x, point.y))
        # self.ctx.stroke()
        # self.ctx.closePath()
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
        # for point in self.pointMap:
        #     x = point.x
        #     y = point.y
        #     z = point.z
        #     # 绕X旋转
        #     point.x = x
        #     point.y = y * math.cos(self.rotationAngle / 180 * math.pi) - z * math.sin(self.rotationAngle / 180 * math.pi)
        #     point.z = z * math.cos(self.rotationAngle / 180 * math.pi) + y * math.sin(self.rotationAngle / 180 * math.pi)
        # for point in self.pointMap:
        #     x = point.x
        #     y = point.y
        #     z = point.z
        #     # 绕Z旋转
        #     point.x = x * math.cos(self.rotationAngle / 180 * math.pi) - y * math.sin(self.rotationAngle / 180 * math.pi)
        #     point.y = y * math.cos(self.rotationAngle / 180 * math.pi) + x * math.sin(self.rotationAngle / 180 * math.pi)
        #     point.z = z
        