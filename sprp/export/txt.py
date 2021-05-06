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

import numpy as np

from ..core.alg import *

class TxtExporter(SimpleExportor):
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
                self.z.append(self.aboveGround+0.01)

            calculator.set_progress_value(lineIndex, len(calculator.points), 
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
                rect  = calculator.calculate_footprint_from(p)

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
                

            calculator.set_progress_value(lineIndex, len(calculator.points), 
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