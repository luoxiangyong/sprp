#!/bin/bash


filepath='/Users/luoxiangyong/Devel/test-data'
wkt='POLYGON ((116.22868787256349776 39.87961146736231655, 116.23701802381721393 39.89238421790663125, 116.24727333052047129 39.89254924122688095, 116.25439018557376869 39.8861456912557415, 116.23926097485040998 39.87592713868099992, 116.22868787256349776 39.87961146736231655))'

sprp-cmd --path $filepath --name test-cmd-data -l 4000 -w 3000 -p 2 -f 35 \
        -c 0.8 -s 0.6  -g 0.05 --wkt "$wkt"

sprp-cmd --path $filepath --name test-cmd-data -l 4000 -w 3000 -p 2 -f 35 \
        -c 0.8 -s 0.6  -g 0.05 --wkt "$wkt" -t shapefile

#sprp-cmd --path $filepath --name test-cmd-data -l 4000 -w 3000 -p 2 -f 35 \
#        -c 0.8 -s 0.6  -g 0.05 --wkt "$wkt" -t ply

#sprp-cmd --path $filepath --name test-cmd-data -l 4000 -w 3000 -p 2 -f 35 \
#        -c 0.8 -s 0.6  -g 0.05 --wkt "$wkt" -t las

#sprp-cmd --path $filepath --name test-cmd-data -l 4000 -w 3000 -p 2 -f 35 \
#        -c 0.8 -s 0.6  -g 0.05 --wkt "$wkt" -t txt