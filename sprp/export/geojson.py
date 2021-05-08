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
import random
import pyproj
from geojson import Feature, Point, FeatureCollection,dumps,Polygon

from ..core.alg import *

class GeoJsonExportor(SimpleExportor):
    def __init__(self,filename='', aboveGround = 0.):
        super().__init__()
        self.name = "GeoJson Exporter"
        self.filename = filename
        self._geojson = None
    
    @property
    def geojson(self):
        return self._geojson

    def save(self,calculator):

        allPointsFeature = []
        allPolygonsFeature = []
       

        # polygon
        for line_index, line in enumerate(calculator.points):
            for point_index, point in enumerate(line):

                name = "{}".format(point_index)
                lineName = "{}".format(line_index)
        
                polygon = []
                rect  = calculator.calculate_footprint_from(point)
                polygon.append([
                    (rect[0][0], rect[0][1]),
                    (rect[1][0], rect[1][1]),
                    (rect[2][0], rect[2][1]),
                    (rect[3][0], rect[3][1])
                ])

                feature = Feature(geometry=Polygon(polygon), 
                    properties={"name": "{}-{}".format(lineName,point_index)})
                allPolygonsFeature.append(feature)

         # points
        for line_index, line in enumerate(calculator.points):
            for point_index, point in enumerate(line):

                name = "{}".format(point_index)
                lineName = "{}".format(line_index)
                #allPoints.append((line_index, point_index, point[0], point[1]))
                #allPoints.append(Point(point[0], point[1]))
                feature = Feature(geometry=Point((point[0], point[1])), 
                    properties={"name": "{}-{}".format(lineName, point_index)})
                allPointsFeature.append(feature)

        allFeatureCollection = FeatureCollection([*allPointsFeature,
                                                  *allPolygonsFeature])

        self._geojson = dumps(allFeatureCollection)
        if self.filename != '':
            with open(self.filename,'w') as file:
                file.write(self._geojson)

        

        