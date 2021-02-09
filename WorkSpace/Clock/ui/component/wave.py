import math
from . import Point3D, Point3DMap, Object3D, Line
import pygame
from ui.core import UIManager
from ui.theme import *

class Wave(Object3D):

    visual = Point3D(0, -40, 600) # x, y, z
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
    lineList = [
        Line(10, 2, 0, 0, -150, -200, 200, 10),
        Line(10, 2, 0, 0, -120, -200, 200, 10),
        Line(10, 2, 0, 0, -90, -200, 200, 10),
        Line(10, 2, 0, 0, -60, -200, 200, 10),
        Line(10, 2, 0, 0, -30, -200, 200, 10),
        Line(10, 2, 0, 0, 0, -200, 200, 10),
        Line(10, 2, 0, 0, 30, -200, 200, 10),
        Line(10, 2, 0, 0, 60, -200, 200, 10),
        Line(10, 2, 0, 0, 90, -200, 200, 10),
        Line(10, 2, 0, 0, 120, -200, 200, 10),
        Line(10, 2, 0, 0, 150, -200, 200, 10)
    ]
    lineOffset = 0
    rotationAngleSpeed = 1

    def draw(self, surface):
        windowSize = UIManager().getWindowSize()
        # this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight)
        # this.lineList.forEach(line => {
        for line in self.lineList:
            # line.pointList.forEach(item => {
            for item in line.pointList:
                # this.ctx.beginPath()
                # // 暂且假定小圆点的原始半径是2,则投影半径可表示为
                pointSize = 2 * self.visual.z / (self.visual.z - item['z'])
                center_x = item['canvasX'] + windowSize[0] / 2
                center_y = item['canvasY'] + windowSize[1] / 3
                r = pointSize
                sAngle = 0
                eAngle = 2 * math.pi
                # this.ctx.arc(item.canvasX + this.canvasWidth / 2, item.canvasY + this.canvasHeight / 3, pointSize, 0, 2 * Math.PI)
                # this.ctx.closePath()
                # this.ctx.fill()
                # pygame.draw.arc(surface, color, rect, start_angle, stop_angle, width=1)
                pygame.draw.arc(surface, color_white, (center_x - r / 2, center_y - r / 2, r*2, r*2), sAngle, eAngle)
                # pygame.draw.circle(surface, color_white, (int(center_x - r / 2), int(center_y - r / 2)), int(r))


    def animationFrame(self):
        # self.lineList.forEach((line, index) => {
        for line in self.lineList:
            index = self.lineList.index(line)
            line.c = self.lineOffset + index * 30
            line.updatePointList(self.rotationAngleSpeed, self.visual)
        self.lineOffset = self.lineOffset + 2
        # self.logger.debug('animationFrame _after {} {}'.format(self.rotationAngle, self.pointMap.A.value()))
        # this.draw()
        # this.animationFrame()
        # this.lineList.forEach((line, index) => {