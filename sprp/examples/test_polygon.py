from shapely import geometry,wkt
import pyproj
from alg import *
from shapefile_exporter import *

poly = wkt.loads("POLYGON ((116.22868787256349776 39.87961146736231655, 116.23701802381721393 39.89238421790663125, 116.24727333052047129 39.89254924122688095, 116.25439018557376869 39.8861456912557415, 116.23926097485040998 39.87592713868099992, 116.22868787256349776 39.87961146736231655))")

print(poly)
print(type(poly))
print(dir(poly))

#print(geometry.polygon.Polygon.minimum_rotated_rectangle))


print(poly.minimum_rotated_rectangle)
print(type(poly.boundary.xy))
print(type(poly.boundary.xy[0].tolist()))

lon = poly.boundary.xy[0].tolist()
lon.sort()
lat = poly.boundary.xy[1].tolist()
lat.sort()
print(lon),print(lat)

rect = poly.minimum_rotated_rectangle
print("RECT:",rect.to_wkt())
rect_coords = list(rect.exterior.coords)
print(rect_coords)

# 获取最佳包围矩形的三个点
p1 = rect_coords[0]
p2 = rect_coords[1]
p4 = rect_coords[3]

# 分别计算第一个点到邻近两个点的距离
geod = pyproj.Geod(ellps="WGS84")

# distance1 代表与第二个点的距离，CCW
angle1,backAngle1,distance1 = geod.inv(p1[0],p1[1],p2[0],p2[1])
# distance1 代表与第4个点的距离
angle2,backAngle2,distance2 = geod.inv(p1[0],p1[1],p4[0],p4[1])

print(angle1,backAngle1,distance1)
print(angle2,backAngle2,distance2)

angle1 = angle1 if angle1 > 0 else angle1 + 360
angle2 = angle2 if angle2 > 0 else angle2 + 360

print(angle1,backAngle1,distance1)
print(angle2,backAngle2,distance2)

# 确定使用哪个方向上的点为我所用
point_final = p2 if distance1 > distance2 else p4
distance_final = distance1 if distance1 < distance2 else distance2
angle_final_added = 0
if distance1 > distance2 and p1[0] < p4[0]:
    angle_final_added = -90
else:
     angle_final_added = 90

sidewiseline = 100

expand_count = int(distance_final / sidewiseline)
left_expand = expand_count if angle_final_added < 0 else 0
right_expand = expand_count if angle_final_added > 0 else 0


print("最终结果：",point_final,distance_final,expand_count,left_expand,right_expand)

ssc = SimpleStripCalculator(*p1,*point_final,
        left_expand,right_expand, 
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

sfe = ShapefileExporter('/Users/luoxiangyong/Devel/sprp/Data', 'test-polygon')
sfe.save(ssc)
