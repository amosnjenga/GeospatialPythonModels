#Import libraries
import numpy as np
import math,shapefile
from linecache import getline
import pickle
from osgeo import gdal

#1) Define input and output data sources
#Source Terrain data
source = "./data/dem.asc"

asc = gdal.Open(source)
gt = asc.GetGeoTransform()
print(gt)

#output filename for the path raster
target = "./data/path.asc"

#2) Load the grid skipping over the head
print("Opening %s..." % source)
cost = np.loadtxt(source,skiprows=6)
print("Opened %s." % source)

#3)Parse the header for geospatial and grid size info
hdr = [getline(source,i) for i in range(1,7)]
values = [float(ln.split(" ")[-1].strip()) for ln in hdr]
print(values)
cols,rows,lx,ly,cell,nd = values

#4) Define starting and end locations
#Starting column,row
sx = 1006
sy = 954

#Ending column,row
dx = 303
dy = 109

#5) Functions
#Euclidean distance btn points
def e_dist(p1,p2):
    """ Takes two points and returns the Euclidean distance"""
    x1,y1 = p1
    x2,y2 = p2
    distance =  math.sqrt((x1-x2)**2+(y1-y2)**2)
    return int(distance)

#Weight function to score each node for suitability to move
def weighted_score(cur,node,h,start,end):
    """
    Provides a weighted score by comparing the current node
    with a neighbouring node.Loosely based on the Nisson Score
    concept: f = g + h. In this case, the "h" value,or "heuristic",
    is the elevation value for each node.
    """
    #1) Start with score 0 and check node's distance from the end to start
    score = 0
    # current node elevation
    cur_h = h[cur]
    # current node distance from end
    cur_g = e_dist(cur,end)
    # current node distance from start
    cur_d = e_dist(cur,start)

    #2) Examine neighbouring nodes to make decision where to move
    #neighbour node elevation
    node_h = h[node]
    #neighbour node distance from end
    node_g = e_dist(node,end)
    #neighbour node from the start
    node_d = e_dist(node,start)

    #Compare values with the highest weight given to terrain followed
    #by progress towards the goal
    if node_h < cur_h:
        score += cur_h - node_h
    if node_g < cur_g:
        score += 10
    if node_d > cur_d:
        score += 10
    return score

#A* function
def astar(start,end,h):
    """
    A-Star search algorithm.
    Moves through nodes in a network (or grid), scores each node's
    neighours, and goes to the node with the best score until it finds the end
    """
    # Closed set of nodes to avoid
    closed_set = set()
    #Open set of nodes to evaluate
    open_set = set()
    #Output set of path nodes
    path = set()

    #Add the starting point to begin processing
    open_set.add(start)
    while open_set:
        #Grab the next node
        cur = open_set.pop()
        #Return if we're at the end
        if cur == end:
            return path
        #Close off this node to future processing
        closed_set.add(cur)
        #The current node is always a path node by definition
        path.add(cur)

        #List to hold neigbouring nodes for processing
        options = []
        #Grab all of the neigbours
        y1 = cur[0]
        x1 = cur[1]
        if y1 > 0:
            options.append((y1-1,x1))
        if y1 < h.shape[0]-1:
            options.append((y1+1,x1))
        if x1 > 0:
            options.append((y1,x1-1))
        if x1 < h.shape[1]-1:
            options.append((y1,x1+1))
        if x1 > 0 and y1 > 0 :
            options.append((y1-1,x1-1))
        if y1 < h.shape[0]-1 and x1 < h.shape[1]-1:
            options.append((y1+1,x1+1))
        if y1 < h.shape[0]-1 and x1 > 0:
            options.append((y1+1,x1-1))
        if y1 > 0 and x1 < h.shape[1]-1:
            options.append((y1-1,x1+1))

        #if the end is a neighbour,return
        if end in options:
            return path

        #Store the best known node
        best = options[0]
        #Begin scoring neighbours
        best_score = weighted_score(cur,best,h,start,end)

        #process the other  neighbours
        for i in range(1,len(options)):
            option = options[i]

        #Make sure the node is new
            if option in closed_set:
                continue
            else:
                #Score the option and compare it to the best known
                option_score = weighted_score(cur,option,h,start,end)
                if option_score > best_score:
                    best = option
                    best_score = option_score
                else:
                    #If node isn't better seal it off
                    closed_set.add(option)
                    #print(best,e_dist(best,end)) # Uncomment this to watch the path develop in real time
        open_set.add(best)
    return []

#Function to convert pixel to lat lon
def pix2coord(gt,x,y):
    gt = list(gt)
    x_min = gt[0]
    x_size = gt[1]
    y_min = gt[3]
    y_size = gt[5]

    cx = x * x_size + x_min  # x pixel
    cy = y * y_size + y_min  # y pixel
    return cx, cy

###Generating path
print("Searching for path...")
p = astar((sy,sx),(dy,dx),cost)
print(p)
print("Path found.")
print("Creating path grid...")

#pixel to coordinates
coords = []

#creating path image
path = np.zeros(cost.shape)
print("Plotting path...")

for y,x in p:
    path[y][x] = 1
    print(y,x)
    coords.append(pix2coord(gt,x,y))
path[dy][dx] = 1
print("Path plotted.")

#Coordinates for shapefile
print(coords)
starting_point = pix2coord(gt,sx,sy)
starting_point = list(starting_point)
s = sorted(coords, key = lambda a: (a[0], a[1]))
#print(s)




#Save path as an ASCII Grid
print("Saving %s..." % target)
header = ""
for i in range(6):
    header += hdr[i]

# Open the output file, add the hdr, save the array
with open(target, "wb") as f:
    f.write(bytes(header, 'UTF-8'))
    np.savetxt(f, path, fmt="%4i")

#Save data as a pickle python object for creating vector shapefile
print("Saving path data...")
with open("path.p", "wb") as pathFile:
    pickle.dump(p, pathFile)
print("Done!")


#Write data to shapefile
with shapefile.Writer("path", shapeType=shapefile.POLYLINE) as w:
    w.field("NAME")
    w.record("LeastCostPath")
    w.line([[list(p) for p in s]])
    w.close()



