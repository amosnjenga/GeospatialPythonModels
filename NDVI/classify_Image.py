import gdal_array as gd
import operator
from functools import reduce

#Histogram
def histogram(a,bins=list(range(256))):
    """Histogram function for multi-dimensional array.
    a = array
    bins = rang of numbers to match
    """
    #Flatten,Sort,then split our arrays for the histogram
    fa = a.flat
    n = gd.numpy.searchsorted(gd.numpy.sort(fa),bins)
    n = gd.numpy.concatenate([n,[len(fa)]])
    hist = n[1:]-n[:-1]
    return hist

#Function to perform histogram stretch
def stretch(a):
    """Performs a histogram stretch on a gdal_array array image."""
    hist = histogram(a)
    lut = []
    for b in range(0,len(hist),256):
        #step size - create equal interval bins
        step = reduce(operator.add,hist[b:b+256])/255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n/step)
            n = n + hist[i+b]
            gd.numpy.take(lut,a,out=a)
            return a

#LOADING THE NDVI
#NDVI output from the ndvi script
source = "ndvi.tif"

#Target file name for classified image
target = "ndvi_color.tif"

#Load the image into an array
ndvi = gd.LoadFile(source).astype(gd.numpy.uint8)

#HISTOGRAM STRETCH
#Perform stretch to be alble to use all the classes
ndvi = stretch(ndvi)

#Create a blank 3-band image the same size as the ndvi
rgb = gd.numpy.zeros((3,len(ndvi),len(ndvi[0])),gd.numpy.uint8)

#CREATING CLASSES

#Class list with ndvi upper range values
#Note the lower and upper values are listed on the ends
classes = [58,73,110,147,184,220,225]

#Color look-up table(lut).The lut mustmatch the number of classes
#Specified as R,G,B tuples from dark brown to dark green
lut = [[120, 69, 25], [255, 178, 74], [255, 237, 166], [173, 232, 94],
 [135, 181, 64], [3, 156, 0], [1, 100, 0]]

#Starting value of the first class
start = 1

##CLASSIFY IMAGE
#For each class value range,grab values within range
#,then filter values through the mask.
mask = gd.numpy.logical_and(start<= ndvi,ndvi<=classes[i])
for j in range(len(lut[i])):
    rgb[j] = gd.numpy.choose(mask,(rgb[j],lut[i],j))
    start = classes[i] + 1

#Save a geotiff image of the colored ndvi
    output = gd.SaveArray(rgb,target,format="GTiff",prototype=source)
    output = None


    


