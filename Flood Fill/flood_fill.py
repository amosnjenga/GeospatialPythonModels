#import libraries
import numpy as np
from linecache import getline

#Flood Fill Function
def floodFill(c,r,mask):
    """Crawls a mask array containing only 1 and 0 values from the
    starting point (c=clomn,r=row - aka x,y) and returns an
    array with all 1 values connected to the starting cell
    """
    #1) Create Sets
    #set for cells already filled
    filled = set()
    #set for cells to fill
    fill = set()
    fill.add((c,r))
    width = mask.shape[1]-1
    height = mask.shape[0]-1

    #2) Output inundation array
    flood = np.zeros_like(mask,dtype=np.int8)

    #3) Loop through the cells and flood them,or not:modify cells which need to be checked
    while fill:
        #Grab a cell
        x,y = fill.pop()
        #if higher than the flood water,skip it
        if y == height or x == width or x < 0 or y < 0:
            #Dont fill
            continue
        if mask[y][x] == 1:
            #Do fill
            flood[y][x] = 1
        filled.add((x,y))

        #Check neighbours for 1 values
        west = (x-1,y)
        east = (x+1,y)
        north = (x,y-1)
        south = (x,y+1)
        if west not in filled:
            fill.add(west)
        if east not in filled:
            fill.add(east)
        if north not in filled:
            fill.add(north)
        if south not in filled:
            fill.add(south)
    return flood

#1) Load the source and target data names
#source = "F:/Python Projects/GeospatialPythonModels/Flood Fill/data/terrain.asc"
source = "F:/Python Projects/GeospatialPythonModels/Flood Fill/data/nakuru.asc"

#target = "flood.asc"
target = "nakuru_flood.asc"

#Open the source
print("Opening the image...")
img = np.loadtxt(source,skiprows=6)
print("Image opened")

#2) Create a mask array of everything below 70 meters(Flood Elevation Value)
wet = np.where(img<1800,1,0)
print("Image masked")

#3) Parse the header using a loop and the built in linecahe module
hdr = [getline(source,i) for i in range(1,7)]
values = [float(h.split(" ")[-1].strip()) for h in hdr]
cols,rows,lx,ly,cell,nd = values
xres = cell
yres = cell * -1

#4) Define starting point for the flood inundation in pixel coordinates
sx = 421
sy = 499

#5) Trigger flooFill function
print("Beginning flood fill")
fld = floodFill(sx,sy,wet)
print("Finished flood fill")

header = ""
for i in range(6):
    header += hdr[i]

#6) Save flood inundation model output
print("Saving Output")
#Open the output file,add hdr ,save the array
with open(target,"wb") as f:
    f.write(bytes(header,'utf-8'))
    np.savetxt(f,fld,fmt="%li")
print("Done!")


#Next steps:
#1) save as tiff,jpg
#2) use GDAL to polgonize the flood layer

        
            
    
