#!/usr/bin/python

import sys
import argparse
import gzip
import time

des='Parse the time sorted (ascending) filtered sms file to find the best geolocation \
in the time sorted (ascending) geolocation file.'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-fsms', metavar='filtered_sms_file', help='input file for filtered data (gziped)', default=None)
parser.add_argument('-geo', metavar='geo_file', help='input geolocation file (gziped)', required=True)
parser.add_argument("-geosms", metavar='geo_sms_file', help='output file with geolocated sms (gziped)', required=True)

args = parser.parse_args()

if args.fsms != None:
    try:
        sms_file = gzip.open(args.fsms, 'r')
    except IOError:
        print('Error: can\'t open file named ' + args.fsms)
        exit()
else:
    sms_file = sys.stdin
    
try:
    geo_file = gzip.open(args.geo, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.geo)
    exit()
    
output_file = gzip.open(args.geosms, 'w')

temp = {}
t2 = 0
later = 0

for line in sms_file:
    test=1
    line = line.rstrip('\n')
    items = line.split('\t')
    if (len(items)==3):
        caller=items[1]
        callee=items[2]
        t1 = int(items[0])

        if (t1>=t2):
            if (later == 1):
                temp[items2[1]]=(t2,items2[2])
            later = 0
            while test == 1:
                line2 = geo_file.readline()
                if line2 == '':
                    break
                line2 = line2.rstrip('\n')
                items2 = line2.split('\t')
                t2 = int(items2[0])
                if (t2<=t1):
                    temp[items2[1]]=(t2,items2[2])
                else:
                    later = 1
                    test=0
        if (caller in temp):
            time1 = temp[caller][0]
            geo1 = temp[caller][1]
        else:
            time1 = -1
            geo1 = 0
            temp[caller]=(-1,0)
        if (callee in temp):
            time2 = temp[callee][0]
            geo2 = temp[callee][1]
        else:
            time2 = -1
            geo2 = 0
            temp[callee]=(-1,0)
        output_file.write(str(t1) + '\t' + str(caller) + '\t' + str(callee) + '\t' + str(time1) + '\t' + str(geo1) + '\t' + str(time2) + '\t' + str(geo2) + '\n')
        
sms_file.close()
geo_file.close()
output_file.close()