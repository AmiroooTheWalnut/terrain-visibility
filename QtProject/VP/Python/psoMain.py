import numpy as np
import argparse
from Visibility import calc_vis
from ReadElevImg import read_png, show_terrain
from TerrainInput import classComp, classGuard, findIntersections, findConnected, printGuards, clearAll
from TerrainInput import gGuards, gComps, gNorths, gSouths
from ilpAlgGenBSF import runBSF, show_frontiers
import pyswarms as ps
import time
import copy

nFrontiers = 9999
lastComps = []
lastGuards = []

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
#---------------------------------------
def square_uniform(n_points, nrows, ncols):
    global numGuards
    
    nGRows = max(1.0, np.sqrt(float(n_points)*float(nrows)/float(ncols)))
    nGCols = max(1.0, np.sqrt(float(n_points)*float(ncols)/float(nrows)))
    nRowGuardPixels = np.floor(max(1.0, float(ncols)/(nGCols+1.0)))
    nColGuardPixels = np.floor(max(1.0, float(nrows)/(nGRows+1.0)))

    points = []
    for i in range(int(nGRows)):
        for j in range(int(nGCols)):
            points.append(((i+1)*int(nRowGuardPixels), (j+1)*int(nColGuardPixels)))

    # Update numGuards based on how many points it ends up
    numGuards = len(points)

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
    printGuards(verbose)

    if verbose:
        end_time = time.time()
        print(f"Time to set up guard/connected components = {end_time - start_time:.2g} seconds")

#---------------------------------------
# Particle Swarm Optimization
#---------------------------------------
def bsfScore(guard_positions):
    global numGuards, nFrontiers, iteration, lastComps, lastGuards

    score = 0
    guard_positions = np.round(guard_positions).reshape((numGuards, 2))

    # Don't move the guards touching North or South 
    if keepNS:
        if iteration > 0:
            for comp in lastComps:
                if comp.minX == 0 or comp.maxX == nrows-1:
                    id = comp.parentID
                    guard_positions[id] = (lastGuards[id].x, lastGuards[id].y)

    setup(guard_positions)
    num = runBSF(gGuards, gComps, gNorths, gSouths, verbose)
    print(f"Iteration: {iteration}, Cost = {num}", flush=True)
    if num < nFrontiers:
        nFrontiers = num
        if enableShow:
            show_frontiers(nrows, ncols, bitmap, gComps)

    #num = runILP(gGuards, gComps, gNorths, gSouths, verbose)
    #print(f"Number of Frontier = {num}")
    #print(guard_positions)

    iteration += 1

    lastComps.clear()
    lastComps = gComps.copy()
    lastGuards.clear()
    lastGuards = gGuards.copy()

    return nFrontiers  # Lower cost the better

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Visibility')
    parser.add_argument('--name', type=str, help="test.png")
    parser.add_argument('--radius', type=int, help="120")
    parser.add_argument('--numGuards', type=int, help="50")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose")
    parser.add_argument('--show', action='store_true', help="Enable showing frontiers")
    parser.add_argument('--keepNS', action='store_true', help="Keep NS guard pos")

    args = parser.parse_args()
    filename = args.name
    radius = args.radius
    numGuards = args.numGuards
    verbose = args.verbose
    enableShow = args.show
    keepNS = args.keepNS
    elev = 10     # Default = 10

    start_time = time.time()   

    # Read bitmap
    bitmap = read_png(filename, verbose, enableShow)
    nrows, ncols = bitmap.shape

    # Initial guard positions determined by fibonacci lattice
    guard_positions = fibonacci_lattice(numGuards, nrows, ncols)
    #guard_positions = square_uniform(numGuards, nrows, ncols)

    # Get a baseline
    iteration = 0
    bsfScore(guard_positions)

    # Define bounds for the guards to not exceed the bitmap
    num_dimensions = 2
    lb = np.array([0, 0])
    ub = np.array([nrows-1, ncols-1])
   
    # Two options:
    # Option 1: n_particles = numGuards, num_dimensions = 2     - Optimize individual position    
    # Option 2: n_particles = 1, num_dimensions = numGuards * 2 - Optimize entire set
    # c1 [0.5 to 2.5] = Cognitive parameter (high: more based on individual memory) 
    # c2 [0.5 to 2.5] = Social parameter (high: converge quickly)
    # w [0.4 to 1.2] = Inertia weight (high: explore more wider space)
    optimizer = ps.single.GlobalBestPSO(n_particles=numGuards, dimensions=num_dimensions,
                                        options={'c1': 1.2, 'c2': 0.3, 'w': 1.0},
                                        bounds=(lb, ub), init_pos=guard_positions.astype(float))
    
    cost, pos = optimizer.optimize(bsfScore, iters=100)
    #best_positions = pos.reshape((numGuards, 2))

    end_time = time.time()
    print(f"Total running time = {end_time - start_time:.2g} seconds")    


    

    