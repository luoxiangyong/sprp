#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask_cors import CORS
from flask import Flask, render_template,request

from sprp.core.alg import *
from sprp.export.geojson import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sprp/simple')
def simple():
    startx=request.args.get("startx")
    starty=request.args.get("starty")
    endx=request.args.get("endx")
    endy=request.args.get("endy")

    # print(">>> ", minx, miny, maxx, maxy)
    # ?startx=116.23589&starty=39.90387&endx=116.25291&endy=39.90391
    ssc = SimpleStripCalculator(float(startx), float(starty),
                                float(endx), float(endy),
                            0,0, 
                            **{
                            "cameraWidth": 4000,
                            "cameraHeight":3000,
                            "focusLength":35,
                            "pixelSize":2,
                            "gsd":0.05,
                            "flightSpeed":80,
                            "courseOverlap":0.8,
                            "sidewiseOverlap":0.6, }
         )

    result = ssc.calculate()

    gje = GeoJsonExportor()
    gje.save(ssc)


    return "{}".format(gje.geojson)

@app.route('/api/sprp/polygon')
def polygon():
    polygon_wkt = request.args.get("wkt")
    focusLength = request.args.get("focusLength")
    pixelSize = request.args.get("pixelSize")
    cameraWidth = request.args.get("cameraWidth")
    cameraHeight = request.args.get("cameraHeight")
    courseOverlap = request.args.get("courseOverlap")
    sidewiseOverlap = request.args.get("sidewiseOverlap")
    gsd = request.args.get("gsd")


    print(">>> ", polygon_wkt)
   
   # ?wkt=POLYGON((116.23589 39.90387, 116.23589 39.90391,116.25291 39.90391, 116.25291 39.90387))
    spc = SimplePolygonCalculator(polygon_wkt,
                            **{
                            "cameraWidth": int(float(cameraWidth)),
                            "cameraHeight":int(float(cameraHeight)),
                            "focusLength":float(focusLength),
                            "pixelSize":float(pixelSize),
                            "gsd":float(gsd),
                            "flightSpeed":80,
                            "courseOverlap":float(courseOverlap),
                            "sidewiseOverlap":float(sidewiseOverlap), }
          )

    result = spc.calculate()

    gje = GeoJsonExportor()
    gje.save(spc)


    return "{}".format(gje.geojson)


def main():
    app.run(host='0.0.0.0', port=8000, debug=True)

if __name__ == "__main__":
    main()