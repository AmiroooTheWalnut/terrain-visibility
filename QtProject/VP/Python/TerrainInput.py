# Read guard text file input
# Input format:
#     Guard K                 <for each guard>
#     ConnectedComponent N    <at least one line>
#     Intersecting I          <at least zero line>
#     ....
#     CrossNorth A            <at least one line>
#     CrossSouth B            <at least one line>
#
import gc
import time
import numpy as np

#---------------------------------------
# Elapsed time - Can't import from common to avoid circular import
#---------------------------------------
def elapsed(verbose, start_time, str=""):
    end_time = time.time()
    if verbose:   
        print(f"{str}: Elapsed time = {end_time - start_time:.2g} seconds", flush=True)
    return end_time

# -----------------------------
# Connected Component
# -----------------------------
class classComp:
    def __init__(self, id, parentID):
        self.id = id
        self.parentID = parentID
        self.intersects = []
        self.connectedRows = []
        self.selected = False

    def addIntersect(self, id):
        if (id in self.intersects) == False: 
            self.intersects.append(id)

    # For Geogebra export
    def setLocation(self, cx, cy, radius):
        self.cx = cx
        self.cy = cy
        self.radius = radius

    # add Row
    def addRow(self, row, yStart, yEnd):
        self.connectedRows.append([row, yStart, yEnd])

    def clear(self):
        del self.intersects
        del self.connectedRows
        self.selected = False
        gc.collect()

# -----------------------------
# Guard
# -----------------------------
class classGuard:
    def __init__(self, id):
        self.id = id
        self.compIDs = []
        self.paired = False
        self.xmin = 10000
        self.xmax = -10000

    def addComp(self, comp):
        self.compIDs.append(comp.id)

    def setLocation(self, row, col, ht, radius):
        self.row = int(row)
        self.col = int(col)
        self.ht = int(ht)
        self.radius = int(radius)

    def setMinMax(self, xmin, xmax):
        self.xmin = xmin
        self.xmax = xmax

    def clear(self):
        del self.compIDs
        self.paired = False
        self.xmin = 10000
        self.xmax = -10000
        gc.collect()

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
# Assume this is called inside setupGraph
# -----------------------------
def findIntersections(gComps, verbose=False):
    for c1 in gComps:
        for c2 in gComps:
            timestamp = time.time()
            if intersect(c1, c2):
                c1.addIntersect(c2.id)
                c2.addIntersect(c1.id)
            timestamp = elapsed(verbose, timestamp, "Process two component intersection")

# -----------------------------
# Determine if two Components intersect
# -----------------------------
def intersect(comp1, comp2):
    for conRow1 in comp1.connectedRows:
        for conRow2 in comp2.connectedRows:
            if conRow1[0] == conRow2[0]:
                if not (conRow1[2] < conRow2[1] or conRow2[2] < conRow1[1]):
                    return True

    return False

# -----------------------------
# Find the connected components of a single guard based on the viewshed
# -----------------------------
def findConnected(guard, viewshed, gComps, gNorths, gSouths, verbose=False):

    nrows, ncols = viewshed.shape

    done = False
    while done == False:
        # Find a non-zero pixel to start 
        found = False
        for i in range(nrows):
            for j in range(ncols):
                if viewshed[i][j] == 1:  # Either one or zero
                    timestamp = time.time()

                    flood_fill((i, j), viewshed) # Fill all the connected points and set the pixels to 2
                    timestamp = elapsed(verbose, timestamp, "Flood fill")

                    setConnectedComponent(guard, viewshed, gComps, gNorths, gSouths, verbose)
                    timestamp = elapsed(verbose, timestamp, "Set connected component")

                    found = True
        if found == False:
            done = True

# -----------------------------
# Define a single connected component
# viewshed contains the mask for the connected component (visible = 2 after flood fill)
# Other pixels (if visible by the same guard) = 1
# -----------------------------
def setConnectedComponent(guard, viewshed, gComps, gNorths, gSouths, verbose=False):

    nrows, ncols = viewshed.shape

    compnum = len(gComps)
    comp = classComp(compnum, guard.id)
    guard.addComp(comp)
    gComps.append(comp)

    maxX=-10000
    minX=10000

    for i in range(nrows):
        startY = -1
        endY = -1
        compRow = i
        for j in range(ncols):
            value = viewshed[i][j]
            if value == 2 and j < ncols-1:  # Force start <> end
                if startY < 0: 
                    startY = j
                    compRow = i
            elif (j==ncols-1 and value==2) or value != 2:
                if startY >= 0:
                    if j==ncols-1 and value==2:
                        endY = j
                    else:
                        endY = j-1
                    comp.addRow(compRow, startY, endY)
                    viewshed[i][startY:endY+1] = 0  # Clear pixel after setting the ConnectedRow
                    startY = -1 # To allow multiple strips per row
                    minX = min(i, minX)
                    maxX = max(i, maxX)

    # Potentially add to gNorth or gSouth
    # In the appVP, this is done during construction of first frontier
    # In this solution, we predetermine the components that overlaps with N/S
    if minX == 0:
        gNorths.append(compnum)
    if maxX == nrows-1:
        gSouths.append(compnum)

    guard.setMinMax(minX, maxX)

# -----------------------------
# Flood fill a 2D array
# -----------------------------
def flood_fill(start, viewshed):

    nrows, ncols = viewshed.shape

    stack = []
    stack.append((start))
        
    while len(stack) > 0:
        row, col = stack.pop(0)
        
        # Skip if out of bounds
        if row < 0 or row >= nrows or col < 0 or col >= ncols or viewshed[row][col] != 1:
            continue
        
        # Fill the current pixel with the fill value
        viewshed[row][col] = 2
        
        # Add the 4 neighboring cells to the stack (up, down, left, right)
        stack.append((row + 1, col))  # Right
        stack.append((row - 1, col))  # Left
        stack.append((row, col + 1))  # Down
        stack.append((row, col - 1))  # Up
        
# -----------------------------
# Print Guard information
# A section will be the same format as the input file for the algorithms
# -----------------------------
def printGuards(gGuards, gComps, gNorths, gSouths, verbose=False):
    print("----------Guard/Component Locations----------", flush=True)
    for guard in gGuards:
        print(f"Guard {guard.id} at ({guard.row}, {guard.col})", flush=True)
        for id in guard.compIDs:
            comp = gComps[id]
            print(f"Component {id}: {comp.connectedRows}", flush=True)

    print("-----------Input File Format----------", flush=True)
    for guard in gGuards:
        print(f"Guard {guard.id}", flush=True)
        for id in guard.compIDs:
            print(f"ConnectedComponent {id}", flush=True)
            comp = gComps[id]
            for k in comp.intersects:
                print(f"Intersecting {k}", flush=True)
    for id in gNorths:
        print(f"CrossNorth {id}", flush=True)
    for id in gSouths:
        print(f"CrossSouth {id}", flush=True)
        
# -----------------------------
# Print viewshed
# -----------------------------
def debugPrintMask(viewshed):

    nrows, ncols = viewshed.shape
    for row in range(nrows):
        s = ""
        for col in range(cols):
            s = s + "," + str(viewshed[row][col])
        print(s, flush=True)


    
