import numpy as np

#Width and the Height of grids
w = 5
h = 5

#Starting and eding locations cells
#Start location - lower left of the grid
start = (h-1,0)

#End location - Top right of grid
dx = w-1
dy = 0

#Create blank grid of zeros based on width and height
blank = np.zeros((w,h))

#Set up distance grid to create  impedance values
#Distance grid
dist = np.zeros(blank.shape,dtype=np.int8)

#Calculate distance for all cells
for y,x in np.ndindex(blank.shape):
    dist[y][x] = abs((dx-x)+(dy-y))

#Print cost value for each cell in the cost grid
#"Terrain" is the random value between 1-16
    #Add terrain to the distance grid to calculate the cost of moving to a cell

cost = np.random.randint(1,16,(w,h)) + dist

print("COST GRID ( Elev Value + Distance)\n{}\n".format(cost))

#A* search algorithm
def astar(start,end,h,g):
    #sets to keep track of the path progress
    closed_set = set()
    open_set = set()
    path = set()

    #Add starting cell to open list of cells and in order to
    #process & begin looping through that set
    open_set.add(start)
    while open_set:
        cur = open_set.pop()
        if cur == end:
            return path
        closed_set.add(cur)
        path.add(cur)
        options = []
        y1 = cur[0]
        x1 = cur[1]

        #Check sorounding cells as options for forward progress
        if y1 > 0:
            options.append((y1-1,x1))
        if y1 < h.shape[0]-1:
            options.append((y1+1,x1))
        if x1 > 0:
            options.append((y1,x1-1))
        if x1 < h.shape[1]-1:
            options.append((y1,x1+1))
        if end in options:
            return path
        best = options[0]
        closed_set.add(options[0])

        #Check each option for the best option and append to path until
        #we reach the end
        for i in range(1,len(options)):
            option = options[i]
            if option in closed_set:
                continue
            elif h[option] <= h[best]:
                best = option
                closed_set.add(option)
            elif g[option] < g[best]:
                best = option
                closed_set.add(option)
            else:
                closed_set.add(option)
        print(best,", ",h[best], ", ",g[best])
        open_set.add(best)
    return []

#Ind the path
path = astar(start,(dy,dx),cost,dist)
print(path)

#create path grid
path_grid = np.zeros(cost.shape,dtype=np.uint8)
for y,x in path:
    path_grid[y][x]=1
    path_grid[dy,dx] = 1

print("PATH GRID: 1=PATH")
print(path_grid)
    
