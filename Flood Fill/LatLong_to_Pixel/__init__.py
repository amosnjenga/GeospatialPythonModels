import gdal
from osgeo import gdal
from osgeo import gdal_array
from osgeo import ogr

class LatLong_to_Pixels:
    def __init__(self,path,long,lat):
        self.source = path
        self.long = long
        self.lat = lat

        #load image as a gdal image to get geotransform info
        self.srcImage = gdal.Open(self.source)
        self.geoTrans = self.srcImage.GetGeoTransform()
        self.geoMatrix = self.geoTrans

    def world2Pixel(self):
        """Uses a gdal geoMatrix (gdal.GetGeotransform())
        to calculate the pixel location of a geospatial coordinate."""
        ulX = self.geoMatrix[0]
        ulY = self.geoMatrix[3]
        xDist = self.geoMatrix[1]
        yDist = self.geoMatrix[5]
        rtnX = self.geoMatrix[2]
        rtnY = self.geoMatrix[4]
        pixel = int((self.long - ulX) / xDist)
        line = int((ulY - self.lat) / abs(yDist))
        return (pixel, line)

x,y = LatLong_to_Pixels("F:/Python Projects/GeospatialPythonModels/Flood Fill/data/nakuru_terrain.tif",36.116864,-0.327858).world2Pixel()
print(x,y)