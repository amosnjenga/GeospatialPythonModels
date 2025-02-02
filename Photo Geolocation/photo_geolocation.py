#GOAL: use exif tags from photos to create point locations shapefile

#Import libraries
import glob
import os
try:
    import Image
    import ImageDraw
except ImportError:
    from PIL import Image
    from PIL.ExifTags import TAGS
import shapefile

#2) Functions
# function to extract EXIF data
def exif(img):
    #extract exif data
    exif_data = {}
    try:
        i = Image.open(img)
        tags = i._getexif()
        for tag,value in tags.items():
            decoded = TAGS.get(tag,tag)
            exif_data[decoded] = value
    except:
        pass
    return exif_data

# function to convert degrees,minutes,seconds to decimal degrees
def dms2dd(d,m,s,i):
    sec = float((m * 60) + s)
    dec = float(sec / 3600)
    deg = float(d + dec)
    if i.upper() == 'W':
        deg = deg * -1
    elif i.upper() == 'S':
        deg = deg * -1
    return float(deg)

# function to extract GPS data and perfom coordinate conversion
def gps(exif):
    #get gps data from exif
    lat = None
    lon = None
    if exif['GPSInfo']:
        #Lat
        coords = exif['GPSInfo']
        i = coords[1]
        temp_coords = list(coords[2])
        d = temp_coords[0]
        m = temp_coords[1]
        s = temp_coords[2]
        lat = dms2dd(d,m,s,i)
        #Lon
        i = coords[3]
        temp_coords = list(coords[4])
        d = temp_coords[0]
        m = temp_coords[1]
        s = temp_coords[2]
        lon = dms2dd(d, m, s, i)
    return lat,lon

#3) Loop through photos,extract the coordinates,and store the coordninates
#and filenames in a dictionary
photos = {}
photos_dir = './photos'
files = glob.glob(os.path.join(photos_dir,"*.jpg"))
for f in files:
    e = exif(f)
    lat,lon = gps(e)
    photos[f] = [lon,lat]


#4) Save the photo information as a shapefile
with shapefile.Writer("photos",shapefile.POINT) as w:
    w.field("NAME","C",80)
    for f,coords in photos.items():
        w.point(*coords)
        w.record(f)
        
        
    
    
