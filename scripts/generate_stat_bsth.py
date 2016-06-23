#!/usr/bin/python

import sys
import argparse
import gzip
import time

des='Parse geolocated sms to generate statistics on each base station/hour'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-smsgeo', metavar='geolocated_sms_file', help='input file with sms (gziped)', required=True)
parser.add_argument('-diffmax', metavar='seconds', help='diff maximum in seconds', required=True, type=int)
parser.add_argument('-bsthstat', metavar='bs_stat_file', help='output file with bs/hour statistics (gziped)', required=True)

args = parser.parse_args()

try:
    sms_geo_file = gzip.open(args.smsgeo, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.smsgeo)
    exit()
    
output_file = gzip.open(args.bsthstat, 'w')

diffmax = args.diffmax

bs_stat = {}

for line in sms_geo_file:
    line = line.rstrip('\n')
    items = line.split('\t')
    
    diff1 = int(items[3])
    diff2 = int(items[5])
    if diff1>diffmax or diff2>diffmax:
        continue
    
    time = int(items[0])
    geo1 = int(items[4])
    geo2 = int(items[6])
    ks = int(items[7])
    ds = float(items[8])
    
    hour = (time/3600+1)%24
    
    for geo in (geo1, geo2):
        try:
            stat = bs_stat[(geo, hour)]
        except KeyError:
            stat = {'ks':0, 'ds':0, 'a':0, 'pk0':0, 'pk1':0, 'pk2':0, 'pk3':0, 'pk4':0, 'pk5':0}
            bs_stat[(geo, hour)] = stat
        stat['ks'] += ks
        stat['ds'] += ds
        stat['a'] += 1
        if ks == 0:
            stat['pk0'] += 1
        elif ks == 1:
            stat['pk1'] += 1
        elif ks == 2:
            stat['pk2'] += 1
        elif ks == 3:
            stat['pk3'] += 1
        elif ks == 4:
            stat['pk4'] += 1
        elif ks == 5:
            stat['pk5'] += 1

for key in bs_stat:
    a = float(bs_stat[key]['a'])
    ks = bs_stat[key]['ks'] / a
    ds = bs_stat[key]['ds'] / a
    pk0 = bs_stat[key]['pk0'] / a
    pk1 = bs_stat[key]['pk1'] / a
    pk2 = bs_stat[key]['pk2'] / a
    pk3 = bs_stat[key]['pk3'] / a
    pk4 = bs_stat[key]['pk4'] / a
    pk5 = bs_stat[key]['pk5'] / a
    th = key[1]
    bs = key[0]
    
    output_file.write(str(th) + '\t' + str(bs) + '\t' + str(ks) + '\t' + str(ds) + '\t' + str(int(a)) + '\t' + str(pk0) + '\t' + str(pk1) + '\t' + str(pk2) + '\t' + str(pk3) + '\t' + str(pk4) + '\t' + str(pk5) + '\n')
        
sms_geo_file.close()
output_file.close()