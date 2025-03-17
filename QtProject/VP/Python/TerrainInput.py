# Read guard text file input
# Input format:
#     Guard K                 <for each guard>
#     ConnectedComponent N    <at least one line>
#     Intersecting I          <at least zero line>
#     ....
#     CrossNorth A            <at least one line>
#     CrossSouth B            <at least one line>
#
from PIL import Image, ImageDraw
import numpy as np

gGuards = []   # Contains the comps
gComps = []    # Contains the comps
gNorths = []   # Contains IDs only
gSouths = []   # Contains IDs only
gCompMask = None

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
    def setBitmap(self, minX, maxX, minZ, maxZ, bitmap):
        self.minX = minX
        self.maxX = maxX
        self.minZ = minZ
        self.maxZ = maxZ
        self.bitmap = bitmap.copy()
        

# -----------------------------
# Guard
# -----------------------------
class classGuard:
    def __init__(self, id):
        self.id = id
        self.comps = []

    def addComp(self, comp):
        self.comps.append(comp)

    def setLocation(self, x, y, h, r):
        self.x = x
        self.y = y
        self.h = h
        self.r = r

# -----------------------------
# Read a text file input to define the guards and 
# connected components and their relationships
# -----------------------------
def readInput(f, verbose):

    guardnum = -1
    compnum = -1
 
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
        print("There is no north-crossing or no south-crossing connected components!")
        return

    printAll(verbose)

    return gGuards, gComps, gNorths, gSouths

# -----------------------------
# Find intersecting components
# -----------------------------
def findIntersections(verbose):
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
    minZ = max(comp1.minZ, comp2.minZ)
    maxZ = min(comp1.maxZ, comp2.maxZ)

    for i in range(minX, maxX+1):
        for j in range(minZ, maxZ+1):
            if comp1.bitmap[i-comp1.minX][j-comp1.minZ] and \
                comp2.bitmap[i-comp2.minX][j-comp2.minZ]:
                return True

    return False

# -----------------------------
# Find the connected components of a single guard based on the viewshed
# -----------------------------
def findConnected(guard, viewshed, verbose):
    global gCompMask

    width, height = viewshed.shape
    gCompMask = viewshed.copy()

    done = False
    while done == False:
        # Find a non-zero pixel to start 
        found = False
        for i in range(width):
            for j in range(height):
                if gCompMask[i][j] == 1:  # Either one or zero
                    #if verbose:
                    #    print(f"Find component start point at {i},{j}")
                    flood_fill((i, j))
                    #debugPrintMask()
                    setConnectedComponent(guard, verbose)
                    found = True
        if found == False:
            done = True

# -----------------------------
# Define a single connected component
# Crop the bitmap to the minimize size needed to store the info
# gCompMask contains the mask for the connected component (visible = 2 after flood fill)
# Other pixels (if visible by the same guard) = 1
# -----------------------------
def setConnectedComponent(guard, verbose):
    global gCompMask

    nrows, ncols = gCompMask.shape

    compnum = len(gComps)
    comp = classComp(compnum, guard.id)
    guard.addComp(comp)
    gComps.append(comp)

    maxX=-100000
    minX=100000
    maxZ=-100000
    minZ=100000

    bitmap = np.zeros((nrows, ncols), dtype=np.uint32)

    for i in range(nrows):
        for j in range(ncols):
            if gCompMask[i][j] == 2:
                minX = min(i, minX)
                maxX = max(i, maxX)
                minZ = min(j, minZ)
                maxZ = max(j, maxZ)
                gCompMask[i][j] = 0  # Clear pixel after processing so we are done with this component, leave other pixels alone
                bitmap[i][j] = 1

    #if verbose:
    #    print(f"Component boundary = {compnum}: {minX}, {maxX}, {minZ}, {maxZ}")

    bitmap = bitmap[minX:maxX+1, minZ:maxZ+1]
    comp.setBitmap(minX, maxX, minZ, maxZ, bitmap)

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
def flood_fill(start):
    global gCompMask

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
# -----------------------------
def printGuards(verbose):
    if verbose:
        print("----------Guard/Region Info----------")
        for i in range(len(gGuards)):
            guard = gGuards[i]
            print(f"Guard {guard.id} at ({guard.x}, {guard.y})")
            for j in range(len(guard.comps)):
                comp = guard.comps[j]
                print(f"Component {comp.id}: {comp.minX}, {comp.maxX}, {comp.minZ}, {comp.maxZ}")
                print(f"Intersections: {comp.intersects}")
        print("gNorths:")
        print(gNorths)
        print("gSouths:")
        print(gSouths)
# -----------------------------
# Print gCompMask
# -----------------------------
def debugPrintMask():
    global gCompMask

    width, height = gCompMask.shape
    for i in range(width):
        s = ""
        for j in range(height):
            s = s + "," + str(gCompMask[i][j])
        print(s)