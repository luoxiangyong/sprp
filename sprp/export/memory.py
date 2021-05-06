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
import pyproj
import math,os,shutil
from osgeo import ogr,osr

from qgis.core import *
from qgis.utils import *

from ..core.alg  import *

class MemoryExporter(SimpleExportor):
    def __init__(self):
        super().__init__()
        self.name = "Memory Exporter"

    def generatePointsLayer(self,calculator):
        ########################################################################
        # 创建点文件
        
        vLayer = QgsVectorLayer('Point?crs=epsg:4326&field=ID:integer&field=NAME:string(20)', 
                                'Photogrammetry Point Dfaft Layer' , "memory")
        QgsProject().instance().addMapLayer(vLayer)


        # field = ogr.FieldDefn("ID", ogr.OFTInteger)
        # field.SetWidth(4)
        # vLayer.CreateField(field)
        # field = ogr.FieldDefn("NAME", ogr.OFTString)
        # field.SetWidth(20)
        # vLayer.CreateField(field)
        # field = ogr.FieldDefn("LINE", ogr.OFTString)
        # field.SetWidth(20)
        # vLayer.CreateField(field)
        ########################################################################

        
        # 写入点
        id = 0
        lineIndex = 0
        
        for line in calculator.points:
            lineIndex = lineIndex + 1
            id = 0
            for p in line:
                id = id + 1
                name = "{}".format(id)
                lineName = "{}".format(lineIndex)
                wkt = "POINT({} {})".format(p[0],p[1])
                #print(wkt)
                pr = vLayer.dataProvider()
                geometry = QgsGeometry.fromWkt(wkt)
                feature = QgsFeature()
                feature.setGeometry(geometry)
                feature.setAttributes([id,lineName])
                pr.addFeature(feature)
                # feature.SetField("ID", id)
                # feature.SetField("NAME", name)
                # feature.SetField("LINE", lineName)
                # vLayer.CreateFeature(feature)

            calculator.set_progress_value(lineIndex, len(calculator.points), 
                            "Save memory file for points:{}".format(lineIndex))

    def generatePolygonsLayer(self, calculator):
        ########################################################################
        # 创建每个点对应的多边形文件
        
        vLayer = QgsVectorLayer('Polygon?crs=epsg:4326&field=ID:integer&field=NAME:string(20)&field=LINE:string(20)', 
                                'Photogrammetry Polygon Dfaft Layer' , "memory")
        QgsProject().instance().addMapLayer(vLayer)

        # field = ogr.FieldDefn("ID", ogr.OFTInteger)
        # field.SetWidth(4)
        # vLayer.CreateField(field)

        # 写入点对应的多边形
        idPolygon = 0
        lineIndex = 0
        #print("Total Line: {}".format(len(areaPoints)))
        for line in calculator.points:
            lineIndex = lineIndex + 1
            id = 0
            for p in line:
                id = id + 1
                name = "{}".format(id)
                lineName = "{}".format(lineIndex)
                rect  = calculator.calculate_footprint_from(p)
                wkt = "POLYGON(({} {},{} {},{} {},{} {},{} {}))".format(
                    rect[0][0],rect[0][1],
                    rect[1][0],rect[1][1],
                    rect[2][0],rect[2][1],
                    rect[3][0],rect[3][1],
                    rect[0][0],rect[0][1],
                    )
                pr = vLayer.dataProvider()
                geometry = QgsGeometry.fromWkt(wkt)
                feature = QgsFeature()
                feature.setGeometry(geometry)
                feature.setAttributes([id,name,lineName])
                pr.addFeature(feature)
                #print("POINT({},{})".format(p[0],p[1]))
                #print(wkt)
                # geometry = ogr.CreateGeometryFromWkt(wkt)
                # feature = ogr.Feature(vLayer.GetLayerDefn())
                # feature.SetGeometry(geometry)
                # feature.SetField("ID", idPolygon)
                # # feature.SetField("NAME", name)
                # # feature.SetField("LINE", lineName)
                # vLayer.CreateFeature(feature)

            calculator.set_progress_value(lineIndex, len(calculator.points), 
                            "Save memory file for polygons:{}".format(lineIndex))

    def generateLinesLayer(self, calculator):
        vLayer = QgsVectorLayer('LineString?crs=epsg:4326&field=ID:integer&field=NAME:string(20)', 
                                'Photogrammetry Line Dfaft Layer' , "memory")
        QgsProject().instance().addMapLayer(vLayer)

        # field = ogr.FieldDefn("ID", ogr.OFTInteger)
        # field.SetWidth(4)
        # vLayer.CreateField(field)
        
        # field = ogr.FieldDefn("LINE", ogr.OFTString)
        # field.SetWidth(20)
        # vLayer.CreateField(field)
        ########################################################################

        # 写入点
        id = 0
        lineIndex = 0
        
        for line in calculator.lines:
            lineIndex = lineIndex + 1
            id = id + 1

            name = "{}".format(id)
            lineName = "{}".format(lineIndex)
            wkt = "LineString({} {}, {} {})".format(line[0],line[1],
                                                    line[2],line[3])
            # print(wkt)
            # geometry = ogr.CreateGeometryFromWkt(wkt)
            # feature = ogr.Feature(layer.GetLayerDefn())
            # feature.SetGeometry(geometry)
            # feature.SetField("ID", id)
            # feature.SetField("LINE", lineName)
            # vLayer.CreateFeature(feature)

            pr = vLayer.dataProvider()
            geometry = QgsGeometry.fromWkt(wkt)
            feature = QgsFeature()
            feature.setGeometry(geometry)
            feature.setAttributes([id,lineName])
            pr.addFeature(feature)

            calculator.set_progress_value(lineIndex, len(calculator.points), 
                            "Save memory file for lines:{}".format(lineIndex))

    def save(self,calculator):
        self.generatePolygonsLayer(calculator)
        self.generateLinesLayer(calculator)
        self.generatePointsLayer(calculator)

        return True