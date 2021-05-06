#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from sprp.core.alg import *
from sprp.export.geojson import *


from flask_cors import CORS

from flask import Flask, render_template,request
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sprp')
def api():
    minx=request.args.get("minx")
    miny=request.args.get("miny")
    maxx=request.args.get("maxx")
    maxy=request.args.get("maxy")

    print(minx, miny,maxx,maxy)
    # ?minx=116.23589&miny=39.90387&maxx=116.25291&maxy=39.90391
    ssc = SimpleStripCalculator(float(minx),float(miny),float(maxx),float(maxy),
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

    gje = GeoJsonExportor()
    gje.save(ssc)


    return "{}".format(gje.geojson)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)