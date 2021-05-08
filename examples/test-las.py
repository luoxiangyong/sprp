
import laspy
import numpy as np

from sprp.core.alg import *
from sprp.export.las import *

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

filepath = '/Users/luoxiangyong/Devel/test-data'
import sys,os

if len(sys.argv) == 2:
    filepath = sys.argv[1]

sfe = LasExporter(os.path.join(filepath,'test-las.las'))
sfe.save(ssc)
