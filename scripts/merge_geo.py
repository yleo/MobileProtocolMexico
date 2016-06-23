#!/usr/bin/python

import sys
import argparse
import gzip
import time

des='Merge the two geolocated sms file to find the best location.'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-geosms1', metavar='geo_sms_file1', help='input file1 with geolocated sms (gziped)', required=True)
parser.add_argument('-geosms2', metavar='geo_sms_file2', help='input file2 with geolocated sms (gziped)', required=True)
parser.add_argument('-geosmsoutput', metavar='geo_sms_file_output', help='output file with best geolocated sms (gziped)', required=True)

args = parser.parse_args()
    
try:
    geo_sms_file1 = gzip.open(args.geosms1, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.geosms1)
    exit()

try:
    geo_sms_file2 = gzip.open(args.geosms2, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.geosms2)
    exit()

output_file = gzip.open(args.geosmsoutput, 'w')

line1 = geo_sms_file1.readline()
line2 = geo_sms_file2.readline()
while line1 != '' and line2 != '':
    items1 = line1.rstrip('\n').split('\t')
    items2 = line2.rstrip('\n').split('\t')
    
    if items1[0] == items2[0] and items1[1] == items2[1] and items1[2] == items2[2]:
        time = int(items1[0])
        geo1f1 = items1[4]
        geo1f2 = items2[4]
        geo2f1 = items1[6]
        geo2f2 = items2[6]
        t1f1 = int(items1[3])
        t1f2 = int(items2[3])
        t2f1 = int(items1[5])
        t2f2 = int(items2[5])
        if (t1f1 != -1 or t1f2 != -1) and (t2f1 != -1 or t2f2 != -1):
            diff1f1 = abs(time - t1f1)
            diff1f2 = abs(time - t1f2)
            diff2f1 = abs(time - t2f1)
            diff2f2 = abs(time - t2f2)
            if diff1f1 < diff1f2:
                diff1 = diff1f1
                geo1 = geo1f1
            else:
                diff1 = diff1f2
                geo1 = geo1f2
            if diff2f1 < diff2f2:
                diff2 = diff2f1
                geo2 = geo2f1
            else:
                diff2 = diff2f2
                geo2 = geo2f2
            output_file.write(str(time) + '\t' + str(items1[1]) + '\t' + str(items1[2]) + '\t' + str(diff1) + '\t' + str(geo1) + '\t' + str(diff2) + '\t' + str(geo2) + '\n')
    else:
        print('Error with line1= ' + line1 + ' and line2= ' + line2)
    
    line1 = geo_sms_file1.readline()
    line2 = geo_sms_file2.readline()
        
geo_sms_file1.close()
geo_sms_file2.close()
output_file.close()