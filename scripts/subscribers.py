import math
import sys
import argparse
import datetime
import time

def distance(input,  output):
    call_in= [[0 for i in range(0,24)] for j in range(0,366)]
    call_out = [[0 for i in range(0,24)] for j in range(0,366)]
    start = 1388530800

    for line in input:
        item = line.replace('\n','').split('\t')
        outcome=int(item[4])
        timer = int(item[1])
        d = int((timer-1388530800)/(24*3600))
        h = int((timer-1388530800-3600*24*d)/3600)
        if (d<366 and h<24 and item[0]!="" and d>=0 and h>=0):
            if (outcome==1):
                call_in[d][h]=call_in[d][h]+1
            else:
                call_out[d][h]=call_out[d][h]+1
    
    for i in range(0,366):
        for j in range(0,24):
            output.write(str(i)+"\t"+str(j)+"\t"+str(call_in[i][j])+"\t"+str(call_out[i][j])+"\t"+str(call_in[i][j]+call_out[i][j])+"\n")
    
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="input file name")
    parser.add_argument("-o", "--output",
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help="output")
    args = parser.parse_args()
    ids_dumped = distance(args.input,args.output)
    
    args.input.close()
    args.output.close()

if __name__ == "__main__":
    main()
