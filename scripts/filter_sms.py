#!/usr/bin/python

import time
import argparse
import gzip
import sys

des='Parse a raw sms file to only extract necessary data (timestamp, caller and callee) \
with only known users in the id user file.'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-fsms', metavar='filtered_sms_file', help='output file for filtered data (gziped)', required=True)
parser.add_argument('-uid', metavar='user_id_file', help='input file for id yoda graph (gziped)', required=True)
parser.add_argument('-sms', metavar='raw_sms_file', help='input file with raw sms data (gziped)', default=None)
parser.add_argument('-v', action='store_true', help='verbose output')
args = parser.parse_args()

if args.sms != None:
    try:
        input_file = gzip.open(args.sms, 'r')
    except IOError:
        print('Error: can\'t open file named ' + args.sms)
        exit()
else:
    input_file = sys.stdin

try:
    id_user_file = gzip.open(args.uid, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.uid)
    exit()

output_file = gzip.open(args.fsms, 'w')
verbose = args.v

print('Started...')

sys.stdout.write('Reading id user file...')
sys.stdout.flush()
id_user_list = {}
for line in id_user_file:
    line = line.rstrip('\n')
    items = line.split('\t')
    if(len(items) != 2):
        continue
    id_user_list[items[0]]=items[1]
sys.stdout.write('End.\n')
sys.stdout.flush()

print('Reading sms file...')
total_count = 0
good_count = 0
for line in input_file:
    items = line.rstrip('\r').rstrip('\n').split('\t')
    total_count +=1
    if(len(items) != 10):
        raise ValueError
    try:
        caller = items[2]
        callee = items[3]
        if caller == callee:
            raise ValueError
        timestamp = time.mktime(time.strptime(items[9].replace('.', ''), '%d/%m/%Y %I:%M:%S %p'))
        if (caller not in id_user_list) or (callee not in id_user_list):
            raise ValueError
        caller_id = id_user_list[caller]
        callee_id = id_user_list[callee]
        good_count +=1
        output_file.write(str(int(timestamp)) + '\t' + str(caller_id) + '\t' + str(callee_id) + '\n')
    except (ValueError, IndexError):
        continue
    finally:
        if verbose:
            print('Good: ' + str(good_count) + ' || Good ratio: ' + str(good_count/float(total_count)*100) + '% || Total: ' + str(total_count))
        else:
            if total_count%500000 == 0:
                print('  parsed lines: ' + str(total_count))

print('End !')
print
print('Total parsed lines: ' + str(total_count))
print(str(good_count) + ' lines in the output file')
print('Good data ratio: ' + str(good_count/float(total_count)*100) + '%')
print

input_file.close()
id_user_file.close()
output_file.close()