"""
A simple photogrammetry routeing planner for UAV

Requirements: Python 3.6+.

Contact:  Xiangyong Luo <solo_lxy@126.com>

BSD 2-Clause License

Copyright (c) 2021, luoxiangyong
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from shapely import geometry, wkt
import pyproj
import math
import os
import shutil
from osgeo import ogr, osr


class SimpleExportor:
    def __init__(self):
        self.name = "Simple Exporter"

    def save(self, calculator):
        return False


class GeojsonExporter(SimpleExportor):
    def __init__(self):
        super().__init__()
        self.name = "Geojson Exporter"

    def save(self, calculator):
        return False


###############################################################################
class SimpleCalculator:
    """
    本类提供简单航摄区域自动曝光点设计的支持
    """

    def __init__(self, **kwargs):
        self.cameraWidth = kwargs.get('cameraWidth', 3000)
        self.cameraHeight = kwargs.get('cameraHeight', 2000)
        self.focusLength = kwargs.get('focusLength', 35)
        self.pixelSize = kwargs.get('pixelSize', 2.0)
        self.gsd = kwargs.get('gsd', 35)
        self.flightSpeed = kwargs.get('flightSpeed', 80)
        self.courseOverlap = kwargs.get('courseOverlap', 0.8)
        self.sidewiseOverlap = kwargs.get('sidewiseOverlap', 0.6)

        self.courseline = (1 - self.courseOverlap) * \
            self.cameraHeight * self.gsd
        self.sidewiseline = (1 - self.sidewiseOverlap) * \
            self.cameraWidth * self.gsd

        # 存储每条航线的起点与终点 （startx, starty, endx, endy）
        self._lines = None

        # 存储整个区域的最终设计点，列表的列表
        self._points = None

        # 当前的设计航像
        self.courseAngle = None

        self.cb = None

        self.currentProgressValue = 0
        self.totalProgressValue = 100

    @property
    def points(self):
        return self._points

    @property
    def lines(self):
        return self._lines

    def flight_height(self):
        return 1000 * self.gsd * self.focusLength / self.pixelSize

    def set_pogress_callback(self, cb):
        self.cb = cb

    def set_progress_value(self, cur, total, msg):
        self.currentProgressValue = cur
        self.totalProgressValue = total
        self.emit_progress(msg)

    def emit_progress(self, msg):
        if self.cb:
            self.cb(self.currentProgressValue, self.totalProgressValue, msg)

    def __str__(self):
        resstr = """
            cameraWidth:{},
            cameraHeight:{},
            focusLength:{},
            pixelSize:{},
            gsd:{},
            flightSpeed:{},
            courseOverlap:{},
            sidewiseOverlap:{}
            courseline:{},
            sidewiseline:{}
        """.format(self.cameraWidth, self.cameraHeight,
                   self.focusLength, self.pixelSize,
                   self.gsd, self.flightSpeed,
                   self.courseOverlap, self.sidewiseOverlap,
                   self.courseline, self.sidewiseline)

        return resstr

    def stastics(self):
        if self._points is not None:
            geod = pyproj.Geod(ellps="WGS84")

            pointCount = 0
            distance = 0

            for line in self._points:
                # print(line)
                pointCount = pointCount + len(line)
                p1 = line[0]
                p2 = line[-1]

                # print("Point:", p1,p2)

                forwardAngle, backwardAngle, distanceTmp = geod.inv(
                    p1[0], p1[1], p2[0], p2[1])
                distance = distance + distanceTmp

            return {
                "flightHeight": self.flight_height(),
                "couselineCount": len(self._lines),
                "pointCount": pointCount,
                "distance": distance / 1000,
                "workingTime": distance / self.flightSpeed
            }
        else:
            return None

    def caculate_line(self, startx, starty, endx, endy):
        geod = pyproj.Geod(ellps="WGS84")
        forwardAngle, backwardAngle, distance = geod.inv(
            startx, starty, endx, endy)
        stationCount = math.floor(distance / self.courseline)
        wishedDistance = self.courseline * (stationCount + 1)
        wished_endx, wished_endy, tempAngle = geod.fwd(
            startx, starty, forwardAngle, wishedDistance)

        points = geod.npts(startx, starty, wished_endx,
                           wished_endy, stationCount - 1)

        results = []
        results.append((startx, starty))
        results.extend(points)
        results.append((wished_endx, wished_endy))

        self.courseAngle = forwardAngle

        return results, forwardAngle

    def calculate(self):
        return False

    def calculate_footprint_from(self, point):
        """
        :brief 从点和指定的角度计算地面覆盖的矩形(footprint)

        :param point: 指定点
        :param angle: 航线方向
        :param iwidth: 图像长度
        :param iheight: 图像高度
        :param gsd: 地面分辨率

        :return: 返回地面覆盖的矩形的四脚点坐标
        """
        width = self.cameraWidth * self.gsd
        height = self.cameraHeight * self.gsd

        imgAngle = math.atan(self.cameraWidth*1.0 /
                             self.cameraHeight) * 180/math.pi

        geod = pyproj.Geod(ellps="WGS84")

        # 矩形的对角线长
        distance = math.sqrt(math.pow(width, 2) + math.pow(height, 2))

        # 计算右上角点
        angleTR = self.courseAngle - imgAngle
        longTR, latTR, tmpAngle = geod.fwd(
            point[0], point[1], angleTR, distance/2)

        # 计算右下角点
        angleBR = self.courseAngle + imgAngle
        longBR, latBR, tmpAngle = geod.fwd(
            point[0], point[1], angleBR, distance/2)

        # 计算左下角点
        angleBL = angleTR + 180
        longBL, latBL, tmpAngle = geod.fwd(
            point[0], point[1], angleBL, distance/2)

        # 计算左上角点
        angleTL = angleBR + 180
        longTL, latTL, tmpAngle = geod.fwd(
            point[0], point[1], angleTL, distance/2)

        result = []
        result.append((longTR, latTR))
        result.append((longBR, latBR))
        result.append((longBL, latBL))
        result.append((longTL, latTL))
        # 多边形闭合
        result.append((longTR, latTR))

        return result


###############################################################################
class SimpleLineCalculator(SimpleCalculator):
    """
    本类提供对线性的简单航摄区域自动曝光点设计的支持
    """

    def __init__(self, startx, starty, endx, endy, **params):
        super().__init__(**params)

        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy

    def set_line(self, startx, starty, endx, endy):
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy

    def calculate(self):

        if self.startx and self.starty and self.endx and self.endy:
            self._points = []
            line = (self.startx, self.starty, self.endx, self.endy)
            self._lines = []

            linePointsResult, forwardAngle = self.caculate_line(*line)
            self._points.append(linePointsResult)
            self._lines.append(line)

            self.currentProgressValue = 100
            self.emit_progress("process the line:1")

            return True
        else:
            return False


class SimpleStripCalculator(SimpleCalculator):
    """
    本类提供对条带区域的简单航摄区域自动曝光点设计的支持
    """

    def __init__(self, startx, starty, endx, endy,
                 leftExpand, rightExpand, **params):
        super().__init__(**params)
        self.leftExpand = leftExpand if leftExpand else 0
        self.rightExpand = rightExpand if rightExpand else 0

        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy

    def set_line(self, startx, starty, endx, endy):
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy

    def __str__(self):
        resstr = """
            cameraWidth:{},
            cameraHeight:{},
            focusLength:{},
            pixelSize:{},
            gsd:{},
            flightSpeed:{},
            courseOverlap:{},
            sidewiseOverlap:{},
            courseline:{},
            sidewiseline:{}
            leftExpand:{},
            rightExpand:{}
        """.format(self.cameraWidth, self.cameraHeight,
                   self.focusLength, self.pixelSize,
                   self.gsd, self.flightSpeed, self.courseOverlap,
                   self.sidewiseOverlap,
                   self.courseline, self.sidewiseline,
                   self.leftExpand, self.rightExpand)

        return resstr

    def calculate(self):
        if self.startx and self.starty and self.endx and self.endy:
            self._points = []
            self._lines = []
            lineStardEndPoints = []

            ########

            geod = pyproj.Geod(ellps="WGS84")
            angle, backAngle, distanceTmp = geod.inv(
                self.startx, self.starty, self.endx, self.endy)

            long = self.startx
            lat = self.starty
            for index in range(self.leftExpand):
                long, lat, tmpAngle = geod.fwd(
                    long, lat, angle-90, self.sidewiseline)
                e_long, e_lat, tempAngle = geod.fwd(
                    long, lat, angle, distanceTmp)
                lineStardEndPoints.append((long, lat, e_long, e_lat))

            lineStardEndPoints.append(
                (self.startx, self.starty, self.endx, self.endy))

            long = self.startx
            lat = self.starty
            for index in range(self.rightExpand):
                long, lat, tmpAngle = geod.fwd(
                    long, lat, angle+90, self.sidewiseline)
                e_long, e_lat, tempAngle = geod.fwd(
                    long, lat, angle, distanceTmp)
                lineStardEndPoints.append((long, lat, e_long, e_lat))
            #######

            self.totalProgressValue = len(lineStardEndPoints)
            for line in lineStardEndPoints:
                linePointsResult, forwardAngle = self.caculate_line(*line)
                self._points.append(linePointsResult)
                self._lines.append(line)

                self.currentProgressValue = self.currentProgressValue + 1
                self.emit_progress("process the line:{}".format(
                    self.currentProgressValue))

            return True
        else:
            return False


class SimplePolygonCalculator(SimpleCalculator):
    """
    本类提供对多边形区域的简单航摄区域自动曝光点设计的支持
    """

    def __init__(self, wkt_polygon, **params):
        super().__init__(**params)

        self.poly = wkt.loads(wkt_polygon)
        # print("Before Orient:", self.poly.wkt)
        self.poly = geometry.polygon.orient(self.poly, 1.0)
        # print("After Orient:", self.poly.wkt)

        rect = self.poly.minimum_rotated_rectangle
        rect_coords = list(rect.exterior.coords)

        # 获取最佳包围矩形的三个点
        p1 = rect_coords[0]
        p2 = rect_coords[1]
        p4 = rect_coords[3]

        # 分别计算第一个点到邻近两个点的距离
        geod = pyproj.Geod(ellps="WGS84")

        # distance1 代表与第二个点的距离，CCW
        angle1, backAngle1, distance1 = geod.inv(p1[0], p1[1], p2[0], p2[1])
        # distance1 代表与第4个点的距离
        angle2, backAngle2, distance2 = geod.inv(p1[0], p1[1], p4[0], p4[1])

        #print(angle1, backAngle1, distance1)
        #print(angle2, backAngle2, distance2)

        angle1 = angle1 if angle1 > 0 else angle1 + 360
        angle2 = angle2 if angle2 > 0 else angle2 + 360

        #print(angle1, backAngle1, distance1)
        #print(angle2, backAngle2, distance2)

        # 确定使用哪个方向上的点为我所用
        self.point_first = p1
        self.point_final = p2 if distance1 > distance2 else p4
        distance_final = distance1 if distance1 < distance2 else distance2
        self.angle_final_added = 0

        directionLeft = True
        if p1[0] < p2[0]:
            if distance2 > distance1:
                directionLeft = False
            else:
                directionLeft = True
        else:
            if distance2 > distance1:
                directionLeft = False
            else:
                directionLeft = True

        expand_count = int(distance_final / self.sidewiseline)
        self.leftExpand = expand_count if directionLeft is True else 0
        self.rightExpand = expand_count if directionLeft is not True else 0

    def calculate(self):
        startx = self.point_first[0]
        starty = self.point_first[1]
        endx = self.point_final[0]
        endy = self.point_final[1]
        if startx and starty and endx and endy:
            self._points = []
            self._lines = []
            lineStardEndPoints = []

            ########
            geod = pyproj.Geod(ellps="WGS84")
            angle, backAngle, distanceTmp = geod.inv(
                startx, starty, endx, endy)

            long = startx
            lat = starty
            for index in range(self.leftExpand):
                long, lat, tmpAngle = geod.fwd(
                    long, lat, angle-90, self.sidewiseline)
                e_long, e_lat, tempAngle = geod.fwd(
                    long, lat, angle, distanceTmp)
                lineStardEndPoints.append((long, lat, e_long, e_lat))

            lineStardEndPoints.append((startx, starty, endx, endy))

            long = startx
            lat = starty
            for index in range(self.rightExpand):
                long, lat, tmpAngle = geod.fwd(
                    long, lat, angle+90, self.sidewiseline)
                e_long, e_lat, tempAngle = geod.fwd(
                    long, lat, angle, distanceTmp)
                lineStardEndPoints.append((long, lat, e_long, e_lat))
            #######

            self.totalProgressValue = len(lineStardEndPoints)
            for line in lineStardEndPoints:
                linePointsResult, forwardAngle = self.caculate_line(*line)
                self._points.append(linePointsResult)
                self._lines.append(line)

                self.currentProgressValue = self.currentProgressValue + 1
                self.emit_progress("process the line:{}".format(
                    self.currentProgressValue))
            return True
        else:
            return False
