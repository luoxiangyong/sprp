#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from flask_cors import CORS
from flask import Flask, render_template,request,jsonify, send_file
import os,json,tempfile,uuid
import zipfile

from sprp.core.alg import *
from sprp.export.geojson import *
from sprp.export.shapefile import *

app = Flask(__name__)
#CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def error_404(error):
    return "对不起，这个地址未开放！"

@app.route('/api/sprp/simple')
def simple():
    startx=request.args.get("startx")
    starty=request.args.get("starty")
    endx=request.args.get("endx")
    endy=request.args.get("endy")

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
    filetype = request.args.get("filetype")
    user_filename = request.args.get("filename")
    
    user_filename = user_filename if (user_filename != None 
                    or user_filename == '') else "lxy"

    # print(">>> ", filetype)
   
    #try:
    # 生成geojson串
    if filetype is None:
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

        res = {
            "status":'success',
            "data":json.loads(gje.geojson)
        } 
        return jsonify(res)
    else: # 发送文件
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
        
        if filetype == 'GeoJSON':
            file_ext = ".json"
            filename = str(uuid.uuid4()) 
            filepath = os.path.join(tempfile.gettempdir(), filename) + file_ext
            # print("GEOJSON", filepath)
            gje = GeoJsonExportor(filepath)
            gje.save(spc)
            mime='application/json,application/octet-stream'
        else:
            filename = "{}".format(uuid.uuid4()) 
            filepath = tempfile.gettempdir()
            #print("ZIP文件：{}\n,{}\n{}\n---\n".format(filetype, filepath,filename))
            sfe = ShapefileExporter(filepath, filename)
            sfe.save(spc)
            
            filepath = os.path.join(filepath,filename)
            
            # 压缩文件
            _files = []
            list_files = os.listdir(filepath)
            
            for f in list_files:
                #print("LIST FILE",f)
                if os.path.isfile(os.path.join(filepath,f)):
                    _files.append(f)
            
            zip_file = zipfile.ZipFile(filepath + ".zip", 
                                        'w', zipfile.ZIP_DEFLATED)
            for f in _files:
                #print("FILE:", f)
                zip_file.write(os.path.join(filepath,f), f)
            zip_file.close()
            filepath = filepath + '.zip'
            mime = 'application/zip,application/octet-stream'

        res = {
            "status":'sucess',
            "data":filepath
            }
        #return jsonify(res)
        return send_file(filepath, mimetype=mime,
                    as_attachment=True, attachment_filename=user_filename)
    
    # except Exception as e:
    #     print(e)
    #     res = {
    #         "status":'failed',
    #         "data":str(e)
    #     } 
    #     return jsonify(res)
        

def main():
    port = os.environ.get("SPRP_PORT", "8000")
    app.run(host='0.0.0.0', port=int(port), debug=True)

if __name__ == "__main__":
    main()