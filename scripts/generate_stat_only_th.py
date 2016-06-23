#!/usr/bin/python

import sys
import argparse
import gzip
import time

des='Parse base station/hour statistics file to generate hour stat'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-bsthstat', metavar='bsth_stat_file', help='input file with base station/hour statistics (gziped)', required=True)
parser.add_argument('-thstat', metavar='th_stat_file', help='output file with hour statistics (gziped)', required=True)

args = parser.parse_args()

try:
    bsth_stat_file = gzip.open(args.bsthstat, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.bsthstat)
    exit()
    
output_file = gzip.open(args.thstat, 'w')

th_stat = {}

for line in bsth_stat_file:
    line = line.rstrip('\n')
    items = line.split('\t')
    
    hour = int(items[0])
    #bsid = int(items[1])
    ks = float(items[2])
    ds = float(items[3])
    a = int(items[4])
    pk0 = float(items[5])
    pk1 = float(items[6])
    pk2 = float(items[7])
    pk3 = float(items[8])
    pk4 = float(items[9])
    pk5 = float(items[10])
    
    try:
        stat = th_stat[hour]
    except KeyError:
        stat = {'ks':0, 'ds':0, 'a':0, 'pk0':0, 'pk1':0, 'pk2':0, 'pk3':0, 'pk4':0, 'pk5':0}
        th_stat[hour] = stat
    stat['ks'] += ks*a
    stat['ds'] += ds*a
    stat['a'] += a
    stat['pk0'] += pk0*a
    stat['pk1'] += pk1*a
    stat['pk2'] += pk2*a
    stat['pk3'] += pk3*a
    stat['pk4'] += pk4*a
    stat['pk5'] += pk5*a

for key in th_stat:
    a = float(th_stat[key]['a'])
    ks = th_stat[key]['ks'] / a
    ds = th_stat[key]['ds'] / a
    pk0 = th_stat[key]['pk0'] / a
    pk1 = th_stat[key]['pk1'] / a
    pk2 = th_stat[key]['pk2'] / a
    pk3 = th_stat[key]['pk3'] / a
    pk4 = th_stat[key]['pk4'] / a
    pk5 = th_stat[key]['pk5'] / a
    th = key
    
    output_file.write(str(th) + '\t' + str(ks) + '\t' + str(ds) + '\t' + str(int(a)) + '\t' + str(pk0) + '\t' + str(pk1) + '\t' + str(pk2) + '\t' + str(pk3) + '\t' + str(pk4) + '\t' + str(pk5) + '\n')
        
bsth_stat_file.close()
output_file.close()