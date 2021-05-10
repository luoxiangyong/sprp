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

from ..core.alg  import *

class ShapefileExporter(SimpleExportor):
    def __init__(self,path,basename):
        super().__init__()
        self.name = "ESRI Shapefile Exporter"

        self.path = path
        self.basename = basename

    def savePointsFile(self,calculator):
        ########################################################################
        # 创建点文件
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        path = os.path.join(self.path,self.basename,
                            "{}-points.shp".format(self.basename))
        #print(path)
        dataSource = driver.CreateDataSource(path)
        
        spatialReference = osr.SpatialReference()
        spatialReference.SetWellKnownGeogCS('WGS84')

        layer = dataSource.CreateLayer("layer", spatialReference)

        field = ogr.FieldDefn("ID", ogr.OFTInteger)
        field.SetWidth(4)
        layer.CreateField(field)
        field = ogr.FieldDefn("NAME", ogr.OFTString)
        field.SetWidth(20)
        layer.CreateField(field)
        field = ogr.FieldDefn("LINE", ogr.OFTString)
        field.SetWidth(20)
        layer.CreateField(field)
        field = ogr.FieldDefn("Z", ogr.OFTReal)
        field.SetWidth(20)
        field.SetPrecision(5)
        layer.CreateField(field)
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
                geometry = ogr.CreateGeometryFromWkt(wkt)
                feature = ogr.Feature(layer.GetLayerDefn())
                feature.SetGeometry(geometry)
                feature.SetField("ID", id)
                feature.SetField("NAME", name)
                feature.SetField("LINE", lineName)
                feature.SetField("Z", calculator.flight_height())
                layer.CreateFeature(feature)

            calculator.set_progress_value(lineIndex, len(calculator.points), 
                            "Save shapefile for points:{}".format(lineIndex))

    def savePolygonsFile(self, calculator):
        ########################################################################
        # 创建每个点对应的多边形文件
        
        driverPointPloygon = ogr.GetDriverByName('ESRI Shapefile')
        path = os.path.join(self.path,
                    self.basename,"{}-polygons.shp".format(self.basename))
        #print(path)
        dataSourcePointPloygon = driverPointPloygon.CreateDataSource(path)
        spatialReference = osr.SpatialReference()
        spatialReference.SetWellKnownGeogCS('WGS84')

        layerPointPloygon = dataSourcePointPloygon.CreateLayer("layer", 
                                                spatialReference)

        field = ogr.FieldDefn("ID", ogr.OFTInteger)
        field.SetWidth(4)
        layerPointPloygon.CreateField(field)

        # 写入点对应的多边形
        idPolygon = 0
        lineIndex = 0
        #print("Total Line: {}".format(len(areaPoints)))
        for line in calculator.points:
            lineIndex = lineIndex + 1
            
            for p in line:
                idPolygon =  idPolygon + 1
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
                #print("POINT({},{})".format(p[0],p[1]))
                #print(wkt)
                geometry = ogr.CreateGeometryFromWkt(wkt)
                feature = ogr.Feature(layerPointPloygon.GetLayerDefn())
                feature.SetGeometry(geometry)
                feature.SetField("ID", idPolygon)
                # feature.SetField("NAME", name)
                # feature.SetField("LINE", lineName)
                layerPointPloygon.CreateFeature(feature)
            
            calculator.set_progress_value(lineIndex, len(calculator.points), 
                            "Save shapefile for polygons:{}".format(lineIndex))

    def saveLinesFile(self, calculator):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        path = os.path.join(self.path,self.basename,
                            "{}-lines.shp".format(self.basename))
        #print(path)
        dataSource = driver.CreateDataSource(path)
        
        spatialReference = osr.SpatialReference()
        spatialReference.SetWellKnownGeogCS('WGS84')

        layer = dataSource.CreateLayer("line layer", spatialReference)

        field = ogr.FieldDefn("ID", ogr.OFTInteger)
        field.SetWidth(4)
        layer.CreateField(field)
        
        field = ogr.FieldDefn("LINE", ogr.OFTString)
        field.SetWidth(20)
        layer.CreateField(field)
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
            geometry = ogr.CreateGeometryFromWkt(wkt)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(geometry)
            feature.SetField("ID", id)
            feature.SetField("LINE", lineName)
            layer.CreateFeature(feature)

            calculator.set_progress_value(lineIndex, len(calculator.points), 
                            "Save shapefile for lines:{}".format(lineIndex))

    def save(self,calculator):
        filename_points = os.path.join(self.path,self.basename)
        if os.path.exists(filename_points):
            shutil.rmtree(filename_points)
        os.mkdir(filename_points)

        self.savePointsFile(calculator)
        self.saveLinesFile(calculator)
        self.savePolygonsFile(calculator)

        return True