#GOAL: Create colorized DEM and Hillshade,then use PIL to blend them
#for an enhanced elevation visualization

import gdal_array as gd
try:
    import Image
except ImportError:
    from PIL import Image


#1)Set up variables for the inputs and outputs
relief = "relief.asc"
dem = "./data/nakuru.asc"
target = "hillshade.tif"

#2) Load the relief as the background image
bg = gd.numpy.loadtxt(relief,skiprows=6)

#3) load the DEM into a numpy array as the foreground image
fg = gd.numpy.loadtxt(dem,skiprows=6)[:-2,:-2]

#4) Create new image to colorize dem
#Create a blank 3-band image to colorize the DEM
rgb = gd.numpy.zeros((3,len(fg),len(fg[0])),gd.numpy.uint8)

# Class list with DEM upper elevations range values.
classes = [356,649,942,1235,1528,1821,2114,2300,2700]

# Color look-up table LUT
#The lut must match the number of classes
#Specified as R,G,B tuples
lut = [[63, 159, 152], [96, 235, 155], [100, 246, 174],
 [248, 251, 155], [246, 190, 39], [242, 155, 39],
 [165, 84, 26], [236, 119, 83], [203, 203, 203]]

#Starting elevation value of the first class
start = 1

#5) perform color classification
#Process all classes
for i in range(len(classes)):
    mask = gd.numpy.logical_and(start<= fg,fg<=classes[i])
    for j in range(len(lut[i])):
        rgb[j] = gd.numpy.choose(mask,(rgb[j],lut[i][j]))
        start = classes[i] + 1

#6) Convert shaded relief,colorized DEM to images
#convert the shaded relief to a PIL image
im1 = Image.fromarray(bg).convert('RGB')

#convert the Colorized DEM to a PIL image
#We nust transpose it from the Numpy row,col order
#to the PIL col,row order(width,height)
im2 = Image.fromarray(rgb.transpose(1,2,0)).convert('RGB')

#7) Blend the two images and save
#Blend the two images with a 40% alpha
hillshade = Image.blend(im1,im2,.4)

#Save the hillshade
hillshade.save(target)

#
