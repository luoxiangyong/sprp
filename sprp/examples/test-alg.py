from alg import *
from shapefile_exporter import *

if __name__ == "__main__":
    slc = SimpleLineCalculator(116.23589,39.90387,116.25291,39.90391,**{
        "cameraWidth": 4000,
        "cameraHeight":3000,
        "focusLength":35,
        "pixelSize":2,
        "gsd":0.05,
        "flightSpeed":80,
        "courseOverlap":0.8,
        "sidewiseOverlap":0.6
    })

    print(slc)

    linePointsResult,forwardAngle = slc.caculateLine(116.23589,39.90387,116.25291,39.90391)

    #slc.setLine(116.23589,39.90387,116.25291,39.90391)
    result = slc.calculate()
    print(result)
    print(slc.points)

    print("###############################################################################")

    ssc = SimpleStripCalculator(116.23589,39.90387,116.25291,39.90391,
        3,2, 
        **{
        "cameraWidth": 4000,
        "cameraHeight":3000,
        "focusLength":35,
        "pixelSize":2,
        "gsd":0.05,
        "flightSpeed":80,
        "courseOverlap":0.8,
        "sidewiseOverlap":0.6, 
    })
    result = ssc.calculate()
    print(result)
    print(ssc.points)
    print(len(ssc.points))

    sfe = ShapefileExporter('/Users/luoxiangyong/Devel/sprp/Data', 'test-project')
    sfe.save(ssc)


################################################################
###############################################################################
CAMERA_WIDTH = 2000
CAMERA_HEIGHT = 1000
CAMERA_GSD = 0.05
OVERLAP_FWD = 0.8
OVERLAP_CROSS = 0.6
BASELINE = (1-OVERLAP_FWD) * CAMERA_HEIGHT * CAMERA_GSD
CROSSLINE = (1-OVERLAP_CROSS) * CAMERA_WIDTH * CAMERA_GSD

def caculateLine(startx,starty, endx,endy,baseline):
    geod = pyproj.Geod(ellps="WGS84")
    forwardAngle,backwardAngle,distance = geod.inv(startx,starty, endx,endy)
    stationCount = math.floor(distance / baseline)
    wishedDistance = baseline * (stationCount + 1)
    wished_endx,wished_endy,tempAngle = geod.fwd(startx,starty,forwardAngle,wishedDistance)

    #print("Baseline = {}; Stations={}".format(baseline,stationCount + 1))
    points = geod.npts(startx,starty,wished_endx,wished_endy,stationCount - 1)
    #print(points)
    
    results = []
    results.append((startx,starty))
    results.extend(points)
    results.append((wished_endx,wished_endy))
    return results,forwardAngle

def writeLinesToShapefile(areaStartEndPoints,filename):
    if os.path.exists(filename):
        shutil.rmtree(filename)
    os.mkdir(filename)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    path = os.path.join(filename,"{}.shp".format(filename))
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

    id = 0
    print("Total point: {}".format(len(areaStartEndPoints)))
    for p in areaStartEndPoints:
        id = id + 1
        name = "LINE-{}".format(id)
        wkt = "LINESTRING({} {},{} {})".format(p[0],p[1],p[2],p[3])
        #print("POINT({},{})".format(p[0],p[1]))
        geometry = ogr.CreateGeometryFromWkt(wkt)
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(geometry)
        feature.SetField("ID", id)
        feature.SetField("NAME", name)
        layer.CreateFeature(feature)

def caculateArea(areaStartEndPoints,baseline):
    lineIndex = 0
    areaPoints = []
    for startEndPoint in areaStartEndPoints:
        #print("Caculate:{}".format(startEndPoint))
        points,angle = caculateLine(startEndPoint[0],startEndPoint[1],
                                    startEndPoint[2],startEndPoint[3],
                                    BASELINE)

        lineIndex = lineIndex + 1
        #writeLineToShapefile(points,'test-shapefile-line-{}'.format(lineIndex),angle)
        areaPoints.append(points)
    writeLinesToShapefile(areaStartEndPoints,'test-shapefile-lines')
    writeAreaToShapefile(areaPoints,"test-shapefile",angle)

def writeAreaToShapefile(areaPoints,filename,angle,cameraWidth=3000,cameraHeight=2000,gsd=0.05):
    ########################################################################
    # 创建点文件
    filename_points = "{}-points".format(filename)
    if os.path.exists(filename_points):
        shutil.rmtree(filename_points)
    os.mkdir(filename_points)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    path = os.path.join(filename_points,"{}.shp".format(filename_points))
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
    print("Total Line: {}".format(len(areaPoints)))
    for line in areaPoints:
        lineIndex = lineIndex + 1
        id = 0
        for p in line:
            id = id + 1
            name = "{}".format(id)
            lineName = "{}".format(lineIndex)
            wkt = "POINT({} {})".format(p[0],p[1])
            #print("POINT({},{})".format(p[0],p[1]))
            geometry = ogr.CreateGeometryFromWkt(wkt)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(geometry)
            feature.SetField("ID", id)
            feature.SetField("NAME", name)
            feature.SetField("LINE", lineName)
            layer.CreateFeature(feature)

    ########################################################################
    # 创建边界多边形文件
    filename_polygon = "{}-area-polygon".format(filename)
    if os.path.exists(filename_polygon):
        shutil.rmtree(filename_polygon)
    os.mkdir(filename_polygon)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    path = os.path.join(filename_polygon,"{}.shp".format(filename_polygon))
    dataSourcePolyon = driver.CreateDataSource(path)
    spatialReference = osr.SpatialReference()
    spatialReference.SetWellKnownGeogCS('WGS84')

    layerPolygon = dataSourcePolyon.CreateLayer("layer", spatialReference)

    field = ogr.FieldDefn("ID", ogr.OFTInteger)
    field.SetWidth(4)
    layerPolygon.CreateField(field)
    ########################################################################
    # 写入边界多边形
    wktPolygonStart = "POLYGON(("
    wktPolygonEnd = "))"
    wktPolygonStart = wktPolygonStart + "{} {},".format(areaPoints[0][0][0],areaPoints[0][0][1])
    wktPolygonStart = wktPolygonStart + "{} {},".format(areaPoints[0][-1][0],areaPoints[0][-1][1])
    
    wktPolygonStart = wktPolygonStart + "{} {},".format(areaPoints[-1][-1][0],areaPoints[-1][-1][1])
    wktPolygonStart = wktPolygonStart + "{} {},".format(areaPoints[-1][0][0],areaPoints[-1][0][1])
    wktPolygonStart = wktPolygonStart + "{} {}".format(areaPoints[0][0][0],areaPoints[0][0][1])
    wktPolygonStart = wktPolygonStart + wktPolygonEnd
    #print(wktPolygonStart)
    geometryPolygon = ogr.CreateGeometryFromWkt(wktPolygonStart)
    featurePolygon = ogr.Feature(layerPolygon.GetLayerDefn())
    featurePolygon.SetGeometry(geometryPolygon)
    featurePolygon.SetField("ID", 0)
    layerPolygon.CreateFeature(featurePolygon)


    ########################################################################
    # 创建每个点对应的多边形文件
    filename_polygon = "{}-points-polygon".format(filename)
    if os.path.exists(filename_polygon):
        shutil.rmtree(filename_polygon)
    os.mkdir(filename_polygon)
    driverPointPloygon = ogr.GetDriverByName('ESRI Shapefile')
    path = os.path.join(filename_polygon,"{}.shp".format(filename_polygon))
    dataSourcePointPloygon = driverPointPloygon.CreateDataSource(path)
    spatialReference = osr.SpatialReference()
    spatialReference.SetWellKnownGeogCS('WGS84')

    layerPointPloygon = dataSourcePointPloygon.CreateLayer("layer", spatialReference)

    field = ogr.FieldDefn("ID", ogr.OFTInteger)
    field.SetWidth(4)
    layerPointPloygon.CreateField(field)

    # 写入点对应的多边形
    idPolygon = 0
    lineIndex = 0
    #print("Total Line: {}".format(len(areaPoints)))
    for line in areaPoints:
        lineIndex = lineIndex + 1
        
        for p in line:
            idPolygon =  idPolygon + 1
            name = "{}".format(id)
            lineName = "{}".format(lineIndex)
            rect  = calculateRectangleFormPointAndAngle(p,angle,cameraWidth,cameraHeight,gsd)
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
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(geometry)
            feature.SetField("ID", idPolygon)
            # feature.SetField("NAME", name)
            # feature.SetField("LINE", lineName)
            layerPointPloygon.CreateFeature(feature)


"""
@brief 从点和指定的角度计算地面覆盖的矩形(footprint)

@param point 指定点
@param angle 航线方向
@param iwidth 图像长度
@param iheight 图像高度
@param gsd 地面分辨率

@return 返回地面覆盖的矩形的四脚点坐标
"""
def calculateRectangleFormPointAndAngle(point, angle, iwidth,iheight,gsd):
    width = iwidth * gsd
    height = iheight * gsd

    imgAngle = math.atan(iwidth*1.0/iheight) * 180/math.pi

    geod = pyproj.Geod(ellps="WGS84")

    # 矩形的对角线长
    distance = math.sqrt(math.pow(width,2) + math.pow(height,2)) 

    #print("矩形的计算值：width={} height={} dj = {}".format(width,height,distance))

    # 计算右上角点
    angleTR = angle - imgAngle
    longTR,latTR,tmpAngle = geod.fwd(point[0],point[1],angleTR, distance/2)

    # 计算右下角点
    angleBR = angle + imgAngle 
    longBR,latBR,tmpAngle = geod.fwd(point[0],point[1],angleBR, distance/2)

    # 计算左下角点
    angleBL = angleTR + 180
    longBL,latBL,tmpAngle = geod.fwd(point[0],point[1],angleBL, distance/2)

    # 计算左上角点
    angleTL = angleBR + 180
    longTL,latTL,tmpAngle = geod.fwd(point[0],point[1],angleTL, distance/2)

    #print("当前角度：\n{} \nTR:{} \nBR:{}\nBL:{}\nBT:{}".format(angle, angleTR,angleBR,angleBL,angleTL))

    result = []
    result.append((longTR,latTR))
    result.append((longBR,latBR))
    result.append((longBL,latBL))
    result.append((longTL,latTL))
    # 多边形闭合
    result.append((longTR,latTR))

    return result



if __name__ == "__main__":          
    # points,angle = caculateLine(116.23589,39.90387,116.25291,39.90391,50)
    # print("Angle:{}".format(angle))
    # writeLineToShapefile(points,'test-shapefile-01')

    # points,angle = caculateLine(116.23589,39.90287,116.25291,39.90291,50)
    # print("Angle:{}".format(angle))
    # writeLineToShapefile(points,'test-shapefile-02')


    start_long = 116.23589
    start_lat = 39.90387
    end_long = 116.25291
    end_lat = 39.90591
    geod = pyproj.Geod(ellps="WGS84")
    #long,lat,tmpAngle = geod.fwd(point[0],point[1],angleTR, distance/2)
    # 计算两点的角度
    angle,backAngle,distanceTmp = geod.inv(start_long, start_lat,end_long,end_lat)

    pointsOfLine = []
    long = start_long
    lat = start_lat
    for index in range(10):
        long,lat,tmpAngle = geod.fwd(long,lat, angle-90,CROSSLINE)
        end_long,end_lat,tempAngle = geod.fwd(long,lat, angle,distanceTmp)
        pointsOfLine.append((long,lat,end_long,end_lat))

    caculateArea(pointsOfLine,BASELINE)
    # caculateArea([[116.23589,39.90387,116.25291,39.90391],
    #               [116.23589,39.90287,116.25291,39.90291]],
    #               CAMERA_GSD)