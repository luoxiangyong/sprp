#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
import os.path
from sprp.core.alg import *
from sprp.export.geojson import *
from sprp.export.shapefile import *
from sprp.export.ply import *
from sprp.export.las import *
from sprp.export.txt import *

def main():
    parser = argparse.ArgumentParser(description="A simple photogrammetry route planner for UAV.")

    parser.add_argument( '--filetype', '-t', help="Format of export file")

    parser.add_argument('-l',  '--length', help="Length of camera",type=str,required=True)
    parser.add_argument('-w',  '--width', help="Width of camera",type=int,required=True)
    parser.add_argument('-p',  '--pixelsize', help="Pixel size of camera",type=float,required=True)
    parser.add_argument('-f',  '--focuslength', help="Focus length of camera",type=float,required=True)

    parser.add_argument('-c',  '--courseoverlap', help="Overlap of course orientation",type=float,required=True)
    parser.add_argument('-s',  '--sidewiseoverlap', help="Overlap of sidewise orientation",type=float,required=True)
    parser.add_argument('-g',  '--gsd', help="GSD",type=float,required=True)

    parser.add_argument('--path', help="File path to save",required=True)
    parser.add_argument('--name', help="File name",required=True)

    parser.add_argument('-d','--wkt', help="Geometry",type=str,required=True)

    args = parser.parse_args()

    sc = SimplePolygonCalculator(args.wkt,
                                **{
                                "cameraWidth": int(float(args.length)),
                                "cameraHeight":int(float(args.width)),
                                "focusLength":float(args.focuslength),
                                "pixelSize":float(args.pixelsize),
                                "gsd":float(args.gsd),
                                "flightSpeed":80,
                                "courseOverlap":float(args.courseoverlap),
                                "sidewiseOverlap":float(args.sidewiseoverlap), }
            )
    result = sc.calculate()

    # 没有指定文件格式的情况下，默认为geojson
    #print('FileType:', args.filetype)
    if args.filetype is None or args.filetype.lower() == 'geojson':
        exportor = GeoJsonExportor(os.path.join(args.path, args.name)+'.json')
        exportor.save(sc)
    elif args.filetype.lower() == 'shapefile':
            exportor = ShapefileExporter(args.path, args.name)
            exportor.save(sc)
    elif args.filetype.lower() == 'ply':
            exportor = PlyExportor(os.path.join(args.path, args.name)+'.ply')
            exportor.save(sc)
    elif args.filetype.lower() == 'las':
            exportor = LasExportor(os.path.join(args.path, args.name)+'.las')
            exportor.save(sc)
    elif args.filetype.lower() == 'txt':
            exportor = TxtExportor(os.path.join(args.path, args.name)+'.txt')
            exportor.save(sc)

if __name__ == "__main__":
    main()