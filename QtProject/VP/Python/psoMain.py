import numpy as np
import argparse
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from Visibility import calc_vis
from ReadElevImg import read_png, show_terrain
from TerrainInput import classComp, classGuard, findIntersections, findConnected, printGuards, clearAll
from TerrainInput import gGuards, gComps, gNorths, gSouths
from ilpAlgGenBSF import runBSF
import pyswarms as ps
import time

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
def setup(guard_positions):    
    global verbose

    nrows, ncols = bitmap.shape

    elev = 10     # Default = 10
    radius = 30  # Default = 123

    lattice_points = fibonacci_lattice(numGuards, nrows, ncols)
    x_coords, y_coords = zip(*lattice_points)

    if verbose:
        start_time = time.time()

    clearAll()

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

    if verbose:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time to set up guard/connected components = {elapsed_time:.2g} seconds")

#---------------------------------------
# Particle Swarm Optimization
#---------------------------------------
def bsfScore(guard_positions):
    global numGuards, bitmap, last_pos

    score = 0
    guard_positions = np.round(guard_positions).reshape((numGuards, 2))
    setup(guard_positions)
    nFrontier = runBSF(gGuards, gComps, gNorths, gSouths)
    print(f"nFrontier = {nFrontier}")
    print(guard_positions)

    return nFrontier  # Lower cost the better

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('INPUT', type=str, help="test.png")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    args = parser.parse_args()
    input = args.INPUT
    verbose = args.verbose

    start_time = time.time()   

    # Read bitmap, set up initial guard positions
    numGuards = 100
    bitmap = read_png(input, verbose)

    nrows, ncols = bitmap.shape
    guard_positions = fibonacci_lattice(numGuards, nrows, ncols)

    setup(guard_positions)
    nFrontier = runBSF(gGuards, gComps, gNorths, gSouths)

    last_pos = guard_positions

    # Define bounds for the guards - Don't move too far from original locations
    dimensions = 2 * numGuards
    lb = np.array([0] * dimensions)
    ub = np.tile([nrows, ncols], numGuards)
   
    optimizer = ps.single.GlobalBestPSO(n_particles=1, dimensions=dimensions,
                                        options={'c1': 0.5, 'c2': 0.3, 'w': 0.9},
                                        bounds=(lb, ub))
    
    cost, pos = optimizer.optimize(bsfScore, iters=50)
    best_positions = pos.reshape((numGuards, 2))

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    