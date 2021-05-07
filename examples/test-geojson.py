import numpy as np

from sprp.core.alg import *
from sprp.export.geojson import *



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

gje = GeoJsonExportor('/Users/luoxiangyong/Devel/test-data/test-geojson.json')
gje.save(ssc)