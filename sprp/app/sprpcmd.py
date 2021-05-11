#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import argparse
import os.path
import tqdm,time

import sprp
from sprp.core.alg import *
from sprp.export.geojson import *
from sprp.export.shapefile import *
from sprp.export.ply import *
from sprp.export.las import *
from sprp.export.txt import *


_first_time = True
_pbar = None

def sc_progress_cb(current_value, total_value, msg):
    #print('c={},t={}:{}'.format(current_value, total_value, msg))
    global _first_time,_pbar

    if current_value == total_value:
        _first_time = True

    if _first_time:
        _pbar = tqdm.tqdm(total=total_value)
        _first_time = False
    
    _pbar.set_description(msg)
    _pbar.update(current_value)
    time.sleep(0.01)

def main():
    parser = argparse.ArgumentParser(
                description="A simple photogrammetry route planner for UAV.")

    parser.add_argument('-v', '--version', action='version', version=sprp.__version__,
                        help='Display version')

    parser.add_argument( '--filetype', '-t', 
                        help="Format of export file",
                        default = 'shaplefile',
                        choices=['shapefile','geojson',"txt",'ply','las'])

    parser.add_argument('-l',  '--length', help="Length of camera",
                        type=int,required=True,
                        default = 5000)
    parser.add_argument('-w',  '--width', help="Width of camera",
                        type=int,required=True,
                        default = 3000)
    parser.add_argument('-p',  '--pixelsize', help="Pixel size of camera (um)",
                        type=float,required=True,
                        default = 2.8)
    parser.add_argument('-f',  '--focuslength', help="Focus length of camera (mm)",
                        type=float,required=True,
                        default = 35)

    parser.add_argument('-c',  '--courseoverlap', help="Overlap of course orientation",
                        type=float,required=True,
                        default = 0.6)
    parser.add_argument('-s',  '--sidewiseoverlap', help="Overlap of sidewise orientation",
                        type=float,required=True,
                        default = 0.3)
    parser.add_argument('-g',  '--gsd', help="GSD(meter)",
                        type=float,required=True,
                        default = 0.05)

    parser.add_argument('--path', help="File path to save",required=True)
    parser.add_argument('--name', help="File name",required=True)

    parser.add_argument('-d','--wkt', help="Geometry Data, POLYGON type",type=str,required=True)

    args = parser.parse_args()

    _pbar = tqdm.tqdm(total=100, colour='green')
    _pbar.set_description("start calcuate")
    _pbar.update(0)
    time.sleep(0.1)
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

    #sc.set_pogress_callback(sc_progress_cb)
    result = sc.calculate()
    _pbar.set_description("end calcuate, save to the file")
    _pbar.update(50)

    time.sleep(0.1)

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

    _pbar.set_description("complete")
    _pbar.update(100)

if __name__ == "__main__":
    main()