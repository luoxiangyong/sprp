"""
A simple photogrammetry routeing planning for UAV ,

Requirements: Python 3.6+.

Contact:  Xiangyong Luo <solO_lxy@126.com>

Copyright (c) 2021, Xiangyong Luo.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import pyproj
import math,os,shutil
from osgeo import ogr,osr

class SimpleExporter:
    def __init__(self):
        self.name = "Simple Exporter"

    def save(self,calculator):
        return False


class GeojsonExporter(SimpleExporter):
    def __init__(self):
        super().__init__()
        self.name = "Geojson Exporter"

    def save(self,calculator):
        return False

###############################################################################
class SimpleCalculator:
    def __init__(self, **kwargs):
        self.cameraWidth = kwargs['cameraWidth'] if kwargs['cameraWidth'] else 3000
        self.cameraWidth = kwargs['cameraWidth'] if kwargs['cameraWidth'] else 3000
        self.cameraHeight = kwargs['cameraHeight'] if kwargs['cameraHeight'] else 2000
        self.focusLength = kwargs['focusLength'] if kwargs['focusLength'] else 35
        self.pixelSize = kwargs['pixelSize'] if kwargs['pixelSize'] else 2.0
        self.gsd = kwargs['gsd'] if kwargs['gsd'] else 35
        self.flightSpeed = kwargs['flightSpeed'] if kwargs['flightSpeed'] else 80
        self.courseOverlap = kwargs['courseOverlap'] if kwargs['courseOverlap'] else 0.8
        self.sidewiseOverlap = kwargs['sidewiseOverlap'] if kwargs['sidewiseOverlap'] else 0.6
        
        self.courseline = (1 - self.courseOverlap) * self.cameraHeight * self.gsd
        self.sidewiseline = (1 - self.sidewiseOverlap) * self.cameraWidth * self.gsd

        # 存储每条航线的起点与终点 （startx, starty, endx, endy）
        self.lines = None

        # 存储整个区域的最终设计点，列表的列表
        self.points = None

        # 当前的设计航像
        self.courseAngle = None

        self.cb = None

        self.currentProgressValue = 0
        self.totalProgressValue = 100

    def flightHeight(self):
        return 1000 * self.gsd * self.focusLength / self.pixelSize

    def setPogressCallback(self,cb):
        self.cb = cb

    def setProgressValue(self,cur,total,msg):
        self.currentProgressValue = cur
        self.totalProgressValue = total
        self.emitProgress(msg)

    def emitProgress(self,msg):
        if self.cb:
            self.cb(self.currentProgressValue, self.totalProgressValue,msg)

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
        """.format(self.cameraWidth,self.cameraHeight,self.focusLength,self.pixelSize,
                    self.gsd,self.flightSpeed,self.courseOverlap,self.sidewiseOverlap,
                    self.courseline ,self.sidewiseline )

        return resstr

    def stastics(self):
        if not self.points == None:
            geod = pyproj.Geod(ellps="WGS84")
            
            pointCount = 0
            distance = 0

            for line in self.points:
                #print(line)
                pointCount = pointCount + len(line)
                p1 = line[0]
                p2 = line[-1]

                #print("Point:", p1,p2)

                forwardAngle,backwardAngle,distanceTmp = geod.inv(p1[0],p1[1], p2[0],p2[1])
                distance = distance + distanceTmp

            return {
                "flightHeight": self.flightHeight(),
                "couselineCount": len(self.lines),
                "pointCount": pointCount,
                "distance": distance / 1000,
                "workingTime": distance / self.flightSpeed
            }
        else: return None


    def caculateLine(self,startx,starty, endx,endy):
        geod = pyproj.Geod(ellps="WGS84")
        forwardAngle,backwardAngle,distance = geod.inv(startx,starty, endx,endy)
        stationCount = math.floor(distance / self.courseline)
        wishedDistance = self.courseline * (stationCount + 1)
        wished_endx,wished_endy,tempAngle = geod.fwd(startx,starty,forwardAngle,wishedDistance)

        points = geod.npts(startx,starty,wished_endx,wished_endy,stationCount - 1)
        
        results = []
        results.append((startx,starty))
        results.extend(points)
        results.append((wished_endx,wished_endy))

        self.courseAngle = forwardAngle

        return results,forwardAngle

    def calculate(self):
        return False

    """
    @brief 从点和指定的角度计算地面覆盖的矩形(footprint)

    @param point 指定点
    @param angle 航线方向
    @param iwidth 图像长度
    @param iheight 图像高度
    @param gsd 地面分辨率

    @return 返回地面覆盖的矩形的四脚点坐标
    """
    def calculateRectangleFormPointAndAngle(self,point):
        width = self.cameraWidth * self.gsd
        height = self.cameraHeight * self.gsd

        imgAngle = math.atan(self.cameraWidth*1.0/self.cameraHeight) * 180/math.pi

        geod = pyproj.Geod(ellps="WGS84")

        # 矩形的对角线长
        distance = math.sqrt(math.pow(width,2) + math.pow(height,2)) 

        #print("矩形的计算值：width={} height={} dj = {}".format(width,height,distance))

        # 计算右上角点
        angleTR = self.courseAngle - imgAngle
        longTR,latTR,tmpAngle = geod.fwd(point[0],point[1],angleTR, distance/2)

        # 计算右下角点
        angleBR = self.courseAngle + imgAngle 
        longBR,latBR,tmpAngle = geod.fwd(point[0],point[1],angleBR, distance/2)

        # 计算左下角点
        angleBL = angleTR + 180
        longBL,latBL,tmpAngle = geod.fwd(point[0],point[1],angleBL, distance/2)

        # 计算左上角点
        angleTL = angleBR + 180
        longTL,latTL,tmpAngle = geod.fwd(point[0],point[1],angleTL, distance/2)

        result = []
        result.append((longTR,latTR))
        result.append((longBR,latBR))
        result.append((longBL,latBL))
        result.append((longTL,latTL))
        # 多边形闭合
        result.append((longTR,latTR))

        return result

    

###############################################################################
class SimpleLineCalculator(SimpleCalculator):
    def __init__(self,startx,starty, endx,endy,**params):
        super().__init__(**params)
        #pass
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy

    def setLine(self,startx,starty, endx,endy):
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy


    def calculate(self):

        if self.startx and self.starty and self.endx and self.endy:
            self.points = []
            line = (self.startx,self.starty, self.endx,self.endy)
            self.lines = []
        
            linePointsResult,forwardAngle = self.caculateLine(*line)
            self.points.append(linePointsResult)
            self.lines.append(line)

            self.currentProgressValue = 100
            self.emitProgress("process the line:1")

            return True
        else:
            return False
        

class SimpleStripCalculator(SimpleCalculator):
    def __init__(self,startx,starty, endx,endy,leftExpand,rightExpand,**params):
        super().__init__(**params)
        self.leftExpand = leftExpand if leftExpand else 0
        self.rightExpand = rightExpand if rightExpand else 0

        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy

    def setLine(self,startx,starty, endx,endy):
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
        """.format(self.cameraWidth,self.cameraHeight,self.focusLength,self.pixelSize,
                    self.gsd,self.flightSpeed,self.courseOverlap,self.sidewiseOverlap,
                    self.courseline ,self.sidewiseline,
                    self.leftExpand,self.rightExpand)

        return resstr

    def calculate(self):

        if self.startx and self.starty and self.endx and self.endy:
            self.points = []
            self.lines = []
            lineStardEndPoints = []

            ########

            geod = pyproj.Geod(ellps="WGS84")
            angle,backAngle,distanceTmp = geod.inv(self.startx, self.starty,self.endx,self.endy)

            long = self.startx
            lat = self.starty
            for index in range(self.leftExpand):
                long,lat,tmpAngle = geod.fwd(long,lat, angle-90,self.sidewiseline)
                e_long,e_lat,tempAngle = geod.fwd(long,lat, angle,distanceTmp)
                lineStardEndPoints.append((long,lat,e_long,e_lat))

                
            lineStardEndPoints.append((self.startx, self.starty,self.endx,self.endy))

            long = self.startx
            lat = self.starty
            for index in range(self.rightExpand):
                long,lat,tmpAngle = geod.fwd(long,lat, angle+90,self.sidewiseline)
                e_long,e_lat,tempAngle = geod.fwd(long,lat, angle,distanceTmp)
                lineStardEndPoints.append((long,lat,e_long,e_lat))
            #######

            self.totalProgressValue = len(lineStardEndPoints)
            for line in lineStardEndPoints:
                linePointsResult,forwardAngle = self.caculateLine(*line)
                self.points.append(linePointsResult)
                self.lines.append(line)

                self.currentProgressValue = self.currentProgressValue + 1
                self.emitProgress("process the line:{}".format(self.currentProgressValue))

            return True
        else:
            return False


from shapely import geometry,wkt

class SimplePolygonCalculator(SimpleCalculator):
    def __init__(self,wkt_polygon,**params):
        super().__init__(**params)

        self.poly = wkt.loads(wkt_polygon)
        print("Before Orient:", self.poly.wkt)
        self.poly = geometry.polygon.orient(self.poly, 1.0)
        print("After Orient:", self.poly.wkt)

        rect = self.poly.minimum_rotated_rectangle
        rect_coords = list(rect.exterior.coords)

        # 获取最佳包围矩形的三个点
        p1 = rect_coords[0]
        p2 = rect_coords[1]
        p4 = rect_coords[3]

        # 分别计算第一个点到邻近两个点的距离
        geod = pyproj.Geod(ellps="WGS84")

        # distance1 代表与第二个点的距离，CCW
        angle1,backAngle1,distance1 = geod.inv(p1[0],p1[1],p2[0],p2[1])
        # distance1 代表与第4个点的距离
        angle2,backAngle2,distance2 = geod.inv(p1[0],p1[1],p4[0],p4[1])

        print(angle1,backAngle1,distance1)
        print(angle2,backAngle2,distance2)

        angle1 = angle1 if angle1 > 0 else angle1 + 360
        angle2 = angle2 if angle2 > 0 else angle2 + 360

        print(angle1,backAngle1,distance1)
        print(angle2,backAngle2,distance2)

        # 确定使用哪个方向上的点为我所用
        self.point_first = p1
        self.point_final = p2 if distance1 > distance2 else p4
        distance_final = distance1 if distance1 < distance2 else distance2
        self.angle_final_added = 0

        directionLeft = True
        if p1[0] < p2[0]: 
            if distance2 > distance1: # 
                directionLeft = False
            else:
                directionLeft = True
        else:
            if distance2 > distance1: # 
                directionLeft = False
            else:
                directionLeft = True

        expand_count = int(distance_final / self.sidewiseline)
        self.leftExpand = expand_count if directionLeft ==  True else 0
        self.rightExpand = expand_count if directionLeft !=  True else 0
        
    def calculate(self):

        startx = self.point_first[0] 
        starty = self.point_first[1] 
        endx = self.point_final[0]  
        endy = self.point_final[1] 
        if startx and starty and endx and endy:
            self.points = []
            self.lines = []
            lineStardEndPoints = []


            ########

            geod = pyproj.Geod(ellps="WGS84")
            angle,backAngle,distanceTmp = geod.inv(startx, starty,endx,endy)

            long = startx
            lat = starty
            for index in range(self.leftExpand):
                long,lat,tmpAngle = geod.fwd(long,lat, angle-90,self.sidewiseline)
                e_long,e_lat,tempAngle = geod.fwd(long,lat, angle,distanceTmp)
                lineStardEndPoints.append((long,lat,e_long,e_lat))
                
            lineStardEndPoints.append((startx, starty,endx,endy))

            long = startx
            lat = starty
            for index in range(self.rightExpand):
                long,lat,tmpAngle = geod.fwd(long,lat, angle+90,self.sidewiseline)
                e_long,e_lat,tempAngle = geod.fwd(long,lat, angle,distanceTmp)
                lineStardEndPoints.append((long,lat,e_long,e_lat))
            #######

            self.totalProgressValue = len(lineStardEndPoints)
            for line in lineStardEndPoints:
                linePointsResult,forwardAngle = self.caculateLine(*line)
                self.points.append(linePointsResult)
                self.lines.append(line)

                self.currentProgressValue = self.currentProgressValue + 1
                self.emitProgress("process the line:{}".format(self.currentProgressValue))
            return True
        else:
            return False
