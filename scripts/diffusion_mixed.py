#!/usr/bin/python

import sys
import argparse
import gzip
import time
import sys

des='Parse the time sorted (ascending) filtered sms file to find the best geolocation \
in the time sorted (ascending) geolocation file.'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-fsms', metavar='filtered_sms_file', help='input file for filtered data (gziped)', default=None)
parser.add_argument('-geo', metavar='geo_file', help='input geolocation file (gziped)', required=True)
parser.add_argument('-tres', metavar='t_res_file', help='output file with geolocated sms (gziped)', required=True)
parser.add_argument('-bsnei', metavar='bsnei_file', help='bsnei', required=True)

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

bsnei_file = gzip.open(args.bsnei, 'r')

output_file = gzip.open(args.tres, 'w')

dictGeo = dict()
dictU = dict()

def geoVoisin(geo, fromT, toT):
    res = []
    if geo in dictU:
        for geo1 in dictU[geo]:
            if geo1[1] > fromT and geo1[1] <= toT or geo1[2] > fromT and geo1[2] <= toT:
                if geo1[0] not in res:
                    res.append(geo1[0]) #TODO: unique
    return res

def uniqify(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def geoDest(u, fromT, toT):
    res = []
    if u in dictGeo:
        for geo1 in dictGeo[u]:
            if geo1[1] > fromT and geo1[2] <= toT:
                res.append(geo1) #TODO: unique
    return res

def intersect(geoList1, geoList2, t2):
    res = (-1, -1)
    for geo1 in geoList1:
        for geo2 in geoList2:
            if geo1[0] == geo2[0]:
                if geo1[1] > geo2[1] and geo1[1] <= geo2[2]:
                    if geo1[1] >= t2:
                        res = (geo1[1], geo1[0])
                    elif min(geo1[2], geo2[2]) > t2:
                        res = (t2, geo1[0])
                        
                elif geo1[2] > geo2[1] and geo1[2] <= geo2[2]:
                    if geo2[1] > t2:
                        res = (geo2[1], geo2[0])
                    elif geo1[2] >= t2:
                        res = (t2, geo2[0])
                            
    return res
    

tsms = 0
tgeo = 0
trefresh = 0
indmax = 0
tr = []
store_geo = []
tRes = 0
bs_packers = {}
bs_packers_alone = {}
ns_packers_number = 0
bs_packers_alone_number = 0
de_geo = {}
graph = {}
number_sms =0
de_geo_number = 0

for line in bsnei_file:
    line = line.rstrip('\n')
    items = line.split('\t')
    if (not items[0] in graph):
        graph[items[0]]=[]
    if (not items[1] in graph):
        graph[items[1]]=[]
    graph[items[0]].append(items[1])
    graph[items[1]].append(items[0])

for line in sms_file:
    line = line.rstrip('\n')
    items = line.split('\t')
    number_sms = number_sms+1
    tsms = int(items[0])
    usms = items[1]
    vsms = items[2]
    diff1 = int(items[3])
    geo1sms = items[4]
    diff2 = items[5]
    geo2sms = items[6]
    step=1800
    
    if diff1 > step:
        continue
    
    while tgeo < tsms+3600+step:
        linegeo = geo_file.readline().rstrip('\n')
        if linegeo == '':
            break
        itemsgeo = linegeo.split('\t')
        tgeo = int(itemsgeo[0])
        ugeo = itemsgeo[1]
        geogeo = itemsgeo[2]
        if ugeo in dictGeo:
            last = dictGeo[ugeo][len(dictGeo[ugeo])-1]
            
            if last[2] > tgeo-step:
                middle = (last[2] + (tgeo-step)) / 2
                dictGeo[ugeo][len(dictGeo[ugeo])-1][2] = middle
                dictGeo[ugeo].append([geogeo, middle, tgeo+step])
            else:
                dictGeo[ugeo].append([geogeo, tgeo-step, tgeo+step])
        else:
            dictGeo[ugeo] = [[geogeo, tgeo-step, tgeo+step]]
            
        if geogeo in dictU:
            last = dictU[geogeo][len(dictU[geogeo])-1]
            
            if last[2] > tgeo-step:
                middle = (last[2] + (tgeo-step)) / 2
                dictU[geogeo][len(dictU[geogeo])-1][2] = middle
                dictU[geogeo].append([ugeo, middle, tgeo+step])
            else:
                dictU[geogeo].append([ugeo, tgeo-step, tgeo+step])
        else:
            dictU[geogeo] = [[ugeo, tgeo-step, tgeo+step]]
    
    if tsms - trefresh > 86400:
        trefresh = tsms
        for i in dictGeo:
            indmax = -1;
            for j in range(0, len(dictGeo[i])):
                tcurrent = dictGeo[i][j][1]
                if tcurrent < tgeo-(3600+2*step):
                    indmax = j
            if indmax != -1:
                for j in range(0, indmax):
                    dictGeo[i].pop(0)
        
        for i in dictU:
            indmax = -1;
            for j in range(0, len(dictU[i])):
                tcurrent = dictU[i][j][1]
                if tcurrent < tgeo-(3600+2*step):
                    indmax = j
            if indmax != -1:
                for j in range(0, indmax):
                    dictU[i].pop(0)
                    
    tr_1 = geoVoisin(geo1sms, tsms-step, tsms+step) #liste des packers
    for i in range(0,len(graph[geo1sms])):
        tr_1 = tr_1 + geoVoisin(i, tsms-step, tsms+step)
    
    tr = uniqify(tr_1)
    
    de = geoDest(vsms, tsms-step, tsms+step+3600) #liste des antennes/temps possibles
    de_geo = {}
    de_geo_number = 0
    for k1 in range(0,len(de)):
        if not de[k1][0] in de_geo:
            de_geo[de[k1][0]]=1

    de_geo_number = len(de_geo)
    tRes = -1
    tResGeo = -1
    bs_packers = {}
    bs_packers_alone = {}
    bs_packers_alone_number = 0
    somme = 0
    bs_packers_number = 0
    for n in tr:
        geoTr = geoDest(n,tsms-step, tsms+step+3600) #liste des antennes/temps possibles
        bs_packers_alone = {}
        for k1 in range(0,len(geoTr)):
            if not geoTr[k1][0] in bs_packers:
                bs_packers[geoTr[k1][0]]=1
            if not geoTr[k1][0] in bs_packers_alone:
                bs_packers_alone[geoTr[k1][0]]=1

        somme = somme + len(geoTr)
        bs_packers_alone_number = bs_packers_alone_number + len(bs_packers_alone)
        a = intersect(geoTr, de, tsms)
        if a[0] >= 0 and (tRes == -1 or tRes > a[0]):
            tRes = a[0]
            tResGeo = a[1]
    bs_packers_number = len(bs_packers)
    if tRes != -1:
        tRes = tRes-tsms
    output_file.write(str(tsms) + '\t' + str(usms) + '\t' + str(vsms) + '\t' + str(diff1) + '\t' + str(geo1sms) + '\t' + str(tRes) + '\t' + str(tResGeo) + '\t' + str(len(tr)) + '\t' + str(len(de)) + '\t' + str(somme) + '\t' + str(de_geo_number) + '\t' + str(bs_packers_number)  + '\t' + str(bs_packers_alone_number) + '\n')


sms_file.close()
geo_file.close()
output_file.close()
