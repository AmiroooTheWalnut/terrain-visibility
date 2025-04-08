# ---------------------------------------
# Algorithm optimization using Reverse Visibility, no Machine Learning
# ---------------------------------------
import numpy as np
import argparse
from ReadElevImg import read_png, show_terrain
from common import setupGraph, stepMove
from Visibility import rev_vis
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

    endPos = startPos
    bound = (nrows, ncols)
    dist = np.zeros((5), dtype=int)
    guardPos = np.zeros((5, 2), dtype=int)
    for dir in range(0, 5): # E, SE, S, SW, W (Skip N, NE, or NW)
        if verbose:
            print(f"Checking direction {dir}")

        done = False
        while done == False:
            endPos = stepMove(endPos, bound, dir+2)
            if verbose:
                print(f"Moved to position {endPos}")

            viewshed2 = rev_vis(endPos, bitmap, guardHt, radius, verbose)
            overlap = viewshed1 * viewshed2
            if np.sum(overlap) > 0:
                dist[dir] = np.linalg.norm(endPos - startPos)
                ys, xs = np.where(overlap)
                guardPos[dir] = ([xs.max(), ys.max()])  # Pick a point in the intersection

                if verbose:
                    print(f"Potential guard position = {guardPos[dir]}")

                if guardPos[dir][1] == ncols-1: # Done when we reach South
                    done = True
            else: # Done when the two viewsheds no longer overlap 
                done = True

    index = np.argmax(dist) # Find the longest street        
    
    return guardPos[index], dist.max()

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
    maxD = 0
    pos = np.zeros((2, 2), dtype=int)
    for x in range(nrows):
        p1 = np.array([x, 0])
        p2, distance = findSharedGuardPos(p1, verbose)
        if maxD < distance:
            maxD = distance
            pos[0] = p1
            pos[1] = p2
        
    print(f"First guard at {pos[0]}")
    print(f"Second guard at {pos[1]}")

    # Start at the 2nd guard position
    # Look for the next guard one at a time
    p2 = pos[1]
    while p2[1] < ncols-1:
        p2 = findSharedGuardPos(p2, verbose)
        print(f"Next guard at {p2}")
    
    if p2[1] == ncols-1:
        print(f"South reached!")
    else:
        print(f"Cannot reach South")

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    