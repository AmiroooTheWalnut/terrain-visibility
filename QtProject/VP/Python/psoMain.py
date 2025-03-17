import numpy as np
import argparse
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from Visibility import calc_vis
from ReadElevImg import read_png, show_terrain
from TerrainInput import classComp, classGuard, findIntersections, findConnected, printGuards
from TerrainInput import gGuards, gComps, gNorths, gSouths
from ilpAlgGenBSF import runBSF
#import pyswarms as ps

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
    
    return points

#---------------------------------------
# Set up G(V, E)
# Visibility, guard/connected component information
#---------------------------------------
def setup(guard_positions, bitmap, verbose=False):    
    nrows, ncols = bitmap.shape

    elev = 10     # Default = 10
    radius = 30  # Default = 123

    lattice_points = fibonacci_lattice(numGuards, nrows, ncols)
    x_coords, y_coords = zip(*lattice_points)

    for guardnum in range(numGuards):
        guard = classGuard(guardnum)
        gGuards.append(guard)
        guard.setLocation(x_coords[guardnum], y_coords[guardnum], elev, radius) 
    
        #viewshed is what this guard can see (1 = yes, 0 = no)
        viewshed = calc_vis(guard, bitmap, verbose)  
	
	# Find the Connected Components per guard
        findConnected(guard, viewshed, verbose)

    # Determine the intersections of the Connected Components
    findIntersections(verbose)
    printGuards(verbose)

#---------------------------------------
# Particle Swarm Optimization
#---------------------------------------
def bsfScore(guard_positions):
    global numGuards, bitmap

    score = 0
    guard_points = guard_points.reshape((numGuards, 2))
    setup(guard_positions, args.verbose)
    nFrontier = runBSF(gGuards, gComps, gNorths, gSouths)
    print(f"nFrontier = {nFrontier}")
    return -nFrontier  # Negative because we minimize the number of Frontiers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('INPUT', type=str, help="test.png")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    args = parser.parse_args()
   
    # Read bitmap, set up initial guard positions
    numGuards = 100
    bitmap = read_png(args.INPUT, args.verbose)
    nrows, ncols = bitmap.shape
    guard_positions = fibonacci_lattice(numGuards, nrows, ncols)

    setup(guard_positions, bitmap, args.verbose)
    nFrontier = runBSF(gGuards, gComps, gNorths, gSouths)

    """
    # Define bounds for the guards - Don't move too far from original locations
    limit = 10
    lb = guard_positions
    ub = guard_positions
    for k in range(len(guard_positions)):
        lb[k] = max(guard_positions[k][0]-limit, guard_positions[k][1]-limit)
        ub[k] = min(guard_positions[k][0]+limit, guard_positions[k][1]+limit)

    dimensions = 2
    optimizer = ps.single.GlobalBestPSO(n_particles=30, dimensions=numGuards*dimensions,
                                        options={'c1': 0.5, 'c2': 0.3, 'w': 0.9},
                                        bounds=(lb, ub))
    
    cost, pos = optimizer.optimize(bsfScore, iters=10)
    best_positions = pos.reshape((numGuards, dimensions))

    time3 = time.time()
    print(f"Total running time = {time3 - time1:.2g} seconds")    
    """

    

    