#Import libraries
import pickle
from linecache import getline
import shapefile

#function to convert rows and columns to x,y coordinates

def pix2coord(gt,x,y):
    ox = gt[2]
    oy = gt[3]
    pw = gt[4]
    ph = gt[4]
    cx = ox + pw * x + (pw/2)
    cy = oy + pw * y + (ph/2)
    return cx, cy

#Restore the path object from the pickled object
with open("path.p", "rb") as pathFile:
    path = pickle.load(pathFile)
    #Parse the metadata info
    hdr = [getline("./data/path.asc", i) for i in range(1, 7)]
    gt = [float(ln.split(" ")[-1].strip()) for ln in hdr]
    #print(gt)

    #list of converted coordinates
    coords = []
    #Convert raster cell location to geospatial coordinate
    for y,x in path:
        #print(y,x)
        #latlon = pix2coord(gt,x,y)
        #print(latlon)
        coords.append(pix2coord(gt,x,y))
#print(coords)


#Write data to shapefile
with shapefile.Writer("path", shapeType=shapefile.POLYLINE) as w:
    w.field("NAME")
    w.record("LeastCostPath")
    w.line([[list(p) for p in coords]])
    w.close()
