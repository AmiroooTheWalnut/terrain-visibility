
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
    
    return np.array(points)

#---------------------------------------
# Set up G(V, E)
# Visibility, guard/connected component information
#---------------------------------------
def setup(guard_positions):    
    global verbose, elev, radius

    nrows, ncols = bitmap.shape
    x_coords, y_coords = zip(*guard_positions)

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
    printGuards(True)

    if verbose:
        end_time = time.time()
        print(f"Time to set up guard/connected components = {end_time - start_time:.2g} seconds")

#---------------------------------------
# Particle Swarm Optimization
#---------------------------------------
def bsfScore(guard_positions):
    global numGuards

    score = 0
    guard_positions = np.round(guard_positions).reshape((numGuards, 2))
    setup(guard_positions)
    nFrontier = runBSF(gGuards, gComps, gNorths, gSouths)
    #print(f"nFrontier = {nFrontier}")
    #print(guard_positions)

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
    elev = 10     # Default = 10
    radius = 30  # Default = 123
    numGuards = 100
    bitmap = read_png(input, verbose)
    nrows, ncols = bitmap.shape

    # Initial guard positions determined by fibonacci lattice
    guard_positions = fibonacci_lattice(numGuards, nrows, ncols)

    # Define bounds for the guards to not exceed the bitmap
    num_dimensions = 2
    lb = np.array([0, 0])
    ub = np.array([nrows-1, ncols-1])
   
    # Two options:
    # Option 1: n_particles = numGuards, num_dimensions = 2     - Optimize individual position    
    # Option 2: n_particles = 1, num_dimensions = numGuards * 2 - Optimize entire set
    optimizer = ps.single.GlobalBestPSO(n_particles=numGuards, dimensions=num_dimensions,
                                        options={'c1': 0.5, 'c2': 0.5, 'w': 0.7},
                                        bounds=(lb, ub), init_pos=guard_positions.astype(float))
    
    cost, pos = optimizer.optimize(bsfScore, iters=10)
    #best_positions = pos.reshape((numGuards, 2))

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    