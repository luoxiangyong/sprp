import laspy
import numpy as np

from alg import *

class TxtExporter(SimpleExporter):
    def __init__(self,filename, aboveGround = 0):
        super().__init__()
        self.name = "Las Exporter"

        self.x = []
        self.y = []
        self.z = []

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
                self.z.append(self.aboveGround+0.01)

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
                rect  = calculator.calculateRectangleFormPointAndAngle(p)

                self.x.append(rect[0][0])
                self.y.append(rect[0][1])
                self.z.append(self.aboveGround)

                self.x.append(rect[1][0])
                self.y.append(rect[1][1])
                self.z.append(self.aboveGround)

                self.x.append(rect[2][0])
                self.y.append(rect[2][1])
                self.z.append(self.aboveGround)

                self.x.append(rect[3][0])
                self.y.append(rect[3][1])
                self.z.append(self.aboveGround)
                

            calculator.setProgressValue(lineIndex, len(calculator.points), 
                            "Save las file for polygons:{}".format(lineIndex))

    def save(self,calculator):
        with open(self.filename,"w") as txt:

            self.generatePolygonsLayer(calculator)
            self.generatePointsLayer(calculator)

            allx = np.array(self.x) # Four Points
            ally = np.array(self.y)
            allz = np.array(self.z)

            xmin = np.floor(np.min(allx))
            ymin = np.floor(np.min(ally))
            zmin = np.floor(np.min(allz))

            for i in range(len(self.x)):
                txt.write("{} {} {}\n".format(self.x[i],self.y[i],self.z[i]))

            return True

        return False