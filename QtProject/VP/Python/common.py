"""
  Common code for Machine Learning methods

"""
import numpy as np
import time
from scipy.spatial import distance
from TerrainInput import classComp, classGuard, findIntersections, findConnected, intersect, printGuards
from Visibility import calc_vis

#---------------------------------------
# Print if verbose only
#---------------------------------------
def vprint(verbose, *args, **kwargs):
    if verbose:
        print(*args, **kwargs)

#---------------------------------------
# Step to neighbor
# pt = (x, y)
# bound = (xmax, ymax)
#---------------------------------------
def stepMove(pt, bound, direction):
    assert(direction >= 0 and direction < 8), "Direction out of range"

    if direction == 0:  # North
        newpt = (pt[0], 
                 max(0           , pt[1] - 1))

    elif direction == 1:  # NorthEast
        newpt = (min(bound[0] - 1, pt[0] + 1), 
                 max(0           , pt[1] - 1))

    elif direction == 2:  # East
        newpt = (min(bound[0] - 1, pt[0] + 1),
                 pt[1])

    elif direction == 3:  # SouthEast
        newpt = (min(bound[0] - 1, pt[0] + 1),
                 min(bound[1] - 1, pt[1] + 1))

    elif direction == 4:  # South
        newpt = (pt[0], 
                 min(bound[1] - 1, pt[1] + 1))

    elif direction == 5:  # SouthWest
        newpt = (max(0           , pt[0] - 1),
                 min(bound[1] - 1, pt[1] + 1))

    elif direction == 6:  # West
        newpt = (max(0           , pt[0] - 1),
                 pt[1])

    elif direction == 7:  # NorthWest
        newpt = (max(0           , pt[0] - 1),
                 max(0           , pt[1] - 1))

    return newpt

#---------------------------------------
# Find the diameter of a visibility region
#---------------------------------------
def calc_diameter(npArray):
    y, x = np.where(npArray == 1)
    coords = np.column_stack((x, y))
    diameter = 0
    if len(coords) > 1:
        dist_matrix = distance.cdist(coords, coords, metric='euclidean')
        diameter = np.max(dist_matrix)
    return diameter

#---------------------------------------
# Function to generate Fibonacci lattice
#---------------------------------------
def fibonacci_lattice(n_points, nrows, ncols):
    gR = (1.0 + np.sqrt(5.0)) / 2.0
    
    points = []
    for count in range(n_points):
            
        x = float(count+1) / gR
        x -= int(x)
        y = float(count+1) / (n_points+1)
        points.append((int(x*nrows), int(y*ncols)))  # row/col
    
    return np.array(points)

#---------------------------------------
# Function to generate guard positions in square uniform
# randomize=set the guard positions randomly inside their cell
#---------------------------------------
def square_uniform(n_points, nrows, ncols, randomize=False):
    
    #np.random.seed(42) # Set the seed so we can repeat the results
    xoff = 1.0
    yoff = 1.0

    nGRows = max(1.0, np.sqrt(float(n_points)*float(nrows)/float(ncols)))
    nGCols = max(1.0, np.sqrt(float(n_points)*float(ncols)/float(nrows)))
    nRowGuardPixels = np.floor(max(1.0, float(ncols)/(nGCols+1.0)))
    nColGuardPixels = np.floor(max(1.0, float(nrows)/(nGRows+1.0)))

    points = []
    for i in range(int(nGRows)):
        for j in range(int(nGCols)):
            if randomize:
                xoff = np.random.rand()
                yoff = np.random.rand()
            x = min(max(int((float(i)+xoff)*nRowGuardPixels), 0), nrows-1) # Make sure in range
            y = min(max(int((float(j)+yoff)*nColGuardPixels), 0), ncols-1) # Make sure in range
            points.append((x,y)) # row/col

    return np.array(points) 

#---------------------------------------
# Set up G(V, E)
# Visibility, guard/connected component information
#---------------------------------------
def setupGraph(guard_positions, guardHt, radius, bitmap, verbose=False):

    gGuards = [classGuard(guardnum) for guardnum in range(len(guard_positions))]
    gComps = []
    gNorths = []
    gSouths = []

    start_time = time.time()

    for guard in gGuards:
        guard.setLocation(guard_positions[guard.id][0], guard_positions[guard.id][1], guardHt, radius)
        viewshed = calc_vis(guard, bitmap, verbose)
        findConnected(guard, viewshed, gComps, gNorths, gSouths, verbose)

    findIntersections(gComps, verbose)
    #printGuards(gGuards, gComps, gNorths, gSouths, verbose)

    end_time = time.time()
    vprint(verbose, f"Time to set up guard/connected components = {end_time - start_time:.2g} seconds", flush=True)

    return gGuards, gComps, gNorths, gSouths
# -----------------------------
# Combine two guards if their CCs intersect the most
# Find the top 2 such guards and keep going down the list the guards
# Will modify gGuards, gComps, gNorths, gSouths
# -----------------------------
def pairGuards(nrows, ncols, gGuards, gComps, gNorths, gSouths, verbose=False):
    done = False
    while done==False:
        maxIntsPair = 0
        g1 = -1
        g2 = -1
        for guard1 in gGuards:
            if guard1.paired == False:
                for guard2 in gGuards:
                    if guard2.id != guard1.id and guard2.paired == False:
                        nIntsPair = 0   # Number of intersections between 2 guards
                        for c1 in guard1.compIDs:
                            for c2 in guard2.compIDs:
                                if c1 in gComps[c2].intersects:
                                    nIntsPair += 1         
                        if nIntsPair > maxIntsPair:
                            maxIntsPair = nIntsPair
                            g1 = guard1.id
                            g2 = guard2.id
        if maxIntsPair >= 2:
            vprint(verbose, f"Merging guards {g1} and {g2} with {maxIntsPair} intersecting CC!", flush=True)
            gGuards[g1].paired = True
            gGuards[g2].paired = True
            merge2Guards(g1, g2, gGuards, gComps, gNorths, gSouths, nrows, ncols, verbose)
        else:
            done = True

# -----------------------------
# Merge 2 guards
# g1, g2 are Guard IDs
# In order to merge the CCs correctly, 
# each CC is unwrapped into the same bitmap 
# -----------------------------
def merge2Guards(g1, g2, gGuards, gComps, gNorths, gSouths, nrows, ncols, verbose=False):

    bitmap = np.zeros((nrows, ncols), dtype=np.uint32)

    for cc in gGuards[g1].compIDs:
        comp = gComps[cc]
        for cRow in comp.connectedRows:         
            bitmap[cRow[0]][cRow[1]:cRow[2]+1] = 1
    for cc in gGuards[g2].compIDs:
        comp = gComps[cc]
        for cRow in comp.connectedRows:         
            bitmap[cRow[0]][cRow[1]:cRow[2]+1] = 1

    nComp = len(gComps)
    guard = classGuard(len(gGuards))
    gGuards.append(guard)
    guard.paired = True  # Won't merge after once
    guard.setLocation(gGuards[g1].row, gGuards[g1].col, gGuards[g1].ht, gGuards[g1].radius)
    findConnected(guard, bitmap, gComps, gNorths, gSouths, verbose)

    # Check for intersection ONLY between the existing components and the 
    # new components to avoid duplication
    for i in range(nComp):
        for j in range(nComp, len(gComps)):
            if intersect(gComps[i], gComps[j]):
                gComps[i].addIntersect(j)
                gComps[j].addIntersect(i)

    removeGuard(g1, gGuards, gComps, gNorths, gSouths)
    removeGuard(g2, gGuards, gComps, gNorths, gSouths)

# -----------------------------
# Remove a Guard from gGuards and all its links
# Update all the ids and their references
# Note: id is also the position in gGuards array
# -----------------------------
def removeGuard(id, gGuards, gComps, gNorths, gSouths):

    for g in gGuards:
        if g.id > id:
            g.id -= 1

    for i in gGuards[id].compIDs:
        removeComp(i, gComps, gNorths, gSouths) # This will take are of all parentID links

    gGuards[id].clear()
    gGuards.pop(id)


# -----------------------------
# Remove a Component from gComps and all its links
# Update all the ids and their references
# Note: id is also the position in gComps array
# -----------------------------
def removeComp(id, gComps, gNorths, gSouths):

    # Must remove occurrence before reducing the values
    gComps[id].clear()
    gComps.pop(id)
    if id in gNorths:
        gNorths.remove(id)
    if id in gSouths:
        gSouths.remove(id)

    for c in gComps:
        if c.id > id:
            c.id -= 1
        if id in c.intersects:
            c.intersects.remove(id)
        for i in range(len(c.intersects)):
            if c.intersects[i] > id:
                c.intersects[i] -= 1

    for g in gGuards:
        for i in range(len(g.compIDs)):
            if g.compIDs[i] > id:
                g.compIDs[i] -= 1

    for i in range(len(gNorths)):
        if gNorths[i] > id:
            gNorths[i] -= 1
    for i in range(len(gSouths)):
        if gSouths[i] > id:
            gSouths[i] -= 1
