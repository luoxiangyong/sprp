###############################################################################
# A simple photogrammetry route planner for UAV
# 
# Requirements: Python 3.6+.
# 
# Contact:  Xiangyong Luo <solo_lxy@126.com>
# 
# BSD 2-Clause License
# 
# Copyright (c) 2021, luoxiangyong
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

import sys
if sys.platform == "linux":
    try:
        from pyproj import Geod
    except:
        pass
else:
    from shapely import wkt,geometry
    from pyproj import Geod

import math


class SimpleProgressNotifier(object):
    def __init__(self):
        self.cb = None
        self.currentProgressValue = 0
        self.totalProgressValue = 100

    def set_pogress_callback(self, cb):
        self.cb = cb

    def set_progress_value(self, cur, total, msg):
        self.currentProgressValue = cur
        self.totalProgressValue = total
        self.emit_progress(msg)

    def emit_progress(self, msg):
        if self.cb:
            self.cb(self.currentProgressValue, self.totalProgressValue, msg)


class SimpleExportor(SimpleProgressNotifier):
    def __init__(self):
        super(SimpleExportor, self).__init__()
        self.name = "Simple Exportor"

    def save(self, calculator):
        return False

###############################################################################
class SimpleCalculator(SimpleProgressNotifier):
    """????????????????????????????????????????????????????????????
    """
    def __init__(self, **kwargs):

        super(SimpleCalculator, self).__init__()

        self.cameraWidth = kwargs.get('cameraWidth', 3000)
        self.cameraHeight = kwargs.get('cameraHeight', 2000)
        self.focusLength = kwargs.get('focusLength', 35)
        self.pixelSize = kwargs.get('pixelSize', 2.0)
        self.gsd = kwargs.get('gsd', 35)
        self.flightSpeed = kwargs.get('flightSpeed', 80)
        self.courseOverlap = kwargs.get('courseOverlap', 0.8)
        self.sidewiseOverlap = kwargs.get('sidewiseOverlap', 0.6)

        self.courseExpand = kwargs.get('courseExpand', 3)
        self.sidewiseExpand = kwargs.get('sidewiseExpand', 3)

        self.courseline = (1 - self.courseOverlap) * \
            self.cameraHeight * self.gsd
        self.sidewiseline = (1 - self.sidewiseOverlap) * \
            self.cameraWidth * self.gsd

        # ???????????????????????????????????? ???startx, starty, endx, endy???
        self._lines = None

        # ??????????????????????????????????????????????????????
        self._points = None

        # ?????????????????????
        self.courseAngle = None

    @property
    def points(self):
        return self._points

    @property
    def lines(self):
        return self._lines

    def flight_height(self):
        return 1000 * self.gsd * self.focusLength / self.pixelSize

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
            geod = Geod(ellps="WGS84")

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
        geod = Geod(ellps="WGS84")
        forwardAngle, backwardAngle, distance = geod.inv(
            startx, starty, endx, endy)
        
        stationCount = math.floor(distance / self.courseline)

        wished_startx, wished_starty, tempAngle = geod.fwd(
            startx, starty, backwardAngle, self.courseline * self.courseExpand)


        print("wished start x,y:", wished_startx, wished_starty)

        wishedDistance = self.courseline * (stationCount + self.courseExpand * 2)
        wished_endx, wished_endy, tempAngle = geod.fwd(
            wished_startx, wished_starty, forwardAngle, wishedDistance)

        print("wished end x,y:", wished_endx, wished_endy)

        points = geod.npts(wished_startx, wished_starty, wished_endx,
                           wished_endy, stationCount + self.courseExpand * 2)



        results = []
        results.append((wished_startx, wished_starty))
        results.extend(points)
        results.append((wished_endx, wished_endy))

        self.courseAngle = forwardAngle

        print(results)

        return results, forwardAngle

    def calculate(self):
        return False

    def calculate_footprint_from(self, point):
        """???????????????????????????????????????????????????(footprint)

        Parameters
        ----------
        point : list 
            ?????????
        angle : float
            ????????????
        width : int 
            ????????????
        iheight : int 
            ????????????
        gsd : float 
            ???????????????

        Returns
        -------
        tuple
            ?????????????????????????????????????????????
        """
        width = self.cameraWidth * self.gsd
        height = self.cameraHeight * self.gsd

        imgAngle = math.atan(self.cameraWidth*1.0 /
                             self.cameraHeight) * 180/math.pi

        geod = Geod(ellps="WGS84")

        # ?????????????????????
        distance = math.sqrt(math.pow(width, 2) + math.pow(height, 2))

        # ??????????????????
        angleTR = self.courseAngle - imgAngle
        longTR, latTR, tmpAngle = geod.fwd(
            point[0], point[1], angleTR, distance/2)

        # ??????????????????
        angleBR = self.courseAngle + imgAngle
        longBR, latBR, tmpAngle = geod.fwd(
            point[0], point[1], angleBR, distance/2)

        # ??????????????????
        angleBL = angleTR + 180
        longBL, latBL, tmpAngle = geod.fwd(
            point[0], point[1], angleBL, distance/2)

        # ??????????????????
        angleTL = angleBR + 180
        longTL, latTL, tmpAngle = geod.fwd(
            point[0], point[1], angleTL, distance/2)

        result = []
        result.append((longTR, latTR))
        result.append((longBR, latBR))
        result.append((longBL, latBL))
        result.append((longTL, latTL))
        # ???????????????
        result.append((longTR, latTR))

        return result


###############################################################################
class SimpleLineCalculator(SimpleCalculator):
    """
    ????????????????????????????????????????????????????????????????????????
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
    ??????????????????????????????????????????????????????????????????????????????
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

            geod = Geod(ellps="WGS84")
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
    ?????????????????????????????????????????????????????????????????????????????????
    """
    def __init__(self, wkt_polygon, **params):
        super().__init__(**params)

        # TODO: wkt.loads may cause QGIS crash!!!
        #if sys.platform == 'linux':
        #    from shapely import wkt,geometry
        from shapely import wkt,geometry

        print("Original WKT:", wkt_polygon)
        self.poly = wkt.loads(wkt_polygon)
        #print("Before Orient:", self.poly.wkt)
        self.poly = geometry.polygon.orient(self.poly, 1.0)
        # print("After Orient:", self.poly.wkt)

        rect = self.poly.minimum_rotated_rectangle
        rect_coords = list(rect.exterior.coords)

        # ????????????????????????????????????
        p1 = rect_coords[0]
        p2 = rect_coords[1]
        p4 = rect_coords[3]

        # ???????????????????????????????????????????????????
        geod = Geod(ellps="WGS84")

        # distance1 ?????????????????????????????????CCW
        angle1, backAngle1, distance1 = geod.inv(p1[0], p1[1], p2[0], p2[1])
        # distance1 ????????????4???????????????
        angle2, backAngle2, distance2 = geod.inv(p1[0], p1[1], p4[0], p4[1])

        #print(angle1, backAngle1, distance1)
        #print(angle2, backAngle2, distance2)

        angle1 = angle1 if angle1 > 0 else angle1 + 360
        angle2 = angle2 if angle2 > 0 else angle2 + 360

        #print(angle1, backAngle1, distance1)
        #print(angle2, backAngle2, distance2)

        # ?????????????????????????????????????????????
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
            geod = Geod(ellps="WGS84")
            angle, backAngle, distanceTmp = geod.inv(
                startx, starty, endx, endy)

            long = startx
            lat = starty
            for index in range(self.leftExpand + self.sidewiseExpand):
                long, lat, tmpAngle = geod.fwd(
                    long, lat, angle-90, self.sidewiseline)
                e_long, e_lat, tempAngle = geod.fwd(
                    long, lat, angle, distanceTmp)
                lineStardEndPoints.append((long, lat, e_long, e_lat))

            lineStardEndPoints.append((startx, starty, endx, endy))

            long = startx
            lat = starty
            for index in range(self.rightExpand + self.sidewiseExpand):
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
            
