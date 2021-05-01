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

from .alg import *

class ShapefileExporter(SimpleExporter):
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
        print(path)
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
                layer.CreateFeature(feature)

            calculator.setProgressValue(lineIndex, len(calculator.points), 
                            "Save shapefile for points:{}".format(lineIndex))

    def savePolygonsFile(self, calculator):
        ########################################################################
        # 创建每个点对应的多边形文件
        
        driverPointPloygon = ogr.GetDriverByName('ESRI Shapefile')
        path = os.path.join(self.path,
                    self.basename,"{}-polygons.shp".format(self.basename))
        print(path)
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
                rect  = calculator.calculateRectangleFormPointAndAngle(p)
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
            
            calculator.setProgressValue(lineIndex, len(calculator.points), 
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
            print(wkt)
            geometry = ogr.CreateGeometryFromWkt(wkt)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(geometry)
            feature.SetField("ID", id)
            feature.SetField("LINE", lineName)
            layer.CreateFeature(feature)

            calculator.setProgressValue(lineIndex, len(calculator.points), 
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