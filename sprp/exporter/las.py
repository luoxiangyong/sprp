import laspy
import numpy as np
import random
import pyproj

from alg import *

class LasExporter(SimpleExporter):
    def __init__(self,filename, aboveGround = 0.):
        super().__init__()
        self.name = "Las Exporter"

        self.x = []
        self.y = []
        self.z = []

        self.classification = []

        self.filename = filename

        self.outfile = None

        self.aboveGround = aboveGround
    
    def generatePointsLayer(self,calculator):
    
        # 写入点
        id = 0
        lineIndex = 0
        
        print("Height:", calculator.flightHeight())
        for line in calculator.points:
            lineIndex = lineIndex + 1
            id = 0
            for p in line:
                id = id + 1
                name = "{}".format(id)
                lineName = "{}".format(lineIndex)
                self.x.append(p[0])
                self.y.append(p[1])
                self.z.append(self.aboveGround+calculator.flightHeight())
                self.classification.append(5)

            calculator.setProgressValue(lineIndex, len(calculator.points), 
                            "Save las file for points:{}".format(lineIndex))

    def generatePolygonsLayer(self, calculator):
        # 写入点对应的多边形
        idPolygon = 0
        lineIndex = 0
        for line in calculator.points:
            lineIndex = lineIndex + 1
            id = 0
            for p in line:
                id = id + 1
                name = "{}".format(id)
                lineName = "{}".format(lineIndex)
                rect  = self.calculateNoiseRectangle(p,calculator)

                self.x.append(rect[0][0])
                self.y.append(rect[0][1])
                self.z.append(self.aboveGround)

                self.classification.append(3)

                self.x.append(rect[1][0])
                self.y.append(rect[1][1])
                self.z.append(self.aboveGround)

                self.classification.append(3)

                self.x.append(rect[2][0])
                self.y.append(rect[2][1])
                self.z.append(self.aboveGround)

                self.classification.append(3)

                self.x.append(rect[3][0])
                self.y.append(rect[3][1])
                self.z.append(self.aboveGround)

                self.classification.append(2)
                

            calculator.setProgressValue(lineIndex, len(calculator.points), 
                            "Save las file for polygons:{}".format(lineIndex))

    def calculateNoiseRectangle(self,point,calculator):
        width = calculator.cameraWidth * calculator.gsd
        height = calculator.cameraHeight * calculator.gsd

        imgAngle = math.atan(calculator.cameraWidth*1.0/calculator.cameraHeight) * 180/math.pi
        randomAngle = random.randint(0,5)
        imgAngle = imgAngle + randomAngle

        geod = pyproj.Geod(ellps="WGS84")

        # 矩形的对角线长
        distance = math.sqrt(math.pow(width,2) + math.pow(height,2)) 

        #print("矩形的计算值：width={} height={} dj = {}".format(width,height,distance))

        # 计算右上角点
        angleTR = calculator.courseAngle - imgAngle
        longTR,latTR,tmpAngle = geod.fwd(point[0],point[1],angleTR, distance/2)

        # 计算右下角点
        angleBR = calculator.courseAngle + imgAngle 
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

    def save(self,calculator):
        hdr = laspy.header.Header()
        self.outfile = laspy.file.File(self.filename, mode="w", header=hdr)

        self.generatePolygonsLayer(calculator)
        self.generatePointsLayer(calculator)

        srcCRS = pyproj.Proj(proj = 'latlon', datum = 'WGS84')    # 定义数据地理坐标系
        targetCRS = pyproj.Proj(proj = 'merc', datum = 'WGS84')  # 定义转换投影坐标系
        for i in range(len(self.x)):
            
            #x1, y1 = srcCRS(self.x[i], self.y[i])
            x2, y2 = pyproj.transform(srcCRS, targetCRS, self.x[i], self.y[i])
            self.x[i] = x2
            self.y[i] = y2

            print(x2,y2, self.z[i])

        allx = np.array(self.x) # Four Points
        ally = np.array(self.y)
        allz = np.array(self.z)

        xmin = np.floor(np.min(allx))
        ymin = np.floor(np.min(ally))
        zmin = np.floor(np.min(allz))

        self.outfile.header.offset = [xmin,ymin,zmin]
        self.outfile.header.scale = [0.001,0.001,0.001]

        self.outfile.x = allx
        self.outfile.y = ally
        self.outfile.z = allz
        self.outfile.classification_flags = self.classification
        self.outfile.pt_src_id = np.linspace(0,len(allx))
        

        self.outfile.close()

        print("line count:", len(calculator.points))
        print("point count perline:", len(calculator.points[0]))
        print("total point count:", len(allx))

        print(allz)

        return True