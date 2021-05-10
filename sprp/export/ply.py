"""
A simple photogrammetry routeing planner for UAV ,

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
#import laspy
import numpy as np
import random
import pyproj
#from plyfile import PlyData, PlyElement

from ..core.alg  import *

class PlyExportor(SimpleExportor):
    def __init__(self,filename, aboveGround = 0.):
        super().__init__()
        self.name = "PLY Exporter"

        self.vertex = None

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
        
        print("Height:", calculator.flight_height())
        for line in calculator.points:
            lineIndex = lineIndex + 1
            id = 0
            for p in line:
                id = id + 1
                name = "{}".format(id)
                lineName = "{}".format(lineIndex)
                self.x.append(p[0])
                self.y.append(p[1])
                self.z.append(self.aboveGround+calculator.flight_height())
                self.classification.append(5)

            calculator.set_progress_value(lineIndex, len(calculator.points), 
                            "Save ply file for points:{}".format(lineIndex))

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
                

            calculator.set_progress_value(lineIndex, len(calculator.points), 
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
        self.generatePointsLayer(calculator)
        self.generatePolygonsLayer(calculator)
        

        # 转换成投影坐标
        srcCRS = pyproj.Proj(proj = 'latlon', datum = 'WGS84')    # 定义数据地理坐标系
        targetCRS = pyproj.Proj(proj = 'merc', datum = 'WGS84')  # 定义转换投影坐标系
        for i in range(len(self.x)):
            
            #x1, y1 = srcCRS(self.x[i], self.y[i])
            x2, y2 = pyproj.transform(srcCRS, targetCRS, self.x[i], self.y[i])
            self.x[i] = x2
            self.y[i] = y2

            #print(x2,y2, self.z[i])

        points = [(self.x[i], self.y[i], self.z[i]) for i in range(len(self.x))]

        # face_data = np.array([([0, pIndex, pIndex + 1], 255, 255, 255),
        #                       ([0, pIndex, pIndex + 3], 255,   0,   0),
        #                      ],
        #             dtype=[('vertex_indices', 'i4', (3,)),
        #                    ('red', 'u1'), ('green', 'u1'),
        #                    ('blue', 'u1')])


        totalStations = 0
        for line in calculator.points:
            totalStations = totalStations + len(line)
        vetexCount = len(self.x)
        edgeCount = totalStations * 4
        faceCount = totalStations * 4
        rectCount = totalStations

        print("total station:", totalStations)
        print("The vetex count:", vetexCount)
        print("The edge count:", edgeCount)
        print("The tri face count:", faceCount)
        print("The rect face count:", rectCount)
        
        vertex = np.array(points,dtype=[('x', 'f8'), ('y', 'f8'),('z', 'f8')])
        print("vertex array shape:" , vertex.shape)

        with open(self.filename,'w') as file:
            file.write("""ply
format ascii 1.0
element vertex {}
comment vertices
property double x
property double y
property double z
property uint8 red
property uint8 green
property uint8 blue
element edge {}
property int32 vertex1
property int32 vertex2
property uint8 red
property uint8 green 
property uint8 blue 
element face {}
property list uchar int vertex_indices
end_header
""".format(vetexCount,edgeCount,faceCount+rectCount))

            # write vexex
            colors = np.zeros((totalStations,3),dtype=np.uint8)
            for i in range(len(self.x)):
                if i < totalStations:
                    colors[i,:] = random.randint(0,255),random.randint(0,255),random.randint(0,255)
                    file.write("{} {} {} {} {} {}\n".format(self.x[i], self.y[i], self.z[i],
                                *colors[i,:]))
                    file.flush()
                else:
                    index = int((i - totalStations)/4)
                    #print("对应的摄站点为:",index)
                    file.write("{} {} {} {} {} {}\n".format(self.x[i], self.y[i], self.z[i],
                        *colors[index,:]))
                    file.flush()

            # write edge
            for i in range(totalStations):
                pIndex = totalStations + i * 4
            
                file.write("{} {} 0 255 0\n".format(i, pIndex))
                file.flush()
                file.write("{} {} 0 255 0\n".format(i, pIndex + 1))
                file.flush()
                file.write("{} {} 0 255 0\n".format(i, pIndex + 2))
                file.flush()
                file.write("{} {} 0 255 0\n".format(i, pIndex + 3))
                file.flush()

            # write face
            for i in range(totalStations):
                
                pIndex = totalStations + i * 4
                #print("Current station:{}, pIndex:{}".format(i,pIndex))

                f1 = (i,  pIndex, pIndex + 1)
                f2 = (i , pIndex, pIndex + 3)
                f3 = (i , pIndex + 3, pIndex + 2)
                f4 = (i , pIndex + 2, pIndex + 1)

                #print("conic:", i, f1,f2,f3,f4)

                file.write("3 {} {} {}\n".format(f1[0], f1[1],f1[2]))
                file.flush()
                file.write("3 {} {} {}\n".format(f2[0], f2[1],f2[2]))
                file.flush()
                file.write("3 {} {} {}\n".format(f3[0], f3[1],f3[2]))
                file.flush()
                file.write("3 {} {} {}\n".format(f4[0], f4[1],f4[2]))
                file.flush()

            # write rect
            for i in range(totalStations):
                pIndex = totalStations + i * 4
            
                file.write("4 {} {} {} {}\n".format(pIndex, pIndex + 1,pIndex + 2, pIndex + 3))
                file.flush()

        return True

    # def save(self,calculator):
    #     self.generatePointsLayer(calculator)
    #     self.generatePolygonsLayer(calculator)
        

    #     # 转换成投影坐标
    #     srcCRS = pyproj.Proj(proj = 'latlon', datum = 'WGS84')    # 定义数据地理坐标系
    #     targetCRS = pyproj.Proj(proj = 'merc', datum = 'WGS84')  # 定义转换投影坐标系
    #     for i in range(len(self.x)):
            
    #         #x1, y1 = srcCRS(self.x[i], self.y[i])
    #         x2, y2 = pyproj.transform(srcCRS, targetCRS, self.x[i], self.y[i])
    #         self.x[i] = x2
    #         self.y[i] = y2

    #         #print(x2,y2, self.z[i])

    #     points = [(self.x[i], self.y[i], self.z[i]) for i in range(len(self.x))]
    #     vertex = np.array(points,
    #                 dtype=[('x', 'f8'), ('y', 'f8'),('z', 'f8')])

    #     print("line count:", len(calculator.points))
    #     print("point count perline:", len(calculator.points[0]))
    #     print("vertex size:" , vertex.shape)

    #     el = PlyElement.describe(vertex, 'vertex', comments=['vertices'])


    #     pIndex = len(calculator.points[0])
        
    #     # face_data = np.array([([0, pIndex, pIndex + 1], 255, 255, 255),
    #     #                       ([0, pIndex, pIndex + 3], 255,   0,   0),
    #     #                      ],
    #     #             dtype=[('vertex_indices', 'i4', (3,)),
    #     #                    ('red', 'u1'), ('green', 'u1'),
    #     #                    ('blue', 'u1')])

    #     lineCount = len(calculator.points)
    #     countPerLine = len(calculator.points[0])

    #     totalPoints = lineCount * countPerLine
    #     faceCount = totalPoints * 4

    #     face_data = np.zeros((faceCount,3),
    #                     dtype="i4"
    #                 )

    #     print("total point:", totalPoints)
    #     print("The face count:", faceCount)
    #     print("The face shape:", face_data.shape)

    #     for i in range(totalPoints):
            
    #         pIndex = countPerLine + i * 4
    #         print("Current line:1, pIndex:{}".format(i,pIndex))

    #         f1 = (i, pIndex, pIndex + 1)
    #         f2 = (i , pIndex, pIndex + 3)
    #         f3 = (i , pIndex + 3, pIndex + 2)
    #         f4 = (i , pIndex + 2, pIndex + 1)

    #         print("conic:", i, f1,f2,f3,f4)

    #         face_data[i] = f1
    #         face_data[i+1] = f2
    #         face_data[i+2] = f3
    #         face_data[i+3] = f4


    #     ply_faces = np.zeros(faceCount,
    #                      dtype=[('vertex_indices', 'i4', (3,))])

    #     ply_faces['vertex_indices'] = face_data

    #     face = PlyElement.describe(ply_faces,name='face')

    #     PlyData([el,face],text=True).write(self.filename)

    #     return True