
import laspy
import numpy as np

from sprp.core.alg import *
from sprp.exporter.ply import *

ssc = SimpleStripCalculator(116.23589,39.90387,116.23391,39.90391,
        1,1, 
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

sfe = PlyExporter('/Users/luoxiangyong/Devel/test-data/test-ply.ply')
sfe.save(ssc)
