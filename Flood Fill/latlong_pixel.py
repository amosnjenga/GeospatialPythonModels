import gdal
from osgeo import gdal
from osgeo import gdal_array
from osgeo import ogr

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

#input band
source = "F:/Python Projects/GeospatialPythonModels/Flood Fill/data/Garrisa.tif"


#Also load as a gdal image to get geotransform info
srcImage = gdal.Open(source)
geoTrans = srcImage.GetGeoTransform()

x,y = world2Pixel(geoTrans,39.633039,-0.461247)

print(x,y)