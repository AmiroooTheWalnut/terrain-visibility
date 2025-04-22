# Read guard text file input
# Input format:
#     Guard K                 <for each guard>
#     ConnectedComponent N    <at least one line>
#     Intersecting I          <at least zero line>
#     ....
#     CrossNorth A            <at least one line>
#     CrossSouth B            <at least one line>
#
import numpy as np
import gc

# -----------------------------
# Connected Component
# -----------------------------
class classComp:
    def __init__(self, id, parentID):
        self.id = id
        self.parentID = parentID
        self.intersects = []

    def addIntersect(self, id):
        self.intersects.append(id)

    # For Geogebra export
    def setLocation(self, cx, cy, radius):
        self.cx = cx
        self.cy = cy
        self.radius = radius

    # Store bitmap of the Connected Component
    # bitmap is a numpy array ((nrows, ncols), dtype=np.uint32), cutout of the original bitmap
    # Y is Z in the appVP
    def setBitmap(self, minX, maxX, minY, maxY, bitmap):
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY
        self.bitmap = bitmap.copy()

    def clear(self):
        del self.intersects
        self.bitmap = None
        gc.collect()

# -----------------------------
# Guard
# -----------------------------
class classGuard:
    def __init__(self, id):
        self.id = id
        self.compIDs = []
        self.paired = False

    def addComp(self, comp):
        self.compIDs.append(comp.id)

    def setLocation(self, x, y, h, r):
        self.x = int(x)
        self.y = int(y)
        self.h = int(h)
        self.r = int(r)

    def clear(self):
        del self.compIDs
        self.paired = False

# -----------------------------
# Read a text file input to define the guards and 
# connected components and their relationships
# -----------------------------
def readInput(f, verbose=False):

    guardnum = -1
    compnum = -1

    gGuards = []
    gComps = []
    gNorths = []
    gSouths = []
 
    # Read input file and build the connectedness map
    for l in f.readlines():
        typeStr, numStr = l.split()
        num = int(numStr)

        if typeStr == "Guard":
            guardnum = num
            guard = classGuard(guardnum)
            gGuards.append(guard)
        elif typeStr == "ConnectedComponent":
            compnum = num
            comp = classComp(compnum, guardnum)
            gGuards[guardnum].addComp(comp)
            gComps.append(comp)
        elif typeStr == "Intersecting":
            gComps[compnum].addIntersect(num)
        elif typeStr == "CrossNorth":
            gNorths.append(num)
        elif typeStr == "CrossSouth":
            gSouths.append(num)
        else:
            raise Exception("Uncognized type!")

    if len(gNorths) == 0 or len(gSouths) == 0:
        print("There is no north-crossing or no south-crossing connected components!", flush=True)
        return

    return gGuards, gComps, gNorths, gSouths

# -----------------------------
# Find intersecting components
# -----------------------------
def findIntersections(gComps, verbose=False):
    for i in range(len(gComps)):
        for j in range(i+1, len(gComps)):
            if intersect(gComps[i], gComps[j]):
                gComps[i].addIntersect(j)
                gComps[j].addIntersect(i)

# -----------------------------
# Determine if two Components intersect
# -----------------------------
def intersect(comp1, comp2):
    minX = max(comp1.minX, comp2.minX)  
    maxX = min(comp1.maxX, comp2.maxX)
    minY = max(comp1.minY, comp2.minY)
    maxY = min(comp1.maxY, comp2.maxY)

    for i in range(minX, maxX+1):
        for j in range(minY, maxY+1):
            if comp1.bitmap[i-comp1.minX][j-comp1.minY] and \
                comp2.bitmap[i-comp2.minX][j-comp2.minY]:
                return True

    return False

# -----------------------------
# Find the connected components of a single guard based on the viewshed
# -----------------------------
def findConnected(guard, viewshed, gComps, gNorths, gSouths, verbose=False):

    width, height = viewshed.shape
    gCompMask = viewshed.copy()  # Perform deep copy

    done = False
    while done == False:
        # Find a non-zero pixel to start 
        found = False
        for i in range(width):
            for j in range(height):
                if gCompMask[i][j] == 1:  # Either one or zero
                    #if verbose:
                    #    print(f"Find component start point at {i},{j}")
                    flood_fill((i, j), gCompMask) # Fill all the connected points and set the pixels to 2
                    #debugPrintMask(gCompMask)
                    setConnectedComponent(guard, gCompMask, gComps, gNorths, gSouths, verbose)
                    found = True
        if found == False:
            done = True

# -----------------------------
# Define a single connected component
# Crop the bitmap to the minimize size needed to store the info
# gCompMask contains the mask for the connected component (visible = 2 after flood fill)
# Other pixels (if visible by the same guard) = 1
# -----------------------------
def setConnectedComponent(guard, gCompMask, gComps, gNorths, gSouths, verbose=False):

    nrows, ncols = gCompMask.shape

    compnum = len(gComps)
    comp = classComp(compnum, guard.id)
    guard.addComp(comp)
    gComps.append(comp)

    maxX=-100000
    minX=100000
    maxY=-100000
    minY=100000

    bitmap = np.zeros((nrows, ncols), dtype=np.uint32)

    for i in range(nrows):
        for j in range(ncols):
            if gCompMask[i][j] == 2:
                minX = min(i, minX)
                maxX = max(i, maxX)
                minY = min(j, minY)
                maxY = max(j, maxY)
                gCompMask[i][j] = 0  # Clear pixel after processing so we are done with this component, leave other pixels alone
                bitmap[i][j] = 1

    #if verbose:
    #    print(f"Component boundary = {compnum}: {minX}, {maxX}, {minY}, {maxY}")

    # bitmap is a cutout of the original bitmap
    bitmap = bitmap[minX:maxX+1, minY:maxY+1]
    comp.setBitmap(minX, maxX, minY, maxY, bitmap)

    # Potentially add to gNorth or gSouth
    # In the appVP, this is done during construction of first frontier
    # In this solution, we predetermine the components that overlaps with N/S
    if minX == 0:
        gNorths.append(compnum)
    if maxX == nrows-1:
        gSouths.append(compnum)

# -----------------------------
# Flood fill a 2D array
# -----------------------------
def flood_fill(start, gCompMask):

    width, height = gCompMask.shape

    stack = []
    stack.append((start))
        
    while len(stack) > 0:
        x, y = stack.pop(0)
        
        # Skip if out of bounds
        if x < 0 or x >= width or y < 0 or y >= height or gCompMask[x][y] != 1:
            continue
        
        # Fill the current pixel with the fill value
        gCompMask[x][y] = 2
        
        # Add the 4 neighboring cells to the stack (up, down, left, right)
        stack.append((x + 1, y))  # Right
        stack.append((x - 1, y))  # Left
        stack.append((x, y + 1))  # Down
        stack.append((x, y - 1))  # Up
        
# -----------------------------
# Print Guard information
# A section will be the same format as the input file for the algorithms
# -----------------------------
def printGuards(gGuards, gComps, gNorths, gSouths, verbose=False):
    if verbose:        
        print("----------Guard/Component Locations----------")
        for guard in gGuards:
            print(f"Guard {guard.id} at ({guard.x}, {guard.y})")
            for id in guard.compIDs:
                comp = gComps[id]
                print(f"Component {id}: {comp.minX}, {comp.maxX}, {comp.minY}, {comp.maxY}")

        print("-----------Input File Format----------")
        for guard in gGuards:
            print(f"Guard {guard.id}")
            for id in guard.compIDs:
                print(f"ConnectedComponent {id}")
                comp = gComps[id]
                for k in comp.intersects:
                    print(f"Intersecting {k}")
        for id in gNorths:
            print(f"CrossNorth {id}")
        for id in gSouths:
            print(f"CrossSouth {id}")
        
# -----------------------------
# Print gCompMask
# -----------------------------
def debugPrintMask(gCompMask):

    width, height = gCompMask.shape
    for i in range(width):
        s = ""
        for j in range(height):
            s = s + "," + str(gCompMask[i][j])
        print(s)


    
