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

from qgis.core import *
from qgis.utils import *

from .alg import *

class MemoryExporter(SimpleExporter):
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

            calculator.setProgressValue(lineIndex, len(calculator.points), 
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
                rect  = calculator.calculateRectangleFormPointAndAngle(p)
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

            calculator.setProgressValue(lineIndex, len(calculator.points), 
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

            calculator.setProgressValue(lineIndex, len(calculator.points), 
                            "Save memory file for lines:{}".format(lineIndex))

    def save(self,calculator):
        self.generatePolygonsLayer(calculator)
        self.generateLinesLayer(calculator)
        self.generatePointsLayer(calculator)

        return True