#Libraries
import gdal
from osgeo import gdal
from osgeo import gdal_array
from osgeo import gdalnumeric
from osgeo import ogr
try:
    from PIL import Image
    from PIL import ImageDraw
except ImportError:
    from PIL import Image,ImageDraw


##Functions

def imageToArray(i):
    """ COnverts a PIL array to a gdal_array_image."""
    a = gdal_array.numpy.fromstring(i.tobytes(),'b')
    a.shape = i.im.size[1],i.im.size[0]
    return a

def world2Pixel(geoMatrix,x,y):
    """Uses a gdal geoMatrix (gdal.GetGeotransform())
    to calculate the pixel location of a geospatial coordinate."""
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = int((x-ulX)/xDist)
    line = int((ulY-y)/abs(yDist))
    return (pixel,line)

def copy_geo(array,prototype=None,xoffset=0,yoffset=0):
    """Copy geo metadata from image.Copy geotransform from
    prototype dataset to array but account for x,y offset
    of clipped array."""
    ds = gdal_array.OpenArray(array)
    prototype = gdal.Open(prototype)
    gdal_array.CopyDatasetInfo(prototype,ds,xoff=xoffset,yoff=yoffset)
    return ds

#1) Loading the data
    #Multispectral image used to create the NDVI
    #have red and infrared bands

#input band
source = "./data/farm.tif"

#output geotiff file name
target = "ndvi.tiff"

#Load the source data as a gdal_array array
srcArray = gdal_array.LoadFile(source)

#Also load as a gdal image to get geotransform info
srcImage = gdal.Open(source)
geoTrans = srcImage.GetGeoTransform()

#Red and NIR bands
r = srcArray[1]
ir = srcArray[2]


#2) LOADING AND RASTERIZING THE SHAPEFILE
#clip a field out of the bands using a field boundary shapefile

#create an OGR layer from a field boundary shapefile
field = ogr.Open("./data/field.shp")
#must define a 'layer' to keep OGR happy
lyr = field.GetLayer('field')

#Only one polygon in this shapefile
poly = lyr.GetNextFeature()

#Convert the layer extent to image pixel coordinates
minX,maxX,minY,maxY = lyr.GetExtent()
ulX,ulY = world2Pixel(geoTrans,minX,maxY)
lrX,lrY = world2Pixel(geoTrans,maxX,minY)

#Calculate the pixel size of the new image
pxWidth = int(lrX-ulX)
pxHeight = int(lrY-ulY)

#Create a blank image of the correct size that will serve as the mask
clipped = gdal_array.numpy.zeros((3,pxHeight,pxWidth),gdal_array.numpy.uint8)

#Clip the red and infrared to new bands
rClip = r[ulY:lrY,ulX:lrX]
irClip = ir[ulY:lrY,ulX:lrX]

#Create a new geomatrix for the image: create georeferencing info
geoTrans = list(geoTrans)
geoTrans[0] = minX
geoTrans[3] = maxY

#Map points to pixels for drawig the field boundary on a blank
#8-bit,b&w,mask image
points = []
pixels = []

#Grab the polygon geometry
geom = poly.GetGeometryRef()
pts = geom.GetGeometryRef(0)

#Loop through geometry and turn the points into and
#easy to manage Python list : loop thru points and get their x,y
for p in range(pts.GetPointCount()):
    points.append((pts.GetX(p),pts.GetY(p)))

#Loop through points and convert them to pixels
#Append the pixels to pixel list
for p in points:
    pixels.append(world2Pixel(geoTrans,p[0],p[1]))

#Create mask image as a b&w 'L' mode and filled as white.White =2
rasterPoly = Image.new("L",(pxWidth,pxHeight),1)

#Rasterize polygon
#Create a PIL drwaing object
rasterize = ImageDraw.Draw(rasterPoly)

#Dump the pixels to the image as a polygon.Black = 0
rasterize.polygon(pixels,0)

#convert mask to a numpy array
mask = imageToArray(rasterPoly)


#3)CLIPPING THE BANDS
#clip the red band using the mask
rClip = gdal_array.numpy.choose(mask,(rClip,0)).astype(gdal_array.numpy.uint8)

#clip the nir band using the mask
irClip = gdal_array.numpy.choose(mask,(irClip,0)).astype(gdal_array.numpy.uint8)


#NDVI CALCULATION PART
#Ignore numpy warnings due to NaN values from clipping
gdal_array.numpy.seterr(all="ignore")

#NDVI equation: (NIR-Red)/(NIR+Red)
#*1.0 converts values to floats
#+1.0 prevents ZeroDivisionErrors
ndvi = 1.0 * (irClip - rClip) / irClip + rClip + 1.0

#Convert any NaN values to zero
ndvi = gdal_array.numpy.nan_to_num(ndvi)

#Save ndvi as a GeoTiff and copy/adjust the georeferencing info
#gtiff = gdal.GetDriverByName('GTiff')
#gtiff.CreateCopy(target,copy_geo(ndvi,prototype=source,xoffset = ulX,yoffset=ulY))
#gtiff = None
    

# Save ndvi as tiff
gdalnumeric.SaveArray(ndvi, target,format="GTiff", prototype=srcImage)

# Update georeferencing and NoData value
update = gdal.Open(target, 1)
update.SetGeoTransform(list(geoTrans))
update.GetRasterBand(1).SetNoDataValue(0.0)
update = None

    
