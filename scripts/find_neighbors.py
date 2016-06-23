import math
from scipy.spatial import Delaunay, Voronoi, ConvexHull
from matplotlib import path
from matplotlib.transforms import Affine2D
import argparse
import gzip
import numpy as np

def dist(a,b):
    """Return the distance between a and b"""
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def checkCoupleInList(coupleList, couple):
    """Return True if couple or its inverse is in coupleList, otherwise False"""
    revCouple = couple[:]
    revCouple.reverse()
    return couple in coupleList or revCouple in coupleList

def addCoupleToList(coupleList, couple):
    """Add couple to coupleList if the couple or its inverse is not in coupleList"""
    if(checkCoupleInList(coupleList, couple) == False):
        coupleList.append(couple)

def getCircumCircleCenter(triangle):
    """Return the center of the circumcircle of triangle"""
    return Voronoi(triangle).vertices[0]

def expandPath(path, scale):
    """Expand path with scale and return it"""
    transform = Affine2D()
    transform.scale(scale)
    ex_extents_points = path.get_extents().get_points()
    ex_middle_points = [(ex_extents_points[0,0] + ex_extents_points[1,0])/2., (ex_extents_points[0,1] + ex_extents_points[1,1])/2.]
    
    new_extents_points = path.transformed(transform).get_extents().get_points()
    new_middle_points = [(new_extents_points[0,0] + new_extents_points[1,0])/2., (new_extents_points[0,1] + new_extents_points[1,1])/2.]
    
    transform.translate(ex_middle_points[0]-new_middle_points[0], ex_middle_points[1]-new_middle_points[1])
    return path.transformed(transform)

def getDelaunayEdges(points):
    """Return the list of edges between points without fake neighbors"""
    delau = Delaunay(points)
    hull = ConvexHull(points)
    hull = path.Path(points[hull.vertices])
    hull = expandPath(hull,1.2)
    allEdges = list()
    badEdges = list()
    for simplex in [x.tolist() for x in delau.simplices]:
        for edge in [[x, simplex[simplex.index(x)-1]] for x in simplex]:
                addCoupleToList(allEdges, edge)
        circumCircleCenter = getCircumCircleCenter(points[simplex])
        if(hull.contains_point(circumCircleCenter) == False):
            simplexPoints = points[simplex]
            edge0 = dist(simplexPoints[0], simplexPoints[1])
            edge1 = dist(simplexPoints[1], simplexPoints[2])
            edge2 = dist(simplexPoints[2], simplexPoints[0])
            largestEdge = max(edge0, edge1, edge2)
            if(edge0 == largestEdge):
                addCoupleToList(badEdges, [simplex[0], simplex[1]])
            elif(edge1 == largestEdge):
                addCoupleToList(badEdges, [simplex[1], simplex[2]])
            elif(edge2 == largestEdge):
                addCoupleToList(badEdges, [simplex[2], simplex[0]])
    
    return [x for x in allEdges if checkCoupleInList(badEdges, x) ==  False]

def getNeighbors(edges):
    """Return dictionary of list of neighbors, keys are points ids"""
    neighbors = dict()
    for edge in edges:
        try:
            neiList = neighbors[edge[0]]
            neiList.append(edge[1])
        except KeyError:
            neighbors[edge[0]] = [edge[1]]
        try:
            neiList = neighbors[edge[1]]
            neiList.append(edge[0])
        except KeyError:
            neighbors[edge[1]] = [edge[0]]
    
    return neighbors

des='Parse a bsid file to find neighbors and write it to a file'

parser = argparse.ArgumentParser(description=des)
parser.add_argument('-bsnei', metavar='bs_neighbors_file', help='output file for bs neighbors (gziped)', required=True)
parser.add_argument('-bsid', metavar='bsid_file', help='input file with bsid data (gziped)', required=True)
args = parser.parse_args()

try:
    bsid_file = gzip.open(args.bsid, 'r')
except IOError:
    print('Error: can\'t open file named ' + args.bsid)
    exit()
    
output_file = gzip.open(args.bsnei, 'w')

points = []

for line in bsid_file:
    items = line.rstrip('\r').rstrip('\n').split('\t')
    lon = float(items[0])
    lat = float(items[1])
    #bsid = int(items[2])
    #TODO: avec dict
    points.append((lon, lat))

neighbors = getDelaunayEdges(np.array(points))
for bsid in neighbors:
    output_file.write(str(bsid[0]+1) + "\t" + str(bsid[1]+1) + "\n")


bsid_file.close()
output_file.close()