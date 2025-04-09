# ---------------------------------------
# Algorithm optimization using Reverse Visibility, no Machine Learning
# ---------------------------------------
import numpy as np
import argparse
from ReadElevImg import read_png, show_terrain
from ilpAlgGenBSF import runBSF, show_frontiers
from common import setupGraph, stepMove
from Visibility import rev_vis
from TerrainInput import gGuards, gComps, gNorths, gSouths
import time

#---------------------------------------
# startPos is of format (x, y).  It's a point on the terrain.
# Find the guard position that will see both startPos and furthest endPos
# We find the intersection between the visibility regions of startPos and the 
# visibility regions of endPos.  We keep moving the endPos until the distance
# between startPos and endPos is maximum.
#---------------------------------------
def findSharedGuardPos(startPos, verbose=False):

    # Find reverse visibility from startPos
    viewshed1 = rev_vis(startPos, bitmap, guardHt, radius, verbose)

    bound = (nrows, ncols)
    dist = np.zeros((5), dtype=int)
    endPos = np.zeros((5, 2), dtype=int)
    guardPos = np.zeros((5, 2), dtype=int)

    for dir in range(0, 5): # E, SE, S, SW, W (Skip N, NE, or NW)
        # Always move in the fixed direction
        if verbose:
            print(f"Checking direction {dir}")

        done = False
        endPos[dir] = startPos.copy()
        while done == False:
            pos = stepMove(endPos[dir], bound, dir+2)
            newPos = np.array((pos[0], pos[1]), dtype=int)
            if np.all(newPos == endPos[dir]):
                done = True # Must have reached a bound in that direction
                break

            endPos[dir] = newPos.copy()
            if verbose:
                print(f"Moved to position {newPos}")

            viewshed2 = rev_vis(newPos, bitmap, guardHt, radius, verbose)
            overlap = viewshed1 * viewshed2

            if np.sum(overlap) == 0:
                done = True
            else: # Done when the two viewsheds no longer overlap 
                dist[dir] = np.linalg.norm(newPos - startPos)
                xs, ys = np.where(overlap)
                guardPos[dir] = ([xs.max(), ys.max()])  # Pick a point in the intersection

                if verbose:
                    print(f"Potential guard position = {guardPos[dir]}")

                if endPos[dir][1] == nrows-1: # Done when we reach South
                    done = True

    dir = np.argmax(dist) # Find the longest street        
    
    return guardPos[dir], endPos[dir], dist.max()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing frontiers")

    args = parser.parse_args()
    filename = args.name        # None if not provided
    radius = args.radius        # None if not provided
    verbose = args.verbose      # False if not provided
    enableShow = args.show      # False if not provided

    # Other options
    # ----------------
    guardHt = 10     # Guard height above terrain
    # ----------------

    start_time = time.time()   

    # Read bitmap
    bitmap = read_png(filename, verbose, enableShow)
    nrows, ncols = bitmap.shape

    # First find two points on the terrain.  
    # p1 is a point on the North rim. 
    # p2 is as far down as possible that can share a guard position with p1.
    guard_positions = []
    maxD = 0
    pos = np.zeros((2, 2), dtype=int)
    for x in range(ncols):
        p1 = np.array([x, 0])
        gPos, p2, distance = findSharedGuardPos(p1, verbose)
        print(f"Longest distance from {p1} to {p2} = {distance}")

        if maxD < distance:
            maxD = distance
            pos[0] = p1
            pos[1] = p2
        
    print(f"First guard at {gPos}, watching {pos[0]} and {pos[1]}")
    guard_positions.append((pos[0], pos[1]))

    # Look for the next guard one at a time
    p1 = pos[1]  # Initial position
    done = False
    while done == False:
        gPos, p2, distance = findSharedGuardPos(p1, verbose)
        print(f"Next guard at {gPos}, watching {p1} and {p2}")
        guard_positions.append((gPos[0], gPos[1]))
    
        if p2[1] == ncols-1:
            print(f"South reached!")
            done = True
        p1 = p2 # Move to next position

    setupGraph(np.array(guard_positions), guardHt, radius, bitmap, verbose)
    score = runBSF(gGuards, gComps, gNorths, gSouths, verbose)

    if enableShow:
        show_frontiers(nrows, ncols, bitmap, gGuards, gComps)

    print(f"Number of Frontier = {score}")

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    