# ---------------------------------------
# Algorithm optimization using Reverse Visibility, no Machine Learning
# ---------------------------------------
import numpy as np
import argparse
from ReadElevImg import read_png, show_terrain
from algBSF import runBSF, show_frontiers
from common import setupGraph, stepMove
from Visibility import rev_vis
import time

#---------------------------------------
# Debug reverse visibility overlap
#---------------------------------------
def debugVis(verbose=False):

    pos1 = np.array((510, 57))
    pos2 = np.array((510, 60))

    viewshed1 = rev_vis(pos1, bitmap, guardHt, radius, verbose)
    viewshed2 = rev_vis(pos2, bitmap, guardHt, radius, verbose)
    overlap = viewshed1 * viewshed2
    sum = np.sum(overlap)
    print(f"Overlap {sum} pixels")

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

    for dir in (3, 4, 5): # SE, S, SW # Only goes down 
        idx = dir-3

        # Always move in the fixed direction
        if verbose:
            print(f"Checking direction {dir}", flush=True)

        done = False
        endPos[idx] = (startPos[0], startPos[1])

        while done == False:
            newPos = stepMove(endPos[idx], bound, dir)

            viewshed2 = rev_vis(newPos, bitmap, guardHt, radius, verbose)
            overlap = viewshed1 * viewshed2
            sum = np.sum(overlap)

            if verbose:
                print(f"Trying to move from {startPos} to {newPos}, reverse visibility overlapping {sum} pixels", flush=True)                

            if sum == 0:
                done = True # Done when the two viewsheds no longer overlap 
            else: 
                d = np.linalg.norm(newPos - startPos)
                if d > dist[idx]:
                    dist[idx] = d
                    xs, ys = np.where(overlap)
                    guardPos[idx] = ([xs.max(), ys.max()])  # Pick a point in the intersection
                    if verbose:
                        print(f"Potential guard position = {guardPos[idx]}, {startPos} to {newPos}, distance = {dist[idx]}", flush=True)

            if done == False:
                endPos[idx] = (newPos[0], newPos[1])

            if newPos[1] == nrows-1: # Done when we reach South
                done = True

    dir = np.argmax(dist) # Find the longest street        
    
    return guardPos[idx], endPos[idx], dist[idx]

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
    guardHt = 120     # Guard height above sea level
    # ----------------

    start_time = time.time()   

    # Read bitmap
    bitmap = read_png(filename, verbose, enableShow)
    nrows, ncols = bitmap.shape

    debugVis()

    # First find two points on the terrain.  
    # p1 is a point on the North rim. 
    # p2 is as far down as possible that can share a guard position with p1.
    guard_positions = []
    guard_positions.append((0,0))
    maxD = 0
    pos = np.zeros((2, 2), dtype=int)

    for x in range(radius, ncols-radius):  # Avoid getting stuck on either E or W edge
        p1 = np.array([x, 0])
        gPos, p2, distance = findSharedGuardPos(p1, verbose)
        print(f"Longest distance from {p1} to {p2} = {distance}", flush=True)

        if maxD < distance:
            maxD = distance
            pos[0] = p1
            pos[1] = p2
            guard_positions[0] = gPos
        
    print(f"First guard at {guard_positions[0]}, watching {pos[0]} and {pos[1]}, max distance = {maxD}", flush=True)

    # Look for the next guard one at a time
    p1 = pos[1]  # Initial position
    done = False
    while done == False:
        gPos, p2, distance = findSharedGuardPos(p1, verbose)
        print(f"Next guard at {gPos}, watching {p1} and {p2}, max distance = {distance}", flush=True)
        guard_positions.append((gPos[0], gPos[1]))
    
        if p2[1] == ncols-1:
            print(f"South reached!", flush=True)
            done = True
        p1 = p2 # Move to next position

    arr = np.array(guard_positions)
    gGuards, gComps, gNorths, gSouths = setupGraph(arr, guardHt, radius, bitmap, verbose)
    score = runBSF(gGuards, gComps, gNorths, gSouths, verbose)

    if enableShow:
        show_frontiers(nrows, ncols, bitmap, gGuards, gComps)

    print(f"Number of Frontier = {score}", flush=True)

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds", flush=True)    


    

    