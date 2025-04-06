"""
  Common code for Machine Learning methods

"""
import numpy as np
import time
from scipy.spatial import distance
from TerrainInput import classComp, classGuard, findIntersections, findConnected, intersect, printGuards, clearAll
from TerrainInput import gGuards, gComps, gNorths, gSouths
from Visibility import calc_vis

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
        points.append((int(x*nrows), int(y*ncols)))
    
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
            points.append((x,y))

    return np.array(points)

#---------------------------------------
# Set up G(V, E)
# Visibility, guard/connected component information
#---------------------------------------
def setupGraph(guard_positions, elev, radius, bitmap, verbose=False):
    
    if verbose:
        start_time = time.time()

    clearAll()
    for guardnum in range(len(guard_positions)):
        guard = classGuard(guardnum)
        gGuards.append(guard)
        guard.setLocation(guard_positions[guardnum][0], guard_positions[guardnum][1], elev, radius)
        viewshed = calc_vis(guard, bitmap, verbose)
        findConnected(guard, viewshed, verbose)

    findIntersections(verbose)
    printGuards(verbose)

    if verbose:
        end_time = time.time()
        print(f"Time to set up guard/connected components = {end_time - start_time:.2g} seconds")

# -----------------------------
# Combine two guards if their CCs intersect the most
# Find the top 2 such guards and keep going down the list the guards
# Will modify gGuards, gComps, gNorths, gSouths
# -----------------------------
def pairGuards(nrows, ncols, verbose=False):
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
            print(f"Merging guards {g1} and {g2} with {maxIntsPair} intersecting CC!")
            gGuards[g1].paired = True
            gGuards[g2].paired = True
            merge2Guards(g1, g2, nrows, ncols, verbose)
        else:
            done = True

# -----------------------------
# Merge 2 guards
# g1, g2 are Guard IDs
# In order to merge the CCs correctly, 
# each CC is unwrapped into the same bitmap 
# -----------------------------
def merge2Guards(g1, g2, nrows, ncols, verbose=False):

    bitmap = np.zeros((nrows, ncols), dtype=np.uint32)

    for cc in gGuards[g1].compIDs:
        bitmap[gComps[cc].minX:gComps[cc].maxX+1, gComps[cc].minY:gComps[cc].maxY+1] = \
               np.maximum(gComps[cc].bitmap, \
               bitmap[gComps[cc].minX:gComps[cc].maxX+1, gComps[cc].minY:gComps[cc].maxY+1])
    for cc in gGuards[g2].compIDs:
        bitmap[gComps[cc].minX:gComps[cc].maxX+1, gComps[cc].minY:gComps[cc].maxY+1] = \
               np.maximum(gComps[cc].bitmap, \
               bitmap[gComps[cc].minX:gComps[cc].maxX+1, gComps[cc].minY:gComps[cc].maxY+1])

    nComp = len(gComps)
    guard = classGuard(len(gGuards))
    gGuards.append(guard)
    guard.paired = True  # Won't merge after once
    guard.setLocation(gGuards[g1].x, gGuards[g1].y, gGuards[g1].h, gGuards[g1].r)
    findConnected(guard, bitmap, verbose)

    # Check for intersection ONLY between the existing components and the 
    # new components to avoid duplication
    for i in range(nComp):
        for j in range(nComp, len(gComps)):
            if intersect(gComps[i], gComps[j]):
                gComps[i].addIntersect(j)
                gComps[j].addIntersect(i)

    removeGuard(g1)
    removeGuard(g2)

# -----------------------------
# Remove a Guard from gGuards and all its links
# Update all the ids and their references
# Note: id is also the position in gGuards array
# -----------------------------
def removeGuard(id):
    global gGuards, gComps

    for g in gGuards:
        if g.id > id:
            g.id -= 1

    for i in gGuards[id].compIDs:
        removeComp(i) # This will take are of all parentID links

    gGuards[id].clear()
    gGuards.pop(id)


# -----------------------------
# Remove a Component from gComps and all its links
# Update all the ids and their references
# Note: id is also the position in gComps array
# -----------------------------
def removeComp(id):
    global gGuards, gComps, gNorths, gSouths

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
