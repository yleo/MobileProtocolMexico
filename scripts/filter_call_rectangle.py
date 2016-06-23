import time
import argparse
import gzip
import sys

minlon = -99.3641835; maxlon = -98.9401855; minlat = 19.0482787; maxlat = 19.5919189;

des='Parse a raw call file to only extract geolocation data (timestamp, user id and bsid) \
from Mexico (latitude from ' + str(minlat) + ' to ' + str(maxlat) + \
' and longitude from ' + str(minlon) + ' to ' + str(maxlon) + '), generate the user id graph file \
(id yoda and graph id) and the base station file (longitude, latitude and bsid)'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-geo', metavar='geo_file', help='output file for geolocation data (gziped)', required=True)
parser.add_argument('-uid', metavar='user_id_file', help='output file for id yoda graph (gziped)', required=True)
parser.add_argument('-bs', metavar='bsid_file', help='output file for base station graph (gziped)', required=True)
parser.add_argument('-call', metavar='raw_call_file', help='input file with raw call data (gziped)', default=None)
parser.add_argument('-v', action='store_true', help='verbose output')
args = parser.parse_args()


if args.call != None:
    try:
        input_file = gzip.open(args.call, 'r')
    except IOError:
        print('Error: can\'t open file named ' + args.call)
        exit()
else:
    input_file = sys.stdin
    
output_file = gzip.open(args.geo, 'w')
id_user_file = gzip.open(args.uid, 'w')
bs_graph_file = gzip.open(args.bs, 'w')
verbose = args.v

print('Started...')

id_user_list = {}
bs_list = {}
user_id_inc = 1
bsid_inc = 1
total_count = 0
good_count = 0
for line in input_file:
    items = line.rstrip('\r').rstrip('\n').split('\t')
    total_count +=1
    try:
        if(len(items) != 11):
            raise ValueError
        id_yoda = items[1]
        lon = float(items[8])
        lat = float(items[7])
        if lon < minlon or lon > maxlon or lat < minlat or lat > maxlat :
            raise ValueError
        timestamp = time.mktime(time.strptime(items[10].replace('.', ''), '%d/%m/%Y %I:%M:%S %p'))
        good_count +=1
        
        try:
            user_id = id_user_list[id_yoda]
        except KeyError:
            user_id = user_id_inc
            id_user_list[id_yoda] = user_id
            user_id_inc += 1
            id_user_file.write(str(id_yoda) + '\t' + str(user_id) + '\n')
        finally:
            try:
                bsid = bs_list[(lon, lat)]
            except KeyError:
                bsid = bsid_inc
                bs_list[(lon, lat)] = bsid
                bsid_inc += 1
                bs_graph_file.write(str(lon) + '\t' + str(lat) + '\t' + str(bsid) + '\n')
            finally:
                output_file.write(str(int(timestamp)) + '\t' + str(user_id) + '\t' + str(bsid) + '\n')
            
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
output_file.close()
id_user_file.close()
bs_graph_file.close()