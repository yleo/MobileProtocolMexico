#!/usr/bin/python

import sys
import argparse
import gzip
import time
import math
import snap

def distKm(l1, l2):
    lon1 = float(l1[0])
    lat1 = float(l1[1])
    lon2 = float(l2[0])
    lat2 = float(l2[1])
    lon = lon2-lon1
    lat = lat2-lat1
    
    y = lat*110.54
    x = lon*111.32*math.cos(lat)
    
    return math.sqrt(y*y + x*x)

des='Add the distance, in km, between caller and callee.'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-geosms', metavar='geo_sms_file', help='input file with geolocated sms (gziped)', required=True)
parser.add_argument('-bsgraph', metavar='bs_graph_file', help='input file with geolocated sms (gziped)', required=True)
parser.add_argument('-bsid', metavar='bsid_file', help='input file with geolocated sms (gziped)', required=True)
parser.add_argument('-geosmsoutput', metavar='geo_sms_file_output', help='output file with the distance (gziped)', required=True)

args = parser.parse_args()
    
try:
    geo_sms_file = gzip.open(args.geosms, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.geosms)
    exit()

try:
    bs_graph_file = gzip.open(args.bsgraph, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.bsgraph)
    exit()
    
try:
    bsid_file = gzip.open(args.bsid, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.bsid)
    exit()
    
output_file = gzip.open(args.geosmsoutput, 'w')

Graph = snap.TUNGraph.New()
for line in bs_graph_file:
    items = line.rstrip('\r').rstrip('\n').split('\t')
    bsA = int(items[0])
    bsB = int(items[1])
    if not Graph.IsNode(int(items[0])):
        Graph.AddNode(int(items[0]))
    if not Graph.IsNode(int(items[1])):
        Graph.AddNode(int(items[1]))
    Graph.AddEdge(int(items[0]),int(items[1]))
    
NIdToDistH = snap.TIntH()
shortest = {}
for i in Graph.Nodes():
    snap.GetShortPath(Graph, i.GetId(), NIdToDistH)
    for item in NIdToDistH:
        shortest[(i.GetId(), item)] = NIdToDistH[item]

bsid = {}
for line in bsid_file:
    items = line.rstrip('\r').rstrip('\n').split('\t')
    bsid[items[2]] = (items[0], items[1])

for line in geo_sms_file:
    items = line.rstrip('\r').rstrip('\n').split('\t')
    if items[4] != items[10]:
        ks = shortest[(int(items[4]), int(items[10]))]
    else:
        ks = 0
    ds = distKm(bsid[items[4]], bsid[items[10]])
    output_file.write(str(items[0]) + '\t' + str(items[1]) + '\t' + str(items[2]) + '\t' + str(items[3]) + '\t' + str(items[4]) + '\t' + str(items[5]) + '\t' + str(items[6]) + '\t' + str(items[7]) + '\t' + str(items[8]) + '\t' + str(items[9]) + '\t' + str(items[10]) + '\t' + str(ks) + '\t' + str(ds) + '\n')
    
geo_sms_file.close()
bs_graph_file.close()
bsid_file.close()
output_file.close()
